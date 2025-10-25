# Lab 01: TensorRT Optimization

## Objectives

By the end of this lab, you will:
1. Convert a PyTorch model to ONNX format
2. Build a TensorRT engine with FP16 optimization
3. Implement INT8 calibration for quantized inference
4. Handle dynamic batch sizes with optimization profiles
5. Benchmark performance improvements
6. Compare inference latency and throughput

**Estimated Time**: 5 hours

## Prerequisites

- Completed Lecture 02: TensorRT Deep Dive
- NVIDIA GPU with compute capability 7.0+ (Volta or newer)
- TensorRT 10.x installed
- PyTorch 2.0+ installed

## Setup

```bash
# Install dependencies
pip install torch torchvision onnx onnx-simplifier tensorrt pycuda

# Verify TensorRT installation
python -c "import tensorrt as trt; print(trt.__version__)"

# Download ImageNet validation set (or use subset)
# Or use CIFAR-10 for faster experimentation
```

## Part 1: Model Export to ONNX (45 minutes)

### Task 1.1: Export ResNet-50 to ONNX

```python
import torch
import torch.onnx
import torchvision.models as models

# TODO: Load pre-trained ResNet-50
model = models.resnet50(weights='IMAGENET1K_V1')
model.eval()

# TODO: Create dummy input
batch_size = 1
dummy_input = torch.randn(batch_size, 3, 224, 224, device='cuda')

# TODO: Export to ONNX with dynamic batch dimension
# Hints:
# - Use torch.onnx.export()
# - Set opset_version=18
# - Enable dynamic_axes for batch dimension
# - Enable do_constant_folding

# YOUR CODE HERE
```

### Task 1.2: Simplify ONNX Model

```python
import onnx
from onnxsim import simplify

# TODO: Load ONNX model
onnx_model = onnx.load("resnet50.onnx")

# TODO: Simplify model
# Hints:
# - Use simplify() from onnxsim
# - Check validation passes
# - Save simplified model

# YOUR CODE HERE

# Verify model
onnx.checker.check_model(onnx_model_simp)
```

**Deliverable**: `resnet50_simplified.onnx`

## Part 2: Build FP16 TensorRT Engine (60 minutes)

### Task 2.1: Create TensorRT Builder

```python
import tensorrt as trt
import numpy as np

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

# TODO: Create builder and network
# Hints:
# - Use trt.Builder()
# - Create network with EXPLICIT_BATCH flag
# - Use ONNX parser to populate network

# YOUR CODE HERE

def build_engine_fp16(onnx_path, engine_path):
    """
    Build TensorRT engine with FP16 precision

    Args:
        onnx_path: Path to ONNX model
        engine_path: Path to save TensorRT engine

    Returns:
        Serialized engine
    """
    # TODO: Implement engine building
    # Hints:
    # - Create builder, network, and parser
    # - Parse ONNX file
    # - Create builder config
    # - Set FP16 flag
    # - Set workspace memory (2GB)
    # - Build and serialize engine

    # YOUR CODE HERE

    return serialized_engine

# Build FP16 engine
engine_fp16 = build_engine_fp16("resnet50_simplified.onnx", "resnet50_fp16.engine")
```

### Task 2.2: Create Dynamic Shape Engine

```python
def build_engine_dynamic(onnx_path, engine_path):
    """
    Build TensorRT engine with dynamic batch size

    Args:
        onnx_path: Path to ONNX model
        engine_path: Path to save TensorRT engine

    Returns:
        Serialized engine
    """
    # TODO: Implement dynamic shape engine
    # Hints:
    # - Create optimization profile
    # - Set min/opt/max shapes for 'input'
    #   - min: (1, 3, 224, 224)
    #   - opt: (8, 3, 224, 224)
    #   - max: (32, 3, 224, 224)
    # - Add profile to config
    # - Build engine

    # YOUR CODE HERE

    return serialized_engine

# Build dynamic engine
engine_dynamic = build_engine_dynamic("resnet50_simplified.onnx", "resnet50_dynamic_fp16.engine")
```

**Deliverables**:
- `resnet50_fp16.engine`
- `resnet50_dynamic_fp16.engine`

## Part 3: INT8 Calibration (90 minutes)

### Task 3.1: Implement Calibration Dataset

