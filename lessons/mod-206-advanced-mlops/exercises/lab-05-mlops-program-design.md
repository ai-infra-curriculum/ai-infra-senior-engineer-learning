# Lab 05: MLOps Program Design at Senior Scale

## Objectives

1. Design the MLOps program for a 25-engineer ML org with
   8+ models in production.
2. Decide on the platform's MLOps surface area (what's
   managed vs. owned by ML teams).
3. Plan governance: model registry, promotion gates,
   incident response.
4. Build a 4-quarter rollout plan.

## Senior-scale framing

The engineer-track reference: `engineer-solutions/mod-106` —
14 MLOps exercises with full implementations of registry,
serving, A/B testing, governance, monitoring.

This lab is the **program-design layer**: which patterns
become platform features, which remain in ML teams' hands,
and how the program scales with the org.

## Estimated time

4–5 hours

## Part 1: MLOps surface map

For each MLOps capability, decide ownership:

- **Platform-owned** — built once, used by all ML teams.
- **ML-team-owned** — each team builds their own.
- **Shared with platform standards** — teams build but follow
  platform-mandated patterns.

Capabilities to allocate:
- Experiment tracking (MLflow / W&B).
- Model registry.
- Feature store.
- Serving infrastructure.
- A/B testing.
- Model monitoring + drift detection.
- Retraining pipelines.
- Governance + audit.

## Part 2: Promotion gate design

Author the model promotion gate (cross-references your Module
09 work on policy-as-code):

- What evidence is required.
- Who approves.
- How decisions are audited.
- What can be bypassed (break-glass) and the audit trail
  that requires.

## Part 3: Incident response

For each of these MLOps incidents, write a 1-page response
playbook:

- **Drift detected**: a production model's input distribution
  has shifted.
- **Quality regression**: post-promotion validation finds the
  new model is worse than the prior on a subset.
- **Mass failure**: a serving deployment is returning errors
  on all requests.

## Part 4: 4-quarter rollout

Sequence:
- **Q1**: foundation (registry, basic serving, audit).
- **Q2**: governance (promotion gate, drift monitoring).
- **Q3**: experimentation (A/B testing infrastructure).
- **Q4**: scale (multi-team self-service).

Per quarter: deliverables, success criterion, dependencies.

## Part 5: Deliverables

Submit:

1. **Capability allocation table** (platform vs. team).
2. **Promotion gate spec** (policy + evidence).
3. **Three incident playbooks** (drift, regression, mass
   failure).
4. **4-quarter rollout plan**.

## Reflection questions

1. Which capability will the ML teams resist platform
   ownership of? How do you respond?
2. Which capability will the platform team be happiest to
   offload to ML teams?
3. What's the success metric for the program (not "we
   shipped" — what does the org look like differently when
   it's working)?

## Reference solution

`senior-engineer-solutions/mod-206-advanced-mlops/exercise-05/`
is a pointer doc. Implementation depth lives in
[`engineer-solutions/mod-106`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-106-mlops).
