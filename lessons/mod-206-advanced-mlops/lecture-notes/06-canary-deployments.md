# Lecture 06: Canary Deployments for ML Models

## Learning Objectives

By the end of this lecture, you will be able to:

- Design canary deployment strategies gradually routing production traffic to new model versions (5%→25%→50%→100%) with automated progression or rollback
- Implement automated rollback mechanisms using health checks, error rate monitoring, and anomaly detection triggering instant traffic shift to stable version
- Architect traffic routing patterns using Kubernetes Ingress, Istio service mesh, or AWS App Mesh for fine-grained canary traffic control
- Configure canary analysis with synthetic monitoring, real-user monitoring, and comparative metrics analysis (canary vs baseline) for deployment validation
- Design shadow deployments duplicating production traffic to new models without affecting users enabling safe validation before canary rollout
- Implement blue-green deployments with instant traffic switching and fast rollback as alternative to gradual canary progression
- Build deployment pipelines automating canary workflows with GitOps, Argo Rollouts/Flagger, and integration with CI/CD for continuous deployment
- Monitor canary deployments tracking latency percentiles (p50/p95/p99), error rates, prediction quality, and business metrics to make promotion decisions

## Overview

Canary deployments allow you to test new model versions with a small subset of production traffic before fully rolling out. This minimizes risk and enables quick rollbacks if issues occur.

## Canary Deployment Patterns

### Basic Canary Architecture

```
┌────────────────────────────────────────────────────────┐
│            Canary Deployment Architecture               │
└────────────────────────────────────────────────────────┘

            Production Traffic
                    │
                    ▼
            ┌──────────────┐
            │  Ingress /   │
            │  Load        │
            │  Balancer    │
            └──────────────┘
                    │
        ┌───────────┴───────────┐
        │  90%                  │  10%
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Stable      │        │   Canary     │
│  (v1.0)      │        │   (v2.0)     │
│  10 replicas │        │   1 replica  │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
            ┌──────────────┐
            │  Monitoring  │
            │  & Alerting  │
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │  Automated   │
            │  Promotion/  │
            │  Rollback    │
            └──────────────┘
```

### Traffic Splitting Strategies

1. **Percentage-based**: Fixed percentage to canary
2. **User-based**: Specific users/cohorts
3. **Geographic**: Specific regions
4. **Header-based**: Based on request headers

---

## Kubernetes-based Canary Deployment

### Deployment Manifests

```yaml
# k8s/stable-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-stable
  labels:
    app: ml-model
    version: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: ml-model
      version: stable
  template:
    metadata:
      labels:
        app: ml-model
        version: stable
    spec:
      containers:
      - name: model-server
        image: ml-model:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_VERSION
          value: "v1.0"
        - name: MODEL_NAME
          value: "churn_predictor"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
# k8s/canary-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-canary
  labels:
    app: ml-model
    version: canary
spec:
  replicas: 1  # Start with 1 replica (10% traffic)
  selector:
    matchLabels:
      app: ml-model
      version: canary
  template:
    metadata:
      labels:
        app: ml-model
        version: canary
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: model-server
        image: ml-model:v2.0  # New version
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_VERSION
          value: "v2.0"
        - name: MODEL_NAME
          value: "churn_predictor"
        - name: CANARY
          value: "true"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-model-service
spec:
  selector:
    app: ml-model  # Both stable and canary
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

---

## Istio-based Canary with Advanced Routing

### Istio Virtual Service

```yaml
# istio/virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-model-vs
spec:
  hosts:
  - ml-model-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: ml-model-service
        subset: canary
      weight: 100
  - route:
    - destination:
        host: ml-model-service
        subset: stable
      weight: 90
    - destination:
        host: ml-model-service
        subset: canary
      weight: 10
---
# istio/destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-model-dr
spec:
  host: ml-model-service
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
```

---

## Automated Canary Controller

```python
# canary/canary_controller.py
import kubernetes
from kubernetes import client, config
import prometheus_api_client
from datetime import datetime, timedelta
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CanaryConfig:
    namespace: str
    stable_deployment: str
    canary_deployment: str
    service_name: str
    traffic_increments: List[int]  # e.g., [10, 25, 50, 100]
    stage_duration_minutes: int
    metrics_threshold: Dict[str, float]

