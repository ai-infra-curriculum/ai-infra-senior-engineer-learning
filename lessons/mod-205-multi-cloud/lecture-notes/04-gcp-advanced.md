# Lecture 04: GCP Advanced Services for ML Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:

- Design production ML systems on GCP leveraging Vertex AI for managed ML, GKE for Kubernetes workloads, and Cloud TPU infrastructure for large-scale training
- Architect Vertex AI pipelines integrating data preparation with BigQuery, distributed training with custom containers, hyperparameter tuning, and Vertex Endpoints for serving
- Configure GKE clusters optimized for ML workloads with TPU/GPU node pools, GKE Autopilot for serverless nodes, and GCS FUSE for data access patterns
- Implement Cloud TPU training workflows for large models (>10B parameters) using TPU Pods, JAX/TensorFlow frameworks, and TPU-optimized data pipelines
- Design BigQuery ML architectures for in-warehouse ML using SQL-based model training, AutoML Tables integration, and federated queries across clouds
- Configure GCP cost optimization strategies using Preemptible VMs for training, committed use discounts for inference, and BigQuery slot reservations
- Architect GCP networking for ML including VPC design, Private Google Access for GCS/BigQuery, Cloud Interconnect for hybrid, and multi-region failover
- Build production ML platforms on GCP integrating Cloud IAM, Cloud Monitoring, Pub/Sub for event-driven workflows, and GCP compliance frameworks (ISO, SOC2)

