# Building Data Pipelines with ClickHouse: ELT, Not ETL

**Published:** February 21, 2026
**Reading Time:** 9 minutes
**Tags:** #data-engineering #clickhouse #pipelines #etl #analytics

---

## TL;DR

At AI Data Labs, we use ELT (Extract, Load, Transform) instead of ETL (Extract, Transform, Load) for our data pipelines:

- **Load raw data first** - Get it into ClickHouse fast
- **Transform in-database** - Leverage ClickHouse's SQL engine
- **Real-time ingestion** - No batch processing delays
- **Automated data quality** - Validation at ingest time
- **Idempotent pipelines** - Safe to re-run without duplication
- **Cost-effective** - Minimal transformation infrastructure

**Result:** Billions of events processed per day, < 5s end-to-end latency, <$50/month pipeline cost.

---

## ELT vs ETL: The Difference

### Traditional ETL (Extract, Transform, Load)

```
Extract → Transform → Load
   ↓          ↓          ↓
Source    Processing   Warehouse
```

**Flow:**
1. Extract data from source
2. Transform in external processing layer
3. Load into warehouse

**Problems:**
- **Slow** - Transformation layer adds latency
- **Complex** - Need separate transformation infrastructure
- **Costly** - Processing servers are expensive
- **Inflexible** - Hard to add new transformations

### Modern ELT (Extract, Load, Transform)

```
Extract → Load → Transform
   ↓        ↓          ↓
Source   Warehouse   In-database
```

**Flow:**
1. Extract data from source
2. Load raw into warehouse (ClickHouse)
3. Transform using SQL queries

**Benefits:**
- **Fast** - Data in warehouse immediately
- **Simple** - No transformation infrastructure
- **Cheap** - Use warehouse compute for transforms
- **Flexible** - Easy to add new SQL transforms

---

## Our Pipeline Architecture

### High-Level View

```
┌──────────────────────────────────────────────────────────┐
│                 Data Sources                           │
│  (Customer apps, web events, API, databases)        │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   ClickHouse  │  ← Raw events table
              │   (Raw Data)  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   ClickHouse  │  ← Transformed tables
              │  (Transformed) │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │  Materialized   │  ← Pre-aggregated
              │     Views      │
              └───────┬───────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  Analytics/Queries   │  ← Fast queries
          └───────────────────────┘
```

### Pipeline Stages

#### Stage 1: Ingestion (Load Raw)

**FastAPI ingestion endpoint:**

```python
from fastapi import FastAPI, BackgroundTasks
from clickhouse_connect import get_client
import structlog

app = FastAPI()
client = get_client(host='clickhouse', port=8123)
logger = structlog.get_logger()

@app.post("/api/v1/ingest")
async def ingest_event(event: dict):
    """Ingest single event"""
    try:
        # Insert directly to raw table
        client.insert(
            table='events_raw',
            data=[{
                'event_id': event['id'],
                'user_id': event['user_id'],
                'event_type': event['type'],
                'properties': event['properties'],
                'timestamp': event['timestamp']
            }],
            settings={'async_insert': True}  # Async insertion
        )
        return {"status": "accepted"}
    except Exception as e:
        logger.error("ingest_failed", error=str(e))
        raise HTTPException(500, "Ingestion failed")

@app.post("/api/v1/ingest/batch")
async def ingest_batch(events: list[dict]):
    """Ingest multiple events"""
    try:
        # Batch insert for better performance
        client.insert(
            table='events_raw',
            data=[{
                'event_id': e['id'],
                'user_id': e['user_id'],
                'event_type': e['type'],
                'properties': e['properties'],
                'timestamp': e['timestamp']
            } for e in events],
            settings={'async_insert': True}
        )
        return {"status": "accepted", "count": len(events)}
    except Exception as e:
        logger.error("batch_ingest_failed", error=str(e))
        raise HTTPException(500, "Batch ingestion failed")
```

**Raw table schema:**

```sql
CREATE TABLE events_raw (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    properties JSON,
    timestamp DateTime64(3),
    _ingested_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp)
SETTINGS index_granularity = 8192;
```

#### Stage 2: Transformation (ClickHouse SQL)

**Create transformed table:**

