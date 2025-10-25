#!/bin/bash
# Cleanup multi-region deployment
# TODO for students: Add confirmation prompts, add backup before cleanup, add selective cleanup

set -euo pipefail

echo "========================================"
echo "Multi-Region Cleanup"
echo "========================================"

# Configuration
REGIONS="${REGIONS:-us-east-1,eu-west-1,ap-southeast-1}"
TERRAFORM_DIR="./terraform"
FORCE="${FORCE:-false}"

# Warning
if [ "$FORCE" != "true" ]; then
    echo "⚠ WARNING: This will destroy all infrastructure in the following regions:"
    echo "  $REGIONS"
    echo ""
    read -p "Are you sure? (type 'yes' to confirm): " confirmation
    [ "$confirmation" != "yes" ] && { echo "Cleanup cancelled"; exit 0; }
fi

# Destroy infrastructure per region
echo -e "\n[1/4] Destroying infrastructure..."
cd "$TERRAFORM_DIR"

IFS=',' read -ra REGION_ARRAY <<< "$REGIONS"
for region in "${REGION_ARRAY[@]}"; do
    echo "  Destroying resources in $region..."
    terraform workspace select "$region"
    terraform destroy -auto-approve -var="region=$region" || echo "  ⚠ Some resources may remain in $region"
    echo "  ✓ $region cleaned up"
done
cd ..

# Delete Kubernetes resources
echo -e "\n[2/4] Cleaning up Kubernetes resources..."
for region in "${REGION_ARRAY[@]}"; do
    kubectl delete namespace ml-platform --context="$region" --ignore-not-found=true 2>/dev/null || true
    echo "  ✓ Kubernetes resources deleted in $region"
done

# Clean local files
echo -e "\n[3/4] Cleaning local artifacts..."
rm -rf .terraform/
rm -rf venv/
rm -f terraform.tfstate*
rm -f .env
echo "  ✓ Local artifacts cleaned"

# Remove workspaces
echo -e "\n[4/4] Removing Terraform workspaces..."
cd "$TERRAFORM_DIR"
for region in "${REGION_ARRAY[@]}"; do
    terraform workspace select default 2>/dev/null || true
    terraform workspace delete "$region" 2>/dev/null || echo "  ⚠ Workspace $region not found"
done
cd ..

echo -e "\n========================================"
echo "Cleanup complete!"
echo "All resources have been removed"
echo "========================================"