## Table of Contents
1. [Introduction](#introduction)
2. [Vertex AI Platform](#vertex-ai)
3. [Google Kubernetes Engine (GKE)](#gke)
4. [Cloud TPU Infrastructure](#cloud-tpu)
5. [GCP ML Infrastructure Patterns](#infrastructure)
6. [BigQuery ML](#bigquery-ml)
7. [Cost Optimization on GCP](#cost-optimization)
8. [Real-World Architectures](#real-world)
9. [Summary](#summary)

## Introduction {#introduction}

Google Cloud Platform (GCP) has unique strengths in ML infrastructure, particularly in areas where Google itself has deep expertise: distributed systems, TPUs, and large-scale data analytics. As a Senior AI Infrastructure Engineer, understanding GCP's ML services enables you to leverage Google's internal technologies for your ML workloads.

### GCP's ML Differentiators

**What Makes GCP Unique**:
1. **TPU Technology**: Custom ML accelerators designed by Google (used for training GPT, BERT, PaLM)
2. **TensorFlow Integration**: Deepest integration with TensorFlow ecosystem
3. **BigQuery**: Serverless data warehouse with built-in ML capabilities
4. **Google-Scale Infrastructure**: Technologies proven at massive scale (Borg → Kubernetes)
5. **Research Leadership**: Access to cutting-edge research (Transformers, Attention, etc.)

**GCP vs AWS vs Azure for ML**:
```
| Capability          | GCP                | AWS              | Azure           |
|--------------------|--------------------|------------------|-----------------|
| Custom Accelerators| TPU (Excellent)    | Trainium (Good)  | None (Fair)     |
| Managed ML Platform| Vertex AI (Good)   | SageMaker (Best) | Azure ML (Good) |
| Kubernetes         | GKE (Excellent)    | EKS (Good)       | AKS (Good)      |
| Data Warehouse ML  | BigQuery ML (Best) | Redshift ML (Good)| Synapse (Good)  |
| Research Integration| Best               | Good             | Good            |
| Enterprise Support | Good               | Excellent        | Excellent       |
```

### GCP Regions for ML Workloads

**Best Regions for ML (2025)**:
- **us-central1 (Iowa)**: Best TPU availability, Google's largest datacenter region
- **us-west1 (Oregon)**: Good GPU/TPU availability, low latency to West Coast
- **europe-west4 (Netherlands)**: Best for EU with TPU access
- **asia-southeast1 (Singapore)**: Best for Asia-Pacific with ML hardware

**TPU Availability by Region**:
```python
# GCP TPU availability checker
gcp_tpu_availability = {
    'us-central1': {
        'tpu-v2': True,
        'tpu-v3': True,
        'tpu-v4': True,
        'tpu-v5': True,   # Latest generation
        'tpu-v5p': True,  # Performance optimized
    },
    'us-west1': {
        'tpu-v2': True,
        'tpu-v3': True,
        'tpu-v4': True,
        'tpu-v5': False,  # Limited availability
    },
    'europe-west4': {
        'tpu-v2': True,
        'tpu-v3': True,
        'tpu-v4': True,
        'tpu-v5': False,
    }
}

# GPU availability
gcp_gpu_availability = {
    'us-central1': {
        'nvidia-tesla-t4': True,
        'nvidia-tesla-v100': True,
        'nvidia-tesla-a100': True,
        'nvidia-a100-80gb': True,
        'nvidia-h100-80gb': True,  # Latest
        'nvidia-l4': True,          # Cost-effective inference
    }
}
```

## Vertex AI Platform {#vertex-ai}

Vertex AI is GCP's unified ML platform that brings together Google Cloud's ML offerings under one unified API and user interface.

### Vertex AI Architecture

**Core Components**:
1. **Vertex AI Workbench**: Managed Jupyter notebooks
2. **Vertex AI Training**: Custom and AutoML training
3. **Vertex AI Prediction**: Model deployment and serving
4. **Vertex AI Pipelines**: ML workflow orchestration (based on Kubeflow Pipelines)
5. **Vertex AI Feature Store**: Centralized feature management
6. **Vertex AI Model Registry**: Model versioning and metadata
7. **Vertex AI Experiments**: Experiment tracking and comparison
8. **Vertex AI Metadata**: Lineage tracking for ML artifacts

### Vertex AI Training Deep Dive

**Custom Training on Vertex AI**:

```python
# Vertex AI custom training job
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip_gapic
import google.cloud.aiplatform as aip

# TODO: Initialize Vertex AI
PROJECT_ID = 'your-project-id'
REGION = 'us-central1'
STAGING_BUCKET = 'gs://your-bucket'

aip.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=STAGING_BUCKET
)

# Define custom training job
custom_job = aip.CustomTrainingJob(
    display_name='pytorch-distributed-training',
    script_path='training/train.py',
    container_uri='gcr.io/cloud-aiplatform/training/pytorch-gpu.1-13:latest',
    requirements=['transformers==4.35.0', 'datasets==2.14.0'],
    model_serving_container_image_uri='gcr.io/cloud-aiplatform/prediction/pytorch-gpu.1-13:latest',
)

# Configure distributed training
model = custom_job.run(
    dataset=None,  # Custom data loading in script
    replica_count=4,  # 4 training replicas
    machine_type='n1-standard-16',
    accelerator_type='NVIDIA_TESLA_V100',
    accelerator_count=4,  # 4 V100s per replica = 16 total GPUs
    
    # Training arguments passed to script
    args=[
        '--model_name=bert-large-uncased',
        '--epochs=10',
        '--batch_size=32',
        '--learning_rate=5e-5',
        '--gradient_accumulation_steps=4',
    ],
    
    # Environment variables
    environment_variables={
        'NCCL_DEBUG': 'INFO',
        'TF_CPP_MIN_LOG_LEVEL': '0',
    },
    
    # Restart on failure
    restart_job_on_worker_restart=True,
    
    # Training timeout
    timeout=43200,  # 12 hours
    
    # Use preemptible VMs for cost savings (up to 80% off)
    reduction_server_replica_count=0,  # For large-scale training
    reduction_server_machine_type=None,
    
    # Output location
    base_output_dir=f'{STAGING_BUCKET}/training-output',
    
    # Service account
    service_account='ml-training@your-project.iam.gserviceaccount.com',
    
    # Network configuration
    network='projects/YOUR_PROJECT_NUMBER/global/networks/YOUR_NETWORK',
    
    # Enable training data caching
    enable_web_access=False,  # Security
    enable_dashboard_access=False,
    
    # Labels for organization
    labels={
        'team': 'ml-engineering',
        'project': 'ml-platform',
        'environment': 'production'
    }
)

# Get model URI
print(f"Model artifact location: {model.uri}")
print(f"Training job resource name: {model.resource_name}")

# TODO: Add model to registry
# TODO: Deploy for inference
```

**Training Script (train.py) for Vertex AI**:

```python
"""
Vertex AI training script with distributed training support
Compatible with Vertex AI custom training jobs
"""

import argparse
import json
import os
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AdamW
from datasets import load_dataset
import google.cloud.aiplatform as aip

# Vertex AI environment variables
# These are automatically set by Vertex AI
AIP_MODEL_DIR = os.environ.get('AIP_MODEL_DIR')  # Model output directory
AIP_TENSORBOARD_LOG_DIR = os.environ.get('AIP_TENSORBOARD_LOG_DIR')  # TensorBoard logs
AIP_CHECKPOINT_DIR = os.environ.get('AIP_CHECKPOINT_DIR')  # Checkpoint directory

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    
    # Model arguments
    parser.add_argument('--model_name', type=str, default='bert-base-uncased')
    parser.add_argument('--num_labels', type=int, default=2)
    
    # Training arguments
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--learning_rate', type=float, default=2e-5)
    parser.add_argument('--gradient_accumulation_steps', type=int, default=1)
    parser.add_argument('--warmup_steps', type=int, default=500)
    parser.add_argument('--max_length', type=int, default=512)
    
    # Data arguments
    parser.add_argument('--dataset_name', type=str, default='glue')
    parser.add_argument('--dataset_config', type=str, default='mrpc')
    
    return parser.parse_args()

def setup_distributed():
    """
    Setup distributed training for Vertex AI
    Vertex AI sets up the cluster automatically
    
    TODO: Add error handling for non-distributed setups
    """
    if 'WORLD_SIZE' in os.environ:
        # Distributed training
        dist.init_process_group(backend='nccl')
        world_size = int(os.environ['WORLD_SIZE'])
        rank = int(os.environ['RANK'])
        local_rank = int(os.environ.get('LOCAL_RANK', 0))
    else:
        # Single-node training
        world_size = 1
        rank = 0
        local_rank = 0
    
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank)
        device = torch.device(f'cuda:{local_rank}')
    else:
        device = torch.device('cpu')
    
    return world_size, rank, local_rank, device

def load_data(args, tokenizer, rank, world_size):
    """
    Load and prepare dataset
    
    TODO: Implement efficient data loading from GCS
    TODO: Add data augmentation
    TODO: Implement streaming for large datasets
    """
    # Load dataset
    dataset = load_dataset(args.dataset_name, args.dataset_config)
    
    def tokenize_function(examples):
        return tokenizer(
            examples['sentence1'],
            examples['sentence2'],
            truncation=True,
            padding='max_length',
            max_length=args.max_length
        )
    
    # Tokenize dataset
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset['train'].column_names
    )
    
    # Create dataloaders with distributed sampler
    train_sampler = DistributedSampler(
        tokenized_dataset['train'],
        num_replicas=world_size,
        rank=rank,
        shuffle=True
    )
    
    train_dataloader = DataLoader(
        tokenized_dataset['train'],
        batch_size=args.batch_size,
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True
    )
    
    # Validation dataloader (replicated on all workers)
    val_dataloader = DataLoader(
        tokenized_dataset['validation'],
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    return train_dataloader, val_dataloader, train_sampler

def train_epoch(model, dataloader, optimizer, scheduler, device, epoch, args, rank):
    """
    Train for one epoch
    
    TODO: Implement gradient accumulation
    TODO: Add mixed precision training
    TODO: Implement checkpointing
    """
    model.train()
    total_loss = 0
    
    for step, batch in enumerate(dataloader):
        # Move batch to device
        batch = {k: v.to(device) for k, v in batch.items()}
        
        # Forward pass
        outputs = model(**batch)
        loss = outputs.loss
        
        # Backward pass
        loss.backward()
        
        # Optimizer step (with gradient accumulation)
        if (step + 1) % args.gradient_accumulation_steps == 0:
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        
        total_loss += loss.item()
        
        # Log progress (only on rank 0)
        if rank == 0 and step % 100 == 0:
            print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")
            
            # TODO: Log to TensorBoard
            # TODO: Log to Vertex AI Experiments
    
    avg_loss = total_loss / len(dataloader)
    return avg_loss

def validate(model, dataloader, device, rank):
    """
    Validate model
    
    TODO: Implement comprehensive evaluation metrics
    TODO: Add confusion matrix
    """
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            
            loss = outputs.loss
            total_loss += loss.item()
            
            # Calculate accuracy
            predictions = torch.argmax(outputs.logits, dim=-1)
            correct += (predictions == batch['labels']).sum().item()
            total += batch['labels'].size(0)
    
    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total
    
    if rank == 0:
        print(f"Validation Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
    
    return avg_loss, accuracy

def save_model(model, tokenizer, args, rank):
    """
    Save model artifacts to Vertex AI model directory
    
    TODO: Save model in format compatible with Vertex AI Prediction
    TODO: Add model metadata
    """
    if rank != 0:
        return  # Only save on rank 0
    
    # Save to Vertex AI model directory
    output_dir = AIP_MODEL_DIR or './model_output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model and tokenizer
    model.module.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Save training configuration
    config = {
        'model_name': args.model_name,
        'num_labels': args.num_labels,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate
    }
    
    with open(os.path.join(output_dir, 'training_config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Model saved to {output_dir}")

def main():
    """Main training function"""
    args = parse_args()
    
    # Setup distributed training
    world_size, rank, local_rank, device = setup_distributed()
    
    if rank == 0:
        print(f"Starting training on {world_size} GPUs")
        print(f"Arguments: {args}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=args.num_labels
    )
    model = model.to(device)
    
    # Wrap model with DDP
    if world_size > 1:
        model = DDP(model, device_ids=[local_rank], output_device=local_rank)
    
    # Load data
    train_dataloader, val_dataloader, train_sampler = load_data(
        args, tokenizer, rank, world_size
    )
    
    # Setup optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)
    
    # TODO: Implement proper learning rate scheduler
    from transformers import get_linear_schedule_with_warmup
    total_steps = len(train_dataloader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=args.warmup_steps,
        num_training_steps=total_steps
    )
    
    # Training loop
    for epoch in range(args.epochs):
        # Set epoch for distributed sampler
        if world_size > 1:
            train_sampler.set_epoch(epoch)
        
        # Train
        train_loss = train_epoch(
            model, train_dataloader, optimizer, scheduler,
            device, epoch, args, rank
        )
        
        # Validate
        val_loss, val_accuracy = validate(model, val_dataloader, device, rank)
        
        if rank == 0:
            print(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, "
                  f"Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.4f}")
        
        # TODO: Save checkpoint
        # TODO: Early stopping based on validation metrics
    
    # Save final model
    save_model(model, tokenizer, args, rank)
    
    if rank == 0:
        print("Training completed successfully!")

if __name__ == '__main__':
    main()
```

### TPU Training on Vertex AI

**Using TPUs for Training**:

```python
# Vertex AI TPU training
from google.cloud import aiplatform as aip

# Initialize
aip.init(project='your-project', location='us-central1')

# TPU training job
tpu_job = aip.CustomTrainingJob(
    display_name='tpu-training-job',
    script_path='training/train_tpu.py',
    container_uri='gcr.io/cloud-aiplatform/training/tf-tpu.2-13:latest',
    requirements=['tensorflow==2.13.0', 'tensorflow-datasets==4.9.0'],
)

# Run on TPU
model = tpu_job.run(
    replica_count=1,
    machine_type='cloud-tpu',  # TPU-enabled machine type
    accelerator_type='TPU_V4',  # TPU v4
    accelerator_count=8,  # 8-core TPU pod
    
    # TPU-specific arguments
    args=[
        '--tpu_name=local',  # Vertex AI sets this up
        '--model_dir=gs://your-bucket/tpu-model',
        '--batch_size=1024',  # Large batch size for TPU efficiency
        '--steps_per_loop=1000',  # TPU-optimized training loop
    ],
    
    base_output_dir='gs://your-bucket/tpu-output',
    timeout=86400,  # 24 hours
)
```

**TensorFlow TPU Training Script**:

```python
"""
TensorFlow training script optimized for TPUs
Compatible with Vertex AI TPU training
"""

import tensorflow as tf
import tensorflow_datasets as tfds
import os

def create_model(num_classes=10):
    """
    Create model compatible with TPU training
    
    TODO: Implement custom model architecture
    TODO: Add model configuration options
    """
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224, 224, 3)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, 3, activation='relu'),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes)
    ])
    return model

def prepare_dataset(dataset, batch_size):
    """
    Prepare dataset for TPU training
    
    TODO: Add data augmentation
    TODO: Optimize data pipeline for TPU
    """
    def preprocess(example):
        image = example['image']
        image = tf.cast(image, tf.float32) / 255.0
        image = tf.image.resize(image, [224, 224])
        label = example['label']
        return image, label
    
    dataset = dataset.map(
        preprocess,
        num_parallel_calls=tf.data.AUTOTUNE
    )
    dataset = dataset.cache()
    dataset = dataset.shuffle(10000)
    dataset = dataset.batch(batch_size, drop_remainder=True)  # drop_remainder important for TPU
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset

def train_on_tpu():
    """
    Main training function for TPU
    
    TODO: Implement comprehensive training logic
    TODO: Add checkpointing
    TODO: Add TensorBoard logging
    """
    # TPU initialization
    resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu='local')
    tf.config.experimental_connect_to_cluster(resolver)
    tf.tpu.experimental.initialize_tpu_system(resolver)
    
    # Create TPU strategy
    strategy = tf.distribute.TPUStrategy(resolver)
    
    print(f"Running on TPU with {strategy.num_replicas_in_sync} replicas")
    
    # Load dataset
    ds_train, ds_info = tfds.load(
        'imagenet2012',
        split='train',
        with_info=True,
        as_supervised=False
    )
    
    ds_val = tfds.load('imagenet2012', split='validation', as_supervised=False)
    
    # Prepare datasets
    BATCH_SIZE = 1024  # Large batch size for TPU
    EPOCHS = 90
    
    train_dataset = prepare_dataset(ds_train, BATCH_SIZE)
    val_dataset = prepare_dataset(ds_val, BATCH_SIZE)
    
    # Create model within strategy scope
    with strategy.scope():
        model = create_model(num_classes=1000)
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.SGD(learning_rate=0.1, momentum=0.9),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )
    
    # Setup callbacks
    model_dir = os.environ.get('AIP_MODEL_DIR', './model_output')
    
    callbacks = [
        tf.keras.callbacks.TensorBoard(
            log_dir=os.environ.get('AIP_TENSORBOARD_LOG_DIR', './logs')
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(model_dir, 'checkpoint_{epoch:02d}.h5'),
            save_best_only=True,
            monitor='val_accuracy'
        ),
        tf.keras.callbacks.LearningRateScheduler(
            lambda epoch: 0.1 * (0.1 ** (epoch // 30))
        )
    ]
    
    # Train model
    history = model.fit(
        train_dataset,
        epochs=EPOCHS,
        validation_data=val_dataset,
        callbacks=callbacks,
        steps_per_execution=1000,  # TPU optimization
    )
    
    # Save final model
    model.save(os.path.join(model_dir, 'final_model'))
    
    print("Training completed successfully!")
    return history

if __name__ == '__main__':
    train_on_tpu()
```

### Vertex AI Prediction

**Deploy Model for Inference**:

```python
# Deploy model to Vertex AI endpoint
from google.cloud import aiplatform as aip

# Initialize
aip.init(project='your-project', location='us-central1')

# Upload model to registry
model = aip.Model.upload(
    display_name='bert-classifier',
    artifact_uri='gs://your-bucket/model-artifacts',
    serving_container_image_uri='gcr.io/cloud-aiplatform/prediction/pytorch-gpu.1-13:latest',
    serving_container_environment_variables={
        'MODEL_NAME': 'bert-classifier',
        'NUM_WORKERS': '4',
    },
    serving_container_ports=[8080],
    description='BERT text classification model',
    labels={'team': 'ml-engineering', 'version': 'v1'},
)

# Create endpoint
endpoint = aip.Endpoint.create(
    display_name='bert-classifier-endpoint',
    description='Production endpoint for text classification',
    labels={'environment': 'production'},
)

# Deploy model to endpoint
model.deploy(
    endpoint=endpoint,
    deployed_model_display_name='bert-classifier-v1',
    machine_type='n1-standard-4',
    min_replica_count=2,  # Minimum instances
    max_replica_count=10,  # Maximum instances
    accelerator_type='NVIDIA_TESLA_T4',
    accelerator_count=1,
    
    # Traffic split for A/B testing
    traffic_percentage=100,
    traffic_split={'0': 100},  # 100% to this model version
    
    # Auto-scaling configuration
    autoscaling_metric_specs=[
        {
            'metric_name': 'aiplatform.googleapis.com/prediction/online/cpu/utilization',
            'target': 70,  # Target 70% CPU utilization
        },
        {
            'metric_name': 'aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle',
            'target': 80,  # Target 80% GPU utilization
        }
    ],
    
    # Enable request-response logging (for monitoring)
    enable_access_logging=True,
    enable_container_logging=True,
    
    # Service account
    service_account='ml-inference@your-project.iam.gserviceaccount.com',
)

print(f"Model deployed to endpoint: {endpoint.resource_name}")

# Test prediction
test_instances = [
    {"text": "This is a great product!"},
    {"text": "I'm very disappointed with this service."}
]

predictions = endpoint.predict(instances=test_instances)
print(f"Predictions: {predictions}")

# TODO: Configure monitoring and alerting
# TODO: Set up A/B testing with traffic splits
# TODO: Implement prediction caching for cost optimization
```

### Vertex AI Pipelines

```python
# Define ML pipeline using Kubeflow Pipelines
from kfp.v2 import dsl
from kfp.v2.dsl import component, Input, Output, Dataset, Model, Metrics
from google.cloud import aiplatform as aip

@component(
    base_image='python:3.9',
    packages_to_install=['pandas==1.5.0', 'google-cloud-storage==2.10.0']
)
def preprocess_data(
    input_data: Input[Dataset],
    output_data: Output[Dataset],
    train_split: float = 0.8
):
    """
    Preprocess data for training
    
    TODO: Implement data preprocessing logic
    TODO: Add data validation
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    
    # Load data
    df = pd.read_csv(input_data.path)
    
    # TODO: Data cleaning and preprocessing
    
    # Save processed data
    df.to_csv(output_data.path, index=False)

@component(
    base_image='gcr.io/cloud-aiplatform/training/pytorch-gpu.1-13:latest',
    packages_to_install=['transformers==4.35.0']
)
def train_model(
    training_data: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
    epochs: int = 10,
    batch_size: int = 32
):
    """
    Train model
    
    TODO: Implement training logic
    TODO: Log metrics to Vertex AI Experiments
    """
    # TODO: Training implementation
    
    # Log metrics
    metrics.log_metric('accuracy', 0.95)
    metrics.log_metric('loss', 0.15)

@component
def evaluate_model(
    model: Input[Model],
    test_data: Input[Dataset],
    metrics: Output[Metrics],
    threshold: float = 0.90
) -> str:
    """
    Evaluate model performance
    
    TODO: Implement evaluation logic
    TODO: Add comprehensive metrics
    """
    # TODO: Evaluation implementation
    
    accuracy = 0.95
    metrics.log_metric('test_accuracy', accuracy)
    
    if accuracy >= threshold:
        return 'deploy'
    else:
        return 'reject'

@dsl.pipeline(
    name='ml-training-pipeline',
    description='End-to-end ML training pipeline',
    pipeline_root='gs://your-bucket/pipeline-root'
)
def ml_pipeline(
    input_data_uri: str,
    train_split: float = 0.8,
    epochs: int = 10,
    batch_size: int = 32,
    accuracy_threshold: float = 0.90
):
    """
    Define ML pipeline
    
    TODO: Add more pipeline steps
    TODO: Implement conditional deployment
    """
    # Step 1: Preprocess data
    preprocess_task = preprocess_data(
        input_data=input_data_uri,
        train_split=train_split
    )
    
    # Step 2: Train model
    train_task = train_model(
        training_data=preprocess_task.outputs['output_data'],
        epochs=epochs,
        batch_size=batch_size
    )
    
    # Step 3: Evaluate model
    eval_task = evaluate_model(
        model=train_task.outputs['model'],
        test_data=preprocess_task.outputs['output_data'],
        threshold=accuracy_threshold
    )
    
    # TODO: Step 4: Conditional model deployment
    # TODO: Step 5: Model monitoring setup

# Compile and submit pipeline
from kfp.v2 import compiler

compiler.Compiler().compile(
    pipeline_func=ml_pipeline,
    package_path='ml_pipeline.json'
)

# Submit pipeline to Vertex AI
aip.init(project='your-project', location='us-central1')

job = aip.PipelineJob(
    display_name='ml-training-pipeline-run',
    template_path='ml_pipeline.json',
    parameter_values={
        'input_data_uri': 'gs://your-bucket/training-data.csv',
        'epochs': 20,
        'batch_size': 64,
        'accuracy_threshold': 0.92
    },
    enable_caching=True,
)

job.submit()

print(f"Pipeline job submitted: {job.resource_name}")
```

## Google Kubernetes Engine (GKE) {#gke}

GKE is Google's managed Kubernetes service, offering deep integration with GCP services and advanced features like Autopilot mode.

### GKE for ML Workloads

**GKE Cluster Configuration**:

```yaml
# GKE cluster for ML workloads
apiVersion: container.cnrm.cloud.google.com/v1beta1
kind: ContainerCluster
metadata:
  name: ml-platform-cluster
  namespace: gcp-infrastructure
spec:
  location: us-central1
  
  # Use Autopilot for fully managed Kubernetes
  # Autopilot manages nodes, scaling, and security
  autopilot:
    enabled: true
  
  # Or use Standard mode for more control
  # autopilot:
  #   enabled: false
  
  # Release channel for automatic updates
  releaseChannel:
    channel: REGULAR  # RAPID, REGULAR, or STABLE
  
  # Workload Identity for secure GCP service access
  workloadIdentityConfig:
    workloadPool: YOUR_PROJECT.svc.id.goog
  
  # Enable addons
  addonsConfig:
    gcePersistentDiskCsiDriverConfig:
      enabled: true
    gcpFilestoreCsiDriverConfig:
      enabled: true
    horizontalPodAutoscaling:
      disabled: false
    httpLoadBalancing:
      disabled: false
    networkPolicyConfig:
      disabled: false
  
  # Enable GKE monitoring and logging
  loggingConfig:
    enableComponents:
      - SYSTEM_COMPONENTS
      - WORKLOADS
  monitoringConfig:
    enableComponents:
      - SYSTEM_COMPONENTS
      - WORKLOADS
    managedPrometheus:
      enabled: true
  
  # Network configuration
  ipAllocationPolicy:
    clusterIpv4CidrBlock: 10.0.0.0/14
    servicesIpv4CidrBlock: 10.4.0.0/20
  networkConfig:
    network: projects/YOUR_PROJECT/global/networks/ml-platform
    subnetwork: projects/YOUR_PROJECT/regions/us-central1/subnetworks/ml-platform-subnet
  
  # Enable binary authorization for security
  binaryAuthorization:
    evaluationMode: PROJECT_SINGLETON_POLICY_ENFORCE
  
  # Node pool configuration (if not using Autopilot)
  nodePools:
    - name: gpu-training-pool
      initialNodeCount: 0
      autoscaling:
        minNodeCount: 0
        maxNodeCount: 20
        locationPolicy: BALANCED
      config:
        machineType: n1-standard-16
        diskType: pd-ssd
        diskSizeGb: 500
        guestAccelerator:
          - type: nvidia-tesla-v100
            count: 4
        oauthScopes:
          - https://www.googleapis.com/auth/cloud-platform
        metadata:
          disable-legacy-endpoints: "true"
        workloadMetadataConfig:
          mode: GKE_METADATA
        shieldedInstanceConfig:
          enableSecureBoot: true
          enableIntegrityMonitoring: true
        taints:
          - key: nvidia.com/gpu
            value: "true"
            effect: NO_SCHEDULE
        labels:
          workload-type: training
          gpu-type: v100
      management:
        autoRepair: true
        autoUpgrade: true
    
    - name: tpu-training-pool
      initialNodeCount: 0
      autoscaling:
        minNodeCount: 0
        maxNodeCount: 10
      config:
        machineType: ct4p-hightpu-4t  # Cloud TPU v4
        oauthScopes:
          - https://www.googleapis.com/auth/cloud-platform
        taints:
          - key: cloud.google.com/gke-tpu
            value: "true"
            effect: NO_SCHEDULE
        labels:
          workload-type: training
          accelerator-type: tpu
```

### GKE Autopilot for ML

**Autopilot Benefits for ML**:
- Fully managed nodes (Google handles scaling, updates, security)
- Pay-per-pod pricing (more cost-effective for variable workloads)
- Automatic resource optimization
- Built-in best practices

**Autopilot ML Deployment**:

```yaml
# ML training job on GKE Autopilot
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-training-autopilot
  namespace: ml-platform
spec:
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      # Autopilot automatically provisions appropriate nodes
      # Based on resource requests
      
      # Workload Identity for GCS access
      serviceAccountName: ml-training-sa
      
      containers:
      - name: trainer
        image: gcr.io/your-project/ml-trainer:latest
        
        # Resource requests determine node size
        resources:
          requests:
            nvidia.com/gpu: "4"      # 4 GPUs
            memory: "64Gi"
            cpu: "32"
            ephemeral-storage: "100Gi"
          limits:
            nvidia.com/gpu: "4"
            memory: "64Gi"
            cpu: "32"
            ephemeral-storage: "100Gi"
        
        env:
        - name: TRAINING_DATA
          value: "gs://your-bucket/training-data"
        - name: MODEL_OUTPUT
          value: "gs://your-bucket/models"
        
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
      
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: "16Gi"
      
      restartPolicy: OnFailure
  backoffLimit: 3
```

### TPU Pods on GKE

```yaml
# Train on TPU v4 pods in GKE
apiVersion: batch/v1
kind: Job
metadata:
  name: tpu-training-job
  namespace: ml-platform
spec:
  template:
    spec:
      # Toleration for TPU nodes
      tolerations:
      - key: cloud.google.com/gke-tpu
        operator: Equal
        value: "true"
        effect: NoSchedule
      
      # Node selector for TPU nodes
      nodeSelector:
        cloud.google.com/gke-tpu-topology: 2x2x1  # TPU v4 pod slice
        cloud.google.com/gke-tpu-accelerator: tpu-v4-podslice
      
      containers:
      - name: tpu-trainer
        image: gcr.io/your-project/tpu-trainer:latest
        
        # TPU resource request
        resources:
          requests:
            google.com/tpu: "4"  # 4-chip TPU pod
          limits:
            google.com/tpu: "4"
        
        env:
        - name: TPU_NAME
          value: "local"
        - name: BATCH_SIZE
          value: "2048"  # Large batch for TPU efficiency
        
        command:
        - python
        - train_tpu.py
        - --tpu_name=local
        - --model_dir=gs://your-bucket/tpu-model
      
      restartPolicy: OnFailure
```

## Cloud TPU Infrastructure {#cloud-tpu}

Cloud TPUs are Google's custom-designed machine learning accelerators, optimized for large-scale matrix operations.

### TPU Generations and Use Cases

**TPU Evolution**:

| Generation | Year | Performance | Use Case | Availability |
|------------|------|-------------|----------|--------------|
| TPU v2 | 2017 | 180 TFLOPS | Training (legacy) | Wide |
| TPU v3 | 2018 | 420 TFLOPS | Training | Wide |
| TPU v4 | 2021 | 275 TFLOPS (BF16) | Training (current) | Good |
| TPU v5e | 2023 | Efficient training | Cost-effective training | Limited |
| TPU v5p | 2023 | 459 TFLOPS | Large model training | Very Limited |

**TPU Pod Configurations**:

```python
# TPU pod configurations
tpu_configurations = {
    'v4-8': {
        'chips': 4,
        'memory_gb': 32,
        'topology': '2x2x1',
        'use_case': 'Small models, experimentation',
        'price_per_hour': 4.00
    },
    'v4-32': {
        'chips': 16,
        'memory_gb': 128,
        'topology': '4x4x1',
        'use_case': 'Medium models (BERT, GPT-2)',
        'price_per_hour': 16.00
    },
    'v4-128': {
        'chips': 64,
        'memory_gb': 512,
        'topology': '8x8x1',
        'use_case': 'Large models (GPT-3 class)',
        'price_per_hour': 64.00
    },
    'v4-1024': {
        'chips': 512,
        'memory_gb': 4096,
        'topology': '16x16x2',
        'use_case': 'Very large models (PaLM)',
        'price_per_hour': 512.00
    }
}
```

### TPU vs GPU Decision Matrix

```python
# When to use TPU vs GPU
def recommend_accelerator(model_type, model_size_params, framework, batch_size):
    """
    Recommend TPU or GPU for ML workload
    
    Args:
        model_type: 'transformer', 'cnn', 'rnn', 'other'
        model_size_params: Number of parameters in billions
        framework: 'tensorflow', 'pytorch', 'jax'
        batch_size: Training batch size
    
    Returns:
        Recommendation with reasoning
    
    TODO: Add cost considerations
    TODO: Consider training duration
    """
    
    # TPU advantages
    if model_type == 'transformer' and model_size_params > 1:
        if framework in ['tensorflow', 'jax']:
            if batch_size >= 512:
                return {
                    'recommendation': 'TPU v4',
                    'reasoning': 'Large transformer with large batch size, excellent TPU fit',
                    'alternative': 'A100 GPU for PyTorch'
                }
    
    # GPU advantages
    if framework == 'pytorch' and model_type in ['cnn', 'rnn']:
        return {
            'recommendation': 'A100 GPU',
            'reasoning': 'PyTorch with CNN/RNN works better on GPU',
            'alternative': 'TPU if willing to port to JAX'
        }
    
    # Default recommendation
    if model_size_params < 1:
        return {
            'recommendation': 'V100 or T4 GPU',
            'reasoning': 'Smaller model, GPU more cost-effective',
            'alternative': 'TPU v2 for budget training'
        }
    else:
        return {
            'recommendation': 'TPU v4 or A100 GPU',
            'reasoning': 'Large model, both viable, choose based on framework',
            'alternative': 'Consider both and benchmark'
        }

# Examples
print(recommend_accelerator('transformer', 10, 'jax', 1024))
# -> TPU v4 recommended

print(recommend_accelerator('cnn', 0.5, 'pytorch', 64))
# -> GPU recommended
```

## BigQuery ML {#bigquery-ml}

BigQuery ML enables SQL users to create and execute ML models directly in BigQuery using SQL queries.

### BigQuery ML Capabilities

```sql
-- Create ML model in BigQuery
CREATE OR REPLACE MODEL `your_project.ml_models.customer_churn`
OPTIONS(
  model_type='LOGISTIC_REG',
  input_label_cols=['churned'],
  auto_class_weights=TRUE,
  enable_global_explain=TRUE,
  max_iterations=50,
  learn_rate=0.1,
  l1_reg=0.1,
  l2_reg=0.1
) AS
SELECT
  customer_id,
  tenure_months,
  monthly_charges,
  total_charges,
  contract_type,
  payment_method,
  internet_service,
  churned
FROM
  `your_project.customer_data.features`
WHERE
  _PARTITIONDATE BETWEEN '2024-01-01' AND '2024-12-31';

-- Evaluate model
SELECT
  *
FROM
  ML.EVALUATE(MODEL `your_project.ml_models.customer_churn`,
    (
      SELECT * FROM `your_project.customer_data.test_set`
    ));

-- Make predictions
SELECT
  customer_id,
  predicted_churned,
  predicted_churned_probs[OFFSET(0)].prob AS churn_probability
FROM
  ML.PREDICT(MODEL `your_project.ml_models.customer_churn`,
    (
      SELECT * FROM `your_project.customer_data.current_customers`
    ))
ORDER BY churn_probability DESC
LIMIT 100;

-- Export model for serving
EXPORT MODEL `your_project.ml_models.customer_churn`
OPTIONS(URI='gs://your-bucket/bqml-models/customer-churn');
```

**Advanced BigQuery ML**:

```sql
-- Deep Neural Network in BigQuery
CREATE OR REPLACE MODEL `your_project.ml_models.dnn_classifier`
OPTIONS(
  model_type='DNN_CLASSIFIER',
  hidden_units=[128, 64, 32],  -- Hidden layer sizes
  activation_fn='RELU',
  dropout=0.2,
  batch_size=1000,
  max_iterations=100,
  early_stop=TRUE,
  min_rel_progress=0.001,
  learn_rate_strategy='LINE_SEARCH',
  optimizer='ADAM'
) AS
SELECT * FROM `your_project.dataset.training_data`;

-- AutoML model (automated feature engineering and hyperparameter tuning)
CREATE OR REPLACE MODEL `your_project.ml_models.automl_classifier`
OPTIONS(
  model_type='AUTOML_CLASSIFIER',
  budget_hours=1.0,  -- Training time budget
  optimization_objective='MAXIMIZE_AU_PRC'
) AS
SELECT * FROM `your_project.dataset.training_data`;

-- Time series forecasting
CREATE OR REPLACE MODEL `your_project.ml_models.sales_forecast`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='date',
  time_series_data_col='sales',
  time_series_id_col='store_id',
  holiday_region='US',
  auto_arima=TRUE,
  data_frequency='DAILY',
  include_drift=TRUE
) AS
SELECT
  date,
  store_id,
  sales
FROM
  `your_project.sales_data.daily_sales`
WHERE
  date BETWEEN '2022-01-01' AND '2024-12-31';

-- Generate forecast
SELECT
  *
FROM
  ML.FORECAST(MODEL `your_project.ml_models.sales_forecast`,
              STRUCT(30 AS horizon, 0.95 AS confidence_level));
```

### BigQuery ML + Vertex AI Integration

```python
# Export BigQuery ML model to Vertex AI
from google.cloud import bigquery
from google.cloud import aiplatform as aip

# Initialize clients
bq_client = bigquery.Client(project='your-project')
aip.init(project='your-project', location='us-central1')

# Export model from BigQuery
query = """
  EXPORT MODEL `your_project.ml_models.customer_churn`
  OPTIONS(URI='gs://your-bucket/bqml-export/customer-churn')
"""
bq_client.query(query).result()

# Upload to Vertex AI Model Registry
model = aip.Model.upload(
    display_name='customer-churn-bqml',
    artifact_uri='gs://your-bucket/bqml-export/customer-churn',
    serving_container_image_uri='gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-13:latest',
    description='Customer churn model trained in BigQuery ML',
)

# Deploy to Vertex AI endpoint
endpoint = model.deploy(
    machine_type='n1-standard-4',
    min_replica_count=1,
    max_replica_count=5,
)

print(f"Model deployed to endpoint: {endpoint.resource_name}")

# TODO: Set up online predictions from Vertex AI endpoint
# TODO: Implement batch predictions using BigQuery ML directly
```

## Cost Optimization on GCP {#cost-optimization}

### Preemptible VMs and Spot VMs

```python
# Using preemptible/spot VMs for ML training
from google.cloud import aiplatform as aip

# Create training job with spot VMs
job = aip.CustomContainerTrainingJob(
    display_name='spot-training-job',
    container_uri='gcr.io/your-project/ml-trainer:latest',
)

model = job.run(
    replica_count=4,
    machine_type='n1-highmem-8',
    accelerator_type='NVIDIA_TESLA_V100',
    accelerator_count=2,
    
    # Enable spot VMs (preemptible) for up to 91% savings
    reduction_server_replica_count=0,
    reduction_server_machine_type=None,
    
    # Spot VMs are preemptible - implement checkpointing!
    base_output_dir='gs://your-bucket/checkpoints',
    
    # TODO: Implement automatic restart on preemption
    # TODO: Save checkpoints frequently
)

# Calculate potential savings
on_demand_price = 2.48  # n1-highmem-8 with 2x V100
spot_price = 0.74       # Spot pricing (70% discount)
training_hours = 24

on_demand_cost = on_demand_price * training_hours * 4  # 4 replicas
spot_cost = spot_price * training_hours * 4

print(f"On-demand cost: ${on_demand_cost:.2f}")
print(f"Spot cost: ${spot_cost:.2f}")
print(f"Savings: ${on_demand_cost - spot_cost:.2f} ({((on_demand_cost - spot_cost) / on_demand_cost * 100):.1f}%)")
```

### Committed Use Discounts

```python
# Calculate GCP committed use discount savings
class GCPCommittedUseCalculator:
    """
    Calculate savings from committed use discounts
    
    TODO: Integrate with GCP Billing API
    TODO: Add recommendations based on usage patterns
    """
    
    def __init__(self):
        self.discount_rates = {
            '1-year': {
                'compute': 0.25,  # 25% discount
                'memory': 0.25,
                'gpu': 0.30,      # 30% discount for GPUs
            },
            '3-year': {
                'compute': 0.52,  # 52% discount
                'memory': 0.52,
                'gpu': 0.55,      # 55% discount for GPUs
            }
        }
    
    def calculate_savings(
        self,
        monthly_compute_cost: float,
        monthly_gpu_cost: float,
        commitment_term: str = '1-year'
    ) -> dict:
        """
        Calculate savings from committed use
        
        Args:
            monthly_compute_cost: Monthly compute spend
            monthly_gpu_cost: Monthly GPU spend
            commitment_term: '1-year' or '3-year'
        
        Returns:
            Savings breakdown
        """
        rates = self.discount_rates[commitment_term]
        
        # Calculate annual costs
        annual_compute_on_demand = monthly_compute_cost * 12
        annual_gpu_on_demand = monthly_gpu_cost * 12
        
        # Calculate with discounts
        annual_compute_committed = annual_compute_on_demand * (1 - rates['compute'])
        annual_gpu_committed = annual_gpu_on_demand * (1 - rates['gpu'])
        
        # Total savings
        compute_savings = annual_compute_on_demand - annual_compute_committed
        gpu_savings = annual_gpu_on_demand - annual_gpu_committed
        total_savings = compute_savings + gpu_savings
        
        return {
            'commitment_term': commitment_term,
            'annual_compute_savings': compute_savings,
            'annual_gpu_savings': gpu_savings,
            'total_annual_savings': total_savings,
            'monthly_savings': total_savings / 12,
            'compute_discount_rate': rates['compute'] * 100,
            'gpu_discount_rate': rates['gpu'] * 100,
        }

# Example
calculator = GCPCommittedUseCalculator()

savings = calculator.calculate_savings(
    monthly_compute_cost=10000,
    monthly_gpu_cost=15000,
    commitment_term='3-year'
)

print(f"Annual savings: ${savings['total_annual_savings']:,.2f}")
print(f"Monthly savings: ${savings['monthly_savings']:,.2f}")
```

### Storage Optimization

```python
# GCS storage lifecycle management for ML
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('ml-artifacts-bucket')

# Configure lifecycle rules
lifecycle_rules = [
    {
        'action': {'type': 'SetStorageClass', 'storageClass': 'NEARLINE'},
        'condition': {
            'age': 30,  # Move to Nearline after 30 days
            'matchesPrefix': ['training-data/', 'logs/']
        }
    },
    {
        'action': {'type': 'SetStorageClass', 'storageClass': 'COLDLINE'},
        'condition': {
            'age': 90,  # Move to Coldline after 90 days
            'matchesPrefix': ['training-data/', 'logs/']
        }
    },
    {
        'action': {'type': 'SetStorageClass', 'storageClass': 'ARCHIVE'},
        'condition': {
            'age': 365,  # Archive after 1 year
            'matchesPrefix': ['training-data/']
        }
    },
    {
        'action': {'type': 'Delete'},
        'condition': {
            'age': 90,  # Delete temporary files after 90 days
            'matchesPrefix': ['temp/', 'cache/']
        }
    },
    {
        'action': {'type': 'Delete'},
        'condition': {
            'numNewerVersions': 3,  # Keep only 3 latest versions
            'matchesPrefix': ['models/']
        }
    }
]

bucket.lifecycle_rules = lifecycle_rules
bucket.patch()

print("Lifecycle rules configured for cost optimization")

# Storage class pricing (2025)
storage_pricing = {
    'STANDARD': 0.020,    # per GB/month
    'NEARLINE': 0.010,    # per GB/month (30-day minimum)
    'COLDLINE': 0.004,    # per GB/month (90-day minimum)
    'ARCHIVE': 0.0012,    # per GB/month (365-day minimum)
}

# Calculate savings
training_data_gb = 10000  # 10 TB
standard_cost_annual = training_data_gb * storage_pricing['STANDARD'] * 12
archive_cost_annual = training_data_gb * storage_pricing['ARCHIVE'] * 12

savings = standard_cost_annual - archive_cost_annual
print(f"Annual savings by archiving old training data: ${savings:,.2f}")
```

## Real-World Architectures {#real-world}

### End-to-End ML Platform on GCP

```
┌──────────────────────────────────────────────────────────────────┐
│                      Data Ingestion Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Pub/Sub   │  │Dataflow  │  │Cloud SQL │  │   GCS    │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
└───────┼─────────────┼─────────────┼─────────────┼────────────────┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴────────────────┐
│                   Data Processing Layer                           │
│  ┌─────────────────────────────────────────────────────┐         │
│  │        BigQuery + Dataproc (Spark/Beam)             │         │
│  │      (Data warehousing + ETL processing)            │         │
│  └───────────────────────┬─────────────────────────────┘         │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────────────┐
│                   Training Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Vertex AI   │  │   GKE +     │  │   Cloud     │            │
│  │  Training   │  │ Kubeflow    │  │    TPU      │            │
│  │  (Managed)  │  │(Custom ML)  │  │  (Large     │            │
│  └──────┬──────┘  └──────┬──────┘  │   Models)   │            │
└─────────┼────────────────┼─────────┴──────┬──────────────────┘
          │                │                │
┌─────────┴────────────────┴────────────────┴────────────────────┐
│                    Model Registry                                │
│  ┌──────────────────────────────────────────────────┐           │
│  │    Vertex AI Model Registry + Artifact Registry  │           │
│  └─────────────────────┬────────────────────────────┘           │
└─────────────────────────┼──────────────────────────────────────┘
                          │
┌─────────────────────────┼──────────────────────────────────────┐
│                   Inference Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Vertex AI   │  │   GKE +     │  │Cloud Run +  │            │
│  │ Prediction  │  │   KServe    │  │ Functions   │            │
│  │(Real-time)  │  │(K8s-native) │  │(Serverless) │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
└─────────┼────────────────┼────────────────┼───────────────────┘
          │                │                │
┌─────────┴────────────────┴────────────────┴───────────────────┐
│                  API Gateway Layer                              │
│  ┌──────────────────────────────────────────────────┐          │
│  │   Cloud Endpoints + Cloud Load Balancing + CDN   │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘

Cross-Cutting Services:
├── Monitoring: Cloud Monitoring + Managed Prometheus
├── Logging: Cloud Logging (formerly Stackdriver)
├── Security: IAM + VPC + Binary Authorization + KMS
├── Cost Management: Cloud Billing + Recommender API
└── CI/CD: Cloud Build + Artifact Registry + Cloud Deploy
```

## Summary {#summary}

GCP provides powerful ML infrastructure with unique advantages:

**Key Strengths**:
1. **TPUs**: Unmatched for large transformer model training
2. **Vertex AI**: Comprehensive managed ML platform
3. **BigQuery ML**: SQL-based ML for data teams
4. **GKE**: Advanced Kubernetes with Autopilot
5. **Integration**: Seamless integration across services

**When to Choose GCP**:
- Training large transformer models (use TPUs)
- Teams comfortable with TensorFlow/JAX
- Need for BigQuery + ML integration
- Want managed Kubernetes (Autopilot)
- Leveraging Google Research advances

**Cost Optimization Summary**:
- Use Spot VMs: Up to 91% savings
- Committed use discounts: Up to 55% savings
- Storage lifecycle: Up to 83% savings
- BigQuery slots: Flat-rate pricing for large analytics

**Next Steps**:
1. Set up GCP project with appropriate quotas
2. Deploy pilot ML workloads on Vertex AI
3. Evaluate TPUs for transformer training
4. Implement cost monitoring and optimization
5. Set up CI/CD for ML workflows

---

**Estimated Reading Time**: 120-150 minutes
**Hands-On Labs**: 10-12 hours
**Prerequisites**: GCP account, GCP SDK installed