```sql
CREATE TABLE events_transformed AS events_raw
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp)
AS SELECT
    event_id,
    user_id,
    event_type,
    -- Extract nested properties
    properties['page_url'] AS page_url,
    properties['referrer'] AS referrer,
    properties['device_type'] AS device_type,
    properties['browser'] AS browser,
    properties['revenue']::Decimal(18, 2) AS revenue,
    -- Add derived columns
    toDate(timestamp) AS date,
    toHour(timestamp) AS hour,
    toDayOfWeek(timestamp) AS day_of_week,
    -- User segment calculation
    CASE
        WHEN revenue > 100 THEN 'high_value'
        WHEN revenue > 10 THEN 'medium_value'
        ELSE 'low_value'
    END AS user_segment
FROM events_raw
WHERE _ingested_at >= now() - INTERVAL 7 DAY;
```

#### Stage 3: Materialized Views (Real-time Aggregation)

**Daily metrics view:**

```sql
CREATE MATERIALIZED VIEW events_daily
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, event_type)
AS SELECT
    toDate(timestamp) AS date,
    event_type,
    count() AS event_count,
    sum(revenue) AS total_revenue,
    avg(revenue) AS avg_revenue,
    uniqExact(user_id) AS unique_users,
    countIf(user_segment = 'high_value') AS high_value_users
FROM events_transformed
GROUP BY date, event_type;
```

**Real-time session window:**

```sql
CREATE MATERIALIZED VIEW active_sessions
ENGINE = AggregatingMergeTree()
ORDER BY user_id
AS SELECT
    user_id,
    maxState(timestamp) AS last_seen,
    minState(timestamp) AS session_start,
    countState() AS event_count,
    sumState(revenue) AS session_revenue
FROM events_transformed
GROUP BY user_id
HAVING last_seen >= now() - INTERVAL 30 MINUTE;
```

---

## Data Quality at the Edge

### Validation Rules

**Validate before ingest:**

```python
from pydantic import BaseModel, validator, constr
from datetime import datetime
from decimal import Decimal

class EventValidation(BaseModel):
    """Validate incoming events"""
    event_id: str  # UUID
    user_id: str  # UUID
    event_type: constr(max_length=50)
    properties: dict
    timestamp: datetime

    @validator('event_id')
    def validate_event_id(cls, v):
        try:
            UUID(v)  # Check if valid UUID
        except ValueError:
            raise ValueError('Invalid event_id format')
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        try:
            UUID(v)  # Check if valid UUID
        except ValueError:
            raise ValueError('Invalid user_id format')
        return v

    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = [
            'page_view', 'click', 'purchase', 'signup',
            'login', 'logout', 'error'
        ]
        if v not in allowed_types:
            raise ValueError(f'Unknown event_type: {v}')
        return v

    @validator('properties')
    def validate_properties(cls, v):
        # Ensure properties doesn't contain forbidden keys
        forbidden_keys = ['password', 'token', 'secret']
        for key in v.keys():
            if key.lower() in forbidden_keys:
                raise ValueError(f'Forbidden property: {key}')
        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        # Reject future timestamps
        if v > datetime.utcnow():
            raise ValueError('Timestamp cannot be in the future')
        # Reject timestamps too old (> 30 days)
        if v < datetime.utcnow() - timedelta(days=30):
            raise ValueError('Timestamp too old')
        return v
```

### Quality Checks in ClickHouse

**Add quality metrics to events:**