class CanaryController:
    def __init__(self, config: CanaryConfig, prometheus_url: str):
        self.config = config
        self.prometheus = prometheus_api_client.PrometheusConnect(url=prometheus_url)

        # Load Kubernetes config
        kubernetes.config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()

    def get_metrics(self, version: str, metric_name: str, duration: str = "5m") -> float:
        """Query Prometheus for metrics"""
        query = f'{metric_name}{{version="{version}"}}[{duration}]'
        result = self.prometheus.custom_query(query=query)

        if result:
            return float(result[0]['value'][1])
        return 0.0

    def check_canary_health(self) -> bool:
        """Check if canary meets health criteria"""
        logger.info("Checking canary health metrics...")

        metrics_ok = True

        # Check error rate
        error_rate = self.get_metrics("canary", "model_error_rate")
        threshold = self.config.metrics_threshold.get("max_error_rate", 0.01)
        if error_rate > threshold:
            logger.error(f"Error rate too high: {error_rate} > {threshold}")
            metrics_ok = False

        # Check latency
        latency_p99 = self.get_metrics("canary", "model_latency_p99")
        threshold = self.config.metrics_threshold.get("max_latency_p99", 200)
        if latency_p99 > threshold:
            logger.error(f"Latency too high: {latency_p99}ms > {threshold}ms")
            metrics_ok = False

        # Check prediction quality (if available)
        prediction_drift = self.get_metrics("canary", "model_prediction_drift")
        threshold = self.config.metrics_threshold.get("max_prediction_drift", 0.1)
        if prediction_drift > threshold:
            logger.warning(f"Prediction drift detected: {prediction_drift} > {threshold}")
            metrics_ok = False

        return metrics_ok

    def scale_deployment(self, deployment_name: str, replicas: int):
        """Scale deployment to specified number of replicas"""
        logger.info(f"Scaling {deployment_name} to {replicas} replicas")

        # Update deployment
        self.apps_v1.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=self.config.namespace,
            body={"spec": {"replicas": replicas}}
        )

        # Wait for rollout
        self.wait_for_rollout(deployment_name)

    def wait_for_rollout(self, deployment_name: str, timeout: int = 300):
        """Wait for deployment rollout to complete"""
        logger.info(f"Waiting for {deployment_name} rollout...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.config.namespace
            )

            if (deployment.status.ready_replicas ==
                deployment.spec.replicas ==
                deployment.status.updated_replicas):
                logger.info(f"{deployment_name} rollout complete")
                return True

            time.sleep(5)

        logger.error(f"Timeout waiting for {deployment_name} rollout")
        return False

    def calculate_replicas(self, traffic_percentage: int, total_replicas: int = 10) -> tuple:
        """Calculate stable and canary replicas for traffic percentage"""
        canary_replicas = max(1, int(total_replicas * traffic_percentage / 100))
        stable_replicas = total_replicas - canary_replicas

        return stable_replicas, canary_replicas

    def rollback(self):
        """Rollback canary deployment"""
        logger.warning("Rolling back canary deployment")

        # Scale canary to 0
        self.scale_deployment(self.config.canary_deployment, 0)

        # Scale stable to full capacity
        self.scale_deployment(self.config.stable_deployment, 10)

        logger.info("Rollback complete")

    def promote_canary(self):
        """Promote canary to stable"""
        logger.info("Promoting canary to stable")

        # Get canary image
        canary_deployment = self.apps_v1.read_namespaced_deployment(
            name=self.config.canary_deployment,
            namespace=self.config.namespace
        )
        canary_image = canary_deployment.spec.template.spec.containers[0].image

        # Update stable deployment with canary image
        stable_deployment = self.apps_v1.read_namespaced_deployment(
            name=self.config.stable_deployment,
            namespace=self.config.namespace
        )

        stable_deployment.spec.template.spec.containers[0].image = canary_image

        self.apps_v1.patch_namespaced_deployment(
            name=self.config.stable_deployment,
            namespace=self.config.namespace,
            body=stable_deployment
        )

        # Wait for stable rollout
        self.wait_for_rollout(self.config.stable_deployment)

        # Scale stable to full capacity and canary to 0
        self.scale_deployment(self.config.stable_deployment, 10)
        self.scale_deployment(self.config.canary_deployment, 0)

        logger.info("Promotion complete")

    def run_canary(self):
        """Execute canary deployment process"""
        logger.info("Starting canary deployment")

        for traffic_pct in self.config.traffic_increments:
            logger.info(f"\n{'='*60}")
            logger.info(f"Stage: {traffic_pct}% traffic to canary")
            logger.info(f"{'='*60}")

            # Calculate replicas
            stable_replicas, canary_replicas = self.calculate_replicas(traffic_pct)

            logger.info(f"Scaling: stable={stable_replicas}, canary={canary_replicas}")

            # Scale deployments
            self.scale_deployment(self.config.stable_deployment, stable_replicas)
            self.scale_deployment(self.config.canary_deployment, canary_replicas)

            # Wait for stabilization
            logger.info(f"Waiting {self.config.stage_duration_minutes} minutes for metrics...")
            time.sleep(self.config.stage_duration_minutes * 60)

            # Check health
            if not self.check_canary_health():
                logger.error("Canary health check failed!")
                self.rollback()
                return False

            logger.info(f"Stage {traffic_pct}% passed health checks")

        # All stages passed, promote canary
        self.promote_canary()
        logger.info("Canary deployment successful!")
        return True

