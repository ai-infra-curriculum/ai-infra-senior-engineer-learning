"""
Load Testing Script for Model Serving

This script performs comprehensive load testing using Locust to simulate
realistic production traffic patterns and measure system behavior under load.

TODO for students:
- Implement custom load patterns (spike, ramp-up, steady-state)
- Add failure injection testing
- Measure auto-scaling behavior
- Test circuit breaker activation
- Monitor resource saturation points
"""

import argparse
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust import stats as locust_stats
import gevent
import json
import time
from typing import Dict, List
import random


class ModelServingUser(HttpUser):
    """
    Simulated user for model serving load testing.

    TODO for students:
    - Add different request patterns (burst, steady, gradual)
    - Implement user session simulation
    - Add think time between requests
    - Test different model endpoints
    """

    wait_time = between(0.1, 1.0)  # Wait 0.1-1.0 seconds between tasks

    @task(3)
    def predict_image(self):
        """Test image classification endpoint (higher weight)."""
        payload = {
            "model": "resnet50",
            "input": [[random.random() for _ in range(224*224*3)]],
        }
        with self.client.post(
            "/v1/models/resnet50/predict",
            json=payload,
            catch_response=True,
            name="/predict/image"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(2)
    def generate_text(self):
        """Test LLM text generation endpoint."""
        payload = {
            "model": "gpt2",
            "prompt": "Once upon a time",
            "max_tokens": 50,
        }
        with self.client.post(
            "/v1/completions",
            json=payload,
            catch_response=True,
            name="/generate/text"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(1)
    def health_check(self):
        """Test health check endpoint (lower weight)."""
        with self.client.get("/health", name="/health") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed")


def run_load_test(host: str, users: int, spawn_rate: float, duration: int, output_file: str):
    """
    Run load test with specified parameters.

    TODO for students:
    - Add custom load shapes
    - Implement distributed load testing
    - Add real-time metrics visualization
    - Save detailed percentile data
    """
    # Setup Locust environment
    env = Environment(user_classes=[ModelServingUser])

    # Start statistics collection
    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(stats_history, env.runner)

    # Start load test
    env.runner.start(users, spawn_rate=spawn_rate)

    # Run for specified duration
    print(f"\nRunning load test for {duration} seconds...")
    print(f"Target: {users} users, spawn rate: {spawn_rate} users/sec")
    print(f"{'='*60}\n")

    gevent.spawn_later(duration, lambda: env.runner.quit())
    env.runner.greenlet.join()

    # Collect results
    results = {
        "config": {
            "host": host,
            "users": users,
            "spawn_rate": spawn_rate,
            "duration": duration,
        },
        "summary": {
            "total_requests": env.stats.total.num_requests,
            "total_failures": env.stats.total.num_failures,
            "avg_response_time_ms": env.stats.total.avg_response_time,
            "min_response_time_ms": env.stats.total.min_response_time or 0,
            "max_response_time_ms": env.stats.total.max_response_time or 0,
            "requests_per_sec": env.stats.total.total_rps,
            "failure_rate": env.stats.total.fail_ratio,
        },
        "endpoints": {}
    }

    # Collect per-endpoint statistics
    for name, stat in env.stats.entries.items():
        if name != "Aggregated":
            results["endpoints"][name] = {
                "requests": stat.num_requests,
                "failures": stat.num_failures,
                "avg_response_time_ms": stat.avg_response_time,
                "median_response_time_ms": stat.median_response_time,
                "p95_response_time_ms": stat.get_response_time_percentile(0.95),
                "p99_response_time_ms": stat.get_response_time_percentile(0.99),
                "requests_per_sec": stat.total_rps,
            }

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Load test complete!")
    print(f"Total requests: {results['summary']['total_requests']}")
    print(f"Failures: {results['summary']['total_failures']}")
    print(f"Average response time: {results['summary']['avg_response_time_ms']:.2f} ms")
    print(f"Requests/sec: {results['summary']['requests_per_sec']:.2f}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Load test model serving endpoints")
    parser.add_argument("--host", type=str, required=True, help="Host URL to test")
    parser.add_argument("--users", type=int, default=100, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=float, default=10, help="User spawn rate per second")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--output", type=str, default="results/load_test.json",
                       help="Output file for results")

    args = parser.parse_args()

    run_load_test(
        host=args.host,
        users=args.users,
        spawn_rate=args.spawn_rate,
        duration=args.duration,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
