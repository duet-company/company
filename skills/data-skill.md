# Data Skill

Data engineering and pipeline management agent skill.

## 🎯 Purpose

Manages data pipelines, ETL processes, data quality checks, and transformations for the AI Data Labs platform. Handles data ingestion, transformation, and storage operations.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Ingest yesterday's clickstream data into ClickHouse

# Direct invocation
data-skill "Create a daily sales aggregation pipeline"
```

## 📚 Dependencies

- Apache Airflow (orchestrator)
- ClickHouse client
- Kafka (streaming)
- Python (ETL scripts)
- LLM provider (Claude, GPT-4, or GLM-5)
- Data source connectors (PostgreSQL, S3, API)

## 🔧 Configuration

### Environment Variables

```bash
# Airflow
AIRFLOW_HOME=/opt/airflow
AIRFLOW_DB=postgresql://airflow:***@localhost/airflow
AIRFLOW_API_KEY=***

# Data Storage
CLICKHOUSE_HOST=clickhouse.ai-data-labs
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=***

# Streaming
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP=ai-data-labs

# ETL
ETL_TEMP_DIR=/tmp/etl
ETL_LOG_DIR=/var/log/etl
MAX_FILE_SIZE=100GB
BATCH_SIZE=10000

# Data Quality
QUALITY_CHECK_ENABLED=true
QUALITY_THRESHOLD=0.95
NULL_CHECK_ENABLED=true
DUPLICATE_CHECK_ENABLED=true

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***

# Monitoring
METRICS_ENABLED=true
METRICS_PORT=8080
```

### Skill Configuration

```yaml
data:
  airflow:
    home: ${AIRFLOW_HOME}
    db: ${AIRFLOW_DB}
    api_key: ${AIRFLOW_API_KEY}
  
  storage:
    clickhouse:
      host: ${CLICKHOUSE_HOST}
      port: ${CLICKHOUSE_PORT}
      user: ${CLICKHOUSE_USER}
      password: ${CLICKHOUSE_PASSWORD}
  
  streaming:
    kafka:
      bootstrap_servers: ${KAFKA_BOOTSTRAP_SERVERS}
      consumer_group: ${KAFKA_CONSUMER_GROUP}
  
  etl:
    temp_dir: ${ETL_TEMP_DIR}
    log_dir: ${ETL_LOG_DIR}
    max_file_size: ${MAX_FILE_SIZE}
    batch_size: ${BATCH_SIZE}
  
  quality:
    enabled: ${QUALITY_CHECK_ENABLED}
    threshold: ${QUALITY_THRESHOLD}
    null_check: ${NULL_CHECK_ENABLED}
    duplicate_check: ${DUPLICATE_CHECK_ENABLED}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  monitoring:
    enabled: ${METRICS_ENABLED}
    port: ${METRICS_PORT}
```

## 📖 Examples

### Clickstream Ingestion Pipeline

```markdown
Requirement:
"Ingest yesterday's clickstream data from Kafka into ClickHouse"

Generated Pipeline:

1. Source Configuration:
   - Type: Kafka
   - Topic: clickstream_events
   - Format: JSON
   - Consumer Group: ai-data-labs

2. Target Configuration:
   - Database: ClickHouse
   - Table: events.clickstream
   - Engine: MergeTree
   - Partition: by event_date

3. Transformation:
   - Parse JSON to structured data
   - Enrich with user session info
   - Normalize timestamps
   - Add ingestion metadata

4. Quality Checks:
   - Required fields: user_id, event_type, timestamp
   - Null check: < 1% threshold
   - Duplicate check: user_id + timestamp
   - Schema validation: Pass

5. Performance:
   - Batch size: 10,000 records
   - Parallelism: 4 workers
   - Target throughput: 100k rows/min
   - Retry policy: Exponential backoff

6. Monitoring:
   - Success rate tracking
   - Error rate alerting
   - Latency monitoring
   - Data completeness checks

Execution: Created DAG `clickstream_ingestion_v1`
Schedule: Hourly (0 * * * *)
Owner: data_engineering
```

### Daily Sales Aggregation

```markdown
Requirement:
"Create a daily sales aggregation pipeline with revenue by category"

Generated Pipeline:

1. Source Data:
   - Table: orders
   - Time range: Previous day
   - Columns: order_id, customer_id, product_id, amount, category

2. Aggregation Logic:
   ```sql
   INSERT INTO daily_sales
   SELECT
       toDate(order_date) AS date,
       category,
       COUNT(*) AS order_count,
       SUM(amount) AS revenue,
       COUNT(DISTINCT customer_id) AS customer_count,
       AVG(amount) AS avg_order_value
   FROM orders
   WHERE order_date >= yesterday()
       AND order_date < today()
   GROUP BY date, category
   ```

3. Data Quality:
   - Null check: All required fields
   - Range check: Revenue >= 0
   - Referential check: Valid category IDs
   - Threshold: 99% valid rows

