# Lecture 01: MLOps Maturity Model

## Learning Objectives

By the end of this lecture, you will be able to:

- Design MLOps maturity assessments evaluating organizations across dimensions (automation, CI/CD, monitoring, governance) using Level 0-5 maturity framework
- Architect progression roadmaps from manual workflows (Level 0) to fully automated ML platforms (Level 5) with phased implementation plans and success metrics
- Evaluate organizational MLOps capabilities across critical areas including training automation, deployment pipelines, monitoring systems, and model governance
- Implement automation strategies for transitioning between maturity levels including CI/CD pipelines, automated testing, model validation, and continuous training
- Design governance frameworks appropriate for each maturity level establishing model approval workflows, compliance requirements, and audit trails
- Benchmark organizational MLOps practices against industry standards identifying capability gaps, prioritizing improvements, and measuring progress
- Build business cases for MLOps investment quantifying ROI through reduced time-to-production, improved model performance, and operational efficiency gains
- Architect organizational structures and team compositions required to support different MLOps maturity levels with clear roles, responsibilities, and skill requirements

## Overview

## Overview

MLOps maturity represents an organization's capability to effectively deploy, monitor, and manage machine learning systems in production. Understanding where your organization sits on the maturity spectrum is crucial for planning improvements.

## MLOps Maturity Levels

### Level 0: No MLOps

**Characteristics:**
- Manual, script-driven, and interactive process
- Disconnect between ML and operations
- Lack of automation
- Rare releases
- No CI/CD
- Manual testing
- No monitoring

**Code Example - Typical Level 0 Workflow:**
```python
# manual_training.py - Typical Level 0 approach
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Manually load data
data = pd.read_csv('/home/user/data/training_data_v3_final_FINAL.csv')

# Manual preprocessing
X = data.drop('target', axis=1)
y = data['target']

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Save model manually
with open('model_v3.pkl', 'wb') as f:
    pickle.dump(model, f)

# Email model to ops team or upload to shared drive
print("Model trained! Send to ops team for deployment.")
```

**Deployment:**
```python
# manual_serve.py - Manual serving script
import pickle
from flask import Flask, request

app = Flask(__name__)

# Load model manually
with open('model_v3.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    prediction = model.predict([data['features']])
    return {'prediction': prediction.tolist()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Issues:**
- No version control for models
- No reproducibility
- No monitoring
- Manual coordination between teams
- Deployment requires ops intervention

---

### Level 1: DevOps but No MLOps

**Characteristics:**
- ML code is managed but still experimental
- Unit tests for ML code
- CI/CD for application code (not ML pipeline)
- Releases are automated but model training is not
- Operational metrics but not ML-specific metrics

**Code Example - Level 1 Improvement:**
```python
# training_pipeline.py - Slightly better with version control
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import json
from datetime import datetime

