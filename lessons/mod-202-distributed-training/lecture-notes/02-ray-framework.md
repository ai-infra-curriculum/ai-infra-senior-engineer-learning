# Lecture 02: Ray Framework for Distributed Training

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and deploy Ray clusters on Kubernetes for production ML workloads
- Implement distributed training pipelines using Ray Train for PyTorch and TensorFlow models
- Configure Ray Tune for scalable hyperparameter optimization across hundreds of trials
- Integrate Ray Data for distributed data preprocessing and loading pipelines
- Implement fault tolerance and autoscaling for long-running Ray training jobs
- Optimize Ray cluster performance through resource allocation and task scheduling
- Deploy production Ray applications with monitoring, logging, and observability
- Evaluate trade-offs between Ray and alternative distributed training frameworks

## Table of Contents

1. [Introduction to Ray](#introduction)
2. [Ray Architecture](#ray-architecture)
3. [Ray Core Concepts](#core-concepts)
4. [Ray Train: Distributed Training](#ray-train)
5. [Ray Tune: Hyperparameter Optimization](#ray-tune)
6. [Ray Data: Distributed Data Processing](#ray-data)
7. [Ray on Kubernetes](#ray-kubernetes)
8. [Production Deployment Patterns](#production-patterns)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting and Debugging](#troubleshooting)

## Introduction to Ray

Ray is a unified framework for scaling Python and machine learning workloads. Created at UC Berkeley's RISELab and now maintained by Anyscale, Ray provides:

- **Simple API**: Scale Python applications with minimal code changes
- **Distributed Training**: Built-in support for PyTorch, TensorFlow, and more
- **Hyperparameter Tuning**: Scalable optimization with Ray Tune
- **Production-Ready**: Battle-tested at companies like OpenAI, Uber, Amazon

### Why Ray for ML Infrastructure?

```python
# Without Ray: Complex distributed training setup
# - Manual cluster management
# - Custom communication code
# - Complex fault tolerance
# - Dozens of lines of boilerplate

# With Ray: Simple and scalable
import ray
from ray import train
from ray.train.torch import TorchTrainer

# Define training function
def train_func(config):
    model = create_model()
    train_model(model, config)

# Scale to any number of workers
trainer = TorchTrainer(
    train_func,
    scaling_config=train.ScalingConfig(num_workers=32),
)
result = trainer.fit()
```

### Ray vs Other Frameworks

| Feature | Ray | Spark | Dask | Horovod |
|---------|-----|-------|------|---------|
| ML Training | ✓ Excellent | ✗ Limited | ~ Basic | ✓ Excellent |
| Hyperparameter Tuning | ✓ Ray Tune | ✗ None | ✗ None | ✗ None |
| General Computing | ✓ Flexible | ✓ Batch | ✓ Arrays | ✗ Training only |
| Learning Curve | Easy | Medium | Medium | Easy |
| Fault Tolerance | ✓ Built-in | ✓ Built-in | ~ Limited | ✗ Manual |
| GPU Support | ✓ Excellent | ~ Limited | ~ Limited | ✓ Excellent |

## Ray Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Ray Cluster Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    Head Node                           │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │            Global Control Store (GCS)            │  │    │
│  │  │  - Cluster metadata                              │  │    │
│  │  │  - Object directory                              │  │    │
│  │  │  - Actor registry                                │  │    │
│  │  │  - Placement group info                          │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────┐  ┌──────────────┐                    │    │
│  │  │  Raylet      │  │  Dashboard   │                    │    │
│  │  │  (Scheduler)  │  │  (Port 8265) │                    │    │
│  │  └──────────────┘  └──────────────┘                    │    │
│  │  ┌──────────────┐  ┌──────────────┐                    │    │
│  │  │ Object Store │  │ Worker Pool  │                    │    │
│  │  │  (Plasma)    │  │              │                    │    │
│  │  └──────────────┘  └──────────────┘                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                            │                                    │
│                            │ (Network)                          │
│                            │                                    │
│  ┌─────────────────┬──────┴────────┬─────────────────┐         │
│  │                 │               │                 │         │
│  ▼                 ▼               ▼                 ▼         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Worker   │  │ Worker   │  │ Worker   │  │ Worker   │       │
│  │ Node 1   │  │ Node 2   │  │ Node 3   │  │ Node 4   │       │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤       │
│  │ Raylet   │  │ Raylet   │  │ Raylet   │  │ Raylet   │       │
│  │ Object   │  │ Object   │  │ Object   │  │ Object   │       │
│  │ Store    │  │ Store    │  │ Store    │  │ Store    │       │
│  │ Workers  │  │ Workers  │  │ Workers  │  │ Workers  │       │
│  │ [GPUs]   │  │ [GPUs]   │  │ [GPUs]   │  │ [GPUs]   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architecture Concepts

**1. Raylet (Ray + Tablet)**
- Local scheduler on each node
- Manages resources (CPU, GPU, memory)
- Handles task execution
- Communicates with GCS

**2. Global Control Store (GCS)**
- Centralized metadata store
- Tracks cluster state
- Manages object locations
- Coordinates distributed operations

**3. Object Store (Plasma)**
- Shared memory object store
- Zero-copy data sharing
- Efficient inter-process communication
- Automatic memory management

**4. Worker Processes**
- Execute tasks and actors
- Isolated Python processes
- Can request specific resources (GPU, CPU)

## Ray Core Concepts

### Tasks: Stateless Functions

```python
import ray
import time

# Initialize Ray
ray.init()

# Regular Python function
def regular_sum(values):
    return sum(values)

# Ray remote function (task)
@ray.remote
def ray_sum(values):
    """
    Ray task - stateless, can run anywhere in cluster
    Returns an ObjectRef (future) immediately
    """
    return sum(values)

# Execute tasks
start = time.time()

# Sequential execution
results = []
for i in range(4):
    result = regular_sum(range(1000000))
    results.append(result)

sequential_time = time.time() - start
print(f"Sequential: {sequential_time:.2f}s")

# Parallel execution with Ray
start = time.time()

# Submit tasks (returns immediately)
futures = []
for i in range(4):
    future = ray_sum.remote(range(1000000))
    futures.append(future)

# Get results (blocks until complete)
results = ray.get(futures)

parallel_time = time.time() - start
print(f"Parallel: {parallel_time:.2f}s")
print(f"Speedup: {sequential_time/parallel_time:.2f}x")

# Advanced: Specify resources for tasks
@ray.remote(num_cpus=2, num_gpus=1, memory=1000*1024*1024)  # 1GB
def gpu_task(data):
    """Task that requires specific resources"""
    # TODO: Implement GPU-accelerated processing
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tensor = torch.tensor(data).to(device)
    return tensor.sum().item()

# Submit task - Ray will schedule on node with available GPU
result = ray_sum.remote([1, 2, 3, 4])
value = ray.get(result)
```

### Actors: Stateful Classes

```python
@ray.remote
class Counter:
    """
    Ray Actor - stateful, runs on specific worker
    Maintains state across method calls
    """

    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

    def get_count(self):
        return self.count

    def reset(self):
        self.count = 0

# Create actor instance (runs on remote worker)
counter = Counter.remote()

# Call methods (returns ObjectRef)
ray.get(counter.increment.remote())  # Returns 1
ray.get(counter.increment.remote())  # Returns 2
current = ray.get(counter.get_count.remote())  # Returns 2

print(f"Current count: {current}")

# Multiple actors can run in parallel
@ray.remote
class ParameterServer:
    """
    Example: Distributed parameter server for ML training
    """

    def __init__(self, learning_rate=0.01):
        self.weights = {}
        self.learning_rate = learning_rate

    def get_weights(self, keys):
        """Get current weights"""
        return {k: self.weights.get(k) for k in keys}

    def update_weights(self, gradients):
        """Apply gradient update"""
        # TODO: Implement weight update logic
        for key, gradient in gradients.items():
            if key not in self.weights:
                self.weights[key] = -self.learning_rate * gradient
            else:
                self.weights[key] -= self.learning_rate * gradient
        return True

    def save_checkpoint(self, path):
        """Save weights to file"""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.weights, f)
        return True

# Create parameter server actor
ps = ParameterServer.remote(learning_rate=0.01)

# Multiple workers can interact with same parameter server
@ray.remote
def worker_train(worker_id, param_server, data):
    """Worker training function"""
    # Get weights from parameter server
    weights = ray.get(param_server.get_weights.remote(['layer1', 'layer2']))

    # Compute gradients (simplified)
    gradients = {'layer1': 0.1, 'layer2': 0.2}

    # Push gradients to parameter server
    ray.get(param_server.update_weights.remote(gradients))

    return f"Worker {worker_id} completed"

# Launch multiple workers
workers = [
    worker_train.remote(i, ps, None)
    for i in range(4)
]

# Wait for all workers
results = ray.get(workers)
print(results)
```

### Object Store and Data Sharing

```python
import numpy as np

# Put large objects in object store
large_array = np.random.rand(1000, 1000)

# Put in object store (returns ObjectRef)
ref = ray.put(large_array)

@ray.remote
def process_array(array_ref):
    """
    Process array from object store
    Zero-copy access to data
    """
    array = ray.get(array_ref)
    return array.sum()

# Multiple tasks can access same data without copying
tasks = [process_array.remote(ref) for _ in range(10)]
results = ray.get(tasks)

# Object store automatic memory management
# Objects are reference-counted and garbage collected

# Advanced: Shared memory between tasks on same node
@ray.remote
def task_with_return_large_value():
    """Ray automatically handles large return values"""
    return np.random.rand(10000, 10000)

# This is efficient - stored in object store
result_ref = task_with_return_large_value.remote()

# Best practice: Use object refs instead of ray.get() repeatedly
# BAD: Fetches data 10 times
for i in range(10):
    data = ray.get(result_ref)  # Copy each time
    process(data)

# GOOD: Pass reference to tasks
@ray.remote
def process_data(data_ref):
    data = ray.get(data_ref)  # Fetch once per task
    return process(data)

tasks = [process_data.remote(result_ref) for _ in range(10)]
```

## Ray Train: Distributed Training

Ray Train provides a unified API for distributed training across frameworks.

### Basic PyTorch Training with Ray Train

```python
from ray import train
from ray.train.torch import TorchTrainer
import torch
import torch.nn as nn
import torch.optim as optim

def train_func(config):
    """
    Training function - runs on each worker
    Ray Train handles all distribution logic
    """
    # Get distributed training context
    rank = train.get_context().get_world_rank()
    world_size = train.get_context().get_world_size()

    print(f"Worker {rank}/{world_size} starting")

    # TODO: Create model (Ray Train wraps with DDP automatically)
    model = nn.Linear(10, 1)
    model = train.torch.prepare_model(model)

    # TODO: Create optimizer
    optimizer = optim.SGD(model.parameters(), lr=config["lr"])

    # TODO: Load data with distributed sampler
    train_dataset = create_dataset()
    train_loader = train.torch.prepare_data_loader(
        torch.utils.data.DataLoader(
            train_dataset,
            batch_size=config["batch_size"],
        )
    )

    # Training loop
    for epoch in range(config["num_epochs"]):
        model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.mse_loss(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        # Report metrics (Ray Train aggregates across workers)
        train.report({
            "epoch": epoch,
            "loss": total_loss / len(train_loader),
        })

    return {"final_loss": total_loss / len(train_loader)}

# Create trainer with scaling config
trainer = TorchTrainer(
    train_func,
    train_loop_config={
        "lr": 0.01,
        "batch_size": 32,
        "num_epochs": 10,
    },
    scaling_config=train.ScalingConfig(
        num_workers=4,           # Number of training workers
        use_gpu=True,            # Use GPUs if available
        resources_per_worker={   # Resources per worker
            "CPU": 2,
            "GPU": 1,
        },
    ),
)

# Start distributed training
result = trainer.fit()
print(f"Training completed: {result.metrics}")

# Complete example with all features
class AdvancedTorchTrainer:
    """
    Production-ready Ray Train implementation
    """

    def __init__(self, model_config, data_config, training_config):
        self.model_config = model_config
        self.data_config = data_config
        self.training_config = training_config

    def train_func(self, config):
        """Enhanced training function"""
        import torch
        from torch.utils.data import DataLoader, DistributedSampler
        from torch.utils.tensorboard import SummaryWriter

        # Get distributed context
        rank = train.get_context().get_world_rank()
        world_size = train.get_context().get_world_size()

        # Set device
        device = torch.device(f"cuda:{rank % torch.cuda.device_count()}"
                             if torch.cuda.is_available() else "cpu")

        # Create model
        model = self._create_model()
        model = model.to(device)

        # Wrap with DDP (Ray Train handles this)
        model = train.torch.prepare_model(model)

        # Create optimizer and scheduler
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config["lr"],
            weight_decay=config["weight_decay"],
        )

        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config["num_epochs"],
        )

        # Load data
        train_dataset = self._load_dataset("train")
        val_dataset = self._load_dataset("val")

        # Prepare data loaders (Ray Train handles distributed sampling)
        train_loader = train.torch.prepare_data_loader(
            DataLoader(
                train_dataset,
                batch_size=config["batch_size"],
                shuffle=True,
                num_workers=4,
                pin_memory=True,
            )
        )

        val_loader = train.torch.prepare_data_loader(
            DataLoader(
                val_dataset,
                batch_size=config["batch_size"],
                shuffle=False,
                num_workers=4,
                pin_memory=True,
            )
        )

        # Training loop
        for epoch in range(config["num_epochs"]):
            # Train
            train_metrics = self._train_epoch(
                model, train_loader, optimizer, device
            )

            # Validate
            val_metrics = self._validate(model, val_loader, device)

            # Step scheduler
            scheduler.step()

            # Report metrics
            metrics = {
                "epoch": epoch,
                "train_loss": train_metrics["loss"],
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
                "learning_rate": scheduler.get_last_lr()[0],
            }

            # Save checkpoint (Ray Train handles distributed checkpointing)
            with train.checkpoint_context() as checkpoint_dir:
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "scheduler_state_dict": scheduler.state_dict(),
                }, f"{checkpoint_dir}/checkpoint.pt")

            train.report(metrics)

    def _train_epoch(self, model, dataloader, optimizer, device):
        """Train one epoch"""
        model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.cross_entropy(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        return {"loss": total_loss / len(dataloader)}

    def _validate(self, model, dataloader, device):
        """Validate model"""
        model.eval()
        total_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in dataloader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = nn.functional.cross_entropy(output, target)
                total_loss += loss.item()

                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)

        return {
            "loss": total_loss / len(dataloader),
            "accuracy": correct / total,
        }

    def train(self):
        """Start training"""
        trainer = TorchTrainer(
            self.train_func,
            train_loop_config=self.training_config,
            scaling_config=train.ScalingConfig(
                num_workers=self.training_config["num_workers"],
                use_gpu=True,
                resources_per_worker={"CPU": 4, "GPU": 1},
            ),
            run_config=train.RunConfig(
                name="my_training_job",
                storage_path="/tmp/ray_results",
                checkpoint_config=train.CheckpointConfig(
                    num_to_keep=3,
                    checkpoint_score_attribute="val_loss",
                    checkpoint_score_order="min",
                ),
            ),
        )

        result = trainer.fit()
        return result
```

### TensorFlow Training with Ray Train

```python
from ray.train.tensorflow import TensorflowTrainer
import tensorflow as tf

def train_func_tf(config):
    """TensorFlow training function"""
    # Get distributed context
    strategy = train.tensorflow.prepare_strategy()

    with strategy.scope():
        # TODO: Create model within strategy scope
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax'),
        ])

        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy'],
        )

    # TODO: Load and prepare dataset
    dataset = create_tf_dataset()
    dataset = train.tensorflow.prepare_dataset(dataset)

    # Train
    model.fit(
        dataset,
        epochs=config["num_epochs"],
        callbacks=[
            # Ray Train callback for metrics
            train.tensorflow.TensorflowTrainReportCallback(),
        ],
    )

    return model

# Create TensorFlow trainer
tf_trainer = TensorflowTrainer(
    train_func_tf,
    train_loop_config={"num_epochs": 10},
    scaling_config=train.ScalingConfig(num_workers=4, use_gpu=True),
)

result = tf_trainer.fit()
```

## Ray Tune: Hyperparameter Optimization

Ray Tune provides scalable hyperparameter tuning with advanced algorithms.

### Basic Hyperparameter Tuning

```python
from ray import tune
from ray.tune.schedulers import ASHAScheduler
from ray.tune.search.optuna import OptunaSearch

def train_mnist(config):
    """Training function with hyperparameters"""
    model = create_model(
        hidden_size=config["hidden_size"],
        dropout=config["dropout"],
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config["lr"],
    )

    for epoch in range(10):
        train_loss = train_epoch(model, optimizer)
        val_loss = validate(model)

        # Report metrics to Ray Tune
        tune.report(
            epoch=epoch,
            train_loss=train_loss,
            val_loss=val_loss,
        )

# Define search space
search_space = {
    "lr": tune.loguniform(1e-5, 1e-1),
    "hidden_size": tune.choice([64, 128, 256, 512]),
    "dropout": tune.uniform(0.1, 0.5),
}

# Configure scheduler (early stopping)
scheduler = ASHAScheduler(
    max_t=10,                # Maximum epochs
    grace_period=1,          # Minimum epochs before stopping
    reduction_factor=2,      # Half trials each round
)

# Configure search algorithm
search_alg = OptunaSearch()

# Run hyperparameter search
tuner = tune.Tuner(
    train_mnist,
    param_space=search_space,
    tune_config=tune.TuneConfig(
        metric="val_loss",
        mode="min",
        num_samples=50,          # Number of trials
        scheduler=scheduler,
        search_alg=search_alg,
    ),
    run_config=train.RunConfig(
        name="mnist_hpo",
        storage_path="/tmp/ray_results",
    ),
)

results = tuner.fit()

# Get best configuration
best_result = results.get_best_result("val_loss", "min")
print(f"Best config: {best_result.config}")
print(f"Best val_loss: {best_result.metrics['val_loss']}")

# Advanced: Population Based Training (PBT)
from ray.tune.schedulers import PopulationBasedTraining

pbt_scheduler = PopulationBasedTraining(
    time_attr="training_iteration",
    metric="val_loss",
    mode="min",
    perturbation_interval=5,
    hyperparam_mutations={
        "lr": tune.loguniform(1e-5, 1e-1),
        "dropout": [0.1, 0.2, 0.3, 0.4, 0.5],
    },
)

# PBT continuously evolves hyperparameters during training
tuner_pbt = tune.Tuner(
    train_mnist,
    param_space=search_space,
    tune_config=tune.TuneConfig(
        num_samples=20,
        scheduler=pbt_scheduler,
    ),
)

results_pbt = tuner_pbt.fit()
```

### Distributed Hyperparameter Tuning

```python
def distributed_hpo_with_raytrain(config):
    """
    Combine Ray Train and Ray Tune
    Each trial is distributed training job
    """

    def train_func(train_config):
        # This runs distributed across multiple GPUs
        # TODO: Implement distributed training loop
        pass

    # Create trainer for this trial
    trainer = TorchTrainer(
        train_func,
        train_loop_config=config,
        scaling_config=train.ScalingConfig(
            num_workers=4,  # 4 GPUs per trial
            use_gpu=True,
        ),
    )

    result = trainer.fit()

    # Report metrics to Ray Tune
    return result.metrics

# Run distributed HPO
tuner = tune.Tuner(
    distributed_hpo_with_raytrain,
    param_space={
        "lr": tune.loguniform(1e-5, 1e-1),
        "batch_size": tune.choice([32, 64, 128]),
    },
    tune_config=tune.TuneConfig(
        num_samples=10,  # 10 trials
        # Each trial uses 4 GPUs
        # Total: up to 40 GPUs if available
    ),
)

results = tuner.fit()
```

## Ray Data: Distributed Data Processing

```python
import ray

# Create Ray Dataset
ds = ray.data.read_parquet("s3://bucket/data/*.parquet")

# Transform data in parallel
def preprocess(batch):
    """Preprocess batch of data"""
    # TODO: Implement preprocessing
    batch["processed"] = batch["raw"] * 2
    return batch

ds = ds.map_batches(preprocess, batch_size=1000)

# Integration with Ray Train
def train_func(config):
    # Get dataset shard for this worker
    dataset_shard = train.get_dataset_shard("train")

    # Convert to PyTorch DataLoader
    dataloader = dataset_shard.iter_torch_batches(
        batch_size=config["batch_size"],
    )

    # Train with dataloader
    for epoch in range(config["num_epochs"]):
        for batch in dataloader:
            # TODO: Training step
            pass

# Create trainer with Ray Data
trainer = TorchTrainer(
    train_func,
    scaling_config=train.ScalingConfig(num_workers=4),
    datasets={"train": ds},
)

result = trainer.fit()
```

## Ray on Kubernetes

### Deploying Ray Cluster on Kubernetes

```yaml
# ray-cluster.yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: ray-cluster
  namespace: ray-system
spec:
  rayVersion: '2.9.0'

  # Head node configuration
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      num-cpus: '0'  # Don't schedule tasks on head
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.9.0-py310
          ports:
          - containerPort: 6379  # Redis
          - containerPort: 8265  # Dashboard
          - containerPort: 10001 # Client server
          resources:
            requests:
              cpu: "2"
              memory: "8Gi"
            limits:
              cpu: "2"
              memory: "8Gi"

  # Worker node configuration
  workerGroupSpecs:
  - replicas: 4
    minReplicas: 1
    maxReplicas: 10
    groupName: gpu-workers
    rayStartParams:
      num-gpus: "1"
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.9.0-py310-gpu
          resources:
            requests:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
            limits:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
```

### Autoscaling Ray Cluster

```python
# Submit job to Ray cluster on Kubernetes
from ray.job_submission import JobSubmissionClient

client = JobSubmissionClient("http://ray-cluster-head:8265")

# Submit training job
job_id = client.submit_job(
    entrypoint="python train.py",
    runtime_env={
        "pip": ["torch", "transformers"],
        "working_dir": "./src",
    },
)

# Monitor job
status = client.get_job_status(job_id)
logs = client.get_job_logs(job_id)
```

## Performance Optimization

### Resource Management

```python
# Efficient resource allocation
@ray.remote(num_cpus=1, num_gpus=0.25)  # Share GPU across 4 tasks
def light_gpu_task():
    pass

# Memory management
@ray.remote(memory=2*1024*1024*1024)  # 2GB memory
def memory_intensive_task():
    pass

# Custom resources
@ray.init(resources={"TPU": 8})

@ray.remote(resources={"TPU": 1})
def tpu_task():
    pass
```

### Monitoring and Debugging

```python
# Enable detailed logging
import ray
ray.init(logging_level=logging.DEBUG)

# Ray Dashboard: http://localhost:8265
# - View cluster status
# - Monitor resource utilization
# - Debug failed tasks
# - Profile performance

# Programmatic monitoring
import ray.util.state as state

# Get cluster information
nodes = state.list_nodes()
actors = state.list_actors()
tasks = state.list_tasks()

# Monitor resource usage
for node in nodes:
    print(f"Node {node['node_id']}: "
          f"CPU: {node['cpu_usage']}, "
          f"GPU: {node['gpu_usage']}, "
          f"Memory: {node['memory_usage']}")
```

## Troubleshooting

Common issues and solutions:

### Out of Memory Errors

```python
# Problem: Large objects causing OOM
# Solution: Stream data instead of loading all at once

@ray.remote
def process_large_dataset():
    # BAD: Load entire dataset
    data = load_entire_dataset()  # OOM!

    # GOOD: Stream data in chunks
    for chunk in stream_dataset_chunks():
        process(chunk)
```

### Slow Task Scheduling

```python
# Problem: Too many small tasks
# Solution: Batch operations

# BAD: Submit 1 million tiny tasks
results = [tiny_task.remote(i) for i in range(1000000)]

# GOOD: Batch into larger tasks
@ray.remote
def batch_process(batch):
    return [tiny_operation(i) for i in batch]

batch_size = 1000
batches = [range(i, i+batch_size)
           for i in range(0, 1000000, batch_size)]
results = [batch_process.remote(b) for b in batches]
```

## Summary

Ray provides a powerful, unified framework for distributed ML:

- **Simple API**: Minimal code changes to scale
- **Ray Train**: Distributed training across frameworks
- **Ray Tune**: Scalable hyperparameter optimization
- **Ray Data**: Distributed data processing
- **Production-Ready**: Kubernetes integration, monitoring, fault tolerance

**Best Practices:**
1. Use Ray Train for distributed training
2. Combine with Ray Tune for HPO
3. Deploy on Kubernetes for production
4. Monitor with Ray Dashboard
5. Optimize resource allocation

## Further Reading

- [Ray Documentation](https://docs.ray.io/)
- [Ray Train Examples](https://docs.ray.io/en/latest/train/examples.html)
- [Anyscale Blog](https://www.anyscale.com/blog)
- "Ray: A Distributed Framework for Emerging AI Applications" (Moritz et al., 2018)

## Next Steps

Continue to `03-horovod-pytorch-ddp.md` to learn about Horovod and PyTorch DDP for distributed training.
