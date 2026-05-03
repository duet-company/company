"""
Extended pytest configuration with additional markers and fixtures.
"""

import pytest
import os
import sys
from unittest.mock import Mock, AsyncMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))


# Custom markers
pytest_plugins = ["pytest_asyncio"]


@pytest.mark.unit
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that can run independently"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring external services"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests testing full workflows"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load testing"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "agent: Agent-specific tests"
    )


@pytest.fixture(scope="session")
def mock_database():
    """Mock database connection."""
    mock_db = Mock()
    mock_db.connect = AsyncMock()
    mock_db.disconnect = AsyncMock()
    return mock_db


@pytest.fixture(scope="session")
def mock_redis():
    """Mock Redis client for caching."""
    mock_redis = Mock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    return mock_redis


@pytest.fixture
def mock_llm_providers():
    """Mock LLM providers for testing."""
    return {
        "openai": Mock(),
        "anthropic": Mock(),
        "google": Mock()
    }


@pytest.fixture
def mock_user():
    """Mock user for authentication tests."""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User",
        "is_active": True,
        "created_at": "2026-05-03T01:00:00Z"
    }


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"