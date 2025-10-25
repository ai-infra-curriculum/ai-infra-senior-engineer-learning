# TrainingJob Operator Deployment Guide

Step-by-step deployment instructions for production and development environments.

## Prerequisites

- Kubernetes cluster 1.24+
- kubectl configured
- Python 3.11+
- Helm 3+ (optional)
- Docker (for containerized deployment)

## Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/your-org/trainingjob-operator
cd trainingjob-operator

# Install dependencies
./scripts/setup.sh

# Deploy operator (local mode)
./scripts/deploy.sh
```

## Production Deployment

### 1. Prerequisites Setup

```bash
# Verify cluster access
kubectl cluster-info

# Create namespace
kubectl create namespace trainingjob-system

# Create RBAC resources
kubectl apply -f deploy/rbac.yaml
```

### 2. Install CRD

```bash
# Install TrainingJob CRD
kubectl apply -f deploy/crd.yaml

# Verify CRD installation
kubectl get crd trainingjobs.mlplatform.example.com
```

### 3. Build Operator Image

```bash
# Build Docker image
docker build -t your-registry/trainingjob-operator:v1.0.0 .

# Push to registry
docker push your-registry/trainingjob-operator:v1.0.0
```

### 4. Deploy Operator

#### Option A: Using kubectl

```bash
# Create deployment
kubectl apply -f deploy/operator.yaml -n trainingjob-system

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s \
  deployment/trainingjob-operator -n trainingjob-system

# Check status
kubectl get pods -n trainingjob-system
kubectl logs -f deployment/trainingjob-operator -n trainingjob-system
```

#### Option B: Using Helm

```bash
# Install via Helm
helm install trainingjob-operator ./helm/trainingjob-operator \
  --namespace trainingjob-system \
  --create-namespace \
  --set image.repository=your-registry/trainingjob-operator \
  --set image.tag=v1.0.0

# Verify installation
helm list -n trainingjob-system
```

### 5. Verify Deployment

```bash
# Check operator logs
kubectl logs -f -n trainingjob-system \
  -l app=trainingjob-operator

# Create test job
cat <<EOF | kubectl apply -f -
apiVersion: mlplatform.example.com/v1alpha1
kind: TrainingJob
metadata:
  name: test-job
spec:
  framework: pytorch
  image: pytorch/pytorch:2.1.0
  command: ["python", "-c", "print('Hello from TrainingJob')"]
EOF

# Check job status
kubectl get trainingjobs
kubectl describe trainingjob test-job
```

## Configuration

### Environment Variables

Create `.env` file:
```bash
LOG_LEVEL=INFO
WATCH_NAMESPACE=  # Empty = all namespaces
WORKER_THREADS=10
RESYNC_PERIOD=300
```

### RBAC Configuration

The operator requires these permissions:

```yaml
# deploy/rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: trainingjob-operator
rules:
  - apiGroups: ["mlplatform.example.com"]
    resources: ["trainingjobs"]
    verbs: ["get", "list", "watch", "update", "patch"]
  - apiGroups: ["mlplatform.example.com"]
    resources: ["trainingjobs/status"]
    verbs: ["get", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

## High Availability Setup

### Leader Election

```bash
# Enable leader election in deployment
kubectl set env deployment/trainingjob-operator \
  LEADER_ELECTION_ENABLED=true \
  -n trainingjob-system

# Scale to multiple replicas
kubectl scale deployment/trainingjob-operator \
  --replicas=3 \
  -n trainingjob-system
```

## Monitoring Setup

### Prometheus Integration

```yaml
# ServiceMonitor for Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: trainingjob-operator
  namespace: trainingjob-system
spec:
  selector:
    matchLabels:
      app: trainingjob-operator
  endpoints:
    - port: metrics
      interval: 30s
```

### Grafana Dashboard

```bash
# Import dashboard
kubectl apply -f deploy/grafana-dashboard.json
```

## Storage Configuration

### PVC for Checkpoints

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: training-checkpoints
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  storageClassName: nfs
```

### S3 Configuration

```bash
# Create secret for S3 credentials
kubectl create secret generic s3-credentials \
  --from-literal=access-key=YOUR_ACCESS_KEY \
  --from-literal=secret-key=YOUR_SECRET_KEY \
  -n trainingjob-system
```

## Network Configuration

### Ingress for Metrics

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: operator-metrics
spec:
  rules:
    - host: metrics.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: trainingjob-operator
                port:
                  number: 8000
```

## Upgrading

### Rolling Upgrade

```bash
# Update image
kubectl set image deployment/trainingjob-operator \
  operator=your-registry/trainingjob-operator:v1.1.0 \
  -n trainingjob-system

# Watch rollout
kubectl rollout status deployment/trainingjob-operator \
  -n trainingjob-system
```

### CRD Upgrade

```bash
# Backup existing resources
kubectl get trainingjobs -A -o yaml > backup.yaml

# Update CRD
kubectl apply -f deploy/crd-v1.1.0.yaml

# Verify
kubectl get crd trainingjobs.mlplatform.example.com -o yaml
```

## Cleanup

```bash
# Delete all TrainingJobs
kubectl delete trainingjobs --all -A

# Delete operator
kubectl delete deployment trainingjob-operator -n trainingjob-system

# Delete CRD
kubectl delete crd trainingjobs.mlplatform.example.com

# Delete namespace
kubectl delete namespace trainingjob-system
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
