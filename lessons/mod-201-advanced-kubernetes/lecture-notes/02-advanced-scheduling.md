# Lecture 02: Advanced Scheduling and Resource Management

## Learning Objectives

By the end of this lecture, you will be able to:

- Configure and optimize GPU scheduling for ML workloads using device plugins and resource quotas
- Design node affinity and anti-affinity rules to optimize training performance and high availability
- Implement taints, tolerations, and priority classes to manage heterogeneous compute clusters
- Configure resource quotas and limit ranges to prevent resource contention and ensure fair allocation
- Implement gang scheduling patterns for distributed training jobs requiring coordinated pod placement
- Design custom scheduling strategies for cost optimization using spot instances and node pools
- Troubleshoot common scheduling issues including resource fragmentation and pod pending states
- Evaluate trade-offs between different scheduling approaches for multi-tenant ML platforms

## Table of Contents
1. [Introduction to Kubernetes Scheduling](#introduction)
2. [GPU Scheduling](#gpu-scheduling)
3. [Node Affinity and Anti-Affinity](#affinity)
4. [Taints and Tolerations](#taints-tolerations)
5. [Priority Classes and Preemption](#priority-preemption)
6. [Resource Quotas and Limit Ranges](#quotas)
7. [Gang Scheduling](#gang-scheduling)
8. [Real-World Patterns](#real-world)

## Introduction to Kubernetes Scheduling {#introduction}

### The Scheduler's Role

The Kubernetes scheduler is responsible for placing pods onto nodes. For ML workloads, efficient scheduling is critical because:

- Training jobs require expensive GPU resources
- Large models need specific memory configurations
- Distributed training requires coordinated placement
- Cost optimization demands efficient resource utilization

### Default Scheduling Process

```
1. Filtering: Remove nodes that don't meet requirements
   - Resource requirements (CPU, memory, GPU)
   - Node selectors
   - Affinity/anti-affinity rules
   - Taints and tolerations

2. Scoring: Rank remaining nodes
   - Resource availability
   - Spreading for HA
   - Custom scoring plugins

3. Binding: Assign pod to highest-scoring node
```

### When Default Scheduling Isn't Enough

For ML workloads, you often need:
- **Specialized hardware:** GPUs with specific capabilities
- **Data locality:** Place pods near data storage
- **Cost optimization:** Use spot instances when appropriate
- **Gang scheduling:** Start all workers together or none at all
- **Resource guarantees:** Prevent resource fragmentation

## GPU Scheduling {#gpu-scheduling}

### GPU Resource Management

Kubernetes treats GPUs as extended resources. The device plugin framework exposes hardware to the kubelet.

**Installing NVIDIA Device Plugin:**

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-device-plugin-daemonset
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: nvidia-device-plugin-ds
  template:
    metadata:
      labels:
        name: nvidia-device-plugin-ds
    spec:
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      priorityClassName: system-node-critical
      containers:
      - image: nvcr.io/nvidia/k8s-device-plugin:v0.13.0
        name: nvidia-device-plugin-ctr
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
        volumeMounts:
        - name: device-plugin
          mountPath: /var/lib/kubelet/device-plugins
      volumes:
      - name: device-plugin
        hostPath:
          path: /var/lib/kubelet/device-plugins
```

### Requesting GPUs

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    resources:
      limits:
        nvidia.com/gpu: 2  # Request 2 GPUs
        memory: 16Gi
        cpu: 8
      requests:
        nvidia.com/gpu: 2
        memory: 16Gi
        cpu: 8
```

**Key Points:**
- GPUs are only specified in limits (not requests)
- GPU request = GPU limit (no overcommitment)
- Each GPU is exclusive to one container
- Fractional GPUs require additional tooling

### GPU Sharing Strategies

**1. Time-Slicing (NVIDIA MIG for A100)**

Multi-Instance GPU allows partitioning A100 GPUs:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: device-plugin-config
  namespace: kube-system
data:
  config.yaml: |
    version: v1
    sharing:
      timeSlicing:
        resources:
        - name: nvidia.com/gpu
          replicas: 4  # Each physical GPU appears as 4
```

**2. MPS (Multi-Process Service)**

For CUDA applications that cooperate:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mps-pod
spec:
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    env:
    - name: CUDA_MPS_PIPE_DIRECTORY
      value: /tmp/nvidia-mps
    - name: CUDA_MPS_LOG_DIRECTORY
      value: /var/log/nvidia-mps
    resources:
      limits:
        nvidia.com/gpu: 1
```

**3. vGPU (Virtual GPU)**

Enterprise feature for shared GPUs with guaranteed resources.

### GPU Node Labeling

Label nodes with GPU capabilities:

```bash
# Label nodes with GPU type
kubectl label node gpu-node-1 gpu-type=a100
kubectl label node gpu-node-2 gpu-type=v100
kubectl label node gpu-node-3 gpu-type=t4

# Label with GPU memory
kubectl label node gpu-node-1 gpu-memory=40gb
kubectl label node gpu-node-2 gpu-memory=16gb

# Label with GPU count
kubectl label node gpu-node-1 gpu-count=8
```

Use node selectors to target specific GPUs:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-a100
spec:
  nodeSelector:
    gpu-type: a100
    gpu-memory: 40gb
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    resources:
      limits:
        nvidia.com/gpu: 4
```

### GPU Monitoring

Deploy NVIDIA DCGM exporter for metrics:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: dcgm-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: dcgm-exporter
  template:
    metadata:
      labels:
        app: dcgm-exporter
    spec:
      containers:
      - name: dcgm-exporter
        image: nvcr.io/nvidia/k8s/dcgm-exporter:3.1.3-3.1.4-ubuntu20.04
        ports:
        - name: metrics
          containerPort: 9400
        env:
        - name: DCGM_EXPORTER_LISTEN
          value: ":9400"
        securityContext:
          runAsNonRoot: false
          runAsUser: 0
          capabilities:
            add: ["SYS_ADMIN"]
      nodeSelector:
        nvidia.com/gpu: "true"
```

**Key GPU Metrics:**
- GPU utilization percentage
- GPU memory usage
- GPU temperature
- Power consumption
- SM (Streaming Multiprocessor) occupancy

## Node Affinity and Anti-Affinity {#affinity}

### Node Affinity

Node affinity is like an advanced node selector with more expressive rules.

**Required vs Preferred:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
spec:
  affinity:
    nodeAffinity:
      # Hard requirement - pod won't schedule without this
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: gpu-type
            operator: In
            values:
            - a100
            - v100
          - key: region
            operator: In
            values:
            - us-west-2

      # Soft preference - scheduler tries but not required
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: instance-type
            operator: In
            values:
            - spot  # Prefer spot instances for cost
      - weight: 50
        preference:
          matchExpressions:
          - key: disk-type
            operator: In
            values:
            - nvme  # Prefer NVMe storage

  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
```

**Operators:**
- `In`: Value in list
- `NotIn`: Value not in list
- `Exists`: Key exists (value doesn't matter)
- `DoesNotExist`: Key doesn't exist
- `Gt`: Greater than (for numeric values)
- `Lt`: Less than (for numeric values)

### Pod Affinity

Place pods near other pods (e.g., training workers near parameter servers):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-worker
  labels:
    app: training
    role: worker
spec:
  affinity:
    podAffinity:
      # Schedule near parameter servers
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - training
          - key: role
            operator: In
            values:
            - ps  # parameter server
        topologyKey: kubernetes.io/hostname  # Same node

    podAntiAffinity:
      # Don't schedule multiple workers on same node
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - training
            - key: role
              operator: In
              values:
              - worker
          topologyKey: kubernetes.io/hostname

  containers:
  - name: worker
    image: tensorflow/tensorflow:latest-gpu
```

### Topology Spread Constraints

More sophisticated spreading than pod anti-affinity:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
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
      topologySpreadConstraints:
      # Spread across availability zones
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: model-server

      # Spread across nodes
      - maxSkew: 2
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: model-server

      containers:
      - name: server
        image: model-server:v1
```

**Parameters:**
- `maxSkew`: Maximum difference in pod count between any two topology domains
- `topologyKey`: Node label key defining domains (e.g., zone, hostname)
- `whenUnsatisfiable`: `DoNotSchedule` (hard) or `ScheduleAnyway` (soft)

## Taints and Tolerations {#taints-tolerations}

### Understanding Taints

Taints repel pods from nodes. Use cases:
- Dedicated GPU nodes for training only
- Separating production and development workloads
- Isolating nodes with special hardware
- Draining nodes for maintenance

**Taint Effects:**
- `NoSchedule`: New pods won't be scheduled (existing pods unaffected)
- `PreferNoSchedule`: Scheduler tries to avoid (soft version)
- `NoExecute`: New pods won't schedule, existing pods are evicted

### Applying Taints

```bash
# Taint GPU nodes to dedicate for training
kubectl taint nodes gpu-node-1 workload=training:NoSchedule

# Taint spot instances to mark them as preemptible
kubectl taint nodes spot-node-1 instance-type=spot:NoSchedule

# Taint node being drained
kubectl taint nodes node-1 maintenance=true:NoExecute

# Remove taint (note the trailing minus)
kubectl taint nodes gpu-node-1 workload=training:NoSchedule-
```

### Tolerations

Pods specify tolerations to schedule on tainted nodes:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
spec:
  tolerations:
  # Tolerate training workload taint
  - key: "workload"
    operator: "Equal"
    value: "training"
    effect: "NoSchedule"

  # Tolerate spot instances
  - key: "instance-type"
    operator: "Equal"
    value: "spot"
    effect: "NoSchedule"

  # Tolerate any value for maintenance
  - key: "maintenance"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 300  # Evict after 5 minutes

  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
```

**Toleration Operators:**
- `Equal`: Key and value must match
- `Exists`: Only key needs to exist (value ignored)

### Common Taint Patterns for ML

**Pattern 1: Dedicated GPU Pool**

```bash
# Taint all GPU nodes
kubectl taint nodes -l gpu=true dedicated=gpu:NoSchedule

# Training pods tolerate this
```

```yaml
tolerations:
- key: "dedicated"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"
```

**Pattern 2: Development vs Production**

```bash
kubectl taint nodes -l environment=production workload=production:NoSchedule
```

```yaml
# Production inference pods
tolerations:
- key: "workload"
  operator: "Equal"
  value: "production"
  effect: "NoSchedule"
```

**Pattern 3: Spot Instance Handling**

```bash
kubectl taint nodes -l instance-lifecycle=spot instance-type=spot:NoSchedule
```

```yaml
# Fault-tolerant training job
tolerations:
- key: "instance-type"
  operator: "Equal"
  value: "spot"
  effect: "NoSchedule"
```

## Priority Classes and Preemption {#priority-preemption}

### Priority Classes

Priority classes assign numeric priorities to pods. Higher priority pods can preempt (evict) lower priority pods.

**Creating Priority Classes:**

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-inference
value: 1000000  # High priority
globalDefault: false
description: "Critical inference workloads that serve production traffic"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: training-high
value: 100000
globalDefault: false
description: "High priority training jobs (e.g., urgent model updates)"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: training-normal
value: 10000
globalDefault: true  # Default for pods without priorityClassName
description: "Normal priority training jobs"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: training-low
value: 1000
globalDefault: false
description: "Low priority training jobs (e.g., experiments, research)"
preemptionPolicy: Never  # This class won't preempt others
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-jobs
value: 100
globalDefault: false
description: "Batch processing and data pipelines"
```

### Using Priority Classes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: production-inference
spec:
  priorityClassName: critical-inference
  containers:
  - name: inference
    image: model-server:v1
    resources:
      requests:
        nvidia.com/gpu: 1
        memory: 8Gi
        cpu: 4
      limits:
        nvidia.com/gpu: 1
        memory: 8Gi
        cpu: 4
---
apiVersion: v1
kind: Pod
metadata:
  name: experimental-training
spec:
  priorityClassName: training-low
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    resources:
      requests:
        nvidia.com/gpu: 2
        memory: 16Gi
      limits:
        nvidia.com/gpu: 2
        memory: 16Gi
```

### Preemption Behavior

When a high-priority pod can't be scheduled:

1. Scheduler identifies nodes where preemption would help
2. Selects node with lowest-priority victim pods
3. Evicts victim pods (graceful termination)
4. Schedules high-priority pod

**Preemption Protection:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: long-running-training
spec:
  priorityClassName: training-normal
  terminationGracePeriodSeconds: 3600  # 1 hour to checkpoint
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    lifecycle:
      preStop:
        exec:
          command:
          - /bin/sh
          - -c
          - |
            # Save checkpoint before termination
            python save_checkpoint.py
            sleep 30
```

### Priority-Based Resource Allocation

Combined with resource quotas:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: high-priority-quota
  namespace: ml-team
spec:
  hard:
    requests.nvidia.com/gpu: "20"
    requests.memory: "200Gi"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values:
      - training-high
      - critical-inference
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: low-priority-quota
  namespace: ml-team
spec:
  hard:
    requests.nvidia.com/gpu: "10"
    requests.memory: "100Gi"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values:
      - training-low
      - batch-jobs
```

## Resource Quotas and Limit Ranges {#quotas}

### Resource Quotas

Limit resource consumption per namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ml-team-quota
  namespace: ml-team
spec:
  hard:
    # Compute resources
    requests.cpu: "200"
    requests.memory: "500Gi"
    requests.nvidia.com/gpu: "32"
    limits.cpu: "400"
    limits.memory: "1000Gi"
    limits.nvidia.com/gpu: "32"

    # Object counts
    persistentvolumeclaims: "50"
    services: "20"
    pods: "100"

    # Storage
    requests.storage: "10Ti"
```

**Quota Scopes:**

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: spot-instance-quota
  namespace: ml-team
spec:
  hard:
    requests.nvidia.com/gpu: "64"
  scopes:
  - NotTerminating  # Only long-running pods
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values:
      - training-low
```

### Limit Ranges

Set default and constrain resource requests/limits:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: ml-limits
  namespace: ml-team
spec:
  limits:
  # Container level
  - type: Container
    default:  # Default limits if not specified
      memory: 8Gi
      cpu: 4
    defaultRequest:  # Default requests if not specified
      memory: 4Gi
      cpu: 2
    max:  # Maximum allowed
      memory: 128Gi
      cpu: 32
      nvidia.com/gpu: 8
    min:  # Minimum required
      memory: 1Gi
      cpu: 0.5
    maxLimitRequestRatio:  # Max limit/request ratio
      memory: 4
      cpu: 4

  # Pod level (sum of all containers)
  - type: Pod
    max:
      memory: 256Gi
      cpu: 64
      nvidia.com/gpu: 16

  # PVC level
  - type: PersistentVolumeClaim
    max:
      storage: 5Ti
    min:
      storage: 10Gi
```

### Monitoring Resource Usage

```bash
# View quota usage
kubectl describe resourcequota -n ml-team

# View all quotas across namespaces
kubectl get resourcequota --all-namespaces

# View limit ranges
kubectl describe limitrange -n ml-team
```

## Gang Scheduling {#gang-scheduling}

### The Gang Scheduling Problem

**Scenario:** Distributed training job requires 8 workers to start together:
- 7 workers get scheduled
- 8th worker can't schedule (no resources)
- 7 workers waste resources waiting forever

**Solution:** Gang scheduling ensures all-or-nothing scheduling.

### Volcano Scheduler

Volcano is a batch scheduling system for Kubernetes built for high-performance workloads.

**Installing Volcano:**

```bash
kubectl apply -f https://raw.githubusercontent.com/volcano-sh/volcano/master/installer/volcano-development.yaml
```

**Using Volcano for Gang Scheduling:**

```yaml
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: distributed-training
spec:
  minAvailable: 8  # Minimum pods that must be scheduled
  schedulerName: volcano

  plugins:
    svc: []  # Create service for pod discovery
    env: []  # Set environment variables

  policies:
  - event: PodEvicted
    action: RestartJob

  tasks:
  - name: worker
    replicas: 8
    template:
      metadata:
        labels:
          app: training
          role: worker
      spec:
        containers:
        - name: training
          image: pytorch/pytorch:1.12.0-cuda11.3
          command:
          - python
          - /workspace/train.py
          resources:
            requests:
              nvidia.com/gpu: 1
              memory: 16Gi
              cpu: 8
            limits:
              nvidia.com/gpu: 1
              memory: 16Gi
              cpu: 8
        restartPolicy: Never
```

**Volcano Features:**
- Gang scheduling (all-or-nothing)
- Queue management
- Fair sharing between tenants
- Resource reservation
- Preemption
- Priority scheduling

### Kueue for Job Queueing

Kueue provides job queueing and resource management:

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: gpu-a100
spec:
  nodeLabels:
    gpu-type: a100
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: training-queue
spec:
  namespaceSelector: {}
  resourceGroups:
  - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
    flavors:
    - name: gpu-a100
      resources:
      - name: "cpu"
        nominalQuota: 200
      - name: "memory"
        nominalQuota: 1000Gi
      - name: "nvidia.com/gpu"
        nominalQuota: 32
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: ml-team-queue
  namespace: ml-team
spec:
  clusterQueue: training-queue
```

### Scheduler Plugins

Extend scheduler with custom plugins:

```go
// Example: Custom GPU scoring plugin
type GPUScoring struct{}

func (g *GPUScoring) Name() string {
    return "GPUScoring"
}

func (g *GPUScoring) Score(
    ctx context.Context,
    state *framework.CycleState,
    pod *v1.Pod,
    nodeName string,
) (int64, *framework.Status) {
    // TODO: Implement custom scoring logic
    // - Prefer nodes with matching GPU types
    // - Consider GPU memory fragmentation
    // - Factor in data locality

    return score, nil
}
```

## Real-World Patterns {#real-world}

### Pattern 1: Multi-Tier Scheduling

```yaml
# Tier 1: Production inference (highest priority)
apiVersion: v1
kind: Pod
metadata:
  name: prod-inference
spec:
  priorityClassName: critical-inference
  nodeSelector:
    node-type: on-demand
    instance-size: large
  tolerations:
  - key: workload
    operator: Equal
    value: production
    effect: NoSchedule
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: inference
        topologyKey: kubernetes.io/hostname

---
# Tier 2: Training (medium priority)
apiVersion: v1
kind: Pod
metadata:
  name: training-job
spec:
  priorityClassName: training-normal
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: instance-lifecycle
            operator: In
            values:
            - spot  # Prefer spot for cost savings

---
# Tier 3: Experimentation (low priority)
apiVersion: v1
kind: Pod
metadata:
  name: experiment
spec:
  priorityClassName: training-low
  nodeSelector:
    instance-lifecycle: spot
  tolerations:
  - key: instance-type
    operator: Equal
    value: spot
    effect: NoSchedule
```

### Pattern 2: Data Locality

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: data-intensive-training
spec:
  affinity:
    # Schedule near data
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: storage-type
            operator: In
            values:
            - local-nvme
          - key: datacenter
            operator: In
            values:
            - dc1  # Same datacenter as data

    # Schedule near cache pods
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: cache
              dataset: imagenet
          topologyKey: kubernetes.io/hostname

  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: data
      mountPath: /data
      readOnly: true

  volumes:
  - name: data
    hostPath:
      path: /mnt/nvme/datasets/imagenet
      type: Directory
```

### Pattern 3: Bin Packing for Efficiency

```yaml
# Configure scheduler to bin pack (fill nodes completely)
apiVersion: v1
kind: ConfigMap
metadata:
  name: scheduler-config
  namespace: kube-system
data:
  scheduler-config.yaml: |
    apiVersion: kubescheduler.config.k8s.io/v1
    kind: KubeSchedulerConfiguration
    profiles:
    - schedulerName: bin-packing-scheduler
      plugins:
        score:
          disabled:
          - name: NodeResourcesBalancedAllocation  # Disable spreading
          enabled:
          - name: NodeResourcesMostAllocated  # Enable bin packing
            weight: 100
```

### Pattern 4: Elastic Training

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: elastic-training
  annotations:
    # Min/max workers for elastic training
    elastic.pytorch.org/min-replicas: "4"
    elastic.pytorch.org/max-replicas: "16"
spec:
  priorityClassName: training-normal
  containers:
  - name: worker
    image: pytorch/pytorch:1.12.0-cuda11.3
    command:
    - python
    - -m
    - torch.distributed.run
    - --nnodes=4:16  # Elastic from 4 to 16 nodes
    - --nproc_per_node=8
    - train.py
    resources:
      requests:
        nvidia.com/gpu: 8
```

## Summary

Key takeaways:

1. **GPU scheduling** requires careful management of expensive resources with device plugins, labeling, and monitoring
2. **Node affinity** provides flexible node selection with required and preferred rules
3. **Pod affinity/anti-affinity** enables co-location or separation of related pods
4. **Taints and tolerations** dedicate nodes for specific workloads
5. **Priority classes** enable preemption for critical workloads
6. **Resource quotas** prevent resource exhaustion per namespace
7. **Gang scheduling** ensures all-or-nothing scheduling for distributed jobs
8. **Real-world patterns** combine multiple techniques for optimal resource utilization

## Further Reading

- [Kubernetes Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [Volcano Scheduler](https://volcano.sh/)
- [Kueue Documentation](https://kueue.sigs.k8s.io/)

## Next Steps

Next lecture: **StatefulSets and Storage Architecture** - Learn how to manage stateful ML workloads with persistent storage.
