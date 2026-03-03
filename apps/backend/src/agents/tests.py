"""
Unit tests for the AI agent framework.
"""

import asyncio
from typing import Any, Optional, Dict
import pytest

from .base import BaseAgent, AgentStatus, AgentCapability, AgentMessage
from .config import AgentConfig, AgentType, LLMProviderConfig
from .registry import AgentRegistry
from .lifecycle import AgentLifecycleManager
from .task_queue import TaskQueue, TaskPriority
from .errors import AgentExecutionError, AgentConfigError, AgentAlreadyRegisteredError
from .llm_providers import (
    LLMProviderType,
    LLMMessageRole,
    LLMMessage,
    LLMResponse,
    BaseLLMProvider,
    ClaudeProvider,
    GPT4Provider,
    GLM5Provider,
    LLMProviderFactory,
    create_llm_provider,
)


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


class TestLLMMessage:
    """Tests for LLMMessage."""

    def test_create_message(self):
        """Test creating an LLM message."""
        msg = LLMMessage(
            role=LLMMessageRole.USER,
            content="Hello, how are you?",
        )

        assert msg.role == LLMMessageRole.USER
        assert msg.content == "Hello, how are you?"

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = LLMMessage(
            role=LLMMessageRole.USER,
            content="Test",
            metadata={"test": "value"},
        )

        data = msg.to_dict()

        assert data["role"] == "user"
        assert data["content"] == "Test"
        assert data["metadata"]["test"] == "value"

    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "role": "system",
            "content": "You are a helpful assistant",
        }

        msg = LLMMessage.from_dict(data)

        assert msg.role == LLMMessageRole.SYSTEM
        assert msg.content == "You are a helpful assistant"


class TestLLMResponse:
    """Tests for LLMResponse."""

    def test_create_response(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello! I'm doing well, thank you.",
            model="claude-3-5-sonnet-20241022",
            provider="claude",
            tokens_used={"input_tokens": 10, "output_tokens": 20},
            finish_reason="end_turn",
        )

        assert response.content == "Hello! I'm doing well, thank you."
        assert response.provider == "claude"
        assert response.tokens_used["output_tokens"] == 20

    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = LLMResponse(
            content="Response text",
            model="gpt-4-turbo-preview",
            provider="openai",
            tokens_used={"total_tokens": 100},
        )

        data = response.to_dict()

        assert data["content"] == "Response text"
        assert data["provider"] == "openai"
        assert data["tokens_used"]["total_tokens"] == 100


class TestLLMProviderConfig:
    """Tests for LLMProviderConfig."""

    def test_create_config(self):
        """Test creating an LLM provider configuration."""
        config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            temperature=0.5,
            max_tokens=2048,
            timeout=60,
        )

        assert config.provider == "claude"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.api_key == "test-key"
        assert config.temperature == 0.5

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = LLMProviderConfig(
            provider="gpt4",
            model="gpt-4-turbo-preview",
            api_key="secret-key",
        )

        data = config.to_dict()

        assert data["provider"] == "gpt4"
        assert data["model"] == "gpt-4-turbo-preview"
        assert data["api_key"] == "***"  # masked in to_dict


class TestClaudeProvider:
    """Tests for ClaudeProvider."""

    def test_initialize_without_api_key(self):
        """Test that initialization fails without API key."""
        config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key=None,
        )
        provider = ClaudeProvider(config)

        with pytest.raises(AgentExecutionError, match="Claude API key is required"):
            asyncio.run(provider.initialize())

    def test_initialize_with_api_key(self, monkeypatch):
        """Test initialization with API key."""
        config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )
        provider = ClaudeProvider(config)

        # Should not raise an error
        asyncio.run(provider.initialize())

        assert provider.config.api_key == "test-key"


class TestGPT4Provider:
    """Tests for GPT4Provider."""

    def test_initialize_without_api_key(self):
        """Test that initialization fails without API key."""
        config = LLMProviderConfig(
            provider="gpt4",
            model="gpt-4-turbo-preview",
            api_key=None,
        )
        provider = GPT4Provider(config)

        with pytest.raises(AgentExecutionError, match="OpenAI API key is required"):
            asyncio.run(provider.initialize())

    def test_initialize_with_api_key(self, monkeypatch):
        """Test initialization with API key."""
        config = LLMProviderConfig(
            provider="gpt4",
            model="gpt-4-turbo-preview",
            api_key="test-key",
        )
        provider = GPT4Provider(config)

        # Should not raise an error
        asyncio.run(provider.initialize())


