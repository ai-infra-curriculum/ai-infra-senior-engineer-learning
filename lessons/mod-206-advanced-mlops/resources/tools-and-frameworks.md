# Module 206: Advanced MLOps - Tools and Frameworks

## Experiment Tracking

### MLflow
**Purpose**: End-to-end ML lifecycle management
**Features**:
- Experiment tracking
- Model registry
- Model deployment
- Projects and models

**Pros**:
- Open source, self-hosted
- Language agnostic
- Flexible deployment options

**Cons**:
- Basic UI
- Limited collaboration features

**Getting Started**:
```bash
pip install mlflow
mlflow ui
```

**Best For**: Teams wanting full control, on-premise deployments

---

### Weights & Biases (W&B)
**Purpose**: Experiment tracking and collaboration
**Features**:
- Rich visualizations
- Hyperparameter tuning
- Model versioning
- Team collaboration

**Pros**:
- Beautiful UI
- Real-time monitoring
- Strong community

**Cons**:
- Cloud-based (privacy concerns)
- Pricing for teams

**Getting Started**:
```bash
pip install wandb
wandb login
```

**Best For**: Research teams, deep learning projects

---

### Neptune.ai
**Purpose**: Enterprise ML metadata store
**Features**:
- Experiment comparison
- Model registry
- Team collaboration
- Compliance tracking

**Pros**:
- Enterprise features
- Good UI
- Strong versioning

**Cons**:
- Commercial product
- Can be expensive

**Best For**: Enterprise teams, regulated industries

---

### TensorBoard
**Purpose**: TensorFlow visualization toolkit
**Features**:
- Training metrics visualization
- Model graph visualization
- Embedding projector

**Pros**:
- Free, open source
- Deep TensorFlow integration

**Cons**:
- Limited to TensorFlow/PyTorch
- No model registry

**Best For**: Deep learning experimentation

---

## Feature Stores

### Feast
**Purpose**: Open source feature store
**Features**:
- Online/offline feature serving
- Point-in-time correctness
- Feature versioning
- Multi-cloud support

**Pros**:
- Open source
- Flexible backends
- Active community

**Cons**:
- Setup complexity
- Limited UI

**Getting Started**:
```bash
pip install feast
feast init my_project
```

**Best For**: Teams building custom ML platforms

---

### Tecton
**Purpose**: Enterprise feature platform
**Features**:
- Real-time features
- Feature engineering
- Monitoring and alerts
- Data quality checks

**Pros**:
- Fully managed
- Strong real-time support
- Good UI

**Cons**:
- Expensive
- Vendor lock-in

**Best For**: Large enterprises, real-time ML

---

### AWS SageMaker Feature Store
**Purpose**: AWS-native feature store
**Features**:
- Online/offline stores
- Integration with SageMaker
- Data lineage

**Pros**:
- AWS integration
- Managed service

**Cons**:
- AWS lock-in
- Limited flexibility

**Best For**: AWS-heavy organizations

---

### Hopsworks Feature Store
**Purpose**: Open source feature store with UI
**Features**:
- Feature engineering
- Feature monitoring
- Data validation
- Collaboration tools

**Pros**:
- Good UI
- Open source core
- Feature monitoring

**Cons**:
- Smaller community

**Best For**: Teams wanting OSS with UI

---

## Model Serving

### TensorFlow Serving
**Purpose**: Production TensorFlow model serving
**Features**:
- High-performance serving
- Model versioning
- Batching support
- gRPC and REST APIs

**Pros**:
- Optimized for TensorFlow
- Battle-tested at scale

**Cons**:
- TensorFlow-specific
- Limited flexibility

**Getting Started**:
```bash
docker run -p 8501:8501 \
  --mount type=bind,source=/models/my_model,target=/models/my_model \
  -e MODEL_NAME=my_model -t tensorflow/serving
```

**Best For**: TensorFlow models at scale

---

### TorchServe
**Purpose**: PyTorch model serving
**Features**:
- Model versioning
- A/B testing
- Monitoring
- Multi-model serving

**Pros**:
- PyTorch-native
- Good documentation

**Cons**:
- PyTorch-specific

