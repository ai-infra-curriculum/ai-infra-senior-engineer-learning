# Lab 04: Multi-Cluster Architecture Setup

## Objectives

1. Set up multiple Kubernetes clusters
2. Configure cluster federation with KubeFed
3. Implement cross-cluster service discovery
4. Set up data replication across clusters
5. Test failover scenarios
6. Monitor multi-cluster health

## Prerequisites

- Ability to create multiple Kubernetes clusters (cloud or local)
- kubectl, kubectx, kubens installed
- Understanding of Lecture 06: Multi-Cluster Architecture

## Estimated Time

8 hours

## Part 1: Create Multiple Clusters (1.5 hours)

### Create Three Clusters

```bash
# TODO: Create clusters using your preferred method

# Example with kind (local)
kind create cluster --name cluster-us-west --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

kind create cluster --name cluster-us-east --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF

kind create cluster --name cluster-eu-west --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
EOF

# Verify clusters
kubectl config get-contexts

# Set up kubectx aliases
kubectx us-west=kind-cluster-us-west
kubectx us-east=kind-cluster-us-east
kubectx eu-west=kind-cluster-eu-west
```

## Part 2: Install KubeFed (2 hours)

### Install KubeFed on Host Cluster

```bash
# TODO: Choose us-west as host cluster
kubectx us-west

# Install KubeFed
kubectl apply -k "github.com/kubernetes-sigs/kubefed/manifests/kubefed?ref=v0.10.0"

# Wait for KubeFed pods
kubectl wait --for=condition=ready pod --all -n kube-federation-system --timeout=300s

# Verify installation
kubectl get pods -n kube-federation-system
```

### Install kubefedctl

```bash
# TODO: Install kubefedctl CLI
curl -LO https://github.com/kubernetes-sigs/kubefed/releases/download/v0.10.0/kubefedctl-0.10.0-linux-amd64.tgz
tar -xzf kubefedctl-0.10.0-linux-amd64.tgz
sudo mv kubefedctl /usr/local/bin/
```

### Join Clusters to Federation

```bash
# TODO: Join all three clusters
kubefedctl join us-west \
  --cluster-context us-west \
  --host-cluster-context us-west \
  --v=2

kubefedctl join us-east \
  --cluster-context us-east \
  --host-cluster-context us-west \
  --v=2

kubefedctl join eu-west \
  --cluster-context eu-west \
  --host-cluster-context us-west \
  --v=2

# Verify clusters joined
kubectl get kubefedclusters -n kube-federation-system
```

## Part 3: Deploy Federated Application (2 hours)

### Create Namespace in All Clusters

```yaml
# TODO: Apply federated namespace
apiVersion: types.kubefed.io/v1beta1
kind: FederatedNamespace
metadata:
  name: ml-production
  namespace: ml-production
spec:
  placement:
    clusters:
    - name: us-west
    - name: us-east
    - name: eu-west
```

### Deploy Federated Model Service

```yaml
# TODO: Create federated deployment
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: model-server
  namespace: ml-production
spec:
  template:
    metadata:
      labels:
        app: model-server
    spec:
      replicas: 10
      selector:
        matchLabels:
          app: model-server
      template:
        metadata:
          labels:
            app: model-server
        spec:
          containers:
          - name: server
            image: hashicorp/http-echo:latest
            args:
            - "-text=Model Server"
            ports:
            - containerPort: 5678
  placement:
    clusters:
    - name: us-west
    - name: us-east
    - name: eu-west
  overrides:
  # More replicas in primary region
  - clusterName: us-west
    clusterOverrides:
    - path: "/spec/replicas"
      value: 20
  - clusterName: us-east
    clusterOverrides:
    - path: "/spec/replicas"
      value: 15
  - clusterName: eu-west
    clusterOverrides:
    - path: "/spec/replicas"
      value: 10
```

### Verify Deployment Across Clusters

```bash
# TODO: Check deployment in each cluster
kubectx us-west
kubectl get pods -n ml-production

kubectx us-east
kubectl get pods -n ml-production

kubectx eu-west
kubectl get pods -n ml-production

# Count pods per cluster
echo "US-West: $(kubectl get pods -n ml-production --context=us-west --no-headers | wc -l)"
echo "US-East: $(kubectl get pods -n ml-production --context=us-east --no-headers | wc -l)"
echo "EU-West: $(kubectl get pods -n ml-production --context=eu-west --no-headers | wc -l)"
```

## Part 4: Cross-Cluster Service Discovery (1.5 hours)

### Deploy Service Export (for each cluster)

```bash
# TODO: In us-west cluster
kubectx us-west
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: model-server
  namespace: ml-production
spec:
  selector:
    app: model-server
  ports:
  - port: 8080
    targetPort: 5678
EOF

# Repeat for us-east and eu-west
```

### Test Cross-Cluster Connectivity

```bash
# TODO: Deploy test pod in each cluster
for ctx in us-west us-east eu-west; do
  kubectl --context=$ctx run test-client -n ml-production \
    --image=curlimages/curl:latest \
    --rm -it --restart=Never \
    -- curl model-server.ml-production:8080
done
```

## Part 5: Data Replication (1.5 hours)

### Deploy PostgreSQL in Each Cluster

```yaml
# TODO: Deploy PostgreSQL with replication
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: postgres
  namespace: ml-production
spec:
  template:
    metadata:
      labels:
        app: postgres
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: postgres
      template:
        metadata:
          labels:
            app: postgres
        spec:
          containers:
          - name: postgres
            image: postgres:15
            env:
            - name: POSTGRES_PASSWORD
              value: "password"
            - name: POSTGRES_DB
              value: mldb
            ports:
            - containerPort: 5432
  placement:
    clusters:
    - name: us-west
    - name: us-east
    - name: eu-west
```

