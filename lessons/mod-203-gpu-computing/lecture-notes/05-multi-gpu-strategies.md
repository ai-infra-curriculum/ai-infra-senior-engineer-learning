# Lecture 05: Multi-GPU Strategies and Parallel Training

## Learning Objectives

By the end of this lecture, you will be able to:

- Design distributed training architectures that combine data parallelism, model parallelism, pipeline parallelism, and tensor parallelism for training models that exceed single-GPU capacity
- Implement PyTorch DistributedDataParallel (DDP) and FSDP (Fully Sharded Data Parallel) for efficient multi-node training with optimal gradient synchronization strategies
- Configure NCCL collective operations (AllReduce, Broadcast, ReduceScatter) with proper topology awareness and tuning parameters to minimize communication overhead
- Architect hybrid parallelism strategies (3D parallelism) for training large language models (100B+ parameters) using frameworks like Megatron-LM and DeepSpeed
- Evaluate scaling efficiency metrics (strong scaling, weak scaling) and identify sources of scaling overhead to optimize multi-GPU training performance
- Implement gradient accumulation, gradient compression, and communication-computation overlap techniques to reduce communication bottlenecks in distributed training
- Design fault-tolerant multi-GPU training systems with proper checkpoint strategies and elastic training capabilities for production reliability
- Troubleshoot common multi-GPU issues including NCCL timeouts, imbalanced GPU utilization, and network bandwidth limitations using profiling and monitoring tools

