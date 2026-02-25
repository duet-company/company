#!/bin/bash

# AI Data Labs - VPS Initial Setup Script
# This script configures security, firewall, and basic hardening for new VPS instances

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root"
    exit 1
fi

log_info "Starting AI Data Labs VPS setup..."
log_info "Updating system packages..."

# Update system
apt-get update && apt-get upgrade -y

log_info "Installing essential packages..."

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    htop \
    vim \
    ufw \
    fail2ban \
    unattended-upgrades \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https

log_info "Configuring firewall..."

# Configure UFW firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 6443/tcp  # Kubernetes API
ufw allow 16443/tcp # Kubernetes API
ufw allow 10250/tcp # Kubelet API
ufw allow 30000:32767/tcp # NodePort services

# Enable firewall
ufw --force enable

log_info "Configuring fail2ban..."

# Configure fail2ban
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

systemctl enable fail2ban
systemctl start fail2ban

log_info "Hardening SSH configuration..."

# Backup original SSH config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# SSH security hardening
cat > /etc/ssh/sshd_config.d/ai-data-labs-hardening.conf <<'EOF'
# Disable root login with password
PermitRootLogin prohibit-password

# Disable password authentication
PasswordAuthentication no

# Disable empty passwords
PermitEmptyPasswords no

# Use only protocol 2
Protocol 2

# Disable X11 forwarding
X11Forwarding no

# Disable agent forwarding
AllowAgentForwarding no

# Limit authentication attempts
MaxAuthTries 3
MaxStartups 10:30:60

# Enable strict mode
StrictModes yes

# Disable unnecessary features
AllowTcpForwarding no
GatewayPorts no

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Login grace time
LoginGraceTime 60
EOF

# Restart SSH service
systemctl restart sshd

log_info "Configuring automatic security updates..."

# Configure unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

systemctl enable unattended-upgrades
systemctl start unattended-upgrades

log_info "Configuring system limits for Kubernetes..."

# Configure sysctl settings for Kubernetes
cat > /etc/sysctl.d/99-kubernetes-cri.conf <<'EOF'
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl settings
sysctl --system

log_info "Configuring swap and memory limits..."

# Disable swap (required for Kubernetes)
swapoff -a
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

log_info "Creating user account for operations..."

# Create ops user if it doesn't exist
if ! id -u ops > /dev/null 2>&1; then
    useradd -m -s /bin/bash ops
    usermod -aG sudo ops

    log_warn "Please set a password for the 'ops' user:"
    passwd ops

    log_info "Add your SSH key to /home/ops/.ssh/authorized_keys"
    mkdir -p /home/ops/.ssh
    chmod 700 /home/ops/.ssh
    touch /home/ops/.ssh/authorized_keys
    chmod 600 /home/ops/.ssh/authorized_keys
    chown -R ops:ops /home/ops/.ssh
else
    log_info "User 'ops' already exists"
fi

log_info "Setting up log rotation..."

# Configure log rotation
cat > /etc/logrotate.d/ai-data-labs <<'EOF'
/var/log/ai-data-labs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 syslog adm
}
EOF

log_info "Creating directory structure..."

# Create necessary directories
mkdir -p /var/log/ai-data-labs
mkdir -p /opt/ai-data-labs
mkdir -p /data

log_info "Setup complete! Summary:"
echo "================================"
echo "✓ System updated and upgraded"
echo "✓ Firewall configured (UFW)"
echo "✓ Fail2ban enabled"
echo "✓ SSH hardened (root login disabled)"
echo "✓ Automatic security updates enabled"
echo "✓ Kubernetes prerequisites configured"
echo "✓ User 'ops' created with sudo access"
echo "================================"
echo ""
log_warn "IMPORTANT: Add your SSH public key to /home/ops/.ssh/authorized_keys"
log_warn "Then test SSH access before logging out as root:"
echo "  ssh ops@$(hostname -I | awk '{print $1}')"
echo ""
log_info "Next steps:"
echo "1. Add your SSH key to /home/ops/.ssh/authorized_keys"
echo "2. Test SSH access with ops user"
echo "3. Install MicroK8s: snap install microk8s --classic"
echo "4. Join cluster (see kanboard issue #4)"
