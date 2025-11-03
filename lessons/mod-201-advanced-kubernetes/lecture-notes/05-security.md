# Lecture 05: Kubernetes Security Best Practices

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement comprehensive RBAC policies for multi-tenant ML platforms with principle of least privilege
- Configure Pod Security Standards (PSS) and Pod Security Admission to enforce security baselines
- Implement network policies for zero-trust networking and microsegmentation of ML workloads
- Manage secrets securely using Kubernetes Secrets, external secret managers, and encryption at rest
- Conduct security scanning and vulnerability assessment for container images and dependencies
- Implement runtime security monitoring and anomaly detection for ML workloads
- Design audit logging and compliance frameworks for regulated ML environments
- Evaluate and mitigate security risks specific to ML infrastructure including model theft and data exfiltration

## Table of Contents
1. [Security Principles for ML Infrastructure](#principles)
2. [Role-Based Access Control (RBAC)](#rbac)
3. [Pod Security Standards](#pod-security)
4. [Network Policies](#network-policies)
5. [Secrets Management](#secrets)
6. [Image Security](#image-security)
7. [Runtime Security](#runtime-security)
8. [Compliance and Audit](#compliance)

## Security Principles for ML Infrastructure {#principles}

### The ML Security Challenge

ML workloads introduce unique security considerations:

- **Data sensitivity:** Training data often contains PII or proprietary information
- **Model IP protection:** Trained models represent valuable intellectual property
- **Resource costs:** GPU resources are expensive targets for cryptomining
- **Supply chain:** Dependencies on models, datasets, and libraries
- **Long-running jobs:** Training jobs run for days/weeks, increasing attack surface
- **Multi-tenancy:** Multiple teams sharing infrastructure

### Defense in Depth

```
┌─────────────────────────────────────────────────┐
│  Layer 7: Audit & Compliance                    │
├─────────────────────────────────────────────────┤
│  Layer 6: Runtime Security & Monitoring         │
├─────────────────────────────────────────────────┤
│  Layer 5: Application Security (Code, Deps)     │
├─────────────────────────────────────────────────┤
│  Layer 4: Pod Security (PSA, SecurityContext)   │
├─────────────────────────────────────────────────┤
│  Layer 3: Network Security (Policies, mTLS)     │
├─────────────────────────────────────────────────┤
│  Layer 2: Identity & Access (RBAC, OIDC)        │
├─────────────────────────────────────────────────┤
│  Layer 1: Infrastructure (Node Security, etcd)  │
└─────────────────────────────────────────────────┘
```

### Security Principles

1. **Least Privilege:** Grant minimum permissions needed
2. **Zero Trust:** Never trust, always verify
3. **Defense in Depth:** Multiple security layers
4. **Secure by Default:** Opt-in for elevated privileges
5. **Audit Everything:** Comprehensive logging
6. **Separation of Duties:** No single point of compromise
7. **Immutability:** Use immutable infrastructure

## Role-Based Access Control (RBAC) {#rbac}

### RBAC Components

**Subjects:**
- User accounts
- Service accounts
- Groups

**Resources:**
- Pods, Deployments, Services, etc.
- Custom resources (CRDs)

**Verbs:**
- get, list, watch
- create, update, patch, delete
- exec, logs, portforward

### Roles and ClusterRoles

**Role (namespace-scoped):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-developer
  namespace: ml-team
rules:
# Read access to pods, deployments, services
- apiGroups: ["", "apps"]
  resources: ["pods", "deployments", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
# Full access to training jobs
- apiGroups: ["ml.example.com"]
  resources: ["trainingjobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
# Read logs
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get", "list"]
# No exec or port-forward for security
```

**ClusterRole (cluster-wide):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ml-admin
rules:
# Full access to ML resources across namespaces
- apiGroups: ["ml.example.com"]
  resources: ["*"]
  verbs: ["*"]
# Manage persistent volumes
- apiGroups: [""]
  resources: ["persistentvolumes", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "delete"]
# Manage storage classes
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "list", "watch"]
```

### RoleBindings

**RoleBinding (namespace-scoped):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ml-developers-binding
  namespace: ml-team
subjects:
# Bind to users
- kind: User
  name: alice@example.com
  apiGroup: rbac.authorization.k8s.io
- kind: User
  name: bob@example.com
  apiGroup: rbac.authorization.k8s.io
# Bind to groups
- kind: Group
  name: ml-engineers
  apiGroup: rbac.authorization.k8s.io
# Bind to service accounts
- kind: ServiceAccount
  name: ci-pipeline
  namespace: ml-team
roleRef:
  kind: Role
  name: ml-developer
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRoleBinding (cluster-wide):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ml-admins-binding
subjects:
- kind: Group
  name: ml-admins
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: ml-admin
  apiGroup: rbac.authorization.k8s.io
```

### Service Accounts for Workloads

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: training-job-sa
  namespace: ml-team
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: training-job-role
  namespace: ml-team
rules:
# Access to read config and secrets
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get"]
  resourceNames: ["training-config", "model-credentials"]
# Create pods for distributed training
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch", "create"]
# Update training job status
- apiGroups: ["ml.example.com"]
  resources: ["trainingjobs/status"]
  verbs: ["get", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: training-job-binding
  namespace: ml-team
subjects:
- kind: ServiceAccount
  name: training-job-sa
  namespace: ml-team
roleRef:
  kind: Role
  name: training-job-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
  namespace: ml-team
spec:
  serviceAccountName: training-job-sa
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
```

### RBAC Patterns for ML Teams

**Pattern 1: Multi-Tenant ML Platform**

```yaml
# Data Science Team - Experiment and Train
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: data-scientist
  namespace: ds-team
rules:
- apiGroups: ["ml.example.com"]
  resources: ["trainingjobs", "notebooks"]
  verbs: ["get", "list", "watch", "create", "update", "delete"]
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["get", "list", "create"]
  # Limit PVC size with admission controller
---
# ML Engineering Team - Deploy Models
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer
  namespace: ml-production
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update"]
---
# SRE Team - Monitor and Troubleshoot
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ml-sre
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "events"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
  # Allow exec for troubleshooting
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
```

**Pattern 2: CI/CD Pipeline Service Account**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-cd-pipeline
  namespace: ml-team
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ci-cd-deployer
  namespace: ml-team
rules:
# Deploy applications
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "create", "update", "patch"]
# Manage services
- apiGroups: [""]
  resources: ["services", "configmaps"]
  verbs: ["get", "list", "create", "update", "patch"]
# Read secrets (but not list all secrets)
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["docker-registry-creds"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-cd-binding
  namespace: ml-team
subjects:
- kind: ServiceAccount
  name: ci-cd-pipeline
  namespace: ml-team
roleRef:
  kind: Role
  name: ci-cd-deployer
  apiGroup: rbac.authorization.k8s.io
```

### Testing RBAC

```bash
# Check if user can perform action
kubectl auth can-i create trainingjobs --namespace=ml-team --as=alice@example.com

# Check all permissions for user
kubectl auth can-i --list --namespace=ml-team --as=alice@example.com

# Impersonate user for testing
kubectl get pods --namespace=ml-team --as=alice@example.com

# Check service account permissions
kubectl auth can-i create pods --namespace=ml-team --as=system:serviceaccount:ml-team:training-job-sa
```

## Pod Security Standards {#pod-security}

### Pod Security Admission (PSA)

PSA replaced PodSecurityPolicies in Kubernetes 1.25. Three levels:

1. **Privileged:** Unrestricted (default)
2. **Baseline:** Minimally restrictive, prevents known privilege escalations
3. **Restricted:** Heavily restricted, follows hardening best practices

### Namespace-Level Enforcement

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-production
  labels:
    # Enforce restricted policy
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest

    # Audit baseline violations
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/audit-version: latest

    # Warn on privileged attempts
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

### Security Context

**Pod-level:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-training-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /home/user/.cache
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

### Restricted Profile Requirements

```yaml
# Compliant with restricted profile
apiVersion: v1
kind: Pod
metadata:
  name: restricted-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:v1
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

### Handling GPU Workloads

GPUs require device access, which conflicts with restricted profile:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-training
  namespace: ml-gpu-workloads
spec:
  # GPU pods need some privileges
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
    # Required for GPU access
    supplementalGroups: [44]  # video group
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3-cudnn8
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
        add:
        - SYS_ADMIN  # Required for NVIDIA driver
      # Can't use readOnlyRootFilesystem with GPU
    resources:
      limits:
        nvidia.com/gpu: 1
```

**Solution: Use dedicated namespace with baseline policy:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-gpu-workloads
  labels:
    pod-security.kubernetes.io/enforce: baseline  # Less restrictive
    pod-security.kubernetes.io/enforce-version: latest
```

## Network Policies {#network-policies}

### Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: ml-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Allow Specific Traffic

```yaml
# Model servers accept traffic from API gateway only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: model-server-policy
  namespace: ml-production
spec:
  podSelector:
    matchLabels:
      app: model-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from API gateway
  - from:
    - namespaceSelector:
        matchLabels:
          name: gateway
      podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  # Allow from Prometheus
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
      podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 9090  # Metrics endpoint
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # Allow to feature store
  - to:
    - podSelector:
        matchLabels:
          app: feature-store
    ports:
    - protocol: TCP
      port: 6379
  # Allow to S3 (egress to internet)
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### Training Job Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: training-job-policy
  namespace: ml-training
spec:
  podSelector:
    matchLabels:
      job-type: training
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Workers communicate with each other
  - from:
    - podSelector:
        matchLabels:
          job-type: training
    ports:
    - protocol: TCP
      port: 23456  # Training communication port
  egress:
  # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  # Workers communicate with each other
  - to:
    - podSelector:
        matchLabels:
          job-type: training
    ports:
    - protocol: TCP
      port: 23456
  # Access to data storage
  - to:
    - podSelector:
        matchLabels:
          app: nfs-server
    ports:
    - protocol: TCP
      port: 2049
  # HTTPS for downloading dependencies
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

### Egress Control for Data Exfiltration Prevention

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: prevent-exfiltration
  namespace: ml-production
spec:
  podSelector:
    matchLabels:
      data-sensitive: "true"
  policyTypes:
  - Egress
  egress:
  # Allow only specific destinations
  - to:
    # Internal feature store
    - podSelector:
        matchLabels:
          app: feature-store
  - to:
    # Specific S3 buckets via gateway
    - podSelector:
        matchLabels:
          app: s3-gateway
    ports:
    - protocol: TCP
      port: 443
  # DNS
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # No general internet egress!
```

## Secrets Management {#secrets}

### Kubernetes Secrets

**Best Practices:**
- Never commit secrets to git
- Use separate secrets per environment
- Rotate secrets regularly
- Limit secret access via RBAC
- Encrypt secrets at rest

**Creating Secrets:**

```bash
# From literal values
kubectl create secret generic model-api-key \
    --from-literal=api-key=abc123xyz \
    --namespace=ml-production

# From file
kubectl create secret generic model-config \
    --from-file=config.json \
    --namespace=ml-production

# Docker registry secret
kubectl create secret docker-registry regcred \
    --docker-server=https://index.docker.io/v1/ \
    --docker-username=myuser \
    --docker-password=mypass \
    --docker-email=user@example.com
```

**Using Secrets:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: model-server
spec:
  containers:
  - name: server
    image: model-server:v1
    env:
    # Environment variable from secret
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: model-api-key
          key: api-key
    # Projected into files
    volumeMounts:
    - name: config
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config
    secret:
      secretName: model-config
      defaultMode: 0400  # Read-only
  imagePullSecrets:
  - name: regcred
```

### External Secrets Operator

Integrate with external secret managers (AWS Secrets Manager, HashiCorp Vault, etc.):

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
  namespace: ml-production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: model-credentials
  namespace: ml-production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets
    kind: SecretStore
  target:
    name: model-credentials
    creationPolicy: Owner
  data:
  - secretKey: api-key
    remoteRef:
      key: ml-production/model-api-key
  - secretKey: database-password
    remoteRef:
      key: ml-production/db-password
```

### Sealed Secrets

Encrypt secrets for git storage:

```bash
# Install kubeseal
brew install kubeseal

# Create regular secret
kubectl create secret generic mysecret \
    --from-literal=password=mypass \
    --dry-run=client -o yaml > secret.yaml

# Seal it
kubeseal < secret.yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to git
# Apply to cluster
kubectl apply -f sealed-secret.yaml
# Controller decrypts and creates secret
```

## Image Security {#image-security}

### Image Scanning

**Trivy for vulnerability scanning:**

```bash
# Scan image
trivy image pytorch/pytorch:1.12.0-cuda11.3

# Scan and fail on HIGH/CRITICAL
trivy image --severity HIGH,CRITICAL --exit-code 1 myimage:v1

# Scan in CI/CD
```

**Integration with admission controller:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trivy-config
data:
  config.yaml: |
    vulnerabilityReports:
      scanners:
      - Trivy
      severity: HIGH,CRITICAL
```

### Image Signing with Cosign

```bash
# Sign image
cosign sign --key cosign.key myregistry/myimage:v1

# Verify signature
cosign verify --key cosign.pub myregistry/myimage:v1

# Create Kubernetes policy to require signatures
```

### Admission Controller for Image Policy

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-policy
webhooks:
- name: image-policy.example.com
  admissionReviewVersions: ["v1"]
  clientConfig:
    service:
      name: image-policy-webhook
      namespace: security
      path: /validate
  rules:
  - operations: ["CREATE", "UPDATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  failurePolicy: Fail
  sideEffects: None
  # Policy checks:
  # - Image from approved registry
  # - Image signed
  # - No vulnerabilities above threshold
  # - No latest tag
```

### Allowed Registries

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
spec:
  containers:
  # ✓ Allowed - internal registry
  - name: app
    image: internal.registry.example.com/pytorch:1.12.0

  # ✗ Blocked - external registry
  # - name: app
  #   image: random.docker.io/suspicious:latest

  # ✗ Blocked - latest tag
  # - name: app
  #   image: internal.registry.example.com/app:latest
```

## Runtime Security {#runtime-security}

### Falco for Runtime Detection

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules
  namespace: security
data:
  custom-rules.yaml: |
    # Detect crypto mining
    - rule: Detect Crypto Mining
      desc: Detect cryptocurrency mining activity
      condition: >
        spawned_process and
        proc.name in (xmrig, minerd, cgminer, ethminer)
      output: >
        Crypto mining detected
        (user=%user.name command=%proc.cmdline container=%container.name)
      priority: CRITICAL

    # Detect unexpected network connections
    - rule: Unexpected Outbound Connection
      desc: Detect outbound connections from ML pods
      condition: >
        outbound and
        container.label.app=model-server and
        not fd.sip in (allowed_ips)
      output: >
        Unexpected outbound connection
        (connection=%fd.name user=%user.name container=%container.name)
      priority: WARNING

    # Detect file access to model files
    - rule: Model File Access
      desc: Detect unauthorized access to model files
      condition: >
        open_read and
        fd.name glob /models/* and
        not proc.name in (model-server, backup-service)
      output: >
        Unauthorized model file access
        (file=%fd.name process=%proc.name user=%user.name)
      priority: WARNING
```

### AppArmor

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secured-pod
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-apparmor-example
spec:
  containers:
  - name: app
    image: myapp:v1
```

### seccomp Profiles

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-pod
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/audit.json
  containers:
  - name: app
    image: myapp:v1
```

## Compliance and Audit {#compliance}

### Audit Logging

```yaml
apiVersion: v1
kind: Policy
rules:
# Log all requests to secrets
- level: RequestResponse
  resources:
  - group: ""
    resources: ["secrets"]

# Log metadata for training jobs
- level: Metadata
  resources:
  - group: "ml.example.com"
    resources: ["trainingjobs"]

# Log all authentication
- level: Request
  userGroups: ["system:authenticated"]
```

### OPA Gatekeeper for Policy Enforcement

```yaml
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
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ml-resource-labels
spec:
  match:
    kinds:
    - apiGroups: ["ml.example.com"]
      kinds: ["TrainingJob"]
  parameters:
    labels:
    - "team"
    - "cost-center"
    - "environment"
```

### Compliance Scanning

```bash
# kubesec - Security risk analysis
kubesec scan deployment.yaml

# kube-bench - CIS Kubernetes Benchmark
kube-bench run --targets master,node

# kube-hunter - Penetration testing
kube-hunter --remote <cluster-ip>
```

## Summary

Key takeaways:

1. **RBAC** provides fine-grained access control for users and service accounts
2. **Pod Security Standards** enforce security best practices at pod level
3. **Network Policies** control traffic flow between pods and external systems
4. **Secrets management** requires external secret stores for production
5. **Image security** involves scanning, signing, and policy enforcement
6. **Runtime security** detects anomalous behavior in running containers
7. **Compliance** requires comprehensive audit logging and policy enforcement

## Further Reading

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Falco Rules](https://falco.org/docs/rules/)

## Next Steps

Next lecture: **Multi-Cluster Architecture** - Learn how to design and manage multi-cluster Kubernetes deployments for ML workloads.
