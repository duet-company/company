# AI Agent Framework

A comprehensive, production-ready framework for building and managing AI agents with support for:

- **Agent lifecycle management** (initialization, processing, shutdown)
- **Inter-agent communication** (direct messaging, broadcasting, request/response patterns)
- **Task queuing and execution** with priority and retry support
- **Agent registration and discovery** by capability, type, or name
- **Retry logic and error handling** with configurable backoff
- **LLM provider integration** (Claude, GPT-4, GLM-5, custom providers)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Framework                          │
├─────────────────────────────────────────────────────────────┤
│  BaseAgent (abstract)                                      │
│  ├── initialize()     # Setup agent resources              │
│  ├── process()        # Main processing logic              │
│  ├── shutdown()       # Cleanup resources                  │
│  └── send_message()  # Communicate with other agents      │
├─────────────────────────────────────────────────────────────┤
│  AgentRegistry (singleton)                                 │
│  ├── register_agent()       # Register agent instance      │
│  ├── discover_by_capability() # Find agents by capability │
│  └── list_all_agents()      # List registered agents      │
├─────────────────────────────────────────────────────────────┤
│  CommunicationChannel (singleton)                          │
│  ├── send()             # Direct messaging                 │
│  ├── broadcast()        # Broadcast to all agents          │
│  ├── send_request()     # Request/response pattern         │
│  └── publish()          # Publish/subscribe pattern        │
├─────────────────────────────────────────────────────────────┤
│  TaskQueue (per-agent)                                       │
│  ├── submit_task()      # Submit task to queue             │
│  ├── complete_task()    # Mark task as complete            │
│  └── fail_task()        # Mark task as failed              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Create an Agent

```python
import asyncio
from agents.base import BaseAgent, AgentStatus, AgentCapability
from agents.config import AgentConfig, AgentType

class MyAgent(BaseAgent):
    """Custom agent implementation."""
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        print(f"Initializing {self.config.name}")
        self.set_status(AgentStatus.READY)
    
    async def process(self, input_data: Any, metadata: Dict[str, Any] = None) -> Any:
        """Process input data."""
        self.set_status(AgentStatus.PROCESSING)
        
        try:
            # Your processing logic here
            result = {
                "status": "success",
                "input": str(input_data),
                "agent": self.config.agent_id,
            }
            return result
        finally:
            self.set_status(AgentStatus.READY)
    
    async def shutdown(self) -> None:
        """Cleanup resources."""
        print(f"Shutting down {self.config.name}")
        self.set_status(AgentStatus.SHUTDOWN)

# Create configuration
config = AgentConfig(
    agent_id="my_agent_001",
    name="My Agent",
    version="1.0.0",
    agent_type=AgentType.CUSTOM,
    capabilities=[AgentCapability.QUERY],
)

# Create agent instance
agent = MyAgent(config)

# Initialize
asyncio.run(agent.initialize())

# Process data
result = asyncio.run(agent.process({"test": "data"}))
print(result)
```

### 2. Register Agent with Registry

```python
from agents.registry import AgentRegistry

# Get registry instance
registry = AgentRegistry.get_instance()

# Register agent
registry.register_agent(agent)

# Discover agents by capability
query_agents = registry.discover_by_capability(AgentCapability.QUERY)
print(f"Found {len(query_agents)} query agents")

# List all agents
all_agents = registry.list_all_agents()
for agent_info in all_agents:
    print(f"Agent: {agent_info['name']} ({agent_info['status']})")
```

### 3. Agent Communication

```python
from agents.communication import CommunicationChannel
from agents.base import AgentMessage

# Get communication channel
channel = CommunicationChannel.get_instance()

# Send message from one agent to another
message = AgentMessage(
    sender="agent_a",
    content={"query": "What is the revenue?"},
    message_type="request",
)

response = asyncio.run(
    channel.send("agent_b", message)
)
print(f"Response: {response}")

# Broadcast message to all agents
broadcast_results = asyncio.run(
    channel.broadcast(
        sender="agent_a",
        content="System update available",
        message_type="notification",
    )
)
print(f"Broadcast results: {broadcast_results}")
```

### 4. Task Queue Usage

```python
from agents.task_queue import TaskQueue, TaskPriority

# Each agent has its own task queue
task_queue = TaskQueue("my_agent_001")

# Submit task
task_id = task_queue.submit_task(
    data={"work": "process this"},
    priority=TaskPriority.HIGH,
    metadata={"user": "john"},
)

# Check task status
task = task_queue.get_task(task_id)
print(f"Task status: {task.status}")

# Complete task (usually done inside agent)
task_queue.complete_task(task_id, {"result": "done"})
```

## Framework Configuration

Use `AgentFrameworkManager` for easy setup:

```python
from agents.framework_config import AgentFrameworkManager, FrameworkConfig, setup_agent_framework

# Create framework configuration
config = FrameworkConfig(
    framework=AgentFramework.CUSTOM,
    enable_lifecycle_management=True,
    enable_communication=True,
    enable_task_queue=True,
    max_concurrent_agents=10,
)

# Setup framework
framework = AgentFrameworkManager(config)
status = framework.initialize_framework()

print(f"Framework initialized: {status}")
print(f"Registered agents: {framework.list_agents()}")
```

## Examples

See `example_framework_usage.py` for comprehensive examples:

- **SimpleAgent**: Basic echo agent
- **EchoAgent**: Agent with message handlers
- **WorkerAgent**: Agent with task queue processing
- **Framework Setup**: Complete framework initialization and usage

Run the example:
```bash
python -m agents.example_framework_usage
```

## Key Components

### BaseAgent
Abstract base class that all agents must inherit from. Provides:
- Lifecycle methods: `initialize()`, `process()`, `shutdown()`
- Status management: `set_status()`, `get_status()`
- Communication: `send_message()`, `receive_message()`
- Capability registration: `get_capabilities()`

### AgentConfig
Configuration class for agents with:
- Basic info: agent_id, name, version, type
- LLM configuration: provider, model, API keys
- Retry configuration: max_retries, delay, backoff
- Resource limits: max_concurrent_tasks, memory limits
- Communication settings: queues, timeouts

### AgentRegistry (Singleton)
Central registry for agent management:
- Register/unregister agents
- Discover by capability, type, or name
- Get agent status and metadata
- Singleton pattern ensures global access

### CommunicationChannel (Singleton)
Inter-agent messaging system:
- Direct messaging (send to specific agent)
- Broadcasting (send to all agents)
- Request/response pattern
- Publish/subscribe pattern
- Message history and replay

### TaskQueue (Per-Agent)
Task management for agents:
- Priority-based task queuing
- Task status tracking (pending, running, completed, failed)
- Retry logic with configurable policies
- Task metadata and results

### LLM Providers
Built-in support for:
- **Claude** (Anthropic)
- **GPT-4** (OpenAI)
- **GLM-5** (Zhipu AI)
- **Custom providers** (extend BaseLLMProvider)

## Configuration Files

### Agent Configuration Template

```json
{
  "agent_id": "query_agent_001",
  "name": "Query Agent",
  "version": "1.0.0",
  "agent_type": "query",
  "capabilities": ["query", "analysis"],
  "llm_provider": {
    "provider": "claude",
    "model": "claude-3-5-sonnet-20241022",
    "api_key": "your-api-key",
    "temperature": 0.7,
    "max_tokens": 4096,
    "timeout": 30
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 1.0,
    "backoff_factor": 2.0
  },
  "max_concurrent_tasks": 5,
  "task_timeout": 300,
  "enable_messaging": true,
  "message_queue_size": 100,
  "log_level": "INFO"
}
```

## Error Handling

The framework provides comprehensive error types:

- `AgentError` - Base exception for all agent errors
- `AgentNotRegisteredError` - Agent not found in registry
- `AgentAlreadyRegisteredError` - Duplicate agent registration
- `AgentInitializationError` - Initialization failure
- `AgentExecutionError` - Processing failure
- `AgentTimeoutError` - Operation timeout
- `AgentCommunicationError` - Communication failure
- `AgentTaskQueueError` - Task queue error
- `AgentConfigError` - Configuration error

## Best Practices

1. **Always inherit from BaseAgent** and implement all abstract methods
2. **Use agent statuses correctly** - update status during lifecycle transitions
3. **Handle errors gracefully** - use try/finally and proper error types
4. **Register agents with registry** for discovery and management
5. **Use message handlers** for different message types
6. **Configure retry logic** appropriately for your use case
7. **Set resource limits** to prevent resource exhaustion
8. **Log appropriately** - use the agent's logger instance
9. **Clean up resources** in shutdown() method
10. **Test with the example agents** before building custom agents

## Testing

Run the example to validate your setup:

```bash
python -m agents.example_framework_usage
```

This will test:
- Agent creation and registration
- Lifecycle management (initialize, process, shutdown)
- Inter-agent communication
- Task queue operations
- Framework status and discovery

## Advanced Usage

### Custom LLM Provider

```python
from agents.llm_providers import BaseLLMProvider, LLMResponse

class MyCustomProvider(BaseLLMProvider):
    """Custom LLM provider implementation."""
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        # Your implementation here
        return LLMResponse(
            content="Generated response",
            model="my-model",
            usage={"total_tokens": 100},
        )
```

### Message Handlers

```python
class SmartAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.register_message_handler("query", self.handle_query)
        self.register_message_handler("status", self.handle_status)
    
    async def handle_query(self, message):
        return await self.process(message.content)
    
    async def handle_status(self, message):
        return await self.health_check()
```

## Support

For issues or questions:
1. Check the examples in `example_framework_usage.py`
2. Review the component documentation in each module
3. Test with the provided example agents
4. Check the logs for detailed error information

## License

Part of AI Data Labs platform. All rights reserved.
