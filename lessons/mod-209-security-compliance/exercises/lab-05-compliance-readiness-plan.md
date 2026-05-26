# Lab 05: Compliance Readiness Plan

## Objectives

1. Plan the compliance readiness program for SOC 2 Type 2 +
   GDPR + HIPAA + EU AI Act.
2. Sequence the work realistically given the team size.
3. Define the audit-chain integration that produces
   compliance evidence continuously.
4. Plan the customer-facing trust narrative.

## Senior-scale framing

References:
- `engineer-solutions/mod-109` — IaC + secret management +
  policy as code.
- `engineer-solutions/mod-103 ex-10` — supply-chain controls.
- `security-solutions/projects/project-2-compliance` — the
  compliance project with audit chain.

This lab is the **senior engineer's view of compliance**:
not the regulatory expert's view (that's the security track's
Module 07), but how the engineering org organizes itself
around the compliance work.

## Estimated time

3–4 hours

## Part 1: Regulation overlap matrix

For each regulation, identify the controls that satisfy it +
the controls that overlap with another regulation:

| Control | SOC 2 | GDPR | HIPAA | EU AI Act |
|---|---|---|---|---|
| Encryption at rest | | | | |
| Access reviews | | | | |
| Audit logging | | | | |
| ... | | | | |

The overlap matrix reveals which engineering investments
satisfy multiple regulations at once.

## Part 2: Audit-chain integration

Cross-reference Module 03 (Cryptography) of the security track:
the hash-chain audit log is the compliance substrate.

Design which events get recorded:
- Subject requests.
- Model promotions.
- Vendor sub-processor changes.
- Access reviews.
- Policy violations.
- Breach incidents.
- ...

For each, the signing identity + retention.

## Part 3: 12-month plan

Sequence:
- **Q1**: SOC 2 readiness foundation.
- **Q2**: SOC 2 audit period begins.
- **Q3**: SOC 2 attestation complete + GDPR + HIPAA continuous
  posture.
- **Q4**: EU AI Act technical documentation.

Per quarter: deliverables, success criterion, dependencies.

## Part 4: Customer-facing narrative

Draft (1 page) the compliance posture document that customer
CISOs receive during security reviews. Address:
- Certifications + status.
- Sub-processors with regulated data.
- Encryption / access / audit controls.
- Breach notification commitments.
- Maturity acknowledgment + roadmap.

## Part 5: Deliverables

Submit:

1. **Overlap matrix** showing which controls satisfy multiple
   regulations.
2. **Audit-chain integration spec**.
3. **12-month compliance roadmap**.
4. **Customer-facing compliance narrative** (1 page).

## Reflection questions

1. Which regulation will the team push back on hardest? Why?
2. The first SOC 2 audit period will find gaps. What's the
   structural response?
3. EU AI Act timelines are long but the work is large. How do
   you keep it from being deprioritized in favor of SOC 2?

## Reference solution

`senior-engineer-solutions/mod-209-security-compliance/exercise-
05/` points to security-solutions/projects.
