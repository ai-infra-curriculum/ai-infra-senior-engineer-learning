"""
Global Multi-Region Monitoring Module

Provides unified observability across all regions with aggregated metrics,
global dashboards, and cross-region alerting.

TODO for students:
- Implement distributed tracing across regions
- Add latency maps for global routing
- Create SLO dashboards per region
- Implement anomaly detection across regions
"""

from .global_dashboard import (
    GlobalDashboard,
    create_dashboard,
    update_dashboard,
)
from .metrics_aggregator import (
    MetricsAggregator,
    aggregate_metrics,
    RegionMetrics,
)
from .alerting import (
    AlertManager,
    create_alert,
    CrossRegionAlert,
)

__all__ = [
    # Dashboard
    "GlobalDashboard",
    "create_dashboard",
    "update_dashboard",
    # Metrics
    "MetricsAggregator",
    "aggregate_metrics",
    "RegionMetrics",
    # Alerting
    "AlertManager",
    "create_alert",
    "CrossRegionAlert",
]
