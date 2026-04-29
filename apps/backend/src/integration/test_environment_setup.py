"""
Test environment setup with sample data.

This module sets up a complete test environment with:
- Sample database schema
- Test data fixtures
- Mock LLM responses
- Test configuration
"""

import pytest
import asyncio
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


@pytest.fixture(scope="session")
def test_environment_config():
    """Session-wide test environment configuration."""
    return {
        "database": {
            "host": "localhost",
            "port": 9000,
            "database": "test_duet_company",
            "user": "test_user",
            "password": "test_password"
        },
        "llm_providers": {
            "claude": {
                "api_key": os.getenv("TEST_ANTHROPIC_API_KEY", "test-claude-key"),
                "model": "claude-3-5-sonnet-20241022"
            },
            "gpt4": {
                "api_key": os.getenv("TEST_OPENAI_API_KEY", "test-gpt4-key"),
                "model": "gpt-4-turbo-preview"
            },
            "glm5": {
                "api_key": os.getenv("TEST_ZHIPUAI_API_KEY", "test-glm5-key"),
                "model": "glm-4"
            }
        },
        "agents": {
            "query_agent": {
                "agent_id": "test-query-agent",
                "name": "Test Query Agent",
                "version": "1.0.0"
            },
            "design_agent": {
                "agent_id": "test-design-agent", 
                "name": "Test Design Agent",
                "version": "1.0.0"
            }
        }
    }


@pytest.fixture
def sample_database_schema():
    """Sample database schema for testing."""
    return {
        "tables": {
            "users": {
                "columns": ["id", "name", "email", "created_at", "status"],
                "types": {
                    "id": "UInt32",
                    "name": "String",
                    "email": "String", 
                    "created_at": "DateTime",
                    "status": "String"
                }
            },
            "orders": {
                "columns": ["id", "user_id", "product_id", "amount", "created_at"],
                "types": {
                    "id": "UInt32",
                    "user_id": "UInt32",
                    "product_id": "UInt32",
                    "amount": "Decimal(10,2)",
                    "created_at": "DateTime"
                }
            },
            "products": {
                "columns": ["id", "name", "price", "category", "created_at"],
                "types": {
                    "id": "UInt32",
                    "name": "String",
                    "price": "Decimal(10,2)",
                    "category": "String",
                    "created_at": "DateTime"
                }
            },
            "sales": {
                "columns": ["id", "product_id", "quantity", "total", "date"],
                "types": {
                    "id": "UInt32",
                    "product_id": "UInt32",
                    "quantity": "UInt32",
                    "total": "Decimal(10,2)",
                    "date": "Date"
                }
            }
        },
        "relationships": [
            {"from": "orders.user_id", "to": "users.id"},
            {"from": "orders.product_id", "to": "products.id"},
            {"from": "sales.product_id", "to": "products.id"}
        ]
    }


@pytest.fixture
def sample_test_data():
    """Sample test data for database."""
    now = datetime.now()
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "created_at": now - timedelta(days=30), "status": "active"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "created_at": now - timedelta(days=25), "status": "active"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "created_at": now - timedelta(days=20), "status": "inactive"}
    ]
    
    products = [
        {"id": 1, "name": "Product A", "price": 29.99, "category": "Electronics", "created_at": now - timedelta(days=60)},
        {"id": 2, "name": "Product B", "price": 49.99, "category": "Books", "created_at": now - timedelta(days=55)},
        {"id": 3, "name": "Product C", "price": 19.99, "category": "Electronics", "created_at": now - timedelta(days=50)}
    ]
    
    orders = [
        {"id": 1, "user_id": 1, "product_id": 1, "amount": 29.99, "created_at": now - timedelta(days=10)},
        {"id": 2, "user_id": 1, "product_id": 2, "amount": 49.99, "created_at": now - timedelta(days=9)},
        {"id": 3, "user_id": 2, "product_id": 3, "amount": 19.99, "created_at": now - timedelta(days=8)},
        {"id": 4, "user_id": 3, "product_id": 1, "amount": 29.99, "created_at": now - timedelta(days=7)}
    ]
    
    sales = [
        {"id": 1, "product_id": 1, "quantity": 10, "total": 299.90, "date": (now - timedelta(days=10)).date()},
        {"id": 2, "product_id": 2, "quantity": 5, "total": 249.95, "date": (now - timedelta(days=9)).date()},
        {"id": 3, "product_id": 3, "quantity": 15, "total": 299.85, "date": (now - timedelta(days=8)).date()}
    ]
    
    return {
        "users": users,
        "products": products,
        "orders": orders,
        "sales": sales
    }


