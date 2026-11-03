# Senior AI Infrastructure Engineer — Job Requirements Report

**Role:** Senior AI Infrastructure Engineer (level 30)
**Repository:** `ai-infra-senior-engineer-learning`
**Research window:** 2026-08-05 → 2026-11-03 (last 90 days)
**Postings analyzed:** 37 (25 carried forward from 2026-10 cycle; 12 added from 2026-10-04 → 2026-11-03; 5 aged out of window)
**Content model:** anthropic/claude-opus-4-7
**Machine-readable source:** [`.aicg/job-requirements.json`](.aicg/job-requirements.json)
**Curriculum-plan delta this cycle:** [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json) — **zero additions** (fifth consecutive cycle)

---

## 1. Headline

The 2026-Q4 market for Senior AI Infrastructure Engineers continues to match the existing 10-module + 4-project curriculum cleanly. Across 37 postings from the last 90 days — a sample that now mixes the GPU-platform / inference-platform / SRE cohort from the 2026-10 cycle with twelve fresh observations covering AI-gateway, FinOps, and serving-runtime-internals roles — the core level-30 stack remains above threshold across the board: advanced Kubernetes **0.76**, GPU cluster ops **0.65**, distributed systems **0.59**, multi-cloud + IaC/GitOps **0.38**, observability/SRE **0.38**, LLM serving platforms **0.35** (fifth consecutive cycle above 0.30, owned at level 20), MLOps pipelines **0.30**. `req-model-serving-optimization` fell back under the threshold (0.37 → 0.27) as the sample broadened; it remains covered at level 30 by `mod-204 + project-202`. Every requirement that clears both continuity-bias bars (≥ 3 postings AND ≥ 0.30 frequency) *after applying the Ownership Rule* is already owned at level 30 by an existing senior module.

Two **NEW watchlist signals** emerged this cycle — `watch-ai-gateway` (Cloudflare AI Gateway + SentinelOne/Kong AI Gateway, 2 postings) and `watch-finops-cost` (Charles Schwab + Cargill, 2 postings). Both are platform-engineering patterns worth watching; neither crosses the ≥3-posting bar. `watch-moe-serving` crossed the ≥3-posting bar for the first time (stack8s vLLM, Red Hat llm-d, Uniphore inference) but at 0.08 remains well below 0.30 and belongs at level 20 / peer level-30 regardless.

The curriculum-plan delta is intentionally empty — see §5. This is the **fifth consecutive** cycle to reach a zero-addition verdict; prior cycles 2026-07, -08, -09, -10 reached the same conclusion with 22, 28, 32, and 30 postings respectively.

---

## 2. How to read this document

- Each requirement is grouped by category, lists the **owner role** (per the curriculum hierarchy), and points to where it is covered in this repo *or* in a lower/peer/higher-level repo.
- Ownership follows the lowest-level rule: a requirement is owned by the lowest level where it is genuinely required, and higher-level roles only re-own it when they need extra depth, architecture context, or leadership context.
- Frequencies are the fraction of postings from the last 90 days (out of 37) that explicitly listed the requirement.
- All evidence postings and quotes are in [`.aicg/job-requirements.json`](.aicg/job-requirements.json) under `postings[]` (referenced by ID below).

---

## 3. Market snapshot (last 90 days)

- **Title soup.** The 2026-10 cycle's title cloud (Senior AI Infrastructure Engineer / Senior ML Infrastructure Engineer / Senior Staff+ Infrastructure Engineer / Member of Technical Staff / Staff SWE Managed-K8s / Staff SWE Foundational-Model-Serving / Senior SRE DGX Cloud / Senior Engineering Manager / Forward Deployed Engineer vLLM) is now joined by **four fresh archetypes**: Senior Systems Engineer AI Gateway (Cloudflare), Senior AI Platform Engineer Infrastructure Services (SentinelOne — Kong AI Gateway scope), AI FinOps Development Engineer (Schwab), AI Platform FinOps Senior Engineer (Cargill), Senior Inference Engineer (Uniphore — speculative-decoding/chunked-prefill scope), Principal AI/ML Infra SWE GPU Clusters (NVIDIA), Senior Cloud Infrastructure & Network Operations SA (NVIDIA — NMX-C/NMX-M on GB200/GB300 NVL72), ML Engineer Distributed vLLM / llm-d (Red Hat), Senior Staff SWE AI Runtime (Databricks).
- **Experience band.** 5–8 years remains the dominant ask. The Staff+/Principal band continues to broaden: NVIDIA Principal AI/ML Infra GPU Clusters (15+ years), Databricks Senior Staff AI Runtime (15+ years), Apple Senior Staff ML Platform, Adobe Staff ML Platform, Anthropic Staff+ Node Infra, Lambda Staff Managed-K8s. All retained as they define what a Senior graduates into.
- **Salary band.** USD ~$140k–$500k+ base. Representative salary bands this cycle: NVIDIA Senior Level 4/5 $168K–$356.5K, xAI MTS $180K–$440K, Uniphore Senior Inference $200K–$350K, Ai2 Senior Eng Manager $146,880–$220,320, CrowdStrike $140K–$215K, Firmus SGD 140K–220K.
- **Stable core stack (≥ 30% of postings this cycle):**
  - advanced Kubernetes **0.76** (from 0.80)
  - GPU cluster ops **0.65** (from 0.77)
  - distributed systems design **0.59** (from 0.67)
  - multi-cloud + IaC/GitOps **0.38** (from 0.33)
  - observability/SRE **0.38** (from 0.40)
  - LLM serving frameworks **0.35** (from 0.37; owned at lower level)
  - MLOps pipelines **0.30** (from 0.33)
