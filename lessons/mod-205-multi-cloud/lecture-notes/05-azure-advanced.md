# Advanced Azure for AI Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:

- Design production ML systems on Azure leveraging Azure Machine Learning for managed training/inference, AKS for Kubernetes workloads, and Azure OpenAI Service for LLM applications
- Architect Azure ML pipelines integrating data processing with Azure Data Factory, distributed training with custom compute clusters, AutoML capabilities, and managed online endpoints
- Configure Azure Kubernetes Service (AKS) for ML workloads with GPU node pools, virtual kubelet for burst capacity, Azure Files/NetApp for storage, and Azure CNI networking
- Implement Azure OpenAI Service architectures for enterprise LLM applications using GPT-4, embeddings, content filtering, and private endpoint connectivity
- Design cost-optimized Azure ML infrastructure using Spot VMs for training, reserved capacity for inference, cool/archive storage tiers, and Azure Hybrid Benefit licensing
- Configure Azure networking for ML including VNet design, Private Link for secure service access, ExpressRoute for hybrid connectivity, and availability zones for HA
- Implement Azure-specific optimizations leveraging NDv4/NCads A100 v4 series VMs, Ultra Disk storage, and Azure ML managed compute for automatic scaling
- Build production-grade ML systems on Azure integrating Azure AD authentication, Azure Monitor, Logic Apps for automation, and compliance frameworks (Azure Policy, Blueprints)

## Overview

Microsoft Azure provides powerful services for AI infrastructure, including Azure Machine Learning, GPU-enabled VMs, and strong enterprise integration capabilities. This lesson covers advanced Azure services and patterns for AI workloads.

---

## 1. Azure Machine Learning Service

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Azure ML Workspace                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Compute    │  │  Datastores  │  │  Experiments │  │
│  │  Resources   │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Pipelines  │  │    Models    │  │  Endpoints   │  │
│  │              │  │   Registry   │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Key Components

**1. Compute Resources**

```python
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute, ComputeInstance
from azure.identity import DefaultAzureCredential

# Initialize ML Client
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="<subscription-id>",
    resource_group_name="<rg-name>",
    workspace_name="<workspace-name>"
)

# Create GPU Compute Cluster
gpu_cluster = AmlCompute(
    name="gpu-cluster",
    type="amlcompute",
    size="Standard_NC24ads_A100_v4",  # A100 GPUs
    min_instances=0,
    max_instances=4,
    idle_time_before_scale_down=120,
    tier="dedicated"
)

ml_client.compute.begin_create_or_update(gpu_cluster)
```

**2. Azure ML Pipelines**

```python
from azure.ai.ml import dsl, Input, Output
from azure.ai.ml.constants import AssetTypes

@dsl.pipeline(
    name="distributed_training_pipeline",
    description="Multi-node GPU training pipeline"
)
def training_pipeline(
    training_data: Input(type=AssetTypes.URI_FOLDER),
    epochs: int = 100
):
    # Data preparation step
    prep_job = data_prep_component(
        input_data=training_data,
        train_test_split=0.8
    )

    # Distributed training step
    train_job = distributed_training_component(
        training_data=prep_job.outputs.training_data,
        validation_data=prep_job.outputs.validation_data,
        epochs=epochs,
        nodes=4,
        gpus_per_node=4
    )
    train_job.compute = "gpu-cluster"
    train_job.distribution = {
        "type": "PyTorch",
        "process_count_per_instance": 4
    }

    # Model registration step
    register_job = model_registration_component(
        model_path=train_job.outputs.model_output
    )

    return {
        "model_id": register_job.outputs.model_id,
        "metrics": train_job.outputs.metrics
    }
```

---

## 2. Azure GPU Computing

### VM Series for AI Workloads

| Series | GPU | vCPUs | Memory | Use Case |
|--------|-----|-------|--------|----------|
| NC A100 v4 | NVIDIA A100 | 24-96 | 220-880 GB | Large-scale training |
| ND A100 v4 | NVIDIA A100 | 96 | 900 GB | HPC, distributed training |
| NC T4 v3 | NVIDIA T4 | 4-64 | 28-440 GB | Inference, small training |
| NV v4 | AMD Radeon | 4-32 | 14-112 GB | Visualization, VDI |

### GPU Optimization Strategies

**1. Azure Batch for Parallel Training**

