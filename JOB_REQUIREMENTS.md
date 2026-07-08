# Senior AI Infrastructure Engineer — Job Requirements Report

**Role:** Senior AI Infrastructure Engineer (level 30)
**Repository:** `ai-infra-senior-engineer-learning`
**Research window:** 2026-04-03 → 2026-07-03 (last 90 days)
**Postings analyzed:** 26 total; 22 dated in the last 90 days (4 border-line older postings retained for role definition)
**Content model:** anthropic/claude-opus-4-7
**Machine-readable source:** [`.aicg/job-requirements.json`](.aicg/job-requirements.json)
**Curriculum-plan delta this cycle:** [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json) — **zero additions**

---

## 1. Headline

The 2026-Q2 market for Senior AI Infrastructure Engineers is remarkably aligned with the existing 10-module + 4-project curriculum. Across 22 postings from the last 90 days, no requirement clears both the ≥ 3-posting AND ≥ 0.30-frequency addition thresholds *after applying the Ownership Rule*. Every high-frequency signal (Kubernetes, distributed training, GPU cluster ops, TensorRT/ONNX optimization, multi-cloud + IaC/GitOps, MLOps pipelines, observability/SRE, security, technical leadership) is already owned at level 30 by an existing senior module. Every requirement that clears the frequency threshold but belongs to a lower or higher level (LLM serving frameworks, Slurm/HPC, NCCL/RDMA depth, CUDA kernel authoring) is linked to its owner rather than duplicated.

The curriculum-plan delta is intentionally empty — see §5.

---

## 2. How to read this document

- Each requirement is grouped by category, lists the **owner role** (per the curriculum hierarchy), and points to where it is covered in this repo *or* in a lower/peer/higher-level repo.
- Ownership follows the lowest-level rule: a requirement is owned by the lowest level where it is genuinely required, and higher-level roles only re-own it when they need extra depth, architecture context, or leadership context.
- Frequencies are the number of postings from the last 90 days (out of 22) that explicitly listed the requirement.
- All evidence postings and quotes are in [`.aicg/job-requirements.json`](.aicg/job-requirements.json) under `postings[]` (referenced by ID below).

---

## 3. Market snapshot (last 90 days)

- **Title soup.** Senior postings surface under: Senior AI Infrastructure Engineer, Senior ML Infrastructure Engineer, Senior ML Platform Engineer, Sr. AI Infrastructure Engineer, Senior HPC Infrastructure Engineer, MTS AI Infrastructure Engineer, Senior Software Engineer AI Infrastructure, Senior Staff+ Infrastructure Engineer (Cluster). Postings labeled just "AI Infrastructure Engineer" with 5+-yr requirements were retained as senior-band evidence.
- **Experience band.** 5–8 years is the dominant ask. A handful (Anthropic Senior Staff+, Ai2 8+, Samsara Lead 10+) are the band above; retained because they define what a Senior graduates into.
- **Salary band.** USD ~$155k–$450k base. The middle 50% of postings that list a salary cluster $180k–$260k base.
- **Stable core stack (>60% of postings):** Kubernetes (advanced — CRDs/operators/admission controllers) 0.82; multi-cloud + Terraform/IaC/GitOps 0.77; observability/SRE (Prometheus + Grafana + OpenTelemetry + on-call + SLIs/SLOs) 0.68; Python + one systems language (Go/Rust/C++) 0.68; distributed training (FSDP/DeepSpeed/Ray/Megatron) 0.55; GPU cluster ops (NVIDIA GPU Operator, MIG, CUDA) 0.45.
- **2026 shape signals:**
  - **LLM serving frameworks** (vLLM, SGLang, TensorRT-LLM, TGI, Triton, Ray Serve, KServe) appear in 8/22 (0.36) — well above the frequency threshold. But per the Ownership Rule this is owned at **level 20** in `ai-infra-engineer-learning/mod-110-llm-infrastructure` (already teaches vLLM, RAG, quantization) and reinforced as an explicit **level-30 peer** gap by `ai-infra-ml-platform-learning` (which owns `req-llm-serving-platform`). Adding a duplicate here would violate the rule. See §4.3.
  - **Slurm / HPC schedulers** in 7/22 (0.32) — owned at **level 35** by `ai-infra-performance-learning`. See §4.4.
  - **Agentic workflows in infra tooling** (LangGraph, AutoGen, MCP) appear in 2/22 (0.09) — well below threshold, and owned by the peer level-30 ML Platform track.

---

## 4. Requirements by category

### 4.1 Owned at level 30 in this repo ✅ (covered)

