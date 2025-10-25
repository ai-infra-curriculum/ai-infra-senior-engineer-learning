"""Controller for managing training checkpoints.

TODO for students: Enhance checkpoint management with:
- Incremental checkpointing
- Checkpoint versioning and retention policies
- Automatic checkpoint restoration
- Multi-storage backend support (S3, GCS, Azure, NFS)
- Checkpoint validation and integrity checks
- Compression and encryption
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from kubernetes import client
from kubernetes.client import ApiException

from ..utils.logger import get_logger
from ..utils.k8s_client import get_k8s_client

logger = get_logger(__name__)


class CheckpointStatus(Enum):
    """Status of a checkpoint operation.

    TODO for students: Add more status values
    - VALIDATING
    - UPLOADING
    - RESTORING
    """

    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"


@dataclass
class Checkpoint:
    """Represents a training checkpoint.

    TODO for students: Add fields:
    - Model metrics at checkpoint time
    - Training step/epoch number
    - File size and compression info
    - Checksum for validation
    """

    checkpoint_id: str
    job_name: str
    namespace: str
    storage_path: str
    created_at: datetime
    status: CheckpointStatus
    error_message: Optional[str] = None


class CheckpointController:
    """Controller for managing training checkpoints.

    TODO for students: Implement:
    - Periodic checkpoint scheduling
    - Event-driven checkpointing (on model improvement)
    - Distributed checkpoint coordination
    - Checkpoint registry/catalog
    - Automatic cleanup of old checkpoints

    Attributes:
        core_api: Kubernetes Core API client
        checkpoint_registry: In-memory registry of checkpoints
    """

    def __init__(self):
        """Initialize checkpoint controller.

        TODO for students: Add configuration:
        - Default retention policy
        - Storage backend configuration
        - Compression settings
        """
        self.core_api = get_k8s_client("core_v1")
        self.checkpoint_registry: Dict[str, List[Checkpoint]] = {}
        logger.info("CheckpointController initialized")

    def should_checkpoint(
        self, job_name: str, namespace: str, spec: Dict[str, Any]
    ) -> bool:
        """Determine if a checkpoint should be created.

        TODO for students: Implement intelligent checkpoint scheduling:
        - Check time since last checkpoint
        - Check if model has improved
        - Check available storage space
        - Respect user-defined checkpoint interval

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace
            spec: TrainingJob spec

        Returns:
            True if checkpoint should be created
        """
        checkpoint_config = spec.get("checkpoint", {})

        if not checkpoint_config.get("enabled", True):
            return False

        # Get checkpoint interval
        interval = checkpoint_config.get("interval", 300)  # Default 5 minutes

        # Get last checkpoint time
        last_checkpoint = self._get_last_checkpoint(job_name, namespace)
        if last_checkpoint is None:
            return True

        # Check if interval has elapsed
        time_since_last = datetime.utcnow() - last_checkpoint.created_at
        should_create = time_since_last >= timedelta(seconds=interval)

        # TODO for students: Add more sophisticated logic
        # - Check model metrics improvement
        # - Check training progress (epochs/steps)
        # - Check storage quota

        return should_create

    def create_checkpoint(
        self, job_name: str, namespace: str, spec: Dict[str, Any]
    ) -> Optional[Checkpoint]:
        """Create a checkpoint for a training job.

        TODO for students: Implement:
        - Coordinate checkpoint creation across distributed workers
        - Upload checkpoint to configured storage backend
        - Validate checkpoint integrity
        - Update checkpoint registry
        - Create Kubernetes Event for tracking

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace
            spec: TrainingJob spec

        Returns:
            Created Checkpoint or None if failed
        """
        logger.info(f"Creating checkpoint for {namespace}/{job_name}")

        checkpoint_config = spec.get("checkpoint", {})
        storage_path = checkpoint_config.get("path", "/checkpoints")
        storage_backend = checkpoint_config.get("storage", "pvc")

        # Generate checkpoint ID
        checkpoint_id = f"{job_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            job_name=job_name,
            namespace=namespace,
            storage_path=f"{storage_path}/{checkpoint_id}",
            created_at=datetime.utcnow(),
            status=CheckpointStatus.IN_PROGRESS,
        )

        # TODO for students: Implement actual checkpoint creation
        # 1. Signal pods to save checkpoint
        # 2. Wait for checkpoint to be saved
        # 3. Upload to storage backend if needed
        # 4. Validate checkpoint
        # 5. Update status

        # Simulate checkpoint creation
        checkpoint.status = CheckpointStatus.COMPLETED

        # Register checkpoint
        self._register_checkpoint(checkpoint)

        logger.info(f"Checkpoint created: {checkpoint_id}")
        return checkpoint

    def restore_checkpoint(
        self, job_name: str, namespace: str, checkpoint_id: str
    ) -> bool:
        """Restore a training job from a checkpoint.

        TODO for students: Implement:
        - Download checkpoint from storage
        - Validate checkpoint integrity
        - Configure pods to load checkpoint on startup
        - Handle distributed checkpoint restoration
        - Update job status

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace
            checkpoint_id: Checkpoint ID to restore

        Returns:
            True if restoration initiated successfully
        """
        logger.info(f"Restoring checkpoint {checkpoint_id} for {namespace}/{job_name}")

        checkpoint = self._get_checkpoint(job_name, namespace, checkpoint_id)
        if checkpoint is None:
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False

        # TODO for students: Implement restoration logic
        # 1. Validate checkpoint exists and is valid
        # 2. Download from storage backend
        # 3. Update pod configuration to mount checkpoint
        # 4. Restart pods with checkpoint
        # 5. Monitor restoration progress

        logger.info(f"Checkpoint restoration initiated: {checkpoint_id}")
        return True

    def list_checkpoints(
        self, job_name: str, namespace: str
    ) -> List[Checkpoint]:
        """List checkpoints for a training job.

        TODO for students: Add:
        - Filtering by date range
        - Sorting options
        - Pagination for large lists

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace

        Returns:
            List of checkpoints
        """
        key = f"{namespace}/{job_name}"
        return self.checkpoint_registry.get(key, [])

    def cleanup_old_checkpoints(
        self, job_name: str, namespace: str, retention_count: int = 5
    ) -> int:
        """Clean up old checkpoints based on retention policy.

        TODO for students: Implement:
        - Time-based retention (keep last N days)
        - Count-based retention (keep last N checkpoints)
        - Metric-based retention (keep best N checkpoints)
        - Storage-based retention (keep checkpoints under size limit)

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace
            retention_count: Number of checkpoints to keep

        Returns:
            Number of checkpoints deleted
        """
        logger.info(f"Cleaning up old checkpoints for {namespace}/{job_name}")

        checkpoints = self.list_checkpoints(job_name, namespace)
        if len(checkpoints) <= retention_count:
            return 0

        # Sort by creation time (newest first)
        sorted_checkpoints = sorted(
            checkpoints, key=lambda c: c.created_at, reverse=True
        )

        # Keep only the most recent ones
        to_delete = sorted_checkpoints[retention_count:]
        deleted_count = 0

        for checkpoint in to_delete:
            # TODO for students: Implement actual deletion
            # - Delete from storage backend
            # - Remove from registry
            # - Create Event for audit trail
            logger.info(f"Deleting checkpoint: {checkpoint.checkpoint_id}")
            deleted_count += 1

        # Update registry
        key = f"{namespace}/{job_name}"
        self.checkpoint_registry[key] = sorted_checkpoints[:retention_count]

        logger.info(f"Deleted {deleted_count} old checkpoints")
        return deleted_count

    def _get_last_checkpoint(
        self, job_name: str, namespace: str
    ) -> Optional[Checkpoint]:
        """Get the most recent checkpoint for a job.

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace

        Returns:
            Most recent Checkpoint or None
        """
        checkpoints = self.list_checkpoints(job_name, namespace)
        if not checkpoints:
            return None

        return max(checkpoints, key=lambda c: c.created_at)

    def _get_checkpoint(
        self, job_name: str, namespace: str, checkpoint_id: str
    ) -> Optional[Checkpoint]:
        """Get a specific checkpoint.

        Args:
            job_name: TrainingJob name
            namespace: TrainingJob namespace
            checkpoint_id: Checkpoint ID

        Returns:
            Checkpoint or None if not found
        """
        checkpoints = self.list_checkpoints(job_name, namespace)
        for checkpoint in checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                return checkpoint
        return None

    def _register_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Register a checkpoint in the registry.

        TODO for students: Implement persistent checkpoint registry
        - Store in ConfigMap or custom resource
        - Add metadata indexing for fast lookups
        - Sync with external checkpoint catalog

        Args:
            checkpoint: Checkpoint to register
        """
        key = f"{checkpoint.namespace}/{checkpoint.job_name}"
        if key not in self.checkpoint_registry:
            self.checkpoint_registry[key] = []

        self.checkpoint_registry[key].append(checkpoint)
        logger.debug(f"Registered checkpoint: {checkpoint.checkpoint_id}")
