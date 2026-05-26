# Lab 05: GPU Fleet Strategy at Senior Scale

## Objectives

1. Design a GPU fleet strategy for a 25-engineer ML org with
   mixed training + serving workloads.
2. Decide hardware mix (H100, A100, L4, L40S, T4) based on
   workload characteristics.
3. Build a cost-vs-utilization model.
4. Plan for the Blackwell / next-generation transition.

## Senior-scale framing

The engineer-track reference is `engineer-solutions/mod-107` —
11 GPU-computing exercises with full implementations of
profiling, optimization, multi-GPU patterns.

This lab is the **procurement + fleet-design layer** on top.
Reading the engineer-track gives you the vocabulary; this lab
makes the senior-scale decisions.

## Estimated time

4–5 hours

## Part 1: Workload inventory

You have these production workloads:

- **Training**: nightly retraining of 4 models. Mix of
  data-parallel (DDP) and distributed (FSDP).
- **Inference**: 6 serving deployments. Latency-sensitive
  (recommender, fraud) vs. throughput-sensitive (batch
  scoring).
- **Notebooks**: 20 data scientists with interactive GPU
  notebooks. Most idle most of the time.
- **Fine-tuning**: occasional LoRA / QLoRA runs.

For each workload, identify:
- Required GPU type (compute vs. memory bound).
- Required GPU count (single, multi, distributed).
- Tolerance for spot interruptions.
- Latency / throughput requirements.

## Part 2: Fleet design

Propose a fleet composition. For each SKU:
- Quantity.
- Use case.
- Reservation vs. on-demand vs. spot mix.
- Annual cost estimate.

Apply these constraints:
- Budget: ~$2M annual GPU spend.
- Mix of cloud providers (AWS primary, GCP secondary).
- Reasonable buffer for unexpected workloads.

## Part 3: Utilization model

Build a utilization model:
- Training: % of time the GPU is at >80% utilization.
- Inference: peak / average / valley ratios.
- Notebooks: realistic utilization (typically 10–30%).

Calculate effective cost per useful GPU-hour. Where's the
waste? What's the highest-leverage optimization?

## Part 4: Blackwell transition plan

NVIDIA's Blackwell (B100/B200) ships in 2024+. Plan:
- When does NorthBridge start procuring Blackwell?
- Which workloads migrate first?
- What's the resale strategy for the older H100 fleet?
- How do you avoid being stuck with 2 generations of
  spare capacity?

## Part 5: Deliverables

Submit:

1. **Workload-to-hardware matrix**.
2. **Fleet composition table** with cost estimate.
3. **Utilization model** + identified optimization
   opportunities.
4. **Blackwell transition plan** with phased timeline.

## Reflection questions

1. Which workload is hardest to right-size? Why?
2. The product team wants to add a new LLM serving deployment.
   How do you answer "do we have the GPU capacity"?
3. The CFO sees the fleet cost and asks for 30% reduction.
   What's the response?

## Reference solution

The corresponding `senior-engineer-solutions/mod-203-gpu-
computing/exercise-05/` is a pointer document.
Implementation depth lives in
[`engineer-solutions/mod-107`](https://github.com/ai-infra-curriculum/ai-infra-engineer-solutions/tree/main/modules/mod-107-gpu-computing).