# Usage example
if __name__ == '__main__':
    config = CanaryConfig(
        namespace="ml-models",
        stable_deployment="ml-model-stable",
        canary_deployment="ml-model-canary",
        service_name="ml-model-service",
        traffic_increments=[10, 25, 50, 100],
        stage_duration_minutes=10,
        metrics_threshold={
            "max_error_rate": 0.01,
            "max_latency_p99": 200,
            "max_prediction_drift": 0.1
        }
    )

    controller = CanaryController(config, prometheus_url="http://prometheus:9090")
    success = controller.run_canary()

    if success:
        logger.info("Canary deployment completed successfully")
    else:
        logger.error("Canary deployment failed and was rolled back")
```

---

## Flagger for GitOps Canary

### Flagger Configuration

```yaml
# flagger/canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: ml-model-canary
  namespace: ml-models
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    - name: model-prediction-drift
      thresholdRange:
        max: 0.1
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://ml-model-canary/predict"
  - name: slack-notification
      url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
      timeout: 5s
      metadata:
        message: |
          Canary analysis for ml-model:
          Status: {{ .Status }}
          Version: {{ .CanaryWeight }}%
```

---

## Monitoring Canary Deployments

### Prometheus Metrics

```python
# monitoring/canary_metrics.py
from prometheus_client import Counter, Histogram, Gauge
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Define metrics with version label
prediction_counter = Counter(
    'model_predictions_total',
    'Total predictions',
    ['version', 'status']
)

prediction_latency = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency',
    ['version']
)

model_error_rate = Gauge(
    'model_error_rate',
    'Model error rate',
    ['version']
)

prediction_confidence = Histogram(
    'model_prediction_confidence',
    'Prediction confidence score',
    ['version']
)

@app.route('/predict', methods=['POST'])
def predict():
    version = os.getenv('MODEL_VERSION', 'unknown')

    start_time = time.time()

    try:
        # Make prediction
        data = request.get_json()
        prediction, confidence = make_prediction(data)

        # Record metrics
        latency = time.time() - start_time
        prediction_latency.labels(version=version).observe(latency)
        prediction_counter.labels(version=version, status='success').inc()
        prediction_confidence.labels(version=version).observe(confidence)

        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'version': version
        })

    except Exception as e:
        prediction_counter.labels(version=version, status='error').inc()
        return jsonify({'error': str(e)}), 500
```

### Grafana Dashboard Query

```promql
# Error rate comparison
rate(model_predictions_total{status="error"}[5m])
/ rate(model_predictions_total[5m])

# Latency comparison
histogram_quantile(0.99,
  rate(model_prediction_latency_seconds_bucket[5m])
)

# Prediction confidence distribution
histogram_quantile(0.50,
  rate(model_prediction_confidence_bucket[5m])
)
```

---

## Best Practices

1. **Start Small**: Begin with 1-5% traffic
2. **Monitor Everything**: Track errors, latency, business metrics
3. **Automate Rollback**: Don't wait for manual intervention
4. **Use Feature Flags**: Combine with feature flags for additional control
5. **Test Thoroughly**: Validate canary in staging first
6. **Document Criteria**: Define clear success/failure criteria
7. **Gradual Increments**: Increase traffic gradually (5% → 10% → 25% → 50% → 100%)

## Key Takeaways

- Canary deployments minimize risk by testing with subset of traffic
- Automated health checks enable fast rollback
- Service meshes (Istio) provide advanced routing capabilities
- Monitor business metrics, not just technical metrics
- Combine with A/B testing for comprehensive validation

## Exercises

1. Deploy canary using Kubernetes deployments with manual traffic splitting
2. Implement automated canary controller with Prometheus integration
3. Set up Istio-based canary with advanced routing rules
4. Configure Flagger for GitOps-based canary deployments
5. Create Grafana dashboard for canary monitoring

## Additional Resources

- Flagger documentation
- Istio traffic management guide
- "Implementing Canary Releases" by Martin Fowler
- Kubernetes deployment strategies
