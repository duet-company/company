# Kubernetes vs microk8s: Why We Went Lightweight

**Published:** February 21, 2026
**Reading Time:** 7 minutes
**Tags:** #kubernetes #infrastructure #devops #engineering

---

## TL;DR

We evaluated Kubernetes options for AI Data Labs and chose microk8s because it's:

- **Lightweight** - Single binary, minimal dependencies
- **Easy to set up** - One command install
- **Production-ready** - Backed by Canonical, used by major companies
- **Great for small teams** - No overhead of full-blown K8s clusters
- **Perfect for single-node deployments** - Which is where we're starting

Here's how we made the decision.

---

## The Dilemma: Kubernetes is Powerful but Complex

When building AI Data Labs, we needed container orchestration for:

1. **Query Agent** - FastAPI service handling NL→SQL requests
2. **Platform Designer** - Infrastructure automation service
3. **Support Agent** - Chatbot service with LLM integration
4. **ClickHouse** - Our analytics database
5. **Monitoring stack** - Prometheus, Grafana, alerting
6. **Web dashboard** - React frontend

All of these need to run reliably, scale when needed, and be easy to deploy.

Kubernetes is the obvious choice... but it's also notoriously complex.

---

## The Options We Evaluated

### Option 1: Traditional Kubernetes (kubeadm, EKS, GKE)

**What it is:**
Full-blown Kubernetes cluster with multiple nodes, complex networking, and all the bells and whistles.

**Pros:**
- Industry standard
- Maximum flexibility and scalability
- Huge ecosystem of tools and integrations
- Well-documented and battle-tested

**Cons:**
- **Complex setup** - Days to get running, weeks to master
- **High overhead** - Multiple VMs required for HA
- **Steep learning curve** - Need dedicated DevOps engineer
- **Expensive** - 3+ nodes at $20-50/month each = $60-150/month minimum

**Our assessment:**
Overkill for our needs right now. We're starting small, don't need multi-node HA yet.

### Option 2: Managed Kubernetes (EKS, GKE, AKS, DOKS)

**What it is:**
Cloud-provider managed Kubernetes service.

**Pros:**
- No cluster management overhead
- Auto-upgrades and patching
- Integrated with cloud services
- Pay-as-you-go scaling

**Cons:**
- **Vendor lock-in** - Migrating between providers is painful
- **Complex pricing** - Per-hour control plane costs + worker nodes
- **Minimum cost** - Still $50-100/month even for small deployments
- **Overhead** - Still need to manage worker nodes

**Our assessment:**
Good for production, but expensive for our initial $74/month budget. We'd be paying more for K8s than for our actual services.

### Option 3: Minikube / Kind (Local Development Only)

**What it is:**
Single-node Kubernetes clusters for local development.

**Pros:**
- Great for local development
- Easy to set up and tear down
- Cross-platform

**Cons:**
- **Not production-ready** - Designed for dev, not prod
- Resource-heavy - Runs VM inside VM
- Not meant for long-running workloads

**Our assessment:**
Perfect for local dev, but we need production-ready infrastructure.

### Option 4: K3s (Lightweight Kubernetes)

**What it is:**
CNCF-certified Kubernetes distribution by Rancher. Binary is < 40MB.

**Pros:**
- Very lightweight
- Simple installation
- Production-ready
- Great for edge computing

**Cons:**
- **Different networking model** (Traefik vs traditional K8s services)
- Some K8s features disabled or modified
- Smaller community than mainstream K8s

**Our assessment:**
Strong contender. Lightweight, but different enough that we'd need to learn K3s-specific patterns.

### Option 5: microk8s (Our Choice)

**What it is:**
Canonical's lightweight Kubernetes distribution. Single snap package, minimal dependencies.

**Pros:**
- **Ultra-lightweight** - < 500MB, single snap package
- **One-command install** - `snap install microk8s --classic`
- **Production-ready** - Used by Canonical, Ubuntu, and major companies
- **Easy to upgrade** - `microk8s refresh`
- **Addons available** - DNS, storage, ingress, dashboard, metrics
- **Canonical support** - Backed by the company behind Ubuntu
- **Perfect for single-node** - Can scale to multi-node later
- **Native Ubuntu integration** - Works seamlessly on Ubuntu 22.04

