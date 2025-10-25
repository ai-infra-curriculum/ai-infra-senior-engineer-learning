# Lab 03: GPU Sharing with Multi-Instance GPU (MIG)

## Lab Overview

**Duration**: 2-3 hours
**Difficulty**: Intermediate
**Prerequisites**: Lecture 06 (GPU Virtualization), Access to A100 or H100 GPU

In this lab, you will configure and use NVIDIA MIG to partition a single GPU into multiple isolated instances for multi-tenant workloads.

## Learning Objectives

1. Enable and configure MIG on A100/H100 GPUs
2. Create different MIG instance profiles
3. Deploy containerized workloads to MIG instances
4. Implement resource isolation and QoS
5. Monitor MIG instance utilization

## Lab Requirements

### Hardware
- NVIDIA A100 (40GB or 80GB) or H100 GPU
- OR access to cloud instance (AWS P4d, Google Cloud A2)

### Software
- NVIDIA Driver 450.80.02+ (for A100)
- nvidia-smi with MIG support
- Docker with NVIDIA Container Toolkit
- Kubernetes (optional, for Part 4)

## Part 1: MIG Configuration Basics

### Exercise 1.1: Enable MIG Mode

**Task**: Enable MIG on GPU 0

```bash
# Check current MIG mode
nvidia-smi -i 0 --query-gpu=mig.mode.current --format=csv,noheader

# TODO: Enable MIG mode
sudo nvidia-smi -i 0 -mig 1

# Reset GPU (may require reboot on some systems)
sudo nvidia-smi -i 0 --gpu-reset

# Verify MIG is enabled
nvidia-smi -i 0 --query-gpu=mig.mode.current --format=csv,noheader
# Expected output: Enabled

# TODO: Document any errors encountered
```

### Exercise 1.2: Explore MIG Profiles

**Task**: List available MIG profiles for your GPU

```bash
# List GPU instance profiles
nvidia-smi mig -lgip

# TODO: Document output
# Example for A100 40GB:
# +-----------------------------------------------------------------------------+
# | GPU instance profiles:                                                      |
# | GPU   Name             ID    Instances   Memory     P2P    SM    DEC   ENC  |
# |                              Free/Total   GiB              CE    JPEG  OFA  |
# |=============================================================================|
# |   0  MIG 1g.5gb        19     7/7        4.75       No    14     0     0   |
# |                                                             1     0     0   |
# +-----------------------------------------------------------------------------+
# |   0  MIG 2g.10gb        14     3/3        9.75       No    28     1     0   |
# |                                                             2     0     0   |
# +-----------------------------------------------------------------------------+
# ...

# TODO: Answer these questions:
# 1. How many 1g.5gb instances can you create?
# 2. What is the memory per instance for 3g.20gb?
# 3. How many SMs does a 2g.10gb instance have?
```

## Part 2: Creating and Managing MIG Instances

### Exercise 2.1: Create Uniform MIG Configuration

**Task**: Create 7x 1g.5gb instances (maximum partitioning)

```bash
# TODO: Create GPU instances
# Profile ID 19 = 1g.5gb
sudo nvidia-smi mig -cgi 19,19,19,19,19,19,19 -C

# Verify creation
nvidia-smi mig -lgi

# Expected output shows 7 instances
# +-------------------------------------------------------+
# | GPU instances:                                        |
# | GPU   GI   CI   Profile                     Placement |
# |=======================================================|
# |   0    0    0   MIG 1g.5gb                        0   |
# |   0    1    0   MIG 1g.5gb                        1   |
# ...

# List MIG devices
nvidia-smi -L
# Expected: GPU 0: ... with 7 MIG device entries

# TODO: Document the UUID of each MIG instance
```

### Exercise 2.2: Create Mixed Configuration

**Task**: Create a mixed configuration (1x 3g + 2x 2g)

```bash
# First, destroy existing instances
sudo nvidia-smi mig -dci  # Destroy compute instances
sudo nvidia-smi mig -dgi  # Destroy GPU instances

# TODO: Create mixed configuration
# Profile 9 = 3g.20gb, Profile 14 = 2g.10gb
sudo nvidia-smi mig -cgi 9,14,14 -C

# Verify
nvidia-smi mig -lgi

# TODO: Document the configuration:
# Instance 0: ___ SMs, ___ GB memory
# Instance 1: ___ SMs, ___ GB memory  
# Instance 2: ___ SMs, ___ GB memory
```

### Exercise 2.3: MIG Instance Selection

**Task**: Run workloads on specific MIG instances

