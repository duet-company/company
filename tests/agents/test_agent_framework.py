"""
Agent Framework tests for Duet Company backend.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from apps.backend.src.agents.base import BaseAgent
from apps.backend.src.agents.registry import AgentRegistry
from apps.backend.src.agents.communication import AgentCommunication
from apps.backend.src.agents.config import AgentConfig


class TestAgentFramework:
    """Agent Framework comprehensive test cases."""
    
    @pytest.fixture
    def sample_config(self):
        """Sample agent configuration."""
        return AgentConfig(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7,
            timeout=30
        )
    
    @pytest.mark.unit
    def test_base_agent_creation(self, sample_config):
        """Test BaseAgent creation with configuration."""
        agent = BaseAgent(
            name="test-agent",
            agent_type="general",
            config=sample_config
        )
        
        assert agent.name == "test-agent"
        assert agent.agent_type == "general"
        assert agent.config == sample_config
        assert agent.status == "initialized"
    
    @pytest.mark.unit
    def test_base_agent_lifecycle(self, sample_config):
        """Test BaseAgent lifecycle management."""
        agent = BaseAgent(name="test-agent", config=sample_config)
        
        # Test starting
        agent.start()
        assert agent.status == "running"
        
        # Test stopping
        agent.stop()
        assert agent.status == "stopped"
        
        # Test restarting
        agent.start()
        assert agent.status == "running"
    
    @pytest.mark.unit
    def test_agent_registry_creation(self):
        """Test AgentRegistry creation."""
        registry = AgentRegistry()
        assert len(registry.agents) == 0
        assert hasattr(registry, 'register')
        assert hasattr(registry, 'get_agent')
        assert hasattr(registry, 'unregister')
    
    @pytest.mark.unit
    def test_agent_registration(self, sample_config):
        """Test agent registration in registry."""
        registry = AgentRegistry()
        agent = BaseAgent(name="test-agent", config=sample_config)
        
        # Register agent
        registry.register(agent)
        
        # Verify registration
        assert "test-agent" in registry.agents
        assert registry.agents["test-agent"] == agent
    
    @pytest.mark.unit
    def test_agent_retrieval(self, sample_config):
        """Test agent retrieval from registry."""
        registry = AgentRegistry()
        agent = BaseAgent(name="test-agent", config=sample_config)
        
        registry.register(agent)
        retrieved = registry.get_agent("test-agent")
        
        assert retrieved == agent
    
    @pytest.mark.unit
    def test_agent_unregistration(self, sample_config):
        """Test agent unregistration."""
        registry = AgentRegistry()
        agent = BaseAgent(name="test-agent", config=sample_config)
        
        registry.register(agent)
        registry.unregister("test-agent")
        
        assert "test-agent" not in registry.agents
    
    @pytest.mark.unit
    def test_agent_list_agents(self, sample_config):
        """Test listing all agents."""
        registry = AgentRegistry()
        
        # Add multiple agents
        agent1 = BaseAgent(name="agent1", config=sample_config)
        agent2 = BaseAgent(name="agent2", config=sample_config)
        
        registry.register(agent1)
        registry.register(agent2)
        
        agents = registry.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
    
    @pytest.mark.unit
    def test_agent_get_by_type(self, sample_config):
        """Test getting agents by type."""
        registry = AgentRegistry()
        
        # Add agents with different types
        query_agent = BaseAgent(name="query", agent_type="query", config=sample_config)
        design_agent = BaseAgent(name="design", agent_type="design", config=sample_config)
        
        registry.register(query_agent)
        registry.register(design_agent)
        
        # Get by type
        query_agents = registry.get_agents_by_type("query")
        design_agents = registry.get_agents_by_type("design")
        
        assert len(query_agents) == 1
        assert len(design_agents) == 1
        assert query_agents["query"].agent_type == "query"
        assert design_agents["design"].agent_type == "design"
    
    @pytest.mark.unit
    def test_agent_communication_creation(self):
        """Test AgentCommunication creation."""
        communication = AgentCommunication()
        assert hasattr(communication, 'message_queue')
        assert hasattr(communication, 'event_handlers')
        assert hasattr(communication, 'send_message')
        assert hasattr(communication, 'receive_message')
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.communication.AgentCommunication._send_message_impl')
    def test_message_sending(self, mock_send):
        """Test message sending between agents."""
        communication = AgentCommunication()
        
        # Mock the implementation
        mock_send.return_value = True
        
        result = communication.send_message("target-agent", "Hello!")
        
        assert result is True
        mock_send.assert_called_once_with("target-agent", "Hello!")
    
    @pytest.mark.unit
    @patch('apps.backend.src.agents.communication.AgentCommunication._receive_message_impl')
    def test_message_receiving(self, mock_receive):
        """Test message receiving."""
        communication = AgentCommunication()
        
        # Mock the implementation
        mock_receive.return_value = {"message": "Hello!", "sender": "other-agent"}
        
        result = communication.receive_message("message-id")
        
        assert result["message"] == "Hello!"
        assert result["sender"] == "other-agent"
        mock_receive.assert_called_once_with("message-id")
    
    @pytest.mark.unit
    def test_agent_config_validation(self):
        """Test AgentConfig validation."""
        # Valid config
        config = AgentConfig(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7
        )
        assert config.validate() is True
        
        # Invalid config
        invalid_config = AgentConfig(
            model="",  # Empty model
            max_tokens=-1,  # Negative tokens
            temperature=2.0  # Invalid temperature
        )
        assert invalid_config.validate() is False
    
    @pytest.mark.unit
    def test_agent_error_handling(self, sample_config):
        """Test agent error handling."""
        agent = BaseAgent(name="test-agent", config=sample_config)
        
        # Test invalid operations
        with pytest.raises(ValueError):
            agent.start()  # Already started
        
        agent.stop()
        with pytest.raises(ValueError):
            agent.stop()  # Already stopped
    
    @pytest.mark.integration
    def test_full_agent_workflow(self, sample_config):
        """Test complete agent workflow."""
        # Create registry
        registry = AgentRegistry()
        
        # Create agents
        query_agent = BaseAgent(name="query", agent_type="query", config=sample_config)
        design_agent = BaseAgent(name="design", agent_type="design", config=sample_config)
        
        # Register agents
        registry.register(query_agent)
        registry.register(design_agent)
        
        # Test communication
        communication = AgentCommunication()
        
        # Send message
        result = communication.send_message("design", "Hello from query!")
        assert result is True
        
        # Verify agents are registered
        assert len(registry.list_agents()) == 2
        assert registry.get_agent("query") == query_agent
        assert registry.get_agent("design") == design_agent
    
    @pytest.mark.performance
    def test_agent_performance(self, sample_config):
        """Test agent performance."""
        import time
        
        # Create multiple agents
        registry = AgentRegistry()
        agents = []
        
        start_time = time.time()
        for i in range(10):
            agent = BaseAgent(name=f"agent{i}", config=sample_config)
            registry.register(agent)
            agents.append(agent)
        end_time = time.time()
        
        # Registration should be fast
        assert end_time - start_time < 1.0
        assert len(registry.list_agents()) == 10
    
    @pytest.mark.slow
    async def test_agent_concurrent_operations(self, sample_config):
        """Test concurrent agent operations."""
        import asyncio
        import time
        
        registry = AgentRegistry()
        
        async def register_agent(agent_id):
            agent = BaseAgent(name=f"agent{agent_id}", config=sample_config)
            registry.register(agent)
            await asyncio.sleep(0.01)  # Simulate work
            return agent
        
        # Concurrent registration
        start_time = time.time()
        tasks = [register_agent(i) for i in range(20)]
        agents = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all agents registered
        assert len(registry.list_agents()) == 20
        assert end_time - start_time < 2.0  # Should complete quickly