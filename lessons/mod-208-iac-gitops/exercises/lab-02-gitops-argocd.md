# Lab 2: GitOps with ArgoCD

## Objectives

- Install and configure ArgoCD
- Create GitOps repository structure
- Deploy ML applications via GitOps
- Implement progressive delivery patterns

## Duration

6 hours

## Lab Tasks

### Task 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ready
kubectl wait --for=condition=available --timeout=600s deployment/argocd-server -n argocd

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### Task 2: Create GitOps Repository Structure

```bash
mkdir ml-gitops && cd ml-gitops

# Create structure
mkdir -p {apps/{training,serving},infrastructure/{namespaces,rbac},platform/mlflow}

# Initialize Git
git init
git add .
git commit -m "Initial GitOps structure"
```

### Task 3: ML Training Application

Create `apps/training/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training
  namespace: ml-training
spec:
  replicas: 3
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
        image: ml-training:v1.0.0
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "4"
```

### Task 4: Create ArgoCD Application

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
    repoURL: https://github.com/your-org/ml-gitops
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

### Task 5: Apply and Verify

```bash
kubectl apply -f argocd-apps/ml-training.yaml

# Watch sync
argocd app get ml-training

# View in UI
open http://localhost:8080
```

## Exercises

1. Add Model Serving Application
2. Implement Canary Deployment
3. Set up Multi-Cluster Deployment
4. Configure Notifications

## Submission

- GitOps repository URL
- ArgoCD application screenshots
- Sync status output
