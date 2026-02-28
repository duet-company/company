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
