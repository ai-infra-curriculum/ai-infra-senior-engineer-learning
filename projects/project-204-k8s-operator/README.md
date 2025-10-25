# Project 204: Kubernetes Operator for ML Training

## Overview

Build a custom Kubernetes operator that manages the lifecycle of ML training jobs. This operator automates job scheduling, resource management, checkpoint recovery, and integrates with existing ML infrastructure.

## Learning Objectives

1. **Operator Pattern**: Understand Kubernetes operator pattern
2. **Custom Resources**: Design and implement CRDs
3. **Reconciliation Loop**: Implement controller reconciliation logic
4. **Job Management**: Automate training job lifecycle
5. **Resource Optimization**: Intelligent scheduling and resource allocation
6. **Observability**: Comprehensive operator monitoring

## Prerequisites

- Completed Projects 201, 202, and 203
- Strong understanding of Kubernetes internals
- Experience with Go or Python
- Knowledge of controller patterns

## Quick Start

```bash
# Build operator
make build

# Deploy CRDs
kubectl apply -f config/crd/

# Deploy operator
kubectl apply -f config/manager/

# Create training job
kubectl apply -f examples/trainingjob-sample.yaml
```

## Architecture

See [architecture.md](architecture.md) for operator design.

## Duration

~65 hours
