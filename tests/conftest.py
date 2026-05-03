"""
Pytest configuration and fixtures for Duet Company tests.
"""

import pytest
import os
import sys
from unittest.mock import Mock, AsyncMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))


@pytest.fixture(scope="session")
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_client.chat.completions.create = AsyncMock()
    return mock_client


@pytest.fixture(scope="session") 
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    mock_client.messages.create = AsyncMock()
    return mock_client


@pytest.fixture
def sample_query_data():
    """Sample query data for testing."""
    return {
        "query": "What is artificial intelligence?",
        "type": "general",
        "timestamp": "2026-05-03T01:00:00Z"
    }


@pytest.fixture
def sample_design_data():
    """Sample design data for testing."""
    return {
        "requirements": "Build an e-commerce platform",
        "scope": "full",
        "technologies": ["React", "Node.js", "PostgreSQL"],
        "timestamp": "2026-05-03T01:00:00Z"
    }


@pytest.fixture
def test_database_url():
    """Test database URL."""
    return os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")


@pytest.fixture
def mock_agent_registry():
    """Mock agent registry for testing."""
    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    
    # Add a mock agent
    mock_agent = Mock()
    mock_agent.id = "test-agent"
    mock_agent.name = "Test Agent"
    mock_agent.type = "test"
    mock_agent.status = "running"
    
    registry.register(mock_agent)
    return registry