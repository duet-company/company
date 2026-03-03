"""
Base agent class and interface for all AI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging

from .config import AgentConfig


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


class AgentMessage:
    """Message structure for agent communication."""

    def __init__(
        self,
        sender: str,
        content: Any,
        message_type: str = "request",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        self.message_id = f"{sender}_{self.timestamp.timestamp()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    All agents must inherit from this class and implement the required methods.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.status = AgentStatus.UNINITIALIZED
        self.logger = logging.getLogger(f"agent.{config.name}")
        self._message_handlers: Dict[str, callable] = {}

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the agent.

        This method should:
        - Set up connections to LLM providers
        - Load models and resources
        - Validate configuration
        - Set status to READY

        Raises:
            AgentInitializationError: If initialization fails
        """
        pass

    @abstractmethod
    async def process(
        self,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Process input data and return output.

        This is the main method for agent execution.

        Args:
            input_data: Input data to process
            metadata: Optional metadata about the request

        Returns:
            Processed output

        Raises:
            AgentExecutionError: If processing fails
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Shutdown the agent gracefully.

        This method should:
        - Clean up resources
        - Close connections
        - Set status to SHUTDOWN

        Raises:
            AgentExecutionError: If shutdown fails
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent health.

        Returns:
            Health status information
        """
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "status": self.status.value,
            "version": self.config.version,
            "capabilities": [cap.value for cap in self.get_capabilities()],
        }

    def get_capabilities(self) -> List[AgentCapability]:
        """
        Get list of agent capabilities.

        Returns:
            List of agent capabilities
        """
        return self.config.capabilities

    async def send_message(
        self,
        recipient: str,
        content: Any,
        message_type: str = "request",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a message to another agent.

        Args:
            recipient: Agent ID of the recipient
            content: Message content
            message_type: Type of message (request, response, notification)
            metadata: Optional metadata

        Returns:
            Response from the recipient

        Raises:
            AgentCommunicationError: If communication fails
        """
        # This will be implemented using the communication channel
        message = AgentMessage(
            sender=self.config.agent_id,
            content=content,
            message_type=message_type,
            metadata=metadata,
        )

        # Import here to avoid circular dependency
        from .communication import CommunicationChannel

        channel = CommunicationChannel.get_instance()
        return await channel.send(recipient, message)

    async def receive_message(self, message: AgentMessage) -> Any:
        """
        Receive and process a message from another agent.

        Args:
            message: Incoming message

        Returns:
            Response to the message
        """
        handler = self._message_handlers.get(message.message_type)

        if handler:
            return await handler(message)

        # Default handler
        return await self.default_message_handler(message)

    async def default_message_handler(self, message: AgentMessage) -> Any:
        """
        Default message handler when no specific handler is registered.

        Args:
            message: Incoming message

        Returns:
            Default response
        """
        self.logger.warning(
            f"No handler for message type: {message.message_type}. "
            "Using default handler."
        )
        return {
            "status": "received",
            "message_id": message.message_id,
            "note": "No specific handler registered",
        }

    def register_message_handler(
        self, message_type: str, handler: callable
    ) -> None:
        """
        Register a handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self._message_handlers[message_type] = handler

    def set_status(self, status: AgentStatus) -> None:
        """
        Update agent status.

        Args:
            status: New status
        """
        self.status = status
        self.logger.debug(f"Agent status changed to: {status.value}")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.config.agent_id}, "
            f"name={self.config.name}, "
            f"status={self.status.value}"
            f")"
        )
