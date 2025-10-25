# Project 202: Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer / Ingress                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Intelligent Router                      │
│              (A/B Testing, Canary, Load Balancing)          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐     ┌───────────────┐    ┌───────────────┐
│ TensorRT      │     │  vLLM         │    │  Model        │
│ CNN Serving   │     │  LLM Serving  │    │  Router       │
│ Pods (HPA)    │     │  Pods (HPA)   │    │  Pods         │
└───────────────┘     └───────────────┘    └───────────────┘
        │                     │                     │
┌─────────────────────────────────────────────────────────────┐
│                      Jaeger Tracing                          │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. FastAPI Serving Layer
- Async request handling
- Pydantic models for validation
- Middleware for tracing and metrics

### 2. TensorRT Serving
- Optimized CNN inference
- Multiple precision support
- Batch inference

### 3. vLLM Serving
- LLM inference with PagedAttention
- Streaming responses
- Continuous batching

### 4. Intelligent Router
- Request routing logic
- A/B test configuration
- Traffic splitting

### 5. Distributed Tracing
- Jaeger integration
- Span decorators
- Performance analysis

## Data Flow

1. Request arrives at ingress
2. Router selects backend based on routing rules
3. Request traced through Jaeger
4. Model inference executed
5. Response returned to client
6. Metrics reported to Prometheus

## Monitoring

- Prometheus metrics (latency, throughput, errors)
- Jaeger traces (request flow, bottlenecks)
- Grafana dashboards (real-time monitoring)
