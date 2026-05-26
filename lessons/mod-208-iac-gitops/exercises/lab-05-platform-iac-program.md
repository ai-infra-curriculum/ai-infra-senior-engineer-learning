# Lab 05: Platform IaC + GitOps Program

## Objectives

1. Design the IaC + GitOps program for a 25-engineer ML org.
2. Decide ownership boundaries (platform team vs. ML teams).
3. Plan policy gates + drift detection.
4. Define incident-response for IaC failures.

## Senior-scale framing

The engineer-track reference: `engineer-solutions/mod-109` —
13 IaC exercises covering Terraform modules, GitOps with
ArgoCD, multi-environment promotion, policy-as-code.

This lab focuses on the **program-design layer**: how IaC +
GitOps scales as the platform serves multiple ML teams.

## Estimated time

3–4 hours

## Part 1: IaC ownership boundaries

For each layer, decide ownership:

- **Cluster-level infrastructure** (clusters, IAM, KMS):
  platform team.
- **Shared services** (Vault, monitoring, mesh): ?
- **Per-namespace resources**: ?
- **Application-level configs**: ?

Tighter platform ownership = consistency + slower ML-team
velocity. Tighter ML-team ownership = drift + faster velocity.
Find the balance and defend.

## Part 2: GitOps topology

Design:

- **Per-cluster ArgoCD vs. central ArgoCD?**
- **App-of-apps pattern** or flat manifests?
- **Branch strategy** (env per branch vs. env per directory).
- **Promotion workflow** (PR + approval + auto-sync).

## Part 3: Policy + drift

Cross-reference Module 09 (policy-as-code):
- Which Conftest policies run on every PR?
- What does the admission policy verify on GitOps-applied
  resources?
- How is drift between cluster state and Git state detected?
- What's the on-call response when drift fires?

## Part 4: Incident response

For each scenario, the IR procedure:

- **A bad Terraform plan got applied** — production has a
  misconfigured resource that's causing customer impact.
- **GitOps sync stopped** — silent failure means Git changes
  aren't reaching the cluster.
- **A secret leaked via a public IaC repo commit** (the
  classic).

## Part 5: Deliverables

Submit:

1. **Ownership matrix** with defended boundaries.
2. **GitOps topology diagram**.
3. **Policy-gate inventory** + drift-detection design.
4. **Three IaC incident playbooks**.

## Reflection questions

1. Where will ownership boundaries be most contested?
2. The ML team objects: "GitOps slows us down; we just want
   to `kubectl apply`." What's the response?
3. An incident happens *because* IaC was applied correctly
   to the wrong env. How do you prevent that structurally?

## Reference solution

`senior-engineer-solutions/mod-208-iac-gitops/exercise-05/`
points to
[`engineer-solutions/mod-109`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-109-infrastructure-as-code).
