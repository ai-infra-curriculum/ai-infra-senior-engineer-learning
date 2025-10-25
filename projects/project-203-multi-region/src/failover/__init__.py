"""
Automated Failover and Disaster Recovery Module

Handles automated failover detection, DNS updates, and disaster recovery
across multiple regions with zero-downtime failover.

TODO for students:
- Implement health-based failover triggers
- Add automatic rollback on failed failover
- Create disaster recovery runbooks
- Implement cross-region data recovery
"""

from .failover_controller import (
    FailoverController,
    FailoverPolicy,
    trigger_failover,
)
from .dns_updater import (
    DNSUpdater,
    update_global_dns,
    DNSRecord,
)
from .recovery import (
    DisasterRecovery,
    initiate_recovery,
    RecoveryPlan,
)

__all__ = [
    # Failover Control
    "FailoverController",
    "FailoverPolicy",
    "trigger_failover",
    # DNS Management
    "DNSUpdater",
    "update_global_dns",
    "DNSRecord",
    # Disaster Recovery
    "DisasterRecovery",
    "initiate_recovery",
    "RecoveryPlan",
]
