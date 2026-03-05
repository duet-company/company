"""
Unit tests for Query Agent.

Tests cover:
- SQL generation from natural language
- SQL validation and safety
- Query optimization
- Result caching
- Multi-dialect support
- Query explanations
- Performance metrics
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from .query_agent import (
    QueryAgent,
    SQLDialect,
    QueryCache,
    QueryValidator,
    QueryOptimizer,
    QueryExplainer,
    QueryMetrics,
)
from .config import AgentConfig, AgentType, AgentCapability, LLMProviderConfig
from .base import AgentStatus


class TestQueryCache:
    """Test QueryCache functionality."""

    @pytest.fixture
    def cache(self):
        """Create a test cache instance."""
        return QueryCache(ttl_minutes=1, max_size=10)

    def test_cache_set_get(self, cache):
        """Test setting and getting cached results."""
        query = "Show me sales data"
        result = {"sql": "SELECT * FROM sales"}

        cache.set(query, SQLDialect.CLICKHOUSE, result)
        cached = cache.get(query, SQLDialect.CLICKHOUSE)

        assert cached == result

    def test_cache_miss(self, cache):
        """Test cache miss for non-existent query."""
        cached = cache.get("Non-existent query", SQLDialect.CLICKHOUSE)
        assert cached is None

    def test_cache_expiration(self, cache):
        """Test cache entry expiration after TTL."""
        query = "Test query"
        result = {"sql": "SELECT 1"}

        # Set cache entry
        cache._ttl = timedelta(milliseconds=10)
        cache.set(query, SQLDialect.CLICKHOUSE, result)

        # Wait for expiration
        import time
        time.sleep(0.1)

        # Should be expired
        cached = cache.get(query, SQLDialect.CLICKHOUSE)
        assert cached is None

    def test_cache_eviction(self, cache):
        """Test cache eviction when at capacity."""
        cache = QueryCache(ttl_minutes=10, max_size=2)

        # Fill cache to capacity
        for i in range(3):
            cache.set(f"Query {i}", SQLDialect.CLICKHOUSE, {"sql": f"SELECT {i}"})

        # Oldest entry should be evicted
        assert cache.get("Query 0", SQLDialect.CLICKHOUSE) is None
        assert cache.get("Query 1", SQLDialect.CLICKHOUSE) is not None
        assert cache.get("Query 2", SQLDialect.CLICKHOUSE) is not None

    def test_cache_clear(self, cache):
        """Test clearing all cache entries."""
        for i in range(5):
            cache.set(f"Query {i}", SQLDialect.CLICKHOUSE, {"sql": f"SELECT {i}"})

        cache.clear()

        assert cache.get_stats()["size"] == 0

    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.set("Query 1", SQLDialect.CLICKHOUSE, {"sql": "SELECT 1"})

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["ttl_minutes"] == 1


class TestQueryValidator:
    """Test QueryValidator functionality."""

    @pytest.fixture
    def validator_clickhouse(self):
        """Create validator for ClickHouse."""
        return QueryValidator(SQLDialect.CLICKHOUSE)

    @pytest.fixture
    def validator_postgresql(self):
        """Create validator for PostgreSQL."""
        return QueryValidator(SQLDialect.POSTGRESQL)

    def test_valid_select_query(self, validator_clickhouse):
        """Test validation of valid SELECT query."""
        sql = "SELECT name, amount FROM orders WHERE created_at >= '2026-01-01'"

        is_valid, error = validator_clickhouse.validate(sql)

        assert is_valid
        assert error is None

    def test_sql_injection_detection(self, validator_clickhouse):
        """Test SQL injection pattern detection."""
        # Various SQL injection patterns
        injection_queries = [
            "SELECT * FROM users; DROP TABLE users",
            "SELECT * FROM users -- DROP TABLE users",
            "SELECT * FROM users /* DROP TABLE users */",
            "SELECT * FROM users UNION ALL SELECT * FROM passwords",
            "SELECT * FROM users WHERE 1 = 1",
            "SELECT * FROM users WHERE 1=1",
        ]

        for query in injection_queries:
            is_valid, error = validator_clickhouse.validate(query)
            assert not is_valid
            assert "SQL injection" in error.lower()

    def test_non_select_query_rejected(self, validator_clickhouse):
        """Test rejection of non-SELECT queries."""
        non_select_queries = [
            "DROP TABLE users",
            "DELETE FROM users WHERE id = 1",
            "UPDATE users SET name = 'test'",
            "INSERT INTO users VALUES (1, 'test')",
            "CREATE TABLE test (id INT)",
        ]

        for query in non_select_queries:
            is_valid, error = validator_clickhouse.validate(query)
            assert not is_valid
            assert "Only SELECT" in error

    def test_empty_query_rejected(self, validator_clickhouse):
        """Test rejection of empty query."""
        is_valid, error = validator_clickhouse.validate("")
        assert not is_valid
        assert "Empty" in error

    def test_unbalanced_parentheses(self, validator_clickhouse):
        """Test detection of unbalanced parentheses."""
        unbalanced_queries = [
            "SELECT * FROM users WHERE (id = 1",
            "SELECT * FROM users WHERE id = 1))",
            "SELECT COUNT(*) FROM (SELECT * FROM users",
        ]

        for query in unbalanced_queries:
            is_valid, error = validator_clickhouse.validate(query)
            assert not is_valid
            assert "parentheses" in error.lower()

    def test_schema_validation_valid(self, validator_clickhouse):
        """Test valid schema validation."""
        sql = "SELECT name FROM orders"
        schema = {
            "tables": {
                "orders": {"columns": ["id", "name", "amount"]}
            }
        }

        is_valid, error = validator_clickhouse.validate(sql, schema)

        assert is_valid
        assert error is None

    def test_schema_validation_invalid_table(self, validator_clickhouse):
        """Test invalid table in schema validation."""
        sql = "SELECT name FROM non_existent_table"
        schema = {
            "tables": {
                "orders": {"columns": ["id", "name", "amount"]}
            }
        }

        is_valid, error = validator_clickhouse.validate(sql, schema)

        assert not is_valid
        assert "not found in schema" in error


class TestQueryOptimizer:
    """Test QueryOptimizer functionality."""

    @pytest.fixture
    def optimizer_clickhouse(self):
        """Create optimizer for ClickHouse."""
        return QueryOptimizer(SQLDialect.CLICKHOUSE)

    @pytest.fixture
    def optimizer_postgresql(self):
        """Create optimizer for PostgreSQL."""
        return QueryOptimizer(SQLDialect.POSTGRESQL)

    def test_whitespace_optimization(self, optimizer_clickhouse):
        """Test removal of excess whitespace."""
        sql = "SELECT   name    ,    amount   FROM    orders"
        optimized, notes = optimizer_clickhouse.optimize(sql)

        assert "SELECT   name    ,    amount" not in optimized
        assert optimized == "SELECT name, amount FROM orders"

    def test_limit_addition(self, optimizer_clickhouse):
        """Test automatic LIMIT addition."""
        sql = "SELECT name FROM orders"
        optimized, notes = optimizer_clickhouse.optimize(sql)

        assert "LIMIT 1000" in optimized
        assert any("LIMIT" in note for note in notes)

    def test_no_limit_for_aggregate_queries(self, optimizer_clickhouse):
        """Test no LIMIT added for aggregate queries."""
        sql = "SELECT COUNT(*) FROM orders"
        optimized, notes = optimizer_clickhouse.optimize(sql)

        # Should not add LIMIT for COUNT queries
        assert "LIMIT" not in optimized or "COUNT" not in optimized

    def test_clickhouse_specific_optimizations(self, optimizer_clickhouse):
        """Test ClickHouse-specific optimizations."""
        sql = "SELECT COUNT(*) FROM orders"
        optimized, notes = optimizer_clickhouse.optimize(sql)

        # Should add SAMPLE for COUNT queries
        assert "SAMPLE" in optimized
        assert any("SAMPLE" in note for note in notes)

    def test_postgresql_specific_optimizations(self, optimizer_postgresql):
        """Test PostgreSQL-specific optimizations."""
        sql = "SELECT toDate(created_at) AS date FROM orders"
        optimized, notes = optimizer_postgresql.optimize(sql)

        # Should convert toDate to DATE
        assert "toDate(" not in optimized
        assert "DATE(" in optimized
        assert any("DATE" in note for note in notes)

    def test_get_optimization_hints(self, optimizer_clickhouse):
        """Test getting optimization hints."""
        hints = optimizer_clickhouse.get_optimization_hints()

        assert isinstance(hints, list)
        assert len(hints) > 0
        assert any("SAMPLE" in hint for hint in hints)


class TestQueryExplainer:
    """Test QueryExplainer functionality."""

    @pytest.fixture
    def explainer(self):
        """Create explainer instance."""
        return QueryExplainer()

    def test_simple_query_type_detection(self, explainer):
        """Test detection of simple query type."""
        sql = "SELECT name, amount FROM orders"
        explanation = explainer.explain(sql)

        assert explanation["query_type"] == "simple_query"

    def test_join_query_type_detection(self, explainer):
        """Test detection of JOIN query type."""
        sql = "SELECT o.name, u.email FROM orders o JOIN users u ON o.user_id = u.id"
        explanation = explainer.explain(sql)

        assert explanation["query_type"] == "join_query"

    def test_aggregate_query_type_detection(self, explainer):
        """Test detection of aggregate query type."""
        sql = "SELECT COUNT(*), SUM(amount) FROM orders GROUP BY category"
        explanation = explainer.explain(sql)

        assert explanation["query_type"] == "aggregate_query"

    def test_table_extraction(self, explainer):
        """Test extraction of table names."""
        sql = "SELECT o.name, u.email FROM orders o JOIN users u ON o.user_id = u.id"
        explanation = explainer.explain(sql)

        tables = explanation["tables_accessed"]
        assert "orders" in tables
        assert "users" in tables

    def test_column_extraction(self, explainer):
        """Test extraction of column names."""
        sql = "SELECT name, amount, COUNT(*) FROM orders"
        explanation = explainer.explain(sql)

        columns = explanation["columns_used"]
        assert "name" in columns
        assert "amount" in columns

    def test_operation_extraction(self, explainer):
        """Test extraction of SQL operations."""
        sql = "SELECT COUNT(*), SUM(amount) FROM orders WHERE date >= '2026-01-01' GROUP BY category ORDER BY total DESC LIMIT 10"
        explanation = explainer.explain(sql)

        operations = explanation["operations"]
        assert any("COUNT" in op for op in operations)
        assert any("SUM" in op for op in operations)
        assert any("WHERE" in op for op in operations)
        assert any("GROUP BY" in op for op in operations)
        assert any("ORDER BY" in op for op in operations)
        assert any("LIMIT" in op for op in operations)

    def test_complexity_estimation_low(self, explainer):
        """Test estimation of low complexity."""
        sql = "SELECT name FROM orders LIMIT 10"
        explanation = explainer.explain(sql)

        assert explanation["estimated_complexity"] == "low"

    def test_complexity_estimation_high(self, explainer):
        """Test estimation of high complexity."""
        sql = """
        SELECT o.name, u.email, COUNT(*) as cnt
        FROM orders o
        JOIN users u ON o.user_id = u.id
        GROUP BY o.name, u.email
        HAVING COUNT(*) > 5
        ORDER BY cnt DESC
        LIMIT 10
        """
        explanation = explainer.explain(sql)

        assert explanation["estimated_complexity"] == "high"

    def test_suggestion_generation(self, explainer):
        """Test generation of optimization suggestions."""
        sql = "SELECT * FROM orders"
        explanation = explainer.explain(sql)

        suggestions = explanation["suggestions"]
        assert any("SELECT *" in suggestion for suggestion in suggestions)
        assert any("LIMIT" in suggestion for suggestion in suggestions)


class TestQueryMetrics:
    """Test QueryMetrics functionality."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        return QueryMetrics()

    def test_record_query_success(self, metrics):
        """Test recording successful query."""
        metrics.record_query(100.0, True)

        assert metrics.query_count == 1
        assert metrics.success_count == 1
        assert metrics.error_count == 0
        assert metrics.total_latency_ms == 100.0

    def test_record_query_error(self, metrics):
        """Test recording failed query."""
        metrics.record_query(100.0, False)

        assert metrics.query_count == 1
        assert metrics.success_count == 0
        assert metrics.error_count == 1

    def test_record_cached_query(self, metrics):
        """Test recording cached query."""
        metrics.record_query(10.0, True, cached=True)

        assert metrics.cache_hits == 1
        assert metrics.cache_misses == 0

    def test_record_stage_timing(self, metrics):
        """Test recording stage timing."""
        metrics.record_query(100.0, True)
        metrics.record_stage("sql_generation", 50.0)
        metrics.record_stage("validation", 20.0)
        metrics.record_stage("optimization", 10.0)

        assert metrics.sql_generation_time_ms == 50.0
        assert metrics.validation_time_ms == 20.0
        assert metrics.optimization_time_ms == 10.0

    def test_get_summary(self, metrics):
        """Test metrics summary."""
        for i in range(10):
            metrics.record_query(100.0, i < 9)  # 9 success, 1 error

        summary = metrics.get_summary()

        assert summary["total_queries"] == 10
        assert summary["successful_queries"] == 9
        assert summary["failed_queries"] == 1
        assert summary["success_rate"] == 90.0
        assert summary["average_latency_ms"] == 100.0


