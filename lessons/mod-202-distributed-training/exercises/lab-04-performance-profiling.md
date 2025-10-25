# Lab 04: Performance Profiling and Optimization

## Lab Overview

**Duration**: 4-5 hours  
**Difficulty**: Advanced  
**Prerequisites**: Labs 01-03, profiling tools knowledge

Systematically profile and optimize distributed training performance using industry-standard tools.

## Learning Objectives

- Profile distributed training with PyTorch Profiler
- Use NVIDIA Nsight Systems for GPU profiling
- Identify and resolve performance bottlenecks
- Optimize communication patterns
- Apply memory optimizations
- Measure optimization impact

## Exercise 1: Baseline Profiling

### Task 1.1: Profile with PyTorch Profiler

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[
        profiler.ProfilerActivity.CPU,
        profiler.ProfilerActivity.CUDA,
    ],
    record_shapes=True,
    profile_memory=True,
    with_stack=True,
) as prof:
    train_epoch(model, train_loader, optimizer)

# Analyze results
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))
```

**TODO**:
1. Profile baseline training
2. Identify top 5 time-consuming operations
3. Calculate GPU utilization: __________%
4. Identify bottlenecks

## Exercise 2: Communication Profiling

### Task 2.1: Measure AllReduce Overhead

```python
def measure_communication_overhead():
    # Profile with communication
    # Profile without communication (no_sync context)
    # Calculate overhead percentage
    pass
```

**TODO**: Complete analysis:
- Compute time: __________
- Communication time: __________
- Communication overhead: __________%
- Optimization recommendations: __________

## Exercise 3: Apply Optimizations

### Task 3.1: Enable Mixed Precision

Add AMP and measure impact:

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    output = model(data)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

**TODO**: Record improvements:
- Baseline throughput: __________
- With AMP throughput: __________
- Speedup: __________x
- Memory savings: __________%

### Task 3.2: Gradient Accumulation

Implement and measure gradient accumulation.

### Task 3.3: Data Loading Optimization

Optimize DataLoader configuration.

## Exercise 4: End-to-End Optimization

Apply all optimizations and measure cumulative impact.

**TODO**: Complete optimization summary:

| Optimization | Throughput | Speedup | Memory | Accuracy |
|--------------|-----------|---------|---------|----------|
| Baseline     |           | 1.0x    |         |          |
| + AMP        |           |         |         |          |
| + Grad Accum |           |         |         |          |
| + DataLoader |           |         |         |          |
| + All        |           |         |         |          |

## Challenge: Custom CUDA Kernel

Write and profile custom CUDA kernel for model operation.

**Deliverables**:
1. Profiling reports (PyTorch Profiler, Nsight)
2. Before/after performance comparison
3. Optimization recommendations document
4. 1000-word analysis of results

---

**Estimated Time**: 4-5 hours  
**Difficulty**: Advanced
