# Multi-Region ML Platform - Deployment Guide

> **TODO for students**: Customize this deployment guide with your specific cloud provider setup, automation scripts, and validation procedures.

## Prerequisites

### Required Tools

- [ ] Terraform >= 1.5.0
- [ ] kubectl >= 1.27.0
- [ ] Docker >= 24.0.0
- [ ] Python >= 3.11
- [ ] Cloud CLI (AWS CLI, gcloud, or az)
- [ ] Git

### Required Accounts & Permissions

- [ ] Cloud provider account with admin access
- [ ] GitHub/GitLab account for code repository
- [ ] PagerDuty account for alerting (optional)
- [ ] Datadog/New Relic account for monitoring (optional)

### Knowledge Requirements

- Understanding of Kubernetes concepts
- Familiarity with Terraform and IaC
- Basic understanding of multi-region architectures
- Cloud provider networking concepts

## Deployment Overview

### Deployment Phases

1. **Phase 1**: Infrastructure Setup (Terraform)
2. **Phase 2**: Kubernetes Cluster Configuration
3. **Phase 3**: Application Deployment
4. **Phase 4**: Monitoring Stack Setup
5. **Phase 5**: Traffic Management Configuration
6. **Phase 6**: Validation & Testing

### Deployment Timeline

- **Single Region**: 2-3 hours
- **Multi-Region (3 regions)**: 6-8 hours
- **Full Production Setup**: 2-3 days

## Phase 1: Infrastructure Setup

### Step 1: Configure Cloud Credentials

**AWS:**
```bash
# Configure AWS CLI
aws configure
aws sts get-caller-identity  # Verify credentials

# Set environment variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

**GCP:**
```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Set environment variables
export GCP_PROJECT_ID=$(gcloud config get-value project)
export GCP_REGION=us-central1
```

**TODO for students**: Add Azure configuration instructions.

### Step 2: Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

Required variables:
```bash
# Cloud Provider
CLOUD_PROVIDER=aws  # or gcp, azure

# Regions
PRIMARY_REGION=us-east-1
SECONDARY_REGIONS=eu-west-1,ap-southeast-1
ALL_REGIONS=us-east-1,eu-west-1,ap-southeast-1

# Deployment
ENVIRONMENT=production  # or staging, development
DEPLOYMENT_NAME=ml-platform

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
GRAFANA_ADMIN_PASSWORD=<strong-password>

# TODO for students: Add more configuration as needed
```

### Step 3: Initialize Terraform

```bash
cd terraform/

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Review the plan
terraform show tfplan
```

**TODO for students**: Review Terraform plan carefully before applying.

### Step 4: Deploy Infrastructure

```bash
# Deploy to all regions
./scripts/setup.sh

# Or deploy step-by-step per region
for region in us-east-1 eu-west-1 ap-southeast-1; do
  echo "Deploying to $region..."
  terraform workspace select $region || terraform workspace new $region
  terraform apply -auto-approve -var="region=$region"
done
```

Expected resources created per region:
- VPC with public/private subnets
- EKS/GKE/AKS cluster
- S3/GCS buckets for model storage
- RDS/CloudSQL for metadata
- Load balancers
- Security groups/firewall rules

**Validation:**
```bash
# Verify infrastructure
terraform output

# Check cluster connectivity
export KUBECONFIG=~/.kube/config-us-east-1
kubectl cluster-info
kubectl get nodes
```

## Phase 2: Kubernetes Configuration

### Step 1: Configure kubectl Contexts

```bash
# AWS EKS
aws eks update-kubeconfig --region us-east-1 --name ml-cluster-us-east-1 --alias us-east-1
aws eks update-kubeconfig --region eu-west-1 --name ml-cluster-eu-west-1 --alias eu-west-1
aws eks update-kubeconfig --region ap-southeast-1 --name ml-cluster-ap-southeast-1 --alias ap-southeast-1

# Verify contexts
kubectl config get-contexts

# Test connectivity
for region in us-east-1 eu-west-1 ap-southeast-1; do
  echo "Testing $region..."
  kubectl --context=$region get nodes
