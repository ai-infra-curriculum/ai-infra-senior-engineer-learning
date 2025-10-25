# Lab 02: GPU Profiling and Performance Optimization

## Lab Overview

**Duration**: 3-4 hours
**Difficulty**: Intermediate to Advanced
**Prerequisites**: Lecture 04 (GPU Profiling), Lecture 02 (GPU Architecture)

In this lab, you will profile a GPU-accelerated ML workload, identify performance bottlenecks, and apply optimizations to improve throughput.

## Learning Objectives

1. Use Nsight Systems for system-wide profiling
2. Use Nsight Compute for kernel-level analysis
3. Identify and fix common GPU performance issues
4. Optimize data loading and preprocessing pipelines
5. Improve GPU utilization from <60% to >80%

## Lab Setup

### Prerequisites
```bash
# Install profiling tools (part of CUDA Toolkit)
which nsys
which ncu

# Install PyTorch and dependencies
pip install torch torchvision matplotlib pandas

# Verify GPU access
nvidia-smi
```

## Part 1: Baseline Profiling

### Exercise 1.1: Profile a Training Script

We'll start with an intentionally suboptimal training script and profile it.

**training_unoptimized.py:**
```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import time

class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 28 * 28, 512)
        self.fc2 = nn.Linear(512, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        # Intentionally inefficient: multiple small operations
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)

        x = self.conv2(x)
        x = self.relu(x)
        x = self.pool(x)

        x = self.conv3(x)
        x = self.relu(x)

        x = x.view(x.size(0), -1)

        x = self.fc1(x)
        x = self.relu(x)

        x = self.fc2(x)
        return x

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    start_time = time.time()

    for batch_idx, (data, target) in enumerate(dataloader):
        # Intentional bottleneck: synchronous H2D transfer
        data = data.to(device)
        target = target.to(device)

        # Another bottleneck: unnecessary synchronization
        torch.cuda.synchronize()

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        # More unnecessary synchronization
        torch.cuda.synchronize()

        total_loss += loss.item()

        if batch_idx % 10 == 0:
            print(f'Batch {batch_idx}, Loss: {loss.item():.4f}')

    epoch_time = time.time() - start_time
    return total_loss / len(dataloader), epoch_time

def main():
    # Intentional issues:
    # 1. Small batch size
    # 2. No pin_memory
    # 3. num_workers=0
    batch_size = 32  # Too small for GPU

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Download CIFAR-10 if not present
    train_dataset = datasets.CIFAR10(root='./data', train=True,
                                     download=True, transform=transform)

    # Problematic DataLoader configuration
    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                             shuffle=True, num_workers=0,
                             pin_memory=False)  # Issues here!

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SimpleNet().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    print(f"Starting training on {device}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {len(train_loader)}")

    # Train for 3 epochs
    for epoch in range(3):
        loss, epoch_time = train_epoch(model, train_loader, criterion,
                                       optimizer, device)
        throughput = len(train_dataset) / epoch_time
        print(f"\nEpoch {epoch+1}: Loss={loss:.4f}, "
              f"Time={epoch_time:.2f}s, "
              f"Throughput={throughput:.2f} samples/sec\n")

if __name__ == '__main__':
    main()
```

### Task 1.1: Run Baseline Profile

```bash
# Profile with Nsight Systems
nsys profile --trace=cuda,nvtx,cudnn,cublas --output=baseline \
    python training_unoptimized.py

# Analyze the profile
nsys-ui baseline.qdrep
```

### Task 1.2: Answer Analysis Questions

**TODO: Based on the Nsight Systems timeline, answer:**

1. **GPU Utilization Pattern:**
   - What is the average GPU SM utilization?
   - Are there visible gaps in GPU activity?
   - What causes these gaps?

2. **Data Transfer:**
   - How much time is spent on H2D (Host-to-Device) transfers?
   - Are transfers overlapped with computation?
   - What percentage of time is idle waiting for data?

3. **Kernel Launch Overhead:**
   - Are there many small kernel launches?
   - What is the average kernel duration?
   - Is there visible launch overhead?

4. **CPU Bottlenecks:**
   - Is the CPU maxed out?
   - Are there delays in data loading?

