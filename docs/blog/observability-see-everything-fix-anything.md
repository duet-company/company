# Observability at AI Data Labs: See Everything, Fix Anything

**Published:** February 21, 2026
**Reading Time:** 11 minutes
**Tags:** #observability #monitoring #debugging #engineering #performance

---

## TL;DR

Observability is how we understand our systems. At AI Data Labs, we have complete visibility:

- **Metrics** - Numerical data (CPU, memory, request rate)
- **Logs** - Structured event logs (errors, transactions)
- **Traces** - Distributed tracing (request flow across services)
- **Dashboards** - Real-time visualization (Grafana)
- **Alerts** - Proactive notifications (before users notice)
- **Debugging** - Root cause analysis (identify issues fast)

**Result:** 99.9% uptime, < 5 minute MTTR (mean time to recovery), always know what's happening.

---

## The Three Pillars of Observability

### 1. Metrics - What Happened

Numerical time-series data:

```
CPU: 45%
Memory: 62%
Requests/min: 1,234
Error rate: 0.1%
Query latency P95: 850ms
```

### 2. Logs - What Happened (Detailed)

Text records of events:

```json
{
  "timestamp": "2026-02-21T10:15:30.123Z",
  "level": "error",
  "service": "query-api",
  "request_id": "abc-123-def",
  "message": "ClickHouse query timeout",
  "query": "SELECT * FROM events WHERE ...",
  "duration_ms": 5000
}
```

### 3. Traces - How It Happened

Request flow across services:

```
User Request
  ↓ [50ms]
  → Load Balancer
  ↓ [20ms]
  → FastAPI Backend
  ↓ [100ms]
  → ClickHouse Database
  ↓ [30ms]
  → Response (200ms total)
```

---

## Metrics: Prometheus

### Setup

**Prometheus configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['fastapi:8000']
    metrics_path: '/metrics'

  - job_name: 'clickhouse'
    static_configs:
      - targets: ['clickhouse:9363']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Application Metrics

**Custom metrics in FastAPI:**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from fastapi import FastAPI
import time

app = FastAPI()

# Counter: Monotonically increasing values
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

clickhouse_queries_total = Counter(
    'clickhouse_queries_total',
    'Total ClickHouse queries',
    ['query_type', 'status']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'task']
)

# Histogram: Distributions (latency, request size)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

query_execution_duration = Histogram(
    'query_execution_duration_seconds',
    'ClickHouse query execution time',
    ['query_type']
)

# Gauge: Current values (CPU, memory, queue size)
active_connections = Gauge(
    'active_connections',
    'Active database connections'
)

buffer_size = Gauge(
    'buffer_size',
    'Event buffer size'
)

# Middleware to track requests
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Start metrics server on port 9090
start_http_server(9090)
```

### Infrastructure Metrics

**Node Exporter for system metrics:**

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100
```

### Key Metrics We Track

**Application Metrics:**
```yaml
http_requests_total
http_request_duration_seconds
clickhouse_queries_total
clickhouse_query_duration_seconds
llm_tokens_total
llm_requests_total
active_connections
buffer_size
```

**Infrastructure Metrics:**
```yaml
node_cpu_seconds_total
node_memory_MemAvailable_bytes
node_memory_MemTotal_bytes
node_filesystem_avail_bytes
node_filesystem_size_bytes
node_network_receive_bytes_total
node_network_transmit_bytes_total
container_cpu_usage_seconds_total
container_memory_usage_bytes
```

**Business Metrics:**
```yaml
active_users_total
queries_per_minute
revenue_per_hour
signups_total
subscriptions_created_total
```

---

## Logs: Structured Logging

### Structlog Setup

