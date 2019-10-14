variable "cluster_name" {
  description = "Name of the cluster"
  type = "string"
}

variable "aws_region" {
  type = "string"
}

variable "worker_spot_price" {
  type = "string"
}

variable "worker_type" {
  type = "string"
}

variable "worker_cluster_desired_capacity" {
  type = "string"
}

variable "worker_cluster_min_size" {
  type = "string"
}

variable "worker_cluster_max_size" {
  type = "string"
}