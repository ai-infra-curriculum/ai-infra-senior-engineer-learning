# Lecture 08: Production ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design production ML architectures with proper separation of concerns including feature service, prediction service, model registry, and monitoring systems
- Implement reliability patterns including circuit breakers, retries with exponential backoff, fallback models, and graceful degradation for fault tolerance
- Architect model retraining strategies using scheduled retraining, trigger-based retraining (drift detection), and continuous training with online learning
- Configure production monitoring tracking model performance metrics, system health (latency/throughput/errors), data quality, and business impact
- Design debugging workflows for production ML issues using logging, profiling, A/B test analysis, and feature attribution to identify root causes
- Implement incident response procedures with runbooks, escalation paths, automated rollback, and post-incident reviews for continuous improvement
- Build model versioning and rollback capabilities enabling instant revert to previous stable version with proper traffic management and state consistency
- Architect data validation and quality checks preventing bad data from reaching models using schema validation, statistical tests, and anomaly detection

## Overview

Production ML systems require careful design to handle real-world challenges: data drift, concept drift, system failures, scalability issues, and changing business requirements. This lecture covers patterns and anti-patterns for building reliable ML systems.

## Production ML Architecture

### End-to-End System

```
┌──────────────────────────────────────────────────────────┐
│            Production ML System Architecture              │
└──────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐
│   Client    │────────▶│  API        │
│   Apps      │         │  Gateway    │
└─────────────┘         └─────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │Prediction│  │  Feature │  │   Model  │
        │ Service  │─▶│  Service │  │ Registry │
        └──────────┘  └──────────┘  └──────────┘
                │              │              │
                └──────────────┴──────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │Monitoring│  │  Logging │  │  Metrics │
        │ & Alerts │  │  System  │  │   Store  │
        └──────────┘  └──────────┘  └──────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │   Retraining    │
                    │   Pipeline      │
                    └─────────────────┘
```

---

## Production ML Patterns

### 1. Prediction Caching

**Problem**: Repeated predictions for same inputs waste resources

```python
# patterns/prediction_cache.py
import redis
import hashlib
import json
import pickle
from functools import wraps
from typing import Any, Callable

class PredictionCache:
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def cache_key(self, features: dict, model_version: str) -> str:
        """Generate cache key from features and model version"""
        # Sort features for consistent hashing
        feature_str = json.dumps(features, sort_keys=True)
        key_data = f"{model_version}:{feature_str}"
        return f"pred:{hashlib.md5(key_data.encode()).hexdigest()}"

    def get(self, features: dict, model_version: str) -> Any:
        """Get cached prediction"""
        key = self.cache_key(features, model_version)
        cached = self.redis.get(key)

        if cached:
            return pickle.loads(cached)
        return None

    def set(self, features: dict, model_version: str, prediction: Any):
        """Cache prediction"""
        key = self.cache_key(features, model_version)
        self.redis.setex(key, self.ttl, pickle.dumps(prediction))

def cached_prediction(cache: PredictionCache):
    """Decorator for caching predictions"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(features: dict, model_version: str, *args, **kwargs):
            # Check cache
            cached = cache.get(features, model_version)
            if cached is not None:
                return cached

            # Compute prediction
            prediction = func(features, model_version, *args, **kwargs)

            # Cache result
            cache.set(features, model_version, prediction)

            return prediction
        return wrapper
    return decorator

# Usage
cache = PredictionCache(redis.Redis(host='localhost', port=6379))

@cached_prediction(cache)
def predict(features: dict, model_version: str):
    # Expensive prediction
    return model.predict(features)
```

### 2. Circuit Breaker

**Problem**: Cascading failures from dependent services

```python
# patterns/circuit_breaker.py
import time
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: int = 60  # seconds

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failures = 0

        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.successes = 0
                logger.info("Circuit breaker CLOSED after successful recovery")

    def _on_failure(self):
        """Handle failed call"""
        self.failures += 1
        self.last_failure_time = time.time()
        self.successes = 0

        if self.failures >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker OPEN after {self.failures} failures")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.config.timeout

# Usage
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    timeout=60
))

def get_features_from_service(user_id):
    """External service call protected by circuit breaker"""
    return circuit_breaker.call(
        requests.get,
        f"http://feature-service/features/{user_id}"
    )
```

