"""
Chat API tests for Duet Company backend.
"""

import pytest
from unittest.mock import Mock, patch
import json
from fastapi.testclient import TestClient
from apps.backend.main import app


client = TestClient(app)


class TestChatAPI:
    """Test cases for chat API endpoints."""
    
    @pytest.mark.api
    def test_chat_endpoint_available(self):
        """Test that chat endpoint is available."""
        response = client.get("/chat/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_chat_completion(self):
        """Test chat completion endpoint."""
        test_data = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "model": "gpt-3.5-turbo"
        }
        
        with patch('apps.backend.main.chat_completion') as mock_chat:
            mock_chat.return_value = {
                "response": "I'm doing well, thank you!",
                "usage": {"prompt_tokens": 10, "completion_tokens": 10}
            }
            
            response = client.post("/chat/completion", json=test_data)
            assert response.status_code == 200
            assert "response" in response.json()
    
    @pytest.mark.api
    def test_chat_history_endpoint(self):
        """Test chat history endpoint."""
        response = client.get("/chat/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.api
    def test_chat_clear_history(self):
        """Test clearing chat history."""
        response = client.delete("/chat/history")
        assert response.status_code == 200
        assert "message" in response.json()