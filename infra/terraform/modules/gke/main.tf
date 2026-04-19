variable "project_id" { type = string }
variable "region"     { type = string }
variable "cluster_name" { type = string }
variable "node_pool_machine_type" { type = string }
variable "node_pool_min_count"    { type = number }
variable "node_pool_max_count"    { type = number }

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region
  project  = var.project_id

  # Autopilot manages nodes automatically
  enable_autopilot = true

  ip_allocation_policy {}

  release_channel {
    channel = "REGULAR"
  }
}

output "cluster_name"     { value = google_container_cluster.primary.name }
output "cluster_endpoint" { value = google_container_cluster.primary.endpoint }