@pytest.fixture
def mock_llm_responses():
    """Mock LLM responses for different scenarios."""
    return {
        "simple_select": {
            "content": "SELECT name, email FROM users WHERE status = 'active'",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 50, "output_tokens": 20}
        },
        "aggregate_query": {
            "content": "SELECT p.category, SUM(s.total) as total_sales FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.category ORDER BY total_sales DESC LIMIT 10",
            "model": "claude-3-5-sonnet-20241022", 
            "usage": {"input_tokens": 80, "output_tokens": 45}
        },
        "join_query": {
            "content": "SELECT u.name, COUNT(o.id) as order_count, SUM(o.amount) as total_spent FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.status = 'active' GROUP BY u.id, u.name ORDER BY total_spent DESC",
            "model": "claude-3-5-sonnet-20241022",
            "usage": {"input_tokens": 95, "output_tokens": 55}
        },
        "error_response": {
            "error": "Unable to generate SQL for the given query",
            "model": "claude-3-5-sonnet-20241022"
        }
    }


@pytest.fixture
def sample_natural_language_queries():
    """Sample natural language queries for testing."""
    return [
        {
            "query": "Show me all active users",
            "expected_sql": "SELECT * FROM users WHERE status = 'active'",
            "type": "simple_select"
        },
        {
            "query": "What are the total sales by product category?",
            "expected_sql": "SELECT category, SUM(total) FROM sales JOIN products USING(product_id) GROUP BY category",
            "type": "aggregate"
        },
        {
            "query": "Find users who have placed more than 5 orders",
            "expected_sql": "SELECT user_id, COUNT(*) as order_count FROM orders GROUP BY user_id HAVING order_count > 5",
            "type": "aggregate_having"
        },
        {
            "query": "Show me sales trends over the last 30 days",
            "expected_sql": "SELECT date, SUM(total) as daily_total FROM sales WHERE date >= today() - 30 GROUP BY date ORDER BY date",
            "type": "time_series"
        },
        {
            "query": "Which products have never been sold?",
            "expected_sql": "SELECT p.* FROM products p LEFT JOIN sales s ON p.id = s.product_id WHERE s.id IS NULL",
            "type": "anti_join"
        }
    ]


@pytest.fixture
async def setup_test_database(sample_test_data, test_environment_config):
    """Setup test database with sample data."""
    # This would normally connect to a test database and populate it
    # For now, we'll mock the database setup
    
    database_url = f"clickhouse://{test_environment_config['database']['user']}:{test_environment_config['database']['password']}@{test_environment_config['database']['host']}:{test_environment_config['database']['port']}/{test_environment_config['database']['database']}"
    
    # Mock database setup
    setup_queries = [
        "CREATE TABLE IF NOT EXISTS users (id UInt32, name String, email String, created_at DateTime, status String)",
        "CREATE TABLE IF NOT EXISTS products (id UInt32, name String, price Decimal(10,2), category String, created_at DateTime)",
        "CREATE TABLE IF NOT EXISTS orders (id UInt32, user_id UInt32, product_id UInt32, amount Decimal(10,2), created_at DateTime)",
        "CREATE TABLE IF NOT EXISTS sales (id UInt32, product_id UInt32, quantity UInt32, total Decimal(10,2), date Date)"
    ]
    
    # In real implementation, execute these queries
    # For now, just return the setup info
    return {
        "database_url": database_url,
        "setup_queries": setup_queries,
        "data_loaded": True,
        "tables_created": ["users", "products", "orders", "sales"]
    }


@pytest.fixture
def test_agent_configs(test_environment_config):
    """Test agent configurations."""
    from agents.config import AgentConfig, LLMProviderConfig, AgentType, AgentCapability
    
    configs = {}
    
    # Query Agent config
    query_llm_config = LLMProviderConfig(
        provider="claude",
        model=test_environment_config["llm_providers"]["claude"]["model"],
        api_key=test_environment_config["llm_providers"]["claude"]["api_key"]
    )
    
    configs["query_agent"] = AgentConfig(
        agent_id="test-query-agent",
        name="Test Query Agent",
        version="1.0.0",
        agent_type=AgentType.QUERY,
        capabilities=[AgentCapability.QUERY, AgentCapability.ANALYSIS],
        llm_provider=query_llm_config,
        metadata={"default_dialect": "clickhouse"}
    )
    
    # Design Agent config
    design_llm_config = LLMProviderConfig(
        provider="gpt4", 
        model=test_environment_config["llm_providers"]["gpt4"]["model"],
        api_key=test_environment_config["llm_providers"]["gpt4"]["api_key"]
    )
    
    configs["design_agent"] = AgentConfig(
        agent_id="test-design-agent",
        name="Test Design Agent", 
        version="1.0.0",
        agent_type=AgentType.DESIGN,
        capabilities=[AgentCapability.DESIGN, AgentCapability.ANALYSIS],
        llm_provider=design_llm_config,
        metadata={"default_dialect": "clickhouse"}
    )
    
    return configs


