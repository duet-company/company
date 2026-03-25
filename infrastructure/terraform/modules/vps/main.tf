# VPS Instances Module
# Creates DigitalOcean droplets for the Kubernetes cluster and workloads

resource "digitalocean_droplet" "vps" {
  count = var.droplet_count

  name               = "${var.project_name}-${var.environment}-${count.index + 1}"
  region             = var.region
  size               = var.droplet_size
  image              = "ubuntu-24-04-x64"
  ssh_keys           = var.ssh_key_ids
  tags               = var.tags
  monitoring         = true
  backups            = false

  # Optional cloud-init for additional configuration
  user_data = var.user_data
}