done
```

**TODO for students**: Add GCP and Azure kubectl configuration.

### Step 2: Create Namespaces

```bash
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region create namespace ml-platform
  kubectl --context=$region create namespace monitoring
done
```

### Step 3: Deploy Kubernetes Resources

```bash
# Deploy base resources
kubectl apply -f kubernetes/base/ --context=us-east-1
kubectl apply -f kubernetes/base/ --context=eu-west-1
kubectl apply -f kubernetes/base/ --context=ap-southeast-1

# Verify deployments
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region get pods -n ml-platform
done
```

**TODO for students**: Customize kubernetes manifests for your setup.

## Phase 3: Application Deployment

### Step 1: Build and Push Docker Images

```bash
# Build model server image
docker build -t ml-platform/model-server:v1.0.0 -f docker/model-server/Dockerfile .

# Tag for each registry
docker tag ml-platform/model-server:v1.0.0 <ECR_REGISTRY>/model-server:v1.0.0

# Push to registries
docker push <ECR_REGISTRY>/model-server:v1.0.0

# Or use automated script
./scripts/build-and-push.sh v1.0.0
```

**TODO for students**: Set up CI/CD pipeline for automated builds.

### Step 2: Deploy Application

```bash
# Deploy using orchestrator
./scripts/deploy.sh

# Or use Python deployment script
python -m src.deployment.multi_region_orchestrator \
  --regions us-east-1,eu-west-1,ap-southeast-1 \
  --version v1.0.0 \
  --strategy rolling
```

Deployment strategies:
- **rolling**: Deploy to regions one at a time (safest)
- **blue-green**: Deploy new version alongside old, then switch
- **canary**: Gradually shift traffic to new version

**Monitoring deployment:**
```bash
# Watch deployment progress
kubectl --context=us-east-1 rollout status deployment/model-server -n ml-platform

# Check logs
kubectl --context=us-east-1 logs -f deployment/model-server -n ml-platform
```

### Step 3: Configure Model Replication

```bash
# Upload model to primary region
aws s3 cp models/model-v1.0.0.pth s3://ml-models-us-east-1/models/

# Trigger replication
python -m src.replication.model_replicator \
  --model-id model-v1.0.0 \
  --source-region us-east-1 \
  --target-regions eu-west-1,ap-southeast-1

# Verify replication
python -m src.replication.model_replicator \
  --model-id model-v1.0.0 \
  --check-status
```

**TODO for students**: Automate model replication in deployment pipeline.

## Phase 4: Monitoring Stack

### Step 1: Deploy Prometheus

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Deploy to each region
for region in us-east-1 eu-west-1 ap-southeast-1; do
  helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --kube-context=$region \
    --values kubernetes/monitoring/prometheus-values.yaml
done
```

### Step 2: Deploy Grafana

```bash
# Deploy Grafana
for region in us-east-1 eu-west-1 ap-southeast-1; do
  helm install grafana grafana/grafana \
    --namespace monitoring \
    --kube-context=$region \
    --set adminPassword=$GRAFANA_ADMIN_PASSWORD \
    --values kubernetes/monitoring/grafana-values.yaml
done

# Get Grafana URL
kubectl --context=us-east-1 get svc -n monitoring grafana
```

### Step 3: Import Dashboards

```bash
# Import multi-region dashboard
curl -X POST http://grafana-url/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana-dashboard.json
```

**TODO for students**: Create custom dashboards for your metrics.

## Phase 5: Traffic Management

### Step 1: Configure Global Load Balancer

**AWS Route53:**
```bash
# Create health checks
aws route53 create-health-check \
  --health-check-config \
    IPAddress=<US_EAST_LB_IP>,Port=443,Type=HTTPS,ResourcePath=/health

# Create weighted routing policy
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://route53-config.json
```

**TODO for students**: Add GCP Cloud Load Balancing configuration.

### Step 2: Configure DNS

```bash
# Update DNS records
python -m src.failover.dns_updater \
  --action update \
  --record-name ml-platform.example.com \
  --regions us-east-1,eu-west-1,ap-southeast-1
```

