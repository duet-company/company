"""
Performance and load testing for the platform.

Tests cover:
- API endpoint performance
- Query generation performance
- Database query performance
- Load testing with concurrent users
- Memory usage testing
- Response time benchmarks
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any


@pytest.fixture
async def performance_client():
    """Create test client for performance tests."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestAPIPerformance:
    """Test API endpoint performance."""

    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self, performance_client):
        """Test health endpoint response time."""
        response_times = []
        
        for _ in range(100):
            start_time = time.time()
            response = await performance_client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        
        # Performance assertions
        assert avg_time < 100, f"Average response time too slow: {avg_time:.2f}ms"
        assert max_time < 500, f"Max response time too slow: {max_time:.2f}ms"
        assert p95_time < 200, f"95th percentile too slow: {p95_time:.2f}ms"
        
        print(f"\nHealth Endpoint Performance:")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        print(f"  95th percentile: {p95_time:.2f}ms")

    @pytest.mark.asyncio
    async def test_query_endpoint_performance(self, performance_client):
        """Test query endpoint response time."""
        with patch('agents.api.agents.QueryAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT * FROM users",
                "optimized_sql": "SELECT name FROM users LIMIT 1000",
                "explanation": "Test query",
                "dialect": "clickhouse",
                "cached": False,
                "execution_time_ms": 150
            })
            mock_agent_class.get_instance = AsyncMock(return_value=mock_agent)
            
            response_times = []
            
            for i in range(50):
                start_time = time.time()
                response = await performance_client.post(
                    "/api/queries",
                    json={
                        "query": f"Show me users {i}",
                        "dialect": "clickhouse"
                    }
                )
                end_time = time.time()
                
                assert response.status_code == 200
                response_times.append((end_time - start_time) * 1000)
            
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            # Query generation should be under 5 seconds
            assert avg_time < 5000, f"Average query time too slow: {avg_time:.2f}ms"
            assert max_time < 10000, f"Max query time too slow: {max_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, performance_client):
        """Test handling of concurrent requests."""
        with patch('agents.api.agents.QueryAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT 1",
                "optimized_sql": "SELECT 1",
                "explanation": "Simple test",
                "dialect": "clickhouse",
                "cached": False
            })
            mock_agent_class.get_instance = AsyncMock(return_value=mock_agent)
            
            async def make_request(client, request_id):
                start_time = time.time()
                response = await client.post(
                    "/api/queries",
                    json={
                        "query": f"Test query {request_id}",
                        "dialect": "clickhouse"
                    }
                )
                end_time = time.time()
                return response.status_code, (end_time - start_time) * 1000
            
            # Make 20 concurrent requests
            tasks = []
            for i in range(20):
                task = make_request(performance_client, i)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            status_codes = [result[0] for result in results]
            response_times = [result[1] for result in results]
            
            assert all(code == 200 for code in status_codes), "Some requests failed"
            
            avg_concurrent_time = statistics.mean(response_times)
            assert avg_concurrent_time < 10000, f"Concurrent requests too slow: {avg_concurrent_time:.2f}ms"


