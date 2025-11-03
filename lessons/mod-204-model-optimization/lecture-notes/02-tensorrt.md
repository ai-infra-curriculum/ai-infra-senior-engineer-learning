# Lecture 02: TensorRT Deep Dive

## Learning Objectives

By the end of this lecture, you will be able to:

- Architect TensorRT optimization pipelines that leverage layer fusion, kernel auto-tuning, and precision calibration to achieve 2-10x speedup over framework inference
- Implement INT8 quantization with multiple calibration algorithms (entropy, minmax, percentile) using representative calibration datasets of 500-1000 samples
- Configure dynamic shape optimization profiles with appropriate min/opt/max ranges to handle variable batch sizes and sequence lengths in production
- Design custom TensorRT plugins in C++/CUDA for unsupported operations with optimized kernels, proper memory management, and multi-precision support
- Implement FP16/INT8 mixed precision strategies with per-layer precision control to balance performance gains with accuracy requirements
- Configure advanced TensorRT features including timing cache for faster rebuilds, multi-stream execution, and version compatibility management
- Troubleshoot common TensorRT issues including calibration accuracy degradation, dynamic shape performance problems, and out-of-memory errors
- Benchmark TensorRT engines with proper warmup, measure latency percentiles and throughput, and profile per-layer execution time using NVIDIA Nsight tools

