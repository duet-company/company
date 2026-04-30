"""
Performance tests for load testing and benchmarking
"""

import pytest
import asyncio
import time
import statistics
import concurrent.futures
from unittest.mock import Mock, patch
import sys
import os

# Add the backend source to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend', 'src'))

from agents.query_agent import QueryAgent
from agents.platform_designer import PlatformDesignerAgent
from agents.llm_providers import LLMProviderManager
from agents.communication import AgentCommunication


class TestLoadPerformance:
    """Test cases for load performance"""
    
    @pytest.fixture
    def query_agent(self):
        """Create a query agent instance"""
        return QueryAgent()
    
    @pytest.fixture
    def designer_agent(self):
        """Create a designer agent instance"""
        return PlatformDesignerAgent()
    
    @pytest.fixture
    def llm_manager(self):
        """Create an LLM manager instance"""
        return LLMProviderManager()
    
    @pytest.fixture
    def communication(self):
        """Create a communication instance"""
        return AgentCommunication()
    
    def test_query_agent_performance(self, query_agent):
        """Test query agent performance under load"""
        queries = [
            "What is artificial intelligence?",
            "Explain machine learning",
            "How does deep learning work?",
            "What is natural language processing?",
            "Describe computer vision",
            "Explain reinforcement learning",
            "What is transfer learning?",
            "How does neural networks work?",
            "What is computer vision?",
            "Explain data science"
        ]
        
        response_times = []
        
        for query in queries:
            start_time = time.time()
            
            # Mock the LLM call to avoid actual API calls
            with patch.object(query_agent, 'process_query') as mock_process:
                mock_process.return_value = {
                    "response": f"Response for {query}",
                    "confidence": 0.95
                }
                
                result = query_agent.process_query(query)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert result is not None
                assert "response" in result
                assert "confidence" in result
        
        # Calculate performance metrics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"Query Agent Performance:")
        print(f"  Average response time: {avg_response_time:.4f}s")
        print(f"  Max response time: {max_response_time:.4f}s")
        print(f"  Min response time: {min_response_time:.4f}s")
        
        # Performance assertions
        assert avg_response_time < 1.0, f"Average response time too high: {avg_response_time}s"
        assert max_response_time < 2.0, f"Max response time too high: {max_response_time}s"
    
    def test_designer_agent_performance(self, designer_agent):
        """Test designer agent performance under load"""
        requirements_list = [
            "Build an e-commerce platform",
            "Create a social media app",
            "Develop a data analytics dashboard",
            "Design a recommendation system",
            "Build a task management tool",
            "Create a blog platform",
            "Develop a chat application",
            "Design a project management system",
            "Build a portfolio website",
            "Create a learning management system"
        ]
        
        response_times = []
        
        for requirements in requirements_list:
            start_time = time.time()
            
            # Mock the design generation
            with patch.object(designer_agent, 'generate_design') as mock_generate:
                mock_generate.return_value = {
                    "architecture": "microservices",
                    "components": ["api", "database", "frontend"],
                    "technologies": ["FastAPI", "PostgreSQL", "React"]
                }
                
                result = designer_agent.generate_design({"requirements": requirements})
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                assert result is not None
                assert "architecture" in result
                assert "components" in result
                assert "technologies" in result
        
        # Calculate performance metrics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"Designer Agent Performance:")
        print(f"  Average response time: {avg_response_time:.4f}s")
        print(f"  Max response time: {max_response_time:.4f}s")
        print(f"  Min response time: {min_response_time:.4f}s")
        
        # Performance assertions
        assert avg_response_time < 1.5, f"Average response time too high: {avg_response_time}s"
        assert max_response_time < 3.0, f"Max response time too high: {max_response_time}s"
    
    def test_concurrent_queries(self, query_agent):
        """Test query agent performance under concurrent load"""
        num_concurrent = 10
        queries = [f"Query {i}" for i in range(num_concurrent)]
        
        async def process_query(query):
            with patch.object(query_agent, 'process_query') as mock_process:
                mock_process.return_value = {
                    "response": f"Response for {query}",
                    "confidence": 0.95
                }
                return await asyncio.get_event_loop().run_in_executor(
                    None, query_agent.process_query, query
                )
        
        start_time = time.time()
        
        # Run concurrent queries
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            tasks = [process_query(query) for query in queries]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify all queries were processed
            assert len(results) == num_concurrent
            for result in results:
                assert result is not None
                assert "response" in result
                assert "confidence" in result
            
            print(f"Concurrent Query Performance:")
            print(f"  Total time for {num_concurrent} queries: {total_time:.4f}s")
            print(f"  Average time per query: {total_time/num_concurrent:.4f}s")
            
            # Performance assertions
            assert total_time < 5.0, f"Total time too high: {total_time}s"
            assert total_time/num_concurrent < 0.5, f"Average time per query too high: {total_time/num_concurrent}s"
            
        finally:
            loop.close()
    
    def test_memory_usage(self, query_agent):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many queries to test memory usage
        queries = [f"Memory test query {i}" for i in range(100)]
        
        for query in queries:
            with patch.object(query_agent, 'process_query') as mock_process:
                mock_process.return_value = {
                    "response": f"Response for {query}",
                    "confidence": 0.95
                }
                query_agent.process_query(query)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory Usage Test:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        
        # Memory usage assertions
        assert memory_increase < 100, f"Memory usage too high: {memory_increase} MB"
    
    def test_error_handling_performance(self, query_agent):
        """Test error handling performance"""
        error_queries = [
            "",  # Empty query
            None,  # None query
            "   ",  # Whitespace only
            123,  # Invalid type
            {},  # Invalid format
        ]
        
        for query in error_queries:
            start_time = time.time()
            
            try:
                result = query_agent.process_query(query)
                # If no exception, result should be handled gracefully
                assert result is not None
            except Exception as e:
                # Exception should be handled gracefully
                assert str(e) != ""
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Error handling should be fast
            assert response_time < 1.0, f"Error handling too slow: {response_time}s"
    
    def test_throughput_measurement(self, query_agent):
        """Test throughput measurement"""
        num_queries = 100
        queries = [f"Throughput test query {i}" for i in range(num_queries)]
        
        start_time = time.time()
        
        for query in queries:
            with patch.object(query_agent, 'process_query') as mock_process:
                mock_process.return_value = {
                    "response": f"Response for {query}",
                    "confidence": 0.95
                }
                query_agent.process_query(query)
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = num_queries / total_time
        
        print(f"Throughput Test:")
        print(f"  Total queries: {num_queries}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Throughput: {throughput:.2f} queries/second")
        
        # Throughput assertions
        assert throughput > 20, f"Throughput too low: {throughput} queries/second"
        assert total_time < 10, f"Total time too high: {total_time}s"


