"""
AI Agent Framework for AI Data Labs.

This package provides a comprehensive framework for building and managing
AI agents with support for:
- Agent lifecycle management
- Inter-agent communication
- Task queuing and execution
- Retry logic and error handling
- Agent registration and discovery
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

# LLM Providers
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

# Specific agents
from .platform_designer import PlatformDesignerAgent, get_platform_config

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
    # LLM Providers
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
    # Agents
    "PlatformDesignerAgent",
    "get_platform_config",
]

__version__ = "1.0.0"
