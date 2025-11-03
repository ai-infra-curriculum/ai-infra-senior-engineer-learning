# Lecture 04: Advanced Experiment Tracking

## Learning Objectives

By the end of this lecture, you will be able to:

- Design comprehensive experiment tracking systems using MLflow, Weights & Biases, or Neptune capturing hyperparameters, metrics, artifacts, code versions, and system metrics
- Implement distributed hyperparameter optimization using Optuna, Ray Tune, or Hyperopt parallelizing thousands of experiments across GPUs with early stopping and resource management
- Architect reproducible experiment workflows ensuring exact replication through environment snapshots, data versioning, random seed management, and code version pinning
- Configure automated experiment comparison and analysis creating leaderboards, metric visualizations, hyperparameter importance analysis, and experiment diff tools
- Design experiment organization strategies using hierarchical projects, tags, and naming conventions enabling efficient search and collaboration across teams
- Implement experiment metadata enrichment capturing infrastructure costs, carbon footprint, training duration, and resource utilization for cost optimization analysis
- Build experiment monitoring dashboards providing real-time experiment progress tracking, resource utilization, and automated alerting for failed or stalled experiments
- Architect experiment lifecycle management with automated cleanup of old experiments, archival of important runs, and retention policies balancing storage costs with reproducibility needs

## Overview

Experiment tracking is the systematic recording of machine learning experiments including hyperparameters, metrics, artifacts, and code versions. Proper experiment tracking enables reproducibility, collaboration, and informed decision-making.

## Experiment Tracking Fundamentals

### What to Track

**Essential Information:**
1. **Hyperparameters**: All model and training configuration
2. **Metrics**: Performance measurements over time
3. **Artifacts**: Models, plots, data samples
4. **System Metrics**: Training time, memory usage, GPU utilization
5. **Code Version**: Git commit, branch, repository
6. **Environment**: Dependencies, package versions
7. **Data Version**: Dataset version, data hash
8. **Random Seeds**: For reproducibility

### Experiment Tracking Tools Comparison

| Tool | Pros | Cons | Best For |
|------|------|------|----------|
| MLflow | Open source, flexible, self-hosted | UI basic, limited collaboration | Teams wanting control |
| Weights & Biases | Rich UI, great collaboration | Cloud-based, cost | Research teams |
| Neptune.ai | Enterprise features, versioning | Commercial | Large organizations |
| TensorBoard | PyTorch/TF integration | Limited metadata | Deep learning experiments |
| Comet.ml | Good UI, experiment comparison | Cloud-based | Small to medium teams |

---

## Advanced MLflow Tracking

### Comprehensive Experiment Setup

