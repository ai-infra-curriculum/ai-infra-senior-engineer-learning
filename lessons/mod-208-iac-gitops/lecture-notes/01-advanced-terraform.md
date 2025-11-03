# Lecture 1: Advanced Terraform

## Learning Objectives

By the end of this lecture, you will be able to:

- Design modular Terraform architectures creating reusable modules for ML infrastructure (GPU clusters, model serving, data pipelines) with proper input validation and outputs
- Implement remote state management using S3/GCS backends with state locking (DynamoDB/Cloud Storage) and encryption preventing concurrent modifications and data loss
- Master advanced HCL features including for_each loops, dynamic blocks, conditional expressions, and local values enabling DRY (Don't Repeat Yourself) infrastructure code
- Configure Terraform workspaces or directory structures organizing multi-environment deployments (dev/staging/prod) with shared modules and environment-specific configurations
- Implement Terraform Cloud/Enterprise workflows with remote execution, policy enforcement (Sentinel), cost estimation, and team collaboration features
- Design ML infrastructure patterns using Terraform provisioning SageMaker, Vertex AI, EKS/GKE GPU clusters, and supporting services (VPC, IAM, storage)
- Optimize Terraform performance using targeted applies, parallelism controls, and resource targeting for large infrastructure codebases (1000+ resources)
- Build Terraform CI/CD pipelines with automated plan, approval gates, automated apply, and drift detection ensuring infrastructure changes follow proper change management

## Table of Contents
1. [Terraform Modules](#terraform-modules)
2. [State Management](#state-management)
3. [Advanced Language Features](#advanced-language-features)
4. [Terraform Cloud and Enterprise](#terraform-cloud-and-enterprise)
5. [ML Infrastructure Examples](#ml-infrastructure-examples)
6. [Best Practices](#best-practices)

## Terraform Modules

Modules are the primary way to package and reuse Terraform configuration. For ML infrastructure, well-designed modules enable teams to provision consistent, tested infrastructure quickly.

### Module Structure

```
terraform-aws-ml-cluster/
├── main.tf              # Primary resource definitions
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── versions.tf          # Terraform and provider versions
├── README.md            # Documentation
├── examples/            # Usage examples
│   └── complete/
│       ├── main.tf
│       └── variables.tf
└── modules/             # Sub-modules
    ├── node-pool/
    ├── networking/
    └── storage/
```

### Creating a Reusable Module

**Example: EKS Cluster Module for ML Workloads**

```hcl
# main.tf
resource "aws_eks_cluster" "ml_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = var.enable_private_endpoint
    endpoint_public_access  = var.enable_public_endpoint
    security_group_ids      = [aws_security_group.cluster.id]
  }

  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = var.cluster_log_types

  tags = merge(
    var.tags,
    {
      "Name"        = var.cluster_name
      "Environment" = var.environment
      "Purpose"     = "ml-infrastructure"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
    aws_cloudwatch_log_group.cluster
  ]
}

# GPU node group for training
resource "aws_eks_node_group" "gpu_nodes" {
  cluster_name    = aws_eks_cluster.ml_cluster.name
  node_group_name = "${var.cluster_name}-gpu-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = var.gpu_node_desired_count
    max_size     = var.gpu_node_max_count
    min_size     = var.gpu_node_min_count
  }

  instance_types = var.gpu_instance_types
  capacity_type  = var.use_spot_instances ? "SPOT" : "ON_DEMAND"

  labels = {
    "workload-type"      = "gpu"
    "node-type"          = "ml-training"
    "nvidia.com/gpu"     = "true"
  }

  taints {
    key    = "nvidia.com/gpu"
    value  = "true"
    effect = "NO_SCHEDULE"
  }

  tags = merge(
    var.tags,
    {
      "k8s.io/cluster-autoscaler/enabled"                = "true"
      "k8s.io/cluster-autoscaler/${var.cluster_name}"    = "owned"
      "k8s.io/cluster-autoscaler/node-template/label/workload-type" = "gpu"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.node_policy,
  ]
}

# CPU node group for inference
resource "aws_eks_node_group" "cpu_nodes" {
  cluster_name    = aws_eks_cluster.ml_cluster.name
  node_group_name = "${var.cluster_name}-cpu-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = var.cpu_node_desired_count
    max_size     = var.cpu_node_max_count
    min_size     = var.cpu_node_min_count
  }

  instance_types = var.cpu_instance_types
  capacity_type  = "ON_DEMAND"

  labels = {
    "workload-type" = "cpu"
    "node-type"     = "ml-inference"
  }

  tags = merge(var.tags, {
    "k8s.io/cluster-autoscaler/enabled" = "true"
    "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
  })
}
```

```hcl
# variables.tf
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.cluster_name))
    error_message = "Cluster name must contain only lowercase alphanumeric characters and hyphens."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"

  validation {
    condition     = can(regex("^1\\.(2[4-9]|[3-9][0-9])$", var.kubernetes_version))
    error_message = "Kubernetes version must be 1.24 or higher."
  }
}

variable "gpu_instance_types" {
  description = "Instance types for GPU nodes"
  type        = list(string)
  default     = ["p3.2xlarge", "p3.8xlarge"]

  validation {
    condition = alltrue([
      for t in var.gpu_instance_types : can(regex("^(p3|p4|g4|g5)\\.", t))
    ])
    error_message = "Must specify GPU instance types (p3, p4, g4, g5 families)."
  }
}

variable "cpu_instance_types" {
  description = "Instance types for CPU nodes"
  type        = list(string)
  default     = ["c5.2xlarge", "c5.4xlarge"]
}

variable "gpu_node_desired_count" {
  description = "Desired number of GPU nodes"
  type        = number
  default     = 2
}

variable "gpu_node_min_count" {
  description = "Minimum number of GPU nodes"
  type        = number
  default     = 0
}

variable "gpu_node_max_count" {
  description = "Maximum number of GPU nodes"
  type        = number
  default     = 10
}

variable "use_spot_instances" {
  description = "Use spot instances for GPU nodes"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
```

```hcl
# outputs.tf
output "cluster_id" {
  description = "EKS cluster ID"
  value       = aws_eks_cluster.ml_cluster.id
}

output "cluster_endpoint" {
  description = "Endpoint for EKS cluster"
  value       = aws_eks_cluster.ml_cluster.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_security_group.cluster.id
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.ml_cluster.certificate_authority[0].data
  sensitive   = true
}

output "gpu_node_group_id" {
  description = "GPU node group ID"
  value       = aws_eks_node_group.gpu_nodes.id
}

output "cpu_node_group_id" {
  description = "CPU node group ID"
  value       = aws_eks_node_group.cpu_nodes.id
}
```

### Module Composition

Compose larger modules from smaller, focused modules:

```hcl
# Root module that composes networking, cluster, and storage
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  environment        = var.environment
  tags               = var.tags
}

module "eks_cluster" {
  source = "./modules/eks-cluster"

  cluster_name          = var.cluster_name
  kubernetes_version    = var.kubernetes_version
  subnet_ids            = module.vpc.private_subnet_ids
  vpc_id                = module.vpc.vpc_id

  gpu_instance_types    = var.gpu_instance_types
  cpu_instance_types    = var.cpu_instance_types

  environment           = var.environment
  tags                  = var.tags

  depends_on = [module.vpc]
}

module "s3_storage" {
  source = "./modules/s3-ml-buckets"

  cluster_name = var.cluster_name
  environment  = var.environment

  # IRSA for S3 access from pods
  oidc_provider_arn = module.eks_cluster.oidc_provider_arn

  tags = var.tags
}

module "monitoring" {
  source = "./modules/monitoring"

  cluster_name = var.cluster_name
  cluster_id   = module.eks_cluster.cluster_id

  prometheus_enabled = var.enable_prometheus
  grafana_enabled    = var.enable_grafana

  tags = var.tags
}
```

## State Management

Proper state management is critical for team collaboration and production operations.

### Remote State Backend

**S3 Backend with DynamoDB Locking:**

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state"
    key            = "ml-infrastructure/eks-cluster/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"
    dynamodb_table = "terraform-state-lock"

    # Enable versioning on the S3 bucket
    versioning     = true
  }
}

# Create backend resources (run once)
# backend-setup.tf
resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-company-terraform-state"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "Terraform State"
    Environment = "global"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform.arn
    }
  }
}

resource "aws_dynamodb_table" "terraform_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock"
    Environment = "global"
  }
}
```

### Workspaces for Multi-Environment

```bash
# Create workspaces for different environments
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch between workspaces
terraform workspace select dev

