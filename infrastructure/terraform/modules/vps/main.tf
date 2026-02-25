# VPS Instances Module - AI Data Labs
# Creates and configures DigitalOcean droplets

resource "digitalocean_ssh_key" "default" {
  name       = "ai-data-labs-${var.environment}"
  public_key = var.ssh_public_key
  count      = var.ssh_public_key != "" ? 1 : 0
}

resource "digitalocean_droplet" "control_plane" {
  image    = "ubuntu-22-04-x64"
  name     = "${var.project_name}-control-plane-${var.environment}"
  region   = var.region
  size     = var.droplet_size

  ssh_keys = concat(
    var.ssh_key_ids,
    var.ssh_public_key != "" ? [digitalocean_ssh_key.default[0].id] : []
  )

  tags = concat(var.tags, ["control-plane"])
  monitoring = true
}

resource "digitalocean_droplet" "workers" {
  count    = var.droplet_count - 1
  image    = "ubuntu-22-04-x64"
  name     = "${var.project_name}-worker-${count.index + 1}-${var.environment}"
  region   = var.region
  size     = var.droplet_size

  ssh_keys = concat(
    var.ssh_key_ids,
    var.ssh_public_key != "" ? [digitalocean_ssh_key.default[0].id] : []
  )

  tags = concat(var.tags, ["worker"])
  monitoring = true
}
