# Lecture 04: Quantization Techniques

## Learning Objectives

By the end of this lecture, you will be able to:

- Design quantization strategies selecting appropriate techniques (PTQ vs QAT, symmetric vs asymmetric, per-tensor vs per-channel) based on accuracy and latency requirements
- Implement INT8 post-training quantization using multiple calibration methods (entropy, percentile, minmax) with 500-1000 representative samples achieving <2% accuracy degradation
- Architect quantization-aware training pipelines with fake quantization, straight-through estimators, and proper training schedules (fine-tune, freeze BN, freeze ranges)
- Apply advanced quantization formats including FP16/BF16 mixed precision, FP8 for Hopper GPUs, and INT4 using GPTQ/AWQ for LLM weight compression
- Implement accuracy preservation techniques including per-channel weight quantization, cross-layer equalization, bias correction, and outlier channel handling
- Configure quantization across multiple frameworks (PyTorch native, TensorRT, ONNX Runtime) with appropriate settings for static, dynamic, and QAT workflows
- Evaluate quantization trade-offs analyzing memory reduction (2x for FP16, 4x for INT8, 8x for INT4), compute speedup, and accuracy impact per layer
- Deploy quantized models to production with comprehensive validation (accuracy comparison, output similarity, numerical stability), A/B testing, and continuous monitoring

