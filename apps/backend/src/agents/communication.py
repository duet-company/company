"""
Agent communication channel.

Provides message passing between agents with support for:
- Direct messaging
- Broadcasting
- Request/response patterns
- Message queuing
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from collections import deque
from datetime import datetime

from .base import AgentMessage
from .errors import AgentCommunicationError, AgentNotRegisteredError
from .registry import AgentRegistry


class CommunicationChannel:
    """
    Communication channel for inter-agent messaging.

    Implements an in-memory message bus with support for:
    - Direct messaging between agents
    - Broadcasting to multiple agents
    - Request-response pattern
    - Message history and replay
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern for global communication channel."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the communication channel."""
        if self._initialized:
            return

        self.message_queue: deque = deque(maxlen=1000)
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger("agent.communication")
        self._initialized = True

    @staticmethod
    def get_instance() -> "CommunicationChannel":
        """
        Get the singleton instance.

        Returns:
            CommunicationChannel instance
        """
        return CommunicationChannel()

    async def send(
        self,
        recipient: str,
        message: AgentMessage,
        timeout: float = 30.0,
    ) -> Any:
        """
        Send a message to a specific agent.

        Args:
            recipient: Agent ID of the recipient
            message: Message to send
            timeout: Timeout for response in seconds

        Returns:
            Response from the recipient

        Raises:
            AgentCommunicationError: If communication fails
        """
        registry = AgentRegistry.get_instance()
        agent = registry.get_agent(recipient)

        if not agent:
            raise AgentCommunicationError(
                f"Recipient agent {recipient} not found"
            )

        try:
            self.logger.debug(
                f"Sending message from {message.sender} to {recipient}"
            )

            # Store message in history
            self.message_queue.append({
                "timestamp": datetime.utcnow(),
                "from": message.sender,
                "to": recipient,
                "message": message.to_dict(),
            })

            # Process message
            response = await agent.receive_message(message)

            self.logger.debug(
                f"Received response from {recipient}: "
                f"{response if not isinstance(response, dict) else 'dict'}"
            )

            return response

        except asyncio.TimeoutError:
            raise AgentCommunicationError(
                f"Timeout while communicating with agent {recipient}"
            )
        except Exception as e:
            self.logger.error(f"Communication error: {e}")
            raise AgentCommunicationError(f"Failed to send message: {str(e)}")

    async def broadcast(
        self,
        sender: str,
        content: Any,
        message_type: str = "notification",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Broadcast a message to all agents.

        Args:
            sender: Sender agent ID
            content: Message content
            message_type: Type of message
            metadata: Optional metadata

        Returns:
            Dictionary mapping agent IDs to responses
        """
        registry = AgentRegistry.get_instance()
        results = {}

        for agent in registry.agents.values():
            if agent.config.agent_id == sender:
                continue  # Skip sender

            try:
                message = AgentMessage(
                    sender=sender,
                    content=content,
                    message_type=message_type,
                    metadata=metadata,
                )

                response = await agent.receive_message(message)
                results[agent.config.agent_id] = response

            except Exception as e:
                self.logger.error(
                    f"Failed to send to {agent.config.agent_id}: {e}"
                )
                results[agent.config.agent_id] = {"error": str(e)}

        return results

    async def send_request(
        self,
        recipient: str,
        sender: str,
        content: Any,
        timeout: float = 30.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a request and wait for response.

        Args:
            recipient: Recipient agent ID
            sender: Sender agent ID
            content: Request content
            timeout: Timeout for response
            metadata: Optional metadata

        Returns:
            Response from the recipient
        """
        message = AgentMessage(
            sender=sender,
            content=content,
            message_type="request",
            metadata=metadata,
        )

        return await self.send(recipient, message, timeout)

    async def send_response(
        self,
        recipient: str,
        sender: str,
        content: Any,
        original_message_id: str,
    ) -> Any:
        """
        Send a response to a previous request.

        Args:
            recipient: Recipient agent ID
            sender: Sender agent ID
            content: Response content
            original_message_id: ID of the original request

        Returns:
            Confirmation
        """
        message = AgentMessage(
            sender=sender,
            content=content,
            message_type="response",
            metadata={"original_message_id": original_message_id},
        )

        return await self.send(recipient, message)

    def subscribe(
        self,
        message_type: str,
        handler: Callable[[AgentMessage], Any],
    ) -> None:
        """
        Subscribe to a specific message type.

        Args:
            message_type: Type of message to subscribe to
            handler: Function to handle messages
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)
        self.logger.debug(f"Subscribed to message type: {message_type}")

    def unsubscribe(
        self,
        message_type: str,
        handler: Callable[[AgentMessage], Any],
    ) -> None:
        """
        Unsubscribe from a message type.

        Args:
            message_type: Type of message to unsubscribe from
            handler: Handler function to remove
        """
        if message_type in self.message_handlers:
            if handler in self.message_handlers[message_type]:
                self.message_handlers[message_type].remove(handler)

    async def publish(
        self,
        sender: str,
        content: Any,
        message_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Publish a message to all subscribers of a message type.

        Args:
            sender: Sender agent ID
            content: Message content
            message_type: Type of message
            metadata: Optional metadata

        Returns:
            List of responses from handlers
        """
        message = AgentMessage(
            sender=sender,
            content=content,
            message_type=message_type,
            metadata=metadata,
        )

        handlers = self.message_handlers.get(message_type, [])
        responses = []

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    response = await handler(message)
                else:
                    response = handler(message)

                responses.append(response)

            except Exception as e:
                self.logger.error(f"Handler error for {message_type}: {e}")
                responses.append({"error": str(e)})

        return responses

    def get_message_history(
        self,
        limit: int = 100,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get message history.

        Args:
            limit: Maximum number of messages to return
            sender: Filter by sender (optional)
            recipient: Filter by recipient (optional)

        Returns:
            List of messages
        """
        messages = list(self.message_queue)

        if sender:
            messages = [m for m in messages if m["from"] == sender]

        if recipient:
            messages = [m for m in messages if m["to"] == recipient]

        return messages[-limit:]

    def clear_history(self) -> None:
        """Clear message history."""
        self.message_queue.clear()
        self.logger.debug("Message history cleared")
