# Operations Skill

Infrastructure monitoring and operations automation agent skill.

## 🎯 Purpose

Automates infrastructure operations including monitoring, alerting, auto-scaling, health checks, and self-healing for the AI Data Labs platform.

## 🚀 Usage

```bash
# Via OpenClaw
@duyetbot Check system health and auto-scale if needed

# Direct invocation
ops-skill "Alert: High CPU usage on backend service"
```

## 📚 Dependencies

- Prometheus metrics
- Grafana dashboards
- Kubernetes API
- Cloud provider CLI (DigitalOcean, AWS, GCP)
- LLM provider (Claude, GPT-4, or GLM-5)
- Alert notification systems

## 🔧 Configuration

### Environment Variables

```bash
# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
ALERT_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK

# Kubernetes
KUBECONFIG=~/.kube/config
NAMESPACE=ai-data-labs

# Cloud Provider
CLOUD_PROVIDER=digitalocean|aws|gcp
CLOUD_API_KEY=***

# Auto-scaling
AUTO_SCALE_ENABLED=true
SCALE_UP_THRESHOLD=80
SCALE_DOWN_THRESHOLD=30
MIN_REPLICAS=2
MAX_REPLICAS=10

# Self-healing
SELF_HEAL_ENABLED=true
HEALTH_CHECK_INTERVAL=30s
RESTART_THRESHOLD=3
REPLACEMENT_THRESHOLD=5

# LLM
LLM_PROVIDER=claude|openai|zai
LLM_MODEL=claude-3-opus
LLM_API_KEY=***

# Alerting
ALERT_ENABLED=true
ALERT_COOLDOWN=5m
ESCALATION_HOURS=1
```

### Skill Configuration

```yaml
operations:
  monitoring:
    prometheus: ${PROMETHEUS_URL}
    grafana: ${GRAFANA_URL}
    alert_webhook: ${ALERT_WEBHOOK}
  
  kubernetes:
    config: ${KUBECONFIG}
    namespace: ${NAMESPACE}
  
  auto_scaling:
    enabled: ${AUTO_SCALE_ENABLED}
    scale_up_threshold: ${SCALE_UP_THRESHOLD}
    scale_down_threshold: ${SCALE_DOWN_THRESHOLD}
    min_replicas: ${MIN_REPLICAS}
    max_replicas: ${MAX_REPLICAS}
  
  self_healing:
    enabled: ${SELF_HEAL_ENABLED}
    health_check_interval: ${HEALTH_CHECK_INTERVAL}
    restart_threshold: ${RESTART_THRESHOLD}
    replacement_threshold: ${REPLACEMENT_THRESHOLD}
  
  cloud:
    provider: ${CLOUD_PROVIDER}
    api_key: ${CLOUD_API_KEY}
  
  llm:
    provider: ${LLM_PROVIDER}
    model: ${LLM_MODEL}
    api_key: ${LLM_API_KEY}
  
  alerting:
    enabled: ${ALERT_ENABLED}
    cooldown: ${ALERT_COOLDOWN}
    escalation_hours: ${ESCALATION_HOURS}
```

## 📖 Examples

### High CPU Alert

```markdown
Alert: "Backend service CPU at 85% for 5 minutes"

Automatic Actions Taken:

1. Check current state:
   - Service: backend
   - CPU: 85%
   - Replicas: 3
   - Status: Degraded

2. Analyze cause:
   - Query: High query volume
   - Duration: 15 minutes
   - Impact: Response time +300ms

3. Auto-scale response:
   - Decision: Scale up
   - New replicas: 5
   - Reason: Sustained high CPU

4. Post-scale verification:
   - CPU after 2 min: 45%
   - Response time: Back to normal
   - Status: Healthy

5. Notification:
   - Alert cleared
   - Team notified of scale event
   - Dashboard link provided

Resolution: Auto-scaled from 3 to 5 replicas
Time to resolution: 3 minutes
```

### Database Connection Failure

