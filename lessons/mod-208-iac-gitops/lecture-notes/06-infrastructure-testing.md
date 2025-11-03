# Lecture 6: Infrastructure Testing

## Learning Objectives

By the end of this lecture, you will be able to:

- Design infrastructure testing strategies following testing pyramid with unit tests (syntax validation), integration tests (actual deployment), and contract tests (API compatibility)
- Implement Terratest framework for automated Terraform testing deploying real infrastructure, running validation checks, and cleaning up resources in isolated environments
- Configure Kitchen-Terraform for test-driven infrastructure development using Test Kitchen's workflow for creating, converging, verifying, and destroying infrastructure
- Architect policy testing using Open Policy Agent (OPA) or Sentinel validating infrastructure configurations against security, compliance, and best practice policies before deployment
- Design contract testing for infrastructure APIs ensuring module interfaces remain stable, preventing breaking changes, and validating module outputs
- Build CI/CD pipelines for infrastructure with automated testing, static analysis (tflint, checkov), security scanning, and cost estimation before production deployment
- Implement chaos testing for infrastructure using failure injection validating resilience, testing disaster recovery procedures, and ensuring proper fault handling
- Architect infrastructure test environments with ephemeral test accounts, isolated VPCs, and automated cleanup preventing test pollution and managing test costs

