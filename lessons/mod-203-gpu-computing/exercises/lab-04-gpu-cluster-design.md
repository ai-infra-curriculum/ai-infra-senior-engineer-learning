# Lab 04: GPU Cluster Design Exercise

## Lab Overview

**Duration**: 3-4 hours
**Difficulty**: Advanced
**Prerequisites**: All Module 203 lectures, especially Lecture 08 (GPU Cluster Design)

In this design exercise, you will architect a complete GPU cluster for an enterprise ML platform.

## Learning Objectives

1. Design GPU cluster architecture from requirements
2. Calculate network bandwidth and storage needs
3. Plan power, cooling, and physical infrastructure
4. Create cost estimates and TCO analysis
5. Document design decisions and trade-offs

## Scenario

You are designing a GPU cluster for TechCorp, a mid-sized company building an internal ML platform.

### Business Requirements

**Company Profile:**
- 50 data scientists and ML engineers
- 10 teams working on various ML projects
- Models range from 100M to 100B parameters
- Mix of training (60%) and inference (40%) workloads
- Growth projection: 2x users in 2 years

**Technical Requirements:**
- Support 10-20 concurrent training jobs
- Serve 50+ inference models
- Handle datasets up to 10TB
- 99.5% uptime SLA
- Multi-tenancy with resource quotas
- Cost target: $2-3M initial, <$1M/year operational

**Workload Characteristics:**
- Training: GPT-style models (1B-100B params), vision models (ResNet, BERT)
- Inference: Real-time (p95 latency <100ms) and batch
- Data: Image datasets (100GB-5TB), text corpora (1-10TB)
- Peak usage: 9am-6pm weekdays, 30% utilization nights/weekends

## Part 1: Requirements Analysis

### Exercise 1.1: Compute Requirements

**Task**: Calculate GPU requirements

```
Current Workload Analysis:
===========================

Training Jobs:
- Small models (<1B params): 5 concurrent jobs
  * Batch size: 32-64
  * GPU memory needed: 8-16GB
  * Training time: 2-8 hours
  * Preferred: A10 or better

- Medium models (1B-10B params): 3-5 concurrent jobs
  * Batch size: 16-32
  * GPU memory needed: 24-40GB
  * Training time: 12-48 hours
  * Preferred: A100 40GB

- Large models (10B-100B params): 1-2 concurrent jobs
  * Requires multi-GPU (8-32 GPUs)
  * GPU memory needed: Full A100/H100 nodes
  * Training time: days to weeks
  * Required: A100 80GB or H100

Inference:
- 50 models to serve
- Mix of small (ResNet, BERT-base) and large (GPT-2, BERT-large)
- QPS: 10-1000 per model
- Latency requirement: <100ms p95

TODO: Calculate minimum GPUs needed
======================================
Small training: ___ GPUs (type: ____)
Medium training: ___ GPUs (type: ____)
Large training: ___ GPUs (type: ____)
Inference: ___ GPUs (type: ____)

Total minimum: ___ GPUs
Recommended (with buffer): ___ GPUs

Node configuration:
- ___ nodes with 8x A100 80GB
- ___ nodes with 8x A100 40GB  
- ___ nodes with 4x A10G
```

### Exercise 1.2: Network Requirements

**Task**: Design network topology and calculate bandwidth

```
Network Bandwidth Calculation:
===============================

1. All-reduce traffic for distributed training:
   Model: 10B params = 20GB (FP16)
   All-reduce: 2x model size = 40GB per step
   Training speed: 10 steps/sec desired
   Bandwidth per node: 40GB × 10 / 8 GPUs = 50 GB/s = 400 Gbps

2. Inter-node traffic:
   64 GPUs across 8 nodes
   Ring all-reduce: each node talks to 2 neighbors
   Peak bandwidth: 400 Gbps × 2 = 800 Gbps per node

3. Storage bandwidth:
   Data loading: 1000 images/sec × 150 KB/image = 150 MB/s per job
   10 concurrent jobs: 1.5 GB/s total
   Add 3x margin: 4.5 GB/s = 36 Gbps

TODO: Network design
====================
Intra-node: NVLink (provided by DGX/HGX)

Inter-node:
- Links per node: ___ × ___ GbE
- Total bisection bandwidth: ___ Tbps
- Network topology: ____________
- Switches needed:
  * Leaf switches: ___ × ____ ports
  * Spine switches: ___ × ____ ports
```

