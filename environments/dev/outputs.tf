output "website_url" {
  description = "Static website URL"
  value       = module.s3_website.website_url
}

output "ecr_org_repository_url" {
  description = "ECR repository URL for org-service"
  value       = module.ecr_org.repository_url
}

output "ecr_telemetry_repository_url" {
  description = "ECR repository URL for telemetry-service"
  value       = module.ecr_telemetry.repository_url
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}
