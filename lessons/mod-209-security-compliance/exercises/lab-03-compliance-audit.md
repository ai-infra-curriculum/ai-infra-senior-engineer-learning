# Lab 3: Compliance Audit and Documentation

## Overview

Security audits and compliance documentation are critical for AI infrastructure, especially when handling sensitive data or operating in regulated industries. This lab teaches you to audit Kubernetes clusters for security compliance, document findings, and create remediation plans.

## Learning Objectives

- Conduct comprehensive security audits of ML infrastructure
- Document compliance controls effectively
- Prepare audit evidence for compliance frameworks (SOC 2, ISO 27001, HIPAA)
- Create actionable remediation plans with risk prioritization
- Build security runbooks for incident response

## Duration

4-5 hours

## Prerequisites

- Access to a Kubernetes cluster (or use kind/minikube locally)
- kubectl configured
- Basic understanding of RBAC, NetworkPolicies, and Pod Security
- Completion of Module 209 lectures on security fundamentals

---

## Part 1: Security Audit (120 minutes)

### Task 1.1: RBAC Configuration Audit (30 min)

#### Audit Commands

```bash
# List all ClusterRoles with dangerous permissions
kubectl get clusterroles -o json | jq '.items[] | select(.rules[].verbs[] | contains("*")) | {name: .metadata.name, rules: .rules}'

# Find RoleBindings that grant cluster-admin
kubectl get clusterrolebindings -o json | jq '.items[] | select(.roleRef.name=="cluster-admin") | {name: .metadata.name, subjects: .subjects}'

# Audit service account permissions
kubectl get sa --all-namespaces
kubectl get rolebindings,clusterrolebindings --all-namespaces -o wide

# Check for overly permissive roles
kubectl auth can-i --list --as=system:serviceaccount:default:default
```

#### Findings Template

```markdown
### RBAC Audit Findings

**Finding 1: Overly Permissive ServiceAccount**
- **Severity**: High
- **Description**: Default service account in 'ml-training' namespace has cluster-admin access
- **Risk**: Compromised pod could access entire cluster
- **Recommendation**: Create least-privilege service account for ML workloads
- **Remediation**: [Link to remediation task]

**Finding 2**: [Add your findings]
```

#### Critical Checks

- [ ] No pods use default service account with elevated permissions
- [ ] Cluster-admin only granted to actual cluster administrators
- [ ] Service accounts follow principle of least privilege
- [ ] Roles are namespace-scoped where possible (not ClusterRoles)
- [ ] No wildcard permissions (*) except for monitoring/operators

---

### Task 1.2: Network Policy Audit (25 min)

#### Audit Commands

```bash
# Check if network policies exist
kubectl get networkpolicies --all-namespaces

# Find namespaces without network policies
kubectl get namespaces -o json | jq -r '.items[].metadata.name' | while read ns; do
  count=$(kubectl get networkpolicies -n $ns --no-headers 2>/dev/null | wc -l)
  if [ $count -eq 0 ]; then
    echo "WARNING: No NetworkPolicy in namespace: $ns"
  fi
done

# Audit pod-to-pod communication
kubectl get pods --all-namespaces -o wide
kubectl get networkpolicies --all-namespaces -o yaml
```

#### Network Segmentation Checklist

- [ ] Default deny-all policy in each namespace
- [ ] ML training pods isolated from production serving
- [ ] Database access restricted to authorized services only
- [ ] Egress rules limit external communication
- [ ] Cross-namespace communication explicitly allowed where needed

#### Example Audit Finding

```markdown
**Finding 3: Missing Default Deny Policy**
- **Severity**: Critical
- **Namespace**: ml-training
- **Description**: No default deny NetworkPolicy; all pods can communicate freely
- **Risk**: Lateral movement in case of pod compromise
- **Remediation**:
  ```yaml
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
```

---

### Task 1.3: Encryption Audit (25 min)

#### Data at Rest

```bash
# Check if etcd encryption is enabled (cluster-level check)
kubectl get secrets -n kube-system -o json | \
  jq -r '.items[].data | keys[]' | head -1 | base64 -d

# Verify storage class encryption
kubectl get storageclass -o yaml | grep -i encrypt

# Check PVC encryption settings
kubectl get pvc --all-namespaces -o yaml | grep -i encrypt
```

#### Data in Transit

```bash
# Check for TLS on ingress
kubectl get ingress --all-namespaces -o yaml | grep -i tls

