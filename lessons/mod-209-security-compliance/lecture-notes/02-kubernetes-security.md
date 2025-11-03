# Lecture 2: Kubernetes Security for ML Workloads

## Learning Objectives

By the end of this lecture, you will be able to:

- Design secure Kubernetes clusters with RBAC, Pod Security Standards, Network Policies, and admission controllers preventing unauthorized access and malicious workloads
- Implement pod security contexts with user namespaces, seccomp profiles, AppArmor/SELinux policies, and capability dropping minimizing container privileges
- Configure network security with NetworkPolicies (Calico/Cilium), service mesh mTLS (Istio), and egress controls restricting pod-to-pod and external communication
- Architect secrets management integrating External Secrets Operator, Vault, or cloud KMS ensuring secure credential handling without hardcoded secrets
- Design admission control pipelines using OPA Gatekeeper or Kyverno validating pod specifications, enforcing policies, and mutating resources for security compliance
- Implement image security with vulnerability scanning (Trivy, Clair), image signing (Cosign), and private registries with access controls
- Build security monitoring and audit logging using Falco for runtime security, audit logs for API access, and SIEM integration for threat detection
- Architect multi-tenant Kubernetes security with namespace isolation, resource quotas, RBAC boundaries, and PodSecurityPolicies/Standards ensuring tenant separation