## Table of Contents
1. [Introduction to Quantization](#introduction)
2. [Quantization Fundamentals](#fundamentals)
3. [Post-Training Quantization (PTQ)](#ptq)
4. [Quantization-Aware Training (QAT)](#qat)
5. [INT8 Quantization](#int8)
6. [FP16 and Mixed Precision](#fp16)
7. [Advanced Quantization: FP8 and INT4](#advanced)
8. [Accuracy Preservation Strategies](#accuracy)
9. [Quantization Frameworks and Tools](#frameworks)
10. [Production Deployment](#production)

<a name="introduction"></a>
## 1. Introduction to Quantization

### What is Quantization?

**Quantization** is the process of mapping continuous or high-precision values to discrete lower-precision values. In deep learning, this typically means converting 32-bit floating-point weights and activations to 8-bit integers or 16-bit floats.

### Why Quantize?

**Memory Reduction**:
- FP32 → FP16: 2x smaller models
- FP32 → INT8: 4x smaller models
- FP32 → INT4: 8x smaller models

**Compute Speedup**:
- INT8 Tensor Cores: 2-4x faster than FP16
- Lower precision = more operations per second
- Reduced memory bandwidth requirements

**Energy Efficiency**:
- INT8 operations consume ~30% energy of FP32
- Critical for edge deployment
- Extends battery life on mobile devices

**Cost Savings**:
- Smaller models → less GPU memory → cheaper hardware
- Faster inference → fewer GPU hours
- LLM serving: INT8 can reduce costs by 50%+

### The Quantization Challenge

The fundamental challenge: **maintain accuracy while reducing precision**.

**Typical Accuracy Impact**:
- FP16: <0.1% degradation (usually negligible)
- INT8 (PTQ): 0.5-2% degradation
- INT8 (QAT): 0-0.5% degradation
- INT4: 1-5% degradation (model dependent)

<a name="fundamentals"></a>
## 2. Quantization Fundamentals

### 2.1 Mathematical Foundation

**Symmetric Quantization**:
```python
# Map floating-point values to integers symmetrically

scale = max(abs(tensor)) / (2^(bits-1) - 1)

# For INT8: range is [-127, 127]
scale = max(abs(tensor)) / 127.0

# Quantization
quantized = round(tensor / scale).clamp(-127, 127)

# Dequantization
dequantized = quantized * scale

# Example:
# tensor = [0.5, -0.8, 1.2, -1.5]
# max(abs(tensor)) = 1.5
# scale = 1.5 / 127 = 0.0118
# quantized = round([42.4, -67.8, 101.7, -127.1])
#           = [42, -68, 102, -127]
```

**Asymmetric Quantization**:
```python
# Map to full range including zero offset

# For INT8: range is [0, 255] or [-128, 127]
min_val = tensor.min()
max_val = tensor.max()

scale = (max_val - min_val) / 255.0
zero_point = round(-min_val / scale)

# Quantization
quantized = round(tensor / scale + zero_point).clamp(0, 255)

# Dequantization
dequantized = (quantized - zero_point) * scale
```

**When to Use Each**:
- **Symmetric**: Weights, symmetric activations (ReLU output)
- **Asymmetric**: Activations with skewed distributions

### 2.2 Quantization Granularity

**Per-Tensor Quantization**:
```python
# Single scale/zero-point for entire tensor
# Example: weight tensor [out_channels, in_channels, k, k]

scale = compute_scale(weight)  # Single value
quantized_weight = quantize(weight, scale)

# Pros: Simple, fast
# Cons: Less accurate for heterogeneous distributions
```

**Per-Channel Quantization**:
```python
# Different scale per output channel
# For convolution: separate scale per filter

for out_ch in range(out_channels):
    scale[out_ch] = compute_scale(weight[out_ch])
    quantized_weight[out_ch] = quantize(weight[out_ch], scale[out_ch])

# Pros: Much better accuracy
# Cons: Slightly more complex
# Usage: Standard for weight quantization
```

**Per-Group Quantization** (for LLMs):
```python
# Divide weights into groups, quantize each group
# Commonly used for INT4 quantization

group_size = 128  # Typical value

for group in weight.split(group_size):
    scale = compute_scale(group)
    quantized_group = quantize(group, scale)

# Pros: Balance between accuracy and complexity
# Cons: More scales to manage
```

### 2.3 Calibration Methods

**MinMax Calibration**:
```python
# Use actual min/max from data
def calibrate_minmax(activations):
    return activations.min(), activations.max()

# Simple but sensitive to outliers
```

**Moving Average**:
```python
# Track min/max with exponential moving average
def calibrate_ema(activations, prev_min, prev_max, momentum=0.01):
    cur_min = activations.min()
    cur_max = activations.max()

    new_min = momentum * cur_min + (1 - momentum) * prev_min
    new_max = momentum * cur_max + (1 - momentum) * prev_max

    return new_min, new_max

# More robust to outliers
```

**Percentile Calibration**:
```python
# Use percentiles instead of absolute min/max
def calibrate_percentile(activations, percentile=99.99):
    abs_max = torch.quantile(torch.abs(activations), percentile / 100)
    return -abs_max, abs_max

# Very robust to outliers
# Used in TensorRT
```

**Entropy Calibration** (KL Divergence):
```python
# Minimize information loss (KL divergence)
def calibrate_entropy(activations, num_bins=2048):
    # Create histogram of activations
    hist, bin_edges = np.histogram(activations, bins=num_bins)

    # Search for threshold that minimizes KL divergence
    best_threshold = None
    best_kl_div = float('inf')

    for threshold in candidate_thresholds:
        # Quantize with this threshold
        quantized = quantize_with_threshold(activations, threshold)

        # Compute KL divergence
        kl_div = compute_kl_divergence(activations, quantized)

        if kl_div < best_kl_div:
            best_kl_div = kl_div
            best_threshold = threshold

    return best_threshold

# Most accurate but expensive
# Used in TensorRT (default)
```

<a name="ptq"></a>
## 3. Post-Training Quantization (PTQ)

PTQ quantizes a pre-trained model without retraining.

### 3.1 Static PTQ Workflow

```python
import torch
from torch.quantization import quantize_dynamic, quantize_static

# 1. Load pre-trained model
model = load_pretrained_model()
model.eval()

# 2. Fuse operations (Conv + BN + ReLU)
from torch.quantization import fuse_modules
model = fuse_modules(model, [['conv', 'bn', 'relu']])

# 3. Specify quantization configuration
model.qconfig = torch.quantization.get_default_qconfig('fbgemm')  # for x86
# or 'qnnpack' for ARM

# 4. Prepare model for calibration
torch.quantization.prepare(model, inplace=True)

# 5. Calibration: run representative data through model
with torch.no_grad():
    for data, _ in calibration_loader:
        model(data)

# 6. Convert to quantized model
torch.quantization.convert(model, inplace=True)

# 7. Validate accuracy
accuracy = evaluate(model, test_loader)
print(f"Quantized model accuracy: {accuracy:.2f}%")
```

### 3.2 Dynamic PTQ

Quantizes weights statically but activations dynamically:

```python
# Dynamic quantization (simpler, for LSTM/Transformer)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.LSTM},  # Layers to quantize
    dtype=torch.qint8
)

# Advantages:
# - No calibration needed
# - Good for models where activations vary widely

# Disadvantages:
# - Slower than static quantization
# - Still converts activations at runtime
```

### 3.3 PTQ with TensorRT

```python
import tensorrt as trt

# Create calibrator for PTQ
class Int8Calibrator(trt.IInt8EntropyCalibrator2):
    def __init__(self, calibration_data, cache_file):
        super().__init__()
        self.data = calibration_data
        self.cache_file = cache_file
        self.batch_size = 32

    def get_batch_size(self):
        return self.batch_size

    def get_batch(self, names):
        if self.current_index >= len(self.data):
            return None
        batch = self.data[self.current_index]
        self.current_index += 1
        return [batch.data_ptr()]

    def read_calibration_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return f.read()
        return None

    def write_calibration_cache(self, cache):
        with open(self.cache_file, 'wb') as f:
            f.write(cache)

# Build INT8 engine
config.set_flag(trt.BuilderFlag.INT8)
config.int8_calibrator = Int8Calibrator(calibration_data, 'calibration.cache')

engine = builder.build_serialized_network(network, config)
```

### 3.4 PTQ Best Practices

**Calibration Data Selection**:
```python
# Use 500-1000 representative samples
# Should cover data distribution

# Good: Random samples from training/validation set
calibration_data = random.sample(training_data, 1000)

# Better: Stratified sampling to ensure coverage
calibration_data = stratified_sample(training_data, 1000)

# Best: Difficult examples that stress the model
calibration_data = select_hard_examples(training_data, 1000)
```

**Layer-wise Sensitivity Analysis**:
```python
def analyze_layer_sensitivity(model, test_loader):
    """
    Identify which layers are sensitive to quantization
    """
    sensitivities = {}

    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            # Quantize only this layer
            quantized_model = quantize_single_layer(model, name)

            # Measure accuracy drop
            accuracy = evaluate(quantized_model, test_loader)
            accuracy_drop = baseline_accuracy - accuracy

            sensitivities[name] = accuracy_drop

    # Keep sensitive layers in FP32
    sensitive_layers = [k for k, v in sensitivities.items() if v > 0.5]

    return sensitive_layers
```

<a name="qat"></a>
## 4. Quantization-Aware Training (QAT)

QAT simulates quantization during training to learn robust quantized parameters.

### 4.1 QAT Workflow

```python
import torch
from torch.quantization import prepare_qat, convert

# 1. Load model
model = YourModel()

# 2. Fuse modules
model = fuse_modules(model, [['conv', 'bn', 'relu']])

# 3. Configure quantization
model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')

# 4. Prepare for QAT
model = prepare_qat(model, inplace=True)

# 5. Train with fake quantization
model.train()
optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

for epoch in range(num_epochs):
    for data, target in train_loader:
        optimizer.zero_grad()
        output = model(data)  # Simulates quantization
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

    # Adjust quantization ranges
    if epoch > 3:  # Freeze BN statistics after a few epochs
        model.apply(torch.quantization.disable_observer)
    if epoch > 2:  # Freeze quantization ranges
        model.apply(torch.quantization.disable_fake_quant)

# 6. Convert to actual quantized model
model.eval()
quantized_model = convert(model, inplace=True)

# 7. Validate
accuracy = evaluate(quantized_model, test_loader)
```

### 4.2 Fake Quantization

QAT uses "fake quantization" to simulate INT8 during training:

```python
class FakeQuantize(nn.Module):
    """
    Simulates quantization: x -> Q(x) -> DQ(Q(x))
    """
    def forward(self, x):
        # Compute scale and zero_point
        scale, zero_point = self.calculate_qparams(x)

        # Quantize
        x_int = torch.round(x / scale + zero_point).clamp(0, 255)

        # Immediately dequantize
        x_fake_quant = (x_int - zero_point) * scale

        # Backward pass sees quantization effect
        return x_fake_quant
```

This allows gradients to flow while the model learns to be robust to quantization.

### 4.3 QAT Advanced Techniques

**Learning Quantization Parameters**:
```python
class LearnableQuantization(nn.Module):
    def __init__(self):
        super().__init__()
        # Make scale and zero_point learnable
        self.scale = nn.Parameter(torch.tensor(1.0))
        self.zero_point = nn.Parameter(torch.tensor(0.0))

    def forward(self, x):
        x_int = torch.round(x / self.scale + self.zero_point).clamp(0, 255)
        return (x_int - self.zero_point) * self.scale

# During training, scale and zero_point are optimized
```

**Straight-Through Estimator (STE)**:
```python
class StraightThroughRound(torch.autograd.Function):
    """
    Round in forward pass, but pass gradient unchanged
    """
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)

    @staticmethod
    def backward(ctx, grad_output):
        # Straight-through: gradient passes unchanged
        return grad_output

# Used in quantization to allow gradients through rounding
```

### 4.4 QAT Best Practices

**Training Schedule**:
```python
# Recommended QAT training schedule

# Phase 1: Fine-tune with fake quantization (3-5 epochs)
model.train()
# Use small learning rate (1/10 of original)
lr = base_lr / 10

# Phase 2: Freeze BatchNorm statistics (2-3 epochs)
model.apply(torch.nn.intrinsic.qat.freeze_bn_stats)

# Phase 3: Freeze quantization ranges (1-2 epochs)
model.apply(torch.quantization.disable_observer)

# Phase 4: Convert and validate
model.eval()
quantized_model = convert(model)
```

<a name="int8"></a>
## 5. INT8 Quantization

### 5.1 INT8 Arithmetic

**INT8 Matrix Multiplication**:
```python
# Standard FP32 MatMul
C_fp32 = A_fp32 @ B_fp32

# INT8 quantized MatMul
# Weights (B) quantized per-channel
# Activations (A) quantized per-tensor

A_int8 = quantize(A_fp32, scale_A)  # scale_A is scalar
B_int8 = quantize(B_fp32, scale_B)  # scale_B is vector [out_channels]

# Integer matrix multiply
C_int32 = A_int8 @ B_int8  # Result is INT32 (accumulation)

# Requantize to INT8
C_int8 = requantize(C_int32, scale_A, scale_B, scale_C)

# Mathematically:
# C_int8 = round((A_int8 @ B_int8) * (scale_A * scale_B) / scale_C)
```

**Fused Operations**:
```python
# Conv + BatchNorm + ReLU fused in INT8

# Convolution in INT8
conv_out_int32 = conv_int8(input_int8, weight_int8)

# Fuse BatchNorm parameters into requantization
# BN: y = gamma * (x - mean) / sqrt(var + eps) + beta
# Fold into scale and bias

fused_scale = (scale_in * scale_weight) / scale_out * gamma / sqrt(var + eps)
fused_bias = beta - mean * gamma / sqrt(var + eps)

# Apply fused BN + ReLU during requantization
output_int8 = requantize_with_bn_relu(
    conv_out_int32,
    fused_scale,
    fused_bias,
    scale_out,
    zero_point_out
)
```

### 5.2 INT8 Performance

**Theoretical Speedup**:
- Tensor Core FP16: 312 TFLOPS (A100)
- Tensor Core INT8: 624 TOPS (A100)
- Speedup: 2x compute throughput

**Actual Speedup** (varies by model):
- Small models (ResNet-18): 1.5-2x
- Medium models (ResNet-50): 2-3x
- Large models (BERT-Large): 2.5-4x
- Memory-bound models: Up to 4x (bandwidth reduction)

**Bottlenecks**:
- Requantization overhead
- CPU-GPU transfer (if not optimized)
- Non-quantized operations (softmax, layer norm)

### 5.3 INT8 Accuracy Preservation

**Techniques**:

1. **Per-Channel Weight Quantization**
```python
# Much better than per-tensor for weights
for out_ch in range(out_channels):
    scale_w[out_ch] = max(abs(weight[out_ch])) / 127
    weight_q[out_ch] = round(weight[out_ch] / scale_w[out_ch])
```

2. **Bias Correction**
```python
# Correct for quantization bias
bias_error = (output_fp32 - output_int8).mean(dim=0)
corrected_bias = original_bias + bias_error
```

3. **Outlier Channel Splitting**
```python
# Split channels with extreme values
if max(abs(weight[out_ch])) > threshold:
    # Keep this channel in FP16
    mixed_precision_channels.append(out_ch)
```

4. **Equalization**
```python
# Equalize weight ranges across layers
# For sequential layers A and B:
# scale_factor = sqrt(max(A) / max(B))
# A' = A / scale_factor
# B' = B * scale_factor
# Maintains mathematical equivalence but better quantization
```

<a name="fp16"></a>
## 6. FP16 and Mixed Precision

### 6.1 FP16 Basics

**FP16 Format** (IEEE 754 half-precision):
- 1 sign bit
- 5 exponent bits
- 10 mantissa bits
- Range: ~6e-5 to 65504
- Precision: ~3 decimal digits

**Advantages over INT8**:
- Minimal accuracy loss (<0.1%)
- No calibration needed
- Simpler to implement
- Native hardware support (Tensor Cores)

**Disadvantages**:
- Only 2x speedup (vs 4x for INT8)
- Limited range can cause overflow/underflow

### 6.2 Mixed Precision Training and Inference

**Automatic Mixed Precision (AMP)**:
```python
import torch
from torch.cuda.amp import autocast, GradScaler

# Training with AMP
model = YourModel().cuda()
optimizer = torch.optim.Adam(model.parameters())
scaler = GradScaler()

for data, target in train_loader:
    optimizer.zero_grad()

    # Forward pass in FP16
    with autocast():
        output = model(data)
        loss = criterion(output, target)

    # Backward pass with scaled gradients
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# Inference with AMP
model.eval()
with torch.no_grad():
    with autocast():
        output = model(data)
```

**Which Operations Use FP16?**
```python
# FP16-safe operations (fast, accurate)
# - Matrix multiplications
# - Convolutions
# - Linear layers

# FP32 operations (numerically sensitive)
# - Softmax
# - Layer normalization
# - Loss computation
# - Large reductions

# PyTorch AMP automatically handles this
```

### 6.3 BFloat16 (BF16)

**BF16 Format**:
- 1 sign bit
- 8 exponent bits (same as FP32!)
- 7 mantissa bits
- Range: Same as FP32
- Precision: ~2 decimal digits

**Advantages**:
- Same range as FP32 (no overflow issues)
- Better for training than FP16
- Supported on TPUs, newer NVIDIA GPUs (Ampere+)

**Usage**:
```python
# BF16 training (PyTorch 1.10+)
with torch.cuda.amp.autocast(dtype=torch.bfloat16):
    output = model(data)

# TensorRT with BF16
config.set_flag(trt.BuilderFlag.BF16)
```

<a name="advanced"></a>
## 7. Advanced Quantization: FP8 and INT4

### 7.1 FP8 Quantization

**FP8 Formats** (Hopper H100+):

**E4M3** (4 exponent, 3 mantissa bits):
- Range: ±448
- Precision: Better precision, limited range
- Use case: Forward pass

**E5M2** (5 exponent, 2 mantissa bits):
- Range: ±57344
- Precision: Less precision, wider range
- Use case: Gradients (backward pass)

**FP8 in Practice**:
```python
# Transformer Engine (NVIDIA)
import transformer_engine.pytorch as te

# FP8 linear layer
fp8_linear = te.Linear(
    in_features=768,
    out_features=768,
    params_dtype=torch.float8_e4m3fn
)

# Automatic FP8 handling in forward/backward
output = fp8_linear(input)
```

**FP8 Benefits**:
- 2x speedup over FP16 on H100
- Better accuracy than INT8
- Designed for Transformers and LLMs

### 7.2 INT4 Quantization

**INT4 Range**: [-8, 7] (4 bits including sign)

**Use Cases**:
- LLM weight quantization
- Extreme memory constraints
- Edge deployment

**GPTQ (Accurate INT4 for LLMs)**:
```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

# Configure INT4 quantization
quantize_config = BaseQuantizeConfig(
    bits=4,  # INT4
    group_size=128,  # Quantization group size
    desc_act=False,  # Activation order
)

# Load and quantize model
model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantize_config=quantize_config
)

# Quantize with calibration data
model.quantize(calibration_data)

# Save quantized model
model.save_quantized("llama2-7b-gptq-int4")

# Inference
output = model.generate(**inputs)
```

**AWQ (Activation-aware Weight Quantization)**:
```python
from awq import AutoAWQForCausalLM

# Load model
model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

# Quantize to INT4
model.quantize(
    calibration_data,
    quant_config={
        "zero_point": True,
        "q_group_size": 128,
        "w_bit": 4,
        "version": "GEMM"
    }
)

# Save
model.save_quantized("llama2-7b-awq-int4")
```

**INT4 Trade-offs**:
- Model size: 8x smaller than FP32
- Speed: 2-3x faster (memory-bound models)
- Accuracy: 1-3% degradation typical
- Best with group-wise quantization (e.g., group_size=128)

### 7.3 Mixed Bit-Width Quantization

```python
# Different layers at different precisions

quantization_config = {
    'embeddings': 'fp16',           # Embeddings sensitive
    'attention_qkv': 'int8',        # QKV projections robust
    'attention_output': 'int8',     # Output projection robust
    'ffn_intermediate': 'int4',     # FFN first layer → INT4
    'ffn_output': 'int8',           # FFN second layer → INT8
    'layer_norm': 'fp32',           # LayerNorm in FP32
    'final_layer': 'fp16',          # Final layer sensitive
}

# Apply per-layer quantization
for name, module in model.named_modules():
    precision = get_precision_for_layer(name, quantization_config)
    quantize_layer(module, precision)
```

<a name="accuracy"></a>
## 8. Accuracy Preservation Strategies

### 8.1 Identifying Sensitive Layers

```python
def find_sensitive_layers(model, test_loader, threshold=0.5):
    """
    Quantize each layer individually and measure accuracy impact
    """
    baseline_acc = evaluate(model, test_loader)
    sensitive_layers = []

    for name, module in model.named_modules():
        if not is_quantizable(module):
            continue

        # Quantize only this layer
        original_module = module
        module_quantized = quantize_layer(module)
        setattr_nested(model, name, module_quantized)

        # Measure accuracy
        quant_acc = evaluate(model, test_loader)
        acc_drop = baseline_acc - quant_acc

        if acc_drop > threshold:
            sensitive_layers.append((name, acc_drop))

        # Restore original
        setattr_nested(model, name, original_module)

    return sorted(sensitive_layers, key=lambda x: x[1], reverse=True)
```

### 8.2 Cross-Layer Equalization

```python
def cross_layer_equalization(layer1, layer2):
    """
    Equalize weight ranges between consecutive layers
    """
    # For layer1 → layer2
    # Compute per-channel range

    range1 = layer1.weight.abs().max(dim=[1, 2, 3], keepdim=True)[0]
    range2 = layer2.weight.abs().max(dim=[0, 2, 3], keepdim=True)[0]

    # Equalization scale
    scale = torch.sqrt(range1 / (range2 + 1e-8))

    # Apply equalization
    layer1.weight.data /= scale
    if layer1.bias is not None:
        layer1.bias.data /= scale.squeeze()

    layer2.weight.data *= scale.permute(1, 0, 2, 3)

    # Mathematically equivalent but better for quantization
```

### 8.3 Bias Correction

```python
def apply_bias_correction(model, calibration_data):
    """
    Correct for systematic bias introduced by quantization
    """
    model_fp32 = copy.deepcopy(model)  # Keep FP32 copy
    model_int8 = quantize(model)

    corrections = {}

    for name, module in model_int8.named_modules():
        if not isinstance(module, (nn.Conv2d, nn.Linear)):
            continue

        # Collect activations from both models
        activations_fp32 = []
        activations_int8 = []

        def hook_fp32(m, input, output):
            activations_fp32.append(output.detach())

        def hook_int8(m, input, output):
            activations_int8.append(output.detach())

        # Register hooks
        handle_fp32 = module_fp32.register_forward_hook(hook_fp32)
        handle_int8 = module.register_forward_hook(hook_int8)

        # Run calibration data
        with torch.no_grad():
            for data in calibration_data:
                model_fp32(data)
                model_int8(data)

        # Compute bias correction
        acts_fp32 = torch.cat(activations_fp32, dim=0)
        acts_int8 = torch.cat(activations_int8, dim=0)

        bias_error = (acts_fp32 - acts_int8).mean(dim=0, keepdim=True)

        # Apply correction
        if module.bias is None:
            module.bias = nn.Parameter(bias_error.squeeze())
        else:
            module.bias.data += bias_error.squeeze()

        corrections[name] = bias_error.squeeze()

        handle_fp32.remove()
        handle_int8.remove()

    return corrections
```

<a name="frameworks"></a>
## 9. Quantization Frameworks and Tools

### 9.1 PyTorch Native Quantization

```python
import torch.quantization as quant

# Static quantization
model.qconfig = quant.get_default_qconfig('fbgemm')
model_prepared = quant.prepare(model)
# ... calibration ...
model_quantized = quant.convert(model_prepared)

# Dynamic quantization
model_quantized = quant.quantize_dynamic(
    model,
    {nn.Linear},
    dtype=torch.qint8
)

# QAT
model.qconfig = quant.get_default_qat_qconfig('fbgemm')
model_prepared = quant.prepare_qat(model)
# ... training ...
model_quantized = quant.convert(model_prepared)
```

### 9.2 TensorRT Quantization

```python
# PTQ with INT8
config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.INT8)
config.int8_calibrator = MyCalibrator(calibration_data)
engine = builder.build_serialized_network(network, config)

# QAT from PyTorch
# Export QAT model to ONNX with Q/DQ nodes
torch.onnx.export(qat_model, ...)
# TensorRT automatically recognizes and optimizes Q/DQ patterns
```

### 9.3 ONNX Runtime Quantization

```python
from onnxruntime.quantization import quantize_dynamic, quantize_static

# Dynamic quantization
quantize_dynamic(
    model_input="model.onnx",
    model_output="model_quant.onnx",
    weight_type=QuantType.QInt8
)

# Static quantization
quantize_static(
    model_input="model.onnx",
    model_output="model_quant.onnx",
    calibration_data_reader=calibration_reader,
    quant_format=QuantFormat.QDQ
)
```

### 9.4 Specialized Tools

**NVIDIA TensorRT Model Optimizer**:
```python
import modelopt.torch.quantization as mtq

# Auto-quantization
model = mtq.quantize(model, config, forward_loop=calibrate_loop)

# Export to TensorRT
mtq.export(model, "model.onnx")
```

**Intel Neural Compressor**:
```python
from neural_compressor import Quantization

quantizer = Quantization("config.yaml")
quantized_model = quantizer.fit(model)
```

**Brevitas (QAT framework)**:
```python
from brevitas.nn import QuantLinear, QuantConv2d

# Replace layers with quantized versions
model = nn.Sequential(
    QuantConv2d(3, 64, kernel_size=3, weight_bit_width=8),
    nn.ReLU(),
    QuantLinear(1000, 10, weight_bit_width=8)
)

# Train normally - quantization is built in
```

<a name="production"></a>
## 10. Production Deployment

### 10.1 Deployment Checklist

```python
# Pre-deployment validation

def validate_quantized_model(model_fp32, model_quant, test_loader):
    """
    Comprehensive validation before deployment
    """
    results = {}

    # 1. Accuracy comparison
    acc_fp32 = evaluate_accuracy(model_fp32, test_loader)
    acc_quant = evaluate_accuracy(model_quant, test_loader)
    results['accuracy_drop'] = acc_fp32 - acc_quant

    # 2. Output similarity
    cosine_sim = compute_output_similarity(model_fp32, model_quant, test_loader)
    results['output_similarity'] = cosine_sim

    # 3. Numerical stability
    max_diff = compute_max_difference(model_fp32, model_quant, test_loader)
    results['max_output_diff'] = max_diff

    # 4. Edge case testing
    edge_acc = evaluate_on_edge_cases(model_quant, edge_cases)
    results['edge_case_accuracy'] = edge_acc

    # 5. Performance benchmarking
    latency = benchmark_latency(model_quant)
    results['latency_ms'] = latency

    # 6. Memory usage
    memory = measure_memory_usage(model_quant)
    results['memory_mb'] = memory

    return results
```

### 10.2 Monitoring in Production

```python
class QuantizedModelMonitor:
    """
    Monitor quantized model performance in production
    """
    def __init__(self):
        self.output_ranges = {}
        self.anomaly_count = 0

    def monitor_inference(self, inputs, outputs):
        # Check for numerical anomalies
        if torch.isnan(outputs).any():
            self.anomaly_count += 1
            log_error("NaN detected in output")

        if torch.isinf(outputs).any():
            self.anomaly_count += 1
            log_error("Inf detected in output")

        # Track output distribution
        self.update_output_statistics(outputs)

        # Alert if distribution shifts significantly
        if self.detect_distribution_shift():
            alert_team("Output distribution shifted")
```

### 10.3 A/B Testing Quantized Models

```python
# A/B test framework
class ABTestingFramework:
    def __init__(self, model_a, model_b, traffic_split=0.5):
        self.model_a = model_a  # FP32 baseline
        self.model_b = model_b  # Quantized model
        self.traffic_split = traffic_split
        self.metrics_a = MetricsCollector()
        self.metrics_b = MetricsCollector()

    def inference(self, request):
        # Route traffic
        if random.random() < self.traffic_split:
            output = self.model_a(request)
            self.metrics_a.record(output, request)
        else:
            output = self.model_b(request)
            self.metrics_b.record(output, request)

        return output

    def compare_metrics(self):
        # Statistical significance testing
        return {
            'accuracy_a': self.metrics_a.accuracy(),
            'accuracy_b': self.metrics_b.accuracy(),
            'latency_a': self.metrics_a.avg_latency(),
            'latency_b': self.metrics_b.avg_latency(),
            'p_value': self.compute_significance()
        }
```

## Summary

This lecture covered quantization comprehensively:

- **Fundamentals**: Mathematical basis, granularity, calibration
- **PTQ**: Post-training quantization workflows and best practices
- **QAT**: Quantization-aware training for better accuracy
- **INT8**: Industry-standard quantization with 4x compression
- **FP16/BF16**: Mixed precision for minimal accuracy loss
- **Advanced**: FP8 and INT4 for extreme optimization
- **Accuracy**: Strategies to preserve model quality
- **Frameworks**: PyTorch, TensorRT, ONNX Runtime tools
- **Production**: Deployment validation and monitoring

Quantization is essential for production ML:
- Reduces costs by 50-75%
- Enables edge deployment
- Maintains acceptable accuracy with proper techniques
- Critical skill for LLM serving

## Next Steps

1. Complete Lab 02: Implement INT8 and FP16 quantization
2. Read Lecture 05: Model Pruning and Distillation
3. Experiment with different quantization methods
4. Benchmark quantized models on your hardware

## Further Reading

- "A Survey of Quantization Methods for Efficient Neural Network Inference"
- NVIDIA TensorRT Quantization Guide
- PyTorch Quantization Tutorial
- "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference"
- LLM.int8() paper
- GPTQ and AWQ papers

---

**Lecture Duration**: 8 hours
**Difficulty**: Advanced
