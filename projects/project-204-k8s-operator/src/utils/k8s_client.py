"""Kubernetes client utilities for the operator.

TODO for students: Add support for:
- Multiple cluster connections
- Client pooling and connection reuse
- Retry logic with exponential backoff
- Rate limiting for API calls
"""

import os
from typing import Optional

from kubernetes import client, config
from kubernetes.client import ApiException

from .logger import get_logger

logger = get_logger(__name__)


# Global clients (initialized once)
_core_v1_client: Optional[client.CoreV1Api] = None
_apps_v1_client: Optional[client.AppsV1Api] = None
_batch_v1_client: Optional[client.BatchV1Api] = None
_custom_objects_client: Optional[client.CustomObjectsApi] = None


def initialize_kubernetes_client(in_cluster: Optional[bool] = None) -> None:
    """Initialize Kubernetes client configuration.

    TODO for students: Add support for multiple kubeconfig files

    Args:
        in_cluster: Whether running in-cluster. If None, auto-detect.
    """
    global _core_v1_client, _apps_v1_client, _batch_v1_client, _custom_objects_client

    if in_cluster is None:
        # Auto-detect: check if running in Kubernetes
        in_cluster = os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token")

    try:
        if in_cluster:
            logger.info("Loading in-cluster Kubernetes configuration")
            config.load_incluster_config()
        else:
            logger.info("Loading Kubernetes configuration from kubeconfig")
            config.load_kube_config()

        # Initialize clients
        _core_v1_client = client.CoreV1Api()
        _apps_v1_client = client.AppsV1Api()
        _batch_v1_client = client.BatchV1Api()
        _custom_objects_client = client.CustomObjectsApi()

        logger.info("Kubernetes clients initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Kubernetes client: {e}")
        raise


def get_k8s_client(api: str = "core_v1") -> client.ApiClient:
    """Get a Kubernetes API client.

    TODO for students: Implement client pooling and automatic reconnection

    Args:
        api: API to get client for (core_v1, apps_v1, batch_v1)

    Returns:
        Kubernetes API client

    Raises:
        ValueError: If API is not recognized
        RuntimeError: If clients not initialized
    """
    global _core_v1_client, _apps_v1_client, _batch_v1_client

    # Initialize if not already done
    if _core_v1_client is None:
        initialize_kubernetes_client()

    clients = {
        "core_v1": _core_v1_client,
        "apps_v1": _apps_v1_client,
        "batch_v1": _batch_v1_client,
    }

    if api not in clients:
        raise ValueError(f"Unknown API: {api}. Available: {list(clients.keys())}")

    return clients[api]


def create_custom_object_client() -> client.CustomObjectsApi:
    """Get custom objects API client.

    TODO for students: Add caching and connection pooling

    Returns:
        CustomObjectsApi client
    """
    global _custom_objects_client

    if _custom_objects_client is None:
        initialize_kubernetes_client()

    return _custom_objects_client


def handle_api_exception(e: ApiException, operation: str, resource: str) -> None:
    """Handle Kubernetes API exceptions with logging.

    TODO for students: Add structured error handling and retries

    Args:
        e: API exception
        operation: Operation being performed (create, update, delete)
        resource: Resource being operated on
    """
    if e.status == 404:
        logger.warning(f"{operation} {resource}: Resource not found")
    elif e.status == 409:
        logger.warning(f"{operation} {resource}: Resource already exists or conflict")
    elif e.status == 403:
        logger.error(f"{operation} {resource}: Permission denied")
    else:
        logger.error(f"{operation} {resource}: API error (status={e.status}): {e.reason}")


def patch_custom_resource_status(
    group: str,
    version: str,
    plural: str,
    name: str,
    namespace: str,
    status: dict,
) -> dict:
    """Update status subresource of a custom resource.

    TODO for students: Add retry logic and optimistic locking

    Args:
        group: API group
        version: API version
        plural: Resource plural name
        name: Resource name
        namespace: Resource namespace
        status: Status dict to update

    Returns:
        Updated resource

    Raises:
        ApiException: If update fails
    """
    client_api = create_custom_object_client()

    try:
        # Patch the status subresource
        body = {"status": status}
        result = client_api.patch_namespaced_custom_object_status(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
            body=body,
        )
        logger.debug(f"Updated status for {namespace}/{name}")
        return result

    except ApiException as e:
        handle_api_exception(e, "patch_status", f"{namespace}/{name}")
        raise


def list_custom_resources(
    group: str,
    version: str,
    plural: str,
    namespace: Optional[str] = None,
    label_selector: Optional[str] = None,
) -> dict:
    """List custom resources.

    TODO for students: Add pagination support for large lists

    Args:
        group: API group
        version: API version
        plural: Resource plural name
        namespace: Optional namespace filter
        label_selector: Optional label selector

    Returns:
        List of resources

    Raises:
        ApiException: If list fails
    """
    client_api = create_custom_object_client()

    try:
        if namespace:
            result = client_api.list_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                label_selector=label_selector,
            )
        else:
            result = client_api.list_cluster_custom_object(
                group=group,
                version=version,
                plural=plural,
                label_selector=label_selector,
            )

        return result

    except ApiException as e:
        handle_api_exception(e, "list", plural)
        raise
