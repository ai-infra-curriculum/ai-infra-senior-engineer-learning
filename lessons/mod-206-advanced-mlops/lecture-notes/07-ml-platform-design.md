# Lecture 07: ML Platform Design

## Learning Objectives

By the end of this lecture, you will be able to:

- Design end-to-end ML platforms providing self-service capabilities for data scientists including training orchestration, model deployment, monitoring, and feature stores
- Architect platform abstraction layers with consistent APIs (Python SDK, REST API, CLI) hiding infrastructure complexity while maintaining flexibility
- Implement multi-tenancy strategies with resource quotas, namespace isolation, cost allocation, and access control enabling safe team collaboration
- Design platform services including experiment tracking (MLflow), model registry, feature store (Feast), training orchestration (Kubeflow), and deployment service
- Configure resource management and autoscaling using Kubernetes node pools, GPU scheduling, spot instance integration, and workload prioritization
- Build platform observability with centralized logging, metrics dashboards, distributed tracing, and alerting for platform health monitoring
- Implement governance and compliance controls including model approval workflows, audit trails, data lineage, and policy enforcement (PII handling, bias detection)
- Architect platform scalability patterns supporting 100s of data scientists, 1000s of models, and diverse workload types (training, batch inference, real-time serving)

## Overview

An ML platform provides the infrastructure, tools, and workflows that enable data scientists and ML engineers to build, train, deploy, and monitor models efficiently. A well-designed platform accelerates ML development while maintaining quality and governance.

## ML Platform Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   ML Platform Architecture                   │
└─────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                     User Interfaces                            │
│  Web UI │ CLI │ Python SDK │ REST API │ Notebooks             │
└───────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────────┐
│                    Platform Services                           │
├───────────────────────────────────────────────────────────────┤
│ Experiment      │ Model        │ Feature     │ Data           │
│ Tracking        │ Registry     │ Store       │ Versioning     │
├───────────────────────────────────────────────────────────────┤
│ Training        │ Deployment   │ Monitoring  │ AutoML         │
│ Orchestration   │ Service      │ Service     │ Service        │
└───────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                          │
├───────────────────────────────────────────────────────────────┤
│ Kubernetes  │ Storage  │ Compute  │ Networking  │ Security    │
└───────────────────────────────────────────────────────────────┘
                              │
┌───────────────────────────────────────────────────────────────┐
│                     Cloud Provider                             │
│              AWS / GCP / Azure / On-Premise                    │
└───────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Development Environment**: Notebooks, IDEs, experimentation tools
2. **Data Management**: Versioning, cataloging, quality checks
3. **Feature Store**: Centralized feature management
4. **Training Infrastructure**: Distributed training, GPU management
5. **Model Registry**: Version control for models
6. **Deployment Service**: Model serving at scale
7. **Monitoring & Observability**: Performance tracking, alerting
8. **Governance**: Access control, compliance, audit trails

---

## Platform Design Principles

### 1. Self-Service

**Enable data scientists to be productive without heavy ops involvement**

```python
# Platform SDK - Simple, intuitive API
from ml_platform import Platform

platform = Platform()

# Create experiment
experiment = platform.create_experiment("churn_prediction")

# Train model (platform handles infrastructure)
job = experiment.train(
    script="train.py",
    requirements="requirements.txt",
    instance_type="gpu.large",
    num_gpus=4
)

# Wait for completion
job.wait()

# Deploy model
deployment = experiment.deploy_latest(
    replicas=3,
    auto_scale=True,
    max_replicas=10
)

print(f"Model deployed at: {deployment.endpoint}")
```

### 2. Abstraction

**Hide infrastructure complexity while providing flexibility**

```python
# Platform abstracts infrastructure details
# User doesn't need to know about Kubernetes, Docker, etc.

# High-level API
deployment = platform.deploy_model(
    model_id="churn_v2",
    environment="production",
    scaling_policy="auto"
)

# Platform handles:
# - Docker image building
# - Kubernetes deployment
# - Service mesh configuration
# - Monitoring setup
# - Logging configuration
```

