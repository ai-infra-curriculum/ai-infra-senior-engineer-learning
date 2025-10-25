# Lab 2: Zero-Trust Architecture Implementation

## Overview

Zero-trust architecture assumes no implicit trust within the network perimeter. This lab implements zero-trust principles for ML infrastructure using Istio service mesh, enabling mutual TLS authentication, identity-based authorization, and fine-grained access control between services.

## Learning Objectives

- Deploy and configure Istio service mesh on Kubernetes
- Implement strict mutual TLS (mTLS) for all service-to-service communication
- Create identity-based authorization policies
- Configure request authentication using JWT tokens
- Monitor zero-trust security posture with Kiali and Prometheus
- Apply zero-trust principles to ML inference pipelines

## Duration

4-5 hours

## Prerequisites

- Access to a Kubernetes cluster (1.23+)
- kubectl configured and tested
- Helm 3.x installed
- Basic understanding of Kubernetes Services and Deployments
- Completion of Module 209 Lecture 02 (Network Security)

---

## Part 1: Install Istio Service Mesh (45 minutes)

### Task 1.1: Install Istio CLI and Control Plane (20 min)

#### Download and Install istioctl

```bash
# Download Istio 1.20.x (latest stable)
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -

# Add istioctl to PATH
cd istio-1.20.0
export PATH=$PWD/bin:$PATH

# Verify installation
istioctl version
```

#### Install Istio with Demo Profile

```bash
# Install Istio control plane with demo configuration profile
# This includes: istiod, ingress gateway, egress gateway
istioctl install --set profile=demo -y

# Verify installation
kubectl get pods -n istio-system

# Expected output:
# NAME                                    READY   STATUS
# istio-egressgateway-xxx                 1/1     Running
# istio-ingressgateway-xxx                1/1     Running
# istiod-xxx                              1/1     Running
```

#### Understanding Istio Components

- **istiod**: Control plane that manages configuration and certificate distribution
- **istio-ingressgateway**: Handles incoming traffic to the mesh
- **istio-egressgateway**: Manages outbound traffic from the mesh
- **Envoy sidecar proxies**: Injected into each pod to handle traffic

---

### Task 1.2: Enable Automatic Sidecar Injection (15 min)

#### Create ML Workload Namespace

```bash
# Create namespace for ML serving workloads
kubectl create namespace ml-serving

# Enable automatic Istio sidecar injection
kubectl label namespace ml-serving istio-injection=enabled

# Verify label
kubectl get namespace ml-serving --show-labels
```

#### Deploy Sample ML Application

```yaml
# File: ml-app.yaml
apiVersion: v1
kind: Service
metadata:
  name: model-server
  namespace: ml-serving
spec:
  selector:
    app: model-server
  ports:
  - port: 8080
    targetPort: 8080
    name: http
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
  namespace: ml-serving
spec:
  replicas: 2
  selector:
    matchLabels:
      app: model-server
      version: v1
  template:
    metadata:
      labels:
        app: model-server
        version: v1
    spec:
      containers:
      - name: server
        image: hashicorp/http-echo
        args:
        - "-text=Model Server v1"
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: feature-store
  namespace: ml-serving
spec:
  selector:
    app: feature-store
  ports:
  - port: 9000
    targetPort: 9000
    name: http
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-store
  namespace: ml-serving
spec:
  replicas: 1
  selector:
    matchLabels:
      app: feature-store
  template:
    metadata:
      labels:
        app: feature-store
    spec:
      containers:
      - name: store
        image: hashicorp/http-echo
        args:
        - "-text=Feature Store"
        - "-listen=:9000"
        ports:
        - containerPort: 9000
```

```bash
# Deploy the application
kubectl apply -f ml-app.yaml

# Verify pods have 2 containers (app + Envoy sidecar)
kubectl get pods -n ml-serving

# Should show 2/2 READY (application + istio-proxy)
```

#### Verify Sidecar Injection