### 3. Graceful Degradation

**Problem**: Complete service failure when models unavailable

```python
# patterns/graceful_degradation.py
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, primary_model, fallback_model=None, default_prediction=None):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.default_prediction = default_prediction

    def predict(self, features: dict) -> dict:
        """Predict with graceful degradation"""
        try:
            # Try primary model
            prediction = self.primary_model.predict(features)
            return {
                'prediction': prediction,
                'model': 'primary',
                'confidence': 'high'
            }
        except Exception as e:
            logger.error(f"Primary model failed: {str(e)}")

            # Try fallback model
            if self.fallback_model:
                try:
                    prediction = self.fallback_model.predict(features)
                    logger.warning("Using fallback model")
                    return {
                        'prediction': prediction,
                        'model': 'fallback',
                        'confidence': 'medium'
                    }
                except Exception as e2:
                    logger.error(f"Fallback model failed: {str(e2)}")

            # Use default/rule-based prediction
            if self.default_prediction:
                logger.warning("Using default prediction")
                return {
                    'prediction': self.default_prediction(features),
                    'model': 'default',
                    'confidence': 'low'
                }

            # Last resort: return error
            raise Exception("All prediction methods failed")
```

### 4. Model Versioning in Serving

**Problem**: Rolling updates causing inconsistent predictions

```python
# patterns/versioned_serving.py
from typing import Dict
import threading

class VersionedModelServer:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.default_version = None
        self.lock = threading.RLock()

    def load_model(self, version: str, model: Any):
        """Load new model version"""
        with self.lock:
            self.models[version] = model
            logger.info(f"Loaded model version {version}")

    def set_default_version(self, version: str):
        """Set default model version"""
        with self.lock:
            if version not in self.models:
                raise ValueError(f"Model version {version} not loaded")
            self.default_version = version
            logger.info(f"Set default version to {version}")

    def predict(self, features: dict, version: Optional[str] = None) -> Any:
        """Predict with specified or default version"""
        with self.lock:
            if version is None:
                version = self.default_version

            if version not in self.models:
                raise ValueError(f"Model version {version} not found")

            model = self.models[version]

        return model.predict(features)

    def unload_model(self, version: str):
        """Remove old model version"""
        with self.lock:
            if version == self.default_version:
                raise ValueError("Cannot unload default version")

            if version in self.models:
                del self.models[version]
                logger.info(f"Unloaded model version {version}")

# Usage
server = VersionedModelServer()

# Load multiple versions
server.load_model("v1.0", model_v1)
server.load_model("v2.0", model_v2)

# Set active version
server.set_default_version("v2.0")

# Predict (uses v2.0)
prediction = server.predict(features)

# Predict with specific version
prediction_v1 = server.predict(features, version="v1.0")
```

---

## Data and Concept Drift Detection

### Monitoring Data Distribution

```python
# monitoring/drift_detection.py
import numpy as np
from scipy import stats
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, reference_data: np.ndarray, feature_names: List[str]):
        self.reference_data = reference_data
        self.feature_names = feature_names

        # Compute reference statistics
        self.reference_stats = self._compute_statistics(reference_data)

    def _compute_statistics(self, data: np.ndarray) -> Dict:
        """Compute statistical summary"""
        return {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0),
            'quantiles': np.percentile(data, [25, 50, 75], axis=0)
        }

    def detect_drift(self, current_data: np.ndarray, alpha: float = 0.05) -> Dict:
        """Detect drift using statistical tests"""
        results = {}

        for i, feature_name in enumerate(self.feature_names):
            reference_feature = self.reference_data[:, i]
            current_feature = current_data[:, i]

            # Kolmogorov-Smirnov test
            statistic, pvalue = stats.ks_2samp(reference_feature, current_feature)

            drift_detected = pvalue < alpha

            results[feature_name] = {
                'drift_detected': drift_detected,
                'p_value': pvalue,
                'statistic': statistic,
                'reference_mean': self.reference_stats['mean'][i],
                'current_mean': np.mean(current_feature),
                'reference_std': self.reference_stats['std'][i],
                'current_std': np.std(current_feature)
            }

            if drift_detected:
                logger.warning(
                    f"Drift detected in feature {feature_name}: "
                    f"p-value={pvalue:.4f}"
                )

        return results

# Usage
detector = DriftDetector(training_data, feature_names)

# Check production data periodically
drift_results = detector.detect_drift(production_data)

# Alert if drift detected
for feature, result in drift_results.items():
    if result['drift_detected']:
        send_alert(f"Data drift detected in {feature}")
```

