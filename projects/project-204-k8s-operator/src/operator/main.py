"""Main entry point for the TrainingJob Kubernetes operator.

TODO for students: Add:
- Configuration file support
- Command-line argument parsing
- Health check endpoint
- Leader election for HA
- Metrics endpoint
- Graceful shutdown handling
- Signal handling (SIGTERM, SIGINT)
"""

import argparse
import signal
import sys
from typing import Optional

from ..utils.logger import setup_logging, get_logger
from ..utils.k8s_client import initialize_kubernetes_client
from ..utils.metrics import get_operator_metrics
from ..crd.trainingjob_crd import get_trainingjob_crd
from .reconciler import Reconciler

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    TODO for students: Add more configuration options:
    - --config: Path to config file
    - --namespace: Namespace to watch
    - --workers: Number of worker threads
    - --resync-period: Resync period in seconds
    - --metrics-port: Metrics server port
    - --health-port: Health check port

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="TrainingJob Kubernetes Operator"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level",
    )

    parser.add_argument(
        "--namespace",
        default=None,
        help="Namespace to watch (default: all namespaces)",
    )

    parser.add_argument(
        "--install-crd",
        action="store_true",
        help="Install/update TrainingJob CRD",
    )

    # TODO for students: Add more arguments

    return parser.parse_args()


def install_crd() -> bool:
    """Install or update the TrainingJob CRD.

    TODO for students: Implement CRD installation:
    - Check if CRD exists
    - Create or update CRD
    - Validate CRD installation
    - Handle errors gracefully

    Returns:
        True if successful
    """
    logger.info("Installing TrainingJob CRD...")

    try:
        crd_manifest = get_trainingjob_crd()

        # TODO for students: Implement CRD creation/update
        # from kubernetes import client
        # api = client.ApiextensionsV1Api()
        # try:
        #     api.create_custom_resource_definition(crd_manifest)
        #     logger.info("CRD created successfully")
        # except client.ApiException as e:
        #     if e.status == 409:  # Already exists
        #         api.patch_custom_resource_definition(
        #             crd_manifest["metadata"]["name"],
        #             crd_manifest
        #         )
        #         logger.info("CRD updated successfully")
        #     else:
        #         raise

        logger.info("TrainingJob CRD installed successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to install CRD: {e}")
        return False


def setup_signal_handlers(reconciler: Reconciler) -> None:
    """Set up signal handlers for graceful shutdown.

    TODO for students: Implement graceful shutdown:
    - Finish in-progress reconciliations
    - Save operator state
    - Close connections
    - Cleanup resources

    Args:
        reconciler: Reconciler instance
    """
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down gracefully...")

        # TODO for students: Implement shutdown logic
        # reconciler.stop()

        # Print final metrics
        metrics = get_operator_metrics()
        logger.info(f"Final metrics: {metrics.get_summary()}")

        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_operator(namespace: Optional[str] = None) -> None:
    """Run the operator main loop.

    TODO for students: Implement:
    - Start metrics server
    - Start health check server
    - Start reconciler
    - Monitor operator health
    - Handle errors and restarts

    Args:
        namespace: Namespace to watch (None for all namespaces)
    """
    logger.info("Starting TrainingJob Operator")
    logger.info(f"Watching namespace: {namespace or 'all'}")

    # Initialize Kubernetes client
    try:
        initialize_kubernetes_client()
    except Exception as e:
        logger.error(f"Failed to initialize Kubernetes client: {e}")
        sys.exit(1)

    # Create reconciler
    reconciler = Reconciler(namespace=namespace)

    # Set up signal handlers
    setup_signal_handlers(reconciler)

    # TODO for students: Start metrics server
    # from prometheus_client import start_http_server
    # start_http_server(8000)
    # logger.info("Metrics server started on port 8000")

    # TODO for students: Start health check server
    # start_health_server(8080)

    # Start reconciliation loop
    try:
        logger.info("Starting reconciliation loop")
        reconciler.run()
    except KeyboardInterrupt:
        logger.info("Operator stopped by user")
    except Exception as e:
        logger.exception(f"Operator failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point.

    TODO for students: Add:
    - Version command
    - Configuration validation
    - Pre-flight checks
    - Operator registration
    """
    args = parse_args()

    # Setup logging
    setup_logging(level=args.log_level)

    logger.info("TrainingJob Kubernetes Operator")
    logger.info("================================")

    # Install CRD if requested
    if args.install_crd:
        if not install_crd():
            sys.exit(1)
        logger.info("CRD installation complete")
        return

    # Run operator
    run_operator(namespace=args.namespace)


if __name__ == "__main__":
    main()
