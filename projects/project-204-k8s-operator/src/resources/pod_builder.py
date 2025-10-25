"""Builder for creating Pod specifications for TrainingJobs.

TODO for students: Add support for:
- Init containers for setup tasks
- Sidecar containers for monitoring
- Volume mounts for checkpoints and data
- Security contexts and pod security policies
- Resource quotas and limits
- Affinity and anti-affinity rules
- Tolerations for dedicated nodes
"""

from typing import Dict, Any, List, Optional

from kubernetes import client

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PodBuilder:
    """Builder for creating Pod specifications.

    TODO for students: Implement builder pattern methods:
    - with_volumes()
    - with_environment()
    - with_node_selector()
    - with_tolerations()
    - with_affinity()
    - with_security_context()
    - with_init_containers()

    Attributes:
        job_name: TrainingJob name
        namespace: Kubernetes namespace
        replica_id: Replica ID for distributed training
        spec: TrainingJob spec
        labels: Pod labels
    """

    def __init__(
        self,
        job_name: str,
        namespace: str,
        replica_id: int = 0,
    ):
        """Initialize pod builder.

        Args:
            job_name: TrainingJob name
            namespace: Namespace
            replica_id: Replica ID (0-based)
        """
        self.job_name = job_name
        self.namespace = namespace
        self.replica_id = replica_id
        self.spec: Dict[str, Any] = {}
        self.labels = {
            "trainingjob": job_name,
            "replica-id": str(replica_id),
            "app": "ml-training",
        }
        logger.debug(f"PodBuilder initialized for {job_name}-{replica_id}")

    def with_spec(self, spec: Dict[str, Any]) -> "PodBuilder":
        """Set the TrainingJob spec.

        Args:
            spec: TrainingJob spec

        Returns:
            Self for method chaining
        """
        self.spec = spec
        return self

    def with_labels(self, labels: Dict[str, str]) -> "PodBuilder":
        """Add custom labels.

        Args:
            labels: Labels to add

        Returns:
            Self for method chaining
        """
        self.labels.update(labels)
        return self

    def build(self) -> client.V1Pod:
        """Build the Pod object.

        TODO for students: Implement complete pod creation:
        - Add volumes and volume mounts
        - Configure distributed training env vars
        - Set up resource requests/limits
        - Add node selectors
        - Configure tolerations
        - Set owner references
        - Add annotations

        Returns:
            V1Pod object
        """
        pod_name = f"{self.job_name}-{self.replica_id}"

        # Build container spec
        container = self._build_container()

        # Build pod spec
        pod_spec = client.V1PodSpec(
            containers=[container],
            restart_policy=self.spec.get("restartPolicy", "OnFailure"),
            # TODO for students: Add volumes, service account, etc.
        )

        # Build metadata
        metadata = client.V1ObjectMeta(
            name=pod_name,
            namespace=self.namespace,
            labels=self.labels,
            # TODO for students: Add annotations, owner references
        )

        # Build pod
        pod = client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=pod_spec,
        )

        logger.debug(f"Built pod: {pod_name}")
        return pod

    def _build_container(self) -> client.V1Container:
        """Build the main training container.

        TODO for students: Add:
        - Volume mounts
        - Environment variables for distributed training
        - Liveness and readiness probes
        - Security context
        - Lifecycle hooks

        Returns:
            V1Container object
        """
        image = self.spec.get("image", "")
        command = self.spec.get("command", [])
        args = self.spec.get("args", [])

        # Build resource requirements
        resources = self._build_resources()

        # Build environment variables
        env_vars = self._build_env_vars()

        # Build container
        container = client.V1Container(
            name="training",
            image=image,
            command=command if command else None,
            args=args if args else None,
            resources=resources,
            env=env_vars,
            # TODO for students: Add volume mounts, ports, probes
        )

        return container

    def _build_resources(self) -> Optional[client.V1ResourceRequirements]:
        """Build resource requirements.

        TODO for students: Add GPU resource handling

        Returns:
            V1ResourceRequirements or None
        """
        resources_spec = self.spec.get("resources")
        if not resources_spec:
            return None

        requests = resources_spec.get("requests", {})
        limits = resources_spec.get("limits", {})

        return client.V1ResourceRequirements(
            requests=requests if requests else None,
            limits=limits if limits else None,
        )

    def _build_env_vars(self) -> List[client.V1EnvVar]:
        """Build environment variables.

        TODO for students: Add distributed training env vars:
        - MASTER_ADDR
        - MASTER_PORT
        - WORLD_SIZE
        - RANK
        - LOCAL_RANK
        - NCCL_* variables

        Returns:
            List of V1EnvVar objects
        """
        env_vars = []

        # Add user-defined env vars
        for env_spec in self.spec.get("env", []):
            env_var = client.V1EnvVar(
                name=env_spec["name"],
                value=env_spec.get("value"),
            )
            env_vars.append(env_var)

        # Add replica ID for distributed training
        env_vars.append(
            client.V1EnvVar(
                name="REPLICA_ID",
                value=str(self.replica_id),
            )
        )

        # TODO for students: Add framework-specific env vars
        # framework = self.spec.get("framework")
        # if framework == "pytorch":
        #     env_vars.extend(self._build_pytorch_env_vars())
        # elif framework == "tensorflow":
        #     env_vars.extend(self._build_tensorflow_env_vars())

        return env_vars

    def _build_volumes(self) -> List[client.V1Volume]:
        """Build volumes for the pod.

        TODO for students: Implement:
        - Checkpoint storage volume (PVC, emptyDir, or cloud storage)
        - Data volume for training data
        - Config volume for configuration files
        - Secret volumes for credentials

        Returns:
            List of V1Volume objects
        """
        volumes = []

        # TODO for students: Add checkpoint volume
        # checkpoint_config = self.spec.get("checkpoint", {})
        # if checkpoint_config.get("enabled"):
        #     storage = checkpoint_config.get("storage", "pvc")
        #     if storage == "pvc":
        #         volumes.append(self._build_pvc_volume("checkpoints"))
        #     elif storage == "emptyDir":
        #         volumes.append(self._build_emptydir_volume("checkpoints"))

        return volumes

    def _build_volume_mounts(self) -> List[client.V1VolumeMount]:
        """Build volume mounts for the container.

        TODO for students: Implement volume mounts matching volumes

        Returns:
            List of V1VolumeMount objects
        """
        volume_mounts = []

        # TODO for students: Add checkpoint volume mount
        # checkpoint_config = self.spec.get("checkpoint", {})
        # if checkpoint_config.get("enabled"):
        #     path = checkpoint_config.get("path", "/checkpoints")
        #     volume_mounts.append(
        #         client.V1VolumeMount(
        #             name="checkpoints",
        #             mount_path=path,
        #         )
        #     )

        return volume_mounts
