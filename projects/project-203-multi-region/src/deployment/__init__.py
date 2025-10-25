"""
Multi-Region Deployment Orchestration Module

Coordinates deployments across multiple regions with health checks,
rollout strategies, and automated validation.

TODO for students:
- Implement blue-green deployments per region
- Add canary deployments with automatic promotion
- Create deployment pipelines with approval gates
- Implement automated rollback on failure
"""

from .multi_region_orchestrator import (
    MultiRegionOrchestrator,
    DeploymentPlan,
    orchestrate_deployment,
)
from .region_manager import (
    RegionManager,
    Region,
    manage_region,
)
from .health_checker import (
    HealthChecker,
    check_region_health,
    HealthStatus,
)

__all__ = [
    # Orchestration
    "MultiRegionOrchestrator",
    "DeploymentPlan",
    "orchestrate_deployment",
    # Region Management
    "RegionManager",
    "Region",
    "manage_region",
    # Health Checks
    "HealthChecker",
    "check_region_health",
    "HealthStatus",
]
