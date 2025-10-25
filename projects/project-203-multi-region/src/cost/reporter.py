"""Cost reporting and visualization.

TODO for students: Generate cost reports with:
1. Monthly/weekly cost summaries
2. Cost trends and forecasts
3. Regional comparisons
4. Resource type breakdowns
5. Export to CSV/PDF
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class CostReport:
    """Cost report data structure."""

    report_id: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    by_region: Dict[str, float]
    by_resource_type: Dict[str, float]
    generated_at: datetime


class CostReporter:
    """Generates cost reports for multi-region deployments.

    TODO for students: Implement report generation and export
    """

    def __init__(self, regions: List[str]):
        """Initialize cost reporter."""
        self.regions = regions
        logger.info(f"Initialized CostReporter for {len(regions)} regions")

    def generate_report(self, days: int = 30) -> CostReport:
        """Generate cost report for specified period.

        TODO for students: Aggregate cost data and format report
        """
        logger.info(f"Generating cost report for last {days} days")

        # TODO: Implement report generation
        return CostReport(
            report_id=f"report-{datetime.utcnow().timestamp()}",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            total_cost=0.0,
            by_region={r: 0.0 for r in self.regions},
            by_resource_type={},
            generated_at=datetime.utcnow(),
        )
