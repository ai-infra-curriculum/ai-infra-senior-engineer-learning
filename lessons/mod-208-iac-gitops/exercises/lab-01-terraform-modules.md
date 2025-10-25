# Lab 1: Building Terraform Modules for ML Infrastructure

## Objectives

- Design and implement reusable Terraform modules
- Create an EKS/GKE cluster with GPU node pools
- Implement remote state management
- Test modules with Terratest

## Duration

6 hours

## Prerequisites

- Terraform 1.6+ installed
- AWS CLI configured (or GCP/Azure)
- Go 1.21+ installed (for Terratest)
- kubectl installed
- Basic understanding of Kubernetes

## Lab Overview

You'll build a complete ML infrastructure module that provisions:
1. VPC with public/private subnets
2. EKS cluster with GPU and CPU node groups
3. S3 buckets for ML data
4. IAM roles and policies
5. Monitoring and logging

## Part 1: Project Structure

Create the project structure:

```bash
mkdir -p terraform-ml-infrastructure/{modules,environments,test}
cd terraform-ml-infrastructure

# Create module directories
mkdir -p modules/{vpc,eks-cluster,s3-ml-buckets,iam}
mkdir -p environments/{dev,staging,prod}
mkdir -p test
```

## Part 2: VPC Module

Create `modules/vpc/main.tf`:

```hcl
# modules/vpc/main.tf
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Tags for all resources"
  type        = map(string)
  default     = {}
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name        = "${var.environment}-ml-vpc"
    Environment = var.environment
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name                                           = "${var.environment}-public-${var.availability_zones[count.index]}"
    "kubernetes.io/role/elb"                       = "1"
    "kubernetes.io/cluster/${var.environment}-eks" = "shared"
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.tags, {
    Name                                           = "${var.environment}-private-${var.availability_zones[count.index]}"
    "kubernetes.io/role/internal-elb"              = "1"
    "kubernetes.io/cluster/${var.environment}-eks" = "shared"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${var.environment}-igw"
  })
}

# NAT Gateway EIPs
resource "aws_eip" "nat" {
  count = length(var.availability_zones)

  domain = "vpc"

  tags = merge(var.tags, {
    Name = "${var.environment}-nat-eip-${var.availability_zones[count.index]}"
  })

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.tags, {
    Name = "${var.environment}-nat-${var.availability_zones[count.index]}"
  })

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-public-rt"
  })
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Route Tables
resource "aws_route_table" "private" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-private-rt-${var.availability_zones[count.index]}"
  })
}

# Private Route Table Associations
resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}
```

Create `modules/vpc/variables.tf`, `modules/vpc/outputs.tf`, and `modules/vpc/versions.tf`.

## Part 3: EKS Cluster Module

Create `modules/eks-cluster/main.tf`:

```hcl
# modules/eks-cluster/main.tf
variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for node groups"
  type        = list(string)
}

variable "gpu_instance_types" {
  description = "GPU instance types"
  type        = list(string)
  default     = ["p3.2xlarge"]
}

variable "gpu_node_desired_size" {
  description = "Desired GPU node count"
  type        = number
  default     = 2
}

variable "gpu_node_min_size" {
  description = "Minimum GPU node count"
  type        = number
  default     = 0
}

variable "gpu_node_max_size" {
  description = "Maximum GPU node count"
  type        = number
  default     = 10
}

# ... (rest of EKS module implementation)
# Include: IAM roles, security groups, cluster, node groups, etc.
```

## Part 4: S3 Buckets Module

Create `modules/s3-ml-buckets/main.tf`:

```hcl
# modules/s3-ml-buckets/main.tf
variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "bucket_configs" {
  description = "Configuration for ML data buckets"
  type = map(object({
    versioning       = bool
    encryption       = string
    lifecycle_days   = number
    intelligent_tier = bool
  }))

  default = {
    raw-data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 90
      intelligent_tier = true
    }
    processed-data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 30
      intelligent_tier = true
    }
    models = {
      versioning       = true
      encryption       = "aws:kms"
      lifecycle_days   = 365
      intelligent_tier = false
    }
  }
}

# Create buckets
resource "aws_s3_bucket" "ml_data" {
  for_each = var.bucket_configs

  bucket = "${var.project_name}-${each.key}"

  tags = {
    Name    = each.key
    Purpose = "ml-data-storage"
  }
}

# Versioning
resource "aws_s3_bucket_versioning" "ml_data" {
  for_each = var.bucket_configs

  bucket = aws_s3_bucket.ml_data[each.key].id

  versioning_configuration {
    status = each.value.versioning ? "Enabled" : "Disabled"
  }
}

# Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_data" {
  for_each = var.bucket_configs

  bucket = aws_s3_bucket.ml_data[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = each.value.encryption
    }
  }
}

# Lifecycle policies
resource "aws_s3_bucket_lifecycle_configuration" "ml_data" {
  for_each = var.bucket_configs

  bucket = aws_s3_bucket.ml_data[each.key].id

  rule {
    id     = "transition-rule"
    status = "Enabled"

    transition {
      days          = each.value.lifecycle_days
      storage_class = each.value.intelligent_tier ? "INTELLIGENT_TIERING" : "GLACIER"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "ml_data" {
  for_each = var.bucket_configs

  bucket = aws_s3_bucket.ml_data[each.key].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Outputs
output "bucket_names" {
  description = "Map of bucket names"
  value       = {for k, v in aws_s3_bucket.ml_data : k => v.id}
}

output "bucket_arns" {
  description = "Map of bucket ARNs"
  value       = {for k, v in aws_s3_bucket.ml_data : k => v.arn}
}
```

