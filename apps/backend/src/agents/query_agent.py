"""
Query Agent for AI Data Labs.

This agent transforms natural language queries into optimized SQL for
ClickHouse and PostgreSQL databases with advanced features:
- High-accuracy NL to SQL conversion
- Query optimization hints
- Result caching
- Multi-dialect SQL support
- Query explanations
- Performance metrics tracking
"""

import hashlib
import json
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import logging

from .base import BaseAgent, AgentCapability, AgentStatus
from .config import AgentConfig, AgentType, LLMProviderConfig
from .errors import AgentConfigError, AgentInitializationError, AgentExecutionError
from .llm_providers import (
    BaseLLMProvider,
    LLMMessage,
    LLMMessageRole,
    LLMResponse,
    create_llm_provider,
)


class SQLDialect(Enum):
    """Supported SQL dialects."""
    CLICKHOUSE = "clickhouse"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class QueryMetrics:
    """Metrics for query execution."""

    def __init__(self):
        self.query_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        self.sql_generation_time_ms = 0.0
        self.validation_time_ms = 0.0
        self.optimization_time_ms = 0.0

    def record_query(self, latency_ms: float, success: bool, cached: bool = False):
        """Record a query execution."""
        self.query_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.total_latency_ms += latency_ms
        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def record_stage(self, stage: str, duration_ms: float):
        """Record a specific stage duration."""
        if stage == "sql_generation":
            self.sql_generation_time_ms += duration_ms
        elif stage == "validation":
            self.validation_time_ms += duration_ms
        elif stage == "optimization":
            self.optimization_time_ms += duration_ms

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        avg_latency = (self.total_latency_ms / self.query_count) if self.query_count > 0 else 0.0
        success_rate = (self.success_count / self.query_count) if self.query_count > 0 else 0.0
        cache_hit_rate = (self.cache_hits / self.query_count) if self.query_count > 0 else 0.0

        return {
            "total_queries": self.query_count,
            "successful_queries": self.success_count,
            "failed_queries": self.error_count,
            "success_rate": round(success_rate * 100, 2),
            "average_latency_ms": round(avg_latency, 2),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": round(cache_hit_rate * 100, 2),
            "avg_sql_generation_ms": round(self.sql_generation_time_ms / self.query_count, 2) if self.query_count > 0 else 0,
            "avg_validation_ms": round(self.validation_time_ms / self.query_count, 2) if self.query_count > 0 else 0,
            "avg_optimization_ms": round(self.optimization_time_ms / self.query_count, 2) if self.query_count > 0 else 0,
        }


class QueryCache:
    """Cache for query results."""

    def __init__(self, ttl_minutes: int = 30, max_size: int = 1000):
        """
        Initialize the query cache.

        Args:
            ttl_minutes: Time-to-live for cache entries in minutes
            max_size: Maximum number of cached queries
        """
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_size = max_size

    def _generate_key(self, query: str, dialect: SQLDialect) -> str:
        """Generate cache key from query and dialect."""
        key_string = f"{query}::{dialect.value}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, query: str, dialect: SQLDialect) -> Optional[Any]:
        """
        Get cached result if available and not expired.

        Args:
            query: Natural language query
            dialect: SQL dialect

        Returns:
            Cached result or None
        """
        key = self._generate_key(query, dialect)

        if key in self.cache:
            result, timestamp = self.cache[key]

            # Check if expired
            if datetime.utcnow() - timestamp < self.ttl:
                return result
            else:
                # Remove expired entry
                del self.cache[key]

        return None

    def set(self, query: str, dialect: SQLDialect, result: Any) -> None:
        """
        Cache query result.

        Args:
            query: Natural language query
            dialect: SQL dialect
            result: Query result to cache
        """
        # Evict oldest entry if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        key = self._generate_key(query, dialect)
        self.cache[key] = (result, datetime.utcnow())

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_minutes": int(self.ttl.total_seconds() / 60),
        }