**test_mig.py:**
```python
import torch
import os

def test_mig_instance():
    """Test GPU access within MIG instance"""
    
    print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not set')}")
    
    # Check GPU availability
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available!")
        return
    
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    
    # Get GPU properties
    props = torch.cuda.get_device_properties(0)
    print(f"\nGPU Properties:")
    print(f"  Name: {props.name}")
    print(f"  Total memory: {props.total_memory / 1e9:.2f} GB")
    print(f"  Multiprocessors: {props.multi_processor_count}")
    print(f"  Compute capability: {props.major}.{props.minor}")
    
    # Allocate memory
    try:
        # Try to allocate 80% of available memory
        available = torch.cuda.get_device_properties(0).total_memory
        tensor_size = int(available * 0.8 / 4)  # float32 = 4 bytes
        tensor = torch.randn(tensor_size, device='cuda')
        print(f"\nSuccessfully allocated {tensor_size * 4 / 1e9:.2f} GB")
        
        # Simple computation
        result = tensor.sum()
        print(f"Computation successful: sum = {result.item():.2f}")
        
    except RuntimeError as e:
        print(f"\nAllocation failed: {e}")

if __name__ == "__main__":
    test_mig_instance()
```

**Run on different MIG instances:**
```bash
# Get MIG UUIDs
nvidia-smi -L

# TODO: Run on instance 0 (1g.5gb)
export CUDA_VISIBLE_DEVICES=MIG-<UUID-of-instance-0>
python test_mig.py

# TODO: Run on instance 1 (2g.10gb)
export CUDA_VISIBLE_DEVICES=MIG-<UUID-of-instance-1>
python test_mig.py

# TODO: Compare output
# Instance 0 memory: ___ GB
# Instance 1 memory: ___ GB
```

## Part 3: Multi-Tenant Workload Isolation

### Exercise 3.1: Run Concurrent Workloads

**Task**: Run multiple training jobs on different MIG instances simultaneously

**training_job.py:**
```python
import torch
import torch.nn as nn
import time
import sys

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1024, 4096),
            nn.ReLU(),
            nn.Linear(4096, 4096),
            nn.ReLU(),
            nn.Linear(4096, 1024)
        )
    
    def forward(self, x):
        return self.layers(x)

def train_loop(job_id, num_iterations=1000):
    """Simulate training workload"""
    
    print(f"Job {job_id}: Starting on GPU {torch.cuda.current_device()}")
    
    model = SimpleModel().cuda()
    optimizer = torch.optim.Adam(model.parameters())
    
    # Training loop
    start_time = time.time()
    for i in range(num_iterations):
        data = torch.randn(128, 1024).cuda()
        
        output = model(data)
        loss = output.sum()
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if i % 100 == 0:
            print(f"Job {job_id}: Iteration {i}, Loss: {loss.item():.4f}")
    
    elapsed = time.time() - start_time
    throughput = num_iterations / elapsed
    
    print(f"Job {job_id}: Completed. Throughput: {throughput:.2f} iter/sec")
    return throughput

if __name__ == "__main__":
    job_id = sys.argv[1] if len(sys.argv) > 1 else "0"
    train_loop(job_id)
```

**Launch script:**
```bash
#!/bin/bash
# run_concurrent_jobs.sh

# TODO: Get MIG UUIDs
MIG_INSTANCE_0="MIG-<UUID-0>"
MIG_INSTANCE_1="MIG-<UUID-1>"
MIG_INSTANCE_2="MIG-<UUID-2>"

# Launch jobs on different MIG instances
CUDA_VISIBLE_DEVICES=$MIG_INSTANCE_0 python training_job.py job_0 &
CUDA_VISIBLE_DEVICES=$MIG_INSTANCE_1 python training_job.py job_1 &
CUDA_VISIBLE_DEVICES=$MIG_INSTANCE_2 python training_job.py job_2 &

# Wait for completion
wait

echo "All jobs completed"
```

**Run and monitor:**
```bash
# Terminal 1: Launch jobs
./run_concurrent_jobs.sh

# Terminal 2: Monitor GPU usage
watch -n 1 nvidia-smi mig -i 0 -lgi

# TODO: Document observations:
# - Are instances isolated?
# - Does one job affect others?
# - What is the utilization per instance?
```

### Exercise 3.2: Test Fault Isolation

**Task**: Verify that errors in one instance don't affect others

**crash_test.py:**
```python
import torch
import sys

def cause_oom():
    """Intentionally cause OOM error"""
    try:
        # Try to allocate more memory than available
        huge_tensor = torch.randn(10**10, device='cuda')
    except RuntimeError as e:
        print(f"Expected OOM error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cause_oom()
```

**Test isolation:**
```bash
# Launch normal job on instance 0
CUDA_VISIBLE_DEVICES=MIG-<UUID-0> python training_job.py job_0 &

# Launch crash job on instance 1
CUDA_VISIBLE_DEVICES=MIG-<UUID-1> python crash_test.py

# TODO: Verify that job_0 continues running
# Check with: ps aux | grep training_job

# Expected: job_0 unaffected by crash in instance 1
```

## Part 4: MIG with Docker

### Exercise 4.1: Docker with MIG Support

**Task**: Run containerized workloads on MIG instances

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.0.0-cuda11.8-cudnn8-runtime

WORKDIR /workspace

COPY training_job.py .