## Part 5: Root Module

Create `environments/dev/main.tf`:

```hcl
# environments/dev/main.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "ml-infrastructure/dev/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      Environment = "dev"
      Project     = "ml-infrastructure"
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  environment = "dev"
  azs         = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = {
    Environment = local.environment
    Project     = "ml-infrastructure"
    CostCenter  = "ml-engineering"
  }
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr           = "10.0.0.0/16"
  availability_zones = local.azs
  environment        = local.environment
  tags               = local.tags
}

# EKS Cluster Module
module "eks_cluster" {
  source = "../../modules/eks-cluster"

  cluster_name       = "${local.environment}-ml-cluster"
  kubernetes_version = "1.28"
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  gpu_instance_types    = ["p3.2xlarge"]
  gpu_node_desired_size = 2
  gpu_node_min_size     = 0
  gpu_node_max_size     = 5

  tags = local.tags

  depends_on = [module.vpc]
}

# S3 Buckets Module
module "s3_buckets" {
  source = "../../modules/s3-ml-buckets"

  project_name = "${local.environment}-ml"

  bucket_configs = {
    raw-data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 30
      intelligent_tier = true
    }
    processed-data = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 15
      intelligent_tier = true
    }
    models = {
      versioning       = true
      encryption       = "AES256"
      lifecycle_days   = 90
      intelligent_tier = false
    }
  }
}

# Outputs
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "cluster_name" {
  value = module.eks_cluster.cluster_name
}

output "bucket_names" {
  value = module.s3_buckets.bucket_names
}
```

## Part 6: Testing with Terratest

Create `test/ml_infrastructure_test.go`:

```go
// test/ml_infrastructure_test.go
package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/aws"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestMLInfrastructure(t *testing.T) {
	t.Parallel()

	// Construct options
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../environments/dev",
		Vars: map[string]interface{}{
			"environment": "test",
		},
	})

	// Cleanup
	defer terraform.Destroy(t, terraformOptions)

	// Deploy
	terraform.InitAndApply(t, terraformOptions)

	// Test VPC
	t.Run("VPC", func(t *testing.T) {
		vpcID := terraform.Output(t, terraformOptions, "vpc_id")
		assert.NotEmpty(t, vpcID)

		vpc := aws.GetVpcById(t, vpcID, "us-west-2")
		assert.Equal(t, "10.0.0.0/16", vpc.CidrBlock)
	})

	// Test S3 Buckets
	t.Run("S3_Buckets", func(t *testing.T) {
		bucketNames := terraform.OutputMap(t, terraformOptions, "bucket_names")

		for _, bucketName := range bucketNames {
			// Check bucket exists
			aws.AssertS3BucketExists(t, "us-west-2", bucketName)

			// Check versioning
			versioning := aws.GetS3BucketVersioning(t, "us-west-2", bucketName)
			assert.Equal(t, "Enabled", versioning)

			// Check encryption
			encryption := aws.GetS3BucketEncryption(t, "us-west-2", bucketName)
			assert.NotNil(t, encryption)
		}
	})

	// Test EKS Cluster
	t.Run("EKS_Cluster", func(t *testing.T) {
		clusterName := terraform.Output(t, terraformOptions, "cluster_name")
		assert.NotEmpty(t, clusterName)

		cluster := aws.GetEksCluster(t, "us-west-2", clusterName)
		assert.Equal(t, "ACTIVE", *cluster.Status)
	})
}
```

## Part 7: Deployment

```bash
# Initialize Terraform
cd environments/dev
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Verify
terraform output

# Test with Terratest
cd ../../test
go test -v -timeout 30m
```

## Exercises

### Exercise 1: Add Monitoring Module
Create a module that deploys Prometheus and Grafana using Helm.

### Exercise 2: Implement Cost Estimation
Add a script that estimates monthly costs for the infrastructure.

### Exercise 3: Multi-Environment Support
Extend the modules to support production with higher redundancy and different instance types.

### Exercise 4: Add Compliance Checks
Implement Terratest tests that verify compliance requirements (encryption, tagging, etc.).

## Submission

Submit:
1. Complete module code
2. Terraform plan output
3. Terratest results
4. Cost estimation report

## Success Criteria

- All modules deploy successfully
- Tests pass
- Infrastructure follows best practices
- Resources are properly tagged
- State is stored remotely
- Documentation is complete

## Resources

- [Terraform Module Documentation](https://www.terraform.io/docs/modules/index.html)
- [Terratest Documentation](https://terratest.gruntwork.io/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
