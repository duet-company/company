# VPS Infrastructure Provisioning Plan

**Task:** #3 - Provision VPS infrastructure
**Status:** Planning
**Assignee:** @duyetbot

## Provider Selection

### Options Evaluated

1. **DigitalOcean**
   - Pros:
     - Simple, well-documented API
     - Good community and support
     - Consistent performance
     - Transparent pricing
   - Cons:
     - Higher cost than some alternatives
     - Limited data centers in Asia
   - Pricing: ~$6-24/month per droplet
   - Asia Data Centers: Singapore (SG1)

2. **Hetzner**
   - Pros:
     - Very cost-effective
     - Good performance
     - More data centers in Europe
   - Cons:
     - Support primarily in German (English available but secondary)
     - Documentation can be sparse
   - Pricing: ~$4-11/month per server
   - Asia Data Centers: None (Europe only)

3. **Linode (Akamai)**
   - Pros:
     - Good global coverage
     - Reasonable pricing
     - Solid API and CLI
   - Cons:
     - Less documentation than DigitalOcean
   - Pricing: ~$5-40/month per instance
   - Asia Data Centers: Singapore, Tokyo, Mumbai

4. **Vultr**
   - Pros:
     - Many data centers
     - Competitive pricing
     - Good API
   - Cons:
     - Less community than DigitalOcean
   - Pricing: ~$5-40/month per instance
   - Asia Data Centers: Singapore, Tokyo, Seoul, Mumbai

### Recommended Provider: DigitalOcean (Singapore)

**Reasons:**
- Asia-Pacific presence (Singapore DC)
- Excellent documentation
- Reliable API for automation
- Good track record for uptime
- Easy to scale
- Community support

## Initial VPS Configuration

### Production Environment

**Nodes (Week 1-2):**
1. **Control Plane (1x)**
   - CPU: 4 vCPUs
   - RAM: 8GB
   - Storage: 160GB SSD
   - Location: Singapore (SG1)
   - Purpose: Kubernetes master, monitoring, CI/CD runner
   - Cost: ~$24/month

2. **Worker Nodes (2x)**
   - CPU: 2 vCPUs each
   - RAM: 4GB each
   - Storage: 80GB SSD each
   - Location: Singapore (SG1)
   - Purpose: Application workloads, database replicas
   - Cost: ~$12/month each

**Total Initial Cost:** ~$48/month

### Scaling Plan (Month 2-3)
- Add 2 more worker nodes for HA (additional ~$24/month)
- Upgrade control plane to 8GB RAM if needed

## Security Setup

### 1. SSH Access
```bash
# Generate SSH key pair (if not exists)
ssh-keygen -t ed25519 -f ~/.ssh/aidatalabs -C "duyet@aidatalabs.ai"

# Add public key to VPS (via DigitalOcean API or dashboard)
# SSH key will be stored in infrastructure/ssh-keys/
```

### 2. Firewall Rules
```yaml
# UFW Rules (Ubuntu)
- Allow: SSH (22) from specific IPs only (Tailscale, VPN)
- Allow: HTTPS (443) from anywhere
- Allow: HTTP (80) from anywhere (redirect to HTTPS)
- Allow: 6443 (Kubernetes API) from control plane only
- Allow: 10250-10255 (Kubelet) from control plane only
- Allow: 30000-32767 (NodePort services) from load balancer
- Deny: All other incoming traffic
```

### 3. System Hardening
- Disable root SSH login
- Require key-based authentication only
- Install fail2ban for brute-force protection
- Configure automatic security updates
- Setup intrusion detection (AIDE)
- Enable kernel hardening features

### 4. Network Security
- Private network between nodes
- VPC isolation
- Security groups (if using AWS-like model)
- DDoS protection (DigitalOcean Cloud Firewalls)

## DNS Configuration

