"""
Agent configuration system.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import json

from .enums import AgentType, AgentCapability
from .errors import AgentConfigError


class AgentType(Enum):
    """Types of agents."""
    QUERY = "query"
    DESIGN = "design"
    SUPPORT = "support"
    CUSTOM = "custom"


@dataclass
class LLMProviderConfig:
    """Configuration for LLM providers."""

    provider: str  # "claude", "gpt4", "glm5", "local"
    model: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": "***" if self.api_key else None,
            "api_url": self.api_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    retry_on_timeout: bool = True
    retry_on_error: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "backoff_factor": self.backoff_factor,
            "retry_on_timeout": self.retry_on_timeout,
            "retry_on_error": self.retry_on_error,
        }


@dataclass
class AgentConfig:
    """
    Main agent configuration.

    This class contains all configuration parameters for an agent.
    """

    # Basic identification
    agent_id: str
    name: str
    version: str = "1.0.0"
    agent_type: AgentType = AgentType.CUSTOM

    # Capabilities
    capabilities: List[AgentCapability] = field(default_factory=list)

    # LLM configuration
    llm_provider: LLMProviderConfig = None

    # Retry configuration
    retry_config: RetryConfig = field(default_factory=RetryConfig)

    # Resource limits
    max_concurrent_tasks: int = 5
    task_timeout: int = 300  # seconds
    memory_limit_mb: int = 512

    # Communication
    enable_messaging: bool = True
    message_queue_size: int = 100

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Custom configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.agent_id:
            raise AgentConfigError("agent_id is required")

        if not self.name:
            raise AgentConfigError("name is required")

        if self.llm_provider is None:
            # Set default LLM provider
            self.llm_provider = LLMProviderConfig(
                provider=os.getenv("DEFAULT_LLM_PROVIDER", "claude"),
                model=os.getenv("DEFAULT_LLM_MODEL", "claude-3-5-sonnet-20241022"),
                api_key=os.getenv("DEFAULT_LLM_API_KEY"),
            )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AgentConfig":
        """
        Create AgentConfig from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            AgentConfig instance
        """
        # Parse LLM provider config
        llm_dict = config_dict.pop("llm_provider", {})
        if llm_dict:
            llm_provider = LLMProviderConfig(**llm_dict)
        else:
            llm_provider = None

        # Parse retry config
        retry_dict = config_dict.pop("retry_config", {})
        retry_config = RetryConfig(**retry_dict) if retry_dict else None

        # Parse capabilities
        capabilities_list = config_dict.pop("capabilities", [])
        capabilities = [
            AgentCapability(cap) if isinstance(cap, str) else cap
            for cap in capabilities_list
        ]

        # Parse agent type
        agent_type_str = config_dict.pop("agent_type", "custom")
        agent_type = AgentType(agent_type_str)

        # Create config
        return cls(
            llm_provider=llm_provider,
            retry_config=retry_config,
            capabilities=capabilities,
            agent_type=agent_type,
            **config_dict,
        )

    @classmethod
    def from_file(cls, config_path: str) -> "AgentConfig":
        """
        Load AgentConfig from JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            AgentConfig instance
        """
        with open(config_path, "r") as f:
            config_dict = json.load(f)

        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "agent_type": self.agent_type.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "llm_provider": self.llm_provider.to_dict() if self.llm_provider else None,
            "retry_config": self.retry_config.to_dict(),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "task_timeout": self.task_timeout,
            "memory_limit_mb": self.memory_limit_mb,
            "enable_messaging": self.enable_messaging,
            "message_queue_size": self.message_queue_size,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "custom_config": self.custom_config,
        }

    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to JSON file.

        Args:
            config_path: Path to save configuration
        """
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def update(self, **kwargs) -> None:
        """
        Update configuration parameters.

        Args:
            **kwargs: Parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.custom_config[key] = value
