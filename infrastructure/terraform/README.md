# Terraform Infrastructure - AI Data Labs

## Overview

This Terraform configuration provisions DigitalOcean VPS instances for the AI Data Labs platform infrastructure. It creates:

- 1 Control plane node (Kubernetes control plane)
- 2 Worker nodes (adjustable via `droplet_count`)
- Firewall rules for security
- SSH key management
- Monitoring enabled

## Prerequisites

1. **DigitalOcean Account**: Create an account at https://cloud.digitalocean.com
2. **API Token**: Generate a Personal Access Token:
   - Go to API → Tokens/Keys
   - Create new token with "Write" scope
   - Save it securely

3. **SSH Key Pair** (recommended):
   ```bash
   ssh-keygen -t rsa -b 4096 -C "ai-data-labs"
   ```
   - Copy your public key (`~/.ssh/id_rsa.pub`) for `ssh_public_key` variable

## Quick Start

### 1. Install Terraform

```bash
# macOS
brew install terraform

# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify installation
terraform version
```

### 2. Configure Variables

Copy the example variables file and fill in your values:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Required variables:
- `do_token`: Your DigitalOcean API token
- `ssh_public_key`: Your SSH public key for droplet access

Optional variables (see `terraform.tfvars.example` for defaults):
- `region`: DigitalOcean region (default: Singapore)
- `droplet_size`: VPS size (default: 4 vCPUs, 8GB RAM)
- `droplet_count`: Number of VPS instances (default: 3)

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Plan the Deployment

Review what will be created:

```bash
terraform plan
```

### 5. Deploy Infrastructure

Apply the changes:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 6. Get Connection Info

After deployment, get the IP addresses:

```bash
terraform output
```

Example output:
```
control_plane_ip = "128.199.0.1"
droplet_ids      = [123456789, 123456790, 123456791]
droplet_ips      = ["128.199.0.1", "128.199.0.2", "128.199.0.3"]
worker_ips       = ["128.199.0.2", "128.199.0.3"]
```

### 7. Connect to VPS Instances

```bash
# Control plane
ssh root@$(terraform output -raw control_plane_ip)

# Worker nodes
ssh root@128.199.0.2
ssh root@128.199.0.3
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           DigitalOcean Cloud                 │
│                                              │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Control Plane│  │   Worker 1   │         │
│  │  (master)    │  │              │         │
│  │  128.199.0.1 │  │  128.199.0.2 │         │
│  └──────────────┘  └──────────────┘         │
│         │                  │                 │
│         └────────┬─────────┘                 │
│                  │                           │
│           ┌──────▼──────┐                     │
│           │   Worker 2  │                     │
│           │ 128.199.0.3 │                     │
│           └─────────────┘                     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │     Firewall (DigitalOcean)        │     │
│  │  - SSH (22)                        │     │
│  │  - HTTP (80)                       │     │
│  │  - HTTPS (443)                     │     │
│  │  - K8s API (6443, 16443)          │     │
│  │  - NodePort (30000-32767)         │     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

## Firewall Rules

Inbound rules (configurable via `allowed_inbound_rules` variable):

| Port | Protocol | Purpose        |
|------|----------|----------------|
| 22   | TCP      | SSH            |
| 80   | TCP      | HTTP           |
| 443  | TCP      | HTTPS          |
| 6443 | TCP      | Kubernetes API |
| 16443| TCP      | Kubernetes API |
| 10250| TCP      | Kubelet API    |
| 30000-32767 | TCP | NodePort Services |

**⚠️ Security Note**: In production, restrict SSH access to specific IP addresses instead of `0.0.0.0/0`.

## Maintenance

### Update Infrastructure

After changing Terraform files:

```bash
terraform plan
terraform apply
```

### Scale Up/Down

Modify `droplet_count` in `terraform.tfvars`:

```bash
# Add more workers
terraform apply -var="droplet_count=5"

# Reduce to minimum
terraform apply -var="droplet_count=2"
```

### Destroy Infrastructure

⚠️ **This will delete all resources!**

```bash
terraform destroy
```

## Costs

Estimated monthly costs (Singapore region):

| Resource        | Spec           | Cost/Month |
|-----------------|----------------|------------|
| Control Plane   | 4 vCPU, 8GB RAM | $80        |
| Worker 1        | 4 vCPU, 8GB RAM | $80        |
| Worker 2        | 4 vCPU, 8GB RAM | $80        |
| **Total**       |                | **~$240**  |

See https://www.digitalocean.com/pricing for current pricing.

## Next Steps

After VPS provisioning:

1. **Run Setup Script** on each droplet:
   ```bash
   scp ../scripts/setup-vps.sh root@<ip>:/root/
   ssh root@<ip>
   chmod +x /root/setup-vps.sh
   /root/setup-vps.sh
   ```

2. **Install MicroK8s** → See issue #4 in kanboard
3. **Deploy ClickHouse** → See issue #5 in kanboard
4. **Setup monitoring stack** → See issue #6 in kanboard

## Troubleshooting

### Connection Refused

Check if droplet is running:
```bash
doctl compute droplet list
```

### SSH Access Denied

Verify SSH key is added:
```bash
doctl compute ssh-key list
```

### Terraform State Issues

If Terraform gets confused:
```bash
terraform refresh
terraform plan
```

## Module Structure

```
terraform/
├── main.tf                  # Main configuration
├── variables.tf             # Variable definitions
├── terraform.tfvars.example # Example variables
├── modules/
│   ├── vps/                # VPS provisioning module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── firewall/           # Firewall module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── README.md               # This file
```

## References

- [DigitalOcean Terraform Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [DigitalOcean Droplets](https://www.digitalocean.com/products/droplets/)
- [DigitalOcean Firewalls](https://docs.digitalocean.com/products/networking/firewalls/)
- [Kubernetes on DigitalOcean](https://www.digitalocean.com/community/tech_talks/an-introduction-to-kubernetes)

## Support

For issues or questions:
- GitHub Issue: duet-company/company
- Contact: hello@aidatalabs.ai
