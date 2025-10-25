# Module 207: Tools and Frameworks Reference

## Monitoring

### Prometheus Ecosystem

#### Prometheus Server
- **Description**: Open-source monitoring and alerting toolkit
- **Language**: Go
- **Use Case**: Metrics collection, storage, and querying
- **Installation**:
  ```bash
  # Helm
  helm install prometheus prometheus-community/prometheus
  
  # Operator
  helm install prometheus-operator prometheus-community/kube-prometheus-stack
  ```
- **Key Features**: Pull-based model, PromQL, service discovery
- **Best For**: Kubernetes environments, cloud-native apps
- **License**: Apache 2.0
- **Links**:
  - Website: https://prometheus.io/
  - GitHub: https://github.com/prometheus/prometheus
  - Docs: https://prometheus.io/docs/

#### Thanos
- **Description**: Highly available Prometheus setup with long-term storage
- **Language**: Go
- **Use Case**: Multi-cluster monitoring, unlimited retention
- **Components**: Sidecar, Query, Store, Compactor, Receiver, Ruler
- **Storage Backends**: S3, GCS, Azure Blob, Swift
- **Installation**:
  ```bash
  helm install thanos bitnami/thanos
  ```
- **Best For**: Large-scale Prometheus deployments
- **License**: Apache 2.0
- **Links**:
  - Website: https://thanos.io/
  - GitHub: https://github.com/thanos-io/thanos

#### Cortex
- **Description**: Horizontally scalable, multi-tenant Prometheus
- **Language**: Go
- **Use Case**: Prometheus-as-a-Service, multi-tenancy
- **Key Features**: Horizontal scaling, multi-tenancy, long-term storage
- **Best For**: SaaS providers, multi-tenant platforms
- **License**: Apache 2.0
- **Links**:
  - Website: https://cortexmetrics.io/
  - GitHub: https://github.com/cortexproject/cortex

#### VictoriaMetrics
- **Description**: Fast, cost-effective monitoring solution
- **Language**: Go
- **Use Case**: Prometheus replacement with better performance
- **Key Features**: 10x compression, fast queries, PromQL support
- **Installation**:
  ```bash
  helm install victoria-metrics vm/victoria-metrics-single
  ```
- **Best For**: Cost-conscious deployments, large-scale metrics
- **License**: Apache 2.0
- **Links**:
  - Website**: https://victoriametrics.com/
  - GitHub: https://github.com/VictoriaMetrics/VictoriaMetrics

### Visualization

#### Grafana
- **Description**: Open-source visualization and analytics platform
- **Language**: TypeScript/Go
- **Use Case**: Dashboards, alerting, data exploration
- **Data Sources**: Prometheus, Elasticsearch, Loki, 50+ more
- **Installation**:
  ```bash
  helm install grafana grafana/grafana
  ```
- **Key Features**: Beautiful dashboards, alerting, plugins
- **License**: AGPL 3.0
- **Links**:
  - Website: https://grafana.com/
  - GitHub: https://github.com/grafana/grafana

## Distributed Tracing

### OpenTelemetry
- **Description**: Vendor-neutral observability framework
- **Language**: Multi-language (Python, Go, Java, JavaScript, etc.)
- **Use Case**: Unified metrics, traces, logs collection
- **Components**: SDKs, Collector, Exporters
- **Installation**:
  ```bash
  # Python
  pip install opentelemetry-api opentelemetry-sdk
  
  # Collector (Helm)
  helm install opentelemetry-collector open-telemetry/opentelemetry-collector
  ```
- **Best For**: Modern cloud-native applications
- **License**: Apache 2.0
- **Links**:
  - Website: https://opentelemetry.io/
  - GitHub: https://github.com/open-telemetry

### Jaeger
- **Description**: Distributed tracing platform
- **Language**: Go
- **Use Case**: Trace collection, storage, visualization
- **Storage Backends**: Cassandra, Elasticsearch, Kafka
- **Installation**:
  ```bash
  # All-in-one (development)
  kubectl create -f https://jaegertracing.io/docs/latest/operator/
  
  # Production (Operator)
  kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.49.0/jaeger-operator.yaml
  ```
- **Key Features**: Context propagation, sampling, service graphs
- **License**: Apache 2.0
- **Links**:
  - Website: https://www.jaegertracing.io/
  - GitHub: https://github.com/jaegertracing/jaeger

### Zipkin
- **Description**: Distributed tracing system
- **Language**: Java
- **Use Case**: Latency problem troubleshooting
- **Storage**: Cassandra, Elasticsearch, MySQL
- **Installation**:
  ```bash
  docker run -d -p 9411:9411 openzipkin/zipkin
  ```
- **Best For**: Organizations already using Zipkin
- **License**: Apache 2.0
- **Links**:
  - Website: https://zipkin.io/
  - GitHub: https://github.com/openzipkin/zipkin

