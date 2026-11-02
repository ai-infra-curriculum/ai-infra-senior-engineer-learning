# Senior AI Infrastructure Engineer — Job Requirements Report

**Role:** Senior AI Infrastructure Engineer (level 30)
**Repository:** `ai-infra-senior-engineer-learning`
**Research window:** 2026-07-05 → 2026-10-03 (last 90 days)
**Postings analyzed:** 30 (all within the 90-day window)
**Content model:** anthropic/claude-opus-4-7
**Machine-readable source:** [`.aicg/job-requirements.json`](.aicg/job-requirements.json)
**Curriculum-plan delta this cycle:** [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json) — **zero additions** (fourth consecutive cycle)

---

## 1. Headline

The 2026-Q4 market for Senior AI Infrastructure Engineers has sharpened further around the existing 10-module + 4-project curriculum. Across 30 postings from the last 90 days — a GPU-neocloud + inference-platform + SRE-heavy sample (CrowdStrike LLM Platforms, NVIDIA DGX Cloud + EDA, Perplexity CoreWeave GB200, Cohere HPC GPU/TPU superclusters, Lambda Managed K8s, Red Hat vLLM FDE, stack8s vLLM, Adobe AI Platform, Mirantis SRE, Sesterce SRE, JPM AI Infra, Firmus sovereign-cloud, Anduril Physical Infra) — the core level-30 stack strengthened across the board. Advanced Kubernetes rose to 0.80 (from 0.72), GPU cluster ops to 0.77 (from 0.66), observability/SRE to 0.40 (from 0.31), model-serving optimization to 0.37 (from 0.28, cleanly above threshold now), and LLM serving platforms to 0.37 (fourth consecutive cycle above 0.30). Every requirement that clears both continuity-bias bars (≥ 3 postings AND ≥ 0.30 frequency) *after applying the Ownership Rule* is already owned at level 30 by an existing senior module. The two threshold-clearing items that belong at other levels (`req-llm-serving-link` 0.37 and `req-systems-programming` 0.33) are handled the same way as prior cycles: linked, not duplicated.

The curriculum-plan delta is intentionally empty — see §5. This is the **fourth consecutive** cycle to reach a zero-addition verdict; the 2026-07 cycle reached the same conclusion with 22 postings, 2026-08 with 28, and 2026-09 with 32.

---

## 2. How to read this document

- Each requirement is grouped by category, lists the **owner role** (per the curriculum hierarchy), and points to where it is covered in this repo *or* in a lower/peer/higher-level repo.
- Ownership follows the lowest-level rule: a requirement is owned by the lowest level where it is genuinely required, and higher-level roles only re-own it when they need extra depth, architecture context, or leadership context.
- Frequencies are the fraction of postings from the last 90 days (out of 30) that explicitly listed the requirement.
- All evidence postings and quotes are in [`.aicg/job-requirements.json`](.aicg/job-requirements.json) under `postings[]` (referenced by ID below).

---

## 3. Market snapshot (last 90 days)

