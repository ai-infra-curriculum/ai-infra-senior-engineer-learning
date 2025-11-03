# Lecture 04: NCCL and High-Performance Networking

## Learning Objectives

By the end of this lecture, you will be able to:

- Architect distributed training systems leveraging NCCL's optimized collective communication primitives for multi-GPU and multi-node training
- Implement and configure NCCL collective operations (AllReduce, Broadcast, ReduceScatter, AllGather) for efficient gradient synchronization
- Design and optimize network topology configurations using NVLink, InfiniBand, and RDMA to minimize communication bottlenecks
- Configure NCCL environment variables and tuning parameters to maximize bandwidth utilization and reduce latency for specific workloads
- Evaluate and benchmark network performance using NCCL tests to identify bottlenecks and measure scaling efficiency
- Implement GPUDirect RDMA and InfiniBand optimizations for multi-node training with minimal CPU involvement
- Troubleshoot common NCCL issues including P2P access failures, InfiniBand configuration errors, and communication timeouts
- Design network-aware training architectures that balance compute, communication, and bandwidth constraints for production ML systems

## Table of Contents

1. [Introduction to NCCL](#introduction)
2. [NCCL Architecture](#nccl-architecture)
3. [Collective Operations](#collective-operations)
4. [Network Topology and Performance](#network-topology)
5. [InfiniBand and RDMA](#infiniband-rdma)
6. [GPU Interconnects](#gpu-interconnects)
7. [NCCL Configuration and Tuning](#nccl-configuration)
8. [Performance Benchmarking](#benchmarking)
9. [Troubleshooting](#troubleshooting)

## Introduction to NCCL

NVIDIA Collective Communications Library (NCCL) is a library of optimized primitives for multi-GPU and multi-node communication in NVIDIA GPU clusters.

### Why NCCL Matters

```python
# Without NCCL: Manual gradient averaging
def manual_gradient_average(gradients, world_size):
    """Naive gradient averaging - SLOW"""
    # Each GPU sends to every other GPU
    # O(N²) communication pattern
    averaged = []
    for grad in gradients:
        total = grad.clone()
        for rank in range(1, world_size):
            # Send/receive from each rank
            received = receive_from_rank(rank)
            total += received
        averaged.append(total / world_size)
    return averaged

# With NCCL: Optimized collective operations
def nccl_gradient_average(gradients):
    """NCCL AllReduce - FAST"""
    # Single collective operation
    # Optimized communication pattern
    # Hardware acceleration
    for grad in gradients:
        dist.all_reduce(grad, op=dist.ReduceOp.AVG)
    return gradients
```

### NCCL vs Alternatives

| Feature | NCCL | MPI | GLOO |
|---------|------|-----|------|
| GPU Optimization | Excellent | Good | Basic |
| Multi-node | Excellent | Excellent | Good |
| Single-node | Excellent | Good | Good |
| NVLink Support | Yes | No | No |
| InfiniBand | Yes | Yes | Limited |
| Performance | Best | Very Good | Good |
| CPU Support | No | Yes | Yes |

## NCCL Architecture

### Communication Primitives

```
┌───────────────────────────────────────────────────────────────┐
│                    NCCL Communication Layers                   │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            Application Layer (PyTorch/TF)                │ │
│  └────────────────────────┬─────────────────────────────────┘ │
│                           │                                    │
│  ┌────────────────────────▼─────────────────────────────────┐ │
│  │              NCCL API (Collectives)                      │ │
│  │  AllReduce | Broadcast | Reduce | AllGather | ReduceScatter│
│  └────────────────────────┬─────────────────────────────────┘ │
│                           │                                    │
│  ┌────────────────────────▼─────────────────────────────────┐ │
│  │           NCCL Transport Layer                           │ │
│  │                                                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   NVLink    │  │ InfiniBand  │  │     TCP     │     │ │
│  │  │  (GPU-GPU)  │  │   (RDMA)    │  │  (Fallback) │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│  ┌────────────────────────▼─────────────────────────────────┐ │
│  │              Hardware Layer                              │ │
│  │                                                          │ │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                │ │
│  │  │ GPU0 │──│ GPU1 │──│ GPU2 │──│ GPU3 │  (NVLink)      │ │
│  │  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘                │ │
│  │     └─────────┴─────────┴─────────┘                     │ │
│  │              PCIe Switch / IB HCA                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### NCCL Communication Algorithms

**1. Ring Algorithm**
```
┌────────────────────────────────────────────────────────┐
│              Ring AllReduce Algorithm                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: Scatter-Reduce                                │
│                                                         │
│   GPU0 ─┬─> GPU1 ─┬─> GPU2 ─┬─> GPU3 ─┬              │
│   ^     │          │          │          │              │
│   └─────┴──────────┴──────────┴──────────┘              │
│                                                         │
│   Each GPU sends 1/N of data to next GPU               │
│   N-1 steps: Each GPU accumulates partial sums         │
│                                                         │
│  Step 2: AllGather                                     │
│                                                         │
│   GPU0 ─┬─> GPU1 ─┬─> GPU2 ─┬─> GPU3 ─┬              │
│   ^     │          │          │          │              │
│   └─────┴──────────┴──────────┴──────────┘              │
│                                                         │
│   Each GPU sends final 1/N to next GPU                 │
│   N-1 steps: All GPUs have complete result             │
│                                                         │
│  Total: 2(N-1) steps                                   │
│  Data transferred per GPU: 2(N-1)/N ≈ 2 (for large N)  │
│  Bandwidth optimal!                                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

**2. Tree Algorithm**
```
┌────────────────────────────────────────────────────────┐
│              Tree AllReduce Algorithm                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: Reduce (bottom-up)                            │
│                                                         │
│               GPU0 (root)                               │
│              ╱    ╲                                     │
│          GPU1      GPU2                                 │
│         ╱  ╲      ╱  ╲                                  │
│      GPU3  GPU4 GPU5  GPU6                              │
│                                                         │
│  Step 2: Broadcast (top-down)                          │
│                                                         │
│               GPU0 (root)                               │
│              ╱    ╲                                     │
│          GPU1      GPU2                                 │
│         ╱  ╲      ╱  ╲                                  │
│      GPU3  GPU4 GPU5  GPU6                              │
│                                                         │
│  Total: 2*log₂(N) steps                                │
│  Lower latency than ring for small messages            │
│  Not bandwidth optimal                                  │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Collective Operations

### AllReduce

Most common operation in distributed training - combines values across all ranks.

```python
import torch
import torch.distributed as dist

def demonstrate_allreduce():
    """
    AllReduce: Sum (or other ops) across all ranks
    Result is available on all ranks
    """
    rank = dist.get_rank()
    world_size = dist.get_world_size()

    # Each rank has a tensor
    tensor = torch.tensor([rank], dtype=torch.float32).cuda()
    print(f"Rank {rank} before AllReduce: {tensor.item()}")

    # AllReduce: Sum operation
    # After AllReduce, all ranks will have sum of all tensors
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
    print(f"Rank {rank} after AllReduce: {tensor.item()}")
    # Expected: sum(0,1,2,...,world_size-1)

    # Other operations
    tensor = torch.tensor([rank + 1], dtype=torch.float32).cuda()
    dist.all_reduce(tensor, op=dist.ReduceOp.PRODUCT)  # Product
    dist.all_reduce(tensor, op=dist.ReduceOp.MAX)      # Maximum
    dist.all_reduce(tensor, op=dist.ReduceOp.MIN)      # Minimum

# Gradient synchronization in distributed training
def sync_gradients(model):
    """
    Synchronize gradients across all workers
    This is what DDP does automatically
    """
    for param in model.parameters():
        if param.grad is not None:
            # Average gradients across all workers
            dist.all_reduce(param.grad, op=dist.ReduceOp.AVG)

# Measure AllReduce performance
def benchmark_allreduce(sizes, num_iterations=100):
    """
    Benchmark AllReduce performance for different sizes
    """
    import time

    results = {}

    for size in sizes:
        tensor = torch.randn(size, dtype=torch.float32).cuda()

        # Warmup
        for _ in range(10):
            dist.all_reduce(tensor)

        # Benchmark
        torch.cuda.synchronize()
        start = time.time()

        for _ in range(num_iterations):
            dist.all_reduce(tensor)

        torch.cuda.synchronize()
        elapsed = time.time() - start

        # Calculate metrics
        avg_time = elapsed / num_iterations
        data_size_mb = size * 4 / (1024 * 1024)  # 4 bytes per float32
        bandwidth_gbps = (data_size_mb / avg_time) * 8 / 1024

        results[size] = {
            'avg_time_ms': avg_time * 1000,
            'bandwidth_gbps': bandwidth_gbps,
        }

        if dist.get_rank() == 0:
            print(f"Size: {size:>12,} ({data_size_mb:>8.2f} MB) "
                  f"Time: {avg_time*1000:>8.4f} ms "
                  f"Bandwidth: {bandwidth_gbps:>6.2f} GB/s")

    return results

# Run benchmark
if dist.get_rank() == 0:
    print("\nAllReduce Benchmark:")
    print("=" * 70)

benchmark_allreduce([
    1024,           # 4 KB
    1024 * 256,     # 1 MB
    1024 * 1024,    # 4 MB
    1024 * 1024 * 4,   # 16 MB
    1024 * 1024 * 16,  # 64 MB
    1024 * 1024 * 64,  # 256 MB
])
```

### Broadcast

Send data from one rank to all other ranks.

```python
def demonstrate_broadcast():
    """
    Broadcast: Send tensor from root to all ranks
    """
    rank = dist.get_rank()

    if rank == 0:
        # Root rank: has the data
        tensor = torch.tensor([1, 2, 3, 4, 5], dtype=torch.float32).cuda()
        print(f"Rank 0 broadcasting: {tensor}")
    else:
        # Other ranks: allocate space
        tensor = torch.zeros(5, dtype=torch.float32).cuda()

    # Broadcast from rank 0 to all ranks
    dist.broadcast(tensor, src=0)

    print(f"Rank {rank} received: {tensor}")

# Use case: Broadcast model parameters
def broadcast_model_parameters(model, root_rank=0):
    """
    Ensure all workers start with same parameters
    """
    for param in model.parameters():
        dist.broadcast(param.data, src=root_rank)

    print(f"Rank {dist.get_rank()}: Model parameters synchronized")
```

### ReduceScatter and AllGather

```python
def demonstrate_reduce_scatter():
    """
    ReduceScatter: Reduce and distribute chunks to each rank
    """
    rank = dist.get_rank()
    world_size = dist.get_world_size()

    # Each rank has a tensor
    input_tensor = torch.ones(world_size * 4, dtype=torch.float32).cuda() * rank

    # Output tensor (will receive 1/world_size of result)
    output_tensor = torch.zeros(4, dtype=torch.float32).cuda()

    # ReduceScatter: Sum and distribute
    # Rank i receives sum of all ranks' i-th chunk
    dist.reduce_scatter(output_tensor, list(input_tensor.chunk(world_size)))

    print(f"Rank {rank} ReduceScatter result: {output_tensor}")

def demonstrate_allgather():
    """
    AllGather: Gather tensors from all ranks to all ranks
    """
    rank = dist.get_rank()
    world_size = dist.get_world_size()

    # Each rank has a tensor
    input_tensor = torch.tensor([rank], dtype=torch.float32).cuda()

    # Output: will contain tensors from all ranks
    output_tensors = [torch.zeros(1, dtype=torch.float32).cuda()
                     for _ in range(world_size)]

    # AllGather
    dist.all_gather(output_tensors, input_tensor)

    result = torch.cat(output_tensors)
    print(f"Rank {rank} AllGather result: {result}")

# Use case: Gather metrics from all workers
def gather_metrics(local_metrics):
    """
    Gather metrics from all workers
    Returns dict with metrics from all ranks
    """
    world_size = dist.get_world_size()

    # Convert metrics to tensor
    tensor = torch.tensor([
        local_metrics['loss'],
        local_metrics['accuracy'],
    ], dtype=torch.float32).cuda()

    # AllGather
    gathered = [torch.zeros_like(tensor) for _ in range(world_size)]
    dist.all_gather(gathered, tensor)

    # Convert back to dict
    all_metrics = {}
    for rank, metrics_tensor in enumerate(gathered):
        all_metrics[rank] = {
            'loss': metrics_tensor[0].item(),
            'accuracy': metrics_tensor[1].item(),
        }

    return all_metrics
```

## Network Topology and Performance

### GPU Topology

```python
def print_gpu_topology():
    """
    Print GPU topology information
    """
    import pynvml

    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()

    print(f"\n{'='*70}")
    print(f"GPU Topology ({device_count} GPUs)")
    print(f"{'='*70}\n")

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        name = pynvml.nvmlDeviceGetName(handle)

        print(f"GPU {i}: {name}")

        # Check P2P connectivity
        print(f"  P2P Access to other GPUs:")
        for j in range(device_count):
            if i != j:
                other_handle = pynvml.nvmlDeviceGetHandleByIndex(j)
                try:
                    # Check if GPUs can access each other's memory
                    can_access = pynvml.nvmlDeviceGetP2PStatus(
                        handle, other_handle,
                        pynvml.NVML_P2P_CAPS_INDEX_READ
                    )
                    status = "Yes (NVLink)" if can_access else "No (PCIe)"
                except:
                    status = "Unknown"

                print(f"    GPU {j}: {status}")

        print()

    pynvml.nvmlShutdown()

# Typical topologies
TOPOLOGIES = {
    'DGX-A100': {
        'gpus': 8,
        'nvlink': 'Full mesh (12 NVLink/GPU)',
        'bandwidth': '600 GB/s bidirectional',
        'topology': '''
            GPU0 ─── NVLink ─── GPU1
             │  ╲     ╱     ╲    │
             │    NVLink      NVLink
             │  ╱     ╲     ╱    │
            GPU2 ─── NVLink ─── GPU3
             │                   │
            (All GPUs fully connected via NVLink)
        ''',
    },
    'Standard PCIe': {
        'gpus': 8,
        'nvlink': 'None',
        'bandwidth': '~16 GB/s per GPU',
        'topology': '''
                    CPU
                     │
                 PCIe Switch
              ╱   ╱  │  ╲   ╲
            GPU0 GPU1 ... GPU7
            (All through PCIe)
        ''',
    },
    'Hybrid NVLink': {
        'gpus': 8,
        'nvlink': 'Partial (pairs)',
        'bandwidth': 'Mixed',
        'topology': '''
            GPU0 ═══ GPU1    GPU2 ═══ GPU3
             │               │
            GPU4 ═══ GPU5    GPU6 ═══ GPU7
            (═══ = NVLink, │ = PCIe)
        ''',
    },
}

def analyze_topology_impact():
    """
    Demonstrate impact of topology on performance
    """
    # Bandwidth expectations (approximate)
    topologies = {
        'NVLink (DGX-A100)': 300,      # GB/s per GPU
        'NVLink (V100)': 150,           # GB/s per GPU
        'PCIe 4.0 x16': 32,             # GB/s per GPU
        'PCIe 3.0 x16': 16,             # GB/s per GPU
        'InfiniBand HDR': 25,           # GB/s per link
        'Ethernet 100GbE': 12.5,        # GB/s per link
    }

    # Model size and expected transfer time
    model_sizes = {
        'ResNet-50': 0.1,      # 100 MB
        'BERT-Large': 1.3,     # 1.3 GB
        'GPT-2': 6,            # 6 GB
        'GPT-3 175B': 700,     # 700 GB (FP32)
    }

    print("\nGradient Synchronization Time (AllReduce):")
    print("=" * 70)
    print(f"{'Model':<15} {'Size':<10} {'NVLink':<12} {'PCIe 4.0':<12} {'IB HDR':<12}")
    print("-" * 70)

    for model_name, size_gb in model_sizes.items():
        times = {}
        for topo_name, bandwidth_gbps in topologies.items():
            # AllReduce transfers approximately 2*size
            # (scatter-reduce + allgather)
            transfer_time = (2 * size_gb) / bandwidth_gbps
            times[topo_name] = transfer_time * 1000  # Convert to ms

        print(f"{model_name:<15} {size_gb:>6.1f} GB  "
              f"{times.get('NVLink (DGX-A100)', 0):>8.2f} ms  "
              f"{times.get('PCIe 4.0 x16', 0):>8.2f} ms  "
              f"{times.get('InfiniBand HDR', 0):>8.2f} ms")

analyze_topology_impact()
```

### Network Bottleneck Analysis

```python
def identify_network_bottleneck():
    """
    Identify if training is network-bound
    """
    import time

    # Measure compute time
    model = create_model().cuda()
    data = torch.randn(32, 3, 224, 224).cuda()

    # Warmup
    for _ in range(10):
        output = model(data)
        loss = output.sum()
        loss.backward()

    # Measure forward+backward time
    torch.cuda.synchronize()
    start = time.time()

    for _ in range(100):
        output = model(data)
        loss = output.sum()
        loss.backward()

    torch.cuda.synchronize()
    compute_time = (time.time() - start) / 100

    # Measure communication time
    # Simulate gradient AllReduce
    total_params = sum(p.numel() for p in model.parameters())
    gradient_tensor = torch.randn(total_params).cuda()

    torch.cuda.synchronize()
    start = time.time()

    for _ in range(100):
        dist.all_reduce(gradient_tensor)

    torch.cuda.synchronize()
    comm_time = (time.time() - start) / 100

    # Analysis
    total_time = compute_time + comm_time
    compute_fraction = compute_time / total_time
    comm_fraction = comm_time / total_time

    print(f"\nBottleneck Analysis:")
    print(f"{'='*50}")
    print(f"Compute time:       {compute_time*1000:>8.2f} ms ({compute_fraction*100:.1f}%)")
    print(f"Communication time: {comm_time*1000:>8.2f} ms ({comm_fraction*100:.1f}%)")
    print(f"Total time:         {total_time*1000:>8.2f} ms")
    print(f"{'='*50}")

    if comm_fraction > 0.3:
        print("\n⚠ WARNING: Communication is bottleneck!")
        print("Recommendations:")
        print("  1. Use gradient accumulation to reduce communication frequency")
        print("  2. Increase batch size per GPU (more compute per communication)")
        print("  3. Use gradient compression")
        print("  4. Upgrade network (InfiniBand, faster NVLink)")
        print("  5. Use mixed precision training (smaller gradients)")
    else:
        print("\n✓ Compute-bound: Good! Communication is not a bottleneck.")
```

## InfiniBand and RDMA

### What is RDMA?

Remote Direct Memory Access (RDMA) allows direct memory access from one computer to another without involving the operating system.

```
┌────────────────────────────────────────────────────────────┐
│            Traditional Network vs RDMA                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Traditional TCP/IP:                                        │
│  ┌──────────┐                          ┌──────────┐        │
│  │   App    │                          │   App    │        │
│  ├──────────┤                          ├──────────┤        │
│  │   OS     │  Multiple copies         │   OS     │        │
│  │ (Kernel) │  High CPU usage          │ (Kernel) │        │
│  ├──────────┤  Context switches        ├──────────┤        │
│  │   NIC    │ ─────────────────────────│   NIC    │        │
│  └──────────┘                          └──────────┘        │
│                                                             │
│  RDMA:                                                      │
│  ┌──────────┐                          ┌──────────┐        │
│  │   App    │  Direct memory access    │   App    │        │
│  │          │  Zero-copy               │          │        │
│  ├──────────┤  Low CPU usage           ├──────────┤        │
│  │ (bypass) │  No context switch       │ (bypass) │        │
│  ├──────────┤                          ├──────────┤        │
│  │   NIC    │ ═════════════════════════│   NIC    │        │
│  │ (RDMA)   │                          │ (RDMA)   │        │
│  └──────────┘                          └──────────┘        │
│                                                             │
│  Benefits:                                                  │
│  ✓ Low latency (~1-2 μs)                                   │
│  ✓ High bandwidth (200+ Gbps)                              │
│  ✓ Low CPU utilization                                     │
│  ✓ Zero-copy transfers                                     │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### InfiniBand Configuration

```bash
# Check InfiniBand status
ibstat
ibstatus

# Show InfiniBand devices
ibv_devices

# Check link speed
ibstatus | grep "Rate"
# Expected: 100 Gb/sec (HDR), 200 Gb/sec (HDR200), 400 Gb/sec (NDR)

# Test RDMA bandwidth
ib_write_bw  # On server
ib_write_bw <server-ip>  # On client

# NCCL with InfiniBand
export NCCL_IB_HCA=mlx5_0,mlx5_1  # InfiniBand devices
export NCCL_IB_DISABLE=0          # Enable InfiniBand
export NCCL_IB_GID_INDEX=3        # RoCE v2
export NCCL_SOCKET_IFNAME=ib0     # Interface name
```

## GPU Interconnects

### NVLink Performance

```python
def benchmark_nvlink_vs_pcie():
    """
    Compare NVLink vs PCIe performance
    """
    import time

    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        print("Need at least 2 GPUs")
        return

    sizes = [1, 10, 100, 1000]  # MB

    print("\nNVLink vs PCIe Bandwidth Comparison:")
    print("=" * 70)
    print(f"{'Size (MB)':<12} {'NVLink (GB/s)':<18} {'PCIe (GB/s)':<18}")
    print("-" * 70)

    for size_mb in sizes:
        size = size_mb * 1024 * 1024 // 4  # Convert to float32 elements

        # Test with P2P enabled (NVLink if available)
        tensor_gpu0 = torch.randn(size).cuda(0)
        tensor_gpu1 = torch.zeros(size).cuda(1)

        # Enable P2P
        torch.cuda.set_device(0)

        # Warmup
        for _ in range(10):
            tensor_gpu1.copy_(tensor_gpu0)
        torch.cuda.synchronize()

        # Benchmark
        start = time.time()
        for _ in range(100):
            tensor_gpu1.copy_(tensor_gpu0)
        torch.cuda.synchronize()
        nvlink_time = (time.time() - start) / 100

        nvlink_bandwidth = (size_mb / nvlink_time) / 1024  # GB/s

        # Test through CPU (forced PCIe)
        tensor_cpu = torch.zeros(size)

        # Warmup
        for _ in range(10):
            tensor_cpu.copy_(tensor_gpu0.cpu())
            tensor_gpu1.copy_(tensor_cpu.cuda(1))
        torch.cuda.synchronize()

        # Benchmark
        start = time.time()
        for _ in range(100):
            tensor_cpu.copy_(tensor_gpu0.cpu())
            tensor_gpu1.copy_(tensor_cpu.cuda(1))
        torch.cuda.synchronize()
        pcie_time = (time.time() - start) / 100

        pcie_bandwidth = (size_mb / pcie_time) / 1024  # GB/s

        speedup = nvlink_bandwidth / pcie_bandwidth

        print(f"{size_mb:<12} {nvlink_bandwidth:>14.2f}  "
              f"{pcie_bandwidth:>14.2f}     "
              f"({speedup:.1f}x faster)")

benchmark_nvlink_vs_pcie()
```

## NCCL Configuration and Tuning

### Environment Variables

```python
# NCCL Configuration Guide
NCCL_CONFIG = {
    # Transport selection
    'NCCL_IB_DISABLE': '0',           # 0=enable IB, 1=disable
    'NCCL_P2P_DISABLE': '0',          # 0=enable P2P, 1=disable
    'NCCL_SHM_DISABLE': '0',          # 0=enable shared memory

    # InfiniBand specific
    'NCCL_IB_HCA': 'mlx5_0,mlx5_1',   # IB devices to use
    'NCCL_IB_GID_INDEX': '3',         # For RoCE
    'NCCL_IB_TIMEOUT': '22',          # Timeout value

    # Network interface
    'NCCL_SOCKET_IFNAME': 'ib0',      # Network interface
    'NCCL_NET_GDR_LEVEL': '5',        # GPUDirect RDMA level

    # Algorithm selection
    'NCCL_ALGO': 'Ring',              # Ring or Tree
    'NCCL_PROTO': 'Simple',           # Simple or LL or LL128

    # Tuning
    'NCCL_MIN_NCHANNELS': '4',        # Minimum channels
    'NCCL_MAX_NCHANNELS': '16',       # Maximum channels
    'NCCL_BUFFSIZE': '8388608',       # Buffer size (8MB)

    # Debugging
    'NCCL_DEBUG': 'INFO',             # WARN, INFO, TRACE
    'NCCL_DEBUG_SUBSYS': 'ALL',       # Subsystems to debug

    # Topology
    'NCCL_TOPO_FILE': '/path/to/topo.xml',  # Custom topology
}

def configure_nccl_for_performance():
    """
    Configure NCCL for optimal performance
    """
    import os

    # Basic configuration
    os.environ['NCCL_IB_DISABLE'] = '0'      # Enable InfiniBand
    os.environ['NCCL_P2P_DISABLE'] = '0'      # Enable P2P
    os.environ['NCCL_DEBUG'] = 'WARN'         # Reduce logging

    # InfiniBand optimization
    if has_infiniband():
        os.environ['NCCL_IB_HCA'] = detect_ib_devices()
        os.environ['NCCL_IB_GID_INDEX'] = '3'
        os.environ['NCCL_NET_GDR_LEVEL'] = '5'  # GPUDirect RDMA

    # NVLink optimization
    if has_nvlink():
        os.environ['NCCL_P2P_LEVEL'] = 'NVL'  # Force NVLink

    # Increase channels for large clusters
    if world_size > 8:
        os.environ['NCCL_MIN_NCHANNELS'] = '8'
        os.environ['NCCL_MAX_NCHANNELS'] = '16'

    print("NCCL configured for optimal performance")

def has_infiniband():
    """Check if InfiniBand is available"""
    import subprocess
    try:
        result = subprocess.run(['ibstat'], capture_output=True)
        return result.returncode == 0
    except:
        return False

def detect_ib_devices():
    """Detect InfiniBand devices"""
    import subprocess
    try:
        result = subprocess.run(
            ['ibv_devices'],
            capture_output=True,
            text=True
        )
        # Parse output to get device names
        devices = []
        for line in result.stdout.split('\n'):
            if 'mlx' in line:
                device = line.split()[0]
                devices.append(device)
        return ','.join(devices)
    except:
        return 'mlx5_0'
```

### Performance Tuning

```python
def tune_nccl_for_workload(model_size_gb, world_size, network_type):
    """
    Tune NCCL based on workload characteristics

    Args:
        model_size_gb: Model size in GB
        world_size: Number of GPUs
        network_type: 'nvlink', 'infiniband', or 'ethernet'
    """
    import os

    print(f"\nTuning NCCL for:")
    print(f"  Model size: {model_size_gb:.2f} GB")
    print(f"  World size: {world_size}")
    print(f"  Network: {network_type}")
    print()

    # Small model (< 1 GB): Latency matters
    if model_size_gb < 1:
        os.environ['NCCL_ALGO'] = 'Tree'  # Lower latency
        os.environ['NCCL_PROTO'] = 'Simple'
        print("✓ Using Tree algorithm for low latency")

    # Large model (> 10 GB): Bandwidth matters
    elif model_size_gb > 10:
        os.environ['NCCL_ALGO'] = 'Ring'  # Bandwidth optimal
        os.environ['NCCL_PROTO'] = 'LL128'  # Low-latency 128B protocol
        os.environ['NCCL_BUFFSIZE'] = str(16 * 1024 * 1024)  # 16MB buffers
        print("✓ Using Ring algorithm for high bandwidth")

    # Medium model: Balanced
    else:
        os.environ['NCCL_ALGO'] = 'Ring'
        os.environ['NCCL_PROTO'] = 'Simple'
        print("✓ Using balanced configuration")

    # Network-specific tuning
    if network_type == 'nvlink':
        os.environ['NCCL_P2P_LEVEL'] = 'NVL'
        os.environ['NCCL_MIN_NCHANNELS'] = '16'  # More channels for NVLink
        print("✓ Optimized for NVLink")

    elif network_type == 'infiniband':
        os.environ['NCCL_IB_DISABLE'] = '0'
        os.environ['NCCL_NET_GDR_LEVEL'] = '5'
        os.environ['NCCL_IB_GID_INDEX'] = '3'
        print("✓ Optimized for InfiniBand")

    elif network_type == 'ethernet':
        os.environ['NCCL_IB_DISABLE'] = '1'  # Disable IB
        os.environ['NCCL_MIN_NCHANNELS'] = '4'  # Fewer channels
        print("✓ Optimized for Ethernet")

    # Scale-specific tuning
    if world_size > 64:
        os.environ['NCCL_CROSS_NIC'] = '1'  # Use multiple NICs
        os.environ['NCCL_MAX_NCHANNELS'] = '32'
        print("✓ Large-scale optimizations enabled")

    print("\nNCCL tuning complete!")

# Example usage
tune_nccl_for_workload(
    model_size_gb=7.5,      # GPT-3 7B
    world_size=64,           # 64 GPUs
    network_type='infiniband'
)
```

## Performance Benchmarking

### NCCL Tests

```bash
# Build NCCL tests
git clone https://github.com/NVIDIA/nccl-tests.git
cd nccl-tests
make MPI=1 MPI_HOME=/usr/lib/x86_64-linux-gnu/openmpi

# Run all_reduce_perf test
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 8

# Run on multiple nodes
mpirun -np 16 -H node1:8,node2:8 \
    ./build/all_reduce_perf -b 8 -e 8G -f 2

# Expected output (DGX-A100, 8 GPUs):
# size      time   algbw   busbw
# 1MB       X.XX   YY.Y    ZZ.Z
# ...
# 1GB       X.XX   300+    450+  GB/s (excellent!)
```

## Troubleshooting

### Common Issues

```python
def diagnose_nccl_issues():
    """
    Diagnose common NCCL issues
    """
    print("NCCL Diagnostics")
    print("=" * 70)

    # 1. Check NCCL version
    try:
        import subprocess
        nccl_ver = torch.cuda.nccl.version()
        print(f"✓ NCCL version: {nccl_ver}")
    except:
        print("✗ Could not determine NCCL version")

    # 2. Check GPU P2P access
    print("\nP2P Access Matrix:")
    for i in range(torch.cuda.device_count()):
        for j in range(torch.cuda.device_count()):
            if i != j:
                can_access = torch.cuda.can_device_access_peer(i, j)
                print(f"  GPU{i} -> GPU{j}: {'Yes' if can_access else 'No'}")

    # 3. Check InfiniBand
    print("\nInfiniBand:")
    if has_infiniband():
        print("  ✓ InfiniBand detected")
        devices = detect_ib_devices()
        print(f"  Devices: {devices}")
    else:
        print("  ✗ InfiniBand not detected")

    # 4. Check environment variables
    print("\nNCCL Environment Variables:")
    nccl_vars = [k for k in os.environ.keys() if k.startswith('NCCL_')]
    if nccl_vars:
        for var in sorted(nccl_vars):
            print(f"  {var}={os.environ[var]}")
    else:
        print("  No NCCL variables set")

    print("\n" + "=" * 70)

# Common error messages and solutions
NCCL_ERRORS = {
    "NCCL WARN Call to ibv_create_qp failed": {
        "cause": "InfiniBand queue pair creation failed",
        "solutions": [
            "Check InfiniBand driver: ibstat",
            "Verify IB devices: ibv_devices",
            "Check NCCL_IB_HCA setting",
            "Ensure sufficient locked memory: ulimit -l unlimited",
        ],
    },
    "NCCL WARN Could not enable P2P": {
        "cause": "P2P access between GPUs failed",
        "solutions": [
            "Check GPU topology: nvidia-smi topo -m",
            "Verify IOMMU settings in BIOS",
            "Try: NCCL_P2P_LEVEL=SYS",
            "Check PCIe ACS (Access Control Services)",
        ],
    },
    "NCCL timeout": {
        "cause": "Communication timeout",
        "solutions": [
            "Increase timeout: NCCL_TIMEOUT=300",
            "Check network connectivity",
            "Verify all ranks are running",
            "Check for hanging processes",
        ],
    },
}

def print_error_solutions(error_msg):
    """Print solutions for common NCCL errors"""
    for error, info in NCCL_ERRORS.items():
        if error.lower() in error_msg.lower():
            print(f"\nError: {error}")
            print(f"Cause: {info['cause']}")
            print("Solutions:")
            for solution in info['solutions']:
                print(f"  - {solution}")
            return

    print("Error not in known issues database")
```

## Summary

Key takeaways:

1. **NCCL** is essential for efficient multi-GPU communication
2. **Ring AllReduce** is bandwidth-optimal for large transfers
3. **Network topology** significantly impacts performance
4. **NVLink** provides much higher bandwidth than PCIe
5. **InfiniBand/RDMA** is crucial for multi-node training
6. **Proper configuration** can dramatically improve performance

**Best Practices:**
- Use NVLink for intra-node communication
- Use InfiniBand for inter-node communication
- Tune NCCL parameters based on workload
- Monitor bandwidth utilization
- Enable GPUDirect RDMA when available

## Further Reading

- [NCCL Documentation](https://docs.nvidia.com/deeplearning/nccl/)
- [NCCL Tests GitHub](https://github.com/NVIDIA/nccl-tests)
- [InfiniBand Architecture](https://www.infinibandta.org/)
- "Bringing HPC Techniques to Deep Learning" (NVIDIA, 2017)

## Next Steps

Continue to `05-mixed-precision-training.md` to learn about FP16/BF16 training and automatic mixed precision.
