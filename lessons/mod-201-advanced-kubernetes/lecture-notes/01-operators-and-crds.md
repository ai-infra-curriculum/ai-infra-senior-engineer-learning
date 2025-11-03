# Lecture 01: Kubernetes Operators and Custom Resource Definitions

## Learning Objectives

By the end of this lecture, you will be able to:

- Design and implement production-grade Kubernetes operators using the controller-runtime framework
- Create Custom Resource Definitions (CRDs) that extend the Kubernetes API for ML-specific workloads
- Build reconciliation loops that handle complex distributed training and inference scenarios
- Implement proper status reporting, conditions, and observability for operator-managed resources
- Apply best practices for operator development including idempotency, finalizers, and error handling
- Integrate ML-specific operators (KubeFlow, Ray) into existing platform architectures
- Evaluate trade-offs between building custom operators versus leveraging existing frameworks
- Design operators that achieve Level 3-4 maturity (full lifecycle management and deep insights)

## Table of Contents
1. [Introduction to the Operator Pattern](#introduction)
2. [Understanding Custom Resource Definitions](#crds)
3. [Controller Runtime and Reconciliation](#controller-runtime)
4. [Building Operators](#building-operators)
5. [ML-Specific Operators](#ml-operators)
6. [Best Practices](#best-practices)
7. [Real-World Examples](#examples)

## Introduction to the Operator Pattern {#introduction}

### What is an Operator?

A Kubernetes operator is a method of packaging, deploying, and managing a Kubernetes application. Operators extend the Kubernetes API to create, configure, and manage instances of complex applications on behalf of users.

The operator pattern was popularized by CoreOS (now part of Red Hat) and represents the culmination of years of experience running stateful applications on Kubernetes.

**Key Concept:** An operator is human operational knowledge encoded as software that automates application management tasks.

### The Problem Operators Solve

Traditional Kubernetes resources (Deployments, Services, etc.) work well for stateless applications but struggle with stateful, complex applications that require:

- Custom initialization procedures
- Complex upgrade logic
- Application-aware scaling
- Backup and restore operations
- Failure recovery with application knowledge
- Integration with external systems

**Example Scenario:** Consider deploying a distributed ML training job. You need to:
- Coordinate multiple worker pods
- Handle parameter server setup
- Manage checkpoint storage
- Handle worker failures and restarts
- Clean up resources after completion
- Monitor training progress

This complexity is difficult to express with basic Kubernetes primitives. An operator automates these tasks.

### Operator Architecture

```
┌─────────────────────────────────────────────┐
│           Kubernetes API Server              │
└─────────────────┬───────────────────────────┘
                  │
                  │ Watch/List
                  │
┌─────────────────▼───────────────────────────┐
│              Operator                        │
│  ┌──────────────────────────────────────┐  │
│  │    Controller/Reconciliation Loop    │  │
│  │                                       │  │
│  │  1. Observe current state            │  │
│  │  2. Compare to desired state         │  │
│  │  3. Take action to reconcile         │  │
│  └──────────────────────────────────────┘  │
└─────────────────┬───────────────────────────┘
                  │
                  │ Create/Update/Delete
                  │
┌─────────────────▼───────────────────────────┐
│        Kubernetes Resources                  │
│   (Pods, Services, ConfigMaps, etc.)        │
└─────────────────────────────────────────────┘
```

### The Control Loop

At the heart of every operator is a control loop (reconciliation loop):

```go
for {
    desired := getDesiredState()
    current := getCurrentState()

    if current != desired {
        reconcile(current, desired)
    }

    wait()
}
```

This pattern, borrowed from control theory, continuously drives the system toward the desired state.

### Operator Maturity Model

Operators can be classified by their capability level:

1. **Level 1 - Basic Install:** Automated application provisioning and configuration
2. **Level 2 - Seamless Upgrades:** Automated updates with no manual intervention
3. **Level 3 - Full Lifecycle:** App lifecycle, storage lifecycle, backup/restore
4. **Level 4 - Deep Insights:** Metrics, alerts, log processing, workload analysis
5. **Level 5 - Auto Pilot:** Horizontal/vertical scaling, auto-config tuning, abnormality detection, scheduling tuning

**Goal for Senior Engineers:** Build Level 3-4 operators for ML workloads.

## Understanding Custom Resource Definitions {#crds}

### What are CRDs?

Custom Resource Definitions (CRDs) extend the Kubernetes API with custom resource types. They allow you to define your own API objects specific to your application domain.

### CRD Structure

A CRD consists of:
1. **Group:** API group (e.g., `ml.example.com`)
2. **Version:** API version (e.g., `v1alpha1`, `v1beta1`, `v1`)
3. **Kind:** Resource type (e.g., `TrainingJob`)
4. **Spec:** Desired state defined by user
5. **Status:** Current state observed by operator

### Example: ML Training Job CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: trainingjobs.ml.example.com
spec:
  group: ml.example.com
  names:
    kind: TrainingJob
    listKind: TrainingJobList
    plural: trainingjobs
    singular: trainingjob
    shortNames:
    - tj
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              framework:
                type: string
                enum: ["pytorch", "tensorflow"]
              workers:
                type: integer
                minimum: 1
                maximum: 100
              gpuPerWorker:
                type: integer
                minimum: 0
                maximum: 8
              image:
                type: string
              command:
                type: array
                items:
                  type: string
              dataVolume:
                type: object
                properties:
                  claimName:
                    type: string
              checkpointDir:
                type: string
              hyperparameters:
                type: object
                x-kubernetes-preserve-unknown-fields: true
            required:
            - framework
            - workers
            - image
            - command
          status:
            type: object
            properties:
              phase:
                type: string
                enum: ["Pending", "Running", "Succeeded", "Failed"]
              startTime:
                type: string
                format: date-time
              completionTime:
                type: string
                format: date-time
              workerStatuses:
                type: array
                items:
                  type: object
                  properties:
                    workerId:
                      type: integer
                    podName:
                      type: string
                    status:
                      type: string
              conditions:
                type: array
                items:
                  type: object
                  properties:
                    type:
                      type: string
                    status:
                      type: string
                    reason:
                      type: string
                    message:
                      type: string
                    lastTransitionTime:
                      type: string
                      format: date-time
    subresources:
      status: {}
    additionalPrinterColumns:
    - name: Framework
      type: string
      jsonPath: .spec.framework
    - name: Workers
      type: integer
      jsonPath: .spec.workers
    - name: Phase
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
```

### CRD Validation

OpenAPI v3 schema validation ensures:
- Type safety (string, integer, boolean, etc.)
- Required fields
- Value constraints (min/max, enum, regex)
- Nested structure validation

**Best Practice:** Always include comprehensive validation in your CRD schema.

### Using the Custom Resource

Once the CRD is registered, users can create instances:

```yaml
apiVersion: ml.example.com/v1alpha1
kind: TrainingJob
metadata:
  name: mnist-training
  namespace: ml-team
spec:
  framework: pytorch
  workers: 4
  gpuPerWorker: 1
  image: pytorch/pytorch:1.12.0-cuda11.3
  command:
  - python
  - /workspace/train.py
  - --epochs=10
  - --batch-size=64
  dataVolume:
    claimName: training-data-pvc
  checkpointDir: /checkpoints/mnist
  hyperparameters:
    learningRate: 0.001
    optimizer: adam
    momentum: 0.9
```

Users interact with it like any Kubernetes resource:

```bash
kubectl apply -f mnist-training.yaml
kubectl get trainingjobs
kubectl describe trainingjob mnist-training
kubectl delete trainingjob mnist-training
```

## Controller Runtime and Reconciliation {#controller-runtime}

### The Controller-Runtime Library

Controller-runtime is a Go library that provides:
- Client for interacting with Kubernetes API
- Cache for efficient resource watching
- Manager for running multiple controllers
- Webhook server for admission control
- Testing utilities

It's the foundation for both operator-sdk and kubebuilder.

### The Reconciliation Loop

The reconcile function is called whenever:
1. A custom resource is created, updated, or deleted
2. Related resources (Pods, Services) change
3. Periodic re-sync occurs

**Reconcile Function Signature:**

```go
func (r *TrainingJobReconciler) Reconcile(
    ctx context.Context,
    req ctrl.Request,
) (ctrl.Result, error) {
    // req contains namespace and name of the resource
    // Returns Result and error
}
```

### Reconciliation Pattern

```go
func (r *TrainingJobReconciler) Reconcile(
    ctx context.Context,
    req ctrl.Request,
) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // 1. Fetch the TrainingJob instance
    trainingJob := &mlv1alpha1.TrainingJob{}
    err := r.Get(ctx, req.NamespacedName, trainingJob)
    if err != nil {
        if errors.IsNotFound(err) {
            // Resource deleted, cleanup if needed
            return ctrl.Result{}, nil
        }
        return ctrl.Result{}, err
    }

    // 2. Check if being deleted (finalizer pattern)
    if !trainingJob.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, trainingJob)
    }

    // 3. Add finalizer if not present
    if !containsString(trainingJob.Finalizers, finalizerName) {
        trainingJob.Finalizers = append(trainingJob.Finalizers, finalizerName)
        if err := r.Update(ctx, trainingJob); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 4. Reconcile the desired state
    if err := r.reconcileWorkers(ctx, trainingJob); err != nil {
        return ctrl.Result{}, err
    }

    if err := r.reconcileService(ctx, trainingJob); err != nil {
        return ctrl.Result{}, err
    }

    // 5. Update status
    if err := r.updateStatus(ctx, trainingJob); err != nil {
        return ctrl.Result{}, err
    }

    // 6. Requeue if needed
    if trainingJob.Status.Phase == mlv1alpha1.PhaseRunning {
        // Check again in 30 seconds
        return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
    }

    return ctrl.Result{}, nil
}
```

### Idempotency

**Critical Principle:** Reconciliation must be idempotent.

The same reconcile call may be executed multiple times:
- Due to errors and retries
- Due to periodic re-sync
- Due to related resource changes

Your reconcile logic must handle repeated execution safely:

```go
// BAD: Not idempotent
func (r *Reconciler) reconcile(ctx context.Context, obj *MyResource) error {
    // Always creates, will fail on second call
    pod := constructPod(obj)
    return r.Create(ctx, pod)
}

// GOOD: Idempotent
func (r *Reconciler) reconcile(ctx context.Context, obj *MyResource) error {
    pod := &corev1.Pod{}
    err := r.Get(ctx, types.NamespacedName{
        Name: obj.Name + "-pod",
        Namespace: obj.Namespace,
    }, pod)

    if errors.IsNotFound(err) {
        // Create if doesn't exist
        pod = constructPod(obj)
        return r.Create(ctx, pod)
    } else if err != nil {
        return err
    }

    // Update if needed
    if needsUpdate(pod, obj) {
        updatePod(pod, obj)
        return r.Update(ctx, pod)
    }

    return nil
}
```

### Owner References and Garbage Collection

Set owner references so Kubernetes automatically cleans up child resources:

```go
import (
    ctrl "sigs.k8s.io/controller-runtime"
)

func constructPod(trainingJob *mlv1alpha1.TrainingJob) *corev1.Pod {
    pod := &corev1.Pod{
        ObjectMeta: metav1.ObjectMeta{
            Name:      trainingJob.Name + "-worker-0",
            Namespace: trainingJob.Namespace,
        },
        Spec: corev1.PodSpec{
            // ... pod spec
        },
    }

    // Set owner reference - pod will be deleted when TrainingJob is deleted
    ctrl.SetControllerReference(trainingJob, pod, r.Scheme)

    return pod
}
```

### Watching Related Resources

Controllers can watch multiple resource types:

```go
func (r *TrainingJobReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&mlv1alpha1.TrainingJob{}).        // Primary resource
        Owns(&corev1.Pod{}).                    // Owned resources
        Watches(
            &source.Kind{Type: &corev1.ConfigMap{}},
            handler.EnqueueRequestsFromMapFunc(r.findJobsForConfigMap),
        ).
        Complete(r)
}

func (r *TrainingJobReconciler) findJobsForConfigMap(
    obj client.Object,
) []reconcile.Request {
    // Return list of TrainingJobs to reconcile when ConfigMap changes
    // TODO: Implement logic to find affected TrainingJobs
    return []reconcile.Request{}
}
```

## Building Operators {#building-operators}

### Operator SDK vs Kubebuilder

Two popular frameworks for building operators:

**Operator SDK:**
- Built by Red Hat/CoreOS
- More opinionated, includes scaffolding for Helm and Ansible operators
- Better integration with OperatorHub
- Includes operator lifecycle management

**Kubebuilder:**
- Built by Kubernetes SIG
- More focused on Go-based operators
- Lighter weight, closer to controller-runtime
- Excellent documentation

**Recommendation:** Both are excellent. Kubebuilder for simpler operators, Operator SDK for complex operators that need lifecycle management.

### Setting Up Operator Development Environment

```bash
# Install Go 1.19+
# Install Docker or Podman

# Install operator-sdk
brew install operator-sdk
# or
curl -LO https://github.com/operator-framework/operator-sdk/releases/latest/download/operator-sdk_linux_amd64
chmod +x operator-sdk_linux_amd64
sudo mv operator-sdk_linux_amd64 /usr/local/bin/operator-sdk

# Install kubebuilder (alternative)
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)
chmod +x kubebuilder
sudo mv kubebuilder /usr/local/bin/
```

### Creating an Operator Project

```bash
# Create directory
mkdir training-job-operator
cd training-job-operator

# Initialize operator project
operator-sdk init --domain example.com --repo github.com/example/training-job-operator

# Create API and Controller
operator-sdk create api --group ml --version v1alpha1 --kind TrainingJob --resource --controller

# This creates:
# - api/v1alpha1/trainingjob_types.go (CRD definition)
# - controllers/trainingjob_controller.go (Controller logic)
# - config/ (Kubernetes manifests)
```

### Defining the API (types.go)

```go
// api/v1alpha1/trainingjob_types.go

package v1alpha1

import (
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// TrainingJobSpec defines the desired state of TrainingJob
type TrainingJobSpec struct {
    // Framework specifies the ML framework (pytorch, tensorflow)
    // +kubebuilder:validation:Enum=pytorch;tensorflow
    Framework string `json:"framework"`

    // Workers specifies the number of worker pods
    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:validation:Maximum=100
    Workers int32 `json:"workers"`

    // GPUPerWorker specifies GPUs per worker
    // +kubebuilder:validation:Minimum=0
    // +kubebuilder:validation:Maximum=8
    GPUPerWorker int32 `json:"gpuPerWorker,omitempty"`

    // Image specifies the container image
    Image string `json:"image"`

    // Command specifies the training command
    Command []string `json:"command"`

    // Args specifies command arguments
    Args []string `json:"args,omitempty"`

    // DataVolume specifies the data PVC
    DataVolume *corev1.PersistentVolumeClaimVolumeSource `json:"dataVolume,omitempty"`

    // CheckpointDir specifies checkpoint storage path
    CheckpointDir string `json:"checkpointDir,omitempty"`

    // Hyperparameters for the training job
    Hyperparameters map[string]string `json:"hyperparameters,omitempty"`

    // Resources specifies compute resources
    Resources corev1.ResourceRequirements `json:"resources,omitempty"`
}

// TrainingJobPhase represents the phase of training job
type TrainingJobPhase string

const (
    PhasePending   TrainingJobPhase = "Pending"
    PhaseRunning   TrainingJobPhase = "Running"
    PhaseSucceeded TrainingJobPhase = "Succeeded"
    PhaseFailed    TrainingJobPhase = "Failed"
)

// WorkerStatus represents status of a single worker
type WorkerStatus struct {
    WorkerID int32  `json:"workerId"`
    PodName  string `json:"podName"`
    Status   string `json:"status"`
}

// TrainingJobStatus defines the observed state of TrainingJob
type TrainingJobStatus struct {
    // Phase represents the current phase
    Phase TrainingJobPhase `json:"phase,omitempty"`

    // StartTime represents when training started
    StartTime *metav1.Time `json:"startTime,omitempty"`

    // CompletionTime represents when training completed
    CompletionTime *metav1.Time `json:"completionTime,omitempty"`

    // WorkerStatuses contains status of each worker
    WorkerStatuses []WorkerStatus `json:"workerStatuses,omitempty"`

    // Conditions represent the latest observations
    Conditions []metav1.Condition `json:"conditions,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:shortName=tj
// +kubebuilder:printcolumn:name="Framework",type=string,JSONPath=`.spec.framework`
// +kubebuilder:printcolumn:name="Workers",type=integer,JSONPath=`.spec.workers`
// +kubebuilder:printcolumn:name="Phase",type=string,JSONPath=`.status.phase`
// +kubebuilder:printcolumn:name="Age",type=date,JSONPath=`.metadata.creationTimestamp`

// TrainingJob is the Schema for the trainingjobs API
type TrainingJob struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   TrainingJobSpec   `json:"spec,omitempty"`
    Status TrainingJobStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// TrainingJobList contains a list of TrainingJob
type TrainingJobList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []TrainingJob `json:"items"`
}

func init() {
    SchemeBuilder.Register(&TrainingJob{}, &TrainingJobList{})
}
```

### Implementing the Controller

```go
// controllers/trainingjob_controller.go

package controllers

import (
    "context"
    "fmt"
    "time"

    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/types"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    mlv1alpha1 "github.com/example/training-job-operator/api/v1alpha1"
)

const (
    finalizerName = "trainingjob.ml.example.com/finalizer"
)

// TrainingJobReconciler reconciles a TrainingJob object
type TrainingJobReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs/finalizers,verbs=update
// +kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete

func (r *TrainingJobReconciler) Reconcile(
    ctx context.Context,
    req ctrl.Request,
) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the TrainingJob instance
    trainingJob := &mlv1alpha1.TrainingJob{}
    err := r.Get(ctx, req.NamespacedName, trainingJob)
    if err != nil {
        if errors.IsNotFound(err) {
            log.Info("TrainingJob resource not found. Ignoring since object must be deleted")
            return ctrl.Result{}, nil
        }
        log.Error(err, "Failed to get TrainingJob")
        return ctrl.Result{}, err
    }

    // TODO: Handle deletion with finalizer
    if !trainingJob.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, trainingJob)
    }

    // TODO: Add finalizer if not present
    if !containsString(trainingJob.Finalizers, finalizerName) {
        trainingJob.Finalizers = append(trainingJob.Finalizers, finalizerName)
        if err := r.Update(ctx, trainingJob); err != nil {
            return ctrl.Result{}, err
        }
    }

    // TODO: Reconcile worker pods
    if err := r.reconcileWorkers(ctx, trainingJob); err != nil {
        log.Error(err, "Failed to reconcile workers")
        return ctrl.Result{}, err
    }

    // TODO: Reconcile service for distributed training
    if err := r.reconcileService(ctx, trainingJob); err != nil {
        log.Error(err, "Failed to reconcile service")
        return ctrl.Result{}, err
    }

    // TODO: Update status
    if err := r.updateStatus(ctx, trainingJob); err != nil {
        log.Error(err, "Failed to update status")
        return ctrl.Result{}, err
    }

    // Requeue if training is still running
    if trainingJob.Status.Phase == mlv1alpha1.PhaseRunning {
        return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
    }

    return ctrl.Result{}, nil
}

func (r *TrainingJobReconciler) reconcileWorkers(
    ctx context.Context,
    trainingJob *mlv1alpha1.TrainingJob,
) error {
    // TODO: Implement worker pod reconciliation
    // 1. List existing worker pods
    // 2. Create missing pods
    // 3. Delete extra pods
    // 4. Update pods if spec changed

    return nil
}

func (r *TrainingJobReconciler) reconcileService(
    ctx context.Context,
    trainingJob *mlv1alpha1.TrainingJob,
) error {
    // TODO: Implement service reconciliation for distributed training
    // Create headless service for worker discovery

    return nil
}

func (r *TrainingJobReconciler) updateStatus(
    ctx context.Context,
    trainingJob *mlv1alpha1.TrainingJob,
) error {
    // TODO: Implement status update logic
    // 1. Check worker pod statuses
    // 2. Update phase based on worker states
    // 3. Update conditions
    // 4. Set start/completion times

    return nil
}

func (r *TrainingJobReconciler) handleDeletion(
    ctx context.Context,
    trainingJob *mlv1alpha1.TrainingJob,
) (ctrl.Result, error) {
    // TODO: Implement cleanup logic
    // 1. Clean up external resources (e.g., storage)
    // 2. Remove finalizer

    if containsString(trainingJob.Finalizers, finalizerName) {
        // Remove finalizer
        trainingJob.Finalizers = removeString(trainingJob.Finalizers, finalizerName)
        if err := r.Update(ctx, trainingJob); err != nil {
            return ctrl.Result{}, err
        }
    }

    return ctrl.Result{}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *TrainingJobReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&mlv1alpha1.TrainingJob{}).
        Owns(&corev1.Pod{}).
        Owns(&corev1.Service{}).
        Complete(r)
}

// Helper functions
func containsString(slice []string, s string) bool {
    for _, item := range slice {
        if item == s {
            return true
        }
    }
    return false
}

func removeString(slice []string, s string) []string {
    result := []string{}
    for _, item := range slice {
        if item != s {
            result = append(result, item)
        }
    }
    return result
}
```

### Building and Deploying

```bash
# Generate CRD manifests
make manifests

# Build and push operator image
make docker-build docker-push IMG=your-registry/training-job-operator:v0.1.0

# Deploy CRDs
make install

# Deploy operator
make deploy IMG=your-registry/training-job-operator:v0.1.0

# Test locally (without building image)
make run
```

## ML-Specific Operators {#ml-operators}

### KubeFlow Training Operator

The KubeFlow Training Operator provides Kubernetes CRDs for distributed ML training:

**Supported Frameworks:**
- TFJob (TensorFlow)
- PyTorchJob (PyTorch)
- MXNetJob (MXNet)
- XGBoostJob (XGBoost)

**Example PyTorchJob:**

```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: pytorch-dist-mnist
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:1.12.0-cuda11.3
            command:
            - python
            - /workspace/mnist.py
            resources:
              limits:
                nvidia.com/gpu: 1
    Worker:
      replicas: 3
      restartPolicy: OnFailure
      template:
        spec:
          containers:
          - name: pytorch
            image: pytorch/pytorch:1.12.0-cuda11.3
            command:
            - python
            - /workspace/mnist.py
            resources:
              limits:
                nvidia.com/gpu: 1
```

The operator handles:
- Setting up distributed environment variables (MASTER_ADDR, RANK, etc.)
- Creating services for communication
- Monitoring job completion
- Cleanup after completion

### Ray Operator

Ray is a distributed computing framework popular for ML workloads. The Ray Operator manages Ray clusters on Kubernetes.

```yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: ray-cluster
spec:
  rayVersion: '2.3.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.3.0
          resources:
            limits:
              cpu: "2"
              memory: "8Gi"
  workerGroupSpecs:
  - replicas: 3
    minReplicas: 1
    maxReplicas: 10
    groupName: worker-group
    rayStartParams: {}
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.3.0
          resources:
            limits:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
```

### Seldon Core Operator

For model serving:

```yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: iris-model
spec:
  predictors:
  - name: default
    replicas: 3
    graph:
      name: classifier
      implementation: SKLEARN_SERVER
      modelUri: gs://seldon-models/sklearn/iris
      resources:
        requests:
          memory: 1Gi
```

## Best Practices {#best-practices}

### 1. Design Principles

**Declarative API Design:**
- Users declare desired state (spec)
- Operator ensures current state matches desired state
- Status reflects observed state, never user input

**Separation of Concerns:**
- Spec: What the user wants
- Status: What the operator observes
- Don't mix them

**API Versioning:**
- Start with v1alpha1 for experimental APIs
- Move to v1beta1 when API is stable
- Promote to v1 for production
- Support multiple versions during transitions

### 2. Error Handling

```go
func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // Transient errors: Return error, will retry with exponential backoff
    if err := r.someOperation(); err != nil {
        return ctrl.Result{}, err
    }

    // Explicit requeue after interval
    if needsRecheck {
        return ctrl.Result{RequeueAfter: 5 * time.Minute}, nil
    }

    // Success, don't requeue
    return ctrl.Result{}, nil
}
```

**Error Types:**
- **Transient errors:** Network issues, temporary unavailability - Return error for retry
- **Permanent errors:** Invalid configuration - Update status, don't retry
- **External dependencies:** Requeue after delay

### 3. Status Updates

Always update status separately from spec:

```go
// Update spec
if err := r.Update(ctx, obj); err != nil {
    return ctrl.Result{}, err
}

// Update status (separate API call)
if err := r.Status().Update(ctx, obj); err != nil {
    return ctrl.Result{}, err
}
```

Use conditions for detailed status:

```go
import metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

func setCondition(obj *MyResource, condType string, status metav1.ConditionStatus, reason, message string) {
    condition := metav1.Condition{
        Type:               condType,
        Status:             status,
        ObservedGeneration: obj.Generation,
        LastTransitionTime: metav1.Now(),
        Reason:             reason,
        Message:            message,
    }

    // TODO: Add or update condition in obj.Status.Conditions
}
```

### 4. Finalizers

Use finalizers for cleanup:

```go
const finalizerName = "myresource.example.com/finalizer"

if !obj.DeletionTimestamp.IsZero() {
    // Resource is being deleted
    if containsString(obj.Finalizers, finalizerName) {
        // Perform cleanup
        if err := r.cleanup(ctx, obj); err != nil {
            return ctrl.Result{}, err
        }

        // Remove finalizer
        obj.Finalizers = removeString(obj.Finalizers, finalizerName)
        if err := r.Update(ctx, obj); err != nil {
            return ctrl.Result{}, err
        }
    }
    return ctrl.Result{}, nil
}

// Add finalizer if not present
if !containsString(obj.Finalizers, finalizerName) {
    obj.Finalizers = append(obj.Finalizers, finalizerName)
    if err := r.Update(ctx, obj); err != nil {
        return ctrl.Result{}, err
    }
}
```

### 5. Testing

**Unit Tests:**

```go
func TestReconcile(t *testing.T) {
    // Create fake client
    scheme := runtime.NewScheme()
    _ = mlv1alpha1.AddToScheme(scheme)
    _ = corev1.AddToScheme(scheme)

    trainingJob := &mlv1alpha1.TrainingJob{
        ObjectMeta: metav1.ObjectMeta{
            Name:      "test-job",
            Namespace: "default",
        },
        Spec: mlv1alpha1.TrainingJobSpec{
            Framework: "pytorch",
            Workers:   2,
        },
    }

    client := fake.NewClientBuilder().
        WithScheme(scheme).
        WithObjects(trainingJob).
        Build()

    reconciler := &TrainingJobReconciler{
        Client: client,
        Scheme: scheme,
    }

    // Test reconciliation
    req := ctrl.Request{
        NamespacedName: types.NamespacedName{
            Name:      "test-job",
            Namespace: "default",
        },
    }

    result, err := reconciler.Reconcile(context.TODO(), req)
    if err != nil {
        t.Fatalf("Reconcile failed: %v", err)
    }

    // TODO: Add assertions
}
```

**Integration Tests:**
Use envtest to run tests against real API server:

```go
import "sigs.k8s.io/controller-runtime/pkg/envtest"

var testEnv *envtest.Environment

func TestMain(m *testing.M) {
    testEnv = &envtest.Environment{
        CRDDirectoryPaths: []string{"../config/crd/bases"},
    }

    cfg, err := testEnv.Start()
    if err != nil {
        panic(err)
    }

    code := m.Run()

    testEnv.Stop()
    os.Exit(code)
}
```

### 6. Observability

Add metrics:

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "sigs.k8s.io/controller-runtime/pkg/metrics"
)

var (
    jobsCreated = prometheus.NewCounter(
        prometheus.CounterOpts{
            Name: "training_jobs_created_total",
            Help: "Total number of training jobs created",
        },
    )

    jobDuration = prometheus.NewHistogram(
        prometheus.HistogramOpts{
            Name: "training_job_duration_seconds",
            Help: "Training job duration in seconds",
        },
    )
)

func init() {
    metrics.Registry.MustRegister(jobsCreated, jobDuration)
}
```

Add events:

```go
import (
    "k8s.io/client-go/tools/record"
)

type Reconciler struct {
    client.Client
    Scheme   *runtime.Scheme
    Recorder record.EventRecorder
}

func (r *Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // ...

    r.Recorder.Event(
        trainingJob,
        corev1.EventTypeNormal,
        "WorkersCreated",
        fmt.Sprintf("Created %d worker pods", trainingJob.Spec.Workers),
    )

    // ...
}
```

## Real-World Examples {#examples}

### Example 1: Netflix's Control Plane

Netflix uses operators extensively for their ML platform:
- Custom operators for Jupyter notebooks
- Model training orchestration
- A/B testing infrastructure
- Auto-scaling based on queue depth

### Example 2: Uber's Michelangelo

Uber's ML platform uses Kubernetes operators for:
- Training job management
- Model deployment
- Feature store operations
- Resource allocation

### Example 3: Spotify's ML Platform

Spotify's operators handle:
- Podcast recommendation training
- Music recommendation serving
- Real-time feature computation
- Multi-region deployments

## Summary

Key takeaways:

1. **Operators encode operational knowledge** as software that automates complex application management
2. **CRDs extend Kubernetes API** with domain-specific resources
3. **Reconciliation loops** continuously drive system toward desired state
4. **Idempotency is critical** - same input produces same output, safely repeatable
5. **Status vs Spec separation** - declarative desired state vs observed state
6. **Finalizers enable cleanup** before resource deletion
7. **Testing and observability** are essential for production operators
8. **ML-specific operators** (KubeFlow, Ray) provide battle-tested patterns

## Further Reading

- [Kubernetes Operator Pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [Operator SDK Documentation](https://sdk.operatorframework.io/)
- [Kubebuilder Book](https://book.kubebuilder.io/)
- [Controller Runtime](https://github.com/kubernetes-sigs/controller-runtime)
- [KubeFlow Training Operator](https://github.com/kubeflow/training-operator)

## Next Steps

In the next lecture, we'll dive into **Advanced Scheduling** and learn how to optimize resource allocation for ML workloads, including GPU scheduling, gang scheduling, and priority-based preemption.