### Step 3: Test Traffic Routing

```bash
# Test from different regions
curl -I https://ml-platform.example.com/health

# Check routing
dig ml-platform.example.com

# Test latency from different locations
./scripts/test-latency.sh
```

## Phase 6: Validation & Testing

### Step 1: Run Health Checks

```bash
# Check all regional endpoints
./scripts/test.sh

# Or run manually
for region in us-east-1 eu-west-1 ap-southeast-1; do
  echo "Testing $region..."
  curl -f https://$region.ml-platform.example.com/health
done
```

### Step 2: Run Integration Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run integration tests
pytest tests/integration/ -v

# Run load tests
python tests/load/load_test.py --duration 300 --rps 100
```

### Step 3: Verify Replication

```bash
# Check replication status
python -m src.replication.model_replicator --verify-all

# Check data sync
python -m src.replication.data_sync --check-consistency
```

### Step 4: Test Failover

```bash
# Test manual failover
python -m src.failover.failover_controller \
  --from-region us-east-1 \
  --to-region eu-west-1 \
  --dry-run

# Monitor during failover
watch -n 1 'curl -s https://ml-platform.example.com/health | jq .'
```

**TODO for students**: Document expected test results and success criteria.

## Post-Deployment Tasks

### 1. Security Hardening

```bash
# Enable pod security policies
kubectl apply -f kubernetes/security/pod-security-policy.yaml

# Configure network policies
kubectl apply -f kubernetes/security/network-policies.yaml

# Rotate secrets
./scripts/rotate-secrets.sh
```

### 2. Backup Configuration

```bash
# Backup Terraform state
terraform state pull > terraform-backup-$(date +%Y%m%d).json

# Backup Kubernetes resources
kubectl get all --all-namespaces -o yaml > k8s-backup-$(date +%Y%m%d).yaml
```

### 3. Documentation

- [ ] Update architecture diagrams
- [ ] Document environment variables
- [ ] Create runbook for operations team
- [ ] Update monitoring dashboards

### 4. Training

- [ ] Train ops team on deployment procedures
- [ ] Conduct failover drills
- [ ] Review incident response procedures

## Rollback Procedures

### Application Rollback

```bash
# Rollback to previous version
kubectl --context=us-east-1 rollout undo deployment/model-server -n ml-platform

# Or use orchestrator
python -m src.deployment.multi_region_orchestrator \
  --rollback \
  --deployment-id <DEPLOYMENT_ID>
```

### Infrastructure Rollback

```bash
# Rollback Terraform changes
cd terraform/
terraform apply -auto-approve <previous-tfplan>

# Or destroy and recreate
terraform destroy -auto-approve
# Then redeploy from backup
```

**TODO for students**: Test rollback procedures in staging environment.

## Troubleshooting

### Common Issues

**Issue: Terraform fails to create resources**
```bash
# Check cloud provider quotas
aws service-quotas list-service-quotas --service-code ec2

# Check IAM permissions
aws iam get-user
```

**Issue: Kubernetes pods not starting**
```bash
# Check pod events
kubectl describe pod <POD_NAME> -n ml-platform

# Check logs
kubectl logs <POD_NAME> -n ml-platform

# Check resource limits
kubectl top nodes
```

**Issue: Health checks failing**
```bash
# Test endpoint directly
curl -v https://<REGION_LB>/health

# Check logs
kubectl logs -l app=model-server -n ml-platform --tail=100
```

**TODO for students**: See TROUBLESHOOTING.md for comprehensive debugging guide.

## Next Steps

- Review RUNBOOK.md for operational procedures
- Set up alerting rules in PagerDuty
- Schedule regular DR drills
- Optimize costs using recommendations from cost analyzer

## Support

For deployment issues:
1. Check TROUBLESHOOTING.md
2. Review logs in CloudWatch/Stackdriver
3. Contact platform team via Slack #ml-platform
4. Create ticket in Jira

**TODO for students**: Update support contacts and escalation procedures.
