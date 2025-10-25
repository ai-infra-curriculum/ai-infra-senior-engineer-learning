# Lab 03: Deploy and Configure Service Mesh for ML Services

## Objectives

1. Install Istio service mesh
2. Configure automatic sidecar injection
3. Implement traffic splitting for A/B testing models
4. Set up distributed tracing for ML inference pipeline
5. Configure mTLS between services
6. Create authorization policies for model access

## Prerequisites

- Kubernetes cluster (3+ nodes recommended)
- kubectl access
- istioctl CLI installed
- Understanding of Lecture 04: Networking and Service Mesh

## Estimated Time

8 hours

## Part 1: Install Istio (1 hour)

### Download and Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.19.0
export PATH=$PWD/bin:$PATH

# Verify istioctl
istioctl version

# Install Istio with demo profile (for learning)
istioctl install --set profile=demo -y

# For production, use:
# istioctl install --set profile=production -y

# Verify installation
kubectl get pods -n istio-system
kubectl get svc -n istio-system

# Install observability addons
kubectl apply -f samples/addons/prometheus.yaml
kubectl apply -f samples/addons/grafana.yaml
kubectl apply -f samples/addons/jaeger.yaml
kubectl apply -f samples/addons/kiali.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n istio-system --timeout=300s
```

### Enable Sidecar Injection

```bash
# TODO: Create namespace for ML services
kubectl create namespace ml-services

# Enable automatic sidecar injection
kubectl label namespace ml-services istio-injection=enabled

# Verify label
kubectl get namespace ml-services --show-labels
```

## Part 2: Deploy ML Services (1.5 hours)

### Deploy Feature Store Service

```yaml
# TODO: Apply this manifest
apiVersion: v1
kind: Service
metadata:
  name: feature-store
  namespace: ml-services
  labels:
    app: feature-store
spec:
  ports:
  - port: 6379
    name: redis
  selector:
    app: feature-store
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: feature-store
  namespace: ml-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: feature-store
  template:
    metadata:
      labels:
        app: feature-store
        version: v1
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### Deploy Model Inference Service (V1)

```yaml
# TODO: Apply model inference v1
apiVersion: v1
kind: Service
metadata:
  name: model-inference
  namespace: ml-services
  labels:
    app: model-inference
spec:
  ports:
  - port: 8080
    name: http
  selector:
    app: model-inference
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-inference-v1
  namespace: ml-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-inference
      version: v1
  template:
    metadata:
      labels:
        app: model-inference
        version: v1
    spec:
      containers:
      - name: inference
        image: hashicorp/http-echo:latest
        args:
        - "-text=Model v1 prediction"
        ports:
        - containerPort: 5678
        env:
        - name: VERSION
          value: "v1"
```

### Deploy Model Inference Service (V2)

```yaml
# TODO: Apply model inference v2 (new model version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-inference-v2
  namespace: ml-services
spec:
  replicas: 1  # Start with fewer replicas for canary
  selector:
    matchLabels:
      app: model-inference
      version: v2
  template:
    metadata:
      labels:
        app: model-inference
        version: v2
    spec:
      containers:
      - name: inference
        image: hashicorp/http-echo:latest
        args:
        - "-text=Model v2 prediction (NEW)"
        ports:
        - containerPort: 5678
        env:
        - name: VERSION
          value: "v2"
```

### Verify Sidecars Injected

```bash
# TODO: Check that sidecars are injected
kubectl get pods -n ml-services

# Should see 2/2 containers per pod (app + envoy sidecar)
kubectl describe pod -n ml-services -l app=model-inference | grep -A 5 "Containers:"
```

## Part 3: Traffic Management (2 hours)

### Create Gateway for External Traffic

```yaml
# TODO: Create gateway for ingress traffic
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: ml-gateway
  namespace: ml-services
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

### Create VirtualService for Routing

```yaml
# TODO: Create basic routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference-vs
  namespace: ml-services
spec:
  hosts:
  - "*"
  gateways:
  - ml-gateway
  http:
  - match:
    - uri:
        prefix: "/predict"
    route:
    - destination:
        host: model-inference
        port:
          number: 8080
        subset: v1
      weight: 100
```

### Create DestinationRule for Subsets

```yaml
# TODO: Define v1 and v2 subsets
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: model-inference-dr
  namespace: ml-services