| ID | Requirement | Freq. (90d) | Coverage | Evidence |
|----|-------------|------------:|----------|----------|
| req-k8s-advanced | **Advanced Kubernetes** (operators/CRDs, admission controllers, multi-cluster, GPU scheduling, service mesh) | 0.82 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/) | p01, p02, p03, p05, p06, p08, p09, p10, p12, p13, p14, p15, p16, p17, p18, p19, p23, p24, p25 |
| req-distributed-training | **Distributed training** (PyTorch DDP/FSDP, DeepSpeed, Ray Train, Megatron, checkpointing) | 0.55 | [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-201-distributed-training/`](projects/project-201-distributed-training/) | p01, p02, p12, p14, p15, p17, p18, p19 |
| req-gpu-cluster-ops | **GPU cluster ops** (NVIDIA GPU Operator, MIG, CUDA drivers, H100/H200, profiling, cost) | 0.45 | [`lessons/mod-203-gpu-computing/`](lessons/mod-203-gpu-computing/) | p01, p06, p07, p08, p09, p18, p23, p24 |
| req-model-serving-optimization | **Model optimization & serving** (TensorRT, ONNX, quantization, dynamic batching, Triton) | 0.36 | [`lessons/mod-204-model-optimization/`](lessons/mod-204-model-optimization/), [`projects/project-202-model-serving/`](projects/project-202-model-serving/) | p04, p11, p13, p17, p20 |
| req-multi-cloud-iac | **Multi-cloud + IaC/GitOps** (AWS/GCP/Azure, Terraform, Pulumi, Ansible, Helm, ArgoCD/Flux) | 0.77 | [`lessons/mod-205-multi-cloud/`](lessons/mod-205-multi-cloud/), [`lessons/mod-208-iac-gitops/`](lessons/mod-208-iac-gitops/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p01, p02, p03, p04, p06, p09, p10, p11, p12, p14, p16, p17, p19, p21, p23, p24, p25 |
| req-mlops-pipelines | **MLOps pipelines** (Kubeflow, Airflow, Argo Workflows, MLflow, feature stores, model registry, CI/CD for ML) | 0.32 | [`lessons/mod-206-advanced-mlops/`](lessons/mod-206-advanced-mlops/) | p02, p12, p15, p19, p20 |
| req-observability-sre | **Observability & SRE** (Prometheus, Grafana, OpenTelemetry, distributed tracing, SLI/SLO, incident response, chaos) | 0.68 | [`lessons/mod-207-observability-sre/`](lessons/mod-207-observability-sre/) | p01, p02, p03, p04, p05, p06, p08, p09, p10, p11, p12, p14, p15, p16, p20, p21, p23, p25 |
| req-security-compliance | **Security & compliance** (multi-tenant RBAC, secrets management, network policies, GDPR/SOC2/ISO-27001, tenant isolation) | 0.23 | [`lessons/mod-209-security-compliance/`](lessons/mod-209-security-compliance/) | p03, p09, p15, p23 |
| req-technical-leadership | **Technical leadership** (RFCs, code reviews, mentoring, cross-team initiatives, technology evaluation) | 0.32 | [`lessons/mod-210-technical-leadership/`](lessons/mod-210-technical-leadership/) | p03, p05, p15, p21, p24 |
| req-distributed-systems | **Large-scale distributed systems design** (capacity, HA, cross-region) | 0.36 | [`lessons/mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), [`lessons/mod-202-distributed-training/`](lessons/mod-202-distributed-training/), [`projects/project-203-multi-region/`](projects/project-203-multi-region/) | p03, p04, p05, p16, p21 |

Every level-30-owned requirement above is already covered by an existing module or project. No net-new module or exercise is proposed on the basis of any of these.

### 4.2 Owned at level 20 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-systems-programming | **Python + one systems language** (Go / Rust / C++) for infra tooling; Linux internals | 0.68 | `ai-infra-engineer-learning` (20) | [ai-infra-engineer-learning — Modules 01, 04, 07](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) — this senior curriculum builds on it directly in [`project-204-k8s-operator/`](projects/project-204-k8s-operator/) (Go with operator-sdk). |
| req-llm-serving-link | **LLM serving frameworks** (vLLM, SGLang, TensorRT-LLM, TGI, Triton, Ray Serve, KServe) | 0.36 | `ai-infra-engineer-learning` (20) primary; `ai-infra-ml-platform-learning` (30 peer) for platform-level | [ai-infra-engineer-learning Module 10 — LLM Infrastructure](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure); peer platform coverage: [ai-infra-ml-platform-learning JOB_REQUIREMENTS.md — req-llm-serving-platform](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning/blob/main/JOB_REQUIREMENTS.md). |

