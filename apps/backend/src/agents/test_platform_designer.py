"""
Unit tests for the Platform Designer Agent.

Tests cover:
- Agent initialization and configuration
- Design processing with various inputs
- LLM provider integration
- Output format handling (JSON/Markdown)
- Error handling
- Health checks
"""

import asyncio
import os
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .platform_designer import PlatformDesignerAgent, get_platform_config
from .config import AgentConfig, AgentType, LLMProviderConfig
from .base import AgentStatus
from .errors import AgentInitializationError, AgentExecutionError, AgentConfigError


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value="# Test Design\n\nThis is a test design.")
    return provider


@pytest.fixture
def platform_config(mock_llm_provider):
    """Create test configuration for Platform Designer Agent."""
    return AgentConfig(
        agent_id="test-platform-designer",
        name="Test Platform Designer",
        version="1.0.0",
        agent_type=AgentType.DESIGN,
        llm_provider=LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-api-key",
            temperature=0.7,
            max_tokens=4096,
        ),
        max_concurrent_tasks=3,
        task_timeout=600,
        log_level="INFO",
    )


class TestPlatformDesignerAgent:
    """Tests for PlatformDesignerAgent class."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, platform_config, mock_llm_provider):
        """Test agent initialization."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)

            assert agent.status == AgentStatus.UNINITIALIZED

            await agent.initialize()

            assert agent.status == AgentStatus.READY
            assert agent.llm_provider is not None

    @pytest.mark.asyncio
    async def test_agent_initialization_without_llm_config(self):
        """Test that initialization fails without LLM provider config."""
        config = AgentConfig(
            agent_id="test-platform-designer",
            name="Test Platform Designer",
            version="1.0.0",
            agent_type=AgentType.DESIGN,
            llm_provider=None,
        )

        agent = PlatformDesignerAgent(config)

        with pytest.raises(AgentInitializationError):
            await agent.initialize()

    @pytest.mark.asyncio
    async def test_process_string_input(self, platform_config, mock_llm_provider):
        """Test processing string input (natural language requirements)."""
        mock_llm_provider.generate.return_value = "# Architecture Overview\n\nTest architecture."

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            result = await agent.process("I need a data platform with ClickHouse.")

            assert "design" in result
            assert result["format"] == "markdown"
            assert "metadata" in result
            assert result["metadata"]["agent_id"] == "test-platform-designer"

    @pytest.mark.asyncio
    async def test_process_dict_input(self, platform_config, mock_llm_provider):
        """Test processing dict input with constraints."""
        mock_llm_provider.generate.return_value = "# Architecture Overview\n\nTest architecture."

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            input_data = {
                "requirements": "I need a data platform with ClickHouse.",
                "constraints": "Budget < $100/month",
                "format": "markdown",
            }

            result = await agent.process(input_data)

            assert result["metadata"]["requirements"] == "I need a data platform with ClickHouse."
            assert result["metadata"]["constraints"] == "Budget < $100/month"
            assert result["metadata"]["output_format"] == "markdown"

    @pytest.mark.asyncio
    async def test_process_json_format(self, platform_config, mock_llm_provider):
        """Test processing with JSON output format."""
        mock_response = '''{
            "architecture_overview": "Test architecture",
            "components": [
                {
                    "name": "clickhouse",
                    "type": "database"
                }
            ],
            "resource_estimates": {
                "total_cpu": "2 cores",
                "total_memory": "4GB"
            },
            "cost_estimate": {
                "monthly_total": "$50",
                "breakdown": {
                    "vps": "$50"
                }
            }
        }'''

        mock_llm_provider.generate.return_value = mock_response

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            input_data = {
                "requirements": "I need a data platform.",
                "format": "json",
            }

            result = await agent.process(input_data)

            assert result["architecture_overview"] == "Test architecture"
            assert len(result["components"]) == 1
            assert result["cost_estimate"]["monthly_total"] == "$50"

    @pytest.mark.asyncio
    async def test_process_invalid_json_fallback(self, platform_config, mock_llm_provider):
        """Test that invalid JSON falls back to markdown format."""
        mock_llm_provider.generate.return_value = "Invalid JSON: {broken}"

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            input_data = {
                "requirements": "I need a data platform.",
                "format": "json",
            }

            result = await agent.process(input_data)

            assert result["design"] == "Invalid JSON: {broken}"
            assert result["format"] == "raw"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_process_empty_requirements(self, platform_config, mock_llm_provider):
        """Test that processing fails with empty requirements."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            with pytest.raises(ValueError):
                await agent.process("")

    @pytest.mark.asyncio
    async def test_process_invalid_input_type(self, platform_config, mock_llm_provider):
        """Test that processing fails with invalid input type."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            with pytest.raises(ValueError):
                await agent.process(123)  # Invalid type

    @pytest.mark.asyncio
    async def test_markdown_section_extraction(self, platform_config, mock_llm_provider):
        """Test extraction of sections from markdown output."""
        mock_llm_provider.generate.return_value = """# Architecture Overview

This is the architecture.

# Component Specifications

Component details here.

# Cost Estimate

$100/month.
"""

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            result = await agent.process("I need a data platform.")

            assert "sections" in result
            assert "Architecture Overview" in result["sections"]
            assert "Component Specifications" in result["sections"]
            assert "Cost Estimate" in result["sections"]

    @pytest.mark.asyncio
    async def test_health_check(self, platform_config, mock_llm_provider):
        """Test extended health check with LLM provider status."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            health = await agent.health_check()

            assert health["agent_id"] == "test-platform-designer"
            assert health["name"] == "Test Platform Designer"
            assert health["status"] == "ready"
            assert health["llm_provider"] == "claude"
            assert health["model"] == "claude-3-5-sonnet-20241022"

    @pytest.mark.asyncio
    async def test_llm_provider_connection_test(self, platform_config):
        """Test that agent validates LLM provider connection during init."""
        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(return_value="Test connection successful")

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            # Verify connection test was called
            mock_provider.generate.assert_called_once()
            call_args = mock_provider.generate.call_args[0][0]
            assert call_args[0]["role"] == "user"
            assert "Test connection" in call_args[0]["content"]

    @pytest.mark.asyncio
    async def test_build_system_prompt_with_constraints(self, platform_config, mock_llm_provider):
        """Test that system prompt includes user constraints."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            input_data = {
                "requirements": "I need a data platform.",
                "constraints": "Budget < $100/month",
            }

            await agent.process(input_data)

            # Check that generate was called
            mock_llm_provider.generate.assert_called_once()
            call_args = mock_llm_provider.generate.call_args[0][0]

            # Verify constraints in prompt
            system_prompt = call_args[0]["content"]
            assert "Budget < $100/month" in system_prompt

    @pytest.mark.asyncio
    async def test_metadata_includes_timestamp(self, platform_config, mock_llm_provider):
        """Test that metadata includes timestamp."""
        mock_llm_provider.generate.return_value = "# Test Design"

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            result = await agent.process("I need a data platform.")

            assert "timestamp" in result["metadata"]
            assert "Z" in result["metadata"]["timestamp"]  # UTC timezone marker

    @pytest.mark.asyncio
    async def test_llm_provider_failure_during_init(self, platform_config):
        """Test that initialization fails if LLM provider test fails."""
        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(side_effect=Exception("Connection failed"))

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_provider):
            agent = PlatformDesignerAgent(platform_config)

            with pytest.raises(AgentInitializationError):
                await agent.initialize()

    @pytest.mark.asyncio
    async def test_llm_provider_failure_during_process(self, platform_config, mock_llm_provider):
        """Test that processing fails if LLM provider fails."""
        mock_llm_provider.generate = AsyncMock(side_effect=Exception("LLM API error"))

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            with pytest.raises(AgentExecutionError):
                await agent.process("I need a data platform.")

            # Verify agent status is ERROR after failure
            assert agent.status == AgentStatus.ERROR

    @pytest.mark.asyncio
    async def test_shutdown(self, platform_config, mock_llm_provider):
        """Test agent shutdown."""
        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            assert agent.status == AgentStatus.READY

            await agent.shutdown()

            assert agent.status == AgentStatus.SHUTDOWN