class ModelTrainer:
    def __init__(self, data_path, model_path):
        self.data_path = data_path
        self.model_path = model_path
        self.metadata = {}

    def load_data(self):
        """Load and split data"""
        data = pd.read_csv(self.data_path)
        X = data.drop('target', axis=1)
        y = data['target']
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self):
        """Train model with basic tracking"""
        X_train, X_test, y_train, y_test = self.load_data()

        # Train
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))

        # Save metadata
        self.metadata = {
            'training_date': datetime.now().isoformat(),
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'data_path': self.data_path,
            'n_estimators': 100
        }

        # Save model and metadata
        with open(self.model_path, 'wb') as f:
            pickle.dump(model, f)

        with open(self.model_path + '.metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)

        return model, self.metadata

if __name__ == '__main__':
    trainer = ModelTrainer('data/training_data.csv', 'models/model_v1.pkl')
    model, metadata = trainer.train()
    print(f"Model trained. Accuracy: {metadata['test_accuracy']:.3f}")
```

**Dockerfile for serving:**
```dockerfile
# Dockerfile - Basic containerization
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY model_v1.pkl .
COPY serve.py .

EXPOSE 5000

CMD ["python", "serve.py"]
```

**Still Missing:**
- Automated training pipeline
- Experiment tracking
- Model registry
- Feature store
- ML-specific monitoring

---

### Level 2: Automated Training

**Characteristics:**
- Automated training pipeline
- Experiment tracking implemented
- Model versioning
- Feature engineering is automated
- CT (Continuous Training) pipeline
- Basic model validation before deployment

**Code Example - Level 2 with MLflow:**
```python
# automated_training_pipeline.py
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLOpsTrainingPipeline:
    def __init__(self, experiment_name, data_path):
        self.experiment_name = experiment_name
        self.data_path = data_path
        mlflow.set_experiment(experiment_name)
        self.client = MlflowClient()

    def load_and_preprocess(self):
        """Load and preprocess data"""
        logger.info(f"Loading data from {self.data_path}")
        data = pd.read_csv(self.data_path)

        # Log data statistics
        mlflow.log_param("n_samples", len(data))
        mlflow.log_param("n_features", len(data.columns) - 1)

        X = data.drop('target', axis=1)
        y = data['target']

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train, hyperparams):
        """Train model with hyperparameters"""
        logger.info(f"Training model with params: {hyperparams}")

        model = RandomForestClassifier(**hyperparams)
        model.fit(X_train, y_train)

        return model

    def evaluate_model(self, model, X_train, y_train, X_test, y_test):
        """Comprehensive model evaluation"""
        # Training metrics
        train_pred = model.predict(X_train)
        train_metrics = {
            'train_accuracy': accuracy_score(y_train, train_pred),
            'train_precision': precision_score(y_train, train_pred, average='weighted'),
            'train_recall': recall_score(y_train, train_pred, average='weighted'),
            'train_f1': f1_score(y_train, train_pred, average='weighted')
        }

        # Test metrics
        test_pred = model.predict(X_test)
        test_metrics = {
            'test_accuracy': accuracy_score(y_test, test_pred),
            'test_precision': precision_score(y_test, test_pred, average='weighted'),
            'test_recall': recall_score(y_test, test_pred, average='weighted'),
            'test_f1': f1_score(y_test, test_pred, average='weighted')
        }

        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_metrics = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }

        return {**train_metrics, **test_metrics, **cv_metrics}

    def validate_model(self, metrics, thresholds):
        """Validate model meets minimum thresholds"""
        logger.info("Validating model against thresholds")

        validations = {
            'accuracy_threshold': metrics['test_accuracy'] >= thresholds.get('min_accuracy', 0.7),
            'precision_threshold': metrics['test_precision'] >= thresholds.get('min_precision', 0.7),
            'overfitting_check': abs(metrics['train_accuracy'] - metrics['test_accuracy']) < 0.15
        }

        is_valid = all(validations.values())

        for check, passed in validations.items():
            mlflow.log_metric(f"validation_{check}", 1 if passed else 0)

        return is_valid, validations

    def run_training_pipeline(self, hyperparams, thresholds):
        """Execute full training pipeline"""
        with mlflow.start_run() as run:
            logger.info(f"Starting MLflow run: {run.info.run_id}")

            # Log hyperparameters
            mlflow.log_params(hyperparams)

            # Load data
            X_train, X_test, y_train, y_test = self.load_and_preprocess()

            # Train model
            model = self.train_model(X_train, y_train, hyperparams)

            # Evaluate model
            metrics = self.evaluate_model(model, X_train, y_train, X_test, y_test)
            mlflow.log_metrics(metrics)

            # Validate model
            is_valid, validations = self.validate_model(metrics, thresholds)

            if is_valid:
                # Log model
                mlflow.sklearn.log_model(
                    model,
                    "model",
                    registered_model_name=f"{self.experiment_name}_model"
                )
                logger.info("Model passed validation and registered")
                mlflow.set_tag("validation_status", "passed")
            else:
                logger.warning(f"Model failed validation: {validations}")
                mlflow.set_tag("validation_status", "failed")

            return run.info.run_id, is_valid, metrics

# Example usage
if __name__ == '__main__':
    pipeline = MLOpsTrainingPipeline(
        experiment_name="customer_churn_prediction",
        data_path="data/training_data.csv"
    )

    hyperparams = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42
    }

    thresholds = {
        'min_accuracy': 0.85,
        'min_precision': 0.80
    }

    run_id, passed, metrics = pipeline.run_training_pipeline(hyperparams, thresholds)
    print(f"Run ID: {run_id}")
    print(f"Validation: {'PASSED' if passed else 'FAILED'}")
    print(f"Test Accuracy: {metrics['test_accuracy']:.3f}")
```

**Airflow DAG for Scheduled Training:**
```python
# dags/ml_training_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_model_training',
    default_args=default_args,
    description='Automated ML model training pipeline',
    schedule_interval='@weekly',
    catchup=False
)

def extract_features(**context):
    from automated_training_pipeline import MLOpsTrainingPipeline
    # Feature extraction logic
    pass

