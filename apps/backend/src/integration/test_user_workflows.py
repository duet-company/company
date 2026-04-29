"""
End-to-end tests for complete user workflows.

Tests cover:
- User onboarding workflow
- Query execution workflow
- Agent interaction workflow
- Dashboard workflow
- Error recovery workflow
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, Mock
from typing import Dict, Any

from main import app
from agents.config import AgentConfig, LLMProviderConfig
from agents.query_agent import QueryAgent
from agents.base import AgentStatus


@pytest.fixture
async def test_client():
    """Create test client for E2E tests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_database():
    """Mock database connection."""
    return Mock()


@pytest.fixture
def mock_ai_agents():
    """Mock AI agents."""
    query_agent = Mock()
    query_agent.status = AgentStatus.READY
    query_agent.process = AsyncMock(return_value={
        "generated_sql": "SELECT name, SUM(amount) as total FROM orders GROUP BY name",
        "optimized_sql": "SELECT name, SUM(amount) as total FROM orders GROUP BY name LIMIT 1000",
        "explanation": "Query to get sales summary by product",
        "dialect": "clickhouse",
        "cached": False,
        "execution_time_ms": 250
    })
    return {"query": query_agent}


class TestUserOnboardingWorkflow:
    """Test complete user onboarding workflow."""

    @pytest.mark.asyncio
    async def test_complete_onboarding_flow(self, test_client):
        """Test complete user onboarding from signup to first query."""
        # Step 1: User registration
        registration_response = await test_client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "company_name": "Test Company",
                "plan": "pro"
            }
        )
        
        assert registration_response.status_code == 201
        registration_data = registration_response.json()
        user_id = registration_data["user_id"]
        
        # Step 2: Email verification (mock)
        verification_response = await test_client.post(
            "/api/auth/verify-email",
            json={
                "user_id": user_id,
                "token": "mock-verification-token"
            }
        )
        
        assert verification_response.status_code == 200
        
        # Step 3: Setup company profile
        profile_response = await test_client.put(
            f"/api/users/{user_id}/profile",
            json={
                "company_name": "Test Company Inc.",
                "industry": "technology",
                "timezone": "UTC"
            }
        )
        
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["company_name"] == "Test Company Inc."
        
        # Step 4: Create first project
        project_response = await test_client.post(
            f"/api/users/{user_id}/projects",
            json={
                "name": "Sales Analytics",
                "description": "Track sales performance and trends"
            }
        )
        
        assert project_response.status_code == 201
        project_data = project_response.json()
        project_id = project_data["project_id"]
        
        # Step 5: Connect data source
        datasource_response = await test_client.post(
            f"/api/projects/{project_id}/datasources",
            json={
                "name": "Production Database",
                "type": "clickhouse",
                "connection_string": "clickhouse://user:pass@localhost:9000/test",
                "description": "Main production ClickHouse database"
            }
        )
        
        assert datasource_response.status_code == 201
        datasource_data = datasource_response.json()
        datasource_id = datasource_data["datasource_id"]
        
        # Step 6: Setup AI agents
        agents_response = await test_client.post(
            f"/api/projects/{project_id}/agents/setup",
            json={
                "agent_types": ["query", "design", "monitor"],
                "llm_providers": ["claude", "gpt4"]
            }
        )
        
        assert agents_response.status_code == 201
        
        # Step 7: First query (onboarding complete)
        query_response = await test_client.post(
            "/api/queries",
            json={
                "query": "Show me sales by product",
                "project_id": project_id,
                "datasource_id": datasource_id,
                "dialect": "clickhouse"
            }
        )
        
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert "generated_sql" in query_data
        assert "explanation" in query_data
        
        # Verify onboarding completion
        completion_response = await test_client.get(
            f"/api/users/{user_id}/onboarding/status"
        )
        
        assert completion_response.status_code == 200
        completion_data = completion_response.json()
        assert completion_data["onboarding_complete"] is True
        assert completion_data["completed_steps"] >= 6

    @pytest.mark.asyncio
    async def test_onboarding_with_errors(self, test_client):
        """Test onboarding workflow with error handling."""
        # Step 1: Successful registration
        registration_response = await test_client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "company_name": "Test Company"
            }
        )
        
        assert registration_response.status_code == 201
        user_id = registration_response.json()["user_id"]
        
        # Step 2: Invalid verification token
        verification_response = await test_client.post(
            "/api/auth/verify-email",
            json={
                "user_id": user_id,
                "token": "invalid-token"
            }
        )
        
        assert verification_response.status_code == 400
        
        # Step 3: Retry with correct token (mock)
        verification_response = await test_client.post(
            "/api/auth/verify-email",
            json={
                "user_id": user_id,
                "token": "mock-verification-token"
            }
        )
        
        assert verification_response.status_code == 200
        
        # Step 4: Invalid project creation (missing required field)
        project_response = await test_client.post(
            f"/api/users/{user_id}/projects",
            json={
                "description": "Missing name field"
                # Missing "name" field
            }
        )
        
        assert project_response.status_code == 422