**Document your findings in a report:**
```
# baseline_analysis.txt

GPU Utilization: ____%
Main Bottlenecks:
1. _______
2. _______
3. _______

Estimated improvement potential: ____%
```

## Part 2: Data Loading Optimization

### Exercise 2.1: Optimize DataLoader

**Task**: Fix the DataLoader configuration

```python
# training_dataloader_optimized.py

# TODO: Modify the DataLoader configuration
train_loader = DataLoader(
    train_dataset,
    batch_size=________,  # TODO: Increase batch size
    shuffle=True,
    num_workers=________,  # TODO: Add parallel workers
    pin_memory=________,   # TODO: Enable pinned memory
    persistent_workers=True  # TODO: Keep workers alive
)

# TODO: Profile again and compare
```

**Expected improvements:**
- Reduced CPU bottleneck
- Better GPU utilization
- Higher throughput

### Task 2.1: Benchmark Different Configurations

```python
# benchmark_dataloader.py
import time
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

def benchmark_dataloader(batch_size, num_workers, pin_memory):
    """Benchmark dataloader with given configuration"""

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    dataset = datasets.CIFAR10(root='./data', train=True,
                               download=True, transform=transform)

    dataloader = DataLoader(dataset, batch_size=batch_size,
                           shuffle=True, num_workers=num_workers,
                           pin_memory=pin_memory)

    # Warm up
    for i, (data, target) in enumerate(dataloader):
        data = data.cuda()
        if i >= 10:
            break

    # Benchmark
    torch.cuda.synchronize()
    start = time.time()
    for i, (data, target) in enumerate(dataloader):
        data = data.cuda()
        if i >= 100:
            break
    torch.cuda.synchronize()
    elapsed = time.time() - start

    throughput = (100 * batch_size) / elapsed
    print(f"BS={batch_size:3d}, Workers={num_workers:2d}, "
          f"Pinned={pin_memory}, "
          f"Throughput={throughput:>8.2f} samples/sec")

# TODO: Test different configurations
print("Benchmarking DataLoader configurations:\n")
for batch_size in [32, 64, 128, 256]:
    for num_workers in [0, 2, 4, 8]:
        for pin_memory in [False, True]:
            benchmark_dataloader(batch_size, num_workers, pin_memory)
        print()

# TODO: Identify optimal configuration
print("\nOptimal configuration: BS=___, Workers=___, Pinned=___")
```

## Part 3: Kernel-Level Optimization

### Exercise 3.1: Analyze Kernel Performance

**Task**: Use Nsight Compute to profile specific kernels

```bash
# Profile convolution kernels
ncu --set full --kernel-name ".*conv.*" \
    --launch-count 10 \
    --output=conv_kernels \
    python training_optimized.py

# Analyze in GUI
ncu-ui conv_kernels.ncu-rep
```

### Task 3.1: Optimize Model Architecture

The current model has inefficient operations. Optimize it:

```python
# training_model_optimized.py

class OptimizedNet(nn.Module):
    def __init__(self):
        super(OptimizedNet, self).__init__()

        # TODO: Use nn.Sequential to fuse operations
        self.features = nn.Sequential(
            # TODO: Combine conv+relu+pool into sequential blocks
            # IMPLEMENT THIS
        )

        self.classifier = nn.Sequential(
            # TODO: Combine fc+relu
            # IMPLEMENT THIS
        )

    def forward(self, x):
        # TODO: Simplified forward pass
        # IMPLEMENT THIS
        return x

# TODO: Compare with original model
# Measure:
# - Number of kernel launches
# - Total execution time
# - GPU utilization
```

## Part 4: Memory Optimization

### Exercise 4.1: Reduce Memory Footprint

**Task**: Enable gradient checkpointing and mixed precision