```python
import azure.batch.batch_service_client as batch
from azure.batch import BatchServiceClient
from azure.common.credentials import ServicePrincipalCredentials

# Configure batch client
credentials = ServicePrincipalCredentials(
    client_id='<client-id>',
    secret='<secret>',
    tenant='<tenant-id>',
    resource='https://batch.core.windows.net/'
)

batch_client = BatchServiceClient(
    credentials,
    batch_url='https://<account>.westus2.batch.azure.com'
)

# Create GPU pool
pool_config = {
    'id': 'gpu-training-pool',
    'vm_size': 'Standard_NC24ads_A100_v4',
    'target_dedicated_nodes': 4,
    'start_task': {
        'command_line': '/bin/bash -c "nvidia-smi && pip install torch torchvision"',
        'user_identity': {
            'auto_user': {
                'elevation_level': 'admin'
            }
        }
    },
    'virtual_machine_configuration': {
        'image_reference': {
            'publisher': 'microsoft-azure-batch',
            'offer': 'ubuntu-server-container',
            'sku': '20-04-lts',
            'version': 'latest'
        },
        'node_agent_sku_id': 'batch.node.ubuntu 20.04'
    }
}

batch_client.pool.add(pool_config)
```

**2. Low-Priority VMs for Cost Savings**

```python
# Configure low-priority GPU instances (up to 80% cost savings)
low_priority_config = AmlCompute(
    name="low-priority-cluster",
    size="Standard_NC24ads_A100_v4",
    min_instances=0,
    max_instances=10,
    tier="low_priority",  # Low-priority VMs
    idle_time_before_scale_down=300
)

# Implement checkpoint recovery for preemption
checkpoint_config = {
    'checkpoint_frequency': 1000,  # steps
    'checkpoint_location': 'azureml://datastores/checkpoints',
    'resume_from_checkpoint': True
}
```

---

## 3. Azure Storage for AI Workloads

### Storage Options Comparison

**Azure Blob Storage**
```python
from azure.storage.blob import BlobServiceClient, ContainerClient

# High-performance blob storage for datasets
blob_client = BlobServiceClient.from_connection_string(
    "<connection-string>"
)

# Use premium block blobs for training data
container_client = blob_client.get_container_client("training-data")

# Enable hierarchical namespace for Data Lake Gen2
# Provides file system semantics with blob scalability
```

**Azure Files**
```python
from azure.storage.fileshare import ShareServiceClient

# NFSv4.1 support for parallel access
share_client = ShareServiceClient.from_connection_string(
    "<connection-string>"
)

# Premium file shares for low-latency workloads
# Up to 100,000 IOPS per share
```

**Performance Tiers**

| Storage Type | IOPS | Throughput | Latency | Cost/GB |
|--------------|------|------------|---------|---------|
| Premium Block Blob | 100K+ | 10+ GB/s | <10ms | $$$ |
| Premium Files | 100K | 10 GB/s | <10ms | $$$ |
| Hot Blob | 20K | 2 GB/s | <50ms | $ |
| Cool Blob | 500 | 250 MB/s | Variable | $ |

---

## 4. Azure Networking for AI

### Private Endpoints and VNet Integration

```python
from azure.ai.ml.entities import Workspace

# Create workspace with private link
workspace = Workspace(
    name="secure-ml-workspace",
    location="eastus",
    public_network_access="Disabled",  # No public access
    managed_network={
        "isolation_mode": "allow_only_approved_outbound"
    }
)

# Configure private endpoint
private_endpoint_config = {
    'name': 'ml-workspace-pe',
    'subnet_id': '/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/<vnet>/subnets/<subnet>',
    'private_dns_zone_configs': [
        {
            'name': 'privatelink.api.azureml.ms',
            'private_dns_zone_id': '<zone-id>'
        }
    ]
}
```

### ExpressRoute for Hybrid Connectivity

```
┌──────────────────┐
│   On-Premises    │
│   Data Center    │
└────────┬─────────┘
         │
    ExpressRoute
    (10 Gbps)
         │
┌────────▼─────────┐
│  Azure VNet      │
├──────────────────┤
│  ┌────────────┐  │
│  │ Azure ML   │  │
│  │ Workspace  │  │
│  └────────────┘  │
│  ┌────────────┐  │
│  │ GPU VMs    │  │
│  └────────────┘  │
└──────────────────┘
```

---

## 5. Azure Container Services

### Azure Kubernetes Service (AKS) for ML

**GPU Node Pools**

