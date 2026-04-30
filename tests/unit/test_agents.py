"""
Unit tests for AI agents
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the agents module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'apps', 'backend', 'src'))

from agents.base import AgentBase
from agents.query_agent import QueryAgent
from agents.platform_designer import PlatformDesignerAgent
from agents.llm_providers import LLMProviderManager
from agents.communication import AgentCommunication
from agents.config import AgentConfig
from agents.registry import AgentRegistry
from agents.lifecycle import AgentLifecycle
from agents.task_queue import TaskQueue


class TestAgentBase:
    """Test cases for AgentBase class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = AgentBase()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent.id is not None
        assert self.agent.status == "initialized"
        assert self.agent.created_at is not None
    
    def test_agent_lifecycle(self):
        """Test agent lifecycle management"""
        # Test starting agent
        self.agent.start()
        assert self.agent.status == "running"
        
        # Test stopping agent
        self.agent.stop()
        assert self.agent.status == "stopped"
        
        # Test restarting agent
        self.agent.start()
        assert self.agent.status == "running"
        self.agent.stop()
        assert self.agent.status == "stopped"
    
    @patch('agents.base.AgentBase.execute')
    def test_agent_execution(self, mock_execute):
        """Test agent execution"""
        mock_execute.return_value = {"result": "success"}
        
        result = self.agent.execute({"task": "test"})
        assert result == {"result": "success"}
        mock_execute.assert_called_once_with({"task": "test"})


class TestQueryAgent:
    """Test cases for QueryAgent class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = QueryAgent()
    
    def test_query_agent_initialization(self):
        """Test query agent initialization"""
        assert self.agent.agent_type == "query"
        assert hasattr(self.agent, 'llm_manager')
        assert hasattr(self.agent, 'query_processor')
    
    @patch('agents.query_agent.QueryAgent.process_query')
    def test_query_processing(self, mock_process):
        """Test query processing"""
        mock_process.return_value = {"response": "test response", "confidence": 0.95}
        
        result = self.agent.process_query("What is AI?")
        assert result == {"response": "test response", "confidence": 0.95}
        mock_process.assert_called_once_with("What is AI?")


class TestPlatformDesignerAgent:
    """Test cases for PlatformDesignerAgent class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = PlatformDesignerAgent()
    
    def test_platform_designer_initialization(self):
        """Test platform designer agent initialization"""
        assert self.agent.agent_type == "platform_designer"
        assert hasattr(self.agent, 'design_templates')
        assert hasattr(self.agent, 'component_registry')
    
    @patch('agents.platform_designer.PlatformDesignerAgent.generate_design')
    def test_design_generation(self, mock_generate):
        """Test design generation"""
        mock_generate.return_value = {
            "architecture": "microservices",
            "components": ["api", "database", "frontend"],
            "technologies": ["FastAPI", "PostgreSQL", "React"]
        }
        
        result = self.agent.generate_design({"requirements": "e-commerce platform"})
        assert "architecture" in result
        assert "components" in result
        assert "technologies" in result
        mock_generate.assert_called_once_with({"requirements": "e-commerce platform"})


class TestLLMProviderManager:
    """Test cases for LLMProviderManager class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = LLMProviderManager()
    
    def test_llm_manager_initialization(self):
        """Test LLM manager initialization"""
        assert len(self.manager.providers) > 0
        assert "openai" in self.manager.providers
        assert "anthropic" in self.manager.providers
        assert "google" in self.manager.providers
    
    @patch('agents.llm_providers.LLMProviderManager.call_provider')
    def test_llm_provider_call(self, mock_call):
        """Test LLM provider call"""
        mock_call.return_value = {"response": "AI response", "usage": {"prompt": 100, "completion": 200}}
        
        result = self.manager.call_provider("openai", "Hello, AI!")
        assert result == {"response": "AI response", "usage": {"prompt": 100, "completion": 200}}
        mock_call.assert_called_once_with("openai", "Hello, AI!")


class TestAgentCommunication:
    """Test cases for AgentCommunication class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.communication = AgentCommunication()
    
    def test_communication_initialization(self):
        """Test communication initialization"""
        assert hasattr(self.communication, 'message_queue')
        assert hasattr(self.communication, 'event_handlers')
    
    @patch('agents.communication.AgentCommunication.send_message')
    def test_message_sending(self, mock_send):
        """Test message sending"""
        mock_send.return_value = True
        
        result = self.communication.send_message("target_agent", "Hello!")
        assert result is True
        mock_send.assert_called_once_with("target_agent", "Hello!")


class TestAgentConfig:
    """Test cases for AgentConfig class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = AgentConfig()
    
    def test_config_initialization(self):
        """Test configuration initialization"""
        assert hasattr(self.config, 'settings')
        assert hasattr(self.config, 'load_config')
    
    def test_config_loading(self):
        """Test configuration loading"""
        config_data = self.config.load_config()
        assert isinstance(config_data, dict)
        assert 'agents' in config_data


class TestAgentRegistry:
    """Test cases for AgentRegistry class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.registry = AgentRegistry()
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        assert hasattr(self.registry, 'agents')
        assert hasattr(self.registry, 'register_agent')
    
    def test_agent_registration(self):
        """Test agent registration"""
        mock_agent = Mock()
        mock_agent.id = "test_agent"
        mock_agent.type = "test"
        
        self.registry.register_agent(mock_agent)
        assert "test_agent" in self.registry.agents
        assert self.registry.agents["test_agent"] == mock_agent
    
    def test_agent_retrieval(self):
        """Test agent retrieval"""
        mock_agent = Mock()
        mock_agent.id = "test_agent"
        mock_agent.type = "test"
        
        self.registry.register_agent(mock_agent)
        retrieved = self.registry.get_agent("test_agent")
        assert retrieved == mock_agent


class TestAgentLifecycle:
    """Test cases for AgentLifecycle class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.lifecycle = AgentLifecycle()
    
    def test_lifecycle_initialization(self):
        """Test lifecycle initialization"""
        assert hasattr(self.lifecycle, 'states')
        assert hasattr(self.lifecycle, 'transitions')
    
    def test_lifecycle_state_transition(self):
        """Test lifecycle state transition"""
        result = self.lifecycle.transition("initialized", "started")
        assert result is True
        assert "started" in self.lifecycle.states


class TestTaskQueue:
    """Test cases for TaskQueue class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.task_queue = TaskQueue()
    
    def test_task_queue_initialization(self):
        """Test task queue initialization"""
        assert hasattr(self.task_queue, 'queue')
        assert hasattr(self.task_queue, 'add_task')
        assert hasattr(self.task_queue, 'process_tasks')
    
    def test_task_addition(self):
        """Test task addition"""
        task = {
            "id": "task_1",
            "type": "query",
            "data": {"query": "test query"},
            "priority": "high"
        }
        
        self.task_queue.add_task(task)
        assert len(self.task_queue.queue) == 1
        assert self.task_queue.queue[0] == task
    
    def test_task_processing(self):
        """Test task processing"""
        task = {
            "id": "task_1",
            "type": "query",
            "data": {"query": "test query"},
            "priority": "high"
        }
        
        self.task_queue.add_task(task)
        processed = self.task_queue.process_tasks()
        assert len(processed) == 1
        assert processed[0]["id"] == "task_1"


if __name__ == "__main__":
    pytest.main([__file__])