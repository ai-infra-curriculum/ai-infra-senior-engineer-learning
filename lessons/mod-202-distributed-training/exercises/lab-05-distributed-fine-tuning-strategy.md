# Lab 05: Distributed Fine-Tuning Strategy

## Objectives

1. Design a distributed fine-tuning pipeline for a large open-
   weight LLM (Llama 3 70B or similar).
2. Choose between LoRA, QLoRA, full fine-tuning, and decide on
   parallelism strategy (DDP, FSDP, DeepSpeed Zero).
3. Quantify the GPU-hour cost and define the validation
   methodology.
4. Plan for spot-instance interruptions and checkpoint
   recovery.

## Senior-scale framing

The engineer-track references give you the implementations:
- `engineer-solutions/mod-110 ex-05` — LoRA/QLoRA mechanics.
- `engineer-solutions/mod-107 ex-03` — single-node training
  baseline.

This lab is about the **decision-making layer**: which strategy
fits which use case, what the cost model looks like, and how
the rollout is structured for an org that needs to fine-tune
multiple models across multiple teams.

## Estimated time

4–6 hours

## Part 1: Scenario

Your platform has three concurrent fine-tuning needs:

- **Clinical** team: domain-adapt Llama 3 70B on 50k de-identified
  patient notes. Privacy-sensitive (DP-SGD candidate).
- **Customer-support** team: fine-tune on customer-support
  conversations. Volume large, sensitivity moderate.
- **Internal-docs** team: small (5k example) fine-tune for an
  internal RAG assistant. Low-priority.

Produce a per-team decision matrix.

## Part 2: Strategy decisions

For each team, decide:

- LoRA vs. QLoRA vs. full fine-tune.
- Parallelism (DDP vs. FSDP vs. DeepSpeed Zero).
- Hardware (H100, A100, on-demand vs. spot).
- Budget per training run.
- Validation methodology.
- DP-SGD on/off + privacy budget if on.

Defend each choice. Cite the engineer-track exercises for the
mechanics; this lab focuses on the trade-offs.

## Part 3: Cost model

Build a spreadsheet (or table) estimating GPU-hours per training
run for each team. Convert to dollars at current cloud rates.

Sensitivity analysis: what if the team needs to retrain monthly?
What's the annual budget envelope?

## Part 4: Checkpoint + spot recovery

For the spot-eligible training runs, document:

- Checkpoint cadence (per how many steps).
- Storage cost of checkpoints.
- Recovery time when a spot instance is reclaimed.
- The break-even point where spot is cheaper than on-demand.

## Part 5: Deliverables

Submit:

1. **Strategy doc** (2 pages) — per-team decisions with rationale.
2. **Cost spreadsheet** — GPU-hours, dollars, sensitivity bands.
3. **Operational runbook** for the highest-stakes training run
   (clinical) including spot recovery, DP-SGD accounting, and
   validation gating.

## Reflection questions

1. Which decision will the CFO push back on most? How do you
   defend it?
2. Which decision will the ML engineer push back on most? How
   do you defend it?
3. If GPU supply tightens (e.g., during a major release wave),
   which training runs get paused first?

## Reference solution

The corresponding `senior-engineer-solutions/mod-202-distributed-
training/exercise-05/` is a pointer document; implementation
mechanics live in
[`engineer-solutions/mod-110`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-110-llm-infrastructure)
and
[`engineer-solutions/mod-107`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-107-gpu-computing).