```python
import torch
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms

class CalibrationDataset(Dataset):
    """
    Dataset for INT8 calibration

    Use representative samples from training/validation set
    """
    def __init__(self, data_dir, num_samples=1000):
        # TODO: Implement calibration dataset
        # Hints:
        # - Load images from data_dir
        # - Apply ImageNet preprocessing
        # - Limit to num_samples images

        # YOUR CODE HERE
        pass

    def __len__(self):
        # YOUR CODE HERE
        pass

    def __getitem__(self, idx):
        # TODO: Return preprocessed image
        # YOUR CODE HERE
        pass

# Create calibration dataset
calib_dataset = CalibrationDataset("/path/to/imagenet/val", num_samples=1000)
calib_loader = DataLoader(calib_dataset, batch_size=32, shuffle=False)
```

### Task 3.2: Implement INT8 Calibrator

```python
import pycuda.driver as cuda
import pycuda.autoinit

class Int8EntropyCalibrator(trt.IInt8EntropyCalibrator2):
    """
    Entropy calibrator for INT8 quantization
    """
    def __init__(self, calibration_loader, cache_file):
        super().__init__()
        # TODO: Initialize calibrator
        # Hints:
        # - Store calibration_loader
        # - Store cache_file path
        # - Create iterator
        # - Allocate device memory for input

        # YOUR CODE HERE

    def get_batch_size(self):
        # TODO: Return batch size
        # YOUR CODE HERE
        pass

    def get_batch(self, names):
        """
        Get next batch for calibration

        Returns:
            List of device pointers to input data
        """
        # TODO: Implement batch retrieval
        # Hints:
        # - Get next batch from iterator
        # - Copy to device memory
        # - Return list of device pointers
        # - Return None when done

        # YOUR CODE HERE
        pass

    def read_calibration_cache(self):
        """
        Read calibration cache if exists
        """
        # TODO: Implement cache reading
        # YOUR CODE HERE
        pass

    def write_calibration_cache(self, cache):
        """
        Write calibration cache
        """
        # TODO: Implement cache writing
        # YOUR CODE HERE
        pass

# Create calibrator
calibrator = Int8EntropyCalibrator(calib_loader, "resnet50_calib.cache")
```

### Task 3.3: Build INT8 Engine

```python
def build_engine_int8(onnx_path, engine_path, calibrator):
    """
    Build TensorRT engine with INT8 quantization

    Args:
        onnx_path: Path to ONNX model
        engine_path: Path to save engine
        calibrator: INT8 calibrator

    Returns:
        Serialized engine
    """
    # TODO: Implement INT8 engine building
    # Hints:
    # - Create builder and network
    # - Parse ONNX
    # - Create config with INT8 flag
    # - Set calibrator
    # - Build engine

    # YOUR CODE HERE

    return serialized_engine

# Build INT8 engine
engine_int8 = build_engine_int8(
    "resnet50_simplified.onnx",
    "resnet50_int8.engine",
    calibrator
)
```

**Deliverables**:
- `resnet50_int8.engine`
- `resnet50_calib.cache`

## Part 4: Inference Implementation (60 minutes)

### Task 4.1: Create Inference Class

```python
class TensorRTInference:
    """
    Wrapper for TensorRT inference
    """
    def __init__(self, engine_path):
        # TODO: Initialize inference
        # Hints:
        # - Load engine from file
        # - Create runtime
        # - Deserialize engine
        # - Create execution context
        # - Allocate device buffers

        # YOUR CODE HERE

    def allocate_buffers(self):
        """
        Allocate input/output buffers
        """
        # TODO: Allocate buffers for all bindings
        # Hints:
        # - Iterate over engine bindings
        # - Get binding dimensions
        # - Allocate device memory
        # - Create host buffers for input/output

        # YOUR CODE HERE

    def infer(self, input_data):
        """
        Run inference

        Args:
            input_data: numpy array [batch, channels, height, width]

        Returns:
            output: numpy array [batch, num_classes]
        """
        # TODO: Implement inference
        # Hints:
        # - Copy input to device
        # - Execute context
        # - Copy output to host
        # - Return results

        # YOUR CODE HERE

    def __del__(self):
        # TODO: Cleanup
        # Free device memory
        pass

# Create inference engines
model_fp32 = models.resnet50(weights='IMAGENET1K_V1').cuda().eval()
model_fp16 = TensorRTInference("resnet50_fp16.engine")
model_int8 = TensorRTInference("resnet50_int8.engine")
```

