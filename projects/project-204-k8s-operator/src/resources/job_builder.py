"""Builder for creating Kubernetes Job resources for TrainingJobs.

TODO for students: Consider using Jobs instead of raw Pods for:
- Automatic restart and backoff handling
- Completion tracking
- Parallel job execution
- Job TTL for cleanup
"""

from typing import Dict, Any, Optional

from kubernetes import client

from ..utils.logger import get_logger
from .pod_builder import PodBuilder

logger = get_logger(__name__)


class JobBuilder:
    """Builder for creating Kubernetes Job resources.

    TODO for students: Implement builder methods for:
    - Parallelism configuration
    - Completion tracking
    - Job TTL
    - Pod template customization
    - Backoff limits

    Attributes:
        job_name: TrainingJob name
        namespace: Kubernetes namespace
        spec: TrainingJob spec
        labels: Job labels
    """

    def __init__(self, job_name: str, namespace: str):
        """Initialize job builder.

        Args:
            job_name: TrainingJob name
            namespace: Namespace
        """
        self.job_name = job_name
        self.namespace = namespace
        self.spec: Dict[str, Any] = {}
        self.labels = {
            "trainingjob": job_name,
            "app": "ml-training",
        }
        logger.debug(f"JobBuilder initialized for {job_name}")

    def with_spec(self, spec: Dict[str, Any]) -> "JobBuilder":
        """Set the TrainingJob spec.

        Args:
            spec: TrainingJob spec

        Returns:
            Self for method chaining
        """
        self.spec = spec
        return self

    def build(self) -> client.V1Job:
        """Build the Job object.

        TODO for students: Implement complete job creation:
        - Configure parallelism for distributed training
        - Set backoff limit from spec
        - Add owner references
        - Configure TTL for completed jobs
        - Add job-level labels and annotations

        Returns:
            V1Job object
        """
        # Build pod template using PodBuilder
        pod_builder = PodBuilder(self.job_name, self.namespace, replica_id=0)
        pod = pod_builder.with_spec(self.spec).build()

        # Extract pod template spec
        pod_template = client.V1PodTemplateSpec(
            metadata=pod.metadata,
            spec=pod.spec,
        )

        # Build job spec
        job_spec = client.V1JobSpec(
            template=pod_template,
            backoff_limit=self.spec.get("backoffLimit", 3),
            completions=1,  # Single-completion job
            parallelism=1,  # TODO for students: Configure for distributed training
            # TODO for students: Add TTL
            # ttl_seconds_after_finished=self.spec.get("ttlSecondsAfterFinished"),
        )

        # Build metadata
        metadata = client.V1ObjectMeta(
            name=self.job_name,
            namespace=self.namespace,
            labels=self.labels,
            # TODO for students: Add annotations, owner references
        )

        # Build job
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=job_spec,
        )

        logger.debug(f"Built job: {self.job_name}")
        return job
