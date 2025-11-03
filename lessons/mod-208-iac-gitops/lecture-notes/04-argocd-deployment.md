# Lecture 4: ArgoCD Deployment

## Learning Objectives

By the end of this lecture, you will be able to:

- Design ArgoCD architectures for GitOps continuous delivery automatically synchronizing Kubernetes application state from Git repositories with live cluster state
- Implement ArgoCD application deployment patterns using Helm charts, Kustomize overlays, and plain manifests with automated sync policies and health checks
- Configure sync strategies including manual sync, automated sync, self-heal (auto-fix drift), and prune (remove orphaned resources) based on application requirements
- Architect multi-cluster management with ArgoCD managing 100+ Kubernetes clusters from centralized control plane with RBAC and namespace isolation
- Design ML model deployment workflows using ArgoCD for canary deployments, blue-green deployments, and progressive delivery of ML models
- Implement ApplicationSets for multi-environment deployments generating applications dynamically from Git directory structure, cluster list, or pull request generators
- Configure ArgoCD notifications with webhooks, Slack, email alerting on sync failures, degraded applications, and deployment events
- Build GitOps workflows with branch-based environments, pull request previews, and automated promotion pipelines for production ML deployments

## Table of Contents
1. [ArgoCD Architecture](#argocd-architecture)
2. [Installation and Setup](#installation-and-setup)
3. [Application Deployment Patterns](#application-deployment-patterns)
4. [Sync Strategies and Policies](#sync-strategies-and-policies)
5. [Multi-Cluster Management](#multi-cluster-management)
6. [ML Model Deployment](#ml-model-deployment)

## ArgoCD Architecture

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It automatically synchronizes the desired application state from Git with the live state in Kubernetes.

### Core Components

```
┌──────────────────────────────────────────────────────────────────┐
│                    ArgoCD Architecture                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────┐         ┌──────────────┐        ┌────────────┐  │
│  │  API Server│◄────────│  Repo Server │───────►│ Git Repo   │  │
│  └─────┬──────┘         └──────────────┘        └────────────┘  │
│        │                                                          │
│        │                                                          │
│        ▼                                                          │
│  ┌────────────┐         ┌──────────────┐                        │
│  │ Controller │────────►│ Application  │                         │
│  │            │         │  Controller  │                         │
│  └────────────┘         └──────┬───────┘                        │
│                                 │                                 │
│                                 ▼                                 │
│                         ┌──────────────┐                         │
│                         │  Kubernetes  │                         │
│                         │   Cluster    │                         │
│                         └──────────────┘                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

Components:
- API Server: gRPC/REST server exposing API
- Repo Server: Maintains local cache of Git repositories
- Application Controller: Monitors applications and compares state
- Redis: Caching and queuing
- Dex (optional): Identity service for SSO
```

### How ArgoCD Works

1. **Monitor**: Continuously watches Git repository for changes
2. **Compare**: Compares desired state (Git) with actual state (Kubernetes)
3. **Sync**: Applies changes to bring actual state to desired state
4. **Health**: Monitors application health status
5. **Prune**: Optionally removes resources not in Git

## Installation and Setup

### Installation Methods

**Method 1: kubectl apply (Quick Start)**
```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access: https://localhost:8080
# Username: admin
# Password: (from above command)
```

**Method 2: Helm Chart**
```bash
# Add ArgoCD Helm repository
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# Create values file
cat <<EOF > argocd-values.yaml
server:
  ingress:
    enabled: true
    hosts:
      - argocd.example.com
    tls:
      - secretName: argocd-tls
        hosts:
          - argocd.example.com

  config:
    repositories: |
      - type: git
        url: https://github.com/company/ml-gitops.git
      - type: helm
        url: https://charts.bitnami.com/bitnami
        name: bitnami

  rbacConfig:
    policy.default: role:readonly
    policy.csv: |
      p, role:ml-team, applications, *, */*, allow
      p, role:ml-team, repositories, *, *, allow
      g, ml-engineers, role:ml-team

repoServer:
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "1"
      memory: "1Gi"

controller:
  resources:
    requests:
      cpu: "1"
      memory: "1Gi"
    limits:
      cpu: "2"
      memory: "2Gi"

redis:
  enabled: true

dex:
  enabled: true
EOF

# Install ArgoCD
helm install argocd argo/argo-cd -n argocd --create-namespace -f argocd-values.yaml
```

**Method 3: ArgoCD Operator**
```yaml
# argocd-operator.yaml
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: argocd
  namespace: argocd
spec:
  server:
    route:
      enabled: true
      tls:
        termination: reencrypt
        insecureEdgeTerminationPolicy: Redirect

  repo:
    resources:
      requests:
        cpu: 500m
        memory: 512Mi

  controller:
    resources:
      requests:
        cpu: 1000m
        memory: 1Gi

  dex:
    openShiftOAuth: true

  rbac:
    defaultPolicy: 'role:readonly'
    policy: |
      g, system:cluster-admins, role:admin
      g, ml-team, role:admin
```

### ArgoCD CLI

```bash
# Install ArgoCD CLI
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# Login
argocd login argocd.example.com --username admin --password <password>

# Or with port-forward
argocd login localhost:8080 --username admin --insecure

# Add Git repository
argocd repo add https://github.com/company/ml-gitops.git \
  --username <username> \
  --password <password>

# Or with SSH
argocd repo add git@github.com:company/ml-gitops.git \
  --ssh-private-key-path ~/.ssh/id_rsa

# List repositories
argocd repo list

# Create application
argocd app create ml-training \
  --repo https://github.com/company/ml-gitops.git \
  --path apps/training \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace ml-training

# Sync application
argocd app sync ml-training

# Get application status
argocd app get ml-training

# List applications
argocd app list

# Delete application
argocd app delete ml-training
```

## Application Deployment Patterns

### Basic Application

```yaml
# argocd-apps/ml-training.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-training
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/company/ml-gitops.git
    targetRevision: main
    path: apps/training

  destination:
    server: https://kubernetes.default.svc
    namespace: ml-training

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Application with Kustomize

```yaml
# argocd-apps/ml-serving-prod.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-serving-prod
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: ml-platform

  source:
    repoURL: https://github.com/company/ml-gitops.git
    targetRevision: main
    path: apps/serving/overlays/prod

  destination:
    server: https://kubernetes.default.svc
    namespace: ml-serving-prod

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true

  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # Ignore HPA changes
```

### Application with Helm

```yaml
# argocd-apps/mlflow.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mlflow
  namespace: argocd
spec:
  project: ml-platform

  source:
    repoURL: https://community-charts.github.io/helm-charts
    chart: mlflow
    targetRevision: 0.7.19

    helm:
      values: |
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

        backendStore:
          postgres:
            enabled: true
            host: postgres.database.svc.cluster.local
            port: 5432
            database: mlflow
            username: mlflow
            password: changeme

        artifactRoot:
          s3:
            enabled: true
            bucket: ml-artifacts
            region: us-west-2

  destination:
    server: https://kubernetes.default.svc
    namespace: mlflow

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### App of Apps Pattern

```yaml
# argocd-apps/ml-platform.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-platform
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/company/ml-gitops.git
    targetRevision: main
    path: platform

  destination:
    server: https://kubernetes.default.svc
    namespace: argocd

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```yaml
# platform/training.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-training
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/company/ml-gitops.git
    targetRevision: main
    path: apps/training
  destination:
    server: https://kubernetes.default.svc
    namespace: ml-training
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-serving
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/company/ml-gitops.git
    targetRevision: main
    path: apps/serving
  destination:
    server: https://kubernetes.default.svc
    namespace: ml-serving
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mlflow
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://community-charts.github.io/helm-charts
    chart: mlflow
    targetRevision: 0.7.19
  destination:
    server: https://kubernetes.default.svc
    namespace: mlflow
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Sync Strategies and Policies

### Manual vs Automated Sync

**Manual Sync:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-training-manual
spec:
  # ... source and destination ...

  syncPolicy: {}  # No automated sync
```

```bash
# Manual sync via CLI
argocd app sync ml-training-manual

# Sync with specific resources
argocd app sync ml-training-manual --resource apps:Deployment:ml-trainer
```

**Automated Sync:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ml-training-auto
spec:
  syncPolicy:
    automated:
      prune: true        # Delete resources not in Git
      selfHeal: true     # Override manual changes
      allowEmpty: false  # Don't sync if manifests are empty

    syncOptions:
      - Validate=true              # Validate resources before apply
      - CreateNamespace=true       # Create namespace if doesn't exist
      - PrunePropagationPolicy=foreground  # Wait for dependents before pruning
      - PruneLast=true            # Prune after other resources sync

    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Sync Waves

Control order of resource creation:

```yaml
# 01-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training
  annotations:
    argocd.argoproj.io/sync-wave: "0"  # Create first
```

```yaml
# 02-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-config
  namespace: ml-training
  annotations:
    argocd.argoproj.io/sync-wave: "1"  # Create second
data:
  config.yaml: |
    model_path: /models
```

```yaml
# 03-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-trainer
  namespace: ml-training
  annotations:
    argocd.argoproj.io/sync-wave: "2"  # Create third
spec:
  # ... deployment spec ...
```

### Sync Hooks

Run tasks before/after sync:

```yaml
# pre-sync-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: ml-training
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: ml-platform/db-migrate:latest
        command: ["python", "migrate.py"]
        env:
        - name: DB_HOST
          value: postgres.database.svc.cluster.local
```

```yaml
# post-sync-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  namespace: ml-training
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: test
        image: ml-platform/smoke-test:latest
        command: ["./run-smoke-tests.sh"]
```

### Health Assessment

```yaml
# Custom health check
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations: |
    argoproj.io/Rollout:
      health.lua: |
        hs = {}
        if obj.status ~= nil then
          if obj.status.phase == "Healthy" then
            hs.status = "Healthy"
            hs.message = "Rollout is healthy"
            return hs
          end
        end
        hs.status = "Progressing"
        hs.message = "Rollout is progressing"
        return hs
```

## Multi-Cluster Management

### Add Cluster

```bash
# List contexts
kubectl config get-contexts

# Add cluster to ArgoCD
argocd cluster add prod-cluster-context --name prod-cluster

# List clusters
argocd cluster list

# Example output:
# SERVER                          NAME            VERSION  STATUS      MESSAGE
# https://kubernetes.default.svc  in-cluster              Successful
# https://prod-cluster.example    prod-cluster    1.28     Successful
```

### Deploy to Multiple Clusters

```yaml
# argocd-apps/ml-serving-multi-cluster.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: ml-serving
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - cluster: in-cluster
            url: https://kubernetes.default.svc
            environment: dev

          - cluster: staging-cluster
            url: https://staging.k8s.example.com
            environment: staging

          - cluster: prod-cluster
            url: https://prod.k8s.example.com
            environment: prod

  template:
    metadata:
      name: 'ml-serving-{{environment}}'
    spec:
      project: ml-platform

      source:
        repoURL: https://github.com/company/ml-gitops.git
        targetRevision: main
        path: 'apps/serving/overlays/{{environment}}'

      destination:
        server: '{{url}}'
        namespace: 'ml-serving-{{environment}}'

      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

### Cluster-Specific Configuration

```yaml
# ApplicationSet with cluster generator
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: monitoring-stack
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            monitoring: enabled

  template:
    metadata:
      name: 'monitoring-{{name}}'
    spec:
      project: platform

      source:
        repoURL: https://github.com/company/monitoring.git
        targetRevision: main
        path: manifests

      destination:
        server: '{{server}}'
        namespace: monitoring

      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## ML Model Deployment

### Training Job Deployment

```yaml
# apps/training/kubeflow-job.yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: resnet-training
  namespace: ml-training
  annotations:
    argocd.argoproj.io/sync-wave: "2"
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            argocd.argoproj.io/sync-options: Replace=true
        spec:
          containers:
          - name: pytorch
            image: ml-training/resnet:v1.0.0
            command:
              - python
              - train.py
            args:
              - --backend=nccl
              - --epochs=100
              - --batch-size=256
            resources:
              limits:
                nvidia.com/gpu: 1

    Worker:
      replicas: 3
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: ml-training/resnet:v1.0.0
            command:
              - python
              - train.py
            args:
              - --backend=nccl
            resources:
              limits:
                nvidia.com/gpu: 1
```

### Model Serving with Progressive Delivery

```yaml
# apps/serving/seldon-deployment.yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: sentiment-model
  namespace: ml-serving
  annotations:
    argocd.argoproj.io/sync-wave: "3"
spec:
  name: sentiment
  predictors:
  - name: main
    replicas: 3
    componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: ml-models/sentiment:v1.2.0
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"

    graph:
      name: classifier
      type: MODEL
      parameters:
      - name: model_uri
        value: "s3://models/sentiment/v1.2.0"

    traffic: 90

  # Canary deployment
  - name: canary
    replicas: 1
    componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: ml-models/sentiment:v1.3.0
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"

    graph:
      name: classifier
      type: MODEL
      parameters:
      - name: model_uri
        value: "s3://models/sentiment/v1.3.0"

    traffic: 10
```

### ML Pipeline Deployment

```yaml
# apps/pipelines/kubeflow-pipeline.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: ml-pipeline
  namespace: ml-pipelines
  annotations:
    argocd.argoproj.io/hook: PostSync
spec:
  entrypoint: ml-pipeline
  arguments:
    parameters:
    - name: data-path
      value: "s3://ml-data/training-data"
    - name: model-output
      value: "s3://ml-models/output"

  templates:
  - name: ml-pipeline
    steps:
    - - name: data-preprocessing
        template: preprocess
    - - name: model-training
        template: train
    - - name: model-evaluation
        template: evaluate
    - - name: model-registration
        template: register

  - name: preprocess
    container:
      image: ml-pipeline/preprocess:latest
      command: ["python", "preprocess.py"]
      args: ["--input={{workflow.parameters.data-path}}"]

  - name: train
    container:
      image: ml-pipeline/train:latest
      command: ["python", "train.py"]
      resources:
        limits:
          nvidia.com/gpu: 4

  - name: evaluate
    container:
      image: ml-pipeline/evaluate:latest
      command: ["python", "evaluate.py"]

  - name: register
    container:
      image: ml-pipeline/register:latest
      command: ["python", "register.py"]
      args: ["--output={{workflow.parameters.model-output}}"]
```

## Summary

ArgoCD provides:
- **Declarative GitOps**: Manage deployments via Git
- **Automated Sync**: Continuous reconciliation
- **Multi-Cluster**: Manage multiple Kubernetes clusters
- **Progressive Delivery**: Canary and blue-green deployments
- **Extensibility**: Hooks, sync waves, custom health checks

**Key Concepts:**
1. Applications represent deployments
2. Projects provide logical grouping
3. Sync policies control automation
4. ApplicationSets enable multi-cluster
5. Hooks enable pre/post-sync actions

## Next Steps

- Continue to [Lecture 5: FluxCD Automation](05-fluxcd-automation.md)
- Install ArgoCD in your cluster
- Create sample applications
- Practice with sync strategies

## Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [ApplicationSet Documentation](https://argocd-applicationset.readthedocs.io/)
- [ArgoCD Patterns](https://github.com/argoproj/argocd-example-apps)
