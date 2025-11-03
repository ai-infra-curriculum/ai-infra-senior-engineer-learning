# Lecture 03: AWS Advanced Services for ML Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:

- Design production ML systems on AWS leveraging SageMaker for managed training/inference, EKS for containerized workloads, and Bedrock for generative AI applications
- Architect SageMaker pipelines integrating data processing, model training with distributed strategies, hyperparameter optimization, and multi-model endpoints for production serving
- Configure Amazon EKS clusters for ML workloads with GPU node groups, Karpenter autoscaling, EFA networking, and FSx for Lustre storage for high-performance training
- Implement AWS Bedrock architectures for LLM applications using foundation models, RAG patterns with vector databases, and fine-tuning with custom datasets
- Design cost-optimized AWS ML infrastructure using Spot instances for training, Savings Plans for inference, S3 Intelligent-Tiering for data, and rightsizing recommendations
- Configure AWS networking for ML including VPC design, PrivateLink for secure SageMaker access, Direct Connect for hybrid workloads, and multi-region architectures
- Implement AWS-specific optimizations leveraging Trainium/Inferentia accelerators, EBS io2 Block Express volumes, and AWS-optimized ML AMIs for maximum performance
- Build production-grade ML systems on AWS integrating IAM policies, CloudWatch monitoring, EventBridge automation, and compliance (HIPAA, PCI-DSS) requirements

