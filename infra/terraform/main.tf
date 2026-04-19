terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "investment-mcp-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "gke" {
  source     = "./modules/gke"
  project_id = var.project_id
  region     = var.region
  cluster_name = var.cluster_name
  node_pool_machine_type = var.node_pool_machine_type
  node_pool_min_count    = var.node_pool_min_count
  node_pool_max_count    = var.node_pool_max_count
}

module "cloudsql" {
  source       = "./modules/cloudsql"
  project_id   = var.project_id
  region       = var.region
  db_name      = var.db_name
  db_tier      = var.db_tier
}

resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = "investment-mcp"
  description   = "Docker images for investment MCP system"
  format        = "DOCKER"
}
