#!/bin/bash
# Cleanup script for TrainingJob Kubernetes Operator
# This script removes operator resources from the cluster
#
# TODO for students: Add:
# - Confirmation prompt
# - Backup option before cleanup
# - Selective cleanup (CRD only, deployment only, etc.)
# - Cleanup verification

set -e

echo "===================================="
echo "TrainingJob Operator Cleanup"
echo "===================================="

NAMESPACE=${WATCH_NAMESPACE:-trainingjob-system}

# TODO for students: Add confirmation prompt
# read -p "This will delete all operator resources. Continue? (y/N) " -n 1 -r
# echo
# if [[ ! $REPLY =~ ^[Yy]$ ]]; then
#     echo "Cleanup cancelled"
#     exit 0
# fi

# Delete TrainingJob resources
echo ""
echo "Deleting TrainingJob resources..."
if kubectl get trainingjobs -A &> /dev/null; then
    kubectl delete trainingjobs --all -A
    echo "TrainingJob resources deleted"
else
    echo "No TrainingJob resources found"
fi

# TODO for students: Delete operator deployment
# echo ""
# echo "Deleting operator deployment..."
# kubectl delete deployment trainingjob-operator -n $NAMESPACE --ignore-not-found

# TODO for students: Delete RBAC resources
# echo ""
# echo "Deleting RBAC resources..."
# kubectl delete -f deploy/rbac.yaml --ignore-not-found

# Delete CRD
echo ""
echo "Deleting TrainingJob CRD..."
kubectl delete crd trainingjobs.mlplatform.example.com --ignore-not-found
echo "CRD deleted"

# Delete namespace
echo ""
echo "Deleting namespace: $NAMESPACE"
kubectl delete namespace $NAMESPACE --ignore-not-found
echo "Namespace deleted"

# TODO for students: Clean up local files
# echo ""
# echo "Cleaning up local files..."
# rm -rf htmlcov/
# rm -rf .pytest_cache/
# rm -rf __pycache__/
# find . -type d -name '__pycache__' -exec rm -rf {} +
# find . -type f -name '*.pyc' -delete

echo ""
echo "===================================="
echo "Cleanup complete!"
echo "===================================="
echo ""
echo "All operator resources have been removed."
echo ""
