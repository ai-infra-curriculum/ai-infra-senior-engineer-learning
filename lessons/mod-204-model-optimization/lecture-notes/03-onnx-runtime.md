# Lecture 03: ONNX Runtime for Cross-Platform Inference

## Learning Objectives

By the end of this lecture, you will be able to:

- Design cross-platform ML inference architectures using ONNX Runtime that deploy consistently across NVIDIA, AMD, Intel GPUs, ARM CPUs, mobile, and edge devices
- Implement execution provider selection strategies with appropriate fallback chains (TensorRT→CUDA→CPU) and configure provider-specific optimizations for maximum performance
- Convert models from PyTorch and TensorFlow to ONNX format with proper dynamic axes, validate with ONNX checker, and simplify graphs using onnx-simplifier
- Configure ONNX Runtime session options including graph optimization levels, threading parameters, memory optimization, and I/O binding to eliminate CPU-GPU transfers
- Apply ONNX Runtime quantization techniques including dynamic quantization (weights only) and static quantization (weights and activations) with proper calibration
- Implement specialized optimizations for Transformer models using fusion patterns for attention, layer normalization, GELU, and embedding layers
- Profile ONNX Runtime inference with built-in profiling tools, analyze per-layer timings, and benchmark under realistic load to identify performance bottlenecks
- Deploy ONNX Runtime models across multiple platforms (cloud GPUs, mobile devices, edge hardware) with appropriate execution providers and validate production readiness

