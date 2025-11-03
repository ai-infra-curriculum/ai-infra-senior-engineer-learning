# Lecture 04: ML-Specific Observability

## Learning Objectives

By the end of this lecture, you will be able to:

- Design ML observability systems monitoring model quality metrics (accuracy, precision, recall, AUC) in production using ground truth labels when available
- Implement data drift detection using statistical tests (KS test, PSI, Wasserstein distance) alerting when input distributions diverge from training data
- Configure model drift detection monitoring prediction distributions, confidence scores, and surrogate metrics detecting model degradation without labels
- Build feature store observability tracking feature staleness, null rates, outliers, and distribution shifts ensuring feature quality for inference
- Design training observability systems monitoring loss curves, gradient norms, GPU utilization, and data loading bottlenecks for large-scale training jobs
- Implement inference observability tracking latency percentiles (p50/p95/p99), throughput, batch size utilization, and model serving resource efficiency
- Architect ML metrics collection pipelines using custom Prometheus exporters, log-based metrics, and specialized ML monitoring tools (Evidently, WhyLabs)
- Build automated remediation workflows triggered by observability alerts including model retraining, automatic rollback, and circuit breaker activation

## Table of Contents
1. [Introduction](#introduction)
2. [Model Performance Monitoring](#model-performance-monitoring)
3. [Data Drift Detection](#data-drift-detection)
4. [Model Drift Detection](#model-drift-detection)
5. [Feature Store Observability](#feature-store-observability)
6. [A/B Testing Metrics](#ab-testing-metrics)
7. [Model Explainability](#model-explainability)
8. [Training Observability](#training-observability)
9. [Inference Observability](#inference-observability)
10. [ML Metrics Collection](#ml-metrics-collection)

## Introduction

Traditional observability focuses on infrastructure and application metrics. ML systems require additional observability layers to track model performance, data quality, and the health of the ML lifecycle. Poor model performance often stems not from infrastructure issues but from data drift, concept drift, or model degradation—problems that standard monitoring cannot detect.

### Why ML-Specific Observability Matters

**Unique ML Challenges**:
- Models degrade over time as data distributions change
- A healthy infrastructure doesn't guarantee accurate predictions
- Training metrics (accuracy on test set) don't always reflect production performance
- Data quality issues manifest as subtle prediction degradation
- Model behavior can change without code or infrastructure changes

**What to Monitor**:
- **Model quality**: Accuracy, precision, recall, F1, AUC-ROC
- **Data quality**: Feature distributions, missing values, outliers
- **Data drift**: Changes in input data distribution
- **Concept drift**: Changes in relationship between features and target
- **Prediction distribution**: Output distribution shifts
- **Business metrics**: Revenue impact, user satisfaction, conversion rates

## Model Performance Monitoring

### Online Metrics Collection

```python
# model_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# TODO: Define model performance metrics
predictions_total = Counter(
    'model_predictions_total',
    'Total predictions made',
    ['model_name', 'model_version', 'predicted_class']
)

prediction_confidence = Histogram(
    'model_prediction_confidence',
    'Prediction confidence scores',
    ['model_name', 'model_version'],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

model_accuracy = Gauge(
    'model_accuracy',
    'Model accuracy on recent predictions',
    ['model_name', 'model_version']
)

model_precision = Gauge(
    'model_precision',
    'Model precision on recent predictions',
    ['model_name', 'model_version', 'class']
)

model_recall = Gauge(
    'model_recall',
    'Model recall on recent predictions',
    ['model_name', 'model_version', 'class']
)

class ModelMonitor:
    def __init__(self, model_name, model_version, window_size=1000):
        self.model_name = model_name
        self.model_version = model_version
        self.window_size = window_size
        self.predictions_buffer = []
        self.labels_buffer = []

    # TODO: Record prediction and calculate metrics
    def record_prediction(self, prediction, confidence, label=None):
        """Record a prediction and optionally the ground truth label"""
        # Increment prediction counter
        predictions_total.labels(
            model_name=self.model_name,
            model_version=self.model_version,
            predicted_class=str(prediction)
        ).inc()

        # Record confidence
        prediction_confidence.labels(
            model_name=self.model_name,
            model_version=self.model_version
        ).observe(confidence)

        # If ground truth is available, calculate metrics
        if label is not None:
            self.predictions_buffer.append(prediction)
            self.labels_buffer.append(label)

            # Keep only recent predictions
            if len(self.predictions_buffer) > self.window_size:
                self.predictions_buffer.pop(0)
                self.labels_buffer.pop(0)

            # Calculate and update metrics
            if len(self.predictions_buffer) >= 100:  # Minimum samples
                self._update_metrics()

    def _update_metrics(self):
        """Calculate and update model performance metrics"""
        # TODO: Calculate accuracy
        accuracy = accuracy_score(self.labels_buffer, self.predictions_buffer)
        model_accuracy.labels(
            model_name=self.model_name,
            model_version=self.model_version
        ).set(accuracy)

        # TODO: Calculate per-class precision and recall
        unique_classes = set(self.labels_buffer)
        for cls in unique_classes:
            # Binary classification for this class
            y_true_binary = [1 if y == cls else 0 for y in self.labels_buffer]
            y_pred_binary = [1 if y == cls else 0 for y in self.predictions_buffer]

            precision = precision_score(y_true_binary, y_pred_binary, zero_division=0)
            recall = recall_score(y_true_binary, y_pred_binary, zero_division=0)

            model_precision.labels(
                model_name=self.model_name,
                model_version=self.model_version,
                class_name=str(cls)
            ).set(precision)

            model_recall.labels(
                model_name=self.model_name,
                model_version=self.model_version,
                class_name=str(cls)
            ).set(recall)

# Usage
monitor = ModelMonitor("sentiment-classifier", "v2.1")

# During inference
prediction = model.predict(features)
confidence = prediction.max()
monitor.record_prediction(
    prediction=prediction.argmax(),
    confidence=confidence,
    label=ground_truth  # May be available later via feedback loop
)
```

### Delayed Ground Truth Handling

Many ML systems don't have immediate ground truth. Solutions:

1. **Feedback loops**: Collect user feedback (thumbs up/down, corrections)
2. **Natural labels**: E.g., click-through rate for recommendations
3. **Periodic evaluation**: Use holdout dataset or production sample
4. **Proxy metrics**: Monitor related business metrics

```python
# delayed_feedback.py
import redis
from datetime import datetime, timedelta

# TODO: Handle delayed ground truth feedback
class FeedbackCollector:
    def __init__(self, redis_client):
        self.redis = redis_client

    def store_prediction(self, prediction_id, features, prediction, timestamp):
        """Store prediction for later evaluation"""
        # TODO: Store in Redis with expiration
        key = f"prediction:{prediction_id}"
        data = {
            "features": json.dumps(features),
            "prediction": prediction,
            "timestamp": timestamp
        }
        self.redis.hset(key, mapping=data)
        self.redis.expire(key, 30 * 24 * 3600)  # 30 days

    def record_feedback(self, prediction_id, actual_label):
        """Record ground truth when available"""
        # TODO: Retrieve prediction and calculate metrics
        key = f"prediction:{prediction_id}"
        prediction_data = self.redis.hgetall(key)

        if prediction_data:
            predicted = int(prediction_data["prediction"])
            correct = (predicted == actual_label)

            # Store evaluation result
            eval_key = f"evaluation:{datetime.now().strftime('%Y-%m-%d')}"
            self.redis.hincrby(eval_key, "total", 1)
            if correct:
                self.redis.hincrby(eval_key, "correct", 1)

            # Calculate daily accuracy
            total = int(self.redis.hget(eval_key, "total") or 0)
            correct_count = int(self.redis.hget(eval_key, "correct") or 0)
            accuracy = correct_count / total if total > 0 else 0

            # Update Prometheus gauge
            model_accuracy.labels(
                model_name="model_name",
                model_version="version"
            ).set(accuracy)
```

## Data Drift Detection

Data drift occurs when the distribution of input features changes over time.

### Statistical Tests for Drift

```python
# drift_detection.py
from scipy import stats
import numpy as np
from prometheus_client import Gauge

# TODO: Implement drift detection metrics
feature_drift_score = Gauge(
    'feature_drift_score',
    'Statistical drift score for features',
    ['feature_name', 'model_name']
)

class DriftDetector:
    def __init__(self, reference_data, model_name):
        """
        reference_data: Baseline feature distributions (training data)
        """
        self.reference_data = reference_data
        self.model_name = model_name
        self.feature_names = reference_data.columns

    # TODO: Detect drift using Kolmogorov-Smirnov test
    def detect_drift_ks(self, current_data):
        """Detect drift using Kolmogorov-Smirnov test"""
        drift_results = {}

        for feature in self.feature_names:
            # KS test compares two distributions
            statistic, p_value = stats.ks_2samp(
                self.reference_data[feature],
                current_data[feature]
            )

            drift_results[feature] = {
                "statistic": statistic,
                "p_value": p_value,
                "drifted": p_value < 0.05  # Significance level
            }

            # Update Prometheus metric
            feature_drift_score.labels(
                feature_name=feature,
                model_name=self.model_name
            ).set(statistic)

        return drift_results

    # TODO: Detect drift using Population Stability Index (PSI)
    def detect_drift_psi(self, current_data, num_bins=10):
        """Detect drift using Population Stability Index"""
        drift_results = {}

        for feature in self.feature_names:
            # Calculate PSI
            psi = self._calculate_psi(
                self.reference_data[feature],
                current_data[feature],
                num_bins
            )

            drift_results[feature] = {
                "psi": psi,
                "drifted": psi > 0.2  # PSI > 0.2 indicates significant drift
            }

            feature_drift_score.labels(
                feature_name=feature,
                model_name=self.model_name
            ).set(psi)

        return drift_results

    def _calculate_psi(self, reference, current, num_bins):
        """Calculate Population Stability Index"""
        # TODO: Implement PSI calculation
        # Create bins based on reference data
        bins = np.percentile(reference, np.linspace(0, 100, num_bins + 1))
        bins[0] = -np.inf
        bins[-1] = np.inf

        # Calculate distributions
        ref_dist, _ = np.histogram(reference, bins=bins)
        cur_dist, _ = np.histogram(current, bins=bins)

        # Normalize to get percentages
        ref_dist = ref_dist / len(reference)
        cur_dist = cur_dist / len(current)

        # Add small constant to avoid division by zero
        ref_dist = ref_dist + 0.0001
        cur_dist = cur_dist + 0.0001

        # Calculate PSI
        psi = np.sum((cur_dist - ref_dist) * np.log(cur_dist / ref_dist))

        return psi

    # TODO: Detect multivariate drift
    def detect_drift_multivariate(self, current_data):
        """Detect drift in multiple features simultaneously"""
        # Use Maximum Mean Discrepancy (MMD) or similar
        from sklearn.metrics.pairwise import rbf_kernel

        # Calculate kernel matrices
        K_ref = rbf_kernel(self.reference_data)
        K_cur = rbf_kernel(current_data)
        K_cross = rbf_kernel(self.reference_data, current_data)

        # Calculate MMD
        m = len(self.reference_data)
        n = len(current_data)

        mmd = (
            K_ref.sum() / (m * m) +
            K_cur.sum() / (n * n) -
            2 * K_cross.sum() / (m * n)
        )

        return {
            "mmd": mmd,
            "drifted": mmd > 0.01  # Threshold
        }
```

### Continuous Drift Monitoring

```python
# continuous_drift_monitoring.py
import pandas as pd
from datetime import datetime, timedelta

# TODO: Monitor drift continuously
class ContinuousDriftMonitor:
    def __init__(self, reference_data, model_name, window_hours=24):
        self.detector = DriftDetector(reference_data, model_name)
        self.window_hours = window_hours
        self.recent_predictions = []

    def add_prediction(self, features, prediction, timestamp):
        """Add a prediction to the monitoring window"""
        self.recent_predictions.append({
            "features": features,
            "prediction": prediction,
            "timestamp": timestamp
        })

        # Remove old predictions
        cutoff = datetime.now() - timedelta(hours=self.window_hours)
        self.recent_predictions = [
            p for p in self.recent_predictions
            if p["timestamp"] > cutoff
        ]

    def check_drift(self):
        """Check for drift in recent predictions"""
        if len(self.recent_predictions) < 100:
            return None  # Not enough data

        # Convert to DataFrame
        current_data = pd.DataFrame([
            p["features"] for p in self.recent_predictions
        ])

        # Detect drift
        drift_results = self.detector.detect_drift_psi(current_data)

        # Check if any feature has drifted
        drifted_features = [
            feature for feature, result in drift_results.items()
            if result["drifted"]
        ]

        if drifted_features:
            # TODO: Alert on drift
            print(f"DRIFT ALERT: Features {drifted_features} have drifted")
            return {
                "drifted": True,
                "features": drifted_features,
                "results": drift_results
            }

        return {"drifted": False, "results": drift_results}
```

## Model Drift Detection

Model drift (concept drift) occurs when the relationship between features and target changes.

```python
# model_drift_detection.py
from prometheus_client import Gauge

# TODO: Monitor model performance degradation
model_performance_degradation = Gauge(
    'model_performance_degradation',
    'Performance degradation compared to baseline',
    ['model_name', 'metric']
)

class ModelDriftDetector:
    def __init__(self, baseline_metrics, model_name):
        """
        baseline_metrics: Expected performance (from validation set)
        """
        self.baseline_metrics = baseline_metrics
        self.model_name = model_name

    def detect_performance_drift(self, current_metrics, threshold=0.05):
        """Detect significant performance degradation"""
        # TODO: Compare current vs baseline performance
        drift_detected = False
        results = {}

        for metric_name, baseline_value in self.baseline_metrics.items():
            current_value = current_metrics.get(metric_name, 0)
            degradation = (baseline_value - current_value) / baseline_value

            results[metric_name] = {
                "baseline": baseline_value,
                "current": current_value,
                "degradation": degradation,
                "drifted": degradation > threshold
            }

            # Update Prometheus
            model_performance_degradation.labels(
                model_name=self.model_name,
                metric=metric_name
            ).set(degradation)

            if degradation > threshold:
                drift_detected = True

        return {
            "drifted": drift_detected,
            "results": results
        }
```

## Feature Store Observability

Monitor feature freshness, availability, and quality.

```python
# feature_store_monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# TODO: Define feature store metrics
feature_retrieval_duration = Histogram(
    'feature_retrieval_duration_seconds',
    'Time to retrieve features',
    ['feature_set', 'source']
)

feature_cache_hit_rate = Gauge(
    'feature_cache_hit_rate',
    'Feature cache hit rate',
    ['feature_set']
)

feature_freshness_seconds = Gauge(
    'feature_freshness_seconds',
    'Age of feature values',
    ['feature_name']
)

feature_null_rate = Gauge(
    'feature_null_rate',
    'Percentage of null feature values',
    ['feature_name']
)

class FeatureStoreMonitor:
    def __init__(self):
        self.cache_hits = {}
        self.cache_misses = {}

    # TODO: Monitor feature retrieval
    def record_feature_retrieval(self, feature_set, source, duration, cache_hit):
        """Record feature retrieval metrics"""
        feature_retrieval_duration.labels(
            feature_set=feature_set,
            source=source
        ).observe(duration)

        # Update cache statistics
        if feature_set not in self.cache_hits:
            self.cache_hits[feature_set] = 0
            self.cache_misses[feature_set] = 0

        if cache_hit:
            self.cache_hits[feature_set] += 1
        else:
            self.cache_misses[feature_set] += 1

        # Calculate hit rate
        total = self.cache_hits[feature_set] + self.cache_misses[feature_set]
        hit_rate = self.cache_hits[feature_set] / total

        feature_cache_hit_rate.labels(
            feature_set=feature_set
        ).set(hit_rate)

    # TODO: Monitor feature quality
    def check_feature_quality(self, features_df):
        """Monitor feature quality metrics"""
        for column in features_df.columns:
            # Null rate
            null_rate = features_df[column].isnull().mean()
            feature_null_rate.labels(
                feature_name=column
            ).set(null_rate)

            # Freshness (if timestamp available)
            if f"{column}_timestamp" in features_df.columns:
                avg_age = (
                    datetime.now() - features_df[f"{column}_timestamp"]
                ).mean().total_seconds()

                feature_freshness_seconds.labels(
                    feature_name=column
                ).set(avg_age)
```

## A/B Testing Metrics

Track metrics for A/B tests between model versions.

```python
# ab_testing_metrics.py
from prometheus_client import Counter, Histogram

# TODO: Define A/B testing metrics
ab_test_requests = Counter(
    'ab_test_requests_total',
    'Total requests per variant',
    ['test_name', 'variant']
)

ab_test_conversions = Counter(
    'ab_test_conversions_total',
    'Conversions per variant',
    ['test_name', 'variant']
)

ab_test_latency = Histogram(
    'ab_test_latency_seconds',
    'Request latency per variant',
    ['test_name', 'variant']
)

class ABTestMonitor:
    def __init__(self, test_name):
        self.test_name = test_name

    # TODO: Record A/B test metrics
    def record_request(self, variant, latency, converted=False):
        """Record A/B test request"""
        ab_test_requests.labels(
            test_name=self.test_name,
            variant=variant
        ).inc()

        ab_test_latency.labels(
            test_name=self.test_name,
            variant=variant
        ).observe(latency)

        if converted:
            ab_test_conversions.labels(
                test_name=self.test_name,
                variant=variant
            ).inc()

# Usage
monitor = ABTestMonitor("model-v2-vs-v3")

# For each request
variant = assign_variant(user_id)  # "control" or "treatment"
start = time.time()
prediction = get_model(variant).predict(features)
latency = time.time() - start

monitor.record_request(
    variant=variant,
    latency=latency,
    converted=user_clicked  # Track business metric
)
```

## Model Explainability

Monitor model behavior and explanations.

```python
# model_explainability_monitoring.py
import shap
from prometheus_client import Histogram

# TODO: Monitor feature importance
feature_importance_score = Histogram(
    'feature_importance_score',
    'SHAP values for features',
    ['model_name', 'feature_name']
)

class ExplainabilityMonitor:
    def __init__(self, model, background_data, model_name):
        """Initialize SHAP explainer"""
        # TODO: Create SHAP explainer
        self.explainer = shap.Explainer(model, background_data)
        self.model_name = model_name

    def explain_prediction(self, features):
        """Generate explanation for prediction"""
        # TODO: Calculate SHAP values
        shap_values = self.explainer(features)

        # Record feature importance
        for i, feature_name in enumerate(features.columns):
            importance = abs(shap_values.values[0][i])
            feature_importance_score.labels(
                model_name=self.model_name,
                feature_name=feature_name
            ).observe(importance)

        return shap_values
```

## Training Observability

Monitor training jobs for performance and resource usage.

```python
# training_observability.py
from prometheus_client import Counter, Gauge, Histogram

# TODO: Define training metrics
training_epoch_duration = Histogram(
    'training_epoch_duration_seconds',
    'Time to complete training epoch',
    ['job_id']
)

training_loss = Gauge(
    'training_loss',
    'Current training loss',
    ['job_id', 'epoch']
)

training_gpu_utilization = Gauge(
    'training_gpu_utilization',
    'GPU utilization during training',
    ['job_id', 'gpu_id']
)

training_throughput = Gauge(
    'training_throughput_samples_per_second',
    'Training throughput',
    ['job_id']
)

class TrainingMonitor:
    def __init__(self, job_id):
        self.job_id = job_id

    # TODO: Monitor training progress
    def record_epoch(self, epoch, duration, loss, accuracy):
        """Record training epoch metrics"""
        training_epoch_duration.labels(
            job_id=self.job_id
        ).observe(duration)

        training_loss.labels(
            job_id=self.job_id,
            epoch=epoch
        ).set(loss)

    def record_gpu_utilization(self, gpu_id, utilization):
        """Record GPU utilization"""
        training_gpu_utilization.labels(
            job_id=self.job_id,
            gpu_id=str(gpu_id)
        ).set(utilization)

    def record_throughput(self, samples_per_second):
        """Record training throughput"""
        training_throughput.labels(
            job_id=self.job_id
        ).set(samples_per_second)
```

## Inference Observability

Monitor model serving and inference performance.

```python
# inference_observability.py
from prometheus_client import Counter, Histogram, Gauge

# TODO: Define inference metrics
inference_requests = Counter(
    'inference_requests_total',
    'Total inference requests',
    ['model_name', 'version', 'status']
)

inference_latency = Histogram(
    'inference_latency_seconds',
    'Inference latency',
    ['model_name', 'version', 'stage'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

batch_size = Histogram(
    'inference_batch_size',
    'Inference batch size',
    ['model_name', 'version']
)

class InferenceMonitor:
    def __init__(self, model_name, version):
        self.model_name = model_name
        self.version = version

    # TODO: Monitor inference requests
    def record_inference(self, preprocessing_time, inference_time,
                        postprocessing_time, batch_size_val, status="success"):
        """Record inference metrics"""
        inference_requests.labels(
            model_name=self.model_name,
            version=self.version,
            status=status
        ).inc()

        inference_latency.labels(
            model_name=self.model_name,
            version=self.version,
            stage="preprocessing"
        ).observe(preprocessing_time)

        inference_latency.labels(
            model_name=self.model_name,
            version=self.version,
            stage="inference"
        ).observe(inference_time)

        inference_latency.labels(
            model_name=self.model_name,
            version=self.version,
            stage="postprocessing"
        ).observe(postprocessing_time)

        batch_size.labels(
            model_name=self.model_name,
            version=self.version
        ).observe(batch_size_val)
```

## ML Metrics Collection

Comprehensive metrics collection framework.

```python
# ml_metrics_framework.py
from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class MLMetrics:
    """Comprehensive ML metrics"""
    # Model performance
    accuracy: float
    precision: Dict[str, float]
    recall: Dict[str, float]
    f1_score: Dict[str, float]

    # Data quality
    null_rate: Dict[str, float]
    outlier_rate: Dict[str, float]

    # Drift
    feature_drift_scores: Dict[str, float]
    performance_degradation: float

    # Operational
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput: float
    error_rate: float

    def to_prometheus(self):
        """Export metrics to Prometheus"""
        # TODO: Update all Prometheus gauges/counters
        pass

    def to_json(self):
        """Export as JSON for logging"""
        return json.dumps(self.__dict__, default=str)

    def alert_check(self) -> Dict[str, Any]:
        """Check if any metrics violate thresholds"""
        alerts = {}

        # TODO: Implement alerting logic
        if self.accuracy < 0.85:
            alerts['accuracy'] = f"Accuracy dropped to {self.accuracy}"

        if self.performance_degradation > 0.1:
            alerts['degradation'] = f"Performance degraded by {self.performance_degradation * 100}%"

        if self.p99_latency_ms > 1000:
            alerts['latency'] = f"P99 latency is {self.p99_latency_ms}ms"

        return alerts
```

## Summary

ML-specific observability is critical for production ML systems:
- Monitor model performance, not just infrastructure
- Detect data drift and concept drift early
- Track feature quality and freshness
- Implement comprehensive A/B testing
- Monitor both training and inference
- Alert on model degradation

These techniques enable:
- Early detection of model issues
- Data-driven model updates
- Improved model reliability
- Better understanding of model behavior

In the next lecture, we'll explore SRE principles for ML systems.

## Further Reading

- "Monitoring Machine Learning Models in Production" by Google
- "Hidden Technical Debt in Machine Learning Systems" (Google Research)
- [Evidently AI Documentation](https://docs.evidentlyai.com/)
- [WhyLabs Documentation](https://docs.whylabs.ai/)
- "Machine Learning Design Patterns" by Lakshmanan, Robinson, Munn
