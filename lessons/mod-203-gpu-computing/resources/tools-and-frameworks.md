# Module 203: Tools and Frameworks Reference

## Development Tools

### CUDA Development Kit

**CUDA Toolkit**
- Current Version: 12.3 (as of 2024)
- Download: https://developer.nvidia.com/cuda-toolkit
- Includes: nvcc compiler, libraries, debugger, profilers
- Installation:
  ```bash
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
  sudo dpkg -i cuda-keyring_1.1-1_all.deb
  sudo apt-get update
  sudo apt-get -y install cuda-toolkit-12-3
  ```

**NVIDIA Drivers**
- Required: 525+ for A100/H100
- Check compatibility: https://docs.nvidia.com/deploy/cuda-compatibility/
- Installation:
  ```bash
  sudo apt-get install -y nvidia-driver-535
  ```

**NVIDIA Container Toolkit**
- Enables GPU support in Docker
- Installation:
  ```bash
  distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
  curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
  curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update
  sudo apt-get install -y nvidia-container-toolkit
  sudo systemctl restart docker
  ```

### Compilers and IDEs

**nvcc (NVIDIA CUDA Compiler)**
- Part of CUDA Toolkit
- Compiles CUDA C/C++ code
- Usage:
  ```bash
  nvcc -o program program.cu -arch=sm_80  # For A100
  nvcc -O3 -use_fast_math -o optimized program.cu
  ```

**Visual Studio Code with CUDA Extensions**
- Extension: "CUDA C++" by kriegalex
- Features: Syntax highlighting, IntelliSense
- Installation: Search "CUDA" in VS Code extensions

**NVIDIA Nsight Visual Studio Edition**
- Windows-only IDE for CUDA development
- Integrated debugging and profiling
- Download: https://developer.nvidia.com/nsight-visual-studio-edition

**CLion with CUDA Support**
- Cross-platform C++ IDE
- CUDA plugin available
- Website: https://www.jetbrains.com/clion/

## Profiling and Debugging Tools

### NVIDIA Nsight Systems

**Description**: System-wide performance analysis
**Key Features**:
- Timeline visualization
- CPU/GPU activity correlation
- CUDA API trace
- Multi-GPU support

**Installation**:
```bash
# Included in CUDA Toolkit or download standalone
wget https://developer.nvidia.com/downloads/assets/tools/secure/nsight-systems/2023_4_1/nsightsystems-linux-public-2023.4.1.97-3355750.deb
sudo dpkg -i nsightsystems-linux-public-2023.4.1.97-3355750.deb
```

**Basic Usage**:
```bash
# Profile application
nsys profile -o my_profile python train.py

# Profile with specific traces
nsys profile --trace=cuda,nvtx,cudnn,cublas --output=detailed python train.py

# Open GUI
nsys-ui my_profile.qdrep
```

### NVIDIA Nsight Compute

**Description**: Kernel-level performance analysis
**Key Features**:
- Detailed kernel metrics
- Roofline analysis
- Instruction-level profiling
- Optimization suggestions

**Installation**: Included in CUDA Toolkit

**Basic Usage**:
```bash
# Profile all kernels
ncu -o kernel_profile python train.py

# Profile specific kernel
ncu --kernel-name "matmul.*" -o matmul_profile python train.py

# Full analysis
ncu --set full -o detailed_profile python train.py

# Open GUI
ncu-ui kernel_profile.ncu-rep
```

### CUDA-GDB

**Description**: GPU debugger
**Key Features**:
- Set breakpoints in kernels
- Inspect GPU threads
- Examine device memory

**Basic Usage**:
```bash
# Compile with debug symbols
nvcc -g -G -o program program.cu

# Run debugger
cuda-gdb ./program

# Common commands
(cuda-gdb) break kernel_name
(cuda-gdb) run
(cuda-gdb) cuda thread
(cuda-gdb) print variable
```

### Compute Sanitizer

**Description**: Runtime error detection tool
**Types**:
- memcheck: Memory errors
- racecheck: Race conditions
- initcheck: Uninitialized memory
- synccheck: Synchronization errors

**Usage**:
```bash
# Check for memory errors
compute-sanitizer --tool memcheck ./program

# Check for race conditions
compute-sanitizer --tool racecheck ./program

# Check with Python
compute-sanitizer --tool memcheck python train.py
```

## GPU Management Tools

### nvidia-smi

**Description**: GPU monitoring and management
**Key Features**:
- Real-time GPU stats
- Process monitoring
- Power management
- MIG configuration

**Common Commands**:
```bash
# Basic status
nvidia-smi

# Continuous monitoring
nvidia-smi dmon -s puct -c 100

# Query specific metrics
nvidia-smi --query-gpu=gpu_name,temperature.gpu,utilization.gpu,memory.used --format=csv

# MIG commands
nvidia-smi -mig 1  # Enable MIG
nvidia-smi mig -lgip  # List GPU instance profiles
nvidia-smi mig -cgi 19,19 -C  # Create instances

# Process monitoring
nvidia-smi pmon -c 100
```