class TestQueryAgent:
    """Test QueryAgent main functionality."""

    @pytest.fixture
    def config(self):
        """Create agent configuration."""
        llm_config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            temperature=0.3,
            max_tokens=4096,
        )

        return AgentConfig(
            agent_id="query-agent-test",
            name="Query Agent Test",
            version="1.0.0",
            agent_type=AgentType.QUERY,
            capabilities=[AgentCapability.QUERY],
            llm_provider=llm_config,
            metadata={
                "default_dialect": "clickhouse",
                "cache_ttl_minutes": 30,
                "cache_max_size": 100,
            },
        )

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response."""
        return Mock(
            content="SELECT name, SUM(amount) as total\nFROM orders\nWHERE created_at >= now() - INTERVAL 6 MONTH\nGROUP BY name\nORDER BY total DESC\nLIMIT 10"
        )

    @pytest.mark.asyncio
    async def test_initialization(self, config):
        """Test agent initialization."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=Mock(content="test"))
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            assert agent.status == AgentStatus.READY
            assert agent.llm_provider is not None
            assert agent.cache is not None
            assert agent.validator is not None
            assert agent.optimizer is not None

    @pytest.mark.asyncio
    async def test_process_string_query(self, config, mock_llm_response):
        """Test processing string query."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            result = await agent.process("Show me top 10 products by sales")

            assert "generated_sql" in result
            assert "optimized_sql" in result
            assert "explanation" in result
            assert result["dialect"] == "clickhouse"
            assert not result["cached"]

    @pytest.mark.asyncio
    async def test_process_dict_query(self, config, mock_llm_response):
        """Test processing dict query with dialect."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            result = await agent.process({
                "query": "Show me revenue trends",
                "dialect": "postgresql"
            })

            assert result["dialect"] == "postgresql"

    @pytest.mark.asyncio
    async def test_caching(self, config, mock_llm_response):
        """Test query result caching."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            query = "Show me top products"

            # First call - should hit LLM
            result1 = await agent.process(query)
            assert not result1["cached"]

            # Second call - should hit cache
            result2 = await agent.process(query)
            assert result2["cached"]

            # LLM should only be called once
            mock_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_validation_error(self, config):
        """Test SQL validation error."""
        # Mock LLM to return malicious SQL
        mock_response = Mock(content="SELECT * FROM users; DROP TABLE users")

        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            with pytest.raises(Exception) as exc_info:
                await agent.process("Test query")

            assert "SQL validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check(self, config, mock_llm_response):
        """Test health check."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            health = await agent.health_check()

            assert health["agent_id"] == "query-agent-test"
            assert health["status"] == "ready"
            assert "cache_stats" in health
            assert "metrics_summary" in health

    @pytest.mark.asyncio
    async def test_shutdown(self, config, mock_llm_response):
        """Test agent shutdown."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_provider.shutdown = AsyncMock()
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            await agent.initialize()

            await agent.shutdown()

            assert agent.status == AgentStatus.SHUTDOWN
            mock_provider.shutdown.assert_called_once()

    def test_get_optimization_hints(self, config):
        """Test getting optimization hints."""
        agent = QueryAgent(config)

        hints_clickhouse = agent.get_optimization_hints("clickhouse")
        hints_postgresql = agent.get_optimization_hints("postgresql")

        assert isinstance(hints_clickhouse, list)
        assert isinstance(hints_postgresql, list)
        assert len(hints_clickhouse) > 0
        assert len(hints_postgresql) > 0

    def test_clear_cache(self, config, mock_llm_response):
        """Test clearing cache."""
        with patch('agents.query_agent.create_llm_provider') as mock_create:
            mock_provider = AsyncMock()
            mock_provider.initialize = AsyncMock()
            mock_provider.generate = AsyncMock(return_value=mock_llm_response)
            mock_create.return_value = mock_provider

            agent = QueryAgent(config)
            agent.cache = QueryCache(ttl_minutes=30, max_size=10)

            # Add some entries
            for i in range(5):
                agent.cache.set(f"Query {i}", SQLDialect.CLICKHOUSE, {"sql": f"SELECT {i}"})

            # Clear cache
            result = agent.clear_cache()

            assert result["status"] == "cleared"
            assert result["cache_stats"]["size"] == 0


class TestMultiDialectSupport:
    """Test multi-dialect SQL support."""

    @pytest.fixture
    def config(self):
        """Create agent configuration."""
        llm_config = LLMProviderConfig(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )

        return AgentConfig(
            agent_id="query-agent-test",
            name="Query Agent Test",
            agent_type=AgentType.QUERY,
            capabilities=[AgentCapability.QUERY],
            llm_provider=llm_config,
            metadata={"default_dialect": "clickhouse"},
        )

    def test_clickhouse_dialect(self, config):
        """Test ClickHouse dialect."""
        optimizer = QueryOptimizer(SQLDialect.CLICKHOUSE)
        sql = "SELECT COUNT(*) FROM orders"
        optimized, notes = optimizer.optimize(sql)

        assert "SAMPLE" in optimized

    def test_postgresql_dialect(self, config):
        """Test PostgreSQL dialect."""
        optimizer = QueryOptimizer(SQLDialect.POSTGRESQL)
        sql = "SELECT toDate(created_at) FROM orders"
        optimized, notes = optimizer.optimize(sql)

        assert "DATE(" in optimized
        assert "toDate(" not in optimized

    def test_mysql_dialect(self, config):
        """Test MySQL dialect."""
        optimizer = QueryOptimizer(SQLDialect.MYSQL)
        sql = "SELECT * FROM orders"
        optimized, notes = optimizer.optimize(sql)

        # Should add LIMIT
        assert "LIMIT" in optimized

    def test_sqlite_dialect(self, config):
        """Test SQLite dialect."""
        validator = QueryValidator(SQLDialect.SQLITE)
        sql = "SELECT name FROM users"
        is_valid, error = validator.validate(sql)

        assert is_valid
        assert error is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
