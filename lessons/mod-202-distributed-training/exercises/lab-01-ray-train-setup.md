# Lab 01: Ray Train Setup and Basic Distributed Training

## Lab Overview

**Duration**: 3-4 hours
**Difficulty**: Intermediate
**Prerequisites**: Python, PyTorch basics, Kubernetes knowledge

In this lab, you'll set up a Ray cluster on Kubernetes and implement basic distributed training with Ray Train. You'll learn to scale training from single GPU to multi-node distributed training.

## Learning Objectives

By the end of this lab, you will be able to:
- Deploy a Ray cluster on Kubernetes
- Configure Ray Train for distributed training
- Scale training across multiple nodes
- Monitor distributed training with Ray Dashboard
- Implement checkpointing with Ray Train
- Benchmark scaling efficiency

## Prerequisites

- Kubernetes cluster with at least 2 nodes
- Each node should have at least 1 GPU
- kubectl configured and working
- Docker installed locally
- Python 3.9+ with PyTorch

## Lab Environment Setup

### Step 1: Install KubeRay Operator

```bash
# Install KubeRay operator
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Create namespace
kubectl create namespace ray-system

# Install operator
helm install kuberay-operator kuberay/kuberay-operator \
  --namespace ray-system \
  --set image.tag=v0.6.0

# Verify installation
kubectl get pods -n ray-system
```

**Expected Output**:
```
NAME                                READY   STATUS    RESTARTS   AGE
kuberay-operator-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### Step 2: Create Ray Cluster

Create a file `ray-cluster.yaml`:

```yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: ray-cluster
  namespace: ray-system
spec:
  rayVersion: '2.9.0'

  # Head node
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      num-cpus: '0'  # Don't schedule tasks on head
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.9.0-py310-gpu
          ports:
          - containerPort: 6379  # Redis
            name: redis
          - containerPort: 8265  # Dashboard
            name: dashboard
          - containerPort: 10001 # Client
            name: client
          resources:
            requests:
              cpu: "2"
              memory: "8Gi"
            limits:
              cpu: "2"
              memory: "8Gi"
          volumeMounts:
          - name: shared-storage
            mountPath: /mnt/shared
        volumes:
        - name: shared-storage
          persistentVolumeClaim:
            claimName: ray-shared-storage

  # Worker nodes
  workerGroupSpecs:
  - replicas: 2
    minReplicas: 1
    maxReplicas: 4
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
          volumeMounts:
          - name: shared-storage
            mountPath: /mnt/shared
        volumes:
        - name: shared-storage
          persistentVolumeClaim:
            claimName: ray-shared-storage
```

Create PVC for shared storage:

```yaml
# ray-storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ray-shared-storage
  namespace: ray-system
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs-client  # Adjust based on your cluster
```

Deploy:

```bash
# Create PVC
kubectl apply -f ray-storage.yaml

# Create Ray cluster
kubectl apply -f ray-cluster.yaml

# Wait for cluster to be ready
kubectl wait --for=condition=ready pod \
  -l ray.io/cluster=ray-cluster \
  -n ray-system \
  --timeout=300s

# Check cluster status
kubectl get rayclusters -n ray-system
kubectl get pods -n ray-system -l ray.io/cluster=ray-cluster
```

### Step 3: Access Ray Dashboard

```bash
# Port forward to access dashboard
kubectl port-forward -n ray-system \
  svc/ray-cluster-head-svc 8265:8265

