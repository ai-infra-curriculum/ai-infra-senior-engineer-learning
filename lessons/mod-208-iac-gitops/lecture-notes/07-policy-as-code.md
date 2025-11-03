# Lecture 7: Policy as Code

## Learning Objectives

By the end of this lecture, you will be able to:

- Design policy-as-code systems using Open Policy Agent (OPA) or HashiCorp Sentinel enforcing security, compliance, and best practice policies through automated validation
- Implement OPA policies written in Rego language validating Kubernetes manifests, Terraform plans, and API requests against organizational requirements before deployment
- Configure Sentinel policies for Terraform Cloud/Enterprise with policy sets, enforcement levels (advisory, soft-mandatory, hard-mandatory), and cost controls
- Architect CI/CD policy enforcement pipelines with automated policy validation, violation reporting, and deployment blocking for non-compliant changes
- Design compliance automation frameworks mapping policies to regulatory requirements (SOC2, PCI-DSS, HIPAA, GDPR) with audit trails and compliance reporting
- Implement ML infrastructure security policies including GPU quota enforcement, data access controls, model registry permissions, and resource tagging requirements
- Build policy testing workflows with unit tests, integration tests, and regression tests ensuring policy logic correctness before production deployment
- Architect policy governance processes with policy versioning, change approval, impact analysis, and gradual rollout minimizing disruption to development teams

