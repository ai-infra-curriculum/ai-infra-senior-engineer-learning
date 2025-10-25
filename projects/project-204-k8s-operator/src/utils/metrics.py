"""Metrics collection for the Kubernetes operator.

TODO for students: Implement comprehensive metrics:
- Reconciliation duration histogram
- Error rate counter
- Resource count gauges
- Custom training job metrics
- Integration with Prometheus
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from .logger import get_logger

logger = get_logger(__name__)


class ReconciliationResult(Enum):
    """Result of a reconciliation operation."""

    SUCCESS = "success"
    FAILURE = "failure"
    REQUEUE = "requeue"


@dataclass
class ReconciliationMetric:
    """Metrics for a single reconciliation."""

    resource_name: str
    namespace: str
    result: ReconciliationResult
    duration_seconds: float
    timestamp: datetime
    error_message: Optional[str] = None


@dataclass
class OperatorMetrics:
    """Aggregated metrics for the operator.

    TODO for students: Export these metrics to Prometheus

    Attributes:
        reconciliations_total: Total number of reconciliations
        reconciliations_success: Number of successful reconciliations
        reconciliations_failure: Number of failed reconciliations
        reconciliation_duration: Average reconciliation duration
        active_resources: Current number of active resources
        reconciliation_history: Recent reconciliation metrics
    """

    reconciliations_total: int = 0
    reconciliations_success: int = 0
    reconciliations_failure: int = 0
    reconciliation_duration_total: float = 0.0
    active_resources: int = 0
    reconciliation_history: list = field(default_factory=list)
    max_history_size: int = 100

    def record_reconciliation(
        self,
        resource_name: str,
        namespace: str,
        result: ReconciliationResult,
        duration: float,
        error: Optional[str] = None,
    ) -> None:
        """Record a reconciliation event.

        TODO for students: Export to Prometheus with labels

        Args:
            resource_name: Name of the resource
            namespace: Namespace of the resource
            result: Result of reconciliation
            duration: Duration in seconds
            error: Optional error message
        """
        self.reconciliations_total += 1
        self.reconciliation_duration_total += duration

        if result == ReconciliationResult.SUCCESS:
            self.reconciliations_success += 1
        elif result == ReconciliationResult.FAILURE:
            self.reconciliations_failure += 1

        # Record in history
        metric = ReconciliationMetric(
            resource_name=resource_name,
            namespace=namespace,
            result=result,
            duration_seconds=duration,
            timestamp=datetime.utcnow(),
            error_message=error,
        )

        self.reconciliation_history.append(metric)

        # Trim history if too large
        if len(self.reconciliation_history) > self.max_history_size:
            self.reconciliation_history = self.reconciliation_history[-self.max_history_size:]

        # Log summary
        logger.info(
            f"Reconciliation {result.value}: {namespace}/{resource_name} "
            f"(duration={duration:.2f}s, total={self.reconciliations_total})"
        )

    def get_average_duration(self) -> float:
        """Get average reconciliation duration.

        Returns:
            Average duration in seconds
        """
        if self.reconciliations_total == 0:
            return 0.0
        return self.reconciliation_duration_total / self.reconciliations_total

    def get_success_rate(self) -> float:
        """Get reconciliation success rate.

        Returns:
            Success rate as percentage (0-100)
        """
        if self.reconciliations_total == 0:
            return 0.0
        return (self.reconciliations_success / self.reconciliations_total) * 100

    def get_summary(self) -> Dict[str, any]:
        """Get metrics summary.

        TODO for students: Add more detailed metrics

        Returns:
            Dictionary of metrics
        """
        return {
            "reconciliations_total": self.reconciliations_total,
            "reconciliations_success": self.reconciliations_success,
            "reconciliations_failure": self.reconciliations_failure,
            "success_rate": self.get_success_rate(),
            "average_duration": self.get_average_duration(),
            "active_resources": self.active_resources,
        }


# Global metrics instance
_operator_metrics = OperatorMetrics()


def get_operator_metrics() -> OperatorMetrics:
    """Get the global operator metrics instance.

    Returns:
        Operator metrics
    """
    return _operator_metrics


@contextmanager
def record_reconciliation(
    resource_name: str,
    namespace: str,
):
    """Context manager to record reconciliation metrics.

    TODO for students: Add automatic error capture and timing

    Usage:
        with record_reconciliation("my-job", "default") as result:
            # Perform reconciliation
            if success:
                result.mark_success()
            else:
                result.mark_failure("Error message")

    Args:
        resource_name: Name of the resource
        namespace: Namespace of the resource

    Yields:
        ReconciliationRecorder instance
    """
    recorder = ReconciliationRecorder(resource_name, namespace)
    start_time = time.time()

    try:
        yield recorder
    except Exception as e:
        recorder.mark_failure(str(e))
        raise
    finally:
        duration = time.time() - start_time
        recorder.finalize(duration)


class ReconciliationRecorder:
    """Helper class for recording reconciliation results.

    TODO for students: Add more context and metadata capture
    """

    def __init__(self, resource_name: str, namespace: str):
        """Initialize reconciliation recorder."""
        self.resource_name = resource_name
        self.namespace = namespace
        self.result = ReconciliationResult.SUCCESS
        self.error_message: Optional[str] = None

    def mark_success(self) -> None:
        """Mark reconciliation as successful."""
        self.result = ReconciliationResult.SUCCESS
        self.error_message = None

    def mark_failure(self, error: str) -> None:
        """Mark reconciliation as failed.

        Args:
            error: Error message
        """
        self.result = ReconciliationResult.FAILURE
        self.error_message = error

    def mark_requeue(self) -> None:
        """Mark reconciliation for requeue."""
        self.result = ReconciliationResult.REQUEUE

    def finalize(self, duration: float) -> None:
        """Finalize and record the metrics.

        Args:
            duration: Duration in seconds
        """
        metrics = get_operator_metrics()
        metrics.record_reconciliation(
            resource_name=self.resource_name,
            namespace=self.namespace,
            result=self.result,
            duration=duration,
            error=self.error_message,
        )
