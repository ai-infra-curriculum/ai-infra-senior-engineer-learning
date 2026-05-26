# Module 203: GPU Computing and Optimization - Knowledge Quiz

## Instructions

- 25 questions covering all module topics
- Multiple choice and short answer
- Time limit: 60 minutes (recommended)
- Passing score: 80% (20/25 correct)
- Answers provided at the end

---

## Section 1: CUDA Fundamentals (Questions 1-5)

**Question 1:** In CUDA, what is a warp?

A) A group of 16 threads that execute in lockstep  
B) A group of 32 threads that execute in lockstep  
C) A group of 64 threads that execute independently  
D) A single thread with special privileges

**Question 2:** Which CUDA memory type has the fastest access latency?

A) Global memory  
B) Shared memory  
C) Registers  
D) Constant memory

**Question 3:** What is the maximum number of threads per block on modern GPUs (compute capability 7.0+)?

A) 512  
B) 768  
C) 1024  
D) 2048

**Question 4:** In this code, what causes warp divergence?

```cuda
__global__ void kernel(int* data, int N) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < N) {
        if (data[idx] % 2 == 0) {
            data[idx] *= 2;
        } else {
            data[idx] *= 3;
        }
    }
}
```

A) The boundary check `idx < N`  
B) The modulo operation `data[idx] % 2`  
C) The if-else branches based on even/odd  
D) No divergence occurs

**Question 5:** For optimal memory coalescing, threads in a warp should access memory that is:

A) Random and scattered  
B) Consecutive and aligned  
C) In reverse order  
D) From different memory segments

---

## Section 2: GPU Architecture (Questions 6-10)

**Question 6:** What is the primary advantage of Tensor Cores over regular CUDA cores?

A) Higher clock speeds  
B) More memory bandwidth  
C) Specialized matrix multiply-accumulate operations  
D) Better branch prediction

**Question 7:** Which GPU architecture introduced FP8 support?

A) Volta  
B) Ampere  
C) Ada Lovelace  
D) Hopper

**Question 8:** An NVIDIA A100 GPU has how many Streaming Multiprocessors (SMs)?

A) 84  
B) 98  
C) 108  
D) 128

**Question 9:** What is HBM?

A) High Bandwidth Memory - stacked DRAM technology  
B) Hierarchical Buffer Memory - cache architecture  
C) Host Bridge Module - PCIe interface  
D) Hyper-threaded Block Memory - shared memory

**Question 10:** Compute capability determines:

A) GPU clock speed  
B) Available GPU features and instruction sets  
C) Number of GPUs in system  
D) Power consumption limits

---

## Section 3: CUDA Libraries (Questions 11-13)

**Question 11:** Which library would you use for optimizing neural network inference for production deployment?

A) cuDNN  
B) cuBLAS  
C) TensorRT  
D) cuSPARSE

**Question 12:** cuDNN automatically uses Tensor Cores when:

A) You explicitly enable them in code  
B) Using FP16/BF16 precision on supported GPUs  
C) Only on H100 GPUs  
D) Never, Tensor Cores are only for cuBLAS

**Question 13:** What does NCCL provide?

A) Neural network training frameworks  
B) Collective communication operations for multi-GPU training  
C) GPU memory management  
D) Kernel profiling tools

---

## Section 4: GPU Profiling (Questions 14-16)

**Question 14:** Which NVIDIA profiling tool should you use for system-wide timeline analysis showing CPU and GPU activity?

A) Nsight Compute  
B) Nsight Systems  
C) nvprof  
D) nvidia-smi

**Question 15:** If a kernel has low SM utilization (<50%) and low memory bandwidth utilization (<40%), the likely cause is:

A) Memory-bound workload  
B) Compute-bound workload  
C) Insufficient parallelism or small problem size  
D) Thermal throttling

**Question 16:** What is NVTX used for?

A) GPU power management  
B) Adding custom markers to code for profiling  
C) Network communication  
D) Tensor Core acceleration

---

## Section 5: Multi-GPU Strategies (Questions 17-19)

**Question 17:** In Data Parallel training with 8 GPUs, what operation synchronizes gradients across all GPUs?

A) Broadcast  
B) All-reduce  
C) Scatter  
D) Gather

**Question 18:** NVLink provides approximately how much more bandwidth than PCIe Gen3 x16?

A) 2x  
B) 5x  
C) 10x  
D) 20x

**Question 19:** For a model with 10B parameters (20GB in FP16), what is the minimum all-reduce communication per training step in Data Parallel mode?

A) 20 GB  
B) 40 GB  
C) 80 GB  
D) 160 GB

---

## Section 6: GPU Virtualization (Questions 20-22)

**Question 20:** Multi-Instance GPU (MIG) is available on which GPUs?

A) All NVIDIA GPUs  
B) GTX and RTX series  
C) A30, A100, H100 data center GPUs  
D) Only H100

**Question 21:** An A100 40GB GPU can be partitioned into a maximum of how many 1g.5gb MIG instances?

A) 4  
B) 5  
C) 7  
D) 8

**Question 22:** Which GPU sharing method provides the strongest isolation?

A) Time-slicing  
B) MPS (Multi-Process Service)  
C) MIG (Multi-Instance GPU)  
D) vGPU

---

## Section 7: GPU Monitoring (Questions 23-24)

**Question 23:** DCGM stands for:

A) Data Center GPU Manager  
B) Dynamic CUDA Graphics Module  
C) Distributed Computing GPU Monitor  
D) Device Control GPU Metrics

**Question 24:** What is a critical GPU health indicator that suggests hardware failure?

A) High GPU utilization (>90%)  
B) Double-bit ECC errors  
C) Power usage at limit  
D) Temperature at 80°C

---

## Section 8: GPU Cluster Design (Question 25)

**Question 25:** For a DGX A100 system with 8x A100 80GB GPUs, what is the approximate total power consumption?

A) 2-3 kW  
B) 4-5 kW  
C) 6-7 kW  
D) 10-11 kW

---

## Short Answer Questions (Bonus)

**Question 26:** Explain the difference between memory-bound and compute-bound GPU kernels. How would you identify each using profiling tools? (3-4 sentences)

**Question 27:** Why is NVSwitch important for scaling GPU clusters beyond 8 GPUs? What problem does it solve? (2-3 sentences)

**Question 28:** When would you choose MIG over regular GPU sharing (time-slicing)? Provide two specific use cases. (2-3 sentences)

---

## Answer Key

### Multiple Choice Answers

1. **B** - A warp is 32 threads that execute in SIMT fashion
2. **C** - Registers have the fastest access (~1 cycle)
3. **C** - 1024 threads per block maximum
4. **C** - The if-else based on even/odd causes warp divergence
5. **B** - Consecutive, aligned access enables coalescing
6. **C** - Tensor Cores specialize in matrix operations (GEMM)
7. **D** - Hopper (H100) introduced FP8 support
8. **C** - A100 has 108 SMs (98 on 40GB variant)
9. **A** - HBM is High Bandwidth Memory (stacked DRAM)
10. **B** - Compute capability defines available features
11. **C** - TensorRT optimizes models for inference deployment
12. **B** - cuDNN automatically uses Tensor Cores with FP16/BF16
13. **B** - NCCL provides collective communications (all-reduce, etc.)
14. **B** - Nsight Systems for system-wide timeline
15. **C** - Low utilization on both indicates insufficient parallelism
16. **B** - NVTX adds custom markers for profiling
17. **B** - All-reduce synchronizes gradients in data parallel
18. **D** - NVLink ~20x faster than PCIe Gen3 (600 GB/s vs 32 GB/s)
19. **B** - 40 GB (ring all-reduce transfers 2x model size)
20. **C** - MIG on A30, A100, H100 data center GPUs
21. **C** - A100 40GB supports 7x 1g.5gb instances
22. **C** - MIG provides hardware-enforced isolation
23. **A** - Data Center GPU Manager
24. **B** - Double-bit ECC errors indicate memory failure
25. **C** - DGX A100 consumes ~6.5 kW

### Short Answer Sample Answers

**Question 26:**
Memory-bound kernels are limited by memory bandwidth, spending most time waiting for data. Compute-bound kernels are limited by arithmetic throughput. In profiling tools like Nsight Compute, check the "Speed of Light" metrics: if memory throughput is high (>60%) and compute is low, it's memory-bound; if compute throughput is high and memory is low, it's compute-bound. The roofline model visualization also clearly shows this distinction.

**Question 27:**
NVSwitch enables full bisection bandwidth between all GPUs in a node, allowing any GPU to communicate with any other at full NVLink speed. Without NVSwitch, GPUs can only directly connect to a limited number of neighbors (typically 2-4), creating bandwidth bottlenecks for collective operations like all-reduce. NVSwitch is essential for achieving linear scaling with 8+ GPUs per node.

**Question 28:**
Use MIG when you need strong isolation for multi-tenant workloads, such as: (1) Running production inference services for different teams/customers where one tenant's errors shouldn't affect others, or (2) Providing guaranteed QoS for batch inference workloads where each tenant needs predictable performance. MIG provides hardware-level isolation with dedicated memory, SMs, and L2 cache, unlike time-slicing which offers no isolation.

---

## Scoring Guide

- Questions 1-25: 1 point each (25 points total)
- Questions 26-28: 2 points each (6 bonus points)
- Maximum score: 25 points (31 with bonus)
- Passing score: 20/25 (80%)

**Performance Levels:**
- 23-25 (92-100%): Excellent - Strong mastery of GPU computing
- 20-22 (80-88%): Good - Solid understanding, ready for advanced topics
- 17-19 (68-76%): Fair - Review weak areas before proceeding
- <17 (<68%): Needs improvement - Review lectures and retry

---

## Review Recommendations

Based on your score, focus review on:

- **Questions 1-5 missed**: Review Lecture 01 (CUDA Fundamentals)
- **Questions 6-10 missed**: Review Lecture 02 (GPU Architecture)
- **Questions 11-13 missed**: Review Lecture 03 (CUDA Libraries)
- **Questions 14-16 missed**: Review Lecture 04 (GPU Profiling)
- **Questions 17-19 missed**: Review Lecture 05 (Multi-GPU Strategies)
- **Questions 20-22 missed**: Review Lecture 06 (GPU Virtualization)
- **Questions 23-24 missed**: Review Lecture 07 (GPU Monitoring)
- **Question 25 missed**: Review Lecture 08 (GPU Cluster Design)

---

**Congratulations on completing the Module 203 quiz! Use your results to guide further study and practice.**