- **Fell below 0.30 this cycle:**
  - model optimization & serving **0.27** (from 0.37) — sample broadened; still covered at level 30 by mod-204
  - systems programming **0.16** (from 0.33) — three systems-programming-explicit postings aged out
- **Movement vs. 2026-10 cycle:**
  - `req-k8s-advanced` 0.80 → **0.76** as the sample broadened to include AI-gateway (Cloudflare, SentinelOne), FinOps (Schwab, Cargill), and runtime-internals (Uniphore) roles where K8s is implicit but not always surfaced in retrievable snippet text. Still dominant.
  - `req-gpu-cluster-ops` 0.77 → **0.65** on the same broadening. Blackwell NVL72 fabric specifics now explicit at operator level (p32 NVIDIA Cloud Infra Network Ops: NMX-C/NMX-M partition management, Spectrum-X Ethernet).
  - `req-distributed-systems` 0.67 → **0.59**. Sampling variation.
  - `req-model-serving-optimization` 0.37 → **0.27** falls back below threshold. Not a loss of relevance — the specific vocabulary consolidates into runtime-specific postings (Red Hat llm-d, Uniphore, Fireworks) that live at level 20 / peer level-30 by Ownership Rule.
  - `req-llm-serving-link` 0.37 → **0.35** — fifth consecutive cycle above threshold. Red Hat llm-d (distributed vLLM + Gateway Inference Extension API), Fireworks, Cloudflare AI Gateway, SentinelOne Kong AI Gateway, Uniphore (speculative decoding / chunked prefill / MoE), Cohere Agent Infra, Perplexity GPU Cluster. Owned at level 20 unchanged.
  - `req-observability-sre` 0.40 → **0.38** — stable above threshold. FinOps postings (Schwab, Cargill) reinforce observability as the entry surface for cost attribution.
  - `req-multi-cloud-iac` 0.33 → **0.38** — Cloudflare AI Gateway (edge network) and FinOps postings (multi-cloud cost reach) push this up.
  - `req-mlops-pipelines` 0.33 → **0.30** — at the line. Still covered.
  - `req-systems-programming` 0.33 → **0.16** — three explicit postings (Together AI Systems, Ai2 Sr SWE, OpenTeams) aged out. The underlying skill demand is unchanged (NVIDIA, Databricks, Anthropic, Mirantis all require systems languages); the drop is a snippet-retrieval artifact.
  - `req-security-compliance` 0.17 → **0.14** as OpenTeams aged out. SentinelOne adds an AI-gateway flavor (auth / rate-limit / monitor) of multi-tenant isolation. Still covered.
  - `req-hpc-slurm-link` 0.20 → **0.11** as Ai2 Sr SWE, Perplexity, OpenTeams aged out. Only NVIDIA Principal GPU Clusters names HPC among new observations.
  - `req-nccl-networking` 0.17 → **0.11** but with sharpened operator-level depth in NVIDIA Cloud Infra Network Ops (NMX-C/NMX-M, Spectrum-X).
  - `req-distributed-training` 0.17 → **0.22** — Perplexity GPU Cluster, Databricks AI Runtime, Uniphore.
  - `req-technical-leadership` 0.20 → **0.22** — NVIDIA Principal, Databricks Senior Staff.
  - `req-cuda-kernel-link` 0.00 → **0.05** — first non-zero cycle. Databricks AI Runtime and Uniphore inference touch kernel-adjacent work (multi-GPU parallel execution, checkpointing performance). Still well below both bars; owned at level 35.
  - `req-agentic-workflows` 0.03 → **0.05** — Cohere Agent Infrastructure joins Gatik AI.
- **NEW shape signals this cycle (added to watchlist, not promoted):**
  - **AI Gateway as a discrete platform layer** — Cloudflare AI Gateway (p36) + SentinelOne / Kong AI Gateway (p37). Red Hat llm-d (p33) names the Gateway Inference Extension API in the same posting as distributed vLLM. 2–3 citations depending on whether you count the llm-d reference as a third; conservatively 2/37 = **0.05**. **NEW watchlist entry** `watch-ai-gateway`.
  - **AI FinOps / token economics / unit-cost platforms** — Charles Schwab AI FinOps Dev Engineer (p38) + Cargill AI Platform FinOps Sr Engineer (p39, APAC). Distinct from generic observability-sre: emphasizes unit cost models, token economics, chargeback. 2/37 = **0.05**. **NEW watchlist entry** `watch-finops-cost`.
