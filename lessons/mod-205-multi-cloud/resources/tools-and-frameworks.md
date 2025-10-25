# Module 205: Multi-Cloud Architecture - Tools and Frameworks

## Infrastructure as Code (IaC)

### Terraform
- **Purpose**: Multi-cloud infrastructure provisioning
- **Website**: https://www.terraform.io/
- **License**: MPL 2.0
- **Key Features**:
  - Cloud-agnostic HCL language
  - State management
  - Provider ecosystem (AWS, GCP, Azure, 100+)
  - Module registry
- **Use Cases**: Provisioning VPCs, VPNs, compute resources across clouds
- **Installation**: 
  ```bash
  brew install terraform
  # or download from terraform.io
  ```

### Pulumi
- **Purpose**: Infrastructure as code using programming languages
- **Website**: https://www.pulumi.com/
- **License**: Apache 2.0
- **Languages**: TypeScript, Python, Go, C#, Java
- **Key Features**:
  - Use familiar programming languages
  - Built-in testing capabilities
  - State management
  - Policy as code
- **Installation**:
  ```bash
  curl -fsSL https://get.pulumi.com | sh
  ```

### Crossplane
- **Purpose**: Kubernetes-based infrastructure management
- **Website**: https://crossplane.io/
- **License**: Apache 2.0
- **Key Features**:
  - Kubernetes CRDs for cloud resources
  - GitOps-friendly
  - Composition of resources
- **Installation**:
  ```bash
  helm install crossplane --namespace crossplane-system \
    crossplane-stable/crossplane --create-namespace
  ```

---

## Container Orchestration

### Kubernetes
- **Purpose**: Container orchestration platform
- **Website**: https://kubernetes.io/
- **License**: Apache 2.0
- **Managed Services**:
  - AWS EKS
  - GCP GKE
  - Azure AKS
- **Multi-Cloud Tools**:
  - **kubefed**: Kubernetes Cluster Federation
  - **Submariner**: Cross-cluster networking
  - **Cluster API**: Declarative cluster management

### Managed Kubernetes Tools

#### eksctl
- **Purpose**: EKS cluster management
- **Website**: https://eksctl.io/
- **Installation**:
  ```bash
  brew install eksctl
  ```

#### gcloud container
- **Purpose**: GKE cluster management
- **Installation**: Part of Google Cloud SDK

---

## Service Mesh

### Istio
- **Purpose**: Service mesh for microservices
- **Website**: https://istio.io/
- **License**: Apache 2.0
- **Key Features**:
  - Traffic management
  - Security (mTLS)
  - Observability
  - Multi-cluster support
- **Installation**:
  ```bash
  curl -L https://istio.io/downloadIstio | sh -
  istioctl install --set profile=demo
  ```

### Linkerd
- **Purpose**: Lightweight service mesh
- **Website**: https://linkerd.io/
- **License**: Apache 2.0
- **Key Features**:
  - Simpler than Istio
  - Low resource overhead
  - Automatic mTLS
  - Multi-cluster
- **Installation**:
  ```bash
  curl -sL https://run.linkerd.io/install | sh
  linkerd install | kubectl apply -f -
  ```

### Consul
- **Purpose**: Service mesh and service discovery
- **Website**: https://www.consul.io/
- **License**: MPL 2.0
- **Key Features**:
  - Multi-cloud service discovery
  - Health checking
  - Key/value store
  - Multi-datacenter

---

## Networking

### WireGuard
- **Purpose**: Modern VPN protocol
- **Website**: https://www.wireguard.com/
- **License**: GPLv2
- **Key Features**:
  - Faster than IPsec
  - Simpler configuration
  - Built into Linux kernel
- **Use Case**: Alternative to cloud provider VPNs

### Tailscale
- **Purpose**: WireGuard-based mesh VPN
- **Website**: https://tailscale.com/
- **Key Features**:
  - Zero-config mesh networking
  - Works across clouds
  - Built on WireGuard
