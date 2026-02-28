# Scaling from Startup to Enterprise: Our Journey to 100x Growth

**Published:** February 21, 2026
**Reading Time:** 10 minutes
**Tags:** #scaling #architecture #infrastructure #engineering #growth

---

## TL;DR

We designed AI Data Labs to scale from 100 users to 100,000+ without rearchitecture:

- **Start small** - Single-node K8s, 8GB RAM, $74/month
- **Scale horizontally** - Add nodes, not bigger servers
- **Database sharding** - ClickHouse replicas across clusters
- **Caching everywhere** - Redis, CDN, query results
- **Async everything** - Non-blocking operations for throughput
- **Multi-region** - Deploy closer to users for low latency

**Scaling path:**
- **Phase 1:** 100 users, $74/month
- **Phase 2:** 1,000 users, $200/month
- **Phase 3:** 10,000 users, $1,000/month
- **Phase 4:** 100,000 users, $5,000/month

---

## Phase 1: Startup (Months 1-3)

### Current Architecture

```
┌─────────────────────────────────────────────┐
│      Single VPS (4 vCPUs, 8 GB RAM)     │
│              microk8s (single node)        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  All Services │
         │  (1 node)     │
         └─────────────────┘
```

### Capacity

- **Users:** 100 concurrent
- **Queries/minute:** 100
- **Data:** 1 TB
- **Uptime:** 99.5% (single point of failure)
- **Cost:** $74/month

### When to Scale

**Triggers:**
- CPU usage > 80% for 30+ minutes
- Memory usage > 90% for 30+ minutes
- Query latency P95 > 2s
- 90+ concurrent users

**Actions:**
- Add 8 GB RAM → $24/month
- Optimize queries
- Add caching

---

## Phase 2: Growth (Months 4-6)

### Architecture

```
┌─────────────────────────────────────────────┐
│      Load Balancer (Cloudflare)           │
└──────┬───────────────┬──────────────────┘
       │               │
┌──────▼──────┐  ┌───▼────────┐
│  Node 1      │  │  Node 2    │
│ (Control)    │  │ (Worker)    │
│  8 GB RAM   │  │  16 GB RAM  │
└──────┬───────┘  └───┬────────┘
       │               │
       └───────┬───────┘
               │
       ┌───────▼────────┐
       │  Shared Data    │
       │  (ClickHouse)  │
       └────────────────┘
```

### Changes

**1. Add Worker Nodes:**

```bash
# Add second node
microk8s add-node

# Add third node
microk8s add-node

# Now we have 3-node cluster
microk8s status
```

**2. Separate Roles:**

- **Control plane:** Management, ingress, monitoring
- **Worker nodes:** Application workloads

**3. ClickHouse Replication:**

```sql
-- Create replicated table
CREATE TABLE events_replicated
(
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    timestamp DateTime64(3)
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',
    '{replica}'
)
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp);
```

### Capacity

- **Users:** 1,000 concurrent
- **Queries/minute:** 1,000
- **Data:** 10 TB
- **Uptime:** 99.9% (HA with 2 replicas)
- **Cost:** $200-250/month

### When to Scale

**Triggers:**
- Database storage > 80% full
- Query latency P95 > 3s
- 900+ concurrent users
- Revenue > $10k/month

**Actions:**
- Add more nodes
- Implement database sharding
- Add Redis caching
- Consider managed K8s

---

## Phase 3: Scale (Months 7-12)

### Architecture

```
┌─────────────────────────────────────────────┐
│      Global Load Balancer (Cloudflare)       │
└──────┬───────────────┬──────────────────┘
       │               │
┌──────▼─────────────▼─────────┐
│   Multi-Region K8s Cluster      │
│  ┌──────────┐  ┌──────────┐│
│  │   US-East │  │  EU-West ││
│  │ 5 nodes   │  │  3 nodes  ││
│  └──────────┘  └──────────┘│
└──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  ClickHouse Cluster            │
│  ┌──────────┐  ┌──────────┐│
│  │  Shard 1 │  │  Shard 2 ││
│  └──────────┘  └──────────┘│
└──────────────────────────────────┘
```

