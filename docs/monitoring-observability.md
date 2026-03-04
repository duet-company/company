# Monitoring & Observability

AI Data Labs platform monitoring stack using Prometheus, Grafana, and Alertmanager.

## Components

### Prometheus
Collects metrics from all platform components:
- API request metrics (latency, throughput, errors)
- Agent metrics (active agents, request rates, errors)
- Database metrics (connections, query latency)
- System metrics (CPU, memory, disk)

### Grafana
Visualization dashboard for all platform metrics:
- Request rate and latency
- Error rates and agent status
- System resource usage
- Database performance

### Alertmanager (optional)
Alert routing and notification for critical issues (to be integrated)

## Setup

### Prerequisites

- Kubernetes cluster (microk8s)
- kubectl configured
- Helm (optional)

### Deployment

1. Apply all manifests in `infrastructure/kubernetes/manifests/monitoring/`:

```bash
kubectl apply -f infrastructure/kubernetes/manifests/monitoring/
```

2. Verify deployments:

```bash
kubectl get pods -n monitoring
kubectl get services -n monitoring
```

3. Access Grafana:

```bash
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

Then open http://localhost:3000 in your browser.
Default credentials: admin/admin

4. Access Prometheus:

```bash
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
```

Then open http://localhost:9090 in your browser.

## Configuration

### Backend Metrics

The backend automatically exposes metrics at `/metrics` endpoint. Ensure that:

1. Prometheus can reach the backend service on port 8000
2. The backend has the `prometheus-client` library installed
3. The MetricsMiddleware is enabled in main.py

Metrics collected:
- `aidatalabs_api_requests_total` - Total API requests by method, endpoint, status
- `aidatalabs_api_request_duration_seconds` - Request duration histogram
- `aidatalabs_api_errors_total` - API errors by method, endpoint, type
- `aidatalabs_agents_active` - Active agent count by type
- `aidatalabs_agent_requests_total` - Agent operations count
- `aidatalabs_agent_request_duration_seconds` - Agent operation latency
- `aidatalabs_db_queries_total` - Database queries by type and success
- `aidatalabs_db_query_duration_seconds` - Query latency histogram
- `aidatalabs_system_memory_bytes` - System memory usage
- `aidatalabs_system_cpu_percent` - CPU usage
- `aidatalabs_system_disk_bytes` - Disk usage by mountpoint

### Alerting Rules

Default alerts configured in `05-alerts.yaml`:

- **HighErrorRate**: Error rate > 5% for 2 minutes
- **HighLatency**: 95th percentile latency > 1s for 5 minutes
- **AgentDown**: No active agents for 3 minutes
- **HighMemoryUsage**: Memory usage > 90% for 5 minutes
- **HighCPUUsage**: CPU usage > 80% for 5 minutes

To receive alerts, configure Alertmanager and notification channels (email, Slack, etc.).

## Dashboard

The provided Grafana dashboard includes:
- Request rate and latency graphs
- Active agents count
- Error rate statistic
- System memory usage
- Database query latency

## Health Checks

Enhanced health endpoint available at `/health` includes:
- API and auth status
- Database connectivity status (when integrated)
- System metrics snapshot

## Operational Runbooks

### Incident Response

1. Check Grafana dashboard for system overview
2. Investigate high error rates or latency:
   - Review recent deployments
   - Check agent logs
   - Verify database connectivity
3. Check Prometheus targets for scraped metrics status
4. Review logs from relevant services

### On-Call Procedures

- Check the Grafana dashboard first for any obvious spikes
- Verify that all agents are running and responsive
- Check Prometheus alerting panel for active alerts
- If database latency is high, investigate query performance and connection pool

## Maintenance

### Rotating Grafana Dashboard

Grafana dashboards are stored as ConfigMaps. To update:

1. Edit the dashboard JSON in `06-grafana-dashboard.yaml`
2. Apply the changes: `kubectl apply -f 06-grafana-dashboard.yaml`

### Metrics Retention

Prometheus retention is set to 200 hours (~8 days) by default. Adjust in the Prometheus deployment args if needed.

### Scaling

- Prometheus: Scale replicas in Deployment for HA (requires remote storage)
- Grafana: Scale horizontally as needed

## Troubleshooting

### Metrics not showing

- Verify MetricsMiddleware is enabled in backend
- Check that `/metrics` endpoint returns data
- Ensure Prometheus can reach backend service (network policies, service discovery)
- Check Prometheus targets page: http://localhost:9090/targets

### Grafana shows "No data"

- Verify Prometheus is scraping the backend
- Check that metrics names match what's in the dashboard
- Use Prometheus query interface to test metric existence

### Alerts not firing

- Check alert rules are loaded in Prometheus
- Verify alert state in Prometheus Alerts page
- Ensure Alertmanager is configured and reachable