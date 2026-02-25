# Firewall Module Outputs

output "firewall_id" {
  description = "ID of created firewall"
  value       = digitalocean_firewall.default.id
}

output "firewall_name" {
  description = "Name of created firewall"
  value       = digitalocean_firewall.default.name
}