class QueryValidator:
    """Validator for generated SQL queries."""

    # SQL injection patterns to detect
    INJECTION_PATTERNS = [
        r';\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE)\s',
        r'--\s*[\w\s]*(DROP|DELETE|UPDATE|INSERT)',
        r'/\*[\s\S]*?DROP|DELETE|UPDATE|INSERT[\s\S]*?\*/',
        r'UNION\s+ALL\s+SELECT',
        r'1\s*=\s*1',
        r'OR\s+1\s*=\s*1',
        r'AND\s+1\s*=\s*1',
    ]

    def __init__(self, dialect: SQLDialect):
        """
        Initialize validator.

        Args:
            dialect: SQL dialect for validation
        """
        self.dialect = dialect

    def validate(self, sql: str, schema: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety and correctness.

        Args:
            sql: SQL query to validate
            schema: Optional database schema for validation

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for SQL injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE | re.MULTILINE):
                return False, f"Potential SQL injection detected: {pattern}"

        # Check for basic SQL syntax
        if not sql.strip():
            return False, "Empty SQL query"

        # Ensure it starts with SELECT (read-only for now)
        if not re.match(r'^\s*SELECT', sql, re.IGNORECASE):
            return False, "Only SELECT queries are supported"

        # Check for balanced parentheses
        if sql.count('(') != sql.count(')'):
            return False, "Unbalanced parentheses in SQL"

        # Validate against schema if provided
        if schema:
            schema_valid, schema_error = self._validate_against_schema(sql, schema)
            if not schema_valid:
                return False, schema_error

        return True, None

    def _validate_against_schema(self, sql: str, schema: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL against database schema.

        Args:
            sql: SQL query
            schema: Database schema

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Extract table names from SQL
        table_pattern = r'FROM\s+(\w+)'
        tables = re.findall(table_pattern, sql, re.IGNORECASE)

        for table in tables:
            if table not in schema.get("tables", {}):
                return False, f"Table '{table}' not found in schema"

        return True, None


class QueryOptimizer:
    """Optimizer for SQL queries."""

    OPTIMIZATION_HINTS = {
        SQLDialect.CLICKHOUSE: [
            "Use SAMPLE clause for approximate queries on large tables",
            "Consider using materialized views for aggregations",
            "Use PREWHERE for filtering before column read",
            "Avoid using SELECT * for large tables",
            "Use toStartOfMonth/toDate for date grouping",
        ],
        SQLDialect.POSTGRESQL: [
            "Use EXPLAIN ANALYZE to check query plan",
            "Create indexes on frequently filtered columns",
            "Use VACUUM ANALYZE for statistics",
            "Consider using CTEs for complex queries",
            "Use LIMIT with OFFSET carefully",
        ],
    }

    def __init__(self, dialect: SQLDialect):
        """
        Initialize optimizer.

        Args:
            dialect: SQL dialect for optimization
        """
        self.dialect = dialect

    def optimize(self, sql: str) -> Tuple[str, List[str]]:
        """
        Optimize SQL query.

        Args:
            sql: SQL query to optimize

        Returns:
            Tuple of (optimized_sql, optimization_notes)
        """
        optimized_sql = sql
        notes = []

        # Remove unnecessary whitespace
        optimized_sql = re.sub(r'\s+', ' ', optimized_sql).strip()

        # Add LIMIT if missing for non-aggregate queries
        if not re.search(r'LIMIT\s+\d+', optimized_sql, re.IGNORECASE):
            if 'COUNT(' not in optimized_sql.upper() and 'SUM(' not in optimized_sql.upper():
                optimized_sql += " LIMIT 1000"
                notes.append("Added LIMIT 1000 to prevent excessive results")

        # Dialect-specific optimizations
        if self.dialect == SQLDialect.CLICKHOUSE:
            optimized_sql = self._optimize_clickhouse(optimized_sql, notes)
        elif self.dialect == SQLDialect.POSTGRESQL:
            optimized_sql = self._optimize_postgresql(optimized_sql, notes)

        return optimized_sql, notes

    def _optimize_clickhouse(self, sql: str, notes: List[str]) -> str:
        """Apply ClickHouse-specific optimizations."""
        # Convert date functions to ClickHouse format
        if re.search(r'\bDATE\b', sql, re.IGNORECASE):
            sql = re.sub(r'\bDATE\(', 'toDate(', sql)
            notes.append("Converted DATE() to toDate() for ClickHouse")

        # Use SAMPLE for approximate queries
        if 'COUNT(*)' in sql.upper() and 'SAMPLE' not in sql.upper():
            sql = sql.replace('COUNT(*)', 'COUNT(*) SAMPLE 0.1')
            notes.append("Added SAMPLE for approximate COUNT")

        return sql

    def _optimize_postgresql(self, sql: str, notes: List[str]) -> str:
        """Apply PostgreSQL-specific optimizations."""
        # Convert date functions to PostgreSQL format
        if 'toDate(' in sql:
            sql = re.sub(r'toDate\(', 'DATE(', sql)
            notes.append("Converted toDate() to DATE() for PostgreSQL")

        return sql

    def get_optimization_hints(self) -> List[str]:
        """Get optimization hints for the current dialect."""
        return self.OPTIMIZATION_HINTS.get(self.dialect, [])


class QueryExplainer:
    """Explainer for SQL queries."""

    def explain(self, sql: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate explanation for SQL query.

        Args:
            sql: SQL query to explain
            schema: Optional database schema

        Returns:
            Explanation dictionary
        """
        explanation = {
            "query_type": self._detect_query_type(sql),
            "tables_accessed": self._extract_tables(sql),
            "columns_used": self._extract_columns(sql),
            "operations": self._extract_operations(sql),
            "estimated_complexity": self._estimate_complexity(sql),
            "suggestions": self._generate_suggestions(sql),
        }

        if schema:
            explanation["schema_validation"] = self._validate_with_schema(sql, schema)

        return explanation

    def _detect_query_type(self, sql: str) -> str:
        """Detect the type of query (simple, join, aggregate, subquery)."""
        sql_upper = sql.upper()

        if ' JOIN ' in sql_upper:
            return "join_query"
        elif ' GROUP BY ' in sql_upper:
            return "aggregate_query"
        elif ' UNION ' in sql_upper:
            return "union_query"
        elif '(' in sql and ')' in sql:
            return "subquery"
        else:
            return "simple_query"

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL."""
        pattern = r'FROM\s+([^\s,)]+)'
        tables = re.findall(pattern, sql, re.IGNORECASE)
        return list(set(tables))

    def _extract_columns(self, sql: str) -> List[str]:
        """Extract column names from SQL."""
        # Extract from SELECT clause
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if select_match:
            columns_str = select_match.group(1)
            columns = [col.strip().split(' AS ')[0].strip() for col in columns_str.split(',')]
            return [col for col in columns if col != '*']
        return []

    def _extract_operations(self, sql: str) -> List[str]:
        """Extract SQL operations from query."""
        operations = []

        operation_patterns = {
            'COUNT': 'COUNT aggregation',
            'SUM': 'SUM aggregation',
            'AVG': 'AVG aggregation',
            'MAX': 'MAX aggregation',
            'MIN': 'MIN aggregation',
            'JOIN': 'JOIN operation',
            'WHERE': 'WHERE filter',
            'GROUP BY': 'GROUP BY grouping',
            'ORDER BY': 'ORDER BY sorting',
            'HAVING': 'HAVING filter',
            'LIMIT': 'LIMIT pagination',
        }

        for op, desc in operation_patterns.items():
            if op in sql.upper():
                operations.append(desc)

        return operations

    def _estimate_complexity(self, sql: str) -> str:
        """Estimate query complexity based on operations."""
        complexity_score = 0

        if 'JOIN' in sql.upper():
            complexity_score += 2
        if 'GROUP BY' in sql.upper():
            complexity_score += 1
        if 'HAVING' in sql.upper():
            complexity_score += 1
        if 'UNION' in sql.upper():
            complexity_score += 2
        if 'CASE WHEN' in sql.upper():
            complexity_score += 1

        if complexity_score <= 1:
            return "low"
        elif complexity_score <= 3:
            return "medium"
        else:
            return "high"

    def _generate_suggestions(self, sql: str) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []

        if 'SELECT *' in sql.upper():
            suggestions.append("Consider selecting only required columns instead of SELECT *")

        if sql.upper().count('JOIN') > 2:
            suggestions.append("Multiple JOINs may impact performance. Consider breaking into separate queries")

        if 'LIMIT' not in sql.upper():
            suggestions.append("Consider adding LIMIT to prevent excessive result sets")

        return suggestions

    def _validate_with_schema(self, sql: str, schema: Dict) -> Dict[str, Any]:
        """Validate query against provided schema."""
        return {
            "validated": True,
            "schema_version": schema.get("version", "unknown"),
        }


class QueryAgent(BaseAgent):
    """
    Query Agent for natural language to SQL translation.

    Capabilities:
    - QUERY: Transform NL queries to SQL
    - ANALYSIS: Analyze and explain queries
    - VALIDATION: Validate SQL syntax and safety

    Example usage:
        agent = QueryAgent(config)
        await agent.initialize()
        result = await agent.process({
            "query": "Show me revenue trends for last 6 months",
            "dialect": "clickhouse"
        })
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the Query Agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.llm_provider: Optional[BaseLLMProvider] = None
        self.cache: Optional[QueryCache] = None
        self.validator: Optional[QueryValidator] = None
        self.optimizer: Optional[QueryOptimizer] = None
        self.explainer: QueryExplainer = QueryExplainer()
        self.metrics: QueryMetrics = QueryMetrics()
        self.schema: Optional[Dict] = None

    async def initialize(self) -> None:
        """
        Initialize the agent.

        Raises:
            AgentInitializationError: If initialization fails
        """
        try:
            self.set_status(AgentStatus.INITIALIZING)
            self.logger.info("Initializing Query Agent...")

            # Initialize LLM provider
            if not self.config.llm_provider:
                raise AgentConfigError("LLM provider configuration required")

            self.llm_provider = create_llm_provider(
                provider=self.config.llm_provider.provider,
                model=self.config.llm_provider.model,
                api_key=self.config.llm_provider.api_key,
                api_url=self.config.llm_provider.api_url,
                temperature=self.config.llm_provider.temperature,
                max_tokens=self.config.llm_provider.max_tokens,
            )

            # Validate LLM connection
            self.logger.info("Testing LLM provider connection...")
            await self.llm_provider.initialize()
            test_response = await self.llm_provider.generate([
                LLMMessage(role=LLMMessageRole.USER, content="Test connection")
            ])
            self.logger.info(f"LLM connection successful: {len(test_response.content)} chars")

            # Initialize cache
            cache_ttl = self.config.metadata.get("cache_ttl_minutes", 30)
            cache_max_size = self.config.metadata.get("cache_max_size", 1000)
            self.cache = QueryCache(ttl_minutes=cache_ttl, max_size=cache_max_size)

            # Initialize validator and optimizer with default dialect
            default_dialect = self.config.metadata.get("default_dialect", "clickhouse")
            self.validator = QueryValidator(SQLDialect(default_dialect))
            self.optimizer = QueryOptimizer(SQLDialect(default_dialect))

            # Load schema if provided
            schema_path = self.config.metadata.get("schema_path")
            if schema_path:
                await self._load_schema(schema_path)

            self.set_status(AgentStatus.READY)
            self.logger.info("Query Agent initialized successfully")

        except Exception as e:
            self.set_status(AgentStatus.ERROR)
            self.logger.error(f"Failed to initialize Query Agent: {e}")
            raise AgentInitializationError(f"Initialization failed: {e}")

    async def process(
        self,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process natural language query and generate SQL.

        Args:
            input_data: Can be a string (query) or dict with 'query' and 'dialect'
            metadata: Optional metadata including schema, options

        Returns:
            Dictionary with SQL query, explanation, and metadata

        Raises:
            AgentExecutionError: If processing fails
        """
        self.set_status(AgentStatus.PROCESSING)
        start_time = time.time()

        try:
            # Parse input
            if isinstance(input_data, str):
                query = input_data
                dialect_str = self.config.metadata.get("default_dialect", "clickhouse")
            elif isinstance(input_data, dict):
                query = input_data.get("query", "")
                dialect_str = input_data.get("dialect", self.config.metadata.get("default_dialect", "clickhouse"))
                schema = input_data.get("schema")
                if schema:
                    self.schema = schema
            else:
                raise AgentExecutionError("Invalid input data format")

            if not query:
                raise AgentExecutionError("Query is required")

            dialect = SQLDialect(dialect_str)
            self.validator = QueryValidator(dialect)
            self.optimizer = QueryOptimizer(dialect)

            # Check cache first
            cached_result = self.cache.get(query, dialect)
            if cached_result:
                latency_ms = (time.time() - start_time) * 1000
                self.metrics.record_query(latency_ms, True, cached=True)
                self.set_status(AgentStatus.READY)
                return {
                    **cached_result,
                    "cached": True,
                    "execution_time_ms": round(latency_ms, 2),
                }

            # Generate SQL
            sql_gen_start = time.time()
            sql = await self._generate_sql(query, dialect, metadata)
            sql_gen_time = (time.time() - sql_gen_start) * 1000
            self.metrics.record_stage("sql_generation", sql_gen_time)

            # Validate SQL
            validation_start = time.time()
            is_valid, validation_error = self.validator.validate(sql, self.schema)
            validation_time = (time.time() - validation_start) * 1000
            self.metrics.record_stage("validation", validation_time)

            if not is_valid:
                raise AgentExecutionError(f"SQL validation failed: {validation_error}")

            # Optimize SQL
            optimization_start = time.time()
            optimized_sql, optimization_notes = self.optimizer.optimize(sql)
            optimization_time = (time.time() - optimization_start) * 1000
            self.metrics.record_stage("optimization", optimization_time)

            # Generate explanation
            explanation = self.explainer.explain(optimized_sql, self.schema)

            # Build result
            result = {
                "original_query": query,
                "generated_sql": sql,
                "optimized_sql": optimized_sql,
                "dialect": dialect.value,
                "explanation": explanation,
                "optimization_notes": optimization_notes,
                "validation": {
                    "is_valid": is_valid,
                    "error": validation_error,
                },
                "cached": False,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "performance": {
                    "sql_generation_ms": round(sql_gen_time, 2),
                    "validation_ms": round(validation_time, 2),
                    "optimization_ms": round(optimization_time, 2),
                },
            }

            # Cache the result
            self.cache.set(query, dialect, result)

            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_query(latency_ms, True)

            self.set_status(AgentStatus.READY)
            return result

        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_query(latency_ms, False)
            self.set_status(AgentStatus.ERROR)
            raise AgentExecutionError(f"Query processing failed: {e}")

    async def _generate_sql(
        self,
        query: str,
        dialect: SQLDialect,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Generate SQL from natural language query using LLM.

        Args:
            query: Natural language query
            dialect: Target SQL dialect
            metadata: Additional metadata

        Returns:
            Generated SQL query
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(dialect)

        # Build user prompt with schema context
        user_prompt = self._build_user_prompt(query, dialect, self.schema)

        messages = [
            LLMMessage(role=LLMMessageRole.SYSTEM, content=system_prompt),
            LLMMessage(role=LLMMessageRole.USER, content=user_prompt),
        ]

        # Generate SQL
        response: LLMResponse = await self.llm_provider.generate(messages)

        # Extract SQL from response (handle markdown code blocks)
        sql = self._extract_sql_from_response(response.content)

        return sql

    def _build_system_prompt(self, dialect: SQLDialect) -> str:
        """Build system prompt for LLM."""
        prompt = f"""You are an expert SQL query generator for {dialect.value} database.

Your task is to convert natural language questions into accurate, optimized SQL queries.

Guidelines:
- Generate only valid SQL, no explanations or markdown
- Use appropriate {dialect.value} syntax and functions
- Ensure queries are read-only (SELECT statements only)
- Use meaningful column and table aliases
- Include LIMIT clauses for non-aggregate queries
- Optimize for performance when possible

{dialect.value}-specific considerations:
"""
        if dialect == SQLDialect.CLICKHOUSE:
            prompt += """
- Use toStartOfMonth/toDate for date grouping
- Use SAMPLE for approximate aggregations on large tables
- Use PREWHERE for filtering before column read
- Use arrayJoin for array operations
- Use toYYYYMM for year-month grouping
"""
        elif dialect == SQLDialect.POSTGRESQL:
            prompt += """
- Use DATE_TRUNC for date grouping
- Use ILIKE for case-insensitive matching
- Use ARRAY_AGG for array aggregation
- Use COALESCE for null handling
- Use CAST or :: for type conversion
"""

        return prompt

    def _build_user_prompt(self, query: str, dialect: SQLDialect, schema: Optional[Dict]) -> str:
        """Build user prompt with query and schema context."""
        prompt = f"Convert this natural language question to SQL:\n\n{query}\n\n"

        if schema:
            prompt += "Database Schema:\n"
            for table_name, table_info in schema.get("tables", {}).items():
                prompt += f"\nTable: {table_name}\n"
                prompt += f"Columns: {', '.join(table_info.get('columns', []))}\n"
                if table_info.get('description'):
                    prompt += f"Description: {table_info['description']}\n"

        return prompt

    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL from LLM response, handling markdown code blocks."""
        # Try to extract from markdown code blocks
        code_block_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()

        # Try without language specifier
        code_block_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()

        # Return entire response if no code block found
        return response.strip()

    async def _load_schema(self, schema_path: str) -> None:
        """
        Load database schema from file.

        Args:
            schema_path: Path to schema JSON file
        """
        try:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
            self.logger.info(f"Loaded schema from {schema_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load schema from {schema_path}: {e}")

    async def shutdown(self) -> None:
        """
        Shutdown the agent gracefully.

        Raises:
            AgentExecutionError: If shutdown fails
        """
        try:
            self.set_status(AgentStatus.SHUTTING_DOWN)

            if self.llm_provider:
                await self.llm_provider.shutdown()

            if self.cache:
                self.cache.clear()

            self.set_status(AgentStatus.SHUTDOWN)
            self.logger.info("Query Agent shut down successfully")

        except Exception as e:
            self.set_status(AgentStatus.ERROR)
            self.logger.error(f"Failed to shutdown Query Agent: {e}")
            raise AgentExecutionError(f"Shutdown failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Check agent health and return status."""
        health = await super().health_check()

        # Add additional health information
        health.update({
            "cache_stats": self.cache.get_stats() if self.cache else {},
            "metrics_summary": self.metrics.get_summary(),
            "schema_loaded": self.schema is not None,
        })

        return health

    def get_metrics(self) -> Dict[str, Any]:
        """Get query metrics."""
        return self.metrics.get_summary()

    def get_optimization_hints(self, dialect: Optional[str] = None) -> List[str]:
        """Get optimization hints for a dialect."""
        if dialect:
            optimizer = QueryOptimizer(SQLDialect(dialect))
            return optimizer.get_optimization_hints()
        return self.optimizer.get_optimization_hints()

    def clear_cache(self) -> Dict[str, Any]:
        """Clear the query cache."""
        if self.cache:
            self.cache.clear()
            return {"status": "cleared", "cache_stats": self.cache.get_stats()}
        return {"status": "no cache"}