```markdown
Alert: "ClickHouse database connection failed (3 attempts)"

Automatic Actions Taken:

1. Immediate diagnosis:
   - Service: clickhouse
   - Status: Not responding
   - Replicas: 2/2 unhealthy
   - Last successful: 2 hours ago

2. Root cause analysis:
   - Pods status: CrashLoopBackOff
   - Logs: Out of memory
   - Cause: Query memory leak

3. Self-healing response:
   - Action 1: Restart pods
   - Action 2: Increase memory limit
   - Action 3: Scale to 3 replicas

4. Verification:
   - Pods: 3/3 healthy
   - Connection: Restored
   - Performance: Normal

5. Investigation:
   - Created incident ticket
   - Escalated to engineering
   - Monitoring query patterns
   - Scheduled review

Resolution: Self-healed via restart and scale
Time to resolution: 8 minutes
Incident: INC-2026-02-16-001
```

### Disk Space Warning

```markdown
Alert: "Database disk usage at 85%"

Automatic Actions Taken:

1. Check storage:
   - Path: /var/lib/clickhouse
   - Usage: 850GB / 1TB
   - Growth rate: 10GB/day
   - Est. full: 15 days

2. Cleanup options:
   - Drop old partitions: Yes
   - Compress data: Consider
   - Expand storage: Planned

3. Automated actions:
   - Dropped partitions older than 90 days
   - Freed space: 200GB
   - New usage: 65%

4. Prevention:
   - Updated retention policy
   - Scheduled daily cleanup
   - Set alert threshold to 70%

5. Team notification:
   - Alert cleared
   - Cleanup summary sent
   - Future action plan provided

Resolution: Automated cleanup freed 200GB
Time to resolution: 5 minutes
```

## 🐛 Troubleshooting

### Issue: False positive alerts

**Possible causes:**
- Thresholds too aggressive
- Temporary traffic spikes
- Monitoring lag
- Metric collection issues

**Solutions:**
1. Review alert history: `ops-skill --alert-history`
2. Adjust thresholds: `ops-skill --update-threshold`
3. Add cooldown period: Already configured (5m)
4. Filter by duration: Require sustained duration

### Issue: Auto-scaling thrashing

**Possible causes:**
- Scale up/down thresholds too close
- Health check interval too short
- Load not stabilized
- Application startup time

**Solutions:**
1. Widen thresholds: e.g., 80% → 85%, 30% → 25%
2. Increase cooldown: 5m → 15m
3. Check application startup: Ensure pods ready before considering
4. Monitor scale events: `ops-skill --scale-history`

### Issue: Self-healing loops

**Possible causes:**
- Underlying issue not fixed
- Health check incorrect
- Restart not sufficient
- Configuration error

**Solutions:**
1. Check restart threshold: Limit consecutive restarts
2. Validate health checks: Ensure they're accurate
3. Replace instead of restart: After threshold reached
4. Create incident: Escalate if loop continues

## 📊 Health Checks

### Service Health Matrix

| Service | Check Type | Frequency | Threshold | Action |
|----------|------------|-----------|-----------|---------|
| Backend | HTTP /health | 30s | 200 OK → None |
| Frontend | HTTP /health | 30s | 200 OK → None |
| ClickHouse | TCP 8123 | 30s | Open → Scale |
| PostgreSQL | TCP 5432 | 30s | Open → Scale |
| Redis | TCP 6379 | 30s | Open → None |

### Auto-scaling Rules

```yaml
scale_up:
  cpu_usage: > 80%
  duration: > 5 minutes
  action: +1 replica
  max: 10 replicas

scale_down:
  cpu_usage: < 30%
  duration: > 15 minutes
  action: -1 replica
  min: 2 replicas

scale_out:
  error_rate: > 10%
  duration: > 2 minutes
  action: +2 replicas
  immediate: true
```

## 🔗 Related Skills

- [Query Skill](./query-skill.md) - Performance monitoring
- [Design Skill](./design-skill.md) - Infrastructure provisioning
- [Support Skill](./support-skill.md) - Issue escalation

## 📖 References

- [Infrastructure Guide](https://github.com/duet-company/infrastructure)
- [Monitoring Setup](https://github.com/duet-company/infrastructure/blob/main/monitoring/README.md)
- [Kubernetes Operations](https://github.com/duet-company/infrastructure/blob/main/kubernetes/README.md)
- [Incident Response](https://github.com/duet-company/playbook/blob/main/operations/incident-response.md)

---

**Skill Version:** 1.0.0
**Last Updated:** 2026-02-16
**Maintainer:** Duet Company AI Team
