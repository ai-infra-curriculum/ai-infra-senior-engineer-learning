# Tools and Frameworks - Module 204

## Optimization Frameworks

### TensorRT (NVIDIA)

**Purpose**: High-performance inference optimizer for NVIDIA GPUs

**Installation**:
```bash
# Via pip (with CUDA 12.x)
pip install tensorrt

# Or download from NVIDIA: https://developer.nvidia.com/tensorrt
```

**Key Features**:
- Layer fusion and kernel auto-tuning
- FP16, INT8, FP8 precision support
- Dynamic shape optimization
- Custom plugin support

**Use Cases**:
- Production inference on NVIDIA GPUs
- Vision models (ResNet, EfficientNet)
- NLP models (BERT, GPT-small)
- Maximum performance requirements

**Learning Resources**:
- Official docs: https://docs.nvidia.com/deeplearning/tensorrt/
- Examples: https://github.com/NVIDIA/TensorRT

---

### ONNX Runtime (Microsoft)

**Purpose**: Cross-platform ML inference engine

**Installation**:
```bash
# CPU version
pip install onnxruntime

# GPU version (CUDA)
pip install onnxruntime-gpu
```

**Key Features**:
- Multiple execution providers (CPU, CUDA, TensorRT, ROCm, CoreML, etc.)
- Graph optimizations
- Quantization support
- Framework-agnostic (works with PyTorch, TensorFlow, etc.)

**Use Cases**:
- Multi-platform deployment
- AMD/Intel GPU support
- CPU inference optimization
- Framework flexibility needed

**Learning Resources**:
- Official docs: https://onnxruntime.ai/
- GitHub: https://github.com/microsoft/onnxruntime

---

### vLLM

**Purpose**: High-throughput LLM serving with PagedAttention

**Installation**:
```bash
pip install vllm
```

**Key Features**:
- PagedAttention for efficient KV cache
- Continuous batching
- OpenAI-compatible API
- Multi-GPU tensor parallelism

**Use Cases**:
- LLM serving at scale
- High-throughput generation
- Memory-efficient inference
- Production chatbots/APIs

**Learning Resources**:
- Docs: https://docs.vllm.ai/
- GitHub: https://github.com/vllm-project/vllm
- Paper: https://arxiv.org/abs/2309.06180

---

### TensorRT-LLM (NVIDIA)

**Purpose**: Optimized LLM inference with TensorRT

**Installation**:
```bash
# Build from source (complex setup)
git clone https://github.com/NVIDIA/TensorRT-LLM
# Follow installation guide
```

**Key Features**:
- Maximum LLM performance on NVIDIA GPUs
- FP8, INT4 quantization support
- In-flight batching
- Custom CUDA kernels

**Use Cases**:
- Maximum performance on NVIDIA GPUs
- INT4/FP8 quantization needed
- Willing to invest in setup

**Learning Resources**:
- GitHub: https://github.com/NVIDIA/TensorRT-LLM
- Examples: Included in repo

---

### SGLang

**Purpose**: Structured generation and speculative decoding

**Installation**:
```bash
pip install sglang
```

**Key Features**:
- Speculative decoding
- Structured output (JSON, code)
- Constrained generation
- Fast inference

**Use Cases**:
- Structured outputs needed
- Speculative decoding benefits
- Complex generation tasks

**Learning Resources**:
- GitHub: https://github.com/sgl-project/sglang
- Docs: In repo

---

## Quantization Tools

### PyTorch Quantization

**Built-in PyTorch quantization**

```bash
# Included in PyTorch
pip install torch torchvision
```

**Features**:
- Static and dynamic quantization
- Quantization-aware training (QAT)
- INT8, FP16 support
- Easy integration

**Use Cases**:
- PyTorch-native quantization
- Custom quantization schemes
- Research and prototyping

---

### Brevitas (Xilinx)

**Quantization-aware training framework**

```bash
pip install brevitas
```

**Features**:
- Flexible QAT
- Arbitrary bit-widths
- FPGA-friendly quantization
- Research-oriented

**Use Cases**:
- Custom quantization research
- FPGA deployment
- Fine-grained control

**GitHub**: https://github.com/Xilinx/brevitas

---

### Intel Neural Compressor

**Quantization and optimization toolkit**

```bash
pip install neural-compressor
```

