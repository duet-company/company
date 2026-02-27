# ClickHouse Kubernetes Deployment

This directory contains Kubernetes manifests for deploying ClickHouse as the primary analytics database for AI Data Labs.

## Prerequisites

- Kubernetes cluster with microk8s (issue #4)
- Storage class `clickhouse-fast` configured (see `../storageclasses.yaml`)
- Storage class `standard` configured (for logs)
- Namespace `clickhouse` created (included in manifests)
- Ingress controller installed (optional, for external access)

## Quick Deploy

### 1. Review and Update Secrets

**IMPORTANT:** Update the secrets before deploying!

```bash
cd manifests/clickhouse
kubectl create secret generic clickhouse-secrets \
  --namespace=clickhouse \
  --from-literal=CH_PASSWORD_DEFAULT='your-default-password' \
  --from-literal=CH_PASSWORD_READONLY='your-readonly-password' \
  --from-literal=CH_PASSWORD_ADMIN='your-admin-password' \
  --dry-run=client -o yaml | kubectl apply -f -
```

For production, use strong, randomly generated passwords.

### 2. Deploy ClickHouse

Apply all manifests in order:

```bash
# Create namespace (if not already exists)
kubectl apply -f 01-namespace.yaml

# Create ConfigMap with ClickHouse configuration
kubectl apply -f 02-configmap.yaml

# Create secrets (skip if already created)
kubectl apply -f 03-secrets.yaml

# Create PersistentVolumeClaims
kubectl apply -f 04-pvc.yaml

# Create Service (headless)
kubectl apply -f 05-service.yaml

# Deploy StatefulSet
kubectl apply -f 06-statefulset.yaml
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -n clickhouse --watch

# Check PVC status
kubectl get pvc -n clickhouse

# Check service
kubectl get svc -n clickhouse

# View logs
kubectl logs -f deployment/clickhouse -n clickhouse  # Note: StatefulSet uses statefulset name, not deployment

# Access ClickHouse console
kubectl exec -it clickhouse-0 -n clickhouse -- clickhouse-client --multi-line
```

## Configuration

### Storage

Two storage classes are used:
- **clickhouse-fast**: For ClickHouse data (100Gi requested)
- **standard**: For logs (20Gi requested)

Adjust sizes in `04-pvc.yaml` as needed.

### Resources

By default, the ClickHouse pod requests:
- CPU: 500m
- Memory: 2Gi

Limits:
- CPU: 2000m (2 cores)
- Memory: 4Gi

Adjust according to your workload in `06-statefulset.yaml`.

### Access Control

Three users are pre-configured:
- `default`: Full access (password in secret)
- `readonly`: Read-only access (password in secret)
- `admin`: Admin access (password in secret)

Change all passwords in production!

### External Access

To expose ClickHouse outside the cluster (e.g., for BI tools):

1. Ensure Ingress controller is installed: `microk8s enable ingress`
2. Update `07-ingress.yaml` with your domain (clickhouse.aidatalabs.ai)
3. Apply the ingress: `kubectl apply -f 07-ingress.yaml`
4. Configure DNS to point to the cluster's load balancer IP

**Security Note:** Enable basic auth or restrict IPs when exposing ClickHouse externally.

## Using ClickHouse

### From within the cluster

Connect from any pod in the same cluster:

```bash
clickhouse-client --host clickhouse.clickhouse.svc.cluster.local --port 9000 --user default --password
```

HTTP interface:

```bash
curl "http://clickhouse.clickhouse.svc.cluster.local:8123/?query=SELECT%201"
```

### From outside the cluster (if Ingress enabled)

```bash
# Get ingress IP
kubectl get ingress -n clickhouse

# Connect via HTTP
curl "http://clickhouse.aidatalabs.ai/?query=SELECT%201"

# Or use clickhouse-client with proxy
clickhouse-client --host clickhouse.aidatalabs.ai --port 443 --secure --password
```

## Backups

### Manual Backup

```bash
# Exec into pod and create backup
kubectl exec -it clickhouse-0 -n clickhouse -- bash

# Inside pod:
clickhouse-backup create default backup_name

# Copy backup to persistent storage or external storage
# (Configure backup destination in config.xml if needed)
```

### Automated Backups

Set up a CronJob in Kubernetes to run backups periodically. Example:

```yaml
# backup-cron.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: clickhouse-backup
  namespace: clickhouse
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: clickhouse-backup
            image: clickhouse/clickhouse-server:23.10-alpine
            command:
            - /bin/bash
            - -c
            - |
              clickhouse-backup create daily-$(date +%Y%m%d)
              # Upload to S3 or other storage
            env:
            - name: CLICKHOUSE_HOST
              value: clickhouse.clickhouse.svc.cluster.local
            - name: CLICKHOUSE_PORT
              value: "9000"
            - name: CLICKHOUSE_USER
              value: "default"
            - name: CLICKHOUSE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: clickhouse-secrets
                  key: CH_PASSWORD_DEFAULT
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: clickhouse-backup-pvc
```

## Monitoring

### Metrics

ClickHouse exposes metrics on port 8000 when enabled. To expose:

1. Add the following to `config.xml`:

```xml
<metrics_port>8000</metrics_port>
<prometheus>
  <endpoint>/metrics</endpoint>
</prometheus>
```

2. Add port 8000 to the StatefulSet container ports.

3. Configure Prometheus to scrape the endpoint.

### Logs

Logs are written to `/var/log/clickhouse-server/` and can be collected via:
- Sidecar container with fluentd/filebeat
- Node-level log collector
- Directly from pod logs: `kubectl logs -f clickhouse-0 -n clickhouse`

## Scaling

### Vertical Scaling

Edit the StatefulSet to increase CPU/memory:

```bash
kubectl edit statefulset clickhouse -n clickhouse
```

Increase `resources.requests` and `resources.limits`, then restart the pod.

### Horizontal Scaling (Replica Count)

For HA and read scaling, increase replicas:

```bash
kubectl patch statefulset clickhouse -n clickhouse -p '{"spec":{"replicas":3}}'
```

**Note:** ClickHouse replication requires additional configuration ( ZooKeeper or ClickHouse Keeper). See ClickHouse documentation for distributed setup.

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl describe pod clickhouse-0 -n clickhouse

# Check logs
kubectl logs clickhouse-0 -n clickhouse

# Common issues:
# - PVC not bound: Check storage class and available storage
# - Config errors: Validate XML in configmap: clickhouse-0 -c clickhouse-config /etc/clickhouse-server/config.xml
```

### Performance issues

```bash
# Check resource usage
kubectl top pod clickhouse-0 -n clickhouse

# Connect and check system metrics
kubectl exec -it clickhouse-0 -n clickhouse -- clickhouse-client --query="SELECT * FROM system.metrics"

# Check slow queries
clickhouse-client --query="SELECT * FROM system.query_log WHERE type = 2 AND query_start_time >= now() - INTERVAL 1 HOUR ORDER BY query_duration_ms DESC LIMIT 10"
```

### Connection refused

```bash
# Verify service exists
kubectl get svc -n clickhouse

# Verify pod is ready
kubectl get pods -n clickhouse

# Test connectivity from another pod
kubectl run -i --tty --rm debug --image=alpine --restart=Never --namespace=clickhouse -- sh
# Inside debug pod:
apk add clickhouse-client
clickhouse-client --host clickhouse --port 9000
```

## Next Steps

- [ ] Configure backups (see above)
- [ ] Enable monitoring (Prometheus metrics)
- [ ] Set up alerting (disk space, query latency, errors)
- [ ] Implement replication for HA (if needed)
- [ ] Optimize configurations for your specific workload
- [ ] Set up log aggregation
- [ ] Configure SSL/TLS for client connections

## References

- [ClickHouse Documentation](https://clickhouse.com/docs)
- [ClickHouse Kubernetes Best Practices](https://clickhouse.com/docs/en/operations/kubernetes)
- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

---

**Task:** #5 - Deploy ClickHouse database
**Status:** Ready for implementation (blocked by #4)
**Dependencies:** #4 - Setup Kubernetes cluster
**Last Updated:** 2026-02-27