## Table of Contents
1. [Introduction to ONNX and ONNX Runtime](#introduction)
2. [ONNX Format Deep Dive](#onnx-format)
3. [ONNX Runtime Architecture](#architecture)
4. [Execution Providers](#execution-providers)
5. [Graph Optimizations](#graph-optimizations)
6. [Model Conversion and Validation](#conversion)
7. [Performance Tuning](#performance-tuning)
8. [Advanced Features](#advanced-features)
9. [Multi-Platform Deployment](#multi-platform)
10. [Best Practices](#best-practices)

<a name="introduction"></a>
## 1. Introduction to ONNX and ONNX Runtime

### What is ONNX?

**ONNX (Open Neural Network Exchange)** is an open standard format for representing machine learning models. It enables interoperability between different ML frameworks, allowing you to train in one framework and deploy in another.

**Key Benefits**:
- **Framework Agnostic**: Train in PyTorch, TensorFlow, or others; deploy anywhere
- **Platform Independent**: Run on cloud, edge, mobile, or specialized hardware
- **Optimization Ready**: Standard format enables consistent optimization
- **Production Proven**: Used by Microsoft, Meta, NVIDIA, and hundreds of companies

### What is ONNX Runtime?

**ONNX Runtime (ORT)** is a high-performance inference engine for ONNX models. It's designed to maximize performance across different hardware platforms while maintaining a consistent API.

**Key Features**:
- **Cross-platform**: Windows, Linux, macOS, iOS, Android, WebAssembly
- **Multi-hardware**: CPU, GPU (NVIDIA, AMD, Intel), NPU, TPU, custom accelerators
- **Optimizations**: Graph optimizations, kernel fusion, memory planning
- **Flexibility**: Easy integration with Python, C++, C#, Java, JavaScript
- **Production Ready**: Powers Bing, Office 365, and Azure ML

### Why ONNX Runtime?

**Use Cases**:
- Deploy same model across cloud and edge
- Support multiple hardware vendors
- Need flexibility between providers
- Want framework independence
- Require production reliability

**When to Choose ORT Over TensorRT**:
- Multi-vendor GPU support (AMD, Intel, NVIDIA)
- CPU inference requirements
- Cross-platform deployment
- Framework flexibility needed
- TensorRT plugins not available

<a name="onnx-format"></a>
## 2. ONNX Format Deep Dive

### 2.1 ONNX Model Structure

An ONNX model is a Protocol Buffer (protobuf) file containing:

```python
import onnx

# Load ONNX model
model = onnx.load("model.onnx")

# Model structure
print(f"IR Version: {model.ir_version}")
print(f"Producer: {model.producer_name}")
print(f"Opset Version: {model.opset_import[0].version}")

# Graph structure
graph = model.graph
print(f"Inputs: {[input.name for input in graph.input]}")
print(f"Outputs: {[output.name for output in graph.output]}")
print(f"Nodes: {len(graph.node)}")
```

**Components**:
- **ModelProto**: Top-level model container
- **GraphProto**: Computational graph
- **NodeProto**: Individual operations (Conv, MatMul, etc.)
- **TensorProto**: Weight tensors and constants
- **ValueInfoProto**: Tensor type information

### 2.2 ONNX Operators

ONNX defines standard operators across versions (opsets):

**Opset Evolution**:
- **Opset 7-9** (2018): Basic operators, limited ML coverage
- **Opset 10-11** (2019): Control flow (If, Loop), expanded ops
- **Opset 12-13** (2020): Einsum, SequenceMap, improved quantization
- **Opset 14-15** (2021-2022): Transformer ops, training support
- **Opset 16-18** (2023-2024): Advanced quantization, custom ops

**Common Operators**:
```python
# Convolution
Conv(input, weight, bias,
     kernel_shape, strides, pads, dilations, group)

# Matrix Multiplication
MatMul(A, B)
Gemm(A, B, C, alpha, beta, transA, transB)  # alpha*A*B + beta*C

# Attention (Opset 14+)
Attention(input, weight, bias,
          num_heads, qkv_hidden_sizes)

# Layer Normalization
LayerNormalization(input, scale, bias, axis, epsilon)

# Activation Functions
Relu(input)
Gelu(input)
Silu(input)  # Swish
```

### 2.3 ONNX Type System

ONNX supports rich type information:

```python
# Tensor types
elem_type = onnx.TensorProto.FLOAT     # FP32
elem_type = onnx.TensorProto.FLOAT16   # FP16
elem_type = onnx.TensorProto.INT8      # INT8
elem_type = onnx.TensorProto.INT64     # INT64

# Shape specification
shape = [1, 3, 224, 224]  # Static shape
shape = [-1, 3, 224, 224]  # Dynamic batch dimension

# Advanced types (Opset 11+)
# Sequences, Maps, Optional types supported
```

### 2.4 Metadata and Model Documentation

ONNX models can embed metadata:

```python
# Add metadata to model
model.doc_string = "ResNet50 v1.5 trained on ImageNet"
model.model_version = 1

# Add custom metadata
metadata = model.metadata_props.add()
metadata.key = "author"
metadata.value = "AI Infrastructure Team"

metadata = model.metadata_props.add()
metadata.key = "accuracy"
metadata.value = "76.1% top-1"

# Save with metadata
onnx.save(model, "model_with_metadata.onnx")
```

<a name="architecture"></a>
## 3. ONNX Runtime Architecture

### 3.1 Core Components

```
┌─────────────────────────────────────────────┐
│           ONNX Runtime API                   │
│  (Python, C++, C#, Java, JavaScript)        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Session Management                   │
│  - Model loading and validation              │
│  - Graph optimization                        │
│  - Memory planning                           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Graph Transformers                      │
│  - Constant folding                          │
│  - Operator fusion                           │
│  - Layout optimization                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Execution Providers                     │
│  CPU │ CUDA │ TensorRT │ DML │ CoreML │ ...│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Hardware                            │
│  CPU │ NVIDIA GPU │ AMD GPU │ NPU │ TPU    │
└─────────────────────────────────────────────┘
```

### 3.2 Session Creation and Configuration

```python
import onnxruntime as ort
import numpy as np

# Create inference session
session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

# Inspect model inputs
inputs = session.get_inputs()
for inp in inputs:
    print(f"Input: {inp.name}")
    print(f"  Shape: {inp.shape}")
    print(f"  Type: {inp.type}")

# Inspect outputs
outputs = session.get_outputs()
for out in outputs:
    print(f"Output: {out.name}")
    print(f"  Shape: {out.shape}")
    print(f"  Type: {out.type}")
```

### 3.3 Session Options

```python
# Advanced session configuration
sess_options = ort.SessionOptions()

# Graph optimization level
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Intra-op parallelism (within operations)
sess_options.intra_op_num_threads = 8

# Inter-op parallelism (between operations)
sess_options.inter_op_num_threads = 2

# Enable profiling
sess_options.enable_profiling = True

# Memory optimization
sess_options.enable_mem_pattern = True
sess_options.enable_mem_reuse = True

# Execution mode
sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
# or ORT_PARALLEL for parallel execution

# Create session with options
session = ort.InferenceSession(
    "model.onnx",
    sess_options=sess_options,
    providers=['CUDAExecutionProvider']
)
```

<a name="execution-providers"></a>
## 4. Execution Providers

Execution Providers (EPs) are ONNX Runtime's abstraction for hardware acceleration.

### 4.1 Available Execution Providers

**CPU Providers**:
- **CPUExecutionProvider**: Default, optimized CPU kernels
- **DnnlExecutionProvider**: Intel oneDNN (MKL-DNN) acceleration
- **OpenVINOExecutionProvider**: Intel OpenVINO toolkit
- **ACLExecutionProvider**: ARM Compute Library (ARM CPUs)

**GPU Providers**:
- **CUDAExecutionProvider**: NVIDIA CUDA acceleration
- **TensorrtExecutionProvider**: NVIDIA TensorRT optimization
- **ROCMExecutionProvider**: AMD ROCm acceleration
- **DmlExecutionProvider**: DirectML (Windows, any GPU)
- **MIGraphXExecutionProvider**: AMD MIGraphX

**Mobile/Edge Providers**:
- **CoreMLExecutionProvider**: Apple Neural Engine (iOS/macOS)
- **NNAPIExecutionProvider**: Android Neural Networks API
- **QNNExecutionProvider**: Qualcomm AI Engine

**Cloud Providers**:
- **VitisAIExecutionProvider**: Xilinx/AMD FPGAs
- **RknpuExecutionProvider**: Rockchip NPU

### 4.2 CUDA Execution Provider

Basic NVIDIA GPU acceleration:

```python
# Enable CUDA provider
providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

# Advanced CUDA configuration
cuda_provider_options = {
    'device_id': 0,                          # GPU device ID
    'arena_extend_strategy': 'kSameAsRequested',  # Memory allocation
    'gpu_mem_limit': 2 * 1024 * 1024 * 1024, # 2GB limit
    'cudnn_conv_algo_search': 'EXHAUSTIVE',  # Conv algorithm search
    'do_copy_in_default_stream': True,       # Sync behavior
}

session = ort.InferenceSession(
    "model.onnx",
    providers=[
        ('CUDAExecutionProvider', cuda_provider_options),
        'CPUExecutionProvider'
    ]
)
```

**CUDA Provider Features**:
- Automatic cuDNN kernel selection
- Memory pool management
- Stream-based execution
- Multi-GPU support

### 4.3 TensorRT Execution Provider

Combines ONNX Runtime with TensorRT optimization:

```python
# TensorRT provider options
trt_provider_options = {
    'device_id': 0,
    'trt_max_workspace_size': 4 * 1024 * 1024 * 1024,  # 4GB
    'trt_fp16_enable': True,                # Enable FP16
    'trt_int8_enable': False,               # Enable INT8
    'trt_int8_calibration_table_name': '',  # Calibration cache
    'trt_engine_cache_enable': True,        # Cache TRT engines
    'trt_engine_cache_path': './trt_cache', # Cache directory
    'trt_force_sequential_engine_build': False,
}

session = ort.InferenceSession(
    "model.onnx",
    providers=[
        ('TensorrtExecutionProvider', trt_provider_options),
        'CUDAExecutionProvider',
        'CPUExecutionProvider'
    ]
)
```

**TensorRT Provider Benefits**:
- Automatic TensorRT optimization
- Transparent fallback to CUDA for unsupported ops
- Engine caching for faster startup
- Easier than native TensorRT API

**When to Use**:
- Want TensorRT performance with ONNX Runtime API
- Need automatic fallback for unsupported ops
- Deploying on NVIDIA GPUs
- Don't want to manage TensorRT directly

### 4.4 Provider Fallback Mechanism

ONNX Runtime uses a fallback chain:

```python
# Provider priority order (first to last)
providers = [
    'TensorrtExecutionProvider',  # Try TensorRT first
    'CUDAExecutionProvider',      # Fall back to CUDA
    'CPUExecutionProvider'        # Final fallback to CPU
]

# ORT will:
# 1. Assign ops to TensorRT where possible
# 2. Fall back to CUDA for unsupported TensorRT ops
# 3. Fall back to CPU for unsupported CUDA ops

session = ort.InferenceSession("model.onnx", providers=providers)

# Check which provider is used for each node
meta = session.get_provider_options()
print(meta)
```

### 4.5 Custom Execution Provider

For specialized hardware, you can implement custom EPs:

```cpp
// Custom EP implementation (C++)
class MyCustomExecutionProvider : public IExecutionProvider {
public:
    MyCustomExecutionProvider(const MyCustomExecutionProviderInfo& info)
        : IExecutionProvider(kMyCustomExecutionProvider) {
        // Initialize custom hardware
    }

    std::vector<std::unique_ptr<ComputeCapability>>
    GetCapability(const GraphViewer& graph_viewer,
                  const IKernelLookup& kernel_lookup) const override {
        // Determine which nodes this EP can handle
    }

    Status Compile(const std::vector<FusedNodeAndGraph>& fused_nodes_and_graphs,
                   std::vector<NodeComputeInfo>& node_compute_funcs) override {
        // Compile subgraphs for custom hardware
    }
};
```

<a name="graph-optimizations"></a>
## 5. Graph Optimizations

ONNX Runtime performs multiple levels of graph optimization:

### 5.1 Optimization Levels

```python
import onnxruntime as ort

# Level 0: Disabled
# - No optimizations
# - Useful for debugging

# Level 1: Basic
# - Constant folding
# - Redundant node elimination
# - Semantics-preserving node fusion

# Level 2: Extended (Default)
# - All Level 1 optimizations
# - More aggressive fusion
# - Complex pattern matching

# Level 99: All
# - All available optimizations
# - Layout transformations
# - Experimental optimizations

sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
```

### 5.2 Common Graph Transformations

**Constant Folding**:
```python
# Before optimization
# x = input
# y = Const(2)
# z = Const(3)
# result = x * (y + z)  # (y + z) computed at runtime

# After optimization
# x = input
# precomputed = Const(5)  # 2 + 3 computed at build time
# result = x * precomputed
```

**Dead Code Elimination**:
```python
# Before
x = input
y = Conv(x, w1)
z = Conv(x, w2)  # Not used in output
output = Relu(y)

# After
x = input
y = Conv(x, w1)
output = Relu(y)  # z and Conv(x, w2) removed
```

**Operator Fusion**:
```python
# Before: Conv -> BatchNorm -> Relu (3 ops)
x = Conv(input, weight, bias)
x = BatchNormalization(x, scale, B, mean, var)
output = Relu(x)

# After: Fused ConvBatchNormRelu (1 op)
output = FusedConvBatchNormRelu(input, fused_weight, fused_bias)

# Benefit: 3x fewer kernel launches, better memory locality
```

**Reshape Elimination**:
```python
# Before
x = Reshape(input, [batch, -1])
y = Reshape(x, original_shape)  # Inverse reshape
output = Add(y, something)

# After
output = Add(input, something)  # Reshapes eliminated
```

### 5.3 Layout Optimization

ONNX Runtime can optimize memory layouts:

```python
# NCHW (Channels-first) vs NHWC (Channels-last)

# PyTorch/ONNX default: NCHW [batch, channels, height, width]
# TensorFlow default: NHWC [batch, height, width, channels]
# Tensor Cores prefer: NHWC for convolutions

# ORT can automatically insert layout transposes
# Or optimize entire model to preferred layout

sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Layout optimization happens automatically
# Based on execution provider preferences
```

### 5.4 Quantization in ONNX Runtime

ONNX Runtime supports quantization as a graph transformation:

```python
from onnxruntime.quantization import quantize_dynamic, quantize_static

# Dynamic Quantization (weights only, activations FP32)
quantize_dynamic(
    model_input="model.onnx",
    model_output="model_quant_dynamic.onnx",
    weight_type=ort.QuantType.QInt8  # or QUInt8
)

# Static Quantization (weights and activations INT8)
from onnxruntime.quantization import CalibrationDataReader

class DataReader(CalibrationDataReader):
    def __init__(self, calibration_data):
        self.data = calibration_data
        self.iterator = iter(calibration_data)

    def get_next(self):
        try:
            return next(self.iterator)
        except StopIteration:
            return None

quantize_static(
    model_input="model.onnx",
    model_output="model_quant_static.onnx",
    calibration_data_reader=DataReader(calibration_data),
    quant_format=ort.QuantFormat.QDQ,  # QuantizeLinear/DequantizeLinear
    activation_type=ort.QuantType.QInt8,
    weight_type=ort.QuantType.QInt8
)
```

<a name="conversion"></a>
## 6. Model Conversion and Validation

### 6.1 PyTorch to ONNX

```python
import torch
import torch.onnx

# PyTorch model
model = torch.load("pytorch_model.pth")
model.eval()

# Dummy input for tracing
dummy_input = torch.randn(1, 3, 224, 224)

# Export to ONNX
torch.onnx.export(
    model,                          # PyTorch model
    dummy_input,                    # Example input
    "model.onnx",                   # Output file
    export_params=True,             # Include weights
    opset_version=18,               # ONNX opset version
    do_constant_folding=True,       # Optimize constants
    input_names=['input'],          # Input names
    output_names=['output'],        # Output names
    dynamic_axes={                  # Dynamic dimensions
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

# Verify ONNX model
import onnx
onnx_model = onnx.load("model.onnx")
onnx.checker.check_model(onnx_model)
```

### 6.2 TensorFlow to ONNX

```python
import tf2onnx
import tensorflow as tf

# TensorFlow model
model = tf.keras.models.load_model("tf_model.h5")

# Convert to ONNX
spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)

model_proto, external_tensor_storage = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=18,
    output_path="model.onnx"
)
```

### 6.3 ONNX Model Validation

```python
import onnx
from onnx import checker, shape_inference, optimizer

# Load model
model = onnx.load("model.onnx")

# Check model validity
checker.check_model(model)
print("✓ Model is valid")

# Infer shapes
inferred_model = shape_inference.infer_shapes(model)
onnx.save(inferred_model, "model_with_shapes.onnx")

# Optimize model (ONNX level, before ORT)
optimized_model = optimizer.optimize(model)
onnx.save(optimized_model, "model_optimized.onnx")
```

### 6.4 ONNX Simplifier

Simplify ONNX graphs for better performance:

```python
import onnx
from onnxsim import simplify

# Load model
model = onnx.load("model.onnx")

# Simplify
model_simp, check = simplify(model)

if check:
    print("✓ Simplified model validated")
    onnx.save(model_simp, "model_simplified.onnx")
else:
    print("✗ Simplification failed validation")
```

**What ONNX Simplifier Does**:
- Constant folding
- Remove redundant operators
- Optimize reshape chains
- Eliminate dead code
- Simplify control flow

<a name="performance-tuning"></a>
## 7. Performance Tuning

### 7.1 Threading Configuration

```python
import onnxruntime as ort
import multiprocessing

# Determine optimal thread counts
num_cores = multiprocessing.cpu_count()

sess_options = ort.SessionOptions()

# Intra-op threads (parallel execution within operators)
# Good for: Large matrix operations
# Typical: num_physical_cores (not hyperthreading)
sess_options.intra_op_num_threads = num_cores // 2

# Inter-op threads (parallel execution of independent operators)
# Good for: Models with parallel branches
# Typical: 1-2 for most models
sess_options.inter_op_num_threads = 2

# Execution mode
# SEQUENTIAL: Lower memory, simpler debugging
# PARALLEL: Better throughput for models with parallelism
sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

session = ort.InferenceSession("model.onnx", sess_options=sess_options)
```

### 7.2 Memory Optimization

```python
sess_options = ort.SessionOptions()

# Enable memory pattern optimization
sess_options.enable_mem_pattern = True

# Enable memory reuse
sess_options.enable_mem_reuse = True

# For models with limited memory:
sess_options.enable_cpu_mem_arena = False  # Disable memory arena
```

### 7.3 I/O Binding for GPU

Eliminate CPU-GPU memory copies:

```python
import onnxruntime as ort
import numpy as np

session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider']
)

# Create IOBinding
io_binding = session.io_binding()

# Bind input to GPU memory
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
input_tensor = ort.OrtValue.ortvalue_from_numpy(input_data, 'cuda', 0)

io_binding.bind_input(
    name='input',
    device_type='cuda',
    device_id=0,
    element_type=np.float32,
    shape=input_tensor.shape(),
    buffer_ptr=input_tensor.data_ptr()
)

# Bind output to GPU memory
output_shape = [1, 1000]
output_tensor = ort.OrtValue.ortvalue_from_shape_and_type(
    output_shape, np.float32, 'cuda', 0
)

io_binding.bind_output(
    name='output',
    device_type='cuda',
    device_id=0,
    element_type=np.float32,
    shape=output_shape,
    buffer_ptr=output_tensor.data_ptr()
)

# Run inference (no CPU-GPU copies!)
session.run_with_iobinding(io_binding)

# Get results
outputs = io_binding.copy_outputs_to_cpu()
```

### 7.4 Profiling and Benchmarking

```python
import onnxruntime as ort
import time
import numpy as np

# Enable profiling
sess_options = ort.SessionOptions()
sess_options.enable_profiling = True

session = ort.InferenceSession(
    "model.onnx",
    sess_options=sess_options,
    providers=['CUDAExecutionProvider']
)

# Warmup
input_data = {'input': np.random.randn(1, 3, 224, 224).astype(np.float32)}
for _ in range(10):
    session.run(None, input_data)

# Benchmark
num_iterations = 1000
start = time.perf_counter()

for _ in range(num_iterations):
    outputs = session.run(None, input_data)

end = time.perf_counter()

avg_time_ms = (end - start) / num_iterations * 1000
throughput_qps = 1000 / avg_time_ms

print(f"Average latency: {avg_time_ms:.2f} ms")
print(f"Throughput: {throughput_qps:.2f} QPS")

# Get profiling results
prof_file = session.end_profiling()
print(f"Profiling data saved to: {prof_file}")

# Analyze profiling data (JSON format)
import json
with open(prof_file, 'r') as f:
    prof_data = json.load(f)

# Sort by duration
events = sorted(prof_data, key=lambda x: x['dur'], reverse=True)
for event in events[:10]:
    print(f"{event['name']}: {event['dur']} us")
```

<a name="advanced-features"></a>
## 8. Advanced Features

### 8.1 Model Optimization

Save optimized graph for faster loading:

```python
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Save optimized model
sess_options.optimized_model_filepath = "model_optimized.onnx"

session = ort.InferenceSession(
    "model.onnx",
    sess_options=sess_options
)

# Next time, load optimized model directly
session_fast = ort.InferenceSession("model_optimized.onnx")
```

### 8.2 Custom Operators

Register custom operators:

```python
from onnxruntime import InferenceSession, SessionOptions

# Custom op library (C++ implementation)
sess_options = SessionOptions()
sess_options.register_custom_ops_library("libcustom_ops.so")

session = InferenceSession("model_with_custom_ops.onnx", sess_options)
```

### 8.3 Transformer Optimization

Specialized optimizations for Transformer models:

```python
from onnxruntime.transformers import optimizer

# Optimize BERT/GPT/T5 models
optimized_model = optimizer.optimize_model(
    "bert_model.onnx",
    model_type='bert',           # or 'gpt2', 't5'
    num_heads=12,
    hidden_size=768,
    optimization_options={
        'enable_attention_fusion': True,
        'enable_layer_norm_fusion': True,
        'enable_gelu_fusion': True,
        'enable_skip_layer_norm': True,
        'enable_embed_layer_norm': True,
    }
)

optimized_model.save_model_to_file("bert_optimized.onnx")
```

### 8.4 Training Support

ONNX Runtime supports training (not just inference):

```python
import onnxruntime.training as ort_training

# Load training model
session = ort_training.TrainingSession(
    "training_model.onnx",
    "eval_model.onnx",
    "optimizer_model.onnx"
)

# Training loop
for epoch in range(num_epochs):
    for batch in dataloader:
        loss = session.train_step(batch)

        if step % eval_interval == 0:
            eval_loss = session.eval_step(eval_batch)
```

<a name="multi-platform"></a>
## 9. Multi-Platform Deployment

### 9.1 CPU Optimization (Intel)

```python
# Use oneDNN (DNNL) for Intel CPUs
providers = [
    ('DnnlExecutionProvider', {
        'use_arena': True
    }),
    'CPUExecutionProvider'
]

session = ort.InferenceSession("model.onnx", providers=providers)
```

### 9.2 Mobile Deployment

**iOS with CoreML**:
```python
# Convert ONNX to CoreML
from onnxruntime_extensions import get_coreml_providers

providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
session = ort.InferenceSession("model.onnx", providers=providers)
```

**Android with NNAPI**:
```python
providers = ['NNAPIExecutionProvider', 'CPUExecutionProvider']
session = ort.InferenceSession("model.onnx", providers=providers)
```

### 9.3 AMD GPU

```python
# ROCm for AMD GPUs
providers = [
    ('ROCMExecutionProvider', {
        'device_id': 0,
    }),
    'CPUExecutionProvider'
]

session = ort.InferenceSession("model.onnx", providers=providers)
```

<a name="best-practices"></a>
## 10. Best Practices

### 10.1 Model Preparation Checklist

- [ ] Export with latest opset (17-18)
- [ ] Use dynamic axes for variable dimensions
- [ ] Run ONNX checker
- [ ] Simplify with onnx-simplifier
- [ ] Infer and save shapes
- [ ] Test with sample inputs

### 10.2 Performance Optimization Checklist

- [ ] Choose appropriate execution provider
- [ ] Enable graph optimization (Level 2 or All)
- [ ] Configure threading for hardware
- [ ] Use I/O binding for GPU to avoid copies
- [ ] Profile to identify bottlenecks
- [ ] Consider quantization for INT8
- [ ] Cache optimized model

### 10.3 Production Deployment Checklist

- [ ] Version ONNX Runtime library
- [ ] Test on target hardware
- [ ] Implement fallback providers
- [ ] Monitor inference metrics
- [ ] Handle exceptions gracefully
- [ ] Load test under realistic conditions
- [ ] Document provider requirements
- [ ] Plan for model updates

## Summary

This lecture covered ONNX Runtime comprehensively:

- **ONNX Format**: Standard model representation
- **Architecture**: Session management and execution
- **Execution Providers**: Hardware acceleration abstraction
- **Graph Optimizations**: Automatic model optimization
- **Conversion**: PyTorch/TensorFlow to ONNX
- **Performance Tuning**: Threading, memory, I/O binding
- **Advanced Features**: Custom ops, quantization, training
- **Multi-platform**: CPU, GPU, mobile deployment

ONNX Runtime provides:
- Framework independence
- Hardware flexibility
- Production reliability
- Cross-platform consistency

## Next Steps

1. Complete Lab 02: Quantization with ONNX Runtime
2. Read Lecture 04: Quantization Techniques
3. Experiment with different execution providers
4. Profile your models with ORT

## Further Reading

- ONNX Runtime Documentation: https://onnxruntime.ai/
- ONNX Specification: https://onnx.ai/
- Execution Providers Guide
- Performance Tuning Guide
- Model Zoo: https://github.com/onnx/models

---

**Lecture Duration**: 6 hours
**Difficulty**: Intermediate to Advanced