```python
# training_memory_optimized.py
from torch.cuda.amp import autocast, GradScaler
import torch.utils.checkpoint as checkpoint

class MemoryEfficientNet(nn.Module):
    def __init__(self):
        super(MemoryEfficientNet, self).__init__()
        # Same architecture as before
        self.conv_block1 = self._make_conv_block(3, 64)
        self.conv_block2 = self._make_conv_block(64, 128)
        self.conv_block3 = self._make_conv_block(128, 256)
        self.classifier = nn.Sequential(
            nn.Linear(256 * 28 * 28, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, 10)
        )

    def _make_conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )

    def forward(self, x):
        # TODO: Use gradient checkpointing for conv blocks
        x = checkpoint.checkpoint(self.conv_block1, x)
        x = checkpoint.checkpoint(self.conv_block2, x)
        x = checkpoint.checkpoint(self.conv_block3, x)

        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

def train_with_amp(model, dataloader, criterion, optimizer, device):
    """Training with Automatic Mixed Precision"""

    # TODO: Create GradScaler for mixed precision
    scaler = GradScaler()

    model.train()
    for data, target in dataloader:
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()

        # TODO: Use autocast for mixed precision forward pass
        with autocast():
            output = model(data)
            loss = criterion(output, target)

        # TODO: Scaled backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

# TODO: Measure memory usage before and after
# Use torch.cuda.memory_allocated() and torch.cuda.max_memory_allocated()
```

### Task 4.1: Benchmark Memory and Speed

```python
# benchmark_memory.py

def measure_memory_and_speed(model, batch_size, use_amp=False):
    """Measure peak memory and throughput"""

    device = torch.device('cuda')
    model = model.to(device)

    # Generate dummy data
    data = torch.randn(batch_size, 3, 224, 224).to(device)

    # Warm up
    for _ in range(10):
        if use_amp:
            with autocast():
                _ = model(data)
        else:
            _ = model(data)

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()

    start = time.time()
    for _ in range(100):
        if use_amp:
            with autocast():
                _ = model(data)
        else:
            _ = model(data)
    torch.cuda.synchronize()
    elapsed = time.time() - start

    peak_memory = torch.cuda.max_memory_allocated() / 1e9  # GB
    throughput = (100 * batch_size) / elapsed

    print(f"BS={batch_size}, AMP={use_amp}: "
          f"Memory={peak_memory:.2f}GB, "
          f"Throughput={throughput:.2f} samples/sec")

# TODO: Compare FP32 vs AMP, different batch sizes
model = SimpleNet()

for batch_size in [32, 64, 128, 256]:
    print(f"\nBatch size: {batch_size}")
    measure_memory_and_speed(model, batch_size, use_amp=False)
    measure_memory_and_speed(model, batch_size, use_amp=True)
```

## Part 5: Multi-GPU Scaling

### Exercise 5.1: Data Parallel Training

**Task**: Convert to DistributedDataParallel

```python
# training_ddp.py
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup_ddp():
    """Initialize distributed training"""
    dist.init_process_group(backend='nccl')
    local_rank = int(os.environ['LOCAL_RANK'])
    torch.cuda.set_device(local_rank)
    return local_rank

def train_ddp(local_rank):
    """DDP training function"""

    # TODO: Create model and wrap with DDP
    model = SimpleNet().to(local_rank)
    ddp_model = DDP(model, device_ids=[local_rank])

    # TODO: Create DistributedSampler
    train_sampler = DistributedSampler(
        train_dataset,
        num_replicas=dist.get_world_size(),
        rank=local_rank
    )

    # TODO: Create DataLoader with sampler
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True
    )

    # TODO: Training loop
    for epoch in range(num_epochs):
        train_sampler.set_epoch(epoch)  # Shuffle differently each epoch
        train_epoch(ddp_model, train_loader, criterion, optimizer, local_rank)

def main():
    local_rank = setup_ddp()
    train_ddp(local_rank)
    dist.destroy_process_group()

if __name__ == '__main__':
    main()
```

**Run with:**
```bash
# Single node, 4 GPUs
torchrun --nproc_per_node=4 training_ddp.py

# TODO: Measure scaling efficiency
# Compare 1, 2, 4, 8 GPUs
```

### Task 5.1: Scaling Analysis

