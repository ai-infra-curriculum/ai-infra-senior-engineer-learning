# Lecture 4: Decision Making and Architecture

## Learning Objectives

By the end of this lecture, you will be able to:

- Evaluate technical decisions matching analysis depth to impact and reversibility using type 1 vs type 2 decision frameworks
- Apply structured decision frameworks using DECIDE process establishing criteria considering alternatives identifying best options implementing monitoring outcomes
- Write comprehensive Architecture Decision Records capturing context rationale consequences alternatives providing future teams with decision understanding preventing relitigating
- Execute trade-off analysis making explicit evaluations across performance cost complexity maintainability visualizing options scoring systematically against weighted criteria
- Apply ML infrastructure decision patterns choosing training frameworks model serving architectures data storage matching requirements to proven approaches
- Decide refactor vs rebuild analyzing technical debt test coverage team understanding using strangler fig pattern for safe migrations
- Build stakeholder consensus using RACI matrix understanding motivations socializing early incorporating feedback navigating disagreement building broad support
- Avoid decision pitfalls preventing analysis paralysis resume-driven development sunk cost fallacy setting deadlines using 70% rule focusing on problem-fit

## Table of Contents
1. [The Art of Technical Decision Making](#the-art-of-technical-decision-making)
2. [Decision-Making Frameworks](#decision-making-frameworks)
3. [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
4. [Trade-off Analysis](#trade-off-analysis)
5. [ML Infrastructure Decision Patterns](#ml-infrastructure-decision-patterns)
6. [When to Refactor vs Rebuild](#when-to-refactor-vs-rebuild)
7. [Involving Stakeholders](#involving-stakeholders)
8. [Decision Pitfalls to Avoid](#decision-pitfalls-to-avoid)

## The Art of Technical Decision Making

As a senior engineer, **you are paid to make good decisions**, not to write the most code. Your decisions compound—good ones create momentum, bad ones create technical debt.

### The Weight of Decisions

```python
class TechnicalDecision:
    """Understanding the impact of technical decisions"""

    def __init__(self, name: str, reversibility: str, impact: str):
        self.name = name
        self.reversibility = reversibility  # easy, moderate, hard, irreversible
        self.impact = impact  # low, medium, high, critical

    def decision_weight(self) -> str:
        """Determine how much analysis this decision deserves"""

        weights = {
            ('easy', 'low'): 'Quick decision: 5-30 minutes',
            ('easy', 'medium'): 'Light analysis: 1-2 hours',
            ('moderate', 'medium'): 'Moderate analysis: 1-2 days',
            ('moderate', 'high'): 'Deep analysis: 1 week',
            ('hard', 'high'): 'Extended analysis: 2-4 weeks',
            ('irreversible', 'critical'): 'Exhaustive analysis: 1-3 months'
        }

        return weights.get((self.reversibility, self.impact),
                          'Significant analysis required')

    def decision_approach(self) -> dict:
        """How to approach this decision"""

        if self.reversibility == 'easy' and self.impact in ['low', 'medium']:
            # Type 1 Decision: Reversible, use bias for action
            return {
                'strategy': 'Make decision quickly, iterate',
                'process': 'Discuss with 1-2 people, document briefly, proceed',
                'example': 'Choose logging format, pick test framework'
            }
        else:
            # Type 2 Decision: Irreversible or high impact, be careful
            return {
                'strategy': 'Analyze thoroughly, build consensus',
                'process': 'Write RFC/ADR, gather feedback, pilot if possible',
                'example': 'Choose database, select cloud provider, design architecture'
            }

# Examples
quick_decision = TechnicalDecision(
    "Choose JSON vs YAML for config",
    reversibility="easy",
    impact="low"
)
print(quick_decision.decision_weight())
# Output: Quick decision: 5-30 minutes

major_decision = TechnicalDecision(
    "Choose Kubernetes vs EC2 for ML platform",
    reversibility="hard",
    impact="critical"
)
print(major_decision.decision_weight())
# Output: Extended analysis: 2-4 weeks
```

### The Decision Matrix: Impact vs Reversibility

```
High Impact
    │
    │  🔴 Critical          🔴 Major
    │  (Slow, thorough)    (Careful, consensus)
    │  Example: DB choice  Example: API design
    │
    │  🟡 Important        🟢 Safe to try
    │  (Moderate effort)   (Bias for action)
    │  Example: Caching    Example: Code style
    │
    └─────────────────────────────────── Easy to reverse
                                         (Reversibility)
```

## Decision-Making Frameworks

### Framework 1: DECIDE Process

```python
class DECIDEFramework:
    """
    D - Define the problem
    E - Establish criteria
    C - Consider alternatives
    I - Identify the best alternative
    D - Develop and implement
    E - Evaluate and monitor
    """

    def __init__(self, problem: str):
        self.problem = problem
        self.criteria = []
        self.alternatives = []
        self.chosen = None
        self.rationale = ""

    def define_problem(self):
        """What are we really solving?"""
        return {
            'problem_statement': self.problem,
            'root_cause': 'Why does this problem exist?',
            'constraints': ['Budget', 'Timeline', 'Team skills', 'Compliance'],
            'success_metrics': 'How will we know we solved it?',
            'stakeholders': 'Who cares about this problem?'
        }

    def establish_criteria(self):
        """What makes a solution good?"""
        self.criteria = [
            {'name': 'Performance', 'weight': 0.25, 'must_have': True},
            {'name': 'Cost', 'weight': 0.20, 'must_have': True},
            {'name': 'Maintainability', 'weight': 0.20, 'must_have': False},
            {'name': 'Team expertise', 'weight': 0.15, 'must_have': False},
            {'name': 'Community support', 'weight': 0.10, 'must_have': False},
            {'name': 'Time to implement', 'weight': 0.10, 'must_have': False}
        ]
        return self.criteria

    def consider_alternatives(self):
        """Brainstorm options - quantity over quality initially"""
        return {
            'diverge': 'Generate many options without judgment',
            'research': 'Investigate each option deeply',
            'prototype': 'Build small POCs if needed',
            'converge': 'Narrow to 2-4 viable options'
        }

    def identify_best(self):
        """Score alternatives against criteria"""

        # Example scoring matrix
        scoring_matrix = """
        | Criteria       | Weight | Option A | Option B | Option C |
        |----------------|--------|----------|----------|----------|
        | Performance    | 0.25   | 8/10     | 6/10     | 9/10     |
        | Cost           | 0.20   | 5/10     | 9/10     | 7/10     |
        | Maintainability| 0.20   | 9/10     | 7/10     | 6/10     |
        | Team expertise | 0.15   | 8/10     | 9/10     | 4/10     |
        | Community      | 0.10   | 7/10     | 8/10     | 6/10     |
        | Time to impl.  | 0.10   | 6/10     | 8/10     | 5/10     |
        |----------------|--------|----------|----------|----------|
        | Weighted Score |        | 7.3/10   | 7.7/10   | 7.0/10   |

        Recommendation: Option B (highest score)

        Sensitivity analysis:
        - If performance weight increases to 0.35, Option C wins
        - If cost weight increases to 0.30, Option B still wins
        """

        return scoring_matrix

# Example: Choosing a model serving framework
decision = DECIDEFramework("Choose model serving framework for ML platform")
criteria = decision.establish_criteria()
print(f"Evaluating {len(criteria)} criteria with weighted scores")
```

### Framework 2: Pre-Mortem Analysis

Before making a decision, imagine it failed catastrophically. What went wrong?

```python
def pre_mortem_analysis(decision: str) -> dict:
    """
    Imagine the decision was made and failed badly.
    What went wrong? This uncovers hidden risks.
    """

    exercise = {
        'premise': f"It's 1 year later. We chose {decision} and it was a disaster.",

        'questions': [
            "What technical problems occurred?",
            "What assumptions were wrong?",
            "What did we not foresee?",
            "How did the team struggle?",
            "What external factors changed?",
            "What would we have done differently?"
        ],

        'benefits': [
            'Uncovers risks people were afraid to voice',
            'Identifies blind spots in analysis',
            'Surfaces assumptions to validate',
            'Creates mitigation plans proactively'
        ],

        'example_failure_modes': {
            'kubernetes': [
                'Team never learned K8s well, constant outages',
                'Operational complexity overwhelmed us',
                'Cost spiraled with poor resource management',
                'Migration took 2x longer than expected'
            ],
            'custom_solution': [
                'Underestimated maintenance burden',
                'Key engineer left, no one understands it',
                'Missing features we thought were easy',
                'Security vulnerabilities we didn\'t anticipate'
            ]
        }
    }

    return exercise

# Run this exercise with your team before major decisions
pre_mortem = pre_mortem_analysis("Kubernetes for ML platform")
print(f"Scenario: {pre_mortem['premise']}")
for question in pre_mortem['questions']:
    print(f"  - {question}")
```

### Framework 3: Regret Minimization

Borrowed from Jeff Bezos: Will you regret this in 10 years?

```python
class RegretMinimization:
    """Project yourself into the future"""

    def evaluate_decision(self, decision: dict) -> str:
        """Will you regret this decision?"""

        timeframes = {
            '1_week': decision.get('short_term_pain', 0),
            '1_year': decision.get('medium_term_value', 0),
            '10_years': decision.get('long_term_impact', 0)
        }

        if timeframes['10_years'] > 7:
            return "High long-term value - do it even if short-term is hard"
        elif timeframes['1_year'] < 3:
            return "Low medium-term value - probably not worth it"
        else:
            return "Analyze deeper - unclear value"

# Example: Should we refactor our training pipeline?
refactor_decision = {
    'short_term_pain': 8,      # High: 3 months of work, feature slowdown
    'medium_term_value': 9,    # High: Much faster to add features
    'long_term_impact': 9      # High: Enables future innovation
}

result = RegretMinimization().evaluate_decision(refactor_decision)
print(result)
# Output: High long-term value - do it even if short-term is hard
```

## Architecture Decision Records (ADRs)

ADRs are the most important documentation you'll write. They capture **why** decisions were made, not just **what** was decided.

### ADR Template

```markdown
# ADR-001: Choose Ray for Distributed Training

## Status
Accepted | Proposed | Deprecated | Superseded by ADR-XXX

## Context
What is the issue we're facing that motivates this decision?

We need to scale our model training from single-GPU to multi-node distributed
training. Our current training jobs:
- Take 5 days on single V100 GPU
- Need to scale to 100B+ parameter models
- Require elastic scaling (jobs interrupted frequently on spot instances)
- Team has Python expertise, limited C++ experience

We evaluated distributed training frameworks to support our roadmap.

## Decision
We will use Ray Train for distributed training.

## Consequences

### Positive
- **Elastic scaling**: Ray handles worker failures automatically
- **Familiar API**: PyTorch-like, minimal code changes needed
- **Unified platform**: Can also use Ray for data processing and serving
- **Good community**: Active development, strong documentation
- **Cost effective**: Works well with spot instances

### Negative
- **Learning curve**: Team needs to learn Ray concepts (actors, tasks)
- **Complexity**: Adds another framework to our stack
- **Debugging**: Distributed debugging is harder than local
- **Resource overhead**: Ray's scheduler adds ~5% overhead
- **Lock-in**: Migration away from Ray would be significant effort

### Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Team expertise gap | High | 2-week training program, pair programming |
| Production instability | Critical | 3-month pilot on non-critical models |
| Cost overruns | Medium | Set budget alerts, optimize resource usage |
| Ray development stalls | Low | Large community, backed by Anyscale |

## Alternatives Considered

### Horovod
**Pros**: Battle-tested, Uber scale, lower overhead
**Cons**: No fault tolerance, harder to use, C++ required for customization
**Why not chosen**: Lack of fault tolerance is dealbreaker for spot instances

### PyTorch DDP
**Pros**: Native PyTorch, no additional framework, well-documented
**Cons**: No fault tolerance, manual resource management, limited to single framework
**Why not chosen**: Need fault tolerance and plan to use Ray for other workloads

### Custom solution on NCCL
**Pros**: Maximum control, optimized for our exact use case
**Cons**: 6+ months to build, ongoing maintenance burden, security/reliability risks
**Why not chosen**: Not our core competency, would slow feature development

## Implementation Plan

### Phase 1 (Weeks 1-2): Learning and POC
- [ ] Team completes Ray tutorial
- [ ] Build simple distributed training POC
- [ ] Measure overhead vs native PyTorch

### Phase 2 (Weeks 3-6): Pilot
- [ ] Convert 1 training job to Ray
- [ ] Run in production alongside existing solution
- [ ] Validate performance and cost

### Phase 3 (Weeks 7-12): Rollout
- [ ] Migrate remaining training jobs
- [ ] Build monitoring and debugging tools
- [ ] Document best practices

### Phase 4 (Ongoing): Optimize
- [ ] Profile and optimize hot paths
- [ ] Build internal libraries for common patterns
- [ ] Share learnings with team

## Revision History
- 2025-10-16: Initial proposal (John Doe)
- 2025-10-18: Accepted after team discussion (Architecture team)
- 2025-11-01: Added implementation learnings (Jane Smith)
```

### When to Write an ADR

```python
def should_write_adr(decision: dict) -> bool:
    """Determine if a decision deserves an ADR"""

    triggers = [
        decision.get('affects_multiple_teams', False),
        decision.get('hard_to_reverse', False),
        decision.get('high_cost', False),
        decision.get('impacts_architecture', False),
        decision.get('sets_precedent', False),
        decision.get('controversial', False),
        decision.get('future_you_will_ask_why', False)
    ]

    # If any trigger is True, write an ADR
    if any(triggers):
        return True

    # Also write for decisions you're uncertain about
    if decision.get('confidence_level', 10) < 7:
        return True

    return False

# Examples
print(should_write_adr({
    'decision': 'Choose tab vs spaces',
    'affects_multiple_teams': False,
    'hard_to_reverse': False,
    'impacts_architecture': False
}))
# Output: False (just set in linter config)

print(should_write_adr({
    'decision': 'Choose PostgreSQL vs MongoDB',
    'affects_multiple_teams': True,
    'hard_to_reverse': True,
    'impacts_architecture': True,
    'high_cost': True
}))
# Output: True (definitely write ADR)
```

## Trade-off Analysis

Every technical decision is a trade-off. Make trade-offs explicit.

### The Trade-off Matrix

```python
class TradeoffAnalysis:
    """Explicit trade-off evaluation"""

    def __init__(self):
        self.common_tradeoffs = {
            'performance_vs_complexity': {
                'axis_1': 'Performance (faster is better)',
                'axis_2': 'Complexity (simpler is better)',
                'examples': [
                    ('In-memory cache', 'high performance', 'higher complexity'),
                    ('Simple disk storage', 'lower performance', 'lower complexity'),
                    ('Tiered caching', 'balanced', 'moderate complexity')
                ]
            },

            'cost_vs_reliability': {
                'axis_1': 'Cost (lower is better)',
                'axis_2': 'Reliability (higher is better)',
                'examples': [
                    ('Spot instances', 'low cost', 'lower reliability'),
                    ('On-demand instances', 'high cost', 'higher reliability'),
                    ('Mixed fleet', 'moderate cost', 'moderate reliability')
                ]
            },

            'flexibility_vs_simplicity': {
                'axis_1': 'Flexibility (more options)',
                'axis_2': 'Simplicity (easier to use)',
                'examples': [
                    ('Config-driven', 'high flexibility', 'lower simplicity'),
                    ('Opinionated framework', 'lower flexibility', 'higher simplicity'),
                    ('Sensible defaults + config', 'balanced', 'balanced')
                ]
            },

            'time_to_market_vs_quality': {
                'axis_1': 'Speed to ship',
                'axis_2': 'Code quality',
                'examples': [
                    ('Quick hack', 'fast', 'low quality - creates debt'),
                    ('Proper design', 'slower', 'high quality'),
                    ('MVP + refactor', 'moderate', 'improves over time')
                ]
            }
        }

    def evaluate_option(self, option: dict) -> dict:
        """Score an option across multiple dimensions"""

        scores = {
            'performance': option.get('performance_score', 5),  # 1-10
            'cost': option.get('cost_score', 5),
            'complexity': option.get('complexity_score', 5),
            'maintainability': option.get('maintainability_score', 5),
            'time_to_implement': option.get('time_score', 5),
            'team_expertise': option.get('expertise_score', 5)
        }

        # Calculate composite score
        weights = {
            'performance': 0.25,
            'cost': 0.20,
            'complexity': 0.15,
            'maintainability': 0.20,
            'time_to_implement': 0.10,
            'team_expertise': 0.10
        }

        weighted_score = sum(scores[k] * weights[k] for k in scores.keys())

        return {
            'scores': scores,
            'weighted_score': round(weighted_score, 2),
            'recommendation': 'Consider' if weighted_score > 6.5 else 'Pass'
        }

# Example: Evaluating TensorRT for model serving
tensorrt_option = {
    'performance_score': 9,       # Excellent: 5x faster inference
    'cost_score': 8,              # Good: Lower cost per inference
    'complexity_score': 4,        # Complex: Requires CUDA expertise
    'maintainability_score': 5,   # Moderate: NVIDIA support but niche
    'time_score': 3,              # Slow: 2-3 months to integrate
    'expertise_score': 4          # Low: Team needs to learn
}

analysis = TradeoffAnalysis().evaluate_option(tensorrt_option)
print(f"Weighted score: {analysis['weighted_score']}/10")
print(f"Recommendation: {analysis['recommendation']}")
# Weighted score: 6.25/10 - borderline, needs deeper analysis
```

### Visualizing Trade-offs

```python
def create_tradeoff_chart(options: list) -> str:
    """
    Create a 2x2 matrix to visualize trade-offs

    Example: Performance vs Complexity for model serving
    """

    chart = """
    High Performance
         │
         │  Option C          Option A
         │  (Ray Serve)       (TensorRT)
         │  ★ 7/10 perf      ★ 9/10 perf
         │  ● 6/10 complex    ● 8/10 complex
         │
         │  Option B          Option D
         │  (TorchServe)      (Custom)
         │  ★ 5/10 perf       ★ 8/10 perf
         │  ● 4/10 complex    ● 9/10 complex
         │
         └────────────────────────────── Low Complexity
                                         (Simple)

    Recommendation: Option C (Ray Serve)
    - Best balance of performance and complexity
    - Team has Ray experience from training
    - Can be optimized later if needed

    Second choice: Option B (TorchServe)
    - Lower performance acceptable for MVP
    - Much simpler to get started
    - PyTorch native, familiar to team
    """

    return chart

print(create_tradeoff_chart([]))
```

## ML Infrastructure Decision Patterns

### Decision Pattern 1: Training Framework

```python
class TrainingFrameworkDecision:
    """Common decision: Choose training framework"""

    def analyze(self, requirements: dict) -> dict:
        """Decision tree for training frameworks"""

        # Single GPU, simple models
        if requirements['scale'] == 'single_gpu':
            return {
                'recommendation': 'PyTorch or TensorFlow (your preference)',
                'rationale': 'Both work great for single-GPU, pick what team knows'
            }

        # Multi-GPU, single node
        elif requirements['scale'] == 'multi_gpu_single_node':
            return {
                'recommendation': 'PyTorch DDP or TensorFlow MultiWorkerMirroredStrategy',
                'rationale': 'Native frameworks work well at this scale'
            }

        # Multi-node, stable infrastructure
        elif requirements['scale'] == 'multi_node' and requirements['stability'] == 'high':
            return {
                'recommendation': 'Horovod or DeepSpeed',
                'rationale': 'Battle-tested, maximum performance'
            }

        # Multi-node, spot instances
        elif requirements['scale'] == 'multi_node' and requirements['stability'] == 'low':
            return {
                'recommendation': 'Ray Train',
                'rationale': 'Fault tolerance critical for spot instances'
            }

        # Massive scale (100B+ parameters)
        elif requirements['scale'] == 'massive':
            return {
                'recommendation': 'Megatron-LM or DeepSpeed ZeRO',
                'rationale': 'Specialized for giant models, 3D parallelism'
            }

        else:
            return {
                'recommendation': 'Need more info',
                'questions': [
                    'What is your largest model size?',
                    'What is your team\'s expertise?',
                    'What is your budget for spot vs on-demand?',
                    'How important is fault tolerance?'
                ]
            }

# Example usage
decision = TrainingFrameworkDecision()
result = decision.analyze({
    'scale': 'multi_node',
    'stability': 'low',  # Using spot instances
    'model_size': '7B parameters'
})
print(f"Recommendation: {result['recommendation']}")
print(f"Rationale: {result['rationale']}")
```

### Decision Pattern 2: Model Serving Architecture

```python
class ServingArchitectureDecision:
    """Common decision: Choose serving architecture"""

    def analyze(self, requirements: dict) -> dict:
        """Decision factors for serving"""

        latency = requirements.get('latency_requirement_ms', 1000)
        throughput = requirements.get('requests_per_second', 100)
        models = requirements.get('number_of_models', 1)
        cost_sensitivity = requirements.get('cost_sensitive', False)

        # Very low latency (<10ms) - optimize for latency
        if latency < 10:
            return {
                'recommendation': 'TensorRT or ONNX Runtime on GPU',
                'architecture': 'Direct model inference, minimal layers',
                'rationale': 'Need maximum performance, complexity justified'
            }

        # High throughput (>1000 RPS) - optimize for throughput
        elif throughput > 1000:
            return {
                'recommendation': 'vLLM or TensorRT-LLM with batching',
                'architecture': 'Dynamic batching, request queuing',
                'rationale': 'Batching critical for throughput'
            }

        # Many models (>10) - multi-model serving
        elif models > 10:
            return {
                'recommendation': 'Ray Serve or TorchServe',
                'architecture': 'Multi-model server, model versioning',
                'rationale': 'Need model management, not just inference'
            }

        # Cost-sensitive - optimize for cost
        elif cost_sensitivity:
            return {
                'recommendation': 'vLLM or TorchServe on CPU',
                'architecture': 'Auto-scaling, spot instances',
                'rationale': 'CPU cheaper if latency acceptable'
            }

        # Balanced requirements - simple solution
        else:
            return {
                'recommendation': 'FastAPI + PyTorch',
                'architecture': 'Simple REST API, straightforward deployment',
                'rationale': 'Start simple, optimize later if needed'
            }

# Example: High-throughput LLM serving
serving_decision = ServingArchitectureDecision()
result = serving_decision.analyze({
    'latency_requirement_ms': 100,
    'requests_per_second': 5000,
    'number_of_models': 3,
    'cost_sensitive': True
})

print(f"Recommendation: {result['recommendation']}")
print(f"Architecture: {result['architecture']}")
```

### Decision Pattern 3: Data Storage

```python
class DataStorageDecision:
    """Common decision: Where to store training data"""

    def analyze(self, requirements: dict) -> dict:
        """Decision tree for data storage"""

        size_tb = requirements.get('data_size_tb', 1)
        access_pattern = requirements.get('access_pattern', 'sequential')
        query_needs = requirements.get('needs_queries', False)
        budget = requirements.get('budget', 'medium')

        # Small data (<100GB) - keep it simple
        if size_tb < 0.1:
            return {
                'recommendation': 'Local SSD or EBS',
                'rationale': 'Small enough to fit on instance storage'
            }

        # Large data, sequential access (training)
        elif size_tb > 1 and access_pattern == 'sequential':
            return {
                'recommendation': 'S3 or GCS with prefetching',
                'rationale': 'Object storage cost-effective for large sequential reads',
                'optimization': 'Use data loaders with prefetching (5-10x faster)'
            }

        # Need SQL queries
        elif query_needs:
            return {
                'recommendation': 'Data lakehouse (Delta Lake, Iceberg)',
                'rationale': 'Supports both analytics and ML workloads',
                'tools': 'Spark for processing, direct parquet reading for training'
            }

        # Random access patterns
        elif access_pattern == 'random':
            return {
                'recommendation': 'Distributed file system (Lustre, WekaFS) or local NVMe',
                'rationale': 'Random access needs low latency',
                'tradeoff': 'Higher cost but necessary for performance'
            }

        # Budget constrained
        elif budget == 'low':
            return {
                'recommendation': 'S3 Glacier + on-demand retrieval',
                'rationale': 'Archive rarely-used data, retrieve when needed',
                'consideration': 'Retrieval takes hours, plan accordingly'
            }

        else:
            return {
                'recommendation': 'Hybrid: S3 for storage + local NVMe for caching',
                'rationale': 'Best of both worlds',
                'architecture': 'Cache hot data locally, stream from S3'
            }
```

## When to Refactor vs Rebuild

One of the hardest decisions: fix what exists or start over?

```python
class RefactorVsRebuildDecision:
    """Framework for refactor vs rebuild decisions"""

    def analyze(self, codebase: dict) -> str:
        """Should you refactor or rebuild?"""

        # Scoring factors (1-10, higher is worse)
        technical_debt = codebase.get('technical_debt_score', 5)
        test_coverage = 10 - codebase.get('test_coverage_percent', 50) / 10
        team_understanding = 10 - codebase.get('team_understands_it', 5)
        change_frequency = codebase.get('changes_per_month', 5)
        business_criticality = codebase.get('criticality', 5)

        # Calculate rebuild pressure
        rebuild_score = (
            technical_debt * 0.30 +
            test_coverage * 0.25 +
            team_understanding * 0.25 +
            (10 - business_criticality) * 0.20  # Low criticality = safer to rebuild
        )

        # Decision logic
        if rebuild_score > 7.5:
            return self.rebuild_recommendation(codebase)
        elif rebuild_score < 4.5:
            return self.refactor_recommendation(codebase)
        else:
            return self.hybrid_recommendation(codebase)

    def rebuild_recommendation(self, codebase: dict) -> str:
        return """
        🔴 REBUILD RECOMMENDED

        Signals pointing to rebuild:
        - Technical debt is very high
        - Low/no test coverage (risky to refactor)
        - Team doesn't understand existing code
        - Not business-critical (can afford downtime)

        Rebuild Strategy:
        1. Build new system alongside old one
        2. Migrate traffic gradually (strangler pattern)
        3. Keep old system running until new one proven
        4. Decommission old system only when confident

        Timeline: 6-12 months typically

        Risks:
        - Classic "rewrite trap" - takes longer than expected
        - May rebuild same bugs if requirements unclear
        - Opportunity cost of not shipping features

        Mitigation:
        - Start with small, valuable slice (not everything)
        - Ship to production early and often
        - Keep old system as safety net
        """

    def refactor_recommendation(self, codebase: dict) -> str:
        return """
        🟢 REFACTOR RECOMMENDED

        Signals pointing to refactor:
        - Technical debt is manageable
        - Good test coverage (safe to refactor)
        - Team understands the code
        - Business-critical (can't afford rewrite risk)

        Refactor Strategy:
        1. Add tests for existing behavior first
        2. Refactor in small, safe steps
        3. Each step leaves code working
        4. Continuous delivery throughout

        Timeline: 2-4 months typically

        Benefits:
        - Lower risk than rebuild
        - Faster time to improvement
        - Learn from existing code
        - Preserve domain knowledge

        Approach:
        - Boy Scout Rule: Leave code better than you found it
        - Strategic refactoring: Focus on pain points
        - Incremental improvement over time
        """

    def hybrid_recommendation(self, codebase: dict) -> str:
        return """
        🟡 HYBRID APPROACH RECOMMENDED

        Signals are mixed - consider selective rebuild:

        Hybrid Strategy:
        1. Identify the core that's salvageable
        2. Rebuild the problematic parts
        3. Refactor the rest

        Example:
        - Keep: Data models (well-tested, understood)
        - Rebuild: Training pipeline (messy, untested)
        - Refactor: Serving API (moderate debt)

        Timeline: 4-8 months

        This gives you:
        - Lower risk than full rebuild
        - Bigger improvement than pure refactor
        - Flexibility to adjust as you learn
        """

# Example: Evaluate existing training pipeline
pipeline_analysis = RefactorVsRebuildDecision()
result = pipeline_analysis.analyze({
    'technical_debt_score': 8,      # Very high debt
    'test_coverage_percent': 20,    # Low coverage
    'team_understands_it': 3,       # Only 1 person understands it
    'changes_per_month': 15,        # High change frequency
    'criticality': 7                # Important but not mission-critical
})

print(result)
```

### The Strangler Fig Pattern

```python
def strangler_pattern_guide() -> str:
    """
    Safely replace legacy systems without big-bang rewrites

    Named after strangler figs that grow around host trees
    """

    guide = """
    # Strangler Fig Pattern for ML Infrastructure

    ## Phase 1: Create Facade (Weeks 1-2)
    ┌─────────────────────────────────────────┐
    │           API Gateway / Facade           │
    │  (Routes requests to old or new system)  │
    └───┬─────────────────────────────────┬───┘
        │                                  │
        ▼                                  ▼
    ┌───────────┐                   ┌───────────┐
    │    Old    │                   │    New    │
    │  System   │                   │  System   │
    │  (100%)   │                   │   (0%)    │
    └───────────┘                   └───────────┘

    Actions:
    - Create routing layer
    - Route 100% to old system
    - New system exists but unused

    ## Phase 2: Implement & Test (Weeks 3-8)
    - Build new system feature by feature
    - Test thoroughly in isolation
    - No production traffic yet

    ## Phase 3: Gradual Migration (Weeks 9-20)
    ┌─────────────────────────────────────────┐
    │            Facade (routing)              │
    └───┬────────────────────────────────┬────┘
        │ 80%                            │ 20%
        ▼                                ▼
    ┌───────────┐                   ┌───────────┐
    │    Old    │                   │    New    │
    │  System   │                   │  System   │
    └───────────┘                   └───────────┘

    Migration schedule:
    - Week 9:  1% traffic to new (canary)
    - Week 10: 5% traffic to new
    - Week 12: 20% traffic to new
    - Week 14: 50% traffic to new
    - Week 16: 80% traffic to new
    - Week 18: 95% traffic to new
    - Week 20: 100% traffic to new

    Validation at each step:
    - Compare outputs (new vs old)
    - Monitor error rates
    - Check latency
    - Validate correctness

    ## Phase 4: Decommission Old (Week 21+)
    - Keep old system on standby (1 month)
    - Remove routing layer
    - Delete old code
    - Celebrate! 🎉

    ## Example: Migrating Training Pipeline

    Old pipeline: Brittle, hard-coded, no tests
    New pipeline: Ray-based, tested, modular

    Week 1-2:   Build orchestration layer
    Week 3-8:   Build new pipeline (not used yet)
    Week 9:     Run 1 non-critical model on new pipeline
    Week 10:    Run 5 models on new pipeline
    Week 12:    Run 20 models (20% of workload)
    Week 14:    Run 50 models (50% of workload)
    Week 16:    Run 80 models (80% of workload)
    Week 18:    All but 2 critical models
    Week 20:    Everything on new pipeline
    Week 24:    Delete old pipeline

    Benefits:
    - Low risk (can always rollback)
    - Continuous validation
    - Learn and adjust as you go
    - No big-bang switchover
    """

    return guide

print(strangler_pattern_guide())
```

## Involving Stakeholders

Good decisions require input from the right people at the right time.

### The RACI Matrix

```python
class StakeholderInvolvement:
    """Who should be involved in the decision?"""

    def __init__(self, decision: str):
        self.decision = decision
        self.roles = {
            'R - Responsible': 'Does the work, implements the decision',
            'A - Accountable': 'Ultimately answerable, has veto power',
            'C - Consulted': 'Provides input, two-way communication',
            'I - Informed': 'Kept in the loop, one-way communication'
        }

    def example_raci(self) -> dict:
        """Example RACI for 'Choose distributed training framework'"""

        return {
            'decision': 'Choose Ray vs Horovod for distributed training',

            'Responsible': [
                'Senior ML Engineer (you) - Research and recommendation',
                'ML Platform Team - Implementation'
            ],

            'Accountable': [
                'Engineering Manager - Final decision',
                'VP Engineering - Approves budget'
            ],

            'Consulted': [
                'ML Scientists - Training requirements and workflows',
                'SRE Team - Operational concerns',
                'Cost Team - Budget implications',
                'Security Team - Security review'
            ],

            'Informed': [
                'Data Engineering Team - May use Ray for data processing',
                'Product Team - Impacts roadmap timeline',
                'Executive Team - Strategic initiative'
            ]
        }

    def when_to_consult(self, stakeholder: str) -> str:
        """When to involve each stakeholder"""

        timing = {
            'ML Scientists': 'Early - understand requirements',
            'SRE Team': 'Middle - operational feasibility',
            'Security Team': 'Middle - security review',
            'Engineering Manager': 'Late - final decision',
            'VP Engineering': 'Late - budget approval',
            'Product Team': 'After decision - communicate impact'
        }

        return timing.get(stakeholder, 'TBD - assess impact first')

# Example usage
decision = StakeholderInvolvement("Choose training framework")
raci = decision.example_raci()

print("Decision:", raci['decision'])
print("\nResponsible:", raci['Responsible'])
print("Accountable:", raci['Accountable'])
print("\nConsult these people:", raci['Consulted'])
```

### Building Consensus

```python
def build_consensus_process() -> dict:
    """How to build consensus for technical decisions"""

    return {
        'step_1_socialize_early': {
            'action': 'Share rough ideas with key stakeholders',
            'why': 'Catch major concerns early, before investing heavily',
            'how': '1-on-1 conversations, informal whiteboard sessions',
            'example': 'Grab coffee with SRE lead, sketch out Ray idea'
        },

        'step_2_incorporate_feedback': {
            'action': 'Integrate feedback into proposal',
            'why': 'People support what they help create',
            'how': 'Update RFC with "Thanks to X for feedback on Y"',
            'example': 'SRE suggested elastic scaling - added to requirements'
        },

        'step_3_formal_review': {
            'action': 'Present formal proposal to team',
            'why': 'Get explicit buy-in or concerns on record',
            'how': 'RFC document, team meeting discussion',
            'example': '1-hour meeting to review Ray proposal'
        },

        'step_4_address_objections': {
            'action': 'Take objections seriously, address or acknowledge',
            'why': 'Unaddressed concerns become resentment',
            'how': 'Update proposal or explain why not changing',
            'example': 'Concern: learning curve. Mitigation: 2-week training'
        },

        'step_5_decide_and_commit': {
            'action': 'Make decision, ask for commitment even from dissenters',
            'why': 'Can disagree and commit - unity after decision',
            'how': 'Explicitly ask "Can everyone commit to this?"',
            'example': 'Bob preferred Horovod but commits to Ray'
        },

        'step_6_communicate_widely': {
            'action': 'Share decision and rationale broadly',
            'why': 'Avoid surprises, build understanding',
            'how': 'Email summary, ADR published, team all-hands',
            'example': 'ADR-007 sent to engineering@, discussed at all-hands'
        }
    }

# Example: Building consensus for major decision
process = build_consensus_process()
for step_name, step_details in process.items():
    print(f"\n{step_name.replace('_', ' ').title()}:")
    print(f"  {step_details['action']}")
    print(f"  Example: {step_details['example']}")
```

## Decision Pitfalls to Avoid

### Pitfall 1: Analysis Paralysis

```python
def avoid_analysis_paralysis() -> dict:
    """How to make decisions without getting stuck"""

    return {
        'symptom': 'Weeks/months pass, no decision made, more analysis requested',

        'causes': [
            'Perfectionism - waiting for perfect information',
            'Fear of being wrong',
            'Lack of decision criteria',
            'No deadline for decision'
        ],

        'solutions': [
            'Set decision deadline: "We decide by Friday"',
            'Use 70% rule: Decide when 70% confident (not 100%)',
            'Time-box research: "2 days of research, then decide"',
            'Make it reversible: "We can change this if wrong"',
            'Clarify criteria: "What info would change your mind?"'
        ],

        'example': """
        Team spent 3 weeks debating Ray vs Horovod vs DeepSpeed.

        Breaking the paralysis:
        - Monday: Define decision criteria and weights
        - Tuesday: Each person researches 1 framework (4 hours max)
        - Wednesday: Present findings (1 hour)
        - Thursday: Score options, discuss concerns
        - Friday: Make decision, write ADR

        Decision made in 1 week instead of endless debate.
        """
    }
```

### Pitfall 2: Resume-Driven Development

```python
class ResumeDrivenDevelopment:
    """Choosing technology to pad resume, not solve problem"""

    def detect(self, decision: dict) -> bool:
        """Is this resume-driven development?"""

        red_flags = [
            'Technology is very new/hyped',
            'No one on team has used it',
            'Simpler alternatives exist',
            'Main benefit is "learning experience"',
            'Decision maker recently saw conference talk about it',
            'Heavy emphasis on "cutting-edge" rather than "right fit"'
        ]

        concerns = [flag for flag in red_flags if decision.get(flag.lower(), False)]

        if len(concerns) >= 3:
            return True  # Likely resume-driven
        return False

    def evaluate_properly(self, technology: str, problem: str) -> dict:
        """Evaluate technology for right reasons"""

        return {
            'questions': [
                f'Does {technology} solve {problem} better than alternatives?',
                f'Is {technology} mature enough for production?',
                f'Can our team support {technology}?',
                f'What is the operational burden of {technology}?',
                f'What happens if {technology} fails us?'
            ],

            'valid_reasons': [
                'Solves our specific problem better',
                'More cost-effective',
                'Better performance',
                'Reduces operational burden',
                'Strong ecosystem and community',
                'Team has expertise or can gain it quickly'
            ],

            'invalid_reasons': [
                'Looks good on resume',
                'Everyone is talking about it',
                'Conference speaker recommended it',
                'Want to learn something new',
                'Previous company used it'
            ]
        }

# Example: Kubernetes for single-instance app
k8s_decision = ResumeDrivenDevelopment()
is_resume_driven = k8s_decision.detect({
    'technology is very new/hyped': False,  # K8s is mature
    'no one on team has used it': True,
    'simpler alternatives exist': True,      # Docker Compose, ECS
    'main benefit is "learning experience"': True,
    'decision maker recently saw conference talk about it': True,
    'heavy emphasis on "cutting-edge" rather than "right fit"': False
})

if is_resume_driven:
    print("⚠️  This looks like resume-driven development")
    print("Reconsider: Do we need K8s for a single container?")
```

### Pitfall 3: Sunk Cost Fallacy

```python
def recognize_sunk_cost_fallacy() -> dict:
    """Don't continue bad decisions because you've already invested"""

    return {
        'definition': 'Continuing a project because of past investment, not future value',

        'examples': [
            'We spent 3 months on this custom solution, we can\'t abandon it now',
            'We already bought this software license, we have to use it',
            'I spent 2 weeks learning this framework, switching would waste that time'
        ],

        'reality': 'Past investment is gone either way. Only future matters.',

        'correct_thinking': [
            'Past time is SUNK - can\'t get it back',
            'Only question: What maximizes future value?',
            'Better to abandon and start right than continue wrong'
        ],

        'framework': {
            'ignore': 'Time/money already spent',
            'consider': [
                'Cost to complete current approach',
                'Cost to switch to better approach',
                'Value of current approach when done',
                'Value of alternative approach when done'
            ]
        },

        'example': """
        Situation:
        - Spent 3 months building custom distributed training system
        - Discovered Ray Train exists and is better
        - Custom system needs 3 more months to reach MVP
        - Ray Train would take 1 month to integrate

        Sunk cost fallacy says: "We've already invested 3 months, finish it"

        Correct analysis:
        - 3 months is SUNK (gone either way)
        - Custom: 3 more months → working but ongoing maintenance
        - Ray: 1 month → working AND community support
        - Decision: Switch to Ray (saves 2 months, better long-term)

        The 3 months already spent is painful but irrelevant to decision.
        """
    }

print(recognize_sunk_cost_fallacy()['example'])
```

## Summary

**Decision-making is the core skill of senior engineers**. Your code will be rewritten, but your decisions compound over time.

### Key Principles

1. **Match Decision Weight to Impact**
   - Quick decisions for reversible, low-impact choices
   - Deep analysis for irreversible, high-impact choices

2. **Make Trade-offs Explicit**
   - Every decision is a trade-off
   - Document what you're optimizing for and sacrificing

3. **Write ADRs for Important Decisions**
   - Captures context and rationale
   - Invaluable for future team members
   - Prevents relitigating old decisions

4. **Involve the Right People**
   - Too few: miss important concerns
   - Too many: decision paralysis
   - Use RACI to clarify roles

5. **Avoid Common Pitfalls**
   - Analysis paralysis → Set deadlines
   - Resume-driven development → Focus on problem-fit
   - Sunk cost fallacy → Ignore past investment

6. **Build Consensus**
   - Socialize early
   - Incorporate feedback
   - Disagree and commit

7. **Bias for Action**
   - 70% confidence is enough
   - Make reversible decisions quickly
   - Perfect is the enemy of good

### ML Infrastructure-Specific

- **Training**: Consider scale, fault-tolerance, team expertise
- **Serving**: Balance latency, throughput, cost
- **Data**: Match storage to access patterns
- **Refactor vs Rebuild**: Analyze objectively, use strangler pattern

### Most Important

**Document your decisions**. Future you (and your team) will thank you.

## Next Steps

- Continue to [Lecture 5: Technical Communication](05-technical-communication.md)
- Write an ADR for a recent decision
- Review your last major decision - would you decide differently now?
- Practice the DECIDE framework on a current problem

## Additional Resources

**Books**:
- "Thinking in Systems" by Donella Meadows
- "The Decision Book" by Mikael Krogerus
- "Decisive" by Chip and Dan Heath
- "Thinking, Fast and Slow" by Daniel Kahneman

**Articles**:
- AWS Architecture Decision Records: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/
- Martin Fowler on ADRs: https://martinfowler.com/articles/scaling-architecture-conversationally.html
- Joel Spolsky on Architecture Astronauts: https://www.joelonsoftware.com/2001/04/21/dont-let-architecture-astronauts-scare-you/

**Tools**:
- ADR Tools: https://github.com/npryce/adr-tools
- Decision Matrix Templates: https://www.mindtools.com/a8o9dke/decision-matrix-analysis
