variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "investment-mcp-cluster"
}

variable "node_pool_machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-4"
}

variable "node_pool_min_count" {
  description = "Minimum node count"
  type        = number
  default     = 1
}

variable "node_pool_max_count" {
  description = "Maximum node count"
  type        = number
  default     = 5
}

variable "db_name" {
  description = "Cloud SQL database name"
  type        = string
  default     = "investment_db"
}

variable "db_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-g1-small"
}
