"""
LLM provider integration for AI agents.

Provides unified interface to Claude, GPT-4, and GLM-5 providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
from enum import Enum
import logging
import os
import aiohttp
import json

from .config import LLMProviderConfig
from .errors import AgentExecutionError


class LLMProviderType(Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GLM5 = "glm5"
    LOCAL = "local"


class LLMMessageRole(Enum):
    """Message roles in LLM conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage:
    """Message structure for LLM conversations."""

    def __init__(
        self,
        role: LLMMessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.role = role
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "role": self.role.value,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMMessage":
        """Create LLMMessage from dictionary."""
        role = LLMMessageRole(data["role"])
        return cls(role=role, content=data["content"])


class LLMResponse:
    """Response from LLM provider."""

    def __init__(
        self,
        content: str,
        model: str,
        provider: str,
        tokens_used: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_used = tokens_used or {}
        self.finish_reason = finish_reason
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
        }


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM provider implementations must inherit from this class.
    """

    def __init__(self, config: LLMProviderConfig):
        """
        Initialize the LLM provider.

        Args:
            config: LLM provider configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"llm.{config.provider}")
        self._session: Optional[aiohttp.ClientSession] = None

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the LLM provider connection.

        Should set up API sessions, validate credentials, etc.

        Raises:
            AgentExecutionError: If initialization fails
        """
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content and metadata

        Raises:
            AgentExecutionError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated text

        Raises:
            AgentExecutionError: If generation fails
        """
        pass

    async def shutdown(self) -> None:
        """
        Shutdown the LLM provider connection.

        Should clean up sessions, close connections, etc.
        """
        if self._session:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create HTTP session.

        Returns:
            aiohttp.ClientSession instance
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude API provider.

    Supports Claude 3.5 Sonnet, Claude 3 Opus, etc.
    """

    BASE_URL = "https://api.anthropic.com/v1/messages"

    async def initialize(self) -> None:
        """Initialize Claude API connection."""
        if not self.config.api_key:
            raise AgentExecutionError(
                "Claude API key is required. Set ANTHROPIC_API_KEY environment variable "
                "or provide in config."
            )

        self.logger.info(f"Claude provider initialized with model: {self.config.model}")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response using Claude API.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (top_p, top_k, stop_sequences, etc.)

        Returns:
            LLMResponse with generated content
        """
        session = await self._get_session()

        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Build request payload
        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages if msg.role != LLMMessageRole.SYSTEM],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }

        # Add system message if present
        system_messages = [msg for msg in messages if msg.role == LLMMessageRole.SYSTEM]
        if system_messages:
            payload["system"] = system_messages[0].content

        # Add additional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        if "stop_sequences" in kwargs:
            payload["stop_sequences"] = kwargs["stop_sequences"]

        try:
            async with session.post(self.BASE_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"Claude API error: {response.status} - {error_text}"
                    )

                data = await response.json()

                return LLMResponse(
                    content=data["content"][0]["text"],
                    model=data["model"],
                    provider="claude",
                    tokens_used={
                        "input_tokens": data["usage"]["input_tokens"],
                        "output_tokens": data["usage"]["output_tokens"],
                    },
                    finish_reason=data["stop_reason"],
                    metadata={"id": data["id"], "type": data["type"]},
                )

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"Claude API request failed: {e}")

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using Claude API.

        Yields chunks of generated text as they arrive.
        """
        session = await self._get_session()

        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages if msg.role != LLMMessageRole.SYSTEM],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "stream": True,
        }

        system_messages = [msg for msg in messages if msg.role == LLMMessageRole.SYSTEM]
        if system_messages:
            payload["system"] = system_messages[0].content

        try:
            async with session.post(
                self.BASE_URL, headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"Claude API error: {response.status} - {error_text}"
                    )

                async for line in response.content:
                    if line:
                        line_text = line.decode("utf-8")
                        if line_text.startswith("data: "):
                            data_str = line_text[6:]
                            if data_str == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if "text" in delta:
                                        yield delta["text"]
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"Claude API streaming failed: {e}")


class GPT4Provider(BaseLLMProvider):
    """
    OpenAI GPT-4 API provider.

    Supports GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, etc.
    """

    BASE_URL = "https://api.openai.com/v1/chat/completions"

    async def initialize(self) -> None:
        """Initialize OpenAI API connection."""
        if not self.config.api_key:
            raise AgentExecutionError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or provide in config."
            )

        self.logger.info(f"OpenAI provider initialized with model: {self.config.model}")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response using OpenAI API.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (top_p, frequency_penalty, presence_penalty, etc.)

        Returns:
            LLMResponse with generated content
        """
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }

        # Add additional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        if "stop" in kwargs:
            payload["stop"] = kwargs["stop"]

        try:
            async with session.post(self.BASE_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"OpenAI API error: {response.status} - {error_text}"
                    )

                data = await response.json()

                choice = data["choices"][0]
                return LLMResponse(
                    content=choice["message"]["content"],
                    model=data["model"],
                    provider="openai",
                    tokens_used={
                        "prompt_tokens": data["usage"]["prompt_tokens"],
                        "completion_tokens": data["usage"]["completion_tokens"],
                        "total_tokens": data["usage"]["total_tokens"],
                    },
                    finish_reason=choice["finish_reason"],
                    metadata={"id": data["id"], "object": data["object"]},
                )

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"OpenAI API request failed: {e}")

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using OpenAI API.

        Yields chunks of generated text as they arrive.
        """
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "stream": True,
        }

        try:
            async with session.post(
                self.BASE_URL, headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"OpenAI API error: {response.status} - {error_text}"
                    )

                async for line in response.content:
                    if line:
                        line_text = line.decode("utf-8")
                        if line_text.startswith("data: "):
                            data_str = line_text[6:]
                            if data_str == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                            except (json.JSONDecodeError, IndexError, KeyError):
                                continue

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"OpenAI API streaming failed: {e}")


class GLM5Provider(BaseLLMProvider):
    """
    Zhipu AI GLM-5 API provider.

    Supports GLM-5 and other Zhipu AI models.
    """

    BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    async def initialize(self) -> None:
        """Initialize Zhipu AI API connection."""
        if not self.config.api_key:
            raise AgentExecutionError(
                "Zhipu AI API key is required. Set ZHIPUAI_API_KEY environment variable "
                "or provide in config."
            )

        self.logger.info(f"GLM-5 provider initialized with model: {self.config.model}")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response using Zhipu AI API.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (top_p, etc.)

        Returns:
            LLMResponse with generated content
        """
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }

        # Add additional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]

        try:
            async with session.post(self.BASE_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"Zhipu AI API error: {response.status} - {error_text}"
                    )

                data = await response.json()

                choice = data["choices"][0]
                return LLMResponse(
                    content=choice["message"]["content"],
                    model=data["model"],
                    provider="glm5",
                    tokens_used={
                        "prompt_tokens": data["usage"]["prompt_tokens"],
                        "completion_tokens": data["usage"]["completion_tokens"],
                        "total_tokens": data["usage"]["total_tokens"],
                    },
                    finish_reason=choice["finish_reason"],
                    metadata={"id": data["id"], "object": data["object"]},
                )

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"Zhipu AI API request failed: {e}")

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using Zhipu AI API.

        Yields chunks of generated text as they arrive.
        """
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "stream": True,
        }

        try:
            async with session.post(
                self.BASE_URL, headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise AgentExecutionError(
                        f"Zhipu AI API error: {response.status} - {error_text}"
                    )

                async for line in response.content:
                    if line:
                        line_text = line.decode("utf-8")
                        if line_text.startswith("data: "):
                            data_str = line_text[6:]
                            if data_str == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                            except (json.JSONDecodeError, IndexError, KeyError):
                                continue

        except aiohttp.ClientError as e:
            raise AgentExecutionError(f"Zhipu AI API streaming failed: {e}")


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.
    """

    _providers = {
        "claude": ClaudeProvider,
        "gpt4": GPT4Provider,
        "glm5": GLM5Provider,
    }

    @classmethod
    def create(cls, config: LLMProviderConfig) -> BaseLLMProvider:
        """
        Create LLM provider instance from configuration.

        Args:
            config: LLM provider configuration

        Returns:
            BaseLLMProvider instance

        Raises:
            AgentExecutionError: If provider type is not supported
        """
        provider_class = cls._providers.get(config.provider)

        if not provider_class:
            raise AgentExecutionError(
                f"Unsupported LLM provider: {config.provider}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )

        return provider_class(config)

    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a custom LLM provider.

        Args:
            name: Provider name
            provider_class: Provider class (must inherit from BaseLLMProvider)
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError("Provider class must inherit from BaseLLMProvider")

        cls._providers[name] = provider_class

    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all available provider names.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())


# Convenience function for quick provider creation
def create_llm_provider(
    provider: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 30,
) -> BaseLLMProvider:
    """
    Quick helper to create an LLM provider.

    Args:
        provider: Provider name (claude, gpt4, glm5)
        model: Model name (default based on provider)
        api_key: API key (from environment if not provided)
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        timeout: Request timeout in seconds

    Returns:
        BaseLLMProvider instance

    Raises:
        AgentExecutionError: If provider creation fails
    """
    # Set default models based on provider
    default_models = {
        "claude": "claude-3-5-sonnet-20241022",
        "gpt4": "gpt-4-turbo-preview",
        "glm5": "glm-4",
    }

    # Set default API keys from environment
    default_api_keys = {
        "claude": os.getenv("ANTHROPIC_API_KEY"),
        "gpt4": os.getenv("OPENAI_API_KEY"),
        "glm5": os.getenv("ZHIPUAI_API_KEY"),
    }

    config = LLMProviderConfig(
        provider=provider,
        model=model or default_models.get(provider),
        api_key=api_key or default_api_keys.get(provider),
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )

    return LLMProviderFactory.create(config)
