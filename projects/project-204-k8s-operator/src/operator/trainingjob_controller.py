"""Facade controller providing simplified interface for TrainingJob operations.

TODO for students: This facade provides a simplified API for:
- Creating TrainingJobs programmatically
- Querying TrainingJob status
- Scaling training replicas
- Managing checkpoints
- Retrieving metrics
"""

from typing import Dict, Any, List, Optional

from ..utils.logger import get_logger
from ..controllers.job_controller import JobController
from ..controllers.checkpoint_controller import CheckpointController
from ..controllers.status_controller import StatusController
from ..crd.defaults import apply_defaults
from ..crd.validation import validate_training_job, ValidationError

logger = get_logger(__name__)


class TrainingJobController:
    """High-level controller for TrainingJob operations.

    TODO for students: This is a facade/simplified API for common operations.
    Students can use this to build CLIs, UIs, or integrations.

    Attributes:
        job_controller: Job lifecycle controller
        checkpoint_controller: Checkpoint management controller
        status_controller: Status management controller
    """

    def __init__(self, namespace: str = "default"):
        """Initialize TrainingJob controller.

        Args:
            namespace: Default namespace for operations
        """
        self.namespace = namespace
        self.job_controller = JobController(namespace=namespace)
        self.checkpoint_controller = CheckpointController()
        self.status_controller = StatusController()
        logger.info(f"TrainingJobController initialized (namespace={namespace})")

    def create_job(
        self,
        name: str,
        spec: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Create a new TrainingJob.

        TODO for students: Implement job creation:
        - Validate spec
        - Apply defaults
        - Create CRD resource
        - Wait for job to start
        - Return job object

        Args:
            name: Job name
            spec: Job specification
            namespace: Namespace (uses default if None)

        Returns:
            True if job created successfully

        Raises:
            ValidationError: If spec validation fails
        """
        ns = namespace or self.namespace
        logger.info(f"Creating TrainingJob {ns}/{name}")

        # Validate spec
        validation_result = validate_training_job(spec)
        if not validation_result.is_valid:
            error_msg = "; ".join(validation_result.errors)
            raise ValidationError(f"Validation failed: {error_msg}")

        # Apply defaults
        spec_with_defaults = apply_defaults(spec)

        # TODO for students: Create the CRD resource
        # from kubernetes import client
        # custom_api = client.CustomObjectsApi()
        # body = {
        #     "apiVersion": "mlplatform.example.com/v1alpha1",
        #     "kind": "TrainingJob",
        #     "metadata": {"name": name, "namespace": ns},
        #     "spec": spec_with_defaults,
        # }
        # custom_api.create_namespaced_custom_object(
        #     group="mlplatform.example.com",
        #     version="v1alpha1",
        #     namespace=ns,
        #     plural="trainingjobs",
        #     body=body,
        # )

        logger.info(f"TrainingJob {ns}/{name} created")
        return True

    def get_job_status(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get status of a TrainingJob.

        TODO for students: Add status formatting and enrichment

        Args:
            name: Job name
            namespace: Namespace (uses default if None)

        Returns:
            Status dict or None if not found
        """
        ns = namespace or self.namespace
        return self.status_controller.get_status(name, ns)

    def list_jobs(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List TrainingJobs.

        TODO for students: Add filtering and sorting options

        Args:
            namespace: Namespace filter (None for all)
            label_selector: Label selector filter

        Returns:
            List of TrainingJob resources
        """
        return self.job_controller.list_training_jobs(namespace, label_selector)

    def scale_job(
        self,
        name: str,
        replicas: int,
        namespace: Optional[str] = None,
    ) -> bool:
        """Scale a TrainingJob.

        TODO for students: Implement scaling:
        - Validate new replica count
        - Update job spec
        - Coordinate with checkpoint controller
        - Update status

        Args:
            name: Job name
            replicas: New replica count
            namespace: Namespace (uses default if None)

        Returns:
            True if scaling succeeded
        """
        ns = namespace or self.namespace
        logger.info(f"Scaling {ns}/{name} to {replicas} replicas")

        # TODO for students: Implement scaling logic
        # - Update TrainingJob spec.replicas
        # - Trigger reconciliation
        # - Wait for new replicas to be ready

        return True

    def create_checkpoint(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """Create a checkpoint for a TrainingJob.

        TODO for students: Add checkpoint validation and error handling

        Args:
            name: Job name
            namespace: Namespace (uses default if None)

        Returns:
            True if checkpoint created successfully
        """
        ns = namespace or self.namespace
        logger.info(f"Creating checkpoint for {ns}/{name}")

        # Get job spec
        # TODO for students: Fetch actual job spec
        spec = {}

        checkpoint = self.checkpoint_controller.create_checkpoint(name, ns, spec)
        return checkpoint is not None

    def list_checkpoints(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List checkpoints for a TrainingJob.

        TODO for students: Format checkpoint info for display

        Args:
            name: Job name
            namespace: Namespace (uses default if None)

        Returns:
            List of checkpoint info dicts
        """
        ns = namespace or self.namespace
        checkpoints = self.checkpoint_controller.list_checkpoints(name, ns)

        # Convert to dicts for JSON serialization
        return [
            {
                "checkpoint_id": cp.checkpoint_id,
                "created_at": cp.created_at.isoformat(),
                "status": cp.status.value,
                "storage_path": cp.storage_path,
            }
            for cp in checkpoints
        ]

    def delete_job(
        self,
        name: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """Delete a TrainingJob.

        TODO for students: Implement deletion:
        - Delete CRD resource
        - Wait for cleanup
        - Archive checkpoints if configured

        Args:
            name: Job name
            namespace: Namespace (uses default if None)

        Returns:
            True if deletion succeeded
        """
        ns = namespace or self.namespace
        logger.info(f"Deleting TrainingJob {ns}/{name}")

        # TODO for students: Implement deletion
        # custom_api = client.CustomObjectsApi()
        # custom_api.delete_namespaced_custom_object(
        #     group="mlplatform.example.com",
        #     version="v1alpha1",
        #     namespace=ns,
        #     plural="trainingjobs",
        #     name=name,
        # )

        return True
