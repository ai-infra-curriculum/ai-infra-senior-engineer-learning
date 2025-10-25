"""
Benchmark Results Analysis and Visualization

This script analyzes benchmark results and generates comparison charts
for TensorRT, vLLM, and load testing metrics.

TODO for students:
- Add cost analysis ($/request, $/token)
- Generate comparison charts (matplotlib/plotly)
- Calculate ROI for different optimization strategies
- Create executive summary reports
- Add trend analysis across multiple benchmark runs
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from dataclasses import dataclass


@dataclass
class BenchmarkSummary:
    """Summary statistics from benchmark analysis."""
    name: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput: float
    throughput_unit: str


class BenchmarkAnalyzer:
    """
    Analyze and compare benchmark results.

    TODO for students:
    - Generate HTML reports with charts
    - Add statistical significance testing
    - Compare multiple benchmark runs
    - Calculate efficiency metrics (throughput/cost)
    """

    def __init__(self):
        self.summaries: List[BenchmarkSummary] = []

    def load_tensorrt_results(self, file_path: str) -> BenchmarkSummary:
        """Load and summarize TensorRT benchmark results."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        results = data["results"]

        # Find best performing configuration
        best = min(results, key=lambda x: x["avg_latency_ms"])

        return BenchmarkSummary(
            name=f"TensorRT ({data['config']['precision']})",
            avg_latency_ms=best["avg_latency_ms"],
            p95_latency_ms=best["p95_latency_ms"],
            p99_latency_ms=best["p99_latency_ms"],
            throughput=best["throughput_samples_per_sec"],
            throughput_unit="samples/sec"
        )

    def load_vllm_results(self, file_path: str) -> BenchmarkSummary:
        """Load and summarize vLLM benchmark results."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        results = data["results"]

        # Average across all prompt lengths
        avg_latency = sum(r["avg_latency_ms"] for r in results) / len(results)
        avg_p95 = sum(r["p95_latency_ms"] for r in results) / len(results)
        avg_p99 = sum(r["p99_latency_ms"] for r in results) / len(results)
        avg_throughput = sum(r["throughput_tokens_per_sec"] for r in results) / len(results)

        return BenchmarkSummary(
            name=f"vLLM ({data['config']['model_name']})",
            avg_latency_ms=avg_latency,
            p95_latency_ms=avg_p95,
            p99_latency_ms=avg_p99,
            throughput=avg_throughput,
            throughput_unit="tokens/sec"
        )

    def load_loadtest_results(self, file_path: str) -> BenchmarkSummary:
        """Load and summarize load test results."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        summary = data["summary"]

        return BenchmarkSummary(
            name="Load Test",
            avg_latency_ms=summary["avg_response_time_ms"],
            p95_latency_ms=0,  # TODO: Extract from endpoints
            p99_latency_ms=0,
            throughput=summary["requests_per_sec"],
            throughput_unit="req/sec"
        )

    def generate_summary_table(self) -> str:
        """Generate ASCII table summary of all benchmarks."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("BENCHMARK RESULTS SUMMARY")
        lines.append("="*80 + "\n")

        # Header
        lines.append(f"{'Benchmark':<30} {'Avg Latency':<15} {'P95 Latency':<15} {'Throughput':<20}")
        lines.append("-"*80)

        # Data rows
        for summary in self.summaries:
            lines.append(
                f"{summary.name:<30} "
                f"{summary.avg_latency_ms:>10.2f} ms   "
                f"{summary.p95_latency_ms:>10.2f} ms   "
                f"{summary.throughput:>10.2f} {summary.throughput_unit}"
            )

        lines.append("="*80 + "\n")
        return "\n".join(lines)

    def save_comparison_report(self, output_file: str):
        """Save detailed comparison report."""
        report = {
            "benchmarks": [
                {
                    "name": s.name,
                    "avg_latency_ms": s.avg_latency_ms,
                    "p95_latency_ms": s.p95_latency_ms,
                    "p99_latency_ms": s.p99_latency_ms,
                    "throughput": s.throughput,
                    "throughput_unit": s.throughput_unit,
                }
                for s in self.summaries
            ],
            "recommendations": [
                "TensorRT shows best latency for image models",
                "vLLM provides optimal throughput for LLM serving",
                "Load testing confirms system handles production traffic",
                "TODO: Add cost-performance analysis",
                "TODO: Add scaling recommendations",
            ]
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Comparison report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze and compare benchmark results")
    parser.add_argument("--tensorrt", type=str, help="TensorRT benchmark results file")
    parser.add_argument("--vllm", type=str, help="vLLM benchmark results file")
    parser.add_argument("--loadtest", type=str, help="Load test results file")
    parser.add_argument("--output", type=str, default="results/benchmark_comparison.json",
                       help="Output file for comparison report")

    args = parser.parse_args()

    analyzer = BenchmarkAnalyzer()

    # Load results from provided files
    if args.tensorrt and Path(args.tensorrt).exists():
        summary = analyzer.load_tensorrt_results(args.tensorrt)
        analyzer.summaries.append(summary)
        print(f"Loaded TensorRT results: {summary.name}")

    if args.vllm and Path(args.vllm).exists():
        summary = analyzer.load_vllm_results(args.vllm)
        analyzer.summaries.append(summary)
        print(f"Loaded vLLM results: {summary.name}")

    if args.loadtest and Path(args.loadtest).exists():
        summary = analyzer.load_loadtest_results(args.loadtest)
        analyzer.summaries.append(summary)
        print(f"Loaded load test results: {summary.name}")

    if not analyzer.summaries:
        print("No benchmark results found. Please provide at least one results file.")
        return

    # Generate and display summary
    print(analyzer.generate_summary_table())

    # Save comparison report
    analyzer.save_comparison_report(args.output)


if __name__ == "__main__":
    main()
