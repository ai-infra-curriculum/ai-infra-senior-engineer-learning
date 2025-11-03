# Lecture 02: Distributed Tracing

## Learning Objectives

By the end of this lecture, you will be able to:

- Design distributed tracing architectures using OpenTelemetry, Jaeger, or Zipkin providing end-to-end visibility into ML inference requests across microservices
- Implement trace instrumentation for ML services capturing spans for data preprocessing, feature extraction, model inference, post-processing, and caching layers
- Configure trace sampling strategies balancing observability coverage with performance overhead using head-based, tail-based, and adaptive sampling techniques
- Analyze trace data identifying performance bottlenecks, latency percentiles, critical path analysis, and service dependencies in complex ML systems
- Design context propagation strategies ensuring trace IDs flow correctly through HTTP, gRPC, message queues, and async processing maintaining request correlation
- Implement trace-based alerting on anomalous latency patterns, error rates, and SLO violations triggering automatic investigation or remediation workflows
- Optimize tracing performance managing trace volume, reducing sampling overhead, and using async exporters to minimize impact on application latency
- Build trace analysis workflows correlating traces with logs and metrics for comprehensive debugging and root cause analysis of production issues

## Table of Contents
1. [Introduction](#introduction)
2. [Why Distributed Tracing Matters for ML](#why-distributed-tracing-matters-for-ml)
3. [Tracing Fundamentals](#tracing-fundamentals)
4. [OpenTelemetry](#opentelemetry)
5. [Jaeger](#jaeger)
6. [Zipkin](#zipkin)
7. [Instrumenting ML Services](#instrumenting-ml-services)
8. [Trace Analysis](#trace-analysis)
9. [Performance Optimization](#performance-optimization)
10. [Production Best Practices](#production-best-practices)

## Introduction

Distributed tracing provides end-to-end visibility into requests as they flow through complex microservices architectures. For AI infrastructure, where a single inference request might touch data preprocessing, feature extraction, model serving, post-processing, and caching layers, tracing is essential for understanding performance bottlenecks and debugging issues.

### What is Distributed Tracing?

Distributed tracing tracks a request's journey through multiple services by creating a trace—a tree of spans representing individual operations. Each span contains:

- **Span ID**: Unique identifier for the span
- **Trace ID**: Identifier linking all spans in a trace
- **Parent Span ID**: Reference to the calling span
- **Operation name**: What the span represents
- **Start/end timestamps**: Duration of the operation
- **Tags**: Key-value metadata
- **Logs**: Timestamped events within the span

```
Trace: user-prediction-request-abc123
│
├─ Span: API Gateway [200ms]
│  │
│  ├─ Span: Authentication [15ms]
│  │
│  ├─ Span: Load Balancer [5ms]
│  │
│  └─ Span: Prediction Service [180ms]
│     │
│     ├─ Span: Feature Extraction [50ms]
│     │  │
│     │  ├─ Span: Redis Cache Lookup [3ms]
│     │  └─ Span: Feature DB Query [45ms]
│     │
│     ├─ Span: Model Inference [100ms]
│     │  │
│     │  ├─ Span: Preprocess [10ms]
│     │  ├─ Span: GPU Inference [80ms]
│     │  └─ Span: Postprocess [10ms]
│     │
│     └─ Span: Result Caching [30ms]
│        └─ Span: Redis Write [28ms]
```

## Why Distributed Tracing Matters for ML

### 1. Complex Request Paths

ML inference requests often traverse many services:
- API gateway
- Authentication/authorization
- Feature store
- Model serving
- A/B testing framework
- Result aggregation
- Caching layers

Tracing reveals which component is the bottleneck.

### 2. Performance Debugging

Questions tracing answers:
- Why is inference taking 500ms when the model alone runs in 50ms?
- Which feature extraction step is slow?
- Are database queries serialized when they could be parallel?
- Is the bottleneck in the network, CPU, or GPU?

### 3. Dependency Mapping

Tracing automatically builds a service dependency graph, showing:
- Which services call which
- Critical path dependencies
- Retry and fallback patterns
- Cache hit rates

### 4. SLO Monitoring

Track latency at each layer to identify SLO violations:
- 95th percentile feature extraction latency
- Model inference p99 latency
- End-to-end request latency breakdown

## Tracing Fundamentals

### The OpenTelemetry Standard

OpenTelemetry (OTel) is the industry-standard observability framework, merging OpenTracing and OpenCensus. It provides:

- **Unified API** for metrics, traces, and logs
- **Language SDKs** for instrumentation
- **Automatic instrumentation** for popular frameworks
- **Vendor-neutral** data export to any backend
- **Context propagation** across service boundaries

### Trace Context Propagation

For distributed tracing to work, context must propagate across service boundaries. This happens through HTTP headers or message metadata.

**W3C Trace Context Headers**:
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor1=value1,vendor2=value2
```

Format: `version-trace_id-parent_span_id-trace_flags`

### Sampling Strategies

Recording every trace is expensive. Sampling reduces overhead while maintaining statistical validity.

**Sampling Types**:

1. **Head-based Sampling** (decision at trace start)
   - Probabilistic: Sample X% of traces
   - Rate limiting: Sample N traces per second
   - Parent-based: Follow parent's sampling decision

2. **Tail-based Sampling** (decision after trace completion)
   - Error sampling: Always sample traces with errors
   - Latency sampling: Sample slow traces
   - Attribute-based: Sample based on tags (e.g., user_tier=premium)

```python
# Head-based sampling configuration
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
    ALWAYS_OFF
)

# Sample 10% of traces
sampler = ParentBased(root=TraceIdRatioBased(0.1))
```

## OpenTelemetry

OpenTelemetry is the recommended approach for modern tracing implementations.

### Architecture

```
┌──────────────────────────────────────────────────┐
│              Your Application                     │
│  ┌────────────────────────────────────────┐     │
│  │     OpenTelemetry SDK                  │     │
│  │  ┌──────────┐  ┌──────────┐           │     │
│  │  │  Tracer  │  │ Metrics  │           │     │
│  │  └──────────┘  └──────────┘           │     │
│  │         ↓              ↓               │     │
│  │  ┌──────────────────────────┐         │     │
│  │  │   Exporters              │         │     │
│  │  │  - Jaeger                │         │     │
│  │  │  - Zipkin                │         │     │
│  │  │  - OTLP                  │         │     │
│  │  └──────────────────────────┘         │     │
│  └────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│         OpenTelemetry Collector                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Receivers │→ │Processors│→ │Exporters │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────────────────────────────────────────┘
                    ↓
       ┌────────────┴────────────┐
       ↓                         ↓
┌─────────────┐         ┌─────────────┐
│   Jaeger    │         │   Zipkin    │
└─────────────┘         └─────────────┘
```

### Installing OpenTelemetry

```bash
# Python
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-requests \
            opentelemetry-exporter-jaeger \
            opentelemetry-exporter-otlp

# Node.js
npm install @opentelemetry/api \
            @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-jaeger

# Go
go get go.opentelemetry.io/otel \
       go.opentelemetry.io/otel/exporters/jaeger \
       go.opentelemetry.io/otel/sdk
```

### Basic Instrumentation

```python
# app.py - FastAPI application with OpenTelemetry
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# TODO: Configure tracer provider with service information
resource = Resource(attributes={
    "service.name": "ml-inference-service",
    "service.version": "1.0.0",
    "deployment.environment": "production"
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

# TODO: Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.monitoring.svc.cluster.local",
    agent_port=6831,
)

# TODO: Add span processor
span_processor = BatchSpanProcessor(jaeger_exporter)
tracer_provider.add_span_processor(span_processor)

# Create FastAPI app
app = FastAPI()

# TODO: Instrument FastAPI automatically
FastAPIInstrumentor.instrument_app(app)

# Get tracer
tracer = trace.get_tracer(__name__)

# TODO: Manual instrumentation for custom spans
@app.post("/predict")
async def predict(request: PredictRequest):
    with tracer.start_as_current_span("prediction_handler") as span:
        # Add attributes to span
        span.set_attribute("model.name", request.model_name)
        span.set_attribute("model.version", request.model_version)
        span.set_attribute("input.size", len(request.features))

        # Feature extraction
        with tracer.start_as_current_span("feature_extraction") as feature_span:
            features = extract_features(request.features)
            feature_span.set_attribute("features.count", len(features))

        # Model inference
        with tracer.start_as_current_span("model_inference") as inference_span:
            inference_span.set_attribute("model.type", "pytorch")
            prediction = model.predict(features)
            inference_span.set_attribute("prediction.confidence", prediction.confidence)

        # Add event to span
        span.add_event("prediction_completed", {
            "prediction": str(prediction),
            "latency_ms": 150
        })

        return {"prediction": prediction}
```

### Automatic Instrumentation

```python
# auto_instrument.py
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorClient,
    GrpcInstrumentorServer
)

# TODO: Automatically instrument libraries
RequestsInstrumentor().instrument()  # HTTP requests
SQLAlchemyInstrumentor().instrument()  # Database queries
RedisInstrumentor().instrument()  # Redis operations
GrpcInstrumentorClient().instrument()  # gRPC client
GrpcInstrumentorServer().instrument()  # gRPC server
```

### Advanced Span Management

```python
# advanced_tracing.py
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import time

tracer = trace.get_tracer(__name__)

# TODO: Implement complex span hierarchy
def process_ml_pipeline(job_id, data):
    with tracer.start_as_current_span("ml_pipeline") as pipeline_span:
        pipeline_span.set_attribute("job.id", job_id)
        pipeline_span.set_attribute("data.size", len(data))

        try:
            # Data validation
            with tracer.start_as_current_span("data_validation") as val_span:
                validate_data(data)
                val_span.set_status(Status(StatusCode.OK))

            # Preprocessing
            with tracer.start_as_current_span("preprocessing") as prep_span:
                start = time.time()
                preprocessed = preprocess(data)
                duration = time.time() - start

                prep_span.set_attribute("preprocessing.duration_ms", duration * 1000)
                prep_span.set_attribute("preprocessing.method", "standard_scaler")
                prep_span.add_event("preprocessing_completed", {
                    "records_processed": len(preprocessed)
                })

            # Feature engineering
            with tracer.start_as_current_span("feature_engineering") as feat_span:
                features = engineer_features(preprocessed)
                feat_span.set_attribute("features.generated", features.shape[1])

            # Model inference (parallel)
            with tracer.start_as_current_span("parallel_inference") as parallel_span:
                # Create child spans for parallel model calls
                predictions = []
                for model_name in ["model_a", "model_b", "model_c"]:
                    with tracer.start_as_current_span(f"inference_{model_name}") as model_span:
                        model_span.set_attribute("model.name", model_name)
                        pred = run_model(model_name, features)
                        predictions.append(pred)
                        model_span.set_attribute("prediction.shape", pred.shape)

            # Ensemble
            with tracer.start_as_current_span("ensemble") as ens_span:
                final_prediction = ensemble(predictions)
                ens_span.set_attribute("ensemble.method", "weighted_average")

            pipeline_span.set_status(Status(StatusCode.OK))
            return final_prediction

        except Exception as e:
            # Record exception in span
            pipeline_span.record_exception(e)
            pipeline_span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

## Jaeger

Jaeger is a distributed tracing platform originally developed by Uber, now a CNCF graduated project.

### Jaeger Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Applications                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │ Service│  │ Service│  │ Service│  │ Service│        │
│  │   A    │  │   B    │  │   C    │  │   D    │        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
└──────────────────────────────────────────────────────────┘
       ↓            ↓            ↓            ↓
┌──────────────────────────────────────────────────────────┐
│                   Jaeger Agents                           │
│     (One per host, receives spans via UDP)                │
└──────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│                  Jaeger Collectors                        │
│    (Validate, index, and store spans)                     │
└──────────────────────────────────────────────────────────┘
                           ↓
       ┌───────────────────┴───────────────────┐
       ↓                                       ↓
┌─────────────┐                        ┌─────────────┐
│   Storage   │                        │    Kafka    │
│ (Cassandra, │                        │  (optional) │
│Elasticsearch│                        └─────────────┘
│     ES)     │
└─────────────┘
       ↓
┌──────────────────────────────────────────────────────────┐
│                   Jaeger Query                            │
│           (API and UI for trace retrieval)                │
└──────────────────────────────────────────────────────────┘
```

### Deploying Jaeger on Kubernetes

```yaml
# jaeger-all-in-one.yaml (for development/testing)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.49
          env:
            - name: COLLECTOR_ZIPKIN_HOST_PORT
              value: ":9411"
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"
          ports:
            - containerPort: 5775
              protocol: UDP
              name: zipkin-compact
            - containerPort: 6831
              protocol: UDP
              name: jaeger-compact
            - containerPort: 6832
              protocol: UDP
              name: jaeger-binary
            - containerPort: 5778
              protocol: TCP
              name: configs
            - containerPort: 16686
              protocol: TCP
              name: ui
            - containerPort: 14250
              protocol: TCP
              name: grpc
            - containerPort: 14268
              protocol: TCP
              name: http
            - containerPort: 14269
              protocol: TCP
              name: admin
            - containerPort: 9411
              protocol: TCP
              name: zipkin
            - containerPort: 4317
              protocol: TCP
              name: otlp-grpc
            - containerPort: 4318
              protocol: TCP
              name: otlp-http
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 1000m
              memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-collector
  namespace: monitoring
spec:
  selector:
    app: jaeger
  ports:
    - name: jaeger-compact
      port: 6831
      protocol: UDP
      targetPort: 6831
    - name: jaeger-binary
      port: 6832
      protocol: UDP
      targetPort: 6832
    - name: grpc
      port: 14250
      targetPort: 14250
    - name: http
      port: 14268
      targetPort: 14268
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: otlp-http
      port: 4318
      targetPort: 4318
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger-query
  namespace: monitoring
spec:
  selector:
    app: jaeger
  ports:
    - name: ui
      port: 16686
      targetPort: 16686
  type: LoadBalancer
```

### Production Jaeger Deployment

```yaml
# jaeger-production.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-production
  namespace: monitoring
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: https://elasticsearch.monitoring.svc:9200
        index-prefix: jaeger
        tls:
          ca: /etc/ssl/certs/ca.crt
        username: jaeger
        password-file: /etc/jaeger/es-password
    secretName: jaeger-secret
  collector:
    replicas: 3
    maxReplicas: 10
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 2000m
        memory: 4Gi
    autoscale: true
    options:
      collector:
        num-workers: 100
        queue-size: 5000
  query:
    replicas: 2
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1000m
        memory: 2Gi
    options:
      query:
        base-path: /jaeger
  agent:
    strategy: DaemonSet
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 200m
        memory: 256Mi
```

### Jaeger Query API

```python
# jaeger_query.py
import requests
from datetime import datetime, timedelta

# TODO: Query Jaeger for traces
class JaegerClient:
    def __init__(self, base_url="http://jaeger-query.monitoring.svc:16686"):
        self.base_url = base_url

    def find_traces(self, service, operation=None, tags=None, limit=20, lookback_hours=1):
        """Search for traces"""
        # TODO: Build query parameters
        params = {
            "service": service,
            "limit": limit,
            "lookback": f"{lookback_hours}h"
        }

        if operation:
            params["operation"] = operation

        if tags:
            # Tags format: key1=value1 key2=value2
            params["tags"] = " ".join([f"{k}={v}" for k, v in tags.items()])

        response = requests.get(f"{self.base_url}/api/traces", params=params)
        return response.json()

    def get_trace(self, trace_id):
        """Get a specific trace by ID"""
        # TODO: Fetch trace details
        response = requests.get(f"{self.base_url}/api/traces/{trace_id}")
        return response.json()

    def get_services(self):
        """Get list of all services"""
        response = requests.get(f"{self.base_url}/api/services")
        return response.json()

    def get_operations(self, service):
        """Get operations for a service"""
        response = requests.get(
            f"{self.base_url}/api/services/{service}/operations"
        )
        return response.json()

    def find_slow_traces(self, service, min_duration_ms=1000, limit=20):
        """Find traces slower than threshold"""
        # TODO: Query for slow traces
        params = {
            "service": service,
            "minDuration": f"{min_duration_ms}ms",
            "limit": limit,
            "lookback": "24h"
        }
        response = requests.get(f"{self.base_url}/api/traces", params=params)
        return response.json()

    def find_error_traces(self, service, limit=20):
        """Find traces with errors"""
        # TODO: Query for traces with error tag
        return self.find_traces(
            service=service,
            tags={"error": "true"},
            limit=limit
        )

# Usage example
client = JaegerClient()

# Find slow ML inference requests
slow_traces = client.find_slow_traces(
    service="ml-inference-service",
    min_duration_ms=500
)

# Find traces with errors
error_traces = client.find_error_traces(
    service="ml-inference-service"
)

# Find traces for specific model
model_traces = client.find_traces(
    service="ml-inference-service",
    tags={"model.name": "resnet50"},
    limit=50
)
```

## Zipkin

Zipkin is another popular distributed tracing system, originally developed by Twitter.

### Zipkin vs Jaeger

| Feature | Jaeger | Zipkin |
|---------|--------|--------|
| Storage | Cassandra, Elasticsearch, Kafka | Cassandra, Elasticsearch, MySQL |
| UI | Modern, feature-rich | Simpler, lightweight |
| Sampling | Client-side | Client and server-side |
| Maturity | Newer (2016) | Older (2012) |
| Ecosystem | CNCF, Kubernetes-native | Broader language support |

### Deploying Zipkin

```yaml
# zipkin.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
        - name: zipkin
          image: openzipkin/zipkin:2.24
          env:
            - name: STORAGE_TYPE
              value: elasticsearch
            - name: ES_HOSTS
              value: elasticsearch.monitoring.svc:9200
          ports:
            - containerPort: 9411
              name: http
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 1000m
              memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: zipkin
  namespace: monitoring
spec:
  selector:
    app: zipkin
  ports:
    - port: 9411
      targetPort: 9411
  type: LoadBalancer
```

## Instrumenting ML Services

### Feature Store Tracing

```python
# feature_store_tracing.py
from opentelemetry import trace
import redis
import psycopg2

tracer = trace.get_tracer(__name__)

class FeatureStore:
    def __init__(self, redis_client, pg_conn):
        self.redis = redis_client
        self.pg = pg_conn

    # TODO: Add tracing to feature retrieval
    def get_features(self, entity_id, feature_names):
        with tracer.start_as_current_span("get_features") as span:
            span.set_attribute("entity.id", entity_id)
            span.set_attribute("features.requested", len(feature_names))

            features = {}

            # Try cache first
            with tracer.start_as_current_span("redis_cache_lookup") as cache_span:
                cache_key = f"features:{entity_id}"
                cached = self.redis.hgetall(cache_key)
                cache_span.set_attribute("cache.hit", len(cached) > 0)
                cache_span.set_attribute("cache.key", cache_key)

                if cached:
                    features.update(cached)
                    span.add_event("cache_hit", {"cached_features": len(cached)})

            # Fetch missing features from database
            missing_features = set(feature_names) - set(features.keys())
            if missing_features:
                with tracer.start_as_current_span("postgres_feature_fetch") as db_span:
                    db_span.set_attribute("missing_features.count", len(missing_features))

                    query = """
                        SELECT feature_name, feature_value
                        FROM features
                        WHERE entity_id = %s AND feature_name = ANY(%s)
                    """
                    cursor = self.pg.cursor()
                    cursor.execute(query, (entity_id, list(missing_features)))

                    db_features = dict(cursor.fetchall())
                    features.update(db_features)
                    db_span.set_attribute("db.rows_fetched", len(db_features))

                    # Update cache
                    with tracer.start_as_current_span("redis_cache_update"):
                        self.redis.hset(cache_key, mapping=db_features)
                        self.redis.expire(cache_key, 3600)

            span.set_attribute("features.returned", len(features))
            return features
```

### Model Serving Tracing

```python
# model_serving_tracing.py
from opentelemetry import trace
import torch
import numpy as np

tracer = trace.get_tracer(__name__)

class ModelServer:
    def __init__(self, model_path):
        # TODO: Add tracing to model loading
        with tracer.start_as_current_span("model_loading") as span:
            span.set_attribute("model.path", model_path)
            self.model = torch.load(model_path)
            self.model.eval()
            span.add_event("model_loaded")

    # TODO: Add comprehensive tracing to prediction
    def predict(self, input_data):
        with tracer.start_as_current_span("model_prediction") as span:
            span.set_attribute("input.shape", str(input_data.shape))
            span.set_attribute("model.framework", "pytorch")

            # Preprocessing
            with tracer.start_as_current_span("preprocessing") as prep_span:
                preprocessed = self._preprocess(input_data)
                prep_span.set_attribute("preprocessing.method", "normalize")

            # GPU transfer
            with tracer.start_as_current_span("gpu_transfer") as gpu_span:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                input_tensor = torch.tensor(preprocessed).to(device)
                gpu_span.set_attribute("device", str(device))

            # Inference
            with tracer.start_as_current_span("inference") as inf_span:
                with torch.no_grad():
                    output = self.model(input_tensor)

                inf_span.set_attribute("output.shape", str(output.shape))
                inf_span.add_event("inference_complete")

            # Postprocessing
            with tracer.start_as_current_span("postprocessing") as post_span:
                result = self._postprocess(output)
                post_span.set_attribute("result.confidence", float(result.max()))

            span.set_attribute("prediction.class", int(result.argmax()))
            return result

    def _preprocess(self, data):
        # Normalization logic
        return (data - data.mean()) / data.std()

    def _postprocess(self, output):
        # Softmax
        return torch.nn.functional.softmax(output, dim=-1).cpu().numpy()
```

### Training Job Tracing

```python
# training_tracing.py
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

# TODO: Instrument training loop with tracing
def train_model(model, dataloader, epochs, job_id):
    with tracer.start_as_current_span("training_job") as job_span:
        job_span.set_attribute("job.id", job_id)
        job_span.set_attribute("epochs", epochs)
        job_span.set_attribute("batch_size", dataloader.batch_size)

        for epoch in range(epochs):
            with tracer.start_as_current_span(f"epoch_{epoch}") as epoch_span:
                epoch_span.set_attribute("epoch.number", epoch)

                total_loss = 0
                batch_count = 0

                for batch_idx, (data, target) in enumerate(dataloader):
                    with tracer.start_as_current_span(f"batch_{batch_idx}") as batch_span:
                        batch_span.set_attribute("batch.index", batch_idx)
                        batch_span.set_attribute("batch.size", len(data))

                        # Forward pass
                        with tracer.start_as_current_span("forward_pass"):
                            output = model(data)
                            loss = criterion(output, target)

                        # Backward pass
                        with tracer.start_as_current_span("backward_pass"):
                            optimizer.zero_grad()
                            loss.backward()
                            optimizer.step()

                        batch_span.set_attribute("loss", float(loss))
                        total_loss += loss.item()
                        batch_count += 1

                avg_loss = total_loss / batch_count
                epoch_span.set_attribute("epoch.avg_loss", avg_loss)
                epoch_span.add_event("epoch_complete", {"avg_loss": avg_loss})

        job_span.add_event("training_complete")
```

## Trace Analysis

### Finding Performance Bottlenecks

```python
# trace_analysis.py
from jaeger_client import JaegerClient

# TODO: Analyze traces to find bottlenecks
def analyze_bottlenecks(service, lookback_hours=1):
    client = JaegerClient()

    # Get recent traces
    traces = client.find_traces(
        service=service,
        limit=100,
        lookback_hours=lookback_hours
    )

    # Analyze span durations
    span_durations = {}
    for trace in traces["data"]:
        for span in trace["spans"]:
            operation = span["operationName"]
            duration = span["duration"]

            if operation not in span_durations:
                span_durations[operation] = []
            span_durations[operation].append(duration)

    # Calculate statistics
    bottlenecks = []
    for operation, durations in span_durations.items():
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]

        bottlenecks.append({
            "operation": operation,
            "avg_ms": avg_duration / 1000,
            "max_ms": max_duration / 1000,
            "p95_ms": p95_duration / 1000,
            "count": len(durations)
        })

    # Sort by p95 duration
    bottlenecks.sort(key=lambda x: x["p95_ms"], reverse=True)
    return bottlenecks
```

### Dependency Graph Generation

```python
# dependency_graph.py
def build_dependency_graph(service, lookback_hours=24):
    """Build service dependency graph from traces"""
    client = JaegerClient()
    traces = client.find_traces(service, limit=1000, lookback_hours=lookback_hours)

    # TODO: Extract service dependencies
    dependencies = {}  # {(parent, child): call_count}

    for trace in traces["data"]:
        spans_by_id = {span["spanID"]: span for span in trace["spans"]}

        for span in trace["spans"]:
            service_name = span["process"]["serviceName"]
            parent_id = span.get("references", [{}])[0].get("spanID")

            if parent_id and parent_id in spans_by_id:
                parent_service = spans_by_id[parent_id]["process"]["serviceName"]
                edge = (parent_service, service_name)

                dependencies[edge] = dependencies.get(edge, 0) + 1

    # Generate graph
    import networkx as nx
    G = nx.DiGraph()

    for (parent, child), count in dependencies.items():
        G.add_edge(parent, child, weight=count)

    return G
```

## Performance Optimization

### Sampling Configuration

```python
# sampling.py
from opentelemetry.sdk.trace.sampling import (
    ParentBased,
    TraceIdRatioBased,
    ALWAYS_ON,
    ALWAYS_OFF
)

# TODO: Configure adaptive sampling
class AdaptiveSampler:
    """Sample based on request characteristics"""

    def should_sample(self, context, trace_id, name, attributes):
        # Always sample errors
        if attributes.get("error") == "true":
            return ALWAYS_ON

        # Always sample slow requests
        if attributes.get("duration_ms", 0) > 1000:
            return ALWAYS_ON

        # Sample 10% of normal requests
        return TraceIdRatioBased(0.1)
```

### Reducing Overhead

- Use asynchronous span processors
- Batch span exports
- Sample strategically
- Minimize span attributes
- Use tail-based sampling for production

## Production Best Practices

1. **Use OpenTelemetry Collector**: Centralize span processing
2. **Implement Sampling**: Reduce costs while maintaining visibility
3. **Monitor Tracing Infrastructure**: Alert on collector lag, storage issues
4. **Secure Trace Data**: Contains potentially sensitive information
5. **Set Retention Policies**: Balance cost and debugging needs
6. **Correlate with Metrics/Logs**: Use trace IDs in logs for correlation
7. **Document Spans**: Clearly name operations and add meaningful attributes
8. **Test Instrumentation**: Verify spans are created correctly

## Summary

Distributed tracing provides critical visibility into ML systems:
- Understand request flow through complex pipelines
- Identify performance bottlenecks
- Debug production issues
- Optimize resource usage
- Build service dependency maps

In the next lecture, we'll explore log aggregation to complete the observability picture.

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Zipkin Documentation](https://zipkin.io/)
- "Distributed Tracing in Practice" by Austin Parker et al.
