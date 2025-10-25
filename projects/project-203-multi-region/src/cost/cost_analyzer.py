"""Multi-region cost analysis and reporting.

TODO for students: Implement cost tracking for:
1. Compute resources (VMs, containers)
2. Storage (object storage, block storage)
3. Network transfer between regions
4. Managed services (databases, caches)
5. Cost trends and forecasting
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Cloud resource types for cost tracking."""

    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"


@dataclass
class CostEntry:
    """Individual cost entry."""

    resource_id: str
    resource_type: ResourceType
    region: str
    cost_usd: float
    timestamp: datetime
    usage_amount: float
    usage_unit: str


@dataclass
class CostSummary:
    """Cost summary for a time period."""

    total_cost: float
    by_region: Dict[str, float]
    by_resource_type: Dict[str, float]
    start_date: datetime
    end_date: datetime


class CostAnalyzer:
    """Analyzes costs across multiple regions.

    TODO for students: Implement the following methods:
    1. get_cost_by_region() - Get costs per region
    2. get_cost_by_resource_type() - Get costs per resource type
    3. get_cost_trends() - Analyze cost trends over time
    4. compare_regions() - Compare costs between regions
    5. forecast_costs() - Predict future costs

    Example usage:
        analyzer = CostAnalyzer(["us-east-1", "eu-west-1"])
        summary = analyzer.get_cost_summary(days=30)
        print(f"Total cost: ${summary.total_cost:.2f}")
    """

    def __init__(self, regions: List[str]):
        """Initialize cost analyzer."""
        self.regions = regions
        self.cost_data: List[CostEntry] = []
        logger.info(f"Initialized CostAnalyzer for regions: {regions}")

    def get_cost_summary(self, days: int = 30) -> CostSummary:
        """Get cost summary for the specified period.

        TODO for students: Aggregate costs from cloud provider APIs
        """
        logger.info(f"Getting cost summary for last {days} days")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # TODO: Implement cost aggregation
        return CostSummary(
            total_cost=0.0,
            by_region={region: 0.0 for region in self.regions},
            by_resource_type={rt.value: 0.0 for rt in ResourceType},
            start_date=start_date,
            end_date=end_date,
        )

    def get_cost_by_region(self, days: int = 30) -> Dict[str, float]:
        """Get costs broken down by region.

        TODO for students: Query costs from cloud provider billing APIs
        """
        logger.info(f"Getting costs by region (last {days} days)")

        # TODO: Implement region cost breakdown
        return {region: 0.0 for region in self.regions}

    def get_cost_trends(self, days: int = 90) -> Dict[str, List[float]]:
        """Analyze cost trends over time.

        TODO for students: Calculate daily/weekly trends
        """
        logger.info(f"Analyzing cost trends (last {days} days)")

        # TODO: Implement trend analysis
        return {}

    def forecast_costs(self, forecast_days: int = 30) -> Dict[str, float]:
        """Forecast costs for the next period.

        TODO for students: Use linear regression or time series forecasting
        """
        logger.info(f"Forecasting costs for next {forecast_days} days")

        # TODO: Implement cost forecasting
        return {region: 0.0 for region in self.regions}
