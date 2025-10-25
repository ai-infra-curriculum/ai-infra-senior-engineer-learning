# Tools and Frameworks for Module 201

## Essential Tools

### Kubernetes Core Tools

#### kubectl
- **Description:** Official Kubernetes CLI
- **Installation:**
  ```bash
  # macOS
  brew install kubectl

  # Linux
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/
  ```
- **Key Features:** Resource management, debugging, port-forwarding
- **Website:** https://kubernetes.io/docs/reference/kubectl/

#### kubectx and kubens
- **Description:** Fast context and namespace switching
- **Installation:**
  ```bash
  brew install kubectx
  ```
- **Usage:**
  ```bash
  kubectx                    # List contexts
  kubectx my-cluster        # Switch context
  kubens ml-production      # Switch namespace
  ```
- **Website:** https://github.com/ahmetb/kubectx

#### k9s
- **Description:** Terminal UI for Kubernetes
- **Installation:**
  ```bash
  brew install k9s
  ```
- **Features:** Real-time cluster monitoring, log viewing, resource editing
- **Website:** https://k9scli.io/

#### stern
- **Description:** Multi-pod log tailing
- **Installation:**
  ```bash
  brew install stern
  ```
- **Usage:**
  ```bash
  stern model-server --namespace ml-production
  ```
- **Website:** https://github.com/stern/stern

#### kube-ps1
- **Description:** Shows current context and namespace in shell prompt
- **Installation:**
  ```bash
  brew install kube-ps1
  ```
- **Website:** https://github.com/jonmosco/kube-ps1

## Operator Development

### operator-sdk
- **Description:** Framework for building Kubernetes operators
- **Installation:**
  ```bash
  brew install operator-sdk
  ```
- **Features:** Project scaffolding, CRD generation, testing utilities
- **Website:** https://sdk.operatorframework.io/

### kubebuilder
- **Description:** SDK for building Kubernetes APIs using CRDs
- **Installation:**
  ```bash
  brew install kubebuilder
  ```
- **Features:** Code generation, webhook scaffolding, testing framework
- **Website:** https://book.kubebuilder.io/

### controller-runtime
- **Description:** Core library for building Kubernetes controllers
- **Language:** Go
- **Usage:** Used by operator-sdk and kubebuilder
- **GitHub:** https://github.com/kubernetes-sigs/controller-runtime

## GPU Management

### NVIDIA Device Plugin
- **Description:** Enables GPU support in Kubernetes
- **Installation:**
  ```bash
  helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
  helm install nvdp nvdp/nvidia-device-plugin --namespace kube-system
  ```
- **Website:** https://github.com/NVIDIA/k8s-device-plugin

### NVIDIA GPU Operator
- **Description:** Automates GPU software component deployment
- **Installation:**
  ```bash
  helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
  helm install gpu-operator nvidia/gpu-operator --namespace gpu-operator-resources --create-namespace
  ```
- **Features:** Driver installation, monitoring, time-slicing
- **Website:** https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/

### DCGM Exporter
- **Description:** GPU metrics for Prometheus
- **Installation:** Via GPU Operator or standalone DaemonSet
- **Metrics:** GPU utilization, memory, temperature, power
- **Website:** https://github.com/NVIDIA/dcgm-exporter

## Service Mesh

### Istio
- **Description:** Full-featured service mesh
- **Installation:**
  ```bash
  curl -L https://istio.io/downloadIstio | sh -
  cd istio-*
  export PATH=$PWD/bin:$PATH
  istioctl install --set profile=demo
  ```
- **Features:** Traffic management, security, observability
- **Website:** https://istio.io/

#### istioctl
- **Description:** Istio CLI
- **Commands:**
  ```bash
  istioctl analyze              # Validate configuration
  istioctl proxy-status        # Check proxy sync status
  istioctl dashboard kiali     # Open Kiali dashboard
  ```

### Linkerd
- **Description:** Lightweight service mesh
- **Installation:**
  ```bash
  curl -sL https://run.linkerd.io/install | sh
  linkerd install | kubectl apply -f -
  ```
- **Features:** Simple, fast, Rust-based proxy
- **Website:** https://linkerd.io/