```python
# experiments/advanced_experiment_tracker.py
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import logging
import psutil
import GPUtil
from contextlib import contextmanager
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedExperimentTracker:
    def __init__(self, experiment_name, tracking_uri="http://localhost:5000"):
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.client = MlflowClient()

    @contextmanager
    def track_resources(self):
        """Context manager to track system resources"""
        start_time = time.time()

        # Initial resource measurements
        start_memory = psutil.virtual_memory().used / (1024 ** 3)  # GB
        start_gpu_memory = self._get_gpu_memory()

        yield

        # Final measurements
        end_time = time.time()
        end_memory = psutil.virtual_memory().used / (1024 ** 3)
        end_gpu_memory = self._get_gpu_memory()

        # Log resource metrics
        mlflow.log_metric("training_time_seconds", end_time - start_time)
        mlflow.log_metric("peak_memory_gb", end_memory)
        mlflow.log_metric("memory_delta_gb", end_memory - start_memory)

        if end_gpu_memory is not None:
            mlflow.log_metric("peak_gpu_memory_gb", end_gpu_memory)

    def _get_gpu_memory(self):
        """Get current GPU memory usage"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].memoryUsed / 1024  # Convert MB to GB
        except:
            pass
        return None

    def log_dataset_info(self, X_train, X_test, y_train, y_test):
        """Log comprehensive dataset information"""
        dataset_info = {
            'n_train_samples': len(X_train),
            'n_test_samples': len(X_test),
            'n_features': X_train.shape[1],
            'n_classes': len(np.unique(y_train)),
            'train_class_distribution': dict(zip(*np.unique(y_train, return_counts=True))),
            'test_class_distribution': dict(zip(*np.unique(y_test, return_counts=True))),
            'feature_names': list(X_train.columns) if hasattr(X_train, 'columns') else None
        }

        # Log as parameters and artifacts
        mlflow.log_params({
            'n_train_samples': dataset_info['n_train_samples'],
            'n_test_samples': dataset_info['n_test_samples'],
            'n_features': dataset_info['n_features'],
            'n_classes': dataset_info['n_classes']
        })

        # Save complete info as artifact
        with open('dataset_info.json', 'w') as f:
            json.dump(dataset_info, f, indent=2, default=str)
        mlflow.log_artifact('dataset_info.json')

    def log_feature_importance(self, model, feature_names=None):
        """Log and visualize feature importance"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_

            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(len(importance))]

            # Create DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)

            # Log top 20 as parameters
            for idx, row in importance_df.head(20).iterrows():
                mlflow.log_metric(f"importance_{row['feature']}", row['importance'])

            # Create visualization
            plt.figure(figsize=(10, 8))
            sns.barplot(data=importance_df.head(20), x='importance', y='feature')
            plt.title('Top 20 Feature Importances')
            plt.tight_layout()
            plt.savefig('feature_importance.png')
            mlflow.log_artifact('feature_importance.png')
            plt.close()

            # Log full importance as CSV
            importance_df.to_csv('feature_importance.csv', index=False)
            mlflow.log_artifact('feature_importance.csv')

    def log_confusion_matrix(self, y_true, y_pred, labels=None):
        """Log confusion matrix visualization"""
        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        mlflow.log_artifact('confusion_matrix.png')
        plt.close()

        # Log as metrics
        for i, label in enumerate(labels or range(len(cm))):
            for j in range(len(cm)):
                mlflow.log_metric(f"cm_{label}_{j}", int(cm[i][j]))

    def log_classification_report(self, y_true, y_pred, labels=None):
        """Log detailed classification report"""
        report = classification_report(y_true, y_pred, output_dict=True)

        # Log per-class metrics
        for label, metrics in report.items():
            if isinstance(metrics, dict):
                for metric_name, value in metrics.items():
                    mlflow.log_metric(f"{label}_{metric_name}", value)

        # Save full report
        report_text = classification_report(y_true, y_pred, target_names=labels)
        with open('classification_report.txt', 'w') as f:
            f.write(report_text)
        mlflow.log_artifact('classification_report.txt')

    def log_learning_curves(self, model, X_train, y_train):
        """Log learning curves for model"""
        from sklearn.model_selection import learning_curve

        train_sizes, train_scores, val_scores = learning_curve(
            model, X_train, y_train,
            train_sizes=np.linspace(0.1, 1.0, 10),
            cv=5,
            n_jobs=-1
        )

        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)

        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes, train_mean, label='Training score', color='blue')
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='blue')
        plt.plot(train_sizes, val_mean, label='Cross-validation score', color='red')
        plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='red')

        plt.xlabel('Training Set Size')
        plt.ylabel('Score')
        plt.title('Learning Curves')
        plt.legend(loc='best')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('learning_curves.png')
        mlflow.log_artifact('learning_curves.png')
        plt.close()

    def run_experiment(self, model, model_name, X_train, X_test, y_train, y_test, hyperparams, tags=None):
        """Run comprehensive experiment with full tracking"""
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log model type and hyperparameters
            mlflow.log_param("model_type", model_name)
            mlflow.log_params(hyperparams)

            # Log dataset info
            self.log_dataset_info(X_train, X_test, y_train, y_test)

            # Track resources during training
            with self.track_resources():
                # Train model
                logger.info(f"Training {model_name}...")
                model.fit(X_train, y_train)

            # Evaluate on training set
            train_pred = model.predict(X_train)
            train_metrics = {
                'train_accuracy': accuracy_score(y_train, train_pred),
                'train_precision': precision_score(y_train, train_pred, average='weighted'),
                'train_recall': recall_score(y_train, train_pred, average='weighted'),
                'train_f1': f1_score(y_train, train_pred, average='weighted')
            }

            # Evaluate on test set
            test_pred = model.predict(X_test)
            test_metrics = {
                'test_accuracy': accuracy_score(y_test, test_pred),
                'test_precision': precision_score(y_test, test_pred, average='weighted'),
                'test_recall': recall_score(y_test, test_pred, average='weighted'),
                'test_f1': f1_score(y_test, test_pred, average='weighted')
            }

            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, n_jobs=-1)
            cv_metrics = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_min': cv_scores.min(),
                'cv_max': cv_scores.max()
            }

            # Calculate overfitting metric
            overfitting_score = train_metrics['train_accuracy'] - test_metrics['test_accuracy']

            # Log all metrics
            all_metrics = {**train_metrics, **test_metrics, **cv_metrics, 'overfitting_score': overfitting_score}
            mlflow.log_metrics(all_metrics)

            # Log visualizations
            self.log_confusion_matrix(y_test, test_pred)
            self.log_classification_report(y_test, test_pred)
            self.log_feature_importance(model, X_train.columns if hasattr(X_train, 'columns') else None)
            self.log_learning_curves(model, X_train, y_train)

            # Log model
            mlflow.sklearn.log_model(model, "model")

            # Add tags
            if tags:
                mlflow.set_tags(tags)

            mlflow.set_tag("training_complete", "true")

            logger.info(f"Experiment complete. Test accuracy: {test_metrics['test_accuracy']:.3f}")

            return all_metrics

# Usage example
if __name__ == '__main__':
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

    # Generate sample data
    X, y = make_classification(n_samples=10000, n_features=20, n_informative=15,
                               n_redundant=5, random_state=42)
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(20)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize tracker
    tracker = AdvancedExperimentTracker("advanced_classification_experiments")

    # Run experiments with different models
    models = [
        (RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
         "random_forest",
         {'n_estimators': 100, 'max_depth': 10}),

        (GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42),
         "gradient_boosting",
         {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1}),

        (LogisticRegression(max_iter=1000, random_state=42),
         "logistic_regression",
         {'max_iter': 1000})
    ]

    for model, name, params in models:
        tracker.run_experiment(model, name, X_train, X_test, y_train, y_test, params,
                             tags={'experiment_batch': 'baseline_comparison'})
```