**Why we do NOT propose adding a Senior-track LLM-serving module:** the frequency threshold is cleared (0.36 ≥ 0.30, 8 postings ≥ 3), but the Ownership Rule places it at **level 20** — `mod-110-llm-infrastructure` already teaches vLLM, RAG, quantization, TGI, LangChain, LoRA. The senior curriculum's `mod-204-model-optimization` already carries the transferable optimization skill (TensorRT layer fusion, ONNX Runtime execution providers, quantization, dynamic batching) that generalizes to any serving runtime. Adding a duplicate would violate the Ownership Rule; extending `mod-204` further would push toward the level-30 ML Platform sibling's declared surface. If the market moves further, the right home is `ai-infra-ml-platform-learning`, not this repo.

### 4.3 Owned at level 30 (peer) — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-agentic-workflows | **Agentic workflows in infra tooling** (LangGraph, AutoGen, MCP) | 0.09 | `ai-infra-ml-platform-learning` (30 peer) | [ai-infra-ml-platform-learning](https://github.com/ai-infra-curriculum/ai-infra-ml-platform-learning) — the ML Platform peer owns agentic frameworks as a platform surface (LLM gateway, eval harness). Below the 0.30 threshold at senior level anyway. |

### 4.4 Owned at level 35 — linked, not duplicated

