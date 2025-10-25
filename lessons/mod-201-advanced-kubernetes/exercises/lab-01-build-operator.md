# Lab 01: Build a Custom Kubernetes Operator for ML Training Jobs

## Objectives

By the end of this lab, you will:
1. Set up an operator development environment
2. Design a CRD for ML training jobs
3. Implement controller logic using operator-sdk
4. Add reconciliation logic for job lifecycle management
5. Deploy and test the operator
6. Add status updates and event handling

## Prerequisites

- Go 1.19+ installed
- Docker or Podman installed
- Access to a Kubernetes cluster (1.25+)
- kubectl configured
- operator-sdk installed
- Basic understanding of Go programming
- Completion of Lecture 01: Operators and CRDs

## Estimated Time

8 hours

## Lab Environment Setup

### Step 1: Install Required Tools

```bash
# Install operator-sdk (if not already installed)
# macOS
brew install operator-sdk

# Linux
export ARCH=$(case $(uname -m) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(uname -m) ;; esac)
export OS=$(uname | awk '{print tolower($0)}')
export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/v1.31.0
curl -LO ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH}
chmod +x operator-sdk_${OS}_${ARCH}
sudo mv operator-sdk_${OS}_${ARCH} /usr/local/bin/operator-sdk

# Verify installation
operator-sdk version
go version
kubectl version --client
docker version
```

### Step 2: Verify Cluster Access

```bash
# Check cluster access
kubectl cluster-info
kubectl get nodes

# Create namespace for operator development
kubectl create namespace ml-operator-system
kubectl create namespace ml-jobs
```

## Part 1: Project Setup (30 minutes)

### Create Operator Project

```bash
# Create project directory
mkdir -p ~/ml-training-operator
cd ~/ml-training-operator

# Initialize operator project
operator-sdk init \
  --domain ml.example.com \
  --repo github.com/yourusername/ml-training-operator \
  --plugins go/v4-alpha

# Create API and Controller
operator-sdk create api \
  --group ml \
  --version v1alpha1 \
  --kind TrainingJob \
  --resource \
  --controller

# Project structure created:
# .
# ├── api/
# │   └── v1alpha1/
# │       ├── trainingjob_types.go
# │       └── zz_generated.deepcopy.go
# ├── config/
# │   ├── crd/
# │   ├── manager/
# │   ├── rbac/
# │   └── samples/
# ├── controllers/
# │   └── trainingjob_controller.go
# ├── Dockerfile
# ├── Makefile
# └── go.mod
```

## Part 2: Define the TrainingJob CRD (1 hour)

### Edit `api/v1alpha1/trainingjob_types.go`