## Part 5: Benchmarking and Evaluation (90 minutes)

### Task 5.1: Implement Latency Benchmark

```python
import time
import numpy as np

def benchmark_latency(model, input_data, num_iterations=1000, warmup=10):
    """
    Benchmark inference latency

    Args:
        model: Model to benchmark
        input_data: Sample input
        num_iterations: Number of iterations
        warmup: Warmup iterations

    Returns:
        dict with latency statistics
    """
    # TODO: Implement latency benchmarking
    # Hints:
    # - Warmup iterations
    # - Measure each iteration
    # - Compute statistics (mean, median, p95, p99)
    # - Use torch.cuda.synchronize() for accurate timing

    # YOUR CODE HERE

    return {
        'mean_ms': None,
        'median_ms': None,
        'p95_ms': None,
        'p99_ms': None,
        'std_ms': None
    }

# Benchmark all models
input_fp32 = torch.randn(1, 3, 224, 224, device='cuda')
input_np = input_fp32.cpu().numpy()

print("Benchmarking FP32 (PyTorch)...")
latency_fp32 = benchmark_latency(model_fp32, input_fp32)

print("Benchmarking FP16 (TensorRT)...")
latency_fp16 = benchmark_latency(model_fp16, input_np)

print("Benchmarking INT8 (TensorRT)...")
latency_int8 = benchmark_latency(model_int8, input_np)

# Print results
print("\n=== Latency Results ===")
print(f"FP32: {latency_fp32['mean_ms']:.2f} ms")
print(f"FP16: {latency_fp16['mean_ms']:.2f} ms ({latency_fp32['mean_ms']/latency_fp16['mean_ms']:.2f}x speedup)")
print(f"INT8: {latency_int8['mean_ms']:.2f} ms ({latency_fp32['mean_ms']/latency_int8['mean_ms']:.2f}x speedup)")
```

### Task 5.2: Implement Throughput Benchmark

```python
def benchmark_throughput(model, batch_size, duration_sec=60):
    """
    Benchmark throughput (QPS)

    Args:
        model: Model to benchmark
        batch_size: Batch size
        duration_sec: Benchmark duration

    Returns:
        Throughput in queries per second
    """
    # TODO: Implement throughput benchmarking
    # Hints:
    # - Generate random inputs
    # - Run for duration_sec
    # - Count total queries processed
    # - Compute QPS

    # YOUR CODE HERE

    return qps

# Benchmark throughput for different batch sizes
batch_sizes = [1, 4, 8, 16, 32]

print("\n=== Throughput Results (QPS) ===")
print(f"{'Batch':<8} {'FP32':<12} {'FP16':<12} {'INT8':<12}")
print("-" * 50)

for bs in batch_sizes:
    # TODO: Benchmark each model with batch size
    # YOUR CODE HERE
    pass
```

### Task 5.3: Accuracy Evaluation

```python
def evaluate_accuracy(model, val_loader, num_samples=1000):
    """
    Evaluate model accuracy on validation set

    Args:
        model: Model to evaluate
        val_loader: Validation data loader
        num_samples: Number of samples to evaluate

    Returns:
        Top-1 and Top-5 accuracy
    """
    # TODO: Implement accuracy evaluation
    # Hints:
    # - Iterate over val_loader
    # - Run inference
    # - Compute top-1 and top-5 accuracy
    # - Limit to num_samples

    # YOUR CODE HERE

    return top1_acc, top5_acc

# Evaluate accuracy
print("\n=== Accuracy Results ===")

# TODO: Create validation data loader
# val_loader = ...

# Evaluate all models
acc_fp32 = evaluate_accuracy(model_fp32, val_loader)
acc_fp16 = evaluate_accuracy(model_fp16, val_loader)
acc_int8 = evaluate_accuracy(model_int8, val_loader)

print(f"FP32 - Top-1: {acc_fp32[0]:.2f}%, Top-5: {acc_fp32[1]:.2f}%")
print(f"FP16 - Top-1: {acc_fp16[0]:.2f}%, Top-5: {acc_fp16[1]:.2f}%")
print(f"INT8 - Top-1: {acc_int8[0]:.2f}%, Top-5: {acc_int8[1]:.2f}%")

print(f"\nFP16 Accuracy Drop: {acc_fp32[0] - acc_fp16[0]:.2f}%")
print(f"INT8 Accuracy Drop: {acc_fp32[0] - acc_int8[0]:.2f}%")
```

