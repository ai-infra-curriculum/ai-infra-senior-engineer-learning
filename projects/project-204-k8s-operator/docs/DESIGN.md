# TrainingJob Operator Design Document

System architecture and design decisions for the TrainingJob Kubernetes Operator.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌────────────────┐                                         │
│  │  TrainingJob   │ (Custom Resource)                       │
│  │  CRD           │                                         │
│  └────────────────┘                                         │
│         ↓                                                    │
│  ┌────────────────────────────────────────────────┐         │
│  │         TrainingJob Operator                   │         │
│  │  ┌──────────────┐  ┌─────────────────────┐    │         │
│  │  │  Reconciler  │──│  JobController     │    │         │
│  │  │   (Watch)    │  │  - Validation      │    │         │
│  │  └──────────────┘  │  - Reconciliation  │    │         │
│  │                    └─────────────────────┘    │         │
│  │                            │                   │         │
│  │         ┌──────────────────┼──────────────┐   │         │
│  │         ↓                  ↓               ↓   │         │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐        │
│  │  │  Resource   │  │  Status     │  │Checkpoint│        │
│  │  │ Controller  │  │ Controller  │  │Controller│        │
│  │  └─────────────┘  └─────────────┘  └──────────┘        │
│  └────────────────────────────────────────────────┘         │
│                      ↓                                       │
│  ┌────────────────────────────────────────────┐             │
│  │     Kubernetes Resources                   │             │
│  │  ┌────────┐  ┌─────────┐  ┌────────────┐  │             │
│  │  │  Pods  │  │ Services│  │ ConfigMaps │  │             │
│  │  └────────┘  └─────────┘  └────────────┘  │             │
│  └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Reconciler
- **Purpose**: Watch TrainingJob resources and trigger reconciliation
- **Pattern**: Kubernetes watch loop with event queue
- **Key Features**:
  - Event-driven reconciliation (ADDED, MODIFIED, DELETED)
  - Periodic resync for eventual consistency
  - Worker pool for concurrent reconciliation
  - Retry with exponential backoff

### 2. JobController
- **Purpose**: Main reconciliation logic for TrainingJob lifecycle
- **Responsibilities**:
  - Validate TrainingJob spec
  - Apply defaults
  - Create/update Kubernetes resources
  - Monitor job status
  - Handle phase transitions
- **State Machine**:
  ```
  Pending → Running → Succeeded
                   → Failed
  ```

### 3. ResourceController
- **Purpose**: Manage Kubernetes resources (Pods, Services, etc.)
- **Pattern**: Builder pattern for resource creation
- **Operations**:
  - Create training pods (one per replica)
  - Create headless service (for distributed training)
  - Create master service (for monitoring)
  - Cleanup resources on completion

### 4. StatusController
- **Purpose**: Update TrainingJob status
- **Pattern**: Status subresource updates
- **Updates**:
  - Phase transitions
  - Replica counts
  - Conditions
  - Progress metrics

### 5. CheckpointController
- **Purpose**: Manage training checkpoints
- **Features**:
  - Time-based checkpointing
  - Multiple storage backends (PVC, S3, GCS, Azure)
  - Checkpoint retention policies
  - Checkpoint restoration

## Design Decisions

### Why Custom Resource Definition (CRD)?

**Pros**:
- Native Kubernetes integration
- Declarative configuration
- kubectl support out of the box
- RBAC integration
- Versioning and schema validation

**Alternatives Considered**:
- ConfigMaps: Too limited, no validation
- Jobs API directly: Not flexible enough for ML workloads

### Why Operator Pattern?

**Benefits**:
- Automates operational knowledge
- Handles complex lifecycle management
- Provides self-healing capabilities
- Integrates with Kubernetes ecosystem

### Architecture Patterns

#### 1. Controller Pattern
Standard Kubernetes controller with reconciliation loop:
```
Watch → Event → Reconcile → Update Status
```

#### 2. Builder Pattern
For creating Kubernetes resources:
```python
pod = PodBuilder(job_name, namespace, replica_id) \
    .with_spec(spec) \
    .with_labels(labels) \
    .build()
```

#### 3. Facade Pattern
TrainingJobController provides simplified high-level API.

## Data Flow

### 1. Job Creation
```
User creates TrainingJob
  → CRD validates spec (OpenAPI schema)
  → Event added to queue
  → Reconciler processes event
  → JobController validates & applies defaults
  → ResourceController creates Pods/Services
  → StatusController updates status to Running
```

### 2. Job Monitoring
```
ResourceController polls pod status
  → Status aggregated
  → Checkpoint Controller checks if checkpoint needed
  → StatusController updates replica counts
  → Progress metrics collected
```

### 3. Job Completion
```
All pods succeed
  → StatusController updates phase to Succeeded
  → ResourceController preserves checkpoints
  → (Optional) TTL cleanup after configured time
```

## Resource Management

### Pod Creation
- One pod per replica
- Labels: `trainingjob=<name>`, `replica-id=<N>`
- Owner references for garbage collection
- Resource requests/limits from spec

### Service Creation
- **Headless service**: For pod discovery (distributed training)
- **Master service**: For metrics collection (replica 0)

### Checkpoint Storage
- PVC: Kubernetes PersistentVolumeClaim
- S3/GCS/Azure: Cloud storage with pre-signed URLs

## Scalability

### Concurrency
- Worker pool: 10 concurrent reconciliations (configurable)
- Queue-based event processing
- Rate limiting to prevent API server overload

### Performance
- Watch caching reduces API calls
- Status updates use PATCH (not full replace)
- Periodic resync: Every 5 minutes (configurable)

## Reliability

### Error Handling
- Validation errors: Update status, don't retry
- Transient errors: Exponential backoff retry
- Resource conflicts: Retry with fresh resource version

### High Availability
- Leader election (TODO for students)
- Multiple operator replicas
- Crash recovery via periodic resync

## Security

### RBAC
Required permissions:
- **trainingjobs**: get, list, watch, update, patch
- **trainingjobs/status**: get, update, patch
- **pods**: get, list, watch, create, delete
- **services**: get, list, watch, create, delete

### Pod Security
- ServiceAccount per job (TODO for students)
- SecurityContext for non-root execution
- Resource limits to prevent DoS

## Technology Stack

- **Language**: Python 3.11+
- **Kubernetes Client**: kubernetes-python
- **CRD**: OpenAPI v3 schema validation
- **Monitoring**: Prometheus metrics
- **Logging**: Structured JSON logging

## Extension Points (TODO for Students)

1. **Admission Webhooks**
   - Defaulting webhook: Auto-populate fields
   - Validating webhook: Complex validation logic

2. **Custom Schedulers**
   - GPU-aware scheduling
   - Topology-aware placement

3. **Autoscaling**
   - HPA integration for dynamic replica scaling
   - Vertical pod autoscaling for resources

4. **Multi-Tenancy**
   - Namespace quotas
   - Resource prioritization
   - Fair scheduling

## Testing Strategy

### Unit Tests
- Controller logic
- Validation rules
- Resource builders

### Integration Tests
- End-to-end job lifecycle
- Failure scenarios
- Resource cleanup

### E2E Tests
- Real cluster deployment
- Multi-replica training
- Checkpoint/restore

## TODO for Students

- Implement admission webhooks
- Add leader election for HA
- Implement autoscaling
- Add advanced scheduling
- Integrate with service mesh
- Add cost tracking
- Implement quota management
