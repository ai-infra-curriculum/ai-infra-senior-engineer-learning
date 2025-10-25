"""Controller for managing TrainingJob status updates.

TODO for students: Add:
- Optimistic locking for concurrent updates
- Status change event publishing
- Status history tracking
- Condition management
- Metrics collection on status changes
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from kubernetes.client import ApiException

from ..utils.logger import get_logger
from ..utils.k8s_client import create_custom_object_client, patch_custom_resource_status

logger = get_logger(__name__)


class ConditionType(Enum):
    """Types of status conditions.

    TODO for students: Add more condition types
    - CHECKPOINT_READY
    - SCALING
    - DEGRADED
    """

    READY = "Ready"
    PROGRESSING = "Progressing"
    FAILED = "Failed"
    COMPLETED = "Completed"


class ConditionStatus(Enum):
    """Status values for conditions."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


@dataclass
class StatusCondition:
    """Represents a status condition.

    TODO for students: Add fields:
    - Observed generation for tracking spec changes
    - Severity level
    - Related objects
    """

    type: str
    status: str
    reason: str
    message: str
    last_transition_time: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class StatusController:
    """Controller for managing TrainingJob status.

    TODO for students: Implement:
    - Status transition validation
    - Status event recording
    - Status condition management
    - Metrics tracking on status changes
    - Status history/audit trail

    Attributes:
        client: Kubernetes custom objects API client
        group: CRD API group
        version: CRD API version
        plural: CRD plural name
    """

    def __init__(self):
        """Initialize status controller.

        TODO for students: Add status caching for optimization
        """
        self.client = create_custom_object_client()
        self.group = "mlplatform.example.com"
        self.version = "v1alpha1"
        self.plural = "trainingjobs"
        logger.info("StatusController initialized")

    def update_phase(
        self,
        name: str,
        namespace: str,
        phase: Enum,
        message: Optional[str] = None,
    ) -> bool:
        """Update the phase of a TrainingJob.

        TODO for students: Implement:
        - Validate phase transition
        - Update related conditions
        - Record phase change event
        - Update metrics

        Args:
            name: TrainingJob name
            namespace: Namespace
            phase: New phase
            message: Optional status message

        Returns:
            True if update succeeded
        """
        logger.info(f"Updating phase for {namespace}/{name} to {phase.value}")

        status = {
            "phase": phase.value,
            "lastTransitionTime": datetime.utcnow().isoformat(),
        }

        if message:
            status["message"] = message

        # Add appropriate condition based on phase
        if phase.value == "Running":
            self._add_condition(
                status,
                ConditionType.PROGRESSING.value,
                ConditionStatus.TRUE.value,
                "TrainingStarted",
                "Training has started",
            )
        elif phase.value == "Succeeded":
            self._add_condition(
                status,
                ConditionType.COMPLETED.value,
                ConditionStatus.TRUE.value,
                "TrainingCompleted",
                "Training completed successfully",
            )
            status["completionTime"] = datetime.utcnow().isoformat()
        elif phase.value == "Failed":
            self._add_condition(
                status,
                ConditionType.FAILED.value,
                ConditionStatus.TRUE.value,
                "TrainingFailed",
                message or "Training failed",
            )
            status["completionTime"] = datetime.utcnow().isoformat()

        return self._update_status(name, namespace, status)

    def update_replica_status(
        self, name: str, namespace: str, replicas: int, ready_replicas: int
    ) -> bool:
        """Update replica status counts.

        TODO for students: Add:
        - Available replicas count
        - Unavailable replicas count
        - Updated replicas count

        Args:
            name: TrainingJob name
            namespace: Namespace
            replicas: Total replicas
            ready_replicas: Ready replicas

        Returns:
            True if update succeeded
        """
        logger.debug(
            f"Updating replica status for {namespace}/{name}: "
            f"{ready_replicas}/{replicas} ready"
        )

        status = {
            "replicas": replicas,
            "readyReplicas": ready_replicas,
        }

        # Update Ready condition based on replica status
        if ready_replicas == replicas and replicas > 0:
            self._add_condition(
                status,
                ConditionType.READY.value,
                ConditionStatus.TRUE.value,
                "AllReplicasReady",
                f"All {replicas} replicas are ready",
            )
        elif ready_replicas < replicas:
            self._add_condition(
                status,
                ConditionType.READY.value,
                ConditionStatus.FALSE.value,
                "ReplicasNotReady",
                f"Only {ready_replicas}/{replicas} replicas are ready",
            )

        return self._update_status(name, namespace, status)

    def add_condition(
        self,
        name: str,
        namespace: str,
        condition_type: str,
        status: str,
        reason: str,
        message: str,
    ) -> bool:
        """Add or update a status condition.

        TODO for students: Implement:
        - Merge with existing conditions
        - Only update if condition changed
        - Preserve condition history

        Args:
            name: TrainingJob name
            namespace: Namespace
            condition_type: Condition type
            status: Condition status (True/False/Unknown)
            reason: Reason code
            message: Human-readable message

        Returns:
            True if update succeeded
        """
        logger.debug(
            f"Adding condition to {namespace}/{name}: {condition_type}={status}"
        )

        status_update: Dict[str, Any] = {}
        self._add_condition(status_update, condition_type, status, reason, message)

        return self._update_status(name, namespace, status_update)

    def set_start_time(self, name: str, namespace: str) -> bool:
        """Set the start time for a TrainingJob.

        TODO for students: Also set scheduling time, initialization time

        Args:
            name: TrainingJob name
            namespace: Namespace

        Returns:
            True if update succeeded
        """
        logger.info(f"Setting start time for {namespace}/{name}")

        status = {
            "startTime": datetime.utcnow().isoformat(),
        }

        return self._update_status(name, namespace, status)

    def update_progress(
        self,
        name: str,
        namespace: str,
        current_epoch: int,
        total_epochs: int,
        metrics: Optional[Dict[str, float]] = None,
    ) -> bool:
        """Update training progress.

        TODO for students: Implement full progress tracking:
        - Training steps/iterations
        - Loss and accuracy metrics
        - Estimated time to completion
        - Resource utilization

        Args:
            name: TrainingJob name
            namespace: Namespace
            current_epoch: Current epoch number
            total_epochs: Total epochs
            metrics: Optional training metrics

        Returns:
            True if update succeeded
        """
        logger.debug(
            f"Updating progress for {namespace}/{name}: "
            f"epoch {current_epoch}/{total_epochs}"
        )

        status = {
            "progress": {
                "currentEpoch": current_epoch,
                "totalEpochs": total_epochs,
                "percentage": (current_epoch / total_epochs * 100) if total_epochs > 0 else 0,
            }
        }

        if metrics:
            status["progress"]["metrics"] = metrics

        return self._update_status(name, namespace, status)

    def _update_status(
        self, name: str, namespace: str, status_update: Dict[str, Any]
    ) -> bool:
        """Update TrainingJob status.

        TODO for students: Add:
        - Retry logic with exponential backoff
        - Optimistic locking (resource version)
        - Batch status updates
        - Status update validation

        Args:
            name: TrainingJob name
            namespace: Namespace
            status_update: Status fields to update

        Returns:
            True if update succeeded
        """
        try:
            patch_custom_resource_status(
                group=self.group,
                version=self.version,
                plural=self.plural,
                name=name,
                namespace=namespace,
                status=status_update,
            )
            logger.debug(f"Status updated for {namespace}/{name}")
            return True

        except ApiException as e:
            logger.error(
                f"Failed to update status for {namespace}/{name}: {e.status} - {e.reason}"
            )
            return False

    def _add_condition(
        self,
        status: Dict[str, Any],
        condition_type: str,
        condition_status: str,
        reason: str,
        message: str,
    ) -> None:
        """Add a condition to a status dict.

        TODO for students: Implement condition merging logic

        Args:
            status: Status dict to update
            condition_type: Condition type
            condition_status: Condition status
            reason: Reason code
            message: Human-readable message
        """
        if "conditions" not in status:
            status["conditions"] = []

        condition = {
            "type": condition_type,
            "status": condition_status,
            "reason": reason,
            "message": message,
            "lastTransitionTime": datetime.utcnow().isoformat(),
        }

        # TODO for students: Check if condition already exists and merge
        # For now, just append
        status["conditions"].append(condition)

    def get_status(self, name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get current status of a TrainingJob.

        TODO for students: Add status caching

        Args:
            name: TrainingJob name
            namespace: Namespace

        Returns:
            Status dict or None if not found
        """
        try:
            job = self.client.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=namespace,
                plural=self.plural,
                name=name,
            )
            return job.get("status", {})

        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"Failed to get status for {namespace}/{name}: {e}")
            raise