# List workspaces
terraform workspace list

# Show current workspace
terraform workspace show
```

```hcl
# Use workspace in configuration
locals {
  environment = terraform.workspace

  # Environment-specific configuration
  config = {
    dev = {
      instance_type = "t3.medium"
      node_count    = 2
      enable_backup = false
    }
    staging = {
      instance_type = "c5.xlarge"
      node_count    = 3
      enable_backup = true
    }
    prod = {
      instance_type = "c5.2xlarge"
      node_count    = 5
      enable_backup = true
    }
  }

  env_config = local.config[local.environment]
}

resource "aws_instance" "ml_server" {
  instance_type = local.env_config.instance_type
  count         = local.env_config.node_count

  tags = {
    Name        = "ml-server-${local.environment}-${count.index}"
    Environment = local.environment
  }
}
```

### State Locking and Consistency

```python
# Example: Safely managing Terraform state in CI/CD
import subprocess
import time
import sys

def run_terraform_with_retry(command, max_retries=3):
    """Run terraform command with retry logic for state locking"""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            if "Error acquiring the state lock" in e.stderr:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"State locked, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("Failed to acquire state lock after retries")
                    sys.exit(1)
            else:
                print(f"Terraform error: {e.stderr}")
                sys.exit(1)

# Usage in CI/CD
run_terraform_with_retry(["terraform", "plan", "-out=tfplan"])
run_terraform_with_retry(["terraform", "apply", "tfplan"])
```

## Advanced Language Features

### Dynamic Blocks

Generate repeated nested blocks programmatically:

```hcl
# Without dynamic blocks (repetitive)
resource "aws_security_group" "ml_cluster" {
  name   = "ml-cluster-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  # ... many more rules
}

