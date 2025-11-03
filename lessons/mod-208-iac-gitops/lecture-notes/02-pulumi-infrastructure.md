# Lecture 2: Pulumi Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:

- Design infrastructure-as-code solutions using Pulumi with Python, TypeScript, or Go leveraging programming language features (loops, conditionals, functions) for dynamic infrastructure
- Architect Pulumi stack management strategies organizing environments (dev/staging/prod) with shared components, stack references, and configuration management
- Implement ML infrastructure with Pulumi provisioning GPU clusters, managed ML services (SageMaker, Vertex AI), and data pipelines using cloud-native providers
- Configure Pulumi automation API building self-service infrastructure platforms enabling developers to provision resources programmatically via REST APIs
- Design component resources creating reusable infrastructure abstractions (ML training cluster, model serving endpoint) with encapsulated logic and validation
- Implement Pulumi testing strategies using unit tests, integration tests, and policy tests validating infrastructure code before deployment
- Architect multi-cloud Pulumi programs using provider abstractions deploying identical infrastructure patterns across AWS, GCP, and Azure
- Build CI/CD pipelines for Pulumi with automated previews, approval workflows, state management, and rollback capabilities for production infrastructure changes

## Table of Contents
1. [Pulumi Fundamentals](#pulumi-fundamentals)
2. [Language Support](#language-support)
3. [Comparison with Terraform](#comparison-with-terraform)
4. [Stack and Configuration Management](#stack-and-configuration-management)
5. [ML Infrastructure with Pulumi](#ml-infrastructure-with-pulumi)
6. [Advanced Patterns](#advanced-patterns)

## Pulumi Fundamentals

Pulumi enables infrastructure as code using familiar programming languages (Python, TypeScript, Go, C#). This allows leveraging existing programming skills, tools, and ecosystems.

### Core Concepts

**Resources**: Cloud infrastructure components
**Stacks**: Isolated instances of your program
**Projects**: Pulumi programs and metadata
**Outputs**: Values exported from your infrastructure
**State**: Current state of your infrastructure

### Getting Started

```bash
# Install Pulumi
curl -fsSL https://get.pulumi.com | sh

# Create new project
pulumi new aws-python

# Directory structure created:
# ├── __main__.py          # Program entry point
# ├── Pulumi.yaml          # Project metadata
# ├── requirements.txt     # Python dependencies
# └── venv/               # Python virtual environment
```

**Pulumi.yaml**:
```yaml
name: ml-infrastructure
runtime: python
description: ML infrastructure on AWS
```

### Basic Example

```python
# __main__.py
import pulumi
import pulumi_aws as aws

# Create an S3 bucket
bucket = aws.s3.Bucket('ml-data-bucket',
    bucket='my-ml-data-bucket',
    acl='private',
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
    server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
        rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm='AES256',
            ),
        ),
    ),
    tags={
        'Name': 'ML Data Bucket',
        'Environment': 'production',
    }
)

# Export the bucket name
pulumi.export('bucket_name', bucket.id)
pulumi.export('bucket_arn', bucket.arn)
```

```bash
# Deploy infrastructure
pulumi up

# View outputs
pulumi stack output bucket_name

# Destroy infrastructure
pulumi destroy
```

## Language Support

Pulumi supports multiple languages, each with native SDK support.

### Python Example: EKS Cluster

```python
# eks_cluster.py
import pulumi
import pulumi_aws as aws
import pulumi_eks as eks

# Configuration
config = pulumi.Config()
cluster_name = config.get('cluster_name') or 'ml-cluster'
min_nodes = config.get_int('min_nodes') or 2
max_nodes = config.get_int('max_nodes') or 10
desired_nodes = config.get_int('desired_nodes') or 3

# Create VPC
vpc = aws.ec2.Vpc('ml-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={'Name': f'{cluster_name}-vpc'}
)

# Create subnets across availability zones
availability_zones = aws.get_availability_zones(state='available').names[:3]

public_subnets = []
private_subnets = []

for i, az in enumerate(availability_zones):
    # Public subnet
    public_subnet = aws.ec2.Subnet(f'public-subnet-{i}',
        vpc_id=vpc.id,
        cidr_block=f'10.0.{i}.0/24',
        availability_zone=az,
        map_public_ip_on_launch=True,
        tags={
            'Name': f'{cluster_name}-public-{az}',
            'kubernetes.io/role/elb': '1',
        }
    )
    public_subnets.append(public_subnet)

    # Private subnet
    private_subnet = aws.ec2.Subnet(f'private-subnet-{i}',
        vpc_id=vpc.id,
        cidr_block=f'10.0.{100+i}.0/24',
        availability_zone=az,
        tags={
            'Name': f'{cluster_name}-private-{az}',
            'kubernetes.io/role/internal-elb': '1',
        }
    )
    private_subnets.append(private_subnet)

# Internet Gateway
igw = aws.ec2.InternetGateway('igw',
    vpc_id=vpc.id,
    tags={'Name': f'{cluster_name}-igw'}
)

# NAT Gateways (one per AZ for HA)
nat_gateways = []
for i, public_subnet in enumerate(public_subnets):
    eip = aws.ec2.Eip(f'nat-eip-{i}',
        domain='vpc',
        tags={'Name': f'{cluster_name}-nat-eip-{i}'}
    )

    nat = aws.ec2.NatGateway(f'nat-{i}',
        allocation_id=eip.id,
        subnet_id=public_subnet.id,
        tags={'Name': f'{cluster_name}-nat-{i}'}
    )
    nat_gateways.append(nat)

# Route tables
public_rt = aws.ec2.RouteTable('public-rt',
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block='0.0.0.0/0',
        gateway_id=igw.id,
    )],
    tags={'Name': f'{cluster_name}-public-rt'}
)

# Associate public subnets with public route table
for i, subnet in enumerate(public_subnets):
    aws.ec2.RouteTableAssociation(f'public-rta-{i}',
        subnet_id=subnet.id,
        route_table_id=public_rt.id
    )

# Private route tables (one per AZ)
for i, (subnet, nat) in enumerate(zip(private_subnets, nat_gateways)):
    private_rt = aws.ec2.RouteTable(f'private-rt-{i}',
        vpc_id=vpc.id,
        routes=[aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            nat_gateway_id=nat.id,
        )],
        tags={'Name': f'{cluster_name}-private-rt-{i}'}
    )

    aws.ec2.RouteTableAssociation(f'private-rta-{i}',
        subnet_id=subnet.id,
        route_table_id=private_rt.id
    )

# Create EKS cluster using eks package
cluster = eks.Cluster('ml-eks-cluster',
    name=cluster_name,
    vpc_id=vpc.id,
    subnet_ids=[s.id for s in private_subnets],
    instance_type='t3.medium',
    desired_capacity=desired_nodes,
    min_size=min_nodes,
    max_size=max_nodes,
    node_associate_public_ip_address=False,
    tags={
        'Name': cluster_name,
        'Environment': 'production',
    }
)

# GPU node group for ML training
gpu_node_group = eks.NodeGroup('gpu-nodes',
    cluster=cluster.core,
    instance_type='p3.2xlarge',
    desired_capacity=2,
    min_size=0,
    max_size=10,
    labels={
        'workload-type': 'gpu',
        'node-type': 'ml-training',
    },
    taints=[{
        'key': 'nvidia.com/gpu',
        'value': 'true',
        'effect': 'NoSchedule',
    }],
    tags={
        'k8s.io/cluster-autoscaler/enabled': 'true',
        'k8s.io/cluster-autoscaler/node-template/label/workload-type': 'gpu',
    }
)

# Export cluster details
pulumi.export('cluster_name', cluster.core.cluster.name)
pulumi.export('kubeconfig', cluster.kubeconfig)
pulumi.export('cluster_endpoint', cluster.core.cluster.endpoint)
pulumi.export('cluster_security_group', cluster.core.cluster.vpc_config.cluster_security_group_id)
```

### TypeScript Example

```typescript
// index.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as eks from "@pulumi/eks";

// Configuration
const config = new pulumi.Config();
const clusterName = config.get("clusterName") || "ml-cluster";
const nodeCount = config.getNumber("nodeCount") || 3;

// Create VPC
const vpc = new aws.ec2.Vpc("ml-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: { Name: `${clusterName}-vpc` },
});

// Create EKS cluster
const cluster = new eks.Cluster("ml-cluster", {
    vpcId: vpc.id,
    instanceType: "t3.medium",
    desiredCapacity: nodeCount,
    minSize: 2,
    maxSize: 10,
    deployDashboard: false,
    enabledClusterLogTypes: [
        "api",
        "audit",
        "authenticator",
    ],
});

// Create node group with GPU instances
const gpuNodeGroup = cluster.createNodeGroup("gpu-nodes", {
    instanceType: "p3.2xlarge",
    desiredCapacity: 2,
    minSize: 0,
    maxSize: 5,
    labels: {
        "workload-type": "gpu",
        "nvidia.com/gpu": "true",
    },
    taints: [{
        key: "nvidia.com/gpu",
        value: "true",
        effect: "NoSchedule",
    }],
});

// S3 buckets for ML data
interface BucketConfig {
    versioning: boolean;
    lifecycleDays: number;
    storageClass: string;
}

const buckets: { [key: string]: BucketConfig } = {
    "raw-data": {
        versioning: true,
        lifecycleDays: 90,
        storageClass: "GLACIER",
    },
    "processed-data": {
        versioning: true,
        lifecycleDays: 30,
        storageClass: "STANDARD_IA",
    },
    "models": {
        versioning: true,
        lifecycleDays: 365,
        storageClass: "STANDARD",
    },
};

// Create buckets
const mlBuckets = Object.entries(buckets).map(([name, config]) => {
    const bucket = new aws.s3.Bucket(`${name}-bucket`, {
        bucket: `${clusterName}-${name}`,
        acl: "private",
        versioning: {
            enabled: config.versioning,
        },
        lifecycleRules: [{
            enabled: true,
            transitions: [{
                days: config.lifecycleDays,
                storageClass: config.storageClass,
            }],
        }],
        serverSideEncryptionConfiguration: {
            rule: {
                applyServerSideEncryptionByDefault: {
                    sseAlgorithm: "AES256",
                },
            },
        },
        tags: {
            Name: name,
            Purpose: "ml-data-storage",
        },
    });

    return { name, bucket };
});

// Exports
export const clusterId = cluster.core.cluster.id;
export const kubeconfig = cluster.kubeconfig;
export const bucketNames = mlBuckets.map(b => b.bucket.id);
```

### Go Example

```go
// main.go
package main

import (
    "fmt"

    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/ec2"
    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/eks"
    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/iam"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

func main() {
    pulumi.Run(func(ctx *pulumi.Context) error {
        // Configuration
        cfg := config.New(ctx, "")
        clusterName := cfg.Get("clusterName")
        if clusterName == "" {
            clusterName = "ml-cluster"
        }

        // Create VPC
        vpc, err := ec2.NewVpc(ctx, "ml-vpc", &ec2.VpcArgs{
            CidrBlock:          pulumi.String("10.0.0.0/16"),
            EnableDnsHostnames: pulumi.Bool(true),
            EnableDnsSupport:   pulumi.Bool(true),
            Tags: pulumi.StringMap{
                "Name": pulumi.String(fmt.Sprintf("%s-vpc", clusterName)),
            },
        })
        if err != nil {
            return err
        }

        // Create EKS cluster IAM role
        clusterRole, err := iam.NewRole(ctx, "eks-cluster-role", &iam.RoleArgs{
            AssumeRolePolicy: pulumi.String(`{
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }`),
        })
        if err != nil {
            return err
        }

        // Attach policies to cluster role
        _, err = iam.NewRolePolicyAttachment(ctx, "eks-cluster-policy", &iam.RolePolicyAttachmentArgs{
            PolicyArn: pulumi.String("arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"),
            Role:      clusterRole.Name,
        })
        if err != nil {
            return err
        }

        // Create EKS cluster
        cluster, err := eks.NewCluster(ctx, "ml-cluster", &eks.ClusterArgs{
            Name:    pulumi.String(clusterName),
            RoleArn: clusterRole.Arn,
            VpcConfig: &eks.ClusterVpcConfigArgs{
                SubnetIds: pulumi.StringArray{
                    // Add subnet IDs here
                },
            },
            EnabledClusterLogTypes: pulumi.StringArray{
                pulumi.String("api"),
                pulumi.String("audit"),
                pulumi.String("authenticator"),
            },
            Tags: pulumi.StringMap{
                "Name":        pulumi.String(clusterName),
                "Environment": pulumi.String("production"),
            },
        })
        if err != nil {
            return err
        }

        // Export outputs
        ctx.Export("vpcId", vpc.ID())
        ctx.Export("clusterName", cluster.Name)
        ctx.Export("clusterEndpoint", cluster.Endpoint)
        ctx.Export("clusterArn", cluster.Arn)

        return nil
    })
}
```

## Comparison with Terraform

### Similarities

Both Terraform and Pulumi:
- Manage infrastructure as code
- Support multiple cloud providers
- Track infrastructure state
- Provide preview before changes
- Enable team collaboration

### Key Differences

| Aspect | Terraform | Pulumi |
|--------|-----------|--------|
| **Language** | HCL (custom DSL) | Python, TypeScript, Go, C#, Java |
| **Loops** | `count`, `for_each` | Native language loops |
| **Conditionals** | Ternary operators | Native if/else |
| **Functions** | Built-in functions only | Full language ecosystem |
| **Testing** | Terratest (separate) | Native unit testing |
| **Type Safety** | Limited | Full type checking (TS, Go) |
| **IDE Support** | Basic | Full autocomplete, intellisense |
| **State** | State file | State file (compatible) |
| **Modules** | HCL modules | Language packages |
| **Community** | Larger, more mature | Growing rapidly |

### When to Choose Pulumi

**Choose Pulumi if:**
- Team prefers general-purpose languages
- Need complex logic and abstractions
- Want familiar tooling (IDEs, linters, formatters)
- Need strong type safety
- Want to share code between IaC and application
- Prefer testing with familiar frameworks

### When to Choose Terraform

**Choose Terraform if:**
- Existing Terraform codebase
- Large ecosystem of modules needed
- Declarative DSL preferred
- Wider community support important
- Sentinel policy requirements (Enterprise)

### Migration Example

**Terraform:**
```hcl
variable "environments" {
  type = map(object({
    instance_type = string
    node_count   = number
  }))
}

resource "aws_instance" "web" {
  for_each = var.environments

  instance_type = each.value.instance_type
  count         = each.value.node_count

  tags = {
    Environment = each.key
  }
}
```

**Pulumi (Python):**
```python
environments = {
    'dev': {'instance_type': 't3.small', 'node_count': 2},
    'prod': {'instance_type': 't3.large', 'node_count': 5}
}

instances = {}
for env_name, env_config in environments.items():
    instances[env_name] = []
    for i in range(env_config['node_count']):
        instance = aws.ec2.Instance(
            f'web-{env_name}-{i}',
            instance_type=env_config['instance_type'],
            tags={
                'Environment': env_name,
                'Index': str(i)
            }
        )
        instances[env_name].append(instance)
```

## Stack and Configuration Management

### Stacks

Stacks are isolated instances of your Pulumi program (dev, staging, prod).

```bash
# Create stacks
pulumi stack init dev
pulumi stack init staging
pulumi stack init prod

# List stacks
pulumi stack ls

# Switch stacks
pulumi stack select dev

# Stack-specific configuration
pulumi config set cluster_name ml-cluster-dev
pulumi config set --stack prod cluster_name ml-cluster-prod

# Secrets (encrypted)
pulumi config set --secret dbPassword mySecretPassword
```

### Configuration Management

```python
# __main__.py
import pulumi

# Get configuration
config = pulumi.Config()

# Required config (fails if not set)
cluster_name = config.require('cluster_name')

# Optional config with default
node_count = config.get_int('node_count') or 3

# Secret config (automatically encrypted)
db_password = config.require_secret('db_password')

# Environment-specific config
environment = pulumi.get_stack()

# Configuration file: Pulumi.dev.yaml
# config:
#   ml-infrastructure:cluster_name: ml-cluster-dev
#   ml-infrastructure:node_count: "3"
#   ml-infrastructure:db_password:
#     secure: AAABAEhYk8...  # encrypted

# Use configuration
cluster = create_eks_cluster(
    name=cluster_name,
    node_count=node_count,
    environment=environment
)
```

### Stack References

Share outputs between stacks:

```python
# infrastructure/__main__.py
import pulumi

vpc = create_vpc()
cluster = create_eks_cluster(vpc_id=vpc.id)

# Export for other stacks
pulumi.export('vpc_id', vpc.id)
pulumi.export('cluster_name', cluster.name)
pulumi.export('cluster_endpoint', cluster.endpoint)
```

```python
# application/__main__.py
import pulumi

# Reference infrastructure stack
infra = pulumi.StackReference(f"organization/infrastructure/{pulumi.get_stack()}")

vpc_id = infra.get_output('vpc_id')
cluster_name = infra.get_output('cluster_name')

# Use infrastructure outputs
app = deploy_application(
    cluster_name=cluster_name,
    vpc_id=vpc_id
)
```

## ML Infrastructure with Pulumi

### Complete ML Platform

```python
# ml_platform.py
import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s
from typing import Dict, List

class MLPlatform:
    """Complete ML infrastructure platform"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config

        # Create components
        self.vpc = self._create_vpc()
        self.storage = self._create_storage()
        self.cluster = self._create_eks_cluster()
        self.ml_services = self._deploy_ml_services()

    def _create_vpc(self):
        """Create VPC with public and private subnets"""
        vpc = aws.ec2.Vpc(f'{self.name}-vpc',
            cidr_block='10.0.0.0/16',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={'Name': f'{self.name}-vpc'}
        )

        # Create subnets (abbreviated)
        return {
            'vpc': vpc,
            'public_subnets': self._create_public_subnets(vpc),
            'private_subnets': self._create_private_subnets(vpc),
        }

    def _create_storage(self):
        """Create S3 buckets and EFS"""
        buckets = {}

        # Data buckets
        for bucket_type in ['raw-data', 'processed-data', 'models', 'experiments']:
            bucket = aws.s3.Bucket(f'{self.name}-{bucket_type}',
                bucket=f'{self.name}-{bucket_type}',
                acl='private',
                versioning=aws.s3.BucketVersioningArgs(enabled=True),
                lifecycle_rules=[
                    aws.s3.BucketLifecycleRuleArgs(
                        enabled=True,
                        transitions=[aws.s3.BucketLifecycleRuleTransitionArgs(
                            days=30 if bucket_type == 'experiments' else 90,
                            storage_class='INTELLIGENT_TIERING',
                        )],
                    )
                ],
                server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
                    rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                        apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                            sse_algorithm='AES256',
                        ),
                    ),
                ),
            )
            buckets[bucket_type] = bucket

        # EFS for shared storage
        efs = aws.efs.FileSystem(f'{self.name}-efs',
            encrypted=True,
            performance_mode='generalPurpose',
            throughput_mode='bursting',
            tags={'Name': f'{self.name}-efs'}
        )

        return {'buckets': buckets, 'efs': efs}

    def _create_eks_cluster(self):
        """Create EKS cluster with GPU and CPU node groups"""
        # Cluster creation (abbreviated)
        cluster = create_eks_cluster(
            name=self.name,
            vpc_id=self.vpc['vpc'].id,
            subnet_ids=[s.id for s in self.vpc['private_subnets']]
        )

        return cluster

    def _deploy_ml_services(self):
        """Deploy ML services to Kubernetes"""
        # Kubernetes provider
        k8s_provider = k8s.Provider(f'{self.name}-k8s',
            kubeconfig=self.cluster['kubeconfig']
        )

        services = {}

        # MLflow
        services['mlflow'] = self._deploy_mlflow(k8s_provider)

        # Model serving (Seldon Core)
        services['seldon'] = self._deploy_seldon(k8s_provider)

        # Monitoring (Prometheus/Grafana)
        services['monitoring'] = self._deploy_monitoring(k8s_provider)

        return services

    def _deploy_mlflow(self, provider):
        """Deploy MLflow tracking server"""
        namespace = k8s.core.v1.Namespace('mlflow',
            metadata={'name': 'mlflow'},
            opts=pulumi.ResourceOptions(provider=provider)
        )

        # PostgreSQL for MLflow backend
        db = aws.rds.Instance('mlflow-db',
            allocated_storage=20,
            engine='postgres',
            engine_version='13.7',
            instance_class='db.t3.micro',
            db_name='mlflow',
            username='mlflow',
            password=self.config['db_password'],
            skip_final_snapshot=True,
        )

        # MLflow deployment
        mlflow_deployment = k8s.apps.v1.Deployment('mlflow',
            metadata={
                'name': 'mlflow',
                'namespace': namespace.metadata['name']
            },
            spec={
                'replicas': 2,
                'selector': {'matchLabels': {'app': 'mlflow'}},
                'template': {
                    'metadata': {'labels': {'app': 'mlflow'}},
                    'spec': {
                        'containers': [{
                            'name': 'mlflow',
                            'image': 'ghcr.io/mlflow/mlflow:latest',
                            'ports': [{'containerPort': 5000}],
                            'env': [
                                {'name': 'MLFLOW_BACKEND_STORE_URI',
                                 'value': pulumi.Output.all(db.endpoint, db.db_name).apply(
                                     lambda args: f'postgresql://mlflow:{self.config["db_password"]}@{args[0]}/{args[1]}'
                                 )},
                                {'name': 'MLFLOW_DEFAULT_ARTIFACT_ROOT',
                                 'value': pulumi.Output.concat('s3://', self.storage['buckets']['experiments'].id, '/mlflow')},
                            ],
                        }],
                    },
                },
            },
            opts=pulumi.ResourceOptions(provider=provider)
        )

        # Service
        mlflow_service = k8s.core.v1.Service('mlflow',
            metadata={
                'name': 'mlflow',
                'namespace': namespace.metadata['name']
            },
            spec={
                'selector': {'app': 'mlflow'},
                'ports': [{'port': 80, 'targetPort': 5000}],
                'type': 'LoadBalancer',
            },
            opts=pulumi.ResourceOptions(provider=provider)
        )

        return {
            'namespace': namespace,
            'db': db,
            'deployment': mlflow_deployment,
            'service': mlflow_service,
        }

# Usage
config = pulumi.Config()
platform = MLPlatform('ml-platform', {
    'db_password': config.require_secret('db_password'),
    'node_count': config.get_int('node_count') or 3,
})

# Exports
pulumi.export('cluster_endpoint', platform.cluster['endpoint'])
pulumi.export('mlflow_endpoint', platform.ml_services['mlflow']['service'].status.apply(
    lambda status: status.load_balancer.ingress[0].hostname if status else None
))
```

## Advanced Patterns

### Component Resources

```python
from pulumi import ComponentResource, ResourceOptions, Output
import pulumi_aws as aws

class MLDataLake(ComponentResource):
    """Reusable ML data lake component"""

    def __init__(self, name: str, args: dict, opts: ResourceOptions = None):
        super().__init__('custom:ml:DataLake', name, {}, opts)

        child_opts = ResourceOptions(parent=self)

        # Raw data bucket
        self.raw_bucket = aws.s3.Bucket(f'{name}-raw',
            bucket=f'{args["project"]}-raw-data',
            versioning=aws.s3.BucketVersioningArgs(enabled=True),
            opts=child_opts
        )

        # Processed data bucket
        self.processed_bucket = aws.s3.Bucket(f'{name}-processed',
            bucket=f'{args["project"]}-processed-data',
            versioning=aws.s3.BucketVersioningArgs(enabled=True),
            opts=child_opts
        )

        # Glue catalog database
        self.catalog_db = aws.glue.CatalogDatabase(f'{name}-catalog',
            name=f'{args["project"]}_data_lake',
            opts=child_opts
        )

        self.register_outputs({
            'raw_bucket': self.raw_bucket.id,
            'processed_bucket': self.processed_bucket.id,
            'catalog_db': self.catalog_db.name,
        })

# Usage
data_lake = MLDataLake('data-lake', {
    'project': 'ml-platform',
})

pulumi.export('raw_bucket', data_lake.raw_bucket.id)
```

### Dynamic Providers

```python
from pulumi import dynamic, Output
import requests

class MLModelRegistration(dynamic.Resource):
    """Custom resource for ML model registration"""

    def __init__(self, name: str, model_info: dict, opts=None):
        super().__init__(MLModelProvider(), name, {
            'model_name': model_info['name'],
            'model_version': model_info['version'],
            'model_uri': model_info['uri'],
        }, opts)

class MLModelProvider(dynamic.ResourceProvider):
    """Provider for ML model registration"""

    def create(self, props):
        # Register model with MLflow
        response = requests.post(
            f"{props['mlflow_uri']}/api/2.0/mlflow/registered-models/create",
            json={'name': props['model_name']}
        )

        # Create model version
        version_response = requests.post(
            f"{props['mlflow_uri']}/api/2.0/mlflow/model-versions/create",
            json={
                'name': props['model_name'],
                'source': props['model_uri'],
            }
        )

        return dynamic.CreateResult(
            id_=f"{props['model_name']}-{props['model_version']}",
            outs={
                'model_name': props['model_name'],
                'version': version_response.json()['model_version']['version'],
            }
        )

    def delete(self, id, props):
        # Cleanup logic
        pass

# Usage
model = MLModelRegistration('my-model', {
    'name': 'sentiment-classifier',
    'version': '1.0.0',
    'uri': 's3://models/sentiment-classifier/1.0.0',
})
```

## Best Practices

### 1. Project Organization

```
ml-infrastructure/
├── __main__.py           # Entry point
├── network.py            # VPC, subnets
├── compute.py            # EKS, node groups
├── storage.py            # S3, EFS, RDS
├── ml_services.py        # MLflow, model serving
├── monitoring.py         # Prometheus, Grafana
├── components/           # Reusable components
│   ├── data_lake.py
│   └── ml_cluster.py
├── Pulumi.yaml          # Project config
├── Pulumi.dev.yaml      # Dev stack config
├── Pulumi.prod.yaml     # Prod stack config
└── requirements.txt     # Python deps
```

### 2. Use Type Hints (Python)

```python
from typing import Dict, List, Optional
import pulumi
import pulumi_aws as aws

def create_ml_buckets(
    project_name: str,
    bucket_configs: Dict[str, Dict[str, any]],
    tags: Optional[Dict[str, str]] = None
) -> Dict[str, aws.s3.Bucket]:
    """Create ML data buckets with type safety"""

    buckets: Dict[str, aws.s3.Bucket] = {}

    for bucket_name, config in bucket_configs.items():
        bucket = aws.s3.Bucket(
            f'{project_name}-{bucket_name}',
            bucket=f'{project_name}-{bucket_name}',
            versioning=aws.s3.BucketVersioningArgs(
                enabled=config.get('versioning', True)
            ),
            tags=tags or {}
        )
        buckets[bucket_name] = bucket

    return buckets
```

### 3. Testing

```python
# tests/test_infrastructure.py
import unittest
import pulumi

class TestInfrastructure(unittest.TestCase):

    @pulumi.runtime.test
    def test_bucket_encryption(self):
        def check_encryption(args):
            bucket, encryption = args
            self.assertEqual(encryption['rule']['apply_server_side_encryption_by_default']['sse_algorithm'], 'AES256')

        bucket = aws.s3.Bucket('test-bucket',
            server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
                rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                    apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                        sse_algorithm='AES256'
                    )
                )
            )
        )

        return pulumi.Output.all(bucket, bucket.server_side_encryption_configuration).apply(check_encryption)
```

## Summary

Pulumi enables:
- Infrastructure as code using familiar programming languages
- Strong type safety and IDE support
- Reusable components and abstractions
- Native testing capabilities
- Seamless integration with application code

**Key Takeaways:**
1. Choose the language that fits your team's expertise
2. Leverage programming language features for complex logic
3. Use component resources for reusability
4. Implement proper stack and configuration management
5. Write tests for infrastructure code
6. Follow consistent project organization

## Next Steps

- Continue to [Lecture 3: GitOps Principles](03-gitops-principles.md)
- Build a sample ML infrastructure with Pulumi
- Compare Pulumi and Terraform implementations
- Explore component resources

## Additional Resources

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi Examples](https://github.com/pulumi/examples)
- [Pulumi AWS Provider](https://www.pulumi.com/registry/packages/aws/)
- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