### Exercise 1.3: Storage Requirements

**Task**: Design storage architecture

```
Storage Calculation:
====================

Datasets:
- Current: 10TB
- Growth: 50TB in 2 years
- Working set: 5TB (frequently accessed)

Checkpoints:
- Model checkpoints: 100GB each (large models)
- Checkpoint frequency: every 1000 steps
- Retention: Keep last 10 checkpoints = 1TB per training job
- Concurrent jobs: 10 × 1TB = 10TB

Model registry:
- Trained models: 200 models × 5GB avg = 1TB
- Model versions: 3x = 3TB

TODO: Storage tiers
===================
Tier 1 - Hot (NVMe, parallel FS):
- Capacity: ___ TB
- Bandwidth: ___ GB/s
- IOPS: ___ K
- Use case: Active training, checkpoints

Tier 2 - Warm (SAS/SATA):
- Capacity: ___ TB
- Bandwidth: ___ GB/s
- Use case: Dataset archive, old checkpoints

Tier 3 - Cold (Object storage):
- Capacity: ___ TB
- Use case: Long-term archive, backups

Chosen storage solution: _____________ (e.g., WekaFS, Vast, DDN)
```

## Part 2: Cluster Architecture Design

### Exercise 2.1: Node Configuration

**Task**: Design compute node specifications

```
Node Type 1: Training Nodes (DGX-style)
========================================
GPU: 8× NVIDIA ______ (A100/H100)
CPU: 2× ______ (cores: ____)
RAM: ____ GB (DDR4/DDR5)
Storage: ____ TB NVMe
Network: __× ____ GbE NICs
Form factor: ____ U
Power: ____ kW per node

Quantity: ____ nodes
Total cost: $_____ (estimate)

Node Type 2: Inference Nodes
=============================
GPU: ___× NVIDIA ______ (A10/L4/T4)
CPU: ___× ______
RAM: ____ GB
Storage: ____ TB NVMe
Network: __× ____ GbE NICs
Form factor: ____ U
Power: ____ kW per node

Quantity: ____ nodes
Total cost: $_____ (estimate)

TODO: Justify node type choices
================================
Why this GPU model? ___________________________
Why this quantity? ___________________________
Alternatives considered: ___________________________
```

### Exercise 2.2: Network Topology Diagram

**Task**: Draw network architecture

```
TODO: Create network diagram showing:
======================================
- Compute nodes
- Network switches (leaf/spine)
- Storage systems
- Management network
- Uplinks to internet/cloud

Use ASCII art or draw.io:

Example skeleton:
                 [Spine 1] [Spine 2]
                  /  |  \    /  |  \
              [Leaf1][Leaf2][Leaf3][Leaf4]
                |  |    |  |    |  |    |  |
              [DGX] [DGX] [Inf] [Inf] [Storage]

TODO: Complete diagram with:
- Port counts
- Bandwidth labels
- VLAN segmentation
- Redundancy paths
```

### Exercise 2.3: Storage Architecture

**Task**: Design storage system

```
Parallel Filesystem: ____________
===================================
Metadata servers: ___ nodes
Data servers: ___ nodes
Client mounts: All compute nodes
Protocol: NFS/Lustre/WekaFS

Performance targets:
- Aggregate bandwidth: ___ GB/s
- Random read IOPS: ___ K
- Random write IOPS: ___ K

Capacity: ___ TB usable (___ TB raw)

Backup strategy:
- Snapshots: ___________________
- Off-site backup: ___________________
- Recovery time objective (RTO): ___ hours
- Recovery point objective (RPO): ___ hours
```

## Part 3: Infrastructure Planning

### Exercise 3.1: Power and Cooling

**Task**: Calculate datacenter requirements