CMD ["python", "training_job.py"]
```

**Build and run:**
```bash
# Build image
docker build -t mig-training .

# TODO: Run container on MIG instance 0
docker run --rm --gpus '"device=MIG-<UUID-0>"' mig-training

# TODO: Run multiple containers on different instances
docker run -d --name job0 --gpus '"device=MIG-<UUID-0>"' mig-training
docker run -d --name job1 --gpus '"device=MIG-<UUID-1>"' mig-training
docker run -d --name job2 --gpus '"device=MIG-<UUID-2>"' mig-training

# Monitor containers
docker ps
docker logs job0

# Cleanup
docker rm -f job0 job1 job2
```

### Exercise 4.2: Docker Compose for Multi-Instance

**docker-compose.yml:**
```yaml
version: '3'
services:
  training-job-0:
    image: mig-training
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['MIG-<UUID-0>']
              capabilities: [gpu]
    environment:
      - JOB_ID=0

  training-job-1:
    image: mig-training
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['MIG-<UUID-1>']
              capabilities: [gpu]
    environment:
      - JOB_ID=1

# TODO: Add more services for additional MIG instances
```

**Run:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Part 5: MIG Monitoring and Metrics

### Exercise 5.1: Collect MIG Metrics

**Task**: Monitor MIG instance utilization

**monitor_mig.sh:**
```bash
#!/bin/bash

echo "MIG Instance Monitoring"
echo "======================"
echo ""

while true; do
    clear
    echo "Timestamp: $(date)"
    echo ""
    
    # TODO: Display MIG instance info
    nvidia-smi mig -lgi
    
    echo ""
    echo "Per-Instance Utilization:"
    # TODO: Query per-instance metrics
    nvidia-smi --query-gpu=mig.mode.current --format=csv
    
    echo ""
    echo "Active Processes:"
    nvidia-smi pmon -c 1
    
    sleep 2
done
```

### Exercise 5.2: Export Metrics to Prometheus

**Task**: Use DCGM Exporter with MIG

```bash
# Run DCGM Exporter with MIG support
docker run -d --name dcgm-exporter \
    --gpus all \
    --rm \
    -p 9400:9400 \
    nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04

# Check metrics
curl http://localhost:9400/metrics | grep DCGM_FI_DEV_GPU_UTIL

# TODO: Verify MIG instance metrics are exposed
# Each MIG instance should have separate metric labels
```

## Part 6: Best Practices and Cleanup

### Exercise 6.1: Right-Sizing Workloads

**Task**: Determine optimal MIG profile for different workloads

**benchmark_profiles.py:**
```python
import torch
import time

def benchmark_model(model_size):
    """Benchmark model on current MIG instance"""
    
    # Define model based on size
    if model_size == 'small':
        layers = [1024, 2048, 1024]
    elif model_size == 'medium':
        layers = [2048, 4096, 2048]
    elif model_size == 'large':
        layers = [4096, 8192, 4096]
    
    # TODO: Build and benchmark model
    # Measure:
    # - Peak memory usage
    # - Throughput (samples/sec)
    # - Success/Failure (OOM)
    
    return results

# TODO: Test each model size on different MIG profiles
# Document minimum required profile for each model
```

### Exercise 6.2: Cleanup and Reset

**Task**: Return GPU to normal mode

```bash
# Destroy all MIG instances
sudo nvidia-smi mig -dci
sudo nvidia-smi mig -dgi

# Disable MIG mode
sudo nvidia-smi -i 0 -mig 0

# Reset GPU
sudo nvidia-smi -i 0 --gpu-reset

# Verify normal mode
nvidia-smi
```

## Deliverables

Submit:

1. **Configuration Screenshots**:
   - MIG enabled
   - Different profile configurations
   - Running workloads

2. **Performance Analysis**:
   - Concurrent job throughput
   - Isolation verification results
   - Resource utilization charts

3. **Best Practices Document**:
   - Profile selection guidelines
   - Resource allocation strategies
   - Monitoring approach

4. **Use Case Recommendations**:
   - When to use MIG vs. time-slicing
   - Profile sizing for common workloads
   - Multi-tenant deployment patterns

## Bonus Challenges

1. **Kubernetes Integration**: Deploy MIG-enabled cluster with GPU Operator
2. **Dynamic Reconfiguration**: Script to change MIG config without downtime
3. **Cost Analysis**: Calculate cost savings of MIG vs. dedicated GPUs
4. **Advanced Monitoring**: Build Grafana dashboard for MIG metrics

## Troubleshooting Guide

**Common Issues:**

1. **MIG Not Supported**: Check GPU model and driver version
2. **Cannot Enable MIG**: May require system reboot
3. **Profile Creation Fails**: Check for conflicting profiles
4. **Container Access Issues**: Verify NVIDIA Container Toolkit version

---

**Success Criteria**: Successfully partition GPU, run isolated workloads, and demonstrate resource efficiency gains with MIG.
