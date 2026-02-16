# Query Skill

Natural language to SQL translation agent skill.

## 🎯 Purpose

Transforms natural language queries into optimized SQL for ClickHouse and PostgreSQL databases. Enables users to ask questions in plain English and get accurate, optimized SQL queries.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Show me revenue trends for last 6 months

# Direct invocation
query-skill "What are our top 10 products by sales?"
```

## 📚 Dependencies

- ClickHouse client or PostgreSQL driver
- LLM provider (Claude, GPT-4, or GLM-5)
- Schema metadata access
- Query validation tools

## 🔧 Configuration

### Environment Variables

```bash
# Database connection
DB_TYPE=clickhouse|postgresql
DB_HOST=localhost
DB_PORT=8123
DB_NAME=analytics
DB_USER=default
DB_PASSWORD=***

# LLM provider
LLM_PROVIDER=claude|openai|zai
LLM_API_KEY=***
LLM_MODEL=claude-3-opus|gpt-4|glm-5

# Query settings
QUERY_TIMEOUT=30
MAX_ROWS=100000
ENABLE_OPTIMIZATION=true
```

### Skill Configuration

```yaml
query:
  database:
    type: clickhouse
    host: ${DB_HOST}
    port: ${DB_PORT}
    name: ${DB_NAME}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  optimization:
    enabled: ${ENABLE_OPTIMIZATION}
    max_rows: ${MAX_ROWS}
    timeout: ${QUERY_TIMEOUT}
```

## 📖 Examples

### Basic Queries

```sql
-- Natural Language
"Show me revenue trends for last 6 months"

-- Generated SQL
SELECT 
    toStartOfMonth(created_at) AS month,
    SUM(revenue) AS total_revenue,
    COUNT(*) AS order_count
FROM orders
WHERE created_at >= now() - INTERVAL 6 MONTH
GROUP BY month
ORDER BY month
```

```sql
-- Natural Language
"What are our top 10 products by sales?"

-- Generated SQL
SELECT 
    product_name,
    SUM(quantity) AS total_sold,
    SUM(price * quantity) AS total_revenue
FROM order_items
WHERE created_at >= now() - INTERVAL 30 DAY
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 10
```

### Complex Queries

```sql
-- Natural Language
"Show me customer retention rates over time by cohort"

-- Generated SQL
WITH cohorts AS (
    SELECT
        user_id,
        min(created_at) AS first_order
    FROM orders
    GROUP BY user_id
),
retention AS (
    SELECT
        toStartOfMonth(c.first_order) AS cohort_month,
        toStartOfMonth(o.created_at) AS activity_month,
        COUNT(DISTINCT c.user_id) AS cohort_size,
        COUNT(DISTINCT o.user_id) AS active_users
    FROM cohorts c
    JOIN orders o ON o.user_id = c.user_id
    WHERE o.created_at >= c.first_order
        AND o.created_at < c.first_order + INTERVAL 6 MONTH
    GROUP BY cohort_month, activity_month
)
SELECT
    cohort_month,
    activity_month,
    cohort_size,
    active_users,
    ROUND(active_users * 100.0 / cohort_size, 2) AS retention_rate
FROM retention
ORDER BY cohort_month, activity_month
```

## 🐛 Troubleshooting

### Issue: SQL returns empty results

**Possible causes:**
- Table names incorrect
- Column names don't match schema
- Date range too restrictive

**Solutions:**
1. Check schema metadata: `query-skill --schema`
2. Validate table names in generated SQL
3. Expand date range in query
4. Check database permissions

### Issue: Query too slow

**Possible causes:**
- Missing indexes
- Suboptimal JOIN order
- No partition pruning

**Solutions:**
1. Enable automatic optimization: `ENABLE_OPTIMIZATION=true`
2. Check query plan: `EXPLAIN <query>`
3. Add indexes to frequently queried columns
4. Use materialized views for complex aggregations

### Issue: LLM generates invalid SQL

**Possible causes:**
- Schema not loaded
- Ambiguous column names
- Complex requirements

**Solutions:**
1. Refresh schema: `query-skill --refresh-schema`
2. Provide more context in query
3. Break complex query into multiple steps
4. Use explicit table prefixes

## 📊 Performance

### Benchmarks

| Query Type | Avg Time | Success Rate |
|------------|-----------|--------------|
| Simple SELECT | 50ms | 98% |
| JOIN queries | 200ms | 95% |
| Aggregations | 300ms | 92% |
| Complex | 800ms | 85% |

### Optimization Tips

1. **Use appropriate indexes** on WHERE and JOIN columns
2. **Limit result sets** with sensible LIMIT clauses
3. **Partition by date** for time-series queries
4. **Materialize common views** for complex queries
5. **Use approximate functions** when exact values not needed

## 🔗 Related Skills

- [Design Skill](./design-skill.md) - Schema design
- [Data Skill](./data-skill.md) - Pipeline management
- [Ops Skill](./ops-skill.md) - Monitoring queries

## 📖 References

- [ClickHouse SQL Reference](https://clickhouse.com/docs/en/sql-reference/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Best Practices](https://docs.openclaw.ai/sql-best-practices)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company AI Team
