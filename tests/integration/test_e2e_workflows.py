"""
End-to-end tests for user workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the backend source to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))

from agents.query_agent import QueryAgent
from agents.platform_designer import PlatformDesignerAgent
from agents.llm_providers import LLMProviderManager
from agents.communication import AgentCommunication


class TestUserWorkflows:
    """Test cases for end-to-end user workflows"""
    
    @pytest.fixture
    def setup_test_agents(self):
        """Setup test agents"""
        query_agent = QueryAgent()
        designer_agent = PlatformDesignerAgent()
        llm_manager = LLMProviderManager()
        communication = AgentCommunication()
        
        return {
            'query_agent': query_agent,
            'designer_agent': designer_agent,
            'llm_manager': llm_manager,
            'communication': communication
        }
    
    def test_complete_user_query_workflow(self, setup_test_agents):
        """Test complete user query workflow"""
        agents = setup_test_agents
        query_agent = agents['query_agent']
        communication = agents['communication']
        
        # Simulate user asking a question
        user_question = "How do I implement a microservices architecture?"
        
        # Mock the LLM response
        with patch.object(query_agent, 'process_query') as mock_query:
            mock_query.return_value = {
                "response": "To implement microservices architecture...",
                "confidence": 0.92,
                "sources": ["microservices_design", "best_practices"]
            }
            
            # Process the query
            result = query_agent.process_query(user_question)
            
            # Verify the result
            assert result is not None
            assert "response" in result
            assert "confidence" in result
            assert result["confidence"] > 0.9
            
            # Verify communication was used
            mock_query.assert_called_once_with(user_question)
    
    def test_complete_design_generation_workflow(self, setup_test_agents):
        """Test complete design generation workflow"""
        agents = setup_test_agents
        designer_agent = agents['designer_agent']
        communication = agents['communication']
        
        # Simulate user requesting a design
        user_requirements = {
            "type": "ecommerce-platform",
            "features": ["product_catalog", "shopping_cart", "payment_processing"],
            "constraints": ["scalability", "security"],
            "timeline": "3_months"
        }
        
        # Mock the design generation
        with patch.object(designer_agent, 'generate_design') as mock_design:
            mock_design.return_value = {
                "architecture": "microservices",
                "components": [
                    "product_service",
                    "cart_service",
                    "payment_service",
                    "user_service",
                    "order_service"
                ],
                "technologies": ["FastAPI", "PostgreSQL", "Redis", "React"],
                "deployment": "Kubernetes",
                "estimated_timeline": "12_weeks"
            }
            
            # Generate the design
            result = designer_agent.generate_design(user_requirements)
            
            # Verify the result
            assert result is not None
            assert "architecture" in result
            assert "components" in result
            assert "technologies" in result
            assert "deployment" in result
            
            # Verify communication was used
            mock_design.assert_called_once_with(user_requirements)
    
    def test_multi_step_user_interaction_workflow(self, setup_test_agents):
        """Test multi-step user interaction workflow"""
        agents = setup_test_agents
        query_agent = agents['query_agent']
        designer_agent = agents['designer_agent']
        communication = agents['communication']
        
        # Mock the LLM manager to avoid actual API calls
        with patch.object(agents['llm_manager'], 'call_provider') as mock_llm:
            mock_llm.return_value = {
                "response": "AI response",
                "usage": {"prompt": 100, "completion": 200}
            }
            
            # Step 1: User asks about microservices
            query_1 = "What are microservices?"
            with patch.object(query_agent, 'process_query') as mock_query:
                mock_query.return_value = {
                    "response": "Microservices are a software architecture...",
                    "confidence": 0.95
                }
                result_1 = query_agent.process_query(query_1)
                assert result_1 is not None
            
            # Step 2: User asks for design based on microservices
            design_request = {
                "architecture": "microservices",
                "requirements": ["modularity", "scalability"]
            }
            with patch.object(designer_agent, 'generate_design') as mock_design:
                mock_design.return_value = {
                    "architecture": "microservices",
                    "components": ["service_a", "service_b"],
                    "technologies": ["Docker", "Kubernetes"]
                }
                result_2 = designer_agent.generate_design(design_request)
                assert result_2 is not None
            
            # Step 3: Follow-up question about implementation
            query_3 = "How do I implement this design?"
            with patch.object(query_agent, 'process_query') as mock_query:
                mock_query.return_value = {
                    "response": "Implementation steps for microservices...",
                    "confidence": 0.93
                }
                result_3 = query_agent.process_query(query_3)
                assert result_3 is not None
            
            # Verify all interactions occurred
            assert mock_llm.call_count >= 3  # Three LLM calls
    
    def test_error_recovery_workflow(self, setup_test_agents):
        """Test error recovery in user workflows"""
        agents = setup_test_agents
        query_agent = agents['query_agent']
        designer_agent = agents['designer_agent']
        
        # Test 1: Invalid query followed by valid query
        invalid_query = ""
        with patch.object(query_agent, 'process_query', side_effect=ValueError("Invalid input")):
            try:
                query_agent.process_query(invalid_query)
            except ValueError as e:
                assert str(e) == "Invalid input"
        
        # Recovery: Valid query
        valid_query = "What is AI?"
        with patch.object(query_agent, 'process_query') as mock_query:
            mock_query.return_value = {
                "response": "AI is artificial intelligence",
                "confidence": 0.95
            }
            result = query_agent.process_query(valid_query)
            assert result is not None
        
        # Test 2: Design generation failure followed by recovery
        invalid_design_request = {}
        with patch.object(designer_agent, 'generate_design', side_effect=ValueError("Missing requirements")):
            try:
                designer_agent.generate_design(invalid_design_request)
            except ValueError as e:
                assert str(e) == "Missing requirements"
        
        # Recovery: Valid design request
        valid_design_request = {"requirements": "Build an app"}
        with patch.object(designer_agent, 'generate_design') as mock_design:
            mock_design.return_value = {
                "architecture": "monolithic",
                "components": ["backend", "frontend"]
            }
            result = designer_agent.generate_design(valid_design_request)
            assert result is not None
    
    def test_workflow_performance(self, setup_test_agents):
        """Test end-to-end workflow performance"""
        import time
        
        agents = setup_test_agents
        query_agent = agents['query_agent']
        designer_agent = agents['designer_agent']
        
        # Mock all external calls
        with patch.object(query_agent, 'process_query') as mock_query:
            mock_query.return_value = {
                "response": "Test response",
                "confidence": 0.95
            }
            
            with patch.object(designer_agent, 'generate_design') as mock_design:
                mock_design.return_value = {
                    "architecture": "microservices",
                    "components": ["service"],
                    "technologies": ["FastAPI"]
                }
                
                # Time the complete workflow
                start_time = time.time()
                
                # Step 1: User query
                result_1 = query_agent.process_query("What is AI?")
                assert result_1 is not None
                
                # Step 2: Design request based on query
                result_2 = designer_agent.generate_design({"requirements": "Build AI app"})
                assert result_2 is not None
                
                # Step 3: Follow-up query
                result_3 = query_agent.process_query("How do I implement this?")
                assert result_3 is not None
                
                end_time = time.time()
                total_time = end_time - start_time
                
                print(f"End-to-End Workflow Performance:")
                print(f"  Total workflow time: {total_time:.4f}s")
                print(f"  Steps: 3")
                print(f"  Average time per step: {total_time/3:.4f}s")
                
                # Performance assertions
                assert total_time < 3.0, f"Total workflow time too high: {total_time}s"
                assert total_time/3 < 1.0, f"Average step time too high: {total_time/3}s"


class TestSecurityWorkflows:
    """Test cases for security-related workflows"""
    
    def test_input_validation_workflow(self, setup_test_agents):
        """Test input validation in workflows"""
        agents = setup_test_agents
        query_agent = agents['query_agent']
        
        # Test various invalid inputs
        invalid_inputs = [
            "",
            None,
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "DROP TABLE users;"
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = query_agent.process_query(invalid_input)
                # If no exception, result should indicate validation failure
                if result:
                    assert "error" in result or result["confidence"] < 0.5
            except Exception as e:
                # Exception should be appropriate
                assert str(e) != ""
    
    def test_output_sanitization_workflow(self, setup_test_agents):
        """Test output sanitization in workflows"""
        agents = setup_test_agents
        query_agent = agents['query_agent']
        
        # Mock response with potentially unsafe content
        with patch.object(query_agent, 'process_query') as mock_query:
            mock_query.return_value = {
                "response": "Response <script>alert('xss')</script>",
                "confidence": 0.95
            }
            
            result = query_agent.process_query("Some query")
            
            # Verify result structure
            assert result is not None
            assert "response" in result
            assert "confidence" in result
    
    def test_access_control_workflow(self, setup_test_agents):
        """Test access control in workflows"""
        agents = setup_test_agents
        designer_agent = agents['designer_agent']
        
        # Test with different permission levels
        restricted_request = {
            "requirements": "Build system",
            "permissions": {"level": "restricted"}
        }
        
        full_access_request = {
            "requirements": "Build system",
            "permissions": {"level": "full"}
        }
        
        with patch.object(designer_agent, 'generate_design') as mock_design:
            # Mock restricted access response
            mock_design.return_value = {
                "architecture": "basic",
                "components": ["base_service"],
                "technologies": ["Basic"]
            }
            
            # Restricted access
            restricted_result = designer_agent.generate_design(restricted_request)
            assert restricted_result is not None
            
            # Full access
            full_result = designer_agent.generate_design(full_access_request)
            assert full_result is not None


if __name__ == "__main__":
    pytest.main([__file__])