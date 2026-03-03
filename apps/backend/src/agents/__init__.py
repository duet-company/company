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