### Tempo
- **Description**: High-volume distributed tracing backend
- **Language**: Go
- **Use Case**: Cost-effective trace storage
- **Storage**: Object storage (S3, GCS)
- **Key Features**: No indexing (cost-effective), TraceQL queries
- **Best For**: High trace volumes, cost optimization
- **License**: AGPL 3.0
- **Links**:
  - Website: https://grafana.com/oss/tempo/
  - GitHub: https://github.com/grafana/tempo

## Logging

### ELK Stack

#### Elasticsearch
- **Description**: Distributed search and analytics engine
- **Language**: Java
- **Use Case**: Log storage and search
- **Installation**:
  ```bash
  helm install elasticsearch elastic/elasticsearch
  ```
- **Key Features**: Full-text search, real-time indexing, RESTful API
- **License**: Elastic License / SSPL
- **Links**:
  - Website: https://www.elastic.co/elasticsearch/
  - GitHub: https://github.com/elastic/elasticsearch

#### Logstash
- **Description**: Server-side data processing pipeline
- **Language**: JRuby
- **Use Case**: Log ingestion, parsing, enrichment
- **Installation**:
  ```bash
  helm install logstash elastic/logstash
  ```
- **Key Features**: 200+ plugins, filters, outputs
- **License**: Elastic License
- **Links**:
  - Website: https://www.elastic.co/logstash/
  - GitHub: https://github.com/elastic/logstash

#### Kibana
- **Description**: Data visualization platform for Elasticsearch
- **Language**: TypeScript
- **Use Case**: Log visualization, dashboards
- **Installation**:
  ```bash
  helm install kibana elastic/kibana
  ```
- **License**: Elastic License
- **Links**:
  - Website: https://www.elastic.co/kibana/
  - GitHub: https://github.com/elastic/kibana

### Log Collectors

#### Fluentd
- **Description**: Unified logging layer
- **Language**: Ruby/C
- **Use Case**: Log collection and routing
- **Installation**:
  ```bash
  helm install fluentd fluent/fluentd
  ```
- **Key Features**: 500+ plugins, buffering, routing
- **License**: Apache 2.0
- **Links**:
  - Website: https://www.fluentd.org/
  - GitHub: https://github.com/fluent/fluentd

#### Fluent Bit
- **Description**: Lightweight log processor and forwarder
- **Language**: C
- **Use Case**: Edge log collection, low resource environments
- **Key Features**: Low memory footprint, high performance
- **License**: Apache 2.0
- **Links**:
  - Website: https://fluentbit.io/
  - GitHub: https://github.com/fluent/fluent-bit

#### Filebeat
- **Description**: Lightweight log shipper
- **Language**: Go
- **Use Case**: Log forwarding to Elasticsearch/Logstash
- **Installation**:
  ```bash
  helm install filebeat elastic/filebeat
  ```
- **License**: Elastic License
- **Links**:
  - Website: https://www.elastic.co/beats/filebeat
  - GitHub: https://github.com/elastic/beats

### Loki Stack

#### Loki
- **Description**: Log aggregation system (like Prometheus for logs)
- **Language**: Go
- **Use Case**: Cost-effective log storage
- **Installation**:
  ```bash
  helm install loki grafana/loki-stack
  ```
- **Key Features**: Label-based indexing, low cost, LogQL
- **License**: AGPL 3.0
- **Links**:
  - Website: https://grafana.com/oss/loki/
  - GitHub: https://github.com/grafana/loki

#### Promtail
- **Description**: Log collector for Loki
- **Language**: Go
- **Use Case**: Ship logs to Loki
- **Key Features**: Label extraction, pipeline stages
- **License**: AGPL 3.0
- **Links**: Same as Loki

## ML Observability

### Evidently
- **Description**: ML monitoring and testing
- **Language**: Python
- **Use Case**: Data drift, model drift detection
- **Installation**:
  ```bash
  pip install evidently
  ```
- **Key Features**: Drift reports, dashboards, tests
- **License**: Apache 2.0
- **Links**:
  - Website: https://www.evidentlyai.com/
  - GitHub: https://github.com/evidentlyai/evidently

### WhyLabs
- **Description**: AI observability platform
- **Language**: Python
- **Use Case**: ML monitoring, data quality
- **Installation**:
  ```bash
  pip install whylogs
  ```
- **Key Features**: Profile logging, anomaly detection
- **License**: Apache 2.0 (whylogs), Commercial (platform)
- **Links**:
  - Website: https://whylabs.ai/
  - GitHub: https://github.com/whylabs/whylogs

### Alibi Detect
- **Description**: Outlier, adversarial, and drift detection
- **Language**: Python
- **Use Case**: Advanced drift detection algorithms
- **Installation**:
  ```bash
  pip install alibi-detect
  ```
