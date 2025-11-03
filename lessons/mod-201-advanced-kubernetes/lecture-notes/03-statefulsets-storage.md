# Lecture 03: StatefulSets and Storage Architecture

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and deploy StatefulSets for distributed ML workloads requiring stable identity and persistent storage
- Implement Container Storage Interface (CSI) drivers for high-performance storage in ML training environments
- Configure storage classes and dynamic provisioning for efficient resource allocation across training workloads
- Implement volume snapshots and cloning for checkpoint management and experiment reproducibility
- Optimize data locality and storage performance for large-scale model training and feature stores
- Design backup and restore strategies for stateful ML applications and model registries
- Troubleshoot common StatefulSet issues including pod initialization, volume attachment, and scaling problems
- Evaluate trade-offs between different storage solutions (block vs. file vs. object storage) for ML workloads

## Table of Contents
1. [Introduction to StatefulSets](#introduction)
2. [Persistent Storage for ML Workloads](#persistent-storage)
3. [Container Storage Interface (CSI)](#csi)
4. [Volume Snapshots and Cloning](#snapshots)
5. [Storage Classes and Dynamic Provisioning](#storage-classes)
6. [Data Locality and Performance](#performance)
7. [Backup and Restore Strategies](#backup)

## Introduction to StatefulSets {#introduction}

### What are StatefulSets?

StatefulSets are Kubernetes workload resources designed for stateful applications that require:
- Stable, unique network identifiers
- Stable, persistent storage
- Ordered, graceful deployment and scaling
- Ordered, automated rolling updates

**Key Differences from Deployments:**

| Feature | Deployment | StatefulSet |
|---------|-----------|-------------|
| Pod naming | Random suffix | Ordered index (0,1,2...) |
| Pod identity | Ephemeral | Persistent |
| Scaling | Simultaneous | Sequential |
| Storage | Shared or ephemeral | Dedicated per pod |
| Network identity | Random | Stable DNS |

### When to Use StatefulSets for ML

**Use Cases:**
- Distributed training with checkpoint coordination
- Parameter servers requiring persistent state
- Distributed databases (e.g., feature stores)
- Model registries with persistent storage
- Training jobs needing individual storage per worker
- Systems requiring stable network identities

**Example: Distributed TensorFlow Training**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tensorflow-ps
  labels:
    app: tensorflow
    role: ps
spec:
  clusterIP: None  # Headless service
  selector:
    app: tensorflow
    role: ps
  ports:
  - port: 2222
    name: ps-port
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tensorflow-ps
spec:
  serviceName: tensorflow-ps
  replicas: 3
  selector:
    matchLabels:
      app: tensorflow
      role: ps
  template:
    metadata:
      labels:
        app: tensorflow
        role: ps
    spec:
      containers:
      - name: ps
        image: tensorflow/tensorflow:2.11.0-gpu
        command:
        - python
        - -c
        - |
          import tensorflow as tf
          import os

          cluster_spec = {
              "ps": [f"tensorflow-ps-{i}.tensorflow-ps.default.svc.cluster.local:2222"
                     for i in range(3)],
              "worker": [f"tensorflow-worker-{i}.tensorflow-worker.default.svc.cluster.local:2223"
                        for i in range(5)]
          }

          task_index = int(os.environ.get("HOSTNAME").split("-")[-1])

          server = tf.distribute.Server(
              cluster_spec,
              job_name="ps",
              task_index=task_index
          )
          server.join()
        ports:
        - containerPort: 2222
          name: ps-port
        volumeMounts:
        - name: checkpoint-storage
          mountPath: /checkpoints
  volumeClaimTemplates:
  - metadata:
      name: checkpoint-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### StatefulSet Features

**1. Stable Network Identity**

Each pod gets a predictable DNS name:
```
<statefulset-name>-<ordinal>.<service-name>.<namespace>.svc.cluster.local

Example: tensorflow-ps-0.tensorflow-ps.default.svc.cluster.local
```

**2. Ordered Deployment**

Pods are created sequentially:
```
1. Create pod-0, wait for Running and Ready
2. Create pod-1, wait for Running and Ready
3. Create pod-2, ...
```

**3. Ordered Termination**

Pods are terminated in reverse order:
```
1. Terminate pod-2, wait for deletion
2. Terminate pod-1, wait for deletion
3. Terminate pod-0
```

**4. Volume Claim Templates**

Each pod gets its own PVC:
```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 1Ti
```

This creates:
- `data-mystatefulset-0` for pod 0
- `data-mystatefulset-1` for pod 1
- etc.

### StatefulSet Update Strategies

**RollingUpdate (default):**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: training-workers
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2  # Update pods >= 2 only (canary deployment)
  # ...
```

**OnDelete:**
```yaml
spec:
  updateStrategy:
    type: OnDelete  # Manual pod deletion required for update
```

### Pod Management Policies

**OrderedReady (default):**
- Sequential creation/deletion
- Wait for each pod to be ready

**Parallel:**
```yaml
spec:
  podManagementPolicy: Parallel
  # Pods created/deleted simultaneously (still get stable identities)
```

## Persistent Storage for ML Workloads {#persistent-storage}

### Storage Types for ML

**1. Training Data Storage**
- Large datasets (hundreds of GB to TB)
- Read-heavy workload
- Shared across multiple jobs
- Requirements: High throughput, parallel access

**2. Checkpoint Storage**
- Model weights and optimizer state
- Periodic writes during training
- Read on job restart
- Requirements: Low latency, consistency

**3. Model Registry Storage**
- Versioned model artifacts
- Infrequent updates
- Requirements: Durability, versioning

**4. Feature Store Storage**
- Pre-computed features
- High-throughput reads during training
- Requirements: Low latency, high IOPS

**5. Logs and Metrics**
- Training logs, metrics, tensorboard data
- Continuous writes
- Requirements: Cost-effective, searchable

### PersistentVolume and PersistentVolumeClaim

**PersistentVolume (PV):** Cluster-level storage resource

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: training-data-pv
spec:
  capacity:
    storage: 10Ti
  accessModes:
  - ReadOnlyMany  # Multiple pods can read
  persistentVolumeReclaimPolicy: Retain
  storageClassName: shared-nfs
  mountOptions:
  - nfsvers=4.1
  - rsize=1048576
  - wsize=1048576
  nfs:
    path: /exports/training-data
    server: nfs-server.example.com
```

**PersistentVolumeClaim (PVC):** Namespace-level storage request

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: training-data-pvc
  namespace: ml-team
spec:
  accessModes:
  - ReadOnlyMany
  storageClassName: shared-nfs
  resources:
    requests:
      storage: 10Ti
```

**Access Modes:**
- `ReadWriteOnce` (RWO): Single node read-write (most common)
- `ReadOnlyMany` (ROX): Multiple nodes read-only (shared datasets)
- `ReadWriteMany` (RWX): Multiple nodes read-write (rare, expensive)
- `ReadWriteOncePod` (RWOP): Single pod read-write (1.22+)

### Storage Patterns for ML

**Pattern 1: Shared Dataset with Local Caching**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-pod
spec:
  initContainers:
  # Copy data to local disk on startup
  - name: data-loader
    image: alpine:latest
    command:
    - sh
    - -c
    - |
      cp -r /shared-data/* /local-cache/
    volumeMounts:
    - name: shared-data
      mountPath: /shared-data
      readOnly: true
    - name: local-cache
      mountPath: /local-cache

  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: local-cache
      mountPath: /data
      readOnly: true
    - name: checkpoints
      mountPath: /checkpoints

  volumes:
  - name: shared-data
    persistentVolumeClaim:
      claimName: imagenet-pvc
      readOnly: true
  - name: local-cache
    emptyDir:
      sizeLimit: 500Gi
  - name: checkpoints
    persistentVolumeClaim:
      claimName: training-checkpoints-pvc
```

**Pattern 2: Per-Worker Checkpoints**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: distributed-training
spec:
  serviceName: training
  replicas: 8
  template:
    spec:
      containers:
      - name: worker
        image: pytorch/pytorch:1.12.0-cuda11.3
        volumeMounts:
        - name: worker-checkpoint
          mountPath: /checkpoints
        - name: shared-data
          mountPath: /data
          readOnly: true
      volumes:
      - name: shared-data
        persistentVolumeClaim:
          claimName: shared-training-data

  volumeClaimTemplates:
  - metadata:
      name: worker-checkpoint
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 200Gi
```

**Pattern 3: Data Locality with HostPath**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: local-data-training
spec:
  nodeSelector:
    data-node: imagenet-cached
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: local-nvme
      mountPath: /data
      readOnly: true
  volumes:
  - name: local-nvme
    hostPath:
      path: /mnt/nvme/datasets/imagenet
      type: Directory
```

## Container Storage Interface (CSI) {#csi}

### Understanding CSI

CSI is a standard for exposing storage systems to containerized workloads. It separates storage logic from Kubernetes core.

**CSI Architecture:**

```
┌─────────────────────────────────────┐
│     Kubernetes Control Plane        │
│  ┌──────────────────────────────┐  │
│  │   External Provisioner        │  │
│  │   External Attacher           │  │
│  │   External Snapshotter        │  │
│  └────────────┬─────────────────┘  │
└───────────────┼─────────────────────┘
                │ CSI API (gRPC)
┌───────────────▼─────────────────────┐
│         CSI Driver                  │
│  ┌──────────────────────────────┐  │
│  │  Controller Service           │  │
│  │  (CreateVolume, DeleteVolume)│  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                │
┌───────────────▼─────────────────────┐
│      Storage System                 │
│   (EBS, NFS, Ceph, etc.)           │
└─────────────────────────────────────┘
```

### Popular CSI Drivers for ML

**1. AWS EBS CSI Driver**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "16000"
  throughput: "1000"
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**2. GCP Persistent Disk CSI Driver**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: pd-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**3. Azure Disk CSI Driver**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: managed-premium
provisioner: disk.csi.azure.com
parameters:
  storageaccounttype: Premium_LRS
  kind: Managed
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**4. Rook-Ceph CSI Driver (for on-prem)**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-rbd
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: ml-pool
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: Immediate
```

**5. NFS CSI Driver**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.example.com
  share: /exports/ml-data
mountOptions:
  - nfsvers=4.1
  - rsize=1048576
  - wsize=1048576
  - hard
  - timeo=600
  - retrans=2
```

### CSI Features for ML

**Volume Expansion:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: expanding-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ebs-gp3
  resources:
    requests:
      storage: 100Gi

# Later, edit the PVC to expand:
# kubectl edit pvc expanding-pvc
# Change storage: 100Gi to storage: 500Gi
```

**Volume Topology:**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: zone-aware-storage
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer  # Delays binding until pod scheduled
allowedTopologies:
- matchLabelExpressions:
  - key: topology.ebs.csi.aws.com/zone
    values:
    - us-west-2a
    - us-west-2b
```

## Volume Snapshots and Cloning {#snapshots}

### Volume Snapshots

Create point-in-time copies of volumes for backup or cloning.

**VolumeSnapshotClass:**

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  encrypted: "true"
```

**Creating a Snapshot:**

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: checkpoint-snapshot-v1
  namespace: ml-team
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: training-checkpoint-pvc
```

**Restoring from Snapshot:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-checkpoint-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ebs-gp3
  dataSource:
    name: checkpoint-snapshot-v1
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  resources:
    requests:
      storage: 200Gi
```

### Volume Cloning

Clone volumes without snapshots (faster for same zone):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: ebs-gp3
  dataSource:
    name: source-pvc
    kind: PersistentVolumeClaim
  resources:
    requests:
      storage: 200Gi
```

### ML Use Cases for Snapshots

**1. Checkpoint Management:**

```bash
# Script to snapshot checkpoint after training epoch
#!/bin/bash

EPOCH=$1
NAMESPACE="ml-team"
PVC_NAME="training-checkpoint-pvc"

kubectl create -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: checkpoint-epoch-${EPOCH}
  namespace: ${NAMESPACE}
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: ${PVC_NAME}
EOF
```

**2. Experiment Branching:**

```yaml
# Clone checkpoint to try different hyperparameters
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: experiment-branch-lr001
spec:
  dataSource:
    name: checkpoint-epoch-100
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
  - ReadWriteOnce
  storageClassName: ebs-gp3
  resources:
    requests:
      storage: 200Gi
```

**3. Dataset Versioning:**

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: dataset-imagenet-v2-2024-01
  labels:
    dataset: imagenet
    version: v2
    date: "2024-01"
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: imagenet-preprocessing-pvc
```

## Storage Classes and Dynamic Provisioning {#storage-classes}

### Storage Class Design for ML

**Performance Tiers:**

```yaml
# Tier 1: Ultra-high performance (active training)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ultra-fast
provisioner: ebs.csi.aws.com
parameters:
  type: io2
  iops: "64000"
  throughput: "4000"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
# Tier 2: High performance (checkpoints)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "16000"
  throughput: "1000"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
# Tier 3: Balanced (datasets)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: balanced
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
# Tier 4: Archival (completed experiments)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: archival
provisioner: ebs.csi.aws.com
parameters:
  type: st1  # Throughput-optimized HDD
volumeBindingMode: Immediate
allowVolumeExpansion: true
```

### Reclaim Policies

**Retain:** Keep data after PVC deletion
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: important-data
provisioner: ebs.csi.aws.com
reclaimPolicy: Retain  # Manual cleanup required
```

**Delete:** Auto-delete after PVC deletion (default)
```yaml
reclaimPolicy: Delete  # Automatic cleanup
```

**Recycle:** Deprecated, use Delete instead

### Volume Binding Modes

**Immediate:** Volume created immediately
```yaml
volumeBindingMode: Immediate
# Pro: Fast PVC binding
# Con: May provision in wrong zone
```

**WaitForFirstConsumer:** Volume created when pod scheduled
```yaml
volumeBindingMode: WaitForFirstConsumer
# Pro: Correct topology (same zone as pod)
# Con: First pod startup slower
```

## Data Locality and Performance {#performance}

### Performance Optimization Strategies

**1. Use Local NVMe for Hot Data**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: local-nvme-training
spec:
  nodeSelector:
    storage: local-nvme
  initContainers:
  - name: data-loader
    image: alpine:latest
    command:
    - sh
    - -c
    - |
      # Copy dataset to local NVMe
      time cp -r /remote-data/* /local-nvme/
      echo "Data loading complete"
    volumeMounts:
    - name: remote-data
      mountPath: /remote-data
    - name: local-nvme
      mountPath: /local-nvme
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: local-nvme
      mountPath: /data
  volumes:
  - name: remote-data
    persistentVolumeClaim:
      claimName: s3-dataset-pvc
  - name: local-nvme
    hostPath:
      path: /mnt/nvme0n1/training-data
      type: DirectoryOrCreate
```

**2. Use emptyDir with Memory**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: memory-backed-cache
spec:
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: memory-cache
      mountPath: /cache
  volumes:
  - name: memory-cache
    emptyDir:
      medium: Memory  # RAM-backed
      sizeLimit: 32Gi
```

**3. Optimize Mount Options**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: optimized-nfs
spec:
  capacity:
    storage: 10Ti
  accessModes:
  - ReadOnlyMany
  mountOptions:
  - nfsvers=4.1
  - rsize=1048576    # 1MB read size
  - wsize=1048576    # 1MB write size
  - hard             # Hard mount
  - timeo=600        # 60 second timeout
  - retrans=2        # 2 retransmissions
  - nordirplus       # Disable READDIRPLUS
  nfs:
    path: /exports/training-data
    server: nfs-server.example.com
```

**4. Use DaemonSet for Data Caching**

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: dataset-cache
spec:
  selector:
    matchLabels:
      app: dataset-cache
  template:
    metadata:
      labels:
        app: dataset-cache
    spec:
      nodeSelector:
        node-type: gpu
      initContainers:
      - name: cache-loader
        image: alpine:latest
        command:
        - sh
        - -c
        - |
          # Cache dataset on all GPU nodes
          if [ ! -d "/cache/imagenet/complete" ]; then
            rsync -avz /remote/imagenet/ /cache/imagenet/
            touch /cache/imagenet/complete
          fi
        volumeMounts:
        - name: cache
          mountPath: /cache
        - name: remote
          mountPath: /remote
      containers:
      - name: pause
        image: gcr.io/google_containers/pause:latest
      volumes:
      - name: cache
        hostPath:
          path: /mnt/nvme/cache
      - name: remote
        nfs:
          server: nfs-server.example.com
          path: /exports/datasets
```

### Performance Benchmarking

```bash
# Test sequential read performance
kubectl run fio-test --rm -it --image=ljishen/fio \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "fio-test",
      "image": "ljishen/fio",
      "args": [
        "--name=seqread",
        "--rw=read",
        "--bs=1m",
        "--size=10g",
        "--numjobs=4",
        "--time_based",
        "--runtime=60",
        "--directory=/data"
      ],
      "volumeMounts": [{
        "name": "test-volume",
        "mountPath": "/data"
      }]
    }],
    "volumes": [{
      "name": "test-volume",
      "persistentVolumeClaim": {
        "claimName": "test-pvc"
      }
    }]
  }
}'

# Test random read IOPS
kubectl run fio-iops --rm -it --image=ljishen/fio \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "fio-iops",
      "image": "ljishen/fio",
      "args": [
        "--name=randread",
        "--rw=randread",
        "--bs=4k",
        "--size=10g",
        "--numjobs=16",
        "--iodepth=64",
        "--time_based",
        "--runtime=60",
        "--directory=/data"
      ],
      "volumeMounts": [{
        "name": "test-volume",
        "mountPath": "/data"
      }]
    }],
    "volumes": [{
      "name": "test-volume",
      "persistentVolumeClaim": {
        "claimName": "test-pvc"
      }
    }]
  }
}'
```

## Backup and Restore Strategies {#backup}

### Velero for Kubernetes Backup

**Installing Velero:**

```bash
# Install Velero CLI
brew install velero

# Install Velero server
velero install \
    --provider aws \
    --plugins velero/velero-plugin-for-aws:v1.7.0 \
    --bucket ml-cluster-backups \
    --backup-location-config region=us-west-2 \
    --snapshot-location-config region=us-west-2 \
    --secret-file ./credentials-velero
```

**Backup StatefulSet with Volumes:**

```yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: training-statefulset-backup
  namespace: velero
spec:
  includedNamespaces:
  - ml-team
  includedResources:
  - statefulsets
  - persistentvolumeclaims
  - persistentvolumes
  labelSelector:
    matchLabels:
      app: distributed-training
  snapshotVolumes: true
  ttl: 720h  # 30 days
```

**Scheduled Backups:**

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: ml-nightly-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  template:
    includedNamespaces:
    - ml-team
    snapshotVolumes: true
    ttl: 720h
```

**Restore from Backup:**

```bash
# List backups
velero backup get

# Restore specific backup
velero restore create --from-backup training-statefulset-backup

# Restore to different namespace
velero restore create --from-backup training-statefulset-backup \
    --namespace-mappings ml-team:ml-team-restored
```

### Application-Level Backup

**Checkpoint Management Sidecar:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: training-with-backup
spec:
  containers:
  - name: training
    image: pytorch/pytorch:1.12.0-cuda11.3
    volumeMounts:
    - name: checkpoints
      mountPath: /checkpoints

  - name: checkpoint-backup
    image: amazon/aws-cli:latest
    command:
    - sh
    - -c
    - |
      while true; do
        # Watch for new checkpoints
        inotifywait -r -e close_write /checkpoints

        # Sync to S3
        aws s3 sync /checkpoints s3://ml-checkpoints/job-${JOB_ID}/ \
          --exclude "*.tmp"

        echo "Checkpoint backed up at $(date)"
      done
    env:
    - name: JOB_ID
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    volumeMounts:
    - name: checkpoints
      mountPath: /checkpoints
      readOnly: true

  volumes:
  - name: checkpoints
    persistentVolumeClaim:
      claimName: training-checkpoints
```

### Disaster Recovery Plan

**1. Regular Backups:**
- Velero daily backups of entire namespaces
- Volume snapshots of critical PVCs
- Application-level checkpoints to object storage

**2. Testing:**
```bash
# Test restore monthly
velero restore create --from-backup monthly-test-backup \
    --namespace-mappings production:dr-test

# Validate functionality
kubectl -n dr-test get pods
kubectl -n dr-test exec -it test-pod -- pytest
```

**3. Documentation:**
```markdown
## Disaster Recovery Procedure

### Full Cluster Loss
1. Provision new cluster
2. Install Velero: `velero install ...`
3. Restore backups: `velero restore create --from-backup latest-backup`
4. Verify all StatefulSets running
5. Validate data integrity

### Single Namespace Loss
1. velero restore create --from-backup latest-backup \
     --include-namespaces ml-team
2. Verify PVCs bound
3. Check pod status

### Data Corruption
1. Identify last good snapshot
2. Create new PVC from snapshot
3. Update StatefulSet to use new PVC
4. Restart pods
```

## Summary

Key takeaways:

1. **StatefulSets** provide stable identities and persistent storage for stateful ML workloads
2. **CSI drivers** standardize storage integration across different providers
3. **Volume snapshots** enable checkpoint management and experiment branching
4. **Storage classes** create performance tiers for different workload needs
5. **Data locality** dramatically impacts training performance
6. **Backup strategies** combine Kubernetes-level and application-level approaches
7. **Performance optimization** requires understanding storage characteristics and access patterns

## Further Reading

- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Container Storage Interface Spec](https://github.com/container-storage-interface/spec)
- [Velero Documentation](https://velero.io/docs/)
- [Performance Tuning for Storage](https://kubernetes.io/docs/tasks/administer-cluster/storage-performance/)

## Next Steps

Next lecture: **Advanced Networking and Service Mesh** - Learn how to implement sophisticated networking for ML microservices.