def train_model(**context):
    from automated_training_pipeline import MLOpsTrainingPipeline
    pipeline = MLOpsTrainingPipeline("customer_churn", "data/latest.csv")
    # Training logic
    pass

def validate_and_register(**context):
    # Model validation and registration
    pass

extract = PythonOperator(
    task_id='extract_features',
    python_callable=extract_features,
    dag=dag
)

train = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

validate = PythonOperator(
    task_id='validate_and_register',
    python_callable=validate_and_register,
    dag=dag
)

extract >> train >> validate
```

---

### Level 3: Automated Deployment

**Characteristics:**
- CI/CD for ML models
- A/B testing framework
- Automated model deployment
- Canary releases
- Automated rollback
- Model monitoring in production
- Shadow mode deployment

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Level 3 MLOps Architecture                │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Feature    │────▶│   Training   │────▶│    Model     │
│    Store     │     │   Pipeline   │     │   Registry   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐     ┌──────────────┐
                     │ Experiment   │     │  Validation  │
                     │  Tracking    │     │   Service    │
                     └──────────────┘     └──────────────┘
                                                  │
                            ┌─────────────────────┤
                            ▼                     ▼
                    ┌──────────────┐     ┌──────────────┐
                    │   Canary     │     │  Production  │
                    │ Deployment   │────▶│  Deployment  │
                    └──────────────┘     └──────────────┘
                            │                     │
                            └──────────┬──────────┘
                                       ▼
                            ┌──────────────────┐
                            │    Monitoring    │
                            │  & Observability │
                            └──────────────────┘
```

**Key Components:**
- Feature Store: Centralized feature management
- Experiment Tracking: MLflow, Weights & Biases
- Model Registry: Versioned model storage
- Automated deployment with traffic splitting
- Comprehensive monitoring

---

### Level 4: Full MLOps Automation

**Characteristics:**
- End-to-end automation
- Automated feature engineering
- AutoML integration
- Continuous monitoring and retraining
- Data drift detection
- Model performance monitoring
- Automated rollback based on metrics
- Multi-model orchestration

**Comprehensive Monitoring:**
```python
# monitoring/model_monitor.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging

class ModelMonitor:
    def __init__(self):
        # Prediction metrics
        self.prediction_counter = Counter(
            'model_predictions_total',
            'Total number of predictions',
            ['model_name', 'version']
        )

        self.prediction_latency = Histogram(
            'model_prediction_latency_seconds',
            'Model prediction latency',
            ['model_name', 'version']
        )

        self.prediction_confidence = Histogram(
            'model_prediction_confidence',
            'Prediction confidence score',
            ['model_name', 'version']
        )

        # Data drift metrics
        self.data_drift_score = Gauge(
            'model_data_drift_score',
            'Data drift score',
            ['model_name', 'feature']
        )

        # Model performance metrics
        self.model_accuracy = Gauge(
            'model_accuracy',
            'Model accuracy over time',
            ['model_name', 'version']
        )

        # Error tracking
        self.prediction_errors = Counter(
            'model_prediction_errors_total',
            'Total prediction errors',
            ['model_name', 'error_type']
        )

    def record_prediction(self, model_name, version, latency, confidence):
        """Record prediction metrics"""
        self.prediction_counter.labels(
            model_name=model_name,
            version=version
        ).inc()

        self.prediction_latency.labels(
            model_name=model_name,
            version=version
        ).observe(latency)

        self.prediction_confidence.labels(
            model_name=model_name,
            version=version
        ).observe(confidence)

    def record_drift(self, model_name, feature, drift_score):
        """Record data drift"""
        self.data_drift_score.labels(
            model_name=model_name,
            feature=feature
        ).set(drift_score)

    def record_error(self, model_name, error_type):
        """Record prediction error"""
        self.prediction_errors.labels(
            model_name=model_name,
            error_type=error_type
        ).inc()

# Start Prometheus metrics server
if __name__ == '__main__':
    monitor = ModelMonitor()
    start_http_server(8000)

    # Keep running
    while True:
        time.sleep(1)
```

---

## MLOps Maturity Assessment Framework

### Assessment Criteria

**1. Data Management (0-5 score)**
- 0: Manual data handling
- 1: Version-controlled data
- 2: Automated data validation
- 3: Feature store implementation
- 4: Real-time feature serving
- 5: Automated feature discovery

**2. Model Development (0-5 score)**
- 0: Notebooks without version control
- 1: Versioned code in Git
- 2: Experiment tracking
- 3: Automated hyperparameter tuning
- 4: AutoML integration
- 5: Automated model selection

