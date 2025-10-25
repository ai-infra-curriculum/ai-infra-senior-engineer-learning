# Lab 03: Fault-Tolerant Training System

## Lab Overview

**Duration**: 3-4 hours  
**Difficulty**: Advanced  
**Prerequisites**: Labs 01-02, Python asyncio basics

Build a production-grade fault-tolerant distributed training system with automatic checkpointing, failure detection, and recovery.

## Learning Objectives

- Implement distributed checkpointing strategies
- Build automatic failure detection
- Create elastic training that handles node failures
- Test recovery from various failure scenarios
- Measure impact of checkpointing on performance
- Design production-ready fault tolerance

## Exercise 1: Implement Checkpointing Manager

### Task 1.1: Create Checkpoint Manager

```python
import torch
import torch.distributed as dist
from pathlib import Path
import time

class DistributedCheckpointManager:
    def __init__(self, checkpoint_dir, keep_last_n=3):
        # TODO: Implement initialization
        pass

    def save_checkpoint(self, model, optimizer, epoch, metrics):
        # TODO: Implement distributed checkpointing
        # Only rank 0 saves, others wait at barrier
        pass

    def load_checkpoint(self, model, optimizer, checkpoint_path=None):
        # TODO: Implement checkpoint loading
        # All ranks load and synchronize
        pass

    def cleanup_old_checkpoints(self):
        # TODO: Remove old checkpoints
        pass
```

**TODO**:
1. Implement all methods
2. Test save/load cycle
3. Verify state consistency across ranks

## Exercise 2: Failure Detection

### Task 2.1: Health Monitoring

```python
class HealthMonitor:
    def __init__(self, timeout_seconds=300):
        # TODO: Initialize health monitor
        pass

    def check_progress(self):
        # TODO: Check if training is making progress
        pass

    def detect_nan_inf(self, loss):
        # TODO: Detect NaN/Inf in loss
        pass

    def detect_oom(self):
        # TODO: Detect out-of-memory condition
        pass
```

### Task 2.2: Automatic Recovery

```python
def train_with_auto_recovery():
    checkpoint_mgr = DistributedCheckpointManager('./checkpoints')
    health_monitor = HealthMonitor()

    for epoch in range(num_epochs):
        try:
            # Training epoch
            metrics = train_epoch(model, train_loader, optimizer)

            # Health checks
            if health_monitor.detect_nan_inf(metrics['loss']):
                raise RuntimeError("NaN/Inf detected")

            if health_monitor.detect_oom():
                torch.cuda.empty_cache()

            # Save checkpoint
            checkpoint_mgr.save_checkpoint(model, optimizer, epoch, metrics)

        except Exception as e:
            print(f"Error: {e}. Attempting recovery...")
            # TODO: Implement recovery logic
            # 1. Load last checkpoint
            # 2. Synchronize state across ranks
            # 3. Continue training
            pass
```

**TODO**:
1. Implement recovery logic
2. Test recovery from NaN
3. Test recovery from node failure

## Exercise 3: Elastic Training

### Task 3.1: Dynamic Worker Scaling

Use Ray Train's elastic training:

```python
from ray import train
from ray.train.torch import TorchTrainer

def elastic_train_func(config):
    # Training function that handles changing world size
    rank = train.get_context().get_world_rank()
    world_size = train.get_context().get_world_size()

    # TODO: Implement training that adapts to world size changes
    for epoch in range(config['num_epochs']):
        current_world_size = train.get_context().get_world_size()
        if current_world_size != world_size:
            print(f"World size changed: {world_size} → {current_world_size}")
            # TODO: Handle world size change
        # Train epoch
        pass

trainer = TorchTrainer(
    elastic_train_func,
    scaling_config=train.ScalingConfig(
        num_workers=4,
        use_gpu=True,
    ),
    run_config=train.RunConfig(
        failure_config=train.FailureConfig(max_failures=3),
    ),
)
```

### Task 3.2: Test Elastic Scaling

**TODO**: Test scenarios:
1. Start with 4 workers
2. Kill 1 worker during training
3. Verify training continues with 3 workers
4. Add 2 new workers
5. Verify training scales to 5 workers

Record results:
- Initial world size: __________
- After failure: __________
- After scale-up: __________
- Training continuity: __________

## Exercise 4: Failure Scenarios

Test recovery from various failure modes.

### Test Case 1: Single Node Failure

```bash
# Start training with 4 workers
python train_fault_tolerant.py

# Kill one worker pod
kubectl delete pod ray-cluster-worker-xxxxx

# Observe automatic recovery
```

**TODO**: Record metrics:
- Time to detect failure: __________
- Time to recover: __________
- Training epochs lost: __________

### Test Case 2: Network Partition

Simulate network partition and test recovery.

**TODO**: Test and document recovery process

### Test Case 3: OOM Recovery

Trigger OOM and test automatic recovery with reduced batch size.

**TODO**: Implement and test OOM recovery

## Exercise 5: Checkpoint Performance Analysis

Measure checkpointing overhead.

### Task 5.1: Benchmark Checkpointing

```python
def benchmark_checkpointing():
    # Measure time without checkpointing
    start = time.time()
    for epoch in range(10):
        train_epoch_no_checkpoint()
    time_no_checkpoint = time.time() - start

    # Measure time with checkpointing every epoch
    start = time.time()
    for epoch in range(10):
        train_epoch_with_checkpoint()
    time_with_checkpoint = time.time() - start

    overhead = (time_with_checkpoint - time_no_checkpoint) / time_no_checkpoint * 100
    print(f"Checkpointing overhead: {overhead:.1f}%")
```

**TODO**: Complete performance analysis:

| Checkpoint Frequency | Training Time | Overhead | Recovery Time |
|---------------------|---------------|----------|---------------|
| Every epoch         |               |          |               |
| Every 5 epochs      |               |          |               |
| Every 10 epochs     |               |          |               |

## Challenge Exercise: Production System

Build complete production-grade fault-tolerant training system:

**Requirements**:
1. Automatic checkpointing with configurable frequency
2. Health monitoring and alerting
3. Automatic recovery from failures
4. Elastic scaling support
5. Metrics logging and monitoring
6. Integration with monitoring systems (Prometheus)

**Deliverables**:
1. Complete implementation
2. Test results from all failure scenarios
3. Performance analysis report
4. Production deployment guide
5. 1000-word architecture document

---

**Estimated Time**: 3-4 hours  
**Difficulty**: Advanced