4. Output Tables:
   - daily_sales (aggregated results)
   - daily_sales_quality (quality metrics)
   - pipeline_runs (execution metadata)

5. Scheduling:
   - Trigger: 1:00 AM UTC
   - Backfill: Last 30 days on first run
   - Alert: On failure

6. Performance:
   - Processing time: < 30 min
   - Record count: ~1M rows
   - Optimization: Use materialized views

Execution: Created DAG `daily_sales_aggregation_v1`
Schedule: Daily (0 1 * * *)
Owner: data_engineering
```

### Data Quality Check Pipeline

```markdown
Requirement:
"Run data quality checks on customer profiles"

Generated Pipeline:

1. Quality Checks:

   Null Check:
   ```sql
   SELECT 
       'email' AS field,
       COUNT(*) - COUNT(email) AS null_count,
       COUNT(*) AS total,
       ROUND((COUNT(*) - COUNT(email)) * 100.0 / COUNT(*), 2) AS null_percent
   FROM customers
   ```

   Range Check:
   ```sql
   SELECT 
       'order_date' AS field,
       COUNT(*) - COUNT(order_date BETWEEN '2020-01-01' AND NOW()) AS invalid_range,
       COUNT(*) AS total
   FROM orders
   ```

   Duplicate Check:
   ```sql
   SELECT 
       'email' AS field,
       COUNT(email) - COUNT(DISTINCT email) AS duplicates,
       COUNT(DISTINCT email) AS unique
   FROM customers
   ```

   Referential Check:
   ```sql
   SELECT 
       COUNT(o.customer_id) - COUNT(DISTINCT c.customer_id) AS orphaned_orders
   FROM orders o
   LEFT JOIN customers c ON o.customer_id = c.customer_id
   WHERE c.customer_id IS NULL
   ```

2. Thresholds:
   - Null threshold: < 1%
   - Invalid range: < 0.1%
   - Duplicate threshold: < 0.5%
   - Orphaned records: 0

3. Actions:
   - Pass threshold: 95%
   - Alert on failure
   - Create quality report
   - Store metrics in ClickHouse

4. Report:
   - Total records checked: 10M
   - Quality score: 98.5%
   - Issues found: 150K
   - Status: PASS

Execution: Created DAG `data_quality_check_v1`
Schedule: Hourly (0 * * * *)
Owner: data_engineering
```

## 🐛 Troubleshooting

### Issue: Pipeline stuck

**Possible causes:**
- Deadlock in database
- Network partition unavailable
- Resource exhaustion
- Airflow scheduler hung

**Solutions:**
1. Check Airflow logs: `airflow dags report`
2. Check task status: `airflow tasks list <dag_id>`
3. Kill stuck tasks: `airflow tasks clear <dag_id> --downstream`
4. Review resource limits: CPU, memory, disk
5. Restart scheduler: `airflow scheduler restart`

### Issue: Data ingestion lag

**Possible causes:**
- Kafka consumer offset lag
- High query volume
- Insufficient workers
- Network bottleneck

**Solutions:**
1. Check consumer lag: `kafka-consumer-groups --describe`
2. Increase workers: Update parallelism setting
3. Optimize queries: Review query plans
4. Batch size adjustment: Find optimal size
5. Scale infrastructure: Add more workers

### Issue: Quality check failures

**Possible causes:**
- Schema changes not reflected
- Data type mismatches
- Referential integrity issues
- Outdated validation rules

**Solutions:**
1. Refresh schema: `data-skill --refresh-schema`
2. Review quality rules: Check thresholds
3. Validate source data: Sample and inspect
4. Update checks: Fix validation logic
5. Quarantine bad data: Separate table for review

## 📊 Pipeline Monitoring

### Pipeline Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Success Rate | > 99% | TBD |
| Average Runtime | < 30 min | TBD |
| Data Freshness | < 1 hour | TBD |
| Quality Score | > 95% | TBD |
| Error Rate | < 1% | TBD |

### DAG Health

```yaml
daily_sales_aggregation_v1:
  last_run: 2026-02-16 01:00 UTC
  status: Success
  duration: 25 min 30s
  records_processed: 1,234,567
  quality_score: 98.5%

clickstream_ingestion_v1:
  last_run: 2026-02-16 00:30 UTC
  status: Success
  duration: 15 min 12s
  records_processed: 5,678,901
  lag: 30 min
```

## 🔗 Related Skills

- [Query Skill](./query-skill.md) - Query validation
- [Design Skill](./design-skill.md) - Schema updates
- [Ops Skill](./ops-skill.md) - Pipeline monitoring

## 📖 References

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [ClickHouse Best Practices](https://clickhouse.com/docs/en/best-practices/)
- [Kafka Guide](https://kafka.apache.org/documentation/)
- [Data Engineering Playbook](https://github.com/duet-company/playbook/blob/main/data-engineering/README.md)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company AI Team