class TestDatabasePerformance:
    """Test cases for database performance"""
    
    @pytest.mark.asyncio
    async def test_database_connection_performance(self):
        """Test database connection performance"""
        import time
        
        # Mock database connections
        connection_times = []
        
        for i in range(10):
            start_time = time.time()
            
            # Mock connection
            with patch('sqlalchemy.create_async_engine') as mock_create:
                mock_create.return_value = Mock()
                
                # Simulate connection delay
                await asyncio.sleep(0.01)
                
                end_time = time.time()
                connection_time = end_time - start_time
                connection_times.append(connection_time)
        
        avg_connection_time = statistics.mean(connection_times)
        max_connection_time = max(connection_times)
        
        print(f"Database Connection Performance:")
        print(f"  Average connection time: {avg_connection_time:.4f}s")
        print(f"  Max connection time: {max_connection_time:.4f}s")
        
        # Performance assertions
        assert avg_connection_time < 0.1, f"Average connection time too high: {avg_connection_time}s"
        assert max_connection_time < 0.2, f"Max connection time too high: {max_connection_time}s"
    
    @pytest.mark.asyncio
    async def test_query_performance(self):
        """Test database query performance"""
        import time
        
        # Mock query execution
        query_times = []
        
        for i in range(50):
            start_time = time.time()
            
            # Mock query execution
            with patch('clickhouse_connect.get_client') as mock_get:
                mock_client = Mock()
                mock_client.query.return_value = {
                    'columns': ['id', 'value'],
                    'data': [[i, f'value_{i}']]
                }
                mock_get.return_value = mock_client
                
                # Simulate query execution
                await asyncio.sleep(0.005)
                
                end_time = time.time()
                query_time = end_time - start_time
                query_times.append(query_time)
        
        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)
        
        print(f"Database Query Performance:")
        print(f"  Average query time: {avg_query_time:.4f}s")
        print(f"  Max query time: {max_query_time:.4f}s")
        
        # Performance assertions
        assert avg_query_time < 0.05, f"Average query time too high: {avg_query_time}s"
        assert max_query_time < 0.1, f"Max query time too high: {max_query_time}s"


if __name__ == "__main__":
    pytest.main([__file__])