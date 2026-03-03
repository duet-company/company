# Frontend Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the AI Data Labs Next.js frontend dashboard.

## Overview

- **Deployment**: 2 replicas (autoscaling 2-10)
- **Service**: ClusterIP on port 3000
- **Ingress**: aidatalabs.ai → frontend-service
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS

## Prerequisites

1. Backend service must be running (backend-service)
2. Namespace `aidatalabs` must exist
3. DNS for aidatalabs.ai must be configured

## Files

1. **01-configmap.yaml** - Configuration for frontend (API URLs, feature flags)
2. **02-service.yaml** - ClusterIP service for frontend
3. **03-deployment.yaml** - Deployment with 2 replicas
4. **04-ingress.yaml** - Ingress for aidatalabs.ai
5. **05-hpa.yaml** - HorizontalPodAutoscaler (2-10 replicas)

## Setup

### 1. Configure ConfigMap

Edit `01-configmap.yaml` to customize:
- API URLs (if backend is on different domain)
- Feature flags (enable/disable features)
- Analytics settings

### 2. Apply Manifests

```bash
# Apply all manifests
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-service.yaml
kubectl apply -f 03-deployment.yaml
kubectl apply -f 04-ingress.yaml
kubectl apply -f 05-hpa.yaml

# Or apply all at once
kubectl apply -f .
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n aidatalabs -l app=frontend

# Check service
kubectl get svc -n aidatalabs frontend-service

# Check ingress
kubectl get ingress -n aidatalabs frontend-ingress

# Check HPA
kubectl get hpa -n aidatalabs frontend-hpa

# Check logs
kubectl logs -n aidatalabs -l app=frontend --tail=50
```

### 4. Access Application

**Option 1: Via Ingress (production)**
```bash
# Configure DNS: aidatalabs.ai → ingress IP
curl https://aidatalabs.ai
```

**Option 2: Port Forward (development)**
```bash
# Port forward to local
kubectl port-forward -n aidatalabs svc/frontend-service 3000:3000

# Access at http://localhost:3000
open http://localhost:3000
```

**Option 3: Via LoadBalancer (if using)**
```bash
# Get external IP
kubectl get svc -n aidatalabs frontend-ingress

# Access via external IP
curl http://<external-ip>
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
kubectl scale -n aidatalabs deployment/frontend --replicas=5

# Check autoscaler status
kubectl describe hpa -n aidatalabs frontend-hpa
```

## Configuration

### ConfigMap

Edit `01-configmap.yaml` to change:
- Backend API URL
- Feature flags
- Analytics settings

### Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (for client-side)
- `NEXT_PUBLIC_API_WS_URL`: WebSocket URL for real-time updates
- `NEXT_PUBLIC_ENABLE_CHAT`: Enable/disable chat feature
- `NEXT_PUBLIC_ENABLE_DASHBOARD`: Enable/disable dashboard
- `NEXT_PUBLIC_ENABLE_QUERY`: Enable/disable query editor

## Monitoring

### Logs

```bash
# View logs
kubectl logs -n aidatalabs -l app=frontend --tail=100 -f

# View logs for a specific pod
kubectl logs -n aidatalabs -l app=frontend --tail=100
```

### Health Checks

The deployment includes:
- **Liveness probe**: `/` every 10s (initial delay 30s)
- **Readiness probe**: `/` every 5s (initial delay 5s)

### Resource Usage

```bash
# Check resource usage
kubectl top pods -n aidatalabs -l app=frontend

# Check HPA metrics
kubectl describe hpa -n aidatalabs frontend-hpa
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -n aidatalabs -l app=frontend

# Check pod logs
kubectl logs -n aidatalabs -l app=frontend

# Check events
kubectl get events -n aidatalabs --sort-by='.lastTimestamp'
```

### Connection Issues

```bash
# Test DNS resolution to backend
kubectl run -n aidatalabs --rm -it --restart=Never dns-test --image=busybox -- nslookup backend-service.aidatalabs.svc.cluster.local

# Test connectivity to backend
kubectl run -n aidatalabs --rm -it --restart=Never net-test --image=busybox -- wget -O- http://backend-service.aidatalabs.svc.cluster.local:8000/health
```

### Ingress Issues

```bash
# Check ingress status
kubectl describe ingress -n aidatalabs frontend-ingress

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50
```

### Build Issues

If the Next.js build fails:

```bash
# Check build logs
kubectl logs -n aidatalabs -l app=frontend --tail=100

# Check if image exists
kubectl describe pod -n aidatalabs -l app=frontend | grep Image
```

## Performance Optimization

### Static Assets

Next.js automatically optimizes static assets. To enable further caching:

```bash
# Verify caching headers in ingress
kubectl get ingress -n aidatalabs frontend-ingress -o yaml | grep -A 5 proxy_cache_valid
```

### Gzip Compression

Gzip is enabled in the ingress annotations for faster page loads.

### CDN Integration

For production, consider using a CDN (Cloudflare, AWS CloudFront):

1. Point aidatalabs.ai to CDN
2. Configure CDN to origin at ingress IP
3. Enable CDN caching for static assets

## SSL/TLS Configuration

### Using cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: hello@aidatalabs.ai
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: public
EOF

# Update ingress with TLS annotation
kubectl annotate ingress frontend-ingress -n aidatalabs \
  cert-manager.io/cluster-issuer=letsencrypt-prod

# Add TLS spec to ingress
kubectl patch ingress frontend-ingress -n aidatalabs -p '{
  "spec": {
    "tls": [{
      "hosts": ["aidatalabs.ai"],
      "secretName": "aidatalabs-tls"
    }]
  }
}'
```

## Deployment Workflow

### Build and Push Docker Image

```bash
# Build Next.js production image
cd apps/frontend
docker build -t aidatalabs/frontend:latest .

# Tag and push to registry
docker tag aidatalabs/frontend:latest registry.aidatalabs.ai/frontend:latest
docker push registry.aidatalabs.ai/frontend:latest

# Update deployment to use new image
kubectl set image deployment/frontend -n aidatalabs nextjs=aidatalabs/frontend:latest
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/frontend -n aidatalabs

# Rollback to previous version
kubectl rollout undo deployment/frontend -n aidatalabs

# Rollback to specific revision
kubectl rollout undo deployment/frontend -n aidatalabs --to-revision=2
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f .

# Or delete specific resources
kubectl delete -n aidatalabs deployment frontend
kubectl delete -n aidatalabs service frontend-service
kubectl delete -n aidatalabs ingress frontend-ingress
kubectl delete -n aidatalabs hpa frontend-hpa
```

## Next Steps

1. Configure DNS for aidatalabs.ai
2. Set up SSL/TLS certificates
3. Configure analytics (Google Analytics, Mixpanel)
4. Set up error tracking (Sentry)
5. Configure CDN for static assets
6. Set up A/B testing

## Dependencies

- Backend service (backend-service.aidatalabs.svc.cluster.local:8000)
- NGINX ingress controller (for Ingress)
- cert-manager (optional, for SSL/TLS)

## Cost

Running on DigitalOcean 4 vCPU, 8GB RAM ($48/month):
- Frontend (2 pods): ~128-256MB RAM, 50-150m CPU each
- Total: ~256-512MB RAM, 100-300m CPU
- Well within 8GB RAM limit

## Performance

Expected performance metrics:
- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.5s
- **Cumulative Layout Shift (CLS)**: < 0.1

## Support

For issues or questions:
- Check logs: `kubectl logs -n aidatalabs -l app=frontend`
- Check status: `kubectl get pods -n aidatalabs -l app=frontend`
- Check events: `kubectl get events -n aidatalabs`
