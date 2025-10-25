# Lab 2: Multi-Cloud Application Deployment

## Objective

Deploy a containerized ML inference application across AWS EKS and GCP GKE with unified service mesh and observability.

## Prerequisites

- Completed Lab 1 (AWS-GCP VPN)
- Docker installed
- kubectl configured
- Helm 3 installed
- Understanding of Kubernetes and Istio

## Estimated Time

3-4 hours

---

## Architecture Overview

```
                    ┌──────────────────────────────┐
                    │   Global Load Balancer       │
                    │   (Cloud Load Balancing)     │
                    └──────────┬──────────┬────────┘
                               │          │
                ┌──────────────┘          └──────────────┐
                │                                        │
        ┌───────▼─────────┐                    ┌────────▼────────┐
        │   AWS EKS       │                    │   GCP GKE       │
        │   Cluster       │◄──────VPN─────────►│   Cluster       │
        │                 │                    │                 │
        │ ┌─────────────┐ │                    │ ┌─────────────┐ │
        │ │   Istio     │ │                    │ │   Istio     │ │
        │ │  Control    │ │                    │ │  Control    │ │
        │ │   Plane     │ │                    │ │   Plane     │ │
        │ └─────────────┘ │                    │ └─────────────┘ │
        │                 │                    │                 │
        │ ┌─────────────┐ │                    │ ┌─────────────┐ │
        │ │ Inference   │ │                    │ │ Inference   │ │
        │ │  Service    │ │                    │ │  Service    │ │
        │ │  (3 pods)   │ │                    │ │  (3 pods)   │ │
        │ └─────────────┘ │                    │ └─────────────┘ │
        └─────────────────┘                    └─────────────────┘
                │                                        │
                └────────────────┬───────────────────────┘
                                 │
                        ┌────────▼─────────┐
                        │   Prometheus     │
                        │   (Multi-Cloud)  │
                        └──────────────────┘
```

---

## Part 1: Prepare Application

### Step 1.1: Create Inference Application

Create `app/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import numpy as np
import os
import logging

app = FastAPI(title="ML Inference Service")
logger = logging.getLogger(__name__)

# Metadata
CLOUD_PROVIDER = os.environ.get("CLOUD_PROVIDER", "unknown")
REGION = os.environ.get("REGION", "unknown")
POD_NAME = os.environ.get("HOSTNAME", "unknown")

# Dummy model for demo
class DummyModel:
    def predict(self, input_data):
        # Simulate inference
        return np.random.rand(10).tolist()

model = DummyModel()

class PredictionRequest(BaseModel):
    data: list

class PredictionResponse(BaseModel):
    prediction: list
    metadata: dict

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "cloud": CLOUD_PROVIDER,
        "region": REGION,
        "pod": POD_NAME
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        prediction = model.predict(request.data)

        return PredictionResponse(
            prediction=prediction,
            metadata={
                "cloud": CLOUD_PROVIDER,
                "region": REGION,
                "pod": POD_NAME
            }
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "service": "ML Inference Service",
        "version": "1.0.0",
        "cloud": CLOUD_PROVIDER,
        "region": REGION
    }
```

Create `app/requirements.txt`:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
torch==2.1.0
numpy==1.24.3
prometheus-client==0.19.0
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/main.py .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 1.2: Build and Push Container

```bash
# Build for multi-architecture
docker buildx create --name multiarch --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t gcr.io/YOUR_PROJECT/ml-inference:v1.0 \
  --push .

# Also push to AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

docker tag gcr.io/YOUR_PROJECT/ml-inference:v1.0 \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-inference:v1.0

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-inference:v1.0
```

---

## Part 2: Deploy to AWS EKS

### Step 2.1: Create EKS Cluster

Create `eks-cluster.tf`:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "ml-inference-cluster"
  cluster_version = "1.28"

  vpc_id     = aws_vpc.main.id
  subnet_ids = [aws_subnet.private.id]

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    inference = {
      min_size     = 2
      max_size     = 6
      desired_size = 3

      instance_types = ["t3.medium"]
      capacity_type  = "SPOT"

      labels = {
        workload = "inference"
      }
    }
  }

  tags = {
    Environment = "lab"
    Project     = "multi-cloud-deployment"
  }
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}
```

### Step 2.2: Install Istio on EKS

```bash
# Configure kubectl
aws eks update-kubeconfig --name ml-inference-cluster --region us-east-1

# Install Istio
istioctl install --set profile=demo -y

# Enable automatic sidecar injection
kubectl label namespace default istio-injection=enabled
```

### Step 2.3: Deploy Application to EKS

Create `k8s/aws-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-inference
  labels:
    istio-injection: enabled
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference-aws
  namespace: ml-inference
  labels:
    app: ml-inference
    cloud: aws
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
      cloud: aws
  template:
    metadata:
      labels:
        app: ml-inference
        cloud: aws
        version: v1
    spec:
      containers:
      - name: inference
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-inference:v1.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: CLOUD_PROVIDER
          value: "aws"
        - name: REGION
          value: "us-east-1"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference
  namespace: ml-inference
  labels:
    app: ml-inference