### NVIDIA Data Center GPU Manager (DCGM)

**Description**: Datacenter GPU management and monitoring
**Key Features**:
- Health checks
- Diagnostics
- Policy enforcement
- Metrics collection

**Installation**:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install -y datacenter-gpu-manager
```

**Usage**:
```bash
# Start DCGM daemon
sudo nv-hostengine

# Health check
dcgmi health -c -a

# Run diagnostics
dcgmi diag -r 3

# Monitor GPUs
dcgmi dmon -e 100,155,156,203

# DCGM Exporter for Prometheus
docker run -d --gpus all -p 9400:9400 nvcr.io/nvidia/k8s/dcgm-exporter:latest
```

## ML Frameworks

### PyTorch

**Description**: Dynamic ML framework with excellent GPU support
**Installation**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**GPU Usage**:
```python
import torch

# Check GPU availability
print(torch.cuda.is_available())
print(torch.cuda.device_count())

# Move model and data to GPU
model = Model().cuda()
data = data.cuda()

# Automatic Mixed Precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(data)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### TensorFlow

**Description**: Production-ready ML framework
**Installation**:
```bash
pip install tensorflow[and-cuda]
```

**GPU Configuration**:
```python
import tensorflow as tf

# List GPUs
print(tf.config.list_physical_devices('GPU'))

# Set memory growth
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# Mixed precision
from tensorflow.keras import mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)
```

### JAX

**Description**: High-performance numerical computing
**Installation**:
```bash
pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

**GPU Usage**:
```python
import jax
import jax.numpy as jnp

# Check devices
print(jax.devices())

# Automatic device placement
x = jnp.array([1, 2, 3])  # Automatically on GPU

# JIT compilation
@jax.jit
def fast_function(x):
    return jnp.dot(x, x.T)
```

## Distributed Training Frameworks

### PyTorch Distributed (DDP)

**Description**: Built-in distributed training
**Usage**:
```bash
# Single node, multiple GPUs
torchrun --nproc_per_node=8 train.py

# Multi-node
# Node 0:
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=0 \
    --master_addr="192.168.1.1" --master_port=12355 train.py
# Node 1:
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=1 \
    --master_addr="192.168.1.1" --master_port=12355 train.py
```

### DeepSpeed

**Description**: Microsoft's optimization library
**Installation**:
```bash
pip install deepspeed
```

**Usage**:
```python
import deepspeed

# DeepSpeed config
ds_config = {
    "train_batch_size": 64,
    "train_micro_batch_size_per_gpu": 8,
    "optimizer": {
        "type": "Adam",
        "params": {"lr": 0.001}
    },
    "fp16": {"enabled": True},
    "zero_optimization": {"stage": 2}
}

# Initialize
model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    model_parameters=model.parameters(),
    config=ds_config
)

# Train
for data, target in dataloader:
    loss = model_engine(data, target)
    model_engine.backward(loss)
    model_engine.step()
```

### Megatron-LM

**Description**: NVIDIA's large model training
**Installation**:
```bash
git clone https://github.com/NVIDIA/Megatron-LM.git
cd Megatron-LM
pip install -r requirements.txt
```

**Usage**:
```bash
python pretrain_gpt.py \
    --tensor-model-parallel-size 4 \
    --pipeline-model-parallel-size 2 \
    --num-layers 24 \
    --hidden-size 1024 \
    --num-attention-heads 16 \
    --micro-batch-size 4 \
    --global-batch-size 32
```

### Horovod

**Description**: Uber's distributed training framework
**Installation**:
```bash
HOROVOD_GPU_OPERATIONS=NCCL pip install horovod[pytorch]
```

**Usage**:
```python
import horovod.torch as hvd

hvd.init()
torch.cuda.set_device(hvd.local_rank())

model = Model().cuda()
optimizer = optim.SGD(model.parameters())
optimizer = hvd.DistributedOptimizer(optimizer)
hvd.broadcast_parameters(model.state_dict(), root_rank=0)

# Training loop (Horovod handles synchronization)
```

## Inference Optimization Tools

### TensorRT

**Description**: NVIDIA's inference optimizer
**Installation**:
```bash
pip install tensorrt
```

**Usage**:
```python
import tensorrt as trt

# Build engine from ONNX
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
parser = trt.OnnxParser(network, logger)

with open('model.onnx', 'rb') as f:
    parser.parse(f.read())

config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)  # Enable FP16

engine = builder.build_engine(network, config)

# Serialize engine
with open('model.plan', 'wb') as f:
    f.write(engine.serialize())
```

### NVIDIA Triton Inference Server

**Description**: Production inference serving
**Installation**:
```bash
docker pull nvcr.io/nvidia/tritonserver:23.10-py3
```

**Usage**:
```bash
# Run Triton server
docker run --gpus all --rm -p 8000:8000 -p 8001:8001 -p 8002:8002 \
    -v /path/to/model_repository:/models \
    nvcr.io/nvidia/tritonserver:23.10-py3 \
    tritonserver --model-repository=/models