# Open browser to http://localhost:8265
```

**TODO**: Take a screenshot of Ray Dashboard showing your cluster

## Exercise 1: Single-Node Training Baseline

First, implement single-GPU training to establish a baseline.

### Task 1.1: Create Training Script

Create `train_baseline.py`:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time

# TODO: Define a simple CNN model
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # TODO: Implement CNN architecture
        # - Conv2d layers
        # - BatchNorm
        # - ReLU activations
        # - MaxPool
        # - Fully connected layers
        pass

    def forward(self, x):
        # TODO: Implement forward pass
        pass

def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train one epoch"""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    start_time = time.time()

    for batch_idx, (data, target) in enumerate(dataloader):
        # TODO: Implement training step
        # 1. Move data to device
        # 2. Forward pass
        # 3. Compute loss
        # 4. Backward pass
        # 5. Optimizer step
        pass

        if batch_idx % 10 == 0:
            print(f'Batch {batch_idx}/{len(dataloader)}, '
                  f'Loss: {loss.item():.4f}')

    elapsed = time.time() - start_time

    return {
        'loss': total_loss / len(dataloader),
        'accuracy': correct / total,
        'time': elapsed,
        'throughput': len(dataloader.dataset) / elapsed,
    }

def main():
    # Configuration
    batch_size = 64
    num_epochs = 5
    learning_rate = 0.001
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # TODO: Create dataset and dataloader
    # Use CIFAR-10 or similar
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    train_dataset = datasets.CIFAR10(
        root='./data',
        train=True,
        download=True,
        transform=transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=2
    )

    # TODO: Create model, optimizer, criterion
    model = SimpleCNN().to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    # Training loop
    print(f"Training on {device}")
    for epoch in range(num_epochs):
        metrics = train_epoch(model, train_loader, optimizer, criterion, device)
        print(f"Epoch {epoch}: Loss={metrics['loss']:.4f}, "
              f"Acc={metrics['accuracy']:.4f}, "
              f"Time={metrics['time']:.2f}s, "
              f"Throughput={metrics['throughput']:.0f} samples/s")

if __name__ == '__main__':
    main()
```

### Task 1.2: Run Baseline Training

```bash
# Run training
python train_baseline.py
```

**TODO**: Record baseline metrics:
- Training time per epoch: __________ seconds
- Throughput: __________ samples/second
- Final accuracy: __________%

## Exercise 2: Distributed Training with Ray Train

Now convert to distributed training using Ray Train.

### Task 2.1: Create Distributed Training Script

Create `train_ray_distributed.py`:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from ray import train
from ray.train.torch import TorchTrainer
import ray

# TODO: Use the same SimpleCNN model from Exercise 1

def train_func(config):
    """
    Training function that runs on each worker
    Ray Train handles distribution automatically
    """
    # Get distributed training context
    rank = train.get_context().get_world_rank()
    world_size = train.get_context().get_world_size()

    print(f"Worker {rank}/{world_size} starting")

    # TODO: Create model
    model = SimpleCNN()
    # TODO: Wrap model with Ray Train (handles DDP automatically)
    model = train.torch.prepare_model(model)

    # TODO: Create optimizer
    optimizer = optim.Adam(
        model.parameters(),
        lr=config['learning_rate'] * world_size  # Scale learning rate
    )

    criterion = nn.CrossEntropyLoss()

    # TODO: Create dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    train_dataset = datasets.CIFAR10(
        root='./data',
        train=True,
        download=True,
        transform=transform
    )

    # TODO: Create dataloader with Ray Train preparation
    # This handles distributed sampling automatically
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=2
    )
    train_loader = train.torch.prepare_data_loader(train_loader)

    # Training loop
    for epoch in range(config['num_epochs']):
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            # TODO: Implement training step
            # Similar to baseline, but gradients are automatically synchronized
            pass

        # TODO: Calculate metrics
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total

        # TODO: Report metrics to Ray Train
        # Metrics are automatically aggregated across workers
        train.report({
            'epoch': epoch,
            'loss': avg_loss,
            'accuracy': accuracy,
        })

        if rank == 0:
            print(f"Epoch {epoch}: Loss={avg_loss:.4f}, Acc={accuracy:.4f}")

def main():
    # Initialize Ray
    ray.init(address='auto')  # Connect to existing cluster

    # Configuration
    config = {
        'learning_rate': 0.001,
        'batch_size': 64,
        'num_epochs': 5,
    }

    # TODO: Create TorchTrainer
    trainer = TorchTrainer(
        train_func,
        train_loop_config=config,
        scaling_config=train.ScalingConfig(
            num_workers=2,  # Number of GPUs
            use_gpu=True,
            resources_per_worker={"CPU": 2, "GPU": 1},
        ),
        run_config=train.RunConfig(
            name="cifar10_distributed",
            storage_path="/mnt/shared/ray_results",
        ),
    )

    # Train
    print("Starting distributed training...")
    result = trainer.fit()

    print("\nTraining complete!")
    print(f"Final metrics: {result.metrics}")

    ray.shutdown()

if __name__ == '__main__':
    main()
