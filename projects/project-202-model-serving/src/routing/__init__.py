"""
Intelligent Request Routing

This module provides advanced routing strategies including A/B testing,
canary deployments, and load balancing.

TODO for students:
- Implement sticky sessions for stateful models
- Add shadow traffic for A/B testing
- Implement gradual rollout with automatic rollback
- Add latency-based routing
- Implement geo-aware routing
"""

from .ab_testing import (
    ABTester,
    ABTestConfig,
    Variant,
    split_traffic,
)
from .canary import (
    CanaryDeployment,
    CanaryConfig,
    CanaryStrategy,
    gradual_rollout,
)
from .load_balancer import (
    LoadBalancer,
    RoundRobinBalancer,
    LeastLatencyBalancer,
    WeightedBalancer,
)

__all__ = [
    # A/B Testing
    "ABTester",
    "ABTestConfig",
    "Variant",
    "split_traffic",
    # Canary Deployment
    "CanaryDeployment",
    "CanaryConfig",
    "CanaryStrategy",
    "gradual_rollout",
    # Load Balancing
    "LoadBalancer",
    "RoundRobinBalancer",
    "LeastLatencyBalancer",
    "WeightedBalancer",
]
