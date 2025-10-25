# Lab 02: Quantization Implementation

## Objectives

Implement and compare various quantization techniques:
1. Post-Training Quantization (PTQ) with PyTorch
2. INT8 and FP16 quantization
3. Quantization-Aware Training (QAT)
4. Accuracy analysis and preservation strategies
5. Performance benchmarking

**Estimated Time**: 5 hours

## Prerequisites

- Completed Lecture 04: Quantization Techniques
- PyTorch 2.0+ with quantization support
- NVIDIA GPU (optional, for faster training)

## Part 1: Post-Training Static Quantization (90 minutes)

### Task 1.1: Implement PTQ Pipeline

```python
import torch
import torch.quantization as quant
from torchvision import models, datasets, transforms

# TODO: Implement static PTQ
# 1. Load pre-trained ResNet-18
# 2. Fuse Conv-BN-ReLU modules
# 3. Configure quantization (fbgemm backend)
# 4. Prepare model for calibration
# 5. Run calibration with representative data
# 6. Convert to quantized model
# 7. Evaluate accuracy

model = models.resnet18(weights='IMAGENET1K_V1')
model.eval()

# YOUR CODE HERE
```

### Task 1.2: Implement Calibration Loop

```python
def calibrate_model(model, calibration_loader, num_batches=100):
    """
    Calibrate model for static quantization

    TODO:
    - Run model on calibration data
    - No gradients needed
    - Observers collect statistics
    """
    # YOUR CODE HERE
    pass
```

**Expected Accuracy**: <1% drop from FP32 baseline

## Part 2: Dynamic Quantization (30 minutes)

### Task 2.1: Apply Dynamic Quantization

```python
# TODO: Implement dynamic quantization
# Apply to Linear and LSTM layers only
# Compare speed and accuracy with static quantization

model_dynamic = quant.quantize_dynamic(
    model,
    # YOUR CODE HERE
)
```

## Part 3: Quantization-Aware Training (120 minutes)

### Task 3.1: Implement QAT

```python
def train_qat(model, train_loader, val_loader, epochs=5):
    """
    Quantization-aware training

    TODO:
    - Configure QAT
    - Prepare model with fake quantization
    - Train for several epochs
    - Freeze BN stats after 2 epochs
    - Freeze quantization ranges after 3 epochs
    - Convert to quantized model
    """
    # YOUR CODE HERE
    pass
```

### Task 3.2: Compare PTQ vs QAT

```python
# TODO: Evaluate and compare:
# - Accuracy: PTQ vs QAT vs FP32
# - Inference latency
# - Model size
# Create comparison table and charts
```

**Expected Results**: QAT should achieve <0.5% accuracy drop

## Part 4: Per-Channel Quantization (45 minutes)

### Task 4.1: Implement Per-Channel Quantization

```python
# TODO: Configure per-channel weight quantization
# Compare with per-tensor quantization
# Measure accuracy improvement

qconfig = torch.quantization.QConfig(
    # YOUR CODE HERE
)
```

## Part 5: Sensitivity Analysis (60 minutes)

### Task 5.1: Layer-wise Sensitivity

```python
def analyze_layer_sensitivity(model, test_loader):
    """
    Identify quantization-sensitive layers

    TODO:
    - Quantize each layer individually
    - Measure accuracy drop
    - Rank layers by sensitivity
    - Return top-k sensitive layers
    """
    # YOUR CODE HERE
    pass

# TODO: Use results to configure mixed-precision
sensitive_layers = analyze_layer_sensitivity(model, test_loader)
```

### Task 5.2: Mixed Precision Quantization

```python
# TODO: Keep sensitive layers in FP32, quantize others
# Expected: Better accuracy than full INT8
```

## Part 6: Benchmarking (45 minutes)

### Task 6.1: Comprehensive Benchmark

```python
# TODO: Benchmark all quantized models:
# - FP32 baseline
# - Static PTQ INT8
# - Dynamic PTQ
# - QAT INT8
# - Mixed precision

# Metrics:
# - Latency (CPU and GPU)
# - Throughput
# - Model size
# - Accuracy
# - Memory usage during inference
```

### Task 6.2: Create Comparison Report

```python
# TODO: Generate report with:
# - Accuracy vs speedup trade-off chart
# - Model size comparison
# - Inference latency breakdown
# - Recommendations for production
```

## Bonus: ONNX Runtime Quantization

```python
# TODO: Export quantized model to ONNX
# Use ONNX Runtime quantization
# Compare with PyTorch quantization
```

## Deliverables

- Quantized models (PTQ, QAT, mixed precision)
- Sensitivity analysis results
- Benchmark results and charts
- Performance report

## Expected Results

| Model | Accuracy Drop | Speedup | Size Reduction |
|-------|---------------|---------|----------------|
| PTQ   | 0.5-1%        | 2-3x    | 4x             |
| QAT   | 0-0.5%        | 2-3x    | 4x             |
| Mixed | <0.5%         | 1.5-2x  | 3x             |

---

**Lab Duration**: 5 hours
**Difficulty**: Intermediate to Advanced
