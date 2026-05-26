# Lab 05: Senior-Scale Platform Operator Design

## Objectives

1. Design a Kubernetes operator for a non-trivial ML platform
   abstraction (`TrainingJob`, `ModelDeployment`, or
   `FeatureStoreView`).
2. Articulate the multi-team, multi-tenant constraints the
   operator must respect.
3. Identify what the operator should *enforce* versus what
   should remain in policy-as-code or admission controllers.
4. Produce an architecture document + a CRD spec + a
   reconciliation outline.

## Senior-scale framing

The engineer-track work (`engineer-solutions/mod-104` —
operator, GPU scheduling, helm, multi-tenancy) is the
**implementation reference**. This lab is about the layer above
it: the design decisions that determine whether the operator
serves a 5-team or 50-team org.

You are not writing production-grade Go for a controller here.
You are designing the *contract*: the CRD, the reconciliation
loop, the failure modes, the rollout plan.

## Prerequisites

- Completion of mod-201 lectures + labs 01–04.
- Read `engineer-solutions/mod-104` end-to-end as background.
- Working understanding of Kubernetes controller patterns
  (informers, reconciliation, finalizers).

## Estimated Time

6–8 hours

## Part 1: Scope the operator (1 hour)

Pick one of these (or propose your own with rationale):

- `TrainingJob` — orchestrates multi-node distributed training
  runs with checkpointing, spot tolerance, and per-team
  isolation.
- `ModelDeployment` — manages canary, blue-green, and shadow
  rollouts of model versions; integrates with the registry.
- `FeatureStoreView` — exposes per-team subsets of a shared
  feature store with quotas and audit.

Produce:

- A **user story** (what does an ML engineer want to write?
  What's the YAML the operator consumes?).
- A **non-goal list** (what does the operator deliberately not
  do?).
- A **trust boundary diagram** (what does the operator trust;
  what does it verify?).

## Part 2: CRD specification (2 hours)

Author the CRD spec in YAML. Required fields:

- `metadata` — name, namespace, ownership labels.
- `spec` — the user-facing configuration.
- `status` — observed state, phase, conditions.

Apply the following constraints:

- The spec must be **enforceable** — fields that can't be
  validated at admission go in `status` with explicit
  reconciliation.
- The spec must **versionable** — assume v1alpha1 → v1beta1 →
  v1 transitions over 18 months.
- The spec must **multi-tenant safe** — no field can reach
  cross-tenant resources without an explicit policy check.

## Part 3: Reconciliation outline (2 hours)

Sketch the reconciliation loop:

- **Watch** — which resources does the operator watch?
- **Decide** — for each spec change, what's the desired state?
- **Act** — what does the operator create/update/delete?
- **Status** — what does the operator write back?
- **Failure** — what happens when downstream resources fail?

Identify at least 5 failure modes and the recovery for each.

## Part 4: Multi-tenancy + policy boundary (1 hour)

For each of the following concerns, name whether the operator
enforces it, an admission policy enforces it, or both:

- Tenant labels must be present.
- GPU quotas per tenant.
- Image must be signed (cosign verification).
- Resource requests/limits must be set.
- Network policy must permit egress to expected destinations
  only.
- Model artifact must come from approved registry.

Justify your choice for each. (Hint: belt-and-suspenders is
sometimes correct, sometimes operational overhead.)

## Part 5: Deliverables

Submit:

1. **Architecture document** (2–3 pages) — user story,
   scope, trust boundaries, rationale.
2. **CRD spec YAML** with comments explaining the design
   decisions.
3. **Reconciliation pseudocode** (or Go skeleton) covering
   the happy path + 3 failure modes.
4. **Policy boundary table** showing what's operator vs.
   admission vs. both.

## Reflection questions

1. Which design decision will most constrain you in 18 months
   when v2 of the CRD ships? What's the migration story?
2. The platform team operates the operator. The ML teams
   are the users. What does the operator team owe the ML
   teams as an SLA?
3. A new ML team has a use case that doesn't fit your CRD.
   What's the right response: extend the CRD, extend with a
   sub-CRD, or push back?

## Reference solution

The corresponding `senior-engineer-solutions/mod-201-advanced-
kubernetes/exercise-05/` is a pointer document. The underlying
implementation patterns live in
[`engineer-solutions/mod-104`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-104-kubernetes).
The senior-scale layer (architecture, scale, trade-offs) is
what this lab adds on top.