```go
package v1alpha1

import (
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// EDIT THIS FILE! Add your custom resource definition fields here.

// TrainingJobSpec defines the desired state of TrainingJob
type TrainingJobSpec struct {
	// Framework specifies the ML framework (pytorch, tensorflow, xgboost)
	// +kubebuilder:validation:Enum=pytorch;tensorflow;xgboost
	// +kubebuilder:validation:Required
	Framework string `json:"framework"`

	// Image specifies the container image for training
	// +kubebuilder:validation:Required
	Image string `json:"image"`

	// Command is the training command
	// +kubebuilder:validation:Required
	// +kubebuilder:validation:MinItems=1
	Command []string `json:"command"`

	// Args are arguments for the command
	// +optional
	Args []string `json:"args,omitempty"`

	// Workers specifies the number of worker pods
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:validation:Maximum=100
	// +kubebuilder:default=1
	Workers int32 `json:"workers"`

	// GPUPerWorker specifies GPUs per worker
	// +kubebuilder:validation:Minimum=0
	// +kubebuilder:validation:Maximum=8
	// +kubebuilder:default=0
	GPUPerWorker int32 `json:"gpuPerWorker,omitempty"`

	// Resources specifies compute resources
	// +optional
	Resources corev1.ResourceRequirements `json:"resources,omitempty"`

	// DataVolume specifies the PVC for training data
	// +optional
	DataVolume *corev1.PersistentVolumeClaimVolumeSource `json:"dataVolume,omitempty"`

	// CheckpointDir specifies where to save checkpoints
	// +optional
	CheckpointDir string `json:"checkpointDir,omitempty"`

	// CheckpointInterval specifies how often to checkpoint (in epochs)
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:default=1
	// +optional
	CheckpointInterval int32 `json:"checkpointInterval,omitempty"`

	// Hyperparameters for the training job
	// +optional
	Hyperparameters map[string]string `json:"hyperparameters,omitempty"`

	// RestartPolicy for worker pods (OnFailure, Never)
	// +kubebuilder:validation:Enum=OnFailure;Never
	// +kubebuilder:default=OnFailure
	// +optional
	RestartPolicy corev1.RestartPolicy `json:"restartPolicy,omitempty"`
}

// TrainingJobPhase represents the phase of training job
// +kubebuilder:validation:Enum=Pending;Running;Succeeded;Failed
type TrainingJobPhase string

const (
	// TrainingJobPhasePending means the job is waiting to start
	TrainingJobPhasePending TrainingJobPhase = "Pending"
	// TrainingJobPhaseRunning means the job is running
	TrainingJobPhaseRunning TrainingJobPhase = "Running"
	// TrainingJobPhaseSucceeded means the job completed successfully
	TrainingJobPhaseSucceeded TrainingJobPhase = "Succeeded"
	// TrainingJobPhaseFailed means the job failed
	TrainingJobPhaseFailed TrainingJobPhase = "Failed"
)

// WorkerStatus represents status of a single worker
type WorkerStatus struct {
	// WorkerID is the worker index
	WorkerID int32 `json:"workerId"`

	// PodName is the name of the worker pod
	PodName string `json:"podName"`

	// Phase is the current phase of the worker
	Phase corev1.PodPhase `json:"phase"`

	// RestartCount is the number of times the worker has restarted
	RestartCount int32 `json:"restartCount"`
}

// TrainingJobStatus defines the observed state of TrainingJob
type TrainingJobStatus struct {
	// Phase represents the current phase
	// +optional
	Phase TrainingJobPhase `json:"phase,omitempty"`

	// StartTime represents when training started
	// +optional
	StartTime *metav1.Time `json:"startTime,omitempty"`

	// CompletionTime represents when training completed
	// +optional
	CompletionTime *metav1.Time `json:"completionTime,omitempty"`

	// WorkerStatuses contains status of each worker
	// +optional
	WorkerStatuses []WorkerStatus `json:"workerStatuses,omitempty"`

	// Conditions represent the latest observations
	// +optional
	// +patchMergeKey=type
	// +patchStrategy=merge
	// +listType=map
	// +listMapKey=type
	Conditions []metav1.Condition `json:"conditions,omitempty" patchStrategy:"merge" patchMergeKey:"type"`

	// ObservedGeneration is the generation observed by the controller
	// +optional
	ObservedGeneration int64 `json:"observedGeneration,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:shortName=tj;trainingjob
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

### Generate CRD Manifests

```bash
# Generate CRD manifests and deepcopy methods
make generate
make manifests

# Review generated CRD
cat config/crd/bases/ml.example.com_trainingjobs.yaml
```

## Part 3: Implement Controller Logic (3 hours)

### Edit `controllers/trainingjob_controller.go`

This is the main controller implementation. You need to complete the TODO sections:

