# Lab 04: Cross-Cloud IaC Design

## Objectives

1. Design Terraform module structure for a multi-cloud
   platform (AWS + GCP, optionally Azure).
2. Decide on shared abstractions vs. per-cloud modules.
3. Plan the state-management and CI/CD topology.
4. Identify the operational cost of multi-cloud IaC.

## Senior-scale framing

The engineer-track reference: `engineer-solutions/mod-109` —
13 IaC exercises with full Terraform implementations.

This lab is about the **architecture above the IaC code**: how
modules compose across clouds, what's shared, what's per-cloud,
and what the team's operational burden looks like.

## Estimated time

3–4 hours

## Part 1: Cloud architecture overview

Document your multi-cloud topology:
- Primary cloud (AWS) — what runs here.
- Secondary cloud (GCP) — what runs here.
- DR / failover relationship.
- Data residency considerations (EU customers on GCP-EU).

## Part 2: Module structure

Propose a Terraform module structure. Address:
- **Shared modules** — abstractions that work across clouds
  (Kubernetes cluster, monitoring stack).
- **Per-cloud modules** — things that don't abstract well
  (IAM, KMS).
- **Environment-level overlays** — dev/staging/prod.

Show the directory layout + the relationship between modules.

## Part 3: State management

Design state management:
- Per-environment state files?
- Per-cloud or unified?
- Locking mechanism.
- Backup + recovery.

## Part 4: CI/CD topology

Plan the CI/CD:
- Plan + apply workflows.
- Approval gates (especially for prod).
- Drift detection.
- Cost tracking integration.

## Part 5: Operational cost

Honestly estimate:
- Engineer-hours per quarter to maintain.
- Drift remediation time.
- Cost of a multi-cloud outage (one provider has incident
  affecting your IaC).

## Part 6: Deliverables

Submit:

1. **Architecture diagram** (clouds, environments, modules).
2. **Module tree** with naming and ownership.
3. **State management design**.
4. **CI/CD workflow** outline.
5. **Operational cost estimate**.

## Reflection questions

1. Which abstraction will fall apart first as the platform
   grows?
2. The team objects: "Multi-cloud IaC is too much work; let's
   stick with one cloud." Argue both sides.
3. If you had to migrate from AWS-primary to GCP-primary in
   12 months, what does the plan look like?

## Reference solution

`senior-engineer-solutions/mod-205-multi-cloud/exercise-04/` is
a pointer doc. The IaC code lives in
[`engineer-solutions/mod-109`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-109-infrastructure-as-code)
and federation patterns in
[`engineer-solutions/mod-104 ex-10`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-104-kubernetes/exercise-10-cluster-federation).
