# Lecture 01: Model Optimization Overview

## Learning Objectives

By the end of this lecture, you will be able to:

- Design systematic model optimization strategies that balance latency, throughput, memory, and accuracy requirements for production ML deployments
- Architect optimization workflows that systematically identify bottlenecks through profiling and apply appropriate techniques (quantization, pruning, compilation) incrementally
- Evaluate trade-offs between optimization approaches (conservative vs aggressive) based on use case requirements and acceptable accuracy degradation thresholds
- Implement comprehensive performance measurement frameworks that track latency percentiles, throughput metrics, GPU utilization, and cost per query
- Configure hardware-specific optimizations leveraging Tensor Cores, specialized accelerators, and execution providers for different deployment targets (NVIDIA, AMD, TPU, edge)
- Apply the complete optimization taxonomy to select appropriate techniques based on identified bottlenecks (memory-bound, compute-bound, latency-bound, cost-bound)
- Benchmark optimized models under realistic load conditions and generate detailed performance reports comparing baseline vs optimized metrics
- Design production optimization pipelines with proper validation, A/B testing, monitoring, and rollback mechanisms to ensure quality and reliability

## Table of Contents
1. [Introduction to Model Optimization](#introduction)
2. [Why Optimization Matters](#why-optimization-matters)
3. [Optimization Taxonomy](#optimization-taxonomy)
4. [Performance Metrics](#performance-metrics)
5. [Optimization Workflow](#optimization-workflow)
6. [Common Bottlenecks](#common-bottlenecks)
7. [Hardware Considerations](#hardware-considerations)
8. [Trade-offs and Decision Framework](#trade-offs)
9. [Industry Case Studies](#case-studies)
10. [Best Practices](#best-practices)

<a name="introduction"></a>
## 1. Introduction to Model Optimization

Model optimization is the systematic process of improving the efficiency of deep learning models for inference in production environments. While training optimization focuses on faster convergence and better accuracy, inference optimization prioritizes reducing latency, increasing throughput, minimizing memory usage, and lowering operational costs.

### The Production Reality

When you train a model in a research environment, you typically optimize for accuracy on a validation set. However, production deployment introduces entirely different constraints:

- **Latency Requirements**: Users expect sub-second (often sub-100ms) responses
- **Cost Constraints**: Cloud GPU costs can reach $10,000+ per month per instance
- **Scale Demands**: Systems must handle thousands to millions of requests per day
- **Energy Efficiency**: Data center power consumption directly impacts profitability
- **Memory Limits**: Inference servers have fixed GPU memory budgets
- **Multi-tenancy**: Multiple models often share the same hardware

A model that achieves 95% accuracy but takes 5 seconds to run is often less valuable than a model with 93% accuracy that runs in 50ms. This module teaches you how to bridge this gap.

### The Optimization Landscape in 2025

The field of model optimization has exploded in recent years, driven primarily by:

1. **LLM Adoption**: Large Language Models with billions of parameters require sophisticated optimization to be economically viable
2. **Edge Deployment**: More models are running on edge devices with severe resource constraints
3. **Sustainability Concerns**: AI's carbon footprint has made efficiency a business imperative
4. **Real-time Requirements**: Applications like autonomous vehicles and robotics demand ultra-low latency
5. **Cost Pressure**: As AI deployment scales, inference costs dominate total ML budgets

<a name="why-optimization-matters"></a>
## 2. Why Optimization Matters

### Economic Impact

Consider a typical production LLM serving scenario:

**Unoptimized Setup:**
- Model: LLaMA-2 70B
- Hardware: 4x A100 80GB GPUs
- Throughput: 50 tokens/second
- Cost: $16/hour on AWS (4 x p4d.24xlarge)
- Daily cost: $384
- Monthly cost: $11,520

**Optimized Setup:**
- Model: LLaMA-2 70B with INT8 quantization + vLLM
- Hardware: 2x A100 80GB GPUs
- Throughput: 400 tokens/second (8x improvement)
- Cost: $8/hour on AWS
- Daily cost: $192
- Monthly cost: $5,760

**Result**: 50% cost reduction while increasing throughput by 8x. For a company running 10 such deployments, this saves $700,000+ annually.

### Latency Criticality

Research shows that latency directly impacts user behavior:

- **100ms delay**: 1% drop in conversion for e-commerce
- **500ms delay**: 20% increase in bounce rate
- **1 second delay**: 7% reduction in conversions
- **3 second delay**: 50%+ abandonment rate

For real-time applications like conversational AI, users expect responses to begin streaming within 200-300ms. Without optimization, most LLMs would fail this requirement.

### Environmental Impact

Training a single large model (GPT-3 scale) produces approximately 552 metric tons of CO2. However, inference accounts for 80-90% of total ML carbon footprint over a model's lifetime:

- **Unoptimized inference**: 1000 models running 24/7 = ~500 tons CO2/year
- **Optimized inference**: Same workload = ~150 tons CO2/year

Optimization isn't just good business; it's environmental responsibility.

### Democratization of AI

Optimization makes advanced AI accessible:

- Enables deployment on consumer hardware (laptops, phones)
- Reduces cloud costs for startups
- Makes open-source models competitive with proprietary APIs
- Enables AI in bandwidth-constrained environments

<a name="optimization-taxonomy"></a>
## 3. Optimization Taxonomy

Model optimization techniques can be categorized along several dimensions:

### 3.1 By Optimization Stage

**Training-time Optimization:**
- Quantization-Aware Training (QAT)
- Knowledge Distillation
- Neural Architecture Search (NAS)
- Pruning during training

**Post-training Optimization:**
- Post-Training Quantization (PTQ)
- Post-training Pruning
- Model compilation
- Graph optimization

**Deployment-time Optimization:**
- Batching strategies
- Kernel fusion
- Memory layout optimization
- Multi-instance serving

### 3.2 By Optimization Target

**Compute Optimization:**
- Reduces FLOPs (floating point operations)
- Examples: Pruning, distillation, efficient architectures

**Memory Optimization:**
- Reduces model size and activation memory
- Examples: Quantization, weight sharing, KV cache optimization

**Latency Optimization:**
- Reduces end-to-end inference time
- Examples: Kernel fusion, asynchronous execution, speculative decoding

**Throughput Optimization:**
- Maximizes requests per second
- Examples: Batching, pipelining, multi-instance serving

### 3.3 By Technique Category

**Model Compression:**
- **Quantization**: Reduce numerical precision (FP32 → INT8)
- **Pruning**: Remove unnecessary weights or neurons
- **Knowledge Distillation**: Train smaller model to mimic larger one
- **Low-rank Factorization**: Decompose weight matrices
- **Weight Sharing**: Reuse weights across layers

**System Optimization:**
- **Kernel Fusion**: Combine operations to reduce memory transfers
- **Graph Optimization**: Algebraic simplification and operator fusion
- **Memory Planning**: Optimize memory allocation and reuse
- **Parallelization**: Tensor, pipeline, and data parallelism

**Algorithm Optimization:**
- **Continuous Batching**: Dynamic request batching for LLMs
- **Speculative Decoding**: Parallel token generation
- **Flash Attention**: Memory-efficient attention computation
- **PagedAttention**: Virtual memory for KV cache

**Hardware-specific Optimization:**
- **Tensor Core Utilization**: Leverage specialized hardware (NVIDIA)
- **Mixed Precision**: Use FP16/BF16 for compatible operations
- **Operator Libraries**: cuDNN, cuBLAS, TensorRT
- **Custom Kernels**: Hand-written CUDA/Triton kernels

<a name="performance-metrics"></a>
## 4. Performance Metrics

Understanding how to measure optimization impact is critical.

### 4.1 Latency Metrics

**Time to First Token (TTFT)**: For generative models, time until first output token
- Critical for user experience in chatbots
- Target: <300ms for conversational AI

**Time Per Output Token (TPOT)**: Average time to generate each subsequent token
- Determines streaming speed
- Target: <50ms for smooth streaming

**End-to-End Latency**: Total time from request to complete response
- Includes preprocessing, inference, and postprocessing
- Measured at p50, p95, p99 percentiles

**Breakdown:**
```
Total Latency = Network + Preprocessing + Inference + Postprocessing + Network
```

Always measure latency under realistic load conditions, not idle systems.

### 4.2 Throughput Metrics

**Queries Per Second (QPS)**: Number of complete requests processed per second
- Standard metric for classification/detection models
- Measured at different batch sizes

**Tokens Per Second (TPS)**: For generative models, total tokens generated per second
- Accounts for both input and output tokens
- Can be measured per-instance or aggregate

**GPU Utilization**: Percentage of GPU compute being used
- Target: >80% for cost-effective deployment
- Monitor with nvidia-smi or profiling tools

### 4.3 Efficiency Metrics

**Latency-Throughput Curve**: Plot showing trade-off between latency and throughput
- Useful for capacity planning
- Identifies optimal operating point

**Cost Per Query**: Amortized hardware cost divided by QPS
```
Cost per Query = (GPU cost per hour / 3600) / QPS
```

**Tokens Per Dollar**: For LLM serving
```
Tokens per Dollar = (TPS * 3600) / GPU cost per hour
```

**Memory Efficiency**: Model size relative to accuracy or capability
```
Memory Efficiency = Accuracy / Model Size (GB)
```

### 4.4 Quality Metrics

Optimization should not significantly degrade model quality:

**Accuracy Degradation**: Change in accuracy after optimization
- Target: <1% for most applications
- Critical applications: <0.1%

**Perplexity (for LLMs)**: Measure of language model quality
- Lower is better
- Compare before and after optimization

**Task-specific Metrics**: BLEU, ROUGE, F1, mAP depending on application
- Always validate on representative test set
- Monitor for distribution shift

<a name="optimization-workflow"></a>
## 5. Optimization Workflow

A systematic approach to model optimization:

### Step 1: Establish Baseline

Before optimization, measure current performance:

```python
# Baseline measurement template
baseline_metrics = {
    'latency_p50': measure_latency(model, test_data, percentile=50),
    'latency_p95': measure_latency(model, test_data, percentile=95),
    'throughput': measure_throughput(model, test_data),
    'memory_usage': measure_gpu_memory(model),
    'accuracy': evaluate_accuracy(model, validation_set),
    'gpu_utilization': profile_gpu_utilization(model, test_data)
}
```

### Step 2: Profile and Identify Bottlenecks

Use profiling tools to understand where time is spent:

**Layer-level Profiling:**
- Which layers consume most time?
- Are there unexpected bottlenecks?
- Is GPU utilization high?

**Operation-level Profiling:**
- Which operations dominate (matmul, attention, activation)?
- Are there CPU-GPU synchronization points?
- Is there unnecessary data movement?

**Tools:**
- NVIDIA Nsight Systems
- PyTorch Profiler
- TensorFlow Profiler
- Custom timing decorators

### Step 3: Choose Optimization Techniques

Based on profiling results and requirements:

**If memory-bound:**
- Quantization (INT8, FP16)
- KV cache optimization
- Activation checkpointing

**If compute-bound:**
- Kernel fusion
- Better batching
- Tensor Core utilization

**If latency-bound:**
- Reduce model size (distillation, pruning)
- Pipeline parallelism
- Speculative decoding (for LLMs)

**If cost-bound:**
- Aggressive quantization (INT4)
- Model compression
- Multi-model serving

### Step 4: Implement Optimizations Incrementally

Apply one technique at a time to understand impact:

```python
optimization_log = []

for technique in [quantization, pruning, kernel_fusion]:
    optimized_model = apply_optimization(model, technique)
    metrics = measure_all_metrics(optimized_model)

    optimization_log.append({
        'technique': technique.__name__,
        'metrics': metrics,
        'improvement': calculate_improvement(baseline_metrics, metrics)
    })

    if metrics['accuracy'] < threshold:
        print(f"Accuracy degradation too high, reverting {technique}")
        continue

    model = optimized_model  # Accept optimization
```

### Step 5: Validate Quality

Rigorously test optimized model:

- Run full evaluation suite
- Test edge cases and failure modes
- Perform A/B testing if possible
- Monitor for distribution shift
- Validate numerical stability

### Step 6: Benchmark and Report

Generate comprehensive performance report:

```markdown
# Optimization Report

## Baseline
- Latency P50: 150ms
- Throughput: 100 QPS
- GPU Memory: 24GB
- Accuracy: 94.2%

## Optimized
- Latency P50: 45ms (3.3x improvement)
- Throughput: 420 QPS (4.2x improvement)
- GPU Memory: 6GB (4x reduction)
- Accuracy: 93.8% (-0.4%)

## Techniques Applied
1. INT8 Quantization: 2x speedup, -0.3% accuracy
2. TensorRT Compilation: 1.5x speedup
3. Continuous Batching: 1.1x throughput improvement

## Cost Impact
- Before: $384/day
- After: $96/day
- Annual Savings: $105,120
```

<a name="common-bottlenecks"></a>
## 6. Common Bottlenecks

Understanding typical performance bottlenecks helps focus optimization efforts.

### 6.1 Memory Bandwidth

**Symptom**: Low GPU utilization despite high memory usage

**Causes:**
- Large activations moving between GPU memory and compute units
- Inefficient memory access patterns
- Small batch sizes not saturating memory bandwidth

**Solutions:**
- Increase batch size
- Use FP16 or INT8 to reduce memory traffic
- Kernel fusion to keep data in cache
- Use Tensor Cores with appropriate data types

### 6.2 Compute Inefficiency

**Symptom**: GPU utilization <50% with plenty of available memory

**Causes:**
- Operators not optimized for GPU
- CPU-GPU synchronization
- Small matrix operations
- Inefficient kernel implementations

**Solutions:**
- Use optimized libraries (cuDNN, cuBLAS)
- Fuse small operations
- Increase batch size
- Use TensorRT or compiler optimizations

### 6.3 KV Cache Management (LLMs)

**Symptom**: Memory exhaustion or low batch sizes with LLMs

**Causes:**
- Linear growth of KV cache with sequence length
- Memory fragmentation
- Static memory allocation

**Solutions:**
- PagedAttention (vLLM)
- KV cache quantization
- Multi-query attention (MQA)
- Grouped-query attention (GQA)

### 6.4 Batch Size Suboptimality

**Symptom**: High latency per request or low GPU utilization

**Causes:**
- Static batching waiting for full batch
- Variable sequence lengths causing padding waste
- No batching at all

**Solutions:**
- Dynamic batching
- Continuous batching (for LLMs)
- Sequence packing
- Variable batch size scheduling

### 6.5 Preprocessing/Postprocessing

**Symptom**: CPU bottleneck before or after GPU inference

**Causes:**
- Complex tokenization or image preprocessing
- Single-threaded preprocessing
- Inefficient data transfer to GPU

**Solutions:**
- Precompute when possible
- Use GPU preprocessing
- Parallelize preprocessing
- Pipeline preprocessing with inference

<a name="hardware-considerations"></a>
## 7. Hardware Considerations

Different hardware has different optimization opportunities:

### 7.1 NVIDIA GPUs

**Tensor Cores**: Specialized units for matrix multiplication
- Available on Volta, Turing, Ampere, Hopper architectures
- Require specific data types: FP16, BF16, INT8, FP8
- Require specific matrix dimensions (multiples of 8 or 16)

**Memory Hierarchy**:
- L1 Cache: ~128KB per SM
- Shared Memory: ~164KB per SM (configurable with L1)
- L2 Cache: 40MB (A100) to 60MB (H100)
- HBM: 40-80GB (A100) to 96GB (H100)

**Optimization Strategy**:
- Use FP16/BF16 for Tensor Core utilization
- TensorRT for automatic kernel fusion and optimization
- cuDNN for standard operations
- Triton for custom kernels

### 7.2 AMD GPUs

**Matrix Core**: Similar to Tensor Cores
- Available on CDNA architectures (MI100, MI250)
- Supports FP16, BF16, INT8

**ROCm**: AMD's CUDA alternative
- Good PyTorch support
- Limited TensorRT equivalent (MIGraphX)

**Optimization Strategy**:
- Use ROCm-optimized libraries
- ONNX Runtime with ROCm execution provider
- Profile with rocprof

### 7.3 Cloud TPUs

**Systolic Array**: Matrix multiplication specialized hardware
- Optimized for large matrix operations
- BF16 native support

**Memory**: HBM with fast interconnect

**Optimization Strategy**:
- XLA compiler automatically optimizes
- Use TensorFlow or JAX
- Optimize for large batch sizes

### 7.4 Edge Devices

**ARM CPUs**: Neoverse, Apple Silicon
- NEON SIMD instructions
- Limited memory (1-8GB)

**Mobile GPUs**: Mali, Adreno
- Lower precision (FP16 common)
- Power constraints

**NPUs/ASICs**: Google Edge TPU, Apple Neural Engine
- Fixed-function accelerators
- INT8 common

**Optimization Strategy**:
- Aggressive quantization (INT8, INT4)
- Model pruning
- Use TFLite, ONNX Runtime Mobile, CoreML
- Optimize for power consumption

<a name="trade-offs"></a>
## 8. Trade-offs and Decision Framework

Every optimization involves trade-offs. Here's a framework for decision-making:

### Accuracy vs. Speed Trade-off

**Conservative Approach** (< 0.5% accuracy loss):
- FP16 mixed precision
- Light pruning (10-20%)
- INT8 with careful calibration
- Use case: Medical, financial, safety-critical

**Balanced Approach** (0.5-1.5% accuracy loss):
- INT8 quantization
- Moderate pruning (30-50%)
- Knowledge distillation
- Use case: Most production applications

**Aggressive Approach** (>1.5% accuracy loss acceptable):
- INT4 quantization
- Heavy pruning (70%+)
- Extreme distillation
- Use case: Edge devices, cost-sensitive, soft targets

### Latency vs. Throughput Trade-off

**Latency-Optimized**:
- Small batch sizes (1-4)
- Multiple model instances
- Simple preprocessing
- Use case: Real-time applications, chatbots

**Throughput-Optimized**:
- Large batch sizes (32-128+)
- Single powerful instance
- Batched preprocessing
- Use case: Batch processing, offline inference

**Balanced**:
- Dynamic batching
- Moderate batch sizes (8-16)
- Request queuing
- Use case: General web services

### Development Time vs. Optimization Gain

**Quick Wins** (hours to implement):
- FP16 inference
- Increase batch size
- Use TensorRT/ONNX Runtime
- Expected gain: 2-3x

**Moderate Effort** (days to implement):
- INT8 quantization
- Model distillation
- Custom batching logic
- Expected gain: 3-5x

**Heavy Investment** (weeks to implement):
- Custom CUDA kernels
- Architecture redesign
- Advanced compression
- Expected gain: 5-10x+

### Decision Matrix

| Use Case | Priority | Recommended Techniques |
|----------|----------|------------------------|
| Real-time inference | Latency | FP16, TensorRT, small models |
| Batch processing | Throughput | Large batches, INT8, model parallelism |
| Edge deployment | Size + Power | INT8/INT4, pruning, distillation |
| Cost optimization | Efficiency | INT8, continuous batching, multi-tenancy |
| Quick deployment | Time to market | TensorRT auto-optimization, FP16 |

<a name="case-studies"></a>
## 9. Industry Case Studies

### Case Study 1: OpenAI GPT-3.5 Serving

**Challenge**: Serve GPT-3.5 at scale with acceptable latency and cost

**Optimizations Applied**:
- Custom CUDA kernels for attention
- Dynamic batching
- Speculative decoding for some queries
- Multi-query attention for faster KV cache

**Results**:
- 50% cost reduction
- Sub-second TTFT for most queries
- 10x throughput improvement

### Case Study 2: Tesla Autopilot

**Challenge**: Run multiple vision models at 36 FPS on custom hardware

**Optimizations Applied**:
- INT8 quantization with QAT
- Custom hardware accelerator
- Highly optimized inference pipeline
- Multi-model fusion

**Results**:
- 25 TOPS on custom chip
- 36 FPS with 8 camera streams
- 72W power consumption

### Case Study 3: Google Translate

**Challenge**: Serve billions of translation requests daily

**Optimizations Applied**:
- Knowledge distillation (large model → smaller model)
- TPU-optimized serving
- Aggressive caching
- Request batching

**Results**:
- 10x cost reduction
- <100ms latency for most translations
- Maintained quality

<a name="best-practices"></a>
## 10. Best Practices

### DO:

1. **Always Measure**: Profile before optimizing
2. **Incremental Changes**: Apply one optimization at a time
3. **Validate Quality**: Test thoroughly after each change
4. **Document**: Keep detailed records of what works
5. **Use Production Data**: Test with realistic inputs
6. **Monitor**: Track metrics in production
7. **Version Control**: Keep optimized models versioned
8. **A/B Test**: Compare against baseline in production

### DON'T:

1. **Premature Optimization**: Profile first, optimize second
2. **Ignore Quality**: Speed without accuracy is useless
3. **Optimize in Isolation**: Consider end-to-end pipeline
4. **Forget to Benchmark**: Measure real-world performance
5. **Over-optimize**: Know when good enough is good enough
6. **Ignore Maintenance**: Optimized code requires upkeep
7. **Skip Validation**: Always test edge cases
8. **Forget TCO**: Consider operational costs

### Optimization Checklist

Before deploying an optimized model:

- [ ] Baseline metrics measured and documented
- [ ] Profiling completed and bottlenecks identified
- [ ] Optimization techniques selected based on data
- [ ] Each optimization applied incrementally
- [ ] Quality validated on representative test set
- [ ] Performance benchmarked under realistic load
- [ ] Edge cases and failure modes tested
- [ ] Documentation updated
- [ ] Monitoring dashboards configured
- [ ] Rollback plan prepared
- [ ] Team trained on new deployment
- [ ] Cost analysis completed

## Summary

Model optimization is a critical skill for production AI systems. This lecture provided:

- **Economic and technical justification** for optimization
- **Comprehensive taxonomy** of optimization techniques
- **Metrics and measurement** frameworks
- **Systematic workflow** for optimization projects
- **Common bottlenecks** and solutions
- **Hardware-specific** considerations
- **Trade-off frameworks** for decision-making
- **Real-world case studies** from industry leaders
- **Best practices** for successful optimization

In the following lectures, we'll dive deep into specific techniques:
- **Lecture 02**: TensorRT for NVIDIA GPUs
- **Lecture 03**: ONNX Runtime for cross-platform inference
- **Lecture 04**: Quantization techniques in depth
- **Lecture 05**: Pruning and distillation
- **Lecture 06**: LLM-specific optimizations
- **Lecture 07**: Continuous batching and KV cache management

## Further Reading

- "Efficient Deep Learning" book by Gaurav Menghani
- NVIDIA TensorRT documentation
- vLLM technical blog posts
- "A Survey of Model Compression and Acceleration" papers
- MLPerf Inference benchmarks

## Next Steps

1. Complete the exercises in `exercises/lab-01-tensorrt-optimization.md`
2. Proceed to Lecture 02 on TensorRT
3. Set up your development environment with TensorRT installed
4. Review the quiz questions to test your understanding

---

**Lecture Duration**: 4 hours (reading + exercises)
**Difficulty**: Intermediate to Advanced
**Prerequisites**: Deep learning fundamentals, Python, PyTorch/TensorFlow