class TestGLM5Provider:
    """Tests for GLM5Provider."""

    def test_initialize_without_api_key(self):
        """Test that initialization fails without API key."""
        config = LLMProviderConfig(
            provider="glm5",
            model="glm-4",
            api_key=None,
        )
        provider = GLM5Provider(config)

        with pytest.raises(AgentExecutionError, match="Zhipu AI API key is required"):
            asyncio.run(provider.initialize())

    def test_initialize_with_api_key(self, monkeypatch):
        """Test initialization with API key."""
        config = LLMProviderConfig(
            provider="glm5",
            model="glm-4",
            api_key="test-key",
        )
        provider = GLM5Provider(config)

        # Should not raise an error
        asyncio.run(provider.initialize())


class TestLLMProviderFactory:
    """Tests for LLMProviderFactory."""

    def test_create_claude_provider(self):
        """Test creating a Claude provider."""
        config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )
        provider = LLMProviderFactory.create(config)

        assert isinstance(provider, ClaudeProvider)
        assert provider.config.provider == "claude"

    def test_create_gpt4_provider(self):
        """Test creating a GPT-4 provider."""
        config = LLMProviderConfig(
            provider="gpt4",
            model="gpt-4-turbo-preview",
            api_key="test-key",
        )
        provider = LLMProviderFactory.create(config)

        assert isinstance(provider, GPT4Provider)
        assert provider.config.provider == "gpt4"

    def test_create_glm5_provider(self):
        """Test creating a GLM-5 provider."""
        config = LLMProviderConfig(
            provider="glm5",
            model="glm-4",
            api_key="test-key",
        )
        provider = LLMProviderFactory.create(config)

        assert isinstance(provider, GLM5Provider)
        assert provider.config.provider == "glm5"

    def test_create_unsupported_provider(self):
        """Test that creating an unsupported provider raises error."""
        config = LLMProviderConfig(
            provider="unsupported",
            model="test-model",
            api_key="test-key",
        )

        with pytest.raises(AgentExecutionError, match="Unsupported LLM provider"):
            LLMProviderFactory.create(config)

    def test_list_providers(self):
        """Test listing available providers."""
        providers = LLMProviderFactory.list_providers()

        assert "claude" in providers
        assert "gpt4" in providers
        assert "glm5" in providers

    def test_register_custom_provider(self):
        """Test registering a custom provider."""

        class CustomProvider(BaseLLMProvider):
            async def initialize(self) -> None:
                pass

            async def generate(self, messages, temperature=None, max_tokens=None, **kwargs):
                pass

            async def generate_stream(self, messages, temperature=None, max_tokens=None, **kwargs):
                pass

        LLMProviderFactory.register_provider("custom", CustomProvider)

        providers = LLMProviderFactory.list_providers()
        assert "custom" in providers

        # Clean up
        LLMProviderFactory._providers.pop("custom")


class TestCreateLLMProviderFunction:
    """Tests for the create_llm_provider convenience function."""

    def test_create_claude_with_defaults(self, monkeypatch):
        """Test creating Claude provider with defaults from environment."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("DEFAULT_LLM_PROVIDER", raising=False)
        monkeypatch.delenv("DEFAULT_LLM_MODEL", raising=False)

        provider = create_llm_provider(provider="claude")

        assert isinstance(provider, ClaudeProvider)
        assert provider.config.model == "claude-3-5-sonnet-20241022"
        assert provider.config.api_key == "test-key"

    def test_create_gpt4_with_overrides(self, monkeypatch):
        """Test creating GPT-4 provider with custom model."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        provider = create_llm_provider(
            provider="gpt4",
            model="gpt-4-vision-preview",
            temperature=0.3,
            max_tokens=1024,
        )

        assert isinstance(provider, GPT4Provider)
        assert provider.config.model == "gpt-4-vision-preview"
        assert provider.config.temperature == 0.3
        assert provider.config.max_tokens == 1024

    def test_create_glm5_with_explicit_key(self):
        """Test creating GLM-5 provider with explicit API key."""
        provider = create_llm_provider(
            provider="glm5",
            api_key="explicit-key",
            model="glm-4",
        )

        assert isinstance(provider, GLM5Provider)
        assert provider.config.api_key == "explicit-key"

    def test_create_with_missing_api_key(self, monkeypatch):
        """Test that creating provider without API key raises error."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ZHIPUAI_API_KEY", raising=False)

        with pytest.raises(AgentExecutionError, match="API key is required"):
            create_llm_provider(provider="claude")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
