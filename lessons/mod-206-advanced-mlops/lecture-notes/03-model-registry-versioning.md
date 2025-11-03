# Lecture 03: Model Registry and Versioning

## Learning Objectives

By the end of this lecture, you will be able to:

- Design centralized model registries using MLflow, Neptune, or cloud-native solutions providing unified model catalog with versioning, metadata, and lifecycle management
- Implement semantic versioning strategies for ML models (major.minor.patch) with automated version bumping based on data changes, architecture updates, or hyperparameter modifications
- Architect model lifecycle management workflows with stages (Development, Staging, Production, Archived) and automated promotion rules based on performance metrics
- Configure model lineage tracking capturing complete model provenance including training data, code version, hyperparameters, dependencies, and parent models
- Design model metadata schemas storing essential information (training metrics, feature importance, model signatures, performance benchmarks, compliance certifications)
- Implement model promotion workflows with approval processes, A/B test requirements, performance thresholds, and automated rollback capabilities
- Build model reproducibility systems enabling exact model recreation from registry metadata including environment snapshots and deterministic training pipelines
- Architect model governance controls with access policies, audit logs, compliance validation, and automated retirement of outdated models

## Overview

A model registry is a centralized catalog for managing machine learning models throughout their lifecycle, from experimentation to production deployment. It provides versioning, lineage tracking, and stage management capabilities.

## The Model Registry Problem

### Without a Model Registry

**Common Issues:**
```python
# Problem 1: Models scattered everywhere
models/
├── model_v1.pkl
├── model_v2_final.pkl
├── model_v2_final_FINAL.pkl
├── model_v3_with_new_features.pkl
├── model_production_2024_03_15.pkl
└── best_model_DO_NOT_DELETE.pkl

# Problem 2: No metadata tracking
# Which model is in production?
# What data was used to train it?
# What were the hyperparameters?
# Who trained it and when?

# Problem 3: No lineage
# Can't reproduce model
# Don't know which code version was used
# Can't track feature transformations
```

**Manual Model Deployment:**
```python
# deploy.py - Error-prone manual process
import joblib
import shutil
from datetime import datetime

# Load "best" model (which one?)
model = joblib.load('models/model_v2_final_FINAL.pkl')

# Copy to production location (manual, error-prone)
shutil.copy(
    'models/model_v2_final_FINAL.pkl',
    '/production/models/current_model.pkl'
)

# Manual logging
with open('deployment_log.txt', 'a') as f:
    f.write(f"{datetime.now()}: Deployed model_v2_final_FINAL.pkl\n")

# No rollback mechanism!
# No A/B testing support!
# No approval workflow!
```

---

## Model Registry Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Model Registry Architecture                 │
└─────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────┐
│  Experiment  │────────▶│  Model Registry  │
│   Tracking   │         │   (Metadata DB)  │
└──────────────┘         └──────────────────┘
                                  │
                   ┌──────────────┼──────────────┐
                   ▼              ▼              ▼
            ┌───────────┐  ┌───────────┐  ┌───────────┐
            │   None    │  │  Staging  │  │Production │
            │  (Recent) │  │  (Testing)│  │  (Live)   │
            └───────────┘  └───────────┘  └───────────┘
                   │              │              │
                   └──────────────┴──────────────┘
                                  ▼
                        ┌──────────────────┐
                        │  Artifact Store  │
                        │  (S3, GCS, etc.) │
                        └──────────────────┘
```

### Components

1. **Model Metadata**: Parameters, metrics, tags, versions
2. **Artifact Storage**: Actual model files
3. **Stage Management**: None, Staging, Production, Archived
4. **Lineage Tracking**: Code version, data version, dependencies
5. **Approval Workflow**: Model promotion gates

---

## MLflow Model Registry Implementation

### Setup and Configuration

```python
# config/mlflow_config.py
import mlflow
import os

