# Lecture 05: SLI, SLO, and SLA for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design Service Level Indicators (SLIs) for ML systems measuring availability (99.9%), latency (p95 <100ms), correctness (accuracy), and freshness
- Define Service Level Objectives (SLOs) balancing reliability targets with development velocity using error budgets (e.g., 99.9% availability = 43 minutes downtime/month)
- Create Service Level Agreements (SLAs) for ML services with customer commitments, penalties, and exclusions for external dependencies
- Implement SLO monitoring and alerting with burn rate alerts detecting fast and slow SLO consumption triggering appropriate urgency responses
- Calculate and manage error budgets allocating reliability buffer for deployments, experiments, and infrastructure changes without exceeding SLO targets
- Design multi-window burn rate alerts (1h, 6h, 24h, 3d) providing early warning of SLO violations with appropriate notification thresholds
- Build SLO dashboards visualizing current SLO compliance, remaining error budget, historical trends, and burn rate enabling data-driven operational decisions
- Architect reliability practices balancing innovation speed with system stability using SLOs to inform deployment policies, testing requirements, and incident priorities

## Overview

SLIs, SLOs, and SLAs form the foundation of reliability engineering for ML systems. They provide measurable targets for service quality and guide operational decisions.

## Definitions

### Service Level Indicator (SLI)
**Quantitative measure of service level**

For ML systems:
- **Availability**: Percentage of successful prediction requests
- **Latency**: Response time for predictions (p50, p95, p99)
- **Correctness**: Model accuracy/precision on production data
- **Freshness**: Age of model or features
- **Throughput**: Predictions per second

### Service Level Objective (SLO)
**Target value or range for an SLI**

Examples:
- 99.9% of prediction requests succeed
- 95% of predictions complete within 200ms
- Model accuracy stays above 85%
- Features refreshed every hour
- System handles 10,000 QPS

### Service Level Agreement (SLA)
**Contract with consequences if SLOs not met**

Typically includes:
- SLO commitments
- Measurement methodology
- Exclusions (planned maintenance)
- Consequences (credits, penalties)

##Common SLIs for ML Systems

### 1. Availability SLI

**Definition**: Percentage of successful prediction requests

```python
# metrics/availability_sli.py
from prometheus_client import Counter, Gauge

# Track requests
prediction_requests_total = Counter(
    'ml_prediction_requests_total',
    'Total prediction requests',
    ['model', 'status']
)

# Track current availability
availability_sli = Gauge(
    'ml_availability_sli',
    'Current availability SLI',
    ['model', 'window']
)

def record_prediction(model: str, success: bool):
    """Record prediction attempt"""
    status = 'success' if success else 'error'
    prediction_requests_total.labels(model=model, status=status).inc()

def calculate_availability(model: str, window: str = '5m'):
    """Calculate availability over time window"""
    # Query Prometheus for last N minutes
    query = f'''
        sum(rate(ml_prediction_requests_total{{model="{model}",status="success"}}[{window}]))
        /
        sum(rate(ml_prediction_requests_total{{model="{model}"}}[{window}]))
    '''
    # Execute query and update gauge
    availability = execute_prometheus_query(query)
    availability_sli.labels(model=model, window=window).set(availability)
    return availability
```

**PromQL Query**:
```promql
# 5-minute availability
sum(rate(ml_prediction_requests_total{status="success"}[5m]))
/
sum(rate(ml_prediction_requests_total[5m]))

# 30-day availability (error budget calculation)
1 - (
  sum(increase(ml_prediction_requests_total{status="error"}[30d]))
  /
  sum(increase(ml_prediction_requests_total[30d]))
)
```

### 2. Latency SLI

**Definition**: Request latency percentiles

```python
# metrics/latency_sli.py
from prometheus_client import Histogram

prediction_latency = Histogram(
    'ml_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()

    # Make prediction
    result = model.predict(data)

    # Record latency
    latency = time.time() - start_time
    prediction_latency.labels(model='churn_predictor').observe(latency)

    return jsonify(result)
```