## Table of Contents
1. [Why Test Infrastructure?](#why-test-infrastructure)
2. [Terratest Framework](#terratest-framework)
3. [Kitchen-Terraform](#kitchen-terraform)
4. [Policy Testing](#policy-testing)
5. [Contract and Integration Testing](#contract-and-integration-testing)
6. [CI/CD for Infrastructure](#cicd-for-infrastructure)

## Why Test Infrastructure?

Infrastructure code is code. It should be tested like application code to prevent:
- Configuration drift
- Breaking changes
- Security vulnerabilities
- Cost overruns
- Deployment failures

### Testing Pyramid for Infrastructure

```
                    ┌───────────────┐
                    │   Manual      │
                    │   Testing     │
                    └───────────────┘
                  ┌───────────────────┐
                  │  End-to-End       │
                  │  Integration      │
                  └───────────────────┘
              ┌─────────────────────────┐
              │  Integration Tests      │
              │  (Deploy + Validate)    │
              └─────────────────────────┘
          ┌───────────────────────────────┐
          │  Contract Tests                │
          │  (API/Interface Validation)    │
          └───────────────────────────────┘
      ┌───────────────────────────────────────┐
      │  Unit Tests                            │
      │  (Static Analysis, Linting, Policies)  │
      └───────────────────────────────────────┘
```

### Types of Infrastructure Tests

1. **Unit Tests**: Validate configuration syntax and policies
2. **Contract Tests**: Verify resource interfaces and APIs
3. **Integration Tests**: Deploy and validate actual infrastructure
4. **End-to-End Tests**: Test complete workflows
5. **Performance Tests**: Validate scalability and performance
6. **Security Tests**: Check for vulnerabilities and compliance

## Terratest Framework

Terratest is a Go library for writing automated tests for infrastructure code.

### Setup

```go
// go.mod
module github.com/company/ml-infrastructure-tests

go 1.21

require (
    github.com/gruntwork-io/terratest v0.46.0
    github.com/stretchr/testify v1.8.4
)
```

### Basic Terratest Example

```go
// test/eks_cluster_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
)

func TestEKSCluster(t *testing.T) {
    t.Parallel()

    // Construct Terraform options
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        // Path to Terraform code
        TerraformDir: "../modules/eks-cluster",

        // Variables to pass
        Vars: map[string]interface{}{
            "cluster_name":    "test-ml-cluster",
            "region":          "us-west-2",
            "instance_types":  []string{"t3.medium"},
            "desired_size":    2,
        },

        // Environment variables
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-west-2",
        },
    })

    // Clean up resources with "terraform destroy"
    defer terraform.Destroy(t, terraformOptions)

    // Run "terraform init" and "terraform apply"
    terraform.InitAndApply(t, terraformOptions)

    // Run validations
    clusterName := terraform.Output(t, terraformOptions, "cluster_name")
    assert.Equal(t, "test-ml-cluster", clusterName)

    // Validate cluster exists in AWS
    cluster := aws.GetEksCluster(t, "us-west-2", clusterName)
    assert.Equal(t, "ACTIVE", *cluster.Status)

    // Validate node groups
    nodeGroups := aws.GetEksNodeGroups(t, "us-west-2", clusterName)
    assert.Greater(t, len(nodeGroups), 0)
}
```

### Testing S3 Buckets

```go
// test/s3_buckets_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
)

func TestMLDataBuckets(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../modules/s3-ml-buckets",
        Vars: map[string]interface{}{
            "project_name": "test-ml-project",
            "environment":  "test",
            "bucket_configs": map[string]interface{}{
                "raw-data": map[string]interface{}{
                    "versioning": true,
                    "encryption": "AES256",
                },
                "models": map[string]interface{}{
                    "versioning": true,
                    "encryption": "aws:kms",
                },
            },
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Get bucket names from outputs
    rawDataBucket := terraform.Output(t, terraformOptions, "raw_data_bucket_name")
    modelsBucket := terraform.Output(t, terraformOptions, "models_bucket_name")

    // Validate bucket exists
    aws.AssertS3BucketExists(t, "us-west-2", rawDataBucket)
    aws.AssertS3BucketExists(t, "us-west-2", modelsBucket)

    // Validate versioning is enabled
    actualVersioning := aws.GetS3BucketVersioning(t, "us-west-2", rawDataBucket)
    assert.Equal(t, "Enabled", actualVersioning)

    // Validate encryption
    actualEncryption := aws.GetS3BucketEncryption(t, "us-west-2", modelsBucket)
    assert.NotNil(t, actualEncryption)
    assert.Equal(t, "aws:kms", actualEncryption.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm)

    // Validate bucket policy
    policy := aws.GetS3BucketPolicy(t, "us-west-2", rawDataBucket)
    assert.Contains(t, policy, "s3:GetObject")
}
```

### Testing Kubernetes Resources

```go
// test/kubernetes_resources_test.go
package test

import (
    "testing"
    "path/filepath"
    "github.com/gruntwork-io/terratest/modules/k8s"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func TestMLTrainingDeployment(t *testing.T) {
    t.Parallel()

    // Setup Terraform
    terraformOptions := &terraform.Options{
        TerraformDir: "../modules/k8s-ml-training",
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Get kubeconfig
    kubeconfig := terraform.Output(t, terraformOptions, "kubeconfig_path")

    // Setup Kubernetes options
    kubectlOptions := k8s.NewKubectlOptions("", kubeconfig, "ml-training")

    // Wait for deployment to be ready
    k8s.WaitUntilDeploymentAvailable(t, kubectlOptions, "ml-trainer", 10, 30)

    // Get deployment
    deployment := k8s.GetDeployment(t, kubectlOptions, "ml-trainer")

    // Validate replicas
    assert.Equal(t, int32(3), *deployment.Spec.Replicas)

    // Validate container image
    containers := deployment.Spec.Template.Spec.Containers
    assert.Equal(t, "ml-training:v1.0.0", containers[0].Image)

    // Validate GPU resources
    gpuLimit := containers[0].Resources.Limits["nvidia.com/gpu"]
    assert.Equal(t, "1", gpuLimit.String())

    // Validate pod is running
    pods := k8s.ListPods(t, kubectlOptions, metav1.ListOptions{
        LabelSelector: "app=ml-trainer",
    })
    assert.Greater(t, len(pods), 0)

    for _, pod := range pods {
        assert.Equal(t, "Running", string(pod.Status.Phase))
    }
}
```

### Advanced Testing Patterns

```go
// test/ml_infrastructure_test.go
package test

import (
    "fmt"
    "testing"
    "time"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/retry"
    "github.com/gruntwork-io/terratest/modules/http-helper"
    "github.com/stretchr/testify/assert"
)

func TestCompleteMLInfrastructure(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../infrastructure/complete",
        Vars: map[string]interface{}{
            "environment": "test",
            "region":      "us-west-2",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    // Test 1: Validate VPC
    t.Run("VPC", func(t *testing.T) {
        vpcID := terraform.Output(t, terraformOptions, "vpc_id")
        assert.NotEmpty(t, vpcID)
    })

    // Test 2: Validate EKS cluster
    t.Run("EKS Cluster", func(t *testing.T) {
        clusterEndpoint := terraform.Output(t, terraformOptions, "cluster_endpoint")
        assert.NotEmpty(t, clusterEndpoint)

        // Wait for cluster to be fully ready
        maxRetries := 30
        sleepBetweenRetries := 10 * time.Second

        retry.DoWithRetry(t, "Wait for cluster", maxRetries, sleepBetweenRetries, func() (string, error) {
            // Check cluster health
            statusCode, err := http_helper.HttpGetE(t, fmt.Sprintf("%s/healthz", clusterEndpoint))
            if err != nil || statusCode != 200 {
                return "", fmt.Errorf("cluster not ready")
            }
            return "Cluster ready", nil
        })
    })

    // Test 3: Validate S3 buckets
    t.Run("S3 Buckets", func(t *testing.T) {
        rawDataBucket := terraform.Output(t, terraformOptions, "raw_data_bucket")
        assert.NotEmpty(t, rawDataBucket)

        modelsBucket := terraform.Output(t, terraformOptions, "models_bucket")
        assert.NotEmpty(t, modelsBucket)
    })

    // Test 4: Validate monitoring
    t.Run("Monitoring", func(t *testing.T) {
        prometheusURL := terraform.Output(t, terraformOptions, "prometheus_url")

        // Check Prometheus is accessible
        http_helper.HttpGetWithRetry(t, prometheusURL, nil, 200, "prometheus", 30, 10*time.Second)
    })

    // Test 5: Validate ML services
    t.Run("ML Services", func(t *testing.T) {
        mlflowURL := terraform.Output(t, terraformOptions, "mlflow_url")

        // Check MLflow is accessible
        http_helper.HttpGetWithRetry(t, mlflowURL, nil, 200, "MLflow", 30, 10*time.Second)
    })
}
```

## Kitchen-Terraform

Kitchen-Terraform brings Test Kitchen to Terraform, enabling infrastructure testing workflows.

### Setup

```ruby
# Gemfile
source 'https://rubygems.org'

gem 'kitchen-terraform', '~> 7.0'
gem 'test-kitchen', '~> 3.5'
```

### Kitchen Configuration

```yaml
# .kitchen.yml
---
driver:
  name: terraform
  root_module_directory: test/fixtures/complete

provisioner:
  name: terraform

platforms:
  - name: terraform

verifier:
  name: terraform
  systems:
    - name: ml_infrastructure
      backend: aws
      controls:
        - eks_cluster
        - s3_buckets
        - networking

suites:
  - name: default
    driver:
      variables:
        cluster_name: test-ml-cluster
        environment: test
    verifier:
      systems:
        - name: ml_infrastructure
          backend: aws
          profile_locations:
            - test/integration/default
```

### InSpec Tests

```ruby
# test/integration/default/controls/eks_cluster.rb
control 'eks_cluster' do
  impact 1.0
  title 'EKS Cluster'
  desc 'Validate EKS cluster configuration'

  cluster_name = input('cluster_name')

  # Check cluster exists
  describe aws_eks_cluster(cluster_name) do
    it { should exist }
    its('status') { should eq 'ACTIVE' }
    its('version') { should cmp >= '1.27' }
  end

  # Check node groups
  describe aws_eks_node_groups(cluster_name) do
    its('node_group_names') { should include 'gpu-nodes' }
    its('node_group_names') { should include 'cpu-nodes' }
  end

  # Check GPU node group
  describe aws_eks_node_group(cluster_name: cluster_name, node_group_name: 'gpu-nodes') do
    it { should exist }
    its('status') { should eq 'ACTIVE' }
    its('instance_types') { should include 'p3.2xlarge' }
  end
end
```

```ruby
# test/integration/default/controls/s3_buckets.rb
control 's3_buckets' do
  impact 1.0
  title 'S3 Buckets'
  desc 'Validate S3 bucket configuration'

  bucket_prefix = input('bucket_prefix')

  ['raw-data', 'processed-data', 'models'].each do |bucket_type|
    bucket_name = "#{bucket_prefix}-#{bucket_type}"

    describe aws_s3_bucket(bucket_name) do
      it { should exist }
      it { should have_default_encryption_enabled }
      it { should have_versioning_enabled }
      it { should_not be_public }
    end

    # Check encryption
    describe aws_s3_bucket(bucket_name) do
      its('encryption_rules.first.apply_server_side_encryption_by_default.sse_algorithm') do
        should be_in ['AES256', 'aws:kms']
      end
    end

    # Check lifecycle policies
    describe aws_s3_bucket(bucket_name) do
      its('lifecycle_rules') { should_not be_empty }
    end
  end
end
```

## Policy Testing

### Open Policy Agent (OPA)

```rego
# policies/kubernetes/deny_privileged.rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Privileged containers are not allowed: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext.runAsNonRoot
    msg := "Pods must run as non-root user"
}
```

```rego
# policies/kubernetes/require_resources.rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.requests.memory
    msg := sprintf("Container %v must specify memory request", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.requests.cpu
    msg := sprintf("Container %v must specify CPU request", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container %v must specify memory limit", [container.name])
}
```

### Testing OPA Policies

```rego
# policies/kubernetes/deny_privileged_test.rego
package kubernetes.admission

test_privileged_denied {
    deny[msg] with input as {
        "request": {
            "kind": {"kind": "Pod"},
            "object": {
                "spec": {
                    "containers": [{
                        "name": "test",
                        "securityContext": {"privileged": true}
                    }]
                }
            }
        }
    }
}

test_non_privileged_allowed {
    count(deny) == 0 with input as {
        "request": {
            "kind": {"kind": "Pod"},
            "object": {
                "spec": {
                    "securityContext": {"runAsNonRoot": true},
                    "containers": [{
                        "name": "test",
                        "securityContext": {"privileged": false},
                        "resources": {
                            "requests": {"cpu": "100m", "memory": "128Mi"},
                            "limits": {"cpu": "200m", "memory": "256Mi"}
                        }
                    }]
                }
            }
        }
    }
}
```

```bash
# Run OPA tests
opa test policies/ -v

# Output:
# policies/kubernetes/deny_privileged_test.rego:
# data.kubernetes.admission.test_privileged_denied: PASS (0.5ms)
# data.kubernetes.admission.test_non_privileged_allowed: PASS (0.3ms)
# ------------------------
# PASS: 2/2
```

### Conftest for Policy Testing

```bash
# Install conftest
brew install conftest

# Test Kubernetes manifests
conftest test manifests/deployment.yaml -p policies/

# Test Terraform plans
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
conftest test tfplan.json -p policies/terraform/
```

```rego
# policies/terraform/s3_encryption.rego
package main

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not resource.change.after.server_side_encryption_configuration
    msg := sprintf("S3 bucket %v must have encryption enabled", [resource.address])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.acl == "public-read"
    msg := sprintf("S3 bucket %v must not be public", [resource.address])
}
```

## Contract and Integration Testing

### API Contract Testing

```python
# tests/test_ml_api_contract.py
import pytest
import requests
from jsonschema import validate, ValidationError

# Expected API response schema
PREDICTION_SCHEMA = {
    "type": "object",
    "properties": {
        "prediction": {"type": "number"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "model_version": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"}
    },
    "required": ["prediction", "confidence", "model_version"]
}

class TestMLAPIContract:
    """Test ML model API contract"""

    def test_prediction_endpoint_exists(self, ml_api_url):
        """Test prediction endpoint is accessible"""
        response = requests.get(f"{ml_api_url}/health")
        assert response.status_code == 200

    def test_prediction_response_schema(self, ml_api_url):
        """Test prediction response matches schema"""
        payload = {
            "features": [1.0, 2.0, 3.0, 4.0]
        }

        response = requests.post(
            f"{ml_api_url}/predict",
            json=payload
        )

        assert response.status_code == 200

        # Validate response schema
        try:
            validate(instance=response.json(), schema=PREDICTION_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Response schema validation failed: {e}")

    def test_batch_prediction(self, ml_api_url):
        """Test batch prediction endpoint"""
        payload = {
            "instances": [
                {"features": [1.0, 2.0, 3.0, 4.0]},
                {"features": [2.0, 3.0, 4.0, 5.0]}
            ]
        }

        response = requests.post(
            f"{ml_api_url}/predict/batch",
            json=payload
        )

        assert response.status_code == 200
        predictions = response.json()["predictions"]
        assert len(predictions) == 2

    def test_error_handling(self, ml_api_url):
        """Test API error handling"""
        # Invalid input
        response = requests.post(
            f"{ml_api_url}/predict",
            json={"invalid": "data"}
        )

        assert response.status_code == 400
        assert "error" in response.json()
```

### Integration Testing

```python
# tests/test_ml_pipeline_integration.py
import pytest
import boto3
from kubernetes import client, config

class TestMLPipelineIntegration:
    """Integration tests for ML pipeline"""

    @pytest.fixture(scope="class")
    def k8s_client(self):
        config.load_kube_config()
        return client.BatchV1Api()

    @pytest.fixture(scope="class")
    def s3_client(self):
        return boto3.client('s3')

    def test_training_job_completes(self, k8s_client):
        """Test training job runs to completion"""
        # Create training job
        job_manifest = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {"name": "test-training-job"},
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "trainer",
                            "image": "ml-training:test",
                            "command": ["python", "train.py"],
                            "args": ["--epochs=1", "--batch-size=32"]
                        }],
                        "restartPolicy": "Never"
                    }
                }
            }
        }

        # Submit job
        k8s_client.create_namespaced_job(
            namespace="ml-training",
            body=job_manifest
        )

        # Wait for completion (simplified)
        import time
        for _ in range(60):
            job = k8s_client.read_namespaced_job(
                name="test-training-job",
                namespace="ml-training"
            )

            if job.status.succeeded == 1:
                break

            time.sleep(10)
        else:
            pytest.fail("Training job did not complete")

    def test_model_artifacts_saved(self, s3_client):
        """Test model artifacts are saved to S3"""
        bucket = "ml-models-test"
        prefix = "test-model/"

        # Check artifacts exist
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix
        )

        assert "Contents" in response
        artifacts = [obj["Key"] for obj in response["Contents"]]

        # Verify required artifacts
        assert any("model.pth" in a for a in artifacts)
        assert any("metadata.json" in a for a in artifacts)

    def test_end_to_end_pipeline(self, k8s_client, s3_client):
        """Test complete ML pipeline"""
        # 1. Upload training data
        s3_client.put_object(
            Bucket="ml-data-test",
            Key="training/data.csv",
            Body=b"feature1,feature2,label\n1.0,2.0,0\n"
        )

        # 2. Trigger training job
        # ... (create and wait for job)

        # 3. Verify model registration
        # ... (check MLflow)

        # 4. Deploy model
        # ... (create deployment)

        # 5. Test inference
        # ... (send prediction request)

        assert True  # Placeholder
```

## CI/CD for Infrastructure

### GitHub Actions Workflow

```yaml
# .github/workflows/infrastructure-ci.yaml
name: Infrastructure CI

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'modules/**'
  push:
    branches: [main]

env:
  TF_VERSION: 1.6.0
  GO_VERSION: 1.21

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform fmt
        run: terraform fmt -check -recursive

      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
        with:
          tflint_version: latest

      - name: Run TFLint
        run: tflint --recursive

  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform

  policy-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup OPA
        uses: open-policy-agent/setup-opa@v2

      - name: Run OPA tests
        run: opa test policies/ -v

      - name: Test with Conftest
        run: |
          terraform plan -out=tfplan.binary
          terraform show -json tfplan.binary > tfplan.json
          conftest test tfplan.json -p policies/terraform/

  terratest:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: ${{ env.GO_VERSION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_TEST_ROLE }}
          aws-region: us-west-2

      - name: Run Terratest
        run: |
          cd test
          go test -v -timeout 30m -parallel 4

      - name: Cleanup
        if: always()
        run: |
          cd test
          go test -v -cleanup

  deploy:
    needs: [lint, validate, security-scan, policy-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan -out=tfplan

      - name: Terraform Apply
        run: terraform apply tfplan
```

## Summary

Infrastructure testing provides:
- **Confidence**: Deploy with confidence
- **Quality**: Catch issues early
- **Compliance**: Enforce policies
- **Documentation**: Tests as documentation
- **Repeatability**: Consistent validation

**Testing Strategy:**
1. Unit tests: Static analysis and linting
2. Policy tests: OPA/Conftest validation
3. Integration tests: Terratest/Kitchen-Terraform
4. Contract tests: API validation
5. End-to-end tests: Complete workflows

## Next Steps

- Continue to [Lecture 7: Policy as Code](07-policy-as-code.md)
- Write Terratest tests for your modules
- Implement OPA policies
- Set up CI/CD for infrastructure

## Additional Resources

- [Terratest Documentation](https://terratest.gruntwork.io/)
- [Kitchen-Terraform](https://github.com/newcontext-oss/kitchen-terraform)
- [OPA Testing](https://www.openpolicyagent.org/docs/latest/policy-testing/)
- [Conftest](https://www.conftest.dev/)
