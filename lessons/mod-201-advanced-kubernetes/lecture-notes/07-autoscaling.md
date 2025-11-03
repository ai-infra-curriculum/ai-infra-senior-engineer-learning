# Lecture 07: Autoscaling Strategies

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement Horizontal Pod Autoscaler (HPA) configurations for ML inference services with custom metrics
- Configure Vertical Pod Autoscaler (VPA) for optimal resource allocation in training and serving workloads
- Implement Cluster Autoscaler for dynamic node scaling based on workload demands
- Design custom metrics autoscaling using Prometheus, application metrics, and business KPIs
- Implement event-driven autoscaling (KEDA) for queue-based ML processing pipelines
- Configure cost-aware autoscaling strategies using spot instances and intelligent workload placement
- Design autoscaling policies specific to ML workloads including GPU-based scaling and batch job optimization
- Troubleshoot autoscaling issues including flapping, slow scale-up, and resource quota limits

## Table of Contents
1. [Introduction to Autoscaling](#introduction)
2. [Horizontal Pod Autoscaler (HPA)](#hpa)
3. [Vertical Pod Autoscaler (VPA)](#vpa)
4. [Cluster Autoscaler](#cluster-autoscaler)
5. [Custom Metrics Autoscaling](#custom-metrics)
6. [Event-Driven Autoscaling (KEDA)](#keda)
7. [Autoscaling ML Workloads](#ml-autoscaling)
8. [Cost-Aware Autoscaling](#cost-aware)

## Introduction to Autoscaling {#introduction}

### Why Autoscaling for ML?

ML workloads have unique scaling characteristics:

- **Inference:** Variable request rates (spikes, valleys)
- **Training:** Batch jobs with defined start/end
- **Data Processing:** Bursty workload patterns
- **Cost:** GPUs are expensive; minimize idle time
- **Performance:** Meet SLAs without over-provisioning

### Types of Autoscaling

```
┌─────────────────────────────────────────────────┐
│  Horizontal Pod Autoscaler (HPA)                │
│  Scale pod replicas based on metrics            │
│  ┌────┐ ┌────┐ ┌────┐    →   ┌────┐ ┌────┐     │
│  │Pod │ │Pod │ │Pod │         │Pod │ │Pod │     │
│  └────┘ └────┘ └────┘         └────┘ └────┘     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Vertical Pod Autoscaler (VPA)                  │
│  Adjust pod resource requests/limits            │
│  ┌──────────┐         ┌──────────┐             │
│  │ 1 CPU    │    →    │ 4 CPU    │             │
│  │ 2GB RAM  │         │ 8GB RAM  │             │
│  └──────────┘         └──────────┘             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Cluster Autoscaler (CA)                        │
│  Add/remove nodes based on pending pods         │
│  ┌──────┐ ┌──────┐     →   ┌──────┐ ┌──────┐  │
│  │Node 1│ │Node 2│          │Node 1│ │Node 2│  │
│  └──────┘ └──────┘          └──────┘ └──────┘  │
│                             ┌──────┐            │
│                             │Node 3│            │
│                             └──────┘            │
└─────────────────────────────────────────────────┘
```

## Horizontal Pod Autoscaler (HPA) {#hpa}

### Basic CPU-Based HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min cooldown
      policies:
      - type: Percent
        value: 50  # Scale down max 50% of pods
        periodSeconds: 60
      - type: Pods
        value: 5   # Scale down max 5 pods
        periodSeconds: 60
      selectPolicy: Min  # Use most conservative policy
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Double pods if needed
        periodSeconds: 30
      - type: Pods
        value: 10   # Add max 10 pods at once
        periodSeconds: 30
      selectPolicy: Max  # Use most aggressive policy
```

### Memory-Based HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-memory-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Multi-Metric HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-multi-metric
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 5
  maxReplicas: 100
  metrics:
  # CPU target
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Memory target
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # Custom metric: requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  # External metric: SQS queue depth
  - type: External
    external:
      metric:
        name: sqs_queue_depth
        selector:
          matchLabels:
            queue_name: inference_queue
      target:
        type: AverageValue
        averageValue: "30"
```

### HPA Best Practices

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: production-hpa-best-practices
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 10  # Always run minimum for availability
  maxReplicas: 200
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # 30% headroom for spikes
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10  # Conservative scale-down (10% per minute)
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 50  # Aggressive scale-up
        periodSeconds: 15
      - type: Pods
        value: 20
        periodSeconds: 15
      selectPolicy: Max
```

## Vertical Pod Autoscaler (VPA) {#vpa}

### Installing VPA

```bash
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

### Basic VPA

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: training-job-vpa
  namespace: ml-team
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: training-job
  updatePolicy:
    updateMode: "Auto"  # Auto, Recreate, Initial, Off
  resourcePolicy:
    containerPolicies:
    - containerName: training
      minAllowed:
        cpu: 1
        memory: 2Gi
      maxAllowed:
        cpu: 16
        memory: 64Gi
      controlledResources:
      - cpu
      - memory
```

### VPA Update Modes

**Auto:** VPA updates running pods
```yaml
updatePolicy:
  updateMode: "Auto"
```

**Recreate:** VPA evicts pods for recreation
```yaml
updatePolicy:
  updateMode: "Recreate"
```

**Initial:** VPA only sets requests on pod creation
```yaml
updatePolicy:
  updateMode: "Initial"
```

**Off:** VPA only provides recommendations
```yaml
updatePolicy:
  updateMode: "Off"
```

### VPA Recommendations

```bash
kubectl describe vpa training-job-vpa
```

```yaml
Status:
  Recommendation:
    Container Recommendations:
    - Container Name:  training
      Lower Bound:
        Cpu:     2
        Memory:  4Gi
      Target:
        Cpu:     4
        Memory:  8Gi
      Uncapped Target:
        Cpu:     8
        Memory:  16Gi
      Upper Bound:
        Cpu:     16
        Memory:  32Gi
```

### VPA + HPA (Careful!)

VPA and HPA can conflict. If using both:

```yaml
# Use VPA for memory, HPA for replicas based on custom metrics
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: model-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: server
      controlledResources:
      - memory  # VPA only manages memory
      minAllowed:
        memory: 4Gi
      maxAllowed:
        memory: 32Gi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 5
  maxReplicas: 100
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  # Don't use CPU/memory metrics with VPA
```

## Cluster Autoscaler {#cluster-autoscaler}

### AWS Cluster Autoscaler

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/ml-cluster
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-utilization-threshold=0.5
        env:
        - name: AWS_REGION
          value: us-west-2
```

### Node Group Priority

```yaml
# Priority expander config
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-priority-expander
  namespace: kube-system
data:
  priorities: |
    10:
      - .*-spot-.*  # Prefer spot instances
    50:
      - .*-on-demand-gpu-.*  # GPU on-demand second priority
    90:
      - .*-on-demand-cpu-.*  # CPU on-demand last resort
```

### Pod Priority and Preemption with CA

```yaml
# Low priority pods can be preempted to make room
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-low-priority
value: 1000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
---
apiVersion: v1
kind: Pod
metadata:
  name: batch-job
spec:
  priorityClassName: batch-low-priority
  containers:
  - name: worker
    image: batch-processor:v1
    resources:
      requests:
        cpu: 4
        memory: 16Gi
```

### Cluster Autoscaler Annotations

```yaml
# Prevent scale-down of specific nodes
apiVersion: v1
kind: Node
metadata:
  name: critical-node-1
  annotations:
    cluster-autoscaler.kubernetes.io/scale-down-disabled: "true"
---
# Pod annotation to prevent node scale-down
apiVersion: v1
kind: Pod
metadata:
  name: stateful-app
  annotations:
    cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
spec:
  containers:
  - name: app
    image: myapp:v1
```

## Custom Metrics Autoscaling {#custom-metrics}

### Prometheus Adapter

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: adapter-config
  namespace: monitoring
data:
  config.yaml: |
    rules:
    # HTTP requests per second
    - seriesQuery: 'http_requests_total{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        matches: "^(.*)_total$"
        as: "${1}_per_second"
      metricsQuery: 'sum(rate(<<.Series>>{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'

    # Model inference latency (p95)
    - seriesQuery: 'inference_duration_seconds{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        as: "inference_latency_p95"
      metricsQuery: 'histogram_quantile(0.95, sum(rate(<<.Series>>_bucket{<<.LabelMatchers>>}[5m])) by (le, <<.GroupBy>>))'

    # Queue depth
    - seriesQuery: 'inference_queue_depth{namespace!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
      name:
        as: "inference_queue_depth"
      metricsQuery: 'avg(<<.Series>>{<<.LabelMatchers>>}) by (<<.GroupBy>>)'

    # GPU utilization
    - seriesQuery: 'DCGM_FI_DEV_GPU_UTIL{pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        as: "gpu_utilization"
      metricsQuery: 'avg(<<.Series>>{<<.LabelMatchers>>}) by (<<.GroupBy>>)'
```

### HPA with Custom Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-custom-metrics
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-inference
  minReplicas: 5
  maxReplicas: 100
  metrics:
  # Custom metric: HTTP requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  # Custom metric: P95 latency (scale up if > 100ms)
  - type: Pods
    pods:
      metric:
        name: inference_latency_p95
      target:
        type: AverageValue
        averageValue: "0.1"  # 100ms in seconds
  # Custom metric: Queue depth
  - type: Object
    object:
      metric:
        name: inference_queue_depth
      describedObject:
        apiVersion: v1
        kind: Service
        name: inference-service
      target:
        type: AverageValue
        averageValue: "50"
```

## Event-Driven Autoscaling (KEDA) {#keda}

### Installing KEDA

```bash
kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.11.0/keda-2.11.0.yaml
```

### KEDA with SQS

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-queue-scaler
  namespace: ml-production
spec:
  scaleTargetRef:
    name: batch-inference
  minReplicaCount: 0  # Scale to zero when idle
  maxReplicaCount: 100
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-west-2.amazonaws.com/123456789/inference-queue
      queueLength: "30"  # Target 30 messages per pod
      awsRegion: "us-west-2"
      identityOwner: "operator"  # Use IRSA
```

### KEDA with Kafka

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-processor
spec:
  scaleTargetRef:
    name: stream-processor
  minReplicaCount: 1
  maxReplicaCount: 50
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka-broker:9092
      consumerGroup: ml-processors
      topic: training-data
      lagThreshold: "1000"  # Scale up if lag > 1000
```

### KEDA with Prometheus

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: prometheus-scaler
spec:
  scaleTargetRef:
    name: model-server
  minReplicaCount: 3
  maxReplicaCount: 100
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: http_requests_per_second
      threshold: "1000"
      query: sum(rate(http_requests_total{job="model-server"}[2m]))
```

### KEDA Scale to Zero

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: batch-processor-scale-to-zero
spec:
  scaleTargetRef:
    name: batch-processor
  minReplicaCount: 0  # Scale to zero when no work
  maxReplicaCount: 50
  pollingInterval: 30
  cooldownPeriod: 300  # Wait 5 min before scaling to zero
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-west-2.amazonaws.com/123456789/batch-jobs
      queueLength: "10"
      awsRegion: "us-west-2"
```

## Autoscaling ML Workloads {#ml-autoscaling}

### Inference Autoscaling

```yaml
# Scale based on request rate and latency
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-inference
  minReplicas: 10  # Always available
  maxReplicas: 200
  metrics:
  # Scale on request rate
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "500"
  # Also scale on latency (if p95 > 200ms)
  - type: Pods
    pods:
      metric:
        name: inference_latency_p95
      target:
        type: AverageValue
        averageValue: "0.2"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Batch Training Autoscaling

```yaml
# Use KEDA to scale batch training based on queue
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: training-queue-scaler
spec:
  scaleTargetRef:
    name: training-workers
  minReplicaCount: 0
  maxReplicaCount: 50
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-west-2.amazonaws.com/123456789/training-jobs
      queueLength: "1"  # One worker per job
      awsRegion: "us-west-2"
---
# Worker deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: training-workers
spec:
  replicas: 0  # Managed by KEDA
  selector:
    matchLabels:
      app: training-worker
  template:
    metadata:
      labels:
        app: training-worker
    spec:
      containers:
      - name: worker
        image: training-worker:v1
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: 16Gi
            cpu: 8
          limits:
            nvidia.com/gpu: 1
            memory: 16Gi
            cpu: 8
```

### GPU-Based Autoscaling

```yaml
# Scale based on GPU utilization
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gpu-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gpu-inference
  minReplicas: 3
  maxReplicas: 20
  metrics:
  # GPU utilization from DCGM exporter
  - type: Pods
    pods:
      metric:
        name: gpu_utilization
      target:
        type: AverageValue
        averageValue: "70"  # Target 70% GPU utilization
  # Also consider GPU memory
  - type: Pods
    pods:
      metric:
        name: gpu_memory_utilization
      target:
        type: AverageValue
        averageValue: "80"
```

## Cost-Aware Autoscaling {#cost-aware}

### Spot Instance Autoscaling

```yaml
# Prefer spot instances, fall back to on-demand
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: cost-optimized
spec:
  requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: ["spot", "on-demand"]
  - key: node.kubernetes.io/instance-type
    operator: In
    values: ["c5.4xlarge", "c5.9xlarge", "c5.18xlarge"]
  limits:
    resources:
      cpu: 1000
  weight: 100  # High priority for spot
  ttlSecondsAfterEmpty: 30
  ttlSecondsUntilExpired: 604800  # 7 days
---
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: on-demand-fallback
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
      cpu: 100
  weight: 10  # Low priority, only if spot unavailable
```

### Time-Based Scaling

```yaml
# Scale down non-production during off-hours
apiVersion: v1
kind: CronJob
metadata:
  name: scale-down-dev
spec:
  schedule: "0 19 * * 1-5"  # 7 PM weekdays
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl scale deployment --all --replicas=0 -n development
              kubectl scale deployment --all --replicas=0 -n staging
          restartPolicy: OnFailure
---
apiVersion: v1
kind: CronJob
metadata:
  name: scale-up-dev
spec:
  schedule: "0 8 * * 1-5"  # 8 AM weekdays
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scaler
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl scale deployment --all --replicas=3 -n development
              kubectl scale deployment --all --replicas=2 -n staging
          restartPolicy: OnFailure
```

### Cost Monitoring

```yaml
# Prometheus alerts for cost anomalies
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-alerts
data:
  alerts.yaml: |
    groups:
    - name: cost
      rules:
      - alert: HighGPUCost
        expr: sum(rate(container_gpu_usage_seconds_total[1h])) * 12.24 > 1000
        for: 1h
        annotations:
          summary: "GPU cost exceeds $1000/hour"
          description: "Current GPU usage would cost {{ $value | humanize }} per hour"

      - alert: IdleGPUs
        expr: avg(DCGM_FI_DEV_GPU_UTIL) < 20
        for: 30m
        annotations:
          summary: "GPUs underutilized"
          description: "Average GPU utilization is {{ $value }}%"
```

## Summary

Key takeaways:

1. **HPA scales horizontally** based on CPU, memory, or custom metrics
2. **VPA adjusts resource requests** vertically for better efficiency
3. **Cluster Autoscaler** adds/removes nodes based on demand
4. **Custom metrics** enable ML-specific autoscaling (latency, queue depth)
5. **KEDA** provides event-driven scaling including scale-to-zero
6. **ML workloads** require tailored autoscaling strategies
7. **Cost optimization** through spot instances and time-based scaling

## Further Reading

- [HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [VPA GitHub](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [KEDA Documentation](https://keda.sh/docs/)

## Next Steps

Next lecture: **Production Kubernetes for ML** - Learn how to operate production-grade Kubernetes clusters for ML workloads.
