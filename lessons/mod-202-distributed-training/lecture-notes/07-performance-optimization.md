# Lecture 07: Performance Optimization for Distributed Training

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement systematic performance profiling strategies using PyTorch Profiler and NVIDIA Nsight to identify distributed training bottlenecks
- Analyze and decompose training performance into components (data loading, forward pass, backward pass, communication, optimizer) to identify bottlenecks
- Implement communication optimizations including gradient compression, gradient accumulation, and NCCL tuning to reduce communication overhead
- Apply memory optimization techniques including gradient checkpointing, ZeRO optimizer stages, and memory-efficient data structures for large models
- Optimize data loading pipelines with prefetching, pinned memory, persistent workers, and GPU-aware data loaders to eliminate I/O bottlenecks
- Implement computation optimizations including mixed precision training, torch.compile, operation fusion, and cudnn tuning
- Evaluate trade-offs between communication frequency, batch size, memory usage, and training throughput in distributed settings
- Design end-to-end optimization strategies that systematically address bottlenecks and achieve high GPU utilization and scaling efficiency

## Table of Contents

1. [Introduction to Performance Optimization](#introduction)
2. [Profiling Distributed Training](#profiling)
3. [Bottleneck Identification](#bottleneck-identification)
4. [Communication Optimization](#communication-optimization)
5. [Memory Optimization](#memory-optimization)
6. [Computation Optimization](#computation-optimization)
7. [I/O and Data Loading Optimization](#io-optimization)
8. [End-to-End Optimization Strategy](#optimization-strategy)

## Introduction to Performance Optimization

Distributed training performance depends on balancing computation, communication, and I/O. This lecture covers systematic approaches to identify and resolve bottlenecks.

### Performance Metrics

```python
import time
import torch
import torch.distributed as dist

class PerformanceMonitor:
    """
    Monitor distributed training performance metrics
    """

    def __init__(self):
        self.metrics = {
            'data_loading_time': [],
            'forward_time': [],
            'backward_time': [],
            'optimizer_time': [],
            'communication_time': [],
            'total_time': [],
        }

        self.step_start_time = None

    def start_step(self):
        """Mark start of training step"""
        self.step_start_time = time.time()

    def record_metric(self, name, value):
        """Record a performance metric"""
        if name in self.metrics:
            self.metrics[name].append(value)

    def get_statistics(self):
        """Calculate statistics for all metrics"""
        import numpy as np

        stats = {}
        for name, values in self.metrics.items():
            if len(values) > 0:
                stats[name] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'p50': np.median(values),
                    'p95': np.percentile(values, 95),
                    'p99': np.percentile(values, 99),
                }

        return stats

    def print_summary(self):
        """Print performance summary"""
        stats = self.get_statistics()

        print("\n" + "="*80)
        print("Performance Summary")
        print("="*80)

        # Calculate breakdown
        if 'total_time' in stats and stats['total_time']['mean'] > 0:
            total = stats['total_time']['mean']

            print(f"\n{'Metric':<25} {'Mean (ms)':<12} {'Std (ms)':<12} {'% of Total':<12}")
            print("-"*80)

            for name in ['data_loading_time', 'forward_time', 'backward_time',
                        'optimizer_time', 'communication_time', 'total_time']:
                if name in stats:
                    mean_ms = stats[name]['mean'] * 1000
                    std_ms = stats[name]['std'] * 1000
                    pct = (stats[name]['mean'] / total) * 100 if name != 'total_time' else 100.0

                    print(f"{name:<25} {mean_ms:>10.2f}  {std_ms:>10.2f}  {pct:>10.1f}%")

        print("="*80)

        # Identify bottlenecks
        self._identify_bottlenecks(stats)

    def _identify_bottlenecks(self, stats):
        """Identify performance bottlenecks"""
        if 'total_time' not in stats:
            return

        total = stats['total_time']['mean']
        bottlenecks = []

        # Check each component
        for name, display_name, threshold in [
            ('data_loading_time', 'Data Loading', 0.20),
            ('communication_time', 'Communication', 0.30),
            ('forward_time', 'Forward Pass', 0.15),
            ('backward_time', 'Backward Pass', 0.15),
        ]:
            if name in stats:
                fraction = stats[name]['mean'] / total
                if fraction > threshold:
                    bottlenecks.append((display_name, fraction * 100))

        if bottlenecks:
            print("\n⚠ Potential Bottlenecks Detected:")
            for name, pct in bottlenecks:
                print(f"  - {name}: {pct:.1f}% of total time")

                # Suggest optimizations
                suggestions = self._get_optimization_suggestions(name)
                for suggestion in suggestions:
                    print(f"    → {suggestion}")

    def _get_optimization_suggestions(self, bottleneck_name):
        """Get optimization suggestions for bottleneck"""
        suggestions = {
            'Data Loading': [
                "Increase num_workers in DataLoader",
                "Use pin_memory=True",
                "Prefetch data to GPU",
                "Use faster storage (NVMe, RAM disk)",
                "Optimize data preprocessing",
            ],
            'Communication': [
                "Use gradient accumulation",
                "Enable gradient compression",
                "Optimize network (InfiniBand, RDMA)",
                "Increase batch size per GPU",
                "Use mixed precision (smaller gradients)",
            ],
            'Forward Pass': [
                "Use mixed precision training",
                "Optimize model architecture",
                "Enable cudnn.benchmark",
                "Use TensorRT or torch.compile",
            ],
            'Backward Pass': [
                "Use mixed precision training",
                "Enable gradient checkpointing",
                "Optimize memory layout",
            ],
        }

        return suggestions.get(bottleneck_name, [])

# Usage in training loop
def train_with_monitoring():
    """Training loop with performance monitoring"""
    monitor = PerformanceMonitor()

    for epoch in range(num_epochs):
        for batch_idx, batch in enumerate(train_loader):
            monitor.start_step()

            # Data loading
            start = time.time()
            data, target = batch
            data, target = data.cuda(), target.cuda()
            monitor.record_metric('data_loading_time', time.time() - start)

            # Forward pass
            start = time.time()
            output = model(data)
            loss = criterion(output, target)
            monitor.record_metric('forward_time', time.time() - start)

            # Backward pass
            start = time.time()
            optimizer.zero_grad()
            loss.backward()
            monitor.record_metric('backward_time', time.time() - start)

            # Optimizer step (includes communication for DDP)
            start = time.time()
            optimizer.step()
            monitor.record_metric('optimizer_time', time.time() - start)

            # Total time
            monitor.record_metric('total_time',
                                time.time() - monitor.step_start_time)

        # Print summary every epoch
        if dist.get_rank() == 0:
            monitor.print_summary()
```

## Profiling Distributed Training

### PyTorch Profiler

```python
import torch.profiler as profiler

def profile_distributed_training(model, train_loader, num_steps=100):
    """
    Profile distributed training with PyTorch Profiler
    """

    with profiler.profile(
        activities=[
            profiler.ProfilerActivity.CPU,
            profiler.ProfilerActivity.CUDA,
        ],
        schedule=profiler.schedule(
            wait=10,      # Skip first 10 steps
            warmup=10,    # Warmup for 10 steps
            active=20,    # Profile 20 steps
            repeat=1,
        ),
        on_trace_ready=profiler.tensorboard_trace_handler('./profiler_logs'),
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:

        for step, batch in enumerate(train_loader):
            if step >= num_steps:
                break

            # Training step
            data, target = batch
            data, target = data.cuda(), target.cuda()

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            # Step profiler
            prof.step()

    # Print summary
    if dist.get_rank() == 0:
        print("\nTop CUDA Operations:")
        print(prof.key_averages().table(
            sort_by="cuda_time_total",
            row_limit=20
        ))

        print("\nTop Memory Operations:")
        print(prof.key_averages().table(
            sort_by="self_cuda_memory_usage",
            row_limit=20
        ))

# Advanced profiling with custom markers
def profile_with_markers(model, train_loader):
    """Profile with custom markers for detailed analysis"""

    with profiler.profile(
        activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
        record_shapes=True,
    ) as prof:

        for batch in train_loader:
            # Mark data loading
            with profiler.record_function("DATA_LOADING"):
                data, target = batch
                data, target = data.cuda(non_blocking=True), target.cuda(non_blocking=True)

            # Mark forward pass
            with profiler.record_function("FORWARD"):
                output = model(data)
                loss = criterion(output, target)

            # Mark backward pass
            with profiler.record_function("BACKWARD"):
                optimizer.zero_grad()
                loss.backward()

            # Mark optimizer step
            with profiler.record_function("OPTIMIZER"):
                optimizer.step()

            break  # Profile one step

    # Analyze
    print(prof.key_averages().table(
        sort_by="cuda_time_total",
        row_limit=30
    ))
```

### NVIDIA Nsight Systems

```python
# Profile with NVIDIA Nsight Systems
# Run from command line:
"""
nsys profile -o profile_output \\
    --trace cuda,nvtx,osrt,cudnn,cublas \\
    --cuda-memory-usage true \\
    python train.py

# Then analyze with:
nsys-ui profile_output.qdrep
"""

# Add NVTX markers for Nsight
try:
    import torch.cuda.nvtx as nvtx
    NVTX_AVAILABLE = True
except ImportError:
    NVTX_AVAILABLE = False

def train_with_nvtx_markers(model, train_loader):
    """Training with NVTX markers for Nsight profiling"""

    for epoch in range(num_epochs):
        if NVTX_AVAILABLE:
            nvtx.range_push(f"Epoch {epoch}")

        for batch_idx, batch in enumerate(train_loader):
            if NVTX_AVAILABLE:
                nvtx.range_push(f"Step {batch_idx}")

            # Data loading
            if NVTX_AVAILABLE:
                nvtx.range_push("Data Loading")
            data, target = batch
            data, target = data.cuda(), target.cuda()
            if NVTX_AVAILABLE:
                nvtx.range_pop()

            # Forward
            if NVTX_AVAILABLE:
                nvtx.range_push("Forward")
            output = model(data)
            loss = criterion(output, target)
            if NVTX_AVAILABLE:
                nvtx.range_pop()

            # Backward
            if NVTX_AVAILABLE:
                nvtx.range_push("Backward")
            optimizer.zero_grad()
            loss.backward()
            if NVTX_AVAILABLE:
                nvtx.range_pop()

            # Optimizer
            if NVTX_AVAILABLE:
                nvtx.range_push("Optimizer")
            optimizer.step()
            if NVTX_AVAILABLE:
                nvtx.range_pop()

            if NVTX_AVAILABLE:
                nvtx.range_pop()  # Step

        if NVTX_AVAILABLE:
            nvtx.range_pop()  # Epoch
```

## Bottleneck Identification

### Systematic Bottleneck Analysis

```python
class BottleneckAnalyzer:
    """
    Systematic approach to identify bottlenecks
    """

    def __init__(self, model, train_loader, device):
        self.model = model
        self.train_loader = train_loader
        self.device = device

    def analyze(self):
        """
        Run comprehensive bottleneck analysis
        """
        print("\n" + "="*80)
        print("Bottleneck Analysis")
        print("="*80)

        results = {}

        # 1. Measure compute throughput
        print("\n1. Compute Throughput Analysis")
        results['compute'] = self.measure_compute_throughput()

        # 2. Measure communication overhead
        print("\n2. Communication Overhead Analysis")
        results['communication'] = self.measure_communication_overhead()

        # 3. Measure data loading throughput
        print("\n3. Data Loading Analysis")
        results['data_loading'] = self.measure_data_loading_throughput()

        # 4. Measure memory usage
        print("\n4. Memory Usage Analysis")
        results['memory'] = self.measure_memory_usage()

        # 5. Overall assessment
        print("\n5. Overall Assessment")
        self.provide_recommendations(results)

        return results

    def measure_compute_throughput(self):
        """Measure pure compute throughput (no communication)"""
        # Disable DDP communication temporarily
        if hasattr(self.model, 'require_backward_grad_sync'):
            self.model.require_backward_grad_sync = False

        batch = next(iter(self.train_loader))
        data, target = batch
        data, target = data.to(self.device), target.to(self.device)

        # Warmup
        for _ in range(10):
            output = self.model(data)
            loss = output.sum()
            loss.backward()

        # Measure
        torch.cuda.synchronize()
        start = time.time()

        num_iterations = 100
        for _ in range(num_iterations):
            self.model.zero_grad()
            output = self.model(data)
            loss = output.sum()
            loss.backward()

        torch.cuda.synchronize()
        elapsed = time.time() - start

        compute_time = elapsed / num_iterations
        throughput = 1.0 / compute_time  # iterations/sec

        print(f"  Compute time per step: {compute_time*1000:.2f} ms")
        print(f"  Throughput: {throughput:.2f} iterations/sec")

        # Re-enable communication
        if hasattr(self.model, 'require_backward_grad_sync'):
            self.model.require_backward_grad_sync = True

        return {
            'time_ms': compute_time * 1000,
            'throughput': throughput,
        }

    def measure_communication_overhead(self):
        """Measure communication overhead in distributed training"""
        if not dist.is_initialized():
            print("  Not distributed - skipping")
            return None

        # Get total gradient size
        total_params = sum(p.numel() for p in self.model.parameters())
        param_size_mb = total_params * 4 / (1024 * 1024)  # FP32

        # Measure AllReduce time
        tensor = torch.randn(total_params, device=self.device)

        # Warmup
        for _ in range(10):
            dist.all_reduce(tensor)

        # Measure
        torch.cuda.synchronize()
        start = time.time()

        num_iterations = 100
        for _ in range(num_iterations):
            dist.all_reduce(tensor)

        torch.cuda.synchronize()
        elapsed = time.time() - start

        comm_time = elapsed / num_iterations
        bandwidth_gbps = (param_size_mb / comm_time) * 8 / 1024  # Gbps

        print(f"  Gradient size: {param_size_mb:.2f} MB")
        print(f"  AllReduce time: {comm_time*1000:.2f} ms")
        print(f"  Effective bandwidth: {bandwidth_gbps:.2f} Gbps")

        return {
            'time_ms': comm_time * 1000,
            'bandwidth_gbps': bandwidth_gbps,
            'param_size_mb': param_size_mb,
        }

    def measure_data_loading_throughput(self):
        """Measure data loading throughput"""
        # Measure how fast we can iterate through data
        start = time.time()
        num_batches = 0

        for batch in self.train_loader:
            data, target = batch
            # Move to GPU
            data = data.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            torch.cuda.synchronize()  # Wait for transfer

            num_batches += 1
            if num_batches >= 100:
                break

        elapsed = time.time() - start
        time_per_batch = elapsed / num_batches

        print(f"  Time per batch: {time_per_batch*1000:.2f} ms")
        print(f"  Throughput: {1.0/time_per_batch:.2f} batches/sec")

        return {
            'time_ms': time_per_batch * 1000,
            'throughput': 1.0 / time_per_batch,
        }

    def measure_memory_usage(self):
        """Measure memory usage during training"""
        if not torch.cuda.is_available():
            return None

        batch = next(iter(self.train_loader))
        data, target = batch
        data, target = data.to(self.device), target.to(self.device)

        # Reset peak memory
        torch.cuda.reset_peak_memory_stats()

        # Forward + backward pass
        output = self.model(data)
        loss = output.sum()
        loss.backward()

        # Get memory stats
        allocated = torch.cuda.memory_allocated() / (1024**3)  # GB
        reserved = torch.cuda.memory_reserved() / (1024**3)
        peak = torch.cuda.max_memory_allocated() / (1024**3)

        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        usage_pct = (peak / total_memory) * 100

        print(f"  Allocated: {allocated:.2f} GB")
        print(f"  Reserved: {reserved:.2f} GB")
        print(f"  Peak: {peak:.2f} GB")
        print(f"  Usage: {usage_pct:.1f}% of {total_memory:.1f} GB")

        return {
            'allocated_gb': allocated,
            'reserved_gb': reserved,
            'peak_gb': peak,
            'total_gb': total_memory,
            'usage_pct': usage_pct,
        }

    def provide_recommendations(self, results):
        """Provide optimization recommendations based on analysis"""
        recommendations = []

        # Check compute efficiency
        if results.get('compute'):
            compute_time = results['compute']['time_ms']
            if results.get('communication'):
                comm_time = results['communication']['time_ms']
                comm_fraction = comm_time / (compute_time + comm_time)

                if comm_fraction > 0.3:
                    recommendations.append(
                        f"⚠ Communication overhead is high ({comm_fraction*100:.1f}%)\n"
                        "  → Use gradient accumulation\n"
                        "  → Increase batch size per GPU\n"
                        "  → Enable gradient compression"
                    )

        # Check data loading
        if results.get('data_loading'):
            data_time = results['data_loading']['time_ms']
            if results.get('compute'):
                compute_time = results['compute']['time_ms']
                if data_time > compute_time * 0.2:
                    recommendations.append(
                        f"⚠ Data loading is slow ({data_time:.1f} ms)\n"
                        "  → Increase num_workers\n"
                        "  → Use pin_memory=True\n"
                        "  → Prefetch data to GPU"
                    )

        # Check memory usage
        if results.get('memory'):
            usage_pct = results['memory']['usage_pct']
            if usage_pct > 90:
                recommendations.append(
                    f"⚠ High memory usage ({usage_pct:.1f}%)\n"
                    "  → Use gradient checkpointing\n"
                    "  → Reduce batch size\n"
                    "  → Enable mixed precision training"
                )
            elif usage_pct < 50:
                recommendations.append(
                    f"ℹ Low memory usage ({usage_pct:.1f}%)\n"
                    "  → Consider increasing batch size\n"
                    "  → Could train larger models"
                )

        # Print recommendations
        if recommendations:
            print("\nRecommendations:")
            print("-" * 80)
            for rec in recommendations:
                print(rec)
                print()
        else:
            print("\n✓ No major bottlenecks detected!")

# Usage
analyzer = BottleneckAnalyzer(model, train_loader, device)
results = analyzer.analyze()
```

## Communication Optimization

### Gradient Compression

```python
class GradientCompressor:
    """
    Compress gradients to reduce communication
    """

    def __init__(self, compression_ratio=0.01):
        """
        Args:
            compression_ratio: Fraction of gradients to keep (top-k)
        """
        self.compression_ratio = compression_ratio

    def compress_topk(self, tensor):
        """
        Top-K compression: Keep only largest K gradients
        """
        numel = tensor.numel()
        k = max(1, int(numel * self.compression_ratio))

        # Get top-k values and indices
        values, indices = torch.topk(tensor.abs().view(-1), k)

        # Get signs
        signs = torch.sign(tensor.view(-1)[indices])
        values = values * signs

        return {
            'values': values,
            'indices': indices,
            'shape': tensor.shape,
            'compression_ratio': k / numel,
        }

    def decompress_topk(self, compressed):
        """Decompress top-k compressed tensor"""
        # Create zero tensor
        tensor = torch.zeros(compressed['shape']).view(-1)

        # Fill in top-k values
        tensor[compressed['indices']] = compressed['values']

        return tensor.view(compressed['shape'])

    def compress_quantize(self, tensor, num_bits=8):
        """
        Quantization: Reduce precision to fewer bits
        """
        # Find min and max
        min_val = tensor.min()
        max_val = tensor.max()

        # Quantize to num_bits
        scale = (max_val - min_val) / (2**num_bits - 1)
        quantized = ((tensor - min_val) / scale).round().to(torch.uint8)

        return {
            'quantized': quantized,
            'min_val': min_val,
            'max_val': max_val,
            'scale': scale,
            'shape': tensor.shape,
        }

    def decompress_quantize(self, compressed):
        """Decompress quantized tensor"""
        quantized = compressed['quantized'].to(torch.float32)
        tensor = quantized * compressed['scale'] + compressed['min_val']
        return tensor.view(compressed['shape'])

# Integrate with distributed training
class CompressedDDP(torch.nn.Module):
    """
    DDP with gradient compression
    """

    def __init__(self, model, compression_ratio=0.01):
        super().__init__()
        self.model = model
        self.compressor = GradientCompressor(compression_ratio)

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def backward_with_compression(self, loss):
        """
        Backward pass with gradient compression
        """
        # Compute gradients
        loss.backward()

        # Compress and communicate gradients
        for param in self.model.parameters():
            if param.grad is not None:
                # Compress
                compressed = self.compressor.compress_topk(param.grad)

                # AllReduce compressed values
                # (In practice, this needs custom NCCL ops)
                # For now, we'll demonstrate the concept

                # Decompress
                param.grad = self.compressor.decompress_topk(compressed)

# Benchmark compression
def benchmark_compression():
    """Compare communication time with and without compression"""
    sizes = [1024**2, 10*1024**2, 100*1024**2]  # 1MB, 10MB, 100MB elements

    print("\nGradient Compression Benchmark:")
    print("=" * 80)
    print(f"{'Size':<15} {'Uncompressed':<20} {'Compressed (1%)':<20} {'Speedup'}")
    print("-" * 80)

    compressor = GradientCompressor(compression_ratio=0.01)

    for size in sizes:
        tensor = torch.randn(size, device='cuda')

        # Uncompressed AllReduce
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(100):
            dist.all_reduce(tensor)
        torch.cuda.synchronize()
        uncompressed_time = (time.time() - start) / 100

        # Compressed communication
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(100):
            compressed = compressor.compress_topk(tensor)
            # AllReduce compressed values (simplified)
            dist.all_reduce(compressed['values'])
            dist.all_reduce(compressed['indices'])
        torch.cuda.synchronize()
        compressed_time = (time.time() - start) / 100

        speedup = uncompressed_time / compressed_time

        print(f"{size/1024**2:>8.0f} MB    "
              f"{uncompressed_time*1000:>12.2f} ms      "
              f"{compressed_time*1000:>12.2f} ms      "
              f"{speedup:>6.2f}x")

# Note: Real gradient compression requires:
# 1. Custom NCCL operations
# 2. Error feedback to compensate for compression loss
# 3. Careful tuning of compression ratio
```

### Gradient Accumulation

```python
def train_with_gradient_accumulation(
    model,
    train_loader,
    optimizer,
    accumulation_steps=4
):
    """
    Training with gradient accumulation

    Reduces communication frequency by N times
    """
    model.train()
    optimizer.zero_grad()

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.cuda(), target.cuda()

        # Forward pass
        output = model(data)
        loss = criterion(output, target)

        # Scale loss by accumulation steps
        loss = loss / accumulation_steps

        # Backward pass (accumulate gradients)
        loss.backward()

        # Update weights every accumulation_steps
        if (batch_idx + 1) % accumulation_steps == 0:
            # Gradient communication happens here (for DDP)
            optimizer.step()
            optimizer.zero_grad()

    # Performance benefit calculation
    baseline_comm_freq = len(train_loader)  # Communication per step
    optimized_comm_freq = len(train_loader) / accumulation_steps

    print(f"\nCommunication Reduction:")
    print(f"  Baseline: {baseline_comm_freq} communications/epoch")
    print(f"  With accumulation: {optimized_comm_freq:.0f} communications/epoch")
    print(f"  Reduction: {accumulation_steps}x")
```

## Memory Optimization

### Gradient Checkpointing

```python
import torch.utils.checkpoint as checkpoint

class CheckpointedModel(torch.nn.Module):
    """
    Model with gradient checkpointing

    Trades compute for memory
    """

    def __init__(self, num_layers=12):
        super().__init__()

        # Create layers
        self.layers = torch.nn.ModuleList([
            TransformerLayer() for _ in range(num_layers)
        ])

    def forward(self, x):
        """Forward pass with gradient checkpointing"""
        for layer in self.layers:
            # Use checkpoint for each layer
            # Activations are not saved, recomputed in backward pass
            x = checkpoint.checkpoint(layer, x, use_reentrant=False)

        return x

# Measure memory savings
def compare_memory_usage():
    """Compare memory usage with and without checkpointing"""
    batch_size = 32
    seq_len = 512
    hidden_size = 768

    input_data = torch.randn(batch_size, seq_len, hidden_size, device='cuda')

    # Without checkpointing
    torch.cuda.reset_peak_memory_stats()
    model_regular = RegularModel().cuda()
    output = model_regular(input_data)
    loss = output.sum()
    loss.backward()
    memory_regular = torch.cuda.max_memory_allocated() / (1024**3)  # GB

    # With checkpointing
    torch.cuda.reset_peak_memory_stats()
    model_checkpointed = CheckpointedModel().cuda()
    output = model_checkpointed(input_data)
    loss = output.sum()
    loss.backward()
    memory_checkpointed = torch.cuda.max_memory_allocated() / (1024**3)  # GB

    print("\nMemory Usage Comparison:")
    print(f"  Without checkpointing: {memory_regular:.2f} GB")
    print(f"  With checkpointing: {memory_checkpointed:.2f} GB")
    print(f"  Savings: {(1 - memory_checkpointed/memory_regular)*100:.1f}%")
```

### ZeRO Optimizer

```python
# ZeRO (Zero Redundancy Optimizer) concept
# Partitions optimizer states, gradients, and parameters across GPUs

class ZeROStage1Optimizer:
    """
    ZeRO Stage 1: Partition optimizer states
    """

    def __init__(self, params, lr=1e-3):
        self.params = list(params)
        self.lr = lr

        # Get distributed info
        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()

        # Partition parameters across ranks
        self.param_groups = self._partition_parameters()

        # Create optimizer for this rank's partition
        self.optimizer = torch.optim.Adam(
            self.param_groups[self.rank],
            lr=self.lr
        )

    def _partition_parameters(self):
        """Partition parameters across ranks"""
        params_per_rank = len(self.params) // self.world_size

        groups = []
        for rank in range(self.world_size):
            start_idx = rank * params_per_rank
            end_idx = start_idx + params_per_rank if rank < self.world_size - 1 else len(self.params)
            groups.append(self.params[start_idx:end_idx])

        return groups

    def step(self):
        """
        Optimizer step with ZeRO

        Each rank updates its partition, then broadcasts to others
        """
        # Update this rank's partition
        self.optimizer.step()

        # Broadcast updated parameters to all ranks
        for param in self.param_groups[self.rank]:
            dist.broadcast(param.data, src=self.rank)

# Memory savings calculation
def calculate_zero_savings(num_params, world_size):
    """
    Calculate memory savings with ZeRO

    Args:
        num_params: Number of model parameters
        world_size: Number of GPUs
    """
    # Standard optimizer (Adam)
    param_memory = num_params * 4 / 1e9  # FP32, GB
    grad_memory = param_memory
    optimizer_memory = num_params * 8 / 1e9  # 2 states (momentum, variance)
    total_standard = param_memory + grad_memory + optimizer_memory

    # ZeRO Stage 1: Partition optimizer states
    zero1_optimizer = optimizer_memory / world_size
    total_zero1 = param_memory + grad_memory + zero1_optimizer

    # ZeRO Stage 2: Partition gradients too
    zero2_grad = grad_memory / world_size
    total_zero2 = param_memory + zero2_grad + zero1_optimizer

    # ZeRO Stage 3: Partition parameters too
    zero3_param = param_memory / world_size
    total_zero3 = zero3_param + zero2_grad + zero1_optimizer

    print(f"\nZeRO Memory Savings ({num_params/1e9:.0f}B params, {world_size} GPUs):")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Memory/GPU (GB)':<20} {'Savings'}")
    print("-" * 80)
    print(f"{'Standard':<20} {total_standard:>15.2f}       {'baseline'}")
    print(f"{'ZeRO Stage 1':<20} {total_zero1:>15.2f}       "
          f"{(1-total_zero1/total_standard)*100:>5.1f}%")
    print(f"{'ZeRO Stage 2':<20} {total_zero2:>15.2f}       "
          f"{(1-total_zero2/total_standard)*100:>5.1f}%")
    print(f"{'ZeRO Stage 3':<20} {total_zero3:>15.2f}       "
          f"{(1-total_zero3/total_standard)*100:>5.1f}%")

calculate_zero_savings(num_params=175e9, world_size=64)
```

## I/O and Data Loading Optimization

### Optimized DataLoader

```python
class OptimizedDataLoader:
    """
    Optimized DataLoader configuration
    """

    @staticmethod
    def create_dataloader(dataset, batch_size, num_workers='auto', **kwargs):
        """
        Create optimized DataLoader

        Args:
            dataset: Dataset
            batch_size: Batch size
            num_workers: Number of workers ('auto' to auto-detect)
        """
        if num_workers == 'auto':
            # Rule of thumb: 4 workers per GPU
            num_workers = 4 * torch.cuda.device_count() if torch.cuda.is_available() else 4

        return torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            num_workers=num_workers,
            pin_memory=True,              # Fast GPU transfer
            persistent_workers=True,       # Keep workers alive
            prefetch_factor=2,            # Prefetch batches
            drop_last=True,               # For batch norm stability
            **kwargs
        )

# Data prefetching to GPU
class CudaDataLoader:
    """
    DataLoader wrapper that prefetches to GPU
    """

    def __init__(self, dataloader, device):
        self.dataloader = dataloader
        self.device = device
        self.stream = torch.cuda.Stream()

    def __iter__(self):
        loader_iter = iter(self.dataloader)

        # Prefetch first batch
        try:
            with torch.cuda.stream(self.stream):
                next_data, next_target = next(loader_iter)
                next_data = next_data.to(self.device, non_blocking=True)
                next_target = next_target.to(self.device, non_blocking=True)
        except StopIteration:
            return

        while True:
            torch.cuda.current_stream().wait_stream(self.stream)
            data, target = next_data, next_target

            try:
                # Prefetch next batch
                with torch.cuda.stream(self.stream):
                    next_data, next_target = next(loader_iter)
                    next_data = next_data.to(self.device, non_blocking=True)
                    next_target = next_target.to(self.device, non_blocking=True)
            except StopIteration:
                yield data, target
                break

            yield data, target

# Usage
regular_loader = torch.utils.data.DataLoader(dataset, batch_size=32)
optimized_loader = CudaDataLoader(regular_loader, device='cuda')

for data, target in optimized_loader:
    # Data is already on GPU!
    output = model(data)
```

## End-to-End Optimization Strategy

### Comprehensive Optimization Checklist

```python
OPTIMIZATION_CHECKLIST = {
    'Model Architecture': [
        '☐ Use efficient architectures (MobileNet, EfficientNet)',
        '☐ Remove unnecessary operations',
        '☐ Fuse operations where possible',
        '☐ Use torch.compile() for automatic optimization',
    ],
    'Mixed Precision': [
        '☐ Enable AMP with torch.cuda.amp',
        '☐ Use BF16 on A100/H100',
        '☐ Keep numerically sensitive ops in FP32',
    ],
    'Data Loading': [
        '☐ Use num_workers >= 4',
        '☐ Enable pin_memory=True',
        '☐ Use persistent_workers=True',
        '☐ Prefetch data to GPU',
        '☐ Optimize data preprocessing',
    ],
    'Communication': [
        '☐ Use gradient accumulation for large models',
        '☐ Enable NCCL optimizations',
        '☐ Use NVLink for intra-node',
        '☐ Use InfiniBand for inter-node',
        '☐ Consider gradient compression',
    ],
    'Memory': [
        '☐ Use gradient checkpointing for large models',
        '☐ Enable ZeRO for very large models',
        '☐ Optimize batch size',
        '☐ Clear cache when needed',
    ],
    'Computation': [
        '☐ Enable cudnn.benchmark',
        '☐ Use torch.compile() (PyTorch 2.0+)',
        '☐ Optimize tensor operations',
        '☐ Avoid unnecessary data transfers',
    ],
    'Monitoring': [
        '☐ Profile with PyTorch Profiler',
        '☐ Monitor GPU utilization',
        '☐ Track scaling efficiency',
        '☐ Monitor network bandwidth',
    ],
}

def print_optimization_checklist():
    """Print optimization checklist"""
    print("\nDistributed Training Optimization Checklist")
    print("=" * 80)
    for category, items in OPTIMIZATION_CHECKLIST.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")
    print("\n" + "=" * 80)

print_optimization_checklist()
```

## Summary

Key takeaways:

1. **Profile first** - identify bottlenecks before optimizing
2. **Communication is often the bottleneck** in distributed training
3. **Gradient accumulation** reduces communication frequency
4. **Mixed precision** reduces memory and speeds up computation
5. **Gradient checkpointing** trades compute for memory
6. **Data loading** can be a hidden bottleneck
7. **Systematic approach** - optimize one component at a time

**Optimization Priority:**
1. Enable mixed precision (biggest impact, least effort)
2. Optimize data loading (pin_memory, num_workers)
3. Use gradient accumulation (if communication-bound)
4. Apply gradient checkpointing (if memory-bound)
5. Consider ZeRO (for very large models)
6. Profile and iterate

## Further Reading

- [PyTorch Performance Tuning Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [NVIDIA Deep Learning Performance Guide](https://docs.nvidia.com/deeplearning/performance/)
- "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" (Rajbhandari et al., 2020)

## Conclusion

This concludes Module 202 on Distributed Training at Scale. You now have the knowledge to design, implement, and optimize production-scale distributed training systems.

**Next Steps:**
- Complete the hands-on labs
- Take the module quiz
- Start planning your distributed training project
