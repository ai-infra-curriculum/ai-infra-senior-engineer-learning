#!/bin/bash
# Deploy script for TrainingJob Kubernetes Operator
# This script deploys the operator to a Kubernetes cluster
#
# TODO for students: Add:
# - Docker image building
# - Image registry push
# - Helm chart deployment
# - Configuration validation
# - Deployment verification

set -e

echo "===================================="
echo "TrainingJob Operator Deployment"
echo "===================================="

# Load configuration
if [ -f .env ]; then
    echo "Loading configuration from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

NAMESPACE=${WATCH_NAMESPACE:-trainingjob-system}
DEPLOYMENT_NAME="trainingjob-operator"

# TODO for students: Build Docker image
# echo ""
# echo "Building Docker image..."
# IMAGE_TAG="${OPERATOR_IMAGE:-trainingjob-operator:latest}"
# docker build -t $IMAGE_TAG .

# TODO for students: Push to registry
# if [ -n "$DOCKER_REGISTRY" ]; then
#     echo ""
#     echo "Pushing image to registry..."
#     docker tag $IMAGE_TAG $DOCKER_REGISTRY/$IMAGE_TAG
#     docker push $DOCKER_REGISTRY/$IMAGE_TAG
# fi

# Install CRD
echo ""
echo "Installing TrainingJob CRD..."
python3 -m src.operator.main --install-crd

# TODO for students: Create deployment
# echo ""
# echo "Creating operator deployment..."
# kubectl apply -f deploy/operator.yaml -n $NAMESPACE

# For local development, run operator directly
echo ""
echo "Starting operator (local mode)..."
echo "Press Ctrl+C to stop"
echo ""

# Set environment variables
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export WATCH_NAMESPACE=$NAMESPACE

# Run operator
python3 -m src.operator.main --namespace $NAMESPACE

# TODO for students: Wait for deployment to be ready (if using k8s deployment)
# echo ""
# echo "Waiting for deployment to be ready..."
# kubectl wait --for=condition=available --timeout=300s \
#     deployment/$DEPLOYMENT_NAME -n $NAMESPACE

# echo ""
# echo "===================================="
# echo "Deployment complete!"
# echo "===================================="
# echo ""
# echo "Operator is running in namespace: $NAMESPACE"
# echo ""
# echo "Check status:"
# echo "  kubectl get pods -n $NAMESPACE"
# echo ""
# echo "View logs:"
# echo "  kubectl logs -f deployment/$DEPLOYMENT_NAME -n $NAMESPACE"
# echo ""
