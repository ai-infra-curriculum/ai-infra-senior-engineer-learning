# Lecture 01: Distributed Training Fundamentals

## Learning Objectives

By the end of this lecture, you will be able to:

- Analyze memory and compute requirements for large-scale model training and determine when distributed training is necessary
- Design distributed training architectures using data parallelism, model parallelism, pipeline parallelism, and tensor parallelism
- Implement hybrid parallelism strategies for training models exceeding single-device memory capacity
- Configure gradient synchronization strategies (AllReduce, parameter servers) for optimal training performance
- Evaluate communication patterns and bottlenecks in distributed training systems
- Calculate scaling efficiency metrics and identify sources of training overhead
- Design fault-tolerant distributed training systems with checkpoint and recovery strategies
- Optimize distributed training performance by balancing compute, communication, and memory constraints

## Table of Contents

1. [Introduction to Distributed Training](#introduction)
2. [Why Distributed Training?](#why-distributed-training)
3. [Parallelism Strategies](#parallelism-strategies)
4. [Data Parallelism](#data-parallelism)
5. [Model Parallelism](#model-parallelism)
6. [Pipeline Parallelism](#pipeline-parallelism)
7. [Tensor Parallelism](#tensor-parallelism)
8. [Hybrid Parallelism](#hybrid-parallelism)
9. [Gradient Synchronization Strategies](#gradient-synchronization)
10. [Scaling Laws and Efficiency Metrics](#scaling-laws)
11. [Communication Patterns](#communication-patterns)
12. [Practical Considerations](#practical-considerations)

## Introduction to Distributed Training

Distributed training is the practice of training machine learning models across multiple computing devices (GPUs, TPUs, or CPUs) simultaneously. As models grow larger and datasets expand, single-device training becomes impractical or impossible. Distributed training enables us to:

- **Train larger models** that don't fit on a single device
- **Process more data** in less time
- **Experiment faster** with reduced training time
- **Improve model quality** through larger batch sizes and more data

Modern AI systems like GPT-4, DALL-E, and Stable Diffusion rely heavily on distributed training. Understanding distributed training fundamentals is essential for any Senior AI Infrastructure Engineer.

## Why Distributed Training?

### The Scale Challenge

Consider the scale of modern AI models:

| Model | Parameters | Training Data | Single GPU Training Time |
|-------|-----------|---------------|--------------------------|
| ResNet-50 | 25M | ImageNet (1.2M images) | ~1-2 days |
| BERT-Large | 340M | 16GB text | ~1 week |
| GPT-3 | 175B | 45TB text | ~355 years* |
| GPT-4 | ~1.7T (estimated) | Unknown | Infeasible |

*Estimated on a single NVIDIA A100 GPU

### Memory Constraints

A typical NVIDIA A100 GPU has 80GB of memory. Training a model requires memory for:

```
Total Memory = Model Parameters + Gradients + Optimizer States + Activations + Forward Pass Buffers

For Adam optimizer:
- Model parameters: 2 bytes per parameter (FP16)
- Gradients: 2 bytes per parameter
- Optimizer states: 8 bytes per parameter (first moment, second moment in FP32)
- Total: ~12 bytes per parameter (minimum)

For a 175B parameter model:
175B × 12 bytes = 2.1TB just for model, gradients, and optimizer!
```

This clearly exceeds single-GPU memory, necessitating distributed training.

### Time Constraints

Even if memory wasn't an issue, training time would be:

```python
# Simplified training time calculation
def estimate_training_time(dataset_size, batch_size, epochs, samples_per_second):
    """
    Estimate training time for a model

    Args:
        dataset_size: Number of training samples
        batch_size: Samples per batch
        epochs: Number of training epochs
        samples_per_second: Throughput of training

    Returns:
        Training time in hours
    """
    total_samples = dataset_size * epochs
    batches = total_samples / batch_size
    seconds = batches * (batch_size / samples_per_second)
    hours = seconds / 3600
    return hours

# Example: Training GPT-3 scale model
# Assuming 300B tokens, 1 epoch, 4M token batch, 1000 tokens/sec throughput
time = estimate_training_time(
    dataset_size=300e9,  # 300B tokens
    batch_size=4e6,      # 4M tokens per batch
    epochs=1,
    samples_per_second=1000
)
print(f"Estimated training time: {time:,.0f} hours ({time/24:,.0f} days)")
# Output: ~20,833 hours (~868 days) on single GPU
```

### Cost Efficiency

Distributed training isn't just about making training possible—it's about making it economically viable:

- **Single A100 GPU**: $3/hour on cloud
- **Training 175B model for 1 year**: $3 × 24 × 365 = $26,280
- **256 A100 GPUs for 1.5 days**: $3 × 256 × 36 = $27,648

With proper scaling efficiency (>90%), distributed training becomes cost-competitive at much shorter timescales.

## Parallelism Strategies

There are four main parallelism strategies in distributed training:

```
┌─────────────────────────────────────────────────────────┐
│              Parallelism Strategy Landscape              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Data      │  │    Model     │  │   Pipeline   │  │
│  │ Parallelism  │  │ Parallelism  │  │ Parallelism  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │         │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                            ▼                            │
│                  ┌──────────────────┐                   │
│                  │     Hybrid       │                   │
│                  │   Parallelism    │                   │
│                  └──────────────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Strategy Selection Matrix

| Model Size | GPU Memory | Best Strategy | Secondary Strategy |
|-----------|------------|---------------|-------------------|
| < 1B params | Fits in single GPU | Data Parallelism | None needed |
| 1B - 10B | Fits in single GPU | Data Parallelism | Pipeline (optional) |
| 10B - 100B | Doesn't fit | Pipeline + Data | Model Parallelism |
| > 100B | Way too large | Hybrid (all strategies) | ZeRO optimization |

## Data Parallelism

Data parallelism is the most common and straightforward distributed training strategy. Each device holds a complete copy of the model and processes different batches of data.

### How Data Parallelism Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Parallelism Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Global Batch (size: 256)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [Batch Data] ─────────────┐                          │   │
│  └───────────────────────────│──────────────────────────┘   │
│                              │                              │
│              ┌───────────────┴───────────────┐              │
│              │        Split into 4           │              │
│              │      micro-batches (64)       │              │
│              └───────────────┬───────────────┘              │
│                              │                              │
│       ┌──────────┬───────────┼───────────┬──────────┐       │
│       ▼          ▼           ▼           ▼          │       │
│   ┌──────┐  ┌──────┐    ┌──────┐    ┌──────┐       │       │
│   │GPU 0 │  │GPU 1 │    │GPU 2 │    │GPU 3 │       │       │
│   │Model │  │Model │    │Model │    │Model │       │       │
│   │Copy  │  │Copy  │    │Copy  │    │Copy  │       │       │
│   └──────┘  └──────┘    └──────┘    └──────┘       │       │
│       │          │           │           │          │       │
│       │  Forward Pass & Backward Pass   │          │       │
│       ▼          ▼           ▼           ▼          │       │
│   ┌──────┐  ┌──────┐    ┌──────┐    ┌──────┐       │       │
│   │Grad 0│  │Grad 1│    │Grad 2│    │Grad 3│       │       │
│   └──────┘  └──────┘    └──────┘    └──────┘       │       │
│       │          │           │           │          │       │
│       └──────────┴───────────┴───────────┘          │       │
│                      │                              │       │
│                      ▼                              │       │
│              ┌──────────────┐                       │       │
│              │  AllReduce   │                       │       │
│              │  (Average    │                       │       │
│              │  Gradients)  │                       │       │
│              └──────────────┘                       │       │
│                      │                              │       │
│       ┌──────────────┴──────────────┐               │       │
│       ▼              ▼              ▼               │       │
│   Update Model   Update Model   Update Model       │       │
│                                                     │       │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Example

```python
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup_distributed():
    """
    Initialize distributed training environment
    """
    # TODO: Initialize process group with appropriate backend (nccl for GPU)
    # Hint: Use dist.init_process_group()
    pass

def create_data_parallel_model(model, device_id):
    """
    Wrap model for data parallel training

    Args:
        model: PyTorch model to parallelize
        device_id: GPU device ID for this process

    Returns:
        DDP-wrapped model
    """
    # TODO: Move model to device
    # TODO: Wrap model with DistributedDataParallel
    # Hint: Consider gradient_as_bucket_view=True for efficiency
    pass

# Basic data parallel training loop
def train_epoch_data_parallel(model, dataloader, optimizer, device):
    """
    Train one epoch with data parallelism

    Args:
        model: DDP-wrapped model
        dataloader: Distributed sampler dataloader
        optimizer: Optimizer instance
        device: Training device
    """
    model.train()
    total_loss = 0

    for batch_idx, (data, target) in enumerate(dataloader):
        # TODO: Move data to device
        # TODO: Forward pass
        # TODO: Compute loss
        # TODO: Backward pass
        # TODO: Optimizer step
        # TODO: Zero gradients

        # Each process computes on its local batch
        # Gradients are automatically averaged via AllReduce
        pass

    return total_loss / len(dataloader)

# Complete example with proper synchronization
class DataParallelTrainer:
    """
    Complete data parallel training implementation
    """

    def __init__(self, model, train_dataset, config):
        """
        Initialize distributed trainer

        Args:
            model: Model to train
            train_dataset: Training dataset
            config: Training configuration
        """
        self.config = config
        self.device = torch.device(f"cuda:{dist.get_rank()}")

        # Move model to device and wrap with DDP
        self.model = model.to(self.device)
        self.model = DDP(
            self.model,
            device_ids=[dist.get_rank()],
            output_device=dist.get_rank(),
            gradient_as_bucket_view=True,  # More efficient gradient bucketing
            broadcast_buffers=False,  # Only sync running stats when needed
        )

        # Create distributed sampler
        self.train_sampler = torch.utils.data.distributed.DistributedSampler(
            train_dataset,
            num_replicas=dist.get_world_size(),
            rank=dist.get_rank(),
            shuffle=True,
        )

        self.train_loader = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            sampler=self.train_sampler,
            num_workers=config.num_workers,
            pin_memory=True,
        )

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
        )

    def train_epoch(self, epoch):
        """Train one epoch"""
        # Set epoch for proper shuffling
        self.train_sampler.set_epoch(epoch)

        self.model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(self.train_loader):
            data = data.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)

            # Forward pass
            output = self.model(data)
            loss = nn.functional.cross_entropy(output, target)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()

            # Gradient clipping (optional but recommended)
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0
            )

            # Optimizer step
            self.optimizer.step()

            total_loss += loss.item()

            if batch_idx % 100 == 0 and dist.get_rank() == 0:
                print(f"Epoch {epoch} Batch {batch_idx} Loss: {loss.item():.4f}")

        # Average loss across all processes
        avg_loss = torch.tensor(total_loss / len(self.train_loader)).to(self.device)
        dist.all_reduce(avg_loss, op=dist.ReduceOp.SUM)
        avg_loss = avg_loss.item() / dist.get_world_size()

        return avg_loss
```

### Data Parallelism Performance Characteristics

**Advantages:**
- Simple to implement and understand
- Near-linear scaling for small models (< 1B parameters)
- No model architecture changes required
- Works with any model architecture

**Limitations:**
- Each device must hold full model copy
- Communication overhead grows with model size
- Memory bounded by largest single model
- Gradient synchronization can become bottleneck

**Scaling Efficiency:**

```python
def calculate_scaling_efficiency(time_single_gpu, time_n_gpus, n_gpus):
    """
    Calculate strong scaling efficiency

    Perfect scaling: time_n_gpus = time_single_gpu / n_gpus
    Efficiency = (time_single_gpu / n_gpus) / time_n_gpus
    """
    ideal_time = time_single_gpu / n_gpus
    efficiency = ideal_time / time_n_gpus
    return efficiency * 100  # Return as percentage

# Example measurements for ResNet-50
single_gpu_time = 100  # seconds per epoch
measurements = {
    2: 52,   # 96% efficient
    4: 27,   # 93% efficient
    8: 15,   # 83% efficient
    16: 9,   # 69% efficient
    32: 6,   # 52% efficient
}

for n_gpus, time in measurements.items():
    eff = calculate_scaling_efficiency(single_gpu_time, time, n_gpus)
    print(f"{n_gpus} GPUs: {time}s per epoch, {eff:.1f}% efficient")
```

## Model Parallelism

Model parallelism splits the model itself across multiple devices. This is necessary when a model is too large to fit on a single device.

### Naive Model Parallelism

The simplest form places different layers on different devices:

```
┌────────────────────────────────────────────────────────┐
│              Naive Model Parallelism                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Input Batch                                           │
│      │                                                  │
│      ▼                                                  │
│  ┌───────────────┐                                     │
│  │  GPU 0        │                                     │
│  │  Layers 1-3   │───────┐                            │
│  │  (Embedding + │       │                            │
│  │   Attention)  │       │                            │
│  └───────────────┘       │                            │
│                          │ Transfer                    │
│                          │ Activation                  │
│                          ▼                             │
│                      ┌───────────────┐                 │
│                      │  GPU 1        │                 │
│                      │  Layers 4-6   │────┐           │
│                      │  (Attention + │    │           │
│                      │   FFN)        │    │           │
│                      └───────────────┘    │           │
│                                           │           │
│                                           ▼           │
│                                       ┌───────────────┐│
│                                       │  GPU 2        ││
│                                       │  Layers 7-9   ││
│                                       │  (FFN +       ││
│                                       │   Output)     ││
│                                       └───────────────┘│
│                                           │            │
│                                           ▼            │
│                                        Output          │
│                                                        │
│  Problem: GPU 0 and GPU 2 are idle while GPU 1 works! │
│  This is called "pipeline bubble" - very inefficient  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Implementation Example

```python
import torch
import torch.nn as nn

class NaiveModelParallelTransformer(nn.Module):
    """
    Example of naive model parallelism - inefficient but simple
    """

    def __init__(self, vocab_size, d_model, n_heads, n_layers):
        super().__init__()

        # Split layers across 2 GPUs
        split_point = n_layers // 2

        # First half on GPU 0
        self.embedding = nn.Embedding(vocab_size, d_model).to('cuda:0')
        self.layers_gpu0 = nn.ModuleList([
            TransformerLayer(d_model, n_heads).to('cuda:0')
            for _ in range(split_point)
        ])

        # Second half on GPU 1
        self.layers_gpu1 = nn.ModuleList([
            TransformerLayer(d_model, n_heads).to('cuda:1')
            for _ in range(n_layers - split_point)
        ])

        self.output_layer = nn.Linear(d_model, vocab_size).to('cuda:1')

    def forward(self, x):
        # TODO: Process through first half on GPU 0
        # TODO: Transfer to GPU 1
        # TODO: Process through second half on GPU 1
        # TODO: Return output

        # Start on GPU 0
        x = x.to('cuda:0')
        x = self.embedding(x)

        for layer in self.layers_gpu0:
            x = layer(x)

        # Transfer to GPU 1 (THIS IS EXPENSIVE!)
        x = x.to('cuda:1')

        for layer in self.layers_gpu1:
            x = layer(x)

        x = self.output_layer(x)

        return x

# This implementation has severe limitations:
# 1. Only one GPU active at a time (poor utilization)
# 2. Expensive cross-GPU transfers
# 3. No parallelism across batch dimension
# 4. Difficult to scale beyond 2-4 GPUs
```

### Why Naive Model Parallelism is Inefficient

```python
import time

def simulate_naive_model_parallel_time(
    n_layers=12,
    n_gpus=3,
    layer_time_ms=10,
    transfer_time_ms=5
):
    """
    Simulate time for naive model parallel training

    Args:
        n_layers: Total number of layers
        n_gpus: Number of GPUs
        layer_time_ms: Time to process one layer
        transfer_time_ms: Time to transfer activations between GPUs

    Returns:
        Total forward pass time in milliseconds
    """
    layers_per_gpu = n_layers // n_gpus

    # Time for forward pass (sequential across GPUs)
    forward_time = 0
    for gpu in range(n_gpus):
        # Process layers on this GPU
        forward_time += layers_per_gpu * layer_time_ms

        # Transfer to next GPU (except last)
        if gpu < n_gpus - 1:
            forward_time += transfer_time_ms

    # Backward pass is similar
    backward_time = forward_time

    total_time = forward_time + backward_time

    # Calculate GPU utilization
    active_compute_time = n_layers * layer_time_ms * 2  # Forward + backward
    total_possible_time = n_gpus * total_time
    utilization = (active_compute_time / total_possible_time) * 100

    print(f"Forward pass: {forward_time}ms")
    print(f"Total time: {total_time}ms")
    print(f"GPU Utilization: {utilization:.1f}%")

    return total_time

# Example
simulate_naive_model_parallel_time(n_layers=12, n_gpus=3)
# Output:
# Forward pass: 50ms (4 layers × 10ms + 2 transfers × 5ms)
# Total time: 100ms
# GPU Utilization: 40% (very inefficient!)
```

## Pipeline Parallelism

Pipeline parallelism improves on naive model parallelism by introducing micro-batching, allowing multiple GPUs to work simultaneously.

### GPipe: Pipeline Parallelism

```
┌───────────────────────────────────────────────────────────────┐
│                  Pipeline Parallelism (GPipe)                  │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Batch split into 4 micro-batches: [MB1, MB2, MB3, MB4]      │
│                                                                │
│  Time ──────────────────────────────────────────────>         │
│                                                                │
│  GPU 0   │ MB1 │ MB2 │ MB3 │ MB4 │     │ MB1 │ MB2 │ MB3 │ MB4│
│  Layer   │ Fwd │ Fwd │ Fwd │ Fwd │     │ Bwd │ Bwd │ Bwd │ Bwd│
│  1-3     └─────┴─────┴─────┴─────┘     └─────┴─────┴─────┴───│
│                 │     │     │                                  │
│  GPU 1          │ MB1 │ MB2 │ MB3 │ MB4 │     │ MB1 │ MB2 │ MB3│
│  Layer          │ Fwd │ Fwd │ Fwd │ Fwd │     │ Bwd │ Bwd │ Bwd│
│  4-6            └─────┴─────┴─────┴─────┘     └─────┴─────┴───│
│                       │     │     │                            │
│  GPU 2                │ MB1 │ MB2 │ MB3 │ MB4 │     │ MB1 │ MB2│
│  Layer                │ Fwd │ Fwd │ Fwd │ Fwd │     │ Bwd │ Bwd│
│  7-9                  └─────┴─────┴─────┴─────┘     └─────┴───│
│                                                                │
│  Legend: MB = Micro-batch, Fwd = Forward, Bwd = Backward      │
│                                                                │
│  Note: Pipeline bubble at start and end (gray areas)          │
│  Bubble fraction = (n_gpus - 1) / n_microbatches              │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### Pipeline Parallelism Implementation

```python
import torch
from torch.distributed.pipeline.sync import Pipe

class PipelineParallelModel(nn.Module):
    """
    Pipeline parallel model using PyTorch Pipe
    """

    def __init__(self, layers, balance, devices):
        """
        Args:
            layers: List of nn.Module layers
            balance: List of layer counts per device [3, 3, 3] for 3 devices
            devices: List of device names ['cuda:0', 'cuda:1', 'cuda:2']
        """
        super().__init__()

        # TODO: Create sequential model from layers
        # TODO: Wrap with Pipe for pipeline parallelism
        # Hint: chunks parameter controls number of micro-batches

        self.model = nn.Sequential(*layers)

        # Wrap with Pipe - handles micro-batching automatically
        self.pipe_model = Pipe(
            self.model,
            balance=balance,  # How many layers on each device
            devices=devices,   # Which devices to use
            chunks=8,          # Number of micro-batches
        )

    def forward(self, x):
        # Pipe handles all the complexity
        return self.pipe_model(x)

# More sophisticated example with manual micro-batching
class ManualPipelineParallel:
    """
    Manual pipeline parallelism implementation for educational purposes
    """

    def __init__(self, model_parts, devices):
        """
        Args:
            model_parts: List of model parts (nn.Module) for each device
            devices: List of device IDs
        """
        self.model_parts = [part.to(f'cuda:{dev}')
                           for part, dev in zip(model_parts, devices)]
        self.devices = devices
        self.n_stages = len(devices)

    def forward_pipeline(self, x, n_microbatches=4):
        """
        Forward pass with pipeline parallelism

        Args:
            x: Input tensor
            n_microbatches: Number of micro-batches to split input
        """
        batch_size = x.shape[0]
        microbatch_size = batch_size // n_microbatches

        # Split input into micro-batches
        microbatches = [
            x[i:i+microbatch_size]
            for i in range(0, batch_size, microbatch_size)
        ]

        # Storage for intermediate activations
        stage_outputs = [[] for _ in range(self.n_stages)]

        # Forward pass pipeline schedule
        for mb_idx, mb in enumerate(microbatches):
            # TODO: Implement pipeline schedule
            # Each micro-batch flows through stages sequentially
            # Multiple micro-batches can be in different stages simultaneously

            current_input = mb.to(f'cuda:{self.devices[0]}')

            for stage_idx, model_part in enumerate(self.model_parts):
                # Process this stage
                with torch.no_grad():  # Save memory during forward
                    current_input = model_part(current_input)

                # Store output for backward pass
                stage_outputs[stage_idx].append(current_input.detach())

                # Move to next device if not last stage
                if stage_idx < self.n_stages - 1:
                    current_input = current_input.to(
                        f'cuda:{self.devices[stage_idx + 1]}'
                    )

        # Concatenate all micro-batch outputs
        final_output = torch.cat(stage_outputs[-1], dim=0)

        return final_output, stage_outputs

    def backward_pipeline(self, loss, stage_outputs):
        """
        Backward pass with pipeline parallelism

        TODO: Implement backward pipeline
        - Process in reverse order
        - Each stage computes gradients for its parameters
        - Pass gradient signals to previous stage
        """
        pass

# Calculate pipeline efficiency
def pipeline_efficiency(n_stages, n_microbatches):
    """
    Calculate pipeline parallel efficiency

    Pipeline bubble = (n_stages - 1) / n_microbatches
    Efficiency = 1 - bubble_fraction
    """
    bubble_fraction = (n_stages - 1) / n_microbatches
    efficiency = 1 - bubble_fraction

    return efficiency * 100

# Examples
print("Pipeline Efficiency Analysis:")
for n_micro in [4, 8, 16, 32]:
    eff = pipeline_efficiency(n_stages=4, n_microbatches=n_micro)
    print(f"  {n_micro} micro-batches: {eff:.1f}% efficient")

# Output:
#   4 micro-batches: 25.0% efficient (large bubble!)
#   8 micro-batches: 62.5% efficient
#   16 micro-batches: 81.2% efficient
#   32 micro-batches: 90.6% efficient (good!)
```

### Pipeline Parallelism Characteristics

**Advantages:**
- Enables training models larger than single GPU memory
- Better GPU utilization than naive model parallelism
- Scales to many devices (8-64+ GPUs)
- Preserves model architecture

**Challenges:**
- Pipeline bubble reduces efficiency
- Requires many micro-batches for good efficiency
- Memory overhead for storing activations
- Complexity in gradient synchronization

## Tensor Parallelism

Tensor parallelism (also called intra-layer model parallelism) splits individual operations across devices.

### Megatron-LM Style Tensor Parallelism

```
┌──────────────────────────────────────────────────────────────┐
│            Tensor Parallelism - Matrix Multiplication         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Standard Matrix Multiplication:                             │
│  Y = X @ W                                                    │
│  (B, S, H) @ (H, 4H) = (B, S, 4H)                           │
│                                                               │
│  Tensor Parallel (column-split):                             │
│                                                               │
│         W₁              W₂                                   │
│  X  @  [─────]    X  @  [─────]                              │
│        [─────]          [─────]                              │
│        (H,2H)           (H,2H)                               │
│         GPU 0            GPU 1                               │
│           │                │                                 │
│           ▼                ▼                                 │
│          Y₁               Y₂                                 │
│       (B,S,2H)         (B,S,2H)                             │
│           │                │                                 │
│           └────── Cat ─────┘                                 │
│                    │                                         │
│                    ▼                                         │
│              Y (B,S,4H)                                      │
│                                                               │
│  Communication: AllGather on output                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Tensor Parallelism Implementation

```python
import torch
import torch.distributed as dist

class ColumnParallelLinear(torch.nn.Module):
    """
    Linear layer with column parallelism

    Splits weight matrix by columns across devices
    """

    def __init__(self, in_features, out_features, bias=True):
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features

        # Get tensor parallel world size
        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()

        # Ensure output features divisible by world size
        assert out_features % self.world_size == 0

        self.out_features_per_partition = out_features // self.world_size

        # TODO: Initialize weight matrix partition
        # Each device holds out_features_per_partition columns
        self.weight = torch.nn.Parameter(
            torch.empty(
                self.out_features_per_partition,
                in_features,
            )
        )

        if bias:
            self.bias = torch.nn.Parameter(
                torch.empty(self.out_features_per_partition)
            )
        else:
            self.register_parameter('bias', None)

        # Initialize weights
        torch.nn.init.kaiming_uniform_(self.weight)
        if bias is not None:
            torch.nn.init.zeros_(self.bias)

    def forward(self, x):
        """
        Forward pass with column parallelism

        Args:
            x: Input tensor (B, S, H)

        Returns:
            Output tensor (B, S, 4H) gathered across all devices
        """
        # TODO: Perform linear operation on local partition
        # Input is replicated across all devices
        # Each device computes a subset of output features

        output_parallel = torch.nn.functional.linear(
            x, self.weight, self.bias
        )

        # TODO: AllGather outputs from all devices
        # This communication is necessary to get full output
        output = self._all_gather(output_parallel)

        return output

    def _all_gather(self, tensor):
        """Gather tensors from all devices"""
        # TODO: Implement AllGather communication
        world_size = dist.get_world_size()

        # Prepare buffer for gathering
        tensor_list = [
            torch.empty_like(tensor) for _ in range(world_size)
        ]

        # AllGather operation
        dist.all_gather(tensor_list, tensor)

        # Concatenate along feature dimension
        output = torch.cat(tensor_list, dim=-1)

        return output

class RowParallelLinear(torch.nn.Module):
    """
    Linear layer with row parallelism

    Splits weight matrix by rows across devices
    """

    def __init__(self, in_features, out_features, bias=True):
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features

        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()

        # Ensure input features divisible by world size
        assert in_features % self.world_size == 0

        self.in_features_per_partition = in_features // self.world_size

        # TODO: Initialize weight matrix partition
        # Each device holds in_features_per_partition rows
        self.weight = torch.nn.Parameter(
            torch.empty(
                out_features,
                self.in_features_per_partition,
            )
        )

        # Bias only on rank 0 (will be broadcast)
        if bias and self.rank == 0:
            self.bias = torch.nn.Parameter(torch.empty(out_features))
            torch.nn.init.zeros_(self.bias)
        else:
            self.register_parameter('bias', None)

        torch.nn.init.kaiming_uniform_(self.weight)

    def forward(self, x):
        """
        Forward pass with row parallelism

        Args:
            x: Input tensor (B, S, 4H) - already split across devices

        Returns:
            Output tensor (B, S, H)
        """
        # TODO: Input is already partitioned
        # Each device has a slice of input features

        # Perform local linear operation
        output_parallel = torch.nn.functional.linear(
            x, self.weight, None  # No bias yet
        )

        # TODO: AllReduce to sum partial results
        # Each device computed with subset of input features
        # Need to sum all partial results
        output = self._all_reduce(output_parallel)

        # Add bias on final output
        if self.bias is not None:
            output = output + self.bias

        return output

    def _all_reduce(self, tensor):
        """Sum tensors from all devices"""
        # TODO: Implement AllReduce communication
        dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
        return tensor

# Complete Transformer layer with tensor parallelism
class TensorParallelTransformerLayer(torch.nn.Module):
    """
    Transformer layer with tensor parallelism (Megatron-LM style)
    """

    def __init__(self, hidden_size, ffn_hidden_size):
        super().__init__()

        # Attention: Q, K, V projections with column parallelism
        self.query_key_value = ColumnParallelLinear(
            hidden_size,
            3 * hidden_size,  # Q, K, V together
        )

        # Attention: Output projection with row parallelism
        self.attention_output = RowParallelLinear(
            hidden_size,
            hidden_size,
        )

        # FFN: First layer with column parallelism
        self.ffn_1 = ColumnParallelLinear(
            hidden_size,
            ffn_hidden_size,
        )

        # FFN: Second layer with row parallelism
        self.ffn_2 = RowParallelLinear(
            ffn_hidden_size,
            hidden_size,
        )

        self.layer_norm_1 = torch.nn.LayerNorm(hidden_size)
        self.layer_norm_2 = torch.nn.LayerNorm(hidden_size)

    def forward(self, x):
        """
        Forward pass with tensor parallelism

        Communication pattern:
        1. ColumnParallel (Q,K,V): AllGather on output
        2. RowParallel (attn out): AllReduce on output
        3. ColumnParallel (FFN1): AllGather on output
        4. RowParallel (FFN2): AllReduce on output

        Total: 4 collective communications per layer
        """
        # TODO: Implement attention with tensor parallelism
        residual = x
        x = self.layer_norm_1(x)

        # Self-attention (simplified)
        qkv = self.query_key_value(x)  # AllGather here
        # ... attention computation ...
        attn_output = self.attention_output(qkv)  # AllReduce here

        x = residual + attn_output

        # FFN
        residual = x
        x = self.layer_norm_2(x)
        x = self.ffn_1(x)  # AllGather here
        x = torch.nn.functional.gelu(x)
        x = self.ffn_2(x)  # AllReduce here

        x = residual + x

        return x
```

### Tensor Parallelism Characteristics

**Advantages:**
- Fine-grained parallelism within layers
- Excellent for large hidden dimensions
- Minimal memory overhead
- Works well with data parallelism (hybrid)

**Challenges:**
- Requires high-bandwidth interconnect (NVLink, InfiniBand)
- Communication per layer (not just per batch)
- Model architecture changes required
- Limited to models with large matrix operations

## Hybrid Parallelism

Modern large-scale training combines multiple parallelism strategies.

### 3D Parallelism Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    3D Parallelism (Example)                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Model: 100B parameters, 64 layers                           │
│  Cluster: 512 GPUs (64 nodes × 8 GPUs/node)                 │
│                                                               │
│  Strategy:                                                    │
│  - Tensor Parallel (TP): 8-way (within node, NVLink)        │
│  - Pipeline Parallel (PP): 8-way (across nodes, IB)         │
│  - Data Parallel (DP): 8-way (across nodes, IB)             │
│                                                               │
│  Total: 8 (TP) × 8 (PP) × 8 (DP) = 512 GPUs                 │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Data Parallel Group 0 (8 nodes)                      │  │
│  │                                                        │  │
│  │  Node 0 (8 GPUs with NVLink - TP group)              │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Layers 1-8  │ [GPU0][GPU1]...[GPU7]          │    │  │
│  │  │ (PP stage 0)│  Each GPU has 1/8 of layer     │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │        ↓ (Pipeline)                                   │  │
│  │  Node 1 (8 GPUs with NVLink - TP group)              │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Layers 9-16 │ [GPU8][GPU9]...[GPU15]         │    │  │
│  │  │ (PP stage 1)│  Each GPU has 1/8 of layer     │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │        ↓ (Pipeline)                                   │  │
│  │       ...                                             │  │
│  │        ↓ (Pipeline)                                   │  │
│  │  Node 7 (8 GPUs with NVLink - TP group)              │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │ Layers 57-64│ [GPU56][GPU57]...[GPU63]       │    │  │
│  │  │ (PP stage 7)│  Each GPU has 1/8 of layer     │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│         ↕ (Data Parallel - gradient synchronization)         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Data Parallel Group 1 (8 nodes)                      │  │
│  │  ... (same structure, different data)                 │  │
│  └────────────────────────────────────────────────────────┘  │
│         ↕                                                     │
│       ...                                                     │
│         ↕                                                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Data Parallel Group 7 (8 nodes)                      │  │
│  │  ... (same structure, different data)                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Hybrid Parallelism Configuration

```python
from dataclasses import dataclass

@dataclass
class ParallelismConfig:
    """Configuration for hybrid parallelism"""

    # Parallelism degrees
    tensor_parallel_size: int = 1
    pipeline_parallel_size: int = 1
    data_parallel_size: int = 1

    # Must satisfy: TP × PP × DP = total_gpus

    # Advanced options
    virtual_pipeline_stages: int = None  # For interleaved pipeline
    sequence_parallel: bool = False      # Sequence parallelism
    zero_stage: int = 0                  # ZeRO optimization stage

    def validate(self, total_gpus):
        """Validate configuration"""
        total = (self.tensor_parallel_size *
                self.pipeline_parallel_size *
                self.data_parallel_size)

        if total != total_gpus:
            raise ValueError(
                f"Parallelism config ({total}) doesn't match "
                f"total GPUs ({total_gpus})"
            )

        return True

    def get_topology(self):
        """Return parallelism topology description"""
        return {
            'tensor_parallel': self.tensor_parallel_size,
            'pipeline_parallel': self.pipeline_parallel_size,
            'data_parallel': self.data_parallel_size,
            'total_gpus': (self.tensor_parallel_size *
                          self.pipeline_parallel_size *
                          self.data_parallel_size),
        }

# Example configurations for different scales
def get_parallelism_config(model_size, total_gpus):
    """
    Recommend parallelism configuration based on model size and resources

    Rules of thumb:
    - Tensor parallel within node (8 GPUs max, NVLink)
    - Pipeline parallel across nodes
    - Data parallel for scaling
    """
    # TODO: Implement configuration logic

    if model_size < 1e9:  # < 1B parameters
        # Small model - only data parallelism
        return ParallelismConfig(
            tensor_parallel_size=1,
            pipeline_parallel_size=1,
            data_parallel_size=total_gpus,
        )

    elif model_size < 10e9:  # 1B-10B parameters
        # Medium model - TP + DP
        tp_size = min(8, total_gpus)
        dp_size = total_gpus // tp_size
        return ParallelismConfig(
            tensor_parallel_size=tp_size,
            pipeline_parallel_size=1,
            data_parallel_size=dp_size,
        )

    elif model_size < 100e9:  # 10B-100B parameters
        # Large model - full 3D parallelism
        tp_size = 8  # Within node
        pp_size = min(8, total_gpus // 8)
        dp_size = total_gpus // (tp_size * pp_size)
        return ParallelismConfig(
            tensor_parallel_size=tp_size,
            pipeline_parallel_size=pp_size,
            data_parallel_size=dp_size,
        )

    else:  # > 100B parameters
        # Very large model - aggressive parallelism
        tp_size = 8
        pp_size = total_gpus // (8 * 8)  # Leave room for DP
        dp_size = 8
        return ParallelismConfig(
            tensor_parallel_size=tp_size,
            pipeline_parallel_size=pp_size,
            data_parallel_size=dp_size,
            virtual_pipeline_stages=2,  # Reduce bubble
            sequence_parallel=True,
        )

# Example usage
configs = [
    (1e9, 8),     # 1B model, 8 GPUs
    (13e9, 64),   # 13B model, 64 GPUs
    (70e9, 256),  # 70B model, 256 GPUs
    (175e9, 1024), # 175B model, 1024 GPUs
]

print("Recommended Parallelism Configurations:\n")
for model_size, gpus in configs:
    config = get_parallelism_config(model_size, gpus)
    print(f"Model: {model_size/1e9:.0f}B params, GPUs: {gpus}")
    print(f"  Configuration: {config.get_topology()}")
    print()
```

## Gradient Synchronization Strategies

### Synchronous vs Asynchronous Training

```python
# Synchronous Data Parallel Training
def synchronous_training_step(model, batch, optimizer):
    """
    Standard synchronous training step
    All workers must finish before continuing
    """
    # Forward pass
    output = model(batch['input'])
    loss = compute_loss(output, batch['target'])

    # Backward pass
    optimizer.zero_grad()
    loss.backward()

    # SYNCHRONIZATION POINT: AllReduce gradients
    # All workers wait here until everyone finishes
    # Gradients are averaged across all workers
    for param in model.parameters():
        if param.grad is not None:
            dist.all_reduce(param.grad, op=dist.ReduceOp.AVG)

    # All workers have identical gradients now
    optimizer.step()

    return loss.item()

# Asynchronous Training (parameter server)
class ParameterServer:
    """
    Asynchronous training with parameter server
    Workers update parameters independently
    """

    def __init__(self, model):
        self.parameters = {
            name: param.data.clone()
            for name, param in model.named_parameters()
        }
        self.lock = threading.Lock()

    def push_gradients(self, gradients, learning_rate):
        """
        Worker pushes gradients to update parameters
        No waiting for other workers!
        """
        with self.lock:
            for name, grad in gradients.items():
                # TODO: Apply gradient update
                self.parameters[name] -= learning_rate * grad

    def pull_parameters(self):
        """Worker pulls latest parameters"""
        with self.lock:
            return {
                name: param.clone()
                for name, param in self.parameters.items()
            }

def asynchronous_worker_step(model, batch, optimizer, param_server):
    """
    Asynchronous training step
    Worker proceeds independently
    """
    # Pull latest parameters
    latest_params = param_server.pull_parameters()
    for name, param in model.named_parameters():
        param.data = latest_params[name]

    # Compute gradients
    output = model(batch['input'])
    loss = compute_loss(output, batch['target'])
    optimizer.zero_grad()
    loss.backward()

    # Push gradients (non-blocking)
    gradients = {
        name: param.grad.clone()
        for name, param in model.named_parameters()
        if param.grad is not None
    }
    param_server.push_gradients(gradients, optimizer.defaults['lr'])

    # Continue to next batch immediately!
    return loss.item()
```

### Gradient Accumulation

```python
def train_with_gradient_accumulation(
    model,
    dataloader,
    optimizer,
    accumulation_steps=4
):
    """
    Training with gradient accumulation
    Simulates larger batch size without memory increase

    Args:
        accumulation_steps: Number of micro-batches to accumulate
    """
    model.train()
    optimizer.zero_grad()

    total_loss = 0

    for batch_idx, batch in enumerate(dataloader):
        # Forward pass
        output = model(batch['input'])
        loss = compute_loss(output, batch['target'])

        # Scale loss by accumulation steps
        loss = loss / accumulation_steps

        # Backward pass (accumulate gradients)
        loss.backward()

        total_loss += loss.item()

        # Update weights every accumulation_steps
        if (batch_idx + 1) % accumulation_steps == 0:
            # TODO: Perform gradient synchronization (if distributed)
            # TODO: Clip gradients if needed
            # TODO: Optimizer step
            # TODO: Zero gradients

            # Synchronize gradients across all workers
            for param in model.parameters():
                if param.grad is not None:
                    dist.all_reduce(param.grad, op=dist.ReduceOp.SUM)
                    param.grad /= dist.get_world_size()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            # Optimizer step
            optimizer.step()
            optimizer.zero_grad()

            if batch_idx % 100 == 0:
                print(f"Batch {batch_idx}, Loss: {total_loss:.4f}")
                total_loss = 0

    return total_loss

# Benefits of gradient accumulation:
# 1. Simulate larger batch sizes without memory increase
# 2. Reduce communication frequency in distributed training
# 3. Improve throughput when communication is bottleneck
```

## Scaling Laws and Efficiency Metrics

### Strong Scaling vs Weak Scaling

```python
def measure_scaling_efficiency():
    """
    Measure strong scaling (fixed problem size) and
    weak scaling (problem size grows with resources)
    """

    # Strong Scaling: Fixed total batch size
    # Ideal: time(N GPUs) = time(1 GPU) / N
    strong_scaling = {
        'gpus': [1, 2, 4, 8, 16, 32],
        'time_per_epoch': [1000, 520, 270, 145, 80, 50],  # seconds
    }

    # Calculate strong scaling efficiency
    baseline = strong_scaling['time_per_epoch'][0]
    for n_gpus, time in zip(strong_scaling['gpus'],
                            strong_scaling['time_per_epoch']):
        ideal_time = baseline / n_gpus
        efficiency = (ideal_time / time) * 100
        speedup = baseline / time
        print(f"{n_gpus:2d} GPUs: {time:4.0f}s, "
              f"Speedup: {speedup:5.2f}x, "
              f"Efficiency: {efficiency:5.1f}%")

    print("\nWeak Scaling: Batch size grows with GPUs")
    # Weak Scaling: Batch size per GPU constant
    # Ideal: time stays constant as we add GPUs
    weak_scaling = {
        'gpus': [1, 2, 4, 8, 16, 32],
        'batch_per_gpu': 32,  # constant
        'time_per_epoch': [1000, 1020, 1050, 1100, 1180, 1300],  # seconds
    }

    baseline = weak_scaling['time_per_epoch'][0]
    for n_gpus, time in zip(weak_scaling['gpus'],
                            weak_scaling['time_per_epoch']):
        efficiency = (baseline / time) * 100
        total_batch = n_gpus * weak_scaling['batch_per_gpu']
        print(f"{n_gpus:2d} GPUs (batch {total_batch:4d}): {time:4.0f}s, "
              f"Efficiency: {efficiency:5.1f}%")

# Scaling efficiency breakdown
def analyze_scaling_bottlenecks(
    compute_time,
    communication_time,
    n_gpus
):
    """
    Analyze what limits scaling efficiency

    Args:
        compute_time: Time spent in computation
        communication_time: Time spent in communication
        n_gpus: Number of GPUs
    """
    total_time = compute_time + communication_time

    # Communication typically grows with log(N) for AllReduce
    # or linearly for parameter server
    communication_fraction = communication_time / total_time
    compute_fraction = compute_time / total_time

    print(f"\nScaling Analysis ({n_gpus} GPUs):")
    print(f"  Compute time: {compute_time:.2f}s ({compute_fraction*100:.1f}%)")
    print(f"  Communication time: {communication_time:.2f}s "
          f"({communication_fraction*100:.1f}%)")
    print(f"  Total time: {total_time:.2f}s")

    # Maximum achievable speedup (Amdahl's Law)
    # Assuming communication doesn't parallelize
    max_speedup = 1 / (communication_fraction + compute_fraction / n_gpus)

    print(f"  Max theoretical speedup: {max_speedup:.2f}x")
    print(f"  Communication overhead: {communication_fraction*100:.1f}%")

    if communication_fraction > 0.3:
        print("  ⚠ WARNING: Communication is bottleneck!")
        print("  Suggestions:")
        print("    - Use gradient accumulation")
        print("    - Optimize network (InfiniBand, RDMA)")
        print("    - Use gradient compression")
        print("    - Increase batch size per GPU")

# Example: Analyze different scenarios
print("Scenario 1: Small model, fast network")
analyze_scaling_bottlenecks(
    compute_time=90,
    communication_time=10,
    n_gpus=8
)

print("\nScenario 2: Large model, slow network")
analyze_scaling_bottlenecks(
    compute_time=60,
    communication_time=40,
    n_gpus=8
)
```

## Communication Patterns

### AllReduce

AllReduce is the most common collective operation in distributed training:

```python
def simulate_allreduce_time(
    tensor_size_mb,
    bandwidth_gbps,
    n_gpus,
    algorithm='ring'
):
    """
    Estimate AllReduce communication time

    Args:
        tensor_size_mb: Size of tensor in megabytes
        bandwidth_gbps: Network bandwidth in Gbps
        n_gpus: Number of GPUs
        algorithm: 'ring' or 'tree'

    Returns:
        Time in milliseconds
    """
    tensor_size_gb = tensor_size_mb / 1024

    if algorithm == 'ring':
        # Ring AllReduce: 2(N-1)/N data transfer
        # Bandwidth optimal: (N-1)/N ≈ 1 for large N
        steps = 2 * (n_gpus - 1)
        data_per_step = tensor_size_gb / n_gpus
        time_per_step = (data_per_step / bandwidth_gbps) * 1000  # ms
        total_time = steps * time_per_step

    elif algorithm == 'tree':
        # Tree AllReduce: 2*log2(N) steps
        # Not bandwidth optimal but lower latency
        import math
        steps = 2 * math.ceil(math.log2(n_gpus))
        time_per_step = (tensor_size_gb / bandwidth_gbps) * 1000  # ms
        total_time = steps * time_per_step

    return total_time

# Compare communication time for different configurations
print("AllReduce Time Comparison:\n")
configs = [
    (100, 100, 8, 'ring'),    # 100MB tensor, 100Gbps, 8 GPUs, ring
    (100, 100, 8, 'tree'),    # tree algorithm
    (100, 400, 8, 'ring'),    # NVLink (400Gbps)
    (1000, 100, 8, 'ring'),   # 1GB tensor
    (100, 100, 64, 'ring'),   # More GPUs
]

for tensor_size, bandwidth, n_gpus, algo in configs:
    time_ms = simulate_allreduce_time(tensor_size, bandwidth, n_gpus, algo)
    print(f"{tensor_size:4d}MB, {bandwidth:3d}Gbps, {n_gpus:2d} GPUs, "
          f"{algo:4s}: {time_ms:6.2f}ms")
```

## Practical Considerations

### Memory Requirements

```python
def estimate_memory_per_gpu(
    model_params,
    batch_size_per_gpu,
    sequence_length,
    hidden_size,
    n_layers,
    optimizer='adam',
    mixed_precision=False,
    activation_checkpointing=False,
):
    """
    Estimate memory requirements per GPU

    Returns memory in GB
    """
    # Model parameters
    if mixed_precision:
        param_memory = model_params * 2 / 1e9  # FP16: 2 bytes
    else:
        param_memory = model_params * 4 / 1e9  # FP32: 4 bytes

    # Gradients (same size as parameters)
    grad_memory = param_memory

    # Optimizer states
    if optimizer == 'adam':
        # Adam: 2 states (momentum, variance) in FP32
        optimizer_memory = model_params * 8 / 1e9
    elif optimizer == 'sgd':
        # SGD with momentum: 1 state
        optimizer_memory = model_params * 4 / 1e9
    else:
        optimizer_memory = 0

    # Activations (largest memory consumer!)
    # Approximate: batch_size * seq_len * hidden_size * n_layers * 4 (FP32)
    # * 2 for storing intermediate activations
    if activation_checkpointing:
        # Only store √n_layers activations
        import math
        activation_memory = (batch_size_per_gpu * sequence_length *
                           hidden_size * math.sqrt(n_layers) * 4 * 2 / 1e9)
    else:
        activation_memory = (batch_size_per_gpu * sequence_length *
                           hidden_size * n_layers * 4 * 2 / 1e9)

    # Total
    total_memory = (param_memory + grad_memory +
                   optimizer_memory + activation_memory)

    print(f"Memory Breakdown:")
    print(f"  Parameters:  {param_memory:6.2f} GB")
    print(f"  Gradients:   {grad_memory:6.2f} GB")
    print(f"  Optimizer:   {optimizer_memory:6.2f} GB")
    print(f"  Activations: {activation_memory:6.2f} GB")
    print(f"  Total:       {total_memory:6.2f} GB")

    return total_memory

# Example: GPT-3 175B
print("GPT-3 175B Memory Requirements:\n")
memory = estimate_memory_per_gpu(
    model_params=175e9,
    batch_size_per_gpu=1,
    sequence_length=2048,
    hidden_size=12288,
    n_layers=96,
    optimizer='adam',
    mixed_precision=True,
    activation_checkpointing=False,
)
print(f"\nA100 80GB: {'✓ Fits' if memory < 80 else '✗ Does not fit'}\n")

# With activation checkpointing
print("With Activation Checkpointing:")
memory_opt = estimate_memory_per_gpu(
    model_params=175e9,
    batch_size_per_gpu=1,
    sequence_length=2048,
    hidden_size=12288,
    n_layers=96,
    optimizer='adam',
    mixed_precision=True,
    activation_checkpointing=True,
)
print(f"\nA100 80GB: {'✓ Fits' if memory_opt < 80 else '✗ Does not fit'}")
```

## Summary

Key takeaways from distributed training fundamentals:

1. **Data Parallelism**: Simple, works for models that fit on one GPU. Communication grows with model size.

2. **Model Parallelism**: Necessary for large models. Naive approach is inefficient due to pipeline bubbles.

3. **Pipeline Parallelism**: Improves model parallelism with micro-batching. Requires many micro-batches for efficiency.

4. **Tensor Parallelism**: Fine-grained parallelism within layers. Requires fast interconnect. Best for large hidden dimensions.

5. **Hybrid Parallelism**: Combining strategies is essential for modern large-scale training. 3D parallelism (TP+PP+DP) enables training models with trillions of parameters.

6. **Scaling Laws**: Understanding strong vs weak scaling helps optimize resource utilization. Communication overhead is the main bottleneck.

## Further Reading

- "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism" (Shoeybi et al., 2019)
- "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism" (Huang et al., 2019)
- "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" (Rajbhandari et al., 2020)
- PyTorch Distributed Training Documentation

## Next Steps

Continue to `02-ray-framework.md` to learn about Ray, a powerful framework for distributed training that simplifies many of these concepts.