def setup_mlflow():
    """Configure MLflow tracking and registry"""
    # Set tracking URI (can be local, remote, or cloud)
    mlflow.set_tracking_uri("http://mlflow-server:5000")

    # Optional: Set artifact root (S3, GCS, Azure Blob)
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio:9000'

    # Set experiment
    mlflow.set_experiment("production_model_training")

    print(f"MLflow URI: {mlflow.get_tracking_uri()}")
    print(f"Experiment: {mlflow.get_experiment_by_name('production_model_training')}")

# Docker Compose for MLflow Server
"""
version: '3.8'

services:
  mlflow-server:
    image: python:3.11-slim
    ports:
      - "5000:5000"
    volumes:
      - ./mlruns:/mlflow/mlruns
      - ./mlflow-artifacts:/mlflow/artifacts
    environment:
      - BACKEND_STORE_URI=sqlite:///mlflow/mlruns/mlflow.db
      - DEFAULT_ARTIFACT_ROOT=/mlflow/artifacts
    command: >
      bash -c "pip install mlflow psycopg2-binary boto3 &&
               mlflow server
               --backend-store-uri sqlite:///mlflow/mlruns/mlflow.db
               --default-artifact-root /mlflow/artifacts
               --host 0.0.0.0
               --port 5000"

  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
"""
```

### Model Training with Registry Integration

```python
# training/train_with_registry.py
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np
from datetime import datetime
import json

class ModelTrainerWithRegistry:
    def __init__(self, experiment_name, model_name):
        self.experiment_name = experiment_name
        self.model_name = model_name
        self.client = MlflowClient()

        mlflow.set_experiment(experiment_name)

    def load_data(self, data_path):
        """Load and split data"""
        data = pd.read_csv(data_path)
        X = data.drop('target', axis=1)
        y = data['target']

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train, hyperparams):
        """Train model with hyperparameters"""
        model = RandomForestClassifier(**hyperparams)
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_test, y_test):
        """Compute comprehensive metrics"""
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted'),
            'recall': recall_score(y_test, predictions, average='weighted'),
            'f1_score': f1_score(y_test, predictions, average='weighted')
        }

        return metrics, predictions, probabilities

    def log_model_signature(self, X_train, predictions, probabilities):
        """Create model signature for input/output schema"""
        from mlflow.models.signature import infer_signature

        # Infer signature from training data and predictions
        signature = infer_signature(
            X_train,
            predictions
        )

        return signature

    def run_training_pipeline(self, data_path, hyperparams, tags=None):
        """Complete training pipeline with registry integration"""
        with mlflow.start_run(run_name=f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
            # Log parameters
            mlflow.log_params(hyperparams)

            # Log dataset info
            X_train, X_test, y_train, y_test = self.load_data(data_path)

            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_param("n_test_samples", len(X_test))
            mlflow.log_param("n_features", X_train.shape[1])
            mlflow.log_param("data_path", data_path)

            # Train model
            model = self.train_model(X_train, y_train, hyperparams)

            # Evaluate model
            metrics, predictions, probabilities = self.evaluate_model(
                model, X_test, y_test
            )

            # Log metrics
            mlflow.log_metrics(metrics)

            # Create signature
            signature = self.log_model_signature(
                X_train, predictions, probabilities
            )

            # Log model to registry
            model_info = mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                signature=signature,
                registered_model_name=self.model_name,
                input_example=X_train.iloc[:5],  # Log example input
                pip_requirements=[
                    f"scikit-learn=={sklearn.__version__}",
                    f"pandas=={pd.__version__}",
                    f"numpy=={np.__version__}"
                ]
            )

            # Add custom tags
            if tags:
                for key, value in tags.items():
                    mlflow.set_tag(key, value)

            # Add standard tags
            mlflow.set_tag("model_type", "random_forest")
            mlflow.set_tag("training_date", datetime.now().isoformat())
            mlflow.set_tag("data_version", "v1.0")

            # Get model version
            model_version = model_info.registered_model_version

            # Add description to model version
            self.client.update_model_version(
                name=self.model_name,
                version=model_version,
                description=f"""
                Model trained on {datetime.now().strftime('%Y-%m-%d')}
                Test Accuracy: {metrics['accuracy']:.3f}
                Test F1 Score: {metrics['f1_score']:.3f}

                Hyperparameters:
                {json.dumps(hyperparams, indent=2)}
                """
            )

            print(f"Model registered: {self.model_name} version {model_version}")
            print(f"Run ID: {run.info.run_id}")
            print(f"Metrics: {metrics}")

            return model_info, metrics, model_version