class TestQueryExecutionWorkflow:
    """Test complete query execution workflow."""

    @pytest.mark.asyncio
    async def test_query_execution_from_start_to_finish(self, test_client, mock_ai_agents):
        """Test complete query execution workflow."""
        # Setup user and project
        user_id = "test-user"
        project_id = "test-project"
        datasource_id = "test-datasource"
        
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_ai_agents["query"]
            
            # Step 1: User writes natural language query
            query_request = {
                "query": "Show me total sales by product for the last 30 days",
                "project_id": project_id,
                "datasource_id": datasource_id,
                "dialect": "clickhouse"
            }
            
            # Step 2: Submit query
            response = await test_client.post(
                "/api/queries",
                json=query_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Step 3: Verify query processing
            assert "generated_sql" in result
            assert "optimized_sql" in result
            assert "explanation" in result
            assert result["dialect"] == "clickhouse"
            
            # Step 4: Execute the generated SQL
            execute_response = await test_client.post(
                "/api/queries/execute",
                json={
                    "sql": result["optimized_sql"],
                    "datasource_id": datasource_id,
                    "project_id": project_id
                }
            )
            
            assert execute_response.status_code == 200
            execute_data = execute_response.json()
            assert "results" in execute_data
            assert "columns" in execute_data
            assert "row_count" in execute_data
            
            # Step 5: Save query as template
            template_response = await test_client.post(
                f"/api/projects/{project_id}/templates",
                json={
                    "name": "Sales by Product (30 days)",
                    "query": result["generated_sql"],
                    "description": "Get total sales by product for last 30 days",
                    "tags": ["sales", "products", "revenue"]
                }
            )
            
            assert template_response.status_code == 201
            template_data = template_response.json()
            template_id = template_data["template_id"]
            
            # Step 6: Share template
            share_response = await test_client.post(
                f"/api/projects/{project_id}/templates/{template_id}/share",
                json={
                    "users": ["user1", "user2"],
                    "permissions": ["read", "execute"]
                }
            )
            
            assert share_response.status_code == 200
            
            # Step 7: Get query history
            history_response = await test_client.get(
                f"/api/users/{user_id}/queries"
            )
            
            assert history_response.status_code == 200
            history_data = history_response.json()
            assert len(history_data["queries"]) > 0
            assert any(q["template_id"] == template_id for q in history_data["queries"])

    @pytest.mark.asyncio
    async def test_query_execution_with_error_recovery(self, test_client, mock_ai_agents):
        """Test query execution with error recovery."""
        user_id = "test-user"
        project_id = "test-project"
        datasource_id = "test-datasource"
        
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_get.return_value = mock_ai_agents["query"]
            
            # Step 1: Submit valid query
            response = await test_client.post(
                "/api/queries",
                json={
                    "query": "Show me users",
                    "project_id": project_id,
                    "datasource_id": datasource_id,
                    "dialect": "clickhouse"
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Step 2: Execute with simulated database error
            with patch('database.execute_query') as mock_execute:
                mock_execute.side_effect = Exception("Connection timeout")
                
                execute_response = await test_client.post(
                    "/api/queries/execute",
                    json={
                        "sql": result["optimized_sql"],
                        "datasource_id": datasource_id,
                        "project_id": project_id
                    }
                )
                
                assert execute_response.status_code == 500
                error_data = execute_response.json()
                assert "database" in str(error_data).lower()
            
            # Step 3: Retry with fallback
            retry_response = await test_client.post(
                "/api/queries/execute",
                json={
                    "sql": result["optimized_sql"],
                    "datasource_id": datasource_id,
                    "project_id": project_id,
                    "retry": True,
                    "timeout_ms": 30000
                }
            )
            
            # Should succeed or give appropriate error
            assert retry_response.status_code in [200, 500]


class TestDashboardWorkflow:
    """Test dashboard workflow and analytics."""

    @pytest.mark.asyncio
    async def test_dashboard_workflow(self, test_client):
        """Test complete dashboard workflow."""
        user_id = "test-user"
        project_id = "test-project"
        
        # Step 1: Get dashboard overview
        overview_response = await test_client.get(
            f"/api/users/{user_id}/dashboard"
        )
        
        assert overview_response.status_code == 200
        overview_data = overview_response.json()
        assert "recent_queries" in overview_data
        assert "active_projects" in overview_data
        assert "agent_stats" in overview_data
        
        # Step 2: Get project analytics
        analytics_response = await test_client.get(
            f"/api/projects/{project_id}/analytics"
        )
        
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        assert "query_frequency" in analytics_data
        assert "popular_queries" in analytics_data
        assert "performance_metrics" in analytics_data
        
        # Step 3: Get agent performance
        agent_response = await test_client.get(
            f"/api/projects/{project_id}/agents/performance"
        )
        
        assert agent_response.status_code == 200
        agent_data = agent_response.json()
        assert "query_agent" in agent_data
        assert "response_times" in agent_data
        assert "success_rates" in agent_data
        
        # Step 4: Get system health
        health_response = await test_client.get(
            f"/api/projects/{project_id}/health"
        )
        
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert "overall_status" in health_data
        assert "database_status" in health_data
        assert "agent_status" in health_data


class TestCollaborationWorkflow:
    """Test team collaboration workflow."""

    @pytest.mark.asyncio
    async def test_team_collaboration_workflow(self, test_client):
        """Test complete team collaboration workflow."""
        user_id = "test-user"
        project_id = "test-project"
        
        # Step 1: Add team member
        member_response = await test_client.post(
            f"/api/projects/{project_id}/members",
            json={
                "email": "teammate@example.com",
                "role": "editor",
                "permissions": ["read", "write", "execute"]
            }
        )
        
        assert member_response.status_code == 201
        member_data = member_response.json()
        member_id = member_data["member_id"]
        
        # Step 2: Create shared query template
        template_response = await test_client.post(
            f"/api/projects/{project_id}/templates",
            json={
                "name": "Team Sales Report",
                "query": "SELECT product, SUM(amount) FROM sales GROUP BY product",
                "description": "Standard sales report for the team",
                "shared": True,
                "tags": ["team", "sales", "report"]
            }
        )
        
        assert template_response.status_code == 201
        template_data = template_response.json()
        template_id = template_data["template_id"]
        
        # Step 3: Team member uses shared template
        usage_response = await test_client.post(
            "/api/queries/from-template",
            json={
                "template_id": template_id,
                "project_id": project_id,
                "parameters": {
                    "date_range": "last_30_days"
                }
            }
        )
        
        assert usage_response.status_code == 200
        usage_data = usage_response.json()
        assert "generated_sql" in usage_data
        
        # Step 4: Create team discussion
        discussion_response = await test_client.post(
            f"/api/projects/{project_id}/discussions",
            json={
                "title": "Sales Report Optimization",
                "content": "Can we optimize this query better?",
                "query_id": usage_data["query_id"]
            }
        )
        
        assert discussion_response.status_code == 201
        discussion_data = discussion_response.json()
        discussion_id = discussion_data["discussion_id"]
        
        # Step 5: Add comment to discussion
        comment_response = await test_client.post(
            f"/api/projects/{project_id}/discussions/{discussion_id}/comments",
            json={
                "content": "We could add indexing on the date column",
                "code_snippet": "CREATE INDEX idx_sales_date ON sales(date)"
            }
        )
        
        assert comment_response.status_code == 201


class TestErrorRecoveryWorkflow:
    """Test error recovery and resilience workflows."""

    @pytest.mark.asyncio
    async def test_query_error_recovery(self, test_client):
        """Test query error recovery workflow."""
        user_id = "test-user"
        project_id = "test-project"
        datasource_id = "test-datasource"
        
        # Step 1: Submit query that will fail
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_agent = Mock()
            mock_agent.status = AgentStatus.READY
            mock_agent.process = AsyncMock(side_effect=Exception("SQL validation failed"))
            mock_get.return_value = mock_agent
            
            response = await test_client.post(
                "/api/queries",
                json={
                    "query": "DROP TABLE users",
                    "project_id": project_id,
                    "datasource_id": datasource_id,
                    "dialect": "clickhouse"
                }
            )
            
            assert response.status_code == 400
            error_data = response.json()
            assert "validation" in str(error_data).lower()
        
        # Step 2: Get error suggestions
        suggestions_response = await test_client.get(
            f"/api/users/{user_id}/queries/errors/suggestions"
        )
        
        assert suggestions_response.status_code == 200
        suggestions_data = suggestions_response.json()
        assert "common_fixes" in suggestions_data
        assert "prevention_tips" in suggestions_data
        
        # Step 3: Retry with corrected query
        with patch('agents.api.agents.QueryAgent.get_instance') as mock_get:
            mock_agent = Mock()
            mock_agent.status = AgentStatus.READY
            mock_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT name FROM users",
                "optimized_sql": "SELECT name FROM users LIMIT 1000",
                "explanation": "Safe query to get user names",
                "dialect": "clickhouse",
                "cached": False
            })
            mock_get.return_value = mock_agent
            
            retry_response = await test_client.post(
                "/api/queries",
                json={
                    "query": "Show me user names safely",
                    "project_id": project_id,
                    "datasource_id": datasource_id,
                    "dialect": "clickhouse"
                }
            )
            
            assert retry_response.status_code == 200

    @pytest.mark.asyncio
    async def test_system_error_recovery(self, test_client):
        """Test system-wide error recovery."""
        # Simulate system maintenance mode
        with patch('app.maintenance_mode', True):
            response = await test_client.get("/health")
            assert response.status_code == 503
        
        # Check maintenance status
        maintenance_response = await test_client.get("/api/maintenance/status")
        assert maintenance_response.status_code == 200
        maintenance_data = maintenance_response.json()
        assert maintenance_data["maintenance_mode"] is True
        assert "estimated_end_time" in maintenance_data
        
        # After maintenance (mock)
        with patch('app.maintenance_mode', False):
            response = await test_client.get("/health")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])