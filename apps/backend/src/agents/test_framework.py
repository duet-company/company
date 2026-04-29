"""
Test suite for AI Agent Framework

Validates:
- Agent creation and registration
- Lifecycle management
- Communication between agents
- Task queue operations
- Registry and discovery
- Error handling
"""

import asyncio
import unittest
from typing import Any, Dict, List
from unittest.mock import AsyncMock, patch

from .base import BaseAgent, AgentStatus, AgentCapability, AgentMessage
from .config import AgentConfig, AgentType, LLMProviderConfig, RetryConfig
from .errors import (
    AgentError,
    AgentNotRegisteredError,
    AgentAlreadyRegisteredError,
    AgentInitializationError,
    AgentExecutionError,
)
from .registry import AgentRegistry
from .communication import CommunicationChannel
from .task_queue import TaskQueue, Task, TaskStatus, TaskPriority
from .framework_config import AgentFrameworkManager, FrameworkConfig, AgentFramework


# ============================================================================
# Test Helper Agents
# ============================================================================

class TestAgent(BaseAgent):
    """Test agent for framework validation."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.initialized = False
        self.processed_data = []
        
    async def initialize(self) -> None:
        """Initialize test agent."""
        self.initialized = True
        self.set_status(AgentStatus.READY)
        
    async def process(self, input_data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)
        self.processed_data.append(input_data)
        
        try:
            return {
                "status": "success",
                "agent_id": self.config.agent_id,
                "processed": str(input_data),
                "metadata": metadata,
            }
        finally:
            self.set_status(AgentStatus.READY)
    
    async def shutdown(self) -> None:
        """Shutdown test agent."""
        self.set_status(AgentStatus.SHUTTING_DOWN)
        self.initialized = False
        self.set_status(AgentStatus.SHUTDOWN)


# ============================================================================
# Test Cases
# ============================================================================

class TestAgentFramework(unittest.TestCase):
    """Test suite for AI Agent Framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry.get_instance()
        self.communication = CommunicationChannel.get_instance()
        
        # Clear registry before each test
        self.registry.clear_all()
        self.communication.clear_history()
        
        # Create test configurations
        self.agent_config = AgentConfig(
            agent_id="test_agent_001",
            name="Test Agent",
            version="1.0.0",
            agent_type=AgentType.CUSTOM,
            capabilities=[AgentCapability.QUERY],
        )
        
        self.agent = TestAgent(self.agent_config)
    
    def tearDown(self):
        """Clean up after tests."""
        self.registry.clear_all()
        self.communication.clear_history()
    
    # =========================================================================
    # Agent Lifecycle Tests
    # =========================================================================
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        asyncio.run(self.agent.initialize())
        
        self.assertTrue(self.agent.initialized)
        self.assertEqual(self.agent.status, AgentStatus.READY)
    
    def test_agent_processing(self):
        """Test agent processing."""
        asyncio.run(self.agent.initialize())
        
        result = asyncio.run(self.agent.process({"test": "data"}))
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["agent_id"], "test_agent_001")
        self.assertEqual(len(self.agent.processed_data), 1)
    
    def test_agent_shutdown(self):
        """Test agent shutdown."""
        asyncio.run(self.agent.initialize())
        self.assertEqual(self.agent.status, AgentStatus.READY)
        
        asyncio.run(self.agent.shutdown())
        self.assertEqual(self.agent.status, AgentStatus.SHUTDOWN)
        self.assertFalse(self.agent.initialized)
    
    def test_agent_status_transitions(self):
        """Test agent status transitions."""
        self.assertEqual(self.agent.status, AgentStatus.UNINITIALIZED)
        
        asyncio.run(self.agent.initialize())
        self.assertEqual(self.agent.status, AgentStatus.READY)
        
        asyncio.run(self.agent.shutdown())
        self.assertEqual(self.agent.status, AgentStatus.SHUTDOWN)
    
    # =========================================================================
    # Registry Tests
    # =========================================================================
    
    def test_register_agent(self):
        """Test agent registration."""
        self.registry.register_agent(self.agent)
        
        retrieved = self.registry.get_agent("test_agent_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.config.agent_id, "test_agent_001")
    
    def test_register_duplicate_agent(self):
        """Test duplicate agent registration raises error."""
        self.registry.register_agent(self.agent)
        
        with self.assertRaises(AgentAlreadyRegisteredError):
            self.registry.register_agent(self.agent)
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        self.registry.register_agent(self.agent)
        self.assertIsNotNone(self.registry.get_agent("test_agent_001"))
        
        self.registry.unregister_agent("test_agent_001")
        self.assertIsNone(self.registry.get_agent("test_agent_001"))
    
    def test_unregister_nonexistent_agent(self):
        """Test unregistering non-existent agent raises error."""
        with self.assertRaises(AgentNotRegisteredError):
            self.registry.unregister_agent("nonexistent")
    
    def test_discover_by_capability(self):
        """Test agent discovery by capability."""
        self.registry.register_agent(self.agent)
        
        query_agents = self.registry.discover_by_capability(AgentCapability.QUERY)
        self.assertEqual(len(query_agents), 1)
        self.assertEqual(query_agents[0].config.agent_id, "test_agent_001")
    
    def test_list_all_agents(self):
        """Test listing all agents."""
        self.registry.register_agent(self.agent)
        
        agents = self.registry.list_all_agents()
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["agent_id"], "test_agent_001")
    
    def test_get_agent_count(self):
        """Test getting agent count."""
        self.assertEqual(self.registry.get_count(), 0)
        
        self.registry.register_agent(self.agent)
        self.assertEqual(self.registry.get_count(), 1)
    
    # =========================================================================
    # Communication Tests
    # =========================================================================
    
    def test_direct_messaging(self):
        """Test direct messaging between agents."""
        asyncio.run(self.agent.initialize())
        self.registry.register_agent(self.agent)
        
        message = AgentMessage(
            sender="test_sender",
            content="Hello, Agent!",
            message_type="request",
        )
        
        response = asyncio.run(self.communication.send("test_agent_001", message))
        
        self.assertEqual(response["status"], "received")
        self.assertEqual(response["message_id"], message.message_id)
    
    def test_broadcast_messaging(self):
        """Test broadcasting messages."""
        asyncio.run(self.agent.initialize())
        self.registry.register_agent(self.agent)
        
        results = asyncio.run(
            self.communication.broadcast(
                sender="test_sender",
                content="Broadcast message",
                message_type="notification",
            )
        )
        
        self.assertIn("test_agent_001", results)
    
    def test_message_history(self):
        """Test message history recording."""
        asyncio.run(self.agent.initialize())
        self.registry.register_agent(self.agent)
        
        message = AgentMessage(
            sender="test_sender",
            content="Test message",
            message_type="request",
        )
        
        asyncio.run(self.communication.send("test_agent_001", message))
        
        history = self.communication.get_message_history(limit=10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["from"], "test_sender")
        self.assertEqual(history[0]["to"], "test_agent_001")
    
    # =========================================================================
    # Task Queue Tests
    # =========================================================================
    
    def test_task_submission(self):
        """Test task submission to queue."""
        task_queue = TaskQueue("test_agent_001")
        
        task_id = task_queue.submit_task(
            data={"work": "test"},
            priority=TaskPriority.NORMAL,
            metadata={"user": "test"},
        )
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, task_queue.tasks)
    
    def test_task_completion(self):
        """Test task completion."""
        task_queue = TaskQueue("test_agent_001")
        
        task_id = task_queue.submit_task(data={"work": "test"})
        task = task_queue.get_task(task_id)
        
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        task_queue.complete_task(task_id, {"result": "done"})
        task = task_queue.get_task(task_id)
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result["result"], "done")
    
    def test_task_failure(self):
        """Test task failure."""
        task_queue = TaskQueue("test_agent_001")
        
        task_id = task_queue.submit_task(data={"work": "test"})
        task_queue.fail_task(task_id, "Something went wrong")
        
        task = task_queue.get_task(task_id)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error, "Something went wrong")
    
    def test_task_priority(self):
        """Test task priority ordering."""
        task_queue = TaskQueue("test_agent_001")
        
        # Submit tasks with different priorities
        low_id = task_queue.submit_task(data="low", priority=TaskPriority.LOW)
        high_id = task_queue.submit_task(data="high", priority=TaskPriority.HIGH)
        normal_id = task_queue.submit_task(data="normal", priority=TaskPriority.NORMAL)
        
        # Get next task - should be high priority first
        next_task = task_queue.get_next_task()
        self.assertEqual(next_task.id, high_id)
    
    # =========================================================================
    # Framework Manager Tests
    # =========================================================================
    
    def test_framework_initialization(self):
        """Test framework manager initialization."""
        config = FrameworkConfig(
            framework=AgentFramework.CUSTOM,
            enable_communication=True,
            enable_lifecycle_management=True,
        )
        
        manager = AgentFrameworkManager(config)
        status = manager.initialize_framework()
        
        self.assertTrue(status["initialized"])
        self.assertEqual(status["framework"], "custom")
    
    def test_framework_agent_registration(self):
        """Test framework agent registration."""
        config = FrameworkConfig()
        manager = AgentFrameworkManager(config)
        manager.initialize_framework()
        
        result = manager.register_agent(self.agent)
        
        self.assertEqual(result["status"], "registered")
        self.assertEqual(result["agent_id"], "test_agent_001")
    
    def test_framework_status(self):
        """Test framework status reporting."""
        config = FrameworkConfig()
        manager = AgentFrameworkManager(config)
        manager.initialize_framework()
        manager.register_agent(self.agent)
        
        status = manager.get_framework_status()
        
        self.assertTrue(status["initialized"])
        self.assertEqual(status["agents_registered"], 1)
    
    # =========================================================================
    # Error Handling Tests
    # =========================================================================
    
    def test_agent_error_hierarchy(self):
        """Test agent error class hierarchy."""
        self.assertTrue(issubclass(AgentNotRegisteredError, AgentError))
        self.assertTrue(issubclass(AgentAlreadyRegisteredError, AgentError))
        self.assertTrue(issubclass(AgentInitializationError, AgentError))
        self.assertTrue(issubclass(AgentExecutionError, AgentError))
    
    def test_communication_error(self):
        """Test communication error when agent not found."""
        message = AgentMessage(
            sender="test",
            content="Hello",
            message_type="request",
        )
        
        with self.assertRaises(Exception):  # AgentCommunicationError
            asyncio.run(self.communication.send("nonexistent", message))
    
    # =========================================================================
    # Integration Tests
    # =========================================================================
    
    def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        # Initialize
        asyncio.run(self.agent.initialize())
        self.assertEqual(self.agent.status, AgentStatus.READY)
        
        # Register
        self.registry.register_agent(self.agent)
        self.assertEqual(self.registry.get_count(), 1)
        
        # Process
        result = asyncio.run(self.agent.process({"test": "data"}))
        self.assertEqual(result["status"], "success")
        
        # Communicate
        message = AgentMessage(
            sender="test",
            content="Ping",
            message_type="request",
        )
        response = asyncio.run(self.communication.send("test_agent_001", message))
        self.assertEqual(response["status"], "received")
        
        # Shutdown
        asyncio.run(self.agent.shutdown())
        self.assertEqual(self.agent.status, AgentStatus.SHUTDOWN)
    
    def test_multiple_agents_communication(self):
        """Test communication between multiple agents."""
        # Create second agent
        agent2_config = AgentConfig(
            agent_id="test_agent_002",
            name="Test Agent 2",
            version="1.0.0",
            agent_type=AgentType.CUSTOM,
            capabilities=[AgentCapability.DESIGN],
        )
        agent2 = TestAgent(agent2_config)
        
        # Initialize and register both
        asyncio.run(self.agent.initialize())
        asyncio.run(agent2.initialize())
        
        self.registry.register_agent(self.agent)
        self.registry.register_agent(agent2)
        
        # Test communication between agents
        message = AgentMessage(
            sender="test_agent_001",
            content="Hello from agent 1",
            message_type="request",
        )
        
        response = asyncio.run(self.communication.send("test_agent_002", message))
        self.assertEqual(response["status"], "received")
        
        # Cleanup
        asyncio.run(agent2.shutdown())


# ============================================================================
# Test Runner
# ============================================================================

def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAgentFramework)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    run_tests()
