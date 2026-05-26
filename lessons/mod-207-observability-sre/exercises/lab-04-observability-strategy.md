# Lab 04: Observability Strategy

## Objectives

1. Design the observability stack for a multi-cluster, multi-
   team ML platform.
2. Decide what's metrics, what's logs, what's traces — and
   what goes where.
3. Plan retention, storage cost, and query patterns.
4. Identify the three signals that matter most.

## Senior-scale framing

The engineer-track reference: `engineer-solutions/mod-108` —
10 observability exercises with Prometheus, Grafana, OpenTelemetry,
alert routing, dashboards-as-code.

This lab is the **strategy layer**: which observability
investment compounds; which signals are noise; how the program
scales with the org.

## Estimated time

4 hours

## Part 1: Pillar allocation

For each observability concern, choose the right pillar
(metrics, logs, traces) and rationale:

- Per-request latency.
- Per-tenant cost.
- Model accuracy drift.
- Pipeline execution status.
- Per-service availability.
- Per-request user identity (for audit).
- Per-prediction confidence distribution.
- GPU utilization.

## Part 2: Storage + retention

Build a retention table:

| Signal type | Hot retention | Warm retention | Cold retention | Total cost/mo |
|---|---|---|---|---|

Address: what gets sampled at scale, what survives audit
windows, what's compliance-required.

## Part 3: The three signals that matter most

Identify the **three observability signals** that, if you could
only have three, you would keep. Defend.

This forces the question of what observability is *for*.
"Everything is important" is not a defense.

## Part 4: SLO framework

Define SLOs for two production workloads (your choice):

- The SLO (e.g., 99.9% of requests < 200ms).
- The error budget.
- The burn-rate alert thresholds.
- The decision rule when budget is exhausted.

## Part 5: Deliverables

Submit:

1. **Pillar allocation table** with rationale per signal.
2. **Retention + cost model**.
3. **Top-3 signals** with defense.
4. **Two SLO specs** + alert rules.

## Reflection questions

1. Which signal would your CTO be most surprised to see is
   "not in the top 3"?
2. The team objects: "Datadog costs are too high; cut the
   bill 30%." What do you cut first?
3. A new ML team launches; what observability investment
   carries over directly vs. needs new work?

## Reference solution

`senior-engineer-solutions/mod-207-observability-sre/exercise-
04/` is a pointer doc. Implementation depth in
[`engineer-solutions/mod-108`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-108-monitoring-observability).
