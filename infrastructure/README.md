# Duet Company - Infrastructure

Infrastructure as code for Duet Company's AI data platform.

## 🏗️ Overview

This repository contains all infrastructure definitions for deploying and managing Duet Company's platform.

### Tech Stack

- **Kubernetes:** Container orchestration
- **Terraform:** Infrastructure provisioning
- **Helm:** Package management for K8s
- **Docker:** Container images
- **GitHub Actions:** CI/CD pipelines

## 📁 Structure

```
infrastructure/
├── terraform/           # Terraform configurations
│   ├── cloud/           # Cloud provider resources
│   ├── kubernetes/      # K8s cluster resources
│   └── modules/         # Reusable modules
├── kubernetes/          # Kubernetes manifests
│   ├── base/            # Base manifests
│   ├── overlays/        # Environment-specific configs
│   └── helmcharts/      # Custom Helm charts
├── docker/              # Dockerfiles
│   ├── backend/         # FastAPI backend
│   ├── frontend/        # React frontend
│   └── agents/         # AI agent containers
├── github-actions/       # CI/CD workflows
│   ├── deploy.yml       # Deployment pipeline
│   ├── test.yml        # Testing pipeline
│   └── security.yml    # Security scanning
└── scripts/             # Utility scripts
    ├── setup.sh        # Initial setup
    ├── deploy.sh       # Deployment script
    └── backup.sh       # Backup script
```

## 🚀 Quick Start

### Prerequisites

- Terraform >= 1.0
- kubectl
- helm
- docker
- AWS/DigitalOcean account

### Setup

```bash
# Clone the repo
git clone git@github.com:duet-company/infrastructure.git
cd infrastructure

# Initialize Terraform
cd terraform/cloud
terraform init

# Configure backend (state storage)
# Edit backend.tf with your S3 bucket details

# Plan infrastructure
terraform plan

# Apply infrastructure
terraform apply
```

### Deploy to Kubernetes

```bash
# Get kubeconfig
# For cloud provider, export KUBECONFIG or use cloud CLI

# Deploy base manifests
kubectl apply -f kubernetes/base/

# Deploy environment-specific overlays
kubectl apply -k kubernetes/overlays/production

# Deploy Helm charts
helm install clickhouse ./kubernetes/helmcharts/clickhouse
helm install platform ./kubernetes/helmcharts/platform
```

## 📊 Environments

### Development
- **Purpose:** Local development and testing
- **Cost:** Minimal
- **Scale:** 1 replica per service

### Staging
- **Purpose:** Pre-production testing
- **Cost:** Medium
- **Scale:** 2-3 replicas per service

### Production
- **Purpose:** Customer-facing deployment
- **Cost:** Optimized for scale
- **Scale:** Auto-scaling (3-10+ replicas)

## 🐳 Docker Images

### Building Images

```bash
# Build backend
docker build -f docker/backend/Dockerfile -t duet-backend:latest .

# Build frontend
docker build -f docker/frontend/Dockerfile -t duet-frontend:latest .

# Build agent
docker build -f docker/agents/Dockerfile -t duet-agent:latest .
```

### Pushing to Registry

```bash
# Tag images
docker tag duet-backend:latest ghcr.io/duet-company/duet-backend:latest

# Push to registry
docker push ghcr.io/duet-company/duet-backend:latest
```

## 🔄 CI/CD

### GitHub Actions Workflows

**Deploy Workflow** (.github/workflows/deploy.yml)
- Triggers on push to main
- Runs tests
- Builds Docker images
- Pushes to registry
- Deploys to Kubernetes

**Test Workflow** (.github/workflows/test.yml)
- Runs on every PR
- Unit tests
- Integration tests
- Linting
- Security scanning

### Manual Deployment

```bash
# Run deploy script
./scripts/deploy.sh staging
```

## 📈 Monitoring

### Prometheus + Grafana

Metrics collection and visualization:
- CPU, memory, disk usage
- Request/response times
- Error rates
- Business metrics

### Logging

Centralized logging with:
- Application logs
- System logs
- Audit logs
- Access logs

### Alerts

Configured alerts for:
- High error rates
- Performance degradation
- Service unavailability
- Resource exhaustion

## 🔐 Security

### Best Practices

- Least privilege access
- Secrets management (Kubernetes Secrets / AWS Secrets Manager)
- Network policies
- Pod security policies
- Regular security scans

### Secrets

Never commit secrets to this repository. Use:
- Kubernetes Secrets
- Environment variables
- Secret management services

## 💰 Cost Management

### Cost Optimization

- Right-sizing instances
- Auto-scaling policies
- Spot instances for non-critical workloads
- Resource quotas
- Regular cost reviews

### Monitoring Costs

- Cost alerts
- Usage tracking
- Budget management
- Cost allocation tags

## 📖 Documentation

- [Terraform Documentation](./terraform/README.md)
- [Kubernetes Guide](./kubernetes/README.md)
- [Docker Guide](./docker/README.md)
- [CI/CD Pipeline](./github-actions/README.md)
- [Security Guide](./SECURITY.md)

## 🆘 Support

- Infrastructure issues: Create a GitHub issue
- Emergency: Contact infrastructure team
- Documentation: Update this repo!

---

**Maintainer:** Infrastructure Team
**Last Updated:** 2026-02-16
**Review Cycle:** Weekly
