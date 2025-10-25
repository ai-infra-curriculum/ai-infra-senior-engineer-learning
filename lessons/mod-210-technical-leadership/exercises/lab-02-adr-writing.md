# Lab 2: Architecture Decision Record (ADR) Writing

## Overview

Architecture Decision Records (ADRs) are crucial documents that capture the context, reasoning, and consequences of significant technical decisions. As a Senior AI Infrastructure Engineer, you'll frequently make decisions that impact your organization for months or years. This lab teaches you to document these decisions effectively.

## Learning Objectives

By the end of this lab, you will be able to:
- Write clear, concise Architecture Decision Records
- Document technical decisions with proper context and rationale
- Apply decision-making frameworks to complex infrastructure choices
- Understand when ADRs are necessary vs. overkill
- Review and critique existing ADRs for completeness

## Duration

3-4 hours

## Prerequisites

- Understanding of distributed systems concepts
- Familiarity with your organization's tech stack
- Completion of Module 210 Lecture 4 (Decision Making and Architecture)

---

## Part 1: ADR Fundamentals (30 minutes)

### What is an ADR?

An Architecture Decision Record documents a significant architectural decision along with its context and consequences. ADRs are:
- **Immutable**: Once written, they're not changed (new ADRs supersede old ones)
- **Numbered**: Sequential numbering tracks decision evolution
- **Concise**: Typically 1-2 pages, focused on the essential information
- **Context-rich**: Explains the "why" behind decisions

### When to Write an ADR

Write an ADR when:
- The decision has long-term implications (>6 months)
- The decision affects multiple teams or systems
- The decision involves significant trade-offs
- Future engineers will wonder "why did they choose this?"
- The decision is difficult to reverse

Don't write an ADR for:
- Routine technology upgrades
- Temporary workarounds
- Team-local implementation details
- Decisions that can be easily reversed

---

## Part 2: ADR Template

Use this template for your ADRs:

```markdown
# ADR-XXX: [Title - Short noun phrase]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
[What is the issue we're facing? What forces are at play?
Include technical, organizational, and business constraints.]

## Decision
[What is the change we're proposing/making? State clearly in active voice.]

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Other implications]

## Alternatives Considered
### Option 1: [Name]
- Description
- Pros
- Cons
- Why rejected

### Option 2: [Name]
- Description
- Pros
- Cons
- Why rejected

## Implementation Notes
[Optional: Technical details, migration path, rollback plan]

## Related Decisions
- ADR-XXX: [Related decision]
- ADR-YYY: [Superseded decision]

## References
- [Links to docs, RFCs, discussions]
```

---

## Part 3: Scenario 1 - Model Serving Infrastructure (90 minutes)

### Background

Your AI infrastructure team currently serves ML models using a home-grown Python Flask application. The system:
- Handles 10,000 requests/second at peak
- Serves 45 different models (PyTorch and TensorFlow)
- Runs on 20 CPU-based Kubernetes pods
- Has p95 latency of 350ms
- Costs $15,000/month in compute

### The Problem

Leadership wants to:
1. Reduce latency to <100ms p95
2. Support 50,000 requests/second
3. Add support for LLMs (7B-70B parameter models)
4. Reduce costs by 30%

### Your Task

Write an ADR evaluating these options:

**Option A: TensorRT + Triton Inference Server**
- Pros: Excellent performance, GPU optimization, multi-framework support
- Cons: Steep learning curve, requires GPU infrastructure, NVIDIA-specific

**Option B: TorchServe**
- Pros: PyTorch-native, good community support, easier migration
- Cons: Limited TensorFlow support, less performance optimization

**Option C: Custom FastAPI + ONNX Runtime**
- Pros: Maximum flexibility, can optimize per-model, portable
- Cons: Significant development effort, maintenance burden

**Option D: Managed Service (AWS SageMaker / GCP Vertex AI)**
- Pros: Minimal operational overhead, auto-scaling, managed infrastructure
- Cons: Higher cost, vendor lock-in, less control

### Deliverable

Write ADR-001 documenting your decision. Include:
- Context explaining the current state and requirements
- Your chosen solution with clear rationale
- Analysis of all four options
- Implementation approach
- Success metrics

### Evaluation Criteria

Your ADR will be assessed on:
- **Completeness** (25%): All sections filled with relevant information
- **Clarity** (25%): Clear, concise writing without jargon
- **Technical Depth** (25%): Demonstrates understanding of trade-offs
- **Business Alignment** (25%): Connects technical decisions to business goals

---

## Part 4: Scenario 2 - GPU Scheduling Strategy (60 minutes)

### Background

Your organization runs a GPU cluster for training and inference:
- 200 NVIDIA A100 GPUs across 50 nodes
- 15 data science teams (5-20 people each)
- Mix of long-running training jobs (days) and short inference workloads (seconds)
- Current utilization: 45% (expensive underutilization!)

### The Problem

Teams are frustrated:
- Data scientists can't get GPUs when needed
- Long jobs block urgent inference workloads
- No fair allocation mechanism
- GPU costs are $100,000/month with poor utilization