### 3. Consistency

**Standardized workflows across the organization**

```python
# All teams use same platform APIs
# Ensures consistency and best practices

class StandardMLWorkflow:
    def __init__(self, platform):
        self.platform = platform

    def run(self, config):
        # Data validation
        dataset = self.platform.data.load(config.dataset_id)
        self.platform.data.validate(dataset, schema=config.schema)

        # Feature engineering (using standard feature store)
        features = self.platform.features.create(dataset, config.feature_defs)

        # Training (using standard infrastructure)
        experiment = self.platform.train(features, config.model_config)

        # Evaluation (standard metrics)
        metrics = self.platform.evaluate(experiment, config.test_data)

        # Deployment (standard process)
        if metrics.passes_threshold(config.deployment_criteria):
            self.platform.deploy(experiment.best_model)
```

### 4. Scalability

**Support growth in users, models, and data**

- **Horizontal scaling**: Add more nodes as load increases
- **Multi-tenancy**: Isolate teams/projects efficiently
- **Resource management**: Fair sharing with quotas
- **Cost optimization**: Right-size resources automatically

### 5. Governance

**Maintain control, compliance, and security**

```python
# Platform enforces governance policies
class GovernancePolicies:
    @enforce_policy("data_access")
    def access_data(self, user, dataset_id):
        # Check permissions
        if not self.has_permission(user, dataset_id):
            raise PermissionError("Access denied")
        return self.load_dataset(dataset_id)

    @enforce_policy("model_deployment")
    def deploy_model(self, model, environment):
        # Require approvals for production
        if environment == "production":
            if not self.has_approval(model):
                raise ValueError("Production deployment requires approval")

        # Enforce monitoring
        self.setup_monitoring(model)
        return self.deploy(model, environment)
```

---

## Platform API Design

### RESTful API

```python
# api/platform_api.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(title="ML Platform API")

# Models
class TrainingJob(BaseModel):
    job_id: str
    status: str
    model_id: Optional[str]
    metrics: Optional[dict]

class DeploymentConfig(BaseModel):
    model_id: str
    environment: str
    replicas: int = 3
    auto_scale: bool = True
    max_replicas: int = 10

# Endpoints
@app.post("/experiments", status_code=201)
def create_experiment(name: str, description: Optional[str] = None):
    """Create new experiment"""
    experiment_id = str(uuid.uuid4())
    # Store in database
    return {
        "experiment_id": experiment_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat()
    }

@app.post("/experiments/{experiment_id}/train", status_code=202)
def start_training(experiment_id: str, config: TrainingConfig):
    """Start training job"""
    job_id = str(uuid.uuid4())

    # Submit to training infrastructure
    submit_training_job(experiment_id, job_id, config)

    return {
        "job_id": job_id,
        "status": "submitted",
        "experiment_id": experiment_id
    }

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get training job status"""
    job = get_job_from_db(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/models/{model_id}/deploy")
def deploy_model(model_id: str, config: DeploymentConfig):
    """Deploy model to environment"""
    # Validate model exists
    model = get_model_from_registry(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Check permissions
    check_deployment_permissions(model_id, config.environment)

    # Deploy
    deployment = create_deployment(model_id, config)

    return {
        "deployment_id": deployment.id,
        "endpoint": deployment.endpoint,
        "status": "deploying"
    }

@app.get("/deployments/{deployment_id}/metrics")
def get_deployment_metrics(deployment_id: str, window: str = "1h"):
    """Get deployment metrics"""
    metrics = query_prometheus(deployment_id, window)
    return metrics
```

### Python SDK