- **Use Case**: Connecting resources across clouds easily

### Calico
- **Purpose**: Kubernetes networking and security
- **Website**: https://www.tigera.io/project-calico/
- **License**: Apache 2.0
- **Key Features**:
  - Network policy enforcement
  - Cross-cloud networking
  - eBPF dataplane

---

## Monitoring & Observability

### Prometheus
- **Purpose**: Metrics collection and alerting
- **Website**: https://prometheus.io/
- **License**: Apache 2.0
- **Key Features**:
  - Pull-based metrics
  - PromQL query language
  - Federation for multi-cluster
  - Extensive exporter ecosystem
- **Installation**:
  ```bash
  helm install prometheus prometheus-community/kube-prometheus-stack
  ```

### Grafana
- **Purpose**: Visualization and dashboards
- **Website**: https://grafana.com/
- **License**: AGPLv3
- **Key Features**:
  - Multi-datasource support
  - Dashboard templating
  - Alerting
  - Cloud monitoring plugins
- **Installation**:
  ```bash
  helm install grafana grafana/grafana
  ```

### Thanos
- **Purpose**: Prometheus long-term storage
- **Website**: https://thanos.io/
- **License**: Apache 2.0
- **Key Features**:
  - Object storage backend
  - Cross-cluster queries
  - Downsampling
  - High availability

### Datadog
- **Purpose**: Cloud monitoring platform (SaaS)
- **Website**: https://www.datadoghq.com/
- **Key Features**:
  - Unified monitoring across clouds
  - APM and tracing
  - Log management
  - Native cloud integrations

### New Relic
- **Purpose**: Application performance monitoring
- **Website**: https://newrelic.com/
- **Key Features**:
  - Multi-cloud visibility
  - AI-powered insights
  - Distributed tracing

---

## Logging

### ELK Stack (Elasticsearch, Logstash, Kibana)
- **Purpose**: Log aggregation and analysis
- **Website**: https://www.elastic.co/
- **License**: Elastic License / SSPL
- **Use Case**: Centralized logging across clouds

### Loki
- **Purpose**: Log aggregation system by Grafana
- **Website**: https://grafana.com/oss/loki/
- **License**: AGPLv3
- **Key Features**:
  - Designed for Kubernetes
  - Cost-effective
  - Labels-based indexing
  - Integrates with Grafana

### Fluentd
- **Purpose**: Log collector and forwarder
- **Website**: https://www.fluentd.org/
- **License**: Apache 2.0
- **Key Features**:
  - Unified logging layer
  - 500+ plugins
  - Cloud-native

---

## Distributed Tracing

### Jaeger
- **Purpose**: Distributed tracing
- **Website**: https://www.jaegertracing.io/
- **License**: Apache 2.0
- **Key Features**:
  - OpenTelemetry compatible
  - Multiple storage backends
  - Service dependency analysis

### Zipkin
- **Purpose**: Distributed tracing
- **Website**: https://zipkin.io/
- **License**: Apache 2.0
- **Key Features**:
  - Simple setup
  - Multiple language support
  - Trace visualization

### OpenTelemetry
- **Purpose**: Observability framework
- **Website**: https://opentelemetry.io/
- **License**: Apache 2.0
- **Key Features**:
  - Vendor-neutral
  - Metrics, logs, traces
  - Auto-instrumentation

---

## Cost Management

### Kubecost
- **Purpose**: Kubernetes cost monitoring
- **Website**: https://www.kubecost.com/
- **Key Features**:
  - Multi-cloud cost allocation
  - Resource efficiency recommendations
  - Real-time cost monitoring
  - Supports EKS, GKE, AKS

### CloudHealth (VMware)
- **Purpose**: Multi-cloud cost management
- **Website**: https://www.cloudhealthtech.com/
- **Key Features**:
  - Unified cloud costs
  - Optimization recommendations
  - Budgets and forecasting