**Getting Started**:
```bash
pip install torchserve torch-model-archiver
torchserve --start --model-store model_store
```

**Best For**: PyTorch models

---

### Seldon Core
**Purpose**: ML deployment on Kubernetes
**Features**:
- Multi-framework support
- Advanced deployments (canary, shadow)
- Explainability integration
- Drift detection

**Pros**:
- Framework agnostic
- Kubernetes-native
- Rich features

**Cons**:
- Kubernetes required
- Complex setup

**Best For**: Kubernetes-based ML platforms

---

### KServe (formerly KFServing)
**Purpose**: Serverless ML serving on Kubernetes
**Features**:
- Auto-scaling
- Canary rollouts
- Transformer pipelines
- Multi-framework

**Pros**:
- Serverless architecture
- Good abstractions

**Cons**:
- Requires Istio/Knative

**Best For**: Serverless ML on Kubernetes

---

### BentoML
**Purpose**: ML model serving framework
**Features**:
- Model packaging
- API generation
- Multi-model serving
- Easy deployment

**Pros**:
- Simple to use
- Good abstractions
- Multiple deployment targets

**Cons**:
- Smaller ecosystem

**Best For**: Fast prototyping to production

---

## Workflow Orchestration

### Apache Airflow
**Purpose**: Workflow orchestration
**Features**:
- DAG-based workflows
- Extensive operators
- Monitoring and alerting
- Distributed execution

**Pros**:
- Mature, widely adopted
- Rich ecosystem
- Good UI

**Cons**:
- Complex setup
- Not ML-specific

**Best For**: Complex data/ML pipelines

---

### Kubeflow Pipelines
**Purpose**: ML workflows on Kubernetes
**Features**:
- ML pipeline definition
- Experiment tracking
- Component reuse
- Kubernetes-native

**Pros**:
- ML-focused
- Kubernetes integration

**Cons**:
- Steep learning curve
- Kubernetes required

**Best For**: Kubernetes-based ML platforms

---

### Prefect
**Purpose**: Modern workflow orchestration
**Features**:
- Pythonic API
- Dynamic workflows
- Cloud or self-hosted
- Strong error handling

**Pros**:
- Easy to use
- Modern design
- Good debugging

**Cons**:
- Newer tool
- Smaller community

**Best For**: Python-first teams

---

### Metaflow
**Purpose**: Netflix's ML workflow framework
**Features**:
- Version everything
- Easy scaling
- Notebook-friendly
- Production-ready

**Pros**:
- Simple API
- Battle-tested at Netflix
- Great DX

**Cons**:
- Opinionated

**Best For**: Python ML workflows

---

## Hyperparameter Optimization

### Optuna
**Purpose**: Hyperparameter optimization framework
**Features**:
- Bayesian optimization
- Pruning algorithms
- Distributed optimization
- Framework integration

**Pros**:
- Easy to use
- Efficient algorithms
- Good visualization

**Cons**:
- None significant

**Getting Started**:
```python
import optuna

def objective(trial):
    x = trial.suggest_float('x', -10, 10)
    return (x - 2) ** 2

study = optuna.create_study()
study.optimize(objective, n_trials=100)
```

**Best For**: All ML projects

---

### Ray Tune
**Purpose**: Scalable hyperparameter tuning
**Features**:
- Distributed tuning
- Multiple algorithms
- Early stopping
- ML framework integration

**Pros**:
- Highly scalable
- Part of Ray ecosystem

**Cons**:
- Learning curve

**Best For**: Large-scale tuning

---

### Weights & Biases Sweeps
**Purpose**: Hyperparameter optimization with W&B
**Features**:
- Bayesian optimization
- Grid/random search
- Parallelization
- Visualization

**Pros**:
- Integrated with W&B
- Good UI

**Cons**:
- Requires W&B

**Best For**: W&B users

---

## Monitoring & Observability

### Prometheus + Grafana
**Purpose**: Metrics and visualization
**Features**:
- Time-series metrics
- Alerting
- Rich visualizations
- Service discovery

**Pros**:
- Industry standard
- Powerful querying
- Large ecosystem

**Cons**:
- Setup complexity

**Best For**: Kubernetes deployments

