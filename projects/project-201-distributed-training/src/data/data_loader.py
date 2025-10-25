"""Data loader utilities for distributed training."""

from torch.utils.data import DataLoader, DistributedSampler
from typing import Tuple


def create_distributed_dataloader(
    dataset,
    batch_size: int,
    num_workers: int,
    world_size: int,
    rank: int,
    is_train: bool = True
) -> Tuple[DataLoader, DistributedSampler]:
    """
    Create distributed data loader.

    TODO: Implement distributed data loader:
    1. Create DistributedSampler with proper rank and world_size
    2. Configure DataLoader with:
       - Appropriate num_workers
       - pin_memory for GPU training
       - prefetch_factor for pipelining
       - persistent_workers for efficiency
    3. Return both DataLoader and sampler (for epoch shuffling)

    Args:
        dataset: PyTorch dataset
        batch_size: Batch size per worker
        num_workers: Number of data loading workers
        world_size: Total number of distributed workers
        rank: Rank of current worker
        is_train: Whether this is training data

    Returns:
        Tuple of (DataLoader, DistributedSampler)
    """
    # TODO: Implement distributed data loader creation
    pass
