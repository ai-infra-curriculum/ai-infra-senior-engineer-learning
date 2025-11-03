# Lecture 02: GPU Architecture Deep Dive

## Learning Objectives

By the end of this lecture, you will be able to:

- Architect ML workloads that leverage GPU architectural features including Streaming Multiprocessors, Tensor Cores, and memory hierarchies for optimal performance
- Design memory access patterns that exploit the multi-level GPU memory hierarchy (registers, shared memory, L1/L2 cache, HBM) to minimize memory latency
- Evaluate GPU selection criteria based on architectural differences between NVIDIA GPU generations (Volta, Turing, Ampere, Hopper, Blackwell) for specific ML workloads
- Implement Tensor Core utilization strategies in deep learning models to achieve 2-10x speedups through mixed precision training
- Configure warp scheduling and occupancy parameters to balance SM utilization, register pressure, and memory bandwidth for different kernel types
- Analyze roofline models to identify whether ML workloads are compute-bound or memory-bound and apply appropriate optimization strategies
- Design training pipelines that account for PCIe bandwidth limitations between CPU and GPU memory to minimize data transfer bottlenecks
- Troubleshoot common GPU architecture-related performance issues including warp divergence, bank conflicts, and insufficient occupancy

## Table of Contents
1. [Introduction to GPU Architecture](#introduction-to-gpu-architecture)
2. [GPU vs CPU Architecture](#gpu-vs-cpu-architecture)
3. [NVIDIA GPU Generations](#nvidia-gpu-generations)
4. [Streaming Multiprocessors (SMs)](#streaming-multiprocessors-sms)
5. [Memory Architecture](#memory-architecture)
6. [Ampere Architecture](#ampere-architecture)
7. [Hopper Architecture](#hopper-architecture)
8. [Compute Capability](#compute-capability)
9. [Performance Considerations](#performance-considerations)

## Introduction to GPU Architecture

Understanding GPU architecture is essential for optimizing ML workloads and making informed infrastructure decisions. This lecture explores the internal architecture of NVIDIA GPUs, with focus on Ampere (A100, A30, A10) and Hopper (H100, H200) generations that power modern AI infrastructure.

### Why Architecture Matters

1. **Performance Optimization**: Understanding hardware enables better code optimization
2. **Resource Planning**: Knowing capabilities helps size GPU infrastructure correctly
3. **Debugging**: Architecture knowledge aids in diagnosing performance issues
4. **Feature Utilization**: Leverage architecture-specific features (Tensor Cores, MIG)
5. **Cost Optimization**: Choose appropriate GPU SKUs based on workload requirements

### GPU Design Philosophy

GPUs are designed for **throughput** over **latency**:

- Thousands of lightweight threads vs. few heavyweight threads (CPU)
- Maximize parallel execution
- Hide memory latency with massive multithreading
- Optimize for data-parallel workloads

## GPU vs CPU Architecture

### Architectural Differences

**CPU Architecture:**
- Few cores (8-64 typically) with high clock speeds (3-5 GHz)
- Large caches (MB per core)
- Complex control logic and branch prediction
- Optimized for latency: get one task done fast
- Out-of-order execution, speculative execution
- Good for serial, complex control flow

**GPU Architecture:**
- Thousands of cores (5,000-20,000+) with lower clock speeds (1-2 GHz)
- Smaller caches, larger memory bandwidth
- Simple control logic
- Optimized for throughput: get many tasks done overall
- In-order execution within warps
- Excellent for parallel, regular workloads

### Die Area Comparison

```
CPU Die:
┌─────────────────────────┐
│  Large Caches (40%)     │
│─────────────────────────│
│  Control Logic (30%)    │
│─────────────────────────│
│  ALUs (20%)             │
│─────────────────────────│
│  DRAM Controllers (10%) │
└─────────────────────────┘

GPU Die:
┌─────────────────────────┐
│  ALUs (70%)             │
│─────────────────────────│
│  Caches (15%)           │
│─────────────────────────│
│  Control Logic (10%)    │
│─────────────────────────│
│  DRAM Controllers (5%)  │
└─────────────────────────┘
```

### Memory Bandwidth

- **CPU**: ~100 GB/s (DDR5)
- **GPU**: ~1,500-3,000 GB/s (HBM2/HBM3)

GPUs achieve 10-30x higher memory bandwidth, critical for ML workloads.

### Comparison Table

| Feature | CPU | GPU |
|---------|-----|-----|
| Cores | 8-64 | 5,000-20,000 |
| Clock Speed | 3-5 GHz | 1-2 GHz |
| Memory | 128-512 GB DDR5 | 40-80 GB HBM |
| Memory BW | ~100 GB/s | 1,500-3,000 GB/s |
| FP32 TFLOPS | 1-2 | 19-60 |
| FP16 TFLOPS | - | 150-1,000 |
| INT8 TOPS | - | 300-2,000 |
| Power | 150-300W | 250-700W |
| Best For | Serial tasks | Parallel tasks |

## NVIDIA GPU Generations

### Historical Evolution

1. **Tesla (2006)**: First CUDA-capable GPUs
2. **Fermi (2010)**: Introduced ECC memory, better double precision
3. **Kepler (2012)**: Dynamic parallelism, Hyper-Q
4. **Maxwell (2014)**: Power efficiency improvements
5. **Pascal (2016)**: HBM2 memory, NVLink
6. **Volta (2017)**: **Tensor Cores introduced** - game changer for AI
7. **Turing (2018)**: RT cores for ray tracing, improved Tensor Cores
8. **Ampere (2020)**: 3rd gen Tensor Cores, MIG, sparsity acceleration
9. **Hopper (2022)**: Transformer Engine, 4th gen Tensor Cores, FP8

### Key Innovations by Generation

**Volta (V100) - 2017:**
- First-generation Tensor Cores (FP16)
- 640 Tensor Cores
- 125 TFLOPS FP16 (with Tensor Cores)
- 300W TDP

**Ampere (A100) - 2020:**
- 3rd-generation Tensor Cores (FP16, TF32, BF16, FP64, INT8)
- 432 Tensor Cores
- 312 TFLOPS FP16 (with Tensor Cores)
- Structured sparsity (2:4 sparsity pattern)
- Multi-Instance GPU (MIG)
- 400W TDP

**Hopper (H100) - 2022:**
- 4th-generation Tensor Cores with FP8 support
- 528 Tensor Cores
- 1,000 TFLOPS FP8 (with Tensor Cores)
- Transformer Engine for mixed FP8/FP16 precision
- New DPX instructions for dynamic programming
- 700W TDP (SXM5)

### Compute vs. Data Center GPUs

**Gaming/Consumer GPUs** (RTX series):
- Consumer market focus
- Graphics features (RT cores)
- No ECC memory
- Limited double precision
- Lower price point

**Data Center GPUs** (Tesla/A-series/H-series):
- AI and HPC focus
- ECC memory
- High double precision performance
- MIG support (A100, H100)
- NVLink support
- Higher reliability and support
- Significantly more expensive

## Streaming Multiprocessors (SMs)

The SM is the fundamental building block of GPU architecture.

### SM Components

Each SM contains:
- **CUDA Cores**: Standard FP32 and INT32 processing units
- **Tensor Cores**: Specialized matrix multiplication units
- **Special Function Units (SFUs)**: Transcendental functions (sin, cos, exp)
- **Load/Store Units (LD/ST)**: Memory operations
- **Warp Schedulers**: Schedule warps for execution
- **Register File**: Fast storage for thread data
- **Shared Memory/L1 Cache**: Configurable fast memory
- **Texture Units**: Texture sampling operations

### Warp Scheduling

A warp is 32 threads that execute in lockstep:

```
SM Execution:
┌─────────────────────────┐
│ Warp Scheduler          │
│   ↓                     │
│ Warp 0: [32 threads]    │ → CUDA Cores
│ Warp 1: [32 threads]    │ → Tensor Cores
│ Warp 2: [32 threads]    │ → LD/ST Units
│ Warp 3: [32 threads]    │ → SFUs
│   ...                   │
│ Warp N: [32 threads]    │
└─────────────────────────┘
```

**Warp Scheduler**: Selects ready warps for execution each cycle
- Multiple warp schedulers per SM
- Hide memory latency by switching between warps
- Zero-overhead context switching

### Occupancy

**Occupancy** = Active warps / Maximum warps per SM

Factors limiting occupancy:
1. **Registers**: Each thread's register usage
2. **Shared Memory**: Per-block shared memory usage
3. **Block Size**: Threads per block
4. **Hardware Limits**: Maximum warps/blocks per SM

Example calculation:
```
SM has:
- 64K 32-bit registers
- 48KB shared memory
- Max 64 warps (2048 threads)
- Max 32 blocks

Kernel uses:
- 40 registers/thread
- 16KB shared memory/block
- 256 threads/block = 8 warps/block

Register limit: 64K registers / 40 registers/thread = 1,638 threads = 51 warps
Shared memory limit: 48KB / 16KB = 3 blocks = 24 warps
Block limit: 32 blocks = 32 * 8 = 256 warps (not limiting)

Occupancy = min(51, 24, 64) / 64 = 24 / 64 = 37.5%
```

### Occupancy Calculator

NVIDIA provides tools to calculate occupancy:

```bash
# Use CUDA Occupancy Calculator (spreadsheet)
# Or use runtime API

int numBlocks;
cudaOccupancyMaxActiveBlocksPerMultiprocessor(
    &numBlocks,
    myKernel,
    threadsPerBlock,
    sharedMemPerBlock
);

float occupancy = (numBlocks * threadsPerBlock / 32.0f) / maxWarpsPerSM;
```

## Memory Architecture

### Memory Hierarchy Details

**Registers:**
- 32-bit registers
- ~65K registers per SM (Ampere)
- Fastest access (1 cycle)
- Private to each thread
- Automatic allocation for local variables

**Shared Memory:**
- 164KB per SM (A100, configurable)
- ~20 cycles latency
- Shared across threads in a block
- Software-managed cache
- Organized into banks (32 banks, 4 bytes each)

**L1 Cache:**
- Unified with shared memory (configurable split)
- Per-SM cache
- Caches local and global memory accesses

**L2 Cache:**
- 40MB (A100), 50MB (H100)
- Shared across all SMs
- ~200 cycles latency
- Caches global memory

**Global Memory (HBM):**
- 40GB (A100 40GB), 80GB (A100 80GB), 80GB (H100)
- ~400-800 cycles latency
- High bandwidth: 1.6 TB/s (A100), 3.0 TB/s (H100)
- Persistent across kernel launches

### HBM (High Bandwidth Memory)

HBM achieves high bandwidth through:
- Wide bus: 5,120-bit (vs. 64-bit DDR)
- Stacked DRAM dies
- Through-silicon vias (TSVs)
- Close proximity to GPU die (interposer)

**HBM2e** (A100):
- 5 HBM2e stacks
- 1,555 GB/s bandwidth (40GB model)
- 1,935 GB/s bandwidth (80GB model)

**HBM3** (H100):
- 5 HBM3 stacks
- 3,000 GB/s bandwidth
- Higher density, lower power

### Memory Coalescing

**Coalesced Access** (Efficient):
```
Warp threads:    [0  1  2  3  4  5  6  7 ... 31]
Access addresses:[0  4  8  12 16 20 24 28 ... 124]
                 └────────────────────────────────┘
                 Single 128-byte memory transaction
```

**Uncoalesced Access** (Inefficient):
```
Warp threads:    [0  1  2  3  4  5  6  7 ... 31]
Access addresses:[0  1024 2048 3072 4096 ...]
                 ↓  ↓    ↓    ↓    ↓
                 32 separate memory transactions!
```

Coalescing rules:
- Threads in a warp should access consecutive addresses
- Alignment matters: align to 32, 64, or 128 bytes
- Access pattern should be linear or uniform

### Bank Conflicts in Shared Memory

Shared memory is organized into 32 banks:

**No Bank Conflict** (Good):
```cpp
__shared__ float data[128];
float value = data[threadIdx.x];  // Each thread accesses different bank
```

**Bank Conflict** (Bad):
```cpp
__shared__ float data[128];
float value = data[threadIdx.x * 2];  // Half the banks used, 2-way conflict
```

**Broadcast** (OK):
```cpp
__shared__ float data[128];
float value = data[0];  // All threads read same address, broadcast
```

## Ampere Architecture

Ampere (GA100 die) introduced significant improvements for AI workloads.

### A100 Specifications

**Full GA100 Die:**
- 8 GPCs (Graphics Processing Clusters)
- 8 TPCs per GPC (Texture Processing Clusters)
- 2 SMs per TPC
- **128 SMs total** (full die, A100 has 108 enabled)
- 64 FP32 CUDA cores per SM
- 4 Tensor Cores per SM
- 40 or 80 GB HBM2e

**A100 80GB Configuration:**
- 108 SMs (6,912 CUDA cores)
- 432 3rd-gen Tensor Cores
- 40MB L2 cache
- 1,555 GB/s memory bandwidth (40GB) or 1,935 GB/s (80GB)
- 400W TDP

### Ampere SM Architecture

Each Ampere SM has:
- 64 FP32 CUDA cores
- 32 FP64 CUDA cores
- 4 Tensor Cores (3rd generation)
- 4 warp schedulers
- 128 KB L1/shared memory (configurable)
- 256 KB register file

```
Ampere SM (Simplified):
┌─────────────────────────────────────┐
│ Warp Scheduler 0 | Warp Scheduler 1 │
├─────────────────────────────────────┤
│ [16 FP32] [4 LD/ST] [Tensor Core]   │
│ [16 FP32] [4 LD/ST] [Tensor Core]   │
│ [16 FP32] [4 LD/ST] [Tensor Core]   │
│ [16 FP32] [4 LD/ST] [Tensor Core]   │
├─────────────────────────────────────┤
│ Register File (256 KB)              │
├─────────────────────────────────────┤
│ L1 Cache / Shared Memory (128 KB)  │
└─────────────────────────────────────┘
```

### 3rd Generation Tensor Cores

Ampere Tensor Cores support:
- **FP16** (half precision)
- **BF16** (bfloat16 - better range than FP16)
- **TF32** (TensorFloat-32 - FP32 replacement for Tensor Cores)
- **FP64** (double precision, for HPC)
- **INT8/INT4** (inference and training)

**TF32 Format:**
- 19 bits total: 1 sign, 8 exponent, 10 mantissa
- Same range as FP32 (8-bit exponent)
- Less precision than FP32 (10 vs 23 mantissa bits)
- Automatic in PyTorch/TensorFlow for GEMM operations
- No code changes required

```python
# TF32 is enabled by default in PyTorch 1.7+
import torch
# To disable TF32 (if needed):
# torch.backends.cuda.matmul.allow_tf32 = False
```

**Structured Sparsity:**
- 2:4 sparsity pattern: 2 values zero out of every 4
- 2x speedup on sparse models
- Requires model pruning to 2:4 pattern

```python
# Example sparse pattern
Dense:  [1.2, 3.4, 0.5, 2.1, 4.5, 0.8, 1.1, 3.2]
Sparse: [1.2, 3.4, 0.0, 0.0, 4.5, 0.8, 0.0, 0.0]  # 2:4 pattern
        └────────┘       └────────┘
        2 non-zero       2 non-zero
```

### Multi-Instance GPU (MIG)

MIG allows partitioning a single A100 into up to **7 independent GPU instances**.

**MIG Configurations:**
- 1x 7g.40gb (full GPU)
- 2x 3g.20gb
- 3x 2g.10gb
- 7x 1g.5gb
- Mixed configurations (e.g., 1x 3g + 2x 2g)

Each MIG instance has:
- Dedicated SMs
- Dedicated memory slice
- Dedicated L2 cache
- QoS and fault isolation

**Use Cases:**
- Multi-tenant GPU sharing
- Batch inference workloads
- Development/testing environments
- Resource isolation for different teams

```bash
# Configure MIG on A100
nvidia-smi -i 0 -mig 1  # Enable MIG mode

# Create MIG instances
nvidia-smi mig -cgi 9,9  # Create 2x 3g.20gb instances

# List instances
nvidia-smi mig -lgi
```

### NVLink 3.0

A100 features NVLink 3.0:
- 12 NVLink links per GPU
- 600 GB/s total bandwidth (bidirectional)
- 50 GB/s per link
- Up to 8 GPUs directly connected in DGX A100
- Enables fast multi-GPU communication

## Hopper Architecture

Hopper (GH100) is NVIDIA's latest data center GPU architecture, optimized for large language models and transformers.

### H100 Specifications

**Full GH100 Die:**
- 144 SMs (H100 SXM5 has 132 enabled)
- 16,896 CUDA cores (FP32)
- 528 4th-gen Tensor Cores
- 50MB L2 cache
- 80GB HBM3
- 3.0 TB/s memory bandwidth
- 700W TDP (SXM5), 350W (PCIe)

### Hopper SM Architecture

Each Hopper SM has:
- 128 FP32 CUDA cores (2x Ampere)
- 64 FP64 CUDA cores
- 4 Tensor Cores (4th generation)
- 4 warp schedulers
- 256 KB register file
- 256 KB L1/shared memory (2x Ampere)

### 4th Generation Tensor Cores with FP8

Hopper introduces **FP8** support:

**FP8 Formats:**
1. **E4M3** (Training): 1 sign, 4 exponent, 3 mantissa bits
2. **E5M2** (Inference): 1 sign, 5 exponent, 2 mantissa bits

**Performance:**
- 2x throughput vs. FP16/BF16
- H100: 1,000 TFLOPS FP8 (vs. 500 TFLOPS FP16)

**Transformer Engine:**
- Automatic FP8/FP16 mixed precision
- Per-layer precision selection
- Scaling factor management
- Minimizes accuracy loss

```python
# Using Transformer Engine in PyTorch
import transformer_engine.pytorch as te

# Replace linear layers with TE layers
linear = te.Linear(768, 3072, params_dtype=torch.float16)

# Automatic FP8 during forward/backward
with te.fp8_autocast(enabled=True):
    output = linear(input)
```

### DPX Instructions

New DPX (Dynamic Programming) instructions accelerate:
- Genomics algorithms (Smith-Waterman)
- Route optimization
- Graph analytics
- 7x faster than A100 for Floyd-Warshall algorithm

### Thread Block Clusters

New programming model:
- Groups of thread blocks that cooperate
- Share distributed shared memory
- Asynchronous memory copies between blocks

```cpp
// Thread Block Cluster (conceptual example)
__global__ void __cluster_dims__(2, 2, 1) clusterKernel() {
    // This kernel runs with 2x2 = 4 blocks per cluster
    // Blocks can cooperate via distributed shared memory
}
```

### NVLink 4.0 and NVSwitch

H100 features NVLink 4.0:
- 18 NVLink links per GPU
- 900 GB/s total bandwidth (bidirectional)
- 50 GB/s per link
- NVSwitch 3.0: 64 GPUs fully connected

### Confidential Computing

H100 supports TEE (Trusted Execution Environment):
- Encrypted memory
- Secure boot
- Remote attestation
- Protects sensitive data during computation

## Compute Capability

Compute capability defines the feature set of a GPU architecture.

### Compute Capability Versions

| Capability | Architecture | Example GPUs | Key Features |
|------------|--------------|--------------|--------------|
| 7.0 | Volta | V100 | 1st-gen Tensor Cores, NVLink 2.0 |
| 7.5 | Turing | RTX 2080, T4 | 2nd-gen Tensor Cores, INT8 Tensor Cores |
| 8.0 | Ampere | A100 | 3rd-gen Tensor Cores, MIG, TF32, BF16 |
| 8.6 | Ampere | RTX 3090, A10 | Consumer Ampere features |
| 9.0 | Hopper | H100 | 4th-gen Tensor Cores, FP8, Thread Block Clusters |

### Feature Support by Compute Capability

**Tensor Cores:**
- 7.0+: FP16 Tensor Cores
- 7.5+: INT8 Tensor Cores
- 8.0+: TF32, BF16 Tensor Cores
- 9.0+: FP8 Tensor Cores

**Precision Support:**
- All: FP32, FP64
- 7.0+: FP16 (half precision)
- 8.0+: TF32, BF16
- 9.0+: FP8 (E4M3, E5M2)

**Features:**
- 7.0+: Independent thread scheduling
- 8.0+: MIG (Multi-Instance GPU) on A100/A30
- 9.0+: Thread Block Clusters, DPX instructions

### Checking Compute Capability

```bash
# Using nvidia-smi
nvidia-smi --query-gpu=compute_cap --format=csv

# Using CUDA sample
cd /usr/local/cuda/samples/1_Utilities/deviceQuery
make && ./deviceQuery
```

```cpp
// From CUDA code
int device;
cudaGetDevice(&device);

cudaDeviceProp prop;
cudaGetDeviceProperties(&prop, device);

printf("Compute Capability: %d.%d\n", prop.major, prop.minor);
```

```python
# From PyTorch
import torch
print(torch.cuda.get_device_capability(0))  # Returns (major, minor)
```

### Compiling for Specific Architectures

```bash
# Compile for specific compute capability
nvcc -arch=sm_80 -o program program.cu  # Ampere A100

# Compile for multiple architectures (fat binary)
nvcc -gencode arch=compute_70,code=sm_70 \
     -gencode arch=compute_80,code=sm_80 \
     -gencode arch=compute_90,code=sm_90 \
     -o program program.cu

# PTX for forward compatibility
nvcc -gencode arch=compute_80,code=compute_80 -o program program.cu
```

```python
# PyTorch: compile for specific architectures
# Set environment variable before installing
export TORCH_CUDA_ARCH_LIST="7.0;8.0;9.0"
pip install torch
```

## Performance Considerations

### Understanding Performance Metrics

**FLOPS (Floating Point Operations Per Second):**
- FP32: 19.5 TFLOPS (A100), 60 TFLOPS (H100)
- FP16/BF16 Tensor Core: 312 TFLOPS (A100), 500 TFLOPS (H100)
- FP8 Tensor Core: N/A (A100), 1,000 TFLOPS (H100)

**Memory Bandwidth:**
- A100: 1.6-1.9 TB/s
- H100: 3.0 TB/s
- Critical for memory-bound operations

**Roofline Model:**
```
Performance = min(Peak FLOPS, Memory Bandwidth × Arithmetic Intensity)

Arithmetic Intensity = FLOPs / Bytes transferred
```

### Memory vs. Compute Bound

**Compute-Bound Operations:**
- Matrix multiplication (large matrices)
- Convolutions (large kernel sizes)
- Limited by FLOPS

**Memory-Bound Operations:**
- Element-wise operations (ReLU, sigmoid)
- Normalization layers (BatchNorm, LayerNorm)
- Small matrix operations
- Limited by memory bandwidth

Example: Analyzing ReLU
```
ReLU: y = max(0, x)

Per element:
- 1 FP32 operation (comparison/max)
- 2 memory accesses (read x, write y) = 8 bytes

Arithmetic Intensity = 1 FLOP / 8 bytes = 0.125 FLOP/byte

A100 peak: 19.5 TFLOPS / 1,555 GB/s = 12.5 FLOP/byte

0.125 << 12.5, so ReLU is heavily memory-bound!
```

### Optimizing for Architecture

**For Memory-Bound Ops:**
1. Fuse operations to reduce memory traffic
2. Use in-place operations when possible
3. Increase arithmetic intensity
4. Optimize memory access patterns

**For Compute-Bound Ops:**
1. Use Tensor Cores (mixed precision)
2. Increase batch size or problem size
3. Optimize for warp execution
4. Minimize control divergence

### GPU Selection Guide

**Inference Workloads:**
- T4 (Turing): Cost-effective, INT8 support
- A10 (Ampere): Balance of performance and cost
- L4 (Ada): Latest architecture, efficient

**Training Small Models (<1B params):**
- RTX 3090/4090: Cost-effective for research
- A10/A30: Data center reliability
- L40: High memory bandwidth

**Training Large Models (>1B params):**
- A100 40GB/80GB: Excellent all-around
- H100: Best performance, large models
- H200: More memory (141GB) for huge models

**Multi-GPU Training:**
- Prefer SXM form factor over PCIe
- NVLink essential for good scaling
- DGX systems for best performance

### Future Trends

**Upcoming Architectures:**
- Blackwell (2024): Next generation after Hopper
- Increased memory capacity
- Higher bandwidth and compute
- Better energy efficiency

**Technology Trends:**
- Lower precision formats (FP4, INT4)
- Larger memory capacity (HBM3e)
- Optical interconnects
- Chiplet-based designs

## Summary

Key takeaways from GPU architecture:

1. **SM is the fundamental unit**: Understanding SMs helps optimize occupancy
2. **Memory hierarchy matters**: Optimize access patterns for coalescing
3. **Tensor Cores are essential**: Use mixed precision for ML workloads
4. **Architecture-specific features**: MIG (Ampere), FP8 (Hopper) enable new use cases
5. **Know your workload**: Memory-bound vs. compute-bound drives optimization strategy

## Hands-on Exercise

Query your GPU architecture:
```bash
# Get detailed GPU information
nvidia-smi -q

# Query specific properties
nvidia-smi --query-gpu=name,compute_cap,memory.total,memory.free,clocks.sm,clocks.mem --format=csv

# Run deviceQuery sample
/usr/local/cuda/samples/1_Utilities/deviceQuery/deviceQuery
```

## Next Steps

- Profile applications to understand compute vs. memory bottlenecks
- Experiment with mixed precision training (TF32, BF16)
- Learn about CUDA libraries that leverage Tensor Cores
- Explore MIG configuration on A100 GPUs

## Further Reading

- NVIDIA Ampere Architecture Whitepaper: https://www.nvidia.com/content/PDF/nvidia-ampere-ga-102-gpu-architecture-whitepaper-v2.pdf
- NVIDIA Hopper Architecture Whitepaper: https://resources.nvidia.com/en-us-tensor-core
- CUDA C Programming Guide - Hardware Implementation: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#hardware-implementation

---

**Next Lecture**: CUDA Libraries for ML - cuDNN, cuBLAS, TensorRT