### Changes

**1. Multi-Region Deployment:**

```yaml
# Regional clusters
clusters:
  - name: us-east
    region: us-east-1
    nodes: 5
    storage: clickhouse-shard-1

  - name: eu-west
    region: eu-west-1
    nodes: 3
    storage: clickhouse-shard-2
```

**2. Database Sharding:**

```sql
-- Shard by user_id hash
CREATE TABLE events_sharded
(
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    timestamp DateTime64(3)
) ENGINE = Distributed(
    'cluster',
    'events',
    'sharded',
    cityHash64(user_id)
);
```

**3. Redis Caching Layer:**

```python
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

async def execute_query(query: str):
    # Check cache
    cache_key = f"query:{hash(query)}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Execute query
    result = await clickhouse.execute(query)

    # Cache result for 5 minutes
    redis_client.setex(
        cache_key,
        300,
        json.dumps(result)
    )

    return result
```

**4. Separate Services:**

- **Query Service:** Dedicated servers for queries
- **Ingestion Service:** Separate for event ingestion
- **AI Agent Service:** Separate for LLM processing
- **Admin Service:** Separate for management

### Capacity

- **Users:** 10,000 concurrent
- **Queries/minute:** 10,000
- **Data:** 100 TB
- **Uptime:** 99.95% (multi-region HA)
- **Cost:** $1,000-1,500/month

### When to Scale

**Triggers:**
- Sharding needed (> 10 TB per shard)
- Network latency > 100ms between regions
- 9,000+ concurrent users
- Revenue > $50k/month

**Actions:**
- Add more shards
- Add more regions (APAC)
- Consider ClickHouse Cloud
- Hire dedicated DevOps engineer

---

## Phase 4: Enterprise (Year 2+)

### Architecture

```
┌─────────────────────────────────────────────┐
│      Global CDN (Cloudflare Enterprise)      │
└──────┬───────────────┬──────────────────┘
       │               │
┌──────▼────┐  ┌──────▼────┐  ┌──────▼────┐
│  US-East   │  │  EU-West   │  │  APAC-East  │
│  20 nodes  │  │  15 nodes  │  │  10 nodes   │
│  5 shards  │  │  3 shards  │  │  2 shards  │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │                │                │
       └────────────────┴────────────────┘
                       │
              ┌────────▼────────┐
              │  Object Storage  │
              │    (S3)       │
              └─────────────────┘
```

### Changes

**1. Managed Kubernetes:**

```yaml
# Migrate from microk8s to EKS
provider: aws
cluster: aidatalabs-prod
node_groups:
  - name: query-servers
    instance_type: c5.4xlarge
    min_size: 10
    max_size: 50
    desired_size: 20

  - name: ingestion-servers
    instance_type: c5.2xlarge
    min_size: 5
    max_size: 30
    desired_size: 15
```

**2. ClickHouse Cloud:**

```yaml
# ClickHouse Cloud managed service
cluster: aidatalabs-prod
clickhouse_version: latest
replicas:
  - region: us-east-1
    count: 5
    type: Large
  - region: eu-west-1
    count: 3
    type: Large
  - region: apac-east-1
    count: 2
    type: Large
```

**3. Event Streaming (Kafka):**

```python
# Replace HTTP ingestion with Kafka
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='kafka-1:9092,kafka-2:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Produce to Kafka
producer.send(
    topic='events',
    value=event_data
)

# ClickHouse Kafka engine
CREATE TABLE events_kafka
(
    event_id UUID,
    user_id UUID,
    event_type String,
    properties JSON
) ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092,kafka-2:9092',
  kafka_topic_list = 'events',
  kafka_group_name = 'clickhouse_consumer',
  kafka_format = 'JSONEachRow';

-- Materialized view to consume
CREATE MATERIALIZED VIEW events_mv
ENGINE = MergeTree()
AS SELECT * FROM events_kafka;
```