```bash
# Create AKS cluster with GPU node pool
az aks create \
    --resource-group ml-infrastructure \
    --name ml-aks-cluster \
    --node-count 1 \
    --generate-ssh-keys \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5

# Add GPU node pool
az aks nodepool add \
    --resource-group ml-infrastructure \
    --cluster-name ml-aks-cluster \
    --name gpunodepool \
    --node-count 2 \
    --node-vm-size Standard_NC24ads_A100_v4 \
    --enable-cluster-autoscaler \
    --min-count 0 \
    --max-count 4 \
    --labels workload=gpu-training \
    --node-taints sku=gpu:NoSchedule
```

**Azure ML Extension for AKS**

```bash
# Install Azure ML extension on AKS
az k8s-extension create \
    --name ml-extension \
    --extension-type Microsoft.AzureML.Kubernetes \
    --cluster-type managedClusters \
    --cluster-name ml-aks-cluster \
    --resource-group ml-infrastructure \
    --scope cluster \
    --configuration-settings \
        enableInference=True \
        enableTraining=True \
        inferenceRouterServiceType=LoadBalancer
```

### Azure Container Instances (ACI)

```python
from azure.ai.ml.entities import OnlineDeployment, ManagedOnlineEndpoint

# Deploy to ACI for lightweight inference
endpoint = ManagedOnlineEndpoint(
    name="lightweight-endpoint",
    description="CPU-based inference endpoint",
    auth_mode="key"
)

deployment = OnlineDeployment(
    name="blue",
    endpoint_name="lightweight-endpoint",
    model=model,
    instance_type="Standard_DS3_v2",  # CPU instance
    instance_count=1,
    environment=env,
    code_configuration=CodeConfiguration(
        code="./src",
        scoring_script="score.py"
    )
)
```

---

## 6. Azure Cost Optimization

### Reserved Instances and Savings Plans

```python
# Estimate savings with reserved instances
reserved_instance_savings = {
    'Standard_NC24ads_A100_v4': {
        'pay_as_you_go': 3.673,  # $/hour
        '1_year_reserved': 2.567,  # 30% savings
        '3_year_reserved': 1.836,  # 50% savings
    }
}

# Azure Savings Plan (flexible alternative)
# - Apply to any compute across subscriptions
# - 1-year or 3-year commitment
# - Up to 65% savings on compute
```

### Cost Management Best Practices

**1. Auto-shutdown Policies**

```python
from azure.ai.ml.entities import ComputeInstance

# Configure auto-shutdown
compute_instance = ComputeInstance(
    name="dev-instance",
    size="Standard_NC24ads_A100_v4",
    idle_time_before_shutdown=15,  # minutes
    schedules={
        'compute_start_stop': [
            {
                'action': 'stop',
                'trigger': {'type': 'cron', 'expression': '0 18 * * *'},
                'time_zone': 'Pacific Standard Time'
            },
            {
                'action': 'start',
                'trigger': {'type': 'cron', 'expression': '0 8 * * 1-5'},
                'time_zone': 'Pacific Standard Time'
            }
        ]
    }
)
```

**2. Cost Anomaly Detection**

```python
from azure.mgmt.costmanagement import CostManagementClient
from azure.identity import DefaultAzureCredential

cost_client = CostManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="<subscription-id>"
)

# Create budget alert
budget_config = {
    'name': 'ml-monthly-budget',
    'amount': 10000,
    'time_grain': 'Monthly',
    'notifications': {
        'actual_greater_than_80_percent': {
            'enabled': True,
            'operator': 'GreaterThan',
            'threshold': 80,
            'contact_emails': ['ml-team@company.com']
        }
    }
}
```

---

## 7. Azure Monitor and Application Insights

### ML Model Monitoring

```python
from azure.ai.ml.entities import ModelMonitoring, AlertNotification

# Configure model monitoring
monitoring = ModelMonitoring(
    name="model-performance-monitor",
    endpoint_name="production-endpoint",
    deployment_name="blue",
    monitoring_signals={
        'data_drift': {
            'enabled': True,
            'baseline_dataset': 'training_data',
            'target_dataset': 'inference_data',
            'features': ['feature1', 'feature2', 'feature3'],
            'threshold': 0.3
        },
        'prediction_drift': {
            'enabled': True,
            'threshold': 0.2
        },
        'data_quality': {
            'enabled': True,
            'null_value_threshold': 0.05,
            'out_of_range_threshold': 0.1
        }
    },
    alert_notification=AlertNotification(
        emails=['ml-ops@company.com']
    )
)
```