## Part 6: Analysis and Report (30 minutes)

### Task 6.1: Generate Performance Report

Create a comprehensive report with the following:

```python
# TODO: Generate report with:
# 1. Model sizes (FP32, FP16, INT8)
# 2. Latency comparison (table and chart)
# 3. Throughput comparison (table and chart)
# 4. Accuracy comparison
# 5. Speedup analysis
# 6. Memory usage

# Example report structure:
report = {
    'model_sizes': {
        'fp32': get_model_size(model_fp32),
        'fp16': get_file_size('resnet50_fp16.engine'),
        'int8': get_file_size('resnet50_int8.engine')
    },
    'latency': {
        'fp32': latency_fp32,
        'fp16': latency_fp16,
        'int8': latency_int8
    },
    'throughput': {
        # ... throughput results
    },
    'accuracy': {
        # ... accuracy results
    }
}

# Generate visualizations
import matplotlib.pyplot as plt

# TODO: Create charts for:
# - Latency comparison
# - Throughput vs batch size
# - Speedup comparison
# - Accuracy vs speedup trade-off
```

**Expected Results**:
- FP16: 2-3x speedup, <0.1% accuracy loss
- INT8: 3-5x speedup, 0.5-1% accuracy loss
- Model size reduction: 2x (FP16), 4x (INT8)

## Bonus Challenges (Optional)

### Challenge 1: Mixed Precision

Implement mixed precision engine where some layers use INT8 and others use FP16:

```python
# TODO: Mark sensitive layers for FP16, rest INT8
# Hints:
# - Use layer-wise sensitivity analysis
# - Keep first/last layers in FP16
# - Use STRICT_TYPES flag
```

### Challenge 2: Optimization Profiles Analysis

Compare performance across different batch sizes:

```python
# TODO: Test dynamic engine with various batch sizes
# Compare against separate static engines
# Analyze performance trade-offs
```

### Challenge 3: BERT Optimization

Apply the same techniques to BERT-base:

```python
# TODO: Export BERT to ONNX
# Build FP16 and INT8 engines
# Handle dynamic sequence lengths
# Benchmark on SQuAD or GLUE
```

## Submission Checklist

- [ ] ONNX model exported and simplified
- [ ] FP16 TensorRT engine built
- [ ] INT8 calibration implemented
- [ ] INT8 TensorRT engine built
- [ ] Inference wrapper implemented
- [ ] Latency benchmark completed
- [ ] Throughput benchmark completed
- [ ] Accuracy evaluation completed
- [ ] Performance report generated
- [ ] Code documented and formatted

## Evaluation Criteria

- **Correctness** (40%): All engines build and run correctly
- **Performance** (30%): Achieves expected speedups
- **Accuracy** (15%): Accuracy maintained within acceptable range
- **Documentation** (15%): Clear code and comprehensive report

## Troubleshooting

**Issue**: Engine build fails
- Check ONNX model is valid
- Verify TensorRT version compatibility
- Ensure sufficient GPU memory

**Issue**: INT8 accuracy drop too high
- Use more calibration samples
- Try different calibration algorithm
- Identify sensitive layers for mixed precision

**Issue**: Slow inference
- Ensure CUDA synchronization in benchmarks
- Check batch size is within optimization profile
- Verify GPU utilization with nvidia-smi

## Resources

- [TensorRT Documentation](https://docs.nvidia.com/deeplearning/tensorrt/)
- [TensorRT Python API](https://docs.nvidia.com/deeplearning/tensorrt/api/python_api/)
- [ONNX Model Zoo](https://github.com/onnx/models)
- [TensorRT Examples](https://github.com/NVIDIA/TensorRT)

---

**Lab Duration**: 5 hours
**Difficulty**: Advanced
**Due**: Complete before Module 204 assessment