# Usage
if __name__ == '__main__':
    trainer = ModelTrainerWithRegistry(
        experiment_name="customer_churn_prediction",
        model_name="churn_predictor"
    )

    hyperparams = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42
    }

    tags = {
        'team': 'ml_platform',
        'purpose': 'production_candidate',
        'ticket': 'JIRA-1234'
    }

    model_info, metrics, version = trainer.run_training_pipeline(
        data_path='data/training_data.csv',
        hyperparams=hyperparams,
        tags=tags
    )
```

---

## Model Lifecycle Management

### Stage Transitions

```python
# lifecycle/model_lifecycle_manager.py
from mlflow.tracking import MlflowClient
from mlflow.entities.model_registry import ModelVersionStatus
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelLifecycleManager:
    def __init__(self):
        self.client = MlflowClient()

    def get_model_versions(self, model_name):
        """Get all versions of a model"""
        return self.client.search_model_versions(f"name='{model_name}'")

    def get_latest_versions(self, model_name, stages=None):
        """Get latest model versions by stage"""
        if stages is None:
            stages = ["None", "Staging", "Production"]

        versions = {}
        for stage in stages:
            latest = self.client.get_latest_versions(model_name, stages=[stage])
            if latest:
                versions[stage] = latest[0]

        return versions

    def transition_to_staging(self, model_name, version):
        """Move model to Staging stage"""
        logger.info(f"Transitioning {model_name} v{version} to Staging")

        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Staging",
            archive_existing_versions=False
        )

        # Add transition annotation
        self.client.update_model_version(
            name=model_name,
            version=version,
            description=f"Moved to Staging on {datetime.now().isoformat()}"
        )

        logger.info(f"Successfully moved to Staging")

    def transition_to_production(self, model_name, version, archive_existing=True):
        """Move model to Production stage"""
        logger.info(f"Transitioning {model_name} v{version} to Production")

        # Archive existing production models
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=archive_existing
        )

        # Add transition annotation
        self.client.update_model_version(
            name=model_name,
            version=version,
            description=f"Deployed to Production on {datetime.now().isoformat()}"
        )

        logger.info(f"Successfully deployed to Production")

    def archive_model(self, model_name, version):
        """Archive a model version"""
        logger.info(f"Archiving {model_name} v{version}")

        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Archived"
        )

    def compare_models(self, model_name, version1, version2):
        """Compare two model versions"""
        # Get runs for both versions
        mv1 = self.client.get_model_version(model_name, version1)
        mv2 = self.client.get_model_version(model_name, version2)

        run1 = self.client.get_run(mv1.run_id)
        run2 = self.client.get_run(mv2.run_id)

        comparison = {
            'version1': {
                'version': version1,
                'metrics': run1.data.metrics,
                'params': run1.data.params,
                'stage': mv1.current_stage
            },
            'version2': {
                'version': version2,
                'metrics': run2.data.metrics,
                'params': run2.data.params,
                'stage': mv2.current_stage
            }
        }

        return comparison

# Usage
manager = ModelLifecycleManager()

# Get all versions
versions = manager.get_model_versions("churn_predictor")
print(f"Found {len(versions)} versions")

# Get latest by stage
latest = manager.get_latest_versions("churn_predictor")
print(f"Production: v{latest.get('Production').version if 'Production' in latest else 'None'}")

# Compare models
comparison = manager.compare_models("churn_predictor", "1", "2")
```

### Automated Model Promotion

```python
# lifecycle/automated_promotion.py
from mlflow.tracking import MlflowClient
import logging

logger = logging.getLogger(__name__)

