# Project 204: Operator Architecture

## Operator Pattern

```
┌──────────────────────────────────────────────────────────────┐
│                    Kubernetes API Server                      │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ (Watch TrainingJob resources)
                         │
┌──────────────────────────────────────────────────────────────┐
│                  Training Job Operator                        │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Reconciliation Loop                        │ │
│  │  1. Observe TrainingJob state                          │ │
│  │  2. Compare with desired state                         │ │
│  │  3. Take actions to converge                           │ │
│  │  4. Update status                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Controllers:                                                │
│  - Job Controller (create/delete jobs)                       │
│  - Resource Controller (allocate resources)                  │
│  - Checkpoint Controller (manage checkpoints)                │
│  - Status Controller (update job status)                     │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ (Create/Update/Delete)
                         │
┌──────────────────────────────────────────────────────────────┐
│               Kubernetes Resources                            │
│  - Jobs                                                       │
│  - Pods                                                       │
│  - Services                                                   │
│  - ConfigMaps                                                 │
│  - PVCs                                                       │
└──────────────────────────────────────────────────────────────┘
```

## Custom Resource Definition

```yaml
apiVersion: ml.example.com/v1
kind: TrainingJob
metadata:
  name: resnet-training
spec:
  model: resnet50
  dataset: imagenet
  numWorkers: 4
  gpusPerWorker: 2
  resources:
    limits:
      nvidia.com/gpu: 8
  checkpoint:
    enabled: true
    frequency: 5
status:
  phase: Running
  progress: 45%
  currentEpoch: 23
  metrics:
    loss: 0.45
```

## Reconciliation Flow

1. User creates TrainingJob CR
2. Operator detects new resource
3. Validate job specification
4. Create Ray cluster resources
5. Submit training job
6. Monitor progress
7. Update status
8. Handle completion/failure
9. Cleanup resources

## Controller Design

- **Job Controller**: Main reconciliation logic
- **Resource Controller**: GPU/CPU allocation
- **Checkpoint Controller**: Checkpoint lifecycle
- **Metrics Controller**: Collect and expose metrics
