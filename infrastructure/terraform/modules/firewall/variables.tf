# Firewall Module Variables

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
}

variable "droplet_ids" {
  description = "List of droplet IDs to apply firewall to"
  type        = list(string)
}

variable "allowed_inbound_rules" {
  description = "List of inbound firewall rules"
  type = list(object({
    port_range = string
    protocol   = string
    sources    = list(string)
  }))
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
