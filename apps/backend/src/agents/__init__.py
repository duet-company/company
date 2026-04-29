"""
AI Agent Framework for AI Data Labs.

This package provides a comprehensive framework for building and managing
AI agents with support for:
- Agent lifecycle management
- Inter-agent communication
- Task queuing and execution
- Retry logic and error handling
- Agent registration and discovery

Note: LLM provider imports are lazy to avoid requiring all dependencies at import time.
"""

# Base agent class
from .base import (
    BaseAgent,
    AgentStatus,
    AgentCapability,
    AgentMessage,
)

# Configuration
from .config import (
    AgentConfig,
    AgentType,
    LLMProviderConfig,
    RetryConfig,
)

# Lifecycle management
from .lifecycle import AgentLifecycleManager

# Registry and discovery
from .registry import AgentRegistry

# Communication
from .communication import CommunicationChannel

# Task queue
from .task_queue import TaskQueue, Task, TaskStatus, TaskPriority

# Errors
from .errors import (
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

# Lazy imports for LLM providers and specific agents
def __getattr__(name):
    """Lazy import for modules that require optional dependencies."""
    if name == "LLMProviderType":
        from .enums import LLMProviderType
        return LLMProviderType
    elif name == "LLMMessageRole":
        from .enums import LLMMessageRole
        return LLMMessageRole
    elif name == "LLMMessage":
        from .enums import LLMMessage
        return LLMMessage
    elif name == "LLMResponse":
        from .enums import LLMResponse
        return LLMResponse
    elif name in ["BaseLLMProvider", "ClaudeProvider", "GPT4Provider", "GLM5Provider"]:
        from .llm_providers import (
            BaseLLMProvider,
            ClaudeProvider,
            GPT4Provider,
            GLM5Provider,
        )
        return locals()[name]
    elif name in ["LLMProviderFactory", "create_llm_provider"]:
        from .llm_providers import LLMProviderFactory, create_llm_provider
        return locals()[name]
    elif name in ["PlatformDesignerAgent", "get_platform_config"]:
        from .platform_designer import PlatformDesignerAgent, get_platform_config
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Base agent
    "BaseAgent",
    "AgentStatus",
    "AgentCapability",
    "AgentMessage",
    # Configuration
    "AgentConfig",
    "AgentType",
    "LLMProviderConfig",
    "RetryConfig",
    # Lifecycle
    "AgentLifecycleManager",
    # Registry
    "AgentRegistry",
    # Communication
    "CommunicationChannel",
    # Task queue
    "TaskQueue",
    "Task",
    "TaskStatus",
    "TaskPriority",
    # Errors
    "AgentError",
    "AgentNotRegisteredError",
    "AgentAlreadyRegisteredError",
    "AgentInitializationError",
    "AgentExecutionError",
    "AgentTimeoutError",
    "AgentCommunicationError",
    "AgentTaskQueueError",
    "AgentConfigError",
]

__version__ = "1.0.0"

# Add lazy imports to __all__
__all__.extend([
    "LLMProviderType",
    "LLMMessageRole",
    "LLMMessage",
    "LLMResponse",
    "BaseLLMProvider",
    "ClaudeProvider",
    "GPT4Provider",
    "GLM5Provider",
    "LLMProviderFactory",
    "create_llm_provider",
    "PlatformDesignerAgent",
    "get_platform_config",
])