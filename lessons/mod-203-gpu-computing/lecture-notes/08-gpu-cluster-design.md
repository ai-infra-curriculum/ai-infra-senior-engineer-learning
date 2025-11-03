# Lecture 08: GPU Cluster Design and Architecture

## Learning Objectives

By the end of this lecture, you will be able to:

- Design enterprise-scale GPU clusters following NVIDIA BasePOD reference architectures with proper consideration for network topology, storage, power, and cooling requirements
- Architect high-performance network fabrics using NVSwitch, NVLink, InfiniBand, or RoCE with proper topology design to minimize communication bottlenecks in distributed training
- Implement GPUDirect RDMA and NCCL optimizations to achieve maximum inter-node GPU communication bandwidth and minimize latency for multi-node training workloads
- Design tiered storage architectures combining local NVMe, parallel filesystems, and object storage to optimize data loading performance and cost for different ML workflow stages
- Evaluate GPU cluster configurations (DGX systems, networking, storage) based on workload requirements, budget constraints, and scalability objectives for organizations of different sizes
- Calculate and plan for power, cooling, and datacenter infrastructure requirements including PDUs, UPS systems, and cooling strategies (air, liquid, immersion) for high-density GPU deployments
- Architect fault-tolerant GPU infrastructure with redundant network paths, storage systems, and power distribution to minimize single points of failure in production ML platforms
- Design capacity planning and growth strategies for GPU clusters that balance immediate needs with future scalability using modular expansion approaches and spine-leaf network topologies