### Kiali
- **Description:** Service mesh observability console
- **Installation:** Included with Istio demo profile
- **Features:** Service graph, traffic metrics, configuration validation
- **Website:** https://kiali.io/

## Storage

### Velero
- **Description:** Backup and disaster recovery for Kubernetes
- **Installation:**
  ```bash
  brew install velero
  velero install --provider aws --plugins velero/velero-plugin-for-aws:v1.7.0 --bucket my-backup-bucket
  ```
- **Features:** Backup, restore, migration, DR
- **Website:** https://velero.io/

### Rook
- **Description:** Storage orchestration for Kubernetes
- **Supports:** Ceph, NFS, Cassandra, CockroachDB
- **Installation:** Helm or manifests
- **Website:** https://rook.io/

### Longhorn
- **Description:** Distributed block storage for Kubernetes
- **Features:** Snapshots, backups, disaster recovery
- **Installation:**
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/master/deploy/longhorn.yaml
  ```
- **Website:** https://longhorn.io/

## Autoscaling

### Karpenter
- **Description:** Kubernetes node autoscaling
- **Installation:**
  ```bash
  helm repo add karpenter https://charts.karpenter.sh
  helm install karpenter karpenter/karpenter --namespace karpenter
  ```
- **Features:** Fast provisioning, bin-packing, diverse instance types
- **Website:** https://karpenter.sh/

### KEDA
- **Description:** Kubernetes Event-Driven Autoscaling
- **Installation:**
  ```bash
  kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.11.0/keda-2.11.0.yaml
  ```
- **Features:** Scale to zero, 50+ scalers (SQS, Kafka, etc.)
- **Website:** https://keda.sh/

### Goldilocks
- **Description:** VPA recommendations dashboard
- **Installation:**
  ```bash
  helm repo add fairwinds-stable https://charts.fairwinds.com/stable
  helm install goldilocks fairwinds-stable/goldilocks
  ```
- **Features:** Resource recommendation UI
- **Website:** https://github.com/FairwindsOps/goldilocks

## Multi-Cluster

### KubeFed
- **Description:** Kubernetes Cluster Federation
- **Installation:**
  ```bash
  kubectl apply -k "github.com/kubernetes-sigs/kubefed/manifests/kubefed?ref=v0.10.0"
  ```
- **Features:** Multi-cluster resource sync, placement policies
- **Website:** https://github.com/kubernetes-sigs/kubefed

### Rancher
- **Description:** Multi-cluster management platform
- **Installation:** Docker or Kubernetes
- **Features:** UI, RBAC, monitoring, logging
- **Website:** https://rancher.com/

### ArgoCD
- **Description:** GitOps continuous delivery for Kubernetes
- **Installation:**
  ```bash
  kubectl create namespace argocd
  kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
  ```
- **Features:** Git as source of truth, multi-cluster support
- **Website:** https://argo-cd.readthedocs.io/

### Flux
- **Description:** GitOps toolkit for Kubernetes
- **Installation:**
  ```bash
  brew install fluxcd/tap/flux
  flux bootstrap github --owner=myorg --repository=fleet-infra
  ```
- **Features:** Git sync, Helm support, notifications
- **Website:** https://fluxcd.io/

## Observability

### Prometheus
- **Description:** Metrics and alerting
- **Installation:**
  ```bash
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm install prometheus prometheus-community/kube-prometheus-stack
  ```
- **Features:** Time-series database, PromQL, alerting
- **Website:** https://prometheus.io/

### Grafana
- **Description:** Visualization and dashboards
- **Installation:** Included with Prometheus stack
- **Features:** Dashboards, alerts, data source integration
- **Website:** https://grafana.com/

### Jaeger
- **Description:** Distributed tracing
- **Installation:**
  ```bash
  kubectl create namespace observability
  kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.47.0/jaeger-operator.yaml
  ```
- **Features:** Trace collection, analysis, service dependencies
- **Website:** https://www.jaegertracing.io/

### Loki
- **Description:** Log aggregation system
- **Installation:**
  ```bash
  helm repo add grafana https://grafana.github.io/helm-charts
  helm install loki grafana/loki-stack
  ```
- **Features:** Log storage, querying with LogQL
- **Website:** https://grafana.com/oss/loki/

### OpenTelemetry
- **Description:** Observability framework
- **Installation:** Operator or SDK
- **Features:** Traces, metrics, logs collection
- **Website:** https://opentelemetry.io/

## Security

### Falco
- **Description:** Runtime security and threat detection
- **Installation:**
  ```bash
  helm repo add falcosecurity https://falcosecurity.github.io/charts
  helm install falco falcosecurity/falco
  ```
- **Features:** Anomaly detection, syscall monitoring
- **Website:** https://falco.org/

### OPA Gatekeeper
- **Description:** Policy enforcement
- **Installation:**
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
  ```