```bash
# Check pod details
kubectl describe pod -n ml-serving -l app=model-server | grep -A 5 "Containers:"

# You should see two containers:
# 1. server (your application)
# 2. istio-proxy (Envoy sidecar)
```

---

### Task 1.3: Verify Service Mesh Connectivity (10 min)

#### Test Service Communication

```bash
# Deploy a test client pod
kubectl run -n ml-serving test-client --image=curlimages/curl --rm -it -- sh

# Inside the pod, test connectivity:
curl http://model-server:8080
# Expected: "Model Server v1"

curl http://feature-store:9000
# Expected: "Feature Store"

exit
```

#### Check Istio Proxy Status

```bash
# Verify Envoy proxy configuration sync
istioctl proxy-status

# Should show all pods with SYNCED status
```

---

## Part 2: Configure Mutual TLS (90 minutes)

### Task 2.1: Enable Strict mTLS (30 min)

#### Understanding mTLS Modes

- **PERMISSIVE**: Accepts both plaintext and mTLS (default during migration)
- **STRICT**: Requires mTLS for all connections
- **DISABLE**: No mTLS enforcement

#### Create Strict mTLS Policy

```yaml
# File: strict-mtls.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: ml-serving
spec:
  mtls:
    mode: STRICT
```

```bash
# Apply strict mTLS policy
kubectl apply -f strict-mtls.yaml

# Verify policy
kubectl get peerauthentication -n ml-serving
```

#### Test mTLS Enforcement

```bash
# Try to connect WITHOUT Istio sidecar (should fail)
kubectl run -n ml-serving test-plain --image=curlimages/curl --rm -it -- sh

# This pod has no sidecar, so cannot do mTLS
curl http://model-server:8080
# Expected: Connection refused or timeout (mTLS required)

exit
```

```bash
# Deploy client WITH sidecar injection
kubectl run -n ml-serving test-mtls \
  --image=curlimages/curl \
  --labels="app=test-client" \
  --rm -it -- sh

# This pod has sidecar, can do mTLS
curl http://model-server:8080
# Expected: "Model Server v1" (success via mTLS)

exit
```

---

### Task 2.2: Verify mTLS with istioctl (15 min)

```bash
# Check mTLS status for all services
istioctl authn tls-check -n ml-serving

# Output shows:
# - HOST:PORT          STATUS     SERVER     CLIENT
# - model-server:8080  OK         STRICT     ISTIO_MUTUAL
# - feature-store:9000 OK         STRICT     ISTIO_MUTUAL
```

#### Inspect Certificate Information

```bash
# Get a pod name
POD=$(kubectl get pod -n ml-serving -l app=model-server -o jsonpath='{.items[0].metadata.name}')

# View certificate details from Envoy
kubectl exec -n ml-serving $POD -c istio-proxy -- \
  openssl s_client -showcerts -connect model-server:8080 < /dev/null

# Shows X.509 certificate with:
# - Subject: spiffe://cluster.local/ns/ml-serving/sa/default
# - Issuer: Istio CA
# - Valid for 24 hours (auto-rotated)
```

---

### Task 2.3: Monitor mTLS Traffic with Kiali (45 min)

#### Install Kiali Dashboard

```bash
# Install Kiali, Prometheus, Grafana, Jaeger (observability stack)
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml

# Wait for Kiali to be ready
kubectl rollout status deployment/kiali -n istio-system

# Access Kiali dashboard
istioctl dashboard kiali
```

#### Generate Traffic for Visualization

```bash
# In a separate terminal, generate traffic
kubectl run -n ml-serving load-generator \
  --image=busybox \
  --restart=Never \
  -- /bin/sh -c "while true; do wget -q -O- http://model-server:8080; sleep 1; done"
```

#### Explore Kiali Features

In the Kiali UI:

1. **Graph View** (Graph tab):
   - Select namespace: `ml-serving`
   - Display: "Security" badges
   - Look for padlock icons indicating mTLS connections

2. **Service Details**:
   - Click on `model-server` service
   - Check "Security" section - should show mTLS STRICT