**PromQL Queries**:
```promql
# P50 latency
histogram_quantile(0.50,
  rate(ml_prediction_latency_seconds_bucket[5m])
)

# P95 latency
histogram_quantile(0.95,
  rate(ml_prediction_latency_seconds_bucket[5m])
)

# P99 latency
histogram_quantile(0.99,
  rate(ml_prediction_latency_seconds_bucket[5m])
)
```

### 3. Model Quality SLI

**Definition**: Model performance metrics

```python
# metrics/quality_sli.py
from prometheus_client import Gauge
import numpy as np

model_accuracy = Gauge(
    'ml_model_accuracy',
    'Model accuracy on recent predictions',
    ['model', 'window']
)

model_precision = Gauge(
    'ml_model_precision',
    'Model precision on recent predictions',
    ['model', 'window']
)

class ModelQualityTracker:
    def __init__(self, window_size=1000):
        self.predictions = []
        self.actuals = []
        self.window_size = window_size

    def record_prediction(self, prediction, actual=None):
        """Record prediction and actual outcome"""
        self.predictions.append(prediction)
        if actual is not None:
            self.actuals.append(actual)

        # Keep only recent predictions
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)
            if self.actuals:
                self.actuals.pop(0)

    def calculate_metrics(self, model: str):
        """Calculate and update metrics"""
        if len(self.actuals) < 100:  # Need minimum samples
            return

        accuracy = np.mean(np.array(self.predictions[-len(self.actuals):]) == np.array(self.actuals))
        model_accuracy.labels(model=model, window='1000').set(accuracy)

        # Calculate precision (for binary classification)
        # ... implementation
```

### 4. Freshness SLI

**Definition**: Age of model or features

```python
# metrics/freshness_sli.py
from prometheus_client import Gauge
from datetime import datetime

model_age_seconds = Gauge(
    'ml_model_age_seconds',
    'Age of currently deployed model in seconds',
    ['model']
)

feature_age_seconds = Gauge(
    'ml_feature_age_seconds',
    'Age of features in seconds',
    ['model', 'feature_store']
)

def update_model_age(model: str, deployment_time: datetime):
    """Update model age metric"""
    age = (datetime.now() - deployment_time).total_seconds()
    model_age_seconds.labels(model=model).set(age)

def update_feature_age(model: str, feature_store: str, last_update: datetime):
    """Update feature age metric"""
    age = (datetime.now() - last_update).total_seconds()
    feature_age_seconds.labels(model=model, feature_store=feature_store).set(age)
```

**PromQL Query**:
```promql
# Model hasn't been updated in 7 days
ml_model_age_seconds > (7 * 24 * 60 * 60)

# Features older than 1 hour
ml_feature_age_seconds > 3600
```

---

## Defining SLOs

### SLO Framework

1. **Identify user journey**: What do users care about?
2. **Choose SLIs**: Which metrics matter most?
3. **Set targets**: What's good enough?
4. **Define measurement window**: Over what period?
5. **Document**: Write it down clearly

### Example SLOs for ML Service

```yaml
# slo_definitions.yaml
service: ml_prediction_api
team: ml_platform

slos:
  - name: availability
    description: "Prediction requests succeed"
    sli:
      type: availability
      metric: ml_prediction_requests_total
    target: 99.9
    window: 30d
    measurement: "ratio of successful requests to total requests"

  - name: latency_p95
    description: "95% of predictions complete quickly"
    sli:
      type: latency
      percentile: 95
      metric: ml_prediction_latency_seconds
    target: 200ms
    window: 5m
    measurement: "95th percentile latency"

  - name: model_accuracy
    description: "Model maintains minimum accuracy"
    sli:
      type: quality
      metric: ml_model_accuracy
    target: 0.85
    window: 24h
    measurement: "accuracy on labeled production data"

  - name: feature_freshness
    description: "Features are updated regularly"
    sli:
      type: freshness
      metric: ml_feature_age_seconds
    target: 3600  # 1 hour
    window: 1h
    measurement: "maximum feature age"
```

