# Module 202 Quiz: Distributed Training at Scale

**Total Questions**: 25  
**Passing Score**: 80% (20/25 correct)  
**Time Limit**: 60 minutes

## Section 1: Fundamentals (Questions 1-7)

### Question 1
What is the main advantage of data parallelism over model parallelism?

A) Requires less memory per GPU  
B) Scales to larger models  
C) Simpler to implement and works with any model architecture  
D) Provides better accuracy

**Answer**: C

**Explanation**: Data parallelism is simpler because it requires minimal code changes and works with any model architecture. Each GPU holds a complete model copy and processes different data batches. Model parallelism is more complex but necessary when models don't fit on a single GPU.

---

### Question 2
In Ring AllReduce, how many times is data transferred for N GPUs?

A) N times  
B) N-1 times  
C) 2(N-1) times  
D) N² times

**Answer**: C

**Explanation**: Ring AllReduce consists of two phases: scatter-reduce (N-1 steps) and allgather (N-1 steps), totaling 2(N-1) communication steps. This makes it bandwidth-optimal.

---

### Question 3
Which parallelism strategy is best for a 175B parameter model that doesn't fit on a single GPU?

A) Data parallelism only  
B) Tensor parallelism only  
C) Pipeline parallelism only  
D) Hybrid parallelism (combining multiple strategies)

**Answer**: D

**Explanation**: Very large models like 175B parameters require hybrid parallelism (3D parallelism) combining tensor, pipeline, and data parallelism to fit the model across GPUs and scale training efficiently.

---

### Question 4
What is the pipeline bubble in pipeline parallelism?

A) Memory overflow in the pipeline  
B) Idle time when GPUs wait for data  
C) Communication bottleneck  
D) Gradient accumulation overhead

**Answer**: B

**Explanation**: Pipeline bubble refers to idle time at the beginning and end of each batch when some GPUs are waiting. The bubble fraction is (N-1)/M where N is number of pipeline stages and M is number of micro-batches.

---

### Question 5
Why does data parallel training typically scale learning rate by world size?

A) To prevent overfitting  
B) To maintain effective batch size  
C) To reduce communication  
D) To improve convergence speed

**Answer**: B

**Explanation**: When using data parallelism, the effective batch size increases by world_size. Scaling the learning rate proportionally maintains the training dynamics. Common practice: lr_effective = lr_base × world_size.

---

### Question 6
What is gradient accumulation primarily used for?

A) Improving model accuracy  
B) Simulating larger batch sizes without memory increase  
C) Reducing training time  
D) Enabling model parallelism

**Answer**: B

**Explanation**: Gradient accumulation allows training with larger effective batch sizes by accumulating gradients over multiple forward/backward passes before updating weights. This also reduces communication frequency in distributed training.

---

### Question 7
In ZeRO Stage 3, what is partitioned across GPUs?

A) Only optimizer states  
B) Optimizer states and gradients  
C) Optimizer states, gradients, and model parameters  
D) Only model parameters

**Answer**: C

**Explanation**: ZeRO Stage 3 partitions everything: optimizer states, gradients, and model parameters across GPUs. This provides maximum memory savings but requires more communication during forward/backward passes.

---

## Section 2: Ray and Frameworks (Questions 8-12)

### Question 8
What is the main advantage of Ray Train over pure PyTorch DDP?

A) Faster training speed  
B) Built-in fault tolerance and easier scaling  
C) Better GPU utilization  
D) Lower memory usage

**Answer**: B

**Explanation**: Ray Train provides built-in fault tolerance, automatic checkpointing, elastic scaling, and easier deployment on Kubernetes. It abstracts away complexity while PyTorch DDP requires manual fault tolerance implementation.

---

### Question 9
In Ray, what is an ObjectRef?

A) A reference to a Python object in Ray's object store  
B) A GPU memory pointer  
C) A distributed lock  
D) A checkpoint reference

**Answer**: A

