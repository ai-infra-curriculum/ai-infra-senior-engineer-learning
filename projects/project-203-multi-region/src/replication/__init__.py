"""
Multi-Region Data Replication Module

Handles model, data, and configuration replication across multiple regions
with consistency guarantees and conflict resolution.

TODO for students:
- Implement eventual consistency mechanisms
- Add bidirectional replication
- Handle network partitions gracefully
- Implement conflict resolution strategies
"""

from .model_replicator import (
    ModelReplicator,
    ReplicationConfig,
    replicate_model,
)
from .data_sync import (
    DataSynchronizer,
    SyncStrategy,
    sync_datasets,
)
from .config_sync import (
    ConfigSynchronizer,
    sync_configurations,
    validate_sync,
)

__all__ = [
    # Model Replication
    "ModelReplicator",
    "ReplicationConfig",
    "replicate_model",
    # Data Synchronization
    "DataSynchronizer",
    "SyncStrategy",
    "sync_datasets",
    # Config Sync
    "ConfigSynchronizer",
    "sync_configurations",
    "validate_sync",
]
