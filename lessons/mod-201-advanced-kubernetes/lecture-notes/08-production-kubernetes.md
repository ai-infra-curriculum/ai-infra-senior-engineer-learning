# Lecture 08: Production Kubernetes for ML

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement highly available Kubernetes architectures with multi-AZ control planes for ML platforms
- Develop and test disaster recovery procedures including backup, restore, and failover strategies
- Implement comprehensive monitoring and observability using Prometheus, Grafana, and distributed tracing
- Conduct performance tuning for ML workloads including etcd optimization, API server scaling, and network tuning
- Design and execute incident response procedures specific to ML platform failures
- Perform capacity planning for growing ML workloads including GPU resource forecasting
- Conduct production readiness reviews using industry-standard checklists and best practices
- Evaluate and implement SLIs, SLOs, and error budgets for ML infrastructure services

## Table of Contents
1. [Production Readiness](#production-readiness)
2. [High Availability Design](#ha-design)
3. [Disaster Recovery](#disaster-recovery)
4. [Monitoring and Observability](#monitoring)
5. [Performance Tuning](#performance)
6. [Incident Response](#incident-response)
7. [Capacity Planning](#capacity-planning)
8. [Production Checklist](#checklist)

## Production Readiness {#production-readiness}

### What Makes a Cluster Production-Ready?

**Critical Requirements:**
- High availability (no single points of failure)
- Automated backup and restore
- Comprehensive monitoring and alerting
- Security hardening
- Disaster recovery plan (tested regularly)
- Capacity planning and autoscaling
- Incident response procedures
- Documentation and runbooks

### Production vs Non-Production

| Aspect | Non-Production | Production |
|--------|---------------|------------|
| HA Control Plane | Single master | 3+ masters across AZs |
| etcd | Single instance | 3-5 node cluster |
| Node count | Few nodes | Many nodes, multiple AZs |
| Monitoring | Basic | Comprehensive + alerting |
| Backups | Optional | Automated, tested |
| DR | None | Tested DR procedures |
| Security | Relaxed | Hardened, audited |
| Cost | Optimize | Balance with reliability |

## High Availability Design {#ha-design}

### Control Plane HA

**AWS EKS Example:**

```bash
eksctl create cluster \
  --name ml-production \
  --region us-west-2 \
  --zones us-west-2a,us-west-2b,us-west-2c \
  --version 1.27 \
  --with-oidc \
  --managed \
  --nodegroup-name cpu-workers \
  --nodes 6 \
  --nodes-min 6 \
  --nodes-max 50 \
  --node-type c5.4xlarge \
  --node-zones us-west-2a,us-west-2b,us-west-2c
```

**Self-Managed Example:**

```yaml
# 3 control plane nodes across availability zones
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.27.0
controlPlaneEndpoint: "lb.example.com:6443"  # Load balancer
etcd:
  external:
    endpoints:
    - https://etcd-1.example.com:2379
    - https://etcd-2.example.com:2379
    - https://etcd-3.example.com:2379
    caFile: /etc/kubernetes/pki/etcd/ca.crt
    certFile: /etc/kubernetes/pki/apiserver-etcd-client.crt
    keyFile: /etc/kubernetes/pki/apiserver-etcd-client.key
networking:
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12
apiServer:
  extraArgs:
    cloud-provider: "external"
    audit-log-path: "/var/log/kubernetes/audit.log"
    audit-log-maxage: "30"
    audit-log-maxbackup: "10"
    audit-log-maxsize: "100"
controllerManager:
  extraArgs:
    cloud-provider: "external"
    node-monitor-period: "5s"
    node-monitor-grace-period: "40s"
    pod-eviction-timeout: "30s"
```

### Worker Node HA

```yaml
# Spread workers across zones
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 30
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      # Spread across zones
      topologySpreadConstraints:
      - maxSkew: 2
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: model-server
      # Spread across nodes
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: model-server
      # Anti-affinity to avoid single node
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: model-server
              topologyKey: kubernetes.io/hostname
      containers:
      - name: server
        image: model-server:v1
        resources:
          requests:
            cpu: "4"
            memory: 8Gi
          limits:
            cpu: "4"
            memory: 8Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/sh
              - -c
              - sleep 15  # Allow time for load balancer to remove
```

### Pod Disruption Budgets

```yaml
# Ensure minimum availability during disruptions
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: model-server-pdb
spec:
  minAvailable: 20  # Always keep 20 pods running
  selector:
    matchLabels:
      app: model-server
---
# Alternative: maxUnavailable
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: training-coordinator-pdb
spec:
  maxUnavailable: 1  # Only one can be down at a time
  selector:
    matchLabels:
      app: training-coordinator
```

### Service Mesh for Resilience

```yaml
# Istio DestinationRule with circuit breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: model-server-resilience
spec:
  host: model-server
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
    loadBalancer:
      simple: LEAST_REQUEST
```

## Disaster Recovery {#disaster-recovery}

### Backup Strategy

**etcd Backup:**

```bash
#!/bin/bash
# Automated etcd backup script

ETCDCTL_API=3
BACKUP_DIR="/backups/etcd"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Backup etcd
etcdctl snapshot save "${BACKUP_DIR}/snapshot-${TIMESTAMP}.db" \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
etcdctl snapshot status "${BACKUP_DIR}/snapshot-${TIMESTAMP}.db"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/snapshot-${TIMESTAMP}.db" \
  s3://ml-cluster-backups/etcd/

# Keep last 30 days locally
find "${BACKUP_DIR}" -name "snapshot-*.db" -mtime +30 -delete

echo "Backup completed: snapshot-${TIMESTAMP}.db"
```

**Velero Backup Schedule:**

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: production-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  template:
    includedNamespaces:
    - ml-production
    - ml-staging
    excludedResources:
    - events
    - events.events.k8s.io
    snapshotVolumes: true
    ttl: 720h  # 30 days
    storageLocation: default
    volumeSnapshotLocations:
    - aws-us-west-2
    hooks:
      resources:
      - name: postgres-backup
        includedNamespaces:
        - ml-production
        labelSelector:
          matchLabels:
            app: postgres
        pre:
        - exec:
            container: postgres
            command:
            - /bin/bash
            - -c
            - PGPASSWORD=$POSTGRES_PASSWORD pg_dump -U postgres -d mldb > /tmp/backup.sql
        post:
        - exec:
            container: postgres
            command:
            - /bin/bash
            - -c
            - rm /tmp/backup.sql
```

### Disaster Recovery Procedures

**Full Cluster Recovery:**

```markdown
## DR Procedure: Full Cluster Loss

### Prerequisites
- Access to backup storage (S3)
- Access to cloud provider (AWS)
- Velero CLI installed
- kubectl configured

### Steps

1. **Provision New Cluster**
   ```bash
   eksctl create cluster -f cluster-config.yaml
   ```

2. **Install Velero**
   ```bash
   velero install \
     --provider aws \
     --plugins velero/velero-plugin-for-aws:v1.7.0 \
     --bucket ml-cluster-backups \
     --backup-location-config region=us-west-2 \
     --secret-file ./credentials-velero
   ```

3. **Restore from Latest Backup**
   ```bash
   # List available backups
   velero backup get

   # Restore
   velero restore create --from-backup production-backup-20240115 \
     --wait

   # Monitor restore
   velero restore describe production-backup-20240115-restore
   velero restore logs production-backup-20240115-restore
   ```

4. **Verify Services**
   ```bash
   kubectl get pods --all-namespaces
   kubectl get pvc --all-namespaces
   kubectl get svc --all-namespaces
   ```

5. **Restore DNS and Load Balancers**
   ```bash
   # External-DNS will recreate DNS records
   # Check that LoadBalancer services get external IPs
   kubectl get svc -o wide
   ```

6. **Validate Functionality**
   ```bash
   # Run smoke tests
   ./scripts/smoke-tests.sh

   # Check model inference
   curl https://api.ml.example.com/predict -d '{...}'
   ```

7. **Update Monitoring**
   - Update monitoring dashboards with new cluster info
   - Verify alerts are firing correctly

### RTO: 2 hours
### RPO: 24 hours (daily backups)
```

### DR Testing

```yaml
# Monthly DR drill CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dr-drill
  namespace: ops
spec:
  schedule: "0 10 1 * *"  # 10 AM on 1st of month
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: dr-drill
            image: dr-testing:v1
            env:
            - name: SLACK_WEBHOOK
              valueFrom:
                secretKeyRef:
                  name: slack-webhooks
                  key: dr-channel
            command:
            - /bin/bash
            - -c
            - |
              echo "Starting DR drill..."

              # Create test cluster
              eksctl create cluster -f dr-test-cluster.yaml

              # Restore latest backup
              velero restore create --from-backup latest \
                --namespace-mappings production:dr-test

              # Run tests
              pytest tests/dr_validation/

              # Generate report
              ./generate-dr-report.sh

              # Cleanup
              eksctl delete cluster -f dr-test-cluster.yaml

              echo "DR drill complete"
          restartPolicy: OnFailure
```

## Monitoring and Observability {#monitoring}

### Prometheus Stack

```yaml
# Prometheus for metrics
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: ml-prometheus
  namespace: monitoring
spec:
  replicas: 2
  retention: 30d
  retentionSize: 500GB
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 500Gi
  serviceMonitorSelector:
    matchLabels:
      team: ml-platform
  podMonitorSelector:
    matchLabels:
      team: ml-platform
  resources:
    requests:
      memory: 16Gi
      cpu: 4
    limits:
      memory: 32Gi
      cpu: 8
  alerting:
    alertmanagers:
    - namespace: monitoring
      name: alertmanager
      port: web
```

### Critical Alerts

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ml-platform-alerts
  namespace: monitoring
spec:
  groups:
  - name: infrastructure
    interval: 30s
    rules:
    # Node down
    - alert: NodeDown
      expr: up{job="node-exporter"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Node {{ $labels.instance }} is down"
        description: "Node has been down for more than 5 minutes"

    # High node CPU
    - alert: HighNodeCPU
      expr: (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)) * 100 > 90
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage on {{ $labels.instance }}"
        description: "CPU usage is {{ $value }}%"

    # High node memory
    - alert: HighNodeMemory
      expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage on {{ $labels.instance }}"

  - name: ml-workloads
    interval: 30s
    rules:
    # Model server down
    - alert: ModelServerDown
      expr: up{job="model-server"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Model server down"
        description: "No model server pods are running"

    # High inference latency
    - alert: HighInferenceLatency
      expr: histogram_quantile(0.95, rate(inference_duration_seconds_bucket[5m])) > 0.5
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: "High inference latency"
        description: "P95 latency is {{ $value }}s"

    # GPU not utilized
    - alert: GPUUnderutilized
      expr: avg(DCGM_FI_DEV_GPU_UTIL) < 20
      for: 1h
      labels:
        severity: info
      annotations:
        summary: "GPUs underutilized"
        description: "Average GPU utilization is {{ $value }}%"

    # Training job failed
    - alert: TrainingJobFailed
      expr: increase(training_jobs_failed_total[1h]) > 5
      labels:
        severity: warning
      annotations:
        summary: "Multiple training jobs failing"
        description: "{{ $value }} training jobs failed in last hour"

  - name: kubernetes
    interval: 30s
    rules:
    # Pod crash looping
    - alert: PodCrashLooping
      expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} crash looping"

    # Persistent volume full
    - alert: PersistentVolumeSpaceRunningLow
      expr: (kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes) * 100 < 10
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "PV {{ $labels.persistentvolumeclaim }} almost full"
        description: "Only {{ $value }}% space remaining"
```

### Distributed Tracing

```yaml
# Jaeger for distributed tracing
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: ml-jaeger
  namespace: monitoring
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
        index-prefix: jaeger
    esIndexCleaner:
      enabled: true
      numberOfDays: 7
      schedule: "55 23 * * *"
  ingress:
    enabled: true
    hosts:
    - jaeger.ml.example.com
```

### Log Aggregation

```yaml
# Loki for logs
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
  namespace: monitoring
data:
  loki.yaml: |
    auth_enabled: false

    server:
      http_listen_port: 3100

    ingester:
      lifecycler:
        ring:
          kvstore:
            store: inmemory
          replication_factor: 1
      chunk_idle_period: 15m
      chunk_retain_period: 30s

    schema_config:
      configs:
      - from: 2023-01-01
        store: boltdb-shipper
        object_store: s3
        schema: v11
        index:
          prefix: loki_index_
          period: 24h

    storage_config:
      boltdb_shipper:
        active_index_directory: /loki/index
        cache_location: /loki/cache
        shared_store: s3
      aws:
        s3: s3://us-west-2/ml-logs
        sse_encryption: true

    limits_config:
      retention_period: 744h  # 31 days
```

## Performance Tuning {#performance}

### API Server Tuning

```yaml
# API server configuration
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
apiServer:
  extraArgs:
    max-requests-inflight: "400"
    max-mutating-requests-inflight: "200"
    default-watch-cache-size: "500"
    watch-cache-sizes: "persistentvolumes#1000,persistentvolumeclaims#1000"
```

### etcd Tuning

```bash
# etcd configuration
ETCD_HEARTBEAT_INTERVAL=100  # ms
ETCD_ELECTION_TIMEOUT=1000   # ms
ETCD_SNAPSHOT_COUNT=10000
ETCD_QUOTA_BACKEND_BYTES=$((8*1024*1024*1024))  # 8GB
```

### Node Configuration

```yaml
# Kubelet configuration
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
maxPods: 110
podsPerCore: 10
kubeReserved:
  cpu: "1"
  memory: "2Gi"
  ephemeral-storage: "10Gi"
systemReserved:
  cpu: "1"
  memory: "2Gi"
  ephemeral-storage: "10Gi"
evictionHard:
  memory.available: "500Mi"
  nodefs.available: "10%"
  imagefs.available: "10%"
evictionSoft:
  memory.available: "1Gi"
  nodefs.available: "15%"
  imagefs.available: "15%"
evictionSoftGracePeriod:
  memory.available: "1m30s"
  nodefs.available: "2m"
  imagefs.available: "2m"
imageGCHighThresholdPercent: 85
imageGCLowThresholdPercent: 80
```

## Incident Response {#incident-response}

### Runbooks

**Example: Model Server Outage**

```markdown
## Runbook: Model Server Outage

### Symptoms
- 5xx errors from model-server
- No healthy pods
- Alerts: ModelServerDown

### Investigation Steps

1. **Check pod status**
   ```bash
   kubectl get pods -n production -l app=model-server
   kubectl describe pod -n production -l app=model-server
   ```

2. **Check logs**
   ```bash
   kubectl logs -n production -l app=model-server --tail=100
   ```

3. **Check recent changes**
   ```bash
   kubectl rollout history deployment/model-server -n production
   git log --since="1 hour ago" --oneline
   ```

4. **Check resource usage**
   ```bash
   kubectl top pods -n production -l app=model-server
   kubectl top nodes
   ```

5. **Check dependencies**
   ```bash
   # Feature store
   kubectl get pods -n production -l app=feature-store

   # Database
   kubectl get pods -n production -l app=postgres
   ```

### Remediation

**If recent deployment:**
```bash
kubectl rollout undo deployment/model-server -n production
```

**If resource exhaustion:**
```bash
# Scale up
kubectl scale deployment/model-server -n production --replicas=50

# Add nodes if needed
kubectl get nodes
```

**If external dependency:**
```bash
# Check and fix dependency
# Then restart model-server
kubectl rollout restart deployment/model-server -n production
```

### Communication
- Update status page
- Notify #incidents channel
- Page on-call if critical

### Post-Incident
- File incident report
- Schedule post-mortem
- Create follow-up tasks
```

## Capacity Planning {#capacity-planning}

### Capacity Monitoring

```python
# Capacity planning script
import pandas as pd
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1API()

def get_cluster_capacity():
    nodes = v1.list_node()
    total_cpu = 0
    total_memory = 0
    total_gpu = 0

    for node in nodes.items:
        allocatable = node.status.allocatable
        total_cpu += int(allocatable['cpu'])
        total_memory += int(allocatable['memory'].rstrip('Ki')) / 1024 / 1024  # GB
        if 'nvidia.com/gpu' in allocatable:
            total_gpu += int(allocatable['nvidia.com/gpu'])

    return {
        'cpu': total_cpu,
        'memory_gb': total_memory,
        'gpu': total_gpu
    }

def get_cluster_usage():
    # TODO: Query Prometheus for actual usage
    # Return current usage as percentage of capacity
    pass

def predict_capacity_needs(days_ahead=30):
    # TODO: Use historical data to predict future needs
    # Return predicted resource requirements
    pass

capacity = get_cluster_capacity()
print(f"Total capacity: {capacity}")
```

## Production Checklist {#checklist}

```markdown
## Production Readiness Checklist

### Infrastructure
- [ ] Multi-AZ control plane (3+ masters)
- [ ] Multi-AZ worker nodes
- [ ] Separate node pools (inference, training, system)
- [ ] Auto-scaling configured (HPA, VPA, CA)
- [ ] PodDisruptionBudgets for critical services
- [ ] Resource quotas per namespace
- [ ] LimitRanges configured

### Security
- [ ] RBAC configured (least privilege)
- [ ] Pod Security Standards enforced
- [ ] Network Policies in place
- [ ] Secrets encrypted at rest
- [ ] External secret management (Vault/AWS Secrets Manager)
- [ ] Image scanning enabled
- [ ] Audit logging enabled
- [ ] mTLS between services (service mesh)

### Monitoring
- [ ] Prometheus + Grafana deployed
- [ ] Critical alerts configured
- [ ] PagerDuty/Opsgenie integration
- [ ] Distributed tracing (Jaeger)
- [ ] Log aggregation (Loki/ELK)
- [ ] Dashboards for key metrics
- [ ] SLO/SLI defined and tracked

### Backup & DR
- [ ] etcd automated backups
- [ ] Velero backups configured
- [ ] Backup verification automated
- [ ] DR procedures documented
- [ ] DR drills scheduled
- [ ] RTO/RPO defined and met

### Performance
- [ ] API server tuned
- [ ] etcd tuned
- [ ] Node resources optimized
- [ ] Network CNI selected appropriately
- [ ] Storage classes configured
- [ ] Load testing completed

### Operations
- [ ] Runbooks for common incidents
- [ ] On-call rotation defined
- [ ] Incident response procedures
- [ ] Change management process
- [ ] Capacity planning process
- [ ] Cost tracking and optimization

### Documentation
- [ ] Architecture diagrams
- [ ] Network diagrams
- [ ] Security policies
- [ ] Deployment procedures
- [ ] Troubleshooting guides
- [ ] Contact information

### Testing
- [ ] Integration tests
- [ ] Load tests
- [ ] Chaos engineering tests
- [ ] DR tests
- [ ] Security scans
```

## Summary

Key takeaways:

1. **Production readiness** requires comprehensive planning across multiple dimensions
2. **High availability** through multi-AZ deployments and proper pod distribution
3. **Disaster recovery** needs automated backups and tested recovery procedures
4. **Monitoring and observability** are critical for maintaining production systems
5. **Performance tuning** at all layers (API server, etcd, nodes, applications)
6. **Incident response** requires documentation, automation, and practice
7. **Capacity planning** prevents resource exhaustion and cost overruns
8. **Checklists** ensure nothing is missed in production deployments

## Further Reading

- [Kubernetes Production Best Practices](https://learnk8s.io/production-best-practices)
- [SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Kubernetes Failure Stories](https://k8s.af/)
- [Velero Documentation](https://velero.io/docs/)

## Conclusion

Congratulations on completing Module 201: Advanced Kubernetes and Cloud-Native Architecture! You now have the knowledge to design, build, and operate production-grade Kubernetes infrastructure for ML workloads.

**Next Steps:**
- Complete the hands-on labs
- Apply concepts to your organization's ML platform
- Move on to Module 202: Distributed ML Training at Scale