```
Power Calculation:
==================

Compute nodes: ___ nodes × ___ kW = ___ kW
Network switches: ___ switches × ___ kW = ___ kW
Storage: ___ kW
Cooling (PUE 1.3): ___ kW × 0.3 = ___ kW

Total power: ___ kW (___  kVA @ 0.9 PF)

Cooling:
--------
Heat output: ___ kW × 3.41 = ___ BTU/hr
Cooling capacity needed: ___ tons (1 ton = 12,000 BTU/hr)

Cooling approach: [ ] Air  [ ] Liquid  [ ] Hybrid

Rack layout:
------------
Racks needed: ____ × 42U racks
Power per rack: ____ kW
Cooling per rack: ____ tons

TODO: Justify cooling choice
=============================
If air cooling: Max power per rack = ____ kW (datacenter limit)
If liquid cooling: Benefits: _________________________
                  Additional cost: $_________
```

### Exercise 3.2: Physical Layout

**Task**: Design datacenter floor plan

```
Datacenter Requirements:
========================

Floor space:
- Compute racks: ____ racks
- Network racks: ____ racks
- Storage racks: ____ racks
- Hot aisle / cold aisle layout

Total space: ____ sq ft

Power distribution:
- Main feed: ____ V, ____ A
- PDUs: ____ redundant
- UPS: ____ minutes runtime

TODO: Create rack elevation diagram
====================================
Show:
- Equipment layout in each rack type
- Cable management
- Airflow direction
- Power distribution
```

## Part 4: Software Stack

### Exercise 4.1: System Software

**Task**: Define software architecture

```
Operating System: ____________
GPU Drivers: NVIDIA Driver version _____
CUDA Toolkit: Version _____

Container Runtime:
- Docker / containerd version _____
- NVIDIA Container Toolkit version _____

Orchestration:
[ ] Kubernetes
[ ] Slurm
[ ] Ray
[ ] Custom

TODO: If Kubernetes, specify:
==============================
- Distribution: ___________ (vanilla/OpenShift/Rancher/etc.)
- GPU operator version: _____
- Network CNI: ___________ (Calico/Cilium/etc.)
- Storage CSI: ___________
- Ingress controller: ___________

Node pools:
- Training pool: ____ nodes
- Inference pool: ____ nodes
- System pool: ____ nodes
```

### Exercise 4.2: ML Platform

**Task**: Design ML platform components

```
ML Platform Stack:
==================

Experiment tracking:
[ ] MLflow
[ ] Weights & Biases
[ ] Custom
Choice: ___________ 
Reasoning: ___________________

Model serving:
[ ] TorchServe
[ ] TensorFlow Serving
[ ] Triton Inference Server
[ ] KServe
Choice: ___________
Reasoning: ___________________

Job scheduling:
[ ] Kubeflow
[ ] MLflow
[ ] Airflow
[ ] Ray
Choice: ___________
Reasoning: ___________________

Notebooks:
[ ] JupyterHub
[ ] Custom
Choice: ___________
GPU support: [ ] Yes [ ] No

Monitoring:
- Metrics: Prometheus + Grafana
- Logging: ___________ (ELK/Loki/etc.)
- Tracing: ___________ (Jaeger/Zipkin/etc.)
- GPU monitoring: DCGM Exporter
```

## Part 5: Cost Analysis

### Exercise 5.1: Capital Expenditure (CapEx)

**Task**: Estimate initial investment

```
Hardware Costs:
===============

Compute:
- Training nodes: $_____ × ____ = $_______
- Inference nodes: $_____ × ____ = $_______

Networking:
- Leaf switches: $_____ × ____ = $_______
- Spine switches: $_____ × ____ = $_______
- NICs/cables: $_______

Storage:
- Parallel FS: $_______
- Backup system: $_______

Infrastructure:
- Racks/PDUs: $_______
- Cooling (if liquid): $_______

Installation/integration: $_______

Total CapEx: $_______

TODO: Verify within budget ($_______}
```

### Exercise 5.2: Operational Expenditure (OpEx)

**Task**: Estimate annual operating costs

```
Annual OpEx:
============

Power:
- Consumption: ____ kW × 24hr × 365 × $0.12/kWh = $_______

Datacenter:
- Colocation: $___/rack/month × ____ racks × 12 = $_______
- Or cloud: $___/hour × ____ hours/year = $_______

Personnel:
- Cluster admin: 2 FTE × $___K = $_______
- ML platform engineers: 2 FTE × $___K = $_______

Software licenses:
- Enterprise support: $_______
- ML platform: $_______

Maintenance:
- Hardware support (10% of CapEx): $_______

Total annual OpEx: $_______
```