# Verify service mesh mTLS (if using Istio)
kubectl get peerauthentication --all-namespaces
kubectl get destinationrules --all-namespaces -o yaml | grep -i tls

# Check for unencrypted services
kubectl get svc --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.type=="LoadBalancer") | {name: .metadata.name, namespace: .metadata.namespace}'
```

#### Encryption Checklist

- [ ] etcd encryption at rest enabled
- [ ] PersistentVolumes use encrypted storage classes
- [ ] All ingress uses TLS (no HTTP-only endpoints)
- [ ] Inter-service communication uses mTLS (if service mesh)
- [ ] Database connections use TLS
- [ ] Model artifacts stored in encrypted S3/GCS buckets

---

### Task 1.4: Secrets Management Audit (20 min)

```bash
# Find secrets in environment variables (anti-pattern)
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.containers[].env[]?.valueFrom.secretKeyRef) | {pod: .metadata.name, namespace: .metadata.namespace}'

# Check for base64-encoded secrets in ConfigMaps (bad practice)
kubectl get configmaps --all-namespaces -o yaml | grep -i password

# Verify external secrets operator (if using)
kubectl get externalsecrets --all-namespaces

# Check secret rotation
kubectl get secrets --all-namespaces -o json | \
  jq -r '.items[] | {name: .metadata.name, namespace: .metadata.namespace, age: .metadata.creationTimestamp}'
```

#### Secrets Management Checklist

- [ ] No hardcoded secrets in code or configs
- [ ] Secrets mounted as volumes, not environment variables
- [ ] External secrets manager used (Vault, AWS Secrets Manager, etc.)
- [ ] Secrets rotated regularly (< 90 days)
- [ ] Service account tokens have expiration
- [ ] Secret access audited via RBAC

---

### Task 1.5: Pod Security Standards (20 min)

```bash
# Check Pod Security Admission configuration
kubectl get ns -o yaml | grep -A 5 'pod-security.kubernetes.io'

# Find pods violating Pod Security Standards
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.securityContext.runAsNonRoot != true) | {pod: .metadata.name, namespace: .metadata.namespace, runAsRoot: true}'

# Check for privileged containers
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.containers[].securityContext.privileged == true) | {pod: .metadata.name, namespace: .metadata.namespace}'

# Verify no host path mounts
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.volumes[]?.hostPath) | {pod: .metadata.name, namespace: .metadata.namespace}'
```

#### Pod Security Checklist

- [ ] All namespaces enforce Pod Security Standards (baseline minimum)
- [ ] Production namespaces use "restricted" policy
- [ ] No privileged containers in production
- [ ] Containers run as non-root user
- [ ] Read-only root filesystem where possible
- [ ] No hostPath volumes in production
- [ ] Resource limits set on all containers

---

## Part 2: Documentation (90 minutes)

### Task 2.1: Security Architecture Documentation (30 min)

Create a security architecture document covering:

```markdown
# ML Infrastructure Security Architecture

## Overview
[High-level security approach]

## Network Architecture
### Diagram
[Include C4 or network diagram showing security zones]

### Segmentation Strategy
- **Zone 1: Control Plane**: Kubernetes API, etcd
- **Zone 2: Data Plane - Training**: ML training workloads
- **Zone 3: Data Plane - Serving**: Model inference endpoints
- **Zone 4: Data Storage**: Databases, object storage

### Network Policies
[Document default deny policies and allowed traffic flows]

## Identity and Access Management
### Authentication
- **Cluster Access**: [OIDC, certificates, etc.]
- **Service Accounts**: [Naming convention, lifecycle]
- **Workload Identity**: [How pods authenticate to cloud services]

### Authorization
- **RBAC Model**: [Roles, groups, least privilege]
- **Namespace Strategy**: [How namespaces map to teams/environments]

## Data Protection
### At Rest
- etcd encryption: [Enabled/Disabled, key management]
- PersistentVolume encryption: [Storage class configuration]
- Model artifact encryption: [S3/GCS encryption settings]

### In Transit
- Ingress TLS: [Certificate management, renewal process]
- Service mesh mTLS: [If applicable]
- Database TLS: [Configuration]

## Secrets Management
- **Tool**: [Vault, AWS Secrets Manager, etc.]
- **Rotation Policy**: [Frequency, process]
- **Access Control**: [Who can access which secrets]

