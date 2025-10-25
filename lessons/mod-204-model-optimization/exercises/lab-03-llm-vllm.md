# Lab 03: LLM Deployment with vLLM

## Objectives

Deploy and optimize a Large Language Model using vLLM:
1. Set up vLLM for LLaMA-2 or Mistral models
2. Configure continuous batching and PagedAttention
3. Implement request serving with OpenAI-compatible API
4. Optimize KV cache configuration
5. Benchmark throughput and latency
6. Compare with naive HuggingFace Transformers serving

**Estimated Time**: 6 hours

## Prerequisites

- Completed Lecture 06: LLM Inference Optimization
- NVIDIA GPU with 24GB+ VRAM (or multiple GPUs)
- vLLM installed (`pip install vllm`)
- HuggingFace account (for gated models)

## Part 1: Setup and Basic Deployment (60 minutes)

### Task 1.1: Install and Verify vLLM

```bash
# Install vLLM
pip install vllm

# Verify installation
python -c "import vllm; print(vllm.__version__)"

# Log in to HuggingFace (for LLaMA-2)
huggingface-cli login
```

### Task 1.2: Deploy LLaMA-2-7B with vLLM

```python
from vllm import LLM, SamplingParams

# TODO: Initialize vLLM with LLaMA-2-7B
# Configure:
# - tensor_parallel_size (based on available GPUs)
# - dtype (float16)
# - max_model_len (4096)
# - gpu_memory_utilization (0.9)

llm = LLM(
    # YOUR CODE HERE
)

# Test simple generation
prompts = ["Explain machine learning in one sentence."]
sampling_params = SamplingParams(temperature=0.7, max_tokens=100)

outputs = llm.generate(prompts, sampling_params)
print(outputs[0].outputs[0].text)
```

## Part 2: OpenAI-Compatible API Server (90 minutes)

### Task 2.1: Start vLLM Server

```bash
# TODO: Start vLLM server with proper configuration
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --tensor-parallel-size 1 \
    --dtype float16 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9 \
    --port 8000
```

### Task 2.2: Implement Client

```python
from openai import OpenAI
import time

# TODO: Implement OpenAI-compatible client
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

def chat_completion(messages, max_tokens=512, stream=False):
    """
    TODO: Implement chat completion
    - Send request to vLLM server
    - Handle streaming responses
    - Measure Time-To-First-Token (TTFT)
    - Measure Time-Per-Output-Token (TPOT)
    """
    # YOUR CODE HERE
    pass

# Test
messages = [
    {"role": "user", "content": "What is continuous batching?"}
]
response = chat_completion(messages, stream=True)
```

## Part 3: KV Cache Optimization (75 minutes)

### Task 3.1: Configure KV Cache Block Size

```python
# TODO: Experiment with different block sizes
# Try: 8, 16, 32, 64
# Measure:
# - Memory utilization
# - Throughput
# - Latency

for block_size in [8, 16, 32, 64]:
    llm = LLM(
        model="meta-llama/Llama-2-7b-chat-hf",
        block_size=block_size,
        # YOUR CODE HERE
    )
    # Benchmark...
```

### Task 3.2: Test KV Cache Quantization

```python
# TODO: Enable KV cache quantization
# Try INT8 and FP8 (if supported)
# Measure memory savings vs accuracy impact

llm_kv_int8 = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    kv_cache_dtype="int8",
    # YOUR CODE HERE
)
```

## Part 4: Throughput Benchmarking (90 minutes)

### Task 4.1: Implement Load Generator

```python
import asyncio
import numpy as np

async def load_test(num_requests, concurrency, prompt_length, output_length):
    """
    Load test vLLM server

    TODO:
    - Generate num_requests with random prompts
    - Send with specified concurrency
    - Measure:
      - Total throughput (tokens/second)
      - Request latency distribution
      - Time-To-First-Token (TTFT)
      - Time-Per-Output-Token (TPOT)
    """
    # YOUR CODE HERE
    pass

# Run load tests
results = asyncio.run(load_test(
    num_requests=100,
    concurrency=10,
    prompt_length=512,
    output_length=256
))
```

### Task 4.2: Compare Batch Sizes

```python
# TODO: Test different concurrency levels
# Measure throughput vs latency trade-off
# Plot throughput curve

concurrency_levels = [1, 2, 4, 8, 16, 32, 64]
results = []

for concurrency in concurrency_levels:
    result = asyncio.run(load_test(
        num_requests=100,
        concurrency=concurrency,
        prompt_length=512,
        output_length=256
    ))
    results.append(result)

# TODO: Create throughput vs latency plot
```

## Part 5: Comparison with Baseline (90 minutes)

### Task 5.1: Implement HuggingFace Transformers Serving

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# TODO: Implement naive serving with HF Transformers
class HFBaselineServer:
    def __init__(self, model_name):
        # Load model and tokenizer
        # YOUR CODE HERE
        pass

    def generate(self, prompts, max_tokens=512):
        # TODO: Implement generation
        # Use simple batching or no batching
        # YOUR CODE HERE
        pass

baseline = HFBaselineServer("meta-llama/Llama-2-7b-chat-hf")
```

### Task 5.2: Benchmark Comparison

```python
# TODO: Compare vLLM vs HF Transformers
# Metrics:
# - Throughput (tokens/second)
# - Latency (ms)
# - Memory usage (GB)
# - GPU utilization (%)
# - Batch efficiency

# Run same load test on both
results_vllm = benchmark(vllm_client)
results_baseline = benchmark(baseline)

# Create comparison table and charts
```

**Expected Results**: vLLM should achieve 5-10x better throughput

## Part 6: Advanced Features (60 minutes)

### Task 6.1: Prefix Caching

```python
# TODO: Test prefix caching with shared system prompt
system_prompt = "You are a helpful AI assistant."

prompts = [
    system_prompt + "\n\nUser: " + query
    for query in user_queries
]

# Measure:
# - TTFT improvement for requests with same prefix
# - Memory savings
```

### Task 6.2: Multi-GPU Tensor Parallelism

```python
# TODO: Deploy with tensor parallelism
# Use 2 or 4 GPUs

llm_tp = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",  # Larger model
    tensor_parallel_size=4,
    # YOUR CODE HERE
)

# Measure scaling efficiency
```

## Deliverables

1. Deployed vLLM server with optimal configuration
2. Load testing framework
3. Benchmark results (vLLM vs baseline)
4. Throughput vs latency curves
5. KV cache optimization analysis
6. Performance report with recommendations

## Expected Performance

For LLaMA-2-7B on A100 (40GB):

| Metric | vLLM | HF Baseline | Improvement |
|--------|------|-------------|-------------|
| Throughput | 400+ tokens/s | 50-80 tokens/s | 5-8x |
| TTFT | <200ms | 200-500ms | 1-2.5x |
| Memory Utilization | 85-95% | 40-60% | 1.5-2x |

## Troubleshooting

- OOM errors: Reduce max_model_len or gpu_memory_utilization
- Slow throughput: Increase concurrency in client
- High TTFT: Check if CPU preprocessing is bottleneck

---

**Lab Duration**: 6 hours
**Difficulty**: Advanced
