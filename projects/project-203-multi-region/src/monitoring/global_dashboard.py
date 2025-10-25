"""Global dashboard data generator for multi-region monitoring.

TODO for students: Generate dashboard data for:
1. Regional health status
2. Cross-region latency
3. Replication lag
4. Cost breakdown by region
5. Traffic distribution
"""

import logging
from dataclasses import dataclass
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class DashboardData:
    """Dashboard data structure."""

    regions: List[str]
    health_status: Dict[str, str]
    latency_ms: Dict[str, float]
    traffic_distribution: Dict[str, float]
    cost_breakdown: Dict[str, float]


class GlobalDashboard:
    """Generates data for global multi-region dashboard.

    TODO for students: Aggregate metrics from all regions
    """

    def __init__(self, regions: List[str]):
        """Initialize global dashboard."""
        self.regions = regions
        logger.info(f"Initialized GlobalDashboard for {len(regions)} regions")

    def get_dashboard_data(self) -> DashboardData:
        """Get current dashboard data.

        TODO for students: Query metrics from monitoring systems
        """
        logger.info("Generating global dashboard data")

        # TODO: Implement data aggregation
        return DashboardData(
            regions=self.regions,
            health_status={r: "unknown" for r in self.regions},
            latency_ms={r: 0.0 for r in self.regions},
            traffic_distribution={r: 0.0 for r in self.regions},
            cost_breakdown={r: 0.0 for r in self.regions},
        )
