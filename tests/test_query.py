"""
Query processing tests for Duet Company backend.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from apps.backend.src.agents.query_agent import QueryAgent
from apps.backend.src.schemas import QueryRequest


class TestQueryAgent:
    """Test cases for QueryAgent functionality."""
    
    @pytest.fixture
    def query_agent(self):
        """Create a QueryAgent instance for testing."""
        return QueryAgent()
    
    @pytest.mark.unit
    def test_query_agent_initialization(self, query_agent):
        """Test QueryAgent initialization."""
        assert query_agent.agent_type == "query"
        assert hasattr(query_agent, 'llm_manager')
        assert hasattr(query_agent, 'query_processor')
        assert query_agent.status == "initialized"
    
    @pytest.mark.unit
    def test_query_agent_start_stop(self, query_agent):
        """Test QueryAgent start/stop lifecycle."""
        query_agent.start()
        assert query_agent.status == "running"
        
        query_agent.stop()
        assert query_agent.status == "stopped"
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._initialize_llm_manager')
    def test_query_agent_llm_initialization(self, mock_init, query_agent):
        """Test LLM manager initialization."""
        mock_init.return_value = True
        
        query_agent.start()
        mock_init.assert_called_once()
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._process_query')
    async def test_process_query_basic(self, mock_process, query_agent):
        """Test basic query processing."""
        mock_process.return_value = {
            "response": "This is a test response",
            "confidence": 0.85,
            "sources": []
        }
        
        query_request = QueryRequest(query="What is AI?")
        result = await query_agent.process_query(query_request)
        
        assert result["response"] == "This is a test response"
        assert result["confidence"] == 0.85
        mock_process.assert_called_once_with(query_request)
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.query_agent.QueryAgent._validate_query')
    def test_query_validation(self, mock_validate, query_agent):
        """Test query validation."""
        mock_validate.return_value = True
        
        query_request = QueryRequest(query="What is AI?")
        is_valid = query_agent._validate_query(query_request)
        
        assert is_valid is True
        mock_validate.assert_called_once_with(query_request)
    
    @pytest.mark.unit
    def test_query_validation_fails(self, query_agent):
        """Test query validation failure."""
        with pytest.raises(ValueError):
            query_agent._validate_query(None)
    
    @pytest.mark.integration
    @patch('apps.backend.src.agents.query_agent.QueryAgent._call_llm_provider')
    async def test_llm_integration(self, mock_call, query_agent):
        """Test LLM provider integration."""
        mock_call.return_value = {
            "response": "LLM response",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
        
        query_request = QueryRequest(query="Test query")
        result = await query_agent.process_query(query_request)
        
        assert result["response"] == "LLM response"
        assert "usage" in result
        mock_call.assert_called_once()
    
    @pytest.mark.unit
    def test_error_handling(self, query_agent):
        """Test error handling in query processing."""
        with pytest.raises(Exception):
            await query_agent.process_query(None)
    
    @pytest.mark.performance
    @patch('apps.backend.src.agents.query_agent.QueryAgent._call_llm_provider')
    async def test_performance(self, mock_call, query_agent):
        """Test query processing performance."""
        mock_call.return_value = {
            "response": "Fast response",
            "usage": {"prompt_tokens": 5, "completion_tokens": 5}
        }
        
        import time
        start_time = time.time()
        
        for i in range(10):
            query_request = QueryRequest(query=f"Test query {i}")
            await query_agent.process_query(query_request)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete 10 queries in under 5 seconds
        assert processing_time < 5.0
    
    @pytest.mark.slow
    @patch('apps.backend.src.agents.query_agent.QueryAgent._call_llm_provider')
    async def test_slow_query_processing(self, mock_call, query_agent):
        """Test slow query processing (simulated)."""
        mock_call.side_effect = AsyncMock(
            side_effect=lambda x: {
                "response": f"Response for {x.query}",
                "usage": {"prompt_tokens": 10, "completion_tokens": 10}
            }
        )
        
        query_request = QueryRequest(query="Complex multi-step reasoning question")
        result = await query_agent.process_query(query_request)
        
        assert "Response for" in result["response"]
        mock_call.assert_called_once()