```sql
-- Add quality columns
ALTER TABLE events_raw ADD COLUMN _quality_score Float32 DEFAULT 0.0;
ALTER TABLE events_raw ADD COLUMN _quality_issues Array(String) DEFAULT [];

-- Quality check function
CREATE OR REPLACE FUNCTION quality_check(
    properties JSON,
    user_id UUID,
    timestamp DateTime64(3)
) RETURNS Tuple(Float32, Array(String))
AS BEGIN
    DECLARE quality_score Float32 = 1.0;
    DECLARE issues Array(String) = [];

    -- Check for missing required fields
    if not has(properties, 'event_name') then
        quality_score = quality_score - 0.2;
        arrayPushBack(issues, 'missing_event_name');
    end if;

    -- Check for invalid values
    if properties['revenue'] < 0 then
        quality_score = quality_score - 0.3;
        arrayPushBack(issues, 'negative_revenue');
    end if;

    -- Check for suspicious patterns
    if length(properties['user_agent']) < 10 then
        quality_score = quality_score - 0.1;
        arrayPushBack(issues, 'suspicious_user_agent');
    end if;

    -- Check for duplicate events (simple heuristic)
    if (timestamp, user_id) in (
        SELECT timestamp, user_id
        FROM events_raw
        WHERE timestamp >= now() - INTERVAL 1 SECOND
        LIMIT 1
    ) then
        quality_score = quality_score - 0.4;
        arrayPushBack(issues, 'possible_duplicate');
    end if;

    -- Ensure quality_score is >= 0
    if quality_score < 0 then
        quality_score = 0;
    end if;

    RETURN (quality_score, issues);
END;
```

---

## Idempotent Ingestion

### Deduplication with ReplacingMergeTree

```sql
CREATE TABLE events_deduped (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    properties JSON,
    timestamp DateTime64(3),
    _ingested_at DateTime DEFAULT now(),
    _version UInt64 DEFAULT 1
) ENGINE = ReplacingMergeTree(_version)
PARTITION BY toYYYYMM(timestamp)
ORDER BY (event_id)
SETTINGS index_granularity = 8192;
```

**Upsert pattern:**

```python
def upsert_event(event: dict):
    """Upsert event (update if exists, insert if not)"""
    version = get_event_version(event['event_id']) + 1

    client.insert(
        table='events_deduped',
        data=[{
            'event_id': event['event_id'],
            'user_id': event['user_id'],
            'event_type': event['event_type'],
            'properties': event['properties'],
            'timestamp': event['timestamp'],
            '_version': version  # Higher version wins
        }]
    )
```

---

## Performance Optimizations

### Async Insertion

```python
# Async insert settings
client.insert(
    table='events_raw',
    data=events,
    settings={
        'async_insert': True,  # Async insertion
        'wait_for_async_insert': 0,  # Don't wait
        'async_insert_max_data_size': 1000000,  # 1MB batches
        'async_insert_busy_timeout_ms': 1000  # Wait up to 1s
    }
)
```

### Batch Processing

```python
# Collect events in buffer
event_buffer = []
buffer_size = 1000  # Process in batches
buffer_timeout = 5  # Flush every 5 seconds

async def flush_buffer():
    """Flush buffer to ClickHouse"""
    if event_buffer:
        client.insert(
            table='events_raw',
            data=event_buffer,
            settings={'async_insert': True}
        )
        event_buffer.clear()

@app.post("/api/v1/ingest")
async def ingest_event(event: dict):
    """Ingest event (buffered)"""
    event_buffer.append(event)

    # Flush if buffer full
    if len(event_buffer) >= buffer_size:
        await flush_buffer()

    return {"status": "accepted"}

# Background task to flush periodically
@app.on_event("startup")
async def start_flusher():
    asyncio.create_task(periodic_flush())

async def periodic_flush():
    """Periodically flush buffer"""
    while True:
        await asyncio.sleep(buffer_timeout)
        await flush_buffer()
```

### Partitioning Strategy

```sql
-- Partition by date for efficient querying
PARTITION BY toYYYYMM(timestamp)

-- Benefits:
-- - Drop old partitions: ALTER TABLE ... DROP PARTITION
-- - Query pruning: Only scan relevant partitions
-- - Faster ingestion: Parallel partition writes

-- Example: Drop old data
ALTER TABLE events_raw DROP PARTITION 202501;
```

---

## Monitoring Pipeline Health

### Pipeline Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
events_ingested_total = Counter(
    'events_ingested_total',
    'Total events ingested',
    ['event_type']
)

events_ingested_duration = Histogram(
    'events_ingested_duration_seconds',
    'Time to ingest events',
    ['event_type']
)

events_deduped_total = Counter(
    'events_deduped_total',
    'Total duplicate events detected'
)

pipeline_buffer_size = Gauge(
    'pipeline_buffer_size',
    'Current buffer size'
)