**Features**:
- Auto-quantization
- Intel CPU optimization
- Multiple frameworks
- Benchmarking tools

**Use Cases**:
- Intel CPU deployment
- Auto-optimization
- Multi-framework support

**GitHub**: https://github.com/intel/neural-compressor

---

### GPTQ / AWQ

**INT4 quantization for LLMs**

```bash
# GPTQ
pip install auto-gptq

# AWQ
pip install autoawq
```

**Features**:
- INT4 weight quantization
- Minimal accuracy loss
- 4x memory reduction
- LLM-specific

**Use Cases**:
- Extreme LLM compression
- Memory-constrained deployment
- 70B+ models on consumer GPUs

**GitHub**:
- GPTQ: https://github.com/IST-DASLab/gptq
- AWQ: https://github.com/mit-han-lab/llm-awq

---

## Profiling and Benchmarking

### NVIDIA Nsight Systems

**System-wide performance profiling**

**Installation**: Download from NVIDIA website

**Features**:
- CPU/GPU timeline view
- Kernel execution analysis
- Memory transfers
- API calls tracing

**Use Cases**:
- Identify performance bottlenecks
- Optimize CUDA kernels
- Analyze memory bandwidth

**Download**: https://developer.nvidia.com/nsight-systems

---

### NVIDIA Nsight Compute

**GPU kernel profiling**

**Installation**: Download from NVIDIA website

**Features**:
- Detailed kernel metrics
- Occupancy analysis
- Memory bandwidth utilization
- Instruction-level profiling

**Use Cases**:
- Optimize custom CUDA kernels
- Deep performance analysis
- Understand GPU utilization

**Download**: https://developer.nvidia.com/nsight-compute

---

### PyTorch Profiler

**PyTorch-native profiling**

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
    record_shapes=True
) as prof:
    model(input_data)

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

**Features**:
- Integrated with PyTorch
- Layer-level timing
- Memory profiling
- TensorBoard visualization

---

### MLPerf Inference

**Industry-standard benchmarks**

```bash
git clone https://github.com/mlcommons/inference
# Follow setup instructions
```

**Features**:
- Standardized benchmarks
- Multiple models and scenarios
- Hardware comparison
- Submission to leaderboard

**Use Cases**:
- Compare against industry baselines
- Hardware evaluation
- Production readiness validation

**Website**: https://mlcommons.org/en/inference/

---

## Model Conversion Tools

### ONNX

**Model format for interoperability**

```bash
pip install onnx onnx-simplifier
```

**Features**:
- Framework-agnostic format
- Standard operator set
- Optimization passes
- Wide tool support

**Tools**:
- `torch.onnx.export`: PyTorch → ONNX
- `tf2onnx`: TensorFlow → ONNX
- `onnx-simplifier`: Optimize ONNX graphs

---

### Polygraphy (NVIDIA)

**TensorRT debugging and comparison**

```bash
pip install polygraphy
```

**Features**:
- Compare TensorRT vs ONNX Runtime
- Layer-by-layer debugging
- Tactic replay
- Accuracy debugging

**Use Cases**:
- Debug TensorRT accuracy issues
- Compare implementations
- Optimize tactic selection

**Docs**: https://docs.nvidia.com/deeplearning/tensorrt/polygraphy/

---

## Development Environments

### Docker Images

**Pre-configured environments**

```bash
# PyTorch with CUDA
docker pull pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# TensorFlow with GPU
docker pull tensorflow/tensorflow:latest-gpu

# NVIDIA NGC Containers (optimized)
docker pull nvcr.io/nvidia/pytorch:23.12-py3
docker pull nvcr.io/nvidia/tensorrt:23.12-py3
```

**NVIDIA NGC Catalog**: https://catalog.ngc.nvidia.com/

---

### Google Colab

**Free GPU access for experimentation**

- Free T4 GPU (limited hours)
- Colab Pro: Better GPUs (A100)
- Pre-installed ML libraries
- Good for learning and prototyping

**URL**: https://colab.research.google.com/

---

### Vast.ai / RunPod

**Affordable GPU rentals**

- Rent GPUs by the hour
- Various GPU types (A100, H100, 4090)
- Good for experiments and benchmarking

**URLs**:
- Vast.ai: https://vast.ai/
- RunPod: https://www.runpod.io/

---

## Monitoring and Observability

### NVIDIA SMI

**GPU monitoring CLI**

