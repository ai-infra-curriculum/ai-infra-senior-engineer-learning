# Project 202: High-Performance Model Serving

## Overview

Build a high-performance model serving platform that leverages TensorRT optimization and vLLM for efficient LLM serving. This project implements intelligent routing, auto-scaling, and comprehensive observability with distributed tracing.

## Learning Objectives

1. **TensorRT Optimization**: Convert and optimize models with TensorRT
2. **LLM Serving**: Deploy large language models with vLLM
3. **Intelligent Routing**: Implement A/B testing and canary deployments
4. **Auto-scaling**: Configure Kubernetes HPA for dynamic scaling
5. **Distributed Tracing**: Implement request tracing with Jaeger
6. **Performance Benchmarking**: Measure and optimize serving latency/throughput

## Prerequisites

- Completed Project 201 (Distributed Training)
- Experience with FastAPI and async Python
- Understanding of model optimization techniques
- Kubernetes and containerization knowledge

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Convert model to TensorRT
python src/tensorrt/convert_to_tensorrt.py --model resnet50

# Run serving locally
python src/serving/main.py

# Deploy to Kubernetes
kubectl apply -f kubernetes/
```

## Architecture

See [architecture.md](architecture.md) for detailed system design.

## Duration

~70 hours
