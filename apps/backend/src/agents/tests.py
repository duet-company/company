"""
Unit tests for the AI agent framework.
"""

import asyncio
from typing import Any, Optional, Dict
import pytest

from .base import BaseAgent, AgentStatus, AgentCapability, AgentMessage
from .config import AgentConfig, AgentType, RetryConfig
from .registry import AgentRegistry
from .lifecycle import AgentLifecycleManager
from .task_queue import TaskQueue, TaskPriority
from .errors import AgentExecutionError, AgentConfigError, AgentAlreadyRegisteredError


# Test agent implementation
class TestAgent(BaseAgent):
    """Simple test agent for testing."""

    async def initialize(self) -> None:
        """Initialize the test agent."""
        self.set_status(AgentStatus.INITIALIZING)
        await asyncio.sleep(0.1)
        self.set_status(AgentStatus.READY)

    async def process(self, input_data: Any, metadata: Optional[Dict] = None) -> Any:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)
        await asyncio.sleep(0.1)

        if input_data == "error":
            raise AgentExecutionError("Test error")

        result = f"processed: {input_data}"
        self.set_status(AgentStatus.READY)
        return result

    async def shutdown(self) -> None:
        """Shutdown the agent."""
        self.set_status(AgentStatus.SHUTTING_DOWN)
        await asyncio.sleep(0.1)
        self.set_status(AgentStatus.SHUTDOWN)


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_create_config(self):
        """Test creating an agent configuration."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            agent_type=AgentType.CUSTOM,
        )

        assert config.agent_id == "test-agent"
        assert config.name == "Test Agent"
        assert config.version == "1.0.0"
        assert config.agent_type == AgentType.CUSTOM

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "agent_id": "test-agent",
            "name": "Test Agent",
            "version": "1.0.0",
            "agent_type": "custom",
            "capabilities": ["query", "analysis"],
        }

        config = AgentConfig.from_dict(config_dict)

        assert config.agent_id == "test-agent"
        assert len(config.capabilities) == 2

    def test_config_validation(self):
        """Test config validation."""
        with pytest.raises(AgentConfigError):
            AgentConfig(agent_id="", name="Test")


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_singleton(self):
        """Test that registry is a singleton."""
        registry1 = AgentRegistry.get_instance()
        registry2 = AgentRegistry.get_instance()

        assert registry1 is registry2

    def test_register_agent(self):
        """Test registering an agent."""
        registry = AgentRegistry.get_instance()
        config = AgentConfig(agent_id="test-agent", name="Test Agent")
        agent = TestAgent(config)

        registry.register_agent(agent)
        assert registry.get_agent("test-agent") is agent

    def test_register_duplicate(self):
        """Test that duplicate registration raises error."""
        registry = AgentRegistry.get_instance()
        config = AgentConfig(agent_id="test-agent", name="Test Agent")
        agent1 = TestAgent(config)

        registry.register_agent(agent1)

        agent2 = TestAgent(config)
        with pytest.raises(AgentAlreadyRegisteredError):
            registry.register_agent(agent2)

    def test_discover_by_capability(self):
        """Test discovering agents by capability."""
        registry = AgentRegistry.get_instance()

        config1 = AgentConfig(
            agent_id="agent-1",
            name="Agent 1",
            capabilities=[AgentCapability.QUERY],
        )
        agent1 = TestAgent(config1)

        config2 = AgentConfig(
            agent_id="agent-2",
            name="Agent 2",
            capabilities=[AgentCapability.DESIGN],
        )
        agent2 = TestAgent(config2)

        config3 = AgentConfig(
            agent_id="agent-3",
            name="Agent 3",
            capabilities=[AgentCapability.QUERY, AgentCapability.ANALYSIS],
        )
        agent3 = TestAgent(config3)

        registry.register_agent(agent1)
        registry.register_agent(agent2)
        registry.register_agent(agent3)

        query_agents = registry.discover_by_capability(AgentCapability.QUERY)
        assert len(query_agents) == 2

        design_agents = registry.discover_by_capability(AgentCapability.DESIGN)
        assert len(design_agents) == 1


class TestAgentLifecycleManager:
    """Tests for AgentLifecycleManager."""

    @pytest.mark.asyncio
    async def test_lifecycle_initialization(self):
        """Test agent lifecycle initialization."""
        manager = AgentLifecycleManager()

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        manager.register_agent(agent)

        results = await manager.initialize_all()
        assert results["test-agent"] is True
        assert agent.status == AgentStatus.READY

    @pytest.mark.asyncio
    async def test_lifecycle_shutdown(self):
        """Test agent lifecycle shutdown."""
        manager = AgentLifecycleManager()

        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        manager.register_agent(agent)

        await manager.initialize_all()
        await manager.shutdown_all()

        assert agent.status == AgentStatus.SHUTDOWN


class TestCommunicationChannel:
    """Tests for CommunicationChannel."""

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending a message between agents."""
        registry = AgentRegistry.get_instance()

        config1 = AgentConfig(
            agent_id="sender",
            name="Sender",
            capabilities=[AgentCapability.QUERY],
        )
        sender = TestAgent(config1)

        config2 = AgentConfig(
            agent_id="receiver",
            name="Receiver",
            capabilities=[AgentCapability.QUERY],
        )
        receiver = TestAgent(config2)

        registry.register_agent(sender)
        registry.register_agent(receiver)

        await sender.initialize()
        await receiver.initialize()

        message = AgentMessage(
            sender="sender",
            content="test message",
            message_type="request",
        )

        response = await receiver.receive_message(message)
        assert response is not None


