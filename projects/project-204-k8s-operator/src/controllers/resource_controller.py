"""Controller for managing Kubernetes resources for TrainingJobs.

TODO for students: Add support for:
- PersistentVolumeClaims for storage
- ConfigMaps for configuration
- Secrets for credentials
- ServiceAccounts and RBAC
- NetworkPolicies for security
- HorizontalPodAutoscaler for autoscaling
"""

from typing import Dict, Any, List, Optional

from kubernetes import client
from kubernetes.client import ApiException, V1Pod, V1Service, V1PodList

from ..utils.logger import get_logger
from ..utils.k8s_client import get_k8s_client, handle_api_exception
from ..resources.pod_builder import PodBuilder
from ..resources.service_builder import ServiceBuilder

logger = get_logger(__name__)


class ResourceController:
    """Controller for managing Kubernetes resources.

    TODO for students: Implement:
    - Resource ownership and garbage collection
    - Resource update strategies (rolling, recreate)
    - Resource status monitoring
    - Resource cleanup and finalization
    - Resource quota management

    Attributes:
        core_api: Kubernetes Core API client
        apps_api: Kubernetes Apps API client
    """

    def __init__(self):
        """Initialize resource controller.

        TODO for students: Add resource caching for performance
        """
        self.core_api = get_k8s_client("core_v1")
        self.apps_api = get_k8s_client("apps_v1")
        logger.info("ResourceController initialized")

    def create_training_pods(
        self, job_name: str, namespace: str, spec: Dict[str, Any]
    ) -> List[V1Pod]:
        """Create pods for a training job.

        TODO for students: Implement:
        - Create pods based on replica count
        - Set up distributed training environment variables
        - Configure resource requests/limits
        - Add owner references for garbage collection
        - Set up volume mounts for checkpoints
        - Configure node affinity and tolerations

        Args:
            job_name: TrainingJob name
            namespace: Namespace
            spec: TrainingJob spec

        Returns:
            List of created pods
        """
        logger.info(f"Creating training pods for {namespace}/{job_name}")

        replicas = spec.get("replicas", 1)
        pods = []

        # TODO for students: Use PodBuilder to create pods
        # for replica_id in range(replicas):
        #     pod_builder = PodBuilder(job_name, namespace, replica_id)
        #     pod = pod_builder.with_spec(spec).build()
        #     created_pod = self.core_api.create_namespaced_pod(namespace, pod)
        #     pods.append(created_pod)

        logger.info(f"Created {len(pods)} training pods")
        return pods

    def create_training_services(
        self, job_name: str, namespace: str, spec: Dict[str, Any]
    ) -> List[V1Service]:
        """Create services for distributed training.

        TODO for students: Implement:
        - Create headless service for pod discovery
        - Create service for master/coordinator
        - Configure service ports based on framework
        - Set up service monitors for Prometheus

        Args:
            job_name: TrainingJob name
            namespace: Namespace
            spec: TrainingJob spec

        Returns:
            List of created services
        """
        logger.info(f"Creating training services for {namespace}/{job_name}")

        services = []

        # TODO for students: Use ServiceBuilder to create services
        # service_builder = ServiceBuilder(job_name, namespace)
        # service = service_builder.with_spec(spec).build()
        # created_service = self.core_api.create_namespaced_service(namespace, service)
        # services.append(created_service)

        logger.info(f"Created {len(services)} training services")
        return services

    def get_pod_status(
        self, job_name: str, namespace: str
    ) -> Dict[str, Any]:
        """Get status of pods for a training job.

        TODO for students: Implement:
        - Query pod status
        - Aggregate pod conditions
        - Calculate readiness status
        - Track resource usage
        - Monitor pod events

        Args:
            job_name: TrainingJob name
            namespace: Namespace

        Returns:
            Dictionary with pod status information
        """
        try:
            label_selector = f"trainingjob={job_name}"
            pod_list: V1PodList = self.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
            )

            status = {
                "total": len(pod_list.items),
                "running": 0,
                "succeeded": 0,
                "failed": 0,
                "pending": 0,
                "unknown": 0,
                "pods": [],
            }

            for pod in pod_list.items:
                phase = pod.status.phase
                pod_info = {
                    "name": pod.metadata.name,
                    "phase": phase,
                    "ready": self._is_pod_ready(pod),
                }

                # Count by phase
                if phase == "Running":
                    status["running"] += 1
                elif phase == "Succeeded":
                    status["succeeded"] += 1
                elif phase == "Failed":
                    status["failed"] += 1
                elif phase == "Pending":
                    status["pending"] += 1
                else:
                    status["unknown"] += 1

                status["pods"].append(pod_info)

            return status

        except ApiException as e:
            handle_api_exception(e, "list", f"pods for {namespace}/{job_name}")
            raise

    def delete_job_resources(
        self, job_name: str, namespace: str
    ) -> None:
        """Delete all resources for a training job.

        TODO for students: Implement:
        - Delete pods gracefully
        - Delete services
        - Delete ConfigMaps
        - Delete PVCs (based on policy)
        - Wait for deletion to complete
        - Handle deletion errors

        Args:
            job_name: TrainingJob name
            namespace: Namespace
        """
        logger.info(f"Deleting resources for {namespace}/{job_name}")

        label_selector = f"trainingjob={job_name}"

        try:
            # Delete pods
            self.core_api.delete_collection_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
            )
            logger.info(f"Deleted pods for {namespace}/{job_name}")

            # TODO for students: Delete other resources
            # - Services
            # - ConfigMaps
            # - PVCs (if policy allows)
            # - Secrets

        except ApiException as e:
            handle_api_exception(e, "delete", f"resources for {namespace}/{job_name}")
            raise

    def cleanup_job_resources(
        self, job_name: str, namespace: str
    ) -> None:
        """Clean up resources after job completion.

        TODO for students: Implement:
        - Respect TTL for completed jobs
        - Archive logs before deletion
        - Preserve checkpoints
        - Create final metrics snapshot
        - Delete temporary resources only

        Args:
            job_name: TrainingJob name
            namespace: Namespace
        """
        logger.info(f"Cleaning up resources for {namespace}/{job_name}")

        # TODO for students: Implement selective cleanup
        # - Delete failed/completed pods
        # - Keep services for debugging (with TTL)
        # - Archive logs to persistent storage
        # - Keep checkpoints based on retention policy

    def update_pod_replicas(
        self, job_name: str, namespace: str, new_replicas: int
    ) -> None:
        """Update number of pod replicas for a training job.

        TODO for students: Implement:
        - Scale up by creating new pods
        - Scale down by gracefully terminating pods
        - Update distributed training configuration
        - Coordinate with checkpoint controller
        - Handle in-flight training gracefully

        Args:
            job_name: TrainingJob name
            namespace: Namespace
            new_replicas: New replica count
        """
        logger.info(
            f"Updating replicas for {namespace}/{job_name} to {new_replicas}"
        )

        # TODO for students: Implement scaling logic
        # current_pods = self.get_pod_status(job_name, namespace)["total"]
        # if new_replicas > current_pods:
        #     # Scale up
        #     self._scale_up(job_name, namespace, new_replicas - current_pods)
        # elif new_replicas < current_pods:
        #     # Scale down
        #     self._scale_down(job_name, namespace, current_pods - new_replicas)

    def _is_pod_ready(self, pod: V1Pod) -> bool:
        """Check if a pod is ready.

        TODO for students: Add more sophisticated readiness checks

        Args:
            pod: Pod object

        Returns:
            True if pod is ready
        """
        if not pod.status or not pod.status.conditions:
            return False

        for condition in pod.status.conditions:
            if condition.type == "Ready" and condition.status == "True":
                return True

        return False