spec:
  host: model-inference
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Test Traffic Routing

```bash
# Get ingress gateway URL
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT

# Test requests (should all go to v1)
for i in {1..10}; do
  curl -s http://$GATEWAY_URL/predict
done
```

### Implement Canary Deployment (10% v2)

```yaml
# TODO: Update VirtualService for 90/10 split
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference-vs
  namespace: ml-services
spec:
  hosts:
  - "*"
  gateways:
  - ml-gateway
  http:
  - match:
    - uri:
        prefix: "/predict"
    route:
    - destination:
        host: model-inference
        subset: v1
      weight: 90
    - destination:
        host: model-inference
        subset: v2
      weight: 10
```

### Test Canary Deployment

```bash
# TODO: Send 100 requests and count v1 vs v2 responses
for i in {1..100}; do
  curl -s http://$GATEWAY_URL/predict
done | sort | uniq -c
```

### Implement A/B Testing (User-Based)

```yaml
# TODO: Route based on user header
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference-ab
  namespace: ml-services
spec:
  hosts:
  - model-inference
  http:
  # Beta users get v2
  - match:
    - headers:
        x-user-group:
          exact: "beta"
    route:
    - destination:
        host: model-inference
        subset: v2
  # Everyone else gets v1
  - route:
    - destination:
        host: model-inference
        subset: v1
```

### Test A/B Testing

```bash
# Regular user (should get v1)
curl -H "x-user-group: regular" http://$GATEWAY_URL/predict

# Beta user (should get v2)
curl -H "x-user-group: beta" http://$GATEWAY_URL/predict
```

## Part 4: Distributed Tracing (1.5 hours)

### Access Jaeger Dashboard

```bash
# Port-forward to Jaeger
kubectl port-forward -n istio-system svc/tracing 16686:80

# Open browser to http://localhost:16686
```

### Generate Traffic with Trace Headers

```bash
# TODO: Send requests that generate traces
for i in {1..50}; do
  curl -H "x-request-id: test-$i" http://$GATEWAY_URL/predict
  sleep 0.5
done
```

### Analyze Trace Data