---

## Hyperparameter Optimization

### Grid Search with Tracking

```python
# experiments/hyperparam_optimization.py
import mlflow
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class TrackedHyperparamSearch:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)

    def grid_search_with_tracking(self, model, param_grid, X_train, y_train, cv=5):
        """Grid search with MLflow tracking"""
        with mlflow.start_run(run_name="grid_search_parent"):
            mlflow.log_param("search_type", "grid_search")
            mlflow.log_param("cv_folds", cv)
            mlflow.log_dict(param_grid, "param_grid.json")

            # Perform grid search
            grid_search = GridSearchCV(model, param_grid, cv=cv, n_jobs=-1, verbose=1)
            grid_search.fit(X_train, y_train)

            # Log results for each parameter combination
            for i, params in enumerate(grid_search.cv_results_['params']):
                with mlflow.start_run(run_name=f"config_{i}", nested=True):
                    # Log parameters
                    mlflow.log_params(params)

                    # Log metrics
                    mlflow.log_metric("mean_test_score", grid_search.cv_results_['mean_test_score'][i])
                    mlflow.log_metric("std_test_score", grid_search.cv_results_['std_test_score'][i])
                    mlflow.log_metric("mean_fit_time", grid_search.cv_results_['mean_fit_time'][i])

            # Log best results
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("best_score", grid_search.best_score_)
            mlflow.sklearn.log_model(grid_search.best_estimator_, "best_model")

            return grid_search

# Usage
tracker = TrackedHyperparamSearch("hyperparameter_tuning")

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

best_model = tracker.grid_search_with_tracking(
    RandomForestClassifier(random_state=42),
    param_grid,
    X_train,
    y_train
)
```

### Bayesian Optimization with Optuna

```python
# experiments/bayesian_optimization.py
import optuna
from optuna.integration.mlflow import MLflowCallback
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

class OptunaMLflowOptimizer:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)

    def objective(self, trial, X_train, y_train):
        """Optuna objective function"""
        # Define hyperparameter search space
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
            'random_state': 42
        }

        # Train model
        model = RandomForestClassifier(**params)

        # Cross-validation score
        score = cross_val_score(model, X_train, y_train, cv=5, n_jobs=-1).mean()

        return score

    def optimize(self, X_train, y_train, n_trials=100):
        """Run Bayesian optimization"""
        # Create MLflow callback
        mlflc = MLflowCallback(
            tracking_uri=mlflow.get_tracking_uri(),
            metric_name="cv_score"
        )

        # Create study
        study = optuna.create_study(direction='maximize')

        # Optimize
        study.optimize(
            lambda trial: self.objective(trial, X_train, y_train),
            n_trials=n_trials,
            callbacks=[mlflc]
        )

        # Log best results
        with mlflow.start_run(run_name="best_params"):
            mlflow.log_params(study.best_params)
            mlflow.log_metric("best_cv_score", study.best_value)

            # Train final model with best params
            best_model = RandomForestClassifier(**study.best_params)
            best_model.fit(X_train, y_train)
            mlflow.sklearn.log_model(best_model, "best_model")

        return study

# Usage
optimizer = OptunaMLflowOptimizer("bayesian_optimization")
study = optimizer.optimize(X_train, y_train, n_trials=50)
```

---

## Distributed Experiment Tracking

### Parallel Experiments