# With dynamic blocks (concise)
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))

  default = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "HTTPS from VPC"
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "HTTP from VPC"
    },
    {
      from_port   = 6443
      to_port     = 6443
      protocol    = "tcp"
      cidr_blocks = ["10.0.0.0/8"]
      description = "Kubernetes API"
    }
  ]
}

resource "aws_security_group" "ml_cluster" {
  name   = "ml-cluster-sg"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  tags = {
    Name = "ml-cluster-sg"
  }
}
```

### For Each and Count

**Count** creates multiple similar resources:

```hcl
# Create multiple S3 buckets with count
variable "data_buckets" {
  type = list(string)
  default = ["raw-data", "processed-data", "models"]
}

resource "aws_s3_bucket" "ml_data" {
  count  = length(var.data_buckets)
  bucket = "${var.project_name}-${var.data_buckets[count.index]}"

  tags = {
    Name    = var.data_buckets[count.index]
    Purpose = "ml-data-storage"
  }
}

# Access outputs
output "bucket_arns" {
  value = aws_s3_bucket.ml_data[*].arn
}
```

**For Each** creates resources from a map or set:

```hcl
# More flexible with for_each
variable "ml_buckets" {
  type = map(object({
    versioning_enabled = bool
    lifecycle_days     = number
    storage_class      = string
  }))

  default = {
    "raw-data" = {
      versioning_enabled = true
      lifecycle_days     = 90
      storage_class      = "GLACIER"
    }
    "processed-data" = {
      versioning_enabled = true
      lifecycle_days     = 30
      storage_class      = "STANDARD_IA"
    }
    "models" = {
      versioning_enabled = true
      lifecycle_days     = 365
      storage_class      = "STANDARD"
    }
  }
}

resource "aws_s3_bucket" "ml_data" {
  for_each = var.ml_buckets

  bucket = "${var.project_name}-${each.key}"

  tags = {
    Name         = each.key
    Purpose      = "ml-data-storage"
    StorageClass = each.value.storage_class
  }
}

