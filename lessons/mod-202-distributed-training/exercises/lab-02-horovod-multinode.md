# Lab 02: Multi-Node Training with Horovod

## Lab Overview

**Duration**: 3-4 hours
**Difficulty**: Advanced
**Prerequisites**: Lab 01 completion, MPI basics, multi-node cluster access

In this lab, you'll implement multi-node distributed training using Horovod with MPI. You'll learn to configure InfiniBand/RDMA, optimize communication, and benchmark performance at scale.

## Learning Objectives

- Deploy Horovod on multi-node Kubernetes cluster
- Configure NCCL and InfiniBand for optimal performance
- Implement data-parallel training with Horovod
- Measure and optimize communication overhead
- Compare Horovod vs Ray Train performance
- Troubleshoot distributed training issues

## Prerequisites

- Multi-node Kubernetes cluster (2+ nodes)
- InfiniBand or 10GbE+ networking
- NVIDIA GPUs with NCCL support
- MPI installation (OpenMPI or Intel MPI)
- Completed Lab 01

## Exercise 1: Deploy Horovod on Kubernetes

### Task 1.1: Install MPI Operator

```bash
# Install Kubeflow MPI Operator
kubectl apply -f https://raw.githubusercontent.com/kubeflow/mpi-operator/master/deploy/v2beta1/mpi-operator.yaml

# Verify
kubectl get pods -n mpi-operator
```

### Task 1.2: Create Horovod Training Job

Create `horovod-job.yaml`:

```yaml
apiVersion: kubeflow.org/v2beta1
kind: MPIJob
metadata:
  name: horovod-cifar10
spec:
  slotsPerWorker: 1
  runPolicy:
    cleanPodPolicy: Running

  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
        spec:
          containers:
          - name: horovod-launcher
            image: horovod/horovod:latest
            command:
            - mpirun
            args:
            - -np
            - "4"
            - --allow-run-as-root
            - -bind-to
            - none
            - -map-by
            - slot
            - -x
            - NCCL_DEBUG=INFO
            - -x
            - LD_LIBRARY_PATH
            - -x
            - PATH
            - python
            - /workspace/train_horovod.py
            volumeMounts:
            - name: workspace
              mountPath: /workspace
          volumes:
          - name: workspace
            persistentVolumeClaim:
              claimName: shared-storage

    Worker:
      replicas: 4
      template:
        spec:
          containers:
          - name: horovod-worker
            image: horovod/horovod:latest
            resources:
              limits:
                nvidia.com/gpu: 1
            volumeMounts:
            - name: workspace
              mountPath: /workspace
          volumes:
          - name: workspace
            persistentVolumeClaim:
              claimName: shared-storage
```

### Task 1.3: Create Training Script

Create `train_horovod.py`:

```python
import torch
import torch.nn as nn
import horovod.torch as hvd
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
import time

# Initialize Horovod
hvd.init()

# Pin GPU to local rank
torch.cuda.set_device(hvd.local_rank())

# Model (same as Lab 01)
class SimpleCNN(nn.Module):
    # TODO: Implement model
    pass

def train():
    # TODO: Implement training with Horovod
    # 1. Scale learning rate by hvd.size()
    # 2. Wrap optimizer with hvd.DistributedOptimizer
    # 3. Broadcast initial parameters
    # 4. Use DistributedSampler
    # 5. Train and measure performance
    pass

if __name__ == '__main__':
    train()
```

**TODO Tasks**:
1. Complete the training script
2. Deploy the MPIJob
3. Monitor training progress
4. Record performance metrics

**Expected Metrics**:
- Training time: __________
- Throughput: __________
- GPU utilization: __________%

## Exercise 2: NCCL and Network Optimization

### Task 2.1: Benchmark Network Performance

```bash
# Run NCCL tests
kubectl apply -f nccl-tests-job.yaml

# Monitor results
kubectl logs -f nccl-tests-xxxxx
```

### Task 2.2: Configure NCCL for InfiniBand

Update MPIJob with NCCL environment variables:

```yaml
env:
- name: NCCL_IB_DISABLE
  value: "0"
- name: NCCL_IB_HCA
  value: "mlx5_0,mlx5_1"
- name: NCCL_IB_GID_INDEX
  value: "3"
- name: NCCL_SOCKET_IFNAME
  value: "ib0"
- name: NCCL_DEBUG
  value: "INFO"
```

**TODO**: Measure impact of optimizations
- Baseline bandwidth: __________
- Optimized bandwidth: __________
- Improvement: __________%

## Exercise 3: Performance Profiling

Profile Horovod training to identify bottlenecks.

### Task 3.1: Add Profiling Code

```python
import nvtx

def train_with_profiling():
    for epoch in range(num_epochs):
        nvtx.range_push(f"Epoch {epoch}")

        for batch_idx, batch in enumerate(train_loader):
            nvtx.range_push("Data Loading")
            data, target = batch
            nvtx.range_pop()

            nvtx.range_push("Forward")
            output = model(data)
            nvtx.range_pop()

            nvtx.range_push("Backward")
            loss.backward()
            nvtx.range_pop()

            nvtx.range_push("AllReduce")
            optimizer.step()
            nvtx.range_pop()

        nvtx.range_pop()
```

### Task 3.2: Collect Profiles

```bash
# Run with Nsight Systems
nsys profile -o horovod_profile python train_horovod.py
```

**TODO**: Analyze profile
1. What is the communication overhead? __________%
2. Is GPU compute overlapping with communication? __________
3. Identify top 3 bottlenecks

## Exercise 4: Scaling Study

Conduct systematic scaling study.

**TODO**: Complete scaling table

| Workers | Time/Epoch | Throughput | Speedup | Efficiency | Comm Time |
|---------|-----------|------------|---------|------------|-----------|
| 1       |           |            | 1.0x    | 100%       | 0%        |
| 2       |           |            |         |            |           |
| 4       |           |            |         |            |           |
| 8       |           |            |         |            |           |

## Challenge: Horovod Timeline

Generate and analyze Horovod timeline.

```python
# Enable timeline
hvd.init()
with hvd.timeline_context(filename='timeline.json'):
    train()

# Analyze with Chrome tracing (chrome://tracing)
```

**TODO**: 
1. Generate timeline
2. Identify communication patterns
3. Suggest 3 optimizations

## Lab Deliverables

1. Complete training scripts
2. Performance comparison report
3. Profiling analysis
4. Scaling study results
5. 750-word reflection on Horovod vs Ray Train

---

**Estimated Time**: 3-4 hours
**Difficulty**: Advanced
