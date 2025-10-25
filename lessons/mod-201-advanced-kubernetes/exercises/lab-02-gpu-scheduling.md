# Lab 02: Implement Advanced GPU Scheduling

## Objectives

1. Configure GPU resource management with NVIDIA device plugin
2. Implement GPU time-slicing for shared GPU access
3. Set up node affinity for different GPU types
4. Create priority classes for GPU workloads
5. Test preemption scenarios
6. Monitor GPU utilization with DCGM exporter

## Prerequisites

- Kubernetes cluster with GPU nodes (or ability to simulate)
- kubectl access
- Helm 3.x installed
- Understanding of Lecture 02: Advanced Scheduling

## Estimated Time

6 hours

## Part 1: GPU Device Plugin Setup (1 hour)

### Install NVIDIA Device Plugin

```bash
# Add NVIDIA Helm repo
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo update

# Install device plugin
helm install nvdp nvdp/nvidia-device-plugin \
  --namespace kube-system \
  --create-namespace \
  --set-file config.map.config=gpu-config.yaml

# Verify installation
kubectl get pods -n kube-system -l app.kubernetes.io/name=nvidia-device-plugin

# Check GPU resources on nodes
kubectl get nodes -o json | jq '.items[] | {name:.metadata.name, gpus:.status.allocatable["nvidia.com/gpu"]}'
```

### GPU Configuration File (gpu-config.yaml)

```yaml
# TODO: Complete this configuration for your cluster
version: v1
sharing:
  timeSlicing:
    renameByDefault: false
    failRequestsGreaterThanOne: false
    resources:
    - name: nvidia.com/gpu
      replicas: 4  # Each physical GPU appears as 4 logical GPUs
```

## Part 2: GPU Node Labeling (30 minutes)

### Label Nodes by GPU Type

```bash
# TODO: Identify GPU types on your nodes
kubectl get nodes -o json | jq '.items[] | {name:.metadata.name, gpu:.status.capacity["nvidia.com/gpu"]}'

# Label nodes with GPU types
# TODO: Replace node names and GPU types with your actual values
kubectl label node gpu-node-1 gpu-type=a100 gpu-memory=40gb gpu-count=8
kubectl label node gpu-node-2 gpu-type=v100 gpu-memory=16gb gpu-count=4
kubectl label node gpu-node-3 gpu-type=t4 gpu-memory=16gb gpu-count=2

# Verify labels
kubectl get nodes --show-labels | grep gpu
```

## Part 3: Priority Classes for GPU Workloads (1 hour)

### Create Priority Classes

```yaml
# TODO: Apply these priority classes to your cluster
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: gpu-critical
value: 1000000
globalDefault: false
description: "Critical GPU workloads (production inference)"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: gpu-high
value: 100000
globalDefault: false
description: "High priority GPU workloads (urgent training)"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: gpu-normal
value: 10000
globalDefault: true
description: "Normal priority GPU workloads (standard training)"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: gpu-low
value: 1000
globalDefault: false
preemptionPolicy: Never
description: "Low priority GPU workloads (experiments)"
```

### Test Priority and Preemption

```bash
# TODO: Create low priority pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: low-priority-gpu
  labels:
    priority: low
spec:
  priorityClassName: gpu-low
  containers:
  - name: training
    image: nvidia/cuda:11.8.0-base-ubuntu22.04
    command: ["sleep", "3600"]
    resources:
      limits:
        nvidia.com/gpu: 1
EOF

# TODO: Create high priority pod (should preempt low priority)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-gpu
  labels:
    priority: high
spec:
  priorityClassName: gpu-high
  containers:
  - name: inference
    image: nvidia/cuda:11.8.0-base-ubuntu22.04
    command: ["sleep", "3600"]
    resources:
      limits:
        nvidia.com/gpu: 1
EOF

# Watch preemption happen
kubectl get events --sort-by='.lastTimestamp' | grep -i preempt
kubectl get pods -w
```

## Part 4: GPU Node Affinity and Selectors (1 hour)

### Deploy Workloads to Specific GPU Types

```yaml
# TODO: Create deployment targeting A100 GPUs
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a100-training
spec:
  replicas: 2
  selector:
    matchLabels:
      app: a100-training
  template:
    metadata:
      labels:
        app: a100-training
    spec:
      nodeSelector:
        gpu-type: a100
      containers:
      - name: training
        image: pytorch/pytorch:2.0.0-cuda11.8-cudnn8
        command: ["python", "train.py"]
        resources:
          limits:
            nvidia.com/gpu: 2
            memory: 32Gi
          requests:
            nvidia.com/gpu: 2
            memory: 32Gi
```

### Advanced Affinity Rules

```yaml
# TODO: Implement this pod with complex affinity rules
apiVersion: v1
kind: Pod
metadata:
  name: flexible-gpu-pod
spec:
  affinity:
    nodeAffinity:
      # Required: Must have GPU
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: nvidia.com/gpu
            operator: Exists
      # Preferred: Prefer A100, then V100
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: gpu-type
            operator: In
            values:
            - a100
      - weight: 50
        preference:
          matchExpressions:
          - key: gpu-type
            operator: In
            values:
            - v100
  containers:
  - name: training
    image: pytorch/pytorch:2.0.0-cuda11.8-cudnn8
    resources:
      limits:
        nvidia.com/gpu: 1
```

## Part 5: GPU Taints and Tolerations (1 hour)

### Taint GPU Nodes

```bash
# TODO: Taint GPU nodes to dedicate for specific workloads
kubectl taint nodes -l nvidia.com/gpu=true \
  dedicated=gpu:NoSchedule

# Verify taints
kubectl describe nodes | grep -A 5 Taints
```