resource "aws_s3_bucket_versioning" "ml_data" {
  for_each = var.ml_buckets

  bucket = aws_s3_bucket.ml_data[each.key].id

  versioning_configuration {
    status = each.value.versioning_enabled ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ml_data" {
  for_each = var.ml_buckets

  bucket = aws_s3_bucket.ml_data[each.key].id

  rule {
    id     = "transition-to-${each.value.storage_class}"
    status = "Enabled"

    transition {
      days          = each.value.lifecycle_days
      storage_class = each.value.storage_class
    }
  }
}

# Access specific bucket
output "models_bucket_arn" {
  value = aws_s3_bucket.ml_data["models"].arn
}
```

### Locals and Functions

```hcl
locals {
  # Common tags applied to all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    CostCenter  = var.cost_center
  }

  # Computed values
  cluster_name = "${var.project_name}-${var.environment}-eks"

  # Conditional logic
  use_gpu = var.environment == "prod" || var.enable_training

  # Transform data structures
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)

  # Complex transformations
  node_groups = {
    for ng in var.node_group_configs : ng.name => {
      instance_types = ng.instance_types
      min_size      = ng.min_size
      max_size      = ng.max_size
      desired_size  = ng.desired_size
      labels        = merge(ng.labels, { environment = var.environment })
    }
  }
}

# Built-in functions
locals {
  # String functions
  uppercase_env = upper(var.environment)
  cluster_fqdn  = format("%s.%s.%s", var.cluster_name, var.environment, var.domain)

  # Collection functions
  all_subnet_ids = concat(var.public_subnet_ids, var.private_subnet_ids)
  unique_regions = distinct(var.regions)
  sorted_azs     = sort(local.availability_zones)

  # Encoding functions
  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    cluster_name = local.cluster_name
    region       = var.region
  }))

  # Type conversion
  node_count    = tonumber(var.node_count_string)
  enable_backup = tobool(var.backup_enabled_string)

  # Filesystem functions
  init_script = file("${path.module}/scripts/init.sh")

  # Date and time
  timestamp = formatdate("YYYY-MM-DD", timestamp())
}
```

### Conditional Expressions

```hcl
# Ternary operator
resource "aws_instance" "ml_training" {
  count = var.enable_training ? 1 : 0

  instance_type = var.environment == "prod" ? "p3.8xlarge" : "p3.2xlarge"
  ami           = var.ami_id != "" ? var.ami_id : data.aws_ami.latest.id

  tags = {
    Name = var.environment == "prod" ? "ml-training-prod" : "ml-training-dev"
  }
}

# Conditional resource creation
resource "aws_cloudwatch_log_group" "application" {
  count = var.enable_logging ? 1 : 0

  name              = "/aws/eks/${var.cluster_name}/application"
  retention_in_days = var.log_retention_days
}

# Conditional module
module "cdn" {
  source = "./modules/cloudfront"
  count  = var.enable_cdn ? 1 : 0

  domain_name = var.domain_name
  origin_id   = module.s3_bucket.bucket_regional_domain_name
}
```

## Terraform Cloud and Enterprise

### Workspace Management

```hcl
# Configure Terraform Cloud backend
terraform {
  cloud {
    organization = "my-company"

    workspaces {
      # Can specify by name or tags
      name = "ml-infrastructure-prod"

      # Or use tags for dynamic workspace selection
      # tags = ["ml", "production"]
    }
  }
}
```

### Sentinel Policies (Enterprise)

```python
# Sentinel policy to enforce tagging
import "tfplan/v2" as tfplan

# Required tags for all resources
required_tags = ["Environment", "Project", "CostCenter", "Owner"]

# Get all resources that support tags
all_resources = filter tfplan.resource_changes as _, rc {
  rc.mode is "managed" and
  rc.change.actions is not ["delete"]
}

# Validation function
validate_tags = func(resource) {
  if "tags" not in resource.change.after {
    return false
  }

  for required_tags as tag {
    if tag not in keys(resource.change.after.tags) {
      return false
    }
  }

  return true
}

# Check all resources
violations = filter all_resources as _, resource {
  not validate_tags(resource)
}

# Policy enforcement
main = rule {
  length(violations) is 0
}
```

### Remote Execution

```yaml
# GitHub Actions workflow for Terraform Cloud
name: Terraform Cloud
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TF_CLOUD_ORGANIZATION: "my-company"
  TF_WORKSPACE: "ml-infrastructure-prod"
  TF_API_TOKEN: ${{ secrets.TF_API_TOKEN }}

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}
          terraform_version: 1.6.0

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        run: terraform plan -no-color

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
```

## ML Infrastructure Examples

### Complete ML Training Infrastructure

```hcl
# main.tf - Complete ML training environment
module "ml_training_infrastructure" {
  source = "./modules/ml-training"