- **Features:** Admission control, compliance policies
- **Website:** https://open-policy-agent.github.io/gatekeeper/

### Trivy
- **Description:** Vulnerability scanner
- **Installation:**
  ```bash
  brew install trivy
  ```
- **Usage:**
  ```bash
  trivy image pytorch/pytorch:1.12.0-cuda11.3
  trivy k8s --report summary cluster
  ```
- **Website:** https://trivy.dev/

### Cosign
- **Description:** Container signing and verification
- **Installation:**
  ```bash
  brew install cosign
  ```
- **Usage:**
  ```bash
  cosign sign --key cosign.key myimage:v1
  cosign verify --key cosign.pub myimage:v1
  ```
- **Website:** https://docs.sigstore.dev/cosign/

### cert-manager
- **Description:** X.509 certificate management
- **Installation:**
  ```bash
  kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
  ```
- **Features:** Automatic certificate issuance and renewal
- **Website:** https://cert-manager.io/

### External Secrets Operator
- **Description:** Integrate external secret managers
- **Installation:**
  ```bash
  helm repo add external-secrets https://charts.external-secrets.io
  helm install external-secrets external-secrets/external-secrets
  ```
- **Supports:** AWS Secrets Manager, Vault, GCP Secret Manager, Azure Key Vault
- **Website:** https://external-secrets.io/

## Testing and Validation

### kubeval
- **Description:** Validate Kubernetes manifests
- **Installation:**
  ```bash
  brew install kubeval
  ```
- **Usage:**
  ```bash
  kubeval deployment.yaml
  ```
- **Website:** https://kubeval.com/

### kubeconform
- **Description:** Fast Kubernetes manifest validation
- **Installation:**
  ```bash
  brew install kubeconform
  ```
- **Features:** Faster than kubeval, CRD support
- **Website:** https://github.com/yannh/kubeconform

### kube-score
- **Description:** Static analysis of Kubernetes manifests
- **Installation:**
  ```bash
  brew install kube-score
  ```
- **Usage:**
  ```bash
  kube-score score deployment.yaml
  ```
- **Website:** https://kube-score.com/

### Polaris
- **Description:** Best practices validation
- **Installation:**
  ```bash
  kubectl apply -f https://github.com/FairwindsOps/polaris/releases/latest/download/dashboard.yaml
  ```
- **Features:** Security, efficiency, reliability checks
- **Website:** https://www.fairwinds.com/polaris

### Chaos Mesh
- **Description:** Chaos engineering platform
- **Installation:**
  ```bash
  helm repo add chaos-mesh https://charts.chaos-mesh.org
  helm install chaos-mesh chaos-mesh/chaos-mesh
  ```
- **Features:** Pod/network/IO/stress chaos experiments
- **Website:** https://chaos-mesh.org/

## ML-Specific Tools

### KubeFlow
- **Description:** ML toolkit for Kubernetes
- **Installation:** Complex, see documentation
- **Components:** Pipelines, Training Operator, Katib, Serving
- **Website:** https://www.kubeflow.org/

### Ray on Kubernetes (KubeRay)
- **Description:** Distributed computing framework operator
- **Installation:**
  ```bash
  helm repo add kuberay https://ray-project.github.io/kuberay-helm/
  helm install kuberay-operator kuberay/kuberay-operator
  ```
- **Features:** Ray cluster management, autoscaling
- **Website:** https://docs.ray.io/en/latest/cluster/kubernetes/index.html

### Seldon Core
- **Description:** ML model serving platform
- **Installation:**
  ```bash
  helm install seldon-core seldon-core-operator --repo https://storage.googleapis.com/seldon-charts
  ```
- **Features:** Multi-framework serving, A/B testing, canary deployments
- **Website:** https://www.seldon.io/