data_quality_score = Gauge(
    'data_quality_score',
    'Average data quality score',
    ['event_type']
)
```

### Health Checks

```python
@app.get("/health/pipeline")
async def pipeline_health():
    """Check pipeline health"""
    # Check ClickHouse connectivity
    try:
        client.query('SELECT 1')
        clickhouse_healthy = True
    except:
        clickhouse_healthy = False

    # Check buffer size
    buffer_healthy = len(event_buffer) < 10000

    # Check ingestion rate
    ingestion_rate = get_ingestion_rate()
    rate_healthy = ingestion_rate > 0

    health = {
        'status': 'healthy' if all([
            clickhouse_healthy,
            buffer_healthy,
            rate_healthy
        ]) else 'unhealthy',
        'checks': {
            'clickhouse': clickhouse_healthy,
            'buffer': buffer_healthy,
            'ingestion_rate': rate_healthy
        },
        'metrics': {
            'buffer_size': len(event_buffer),
            'ingestion_rate': ingestion_rate
        }
    }

    status_code = 200 if health['status'] == 'healthy' else 503
    return JSONResponse(content=health, status_code=status_code)
```

---

## Backfill and Replay

### Backfill Historical Data

```sql
-- Backfill from raw to transformed
INSERT INTO events_transformed
SELECT
    event_id,
    user_id,
    event_type,
    properties,
    timestamp,
    date,
    hour,
    day_of_week,
    user_segment
FROM events_raw
WHERE timestamp >= '2025-01-01'
  AND timestamp < '2025-02-01'
SETTINGS max_threads = 4;  -- Use 4 threads for parallel processing
```

### Replay Bad Batches

```python
def replay_batch(batch_id: str):
    """Replay events from a failed batch"""
    # Get events from raw table
    events = client.query(
        'SELECT * FROM events_raw WHERE _batch_id = %(batch_id)s',
        parameters={'batch_id': batch_id}
    )

    # Replay to transformed table
    for event in events.named_results():
        try:
            transform_and_insert(event)
        except Exception as e:
            logger.error("replay_failed", batch_id=batch_id, event_id=event.event_id)
            continue
```

---

## Best Practices

### 1. Load Raw, Transform Later

Don't transform during ingestion. Load raw, transform in database.

### 2. Use Materialized Views

Pre-compute aggregations for fast queries.

### 3. Partition Wisely

Partition by date. Don't over-partition.

### 4. Validate at Ingest

Reject bad data early. Don't pollute your warehouse.

### 5. Make Pipelines Idempotent

Safe to re-run. No duplicates.

### 6. Monitor Everything

Ingestion rate, error rate, lag, data quality.

---

## Tools We Use

| Purpose | Tool | Why? |
|----------|-------|-------|
| Ingestion | FastAPI | Async, type-safe, fast |
| Database | ClickHouse | Columnar, real-time, SQL |
| Transformation | ClickHouse SQL | In-database, no ETL infrastructure |
| Monitoring | Prometheus | Metrics, alerts |
| Validation | Pydantic | Type-safe validation |
| Async processing | asyncio | Non-blocking I/O |

---

## Lessons Learned

### 1. ELT > ETL for Analytics

Transform in database. It's faster, simpler, cheaper.

### 2. Real-time is Possible

With ClickHouse, you can have real-time analytics without complex infrastructure.

### 3. Quality at the Edge

Validate early. Fix data quality issues at ingest, not in queries.

### 4. Idempotency Saves Headaches

Make pipelines idempotent. Safe to re-run, safe to fail.

### 5. Monitor Everything

You can't optimize what you don't measure.

---

## Conclusion

ELT pipelines with ClickHouse are powerful:

- **Fast** - Real-time ingestion, sub-second queries
- **Simple** - No transformation infrastructure
- **Cheap** - Minimal pipeline cost
- **Flexible** - Easy to add new transforms

Load raw, transform in database. That's it.

Billions of events per day. <$50/month.

You don't need complex ETL pipelines. You need ClickHouse.

---

**Want to learn more?**

- Check our [ClickHouse deep dive](/blog/clickhouse-why-we-chose-it)
- Learn about our [tech stack](/blog/tech-stack-architecture)
- See our [open source code](https://github.com/duet-company)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Data Engineering Series. Next up: "Data Modeling in ClickHouse: Patterns and Anti-Patterns."*