## Table of Contents
1. [Introduction to Policy as Code](#introduction-to-policy-as-code)
2. [Open Policy Agent (OPA)](#open-policy-agent-opa)
3. [HashiCorp Sentinel](#hashicorp-sentinel)
4. [CI/CD Policy Enforcement](#cicd-policy-enforcement)
5. [Compliance Automation](#compliance-automation)
6. [ML Infrastructure Security Policies](#ml-infrastructure-security-policies)

## Introduction to Policy as Code

Policy as Code enables defining, versioning, and enforcing organizational policies through code. It brings software development best practices to policy management.

### Why Policy as Code?

**Traditional Policy Management:**
- Manual reviews
- Inconsistent enforcement
- Lack of auditing
- Slow feedback cycles
- Human error

**Policy as Code Benefits:**
- Automated enforcement
- Consistent application
- Version control
- Fast feedback
- Audit trail
- Testable policies

### Policy as Code Workflow

```
┌───────────────────────────────────────────────────────────────┐
│              Policy as Code Workflow                           │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Define Policies (Rego, Sentinel, etc.)                    │
│     └─> Version control in Git                                │
│     └─> Peer review via pull requests                         │
│                                                                │
│  2. Test Policies                                              │
│     └─> Unit tests for policy logic                           │
│     └─> Integration tests with sample data                    │
│                                                                │
│  3. Deploy Policies                                            │
│     └─> Push to policy server (OPA, Sentinel)                 │
│     └─> Configure admission controllers                       │
│                                                                │
│  4. Enforce Policies                                           │
│     └─> Evaluate on every deployment                          │
│     └─> Block or warn on violations                           │
│                                                                │
│  5. Monitor & Audit                                            │
│     └─> Log all policy decisions                              │
│     └─> Alert on violations                                   │
│     └─> Compliance reporting                                  │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## Open Policy Agent (OPA)

OPA is a general-purpose policy engine that enables unified policy enforcement across the stack.

### OPA Architecture

```
Application/Service
        │
        │ (authorization query)
        ▼
   ┌─────────┐
   │   OPA   │
   │  Engine │
   └────┬────┘
        │
        ├─> Policy (Rego)
        ├─> Data (JSON/YAML)
        └─> Decision (allow/deny)
```

### Rego Language Basics

```rego
# Basic rule
allow {
    input.user == "admin"
}

# Rule with conditions
allow {
    input.user == current_user
    input.action == "read"
}

# Iteration
deny[msg] {
    container := input.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container %v must run as non-root", [container.name])
}

# Functions
is_admin {
    input.user.role == "admin"
}

# Comprehensions
allowed_users := {user | user := data.users[_]; user.active == true}
```

### Kubernetes Admission Control

**OPA Gatekeeper Installation:**
```bash
# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Verify installation
kubectl get pods -n gatekeeper-system
```

**Constraint Template:**
```yaml
# constraint-template-required-labels.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string

  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

**Constraint:**
```yaml
# constraint-ml-required-labels.yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ml-required-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
    namespaces:
      - ml-training
      - ml-serving

  parameters:
    labels:
      - app
      - environment
      - team
      - cost-center
```

### ML-Specific Policies

**GPU Resource Limits:**
```rego
# policies/gpu_limits.rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]

    # Check if GPU is requested
    gpu_request := container.resources.requests["nvidia.com/gpu"]
    gpu_request

    # GPU must equal limit
    gpu_limit := container.resources.limits["nvidia.com/gpu"]
    gpu_request != gpu_limit

    msg := sprintf("GPU request must equal limit for container %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]

    # Check GPU count
    gpu_count := to_number(container.resources.requests["nvidia.com/gpu"])
    gpu_count > 8

    msg := sprintf("Container %v requests %v GPUs, max is 8", [container.name, gpu_count])
}
```

**Training Job Validation:**
```rego
# policies/training_jobs.rego
package kubernetes.admission

import data.kubernetes.namespaces

# Training jobs must have specific labels
deny[msg] {
    input.request.kind.kind == "Job"
    input.request.namespace == "ml-training"

    required_labels := {"experiment-id", "model-type", "dataset"}
    provided_labels := {label | input.request.object.metadata.labels[label]}
    missing := required_labels - provided_labels

    count(missing) > 0
    msg := sprintf("Training job missing labels: %v", [missing])
}

# Training jobs must specify resource limits
deny[msg] {
    input.request.kind.kind == "Job"
    input.request.namespace == "ml-training"
    container := input.request.object.spec.template.spec.containers[_]

    not container.resources.limits.memory
    not container.resources.limits.cpu

    msg := sprintf("Training container %v must specify resource limits", [container.name])
}

# Training jobs must use specific service account
deny[msg] {
    input.request.kind.kind == "Job"
    input.request.namespace == "ml-training"

    sa := input.request.object.spec.template.spec.serviceAccountName
    sa != "ml-training-sa"

    msg := "Training jobs must use ml-training-sa service account"
}

# Training jobs must have retry limit
deny[msg] {
    input.request.kind.kind == "Job"
    input.request.namespace == "ml-training"

    not input.request.object.spec.backoffLimit

    msg := "Training jobs must specify backoffLimit"
}
```

**Model Serving Policies:**
```rego
# policies/model_serving.rego
package kubernetes.admission

# Model serving must have health checks
deny[msg] {
    input.request.kind.kind == "Deployment"
    input.request.namespace == "ml-serving"
    container := input.request.object.spec.template.spec.containers[_]

    not container.livenessProbe
    not container.readinessProbe

    msg := sprintf("Serving container %v must have health checks", [container.name])
}

# Model serving must have HPA
deny[msg] {
    input.request.kind.kind == "Deployment"
    input.request.namespace == "ml-serving"

    labels := input.request.object.metadata.labels
    not labels["autoscaling"]

    msg := "Model serving deployments must have autoscaling enabled"
}

# Model serving must specify model version
deny[msg] {
    input.request.kind.kind == "Deployment"
    input.request.namespace == "ml-serving"
    container := input.request.object.spec.template.spec.containers[_]

    env_vars := {e.name | e := container.env[_]}
    not env_vars["MODEL_VERSION"]

    msg := sprintf("Container %v must specify MODEL_VERSION", [container.name])
}

# Enforce resource requests for inference
deny[msg] {
    input.request.kind.kind == "Deployment"
    input.request.namespace == "ml-serving"
    container := input.request.object.spec.template.spec.containers[_]

    not container.resources.requests.cpu
    not container.resources.requests.memory

    msg := sprintf("Serving container %v must specify resource requests", [container.name])
}
```

### Data Validation

**MLflow Experiment Policies:**
```rego
# policies/mlflow_experiments.rego
package mlflow

# Experiments must have required tags
deny[msg] {
    input.request.type == "create_experiment"

    required_tags := {"team", "project", "cost-center"}
    provided_tags := {tag | input.request.tags[tag]}
    missing := required_tags - provided_tags

    count(missing) > 0
    msg := sprintf("Experiment missing tags: %v", [missing])
}

# Experiments must follow naming convention
deny[msg] {
    input.request.type == "create_experiment"
    not regex.match(`^[a-z0-9-]+/[a-z0-9-]+$`, input.request.name)

    msg := "Experiment name must match pattern: team/project"
}

# Model registration must include metrics
deny[msg] {
    input.request.type == "register_model"
    not input.request.metrics.accuracy

    msg := "Model registration must include accuracy metric"
}
```

## HashiCorp Sentinel

Sentinel is a policy-as-code framework integrated with HashiCorp enterprise products.

### Sentinel Language

```python
# sentinel.hcl - Sentinel policies for Terraform

import "tfplan/v2" as tfplan

# Required tags policy
required_tags = ["Environment", "Owner", "Project", "CostCenter"]

# Main rule
main = rule {
    all_resources_have_required_tags
}

# Check all resources
all_resources_have_required_tags = rule {
    all tfplan.resource_changes as _, rc {
        rc.mode is "managed" and
        rc.change.actions is not ["delete"] and
        has_required_tags(rc)
    }
}

# Function to check tags
has_required_tags = func(resource) {
    if "tags" not in resource.change.after {
        return false
    }

    for required_tags as tag {
        if tag not in keys(resource.change.after.tags) {
            print("Missing tag:", tag, "in", resource.address)
            return false
        }
    }

    return true
}
```

### ML Infrastructure Policies

**S3 Bucket Security:**
```python
# policies/s3-security.sentinel
import "tfplan/v2" as tfplan

# Get all S3 buckets
s3_buckets = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_s3_bucket" and
    rc.mode is "managed" and
    rc.change.actions is not ["delete"]
}

# Encryption required
require_encryption = rule {
    all s3_buckets as _, bucket {
        bucket.change.after.server_side_encryption_configuration is not null
    }
}

# Versioning required for model buckets
require_versioning = rule {
    all s3_buckets as _, bucket {
        bucket.change.after.bucket matches ".*-models$" implies
            bucket.change.after.versioning[0].enabled is true
    }
}

# Block public access
block_public_access = rule {
    all s3_buckets as _, bucket {
        bucket.change.after.acl is not "public-read" and
        bucket.change.after.acl is not "public-read-write"
    }
}

# Lifecycle policies for cost optimization
require_lifecycle = rule {
    all s3_buckets as _, bucket {
        bucket.change.after.bucket matches ".*-raw-data$" implies
            length(bucket.change.after.lifecycle_rule else []) > 0
    }
}

main = rule {
    require_encryption and
    require_versioning and
    block_public_access and
    require_lifecycle
}
```

**EKS Cluster Policies:**
```python
# policies/eks-security.sentinel
import "tfplan/v2" as tfplan

# Get all EKS clusters
eks_clusters = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_eks_cluster" and
    rc.mode is "managed"
}

# Cluster logging required
require_logging = rule {
    all eks_clusters as _, cluster {
        length(cluster.change.after.enabled_cluster_log_types else []) >= 3
    }
}

# Encryption required
require_encryption = rule {
    all eks_clusters as _, cluster {
        cluster.change.after.encryption_config is not null and
        length(cluster.change.after.encryption_config) > 0
    }
}

# Private endpoint required for production
require_private_endpoint = rule when tfplan.variables.environment is "production" {
    all eks_clusters as _, cluster {
        cluster.change.after.vpc_config[0].endpoint_private_access is true
    }
}

# Minimum Kubernetes version
require_minimum_version = rule {
    all eks_clusters as _, cluster {
        float(cluster.change.after.version) >= 1.27
    }
}

main = rule {
    require_logging and
    require_encryption and
    require_private_endpoint and
    require_minimum_version
}
```

**Cost Control Policies:**
```python
# policies/cost-control.sentinel
import "tfplan/v2" as tfplan
import "decimal"

# Maximum instance counts
max_instances = {
    "dev": 5,
    "staging": 10,
    "prod": 50,
}

# Get all EC2 instances
ec2_instances = filter tfplan.resource_changes as _, rc {
    rc.type is "aws_instance" and
    rc.mode is "managed"
}

# Enforce instance limits
enforce_instance_limits = rule {
    length(ec2_instances) <= max_instances[tfplan.variables.environment]
}

# Restrict expensive instance types
allowed_instance_types = [
    "t3.micro", "t3.small", "t3.medium", "t3.large",
    "c5.xlarge", "c5.2xlarge",
    "p3.2xlarge",  # GPU for ML
]

restrict_instance_types = rule when tfplan.variables.environment is not "prod" {
    all ec2_instances as _, instance {
        instance.change.after.instance_type in allowed_instance_types
    }
}

# Estimate monthly cost
estimate_monthly_cost = func() {
    costs = {
        "t3.micro": 7.59,
        "t3.small": 15.18,
        "t3.medium": 30.37,
        "c5.xlarge": 122.93,
        "p3.2xlarge": 2216.16,
    }

    total = decimal.new(0)

    for ec2_instances as _, instance {
        instance_type = instance.change.after.instance_type
        if instance_type in keys(costs) {
            total = decimal.add(total, decimal.new(costs[instance_type]))
        }
    }

    return decimal.to_float(total)
}

# Cost alert (advisory)
cost_threshold = 5000.0

cost_alert = rule when estimate_monthly_cost() > cost_threshold {
    print("Warning: Estimated monthly cost $", estimate_monthly_cost(), "exceeds threshold $", cost_threshold)
    true  # Advisory only
}

main = rule {
    enforce_instance_limits and
    restrict_instance_types and
    cost_alert
}
```

## CI/CD Policy Enforcement

### GitHub Actions Integration

```yaml
# .github/workflows/policy-check.yaml
name: Policy Check

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'manifests/**'

jobs:
  opa-policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup OPA
        uses: open-policy-agent/setup-opa@v2

      - name: Test OPA policies
        run: |
          opa test policies/ -v

      - name: Validate Kubernetes manifests
        run: |
          find manifests/ -name '*.yaml' | while read manifest; do
            echo "Checking $manifest"
            opa eval -i "$manifest" -d policies/ "data.kubernetes.admission.deny" --fail
          done

  conftest-terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Terraform Plan
        run: |
          cd terraform/
          terraform init
          terraform plan -out=tfplan.binary
          terraform show -json tfplan.binary > tfplan.json

      - name: Install Conftest
        run: |
          wget https://github.com/open-policy-agent/conftest/releases/latest/download/conftest_Linux_x86_64.tar.gz
          tar xzf conftest_Linux_x86_64.tar.gz
          sudo mv conftest /usr/local/bin/

      - name: Run Conftest
        run: |
          conftest test terraform/tfplan.json -p policies/terraform/

  sentinel-check:
    runs-on: ubuntu-latest
    if: github.repository == 'company/ml-infrastructure-enterprise'
    steps:
      - uses: actions/checkout@v3

      - name: Setup Sentinel
        run: |
          wget https://releases.hashicorp.com/sentinel/0.22.0/sentinel_0.22.0_linux_amd64.zip
          unzip sentinel_0.22.0_linux_amd64.zip
          sudo mv sentinel /usr/local/bin/

      - name: Run Sentinel tests
        run: |
          sentinel test policies/

      - name: Sentinel apply
        run: |
          sentinel apply -config=sentinel.hcl policies/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint

  - repo: local
    hooks:
      - id: opa-test
        name: OPA Policy Tests
        entry: opa test policies/
        language: system
        pass_filenames: false

      - id: conftest-kubernetes
        name: Conftest Kubernetes
        entry: bash -c 'find manifests/ -name "*.yaml" -exec conftest test {} -p policies/ \;'
        language: system
        files: \.yaml$

      - id: sentinel-test
        name: Sentinel Tests
        entry: sentinel test policies/
        language: system
        pass_filenames: false
```

## Compliance Automation

### Compliance Frameworks

**CIS Kubernetes Benchmark:**
```rego
# policies/compliance/cis-kubernetes.rego
package compliance.cis

# 5.2.2 - Minimize the admission of containers with capabilities
deny_capabilities[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    caps := container.securityContext.capabilities.add

    forbidden := {"SYS_ADMIN", "NET_ADMIN", "SYS_MODULE"}
    violation := caps[_]
    forbidden[violation]

    msg := sprintf("Container %v has forbidden capability %v", [container.name, violation])
}

# 5.2.3 - Minimize admission of containers with root user
deny_root_user[msg] {
    input.kind == "Pod"
    not input.spec.securityContext.runAsNonRoot == true

    msg := "Pod must run as non-root user"
}

# 5.2.6 - Minimize admission of root containers
deny_privileged[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged == true

    msg := sprintf("Container %v must not run privileged", [container.name])
}

# 5.2.9 - Minimize admission of containers with specific capabilities
deny_host_network[msg] {
    input.kind == "Pod"
    input.spec.hostNetwork == true

    msg := "Pod must not use host network"
}
```

**HIPAA Compliance:**
```rego
# policies/compliance/hipaa.rego
package compliance.hipaa

# Encryption at rest required
deny_unencrypted_storage[msg] {
    input.type == "aws_ebs_volume"
    not input.encrypted == true

    msg := sprintf("EBS volume %v must be encrypted", [input.id])
}

# Encryption in transit required
deny_unencrypted_transit[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"

    annotations := input.metadata.annotations
    not annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"]

    msg := "LoadBalancer must use SSL/TLS"
}

# Audit logging required
deny_no_audit_logs[msg] {
    input.type == "aws_eks_cluster"

    log_types := input.enabled_cluster_log_types
    not log_types[_] == "audit"

    msg := "EKS cluster must enable audit logs"
}

# Data retention policy
deny_insufficient_retention[msg] {
    input.type == "aws_cloudwatch_log_group"
    input.retention_in_days < 365

    msg := "Log retention must be at least 365 days for HIPAA"
}
```

### Automated Compliance Reporting

```python
# scripts/compliance_report.py
"""
Generate compliance reports from policy evaluations
"""
import json
import subprocess
from datetime import datetime
from typing import Dict, List

class ComplianceReporter:
    """Generate compliance reports"""

    def __init__(self, policies_dir: str):
        self.policies_dir = policies_dir
        self.results = []

    def evaluate_policies(self, resources_dir: str) -> Dict:
        """Evaluate all policies against resources"""

        # Run OPA evaluation
        cmd = [
            "opa", "eval",
            "-d", self.policies_dir,
            "-i", resources_dir,
            "--format", "json",
            "data.compliance"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

    def generate_report(self, evaluation_results: Dict) -> str:
        """Generate HTML compliance report"""

        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Compliance Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>ML Infrastructure Compliance Report</h1>
            <p>Generated: {datetime.now().isoformat()}</p>

            <h2>Summary</h2>
            <table>
                <tr>
                    <th>Framework</th>
                    <th>Total Checks</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Status</th>
                </tr>
        """

        # Add framework results
        for framework, results in evaluation_results.items():
            total = results['total']
            passed = results['passed']
            failed = results['failed']
            status = "PASS" if failed == 0 else "FAIL"

            report += f"""
                <tr>
                    <td>{framework}</td>
                    <td>{total}</td>
                    <td class="pass">{passed}</td>
                    <td class="fail">{failed}</td>
                    <td class="{'pass' if status == 'PASS' else 'fail'}">{status}</td>
                </tr>
            """

        report += """
            </table>
            </body>
            </html>
        """

        return report

    def export_report(self, report: str, filename: str):
        """Export report to file"""
        with open(filename, 'w') as f:
            f.write(report)

# Usage
reporter = ComplianceReporter("policies/compliance")
results = reporter.evaluate_policies("resources/")
report = reporter.generate_report(results)
reporter.export_report(report, "compliance-report.html")
```

## ML Infrastructure Security Policies

### Data Access Control

```rego
# policies/data_access.rego
package data.access

import data.users
import data.datasets

# Data classification levels
data_levels = {"public", "internal", "confidential", "restricted"}

# User can access dataset if clearance >= data level
allow {
    user := data.users[input.user]
    dataset := data.datasets[input.dataset]

    user.clearance_level >= dataset.classification_level
}

# Audit all data access
audit[entry] {
    entry := {
        "user": input.user,
        "dataset": input.dataset,
        "action": input.action,
        "timestamp": time.now_ns(),
        "allowed": allow,
    }
}
```

### Model Deployment Security

```rego
# policies/model_deployment.rego
package model.deployment

# Model must be scanned for vulnerabilities
deny[msg] {
    input.type == "model_deployment"
    not input.security_scan.completed == true

    msg := "Model must pass security scan before deployment"
}

# Model must have required metadata
deny[msg] {
    input.type == "model_deployment"

    required_metadata := {"version", "author", "training_date", "dataset"}
    provided_metadata := {k | input.metadata[k]}
    missing := required_metadata - provided_metadata

    count(missing) > 0
    msg := sprintf("Model missing metadata: %v", [missing])
}

# Production models must have approval
deny[msg] {
    input.type == "model_deployment"
    input.environment == "production"
    not input.approval.approved == true

    msg := "Production deployments require approval"
}
```

## Summary

Policy as Code provides:
- **Automated Enforcement**: Consistent policy application
- **Version Control**: Track policy changes over time
- **Testing**: Validate policies before deployment
- **Compliance**: Automate compliance checks
- **Audit Trail**: Complete history of policy decisions

**Key Tools:**
1. OPA: General-purpose policy engine
2. Gatekeeper: Kubernetes admission controller
3. Sentinel: HashiCorp policy framework
4. Conftest: Test configuration files
5. Policy libraries: CIS, HIPAA, SOC 2

## Next Steps

- Continue to [Lecture 8: Secrets Management](08-secrets-management.md)
- Write OPA policies for your infrastructure
- Implement Gatekeeper in Kubernetes
- Set up compliance automation

## Additional Resources

- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [Gatekeeper Documentation](https://open-policy-agent.github.io/gatekeeper/)
- [Sentinel Documentation](https://docs.hashicorp.com/sentinel)
- [Conftest](https://www.conftest.dev/)
- [Policy Library](https://github.com/open-policy-agent/library)