```python
# sdk/ml_platform_sdk.py
import requests
from typing import Optional, Dict, Any
import time

class MLPlatformSDK:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def create_experiment(self, name: str, description: Optional[str] = None):
        """Create experiment"""
        response = self.session.post(
            f"{self.api_url}/experiments",
            params={"name": name, "description": description}
        )
        response.raise_for_status()
        return Experiment(self, response.json())

    def get_experiment(self, experiment_id: str):
        """Get experiment by ID"""
        response = self.session.get(f"{self.api_url}/experiments/{experiment_id}")
        response.raise_for_status()
        return Experiment(self, response.json())

class Experiment:
    def __init__(self, client: MLPlatformSDK, data: dict):
        self.client = client
        self.id = data["experiment_id"]
        self.name = data["name"]

    def train(self, script: str, config: Dict[str, Any]) -> 'TrainingJob':
        """Submit training job"""
        response = self.client.session.post(
            f"{self.client.api_url}/experiments/{self.id}/train",
            json={"script": script, "config": config}
        )
        response.raise_for_status()
        return TrainingJob(self.client, response.json())

    def deploy_latest(self, **kwargs) -> 'Deployment':
        """Deploy latest model"""
        # Get latest model
        models = self.get_models()
        latest = max(models, key=lambda m: m.created_at)

        # Deploy
        return latest.deploy(**kwargs)

class TrainingJob:
    def __init__(self, client: MLPlatformSDK, data: dict):
        self.client = client
        self.id = data["job_id"]
        self.status = data["status"]

    def wait(self, poll_interval: int = 30):
        """Wait for job completion"""
        while self.status in ["submitted", "running"]:
            time.sleep(poll_interval)
            self.refresh()

        if self.status == "failed":
            raise RuntimeError(f"Job {self.id} failed")

    def refresh(self):
        """Refresh job status"""
        response = self.client.session.get(
            f"{self.client.api_url}/jobs/{self.id}"
        )
        response.raise_for_status()
        data = response.json()
        self.status = data["status"]

# Usage
platform = MLPlatformSDK(
    api_url="https://ml-platform.company.com/api",
    api_key="your-api-key"
)

experiment = platform.create_experiment("churn_prediction")
job = experiment.train("train.py", config={"learning_rate": 0.01})
job.wait()
deployment = experiment.deploy_latest(environment="production")
```

---

## Multi-Tenancy

### Resource Isolation

```yaml
# k8s/namespace-per-team.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-team-data-science
  labels:
    team: data-science
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: ml-team-data-science
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    requests.nvidia.com/gpu: "10"
    persistentvolumeclaims: "50"
    services.loadbalancers: "5"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: team-limits
  namespace: ml-team-data-science
spec:
  limits:
  - max:
      cpu: "32"
      memory: "128Gi"
      nvidia.com/gpu: "8"
    min:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

### Access Control

```python
# platform/rbac.py
from enum import Enum
from typing import Set, List
from dataclasses import dataclass

class Permission(Enum):
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    TRAIN_MODEL = "train_model"
    DEPLOY_STAGING = "deploy_staging"
    DEPLOY_PRODUCTION = "deploy_production"
    MANAGE_TEAM = "manage_team"

class Role(Enum):
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    TEAM_LEAD = "team_lead"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    Role.DATA_SCIENTIST: {
        Permission.READ_DATA,
        Permission.TRAIN_MODEL,
        Permission.DEPLOY_STAGING
    },
    Role.ML_ENGINEER: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.TRAIN_MODEL,
        Permission.DEPLOY_STAGING,
        Permission.DEPLOY_PRODUCTION
    },
    Role.TEAM_LEAD: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.TRAIN_MODEL,
        Permission.DEPLOY_STAGING,
        Permission.DEPLOY_PRODUCTION,
        Permission.MANAGE_TEAM
    },
    Role.ADMIN: set(Permission)  # All permissions
}

@dataclass
class User:
    id: str
    name: str
    email: str
    role: Role
    team: str

class AccessController:
    def check_permission(self, user: User, permission: Permission, resource: str):
        """Check if user has permission for resource"""
        # Check role permissions
        if permission not in ROLE_PERMISSIONS[user.role]:
            raise PermissionError(f"User {user.name} lacks {permission.value}")

        # Check resource ownership (team-based)
        if not self.owns_resource(user.team, resource):
            raise PermissionError(f"Team {user.team} does not own {resource}")

    def owns_resource(self, team: str, resource: str) -> bool:
        """Check if team owns resource"""
        # Query database for resource ownership
        return True  # Simplified