1. Open Jaeger UI (http://localhost:16686)
2. Select "istio-ingressgateway" service
3. Click "Find Traces"
4. Explore trace details:
   - Request latency
   - Service dependencies
   - Error rates

### TODO: Answer these questions from trace data

```markdown
1. What is the average end-to-end latency?
2. How many services are in the request path?
3. What is the latency breakdown by service?
4. Are there any failed requests? What caused them?
```

## Part 5: Security with mTLS (1.5 hours)

### Enable Strict mTLS

```yaml
# TODO: Enforce strict mTLS for ml-services namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: ml-services
spec:
  mtls:
    mode: STRICT
```

### Verify mTLS

```bash
# TODO: Check mTLS status
istioctl authn tls-check model-inference-v1-xxxxx.ml-services feature-store.ml-services

# Should show mTLS enabled
```

### Create Authorization Policy

```yaml
# TODO: Restrict access to model-inference
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: model-inference-authz
  namespace: ml-services
spec:
  selector:
    matchLabels:
      app: model-inference
  action: ALLOW
  rules:
  # Allow from ingress gateway
  - from:
    - source:
        principals: ["cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account"]
  # Allow from other services in ml-services namespace
  - from:
    - source:
        namespaces: ["ml-services"]
```

### Test Authorization

```bash
# TODO: Try to access from unauthorized pod
kubectl run -n default test-pod --image=curlimages/curl:latest --rm -it -- sh
# In pod:
curl -v model-inference.ml-services:8080/predict
# Should get RBAC: access denied
```

### Add Metrics Access for Prometheus

```yaml
# TODO: Allow Prometheus to scrape metrics
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-prometheus
  namespace: ml-services
spec:
  action: ALLOW
  rules:
  - from:
    - source:
        namespaces: ["istio-system"]
        principals: ["cluster.local/ns/istio-system/sa/prometheus"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/stats/prometheus"]
```

## Part 6: Resilience Patterns (1.5 hours)

### Circuit Breaking

```yaml
# TODO: Add circuit breaker to feature-store
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: feature-store-cb
  namespace: ml-services
spec:
  host: feature-store
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

### Retry Policy

```yaml
# TODO: Add retry logic for model-inference
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference-retry
  namespace: ml-services
spec:
  hosts:
  - model-inference
  http:
  - route:
    - destination:
        host: model-inference
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

### Test Resilience

```bash
# TODO: Deploy fault injection to test retry
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-inference-fault
  namespace: ml-services
spec:
  hosts:
  - model-inference
  http:
  - fault:
      delay:
        percentage:
          value: 50
        fixedDelay: 5s
    route:
    - destination:
        host: model-inference
EOF

# Send requests and observe retry behavior
time curl http://$GATEWAY_URL/predict
```

## Part 7: Observability (1 hour)

### Access Kiali Dashboard

```bash
# Port-forward to Kiali
kubectl port-forward -n istio-system svc/kiali 20001:20001

# Open browser to http://localhost:20001
# Default credentials: admin/admin
```

### Access Grafana Dashboard

```bash
# Port-forward to Grafana
kubectl port-forward -n istio-system svc/grafana 3000:3000

# Open browser to http://localhost:3000
# Navigate to Istio dashboards
```

### TODO: Explore Metrics

In Grafana, explore these Istio dashboards:
1. Istio Mesh Dashboard - Overall cluster metrics
2. Istio Service Dashboard - Per-service metrics
3. Istio Workload Dashboard - Per-pod metrics
4. Istio Performance Dashboard - Latency and throughput

Answer these questions:
```markdown
1. What is the request rate to model-inference?
2. What is the P95 latency?
3. What is the error rate?
4. How is traffic distributed between v1 and v2?
```

## Deliverables

1. **Istio installation** with observability addons
2. **ML services** deployed with sidecars
3. **Traffic management** with canary and A/B testing
4. **Distributed tracing** configured and analyzed
5. **mTLS** enabled and verified
6. **Authorization policies** enforced
7. **Resilience patterns** implemented and tested
8. **Observability dashboards** configured
9. **Documentation** of:
   - Service mesh architecture
   - Traffic routing strategy
   - Security policies
   - Observed metrics

## Testing Checklist

- [ ] Istio control plane healthy
- [ ] Sidecars injected into all pods
- [ ] Traffic routing works (v1 and v2)
- [ ] Canary deployment functional
- [ ] A/B testing based on headers
- [ ] Traces visible in Jaeger
- [ ] mTLS enforced
- [ ] Authorization policies working
- [ ] Circuit breaker triggers correctly
- [ ] Retries happen on failures
- [ ] Kiali shows service graph
- [ ] Grafana shows metrics

## Troubleshooting

### Sidecars Not Injected

```bash
# Check namespace label
kubectl get namespace ml-services --show-labels

# Check webhook
kubectl get mutatingwebhookconfigurations

# Manual injection if needed
istioctl kube-inject -f deployment.yaml | kubectl apply -f -
```

### Traffic Not Routing Correctly

```bash
# Check VirtualService
kubectl get virtualservice -n ml-services
kubectl describe virtualservice model-inference-vs -n ml-services

# Check DestinationRule
kubectl get destinationrule -n ml-services
kubectl describe destinationrule model-inference-dr -n ml-services

# Check proxy config
istioctl proxy-config routes <pod-name> -n ml-services
```

### mTLS Issues

```bash
# Check mTLS status
istioctl authn tls-check <pod-name> <service-name>

# Check peer authentication
kubectl get peerauthentication -n ml-services

# Debug with proxy logs
kubectl logs -n ml-services <pod-name> -c istio-proxy
```

## Bonus Challenges

1. Implement **traffic mirroring** to test v2 without affecting users
2. Add **rate limiting** for model inference API
3. Configure **external authorization** with OPA
4. Set up **multi-cluster service mesh**
5. Implement **circuit breaker testing** with chaos engineering
6. Create **custom dashboards** for ML-specific metrics

## Additional Resources

- [Istio Documentation](https://istio.io/latest/docs/)
- [Istio Tasks](https://istio.io/latest/docs/tasks/)
- [Kiali Documentation](https://kiali.io/docs/)
- [Service Mesh Patterns](https://www.manning.com/books/service-mesh-patterns)

---

**Service mesh adds complexity but provides powerful capabilities. Use it when benefits outweigh operational overhead.**