class TestGetPlatformConfig:
    """Tests for get_platform_config() function."""

    def test_default_config(self):
        """Test default configuration."""
        config = get_platform_config()

        assert config.agent_id == "platform-designer-001"
        assert config.name == "Platform Designer"
        assert config.version == "1.0.0"
        assert config.agent_type == AgentType.DESIGN
        assert config.max_concurrent_tasks == 3
        assert config.task_timeout == 600

    def test_default_llm_provider(self):
        """Test default LLM provider configuration."""
        config = get_platform_config()

        assert config.llm_provider.provider == "claude"
        assert config.llm_provider.model == "claude-3-5-sonnet-20241022"
        assert config.llm_provider.temperature == 0.7
        assert config.llm_provider.max_tokens == 8192

    def test_environment_variable_override_provider(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {"PLATFORM_DESIGNER_LLM_PROVIDER": "gpt-4"}):
            config = get_platform_config()
            assert config.llm_provider.provider == "gpt-4"

    def test_environment_variable_override_model(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {"PLATFORM_DESIGNER_LLM_MODEL": "gpt-4-turbo"}):
            config = get_platform_config()
            assert config.llm_provider.model == "gpt-4-turbo"

    def test_environment_variable_override_api_key(self):
        """Test that environment variables override defaults."""
        test_key = "test-api-key-123"
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": test_key}):
            config = get_platform_config()
            assert config.llm_provider.api_key == test_key


class TestPlatformDesignerAgentIntegration:
    """Integration tests for Platform Designer Agent."""

    @pytest.mark.asyncio
    async def test_full_design_workflow(self, platform_config, mock_llm_provider):
        """Test complete workflow from init to design to shutdown."""
        mock_llm_provider.generate.return_value = """# Architecture Overview

Complete data platform.

# Components

- ClickHouse Database
- FastAPI Backend
- React Frontend

# Cost Estimate

$50/month
"""

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            # Initialize
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            # Process design request
            input_data = {
                "requirements": "I need a complete data platform with ClickHouse, backend, and frontend.",
                "constraints": "Budget < $100/month",
            }

            result = await agent.process(input_data)

            # Verify result structure
            assert "design" in result
            assert "metadata" in result
            assert result["metadata"]["requirements"] == input_data["requirements"]
            assert "Complete data platform" in result["design"]

            # Health check
            health = await agent.health_check()
            assert health["status"] == "ready"

            # Shutdown
            await agent.shutdown()
            assert agent.status == AgentStatus.SHUTDOWN

    @pytest.mark.asyncio
    async def test_concurrent_design_requests(self, platform_config, mock_llm_provider):
        """Test handling multiple concurrent design requests."""
        mock_llm_provider.generate = AsyncMock(return_value="# Design")

        with patch('agents.platform_designer.create_llm_provider', return_value=mock_llm_provider):
            agent = PlatformDesignerAgent(platform_config)
            await agent.initialize()

            # Create multiple concurrent requests
            tasks = [
                agent.process(f"Design {i}") for i in range(3)
            ]

            results = await asyncio.gather(*tasks)

            # Verify all requests completed
            assert len(results) == 3
            for result in results:
                assert "design" in result

            await agent.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