  # Network configuration
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  # Cluster configuration
  cluster_name       = "ml-training-prod"
  kubernetes_version = "1.28"

  # GPU node pool for training
  gpu_node_pool = {
    instance_types = ["p3.8xlarge", "p3.16xlarge"]
    min_size       = 0
    max_size       = 20
    desired_size   = 2
    disk_size      = 500

    labels = {
      workload-type = "training"
      gpu-type      = "v100"
    }

    taints = [{
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NO_SCHEDULE"
    }]
  }

  # CPU node pool for preprocessing
  cpu_node_pool = {
    instance_types = ["c5.4xlarge"]
    min_size       = 2
    max_size       = 10
    desired_size   = 3
    disk_size      = 200

    labels = {
      workload-type = "preprocessing"
    }
  }

  # Storage configuration
  data_buckets = {
    raw_data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 90
      intelligent_tier = true
    }
    processed_data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 30
      intelligent_tier = true
    }
    model_artifacts = {
      versioning       = true
      encryption       = "aws:kms"
      lifecycle_days   = 365
      intelligent_tier = false
    }
  }

  # EFS for shared storage
  enable_efs = true
  efs_config = {
    performance_mode = "generalPurpose"
    throughput_mode  = "bursting"
    encrypted        = true
  }

  # Monitoring and observability
  monitoring = {
    prometheus_enabled        = true
    grafana_enabled          = true
    prometheus_retention_days = 30

    log_types = [
      "api",
      "audit",
      "authenticator",
      "controllerManager",
      "scheduler"
    ]
  }

  # Add-ons
  addons = {
    cluster_autoscaler = true
    nvidia_device_plugin = true
    aws_load_balancer_controller = true
    ebs_csi_driver = true
    efs_csi_driver = true
  }

  # Tags
  tags = {
    Project     = "ml-platform"
    Environment = "production"
    CostCenter  = "ml-engineering"
    Owner       = "ml-infrastructure-team"
  }
}
```

## Best Practices

### 1. Module Design Principles

- **Single Responsibility**: Each module should do one thing well
- **Reusability**: Design for multiple use cases
- **Composability**: Modules should work together
- **Documentation**: Clear README with examples
- **Versioning**: Use semantic versioning for modules

### 2. State Management

- **Remote State**: Always use remote state for teams
- **State Locking**: Enable locking to prevent conflicts
- **Encryption**: Encrypt state at rest and in transit
- **Backup**: Enable versioning on state storage
- **Separation**: Separate state by environment and component

### 3. Security

- **Sensitive Data**: Mark outputs as sensitive
- **Least Privilege**: Use minimal IAM permissions
- **Encryption**: Enable encryption for all resources
- **Secrets**: Never commit secrets; use secret management
- **Network**: Follow zero-trust principles

### 4. CI/CD Integration

- **Automated Testing**: Test all changes before apply
- **Plan Review**: Require manual approval for apply
- **Drift Detection**: Regularly check for drift
- **Documentation**: Auto-generate documentation
- **Rollback**: Have rollback procedures

### 5. Code Organization

```
terraform-infrastructure/
├── modules/              # Reusable modules
│   ├── networking/
│   ├── compute/
│   └── storage/
├── environments/         # Environment-specific configs
│   ├── dev/
│   ├── staging/
│   └── prod/
├── global/              # Global resources
│   ├── iam/
│   └── dns/
└── scripts/             # Helper scripts
```

## Summary

Advanced Terraform enables:
- Building reusable, composable infrastructure modules
- Managing state safely across teams
- Leveraging powerful language features for flexibility
- Integrating with Terraform Cloud/Enterprise
- Implementing infrastructure best practices

**Key Takeaways:**
1. Design modules for reusability and composition
2. Use remote state with locking for team collaboration
3. Leverage advanced features (for_each, dynamic blocks)
4. Implement proper security and access controls
5. Integrate with CI/CD for automation
6. Follow consistent code organization patterns

## Next Steps

- Continue to [Lecture 2: Pulumi Infrastructure](02-pulumi-infrastructure.md)
- Practice building reusable modules
- Implement remote state management
- Set up Terraform Cloud workspace

## Additional Resources

- [Terraform Module Registry](https://registry.terraform.io/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)
- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
