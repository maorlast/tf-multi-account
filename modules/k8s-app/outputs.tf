output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.this.metadata[0].name
}

output "service_name" {
  description = "Kubernetes service name"
  value       = kubernetes_service.this.metadata[0].name
}