**Explanation**: ObjectRef is Ray's reference to data stored in the distributed object store. It enables zero-copy data sharing and lazy evaluation. ray.get() dereferences an ObjectRef to get the actual value.

---

### Question 10
How does Horovod synchronize gradients?

A) Parameter server  
B) AllReduce collective operation  
C) Peer-to-peer communication  
D) Central coordinator

**Answer**: B

**Explanation**: Horovod uses AllReduce (via MPI/NCCL) to synchronize gradients across all workers. This is bandwidth-optimal and scales well to many GPUs compared to parameter server approaches.

---

### Question 11
What is Ray Tune primarily used for?

A) Distributed training  
B) Hyperparameter optimization  
C) Model deployment  
D) Data preprocessing

**Answer**: B

**Explanation**: Ray Tune is Ray's library for distributed hyperparameter tuning. It supports various search algorithms (grid, random, Bayesian, PBT) and schedulers (ASHA, HyperBand) for efficient optimization at scale.

---

### Question 12
In PyTorch DDP, when do gradients get synchronized?

A) During forward pass  
B) During backward pass automatically  
C) During optimizer.step()  
D) Manually by calling sync()

**Answer**: B

**Explanation**: PyTorch DDP automatically synchronizes gradients during the backward pass using AllReduce hooks. This overlaps communication with computation for efficiency. No manual synchronization is needed.

---

## Section 3: NCCL and Networking (Questions 13-16)

### Question 13
What is RDMA (Remote Direct Memory Access)?

A) A GPU memory technology  
B) Direct memory access between nodes without OS involvement  
C) A type of SSD  
D) A network protocol

**Answer**: B

**Explanation**: RDMA allows direct memory access from one computer to another without involving the operating system, reducing latency and CPU overhead. InfiniBand provides RDMA capabilities for high-performance distributed training.

---

### Question 14
Which NCCL environment variable enables InfiniBand support?

A) NCCL_IB_ENABLE=1  
B) NCCL_IB_DISABLE=0  
C) NCCL_INFINIBAND=1  
D) NCCL_RDMA=1

**Answer**: B

**Explanation**: NCCL_IB_DISABLE=0 enables InfiniBand support (disabled by default in some configurations). Other important variables include NCCL_IB_HCA (device selection) and NCCL_NET_GDR_LEVEL (GPUDirect RDMA).

---

### Question 15
What is the typical bandwidth of NVLink 3.0 per GPU?

A) 32 GB/s  
B) 100 GB/s  
C) 300 GB/s  
D) 600 GB/s

**Answer**: D

**Explanation**: NVLink 3.0 (A100) provides 600 GB/s bidirectional bandwidth per GPU through 12 NVLink connections. This is significantly faster than PCIe 4.0 x16 (32 GB/s).

---

### Question 16
Why is Ring AllReduce bandwidth-optimal?

A) Uses minimum number of communication steps  
B) Each GPU transfers approximately 2× the data size regardless of N  
C) Requires no synchronization  
D) Works only with NVLink

**Answer**: B

**Explanation**: In Ring AllReduce, each GPU transfers approximately 2(N-1)/N ≈ 2× the data size, which approaches the theoretical minimum. This makes it bandwidth-optimal for large N, unlike tree-based algorithms.

---

## Section 4: Mixed Precision and Optimization (Questions 17-21)

### Question 17
What is the main advantage of BF16 over FP16?

A) Higher precision  
B) Same dynamic range as FP32  
C) Faster computation  
D) Less memory usage

**Answer**: B

**Explanation**: BFloat16 has the same exponent bits (8) as FP32, giving it the same dynamic range (±3.4e38). FP16 has only 5 exponent bits with range ±65504, making it prone to overflow/underflow. BF16 trades precision for range.

---

### Question 18
Why is gradient scaling necessary for FP16 training?

A) To prevent overflow  
B) To prevent underflow of small gradients  
C) To improve convergence  
D) To reduce memory usage