@pytest.fixture
def performance_benchmarks():
    """Performance benchmarks for testing."""
    return {
        "query_generation": {
            "max_time_ms": 5000,  # 5 seconds max for query generation
            "target_time_ms": 2000,  # 2 seconds target
            "min_cache_hit_rate": 0.3  # 30% cache hit rate minimum
        },
        "api_endpoints": {
            "/health": {"max_time_ms": 100, "target_time_ms": 50},
            "/api/queries": {"max_time_ms": 10000, "target_time_ms": 5000},
            "/api/agents": {"max_time_ms": 500, "target_time_ms": 200}
        },
        "database_queries": {
            "simple_select": {"max_time_ms": 1000, "target_time_ms": 500},
            "aggregate_query": {"max_time_ms": 5000, "target_time_ms": 2000},
            "join_query": {"max_time_ms": 3000, "target_time_ms": 1500}
        }
    }


class TestEnvironmentSetup:
    """Test the test environment setup itself."""
    
    def test_config_loading(self, test_environment_config):
        """Test that test config loads correctly."""
        assert "database" in test_environment_config
        assert "llm_providers" in test_environment_config
        assert "agents" in test_environment_config
        
        # Check database config
        db_config = test_environment_config["database"]
        assert "host" in db_config
        assert "port" in db_config
        assert "database" in db_config
        
        # Check LLM provider configs
        llm_config = test_environment_config["llm_providers"]
        assert "claude" in llm_config
        assert "gpt4" in llm_config
        assert "glm5" in llm_config
    
    def test_sample_schema(self, sample_database_schema):
        """Test sample database schema."""
        schema = sample_database_schema
        
        assert "tables" in schema
        assert "relationships" in schema
        
        # Check tables
        tables = schema["tables"]
        assert "users" in tables
        assert "orders" in tables
        assert "products" in tables
        assert "sales" in tables
        
        # Check columns
        user_columns = tables["users"]["columns"]
        assert "id" in user_columns
        assert "name" in user_columns
        assert "email" in user_columns
    
    def test_sample_data(self, sample_test_data):
        """Test sample test data."""
        data = sample_test_data
        
        assert "users" in data
        assert "products" in data  
        assert "orders" in data
        assert "sales" in data
        
        # Check data counts
        assert len(data["users"]) == 3
        assert len(data["products"]) == 3
        assert len(data["orders"]) == 4
        assert len(data["sales"]) == 3
    
    def test_mock_llm_responses(self, mock_llm_responses):
        """Test mock LLM responses."""
        responses = mock_llm_responses
        
        assert "simple_select" in responses
        assert "aggregate_query" in responses
        assert "join_query" in responses
        assert "error_response" in responses
        
        # Check response structure
        simple_resp = responses["simple_select"]
        assert "content" in simple_resp
        assert "model" in simple_resp
        assert "usage" in simple_resp
    
    def test_natural_language_queries(self, sample_natural_language_queries):
        """Test sample natural language queries."""
        queries = sample_natural_language_queries
        
        assert len(queries) == 5
        
        for query in queries:
            assert "query" in query
            assert "expected_sql" in query
            assert "type" in query
    
    def test_agent_configs(self, test_agent_configs):
        """Test agent configurations."""
        configs = test_agent_configs
        
        assert "query_agent" in configs
        assert "design_agent" in configs
        
        # Check query agent config
        query_config = configs["query_agent"]
        assert query_config.agent_id == "test-query-agent"
        assert query_config.agent_type.value == "query"
        assert len(query_config.capabilities) == 2
    
    def test_performance_benchmarks(self, performance_benchmarks):
        """Test performance benchmark definitions."""
        benchmarks = performance_benchmarks
        
        assert "query_generation" in benchmarks
        assert "api_endpoints" in benchmarks
        assert "database_queries" in benchmarks
        
        # Check query generation benchmarks
        query_bench = benchmarks["query_generation"]
        assert "max_time_ms" in query_bench
        assert "target_time_ms" in query_bench
        assert "min_cache_hit_rate" in query_bench


if __name__ == "__main__":
    pytest.main([__file__, "-v"])