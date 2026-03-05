# AI Agent Framework

Comprehensive framework for building and managing AI agents in the AI Data Labs platform.

## Overview

The AI Agent Framework provides a robust foundation for developing, deploying, and managing AI agents with support for:

- **Agent Lifecycle Management** - Initialize, monitor, and shutdown agents gracefully
- **Inter-Agent Communication** - Message passing between agents
- **Task Queuing** - Asynchronous task execution with retry logic
- **Agent Registry** - Central registry for agent discovery
- **Error Handling** - Comprehensive error types and recovery
- **Configuration Management** - Flexible configuration system

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Framework                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   BaseAgent  │  │ AgentConfig  │  │  AgentError  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Lifecycle   │  │  Registry    │  │Communication │     │
│  │   Manager    │  │              │  │   Channel    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                  ↓                  ↓              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Task Queue                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Define Your Agent

```python
from agents import BaseAgent, AgentConfig, AgentCapability
from typing import Any, Dict, Optional

class MyAgent(BaseAgent):
    """Custom agent implementation."""

    async def initialize(self) -> None:
        """Initialize the agent."""
        self.set_status(AgentStatus.INITIALIZING)

        # Set up LLM connections
        # Load resources
        # Validate configuration

        self.set_status(AgentStatus.READY)

    async def process(
        self,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)

        # Your agent logic here
        result = f"Processed: {input_data}"

        self.set_status(AgentStatus.READY)
        return result

    async def shutdown(self) -> None:
        """Shutdown the agent."""
        self.set_status(AgentStatus.SHUTTING_DOWN)

        # Cleanup resources
        # Close connections

        self.set_status(AgentStatus.SHUTDOWN)
```

### 2. Configure Your Agent

```python
from agents import AgentConfig, AgentType, AgentCapability

config = AgentConfig(
    agent_id="my-agent",
    name="My Agent",
    version="1.0.0",
    agent_type=AgentType.CUSTOM,
    capabilities=[
        AgentCapability.QUERY,
        AgentCapability.ANALYSIS,
    ],
    max_concurrent_tasks=5,
    task_timeout=300,
)
```

### 3. Use the Framework

```python
import asyncio
from agents import AgentRegistry, AgentLifecycleManager

async def main():
    # Create agent
    config = AgentConfig(agent_id="my-agent", name="My Agent")
    agent = MyAgent(config)

    # Register agent
    registry = AgentRegistry.get_instance()
    registry.register_agent(agent)

    # Initialize agent
    lifecycle = AgentLifecycleManager()
    lifecycle.register_agent(agent)
    await lifecycle.initialize_all()

    # Process tasks
    result = await agent.process("Hello, Agent!")
    print(result)

    # Shutdown
    await lifecycle.shutdown_all()

if __name__ == "__main__":
    asyncio.run(main())
```

## Components

### BaseAgent

Abstract base class for all agents. Provides:

- **Status Management** - Track agent state through lifecycle
- **Health Checks** - Monitor agent health
- **Message Handling** - Receive and respond to messages
- **Capabilities** - Define agent capabilities for discovery

```python
from agents import BaseAgent, AgentStatus

class MyAgent(BaseAgent):
    async def initialize(self) -> None:
        # Initialize agent
        pass

    async def process(self, input_data: Any, metadata=None) -> Any:
        # Process input
        return result

    async def shutdown(self) -> None:
        # Cleanup
        pass

    async def health_check(self) -> Dict[str, Any]:
        # Return health status
        return {"status": "ready"}
```

### AgentConfig

Configuration system for agents:

```python
from agents import AgentConfig, AgentType, LLMProviderConfig

config = AgentConfig(
    agent_id="query-agent",
    name="Query Agent",
    version="1.0.0",
    agent_type=AgentType.QUERY,
    capabilities=[AgentCapability.QUERY],

    # LLM configuration
    llm_provider=LLMProviderConfig(
        provider="claude",
        model="claude-3-5-sonnet-20241022",
        api_key="your-api-key",
        temperature=0.7,
        max_tokens=4096,
    ),

    # Retry configuration
    max_retries=3,
    retry_delay=1.0,

    # Resource limits
    max_concurrent_tasks=5,
    task_timeout=300,
)
```

