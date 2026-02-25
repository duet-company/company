# AI Data Labs Infrastructure - Variables

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region for VPS instances"
  type        = string
  default     = "sgp1" # Singapore - closest to Vietnam
}

variable "droplet_size" {
  description = "DigitalOcean droplet size"
  type        = string
  default     = "s-4vcpu-8gb-amd" # 4 vCPUs, 8GB RAM, 160GB SSD
}

variable "ssh_key_ids" {
  description = "List of SSH key IDs to add to droplets"
  type        = list(number)
  default     = []
}

variable "ssh_public_key" {
  description = "SSH public key to add to droplets"
  type        = string
  default     = ""
}

variable "droplet_count" {
  description = "Number of VPS instances to create"
  type        = number
  default     = 3 # Initial cluster: 1 control plane + 2 workers
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = list(string)
  default = [
    "ai-data-labs",
    "duet-company",
    "production"
  ]
}

variable "project_name" {
  description = "Project name for resource organization"
  type        = string
  default     = "ai-data-labs"
}

variable "environment" {
  description = "Environment identifier"
  type        = string
  default     = "production"
}

variable "allowed_inbound_rules" {
  description = "Allowed inbound firewall rules"
  type = list(object({
    port_range = string
    protocol   = string
    sources    = list(string)
  }))
  default = [
    {
      port_range = "22"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # SSH - restrict in production
    },
    {
      port_range = "80"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # HTTP
    },
    {
      port_range = "443"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # HTTPS
    },
    {
      port_range = "16443"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # Kubernetes API
    },
    {
      port_range = "6443"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # Kubernetes API (standard)
    },
    {
      port_range = "10250"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # Kubelet API
    },
    {
      port_range = "30000-32767"
      protocol   = "tcp"
      sources    = ["0.0.0.0/0"] # NodePort services
    }
  ]
}