class TestTaskQueue:
    """Tests for TaskQueue."""

    @pytest.mark.asyncio
    async def test_enqueue_and_execute(self):
        """Test enqueuing and executing a task."""
        queue = TaskQueue(max_concurrent_tasks=1)

        async def simple_task(x: int) -> int:
            return x * 2

        await queue.start()

        task_id = await queue.enqueue(
            agent_id="test-agent",
            function=simple_task,
            args=(5,),
        )

        result = await queue.get_task_result(task_id, timeout=5.0)
        assert result == 10

        await queue.stop()

    @pytest.mark.asyncio
    async def test_task_priority(self):
        """Test that higher priority tasks execute first."""
        queue = TaskQueue(max_concurrent_tasks=1)

        execution_order = []

        async def priority_task(name: str, delay: float):
            await asyncio.sleep(delay)
            execution_order.append(name)

        await queue.start()

        # Enqueue tasks with different priorities
        await queue.enqueue(
            agent_id="test-agent",
            function=priority_task,
            args=("low", 0.1),
            priority=TaskPriority.LOW,
        )

        await queue.enqueue(
            agent_id="test-agent",
            function=priority_task,
            args=("high", 0.1),
            priority=TaskPriority.HIGH,
        )

        await queue.enqueue(
            agent_id="test-agent",
            function=priority_task,
            args=("normal", 0.1),
            priority=TaskPriority.NORMAL,
        )

        # Wait for all tasks to complete
        await asyncio.sleep(1.0)

        assert execution_order[0] == "high"
        assert execution_order[1] == "normal"
        assert execution_order[2] == "low"

        await queue.stop()

    @pytest.mark.asyncio
    async def test_task_retry(self):
        """Test task retry on failure."""
        queue = TaskQueue(max_concurrent_tasks=1)

        attempt_count = 0

        async def failing_task():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"

        await queue.start()

        task_id = await queue.enqueue(
            agent_id="test-agent",
            function=failing_task,
            max_retries=3,
        )

        result = await queue.get_task_result(task_id, timeout=10.0)
        assert result == "success"
        assert attempt_count == 3

        await queue.stop()


class TestBaseAgent:
    """Tests for BaseAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initialization."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        assert agent.status == AgentStatus.UNINITIALIZED

        await agent.initialize()

        assert agent.status == AgentStatus.READY

    @pytest.mark.asyncio
    async def test_agent_processing(self):
        """Test agent processing."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        await agent.initialize()

        result = await agent.process("test input")

        assert result == "processed: test input"

    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        await agent.initialize()

        with pytest.raises(AgentExecutionError):
            await agent.process("error")

    @pytest.mark.asyncio
    async def test_agent_health_check(self):
        """Test agent health check."""
        config = AgentConfig(
            agent_id="test-agent",
            name="Test Agent",
            capabilities=[AgentCapability.QUERY],
        )
        agent = TestAgent(config)

        await agent.initialize()

        health = await agent.health_check()

        assert health["agent_id"] == "test-agent"
        assert health["name"] == "Test Agent"
        assert health["status"] == "ready"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
