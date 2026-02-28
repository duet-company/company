# VPS Module Variables

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
}

variable "droplet_size" {
  description = "Droplet size slug"
  type        = string
}

variable "ssh_key_ids" {
  description = "Existing SSH key IDs"
  type        = list(number)
  default     = []
}

variable "ssh_public_key" {
  description = "SSH public key to add"
  type        = string
  default     = ""
}

variable "droplet_count" {
  description = "Number of droplets to create"
  type        = number
  default     = 3
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
