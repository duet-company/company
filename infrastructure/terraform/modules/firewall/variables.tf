# Firewall Module Variables

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "droplet_ids" {
  description = "List of droplet IDs to attach firewall to"
  type        = list(number)
}

variable "allowed_inbound_rules" {
  description = "Allowed inbound firewall rules"
  type = list(object({
    port_range = string
    protocol   = string
    sources    = list(string)
  }))
  default = []
}

variable "tags" {
  description = "Tags to apply"
  type        = list(string)
  default     = []
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}