## Table of Contents
1. [Introduction to GPU Clusters](#introduction-to-gpu-clusters)
2. [Cluster Architecture Principles](#cluster-architecture-principles)
3. [Network Topology and Fabric](#network-topology-and-fabric)
4. [NVSwitch and GPU Fabric](#nvswitch-and-gpu-fabric)
5. [NVIDIA DGX Systems](#nvidia-dgx-systems)
6. [BasePOD Reference Architecture](#basepod-reference-architecture)
7. [Storage Considerations](#storage-considerations)
8. [Power and Cooling Infrastructure](#power-and-cooling-infrastructure)

## Introduction to GPU Clusters

GPU clusters are the foundation of enterprise AI infrastructure, enabling distributed training of large models and high-throughput inference at scale.

### Why GPU Clusters?

1. **Scale Beyond Single Node**: Train models too large for one server
2. **Faster Training**: Distribute workload across many GPUs
3. **Higher Throughput**: Serve more inference requests
4. **Fault Tolerance**: Continue operating if nodes fail
5. **Resource Efficiency**: Share expensive GPU resources

### Cluster Size Considerations

**Small Cluster (2-8 nodes, 16-64 GPUs):**
- Use case: Single team, medium models, dev/test
- Cost: $100K-$500K
- Network: 100 GbE, single switch
- Cooling: Standard datacenter

**Medium Cluster (8-32 nodes, 64-256 GPUs):**
- Use case: Multiple teams, large models (up to 100B params)
- Cost: $500K-$2M
- Network: 200-400 GbE, spine-leaf
- Cooling: Enhanced cooling required

**Large Cluster (32-128 nodes, 256-1024 GPUs):**
- Use case: Enterprise ML platform, foundation models
- Cost: $2M-$10M+
- Network: 400 GbE-3.2 Tbps, large-scale fabric
- Cooling: Dedicated cooling infrastructure

**Superscale Cluster (128+ nodes, 1024+ GPUs):**
- Use case: Training LLMs (100B-1T params), research labs
- Cost: $10M-$100M+
- Network: Custom fabric, InfiniBand or RoCE
- Cooling: Liquid cooling, dedicated power substations

### Design Goals

1. **High Bandwidth**: Minimize communication overhead
2. **Low Latency**: Fast GPU-to-GPU communication
3. **Scalability**: Easy to add more nodes
4. **Reliability**: Minimize single points of failure
5. **Manageability**: Easy to monitor and maintain
6. **Cost Efficiency**: Optimize price/performance

## Cluster Architecture Principles

### Compute Architecture

**Node Types:**

```
1. Training Nodes (GPU-dense)
   ├── 8x NVIDIA A100/H100 SXM
   ├── 2x AMD EPYC or Intel Xeon (CPU)
   ├── 2TB+ RAM
   ├── NVLink/NVSwitch for intra-node
   └── 8x 200Gbps network (ConnectX-7)

2. Inference Nodes (mixed)
   ├── 4-8x NVIDIA A10/L4/T4
   ├── 1-2x CPU
   ├── 512GB RAM
   ├── PCIe Gen 4/5
   └── 2-4x 100Gbps network

3. CPU Nodes (data processing)
   ├── High core count CPUs
   ├── Large RAM (1-4TB)
   └── Fast storage

4. Storage Nodes
   ├── High-capacity NVMe
   ├── RAID controllers
   └── High network bandwidth
```

### Cluster Topology

**Flat Topology** (Small clusters, <8 nodes):
```
[Node 1] ─┐
[Node 2] ─┤
[Node 3] ─┼─ [Single Switch] ─ [Storage]
[Node 4] ─┤
[Node 5] ─┘
```

Pros: Simple, low latency
Cons: Limited scalability, single point of failure

**Spine-Leaf Topology** (Medium to large clusters):
```
        [Spine 1]     [Spine 2]     [Spine 3]
         /  |  \       /  |  \       /  |  \
        /   |   \     /   |   \     /   |   \
    [Leaf1][Leaf2][Leaf3][Leaf4][Leaf5][Leaf6]
      |  |   |  |   |  |   |  |   |  |   |  |
    Nodes Nodes Nodes Nodes Nodes Nodes Nodes
```

Pros: Scalable, redundant paths, predictable latency
Cons: More complex, higher cost

**Fat Tree Topology** (Large clusters):
```
              [Core Switches]
            /      |      |      \
        [Aggregation Switches]
        /    |    |    |    |    \
    [ToR Switches]
     |  |  |  |  |  |  |  |  |  |
   Nodes with GPUs
```

Pros: High bisection bandwidth, scales well
Cons: Complex, expensive

### Network Requirements

**Bandwidth Calculations:**

For 8 GPUs with data parallel training:
```
All-reduce traffic per step:
  Model size: 10B params × 2 bytes (FP16) = 20GB
  All-reduce: 2 × 20GB = 40GB per step (ring algorithm)
  If 100ms per step, need: 40GB / 0.1s = 400 GB/s total

With 8 GPUs:
  Per-GPU bandwidth: 400 GB/s / 8 = 50 GB/s = 400 Gbps

Add overhead (20%): 480 Gbps per GPU
```

For multi-node (64 GPUs across 8 nodes):
```
Inter-node all-reduce traffic:
  Each node needs to communicate with 7 others
  Traffic per node: 40GB × 7 / 8 = 35GB per step
  Bandwidth per node: 35GB / 0.1s = 350 GB/s = 2.8 Tbps

Use 8x 400GbE links per node (3.2 Tbps total)
```

## Network Topology and Fabric

### Ethernet vs. InfiniBand

**Ethernet (RoCE - RDMA over Converged Ethernet):**

Pros:
- Standard, interoperable
- Lower cost
- Familiar to ops teams
- Scales well

Cons:
- Higher latency than IB
- More CPU overhead
- Requires careful tuning

**InfiniBand:**

Pros:
- Lower latency
- Higher efficiency
- Better for HPC workloads
- Mature RDMA support

Cons:
- Higher cost
- Proprietary (Mellanox/NVIDIA)
- Requires specialized knowledge
- Limited vendor choice

**Recommendation**:
- Ethernet (RoCE) for most AI clusters
- InfiniBand for largest scale or lowest latency requirements

### NVIDIA ConnectX NICs

**ConnectX-7** (Latest generation):
- 400 Gbps (NDR InfiniBand or 400GbE)
- RDMA support
- GPUDirect RDMA (bypass CPU)
- In-network computing (SHARP)
- PCIe Gen 5

**GPUDirect RDMA:**
Direct GPU-to-GPU communication over network without CPU involvement:

```
Traditional Path:
GPU Memory → PCIe → CPU Memory → PCIe → NIC → Network
                                 ↓
                         High latency, CPU overhead

GPUDirect RDMA Path:
GPU Memory → PCIe → NIC → Network
         ↓
  Low latency, no CPU
```

### SHARP (Scalable Hierarchical Aggregation and Reduction Protocol)

SHARP offloads collective operations (all-reduce) to the network switches:

```
Without SHARP:
Each GPU sends to all others
├── N×(N-1) messages
└── High bandwidth usage

With SHARP:
Network switches perform in-network reduction
├── Logarithmic message complexity
└── Lower bandwidth, lower latency
```

### Network Configuration

**NCCL Network Tuning:**

```bash
# Enable GPUDirect RDMA
export NCCL_NET_GDR_LEVEL=5

# Use all available NICs
export NCCL_IB_HCA=mlx5_0,mlx5_1,mlx5_2,mlx5_3

# Enable SHARP (if available)
export NCCL_COLLNET_ENABLE=1

# Tune NCCL algorithms
export NCCL_ALGO=Tree,Ring  # Use both algorithms
export NCCL_PROTO=Simple    # Use simple protocol for large messages

# Set network interface
export NCCL_SOCKET_IFNAME=eth0

# Debug (verbose output)
export NCCL_DEBUG=INFO
```

**Network Topology Awareness:**

```bash
# NCCL can detect topology automatically
# Or specify manually:
export NCCL_TOPO_FILE=/path/to/topology.xml

# Topology file specifies GPU-GPU and GPU-NIC connections
```

Example topology XML:
```xml
<system version="1">
  <cpu numaid="0" affinity="0000ffff">
    <pci busid="0000:00:00.0">
      <gpu dev="0"/>
      <nic dev="mlx5_0"/>
    </pci>
  </cpu>
</system>
```

## NVSwitch and GPU Fabric

### NVLink Architecture

NVLink provides high-bandwidth GPU-to-GPU interconnect:

**NVLink Generations:**

| Generation | GPUs | Bandwidth/Link | Links/GPU | Total BW/GPU |
|------------|------|----------------|-----------|--------------|
| NVLink 2.0 | V100 | 25 GB/s | 6 | 300 GB/s |
| NVLink 3.0 | A100 | 50 GB/s | 12 | 600 GB/s |
| NVLink 4.0 | H100 | 50 GB/s | 18 | 900 GB/s |

**Direct NVLink Connection** (2-4 GPUs):
```
GPU 0 ←→ GPU 1
  ↕        ↕
GPU 2 ←→ GPU 3

Each GPU connected to 3 others via NVLink
Mesh topology for 4 GPUs
```

### NVSwitch

NVSwitch enables full NVLink connectivity for 8+ GPUs:

**NVSwitch Architecture:**

```
         [NVSwitch]
    /    /    |    \    \
   /    /     |     \    \
GPU0 GPU1  GPU2  GPU3  GPU4 ... GPU7

Each GPU has 12 (A100) or 18 (H100) NVLink connections
All connected through NVSwitch
Any GPU can communicate with any other at full NVLink speed
```

**Benefits:**
- Full bisection bandwidth
- Any-to-any connectivity
- All-reduce bandwidth = Single GPU NVLink bandwidth
- Scales to 256 GPUs with NVSwitch systems

**NVSwitch Generations:**

| Version | GPUs | NVLink Gen | Ports | Switch BW |
|---------|------|------------|-------|-----------|
| NVSwitch 1.0 | V100 | 2.0 | 18 | 900 GB/s |
| NVSwitch 2.0 | A100 | 3.0 | 36 | 7.2 TB/s |
| NVSwitch 3.0 | H100 | 4.0 | 64 | 13.6 TB/s |

### Multi-Node NVSwitch Fabric

Connect multiple NVSwitch systems:

**DGX SuperPOD** (32 DGX nodes, 256 GPUs):
```
Each DGX: 8 GPUs with NVSwitch (full connectivity within node)
    ↓
Connect DGX nodes via 8×200GbE per node
    ↓
Network fabric provides inter-node connectivity
    ↓
NCCL routes traffic: intra-node via NVLink, inter-node via Ethernet
```

**Multi-tier Architecture:**
```
Tier 1: Intra-node (NVSwitch)
  - 8 GPUs fully connected
  - 600-900 GB/s per GPU
  - <1 μs latency

Tier 2: Inter-node (Ethernet/IB)
  - Node-to-node communication
  - 1.6-3.2 Tbps per node
  - 5-10 μs latency

Tier 3: Inter-rack (Spine switches)
  - Rack-to-rack communication
  - High bisection bandwidth
  - 10-20 μs latency
```

## NVIDIA DGX Systems

### DGX A100

**Specifications:**
- 8× NVIDIA A100 80GB SXM
- 6× NVSwitch (2nd gen)
- 2× AMD EPYC 7742 (128 cores total)
- 2TB RAM
- 30TB NVMe SSD (15×2TB)
- 8× 200GbE NVIDIA ConnectX-6 NICs
- Dual redundant power supplies (6.5 kW)

**Internal Architecture:**
```
        [NVSwitch 0]  [NVSwitch 1]  [NVSwitch 2]
        [NVSwitch 3]  [NVSwitch 4]  [NVSwitch 5]
             |  |  |  |  |  |  |  |
        [A100][A100][A100][A100][A100][A100][A100][A100]
             |                              |
        [CPU 0]                         [CPU 1]
             |                              |
        [RAM 1TB]                      [RAM 1TB]
             |                              |
        [NVMe Storage]              [Network 8×200GbE]
```

**Use Cases:**
- Training models up to 1T parameters (with multi-node)
- Distributed deep learning
- High-performance inference
- AI research

**Performance:**
- 5 PFLOPS FP16 (with sparsity)
- 2.5 PFLOPS FP16 (dense)
- 10 PFLOPS INT8

### DGX H100

**Specifications:**
- 8× NVIDIA H100 80GB SXM5
- NVSwitch 3rd generation
- 2× Intel Xeon Platinum 8480C (112 cores)
- 2TB RAM
- 30TB NVMe SSD
- 8× 400GbE ConnectX-7 NICs
- 10.2 kW power

**Improvements over DGX A100:**
- 3× faster training (FP8)
- 30× faster inference (with Transformer Engine)
- 2× NVLink bandwidth (900 GB/s per GPU)
- 2× network bandwidth (400GbE vs 200GbE)

**Performance:**
- 32 PFLOPS FP8 (with sparsity)
- 16 PFLOPS FP8 (dense)
- 8 PFLOPS FP16

### DGX GB200

**Next Generation** (Upcoming):
- Grace-Blackwell architecture
- 8× B200 GPUs + 2× Grace CPUs
- Even higher performance
- Expected 2024-2025

## BasePOD Reference Architecture

NVIDIA BasePOD is a validated reference design for scalable GPU clusters.

### BasePOD Components

**Compute:**
- DGX systems (A100 or H100)
- 4, 8, 16, or 32 DGX nodes
- Standard configurations for validation

**Network:**
- NVIDIA Quantum-2 InfiniBand switches (400Gbps)
- Or NVIDIA Spectrum-4 Ethernet switches (400GbE)
- Fat-tree topology
- 1:1 oversubscription (full bisection bandwidth)

**Storage:**
- DDN EXAScaler or VAST Data systems
- NVMe-based parallel filesystem
- 100+ GB/s aggregate bandwidth
- Multi-petabyte capacity

**Management:**
- NVIDIA Base Command Manager
- Monitoring and job scheduling
- Integrated with Kubernetes or Slurm

### BasePOD Configurations

**BasePOD 4** (Smallest):
- 4× DGX A100/H100
- 32 GPUs
- 1-2 spine switches
- 4 leaf switches
- Storage: 1 PB+
- Power: ~60 kW

**BasePOD 8**:
- 8× DGX A100/H100
- 64 GPUs
- 2-4 spine switches
- 8 leaf switches
- Storage: 2 PB+
- Power: ~120 kW

**BasePOD 16**:
- 16× DGX A100/H100
- 128 GPUs
- 4-8 spine switches
- 16 leaf switches
- Storage: 4 PB+
- Power: ~240 kW

**SuperPOD** (Largest):
- 32+ DGX systems
- 256+ GPUs
- Large-scale network fabric
- 10+ PB storage
- 500+ kW power

### Network Design for BasePOD

**Fat-Tree Topology:**

```
             [Spine Layer]
          (4-8 spine switches)
         /    /    |    \    \
        /    /     |     \    \
    [Leaf Layer]
  (16 leaf switches, 2 per rack)
    |  |  |  |  |  |  |  |  |  |
  [DGX][DGX][DGX]...[DGX] (32 nodes)
```

**Connectivity:**
- Each DGX: 8× 400GbE uplinks (3.2 Tbps)
- Each leaf switch: 64× 400GbE ports
- Each spine switch: 128× 400GbE ports
- No oversubscription (1:1)

**Bandwidth:**
- Intra-rack: NVLink + local switch
- Inter-rack: Through spine switches
- Storage: Dedicated network or shared fabric

## Storage Considerations

### Storage Requirements for AI

**Training Data:**
- Large datasets (TB to PB scale)
- High sequential read throughput
- Moderate IOPS

**Checkpoints:**
- Frequent writes during training
- Large files (10-100 GB per checkpoint)
- High write throughput needed

**Inference:**
- Model weights (GB to 100s of GB)
- Low latency reads
- High IOPS for model serving

### Storage Architecture

**Parallel Filesystem** (Training):
```
Example: DDN EXAScaler, VAST Data, WekaFS

Architecture:
┌─────────────────────────────────┐
│     Parallel File System         │
│  (metadata + data servers)       │
└─────────────────────────────────┘
              ↓
    [High-speed network]
              ↓
┌─────────────────────────────────┐
│    Compute Nodes (DGX)          │
│  Mount shared filesystem         │
└─────────────────────────────────┘

Performance:
- 100+ GB/s aggregate throughput
- Millions of IOPS
- Scales with more servers
```

**Object Storage** (Archive):
```
Example: S3, Ceph, MinIO

Use cases:
- Dataset archive
- Long-term checkpoint storage
- Model registry

Cost-effective, scales to exabytes
```

**Local NVMe** (Fast scratch):
```
Each DGX has 30TB NVMe:
- Stage datasets locally before training
- Fast checkpoint writes
- Temporary file operations

100+ GB/s per node
```

### Storage Best Practices

1. **Tiered Storage**:
   - Hot: NVMe (local or fabric)
   - Warm: Parallel filesystem
   - Cold: Object storage

2. **Data Loading Optimization**:
   - Pre-stage datasets to local NVMe
   - Use data loaders with prefetching
   - Cache frequently accessed data

3. **Checkpoint Strategy**:
   - Write checkpoints to fast storage
   - Asynchronously copy to long-term storage
   - Keep only recent N checkpoints on fast storage

4. **Bandwidth Planning**:
```
64 GPUs training ResNet-50:
- Batch size: 32 per GPU
- Images: 224×224×3 bytes = 150 KB
- Total per step: 64 × 32 × 150 KB = 307 MB
- At 100 steps/sec: 30.7 GB/s needed

Add 50% margin: 46 GB/s aggregate storage bandwidth
```

## Power and Cooling Infrastructure

### Power Requirements

**DGX A100:**
- Max power: 6.5 kW per system
- Typical: 5-6 kW sustained
- 8× DGX rack: 52 kW
- Add 20% for networking, storage: 62 kW/rack

**DGX H100:**
- Max power: 10.2 kW per system
- Typical: 8-9 kW sustained
- 8× DGX rack: 81 kW
- Add networking, storage: 97 kW/rack

**Total Cluster (32 DGX H100):**
- 32 systems: 326 kW
- Networking: 20 kW
- Storage: 40 kW
- Overhead (UPS, cooling): 100 kW
- Total: ~500 kW (0.5 MW)

**Power Distribution:**
```
Utility Power
    ↓
PDU (Power Distribution Unit)
    ↓
UPS (Uninterruptible Power Supply)
    ↓
Rack PDUs
    ↓
Individual DGX systems
```

### Cooling Requirements

**Air Cooling:**
- Traditional approach
- 3:1 air:kW ratio (62 kW rack needs 186 CFM)
- Limited to ~40-50 kW per rack
- Higher PUE (1.4-1.6)

**Direct Liquid Cooling:**
- Coolant to GPU cold plates
- 80-90% of heat removed by liquid
- Supports 100+ kW per rack
- Lower PUE (1.1-1.2)
- Used in DGX H100 at scale

**Immersion Cooling:**
- Servers submerged in dielectric fluid
- Highest cooling density
- 200+ kW per tank
- Lowest PUE (<1.1)
- Higher upfront cost

**Cooling Calculations:**
```
32 DGX H100 cluster:
- Heat output: 500 kW
- Air cooling: 500 kW × 3.41 BTU/W = 1.7M BTU/hr
  Need: ~140 tons of cooling capacity

- Liquid cooling: 400 kW via liquid (80%)
  Air cooling for remaining 100 kW
  Need: ~30 tons of cooling capacity
  Significant savings!
```

### Data Center Requirements

**Space:**
- 4 racks for 32 DGX systems
- 2-4 racks for network switches
- 2-4 racks for storage
- Total: 8-12 racks (~1000 sq ft)

**Power:**
- 500 kW for compute
- 100 kW for cooling (PUE 1.2)
- 600 kW total from utility

**Network:**
- Redundant internet uplinks (10-100 Gbps)
- Connectivity to cloud (for hybrid)

**Environmental:**
- Temperature: 18-27°C (64-80°F)
- Humidity: 40-60% RH
- Fire suppression
- Physical security

## Summary

Key GPU cluster design takeaways:

1. **Network is critical**: 400 GbE per node minimum, GPUDirect RDMA essential
2. **NVSwitch enables scaling**: Full GPU-GPU bandwidth within nodes
3. **Use reference architectures**: DGX BasePOD provides validated designs
4. **Storage bandwidth matters**: 100+ GB/s needed for large clusters
5. **Plan for power and cooling**: 10 kW per GPU node, liquid cooling for density
6. **Design for growth**: Start with spine-leaf topology that scales

## Hands-on Exercise

Design a GPU cluster:

**Scenario**: ML platform for 10 teams, training models up to 100B params

**Requirements**:
- 64 GPUs minimum
- High availability (no single point of failure)
- Scalable to 256 GPUs
- 2 PB storage
- Budget: $3M

**TODO: Create design document with:**
1. Hardware specifications
2. Network topology diagram
3. Storage architecture
4. Power and cooling requirements
5. Rack layout
6. Cost breakdown
7. Scaling plan

## Further Reading

- NVIDIA DGX Documentation: https://docs.nvidia.com/dgx/
- NVIDIA BasePOD Design Guide: https://docs.nvidia.com/base-pod/
- NVIDIA Networking Guide: https://docs.nvidia.com/networking/
- GPU Cluster Best Practices: https://www.nvidia.com/en-us/data-center/dgx-superpod/

---

**Congratulations!** You've completed Module 203: Advanced GPU Computing and Optimization. You now have comprehensive knowledge of GPU programming, architecture, profiling, multi-GPU strategies, virtualization, monitoring, and cluster design for AI infrastructure.

**Next Steps:**
- Complete the hands-on labs
- Take the module quiz
- Apply these concepts in your projects
- Proceed to Module 204: Model Optimization and Serving