class TestQueryGenerationPerformance:
    """Test query generation performance."""

    @pytest.mark.asyncio
    async def test_simple_query_performance(self):
        """Test simple query generation performance."""
        from agents.query_agent import QueryAgent
        from agents.config import AgentConfig, LLMProviderConfig
        
        config = AgentConfig(
            agent_id="perf-test-agent",
            name="Performance Test Agent",
            llm_provider=LLMProviderConfig(
                provider="claude",
                model="claude-3-5-sonnet-20241022",
                api_key="test-key"
            )
        )
        
        agent = QueryAgent(config)
        
        # Mock LLM response
        with patch.object(agent, '_generate_sql') as mock_generate:
            mock_generate.return_value = "SELECT name FROM users"
            
            # Test multiple query generations
            times = []
            for i in range(10):
                start_time = time.time()
                result = await agent.process(f"Show me users {i}")
                end_time = time.time()
                
                times.append((end_time - start_time) * 1000)
            
            avg_time = statistics.mean(times)
            assert avg_time < 1000, f"Simple query generation too slow: {avg_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_complex_query_performance(self):
        """Test complex query generation performance."""
        from agents.query_agent import QueryAgent
        from agents.config import AgentConfig, LLMProviderConfig
        
        config = AgentConfig(
            agent_id="perf-test-agent-complex",
            name="Complex Performance Test Agent",
            llm_provider=LLMProviderConfig(
                provider="claude",
                model="claude-3-5-sonnet-20241022",
                api_key="test-key"
            )
        )
        
        agent = QueryAgent(config)
        
        complex_query = """
        Show me total sales by product category for the last 30 days, 
        excluding cancelled orders, with year-over-year comparison
        """
        
        with patch.object(agent, '_generate_sql') as mock_generate:
            mock_generate.return_value = """
            SELECT 
                p.category,
                SUM(s.total) as current_sales,
                SUM(CASE WHEN s.date >= today() - 365 THEN s.total ELSE 0 END) as prev_year_sales
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.date >= today() - 30
            AND s.status != 'cancelled'
            GROUP BY p.category
            ORDER BY current_sales DESC
            """
            
            start_time = time.time()
            result = await agent.process(complex_query)
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000
            assert processing_time < 5000, f"Complex query too slow: {processing_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test query cache performance improvement."""
        from agents.query_agent import QueryAgent, QueryCache
        from agents.config import AgentConfig, LLMProviderConfig
        
        config = AgentConfig(
            agent_id="cache-perf-agent",
            name="Cache Performance Agent",
            llm_provider=LLMProviderConfig(
                provider="claude",
                model="claude-3-5-sonnet-20241022",
                api_key="test-key"
            )
        )
        
        agent = QueryAgent(config)
        agent.cache = QueryCache(ttl_minutes=30, max_size=100)
        
        # Mock LLM response
        call_count = 0
        async def mock_generate(sql_request):
            nonlocal call_count
            call_count += 1
            return "SELECT name FROM users"
        
        with patch.object(agent, '_generate_sql', side_effect=mock_generate):
            # First call - should hit LLM
            start_time = time.time()
            result1 = await agent.process("Show me users")
            first_call_time = (time.time() - start_time) * 1000
            
            # Second call - should hit cache
            start_time = time.time()
            result2 = await agent.process("Show me users")
            second_call_time = (time.time() - start_time) * 1000
            
            # Cache should be faster
            assert second_call_time < first_call_time, "Cache should be faster than LLM call"
            assert result2["cached"] is True
            assert call_count == 1  # LLM called only once


class TestLoadTesting:
    """Load testing with simulated user traffic."""

    @pytest.mark.asyncio
    async def test_sustained_load(self, performance_client):
        """Test sustained load over time."""
        with patch('agents.api.agents.QueryAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT 1",
                "optimized_sql": "SELECT 1",
                "explanation": "Test",
                "dialect": "clickhouse",
                "cached": False
            })
            mock_agent_class.get_instance = AsyncMock(return_value=mock_agent)
            
            # Simulate 5 minutes of sustained load
            # (scaled down for testing - 30 seconds)
            duration_seconds = 30
            requests_per_second = 5
            total_requests = duration_seconds * requests_per_second
            
            async def sustained_request(client, request_id):
                try:
                    response = await client.post(
                        "/api/queries",
                        json={
                            "query": f"Sustained test {request_id}",
                            "dialect": "clickhouse"
                        }
                    )
                    return response.status_code
                except Exception:
                    return 500
            
            start_time = time.time()
            tasks = []
            
            for i in range(total_requests):
                task = sustained_request(performance_client, i)
                tasks.append(task)
                
                # Throttle requests
                if i % requests_per_second == 0:
                    await asyncio.sleep(1)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Calculate success rate
            successful_requests = sum(1 for result in results 
                                   if isinstance(result, int) and result == 200)
            success_rate = successful_requests / len(results)
            
            # Should maintain high success rate under load
            assert success_rate > 0.95, f"Success rate too low under load: {success_rate:.2%}"
            
            actual_duration = end_time - start_time
            print(f"\nLoad Test Results:")
            print(f"  Duration: {actual_duration:.2f}s")
            print(f"  Total requests: {len(results)}")
            print(f"  Success rate: {success_rate:.2%}")
            print(f"  Requests/second: {len(results)/actual_duration:.2f}")

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_client):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('agents.api.agents.QueryAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.process = AsyncMock(return_value={
                "generated_sql": "SELECT 1",
                "optimized_sql": "SELECT 1", 
                "explanation": "Test",
                "dialect": "clickhouse",
                "cached": False
            })
            mock_agent_class.get_instance = AsyncMock(return_value=mock_agent)
            
            # Make many requests
            for i in range(100):
                await performance_client.post(
                    "/api/queries",
                    json={
                        "query": f"Memory test {i}",
                        "dialect": "clickhouse"
                    }
                )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory shouldn't increase by more than 100MB
            assert memory_increase < 100, f"Memory leak detected: {memory_increase:.2f}MB increase"
            
            print(f"\nMemory Usage:")
            print(f"  Initial: {initial_memory:.2f}MB")
            print(f"  Final: {final_memory:.2f}MB")
            print(f"  Increase: {memory_increase:.2f}MB")


