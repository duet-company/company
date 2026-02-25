# Firewall Module - AI Data Labs
# Creates DigitalOcean firewall for VPS instances

resource "digitalocean_firewall" "default" {
  name = "${var.project_name}-firewall-${var.environment}"

  droplet_ids = var.droplet_ids
  tags        = var.tags

  dynamic "inbound_rule" {
    for_each = var.allowed_inbound_rules
    content {
      port_range = inbound_rule.value.port_range
      protocol   = inbound_rule.value.protocol

      dynamic "source_addresses" {
        for_each = inbound_rule.value.sources
        content {
          address = source_addresses.value
        }
      }
    }
  }

  outbound_rule {
    protocol   = "tcp"
    port_range = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol   = "udp"
    port_range = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }

  outbound_rule {
    protocol   = "icmp"
    port_range = "1-65535"
    destination_addresses = ["0.0.0.0/0"]
  }

  tags = concat(var.tags, ["firewall"])
}
