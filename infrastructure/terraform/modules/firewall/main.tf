# Firewall Module
# Creates and configures DigitalOcean firewall for cluster nodes

resource "digitalocean_firewall" "cluster" {
  name        = "${var.project_name}-${var.environment}-firewall"
  region      = var.region
  tags        = var.tags

  # Inbound rules from variable
  dynamic "inbound_rule" {
    for_each = var.allowed_inbound_rules
    content {
      protocol         = inbound_rule.value.protocol
      port_range       = inbound_rule.value.port_range
      source_addresses = inbound_rule.value.sources
    }
  }

  # Outbound rules: allow all
  outbound_rule {
    protocol   = "tcp"
    port_range = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol   = "udp"
    port_range = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Apply to droplets
  droplet_ids = var.droplet_ids
}
