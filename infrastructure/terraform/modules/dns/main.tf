# DNS Module - Manage domain and DNS records on DigitalOcean

terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Create the domain zone in DigitalOcean DNS
resource "digitalocean_domain" "this" {
  name = var.domain_name
}

# A Records
resource "digitalocean_record" "a_records" {
  for_each = var.a_records

  domain = digitalocean_domain.this.name
  type   = "A"
  name   = each.key
  value  = each.value
  ttl    = var.ttl
}

# CNAME Records
resource "digitalocean_record" "cname_records" {
  for_each = var.cname_records

  domain = digitalocean_domain.this.name
  type   = "CNAME"
  name   = each.key
  value  = each.value
  ttl    = var.ttl
}
