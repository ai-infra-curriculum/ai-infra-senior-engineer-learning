# Lecture 04: Advanced Networking and Service Mesh

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement advanced Kubernetes networking architectures using CNI plugins for ML workloads
- Deploy and configure service mesh (Istio/Linkerd) for production ML inference services
- Implement intelligent traffic management including A/B testing, canary deployments, and circuit breaking
- Configure mutual TLS (mTLS) for secure service-to-service communication in multi-tenant environments
- Implement distributed tracing and observability for complex ML serving pipelines
- Design network policies for zero-trust security in ML infrastructure
- Optimize network performance for low-latency inference and high-throughput training data transfer
- Troubleshoot complex networking issues including DNS resolution, service connectivity, and load balancing

## Table of Contents
1. [Kubernetes Networking Deep Dive](#networking-deep-dive)
2. [Container Network Interface (CNI)](#cni)
3. [Service Mesh Architecture](#service-mesh)
4. [Istio for ML Workloads](#istio)
5. [Traffic Management](#traffic-management)
6. [Observability and Tracing](#observability)
7. [Security with mTLS](#security)

## Kubernetes Networking Deep Dive {#networking-deep-dive}

### The Kubernetes Network Model

Kubernetes imposes fundamental networking requirements:

1. **Pod-to-Pod Communication:** All pods can communicate with each other without NAT
2. **Pod-to-Service Communication:** Pods can reach services through ClusterIP
3. **External-to-Service Communication:** External clients can reach services through LoadBalancer or Ingress
4. **Container-to-Container:** Containers in same pod communicate via localhost

### Network Layers

```
┌─────────────────────────────────────────┐
│  Application (Model Inference API)      │
├─────────────────────────────────────────┤
│  Service (ClusterIP, LoadBalancer)      │
├─────────────────────────────────────────┤
│  Pod Network (CNI Plugin)               │
├─────────────────────────────────────────┤
│  Node Network (eth0, etc.)              │
└─────────────────────────────────────────┘
```

### Service Types

**ClusterIP (default):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-inference
spec:
  type: ClusterIP
  selector:
    app: model-server
  ports:
  - port: 8080
    targetPort: 8080
# Accessible only within cluster
# DNS: model-inference.namespace.svc.cluster.local
```

**NodePort:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-inference-nodeport
spec:
  type: NodePort
  selector:
    app: model-server
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080  # 30000-32767
# Accessible on <NodeIP>:30080
```

**LoadBalancer:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-inference-lb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  selector:
    app: model-server
  ports:
  - port: 443
    targetPort: 8080
# Cloud provider creates external LB
```

**Headless Service (for StatefulSets):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: distributed-training
spec:
  clusterIP: None  # Headless
  selector:
    app: training
  ports:
  - port: 23456
# DNS returns pod IPs directly
# distributed-training-0.distributed-training.namespace.svc.cluster.local
```

### DNS in Kubernetes

**Service DNS:**
```
<service-name>.<namespace>.svc.cluster.local
```

**Pod DNS:**
```
<pod-ip-with-dashes>.<namespace>.pod.cluster.local
# Example: 10-244-1-5.default.pod.cluster.local
```

**StatefulSet Pod DNS:**
```
<statefulset-name>-<ordinal>.<service-name>.<namespace>.svc.cluster.local
```

### Network Policies

Control traffic between pods (firewall rules):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: model-server-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: model-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from API gateway only
  - from:
    - namespaceSelector:
        matchLabels:
          name: gateway
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Allow to feature store
  - to:
    - podSelector:
        matchLabels:
          app: feature-store
    ports:
    - protocol: TCP
      port: 6379
  # Allow DNS
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

**Default Deny All:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress
```

## Container Network Interface (CNI) {#cni}

### Popular CNI Plugins

**Calico:**
- Layer 3 networking
- Network policies
- BGP routing
- High performance

```yaml
# Calico configuration
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: default-ipv4-ippool
spec:
  cidr: 192.168.0.0/16
  ipipMode: Always
  natOutgoing: true
```

**Cilium:**
- eBPF-based
- Advanced network policies
- Service mesh features
- Excellent observability

**Flannel:**
- Simple overlay network
- Easy setup
- Good for getting started

**Weave:**
- Mesh networking
- Encryption
- Multicast support

### CNI Plugin for ML Workloads

**Performance Considerations:**

```yaml
# Use host network for latency-sensitive inference
apiVersion: v1
kind: Pod
metadata:
  name: low-latency-inference
spec:
  hostNetwork: true  # Use host network namespace
  dnsPolicy: ClusterFirstWithHostNet
  containers:
  - name: inference
    image: model-server:v1
    ports:
    - containerPort: 8080
      hostPort: 8080
```

**Multi-Network Interface:**

```yaml
# Using Multus CNI for multiple networks
apiVersion: v1
kind: Pod
metadata:
  name: multi-nic-training
  annotations:
    k8s.v1.cni.cncf.io/networks: |
      [
        {
          "name": "data-plane-net",
          "interface": "net1"
        },
        {
          "name": "storage-net",
          "interface": "net2"
        }
      ]
spec:
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    # Now has eth0 (default), net1, net2
```

## Service Mesh Architecture {#service-mesh}

### What is a Service Mesh?

A service mesh is a dedicated infrastructure layer for handling service-to-service communication, providing:

- **Traffic management:** Routing, load balancing, traffic splitting
- **Security:** mTLS, authentication, authorization
- **Observability:** Metrics, logging, tracing
- **Resilience:** Retries, timeouts, circuit breaking

### Service Mesh Components

```
┌─────────────────────────────────────────────────┐
│           Control Plane                         │
│  ┌──────────────────────────────────────────┐  │
│  │  Pilot (Traffic Management)              │  │
│  │  Citadel (Certificate Management)        │  │
│  │  Galley (Configuration)                  │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │ Configuration
┌────────────────▼────────────────────────────────┐
│           Data Plane                            │
│  ┌────────────────────────────────────────┐    │
│  │ App Container │ Envoy Sidecar Proxy    │    │
│  │               │ (intercepts traffic)    │    │
│  └────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Istio vs Linkerd

| Feature | Istio | Linkerd |
|---------|-------|---------|
| Complexity | Higher | Lower |
| Features | Comprehensive | Focused |
| Resource usage | Higher | Lower |
| Proxy | Envoy | Linkerd2-proxy (Rust) |
| Use case | Full-featured | Lightweight |

For ML workloads:
- **Istio:** Production systems with complex requirements
- **Linkerd:** Simpler deployments, resource-constrained environments

## Istio for ML Workloads {#istio}

### Installing Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.18.0
export PATH=$PWD/bin:$PATH

# Install with demo profile
istioctl install --set profile=demo -y

# Enable automatic sidecar injection
kubectl label namespace ml-production istio-injection=enabled
```

### Sidecar Injection

**Automatic Injection:**
```bash
kubectl label namespace ml-production istio-injection=enabled
```

**Manual Injection:**
```bash
istioctl kube-inject -f deployment.yaml | kubectl apply -f -
```

**Control Sidecar Resources:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: model-server
  annotations:
    sidecar.istio.io/proxyCPU: "100m"
    sidecar.istio.io/proxyMemory: "128Mi"
    sidecar.istio.io/proxyCPULimit: "2000m"
    sidecar.istio.io/proxyMemoryLimit: "1Gi"
spec:
  containers:
  - name: inference
    image: model-server:v1
```

### Gateway for External Traffic

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: ml-gateway
  namespace: ml-production
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: ml-tls-cert
    hosts:
    - "api.ml.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference
  namespace: ml-production
spec:
  hosts:
  - "api.ml.example.com"
  gateways:
  - ml-gateway
  http:
  - match:
    - uri:
        prefix: "/v1/models"
    route:
    - destination:
        host: model-server
        port:
          number: 8080
```

## Traffic Management {#traffic-management}

### Canary Deployments

Gradually shift traffic from old to new model version:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-canary
spec:
  hosts:
  - model-server
  http:
  - match:
    - headers:
        x-user-group:
          exact: "beta"
    route:
    - destination:
        host: model-server
        subset: v2
  - route:
    - destination:
        host: model-server
        subset: v1
      weight: 90
    - destination:
        host: model-server
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: model-server
spec:
  host: model-server
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### A/B Testing

Route based on user attributes:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ab-testing
spec:
  hosts:
  - model-server
  http:
  # Model A for users 0-49999
  - match:
    - headers:
        x-user-id:
          regex: "^[0-4].*"
    route:
    - destination:
        host: model-server
        subset: model-a
  # Model B for users 50000-99999
  - match:
    - headers:
        x-user-id:
          regex: "^[5-9].*"
    route:
    - destination:
        host: model-server
        subset: model-b
```

### Traffic Mirroring (Shadow Traffic)

Test new model with production traffic without affecting responses:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: traffic-mirroring
spec:
  hosts:
  - model-server
  http:
  - route:
    - destination:
        host: model-server
        subset: v1
      weight: 100
    mirror:
      host: model-server
      subset: v2  # Mirror traffic to v2 for testing
    mirrorPercentage:
      value: 100.0  # Mirror 100% of traffic
```

### Circuit Breaking

Prevent cascading failures:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: circuit-breaker
spec:
  host: model-server
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

### Retries and Timeouts

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: retry-timeout
spec:
  hosts:
  - model-server
  http:
  - route:
    - destination:
        host: model-server
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

### Rate Limiting

```yaml
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: rate-limit
spec:
  workloadSelector:
    labels:
      app: model-server
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/udpa.type.v1.TypedStruct
          type_url: type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          value:
            stat_prefix: http_local_rate_limiter
            token_bucket:
              max_tokens: 100
              tokens_per_fill: 100
              fill_interval: 60s
```

## Observability and Tracing {#observability}

### Distributed Tracing with Jaeger

```yaml
# Enable tracing
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    enableTracing: true
    defaultConfig:
      tracing:
        sampling: 100.0  # 100% sampling (reduce in production)
        jaeger:
          url: http://jaeger-collector.istio-system:14268/api/traces
```

**Trace Context Propagation:**

```python
# In your application code
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/predict')
def predict():
    # Propagate trace headers
    headers = {}
    trace_headers = [
        'x-request-id',
        'x-b3-traceid',
        'x-b3-spanid',
        'x-b3-parentspanid',
        'x-b3-sampled',
        'x-b3-flags',
        'x-ot-span-context'
    ]

    for header in trace_headers:
        if header in request.headers:
            headers[header] = request.headers[header]

    # Call downstream service
    response = requests.get(
        'http://feature-service/features',
        headers=headers
    )

    # TODO: Add model prediction logic
    return {'prediction': 0.95}
```

### Metrics with Prometheus

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: istio-grafana-dashboards
data:
  istio-mesh-dashboard.json: |
    {
      "dashboard": {
        "title": "Istio Mesh Dashboard",
        "panels": [
          {
            "title": "Request Rate",
            "targets": [
              {
                "expr": "sum(rate(istio_requests_total{destination_service=\"model-server\"}[5m]))"
              }
            ]
          },
          {
            "title": "P95 Latency",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{destination_service=\"model-server\"}[5m])) by (le))"
              }
            ]
          }
        ]
      }
    }
```

### Service Graph Visualization

```bash
# Install Kiali for service mesh visualization
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.18/samples/addons/kiali.yaml

# Access Kiali dashboard
istioctl dashboard kiali
```

## Security with mTLS {#security}

### Enabling mTLS

**Permissive Mode (default):**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: ml-production
spec:
  mtls:
    mode: PERMISSIVE  # Allow both mTLS and plaintext
```

**Strict Mode:**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: ml-production
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic
```

**Per-Service mTLS:**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: model-server-mtls
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-server
  mtls:
    mode: STRICT
  portLevelMtls:
    8080:
      mode: DISABLE  # Disable mTLS for health checks
```

### Authorization Policies

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: model-server-authz
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-server
  action: ALLOW
  rules:
  # Allow from API gateway
  - from:
    - source:
        principals: ["cluster.local/ns/gateway/sa/api-gateway"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/v1/predict"]
  # Allow from monitoring
  - from:
    - source:
        namespaces: ["monitoring"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/metrics"]
---
# Deny by default
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: ml-production
spec:
  {}  # Empty policy denies all
```

### JWT Authentication

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-server
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "ml-api"
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: require-jwt
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-server
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]  # Require valid JWT
```

## Real-World ML Patterns

### Pattern 1: Multi-Model Serving with Traffic Split

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: multi-model-routing
spec:
  hosts:
  - inference.ml.svc.cluster.local
  http:
  # Route to appropriate model based on request
  - match:
    - headers:
        x-model-type:
          exact: "nlp"
    route:
    - destination:
        host: nlp-model-server
  - match:
    - headers:
        x-model-type:
          exact: "vision"
    route:
    - destination:
        host: vision-model-server
  - route:
    - destination:
        host: default-model-server
```

### Pattern 2: Feature Store Service Mesh

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: feature-store
spec:
  hosts:
  - feature-store
  http:
  - route:
    - destination:
        host: feature-store
    timeout: 50ms  # Strict SLA
    retries:
      attempts: 2
      perTryTimeout: 20ms
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: feature-store-lb
spec:
  host: feature-store
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: "x-user-id"  # Route same user to same pod
```

### Pattern 3: Training Job Communication

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: distributed-training
spec:
  hosts:
  - training-workers
  http:
  - route:
    - destination:
        host: training-workers
    timeout: 3600s  # Long timeout for training
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: training-workers
spec:
  host: training-workers
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http2MaxRequests: 1000
```

## Summary

Key takeaways:

1. **Kubernetes networking** provides flexible communication between pods, services, and external clients
2. **CNI plugins** implement the network model with different performance characteristics
3. **Service mesh** adds traffic management, security, and observability without code changes
4. **Istio** provides comprehensive features for production ML systems
5. **Traffic management** enables canary deployments, A/B testing, and traffic mirroring
6. **mTLS** secures service-to-service communication automatically
7. **Observability** through distributed tracing reveals system behavior

## Further Reading

- [Kubernetes Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Istio Documentation](https://istio.io/latest/docs/)
- [Linkerd Documentation](https://linkerd.io/2/overview/)
- [Envoy Proxy](https://www.envoyproxy.io/docs)

## Next Steps

Next lecture: **Security Best Practices** - Learn how to secure ML workloads with RBAC, Pod Security, and Network Policies.
