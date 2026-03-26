# AI Data Labs Infrastructure - Main Terraform Configuration
# Provider: DigitalOcean
# Version: 1.0

terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# VPS Instances Module
module "vps_instances" {
  source = "./modules/vps"

  do_token      = var.do_token
  region        = var.region
  droplet_size  = var.droplet_size
  ssh_key_ids   = var.ssh_key_ids
  tags          = var.tags
  project_name  = var.project_name
  environment   = var.environment
}

# Firewall Module
module "firewall" {
  source = "./modules/firewall"

  do_token       = var.do_token
  droplet_ids    = module.vps_instances.droplet_ids
  allowed_inbound_rules = var.allowed_inbound_rules
  tags          = var.tags
  project_name  = var.project_name
  environment   = var.environment
}

# DNS Configuration Module
# NOTE: The domain must be acquired before DNS records become active.
# This module prepares DNS records for aidatalabs.ai. The root domain points to the control plane.
# API and App subdomains should be updated to point to a Load Balancer IP when available.
module "dns" {
  source = "./modules/dns"

  domain_name = "aidatalabs.ai"
  a_records = {
    "@" = module.vps_instances.control_plane_ip
    # "api" will be set after load balancer is provisioned
    # "app" will be set after load balancer is provisioned
  }
  cname_records = {
    "grafana" = "aidatalabs.ai"
    "k8s"     = "aidatalabs.ai"
  }
}

# Outputs
output "droplet_ids" {
  description = "IDs of created droplets"
  value       = module.vps_instances.droplet_ids
}

output "droplet_ips" {
  description = "Public IPs of created droplets"
  value       = module.vps_instances.droplet_ips
}

output "firewall_id" {
  description = "ID of created firewall"
  value       = module.firewall.firewall_id
}

output "dns_domain_id" {
  description = "ID of the managed DNS domain"
  value       = module.dns.domain_id
}