**Cons:**
- **Snap dependency** - Only officially supports Linux (specifically Ubuntu)
- **Limited to 50 worker nodes** (fine for us)
- **Not as widely known** as EKS/GKE

**Our assessment:**
Perfect fit for our use case: single-node deployment, minimal overhead, easy to scale to multi-node later when needed.

---

## Why microk8s Won

After evaluating all options, microk8s was the clear winner for AI Data Labs.

### 1. Perfect for Single-Node Deployments

We're starting with a single 8GB VPS. microk8s is designed for exactly this scenario:

```bash
# Install in 30 seconds
snap install microk8s --classic --channel=1.29/stable

# Enable addons
microk8s enable dns storage ingress metrics-server dashboard

# Ready in 2 minutes
microk8s status --wait-ready
```

Compare this to traditional Kubernetes:
- `kubeadm init` - 15-30 minutes
- Install CNI plugin (Calico/Flannel) - 5-10 minutes
- Configure storage class - 5-10 minutes
- Setup ingress controller - 10-15 minutes
- **Total: 35-65 minutes** vs **2 minutes**

### 2. Addons Out of the Box

microk8s comes with pre-configured addons:

```bash
microk8s enable dns          # CoreDNS for service discovery
microk8s enable storage       # StorageClass for persistent volumes
microk8s enable ingress       # NGINX ingress controller
microk8s enable registry      # Private Docker registry
microk8s enable dashboard     # Kubernetes dashboard
microk8s enable metrics       # Prometheus metrics server
microk8s enable helm         # Helm package manager
```

No configuration needed. They just work.

### 3. Easy to Manage

```bash
# Check status
microk8s status

# Get cluster info
microk8s config

# Access Kubernetes CLI
microk8s kubectl get pods

# Access services
microk8s kubectl get svc

# Enable/disable addons
microk8s disable dashboard  # Turn off if not needed
```

All commands prefixed with `microk8s`, so no conflicts with system-wide kubectl.

### 4. Can Scale to Multi-Node Later

When we're ready for HA, we can join additional nodes:

```bash
# On control plane
microk8s add-node

# On worker nodes
microk8s join <token> <control-plane-ip>

# Now you have a full multi-node cluster!
```

Seamless upgrade from single-node to multi-node without changing your architecture.

### 5. Canonical Support

Canonical is the company behind Ubuntu. They've been doing Linux for 20+ years. microk8s is:

- Officially maintained
- Security updates via snap
- Commercial support available
- Used in production by major companies
- CNCF-conformant (passes all K8s conformance tests)

### 6. Cost-Effective

For our initial setup:

- **Traditional K8s (3 nodes):** $150/month minimum
- **Managed EKS:** $72/month control plane + $60-120/month workers = $132-192/month
- **microk8s (1 node):** $0 (just runs on our existing VPS)

We're spending $48/month on our VPS. microk8s adds $0.

When we scale to 3 nodes:
- **microk8s cluster:** 3 x $24/month = $72/month
- **Still cheaper** than managed K8s

---

## Our microk8s Architecture

Here's how we're using microk8s at AI Data Labs:

```
┌─────────────────────────────────────────────────────┐
│              DigitalOcean Droplet                   │
│               (Ubuntu 22.04 LTS)                   │
│                  4 vCPUs, 8 GB RAM                  │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │     microk8s     │
              │  (Single Node)   │
              └────────┬─────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐       ┌────▼────┐       ┌────▼────┐
│ Click  │       │  Fast   │       │ React   │
│ House  │       │  API    │       │ App     │
└────────┘       └─────────┘       └─────────┘
    │                  │                  │
┌───▼────┐       ┌────▼────┐       ┌────▼────┐
│Prometh.│       │  AI     │       │Support  │
│Grafana │       │ Agents  │       │ Agent   │
└────────┘       └─────────┘       └─────────┘
```

### Services Deployed

