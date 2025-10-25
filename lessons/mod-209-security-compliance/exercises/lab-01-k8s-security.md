# Lab 1: Kubernetes Security Configuration

## Objectives
- Configure RBAC for ML workloads
- Implement Pod Security Standards
- Deploy network policies for isolation
- Set up secrets management

## Duration
4 hours

## Prerequisites
- Kubernetes cluster (minikube, kind, or cloud cluster)
- kubectl configured
- Basic Kubernetes knowledge

## Part 1: RBAC Configuration (90 minutes)

### Exercise 1.1: Create Service Accounts

Create service accounts for different ML roles:

```bash
# TODO: Create service accounts
kubectl create namespace ml-training

# TODO: Create service account for training jobs
# Hint: kubectl create serviceaccount training-job-sa -n ml-training

# TODO: Create service account for notebooks  
# TODO: Create service account for model serving
```

### Exercise 1.2: Define Roles

Create roles with minimal necessary permissions:

```yaml
# TODO: Complete this role definition
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: training-job-role
  namespace: ml-training
rules:
# TODO: Add rules for:
# - Reading ConfigMaps
# - Reading specific secrets
# - Creating pods
# - Getting pod logs
```

### Exercise 1.3: Create RoleBindings

```bash
# TODO: Bind roles to service accounts
# kubectl create rolebinding ...
```

### Verification

```bash
# Test permissions
kubectl auth can-i create pods --as=system:serviceaccount:ml-training:training-job-sa -n ml-training
kubectl auth can-i delete secrets --as=system:serviceaccount:ml-training:training-job-sa -n ml-training
```

## Part 2: Pod Security Standards (90 minutes)

### Exercise 2.1: Apply Pod Security Labels

```bash
# TODO: Label namespace with Pod Security Standards
kubectl label namespace ml-training \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/warn=restricted

# TODO: What happens when you try to create a privileged pod?
```

### Exercise 2.2: Create Compliant Pod

```yaml
# TODO: Fix this pod to comply with restricted PSS
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
spec:
  containers:
  - name: trainer
    image: python:3.11
    command: ["python", "train.py"]
# TODO: Add security context, resource limits, etc.
```

## Part 3: Network Policies (60 minutes)

### Exercise 3.1: Default Deny

```yaml
# TODO: Create default deny network policy
```

### Exercise 3.2: Allow DNS

```yaml
# TODO: Create policy to allow DNS resolution
```

### Exercise 3.3: Service-to-Service Communication

```yaml
# TODO: Create policy allowing training pods to access data service
```

### Verification

```bash
# Test connectivity
kubectl run test-pod --image=busybox -it --rm -- /bin/sh
# Try to connect to various services
```

## Part 4: Secrets Management (60 minutes)

### Exercise 4.1: Create Encrypted Secrets

```bash
# TODO: Create secret with API key
kubectl create secret generic training-api-key \
  --from-literal=api-key=YOUR_SECRET_KEY \
  -n ml-training

# TODO: Verify encryption at rest
```

### Exercise 4.2: Mount Secrets as Files

```yaml
# TODO: Create pod that mounts secrets as files (not env vars)
```

### Exercise 4.3: External Secrets (Bonus)

```yaml
# TODO: Install External Secrets Operator
# TODO: Configure SecretStore for cloud KMS
# TODO: Create ExternalSecret resource
```

## Deliverables

1. YAML files for all RBAC resources
2. Network policy configurations
3. Screenshots of verification commands
4. Document security improvements made
5. List of security vulnerabilities found (if any)

## Assessment Criteria

- [ ] Service accounts created with minimal permissions
- [ ] Roles follow principle of least privilege
- [ ] Pods comply with restricted PSS
- [ ] Network policies properly isolate workloads
- [ ] Secrets properly managed (not in env vars)
- [ ] All verification tests pass
- [ ] Documentation complete

## Bonus Challenges

1. Configure Istio mTLS for service mesh
2. Set up OPA Gatekeeper policies
3. Implement admission webhook for custom validation
4. Configure Falco rules for runtime security monitoring

## Resources

- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Network Policies Guide](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
