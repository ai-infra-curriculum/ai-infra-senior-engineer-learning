# Lecture 03: Horovod and PyTorch DDP

## Learning Objectives

By the end of this lecture, you will be able to:

- Implement distributed training using Horovod with MPI-based communication for HPC environments
- Configure PyTorch DistributedDataParallel (DDP) for multi-GPU and multi-node training
- Deploy PyTorch Fully Sharded Data Parallel (FSDP) for training large models exceeding single-GPU memory
- Implement TensorFlow distributed strategies including MirroredStrategy and MultiWorkerMirroredStrategy
- Compare performance characteristics of Horovod, PyTorch DDP, and Ray Train for different workloads
- Optimize gradient synchronization and communication patterns for distributed training efficiency
- Implement production deployment patterns for distributed training on Kubernetes and SLURM clusters
- Troubleshoot common distributed training issues including OOM errors, stragglers, and synchronization failures

## Table of Contents

1. [Introduction](#introduction)
2. [Horovod Architecture](#horovod-architecture)
3. [Horovod Implementation](#horovod-implementation)
4. [PyTorch DistributedDataParallel](#pytorch-ddp)
5. [PyTorch FSDP](#pytorch-fsdp)
6. [TensorFlow Distributed Strategies](#tensorflow-distributed)
7. [Framework Comparison](#framework-comparison)
8. [Performance Optimization](#performance-optimization)
9. [Production Deployment](#production-deployment)

## Introduction

Horovod and PyTorch DDP are two of the most popular frameworks for distributed deep learning training. Both provide data parallel training with efficient gradient synchronization.

### Key Differences

| Feature | Horovod | PyTorch DDP | Ray Train |
|---------|---------|-------------|-----------|
| Backend | MPI-based | PyTorch native | Multi-backend |
| Framework Support | Multi-framework | PyTorch only | Multi-framework |
| Learning Curve | Medium | Easy (if know PyTorch) | Easy |
| Setup Complexity | Higher (MPI) | Lower | Lowest |
| Performance | Excellent | Excellent | Very Good |
| Fault Tolerance | Manual | Limited | Built-in |
| Best For | HPC clusters | PyTorch users | Cloud/K8s |

## Horovod Architecture

### MPI-Based Communication

Horovod uses Message Passing Interface (MPI) for inter-process communication, making it ideal for HPC environments.

```
┌──────────────────────────────────────────────────────────────┐
│              Horovod Architecture Overview                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                MPI Coordination Layer                  │  │
│  │  - Process management                                  │  │
│  │  - Rank assignment                                     │  │
│  │  - Communication setup                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐         │
│    │ Rank 0  │       │ Rank 1  │       │ Rank 2  │         │
│    │ (GPU 0) │       │ (GPU 1) │       │ (GPU 2) │         │
│    ├─────────┤       ├─────────┤       ├─────────┤         │
│    │ Model   │       │ Model   │       │ Model   │         │
│    │ Copy    │       │ Copy    │       │ Copy    │         │
│    ├─────────┤       ├─────────┤       ├─────────┤         │
│    │ Batch 0 │       │ Batch 1 │       │ Batch 2 │         │
│    └─────────┘       └─────────┘       └─────────┘         │
│         │                  │                  │             │
│         │    Forward Pass & Backward Pass     │             │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│    ┌─────────┐       ┌─────────┐       ┌─────────┐         │
│    │ Grads 0 │       │ Grads 1 │       │ Grads 2 │         │
│    └─────────┘       └─────────┘       └─────────┘         │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   hvd.allreduce │                       │
│                   │   (Ring or NCCL)│                       │
│                   └────────┬────────┘                       │
│                            │                                │
│         ┌──────────────────┴──────────────────┐             │
│         ▼                  ▼                  ▼             │
│   Averaged Grads     Averaged Grads     Averaged Grads     │
│         │                  │                  │             │
│   Update Model       Update Model       Update Model       │
│                                                             │
└──────────────────────────────────────────────────────────────┘
```

### Core Concepts

**1. Ring-AllReduce Algorithm**
- Each GPU communicates with exactly 2 neighbors
- Bandwidth-optimal: transfers N-1 copies of data
- No single bottleneck node
- Excellent scaling to many GPUs

**2. Hierarchical AllReduce**
- Uses NCCL for intra-node communication (NVLink)
- Uses MPI for inter-node communication (InfiniBand)
- Leverages best of both worlds

**3. Gradient Compression**
- Optional compression to reduce bandwidth
- Trade-off: computation vs communication
- Useful for slow networks

## Horovod Implementation

### Basic Horovod Training

```python
import torch
import torch.nn as nn
import torch.optim as optim
import horovod.torch as hvd

# Initialize Horovod
hvd.init()

# Pin GPU to be used to process local rank
torch.cuda.set_device(hvd.local_rank())

# Build model
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10),
)
model.cuda()

# Scale learning rate by number of workers
optimizer = optim.SGD(
    model.parameters(),
    lr=0.01 * hvd.size()  # Scale learning rate
)

# Wrap optimizer with Horovod Distributed Optimizer
optimizer = hvd.DistributedOptimizer(
    optimizer,
    named_parameters=model.named_parameters()
)

# Broadcast initial parameters from rank 0 to all workers
hvd.broadcast_parameters(model.state_dict(), root_rank=0)
hvd.broadcast_optimizer_state(optimizer, root_rank=0)

# Training loop
def train_epoch(model, optimizer, train_loader, epoch):
    """
    Train one epoch with Horovod
    """
    model.train()

    # Horovod: set epoch for sampler
    train_sampler.set_epoch(epoch)

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.cuda(), target.cuda()

        optimizer.zero_grad()
        output = model(data)
        loss = nn.functional.cross_entropy(output, target)
        loss.backward()

        # Horovod: gradient averaging happens inside optimizer.step()
        optimizer.step()

        if batch_idx % 10 == 0 and hvd.rank() == 0:
            print(f'Epoch {epoch} [{batch_idx}/{len(train_loader)}] '
                  f'Loss: {loss.item():.4f}')

# Create distributed sampler
from torch.utils.data.distributed import DistributedSampler

train_dataset = create_dataset()
train_sampler = DistributedSampler(
    train_dataset,
    num_replicas=hvd.size(),
    rank=hvd.rank()
)

train_loader = torch.utils.data.DataLoader(
    train_dataset,
    batch_size=32,
    sampler=train_sampler,
    num_workers=4,
    pin_memory=True
)

# Train
for epoch in range(10):
    train_epoch(model, optimizer, train_loader, epoch)
```

### Advanced Horovod Features

```python
import horovod.torch as hvd

class HorovodTrainer:
    """
    Production-ready Horovod trainer
    """

    def __init__(self, model, config):
        # Initialize Horovod
        hvd.init()

        # Setup device
        if torch.cuda.is_available():
            torch.cuda.set_device(hvd.local_rank())
            self.device = torch.device('cuda')
        else:
            self.device = torch.device('cpu')

        self.model = model.to(self.device)
        self.config = config

        # Scale learning rate
        base_lr = config['learning_rate']
        scaled_lr = base_lr * hvd.size()

        # Create optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=scaled_lr
        )

        # Wrap with Horovod
        self.optimizer = hvd.DistributedOptimizer(
            self.optimizer,
            named_parameters=self.model.named_parameters(),
            # Gradient compression (optional)
            compression=hvd.Compression.fp16 if config.get('fp16') else hvd.Compression.none,
            # Gradient averaging
            op=hvd.Average,
            # Backward passes per step (for gradient accumulation)
            backward_passes_per_step=config.get('accumulation_steps', 1),
        )

        # Broadcast initial state
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

        # Learning rate scheduler (warmup important for large batch training)
        self.scheduler = self._create_scheduler()

    def _create_scheduler(self):
        """Create learning rate scheduler with warmup"""
        # TODO: Implement learning rate warmup
        # Important for training with large effective batch sizes

        def lr_schedule(epoch):
            # Warmup for first 5 epochs
            warmup_epochs = 5
            if epoch < warmup_epochs:
                return float(epoch + 1) / warmup_epochs
            else:
                # Cosine decay after warmup
                import math
                progress = (epoch - warmup_epochs) / (self.config['epochs'] - warmup_epochs)
                return 0.5 * (1 + math.cos(math.pi * progress))

        return optim.lr_scheduler.LambdaLR(self.optimizer, lr_schedule)

    def train_epoch(self, dataloader, epoch):
        """Train one epoch"""
        self.model.train()

        total_loss = 0
        total_correct = 0
        total_samples = 0

        for batch_idx, (data, target) in enumerate(dataloader):
            data = data.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)

            self.optimizer.zero_grad()
            output = self.model(data)
            loss = nn.functional.cross_entropy(output, target)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0
            )

            self.optimizer.step()

            # Metrics
            pred = output.argmax(dim=1)
            correct = pred.eq(target).sum().item()

            total_loss += loss.item() * data.size(0)
            total_correct += correct
            total_samples += data.size(0)

            if batch_idx % 100 == 0 and hvd.rank() == 0:
                accuracy = 100. * correct / data.size(0)
                print(f'Epoch {epoch} [{batch_idx}/{len(dataloader)}] '
                      f'Loss: {loss.item():.4f} Acc: {accuracy:.2f}%')

        # Average metrics across all workers
        avg_loss = self._metric_average(total_loss / total_samples, 'avg_loss')
        avg_accuracy = self._metric_average(total_correct / total_samples, 'avg_accuracy')

        return avg_loss, avg_accuracy

    def _metric_average(self, val, name):
        """Average metric across all workers"""
        tensor = torch.tensor(val).to(self.device)
        avg_tensor = hvd.allreduce(tensor, name=name)
        return avg_tensor.item()

    def save_checkpoint(self, epoch, metrics, path):
        """Save checkpoint (only on rank 0)"""
        if hvd.rank() == 0:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
                'metrics': metrics,
            }
            torch.save(checkpoint, path)
            print(f'Checkpoint saved: {path}')

    def load_checkpoint(self, path):
        """Load checkpoint"""
        # Load on CPU first
        checkpoint = torch.load(path, map_location='cpu')

        # Load model state
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        # Move model to device
        self.model.to(self.device)

        # Broadcast state to ensure all workers are synchronized
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

        return checkpoint['epoch'], checkpoint['metrics']

# Usage
def main():
    # Configuration
    config = {
        'learning_rate': 0.001,
        'epochs': 50,
        'batch_size': 32,
        'fp16': True,
        'accumulation_steps': 1,
    }

    # Create model
    model = create_model()

    # Create trainer
    trainer = HorovodTrainer(model, config)

    # Create dataloader
    train_dataset = create_dataset()
    train_sampler = DistributedSampler(
        train_dataset,
        num_replicas=hvd.size(),
        rank=hvd.rank()
    )
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True
    )

    # Training loop
    for epoch in range(config['epochs']):
        train_sampler.set_epoch(epoch)
        loss, accuracy = trainer.train_epoch(train_loader, epoch)
        trainer.scheduler.step()

        if hvd.rank() == 0:
            print(f'Epoch {epoch}: Loss={loss:.4f}, Accuracy={accuracy:.4f}')
            trainer.save_checkpoint(
                epoch,
                {'loss': loss, 'accuracy': accuracy},
                f'checkpoint_epoch_{epoch}.pt'
            )

if __name__ == '__main__':
    main()
```

### Launching Horovod Jobs

```bash
# Launch with horovodrun
horovodrun -np 4 -H localhost:4 python train.py

# Multi-node training
horovodrun -np 16 \
    -H server1:4,server2:4,server3:4,server4:4 \
    python train.py

# With MPI directly
mpirun -np 4 \
    -bind-to none \
    -map-by slot \
    -x NCCL_DEBUG=INFO \
    -x LD_LIBRARY_PATH \
    -x PATH \
    -mca pml ob1 \
    -mca btl ^openib \
    python train.py

# On Kubernetes with Horovod Operator
kubectl create -f horovod-job.yaml
```

## PyTorch DistributedDataParallel

PyTorch DDP is the recommended way to do distributed training in PyTorch.

### DDP Implementation

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup(rank, world_size):
    """
    Initialize distributed training

    Args:
        rank: Rank of current process
        world_size: Total number of processes
    """
    # Set environment variables
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'

    # Initialize process group
    # Backend: nccl for GPU, gloo for CPU
    dist.init_process_group(
        backend='nccl',
        init_method='env://',
        rank=rank,
        world_size=world_size
    )

    # Set device
    torch.cuda.set_device(rank)

def cleanup():
    """Cleanup distributed training"""
    dist.destroy_process_group()

def train_ddp(rank, world_size, config):
    """
    DDP training function

    Args:
        rank: Process rank
        world_size: Total number of processes
        config: Training configuration
    """
    # Setup
    setup(rank, world_size)

    # Create model and move to GPU
    model = create_model(config).to(rank)

    # Wrap model with DDP
    model = DDP(
        model,
        device_ids=[rank],
        output_device=rank,
        # Important optimization: avoid unnecessary buffer broadcasts
        broadcast_buffers=False,
        # Gradient as bucket view for memory efficiency
        gradient_as_bucket_view=True,
    )

    # Create optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config['lr'] * world_size  # Scale learning rate
    )

    # Create dataset and sampler
    train_dataset = create_dataset()
    train_sampler = DistributedSampler(
        train_dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True,
        drop_last=True  # Important for batch norm
    )

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True,
        persistent_workers=True,  # Keep workers alive
    )

    # Training loop
    for epoch in range(config['epochs']):
        # Set epoch for proper shuffling
        train_sampler.set_epoch(epoch)

        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            data = data.to(rank, non_blocking=True)
            target = target.to(rank, non_blocking=True)

            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.cross_entropy(output, target)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            optimizer.step()

            if batch_idx % 100 == 0 and rank == 0:
                print(f'Rank {rank} Epoch {epoch} '
                      f'[{batch_idx}/{len(train_loader)}] '
                      f'Loss: {loss.item():.4f}')

    # Cleanup
    cleanup()

def main():
    """Main function to launch distributed training"""
    world_size = torch.cuda.device_count()

    config = {
        'lr': 0.001,
        'batch_size': 32,
        'epochs': 10,
    }

    # Spawn processes for each GPU
    mp.spawn(
        train_ddp,
        args=(world_size, config),
        nprocs=world_size,
        join=True
    )

if __name__ == '__main__':
    main()
```

### Advanced DDP Features

```python
class AdvancedDDPTrainer:
    """
    Production-ready DDP trainer with all optimizations
    """

    def __init__(self, rank, world_size, config):
        self.rank = rank
        self.world_size = world_size
        self.config = config

        # Setup distributed
        self._setup_distributed()

        # Create model
        self.model = self._create_model()

        # Wrap with DDP
        self.model = self._wrap_ddp()

        # Create optimizer and scheduler
        self.optimizer = self._create_optimizer()
        self.scheduler = self._create_scheduler()

        # Mixed precision training
        self.scaler = torch.cuda.amp.GradScaler(
            enabled=config.get('fp16', False)
        )

    def _setup_distributed(self):
        """Setup distributed environment"""
        os.environ['MASTER_ADDR'] = self.config.get('master_addr', 'localhost')
        os.environ['MASTER_PORT'] = self.config.get('master_port', '12355')

        dist.init_process_group(
            backend='nccl',
            init_method='env://',
            rank=self.rank,
            world_size=self.world_size,
            timeout=timedelta(minutes=30)  # Longer timeout for large models
        )

        torch.cuda.set_device(self.rank)

    def _wrap_ddp(self):
        """Wrap model with DDP"""
        # Find unused parameters for complex models
        find_unused = self.config.get('find_unused_parameters', False)

        return DDP(
            self.model,
            device_ids=[self.rank],
            output_device=self.rank,
            broadcast_buffers=False,
            gradient_as_bucket_view=True,
            find_unused_parameters=find_unused,
            # Static graph optimization (if model structure doesn't change)
            static_graph=self.config.get('static_graph', False),
        )

    def train_epoch(self, dataloader, epoch):
        """Train one epoch with all optimizations"""
        self.model.train()

        # DDP: Set epoch for sampler
        if hasattr(dataloader.sampler, 'set_epoch'):
            dataloader.sampler.set_epoch(epoch)

        total_loss = 0
        num_batches = 0

        for batch_idx, (data, target) in enumerate(dataloader):
            data = data.to(self.rank, non_blocking=True)
            target = target.to(self.rank, non_blocking=True)

            # Mixed precision training
            with torch.cuda.amp.autocast(enabled=self.config.get('fp16', False)):
                output = self.model(data)
                loss = nn.functional.cross_entropy(output, target)

            # Backward with gradient scaling
            self.optimizer.zero_grad()
            self.scaler.scale(loss).backward()

            # Gradient clipping (unscale first for mixed precision)
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            # Optimizer step
            self.scaler.step(self.optimizer)
            self.scaler.update()

            total_loss += loss.item()
            num_batches += 1

            if batch_idx % 100 == 0 and self.rank == 0:
                avg_loss = total_loss / num_batches
                print(f'Epoch {epoch} [{batch_idx}/{len(dataloader)}] '
                      f'Loss: {avg_loss:.4f}')

        # Average loss across all ranks
        avg_loss = torch.tensor(total_loss / num_batches).to(self.rank)
        dist.all_reduce(avg_loss, op=dist.ReduceOp.AVG)

        return avg_loss.item()

    @torch.no_grad()
    def validate(self, dataloader):
        """Validation with distributed metrics"""
        self.model.eval()

        total_loss = 0
        total_correct = 0
        total_samples = 0

        for data, target in dataloader:
            data = data.to(self.rank, non_blocking=True)
            target = target.to(self.rank, non_blocking=True)

            with torch.cuda.amp.autocast(enabled=self.config.get('fp16', False)):
                output = self.model(data)
                loss = nn.functional.cross_entropy(output, target)

            pred = output.argmax(dim=1)
            correct = pred.eq(target).sum().item()

            total_loss += loss.item() * data.size(0)
            total_correct += correct
            total_samples += data.size(0)

        # Aggregate metrics across all ranks
        metrics = torch.tensor([total_loss, total_correct, total_samples]).to(self.rank)
        dist.all_reduce(metrics, op=dist.ReduceOp.SUM)

        avg_loss = metrics[0].item() / metrics[2].item()
        accuracy = metrics[1].item() / metrics[2].item()

        return avg_loss, accuracy

    def save_checkpoint(self, epoch, metrics, path):
        """Save checkpoint (only rank 0)"""
        if self.rank == 0:
            # Save model state (unwrap DDP)
            model_state = self.model.module.state_dict()

            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model_state,
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
                'scaler_state_dict': self.scaler.state_dict(),
                'metrics': metrics,
                'config': self.config,
            }

            torch.save(checkpoint, path)
            print(f'Checkpoint saved: {path}')

        # Wait for rank 0 to finish saving
        dist.barrier()

    def load_checkpoint(self, path):
        """Load checkpoint on all ranks"""
        # Map to current device
        checkpoint = torch.load(path, map_location=f'cuda:{self.rank}')

        # Load states
        self.model.module.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.scaler.load_state_dict(checkpoint['scaler_state_dict'])

        # Synchronize all ranks
        dist.barrier()

        return checkpoint['epoch'], checkpoint['metrics']

# Launch with torchrun (recommended)
# torchrun --nproc_per_node=4 train.py

def main():
    # Parse rank and world_size from environment
    rank = int(os.environ['LOCAL_RANK'])
    world_size = int(os.environ['WORLD_SIZE'])

    config = {
        'lr': 0.001,
        'batch_size': 32,
        'epochs': 50,
        'fp16': True,
        'static_graph': True,
    }

    # Create trainer
    trainer = AdvancedDDPTrainer(rank, world_size, config)

    # Create dataloaders
    train_loader = create_train_loader(rank, world_size, config)
    val_loader = create_val_loader(rank, world_size, config)

    # Training loop
    for epoch in range(config['epochs']):
        train_loss = trainer.train_epoch(train_loader, epoch)
        val_loss, val_acc = trainer.validate(val_loader)
        trainer.scheduler.step()

        if rank == 0:
            print(f'Epoch {epoch}: Train Loss={train_loss:.4f}, '
                  f'Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}')

        trainer.save_checkpoint(
            epoch,
            {'train_loss': train_loss, 'val_loss': val_loss, 'val_acc': val_acc},
            f'checkpoint_epoch_{epoch}.pt'
        )

if __name__ == '__main__':
    main()
```

## PyTorch FSDP

Fully Sharded Data Parallel (FSDP) is PyTorch's answer to ZeRO, enabling training of very large models.

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy
from torch.distributed.fsdp import CPUOffload, BackwardPrefetch

def train_fsdp(rank, world_size, config):
    """
    Train with FSDP for large models
    """
    setup(rank, world_size)

    # Create model
    model = create_large_model(config).to(rank)

    # Auto wrap policy (wrap layers with > 100M parameters)
    auto_wrap_policy = size_based_auto_wrap_policy(
        min_num_params=100_000_000
    )

    # Wrap with FSDP
    model = FSDP(
        model,
        auto_wrap_policy=auto_wrap_policy,
        # CPU offloading for very large models
        cpu_offload=CPUOffload(offload_params=True),
        # Mixed precision
        mixed_precision=torch.distributed.fsdp.MixedPrecision(
            param_dtype=torch.float16,
            reduce_dtype=torch.float16,
            buffer_dtype=torch.float16,
        ),
        # Backward prefetch for better performance
        backward_prefetch=BackwardPrefetch.BACKWARD_PRE,
        # Sharding strategy
        sharding_strategy=torch.distributed.fsdp.ShardingStrategy.FULL_SHARD,
    )

    # TODO: Training loop similar to DDP
    # FSDP handles parameter sharding automatically

    cleanup()
```

## TensorFlow Distributed Strategies

```python
import tensorflow as tf

# MultiWorkerMirroredStrategy for multi-node training
strategy = tf.distribute.MultiWorkerMirroredStrategy()

with strategy.scope():
    # Create model within strategy scope
    model = create_model()

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

# Create distributed dataset
def create_tf_dataset(file_pattern):
    dataset = tf.data.TFRecordDataset(file_pattern)
    dataset = dataset.map(parse_function)
    dataset = dataset.batch(batch_size)
    return dataset

train_dataset = create_tf_dataset('train*.tfrecord')
val_dataset = create_tf_dataset('val*.tfrecord')

# Train with distributed strategy
model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=10
)
```

## Framework Comparison

### When to Use Each Framework

**Use Horovod when:**
- Running on HPC clusters with MPI
- Need multi-framework support (PyTorch + TensorFlow)
- Want proven performance at large scale
- Have InfiniBand networking

**Use PyTorch DDP when:**
- Pure PyTorch workflow
- Want native PyTorch integration
- Need simpler setup than Horovod
- Working with medium-scale models (< 10B parameters)

**Use PyTorch FSDP when:**
- Training very large models (> 10B parameters)
- Need ZeRO-style parameter sharding
- Want to maximize model size on limited GPUs
- Pure PyTorch workflow

**Use Ray Train when:**
- Cloud/Kubernetes deployment
- Need fault tolerance
- Want to combine training with HPO
- Need framework flexibility

### Performance Comparison

```python
# Benchmark results (ResNet-50, ImageNet)
# 8x V100 GPUs, single node

frameworks = {
    'Horovod': {
        'throughput': 2850,  # images/sec
        'scaling_efficiency': 0.95,
        'setup_time': '~30min (MPI)',
    },
    'PyTorch DDP': {
        'throughput': 2800,  # images/sec
        'scaling_efficiency': 0.94,
        'setup_time': '~5min',
    },
    'Ray Train': {
        'throughput': 2650,  # images/sec
        'scaling_efficiency': 0.89,
        'setup_time': '~10min',
    },
}

# All frameworks perform similarly at this scale
# Differences become more significant at 100+ GPUs
```

## Production Deployment

### Horovod on Kubernetes

```yaml
apiVersion: kubeflow.org/v1
kind: MPIJob
metadata:
  name: horovod-training
spec:
  slotsPerWorker: 1
  cleanPodPolicy: Running

  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
        spec:
          containers:
          - name: horovod-launcher
            image: horovod/horovod:latest
            command:
            - mpirun
            args:
            - -np
            - "4"
            - --allow-run-as-root
            - -bind-to
            - none
            - -map-by
            - slot
            - -x
            - NCCL_DEBUG=INFO
            - python
            - /app/train.py

    Worker:
      replicas: 4
      template:
        spec:
          containers:
          - name: horovod-worker
            image: horovod/horovod:latest
            resources:
              limits:
                nvidia.com/gpu: 1
```

## Summary

Key takeaways:

1. **Horovod**: Excellent for HPC, multi-framework support, MPI-based
2. **PyTorch DDP**: Native PyTorch, easy setup, great performance
3. **PyTorch FSDP**: For very large models, ZeRO-style sharding
4. **TensorFlow**: Built-in distributed strategies

**Best Practices:**
- Scale learning rate with world size
- Use warmup for large batch training
- Gradient clipping for stability
- Checkpoint only on rank 0
- Synchronize metrics across ranks

## Further Reading

- [Horovod Documentation](https://horovod.readthedocs.io/)
- [PyTorch DDP Tutorial](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [PyTorch FSDP](https://pytorch.org/docs/stable/fsdp.html)

## Next Steps

Continue to `04-nccl-networking.md` to learn about high-performance networking for distributed training.
