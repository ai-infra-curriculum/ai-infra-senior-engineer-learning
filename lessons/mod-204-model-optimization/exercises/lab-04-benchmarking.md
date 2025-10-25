# Lab 04: Comprehensive Inference Benchmarking

## Objectives

Build a comprehensive benchmarking framework for model optimization:
1. Design end-to-end benchmarking pipeline
2. Measure latency, throughput, memory, accuracy
3. Profile GPU utilization and bottlenecks
4. Compare multiple optimization techniques
5. Generate production-ready performance reports
6. Identify optimization opportunities

**Estimated Time**: 4 hours

## Part 1: Benchmarking Framework (90 minutes)

### Task 1.1: Implement Latency Benchmarking

```python
import time
import torch
import numpy as np
from collections import defaultdict

class LatencyBenchmark:
    """
    Comprehensive latency benchmarking
    """
    def __init__(self, model, device='cuda'):
        self.model = model
        self.device = device

    def benchmark(self, inputs, num_iterations=1000, warmup=10):
        """
        TODO: Implement latency benchmarking
        - Warmup iterations
        - Measure each iteration
        - Record timestamps
        - Compute statistics: mean, median, p50, p95, p99, std
        - Use CUDA synchronization for accurate timing
        """
        # YOUR CODE HERE
        pass

    def profile_layers(self, inputs):
        """
        TODO: Profile per-layer execution time
        - Use hooks to measure each layer
        - Identify bottleneck layers
        - Return breakdown
        """
        # YOUR CODE HERE
        pass
```

### Task 1.2: Implement Throughput Benchmarking

```python
class ThroughputBenchmark:
    """
    Throughput benchmarking for various batch sizes
    """
    def benchmark_batch_sizes(self, model, batch_sizes, duration_sec=60):
        """
        TODO: Benchmark throughput across batch sizes
        - Test each batch size
        - Measure QPS (queries per second)
        - Measure tokens per second (for sequence models)
        - Track GPU memory usage
        - Return throughput curves
        """
        # YOUR CODE HERE
        pass

    def find_optimal_batch_size(self, model, target_latency_ms=100):
        """
        TODO: Find largest batch size meeting latency constraint
        - Binary search for optimal batch size
        - Return batch size and throughput
        """
        # YOUR CODE HERE
        pass
```

## Part 2: GPU Profiling (60 minutes)

### Task 2.1: NVIDIA Nsight Integration

```python
class GPUProfiler:
    """
    Profile GPU utilization and memory
    """
    def profile_with_nsight(self, model, inputs):
        """
        TODO: Integrate NVIDIA Nsight profiling
        - Run model with profiling enabled
        - Capture kernel execution times
        - Analyze memory bandwidth
        - Identify compute vs memory bound
        """
        # YOUR CODE HERE
        pass

    def analyze_gpu_utilization(self, model, inputs, duration_sec=60):
        """
        TODO: Monitor GPU utilization over time
        - Use nvidia-smi or pynvml
        - Track GPU utilization %, memory usage, temperature
        - Generate utilization time series
        """
        # YOUR CODE HERE
        pass
```

## Part 3: Accuracy Benchmarking (45 minutes)

### Task 3.1: Implement Accuracy Metrics

```python
class AccuracyBenchmark:
    """
    Measure accuracy for optimized models
    """
    def compare_outputs(self, model_baseline, model_optimized, test_loader):
        """
        TODO: Compare outputs between baseline and optimized
        - Compute output similarity (cosine, MSE)
        - Measure accuracy on test set
        - Compute per-class accuracy
        - Identify degradation patterns
        """
        # YOUR CODE HERE
        pass

    def analyze_numerical_stability(self, model_baseline, model_optimized):
        """
        TODO: Analyze numerical differences
        - Check for NaN/Inf
        - Measure max absolute difference
        - Compute relative error
        """
        # YOUR CODE HERE
        pass
```

## Part 4: Multi-Model Comparison (90 minutes)

### Task 4.1: Benchmark Suite

