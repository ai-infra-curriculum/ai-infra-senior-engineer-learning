# Lecture 06: LLM Inference Optimization

## Learning Objectives

By the end of this lecture, you will be able to:

- Design LLM serving architectures that address autoregressive generation bottlenecks including KV cache memory growth, memory bandwidth limitations, and latency vs throughput trade-offs
- Implement vLLM with PagedAttention achieving 8-10x throughput improvement through block-based KV cache management and continuous batching with 80-95% memory utilization
- Configure TensorRT-LLM engines with multi-GPU tensor parallelism, advanced quantization (FP16, INT8, FP8, INT4 AWQ/GPTQ), and in-flight batching for maximum performance
- Architect speculative decoding systems using draft models to generate candidate tokens achieving 2-3x speedup with parallel verification by target models
- Implement KV cache optimization techniques including INT8/FP8 quantization (2-4x memory savings), Multi-Query Attention (MQA), and Grouped-Query Attention (GQA)
- Configure multi-GPU LLM serving with tensor parallelism (split weights) and pipeline parallelism (split layers) using NVLink for efficient all-reduce communication
- Design continuous batching systems that dynamically adjust batch size as requests arrive and finish achieving 2-10x better throughput and lower latency than static batching
- Deploy production LLM serving systems with appropriate quantization, memory utilization targets (90%), monitoring (TTFT, TPOT, throughput), and graceful degradation strategies