### Your Task

Write ADR-002 evaluating GPU scheduling approaches:

**Option A: Time-sliced Sharing (MIG/MPS)**
- Split GPUs into smaller slices
- Better utilization but reduced performance per job

**Option B: Priority-based Queuing**
- Different priority levels for different workloads
- Risk of priority inflation, unfairness

**Option C: Reserved + On-Demand Pools**
- Reserve some GPUs per team, rest shared
- Clear allocations but potential waste

**Option D: Cost-based Allocation**
- Teams have GPU budgets, bid for resources
- Market-driven efficiency but added complexity

### Deliverable

Write ADR-002 with focus on:
- Multi-stakeholder concerns (data scientists, finance, platform team)
- Quantitative comparison (expected utilization, fairness metrics)
- Implementation complexity and timeline
- Change management approach

---

## Part 5: Peer Review Exercise (45 minutes)

### Instructions

1. Exchange ADRs with a partner or small group
2. Review their ADR using the checklist below
3. Provide constructive feedback
4. Discuss and defend your decisions

### Review Checklist

#### Context Section
- [ ] Problem is clearly stated
- [ ] Business and technical constraints are identified
- [ ] Current state is described
- [ ] Success criteria are defined

#### Decision Section
- [ ] Decision is stated in clear, active voice
- [ ] Scope is well-defined
- [ ] No ambiguity about what's being decided

#### Consequences Section
- [ ] Both positive and negative consequences listed
- [ ] Consequences are realistic and specific
- [ ] Long-term implications considered
- [ ] Risks and mitigations identified

#### Alternatives Section
- [ ] Multiple viable options considered
- [ ] Each alternative has pros/cons
- [ ] Clear reasoning for rejection
- [ ] No strawman arguments

#### Overall Quality
- [ ] Free of jargon or jargon is explained
- [ ] Appropriate level of technical detail
- [ ] Connects to business objectives
- [ ] Would make sense to someone in 2 years

---

## Part 6: Real-World Application (30 minutes)

### Your Own ADR

Think of a significant decision you made (or are facing) in your current role. Write a brief ADR (use the template) for one of:

1. **Infrastructure migration**: Moving from X to Y
2. **Technology adoption**: Adding a new tool/framework to your stack
3. **Architectural pattern**: Choosing between design approaches
4. **Operational change**: Modifying deployment, monitoring, or incident response

This doesn't need to be as detailed as the scenarios above, but should:
- Use the standard template
- Include real context from your environment
- Consider at least 2-3 alternatives
- Connect to business value

---

## Resources

### ADR Tools
- [adr-tools](https://github.com/npryce/adr-tools) - Command-line tools for working with ADRs
- [log4brains](https://github.com/thomvaill/log4brains) - Web UI for browsing ADRs
- [ADR Manager](https://adr.github.io/) - VS Code extension

### Reading List
- [Michael Nygard's article on ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Original ADR concept
- [ADR GitHub organization](https://adr.github.io/) - Templates and examples
- [ThoughtWorks Technology Radar on ADRs](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)

### Example ADRs
- [Kubernetes ADRs](https://github.com/kubernetes/enhancements/tree/master/keps)
- [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/)
- [Microsoft Architecture Decisions](https://docs.microsoft.com/en-us/azure/architecture/guide/design-principles/)

---

## Submission Guidelines

Submit your completed ADRs to your learning management system or share with your mentor:

1. **ADR-001** (Model Serving Infrastructure)
2. **ADR-002** (GPU Scheduling Strategy)
3. **ADR-XXX** (Your real-world decision)
4. **Peer Review Feedback** (summary of feedback you received and gave)

---

## Common Pitfalls to Avoid

1. **Too much technical detail**: ADRs aren't implementation guides
2. **Missing the "why"**: Context is as important as the decision itself
3. **Strawman alternatives**: Don't present weak alternatives just to reject them
4. **Decision by committee**: ADRs document decisions, not debates
5. **Retrofitting ADRs**: Write them when making the decision, not 6 months later
6. **Ignoring consequences**: Every decision has trade-offs - acknowledge them
7. **Vague language**: "We might use X" vs "We will use X for Y starting Z"

---

## Extension Activities

For deeper learning:

1. **Historical Analysis**: Find an old architectural decision in your codebase (based on comments, git history, or tribal knowledge). Write a retroactive ADR documenting what you believe the decision was and why.

2. **ADR Archaeology**: Review your team's existing ADRs (if any). Assess: Are they still relevant? Have they been superseded? What would you improve?

3. **Decision Journal**: For one week, document every technical decision you make (even small ones). Identify which deserved ADRs and which didn't.

---

## Reflection Questions

After completing this lab, reflect on:

1. When have you wished you had documentation about a past decision?
2. What resistance might you face introducing ADRs to your team?
3. How would ADRs fit into your team's existing documentation practices?
4. What decisions in the past 6 months deserved ADRs?

---

## Next Steps

- Complete Lab 3: Technical Presentation Practice
- Review real-world ADRs from your organization
- Start using ADRs for your next significant technical decision
- Share this practice with your team
