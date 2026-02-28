# AI Data Labs Tech Stack: An Architecture Overview

**Published:** February 21, 2026
**Reading Time:** 12 minutes
**Tags:** #architecture #tech-stack #engineering #infrastructure

---

## TL;DR

At AI Data Labs, we're building a real-time analytics platform powered by AI. Here's our tech stack:

- **Database:** ClickHouse (analytics) + PostgreSQL (metadata)
- **Orchestration:** Kubernetes (microk8s)
- **Backend:** FastAPI (Python)
- **Frontend:** React + TypeScript
- **AI:** Multi-model LLM (Claude, GPT-4, GLM-5)
- **Monitoring:** Prometheus + Grafana
- **Infrastructure:** Terraform + DigitalOcean
- **Cost:** $74/month for initial production deployment

Here's why we chose each component and how they fit together.

---

## The Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users & Clients                        │
│                  (Web Dashboard, API, Chat)                   │
└──────────────────────┬────────────────────────────────────────┘
                       │ HTTPS (Cloudflare)
                       │
┌──────────────────────▼────────────────────────────────────────┐
│                     DigitalOcean Droplet                        │
│                   4 vCPUs, 8 GB RAM, 160 GB SSD                  │
└──────────────────────┬────────────────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │   microk8s       │
              │  (Kubernetes)    │
              └────────┬─────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────────┐  ┌────▼─────────┐  ┌────▼─────────┐
│   NGINX     │  │   FastAPI    │  │   React      │
│  Ingress    │  │   Backend    │  │  Frontend    │
└─────────────┘  └──────┬───────┘  └─────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────────┐  ┌────▼─────────┐  ┌────▼─────────┐
│  ClickHouse│  │  PostgreSQL  │  │  AI Agents   │
│  (Analytics)│  │  (Metadata) │  │  (LLM API)   │
└─────────────┘  └─────────────┘  └─────────────┘
                       │
              ┌────────▼─────────┐
              │  Prometheus +    │
              │     Grafana      │
              │   (Monitoring)   │
              └──────────────────┘
