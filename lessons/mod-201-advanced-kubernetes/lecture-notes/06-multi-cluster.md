# Lecture 06: Multi-Cluster Architecture

## Learning Objectives

By the end of this lecture, you will be able to:

- Design multi-cluster architectures for ML platforms including geographic, environment-based, and hybrid patterns
- Implement cluster federation for unified management of distributed Kubernetes clusters
- Configure cross-cluster service discovery and load balancing for global ML inference services
- Design and implement data replication strategies for distributed training and inference workloads
- Architect multi-cloud and hybrid cloud solutions to avoid vendor lock-in and optimize costs
- Implement disaster recovery and failover mechanisms for business-critical ML services
- Optimize costs across multiple clusters using spot instances, reserved capacity, and intelligent workload placement
- Evaluate trade-offs between single-cluster scaling and multi-cluster distribution for ML workloads

## Table of Contents
1. [Introduction to Multi-Cluster](#introduction)
2. [Multi-Cluster Design Patterns](#design-patterns)
3. [Cluster Federation](#federation)
4. [Cross-Cluster Service Discovery](#service-discovery)
5. [Data Replication](#data-replication)
6. [Multi-Cloud and Hybrid Cloud](#multi-cloud)
7. [Disaster Recovery and Failover](#disaster-recovery)
8. [Cost Optimization](#cost-optimization)

## Introduction to Multi-Cluster {#introduction}

### Why Multi-Cluster for ML?

**Reasons for multiple clusters:**

1. **Geographic Distribution:** Reduce latency for global users
2. **Regulatory Compliance:** Data sovereignty requirements
3. **Failure Isolation:** Blast radius containment
4. **Environment Separation:** Dev, staging, production
5. **Resource Optimization:** Different workload types (training vs inference)
6. **Multi-Cloud Strategy:** Avoid vendor lock-in, leverage best-of-breed services
7. **Scale Beyond Single Cluster:** Some organizations outgrow single cluster limits
8. **Cost Optimization:** Mix on-demand, spot, and different cloud providers

### Multi-Cluster Architecture Patterns

```
Pattern 1: Environment-Based
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Dev Cluster  │  │ Stage Cluster│  │ Prod Cluster │
│  US-West-2   │  │  US-West-2   │  │  US-West-2   │
└──────────────┘  └──────────────┘  └──────────────┘

Pattern 2: Geographic
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ US Cluster   │  │  EU Cluster  │  │ Asia Cluster │
│  US-West-2   │  │  EU-West-1   │  │  AP-SE-1     │
└──────────────┘  └──────────────┘  └──────────────┘

Pattern 3: Workload-Based
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Training    │  │  Inference   │  │  Batch Jobs  │
│  GPU Nodes   │  │  CPU Nodes   │  │ Spot Nodes   │
└──────────────┘  └──────────────┘  └──────────────┘

Pattern 4: Hybrid Multi-Cloud
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ AWS Cluster  │  │  GCP Cluster │  │ On-Prem      │
│  Primary     │  │  DR/Backup   │  │  Data Center │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Challenges

1. **Complexity:** Managing multiple control planes
2. **Networking:** Cross-cluster communication
3. **Identity:** Unified authentication and authorization
4. **Data Consistency:** State synchronization
5. **Observability:** Centralized monitoring
6. **Cost:** Overhead of multiple clusters

## Multi-Cluster Design Patterns {#design-patterns}

### Pattern 1: Active-Passive (DR)

Primary cluster handles all traffic; passive cluster for disaster recovery.

```yaml
# Primary cluster (us-west-2)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
  namespace: production
  labels:
    cluster: primary
spec:
  replicas: 20
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
        image: model-server:v1.0.0
        resources:
          limits:
            cpu: "4"
            memory: 8Gi
---
# DR cluster (us-east-1) - scaled down
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
  namespace: production
  labels:
    cluster: dr
spec:
  replicas: 2  # Minimal for health checks
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
        image: model-server:v1.0.0
```

### Pattern 2: Active-Active (Multi-Region)

All clusters actively serve traffic.

```yaml
# Configuration replicated across all clusters
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
  namespace: production
spec:
  replicas: 15
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
        region: ${REGION}  # Templated per cluster
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: model-server
            topologyKey: topology.kubernetes.io/zone
      containers:
      - name: server
        image: model-server:v1.0.0
        env:
        - name: REGION
          value: ${REGION}
        - name: FEATURE_STORE_ENDPOINT
          value: feature-store.${REGION}.example.com
```

### Pattern 3: Workload Segregation

Different clusters for different workload types.

```yaml
# Training Cluster - GPU-optimized
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: kube-system
data:
  cluster-type: "training"
  gpu-enabled: "true"
  autoscaler-config: |
    minNodes: 5
    maxNodes: 100
    scaleDownDelay: 10m
---
# Inference Cluster - CPU-optimized
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: kube-system
data:
  cluster-type: "inference"
  gpu-enabled: "false"
  autoscaler-config: |
    minNodes: 10
    maxNodes: 50
    scaleDownDelay: 5m
```

## Cluster Federation {#federation}

### KubeFed (Kubernetes Federation v2)

Synchronize resources across clusters.

**Installing KubeFed:**

```bash
# Install KubeFed controller
kubectl apply -k "github.com/kubernetes-sigs/kubefed/manifests/kubefed?ref=v0.10.0"

# Join clusters to federation
kubefedctl join us-west --cluster-context=us-west-context --host-cluster-context=host-context
kubefedctl join us-east --cluster-context=us-east-context --host-cluster-context=host-context
kubefedctl join eu-west --cluster-context=eu-west-context --host-cluster-context=host-context
```

**Federated Deployment:**

```yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: model-server
  namespace: production
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
            image: model-server:v1.0.0
  placement:
    clusters:
    - name: us-west
    - name: us-east
    - name: eu-west
  overrides:
  - clusterName: us-west
    clusterOverrides:
    - path: "/spec/replicas"
      value: 20  # More replicas in primary region
  - clusterName: us-east
    clusterOverrides:
    - path: "/spec/replicas"
      value: 15
  - clusterName: eu-west
    clusterOverrides:
    - path: "/spec/replicas"
      value: 10
```

**Federated Service:**

```yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedService
metadata:
  name: model-server
  namespace: production
spec:
  template:
    metadata:
      labels:
        app: model-server
    spec:
      selector:
        app: model-server
      ports:
      - port: 8080
        targetPort: 8080
  placement:
    clusters:
    - name: us-west
    - name: us-east
    - name: eu-west
```

### GitOps for Multi-Cluster

**ArgoCD Multi-Cluster Setup:**

```yaml
# ApplicationSet for multi-cluster deployment
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: model-server-multicluster
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: us-west-2
        url: https://us-west-2.k8s.example.com
        replicas: "20"
        region: us-west-2
      - cluster: us-east-1
        url: https://us-east-1.k8s.example.com
        replicas: "15"
        region: us-east-1
      - cluster: eu-west-1
        url: https://eu-west-1.k8s.example.com
        replicas: "10"
        region: eu-west-1
  template:
    metadata:
      name: 'model-server-{{cluster}}'
    spec:
      project: production
      source:
        repoURL: https://github.com/example/ml-platform
        targetRevision: main
        path: deployments/model-server
        helm:
          parameters:
          - name: replicas
            value: '{{replicas}}'
          - name: region
            value: '{{region}}'
      destination:
        server: '{{url}}'
        namespace: production
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

**Flux Multi-Cluster:**

```yaml
# Flux Kustomization per cluster
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: model-server-us-west
  namespace: flux-system
spec:
  interval: 5m
  path: ./clusters/us-west-2/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  kubeConfig:
    secretRef:
      name: us-west-kubeconfig
---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: model-server-us-east
  namespace: flux-system
spec:
  interval: 5m
  path: ./clusters/us-east-1/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: fleet-infra
  kubeConfig:
    secretRef:
      name: us-east-kubeconfig
```

## Cross-Cluster Service Discovery {#service-discovery}

### Multi-Cluster Services (MCS)

```yaml
# Export service from cluster A
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: feature-store
  namespace: ml-services
---
# Import in cluster B
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceImport
metadata:
  name: feature-store
  namespace: ml-services
spec:
  type: ClusterSetIP
  ports:
  - port: 6379
    protocol: TCP
```

**Access imported service:**
```
feature-store.ml-services.svc.clusterset.local
```

### Istio Multi-Cluster Service Mesh

**Shared Control Plane:**

```bash
# Install Istio on primary cluster
istioctl install --set profile=demo \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster1 \
  --set values.global.network=network1

# Install on remote cluster
istioctl install --set profile=remote \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=cluster2 \
  --set values.global.network=network2 \
  --set values.global.remotePilotAddress=<primary-istio-pilot-ip>
```

**ServiceEntry for Cross-Cluster:**

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: feature-store-remote
spec:
  hosts:
  - feature-store.ml-services.svc.cluster2.local
  location: MESH_INTERNAL
  ports:
  - number: 6379
    name: redis
    protocol: TCP
  resolution: DNS
  endpoints:
  - address: feature-store.ml-services.svc.cluster2.local
    labels:
      cluster: cluster2
```

### Submariner for Cross-Cluster Networking

Direct pod-to-pod communication across clusters.

```bash
# Deploy Submariner broker on primary cluster
subctl deploy-broker --kubeconfig primary-kubeconfig

# Join clusters
subctl join --kubeconfig cluster1-kubeconfig broker-info.subm
subctl join --kubeconfig cluster2-kubeconfig broker-info.subm

# Export service
subctl export service feature-store --namespace ml-services --kubeconfig cluster1-kubeconfig
```

## Data Replication {#data-replication}

### Database Replication

**PostgreSQL Multi-Master:**

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: feature-store-db
spec:
  instances: 3
  primaryUpdateStrategy: unsupervised

  # Multi-region replication
  replica:
    enabled: true
    source: feature-store-db-us-west

  storage:
    storageClass: fast-ssd
    size: 1Ti

  backup:
    barmanObjectStore:
      destinationPath: s3://ml-backups/feature-store-db
      s3Credentials:
        accessKeyId:
          name: aws-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: aws-credentials
          key: SECRET_ACCESS_KEY
```

### Object Storage Replication

**S3 Cross-Region Replication:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: s3-replication-config
data:
  replication.json: |
    {
      "Role": "arn:aws:iam::123456789:role/s3-replication",
      "Rules": [
        {
          "Status": "Enabled",
          "Priority": 1,
          "Filter": {"Prefix": "models/"},
          "Destination": {
            "Bucket": "arn:aws:s3:::ml-models-eu-west-1",
            "ReplicationTime": {
              "Status": "Enabled",
              "Time": {"Minutes": 15}
            }
          }
        }
      ]
    }
```

### Persistent Volume Replication

**Velero for Volume Backup/Restore:**

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: ml-volumes-backup
  namespace: velero
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  template:
    includedNamespaces:
    - ml-production
    includedResources:
    - persistentvolumeclaims
    - persistentvolumes
    snapshotVolumes: true
    storageLocation: default
    volumeSnapshotLocations:
    - us-west-2
    - us-east-1
```

## Multi-Cloud and Hybrid Cloud {#multi-cloud}

### Multi-Cloud Cluster Setup

**AWS EKS:**
```bash
eksctl create cluster \
  --name ml-aws-cluster \
  --region us-west-2 \
  --nodegroup-name gpu-nodes \
  --node-type p3.8xlarge \
  --nodes 5 \
  --nodes-min 0 \
  --nodes-max 20
```

**GCP GKE:**
```bash
gcloud container clusters create ml-gcp-cluster \
  --region us-central1 \
  --machine-type n1-standard-16 \
  --accelerator type=nvidia-tesla-v100,count=4 \
  --num-nodes 5 \
  --enable-autoscaling \
  --min-nodes 0 \
  --max-nodes 20
```

**Azure AKS:**
```bash
az aks create \
  --resource-group ml-resources \
  --name ml-azure-cluster \
  --location eastus \
  --node-count 5 \
  --node-vm-size Standard_NC24 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 20
```

### Unified Management

**Rancher for Multi-Cloud:**

```yaml
apiVersion: management.cattle.io/v3
kind: Cluster
metadata:
  name: ml-aws-cluster
spec:
  displayName: "ML AWS Cluster"
  eksConfig:
    amazonCredentialSecret: aws-credentials
    region: us-west-2
    kubernetesVersion: "1.27"
    nodeGroups:
    - name: gpu-nodes
      instanceType: p3.8xlarge
      desiredSize: 5
      minSize: 0
      maxSize: 20
---
apiVersion: management.cattle.io/v3
kind: Cluster
metadata:
  name: ml-gcp-cluster
spec:
  displayName: "ML GCP Cluster"
  gkeConfig:
    googleCredentialSecret: gcp-credentials
    region: us-central1
    kubernetesVersion: "1.27"
    nodePools:
    - name: gpu-nodes
      machineType: n1-standard-16
      initialNodeCount: 5
      autoscaling:
        enabled: true
        minNodeCount: 0
        maxNodeCount: 20
```

### Cost-Aware Multi-Cloud Scheduling

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloud-cost-config
data:
  pricing.yaml: |
    aws:
      p3.8xlarge: 12.24  # per hour
      us-west-2: 0.01    # data transfer per GB
    gcp:
      n1-standard-16-v100x4: 10.52
      us-central1: 0.01
    azure:
      Standard_NC24: 11.16
      eastus: 0.01

    # Job scheduler uses this to pick cheapest available
```

## Disaster Recovery and Failover {#disaster-recovery}

### DR Strategy

**RTO (Recovery Time Objective):** Time to recover
**RPO (Recovery Point Objective):** Acceptable data loss

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dr-requirements
data:
  tiers: |
    tier1:  # Critical inference services
      rto: 5m
      rpo: 0
      strategy: active-active

    tier2:  # Important batch jobs
      rto: 1h
      rpo: 15m
      strategy: active-passive

    tier3:  # Development workloads
      rto: 24h
      rpo: 24h
      strategy: backup-restore
```

### Automated Failover

**External-DNS for Traffic Shifting:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-inference
  annotations:
    external-dns.alpha.kubernetes.io/hostname: api.ml.example.com
    external-dns.alpha.kubernetes.io/ttl: "60"
spec:
  type: LoadBalancer
  selector:
    app: model-server
  ports:
  - port: 443
    targetPort: 8080
```

**Health-Based Failover:**

```python
# Simple health-check based failover
import requests
import time

PRIMARY_CLUSTER = "https://us-west-2.ml.example.com"
DR_CLUSTER = "https://us-east-1.ml.example.com"

def check_health(cluster_url):
    try:
        response = requests.get(f"{cluster_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def update_dns(cluster_url):
    # TODO: Update DNS to point to healthy cluster
    pass

while True:
    if not check_health(PRIMARY_CLUSTER):
        print("Primary cluster unhealthy, failing over to DR")
        update_dns(DR_CLUSTER)
    else:
        update_dns(PRIMARY_CLUSTER)
    time.sleep(30)
```

### Testing DR

```bash
#!/bin/bash
# DR Drill Script

echo "Starting DR drill..."

# 1. Simulate primary cluster failure
kubectl --context=primary scale deployment model-server --replicas=0

# 2. Verify DR cluster takes over
sleep 60
curl https://api.ml.example.com/health

# 3. Check traffic routing
for i in {1..100}; do
  curl -s https://api.ml.example.com/predict | jq -r .cluster
done | sort | uniq -c

# 4. Restore primary
kubectl --context=primary scale deployment model-server --replicas=20

# 5. Verify failback
sleep 60
for i in {1..100}; do
  curl -s https://api.ml.example.com/predict | jq -r .cluster
done | sort | uniq -c

echo "DR drill complete"
```

## Cost Optimization {#cost-optimization}

### Spot Instance Management

```yaml
# Mix of on-demand and spot across clusters
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: training-spot
spec:
  requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: ["spot"]
  - key: node.kubernetes.io/instance-type
    operator: In
    values: ["p3.8xlarge", "p3.16xlarge"]
  limits:
    resources:
      nvidia.com/gpu: 100
  ttlSecondsAfterEmpty: 30
  taints:
  - key: workload
    value: training
    effect: NoSchedule
---
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: inference-on-demand
spec:
  requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: ["on-demand"]
  - key: node.kubernetes.io/instance-type
    operator: In
    values: ["c5.4xlarge", "c5.9xlarge"]
  limits:
    resources:
      cpu: 1000
  ttlSecondsAfterEmpty: 300
```

### Resource Consolidation

```yaml
# Use bin-packing to minimize node count
apiVersion: v1
kind: ConfigMap
metadata:
  name: scheduler-config
data:
  config.yaml: |
    apiVersion: kubescheduler.config.k8s.io/v1
    kind: KubeSchedulerConfiguration
    profiles:
    - schedulerName: bin-packing
      plugins:
        score:
          disabled:
          - name: NodeResourcesBalancedAllocation
          enabled:
          - name: NodeResourcesMostAllocated
            weight: 100
```

## Summary

Key takeaways:

1. **Multi-cluster architectures** provide resilience, compliance, and optimization opportunities
2. **Federation and GitOps** enable centralized management of multiple clusters
3. **Cross-cluster networking** requires careful planning for service discovery and communication
4. **Data replication** ensures consistency and availability across regions
5. **Multi-cloud strategies** prevent vendor lock-in and optimize costs
6. **Disaster recovery** requires testing and automation for effective failover
7. **Cost optimization** through workload placement and resource management

## Further Reading

- [KubeFed Documentation](https://github.com/kubernetes-sigs/kubefed)
- [Istio Multi-Cluster](https://istio.io/latest/docs/setup/install/multicluster/)
- [Submariner](https://submariner.io/)
- [ArgoCD ApplicationSets](https://argocd-applicationset.readthedocs.io/)

## Next Steps

Next lecture: **Autoscaling Strategies** - Learn how to implement HPA, VPA, and cluster autoscaling for ML workloads.