```python
# experiments/parallel_experiments.py
import mlflow
from joblib import Parallel, delayed
from sklearn.model_selection import ParameterGrid
import logging

logger = logging.getLogger(__name__)

class ParallelExperimentRunner:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)

    def run_single_experiment(self, config, X_train, X_test, y_train, y_test):
        """Run a single experiment configuration"""
        with mlflow.start_run(run_name=f"config_{config['id']}"):
            try:
                # Log configuration
                mlflow.log_params(config['params'])

                # Train model
                model = config['model_class'](**config['params'])
                model.fit(X_train, y_train)

                # Evaluate
                train_score = model.score(X_train, y_train)
                test_score = model.score(X_test, y_test)

                mlflow.log_metric("train_score", train_score)
                mlflow.log_metric("test_score", test_score)

                # Save model
                mlflow.sklearn.log_model(model, "model")

                logger.info(f"Completed config {config['id']}: test_score={test_score:.3f}")

                return test_score

            except Exception as e:
                logger.error(f"Error in config {config['id']}: {str(e)}")
                mlflow.log_param("error", str(e))
                return None

    def run_parallel_experiments(self, configurations, X_train, X_test, y_train, y_test, n_jobs=-1):
        """Run multiple experiments in parallel"""
        logger.info(f"Running {len(configurations)} experiments in parallel")

        # Run experiments in parallel
        results = Parallel(n_jobs=n_jobs)(
            delayed(self.run_single_experiment)(config, X_train, X_test, y_train, y_test)
            for config in configurations
        )

        logger.info("All experiments completed")

        return results

# Usage
runner = ParallelExperimentRunner("parallel_experiments")

# Define configurations
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15]
}

configurations = [
    {
        'id': i,
        'model_class': RandomForestClassifier,
        'params': {**params, 'random_state': 42}
    }
    for i, params in enumerate(ParameterGrid(param_grid))
]

results = runner.run_parallel_experiments(configurations, X_train, X_test, y_train, y_test)
```

---

## Experiment Analysis

### Comparing Experiments

```python
# experiments/experiment_analysis.py
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ExperimentAnalyzer:
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.client = MlflowClient()

        # Get experiment
        self.experiment = self.client.get_experiment_by_name(experiment_name)

    def get_all_runs(self, filter_string=""):
        """Get all runs from experiment"""
        runs = self.client.search_runs(
            experiment_ids=[self.experiment.experiment_id],
            filter_string=filter_string,
            order_by=["metrics.test_accuracy DESC"]
        )

        return runs

    def create_comparison_dataframe(self):
        """Create DataFrame comparing all runs"""
        runs = self.get_all_runs()

        data = []
        for run in runs:
            row = {
                'run_id': run.info.run_id,
                'run_name': run.data.tags.get('mlflow.runName', ''),
                'status': run.info.status,
                **run.data.params,
                **run.data.metrics
            }
            data.append(row)

        df = pd.DataFrame(data)
        return df

    def plot_metric_comparison(self, metric_name, top_n=10):
        """Plot comparison of specific metric across runs"""
        df = self.create_comparison_dataframe()

        # Sort and get top N
        df_sorted = df.sort_values(metric_name, ascending=False).head(top_n)

        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_sorted, x='run_name', y=metric_name)
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Top {top_n} Runs by {metric_name}')
        plt.tight_layout()
        plt.savefig(f'{metric_name}_comparison.png')
        plt.show()

    def find_best_run(self, metric_name, mode='max'):
        """Find best run by metric"""
        runs = self.get_all_runs()

        best_run = None
        best_value = float('-inf') if mode == 'max' else float('inf')

        for run in runs:
            value = run.data.metrics.get(metric_name)
            if value is not None:
                if (mode == 'max' and value > best_value) or (mode == 'min' and value < best_value):
                    best_value = value
                    best_run = run

        return best_run, best_value

# Usage
analyzer = ExperimentAnalyzer("advanced_classification_experiments")

# Get comparison DataFrame
df = analyzer.create_comparison_dataframe()
print(df.head())

# Plot comparisons
analyzer.plot_metric_comparison('test_accuracy')

# Find best run
best_run, best_score = analyzer.find_best_run('test_accuracy')
print(f"Best run: {best_run.info.run_id}, Score: {best_score:.3f}")
```

---

## Key Takeaways

1. **Track Everything**: Hyperparameters, metrics, artifacts, system resources
2. **Reproducibility**: Log code versions, dependencies, random seeds
3. **Visualization**: Create plots and reports for better understanding
4. **Comparison**: Systematically compare experiments to find best models
5. **Automation**: Use tools to automate tracking and analysis

## Exercises

1. Implement comprehensive experiment tracking for your ML project
2. Run hyperparameter optimization with Optuna and MLflow
3. Create automated experiment comparison dashboard
4. Implement parallel experiment execution
5. Build experiment analysis and visualization tools

## Additional Resources

- MLflow Tracking documentation
- Optuna documentation
- "Experiment Tracking for Machine Learning" by Neptune.ai
- Weights & Biases tutorials