**4. Advanced Caching:**

```python
# Multi-layer caching
from cachetools import TTLCache
from redis import Redis

# L1: In-memory cache (fastest)
l1_cache = TTLCache(maxsize=1000, ttl=60)

# L2: Redis cache (fast)
l2_cache = Redis(host='redis', port=6379)

# L3: ClickHouse (source of truth)

async def get_cached_query(query: str):
    # L1: In-memory
    if query in l1_cache:
        return l1_cache[query]

    # L2: Redis
    cached = l2_cache.get(f"query:{hash(query)}")
    if cached:
        l1_cache[query] = cached
        return cached

    # L3: ClickHouse
    result = await clickhouse.execute(query)

    # Cache in L2 and L1
    l2_cache.setex(f"query:{hash(query)}", 300, result)
    l1_cache[query] = result

    return result
```

### Capacity

- **Users:** 100,000+ concurrent
- **Queries/minute:** 100,000+
- **Data:** 1 PB+
- **Uptime:** 99.99% (enterprise-grade)
- **Cost:** $5,000-10,000/month

---

## Scaling Strategies

### 1. Horizontal > Vertical

**Horizontal scaling (add nodes):**
- Better reliability (no single point of failure)
- Linear cost scaling
- Easier to replace failed nodes

**Vertical scaling (bigger servers):**
- Diminishing returns (cost grows faster than performance)
- Single point of failure
- Expensive upgrades

### 2. Database Sharding

**When to shard:**
- Single node can't handle load
- Data too large for one node
- Queries too slow even with indexes

**Sharding strategies:**
- Hash-based: `cityHash64(user_id) % num_shards`
- Range-based: Date ranges, user ID ranges
- Geographic: Shard by region

### 3. Caching Hierarchy

```
┌─────────────┐
│   Browser   │ ← L0: Browser cache
└──────┬──────┘
       │
┌──────▼──────┐
│    CDN      │ ← L1: Edge cache (Cloudflare)
└──────┬──────┘
       │
┌──────▼──────┐
│   Redis     │ ← L2: Application cache
└──────┬──────┘
       │
┌──────▼──────┐
│ ClickHouse  │ ← L3: Database (source)
└──────────────┘
```

### 4. Async Everything

```python
# Synchronous (blocking)
def sync_query(query: str):
    result = clickhouse.execute(query)
    return result

# Asynchronous (non-blocking)
async def async_query(query: str):
    result = await clickhouse.execute(query)
    return result

# Process multiple queries concurrently
async def batch_queries(queries: list[str]):
    results = await asyncio.gather(*[
        async_query(q) for q in queries
    ])
    return results
```

### 5. Multi-Region