### Error Budget

**Concept**: Amount of unreliability allowed

```python
# slo/error_budget.py
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class ErrorBudget:
    slo_target: float  # e.g., 0.999 for 99.9%
    window_days: int   # e.g., 30

    @property
    def allowed_error_rate(self) -> float:
        """Maximum allowed error rate"""
        return 1.0 - self.slo_target

    @property
    def allowed_downtime(self) -> timedelta:
        """Maximum allowed downtime"""
        total_seconds = self.window_days * 24 * 60 * 60
        downtime_seconds = total_seconds * self.allowed_error_rate
        return timedelta(seconds=downtime_seconds)

    def remaining_budget(self, current_error_rate: float, elapsed_days: int) -> float:
        """Calculate remaining error budget"""
        used_budget = current_error_rate * elapsed_days / self.window_days
        return self.allowed_error_rate - used_budget

    def is_budget_exhausted(self, current_error_rate: float, elapsed_days: int) -> bool:
        """Check if error budget is exhausted"""
        return self.remaining_budget(current_error_rate, elapsed_days) <= 0

# Example
budget = ErrorBudget(slo_target=0.999, window_days=30)
print(f"Allowed downtime: {budget.allowed_downtime}")  # ~43 minutes/month
print(f"Allowed error rate: {budget.allowed_error_rate:.4f}")  # 0.001 or 0.1%

# Check current status
current_error_rate = 0.0005  # 0.05%
elapsed = 15  # days into month
remaining = budget.remaining_budget(current_error_rate, elapsed)
print(f"Remaining budget: {remaining:.4%}")
```

---

## SLO Implementation

### Monitoring System

```python
# slo/monitoring.py
from prometheus_api_client import PrometheusConnect
from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger(__name__)

@dataclass
class SLOConfig:
    name: str
    query: str
    target: float
    window: str

class SLOMonitor:
    def __init__(self, prometheus_url: str):
        self.prom = PrometheusConnect(url=prometheus_url)

    def check_slo(self, slo: SLOConfig) -> dict:
        """Check if SLO is being met"""
        # Query Prometheus
        result = self.prom.custom_query(slo.query)

        if not result:
            logger.error(f"No data for SLO: {slo.name}")
            return None

        current_value = float(result[0]['value'][1])

        # Check if meeting target
        meeting_slo = current_value >= slo.target

        status = {
            'slo_name': slo.name,
            'current_value': current_value,
            'target': slo.target,
            'meeting_slo': meeting_slo,
            'margin': current_value - slo.target
        }

        if not meeting_slo:
            logger.warning(
                f"SLO violation: {slo.name} "
                f"current={current_value:.4f} target={slo.target:.4f}"
            )

        return status

    def check_all_slos(self, slos: List[SLOConfig]) -> List[dict]:
        """Check all SLOs"""
        results = []
        for slo in slos:
            status = self.check_slo(slo)
            if status:
                results.append(status)
        return results

# Usage
monitor = SLOMonitor("http://prometheus:9090")

slos = [
    SLOConfig(
        name="availability",
        query='sum(rate(ml_prediction_requests_total{status="success"}[5m])) / sum(rate(ml_prediction_requests_total[5m]))',
        target=0.999,
        window="5m"
    ),
    SLOConfig(
        name="latency_p95",
        query='histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m]))',
        target=0.200,  # 200ms
        window="5m"
    )
]

results = monitor.check_all_slos(slos)
for result in results:
    print(f"{result['slo_name']}: {result['current_value']:.4f} (target: {result['target']:.4f})")
```

### Alerting Rules