```

### ONNX Runtime

**Description**: Cross-platform inference engine
**Installation**:
```bash
pip install onnxruntime-gpu
```

**Usage**:
```python
import onnxruntime as ort

# Create session
session = ort.InferenceSession('model.onnx', providers=['CUDAExecutionProvider'])

# Run inference
outputs = session.run(None, {'input': input_data})
```

## Container and Orchestration Tools

### Docker with NVIDIA Runtime

**PyTorch Container**:
```dockerfile
FROM nvcr.io/nvidia/pytorch:23.10-py3

WORKDIR /workspace
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "train.py"]
```

```bash
docker build -t my-training .
docker run --gpus all my-training
```

### Kubernetes GPU Operator

**Installation**:
```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install --wait gpu-operator nvidia/gpu-operator \
    --namespace gpu-operator-resources \
    --create-namespace
```

**Pod with GPU**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: cuda-container
    image: nvcr.io/nvidia/cuda:12.0-base
    resources:
      limits:
        nvidia.com/gpu: 1
```

### Slurm with GPU Support

**Job Script**:
```bash
#!/bin/bash
#SBATCH --job-name=gpu_training
#SBATCH --gres=gpu:a100:4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=24:00:00

module load cuda/12.0
source activate pytorch-env

python train.py
```

## Monitoring and Observability

### Prometheus + DCGM Exporter

**docker-compose.yml**:
```yaml
version: '3'
services:
  dcgm-exporter:
    image: nvcr.io/nvidia/k8s/dcgm-exporter:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "9400:9400"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
```

### Weights & Biases

**Installation**:
```bash
pip install wandb
```

**Usage**:
```python
import wandb

wandb.init(project="my-project")

# Log metrics
wandb.log({"loss": loss, "accuracy": acc})

# Log GPU metrics
wandb.log({"gpu_utilization": gpu_util})
```

### TensorBoard

**Usage**:
```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('runs/experiment1')

# Log scalars
writer.add_scalar('Loss/train', loss, epoch)

# Log GPU utilization
writer.add_scalar('GPU/utilization', gpu_util, step)
```

## Benchmarking Tools

### NVIDIA DALI (Data Loading Library)

**Installation**:
```bash
pip install --extra-index-url https://developer.download.nvidia.com/compute/redist --upgrade nvidia-dali-cuda120
```

**Usage**:
```python
from nvidia.dali import pipeline_def
import nvidia.dali.fn as fn

@pipeline_def
def image_pipeline():
    jpegs, labels = fn.readers.file(file_root=data_dir, random_shuffle=True)
    images = fn.decoders.image(jpegs, device='mixed')
    images = fn.resize(images, resize_x=224, resize_y=224)
    images = fn.crop_mirror_normalize(images, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    return images, labels
```

### MLPerf Benchmarks

**Installation**:
```bash
git clone https://github.com/mlcommons/training_results_v3.0.git
cd training_results_v3.0/NVIDIA
```

**Run Benchmark**:
```bash
./run_and_time.sh
```

## Utility Scripts

### GPU Memory Monitor

```python
# gpu_monitor.py
import torch
import time

def monitor_gpu_memory():
    while True:
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i) / 1e9
                reserved = torch.cuda.memory_reserved(i) / 1e9
                print(f"GPU {i}: Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
        time.sleep(1)

if __name__ == "__main__":
    monitor_gpu_memory()
```

### Batch Size Finder

```python
# find_batch_size.py
import torch
import torch.nn as nn

def find_max_batch_size(model, input_shape):
    model = model.cuda()
    batch_size = 1

    while True:
        try:
            dummy_input = torch.randn(batch_size, *input_shape).cuda()
            output = model(dummy_input)
            loss = output.sum()
            loss.backward()

            print(f"Batch size {batch_size}: OK")
            batch_size *= 2

            torch.cuda.empty_cache()
        except RuntimeError as e:
            if "out of memory" in str(e):
                print(f"Max batch size: {batch_size // 2}")
                break
            else:
                raise e

# Usage
model = YourModel()
find_max_batch_size(model, input_shape=(3, 224, 224))
```

## Quick Reference Commands

### System Information
```bash
# GPU info
nvidia-smi
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv

# CUDA version
nvcc --version
cat /usr/local/cuda/version.txt

# cuDNN version
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2

# Driver info
cat /proc/driver/nvidia/version
```

### Performance Testing
```bash
# GPU bandwidth test
/usr/local/cuda/samples/1_Utilities/bandwidthTest/bandwidthTest

# Peer-to-peer bandwidth
/usr/local/cuda/samples/1_Utilities/p2pBandwidthLatencyTest/p2pBandwidthLatencyTest

# Device query
/usr/local/cuda/samples/1_Utilities/deviceQuery/deviceQuery
```

---

**This tools reference provides everything you need to develop, profile, optimize, and deploy GPU-accelerated ML workloads in production.**