- **Title soup.** Senior postings surface under: Senior AI Infrastructure Engineer, Senior ML Infrastructure Engineer, Senior Staff+ Infrastructure Engineer (Node Infra / Inference Deployment / Compute Infrastructure), Senior ML Platform Engineer, Senior Software Engineer (AI Infrastructure / Compute Infrastructure / Infrastructure / GPU Infrastructure HPC), Member of Technical Staff (AI Infrastructure / ML & Data Infrastructure), Staff Software Engineer (Managed Kubernetes / Foundational Model Serving / ML Platform / AI Platform), Senior Site Reliability Engineer (GPU Infrastructure / DGX Cloud / AI Hardware), Senior Engineering Manager (AI Infrastructure), Senior AI Infrastructure Engineer (LLM/AI Platforms / Virtualisation / Physical Infrastructure / Training Platform / EDA Infrastructure), Senior Core Infrastructure Engineer (AI Infrastructure), AI Senior Lead Infrastructure Engineer, Forward Deployed Engineer (AI Inference — vLLM & Kubernetes). Postings labeled "AI Infrastructure Engineer" without a "Senior" prefix but requiring 5+ years with senior scope were retained.
- **Experience band.** 5–8 years remains the dominant ask. A growing share (Anthropic Sr Staff+ x2, Databricks Staff, NVIDIA Senior-Level 4/5 x3, Lambda Staff, Apple Senior Staff, Adobe Staff, xAI MTS, Perplexity MTS, JPM Senior Lead, Ai2 Senior Engineering Manager, Red Hat FDE) target the band above, retained because they define what a Senior graduates into. Ai2's 8+ years still qualifies as senior-band per the level-30 mapping.
- **Salary band.** USD ~$140k–$500k+ base, with Staff/Principal bands pushing $208k–$356.5k (NVIDIA Level 5), $180k–$440k (xAI MTS), $146,880–$220,320 (Ai2 Sr Eng Mgr), $140k–$215k (CrowdStrike). Middle 50% of postings that list a salary continue to cluster $185k–$280k base; NVIDIA DGX Cloud, Anthropic Staff+, and xAI MTS are pushing the upper end higher this cycle.
- **Stable core stack (>30% of postings) — strengthened:**
  - advanced Kubernetes **0.80** (from 0.72)
  - GPU cluster ops **0.77** (from 0.66)
  - distributed systems design **0.67** (from 0.69)
  - observability/SRE **0.40** (from 0.31)
  - LLM serving frameworks **0.37** (from 0.31; owned lower level)
  - model optimization & serving **0.37** (from 0.28 — crossed threshold)
  - MLOps pipelines **0.33** (from 0.34)
  - multi-cloud + IaC/GitOps **0.33** (from 0.34)
  - systems programming **0.33** (from 0.25; owned lower level)
- **Movement vs. 2026-09 cycle:**
  - `req-k8s-advanced` continued strengthening 0.72 → **0.80** as the sample tilted further toward K8s-platform, GPU-SRE, and Managed-K8s postings (Lambda Managed K8s, NVIDIA DGX Cloud, Mirantis SRE, OpenTeams, Firmus Virtualisation, stack8s vLLM).
  - `req-gpu-cluster-ops` rose 0.66 → **0.77** — Blackwell NVL72 fabric specifics now appear in 4 postings (Perplexity CoreWeave GB200, NVIDIA DGX, Cohere HPC, Lambda) but mod-203 already generalizes across GPU generations.
  - `req-observability-sre` jumped 0.31 → **0.40** on the back of a SRE-heavy sample (Sesterce, NVIDIA DGX Cloud SRE, Mirantis GPU-SRE, Adobe, CrowdStrike, Anduril, Oracle).
  - `req-model-serving-optimization` rose 0.28 → **0.37** — cleanly above threshold now (CrowdStrike, Databricks Foundational Serving, Red Hat vLLM FDE, stack8s vLLM, Adobe, xAI, Tencent, Anthropic Inference Deployment). Still covered by mod-204; runtime-specific detail belongs lower.
  - `req-llm-serving-link` rose 0.31 → **0.37** — fourth consecutive cycle above threshold. CrowdStrike LLM Platforms, Databricks Foundational Model Serving, stack8s vLLM, Red Hat vLLM FDE, Adobe AI Platform all name vLLM or TensorRT-LLM explicitly. Still owned at level 20.
  - `req-systems-programming` rose 0.25 → **0.33** — NVIDIA DGX (Rust & C++), NVIDIA EDA, Anthropic Node Infra, xAI (Go/Rust/C++), Mirantis (Golang/Kubernetes), OpenTeams (Linux/CUDA), Sesterce (Python automation). Owner stays level 20.
  - `req-security-compliance` recovered 0.09 → **0.17** on JPM regulated-financial, Firmus sovereign-cloud, OpenTeams secure T&E, Anduril defense, Mirantis multi-tenant control plane. Still below 0.30 but the signal is clearly broadening (defense + finance + public sector + sovereign cloud).
  - `req-hpc-slurm-link` steady 0.22 → **0.20** (Ai2 Sr SWE + Sr Eng Mgr, Perplexity, Cohere HPC, OpenTeams, NVIDIA EDA). Still below 0.30; owner at level 35 unchanged.
  - `req-nccl-networking` mild uptick 0.13 → **0.17** (Together AI Systems, NVIDIA DGX, Cohere HPC, Lambda — the Blackwell NVL72 cohort). Still below 0.30; owner at level 35 unchanged.
  - `req-distributed-training` slight recovery 0.13 → **0.17** (Scale AI, Gatik, Perplexity, Cohere HPC, Finoit, Apple). Still below 0.30; coverage unchanged.
  - `req-technical-leadership` recovered 0.16 → **0.20** with the Ai2 Senior Engineering Manager posting and the Staff+ roles (Lambda, Apple, Databricks, Anthropic, JPM).
  - `req-agentic-workflows` fell further 0.06 → **0.03** (only Gatik AI this cycle) — below the ≥3-posting bar again. Owned at peer level-30 ML Platform.
