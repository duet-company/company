# Design Skill

Platform design and infrastructure automation agent skill.

## 🎯 Purpose

Automates data platform design from natural language requirements. Includes schema design, infrastructure provisioning, dashboard creation, and configuration management.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Design an e-commerce analytics platform with real-time dashboards

# Direct invocation
design-skill "I need customer behavior analytics"
```

## 📚 Dependencies

- Kubernetes client (kubectl)
- Terraform CLI
- ClickHouse client
- LLM provider (Claude, GPT-4, or GLM-5)
- Template repository access

## 🔧 Configuration

### Environment Variables

```bash
# Kubernetes
KUBECONFIG=~/.kube/config
KUBERNETES_NAMESPACE=ai-data-labs

# Terraform
TERRAFORM_DIR=/tmp/terraform
TERRAFORM_STATE=s3://duet-company-terraform/state

# Infrastructure
CLOUD_PROVIDER=digitalocean|aws|gcp
REGION=sgp1
NODE_SIZE=c-8vcpu-16gb
STORAGE_SIZE=100GB

# Database
CLICKHOUSE_HOST=clickhouse.ai-data-labs
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=***

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***

# Design settings
AUTO_APPLY=false
DRY_RUN=true
REQUIRE_APPROVAL=true
```

### Skill Configuration

```yaml
design:
  infrastructure:
    provider: ${CLOUD_PROVIDER}
    region: ${REGION}
    kubernetes:
      enabled: true
      replicas: 3
  
  database:
    type: clickhouse
    host: ${CLICKHOUSE_HOST}
    port: ${CLICKHOUSE_PORT}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  automation:
    auto_apply: ${AUTO_APPLY}
    dry_run: ${DRY_RUN}
    require_approval: ${REQUIRE_APPROVAL}
```

## 📖 Examples

### E-commerce Platform Design

```markdown
Requirement:
"I need an e-commerce analytics platform with real-time dashboards"

Generated Design:

1. Schema Design:
   - orders table (clickstream events)
   - customers table (customer profiles)
   - products table (product catalog)
   - sessions table (user sessions)

2. Infrastructure:
   - ClickHouse cluster (3 nodes)
   - Redis cache (for real-time lookups)
   - Grafana dashboards
   - Kubernetes deployment

3. Data Pipelines:
   - Kafka topics for event streaming
   - ClickHouse materialized views
   - Scheduled aggregations

4. Dashboards:
   - Revenue Overview (real-time)
   - Product Performance
   - Customer Behavior
   - Conversion Funnel
```

### Customer Analytics Platform

```markdown
Requirement:
"Build a customer behavior analytics platform with cohort analysis"

Generated Design:

1. Schema:
   - events table (user events)
   - sessions table (web sessions)
   - cohorts table (cohort assignments)
   - metrics table (precomputed metrics)

2. Infrastructure:
   - ClickHouse for events
   - PostgreSQL for metadata
   - Redis for session state
   - Airflow for pipelines

3. Analytics:
   - Cohort retention analysis
   - Funnel conversion tracking
   - Session attribution
   - Behavioral segmentation
```

## 🐛 Troubleshooting

### Issue: Infrastructure provisioning fails

**Possible causes:**
- Insufficient cloud resources
- Invalid Terraform state
- Network connectivity issues
- Missing credentials

**Solutions:**
1. Check cloud quota: `digitaloceanctl account show`
2. Validate Terraform: `terraform validate`
3. Check credentials: `terraform login`
4. Review error logs: `tail -f /var/log/design-skill.log`

### Issue: Schema design conflicts

**Possible causes:**
- Existing tables with same name
- Data type mismatches
- Constraint violations
- Partitioning conflicts

**Solutions:**
1. Check existing schema: `design-skill --show-schema`
2. Use table prefixes for different domains
3. Validate with dry run: `design-skill --dry-run`
4. Review conflict resolution strategy

### Issue: Dashboard not rendering

**Possible causes:**
- Data not available
- Query too slow
- Incorrect query syntax
- Missing fields

**Solutions:**
1. Check data ingestion: `design-skill --check-data`
2. Optimize query: `design-skill --optimize`
3. Validate SQL: `design-skill --validate-sql`
4. Refresh schema metadata

## 📊 Template Repository

### Available Templates

1. **E-commerce Analytics**
   - Events tracking
   - Revenue analytics
   - Product performance
   - Customer insights

2. **SaaS Metrics**
   - Subscription tracking
   - Churn analysis
   - MRR monitoring
   - Funnel analytics

3. **Real-time Dashboard**
   - Streaming metrics
   - Live counters
   - Time-series charts
   - Alert setup

4. **Customer 360**
   - Profile aggregation
   - Behavior tracking
   - Lifetime value
   - Segmentation

## 🔗 Related Skills

- [Query Skill](./query-skill.md) - SQL generation
- [Data Skill](./data-skill.md) - Pipeline management
- [Ops Skill](./ops-skill.md) - Infrastructure monitoring

## 📖 References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform Guide](https://developer.hashicorp.com/terraform)
- [ClickHouse Best Practices](https://clickhouse.com/docs/en/best-practices/)
- [Infrastructure Design](https://github.com/duet-company/infrastructure)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company AI Team