**JSON-structured logging:**

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
```

### Logging Best Practices

**Include context:**

```python
@app.post("/api/v1/query")
async def execute_query(request: Request, data: QueryRequest):
    request_id = generate_request_id()

    # Log with context
    logger.info(
        "query_received",
        request_id=request_id,
        user_id=data.user_id,
        query=data.query,
        user_agent=request.headers.get("user-agent")
    )

    try:
        result = await execute_clickhouse_query(data.query)
        logger.info(
            "query_completed",
            request_id=request_id,
            duration_ms=result.duration_ms,
            rows=result.row_count
        )
        return result

    except Exception as e:
        logger.error(
            "query_failed",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

**Log levels:**

```python
# Debug: Detailed diagnostics
logger.debug("cache_hit", key="user:123", value="...")

# Info: Normal operations
logger.info("query_executed", query="SELECT * FROM ...", rows=100)

# Warning: Something unusual but not broken
logger.warning(
    "slow_query",
    query="SELECT * FROM events",
    duration_ms=5000,
    threshold_ms=1000
)

# Error: Something broke
logger.error("database_connection_failed", error="Connection refused")

# Critical: Service-breaking issue
logger.critical("service_down", reason="Out of memory")
```

### Log Aggregation

**Loki for log aggregation:**

```yaml
# loki-config.yaml
server:
  http_listen_port: 3100

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: fastapi
    static_configs:
      - targets:
          - localhost
        labels:
          job: fastapi
          __path__: /var/log/fastapi/*.log
```

---

## Traces: Distributed Tracing

### OpenTelemetry Setup

**Instrument FastAPI:**

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.clickhouse import ClickHouseInstrumentor
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Set up tracing
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Export to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Instrument ClickHouse
ClickHouseInstrumentor().instrument()
```

### Span Annotations

**Add custom spans:**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.post("/api/v1/query")
async def execute_query(request: Request, data: QueryRequest):
    with tracer.start_as_current_span("execute_query") as span:
        # Add attributes to span
        span.set_attribute("query", data.query)
        span.set_attribute("user_id", data.user_id)

        # Parse query
        with tracer.start_as_current_span("parse_query") as parse_span:
            parsed = parse_natural_language(data.query)
            parse_span.set_attribute("metric", parsed.metric)
            parse_span.set_attribute("dimension", parsed.dimension)

        # Generate SQL
        with tracer.start_as_current_span("generate_sql") as sql_span:
            sql = generate_clickhouse_sql(parsed)
            sql_span.set_attribute("sql", sql)

        # Execute query
        with tracer.start_as_current_span("execute_clickhouse") as exec_span:
            result = clickhouse.execute(sql)
            exec_span.set_attribute("rows", len(result))
            exec_span.set_attribute("duration_ms", result.time_ms)

        return result
```

### Visualizing Traces

**Jaeger UI:**
- Service topology
- Request flow visualization
- Latency breakdown per service
- Error identification

---

## Dashboards: Grafana

### Dashboard Setup

**Grafana configuration:**

```yaml
# grafana-datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
```

### Key Dashboards

**1. System Overview Dashboard:**

```yaml
panels:
  - title: CPU Usage
    targets:
      - expr: 100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))
    type: graph

  - title: Memory Usage
    targets:
      - expr: 100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
    type: graph

  - title: Disk Usage
    targets:
      - expr: 100 * (1 - node_filesystem_avail_bytes / node_filesystem_size_bytes)
    type: graph
```

**2. Application Performance Dashboard:**

```yaml
panels:
  - title: Request Rate
    targets:
      - expr: rate(http_requests_total[5m])
    type: graph

  - title: Error Rate
    targets:
      - expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])
    type: graph

  - title: P95 Latency
    targets:
      - expr: histogram_quantile(0.95, http_request_duration_seconds)
    type: graph
```

**3. Business Metrics Dashboard:**

```yaml
panels:
  - title: Active Users
    targets:
      - expr: active_users_total
    type: stat

  - title: Queries Per Minute
    targets:
      - expr: rate(clickhouse_queries_total[1m])
    type: graph

  - title: Revenue Per Hour
    targets:
      - expr: rate(revenue_per_hour[1h])
    type: graph
```

---

## Alerts: Proactive Monitoring

### Alert Rules

**Prometheus alert rules:**

```yaml
# alerts.yml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m])
          /
          rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, http_request_duration_seconds) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: DatabaseDown
        expr: up{job="clickhouse"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ClickHouse is down"
          description: "ClickHouse has been down for > 1 minute"

  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: |
          100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value | humanizePercentage }}"

      - alert: HighMemoryUsage
        expr: |
          100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      - alert: DiskSpaceLow
        expr: |
          100 * (1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is {{ $value | humanizePercentage }}"
```

### Alert Routing

**Alertmanager configuration:**

```yaml
# alertmanager.yml
route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'

    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<your-pagerduty-key>'

  - name: 'slack'
    slack_configs:
      - api_url: '<your-slack-webhook-url>'
        channel: '#alerts'
        title: '{{ .Status | toUpper }}: {{ .CommonLabels.alertname }}'
```

---

## Debugging: Root Cause Analysis

### Correlating Metrics, Logs, and Traces

**Use Grafana's explore feature:**

1. **Alert triggers** → Check metrics dashboard
2. **Identify anomaly** → Look at traces for that time
3. **Find slow request** → Check logs with trace ID
4. **Identify root cause** → Fix and verify

### Example: Debugging Slow Queries

```
Alert: High P95 latency (> 1s)
  ↓
Check dashboard: Query duration increased
  ↓
Check traces: ClickHouse spans are slow
  ↓
Check logs: "Full table scan detected"
  ↓
Root cause: Query lacks WHERE clause
  ↓
Fix: Add index, optimize query
  ↓
Verify: Latency back to normal
```

### SLO Monitoring

**Service Level Objectives:**

```yaml
# Define SLOs
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: query-api
spec:
  selector:
    matchLabels:
      app: query-api
  endpoints:
  - port: web
    interval: 15s

---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: slos
spec:
  groups:
    - name: slos
      rules:
        # SLO: 99.9% success rate
        - record: slo:success_rate
          expr: |
            (
              sum(rate(http_requests_total{status_code!~"5.."}[5m]))
              /
              sum(rate(http_requests_total[5m]))
            )

        # SLO: 99.9% of requests < 1s
        - record: slo:latency
          expr: |
            (
              histogram_quantile(0.999, rate(http_request_duration_seconds_bucket[5m]))
            )
```

---

## Best Practices

### 1. Log Structured Data

JSON logs, not plain text. Parseable, searchable.

### 2. Include Context

Add request IDs, user IDs, timestamps. Correlate events.

### 3. Use Appropriate Log Levels

Debug, info, warning, error, critical. Not everything is an error.

### 4. Monitor the Right Metrics

- Leading indicators (latency, error rate)
- Lagging indicators (uptime, error count)
- Business metrics (users, revenue)

### 5. Set Meaningful Alerts

Alert on symptoms, not causes. Don't alert on everything.

### 6. Make Alerts Actionable

Every alert should have a runbook. Know what to do when it fires.

---

## Tools We Use

| Purpose | Tool | Why? |
|----------|-------|-------|
| Metrics | Prometheus | Cloud-native, powerful query language |
| Dashboards | Grafana | Beautiful, flexible, industry standard |
| Logs | Loki | Lightweight, integrates with Grafana |
| Tracing | Jaeger | Distributed tracing, request visualization |
| Instrumentation | OpenTelemetry | Standard, vendor-agnostic |
| Alerting | Alertmanager | Flexible routing, rich notifications |

---

## Lessons Learned

### 1. Observability is Not Monitoring

Monitoring tells you something is wrong. Observability helps you understand why.

### 2. Metrics + Logs + Traces = Complete Picture

Each pillar provides unique insights. Need all three.

### 3. Alert Fatigue is Real

Too many alerts = ignored alerts. Alert on symptoms, not noise.

### 4. SLOs Drive Improvements

Set SLOs, measure against them, iterate.

### 5. Debug Fast

Correlate metrics, logs, traces. Root cause analysis in minutes, not hours.

---

## Conclusion

Observability is how we sleep at night:

- **Metrics** tell us what happened
- **Logs** tell us why it happened
- **Traces** tell us how it happened
- **Dashboards** let us see everything
- **Alerts** tell us when to act

99.9% uptime. < 5 minute MTTR.

Always know what's happening.

---

**Want to learn more?**

- Check our [cost optimization](/blog/cost-optimization-74-per-month)
- Learn about our [CI/CD](/blog/development-workflow-ci-cd)
- See our [monitoring stack](https://github.com/duet-company/infrastructure-config)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Engineering Deep Dive Series. Next up: "Incident Response: How We Handle Production Issues."*
