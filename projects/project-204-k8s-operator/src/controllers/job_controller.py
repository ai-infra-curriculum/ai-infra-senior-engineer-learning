"""Main controller for TrainingJob lifecycle management.

TODO for students: Enhance the controller with:
- Leader election for high availability
- Event recording for debugging
- Finalizers for cleanup on deletion
- Owner references for garbage collection
- Retry logic with exponential backoff
- Graceful shutdown handling
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from kubernetes import client
from kubernetes.client import ApiException

from ..utils.logger import get_logger, OperatorLogger
from ..utils.k8s_client import create_custom_object_client, handle_api_exception
from ..utils.metrics import record_reconciliation, ReconciliationResult
from ..crd.validation import validate_training_job
from ..crd.defaults import apply_defaults
from .resource_controller import ResourceController
from .status_controller import StatusController
from .checkpoint_controller import CheckpointController

logger = get_logger(__name__)


class JobPhase(Enum):
    """Phases of a TrainingJob.

    TODO for students: Add more phases as needed
    - INITIALIZING
    - CHECKPOINTING
    - SCALING
    """

    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class JobController:
    """Main controller for TrainingJob resources.

    TODO for students: Implement:
    - Watch mechanism for real-time updates
    - Queue-based reconciliation
    - Concurrent reconciliation with worker pool
    - Health checking and auto-recovery
    - Integration with admission webhooks

    Attributes:
        namespace: Kubernetes namespace to watch (None = all namespaces)
        resync_period: Seconds between full resyncs
        resource_controller: Controller for K8s resources
        status_controller: Controller for status updates
        checkpoint_controller: Controller for checkpoints
    """

    def __init__(
        self,
        namespace: Optional[str] = None,
        resync_period: int = 300,
    ):
        """Initialize job controller.

        TODO for students: Add configuration options:
        - Max concurrent reconciliations
        - Retry backoff configuration
        - Leader election config

        Args:
            namespace: Namespace to watch (None for all)
            resync_period: Resync period in seconds
        """
        self.namespace = namespace
        self.resync_period = resync_period
        self.client = create_custom_object_client()

        # Initialize sub-controllers
        self.resource_controller = ResourceController()
        self.status_controller = StatusController()
        self.checkpoint_controller = CheckpointController()

        # CRD details
        self.group = "mlplatform.example.com"
        self.version = "v1alpha1"
        self.plural = "trainingjobs"

        logger.info(
            f"JobController initialized (namespace={namespace or 'all'}, "
            f"resync_period={resync_period}s)"
        )

    def reconcile(self, name: str, namespace: str) -> bool:
        """Reconcile a single TrainingJob.

        TODO for students: Implement full reconciliation logic:
        1. Get current TrainingJob resource
        2. Validate spec
        3. Apply defaults
        4. Create/update Kubernetes resources (Pods, Services, etc.)
        5. Monitor job status
        6. Handle checkpointing
        7. Update TrainingJob status
        8. Handle cleanup

        Args:
            name: TrainingJob name
            namespace: TrainingJob namespace

        Returns:
            True if reconciliation succeeded, False otherwise
        """
        op_logger = OperatorLogger(__name__, namespace=namespace, resource_name=name)

        with record_reconciliation(name, namespace) as recorder:
            try:
                op_logger.info("Starting reconciliation")

                # Get TrainingJob resource
                job = self._get_training_job(name, namespace)
                if job is None:
                    op_logger.warning("TrainingJob not found, may have been deleted")
                    recorder.mark_success()
                    return True

                spec = job.get("spec", {})
                status = job.get("status", {})

                # Validate spec
                validation_result = validate_training_job(spec)
                if not validation_result.is_valid:
                    error_msg = "; ".join(validation_result.errors)
                    op_logger.error(f"Validation failed: {error_msg}")
                    self.status_controller.update_phase(
                        name, namespace, JobPhase.FAILED, message=error_msg
                    )
                    recorder.mark_failure(error_msg)
                    return False

                # Apply defaults
                spec_with_defaults = apply_defaults(spec)

                # Determine current phase
                current_phase = status.get("phase", "Pending")
                op_logger.info(f"Current phase: {current_phase}")

                # Reconcile based on phase
                if current_phase == "Pending":
                    self._reconcile_pending(name, namespace, spec_with_defaults, op_logger)
                elif current_phase == "Running":
                    self._reconcile_running(name, namespace, spec_with_defaults, op_logger)
                elif current_phase in ["Succeeded", "Failed"]:
                    self._reconcile_completed(name, namespace, spec_with_defaults, op_logger)

                # TODO for students: Handle other phases
                # - Checkpointing
                # - Scaling
                # - Paused

                op_logger.info("Reconciliation completed successfully")
                recorder.mark_success()
                return True

            except Exception as e:
                op_logger.exception(f"Reconciliation failed: {e}")
                recorder.mark_failure(str(e))
                return False

    def _get_training_job(self, name: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get a TrainingJob resource.

        TODO for students: Add caching to reduce API calls

        Args:
            name: Job name
            namespace: Job namespace

        Returns:
            TrainingJob dict or None if not found
        """
        try:
            job = self.client.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=namespace,
                plural=self.plural,
                name=name,
            )
            return job
        except ApiException as e:
            if e.status == 404:
                return None
            handle_api_exception(e, "get", f"{namespace}/{name}")
            raise

    def _reconcile_pending(
        self, name: str, namespace: str, spec: Dict[str, Any], logger: OperatorLogger
    ) -> None:
        """Reconcile a TrainingJob in Pending phase.

        TODO for students: Implement:
        - Create Pods for training replicas
        - Create Services for distributed training
        - Create ConfigMaps for configuration
        - Set up volumes for checkpointing
        - Create ServiceAccount if needed
        - Wait for resources to be ready
        - Transition to Running phase

        Args:
            name: Job name
            namespace: Job namespace
            spec: Job spec with defaults
            logger: Logger instance
        """
        logger.info("Reconciling pending job")

        # TODO for students: Implement resource creation
        # pods = self.resource_controller.create_training_pods(name, namespace, spec)
        # services = self.resource_controller.create_training_services(name, namespace, spec)

        # Update status to Running
        self.status_controller.update_phase(
            name, namespace, JobPhase.RUNNING, message="Training started"
        )

    def _reconcile_running(
        self, name: str, namespace: str, spec: Dict[str, Any], logger: OperatorLogger
    ) -> None:
        """Reconcile a TrainingJob in Running phase.

        TODO for students: Implement:
        - Monitor pod status
        - Handle pod failures and restarts
        - Trigger checkpointing
        - Collect metrics
        - Detect completion
        - Handle scaling requests
        - Transition to Succeeded or Failed

        Args:
            name: Job name
            namespace: Job namespace
            spec: Job spec with defaults
            logger: Logger instance
        """
        logger.info("Reconciling running job")

        # TODO for students: Implement monitoring and checkpoint logic
        # pod_status = self.resource_controller.get_pod_status(name, namespace)
        # if self.checkpoint_controller.should_checkpoint(name, namespace):
        #     self.checkpoint_controller.create_checkpoint(name, namespace)

        # Check for completion
        # if all_pods_succeeded(pod_status):
        #     self.status_controller.update_phase(
        #         name, namespace, JobPhase.SUCCEEDED, message="Training completed"
        #     )
        # elif any_pods_failed_permanently(pod_status):
        #     self.status_controller.update_phase(
        #         name, namespace, JobPhase.FAILED, message="Training failed"
        #     )

    def _reconcile_completed(
        self, name: str, namespace: str, spec: Dict[str, Any], logger: OperatorLogger
    ) -> None:
        """Reconcile a completed TrainingJob.

        TODO for students: Implement:
        - Cleanup temporary resources
        - Preserve logs and checkpoints
        - Update final metrics
        - Handle TTL for completed jobs

        Args:
            name: Job name
            namespace: Job namespace
            spec: Job spec with defaults
            logger: Logger instance
        """
        logger.info("Reconciling completed job")

        # TODO for students: Implement cleanup logic
        # if spec.get("ttlSecondsAfterFinished"):
        #     self.resource_controller.cleanup_job_resources(name, namespace)

    def list_training_jobs(
        self, namespace: Optional[str] = None, label_selector: Optional[str] = None
    ) -> list:
        """List TrainingJob resources.

        TODO for students: Add filtering and pagination

        Args:
            namespace: Optional namespace filter
            label_selector: Optional label selector

        Returns:
            List of TrainingJob resources
        """
        try:
            if namespace:
                result = self.client.list_namespaced_custom_object(
                    group=self.group,
                    version=self.version,
                    namespace=namespace,
                    plural=self.plural,
                    label_selector=label_selector,
                )
            else:
                result = self.client.list_cluster_custom_object(
                    group=self.group,
                    version=self.version,
                    plural=self.plural,
                    label_selector=label_selector,
                )

            return result.get("items", [])

        except ApiException as e:
            handle_api_exception(e, "list", self.plural)
            raise