```go
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
	"k8s.io/client-go/tools/record"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"

	mlv1alpha1 "github.com/yourusername/ml-training-operator/api/v1alpha1"
)

const (
	finalizerName = "trainingjob.ml.example.com/finalizer"
	workerLabel   = "trainingjob.ml.example.com/worker"
)

// TrainingJobReconciler reconciles a TrainingJob object
type TrainingJobReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=ml.example.com,resources=trainingjobs/finalizers,verbs=update
// +kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=services,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups="",resources=events,verbs=create;patch

func (r *TrainingJobReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
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

	// TODO: Implement deletion handling with finalizer
	if !trainingJob.DeletionTimestamp.IsZero() {
		return r.handleDeletion(ctx, trainingJob)
	}

	// TODO: Add finalizer if not present
	if !controllerutil.ContainsFinalizer(trainingJob, finalizerName) {
		controllerutil.AddFinalizer(trainingJob, finalizerName)
		if err := r.Update(ctx, trainingJob); err != nil {
			return ctrl.Result{}, err
		}
	}

	// TODO: Reconcile worker pods
	if err := r.reconcileWorkers(ctx, trainingJob); err != nil {
		log.Error(err, "Failed to reconcile workers")
		r.Recorder.Event(trainingJob, corev1.EventTypeWarning, "ReconcileFailed", err.Error())
		return ctrl.Result{}, err
	}

	// TODO: Reconcile service for distributed training
	if trainingJob.Spec.Workers > 1 {
		if err := r.reconcileService(ctx, trainingJob); err != nil {
			log.Error(err, "Failed to reconcile service")
			return ctrl.Result{}, err
		}
	}

	// TODO: Update status
	if err := r.updateStatus(ctx, trainingJob); err != nil {
		log.Error(err, "Failed to update status")
		return ctrl.Result{}, err
	}

	// Requeue if training is still running
	if trainingJob.Status.Phase == mlv1alpha1.TrainingJobPhaseRunning {
		return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
	}

	return ctrl.Result{}, nil
}

// TODO: Implement this function to reconcile worker pods
func (r *TrainingJobReconciler) reconcileWorkers(ctx context.Context, trainingJob *mlv1alpha1.TrainingJob) error {
	log := log.FromContext(ctx)

	// 1. List existing worker pods
	// 2. Create missing pods
	// 3. Delete extra pods (if workers scaled down)
	// 4. Update pods if spec changed

	log.Info("Reconciling workers", "workers", trainingJob.Spec.Workers)

	// TODO: Implement worker pod reconciliation logic
	// Hint: Use r.constructWorkerPod() to create pod specs
	// Hint: Set owner reference with ctrl.SetControllerReference()

	return nil
}

// TODO: Implement this function to construct a worker pod
func (r *TrainingJobReconciler) constructWorkerPod(trainingJob *mlv1alpha1.TrainingJob, workerID int32) *corev1.Pod {
	// TODO: Build pod specification
	// Include:
	// - Container with training image
	// - Environment variables for distributed training (RANK, WORLD_SIZE, MASTER_ADDR)
	// - Volume mounts for data and checkpoints
	// - Resource requests/limits
	// - GPU resources if specified

	return nil
}

// TODO: Implement this function to reconcile service for distributed training
func (r *TrainingJobReconciler) reconcileService(ctx context.Context, trainingJob *mlv1alpha1.TrainingJob) error {
	// TODO: Create headless service for worker discovery
	// Service should select all worker pods of this training job

	return nil
}

// TODO: Implement this function to update TrainingJob status
func (r *TrainingJobReconciler) updateStatus(ctx context.Context, trainingJob *mlv1alpha1.TrainingJob) error {
	log := log.FromContext(ctx)

	// TODO: Implement status update logic
	// 1. List worker pods
	// 2. Count pod states (pending, running, succeeded, failed)
	// 3. Update WorkerStatuses
	// 4. Determine overall Phase
	// 5. Set StartTime if just started
	// 6. Set CompletionTime if finished
	// 7. Update Conditions

	log.Info("Updating status", "currentPhase", trainingJob.Status.Phase)

	return nil
}

// TODO: Implement this function to handle deletion
func (r *TrainingJobReconciler) handleDeletion(ctx context.Context, trainingJob *mlv1alpha1.TrainingJob) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	if controllerutil.ContainsFinalizer(trainingJob, finalizerName) {
		// TODO: Perform cleanup (e.g., delete external resources)
		log.Info("Cleaning up training job resources")

		// Remove finalizer
		controllerutil.RemoveFinalizer(trainingJob, finalizerName)
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
```

## Part 4: Deploy and Test (2 hours)

### Build and Deploy

```bash
# Install CRDs
make install

# Run operator locally (for testing)
make run

# In another terminal, create a sample TrainingJob
kubectl apply -f config/samples/ml_v1alpha1_trainingjob.yaml

# Watch the operator logs and see reconciliation
# Watch pods being created
kubectl get pods -n ml-jobs -w
```

### Create Sample TrainingJob

Edit `config/samples/ml_v1alpha1_trainingjob.yaml`:

```yaml
apiVersion: ml.example.com/v1alpha1
kind: TrainingJob
metadata:
  name: pytorch-mnist
  namespace: ml-jobs
spec:
  framework: pytorch
  image: pytorch/pytorch:1.12.0-cuda11.3
  command:
  - python
  - -m
  - torch.distributed.run
  - --nproc_per_node=1
  - /workspace/train_mnist.py
  args:
  - --epochs=10
  - --batch-size=64
  workers: 2
  gpuPerWorker: 0  # Use 0 for CPU-only testing
  resources:
    requests:
      cpu: "2"
      memory: 4Gi
    limits:
      cpu: "2"
      memory: 4Gi
  hyperparameters:
    learningRate: "0.001"
    optimizer: "adam"
```

### Test the Operator

