# Kubernetes Cluster Setup

Comprehensive Kubernetes cluster configuration for AI Data Labs platform.

## Overview

This directory contains all Kubernetes cluster-wide configurations including namespaces, network policies, resource quotas, storage classes, and RBAC policies.

## Prerequisites

- **Kubernetes Distribution:** microk8s (as specified in roadmap)
- **Version:** 1.28+ (or latest stable)
- **Nodes:** 3-node cluster (1 control plane + 2 workers)
- **OS:** Ubuntu 22.04 LTS or Debian 12
- **Minimum Resources:** 4 vCPUs, 16GB RAM per node

## Quick Start

### Install microk8s

```bash
# Install microk8s on all nodes
sudo snap install microk8s --classic

# Enable required addons
microk8s enable dns
microk8s enable storage
microk8s enable ingress
microk8s enable rbac
microk8s enable metrics-server
microk8s enable prometheus

# Join worker nodes (run on control plane)
microk8s add-node
# Copy the join command and run it on worker nodes
```

### Apply Cluster Configuration

```bash
# Apply all cluster manifests
kubectl apply -f infrastructure/kubernetes/manifests/cluster/

# Verify namespaces created
kubectl get namespaces

# Verify network policies
kubectl get networkpolicies --all-namespaces

# Verify storage classes
kubectl get storageclasses

# Verify RBAC policies
kubectl get clusterroles
kubectl get clusterrolebindings
```

## Architecture

### Namespaces

The cluster is organized into the following namespaces:

| Namespace | Purpose | Resources |
|-----------|---------|-----------|
| `ai-data-labs` | Shared resources (Redis, configs) | 4 CPU, 8Gi RAM |
| `backend` | FastAPI backend service | 2 CPU, 4Gi RAM |
| `agents` | AI agents (Query, Designer, Support) | 2 CPU, 4Gi RAM |
| `clickhouse` | ClickHouse database | 4 CPU, 8Gi RAM |
| `monitoring` | Prometheus, Grafana | Managed separately |
| `ingress` | Nginx ingress controller | Managed separately |
| `cert-manager` | SSL certificate management | Managed separately |

### Network Policies

**Default Deny:**
- All namespaces have default-deny ingress and egress policies
- Explicit allow rules define permitted traffic flow

**Allowed Traffic Flow:**
```
External → Ingress → Backend
              ↘       ↘
               Agents  ClickHouse
                        ↗
                     Monitoring
```

**Key Rules:**
- Ingress can access Backend and Agents
- Backend can access Agents, ClickHouse, and shared resources
- Agents can access ClickHouse
- Monitoring can scrape all services
- DNS is allowed from all namespaces

### Resource Quotas

Each namespace has resource quotas to prevent resource exhaustion:

- **Requests:** Guaranteed resources (must be available for pod scheduling)
- **Limits:** Maximum resources a pod can consume
- **PVCs:** Maximum number of persistent volumes per namespace

### Storage Classes

Three storage tiers for different use cases:

| Storage Class | Type | Use Case | Size |
|--------------|------|----------|------|
| `standard` | HDD | General purpose, logs | 50Gi × 2 |
| `fast-ssd` | SSD | Application data | 20Gi × 2 |
| `high-iops` | NVMe/SSD | Database storage | 100Gi × 2 |

### RBAC Policies

Service accounts have minimal required permissions:

- **app-reader:** Can read basic cluster resources
- **monitoring-system:** Can scrape metrics from all pods
- **ingress-controller:** Can manage ingress resources and backends
- **cert-manager:** Can manage certificates and secrets

## Configuration Details

### Namespaces

Located in `01-namespaces.yaml`

All namespaces include:
- Labels for organization (name, app, environment)
- Default resource limits via LimitRange

### Network Policies

Located in `02-network-policies.yaml`

Key features:
- Zero-trust network security model
- Namespace isolation
- Explicit allow-list for pod communication
- DNS egress allowed from all namespaces
- Monitoring ingress allowed from external

**Security Best Practices:**
- Default-deny all traffic
- Explicit allow rules only for necessary traffic
- Namespace-level isolation
- No cross-namespace communication without explicit rules

### Resource Quotas

Located in `03-resource-quotas.yaml`

**Quota Allocation Strategy:**

1. **ai-data-labs:** 50% of cluster resources (shared services)
2. **backend:** 25% of cluster resources
3. **agents:** 25% of cluster resources
4. **clickhouse:** 100% of quota (dedicated resources)

**Default Resource Limits:**
- Standard namespace: 500m CPU, 512Mi RAM default
- Backend/agents namespace: 1 CPU, 1Gi RAM default
- ClickHouse namespace: 2 CPU, 4Gi RAM default

### Storage Classes

Located in `04-storage-classes.yaml`

**Storage Provisioning:**
- Manual PV creation (hostPath for testing, use cloud provider in production)
- WaitForFirstConsumer binding mode for optimal scheduling
- Three storage tiers for cost optimization

**Production Notes:**
- Replace hostPath with cloud provider storage (DigitalOcean Volumes, AWS EBS, GCE PD)
- Configure CSI drivers for automatic provisioning
- Enable storage replication for high availability

### RBAC Policies

Located in `05-rbac-policies.yaml`

**Least Privilege Principle:**
- Service accounts only have permissions they need
- No cluster-admin access for applications
- ClusterRoles define reusable permission sets
- ClusterRoleBindings link accounts to roles

**Service Account Mapping:**
| Namespace | ServiceAccount | ClusterRole |
|-----------|----------------|--------------|
| backend | backend | app-reader |
| monitoring | prometheus | monitoring-system |
| ingress | nginx-ingress | ingress-controller |
| cert-manager | cert-manager | cert-manager |

