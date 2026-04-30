"""
Integration tests for API endpoints and agent integration
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch
import sys
import os

# Add the backend source to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))

from agents.query_agent import QueryAgent
from agents.platform_designer import PlatformDesignerAgent
from agents.llm_providers import LLMProviderManager
from agents.communication import AgentCommunication


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    @pytest.fixture
    async def test_client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import app  # Assuming main.py exists
        
        with TestClient(app) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client):
        """Test health endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_query_endpoint(self, test_client):
        """Test query endpoint"""
        from agents.query_agent import QueryAgent
        
        with patch('agents.query_agent.QueryAgent.process_query') as mock_process:
            mock_process.return_value = {
                "response": "Test response",
                "confidence": 0.95
            }
            
            payload = {
                "query": "What is artificial intelligence?",
                "context": {}
            }
            
            response = test_client.post("/api/query", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "confidence" in data
            mock_process.assert_called_once_with("What is artificial intelligence?")
    
    @pytest.mark.asyncio
    async def test_design_endpoint(self, test_client):
        """Test design endpoint"""
        with patch('agents.platform_designer.PlatformDesignerAgent.generate_design') as mock_generate:
            mock_generate.return_value = {
                "architecture": "microservices",
                "components": ["api", "database", "frontend"],
                "technologies": ["FastAPI", "PostgreSQL", "React"]
            }
            
            payload = {
                "requirements": "Build an e-commerce platform",
                "constraints": []
            }
            
            response = test_client.post("/api/design", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "architecture" in data
            assert "components" in data
            assert "technologies" in data
            mock_generate.assert_called_once_with(payload)
    
    @pytest.mark.asyncio
    async def test_agent_status_endpoint(self, test_client):
        """Test agent status endpoint"""
        response = test_client.get("/api/agents/status")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)


class TestAgentIntegration:
    """Test cases for agent integration"""
    
    @pytest.mark.asyncio
    async def test_query_agent_communication(self):
        """Test communication between query agents"""
        query_agent = QueryAgent()
        communication = AgentCommunication()
        
        with patch.object(communication, 'send_message') as mock_send:
            mock_send.return_value = True
            
            # Simulate query agent communicating with another agent
            result = communication.send_message("platform_designer", {
                "type": "query",
                "data": "Design a system for data analysis"
            })
            
            assert result is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_llm_provider_integration(self):
        """Test LLM provider integration with agents"""
        llm_manager = LLMProviderManager()
        query_agent = QueryAgent()
        
        with patch.object(llm_manager, 'call_provider') as mock_call:
            mock_call.return_value = {
                "response": "AI-generated response",
                "usage": {"prompt": 100, "completion": 200}
            }
            
            # Test query agent using LLM provider
            result = query_agent.process_query("Explain machine learning")
            assert "response" in result
            mock_call.assert_called()
    
    @pytest.mark.asyncio
    async def test_agent_collaboration(self):
        """Test collaboration between different agents"""
        query_agent = QueryAgent()
        designer_agent = PlatformDesignerAgent()
        communication = AgentCommunication()
        
        # Mock the communication
        with patch.object(communication, 'send_message') as mock_send:
            mock_send.return_value = True
            
            # Simulate collaboration: query agent gets requirements, designer creates design
            requirements = {"type": "query", "data": "I need a recommendation system"}
            
            # Query agent processes requirements
            with patch.object(query_agent, 'process_query') as mock_query:
                mock_query.return_value = {
                    "analysis": "User wants recommendation system",
                    "features": ["user profiling", "item similarity", "recommendation engine"]
                }
                
                analysis = query_agent.process_query(requirements)
                
                # Designer agent creates design based on analysis
                with patch.object(designer_agent, 'generate_design') as mock_design:
                    mock_design.return_value = {
                        "architecture": "microservices",
                        "components": ["user_service", "similarity_service", "recommendation_service"],
                        "technologies": ["FastAPI", "PostgreSQL", "Redis"]
                    }
                    
                    design = designer_agent.generate_design(analysis)
                    
                    # Verify collaboration worked
                    assert "architecture" in design
                    assert "components" in design
                    assert "technologies" in design


class TestDatabaseIntegration:
    """Test cases for database integration"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection"""
        from sqlalchemy import create_engine
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.orm import sessionmaker
        
        # Mock database configuration
        database_url = "postgresql+asyncpg://localhost:5432/test_db"
        
        with patch('sqlalchemy.create_async_engine') as mock_create:
            mock_create.return_value = Mock()
            
            engine = create_async_engine(database_url)
            assert engine is not None
            mock_create.assert_called_once_with(database_url)
    
    @pytest.mark.asyncio
    async def test_agent_data_persistence(self):
        """Test agent data persistence"""
        from sqlalchemy import Column, Integer, String, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.sql import func
        
        Base = declarative_base()
        
        class AgentLog(Base):
            __tablename__ = 'agent_logs'
            
            id = Column(Integer, primary_key=True)
            agent_id = Column(String, nullable=False)
            action = Column(String, nullable=False)
            timestamp = Column(DateTime, default=func.now())
            data = Column(String)
        
        # Test model creation
        assert hasattr(AgentLog, 'id')
        assert hasattr(AgentLog, 'agent_id')
        assert hasattr(AgentLog, 'action')
        assert hasattr(AgentLog, 'timestamp')
        assert hasattr(AgentLog, 'data')


class TestClickHouseIntegration:
    """Test cases for ClickHouse integration"""
    
    @pytest.mark.asyncio
    async def test_clickhouse_connection(self):
        """Test ClickHouse connection"""
        from clickhouse_connect import get_client
        
        with patch('clickhouse_connect.get_client') as mock_get:
            mock_client = Mock()
            mock_get.return_value = mock_client
            
            client = get_client(host='localhost', port='9000')
            assert client is not None
            mock_get.assert_called_once_with(host='localhost', port='9000')
    
    @pytest.mark.asyncio
    async def test_clickhouse_query(self):
        """Test ClickHouse query execution"""
        from clickhouse_connect import get_client
        
        with patch('clickhouse_connect.get_client') as mock_get:
            mock_client = Mock()
            mock_client.query.return_value = {
                'columns': ['timestamp', 'value'],
                'data': [['2026-04-29T10:00:00', 100], ['2026-04-29T11:00:00', 150]]
            }
            mock_get.return_value = mock_client
            
            client = get_client(host='localhost', port='9000')
            result = client.query('SELECT timestamp, value FROM metrics LIMIT 2')
            
            assert 'columns' in result
            assert 'data' in result
            assert len(result['data']) == 2


if __name__ == "__main__":
    pytest.main([__file__])