# DNS Module Variables

variable "domain_name" {
  description = "The domain name to manage (e.g., aidatalabs.ai)"
  type        = string
}

variable "a_records" {
  description = "Map of A record names to IP addresses. Use '@' for root domain."
  type        = map(string)
  default     = {}
}

variable "cname_records" {
  description = "Map of CNAME record names to target hostnames."
  type        = map(string)
  default     = {}
}

variable "ttl" {
  description = "Time to live for DNS records in seconds"
  type        = number
  default     = 1800
}
