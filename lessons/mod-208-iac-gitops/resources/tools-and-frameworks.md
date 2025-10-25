# Tools and Frameworks - Module 208: IaC and GitOps

## Infrastructure as Code Tools

### Terraform

**Description**: HashiCorp's infrastructure as code tool using HCL (HashiCorp Configuration Language)

**Key Features**:
- Declarative configuration
- Provider ecosystem (AWS, GCP, Azure, Kubernetes, etc.)
- State management
- Module system
- Plan/Apply workflow

**When to Use**:
- Multi-cloud infrastructure
- Established ecosystem and community
- Team familiar with HCL
- Need for HashiCorp ecosystem integration

**Installation**:
```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Resources**:
- Website: https://www.terraform.io/
- Registry: https://registry.terraform.io/
- Documentation: https://www.terraform.io/docs

---

### Pulumi

**Description**: Modern infrastructure as code using familiar programming languages (Python, TypeScript, Go, C#)

**Key Features**:
- Use real programming languages
- Type safety and IDE support
- Component model
- State management
- Testing with standard frameworks

**When to Use**:
- Team prefers general-purpose languages
- Need complex logic and abstractions
- Want familiar tooling
- Sharing code between IaC and application

**Installation**:
```bash
curl -fsSL https://get.pulumi.com | sh
```

**Resources**:
- Website: https://www.pulumi.com/
- Documentation: https://www.pulumi.com/docs/
- Examples: https://github.com/pulumi/examples

---

### AWS CDK

**Description**: AWS Cloud Development Kit for defining cloud infrastructure in code

**Key Features**:
- AWS-focused
- High-level constructs
- Multiple language support
- CloudFormation under the hood

**When to Use**:
- AWS-only infrastructure
- Team familiar with AWS services
- Need for AWS-specific abstractions

**Installation**:
```bash
npm install -g aws-cdk
```

**Resources**:
- Website: https://aws.amazon.com/cdk/
- Documentation: https://docs.aws.amazon.com/cdk/

---

### Comparison Matrix

| Feature | Terraform | Pulumi | AWS CDK |
|---------|-----------|--------|---------|
| Language | HCL | Python/TS/Go/C# | TypeScript/Python/Java |
| Cloud Support | Multi-cloud | Multi-cloud | AWS-only |
| State Management | Required | Required | CloudFormation |
| Community | Large | Growing | AWS-focused |
| Learning Curve | Moderate | Low (if know language) | Moderate |
| Testing | Terratest | Native frameworks | CDK Testing |
| Module Ecosystem | Extensive | Growing | AWS Constructs |

---

## GitOps Tools

### ArgoCD

**Description**: Declarative GitOps continuous delivery tool for Kubernetes

**Key Features**:
- Web UI and CLI
- Automated sync from Git
- Rollback capabilities
- Multi-cluster management
- Application health monitoring

**When to Use**:
- Kubernetes-native deployments
- Need for web UI
- Multi-cluster management
- SSO requirements

**Installation**:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Resources**:
- Website: https://argoproj.github.io/cd/
- Documentation: https://argo-cd.readthedocs.io/
- Examples: https://github.com/argoproj/argocd-example-apps

---

### FluxCD

**Description**: GitOps toolkit for Kubernetes with composable APIs

**Key Features**:
- GitOps Toolkit (modular)
- Image automation
- Kustomize and Helm support
- Multi-tenancy
- Notification system

**When to Use**:
- Need modular architecture
- Image automation required
- Helm and Kustomize workflows
- Multi-tenancy requirements

**Installation**:
```bash
curl -s https://fluxcd.io/install.sh | sudo bash
flux bootstrap github --owner=<org> --repository=<repo>
```

**Resources**:
- Website: https://fluxcd.io/
- Documentation: https://fluxcd.io/docs/
- GitOps Toolkit: https://toolkit.fluxcd.io/

---

### Jenkins X

**Description**: CI/CD solution for cloud native applications on Kubernetes

**Key Features**:
- Complete CI/CD pipeline
- GitOps workflows
- Preview environments
- Tekton pipelines

**When to Use**:
- Need full CI/CD solution
- Preview environments
- Jenkins ecosystem familiarity

**Resources**:
- Website: https://jenkins-x.io/
- Documentation: https://jenkins-x.io/docs/

---

### GitOps Tools Comparison

| Feature | ArgoCD | FluxCD | Jenkins X |
|---------|--------|--------|-----------|
| Architecture | Monolithic | Modular | Complete CI/CD |
| UI | Yes | Limited | Yes |
| Multi-cluster | Yes | Yes | Yes |
| Image Automation | Limited | Yes | Yes |
| Helm Support | Yes | Yes | Yes |
| Maturity | High | High | Moderate |
| Complexity | Low | Moderate | High |

---

## Configuration Management

### Kustomize

**Description**: Kubernetes-native configuration management without templates

**Key Features**:
- Overlay-based customization
- No templates or DSL
- Built into kubectl
- Composition over inheritance

**Installation**: Built into kubectl 1.14+

**Resources**:
- Website: https://kustomize.io/
- Documentation: https://kubectl.docs.kubernetes.io/guides/introduction/kustomize/

---

### Helm

**Description**: Package manager for Kubernetes

**Key Features**:
- Chart repository
- Templating engine
- Release management
- Dependency management

**Installation**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Resources**:
- Website: https://helm.sh/
- Chart Hub: https://artifacthub.io/

---

## Testing Tools

### Terratest

**Description**: Go library for testing infrastructure code

**Key Features**:
- Deploy and validate
- Integration testing
- Parallel test execution
- Retry logic

**Installation**:
```bash
go get github.com/gruntwork-io/terratest
```

**Resources**:
- Website: https://terratest.gruntwork.io/
- Examples: https://github.com/gruntwork-io/terratest/tree/master/examples

---

### Kitchen-Terraform

**Description**: Test Kitchen plugin for Terraform

**Key Features**:
- Ruby-based testing
- InSpec integration
- Multiple platforms
- Converge and verify workflow

**Installation**:
```bash
gem install kitchen-terraform
```

**Resources**:
- GitHub: https://github.com/newcontext-oss/kitchen-terraform

---

### Conftest

**Description**: Write tests against structured configuration data

**Key Features**:
- Policy-based testing
- OPA/Rego policies
- Multiple formats (YAML, JSON, etc.)
- CI/CD integration

**Installation**:
```bash
brew install conftest
```

**Resources**:
- Website: https://www.conftest.dev/
- GitHub: https://github.com/open-policy-agent/conftest

---

## Policy as Code

### Open Policy Agent (OPA)

**Description**: General-purpose policy engine

**Key Features**:
- Rego policy language
- Decoupled policy decision
- Rich ecosystem
- Kubernetes admission control

**Installation**:
```bash
brew install opa
```

**Resources**:
- Website: https://www.openpolicyagent.org/
- Playground: https://play.openpolicyagent.org/
- Library: https://github.com/open-policy-agent/library

---

### Gatekeeper

**Description**: OPA-based Kubernetes admission controller

**Key Features**:
- Constraint templates
- Audit mode
- Native CRDs
- Mutation policies

**Installation**:
```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
```

**Resources**:
- Documentation: https://open-policy-agent.github.io/gatekeeper/
- Library: https://github.com/open-policy-agent/gatekeeper-library

---

### HashiCorp Sentinel

**Description**: Policy as code framework for HashiCorp products

**Key Features**:
- Terraform integration
- Cost estimation
- Compliance enforcement
- Testing framework

**When to Use**: Terraform Enterprise/Cloud users

**Resources**:
- Documentation: https://docs.hashicorp.com/sentinel

---

## Secrets Management

### HashiCorp Vault

**Description**: Secrets and encryption management system

**Key Features**:
- Dynamic secrets
- Encryption as a service
- Multiple auth methods
- Audit logging

**Installation**:
```bash
brew install vault
```

**Resources**:
- Website: https://www.vaultproject.io/
- Documentation: https://www.vaultproject.io/docs

---

### SOPS

**Description**: Secrets OPerationS - encrypt files with KMS

**Key Features**:
- AWS KMS, GCP KMS, Azure Key Vault support
- Git-friendly
- Partial encryption
- Editor integration

**Installation**:
```bash
brew install sops
```

**Resources**:
- GitHub: https://github.com/mozilla/sops

---

### Sealed Secrets

**Description**: Kubernetes controller for one-way encrypted Secrets

**Key Features**:
- Asymmetric encryption
- Git-safe
- Scope control
- Kubernetes-native

**Installation**:
```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

