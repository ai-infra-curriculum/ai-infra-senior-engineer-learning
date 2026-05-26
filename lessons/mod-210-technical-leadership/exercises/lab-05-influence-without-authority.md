# Lab 05: Influence Without Authority

## Objectives

1. Practice the senior-engineer's core skill: driving
   technical change across teams you don't manage.
2. Produce three written artifacts that demonstrate influence.
3. Plan a cross-team initiative with stakeholder buy-in.
4. Identify the failure modes of influence and how to avoid
   them.

## Senior-scale framing

References:
- `engineer-solutions/mod-106 ex-14` — governance patterns
  (the work product that influences ML teams).
- `mlops-learning/projects/project-4-governance` — the
  reference implementation that's an organizing artifact.

This lab focuses on the **leadership** dimension. Senior
engineers ship through documents and conversations as much
as through code; this lab tests whether you can produce them.

## Estimated time

3 hours

## Part 1: An RFC

Pick a real (or realistic) cross-team technical change you
want to drive. Examples:
- Adopting Cosign-keyless across all CI workflows.
- Migrating from in-house secret management to Vault.
- Establishing the model-promotion gate as a hard requirement.

Write the RFC (3–4 pages):
- Problem statement.
- Proposed change.
- Alternatives considered + rejected, with reasons.
- Trade-offs accepted.
- Migration / rollout plan.
- Open questions for stakeholders.

## Part 2: An ADR

Write an Architecture Decision Record for a smaller decision
(1 page):
- Title.
- Status: proposed / accepted / superseded.
- Context.
- Decision.
- Consequences.
- Alternatives.

Pick something concrete: "Use Kyverno over Gatekeeper for
admission control," or "Use SPIFFE-SPIRE for workload identity
over cloud-native IAM."

## Part 3: A pre-mortem

Pick a planned initiative likely to ship next quarter.
Write a 1-page pre-mortem: assume it has failed; document
why, and what the team should do now to prevent each failure
mode.

## Part 4: Stakeholder map

For the RFC in Part 1, map stakeholders:
- Who must approve.
- Who must be informed.
- Who will resist + why.
- The conversation order to reach approval.

## Part 5: Deliverables

Submit:

1. **RFC** (3–4 pages).
2. **ADR** (1 page).
3. **Pre-mortem** (1 page).
4. **Stakeholder map** + conversation plan.

## Reflection questions

1. Which artifact would you actually send tomorrow if
   given the opportunity?
2. Which stakeholder will resist hardest and why?
3. What does success look like for the RFC — not "approved"
   but "operating as designed in 12 months"?

## Reference solution

`senior-engineer-solutions/mod-210-technical-leadership/exercise-
05/` points to engineer-track + the governance reference
implementation.