class TestDatabasePerformance:
    """Test database query performance."""

    def test_query_optimization_impact(self):
        """Test impact of query optimization."""
        from agents.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer("clickhouse")
        
        # Test unoptimized vs optimized queries
        unoptimized_queries = [
            "SELECT   name,    amount   FROM   orders",
            "SELECT * FROM users",
            "SELECT COUNT(*) FROM large_table"
        ]
        
        for query in unoptimized_queries:
            optimized, notes = optimizer.optimize(query)
            
            # Optimized query should be different (better)
            assert optimized != query or len(notes) > 0, f"Query not optimized: {query}"
            
            # Should have optimization notes
            assert isinstance(notes, list), "Optimization should return notes"

    def test_clickhouse_specific_optimizations(self):
        """Test ClickHouse-specific optimizations."""
        from agents.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer("clickhouse")
        
        # Test SAMPLE optimization for COUNT queries
        count_query = "SELECT COUNT(*) FROM orders"
        optimized, notes = optimizer.optimize(count_query)
        
        assert "SAMPLE" in optimized, "ClickHouse COUNT should use SAMPLE"
        assert any("SAMPLE" in note for note in notes), "Should mention SAMPLE optimization"

    def test_postgresql_specific_optimizations(self):
        """Test PostgreSQL-specific optimizations."""
        from agents.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer("postgresql")
        
        # Test function conversion
        query_with_todate = "SELECT toDate(created_at) FROM orders"
        optimized, notes = optimizer.optimize(query_with_todate)
        
        assert "DATE(" in optimized, "PostgreSQL should convert toDate to DATE"
        assert any("DATE" in note for note in notes), "Should mention DATE conversion"


class TestAgentPerformance:
    """Test AI agent performance metrics."""

    @pytest.mark.asyncio
    async def test_agent_initialization_time(self):
        """Test agent initialization performance."""
        from agents.base import BaseAgent
        from agents.config import AgentConfig, AgentType
        
        class FastTestAgent(BaseAgent):
            async def initialize(self):
                self.set_status(AgentStatus.READY)
            
            async def process(self, input_data, metadata=None):
                return "processed"
            
            async def shutdown(self):
                self.set_status(AgentStatus.SHUTDOWN)
        
        config = AgentConfig(
            agent_id="init-perf-agent",
            name="Init Performance Agent",
            agent_type=AgentType.CUSTOM
        )
        
        agent = FastTestAgent(config)
        
        start_time = time.time()
        await agent.initialize()
        init_time = (time.time() - start_time) * 1000
        
        assert init_time < 1000, f"Agent initialization too slow: {init_time:.2f}ms"
        assert agent.status == AgentStatus.READY

    @pytest.mark.asyncio
    async def test_agent_health_check_performance(self):
        """Test agent health check performance."""
        from agents.query_agent import QueryAgent
        from agents.config import AgentConfig, LLMProviderConfig
        
        config = AgentConfig(
            agent_id="health-perf-agent",
            name="Health Performance Agent",
            llm_provider=LLMProviderConfig(
                provider="claude",
                model="claude-3-5-sonnet-20241022",
                api_key="test-key"
            )
        )
        
        agent = QueryAgent(config)
        agent.status = AgentStatus.READY
        
        # Mock health check data
        agent.cache = Mock()
        agent.cache.get_stats = Mock(return_value={"size": 10, "hits": 50, "misses": 20})
        
        start_time = time.time()
        health = await agent.health_check()
        health_time = (time.time() - start_time) * 1000
        
        assert health_time < 500, f"Health check too slow: {health_time:.2f}ms"
        assert "agent_id" in health
        assert "status" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print statements