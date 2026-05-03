"""
Query Agent specific tests for Duet Company backend.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from apps.backend.src.agents.query_agent import QueryAgent
from apps.backend.src.agents.base import BaseAgent


class TestQueryAgentSpecific:
    """Query Agent specific test cases."""
    
    @pytest.fixture
    def query_agent(self):
        """Create a QueryAgent instance."""
        return QueryAgent(
            name="test-query-agent",
            agent_type="query",
            config={
                "model": "gpt-4",
                "max_tokens": 1000,
                "temperature": 0.7
            }
        )
    
    @pytest.mark.unit
    def test_query_agent_inherits_from_base(self, query_agent):
        """Test that QueryAgent inherits from BaseAgent."""
        assert isinstance(query_agent, BaseAgent)
        assert query_agent.agent_type == "query"
        assert query_agent.name == "test-query-agent"
    
    @pytest.mark.unit
    def test_query_agent_default_config(self):
        """Test QueryAgent default configuration."""
        agent = QueryAgent()
        assert agent.config.model == "gpt-4"
        assert agent.config.max_tokens == 1000
        assert agent.config.temperature == 0.7
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._initialize_llm_manager')
    def test_query_agent_initialization_with_config(self, mock_init):
        """Test QueryAgent initialization with custom config."""
        config = {
            "model": "claude-3",
            "max_tokens": 2000,
            "temperature": 0.5
        }
        
        agent = QueryAgent(config=config)
        
        assert agent.config.model == "claude-3"
        assert agent.config.max_tokens == 2000
        assert agent.config.temperature == 0.5
        mock_init.assert_called_once()
    
    @pytest.mark.unit
    def test_query_agent_has_query_processor(self, query_agent):
        """Test that QueryAgent has query processor."""
        assert hasattr(query_agent, 'query_processor')
        assert query_agent.query_processor is not None
    
    @pytest.mark.unit
    def test_query_agent_has_llm_manager(self, query_agent):
        """Test that QueryAgent has LLM manager."""
        assert hasattr(query_agent, 'llm_manager')
        assert query_agent.llm_manager is not None
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._validate_query')
    def test_query_validation_method(self, mock_validate, query_agent):
        """Test query validation method."""
        from apps.backend.src.schemas import QueryRequest
        
        query_request = QueryRequest(query="Test query")
        query_agent._validate_query(query_request)
        
        mock_validate.assert_called_once_with(query_request)
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._preprocess_query')
    def test_query_preprocessing(self, mock_preprocess, query_agent):
        """Test query preprocessing."""
        from apps.backend.src.schemas import QueryRequest
        
        query_request = QueryRequest(query="Test query")
        query_agent._preprocess_query(query_request)
        
        mock_preprocess.assert_called_once_with(query_request)
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._postprocess_response')
    def test_response_postprocessing(self, mock_postprocess, query_agent):
        """Test response postprocessing."""
        raw_response = {"response": "Raw response", "confidence": 0.8}
        
        processed = query_agent._postprocess_response(raw_response)
        
        mock_postprocess.assert_called_once_with(raw_response)
        assert processed is not None
    
    @pytest.mark.unit
    def test_query_agent_state_management(self, query_agent):
        """Test QueryAgent state management."""
        # Initial state
        assert query_agent.status == "initialized"
        
        # Start agent
        query_agent.start()
        assert query_agent.status == "running"
        
        # Stop agent
        query_agent.stop()
        assert query_agent.status == "stopped"
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._health_check')
    def test_health_check(self, mock_health, query_agent):
        """Test QueryAgent health check."""
        mock_health.return_value = True
        
        is_healthy = query_agent.health_check()
        
        assert is_healthy is True
        mock_health.assert_called_once()
    
    @pytest.mark.unit
    def test_query_agent_error_handling(self, query_agent):
        """Test QueryAgent error handling."""
        with pytest.raises(ValueError):
            query_agent.process_query(None)
        
        with pytest.raises(ValueError):
            query_agent._validate_query(None)
    
    @pytest.mark.integration
    @patch('apps.backend.src.agents.query_agent.QueryAgent._call_llm_provider')
    @patch('apps.backend.src.agents.query_agent.QueryAgent._validate_query')
    async def test_full_query_pipeline(self, mock_validate, mock_call, query_agent):
        """Test full query processing pipeline."""
        from apps.backend.src.schemas import QueryRequest
        
        # Setup mocks
        mock_validate.return_value = True
        mock_call.return_value = {
            "response": "Processed response",
            "confidence": 0.9,
            "sources": ["doc1", "doc2"]
        }
        
        # Execute pipeline
        query_request = QueryRequest(query="What is AI?")
        result = await query_agent.process_query(query_request)
        
        # Verify results
        assert result["response"] == "Processed response"
        assert result["confidence"] == 0.9
        assert len(result["sources"]) == 2
        
        # Verify calls
        mock_validate.assert_called_once()
        mock_call.assert_called_once()
    
    @pytest.mark.performance
    @patch('apps.backend.src.agents.query_agent.QueryAgent._call_llm_provider')
    async def test_query_performance(self, mock_call, query_agent):
        """Test query processing performance."""
        import time
        
        mock_call.return_value = {
            "response": "Fast response",
            "confidence": 0.8
        }
        
        # Time multiple queries
        start_time = time.time()
        for i in range(5):
            query_request = QueryRequest(query=f"Query {i}")
            await query_agent.process_query(query_request)
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 2.0
        assert mock_call.call_count == 5