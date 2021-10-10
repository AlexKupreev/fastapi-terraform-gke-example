terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.60.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "3.60.0"
    }
  }
  backend "gcs" {
    credentials = "./terraform-gke-keyfile.json"
    bucket      = "fastapi-terraform-gke-example-tf-gke"
    prefix      = "terraform/state"
  }
}
