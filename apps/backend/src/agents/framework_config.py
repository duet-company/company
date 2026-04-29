"""
AI Agent Framework Configuration

This module provides configuration templates and setup utilities for the AI agent framework.
It includes:
- Agent framework selection (LangChain/LangGraph/Custom)
- Base configuration presets
- Agent type definitions
- Communication protocol setup
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base import BaseAgent, AgentCapability, AgentStatus
from .config import AgentConfig, AgentType, LLMProviderConfig, RetryConfig
from .registry import AgentRegistry
from .communication import CommunicationChannel


class AgentFramework(Enum):
    """Available agent frameworks."""
    CUSTOM = "custom"  # Custom implementation
    LANGCHAIN = "langchain"  # LangChain framework
    LANGGRAPH = "langgraph"  # LangGraph framework (stateful)
    AUTOGEN = "autogen"  # AutoGen framework


@dataclass
class FrameworkConfig:
    """Configuration for agent framework setup."""
    
    framework: AgentFramework = AgentFramework.CUSTOM
    
    # Base agent settings
    enable_lifecycle_management: bool = True
    enable_communication: bool = True
    enable_task_queue: bool = True
    enable_monitoring: bool = True
    
    # Communication settings
    max_message_queue_size: int = 1000
    message_timeout: float = 30.0
    enable_broadcast: bool = True
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # Monitoring settings
    enable_health_checks: bool = True
    health_check_interval: int = 60  # seconds
    log_level: str = "INFO"
    
    # Resource limits
    max_concurrent_agents: int = 10
    max_tasks_per_agent: int = 5
    task_timeout: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "framework": self.framework.value,
            "enable_lifecycle_management": self.enable_lifecycle_management,
            "enable_communication": self.enable_communication,
            "enable_task_queue": self.enable_task_queue,
            "enable_monitoring": self.enable_monitoring,
            "max_message_queue_size": self.max_message_queue_size,
            "message_timeout": self.message_timeout,
            "enable_broadcast": self.enable_broadcast,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "backoff_factor": self.backoff_factor,
            "enable_health_checks": self.enable_health_checks,
            "health_check_interval": self.health_check_interval,
            "log_level": self.log_level,
            "max_concurrent_agents": self.max_concurrent_agents,
            "max_tasks_per_agent": self.max_tasks_per_agent,
            "task_timeout": self.task_timeout,
        }


class AgentFrameworkManager:
    """
    Manages AI agent framework setup and configuration.
    
    Provides methods to:
    - Initialize agent framework
    - Register agents
    - Configure communication
    - Setup monitoring
    """
    
    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize framework manager.
        
        Args:
            config: Framework configuration (uses default if not provided)
        """
        self.config = config or FrameworkConfig()
        self.registry = AgentRegistry.get_instance()
        self.communication = CommunicationChannel.get_instance()
        self._initialized = False
        self._agents: Dict[str, BaseAgent] = {}
    
    def initialize_framework(self) -> Dict[str, Any]:
        """
        Initialize the agent framework with configured settings.
        
        Returns:
            Dictionary with initialization status and details
        """
        if self._initialized:
            return {
                "status": "already_initialized",
                "framework": self.config.framework.value,
                "agents_registered": len(self._agents),
            }
        
        # Setup framework based on configuration
        setup_details = {
            "framework": self.config.framework.value,
            "components_initialized": [],
            "agents": [],
        }
        
        # Initialize communication
        if self.config.enable_communication:
            setup_details["components_initialized"].append("communication")
        
        # Initialize registry
        if self.config.enable_lifecycle_management:
            setup_details["components_initialized"].append("lifecycle_management")
        
        self._initialized = True
        
        setup_details["status"] = "initialized"
        setup_details["agents"] = self.list_agents()
        
        return setup_details
    
    def register_agent(self, agent: BaseAgent) -> Dict[str, Any]:
        """
        Register an agent with the framework.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            Dictionary with registration status
        """
        if not self._initialized:
            self.initialize_framework()
        
        # Register with registry
        self.registry.register_agent(agent)
        self._agents[agent.config.agent_id] = agent
        
        # Initialize agent if lifecycle management is enabled
        if self.config.enable_lifecycle_management:
            import asyncio
            asyncio.create_task(agent.initialize())
        
        return {
            "status": "registered",
            "agent_id": agent.config.agent_id,
            "name": agent.config.name,
            "capabilities": [cap.value for cap in agent.get_capabilities()],
        }
    
    def create_agent_from_config(self, config_dict: Dict[str, Any]) -> Optional[BaseAgent]:
        """
        Create and register an agent from configuration dictionary.
        
        Args:
            config_dict: Agent configuration
            
        Returns:
            Created agent instance or None if creation failed
        """
        agent_config = AgentConfig.from_dict(config_dict)
        
        # This would need to be extended to support specific agent classes
        # For now, returns a base agent that can be extended
        # In practice, you'd want to register agent classes and instantiate them
        
        return None
    
    def setup_communication_protocol(self) -> Dict[str, Any]:
        """Setup communication protocol between agents."""
        return {
            "status": "configured",
            "protocol": "direct_messaging",
            "timeout": self.config.message_timeout,
            "broadcast_enabled": self.config.enable_broadcast,
            "queue_size": self.config.max_message_queue_size,
        }
    
    def get_framework_status(self) -> Dict[str, Any]:
        """
        Get current framework status.
        
        Returns:
            Dictionary with framework status information
        """
        return {
            "initialized": self._initialized,
            "framework": self.config.framework.value,
            "agents_registered": len(self._agents),
            "agents_ready": len([a for a in self._agents.values() 
                                 if a.status == AgentStatus.READY]),
            "configuration": self.config.to_dict(),
            "registry_stats": {
                "total_agents": self.registry.get_count(),
                "ready_agents": len(self.registry.discover_ready_agents()),
                "capabilities": self.registry.get_capabilities_summary(),
            },
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent information
        """
        return self.registry.list_all_agents()
    
    def discover_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """
        Discover agents by capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        return self.registry.discover_by_capability(capability)
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent instance or None if not found
        """
        return self.registry.get_agent(agent_id)
    
    def create_agent_config_template(self, agent_type: AgentType, 
                                     capabilities: List[AgentCapability],
                                     name: str) -> Dict[str, Any]:
        """
        Create agent configuration template.
        
        Args:
            agent_type: Type of agent
            capabilities: List of capabilities
            name: Agent name
            
        Returns:
            Configuration dictionary template
        """
        return {
            "agent_id": f"{agent_type.value}_{name.lower().replace(' ', '_')}",
            "name": name,
            "version": "1.0.0",
            "agent_type": agent_type.value,
            "capabilities": [cap.value for cap in capabilities],
            "llm_provider": {
                "provider": os.getenv("DEFAULT_LLM_PROVIDER", "claude"),
                "model": os.getenv("DEFAULT_LLM_MODEL", "claude-3-5-sonnet-20241022"),
                "temperature": 0.7,
                "max_tokens": 4096,
                "timeout": 30,
            },
            "retry_config": {
                "max_retries": self.config.max_retries,
                "retry_delay": self.config.retry_delay,
                "backoff_factor": self.config.backoff_factor,
            },
            "max_concurrent_tasks": self.config.max_tasks_per_agent,
            "task_timeout": self.config.task_timeout,
            "enable_messaging": self.config.enable_communication,
            "message_queue_size": self.config.max_message_queue_size,
            "log_level": self.config.log_level,
            "custom_config": {},
        }


def setup_agent_framework(framework: str = "custom",
                         config: Optional[FrameworkConfig] = None) -> AgentFrameworkManager:
    """
    Convenience function to setup agent framework.
    
    Args:
        framework: Framework type (custom, langchain, langgraph, autogen)
        config: Optional framework configuration
        
    Returns:
        Initialized framework manager
    """
    framework_enum = AgentFramework(framework)
    
    if config is None:
        config = FrameworkConfig(framework=framework_enum)
    else:
        config.framework = framework_enum
    
    manager = AgentFrameworkManager(config)
    manager.initialize_framework()
    
    return manager


def get_default_config() -> Dict[str, Any]:
    """
    Get default framework configuration.
    
    Returns:
        Default configuration dictionary
    """
    return FrameworkConfig().to_dict()
