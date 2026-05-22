# Terraform Playground

AWS infrastructure boilerplate with multi-environment support using Terraform modules.

## Structure

```
terraform-playground/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── modules/
    └── vpc/
```

Each environment is independently managed with its own remote state backend. Shared infrastructure logic lives in reusable modules under `modules/`.

---

## Dev Environment URLs

| Resource | URL |
|---|---|
| Website | http://tf-multi-account-dev-website.s3-website-us-east-1.amazonaws.com |
| API (org) | http://k8s-podinfo-podinfo-9d6b09e164-1705600783.us-east-1.elb.amazonaws.com/org |
| API (telemetry) | http://k8s-podinfo-podinfo-9d6b09e164-1705600783.us-east-1.elb.amazonaws.com/telemetry |

---

## Architecture

```
                                    AWS us-east-1
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│   S3 (Static Website)                                                         │
│   ┌─────────────────────────────┐                                             │
│   │  index.html                 │                                             │
│   │  [Organization] [Telemetry] │                                             │
│   └──────────────┬──────────────┘                                             │
│                  │ JS fetch /org  /telemetry                                  │
│                  ▼                                                             │
│   ALB (internet-facing)                                                       │
│   ┌─────────────────────────────┐                                             │
│   │  /org       → org-service   │                                             │
│   │  /telemetry → tel-service   │                                             │
│   └──────────┬──────────────────┘                                             │
│              │                                                                │
│   VPC  10.0.0.0/16                                                            │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │  Public Subnets                                                      │   │
│   │  ┌──────────────────────────┐  ┌──────────────────────────┐         │   │
│   │  │ us-east-1a 10.0.1.0/24  │  │ us-east-1b 10.0.2.0/24  │         │   │
│   │  │  NAT Gateway             │  │                          │         │   │
│   │  └──────────────────────────┘  └──────────────────────────┘         │   │
│   │            │                                                         │   │
│   │  Private Subnets           EKS Cluster: tf-multi-account-dev        │   │
│   │  ┌──────────────────────────────────────────────────────────────┐   │   │
│   │  │                                                              │   │   │
│   │  │  us-east-1a 10.0.11.0/24     us-east-1b 10.0.12.0/24       │   │   │
│   │  │  ┌────────────────────┐      ┌────────────────────┐         │   │   │
│   │  │  │  Node (t3.medium)  │      │  Node (t3.medium)  │         │   │   │
│   │  │  │                    │      │                    │         │   │   │
│   │  │  │  ┌─────────────┐   │      │  ┌─────────────┐   │         │   │   │
│   │  │  │  │  org-pod    │   │      │  │  org-pod    │   │         │   │   │
│   │  │  │  │  (replica1) │   │      │  │  (replica2) │   │         │   │   │
│   │  │  │  └─────────────┘   │      │  └─────────────┘   │         │   │   │
│   │  │  │  ┌─────────────┐   │      │  ┌─────────────┐   │         │   │   │
│   │  │  │  │  tel-pod    │   │      │  │  tel-pod    │   │         │   │   │
│   │  │  │  │  (replica1) │   │      │  │  (replica2) │   │         │   │   │
│   │  │  │  └─────────────┘   │      │  └─────────────┘   │         │   │   │
│   │  │  └────────────────────┘      └────────────────────┘         │   │   │
│   │  │                                                              │   │   │
│   │  │  Services (NodePort)                                         │   │   │
│   │  │  org-service ──────────────────▶ org pods                   │   │   │
│   │  │  tel-service ──────────────────▶ tel pods                   │   │   │
│   │  │                                                              │   │   │
│   │  └──────────────────────────────────────────────────────────────┘   │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│   ECR                                                                         │
│   ┌─────────────────────────────────────────────────────┐                    │
│   │  tf-multi-account-dev-org-pod-info:latest           │                    │
│   │  tf-multi-account-dev-telemetry-pod-info:latest     │                    │
│   └─────────────────────────────────────────────────────┘                    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

  Terraform manages:          kubectl manages:
  VPC, EKS, ECR, S3          Namespace, Deployments, Services, Ingress
```

---

## Prerequisites

| Requirement | Version | Install |
|-------------|---------|---------|
| Terraform | >= 1.5.0 | https://developer.hashicorp.com/terraform/install |
| AWS CLI | >= 2.0 | https://aws.amazon.com/cli/ |
| AWS credentials | — | `aws configure` or environment variables |

Verify your setup:

```bash
terraform -version
aws --version
aws sts get-caller-identity
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd terraform-playground
```

### 2. Create remote state resources

Each environment needs an S3 bucket for state storage and a DynamoDB table for state locking. Run the following once per environment (replace `dev` with `staging` or `prod` as needed):

```bash
# Create S3 bucket
aws s3api create-bucket \
  --bucket my-terraform-state-dev \
  --region us-east-1

# Enable versioning on the bucket
aws s3api put-bucket-versioning \
  --bucket my-terraform-state-dev \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking (shared across environments)
aws dynamodb create-table \
  --table-name terraform-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3. Update backend configuration

In each `environments/<env>/main.tf`, update the `backend "s3"` block with your actual bucket name:

```hcl
backend "s3" {
  bucket         = "your-actual-bucket-name"
  key            = "dev/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-lock"
  encrypt        = true
}
```

### 4. Update variables

Edit `environments/<env>/terraform.tfvars` with your project name and desired CIDR ranges:

```hcl
project_name = "your-project-name"
aws_region   = "us-east-1"
```

---

## Command Examples

### Initialize an environment

Downloads required providers and configures the backend:

```bash
cd environments/dev
terraform init
```

### Preview changes

Shows what Terraform will create, update, or destroy without applying:

```bash
terraform plan
```

### Apply changes

Provisions the infrastructure:

```bash
terraform apply
```

To apply without an interactive prompt:

```bash
terraform apply -auto-approve
```

### Destroy resources

Tears down all resources managed by the current environment:

```bash
terraform destroy
```

### Format and validate

```bash
terraform fmt -recursive   # auto-format all .tf files
terraform validate         # check configuration syntax
```

---

## Environments

| Environment | VPC CIDR    | AZs |
|-------------|-------------|-----|
| dev         | 10.0.0.0/16 | 2   |
| staging     | 10.1.0.0/16 | 2   |
| prod        | 10.2.0.0/16 | 3   |

---

## Modules

### `modules/vpc`

Creates a VPC with public/private subnets, an internet gateway, and route tables.

**Inputs**

| Name | Description |
|------|-------------|
| `name` | Name prefix for all resources |
| `cidr_block` | VPC CIDR block |
| `public_subnet_cidrs` | List of public subnet CIDRs |
| `private_subnet_cidrs` | List of private subnet CIDRs |
| `availability_zones` | List of availability zones |
| `tags` | Tags to apply to all resources |

**Outputs**

| Name | Description |
|------|-------------|
| `vpc_id` | The VPC ID |
| `public_subnet_ids` | List of public subnet IDs |
| `private_subnet_ids` | List of private subnet IDs |
