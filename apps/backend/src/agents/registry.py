"""
Agent registration and discovery mechanism.

Provides a centralized registry for managing and discovering agents.
"""

from typing import Dict, List, Optional, Type
import logging

from .base import BaseAgent, AgentCapability
from .config import AgentType
from .errors import AgentNotRegisteredError, AgentAlreadyRegisteredError


class AgentRegistry:
    """
    Central registry for all agents.

    Provides:
    - Agent registration and lookup
    - Discovery by capability
    - Discovery by type
    - Metadata management
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return

        self.agents: Dict[str, BaseAgent] = {}
        self.agent_classes: Dict[str, Type[BaseAgent]] = {}
        self.logger = logging.getLogger("agent.registry")
        self._initialized = True

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.

        Args:
            agent: Agent instance to register

        Raises:
            AgentAlreadyRegisteredError: If agent ID already exists
        """
        agent_id = agent.config.agent_id

        if agent_id in self.agents:
            raise AgentAlreadyRegisteredError(
                f"Agent with ID {agent_id} is already registered"
            )

        self.agents[agent_id] = agent
        self.logger.info(f"Registered agent: {agent_id} ({agent.config.name})")

    def register_agent_class(
        self, agent_id: str, agent_class: Type[BaseAgent]
    ) -> None:
        """
        Register an agent class for later instantiation.

        Args:
            agent_id: Agent ID for this class
            agent_class: Agent class to register
        """
        self.agent_classes[agent_id] = agent_class
        self.logger.info(f"Registered agent class: {agent_id} ({agent_class.__name__})")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent.

        Args:
            agent_id: Agent ID to unregister

        Raises:
            AgentNotRegisteredError: If agent not found
        """
        if agent_id not in self.agents:
            raise AgentNotRegisteredError(
                f"Agent {agent_id} is not registered"
            )

        del self.agents[agent_id]
        self.logger.info(f"Unregistered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.

        Args:
            agent_id: Agent ID to retrieve

        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)

    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.

        Args:
            name: Agent name to retrieve

        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents.values():
            if agent.config.name == name:
                return agent
        return None

    def discover_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """
        Discover agents with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with the capability
        """
        return [
            agent
            for agent in self.agents.values()
            if capability in agent.get_capabilities()
        ]

    def discover_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        Discover agents of a specific type.

        Args:
            agent_type: Agent type to search for

        Returns:
            List of agents of the type
        """
        return [
            agent
            for agent in self.agents.values()
            if agent.config.agent_type == agent_type
        ]

    def discover_ready_agents(self) -> List[BaseAgent]:
        """
        Discover all ready agents.

        Returns:
            List of ready agents
        """
        from .base import AgentStatus

        return [
            agent
            for agent in self.agents.values()
            if agent.status == AgentStatus.READY
        ]

    def list_all_agents(self) -> List[Dict[str, str]]:
        """
        List all registered agents.

        Returns:
            List of agent metadata
        """
        return [
            {
                "agent_id": agent.config.agent_id,
                "name": agent.config.name,
                "type": agent.config.agent_type.value,
                "version": agent.config.version,
                "status": agent.status.value,
            }
            for agent in self.agents.values()
        ]

    def get_capabilities_summary(self) -> Dict[str, List[str]]:
        """
        Get summary of all capabilities across all agents.

        Returns:
            Dictionary mapping capability to list of agent IDs
        """
        summary: Dict[AgentCapability, List[str]] = {}

        for agent in self.agents.values():
            for capability in agent.get_capabilities():
                if capability not in summary:
                    summary[capability] = []
                summary[capability].append(agent.config.agent_id)

        # Convert enum keys to strings
        return {
            cap.value: agent_ids
            for cap, agent_ids in summary.items()
        }

    def create_agent(
        self, agent_id: str, config_dict: dict
    ) -> Optional[BaseAgent]:
        """
        Create an agent instance from registered class.

        Args:
            agent_id: Agent ID to create
            config_dict: Configuration for the agent

        Returns:
            Agent instance or None if class not found
        """
        agent_class = self.agent_classes.get(agent_id)
        if not agent_class:
            self.logger.error(f"No agent class registered for: {agent_id}")
            return None

        from .config import AgentConfig

        config = AgentConfig.from_dict(config_dict)
        return agent_class(config)

    def validate_agent_id(self, agent_id: str) -> bool:
        """
        Validate if an agent ID exists.

        Args:
            agent_id: Agent ID to validate

        Returns:
            True if agent exists, False otherwise
        """
        return agent_id in self.agents

    def get_count(self) -> int:
        """Get total number of registered agents."""
        return len(self.agents)

    def clear_all(self) -> None:
        """Clear all registered agents (useful for testing)."""
        self.agents.clear()
        self.agent_classes.clear()
        self.logger.info("Cleared all registered agents")

    @staticmethod
    def get_instance() -> "AgentRegistry":
        """
        Get the singleton instance.

        Returns:
            AgentRegistry instance
        """
        return AgentRegistry()
