#!/bin/bash
# Cluster initialization script for microk8s

set -e

echo "=== Starting microk8s Cluster Setup ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Install microk8s
echo "=== Installing microk8s ==="
snap install microk8s --classic --channel=1.28/stable

# Wait for microk8s to be ready
echo "=== Waiting for microk8s to be ready ==="
microk8s status --wait-ready

# Enable required add-ons
echo "=== Enabling microk8s add-ons ==="
microk8s enable dns
microk8s enable storage
microk8s enable ingress
microk8s enable metrics-server
microk8s enable registry
microk8s enable rbac

# Configure kubectl
echo "=== Configuring kubectl ==="
mkdir -p ~/.kube
microk8s config > ~/.kube/config
chmod 600 ~/.kube/config

# Create storage directories
echo "=== Creating storage directories ==="
mkdir -p /var/snap/microk8s/common/default-storage/clickhouse
mkdir -p /var/snap/microk8s/common/default-storage/prometheus
mkdir -p /var/snap/microk8s/common/default-storage/grafana
chmod 755 /var/snap/microk8s/common/default-storage/clickhouse

# Apply namespaces
echo "=== Applying namespaces ==="
microk8s kubectl apply -f namespaces.yaml

# Apply storage classes
echo "=== Applying storage classes ==="
microk8s kubectl apply -f storageclasses.yaml

# Apply persistent volume claims
echo "=== Applying persistent volume claims ==="
microk8s kubectl apply -f pvcs.yaml

# Check cluster status
echo "=== Cluster Status ==="
microk8s status

echo "=== Cluster Setup Complete ==="
echo "To join worker nodes, run: microk8s add-node"