## Table of Contents
1. [Introduction to Multi-GPU Training](#introduction-to-multi-gpu-training)
2. [Data Parallelism](#data-parallelism)
3. [Model Parallelism](#model-parallelism)
4. [Pipeline Parallelism](#pipeline-parallelism)
5. [Hybrid Parallelism](#hybrid-parallelism)
6. [NVLink and GPU Interconnects](#nvlink-and-gpu-interconnects)
7. [NCCL for Collective Communications](#nccl-for-collective-communications)
8. [Scaling Efficiency](#scaling-efficiency)

## Introduction to Multi-GPU Training

As models grow larger, single-GPU training becomes insufficient. Multi-GPU strategies enable training larger models faster.

### Why Multi-GPU?

1. **Faster Training**: Linear or near-linear speedup with more GPUs
2. **Larger Models**: Distribute model across multiple GPUs
3. **Larger Batches**: Increase effective batch size
4. **Production Requirements**: Handle more inference requests
5. **Cost Efficiency**: Train in hours instead of days/weeks

### Parallelism Strategies

```
Strategy Comparison:

Data Parallelism:
GPU 0: [Full Model] → Batch 0
GPU 1: [Full Model] → Batch 1
GPU 2: [Full Model] → Batch 2
GPU 3: [Full Model] → Batch 3
└─ Sync gradients

Model Parallelism:
GPU 0: [Layer 1-5]  ┐
GPU 1: [Layer 6-10] ├─ Same batch flows through
GPU 2: [Layer 11-15]┤
GPU 3: [Layer 16-20]┘

Pipeline Parallelism:
GPU 0: [Layer 1-5]  → Micro-batch 0, 4, 8
GPU 1: [Layer 6-10] → Micro-batch 1, 5, 9
GPU 2: [Layer 11-15]→ Micro-batch 2, 6, 10
GPU 3: [Layer 16-20]→ Micro-batch 3, 7, 11
```

### Scaling Challenges

1. **Communication Overhead**: GPUs must synchronize
2. **Load Balancing**: Keep all GPUs equally busy
3. **Memory Constraints**: Large models may not fit in GPU memory
4. **Software Complexity**: More complex training code
5. **Debugging**: Harder to debug distributed training

## Data Parallelism

Data parallelism replicates the model on each GPU and processes different batches.

### How Data Parallelism Works

```
Step 1: Replicate model on each GPU
Step 2: Split batch across GPUs
Step 3: Forward pass (parallel, no communication)
Step 4: Compute loss and gradients (parallel)
Step 5: All-reduce gradients across GPUs
Step 6: Update model parameters (synchronized)
```

### PyTorch DataParallel (Legacy)

```python
import torch
import torch.nn as nn

# Simple DataParallel (single-process, not recommended)
model = MyModel()
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
model = model.cuda()

# Training loop (same as single GPU)
for data, target in dataloader:
    output = model(data.cuda())
    loss = criterion(output, target.cuda())
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

**Limitations of DataParallel:**
- Single-process: Python GIL limits parallelism
- Unbalanced GPU utilization (GPU 0 does more work)
- No support for multiple nodes
- Inefficient for large models

### PyTorch DistributedDataParallel (Recommended)

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup(rank, world_size):
    """Initialize the distributed environment"""
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    """Clean up distributed environment"""
    dist.destroy_process_group()

def train(rank, world_size):
    """Training function for each process"""
    print(f"Running DDP on rank {rank}")
    setup(rank, world_size)

    # Create model and move to GPU
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])

    # Create optimizer
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.01)

    # Create distributed sampler
    dataset = MyDataset()
    sampler = DistributedSampler(
        dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True
    )
    dataloader = DataLoader(
        dataset,
        batch_size=32,
        sampler=sampler,
        num_workers=4,
        pin_memory=True
    )

    # Training loop
    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)  # Shuffle differently each epoch

        for data, target in dataloader:
            data, target = data.to(rank), target.to(rank)

            # Forward pass
            output = ddp_model(data)
            loss = criterion(output, target)

            # Backward pass (gradients automatically all-reduced)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    cleanup()

def main():
    world_size = torch.cuda.device_count()
    mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)

if __name__ == "__main__":
    main()
```

### DDP with torchrun (Recommended for Multi-Node)

```python
# train_ddp.py
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def main():
    # torchrun sets these environment variables
    dist.init_process_group(backend="nccl")

    local_rank = int(os.environ["LOCAL_RANK"])
    global_rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])

    torch.cuda.set_device(local_rank)

    # Create model
    model = MyModel().to(local_rank)
    ddp_model = DDP(model, device_ids=[local_rank])

    # Training loop
    for epoch in range(num_epochs):
        train_one_epoch(ddp_model, dataloader, optimizer, local_rank)

    dist.destroy_process_group()

if __name__ == "__main__":
    main()
```

```bash
# Single node, 4 GPUs
torchrun --nproc_per_node=4 train_ddp.py

# Multi-node: 2 nodes, 8 GPUs each (16 total)
# Node 0 (master):
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=0 \
    --master_addr="192.168.1.1" --master_port=12355 train_ddp.py

# Node 1:
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=1 \
    --master_addr="192.168.1.1" --master_port=12355 train_ddp.py
```

### Gradient Accumulation for Large Batches

Simulate larger batch sizes without OOM:

```python
accumulation_steps = 4  # Effective batch size = batch_size * accumulation_steps

for batch_idx, (data, target) in enumerate(dataloader):
    output = model(data)
    loss = criterion(output, target)

    # Scale loss by accumulation steps
    loss = loss / accumulation_steps
    loss.backward()

    # Update weights every accumulation_steps
    if (batch_idx + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### DDP Best Practices

1. **Use NCCL backend** for multi-GPU (fastest)
2. **Enable gradient bucketing** (default in DDP)
3. **Use DistributedSampler** to split data
4. **Synchronize batch norm** across GPUs if needed
5. **Save checkpoints on rank 0 only**

```python
# Synchronized batch norm (if needed)
model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)
ddp_model = DDP(model, device_ids=[rank])

# Save checkpoint (rank 0 only)
if rank == 0:
    torch.save({
        'epoch': epoch,
        'model_state_dict': ddp_model.module.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, 'checkpoint.pth')

# TODO: Implement distributed validation
# Only rank 0 should print/log metrics
```

## Model Parallelism

Model parallelism splits the model across multiple GPUs when it's too large for a single GPU.

### Naive Model Parallelism

```python
import torch
import torch.nn as nn

class ModelParallelResNet(nn.Module):
    def __init__(self):
        super(ModelParallelResNet, self).__init__()
        # Put first half on GPU 0
        self.seq1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3)
        ).to('cuda:0')

        # Put second half on GPU 1
        self.seq2 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, 1000)
        ).to('cuda:1')

    def forward(self, x):
        # Move through pipeline
        x = self.seq1(x.to('cuda:0'))
        x = self.seq2(x.to('cuda:1'))
        return x

# Usage
model = ModelParallelResNet()
input_data = torch.randn(32, 3, 224, 224)  # On CPU
output = model(input_data)  # Automatically moved through GPUs
```

**Problem with Naive Approach:**
```
GPU 0: [████       ] Forward on seq1
GPU 1: [    ████   ] Wait for GPU 0, then forward on seq2
       └─ Only one GPU active at a time!
```

### Tensor Parallelism (Megatron-LM Style)

Split individual tensors across GPUs:

```python
# Conceptual example of tensor parallelism for transformer
class ColumnParallelLinear(nn.Module):
    """Linear layer with column parallelism"""
    def __init__(self, in_features, out_features, world_size):
        super().__init__()
        self.in_features = in_features
        self.out_features_per_partition = out_features // world_size
        self.weight = nn.Parameter(
            torch.randn(self.out_features_per_partition, in_features)
        )

    def forward(self, x):
        # Each GPU computes part of the output
        output_parallel = F.linear(x, self.weight)
        # All-gather to get full output
        output = gather_from_model_parallel_region(output_parallel)
        return output

class RowParallelLinear(nn.Module):
    """Linear layer with row parallelism"""
    def __init__(self, in_features, out_features, world_size):
        super().__init__()
        self.in_features_per_partition = in_features // world_size
        self.out_features = out_features
        self.weight = nn.Parameter(
            torch.randn(out_features, self.in_features_per_partition)
        )

    def forward(self, x):
        # Input is already split across GPUs
        output_parallel = F.linear(x, self.weight)
        # All-reduce to sum partial results
        output = reduce_from_model_parallel_region(output_parallel)
        return output

# Transformer MLP with tensor parallelism
class ParallelMLP(nn.Module):
    def __init__(self, hidden_size, world_size):
        super().__init__()
        # First linear: split output across GPUs
        self.dense_h_to_4h = ColumnParallelLinear(
            hidden_size, 4 * hidden_size, world_size
        )
        # Second linear: split input across GPUs
        self.dense_4h_to_h = RowParallelLinear(
            4 * hidden_size, hidden_size, world_size
        )

    def forward(self, x):
        # Each GPU computes part of the MLP
        x = self.dense_h_to_4h(x)
        x = F.gelu(x)
        x = self.dense_4h_to_h(x)
        return x
```

### Megatron-LM Example

```bash
# Clone Megatron-LM
git clone https://github.com/NVIDIA/Megatron-LM.git
cd Megatron-LM

# Train GPT model with tensor and pipeline parallelism
python pretrain_gpt.py \
    --tensor-model-parallel-size 4 \
    --pipeline-model-parallel-size 2 \
    --num-layers 24 \
    --hidden-size 1024 \
    --num-attention-heads 16 \
    --micro-batch-size 4 \
    --global-batch-size 32 \
    --seq-length 1024 \
    --max-position-embeddings 1024 \
    --train-iters 500000 \
    --lr-decay-iters 320000 \
    --data-path my-gpt-dataset \
    --vocab-file gpt-vocab.json \
    --merge-file gpt-merges.txt \
    --save checkpoints/gpt \
    --load checkpoints/gpt \
    --distributed-backend nccl

# This uses 4 * 2 = 8 GPUs total
```

## Pipeline Parallelism

Pipeline parallelism divides model into stages and processes multiple micro-batches concurrently.

### Naive Pipeline (GPipe Style)

```python
from torch.distributed.pipeline.sync import Pipe

# Split model into stages
class ModelStage1(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1000, 1000),
            nn.ReLU(),
            nn.Linear(1000, 1000),
            nn.ReLU()
        )

    def forward(self, x):
        return self.layers(x)

class ModelStage2(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1000, 1000),
            nn.ReLU(),
            nn.Linear(1000, 100)
        )

    def forward(self, x):
        return self.layers(x)

# Create pipeline
model = nn.Sequential(
    ModelStage1().to('cuda:0'),
    ModelStage2().to('cuda:1')
)

# Wrap with Pipe for pipeline parallelism
model = Pipe(model, chunks=8)  # Split batch into 8 micro-batches

# Training
for data, target in dataloader:
    output = model(data.to('cuda:0'))
    loss = criterion(output.to('cuda:1'), target.to('cuda:1'))
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

### Pipeline Schedule

```
Without Pipelining (Naive):
GPU 0: [F0] [B0] [F1] [B1] [F2] [B2] [F3] [B3]
GPU 1:      [F0] [B0] [F1] [B1] [F2] [B2] [F3] [B3]
       └─ GPU 0 idle while GPU 1 works

With Pipelining (GPipe):
GPU 0: [F0][F1][F2][F3][B0][B1][B2][B3]
GPU 1:     [F0][F1][F2][F3][B0][B1][B2][B3]
       └─ Better overlap, but still bubbles

With Pipelining (PipeDream):
GPU 0: [F0][F1][F2][F3][B3][B2][B1][B0]
GPU 1:  [F0][F1][F2][F3][B3][B2][B1][B0]
       └─ Reduced bubbles

F = Forward, B = Backward
```

### DeepSpeed Pipeline

```python
from deepspeed.pipe import PipelineModule, LayerSpec

# Define model as list of layers
layers = [
    LayerSpec(nn.Linear, 1000, 1000),
    LayerSpec(nn.ReLU),
    LayerSpec(nn.Linear, 1000, 1000),
    LayerSpec(nn.ReLU),
    LayerSpec(nn.Linear, 1000, 1000),
    LayerSpec(nn.ReLU),
    LayerSpec(nn.Linear, 1000, 100)
]

# Create pipeline model (automatically partitions across GPUs)
model = PipelineModule(
    layers=layers,
    num_stages=2,  # Number of pipeline stages
    loss_fn=nn.CrossEntropyLoss()
)

# DeepSpeed config
ds_config = {
    "train_batch_size": 32,
    "train_micro_batch_size_per_gpu": 4,  # Batch split into micro-batches
    "steps_per_print": 100,
    "optimizer": {
        "type": "Adam",
        "params": {"lr": 0.001}
    }
}

# Initialize DeepSpeed engine
model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    model_parameters=model.parameters(),
    config=ds_config
)

# Training
for data, target in dataloader:
    loss = model_engine(data, target)
    model_engine.backward(loss)
    model_engine.step()
```

## Hybrid Parallelism

Combine data, model, and pipeline parallelism for maximum scale.

### 3D Parallelism (Megatron + DeepSpeed)

```
Example: Train GPT-3 (175B parameters) on 1024 GPUs

3D Parallelism:
- Data Parallelism: 32 groups
- Pipeline Parallelism: 16 stages
- Tensor Parallelism: 2 ways

Total GPUs: 32 * 16 * 2 = 1024 GPUs

Each GPU has:
- 1/2 of tensor (tensor parallel)
- 1/16 of layers (pipeline parallel)
- 1/32 of batch (data parallel)
```

### PyTorch FSDP (Fully Sharded Data Parallel)

FSDP shards model parameters, gradients, and optimizer states:

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy

# Initialize process group
dist.init_process_group(backend="nccl")

# Create model
model = MyLargeModel()

# Wrap with FSDP (automatically shards model)
auto_wrap_policy = size_based_auto_wrap_policy(min_num_params=1e6)
model = FSDP(
    model,
    auto_wrap_policy=auto_wrap_policy,
    mixed_precision=True,
    sharding_strategy="FULL_SHARD",  # Shard params, grads, optimizer
    device_id=torch.cuda.current_device()
)

# Training (same as regular PyTorch)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for data, target in dataloader:
    output = model(data)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

# FSDP automatically:
# 1. Gathers parameters for forward/backward
# 2. Shards gradients
# 3. Reduces gradients across ranks
# 4. Shards optimizer state
```

**FSDP vs DDP:**
- DDP: Replicates full model on each GPU
- FSDP: Shards model across GPUs
- FSDP uses less memory per GPU
- FSDP can train larger models

## NVLink and GPU Interconnects

### GPU Interconnects Comparison

**PCIe:**
- 16-32 GB/s bandwidth (PCIe 4.0/5.0)
- Goes through CPU
- Higher latency
- Standard on all GPUs

**NVLink:**
- 300-900 GB/s bandwidth (total)
- Direct GPU-to-GPU connection
- Lower latency
- Available on data center GPUs

**NVSwitch:**
- Enables full NVLink bandwidth between all GPUs
- Up to 64 GPUs fully connected
- Used in DGX systems

### NVLink Topology

```bash
# Check NVLink topology
nvidia-smi topo -m

# Example output for DGX A100:
#       GPU0  GPU1  GPU2  GPU3  GPU4  GPU5  GPU6  GPU7
# GPU0   X    NV12  NV12  NV12  NV12  NV12  NV12  NV12
# GPU1  NV12   X    NV12  NV12  NV12  NV12  NV12  NV12
# GPU2  NV12  NV12   X    NV12  NV12  NV12  NV12  NV12
# ...
# NV12 = NVLink (12 links)
```

### Testing NVLink Bandwidth

```python
import torch

def test_nvlink_bandwidth(size_mb=1000):
    """Test GPU-to-GPU bandwidth"""
    size = size_mb * 1024 * 1024 // 4  # Convert MB to float count

    # Create tensors on GPU 0 and 1
    tensor0 = torch.randn(size).cuda(0)
    tensor1 = torch.zeros(size).cuda(1)

    # Warm up
    for _ in range(10):
        tensor1.copy_(tensor0)
    torch.cuda.synchronize()

    # Measure bandwidth
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()
    for _ in range(100):
        tensor1.copy_(tensor0)
    end.record()
    torch.cuda.synchronize()

    elapsed_ms = start.elapsed_time(end)
    bandwidth_gb_s = (size_mb * 100) / (elapsed_ms / 1000) / 1024

    print(f"GPU-to-GPU bandwidth: {bandwidth_gb_s:.2f} GB/s")

# Test bandwidth
test_nvlink_bandwidth()

# Expected:
# - With NVLink: 200-300 GB/s
# - Without NVLink (PCIe): 10-20 GB/s
```

## NCCL for Collective Communications

### NCCL Operations

**All-Reduce**: Most common in data parallel training
```python
# Sum gradients from all GPUs, result on all GPUs
tensor = torch.randn(1000).cuda()
dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
```

**Broadcast**: Send data from one GPU to all
```python
# Broadcast from rank 0 to all ranks
tensor = torch.randn(1000).cuda() if rank == 0 else torch.zeros(1000).cuda()
dist.broadcast(tensor, src=0)
```

**All-Gather**: Gather data from all GPUs to all GPUs
```python
# Each rank contributes tensor, all ranks get concatenated result
tensor = torch.randn(100).cuda() * rank  # Different value per rank
tensor_list = [torch.zeros(100).cuda() for _ in range(world_size)]
dist.all_gather(tensor_list, tensor)
# tensor_list now contains tensors from all ranks
```

**Reduce-Scatter**: Reduce and scatter results
```python
# Sum across ranks, scatter result
input_tensor = torch.randn(world_size, 100).cuda()
output_tensor = torch.zeros(100).cuda()
dist.reduce_scatter(output_tensor, list(input_tensor))
```

### NCCL Performance Tuning

```bash
# Environment variables for NCCL tuning

# Use all NVLink bandwidth
export NCCL_P2P_LEVEL=NVL

# Algorithm selection (auto, tree, ring)
export NCCL_ALGO=Tree

# Number of channels (parallel streams)
export NCCL_NCHANNELS_PER_NET_PEER=4

# Debug mode (verbose logging)
export NCCL_DEBUG=INFO

# Network interface
export NCCL_SOCKET_IFNAME=eth0
```

## Scaling Efficiency

### Measuring Scaling Efficiency

```python
def measure_scaling_efficiency():
    """Measure strong and weak scaling"""
    world_size = dist.get_world_size()

    # Strong scaling: fixed problem size, increase GPUs
    batch_size = 256  # Total batch size fixed
    per_gpu_batch = batch_size // world_size

    # Weak scaling: problem size scales with GPUs
    # per_gpu_batch = 32  # Per-GPU batch size fixed

    # Measure throughput
    torch.cuda.synchronize()
    start_time = time.time()

    for _ in range(100):
        train_step(model, dataloader, optimizer)

    torch.cuda.synchronize()
    elapsed = time.time() - start_time

    samples_per_sec = (100 * batch_size) / elapsed

    if dist.get_rank() == 0:
        print(f"GPUs: {world_size}, Throughput: {samples_per_sec:.2f} samples/sec")
        if world_size > 1:
            efficiency = samples_per_sec / (baseline_throughput * world_size)
            print(f"Scaling efficiency: {efficiency:.2%}")

# TODO: Implement and measure scaling on 2, 4, 8 GPUs
```

### Theoretical Speedup

```
Ideal Speedup: S = N (linear with N GPUs)

Actual Speedup: S = N / (1 + C)
where C = Communication Overhead / Computation Time

Example:
- Computation: 100ms per iteration
- Communication: 10ms all-reduce
- C = 10/100 = 0.1
- 8 GPU Speedup: 8 / 1.1 = 7.27x (91% efficiency)
```

### Optimizing Communication

1. **Overlap communication with computation**:
```python
# PyTorch DDP does this automatically
# Manual overlap:
with model.no_sync():  # Skip gradient sync
    for i in range(accumulation_steps - 1):
        loss = train_step(data[i])
        loss.backward()

# Last step: sync gradients
loss = train_step(data[-1])
loss.backward()  # Gradients synced here
```

2. **Gradient compression**:
```python
# FP16 gradients (half the communication)
model = model.half()

# TODO: Implement gradient quantization for further compression
```

3. **Reduce communication frequency**:
```python
# Gradient accumulation reduces all-reduce frequency
accumulation_steps = 4
# All-reduce every 4 iterations instead of every iteration
```

## Summary

Key multi-GPU takeaways:

1. **Data Parallelism**: Use DDP for most workloads (easiest, scales well)
2. **Model Parallelism**: For models too large for single GPU
3. **Pipeline Parallelism**: Combine with model parallelism for very large models
4. **NVLink is essential**: 10-20x faster than PCIe for GPU communication
5. **NCCL optimizations**: Tune for your network topology
6. **Measure scaling**: Track efficiency to identify bottlenecks

## Hands-on Exercise

Compare single-GPU vs multi-GPU training:

```bash
# Single GPU
python train.py --batch-size 256

# 4 GPUs with DDP
torchrun --nproc_per_node=4 train.py --batch-size 64

# Measure and compare:
# - Training time per epoch
# - Throughput (samples/sec)
# - Scaling efficiency

# TODO: Implement and test different parallelism strategies
```

## Further Reading

- PyTorch DDP Tutorial: https://pytorch.org/tutorials/intermediate/ddp_tutorial.html
- Megatron-LM: https://github.com/NVIDIA/Megatron-LM
- DeepSpeed: https://github.com/microsoft/DeepSpeed
- NCCL Documentation: https://docs.nvidia.com/deeplearning/nccl/

---

**Next Lecture**: GPU Virtualization with MIG and vGPU
