"""
Custom exceptions for the AI agent framework.
"""


class AgentError(Exception):
    """Base exception for all agent-related errors."""
    pass


class AgentNotRegisteredError(AgentError):
    """Raised when trying to access an agent that is not registered."""
    pass


class AgentAlreadyRegisteredError(AgentError):
    """Raised when trying to register an agent that already exists."""
    pass


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""
    pass


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when agent operation times out."""
    pass


class AgentCommunicationError(AgentError):
    """Raised when agent communication fails."""
    pass


class AgentTaskQueueError(AgentError):
    """Raised when task queue operations fail."""
    pass


class AgentConfigError(AgentError):
    """Raised when agent configuration is invalid."""
    pass