### Deploy with Tolerations

```yaml
# TODO: Create pod that tolerates GPU taint
apiVersion: v1
kind: Pod
metadata:
  name: tolerated-gpu-pod
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  nodeSelector:
    nvidia.com/gpu: "true"
  containers:
  - name: training
    image: pytorch/pytorch:2.0.0-cuda11.8-cudnn8
    resources:
      limits:
        nvidia.com/gpu: 1
```

## Part 6: GPU Monitoring (1.5 hours)

### Install DCGM Exporter

```bash
# TODO: Deploy DCGM exporter as DaemonSet
kubectl apply -f - <<EOF
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
      nodeSelector:
        nvidia.com/gpu: "true"
      containers:
      - name: dcgm-exporter
        image: nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04
        ports:
        - name: metrics
          containerPort: 9400
        securityContext:
          runAsNonRoot: false
          runAsUser: 0
          capabilities:
            add: ["SYS_ADMIN"]
        volumeMounts:
        - name: pod-gpu-resources
          readOnly: true
          mountPath: /var/lib/kubelet/pod-resources
      volumes:
      - name: pod-gpu-resources
        hostPath:
          path: /var/lib/kubelet/pod-resources
EOF
```

### Create Grafana Dashboard

```yaml
# TODO: Create ConfigMap with Grafana dashboard
apiVersion: v1
kind: ConfigMap
metadata:
  name: gpu-dashboard
  namespace: monitoring
data:
  gpu-dashboard.json: |
    {
      "dashboard": {
        "title": "GPU Utilization",
        "panels": [
          {
            "title": "GPU Utilization %",
            "targets": [
              {
                "expr": "DCGM_FI_DEV_GPU_UTIL"
              }
            ]
          },
          {
            "title": "GPU Memory Used",
            "targets": [
              {
                "expr": "DCGM_FI_DEV_FB_USED"
              }
            ]
          },
          {
            "title": "GPU Temperature",
            "targets": [
              {
                "expr": "DCGM_FI_DEV_GPU_TEMP"
              }
            ]
          }
        ]
      }
    }
```

### Query GPU Metrics

```bash
# TODO: Install Prometheus if not already installed
# Query GPU metrics
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# In another terminal, query:
# GPU utilization: DCGM_FI_DEV_GPU_UTIL
# GPU memory: DCGM_FI_DEV_FB_USED
# GPU power: DCGM_FI_DEV_POWER_USAGE
```

## Part 7: GPU Sharing with Time-Slicing (1 hour)

### Configure Time-Slicing

```yaml
# TODO: Update device plugin config for time-slicing
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
        renameByDefault: false
        resources:
        - name: nvidia.com/gpu
          replicas: 4  # Each GPU appears as 4
```

### Test GPU Sharing

```bash
# TODO: Deploy multiple pods sharing GPUs
for i in {1..8}; do
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: shared-gpu-pod-$i
spec:
  containers:
  - name: cuda
    image: nvidia/cuda:11.8.0-base-ubuntu22.04
    command: ["sleep", "3600"]
    resources:
      limits:
        nvidia.com/gpu: 1  # Logical GPU
EOF
done

# Verify all pods scheduled
kubectl get pods -o wide

# Check actual GPU usage
kubectl exec shared-gpu-pod-1 -- nvidia-smi
```

## Deliverables

1. **GPU device plugin** deployed and functional
2. **Node labels** for GPU types
3. **Priority classes** created and tested
4. **Preemption** demonstrated with test cases
5. **GPU monitoring** with DCGM and Grafana
6. **Time-slicing** configured and tested
7. **Documentation** of:
   - GPU allocation strategy
   - Priority policies
   - Monitoring setup
   - Performance observations

## Testing Checklist

- [ ] Device plugin running on all GPU nodes
- [ ] GPU resources visible in node capacity
- [ ] Priority classes created
- [ ] High priority pods can preempt low priority
- [ ] Node affinity correctly routes to GPU types
- [ ] Taints prevent non-GPU workloads
- [ ] Tolerations allow GPU workloads
- [ ] DCGM exporter collecting metrics
- [ ] Grafana showing GPU utilization
- [ ] Time-slicing allows GPU sharing

## Troubleshooting

### GPUs Not Visible

```bash
# Check device plugin logs
kubectl logs -n kube-system -l app.kubernetes.io/name=nvidia-device-plugin

# Verify NVIDIA drivers on node
kubectl debug node/gpu-node-1 -it --image=ubuntu
# In debug pod:
nvidia-smi
```

### Preemption Not Working

```bash
# Check scheduler logs
kubectl logs -n kube-system -l component=kube-scheduler

# Verify priority class
kubectl get priorityclasses
kubectl describe pod high-priority-gpu
```

### Monitoring Not Working

```bash
# Check DCGM exporter
kubectl logs -n monitoring -l app=dcgm-exporter

# Test metrics endpoint
kubectl port-forward -n monitoring dcgm-exporter-xxxxx 9400:9400
curl localhost:9400/metrics | grep DCGM
```

## Bonus Challenges

1. Implement **MIG (Multi-Instance GPU)** for A100 GPUs
2. Create **custom scheduler** for GPU-aware placement
3. Implement **GPU affinity** for data locality
4. Set up **GPU node autoscaling**
5. Create **cost tracking** for GPU usage
6. Implement **quota management** for GPU resources per team

## Additional Resources

- [NVIDIA Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [DCGM Exporter](https://github.com/NVIDIA/dcgm-exporter)
- [GPU Sharing](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/gpu-sharing.html)
- [MIG Guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)

---

**Remember: GPU resources are expensive. Always clean up test resources when done!**