### Configure Replication

```bash
# TODO: Set up logical replication between PostgreSQL instances
# Note: This is simplified for lab purposes

# In primary (us-west)
kubectx us-west
kubectl exec -it -n ml-production postgres-xxx -- psql -U postgres -d mldb <<EOF
-- Configure primary
ALTER SYSTEM SET wal_level = logical;
CREATE PUBLICATION ml_pub FOR ALL TABLES;
EOF

# In replicas (us-east, eu-west)
# TODO: Configure subscriptions to primary
```

## Part 6: Failover Testing (1.5 hours)

### Simulate Primary Cluster Failure

```bash
# TODO: Scale down model-server in us-west
kubectx us-west
kubectl scale deployment model-server -n ml-production --replicas=0

# Verify traffic shifts to other clusters
# (requires external load balancer configuration)
```

### Automated Failover with External-DNS

```yaml
# TODO: Configure external-DNS for automatic failover
apiVersion: v1
kind: Service
metadata:
  name: model-server
  namespace: ml-production
  annotations:
    external-dns.alpha.kubernetes.io/hostname: api.ml.example.com
    external-dns.alpha.kubernetes.io/ttl: "60"
spec:
  type: LoadBalancer
  selector:
    app: model-server
  ports:
  - port: 80
    targetPort: 5678
```

### Test Failback

```bash
# TODO: Restore us-west cluster
kubectx us-west
kubectl scale deployment model-server -n ml-production --replicas=20

# Verify traffic returns to us-west
# Monitor DNS changes
```

## Part 7: Multi-Cluster Monitoring (1 hour)

### Deploy Prometheus Federation

```yaml
# TODO: Configure Prometheus to scrape all clusters
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 30s

    scrape_configs:
    # Federate from us-west
    - job_name: 'federate-us-west'
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="kubernetes-pods"}'
      static_configs:
      - targets:
        - 'prometheus.us-west:9090'
        labels:
          cluster: 'us-west'

    # Federate from us-east
    - job_name: 'federate-us-east'
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="kubernetes-pods"}'
      static_configs:
      - targets:
        - 'prometheus.us-east:9090'
        labels:
          cluster: 'us-east'

    # Federate from eu-west
    - job_name: 'federate-eu-west'
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="kubernetes-pods"}'
      static_configs:
      - targets:
        - 'prometheus.eu-west:9090'
        labels:
          cluster: 'eu-west'
```

### Create Multi-Cluster Dashboard

```yaml
# TODO: Create Grafana dashboard showing all clusters
# Dashboard should include:
# - Pod count per cluster
# - Request rate per cluster
# - Latency per cluster
# - Error rate per cluster
```

## Deliverables

1. **Three Kubernetes clusters** configured and joined to federation
2. **Federated application** deployed across all clusters
3. **Cross-cluster service discovery** working
4. **Data replication** configured between clusters
5. **Failover testing** documented with results
6. **Multi-cluster monitoring** set up
7. **Documentation** including:
   - Architecture diagram
   - Failover procedures
   - Troubleshooting guide
   - Cost analysis

## Testing Checklist

- [ ] All three clusters healthy
- [ ] KubeFed installed and operational
- [ ] Clusters joined to federation
- [ ] Application deployed to all clusters
- [ ] Replica counts match override specifications
- [ ] Cross-cluster service discovery works
- [ ] Data replication functional
- [ ] Failover tested successfully
- [ ] Failback tested successfully
- [ ] Multi-cluster monitoring operational
- [ ] Documentation complete

## Troubleshooting

### Cluster Join Fails

```bash
# Check kubefed controller logs
kubectl logs -n kube-federation-system -l control-plane=controller-manager

# Verify cluster connectivity
kubectl --context=us-west cluster-info
kubectl --context=us-east cluster-info

# Check kubefedcluster status
kubectl get kubefedclusters -n kube-federation-system -o yaml
```

### Federated Resource Not Propagating

```bash
# Check federated resource
kubectl get federateddeployments -n ml-production

# Check propagation status
kubectl describe federateddeployment model-server -n ml-production

# Check sync controller logs
kubectl logs -n kube-federation-system -l control-plane=controller-manager | grep -i sync
```

## Bonus Challenges

1. Implement **GitOps with ArgoCD ApplicationSets** for multi-cluster deployments
2. Set up **service mesh across clusters** with Istio multi-primary
3. Implement **global load balancing** with cloud provider services
4. Create **automated DR drills** with scheduled failover tests
5. Implement **cost optimization** by shutting down DR cluster during off-hours
6. Set up **compliance controls** across all clusters

## Cleanup

```bash
# Delete all test resources
kubectl delete namespace ml-production --context=us-west
kubectl delete namespace ml-production --context=us-east
kubectl delete namespace ml-production --context=eu-west

# Delete clusters (if using kind)
kind delete cluster --name cluster-us-west
kind delete cluster --name cluster-us-east
kind delete cluster --name cluster-eu-west
```

## Additional Resources

- [KubeFed Documentation](https://github.com/kubernetes-sigs/kubefed)
- [Multi-Cluster Patterns](https://kubernetes.io/docs/concepts/cluster-administration/federation/)
- [Rancher Multi-Cluster Management](https://rancher.com/docs/)

---

**Multi-cluster architectures are complex but essential for production ML systems at scale.**
