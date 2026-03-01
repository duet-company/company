"""
Task queue system for agents.

Provides asynchronous task execution with:
- Task queuing
- Priority handling
- Retry logic
- Task cancellation
- Result caching
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque
import uuid

from .errors import AgentTaskQueueError
from .config import RetryConfig


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a task to be executed."""

    task_id: str
    agent_id: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 300.0  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "metadata": self.metadata,
        }


class TaskQueue:
    """
    Asynchronous task queue for agent operations.

    Features:
    - Priority-based queuing
    - Async task execution
    - Retry logic with exponential backoff
    - Task cancellation
    - Result caching
    """

    def __init__(self, max_concurrent_tasks: int = 5):
        """
        Initialize the task queue.

        Args:
            max_concurrent_tasks: Maximum concurrent tasks
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.queue: deque[Task] = deque()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.task_results: Dict[str, Any] = {}
        self.logger = logging.getLogger("agent.task_queue")
        self._workers: List[asyncio.Task] = []
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """Start the task queue workers."""
        self.logger.info("Starting task queue workers")

        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

        self.logger.info(f"Started {len(self._workers)} workers")

    async def stop(self) -> None:
        """Stop the task queue workers."""
        self.logger.info("Stopping task queue workers")
        self._stop_event.set()

        # Cancel running tasks
        for task in self.running_tasks.values():
            task.status = TaskStatus.CANCELLED

        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        self.logger.info("Task queue workers stopped")

    async def enqueue(
        self,
        agent_id: str,
        function: Callable,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: float = 300.0,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Enqueue a task for execution.

        Args:
            agent_id: ID of the agent to execute the task
            function: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Task priority
            timeout: Task timeout in seconds
            max_retries: Maximum retry attempts
            metadata: Additional task metadata

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())

        task = Task(
            task_id=task_id,
            agent_id=agent_id,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            metadata=metadata or {},
        )

        # Insert into queue based on priority
        inserted = False
        for i, queued_task in enumerate(self.queue):
            if task.priority.value > queued_task.priority.value:
                self.queue.insert(i, task)
                inserted = True
                break

        if not inserted:
            self.queue.append(task)

        self.logger.debug(
            f"Enqueued task {task_id} for agent {agent_id} "
            f"(priority: {priority.value})"
        )

        return task_id

    async def get_task_result(self, task_id: str, timeout: float = 300.0) -> Any:
        """
        Get the result of a task, waiting if necessary.

        Args:
            task_id: Task ID
            timeout: Maximum time to wait for result

        Returns:
            Task result

        Raises:
            AgentTaskQueueError: If task fails or times out
        """
        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            if task_id in self.completed_tasks:
                task = self.completed_tasks[task_id]

                if task.status == TaskStatus.FAILED:
                    raise AgentTaskQueueError(
                        f"Task {task_id} failed: {task.error}"
                    )

                if task.status == TaskStatus.CANCELLED:
                    raise AgentTaskQueueError(f"Task {task_id} was cancelled")

                return task.result

            await asyncio.sleep(0.1)

        raise AgentTaskQueueError(
            f"Timeout waiting for task {task_id} result"
        )

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"Cancelled running task {task_id}")
            return True

        # Check queued tasks
        for i, task in enumerate(self.queue):
            if task.task_id == task_id:
                del self.queue[i]
                task.status = TaskStatus.CANCELLED
                self.completed_tasks[task_id] = task
                self.logger.info(f"Cancelled queued task {task_id}")
                return True

        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.

        Args:
            task_id: Task ID

        Returns:
            Task status or None if not found
        """
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].to_dict()

        # Check queued tasks
        for task in self.queue:
            if task.task_id == task_id:
                return task.to_dict()

        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()

        return None

    def list_tasks(
        self,
        agent_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.

        Args:
            agent_id: Filter by agent ID
            status: Filter by status

        Returns:
            List of tasks
        """
        tasks = []

        # Add running tasks
        for task in self.running_tasks.values():
            tasks.append(task)

        # Add queued tasks
        tasks.extend(self.queue)

        # Add completed tasks (last 100)
        tasks.extend(list(self.completed_tasks.values())[-100:])

        # Apply filters
        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]

        if status:
            tasks = [t for t in tasks if t.status == status]

        return [task.to_dict() for task in tasks]

    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        status_counts = {}
        for task in self.completed_tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "pending": len(self.queue),
            "running": len(self.running_tasks),
            "total_workers": len(self._workers),
            "completed": len(self.completed_tasks),
            "completed_by_status": status_counts,
        }

    async def _worker(self, worker_id: str) -> None:
        """
        Worker coroutine for executing tasks.

        Args:
            worker_id: Worker identifier
        """
        self.logger.debug(f"Worker {worker_id} started")

        while not self._stop_event.is_set():
            try:
                # Wait for tasks with timeout
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=0.1,
                    )
                except asyncio.TimeoutError:
                    pass

                if self._stop_event.is_set():
                    break

                # Get next task from queue
                if not self.queue:
                    continue

                task = self.queue.popleft()

                # Execute task
                await self._execute_task(task)

            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")

        self.logger.debug(f"Worker {worker_id} stopped")

    async def _execute_task(self, task: Task) -> None:
        """
        Execute a single task with retry logic.

        Args:
            task: Task to execute
        """
        task.started_at = datetime.utcnow()
        task.status = TaskStatus.RUNNING
        self.running_tasks[task.task_id] = task

        try:
            self.logger.debug(
                f"Executing task {task.task_id} "
                f"(agent: {task.agent_id}, priority: {task.priority.value})"
            )

            # Execute with timeout
            result = await asyncio.wait_for(
                task.function(*task.args, **task.kwargs),
                timeout=task.timeout,
            )

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self.task_results[task.task_id] = result

            self.logger.info(
                f"Task {task.task_id} completed successfully"
            )

        except asyncio.TimeoutError:
            task.error = f"Task timeout after {task.timeout} seconds"
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

            self.logger.error(
                f"Task {task.task_id} timed out"
            )

        except Exception as e:
            task.error = str(e)
            task.retry_count += 1

            # Retry if under max retries
            if task.retry_count <= task.max_retries:
                task.status = TaskStatus.RETRYING

                # Exponential backoff
                delay = 2 ** (task.retry_count - 1)
                await asyncio.sleep(delay)

                # Re-enqueue
                self.queue.append(task)

                self.logger.warning(
                    f"Task {task.task_id} failed, "
                    f"retrying ({task.retry_count}/{task.max_retries})"
                )
                return

            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

            self.logger.error(
                f"Task {task.task_id} failed after {task.retry_count} retries: {e}"
            )

        finally:
            # Move to completed
            del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task

            # Keep only last 1000 completed tasks
            if len(self.completed_tasks) > 1000:
                oldest = next(iter(self.completed_tasks))
                del self.completed_tasks[oldest]