- **New shape signals that appeared but did NOT cross both bars (added to watchlist / promoted or kept):**
  - **Blackwell NVL72 fabric specifics** — Perplexity CoreWeave GB200 NVL72, NVIDIA DGX, Cohere HPC, Lambda. 4 postings clear the ≥3-posting bar but 0.13 is below the 0.30 frequency bar. mod-203 already generalizes.
  - **Confidential / private inference / sovereign AI** — JPM (regulated-financial), Firmus Virtualisation (sovereign-cloud multi-tenant), OpenTeams (secure T&E, public sector). 3 postings — crosses the ≥3 bar for the first time but at 0.10 well below 0.30. mod-209 covers this at the depth senior expects.
  - **Custom accelerator fleets (TPU / Trainium / Inferentia)** — Anthropic Node Infra (GPUs/TPUs/Trainium), Cohere HPC (GPU/TPU superclusters). 2 postings, below the ≥3 bar.
  - **Kueue / Volcano batch scheduling** — Lambda Managed K8s. 1 posting (down from 2 last cycle). Below the ≥3 bar.
  - **MoE serving internals (KV cache / prefill-decode / continuous batching)** — Red Hat vLLM FDE, stack8s vLLM. 2 postings; serving-runtime-specific and belongs at level 20 mod-110 / peer level-30 ML Platform.

---

## 4. Requirements by category

### 4.1 Owned at level 30 in this repo ✅ (covered)