spec:
  selector:
    app: ml-inference
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-inference
  namespace: ml-inference
spec:
  hosts:
  - ml-inference.ml-inference.svc.cluster.local
  http:
  - route:
    - destination:
        host: ml-inference.ml-inference.svc.cluster.local
        port:
          number: 8000
      weight: 100
```

Apply the configuration:

```bash
kubectl apply -f k8s/aws-deployment.yaml
```

---

## Part 3: Deploy to GCP GKE

### Step 3.1: Create GKE Cluster

Create `gke-cluster.tf`:

```hcl
resource "google_container_cluster" "primary" {
  name     = "ml-inference-cluster"
  location = "us-central1"

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.private.name

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }

  workload_identity_config {
    workload_pool = "YOUR_PROJECT_ID.svc.id.goog"
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "inference-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.primary.name
  node_count = 3

  node_config {
    preemptible  = true
    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      workload = "inference"
    }

    tags = ["inference"]
  }

  autoscaling {
    min_node_count = 2
    max_node_count = 6
  }
}

output "gke_cluster_endpoint" {
  value     = google_container_cluster.primary.endpoint
  sensitive = true
}

output "gke_cluster_name" {
  value = google_container_cluster.primary.name
}
```

### Step 3.2: Install Istio on GKE

```bash
# Configure kubectl for GKE
gcloud container clusters get-credentials ml-inference-cluster \
  --region us-central1

# Install Istio
istioctl install --set profile=demo -y

# Enable automatic sidecar injection
kubectl label namespace default istio-injection=enabled
```

### Step 3.3: Deploy Application to GKE

Create `k8s/gcp-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-inference
  labels:
    istio-injection: enabled
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference-gcp
  namespace: ml-inference
  labels:
    app: ml-inference
    cloud: gcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
      cloud: gcp
  template:
    metadata:
      labels:
        app: ml-inference
        cloud: gcp
        version: v1
    spec:
      containers:
      - name: inference
        image: gcr.io/YOUR_PROJECT/ml-inference:v1.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: CLOUD_PROVIDER
          value: "gcp"
        - name: REGION
          value: "us-central1"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference
  namespace: ml-inference
  labels:
    app: ml-inference
spec:
  selector:
    app: ml-inference
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
```

Apply:

```bash
kubectl apply -f k8s/gcp-deployment.yaml
```

---

## Part 4: Multi-Cluster Service Mesh

### Step 4.1: Configure Istio Multi-Cluster

```bash
# Generate remote secrets for cross-cluster communication
istioctl x create-remote-secret \
  --context=aws-context \
  --name=aws-cluster | \
  kubectl apply -f - --context=gcp-context

istioctl x create-remote-secret \
  --context=gcp-context \
  --name=gcp-cluster | \
  kubectl apply -f - --context=aws-context
```

### Step 4.2: Configure Traffic Distribution

Create `k8s/traffic-split.yaml`:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-inference
  namespace: ml-inference
spec:
  host: ml-inference.ml-inference.svc.cluster.local
  subsets:
  - name: aws
    labels:
      cloud: aws
  - name: gcp
    labels:
      cloud: gcp
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-inference-split
  namespace: ml-inference
spec:
  hosts:
  - ml-inference.ml-inference.svc.cluster.local
  http:
  - match:
    - headers:
        prefer-cloud:
          exact: aws
    route:
    - destination:
        host: ml-inference.ml-inference.svc.cluster.local
        subset: aws
  - match:
    - headers:
        prefer-cloud:
          exact: gcp
    route:
    - destination:
        host: ml-inference.ml-inference.svc.cluster.local
        subset: gcp
  - route:
    - destination:
        host: ml-inference.ml-inference.svc.cluster.local
        subset: aws
      weight: 50
    - destination:
        host: ml-inference.ml-inference.svc.cluster.local
        subset: gcp
      weight: 50
```

---

## Part 5: Observability

### Step 5.1: Deploy Prometheus

```bash
# Install Prometheus with Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Step 5.2: Configure Service Monitors

Create `k8s/service-monitor.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ml-inference
  namespace: ml-inference
spec:
  selector:
    matchLabels:
      app: ml-inference
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
```

---

## Part 6: Testing

### Step 6.1: Test Service

```bash
# Port-forward to service
kubectl port-forward -n ml-inference svc/ml-inference 8000:8000

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3, 4, 5]}'
```

### Step 6.2: Load Testing

```bash
# Install hey
go install github.com/rakyll/hey@latest

# Run load test
hey -n 10000 -c 100 -m POST \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3, 4, 5]}' \
  http://localhost:8000/predict
```

---

## Challenge Exercises

1. Implement canary deployment across clouds
2. Add circuit breaking and retry policies
3. Set up distributed tracing with Jaeger
4. Configure automatic failover on cluster failure
5. Implement cost-based traffic routing

## Learning Outcomes

- ✓ Deploy applications across multiple clouds
- ✓ Configure service mesh for multi-cluster
- ✓ Implement traffic management
- ✓ Set up unified observability
- ✓ Test multi-cloud deployments

## Cleanup

```bash
terraform destroy
```
