"""Metrics aggregation across multiple regions.

TODO for students: Aggregate metrics like:
1. Request latency across regions
2. Error rates per region
3. Resource utilization
4. Replication lag metrics
5. Custom application metrics
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics data."""

    metric_name: str
    by_region: Dict[str, float]
    global_average: float
    timestamp: datetime


class MetricsAggregator:
    """Aggregates metrics from multiple regions.

    TODO for students: Pull metrics from Prometheus/CloudWatch
    """

    def __init__(self, regions: List[str]):
        """Initialize metrics aggregator."""
        self.regions = regions
        logger.info(f"Initialized MetricsAggregator for {len(regions)} regions")

    def aggregate_metric(self, metric_name: str) -> AggregatedMetrics:
        """Aggregate a specific metric across all regions.

        TODO for students: Query and aggregate metric data
        """
        logger.info(f"Aggregating metric: {metric_name}")

        # TODO: Implement metric aggregation
        by_region = {r: 0.0 for r in self.regions}
        global_avg = sum(by_region.values()) / len(by_region) if by_region else 0.0

        return AggregatedMetrics(
            metric_name=metric_name,
            by_region=by_region,
            global_average=global_avg,
            timestamp=datetime.utcnow(),
        )
