# DNS Module Outputs

output "domain_id" {
  description = "ID of the DigitalOcean domain"
  value       = digitalocean_domain.this.id
}

output "a_record_ids" {
  description = "IDs of created A records"
  value       = { for k, v in digitalocean_record.a_records : k => v.id }
}

output "cname_record_ids" {
  description = "IDs of created CNAME records"
  value       = { for k, v in digitalocean_record.cname_records : k => v.id }
}