1. **ClickHouse** - StatefulSet with persistent volume
2. **FastAPI Backend** - Deployment with 2 replicas
3. **React Frontend** - Deployment with Nginx
4. **AI Agents** - Deployment (scale as needed)
5. **Prometheus** - StatefulSet with persistent volume
6. **Grafana** - Deployment with persistent volume
7. **NGINX Ingress** - For routing

### Persistent Storage

```yaml
# microk8s storage class
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: clickhouse-pvc
spec:
  storageClassName: microk8s-hostpath  # Built-in storage class
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

microk8s provides the `microk8s-hostpath` storage class out of the box. Simple and reliable.

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aidatalabs-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: public
  rules:
  - host: api.aidatalabs.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
```

microk8s includes the NGINX ingress controller with the `public` ingress class.

---

## Performance Tips

### 1. Use Resource Limits

Don't let services consume all resources:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: fastapi
    image: aidatalabs/fastapi:latest
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

### 2. Use Probes for Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 3. Use Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Migration Path: microk8s → Full K8s

One of the best things about microk8s: it's Kubernetes.

When we grow beyond a single node:

1. **Add worker nodes** (already tested in our Terraform config)
2. **Deploy with Helm** instead of plain manifests
3. **Add more components** (cert-manager, external-dns, etc.)
4. **Migrate to managed K8s** if desired (EKS/GKE/DOKS)

No need to rewrite deployments or services. They're standard Kubernetes manifests.

---

## Challenges We've Faced

### 1. Snap Updates

Sometimes snap auto-updates microk8s at inconvenient times.

**Solution:**
```bash
# Hold snap updates
snap hold microk8s

# Update manually when ready
snap unhold microk8s
snap refresh microk8s --channel=1.29/stable
snap hold microk8s
```

### 2. Hostpath Storage Limitations

The `microk8s-hostpath` storage class uses local disk. It's great for single-node, but doesn't work well for multi-node.

**Solution:**
When we scale to multi-node, we'll switch to Longhorn or Rook for distributed storage.

### 3. Memory on Small Nodes

Our 8GB VPS gets tight with all services running.

**Solution:**
- Resource limits on all pods
- Deploy only what's needed in production
- Use efficient base images (Alpine, distroless)
- Consider upgrading to 16GB when needed

---

## When to NOT Use microk8s

microk8s isn't for everyone. Consider alternatives if:

- **You need Windows** - Snap is Linux-only
- **You're at scale** - 100+ nodes, petabytes of data (use EKS/GKE/DOKS)
- **You need enterprise features** - Service mesh, advanced RBAC (use managed K8s)
- **You're not on Ubuntu** - Can be made to work on other distros, but Ubuntu is best

---

## Getting Started with microk8s

Want to try microk8s?

```bash
# Install
snap install microk8s --classic

# Enable addons
microk8s enable dns storage ingress

# Check status
microk8s status --wait-ready

# Deploy your first app
microk8s kubectl create deployment hello-world --image=hello-world
microk8s kubectl expose deployment hello-world --type=NodePort --port=80

# Access
microk8s kubectl get svc
```

**Documentation:** https://microk8s.io/docs

---

## Conclusion

For AI Data Labs, microk8s is the perfect Kubernetes distribution:

- **Lightweight** - Minimal resource overhead
- **Simple** - One-command install, easy to manage
- **Production-ready** - Backed by Canonical, used at scale
- **Scalable** - Can grow to multi-node when needed
- **Cost-effective** - $0 additional cost on our VPS

We're not fighting complexity. We're building features.

When you're starting small, don't over-engineer. Use the right tool for the job. For us, that's microk8s.

---

**Want to learn more?**

- Read the [microk8s documentation](https://microk8s.io/docs)
- Check out our [Kubernetes manifests](https://github.com/duet-company/infrastructure-config)
- Follow us on Twitter [@duetcompany](https://twitter.com/duetcompany)

**Questions?** Say hi at [hello@aidatalabs.ai](mailto:hello@aidatalabs.ai)

---

*This post is part 1 of our Infrastructure Deep Dive series. Next up: "Building a Single-Node K8s Cluster on $48/month."*