# Usage
@require_permission(Permission.DEPLOY_PRODUCTION)
def deploy_to_production(user: User, model_id: str):
    """Deploy model to production (requires permission)"""
    # Deployment logic
    pass
```

---

## Platform Observability

### Platform Metrics

```python
# platform/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info

# Usage metrics
platform_users = Gauge(
    'platform_active_users',
    'Number of active platform users',
    ['team']
)

training_jobs = Counter(
    'platform_training_jobs_total',
    'Total training jobs submitted',
    ['team', 'status']
)

deployment_count = Gauge(
    'platform_active_deployments',
    'Number of active deployments',
    ['team', 'environment']
)

# Performance metrics
api_requests = Counter(
    'platform_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

api_latency = Histogram(
    'platform_api_latency_seconds',
    'API request latency',
    ['endpoint']
)

# Resource utilization
gpu_utilization = Gauge(
    'platform_gpu_utilization',
    'GPU utilization percentage',
    ['team', 'node']
)

storage_usage = Gauge(
    'platform_storage_usage_bytes',
    'Storage usage in bytes',
    ['team', 'type']
)

# Platform health
platform_info = Info(
    'platform_info',
    'Platform version and configuration'
)
```

---

## Example Platforms

### 1. Uber Michelangelo

**Key Features:**
- End-to-end ML workflow
- Feature store integration
- Distributed training
- Online and offline serving
- A/B testing framework

### 2. Netflix Metaflow

**Key Features:**
- Python-first design
- Built-in versioning
- Cloud agnostic
- Production-grade error handling
- Seamless notebook-to-production

### 3. Airbnb Bighead

**Key Features:**
- Feature repository
- Model repository
- Automated feature generation
- Multi-model serving

### 4. LinkedIn Pro-ML

**Key Features:**
- Standardized workflows
- Feature marketplace
- Model validation
- Production monitoring

---

## Platform Implementation Checklist

### Phase 1: Foundation (3 months)
- [ ] Kubernetes cluster setup
- [ ] Authentication/authorization
- [ ] Basic API and SDK
- [ ] Experiment tracking (MLflow)
- [ ] Training infrastructure

### Phase 2: Core Features (6 months)
- [ ] Feature store
- [ ] Model registry
- [ ] Deployment service
- [ ] Monitoring and alerting
- [ ] Resource quotas and limits

### Phase 3: Advanced Features (9 months)
- [ ] AutoML capabilities
- [ ] A/B testing framework
- [ ] Data versioning
- [ ] Multi-cloud support
- [ ] Advanced governance

### Phase 4: Optimization (12+ months)
- [ ] Cost optimization
- [ ] Performance tuning
- [ ] Self-service onboarding
- [ ] Documentation and training
- [ ] Community building

---

## Best Practices

1. **Start Simple**: Build MVP, iterate based on user feedback
2. **User-Centric**: Design for data scientists, not for ops
3. **Opinionated**: Provide guardrails, enforce best practices
4. **Extensible**: Allow customization when needed
5. **Observable**: Instrument everything
6. **Documented**: Comprehensive docs and examples
7. **Reliable**: High availability, disaster recovery
8. **Secure**: Built-in security, compliance

## Key Takeaways

- ML platforms enable self-service, accelerating model development
- Good abstractions hide complexity while maintaining flexibility
- Multi-tenancy and governance are critical for enterprise adoption
- Start simple, iterate based on user needs
- Invest in documentation and developer experience

## Exercises

1. Design ML platform architecture for your organization
2. Implement basic platform API with authentication
3. Create Python SDK for platform interactions
4. Set up multi-tenant namespace isolation
5. Build platform observability dashboard

## Additional Resources

- "Building Machine Learning Powered Applications" by Emmanuel Ameisen
- "Machine Learning Design Patterns" by Lakshmanan et al.
- Uber Michelangelo paper
- Netflix Metaflow documentation
- Kubernetes Patterns book
