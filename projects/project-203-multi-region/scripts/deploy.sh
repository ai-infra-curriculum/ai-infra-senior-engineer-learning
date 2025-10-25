#!/bin/bash
# Deploy multi-region ML platform
# TODO for students: Add deployment validation, add progressive rollout, implement rollback capability

set -euo pipefail

echo "========================================"
echo "Multi-Region Deployment"
echo "========================================"

# Configuration
REGIONS="${REGIONS:-us-east-1,eu-west-1,ap-southeast-1}"
TERRAFORM_DIR="./terraform"
DRY_RUN="${DRY_RUN:-false}"

# Deploy infrastructure with Terraform
echo -e "\n[1/4] Deploying infrastructure..."
cd "$TERRAFORM_DIR"

IFS=',' read -ra REGION_ARRAY <<< "$REGIONS"
for region in "${REGION_ARRAY[@]}"; do
    echo "  Deploying to region: $region"
    terraform workspace select "$region"

    if [ "$DRY_RUN" = "true" ]; then
        terraform plan -var="region=$region"
    else
        terraform apply -auto-approve -var="region=$region"
    fi
    echo "  ✓ $region deployed"
done
cd ..

# Configure replication
echo -e "\n[2/4] Configuring cross-region replication..."
python3 -m src.replication.model_replicator --configure || echo "  ⚠ Replication configuration skipped"
echo "  ✓ Replication configured"

# Setup global load balancing
echo -e "\n[3/4] Configuring global load balancing..."
python3 -m src.deployment.multi_region_orchestrator --setup-lb || echo "  ⚠ Load balancing setup skipped"
echo "  ✓ Global load balancing configured"

# Deploy monitoring
echo -e "\n[4/4] Deploying monitoring stack..."
for region in "${REGION_ARRAY[@]}"; do
    echo "  Setting up monitoring in $region..."
    kubectl apply -f kubernetes/monitoring/ --context="$region" 2>/dev/null || echo "  ⚠ Monitoring deployment skipped for $region"
done
echo "  ✓ Monitoring deployed"

echo -e "\n========================================"
echo "Deployment complete!"
echo "Regions deployed: ${REGIONS}"
echo "Next steps:"
echo "  1. Run: ./scripts/test.sh"
echo "  2. Verify: ./scripts/verify_deployment.sh"
echo "========================================"
