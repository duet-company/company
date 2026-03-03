# AI Data Labs - Kubernetes Manifests

Complete Kubernetes manifests for deploying AI Data Labs platform on microk8s.

## Overview

This repository contains production-ready Kubernetes manifests for deploying all components of AI Data Labs:
- **ClickHouse**: Analytics database
- **Backend**: FastAPI service with AI agents
- **Frontend**: Next.js dashboard

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              DigitalOcean Droplet                   │
│               (Ubuntu 22.04 LTS)                   │
│                  4 vCPUs, 8 GB RAM                  │
│                     microk8s                        │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │   Ingress (NGINX)│
              └────────┬─────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────────┐   ┌────▼───────┐   ┌────▼──────┐
│ Frontend   │   │  Backend   │   │ ClickHouse │
│ (Next.js)  │   │ (FastAPI)  │   │ (Database) │
│ :3000      │   │ :8000      │   │ :8123      │
└────────────┘   └────────────┘   └────────────┘
```

## Prerequisites

1. **microk8s** installed and running
2. **DNS configured** for:
   - aidatalabs.ai → Ingress IP
   - api.aidatalabs.ai → Ingress IP
3. **Docker images** built and pushed to registry

## Quick Start

### 1. Install microk8s

```bash
# Install microk8s
snap install microk8s --classic --channel=1.29/stable

# Enable addons
microk8s enable dns storage ingress dashboard metrics-server registry

# Wait for microk8s to be ready
microk8s status --wait-ready

# Alias kubectl
alias kubectl='microk8s kubectl'
```

### 2. Create Namespace

```bash
kubectl create namespace aidatalabs
```

### 3. Deploy ClickHouse

```bash
cd clickhouse
kubectl apply -f .
```

Verify ClickHouse is running:
```bash
kubectl get pods -n aidatalabs -l app=clickhouse
kubectl logs -n aidatalabs -l app=clickhouse
```

### 4. Deploy Backend

```bash
cd backend
# Edit secrets.yaml with your API keys
kubectl apply -f .
```

Verify backend is running:
```bash
kubectl get pods -n aidatalabs -l app=backend
kubectl logs -n aidatalabs -l app=backend
```

Test health endpoint:
```bash
kubectl port-forward -n aidatalabs svc/backend-service 8000:8000
curl http://localhost:8000/health
```

### 5. Deploy Frontend

```bash
cd frontend
kubectl apply -f .
```

Verify frontend is running:
```bash
kubectl get pods -n aidatalabs -l app=frontend
kubectl logs -n aidatalabs -l app=frontend
```

Test frontend:
```bash
kubectl port-forward -n aidatalabs svc/frontend-service 3000:3000
open http://localhost:3000
```

### 6. Configure DNS

Update your DNS records:

```
aidatalabs.ai      A    <ingress-ip>
api.aidatalabs.ai  A    <ingress-ip>
```

Get ingress IP:
```bash
kubectl get ingress -n aidatalabs
```

## Components

### ClickHouse

**Files**: `clickhouse/`
- 01-namespace.yaml
- 02-configmap.yaml
- 03-secrets.yaml
- 04-pvc.yaml
- 05-service.yaml
- 06-statefulset.yaml
- 07-ingress.yaml

**Resources**: 1Gi RAM, 500m CPU

### Backend

**Files**: `backend/`
- 01-namespace.yaml
- 02-configmap.yaml
- 03-secrets.yaml
- 04-service.yaml
- 05-deployment.yaml
- 06-ingress.yaml
- 07-hpa.yaml
- 08-servicemonitor.yaml

**Resources**: 256-512Mi RAM per pod, 100-200m CPU per pod
**Replicas**: 2-10 (autoscaled)

### Frontend

**Files**: `frontend/`
- 01-configmap.yaml
- 02-service.yaml
- 03-deployment.yaml
- 04-ingress.yaml
- 05-hpa.yaml

**Resources**: 128-256Mi RAM per pod, 50-150m CPU per pod
**Replicas**: 2-10 (autoscaled)

## Monitoring

### Health Checks

```bash
# Check all pods
kubectl get pods -n aidatalabs

# Check services
kubectl get svc -n aidatalabs

# Check ingress
kubectl get ingress -n aidatalabs

# Check HPA
kubectl get hpa -n aidatalabs
```

### Logs

```bash
# Backend logs
kubectl logs -n aidatalabs -l app=backend --tail=100 -f

# Frontend logs
kubectl logs -n aidatalabs -l app=frontend --tail=100 -f

# ClickHouse logs
kubectl logs -n aidatalabs -l app=clickhouse --tail=100 -f
```

### Resource Usage

```bash
# Pod resource usage
kubectl top pods -n aidatalabs

# Node resource usage
kubectl top nodes
```

## Scaling

### Manual Scaling

```bash
# Scale backend to 5 replicas
kubectl scale -n aidatalabs deployment/backend --replicas=5

