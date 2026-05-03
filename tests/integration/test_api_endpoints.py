"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))

# Mock the FastAPI app
from main import app
client = TestClient(app)


class TestAgentAPI:
    """Test cases for agent-related API endpoints."""
    
    def setup_method(self):
        """Setup test environment."""
        # Mock the agent registry
        with patch('agents.registry.AgentRegistry') as mock_registry:
            self.mock_registry = mock_registry
            mock_instance = mock_registry.return_value
            mock_instance.list_agents.return_value = {}
            
            # Test client setup
            self.client = TestClient(app)
    
    def test_create_agent_endpoint(self):
        """Test creating a new agent."""
        agent_data = {
            "name": "test-agent",
            "type": "query",
            "config": {
                "model": "gpt-4",
                "max_tokens": 1000
            }
        }
        
        response = self.client.post("/agents/", json=agent_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-agent"
        assert data["type"] == "query"
        assert data["config"]["model"] == "gpt-4"
    
    def test_create_agent_validation_error(self):
        """Test validation error when creating agent with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should be invalid
            "type": "invalid_type"
        }
        
        response = self.client.post("/agents/", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_agent_endpoint(self):
        """Test retrieving an existing agent."""
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_agent = Mock()
            mock_agent.name = "test-agent"
            mock_agent.type = "query"
            mock_agent.config = {"model": "gpt-4"}
            mock_instance.get_agent.return_value = mock_agent
            
            response = self.client.get("/agents/test-agent")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "test-agent"
            assert data["type"] == "query"
    
    def test_get_nonexistent_agent(self):
        """Test retrieving a non-existent agent."""
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_instance.get_agent.side_effect = KeyError("Agent not found")
            
            response = self.client.get("/agents/nonexistent-agent")
            
            assert response.status_code == 404
    
    def test_list_agents_endpoint(self):
        """Test listing all agents."""
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_instance.list_agents.return_value = {
                "agent1": {"name": "agent1", "type": "query"},
                "agent2": {"name": "agent2", "type": "design"}
            }
            
            response = self.client.get("/agents/")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert "agent1" in data
            assert "agent2" in data
    
    def test_delete_agent_endpoint(self):
        """Test deleting an agent."""
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_instance.unregister.return_value = True
            
            response = self.client.delete("/agents/test-agent")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Agent deleted successfully"


class TestQueryAPI:
    """Test cases for query-related API endpoints."""
    
    def test_query_endpoint(self):
        """Test query endpoint with valid request."""
        query_data = {
            "text": "Show me user metrics",
            "agent_type": "query",
            "config": {
                "max_tokens": 500
            }
        }
        
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_agent = Mock()
            mock_agent.query.return_value = "User metrics data"
            mock_instance.get_agent.return_value = mock_agent
            
            response = self.client.post("/query/", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "result" in data
            assert data["result"] == "User metrics data"
    
    def test_query_endpoint_no_agent(self):
        """Test query endpoint when agent doesn't exist."""
        query_data = {
            "text": "Show me user metrics",
            "agent_type": "nonexistent"
        }
        
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_instance.get_agent.side_effect = KeyError("Agent not found")
            
            response = self.client.post("/query/", json=query_data)
            
            assert response.status_code == 404
    
    def test_query_endpoint_error(self):
        """Test query endpoint when agent raises an error."""
        query_data = {
            "text": "Show me user metrics",
            "agent_type": "query"
        }
        
        with patch('agents.registry.AgentRegistry') as mock_registry:
            mock_instance = mock_registry.return_value
            mock_agent = Mock()
            mock_agent.query.side_effect = Exception("Query failed")
            mock_instance.get_agent.return_value = mock_agent
            
            response = self.client.post("/query/", json=query_data)
            
            assert response.status_code == 500


class TestHealthAPI:
    """Test cases for health check API endpoints."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = self.client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "uptime" in data
        assert "requests" in data


class TestConfigurationAPI:
    """Test cases for configuration API endpoints."""
    
    def test_get_config_endpoint(self):
        """Test getting configuration."""
        response = self.client.get("/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "max_tokens" in data
        assert "temperature" in data
    
    def test_update_config_endpoint(self):
        """Test updating configuration."""
        new_config = {
            "model": "claude-3",
            "max_tokens": 2000,
            "temperature": 0.5
        }
        
        response = self.client.put("/config", json=new_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "claude-3"
        assert data["max_tokens"] == 2000
        assert data["temperature"] == 0.5
    
    def test_update_config_validation_error(self):
        """Test validation error when updating config with invalid data."""
        invalid_config = {
            "model": "",
            "max_tokens": -1
        }
        
        response = self.client.put("/config", json=invalid_config)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])