"""
Agent lifecycle management.

Handles agent initialization, health monitoring, and graceful shutdown.
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime

from .base import BaseAgent, AgentStatus
from .errors import AgentInitializationError


class AgentLifecycleManager:
    """
    Manages the lifecycle of multiple agents.

    Provides:
    - Coordinated initialization
    - Health monitoring
    - Graceful shutdown
    - Status tracking
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent.lifecycle")
        self._health_check_interval = 30  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the lifecycle manager.

        Args:
            agent: Agent instance to register
        """
        agent_id = agent.config.agent_id
        if agent_id in self.agents:
            raise AgentInitializationError(
                f"Agent {agent_id} is already registered"
            )

        self.agents[agent_id] = agent
        self.logger.info(f"Registered agent: {agent_id}")

    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all registered agents.

        Returns:
            Dictionary mapping agent_id to initialization status
        """
        results = {}

        # Initialize agents sequentially to avoid resource contention
        for agent_id, agent in self.agents.items():
            try:
                self.logger.info(f"Initializing agent: {agent_id}")
                await agent.initialize()
                results[agent_id] = True
                self.logger.info(f"Agent {agent_id} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_id}: {e}")
                results[agent_id] = False

        return results

    async def shutdown_all(self) -> Dict[str, bool]:
        """
        Shutdown all registered agents gracefully.

        Returns:
            Dictionary mapping agent_id to shutdown status
        """
        results = {}

        # Stop health check if running
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

        # Shutdown agents
        for agent_id, agent in self.agents.items():
            try:
                self.logger.info(f"Shutting down agent: {agent_id}")
                await agent.shutdown()
                results[agent_id] = True
                self.logger.info(f"Agent {agent_id} shutdown successfully")
            except Exception as e:
                self.logger.error(f"Failed to shutdown agent {agent_id}: {e}")
                results[agent_id] = False

        return results

    async def start_health_monitoring(self) -> None:
        """Start periodic health checks for all agents."""
        self.logger.info("Starting agent health monitoring")

        async def health_check_loop():
            while not self._shutdown_event.is_set():
                await self._perform_health_checks()
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self._health_check_interval,
                    )
                except asyncio.TimeoutError:
                    continue

        self._health_check_task = asyncio.create_task(health_check_loop())

    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        self.logger.info("Stopping agent health monitoring")
        self._shutdown_event.set()

    async def _perform_health_checks(self) -> Dict[str, Dict]:
        """
        Perform health checks on all agents.

        Returns:
            Health status for all agents
        """
        health_status = {}

        for agent_id, agent in self.agents.items():
            try:
                health = await agent.health_check()
                health_status[agent_id] = health

                # Log warnings for unhealthy agents
                if health.get("status") != "ready":
                    self.logger.warning(
                        f"Agent {agent_id} is not ready: {health.get('status')}"
                    )
            except Exception as e:
                self.logger.error(f"Health check failed for agent {agent_id}: {e}")
                health_status[agent_id] = {"error": str(e)}

        return health_status

    async def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """
        Get status of a specific agent.

        Args:
            agent_id: Agent ID to query

        Returns:
            Agent status or None if not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        try:
            return await agent.health_check()
        except Exception as e:
            return {"error": str(e)}

    async def get_all_status(self) -> Dict[str, Dict]:
        """
        Get status of all agents.

        Returns:
            Dictionary mapping agent_id to status
        """
        status = {}

        for agent_id, agent in self.agents.items():
            try:
                status[agent_id] = await agent.health_check()
            except Exception as e:
                status[agent_id] = {"error": str(e)}

        return status

    def get_ready_agents(self) -> List[BaseAgent]:
        """
        Get list of agents that are ready to process tasks.

        Returns:
            List of ready agents
        """
        return [
            agent
            for agent in self.agents.values()
            if agent.status == AgentStatus.READY
        ]

    async def restart_agent(self, agent_id: str) -> bool:
        """
        Restart a specific agent.

        Args:
            agent_id: Agent ID to restart

        Returns:
            True if successful, False otherwise
        """
        agent = self.agents.get(agent_id)
        if not agent:
            self.logger.error(f"Cannot restart: agent {agent_id} not found")
            return False

        try:
            self.logger.info(f"Restarting agent: {agent_id}")

            # Shutdown
            await agent.shutdown()

            # Reinitialize
            await agent.initialize()

            self.logger.info(f"Agent {agent_id} restarted successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to restart agent {agent_id}: {e}")
            return False

    async def wait_for_ready(
        self, agent_id: str, timeout: float = 60.0
    ) -> bool:
        """
        Wait for an agent to become ready.

        Args:
            agent_id: Agent ID to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            True if agent became ready, False if timeout
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            if agent.status == AgentStatus.READY:
                return True

            await asyncio.sleep(1)

        return False

    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self.agents)
