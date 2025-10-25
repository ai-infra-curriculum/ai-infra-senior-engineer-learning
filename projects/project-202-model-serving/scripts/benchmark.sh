#!/bin/bash
# Comprehensive benchmarking script for model serving
# TODO for students: Add GPU profiling, add cost analysis, create comparison charts

set -euo pipefail

echo "========================================="
echo "Model Serving Benchmark Suite"
echo "========================================="

# Configuration
RESULTS_DIR="${RESULTS_DIR:-./results}"
MODEL_PATH="${MODEL_PATH:-./models/resnet50.engine}"
VLLM_URL="${VLLM_URL:-http://localhost:8000}"
SERVER_URL="${SERVER_URL:-http://localhost:8080}"

mkdir -p "$RESULTS_DIR"

# Benchmark TensorRT
echo -e "\n[1/4] Benchmarking TensorRT model..."
python benchmarks/benchmark_tensorrt.py \
  --model "$MODEL_PATH" \
  --batch-sizes 1 2 4 8 16 32 \
  --iterations 1000 \
  --precision fp16 \
  --output "$RESULTS_DIR/tensorrt_benchmark.json" || echo "TensorRT benchmark skipped"

# Benchmark vLLM
echo -e "\n[2/4] Benchmarking vLLM server..."
python benchmarks/benchmark_vllm.py \
  --server-url "$VLLM_URL" \
  --model gpt2 \
  --num-requests 100 \
  --concurrent 10 \
  --prompt-lengths 50 100 500 1000 \
  --output "$RESULTS_DIR/vllm_benchmark.json" || echo "vLLM benchmark skipped"

# Load testing
echo -e "\n[3/4] Running load test..."
python benchmarks/load_test.py \
  --host "$SERVER_URL" \
  --users 100 \
  --spawn-rate 10 \
  --duration 60 \
  --output "$RESULTS_DIR/load_test.json" || echo "Load test skipped"

# Analysis
echo -e "\n[4/4] Analyzing results..."
python benchmarks/benchmark_results_analysis.py \
  --tensorrt "$RESULTS_DIR/tensorrt_benchmark.json" \
  --vllm "$RESULTS_DIR/vllm_benchmark.json" \
  --loadtest "$RESULTS_DIR/load_test.json" \
  --output "$RESULTS_DIR/benchmark_comparison.json"

echo -e "\n========================================="
echo "Benchmark complete! Results in: $RESULTS_DIR"
echo "========================================="
