# Lecture 5: FluxCD Automation

## Learning Objectives

By the end of this lecture, you will be able to:

- Design FluxCD architectures using GitOps Toolkit components (Source Controller, Kustomize Controller, Helm Controller, Notification Controller) for composable CD workflows
- Implement Flux bootstrap process installing Flux into cluster via Git repository enabling self-managed GitOps infrastructure with automatic upgrades
- Configure Flux Kustomizations for multi-environment deployments using overlays, patches, and variable substitution managing configuration across dev/staging/prod
- Architect image automation with Flux Image Reflector and Image Automation Controllers automatically updating manifests when new container images are pushed
- Design ML pipeline automation using Flux managing Kubeflow Pipelines, Argo Workflows, or custom training jobs with GitOps-driven deployment
- Implement Flux multi-tenancy using Git repository per team, namespace isolation, and RBAC controls enabling safe self-service deployments
- Configure Flux notifications with Slack, Teams, or webhooks alerting on sync failures, reconciliation errors, and successful deployments
- Build advanced Flux workflows with dependencies, health checks, automated rollbacks, and progressive delivery integrating with Flagger for canary deployments

## Table of Contents
1. [FluxCD Architecture](#fluxcd-architecture)
2. [GitOps Toolkit Components](#gitops-toolkit-components)
3. [Installation and Bootstrap](#installation-and-bootstrap)
4. [Kustomize Integration](#kustomize-integration)
5. [Image Automation](#image-automation)
6. [ML Pipeline Automation](#ml-pipeline-automation)

## FluxCD Architecture

FluxCD is a set of continuous and progressive delivery solutions for Kubernetes that are open and extensible. Flux v2 (current version) is built on the GitOps Toolkit, a composable API and specialized tools.

### Core Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    FluxCD Architecture                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Source Controller (watches Git, Helm, Buckets)            │  │
│  └───────────────────┬────────────────────────────────────────┘  │
│                      │                                            │
│                      ▼                                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Kustomize Controller (applies Kustomize manifests)       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                      │                                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Helm Controller (manages Helm releases)                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                      │                                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Notification Controller (events and webhooks)             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                      │                                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Image Automation Controllers (image updates)              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                      │                                            │
│                      ▼                                            │
│                  Kubernetes                                       │
│                   Cluster                                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Components Overview

**Source Controller**:
- Watches Git repositories, Helm repositories, S3 buckets
- Fetches artifacts and makes them available to other controllers
- Provides API for artifact sources

**Kustomize Controller**:
- Applies Kustomize overlays
- Reconciles Kustomization resources
- Manages dependency ordering

**Helm Controller**:
- Manages Helm releases
- Supports Helm charts from various sources
- Handles rollbacks and testing

**Notification Controller**:
- Sends events to external systems (Slack, Teams, etc.)
- Receives webhooks from Git providers
- Enables event-driven workflows

**Image Automation**:
- Scans container registries
- Updates manifests with new image tags
- Commits changes back to Git

## GitOps Toolkit Components

### Source Resources

**GitRepository:**
```yaml
# flux-sources/ml-gitops-repo.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: ml-gitops
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/company/ml-gitops
  ref:
    branch: main

  secretRef:
    name: git-credentials

  ignore: |
    # Exclude files
    /**/README.md
    /**/.gitignore
```

**HelmRepository:**
```yaml
# flux-sources/bitnami-charts.yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 10m
  url: https://charts.bitnami.com/bitnami
```

**Bucket (S3/GCS):**
```yaml
# flux-sources/ml-models-bucket.yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: Bucket
metadata:
  name: ml-models
  namespace: flux-system
spec:
  interval: 5m
  provider: aws
  bucketName: ml-models-artifacts
  endpoint: s3.amazonaws.com
  region: us-west-2

  secretRef:
    name: aws-credentials
```

### Kustomization Resources

```yaml
# flux-kustomizations/ml-infrastructure.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ml-infrastructure
  namespace: flux-system
spec:
  interval: 10m
  retryInterval: 1m
  timeout: 5m

  sourceRef:
    kind: GitRepository
    name: ml-gitops

  path: ./infrastructure
  prune: true
  wait: true

  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: ml-controller
      namespace: ml-system

  postBuild:
    substitute:
      CLUSTER_NAME: "production"
      REGION: "us-west-2"
```

### HelmRelease Resources

```yaml
# flux-helm/mlflow.yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: mlflow
  namespace: mlflow
spec:
  interval: 10m
  timeout: 5m

  chart:
    spec:
      chart: mlflow
      version: '0.7.19'
      sourceRef:
        kind: HelmRepository
        name: community-charts
        namespace: flux-system

  values:
    image:
      repository: ghcr.io/mlflow/mlflow
      tag: v2.8.1

    service:
      type: LoadBalancer
      port: 80

    resources:
      requests:
        cpu: 500m
        memory: 512Mi
      limits:
        cpu: 1000m
        memory: 1Gi

    postgresql:
      enabled: true
      auth:
        username: mlflow
        password: changeme
        database: mlflow

    s3:
      enabled: true
      bucket: ml-artifacts
      region: us-west-2

  # Rollback on failure
  install:
    remediation:
      retries: 3

  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true

  # Run tests after install/upgrade
  test:
    enable: true

  # Notifications
  postRenderers:
    - kustomize:
        patches:
          - target:
              kind: Deployment
            patch: |
              - op: add
                path: /spec/template/metadata/annotations
                value:
                  fluxcd.io/automated: "true"
```

## Installation and Bootstrap

### Install Flux CLI

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Or with Homebrew
brew install fluxcd/tap/flux

# Verify installation
flux --version

# Check prerequisites
flux check --pre
```

### Bootstrap Flux

**Bootstrap with GitHub:**
```bash
# Export GitHub token
export GITHUB_TOKEN=<your-token>

# Bootstrap Flux
flux bootstrap github \
  --owner=company \
  --repository=ml-gitops \
  --branch=main \
  --path=clusters/production \
  --personal=false \
  --components-extra=image-reflector-controller,image-automation-controller

# This will:
# 1. Create flux-system namespace
# 2. Install Flux components
# 3. Create Git repository if it doesn't exist
# 4. Commit Flux manifests to repo
# 5. Configure Flux to watch the repo
```

**Bootstrap with GitLab:**
```bash
export GITLAB_TOKEN=<your-token>

flux bootstrap gitlab \
  --owner=company \
  --repository=ml-gitops \
  --branch=main \
  --path=clusters/production \
  --token-auth
```

**Manual Bootstrap:**
```bash
# Install Flux components
flux install \
  --components-extra=image-reflector-controller,image-automation-controller \
  --export > flux-system.yaml

kubectl apply -f flux-system.yaml

# Create Git source
flux create source git ml-gitops \
  --url=https://github.com/company/ml-gitops \
  --branch=main \
  --interval=1m \
  --export > ml-gitops-source.yaml

kubectl apply -f ml-gitops-source.yaml

# Create Kustomization
flux create kustomization ml-infrastructure \
  --source=ml-gitops \
  --path="./infrastructure" \
  --prune=true \
  --interval=10m \
  --export > ml-infrastructure-kustomization.yaml

kubectl apply -f ml-infrastructure-kustomization.yaml
```

### Verify Installation

```bash
# Check Flux components
flux check

# Get sources
flux get sources all

# Get kustomizations
flux get kustomizations

# Get helm releases
flux get helmreleases --all-namespaces

# Watch reconciliation
flux logs --follow --all-namespaces
```

## Kustomize Integration

### Directory Structure

```
ml-gitops/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   ├── infrastructure.yaml
│   │   └── apps.yaml
│   └── staging/
│       ├── flux-system/
│       ├── infrastructure.yaml
│       └── apps.yaml
├── infrastructure/
│   ├── base/
│   │   ├── namespaces/
│   │   ├── rbac/
│   │   └── network-policies/
│   └── overlays/
│       ├── production/
│       └── staging/
└── apps/
    ├── ml-training/
    │   ├── base/
    │   └── overlays/
    └── ml-serving/
        ├── base/
        └── overlays/
```

### Base Kustomization

```yaml
# apps/ml-training/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: ml-training

resources:
  - namespace.yaml
  - serviceaccount.yaml
  - deployment.yaml
  - service.yaml
  - hpa.yaml

configMapGenerator:
  - name: ml-config
    files:
      - config.yaml

secretGenerator:
  - name: ml-secrets
    envs:
      - secrets.env

commonLabels:
  app: ml-training
  managed-by: flux
```

### Environment Overlays

```yaml
# apps/ml-training/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: ml-training-prod

replicas:
  - name: ml-trainer
    count: 5

images:
  - name: ml-trainer
    newTag: v1.2.3

patchesStrategicMerge:
  - deployment-patch.yaml

resources:
  - pdb.yaml
  - monitoring.yaml
```

```yaml
# apps/ml-training/overlays/production/deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-trainer
spec:
  template:
    spec:
      nodeSelector:
        node-type: gpu
      containers:
        - name: trainer
          resources:
            requests:
              nvidia.com/gpu: 2
              cpu: "8"
              memory: "32Gi"
            limits:
              nvidia.com/gpu: 2
              cpu: "16"
              memory: "64Gi"
```

### Flux Kustomization

```yaml
# clusters/production/apps.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ml-training
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: ml-gitops
  path: ./apps/ml-training/overlays/production
  prune: true
  wait: true
  timeout: 5m

  # Substitute variables
  postBuild:
    substitute:
      CLUSTER_NAME: "production"
      AWS_REGION: "us-west-2"

  # Health checks
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: ml-trainer
      namespace: ml-training-prod

  # Dependency ordering
  dependsOn:
    - name: ml-infrastructure
```

## Image Automation

### Image Repository

```yaml
# flux-image/ml-training-registry.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: ml-training
  namespace: flux-system
spec:
  image: ghcr.io/company/ml-training
  interval: 1m

  secretRef:
    name: ghcr-credentials
```

### Image Policy

```yaml
# flux-image/ml-training-policy.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: ml-training
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: ml-training

  policy:
    semver:
      range: 1.x.x

  # Or use regex pattern
  # policy:
  #   alphabetical:
  #     order: asc
  #   filterTags:
  #     pattern: '^prod-[a-f0-9]+-(?P<ts>[0-9]+)'
  #     extract: '$ts'
```

### Image Update Automation

```yaml
# flux-image/image-update-automation.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: ml-training
  namespace: flux-system
spec:
  interval: 1m

  sourceRef:
    kind: GitRepository
    name: ml-gitops

  git:
    checkout:
      ref:
        branch: main

    commit:
      author:
        email: fluxcdbot@company.com
        name: Flux CD Bot
      messageTemplate: |
        Update ML training image

        Automation name: {{ .AutomationObject }}

        Files:
        {{ range $filename, $_ := .Updated.Files -}}
        - {{ $filename }}
        {{ end -}}

        Images:
        {{ range .Updated.Images -}}
        - {{.}}
        {{ end -}}

    push:
      branch: main

  update:
    path: ./apps/ml-training/overlays/production
    strategy: Setters
```

### Deployment with Image Markers

```yaml
# apps/ml-training/overlays/production/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-trainer
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: ghcr.io/company/ml-training:v1.0.0  # {"$imagepolicy": "flux-system:ml-training"}
        # Flux will automatically update the tag based on policy
```

## ML Pipeline Automation

### Training Pipeline Automation

```yaml
# ml-pipelines/training-automation.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ml-training-pipeline
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: ml-gitops
  path: ./pipelines/training

  prune: true
  wait: false  # Don't wait for Jobs to complete

  # Substitute experiment parameters
  postBuild:
    substitute:
      EXPERIMENT_ID: "${EXPERIMENT_ID:-default}"
      LEARNING_RATE: "${LEARNING_RATE:-0.001}"
      BATCH_SIZE: "${BATCH_SIZE:-32}"
      EPOCHS: "${EPOCHS:-100}"

  # Run on push to specific paths
  patches:
    - patch: |
        - op: add
          path: /spec/path
          value: ./pipelines/training/experiments/${EXPERIMENT_ID}
      target:
        kind: Kustomization
```

### Model Deployment Automation

```yaml
# ml-pipelines/model-deployment.yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: model-deployment
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
    - kind: Kustomization
      name: ml-serving
  summary: "Model deployment status"

---
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: ml-deployments
  secretRef:
    name: slack-webhook
```

### Automated Canary Deployment

```yaml
# ml-serving/canary-automation.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ml-serving
  namespace: ml-serving
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-serving

  progressDeadlineSeconds: 300

  service:
    port: 8080

  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 5

    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m

    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m

    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://ml-serving-canary:8080/predict"

    - name: notify-slack
      url: https://hooks.slack.com/services/YOUR/WEBHOOK
      type: post-rollout
```

### Experiment Tracking Integration

```python
# automation/experiment_tracker.py
"""
Integrate Flux with MLflow for experiment tracking
"""
import os
import yaml
from mlflow import log_param, log_metric, start_run

class FluxMLflowIntegration:
    """Track Flux deployments in MLflow"""

    def __init__(self, mlflow_uri: str):
        self.mlflow_uri = mlflow_uri
        os.environ['MLFLOW_TRACKING_URI'] = mlflow_uri

    def track_deployment(self, kustomization_path: str):
        """Track deployment as MLflow experiment"""

        # Parse Kustomization
        with open(kustomization_path) as f:
            kustomization = yaml.safe_load(f)

        # Extract parameters
        params = kustomization.get('spec', {}).get('postBuild', {}).get('substitute', {})

        # Start MLflow run
        with start_run(run_name=f"deployment-{kustomization['metadata']['name']}"):
            # Log deployment parameters
            for key, value in params.items():
                log_param(key, value)

            # Log deployment metadata
            log_param('cluster', os.getenv('CLUSTER_NAME'))
            log_param('namespace', kustomization['spec']['path'])
            log_param('git_commit', os.getenv('FLUX_GIT_COMMIT'))

            # Simulate metrics (would be real in production)
            log_metric('deployment_duration_seconds', 45)
            log_metric('pods_ready', 5)

# Usage
tracker = FluxMLflowIntegration('http://mlflow:5000')
tracker.track_deployment('./apps/ml-training/overlays/production/kustomization.yaml')
```

### Event-Driven Workflows

```yaml
# flux-events/webhook-receiver.yaml
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Receiver
metadata:
  name: model-update-webhook
  namespace: flux-system
spec:
  type: generic
  events:
    - "ping"
    - "push"

  secretRef:
    name: webhook-token

  resources:
    - apiVersion: source.toolkit.fluxcd.io/v1
      kind: GitRepository
      name: ml-gitops

---
apiVersion: v1
kind: Secret
metadata:
  name: webhook-token
  namespace: flux-system
type: Opaque
data:
  token: <base64-encoded-token>
```

```bash
# Trigger reconciliation via webhook
curl -X POST \
  https://flux-webhook.example.com/hook/model-update-webhook \
  -H "X-Signature: sha256=<signature>" \
  -d '{"event": "model-updated", "model": "sentiment-classifier", "version": "v1.3.0"}'
```

## Best Practices

### 1. Repository Structure

- Use monorepo or multi-repo based on team size
- Separate infrastructure from applications
- Use overlays for environment-specific config
- Keep secrets out of Git (use Sealed Secrets or SOPS)

### 2. Reconciliation Intervals

```yaml
# Adjust intervals based on requirements
spec:
  interval: 1m   # Frequent for development
  interval: 10m  # Normal for production
  interval: 1h   # Infrequent for stable infrastructure
```

### 3. Health Checks

```yaml
spec:
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: ml-training
      namespace: ml-training
    - apiVersion: batch/v1
      kind: Job
      name: data-preprocessing
      namespace: ml-pipelines
```

### 4. Notifications

```yaml
# Alert on failures
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: critical-alerts
  namespace: flux-system
spec:
  providerRef:
    name: pagerduty
  eventSeverity: error
  eventSources:
    - kind: Kustomization
      name: '*'
      namespace: flux-system
```

## Summary

FluxCD provides:
- **GitOps Automation**: Continuous reconciliation from Git
- **Composable API**: Flexible GitOps Toolkit
- **Image Automation**: Automatic image updates
- **Multi-Tenancy**: Namespace-based isolation
- **Progressive Delivery**: Canary and blue-green deployments

**Key Components:**
1. Source Controller: Watches Git/Helm/Buckets
2. Kustomize Controller: Applies Kustomizations
3. Helm Controller: Manages Helm releases
4. Image Automation: Updates container images
5. Notification Controller: Events and alerts

## Next Steps

- Continue to [Lecture 6: Infrastructure Testing](06-infrastructure-testing.md)
- Bootstrap Flux in your cluster
- Create Kustomizations for ML workloads
- Set up image automation

## Additional Resources

- [FluxCD Documentation](https://fluxcd.io/docs/)
- [GitOps Toolkit](https://toolkit.fluxcd.io/)
- [Flux Examples](https://github.com/fluxcd/flux2-kustomize-helm-example)
- [Image Automation Guide](https://fluxcd.io/docs/guides/image-update/)
