#!/bin/bash
# Multi-Region Infrastructure Setup Script
# TODO for students: Add cloud provider authentication, add region selection, validate prerequisites

set -euo pipefail

echo "========================================"
echo "Multi-Region ML Platform Setup"
echo "========================================"

# Configuration
REGIONS="${REGIONS:-us-east-1,eu-west-1,ap-southeast-1}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-aws}"
TERRAFORM_DIR="./terraform"

echo "Cloud Provider: $CLOUD_PROVIDER"
echo "Target Regions: $REGIONS"

# Check prerequisites
echo -e "\n[1/6] Checking prerequisites..."
command -v terraform >/dev/null 2>&1 || { echo "Error: terraform not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "Error: kubectl not installed"; exit 1; }
command -v aws >/dev/null 2>&1 || echo "Warning: AWS CLI not found"
echo "  ✓ Prerequisites check complete"

# Initialize Terraform
echo -e "\n[2/6] Initializing Terraform..."
cd "$TERRAFORM_DIR"
terraform init
echo "  ✓ Terraform initialized"

# Create Terraform workspace per region
echo -e "\n[3/6] Creating Terraform workspaces..."
IFS=',' read -ra REGION_ARRAY <<< "$REGIONS"
for region in "${REGION_ARRAY[@]}"; do
    terraform workspace new "$region" 2>/dev/null || terraform workspace select "$region"
    echo "  ✓ Workspace created: $region"
done
cd ..

# Setup Python environment
echo -e "\n[4/6] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "  ✓ Python environment ready"

# Create configuration files
echo -e "\n[5/6] Creating configuration files..."
cp .env.example .env
echo "  ✓ Configuration files created (edit .env with your settings)"

# Validate cloud credentials
echo -e "\n[6/6] Validating cloud credentials..."
case "$CLOUD_PROVIDER" in
    aws)
        aws sts get-caller-identity >/dev/null && echo "  ✓ AWS credentials valid" || echo "  ⚠ AWS credentials not configured"
        ;;
    gcp)
        gcloud auth list >/dev/null 2>&1 && echo "  ✓ GCP credentials valid" || echo "  ⚠ GCP credentials not configured"
        ;;
    azure)
        az account show >/dev/null 2>&1 && echo "  ✓ Azure credentials valid" || echo "  ⚠ Azure credentials not configured"
        ;;
esac

echo -e "\n========================================"
echo "Setup complete!"
echo "Next steps:"
echo "  1. Edit .env with your configuration"
echo "  2. Run: ./scripts/deploy.sh"
echo "========================================"
