variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "pod-info"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "pod-info"
}

variable "image" {
  description = "Container image to deploy"
  type        = string
}

variable "replicas" {
  description = "Number of pod replicas"
  type        = number
  default     = 4
}