# Scale frontend to 5 replicas
kubectl scale -n aidatalabs deployment/frontend --replicas=5
```

### Auto-Scaling

Backend and Frontend have HPAs configured:
- **Min**: 2 replicas
- **Max**: 10 replicas
- **CPU Target**: 70%
- **Memory Target**: 80%

Check HPA status:
```bash
kubectl describe hpa -n aidatalabs
```

## Updates

### Rolling Updates

```bash
# Update backend image
kubectl set image deployment/backend -n aidatalabs \
  fastapi=aidatalabs/backend:v2.0.0

# Update frontend image
kubectl set image deployment/frontend -n aidatalabs \
  nextjs=aidatalabs/frontend:v2.0.0
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/backend -n aidatalabs

# Rollback to previous version
kubectl rollout undo deployment/backend -n aidatalabs
```

## Security

### Secrets

Never commit actual secrets to git. Use Kubernetes secrets:

```bash
# Create secret from literal
kubectl create secret generic backend-secrets \
  -n aidatalabs \
  --from-literal=ANTHROPIC_API_KEY='your-key' \
  --from-literal=OPENAI_API_KEY='your-key' \
  --from-literal=ZHIPU_API_KEY='your-key'

# Create secret from file
kubectl create secret generic backend-secrets \
  -n aidatalabs \
  --from-file=secrets.env
```

### Network Policies

Restrict pod-to-pod communication:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: aidatalabs
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### RBAC

Limit service account permissions:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend
  namespace: aidatalabs
automountServiceAccountToken: false
```

## Backup & Recovery

### ClickHouse Backup

```bash
# Backup ClickHouse data
kubectl exec -n aidatalabs -c clickhouse \
  $(kubectl get pod -n aidatalabs -l app=clickhouse -o jsonpath='{.items[0].metadata.name}') \
  -- clickhouse-client --query="BACKUP TABLE database.table TO Disk('backups', 'backup/')"
```

### Persistent Volumes

```bash
# List PVCs
kubectl get pvc -n aidatalabs

# Backup PV data
kubectl cp -n aidatalabs \
  $(kubectl get pod -n aidatalabs -l app=clickhouse -o jsonpath='{.items[0].metadata.name}'):/var/lib/clickhouse \
  ./clickhouse-backup
```

## Troubleshooting

### Common Issues

**Pods not starting**:
```bash
kubectl describe pod -n aidatalabs <pod-name>
kubectl logs -n aidatalabs <pod-name>
```

**DNS issues**:
```bash
kubectl run -n aidatalabs --rm -it --restart=Never dns-test \
  --image=busybox -- nslookup backend-service.aidatalabs.svc.cluster.local
```

**Ingress issues**:
```bash
kubectl describe ingress -n aidatalabs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Events

```bash
# View recent events
kubectl get events -n aidatalabs --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n aidatalabs -w
```

## Cost

**Total monthly cost**: ~$48 (DigitalOcean 4 vCPU, 8GB RAM)

**Resource allocation**:
- ClickHouse: ~1Gi RAM, 500m CPU
- Backend (2-10 pods): ~512Mi-2Gi RAM, 200m-1G CPU
- Frontend (2-10 pods): ~256Mi-1Gi RAM, 100m-500m CPU
- System overhead: ~2-3Gi RAM, 1-2G CPU

**Well within 8GB RAM limit** with room for scaling.

## Performance

### Expected Metrics

- **API response time**: < 200ms (95th percentile)
- **Page load time**: < 2s
- **Query execution**: < 1s (95% of queries)
- **Pod startup time**: < 30s
- **Rollout time**: < 2 minutes

### Optimization Tips

1. **Enable resource limits** on all pods
2. **Use HPA** for auto-scaling
3. **Configure node affinity** for better distribution
4. **Use init containers** for pre-start checks
5. **Set appropriate requests/limits** to prevent resource starvation

## Next Steps

1. **SSL/TLS**: Set up cert-manager for HTTPS
2. **Monitoring**: Deploy Prometheus + Grafana
3. **Logging**: Set up Loki + Grafana
4. **Alerting**: Configure alertmanager
5. **CI/CD**: Set up automated deployment pipeline
6. **Disaster Recovery**: Implement backup strategy
7. **Multi-region**: Deploy to additional regions for HA

## Documentation

- [ClickHouse manifests](./clickhouse/README.md)
- [Backend manifests](./backend/README.md)
- [Frontend manifests](./frontend/README.md)
- [microk8s documentation](https://microk8s.io/docs)
- [Kubernetes documentation](https://kubernetes.io/docs/)

## Support

For issues or questions:
- Check component-specific READMEs
- Check logs: `kubectl logs -n aidatalabs -l app=<app>`
- Check status: `kubectl get pods -n aidatalabs`
- Check events: `kubectl get events -n aidatalabs`

## License

Copyright © 2026 Duet Company. All rights reserved.
