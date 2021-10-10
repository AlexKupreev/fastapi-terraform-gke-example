module "gke" {
  source                     = "terraform-google-modules/kubernetes-engine/google"
  version                    = "14.0.1"
  project_id                 = var.project_id
  region                     = var.region
  zones                      = var.zones
  name                       = var.name
  network                    = "default"
  subnetwork                 = "default"
  ip_range_pods              = ""
  ip_range_services          = ""
  http_load_balancing        = true
  horizontal_pod_autoscaling = true
  network_policy             = true
  identity_namespace         = "enabled"

  node_pools = [
    {
      name               = "default-node-pool"
      machine_type       = var.machine_type
      min_count          = var.min_count
      max_count          = var.max_count
      disk_size_gb       = var.disk_size_gb
      disk_type          = "pd-standard"
      image_type         = "COS"
      auto_repair        = true
      auto_upgrade       = true
      service_account    = var.service_account
      preemptible        = false
      initial_node_count = var.initial_node_count
    },
  ]

  node_pools_oauth_scopes = {
    all = []

    default-node-pool = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/cloud-platform.read-only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/appengine.admin",
      "https://www.googleapis.com/auth/pubsub"
    ]
  }

  node_pools_labels = {
    all = {}

    default-node-pool = {
      default-node-pool = true
    }
  }

  node_pools_metadata = {
    all = {}

    default-node-pool = {
      node-pool-metadata-custom-value = "my-node-pool"
    }
  }

  node_pools_taints = {
    all = []

    default-node-pool = [
      {
        key    = "default-node-pool"
        value  = true
        effect = "PREFER_NO_SCHEDULE"
      },
    ]
  }

  node_pools_tags = {
    all = []

    default-node-pool = [
      "default-node-pool",
    ]
  }
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database" "database" {
  project  = var.project_id
  name     = var.db_name
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_database_instance" "instance" {
  project          = var.project_id
  name             = var.db_instance_name
  region           = var.region
  database_version = "POSTGRES_12"
  settings {
    tier      = var.db_tier
    disk_size = var.db_disk_size_gb
    disk_type = var.db_disk_type
    ip_configuration {
      ipv4_enabled    = true
    }
  }

  deletion_protection  = "true"
}

resource "google_sql_user" "users" {
  project  = var.project_id
  instance = var.db_instance_name
  name     = var.db_user
  password = var.db_password
}

resource "google_compute_global_address" "default" {
  name = "global-cluster-ip"
}

resource "google_service_account" "gsa" {
  account_id = var.service_account_id
  project    = var.project_id
}

resource "google_project_iam_member" "cloud-sql-client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gsa.email}"
}

resource "kubernetes_service_account" "ksa" {
  metadata {
    name = var.kubernetes_sa_name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.gsa.email
    }
  }
}

resource "google_service_account_iam_binding" "gke_gsa_ksa_binding" {
  service_account_id = google_service_account.gsa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/${var.kubernetes_sa_name}]"
  ]
}

resource "google_project_service" "pubsub" {
  project = var.project_id
  service = "pubsub.googleapis.com"
}

resource "google_pubsub_topic" "topic" {
  project = var.project_id
  name    = var.schedule_topic_name

  depends_on = [
    google_project_service.pubsub,
  ]
}

resource "google_project_service" "cloudscheduler" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"
}

resource "google_cloud_scheduler_job" "scheduler_pubsub_job" {
  project  = var.project_id
  region   = var.region
  name     = "scheduler-pubsub-job"
  schedule = var.schedule

  pubsub_target {
    topic_name = google_pubsub_topic.topic.id
    data       = base64encode("Schedule ping")
  }

  depends_on = [
    google_project_service.cloudscheduler,
  ]
}

resource "google_pubsub_subscription" "schedule_subscription" {
  name  = var.schedule_subscription_name
  topic = var.schedule_topic_name

  labels = {
    foo = "bar"
  }

  # 20 minutes
  message_retention_duration = "600s"
  retain_acked_messages      = false

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "90000.5s"
  }
  retry_policy {
    minimum_backoff = "10s"
  }

  enable_message_ordering    = false
}

resource "google_pubsub_subscription_iam_member" "scheduler_subscription_binding" {
  project      = var.project_id
  subscription = google_pubsub_subscription.schedule_subscription.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.gsa.email}"
  depends_on = [
    google_pubsub_subscription.schedule_subscription,
  ]
}

resource "google_pubsub_subscription_iam_member" "scheduler_subscription_sa_binding_subscriber" {
  project      = var.project_id
  subscription = google_pubsub_subscription.schedule_subscription.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.gsa.email}"
  depends_on = [
    google_pubsub_subscription.schedule_subscription,
  ]
}

resource "google_pubsub_subscription_iam_member" "scheduler_subscription_sa_binding_viewer" {
  project      = var.project_id
  subscription = google_pubsub_subscription.schedule_subscription.name
  role         = "roles/pubsub.viewer"
  member       = "serviceAccount:${google_service_account.gsa.email}"
  depends_on = [
    google_pubsub_subscription.schedule_subscription,
  ]
}