**3. Model Deployment (0-5 score)**
- 0: Manual deployment
- 1: Containerized models
- 2: Basic CI/CD
- 3: Canary/blue-green deployment
- 4: Automated A/B testing
- 5: Multi-model orchestration

**4. Monitoring & Observability (0-5 score)**
- 0: No monitoring
- 1: Basic service metrics
- 2: Model-specific metrics
- 3: Data drift detection
- 4: Performance degradation alerts
- 5: Automated retraining triggers

**5. Governance & Compliance (0-5 score)**
- 0: No governance
- 1: Basic model documentation
- 2: Model lineage tracking
- 3: Automated compliance checks
- 4: Audit trail
- 5: Automated policy enforcement

### Assessment Tool

```python
# mlops_assessment.py
class MLOpsMaturityAssessment:
    def __init__(self):
        self.dimensions = {
            'data_management': 0,
            'model_development': 0,
            'model_deployment': 0,
            'monitoring': 0,
            'governance': 0
        }

    def assess(self):
        """Interactive assessment"""
        questions = {
            'data_management': [
                "Is data versioned and tracked?",
                "Is there automated data validation?",
                "Is there a feature store?",
                "Are features served in real-time?",
                "Is there automated feature engineering?"
            ],
            'model_development': [
                "Is model code in version control?",
                "Do you use experiment tracking?",
                "Is hyperparameter tuning automated?",
                "Do you use AutoML?",
                "Is model selection automated?"
            ],
            # ... more questions
        }

        for dimension, questions_list in questions.items():
            score = 0
            for question in questions_list:
                response = input(f"{question} (y/n): ")
                if response.lower() == 'y':
                    score += 1
            self.dimensions[dimension] = score

        return self.calculate_maturity()

    def calculate_maturity(self):
        """Calculate overall maturity level"""
        avg_score = sum(self.dimensions.values()) / len(self.dimensions)

        if avg_score < 1:
            return 0, "No MLOps"
        elif avg_score < 2:
            return 1, "DevOps but no MLOps"
        elif avg_score < 3:
            return 2, "Automated Training"
        elif avg_score < 4:
            return 3, "Automated Deployment"
        else:
            return 4, "Full MLOps Automation"

    def generate_roadmap(self):
        """Generate improvement roadmap"""
        recommendations = []

        for dimension, score in self.dimensions.items():
            if score < 3:
                recommendations.append({
                    'dimension': dimension,
                    'current_score': score,
                    'target_score': 3,
                    'priority': 'high' if score < 2 else 'medium'
                })

        return recommendations

# Usage
if __name__ == '__main__':
    assessment = MLOpsMaturityAssessment()
    level, description = assessment.assess()
    print(f"\nMLOps Maturity Level: {level} - {description}")

    roadmap = assessment.generate_roadmap()
    print("\nImprovement Roadmap:")
    for item in roadmap:
        print(f"- {item['dimension']}: {item['current_score']} → {item['target_score']} (Priority: {item['priority']})")
```

---

## Industry Benchmarks

### Technology Adoption by Maturity Level

**Level 0-1:**
- Jupyter notebooks
- Git
- Docker
- Basic CI/CD

**Level 2:**
- MLflow / Weights & Biases
- DVC (Data Version Control)
- Airflow / Kubeflow
- Model registry

**Level 3:**
- Feature store (Feast, Tecton)
- A/B testing framework
- Prometheus / Grafana
- Kubernetes operators

**Level 4:**
- Real-time feature serving
- Automated retraining
- Multi-model serving
- Advanced monitoring (Evidently AI, Fiddler)

---

## Key Takeaways

1. **MLOps maturity is a journey**: Organizations typically progress through levels over time
2. **Assessment is crucial**: Understanding current state enables effective planning
3. **Focus on automation**: Each level adds more automation
4. **People and process matter**: Technology alone doesn't achieve MLOps maturity
5. **Continuous improvement**: MLOps practices should evolve with the organization

## Exercises

1. Assess your organization's MLOps maturity across all dimensions
2. Identify the biggest gap in your current MLOps capabilities
3. Create a 6-month roadmap to advance one maturity level
4. Compare your assessment with industry benchmarks

## Additional Resources

- "Machine Learning Operations Maturity Model" by Google Cloud
- "MLOps: Continuous delivery and automation pipelines" by Google
- Microsoft's MLOps maturity model
- Databricks MLOps maturity assessment
