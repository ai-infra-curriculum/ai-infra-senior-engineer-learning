# Lab 01: Complete Observability Stack Setup

## Objective
Set up a complete observability stack with Prometheus, Grafana, and Loki for monitoring ML prediction services.

## Duration
3-4 hours

## Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm 3 installed
- Docker

## Architecture

```
ML Service → Metrics → Prometheus → Grafana
           → Logs   → Loki      → Grafana
           → Traces → Tempo     → Grafana
```

## Part 1: Install Prometheus Stack (45 min)

### Step 1: Add Helm Repository
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### Step 2: Create Namespace
```bash
kubectl create namespace monitoring
```

### Step 3: Install kube-prometheus-stack
```yaml
# values.yaml
prometheus:
  prometheusSpec:
    retention: 15d
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi

grafana:
  adminPassword: "admin"
  persistence:
    enabled: true
    size: 10Gi
```

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f values.yaml
```

### Step 4: Verify Installation
```bash
kubectl get pods -n monitoring
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

## Part 2: Deploy ML Service with Metrics (60 min)

### TODO: Implement prediction service with Prometheus metrics

Create `ml_service/app.py`:
```python
# TODO: Import required libraries

# TODO: Initialize Flask app

# TODO: Define Prometheus metrics:
# - prediction_requests_total (Counter)
# - prediction_latency_seconds (Histogram)
# - model_accuracy (Gauge)
# - predictions_in_flight (Gauge)

# TODO: Implement /predict endpoint
# - Record request
# - Time prediction
# - Update metrics

# TODO: Implement /metrics endpoint for Prometheus
# - Expose all metrics

# TODO: Implement /health endpoint
```

### TODO: Create Dockerfile

### TODO: Create Kubernetes Deployment
```yaml
# k8s/deployment.yaml
# TODO: Define deployment with:
# - 3 replicas
# - Resource limits
# - Health checks
# - Service exposing /metrics
```

### TODO: Create ServiceMonitor
```yaml
# k8s/servicemonitor.yaml
# TODO: Configure Prometheus to scrape metrics
```

## Part 3: Create Grafana Dashboards (60 min)

### TODO: Create Request Rate Dashboard
- Total requests per second
- Requests by status code
- Error rate percentage

### TODO: Create Latency Dashboard
- P50, P95, P99 latency
- Latency heatmap
- Slow requests (>200ms)

### TODO: Create Model Performance Dashboard
- Current accuracy
- Accuracy over time
- Prediction distribution

### TODO: Create Resource Usage Dashboard
- CPU usage per pod
- Memory usage per pod
- Network I/O

## Part 4: Configure Alerting (45 min)

### TODO: Create PrometheusRule for alerts

```yaml
# alerts/ml-service-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ml-service-alerts
spec:
  groups:
  - name: ml_service
    rules:
    # TODO: Define alerts:
    # - High error rate (>1%)
    # - High latency (P95 > 200ms)
    # - Low accuracy (<85%)
    # - Service down
```

### TODO: Configure Alertmanager
```yaml
# alertmanager-config.yaml
# TODO: Configure:
# - Slack notifications
# - Email notifications
# - PagerDuty integration
```

## Part 5: Install Loki for Logs (30 min)

### TODO: Install Loki
```bash
helm install loki grafana/loki-stack \
  -n monitoring \
  --set promtail.enabled=true
```

### TODO: Configure log aggregation
- Forward ML service logs to Loki
- Create log dashboard in Grafana
- Set up log-based alerts

## Deliverables

1. **Complete observability stack running**
   - Prometheus scraping metrics
   - Grafana dashboards
   - Loki collecting logs
   - Alerts configured

2. **ML service instrumented**
   - All metrics exposed
   - Logs structured
   - Ready for production

3. **Documentation**
   - Architecture diagram
   - Runbook for common issues
   - Dashboard descriptions

## Validation

- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards showing data
- [ ] Alerts firing correctly
- [ ] Logs searchable in Loki
- [ ] Service monitor working
- [ ] All pods healthy

## Bonus

1. Add distributed tracing with Tempo
2. Create SLO dashboard
3. Implement custom metrics
4. Add business metrics tracking
