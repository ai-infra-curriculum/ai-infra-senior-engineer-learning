"""Region lifecycle management.

TODO for students: Implement region operations:
1. Add new region to deployment
2. Remove region from deployment
3. Update region configuration
4. Scale resources per region
5. Region status monitoring
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RegionStatus(Enum):
    """Region operational status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PROVISIONING = "provisioning"
    DEPROVISIONING = "deprovisioning"
    MAINTENANCE = "maintenance"


@dataclass
class RegionConfig:
    """Region configuration."""

    region_id: str
    cloud_provider: str
    min_replicas: int
    max_replicas: int
    status: RegionStatus
    added_at: datetime


class RegionManager:
    """Manages region lifecycle and configuration.

    TODO for students: Implement region management operations
    """

    def __init__(self):
        """Initialize region manager."""
        self.regions: Dict[str, RegionConfig] = {}
        logger.info("Initialized RegionManager")

    def add_region(
        self,
        region_id: str,
        cloud_provider: str,
        min_replicas: int = 2,
        max_replicas: int = 10,
    ) -> bool:
        """Add a new region to the deployment.

        TODO for students: Implement region provisioning
        """
        logger.info(f"Adding region: {region_id}")

        # TODO: Implement region addition
        config = RegionConfig(
            region_id=region_id,
            cloud_provider=cloud_provider,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            status=RegionStatus.PROVISIONING,
            added_at=datetime.utcnow(),
        )

        self.regions[region_id] = config
        return False

    def remove_region(self, region_id: str) -> bool:
        """Remove a region from deployment.

        TODO for students: Implement safe region removal
        """
        logger.warning(f"Removing region: {region_id}")

        # TODO: Implement region removal
        return False

    def get_active_regions(self) -> List[str]:
        """Get list of active regions.

        TODO for students: Filter regions by status
        """
        return [
            r_id
            for r_id, config in self.regions.items()
            if config.status == RegionStatus.ACTIVE
        ]