```python
class BenchmarkSuite:
    """
    Compare multiple models/optimizations
    """
    def __init__(self, models_dict):
        """
        Args:
            models_dict: {'name': model} dictionary
        """
        self.models = models_dict
        self.results = defaultdict(dict)

    def run_all_benchmarks(self, test_data):
        """
        TODO: Run comprehensive benchmarks on all models
        - Latency (p50, p95, p99)
        - Throughput (various batch sizes)
        - Memory usage
        - GPU utilization
        - Accuracy
        - Model size
        """
        for name, model in self.models.items():
            print(f"Benchmarking {name}...")
            # YOUR CODE HERE

        return self.results

    def generate_comparison_report(self):
        """
        TODO: Generate comparison report
        - Create comparison tables
        - Plot speedup charts
        - Accuracy vs speedup trade-off
        - Memory usage comparison
        - Recommendations
        """
        # YOUR CODE HERE
        pass
```

### Task 4.2: Run Comprehensive Comparison

```python
# TODO: Compare all optimization techniques from previous labs
models = {
    'FP32 Baseline': baseline_model,
    'FP16 TensorRT': tensorrt_fp16_model,
    'INT8 TensorRT': tensorrt_int8_model,
    'PyTorch INT8': pytorch_int8_model,
    'Pruned + Quantized': pruned_quant_model,
}

suite = BenchmarkSuite(models)
results = suite.run_all_benchmarks(test_loader)
suite.generate_comparison_report()
```

## Part 5: Production Readiness (45 minutes)

### Task 5.1: Stress Testing

```python
class StressTest:
    """
    Stress test for production deployment
    """
    def sustained_load_test(self, model, duration_minutes=10):
        """
        TODO: Test model under sustained load
        - Run for extended duration
        - Monitor for memory leaks
        - Check for performance degradation over time
        - Measure thermal throttling effects
        """
        # YOUR CODE HERE
        pass

    def variable_load_test(self, model):
        """
        TODO: Test with variable request patterns
        - Bursty traffic
        - Gradual ramp-up
        - Mixed batch sizes
        - Concurrent requests
        """
        # YOUR CODE HERE
        pass
```

## Part 6: Reporting and Visualization (30 minutes)

### Task 6.1: Generate Performance Report

```python
def generate_performance_report(results):
    """
    TODO: Create comprehensive report
    Include:
    - Executive summary
    - Latency comparison table
    - Throughput comparison chart
    - Memory usage chart
    - Accuracy vs speedup scatter plot
    - Speedup breakdown (by technique)
    - Cost analysis (if applicable)
    - Recommendations for production
    """
    # YOUR CODE HERE

    # Save as PDF/HTML
    report.save('performance_report.html')
```

### Task 6.2: Create Dashboards

```python
# TODO: Create interactive dashboard with plotly/dash
# Include:
# - Real-time metrics
# - Historical trends
# - Drill-down by model/technique
# - Export capabilities
```

## Deliverables

1. Benchmarking framework (latency, throughput, GPU profiling)
2. Multi-model comparison results
3. Stress test results
4. Performance report (HTML/PDF)
5. Interactive dashboard
6. Recommendations document

## Expected Deliverables Format

### Latency Comparison Table

| Model | p50 (ms) | p95 (ms) | p99 (ms) | Speedup |
|-------|----------|----------|----------|---------|
| FP32 Baseline | 150 | 160 | 165 | 1.0x |
| FP16 TensorRT | 50 | 55 | 60 | 3.0x |
| INT8 TensorRT | 35 | 40 | 45 | 4.3x |

### Throughput Comparison

```
Chart: Throughput vs Batch Size
- X-axis: Batch size (1, 4, 8, 16, 32, 64)
- Y-axis: QPS
- Lines: Each optimization technique
```

### Accuracy vs Speedup

```
Scatter plot:
- X-axis: Speedup
- Y-axis: Accuracy
- Points: Each model/technique
- Ideal: Top-right (high speedup, high accuracy)
```

## Bonus: MLPerf Benchmark

```python
# TODO: Run MLPerf inference benchmark
# Compare against industry standards
# Submit results to MLPerf leaderboard
```

---

**Lab Duration**: 4 hours
**Difficulty**: Intermediate to Advanced