## Compliance Controls
[Map controls to compliance framework - see Task 2.2]

## Incident Response
[Link to runbooks - see Task 2.2]
```

---

### Task 2.2: Incident Response Runbooks (30 min)

Create runbooks for common security incidents:

#### Runbook 1: Compromised Pod

```markdown
# Runbook: Suspected Pod Compromise

## Detection
- Unusual network traffic from pod
- Unexpected process execution
- Alert from security monitoring

## Immediate Response (5 minutes)
1. **Isolate the pod**:
   ```bash
   kubectl label pod <pod-name> security=quarantine
   kubectl apply -f - <<EOF
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: quarantine
   spec:
     podSelector:
       matchLabels:
         security: quarantine
     policyTypes:
     - Ingress
     - Egress
   EOF
   ```

2. **Preserve evidence**:
   ```bash
   kubectl logs <pod-name> > evidence-logs.txt
   kubectl get pod <pod-name> -o yaml > evidence-pod-spec.yaml
   ```

## Investigation (30 minutes)
1. **Exec into pod (read-only)**:
   ```bash
   kubectl debug <pod-name> -it --image=busybox --copy-to=debug-pod
   ```

2. **Check for indicators of compromise**:
   - Unexpected processes: `ps aux`
   - Network connections: `netstat -tulpn`
   - Modified files: Compare against known-good image
   - Cron jobs or scheduled tasks

3. **Review audit logs**:
   ```bash
   kubectl get events --namespace <ns> | grep <pod-name>
   # Check cluster audit logs for API access from this pod's service account
   ```

## Containment (15 minutes)
1. **Revoke service account permissions**:
   ```bash
   kubectl delete rolebinding <binding-name>
   ```

2. **Terminate the pod**:
   ```bash
   kubectl delete pod <pod-name>
   ```

## Recovery (60 minutes)
1. **Root cause analysis**: Why did this happen?
2. **Remediation**: Fix underlying vulnerability
3. **Redeploy**: From trusted image
4. **Verify**: Monitor for 24 hours

## Post-Incident
- Document findings in incident report
- Update security controls
- Team debrief
```

#### Runbook 2: Unauthorized Access Attempt

[Similar format for other incidents: data breach, DDoS, insider threat, etc.]

---

### Task 2.3: Compliance Evidence (30 min)

Create compliance evidence package for SOC 2 (or your relevant framework):

```markdown
# SOC 2 Compliance Evidence - ML Infrastructure

## CC6.1: Logical and Physical Access Controls

### Control: RBAC Enforcement
**Evidence**:
- RBAC policy documentation: [Link]
- Quarterly access reviews: [Last review date]
- Audit log sample showing RBAC enforcement: [Attached logs]

**Verification**:
```bash
# Generate RBAC audit report
kubectl get rolebindings,clusterrolebindings --all-namespaces -o wide > rbac-audit-$(date +%Y%m%d).txt
```

## CC6.6: Logical and Physical Access Controls - Encryption

### Control: Data Encryption at Rest
**Evidence**:
- etcd encryption configuration: [Attached config]
- Storage class encryption settings: [kubectl get sc output]
- Encryption key rotation logs: [Last rotation date]

### Control: Data Encryption in Transit
**Evidence**:
- TLS certificate inventory: [List of certs and expiry dates]
- mTLS enforcement policies: [Istio PeerAuthentication configs]
- Network traffic encryption audit: [Test results]

## CC7.2: System Monitoring - Detection

### Control: Security Event Monitoring
**Evidence**:
- Falco rules configuration: [Attached]
- Sample security alerts: [Last 30 days]
- Incident response times: [Average time to detect/respond]

**Verification**:
```bash
# Check Falco is running
kubectl get pods -n falco
kubectl logs -n falco <falco-pod> --tail=100
```

## CC7.3: System Monitoring - Response

### Control: Incident Response Procedures
**Evidence**:
- Incident response runbooks: [Links to all runbooks]
- Recent incident reports: [Anonymized examples]
- Team training records: [Last tabletop exercise date]

---

## Evidence Collection Script