```bash
# Real-time monitoring
watch -n 0.5 nvidia-smi

# Logging
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.total,memory.used --format=csv -l 1
```

---

### PyNVML

**Python bindings for NVIDIA Management Library**

```bash
pip install pynvml
```

```python
import pynvml

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f"Used: {info.used / 1024**3:.2f} GB")
```

---

### Prometheus + Grafana

**Production monitoring**

- Export GPU metrics with NVIDIA DCGM Exporter
- Visualize in Grafana dashboards
- Alert on anomalies

**DCGM Exporter**: https://github.com/NVIDIA/dcgm-exporter

---

## Testing and Validation

### pytest

**Unit testing framework**

```bash
pip install pytest pytest-benchmark
```

**Use for**:
- Unit testing inference code
- Benchmarking with pytest-benchmark
- Regression testing

---

### Locust

**Load testing**

```bash
pip install locust
```

**Use for**:
- Load testing inference APIs
- Stress testing
- Throughput measurement

**Website**: https://locust.io/

---

## Hardware

### Recommended GPUs for Learning

**Entry Level**:
- NVIDIA RTX 4060 Ti (16GB)
- NVIDIA RTX 4070

**Mid-Range**:
- NVIDIA RTX 4090 (24GB)
- NVIDIA RTX A4000/A5000

**Professional**:
- NVIDIA A100 (40GB/80GB)
- NVIDIA H100 (80GB)

**Cloud Options**:
- AWS: p4d/p5 instances (A100/H100)
- GCP: A100/H100 instances
- Azure: NDv4 series

---

## Setup Recommendations

### Development Workstation

```bash
# CUDA Toolkit
# Download from: https://developer.nvidia.com/cuda-toolkit

# cuDNN
# Download from: https://developer.nvidia.com/cudnn

# Python environment
conda create -n optimization python=3.10
conda activate optimization

# Core libraries
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install tensorrt onnxruntime-gpu vllm
pip install transformers accelerate
pip install numpy pandas matplotlib jupyter

# Profiling
pip install py-spy memory-profiler

# Testing
pip install pytest pytest-benchmark locust
```

---

### Production Server

```bash
# Use NVIDIA NGC containers
docker pull nvcr.io/nvidia/pytorch:23.12-py3

# Or build custom Dockerfile
FROM nvcr.io/nvidia/pytorch:23.12-py3
RUN pip install vllm tensorrt onnxruntime-gpu
COPY models/ /app/models/
COPY serve.py /app/
CMD ["python", "/app/serve.py"]
```

---

## Quick Start Examples

### TensorRT

```python
import tensorrt as trt

# Build engine
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)
# ... build engine
```

### vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-2-7b-chat-hf")
outputs = llm.generate(["Hello"], SamplingParams(max_tokens=100))
print(outputs[0].outputs[0].text)
```

### ONNX Runtime

```python
import onnxruntime as ort

session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider']
)
outputs = session.run(None, {'input': input_data})
```

---

## Tool Selection Guide

| Use Case | Recommended Tool | Alternative |
|----------|------------------|-------------|
| Vision Model (NVIDIA GPU) | TensorRT | ONNX Runtime |
| LLM Serving | vLLM | TensorRT-LLM |
| Multi-platform | ONNX Runtime | - |
| Quantization (PyTorch) | PyTorch Native | Brevitas |
| INT4 LLM | GPTQ/AWQ | TensorRT-LLM |
| Profiling | Nsight Systems | PyTorch Profiler |
| Load Testing | Locust | Custom scripts |

---

## Troubleshooting Common Issues

### CUDA Out of Memory
- Reduce batch size
- Use gradient checkpointing
- Enable KV cache quantization (for LLMs)

### Slow Inference
- Profile with Nsight Systems
- Check GPU utilization
- Verify optimal batch size

### Accuracy Degradation
- Use layer-wise sensitivity analysis
- Try mixed precision
- Increase calibration data

---

## Community and Support

- **NVIDIA Developer Forums**: https://forums.developer.nvidia.com/
- **PyTorch Discuss**: https://discuss.pytorch.org/
- **vLLM GitHub Issues**: https://github.com/vllm-project/vllm/issues
- **Stack Overflow**: Tag: tensorrt, onnx, vllm, etc.

---

**Last Updated**: October 2025
**Module**: 204 - Advanced Model Optimization and Inference
