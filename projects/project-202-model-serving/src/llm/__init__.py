"""
Large Language Model (LLM) Serving Module

This module provides vLLM-based serving capabilities for large language models
with optimized inference, streaming responses, and batching.

TODO for students:
- Configure vLLM for optimal GPU memory usage
- Implement continuous batching for better throughput
- Add support for different LLM architectures (GPT, LLaMA, etc.)
- Implement token streaming with SSE (Server-Sent Events)
- Add prompt caching and KV cache optimization
"""

from .vllm_server import (
    VLLMServer,
    VLLMConfig,
    start_vllm_server,
)
from .streaming import (
    StreamingResponse,
    stream_tokens,
    TokenIterator,
)
from .llm_config import (
    LLMConfig,
    ModelConfig,
    SamplingParams,
    load_llm_config,
)

__all__ = [
    # vLLM Server
    "VLLMServer",
    "VLLMConfig",
    "start_vllm_server",
    # Streaming
    "StreamingResponse",
    "stream_tokens",
    "TokenIterator",
    # Configuration
    "LLMConfig",
    "ModelConfig",
    "SamplingParams",
    "load_llm_config",
]
