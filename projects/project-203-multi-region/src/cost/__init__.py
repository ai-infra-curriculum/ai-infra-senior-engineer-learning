"""
Multi-Region Cost Management Module

Analyzes, optimizes, and reports costs across multiple cloud providers
and regions with cost allocation and optimization recommendations.

TODO for students:
- Implement reserved instance recommendations
- Add spot instance optimization
- Create cost forecasting models
- Implement budget alerts and controls
"""

from .cost_analyzer import (
    CostAnalyzer,
    analyze_costs,
    RegionCost,
)
from .optimizer import (
    CostOptimizer,
    optimize_deployments,
    OptimizationRecommendation,
)
from .reporter import (
    CostReporter,
    generate_report,
    CostBreakdown,
)

__all__ = [
    # Analysis
    "CostAnalyzer",
    "analyze_costs",
    "RegionCost",
    # Optimization
    "CostOptimizer",
    "optimize_deployments",
    "OptimizationRecommendation",
    # Reporting
    "CostReporter",
    "generate_report",
    "CostBreakdown",
]
