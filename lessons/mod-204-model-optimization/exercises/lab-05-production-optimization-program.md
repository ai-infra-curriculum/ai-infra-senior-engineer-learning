# Lab 05: Production Optimization Program

## Objectives

1. Build a quarterly model-optimization program for the
   platform.
2. Identify candidate models, predict savings, define
   acceptance criteria.
3. Plan the rollout including regression-testing.
4. Quantify ROI and present to leadership.

## Senior-scale framing

The engineer-track references give you the optimization
techniques:
- `engineer-solutions/mod-110 ex-06` — LLM-specific
  optimization.
- `engineer-solutions/mod-107 ex-08/09` — quantization +
  pruning + ONNX conversion.

This lab is about **running an optimization program**: which
models, in what order, with what success criteria, defended to
leadership.

## Estimated time

4–5 hours

## Part 1: Model inventory + scoring

For each of 8 production models, score:
- Current inference cost / month.
- Estimated optimization gain (% latency reduction or %
  cost reduction).
- Risk of optimization causing quality regression.
- Engineering effort.

Use the scoring to pick the top 3 candidates for this quarter.

## Part 2: Per-model plan

For each top-3 candidate, document:
- Optimization techniques to apply (quantization, distillation,
  pruning, TensorRT conversion).
- Acceptance criteria (clean-accuracy floor, latency target,
  cost target).
- Validation methodology (offline benchmark + shadow traffic).
- Rollback plan if production behavior degrades.

## Part 3: Regression-testing infrastructure

Optimizations silently degrade quality if not monitored.
Design:
- Per-model regression test suite.
- CI integration so every model promotion runs the suite.
- Production drift monitoring.
- Alert thresholds.

## Part 4: ROI presentation

Prepare a 1-page presentation for leadership:
- Total cost reduction expected (dollars + percentage).
- Risk-adjusted estimate.
- Timeline.
- Engineering cost.
- Confidence level.

## Part 5: Deliverables

Submit:

1. **Model inventory + scoring sheet**.
2. **Per-model optimization plan** for the top 3.
3. **Regression-test design** with example rules.
4. **1-page ROI brief** for leadership.

## Reflection questions

1. Which optimization will leadership push back on (e.g.,
   quantization risks for a clinical model)?
2. The team objects: "Optimization is risky; we should
   leave production alone." How do you respond?
3. If you had to cut the program scope to one model, which
   would you keep?

## Reference solution

`senior-engineer-solutions/mod-204-model-optimization/exercise-
05/` is a pointer doc. Implementation depth lives in
[`engineer-solutions/mod-110`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-110-llm-infrastructure)
and
[`engineer-solutions/mod-107`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-107-gpu-computing).