### AgentRegistry

Central registry for agent discovery:

```python
from agents import AgentRegistry, AgentCapability

registry = AgentRegistry.get_instance()

# Register agent
registry.register_agent(agent)

# Get agent
agent = registry.get_agent("my-agent")

# Discover by capability
query_agents = registry.discover_by_capability(AgentCapability.QUERY)

# List all agents
all_agents = registry.list_all_agents()
```

### AgentLifecycleManager

Manage agent lifecycle:

```python
from agents import AgentLifecycleManager

manager = AgentLifecycleManager()

# Register agents
manager.register_agent(agent1)
manager.register_agent(agent2)

# Initialize all
results = await manager.initialize_all()

# Start health monitoring
await manager.start_health_monitoring()

# Shutdown all
await manager.shutdown_all()
```

### CommunicationChannel

Inter-agent messaging:

```python
from agents import CommunicationChannel, AgentMessage

channel = CommunicationChannel.get_instance()

# Send message
response = await channel.send(
    recipient="other-agent",
    message=AgentMessage(
        sender="my-agent",
        content="Hello!",
        message_type="request",
    ),
)

# Broadcast
responses = await channel.broadcast(
    sender="my-agent",
    content="Notification!",
    message_type="notification",
)

# Subscribe to message types
channel.subscribe("alert", my_handler)
```

### TaskQueue

Asynchronous task execution:

```python
from agents import TaskQueue, TaskPriority

queue = TaskQueue(max_concurrent_tasks=5)
await queue.start()

# Enqueue task
task_id = await queue.enqueue(
    agent_id="my-agent",
    function=my_async_function,
    args=(arg1, arg2),
    kwargs={"option": value},
    priority=TaskPriority.HIGH,
    timeout=300,
    max_retries=3,
)

# Get result
result = await queue.get_task_result(task_id, timeout=300)

# Check status
status = queue.get_task_status(task_id)

# Cancel task
await queue.cancel_task(task_id)

# List tasks
tasks = queue.list_tasks(agent_id="my-agent")

await queue.stop()
```

## Agent Status

Agents transition through these states:

```
UNINITIALIZED → INITIALIZING → READY → PROCESSING → READY
                                      ↓
                                    ERROR
                                      ↓
                                   SHUTTING_DOWN → SHUTDOWN
```

- **UNINITIALIZED** - Agent created but not initialized
- **INITIALIZING** - Agent is initializing
- **READY** - Agent ready to process tasks
- **PROCESSING** - Agent is processing a task
- **ERROR** - Agent encountered an error
- **SHUTTING_DOWN** - Agent is shutting down
- **SHUTDOWN** - Agent has shut down

## Agent Capabilities

Standard capabilities for agent discovery:

- **QUERY** - Execute queries and data retrieval
- **DESIGN** - Design and infrastructure automation
- **SUPPORT** - Customer support and assistance
- **ANALYSIS** - Data analysis and insights
- **GENERATION** - Content generation
- **VALIDATION** - Data validation and verification

## LLM Provider Integration

The framework provides built-in support for multiple LLM providers through a unified interface. The `llm_providers` module offers:

- **ClaudeProvider** - Anthropic Claude API (Claude 3.5 Sonnet, Claude 3 Opus)
- **GPT4Provider** - OpenAI API (GPT-4, GPT-4 Turbo, GPT-3.5 Turbo)
- **GLM5Provider** - Zhipu AI API (GLM-4, GLM-5, etc.)

### Basic Usage

```python
from agents import create_llm_provider, LLMMessage, LLMMessageRole

# Quick creation using environment variables
provider = create_llm_provider(
    provider="claude",
    model="claude-3-5-sonnet-20241022",
    temperature=0.7,
    max_tokens=4096,
)

# Or using configuration
from agents import LLMProviderConfig, ClaudeProvider

config = LLMProviderConfig(
    provider="claude",
    model="claude-3-5-sonnet-20241022",
    api_key="your-api-key",
    temperature=0.7,
    max_tokens=4096,
)
provider = ClaudeProvider(config)

await provider.initialize()

messages = [
    LLMMessage(role=LLMMessageRole.SYSTEM, content="You are a helpful assistant."),
    LLMMessage(role=LLMMessageRole.USER, content="Hello, how are you?"),
]

response = await provider.generate(messages)
print(response.content)
```

