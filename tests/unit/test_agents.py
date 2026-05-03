"""
Unit tests for AI agents functionality.
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))

from agents.base import BaseAgent
from agents.config import AgentConfig
from agents.registry import AgentRegistry


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    def test_agent_initialization(self):
        """Test agent initialization with basic parameters."""
        agent = BaseAgent(name="test-agent", agent_type="query")
        assert agent.name == "test-agent"
        assert agent.agent_type == "query"
        assert agent.status == "initialized"
        assert agent.config is None
    
    def test_agent_lifecycle(self):
        """Test agent start/stop lifecycle."""
        agent = BaseAgent(name="test-agent")
        
        # Test starting agent
        agent.start()
        assert agent.status == "running"
        
        # Test stopping agent
        agent.stop()
        assert agent.status == "stopped"
    
    def test_agent_configuration(self):
        """Test agent configuration management."""
        config = AgentConfig(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7
        )
        
        agent = BaseAgent(name="test-agent", config=config)
        assert agent.config == config
        assert agent.config.model == "gpt-4"
    
    @patch('agents.base.BaseAgent._initialize')
    def test_agent_initialization_hook(self, mock_init):
        """Test agent initialization hook."""
        mock_init.return_value = True
        
        agent = BaseAgent(name="test-agent")
        agent.start()
        
        mock_init.assert_called_once()


class TestAgentConfig:
    """Test cases for AgentConfig class."""
    
    def test_config_creation(self):
        """Test configuration creation with default values."""
        config = AgentConfig()
        assert config.model == "gpt-4"
        assert config.max_tokens == 1000
        assert config.temperature == 0.7
    
    def test_config_custom_values(self):
        """Test configuration with custom values."""
        config = AgentConfig(
            model="claude-3",
            max_tokens=2000,
            temperature=0.5,
            timeout=30
        )
        assert config.model == "claude-3"
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.timeout == 30
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration
        config = AgentConfig(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7
        )
        assert config.validate() is True
        
        # Invalid configuration
        config_invalid = AgentConfig(
            model="",
            max_tokens=-1,
            temperature=2.0
        )
        assert config_invalid.validate() is False


class TestAgentRegistry:
    """Test cases for AgentRegistry class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.registry = AgentRegistry()
    
    def test_register_agent(self):
        """Test agent registration."""
        agent = BaseAgent(name="test-agent")
        self.registry.register(agent)
        
        assert "test-agent" in self.registry.agents
        assert self.registry.agents["test-agent"] == agent
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        agent = BaseAgent(name="test-agent")
        self.registry.register(agent)
        self.registry.unregister("test-agent")
        
        assert "test-agent" not in self.registry.agents
    
    def test_get_agent(self):
        """Test retrieving an agent."""
        agent = BaseAgent(name="test-agent")
        self.registry.register(agent)
        
        retrieved_agent = self.registry.get_agent("test-agent")
        assert retrieved_agent == agent
    
    def test_get_nonexistent_agent(self):
        """Test retrieving a non-existent agent."""
        with pytest.raises(KeyError):
            self.registry.get_agent("nonexistent-agent")
    
    def test_list_agents(self):
        """Test listing all agents."""
        agent1 = BaseAgent(name="agent1")
        agent2 = BaseAgent(name="agent2")
        
        self.registry.register(agent1)
        self.registry.register(agent2)
        
        agents = self.registry.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
    
    def test_agent_types(self):
        """Test agent type filtering."""
        query_agent = BaseAgent(name="query-agent", agent_type="query")
        design_agent = BaseAgent(name="design-agent", agent_type="design")
        
        self.registry.register(query_agent)
        self.registry.register(design_agent)
        
        query_agents = self.registry.get_agents_by_type("query")
        design_agents = self.registry.get_agents_by_type("design")
        
        assert len(query_agents) == 1
        assert len(design_agents) == 1
        assert query_agents["query-agent"].agent_type == "query"
        assert design_agents["design-agent"].agent_type == "design"


class TestAgentCommunication:
    """Test cases for agent communication."""
    
    def test_agent_message_passing(self):
        """Test message passing between agents."""
        sender = BaseAgent(name="sender")
        receiver = BaseAgent(name="receiver")
        
        # Mock the message handling
        def mock_message_handler(message):
            return f"Processed: {message}"
        
        receiver.message_handler = mock_message_handler
        
        # Send a message
        response = sender.send_message("Hello", receiver)
        assert response == "Processed: Hello"
    
    def test_agent_error_handling(self):
        """Test error handling in agent communication."""
        sender = BaseAgent(name="sender")
        receiver = BaseAgent(name="receiver")
        
        # Mock a failing message handler
        def failing_handler(message):
            raise Exception("Communication error")
        
        receiver.message_handler = failing_handler
        
        # Test error handling
        with pytest.raises(Exception):
            sender.send_message("Hello", receiver)


if __name__ == "__main__":
    pytest.main([__file__])