```

---

## Why This Stack?

### Design Principles

We chose our tech stack based on these principles:

1. **Performance first** - Queries must complete in < 1 second
2. **Cost-effective** - Target: <$100/TB/month
3. **Open source** - No vendor lock-in, community support
4. **Simple** - Minimal complexity for a small team
5. **Scalable** - Can grow to 10x current workload
6. **AI-native** - Built for AI workloads, not bolted on

---

## Component Deep Dives

### 1. ClickHouse - Analytics Database

**What it is:**
Columnar database for real-time analytics. 100-1000x faster than traditional databases for analytical queries.

**Why we chose it:**

- **Blazing fast** - Queries in milliseconds on billions of rows
- **Incredible compression** - 10-100x better than PostgreSQL
- **SQL native** - No new query language to learn
- **Open source** - Apache 2.0 license, self-hosted
- **Battle-tested** - Used by Uber, Cloudflare, eBay

**Our use cases:**
- Event tracking (page views, clicks, purchases)
- Real-time analytics dashboards
- AI query agent results
- Customer analytics and reporting

**Example schema:**
```sql
CREATE TABLE customer_events (
    event_id UUID,
    user_id UUID,
    event_type LowCardinality(String),
    timestamp DateTime64(3),
    properties JSON,
    revenue Decimal(18, 2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp)
SETTINGS index_granularity = 8192;
```

**Performance:**
- 1 billion rows: 120ms average query time
- Compression: 92% (100GB raw → 8GB on disk)
- Ingestion rate: 1M+ events/second

### 2. PostgreSQL - Metadata Database

**What it is:**
Relational database for transactional data and metadata.

**Why we chose it:**

- **Mature and reliable** - 30+ years of production use
- **ACID compliant** - Safe for critical data
- **JSON support** - Flexible schema for metadata
- **Great tooling** - ORMs, migrations, monitoring

**Our use cases:**
- User authentication and sessions
- Database schemas and table definitions
- Query history and caching
- Agent conversation memory
- Billing and subscriptions

**Example schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    plan VARCHAR(50) DEFAULT 'starter'
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    agent_type VARCHAR(50),
    messages JSONB,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Kubernetes (microk8s) - Orchestration

**What it is:**
Container orchestration platform. microk8s is Canonical's lightweight distribution.

**Why we chose it:**

- **Single-node simplicity** - Runs on one VPS, scales later
- **Easy deployment** - `kubectl apply -f deployment.yaml`
- **Self-healing** - Automatically restarts failed pods
- **Built-in load balancing** - Services handle distribution
- **Addons included** - DNS, storage, ingress, metrics

**Our deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: ghcr.io/duet-company/fastapi:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
```

### 4. FastAPI - Backend API

**What it is:**
Modern Python web framework for building APIs.

**Why we chose it:**

- **Type hints** - Automatic data validation with Pydantic
- **Async support** - Fast I/O, high concurrency
- **Automatic docs** - Swagger UI out of the box
- **Fast** - Comparable to Node.js and Go
- **Python ecosystem** - AI libraries (langchain, openai)

**Our endpoints:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI Data Labs API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    session_id: str

@app.post("/api/v1/query")
async def execute_query(request: QueryRequest):
    # Parse natural language query
    parsed = query_agent.parse(request.query)

    # Generate SQL
    sql = sql_generator.generate(parsed)

    # Execute on ClickHouse
    result = clickhouse.execute(sql)

    # Format response
    return {
        "query": request.query,
        "sql": sql,
        "data": result,
        "execution_time_ms": result.time_ms
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5. React + TypeScript - Frontend

**What it is:**
JavaScript library for building user interfaces with TypeScript for type safety.

**Why we chose it:**

- **Component-based** - Reusable UI components
- **Type safety** - Catches errors at compile time
- **Great ecosystem** - Vite, Tailwind, Chakra UI
- **Real-time updates** - WebSocket integration
- **Mobile-friendly** - Responsive design

**Our dashboard:**
```tsx
import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import { useQuery } from '@tanstack/react-query';

export function Dashboard() {
  const [timeRange, setTimeRange] = useState('7d');

  const { data, isLoading, error } = useQuery({
    queryKey: ['revenue', timeRange],
    queryFn: () => fetch(`/api/v1/analytics/revenue?range=${timeRange}`).then(r => r.json())
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading data</div>;

  return (
    <div>
      <h1>Revenue Dashboard</h1>
      <Line data={data.chartData} options={data.chartOptions} />
    </div>
  );
}
```

### 6. AI Agents - Multi-Model LLM

**What it is:**
Large Language Models for natural language understanding and code generation.

**Why we use multiple models:**

- **Claude (Anthropic)** - Best for code generation, SQL, and complex reasoning
- **GPT-4 (OpenAI)** - Great for conversation, summarization
- **GLM-5** - Fast and cost-effective for simple tasks

**Model selection strategy:**
```python
def choose_model(task):
    if task == "sql_generation":
        return "claude-3-opus"  # Best for code
    elif task == "summarization":
        return "glm-4"  # Fast and cheap
    elif task == "conversation":
        return "gpt-4"  # Great for chat
    else:
        return "claude-3-opus"  # Default
```

### 7. Prometheus + Grafana - Monitoring

**What they are:**
Prometheus for metrics collection, Grafana for visualization.

**Why we chose them:**

- **Cloud-native** - Built for Kubernetes
- **Flexible queries** - Powerful query language (PromQL)
- **Beautiful dashboards** - Grafana is industry standard
- **Alerting** - Built-in alerting system
- **Open source** - No cost, community support

**Key metrics we track:**
```yaml
# Application metrics
app_http_requests_total
app_query_duration_seconds
app_llm_tokens_used_total

# Infrastructure metrics
node_cpu_usage_percent
node_memory_usage_percent
container_cpu_usage_seconds_total

# Business metrics
active_users_count
queries_per_minute
revenue_per_hour
```

### 8. Terraform - Infrastructure as Code

**What it is:**
Tool for provisioning and managing infrastructure.

**Why we chose it:**

- **Declarative** - Define desired state, not steps
- **Version control** - Infrastructure in Git
- **Multi-cloud** - Works with AWS, GCP, Azure, DigitalOcean
- **State management** - Tracks resources automatically

**Our Terraform:**
```hcl
resource "digitalocean_droplet" "aidatalabs" {
  name  = "aidatalabs-prod"
  image = "ubuntu-22-04-x64"
  size  = "s-4vcpu-8gb"
  region = "sgp1"

  ssh_keys = [data.digitalocean_ssh_key.aidatalabs.id]

  user_data = file("${path.module}/cloud-init.yaml")
}
```

---

## Data Flow Examples

### Example 1: Natural Language Query

```
User: "Show me revenue by region over the past 7 days"
  │
  ▼
[React Frontend] - Captures query
  │
  ▼
[FastAPI Backend] - Receives API request
  │
  ▼
[Query Agent (Claude)] - Parses NL query
  │
  ▼
[SQL Generator] - Generates ClickHouse SQL
  │
  ▼
[ClickHouse] - Executes query
  │
  ▼
[FastAPI Backend] - Formats results
  │
  ▼
[React Frontend] - Displays chart
```

### Example 2: Event Ingestion

```
[Customer App] - Sends event
  │
  ▼
[FastAPI Backend] - Receives event
  │
  ├─► [PostgreSQL] - Stores metadata
  │
  ├─► [ClickHouse] - Stores for analytics
  │
  └─► [Prometheus] - Updates metrics
```

### Example 3: Infrastructure Scaling

```
[High CPU Alert] - Prometheus detects issue
  │
  ▼
[Grafana Alert] - Triggers notification
  │
  ▼
[Kubernetes HPA] - Scales pods automatically
  │
  ▼
[DigitalOcean] - Additional worker nodes (if needed)
```

---

## Security Considerations

### Network Security

- **HTTPS only** - Cloudflare for TLS termination
- **Firewall rules** - Only necessary ports open
- **Private networking** - Services communicate internally
- **Secrets management** - Environment variables, Kubernetes secrets

### Application Security

```python
# Input validation with Pydantic
class UserInput(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=1000)

# SQL injection prevention with parameterized queries
sql = "SELECT * FROM events WHERE user_id = %(user_id)s"
clickhouse.execute(sql, {"user_id": user_id})

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/query")
@limiter.limit("100/minute")
async def execute_query(request: Request, data: UserInput):
    ...
```

### Data Security

- **Encryption at rest** - Full disk encryption
- **Backups** - Daily ClickHouse snapshots to object storage
- **Access logs** - All queries and access logged
- **GDPR compliant** - User data deletion on request

---

## Cost Breakdown

### Monthly Costs (Initial Deployment)

| Item | Cost | Notes |
|------|------|-------|
| DigitalOcean Droplet (4 vCPU, 8 GB RAM) | $48 | Main VPS |
| Additional bandwidth (1 TB) | $10 | Included in droplet |
| Cloudflare (Pro plan) | $20 | CDN, WAF, DDoS protection |
| LLM API (10M tokens/month) | $100 | Estimated |
| **Total** | **$178** | Per month |

### Per Customer Costs

| Item | Cost |
|------|------|
| Storage (1 TB data) | $8 |
| Compute (queries) | $15 |
| LLM API | $20 |
| Support | $5 |
| Total | **$48/month** |

**Gross margin:** 52% at $999/month starter price

---

## Scalability Strategy

### Phase 1: Single Node (Months 1-3)

- **Capacity:** 100 concurrent users, 1 TB data
- **Infrastructure:** 1 VPS, microk8s
- **Cost:** $178/month

### Phase 2: Multi-Node (Months 4-6)

- **Capacity:** 1,000 concurrent users, 10 TB data
- **Infrastructure:** 3 VPS (1 control, 2 workers), Load balancer
- **Cost:** $300-400/month

### Phase 3: Cloud-Native (Months 7-12)

- **Capacity:** 10,000 concurrent users, 100 TB data
- **Infrastructure:** Managed K8s (EKS/GKE), Object storage (S3)
- **Cost:** $1,500-2,500/month

---

## Lessons Learned

### 1. Start Simple

We didn't start with 10 microservices. We started with 1 monolithic service and split as needed.

### 2. Measure Everything

We track 100+ metrics. Without data, we're flying blind.

### 3. Automate Early

Terraform, CI/CD, automated tests. Manual processes don't scale.

### 4. Choose Wisely

Every component must justify its existence. If it doesn't add value, remove it.

### 5. Document as You Go

We write documentation alongside code. No "TODO: add docs" comments.

---

## Future Improvements

On our roadmap:

- **Event streaming** - Kafka for real-time data pipelines
- **Vector database** - For semantic search and RAG
- **Feature flags** - For A/B testing and gradual rollouts
- **Service mesh** - Istio or Linkerd for microservices
- **Multi-region** - Global deployment for low latency

---

## Conclusion

Building AI Data Labs requires making hundreds of technology decisions. Our stack balances:

- **Performance** - Queries in milliseconds
- **Cost** - <$200/month initial deployment
- **Complexity** - Manageable for a small team
- **Scalability** - Can grow to 10x current load
- **Reliability** - 99.9% uptime target

The best tech stack is the one that lets you ship fast and iterate faster.

We're building for the long term, but starting small.

---

**Want to dive deeper?**

- Read our [ClickHouse deep dive](/blog/clickhouse-why-we-chose-it)
- Learn about our [AI agent architecture](/blog/building-ai-agents-lessons)
- Check our [open source code](https://github.com/duet-company)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Architecture Series. Next up: "Data Modeling in ClickHouse: Patterns and Anti-Patterns."*