## Troubleshooting

### Pods stuck in Pending state

```bash
# Check why pod is pending
kubectl describe pod <pod-name> -n <namespace>

# Check resource quotas
kubectl describe resourcequota -n <namespace>

# Check available resources
kubectl describe nodes
```

### Network policy blocking traffic

```bash
# Check network policies
kubectl get networkpolicies -n <namespace>

# Test connectivity
kubectl exec -it <pod-name> -n <namespace> -- ping <target-service>

# View denied traffic (requires CNI plugin with logging)
```

### Storage not binding

```bash
# Check storage classes
kubectl get storageclasses

# Check PV status
kubectl get pv

# Check PVC status
kubectl get pvc -n <namespace>

# Describe PVC for events
kubectl describe pvc <pvc-name> -n <namespace>
```

### RBAC permission denied

```bash
# Check service account
kubectl get sa <service-account> -n <namespace>

# Check cluster role
kubectl describe clusterrole <role-name>

# Check cluster role binding
kubectl describe clusterrolebinding <binding-name>

# Test permissions
kubectl auth can-i get pods --as=system:serviceaccount:<namespace>:<service-account>
```

## Maintenance

### Backup Cluster Configuration

```bash
# Backup all cluster resources
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# Backup specific namespaces
kubectl get all -n <namespace> -o yaml > namespace-backup.yaml
```

### Scale Storage

```bash
# Add new persistent volumes
kubectl apply -f infrastructure/kubernetes/manifests/cluster/04-storage-classes.yaml

# Resize existing PVC (requires storage class support)
kubectl patch pvc <pvc-name> -n <namespace> -p '{"spec":{"resources":{"requests":{"storage":"<new-size>"}}}}'
```

### Update Resource Quotas

```bash
# Edit quota file
vim infrastructure/kubernetes/manifests/cluster/03-resource-quotas.yaml

# Apply changes
kubectl apply -f infrastructure/kubernetes/manifests/cluster/03-resource-quotas.yaml
```

### Modify Network Policies

```bash
# Edit network policies
vim infrastructure/kubernetes/manifests/cluster/02-network-policies.yaml

# Apply changes
kubectl apply -f infrastructure/kubernetes/manifests/cluster/02-network-policies.yaml

# Test changes with temporary allow policy
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -O- <target-service>
```

## Security Considerations

### Network Security

- **Default-deny:** All traffic denied by default
- **Namespace isolation:** Prevents cross-namespace communication
- **Least privilege:** Only necessary traffic allowed
- **DNS filtering:** Only DNS egress allowed by default

### Resource Security

- **Quotas:** Prevent resource exhaustion attacks
- **Limits:** Prevent runaway resource consumption
- **Requests:** Guaranteed resources for critical workloads

### Access Control

- **RBAC:** Minimal permissions for service accounts
- **No cluster-admin:** Applications don't have admin access
- **Principle of least privilege:** Accounts only have necessary permissions

### Storage Security

- **Persistent volumes:** Not shared between namespaces
- **Storage classes:** Separation of storage tiers
- **Reclaim policy:** Data retention on deletion (Retain)

## Scaling

### Horizontal Scaling (More Nodes)

```bash
# Add new node
microk8s add-node

# Verify node joins
kubectl get nodes

# Rebalance pods (manual or using descheduler)
kubectl cordon <old-node>
kubectl drain <old-node>
kubectl uncordon <old-node>
```

### Vertical Scaling (More Resources per Node)

```bash
# Update resource quotas in 03-resource-quotas.yaml
# Apply changes
kubectl apply -f infrastructure/kubernetes/manifests/cluster/03-resource-quotas.yaml
```

### Storage Scaling

```bash
# Add new persistent volumes in 04-storage-classes.yaml
# Apply changes
kubectl apply -f infrastructure/kubernetes/manifests/cluster/04-storage-classes.yaml
```

## Production Recommendations

1. **Use cloud provider storage:** Replace hostPath with CSI drivers
2. **Enable Pod Security Policies:** Restrict privileged containers
3. **Configure Pod Disruption Budgets:** Ensure availability during upgrades
4. **Set up cluster autoscaling:** Automatically scale nodes based on demand
5. **Enable audit logging:** Track all cluster changes
6. **Configure backup solution:** Regular etcd backups
7. **Use secrets management:** External secret manager (Vault, Sealed Secrets)
8. **Implement network policies:** Zero-trust network model (already configured)
9. **Set up monitoring and alerting:** Comprehensive observability stack
10. **Configure CI/CD:** Automated deployment pipeline

## Next Steps

1. **Deploy Ingress Controller:** Nginx ingress for external access
2. **Deploy cert-manager:** SSL certificate management
3. **Deploy ClickHouse:** Database layer (issue #5, PR #2 ready)
4. **Deploy Backend:** FastAPI application (issue #8, PR #1 ready)
5. **Deploy AI Agents:** Query, Designer, Support agents
6. **Deploy Monitoring Stack:** Prometheus and Grafana (issue #6, PR #3 ready)
7. **Configure DNS:** External domain setup (aidatalabs.ai)

## Documentation

- [microk8s Documentation](https://microk8s.io/docs)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Kubernetes Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review microk8s documentation
3. Check Kubernetes logs: `journalctl -u snap.microk8s.daemon-kubelet -f`
4. Create issue in GitHub repository

---

**Last Updated:** 2026-02-27
**Version:** 1.0.0
**Maintainer:** Duet Company
**Resolves:** Kanboard issue #4 - Setup Kubernetes cluster
