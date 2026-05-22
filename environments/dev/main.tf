terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "tf-multi-account-state-dev-405903923186"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

# kubernetes provider removed — k8s resources are now managed via kubectl (k8s/)

locals {
  common_tags = {
    Environment = "dev"
    ManagedBy   = "terraform"
    Project     = var.project_name
  }
}

module "vpc" {
  source = "../../modules/vpc"

  name                 = "${var.project_name}-dev"
  cidr_block           = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  tags                 = local.common_tags
}

module "s3_website" {
  source = "../../modules/s3-website"

  bucket_name = "${var.project_name}-dev-website"
  website_dir = "${path.root}/../../website"
  tags        = local.common_tags
}

module "ecr" {
  source = "../../modules/ecr"

  name = "${var.project_name}-dev-pod-info"
  tags = local.common_tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name       = "${var.project_name}-dev"
  private_subnet_ids = module.vpc.private_subnet_ids
  nodes_per_az       = 1
  instance_type      = "t3.medium"
  tags               = local.common_tags
}

# k8s_app module removed — app is now deployed via: kubectl apply -f k8s/