## Table of Contents
1. [Introduction to TensorRT](#introduction)
2. [TensorRT Architecture](#architecture)
3. [Optimization Process](#optimization-process)
4. [Layer Fusion and Kernel Auto-tuning](#layer-fusion)
5. [Precision Calibration](#precision-calibration)
6. [Dynamic Shapes and Optimization Profiles](#dynamic-shapes)
7. [Custom Plugins](#custom-plugins)
8. [Advanced Features](#advanced-features)
9. [Performance Analysis](#performance-analysis)
10. [Best Practices and Troubleshooting](#best-practices)

<a name="introduction"></a>
## 1. Introduction to TensorRT

NVIDIA TensorRT is a high-performance deep learning inference optimizer and runtime library. It's specifically designed to maximize inference performance on NVIDIA GPUs, delivering up to 10x faster inference compared to framework-native implementations.

### Why TensorRT?

**Framework Problem**: Native PyTorch and TensorFlow implementations are designed for flexibility and ease of use, not maximum performance. They:
- Execute operations one at a time
- Use generic kernels
- Don't fully utilize GPU hardware features
- Have significant Python overhead

**TensorRT Solution**: Optimizes models through:
- Layer fusion to reduce memory transfers
- Precision calibration for INT8 and FP16
- Kernel auto-tuning for specific hardware
- Dynamic tensor memory management
- Graph optimization and operator elimination

### TensorRT Evolution

- **TensorRT 1-3** (2016-2017): Basic optimizations, FP32/FP16
- **TensorRT 4-5** (2018-2019): INT8 quantization, dynamic shapes
- **TensorRT 6-7** (2020-2021): ONNX support, improved INT8
- **TensorRT 8** (2022): Transformer optimizations, multi-GPU
- **TensorRT 9** (2023): FP8 support, improved LLM performance
- **TensorRT 10** (2024-2025): Advanced quantization, state-of-the-art LLM optimizations

### When to Use TensorRT

**Ideal Use Cases**:
- Production inference on NVIDIA GPUs
- Latency-critical applications
- Compute-bound models (CNNs, Transformers)
- Models with standard operations

**Less Suitable**:
- Models with many custom operations
- Frequent model updates (re-optimization overhead)
- Non-NVIDIA hardware
- Highly dynamic models with variable control flow

<a name="architecture"></a>
## 2. TensorRT Architecture

### 2.1 Core Components

**Builder**: Optimizes and builds TensorRT engines
```python
import tensorrt as trt

# Create builder
builder = trt.Builder(TRT_LOGGER)

# Create network definition
network = builder.create_network(
    1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
)

# Create builder config
config = builder.create_builder_config()
config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 4 << 30)  # 4GB

# Build engine
engine = builder.build_serialized_network(network, config)
```

**Engine**: Optimized model ready for inference
- Contains optimized kernels and execution plan
- Hardware-specific compilation
- Serializable for deployment

**Context**: Execution environment for inference
- Manages state and buffers
- Thread-safe (one per thread)
- Handles dynamic shapes

**Plugins**: Custom layer implementations
- Extend TensorRT with custom operations
- C++ implementation required

### 2.2 Workflow Overview

```
Model (PyTorch/TF/ONNX)
    ↓
Parse/Import to TensorRT Network
    ↓
Graph Optimization
    ↓
Layer Fusion
    ↓
Kernel Selection & Auto-tuning
    ↓
Precision Calibration (INT8)
    ↓
Build Optimized Engine
    ↓
Serialize for Deployment
    ↓
Runtime Inference
```

### 2.3 Memory Management

TensorRT uses sophisticated memory management:

**Workspace Memory**: Temporary memory for optimization
- Set via `set_memory_pool_limit()`
- More workspace = better optimization (to a point)
- Typical: 1-8GB

**Device Memory**: Persistent buffers for weights and activations
- Automatically managed
- Optimized for reuse

**Managed Memory**: Unified CPU/GPU memory
- Useful for very large models
- Slight performance penalty

<a name="optimization-process"></a>
## 3. Optimization Process

### 3.1 Graph Optimization

TensorRT performs multiple graph-level optimizations:

**Dead Layer Elimination**:
```python
# Before optimization
x = input
y = conv1(x)
z = conv2(y)  # Not used in output
output = conv3(y)

# After optimization
x = input
y = conv1(x)
output = conv3(y)  # conv2 removed
```

**Vertical Fusion**: Combine sequential layers
```python
# Before: Conv → BatchNorm → ReLU (3 kernel launches)
# After: ConvBatchNormReLU (1 fused kernel)
```

**Horizontal Fusion**: Combine parallel operations
```python
# Before: Two separate convolutions on same input
conv1_out = conv1(x)
conv2_out = conv2(x)

# After: Single fused kernel computing both
conv1_out, conv2_out = fused_conv(x)
```

**Constant Folding**: Compute constant operations at build time
```python
# Before
x = input
y = constant1 + constant2  # Computed at inference time
output = x * y

# After
x = input
y_precomputed = 5  # Computed at build time
output = x * y_precomputed
```

### 3.2 Operator Optimization

**Convolution Optimization**:
- Algorithm selection (implicit GEMM, Winograd, FFT)
- Optimal tile sizes
- Tensor Core utilization

**MatMul Optimization**:
- cuBLAS algorithm selection
- Tensor Core usage for FP16/INT8
- Optimal blocking strategies

**Attention Optimization**:
- Flash Attention kernels
- Fused QKV projections
- Optimized softmax

### 3.3 Precision Selection

TensorRT can use different precisions per layer:

```python
# Set allowed precision modes
config.set_flag(trt.BuilderFlag.FP16)
config.set_flag(trt.BuilderFlag.INT8)

# TensorRT will select best precision per layer
# Some layers may stay FP32 for accuracy
# Others may use FP16 or INT8 for speed
```

**Precision Priority**: FP32 → FP16 → INT8
- TensorRT tries INT8 first (if enabled)
- Falls back to FP16 or FP32 if accuracy degrades

<a name="layer-fusion"></a>
## 4. Layer Fusion and Kernel Auto-tuning

### 4.1 Layer Fusion Patterns

Layer fusion reduces memory bandwidth by keeping data in cache:

**CBR Fusion** (Convolution + BatchNorm + ReLU):
```python
# Unfused: 3 kernel launches, 6 memory transfers
conv_out = conv2d(x)           # Read x, write conv_out
bn_out = batch_norm(conv_out)  # Read conv_out, write bn_out
out = relu(bn_out)             # Read bn_out, write out

# Fused: 1 kernel launch, 2 memory transfers
out = conv_bn_relu_fused(x)    # Read x, write out

# Speedup: ~2-3x for this sequence
```

**Attention Fusion**:
```python
# Unfused attention (7+ operations)
Q = linear_q(x)
K = linear_k(x)
V = linear_v(x)
scores = matmul(Q, K.T)
scores = scores / sqrt(d_k)
attn = softmax(scores)
out = matmul(attn, V)

# Fused attention (1 operation)
out = fused_attention(x, weights_qkv)

# Speedup: 3-5x depending on sequence length
```

**Pointwise Fusion**:
```python
# Multiple element-wise operations
x = input
y = add(x, bias)
y = multiply(y, scale)
y = relu(y)
y = divide(y, norm)

# Fused into single kernel
y = fused_pointwise(x, bias, scale, norm)
```

### 4.2 Kernel Auto-tuning

TensorRT benchmarks multiple kernel implementations and selects the fastest:

**Convolution Algorithm Selection**:
```python
# TensorRT evaluates:
# 1. IMPLICIT_GEMM (best for most cases)
# 2. IMPLICIT_PRECOMP_GEMM
# 3. WINOGRAD (good for 3x3 convs)
# 4. FFT (rarely used)
# 5. DIRECT (small kernels)

# Selection based on:
# - Input/output dimensions
# - Kernel size
# - Stride and padding
# - Batch size
# - GPU architecture
```

**Tile Size Optimization**:
- TensorRT tests multiple tile sizes
- Balances GPU occupancy vs. cache utilization
- Hardware-specific tuning

**Tensor Core Utilization**:
```python
# Automatic Tensor Core usage when:
# 1. Data type is FP16/BF16/INT8/FP8
# 2. Dimensions are multiples of 8 or 16
# 3. Available on GPU (Volta+)

# Example: MatMul with Tensor Cores
# M, N, K = 1024, 1024, 1024 (good dimensions)
# Data type: FP16
# Result: ~10x faster than FP32 CUDA cores
```

### 4.3 Memory Optimization

**Activation Reuse**:
```python
# TensorRT analyzes tensor lifetimes
# Reuses memory for non-overlapping tensors

# Example network:
# t1 = conv1(input)  # Allocate buffer A
# t2 = conv2(t1)     # Allocate buffer B, free A
# t3 = conv3(t2)     # Reuse buffer A, free B
# output = conv4(t3) # Reuse buffer B, free A

# Without optimization: A + B memory
# With optimization: max(A, B) memory
```

**In-place Operations**:
- Operations that can modify tensors in-place
- ReLU, BatchNorm, Dropout often in-place
- Reduces memory footprint

<a name="precision-calibration"></a>
## 5. Precision Calibration

### 5.1 FP16 Mixed Precision

FP16 is the easiest optimization with significant benefits:

```python
import tensorrt as trt

builder = trt.Builder(logger)
config = builder.create_builder_config()

# Enable FP16 precision
config.set_flag(trt.BuilderFlag.FP16)

# TensorRT will use FP16 where possible
# Some layers stay FP32 for numerical stability
engine = builder.build_serialized_network(network, config)
```

**Benefits**:
- 2x faster compute on Tensor Cores
- 2x less memory bandwidth
- 2x smaller model size
- Minimal accuracy loss (<0.1% typically)

**Numerical Considerations**:
- FP16 range: ~6e-5 to 65,504
- Underflow risk for very small values
- Overflow risk for large values
- TensorRT keeps sensitive ops in FP32

### 5.2 INT8 Quantization

INT8 provides maximum performance but requires calibration:

**Quantization Basics**:
```python
# Symmetric quantization
# Map FP32 range to INT8 [-127, 127]

scale = max(abs(tensor_values)) / 127.0
quantized = round(tensor_values / scale).clip(-127, 127)

# Dequantization for next layer
dequantized = quantized * scale
```

**Calibration Process**:
```python
import tensorrt as trt

# 1. Create calibrator
class EntropyCalibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calibration_data):
        super().__init__()
        self.calibration_data = calibration_data
        self.batch_size = 32
        self.current_index = 0

    def get_batch_size(self):
        return self.batch_size

    def get_batch(self, names):
        if self.current_index >= len(self.calibration_data):
            return None

        batch = self.calibration_data[self.current_index]
        self.current_index += 1

        # Return dict of input_name -> GPU pointer
        return [batch.data_ptr()]

    def read_calibration_cache(self):
        # Return cached calibration if available
        if os.path.exists('calibration.cache'):
            with open('calibration.cache', 'rb') as f:
                return f.read()
        return None

    def write_calibration_cache(self, cache):
        with open('calibration.cache', 'wb') as f:
            f.write(cache)

# 2. Configure builder
config.set_flag(trt.BuilderFlag.INT8)
config.int8_calibrator = EntropyCalibrator(calibration_data)

# 3. Build engine (calibration happens automatically)
engine = builder.build_serialized_network(network, config)
```

**Calibration Algorithms**:

1. **Entropy Calibration (IInt8EntropyCalibrator2)**:
   - Minimizes information loss
   - Best for most use cases
   - Default recommendation

2. **MinMax Calibration (IInt8MinMaxCalibrator)**:
   - Uses min/max values directly
   - Fast but can be suboptimal
   - Good for debugging

3. **Percentile Calibration (IInt8LegacyCalibrator)**:
   - Uses percentile clipping
   - More robust to outliers
   - Legacy, less commonly used

**Calibration Dataset**:
- Use 500-1000 representative samples
- Should cover data distribution
- Same preprocessing as training
- More data doesn't always help beyond ~1000 samples

### 5.3 Mixed Precision Strategies

TensorRT can mix precisions for optimal accuracy/performance:

```python
# Per-layer precision control
config.set_flag(trt.BuilderFlag.STRICT_TYPES)

# Mark specific layers to keep in FP32
for layer in network:
    if layer.name in sensitive_layers:
        layer.precision = trt.float32
        layer.set_output_type(0, trt.float32)
```

**Common Patterns**:
- First layer: Often FP32 for numerical stability
- Final layer: Often FP32 for precision
- Attention: FP16 or FP32 (softmax sensitive)
- Convolutions: INT8 or FP16 (less sensitive)

### 5.4 Quantization-Aware Training (QAT)

For better INT8 accuracy, use QAT during training:

```python
import torch
from pytorch_quantization import nn as quant_nn
from pytorch_quantization import calib

# 1. Replace layers with quantized versions
quant_nn.TensorQuantizer.use_fb_fake_quant = True

# 2. Train with fake quantization
model = YourModel()
# ... training loop with quantization simulation

# 3. Calibrate and export
# Calibration collects statistics
with torch.no_grad():
    for data in calibration_loader:
        model(data)

# 4. Export to ONNX
torch.onnx.export(model, dummy_input, "model_qat.onnx")

# 5. Convert to TensorRT with INT8
# No calibration needed - scales embedded in ONNX
```

**QAT Benefits**:
- Better accuracy than PTQ (0.5-1% improvement)
- More robust quantization
- Can recover accuracy loss

**QAT Costs**:
- Requires retraining
- Longer training time
- More complex workflow

<a name="dynamic-shapes"></a>
## 6. Dynamic Shapes and Optimization Profiles

### 6.1 The Dynamic Shape Problem

Static engines are optimized for specific input dimensions:

```python
# Static engine: Only works for [batch=1, channels=3, height=224, width=224]
engine = build_static_engine(network, config)

# Problem: What if batch size varies? Need to rebuild!
```

### 6.2 Optimization Profiles

Optimization profiles allow handling dynamic dimensions:

```python
import tensorrt as trt

builder = trt.Builder(logger)
network = builder.create_network(
    1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
)

# Define input with dynamic batch and sequence length
input_tensor = network.add_input(
    name="input",
    dtype=trt.float32,
    shape=(-1, -1, 768)  # [batch, seq_len, hidden]
)

# Create optimization profile
profile = builder.create_optimization_profile()

# Set min, optimal, max shapes
profile.set_shape(
    "input",
    min=(1, 128, 768),      # Min: batch=1, seq=128
    opt=(16, 512, 768),     # Optimal: batch=16, seq=512
    max=(32, 2048, 768)     # Max: batch=32, seq=2048
)

# Add profile to config
config = builder.create_builder_config()
config.add_optimization_profile(profile)

# Build engine optimized for shape range
engine = builder.build_serialized_network(network, config)
```

### 6.3 Multiple Optimization Profiles

For very different workloads, use multiple profiles:

```python
# Profile 1: Small batches, low latency
profile1 = builder.create_optimization_profile()
profile1.set_shape("input",
    min=(1, 64, 768),
    opt=(1, 128, 768),
    max=(4, 256, 768)
)

# Profile 2: Large batches, high throughput
profile2 = builder.create_optimization_profile()
profile2.set_shape("input",
    min=(8, 256, 768),
    opt=(32, 512, 768),
    max=(64, 1024, 768)
)

config.add_optimization_profile(profile1)
config.add_optimization_profile(profile2)

# At inference time, select profile
context = engine.create_execution_context()
context.set_optimization_profile_async(0, stream)  # Use profile 1
```

### 6.4 Best Practices for Dynamic Shapes

**Profile Selection**:
- `min`: Smallest shape you'll encounter
- `opt`: Most common shape (80% of traffic)
- `max`: Largest shape you need to support

**Performance Considerations**:
- Engine is most optimized for `opt` shape
- Shapes far from `opt` may be slower
- Use multiple profiles for very different workloads

**Pitfalls**:
- Too wide range (min=1, max=1024) → suboptimal performance
- Too narrow range → runtime errors if exceeded
- Wrong `opt` value → slow for common case

<a name="custom-plugins"></a>
## 7. Custom Plugins

### 7.1 When to Write Plugins

Write custom plugins when:
- Operation not supported in TensorRT
- Custom fusion for specific pattern
- Specialized hardware utilization
- Performance-critical custom operation

### 7.2 Plugin Implementation

Plugins are implemented in C++:

```cpp
// Custom RoPE (Rotary Position Embedding) plugin
class RoPEPlugin : public nvinfer1::IPluginV2DynamicExt {
public:
    // Configure plugin with input/output info
    void configurePlugin(
        const nvinfer1::DynamicPluginTensorDesc* in,
        int nbInputs,
        const nvinfer1::DynamicPluginTensorDesc* out,
        int nbOutputs) override {
        // Store configuration
    }

    // Return output dimensions
    nvinfer1::DimsExprs getOutputDimensions(
        int outputIndex,
        const nvinfer1::DimsExprs* inputs,
        int nbInputs,
        nvinfer1::IExprBuilder& exprBuilder) override {
        // Output shape = input shape
        return inputs[0];
    }

    // Enqueue execution
    int enqueue(
        const nvinfer1::PluginTensorDesc* inputDesc,
        const nvinfer1::PluginTensorDesc* outputDesc,
        const void* const* inputs,
        void* const* outputs,
        void* workspace,
        cudaStream_t stream) override {

        // Launch CUDA kernel
        const float* input = static_cast<const float*>(inputs[0]);
        float* output = static_cast<float*>(outputs[0]);

        rope_kernel<<<grid, block, 0, stream>>>(
            input, output, batch, seq_len, hidden
        );

        return 0;
    }

    // Other required methods...
};

// CUDA kernel implementation
__global__ void rope_kernel(
    const float* input,
    float* output,
    int batch,
    int seq_len,
    int hidden) {

    // Implement RoPE logic
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < batch * seq_len * hidden) {
        // ... RoPE computation
    }
}
```

### 7.3 Using Plugins in Python

```python
import tensorrt as trt
import ctypes

# Load plugin library
ctypes.CDLL("libcustom_plugins.so")

# Plugin creator is automatically registered
# Use in network
network = builder.create_network(...)

# Add custom plugin layer
plugin_creator = trt.get_plugin_registry().get_plugin_creator(
    "RoPEPlugin", "1"
)
plugin = plugin_creator.create_plugin("rope", trt.PluginFieldCollection([]))

layer = network.add_plugin_v2([input_tensor], plugin)
output = layer.get_output(0)
```

### 7.4 Plugin Best Practices

- **Optimize CUDA kernels**: Use shared memory, coalescing
- **Support multiple precisions**: FP32, FP16, INT8
- **Handle dynamic shapes**: Don't hardcode dimensions
- **Minimize memory transfers**: Fuse operations when possible
- **Provide fallback**: CPU implementation for testing

<a name="advanced-features"></a>
## 8. Advanced Features

### 8.1 Timing Cache

Reuse kernel tuning results across builds:

```python
# Save timing cache
timing_cache = config.create_timing_cache(b"")
config.set_timing_cache(timing_cache, ignore_mismatch=False)

# Build engine (timing cache is populated)
engine = builder.build_serialized_network(network, config)

# Serialize cache for reuse
cache_data = timing_cache.serialize()
with open("timing.cache", "wb") as f:
    f.write(cache_data)

# Load cache for next build
with open("timing.cache", "rb") as f:
    cache_data = f.read()
timing_cache = config.create_timing_cache(cache_data)
config.set_timing_cache(timing_cache, ignore_mismatch=False)
```

**Benefits**:
- Much faster engine rebuilds
- Consistent performance across builds
- Shareable across similar hardware

### 8.2 Tactics and Algorithms

Fine-grained control over kernel selection:

```python
# Disable specific tactics
tactic_sources = config.get_tactic_sources()
tactic_sources &= ~(1 << int(trt.TacticSource.CUBLAS))  # Disable cuBLAS
config.set_tactic_sources(tactic_sources)

# Algorithm selector for custom logic
class CustomAlgorithmSelector(trt.IAlgorithmSelector):
    def select_algorithms(self, context, choices):
        # Custom algorithm selection logic
        # Return list of acceptable algorithms
        return [choices[0]]  # Select first available

config.algorithm_selector = CustomAlgorithmSelector()
```

### 8.3 Version Compatibility

TensorRT engines are hardware and version-specific:

```python
# Engine metadata
print(f"TensorRT version: {trt.__version__}")
print(f"CUDA version: {engine.get_device_memory_size()}")

# Best practice: Store version info with engine
metadata = {
    'trt_version': trt.__version__,
    'cuda_version': get_cuda_version(),
    'gpu_model': get_gpu_model(),
    'build_date': datetime.now().isoformat()
}

# Rebuild engine if versions mismatch
```

### 8.4 Multi-stream Execution

Concurrent inference with multiple streams:

```python
import tensorrt as trt
import pycuda.driver as cuda

# Create multiple contexts (thread-safe)
contexts = [engine.create_execution_context() for _ in range(4)]

# Create CUDA streams
streams = [cuda.Stream() for _ in range(4)]

# Concurrent inference
for i, (data, context, stream) in enumerate(zip(batches, contexts, streams)):
    # Async memory copy
    cuda.memcpy_htod_async(d_input, data, stream)

    # Execute inference
    context.execute_async_v2(bindings, stream.handle)

    # Async copy results back
    cuda.memcpy_dtoh_async(output, d_output, stream)

# Synchronize all streams
for stream in streams:
    stream.synchronize()
```

<a name="performance-analysis"></a>
## 9. Performance Analysis

### 9.1 Layer Timing

Profile per-layer execution time:

```python
# Enable profiling
context.profiler = trt.Profiler()

# Run inference
context.execute_v2(bindings)

# Get layer timings
profiler_data = context.profiler.get_layer_timing()
for layer_name, time_ms in profiler_data:
    print(f"{layer_name}: {time_ms:.3f} ms")
```

### 9.2 Using NVIDIA Nsight

Detailed GPU profiling:

```bash
# Profile with Nsight Systems
nsys profile -o tensorrt_profile python inference.py

# View in Nsight Systems GUI
nsys-ui tensorrt_profile.qdrep

# Profile with Nsight Compute (kernel-level)
ncu --set full -o kernel_profile python inference.py
```

### 9.3 Performance Metrics

Key metrics to monitor:

```python
import time
import numpy as np

def benchmark_tensorrt(engine, context, inputs, num_iterations=1000):
    # Warmup
    for _ in range(10):
        context.execute_v2(inputs)

    # Benchmark
    timings = []
    for _ in range(num_iterations):
        start = time.perf_counter()
        context.execute_v2(inputs)
        cuda.Context.synchronize()
        end = time.perf_counter()
        timings.append((end - start) * 1000)  # Convert to ms

    timings = np.array(timings)

    return {
        'mean_ms': np.mean(timings),
        'median_ms': np.median(timings),
        'p95_ms': np.percentile(timings, 95),
        'p99_ms': np.percentile(timings, 99),
        'std_ms': np.std(timings),
        'throughput_qps': 1000 / np.mean(timings)
    }
```

<a name="best-practices"></a>
## 10. Best Practices and Troubleshooting

### 10.1 Best Practices

**Model Conversion**:
- Use ONNX as intermediate format (better than direct conversion)
- Simplify ONNX graph before conversion (onnx-simplifier)
- Validate ONNX model before TensorRT conversion
- Test with sample inputs during conversion

**Builder Configuration**:
- Provide sufficient workspace memory (2-8GB typical)
- Use timing cache for faster rebuilds
- Set appropriate optimization profiles for dynamic shapes
- Enable only needed precision modes (don't enable INT8 if not using)

**Calibration**:
- Use representative calibration data
- 500-1000 samples usually sufficient
- Same preprocessing as inference
- Cache calibration results

**Inference**:
- Reuse contexts across inferences (don't recreate)
- Use async execution with CUDA streams
- Batch requests when possible
- Monitor GPU utilization

**Deployment**:
- Store TensorRT version and hardware info with engine
- Rebuild engines for production hardware
- Test edge cases and corner cases
- Have fallback to framework inference

### 10.2 Common Issues and Solutions

**Issue: Engine build fails with "out of memory"**

Solution:
```python
# Reduce workspace memory
config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB

# Or use DLA (if available)
config.default_device_type = trt.DeviceType.DLA
config.DLA_core = 0
```

**Issue: INT8 accuracy degradation too high**

Solutions:
1. Use per-layer precision control for sensitive layers
2. Try different calibration algorithms
3. Use more calibration data
4. Switch to QAT instead of PTQ
5. Use FP16 instead of INT8

**Issue: Poor performance with dynamic shapes**

Solutions:
1. Check if actual shapes match optimization profile `opt` value
2. Use multiple profiles for different workload patterns
3. Narrow the min-max range if possible
4. Consider separate engines for very different shapes

**Issue: Engine build takes very long**

Solutions:
```python
# Reduce build time
config.set_flag(trt.BuilderFlag.DISABLE_TIMING_CACHE)  # If cache corrupted
config.max_workspace_size = 1 << 28  # Reduce workspace
config.set_preview_feature(trt.PreviewFeature.FASTER_DYNAMIC_SHAPES_0805, True)

# Use timing cache
config.set_timing_cache(cached_timing, ignore_mismatch=False)
```

**Issue: Accuracy differs from framework**

Debug steps:
1. Compare layer-by-layer outputs
2. Check for precision mismatches
3. Validate input preprocessing
4. Check for unsupported operations (may fallback to suboptimal)
5. Verify ONNX export correctness

### 10.3 Debugging Tools

**Polygraphy**: NVIDIA tool for debugging TensorRT

```bash
# Compare TensorRT vs ONNX Runtime
polygraphy run model.onnx \
    --trt --onnxrt \
    --atol 1e-3 --rtol 1e-3

# Debug accuracy issues layer-by-layer
polygraphy run model.onnx --trt \
    --validate \
    --save-tactics replay.json

# Reduce problematic tactics
polygraphy run model.onnx --trt \
    --load-tactics replay.json \
    --tactic-replay fallback
```

**TensorRT Logs**:
```python
# Set log level for detailed info
logger = trt.Logger(trt.Logger.VERBOSE)
builder = trt.Builder(logger)

# Logs will show:
# - Layer fusion decisions
# - Precision selection
# - Kernel selection
# - Memory allocation
```

### 10.4 Performance Checklist

Before deploying TensorRT engine:

- [ ] FP16 or INT8 enabled appropriately
- [ ] Calibration performed with representative data
- [ ] Optimization profiles match workload
- [ ] Timing cache used for consistent builds
- [ ] Engine rebuilt on target hardware
- [ ] Benchmarked under realistic load
- [ ] Accuracy validated on test set
- [ ] GPU utilization >80%
- [ ] Latency meets requirements
- [ ] Memory usage within bounds
- [ ] Edge cases tested
- [ ] Fallback mechanism in place

## Summary

This lecture covered TensorRT in depth:

- **Architecture**: Builder, Engine, Context components
- **Optimization**: Layer fusion, kernel auto-tuning, graph optimization
- **Precision**: FP16, INT8 quantization, calibration strategies
- **Dynamic Shapes**: Optimization profiles for variable inputs
- **Plugins**: Custom operations implementation
- **Advanced Features**: Timing cache, multi-stream, tactics
- **Performance**: Profiling and benchmarking
- **Best Practices**: Configuration, troubleshooting, deployment

TensorRT is the gold standard for NVIDIA GPU inference optimization. Mastering it enables:
- 2-10x speedup over framework inference
- Optimal GPU utilization
- Production-ready inference at scale

## Next Steps

1. Complete Lab 01: TensorRT Optimization (hands-on practice)
2. Read Lecture 03: ONNX Runtime for cross-platform inference
3. Experiment with different precision modes
4. Profile your own models with TensorRT

## Further Reading

- NVIDIA TensorRT Documentation: https://docs.nvidia.com/deeplearning/tensorrt/
- TensorRT Developer Guide
- "Optimizing Deep Learning Inference" by NVIDIA
- TensorRT GitHub examples
- Polygraphy documentation

---

**Lecture Duration**: 8 hours
**Hands-on Time**: 5 hours (Lab 01)
**Difficulty**: Advanced
