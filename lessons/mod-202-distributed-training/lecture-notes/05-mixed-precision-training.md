# Lecture 05: Mixed Precision Training

## Learning Objectives

By the end of this lecture, you will be able to:

- Design mixed precision training strategies using FP16, BF16, and FP32 to optimize memory usage, training speed, and numerical stability
- Implement PyTorch Automatic Mixed Precision (AMP) with gradient scaling for production training pipelines
- Configure and tune dynamic loss scaling strategies to prevent gradient underflow and numerical instability in FP16 training
- Evaluate trade-offs between FP16 and BF16 precision formats based on hardware capabilities, model architecture, and numerical requirements
- Implement gradient scaling, loss scaling, and master weight management for stable mixed precision training
- Identify and handle operations requiring FP32 precision (LayerNorm, Softmax, loss computation) to maintain training stability
- Benchmark and measure memory savings (25%) and speedup (2-3x) from mixed precision training on different GPU architectures
- Troubleshoot common mixed precision issues including NaN/Inf gradients, scale factor degradation, and convergence problems

## Table of Contents

1. [Introduction to Mixed Precision](#introduction)
2. [Float16 vs BFloat16](#fp16-vs-bf16)
3. [Automatic Mixed Precision (AMP)](#amp)
4. [Gradient Scaling](#gradient-scaling)
5. [Loss Scaling Strategies](#loss-scaling)
6. [Memory and Speed Benefits](#benefits)
7. [Numerical Stability](#numerical-stability)
8. [Framework Implementation](#framework-implementation)
9. [Best Practices](#best-practices)

## Introduction to Mixed Precision

Mixed precision training uses lower-precision (FP16/BF16) for most operations while maintaining FP32 for numerical stability where needed.

### Why Mixed Precision?

```python
# Memory comparison
PRECISION_MEMORY = {
    'FP32': {
        'bytes_per_param': 4,
        'range': '±3.4e38',
        'precision': '~7 decimal digits',
    },
    'FP16': {
        'bytes_per_param': 2,
        'range': '±65504',
        'precision': '~3 decimal digits',
    },
    'BF16': {
        'bytes_per_param': 2,
        'range': '±3.4e38 (same as FP32)',
        'precision': '~2 decimal digits',
    },
}

# For 175B parameter model
def calculate_memory_savings(num_params, precision):
    """Calculate memory usage for different precisions"""
    bytes_per = PRECISION_MEMORY[precision]['bytes_per_param']

    # Model parameters
    params_memory = num_params * bytes_per / 1e9  # GB

    # Gradients (same precision)
    grads_memory = params_memory

    # Optimizer states (always FP32)
    # Adam: 2 states (momentum + variance)
    optimizer_memory = num_params * 4 * 2 / 1e9  # GB

    total = params_memory + grads_memory + optimizer_memory

    return {
        'params_gb': params_memory,
        'grads_gb': grads_memory,
        'optimizer_gb': optimizer_memory,
        'total_gb': total,
    }

# Compare memory usage
print("Memory Usage for 175B Parameter Model:\n")
print(f"{'Precision':<10} {'Params':<10} {'Grads':<10} {'Optimizer':<12} {'Total':<10}")
print("-" * 60)

for precision in ['FP32', 'FP16', 'BF16']:
    mem = calculate_memory_savings(175e9, precision)
    print(f"{precision:<10} {mem['params_gb']:>8.1f} GB {mem['grads_gb']:>8.1f} GB "
          f"{mem['optimizer_gb']:>10.1f} GB {mem['total_gb']:>8.1f} GB")

# Output:
# FP32       700.0 GB   700.0 GB   1400.0 GB   2800.0 GB
# FP16       350.0 GB   350.0 GB   1400.0 GB   2100.0 GB (25% savings)
# BF16       350.0 GB   350.0 GB   1400.0 GB   2100.0 GB (25% savings)
```

### Speed Benefits

```python
# Tensor Core performance (NVIDIA A100)
TENSOR_CORE_PERFORMANCE = {
    'FP32': 19.5,    # TFLOPS
    'TF32': 156,     # TFLOPS (Tensor Float 32)
    'FP16': 312,     # TFLOPS (16x faster than FP32!)
    'BF16': 312,     # TFLOPS
    'INT8': 624,     # TOPS
}

def calculate_speedup():
    """Calculate potential speedup with mixed precision"""
    fp32_speed = TENSOR_CORE_PERFORMANCE['FP32']
    fp16_speed = TENSOR_CORE_PERFORMANCE['FP16']

    theoretical_speedup = fp16_speed / fp32_speed
    # Real-world speedup: ~2-3x (not 16x due to other bottlenecks)
    realistic_speedup = 2.5

    print(f"Theoretical speedup: {theoretical_speedup:.1f}x")
    print(f"Realistic speedup: {realistic_speedup:.1f}x")
    print("\nFactors limiting speedup:")
    print("  - Memory bandwidth")
    print("  - FP32 operations (layer norm, softmax)")
    print("  - Communication overhead")

calculate_speedup()
```

## Float16 vs BFloat16

### Precision Format Comparison

```
┌───────────────────────────────────────────────────────────────┐
│              FP32 vs FP16 vs BF16 Format                      │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  FP32 (32 bits):                                              │
│  ┌─┬────────┬───────────────────────────┐                    │
│  │S│Exponent│      Mantissa             │                    │
│  │1│   8    │          23               │                    │
│  └─┴────────┴───────────────────────────┘                    │
│   Sign  Range: ±3.4e38  Precision: ~7 digits                 │
│                                                                │
│  FP16 (16 bits):                                              │
│  ┌─┬─────┬──────────┐                                         │
│  │S│ Exp │ Mantissa │                                         │
│  │1│  5  │    10    │                                         │
│  └─┴─────┴──────────┘                                         │
│   Sign  Range: ±65504  Precision: ~3 digits                  │
│   Problem: Limited range → overflow/underflow!               │
│                                                                │
│  BF16 (Brain Float16, 16 bits):                              │
│  ┌─┬────────┬──────┐                                          │
│  │S│Exponent│Mant. │                                          │
│  │1│   8    │  7   │                                          │
│  └─┴────────┴──────┘                                          │
│   Sign  Range: ±3.4e38 (same as FP32!)  Precision: ~2 digits│
│   Advantage: Same range as FP32 → less overflow/underflow   │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### FP16 vs BF16 in Practice

```python
import torch

def compare_fp16_bf16():
    """
    Demonstrate differences between FP16 and BF16
    """
    print("FP16 vs BF16 Comparison\n")
    print("=" * 70)

    # Test 1: Range
    print("\n1. Representable Range:")
    large_value = 70000.0

    fp32_tensor = torch.tensor([large_value], dtype=torch.float32)
    fp16_tensor = fp32_tensor.to(torch.float16)
    bf16_tensor = fp32_tensor.to(torch.bfloat16)

    print(f"  FP32: {fp32_tensor.item()}")
    print(f"  FP16: {fp16_tensor.item()}")  # Overflow to inf!
    print(f"  BF16: {bf16_tensor.item()}")  # OK

    # Test 2: Small gradients
    print("\n2. Small Gradient Handling:")
    small_grad = 1e-8

    fp32_grad = torch.tensor([small_grad], dtype=torch.float32)
    fp16_grad = fp32_grad.to(torch.float16)
    bf16_grad = fp32_grad.to(torch.bfloat16)

    print(f"  FP32: {fp32_grad.item():.2e}")
    print(f"  FP16: {fp16_grad.item():.2e}")  # Underflow to 0!
    print(f"  BF16: {bf16_grad.item():.2e}")  # Underflow to 0 (less precision)

    # Test 3: Precision
    print("\n3. Precision Comparison:")
    value = 1.234567890

    fp32_val = torch.tensor([value], dtype=torch.float32)
    fp16_val = fp32_val.to(torch.float16)
    bf16_val = fp32_val.to(torch.bfloat16)

    print(f"  FP32: {fp32_val.item():.10f}")
    print(f"  FP16: {fp16_val.item():.10f}")
    print(f"  BF16: {bf16_val.item():.10f}")

    print("\n" + "=" * 70)

# When to use each
PRECISION_GUIDANCE = {
    'FP16': {
        'use_when': [
            'Training models < 1B parameters',
            'Inference workloads',
            'GPUs without BF16 support (V100)',
        ],
        'challenges': [
            'Requires careful gradient scaling',
            'Risk of overflow/underflow',
            'Some operations need to stay FP32',
        ],
    },
    'BF16': {
        'use_when': [
            'Training large models (> 1B parameters)',
            'GPUs with BF16 support (A100, H100)',
            'Simpler training without gradient scaling',
        ],
        'advantages': [
            'Same range as FP32',
            'Less numerical instability',
            'No gradient scaling needed (usually)',
        ],
    },
}

compare_fp16_bf16()
```

## Automatic Mixed Precision (AMP)

PyTorch AMP automatically handles mixed precision training.

### Basic AMP Usage

```python
import torch
from torch.cuda.amp import autocast, GradScaler

def train_with_amp(model, dataloader, optimizer, device):
    """
    Basic mixed precision training with AMP
    """
    # Create GradScaler for FP16
    scaler = GradScaler()

    model.train()
    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()

        # Forward pass with autocast
        with autocast():
            output = model(data)
            loss = torch.nn.functional.cross_entropy(output, target)

        # Backward pass with gradient scaling
        scaler.scale(loss).backward()

        # Gradient clipping (must unscale first!)
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        # Optimizer step with scaler
        scaler.step(optimizer)
        scaler.update()

    return loss.item()

# BF16 training (simpler - no gradient scaling!)
def train_with_bf16(model, dataloader, optimizer, device):
    """
    BF16 training - no gradient scaler needed
    """
    model.train()
    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()

        # Forward pass with BF16 autocast
        with autocast(dtype=torch.bfloat16):
            output = model(data)
            loss = torch.nn.functional.cross_entropy(output, target)

        # Regular backward pass
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        # Regular optimizer step
        optimizer.step()

    return loss.item()
```

### Advanced AMP Implementation

```python
class AMPTrainer:
    """
    Production-ready AMP trainer with all optimizations
    """

    def __init__(self, model, config, device):
        self.model = model.to(device)
        self.config = config
        self.device = device

        # Choose precision
        self.use_amp = config.get('amp', True)
        self.amp_dtype = torch.float16 if config.get('fp16', True) else torch.bfloat16

        # Create GradScaler (only for FP16)
        self.scaler = GradScaler(enabled=(self.amp_dtype == torch.float16))

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config['lr'],
            weight_decay=config.get('weight_decay', 0.01),
        )

        # Track gradient scaling statistics
        self.scale_history = []

    def train_step(self, data, target):
        """Single training step with AMP"""
        self.optimizer.zero_grad()

        # Forward pass with mixed precision
        with autocast(enabled=self.use_amp, dtype=self.amp_dtype):
            output = self.model(data)
            loss = torch.nn.functional.cross_entropy(output, target)

        # Backward pass with gradient scaling
        if self.scaler.is_enabled():
            self.scaler.scale(loss).backward()

            # Unscale before gradient clipping
            self.scaler.unscale_(self.optimizer)

            # Gradient clipping
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0
            )

            # Optimizer step with scaler
            self.scaler.step(self.optimizer)

            # Update scaler
            old_scale = self.scaler.get_scale()
            self.scaler.update()
            new_scale = self.scaler.get_scale()

            # Track if scale changed
            if old_scale != new_scale:
                self.scale_history.append({
                    'old_scale': old_scale,
                    'new_scale': new_scale,
                    'grad_norm': grad_norm.item(),
                })

        else:
            # BF16 or FP32: regular training
            loss.backward()

            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0
            )

            self.optimizer.step()

        return {
            'loss': loss.item(),
            'grad_norm': grad_norm.item() if isinstance(grad_norm, torch.Tensor) else grad_norm,
            'scale': self.scaler.get_scale() if self.scaler.is_enabled() else 1.0,
        }

    def train_epoch(self, dataloader):
        """Train one epoch"""
        self.model.train()

        total_loss = 0
        total_grad_norm = 0
        num_batches = 0

        for batch_idx, (data, target) in enumerate(dataloader):
            data = data.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)

            metrics = self.train_step(data, target)

            total_loss += metrics['loss']
            total_grad_norm += metrics['grad_norm']
            num_batches += 1

            if batch_idx % 100 == 0:
                avg_loss = total_loss / num_batches
                avg_grad_norm = total_grad_norm / num_batches

                print(f"Batch {batch_idx:>5} "
                      f"Loss: {avg_loss:.4f} "
                      f"GradNorm: {avg_grad_norm:.4f} "
                      f"Scale: {metrics['scale']:.0f}")

        return total_loss / num_batches

    def get_scaling_statistics(self):
        """Analyze gradient scaling behavior"""
        if not self.scale_history:
            return None

        import numpy as np

        old_scales = [h['old_scale'] for h in self.scale_history]
        new_scales = [h['new_scale'] for h in self.scale_history]
        grad_norms = [h['grad_norm'] for h in self.scale_history]

        return {
            'num_scale_changes': len(self.scale_history),
            'scale_increases': sum(1 for i in range(len(self.scale_history))
                                  if new_scales[i] > old_scales[i]),
            'scale_decreases': sum(1 for i in range(len(self.scale_history))
                                  if new_scales[i] < old_scales[i]),
            'avg_grad_norm_at_change': np.mean(grad_norms),
            'final_scale': self.scaler.get_scale(),
        }

# Usage example
config = {
    'lr': 1e-4,
    'amp': True,
    'fp16': True,  # Use FP16 (False for BF16)
    'weight_decay': 0.01,
}

trainer = AMPTrainer(model, config, device)

for epoch in range(num_epochs):
    loss = trainer.train_epoch(train_loader)
    print(f"Epoch {epoch}: Loss = {loss:.4f}")

    # Print scaling statistics
    stats = trainer.get_scaling_statistics()
    if stats:
        print(f"  Scale changes: {stats['num_scale_changes']}")
        print(f"  Final scale: {stats['final_scale']}")
```

## Gradient Scaling

Gradient scaling prevents underflow in FP16 training.

### Why Gradient Scaling?

```python
def demonstrate_gradient_underflow():
    """
    Show why gradient scaling is necessary for FP16
    """
    print("Gradient Underflow Demonstration\n")
    print("=" * 70)

    # Simulate small gradient (common in deep networks)
    gradient_fp32 = torch.tensor([1e-7], dtype=torch.float32)

    print(f"Original gradient (FP32): {gradient_fp32.item():.2e}")

    # Convert to FP16 without scaling
    gradient_fp16 = gradient_fp32.to(torch.float16)
    print(f"Gradient in FP16 (no scaling): {gradient_fp16.item():.2e}")
    # Result: 0.0 (underflow!)

    # With gradient scaling
    scale = 1024.0  # Loss scale factor
    scaled_gradient_fp32 = gradient_fp32 * scale
    scaled_gradient_fp16 = scaled_gradient_fp32.to(torch.float16)
    recovered_gradient = (scaled_gradient_fp16.to(torch.float32) / scale)

    print(f"Scaled gradient (×{scale:.0f}): {scaled_gradient_fp16.item():.2e}")
    print(f"Recovered gradient: {recovered_gradient.item():.2e}")
    # Result: ~1e-7 (preserved!)

    print("\n" + "=" * 70)

demonstrate_gradient_underflow()

# Gradient scaling implementation
class SimpleGradScaler:
    """
    Simplified GradScaler for educational purposes
    """

    def __init__(self, init_scale=2**16, growth_factor=2.0, backoff_factor=0.5):
        """
        Args:
            init_scale: Initial loss scale
            growth_factor: Factor to increase scale
            backoff_factor: Factor to decrease scale
        """
        self._scale = init_scale
        self.growth_factor = growth_factor
        self.backoff_factor = backoff_factor
        self._growth_tracker = 0

    def scale(self, loss):
        """Scale loss before backward pass"""
        return loss * self._scale

    def unscale_(self, optimizer):
        """Unscale gradients"""
        inv_scale = 1.0 / self._scale
        for param_group in optimizer.param_groups:
            for param in param_group['params']:
                if param.grad is not None:
                    param.grad.mul_(inv_scale)

    def step(self, optimizer):
        """
        Perform optimizer step, checking for inf/nan
        """
        # Check for inf/nan in gradients
        found_inf = False
        for param_group in optimizer.param_groups:
            for param in param_group['params']:
                if param.grad is not None:
                    if torch.isinf(param.grad).any() or torch.isnan(param.grad).any():
                        found_inf = True
                        break
            if found_inf:
                break

        if found_inf:
            # Skip this step, decrease scale
            print(f"⚠ Inf/NaN gradients detected! "
                  f"Decreasing scale: {self._scale:.0f} → "
                  f"{self._scale * self.backoff_factor:.0f}")
            self._scale *= self.backoff_factor
            self._growth_tracker = 0
        else:
            # Perform optimizer step
            optimizer.step()
            self._growth_tracker += 1

    def update(self):
        """
        Update scale based on gradient health
        Increase scale every N successful steps
        """
        if self._growth_tracker >= 2000:  # Growth interval
            self._scale *= self.growth_factor
            self._growth_tracker = 0
            print(f"✓ Increasing scale to {self._scale:.0f}")

    def get_scale(self):
        """Get current scale"""
        return self._scale
```

## Loss Scaling Strategies

### Dynamic Loss Scaling

```python
class DynamicLossScaler:
    """
    Dynamic loss scaling that adapts to training
    """

    def __init__(self, init_scale=2**16, scale_window=2000):
        self.scale = init_scale
        self.scale_window = scale_window
        self.consecutive_successes = 0
        self.scale_history = []

    def get_scale(self):
        return self.scale

    def check_overflow(self, grads):
        """Check if any gradient has inf/nan"""
        for grad in grads:
            if grad is not None:
                if torch.isinf(grad).any() or torch.isnan(grad).any():
                    return True
        return False

    def update_scale(self, overflow):
        """Update scale based on overflow"""
        self.scale_history.append({
            'scale': self.scale,
            'overflow': overflow,
        })

        if overflow:
            # Overflow detected: reduce scale
            self.scale = max(self.scale * 0.5, 1.0)
            self.consecutive_successes = 0
            print(f"Overflow! Reducing scale to {self.scale:.0f}")
        else:
            # Success: increment counter
            self.consecutive_successes += 1

            # Increase scale after consecutive successes
            if self.consecutive_successes >= self.scale_window:
                self.scale *= 2.0
                self.consecutive_successes = 0
                print(f"Increasing scale to {self.scale:.0f}")

    def plot_scale_history(self):
        """Plot scale evolution over training"""
        import matplotlib.pyplot as plt

        steps = range(len(self.scale_history))
        scales = [h['scale'] for h in self.scale_history]
        overflows = [h['overflow'] for h in self.scale_history]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Plot scale
        ax1.plot(steps, scales)
        ax1.set_ylabel('Loss Scale')
        ax1.set_yscale('log')
        ax1.set_title('Loss Scale Over Training')
        ax1.grid(True)

        # Plot overflows
        overflow_steps = [i for i, o in enumerate(overflows) if o]
        if overflow_steps:
            ax2.scatter(overflow_steps, [1]*len(overflow_steps), c='red', marker='x')
        ax2.set_ylabel('Overflow')
        ax2.set_xlabel('Training Step')
        ax2.set_title('Gradient Overflow Events')
        ax2.set_ylim([0, 2])
        ax2.grid(True)

        plt.tight_layout()
        return fig
```

### Fixed Loss Scaling

```python
# For BF16 or stable FP16 training
class FixedLossScaler:
    """
    Fixed loss scaling - simpler but less adaptive
    """

    def __init__(self, scale=1.0):
        """
        Args:
            scale: Fixed loss scale (typically 1.0 for BF16)
        """
        self.scale = scale

    def get_scale(self):
        return self.scale

    def scale_loss(self, loss):
        """Scale loss"""
        return loss * self.scale

    def unscale_grads(self, optimizer):
        """Unscale gradients"""
        if self.scale != 1.0:
            inv_scale = 1.0 / self.scale
            for param_group in optimizer.param_groups:
                for param in param_group['params']:
                    if param.grad is not None:
                        param.grad.mul_(inv_scale)
```

## Memory and Speed Benefits

### Benchmarking Mixed Precision

```python
import time
import torch.nn as nn

def benchmark_mixed_precision(model, input_shape, batch_size, num_iterations=100):
    """
    Benchmark FP32 vs FP16 vs BF16 performance
    """
    device = torch.device('cuda')
    results = {}

    precisions = {
        'FP32': torch.float32,
        'FP16': torch.float16,
        'BF16': torch.bfloat16,
    }

    for precision_name, dtype in precisions.items():
        # Skip BF16 if not supported
        if dtype == torch.bfloat16 and not torch.cuda.is_bf16_supported():
            continue

        # Create model and input
        test_model = model().to(device).to(dtype)
        test_input = torch.randn(batch_size, *input_shape, device=device, dtype=dtype)

        # Warmup
        for _ in range(10):
            output = test_model(test_input)
            loss = output.sum()
            loss.backward()

        # Benchmark forward pass
        torch.cuda.synchronize()
        start = time.time()

        for _ in range(num_iterations):
            output = test_model(test_input)

        torch.cuda.synchronize()
        forward_time = (time.time() - start) / num_iterations

        # Benchmark forward + backward
        torch.cuda.synchronize()
        start = time.time()

        for _ in range(num_iterations):
            test_model.zero_grad()
            output = test_model(test_input)
            loss = output.sum()
            loss.backward()

        torch.cuda.synchronize()
        total_time = (time.time() - start) / num_iterations

        # Measure memory
        torch.cuda.reset_peak_memory_stats()
        test_model.zero_grad()
        output = test_model(test_input)
        loss = output.sum()
        loss.backward()
        peak_memory = torch.cuda.max_memory_allocated() / 1e9  # GB

        results[precision_name] = {
            'forward_ms': forward_time * 1000,
            'total_ms': total_time * 1000,
            'memory_gb': peak_memory,
        }

        # Cleanup
        del test_model, test_input
        torch.cuda.empty_cache()

    # Print results
    print("\nMixed Precision Benchmark Results:")
    print("=" * 80)
    print(f"{'Precision':<12} {'Forward (ms)':<15} {'Forward+Backward (ms)':<25} {'Memory (GB)':<15}")
    print("-" * 80)

    fp32_forward = results['FP32']['forward_ms']
    fp32_total = results['FP32']['total_ms']
    fp32_memory = results['FP32']['memory_gb']

    for precision_name, metrics in results.items():
        forward_speedup = fp32_forward / metrics['forward_ms']
        total_speedup = fp32_total / metrics['total_ms']
        memory_reduction = (1 - metrics['memory_gb'] / fp32_memory) * 100

        print(f"{precision_name:<12} "
              f"{metrics['forward_ms']:>8.2f} ({forward_speedup:.2f}x)  "
              f"{metrics['total_ms']:>12.2f} ({total_speedup:.2f}x)      "
              f"{metrics['memory_gb']:>8.2f} (-{memory_reduction:.0f}%)")

    return results

# Example: Benchmark ResNet-50
class SimpleResNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        # ... more layers ...
        self.fc = nn.Linear(2048, 1000)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        # ... more layers ...
        return self.fc(x.mean([2, 3]))

# Run benchmark
# benchmark_mixed_precision(SimpleResNet, input_shape=(3, 224, 224), batch_size=32)
```

## Numerical Stability

### Operations That Need FP32

```python
# Some operations should stay in FP32 for stability
FP32_OPS = [
    'LayerNorm',
    'BatchNorm',
    'Softmax (sometimes)',
    'Loss computation',
    'Optimizer master weights',
]

class StableLayerNorm(nn.Module):
    """
    LayerNorm that always uses FP32 for stability
    """

    def __init__(self, normalized_shape, eps=1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))

    def forward(self, x):
        # Convert to FP32 for normalization
        input_dtype = x.dtype
        x = x.float()

        # LayerNorm computation
        mean = x.mean(-1, keepdim=True)
        var = x.var(-1, keepdim=True, unbiased=False)
        x = (x - mean) / torch.sqrt(var + self.eps)

        # Apply affine transform and convert back
        x = x * self.weight + self.bias
        return x.to(input_dtype)

# Automatic conversion for unstable operations
def should_use_fp32(op_name):
    """Determine if operation should use FP32"""
    unstable_ops = {
        'layer_norm', 'batch_norm', 'instance_norm',
        'softmax', 'log_softmax', 'cross_entropy',
        'exp', 'log', 'sqrt',
    }
    return op_name.lower() in unstable_ops
```

## Best Practices

### Mixed Precision Training Checklist

```python
BEST_PRACTICES = {
    'Gradient Scaling': [
        '✓ Use GradScaler for FP16',
        '✓ Monitor scale factor during training',
        '✓ Check for frequent scale decreases (indicates instability)',
    ],
    'Model Architecture': [
        '✓ Keep LayerNorm/BatchNorm in FP32',
        '✓ Use stable activation functions',
        '✓ Avoid very deep networks without proper initialization',
    ],
    'Training Configuration': [
        '✓ Use gradient clipping (unscale first!)',
        '✓ Start with conservative learning rate',
        '✓ Monitor loss for NaN/Inf',
    ],
    'Precision Selection': [
        '✓ Use BF16 on A100/H100 (simpler, more stable)',
        '✓ Use FP16 on V100 or for inference',
        '✓ Use FP32 for small models or debugging',
    ],
}

def print_best_practices():
    """Print mixed precision best practices"""
    print("\nMixed Precision Training Best Practices:")
    print("=" * 70)
    for category, practices in BEST_PRACTICES.items():
        print(f"\n{category}:")
        for practice in practices:
            print(f"  {practice}")
    print("\n" + "=" * 70)

print_best_practices()
```

## Summary

Key takeaways:

1. **Mixed precision** reduces memory by ~25% and speeds up training by ~2-3x
2. **FP16** requires gradient scaling; **BF16** is more stable but needs newer GPUs
3. **AMP** makes mixed precision easy with automatic type casting
4. **Some operations** (LayerNorm, Softmax) should stay in FP32
5. **Monitor gradient scale** to detect numerical instability

**Recommendations:**
- Use BF16 on A100/H100 for simplicity
- Use FP16 on older GPUs with careful gradient scaling
- Always monitor training for NaN/Inf
- Keep master weights in FP32

## Further Reading

- [PyTorch AMP Documentation](https://pytorch.org/docs/stable/amp.html)
- [NVIDIA Mixed Precision Training Guide](https://docs.nvidia.com/deeplearning/performance/mixed-precision-training/)
- "Mixed Precision Training" (Micikevicius et al., 2017)

## Next Steps

Continue to `06-fault-tolerance.md` to learn about checkpointing and fault-tolerant training systems.
