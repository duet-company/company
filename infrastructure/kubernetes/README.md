# Kubernetes Infrastructure

This directory contains all Kubernetes configuration and setup scripts for the AI Data Labs platform.

## Directory Structure

```
infrastructure/kubernetes/
├── README.md              # This file
├── microk8s-setup.md      # Comprehensive setup documentation
├── setup-control-plane.sh # Initialization script for control plane
├── namespaces.yaml        # Namespace definitions
├── storageclasses.yaml    # Storage class configurations
├── pvcs.yaml              # Persistent volume claims
└── manifests/             # Application manifests (to be added)
    ├── clickhouse/
    ├── backend/
    ├── frontend/
    └── agents/
```

## Quick Start

### Prerequisites

- VPS infrastructure provisioned (see `../vps-provisioning-plan.md`)
- SSH access to all nodes
- At least 3 nodes: 1 control plane + 2 workers

### Control Plane Setup

```bash
# On the control plane node (k8s-control-01)
cd infrastructure/kubernetes
sudo ./setup-control-plane.sh

# Verify cluster is running
microk8s status

# Get join token for worker nodes
microk8s add-node
```

### Worker Node Setup

```bash
# On each worker node (k8s-worker-01, k8s-worker-02)
sudo snap install microk8s --classic --channel=1.28/stable

# Join the cluster using the token from control plane
microk8s join <token>:<ip>:<port>

# Verify node is connected
microk8s kubectl get nodes
```

## Architecture

### Cluster Layout

```
Control Plane (k8s-control-01)
- 4 vCPUs, 8GB RAM, 160GB SSD
- Runs: API Server, ETCD, Controller, Scheduler
- Services: Ingress, Cert-Manager, Metrics Server

Worker 1 (k8s-worker-01)
- 2 vCPUs, 4GB RAM, 80GB SSD
- Runs: Application workloads

Worker 2 (k8s-worker-02)
- 2 vCPUs, 4GB RAM, 80GB SSD
- Runs: Application workloads
```

### Namespaces

- **production** - Production applications
- **staging** - Staging environment
- **monitoring** - Prometheus, Grafana, AlertManager
- **clickhouse** - ClickHouse database cluster

### Storage Classes

- **standard** - Default storage (general purpose)
- **clickhouse-fast** - High-performance storage for ClickHouse

## Workflows

### Adding a New Application

1. Create namespace (if needed): `kubectl create namespace <app-name>`
2. Create deployment manifest: `manifests/<app>/deployment.yaml`
3. Create service manifest: `manifests/<app>/service.yaml`
4. Create ingress manifest (if needed): `manifests/<app>/ingress.yaml`
5. Apply manifests: `kubectl apply -f manifests/<app>/`

### Updating an Application

```bash
# Apply updated manifests
kubectl apply -f manifests/<app>/

# Check rollout status
kubectl rollout status deployment/<app-name> -n <namespace>

# View logs
kubectl logs -f deployment/<app-name> -n <namespace>
```

### Debugging

```bash
# Check cluster status
microk8s status

# Check node status
kubectl get nodes -o wide

# Check pod status
kubectl get pods -n <namespace>

# Describe pod
kubectl describe pod <pod-name> -n <namespace>

# View logs
kubectl logs <pod-name> -n <namespace>

# Execute into pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash
```

## Security

### Network Policies

- Default deny all traffic
- Explicitly allow required ingress/egress
- Separate network policies per namespace

### RBAC

- Service accounts for each application
- Role-based access control
- No cluster-wide permissions for application pods

### Secrets Management

- Use Kubernetes secrets (or external vault)
- Encrypt secrets at rest
- Rotate secrets regularly

## Monitoring

### Metrics Collection

- Prometheus collects metrics from all pods
- Node exporters for node-level metrics
- Application metrics via Prometheus client libraries

### Logging

- Centralized logging (to be implemented)
- Logs from all pods collected
- Log retention: 30 days

### Alerting

- AlertManager for alert routing
- Critical alerts sent to Slack/Telegram
- Warning alerts aggregated in Grafana

## Backup & Recovery

### etcd Backups

- Daily snapshots of etcd database
- Stored to external storage
- Retention: 7 daily, 4 weekly, 12 monthly

### Persistent Volume Backups

- ClickHouse data backed up regularly
- Backup scripts in `scripts/backup/`
- Test restoration procedure monthly

### Disaster Recovery

- Documented recovery procedures
- Tested quarterly
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour

## Maintenance

### Cluster Updates

```bash
# Check current version
microk8s status

# Refresh to latest channel
microk8s refresh

# Check node drain before update
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Update cluster
microk8s refresh --channel=1.28/stable
```

### Resource Scaling

- Monitor resource usage via Grafana
- Add nodes as needed
- Update storage if needed
- Adjust resource requests/limits

## Troubleshooting

### Pods Not Starting

1. Check pod status: `kubectl get pods -n <namespace>`
2. Describe pod: `kubectl describe pod <pod-name> -n <namespace>`
3. Check logs: `kubectl logs <pod-name> -n <namespace>`
4. Check events: `kubectl get events -n <namespace>`

### Storage Issues

1. Check PVC status: `kubectl get pvc -n <namespace>`
2. Check PV status: `kubectl get pv`
3. Check storage class: `kubectl get sc`
4. Check available space: `df -h`

### Network Issues

1. Check network policies: `kubectl get networkpolicies -n <namespace>`
2. Check pod-to-pod connectivity: `kubectl exec -it <pod> -- ping <other-pod>`
3. Check DNS: `kubectl exec -it <pod> -- nslookup kubernetes.default`

## References

- [microk8s Documentation](https://microk8s.io/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Prometheus Operator](https://github.com/prometheus-operator/kube-prometheus-stack)

## Tasks

This infrastructure supports the following tasks from Sprint 1:

- ✅ #3 - Provision VPS infrastructure (prerequisite)
- 🔄 #4 - Setup Kubernetes cluster (this directory)
- ⏳ #5 - Deploy ClickHouse database (manifests/clickhouse/)
- ⏳ #6 - Setup monitoring stack (manifests/monitoring/)

---

**Last Updated:** 2026-02-16
**Maintainer:** Engineering Team
