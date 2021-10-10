variable "credentials" {
  type        = string
  description = "Location of the credentials keyfile."
}

variable "project_id" {
  type        = string
  description = "The project ID to host the cluster in."
}

variable "region" {
  type        = string
  description = "The region to host the cluster in."
}

variable "zones" {
  type        = list(string)
  description = "The zones to host the cluster in."
}

variable "name" {
  type        = string
  description = "The name of the cluster."
}

variable "machine_type" {
  type        = string
  description = "Type of the node compute engines."
}

variable "min_count" {
  type        = number
  description = "Minimum number of nodes in the NodePool. Must be >=0 and <= max_node_count."
}

variable "max_count" {
  type        = number
  description = "Maximum number of nodes in the NodePool. Must be >= min_node_count."
}

variable "disk_size_gb" {
  type        = number
  description = "Size of the node's disk."
}

variable "service_account" {
  type        = string
  description = "The service account to run nodes as if not overridden in `node_pools`. The create_service_account variable default value (true) will cause a cluster-specific service account to be created."
}

variable "initial_node_count" {
  type        = number
  description = "The number of nodes to create in this cluster's default node pool."
}

variable "db_instance_name" {
  type        = string
  description = "Name of database instance."
}

variable "db_name" {
  type        = string
  description = "Name of database within the instance."
}

variable "db_tier" {
  type        = string
  description = "The tier (or machine type) for this instance."
}

variable "db_disk_size_gb" {
  type        = number
  description = "The size of data disk, in GB."
}

variable "db_disk_type" {
  type        = string
  description = "The type of data disk: PD_SSD or PD_HDD."
}

variable "db_user" {
  type        = string
  description = "DB username."
}

variable "db_password" {
  type        = string
  description = "DB password."
}

variable "service_account_id" {
  type        = string
  description = "Service account ID for CloudSQL client."
}

variable "kubernetes_sa_name" {
  type        = string
  description = "Kubernetes Service Account name for the project."
}

variable "schedule_topic_name" {
  type        = string
  description = "Pub/Sub Scheduler topic name."
}

variable "schedule_subscription_name" {
  type        = string
  description = "Pub/Sub Scheduler subscription name."
}

variable "schedule" {
  type        = string
  description = "Pub/Sub Scheduler Cron schedule."
}
