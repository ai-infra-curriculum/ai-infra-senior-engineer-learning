# Lecture 06: GPU Virtualization and Sharing Strategies

## Learning Objectives

By the end of this lecture, you will be able to:

- Design multi-tenant GPU infrastructure using MIG (Multi-Instance GPU) to provide hardware-isolated GPU resources with QoS guarantees for different teams and workloads
- Implement NVIDIA vGPU solutions for virtualized environments enabling GPU acceleration in VMs with live migration support for enterprise infrastructure
- Configure GPU sharing strategies (MIG, MPS, time-slicing) based on workload isolation requirements, QoS needs, and cost optimization objectives
- Architect Kubernetes-based GPU clusters with MIG support using GPU Operator to provide flexible GPU resource allocation and scheduling for containerized workloads
- Evaluate trade-offs between different GPU sharing approaches (MIG vs MPS vs time-slicing vs vGPU) based on performance isolation, overhead, and use case requirements
- Implement fractional GPU allocation strategies for inference serving to maximize GPU utilization while maintaining predictable latency for production services
- Design capacity planning strategies for shared GPU infrastructure that balance resource utilization, cost efficiency, and user experience based on usage patterns
- Troubleshoot common GPU sharing issues including memory contention, performance interference, and MIG configuration problems using monitoring and diagnostic tools