```

### Task 2.2: Run Distributed Training

```bash
# Copy script to Ray cluster
kubectl cp train_ray_distributed.py \
  ray-system/ray-cluster-head-xxxxx:/tmp/

# Execute on Ray cluster
kubectl exec -it -n ray-system ray-cluster-head-xxxxx -- \
  python /tmp/train_ray_distributed.py
```

**TODO**: Record distributed training metrics:
- Training time per epoch: __________ seconds
- Throughput: __________ samples/second
- Speedup vs baseline: __________x
- Scaling efficiency: __________%

## Exercise 3: Scaling to More Workers

Scale up to 4 workers and measure performance.

### Task 3.1: Scale Ray Cluster

```bash
# Scale worker group
kubectl patch raycluster ray-cluster -n ray-system \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/workerGroupSpecs/0/replicas", "value": 4}]'

# Wait for workers
kubectl wait --for=condition=ready pod \
  -l ray.io/group=gpu-workers \
  -n ray-system \
  --timeout=300s
```

### Task 3.2: Run with 4 Workers

Modify `train_ray_distributed.py`:

```python
# Change scaling_config
scaling_config=train.ScalingConfig(
    num_workers=4,  # 4 GPUs
    use_gpu=True,
    resources_per_worker={"CPU": 2, "GPU": 1},
)
```

Run again and record metrics.

**TODO**: Complete scaling analysis table:

| Workers | Time/Epoch | Throughput | Speedup | Efficiency |
|---------|-----------|------------|---------|------------|
| 1       |           |            | 1.0x    | 100%       |
| 2       |           |            |         |            |
| 4       |           |            |         |            |

## Exercise 4: Checkpointing and Recovery

Implement checkpointing to enable fault tolerance.

### Task 4.1: Add Checkpointing

Modify training function:

```python
def train_func_with_checkpointing(config):
    """Training function with checkpointing"""
    rank = train.get_context().get_world_rank()

    # TODO: Create model and optimizer
    model = SimpleCNN()
    model = train.torch.prepare_model(model)
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])

    # TODO: Try to load checkpoint
    checkpoint = train.get_checkpoint()
    if checkpoint:
        with checkpoint.as_directory() as checkpoint_dir:
            checkpoint_dict = torch.load(f"{checkpoint_dir}/checkpoint.pt")
            model.load_state_dict(checkpoint_dict['model_state_dict'])
            optimizer.load_state_dict(checkpoint_dict['optimizer_state_dict'])
            start_epoch = checkpoint_dict['epoch'] + 1
            if rank == 0:
                print(f"Resumed from epoch {checkpoint_dict['epoch']}")
    else:
        start_epoch = 0

    # Create dataloader
    train_loader = # TODO: Create and prepare dataloader

    # Training loop with checkpointing
    for epoch in range(start_epoch, config['num_epochs']):
        # TODO: Train epoch

        # TODO: Save checkpoint every epoch
        checkpoint_dict = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }

        with train.checkpoint_context() as checkpoint_dir:
            torch.save(checkpoint_dict, f"{checkpoint_dir}/checkpoint.pt")

        # Report metrics
        train.report({
            'epoch': epoch,
            'loss': avg_loss,
            'accuracy': accuracy,
        })
```

### Task 4.2: Test Recovery

1. Start training
2. Interrupt it after 2 epochs (Ctrl+C or kill pod)
3. Restart training
4. Verify it resumes from checkpoint

**TODO**: Answer these questions:
1. What epoch did training resume from? __________
2. Were the metrics continuous? __________
3. How much training time was saved? __________

## Exercise 5: Performance Monitoring

Use Ray Dashboard to monitor training performance.

### Task 5.1: Monitor Training

While training is running:

1. Open Ray Dashboard (http://localhost:8265)
2. Navigate to "Jobs" tab
3. Click on your running job
4. Observe:
   - CPU utilization per worker
   - GPU utilization per worker
   - Memory usage
   - Task timeline

**TODO**: Take screenshots of:
1. Job overview
2. Resource utilization graphs
3. Task timeline

### Task 5.2: Identify Bottlenecks

Analyze the metrics:

**TODO**: Answer these questions:
1. What is the average GPU utilization? __________%
2. Are workers idle at any point? __________
3. Is data loading a bottleneck? __________
4. What could be optimized? __________

## Exercise 6: Hyperparameter Tuning with Ray Tune

Combine Ray Train with Ray Tune for distributed hyperparameter search.

### Task 6.1: Create Tuning Script

Create `tune_distributed.py`:

```python
from ray import tune
from ray.tune.schedulers import ASHAScheduler