3. **Workload View**:
   - See pods with sidecars
   - Check health and performance metrics

4. **Configuration Validation**:
   - Applications → Istio Config
   - Look for PeerAuthentication policy

```bash
# Clean up load generator
kubectl delete pod -n ml-serving load-generator
```

---

## Part 3: Implement Zero-Trust Authorization (90 minutes)

### Task 3.1: Service-to-Service Authorization (30 min)

#### Scenario: Only model-server can access feature-store

**Default (Insecure)**: Any service in the mesh can call any other service.

**Goal**: Implement least-privilege access control.

#### Create Deny-All Policy (Default Deny)

```yaml
# File: deny-all.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: ml-serving
spec:
  {}
  # Empty spec = deny all requests
```

```bash
# Apply deny-all policy
kubectl apply -f deny-all.yaml

# Test - should now be denied
kubectl run -n ml-serving test-client --image=curlimages/curl --rm -it -- \
  curl http://model-server:8080
# Expected: RBAC: access denied
```

#### Allow Specific Access

```yaml
# File: allow-model-to-feature-store.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-model-to-feature
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: feature-store
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/ml-serving/sa/model-server-sa"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/features/*"]
```

**Note**: This requires service accounts. Let's create them:

```yaml
# File: service-accounts.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: model-server-sa
  namespace: ml-serving
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: feature-store-sa
  namespace: ml-serving
```

```bash
# Apply service accounts
kubectl apply -f service-accounts.yaml

# Update deployments to use service accounts
kubectl patch deployment model-server -n ml-serving -p '{"spec":{"template":{"spec":{"serviceAccountName":"model-server-sa"}}}}'
kubectl patch deployment feature-store -n ml-serving -p '{"spec":{"template":{"spec":{"serviceAccountName":"feature-store-sa"}}}}'

# Wait for rollout
kubectl rollout status deployment/model-server -n ml-serving
kubectl rollout status deployment/feature-store -n ml-serving
```

#### Apply Authorization Policy

```bash
# Apply the allow policy
kubectl apply -f allow-model-to-feature-store.yaml

# Test from model-server pod (should succeed)
MODEL_POD=$(kubectl get pod -n ml-serving -l app=model-server -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ml-serving $MODEL_POD -c server -- \
  wget -q -O- http://feature-store:9000
# Expected: Success

# Test from other pod (should fail)
kubectl run -n ml-serving unauthorized --image=curlimages/curl --rm -it -- \
  curl http://feature-store:9000
# Expected: RBAC: access denied
```

---

### Task 3.2: Request-Level Authorization (30 min)

#### Implement JWT-Based Authentication

**Scenario**: External requests to model-server must include valid JWT token.

#### Create Request Authentication Policy

```yaml
# File: jwt-auth.yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: model-server
  jwtRules:
  - issuer: "https://ml-platform.example.com"
    jwksUri: "https://ml-platform.example.com/.well-known/jwks.json"
    audiences:
    - "ml-inference-api"
```

#### Create Authorization Policy for JWT

```yaml
# File: require-jwt.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: require-jwt
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: model-server
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["https://ml-platform.example.com/*"]
```

**For testing purposes**, we'll use a simplified setup:

```yaml
# File: jwt-auth-test.yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-test
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: model-server
  jwtRules:
  - issuer: "test-issuer@example.com"
    # Use Istio's built-in test JWKS for demo
    jwks: |
      {
        "keys": [
          {
            "kty": "RSA",
            "kid": "test-key",
            "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
            "e": "AQAB"
          }
        ]
      }
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: require-jwt-test
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: model-server
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["test-issuer@example.com/*"]
  - to:
    - operation:
        paths: ["/health"]  # Allow health checks without JWT
```