### Domains
- **Primary:** aidatalabs.ai
- **Subdomains:**
  - api.aidatalabs.ai - API endpoints
  - app.aidatalabs.ai - Frontend application
  - k8s.aidatalabs.ai - Kubernetes dashboard (internal)
  - grafana.aidatalabs.ai - Monitoring dashboard
  - prometheus.aidatalabs.ai - Prometheus metrics (internal)

### DNS Records
```yaml
A Records:
  aidatalabs.ai -> Load Balancer IP
  api.aidatalabs.ai -> API Load Balancer IP
  app.aidatalabs.ai -> Frontend Load Balancer IP

CNAME Records:
  grafana.aidatalabs.ai -> aidatalabs.ai
  k8s.aidatalabs.ai -> aidatalabs.ai
```

## Automation Strategy

### 1. Infrastructure as Code (IaC)
- **Tool:** Terraform (preferred) or DigitalOcean Provider for Pulumi
- **Repository:** infrastructure/terraform/
- **Modules:**
  - `droplet/` - VPS instance module
  - `network/` - Firewall and networking
  - `kubernetes/` - microk8s setup
  - `dns/` - DNS configuration

### 2. Ansible Configuration Management
- **Playbooks:**
  - `base-setup.yml` - Initial system configuration
  - `kubernetes.yml` - Install and configure microk8s
  - `security.yml` - Apply security hardening
  - `monitoring.yml` - Install monitoring stack

### 3. CI/CD Integration
- GitHub Actions workflow for infrastructure updates
- Automated testing of Terraform changes
- Plan → Review → Apply workflow

## Monitoring & Observability

### 1. System Monitoring
- Prometheus node_exporter on all nodes
- Collect metrics: CPU, memory, disk, network
- Alert on: High CPU (>80%), Low disk space (<15%), High memory (>90%)

### 2. Application Monitoring
- Prometheus for application metrics
- Grafana dashboards
- Alert rules for critical services

### 3. Log Aggregation
- Loki or ELK stack
- Centralized logging from all nodes
- Log retention: 30 days

## Backup Strategy

### 1. Database Backups
- ClickHouse daily snapshots
- Store backups to DigitalOcean Spaces (S3-compatible)
- Retention: 7 daily, 4 weekly, 12 monthly

### 2. System Backups
- Weekly VPS snapshots
- Configuration backups to Git
- SSH keys and secrets encrypted in vault

## Next Actions

### Week 1 (Feb 17-23)
1. [ ] Create DigitalOcean account
2. [ ] Generate SSH keys
3. [ ] Provision 3 droplets (1 control, 2 workers)
4. [ ] Configure firewall rules
5. [ ] Setup DNS records
6. [ ] Document all IP addresses and credentials

### Week 2 (Feb 24 - Mar 2)
1. [ ] Apply security hardening
2. [ ] Setup Tailscale for VPN
3. [ ] Configure private networking
4. [ ] Create Terraform configuration
5. [ ] Test disaster recovery (snapshot restore)

## Cost Breakdown (Monthly)

| Item | Quantity | Unit Cost | Total |
|------|-----------|-----------|-------|
| Control Plane Droplet (8GB) | 1 | $24 | $24 |
| Worker Droplet (4GB) | 2 | $12 | $24 |
| Volumes (Storage) | 3 | $2 | $6 |
| Bandwidth (Transfer) | 1 TB | $0.10/GB | $10 |
| Load Balancer | 1 | $10 | $10 |
| Monitoring (Premium) | 1 | $0 | $0 |
| **Total** | | | **~$74/month** |

**Note:** Costs will scale with usage. Actual bandwidth and storage needs will vary.

## Documentation Links

- DigitalOcean Docs: https://docs.digitalocean.com/
- Terraform DigitalOcean Provider: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs
- microk8s Installation: https://microk8s.io/docs
- Ubuntu Security Guide: https://ubuntu.com/server/docs

---

**Status:** Ready for implementation
**Approval Required:** Yes (requires Duyet to provision account)
**Estimated Implementation Time:** 2-3 hours (once account is ready)
**Dependencies:** None (but depends on task #2 - Domain acquisition for DNS setup)