---

### Evidently AI
**Purpose**: ML monitoring and testing
**Features**:
- Data drift detection
- Model quality monitoring
- Test suites
- Interactive reports

**Pros**:
- ML-specific
- Easy to use
- Great visualizations

**Cons**:
- Newer tool

**Getting Started**:
```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref_data, current_data=curr_data)
report.save_html('report.html')
```

**Best For**: ML model monitoring

---

### Fiddler AI
**Purpose**: Enterprise ML monitoring
**Features**:
- Model monitoring
- Explainability
- Bias detection
- Compliance

**Pros**:
- Enterprise features
- Good UI

**Cons**:
- Commercial product

**Best For**: Enterprise ML monitoring

---

## Testing & Validation

### Great Expectations
**Purpose**: Data validation framework
**Features**:
- Data quality tests
- Data documentation
- Profiling
- Integration with pipelines

**Pros**:
- Comprehensive
- Good documentation
- Active community

**Cons**:
- Verbose syntax

**Getting Started**:
```python
import great_expectations as gx

context = gx.get_context()
validator = context.sources.pandas_default.read_csv("data.csv")
validator.expect_column_values_to_not_be_null("user_id")
```

**Best For**: Data quality in ML pipelines

---

### Deepchecks
**Purpose**: ML validation framework
**Features**:
- Data validation
- Model validation
- Production monitoring
- Test suites

**Pros**:
- ML-focused
- Easy to use
- Good visualizations

**Cons**:
- Newer tool

**Best For**: ML model validation

---

## Data Versioning

### DVC (Data Version Control)
**Purpose**: Version control for data and models
**Features**:
- Git-based workflow
- Remote storage (S3, GCS, etc.)
- Pipeline tracking
- Experiment management

**Pros**:
- Git-like interface
- Open source
- Storage flexibility

**Cons**:
- Learning curve

**Getting Started**:
```bash
pip install dvc
dvc init
dvc add data/training_data.csv
git add data/training_data.csv.dvc
dvc push
```

**Best For**: Version control for data

---

### LakeFS
**Purpose**: Git for data lakes
**Features**:
- Branch, commit, merge for data
- Data versioning
- Time travel
- Reproducibility

**Pros**:
- Git-like workflow
- Scalable
- Integration with data tools

**Cons**:
- Infrastructure overhead

**Best For**: Data lake management

---

## AutoML

### H2O AutoML
**Purpose**: Automated machine learning
**Features**:
- Automated model selection
- Hyperparameter tuning
- Ensemble methods
- Interpretability

**Pros**:
- Open source
- Fast
- Good results

**Cons**:
- Limited deep learning

**Best For**: Tabular data AutoML

---

### Auto-sklearn
**Purpose**: Automated sklearn pipeline building
**Features**:
- Algorithm selection
- Hyperparameter optimization
- Ensemble construction
- Meta-learning

**Pros**:
- Built on sklearn
- Research-backed

**Cons**:
- CPU-intensive

**Best For**: Scikit-learn users

---

## Summary Matrix

| Category | Open Source | Commercial | Best For |
|----------|-------------|------------|----------|
| Experiment Tracking | MLflow | W&B, Neptune | MLflow for control, W&B for UX |
| Feature Store | Feast | Tecton, AWS | Feast for flexibility |
| Model Serving | Seldon, KServe | - | KServe for K8s |
| Orchestration | Airflow, Prefect | - | Airflow for maturity |
| HPO | Optuna, Ray Tune | - | Optuna for ease |
| Monitoring | Prometheus | Fiddler | Evidently for ML-specific |
| Data Versioning | DVC | - | DVC |
| AutoML | H2O, Auto-sklearn | - | H2O for speed |

## Tool Selection Guide

**For Startups/Small Teams**:
- MLflow, Feast, Seldon Core, Airflow, Optuna, Evidently

**For Enterprises**:
- Neptune, Tecton, KServe, Airflow, Ray Tune, Fiddler

**For AWS-Heavy**:
- SageMaker ecosystem

**For Kubernetes-Native**:
- KServe, Kubeflow, Seldon Core

**For Research Teams**:
- Weights & Biases, Ray Tune
