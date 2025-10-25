#!/bin/bash
# Cleanup script for model serving infrastructure
# TODO for students: Add confirmation prompts, add selective cleanup, backup before delete

set -euo pipefail

echo "========================================="
echo "Cleanup Model Serving Infrastructure"
echo "========================================="

NAMESPACE="${NAMESPACE:-default}"

echo "Cleaning up Kubernetes resources in namespace: $NAMESPACE"

# Stop model serving deployments
echo -e "\n[1/5] Stopping model serving deployments..."
kubectl delete deployment -l app=model-serving -n "$NAMESPACE" --ignore-not-found=true

# Delete services
echo -e "\n[2/5] Deleting services..."
kubectl delete service -l app=model-serving -n "$NAMESPACE" --ignore-not-found=true

# Delete monitoring stack
echo -e "\n[3/5] Cleaning up monitoring..."
kubectl delete deployment jaeger prometheus grafana -n "$NAMESPACE" --ignore-not-found=true
kubectl delete service jaeger prometheus grafana -n "$NAMESPACE" --ignore-not-found=true

# Clean up local artifacts
echo -e "\n[4/5] Cleaning local artifacts..."
rm -rf results/*.json
rm -rf models/tensorrt/*.engine
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Clean up Docker containers (optional)
echo -e "\n[5/5] Cleaning Docker containers..."
docker ps -a | grep model-serving | awk '{print $1}' | xargs docker rm -f 2>/dev/null || echo "No containers to clean"

echo -e "\n========================================="
echo "Cleanup complete!"
echo "========================================="
