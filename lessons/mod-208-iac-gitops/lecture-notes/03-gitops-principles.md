# Lecture 3: GitOps Principles

## Table of Contents
1. [What is GitOps?](#what-is-gitops)
2. [Core Principles](#core-principles)
3. [Declarative Infrastructure](#declarative-infrastructure)
4. [Git as Single Source of Truth](#git-as-single-source-of-truth)
5. [Automated Deployment](#automated-deployment)
6. [ML Infrastructure GitOps](#ml-infrastructure-gitops)

## What is GitOps?

GitOps is an operational framework that applies DevOps best practices (version control, collaboration, CI/CD) to infrastructure automation and application deployment. The key idea: the desired state of the system is stored in Git, and automated processes ensure the actual state matches the desired state.

### Traditional vs GitOps Workflow

**Traditional Deployment:**
```
Developer → Manual kubectl apply → Cluster
         → Manual terraform apply → Cloud
         → SSH to servers → Configuration
```

**GitOps Deployment:**
```
Developer → Git commit → Automated sync → Cluster
         → Pull request → Review & merge → Automated deployment
         → Git as truth → Continuous reconciliation
```

### Key Benefits

**For ML Infrastructure:**
- **Reproducibility**: Every deployment is reproducible from Git
- **Auditability**: Complete history of changes
- **Disaster Recovery**: Git contains full system state
- **Collaboration**: Use Git workflows for infrastructure changes
- **Security**: No direct cluster access needed
- **Consistency**: Same deployment process across environments

### GitOps Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                      GitOps Workflow                            │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Developer makes changes                                     │
│     └─> Edit YAML manifests locally                            │
│     └─> Test locally (optional)                                │
│     └─> Git commit & push                                      │
│                                                                 │
│  2. Review process                                              │
│     └─> Create pull request                                    │
│     └─> CI runs validation                                     │
│     └─> Team reviews changes                                   │
│     └─> Merge to main branch                                   │
│                                                                 │
│  3. Automated deployment                                        │
│     └─> GitOps operator detects changes                        │
│     └─> Operator pulls latest manifests                        │
│     └─> Operator applies to cluster                            │
│     └─> Continuous reconciliation                              │
│                                                                 │
│  4. Monitoring & alerting                                       │
│     └─> Monitor application health                             │
│     └─> Alert on sync failures                                 │
│     └─> Audit all changes from Git                             │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. Declarative Description

The entire system is described declaratively (desired state, not imperative commands).

**Imperative (Traditional):**
```bash
# Manual steps to deploy
kubectl create namespace ml-training
kubectl create configmap ml-config --from-file=config.yaml
kubectl apply -f deployment.yaml
kubectl scale deployment ml-training --replicas=5
kubectl set image deployment/ml-training container=image:v2
```

**Declarative (GitOps):**
```yaml
# manifests/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training

---
# manifests/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-config
  namespace: ml-training
data:
  config.yaml: |
    model_path: /models
    batch_size: 32

---
# manifests/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training
  namespace: ml-training
spec:
  replicas: 5
  selector:
    matchLabels:
      app: ml-training
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      containers:
      - name: trainer
        image: ml-training:v2
        resources:
          limits:
            nvidia.com/gpu: 1
```

### 2. Version Control

All configuration is stored in Git, providing version history and collaboration.

```bash
# Repository structure
ml-gitops-repo/
├── apps/
│   ├── ml-training/
│   │   ├── base/
│   │   │   ├── kustomization.yaml
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   └── model-serving/
├── infrastructure/
│   ├── namespaces/
│   ├── rbac/
│   └── network-policies/
└── platform/
    ├── monitoring/
    ├── logging/
    └── mlflow/
```

**Example Git History:**
```bash
$ git log --oneline
a1b2c3d (HEAD -> main) Scale ML training to 10 replicas for experiment
e4f5g6h Update model serving image to v1.2.3
h7i8j9k Add GPU toleration to training pods
k0l1m2n Fix resource limits for inference service
n3o4p5q Initial ML platform deployment
```

### 3. Automated Delivery

Changes are automatically applied to the system when committed to Git.

**GitHub Actions Workflow:**
```yaml
# .github/workflows/gitops-deploy.yaml
name: GitOps Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup tools
        run: |
          curl -s https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh | bash
          curl -Lo kubeval https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64
          chmod +x kubeval

      - name: Validate manifests
        run: |
          find . -name 'kustomization.yaml' -exec dirname {} \; | while read dir; do
            echo "Validating $dir"
            kustomize build "$dir" | ./kubeval --strict
          done

      - name: Validate policies
        run: |
          # Run OPA policy tests
          opa test policies/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Manifests validated successfully!'
            })

  # Deployment is handled by ArgoCD/FluxCD watching the repo
```

### 4. Continuous Reconciliation

Agents continuously observe actual state and reconcile with desired state from Git.

**Reconciliation Loop:**
```python
# Simplified GitOps reconciliation logic
import time
import subprocess
from typing import Dict

class GitOpsReconciler:
    """Simplified GitOps reconciliation loop"""

    def __init__(self, git_repo: str, target_path: str, interval: int = 30):
        self.git_repo = git_repo
        self.target_path = target_path
        self.interval = interval
        self.current_commit = None

    def reconcile_loop(self):
        """Continuous reconciliation loop"""
        while True:
            try:
                # 1. Check for changes in Git
                latest_commit = self.get_latest_commit()

                if latest_commit != self.current_commit:
                    print(f"Detected new commit: {latest_commit}")

                    # 2. Pull latest changes
                    self.pull_changes()

                    # 3. Apply changes to cluster
                    self.apply_manifests()

                    # 4. Update current commit
                    self.current_commit = latest_commit

                # 5. Verify actual state matches desired state
                self.verify_state()

            except Exception as e:
                print(f"Reconciliation error: {e}")

            time.sleep(self.interval)

    def get_latest_commit(self) -> str:
        """Get latest commit hash from Git"""
        result = subprocess.run(
            ['git', 'ls-remote', self.git_repo, 'HEAD'],
            capture_output=True,
            text=True
        )
        return result.stdout.split()[0]

    def pull_changes(self):
        """Pull latest changes from Git"""
        subprocess.run(['git', 'pull'], check=True)

    def apply_manifests(self):
        """Apply manifests to cluster"""
        subprocess.run(
            ['kubectl', 'apply', '-R', '-f', self.target_path],
            check=True
        )

    def verify_state(self):
        """Verify cluster state matches Git"""
        # Check resources exist and match desired state
        pass

# Usage
reconciler = GitOpsReconciler(
    git_repo='https://github.com/company/ml-gitops.git',
    target_path='./manifests',
    interval=30
)
reconciler.reconcile_loop()
```

## Declarative Infrastructure

### Infrastructure as Data

Everything is defined as data (YAML/JSON), not procedures.

**Kubernetes Manifests:**
```yaml
# ml-training-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ml-training-job
  namespace: ml-training
  labels:
    app: ml-training
    experiment: experiment-42
spec:
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      restartPolicy: Never
      nodeSelector:
        workload-type: gpu
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule

      containers:
      - name: trainer
        image: ml-training:v1.0.0
        command: ["python", "train.py"]
        args:
          - --epochs=100
          - --batch-size=64
          - --learning-rate=0.001

        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1

        env:
        - name: MLFLOW_TRACKING_URI
          value: http://mlflow.mlflow.svc.cluster.local
        - name: EXPERIMENT_NAME
          value: experiment-42
        - name: S3_DATA_PATH
          value: s3://ml-data/training-data/
        - name: AWS_ROLE_ARN
          value: arn:aws:iam::123456789:role/ml-training-role

        volumeMounts:
        - name: data
          mountPath: /data
        - name: models
          mountPath: /models

      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: training-data-pvc
      - name: models
        persistentVolumeClaim:
          claimName: model-storage-pvc
```

### Kustomize for Customization

Manage environment-specific configurations without duplication.

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml

commonLabels:
  app: ml-serving
  managed-by: kustomize

configMapGenerator:
  - name: ml-config
    files:
      - config.yaml
```

```yaml
# overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: ml-serving-dev

replicas:
  - name: ml-serving
    count: 2

images:
  - name: ml-serving
    newTag: dev-latest

patches:
  - patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: ml-serving
      spec:
        template:
          spec:
            containers:
              - name: server
                resources:
                  limits:
                    memory: "2Gi"
                    cpu: "1"
```

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: ml-serving-prod

replicas:
  - name: ml-serving
    count: 10

images:
  - name: ml-serving
    newTag: v1.2.3

patches:
  - patch: |-
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: ml-serving
      spec:
        template:
          spec:
            containers:
              - name: server
                resources:
                  limits:
                    memory: "8Gi"
                    cpu: "4"
```

```bash
# Build manifests for each environment
kustomize build overlays/dev > dev-manifests.yaml
kustomize build overlays/prod > prod-manifests.yaml
```

## Git as Single Source of Truth

### Repository Structure

**Monorepo Approach:**
```
ml-infrastructure/
├── apps/                    # Application deployments
│   ├── training/
│   ├── serving/
│   └── experimentation/
├── infrastructure/          # Infrastructure resources
│   ├── namespaces/
│   ├── rbac/
│   ├── network-policies/
│   └── resource-quotas/
├── platform/               # Platform services
│   ├── monitoring/
│   │   ├── prometheus/
│   │   └── grafana/
│   ├── logging/
│   │   └── elasticsearch/
│   └── mlops/
│       ├── mlflow/
│       └── kubeflow/
└── environments/           # Environment configs
    ├── dev/
    ├── staging/
    └── prod/
```

**Multi-Repo Approach:**
```
Repositories:
├── ml-infrastructure-base    # Shared infrastructure
├── ml-apps-training         # Training applications
├── ml-apps-serving          # Serving applications
└── ml-platform-services     # Platform services
```

### Branch Strategy

**Trunk-Based:**
```
main ─────●──────●──────●──────●──────●─────>
          │      │      │      │      │
          │      │      │      │      └─> Deploy to prod
          │      │      │      └─> Deploy to staging
          │      │      └─> Deploy to dev
          └──────┴──────┴─> All commits trigger deployment
```

**Environment Branches:**
```
main ──────●──────●──────●─────>
            \      \      \
dev ─────────●──────●──────●──>
              \      \
staging ───────●──────●────────>
                \
prod ────────────●─────────────>
```

### Pull Request Workflow

```yaml
# Example PR workflow
name: Pull Request Validation

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate YAML
        run: |
          yamllint -c .yamllint.yaml .

      - name: Check Kubernetes manifests
        run: |
          kustomize build overlays/prod | kubeval --strict

      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'

      - name: Policy validation
        run: |
          conftest test -p policies/ manifests/

      - name: Dry-run deployment
        run: |
          kubectl apply --dry-run=server -k overlays/prod
```

## Automated Deployment

### Continuous Delivery Pipeline

**Complete CI/CD Pipeline:**
```yaml
# .github/workflows/cd.yaml
name: Continuous Delivery

on:
  push:
    branches: [main]
    paths:
      - 'apps/**'
      - 'infrastructure/**'

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to dev
        run: |
          kubectl apply -k overlays/dev
          kubectl rollout status deployment/ml-serving -n ml-serving-dev

      - name: Run smoke tests
        run: |
          ./scripts/smoke-test.sh dev

  deploy-staging:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        run: |
          kubectl apply -k overlays/staging
          kubectl rollout status deployment/ml-serving -n ml-serving-staging

      - name: Run integration tests
        run: |
          ./scripts/integration-test.sh staging

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Create deployment record
        run: |
          echo "Deploying commit ${{ github.sha }} to production"

      - name: Deploy to production
        run: |
          kubectl apply -k overlays/prod

      - name: Progressive rollout
        run: |
          # Canary deployment
          kubectl set image deployment/ml-serving server=ml-serving:${{ github.sha }} -n ml-serving-prod
          kubectl rollout pause deployment/ml-serving -n ml-serving-prod

          # Wait and monitor
          sleep 300

          # If healthy, continue rollout
          if [ "$(./scripts/health-check.sh)" == "healthy" ]; then
            kubectl rollout resume deployment/ml-serving -n ml-serving-prod
            kubectl rollout status deployment/ml-serving -n ml-serving-prod
          else
            kubectl rollout undo deployment/ml-serving -n ml-serving-prod
            exit 1
          fi

      - name: Notify team
        if: always()
        run: |
          ./scripts/notify-slack.sh "${{ job.status }}"
```

### Progressive Delivery

**Canary Deployment with Flagger:**
```yaml
# canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ml-serving
  namespace: ml-serving-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-serving

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
        cmd: "hey -z 1m -q 10 -c 2 http://ml-serving-canary:8080/predict"

  # Promotion or rollback based on metrics
```

## ML Infrastructure GitOps

### Training Pipeline GitOps

**Training Job Definition:**
```yaml
# training-jobs/experiment-123.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: training-experiment-123
  namespace: ml-training
  annotations:
    experiment-id: "123"
    model-type: "resnet50"
    dataset: "imagenet-subset"
spec:
  backoffLimit: 3
  template:
    metadata:
      labels:
        experiment-id: "123"
    spec:
      restartPolicy: OnFailure

      initContainers:
      - name: data-downloader
        image: aws-cli:latest
        command: ["aws", "s3", "sync"]
        args: ["s3://ml-data/imagenet-subset/", "/data"]
        volumeMounts:
        - name: data
          mountPath: /data

      containers:
      - name: trainer
        image: ml-training:v2.0.0
        command: ["python", "train.py"]
        args:
          - --model=resnet50
          - --epochs=50
          - --batch-size=128
          - --lr=0.01
          - --data-path=/data
          - --output-path=/models
          - --mlflow-tracking-uri=http://mlflow:5000
          - --experiment-id=123

        resources:
          limits:
            nvidia.com/gpu: 4
            memory: "64Gi"
            cpu: "16"

        volumeMounts:
        - name: data
          mountPath: /data
        - name: models
          mountPath: /models
        - name: dshm
          mountPath: /dev/shm

      volumes:
      - name: data
        emptyDir: {}
      - name: models
        persistentVolumeClaim:
          claimName: model-storage
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: 32Gi
```

### Model Serving GitOps

**Seldon Deployment:**
```yaml
# model-serving/sentiment-classifier.yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: sentiment-classifier
  namespace: ml-serving
spec:
  name: sentiment-classifier
  predictors:
  - name: default
    replicas: 3

    componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: ml-models/sentiment-classifier:v1.2.3
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"

          env:
          - name: MODEL_PATH
            value: /models/sentiment-classifier
          - name: MLFLOW_TRACKING_URI
            value: http://mlflow:5000

          volumeMounts:
          - name: model-storage
            mountPath: /models

        volumes:
        - name: model-storage
          persistentVolumeClaim:
            claimName: model-storage

    graph:
      name: classifier
      type: MODEL
      parameters:
      - name: model_uri
        value: "s3://ml-models/sentiment-classifier/v1.2.3"

    traffic: 100

  # A/B testing
  - name: challenger
    replicas: 1
    graph:
      name: classifier-v2
      type: MODEL
      parameters:
      - name: model_uri
        value: "s3://ml-models/sentiment-classifier/v1.3.0"
    traffic: 0
```

### Feature Store GitOps

**Feast Feature Store:**
```yaml
# feature-store/features.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: feast-features
  namespace: ml-platform
data:
  user_features.py: |
    from feast import Entity, Feature, FeatureView, ValueType
    from feast.data_source import BigQuerySource
    from datetime import timedelta

    user = Entity(
        name="user_id",
        value_type=ValueType.INT64,
        description="User ID"
    )

    user_features = FeatureView(
        name="user_features",
        entities=["user_id"],
        ttl=timedelta(days=1),
        features=[
            Feature(name="age", dtype=ValueType.INT64),
            Feature(name="country", dtype=ValueType.STRING),
            Feature(name="total_purchases", dtype=ValueType.INT64),
            Feature(name="avg_purchase_value", dtype=ValueType.FLOAT),
        ],
        batch_source=BigQuerySource(
            table_ref="project.dataset.user_features",
            event_timestamp_column="event_timestamp",
        )
    )
```

## Summary

GitOps provides:
- **Declarative**: Desired state in Git
- **Versioned**: Complete change history
- **Automated**: Continuous reconciliation
- **Auditable**: All changes tracked
- **Reversible**: Easy rollback via Git
- **Collaborative**: Standard Git workflows

**Key Principles:**
1. Declarative description of system
2. Version control as single source of truth
3. Automated delivery from Git
4. Continuous reconciliation
5. Immutable infrastructure

## Next Steps

- Continue to [Lecture 4: ArgoCD Deployment](04-argocd-deployment.md)
- Set up a GitOps repository structure
- Practice with declarative manifests
- Implement Kustomize overlays

## Additional Resources

- [GitOps Principles](https://www.gitops.tech/)
- [CNCF GitOps Working Group](https://github.com/cncf/tag-app-delivery)
- [Kustomize Documentation](https://kustomize.io/)
- [GitOps Toolkit](https://toolkit.fluxcd.io/)