| ID | Requirement | Freq. (90d) | Owner (level) | Where it lives |
|----|-------------|------------:|---------------|----------------|
| req-nccl-networking | **High-performance networking depth** (NCCL, RDMA, InfiniBand, RoCE, EFA, topology-aware scheduling) | 0.36 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning) — Performance track owns the tuning depth. This senior curriculum introduces NCCL in [`mod-202-distributed-training/`](lessons/mod-202-distributed-training/) and touches CNI (Cilium) in [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/), which matches the level of *reasoning about* the fabric expected at senior. Optimization depth stays with Performance. |
| req-hpc-slurm-link | **Slurm / HPC schedulers** (Slurm/LSF/PBS, MPI, Enroot/Singularity, Charliecloud) | 0.32 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). Senior postings that require Slurm (Anthropic, Perplexity, Ai2, NVIDIA HPC, Firmus, Sarvam) always pair it with Kubernetes — that intersection is already exercised by [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/) + [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/). A standalone Slurm module would duplicate the level-35 owner. |
| req-cuda-kernel-link | **Custom CUDA / Triton kernel authoring** (CUTLASS, Tensor Cores, Nsight profiling) | 0.09 | `ai-infra-performance-learning` (35) | [ai-infra-performance-learning](https://github.com/ai-infra-curriculum/ai-infra-performance-learning). Only 2/22 postings (xAI Kernels, Sarvam Training-Infra) require kernel-authoring work at this seniority; below threshold and unambiguously a Performance-track skill. |

For each item above, the senior curriculum already provides the awareness / reasoning layer (e.g., "why NCCL topology matters for FSDP throughput", "when to reach for Slurm vs. KubeRay") that a senior needs to make architecture decisions and hand off tuning depth to a Performance Engineer.

---

## 5. Curriculum-plan delta this cycle — zero additions

See [`.aicg/curriculum-plan-delta.json`](.aicg/curriculum-plan-delta.json). Every one of `modules`, `exercises`, and `projects` is intentionally an empty array.

**Rationale in one paragraph** (also in the delta JSON):

Across 22 senior-band postings from the last 90 days, the four requirements that clear the ≥ 0.30 frequency + ≥ 3-posting bar are `req-llm-serving-link` (0.36), `req-hpc-slurm-link` (0.32), `req-nccl-networking` (0.36), and `req-systems-programming` (0.68). The Ownership Rule sends the first two to level 20 (`ai-infra-engineer-learning` mod-110 for LLM serving) and level 35 (`ai-infra-performance-learning` for Slurm and NCCL depth); systems programming is a level-20 foundation this repo builds *on*, not owns. Every other senior-band requirement (K8s advanced, distributed training, GPU cluster ops, model optimization, multi-cloud + IaC, MLOps pipelines, observability/SRE, security, distributed systems, technical leadership) is already covered by the 10-module + 4-project senior curriculum. No net-new module, exercise, or project is justified this cycle. Continuity bias — the correct default per the packet spec — applies.

### 5.1 Candidate additions we considered and rejected

| Tempting addition | Why we rejected it |
|-------------------|--------------------|
| New `mod-211-llm-serving-platforms` (vLLM/SGLang/Triton) | Owned at level 20 in [`mod-110-llm-infrastructure`](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning/blob/main/CURRICULUM.md#module-10-llm-infrastructure) and as the flagship level-30 peer gap in `ai-infra-ml-platform-learning`. Senior-track already teaches the *transferable* optimization skill (TensorRT, ONNX, dynamic batching) in [`mod-204-model-optimization/`](lessons/mod-204-model-optimization/). |
| New exercise "Deploy vLLM behind Triton" in mod-204 | Would violate the Ownership Rule — every serving-framework-specific exercise anchors runtime versions and belongs at level 20 / peer level 30. If the market signal grows, add a *link* in the module resources, not a duplicated exercise. |
| New `mod-212-hpc-slurm-for-ai` | Owned at level 35 (`ai-infra-performance-learning`). Senior postings that list Slurm always list Kubernetes too — the interop is already exercised in [`mod-201-advanced-kubernetes/`](lessons/mod-201-advanced-kubernetes/) and [`projects/project-204-k8s-operator/`](projects/project-204-k8s-operator/). |
| New exercise on NCCL tuning + InfiniBand topology in mod-203 | The senior-level *reasoning* layer already exists (mod-202 covers NCCL basics + tuning, mod-203 covers profiling). Tuning depth is Performance-track (level 35). Adding a tuning lab here would duplicate `ai-infra-performance-learning` scope. |
| New `mod-213-ai-workload-sre` for chaos/incident response on LLM serving | Anthropic's Staff AI Reliability posting is the strongest single signal here, but reliability requirements are covered by [`mod-207-observability-sre/`](lessons/mod-207-observability-sre/) (SLOs, error budgets, incident response, postmortems). Adding a duplicate risks anchoring on 2026-Q2 phrasing ("LLM SLI", "token-path tracing"). |
| New agentic-workflows-for-infra-tooling exercise | 2/22 postings (both Gatik AI). Below the 0.30 threshold. Owned at peer level 30 by ML Platform track. |

---

## 6. External resources for out-of-scope items

For learners who want to extend beyond the level-30 senior scope during or after this track:

- **LLM serving depth** — [vLLM docs](https://docs.vllm.ai/), [NVIDIA Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/), [SGLang GitHub](https://github.com/sgl-project/sglang), [TensorRT-LLM repo](https://github.com/NVIDIA/TensorRT-LLM), [KServe docs](https://kserve.github.io/website/).
- **Slurm & HPC** — SchedMD Slurm docs; [NVIDIA DGX SuperPOD reference architectures](https://docs.nvidia.com/dgx-superpod/); [NCCL user guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/).
- **CUDA kernel authoring** — [NVIDIA CUTLASS](https://github.com/NVIDIA/cutlass), [Triton language docs](https://triton-lang.org/), Nsight Compute training.
- **RDMA / InfiniBand** — Mellanox / NVIDIA InfiniBand admin guides; NCCL tuning knobs (`NCCL_IB_HCA`, `NCCL_NET_GDR_LEVEL`).
- **LLM-workload SRE / observability** — Anthropic's AI reliability engineering posts; SRE Book Chapters on capacity planning; [OpenTelemetry semantic conventions for LLMs](https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- **Agentic workflows in infra tooling** — LangGraph tutorials, AutoGen docs, Model Context Protocol (MCP) spec.

These are reference-only and intentionally not pulled into the level-30 senior curriculum this cycle.

---

## 7. Methodology

- **Sources.** Greenhouse (`job-boards.greenhouse.io`), Ashby (`jobs.ashbyhq.com`), Lever (`jobs.lever.co`), company career portals (Scale AI, GM, NVIDIA, Anthropic, Perplexity, Samsara, Red Hat, Lenovo), Built In (`builtin.com` / `builtinsf.com`), LinkedIn.
- **Date window.** 2026-04-03 → 2026-07-03 (last 90 days). Four border-line older postings (Wex 2026-02, ArangoDB 2026-03, Hippocratic 2025-10, NVIDIA Sr AI Infra 2025-08) are retained as evidence for role definition and marked `within_90d=false` in the JSON; they are **not** counted in the frequency denominators.
- **26 postings total.** 22 dated within 90 days form the frequency denominator. Where a full posting body was not retrievable (Prior Labs, Sarvam SRE, Meshy, Pragmatike, Lenovo, Dyna partial), the record still confirms role *prevalence* and *level*; it contributes to postings-analyzed but only to frequencies where an explicit requirement quote was verifiable.
- **Continuity bias.** Applied per packet spec: default to no change, propose additions only when ≥ 3 distinct postings from the last 90 days show a gap, requirement frequency ≥ 0.30, and no existing module can be incrementally extended. In addition, the Ownership Rule was applied — even threshold-clearing items that belong at another level are linked, not duplicated.
- **Verdict.** Zero additions. The 10-module + 4-project curriculum matches the current market cleanly.

---

**Maintained by VeriSwarm.ai**
