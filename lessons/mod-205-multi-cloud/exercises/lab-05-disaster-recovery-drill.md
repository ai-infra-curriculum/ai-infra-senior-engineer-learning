# Lab 05: Multi-Cloud Disaster Recovery Drill

## Objectives

1. Design a DR plan for a multi-cloud ML platform.
2. Define RPO / RTO per workload class.
3. Plan a tabletop drill simulating a cloud-provider regional
   outage.
4. Identify cost vs. recovery-time trade-offs.

## Senior-scale framing

References:
- `engineer-solutions/mod-109` — IaC + GitOps for
  reproducibility.
- `engineer-solutions/mod-104 ex-10` — cluster federation
  patterns.

This lab focuses on the **operational** layer: how the platform
recovers when a cloud provider has a regional incident.

## Estimated time

4 hours

## Part 1: Workload classification

Group production workloads by criticality:
- **Tier 1**: customer-facing inference; RTO < 1 hour.
- **Tier 2**: training pipelines; RTO < 24 hours.
- **Tier 3**: experimentation, notebooks; RTO < 1 week.

Document the RPO and RTO per tier and the SLA implications.

## Part 2: DR architecture

For Tier 1:
- Active-active across regions in primary cloud (AWS
  us-west-2 ↔ us-east-1)?
- Or active-passive cross-cloud (AWS → GCP)?
- Cost vs. recovery time analysis.

For Tier 2:
- Cold-DR via state in object storage + Terraform replay.

For Tier 3:
- Best-effort recovery.

## Part 3: Tabletop scenario

Design a 90-minute tabletop:

- **Setup**: AWS us-west-2 just went down at 14:00 UTC.
  Customer traffic is failing. The DR plan exists in Confluence
  but has never been exercised.
- **Inject events**: at +15, +30, +60 minutes.
- **Decision points**: failover timing, communication, cost.
- **Expected outcomes**: what a well-run drill achieves.

## Part 4: Cost vs. recovery trade-off

Build a table:

| RTO target | Cost / month | Notes |
|---|---|---|
| 5 min | $XXk | Active-active everywhere |
| 1 hour | $XXk | Hot-standby in secondary region |
| 4 hours | $XXk | Cold restore from backup |
| 24 hours | $XXk | Rebuild from IaC |

Show where NorthBridge sits today + the proposed move.

## Part 5: Deliverables

Submit:

1. **DR architecture document** with per-tier strategies.
2. **Tabletop scenario** runnable by the team.
3. **Cost vs. recovery trade-off table**.
4. **Quarterly drill schedule** + scope.

## Reflection questions

1. Which workload is most expensive to keep recoverable?
   What's the business case for that cost?
2. The first tabletop will surface gaps. What's the structural
   change you expect to make?
3. A regulatory auditor asks "show me your DR test results
   from the past year." What do you produce?

## Reference solution

`senior-engineer-solutions/mod-205-multi-cloud/exercise-05/`
points back to `engineer-solutions/mod-109` (IaC) and
[`mod-104 ex-10`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-104-kubernetes/exercise-10-cluster-federation).
