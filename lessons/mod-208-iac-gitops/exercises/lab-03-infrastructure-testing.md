# Lab 3: Infrastructure Testing

## Objectives

- Write Terratest tests for infrastructure
- Implement OPA policies
- Build CI pipeline for infrastructure validation
- Test policy enforcement

## Duration

5 hours

## Lab Tasks

### Task 1: Setup Test Environment

```bash
# Create test directory
mkdir infrastructure-tests && cd infrastructure-tests

# Initialize Go module
go mod init github.com/yourorg/infrastructure-tests

# Add dependencies
go get github.com/gruntwork-io/terratest/modules/terraform
go get github.com/stretchr/testify/assert
```

### Task 2: Write Terratest Tests

Create `vpc_test.go`:

```go
package test

import (
	"testing"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/gruntwork-io/terratest/modules/aws"
	"github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
	t.Parallel()

	opts := &terraform.Options{
		TerraformDir: "../modules/vpc",
		Vars: map[string]interface{}{
			"vpc_cidr": "10.0.0.0/16",
			"environment": "test",
			"availability_zones": []string{"us-west-2a", "us-west-2b"},
		},
	}

	defer terraform.Destroy(t, opts)
	terraform.InitAndApply(t, opts)

	vpcID := terraform.Output(t, opts, "vpc_id")
	vpc := aws.GetVpcById(t, vpcID, "us-west-2")

	assert.Equal(t, "10.0.0.0/16", vpc.CidrBlock)
	assert.True(t, *vpc.EnableDnsHostnames)
}
```

### Task 3: Write OPA Policies

Create `policies/kubernetes/security.rego`:

```rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Privileged containers not allowed: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext.runAsNonRoot
    msg := "Pods must run as non-root"
}
```

### Task 4: Test OPA Policies

```bash
# Test policies
opa test policies/ -v

# Validate manifest
opa eval -i manifest.yaml -d policies/ "data.kubernetes.admission.deny"
```

### Task 5: CI Pipeline

Create `.github/workflows/test.yaml`:

```yaml
name: Infrastructure Tests

on: [push, pull_request]

jobs:
  terratest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Run Terratest
        run: |
          cd test
          go test -v -timeout 30m

  opa-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: open-policy-agent/setup-opa@v2
      - name: Test policies
        run: opa test policies/ -v
```

## Exercises

1. Add contract tests for Kubernetes API
2. Implement compliance tests
3. Test disaster recovery procedures
4. Add performance tests

## Submission

- Test code
- Test results
- CI pipeline output
- Coverage report