```bash
#!/bin/bash
# collect-compliance-evidence.sh

EVIDENCE_DIR="compliance-evidence-$(date +%Y%m%d)"
mkdir -p $EVIDENCE_DIR

echo "Collecting compliance evidence..."

# RBAC evidence
kubectl get rolebindings,clusterrolebindings --all-namespaces -o yaml > $EVIDENCE_DIR/rbac-config.yaml

# Network policies
kubectl get networkpolicies --all-namespaces -o yaml > $EVIDENCE_DIR/network-policies.yaml

# Pod Security Admission
kubectl get ns -o yaml | grep -A 5 'pod-security.kubernetes.io' > $EVIDENCE_DIR/psa-config.txt

# TLS/Encryption
kubectl get ingress --all-namespaces -o yaml | grep -A 10 tls > $EVIDENCE_DIR/ingress-tls.yaml

# Audit logs sample (last 1000 events)
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -1000 > $EVIDENCE_DIR/audit-events.txt

# Security monitoring (Falco)
kubectl logs -n falco -l app=falco --tail=1000 > $EVIDENCE_DIR/security-alerts.txt

echo "Evidence collected in $EVIDENCE_DIR/"
tar -czf $EVIDENCE_DIR.tar.gz $EVIDENCE_DIR
echo "Archive created: $EVIDENCE_DIR.tar.gz"
```

---

## Part 3: Remediation Planning (30 minutes)

### Task 3.1: Prioritize Findings

Use a risk matrix to prioritize:

| Finding | Severity | Likelihood | Risk Score | Priority |
|---------|----------|------------|------------|----------|
| No default deny NetworkPolicy | High | High | 9 | 1 |
| Default SA has cluster-admin | High | Medium | 6 | 2 |
| Secrets in env vars | Medium | High | 6 | 3 |
| Missing TLS on internal service | Low | Low | 2 | 4 |

**Risk Score** = Severity (1-3) × Likelihood (1-3)

---

### Task 3.2: Create Remediation Plan

```markdown
# Security Remediation Plan

## Critical (Fix in 1 week)

### Finding 1: Missing Default Deny NetworkPolicy
**Owner**: Platform Team
**Due Date**: [Date + 7 days]
**Effort**: 2 hours
**Steps**:
1. Create default-deny policy template
2. Apply to all namespaces
3. Test applications still function
4. Document allowed traffic patterns

**Success Criteria**:
- [ ] Default deny policy in all namespaces
- [ ] All applications functioning
- [ ] No unexpected network connectivity

---

## High (Fix in 2 weeks)

### Finding 2: Service Account Over-Privileged
**Owner**: ML Platform Team
**Due Date**: [Date + 14 days]
**Effort**: 4 hours
**Steps**:
1. Audit current SA permissions
2. Design least-privilege roles
3. Create new service accounts
4. Migrate workloads
5. Delete old SA

---

## Medium (Fix in 30 days)

[Continue for all findings]

---

## Continuous Improvements

**Quarterly Tasks**:
- [ ] Access review
- [ ] Certificate rotation audit
- [ ] Security training for team
- [ ] Penetration test

**Automation**:
- [ ] Set up automated security scanning (Trivy, Falco)
- [ ] Auto-remediation for common issues
- [ ] Compliance dashboard
```

---

## Deliverables

Submit the following:

1. **Audit Report** (3-5 pages)
   - Executive summary
   - Findings by severity
   - Risk assessment
   - Recommendations

2. **Security Architecture Documentation** (5-8 pages)
   - Network architecture
   - IAM strategy
   - Encryption strategy
   - Compliance mapping

3. **Incident Response Runbooks** (2-3 runbooks minimum)
   - Compromised pod
   - Unauthorized access
   - Data breach

4. **Remediation Plan** (1-2 pages)
   - Prioritized findings
   - Owners and timelines
   - Success criteria

---

## Extension Activities

1. **Automated Compliance Scanning**: Set up Falco or OPA Gatekeeper for continuous compliance
2. **Penetration Testing**: Conduct a security assessment of your cluster
3. **Compliance Framework Mapping**: Map controls to multiple frameworks (SOC 2, ISO 27001, HIPAA)
4. **Security Metrics Dashboard**: Build Grafana dashboard tracking security KPIs

---

## Resources

- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [Kubernetes Security Checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
- [NSA Kubernetes Hardening Guide](https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2716980/)

---

## Next Steps

- Implement automated compliance scanning
- Schedule quarterly security audits
- Complete Lab 4: Penetration Testing
- Share findings with your team for remediation