### Prediction Drift Monitoring

```python
# monitoring/prediction_drift.py
import numpy as np
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PredictionDriftMonitor:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)

        # Baseline statistics (from validation set)
        self.baseline_mean = None
        self.baseline_std = None

    def set_baseline(self, predictions: np.ndarray):
        """Set baseline statistics from validation set"""
        self.baseline_mean = np.mean(predictions)
        self.baseline_std = np.std(predictions)

    def add_prediction(self, prediction: float):
        """Add new prediction to window"""
        self.predictions.append(prediction)
        self.timestamps.append(datetime.now())

    def check_drift(self, threshold: float = 0.1) -> bool:
        """Check if prediction distribution has drifted"""
        if len(self.predictions) < self.window_size:
            return False  # Not enough data yet

        current_mean = np.mean(self.predictions)
        current_std = np.std(self.predictions)

        # Check if mean has shifted significantly
        mean_shift = abs(current_mean - self.baseline_mean) / self.baseline_std

        if mean_shift > threshold:
            logger.warning(
                f"Prediction drift detected: "
                f"baseline_mean={self.baseline_mean:.3f}, "
                f"current_mean={current_mean:.3f}, "
                f"shift={mean_shift:.3f}"
            )
            return True

        return False

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        if not self.predictions:
            return {}

        return {
            'count': len(self.predictions),
            'mean': np.mean(self.predictions),
            'std': np.std(self.predictions),
            'min': np.min(self.predictions),
            'max': np.max(self.predictions),
            'baseline_mean': self.baseline_mean,
            'baseline_std': self.baseline_std
        }
```

---

## Automated Retraining

### Retraining Triggers

```python
# retraining/trigger_system.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    SCHEDULED = "scheduled"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    MANUAL = "manual"

@dataclass
class RetrainingTrigger:
    trigger_type: TriggerType
    timestamp: datetime
    metadata: dict

class RetrainingOrchestrator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.last_training = datetime.now()

        # Thresholds
        self.performance_threshold = 0.80  # Min accuracy
        self.drift_threshold = 0.05  # Max drift score
        self.min_days_between_training = 7

    def check_triggers(self, metrics: dict) -> Optional[RetrainingTrigger]:
        """Check if retraining should be triggered"""

        # Check scheduled retraining
        if self._should_retrain_scheduled():
            return RetrainingTrigger(
                trigger_type=TriggerType.SCHEDULED,
                timestamp=datetime.now(),
                metadata={'reason': 'scheduled_retraining'}
            )

        # Check performance degradation
        if metrics.get('accuracy', 1.0) < self.performance_threshold:
            return RetrainingTrigger(
                trigger_type=TriggerType.PERFORMANCE_DEGRADATION,
                timestamp=datetime.now(),
                metadata={
                    'current_accuracy': metrics['accuracy'],
                    'threshold': self.performance_threshold
                }
            )

        # Check data drift
        if metrics.get('drift_score', 0.0) > self.drift_threshold:
            return RetrainingTrigger(
                trigger_type=TriggerType.DATA_DRIFT,
                timestamp=datetime.now(),
                metadata={
                    'drift_score': metrics['drift_score'],
                    'threshold': self.drift_threshold
                }
            )

        return None

    def _should_retrain_scheduled(self) -> bool:
        """Check if scheduled retraining is due"""
        days_since_training = (datetime.now() - self.last_training).days
        return days_since_training >= self.min_days_between_training

    def trigger_retraining(self, trigger: RetrainingTrigger):
        """Trigger retraining pipeline"""
        logger.info(
            f"Triggering retraining for {self.model_name}: "
            f"{trigger.trigger_type.value}"
        )

        # Submit retraining job
        job_id = submit_training_job(
            model_name=self.model_name,
            trigger_type=trigger.trigger_type,
            metadata=trigger.metadata
        )

        self.last_training = datetime.now()

        return job_id
```

