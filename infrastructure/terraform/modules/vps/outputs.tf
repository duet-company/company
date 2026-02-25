# VPS Module Outputs

output "droplet_ids" {
  description = "IDs of all created droplets"
  value = concat(
    [digitalocean_droplet.control_plane.id],
    digitalocean_droplet.workers[*].id
  )
}

output "droplet_ips" {
  description = "Public IPs of all droplets"
  value = concat(
    [digitalocean_droplet.control_plane.ipv4_address],
    digitalocean_droplet.workers[*].ipv4_address
  )
}

output "control_plane_ip" {
  description = "IP address of control plane"
  value       = digitalocean_droplet.control_plane.ipv4_address
}

output "worker_ips" {
  description = "IP addresses of worker nodes"
  value       = digitalocean_droplet.workers[*].ipv4_address
}