## Table of Contents
1. [LLM Inference Challenges](#challenges)
2. [Autoregressive Generation Bottlenecks](#bottlenecks)
3. [vLLM and PagedAttention](#vllm)
4. [TensorRT-LLM](#tensorrt-llm)
5. [SGLang and Speculative Decoding](#sglang)
6. [Memory Optimization](#memory)
7. [Multi-GPU Serving](#multi-gpu)
8. [Request Batching Strategies](#batching)
9. [Framework Comparison](#comparison)
10. [Production Best Practices](#best-practices)

<a name="challenges"></a>
## 1. LLM Inference Challenges

### The LLM Inference Problem

Large Language Models present unique optimization challenges:

**Scale**: 7B to 175B+ parameters
- GPT-3: 175B parameters (350GB in FP16)
- LLaMA-2-70B: 140GB in FP16
- Cannot fit in single GPU memory without optimization

**Autoregressive Generation**: Sequential token-by-token generation
- Each token depends on previous tokens
- Cannot fully parallelize generation
- Latency compounds with sequence length

**Memory Bottleneck**: KV cache grows linearly with sequence length
- For LLaMA-70B: ~500MB per 1000 tokens of KV cache
- Long contexts (32k+ tokens) require tens of GB

**Throughput vs Latency**: Conflicting requirements
- Users want low Time-To-First-Token (TTFT) < 300ms
- Servers want high tokens/second throughput
- Static batching hurts latency, no batching hurts throughput

### Economic Impact

**Unoptimized LLM Serving**:
- LLaMA-70B on 4x A100: ~50 tokens/second
- Cost: $16/hour → $11,520/month
- Cannot serve high traffic economically

**Optimized LLM Serving**:
- Same model with vLLM: 400+ tokens/second (8x)
- Cost: $8/hour with better hardware utilization
- Viable for production at scale

<a name="bottlenecks"></a>
## 2. Autoregressive Generation Bottlenecks

### 2.1 Two-Phase Inference

**Prefill Phase**: Process input prompt
- Matrix-matrix operations (batch_size × seq_len)
- Compute-bound
- Can leverage parallelism
- Fast: typically <100ms for most prompts

**Decode Phase**: Generate tokens sequentially
- Matrix-vector operations (batch_size × 1)
- Memory-bound (reading KV cache)
- Sequential by nature
- Slow: 20-50ms per token

```python
# Simplified LLM generation
def generate(model, input_ids, max_length=100):
    # Prefill phase: process entire prompt at once
    past_key_values = None
    current_ids = input_ids

    # First forward pass (prefill)
    outputs = model(current_ids, past_key_values=past_key_values)
    past_key_values = outputs.past_key_values  # Cache KV for all prompt tokens
    next_token = outputs.logits[:, -1, :].argmax(dim=-1)

    generated_ids = [next_token]

    # Decode phase: generate tokens one by one
    for _ in range(max_length - 1):
        # Each iteration: single token input, reuse KV cache
        outputs = model(
            next_token.unsqueeze(1),
            past_key_values=past_key_values  # Growing KV cache
        )
        past_key_values = outputs.past_key_values  # Update cache
        next_token = outputs.logits[:, -1, :].argmax(dim=-1)

        generated_ids.append(next_token)

        if next_token == eos_token_id:
            break

    return torch.cat(generated_ids)
```

### 2.2 KV Cache Memory Growth

KV cache size formula:
```
KV_cache_size = 2 × num_layers × num_heads × head_dim × seq_len × batch_size × sizeof(dtype)

For LLaMA-70B (80 layers, 64 heads, 128 head_dim, FP16):
= 2 × 80 × 64 × 128 × seq_len × batch_size × 2 bytes
= 2.62 MB per token per sequence

For 2048 token sequence: 5.4 GB per sequence
For batch of 32: 172 GB! (exceeds A100 80GB memory)
```

**Problem**: KV cache dominates memory usage for long contexts.

<a name="vllm"></a>
## 3. vLLM and PagedAttention

vLLM revolutionized LLM serving with PagedAttention and continuous batching.

### 3.1 PagedAttention

**Inspiration**: Virtual memory in operating systems

**Traditional KV Cache**: Contiguous memory allocation
```python
# Traditional: Pre-allocate max_length for each sequence
kv_cache = torch.zeros(
    batch_size,
    num_layers,
    max_seq_len,  # Wasteful if actual length < max
    num_heads,
    head_dim
)
# Memory wasted on unused capacity
# Cannot share memory between requests
```

**PagedAttention**: Divide KV cache into fixed-size blocks
```python
# PagedAttention: Allocate blocks as needed
block_size = 16  # tokens per block

# Blocks allocated dynamically
blocks = []
for _ in range(num_blocks_needed):
    block = allocate_block(block_size)
    blocks.append(block)

# Logical sequence stored in non-contiguous blocks
# Similar to virtual memory pages

# Benefits:
# 1. No memory fragmentation
# 2. Efficient memory sharing (for prefix sharing)
# 3. Can pack variable-length sequences efficiently
```

**Memory Efficiency**: vLLM achieves near-zero waste
- Traditional: 20-40% memory utilization (rest is padding)
- vLLM: 80-95% memory utilization

### 3.2 vLLM Architecture

```
┌─────────────────────────────────────────┐
│       Request Queue                      │
│  (Incoming user requests)                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│     Continuous Batching Scheduler        │
│  - Dynamic request admission              │
│  - Preemption and swapping               │
│  - Priority-based scheduling             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       Block Manager                      │
│  - KV cache block allocation             │
│  - Memory pooling                        │
│  - Block sharing (prefix caching)        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      PagedAttention Kernels              │
│  - Custom CUDA kernels                   │
│  - Block-level attention computation     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        Model Execution                   │
│  (LLaMA, GPT, Mistral, etc.)            │
└─────────────────────────────────────────┘
```

### 3.3 Using vLLM

```python
from vllm import LLM, SamplingParams

# Initialize vLLM engine
llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,  # 4 GPUs
    dtype="float16",
    max_model_len=4096,      # Max context length
    gpu_memory_utilization=0.9,  # Use 90% of GPU memory
    enforce_eager=False,     # Use CUDA graphs for speed
)

# Sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    stop=["</s>"]
)

# Single request
prompts = ["Explain quantum computing in simple terms."]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Generated: {output.outputs[0].text}")

# Batch requests (automatically optimized)
prompts = [
    "What is AI?",
    "Explain neural networks.",
    "How does deep learning work?",
    # ... hundreds more
]
outputs = llm.generate(prompts, sampling_params)
# vLLM automatically batches and schedules for optimal throughput
```

### 3.4 vLLM Server (OpenAI-compatible API)

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-70b-chat-hf \
    --tensor-parallel-size 4 \
    --dtype float16 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9

# Client usage (OpenAI API compatible)
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # vLLM doesn't require auth
)

response = client.chat.completions.create(
    model="meta-llama/Llama-2-70b-chat-hf",
    messages=[
        {"role": "user", "content": "Explain PagedAttention"}
    ],
    max_tokens=512,
    temperature=0.7,
    stream=True  # Streaming response
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 3.5 Advanced vLLM Features

**Prefix Caching**: Share common prefixes between requests
```python
# System prompt used by all requests
system_prompt = "You are a helpful AI assistant. Always be polite and concise."

# Requests with same prefix share KV cache blocks
requests = [
    system_prompt + "\n\nUser: What is 2+2?",
    system_prompt + "\n\nUser: What is AI?",
    system_prompt + "\n\nUser: Explain Python.",
]

# vLLM automatically detects shared prefix
# Only computes attention for shared blocks once
# 3x memory savings, faster TTFT
```

**Speculative Decoding** (experimental):
```python
llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    speculative_model="meta-llama/Llama-2-7b-chat-hf",  # Draft model
    num_speculative_tokens=5,  # Generate 5 candidates
    # Draft model generates candidates, main model validates
    # 1.5-2x speedup for compatible draft models
)
```

<a name="tensorrt-llm"></a>
## 4. TensorRT-LLM

NVIDIA's LLM optimization library with TensorRT backend.

### 4.1 TensorRT-LLM Features

- **Maximum Performance**: Hand-optimized CUDA kernels
- **Quantization**: FP16, INT8, FP8, INT4 (AWQ, GPTQ)
- **Multi-GPU**: Tensor parallelism, pipeline parallelism
- **In-flight Batching**: Continuous batching similar to vLLM
- **Custom Attention**: FlashAttention, PagedAttention variants

### 4.2 Building TensorRT-LLM Engine

```python
import tensorrt_llm
from tensorrt_llm.models import LLaMAForCausalLM
from tensorrt_llm.builder import Builder

# Load model configuration
config = {
    'architecture': 'LlamaForCausalLM',
    'dtype': 'float16',
    'num_layers': 80,
    'num_heads': 64,
    'hidden_size': 8192,
    'vocab_size': 32000,
    'max_position_embeddings': 4096,
}

# Build TensorRT engine
builder = Builder()
builder_config = builder.create_builder_config(
    name='llama_70b',
    precision='float16',
    tensor_parallel=4,  # 4-way tensor parallelism
    max_batch_size=128,
    max_input_len=2048,
    max_output_len=512,
    max_beam_width=1,
)

# Build and save engine
engine = builder.build_engine(model_config, builder_config)
engine.save('llama_70b_tp4_fp16.engine')
```

### 4.3 TensorRT-LLM Inference

```python
import tensorrt_llm
from tensorrt_llm.runtime import ModelRunner

# Load engine
runner = ModelRunner.from_dir(
    engine_dir='llama_70b_tp4_fp16.engine',
    rank=0,  # GPU rank for tensor parallelism
)

# Tokenize input
input_text = "Explain machine learning"
input_ids = tokenizer.encode(input_text, return_tensors='pt')

# Run inference
outputs = runner.generate(
    input_ids,
    max_new_tokens=512,
    temperature=0.7,
    top_k=50,
    top_p=0.9,
    streaming=True  # Enable streaming
)

# Streaming output
for token in outputs:
    print(tokenizer.decode(token), end="", flush=True)
```

### 4.4 TensorRT-LLM Quantization

**INT8 Quantization**:
```python
# Quantize to INT8
quant_config = {
    'quant_mode': 'int8_weight_only',  # or 'int8_kv_cache'
    'per_channel': True,
    'per_token': True,
}

engine = builder.build_engine(model_config, builder_config, quant_config)
# 2x memory reduction, 1.5-2x speedup
```

**INT4 with AWQ/GPTQ**:
```python
# Quantize to INT4 using AWQ
quant_config = {
    'quant_mode': 'int4_awq',
    'group_size': 128,
}

engine = builder.build_engine(model_config, builder_config, quant_config)
# 4x memory reduction, 2-3x speedup
# LLaMA-70B: 140GB → 35GB, fits on single A100!
```

<a name="sglang"></a>
## 5. SGLang and Speculative Decoding

SGLang (Structured Generation Language) focuses on structured output and speculative decoding.

### 5.1 Speculative Decoding

**Idea**: Use small "draft" model to generate candidate tokens, verify with large model

```
Normal generation (sequential):
Large Model: T1 → T2 → T3 → T4 → T5
Time: 5 × latency

Speculative decoding (parallel):
Draft Model: T1,T2,T3,T4,T5 (fast, may be wrong)
      ↓
Large Model: Verify all at once (parallel)
             Accept correct tokens, reject rest

If 3/5 tokens accepted:
Time: 1 × draft_latency + 1 × verify_latency
Speedup: ~2-3x (depends on acceptance rate)
```

### 5.2 SGLang Implementation

```python
import sglang as sgl

# Define draft and target models
@sgl.function
def speculative_generate(s, prompt, max_tokens=100):
    # Small draft model (e.g., LLaMA-7B)
    s += sgl.gen(
        prompt,
        max_tokens=max_tokens,
        model="meta-llama/Llama-2-7b-chat-hf",
        name="draft"
    )

    # Large target model verifies (e.g., LLaMA-70B)
    s += sgl.gen(
        prompt,
        max_tokens=max_tokens,
        model="meta-llama/Llama-2-70b-chat-hf",
        draft=s["draft"],  # Use draft as candidates
        name="output"
    )

    return s["output"]

# Run with speculative decoding
result = speculative_generate.run(
    prompt="Explain quantum mechanics",
    max_tokens=512
)
# 2-3x faster than normal generation
```

### 5.3 Structured Generation

SGLang excels at structured outputs (JSON, code, etc.):

```python
@sgl.function
def extract_structured_data(s, text):
    s += sgl.user("Extract person info from: " + text)
    s += sgl.assistant(sgl.gen("response", max_tokens=200))

    # Parse JSON
    with sgl.json_mode():
        s += "{"
        s += '"name": ' + sgl.gen("name", max_tokens=20)
        s += ', "age": ' + sgl.gen("age", max_tokens=5, regex=r"\d+")
        s += ', "occupation": ' + sgl.gen("occupation", max_tokens=30)
        s += "}"

    return s

# Guaranteed valid JSON output
result = extract_structured_data.run(
    text="John Smith is a 45-year-old software engineer."
)
```

<a name="memory"></a>
## 6. Memory Optimization

### 6.1 KV Cache Quantization

Quantize KV cache to INT8 or FP8 for 2-4x memory savings:

```python
# vLLM with KV cache quantization
llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,
    dtype="float16",
    kv_cache_dtype="int8",  # or "fp8"
    # 2x memory savings with minimal accuracy loss
)
```

### 6.2 Multi-Query Attention (MQA)

Share key/value projections across all attention heads:

```
Standard Multi-Head Attention:
Q: [batch, num_heads, seq_len, head_dim]
K: [batch, num_heads, seq_len, head_dim]  ← Large KV cache
V: [batch, num_heads, seq_len, head_dim]  ← Large KV cache

Multi-Query Attention:
Q: [batch, num_heads, seq_len, head_dim]
K: [batch, 1, seq_len, head_dim]  ← Single shared key (num_heads smaller)
V: [batch, 1, seq_len, head_dim]  ← Single shared value

Memory savings: num_heads × reduction (e.g., 32x smaller KV cache)
Speed: Faster due to less memory bandwidth
Accuracy: Minimal loss if trained with MQA
```

### 6.3 Grouped-Query Attention (GQA)

Middle ground between MHA and MQA:

```
Grouped-Query Attention:
Q: [batch, num_heads, seq_len, head_dim]
K: [batch, num_kv_heads, seq_len, head_dim]  ← num_kv_heads < num_heads
V: [batch, num_kv_heads, seq_len, head_dim]

Example: 32 query heads, 4 KV heads → 8x memory savings
```

LLaMA-2, Mistral use GQA by default.

<a name="multi-gpu"></a>
## 7. Multi-GPU Serving

### 7.1 Tensor Parallelism

Split model weights across GPUs:

```python
# vLLM with tensor parallelism
llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,  # Split across 4 GPUs
    # Each GPU holds 1/4 of model weights
    # Forward pass requires all-reduce communication
)

# TensorRT-LLM
builder_config = builder.create_builder_config(
    tensor_parallel=4,  # 4-way TP
    pipeline_parallel=2,  # 2-way PP (optional)
)
```

**Communication Overhead**:
- All-reduce after each layer
- NVLink: ~300 GB/s (acceptable)
- PCIe: ~32 GB/s (bottleneck)

### 7.2 Pipeline Parallelism

Split model layers across GPUs:

```
GPU 0: Layers 0-19   ┐
GPU 1: Layers 20-39  ├─ Process batch in pipeline
GPU 2: Layers 40-59  │
GPU 3: Layers 60-79  ┘

Micro-batching: Split batch into mini-batches
Stage 1 → Stage 2 → Stage 3 → Stage 4
     ↓        ↓        ↓
   (overlap computation with communication)
```

<a name="batching"></a>
## 8. Request Batching Strategies

### 8.1 Static Batching

Traditional: Wait for full batch before processing:

```python
batch_size = 32
requests = []

# Wait until batch is full
while len(requests) < batch_size:
    request = await receive_request()
    requests.append(request)

# Process entire batch
outputs = model(requests)
```

**Problem**: High latency for early requests (waiting for batch to fill).

### 8.2 Continuous Batching

Process requests as they arrive, dynamically adjust batch:

```python
# vLLM/TensorRT-LLM continuous batching
running_requests = []

while True:
    # Add new requests
    if new_request_available():
        running_requests.append(new_request)

    # Remove finished requests
    running_requests = [r for r in running_requests if not r.finished]

    # Generate next token for all running requests
    model.generate_next_token_batch(running_requests)

    # No waiting, optimal GPU utilization
```

**Benefit**: 2-10x better throughput, lower latency.

<a name="comparison"></a>
## 9. Framework Comparison

| Feature | vLLM | TensorRT-LLM | SGLang | Text Generation Inference |
|---------|------|--------------|--------|---------------------------|
| **Ease of Use** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★☆ |
| **Performance** | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| **Memory Efficiency** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **Model Support** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★☆ |
| **Quantization** | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★☆☆ |
| **Multi-GPU** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Speculative Decoding** | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| **Structured Generation** | ★★☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★☆☆ |

**Recommendation**:
- **vLLM**: Best default choice (ease + performance)
- **TensorRT-LLM**: Maximum performance, willing to invest in setup
- **SGLang**: Structured outputs, speculative decoding focus
- **TGI**: HuggingFace ecosystem integration

<a name="best-practices"></a>
## 10. Production Best Practices

### Deployment Checklist

```python
# 1. Choose appropriate quantization
if gpu_memory_limited:
    precision = "int4_awq"  # 4x compression
elif latency_critical:
    precision = "fp16"  # Fastest
else:
    precision = "int8"  # Balanced

# 2. Configure memory usage
llm = LLM(
    model=model_name,
    dtype=precision,
    gpu_memory_utilization=0.90,  # Leave 10% headroom
    max_model_len=4096,  # Set based on use case
    tensor_parallel_size=num_gpus,
)

# 3. Set appropriate sampling parameters
default_sampling = SamplingParams(
    temperature=0.7,  # Tune for use case
    top_p=0.9,
    max_tokens=512,  # Limit to prevent runaway
    stop=["</s>", "\n\nUser:"],  # Stop sequences
)

# 4. Implement request queuing
from asyncio import Queue

request_queue = Queue(maxsize=1000)

# 5. Monitor metrics
metrics = {
    'ttft': [],  # Time to first token
    'tpot': [],  # Time per output token
    'throughput': [],  # Tokens/second
    'queue_depth': [],
    'gpu_memory': [],
}

# 6. Implement graceful degradation
if queue_depth > threshold:
    # Reduce max_tokens
    # Increase batch size
    # Scale horizontally
```

## Summary

LLM inference optimization is critical for production viability:

- **vLLM**: PagedAttention + continuous batching (8-10x improvement)
- **TensorRT-LLM**: Maximum performance with quantization
- **SGLang**: Speculative decoding and structured generation
- **Memory**: KV cache optimization, MQA/GQA, quantization
- **Multi-GPU**: Tensor/pipeline parallelism for large models
- **Batching**: Continuous batching for optimal utilization

Modern LLM serving achieves:
- 400+ tokens/second (70B models)
- <300ms Time-To-First-Token
- 50-75% cost reduction vs naive approaches

## Next Steps

1. Complete Lab 03: Deploy LLM with vLLM
2. Read Lecture 07: Continuous Batching and KV Cache
3. Benchmark different serving frameworks

---

**Lecture Duration**: 12 hours
**Difficulty**: Advanced