```bash
# Apply JWT authentication
kubectl apply -f jwt-auth-test.yaml

# Test without token (should fail)
kubectl run -n ml-serving test-no-jwt --image=curlimages/curl --rm -it -- \
  curl http://model-server:8080
# Expected: "Jwt is missing"

# Test with invalid token (should fail)
kubectl run -n ml-serving test-bad-jwt --image=curlimages/curl --rm -it -- \
  curl -H "Authorization: Bearer invalid-token" http://model-server:8080
# Expected: "Jwt verification fails"
```

---

### Task 3.3: Path-Based Authorization (30 min)

#### Create Fine-Grained Access Control

```yaml
# File: path-based-authz.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: model-server-paths
  namespace: ml-serving
spec:
  selector:
    matchLabels:
      app: model-server
  action: ALLOW
  rules:
  # Allow health checks from any service
  - to:
    - operation:
        paths: ["/health", "/ready"]
        methods: ["GET"]

  # Allow predictions only from authenticated services
  - from:
    - source:
        principals: ["cluster.local/ns/ml-serving/sa/api-gateway-sa"]
    to:
    - operation:
        paths: ["/predict"]
        methods: ["POST"]

  # Allow metrics scraping from Prometheus
  - from:
    - source:
        namespaces: ["istio-system"]
    to:
    - operation:
        paths: ["/metrics"]
        methods: ["GET"]
```

```bash
# Apply path-based authorization
kubectl apply -f path-based-authz.yaml
```

---

## Part 4: Monitoring and Observability (60 minutes)

### Task 4.1: Configure Security Dashboards (20 min)

#### Access Grafana

```bash
# Open Grafana dashboard
istioctl dashboard grafana
```

In Grafana:
1. Navigate to "Dashboards" → "Istio" → "Istio Service Dashboard"
2. Select namespace: `ml-serving`
3. Select service: `model-server`
4. View metrics:
   - Request rate
   - Success rate
   - mTLS status
   - Authorization decisions (allow/deny)

#### Custom Prometheus Queries

```bash
# Open Prometheus
istioctl dashboard prometheus
```

**Query 1: mTLS Requests**
```promql
# Count of mTLS requests
sum(istio_requests_total{destination_service_namespace="ml-serving", connection_security_policy="mutual_tls"}) by (destination_service_name)
```

**Query 2: Authorization Denials**
```promql
# Count of denied requests
sum(istio_requests_total{destination_service_namespace="ml-serving", response_code="403"}) by (destination_service_name)
```

**Query 3: Services Without mTLS**
```promql
# Alert if any plaintext traffic
istio_requests_total{connection_security_policy!="mutual_tls", destination_service_namespace="ml-serving"}
```

---

### Task 4.2: Create Security Alerts (20 min)

#### PrometheusRule for Security Violations

```yaml
# File: security-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: istio-security-alerts
  namespace: istio-system
spec:
  groups:
  - name: istio-security
    interval: 30s
    rules:
    - alert: MtlsDisabled
      expr: |
        sum(istio_requests_total{connection_security_policy!="mutual_tls", destination_service_namespace="ml-serving"}) > 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Plaintext traffic detected in ml-serving namespace"
        description: "Service {{ $labels.destination_service_name }} is receiving plaintext requests"

    - alert: HighAuthzDenialRate
      expr: |
        sum(rate(istio_requests_total{response_code="403", destination_service_namespace="ml-serving"}[5m]))
        /
        sum(rate(istio_requests_total{destination_service_namespace="ml-serving"}[5m])) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High authorization denial rate (>10%)"
        description: "Service {{ $labels.destination_service_name }} has {{ $value }}% denied requests"

    - alert: UnauthorizedAccessAttempt
      expr: |
        increase(istio_requests_total{response_code="403", destination_service_namespace="ml-serving"}[1m]) > 10
      for: 1m
      labels:
        severity: warning
      annotations:
        summary: "Multiple unauthorized access attempts detected"
        description: "{{ $value }} denied requests to {{ $labels.destination_service_name }} in last minute"
```

```bash
# Apply security alerts (if using Prometheus Operator)
kubectl apply -f security-alerts.yaml
```

---

### Task 4.3: Audit Logging (20 min)

