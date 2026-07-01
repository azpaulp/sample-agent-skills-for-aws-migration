# Fixture: app-engine-migration
#
# Purpose: Validate that App Engine maps to Elastic Beanstalk by default.
# Contains resources that trigger Elastic Beanstalk as the AWS target:
#   - App Engine application → must map to Elastic Beanstalk (PaaS-to-PaaS)
#   - Cloud Storage → must map to S3 (unchanged from other fixtures)
#   - Service Account → must map to IAM Role (unchanged)
#
# Resources:
#   PRIMARY:   google_app_engine_application
#   SECONDARY: google_storage_bucket, google_service_account

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "app-engine-test-project"
  region  = "us-central1"
}

# --- App Engine (should map to Elastic Beanstalk) ---

resource "google_app_engine_application" "app" {
  project     = "app-engine-test-project"
  location_id = "us-central"

  feature_settings {
    split_health_checks = true
  }
}

resource "google_app_engine_standard_app_version" "api_v1" {
  project    = "app-engine-test-project"
  service    = "default"
  version_id = "v1"
  runtime    = "python39"

  entrypoint {
    shell = "gunicorn -b :$PORT main:app"
  }

  deployment {
    zip {
      source_url = "https://storage.googleapis.com/app-engine-test-project/api-v1.zip"
    }
  }

  instance_class = "F2"

  automatic_scaling {
    min_idle_instances  = 1
    max_idle_instances  = 3
    min_pending_latency = "1s"
    max_pending_latency = "5s"
  }
}

# --- Supporting resources ---

resource "google_storage_bucket" "assets" {
  name     = "app-engine-test-assets"
  location = "US"

  versioning {
    enabled = true
  }
}

resource "google_service_account" "app_sa" {
  account_id   = "app-engine-sa"
  display_name = "App Engine Service Account"
}
