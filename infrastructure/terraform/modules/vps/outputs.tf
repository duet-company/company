# VPS Module Outputs

output "droplet_ids" {
  description = "IDs of created droplets"
  value       = digitalocean_droplet.vps[*].id
}

output "droplet_ips" {
  description = "Public IPs of droplets"
  value       = digitalocean_droplet.vps[*].ipv4_address
}