#### Enable Envoy Access Logs

```yaml
# File: enable-access-logs.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio
  namespace: istio-system
data:
  mesh: |
    accessLogFile: /dev/stdout
    accessLogEncoding: JSON
```

```bash
# Apply configuration
kubectl apply -f enable-access-logs.yaml

# Restart istiod to pick up changes
kubectl rollout restart deployment/istiod -n istio-system
```

#### View Access Logs

```bash
# View logs from model-server sidecar
kubectl logs -n ml-serving -l app=model-server -c istio-proxy --tail=20

# Example log entry (JSON):
{
  "authority": "model-server:8080",
  "bytes_received": 0,
  "bytes_sent": 16,
  "downstream_local_address": "10.244.0.10:8080",
  "downstream_remote_address": "10.244.0.15:45678",
  "duration": 2,
  "method": "GET",
  "path": "/predict",
  "protocol": "HTTP/1.1",
  "request_id": "abc123",
  "response_code": 200,
  "response_flags": "-",
  "route_name": "default",
  "start_time": "2025-10-16T10:30:45.123Z",
  "upstream_cluster": "inbound|8080||",
  "upstream_host": "127.0.0.1:8080",
  "upstream_local_address": "127.0.0.1:45679",
  "upstream_service_time": "1",
  "user_agent": "curl/7.64.0",
  "x_forwarded_for": "10.244.0.15",
  "requested_server_name": "model-server.ml-serving.svc.cluster.local",
  "connection_termination_details": "-",
  "tls_version": "TLSv1.3",
  "tls_cipher_suite": "TLS_AES_256_GCM_SHA384"
}
```

#### Filter for Security Events

```bash
# Find authorization denials
kubectl logs -n ml-serving -l app=model-server -c istio-proxy | \
  jq 'select(.response_code == 403)'

# Find non-mTLS requests (should be none!)
kubectl logs -n ml-serving -l app=model-server -c istio-proxy | \
  jq 'select(.tls_version == null or .tls_version == "")'
```

---

## Part 5: Advanced Zero-Trust Scenarios (Bonus - 30 minutes)

### Task 5.1: Egress Control

**Goal**: Control external API access from ML services.

```yaml
# File: egress-control.yaml
# Only allow model-server to call external model registry
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-model-registry
  namespace: ml-serving
spec:
  hosts:
  - "models.example.com"
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-model-server-egress
  namespace: istio-system
spec:
  selector:
    matchLabels:
      app: istio-egressgateway
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/ml-serving/sa/model-server-sa"]
    to:
    - operation:
        hosts: ["models.example.com"]
```

---

### Task 5.2: Rate Limiting

```yaml
# File: rate-limit.yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: model-server-ratelimit
  namespace: ml-serving
spec:
  workloadSelector:
    labels:
      app: model-server
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          stat_prefix: http_local_rate_limiter
          token_bucket:
            max_tokens: 100
            tokens_per_fill: 100
            fill_interval: 60s
          filter_enabled:
            runtime_key: local_rate_limit_enabled
            default_value:
              numerator: 100
              denominator: HUNDRED
          filter_enforced:
            runtime_key: local_rate_limit_enforced
            default_value:
              numerator: 100
              denominator: HUNDRED
```

---

## Deliverables

Submit the following:

1. **Istio Configuration Audit** (1-2 pages)
   - List of all PeerAuthentication policies
   - List of all AuthorizationPolicies with descriptions
   - mTLS status for all services (from `istioctl authn tls-check`)
   - Screenshot of Kiali graph showing mTLS (padlock icons)

2. **Security Test Results** (1 page)
   - Evidence that deny-all policy blocks unauthorized access
   - Evidence that only authorized service accounts can access protected services
   - Logs showing JWT authentication failures

3. **Monitoring Dashboard** (Screenshots)
   - Kiali service graph with security badges
   - Grafana dashboard showing authorization metrics
   - Prometheus query results for mTLS traffic

