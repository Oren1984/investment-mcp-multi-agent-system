variable "project_id" { type = string }
variable "region"     { type = string }
variable "db_name"    { type = string }
variable "db_tier"    { type = string }

resource "google_sql_database_instance" "postgres" {
  name             = "investment-mcp-pg"
  database_version = "POSTGRES_16"
  region           = var.region
  project          = var.project_id

  settings {
    tier = var.db_tier

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = "projects/${var.project_id}/global/networks/default"
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "investment_db" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
  project  = var.project_id
}

output "connection_name" { value = google_sql_database_instance.postgres.connection_name }
output "instance_name"   { value = google_sql_database_instance.postgres.name }