### Streaming Responses

```python
async for chunk in provider.generate_stream(messages):
    print(chunk, end="", flush=True)
```

### Integrating with Agents

Your agent can use an LLM provider like this:

```python
from agents import BaseAgent, AgentConfig, create_llm_provider

class MyLLMAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.llm_provider = None

    async def initialize(self) -> None:
        # Create LLM provider from agent config
        llm_config = config.llm_provider
        self.llm_provider = create_llm_provider(
            provider=llm_config.provider,
            model=llm_config.model,
            api_key=llm_config.api_key,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens,
        )
        await self.llm_provider.initialize()
        self.set_status(AgentStatus.READY)

    async def process(self, input_data, metadata=None):
        messages = [
            LLMMessage(role=LLMMessageRole.SYSTEM, content="You are a data analyst."),
            LLMMessage(role=LLMMessageRole.USER, content=input_data),
        ]

        response = await self.llm_provider.generate(messages)
        return response.content

    async def shutdown(self) -> None:
        if self.llm_provider:
            await self.llm_provider.shutdown()
        self.set_status(AgentStatus.SHUTDOWN)
```

### Supported Models

**Claude (Anthropic):**
- claude-3-5-sonnet-20241022 (default)
- claude-3-opus-20240229
- claude-3-haiku-20240307

**GPT-4 (OpenAI):**
- gpt-4-turbo-preview (default)
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

**GLM-5 (Zhipu AI):**
- glm-4 (default)
- glm-3-turbo

### Configuration via Environment Variables

For convenience, providers can use environment variables:

- CLAUDE_API_KEY or ANTHROPIC_API_KEY
- OPENAI_API_KEY
- ZHIPUAI_API_KEY

Set these in your environment or configure them directly in `AgentConfig.llm_provider`.

### Error Handling

LLM providers raise `AgentExecutionError` on failures:

```python
try:
    response = await provider.generate(messages)
except AgentExecutionError as e:
    print(f"LLM request failed: {e}")
```

Rate limiting and API errors are handled with automatic retries based on `config.retry_config`.

## Error Handling

The framework provides specific error types:

```python
from agents import (
    AgentError,
    AgentNotRegisteredError,
    AgentAlreadyRegisteredError,
    AgentInitializationError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentCommunicationError,
    AgentTaskQueueError,
    AgentConfigError,
)

try:
    await agent.process(data)
except AgentExecutionError as e:
    logger.error(f"Agent execution failed: {e}")
    # Handle error
```

## Testing

Run unit tests:

```bash
cd apps/backend
python -m pytest src/agents/tests.py -v
```

## Best Practices

1. **Always call `super().__init__`** when inheriting from BaseAgent
2. **Handle all exceptions** in your agent methods
3. **Use the task queue** for long-running operations
4. **Implement proper cleanup** in shutdown()
5. **Set appropriate timeouts** for all async operations
6. **Use health checks** for monitoring
7. **Register message handlers** for inter-agent communication
8. **Follow retry logic** with exponential backoff

## Examples

See the example agents in the `agents/` directory:

- `query_agent.py` - Query Agent (NL to SQL conversion) - [See detailed documentation](./QUERY_AGENT_README.md)
- `platform_designer.py` - Platform Designer Agent (infrastructure automation) - [See detailed documentation](./PLATFORM_DESIGNER_README.md)
- `support_agent.py` - Support Agent (24/7 customer assistance)
- `test_query_agent.py` - Comprehensive test suite for Query Agent

## API Reference

See the inline documentation for each module:

- `base.py` - Base agent class
- `config.py` - Configuration
- `lifecycle.py` - Lifecycle management
- `registry.py` - Registry and discovery
- `communication.py` - Messaging
- `task_queue.py` - Task execution
- `errors.py` - Error types

## License

MIT License - See LICENSE file