class AutomatedModelPromotion:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = MlflowClient()

    def evaluate_promotion_criteria(self, version):
        """Check if model meets promotion criteria"""
        model_version = self.client.get_model_version(self.model_name, version)
        run = self.client.get_run(model_version.run_id)

        metrics = run.data.metrics

        # Define promotion criteria
        criteria = {
            'min_accuracy': 0.85,
            'min_precision': 0.80,
            'min_recall': 0.75,
            'max_overfitting': 0.15  # train_acc - test_acc
        }

        # Check criteria
        checks = {
            'accuracy_check': metrics.get('accuracy', 0) >= criteria['min_accuracy'],
            'precision_check': metrics.get('precision', 0) >= criteria['min_precision'],
            'recall_check': metrics.get('recall', 0) >= criteria['min_recall'],
        }

        # Check overfitting
        train_acc = metrics.get('train_accuracy', 0)
        test_acc = metrics.get('accuracy', 0)
        checks['overfitting_check'] = (train_acc - test_acc) <= criteria['max_overfitting']

        passed = all(checks.values())

        return passed, checks, metrics

    def auto_promote_to_staging(self, version):
        """Automatically promote model to staging if criteria met"""
        logger.info(f"Evaluating {self.model_name} v{version} for Staging promotion")

        passed, checks, metrics = self.evaluate_promotion_criteria(version)

        if passed:
            logger.info(f"Model passed all checks: {checks}")

            # Promote to staging
            self.client.transition_model_version_stage(
                name=self.model_name,
                version=version,
                stage="Staging"
            )

            logger.info(f"Promoted to Staging successfully")
            return True
        else:
            logger.warning(f"Model failed checks: {checks}")
            return False

    def request_production_promotion(self, version):
        """Request manual approval for production promotion"""
        logger.info(f"Requesting production promotion for {self.model_name} v{version}")

        # Create approval request (could integrate with Jira, Slack, etc.)
        model_version = self.client.get_model_version(self.model_name, version)

        # Add tag indicating approval requested
        self.client.set_model_version_tag(
            name=self.model_name,
            version=version,
            key="approval_status",
            value="requested"
        )

        # In practice, send notification to stakeholders
        logger.info("Approval request created")

# Airflow DAG for automated promotion
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

def promote_new_model(**context):
    """Promote newly trained model"""
    promoter = AutomatedModelPromotion("churn_predictor")

    # Get latest model version
    versions = promoter.client.search_model_versions(
        f"name='{promoter.model_name}'"
    )
    latest_version = max([int(v.version) for v in versions])

    # Try to promote
    success = promoter.auto_promote_to_staging(latest_version)

    return 'send_notification' if success else 'log_failure'

dag = DAG(
    'model_promotion_workflow',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Triggered by training completion
    catchup=False
)

# Wait for training to complete
wait_for_training = ExternalTaskSensor(
    task_id='wait_for_training',
    external_dag_id='ml_model_training',
    external_task_id='train_model',
    dag=dag
)

# Promote model
promote = BranchPythonOperator(
    task_id='promote_model',
    python_callable=promote_new_model,
    dag=dag
)

wait_for_training >> promote
```

---

## Model Lineage Tracking

### Capturing Complete Lineage

```python
# lineage/model_lineage.py
import mlflow
from mlflow.tracking import MlflowClient
import hashlib
import json