### Cloudability (Apptio)
- **Purpose**: Cloud cost intelligence
- **Website**: https://www.cloudability.com/
- **Key Features**:
  - Multi-cloud cost analytics
  - Anomaly detection
  - Rightsizing recommendations

### Infracost
- **Purpose**: Cost estimates for Terraform
- **Website**: https://www.infracost.io/
- **License**: Apache 2.0
- **Key Features**:
  - Terraform cost estimation
  - CI/CD integration
  - Multi-cloud support
- **Installation**:
  ```bash
  brew install infracost
  ```

---

## Security

### HashiCorp Vault
- **Purpose**: Secrets management
- **Website**: https://www.vaultproject.io/
- **License**: MPL 2.0
- **Key Features**:
  - Multi-cloud secrets storage
  - Dynamic secrets
  - Encryption as a service
  - Audit logging

### External Secrets Operator
- **Purpose**: Kubernetes secrets from external sources
- **Website**: https://external-secrets.io/
- **License**: Apache 2.0
- **Key Features**:
  - Sync secrets from AWS Secrets Manager, GCP Secret Manager, Azure Key Vault
  - Kubernetes-native

### Falco
- **Purpose**: Runtime security
- **Website**: https://falco.org/
- **License**: Apache 2.0
- **Key Features**:
  - Threat detection
  - Kubernetes security
  - eBPF-based

### Open Policy Agent (OPA)
- **Purpose**: Policy as code
- **Website**: https://www.openpolicyagent.org/
- **License**: Apache 2.0
- **Key Features**:
  - Unified policy enforcement
  - Kubernetes admission control
  - Multi-cloud policy management

---

## CI/CD

### GitLab CI/CD
- **Purpose**: Complete DevOps platform
- **Website**: https://about.gitlab.com/
- **Key Features**:
  - Built-in CI/CD
  - Multi-cloud deployments
  - Auto DevOps

### GitHub Actions
- **Purpose**: CI/CD workflows
- **Website**: https://github.com/features/actions
- **Key Features**:
  - Native GitHub integration
  - Matrix builds for multi-cloud
  - Extensive marketplace

### Argo CD
- **Purpose**: GitOps continuous delivery
- **Website**: https://argo-cd.readthedocs.io/
- **License**: Apache 2.0
- **Key Features**:
  - Kubernetes-native
  - Multi-cluster support
  - Declarative GitOps

### Flux CD
- **Purpose**: GitOps toolkit
- **Website**: https://fluxcd.io/
- **License**: Apache 2.0
- **Key Features**:
  - Kubernetes operator
  - Multi-tenancy
  - Progressive delivery

### Spinnaker
- **Purpose**: Multi-cloud continuous delivery
- **Website**: https://spinnaker.io/
- **License**: Apache 2.0
- **Key Features**:
  - Native multi-cloud support
  - Deployment strategies
  - Pipeline management

---

## Backup & Disaster Recovery

### Velero
- **Purpose**: Kubernetes backup and restore
- **Website**: https://velero.io/
- **License**: Apache 2.0
- **Key Features**:
  - Cluster backup
  - Cross-cloud migration
  - Disaster recovery
- **Installation**:
  ```bash
  velero install \
    --provider aws \
    --bucket velero-backups \
    --backup-location-config region=us-east-1
  ```

### Restic
- **Purpose**: Backup program
- **Website**: https://restic.net/
- **License**: BSD 2-Clause
- **Key Features**:
  - Encrypted backups
  - Multiple storage backends
  - Incremental backups

---

## Testing

### Chaos Mesh
- **Purpose**: Chaos engineering for Kubernetes
- **Website**: https://chaos-mesh.org/
- **License**: Apache 2.0
- **Key Features**:
  - Multi-cloud chaos testing
  - Network latency injection
  - Pod failures

### Gremlin
- **Purpose**: Chaos engineering platform (SaaS)
- **Website**: https://www.gremlin.com/
- **Key Features**:
  - Multi-cloud chaos experiments
  - Safe failure injection
  - Enterprise features

---

## API Gateways

