# Lecture 04: GPU Profiling and Performance Analysis

## Learning Objectives

By the end of this lecture, you will be able to:

- Design systematic GPU profiling workflows using Nsight Systems and Nsight Compute to identify and diagnose performance bottlenecks in ML training and inference pipelines
- Analyze GPU kernel performance using roofline analysis, occupancy metrics, and memory bandwidth utilization to determine optimization priorities
- Implement targeted optimizations based on profiling insights including kernel fusion, memory coalescing, and asynchronous operations to eliminate identified bottlenecks
- Configure NVTX annotations and custom profiling ranges in training code to precisely measure performance of specific operations and isolate problem areas
- Evaluate trade-offs between profiling overhead and measurement precision to select appropriate profiling strategies for development vs production environments
- Interpret Tensor Core utilization metrics and implement optimizations (alignment, layout, precision) to maximize Tensor Core usage in deep learning workloads
- Design performance regression detection systems that automatically profile training runs and alert on performance degradation compared to baseline metrics
- Troubleshoot common GPU performance issues including CPU-GPU synchronization stalls, data loading bottlenecks, and suboptimal kernel launch configurations using profiling tools

## Table of Contents
1. [Introduction to GPU Profiling](#introduction-to-gpu-profiling)
2. [Profiling Methodology](#profiling-methodology)
3. [NVIDIA Nsight Systems](#nvidia-nsight-systems)
4. [NVIDIA Nsight Compute](#nvidia-nsight-compute)
5. [Performance Metrics](#performance-metrics)
6. [Identifying Bottlenecks](#identifying-bottlenecks)
7. [Optimization Strategies](#optimization-strategies)
8. [Production Profiling](#production-profiling)

## Introduction to GPU Profiling

GPU profiling is essential for understanding and optimizing performance in AI infrastructure. Without profiling, you're optimizing blindly.

### Why Profile?

1. **Identify bottlenecks**: CPU vs. GPU, memory vs. compute
2. **Optimize resource utilization**: Are you using all available GPU resources?
3. **Debug performance issues**: Why is training slow?
4. **Validate optimizations**: Did your changes actually help?
5. **Cost optimization**: Better performance = fewer GPUs needed

### Performance Goals

For ML workloads, aim for:
- **GPU Utilization**: >80% during training
- **Memory Bandwidth Utilization**: >60% for memory-bound ops
- **Tensor Core Utilization**: >50% for mixed precision training
- **Multi-GPU Scaling**: >90% efficiency for 2-8 GPUs

### Profiling Tools Overview

```
Tool Hierarchy:
┌─────────────────────────────────────┐
│ nvidia-smi (System-level monitoring)│
├─────────────────────────────────────┤
│ Nsight Systems (Timeline analysis)  │
├─────────────────────────────────────┤
│ Nsight Compute (Kernel analysis)    │
├─────────────────────────────────────┤
│ CUDA Profiler API (Custom metrics)  │
└─────────────────────────────────────┘
```

**Tool Selection:**
- **nvidia-smi**: Quick health checks, real-time monitoring
- **Nsight Systems**: System-wide analysis, find CPU-GPU gaps
- **Nsight Compute**: Deep kernel analysis, optimize specific kernels
- **Framework Profilers**: PyTorch Profiler, TensorBoard profiler

## Profiling Methodology

Follow a systematic approach to profiling:

### Step 1: Baseline Measurement

Establish baseline metrics before optimization:

```bash
# Run training for 100 iterations
python train.py --iterations 100

# Record:
# - Total time
# - Iterations per second
# - GPU utilization (nvidia-smi)
# - Memory usage
```

### Step 2: System-Level Profiling

Use Nsight Systems to get overview:

```bash
# Profile training script
nsys profile -o baseline_profile python train.py --iterations 100

# Open in GUI
nsys-ui baseline_profile.qdrep
```

Look for:
- CPU-GPU gaps (idle time)
- Kernel launch overhead
- Data transfer bottlenecks
- Framework overhead

### Step 3: Kernel-Level Profiling

Use Nsight Compute for specific kernels:

```bash
# Profile specific kernel
ncu --kernel-name "kernelName" -o kernel_profile python train.py

# Full kernel analysis
ncu --set full -o detailed_profile python train.py
```

### Step 4: Optimize

Make targeted optimizations based on findings.

### Step 5: Validate

Re-profile and compare:

```bash
# Compare before and after
nsys stats baseline_profile.qdrep > baseline_stats.txt
nsys stats optimized_profile.qdrep > optimized_stats.txt
diff baseline_stats.txt optimized_stats.txt
```

### Profiling Best Practices

1. **Profile representative workloads**: Use real data and batch sizes
2. **Warm up before profiling**: Skip initial iterations
3. **Profile enough iterations**: 100-1000 iterations for statistics
4. **Isolate components**: Profile training, inference, data loading separately
5. **Use smaller models for iteration**: Faster profiling cycles
6. **Document everything**: Keep notes on what you profiled and why

## NVIDIA Nsight Systems

Nsight Systems provides system-wide timeline analysis.

### Installing Nsight Systems

```bash
# Nsight Systems is included in CUDA Toolkit
which nsys

# If not installed, download from NVIDIA website
# https://developer.nvidia.com/nsight-systems

# Version check
nsys --version
```

### Basic Profiling

```bash
# Profile Python script
nsys profile -o my_profile python train.py

# Profile with CUDA API trace
nsys profile --trace=cuda,cudnn,cublas -o my_profile python train.py

# Profile specific process
nsys profile --trace=cuda -o my_profile -p <PID>

# Profile multi-GPU training
nsys profile --trace=cuda,nvtx,mpi -o multi_gpu python -m torch.distributed.launch train.py
```

### Command-Line Options

```bash
# Full command with common options
nsys profile \
    --trace=cuda,nvtx,cudnn,cublas \
    --output=profile_output \
    --force-overwrite=true \
    --capture-range=cudaProfilerApi \
    --stop-on-exit=true \
    --export=sqlite \
    python train.py

# Options explained:
# --trace: What to profile (cuda, nvtx, osrt, cudnn, cublas, nvmedia, etc.)
# --output: Output file name
# --force-overwrite: Overwrite existing file
# --capture-range: When to start profiling (cudaProfilerApi = manual control)
# --stop-on-exit: Stop profiling when application exits
# --export: Export format (sqlite for analysis)
```

### Using NVTX for Code Annotation

NVTX (NVIDIA Tools Extension) adds markers to timeline:

```python
import torch.cuda.nvtx as nvtx

def train_step(model, data, target):
    # Annotate forward pass
    nvtx.range_push("forward")
    output = model(data)
    loss = criterion(output, target)
    nvtx.range_pop()

    # Annotate backward pass
    nvtx.range_push("backward")
    loss.backward()
    nvtx.range_pop()

    # Annotate optimizer step
    nvtx.range_push("optimizer")
    optimizer.step()
    optimizer.zero_grad()
    nvtx.range_pop()

# Color-coded ranges
with nvtx.range("data_loading", color="blue"):
    data, target = next(dataloader)

with nvtx.range("training_step", color="green"):
    train_step(model, data, target)
```

### Analyzing Nsight Systems Output

Open profile in GUI:

```bash
nsys-ui my_profile.qdrep
```

**Key Views:**

1. **Timeline View**: Shows GPU activity over time
   - CUDA API calls
   - Kernel executions
   - Memory transfers
   - CPU activity

2. **GPU Metrics View**: GPU utilization, memory bandwidth

3. **Statistics View**: Summary of kernels, API calls

**What to Look For:**

```
Good GPU Utilization:
CPU ████████████████████████████
GPU ████████████████████████████
    └─ Continuous GPU activity

Bad GPU Utilization:
CPU ████  ████  ████  ████
GPU  ████  ████  ████  ████
     └─ Gaps indicate CPU bottleneck
```

### Common Issues Identified

**1. CPU Bottleneck (Data Loading)**
```
Timeline:
[DataLoader] [Kernel] [Gap] [DataLoader] [Kernel] [Gap]
             └─ GPU idle while CPU prepares data

Solution:
- Increase num_workers in DataLoader
- Use pinned memory
- Prefetch data
```

**2. Kernel Launch Overhead**
```
Timeline:
[Launch][Kernel][Launch][Kernel][Launch][Kernel]
└─ Many small kernels with launch overhead

Solution:
- Fuse operations
- Use torch.jit.trace() to fuse ops
- Increase batch size
```

**3. Host-Device Synchronization**
```
Timeline:
[Kernel] [cudaDeviceSynchronize] [Gap] [Kernel]
         └─ Unnecessary synchronization

Solution:
- Remove explicit synchronizations
- Use async operations
- Profile with --trace=cuda to identify sync points
```

### Nsight Systems Reports

Generate text reports:

```bash
# Generate statistics report
nsys stats my_profile.qdrep

# Export to CSV
nsys export my_profile.qdrep -o output_dir

# Query specific data
nsys stats my_profile.qdrep --report cuda_gpu_kern_sum
nsys stats my_profile.qdrep --report cuda_gpu_mem_time_sum
nsys stats my_profile.qdrep --report nvtx_sum
```

## NVIDIA Nsight Compute

Nsight Compute provides detailed kernel-level analysis.

### Installing Nsight Compute

```bash
# Included in CUDA Toolkit
which ncu

# Version check
ncu --version

# Launch GUI
ncu-ui
```

### Basic Kernel Profiling

```bash
# Profile all kernels
ncu -o kernel_profile python train.py

# Profile specific kernel by name
ncu --kernel-name "volta_sgemm" -o gemm_profile python train.py

# Profile first N kernel launches
ncu --launch-count 10 -o first_10_kernels python train.py

# Profile with specific metrics
ncu --metrics sm__throughput.avg.pct_of_peak_sustained_elapsed \
    --metrics dram__throughput.avg.pct_of_peak_sustained_elapsed \
    -o metrics_profile python train.py
```

### Profiling Sets

Nsight Compute has predefined metric sets:

```bash
# Quick profiling (fewer metrics, faster)
ncu --set brief -o quick_profile python train.py

# Full profiling (all metrics, slower)
ncu --set full -o detailed_profile python train.py

# Available sets:
# - brief: Essential metrics
# - default: Common metrics
# - full: All available metrics
# - detailed: Extended metrics
```

### Key Metrics

**1. SM (Streaming Multiprocessor) Metrics:**
- `sm__throughput.avg.pct_of_peak_sustained_elapsed`: SM utilization
- `sm__warps_active.avg.pct_of_peak_sustained_active`: Warp occupancy
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed`: Tensor Core usage

**2. Memory Metrics:**
- `dram__throughput.avg.pct_of_peak_sustained_elapsed`: DRAM bandwidth utilization
- `l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum`: Global memory loads
- `l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum`: Global memory stores

**3. Compute Metrics:**
- `sm__sass_thread_inst_executed_op_fadd_pred_on.sum`: FP32 add operations
- `sm__sass_thread_inst_executed_op_fmul_pred_on.sum`: FP32 multiply operations
- `sm__sass_thread_inst_executed_op_hmma_pred_on.sum`: Tensor Core operations

### Roofline Analysis

Nsight Compute includes roofline analysis:

```bash
# Profile with roofline
ncu --set roofline -o roofline_profile python train.py

# Open in GUI to see roofline chart
ncu-ui roofline_profile.ncu-rep
```

Roofline shows:
- Compute-bound vs. memory-bound regions
- Achieved performance vs. hardware limits
- Optimization opportunities

```
Roofline Chart:
         Peak FLOPS
              │
         ╱╲   │
        ╱  ╲  │
       ╱    ╲ │
      ╱      ╲│
─────┴────────●─────── Memory Bandwidth
              │
         Your kernel location
```

**Interpreting Roofline:**
- **Top left (compute-bound)**: Optimize arithmetic operations, use Tensor Cores
- **Bottom right (memory-bound)**: Optimize memory access, use shared memory
- **Below line**: Not achieving peak for your arithmetic intensity

### Analyzing Kernel Performance

```bash
# Profile with GUI launch
ncu-ui

# In GUI:
# 1. Select application and arguments
# 2. Choose metrics or sets
# 3. Run profile
# 4. Analyze results
```

**Key Analysis Sections:**

1. **Summary**: High-level performance overview
   - Speed of Light (SOL): How close to theoretical peak
   - Memory throughput utilization
   - Compute throughput utilization

2. **Details**: Detailed metrics by category
   - Memory Workload Analysis
   - Compute Workload Analysis
   - Launch Statistics
   - Occupancy

3. **Source View**: Line-by-line SASS/PTX analysis
   - Instruction count per source line
   - Memory access patterns
   - Stalls and inefficiencies

### Optimizing Based on Metrics

**Low SM Utilization (<50%):**
```
Problem: Not enough threads/blocks
Solution:
- Increase grid/block dimensions
- Check for launch configuration issues
- Look for kernel serialization
```

**Low Tensor Core Utilization:**
```
Problem: Not using Tensor Cores effectively
Solution:
- Use mixed precision (FP16/BF16)
- Ensure tensor dimensions are multiples of 8/16
- Use cuDNN/cuBLAS operations
```

**High Memory Latency:**
```
Problem: Poor memory access patterns
Solution:
- Coalesce memory accesses
- Use shared memory
- Increase occupancy to hide latency
```

**Low Occupancy:**
```
Problem: Too many registers or shared memory per thread/block
Solution:
- Reduce register usage (simplify kernel)
- Reduce shared memory usage
- Adjust block size
```

### Command-Line Analysis

```bash
# Generate text report
ncu --csv --log-file results.csv python train.py

# Query specific metrics
ncu --query-metrics
ncu --query-metrics-by-name "sm__throughput"

# Compare profiles
ncu --import baseline.ncu-rep --import optimized.ncu-rep
```

## Performance Metrics

### GPU Utilization Metrics

**GPU Utilization** (nvidia-smi):
```bash
nvidia-smi dmon -s u -c 100
# Shows GPU utilization over time

# Good: 80-100%
# Acceptable: 60-80%
# Poor: <60%
```

**Memory Utilization**:
```bash
nvidia-smi dmon -s m -c 100
# Shows memory bandwidth utilization
```

**Power Usage**:
```bash
nvidia-smi dmon -s p -c 100
# Power usage indicates GPU activity level
# Max power = GPU working hard
```

### Framework-Level Metrics

**PyTorch Profiler:**

```python
import torch
from torch.profiler import profile, ProfilerActivity, schedule

def train_step(model, data, target):
    output = model(data)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

# Profiling with PyTorch
with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
    with_stack=True
) as prof:
    for i in range(100):
        train_step(model, data, target)

# Print summary
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

# Export to Chrome trace
prof.export_chrome_trace("trace.json")
# Open trace.json in chrome://tracing

# Export to TensorBoard
from torch.profiler import tensorboard_trace_handler
with profile(
    activities=[ProfilerActivity.CUDA],
    on_trace_ready=tensorboard_trace_handler('./log/resnet50')
) as prof:
    for i in range(100):
        train_step(model, data, target)
        prof.step()  # Signal end of iteration
```

**TensorFlow Profiler:**

```python
import tensorflow as tf

# Enable profiler
tf.profiler.experimental.start('logdir')

# Train for some steps
for step in range(1000):
    train_step()
    if step == 100:
        tf.profiler.experimental.stop()

# View in TensorBoard
# tensorboard --logdir logdir
```

### Custom Metrics with CUDA Events

```cpp
#include <cuda_runtime.h>

// Create events
cudaEvent_t start, stop;
cudaEventCreate(&start);
cudaEventCreate(&stop);

// Record start
cudaEventRecord(start);

// Execute kernel
kernel<<<blocks, threads>>>(args);

// Record stop
cudaEventRecord(stop);
cudaEventSynchronize(stop);

// Calculate elapsed time
float milliseconds = 0;
cudaEventElapsedTime(&milliseconds, start, stop);
printf("Kernel execution time: %.3f ms\n", milliseconds);

// Cleanup
cudaEventDestroy(start);
cudaEventDestroy(stop);
```

```python
# PyTorch version
import torch

start_event = torch.cuda.Event(enable_timing=True)
end_event = torch.cuda.Event(enable_timing=True)

start_event.record()
# ... operations ...
end_event.record()

torch.cuda.synchronize()
elapsed_time = start_event.elapsed_time(end_event)
print(f"Time: {elapsed_time} ms")
```

## Identifying Bottlenecks

### CPU vs. GPU Bottleneck

**Test:** Compare GPU utilization patterns

```python
import time
import torch
from torch.utils.data import DataLoader

def profile_dataloader(dataloader):
    """Profile data loading time"""
    data_time = 0
    start = time.time()
    for i, (data, target) in enumerate(dataloader):
        data_time += time.time() - start
        if i >= 100:
            break
        start = time.time()
    print(f"Data loading time: {data_time:.3f}s for 100 batches")
    print(f"Avg per batch: {data_time/100*1000:.3f}ms")

# Test different num_workers
for num_workers in [0, 2, 4, 8]:
    dataloader = DataLoader(dataset, batch_size=32, num_workers=num_workers)
    print(f"\nnum_workers={num_workers}")
    profile_dataloader(dataloader)
```

**Solution for CPU bottleneck:**
```python
# Increase num_workers
dataloader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=8,  # More parallel data loading
    pin_memory=True,  # Faster H2D transfer
    persistent_workers=True  # Keep workers alive
)
```

### Memory vs. Compute Bottleneck

Use Nsight Compute to determine:

```bash
ncu --set full -o analysis python train.py

# Check these metrics in ncu-ui:
# - SOL Memory (Speed of Light Memory)
# - SOL Compute (Speed of Light Compute)

# If SOL Memory > SOL Compute: Memory-bound
# If SOL Compute > SOL Memory: Compute-bound
```

**Memory-bound optimization:**
- Reduce memory transfers
- Fuse operations
- Use shared memory
- Optimize data layout

**Compute-bound optimization:**
- Use Tensor Cores (mixed precision)
- Increase batch size
- Optimize algorithms
- Use cuDNN/cuBLAS

### Multi-GPU Communication Bottleneck

```python
import torch
import torch.distributed as dist

def profile_communication():
    """Profile all-reduce communication time"""
    tensor = torch.randn(1000000).cuda()

    # Warm up
    for _ in range(10):
        dist.all_reduce(tensor)

    # Profile
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(100):
        dist.all_reduce(tensor)
    torch.cuda.synchronize()
    elapsed = time.time() - start

    print(f"All-reduce time: {elapsed/100*1000:.3f}ms")
    print(f"Bandwidth: {tensor.numel() * 4 / elapsed / 1e9:.3f} GB/s")

# Run on each GPU
profile_communication()
```

**Solution:**
- Use NCCL backend
- Enable NVLink if available
- Overlap communication with computation
- Use gradient accumulation to reduce frequency

## Optimization Strategies

### Strategy 1: Increase Batch Size

Larger batches = better GPU utilization

```python
# Gradually increase batch size
batch_sizes = [32, 64, 128, 256, 512]

for bs in batch_sizes:
    try:
        dataloader = DataLoader(dataset, batch_size=bs)
        model = Model().cuda()
        optimizer = optim.SGD(model.parameters(), lr=0.01)

        # Warmup
        for _ in range(10):
            data, target = next(iter(dataloader))
            output = model(data.cuda())
            loss = criterion(output, target.cuda())
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        # Measure throughput
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(100):
            data, target = next(iter(dataloader))
            output = model(data.cuda())
            loss = criterion(output, target.cuda())
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        torch.cuda.synchronize()
        elapsed = time.time() - start

        throughput = 100 * bs / elapsed
        print(f"Batch size {bs}: {throughput:.2f} samples/sec")

    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"Batch size {bs}: OOM")
            break
```

### Strategy 2: Mixed Precision Training

Use automatic mixed precision (AMP):

```python
from torch.cuda.amp import autocast, GradScaler

model = Model().cuda()
optimizer = optim.Adam(model.parameters())
scaler = GradScaler()

for data, target in dataloader:
    optimizer.zero_grad()

    # Mixed precision forward pass
    with autocast():
        output = model(data)
        loss = criterion(output, target)

    # Scaled backward pass
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# Profile before and after to see speedup
# Expect 2-3x speedup on Tensor Cores
```

### Strategy 3: Kernel Fusion

Fuse operations to reduce memory traffic:

```python
# Before: Separate operations (multiple kernel launches)
x = x + bias
x = torch.relu(x)
x = x * scale

# After: Fused (torch.jit or custom kernel)
@torch.jit.script
def fused_bias_relu_scale(x, bias, scale):
    return torch.relu(x + bias) * scale

x = fused_bias_relu_scale(x, bias, scale)

# Or use in-place operations
x.add_(bias).relu_().mul_(scale)
```

### Strategy 4: Asynchronous Operations

Overlap computation and communication:

```python
import torch.cuda.comm as comm

# Asynchronous H2D transfer
stream = torch.cuda.Stream()
with torch.cuda.stream(stream):
    data_gpu = data.cuda(non_blocking=True)
    target_gpu = target.cuda(non_blocking=True)

# Meanwhile, do other work on default stream
# ...

# Wait for transfer to complete
torch.cuda.current_stream().wait_stream(stream)

# Now use data_gpu
output = model(data_gpu)
```

## Production Profiling

### Continuous Monitoring

Set up monitoring for production training:

```python
import time
import torch
from collections import deque

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.batch_times = deque(maxlen=window_size)
        self.gpu_memory = deque(maxlen=window_size)

    def record_batch(self):
        # Record GPU memory
        memory_allocated = torch.cuda.memory_allocated() / 1e9
        self.gpu_memory.append(memory_allocated)

        # Record batch time
        torch.cuda.synchronize()
        self.batch_times.append(time.time())

    def get_stats(self):
        if len(self.batch_times) < 2:
            return {}

        # Calculate throughput
        times = list(self.batch_times)
        durations = [times[i+1] - times[i] for i in range(len(times)-1)]
        avg_batch_time = sum(durations) / len(durations)

        return {
            'avg_batch_time_ms': avg_batch_time * 1000,
            'throughput_samples_sec': batch_size / avg_batch_time,
            'avg_gpu_memory_gb': sum(self.gpu_memory) / len(self.gpu_memory)
        }

# Usage
monitor = PerformanceMonitor()

for epoch in range(num_epochs):
    for batch_idx, (data, target) in enumerate(dataloader):
        # Training step
        train_step(model, data, target)

        # Record metrics
        monitor.record_batch()

        if batch_idx % 100 == 0:
            stats = monitor.get_stats()
            print(f"Epoch {epoch}, Batch {batch_idx}: {stats}")
```

### Alerting on Performance Degradation

```python
class PerformanceAlerter:
    def __init__(self, baseline_throughput, threshold=0.9):
        self.baseline = baseline_throughput
        self.threshold = threshold

    def check(self, current_throughput):
        ratio = current_throughput / self.baseline
        if ratio < self.threshold:
            self.alert(f"Performance degraded: {ratio:.2%} of baseline")

    def alert(self, message):
        # Send alert (Slack, email, PagerDuty, etc.)
        print(f"ALERT: {message}")
        # TODO: Integrate with alerting system
```

## Summary

Key profiling takeaways:

1. **Always profile before optimizing**: Don't guess where bottlenecks are
2. **Use right tool for the job**: Nsight Systems for overview, Nsight Compute for kernels
3. **Look for low-hanging fruit**: CPU bottlenecks, small batch sizes, synchronization
4. **Optimize iteratively**: Profile → Optimize → Validate → Repeat
5. **Monitor production**: Continuous performance tracking

## Hands-on Exercise

Profile a training script:

```bash
# 1. System-level profile
nsys profile --trace=cuda,nvtx -o system_profile python train.py

# 2. View timeline
nsys-ui system_profile.qdrep

# 3. Kernel-level profile
ncu --set full -o kernel_profile python train.py

# 4. Analyze specific kernel
ncu-ui kernel_profile.ncu-rep

# TODO: Identify and fix top 3 performance bottlenecks
```

## Further Reading

- Nsight Systems User Guide: https://docs.nvidia.com/nsight-systems/
- Nsight Compute User Guide: https://docs.nvidia.com/nsight-compute/
- NVIDIA Deep Learning Performance Guide: https://docs.nvidia.com/deeplearning/performance/

---

**Next Lecture**: Multi-GPU Strategies and NVLink