- **License**: Apache 2.0
- **Links**:
  - GitHub: https://github.com/SeldonIO/alibi-detect

### SHAP
- **Description**: Model explainability
- **Language**: Python
- **Use Case**: Feature importance, model interpretation
- **Installation**:
  ```bash
  pip install shap
  ```
- **License**: MIT
- **Links**:
  - Website: https://shap.readthedocs.io/
  - GitHub: https://github.com/slundberg/shap

## Chaos Engineering

### Chaos Mesh
- **Description**: Chaos engineering platform for Kubernetes
- **Language**: Go
- **Use Case**: Fault injection in Kubernetes
- **Installation**:
  ```bash
  helm install chaos-mesh chaos-mesh/chaos-mesh --namespace=chaos-mesh
  ```
- **Chaos Types**: Pod failures, network, I/O, time, stress
- **License**: Apache 2.0
- **Links**:
  - Website: https://chaos-mesh.org/
  - GitHub: https://github.com/chaos-mesh/chaos-mesh

### Litmus
- **Description**: Chaos engineering for Kubernetes
- **Language**: Go
- **Use Case**: Chaos workflows, SRE validation
- **Installation**:
  ```bash
  helm install litmus litmuschaos/litmus
  ```
- **Key Features**: ChaosHub (experiments catalog), workflows
- **License**: Apache 2.0
- **Links**:
  - Website: https://litmuschaos.io/
  - GitHub: https://github.com/litmuschaos/litmus

### Gremlin
- **Description**: Chaos engineering SaaS platform
- **Language**: Proprietary
- **Use Case**: Enterprise chaos engineering
- **Key Features**: Managed service, compliance, GameDays
- **License**: Commercial
- **Links**:
  - Website: https://www.gremlin.com/

## Enterprise Observability Platforms

### DataDog
- **Description**: Full-stack observability platform
- **Use Case**: APM, infrastructure monitoring, logs, traces
- **Key Features**: 600+ integrations, ML-powered insights
- **Pricing**: Usage-based, free tier available
- **Best For**: Organizations wanting managed solution
- **Links**:
  - Website: https://www.datadoghq.com/

### New Relic
- **Description**: Observability platform
- **Use Case**: APM, distributed tracing, logs
- **Key Features**: AIOps, full-stack visibility
- **Pricing**: Usage-based, free tier (100GB/month)
- **Links**:
  - Website: https://newrelic.com/

### Dynatrace
- **Description**: Software intelligence platform
- **Use Case**: APM, AIOps, cloud automation
- **Key Features**: AI-powered root cause analysis
- **Pricing**: Enterprise
- **Links**:
  - Website: https://www.dynatrace.com/

### Splunk
- **Description**: Data platform for security and observability
- **Use Case**: Log analysis, SIEM, observability
- **Key Features**: Machine learning, security analytics
- **Pricing**: Enterprise, free tier available
- **Links**:
  - Website: https://www.splunk.com/

## Comparison Matrices

### Monitoring Solutions

| Tool | Type | Cost | Best For | Scalability |
|------|------|------|----------|-------------|
| Prometheus | OSS | Free | Kubernetes, cloud-native | Medium |
| Thanos | OSS | Storage cost | Multi-cluster Prometheus | High |
| Cortex | OSS | Storage cost | Multi-tenant Prometheus | High |
| VictoriaMetrics | OSS | Free | Cost optimization | Very High |
| DataDog | SaaS | $$$ | Managed, enterprise | High |

### Tracing Solutions

| Tool | Type | Cost | Storage | Best For |
|------|------|------|---------|----------|
| Jaeger | OSS | Free+ | Multiple backends | General purpose |
| Zipkin | OSS | Free+ | Multiple backends | Existing Zipkin users |
| Tempo | OSS | Storage | Object storage | High volume, low cost |
| DataDog APM | SaaS | $$$ | Managed | Enterprise |

### Logging Solutions

| Tool | Type | Cost | Index Type | Best For |
|------|------|------|------------|----------|
| ELK Stack | OSS | Infrastructure | Full-text | Complex searches |
| Loki | OSS | Storage | Labels | Cost optimization |
| Splunk | Commercial | $$$ | Full-text | Enterprise, security |
| DataDog Logs | SaaS | $$$ | Full-text | Managed solution |

## Quick Start Commands

```bash
# Install Prometheus Stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack

# Install Jaeger
kubectl create namespace observability
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/examples/simplest.yaml

# Install Loki Stack
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack

# Install Chaos Mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace

# Install OpenTelemetry Collector
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm install opentelemetry-collector open-telemetry/opentelemetry-collector
```

---

**Last Updated**: 2025-10-16
**Module**: 207 - Advanced Observability and SRE Practices
