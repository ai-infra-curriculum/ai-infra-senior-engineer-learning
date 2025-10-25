"""Builder for creating Kubernetes Service resources for TrainingJobs.

TODO for students: Add support for:
- Headless services for distributed training
- Service monitors for Prometheus
- External access configurations
- Multiple service types (ClusterIP, NodePort, LoadBalancer)
"""

from typing import Dict, Any, List, Optional

from kubernetes import client

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ServiceBuilder:
    """Builder for creating Kubernetes Service resources.

    TODO for students: Implement builder methods for:
    - Service type configuration
    - Port configuration
    - Session affinity
    - Service annotations
    - External IPs

    Attributes:
        job_name: TrainingJob name
        namespace: Kubernetes namespace
        spec: TrainingJob spec
        labels: Service labels
        service_type: Service type (ClusterIP, NodePort, LoadBalancer)
    """

    def __init__(
        self,
        job_name: str,
        namespace: str,
        service_type: str = "ClusterIP",
    ):
        """Initialize service builder.

        Args:
            job_name: TrainingJob name
            namespace: Namespace
            service_type: Kubernetes service type
        """
        self.job_name = job_name
        self.namespace = namespace
        self.service_type = service_type
        self.spec: Dict[str, Any] = {}
        self.labels = {
            "trainingjob": job_name,
            "app": "ml-training",
        }
        logger.debug(f"ServiceBuilder initialized for {job_name}")

    def with_spec(self, spec: Dict[str, Any]) -> "ServiceBuilder":
        """Set the TrainingJob spec.

        Args:
            spec: TrainingJob spec

        Returns:
            Self for method chaining
        """
        self.spec = spec
        return self

    def build_headless_service(self) -> client.V1Service:
        """Build a headless service for distributed training.

        TODO for students: Implement headless service for:
        - Pod DNS records for peer discovery
        - Direct pod-to-pod communication
        - Distributed training coordination

        A headless service (clusterIP: None) creates DNS records for each pod,
        allowing pods to discover each other by DNS name.

        Returns:
            V1Service object for headless service
        """
        service_name = f"{self.job_name}-headless"

        # Build service spec (headless)
        service_spec = client.V1ServiceSpec(
            cluster_ip="None",  # Headless service
            selector={"trainingjob": self.job_name},
            ports=self._build_service_ports(),
            # Publish not-ready addresses for distributed training coordination
            publish_not_ready_addresses=True,
        )

        # Build metadata
        metadata = client.V1ObjectMeta(
            name=service_name,
            namespace=self.namespace,
            labels=self.labels,
            # TODO for students: Add annotations for service mesh, metrics
        )

        # Build service
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=metadata,
            spec=service_spec,
        )

        logger.debug(f"Built headless service: {service_name}")
        return service

    def build_master_service(self) -> client.V1Service:
        """Build a service for the master/coordinator pod.

        TODO for students: Implement master service for:
        - Single entry point to training cluster
        - Metrics collection endpoint
        - Monitoring integration

        Returns:
            V1Service object for master service
        """
        service_name = f"{self.job_name}-master"

        # Build service spec
        service_spec = client.V1ServiceSpec(
            type=self.service_type,
            selector={
                "trainingjob": self.job_name,
                "replica-id": "0",  # Select only master pod
            },
            ports=self._build_service_ports(),
        )

        # Build metadata
        metadata = client.V1ObjectMeta(
            name=service_name,
            namespace=self.namespace,
            labels=self.labels,
            # TODO for students: Add Prometheus annotations
            # annotations={
            #     "prometheus.io/scrape": "true",
            #     "prometheus.io/port": str(monitoring_port),
            #     "prometheus.io/path": "/metrics",
            # }
        )

        # Build service
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=metadata,
            spec=service_spec,
        )

        logger.debug(f"Built master service: {service_name}")
        return service

    def _build_service_ports(self) -> List[client.V1ServicePort]:
        """Build service port specifications.

        TODO for students: Add framework-specific ports:
        - PyTorch DDP: 29500 (default)
        - TensorFlow: 2222 (parameter server)
        - Horovod: 12345 (gloo/mpi)
        - Monitoring: 9090 (metrics)

        Returns:
            List of V1ServicePort objects
        """
        ports = []

        # Add monitoring port if enabled
        monitoring_config = self.spec.get("monitoring", {})
        if monitoring_config.get("enabled", True):
            monitoring_port = monitoring_config.get("port", 9090)
            ports.append(
                client.V1ServicePort(
                    name="metrics",
                    port=monitoring_port,
                    target_port=monitoring_port,
                    protocol="TCP",
                )
            )

        # TODO for students: Add framework-specific ports
        # framework = self.spec.get("framework", "pytorch")
        # if framework == "pytorch":
        #     ports.append(
        #         client.V1ServicePort(
        #             name="ddp",
        #             port=29500,
        #             target_port=29500,
        #             protocol="TCP",
        #         )
        #     )

        # Default port if none specified
        if not ports:
            ports.append(
                client.V1ServicePort(
                    name="default",
                    port=8080,
                    target_port=8080,
                    protocol="TCP",
                )
            )

        return ports