**Benefits:**
- Low latency (users connect to nearest region)
- High availability (regional failure doesn't affect all users)
- Data sovereignty (compliance requirements)

**Challenges:**
- Cross-region data consistency
- Higher infrastructure costs
- Complex deployment and monitoring

---

## Cost Optimization at Scale

### 1. Right-Size Resources

**Don't overprovision:**

```python
# Use Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi
  minReplicas: 2
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale at 70%, not 50%
```

### 2. Tiered Storage

**Hot, warm, cold data:**

```sql
-- Hot data (last 7 days): NVMe SSD
CREATE TABLE events_hot (...) ENGINE = MergeTree()
SETTINGS storage_policy = hot_nvme;

-- Warm data (last 30 days): Standard SSD
CREATE TABLE events_warm (...) ENGINE = MergeTree()
SETTINGS storage_policy = warm_ssd;

-- Cold data (older than 30 days): Object storage
CREATE TABLE events_cold (...) ENGINE = MergeTree()
SETTINGS storage_policy = cold_s3;
```

### 3. Spot Instances

**Use spot instances for non-critical workloads:**

```yaml
# EKS node group with spot instances
node_groups:
  - name: spot-workers
    instance_type: c5.4xlarge
    spot: true  # Up to 90% cheaper
    min_size: 5
    max_size: 50
```

### 4. Query Optimization

**Reduce computation:**

```sql
-- Bad: Full table scan
SELECT * FROM events;

-- Better: Filter by date
SELECT * FROM events
WHERE timestamp >= now() - INTERVAL 7 DAY;

-- Best: Filter by index + date
SELECT * FROM events
WHERE user_id = %(user_id)s
  AND timestamp >= now() - INTERVAL 7 DAY;
```

---

## Migration Path

### From Phase 1 to Phase 2

1. **Add worker nodes** → `microk8s add-node`
2. **Enable replication** → Update ClickHouse config
3. **Load balancer** → Cloudflare already handles this
4. **Monitor** → Update Grafana dashboards
5. **Test failover** → Simulate node failure

### From Phase 2 to Phase 3

1. **Create regional clusters** → Deploy K8s in multiple regions
2. **Database sharding** → Configure ClickHouse sharding
3. **Add Redis** → Deploy Redis cluster
4. **Update DNS** → Route traffic to nearest region
5. **Test latency** → Ensure < 100ms cross-region

### From Phase 3 to Phase 4

1. **Migrate to EKS** → `eksctl create cluster`
2. **ClickHouse Cloud** → Migrate to managed service
3. **Add Kafka** → Deploy Kafka cluster
4. **Update pipelines** → Use Kafka instead of HTTP
5. **Enterprise monitoring** → Datadog, New Relic, or similar

---

## Lessons Learned

### 1. Start Simple, Scale When Needed

Don't overengineer. Start with single-node, scale when you need to.

### 2. Horizontal > Vertical

Add nodes, not bigger servers. Better reliability, linear cost scaling.

### 3. Database is the Bottleneck

Invest in database sharding and caching. Nothing else matters if DB can't keep up.

### 4. Caching is Magic

Multi-layer caching gives 10-100x performance improvements.

### 5. Monitor and Measure

You can't scale what you don't measure. Track metrics at every phase.

---

## Scaling Checklist

Use this checklist to prepare for scaling:

**Infrastructure:**
- [ ] Load balancer configured
- [ ] Multi-node cluster ready
- [ ] Auto-scaling enabled
- [ ] Regional deployment planned

**Database:**
- [ ] Replication configured
- [ ] Sharding strategy defined
- [ ] Backup strategy (multi-region)
- [ ] Migration path documented

**Application:**
- [ ] Stateless design (no session affinity)
- [ ] Async operations
- [ ] Connection pooling
- [ ] Rate limiting

**Monitoring:**
- [ ] Multi-region dashboards
- [ ] Distributed tracing
- [ ] Log aggregation (Loki)
- [ ] Alerting for all regions

**Cost:**
- [ ] Right-sizing strategy
- [ ] Tiered storage
- [ ] Spot instances (where safe)
- [ ] Cost alerts configured

---

## Conclusion

Scaling is a journey, not a destination.

At AI Data Labs, we built for scale from day one:
- Start small ($74/month)
- Scale horizontally (add nodes)
- Database sharding (ClickHouse)
- Caching hierarchy (multi-layer)
- Multi-region deployment (global)

From 100 users to 100,000+.

Same codebase, same architecture.

Scale as you grow. Don't rewrite everything.

---

**Want to learn more?**

- Check our [cost optimization](/blog/cost-optimization-74-per-month)
- Learn about our [tech stack](/blog/tech-stack-architecture)
- See our [infrastructure code](https://github.com/duet-company/infrastructure-config)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This is the final post in our Startup to Enterprise Series. Thank you for reading!*
