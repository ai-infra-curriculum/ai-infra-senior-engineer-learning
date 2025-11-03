# Lecture 06: Fault Tolerance and Checkpointing

## Learning Objectives

By the end of this lecture, you will be able to:

- Design fault-tolerant distributed training systems that can detect, recover from, and continue training after hardware, software, and transient failures
- Implement comprehensive checkpointing strategies including incremental, sharded, and distributed checkpointing for large-scale models
- Configure elastic training systems that dynamically adapt to changing cluster sizes with worker addition and removal during training
- Implement automatic failure detection mechanisms for identifying GPU failures, network disconnections, NaN/Inf errors, and training hangs
- Design state consistency verification and synchronization protocols to ensure all workers maintain identical model and optimizer states
- Implement emergency checkpoint mechanisms and watchdog systems that preserve training state during unexpected interruptions
- Calculate failure probability for large-scale training runs and design appropriate checkpoint frequency strategies
- Build production-ready fault-tolerant trainers with automatic recovery, state verification, and minimal training interruption

## Table of Contents

1. [Introduction to Fault Tolerance](#introduction)
2. [Checkpointing Strategies](#checkpointing-strategies)
3. [Elastic Training](#elastic-training)
4. [Failure Detection and Recovery](#failure-detection)
5. [State Consistency](#state-consistency)
6. [Distributed Checkpointing](#distributed-checkpointing)
7. [Production Best Practices](#best-practices)

## Introduction to Fault Tolerance

In large-scale distributed training, failures are inevitable. A fault-tolerant system can detect failures, recover training state, and continue with minimal interruption.

### Why Fault Tolerance Matters

```python
# Calculate probability of failure during training
import math

def calculate_failure_probability(
    num_nodes,
    hours_training,
    mtbf_hours=100000  # Mean Time Between Failures per node
):
    """
    Calculate probability of at least one failure during training

    Args:
        num_nodes: Number of compute nodes
        hours_training: Training duration in hours
        mtbf_hours: MTBF for single node

    Returns:
        Probability of at least one failure
    """
    # Failure rate per node per hour
    lambda_rate = 1.0 / mtbf_hours

    # Probability no failures for one node
    prob_no_fail_single = math.exp(-lambda_rate * hours_training)

    # Probability no failures across all nodes
    prob_no_fail_all = prob_no_fail_single ** num_nodes

    # Probability of at least one failure
    prob_failure = 1 - prob_no_fail_all

    return prob_failure

# Examples
scenarios = [
    (8, 24, "Single DGX node, 1 day"),
    (64, 168, "64 nodes, 1 week"),
    (256, 720, "256 nodes, 1 month"),
    (1024, 2160, "1024 nodes, 3 months"),
]

print("Failure Probability Analysis:")
print("=" * 70)
print(f"{'Scenario':<30} {'Failure Prob':<20} {'Expected Failures'}")
print("-" * 70)

for num_nodes, hours, desc in scenarios:
    prob = calculate_failure_probability(num_nodes, hours)
    expected_failures = prob * num_nodes

    print(f"{desc:<30} {prob*100:>6.2f}%              "
          f"{expected_failures:>6.2f}")

print("=" * 70)
print("\n⚠ Conclusion: Fault tolerance is ESSENTIAL for large-scale training!\n")
```

### Types of Failures

```
┌───────────────────────────────────────────────────────────────┐
│                    Common Failure Types                        │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Hardware Failures:                                        │
│     - GPU failure or hang                                     │
│     - Node crash (OOM, kernel panic)                          │
│     - Network disconnection                                   │
│     - Storage failures                                        │
│                                                                │
│  2. Software Failures:                                        │
│     - Out of memory (OOM)                                     │
│     - Numerical instability (NaN/Inf)                         │
│     - Deadlock in distributed communication                   │
│     - Library bugs                                            │
│                                                                │
│  3. Transient Failures:                                       │
│     - Network congestion                                      │
│     - Temporary GPU errors                                    │
│     - Process preemption (spot instances)                     │
│                                                                │
│  4. Systematic Failures:                                      │
│     - Bad data in dataset                                     │
│     - Gradient explosion                                      │
│     - Configuration errors                                    │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## Checkpointing Strategies

### Basic Checkpointing

```python
import torch
import torch.distributed as dist
import os
from pathlib import Path
import time

class CheckpointManager:
    """
    Checkpoint manager for distributed training
    """

    def __init__(self, checkpoint_dir, keep_last_n=3):
        """
        Args:
            checkpoint_dir: Directory to save checkpoints
            keep_last_n: Number of checkpoints to keep
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.keep_last_n = keep_last_n
        self.checkpoints = []

    def save_checkpoint(self, model, optimizer, scheduler, epoch, metrics, step=None):
        """
        Save checkpoint (only on rank 0 in distributed training)

        Args:
            model: Model to save
            optimizer: Optimizer state
            scheduler: LR scheduler state
            epoch: Current epoch
            metrics: Training metrics dict
            step: Current step (optional)
        """
        # Only rank 0 saves checkpoint
        if dist.is_initialized() and dist.get_rank() != 0:
            dist.barrier()  # Wait for rank 0
            return

        # Create checkpoint filename
        if step is not None:
            filename = f"checkpoint_epoch_{epoch}_step_{step}.pt"
        else:
            filename = f"checkpoint_epoch_{epoch}.pt"

        checkpoint_path = self.checkpoint_dir / filename

        # Prepare checkpoint dict
        checkpoint = {
            'epoch': epoch,
            'step': step,
            'model_state_dict': self._get_model_state(model),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
            'metrics': metrics,
            'timestamp': time.time(),
        }

        # Save checkpoint
        print(f"Saving checkpoint: {checkpoint_path}")
        torch.save(checkpoint, checkpoint_path)

        # Track checkpoints
        self.checkpoints.append(checkpoint_path)

        # Remove old checkpoints
        self._cleanup_old_checkpoints()

        # Save "latest" symlink
        latest_path = self.checkpoint_dir / "latest.pt"
        if latest_path.exists():
            latest_path.unlink()
        latest_path.symlink_to(filename)

        # Wait for all ranks
        if dist.is_initialized():
            dist.barrier()

    def _get_model_state(self, model):
        """Get model state dict (handle DDP/FSDP wrapping)"""
        if hasattr(model, 'module'):
            # Unwrap DDP/FSDP
            return model.module.state_dict()
        else:
            return model.state_dict()

    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints, keeping only last N"""
        if len(self.checkpoints) > self.keep_last_n:
            # Sort by modification time
            self.checkpoints.sort(key=lambda p: p.stat().st_mtime)

            # Remove oldest
            while len(self.checkpoints) > self.keep_last_n:
                old_checkpoint = self.checkpoints.pop(0)
                if old_checkpoint.exists():
                    print(f"Removing old checkpoint: {old_checkpoint}")
                    old_checkpoint.unlink()

    def load_checkpoint(self, model, optimizer=None, scheduler=None, checkpoint_path=None):
        """
        Load checkpoint

        Args:
            model: Model to load weights into
            optimizer: Optimizer to load state (optional)
            scheduler: Scheduler to load state (optional)
            checkpoint_path: Path to checkpoint (if None, loads latest)

        Returns:
            Dictionary with checkpoint info
        """
        # Determine checkpoint path
        if checkpoint_path is None:
            latest_path = self.checkpoint_dir / "latest.pt"
            if not latest_path.exists():
                raise FileNotFoundError("No checkpoint found")
            checkpoint_path = latest_path

        print(f"Loading checkpoint: {checkpoint_path}")

        # Load checkpoint
        # Map to appropriate device
        if dist.is_initialized():
            rank = dist.get_rank()
            map_location = f'cuda:{rank}'
        else:
            map_location = 'cuda' if torch.cuda.is_available() else 'cpu'

        checkpoint = torch.load(checkpoint_path, map_location=map_location)

        # Load model state
        if hasattr(model, 'module'):
            model.module.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint['model_state_dict'])

        # Load optimizer state
        if optimizer is not None and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # Load scheduler state
        if scheduler is not None and 'scheduler_state_dict' in checkpoint:
            if checkpoint['scheduler_state_dict'] is not None:
                scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        # Synchronize all ranks
        if dist.is_initialized():
            dist.barrier()

        return {
            'epoch': checkpoint['epoch'],
            'step': checkpoint.get('step'),
            'metrics': checkpoint['metrics'],
        }

    def list_checkpoints(self):
        """List all available checkpoints"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.pt"))
        return checkpoints

# Usage example
def train_with_checkpointing():
    """Example training loop with checkpointing"""
    # Setup
    model = create_model()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

    checkpoint_mgr = CheckpointManager(
        checkpoint_dir="./checkpoints",
        keep_last_n=3
    )

    # Try to resume from checkpoint
    start_epoch = 0
    try:
        info = checkpoint_mgr.load_checkpoint(model, optimizer, scheduler)
        start_epoch = info['epoch'] + 1
        print(f"Resumed from epoch {info['epoch']}")
    except FileNotFoundError:
        print("Starting from scratch")

    # Training loop
    for epoch in range(start_epoch, num_epochs):
        # Train epoch
        metrics = train_epoch(model, train_loader, optimizer)

        # Step scheduler
        scheduler.step()

        # Save checkpoint every N epochs
        if epoch % 5 == 0:
            checkpoint_mgr.save_checkpoint(
                model, optimizer, scheduler,
                epoch, metrics
            )

        # Also save best checkpoint
        if metrics['val_loss'] < best_loss:
            best_loss = metrics['val_loss']
            checkpoint_mgr.save_checkpoint(
                model, optimizer, scheduler,
                epoch, metrics, step='best'
            )
```

### Incremental Checkpointing

```python
class IncrementalCheckpointManager:
    """
    Incremental checkpointing - only save what changed
    Useful for very large models
    """

    def __init__(self, checkpoint_dir):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.last_model_hash = None

    def save_incremental_checkpoint(self, model, optimizer, epoch, force_full=False):
        """
        Save incremental checkpoint

        Only saves model weights if they changed significantly
        Always saves optimizer state (smaller)
        """
        import hashlib

        # Calculate hash of model parameters
        model_state = self._get_model_state(model)
        current_hash = self._calculate_state_hash(model_state)

        # Check if model changed significantly
        model_changed = (current_hash != self.last_model_hash) or force_full

        checkpoint = {
            'epoch': epoch,
            'optimizer_state_dict': optimizer.state_dict(),
            'model_hash': current_hash,
        }

        if model_changed:
            # Save full model
            checkpoint['model_state_dict'] = model_state
            checkpoint['full_checkpoint'] = True
            self.last_model_hash = current_hash
            print(f"Saving full checkpoint (model changed)")
        else:
            # Only save optimizer state
            checkpoint['full_checkpoint'] = False
            checkpoint['model_checkpoint_path'] = self._get_last_model_path()
            print(f"Saving incremental checkpoint (model unchanged)")

        # Save checkpoint
        checkpoint_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)

        return checkpoint_path

    def _calculate_state_hash(self, state_dict):
        """Calculate hash of model state"""
        import hashlib

        # Create hash from parameter values
        hash_md5 = hashlib.md5()
        for key in sorted(state_dict.keys()):
            hash_md5.update(key.encode())
            hash_md5.update(state_dict[key].cpu().numpy().tobytes())

        return hash_md5.hexdigest()

    def _get_model_state(self, model):
        """Get model state dict"""
        if hasattr(model, 'module'):
            return model.module.state_dict()
        else:
            return model.state_dict()

    def _get_last_model_path(self):
        """Get path to last full model checkpoint"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_*.pt"))
        for cp in reversed(checkpoints):
            checkpoint = torch.load(cp, map_location='cpu')
            if checkpoint.get('full_checkpoint', False):
                return cp
        return None
```

### Sharded Checkpointing

```python
class ShardedCheckpointManager:
    """
    Sharded checkpointing for very large models
    Each rank saves its own shard
    """

    def __init__(self, checkpoint_dir, world_size, rank):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.world_size = world_size
        self.rank = rank

    def save_sharded_checkpoint(self, model, optimizer, epoch):
        """
        Save checkpoint sharded across ranks

        Each rank saves its own portion of the model
        """
        # Create epoch directory
        epoch_dir = self.checkpoint_dir / f"epoch_{epoch}"
        epoch_dir.mkdir(exist_ok=True)

        # Save this rank's shard
        shard_path = epoch_dir / f"rank_{self.rank}.pt"

        checkpoint = {
            'epoch': epoch,
            'rank': self.rank,
            'world_size': self.world_size,
            'model_state_dict': self._get_model_state(model),
            'optimizer_state_dict': optimizer.state_dict(),
        }

        torch.save(checkpoint, shard_path)
        print(f"Rank {self.rank}: Saved shard to {shard_path}")

        # Synchronize all ranks
        dist.barrier()

        # Rank 0: Create metadata file
        if self.rank == 0:
            metadata = {
                'epoch': epoch,
                'world_size': self.world_size,
                'timestamp': time.time(),
            }
            metadata_path = epoch_dir / "metadata.json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)

        dist.barrier()

    def load_sharded_checkpoint(self, model, optimizer, epoch):
        """
        Load sharded checkpoint

        Each rank loads its own shard
        """
        epoch_dir = self.checkpoint_dir / f"epoch_{epoch}"
        shard_path = epoch_dir / f"rank_{self.rank}.pt"

        if not shard_path.exists():
            raise FileNotFoundError(f"Shard not found: {shard_path}")

        print(f"Rank {self.rank}: Loading shard from {shard_path}")

        checkpoint = torch.load(
            shard_path,
            map_location=f'cuda:{self.rank}'
        )

        # Verify shard metadata
        assert checkpoint['rank'] == self.rank
        assert checkpoint['world_size'] == self.world_size

        # Load states
        if hasattr(model, 'module'):
            model.module.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint['model_state_dict'])

        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # Synchronize
        dist.barrier()

        return checkpoint['epoch']

    def _get_model_state(self, model):
        """Get model state dict"""
        if hasattr(model, 'module'):
            return model.module.state_dict()
        else:
            return model.state_dict()
```

## Elastic Training

Elastic training allows adding or removing nodes dynamically during training.

### Elastic Training with Ray

```python
from ray.train.torch import TorchTrainer
from ray import train

def elastic_train_func(config):
    """
    Training function for elastic training

    Ray Train handles worker elasticity automatically
    """
    # Get current world info (may change during training!)
    rank = train.get_context().get_world_rank()
    world_size = train.get_context().get_world_size()

    print(f"Worker {rank}/{world_size} starting")

    # Create model and optimizer
    model = create_model()
    model = train.torch.prepare_model(model)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config['lr'])

    # Load checkpoint if resuming
    checkpoint = train.get_checkpoint()
    if checkpoint:
        with checkpoint.as_directory() as checkpoint_dir:
            state = torch.load(f"{checkpoint_dir}/checkpoint.pt")
            model.load_state_dict(state['model'])
            optimizer.load_state_dict(state['optimizer'])
            start_epoch = state['epoch'] + 1
    else:
        start_epoch = 0

    # Training loop
    for epoch in range(start_epoch, config['num_epochs']):
        # World size may change between epochs!
        current_world_size = train.get_context().get_world_size()

        if current_world_size != world_size:
            print(f"World size changed: {world_size} → {current_world_size}")
            world_size = current_world_size

        # Train epoch
        for batch in train_loader:
            optimizer.zero_grad()
            loss = model(batch)
            loss.backward()
            optimizer.step()

        # Save checkpoint
        checkpoint_dict = {
            'epoch': epoch,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
        }

        with train.checkpoint_context() as checkpoint_dir:
            torch.save(checkpoint_dict, f"{checkpoint_dir}/checkpoint.pt")

        # Report metrics
        train.report({'epoch': epoch, 'loss': loss.item()})

# Create elastic trainer
trainer = TorchTrainer(
    elastic_train_func,
    train_loop_config={'lr': 1e-4, 'num_epochs': 100},
    scaling_config=train.ScalingConfig(
        num_workers=4,
        use_gpu=True,
        # Enable elasticity
        trainer_resources={"CPU": 0},  # Allow dynamic scaling
    ),
    run_config=train.RunConfig(
        # Configure fault tolerance
        failure_config=train.FailureConfig(
            max_failures=3,  # Retry up to 3 times
        ),
    ),
)

result = trainer.fit()
```

### Manual Elastic Training

```python
class ElasticTrainingCoordinator:
    """
    Coordinate elastic training with dynamic world size
    """

    def __init__(self, initial_world_size):
        self.current_world_size = initial_world_size
        self.active_ranks = set(range(initial_world_size))
        self.failed_ranks = set()

    def check_health(self):
        """
        Check health of all workers

        Returns set of failed ranks
        """
        failed = set()

        for rank in self.active_ranks:
            try:
                # Send health check (implementation depends on framework)
                health = self._send_health_check(rank)
                if not health:
                    failed.add(rank)
            except Exception:
                failed.add(rank)

        return failed

    def handle_failure(self, failed_ranks):
        """
        Handle worker failures

        Options:
        1. Remove failed workers and continue (reduce world size)
        2. Replace failed workers with new ones (maintain world size)
        3. Pause and wait for recovery
        """
        self.failed_ranks.update(failed_ranks)
        self.active_ranks -= failed_ranks

        new_world_size = len(self.active_ranks)

        print(f"Handling failures: {failed_ranks}")
        print(f"World size: {self.current_world_size} → {new_world_size}")

        if new_world_size == 0:
            raise RuntimeError("All workers failed!")

        # Update world size
        self.current_world_size = new_world_size

        # Redistribute work to remaining workers
        self._redistribute_work()

    def add_workers(self, num_workers):
        """
        Add new workers dynamically
        """
        new_ranks = set(range(
            max(self.active_ranks) + 1,
            max(self.active_ranks) + 1 + num_workers
        ))

        self.active_ranks.update(new_ranks)
        self.current_world_size = len(self.active_ranks)

        print(f"Added {num_workers} workers. New world size: {self.current_world_size}")

        # Initialize new workers with current model state
        self._initialize_new_workers(new_ranks)

    def _redistribute_work(self):
        """Redistribute work to remaining workers"""
        # TODO: Implement work redistribution
        # - Update data samplers
        # - Rebalance mini-batches
        # - Adjust learning rate if needed
        pass

    def _initialize_new_workers(self, new_ranks):
        """Initialize new workers with current state"""
        # TODO: Implement new worker initialization
        # - Broadcast current model weights
        # - Send checkpoint
        # - Synchronize optimizer state
        pass

    def _send_health_check(self, rank):
        """Send health check to rank"""
        # TODO: Implement health check
        # This depends on your communication framework
        pass
```

## Failure Detection and Recovery

### Automatic Failure Detection

```python
import signal
import sys
from contextlib import contextmanager

class FailureDetector:
    """
    Detect and handle various types of failures
    """

    def __init__(self, checkpoint_manager, timeout_seconds=300):
        self.checkpoint_manager = checkpoint_manager
        self.timeout_seconds = timeout_seconds
        self.last_progress_time = time.time()

    @contextmanager
    def watchdog(self):
        """
        Context manager that saves checkpoint on unexpected exit
        """
        def signal_handler(signum, frame):
            print(f"\n⚠ Received signal {signum}. Saving emergency checkpoint...")
            self._emergency_checkpoint()
            sys.exit(1)

        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        try:
            yield
        except Exception as e:
            print(f"\n⚠ Exception occurred: {e}")
            print("Saving emergency checkpoint...")
            self._emergency_checkpoint()
            raise
        finally:
            # Cleanup
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)

    def check_progress(self):
        """
        Check if training is making progress

        Call this periodically during training
        """
        current_time = time.time()
        elapsed = current_time - self.last_progress_time

        if elapsed > self.timeout_seconds:
            print(f"⚠ No progress for {elapsed:.0f}s. Possible hang!")
            return False

        return True

    def mark_progress(self):
        """Mark that training is making progress"""
        self.last_progress_time = time.time()

    def detect_nan_inf(self, loss):
        """Detect NaN or Inf in loss"""
        if torch.isnan(loss) or torch.isinf(loss):
            print(f"⚠ NaN/Inf detected in loss: {loss}")
            return True
        return False

    def detect_oom(self):
        """Detect out-of-memory condition"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            max_memory = torch.cuda.get_device_properties(0).total_memory / 1e9

            usage_pct = (allocated / max_memory) * 100

            if usage_pct > 95:
                print(f"⚠ High GPU memory usage: {usage_pct:.1f}%")
                return True

        return False

    def _emergency_checkpoint(self):
        """Save emergency checkpoint"""
        # TODO: Implement emergency checkpoint
        # This should save minimal state to resume quickly
        pass

# Usage in training loop
def train_with_failure_detection():
    """Training loop with automatic failure detection"""
    checkpoint_mgr = CheckpointManager("./checkpoints")
    detector = FailureDetector(checkpoint_mgr)

    with detector.watchdog():
        for epoch in range(num_epochs):
            for batch_idx, batch in enumerate(train_loader):
                # Train step
                loss = train_step(model, batch, optimizer)

                # Check for numerical issues
                if detector.detect_nan_inf(loss):
                    print("Recovering from NaN/Inf...")
                    # Load last good checkpoint
                    checkpoint_mgr.load_checkpoint(model, optimizer)
                    continue

                # Check for OOM
                if detector.detect_oom():
                    print("High memory usage. Forcing garbage collection...")
                    torch.cuda.empty_cache()

                # Mark progress
                if batch_idx % 10 == 0:
                    detector.mark_progress()

                # Periodic progress check
                if batch_idx % 100 == 0:
                    if not detector.check_progress():
                        raise RuntimeError("Training appears to be hung!")

            # Save checkpoint every epoch
            checkpoint_mgr.save_checkpoint(
                model, optimizer, None, epoch, {'loss': loss.item()}
            )
```

## State Consistency

### Ensuring Consistent State

```python
def verify_model_consistency(model):
    """
    Verify all workers have consistent model state
    """
    if not dist.is_initialized():
        return True

    rank = dist.get_rank()
    world_size = dist.get_world_size()

    # Calculate hash of model parameters
    import hashlib

    hash_md5 = hashlib.md5()
    for param in model.parameters():
        hash_md5.update(param.data.cpu().numpy().tobytes())

    local_hash = hash_md5.hexdigest()

    # Gather hashes from all ranks
    hash_list = [None] * world_size
    dist.all_gather_object(hash_list, local_hash)

    # Check if all hashes match
    if rank == 0:
        if len(set(hash_list)) == 1:
            print("✓ All workers have consistent model state")
            return True
        else:
            print("✗ Model state inconsistency detected!")
            for i, h in enumerate(hash_list):
                print(f"  Rank {i}: {h}")
            return False

    return True

def synchronize_state(model, optimizer, source_rank=0):
    """
    Synchronize model and optimizer state across all workers

    Broadcasts from source_rank to all other ranks
    """
    if not dist.is_initialized():
        return

    # Broadcast model parameters
    for param in model.parameters():
        dist.broadcast(param.data, src=source_rank)

    # Broadcast optimizer state (more complex)
    if dist.get_rank() == source_rank:
        # Source: prepare optimizer state for broadcast
        opt_state = optimizer.state_dict()
        dist.broadcast_object_list([opt_state], src=source_rank)
    else:
        # Others: receive optimizer state
        opt_state_list = [None]
        dist.broadcast_object_list(opt_state_list, src=source_rank)
        optimizer.load_state_dict(opt_state_list[0])

    print(f"Rank {dist.get_rank()}: State synchronized from rank {source_rank}")
```

## Production Best Practices

### Comprehensive Fault-Tolerant Training

```python
class FaultTolerantTrainer:
    """
    Production-ready fault-tolerant trainer
    """

    def __init__(self, model, config):
        self.model = model
        self.config = config

        # Checkpointing
        self.checkpoint_mgr = CheckpointManager(
            checkpoint_dir=config['checkpoint_dir'],
            keep_last_n=config.get('keep_checkpoints', 3)
        )

        # Failure detection
        self.failure_detector = FailureDetector(
            self.checkpoint_mgr,
            timeout_seconds=config.get('timeout', 300)
        )

        # Training state
        self.epoch = 0
        self.global_step = 0
        self.best_metric = float('inf')

    def train(self, train_loader, val_loader, num_epochs):
        """
        Main training loop with fault tolerance
        """
        # Try to resume from checkpoint
        try:
            info = self.checkpoint_mgr.load_checkpoint(
                self.model, self.optimizer, self.scheduler
            )
            self.epoch = info['epoch'] + 1
            self.global_step = info.get('step', 0)
            print(f"✓ Resumed from epoch {info['epoch']}")
        except FileNotFoundError:
            print("Starting training from scratch")

        # Training loop with failure detection
        with self.failure_detector.watchdog():
            for epoch in range(self.epoch, num_epochs):
                try:
                    # Train epoch
                    train_metrics = self.train_epoch(train_loader, epoch)

                    # Validate
                    val_metrics = self.validate(val_loader, epoch)

                    # Check for improvement
                    if val_metrics['loss'] < self.best_metric:
                        self.best_metric = val_metrics['loss']
                        # Save best checkpoint
                        self.checkpoint_mgr.save_checkpoint(
                            self.model, self.optimizer, self.scheduler,
                            epoch, val_metrics, step='best'
                        )

                    # Regular checkpoint
                    if epoch % self.config.get('checkpoint_freq', 1) == 0:
                        self.checkpoint_mgr.save_checkpoint(
                            self.model, self.optimizer, self.scheduler,
                            epoch, val_metrics, step=self.global_step
                        )

                    # Verify consistency (distributed)
                    if dist.is_initialized():
                        verify_model_consistency(self.model)

                except Exception as e:
                    print(f"⚠ Error in epoch {epoch}: {e}")
                    print("Attempting recovery...")

                    # Try to recover
                    try:
                        # Load last checkpoint
                        self.checkpoint_mgr.load_checkpoint(
                            self.model, self.optimizer, self.scheduler
                        )
                        print("✓ Recovered from checkpoint")

                        # Synchronize state across workers
                        if dist.is_initialized():
                            synchronize_state(self.model, self.optimizer)

                        # Continue training
                        continue

                    except Exception as recovery_error:
                        print(f"✗ Recovery failed: {recovery_error}")
                        raise

    def train_epoch(self, dataloader, epoch):
        """Train one epoch with failure detection"""
        self.model.train()
        total_loss = 0

        for batch_idx, batch in enumerate(dataloader):
            # Train step
            loss = self.train_step(batch)

            # Detect failures
            if self.failure_detector.detect_nan_inf(loss):
                raise RuntimeError("NaN/Inf in loss")

            if self.failure_detector.detect_oom():
                torch.cuda.empty_cache()

            # Mark progress
            self.failure_detector.mark_progress()

            total_loss += loss.item()
            self.global_step += 1

            # Periodic checkpoint (every N steps)
            if self.global_step % self.config.get('checkpoint_steps', 1000) == 0:
                self.checkpoint_mgr.save_checkpoint(
                    self.model, self.optimizer, self.scheduler,
                    epoch, {'loss': total_loss / (batch_idx + 1)},
                    step=self.global_step
                )

        return {'loss': total_loss / len(dataloader)}

    def train_step(self, batch):
        """Single training step"""
        # TODO: Implement training step
        pass

    def validate(self, dataloader, epoch):
        """Validation"""
        # TODO: Implement validation
        pass
```

## Summary

Key takeaways:

1. **Failures are inevitable** in large-scale training
2. **Checkpointing** is essential - save frequently
3. **Sharded checkpoints** for very large models
4. **Elastic training** enables dynamic scaling
5. **Failure detection** should be automatic
6. **State consistency** must be verified in distributed settings

**Best Practices:**
- Checkpoint every N steps and every epoch
- Keep multiple checkpoints (not just latest)
- Verify checkpoint integrity
- Test recovery procedures
- Monitor for common failure modes
- Use elastic training for cloud deployments

## Further Reading

- [PyTorch Distributed Checkpoint](https://pytorch.org/docs/stable/distributed.checkpoint.html)
- [Ray Train Fault Tolerance](https://docs.ray.io/en/latest/train/user-guides/fault-tolerance.html)
- "Elastic Deep Learning in Multi-Tenant GPU Clusters" (Microsoft, 2020)

## Next Steps

Continue to `07-performance-optimization.md` for advanced performance optimization techniques.
