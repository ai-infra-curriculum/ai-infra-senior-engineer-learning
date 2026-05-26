# Lab 05: SRE On-Call Program

## Objectives

1. Design a sustainable on-call rotation for an ML platform
   team scaling from 8 to 25 engineers.
2. Distinguish platform on-call from ML-team on-call.
3. Plan incident response drills + postmortem cadence.
4. Define the metrics that detect on-call burnout before it
   happens.

## Senior-scale framing

The engineer-track reference: `engineer-solutions/mod-108` —
covers AlertManager routing, incident-response gameday, alert
quality.

This lab focuses on the **operational sustainability** at the
team-scale level.

## Estimated time

3–4 hours

## Part 1: Rotation design

At each scale point, design the rotation:

| Team size | Rotation length | Coverage model | Comp |
|---|---|---|---|
| 8 engineers (today) | | | |
| 15 engineers (Q2) | | | |
| 25 engineers (Q4) | | | |

Address:
- Single rotation vs. split (platform + ML-team).
- Weekly vs. daily handoff.
- Time-zone coverage as the team grows geographically.
- Comp time / weekend protection.

## Part 2: Alert quality

The on-call experience depends on alert quality. Define:
- **Actionable alerts** (page someone) — what qualifies.
- **Informational alerts** (Slack) — what qualifies.
- **Auto-resolved alerts** — what qualifies.
- The quarterly cadence to retire stale alerts.

Pull from the runbook + tabletop work in Module 11 (Security
Operations) and Module 08 (Runtime Security) for the patterns.

## Part 3: Drill + postmortem cadence

- Quarterly tabletops on what scenarios?
- Annual game day on what scope?
- Postmortem cadence per incident class?
- Postmortem review cadence (leadership visibility)?

## Part 4: Burnout signals

Define leading indicators of on-call burnout:
- Pages per rotation per engineer.
- Sleep-disrupting pages per rotation.
- Voluntary swaps / declined rotations.
- Survey signals.

What's the structural response when these go red?

## Part 5: Deliverables

Submit:

1. **Rotation design table** for 3 scale points.
2. **Alert quality bar** with examples.
3. **Drill + postmortem calendar** for the year.
4. **Burnout-signal dashboard** mockup + response plan.

## Reflection questions

1. Which scale transition will hurt the most? (Probably
   8 → 15: too small for a real SRE team, too big for one
   rotation.)
2. The CTO asks "how do you measure if on-call is healthy?"
   What's the answer?
3. A senior engineer is consistently picking up double
   rotations because they're "good at it." How do you
   intervene?

## Reference solution

`senior-engineer-solutions/mod-207-observability-sre/exercise-
05/` points to
[`engineer-solutions/mod-108`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-108-monitoring-observability).