### Application Insights Integration

```python
from applicationinsights import TelemetryClient
from applicationinsights.requests import WSGIApplication

# Track custom ML metrics
tc = TelemetryClient('<instrumentation-key>')

def log_inference_metrics(prediction, latency, input_size):
    tc.track_event(
        'model_inference',
        {
            'prediction': prediction,
            'latency_ms': latency,
            'input_size': input_size
        },
        {
            'latency': latency,
            'size': input_size
        }
    )
    tc.flush()
```

---

## 8. Azure Integration Patterns

### Multi-Cloud Data Pipeline

```python
# Azure Function triggered by AWS S3 via EventGrid
import azure.functions as func
import boto3
from azure.storage.blob import BlobServiceClient

def main(event: func.EventGridEvent):
    # Process S3 event
    s3_client = boto3.client('s3')

    # Download from S3
    s3_object = s3_client.get_object(
        Bucket=event.data['bucket'],
        Key=event.data['key']
    )

    # Upload to Azure Blob
    blob_client = BlobServiceClient.from_connection_string(
        os.environ['AZURE_STORAGE_CONNECTION_STRING']
    )

    blob_client.get_blob_client(
        container='ml-data',
        blob=event.data['key']
    ).upload_blob(s3_object['Body'].read())
```

### Azure Arc for Hybrid/Multi-Cloud

```bash
# Connect on-premises Kubernetes to Azure Arc
az connectedk8s connect \
    --name hybrid-k8s-cluster \
    --resource-group ml-infrastructure

# Deploy Azure ML extension to Arc-enabled cluster
az k8s-extension create \
    --name azureml \
    --extension-type Microsoft.AzureML.Kubernetes \
    --cluster-type connectedClusters \
    --cluster-name hybrid-k8s-cluster \
    --resource-group ml-infrastructure
```

---

## 9. Security and Compliance

### Azure AD Integration

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

# Use managed identity for authentication
credential = ManagedIdentityCredential()

# Access Key Vault secrets
vault_url = "https://<vault-name>.vault.azure.net"
secret_client = SecretClient(vault_url=vault_url, credential=credential)

api_key = secret_client.get_secret("openai-api-key").value
```

### Customer-Managed Keys (CMK)

```python
from azure.ai.ml.entities import Workspace

# Configure workspace with CMK
workspace = Workspace(
    name="secure-workspace",
    location="eastus",
    customer_managed_key={
        'key_vault_id': '/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<vault>',
        'key_identifier': 'https://<vault>.vault.azure.net/keys/<key>/<version>'
    },
    encryption_status='Enabled',
    encryption_key_version='<version>'
)
```

---

## 10. Best Practices

### DO ✅

- Use managed identities for authentication
- Implement private endpoints for production workloads
- Enable diagnostic logging for all resources
- Use Azure Policy for governance
- Implement cost budgets and alerts
- Use low-priority VMs for non-critical training
- Enable soft delete on storage accounts
- Use Azure ML pipelines for reproducibility

### DON'T ❌

- Hardcode credentials in code or notebooks
- Use public endpoints in production
- Run GPU instances 24/7 without monitoring
- Store sensitive data without encryption
- Ignore cost anomalies
- Deploy without RBAC configured
- Skip backup and disaster recovery planning
- Use production resources for experimentation

---

## Hands-On Exercise

Build an Azure ML pipeline that:
1. Ingests data from Azure Blob Storage
2. Trains a model on GPU compute cluster
3. Deploys model to AKS with autoscaling
4. Monitors performance with Application Insights
5. Implements cost controls and budgets

---

## Key Takeaways

1. **Azure ML Service** provides end-to-end MLOps capabilities
2. **GPU computing** on Azure offers flexible scaling with cost optimization options
3. **Storage tiers** should match workload performance requirements
4. **Private networking** is essential for production AI workloads
5. **Cost management** requires proactive monitoring and policies
6. **Integration patterns** enable hybrid and multi-cloud architectures
7. **Security** should be built-in from the start, not bolted on

---

## Additional Resources

- [Azure ML Documentation](https://docs.microsoft.com/azure/machine-learning/)
- [Azure GPU VM Sizes](https://docs.microsoft.com/azure/virtual-machines/sizes-gpu)
- [Azure Architecture Center - AI](https://docs.microsoft.com/azure/architecture/browse/?products=ai-machine-learning)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
