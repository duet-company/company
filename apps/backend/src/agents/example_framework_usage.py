"""
Example: AI Agent Framework Usage

This module demonstrates how to use the AI agent framework
with the custom implementation.
"""

import asyncio
import logging
from typing import Any, Dict, List
from dataclasses import dataclass, field

from .base import BaseAgent, AgentStatus, AgentCapability, AgentMessage
from .config import AgentConfig, AgentType, LLMProviderConfig, RetryConfig
from .errors import AgentError
from .registry import AgentRegistry
from .communication import CommunicationChannel
from .task_queue import TaskQueue, Task, TaskStatus, TaskPriority
from .framework_config import AgentFrameworkManager, FrameworkConfig, setup_agent_framework


# ============================================================================
# Example 1: Simple Custom Agent
# ============================================================================

class SimpleAgent(BaseAgent):
    """
    Simple example agent that echoes messages.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        
    async def initialize(self) -> None:
        """Initialize the agent."""
        self.set_status(AgentStatus.READY)
        self.logger.info(f"SimpleAgent {self.config.name} initialized")
    
    async def process(self, input_data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            response = {
                "status": "success",
                "message": f"Processed by {self.config.name}",
                "input": str(input_data),
                "metadata": metadata,
                "agent_id": self.config.agent_id,
            }
            
            return response
            
        finally:
            self.set_status(AgentStatus.READY)
    
    async def shutdown(self) -> None:
        """Shutdown the agent."""
        self.set_status(AgentStatus.SHUTTING_DOWN)
        self.logger.info(f"SimpleAgent {self.config.name} shutting down")
        self.set_status(AgentStatus.SHUTDOWN)


# ============================================================================
# Example 2: Echo Agent with Message Handling
# ============================================================================

class EchoAgent(BaseAgent):
    """
    Agent that echoes messages and handles specific message types.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._register_message_handlers()
        
    def _register_message_handlers(self) -> None:
        """Register custom message handlers."""
        self.register_message_handler("echo", self._handle_echo)
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("status", self._handle_status)
        
    async def _handle_echo(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle echo messages."""
        return {
            "status": "echo",
            "original": message.content,
            "from_agent": self.config.agent_id,
        }
        
    async def _handle_ping(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle ping messages."""
        return {
            "status": "pong",
            "from_agent": self.config.agent_id,
            "timestamp": message.timestamp.isoformat(),
        }
        
    async def _handle_status(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle status request messages."""
        return await self.health_check()
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        self.set_status(AgentStatus.READY)
        self.logger.info(f"EchoAgent {self.config.name} initialized")
    
    async def process(self, input_data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            response = {
                "status": "success",
                "echo": str(input_data),
                "agent": self.config.agent_id,
                "capabilities": [cap.value for cap in self.get_capabilities()],
            }
            
            return response
            
        finally:
            self.set_status(AgentStatus.READY)
    
    async def shutdown(self) -> None:
        """Shutdown the agent."""
        self.set_status(AgentStatus.SHUTTING_DOWN)
        self.logger.info(f"EchoAgent {self.config.name} shutting down")
        self.set_status(AgentStatus.SHUTDOWN)


# ============================================================================
# Example 3: Worker Agent with Task Queue
# ============================================================================

class WorkerAgent(BaseAgent):
    """
    Worker agent that processes tasks from a queue.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.task_queue = TaskQueue(self.config.agent_id)
        self._running = False
        
    async def initialize(self) -> None:
        """Initialize the worker agent."""
        self.set_status(AgentStatus.READY)
        self._running = True
        self.logger.info(f"WorkerAgent {self.config.name} initialized")
        
        # Start background task processor
        asyncio.create_task(self._process_queue())
    
    async def _process_queue(self) -> None:
        """Background task to process queue items."""
        while self._running:
            try:
                task = await self.task_queue.get_next_task()
                if task:
                    await self._execute_task(task)
                else:
                    await asyncio.sleep(0.1)  # Brief pause if no tasks
            except Exception as e:
                self.logger.error(f"Error processing queue: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task."""
        try:
            task.set_status(TaskStatus.RUNNING)
            
            self.set_status(AgentStatus.PROCESSING)
            result = await self.process(task.data, task.metadata)
            
            await self.task_queue.complete_task(task.id, result)
            
        except Exception as e:
            await self.task_queue.fail_task(task.id, str(e))
            self.logger.error(f"Task {task.id} failed: {e}")
        finally:
            self.set_status(AgentStatus.READY)
    
    async def process(self, input_data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input data."""
        # Simulate work
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "agent": self.config.agent_id,
            "processed": str(input_data),
            "metadata": metadata,
        }
    
    async def shutdown(self) -> None:
        """Shutdown the worker agent."""
        self._running = False
        self.set_status(AgentStatus.SHUTTING_DOWN)
        self.logger.info(f"WorkerAgent {self.config.name} shutting down")
        self.set_status(AgentStatus.SHUTDOWN)
    
    def submit_task(self, data: Any, priority: TaskPriority = TaskPriority.NORMAL,
                   metadata: Dict[str, Any] = None) -> str:
        """Submit a task to the worker's queue."""
        return self.task_queue.submit_task(
            data=data,
            priority=priority,
            metadata=metadata,
            source=self.config.agent_id,
        )


# ============================================================================
# Example 4: Framework Setup and Usage
# ============================================================================

async def run_framework_example() -> Dict[str, Any]:
    """
    Demonstrate the complete agent framework setup and usage.
    
    Returns:
        Dictionary with example results
    """
    
    # =========================================================================
    # Step 1: Setup framework with custom configuration
    # =========================================================================
    framework_config = FrameworkConfig(
        framework=AgentFramework.CUSTOM,
        enable_communication=True,
        enable_lifecycle_management=True,
        enable_task_queue=True,
        max_concurrent_agents=10,
        max_tasks_per_agent=5,
    )
    
    framework = AgentFrameworkManager(framework_config)
    
    # =========================================================================
    # Step 2: Create agent configurations
    # =========================================================================
    simple_agent_config = AgentConfig(
        agent_id="simple_agent_001",
        name="Simple Agent",
        version="1.0.0",
        agent_type=AgentType.CUSTOM,
        capabilities=[AgentCapability.QUERY],
        log_level="INFO",
    )
    
    echo_agent_config = AgentConfig(
        agent_id="echo_agent_001",
        name="Echo Agent",
        version="1.0.0",
        agent_type=AgentType.CUSTOM,
        capabilities=[AgentCapability.QUERY, AgentCapability.SUPPORT],
        log_level="INFO",
    )
    
    worker_agent_config = AgentConfig(
        agent_id="worker_agent_001",
        name="Worker Agent",
        version="1.0.0",
        agent_type=AgentType.CUSTOM,
        capabilities=[AgentCapability.ANALYSIS],
        log_level="INFO",
    )
    
    # =========================================================================
    # Step 3: Create and register agents
    # =========================================================================
    simple_agent = SimpleAgent(simple_agent_config)
    echo_agent = EchoAgent(echo_agent_config)
    worker_agent = WorkerAgent(worker_agent_config)
    
    framework.register_agent(simple_agent)
    framework.register_agent(echo_agent)
    framework.register_agent(worker_agent)
    
    # =========================================================================
    # Step 4: Initialize agents
    # =========================================================================
    await simple_agent.initialize()
    await echo_agent.initialize()
    await worker_agent.initialize()
    
    # =========================================================================
    # Step 5: Test direct processing
    # =========================================================================
    simple_result = await simple_agent.process({"test": "data"})
    echo_result = await echo_agent.process("Hello, World!")
    
    # =========================================================================
    # Step 6: Test message passing
    # =========================================================================
    communication = CommunicationChannel.get_instance()
    
    # Send message from simple agent to echo agent
    message = AgentMessage(
        sender="simple_agent_001",
        content="Ping from simple agent",
        message_type="ping",
    )
    
    message_response = await communication.send("echo_agent_001", message)
    
    # Test broadcast
    broadcast_result = await communication.broadcast(
        sender="simple_agent_001",
        content="System status check",
        message_type="status",
    )
    
    # =========================================================================
    # Step 7: Test task queue
    # =========================================================================
    task_id = worker_agent.submit_task(
        data={"work": "process this data"},
        priority=TaskPriority.NORMAL,
        metadata={"user": "framework_test"},
    )
    
    # Wait for task to complete
    await asyncio.sleep(0.5)
    
    task_status = worker_agent.task_queue.get_task_status(task_id)
    task_result = worker_agent.task_queue.get_task_result(task_id)
    
    # =========================================================================
    # Step 8: Get framework status
    # =========================================================================
    framework_status = framework.get_framework_status()
    
    # =========================================================================
    # Step 9: Cleanup
    # =========================================================================
    await simple_agent.shutdown()
    await echo_agent.shutdown()
    await worker_agent.shutdown()
    
    # =========================================================================
    # Return comprehensive results
    # =========================================================================
    return {
        "status": "success",
        "description": "Agent framework example completed successfully",
        "steps_completed": [
            "Framework initialization",
            "Agent creation and registration",
            "Agent initialization",
            "Direct processing test",
            "Message passing test",
            "Broadcast test",
            "Task queue test",
            "Framework status check",
            "Cleanup completed",
        ],
        "results": {
            "simple_agent": simple_result,
            "echo_agent": echo_result,
            "message_response": message_response,
            "broadcast_result": broadcast_result,
            "task_status": task_status,
            "task_result": task_result,
            "framework_status": framework_status,
        },
        "registered_agents": framework.list_agents(),
    }


# ============================================================================
# Main Execution (for testing)
# ============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the example
    result = asyncio.run(run_framework_example())
    
    # Print results
    import json
    print("\n" + "="*80)
    print("AI Agent Framework Example - Complete Results")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))
    print("="*80)