```python
# analyze_scaling.py

def measure_scaling_efficiency():
    """Measure strong scaling efficiency"""

    results = {}
    baseline_time = None

    for num_gpus in [1, 2, 4, 8]:
        # TODO: Run training with num_gpus
        # Measure time per epoch
        time_per_epoch = 0  # IMPLEMENT

        if num_gpus == 1:
            baseline_time = time_per_epoch

        speedup = baseline_time / time_per_epoch
        efficiency = speedup / num_gpus

        results[num_gpus] = {
            'time': time_per_epoch,
            'speedup': speedup,
            'efficiency': efficiency
        }

        print(f"{num_gpus} GPUs: {time_per_epoch:.2f}s, "
              f"Speedup: {speedup:.2f}x, "
              f"Efficiency: {efficiency:.2%}")

    return results

# TODO: Plot scaling curve
```

## Part 6: Final Optimization Challenge

### Exercise 6.1: Achieve >80% GPU Utilization

**Task**: Apply all optimizations to achieve the target

**Checklist:**
- [ ] Optimal batch size (as large as fits in memory)
- [ ] DataLoader: num_workers=4-8, pin_memory=True
- [ ] Mixed precision training (AMP)
- [ ] Fused operations (nn.Sequential)
- [ ] Remove unnecessary synchronizations
- [ ] Asynchronous H2D transfers
- [ ] Gradient accumulation (if batch size limited)

**Final optimized script:**
```python
# training_final_optimized.py

# TODO: Implement all optimizations
# Target: >80% GPU utilization, >3x throughput vs baseline

def main():
    # Configuration
    batch_size = 256  # Optimized
    num_workers = 8
    use_amp = True
    num_epochs = 3

    # Optimized DataLoader
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True,
        prefetch_factor=2  # Prefetch 2 batches
    )

    # Optimized model
    model = OptimizedNet().to(device)

    # Mixed precision training
    scaler = GradScaler()

    # Training loop with all optimizations
    for epoch in range(num_epochs):
        # TODO: IMPLEMENT OPTIMIZED TRAINING LOOP
        pass

if __name__ == '__main__':
    main()
```

### Task 6.1: Final Profiling and Report

```bash
# Profile optimized version
nsys profile --trace=cuda,nvtx --output=final_optimized \
    python training_final_optimized.py

# Compare with baseline
nsys stats baseline.qdrep > baseline_stats.txt
nsys stats final_optimized.qdrep > optimized_stats.txt
```

## Deliverables

Submit:

1. **Baseline Analysis Report** (baseline_analysis.txt):
   - GPU utilization
   - Identified bottlenecks
   - Profiling screenshots

2. **Optimized Scripts**:
   - training_dataloader_optimized.py
   - training_model_optimized.py
   - training_memory_optimized.py
   - training_final_optimized.py

3. **Performance Comparison Table**:
   ```
   | Version | GPU Util | Throughput | Speedup |
   |---------|----------|------------|---------|
   | Baseline| ___%     | ___ s/s    | 1.0x    |
   | DataLoader| ___%   | ___ s/s    | ___x    |
   | Model   | ___%     | ___ s/s    | ___x    |
   | Memory  | ___%     | ___ s/s    | ___x    |
   | Final   | ___%     | ___ s/s    | ___x    |
   ```

4. **Profiling Reports**:
   - Nsight Systems timeline screenshots (before/after)
   - Nsight Compute kernel analysis
   - GPU utilization graphs

5. **Reflection Document** (1-2 pages):
   - What was the biggest bottleneck?
   - Which optimization had the most impact?
   - What would you optimize next?
   - Lessons learned

## Evaluation Criteria

- **Baseline Analysis** (20%): Thorough identification of bottlenecks
- **Incremental Optimizations** (30%): Each step shows improvement
- **Final Performance** (25%): Achieving >80% GPU utilization
- **Documentation** (15%): Clear reports and profiling screenshots
- **Understanding** (10%): Insightful reflection document

## Bonus Challenges

1. **Kernel Fusion**: Write custom fused CUDA kernels for conv+relu+pool
2. **Profiling Automation**: Script to automate profiling and generate reports
3. **Multi-Node DDP**: Scale to 2+ nodes and measure efficiency
4. **Inference Optimization**: Optimize inference pipeline (separate workload)

---

**Success Target**: Achieve 3x+ speedup from baseline with >80% GPU utilization!