## Table of Contents
1. [Introduction](#introduction)
2. [Amazon SageMaker Deep Dive](#sagemaker)
3. [Amazon EKS for ML Workloads](#eks)
4. [Amazon Bedrock for Generative AI](#bedrock)
5. [AWS Infrastructure for ML at Scale](#infrastructure)
6. [Cost Optimization on AWS](#cost-optimization)
7. [Real-World Architectures](#real-world)
8. [Best Practices](#best-practices)
9. [Summary](#summary)

## Introduction {#introduction}

Amazon Web Services (AWS) offers the most comprehensive suite of ML and AI services among cloud providers. As a Senior AI Infrastructure Engineer, understanding how to architect, deploy, and optimize ML workloads on AWS is crucial for building production-grade systems at scale.

### AWS ML Service Landscape

AWS provides ML services across three layers:

1. **AI Services (Highest Level)**: Pre-trained APIs (Rekognition, Comprehend, Translate)
2. **ML Services (Mid Level)**: SageMaker, Bedrock, personalized recommendation engines
3. **ML Infrastructure (Lowest Level)**: EC2 with GPUs, EKS, specialized instances

This lecture focuses on Layer 2 and 3—services that Senior Engineers use to build custom ML platforms.

### AWS Regions for ML Workloads

Not all AWS regions are equal for ML:

**Best Regions for ML (as of 2025)**:
- **us-east-1 (N. Virginia)**: Largest selection of instance types, lowest latency to services
- **us-west-2 (Oregon)**: Good GPU availability, cost-effective
- **eu-west-1 (Ireland)**: Best for GDPR compliance, good GPU selection
- **ap-southeast-1 (Singapore)**: Best for Asia-Pacific deployments

**Instance Availability by Region**:
```python
# AWS instance availability check
aws_ml_instances = {
    'us-east-1': {
        'p4d.24xlarge': True,    # 8x A100 (40GB)
        'p4de.24xlarge': True,   # 8x A100 (80GB)
        'p5.48xlarge': True,     # 8x H100
        'trn1.32xlarge': True,   # AWS Trainium
        'inf2.48xlarge': True,   # AWS Inferentia2
    },
    'us-west-2': {
        'p4d.24xlarge': True,
        'p4de.24xlarge': False,  # Limited availability
        'p5.48xlarge': False,    # Not yet available
        'trn1.32xlarge': True,
        'inf2.48xlarge': True,
    },
    'eu-west-1': {
        'p4d.24xlarge': True,
        'p4de.24xlarge': False,
        'p5.48xlarge': False,
        'trn1.32xlarge': True,
        'inf2.48xlarge': True,
    }
}
```

## Amazon SageMaker Deep Dive {#sagemaker}

Amazon SageMaker is AWS's fully managed ML platform. It provides end-to-end ML lifecycle management from data preparation to production deployment.

### SageMaker Architecture Components

1. **SageMaker Studio**: Integrated development environment for ML
2. **SageMaker Processing**: Data preprocessing and feature engineering at scale
3. **SageMaker Training**: Distributed training with automatic model tuning
4. **SageMaker Inference**: Model hosting for real-time and batch predictions
5. **SageMaker Pipelines**: ML workflow orchestration
6. **SageMaker Feature Store**: Centralized feature repository
7. **SageMaker Model Registry**: Version control for models
8. **SageMaker Clarify**: Bias detection and explainability
9. **SageMaker Model Monitor**: Production model monitoring

### SageMaker Training Deep Dive

**Training Job Anatomy**:

```python
# SageMaker training job configuration
import sagemaker
from sagemaker.pytorch import PyTorch
from sagemaker.inputs import TrainingInput
from sagemaker.debugger import Rule, rule_configs
from sagemaker.model_monitor import DataCaptureConfig

# TODO: Complete training job setup
session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()

# Define training estimator
estimator = PyTorch(
    entry_point='train.py',
    source_dir='./training_code',
    role=role,
    instance_count=4,  # Distributed training across 4 nodes
    instance_type='ml.p4d.24xlarge',  # 8x A100 GPUs per instance
    framework_version='2.1.0',
    py_version='py310',

    # Distributed training configuration
    distribution={
        'pytorchddp': {
            'enabled': True,
            'custom_mpi_options': '-verbose -x NCCL_DEBUG=INFO'
        }
    },

    # Hyperparameters
    hyperparameters={
        'epochs': 100,
        'batch-size': 64,
        'learning-rate': 0.001,
        'model-type': 'bert-large',
        'gradient-accumulation-steps': 4
    },

    # Spot training for cost savings (up to 90% off)
    use_spot_instances=True,
    max_wait=72000,  # Wait up to 20 hours
    max_run=64800,   # Max 18 hours of training

    # Checkpointing for spot instance resilience
    checkpoint_s3_uri=f's3://{bucket}/checkpoints',
    checkpoint_local_path='/opt/ml/checkpoints',

    # Debugger rules for automated issue detection
    rules=[
        Rule.sagemaker(rule_configs.vanishing_gradient()),
        Rule.sagemaker(rule_configs.overfit()),
        Rule.sagemaker(rule_configs.loss_not_decreasing()),
        Rule.sagemaker(rule_configs.stalled_training_rule())
    ],

    # Profiler for performance optimization
    profiler_config={
        'S3OutputPath': f's3://{bucket}/profiler',
        'ProfilingIntervalInMilliseconds': 500,
        'ProfilingParameters': {
            'DataloaderProfilingConfig': '{"StartStep": 5, "NumSteps": 10}',
            'DetailedProfilingConfig': '{"StartStep": 5, "NumSteps": 10}',
            'PythonProfilingConfig': '{"StartStep": 5, "NumSteps": 10}'
        }
    },

    # Output configuration
    output_path=f's3://{bucket}/models',

    # Enable warm pool for faster iteration
    keep_alive_period_in_seconds=3600,  # Keep instances for 1 hour

    # Network isolation for security
    enable_network_isolation=False,  # Set True for production

    # Encryption
    encrypt_inter_container_traffic=True,

    # Tags for cost allocation
    tags=[
        {'Key': 'Project', 'Value': 'MLPlatform'},
        {'Key': 'Team', 'Value': 'MLEngineering'},
        {'Key': 'Environment', 'Value': 'Production'}
    ]
)

# Define input data channels
train_input = TrainingInput(
    s3_data=f's3://{bucket}/training-data',
    content_type='application/x-parquet',
    s3_data_type='S3Prefix',
    distribution='ShardedByS3Key',  # Distribute data across instances
    compression='None'
)

validation_input = TrainingInput(
    s3_data=f's3://{bucket}/validation-data',
    content_type='application/x-parquet',
    s3_data_type='S3Prefix',
    distribution='FullyReplicated'  # Each instance gets full validation set
)

# Start training job
# TODO: Add error handling and job monitoring
estimator.fit({
    'train': train_input,
    'validation': validation_input
}, wait=False)  # Non-blocking

# Get training job details
training_job_name = estimator.latest_training_job.name
print(f"Training job started: {training_job_name}")

# Monitor training job
# TODO: Implement monitoring dashboard
```

**Training Script (train.py)**:

```python
# SageMaker training script with distributed training
import argparse
import os
import json
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from transformers import AutoModel, AutoTokenizer
import smdistributed.dataparallel.torch.distributed as sm_dist

def parse_args():
    """Parse training arguments"""
    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    parser.add_argument('--model-type', type=str, default='bert-base-uncased')
    parser.add_argument('--gradient-accumulation-steps', type=int, default=1)

    # SageMaker environment variables
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--validation', type=str, default=os.environ.get('SM_CHANNEL_VALIDATION'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR'))
    parser.add_argument('--num-gpus', type=int, default=os.environ.get('SM_NUM_GPUS', 1))
    parser.add_argument('--hosts', type=list, default=json.loads(os.environ.get('SM_HOSTS', '[]')))
    parser.add_argument('--current-host', type=str, default=os.environ.get('SM_CURRENT_HOST'))

    return parser.parse_args()

def setup_distributed():
    """
    Setup distributed training environment
    TODO: Add error handling for distribution setup
    """
    # Initialize distributed training
    if 'WORLD_SIZE' in os.environ:
        dist.init_process_group(backend='nccl')
        world_size = int(os.environ['WORLD_SIZE'])
        rank = int(os.environ['RANK'])
        local_rank = int(os.environ['LOCAL_RANK'])
    else:
        world_size = 1
        rank = 0
        local_rank = 0

    # Set device
    torch.cuda.set_device(local_rank)
    device = torch.device(f'cuda:{local_rank}')

    return world_size, rank, local_rank, device

def load_dataset(data_path, tokenizer, batch_size, rank, world_size):
    """
    Load and prepare dataset for distributed training
    TODO: Implement efficient data loading
    TODO: Add data augmentation
    """
    # TODO: Implement actual dataset loading
    # This is a stub - replace with actual implementation
    pass

def train_epoch(model, dataloader, optimizer, scheduler, device, epoch, args):
    """
    Train for one epoch
    TODO: Implement full training loop with logging
    """
    model.train()
    total_loss = 0.0

    for batch_idx, batch in enumerate(dataloader):
        # TODO: Move batch to device
        # TODO: Forward pass
        # TODO: Compute loss
        # TODO: Backward pass with gradient accumulation
        # TODO: Optimizer step
        # TODO: Log metrics
        pass

    return total_loss / len(dataloader)

def validate(model, dataloader, device):
    """
    Validate model performance
    TODO: Implement validation loop
    """
    model.eval()
    total_loss = 0.0

    with torch.no_grad():
        for batch in dataloader:
            # TODO: Validation logic
            pass

    return total_loss / len(dataloader)

def save_model(model, model_dir, args):
    """
    Save model artifacts
    TODO: Save in SageMaker-compatible format
    """
    # Save PyTorch model
    model_path = os.path.join(model_dir, 'model.pth')
    torch.save(model.state_dict(), model_path)

    # Save model configuration
    config_path = os.path.join(model_dir, 'config.json')
    config = {
        'model_type': args.model_type,
        'hyperparameters': {
            'learning_rate': args.learning_rate,
            'batch_size': args.batch_size,
            'epochs': args.epochs
        }
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)

    print(f"Model saved to {model_dir}")

def main():
    """Main training function"""
    args = parse_args()

    # Setup distributed training
    world_size, rank, local_rank, device = setup_distributed()

    # Load model
    # TODO: Initialize model
    # TODO: Move to device and wrap with DDP

    # Load datasets
    # TODO: Load training and validation datasets

    # Training loop
    for epoch in range(args.epochs):
        # TODO: Train epoch
        # TODO: Validate
        # TODO: Save checkpoint
        # TODO: Log metrics to SageMaker
        pass

    # Save final model (only on rank 0)
    if rank == 0:
        save_model(model, args.model_dir, args)

if __name__ == '__main__':
    main()
```

### SageMaker Inference Deep Dive

**Real-Time Inference**:

```python
# Deploy model for real-time inference
from sagemaker.pytorch import PyTorchModel
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

# Create model from training job
model = PyTorchModel(
    model_data=estimator.model_data,  # S3 URI of model artifact
    role=role,
    entry_point='inference.py',
    source_dir='./inference_code',
    framework_version='2.1.0',
    py_version='py310',

    # Environment variables for inference
    env={
        'MODEL_TYPE': 'bert-large',
        'MAX_BATCH_SIZE': '32',
        'MODEL_CACHE_DIR': '/opt/ml/model-cache'
    }
)

# Deploy with multi-model endpoint for cost efficiency
# TODO: Configure auto-scaling and monitoring
endpoint_name = 'ml-inference-production'

predictor = model.deploy(
    instance_type='ml.g5.2xlarge',  # NVIDIA A10G GPU
    initial_instance_count=2,

    # Auto-scaling configuration
    endpoint_name=endpoint_name,

    # Data capture for monitoring
    data_capture_config=DataCaptureConfig(
        enable_capture=True,
        sampling_percentage=10,  # Capture 10% of requests
        destination_s3_uri=f's3://{bucket}/data-capture',
        capture_options=['Input', 'Output']
    ),

    # Serialization
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer()
)

# Configure auto-scaling
from sagemaker import Session
import boto3

client = boto3.client('application-autoscaling')

# Register scalable target
response = client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/{endpoint_name}/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=2,
    MaxCapacity=10
)

# Define scaling policy
response = client.put_scaling_policy(
    PolicyName=f'{endpoint_name}-scaling-policy',
    ServiceNamespace='sagemaker',
    ResourceId=f'endpoint/{endpoint_name}/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% GPU utilization
        'CustomizedMetricSpecification': {
            'MetricName': 'GPUUtilization',
            'Namespace': 'AWS/SageMaker',
            'Dimensions': [
                {'Name': 'EndpointName', 'Value': endpoint_name},
                {'Name': 'VariantName', 'Value': 'AllTraffic'}
            ],
            'Statistic': 'Average'
        },
        'ScaleInCooldown': 300,  # 5 minutes
        'ScaleOutCooldown': 60   # 1 minute
    }
)

# Test inference
test_input = {
    'text': 'This is a test input for the model',
    'max_length': 512
}

response = predictor.predict(test_input)
print(f"Inference result: {response}")
```

**Inference Script (inference.py)**:

```python
# SageMaker inference script
import json
import torch
import os
from transformers import AutoModel, AutoTokenizer

def model_fn(model_dir):
    """
    Load model from directory
    Called once when endpoint starts

    TODO: Implement efficient model loading
    TODO: Add model caching
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load model
    model_path = os.path.join(model_dir, 'model.pth')
    model = AutoModel.from_pretrained(os.environ.get('MODEL_TYPE', 'bert-base-uncased'))
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(os.environ.get('MODEL_TYPE', 'bert-base-uncased'))

    return {'model': model, 'tokenizer': tokenizer, 'device': device}

def input_fn(request_body, request_content_type):
    """
    Deserialize input data

    TODO: Support multiple content types
    TODO: Add input validation
    """
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f'Unsupported content type: {request_content_type}')

def predict_fn(input_data, model_dict):
    """
    Run inference

    TODO: Implement batching for efficiency
    TODO: Add error handling
    """
    model = model_dict['model']
    tokenizer = model_dict['tokenizer']
    device = model_dict['device']

    # Tokenize input
    text = input_data.get('text', '')
    max_length = input_data.get('max_length', 512)

    inputs = tokenizer(
        text,
        max_length=max_length,
        truncation=True,
        padding='max_length',
        return_tensors='pt'
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)

    # TODO: Post-process outputs
    predictions = outputs.last_hidden_state.mean(dim=1).cpu().numpy().tolist()

    return predictions

def output_fn(prediction, content_type):
    """
    Serialize output

    TODO: Support multiple output formats
    """
    if content_type == 'application/json':
        return json.dumps({'predictions': prediction})
    else:
        raise ValueError(f'Unsupported content type: {content_type}')
```

**Batch Transform for Large-Scale Inference**:

```python
# Batch inference for processing large datasets
from sagemaker.transformer import Transformer

transformer = model.transformer(
    instance_count=5,
    instance_type='ml.g5.2xlarge',
    strategy='MultiRecord',  # Process multiple records per request
    max_payload=10,  # 10 MB max payload
    max_concurrent_transforms=50,  # Parallel requests per instance
    output_path=f's3://{bucket}/batch-inference-output',
    assemble_with='Line',  # Output format
    accept='application/json'
)

# Start batch transform job
transformer.transform(
    data=f's3://{bucket}/batch-inference-input',
    content_type='application/json',
    split_type='Line',
    wait=False
)

# Monitor job
job_name = transformer.latest_transform_job.name
print(f"Batch transform job: {job_name}")

# TODO: Implement job monitoring and result processing
```

### SageMaker Pipelines for MLOps

```python
# Define ML pipeline
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import (
    ProcessingStep,
    TrainingStep,
    CreateModelStep,
    TransformStep
)
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterFloat,
    ParameterString
)
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.properties import PropertyFile

# Define pipeline parameters
instance_count = ParameterInteger(name='InstanceCount', default_value=1)
instance_type = ParameterString(name='InstanceType', default_value='ml.m5.xlarge')
model_approval_status = ParameterString(name='ModelApprovalStatus', default_value='PendingManualApproval')

# Step 1: Data preprocessing
# TODO: Define processing step
processing_step = ProcessingStep(
    name='DataPreprocessing',
    # TODO: Add processor configuration
)

# Step 2: Model training
# TODO: Define training step
training_step = TrainingStep(
    name='ModelTraining',
    estimator=estimator,
    inputs={
        'train': TrainingInput(
            s3_data=processing_step.properties.ProcessingOutputConfig.Outputs['train'].S3Output.S3Uri
        )
    }
)

# Step 3: Model evaluation
# TODO: Define evaluation step

# Step 4: Conditional model registration
# TODO: Register model if evaluation passes threshold

# Create pipeline
pipeline = Pipeline(
    name='ml-training-pipeline',
    parameters=[instance_count, instance_type, model_approval_status],
    steps=[processing_step, training_step]  # TODO: Add remaining steps
)

# Create or update pipeline
pipeline.upsert(role_arn=role)

# Execute pipeline
execution = pipeline.start()
print(f"Pipeline execution started: {execution.arn}")

# TODO: Monitor pipeline execution
```

## Amazon EKS for ML Workloads {#eks}

Amazon Elastic Kubernetes Service (EKS) provides managed Kubernetes clusters optimized for ML workloads.

### EKS Cluster Configuration for ML

```yaml
# eksctl cluster configuration for ML workloads
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ml-platform-cluster
  region: us-east-1
  version: "1.28"
  tags:
    Environment: Production
    Project: MLPlatform
    ManagedBy: eksctl

# VPC Configuration
vpc:
  cidr: 10.0.0.0/16
  nat:
    gateway: HighlyAvailable
  clusterEndpoints:
    publicAccess: true
    privateAccess: true

# IAM Configuration
iam:
  withOIDC: true
  serviceAccounts:
  - metadata:
      name: sagemaker-sa
      namespace: ml-platform
    attachPolicyARNs:
    - arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
    - arn:aws:iam::aws:policy/AmazonS3FullAccess

  - metadata:
      name: cluster-autoscaler
      namespace: kube-system
    attachPolicy:
      Version: "2012-10-17"
      Statement:
      - Effect: Allow
        Action:
        - autoscaling:DescribeAutoScalingGroups
        - autoscaling:DescribeAutoScalingInstances
        - autoscaling:DescribeLaunchConfigurations
        - autoscaling:SetDesiredCapacity
        - autoscaling:TerminateInstanceInAutoScalingGroup
        - ec2:DescribeLaunchTemplateVersions
        Resource: '*'

# Node Groups
managedNodeGroups:
  # CPU workloads (preprocessing, orchestration)
  - name: cpu-general
    instanceType: m5.2xlarge
    minSize: 2
    maxSize: 10
    desiredCapacity: 3
    volumeSize: 100
    volumeType: gp3
    labels:
      workload-type: cpu
      node-lifecycle: on-demand
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/ml-platform-cluster: "owned"
    iam:
      withAddonPolicies:
        autoScaler: true
        cloudWatch: true
        ebs: true
        efs: true

  # GPU workloads - Training (spot instances for cost savings)
  - name: gpu-training-spot
    instanceTypes:
      - p3.8xlarge   # 4x V100
      - p3.16xlarge  # 8x V100
      - p4d.24xlarge # 8x A100
    minSize: 0
    maxSize: 20
    desiredCapacity: 0
    volumeSize: 500
    volumeType: gp3
    spot: true
    labels:
      workload-type: training
      gpu-type: nvidia
      node-lifecycle: spot
    taints:
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/ml-platform-cluster: "owned"
    preBootstrapCommands:
      # Install NVIDIA drivers
      - |
        #!/bin/bash
        set -ex
        # NVIDIA driver installation
        sudo yum install -y gcc kernel-devel-$(uname -r)
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
          sudo tee /etc/yum.repos.d/nvidia-docker.repo
        sudo yum clean expire-cache
        sudo yum install -y nvidia-docker2
        sudo systemctl restart docker

  # GPU workloads - Inference (on-demand for reliability)
  - name: gpu-inference
    instanceTypes:
      - g5.xlarge    # 1x A10G
      - g5.2xlarge   # 1x A10G (24GB)
    minSize: 2
    maxSize: 10
    desiredCapacity: 2
    volumeSize: 200
    volumeType: gp3
    labels:
      workload-type: inference
      gpu-type: nvidia
      node-lifecycle: on-demand
    taints:
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"

  # AWS Trainium instances for training
  - name: trainium-training
    instanceTypes:
      - trn1.32xlarge  # 16x Trainium accelerators
    minSize: 0
    maxSize: 5
    desiredCapacity: 0
    volumeSize: 1000
    volumeType: gp3
    labels:
      workload-type: training
      accelerator-type: trainium
      node-lifecycle: on-demand
    taints:
      - key: aws.amazon.com/neuron
        value: "true"
        effect: NoSchedule

  # AWS Inferentia instances for inference
  - name: inferentia-inference
    instanceTypes:
      - inf2.xlarge   # 1x Inferentia2
      - inf2.8xlarge  # 1x Inferentia2 (32GB)
    minSize: 0
    maxSize: 10
    desiredCapacity: 0
    volumeSize: 100
    volumeType: gp3
    labels:
      workload-type: inference
      accelerator-type: inferentia
      node-lifecycle: on-demand
    taints:
      - key: aws.amazon.com/neuron
        value: "true"
        effect: NoSchedule

# Add-ons
addons:
  - name: vpc-cni
    version: latest
    attachPolicyARNs:
      - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
    configurationValues: |-
      env:
        ENABLE_PREFIX_DELEGATION: "true"
        ENABLE_POD_ENI: "true"
        POD_SECURITY_GROUP_ENFORCING_MODE: standard

  - name: coredns
    version: latest

  - name: kube-proxy
    version: latest

  - name: aws-ebs-csi-driver
    version: latest
    attachPolicyARNs:
      - arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy

  - name: aws-efs-csi-driver
    version: latest

# CloudWatch Logging
cloudWatch:
  clusterLogging:
    enableTypes:
      - api
      - audit
      - authenticator
      - controllerManager
      - scheduler
    logRetentionInDays: 30
```

**Deploy EKS Cluster**:

```bash
# Create EKS cluster
eksctl create cluster -f eks-ml-cluster.yaml

# Install NVIDIA device plugin for GPU support
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml

# Install AWS Neuron device plugin for Trainium/Inferentia
kubectl apply -f https://raw.githubusercontent.com/aws-neuron/aws-neuron-sdk/master/src/k8/k8s-neuron-device-plugin.yml

# Install cluster autoscaler
# TODO: Deploy cluster autoscaler with proper IAM role

# Verify GPU nodes
kubectl get nodes -l gpu-type=nvidia
kubectl describe node <gpu-node-name>
```

### Running ML Workloads on EKS

```yaml
# PyTorch distributed training job on EKS
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: pytorch-distributed-training
  namespace: ml-platform
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          nodeSelector:
            workload-type: training
            node-lifecycle: spot
          tolerations:
          - key: nvidia.com/gpu
            operator: Exists
            effect: NoSchedule
          containers:
          - name: pytorch
            image: <account-id>.dkr.ecr.us-east-1.amazonaws.com/ml-training:latest
            command:
            - python
            - train.py
            - --backend=nccl
            - --epochs=100
            env:
            - name: NCCL_DEBUG
              value: "INFO"
            - name: NCCL_SOCKET_IFNAME
              value: "eth0"
            resources:
              limits:
                nvidia.com/gpu: 8
                memory: 240Gi
                cpu: 96
              requests:
                nvidia.com/gpu: 8
                memory: 240Gi
                cpu: 96
            volumeMounts:
            - name: training-data
              mountPath: /data
            - name: model-output
              mountPath: /output
            - name: dshm
              mountPath: /dev/shm
          volumes:
          - name: training-data
            persistentVolumeClaim:
              claimName: training-data-pvc
          - name: model-output
            persistentVolumeClaim:
              claimName: model-output-pvc
          - name: dshm
            emptyDir:
              medium: Memory
              sizeLimit: 64Gi

    Worker:
      replicas: 3
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          nodeSelector:
            workload-type: training
            node-lifecycle: spot
          tolerations:
          - key: nvidia.com/gpu
            operator: Exists
            effect: NoSchedule
          containers:
          - name: pytorch
            image: <account-id>.dkr.ecr.us-east-1.amazonaws.com/ml-training:latest
            command:
            - python
            - train.py
            - --backend=nccl
            - --epochs=100
            env:
            - name: NCCL_DEBUG
              value: "INFO"
            resources:
              limits:
                nvidia.com/gpu: 8
                memory: 240Gi
                cpu: 96
              requests:
                nvidia.com/gpu: 8
                memory: 240Gi
                cpu: 96
            volumeMounts:
            - name: training-data
              mountPath: /data
            - name: dshm
              mountPath: /dev/shm
          volumes:
          - name: training-data
            persistentVolumeClaim:
              claimName: training-data-pvc
          - name: dshm
            emptyDir:
              medium: Memory
              sizeLimit: 64Gi
```

### EKS + SageMaker Integration

```python
# Use SageMaker from EKS workloads
from kubernetes import client, config
import boto3

# Deploy SageMaker training operator on EKS
# This allows triggering SageMaker jobs from Kubernetes

"""
kubectl apply -k "github.com/aws/amazon-sagemaker-operator-for-k8s/release/rolebased?ref=v1.2.2"
"""

# Use SageMaker TrainingJob CRD
sagemaker_training_job = """
apiVersion: sagemaker.aws.amazon.com/v1
kind: TrainingJob
metadata:
  name: xgboost-training
  namespace: ml-platform
spec:
  hyperParameters:
    - name: max_depth
      value: "5"
    - name: eta
      value: "0.2"
  algorithmSpecification:
    trainingImage: 433757028032.dkr.ecr.us-east-1.amazonaws.com/xgboost:latest
    trainingInputMode: File
  roleArn: arn:aws:iam::123456789:role/sagemaker-execution-role
  region: us-east-1
  outputDataConfig:
    s3OutputPath: s3://my-bucket/models
  resourceConfig:
    instanceCount: 1
    instanceType: ml.m5.xlarge
    volumeSizeInGB: 50
  stoppingCondition:
    maxRuntimeInSeconds: 86400
  inputDataConfig:
    - channelName: train
      dataSource:
        s3DataSource:
          s3DataType: S3Prefix
          s3Uri: s3://my-bucket/training-data
          s3DataDistributionType: FullyReplicated
"""

# TODO: Apply training job from EKS
# kubectl apply -f sagemaker-training.yaml
```

## Amazon Bedrock for Generative AI {#bedrock}

Amazon Bedrock provides access to foundation models from AI companies through a unified API. It's AWS's fully managed service for building generative AI applications.

### Available Foundation Models

**Models on Bedrock (2025)**:
- **Anthropic Claude 3** (Opus, Sonnet, Haiku)
- **Amazon Titan** (Text, Embeddings, Multimodal)
- **Meta Llama 3** (70B, 8B)
- **Cohere Command** (Text generation, embeddings)
- **Stability AI** (Stable Diffusion for images)
- **AI21 Jurassic-2** (Text generation)

### Bedrock Integration for ML Platform

```python
# Integrate Bedrock into ML platform
import boto3
import json
from typing import Dict, List, Optional

class BedrockMLPlatform:
    """
    Bedrock integration for ML platform

    TODO: Implement comprehensive Bedrock API wrapper
    TODO: Add streaming support
    TODO: Implement caching for cost optimization
    """

    def __init__(self, region='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.model_ids = {
            'claude-3-opus': 'anthropic.claude-3-opus-20240229-v1:0',
            'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
            'titan-text': 'amazon.titan-text-express-v1',
            'titan-embed': 'amazon.titan-embed-text-v1',
            'llama3-70b': 'meta.llama3-70b-instruct-v1:0',
            'stable-diffusion': 'stability.stable-diffusion-xl-v1'
        }

    def generate_text(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """
        Generate text using Bedrock model

        Args:
            model: Model name (e.g., 'claude-3-sonnet')
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text response

        TODO: Add retry logic
        TODO: Implement request batching
        TODO: Add cost tracking
        """
        model_id = self.model_ids.get(model)
        if not model_id:
            raise ValueError(f"Unknown model: {model}")

        # Format request based on model
        if 'claude' in model:
            body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': max_tokens,
                'temperature': temperature,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
        elif 'titan' in model:
            body = {
                'inputText': prompt,
                'textGenerationConfig': {
                    'maxTokenCount': max_tokens,
                    'temperature': temperature,
                    'topP': kwargs.get('top_p', 0.9)
                }
            }
        elif 'llama' in model:
            body = {
                'prompt': prompt,
                'max_gen_len': max_tokens,
                'temperature': temperature,
            }

        # Invoke model
        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        # TODO: Parse based on model-specific format

        return response_body

    def generate_embeddings(
        self,
        texts: List[str],
        model: str = 'titan-embed'
    ) -> List[List[float]]:
        """
        Generate embeddings for texts

        Args:
            texts: List of input texts
            model: Embedding model name

        Returns:
            List of embedding vectors

        TODO: Implement batching for large inputs
        TODO: Add caching
        """
        model_id = self.model_ids.get(model)
        embeddings = []

        for text in texts:
            body = {'inputText': text}

            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )

            response_body = json.loads(response['body'].read())
            embeddings.append(response_body['embedding'])

        return embeddings

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        height: int = 512,
        width: int = 512,
        cfg_scale: float = 7.0,
        steps: int = 50
    ) -> bytes:
        """
        Generate image using Stable Diffusion

        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid in image
            height: Image height (must be multiple of 64)
            width: Image width (must be multiple of 64)
            cfg_scale: How strongly to follow prompt
            steps: Number of diffusion steps

        Returns:
            Image bytes (PNG format)

        TODO: Implement image variations
        TODO: Add image-to-image support
        """
        model_id = self.model_ids['stable-diffusion']

        body = {
            'text_prompts': [{'text': prompt}],
            'cfg_scale': cfg_scale,
            'steps': steps,
            'height': height,
            'width': width
        }

        if negative_prompt:
            body['text_prompts'].append({
                'text': negative_prompt,
                'weight': -1.0
            })

        response = self.bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )

        response_body = json.loads(response['body'].read())

        # Extract base64 image
        import base64
        image_data = base64.b64decode(response_body['artifacts'][0]['base64'])

        return image_data

# Usage example
bedrock = BedrockMLPlatform()

# Text generation
response = bedrock.generate_text(
    model='claude-3-sonnet',
    prompt='Explain machine learning infrastructure in simple terms',
    max_tokens=500,
    temperature=0.7
)
print(response)

# Generate embeddings
texts = ['machine learning', 'deep learning', 'artificial intelligence']
embeddings = bedrock.generate_embeddings(texts)
print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

# Generate image
image_bytes = bedrock.generate_image(
    prompt='A futuristic data center with AI infrastructure',
    height=512,
    width=512
)
with open('generated_image.png', 'wb') as f:
    f.write(image_bytes)
```

### Bedrock Guardrails

```python
# Configure Bedrock Guardrails for safe AI
import boto3

bedrock = boto3.client('bedrock')

# Create guardrail
response = bedrock.create_guardrail(
    name='ml-platform-guardrail',
    description='Guardrails for ML platform generative AI',
    topicPolicyConfig={
        'topicsConfig': [
            {
                'name': 'Financial Advice',
                'definition': 'Providing specific financial or investment advice',
                'examples': [
                    'Should I invest in this stock?',
                    'What is the best investment strategy?'
                ],
                'type': 'DENY'
            },
            {
                'name': 'Medical Advice',
                'definition': 'Providing medical diagnosis or treatment recommendations',
                'examples': [
                    'What medication should I take?',
                    'Do I have this disease?'
                ],
                'type': 'DENY'
            }
        ]
    },
    contentPolicyConfig={
        'filtersConfig': [
            {
                'type': 'SEXUAL',
                'inputStrength': 'HIGH',
                'outputStrength': 'HIGH'
            },
            {
                'type': 'VIOLENCE',
                'inputStrength': 'HIGH',
                'outputStrength': 'HIGH'
            },
            {
                'type': 'HATE',
                'inputStrength': 'HIGH',
                'outputStrength': 'HIGH'
            },
            {
                'type': 'INSULTS',
                'inputStrength': 'MEDIUM',
                'outputStrength': 'MEDIUM'
            }
        ]
    },
    wordPolicyConfig={
        'wordsConfig': [
            {'text': 'profanity1'},
            {'text': 'profanity2'}
        ],
        'managedWordListsConfig': [
            {'type': 'PROFANITY'}
        ]
    },
    sensitiveInformationPolicyConfig={
        'piiEntitiesConfig': [
            {'type': 'EMAIL', 'action': 'BLOCK'},
            {'type': 'PHONE', 'action': 'BLOCK'},
            {'type': 'SSN', 'action': 'BLOCK'},
            {'type': 'CREDIT_DEBIT_CARD_NUMBER', 'action': 'BLOCK'}
        ],
        'regexesConfig': [
            {
                'name': 'API-Key',
                'description': 'Detect API keys',
                'pattern': r'[A-Za-z0-9]{32}',
                'action': 'BLOCK'
            }
        ]
    },
    blockedInputMessaging': 'Your request was blocked by our content policy.',
    blockedOutputsMessaging': 'The generated response was blocked by our content policy.'
)

guardrail_id = response['guardrailId']
guardrail_version = response['version']

# Use guardrail with Bedrock model
bedrock_runtime = boto3.client('bedrock-runtime')

response = bedrock_runtime.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 1024,
        'messages': [
            {'role': 'user', 'content': 'User prompt here'}
        ]
    }),
    guardrailIdentifier=guardrail_id,
    guardrailVersion=guardrail_version
)

# TODO: Handle guardrail violations
```

## AWS Infrastructure for ML at Scale {#infrastructure}

### Specialized EC2 Instances for ML

**Instance Family Overview**:

| Instance Family | Use Case | Accelerator | Performance | Cost |
|----------------|----------|-------------|-------------|------|
| P5 | Large-scale training | 8x H100 (80GB) | Best | $$$$ |
| P4d/P4de | Training large models | 8x A100 (40/80GB) | Excellent | $$$ |
| P3 | Training medium models | up to 8x V100 | Good | $$ |
| G5 | Inference + training | up to 8x A10G | Good | $$ |
| G4dn | Cost-effective inference | up to 8x T4 | Moderate | $ |
| Trn1 | AWS Trainium training | 16x Trainium | Excellent | $$ |
| Inf2 | AWS Inferentia inference | up to 12x Inf2 | Excellent | $ |

**Instance Selection Guide**:

```python
# Instance selector for ML workloads
class AWSInstanceSelector:
    """
    Select optimal AWS instance for ML workload

    TODO: Integrate with AWS Pricing API
    TODO: Add real-time availability checking
    """

    def __init__(self):
        self.instances = {
            'p5.48xlarge': {
                'gpus': 8,
                'gpu_memory_gb': 80,
                'gpu_type': 'H100',
                'cpu_cores': 192,
                'memory_gb': 2048,
                'network_gbps': 3200,
                'price_per_hour': 98.32,
                'use_case': 'large-scale training'
            },
            'p4d.24xlarge': {
                'gpus': 8,
                'gpu_memory_gb': 40,
                'gpu_type': 'A100',
                'cpu_cores': 96,
                'memory_gb': 1152,
                'network_gbps': 400,
                'price_per_hour': 32.77,
                'use_case': 'training'
            },
            'g5.48xlarge': {
                'gpus': 8,
                'gpu_memory_gb': 24,
                'gpu_type': 'A10G',
                'cpu_cores': 192,
                'memory_gb': 768,
                'network_gbps': 100,
                'price_per_hour': 16.29,
                'use_case': 'inference + light training'
            },
            'g4dn.12xlarge': {
                'gpus': 4,
                'gpu_memory_gb': 16,
                'gpu_type': 'T4',
                'cpu_cores': 48,
                'memory_gb': 192,
                'network_gbps': 50,
                'price_per_hour': 3.91,
                'use_case': 'cost-effective inference'
            },
            'trn1.32xlarge': {
                'accelerators': 16,
                'accelerator_type': 'Trainium',
                'cpu_cores': 128,
                'memory_gb': 512,
                'network_gbps': 800,
                'price_per_hour': 21.50,
                'use_case': 'training (PyTorch/TensorFlow)'
            },
            'inf2.48xlarge': {
                'accelerators': 12,
                'accelerator_type': 'Inferentia2',
                'cpu_cores': 192,
                'memory_gb': 384,
                'network_gbps': 100,
                'price_per_hour': 12.98,
                'use_case': 'high-throughput inference'
            }
        }

    def recommend_instance(
        self,
        workload_type: str,
        model_size_gb: float,
        budget_per_hour: float = None,
        distributed: bool = False
    ) -> str:
        """
        Recommend optimal instance type

        Args:
            workload_type: 'training' or 'inference'
            model_size_gb: Model size in GB
            budget_per_hour: Max price per hour
            distributed: Whether distributed training/inference

        Returns:
            Recommended instance type

        TODO: Implement sophisticated recommendation logic
        TODO: Consider current spot pricing
        TODO: Factor in network requirements
        """
        # TODO: Implement recommendation algorithm
        pass

    def calculate_cost(
        self,
        instance_type: str,
        hours: float,
        use_spot: bool = False,
        spot_discount: float = 0.7
    ) -> float:
        """
        Calculate total cost for workload

        Args:
            instance_type: EC2 instance type
            hours: Runtime hours
            use_spot: Use spot instances
            spot_discount: Spot instance discount (default 70%)

        Returns:
            Total cost in USD

        TODO: Integrate real spot pricing
        """
        if instance_type not in self.instances:
            raise ValueError(f"Unknown instance: {instance_type}")

        base_price = self.instances[instance_type]['price_per_hour']

        if use_spot:
            price = base_price * spot_discount
        else:
            price = base_price

        return price * hours

# Usage
selector = AWSInstanceSelector()

# Training workload
cost_training = selector.calculate_cost(
    'p4d.24xlarge',
    hours=24,
    use_spot=True
)
print(f"Training cost: ${cost_training:.2f}")

# Inference workload
cost_inference = selector.calculate_cost(
    'g4dn.12xlarge',
    hours=24 * 30,  # 1 month
    use_spot=False
)
print(f"Monthly inference cost: ${cost_inference:.2f}")
```

### AWS Storage for ML

**S3 Storage Classes for ML Data**:

```python
# S3 storage lifecycle management for ML
import boto3
from datetime import datetime, timedelta

s3 = boto3.client('s3')

# Configure lifecycle policy for ML artifacts
lifecycle_policy = {
    'Rules': [
        {
            'Id': 'TransitionTrainingData',
            'Status': 'Enabled',
            'Prefix': 'training-data/',
            'Transitions': [
                {
                    'Days': 90,
                    'StorageClass': 'INTELLIGENT_TIERING'
                },
                {
                    'Days': 365,
                    'StorageClass': 'GLACIER_IR'
                }
            ]
        },
        {
            'Id': 'ExpireOldCheckpoints',
            'Status': 'Enabled',
            'Prefix': 'checkpoints/',
            'Expiration': {
                'Days': 30
            }
        },
        {
            'Id': 'ArchiveModels',
            'Status': 'Enabled',
            'Prefix': 'models/',
            'Transitions': [
                {
                    'Days': 180,
                    'StorageClass': 'GLACIER_FLEXIBLE_RETRIEVAL'
                }
            ],
            'NoncurrentVersionTransitions': [
                {
                    'NoncurrentDays': 30,
                    'StorageClass': 'GLACIER_FLEXIBLE_RETRIEVAL'
                }
            ]
        }
    ]
}

# Apply lifecycle policy
# TODO: Apply to actual bucket
# s3.put_bucket_lifecycle_configuration(
#     Bucket='ml-artifacts-bucket',
#     LifecycleConfiguration=lifecycle_policy
# )
```

**EFS for Shared ML Storage**:

```yaml
# EFS for shared training data
apiVersion: v1
kind: PersistentVolume
metadata:
  name: efs-training-data
spec:
  capacity:
    storage: 1Ti
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: efs-sc
  csi:
    driver: efs.csi.aws.com
    volumeHandle: fs-12345678  # EFS file system ID
    volumeAttributes:
      path: /training-data
      basePath: /
      provisioningMode: efs-ap
      gidRangeStart: "1000"
      gidRangeEnd: "2000"
      directoryPerms: "777"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: efs-training-data-claim
  namespace: ml-platform
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 100Gi  # Arbitrary for EFS
  volumeName: efs-training-data
```

**FSx for Lustre for High-Performance ML**:

```python
# Create FSx for Lustre file system
import boto3

fsx = boto3.client('fsx')

response = fsx.create_file_system(
    FileSystemType='LUSTRE',
    StorageCapacity=1200,  # GB
    StorageType='SSD',
    SubnetIds=['subnet-12345'],
    SecurityGroupIds=['sg-12345'],
    LustreConfiguration={
        'ImportPath': 's3://ml-training-data/',  # Import from S3
        'ExportPath': 's3://ml-training-data/results/',
        'DeploymentType': 'SCRATCH_2',  # For temporary, high-performance workloads
        'PerUnitStorageThroughput': 200,  # MB/s/TB
        'DataCompressionType': 'LZ4'
    },
    Tags=[
        {'Key': 'Name', 'Value': 'ml-training-lustre'},
        {'Key': 'Project', 'Value': 'MLPlatform'}
    ]
)

filesystem_id = response['FileSystem']['FileSystemId']
print(f"Created FSx Lustre file system: {filesystem_id}")

# TODO: Mount in EKS cluster
# TODO: Configure auto-import/export
```

## Cost Optimization on AWS {#cost-optimization}

### Spot Instances for Training

```python
# Spot instance management for ML training
import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')

# Check current spot prices
response = ec2.describe_spot_price_history(
    InstanceTypes=['p3.8xlarge', 'p4d.24xlarge', 'g5.12xlarge'],
    ProductDescriptions=['Linux/UNIX'],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow()
)

# Group by instance type
spot_prices = {}
for price_point in response['SpotPriceHistory']:
    instance_type = price_point['InstanceType']
    price = float(price_point['SpotPrice'])

    if instance_type not in spot_prices or price < spot_prices[instance_type]:
        spot_prices[instance_type] = price

# Compare to on-demand pricing
on_demand_prices = {
    'p3.8xlarge': 12.24,
    'p4d.24xlarge': 32.77,
    'g5.12xlarge': 5.67
}

print("Spot Instance Savings:")
for instance_type, spot_price in spot_prices.items():
    on_demand = on_demand_prices[instance_type]
    savings = (1 - (spot_price / on_demand)) * 100
    print(f"{instance_type}: ${spot_price:.2f}/hr (${on_demand:.2f} on-demand) - {savings:.1f}% savings")

# TODO: Implement spot instance interruption handling
# TODO: Set up spot fleet with multiple instance types
# TODO: Configure checkpointing for training resilience
```

### Savings Plans and Reserved Instances

```python
# Calculate savings plans vs on-demand
class AWSSavingsPlanCalculator:
    """
    Calculate optimal savings plan commitment

    TODO: Integrate with Cost Explorer API
    TODO: Add recommendations engine
    """

    def __init__(self):
        self.savings_rates = {
            '1-year-no-upfront': 0.28,      # 28% savings
            '1-year-partial-upfront': 0.33,  # 33% savings
            '1-year-full-upfront': 0.35,     # 35% savings
            '3-year-no-upfront': 0.48,       # 48% savings
            '3-year-partial-upfront': 0.52,  # 52% savings
            '3-year-full-upfront': 0.54,     # 54% savings
        }

    def calculate_savings(
        self,
        monthly_spend: float,
        commitment_term: str = '1-year-no-upfront'
    ) -> dict:
        """
        Calculate savings from commitment

        Args:
            monthly_spend: Current monthly on-demand spend
            commitment_term: Savings plan term and payment option

        Returns:
            Savings analysis

        TODO: Factor in usage patterns
        TODO: Consider compute vs SageMaker savings plans
        """
        savings_rate = self.savings_rates.get(commitment_term, 0)
        annual_spend = monthly_spend * 12
        annual_savings = annual_spend * savings_rate

        return {
            'annual_spend_on_demand': annual_spend,
            'annual_spend_with_plan': annual_spend * (1 - savings_rate),
            'annual_savings': annual_savings,
            'monthly_savings': annual_savings / 12,
            'savings_percentage': savings_rate * 100
        }

calculator = AWSSavingsPlanCalculator()

# Example: $50K/month ML infrastructure spend
savings = calculator.calculate_savings(
    monthly_spend=50000,
    commitment_term='1-year-no-upfront'
)

print(f"Annual savings: ${savings['annual_savings']:,.2f}")
print(f"Monthly savings: ${savings['monthly_savings']:,.2f}")
print(f"Savings rate: {savings['savings_percentage']:.1f}%")
```

### Cost Monitoring and Optimization

```python
# AWS Cost monitoring for ML workloads
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce')  # Cost Explorer

# Get cost and usage for ML services
def get_ml_costs(days=30):
    """
    Get ML infrastructure costs

    TODO: Add cost breakdown by project/team
    TODO: Implement cost anomaly detection
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost', 'UsageQuantity'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': 'Project'}
        ],
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': [
                    'Amazon Elastic Compute Cloud - Compute',
                    'Amazon SageMaker',
                    'Amazon Elastic Kubernetes Service',
                    'Amazon Simple Storage Service'
                ]
            }
        }
    )

    # TODO: Parse and analyze costs
    # TODO: Generate cost optimization recommendations

    return response

# Set up cost alerts
# TODO: Configure AWS Budgets with alerts
# TODO: Set up Cost Anomaly Detection
```

## Real-World Architectures {#real-world}

### End-to-End ML Platform on AWS

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                 │
│  │ Kinesis│  │   MSK  │  │   DMS  │  │   S3   │                 │
│  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘                 │
└──────┼───────────┼───────────┼───────────┼────────────────────────┘
       │           │           │           │
┌──────┴───────────┴───────────┴───────────┴────────────────────────┐
│                  Data Processing Layer                             │
│  ┌────────────────────────────────────────────────────┐            │
│  │              AWS Glue / EMR Spark                  │            │
│  │         (Data cleaning, feature engineering)       │            │
│  └──────────────────────┬──────────────────────────── ┘            │
└─────────────────────────┼───────────────────────────────────────── ┘
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                  Feature Store Layer                               │
│  ┌──────────────────────┴────────────────────────────┐            │
│  │         SageMaker Feature Store                    │            │
│  │    (Online + Offline feature storage)              │            │
│  └──────────────────────┬────────────────────────────┘            │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                  Training Layer                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ SageMaker   │  │   EKS +     │  │    EC2      │               │
│  │  Training   │  │  Kubeflow   │  │  Training   │               │
│  │  (Managed)  │  │ (K8s-native)│  │ (Custom)    │               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
┌─────────┴────────────────┴────────────────┴───────────────────────┐
│                  Model Registry                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  SageMaker Model Registry + ECR (containers)         │         │
│  └──────────────────────┬───────────────────────────────┘         │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────────────┐
│                  Inference Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ SageMaker   │  │   EKS +     │  │   Lambda    │               │
│  │ Endpoints   │  │   KServe    │  │  +Inferentia│               │
│  │ (Real-time) │  │ (K8s-native)│  │ (Serverless)│               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
┌─────────┴────────────────┴────────────────┴───────────────────────┐
│                  API Gateway Layer                                 │
│  ┌──────────────────────────────────────────────────────┐         │
│  │   API Gateway + ALB/NLB + CloudFront (CDN)           │         │
│  └──────────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────┘

Cross-Cutting Concerns:
├── Monitoring: CloudWatch + Prometheus + Grafana
├── Logging: CloudWatch Logs + ELK Stack
├── Security: IAM + VPC + Security Groups + KMS
├── Cost Management: Cost Explorer + Budgets + Savings Plans
└── CI/CD: CodePipeline + GitHub Actions + ArgoCD
```

### Terraform Infrastructure Example

```hcl
# Main AWS ML infrastructure
# TODO: Complete Terraform configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "ml-platform-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "MLPlatform"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# VPC for ML infrastructure
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "ml-platform-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  # S3 VPC endpoint for faster access
  enable_s3_endpoint = true

  # ECR VPC endpoint for container images
  enable_ecr_dkr_endpoint = true
  enable_ecr_api_endpoint = true
}

# EKS cluster for ML workloads
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "ml-platform-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # TODO: Add node groups configuration
  # TODO: Add IAM roles for service accounts
  # TODO: Configure cluster addons
}

# S3 buckets for ML artifacts
resource "aws_s3_bucket" "ml_artifacts" {
  bucket = "ml-platform-artifacts-${var.account_id}"
}

resource "aws_s3_bucket_versioning" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_artifacts" {
  bucket = aws_s3_bucket.ml_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# SageMaker execution role
# TODO: Create IAM role for SageMaker
# TODO: Create IAM role for EKS nodes
# TODO: Configure security groups
```

## Best Practices {#best-practices}

### Security Best Practices

1. **Use IAM Roles, Not Access Keys**: Always use IAM roles for EC2, EKS, SageMaker
2. **Enable Encryption**: Encrypt data at rest (S3, EBS) and in transit (TLS)
3. **VPC Isolation**: Deploy ML infrastructure in private subnets
4. **Least Privilege**: Grant minimum necessary permissions
5. **Audit Logging**: Enable CloudTrail and VPC Flow Logs

### Cost Optimization Best Practices

1. **Use Spot Instances**: 70-90% savings for fault-tolerant training
2. **Right-Size Instances**: Don't over-provision resources
3. **Implement Auto-Scaling**: Scale based on actual demand
4. **Use Savings Plans**: Commit to steady-state usage
5. **Lifecycle Policies**: Move old data to cheaper storage tiers
6. **Monitor Costs**: Set up budgets and alerts

### Performance Optimization Best Practices

1. **Use FSx Lustre**: For high-throughput training data access
2. **Enable EFA**: For distributed training on P4d/P5 instances
3. **Optimize Data Pipeline**: Minimize data transfer and preprocessing
4. **GPU Utilization**: Monitor and maximize GPU usage
5. **Batch Efficiently**: Optimize batch sizes for hardware

## Summary {#summary}

AWS provides comprehensive services for building production ML infrastructure:

**Key Takeaways**:
1. **SageMaker**: Fully managed ML platform for end-to-end workflows
2. **EKS**: Kubernetes-based flexibility for custom ML workloads
3. **Bedrock**: Easy access to foundation models for generative AI
4. **Specialized Hardware**: P5, P4d, Trainium, Inferentia for different needs
5. **Cost Optimization**: Spot instances, savings plans, right-sizing

**When to Use What**:
- **SageMaker**: Quick iteration, managed infrastructure, teams wanting less ops burden
- **EKS**: Custom ML workflows, multi-cloud portability, complex orchestration
- **Bedrock**: Building generative AI applications without model training
- **EC2 Direct**: Maximum control, custom hardware configurations

**Next Steps**:
1. Design AWS architecture for your ML use case
2. Implement cost optimization strategies
3. Set up security and compliance controls
4. Deploy pilot ML workloads
5. Monitor and optimize performance

---

**Estimated Reading Time**: 120-150 minutes
**Hands-on Labs**: 10-12 hours
**Prerequisites**: AWS account, basic AWS knowledge
