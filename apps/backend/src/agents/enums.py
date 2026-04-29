"""
Enumeration definitions for AI Agent Framework.

This module contains the core enums used throughout the framework to avoid circular imports.
"""

from enum import Enum


class AgentStatus(Enum):
    """Agent lifecycle status."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


class AgentCapability(Enum):
    """Standard agent capabilities."""
    QUERY = "query"
    DESIGN = "design"
    SUPPORT = "support"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"


class AgentType(Enum):
    """Types of agents."""
    QUERY = "query"
    DESIGN = "design"
    SUPPORT = "support"
    CUSTOM = "custom"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class LLMProviderType(Enum):
    """LLM provider types."""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GLM5 = "glm5"
    LOCAL = "local"
    CUSTOM = "custom"


class LLMMessageRole(Enum):
    """LLM message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"
    OBSERVATION = "observation"