"""Reconciler - Watches for TrainingJob events and triggers reconciliation.

TODO for students: Implement:
- Watch mechanism using kubernetes.watch
- Event queue for async processing
- Worker threads for concurrent reconciliation
- Periodic resync
- Error handling and retry logic
- Resource event filtering
"""

import time
from typing import Optional
from threading import Thread, Event

from kubernetes import watch

from ..utils.logger import get_logger
from ..utils.k8s_client import create_custom_object_client
from ..controllers.job_controller import JobController

logger = get_logger(__name__)


class Reconciler:
    """Reconciler watches for TrainingJob events and triggers reconciliation.

    TODO for students: Implement:
    - Kubernetes watch for TrainingJob resources
    - Event queue with priority
    - Worker pool for concurrent reconciliation
    - Backoff/retry on reconciliation failures
    - Periodic full resync
    - Resource version tracking
    - Leader election support

    Attributes:
        namespace: Namespace to watch (None for all)
        controller: JobController for reconciliation
        stop_event: Event to signal shutdown
    """

    def __init__(
        self,
        namespace: Optional[str] = None,
        resync_period: int = 300,
    ):
        """Initialize reconciler.

        TODO for students: Add configuration options:
        - Number of worker threads
        - Queue size
        - Reconciliation timeout

        Args:
            namespace: Namespace to watch
            resync_period: Resync period in seconds
        """
        self.namespace = namespace
        self.resync_period = resync_period
        self.client = create_custom_object_client()
        self.controller = JobController(namespace=namespace)
        self.stop_event = Event()

        # CRD details
        self.group = "mlplatform.example.com"
        self.version = "v1alpha1"
        self.plural = "trainingjobs"

        logger.info(f"Reconciler initialized (namespace={namespace or 'all'})")

    def run(self) -> None:
        """Run the reconciliation loop.

        TODO for students: Implement complete watch loop:
        - Start watch on TrainingJob resources
        - Handle ADDED, MODIFIED, DELETED events
        - Queue events for processing
        - Start worker threads
        - Handle watch errors and reconnection
        - Implement periodic resync

        This is a simple implementation. Students should enhance it.
        """
        logger.info("Starting reconciliation loop")

        # Start periodic resync in background
        # TODO for students: Implement proper threading
        # resync_thread = Thread(target=self._periodic_resync, daemon=True)
        # resync_thread.start()

        while not self.stop_event.is_set():
            try:
                self._watch_resources()
            except Exception as e:
                logger.error(f"Watch failed: {e}, retrying in 5s...")
                time.sleep(5)

    def _watch_resources(self) -> None:
        """Watch TrainingJob resources and handle events.

        TODO for students: Implement complete watch handling:
        - Handle all event types (ADDED, MODIFIED, DELETED, BOOKMARK, ERROR)
        - Track resource versions
        - Handle watch timeout and reconnection
        - Filter events (only reconcile on relevant changes)
        """
        logger.info("Starting watch on TrainingJob resources")

        w = watch.Watch()

        try:
            # Watch for TrainingJob events
            if self.namespace:
                stream = w.stream(
                    self.client.list_namespaced_custom_object,
                    group=self.group,
                    version=self.version,
                    namespace=self.namespace,
                    plural=self.plural,
                    timeout_seconds=60,
                )
            else:
                stream = w.stream(
                    self.client.list_cluster_custom_object,
                    group=self.group,
                    version=self.version,
                    plural=self.plural,
                    timeout_seconds=60,
                )

            for event in stream:
                if self.stop_event.is_set():
                    break

                event_type = event["type"]
                obj = event["object"]

                # Extract metadata
                metadata = obj.get("metadata", {})
                name = metadata.get("name")
                namespace = metadata.get("namespace")

                logger.debug(f"Event {event_type}: {namespace}/{name}")

                # Handle event
                if event_type in ["ADDED", "MODIFIED"]:
                    # Reconcile the resource
                    self._reconcile(name, namespace)
                elif event_type == "DELETED":
                    # Handle deletion
                    logger.info(f"TrainingJob deleted: {namespace}/{name}")
                    # TODO for students: Cleanup resources if needed
                elif event_type == "ERROR":
                    logger.error(f"Watch error: {obj}")

        except Exception as e:
            logger.error(f"Watch stream error: {e}")
            raise
        finally:
            w.stop()

    def _reconcile(self, name: str, namespace: str) -> None:
        """Reconcile a single TrainingJob.

        TODO for students: Implement:
        - Queue event for async processing
        - Rate limiting
        - Deduplication
        - Error handling

        Args:
            name: TrainingJob name
            namespace: Namespace
        """
        try:
            logger.debug(f"Reconciling {namespace}/{name}")
            self.controller.reconcile(name, namespace)
        except Exception as e:
            logger.error(f"Reconciliation failed for {namespace}/{name}: {e}")
            # TODO for students: Implement retry with backoff

    def _periodic_resync(self) -> None:
        """Periodically resync all resources.

        TODO for students: Implement periodic resync:
        - List all TrainingJob resources
        - Reconcile each one
        - Sleep for resync_period
        - Handle errors

        Periodic resync ensures eventual consistency even if events are missed.
        """
        logger.info(f"Starting periodic resync (period={self.resync_period}s)")

        while not self.stop_event.is_set():
            try:
                time.sleep(self.resync_period)

                if self.stop_event.is_set():
                    break

                logger.info("Performing periodic resync")
                jobs = self.controller.list_training_jobs(namespace=self.namespace)

                for job in jobs:
                    metadata = job.get("metadata", {})
                    name = metadata.get("name")
                    namespace = metadata.get("namespace")
                    self._reconcile(name, namespace)

                logger.info(f"Periodic resync completed ({len(jobs)} jobs)")

            except Exception as e:
                logger.error(f"Periodic resync failed: {e}")

    def stop(self) -> None:
        """Stop the reconciler.

        TODO for students: Implement graceful shutdown:
        - Stop watch
        - Wait for in-progress reconciliations
        - Save state
        - Cleanup resources
        """
        logger.info("Stopping reconciler")
        self.stop_event.set()