```yaml
# prometheus/slo_alerts.yml
groups:
  - name: ml_slo_alerts
    interval: 30s
    rules:
      - alert: MLAvailabilitySLOViolation
        expr: |
          (
            sum(rate(ml_prediction_requests_total{status="success"}[5m]))
            /
            sum(rate(ml_prediction_requests_total[5m]))
          ) < 0.999
        for: 5m
        labels:
          severity: critical
          slo: availability
        annotations:
          summary: "ML service availability below SLO"
          description: "Availability is {{ $value | humanizePercentage }} (target: 99.9%)"

      - alert: MLLatencySLOViolation
        expr: |
          histogram_quantile(0.95,
            rate(ml_prediction_latency_seconds_bucket[5m])
          ) > 0.200
        for: 5m
        labels:
          severity: warning
          slo: latency
        annotations:
          summary: "ML service latency above SLO"
          description: "P95 latency is {{ $value }}s (target: 200ms)"

      - alert: MLAccuracySLOViolation
        expr: ml_model_accuracy < 0.85
        for: 1h
        labels:
          severity: warning
          slo: quality
        annotations:
          summary: "Model accuracy below SLO"
          description: "Model accuracy is {{ $value | humanizePercentage }} (target: 85%)"

      - alert: ErrorBudgetExhausted
        expr: |
          (
            1 - (
              sum(increase(ml_prediction_requests_total{status="success"}[30d]))
              /
              sum(increase(ml_prediction_requests_total[30d]))
            )
          ) > 0.001  # 99.9% SLO = 0.1% error budget
        labels:
          severity: critical
          slo: error_budget
        annotations:
          summary: "30-day error budget exhausted"
          description: "Error budget for this month is exhausted"
```

---

## SLO-Based Alerting

### Multi-Window, Multi-Burn-Rate Alerts

```yaml
# Advanced SLO alerting with multiple burn rates
groups:
  - name: slo_multiwindow_alerts
    rules:
      # Fast burn (2% budget in 1 hour)
      - alert: MLAvailabilityFastBurn
        expr: |
          (
            (1 - sum(rate(ml_prediction_requests_total{status="success"}[1h])) / sum(rate(ml_prediction_requests_total[1h])))
            > (14.4 * 0.001)  # 14.4x burn rate
          )
          and
          (
            (1 - sum(rate(ml_prediction_requests_total{status="success"}[5m])) / sum(rate(ml_prediction_requests_total[5m])))
            > (14.4 * 0.001)
          )
        labels:
          severity: critical
          burn_rate: fast
        annotations:
          summary: "Fast burn of error budget"
          description: "Burning through error budget at 14.4x rate"

      # Slow burn (10% budget in 24 hours)
      - alert: MLAvailabilitySlowBurn
        expr: |
          (
            (1 - sum(rate(ml_prediction_requests_total{status="success"}[24h])) / sum(rate(ml_prediction_requests_total[24h])))
            > (1.5 * 0.001)  # 1.5x burn rate
          )
          and
          (
            (1 - sum(rate(ml_prediction_requests_total{status="success"}[1h])) / sum(rate(ml_prediction_requests_total[1h])))
            > (1.5 * 0.001)
          )
        labels:
          severity: warning
          burn_rate: slow
        annotations:
          summary: "Slow burn of error budget"
          description: "Burning through error budget at 1.5x rate"
```

---

## Best Practices

1. **Start with few SLOs**: 3-5 key indicators
2. **Set realistic targets**: Based on actual performance
3. **Use error budgets**: Balance reliability and velocity
4. **Document everything**: Clear definitions and measurement
5. **Review regularly**: Adjust targets based on data
6. **Align with users**: SLOs should reflect user experience
7. **Avoid perfection**: 100% is impossible and wasteful

## Key Takeaways

- SLIs measure service level, SLOs set targets, SLAs are contracts
- Focus on user-impacting metrics
- Error budgets enable innovation while maintaining reliability
- Multi-window alerting reduces noise
- Review and adjust SLOs regularly

## Exercises

1. Define SLIs/SLOs for your ML service
2. Implement error budget tracking
3. Create multi-burn-rate alerting
4. Build SLO dashboard in Grafana
5. Calculate required reliability for SLO

## Additional Resources

- "The Site Reliability Workbook" (Chapter 2: SLOs)
- "Implementing Service Level Objectives" by Alex Hidalgo
- Google's SRE books
- SLO calculator tools