### Exercise 5.3: TCO and ROI

**Task**: Calculate 3-year total cost

```
3-Year TCO:
===========

Year 0: CapEx = $_______
Year 1: OpEx = $_______
Year 2: OpEx + hardware refresh (20%) = $_______
Year 3: OpEx = $_______

Total 3-year cost: $_______

Compare to cloud:
-----------------
Equivalent cloud cost:
- ____ A100 instances × $__/hour × ____ hours = $_______/year
- 3-year cloud cost: $_______

Savings vs. cloud: $_______ (____ %)

Break-even: ____ months

TODO: Justification
===================
When does on-prem make sense? _______________________
Risk factors: _______________________
```

## Part 6: Implementation Plan

### Exercise 6.1: Deployment Phases

**Task**: Create rollout plan

```
Phase 1: Initial Deployment (Month 1-2)
=========================================
- Install 1-2 racks of hardware
- Configure network (core + 1-2 leaf switches)
- Setup storage (Tier 1 only)
- Deploy Kubernetes/Slurm
- Onboard 2-3 pilot teams

Deliverable: Working cluster for pilot users
Success criteria: Run 3-5 training jobs successfully

Phase 2: Production Rollout (Month 3-4)
========================================
- Add remaining compute nodes
- Complete network fabric
- Setup monitoring and alerting
- Onboard remaining teams
- Deploy ML platform tools

Deliverable: Full cluster operational
Success criteria: Support all 10 teams

Phase 3: Optimization (Month 5-6)
==================================
- Performance tuning
- Cost optimization
- Documentation
- Training for users
- Runbooks for ops

Deliverable: Optimized, documented platform
Success criteria: Meet SLA targets

TODO: Risks and mitigation
===========================
Risk 1: ________________
Mitigation: ________________

Risk 2: ________________
Mitigation: ________________
```

### Exercise 6.2: Success Metrics

**Task**: Define KPIs

```
Technical KPIs:
===============
- GPU utilization: Target >____% (average)
- Job queue time: Target <____ minutes (p95)
- Training throughput: ____ jobs/day
- Inference latency: <____ ms (p95)
- System uptime: >____% 

Business KPIs:
==============
- User satisfaction: >____/5
- Time to train model: ____ % reduction vs. cloud
- Cost per GPU-hour: $____
- ROI: Break-even in ____ months

Monitoring:
===========
- Dashboard: Grafana
- Alerting: PagerDuty/Opsgenie
- Review cadence: Weekly/Monthly

TODO: How will you track these?
================================
```

## Deliverables

Submit complete design document including:

1. **Executive Summary** (1 page)
   - Business requirements recap
   - Proposed solution overview
   - Cost and timeline summary

2. **Technical Architecture** (5-10 pages)
   - Compute architecture
   - Network topology diagram
   - Storage design
   - Software stack
   - Monitoring and operations

3. **Infrastructure Plan** (3-5 pages)
   - Physical layout
   - Power and cooling
   - Rack elevations
   - Cable diagrams

4. **Cost Analysis** (2-3 pages)
   - CapEx breakdown
   - OpEx projections
   - TCO vs. cloud comparison
   - ROI analysis

5. **Implementation Plan** (2-3 pages)
   - Phased rollout
   - Timeline (Gantt chart)
   - Risks and mitigations
   - Success criteria

6. **Appendices**
   - Vendor quotes (if available)
   - Alternative architectures considered
   - Scaling plan for year 2-3

## Evaluation Criteria

- **Requirements Analysis** (15%): Thorough understanding of needs
- **Technical Design** (30%): Sound architecture decisions
- **Cost Optimization** (20%): Realistic costs, good value
- **Feasibility** (15%): Practical, implementable design
- **Documentation** (10%): Clear, professional presentation
- **Innovation** (10%): Creative solutions to challenges

## Bonus: Advanced Challenges

1. **Hybrid Cloud**: Design for bursting to cloud during peak demand
2. **Multi-Region**: Design for geo-distributed teams
3. **Sustainability**: Calculate carbon footprint, optimize for energy efficiency
4. **Disaster Recovery**: Design HA and DR strategy
5. **Security**: Design security architecture (network segmentation, access control)

---

**This design exercise synthesizes all Module 203 concepts into a real-world architecture. Good luck!**
