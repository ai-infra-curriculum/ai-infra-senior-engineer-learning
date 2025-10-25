#!/bin/bash
# Setup script for TrainingJob Kubernetes Operator
# This script installs dependencies and prepares the development environment
#
# TODO for students: Add:
# - Virtual environment creation
# - Python version checking
# - Kubernetes cluster verification
# - RBAC setup
# - Namespace creation

set -e

echo "===================================="
echo "TrainingJob Operator Setup"
echo "===================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# TODO for students: Validate Python version >= 3.11
# if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
#     echo "Error: Python 3.11+ required"
#     exit 1
# fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# TODO for students: Install development dependencies
# pip3 install -r requirements-dev.txt

# Check kubectl
echo ""
echo "Checking kubectl..."
if ! command -v kubectl &> /dev/null; then
    echo "Warning: kubectl not found. Please install kubectl."
else
    kubectl_version=$(kubectl version --client --short 2>&1 | grep 'Client')
    echo "$kubectl_version"
fi

# TODO for students: Check cluster connectivity
# echo ""
# echo "Checking Kubernetes cluster..."
# if ! kubectl cluster-info &> /dev/null; then
#     echo "Warning: Cannot connect to Kubernetes cluster"
#     echo "Please configure kubectl to connect to your cluster"
# else
#     echo "Kubernetes cluster accessible"
#     kubectl cluster-info
# fi

# Create namespace if it doesn't exist
NAMESPACE=${WATCH_NAMESPACE:-trainingjob-system}
echo ""
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# TODO for students: Create RBAC resources
# echo ""
# echo "Creating RBAC resources..."
# kubectl apply -f deploy/rbac.yaml

# TODO for students: Create CRD
# echo ""
# echo "Installing TrainingJob CRD..."
# python3 -m src.operator.main --install-crd

echo ""
echo "===================================="
echo "Setup complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "  1. Review and edit .env file"
echo "  2. Run ./scripts/test.sh to validate setup"
echo "  3. Run ./scripts/deploy.sh to start the operator"
echo ""