class ModelLineageTracker:
    def __init__(self):
        self.client = MlflowClient()

    def log_data_lineage(self, run_id, data_info):
        """Log data lineage information"""
        self.client.log_param(run_id, "data_source", data_info['source'])
        self.client.log_param(run_id, "data_version", data_info['version'])
        self.client.log_param(run_id, "data_sha256", self.compute_data_hash(data_info['path']))

        # Log dataset as artifact
        self.client.log_artifact(run_id, data_info['path'], "datasets")

    def log_code_lineage(self, run_id, git_info):
        """Log code version information"""
        self.client.set_tag(run_id, "git.repo", git_info['repo'])
        self.client.set_tag(run_id, "git.commit", git_info['commit'])
        self.client.set_tag(run_id, "git.branch", git_info['branch'])

    def log_feature_lineage(self, run_id, feature_info):
        """Log feature engineering lineage"""
        self.client.log_dict(run_id, feature_info, "feature_metadata.json")

    def log_dependency_lineage(self, run_id):
        """Log Python package dependencies"""
        import pkg_resources

        dependencies = {
            pkg.key: pkg.version
            for pkg in pkg_resources.working_set
        }

        self.client.log_dict(run_id, dependencies, "dependencies.json")

    def compute_data_hash(self, filepath):
        """Compute SHA256 hash of data file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_model_lineage(self, model_name, version):
        """Retrieve complete lineage for a model version"""
        model_version = self.client.get_model_version(model_name, version)
        run = self.client.get_run(model_version.run_id)

        lineage = {
            'model': {
                'name': model_name,
                'version': version,
                'stage': model_version.current_stage,
                'created_at': model_version.creation_timestamp
            },
            'data': {
                'source': run.data.params.get('data_source'),
                'version': run.data.params.get('data_version'),
                'hash': run.data.params.get('data_sha256')
            },
            'code': {
                'repo': run.data.tags.get('git.repo'),
                'commit': run.data.tags.get('git.commit'),
                'branch': run.data.tags.get('git.branch')
            },
            'metrics': run.data.metrics,
            'params': run.data.params,
            'artifacts': [a.path for a in self.client.list_artifacts(run.info.run_id)]
        }

        return lineage

# Usage
tracker = ModelLineageTracker()

with mlflow.start_run() as run:
    # Log complete lineage
    tracker.log_data_lineage(run.info.run_id, {
        'source': 's3://my-bucket/data/training_data.csv',
        'version': 'v2.1.0',
        'path': 'data/training_data.csv'
    })

    tracker.log_code_lineage(run.info.run_id, {
        'repo': 'github.com/myorg/ml-models',
        'commit': 'a1b2c3d4',
        'branch': 'main'
    })

    tracker.log_dependency_lineage(run.info.run_id)

    # Train model...
```

---

## Model Versioning Best Practices

### Semantic Versioning for Models

```python
# versioning/semantic_versioning.py
from dataclasses import dataclass
from enum import Enum

class VersionChangeType(Enum):
    MAJOR = "major"  # Breaking changes (new architecture, different features)
    MINOR = "minor"  # Backward compatible improvements
    PATCH = "patch"  # Bug fixes, retraining with same setup

@dataclass
class ModelVersion:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

    def bump(self, change_type: VersionChangeType):
        """Bump version based on change type"""
        if change_type == VersionChangeType.MAJOR:
            self.major += 1
            self.minor = 0
            self.patch = 0
        elif change_type == VersionChangeType.MINOR:
            self.minor += 1
            self.patch = 0
        else:
            self.patch += 1

        return self

# Example usage
version = ModelVersion(1, 0, 0)
print(version)  # v1.0.0

# Minor improvement
version.bump(VersionChangeType.MINOR)
print(version)  # v1.1.0

# Patch (retrain)
version.bump(VersionChangeType.PATCH)
print(version)  # v1.1.1
```

---

## Key Takeaways

1. **Model Registry Centralizes ML Assets**: Single source of truth for models
2. **Version Control for Models**: Track changes, compare versions
3. **Stage Management**: Clear promotion path (None → Staging → Production)
4. **Lineage Tracking**: Full reproducibility with data, code, and environment tracking
5. **Automated Workflows**: Reduce manual errors with automation

## Exercises

1. Set up MLflow Model Registry with PostgreSQL backend
2. Implement automated model promotion workflow
3. Create model comparison dashboard
4. Build complete lineage tracking system
5. Implement rollback mechanism for production models

## Additional Resources

- MLflow Model Registry documentation
- "Versioning ML Models" by Neptune.ai
- "Model Management in Production" by Google
- MLOps best practices guides