**Resources**:
- GitHub: https://github.com/bitnami-labs/sealed-secrets

---

### External Secrets Operator

**Description**: Sync secrets from external stores to Kubernetes

**Key Features**:
- Multiple provider support
- Automated sync
- Secret rotation
- CRD-based

**Installation**:
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets
```

**Resources**:
- Website: https://external-secrets.io/
- Documentation: https://external-secrets.io/latest/

---

### Secrets Management Comparison

| Tool | Type | Key Feature | Best For |
|------|------|-------------|----------|
| Vault | Full solution | Dynamic secrets | Enterprise |
| SOPS | File encryption | Git-friendly | GitOps |
| Sealed Secrets | K8s-native | Simple encryption | Kubernetes |
| ESO | Sync operator | Multi-provider | Integration |

---

## CI/CD Integration Tools

### GitHub Actions

**Description**: GitHub's built-in CI/CD platform

**Key Features**:
- Native GitHub integration
- Marketplace actions
- Matrix builds
- Self-hosted runners

**Resources**:
- Documentation: https://docs.github.com/actions

---

### GitLab CI

**Description**: GitLab's integrated CI/CD

**Key Features**:
- Auto DevOps
- Container registry
- Kubernetes integration
- Security scanning

**Resources**:
- Documentation: https://docs.gitlab.com/ee/ci/

---

### Jenkins

**Description**: Open-source automation server

**Key Features**:
- Extensive plugin ecosystem
- Pipeline as code
- Distributed builds
- Community support

**Resources**:
- Website: https://www.jenkins.io/
- Plugins: https://plugins.jenkins.io/

---

## Monitoring and Observability

### Prometheus

**Description**: Monitoring and alerting toolkit

**Key Features**:
- Time-series database
- PromQL query language
- Service discovery
- Alerting

**Resources**:
- Website: https://prometheus.io/
- Documentation: https://prometheus.io/docs/

---

### Grafana

**Description**: Visualization and analytics platform

**Key Features**:
- Multiple data sources
- Rich visualizations
- Alerting
- Dashboards

**Resources**:
- Website: https://grafana.com/
- Dashboards: https://grafana.com/grafana/dashboards/

---

## Development Tools

### VS Code Extensions

1. **HashiCorp Terraform**: Syntax highlighting and IntelliSense
2. **YAML**: YAML support and validation
3. **Kubernetes**: Kubernetes manifests and tools
4. **GitLens**: Git integration
5. **OPA**: Rego language support

### CLI Tools

1. **kubectl**: Kubernetes CLI
2. **kustomize**: Configuration management
3. **argocd**: ArgoCD CLI
4. **flux**: FluxCD CLI
5. **vault**: Vault CLI
6. **kubeseal**: Sealed Secrets CLI

### IDE Integrations

1. **Terraform Language Server**: LSP for Terraform
2. **Pulumi IDE Extensions**: Language-specific support
3. **Kubernetes Tools**: IntelliJ, VS Code plugins

---

## Recommended Tool Stack for ML Infrastructure

### Small Team (< 10 engineers)
- **IaC**: Terraform
- **GitOps**: ArgoCD
- **Config**: Kustomize
- **Testing**: Conftest + basic Terratest
- **Policy**: OPA/Gatekeeper
- **Secrets**: Sealed Secrets
- **CI/CD**: GitHub Actions

### Medium Team (10-50 engineers)
- **IaC**: Terraform + Pulumi
- **GitOps**: ArgoCD or FluxCD
- **Config**: Kustomize + Helm
- **Testing**: Terratest + Kitchen-Terraform
- **Policy**: OPA/Gatekeeper + Conftest
- **Secrets**: Vault + External Secrets Operator
- **CI/CD**: GitLab CI or GitHub Actions

### Large Team (50+ engineers)
- **IaC**: Terraform with Cloud/Enterprise
- **GitOps**: ArgoCD with ApplicationSets
- **Config**: Kustomize + Helm
- **Testing**: Comprehensive Terratest + InSpec
- **Policy**: OPA + Sentinel
- **Secrets**: Vault with HSM
- **CI/CD**: GitLab CI or Jenkins

---

## Getting Started Checklist

- [ ] Install Terraform and Pulumi
- [ ] Set up kubectl and cluster access
- [ ] Install ArgoCD or FluxCD
- [ ] Set up Kustomize/Helm
- [ ] Install testing tools (Terratest, OPA)
- [ ] Configure secrets management
- [ ] Set up CI/CD pipeline
- [ ] Install monitoring tools

---

**Last Updated**: October 2025