**Answer**: B

**Explanation**: Small gradients (common in deep networks) can underflow to zero in FP16. Gradient scaling multiplies the loss by a scale factor before backward pass, keeping gradients in FP16's representable range, then unscales before optimizer step.

---

### Question 19
What is gradient checkpointing (activation checkpointing)?

A) Saving gradients to disk  
B) Trading computation for memory by recomputing activations  
C) Compressing gradients  
D) Skipping certain layers

**Answer**: B

**Explanation**: Gradient checkpointing reduces memory by not storing all intermediate activations during forward pass. Instead, it recomputes them during backward pass. This trades ~33% more computation for ~50% memory reduction.

---

### Question 20
Which operation should typically remain in FP32 for numerical stability?

A) Matrix multiplication  
B) Convolution  
C) LayerNorm and BatchNorm  
D) ReLU activation

**Answer**: C

**Explanation**: LayerNorm, BatchNorm, and other normalization layers should stay in FP32 for numerical stability. They involve variance calculations and divisions that can suffer from FP16's limited precision. Loss computation also typically stays FP32.

---

### Question 21
What is the typical speedup from mixed precision training on A100 GPUs?

A) 1.2-1.5x  
B) 2-3x  
C) 5-8x  
D) 10-16x

**Answer**: B

**Explanation**: Real-world speedup from mixed precision on A100s is typically 2-3x, not the theoretical 16x from TFLOPS numbers. This is due to memory bandwidth, data transfer overhead, and operations that must remain in FP32.

---

## Section 5: Fault Tolerance and Production (Questions 22-25)

### Question 22
What is the purpose of the barrier() call in distributed training?

A) To synchronize gradients  
B) To ensure all processes reach the same point before continuing  
C) To save checkpoints  
D) To broadcast parameters

**Answer**: B

**Explanation**: dist.barrier() is a synchronization primitive that blocks until all processes in the group reach that point. It's used to ensure consistent state, especially around checkpointing and initialization.

---

### Question 23
In a 256-node cluster running for 1 month, what is the approximate probability of at least one node failure (MTBF = 100,000 hours per node)?

A) 10%  
B) 50%  
C) 90%  
D) 99.9%

**Answer**: D

**Explanation**: With λ = 1/100,000 per hour per node and T = 720 hours (1 month), probability of at least one failure = 1 - e^(-256 × 720/100,000) ≈ 0.999 or 99.9%. Fault tolerance is essential!

---

### Question 24
What is elastic training?

A) Training that adapts batch size automatically  
B) Training that can continue with changing number of workers  
C) Training with variable learning rate  
D) Training with dynamic model architecture

**Answer**: B

**Explanation**: Elastic training allows dynamically adding or removing workers during training without stopping. The system automatically redistributes work and continues from checkpoints. Ray Train and Kubernetes support elastic training.

---

### Question 25
What is the recommended checkpoint frequency for a 3-day training job?

A) Every 10 batches  
B) Every epoch  
C) Every hour  
D) Every 6-12 hours

**Answer**: D

**Explanation**: For long-running jobs, checkpoint every 6-12 hours balances recovery time vs. checkpoint overhead. Too frequent wastes I/O; too infrequent risks losing days of work on failure. Also consider checkpointing at validation milestones.

---

## Scoring Guide

- 25/25: Expert level - Ready for production distributed training
- 20-24: Strong understanding - Minor gaps to address
- 16-19: Good foundation - Review challenging topics
- < 16: Need more study - Revisit lecture notes and labs

## Answer Key Summary

1. C  2. C  3. D  4. B  5. B  
6. B  7. C  8. B  9. A  10. B  
11. B  12. B  13. B  14. B  15. D  
16. B  17. B  18. B  19. B  20. C  
21. B  22. B  23. D  24. B  25. D

---

**Module 202 Quiz Complete**  
**Version**: 1.0  
**Last Updated**: 2025-10-16
