# TrainingJob Operator API Documentation

Complete API reference for the TrainingJob Kubernetes Operator CRD.

## CRD Information

- **API Group**: `mlplatform.example.com`
- **Version**: `v1alpha1`
- **Kind**: `TrainingJob`
- **Plural**: `trainingjobs`
- **Short Names**: `tj`, `trainjob`

## Minimal Example

```yaml
apiVersion: mlplatform.example.com/v1alpha1
kind: TrainingJob
metadata:
  name: my-job
spec:
  framework: pytorch
  image: pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime
  command: ["python", "train.py"]
```

## Spec Fields Reference

### Framework Configuration
- `framework` (string, required): ML framework - `pytorch`, `tensorflow`, `jax`, `mxnet`
- `frameworkVersion` (string, optional): Framework version

### Container Configuration
- `image` (string, required): Container image
- `command` ([]string, required): Command to run
- `args` ([]string, optional): Command arguments
- `env` ([]EnvVar, optional): Environment variables

### Scaling
- `replicas` (integer, default: 1): Number of training replicas (1-100)

### Resources
```yaml
resources:
  requests:
    cpu: "2"
    memory: "4Gi"
  limits:
    cpu: "4"
    memory: "8Gi"
```

### Restart Policy
- `restartPolicy` (string, default: "OnFailure"): `Never`, `OnFailure`, `Always`
- `backoffLimit` (integer, default: 3): Max retries

### Checkpointing
```yaml
checkpoint:
  enabled: true
  interval: 300  # seconds
  path: /checkpoints
  storage: pvc  # pvc, s3, gcs, azure
```

### Monitoring
```yaml
monitoring:
  enabled: true
  port: 9090
  path: /metrics
```

## Status Fields

```yaml
status:
  phase: Running  # Pending, Running, Succeeded, Failed, Unknown
  message: "Training in progress"
  conditions:
    - type: Ready
      status: "True"
      reason: AllReplicasReady
      message: "All replicas ready"
  startTime: "2025-10-17T10:00:00Z"
  completionTime: null
  replicas: 4
  readyReplicas: 4
```

## Examples

### Distributed PyTorch
```yaml
apiVersion: mlplatform.example.com/v1alpha1
kind: TrainingJob
metadata:
  name: pytorch-ddp
spec:
  framework: pytorch
  image: pytorch/pytorch:2.1.0
  command: ["python", "-m", "torch.distributed.launch"]
  args: ["train.py"]
  replicas: 4
  resources:
    requests:
      nvidia.com/gpu: "2"
```

## kubectl Commands

```bash
# Create
kubectl apply -f job.yaml

# List
kubectl get trainingjobs
kubectl get tj  # short name

# Describe
kubectl describe tj my-job

# Logs
kubectl logs -l trainingjob=my-job

# Delete
kubectl delete tj my-job
```

TODO for students: Add volume mounts, node selectors, tolerations, affinity rules