### MLflow on Kubernetes
- **Description:** ML lifecycle management
- **Installation:** Custom deployments
- **Features:** Experiment tracking, model registry
- **Website:** https://mlflow.org/

## Development Tools

### Skaffold
- **Description:** Local Kubernetes development
- **Installation:**
  ```bash
  brew install skaffold
  ```
- **Features:** Auto-rebuild, auto-deploy, port-forwarding
- **Website:** https://skaffold.dev/

### Tilt
- **Description:** Multi-service development environment
- **Installation:**
  ```bash
  brew install tilt
  ```
- **Features:** Fast rebuilds, live updates, UI
- **Website:** https://tilt.dev/

### Lens
- **Description:** Kubernetes IDE
- **Installation:** Download from website
- **Features:** Cluster management, monitoring, logs, terminal
- **Website:** https://k8slens.dev/

### kubectl plugins (krew)
- **Description:** Plugin manager for kubectl
- **Installation:**
  ```bash
  brew install krew
  ```
- **Popular plugins:**
  ```bash
  kubectl krew install ctx        # kubectx alternative
  kubectl krew install ns         # kubens alternative
  kubectl krew install tree       # Resource hierarchy
  kubectl krew install neat       # Clean up manifest output
  kubectl krew install view-secret # Decode secrets
  ```
- **Website:** https://krew.sigs.k8s.io/

## Benchmarking and Load Testing

### k6
- **Description:** Load testing tool
- **Installation:**
  ```bash
  brew install k6
  ```
- **Usage:**
  ```bash
  k6 run script.js
  ```
- **Website:** https://k6.io/

### Locust
- **Description:** Python-based load testing
- **Installation:**
  ```bash
  pip install locust
  ```
- **Features:** Distributed testing, web UI
- **Website:** https://locust.io/

### fio
- **Description:** Storage benchmarking
- **Installation:**
  ```bash
  brew install fio
  ```
- **Usage:** Run in Kubernetes pods to test storage performance
- **Website:** https://fio.readthedocs.io/

## Recommended Tool Stack for ML Infrastructure

### Minimum Viable Stack
1. kubectl, kubectx, kubens
2. Helm
3. Prometheus + Grafana
4. Istio or Linkerd
5. Velero
6. ArgoCD or Flux

### Production Stack
1. All minimum viable tools
2. operator-sdk (for custom operators)
3. NVIDIA GPU Operator
4. KEDA
5. Karpenter
6. Falco
7. OPA Gatekeeper
8. Cert-manager
9. External Secrets Operator
10. KubeFlow or Ray
11. Chaos Mesh
12. Trivy + Cosign

### Development Stack
1. kubectl, kubectx, k9s
2. Skaffold or Tilt
3. Lens
4. kubeval/kubeconform
5. kube-score
6. stern
7. krew + useful plugins

## Installation Script

```bash
#!/bin/bash
# Install essential Kubernetes tools on macOS

# Core tools
brew install kubectl kubectx stern k9s helm

# Development
brew install skaffold operator-sdk kubebuilder

# Security
brew install trivy cosign

# GitOps
brew install argocd fluxcd/tap/flux

# Utilities
brew install krew
kubectl krew install ctx ns tree neat view-secret

# Service mesh
curl -L https://istio.io/downloadIstio | sh -

echo "Installation complete! Don't forget to:"
echo "1. Configure kubectl with your cluster"
echo "2. Install NVIDIA GPU Operator if using GPUs"
echo "3. Set up Prometheus/Grafana for monitoring"
echo "4. Configure backup with Velero"
```

## Tool Selection Criteria

When choosing tools:
1. **Community support:** Active development and community
2. **CNCF status:** Graduated > Incubating > Sandbox > Non-CNCF
3. **Production readiness:** Used by large organizations
4. **Learning curve:** Balance features vs complexity
5. **Integration:** Works with existing stack
6. **Cost:** Open source preferred, commercial for critical features
7. **Vendor lock-in:** Avoid proprietary solutions where possible

---

**Note:** Tool versions and installation methods change frequently. Always check official documentation for the latest instructions.

**Updated:** 2025-10
**Module:** 201 - Advanced Kubernetes and Cloud-Native Architecture
