#!/bin/bash
# Deploy model serving infrastructure to Kubernetes
# TODO for students: Add health checks, add rollback capability, add canary deployment

set -euo pipefail

echo "========================================="
echo "Deploy Model Serving Infrastructure"
echo "========================================="

NAMESPACE="${NAMESPACE:-default}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

echo "Deploying to namespace: $NAMESPACE"
echo "Environment: $ENVIRONMENT"

# Create namespace if it doesn't exist
echo -e "\n[1/6] Creating namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy monitoring stack
echo -e "\n[2/6] Deploying monitoring..."
kubectl apply -f monitoring/prometheus-config.yaml -n "$NAMESPACE"
kubectl apply -f monitoring/jaeger-deployment.yaml -n "$NAMESPACE"
kubectl apply -f monitoring/custom-metrics.yaml -n "$NAMESPACE"

# Build and push Docker images
echo -e "\n[3/6] Building Docker images..."
docker build -t model-serving:$ENVIRONMENT .
# docker push model-serving:$ENVIRONMENT  # Uncomment for registry push

# Deploy model serving
echo -e "\n[4/6] Deploying model serving..."
kubectl apply -f kubernetes/ -n "$NAMESPACE"

# Wait for deployments
echo -e "\n[5/6] Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/model-serving -n "$NAMESPACE" || echo "Deployment still progressing..."

# Port forwarding for local access
echo -e "\n[6/6] Setting up port forwarding..."
echo "Run these commands in separate terminals:"
echo "  kubectl port-forward -n $NAMESPACE svc/model-serving 8080:80"
echo "  kubectl port-forward -n $NAMESPACE svc/jaeger 16686:16686"
echo "  kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"

echo -e "\n========================================="
echo "Deployment complete!"
echo "Model serving: http://localhost:8080"
echo "Jaeger UI: http://localhost:16686"
echo "Grafana: http://localhost:3000"
echo "========================================="