### Kong
- **Purpose**: API gateway and service mesh
- **Website**: https://konghq.com/
- **License**: Apache 2.0
- **Key Features**:
  - Multi-cloud API management
  - Plugin ecosystem
  - Rate limiting, authentication

### Ambassador
- **Purpose**: Kubernetes-native API gateway
- **Website**: https://www.getambassador.io/
- **License**: Apache 2.0
- **Key Features**:
  - Envoy-based
  - Kubernetes ingress
  - Multi-cluster routing

---

## CLI Tools

### kubectl
- **Purpose**: Kubernetes CLI
- **Installation**:
  ```bash
  brew install kubectl
  ```

### kubectx / kubens
- **Purpose**: Switch between Kubernetes contexts/namespaces
- **Installation**:
  ```bash
  brew install kubectx
  ```

### k9s
- **Purpose**: Terminal UI for Kubernetes
- **Installation**:
  ```bash
  brew install k9s
  ```

### aws-cli
- **Purpose**: AWS command line interface
- **Installation**:
  ```bash
  brew install awscli
  ```

### gcloud
- **Purpose**: GCP command line interface
- **Installation**:
  ```bash
  brew install google-cloud-sdk
  ```

### az-cli
- **Purpose**: Azure command line interface
- **Installation**:
  ```bash
  brew install azure-cli
  ```

---

## Comparison Tables

### IaC Tools Comparison

| Feature | Terraform | Pulumi | Crossplane |
|---------|-----------|--------|------------|
| Language | HCL | Multiple | YAML/CRDs |
| State Mgmt | Yes | Yes | Kubernetes |
| Learning Curve | Medium | Low-Medium | Medium-High |
| Cloud Support | Excellent | Excellent | Good |
| Best For | Multi-cloud IaC | Developers | K8s-native |

### Service Mesh Comparison

| Feature | Istio | Linkerd | Consul |
|---------|-------|---------|--------|
| Complexity | High | Low | Medium |
| Resource Usage | High | Low | Medium |
| Multi-cluster | Yes | Yes | Yes |
| Non-K8s | Yes | No | Yes |
| Best For | Enterprise | Simplicity | Multi-DC |

### Monitoring Comparison

| Feature | Prometheus | Datadog | New Relic |
|---------|------------|---------|-----------|
| Type | Self-hosted | SaaS | SaaS |
| Cost | Free (infra) | $$$  | $$$ |
| Setup Complexity | Medium | Low | Low |
| Customization | High | Medium | Medium |
| Best For | K8s, OSS | Enterprise | APM |

---

## Recommended Tool Stack

### Small Team (<10 engineers)
- **IaC**: Terraform
- **Orchestration**: Managed K8s (EKS/GKE)
- **Service Mesh**: Linkerd
- **Monitoring**: Prometheus + Grafana
- **Cost**: Kubecost community edition

### Medium Team (10-50 engineers)
- **IaC**: Terraform + Atlantis
- **Orchestration**: EKS/GKE + Cluster API
- **Service Mesh**: Istio
- **Monitoring**: Prometheus + Thanos + Grafana
- **Cost**: Kubecost or CloudHealth
- **Security**: Vault + External Secrets

### Large Team (50+ engineers)
- **IaC**: Terraform Enterprise + Pulumi
- **Orchestration**: Multi-cluster K8s + Cluster API
- **Service Mesh**: Istio with multi-primary
- **Monitoring**: Datadog or full Prometheus stack
- **Cost**: CloudHealth or Cloudability
- **Security**: Vault Enterprise + OPA
- **CI/CD**: Spinnaker or Argo CD

---

## Getting Started Checklist

- [ ] Install Terraform and learn basics
- [ ] Set up kubectl and connect to test cluster
- [ ] Deploy Prometheus + Grafana
- [ ] Experiment with Istio in lab environment
- [ ] Try Kubecost for cost visibility
- [ ] Set up Velero for backups
- [ ] Configure External Secrets Operator
- [ ] Explore Argo CD for GitOps