```bash
# Create training job
kubectl apply -f config/samples/ml_v1alpha1_trainingjob.yaml

# Check status
kubectl get trainingjobs -n ml-jobs
kubectl describe trainingjob pytorch-mnist -n ml-jobs

# Check worker pods
kubectl get pods -n ml-jobs -l trainingjob.ml.example.com/worker

# View logs
kubectl logs -n ml-jobs -l trainingjob.ml.example.com/worker

# Update training job (e.g., change workers)
kubectl patch trainingjob pytorch-mnist -n ml-jobs \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/workers", "value": 4}]'

# Delete training job
kubectl delete trainingjob pytorch-mnist -n ml-jobs

# Verify cleanup
kubectl get pods -n ml-jobs
```

## Part 5: Add Advanced Features (2 hours)

### Add Status Conditions

```go
// Helper function to set conditions
func setCondition(trainingJob *mlv1alpha1.TrainingJob, condType string, status metav1.ConditionStatus, reason, message string) {
	condition := metav1.Condition{
		Type:               condType,
		Status:             status,
		ObservedGeneration: trainingJob.Generation,
		LastTransitionTime: metav1.Now(),
		Reason:             reason,
		Message:            message,
	}

	// Find existing condition
	for i, existing := range trainingJob.Status.Conditions {
		if existing.Type == condType {
			if existing.Status != status || existing.Reason != reason || existing.Message != message {
				trainingJob.Status.Conditions[i] = condition
			}
			return
		}
	}

	// Add new condition
	trainingJob.Status.Conditions = append(trainingJob.Status.Conditions, condition)
}
```

### Add Event Recording

```go
// In reconcileWorkers function
r.Recorder.Event(trainingJob, corev1.EventTypeNormal, "WorkersCreated",
	fmt.Sprintf("Created %d worker pods", trainingJob.Spec.Workers))

// When training completes
r.Recorder.Event(trainingJob, corev1.EventTypeNormal, "TrainingCompleted",
	"Training job completed successfully")

// When errors occur
r.Recorder.Event(trainingJob, corev1.EventTypeWarning, "WorkerFailed",
	fmt.Sprintf("Worker %d failed", workerID))
```

## Deliverables

1. **Working operator** that manages TrainingJob resources
2. **CRD definition** with validation and printer columns
3. **Controller implementation** with reconciliation logic
4. **Test results** showing:
   - TrainingJob creation
   - Worker pod creation
   - Status updates
   - Cleanup on deletion
5. **Documentation** of:
   - How to build and deploy
   - How to use the operator
   - Known limitations

## Bonus Challenges

1. **Add support for parameter servers** (for TensorFlow)
2. **Implement checkpoint management** (save/restore)
3. **Add metrics** (Prometheus metrics for training jobs)
4. **Implement gang scheduling** integration with Volcano
5. **Add validation webhooks** for TrainingJob spec
6. **Support for different ML frameworks** (TensorFlow, XGBoost)

## Troubleshooting

### Operator not reconciling

```bash
# Check operator logs
kubectl logs -n ml-operator-system -l control-plane=controller-manager

# Check RBAC permissions
kubectl auth can-i create pods --as=system:serviceaccount:ml-operator-system:ml-training-operator-controller-manager
```

### CRD validation errors

```bash
# Describe the CRD
kubectl describe crd trainingjobs.ml.example.com

# Validate sample manifest
kubectl apply --dry-run=server -f config/samples/ml_v1alpha1_trainingjob.yaml
```

### Pods not being created

```bash
# Check reconciliation events
kubectl get events -n ml-jobs

# Describe TrainingJob
kubectl describe trainingjob pytorch-mnist -n ml-jobs

# Check controller logs
kubectl logs -n ml-operator-system -l control-plane=controller-manager --tail=100
```

## Success Criteria

- [ ] Operator successfully creates worker pods
- [ ] Status is accurately updated
- [ ] Cleanup works properly
- [ ] Events are recorded
- [ ] Multiple training jobs can run concurrently
- [ ] Scaling workers up/down works
- [ ] Code follows Go best practices

## Additional Resources

- [Operator SDK Tutorial](https://sdk.operatorframework.io/docs/building-operators/golang/tutorial/)
- [Kubebuilder Book](https://book.kubebuilder.io/)
- [Controller Runtime](https://github.com/kubernetes-sigs/controller-runtime)
- [Sample Operators](https://github.com/operator-framework/operator-sdk/tree/master/testdata)

## Submission

Document your implementation with:
1. Code repository (GitHub link)
2. Demo video or screenshots
3. README with instructions
4. Lessons learned
5. Future improvements

---

**Good luck! Building operators is challenging but rewarding. Don't hesitate to ask for help in the course forum.**