---

## Production Debugging

### Prediction Logging

```python
# debugging/prediction_logger.py
import json
from datetime import datetime
from typing import Any, Dict
import uuid

class PredictionLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file

    def log_prediction(
        self,
        request_id: str,
        features: Dict,
        prediction: Any,
        model_version: str,
        latency_ms: float,
        metadata: Dict = None
    ):
        """Log prediction for debugging"""
        log_entry = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'prediction': prediction,
            'model_version': model_version,
            'latency_ms': latency_ms,
            'metadata': metadata or {}
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

# Prediction service with logging
class DebugablePredictionService:
    def __init__(self, model, logger: PredictionLogger):
        self.model = model
        self.logger = logger

    def predict(self, features: dict) -> dict:
        """Make prediction with comprehensive logging"""
        request_id = str(uuid.uuid4())

        start_time = time.time()

        try:
            prediction = self.model.predict(features)
            latency_ms = (time.time() - start_time) * 1000

            # Log successful prediction
            self.logger.log_prediction(
                request_id=request_id,
                features=features,
                prediction=prediction,
                model_version=self.model.version,
                latency_ms=latency_ms,
                metadata={'status': 'success'}
            )

            return {
                'request_id': request_id,
                'prediction': prediction,
                'latency_ms': latency_ms
            }

        except Exception as e:
            # Log failed prediction
            self.logger.log_prediction(
                request_id=request_id,
                features=features,
                prediction=None,
                model_version=self.model.version,
                latency_ms=(time.time() - start_time) * 1000,
                metadata={'status': 'error', 'error': str(e)}
            )
            raise
```

---

## Production Anti-Patterns

### Anti-Pattern 1: No Monitoring

**Problem**: Can't detect when models degrade
**Solution**: Comprehensive monitoring of metrics, drift, performance

### Anti-Pattern 2: Tight Coupling

**Problem**: Model changes require service redeployment
**Solution**: Decouple models from serving infrastructure

### Anti-Pattern 3: No Rollback Plan

**Problem**: Can't quickly revert bad deployments
**Solution**: Blue-green or canary deployments with automated rollback

### Anti-Pattern 4: Ignoring Data Quality

**Problem**: Bad input data produces bad predictions
**Solution**: Input validation, data quality checks

### Anti-Pattern 5: Static Models

**Problem**: Models become stale, performance degrades
**Solution**: Automated retraining pipelines

---

## Production Checklist

- [ ] **Monitoring**: Metrics, logs, traces, alerts
- [ ] **Observability**: Dashboard, SLIs/SLOs
- [ ] **Error Handling**: Graceful degradation, circuit breakers
- [ ] **Performance**: Caching, load balancing, auto-scaling
- [ ] **Reliability**: Health checks, redundancy, failover
- [ ] **Security**: Authentication, authorization, data encryption
- [ ] **Deployment**: Canary/blue-green, automated rollback
- [ ] **Drift Detection**: Data drift, prediction drift monitoring
- [ ] **Retraining**: Automated triggers, validation
- [ ] **Debugging**: Prediction logging, error tracking
- [ ] **Documentation**: API docs, runbooks, architecture
- [ ] **Testing**: Unit tests, integration tests, load tests

---

## Key Takeaways

1. **Production is Different**: Requires reliability, monitoring, fault tolerance
2. **Monitor Everything**: Metrics, drift, performance, errors
3. **Automate Retraining**: Don't let models become stale
4. **Plan for Failures**: Circuit breakers, graceful degradation
5. **Iterate Continuously**: Monitor, detect issues, improve

## Exercises

1. Implement prediction caching with Redis
2. Build circuit breaker for external service calls
3. Create drift detection system with alerting
4. Design automated retraining pipeline
5. Set up comprehensive production monitoring

## Additional Resources

- "Machine Learning Systems" by Chip Huyen
- "Building Machine Learning Powered Applications" by Ameisen
- "Reliable Machine Learning" by Google
- Production ML best practices
- Site Reliability Engineering book