def trainable(config):
    """Trainable function for Ray Tune"""
    # Use train_func from Exercise 2
    train_func_with_checkpointing(config)

def main():
    ray.init(address='auto')

    # Define search space
    search_space = {
        'learning_rate': tune.loguniform(1e-5, 1e-2),
        'batch_size': tune.choice([32, 64, 128]),
        'num_epochs': 10,
    }

    # Configure scheduler
    scheduler = ASHAScheduler(
        max_t=10,
        grace_period=2,
        reduction_factor=2,
    )

    # TODO: Create Tuner
    tuner = tune.Tuner(
        # Wrap training function
        tune.with_resources(
            tune.with_parameters(trainable),
            resources={"CPU": 2, "GPU": 1}
        ),
        param_space=search_space,
        tune_config=tune.TuneConfig(
            metric="accuracy",
            mode="max",
            num_samples=8,  # 8 trials
            scheduler=scheduler,
        ),
    )

    # Run tuning
    results = tuner.fit()

    # Get best result
    best_result = results.get_best_result("accuracy", "max")
    print(f"\nBest config: {best_result.config}")
    print(f"Best accuracy: {best_result.metrics['accuracy']:.4f}")

    ray.shutdown()

if __name__ == '__main__':
    main()
```

### Task 6.2: Run Hyperparameter Search

```bash
python tune_distributed.py
```

**TODO**: Record results:
- Best learning rate: __________
- Best batch size: __________
- Best accuracy achieved: __________%
- Number of trials completed: __________

## Challenge Exercise: Multi-Node Training

Scale to multi-node training (if you have a multi-node cluster).

### Requirements:
- At least 2 physical nodes
- 2+ GPUs per node
- Inter-node networking (InfiniBand or 10GbE+)

### Tasks:
1. Scale Ray cluster to use multiple nodes
2. Configure network optimizations
3. Run training with 8+ total GPUs
4. Measure inter-node communication overhead
5. Calculate scaling efficiency

**TODO**: Multi-node results:
- Number of nodes: __________
- GPUs per node: __________
- Total GPUs: __________
- Scaling efficiency: __________%
- Communication overhead: __________%

## Lab Deliverables

Submit the following:

1. **Code Files**:
   - `train_baseline.py`
   - `train_ray_distributed.py`
   - `tune_distributed.py`

2. **Performance Report** including:
   - Baseline vs distributed training comparison
   - Scaling efficiency analysis
   - Screenshots of Ray Dashboard
   - Bottleneck analysis

3. **Written Answers** to all TODO questions

4. **Reflection** (500 words):
   - What challenges did you face?
   - What surprised you about distributed training?
   - How would you optimize further?
   - When would you choose Ray Train vs other frameworks?

## Additional Resources

- [Ray Train Documentation](https://docs.ray.io/en/latest/train/train.html)
- [Ray Tune Examples](https://docs.ray.io/en/latest/tune/examples/index.html)
- [KubeRay Documentation](https://ray-project.github.io/kuberay/)

## Troubleshooting

### Issue: Ray cluster pods not starting

```bash
# Check pod status
kubectl describe pod -n ray-system <pod-name>

# Check logs
kubectl logs -n ray-system <pod-name>

# Common issues:
# - Insufficient resources
# - Image pull errors
# - PVC not bound
```

### Issue: Training hanging

- Check Ray Dashboard for worker status
- Verify GPU availability: `kubectl exec -it <pod-name> -- nvidia-smi`
- Check network connectivity between nodes
- Review Ray logs: `kubectl logs -n ray-system <pod-name> -c ray-worker`

### Issue: Out of memory

- Reduce batch size
- Enable gradient checkpointing
- Use mixed precision training
- Scale to more workers

## Next Steps

After completing this lab:
- Proceed to Lab 02: Horovod Multi-Node Training
- Experiment with larger models
- Try different distributed strategies
- Explore Ray's other features (Ray Serve, Ray RLlib)

---

**Estimated Completion Time**: 3-4 hours
**Difficulty**: Intermediate
**Last Updated**: 2025-10-16
