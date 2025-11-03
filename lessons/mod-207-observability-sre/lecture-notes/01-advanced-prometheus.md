# Lecture 01: Advanced Prometheus

## Learning Objectives

By the end of this lecture, you will be able to:

- Design enterprise-grade Prometheus architectures with federation for multi-cluster monitoring aggregating metrics from 100+ clusters to centralized monitoring
- Implement long-term storage solutions using Thanos or Cortex for multi-year metric retention with downsampling and cost-effective object storage backends
- Configure high-availability Prometheus deployments with replication, deduplication, and automatic failover ensuring zero data loss and continuous monitoring
- Master advanced PromQL queries for ML workloads including GPU utilization analysis, training progress tracking, cost attribution, and anomaly detection
- Design recording rules that pre-compute expensive queries achieving 10-100x speedup for dashboards and reducing query load on Prometheus servers
- Implement custom exporters for ML-specific metrics including model inference latency, batch job progress, feature store lag, and data pipeline health
- Optimize Prometheus performance through cardinality management, retention policies, remote write tuning, and query optimization for large-scale deployments
- Architect production Prometheus systems with proper resource sizing, backup strategies, disaster recovery, and capacity planning for growing metric volumes

## Table of Contents
1. [Introduction](#introduction)
2. [Prometheus Architecture Review](#prometheus-architecture-review)
3. [Federation](#federation)
4. [Long-Term Storage](#long-term-storage)
5. [High Availability](#high-availability)
6. [Advanced PromQL](#advanced-promql)
7. [Recording Rules](#recording-rules)
8. [Custom Exporters](#custom-exporters)
9. [Performance Optimization](#performance-optimization)
10. [Production Best Practices](#production-best-practices)

## Introduction

Prometheus has become the de facto standard for monitoring cloud-native applications, particularly in Kubernetes environments. While basic Prometheus usage covers simple metric collection and alerting, production AI infrastructure requires advanced techniques to handle scale, reliability, and long-term data retention.

In this lecture, we'll explore enterprise-grade Prometheus deployments, including federation for multi-cluster monitoring, long-term storage solutions, and advanced query techniques specifically useful for ML workloads.

### Why Advanced Prometheus Matters for AI Infrastructure

AI infrastructure presents unique monitoring challenges:

- **Scale**: Training jobs can span hundreds of GPUs across multiple clusters
- **Cost**: GPU resources are expensive; inefficiencies must be detected quickly
- **Multi-tenancy**: Multiple teams sharing infrastructure need isolated views
- **Long-term trends**: Model performance degradation may occur over weeks or months
- **Complex metrics**: GPU utilization, model accuracy, data drift, and inference latency all need tracking

Basic Prometheus setups struggle with these requirements, making advanced techniques essential.

## Prometheus Architecture Review

Before diving into advanced topics, let's review Prometheus fundamentals and identify scaling limitations.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Prometheus Server                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Retrieval   │→ │    TSDB      │→ │   HTTP API   │      │
│  │  (Scraping)  │  │  (Storage)   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                                      ↑             │
│  ┌──────────────┐                    ┌──────────────┐      │
│  │ Service      │                    │  Grafana     │      │
│  │ Discovery    │                    │  (Queries)   │      │
│  └──────────────┘                    └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         ↓
   ┌──────────────┐
   │  Exporters   │
   │  (Metrics)   │
   └──────────────┘
```

### Scaling Limitations

1. **Storage**: Local TSDB limited by disk space (default 15-day retention)
2. **Memory**: All active time series must fit in memory
3. **Query performance**: Complex queries can overwhelm single instances
4. **High availability**: Single Prometheus instance is a single point of failure
5. **Global view**: No built-in way to query across multiple Prometheus instances

## Federation

Federation allows hierarchical aggregation of metrics from multiple Prometheus servers, enabling multi-cluster and multi-region monitoring.

### Federation Architectures

#### 1. Hierarchical Federation

```
                    ┌──────────────────────┐
                    │  Global Prometheus   │
                    │   (Federation)       │
                    └──────────────────────┘
                             ↑
              ┌──────────────┼──────────────┐
              │              │              │
      ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
      │  Regional      │ │  Regional     │ │  Regional     │
      │  Prometheus    │ │  Prometheus   │ │  Prometheus   │
      │  (us-east)     │ │  (us-west)    │ │  (eu-west)    │
      └───────────────┘ └───────────────┘ └───────────────┘
              ↑                  ↑                 ↑
        ┌─────┴─────┐      ┌─────┴─────┐    ┌─────┴─────┐
        │   │   │   │      │   │   │   │    │   │   │   │
     Cluster Cluster    Cluster Cluster  Cluster Cluster
       Prom   Prom       Prom   Prom      Prom   Prom
```

**Use case**: Large organizations with multiple regions and clusters

#### 2. Cross-Service Federation

```
┌─────────────────────────────────────────────────────────┐
│                 Meta Prometheus                          │
│         (Aggregated metrics from all services)           │
└─────────────────────────────────────────────────────────┘
           ↑              ↑              ↑
           │              │              │
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  Service │   │  Service │   │  Service │
    │   Prom   │   │   Prom   │   │   Prom   │
    │ (Training)│   │(Serving) │   │ (Data)   │
    └──────────┘   └──────────┘   └──────────┘
```

**Use case**: Aggregating metrics across different ML pipeline components

### Implementing Federation

#### Configuration for Global Prometheus

```yaml
# global-prometheus.yml
global:
  scrape_interval: 60s
  evaluation_interval: 60s
  external_labels:
    cluster: 'global'
    environment: 'production'

scrape_configs:
  # Federate from regional Prometheus servers
  - job_name: 'federate-us-east'
    scrape_interval: 30s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        # Aggregate CPU metrics
        - '{job="kubernetes-nodes"}'
        # GPU metrics
        - '{job="gpu-exporter"}'
        # Model serving metrics
        - '{__name__=~"model_.*"}'
        # Custom ML metrics
        - '{__name__=~"ml_training_.*"}'
        # Recording rules from regional instances
        - '{__name__=~"job:.*"}'
    static_configs:
      - targets:
          - 'prometheus-us-east.monitoring.svc:9090'
        labels:
          region: 'us-east-1'

  - job_name: 'federate-us-west'
    scrape_interval: 30s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="kubernetes-nodes"}'
        - '{job="gpu-exporter"}'
        - '{__name__=~"model_.*"}'
        - '{__name__=~"ml_training_.*"}'
        - '{__name__=~"job:.*"}'
    static_configs:
      - targets:
          - 'prometheus-us-west.monitoring.svc:9090'
        labels:
          region: 'us-west-2'

  - job_name: 'federate-eu-west'
    scrape_interval: 30s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="kubernetes-nodes"}'
        - '{job="gpu-exporter"}'
        - '{__name__=~"model_.*"}'
        - '{__name__=~"ml_training_.*"}'
        - '{__name__=~"job:.*"}'
    static_configs:
      - targets:
          - 'prometheus-eu-west.monitoring.svc:9090'
        labels:
          region: 'eu-west-1'
```

#### Regional Prometheus Configuration

```yaml
# regional-prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'us-east-training-01'
    region: 'us-east-1'
    environment: 'production'

scrape_configs:
  # Scrape Kubernetes nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Scrape GPU metrics
  - job_name: 'gpu-exporter'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: gpu-exporter
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod

  # Scrape model training metrics
  - job_name: 'ml-training-jobs'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_job_type]
        action: keep
        regex: training
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

# Recording rules for aggregation
rule_files:
  - '/etc/prometheus/rules/*.yml'
```

### Federation Best Practices

1. **Use `honor_labels: true`**: Preserves labels from source Prometheus instances
2. **Selective metric federation**: Only federate necessary metrics to reduce cardinality
3. **Use recording rules**: Pre-aggregate data at regional level before federation
4. **Set appropriate scrape intervals**: Longer intervals for global Prometheus (30-60s)
5. **Monitor federation lag**: Track federation scrape duration and failures

### Federation for ML Workloads

```yaml
# Example: Federate only ML-specific aggregated metrics
scrape_configs:
  - job_name: 'federate-ml-metrics'
    scrape_interval: 60s
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        # Model performance metrics (pre-aggregated)
        - '{__name__=~"model:accuracy:.*"}'
        - '{__name__=~"model:latency:.*"}'
        - '{__name__=~"model:throughput:.*"}'
        # Training job metrics
        - '{__name__=~"training:gpu_utilization:.*"}'
        - '{__name__=~"training:loss:.*"}'
        # Data pipeline metrics
        - '{__name__=~"data:processing_rate:.*"}'
        - '{__name__=~"data:quality:.*"}'
    static_configs:
      - targets:
          - 'prometheus-training-cluster.svc:9090'
          - 'prometheus-inference-cluster.svc:9090'
```

## Long-Term Storage

Prometheus's local TSDB is designed for short-term storage (typically 15 days). For AI infrastructure, long-term metric retention is crucial for:

- Tracking model performance degradation over months
- Capacity planning based on historical trends
- Compliance and audit requirements
- Cost analysis and optimization

### Long-Term Storage Solutions

#### 1. Thanos

Thanos extends Prometheus with:
- Unlimited retention using object storage (S3, GCS, Azure Blob)
- Global query view across multiple Prometheus instances
- Downsampling for efficient long-term storage
- Deduplication of replicated data

**Thanos Architecture**:

```
┌────────────────────────────────────────────────────────────────┐
│                        Thanos Query                             │
│                    (Global Query Layer)                         │
└────────────────────────────────────────────────────────────────┘
           ↓              ↓              ↓              ↓
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  Thanos  │   │  Thanos  │   │  Thanos  │   │  Thanos  │
    │ Sidecar  │   │ Sidecar  │   │  Store   │   │ Compactor│
    │          │   │          │   │ Gateway  │   │          │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
         ↓              ↓              ↓
    Prometheus    Prometheus    Object Storage
                                  (S3/GCS)
```

**Components**:
- **Sidecar**: Runs alongside Prometheus, uploads blocks to object storage
- **Store Gateway**: Serves historical data from object storage
- **Compactor**: Downsamples and compacts data
- **Query**: Provides global query interface
- **Ruler**: Evaluates recording/alerting rules on global data

#### Thanos Deployment Example

```yaml
# thanos-sidecar.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus-with-thanos
  namespace: monitoring
spec:
  serviceName: prometheus
  replicas: 2
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
        thanos-store-api: "true"
    spec:
      serviceAccountName: prometheus
      containers:
      # Prometheus container
      - name: prometheus
        image: prom/prometheus:v2.45.0
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=24h'  # Short retention, Thanos handles long-term
          - '--storage.tsdb.min-block-duration=2h'
          - '--storage.tsdb.max-block-duration=2h'
          - '--web.enable-lifecycle'
          - '--web.enable-admin-api'
        ports:
          - containerPort: 9090
            name: http
        volumeMounts:
          - name: prometheus-config
            mountPath: /etc/prometheus
          - name: prometheus-storage
            mountPath: /prometheus

      # Thanos Sidecar container
      - name: thanos-sidecar
        image: thanosio/thanos:v0.32.0
        args:
          - sidecar
          - --tsdb.path=/prometheus
          - --prometheus.url=http://localhost:9090
          - --objstore.config-file=/etc/thanos/objstore.yml
          - --grpc-address=0.0.0.0:10901
          - --http-address=0.0.0.0:10902
        ports:
          - containerPort: 10901
            name: grpc
          - containerPort: 10902
            name: http
        volumeMounts:
          - name: prometheus-storage
            mountPath: /prometheus
          - name: thanos-objstore-config
            mountPath: /etc/thanos
        env:
          - name: POD_NAME
            valueFrom:
              fieldRef:
                fieldPath: metadata.name

      volumes:
        - name: prometheus-config
          configMap:
            name: prometheus-config
        - name: thanos-objstore-config
          secret:
            secretName: thanos-objstore-config

  volumeClaimTemplates:
    - metadata:
        name: prometheus-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 50Gi
```

**Object Storage Configuration**:

```yaml
# objstore.yml
type: S3
config:
  bucket: "ai-metrics-long-term-storage"
  endpoint: "s3.us-east-1.amazonaws.com"
  region: "us-east-1"
  access_key: "${AWS_ACCESS_KEY_ID}"
  secret_key: "${AWS_SECRET_ACCESS_KEY}"
  insecure: false
  signature_version2: false
  # Optional: Server-side encryption
  sse_config:
    type: "SSE-S3"
  # Optional: HTTP configuration
  http_config:
    idle_conn_timeout: 90s
    response_header_timeout: 2m
```

**Thanos Query Deployment**:

```yaml
# thanos-query.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thanos-query
  namespace: monitoring
spec:
  replicas: 3
  selector:
    matchLabels:
      app: thanos-query
  template:
    metadata:
      labels:
        app: thanos-query
    spec:
      containers:
        - name: thanos-query
          image: thanosio/thanos:v0.32.0
          args:
            - query
            - --http-address=0.0.0.0:10902
            - --grpc-address=0.0.0.0:10901
            - --store=dnssrv+_grpc._tcp.prometheus-operated.monitoring.svc.cluster.local
            - --store=dnssrv+_grpc._tcp.thanos-store.monitoring.svc.cluster.local
            - --query.replica-label=replica
            - --query.replica-label=prometheus_replica
            - --query.timeout=5m
            - --query.max-concurrent=20
            - --query.lookback-delta=15m
          ports:
            - containerPort: 10902
              name: http
            - containerPort: 10901
              name: grpc
          livenessProbe:
            httpGet:
              path: /-/healthy
              port: http
            initialDelaySeconds: 30
          readinessProbe:
            httpGet:
              path: /-/ready
              port: http
            initialDelaySeconds: 30
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
```

**Thanos Store Gateway**:

```yaml
# thanos-store.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: thanos-store
  namespace: monitoring
spec:
  serviceName: thanos-store
  replicas: 3
  selector:
    matchLabels:
      app: thanos-store
  template:
    metadata:
      labels:
        app: thanos-store
        thanos-store-api: "true"
    spec:
      containers:
        - name: thanos-store
          image: thanosio/thanos:v0.32.0
          args:
            - store
            - --data-dir=/var/thanos/store
            - --objstore.config-file=/etc/thanos/objstore.yml
            - --grpc-address=0.0.0.0:10901
            - --http-address=0.0.0.0:10902
            - --index-cache-size=2GB
            - --chunk-pool-size=2GB
          ports:
            - containerPort: 10901
              name: grpc
            - containerPort: 10902
              name: http
          volumeMounts:
            - name: thanos-objstore-config
              mountPath: /etc/thanos
            - name: store-data
              mountPath: /var/thanos/store
          resources:
            requests:
              cpu: 1000m
              memory: 4Gi
            limits:
              cpu: 2000m
              memory: 8Gi
      volumes:
        - name: thanos-objstore-config
          secret:
            secretName: thanos-objstore-config
  volumeClaimTemplates:
    - metadata:
        name: store-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
```

**Thanos Compactor**:

```yaml
# thanos-compactor.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: thanos-compactor
  namespace: monitoring
spec:
  serviceName: thanos-compactor
  replicas: 1  # Only one compactor should run
  selector:
    matchLabels:
      app: thanos-compactor
  template:
    metadata:
      labels:
        app: thanos-compactor
    spec:
      containers:
        - name: thanos-compactor
          image: thanosio/thanos:v0.32.0
          args:
            - compact
            - --data-dir=/var/thanos/compact
            - --objstore.config-file=/etc/thanos/objstore.yml
            - --http-address=0.0.0.0:10902
            - --retention.resolution-raw=30d
            - --retention.resolution-5m=90d
            - --retention.resolution-1h=365d
            - --wait
            - --delete-delay=48h
            - --compact.concurrency=1
          ports:
            - containerPort: 10902
              name: http
          volumeMounts:
            - name: thanos-objstore-config
              mountPath: /etc/thanos
            - name: compact-data
              mountPath: /var/thanos/compact
          resources:
            requests:
              cpu: 1000m
              memory: 4Gi
            limits:
              cpu: 2000m
              memory: 8Gi
      volumes:
        - name: thanos-objstore-config
          secret:
            secretName: thanos-objstore-config
  volumeClaimTemplates:
    - metadata:
        name: compact-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
```

#### 2. Cortex

Cortex is a horizontally scalable, multi-tenant Prometheus-as-a-Service solution.

**Key Features**:
- Horizontally scalable ingestion and querying
- Multi-tenancy with separate storage per tenant
- Long-term storage in object storage or NoSQL databases
- Compatible with Prometheus API and PromQL

**Cortex Architecture**:

```
┌────────────────────────────────────────────────────────────┐
│                     Query Frontend                          │
│                  (Query coordination)                       │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│                        Querier                              │
│                (Executes PromQL queries)                    │
└────────────────────────────────────────────────────────────┘
           ↓                                    ↓
    ┌──────────┐                         ┌──────────┐
    │ Ingester │                         │  Store   │
    │ (Recent) │                         │ Gateway  │
    └──────────┘                         └──────────┘
           ↓                                    ↓
    ┌──────────────────────────────────────────────┐
    │         Object Storage / NoSQL DB             │
    └──────────────────────────────────────────────┘
```

#### 3. VictoriaMetrics

VictoriaMetrics is a high-performance, cost-effective Prometheus alternative with built-in long-term storage.

**Advantages**:
- Better compression (10x compared to Prometheus)
- Lower memory usage
- Faster queries
- Built-in downsampling
- Simpler deployment than Thanos/Cortex

**Deployment Example**:

```yaml
# victoriametrics.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: victoriametrics
  namespace: monitoring
spec:
  serviceName: victoriametrics
  replicas: 1
  selector:
    matchLabels:
      app: victoriametrics
  template:
    metadata:
      labels:
        app: victoriametrics
    spec:
      containers:
        - name: victoriametrics
          image: victoriametrics/victoria-metrics:v1.93.0
          args:
            - -storageDataPath=/storage
            - -retentionPeriod=12  # 12 months
            - -memory.allowedPercent=80
            - -search.maxQueryDuration=60s
            - -search.maxConcurrentRequests=12
          ports:
            - containerPort: 8428
              name: http
          volumeMounts:
            - name: storage
              mountPath: /storage
          resources:
            requests:
              cpu: 1000m
              memory: 4Gi
            limits:
              cpu: 4000m
              memory: 16Gi
  volumeClaimTemplates:
    - metadata:
        name: storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 500Gi
```

**Prometheus Remote Write to VictoriaMetrics**:

```yaml
# prometheus.yml
remote_write:
  - url: http://victoriametrics.monitoring.svc:8428/api/v1/write
    queue_config:
      max_samples_per_send: 10000
      max_shards: 30
      capacity: 50000
```

## Advanced PromQL

PromQL (Prometheus Query Language) is essential for extracting insights from metrics. Advanced PromQL techniques help analyze complex ML workloads.

### Complex Aggregations for ML Metrics

#### 1. GPU Utilization Analysis

```promql
# Average GPU utilization across training jobs
avg(
  rate(nvidia_gpu_duty_cycle[5m])
) by (job_name, gpu_id)

# GPU memory usage percentage
100 * (
  nvidia_gpu_memory_used_bytes /
  nvidia_gpu_memory_total_bytes
)

# Identify underutilized GPUs (< 50% utilization)
count(
  rate(nvidia_gpu_duty_cycle[5m]) < 0.5
) by (node, gpu_id)

# GPU utilization heatmap by hour
avg_over_time(
  nvidia_gpu_duty_cycle[1h]
) by (gpu_id)
```

#### 2. Model Inference Latency

```promql
# 95th percentile inference latency
histogram_quantile(0.95,
  rate(model_inference_duration_seconds_bucket[5m])
) by (model_name, version)

# Latency SLO compliance (< 100ms)
(
  sum(rate(model_inference_duration_seconds_bucket{le="0.1"}[5m])) by (model_name)
  /
  sum(rate(model_inference_duration_seconds_count[5m])) by (model_name)
) * 100

# Compare latency across model versions
histogram_quantile(0.99,
  rate(model_inference_duration_seconds_bucket[5m])
) by (model_name, version)
```

#### 3. Training Job Metrics

```promql
# Training loss trend
avg(training_loss) by (job_id, epoch)

# Training throughput (samples/second)
rate(training_samples_processed_total[5m]) by (job_id)

# Estimated time to completion
(training_total_steps - training_current_step) /
rate(training_current_step[10m])

# GPU efficiency (actual vs. theoretical throughput)
(
  rate(training_samples_processed_total[5m]) /
  on(job_id) group_left()
  training_gpu_count
) / training_theoretical_max_throughput
```

#### 4. Data Pipeline Metrics

```promql
# Data processing rate
rate(data_records_processed_total[5m]) by (pipeline_stage)

# Pipeline bottleneck detection
topk(5,
  rate(data_stage_duration_seconds_sum[5m]) /
  rate(data_stage_duration_seconds_count[5m])
) by (pipeline_stage)

# Data quality score
avg(data_quality_score) by (dataset, validation_rule)

# Anomaly detection in data volume
abs(
  (
    rate(data_records_processed_total[5m]) -
    avg_over_time(rate(data_records_processed_total[5m])[1h:5m])
  ) /
  stddev_over_time(rate(data_records_processed_total[5m])[1h:5m])
) > 3
```

### Subqueries and Advanced Functions

```promql
# Detect anomalies in model accuracy
# (deviation from 1-hour moving average)
abs(
  model_accuracy -
  avg_over_time(model_accuracy[1h])
) > 0.05

# Rate of change in error rate
deriv(
  rate(model_errors_total[5m])[10m:]
)

# Predict disk space exhaustion
predict_linear(
  node_filesystem_avail_bytes[1h],
  24 * 3600
) < 0

# Custom anomaly detection using stddev
(
  abs(
    metric_value -
    avg_over_time(metric_value[1h])
  )
) > (
  2 * stddev_over_time(metric_value[1h])
)
```

## Recording Rules

Recording rules pre-compute expensive queries, improving dashboard performance and enabling complex aggregations.

### ML-Specific Recording Rules

```yaml
# ml-recording-rules.yml
groups:
  - name: ml_training_metrics
    interval: 30s
    rules:
      # GPU utilization by job
      - record: job:gpu_utilization:avg
        expr: |
          avg(
            rate(nvidia_gpu_duty_cycle[5m])
          ) by (job_name, namespace)

      # GPU memory usage percentage
      - record: job:gpu_memory_usage_percent:avg
        expr: |
          100 * avg(
            nvidia_gpu_memory_used_bytes /
            nvidia_gpu_memory_total_bytes
          ) by (job_name, namespace)

      # Training throughput (samples/sec)
      - record: job:training_throughput:rate5m
        expr: |
          sum(
            rate(training_samples_processed_total[5m])
          ) by (job_id, job_name)

      # Training cost per sample (GPU hours per 1000 samples)
      - record: job:training_cost_per_ksample:rate5m
        expr: |
          (
            sum(
              rate(container_gpu_allocation[5m])
            ) by (job_id)
            /
            sum(
              rate(training_samples_processed_total[5m])
            ) by (job_id)
          ) * 1000

  - name: ml_inference_metrics
    interval: 30s
    rules:
      # Inference request rate
      - record: model:request_rate:rate5m
        expr: |
          sum(
            rate(model_predictions_total[5m])
          ) by (model_name, model_version)

      # P50, P95, P99 latency
      - record: model:latency_p50:rate5m
        expr: |
          histogram_quantile(0.50,
            sum(
              rate(model_inference_duration_seconds_bucket[5m])
            ) by (model_name, model_version, le)
          )

      - record: model:latency_p95:rate5m
        expr: |
          histogram_quantile(0.95,
            sum(
              rate(model_inference_duration_seconds_bucket[5m])
            ) by (model_name, model_version, le)
          )

      - record: model:latency_p99:rate5m
        expr: |
          histogram_quantile(0.99,
            sum(
              rate(model_inference_duration_seconds_bucket[5m])
            ) by (model_name, model_version, le)
          )

      # Error rate
      - record: model:error_rate:rate5m
        expr: |
          sum(
            rate(model_errors_total[5m])
          ) by (model_name, model_version)
          /
          sum(
            rate(model_predictions_total[5m])
          ) by (model_name, model_version)

      # Model availability (success rate)
      - record: model:availability:rate5m
        expr: |
          (
            sum(
              rate(model_predictions_total[5m])
            ) by (model_name, model_version)
            -
            sum(
              rate(model_errors_total[5m])
            ) by (model_name, model_version)
          )
          /
          sum(
            rate(model_predictions_total[5m])
          ) by (model_name, model_version)

  - name: ml_data_quality
    interval: 60s
    rules:
      # Data processing rate by pipeline
      - record: pipeline:processing_rate:rate5m
        expr: |
          sum(
            rate(data_records_processed_total[5m])
          ) by (pipeline_name, stage)

      # Data validation failure rate
      - record: pipeline:validation_failure_rate:rate5m
        expr: |
          sum(
            rate(data_validation_failures_total[5m])
          ) by (pipeline_name, validation_rule)
          /
          sum(
            rate(data_records_processed_total[5m])
          ) by (pipeline_name)

      # Feature drift score (requires custom metric)
      - record: feature:drift_score:avg
        expr: |
          avg(
            feature_distribution_distance
          ) by (feature_name, dataset)
```

## Custom Exporters

For ML-specific metrics not available through standard exporters, custom exporters are essential.

### Building a PyTorch Training Exporter

```python
# pytorch_exporter.py
from prometheus_client import (
    start_http_server,
    Gauge,
    Counter,
    Histogram,
    Summary
)
import time
import torch

# Define metrics
training_loss = Gauge(
    'training_loss',
    'Current training loss',
    ['job_id', 'epoch']
)

training_accuracy = Gauge(
    'training_accuracy',
    'Current training accuracy',
    ['job_id', 'epoch', 'phase']
)

samples_processed = Counter(
    'training_samples_processed_total',
    'Total number of samples processed',
    ['job_id']
)

batch_duration = Histogram(
    'training_batch_duration_seconds',
    'Time spent processing a batch',
    ['job_id'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

gpu_memory_allocated = Gauge(
    'training_gpu_memory_allocated_bytes',
    'GPU memory allocated by PyTorch',
    ['job_id', 'gpu_id']
)

learning_rate = Gauge(
    'training_learning_rate',
    'Current learning rate',
    ['job_id']
)

gradient_norm = Summary(
    'training_gradient_norm',
    'Gradient norm',
    ['job_id', 'layer']
)

# TODO: Implement metric collection during training
class MetricsCollector:
    def __init__(self, job_id, port=8000):
        self.job_id = job_id
        self.current_epoch = 0
        # TODO: Start Prometheus HTTP server
        start_http_server(port)

    def update_loss(self, loss_value, epoch):
        """Update training loss metric"""
        # TODO: Set gauge value with labels
        training_loss.labels(
            job_id=self.job_id,
            epoch=epoch
        ).set(loss_value)

    def update_accuracy(self, acc_value, epoch, phase='train'):
        """Update training/validation accuracy"""
        # TODO: Set gauge value
        training_accuracy.labels(
            job_id=self.job_id,
            epoch=epoch,
            phase=phase
        ).set(acc_value)

    def record_batch(self, batch_size):
        """Record processed samples"""
        # TODO: Increment counter
        samples_processed.labels(
            job_id=self.job_id
        ).inc(batch_size)

    def observe_batch_duration(self, duration):
        """Record batch processing time"""
        # TODO: Observe histogram
        batch_duration.labels(
            job_id=self.job_id
        ).observe(duration)

    def update_gpu_memory(self):
        """Update GPU memory usage from PyTorch"""
        # TODO: Get GPU memory from PyTorch and update gauge
        for gpu_id in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(gpu_id)
            gpu_memory_allocated.labels(
                job_id=self.job_id,
                gpu_id=str(gpu_id)
            ).set(allocated)

    def update_learning_rate(self, lr):
        """Update current learning rate"""
        # TODO: Set gauge value
        learning_rate.labels(
            job_id=self.job_id
        ).set(lr)

    def record_gradient_norm(self, model):
        """Record gradient norms for each layer"""
        # TODO: Calculate and record gradient norms
        for name, param in model.named_parameters():
            if param.grad is not None:
                norm = param.grad.norm().item()
                gradient_norm.labels(
                    job_id=self.job_id,
                    layer=name
                ).observe(norm)

# Usage example
# TODO: Integrate into training loop
def train_with_metrics(model, dataloader, job_id):
    collector = MetricsCollector(job_id)

    for epoch in range(num_epochs):
        for batch_idx, (data, target) in enumerate(dataloader):
            start_time = time.time()

            # Training step
            loss = train_step(model, data, target)

            # Collect metrics
            collector.update_loss(loss.item(), epoch)
            collector.record_batch(len(data))
            collector.observe_batch_duration(time.time() - start_time)
            collector.update_gpu_memory()

            if batch_idx % 100 == 0:
                collector.record_gradient_norm(model)
```

## Performance Optimization

### 1. Reduce Cardinality

High cardinality (many unique label combinations) kills Prometheus performance.

```yaml
# BAD: High cardinality
- record: request_duration
  labels:
    user_id: "12345"  # Thousands of unique users
    request_id: "abc-123"  # Millions of unique requests

# GOOD: Low cardinality
- record: request_duration
  labels:
    endpoint: "/api/predict"
    method: "POST"
    status_code: "200"
```

### 2. Optimize Scrape Intervals

```yaml
# Fast-changing metrics (e.g., request rates)
scrape_interval: 15s

# Slow-changing metrics (e.g., resource capacity)
scrape_interval: 60s

# Very slow metrics (e.g., daily aggregations)
scrape_interval: 300s
```

### 3. Use Recording Rules for Complex Queries

```yaml
# Instead of running this expensive query on every dashboard load:
# histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Create a recording rule:
- record: job:http_request_duration_seconds:p99
  expr: |
    histogram_quantile(0.99,
      rate(http_request_duration_seconds_bucket[5m])
    )
```

## Production Best Practices

### 1. Resource Limits

```yaml
resources:
  requests:
    cpu: 2000m
    memory: 8Gi
  limits:
    cpu: 4000m
    memory: 16Gi
```

### 2. Retention Policies

- Local TSDB: 15-30 days
- Thanos/Cortex raw data: 30-90 days
- Thanos 5m downsampled: 6-12 months
- Thanos 1h downsampled: 2-5 years

### 3. Monitoring Prometheus Itself

```yaml
# Monitor Prometheus health
up{job="prometheus"}

# Monitor scrape duration
scrape_duration_seconds

# Monitor TSDB size
prometheus_tsdb_storage_blocks_bytes

# Monitor query performance
prometheus_engine_query_duration_seconds
```

### 4. Security

- Enable TLS for all communication
- Use authentication for Prometheus API
- Implement network policies
- Regularly update Prometheus versions
- Audit access logs

## Summary

Advanced Prometheus techniques are essential for AI infrastructure:

1. **Federation** enables multi-cluster monitoring and aggregation
2. **Long-term storage** (Thanos, Cortex, VictoriaMetrics) provides historical analysis
3. **Advanced PromQL** extracts insights from complex ML metrics
4. **Recording rules** improve query performance
5. **Custom exporters** capture ML-specific metrics
6. **Performance optimization** ensures scalability

In the next lecture, we'll explore distributed tracing to understand request flows through ML pipelines.

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Thanos Documentation](https://thanos.io/tip/thanos/quick-tutorial.md/)
- [Cortex Documentation](https://cortexmetrics.io/docs/)
- [PromQL for Humans](https://timber.io/blog/promql-for-humans/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
