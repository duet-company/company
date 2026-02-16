# microk8s Cluster Setup

**Task:** #4 - Setup Kubernetes cluster
**Status:** In Progress (blocked by #3)
**Assignee:** @duyetbot

## Overview

This document describes the microk8s cluster setup for the AI Data Labs platform.

## Cluster Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Control     │         │   Worker 1   │                  │
│  │  Plane       │────────▶│              │                  │
│  │  (4 vCPU)    │         │  (2 vCPU)    │                  │
│  │  8GB RAM     │         │  4GB RAM     │                  │
│  └──────────────┘         └──────────────┘                  │
│         │                          │                         │
│         └──────────────────────────┘                         │
│                    │                                         │
│              ┌─────▼─────┐                                  │
│              │  Worker 2 │                                  │
│              │           │                                  │
│              │  (2 vCPU) │                                  │
│              │  4GB RAM  │                                  │
│              └───────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

## Node Configuration

### Control Plane (k8s-control-01)
- **Role:** Master node + ETCD + API Server
- **Hardware:**
  - CPU: 4 vCPUs
  - RAM: 8GB
  - Storage: 160GB SSD
- **Components:**
  - microk8s (latest stable)
  - Nginx Ingress Controller
  - Cert-Manager
  - Metrics Server
  - Dashboard (optional)

### Worker Nodes (k8s-worker-01, k8s-worker-02)
- **Role:** Application workloads
- **Hardware (each):**
  - CPU: 2 vCPUs
  - RAM: 4GB
  - Storage: 80GB SSD
- **Components:**
  - microk8s (latest stable)
  - CNI (Calico or Flannel)
  - Node exporter (for monitoring)

## microk8s Installation

### On Control Plane

```bash
# Install microk8s
sudo snap install microk8s --classic

# Enable required add-ons
microk8s enable dns
microk8s enable storage
microk8s enable ingress
microk8s enable metrics-server
microk8s enable registry
microk8s enable community

# Configure cluster
microk8s config > ~/.kube/microk8s-config
chmod 600 ~/.kube/microk8s-config

# Enable RBAC
microk8s enable rbac

# Check status
microk8s status --wait-ready
```

### On Worker Nodes

```bash
# Install microk8s
sudo snap install microk8s --classic

# Get join token from control plane
microk8s add-node

# On worker, join the cluster
microk8s join <token-from-control-plane>

# Verify node is connected
microk8s kubectl get nodes
```

## Storage Configuration

### Storage Classes

```yaml
# storageclass-clickhouse.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: clickhouse-fast
provisioner: microk8s.io/hostpath
parameters:
  pvDir: /var/snap/microk8s/common/default-storage
allowVolumeExpansion: true
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

```yaml
# storageclass-standard.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: microk8s.io/hostpath
parameters:
  pvDir: /var/snap/microk8s/common/default-storage
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

### Persistent Volume Claims

```yaml
# pvc-clickhouse.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: clickhouse-data
  namespace: production
spec:
  storageClassName: clickhouse-fast
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

## Ingress Configuration

### Ingress Controller (Nginx)

```bash
# Nginx Ingress is enabled via: microk8s enable ingress
```

### Ingress Resource Example

```yaml
# ingress-api.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.aidatalabs.ai
    secretName: api-tls
  rules:
  - host: api.aidatalabs.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080
```

## Namespace Configuration

```yaml
# namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    name: production
    env: prod

---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    name: staging
    env: staging

---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    name: monitoring
    env: prod

---
apiVersion: v1
kind: Namespace
metadata:
  name: clickhouse
  labels:
    name: clickhouse
    env: prod
```

## Security Configuration

### Network Policies

```yaml
# network-policy-default-deny.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

```yaml
# network-policy-allow-egress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
  - to:
    - namespaceSelector:
        matchLabels:
          name: clickhouse
```

### Pod Security Policies

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'MustRunAs'
    ranges:
    - min: 1
      max: 65535
```

## Monitoring Integration

### Prometheus Operator

```bash
# Add Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=15d
```

### Node Exporter (DaemonSet)

```yaml
# node-exporter.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        args:
        - --path.procfs=/host/proc
        - --path.sysfs=/host/sys
        - --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)
        volumeMounts:
        - name: proc
          mountPath: /host/proc
        - name: sys
          mountPath: /host/sys
        - name: root
          mountPath: /host
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      - name: root
        hostPath:
          path: /
```

## Testing the Cluster

### Test Deployment

```yaml
# test-nginx.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-test
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-test
  template:
    metadata:
      labels:
        app: nginx-test
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80

---
apiVersion: v1
kind: Service
metadata:
  name: nginx-test-service
  namespace: production
spec:
  selector:
    app: nginx-test
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### Test Script

```bash
#!/bin/bash
# test-cluster.sh

# Test 1: Check nodes
echo "=== Checking Nodes ==="
microk8s kubectl get nodes -o wide

# Test 2: Check system pods
echo "=== Checking System Pods ==="
microk8s kubectl get pods -n kube-system

# Test 3: Create test deployment
echo "=== Creating Test Deployment ==="
microk8s kubectl apply -f test-nginx.yaml

# Test 4: Wait for pods
echo "=== Waiting for pods to be ready ==="
microk8s kubectl wait --for=condition=ready pod -l app=nginx-test -n production --timeout=60s

# Test 5: Check deployment
echo "=== Checking Deployment ==="
microk8s kubectl get pods -n production

# Test 6: Test ingress
echo "=== Testing Ingress ==="
microk8s kubectl get ingress -n production

# Test 7: Clean up
echo "=== Cleaning up ==="
microk8s kubectl delete -f test-nginx.yaml
```

## Troubleshooting

### Common Issues

**Issue: Nodes not joining cluster**
```bash
# Check microk8s status
microk8s status --wait-ready

# Check logs
sudo snap logs microk8s

# Reset and retry
microk8s reset
```

**Issue: Pods not starting**
```bash
# Describe pod for more info
microk8s kubectl describe pod <pod-name>

# Check events
microk8s kubectl get events -n <namespace>

# Check logs
microk8s kubectl logs <pod-name>
```

**Issue: Storage not provisioning**
```bash
# Check storage class
microk8s kubectl get storageclass

# Check PV status
microk8s kubectl get pv

# Check PVC status
microk8s kubectl get pvc -n <namespace>
```

## Next Steps

1. [ ] Provision VPS infrastructure (#3) - BLOCKED
2. [ ] Install microk8s on all nodes
3. [ ] Configure cluster networking
4. [ ] Setup storage classes
5. [ ] Deploy ingress controller
6. [ ] Configure monitoring stack (#6)
7. [ ] Deploy ClickHouse database (#5)

## Documentation

- microk8s Documentation: https://microk8s.io/docs
- Kubernetes Documentation: https://kubernetes.io/docs/
- Nginx Ingress Controller: https://kubernetes.github.io/ingress-nginx/

---

**Status:** Ready for implementation (blocked by #3)
**Dependencies:** #3 - Provision VPS infrastructure
**Estimated Time:** 2-3 hours (once VPS is ready)