4. **Reflection Document** (1 page)
   - What are the benefits of zero-trust vs. perimeter-based security?
   - What are the operational challenges of strict mTLS?
   - How would you troubleshoot authorization policy issues?

---

## Validation Checklist

- [ ] Istio control plane installed and healthy
- [ ] Automatic sidecar injection enabled in ml-serving namespace
- [ ] Strict mTLS enforced for all services
- [ ] Plaintext traffic blocked (verified with test pod)
- [ ] Default deny-all authorization policy applied
- [ ] Service-to-service authorization working (only model-server → feature-store)
- [ ] JWT authentication configured (optional)
- [ ] Kiali dashboard accessible and showing security status
- [ ] Prometheus metrics showing mTLS traffic
- [ ] Security alerts configured
- [ ] Envoy access logs enabled and viewable

---

## Troubleshooting Guide

### Issue: Pods stuck in Init state

**Symptom**: Pods show `Init:0/1` after deploying

**Cause**: Istio sidecar injection issues

**Fix**:
```bash
kubectl describe pod -n ml-serving <pod-name>
# Check events for CNI or init container errors

# Verify istio-injection label
kubectl get namespace ml-serving --show-labels
```

---

### Issue: 503 Service Unavailable

**Symptom**: Services return 503 after applying strict mTLS

**Cause**: Some pods don't have sidecars

**Fix**:
```bash
# Check all pods have 2/2 containers
kubectl get pods -n ml-serving

# If some pods missing sidecars, restart them
kubectl rollout restart deployment -n ml-serving
```

---

### Issue: RBAC: access denied

**Symptom**: All requests denied after applying AuthorizationPolicy

**Cause**: Too restrictive policies or missing rules

**Fix**:
```bash
# Check authorization policies
kubectl get authorizationpolicy -n ml-serving -o yaml

# Temporarily disable to test
kubectl delete authorizationpolicy deny-all -n ml-serving

# Check Envoy logs for details
kubectl logs -n ml-serving <pod> -c istio-proxy | grep RBAC
```

---

### Issue: Kiali shows no traffic

**Symptom**: Kiali graph is empty

**Cause**: No traffic or Prometheus not scraping

**Fix**:
```bash
# Generate traffic
kubectl run -n ml-serving load \
  --image=busybox --restart=Never -- \
  /bin/sh -c "while true; do wget -q -O- http://model-server:8080; sleep 1; done"

# Check Prometheus is scraping
kubectl port-forward -n istio-system svc/prometheus 9090:9090
# Visit http://localhost:9090/targets
```

---

## Resources

### Official Documentation
- [Istio Security Concepts](https://istio.io/latest/docs/concepts/security/)
- [Istio Authorization Policy](https://istio.io/latest/docs/reference/config/security/authorization-policy/)
- [Istio mTLS](https://istio.io/latest/docs/tasks/security/authentication/mtls-migration/)

### Best Practices
- [Zero Trust Architecture - NIST SP 800-207](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [Istio Security Best Practices](https://istio.io/latest/docs/ops/best-practices/security/)

### Tools
- [Kiali Documentation](https://kiali.io/docs/)
- [istioctl reference](https://istio.io/latest/docs/reference/commands/istioctl/)

---

## Extension Activities

1. **Multi-Cluster Zero-Trust**: Set up Istio multi-cluster mesh with cross-cluster mTLS
2. **External Authorization**: Integrate with OPA (Open Policy Agent) for complex authorization logic
3. **Certificate Management**: Configure Istio with external CA (cert-manager + Let's Encrypt)
4. **WAF Integration**: Add Web Application Firewall (ModSecurity) to ingress gateway
5. **Chaos Engineering**: Test security resilience with Chaos Mesh

---

## Next Steps

- Complete Lab 3: Compliance Audit and Documentation
- Implement zero-trust in your production ML infrastructure
- Schedule quarterly zero-trust security reviews
- Share findings with your team and stakeholders

**Remember**: Zero-trust is a journey, not a destination. Continuously validate and improve your security posture!
