# Lecture 07: GPU Monitoring and Management with DCGM

## Learning Objectives

By the end of this lecture, you will be able to:

- Design comprehensive GPU monitoring infrastructure using NVIDIA DCGM integrated with Prometheus, Grafana, and alerting systems for production ML platforms
- Implement health check and diagnostic workflows using DCGM to proactively detect GPU hardware issues including ECC errors, thermal problems, and XID errors before they cause failures
- Configure multi-tier alerting strategies (critical, warning, info) for GPU metrics including utilization, temperature, power, memory errors, and throttling events
- Architect capacity planning systems that track GPU utilization patterns, forecast resource needs, and trigger scaling decisions based on historical metrics and trends
- Integrate GPU metrics with application-level metrics (training loss, throughput, latency) to provide end-to-end observability for ML workflows
- Design cost allocation and chargeback systems that track GPU usage by team, project, or workload using DCGM metrics and Prometheus queries
- Implement automated remediation workflows that respond to GPU health issues including node drain, workload migration, and alert escalation based on DCGM policy violations
- Troubleshoot GPU infrastructure issues using DCGM diagnostics, profiling metrics, and correlation with system logs to identify root causes of performance degradation and failures

## Table of Contents
1. [Introduction to GPU Monitoring](#introduction-to-gpu-monitoring)
2. [NVIDIA DCGM Overview](#nvidia-dcgm-overview)
3. [GPU Metrics and Health Checks](#gpu-metrics-and-health-checks)
4. [Integration with Prometheus](#integration-with-prometheus)
5. [Alerting Strategies](#alerting-strategies)
6. [Capacity Planning](#capacity-planning)
7. [Production Monitoring Best Practices](#production-monitoring-best-practices)

## Introduction to GPU Monitoring

Comprehensive GPU monitoring is essential for production AI infrastructure to ensure optimal performance, detect issues early, and plan capacity.

### Why Monitor GPUs?

1. **Performance Optimization**: Identify underutilized resources
2. **Issue Detection**: Catch problems before they cause failures
3. **Capacity Planning**: Understand usage patterns for scaling decisions
4. **Cost Management**: Optimize cloud GPU spending
5. **SLA Compliance**: Ensure service level objectives are met
6. **Troubleshooting**: Quickly diagnose performance degradation

### Monitoring Hierarchy

```
Level 1: Real-time Monitoring
├── nvidia-smi (command-line)
└── GPU utilization, temperature, power

Level 2: System Monitoring
├── DCGM (Data Center GPU Manager)
└── Comprehensive metrics, health checks

Level 3: Observability Platform
├── Prometheus + Grafana
├── Time-series data, dashboards, alerts
└── Integration with application metrics

Level 4: ML Platform Monitoring
├── Training throughput, loss curves
├── Model performance metrics
└── End-to-end job monitoring
```

### Key Metrics to Monitor

**Utilization Metrics:**
- GPU utilization (SM activity)
- Memory utilization
- Tensor Core activity (on supported GPUs)
- PCIe/NVLink bandwidth utilization

**Performance Metrics:**
- Achieved FLOPS
- Memory bandwidth
- Kernel execution time
- Power consumption

**Health Metrics:**
- Temperature (GPU, memory)
- Power draw vs. limit
- ECC errors
- Throttling events
- XID errors

**Capacity Metrics:**
- GPU allocation rate
- Queue depth
- Job wait time
- Resource fragmentation

## NVIDIA DCGM Overview

DCGM (Data Center GPU Manager) is NVIDIA's tool for managing and monitoring GPUs at scale in data centers.

### DCGM Architecture

```
Application/User
      ↓
DCGM Client API / dcgmi CLI
      ↓
DCGM Host Engine (daemon)
      ↓
NVML (NVIDIA Management Library)
      ↓
GPU Driver
      ↓
GPU Hardware
```

**Components:**
- **nv-hostengine**: DCGM daemon running on each node
- **dcgmi**: Command-line interface for DCGM
- **DCGM Exporter**: Prometheus exporter for DCGM metrics
- **Client Libraries**: Python, C APIs

### Installing DCGM

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install -y datacenter-gpu-manager

# Or via NVIDIA Docker
docker run -d --gpus all \
  --name dcgm-exporter \
  -p 9400:9400 \
  nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04

# Start DCGM host engine
sudo nv-hostengine

# Or start in foreground for testing
nv-hostengine -n

# Check status
sudo systemctl status nvidia-dcgm
```

### DCGM Command-Line Interface

```bash
# Discovery: List all GPUs
dcgmi discovery -l

# Output:
# 8 GPUs found.
# +--------+----------------------------------------------------------------------+
# | GPU ID | Device Information                                                   |
# +--------+----------------------------------------------------------------------+
# | 0      | Name: NVIDIA A100-SXM4-40GB                                         |
# |        | UUID: GPU-12345678-1234-1234-1234-123456789abc                       |
# | 1      | Name: NVIDIA A100-SXM4-40GB                                         |
# ...

# Health check
dcgmi health -c -g 0  # Check GPU 0
dcgmi health -c -a    # Check all GPUs

# Output shows:
# - Overall health: Healthy/Warning/Failure
# - Individual tests: Memory, Inforom, Thermal, etc.

# Query GPU info
dcgmi dmon -e 100,155,156,203,204 -c 10
# -e: Field IDs to monitor
# -c: Count (10 samples)

# Field IDs:
# 100: GPU Utilization
# 155: Memory utilization
# 156: Temperature
# 203: Power usage
# 204: PCIe bandwidth

# Run diagnostics
dcgmi diag -r 3  # Run level 3 diagnostic (medium)
# Levels: 1 (quick), 2 (medium), 3 (long), 4 (extended)

# Output includes:
# - Memory tests
# - Compute tests
# - Bandwidth tests
# - Stress tests

# Group management (for managing multiple GPUs)
dcgmi group -c test_group  # Create group
dcgmi group -g 1 -a 0,1,2,3  # Add GPUs 0-3 to group
dcgmi group -l  # List groups
dcgmi group -d 1  # Delete group

# Stats (historical data)
dcgmi stats -g 1 -e  # Enable stats for group 1
dcgmi stats -g 1 -v  # View stats
dcgmi stats -g 1 -x  # Disable stats
```

### DCGM Policies

DCGM can enforce policies and take actions based on violations:

```bash
# Create policy: alert on high temperature
dcgmi policy -g 1 --set 1,85  # Policy 1 (temperature), threshold 85°C

# Policy types:
# 1: Temperature
# 2: Power
# 3: PCIe
# 4: Max retired pages
# 5: Thermal violations
# 6: Power violations
# 7: NVLink errors
# 8: XID errors

# Register for violations
dcgmi policy -g 1 --reg

# List policies
dcgmi policy -g 1 --get
```

### DCGM Profiling

Profile GPU metrics at high frequency:

```bash
# Start profiling
dcgmi profile --pause  # Pause profiling
dcgmi profile --resume  # Resume profiling
dcgmi profile --list  # List available metrics

# Available profiling metrics:
# - SM activity
# - SM occupancy
# - Tensor activity
# - FP64/FP32/FP16 activity
# - Memory bandwidth
# - PCIe/NVLink bandwidth

# Example: Profile SM activity
dcgmi profile --gpu 0 --fields 1001,1002,1003
# 1001: SM Active
# 1002: SM Occupancy
# 1003: Tensor Active
```

## GPU Metrics and Health Checks

### Core Metrics

**1. GPU Utilization** (DCGM_FI_DEV_GPU_UTIL)
```bash
dcgmi dmon -e 100 -c 100

# Interpretation:
# >80%: Good utilization
# 50-80%: Moderate, check for bottlenecks
# <50%: Underutilized, investigate CPU/memory/data loading
```

**2. Memory Utilization** (DCGM_FI_DEV_MEM_COPY_UTIL)
```bash
dcgmi dmon -e 155 -c 100

# Interpretation:
# High memory util + low GPU util = memory-bound
# Low both = CPU bottleneck or inefficient kernels
```

**3. Power Usage** (DCGM_FI_DEV_POWER_USAGE)
```bash
dcgmi dmon -e 203 -c 100

# Compare to power limit
dcgmi dmon -e 203,204

# Low power = GPU not working hard (idle or underutilized)
# At limit = working at capacity
```

**4. Temperature** (DCGM_FI_DEV_GPU_TEMP)
```bash
dcgmi dmon -e 156 -c 100

# Temperature ranges:
# <60°C: Idle or light load
# 60-75°C: Normal under load
# 75-85°C: Heavy load, acceptable
# >85°C: Thermal throttling risk, check cooling
```

**5. PCIe/NVLink Throughput**
```bash
# PCIe throughput
dcgmi dmon -e 220,221

# NVLink throughput (if available)
dcgmi dmon -e 240,241,242,243,244,245

# Check for PCIe bandwidth bottlenecks
# Compare to theoretical maximum (16 GB/s for PCIe Gen3 x16)
```

### Health Checks

**ECC Errors** (critical):
```bash
# Single-bit errors (correctable)
dcgmi dmon -e 312

# Double-bit errors (uncorrectable, critical)
dcgmi dmon -e 313

# If DBE > 0, GPU may need replacement
# If SBE increasing, monitor closely
```

**XID Errors** (GPU hardware errors):
```bash
# Check for XID errors in system logs
dmesg | grep -i xid

# Common XIDs:
# XID 48: Double-bit ECC error
# XID 63: Memory page retirement
# XID 79: GPU has fallen off the bus

# DCGM can monitor XIDs
dcgmi health -c -a  # Includes XID check
```

**Throttling Events**:
```bash
# Check if GPU is throttled
dcgmi dmon -e 420,421,422

# Throttling reasons:
# 420: Power throttling
# 421: Thermal throttling
# 422: HW slowdown

# If throttling, investigate:
# - Cooling system
# - Power limits
# - Workload intensity
```

**Retired Pages** (memory failures):
```bash
# Check retired pages
dcgmi dmon -e 314,315

# If retired pages are increasing, GPU memory is degrading
# May need GPU replacement
```

### DCGM Health Checks

```bash
# Comprehensive health check
dcgmi health -c -a

# Output example:
# Overall Health: Healthy
#
# Specific Tests:
# Memory           : Pass
# Inforom          : Pass
# Thermal          : Pass
# Power            : Pass
# PCIe             : Pass
# NVLink           : Pass

# Run diagnostics (deeper tests)
dcgmi diag -r 2

# Diagnostic output:
# +---------------------------+--------+
# | Test                      | Result |
# +---------------------------+--------+
# | Memory                    | Pass   |
# | Diagnostic                | Pass   |
# | Targeted Stress           | Pass   |
# | Targeted Power            | Pass   |
# +---------------------------+--------+

# Schedule periodic health checks
# Add to cron:
# 0 2 * * * dcgmi health -c -a > /var/log/dcgm-health.log
```

## Integration with Prometheus

DCGM Exporter exposes GPU metrics in Prometheus format.

### Installing DCGM Exporter

```bash
# Docker (standalone)
docker run -d --gpus all \
  --name dcgm-exporter \
  -p 9400:9400 \
  nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04

# Kubernetes (DaemonSet)
kubectl create -f https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/dcgm-exporter.yaml

# Helm
helm repo add gpu-helm-charts https://nvidia.github.io/dcgm-exporter/helm-charts
helm install dcgm-exporter gpu-helm-charts/dcgm-exporter

# Verify exporter is running
curl http://localhost:9400/metrics
```

### DCGM Exporter Metrics

Key metrics exposed by DCGM Exporter:

```prometheus
# GPU utilization (%)
DCGM_FI_DEV_GPU_UTIL{gpu="0",UUID="GPU-xxx",device="nvidia0"}

# Memory utilization (%)
DCGM_FI_DEV_MEM_COPY_UTIL{gpu="0"}

# Power usage (W)
DCGM_FI_DEV_POWER_USAGE{gpu="0"}

# Temperature (°C)
DCGM_FI_DEV_GPU_TEMP{gpu="0"}

# SM clock (MHz)
DCGM_FI_DEV_SM_CLOCK{gpu="0"}

# Memory clock (MHz)
DCGM_FI_DEV_MEM_CLOCK{gpu="0"}

# FB (framebuffer) memory used (MB)
DCGM_FI_DEV_FB_USED{gpu="0"}

# FB memory free (MB)
DCGM_FI_DEV_FB_FREE{gpu="0"}

# ECC errors
DCGM_FI_DEV_ECC_SBE_VOL_TOTAL{gpu="0"}  # Single-bit errors
DCGM_FI_DEV_ECC_DBE_VOL_TOTAL{gpu="0"}  # Double-bit errors

# PCIe throughput (KB/s)
DCGM_FI_DEV_PCIE_TX_THROUGHPUT{gpu="0"}  # Transmit
DCGM_FI_DEV_PCIE_RX_THROUGHPUT{gpu="0"}  # Receive

# Profiling metrics (if enabled)
DCGM_FI_PROF_GR_ENGINE_ACTIVE{gpu="0"}  # Graphics engine active (%)
DCGM_FI_PROF_SM_ACTIVE{gpu="0"}  # SM active (%)
DCGM_FI_PROF_SM_OCCUPANCY{gpu="0"}  # SM occupancy (%)
DCGM_FI_PROF_PIPE_TENSOR_ACTIVE{gpu="0"}  # Tensor Core active (%)
DCGM_FI_PROF_DRAM_ACTIVE{gpu="0"}  # Memory active (%)
DCGM_FI_PROF_PCIE_TX_BYTES{gpu="0"}  # PCIe transmit bytes
DCGM_FI_PROF_PCIE_RX_BYTES{gpu="0"}  # PCIe receive bytes
DCGM_FI_PROF_NVLINK_TX_BYTES{gpu="0"}  # NVLink transmit bytes
DCGM_FI_PROF_NVLINK_RX_BYTES{gpu="0"}  # NVLink receive bytes
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'dcgm-exporter'
    static_configs:
      - targets: ['localhost:9400']
        labels:
          cluster: 'ml-cluster'
          datacenter: 'dc1'

  # Kubernetes service discovery
  - job_name: 'kubernetes-dcgm'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: dcgm-exporter
      - source_labels: [__meta_kubernetes_pod_node_name]
        target_label: node
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "GPU Monitoring Dashboard",
    "panels": [
      {
        "title": "GPU Utilization",
        "targets": [
          {
            "expr": "DCGM_FI_DEV_GPU_UTIL",
            "legendFormat": "GPU {{gpu}} - {{node}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Memory Usage",
        "targets": [
          {
            "expr": "DCGM_FI_DEV_FB_USED / (DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE) * 100",
            "legendFormat": "GPU {{gpu}} Memory %"
          }
        ],
        "type": "graph"
      },
      {
        "title": "GPU Temperature",
        "targets": [
          {
            "expr": "DCGM_FI_DEV_GPU_TEMP",
            "legendFormat": "GPU {{gpu}} Temp"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {
              "query": "DCGM_FI_DEV_GPU_TEMP > 85",
              "duration": "5m"
            }
          ]
        }
      },
      {
        "title": "GPU Power Usage",
        "targets": [
          {
            "expr": "DCGM_FI_DEV_POWER_USAGE",
            "legendFormat": "GPU {{gpu}} Power (W)"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

Pre-built Grafana dashboards:
- NVIDIA DCGM Exporter Dashboard: https://grafana.com/grafana/dashboards/12239

```bash
# Import dashboard
# Grafana UI → Dashboards → Import → ID: 12239
```

## Alerting Strategies

### Critical Alerts (PagerDuty/Opsgenie)

**1. GPU Hardware Failure**
```yaml
# prometheus_rules.yml
groups:
  - name: gpu_critical_alerts
    interval: 30s
    rules:
      - alert: GPUHardwareFailure
        expr: DCGM_FI_DEV_XID_ERRORS > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "GPU hardware error detected"
          description: "GPU {{ $labels.gpu }} on {{ $labels.node }} has XID errors"

      - alert: GPUDoubleBitECC
        expr: increase(DCGM_FI_DEV_ECC_DBE_VOL_TOTAL[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "GPU has uncorrectable memory errors"
          description: "GPU {{ $labels.gpu }} has {{ $value }} double-bit ECC errors"

      - alert: GPUOffline
        expr: up{job="dcgm-exporter"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "GPU node is offline"
          description: "Node {{ $labels.node }} DCGM exporter is down"
```

**2. Thermal Issues**
```yaml
      - alert: GPUOverheating
        expr: DCGM_FI_DEV_GPU_TEMP > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GPU temperature high"
          description: "GPU {{ $labels.gpu }} temperature is {{ $value }}°C"

      - alert: GPUThermalThrottle
        expr: DCGM_FI_DEV_CLOCK_THROTTLE_REASONS > 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "GPU is throttling"
          description: "GPU {{ $labels.gpu }} is thermally throttling"
```

### Performance Alerts (Slack/Email)

**3. Underutilization**
```yaml
      - alert: GPUUnderutilized
        expr: avg_over_time(DCGM_FI_DEV_GPU_UTIL[15m]) < 30
        for: 30m
        labels:
          severity: info
        annotations:
          summary: "GPU is underutilized"
          description: "GPU {{ $labels.gpu }} utilization is {{ $value }}%"

      - alert: GPUMemoryLeak
        expr: deriv(DCGM_FI_DEV_FB_USED[1h]) > 100
        for: 2h
        labels:
          severity: warning
        annotations:
          summary: "Possible GPU memory leak"
          description: "GPU {{ $labels.gpu }} memory usage growing continuously"
```

**4. Capacity Alerts**
```yaml
      - alert: GPUMemoryPressure
        expr: (DCGM_FI_DEV_FB_USED / (DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE)) * 100 > 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "GPU memory usage high"
          description: "GPU {{ $labels.gpu }} memory at {{ $value }}%"

      - alert: HighRetiredPages
        expr: DCGM_FI_DEV_RETIRED_PAGES > 100
        labels:
          severity: warning
        annotations:
          summary: "GPU has high retired page count"
          description: "GPU {{ $labels.gpu }} has {{ $value }} retired pages"
```

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'
    - match:
        severity: info
      receiver: 'email'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:5001/'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .CommonAnnotations.summary }}'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#gpu-alerts'
        title: '{{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'email'
    email_configs:
      - to: 'ml-team@company.com'
        from: 'alertmanager@company.com'
        smarthost: 'smtp.company.com:587'
```

## Capacity Planning

### Tracking GPU Utilization Over Time

```promql
# Average GPU utilization per node over 24 hours
avg_over_time(DCGM_FI_DEV_GPU_UTIL[24h])

# Peak GPU utilization
max_over_time(DCGM_FI_DEV_GPU_UTIL[24h])

# GPU idle time (utilization < 10%)
sum(time() - timestamp(DCGM_FI_DEV_GPU_UTIL < 10)) by (node)

# GPU hours used (for cost allocation)
sum(DCGM_FI_DEV_GPU_UTIL / 100 * scalar(time() - time() offset 1h)) by (node)
```

### Forecasting Capacity Needs

```python
# capacity_planning.py
import pandas as pd
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url="http://prometheus:9090", disable_ssl=True)

# Query GPU utilization for last 30 days
query = 'avg(DCGM_FI_DEV_GPU_UTIL)'
result = prom.custom_query_range(
    query,
    start_time=pd.Timestamp.now() - pd.Timedelta(days=30),
    end_time=pd.Timestamp.now(),
    step='1h'
)

# Convert to DataFrame
df = pd.DataFrame(result[0]['values'], columns=['timestamp', 'utilization'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df['utilization'] = df['utilization'].astype(float)

# Calculate trends
df['day'] = df['timestamp'].dt.dayofweek
avg_by_day = df.groupby('day')['utilization'].mean()

# Forecast
from sklearn.linear_model import LinearRegression
X = df.index.values.reshape(-1, 1)
y = df['utilization'].values
model = LinearRegression().fit(X, y)

# Predict 30 days ahead
future_X = np.arange(len(df), len(df) + 30*24).reshape(-1, 1)
future_utilization = model.predict(future_X)

print(f"Current avg utilization: {df['utilization'].mean():.2f}%")
print(f"Predicted utilization in 30 days: {future_utilization[-1]:.2f}%")

if future_utilization[-1] > 80:
    print("WARNING: Need to add GPU capacity!")
    additional_gpus = int((future_utilization[-1] - 80) / 80 * current_gpu_count)
    print(f"Recommendation: Add {additional_gpus} GPUs")
```

### Cost Analysis

```python
# gpu_cost_analysis.py
# Calculate GPU cost per workload/team

def calculate_gpu_costs(gpu_hours_by_team, cost_per_gpu_hour):
    """
    Calculate GPU costs per team

    Args:
        gpu_hours_by_team: Dict of team -> GPU hours used
        cost_per_gpu_hour: Cost per GPU hour (e.g., $3 for A100)
    """
    total_cost = 0
    for team, hours in gpu_hours_by_team.items():
        cost = hours * cost_per_gpu_hour
        total_cost += cost
        print(f"{team}: {hours:.2f} GPU-hours, ${cost:.2f}")

    print(f"\nTotal GPU cost: ${total_cost:.2f}")
    return total_cost

# Query Prometheus for GPU hours by team
# Assumes workloads are labeled with team name
query = '''
sum by (team) (
  DCGM_FI_DEV_GPU_UTIL / 100 *
  (time() - time() offset 30d) / 3600
)
'''

# TODO: Implement cost tracking and chargeback system
```

## Production Monitoring Best Practices

### 1. Monitoring Stack Setup

```yaml
# docker-compose.yml for monitoring stack
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=90d'

  grafana:
    image: grafana/grafana
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  dcgm-exporter:
    image: nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    ports:
      - "9400:9400"

  alertmanager:
    image: prom/alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"

volumes:
  prometheus-data:
  grafana-data:
```

### 2. Custom Metrics

Combine DCGM metrics with application metrics:

```python
# ml_training_metrics.py
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Define metrics
training_iterations = Counter('training_iterations_total', 'Total training iterations')
training_loss = Gauge('training_loss', 'Current training loss')
batch_time = Histogram('batch_processing_seconds', 'Batch processing time')
gpu_memory_allocated = Gauge('gpu_memory_allocated_mb', 'GPU memory allocated')

# Start Prometheus metrics server
start_http_server(8000)

# Training loop with metrics
for epoch in range(num_epochs):
    for batch in dataloader:
        start_time = time.time()

        # Training step
        loss = train_step(model, batch)

        # Record metrics
        training_iterations.inc()
        training_loss.set(loss.item())
        batch_time.observe(time.time() - start_time)
        gpu_memory_allocated.set(torch.cuda.memory_allocated() / 1e6)

# Prometheus can now scrape these metrics alongside DCGM metrics
```

### 3. Logging Integration

Correlate GPU metrics with application logs:

```python
import logging
import json

# Structured logging with GPU context
logger = logging.getLogger(__name__)

def log_with_gpu_context(message, level='info'):
    import pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    gpu_context = {
        'gpu_utilization': pynvml.nvmlDeviceGetUtilizationRates(handle).gpu,
        'gpu_memory_used': pynvml.nvmlDeviceGetMemoryInfo(handle).used / 1e9,
        'gpu_temperature': pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    }

    log_entry = {
        'message': message,
        'gpu': gpu_context,
        'timestamp': time.time()
    }

    getattr(logger, level)(json.dumps(log_entry))

# Usage
log_with_gpu_context("Starting training epoch 5")
```

### 4. Automated Health Checks

```bash
#!/bin/bash
# gpu_health_check.sh

# Run health checks and send alerts if issues found

check_gpu_health() {
    # Run DCGM health check
    result=$(dcgmi health -c -a)

    if echo "$result" | grep -q "Failure"; then
        echo "GPU health check failed!"
        echo "$result"
        # Send alert
        curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
             -H 'Content-Type: application/json' \
             -d '{"text":"GPU health check failed on '$HOSTNAME'"}'
        return 1
    fi

    # Check for ECC errors
    dbe=$(dcgmi dmon -e 313 -c 1 | tail -1 | awk '{print $2}')
    if [ "$dbe" -gt 0 ]; then
        echo "Double-bit ECC errors detected: $dbe"
        # Send critical alert
        return 1
    fi

    echo "GPU health check passed"
    return 0
}

# Run check
check_gpu_health

# Add to cron for periodic checks
# */15 * * * * /usr/local/bin/gpu_health_check.sh >> /var/log/gpu_health.log 2>&1
```

## Summary

Key GPU monitoring takeaways:

1. **Use DCGM for comprehensive monitoring**: Goes beyond nvidia-smi
2. **Integrate with Prometheus/Grafana**: Time-series data and dashboards
3. **Set up alerting**: Critical (hardware), warning (thermal), info (utilization)
4. **Track capacity metrics**: Plan for growth before running out of resources
5. **Combine GPU + application metrics**: Full observability stack
6. **Automate health checks**: Catch issues before they cause failures

## Hands-on Exercise

Set up GPU monitoring stack:

```bash
# 1. Install DCGM
sudo apt-get install -y datacenter-gpu-manager
sudo systemctl start nvidia-dcgm

# 2. Run DCGM exporter
docker run -d --gpus all -p 9400:9400 \
  nvcr.io/nvidia/k8s/dcgm-exporter:3.1.8-3.1.5-ubuntu20.04

# 3. Check metrics
curl http://localhost:9400/metrics | grep DCGM_FI_DEV_GPU_UTIL

# 4. Set up Prometheus and Grafana (using docker-compose above)
docker-compose up -d

# 5. Access Grafana at http://localhost:3000
# 6. Import DCGM dashboard (ID: 12239)
# 7. Configure alerts in Prometheus

# TODO: Create custom dashboard for your workloads
# TODO: Set up alerting for critical GPU issues
```

## Further Reading

- DCGM User Guide: https://docs.nvidia.com/datacenter/dcgm/
- DCGM Exporter: https://github.com/NVIDIA/dcgm-exporter
- Prometheus GPU Monitoring: https://prometheus.io/docs/

---

**Next Lecture**: GPU Cluster Design and Architecture
