# Lab 04: Security Program Design at Senior Scale

## Objectives

1. Design the security program for a 25-engineer ML org.
2. Cover the cross-cutting controls: identity, secrets, runtime,
   supply chain, detection.
3. Plan the relationship with the dedicated security track.
4. Define the maturity model + assessment cadence.

## Senior-scale framing

References:
- `engineer-solutions/mod-109 ex-07/08` — secrets + policy.
- `engineer-solutions/mod-103 ex-10` — supply-chain (Cosign +
  SBOM).
- `security-solutions/projects/` — the 5 dedicated security
  projects.

This lab is the **program-design layer**: how a senior engineer
(not a security specialist) thinks about security investments
and presents them to leadership.

## Estimated time

3–4 hours

## Part 1: Security maturity model

Define a 5-level maturity model across these dimensions:
- Identity (workload + human).
- Secrets management.
- Runtime detection.
- Supply chain.
- Compliance posture.
- Incident response.

For each level, what does it look like operationally? Where is
the org today?

## Part 2: Roadmap

Plan the 12-month roadmap to advance one maturity level:
- What ships in Q1, Q2, Q3, Q4.
- Cost + effort estimates.
- Dependencies (e.g., SOC 2 timeline drives some priorities).
- The first 3 metrics you'd publish to leadership.

## Part 3: Boundary with security team

NorthBridge has a dedicated security engineer (the user of the
[security learning track](https://github.com/ai-infra-curriculum/ai-infra-security-learning)).
Articulate:
- What's owned by the platform team.
- What's owned by the security team.
- The interface (RACI, escalation, joint accountability).

## Part 4: Risk register

Build a 10-item risk register:
- Risk name + description.
- Likelihood × Impact = Score.
- Current mitigations.
- Required mitigations.
- Owner + target date.

## Part 5: Deliverables

Submit:

1. **Maturity model** + current-state assessment.
2. **12-month roadmap**.
3. **Boundary document** (platform vs. security team).
4. **Risk register** (10+ items).

## Reflection questions

1. Where will platform team + security team boundaries be
   contested?
2. The CFO asks "how much security is enough?" What's the
   answer?
3. Which risk in the register is most likely to be
   under-prioritized? Why?

## Reference solution

`senior-engineer-solutions/mod-209-security-compliance/exercise-
04/` points to engineer-track + dedicated security track work.
