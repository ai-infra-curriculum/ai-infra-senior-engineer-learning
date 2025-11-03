# Lecture 03: Log Aggregation

## Learning Objectives

By the end of this lecture, you will be able to:

- Design log aggregation architectures using ELK/EFK stack or Loki collecting logs from distributed ML workloads with centralized search and analysis
- Implement structured logging patterns using JSON format with consistent fields (timestamp, severity, service, trace_id, user_id) enabling efficient querying
- Configure log collection pipelines with Fluentd/Fluent Bit or Promtail handling log parsing, enrichment, filtering, and routing to appropriate storage backends
- Architect cost-optimized log retention using hot/warm/cold storage tiers, log sampling, and compression achieving 10x cost reduction for long-term storage
- Design log-based metrics extracting counters and histograms from logs enabling alerting on patterns without maintaining separate metric instrumentation
- Implement log correlation strategies linking logs across services using trace IDs, request IDs, and session IDs for end-to-end debugging
- Build log analysis workflows using Kibana, Grafana, or custom tooling for real-time monitoring, anomaly detection, and historical analysis
- Optimize log infrastructure managing log volume, query performance, index lifecycle management, and cluster sizing for production workloads

## Table of Contents
1. [Introduction](#introduction)
2. [Log Aggregation Architecture](#log-aggregation-architecture)
3. [ELK Stack](#elk-stack)
4. [EFK Stack](#efk-stack)
5. [Loki](#loki)
6. [Structured Logging](#structured-logging)
7. [Log-Based Metrics](#log-based-metrics)
8. [Query and Analysis](#query-and-analysis)
9. [Cost Optimization](#cost-optimization)
10. [Production Best Practices](#production-best-practices)

## Introduction

Log aggregation is the practice of collecting, centralizing, and analyzing logs from distributed systems. For AI infrastructure, effective log aggregation is critical for debugging training failures, understanding model behavior, tracking data pipeline issues, and maintaining system health.

### Why Log Aggregation Matters

**Challenges in Distributed ML Systems**:
- Training jobs span multiple nodes and GPUs
- Logs are ephemeral in containerized environments
- Debugging requires correlating logs across services
- Real-time monitoring of long-running jobs
- Compliance and audit requirements

**Without log aggregation**:
- SSH into individual pods to view logs
- Logs lost when pods are terminated
- No correlation between related events
- Difficult to identify patterns across services
- No historical analysis capability

**With log aggregation**:
- Centralized search across all services
- Persistent storage of historical logs
- Real-time streaming and alerting
- Pattern detection and anomaly identification
- Compliance and audit trails

## Log Aggregation Architecture

### Common Pattern

```
┌──────────────────────────────────────────────────────────┐
│                    Applications                           │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐        │
│  │Training│  │ Serving│  │   API  │  │  Data  │        │
│  │  Job   │  │ Service│  │Gateway │  │Pipeline│        │
│  └────────┘  └────────┘  └────────┘  └────────┘        │
│      │            │            │            │            │
│      └────────────┴────────────┴────────────┘            │
│                        ↓                                  │
│              (stdout/stderr logs)                         │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│                  Log Collectors                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Fluentd   │  │ Fluent Bit │  │  Filebeat  │        │
│  │ (DaemonSet)│  │ (DaemonSet)│  │ (DaemonSet)│        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│               Aggregation/Processing                      │
│  ┌──────────────────────────────────────────┐           │
│  │  Logstash / Kafka / Fluentd              │           │
│  │  (Parse, filter, enrich, route)          │           │
│  └──────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────┘
                         ↓
       ┌─────────────────┴─────────────────┐
       ↓                                   ↓
┌─────────────┐                    ┌─────────────┐
│   Storage   │                    │   Stream    │
│Elasticsearch│                    │    Kafka    │
│  Loki, S3   │                    │             │
└─────────────┘                    └─────────────┘
       ↓
┌──────────────────────────────────────────────────────────┐
│                  Visualization/Query                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Kibana   │  │  Grafana   │  │   Custom   │        │
│  │            │  │            │  │     UI     │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
```

### Key Components

1. **Collection**: Gather logs from applications (Fluentd, Fluent Bit, Filebeat)
2. **Processing**: Parse, filter, enrich (Logstash, Fluentd)
3. **Storage**: Persist logs (Elasticsearch, Loki, S3)
4. **Visualization**: Query and analyze (Kibana, Grafana)

## ELK Stack

ELK (Elasticsearch, Logstash, Kibana) is the most popular log aggregation stack.

### Architecture

```
Applications → Filebeat/Fluentd → Logstash → Elasticsearch → Kibana
```

### Elasticsearch Deployment

```yaml
# elasticsearch.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: logging
spec:
  version: 8.10.0
  nodeSets:
    # Master nodes
    - name: master
      count: 3
      config:
        node.roles: ["master"]
        xpack.security.enabled: true
        xpack.security.transport.ssl.enabled: true
      volumeClaimTemplates:
        - metadata:
            name: elasticsearch-data
          spec:
            accessModes:
              - ReadWriteOnce
            resources:
              requests:
                storage: 100Gi
            storageClassName: fast-ssd
      podTemplate:
        spec:
          containers:
            - name: elasticsearch
              resources:
                requests:
                  memory: 4Gi
                  cpu: 2000m
                limits:
                  memory: 4Gi
                  cpu: 2000m
              env:
                - name: ES_JAVA_OPTS
                  value: "-Xms2g -Xmx2g"

    # Data nodes (hot tier - recent data)
    - name: data-hot
      count: 3
      config:
        node.roles: ["data_hot", "data_content"]
      volumeClaimTemplates:
        - metadata:
            name: elasticsearch-data
          spec:
            accessModes:
              - ReadWriteOnce
            resources:
              requests:
                storage: 500Gi
            storageClassName: fast-ssd
      podTemplate:
        spec:
          containers:
            - name: elasticsearch
              resources:
                requests:
                  memory: 16Gi
                  cpu: 4000m
                limits:
                  memory: 16Gi
                  cpu: 4000m
              env:
                - name: ES_JAVA_OPTS
                  value: "-Xms8g -Xmx8g"

    # Warm tier (older data)
    - name: data-warm
      count: 2
      config:
        node.roles: ["data_warm"]
      volumeClaimTemplates:
        - metadata:
            name: elasticsearch-data
          spec:
            accessModes:
              - ReadWriteOnce
            resources:
              requests:
                storage: 2Ti
            storageClassName: standard
      podTemplate:
        spec:
          containers:
            - name: elasticsearch
              resources:
                requests:
                  memory: 8Gi
                  cpu: 2000m
                limits:
                  memory: 8Gi
                  cpu: 2000m
              env:
                - name: ES_JAVA_OPTS
                  value: "-Xms4g -Xmx4g"
```

### Index Lifecycle Management (ILM)

```json
// ilm-policy.json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "allocate": {
            "require": {
              "data": "warm"
            }
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "allocate": {
            "require": {
              "data": "cold"
            }
          },
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Logstash Pipeline

```yaml
# logstash-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
  namespace: logging
data:
  logstash.conf: |
    input {
      # Receive logs from Filebeat
      beats {
        port => 5044
      }

      # TODO: Add additional inputs as needed
      # kafka {
      #   bootstrap_servers => "kafka:9092"
      #   topics => ["ml-logs"]
      # }
    }

    filter {
      # Parse JSON logs
      if [message] =~ /^\{.*\}$/ {
        json {
          source => "message"
        }
      }

      # Parse ML training logs
      # TODO: Customize grok patterns for your log format
      if [kubernetes][labels][job-type] == "training" {
        grok {
          match => {
            "message" => "Epoch: %{NUMBER:epoch:int}, Loss: %{NUMBER:loss:float}, Accuracy: %{NUMBER:accuracy:float}"
          }
        }

        # Extract GPU metrics from logs
        grok {
          match => {
            "message" => "GPU %{NUMBER:gpu_id:int}: Utilization: %{NUMBER:gpu_util:float}%, Memory: %{NUMBER:gpu_mem:float}GB"
          }
        }
      }

      # Parse model serving logs
      if [kubernetes][labels][app] == "model-serving" {
        grok {
          match => {
            "message" => "Prediction request - Model: %{WORD:model_name}, Version: %{WORD:model_version}, Latency: %{NUMBER:latency_ms:float}ms"
          }
        }
      }

      # Add timestamp
      date {
        match => ["timestamp", "ISO8601"]
        target => "@timestamp"
      }

      # Enrich with Kubernetes metadata
      mutate {
        add_field => {
          "cluster" => "${CLUSTER_NAME:unknown}"
          "environment" => "${ENVIRONMENT:production}"
        }
      }

      # TODO: Add custom enrichment logic
      # Lookup user information, add cost tags, etc.
    }

    output {
      # Send to Elasticsearch
      elasticsearch {
        hosts => ["https://elasticsearch.logging.svc:9200"]
        index => "ml-logs-%{+YYYY.MM.dd}"
        user => "${ES_USER}"
        password => "${ES_PASSWORD}"
        ssl => true
        cacert => "/etc/logstash/certs/ca.crt"
      }

      # TODO: Optional: Send to S3 for long-term archival
      # s3 {
      #   bucket => "ml-logs-archive"
      #   region => "us-east-1"
      #   codec => "json_lines"
      #   time_file => 60
      # }

      # Debug output (remove in production)
      # stdout { codec => rubydebug }
    }
```

### Kibana Deployment

```yaml
# kibana.yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: logging
spec:
  version: 8.10.0
  count: 2
  elasticsearchRef:
    name: elasticsearch
  podTemplate:
    spec:
      containers:
        - name: kibana
          resources:
            requests:
              memory: 2Gi
              cpu: 1000m
            limits:
              memory: 2Gi
              cpu: 2000m
  http:
    tls:
      selfSignedCertificate:
        disabled: true
```

### Filebeat DaemonSet

```yaml
# filebeat.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: logging
data:
  filebeat.yml: |
    filebeat.inputs:
      - type: container
        paths:
          - /var/log/containers/*.log
        processors:
          - add_kubernetes_metadata:
              host: ${NODE_NAME}
              matchers:
                - logs_path:
                    logs_path: "/var/log/containers/"

    # TODO: Configure output to Logstash or Elasticsearch
    output.logstash:
      hosts: ["logstash.logging.svc:5044"]

    # OR direct to Elasticsearch
    # output.elasticsearch:
    #   hosts: ["https://elasticsearch.logging.svc:9200"]
    #   username: "${ES_USER}"
    #   password: "${ES_PASSWORD}"
    #   ssl.certificate_authorities: ["/etc/filebeat/certs/ca.crt"]

    setup.ilm.enabled: true
    setup.ilm.rollover_alias: "filebeat"
    setup.ilm.pattern: "{now/d}-000001"
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: logging
spec:
  selector:
    matchLabels:
      app: filebeat
  template:
    metadata:
      labels:
        app: filebeat
    spec:
      serviceAccountName: filebeat
      terminationGracePeriodSeconds: 30
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
        - name: filebeat
          image: docker.elastic.co/beats/filebeat:8.10.0
          args: [
            "-c", "/etc/filebeat.yml",
            "-e",
          ]
          env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
          securityContext:
            runAsUser: 0
          resources:
            requests:
              memory: 200Mi
              cpu: 100m
            limits:
              memory: 500Mi
              cpu: 500m
          volumeMounts:
            - name: config
              mountPath: /etc/filebeat.yml
              readOnly: true
              subPath: filebeat.yml
            - name: data
              mountPath: /usr/share/filebeat/data
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: varlog
              mountPath: /var/log
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: filebeat-config
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: varlog
          hostPath:
            path: /var/log
        - name: data
          hostPath:
            path: /var/lib/filebeat-data
            type: DirectoryOrCreate
```

## EFK Stack

EFK (Elasticsearch, Fluentd, Kibana) replaces Logstash with Fluentd, which is lighter weight and more Kubernetes-native.

### Fluentd DaemonSet

```yaml
# fluentd.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: logging
data:
  fluent.conf: |
    # Input: Collect container logs
    <source>
      @type tail
      @id in_tail_container_logs
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>

    # TODO: Add Kubernetes metadata
    <filter kubernetes.**>
      @type kubernetes_metadata
      @id filter_kube_metadata
      kubernetes_url "#{ENV['FLUENT_FILTER_KUBERNETES_URL'] || 'https://' + ENV.fetch('KUBERNETES_SERVICE_HOST') + ':' + ENV.fetch('KUBERNETES_SERVICE_PORT') + '/api'}"
      verify_ssl "#{ENV['KUBERNETES_VERIFY_SSL'] || true}"
      ca_file "#{ENV['KUBERNETES_CA_FILE']}"
    </filter>

    # TODO: Parse ML training logs
    <filter kubernetes.var.log.containers.**training**.log>
      @type parser
      key_name log
      reserve_data true
      <parse>
        @type regexp
        expression /^Epoch: (?<epoch>\d+), Loss: (?<loss>[\d.]+), Accuracy: (?<accuracy>[\d.]+)/
        types epoch:integer,loss:float,accuracy:float
      </parse>
    </filter>

    # TODO: Parse GPU metrics from logs
    <filter kubernetes.var.log.containers.**gpu**.log>
      @type parser
      key_name log
      reserve_data true
      <parse>
        @type regexp
        expression /^GPU (?<gpu_id>\d+): Utilization: (?<gpu_util>[\d.]+)%, Memory: (?<gpu_mem>[\d.]+)GB/
        types gpu_id:integer,gpu_util:float,gpu_mem:float
      </parse>
    </filter>

    # Output to Elasticsearch
    <match **>
      @type elasticsearch
      @id out_es
      @log_level info
      include_tag_key true
      host "#{ENV['FLUENT_ELASTICSEARCH_HOST']}"
      port "#{ENV['FLUENT_ELASTICSEARCH_PORT']}"
      scheme "#{ENV['FLUENT_ELASTICSEARCH_SCHEME'] || 'http'}"
      ssl_verify "#{ENV['FLUENT_ELASTICSEARCH_SSL_VERIFY'] || 'true'}"
      user "#{ENV['FLUENT_ELASTICSEARCH_USER']}"
      password "#{ENV['FLUENT_ELASTICSEARCH_PASSWORD']}"
      logstash_format true
      logstash_prefix ml-logs
      <buffer>
        @type file
        path /var/log/fluentd-buffers/kubernetes.system.buffer
        flush_mode interval
        retry_type exponential_backoff
        flush_thread_count 2
        flush_interval 5s
        retry_forever
        retry_max_interval 30
        chunk_limit_size 2M
        queue_limit_length 8
        overflow_action block
      </buffer>
    </match>
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccountName: fluentd
      containers:
        - name: fluentd
          image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
          env:
            - name: FLUENT_ELASTICSEARCH_HOST
              value: "elasticsearch.logging.svc"
            - name: FLUENT_ELASTICSEARCH_PORT
              value: "9200"
            - name: FLUENT_ELASTICSEARCH_SCHEME
              value: "https"
            - name: FLUENT_ELASTICSEARCH_USER
              value: "elastic"
            - name: FLUENT_ELASTICSEARCH_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: elasticsearch-credentials
                  key: password
          resources:
            requests:
              cpu: 100m
              memory: 200Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: config
              mountPath: /fluentd/etc/fluent.conf
              subPath: fluent.conf
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: config
          configMap:
            name: fluentd-config
```

## Loki

Loki is a horizontally-scalable, multi-tenant log aggregation system inspired by Prometheus. It's more cost-effective than Elasticsearch for many use cases.

### Loki Architecture

```
Applications → Promtail → Loki → Grafana
```

**Key Differences from Elasticsearch**:
- Indexes labels, not full text (like Prometheus)
- Stores compressed log chunks
- 10x cheaper storage
- Better for already structured logs
- Less powerful search compared to Elasticsearch

### Loki Deployment

```yaml
# loki.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
  namespace: logging
data:
  loki.yaml: |
    auth_enabled: false

    server:
      http_listen_port: 3100
      grpc_listen_port: 9096

    common:
      path_prefix: /loki
      storage:
        filesystem:
          chunks_directory: /loki/chunks
          rules_directory: /loki/rules
      replication_factor: 1
      ring:
        instance_addr: 127.0.0.1
        kvstore:
          store: inmemory

    schema_config:
      configs:
        - from: 2023-01-01
          store: boltdb-shipper
          object_store: s3
          schema: v11
          index:
            prefix: index_
            period: 24h

    storage_config:
      boltdb_shipper:
        active_index_directory: /loki/index
        cache_location: /loki/cache
        shared_store: s3
      aws:
        s3: s3://us-east-1/ml-logs-loki
        s3forcepathstyle: true

    limits_config:
      enforce_metric_name: false
      reject_old_samples: true
      reject_old_samples_max_age: 168h
      ingestion_rate_mb: 10
      ingestion_burst_size_mb: 20

    chunk_store_config:
      max_look_back_period: 0s

    table_manager:
      retention_deletes_enabled: true
      retention_period: 720h  # 30 days
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: loki
  namespace: logging
spec:
  serviceName: loki
  replicas: 3
  selector:
    matchLabels:
      app: loki
  template:
    metadata:
      labels:
        app: loki
    spec:
      containers:
        - name: loki
          image: grafana/loki:2.9.0
          args:
            - -config.file=/etc/loki/loki.yaml
          ports:
            - containerPort: 3100
              name: http
            - containerPort: 9096
              name: grpc
          volumeMounts:
            - name: config
              mountPath: /etc/loki
            - name: storage
              mountPath: /loki
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
      volumes:
        - name: config
          configMap:
            name: loki-config
  volumeClaimTemplates:
    - metadata:
        name: storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
```

### Promtail for Log Collection

```yaml
# promtail.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: logging
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0

    positions:
      filename: /tmp/positions.yaml

    clients:
      - url: http://loki.logging.svc:3100/loki/api/v1/push

    scrape_configs:
      # TODO: Scrape Kubernetes pod logs
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: app
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_pod_container_name]
            target_label: container
          - source_labels: [__meta_kubernetes_pod_label_job_type]
            target_label: job_type
          - source_labels: [__meta_kubernetes_pod_label_model_name]
            target_label: model_name

      # TODO: Parse ML training logs
      - job_name: ml-training
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_job_type]
            action: keep
            regex: training
        pipeline_stages:
          - regex:
              expression: 'Epoch: (?P<epoch>\\d+), Loss: (?P<loss>[\\d.]+), Accuracy: (?P<accuracy>[\\d.]+)'
          - labels:
              epoch:
              loss:
              accuracy:
          - metrics:
              training_loss:
                type: Gauge
                description: Training loss
                source: loss
                config:
                  action: set
              training_accuracy:
                type: Gauge
                description: Training accuracy
                source: accuracy
                config:
                  action: set
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: logging
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      serviceAccountName: promtail
      containers:
        - name: promtail
          image: grafana/promtail:2.9.0
          args:
            - -config.file=/etc/promtail/promtail.yaml
          volumeMounts:
            - name: config
              mountPath: /etc/promtail
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
      volumes:
        - name: config
          configMap:
            name: promtail-config
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
```

## Structured Logging

Structured logging outputs logs in a consistent, machine-parsable format (typically JSON).

### Python Structured Logging

```python
# structured_logging.py
import logging
import json
import sys
from datetime import datetime

# TODO: Implement structured JSON logger
class StructuredLogger:
    def __init__(self, name, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)

    def info(self, message, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, extra=kwargs)

    def warning(self, message, **kwargs):
        self.logger.warning(message, extra=kwargs)

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        # TODO: Build structured log entry
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename',
                             'funcName', 'levelname', 'levelno', 'lineno',
                             'module', 'msecs', 'message', 'pathname',
                             'process', 'processName', 'relativeCreated',
                             'thread', 'threadName', 'exc_info', 'exc_text',
                             'stack_info']:
                    log_data[key] = value

        return json.dumps(log_data)

# Usage
logger = StructuredLogger(__name__)

# TODO: Log with structured fields
logger.info(
    "Training epoch completed",
    epoch=5,
    loss=0.234,
    accuracy=0.945,
    model_name="resnet50",
    batch_size=32,
    learning_rate=0.001
)

# Output:
# {"timestamp": "2025-01-15T10:30:45.123456", "level": "INFO",
#  "logger": "__main__", "message": "Training epoch completed",
#  "epoch": 5, "loss": 0.234, "accuracy": 0.945,
#  "model_name": "resnet50", "batch_size": 32, "learning_rate": 0.001}
```

### ML Training Logging

```python
# ml_training_logging.py
from structured_logging import StructuredLogger
import torch

logger = StructuredLogger("ml.training")

# TODO: Comprehensive training logging
def train_epoch(model, dataloader, optimizer, epoch, job_id):
    logger.info(
        "Starting training epoch",
        job_id=job_id,
        epoch=epoch,
        batch_count=len(dataloader),
        learning_rate=optimizer.param_groups[0]['lr']
    )

    for batch_idx, (data, target) in enumerate(dataloader):
        # Training step
        output = model(data)
        loss = criterion(output, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # TODO: Log batch metrics
        if batch_idx % 100 == 0:
            logger.info(
                "Batch completed",
                job_id=job_id,
                epoch=epoch,
                batch=batch_idx,
                loss=float(loss),
                samples_processed=(batch_idx + 1) * len(data),
                gpu_memory_allocated=torch.cuda.memory_allocated() / 1e9,
                gpu_memory_reserved=torch.cuda.memory_reserved() / 1e9
            )

    logger.info(
        "Epoch completed",
        job_id=job_id,
        epoch=epoch
    )
```

## Log-Based Metrics

Extract metrics from logs for alerting and visualization.

### Elasticsearch Metric Extraction

```json
// Create index pattern with metric extraction
PUT _ingest/pipeline/ml-training-metrics
{
  "description": "Extract metrics from ML training logs",
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": ["Epoch: %{NUMBER:epoch:int}, Loss: %{NUMBER:loss:float}, Accuracy: %{NUMBER:accuracy:float}"]
      }
    },
    {
      "script": {
        "lang": "painless",
        "source": "ctx.training_progress = (ctx.epoch / ctx.total_epochs) * 100"
      }
    }
  ]
}
```

### Loki Metric Extraction

```yaml
# In Promtail pipeline_stages
pipeline_stages:
  # TODO: Extract metrics from logs
  - regex:
      expression: 'Loss: (?P<loss>[\\d.]+)'
  - metrics:
      training_loss:
        type: Gauge
        description: Training loss from logs
        source: loss
        config:
          action: set
  - labels:
      loss:
```

## Query and Analysis

### Elasticsearch Query DSL

```python
# elasticsearch_queries.py
from elasticsearch import Elasticsearch

es = Elasticsearch(["https://elasticsearch.logging.svc:9200"])

# TODO: Query for training job errors
def find_training_errors(job_id, hours=24):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"kubernetes.labels.job_id": job_id}},
                    {"match": {"level": "ERROR"}},
                    {"range": {
                        "@timestamp": {
                            "gte": f"now-{hours}h",
                            "lte": "now"
                        }
                    }}
                ]
            }
        },
        "sort": [{"@timestamp": "desc"}],
        "size": 100
    }

    result = es.search(index="ml-logs-*", body=query)
    return result["hits"]["hits"]

# TODO: Aggregate GPU utilization from logs
def aggregate_gpu_utilization(hours=1):
    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": f"now-{hours}h"
                }
            }
        },
        "aggs": {
            "avg_gpu_util": {
                "avg": {"field": "gpu_util"}
            },
            "gpu_utilization_over_time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": "5m"
                },
                "aggs": {
                    "avg_util": {"avg": {"field": "gpu_util"}}
                }
            }
        }
    }

    result = es.search(index="ml-logs-*", body=query, size=0)
    return result["aggregations"]
```

### LogQL (Loki Query Language)

```logql
// Find all ERROR logs for a specific job
{job_type="training", job_id="abc123"} |= "ERROR"

// Calculate rate of errors
rate({job_type="training"} |= "ERROR" [5m])

// Extract and aggregate metrics
sum(rate({job_type="training"} | json | __error__="" | unwrap loss [5m])) by (model_name)

// Pattern matching
{namespace="ml-platform"} |~ "GPU \\d+: Utilization: (\\d+)%"

// Multi-line grep
{app="training-job"} |= "OutOfMemoryError" | line_format "{{.pod}}: {{.message}}"
```

## Cost Optimization

### 1. Log Filtering at Source

```yaml
# Filter out verbose debug logs
filters:
  - type: exclude
    regex: "^DEBUG:"
  - type: exclude
    regex: "health check"
```

### 2. Sampling

```python
# Sample 10% of INFO logs, keep all ERROR logs
import random

def should_log(level, message):
    if level in ["ERROR", "CRITICAL"]:
        return True
    if level == "INFO":
        return random.random() < 0.1
    return False
```

### 3. Index Lifecycle Management

- Hot tier (SSD): 7 days
- Warm tier (HDD): 30 days
- Cold tier (S3): 90 days
- Delete: After 90 days

### 4. Choose Loki for Cost Savings

For many ML workloads, Loki provides 10x cost savings compared to Elasticsearch.

## Production Best Practices

1. **Use structured logging**: JSON format for easy parsing
2. **Include context**: Job ID, user ID, request ID, trace ID
3. **Set appropriate log levels**: DEBUG for development, INFO/WARNING for production
4. **Implement log sampling**: Reduce volume while maintaining visibility
5. **Use index lifecycle management**: Automatically manage retention and costs
6. **Monitor log pipeline**: Alert on collector failures, high latency
7. **Secure logs**: Contain sensitive data (PII, credentials)
8. **Correlate with traces and metrics**: Use trace IDs in logs

## Summary

Log aggregation is essential for ML infrastructure:
- Centralized visibility across distributed systems
- Historical analysis and debugging
- Real-time alerting and monitoring
- Compliance and audit trails

Choose the right stack for your needs:
- ELK/EFK: Full-text search, complex queries
- Loki: Cost-effective, label-based indexing
- Both: Use Loki for most logs, Elasticsearch for searchable logs

In the next lecture, we'll explore ML-specific observability patterns.

## Further Reading

- [Elasticsearch Documentation](https://www.elastic.co/guide/index.html)
- [Fluentd Documentation](https://docs.fluentd.org/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- "Logging in Action" by Phil Wilkins