## Table of Contents
1. [Introduction to Kubernetes Security](#introduction-to-kubernetes-security)
2. [Authentication and Identity Management](#authentication-and-identity-management)
3. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
4. [Pod Security Standards](#pod-security-standards)
5. [Network Policies](#network-policies)
6. [Secrets Management](#secrets-management)
7. [Admission Controllers and Policy Enforcement](#admission-controllers-and-policy-enforcement)
8. [Container Security](#container-security)
9. [Workload Isolation](#workload-isolation)
10. [Security Monitoring and Auditing](#security-monitoring-and-auditing)
11. [Best Practices for ML Workloads](#best-practices-for-ml-workloads)

## Introduction to Kubernetes Security

Kubernetes has become the de facto platform for deploying ML workloads at scale. However, its flexibility and power come with significant security responsibilities. As a Senior AI Infrastructure Engineer, you must understand how to secure Kubernetes clusters running sensitive ML workloads.

### The Kubernetes Security Challenge

ML workloads on Kubernetes present unique security challenges:

1. **Long-Running Training Jobs**: Multi-day jobs increase exposure window
2. **High Resource Requirements**: GPUs and large memory allocations are attractive targets
3. **Data Sensitivity**: Training data often contains PII or proprietary information
4. **Model IP Protection**: Trained models are valuable intellectual property
5. **Multi-Tenancy**: Multiple teams sharing infrastructure requires strong isolation
6. **External Data Access**: ML pipelines frequently access external data sources

### Kubernetes Security Domains

```
┌─────────────────────────────────────────────────────────────┐
│                 Kubernetes Security Layers                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Layer 5: Security Monitoring & Audit Logging      │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Layer 4: Application Security (Workloads)         │    │
│  │  - Pod Security Standards                          │    │
│  │  - Runtime Security                                 │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Layer 3: Network Security                         │    │
│  │  - Network Policies                                 │    │
│  │  - Service Mesh (mTLS)                             │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Layer 2: Access Control                           │    │
│  │  - RBAC                                             │    │
│  │  - Admission Controllers                            │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Layer 1: Authentication                           │    │
│  │  - API Server Authentication                       │    │
│  │  - Service Account Management                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The 4Cs of Cloud Native Security

Security in Kubernetes follows the 4Cs model:

1. **Code**: Application and ML model code security
2. **Container**: Container image security and runtime protection
3. **Cluster**: Kubernetes cluster configuration and security
4. **Cloud**: Infrastructure and cloud provider security

Each layer builds upon and depends on the security of the layers below it.

## Authentication and Identity Management

Authentication is the foundation of Kubernetes security. Understanding authentication mechanisms is crucial for building secure ML platforms.

### Kubernetes Authentication Methods

**1. X.509 Client Certificates**

The most common method for user authentication:

```bash
# Generate user certificate
openssl genrsa -out ml-engineer.key 2048
openssl req -new -key ml-engineer.key -out ml-engineer.csr \
  -subj "/CN=ml-engineer/O=ml-team"

# Sign certificate with cluster CA (typically done by cluster admin)
openssl x509 -req -in ml-engineer.csr \
  -CA /etc/kubernetes/pki/ca.crt \
  -CAkey /etc/kubernetes/pki/ca.key \
  -CAcreateserial \
  -out ml-engineer.crt -days 365

# Create kubeconfig
kubectl config set-credentials ml-engineer \
  --client-certificate=ml-engineer.crt \
  --client-key=ml-engineer.key

kubectl config set-context ml-engineer-context \
  --cluster=production-cluster \
  --namespace=ml-training \
  --user=ml-engineer
```

**2. Service Accounts**

For pods and automation:

```yaml
# Service account for ML training jobs
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-training
  annotations:
    description: "Service account for ML training workloads"
---
# Use service account in pod
apiVersion: v1
kind: Pod
metadata:
  name: model-training
  namespace: ml-training
spec:
  serviceAccountName: ml-training-sa
  automountServiceAccountToken: true  # Explicitly control token mounting
  containers:
  - name: trainer
    image: ml-training:v1.0
    # Pod now has credentials to access Kubernetes API
```

**Best Practices for Service Accounts**:

```yaml
# Disable default service account auto-mounting
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
  namespace: ml-training
automountServiceAccountToken: false

---
# Create specific service accounts for each workload type
apiVersion: v1
kind: ServiceAccount
metadata:
  name: notebook-sa
  namespace: ml-training
  labels:
    app: jupyter-notebook
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: training-job-sa
  namespace: ml-training
  labels:
    app: training-job
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: model-serving-sa
  namespace: ml-production
  labels:
    app: model-serving
```

**3. OIDC Integration**

For enterprise SSO integration:

```yaml
# API server configuration for OIDC
apiVersion: v1
kind: Config
clusters:
- name: production
  cluster:
    server: https://k8s.example.com
users:
- name: oidc-user
  user:
    auth-provider:
      name: oidc
      config:
        client-id: kubernetes
        client-secret: ${OIDC_CLIENT_SECRET}
        id-token: ${OIDC_ID_TOKEN}
        idp-issuer-url: https://sso.example.com
        refresh-token: ${OIDC_REFRESH_TOKEN}
```

### Identity Management for ML Workloads

**Workload Identity Pattern**:

```yaml
# Map service accounts to cloud provider identities
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-training
  annotations:
    # GCP Workload Identity
    iam.gke.io/gcp-service-account: ml-training@project.iam.gserviceaccount.com
    # AWS IAM Roles for Service Accounts (IRSA)
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/ml-training-role
    # Azure Workload Identity
    azure.workload.identity/client-id: "12345678-1234-1234-1234-123456789012"
```

This allows ML workloads to securely access cloud resources (S3, GCS, etc.) without embedding credentials.

## Role-Based Access Control (RBAC)

RBAC is the primary authorization mechanism in Kubernetes. Proper RBAC configuration is essential for secure multi-tenant ML platforms.

### RBAC Concepts

**Core Objects**:
- **Role/ClusterRole**: Define permissions
- **RoleBinding/ClusterRoleBinding**: Grant permissions to users/service accounts
- **Subjects**: Users, groups, or service accounts
- **Resources**: Kubernetes objects (pods, secrets, etc.)
- **Verbs**: Actions (get, list, create, delete, etc.)

### RBAC for ML Platform Personas

**1. Data Scientist Role**

Data scientists need to create notebooks, run experiments, but shouldn't access production:

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: data-scientist
  namespace: ml-training
rules:
# Notebook management
- apiGroups: ["kubeflow.org"]
  resources: ["notebooks"]
  verbs: ["create", "get", "list", "delete", "update"]

# Experiment tracking
- apiGroups: ["kubeflow.org"]
  resources: ["experiments", "trials"]
  verbs: ["create", "get", "list"]

# View pods and logs (for debugging)
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]

# Create training jobs
- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["create", "get", "list", "delete"]

# Access to ConfigMaps for configuration (but not Secrets)
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]

# No access to secrets
# No ability to modify RBAC
# No access to production namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: data-scientist-binding
  namespace: ml-training
subjects:
- kind: Group
  name: data-scientists
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: data-scientist
  apiGroup: rbac.authorization.k8s.io
```

**2. ML Engineer Role**

ML Engineers need broader access including staging deployments:

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer
  namespace: ml-staging
rules:
# Full control of ML resources in staging
- apiGroups: ["serving.kubeflow.org"]
  resources: ["inferenceservices"]
  verbs: ["*"]

# Deployment management
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["*"]

# Service management
- apiGroups: [""]
  resources: ["services"]
  verbs: ["*"]

# Access to secrets (for staging only)
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "create", "update"]

# Resource monitoring
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch", "delete"]

# HPA management
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ml-engineer-binding
  namespace: ml-staging
subjects:
- kind: Group
  name: ml-engineers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: ml-engineer
  apiGroup: rbac.authorization.k8s.io
```

**3. ML SRE/Platform Role**

Platform team has broader access but with audit logging:

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ml-sre
rules:
# Cluster-wide read access
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]

# Node management
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch", "update", "patch"]

# Namespace management
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["*"]

# Production deployment (with approval workflow enforced elsewhere)
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["*"]

# Emergency access to secrets (heavily audited)
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["*"]

# RBAC management (for onboarding users)
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["roles", "rolebindings"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ml-sre-binding
subjects:
- kind: Group
  name: ml-sre-team
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: ml-sre
  apiGroup: rbac.authorization.k8s.io
```

**4. Service Account for Training Jobs**

Minimal permissions for training workloads:

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: training-job-role
  namespace: ml-training
rules:
# Read-only access to ConfigMaps for training config
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]

# Read secrets (for dataset credentials)
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["training-data-credentials", "model-registry-credentials"]

# Create pods for distributed training
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "get", "list"]

# No ability to modify RBAC or access other workloads
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: training-job-binding
  namespace: ml-training
subjects:
- kind: ServiceAccount
  name: ml-training-sa
  namespace: ml-training
roleRef:
  kind: Role
  name: training-job-role
  apiGroup: rbac.authorization.k8s.io
```

### RBAC Best Practices

**1. Principle of Least Privilege**

```yaml
# Bad: Overly permissive
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# Good: Specific permissions
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
  # Only in specific namespace via Role (not ClusterRole)
```

**2. Use Groups Instead of Individual Users**

```yaml
# Bad: Individual user bindings (hard to manage)
subjects:
- kind: User
  name: alice@example.com
- kind: User
  name: bob@example.com
- kind: User
  name: charlie@example.com

# Good: Group-based bindings
subjects:
- kind: Group
  name: ml-engineers
  apiGroup: rbac.authorization.k8s.io
```

**3. Separate Roles by Environment**

```yaml
# Separate roles for dev, staging, production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer-dev
  namespace: ml-dev
  # Permissive rules for development
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer-staging
  namespace: ml-staging
  # Moderate restrictions for staging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer-production
  namespace: ml-production
  # Strict rules, possibly read-only for most engineers
```

**4. Regular RBAC Audits**

```bash
# Audit script to review RBAC permissions
#!/bin/bash

# List all rolebindings with subjects
kubectl get rolebindings --all-namespaces -o json | \
  jq -r '.items[] | "\(.metadata.namespace) | \(.metadata.name) | \(.subjects)"'

# Find overly permissive roles
kubectl get roles --all-namespaces -o json | \
  jq -r '.items[] | select(.rules[] | .verbs[] == "*" or .resources[] == "*") | "\(.metadata.namespace)/\(.metadata.name)"'

# List users with cluster-admin
kubectl get clusterrolebindings -o json | \
  jq -r '.items[] | select(.roleRef.name == "cluster-admin") | "\(.subjects)"'
```

## Pod Security Standards

Pod Security Standards (PSS) define levels of pod security restrictions. They replaced Pod Security Policies in Kubernetes 1.25+.

### Three Pod Security Levels

**1. Privileged**: Unrestricted (no restrictions)
**2. Baseline**: Minimally restrictive, prevents known privilege escalations
**3. Restricted**: Heavily restricted, follows hardening best practices

### Implementing Pod Security Standards

**Namespace-Level Configuration**:

```yaml
# Apply pod security at namespace level
apiVersion: v1
kind: Namespace
metadata:
  name: ml-production
  labels:
    # Enforce restricted standard
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest

    # Warn if baseline violations
    pod-security.kubernetes.io/warn: baseline
    pod-security.kubernetes.io/warn-version: latest

    # Audit all privileged attempts
    pod-security.kubernetes.io/audit: privileged
    pod-security.kubernetes.io/audit-version: latest
---
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training
  labels:
    # More permissive for training (may need specific capabilities)
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/warn: restricted
---
apiVersion: v1
kind: Namespace
metadata:
  name: ml-dev
  labels:
    # Most permissive for development
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/warn: baseline
```

### Restricted Pod Configuration

Example of a pod that meets restricted standards:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-ml-training
  namespace: ml-production
spec:
  # Use specific service account
  serviceAccountName: ml-training-sa
  automountServiceAccountToken: true

  # Security context at pod level
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:
  - name: trainer
    image: ml-training:v1.0

    # Security context at container level
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true

    # Resource limits (required by restricted standard)
    resources:
      limits:
        cpu: "4"
        memory: "16Gi"
        nvidia.com/gpu: "1"
      requests:
        cpu: "2"
        memory: "8Gi"
        nvidia.com/gpu: "1"

    # Use writable volume for model output
    volumeMounts:
    - name: model-output
      mountPath: /models
    - name: tmp
      mountPath: /tmp

  volumes:
  - name: model-output
    persistentVolumeClaim:
      claimName: model-storage
  - name: tmp
    emptyDir: {}
```

### Common PSS Violations and Fixes

**Issue 1: Running as Root**

```yaml
# Violation
spec:
  containers:
  - name: app
    image: my-image

# Fix: Explicitly run as non-root
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: my-image
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
```

**Issue 2: Privilege Escalation**

```yaml
# Violation
spec:
  containers:
  - name: app
    image: my-image
    # Missing allowPrivilegeEscalation: false

# Fix
spec:
  containers:
  - name: app
    image: my-image
    securityContext:
      allowPrivilegeEscalation: false
```

**Issue 3: Unsafe Capabilities**

```yaml
# Violation
spec:
  containers:
  - name: app
    image: my-image
    securityContext:
      capabilities:
        add:
        - NET_ADMIN
        - SYS_ADMIN

# Fix: Drop all, add only what's needed
spec:
  containers:
  - name: app
    image: my-image
    securityContext:
      capabilities:
        drop:
        - ALL
        # Add specific capabilities only if absolutely necessary
```

**Issue 4: Host Namespace Sharing**

```yaml
# Violation: Sharing host network/PID/IPC
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true

# Fix: Use isolated namespaces
spec:
  hostNetwork: false
  hostPID: false
  hostIPC: false
```

### GPU Workloads and Security

ML workloads often require GPUs, which present security challenges:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-training-secure
spec:
  # Run as non-root even with GPU
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000

  containers:
  - name: trainer
    image: pytorch-gpu:v1.0

    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      # Note: readOnlyRootFilesystem may not work with some GPU drivers
      # Test thoroughly

    resources:
      limits:
        nvidia.com/gpu: "1"  # Request GPU

    # GPU device plugin handles device access
    # No need for privileged mode
```

### Runtime Security with Seccomp and AppArmor

**Seccomp Profiles**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault  # Use container runtime's default profile
  containers:
  - name: app
    image: my-image
    securityContext:
      seccompProfile:
        type: Localhost
        localhostProfile: profiles/custom-ml-profile.json
```

Custom seccomp profile for ML workloads:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "mmap", "mprotect", "munmap", "brk",
        "futex", "clone", "execve", "exit_group",
        "socket", "connect", "sendto", "recvfrom"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

## Network Policies

Network Policies control traffic flow between pods, providing micro-segmentation.

### Default Deny Policy

Start with default deny, then allow specific traffic:

```yaml
---
# Default deny all ingress and egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: ml-training
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### ML Platform Network Policies

**1. Training Jobs Policy**

```yaml
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: training-job-policy
  namespace: ml-training
spec:
  podSelector:
    matchLabels:
      app: training-job
  policyTypes:
  - Ingress
  - Egress

  # No ingress (jobs don't receive traffic)
  ingress: []

  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53

  # Allow access to data storage (S3, GCS)
  - to:
    - podSelector:
        matchLabels:
          app: data-gateway
    ports:
    - protocol: TCP
      port: 443

  # Allow access to model registry
  - to:
    - podSelector:
        matchLabels:
          app: model-registry
    ports:
    - protocol: TCP
      port: 8080

  # Allow internet access for pip installs (consider restricting)
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

**2. Model Serving Policy**

```yaml
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: model-serving-policy
  namespace: ml-production
spec:
  podSelector:
    matchLabels:
      app: model-serving
  policyTypes:
  - Ingress
  - Egress

  ingress:
  # Allow traffic from ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080

  # Allow monitoring (Prometheus)
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Metrics port

  egress:
  # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53

  # Feature store access
  - to:
    - podSelector:
        matchLabels:
          app: feature-store
    ports:
    - protocol: TCP
      port: 6379  # Redis

  # Model storage access (for dynamic model loading)
  - to:
    - podSelector:
        matchLabels:
          app: model-registry
    ports:
    - protocol: TCP
      port: 8080
```

**3. Namespace Isolation**

```yaml
---
# Isolate production from non-production
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: production-isolation
  namespace: ml-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

  ingress:
  # Only allow ingress from production namespace and ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          environment: production
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx

  egress:
  # Allow egress only to production services and external APIs
  - to:
    - namespaceSelector:
        matchLabels:
          environment: production
  - to:
    - namespaceSelector: {}
      podSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS for external APIs
```

### Testing Network Policies

```bash
# Test connectivity from pod
kubectl run -it --rm debug \
  --image=nicolaka/netshoot \
  --namespace=ml-training \
  -- /bin/bash

# Inside pod, test connections
curl -v http://model-registry:8080/health  # Should work
curl -v http://production-service:8080     # Should be blocked
```

## Secrets Management

Proper secrets management is critical for ML workloads accessing databases, APIs, and cloud resources.

### Kubernetes Secrets Best Practices

**1. Encryption at Rest**

Enable encryption for secrets in etcd:

```yaml
# encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-key>
      - identity: {}  # Fallback for reading old secrets
```

**2. RBAC for Secrets**

```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
  namespace: ml-training
rules:
# Specific secrets only
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames:
    - "training-data-credentials"
    - "model-registry-token"
  # No "list" verb - prevents enumeration
  # No "*" in resourceNames - prevents wildcard access
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: training-secret-access
  namespace: ml-training
subjects:
- kind: ServiceAccount
  name: ml-training-sa
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

**3. External Secrets Operator**

Integrate with external secret managers:

```yaml
---
# Using External Secrets Operator with AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: ml-training
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
# External Secret definition
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: training-credentials
  namespace: ml-training
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: training-data-credentials
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: ml-training/database
      property: password
  - secretKey: s3-access-key
    remoteRef:
      key: ml-training/s3
      property: access-key
```

**4. Sealed Secrets for GitOps**

Store encrypted secrets in Git:

```bash
# Install kubeseal CLI
# Encrypt secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Sealed secret can be safely committed to Git
```

```yaml
# Original secret (never commit this)
apiVersion: v1
kind: Secret
metadata:
  name: training-api-key
  namespace: ml-training
type: Opaque
stringData:
  api-key: "super-secret-key-123"

---
# Sealed secret (safe to commit)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: training-api-key
  namespace: ml-training
spec:
  encryptedData:
    api-key: AgC7...encrypted-data...==
  template:
    type: Opaque
```

### Using Secrets in Pods

**Best Practice**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-job
spec:
  serviceAccountName: ml-training-sa
  containers:
  - name: trainer
    image: ml-training:v1.0

    # Mount secrets as files (preferred over env vars)
    volumeMounts:
    - name: credentials
      mountPath: /etc/secrets
      readOnly: true

    # Use env vars only for non-sensitive config
    env:
    - name: MODEL_REGISTRY_URL
      valueFrom:
        configMapKeyRef:
          name: ml-config
          key: registry-url

    # Avoid this: secrets in env vars are easier to leak
    # - name: API_KEY
    #   valueFrom:
    #     secretKeyRef:
    #       name: api-secret
    #       key: api-key

  volumes:
  - name: credentials
    secret:
      secretName: training-data-credentials
      defaultMode: 0400  # Read-only for owner
```

## Admission Controllers and Policy Enforcement

Admission controllers intercept requests to the Kubernetes API before objects are persisted, enabling policy enforcement.

### Built-in Admission Controllers

Key admission controllers for security:

- **NamespaceLifecycle**: Prevents deletion of system namespaces
- **LimitRanger**: Enforces resource limits
- **ServiceAccount**: Automates service account management
- **ResourceQuota**: Enforces resource quotas
- **PodSecurity**: Enforces Pod Security Standards

### Dynamic Admission Control

**OPA Gatekeeper** for policy enforcement:

```yaml
---
# Install Gatekeeper
# kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Constraint Template: Require specific labels
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
---
# Constraint: Enforce labels on ML workloads
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ml-workload-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - ml-training
      - ml-production
  parameters:
    labels:
      - "app"
      - "team"
      - "cost-center"
      - "environment"
```

**Example Policies for ML Workloads**:

```yaml
---
# Policy: Require resource limits
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequireresources
spec:
  crd:
    spec:
      names:
        kind: K8sRequireResources
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequireresources

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.cpu
          msg := sprintf("Container %v missing CPU limit", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.memory
          msg := sprintf("Container %v missing memory limit", [container.name])
        }
---
# Policy: Block privileged containers
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sBlockPrivileged
metadata:
  name: block-privileged-ml-workloads
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - ml-production
  # No parameters needed - always deny privileged
```

### Validating Webhook

Custom validation webhook example:

```python
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_pod():
    """Validate pod creation request"""
    admission_review = request.get_json()

    # Extract pod spec
    pod = admission_review['request']['object']
    pod_name = pod['metadata'].get('name', 'unknown')
    namespace = pod['metadata'].get('namespace', 'default')

    # Validation checks
    allowed = True
    status_message = "Pod allowed"

    # Check 1: Require cost-center label
    labels = pod['metadata'].get('labels', {})
    if 'cost-center' not in labels:
        allowed = False
        status_message = "Missing required label: cost-center"

    # Check 2: Validate image registry
    for container in pod['spec'].get('containers', []):
        image = container.get('image', '')
        if not image.startswith('myregistry.example.com/'):
            allowed = False
            status_message = f"Image {image} not from approved registry"
            break

    # Check 3: Ensure GPU limits match requests
    for container in pod['spec'].get('containers', []):
        resources = container.get('resources', {})
        gpu_limit = resources.get('limits', {}).get('nvidia.com/gpu')
        gpu_request = resources.get('requests', {}).get('nvidia.com/gpu')

        if gpu_limit and gpu_request and gpu_limit != gpu_request:
            allowed = False
            status_message = "GPU requests must equal limits"
            break

    # Build admission response
    admission_response = {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'uid': admission_review['request']['uid'],
            'allowed': allowed,
            'status': {
                'message': status_message
            }
        }
    }

    return jsonify(admission_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
```

## Container Security

Container security is foundational for Kubernetes security.

### Image Security

**1. Use Minimal Base Images**

```dockerfile
# Bad: Large attack surface
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY app.py .
CMD ["python3", "app.py"]

# Good: Minimal distroless image
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM gcr.io/distroless/python3-debian11
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
CMD ["app.py"]
```

**2. Image Scanning**

```yaml
# GitHub Actions workflow for image scanning
name: Container Security Scan
on: [push]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build image
        run: docker build -t ml-training:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ml-training:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Fail build on vulnerabilities

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

**3. Image Signing and Verification**

```bash
# Sign images with Cosign
export COSIGN_PASSWORD="your-password"
cosign generate-key-pair
cosign sign --key cosign.key myregistry.example.com/ml-training:v1.0

# Verify signature before deployment
cosign verify --key cosign.pub myregistry.example.com/ml-training:v1.0
```

Enforce signature verification in Kubernetes:

```yaml
# Using Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: enforce
  rules:
    - name: verify-signature
      match:
        resources:
          kinds:
            - Pod
      verifyImages:
        - imageReferences:
            - "myregistry.example.com/*"
          attestors:
            - count: 1
              entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...public key...
                      -----END PUBLIC KEY-----
```

### Runtime Security

**Falco for Runtime Monitoring**:

```yaml
# Falco rules for ML workloads
- rule: Unauthorized Process in ML Container
  desc: Detect unexpected processes in ML containers
  condition: >
    container and
    container.image.repository = "ml-training" and
    not proc.name in (python, pip, nvidia-smi, bash)
  output: >
    Unexpected process in ML container
    (user=%user.name command=%proc.cmdline container=%container.name image=%container.image)
  priority: WARNING

- rule: Sensitive File Access in ML Container
  desc: Detect access to sensitive files
  condition: >
    container and
    container.image.repository = "ml-training" and
    open_read and
    fd.name in (/etc/shadow, /etc/passwd, /root/.ssh/id_rsa)
  output: >
    Sensitive file accessed in ML container
    (user=%user.name file=%fd.name container=%container.name)
  priority: CRITICAL

- rule: Unexpected Outbound Connection
  desc: Detect unexpected network connections
  condition: >
    container and
    container.image.repository = "ml-training" and
    outbound and
    not fd.sip in (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) and
    not fd.sport in (80, 443)
  output: >
    Unexpected outbound connection from ML container
    (dest=%fd.sip:%fd.sport container=%container.name)
  priority: WARNING
```

## Workload Isolation

Proper isolation prevents workloads from interfering with or compromising each other.

### Namespace-Based Isolation

```yaml
# Separate namespaces by function and environment
---
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training-dev
  labels:
    environment: development
    function: training
    isolation: standard
---
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training-prod
  labels:
    environment: production
    function: training
    isolation: strict
---
apiVersion: v1
kind: Namespace
metadata:
  name: ml-serving-prod
  labels:
    environment: production
    function: serving
    isolation: strict
    compliance: pci-dss
```

### Node-Based Isolation

**Dedicated Node Pools**:

```yaml
# Training workloads on GPU nodes
apiVersion: v1
kind: Pod
metadata:
  name: training-job
spec:
  nodeSelector:
    workload-type: ml-training
    gpu-type: a100

  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule

  containers:
  - name: trainer
    image: ml-training:v1.0
    resources:
      limits:
        nvidia.com/gpu: "1"
```

**Node Taints for Isolation**:

```bash
# Taint nodes for specific workloads
kubectl taint nodes gpu-node-1 workload=ml-training:NoSchedule
kubectl taint nodes gpu-node-2 workload=ml-training:NoSchedule

# Only pods with matching tolerations can schedule
```

### Resource Quotas

```yaml
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ml-training-quota
  namespace: ml-training
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "500Gi"
    requests.nvidia.com/gpu: "8"
    limits.cpu: "200"
    limits.memory: "1Ti"
    limits.nvidia.com/gpu: "8"
    persistentvolumeclaims: "20"
    pods: "50"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: ml-training-limits
  namespace: ml-training
spec:
  limits:
  - max:
      cpu: "32"
      memory: "256Gi"
      nvidia.com/gpu: "4"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "4"
      memory: "16Gi"
    defaultRequest:
      cpu: "2"
      memory: "8Gi"
    type: Container
  - max:
      cpu: "64"
      memory: "512Gi"
      nvidia.com/gpu: "8"
    type: Pod
```

## Security Monitoring and Auditing

Comprehensive monitoring and auditing are essential for detecting and responding to security incidents.

### Kubernetes Audit Logging

**Audit Policy Configuration**:

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Log secret access
- level: RequestResponse
  resources:
  - group: ""
    resources: ["secrets"]

# Log RBAC changes
- level: RequestResponse
  resources:
  - group: "rbac.authorization.k8s.io"
    resources: ["roles", "rolebindings", "clusterroles", "clusterrolebindings"]

# Log pod exec/attach (potential compromise indicator)
- level: Metadata
  resources:
  - group: ""
    resources: ["pods/exec", "pods/attach", "pods/portforward"]

# Log production namespace changes
- level: RequestResponse
  namespaces: ["ml-production"]

# Don't log read-only requests to non-sensitive resources
- level: None
  verbs: ["get", "list", "watch"]
  resources:
  - group: ""
    resources: ["events", "nodes", "nodes/status"]
```

### Security Metrics and Alerting

```yaml
# ServiceMonitor for security metrics
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kube-security-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: kubernetes-security
  endpoints:
  - port: metrics
    interval: 30s
```

**Prometheus Alerts**:

```yaml
groups:
- name: kubernetes-security
  rules:

  # Alert on privileged container creation
  - alert: PrivilegedContainerCreated
    expr: |
      increase(apiserver_audit_event_total{
        verb="create",
        objectRef_resource="pods",
        objectRef_subresource="",
        requestObject_spec_containers_securityContext_privileged="true"
      }[5m]) > 0
    labels:
      severity: critical
    annotations:
      summary: "Privileged container created"
      description: "A privileged container was created in namespace {{ $labels.objectRef_namespace }}"

  # Alert on secrets access
  - alert: SecretsAccessed
    expr: |
      increase(apiserver_audit_event_total{
        verb=~"get|list",
        objectRef_resource="secrets"
      }[5m]) > 100
    labels:
      severity: warning
    annotations:
      summary: "High rate of secrets access"
      description: "{{ $labels.user_username }} accessed secrets {{ $value }} times in 5m"

  # Alert on exec into production pods
  - alert: PodExecInProduction
    expr: |
      increase(apiserver_audit_event_total{
        verb="create",
        objectRef_resource="pods",
        objectRef_subresource="exec",
        objectRef_namespace="ml-production"
      }[5m]) > 0
    labels:
      severity: high
    annotations:
      summary: "Exec into production pod"
      description: "{{ $labels.user_username }} exec'd into pod {{ $labels.objectRef_name }} in production"

  # Alert on RBAC changes
  - alert: RBACModified
    expr: |
      increase(apiserver_audit_event_total{
        verb=~"create|update|delete|patch",
        objectRef_resource=~"roles|rolebindings|clusterroles|clusterrolebindings"
      }[5m]) > 0
    labels:
      severity: high
    annotations:
      summary: "RBAC configuration modified"
      description: "{{ $labels.user_username }} modified RBAC: {{ $labels.verb }} {{ $labels.objectRef_resource }}/{{ $labels.objectRef_name }}"
```

## Best Practices for ML Workloads

### Security Checklist

Before deploying ML workloads to production:

**Infrastructure**:
- [ ] Kubernetes version up to date
- [ ] Node OS hardened and patched
- [ ] Network policies enforced
- [ ] RBAC configured with least privilege
- [ ] Audit logging enabled and monitored
- [ ] Pod Security Standards enforced

**Workloads**:
- [ ] Container images scanned and signed
- [ ] Running as non-root user
- [ ] Resource limits configured
- [ ] Secrets externalized (not in env vars)
- [ ] Read-only root filesystem where possible
- [ ] No privileged mode or host namespace access

**Operations**:
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Regular security reviews scheduled
- [ ] Backup and disaster recovery tested
- [ ] Compliance requirements validated

### Common Security Mistakes

**Mistake 1: Overly Permissive RBAC**

```yaml
# Don't do this in production
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: data-scientists
subjects:
- kind: Group
  name: data-scientists
roleRef:
  kind: ClusterRole
  name: cluster-admin  # Way too permissive!
  apiGroup: rbac.authorization.k8s.io
```

**Mistake 2: Secrets in Environment Variables**

```yaml
# Bad: Easy to leak via logs, process listing
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: api-secret
      key: key

# Good: Mount as file
volumeMounts:
- name: api-credentials
  mountPath: /etc/secrets
  readOnly: true
volumes:
- name: api-credentials
  secret:
    secretName: api-secret
    defaultMode: 0400
```

**Mistake 3: No Resource Limits**

```yaml
# Bad: Can cause resource exhaustion
spec:
  containers:
  - name: training
    image: ml-training:v1.0
    # No limits!

# Good: Limits prevent resource exhaustion
spec:
  containers:
  - name: training
    image: ml-training:v1.0
    resources:
      limits:
        cpu: "8"
        memory: "32Gi"
        nvidia.com/gpu: "1"
      requests:
        cpu: "4"
        memory: "16Gi"
        nvidia.com/gpu: "1"
```

## Summary

Kubernetes security for ML workloads requires a comprehensive approach:

1. **Authentication & Authorization**: Use RBAC with least privilege, separate roles by function and environment
2. **Pod Security**: Enforce Pod Security Standards, run as non-root, drop capabilities
3. **Network Security**: Implement network policies for micro-segmentation
4. **Secrets Management**: Use external secret managers, mount as files, never commit to Git
5. **Admission Control**: Use policy engines like OPA Gatekeeper to enforce organizational policies
6. **Container Security**: Scan images, use minimal base images, sign and verify
7. **Runtime Security**: Monitor with Falco, detect anomalous behavior
8. **Monitoring & Auditing**: Enable audit logs, create security metrics and alerts

Kubernetes security is not a one-time configuration but an ongoing process of monitoring, testing, and improvement.

## Additional Resources

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [NIST Application Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [Kubernetes Hardening Guide - NSA/CISA](https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF)

## Next Steps

- Continue to [Lecture 3: Data Security and Encryption](03-data-security.md)
- Complete Lab 1: Kubernetes Security Configuration
- Review RBAC configurations in your organization
