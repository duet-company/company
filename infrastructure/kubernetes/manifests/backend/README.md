# Backend Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the AI Data Labs FastAPI backend service.

## Overview

- **Deployment**: 2 replicas (autoscaling 2-10)
- **Service**: ClusterIP on port 8000
- **Ingress**: api.aidatalabs.ai → backend-service
- **Monitoring**: Prometheus metrics on /metrics
- **Scaling**: HorizontalPodAutoscaler based on CPU/Memory

## Prerequisites

1. ClickHouse service must be running
2. Namespace `aidatalabs` must exist
3. Secrets must be configured with actual API keys

## Files

1. **01-namespace.yaml** - Creates the aidatalabs namespace
2. **02-configmap.yaml** - Configuration for backend (databases, URLs, settings)
3. **03-secrets.yaml** - Sensitive data (passwords, API keys)
4. **04-service.yaml** - ClusterIP service for backend
5. **05-deployment.yaml** - Deployment with 2 replicas
6. **06-ingress.yaml** - Ingress for api.aidatalabs.ai
7. **07-hpa.yaml** - HorizontalPodAutoscaler (2-10 replicas)
8. **08-servicemonitor.yaml** - Prometheus metrics scraping

## Setup

### 1. Configure Secrets

Edit `03-secrets.yaml` and replace placeholders with actual values:

```bash
# Encode your secrets
echo -n "your-anthropic-key" | base64
echo -n "your-openai-key" | base64
echo -n "your-zhipu-key" | base64
echo -n "your-jwt-secret" | base64
```

Update the `stringData` section with your keys.

### 2. Apply Manifests

```bash
# Apply all manifests
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-configmap.yaml
kubectl apply -f 03-secrets.yaml
kubectl apply -f 04-service.yaml
kubectl apply -f 05-deployment.yaml
kubectl apply -f 06-ingress.yaml
kubectl apply -f 07-hpa.yaml
kubectl apply -f 08-servicemonitor.yaml

# Or apply all at once
kubectl apply -f .
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n aidatalabs -l app=backend

# Check service
kubectl get svc -n aidatalabs backend-service

# Check ingress
kubectl get ingress -n aidatalabs backend-ingress

# Check HPA
kubectl get hpa -n aidatalabs backend-hpa

# Check logs
kubectl logs -n aidatalabs -l app=backend --tail=50
```

### 4. Test Health Endpoint

```bash
# Port forward to local
kubectl port-forward -n aidatalabs svc/backend-service 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Or test from within the cluster
kubectl run -n aidatalabs --rm -it --restart=Never test-curl --image=curlimages/curl -- curl http://backend-service.aidatalabs.svc.cluster.local:8000/health
```

## Scaling

The HPA automatically scales based on CPU (70% target) and Memory (80% target):

- **Min replicas**: 2
- **Max replicas**: 10
- **Scale down**: Stabilizes for 300s, reduces by 50% every 60s
- **Scale up**: Stabilizes for 60s, increases by 100% or 2 pods every 30s

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale -n aidatalabs deployment/backend --replicas=5

# Check autoscaler status
kubectl describe hpa -n aidatalabs backend-hpa
```

## Monitoring

### Metrics

The backend exposes Prometheus metrics on `/metrics`:

- Request counts
- Response times
- Error rates
- Agent status
- Database connection pool

The ServiceMonitor configures Prometheus to scrape metrics every 15s.

### Logs

```bash
# View logs
kubectl logs -n aidatalabs -l app=backend --tail=100 -f

# View logs for a specific pod
kubectl logs -n aidatalabs -l app=backend -c fastapi --tail=100
```

### Health Checks

The deployment includes:
- **Liveness probe**: `/health` every 10s (initial delay 30s)
- **Readiness probe**: `/health` every 5s (initial delay 5s)

## Configuration

### ConfigMap

Edit `02-configmap.yaml` to change:
- Database connection strings
- CORS settings
- Agent configuration (timeout, queue size)
- Monitoring settings

### Secrets

Edit `03-secrets.yaml` to change:
- Database passwords
- JWT secret
- AI provider API keys

**Important**: Never commit actual secrets to git. Use Kubernetes secrets or external secret management.

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -n aidatalabs -l app=backend

# Check pod logs
kubectl logs -n aidatalabs -l app=backend

# Check events
kubectl get events -n aidatalabs --sort-by='.lastTimestamp'
```

### Connection Issues

```bash
# Test DNS resolution
kubectl run -n aidatalabs --rm -it --restart=Never dns-test --image=busybox -- nslookup clickhouse-service.aidatalabs.svc.cluster.local

# Test connectivity
kubectl run -n aidatalabs --rm -it --restart=Never net-test --image=busybox -- wget -O- http://backend-service.aidatalabs.svc.cluster.local:8000/health
```

### Scaling Issues

```bash
# Check HPA status
kubectl describe hpa -n aidatalabs backend-hpa

# Check resource usage
kubectl top pods -n aidatalabs -l app=backend
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f .

# Or delete specific resources
kubectl delete -n aidatalabs deployment backend
kubectl delete -n aidatalabs service backend-service
kubectl delete -n aidatalabs ingress backend-ingress
kubectl delete -n aidatalabs hpa backend-hpa
kubectl delete -n aidatalabs servicemonitor backend-metrics
```

## Next Steps

1. Configure DNS for api.aidatalabs.ai
2. Set up SSL/TLS certificates for HTTPS
3. Configure Prometheus to scrape metrics
4. Set up alerting rules
5. Configure log aggregation (Loki, ELK)

## Dependencies

- ClickHouse database (clickhouse-service)
- Prometheus operator (for ServiceMonitor)
- NGINX ingress controller (for Ingress)

## Cost

Running on DigitalOcean 4 vCPU, 8GB RAM ($48/month):
- Backend (2 pods): ~200-400MB RAM, 100-200m CPU each
- Total: ~400-800MB RAM, 200-400m CPU
- Well within 8GB RAM limit

## Support

For issues or questions:
- Check logs: `kubectl logs -n aidatalabs -l app=backend`
- Check status: `kubectl get pods -n aidatalabs -l app=backend`
- Check events: `kubectl get events -n aidatalabs`
