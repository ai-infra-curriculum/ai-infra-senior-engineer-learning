"""
vLLM (Large Language Model) Serving Benchmark

This script benchmarks vLLM server performance for text generation tasks,
measuring latency, throughput, and time-to-first-token (TTFT) metrics.

TODO for students:
- Benchmark continuous batching performance
- Compare PagedAttention vs traditional attention
- Measure KV cache efficiency
- Test different sequence lengths and batch sizes
- Profile token generation rate vs batch size
"""

import argparse
import asyncio
import time
import numpy as np
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import json
import aiohttp

# TODO: Import from src.llm module once implemented
# from src.llm import VLLMServer, SamplingParams


@dataclass
class VLLMBenchmarkConfig:
    """Configuration for vLLM benchmarking."""
    server_url: str
    model_name: str
    num_requests: int
    concurrent_requests: int
    prompt_lengths: List[int]  # Token counts
    max_output_tokens: int
    output_file: str


@dataclass
class VLLMBenchmarkResults:
    """Results from vLLM benchmark."""
    prompt_length: int
    num_requests: int
    concurrent_requests: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_ttft_ms: float  # Time to first token
    throughput_tokens_per_sec: float
    throughput_requests_per_sec: float


class VLLMBenchmark:
    """
    Benchmark vLLM server performance.

    TODO for students:
    - Add streaming mode benchmarks
    - Measure inter-token latency
    - Test with different temperature/top_p settings
    - Compare greedy vs sampling decoding
    """

    def __init__(self, config: VLLMBenchmarkConfig):
        self.config = config
        self.results: List[VLLMBenchmarkResults] = []

    def generate_prompt(self, token_count: int) -> str:
        """Generate a prompt with approximately the specified token count."""
        # Rough estimate: 4 characters per token
        words_per_token = 0.75
        num_words = int(token_count * words_per_token)

        prompt = "Explain the concept of "
        prompt += " and ".join([f"topic_{i}" for i in range(num_words)])
        prompt += " in detail."

        return prompt

    async def send_request(
        self,
        session: aiohttp.ClientSession,
        prompt: str,
        request_id: int
    ) -> Dict:
        """Send a single inference request to vLLM server."""
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "max_tokens": self.config.max_output_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        start_time = time.perf_counter()

        try:
            async with session.post(
                f"{self.config.server_url}/v1/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                result = await response.json()

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000

                # TODO: Extract TTFT from response headers or streaming
                ttft_ms = latency_ms * 0.1  # Placeholder estimate

                return {
                    "request_id": request_id,
                    "latency_ms": latency_ms,
                    "ttft_ms": ttft_ms,
                    "tokens_generated": result.get("usage", {}).get("completion_tokens", 0),
                    "success": True,
                }
        except Exception as e:
            print(f"Request {request_id} failed: {e}")
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
            }

    async def benchmark_prompt_length(self, prompt_length: int) -> VLLMBenchmarkResults:
        """Benchmark a specific prompt length with concurrent requests."""
        print(f"\nBenchmarking prompt length: {prompt_length} tokens")
        print(f"{'-'*40}")

        prompt = self.generate_prompt(prompt_length)
        results = []

        async with aiohttp.ClientSession() as session:
            # Send requests in batches based on concurrency limit
            for batch_start in range(0, self.config.num_requests, self.config.concurrent_requests):
                batch_end = min(batch_start + self.config.concurrent_requests, self.config.num_requests)
                batch_size = batch_end - batch_start

                print(f"  Sending requests {batch_start+1}-{batch_end}...")

                # Create concurrent requests
                tasks = [
                    self.send_request(session, prompt, i)
                    for i in range(batch_start, batch_end)
                ]

                # Wait for all requests in batch to complete
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)

        # Calculate metrics from successful requests
        successful_results = [r for r in results if r.get("success", False)]

        if not successful_results:
            raise ValueError("All requests failed!")

        latencies = [r["latency_ms"] for r in successful_results]
        ttfts = [r["ttft_ms"] for r in successful_results]
        tokens_generated = [r["tokens_generated"] for r in successful_results]

        latencies_np = np.array(latencies)
        ttfts_np = np.array(ttfts)

        total_tokens = sum(tokens_generated)
        total_time_sec = np.sum(latencies) / 1000

        return VLLMBenchmarkResults(
            prompt_length=prompt_length,
            num_requests=len(successful_results),
            concurrent_requests=self.config.concurrent_requests,
            avg_latency_ms=np.mean(latencies_np),
            p50_latency_ms=np.percentile(latencies_np, 50),
            p95_latency_ms=np.percentile(latencies_np, 95),
            p99_latency_ms=np.percentile(latencies_np, 99),
            avg_ttft_ms=np.mean(ttfts_np),
            throughput_tokens_per_sec=total_tokens / total_time_sec if total_time_sec > 0 else 0,
            throughput_requests_per_sec=len(successful_results) / total_time_sec if total_time_sec > 0 else 0,
        )

    async def run_benchmark(self):
        """Run complete vLLM benchmark across all prompt lengths."""
        print(f"\n{'='*60}")
        print(f"vLLM Benchmark - {self.config.model_name}")
        print(f"{'='*60}\n")

        for prompt_length in self.config.prompt_lengths:
            results = await self.benchmark_prompt_length(prompt_length)
            self.results.append(results)

            # Print results
            print(f"\nResults for {prompt_length}-token prompts:")
            print(f"  Successful requests: {results.num_requests}")
            print(f"  Average latency: {results.avg_latency_ms:.2f} ms")
            print(f"  P95 latency: {results.p95_latency_ms:.2f} ms")
            print(f"  Average TTFT: {results.avg_ttft_ms:.2f} ms")
            print(f"  Throughput: {results.throughput_tokens_per_sec:.2f} tokens/sec")
            print(f"  Request rate: {results.throughput_requests_per_sec:.2f} req/sec")

    def save_results(self):
        """Save benchmark results to JSON file."""
        output = {
            "config": {
                "server_url": self.config.server_url,
                "model_name": self.config.model_name,
                "num_requests": self.config.num_requests,
                "concurrent_requests": self.config.concurrent_requests,
                "max_output_tokens": self.config.max_output_tokens,
            },
            "results": [
                {
                    "prompt_length": r.prompt_length,
                    "num_requests": r.num_requests,
                    "avg_latency_ms": r.avg_latency_ms,
                    "p50_latency_ms": r.p50_latency_ms,
                    "p95_latency_ms": r.p95_latency_ms,
                    "p99_latency_ms": r.p99_latency_ms,
                    "avg_ttft_ms": r.avg_ttft_ms,
                    "throughput_tokens_per_sec": r.throughput_tokens_per_sec,
                    "throughput_requests_per_sec": r.throughput_requests_per_sec,
                }
                for r in self.results
            ]
        }

        output_path = Path(self.config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Results saved to: {output_path}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark vLLM server performance")
    parser.add_argument("--server-url", type=str, default="http://localhost:8000",
                       help="vLLM server URL")
    parser.add_argument("--model", type=str, required=True, help="Model name")
    parser.add_argument("--num-requests", type=int, default=100,
                       help="Total number of requests per prompt length")
    parser.add_argument("--concurrent", type=int, default=10,
                       help="Number of concurrent requests")
    parser.add_argument("--prompt-lengths", type=int, nargs="+", default=[50, 100, 500, 1000],
                       help="Prompt lengths (in tokens) to benchmark")
    parser.add_argument("--max-tokens", type=int, default=128,
                       help="Maximum output tokens per request")
    parser.add_argument("--output", type=str, default="results/vllm_benchmark.json",
                       help="Output file for results")

    args = parser.parse_args()

    config = VLLMBenchmarkConfig(
        server_url=args.server_url,
        model_name=args.model,
        num_requests=args.num_requests,
        concurrent_requests=args.concurrent,
        prompt_lengths=args.prompt_lengths,
        max_output_tokens=args.max_tokens,
        output_file=args.output,
    )

    benchmark = VLLMBenchmark(config)
    asyncio.run(benchmark.run_benchmark())
    benchmark.save_results()


if __name__ == "__main__":
    main()