- **Watchlist signals that persisted or shifted:**
  - **MoE / KV cache / prefill-decode / continuous batching / speculative decoding / chunked prefill** — stack8s (p23), Red Hat llm-d (p33), Uniphore (p41). **3 postings — first cycle to clear the ≥3-posting bar.** 3/37 = 0.08 still well below 0.30; serving-runtime-specific and belongs at level 20 / peer level-30 regardless.
  - **Blackwell GB200/GB300 NVL72 fabric specifics** — NVIDIA DGX (p17), Cohere HPC (p21), Lambda (p22), NVIDIA Cloud Infra Network Ops (p32). 4/37 = 0.11, operator depth sharper this cycle via NMX-C/NMX-M + Spectrum-X mentions in p32. mod-203 already generalizes.
  - **Confidential / sovereign AI** — regressed to 2 postings (JPM p16, Firmus p19) as OpenTeams aged out.
  - **Custom accelerator fleets** — 2 postings (Anthropic Node Infra p06 names GPUs/TPUs/Trainium explicitly; Cohere HPC p21 names GPU/TPU superclusters).
  - **Kueue / Volcano batch scheduling** — 1 posting (Lambda p22).

---

## 4. Requirements by category

### 4.1 Owned at level 30 in this repo ✅ (covered)

| ID | Requirement | Freq. (90d) | Coverage | Evidence |
|----|-------------|------------:|----------|----------|
| req-k8s-advanced | **Advanced Kubernetes** (operators/CRDs, admission controllers, multi-cluster, GPU scheduling, service mesh, Kueue/Ray) | 0.76 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/) | p01, p03, p04, p07, p08, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p26, p27, p28, p29, p30, p31, p33, p34, p37, p42 |
| req-gpu-cluster-ops | **GPU cluster ops** (NVIDIA GPU Operator, MIG, CUDA drivers, H100/H200/B200/Blackwell GB200/GB300, NVLink/NVSwitch, profiling, cost, bare-metal ops) | 0.65 | [`lessons/mod-203-gpu-computing/`](lessons/mod-203-gpu-computing/) | p01, p03, p04, p06, p10, p12, p13, p14, p17, p18, p19, p20, p21, p22, p23, p24, p27, p28, p29, p30, p31, p32, p34, p40 |
| req-distributed-systems | **Large-scale distributed systems design** (capacity, HA, cross-region, debugging at 1000+ GPUs) | 0.59 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p01, p03, p06, p08, p10, p13, p14, p15, p17, p18, p19, p20, p22, p26, p29, p31, p32, p33, p35, p36, p40, p42 |
| req-multi-cloud-iac | **Multi-cloud + IaC/GitOps** (AWS/GCP/Azure, Terraform, Pulumi, Ansible, Helm, ArgoCD/Flux) | 0.38 | [`lessons/mod-205-multi-cloud/`](lessons/mod-205-multi-cloud/), [`lessons/mod-208-iac-gitops/`](lessons/mod-208-iac-gitops/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p01, p04, p06, p13, p15, p16, p17, p19, p21, p28, p29, p36, p38, p39 |
| req-observability-sre | **Observability & SRE** (Prometheus, Grafana, OpenTelemetry, distributed tracing, SLI/SLO, incident response, chaos) | 0.38 | [`lessons/mod-207-observability-sre/`](lessons/mod-207-observability-sre/) | p07, p08, p12, p14, p15, p27, p28, p29, p30, p32, p36, p37, p38, p39 |
| req-mlops-pipelines | **MLOps pipelines** (Kubeflow, Airflow, Argo Workflows, MLflow, feature stores, model registry, CI/CD for ML) | 0.30 | [`lessons/mod-206-advanced-mlops/`](lessons/mod-206-advanced-mlops/) | p03, p04, p07, p10, p12, p16, p24, p26, p27, p38, p39 |
| req-model-serving-optimization | **Model optimization & serving** (TensorRT, ONNX, quantization, dynamic batching, Triton) | 0.27 | [`lessons/mod-204-model-optimization/`](lessons/mod-204-model-optimization/), [`projects/project-202-model-serving/`](projects/project-202-model-serving/) | p07, p08, p10, p12, p13, p23, p27, p33, p35, p41 |
| req-technical-leadership | **Technical leadership** (RFCs, code reviews, mentoring, cross-team initiatives, technology evaluation) | 0.22 | [`lessons/mod-210-technical-leadership/`](lessons/mod-210-technical-leadership/) | p06, p08, p16, p20, p22, p26, p31, p40 |
| req-distributed-training | **Distributed training** (PyTorch DDP/FSDP, DeepSpeed, Ray Train, Megatron-LM, JAX, checkpointing) | 0.22 | [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-201-distributed-training/`](projects/project-201-distributed-training/) | p03, p04, p21, p24, p26, p34, p40, p41 |
| req-security-compliance | **Security & compliance** (multi-tenant RBAC, secrets management, network policies, GDPR/SOC2/ISO-27001, secure sandboxes) | 0.14 | [`lessons/mod-209-security-compliance/`](lessons/mod-209-security-compliance/) | p14, p16, p19, p30, p37 |

Every level-30-owned requirement above is already covered by an existing module or project. No net-new module or exercise is proposed on the basis of any of these — including the ones that first cross the 0.30 threshold this cycle (`req-multi-cloud-iac` **0.38**, `req-mlops-pipelines` **0.30**), because they are already covered. `req-model-serving-optimization` **0.27** fell back below threshold on sampling (runtime-specific detail consolidated into Ownership-Rule-lower-level postings); it remains covered. `req-technical-leadership`, `req-distributed-training`, `req-security-compliance` remain fully covered — their frequencies reflect sampling variation on a broader-than-prior-cycle sample, not falling relevance.

### 4.2 Owned at level 20 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-llm-serving-link | **LLM serving frameworks** (vLLM, SGLang, TensorRT-LLM, TGI, Triton, Ray Serve, KServe, BentoML) | 0.35 | `ai-infra-engineer-learning` (20) primary; `ai-infra-ml-platform-learning` (30 peer) for platform-level | [ai-infra-engineer-learning Module 10 — LLM Infrastructure](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure); peer platform coverage: [ai-infra-ml-platform-learning JOB_REQUIREMENTS.md — req-llm-serving-platform](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning/blob/main/JOB_REQUIREMENTS.md). |
| req-systems-programming | **Python + one systems language** (Go / Rust / C++) for infra tooling; Linux internals | 0.16 | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning — Modules 01, 04, 07](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) — this senior curriculum builds on it directly in [`project-204-k8s-operator/`](projects/project-204-k8s-operator/) (Go with operator-sdk). Dropped 0.33 → 0.16 this cycle as three systems-programming-explicit postings (Together AI Systems, Ai2 Sr SWE, OpenTeams) aged out of the window; the underlying skill demand at NVIDIA, Databricks, Anthropic, Mirantis is unchanged. |

**Why we still do NOT propose adding a Senior-track LLM-serving module (unchanged from 2026-07, -08, -09, and -10):** the frequency threshold is cleared for the fifth consecutive cycle (0.35 ≥ 0.30, 13 postings ≥ 3), but the Ownership Rule places it at **level 20** — `mod-110-llm-infrastructure` already teaches vLLM, RAG, quantization, TGI, LangChain, LoRA. The senior curriculum's `mod-204-model-optimization` already carries the transferable optimization skill (TensorRT layer fusion, ONNX Runtime execution providers, quantization, dynamic batching) that generalizes to any serving runtime. This cycle's runtime-specific detail from Red Hat llm-d (Gateway Inference Extension API, distributed vLLM), Uniphore (speculative decoding, continuous batching, chunked prefill, MoE), stack8s (vLLM-GPU-K8s), and Fireworks reinforces the case for keeping runtime specifics out of level 30 — pulling them in would anchor 2026-Q4 phrasing on a curriculum that lives multiple years. Adding a duplicate would violate the Ownership Rule; extending `mod-204` further would push toward the peer level-30 ML Platform sibling's declared surface. If the market pushes even harder, the right home is `ai-infra-ml-platform-learning`, not this repo.

### 4.3 Owned at level 30 (peer) — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-agentic-workflows | **Agentic workflows in infra tooling** (LangGraph, AutoGen, CrewAI, MCP, sandboxed code execution) | 0.05 | `ai-infra-ml-platform-learning` (30 peer) | [ai-infra-ml-platform-learning](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning) — the ML Platform peer owns agentic frameworks as a platform surface (LLM gateway, eval harness, sandboxing). Edged up to 2/37 with Cohere Agent Infrastructure. Watchlist. |

### 4.4 Owned at level 35 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-hpc-slurm-link | **Slurm / HPC schedulers** (Slurm/LSF/PBS, MPI, Enroot/Singularity, Charliecloud) | 0.11 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). Dropped 0.20 → 0.11 as three Slurm-explicit postings aged out. Senior postings that require Slurm continue to pair it with Kubernetes — that intersection is already exercised by [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/) + [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/). A standalone Slurm module would duplicate the level-35 owner. |
| req-nccl-networking | **High-performance networking depth** (NCCL, RDMA, InfiniBand, RoCE, EFA, NVLink/NVSwitch fabric ops, topology-aware scheduling) | 0.11 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) — Performance track owns the tuning depth. The NVIDIA Cloud Infra & Network Ops posting (p32) raises the operator-depth ceiling by naming NMX-C/NMX-M partition management on GB200/GB300 NVL72 and Spectrum-X Ethernet, but this remains a Performance-track specialization. The senior curriculum introduces NCCL in [`mod-202-distributed-training/`](lessons/mod-202-distributed-training/) and [`mod-203-gpu-computing/`](lessons/mod-203-gpu-computing/), and touches CNI (Cilium) in [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), which matches the level of *reasoning about* the fabric expected at senior. Optimization depth stays with Performance. |
| req-cuda-kernel-link | **Custom CUDA / Triton kernel authoring** (CUTLASS, Tensor Cores, Nsight profiling) | 0.05 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). First non-zero cycle — Databricks Senior Staff AI Runtime (p40) and Uniphore Senior Inference Engineer (p41) touch kernel-adjacent work (multi-GPU parallel execution, checkpointing performance). Still well below both bars at 2/37; owner at level 35 unchanged. |

For each item above, the senior curriculum already provides the awareness / reasoning layer (e.g., "why NCCL topology matters for FSDP throughput", "when to reach for Slurm vs. KubeRay", "when to hand off to a Performance Engineer") that a senior needs to make architecture decisions and hand off tuning depth to a Performance Engineer.

### 4.5 Watchlist (sub-threshold this cycle — not tracked as requirements yet)

| Signal | Postings | Notes |
|--------|---------:|-------|
| **AI Gateway as discrete platform layer** (traffic shaping, provider routing/failover, rate limiting, token metering, cost attribution across model providers) — **NEW this cycle** | 2/37 (p36 Cloudflare AI Gateway, p37 SentinelOne / Kong AI Gateway) | Red Hat llm-d (p33) also names the Gateway Inference Extension API in the same posting — a third adjacent citation. Below the 0.30 frequency bar. Candidate ID: `req-ai-gateway`. If next cycle crosses 0.30, the right lever is an exercise inside [`mod-205`](lessons/mod-205-multi-cloud/) (gateway as a multi-cloud/multi-provider pattern) or [`mod-207`](lessons/mod-207-observability-sre/) (token metering / cost attribution as an SLI family), not a new module. |
| **AI FinOps / token economics / unit-cost platforms** — **NEW this cycle** | 2/37 (p38 Charles Schwab AI FinOps Dev Engineer, p39 Cargill AI Platform FinOps Sr Engineer) | Distinct from generic observability-sre: emphasizes unit cost models, token economics, chargeback, business-value tracking. Candidate ID: `req-finops-cost-platform`. Below the ≥3-posting bar; one US financial-services + one APAC industrial signals real breadth. If next cycle clears the ≥3-posting bar, the right lever is an exercise inside [`mod-207`](lessons/mod-207-observability-sre/) (cost attribution as an SLI family) or [`mod-206`](lessons/mod-206-advanced-mlops/) (model-registry-driven chargeback), not a new module. |
| **MoE / KV-cache / prefill-decode / continuous batching / speculative decoding / chunked prefill** (LLM serving runtime internals) | 3/37 (p23 stack8s vLLM, p33 Red Hat llm-d, p41 Uniphore Senior Inference Engineer) | **First cycle to clear the ≥3-posting bar.** Uniphore in particular names the full vocabulary — speculative decoding + continuous batching + chunked prefill + MoE — in a single role. 3/37 = 0.08 is well below the 0.30 frequency bar, and the content belongs at level 20 mod-110 / peer level-30 ML Platform regardless. Serving-runtime-specific detail anchors 2026-Q4 phrasing; keep out of senior. |
| **Blackwell GB200/GB300 NVL72/NVL36 fabric specifics** | 4/37 (p17 NVIDIA DGX, p21 Cohere HPC, p22 Lambda, p32 NVIDIA Cloud Infra Network Ops with explicit NMX-C/NMX-M + Spectrum-X) | Clears the ≥3-posting bar; operator-level depth is sharpening in p32 (NMX-C/NMX-M partition management, Spectrum-X Ethernet). [`mod-203`](lessons/mod-203-gpu-computing/) already generalizes across GPU generations — the Blackwell NVL72 topology story is a specialization of concepts already taught. External NVIDIA Quantum-X800 / NVL72 reference material already linked in §6. |
| **Confidential / sovereign AI** (TEE, Nitro Enclaves, EU AI Act, private inference, tenant isolation for regulated workloads) | 2/37 (p16 JPM, p19 Firmus) | Regressed below the ≥3-posting bar as OpenTeams aged out. mod-209 continues to cover sovereign data residency + multi-tenant isolation at the depth senior expects. If next cycle crosses 0.30 and ≥3 postings, propose an exercise inside mod-209 before a new module. |
| **Custom accelerator fleets** (TPU / Trainium / Inferentia / AMD MI300X) | 2/37 (p06 Anthropic Node Infra — explicit 'every GPU, TPU and Trainium node'; p21 Cohere HPC — GPU/TPU superclusters) | [`mod-203`](lessons/mod-203-gpu-computing/) already teaches heterogeneous device abstractions; external Neuron / TPU / ROCm docs linked in §6. |
| **Kueue / Volcano batch scheduling** on Kubernetes | 1/37 (p22 Lambda) | Flat at 1 posting. If it clears both bars in future, the right lever is a small exercise inside [`mod-201`](lessons/mod-201-advanced-kubernetes/) (which already introduces batch/GPU scheduling), not a new module. |

---

## 5. Curriculum-plan delta this cycle — zero additions

See [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json). Every one of `modules`, `exercises`, and `projects` is intentionally an empty array — the **fifth consecutive** cycle with this verdict.

**Rationale in one paragraph** (also in the delta JSON):

Across 37 senior-band postings from the last 90 days (2026-08-05 → 2026-11-03) — rolling 25 postings forward from the 2026-10 cycle, dropping 5 that aged out, and adding 12 fresh observations from 2026-10-04 to 2026-11-03 — no requirement clears the ≥ 0.30 frequency + ≥ 3-posting bar AND is owned at level 30 AND is not already covered by an existing senior module. Seven requirements cleared both bars this cycle (`req-k8s-advanced` 0.76, `req-gpu-cluster-ops` 0.65, `req-distributed-systems` 0.59, `req-observability-sre` 0.38, `req-multi-cloud-iac` 0.38, `req-llm-serving-link` 0.35 — owned at level 20, `req-mlops-pipelines` 0.30); every one is covered by an existing senior module/project (mod-201 through mod-210, project-201 through project-204) or linked to the level-20 owner. `req-model-serving-optimization` fell back below the 0.30 bar (0.37 → 0.27) as the sample broadened to include AI-gateway, FinOps, and runtime-internals postings; it remains covered. Two **NEW watchlist signals** emerged (`watch-ai-gateway`: Cloudflare + SentinelOne/Kong, 2 postings; `watch-finops-cost`: Schwab + Cargill, 2 postings) — both are platform-engineering patterns worth watching; neither crosses the ≥3-posting bar. `watch-moe-serving` crossed the ≥3-posting bar for the first time (stack8s + Red Hat llm-d + Uniphore) but at 0.08 is well below 0.30 and belongs at level 20 / peer level-30 regardless. `watch-blackwell-nvl72` continues at 4 postings (0.11) with sharpened operator depth; mod-203 already generalizes. Continuity bias — the correct default per the packet spec and the verdict of the prior four consecutive cycles — applies again this cycle, now for the fifth consecutive time.

### 5.1 Candidate additions we considered and rejected (this cycle)

| Tempting addition | Why we rejected it |
|-------------------|--------------------|
| New `mod-211-llm-serving-platforms` (vLLM/SGLang/Triton) | Same reason as 2026-07, -08, -09, and -10: owned at level 20 in [`mod-110-llm-infrastructure`](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure) and as the flagship level-30 peer gap in `ai-infra-ml-platform-learning`. Senior-track already teaches the *transferable* optimization skill in [`mod-204-model-optimization/`](lessons/mod-204-model-optimization/). Fifth consecutive cycle rejecting this. |
| New `mod-211-ai-gateway-platforms` (traffic shaping, provider routing, token metering, cost attribution) | **NEW this cycle.** Only 2 postings explicitly (Cloudflare, SentinelOne/Kong); Red Hat llm-d adds adjacent framing. 2/37 = 0.05, well below the 0.30 frequency bar. The pattern is genuinely new and worth watching, but adding a module on a 2-posting signal would violate continuity bias. If 2026-12 crosses both bars, the right lever is an exercise inside [`mod-205-multi-cloud/`](lessons/mod-205-multi-cloud/) (gateway as a multi-cloud / multi-provider pattern) or [`mod-207-observability-sre/`](lessons/mod-207-observability-sre/) (token metering as an SLI family), not a new module. |
| New `mod-212-ai-finops` (unit cost models, token economics, chargeback) | **NEW this cycle.** Only 2 postings (Schwab US financial-services, Cargill APAC industrial). 2/37 = 0.05, well below both bars. If 2026-12 clears the ≥3-posting bar, the right lever is an exercise inside [`mod-207-observability-sre/`](lessons/mod-207-observability-sre/) (cost attribution as an SLI family) or [`mod-206-advanced-mlops/`](lessons/mod-206-advanced-mlops/) (model-registry-driven chargeback), not a new module. |
| New exercise "Deploy vLLM behind Triton with KV cache offload" in mod-204 | Would violate the Ownership Rule — every serving-framework-specific exercise anchors runtime versions (2026-Q4 vLLM's KV-cache semantics change with every minor release) and belongs at level 20 / peer level 30. |
| New exercise on prefix caching / speculative decoding / chunked prefill / KV-cache offload | Serving-runtime-specific detail (Red Hat llm-d, Uniphore, stack8s vLLM postings). `watch-moe-serving` crosses the ≥3-posting bar for the first time but 0.08 is well below 0.30, and the content anchors 2026-Q4 phrasing and belongs at level 20 mod-110 / peer level-30 ML Platform. |
| New `mod-213-observability-llm-workloads` (OTel semantic conventions for GenAI, token-rate SLOs) | req-observability-sre at 0.38 is already covered by [`mod-207-observability-sre/`](lessons/mod-207-observability-sre/). Pulling in GenAI semantic conventions would anchor 2026-Q4 OTel spec phrasing; link externally in §6 instead. |
| New `mod-214-sovereign-ai-and-confidential-inference` (TEE / EU AI Act / Nitro Enclaves) | `watch-confidential-ai` regressed below the ≥3-posting bar this cycle. mod-209 covers sovereign data residency and multi-tenant isolation at the depth senior expects. |
| New exercise on Blackwell (GB200 NVL72 / GB300 NVL36) fabric specifics / NMX-C/NMX-M | 4 postings (NVIDIA DGX, Cohere HPC, Lambda, NVIDIA Cloud Infra Network Ops) and sharper operator depth, but mod-203 already generalizes across GPU generations. Adding NMX-C/NMX-M bullets would anchor 2026-Q4 hardware phrasing on a curriculum that lives multiple years; link externally in §6 instead. |
| New exercise on custom-accelerator fleets (Trainium/TPU/Inferentia) in mod-203 | 2 postings this cycle (Anthropic Node Infra, Cohere HPC). Below both bars. mod-203 already teaches heterogeneous device abstractions; a link in resources is sufficient. |
| New `mod-215-agentic-workflows-in-infra-tooling` | 2 postings this cycle (Gatik AI, Cohere Agent Infrastructure). Well below both bars. Owned at peer level-30 ML Platform. |
| New `mod-216-kueue-batch-scheduling` | 1 posting (Lambda only). Well below the ≥3-posting bar. mod-201 already introduces batch/GPU scheduling. |

---

## 6. External resources for out-of-scope items

For learners who want to extend beyond the level-30 senior scope during or after this track:

- **LLM serving depth** — [vLLM docs](https://docs.vllm.ai/), [llm-d project](https://github.com/llm-d), [NVIDIA Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/), [SGLang GitHub](https://github.com/sgl-project/sglang), [TensorRT-LLM repo](https://github.com/NVIDIA/TensorRT-LLM), [KServe docs](https://kserve.github.io/website/), [BentoML docs](https://docs.bentoml.com/).
- **LLM serving internals** (KV cache, prefill/decode disaggregation, continuous batching, speculative decoding, chunked prefill, MoE routing) — [vLLM design docs](https://docs.vllm.ai/en/latest/design/arch_overview.html), [NVIDIA Dynamo](https://github.com/ai-dynamo/dynamo), Anyscale Ray Serve LLM patterns.
- **AI gateways** (NEW resource category this cycle) — [Cloudflare AI Gateway docs](https://developers.cloudflare.com/ai-gateway/), [Kong AI Gateway](https://konghq.com/products/kong-ai-gateway), [LiteLLM proxy](https://docs.litellm.ai/), [Portkey AI gateway](https://portkey.ai/), Red Hat llm-d Gateway Inference Extension API.
- **AI FinOps / token economics** (NEW resource category this cycle) — [FinOps Foundation AI FinOps WG](https://www.finops.org/community/working-groups/), [OpenCost](https://www.opencost.io/), model-provider pricing APIs (OpenAI, Anthropic, Google) + chargeback patterns.
- **Slurm & HPC** — SchedMD Slurm docs; [NVIDIA DGX SuperPOD reference architectures](https://docs.nvidia.com/dgx-superpod/); [NCCL user guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/).
- **Batch scheduling on Kubernetes** — [Kueue docs](https://kueue.sigs.k8s.io/), [Ray KubeRay operator](https://ray-project.github.io/kuberay/), Volcano.
- **CUDA kernel authoring** — [NVIDIA CUTLASS](https://github.com/NVIDIA/cutlass), [Triton language docs](https://triton-lang.org/), Nsight Compute training.
- **RDMA / InfiniBand / Blackwell fabrics** — Mellanox / NVIDIA InfiniBand admin guides; NCCL tuning knobs (`NCCL_IB_HCA`, `NCCL_NET_GDR_LEVEL`); [NVIDIA Quantum-X800 InfiniBand overview](https://www.nvidia.com/en-us/networking/quantum-x800/); [NVIDIA GB200 NVL72 reference](https://www.nvidia.com/en-us/data-center/gb200-nvl72/); NVIDIA NMX-C / NMX-M partition management guides (fabric-depth operator reference, Performance-track territory).
- **LLM-workload SRE / observability** — Anthropic's AI reliability engineering posts; SRE Book chapters on capacity planning; [OpenTelemetry semantic conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- **Agentic workflows in infra tooling** — LangGraph tutorials, AutoGen docs, CrewAI docs, [Model Context Protocol (MCP) spec](https://modelcontextprotocol.io/).
- **Custom accelerators** — [AWS Neuron SDK (Trainium/Inferentia)](https://awsdocs-neuron.readthedocs-hosted.com/), [Google Cloud TPU docs](https://cloud.google.com/tpu/docs), [AMD ROCm docs](https://rocm.docs.amd.com/).
- **Confidential AI / TEE / sovereign cloud** — [NVIDIA H100 Confidential Computing](https://docs.nvidia.com/confidential-computing/), [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html), [Azure Confidential Computing](https://learn.microsoft.com/en-us/azure/confidential-computing/), EU AI Act reference material.

These are reference-only and intentionally not pulled into the level-30 senior curriculum this cycle.

---

## 7. Methodology

- **Sources.** Greenhouse (`job-boards.greenhouse.io`, `job-boards.eu.greenhouse.io`, `boards.greenhouse.io`), Workday (`crowdstrike.wd5.myworkdayjobs.com`, `nvidia.wd5.myworkdayjobs.com`, `jobs.nvidia.com`, `schwabjobs.com`), Ashby (`jobs.ashbyhq.com`), Lever (`jobs.lever.co`), company career portals (Together AI, Scale AI, NVIDIA, Anthropic, Perplexity, Databricks, xAI, Oracle, JPMorgan, Tencent, Anduril, Firmus, CrowdStrike, Ai2, Lambda, Red Hat, Cohere, Apple, Adobe, Mirantis, Sesterce, stack8s, Finoit, Gatik AI, Fireworks AI, Cloudflare, SentinelOne, Uniphore, Charles Schwab, Cargill), Built In (`builtin.com` / `builtinsf.com` / `builtinnyc.com` / `builtinboston.com`), Simplify / Zapply / Dreamwork / Freehire / Dice / Accel portfolio/aggregator boards.
- **Date window.** 2026-08-05 → 2026-11-03 (last 90 days). 37 postings — all within the window. Sample composition: 25 postings carried forward from the 2026-10 cycle, 12 postings added from 2026-10-04 → 2026-11-03 observations, 5 postings aged out of the window (`p02-togetherai-ai-infra-systems`, `p05-ai2-sr-swe-ai-infra`, `p09-perplexity-mts-ai-infra`, `p11-redhat-fde-vllm-k8s`, `p25-openteams-sr-infra-gpu`).
- **Frequency denominator.** 37. Frequencies count postings that explicitly listed the requirement based on retrievable snippet or body text; frequencies may underestimate for postings where only aggregator snippets were available.
- **Continuity bias.** Applied per packet spec: default to no change, propose additions only when ≥ 3 distinct postings from the last 90 days show a gap, requirement frequency ≥ 0.30, and no existing module can be incrementally extended. In addition, the Ownership Rule was applied — even threshold-clearing items that belong at another level are linked, not duplicated.
- **Comparison to prior cycles.** The 2026-07 cycle analyzed 22 postings, 2026-08 analyzed 28, 2026-09 analyzed 32, 2026-10 analyzed 30 — all concluded zero additions. This cycle's 37-posting sample continues that trajectory. Movements this cycle (K8s 0.80 → 0.76, GPU ops 0.77 → 0.65, dist-sys 0.67 → 0.59, model-serving-opt 0.37 → 0.27 falling back below threshold, obs-sre 0.40 → 0.38, llm-serving-link 0.37 → 0.35, systems-programming 0.33 → 0.16, mlops 0.33 → 0.30, multi-cloud-iac 0.33 → 0.38, security-comp 0.17 → 0.14, hpc-slurm 0.20 → 0.11, nccl 0.17 → 0.11, dist-training 0.17 → 0.22, tech-leadership 0.20 → 0.22, cuda-kernel 0.00 → 0.05, agentic 0.03 → 0.05) are dominated by a sample broadening to include AI-gateway, FinOps, and runtime-internals roles alongside the GPU-platform / inference-platform / SRE cohort that dominated the 2026-10 cycle. Two NEW watchlist signals emerged (`watch-ai-gateway`, `watch-finops-cost`); `watch-moe-serving` crossed the ≥3-posting bar for the first time; `watch-confidential-ai` regressed. Core ownership assignments and coverage decisions are unchanged.
- **Verdict.** Zero additions. The 10-module + 4-project curriculum continues to match the current market cleanly.

---

**Maintained by VeriSwarm.ai**