## Table of Contents
1. [Introduction to GPU Virtualization](#introduction-to-gpu-virtualization)
2. [Multi-Instance GPU (MIG)](#multi-instance-gpu-mig)
3. [NVIDIA vGPU](#nvidia-vgpu)
4. [Time-Slicing and MPS](#time-slicing-and-mps)
5. [GPU Sharing in Kubernetes](#gpu-sharing-in-kubernetes)
6. [Use Cases and Trade-offs](#use-cases-and-trade-offs)
7. [Performance Isolation](#performance-isolation)

## Introduction to GPU Virtualization

GPU virtualization enables sharing expensive GPU resources across multiple users, applications, or workloads.

### Why GPU Virtualization?

1. **Cost Efficiency**: Maximize GPU utilization across workloads
2. **Multi-Tenancy**: Safely share GPUs between teams/users
3. **Resource Allocation**: Right-size GPU resources for workloads
4. **Development/Testing**: Provide isolated GPU access
5. **Inference Serving**: Serve multiple models on shared GPUs

### GPU Sharing Approaches

```
GPU Sharing Strategies:

1. Time-Slicing (Traditional):
   Time → [App A] [App B] [App A] [App B]
   - Context switching overhead
   - No QoS guarantees
   - No fault isolation

2. MPS (Multi-Process Service):
   Time → [App A + App B running concurrently]
   - Shares SM and memory
   - Better utilization
   - Still no isolation

3. MIG (Multi-Instance GPU):
   GPU split into instances:
   ┌──────────┬──────────┐
   │ Instance │ Instance │
   │    A     │    B     │
   └──────────┴──────────┘
   - Hardware isolation
   - QoS guarantees
   - Fault isolation

4. vGPU (Virtualization):
   Hypervisor layer virtualizes GPU
   - Full VM isolation
   - Live migration support
   - Mediated passthrough
```

### Comparison Matrix

| Feature | Time-Slicing | MPS | MIG | vGPU |
|---------|-------------|-----|-----|------|
| Isolation | None | None | Strong | Strong |
| QoS | No | No | Yes | Yes |
| Overhead | High | Low | Minimal | Medium |
| GPUs | All | All | A30/A100/H100 | Data Center |
| Use Case | Dev/Test | Inference | Multi-Tenant | VMs/VDI |

## Multi-Instance GPU (MIG)

MIG partitions a single A100/A30/H100 into up to 7 isolated GPU instances with dedicated compute, memory, and cache.

### MIG Architecture

Each MIG instance includes:
- **Dedicated SMs**: Fixed number of Streaming Multiprocessors
- **Dedicated Memory**: Slice of HBM with memory controllers
- **Dedicated L2 Cache**: Isolated cache partition
- **QoS Enforcement**: Hardware-enforced quality of service
- **Fault Isolation**: Errors don't affect other instances

```
A100 (108 SMs) MIG Partitioning:

Full GPU (108 SMs, 40/80 GB):
┌─────────────────────────────────┐
│         Entire GPU              │
│      108 SMs, 40/80 GB          │
└─────────────────────────────────┘

Split into 7 instances (1g.5gb each):
┌────┬────┬────┬────┬────┬────┬────┐
│1g  │1g  │1g  │1g  │1g  │1g  │1g  │
│14SM│14SM│14SM│14SM│14SM│14SM│14SM│
│5GB │5GB │5GB │5GB │5GB │5GB │5GB │
└────┴────┴────┴────┴────┴────┴────┘

Split into 2 instances (3g.20gb each):
┌─────────────────┬─────────────────┐
│      3g.20gb    │     3g.20gb     │
│   42 SMs, 20GB  │  42 SMs, 20GB   │
└─────────────────┴─────────────────┘
```

### MIG Profiles

**A100 40GB MIG Profiles:**

| Profile | Instances | SMs | Memory | Fraction |
|---------|-----------|-----|--------|----------|
| 1g.5gb  | 7 | 14 | 5 GB | 1/7 |
| 2g.10gb | 3 | 28 | 10 GB | 1/4 |
| 3g.20gb | 2 | 42 | 20 GB | 3/7 |
| 4g.20gb | 1 | 56 | 20 GB | 4/7 |
| 7g.40gb | 1 | 108 | 40 GB | Full |

**A100 80GB MIG Profiles:**
- 1g.10gb: 7 instances
- 2g.20gb: 3 instances
- 3g.40gb: 2 instances
- 7g.80gb: Full GPU

**Mixed Configurations Allowed:**
- 1x 3g.20gb + 2x 2g.10gb
- 1x 4g.20gb + 1x 2g.10gb + 1x 1g.5gb

### Enabling and Configuring MIG

```bash
# 1. Check if GPU supports MIG
nvidia-smi -i 0 --query-gpu=mig.mode.current --format=csv,noheader
# Output: Enabled or Disabled

# 2. Enable MIG mode (requires reboot/reset)
sudo nvidia-smi -i 0 -mig 1
# or
sudo nvidia-smi -i 0 --mig-config-mode=1

# 3. Reset GPU (if not using drivers that support dynamic MIG)
sudo nvidia-smi -i 0 --gpu-reset

# 4. Check MIG mode
nvidia-smi -i 0 --query-gpu=mig.mode.current --format=csv,noheader

# 5. List available MIG profiles
nvidia-smi mig -lgip
# Output shows available profiles (e.g., 1g.5gb, 2g.10gb, 3g.20gb)

# 6. Create GPU instances
# Create 2x 3g.20gb instances
sudo nvidia-smi mig -cgi 9,9 -C
# -cgi: Create GPU Instance (9 = 3g.20gb profile ID)
# -C: Also create Compute Instance

# Create 7x 1g.5gb instances
sudo nvidia-smi mig -cgi 19,19,19,19,19,19,19 -C

# 7. List created instances
nvidia-smi mig -lgi
# Shows GPU Instance ID, placement, and profile

nvidia-smi mig -lci
# Shows Compute Instance ID

# 8. Check MIG devices
nvidia-smi -L
# Output:
# GPU 0: NVIDIA A100-SXM4-40GB (UUID: GPU-xxx)
#   MIG 1g.5gb Device 0: (UUID: MIG-xxx)
#   MIG 1g.5gb Device 1: (UUID: MIG-xxx)
#   ...
```

### Using MIG Instances

**Method 1: CUDA_VISIBLE_DEVICES with MIG UUID**

```bash
# Get MIG device UUID
nvidia-smi -L
# Copy UUID of MIG device

# Set environment variable
export CUDA_VISIBLE_DEVICES=MIG-abcd1234-xxxx-yyyy-zzzz-123456789abc

# Run application
python train.py

# Application sees single GPU (the MIG instance)
```

**Method 2: CUDA_VISIBLE_DEVICES with Device Index**

```bash
# MIG instances are enumerated
export CUDA_VISIBLE_DEVICES=0  # First MIG instance

python train.py
```

**Method 3: nvidia-smi for Process Management**

```bash
# Run process on specific MIG instance
nvidia-smi mig -i 0 -gi 5 -ci 0 python train.py
# -i 0: GPU 0
# -gi 5: GPU Instance 5
# -ci 0: Compute Instance 0
```

### MIG with Docker

```bash
# Docker with MIG support
docker run --gpus '"device=0:0"' nvidia/cuda:12.0-base nvidia-smi
# device=0:0 means GPU 0, MIG instance 0

# Or use MIG UUID
docker run --gpus 'device=MIG-xxx' nvidia/cuda:12.0-base nvidia-smi

# Docker Compose
services:
  training:
    image: pytorch/pytorch
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['MIG-xxx']
              capabilities: [gpu]
```

### MIG with Kubernetes

```yaml
# GPU Operator with MIG support
apiVersion: v1
kind: Pod
metadata:
  name: mig-pod
spec:
  containers:
  - name: cuda-container
    image: nvidia/cuda:12.0-base
    resources:
      limits:
        nvidia.com/mig-1g.5gb: 1  # Request 1x 1g.5gb MIG instance
    command: ["sleep", "infinity"]
```

### Destroying MIG Instances

```bash
# Destroy all compute instances
sudo nvidia-smi mig -dci

# Destroy all GPU instances
sudo nvidia-smi mig -dgi

# Disable MIG mode
sudo nvidia-smi -i 0 -mig 0

# Reset GPU
sudo nvidia-smi -i 0 --gpu-reset
```

### MIG Best Practices

1. **Right-size instances**: Don't over-provision
2. **Match workload**: Inference = smaller instances, Training = larger
3. **Monitor utilization**: Ensure instances are used efficiently
4. **Automate creation**: Use scripts/Terraform for consistent setup
5. **Profile first**: Understand memory/compute needs before sizing

```bash
# Example: Automate MIG configuration
#!/bin/bash
# setup_mig.sh

GPU_ID=0
PROFILE="1g.5gb"  # or 2g.10gb, 3g.20gb
NUM_INSTANCES=7

# Enable MIG
nvidia-smi -i $GPU_ID -mig 1
nvidia-smi -i $GPU_ID --gpu-reset

# Create instances
PROFILE_ID=$(nvidia-smi mig -lgip | grep $PROFILE | awk '{print $NF}')
INSTANCE_LIST=$(printf "$PROFILE_ID,%.0s" $(seq 1 $NUM_INSTANCES))
INSTANCE_LIST=${INSTANCE_LIST%,}  # Remove trailing comma

nvidia-smi mig -cgi $INSTANCE_LIST -C

# Verify
nvidia-smi mig -lgi
```

## NVIDIA vGPU

NVIDIA vGPU enables GPU virtualization for VMs, providing GPU acceleration with hypervisor isolation.

### vGPU Architecture

```
Hypervisor (ESXi, KVM, Hyper-V)
├── VM 1 (vGPU) → Guest Driver → Virtual GPU
├── VM 2 (vGPU) → Guest Driver → Virtual GPU
└── VM 3 (vGPU) → Guest Driver → Virtual GPU
         ↓
   Host Driver (NVIDIA vGPU Manager)
         ↓
   Physical GPU (A10, A16, A30, A100, etc.)
```

### vGPU Profiles

**A10 vGPU Profiles:**
- A10-1Q: 3GB, 1/6 GPU
- A10-2Q: 6GB, 1/3 GPU
- A10-4Q: 12GB, 2/3 GPU
- A10-12Q: 24GB, Full GPU

**A100 vGPU Profiles:**
- A100-4C: 4GB
- A100-8C: 8GB
- A100-16C: 16GB
- A100-40C: 40GB (Full)

### vGPU Licensing

NVIDIA vGPU requires licenses:
- **vPC** (Virtual PC): VDI workstations
- **vApps** (Virtual Applications): Session-based apps
- **vCS** (Compute Server): AI/ML/HPC workloads (includes MIG support)

```bash
# Configure vGPU license server in VM
# /etc/nvidia/gridd.conf
ServerAddress=license-server.company.com
ServerPort=7070
FeatureType=1  # 1=vCS, 2=vApps, 4=vPC

# Restart license daemon
sudo systemctl restart nvidia-gridd

# Check license status
nvidia-smi -q | grep -A 5 "vGPU Software Licensed Product"
```

### vGPU vs MIG

| Feature | MIG | vGPU |
|---------|-----|------|
| Isolation | Process-level | VM-level |
| Overhead | Minimal | Some (hypervisor) |
| Use Case | Containers, bare-metal | VMs |
| Live Migration | No | Yes (with vMotion/DRS) |
| Licensing | Free | Requires license |
| Setup Complexity | Low | Medium |

## Time-Slicing and MPS

### GPU Time-Slicing

Traditional GPU sharing via context switching:

```bash
# Kubernetes time-slicing (no special config needed)
apiVersion: v1
kind: Pod
metadata:
  name: shared-gpu-pod-1
spec:
  containers:
  - name: container-1
    image: nvidia/cuda:12.0-base
    resources:
      limits:
        nvidia.com/gpu: 1  # Multiple pods can request same GPU
```

**Problems with Time-Slicing:**
- Context switching overhead (can be 100+ ms)
- No QoS or resource limits
- No fault isolation
- Poor for latency-sensitive workloads

### MPS (Multi-Process Service)

MPS allows multiple CUDA contexts to share GPU concurrently:

```bash
# Start MPS daemon
export CUDA_VISIBLE_DEVICES=0
nvidia-cuda-mps-control -d

# Run multiple processes (they share GPU)
python inference_1.py &
python inference_2.py &
python inference_3.py &

# Check MPS status
ps aux | grep mps

# Stop MPS
echo quit | nvidia-cuda-mps-control

# TODO: Compare inference latency with and without MPS
```

**MPS Benefits:**
- Lower overhead than time-slicing
- Better SM utilization (concurrent kernel execution)
- Shared memory allocation

**MPS Limitations:**
- No memory isolation
- One process can OOM all processes
- No QoS guarantees
- Pre-Volta GPUs: limited concurrency

### MPS with Resource Limits

```bash
# Set per-process memory limit (Volta+)
export CUDA_MPS_ACTIVE_THREAD_PERCENTAGE=50  # Use 50% of threads

# Set device memory allocation limit
export CUDA_MPS_PINNED_DEVICE_MEM_LIMIT=0=4G  # 4GB limit on GPU 0

# Start MPS with limits
nvidia-cuda-mps-control -d
```

### When to Use Each Approach

**Use MIG when:**
- Need strong isolation (multi-tenant)
- Need QoS guarantees
- Running on A30/A100/H100
- Containerized workloads

**Use vGPU when:**
- Running VMs
- Need live migration
- VDI or virtual desktops
- Enterprise VM infrastructure

**Use MPS when:**
- Multiple small inference requests
- Low latency requirements
- Trusted workloads (no isolation needed)
- Maximum GPU utilization

**Use Time-Slicing when:**
- Dev/test environments
- No MIG support on GPU
- Temporary sharing needs
- Low cost priority

## GPU Sharing in Kubernetes

### Native GPU Sharing (Time-Slicing)

```yaml
# Device plugin allows sharing
apiVersion: v1
kind: ConfigMap
metadata:
  name: gpu-sharing-config
data:
  any: |-
    version: v1
    sharing:
      timeSlicing:
        replicas: 4  # Share each GPU among 4 pods
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-device-plugin
spec:
  template:
    spec:
      containers:
      - name: nvidia-device-plugin
        image: nvcr.io/nvidia/k8s-device-plugin:v0.14.0
        env:
        - name: CONFIG_FILE
          value: /config/any
        volumeMounts:
        - name: config
          mountPath: /config
      volumes:
      - name: config
        configMap:
          name: gpu-sharing-config
```

### MIG in Kubernetes

```bash
# 1. Enable MIG on nodes
# Run on each GPU node
sudo nvidia-smi -mig 1
sudo nvidia-smi mig -cgi 19,19,19,19 -C  # Create 4x 1g.5gb instances

# 2. Install GPU Operator with MIG support
helm install gpu-operator nvidia/gpu-operator \
  --set mig.strategy=mixed \
  --set operator.defaultRuntime=containerd

# 3. Label nodes with MIG config
kubectl label node gpu-node-1 nvidia.com/mig.config=all-1g.5gb

# 4. Deploy pods requesting MIG instances
apiVersion: v1
kind: Pod
metadata:
  name: mig-pod
spec:
  containers:
  - name: cuda
    image: nvidia/cuda:12.0-base
    resources:
      limits:
        nvidia.com/mig-1g.5gb: 1
```

### Fractional GPU with Third-Party Tools

**Volcano (CNCF project):**

```yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: gpu-queue
spec:
  reclaimable: true
  weight: 1
---
apiVersion: v1
kind: Pod
metadata:
  name: fractional-gpu-pod
spec:
  schedulerName: volcano
  containers:
  - name: training
    image: pytorch/pytorch
    resources:
      limits:
        nvidia.com/gpu-memory: 8192  # Request 8GB GPU memory
```

**Alibaba GPU Sharing:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-share-pod
spec:
  containers:
  - name: training
    image: tensorflow/tensorflow:latest-gpu
    resources:
      limits:
        aliyun.com/gpu-mem: 4  # Request 4GB GPU memory
```

## Use Cases and Trade-offs

### Use Case 1: Batch Inference

**Scenario**: Serving 10 different ML models, each with low QPS

**Solution**: MIG with 1g.5gb or 2g.10gb instances

```yaml
# Deploy each model to separate MIG instance
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-a-inference
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: inference
        image: model-a:latest
        resources:
          limits:
            nvidia.com/mig-1g.5gb: 1

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-b-inference
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: inference
        image: model-b:latest
        resources:
          limits:
            nvidia.com/mig-1g.5gb: 1
```

**Benefits**:
- Isolated resources per model
- Predictable latency
- Cost-efficient (7 models on 1 GPU)

### Use Case 2: Multi-Tenant Training

**Scenario**: 5 data science teams sharing GPU cluster

**Solution**: MIG with 3g.20gb or larger instances per team

```bash
# Create MIG instances per team
# Team A: 3g.20gb
# Team B: 3g.20gb
# Team C: 2g.10gb
# Remaining: 2g.10gb (shared pool)

nvidia-smi mig -cgi 9,9,7,7 -C
```

**Benefits**:
- Resource quotas enforced
- No noisy neighbor issues
- Fair sharing

### Use Case 3: Development/Testing

**Scenario**: Developers need GPUs for testing

**Solution**: Time-slicing with 4-8 shares per GPU

```yaml
# Kubernetes device plugin config
sharing:
  timeSlicing:
    replicas: 8
```

**Benefits**:
- Low overhead for setup
- Flexible sharing
- Sufficient for dev/test

### Use Case 4: High-Throughput Inference

**Scenario**: Single model serving with high QPS

**Solution**: MPS with multiple inference processes

```python
# inference_server.py
import torch
from concurrent.futures import ThreadPoolExecutor

model = load_model()

def handle_request(data):
    with torch.no_grad():
        return model(data)

# Multiple worker threads share GPU via MPS
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(handle_request, data) for data in requests]
```

```bash
# Start inference server with MPS
nvidia-cuda-mps-control -d
python inference_server.py
```

**Benefits**:
- Lower latency than time-slicing
- Better GPU utilization
- Simpler than MIG for single-model case

## Performance Isolation

### Memory Isolation

**MIG**: Hardware-enforced memory isolation
```bash
# MIG instance has fixed memory, cannot exceed
nvidia-smi mig -lgi
# Shows memory size per instance (5GB, 10GB, 20GB, etc.)
```

**MPS**: No memory isolation (use limits)
```bash
export CUDA_MPS_PINNED_DEVICE_MEM_LIMIT=0=4G
```

**Time-Slicing**: No memory isolation
```python
# Processes can OOM the GPU
# Must rely on application-level limits
```

### Compute Isolation

**MIG**: Dedicated SMs per instance
- No SM contention between instances
- Predictable performance

**MPS**: Shared SMs
- Kernels from different processes can run concurrently
- May have SM contention

**Time-Slicing**: Context switching
- Exclusive SM access during time slice
- But high overhead

### Fault Isolation

**MIG**: Isolated
- GPU error in one instance doesn't affect others
- Each instance has separate error tracking

**vGPU**: Isolated at VM level
- VM crash doesn't affect other VMs

**MPS/Time-Slicing**: Not isolated
- One process can crash entire GPU
- Error recovery affects all processes

### QoS Guarantees

**MIG**: Strong QoS
- Fixed resources (SMs, memory, L2)
- Guaranteed performance

**vGPU**: Good QoS
- Scheduler provides fairness
- Resource limits configurable

**MPS**: Weak QoS
- Best-effort sharing
- No guarantees

**Time-Slicing**: No QoS
- First-come, first-served
- No resource guarantees

## Summary

Key GPU virtualization takeaways:

1. **MIG is best for multi-tenant production**: Strong isolation, QoS, on A30/A100/H100
2. **vGPU for VMs**: Enterprise VM infrastructure with live migration
3. **MPS for inference**: Low latency, high throughput single-model serving
4. **Time-slicing for dev/test**: Simple setup, no isolation needed
5. **Profile before choosing**: Understand workload requirements first

## Hands-on Exercise

Set up and test MIG:

```bash
# 1. Enable MIG and create instances
sudo nvidia-smi -mig 1
sudo nvidia-smi mig -cgi 19,19 -C  # 2x 1g.5gb

# 2. Run workload on each instance
export CUDA_VISIBLE_DEVICES=MIG-xxx  # First instance
python train.py &

export CUDA_VISIBLE_DEVICES=MIG-yyy  # Second instance
python train.py &

# 3. Monitor utilization
nvidia-smi mig -lgi
watch -n 1 nvidia-smi

# TODO: Compare performance with and without MIG
# TODO: Test fault isolation (crash one instance)
```

## Further Reading

- NVIDIA MIG User Guide: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/
- NVIDIA vGPU Documentation: https://docs.nvidia.com/grid/
- Kubernetes Device Plugin: https://github.com/NVIDIA/k8s-device-plugin

---

**Next Lecture**: GPU Monitoring with NVIDIA DCGM