| ID | Requirement | Freq. (90d) | Coverage | Evidence |
|----|-------------|------------:|----------|----------|
| req-k8s-advanced | **Advanced Kubernetes** (operators/CRDs, admission controllers, multi-cluster, GPU scheduling, service mesh, Kueue/Ray) | 0.80 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/) | p01, p02, p03, p04, p05, p07, p08, p09, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p27, p28, p29, p30 |
| req-gpu-cluster-ops | **GPU cluster ops** (NVIDIA GPU Operator, MIG, CUDA drivers, H100/H200/B200/Blackwell GB200/GB300, NVLink/NVSwitch, profiling, cost, bare-metal ops) | 0.77 | [`lessons/mod-203-gpu-computing/`](lessons/mod-203-gpu-computing/) | p01, p02, p03, p04, p05, p06, p09, p10, p11, p12, p13, p14, p17, p18, p19, p20, p21, p22, p23, p24, p25, p27, p28, p29, p30 |
| req-distributed-systems | **Large-scale distributed systems design** (capacity, HA, cross-region, debugging at 1000+ GPUs) | 0.67 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p01, p02, p03, p05, p06, p08, p10, p13, p14, p15, p17, p18, p19, p20, p22, p26, p29 |
| req-observability-sre | **Observability & SRE** (Prometheus, Grafana, OpenTelemetry, distributed tracing, SLI/SLO, incident response, chaos) | 0.40 | [`lessons/mod-207-observability-sre/`](lessons/mod-207-observability-sre/) | p07, p08, p12, p14, p15, p27, p28, p29, p30 |
| req-model-serving-optimization | **Model optimization & serving** (TensorRT, ONNX, quantization, dynamic batching, Triton) | 0.37 | [`lessons/mod-204-model-optimization/`](lessons/mod-204-model-optimization/), [`projects/project-202-model-serving/`](projects/project-202-model-serving/) | p07, p08, p10, p11, p12, p13, p23, p27 |
| req-mlops-pipelines | **MLOps pipelines** (Kubeflow, Airflow, Argo Workflows, MLflow, feature stores, model registry, CI/CD for ML) | 0.33 | [`lessons/mod-206-advanced-mlops/`](lessons/mod-206-advanced-mlops/) | p03, p04, p07, p10, p12, p16, p24, p26, p27 |
| req-multi-cloud-iac | **Multi-cloud + IaC/GitOps** (AWS/GCP/Azure, Terraform, Pulumi, Ansible, Helm, ArgoCD/Flux) | 0.33 | [`lessons/mod-205-multi-cloud/`](lessons/mod-205-multi-cloud/), [`lessons/mod-208-iac-gitops/`](lessons/mod-208-iac-gitops/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p01, p02, p04, p06, p13, p15, p16, p17, p19, p21, p28, p29 |
| req-technical-leadership | **Technical leadership** (RFCs, code reviews, mentoring, cross-team initiatives, technology evaluation) | 0.20 | [`lessons/mod-210-technical-leadership/`](lessons/mod-210-technical-leadership/) | p06, p08, p16, p20, p22, p26 |
| req-distributed-training | **Distributed training** (PyTorch DDP/FSDP, DeepSpeed, Ray Train, Megatron-LM, JAX, checkpointing) | 0.17 | [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-201-distributed-training/`](projects/project-201-distributed-training/) | p03, p04, p09, p21, p24, p26 |
| req-security-compliance | **Security & compliance** (multi-tenant RBAC, secrets management, network policies, GDPR/SOC2/ISO-27001, secure sandboxes) | 0.17 | [`lessons/mod-209-security-compliance/`](lessons/mod-209-security-compliance/) | p14, p16, p19, p25, p30 |

Every level-30-owned requirement above is already covered by an existing module or project. No net-new module or exercise is proposed on the basis of any of these — including the ones that first cross the 0.30 threshold this cycle (`req-model-serving-optimization` 0.37, `req-observability-sre` 0.40), because they are already covered. The ones below 0.30 (`req-technical-leadership`, `req-distributed-training`, `req-security-compliance`) remain fully covered — their frequencies reflect sampling variation on a GPU-neocloud / inference-platform / SRE-heavy sample, not falling relevance.

### 4.2 Owned at level 20 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-systems-programming | **Python + one systems language** (Go / Rust / C++) for infra tooling; Linux internals | 0.33 | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning — Modules 01, 04, 07](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) — this senior curriculum builds on it directly in [`project-204-k8s-operator/`](projects/project-204-k8s-operator/) (Go with operator-sdk). Rose 0.25 → 0.33 this cycle as more explicit Rust/Go/C++ callouts appeared (NVIDIA DGX, NVIDIA EDA, Anthropic Node Infra, xAI, Mirantis, OpenTeams, Sesterce). |
| req-llm-serving-link | **LLM serving frameworks** (vLLM, SGLang, TensorRT-LLM, TGI, Triton, Ray Serve, KServe, BentoML) | 0.37 | `ai-infra-engineer-learning` (20) primary; `ai-infra-ml-platform-learning` (30 peer) for platform-level | [ai-infra-engineer-learning Module 10 — LLM Infrastructure](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure); peer platform coverage: [ai-infra-ml-platform-learning JOB_REQUIREMENTS.md — req-llm-serving-platform](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning/blob/main/JOB_REQUIREMENTS.md). |

**Why we still do NOT propose adding a Senior-track LLM-serving module (unchanged from 2026-07, -08, and -09):** the frequency threshold is cleared for the fourth consecutive cycle (0.37 ≥ 0.30, 11 postings ≥ 3), but the Ownership Rule places it at **level 20** — `mod-110-llm-infrastructure` already teaches vLLM, RAG, quantization, TGI, LangChain, LoRA. The senior curriculum's `mod-204-model-optimization` already carries the transferable optimization skill (TensorRT layer fusion, ONNX Runtime execution providers, quantization, dynamic batching) that generalizes to any serving runtime. This cycle's runtime-specific detail from Red Hat (KV caching, prefill/decode separation, continuous batching) and stack8s (vLLM-GPU-K8s focus) reinforces the case for keeping runtime specifics out of level 30 — pulling them in would anchor 2026-Q4 phrasing on a curriculum that lives multiple years. Adding a duplicate would violate the Ownership Rule; extending `mod-204` further would push toward the peer level-30 ML Platform sibling's declared surface. If the market pushes even harder, the right home is `ai-infra-ml-platform-learning`, not this repo.

### 4.3 Owned at level 30 (peer) — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-agentic-workflows | **Agentic workflows in infra tooling** (LangGraph, AutoGen, CrewAI, MCP, sandboxed code execution) | 0.03 | `ai-infra-ml-platform-learning` (30 peer) | [ai-infra-ml-platform-learning](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning) — the ML Platform peer owns agentic frameworks as a platform surface (LLM gateway, eval harness, sandboxing). Fell to 1/30 (Gatik AI only). Watchlist. |

### 4.4 Owned at level 35 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-hpc-slurm-link | **Slurm / HPC schedulers** (Slurm/LSF/PBS, MPI, Enroot/Singularity, Charliecloud) | 0.20 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). Stable 0.22 → 0.20 (Ai2, Perplexity, Cohere HPC, OpenTeams, NVIDIA EDA, Ai2 Sr Eng Mgr). Still below 0.30. Senior postings that require Slurm always pair it with Kubernetes — that intersection is already exercised by [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/) + [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/). A standalone Slurm module would duplicate the level-35 owner. |
| req-nccl-networking | **High-performance networking depth** (NCCL, RDMA, InfiniBand, RoCE, EFA, topology-aware scheduling) | 0.17 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) — Performance track owns the tuning depth. Mild uptick 0.13 → 0.17 (Together AI Systems, NVIDIA DGX, Cohere HPC, Lambda — the Blackwell NVL72 fabric cohort). The senior curriculum introduces NCCL in [`mod-202-distributed-training/`](lessons/mod-202-distributed-training/) and [`mod-203-gpu-computing/`](lessons/mod-203-gpu-computing/), and touches CNI (Cilium) in [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), which matches the level of *reasoning about* the fabric expected at senior. Optimization depth stays with Performance. |
| req-cuda-kernel-link | **Custom CUDA / Triton kernel authoring** (CUTLASS, Tensor Cores, Nsight profiling) | 0.00 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). Zero explicit kernel-authoring mentions at senior level this cycle. The NVIDIA Senior Inference Engineer, GPU Kernel Optimization posting (observed but excluded from the senior sample) is explicitly a Performance-Engineer-level role, confirming the Ownership Rule. |

For each item above, the senior curriculum already provides the awareness / reasoning layer (e.g., "why NCCL topology matters for FSDP throughput", "when to reach for Slurm vs. KubeRay", "when to hand off to a Performance Engineer") that a senior needs to make architecture decisions and hand off tuning depth to a Performance Engineer.

### 4.5 Watchlist (sub-threshold this cycle — not tracked as requirements yet)

| Signal | Postings | Notes |
|--------|---------:|-------|
| **Blackwell GB200/GB300 NVL72/NVL36 fabric specifics** | 4/30 (p09, p17, p21, p22) | Clears the ≥3-posting bar for the first time but 0.13 is below the 0.30 bar. [`mod-203`](lessons/mod-203-gpu-computing/) already generalizes across GPU generations — the Blackwell NVL72 topology story is a specialization of concepts already taught. External NVIDIA Quantum-X800 / NVL72 reference material already linked in §6. |
| **Confidential / sovereign AI** (TEE, Nitro Enclaves, EU AI Act, private inference, tenant isolation for regulated workloads) | 3/30 (p16 JPM, p19 Firmus, p25 OpenTeams) | **First cycle to clear the ≥3-posting bar.** At 0.10 still well below the 0.30 frequency bar. mod-209 already covers sovereign data residency + multi-tenant isolation at the depth senior expects. If next cycle crosses 0.30, propose an exercise inside mod-209 before a new module. |
| **Custom accelerator fleets** (TPU / Trainium / Inferentia / AMD MI300X) | 2/30 (p06 Anthropic Node Infra names GPUs/TPUs/Trainium; p21 Cohere HPC names GPU/TPU superclusters) | [`mod-203`](lessons/mod-203-gpu-computing/) already teaches heterogeneous device abstractions; external Neuron / TPU / ROCm docs linked in §6. |
| **MoE / KV-cache / prefill-decode / continuous batching** (LLM serving internals) | 2/30 (p11 Red Hat vLLM FDE, p23 stack8s vLLM) | Serving-runtime-specific detail; belongs at level 20 mod-110 / peer level-30 ML Platform, not senior. |
| **Kueue / Volcano batch scheduling** on Kubernetes | 1/30 (p22 Lambda) | Dropped from 2/32 last cycle. If it clears both bars in future, the right lever is a small exercise inside [`mod-201`](lessons/mod-201-advanced-kubernetes/) (which already introduces batch/GPU scheduling), not a new module. |

---

## 5. Curriculum-plan delta this cycle — zero additions

See [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json). Every one of `modules`, `exercises`, and `projects` is intentionally an empty array — the **fourth consecutive** cycle with this verdict.

**Rationale in one paragraph** (also in the delta JSON):

Across 30 senior-band postings from the last 90 days (2026-07-05 → 2026-10-03), no requirement clears the ≥ 0.30 frequency + ≥ 3-posting bar AND is owned at level 30 AND is not already covered by an existing senior module. Six requirements cleared both bars at level 30 this cycle (k8s-advanced 0.80, distributed-systems 0.67, gpu-cluster-ops 0.77, mlops-pipelines 0.33, multi-cloud-iac 0.33, observability-sre 0.40, model-serving-optimization 0.37) — every one is covered by an existing senior module/project (mod-201 through mod-210, project-201 through project-204). Two threshold-clearing items belong at lower levels (req-llm-serving-link 0.37 and req-systems-programming 0.33) and are already linked to their owners (level 20 ai-infra-engineer-learning mod-110 LLM Infrastructure and Modules 01/04/07; peer level 30 ai-infra-ml-platform-learning for the platform-level LLM-serving surface). The 2026-10 sample tilts toward GPU-neocloud and inference-platform postings (NVIDIA DGX, Cohere HPC, Lambda Managed K8s, Adobe AI Platform, CrowdStrike LLM Platforms, Perplexity CoreWeave GB200, Red Hat vLLM FDE, stack8s vLLM) which explains the uptick in gpu-cluster-ops, observability-sre, model-serving-optimization, and llm-serving-link. Five watchlist signals surfaced or persisted (blackwell-nvl72 4 postings, confidential-ai 3, custom-accelerator 2, moe-serving 2, kueue-batch 1); only watch-confidential-ai crossed the ≥3-posting bar for the first time (JPM regulated-financial, Firmus sovereign-cloud, OpenTeams secure T&E) but at 0.10 is well below 0.30 — the correct lever if next cycle crosses 0.30 is an exercise inside mod-209, not a new module. Continuity bias — the correct default per the packet spec and the verdict of the prior three consecutive cycles — applies again this cycle.

### 5.1 Candidate additions we considered and rejected (this cycle)

| Tempting addition | Why we rejected it |
|-------------------|--------------------|
| New `mod-211-llm-serving-platforms` (vLLM/SGLang/Triton) | Same reason as 2026-07, -08, and -09: owned at level 20 in [`mod-110-llm-infrastructure`](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure) and as the flagship level-30 peer gap in `ai-infra-ml-platform-learning`. Senior-track already teaches the *transferable* optimization skill in [`mod-204-model-optimization/`](lessons/mod-204-model-optimization/). Fourth consecutive cycle rejecting this. |
| New exercise "Deploy vLLM behind Triton with KV cache offload" in mod-204 | Would violate the Ownership Rule — every serving-framework-specific exercise anchors runtime versions (2026-Q4 vLLM's KV-cache semantics change with every minor release) and belongs at level 20 / peer level 30. |
| New `mod-212-observability-llm-workloads` (OTel semantic conventions for GenAI, token-rate SLOs) | req-observability-sre at 0.40 is already covered by [`mod-207-observability-sre/`](lessons/mod-207-observability-sre/). The jump is a sampling effect (SRE-heavy cycle), not a coverage gap. Pulling in GenAI semantic conventions would anchor 2026-Q4 OTel spec phrasing; link externally in §6 instead. |
| New `mod-213-sovereign-ai-and-confidential-inference` (TEE / EU AI Act / Nitro Enclaves) | watch-confidential-ai crosses the ≥3-posting bar for the first time (3/30 JPM, Firmus, OpenTeams) but 0.10 is well below 0.30. mod-209 already covers sovereign data residency and multi-tenant isolation at the depth senior expects. If next cycle crosses 0.30, propose a mod-209 exercise before a new module. |
| New exercise on Blackwell (GB200 NVL72 / GB300 NVL36) fabric specifics | 4 postings this cycle (Perplexity CoreWeave GB200, NVIDIA DGX, Cohere HPC, Lambda) but mod-203 already generalizes across GPU generations — the Blackwell topology story is a specialization of concepts already taught. Adding version-specific bullets would anchor 2026-Q4 hardware phrasing on a curriculum that lives multiple years. |
| New exercise on custom-accelerator fleets (Trainium/TPU/Inferentia) in mod-203 | 2/30 postings this cycle (Anthropic Node Infra, Cohere HPC). Below both bars. mod-203 already teaches heterogeneous device abstractions; a link in resources is sufficient. |
| New `mod-214-agentic-workflows-in-infra-tooling` | Fell to 1/30 (Gatik AI only) this cycle. Well below both bars. Owned at peer level-30 ML Platform. |
| New exercise on prefix caching / speculative decoding / KV-cache offload | Serving-runtime-specific detail (Red Hat vLLM, stack8s vLLM postings). Anchors 2026-Q4 phrasing and belongs at level 20 mod-110 / peer level-30 ML Platform. |
| New `mod-215-kueue-batch-scheduling` | Dropped from 2 to 1 posting this cycle (Lambda only). Well below the ≥3-posting bar. mod-201 already introduces batch/GPU scheduling. |

---

## 6. External resources for out-of-scope items

For learners who want to extend beyond the level-30 senior scope during or after this track:

- **LLM serving depth** — [vLLM docs](https://docs.vllm.ai/), [NVIDIA Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/), [SGLang GitHub](https://github.com/sgl-project/sglang), [TensorRT-LLM repo](https://github.com/NVIDIA/TensorRT-LLM), [KServe docs](https://kserve.github.io/website/), [BentoML docs](https://docs.bentoml.com/).
- **LLM serving internals** (KV cache, prefill/decode disaggregation, continuous batching, speculative decoding) — [vLLM design docs](https://docs.vllm.ai/en/latest/design/arch_overview.html), Anyscale Ray Serve LLM patterns, [NVIDIA Dynamo](https://github.com/ai-dynamo/dynamo).
- **Slurm & HPC** — SchedMD Slurm docs; [NVIDIA DGX SuperPOD reference architectures](https://docs.nvidia.com/dgx-superpod/); [NCCL user guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/).
- **Batch scheduling on Kubernetes** — [Kueue docs](https://kueue.sigs.k8s.io/), [Ray KubeRay operator](https://ray-project.github.io/kuberay/), Volcano.
- **CUDA kernel authoring** — [NVIDIA CUTLASS](https://github.com/NVIDIA/cutlass), [Triton language docs](https://triton-lang.org/), Nsight Compute training.
- **RDMA / InfiniBand / Blackwell fabrics** — Mellanox / NVIDIA InfiniBand admin guides; NCCL tuning knobs (`NCCL_IB_HCA`, `NCCL_NET_GDR_LEVEL`); [NVIDIA Quantum-X800 InfiniBand overview](https://www.nvidia.com/en-us/networking/quantum-x800/); [NVIDIA GB200 NVL72 reference](https://www.nvidia.com/en-us/data-center/gb200-nvl72/).
- **LLM-workload SRE / observability** — Anthropic's AI reliability engineering posts; SRE Book chapters on capacity planning; [OpenTelemetry semantic conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- **Agentic workflows in infra tooling** — LangGraph tutorials, AutoGen docs, CrewAI docs, [Model Context Protocol (MCP) spec](https://modelcontextprotocol.io/).
- **Custom accelerators** — [AWS Neuron SDK (Trainium/Inferentia)](https://awsdocs-neuron.readthedocs-hosted.com/), [Google Cloud TPU docs](https://cloud.google.com/tpu/docs), [AMD ROCm docs](https://rocm.docs.amd.com/).
- **Confidential AI / TEE / sovereign cloud** — [NVIDIA H100 Confidential Computing](https://docs.nvidia.com/confidential-computing/), [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html), [Azure Confidential Computing](https://learn.microsoft.com/en-us/azure/confidential-computing/), EU AI Act reference material.

These are reference-only and intentionally not pulled into the level-30 senior curriculum this cycle.

---

## 7. Methodology

- **Sources.** Greenhouse (`job-boards.greenhouse.io`, `job-boards.eu.greenhouse.io`, `boards.greenhouse.io`), Workday (`crowdstrike.wd5.myworkdayjobs.com`, `nvidia.wd5.myworkdayjobs.com`), Ashby (`jobs.ashbyhq.com`), Lever (`jobs.lever.co`), company career portals (Together AI, Scale AI, NVIDIA, Anthropic, Perplexity, Databricks, xAI, Oracle, JPMorgan, Tencent, Anduril, Firmus, CrowdStrike, Ai2, Lambda, Red Hat, Cohere, Apple, Adobe, Mirantis, Sesterce, stack8s, Finoit, OpenTeams, Gatik AI), Built In (`builtin.com` / `builtinsf.com` / `builtinnyc.com`), General Catalyst / Menlo Ventures / Simplify / Zapply / Dreamwork / Freehire portfolio/aggregator boards.
- **Date window.** 2026-07-05 → 2026-10-03 (last 90 days). 30 postings — all within the window; no border-line older postings were retained this cycle.
- **Frequency denominator.** 30. Where a full posting body was not retrievable (Ashby / Lever pages that render via JS, or Workday postings cached by secondary aggregators), the requirement quote was recovered via secondary WebSearch snippets or the record contributed to postings-analyzed only. Frequencies count postings that explicitly listed the requirement.
- **Continuity bias.** Applied per packet spec: default to no change, propose additions only when ≥ 3 distinct postings from the last 90 days show a gap, requirement frequency ≥ 0.30, and no existing module can be incrementally extended. In addition, the Ownership Rule was applied — even threshold-clearing items that belong at another level are linked, not duplicated.
- **Comparison to prior cycles.** The 2026-07 cycle analyzed 22 postings and concluded zero additions; the 2026-08 cycle analyzed 28 postings and concluded zero additions; the 2026-09 cycle analyzed 32 postings and concluded zero additions. This cycle's 30-posting sample continues that trajectory. Movements this cycle (K8s 0.72→0.80, GPU ops 0.66→0.77, observability-sre 0.31→0.40, model-serving-opt 0.28→0.37 crossing threshold, llm-serving-link 0.31→0.37, systems-programming 0.25→0.33, security-compliance 0.09→0.17, distributed-systems 0.69→0.67, mlops 0.34→0.33, multi-cloud-iac 0.34→0.33, distributed-training 0.13→0.17, technical-leadership 0.16→0.20, hpc-slurm 0.22→0.20, nccl 0.13→0.17, agentic-workflows 0.06→0.03) are dominated by a GPU-neocloud / inference-platform / SRE sample tilt plus a modest genuine strengthening of the core K8s / GPU-cluster-ops / model-serving-optimization core. Core ownership assignments and coverage decisions are unchanged.
- **Verdict.** Zero additions. The 10-module + 4-project curriculum continues to match the current market cleanly.

---

**Maintained by VeriSwarm.ai**
