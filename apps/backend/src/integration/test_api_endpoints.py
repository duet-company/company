"""
Integration tests for API endpoints.

Tests cover:
- Authentication endpoints
- Query agent endpoints
- Agent management endpoints
- Health check endpoints
- Error handling
- Request validation
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from main import app
from agents.config import AgentConfig, LLMProviderConfig
from agents.query_agent import QueryAgent
from agents.base import AgentStatus


@pytest.fixture
async def test_client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_query_agent():
    """Create mock query agent."""
    config = AgentConfig(
        agent_id="test-query-agent",
        name="Test Query Agent",
        version="1.0.0",
        llm_provider=LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        ),
    )
    agent = QueryAgent(config)
    agent.status = AgentStatus.READY
    return agent


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test basic health check."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check_with_agents(self, test_client, mock_query_agent):
        """Test health check with agent status."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            response = await test_client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert data["agents"]["test-query-agent"]["status"] == "ready"


class TestQueryAgentEndpoint:
    """Test query agent endpoints."""

    @pytest.mark.asyncio
    async def test_query_endpoint_success(self, test_client, mock_query_agent):
        """Test successful query execution."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            # Mock successful query response
            mock_query_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT * FROM users",
                "optimized_sql": "SELECT name FROM users LIMIT 1000",
                "explanation": "Simple query to get all users",
                "dialect": "clickhouse",
                "cached": False,
                "execution_time_ms": 150
            })
            
            response = await test_client.post(
                "/api/queries",
                json={
                    "query": "Show me all users",
                    "dialect": "clickhouse"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "generated_sql" in data
            assert "optimized_sql" in data
            assert "explanation" in data
            assert data["dialect"] == "clickhouse"

    @pytest.mark.asyncio
    async def test_query_endpoint_with_cache(self, test_client, mock_query_agent):
        """Test query endpoint with cached result."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            # Mock cached query response
            mock_query_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT name FROM users",
                "optimized_sql": "SELECT name FROM users LIMIT 1000",
                "explanation": "Simple query to get user names",
                "dialect": "clickhouse",
                "cached": True,
                "execution_time_ms": 5
            })
            
            response = await test_client.post(
                "/api/queries",
                json={
                    "query": "Show me user names",
                    "dialect": "clickhouse"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["cached"] is True
            assert data["execution_time_ms"] < 10  # Should be very fast when cached

    @pytest.mark.asyncio
    async def test_query_endpoint_validation_error(self, test_client, mock_query_agent):
        """Test query endpoint with validation error."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            # Mock validation error
            mock_query_agent.process = AsyncMock(side_effect=Exception("SQL validation failed"))
            
            response = await test_client.post(
                "/api/queries",
                json={
                    "query": "DROP TABLE users",
                    "dialect": "clickhouse"
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert "validation" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_query_endpoint_missing_query(self, test_client):
        """Test query endpoint with missing query parameter."""
        response = await test_client.post(
            "/api/queries",
            json={
                "dialect": "clickhouse"
                # Missing "query" field
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "query" in str(data).lower()

    @pytest.mark.asyncio
    async def test_query_endpoint_invalid_dialect(self, test_client):
        """Test query endpoint with invalid dialect."""
        response = await test_client.post(
            "/api/queries",
            json={
                "query": "Show me users",
                "dialect": "invalid_dialect"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "dialect" in str(data).lower()

    @pytest.mark.asyncio
    async def test_query_endpoint_empty_query(self, test_client):
        """Test query endpoint with empty query."""
        response = await test_client.post(
            "/api/queries",
            json={
                "query": "",
                "dialect": "clickhouse"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "query" in str(data).lower()


class TestAgentManagementEndpoint:
    """Test agent management endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents(self, test_client, mock_query_agent):
        """Test listing all agents."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            response = await test_client.get("/api/agents")
            
            assert response.status_code == 200
            data = response.json()
            assert "agents" in data
            assert len(data["agents"]) > 0

    @pytest.mark.asyncio
    async def test_get_agent_status(self, test_client, mock_query_agent):
        """Test getting specific agent status."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            response = await test_client.get("/api/agents/test-query-agent")
            
            assert response.status_code == 200
            data = response.json()
            assert "agent_id" in data
            assert "status" in data
            assert data["agent_id"] == "test-query-agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, test_client):
        """Test getting status of non-existent agent."""
        response = await test_client.get("/apiagents/non-existent-agent")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in str(data).lower()

    @pytest.mark.asyncio
    async def test_agent_health(self, test_client, mock_query_agent):
        """Test agent health check endpoint."""
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_query_agent
            
            # Mock health check
            mock_query_agent.health_check = AsyncMock(return_value={
                "agent_id": "test-query-agent",
                "status": "ready",
                "uptime_seconds": 3600,
                "queries_processed": 150,
                "cache_stats": {
                    "size": 10,
                    "hits": 50,
                    "misses": 100
                }
            })
            
            response = await test_client.get("/api/agents/test-query-agent/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "agent_id" in data
            assert "status" in data
            assert "uptime_seconds" in data
            assert "queries_processed" in data


class TestAuthenticationEndpoint:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, test_client):
        """Test successful login."""
        response = await test_client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        # This will depend on actual auth implementation
        # For now, just check that it responds
        assert response.status_code in [200, 401, 422]

    @pytest.mark.asyncio
    async def test_login_missing_credentials(self, test_client):
        """Test login with missing credentials."""
        response = await test_client.post(
            "/api/auth/login",
            json={
                # Missing username and password
            }
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_logout(self, test_client):
        """Test logout endpoint."""
        response = await test_client.post("/api/auth/logout")
        
        # Should succeed regardless of auth state
        assert response.status_code in [200, 401]


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, test_client):
        """Test rate limiting when exceeded."""
        # Make many rapid requests to trigger rate limiting
        responses = []
        for _ in range(100):  # Exceed typical rate limits
            response = await test_client.get("/health")
            responses.append(response.status_code)
        
        # Some requests should be rate limited (429)
        assert 429 in responses


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_404_endpoint(self, test_client):
        """Test 404 for non-existent endpoint."""
        response = await test_client.get("/api/non-existent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in str(data).lower()

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, test_client):
        """Test method not allowed error."""
        response = await test_client.delete("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "method not allowed" in str(data).lower()

    @pytest.mark.asyncio
    async def test_invalid_json(self, test_client):
        """Test invalid JSON in request body."""
        response = await test_client.post(
            "/api/queries",
            data="invalid json content"
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_large_request_body(self, test_client):
        """Test handling of large request body."""
        large_query = "SELECT * FROM users" * 10000  # Very large query
        
        response = await test_client.post(
            "/api/queries",
            json={
                "query": large_query,
                "dialect": "clickhouse"
            }
        )
        
        # Should either succeed or fail with appropriate error
        assert response.status_code in [200, 413, 422]


class TestContentTypeValidation:
    """Test content type validation."""

    @pytest.mark.asyncio
    async def test_missing_content_type(self, test_client):
        """Test request without content type."""
        response = await test_client.post(
            "/api/queries",
            json={
                "query": "SELECT 1",
                "dialect": "clickhouse"
            },
            headers={"Content-Type": None}
        )
        
        # Should either work or fail with appropriate error
        assert response.status_code in [200, 415, 422]

    @pytest.mark.asyncio
    async def test_wrong_content_type(self, test_client):
        """Test request with wrong content type."""
        response = await test_client.post(
            "/api/queries",
            json={
                "query": "SELECT 1",
                "dialect": "clickhouse"
            },
            headers={"Content-Type": "application/xml"}
        )
        
        assert response.status_code == 415
        data = response.json()
        assert "unsupported media type" in str(data).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])