# Lecture 08: Capacity Planning for ML Workloads

## Learning Objectives

By the end of this lecture, you will be able to:

- Design capacity planning strategies for ML workloads forecasting training (bursty, GPU-intensive), inference (steady-state, latency-sensitive), and data processing needs
- Implement resource forecasting techniques using historical utilization data, growth projections, and workload modeling predicting future capacity requirements 6-12 months ahead
- Architect cost optimization strategies leveraging spot instances for training (70% savings), reserved capacity for inference, and autoscaling for variable workloads
- Configure resource allocation policies with GPU quotas, priority scheduling, preemption rules, and fair-share mechanisms ensuring efficient multi-tenant resource utilization
- Design scaling strategies including horizontal scaling (adding nodes), vertical scaling (larger instances), and workload optimization (batching, caching) for growing ML platforms
- Implement capacity monitoring tracking GPU utilization, memory usage, storage consumption, and network bandwidth identifying bottlenecks and optimization opportunities
- Build cost allocation systems with chargeback/showback models attributing infrastructure costs to teams, projects, and workloads enabling informed spending decisions
- Architect capacity planning workflows with quarterly reviews, budgeting processes, procurement timelines, and continuous optimization aligning infrastructure with business growth

## Overview

## Overview

Capacity planning ensures your ML infrastructure can handle current and future workloads efficiently and cost-effectively. ML workloads have unique characteristics that require specialized planning approaches.

## ML Resource Characteristics

### Training Workloads

**Characteristics**:
- Bursty and batch-oriented
- High compute/GPU requirements
- Variable duration (hours to days)
- Predictable scheduling
- Can tolerate interruptions (spot instances)

**Resource Needs**:
- GPUs: A100, V100, T4
- Memory: 32GB - 512GB+
- Storage: Fast SSD for data loading
- Network: High bandwidth for distributed training

### Inference Workloads

**Characteristics**:
- Continuous and latency-sensitive
- Predictable patterns (daily/weekly cycles)
- Lower resource per request
- Requires high availability
- Real-time constraints

**Resource Needs**:
- CPU/GPU: Based on model complexity
- Memory: Model size + working memory
- Network: Low latency, high availability
- Caching: Redis for features/predictions

---

## Capacity Planning Process

```
1. Measure Current Usage
   ↓
2. Forecast Future Demand
   ↓
3. Plan Resource Allocation
   ↓
4. Optimize Costs
   ↓
5. Monitor & Adjust
   ↓
(Continuous Loop)
```

---

## Measuring Current Usage

### Infrastructure Metrics

```python
# capacity/metrics_collector.py
from prometheus_api_client import PrometheusConnect
import pandas as pd
from datetime import datetime, timedelta

class CapacityMetricsCollector:
    def __init__(self, prometheus_url):
        self.prom = PrometheusConnect(url=prometheus_url)

    def get_resource_usage(self, days=30):
        """Collect resource usage over time"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        metrics = {
            'cpu_usage': self._query_cpu_usage(start_time, end_time),
            'memory_usage': self._query_memory_usage(start_time, end_time),
            'gpu_usage': self._query_gpu_usage(start_time, end_time),
            'request_rate': self._query_request_rate(start_time, end_time),
            'storage_usage': self._query_storage_usage(start_time, end_time)
        }

        return metrics

    def _query_cpu_usage(self, start, end):
        """Query CPU usage over time"""
        query = '''
        avg(rate(container_cpu_usage_seconds_total{
          namespace="ml-services"
        }[5m])) by (pod)
        '''
        result = self.prom.custom_query_range(
            query=query,
            start_time=start,
            end_time=end,
            step='1h'
        )
        return self._to_dataframe(result)

    def _query_memory_usage(self, start, end):
        """Query memory usage"""
        query = '''
        avg(container_memory_working_set_bytes{
          namespace="ml-services"
        }) by (pod)
        '''
        result = self.prom.custom_query_range(
            query=query,
            start_time=start,
            end_time=end,
            step='1h'
        )
        return self._to_dataframe(result)

    def _query_gpu_usage(self, start, end):
        """Query GPU utilization"""
        query = '''
        avg(DCGM_FI_DEV_GPU_UTIL{
          namespace="ml-services"
        }) by (gpu)
        '''
        result = self.prom.custom_query_range(
            query=query,
            start_time=start,
            end_time=end,
            step='1h'
        )
        return self._to_dataframe(result)

    def _to_dataframe(self, result):
        """Convert Prometheus result to DataFrame"""
        data = []
        for series in result:
            for timestamp, value in series['values']:
                data.append({
                    'timestamp': datetime.fromtimestamp(timestamp),
                    'value': float(value),
                    'labels': series['metric']
                })
        return pd.DataFrame(data)

# Usage
collector = CapacityMetricsCollector("http://prometheus:9090")
metrics = collector.get_resource_usage(days=30)

# Analyze patterns
cpu_df = metrics['cpu_usage']
print(f"Average CPU usage: {cpu_df['value'].mean():.2f}")
print(f"Peak CPU usage: {cpu_df['value'].max():.2f}")
print(f"P95 CPU usage: {cpu_df['value'].quantile(0.95):.2f}")
```

---

## Demand Forecasting

### Time Series Forecasting

```python
# capacity/forecast.py
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt

class DemandForecaster:
    def __init__(self):
        self.model = None

    def forecast_request_rate(self, historical_data: pd.DataFrame, days_ahead=30):
        """Forecast future request rate"""
        # Prepare data for Prophet
        df = historical_data[['timestamp', 'request_rate']].copy()
        df.columns = ['ds', 'y']

        # Create and fit model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True
        )
        model.fit(df)

        # Generate future dates
        future = model.make_future_dataframe(periods=days_ahead)

        # Predict
        forecast = model.predict(future)

        return forecast

    def forecast_resource_needs(self, request_forecast, resources_per_request):
        """Forecast resource requirements based on request forecast"""
        forecast = request_forecast.copy()

        # Calculate resource needs
        forecast['cpu_cores'] = forecast['yhat'] * resources_per_request['cpu']
        forecast['memory_gb'] = forecast['yhat'] * resources_per_request['memory']
        forecast['gpu_count'] = np.ceil(forecast['yhat'] * resources_per_request['gpu'])

        # Add buffer for spikes
        buffer_multiplier = 1.3  # 30% buffer
        forecast['cpu_cores_with_buffer'] = forecast['cpu_cores'] * buffer_multiplier
        forecast['memory_gb_with_buffer'] = forecast['memory_gb'] * buffer_multiplier
        forecast['gpu_count_with_buffer'] = np.ceil(forecast['gpu_count'] * buffer_multiplier)

        return forecast

# Usage
forecaster = DemandForecaster()

# Get historical data
historical_data = load_historical_metrics()  # Your data loading function

# Forecast request rate
request_forecast = forecaster.forecast_request_rate(historical_data, days_ahead=90)

# Forecast resource needs
resources_per_request = {
    'cpu': 0.1,      # CPU cores per request
    'memory': 0.5,   # GB per request
    'gpu': 0.001     # GPU fraction per request
}

resource_forecast = forecaster.forecast_resource_needs(request_forecast, resources_per_request)

# Visualize
plt.figure(figsize=(12, 6))
plt.plot(resource_forecast['ds'], resource_forecast['cpu_cores'], label='Forecasted CPU')
plt.plot(resource_forecast['ds'], resource_forecast['cpu_cores_with_buffer'], label='CPU with buffer', linestyle='--')
plt.xlabel('Date')
plt.ylabel('CPU Cores')
plt.title('CPU Capacity Forecast')
plt.legend()
plt.show()
```

---

## Resource Allocation Strategies

### Auto-Scaling Configuration

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-service-hpa
  namespace: ml-services
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: ml_prediction_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

### GPU Allocation

```yaml
# k8s/gpu-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training-gpu
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: trainer
        image: ml-trainer:latest
        resources:
          requests:
            nvidia.com/gpu: 2
            cpu: "4"
            memory: "32Gi"
          limits:
            nvidia.com/gpu: 2
            cpu: "8"
            memory: "64Gi"
      nodeSelector:
        accelerator: nvidia-tesla-a100
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
```

---

## Cost Optimization

### Cost Analysis

```python
# capacity/cost_analysis.py
import pandas as pd

class CostAnalyzer:
    def __init__(self, pricing):
        self.pricing = pricing  # Dict of resource prices

    def calculate_monthly_cost(self, resource_usage):
        """Calculate monthly infrastructure cost"""
        costs = {
            'compute': self._compute_cost(resource_usage),
            'storage': self._storage_cost(resource_usage),
            'network': self._network_cost(resource_usage),
            'gpu': self._gpu_cost(resource_usage)
        }

        total = sum(costs.values())

        return {
            'breakdown': costs,
            'total': total,
            'per_prediction': total / resource_usage['total_predictions']
        }

    def _compute_cost(self, usage):
        """Calculate compute costs"""
        # CPU hours
        cpu_cost = (
            usage['cpu_core_hours'] *
            self.pricing['cpu_per_core_hour']
        )

        # Memory costs
        memory_cost = (
            usage['memory_gb_hours'] *
            self.pricing['memory_per_gb_hour']
        )

        return cpu_cost + memory_cost

    def _gpu_cost(self, usage):
        """Calculate GPU costs"""
        return (
            usage['gpu_hours'] *
            self.pricing['gpu_per_hour']
        )

    def optimize_instance_types(self, workload_profile):
        """Recommend optimal instance types"""
        recommendations = []

        for workload in workload_profile:
            # Calculate cost for different instance types
            costs = {}
            for instance_type, specs in self.pricing['instance_types'].items():
                # Check if instance meets requirements
                if (specs['cpu'] >= workload['min_cpu'] and
                    specs['memory'] >= workload['min_memory']):

                    # Calculate cost
                    hours = workload['duration_hours']
                    cost = specs['price_per_hour'] * hours

                    costs[instance_type] = {
                        'cost': cost,
                        'specs': specs
                    }

            # Recommend cheapest option that meets requirements
            if costs:
                cheapest = min(costs.items(), key=lambda x: x[1]['cost'])
                recommendations.append({
                    'workload': workload['name'],
                    'recommended_instance': cheapest[0],
                    'cost': cheapest[1]['cost'],
                    'specs': cheapest[1]['specs']
                })

        return recommendations

# Usage
pricing = {
    'cpu_per_core_hour': 0.05,
    'memory_per_gb_hour': 0.01,
    'gpu_per_hour': 2.48,  # A100
    'instance_types': {
        'c5.2xlarge': {'cpu': 8, 'memory': 16, 'price_per_hour': 0.34},
        'c5.4xlarge': {'cpu': 16, 'memory': 32, 'price_per_hour': 0.68},
        'p3.2xlarge': {'cpu': 8, 'memory': 61, 'gpu': 1, 'price_per_hour': 3.06},
    }
}

analyzer = CostAnalyzer(pricing)

# Calculate current costs
current_usage = {
    'cpu_core_hours': 10000,
    'memory_gb_hours': 50000,
    'gpu_hours': 500,
    'total_predictions': 1000000
}

costs = analyzer.calculate_monthly_cost(current_usage)
print(f"Monthly cost: ${costs['total']:.2f}")
print(f"Cost per prediction: ${costs['per_prediction']:.4f}")
```

### Spot Instance Strategy

```python
# capacity/spot_strategy.py
import boto3
from datetime import datetime

class SpotInstanceManager:
    def __init__(self):
        self.ec2 = boto3.client('ec2')

    def get_spot_price_history(self, instance_type, days=7):
        """Get spot price history"""
        response = self.ec2.describe_spot_price_history(
            InstanceTypes=[instance_type],
            ProductDescriptions=['Linux/UNIX'],
            StartTime=datetime.now() - timedelta(days=days)
        )

        prices = pd.DataFrame(response['SpotPriceHistory'])
        prices['SpotPrice'] = prices['SpotPrice'].astype(float)

        return prices

    def recommend_bid_price(self, instance_type, risk_tolerance='medium'):
        """Recommend spot bid price based on historical data"""
        prices = self.get_spot_price_history(instance_type)

        if risk_tolerance == 'low':
            # 95th percentile - low interruption risk
            bid_price = prices['SpotPrice'].quantile(0.95)
        elif risk_tolerance == 'medium':
            # 75th percentile - moderate risk
            bid_price = prices['SpotPrice'].quantile(0.75)
        else:  # high
            # 50th percentile - higher interruption risk but cheaper
            bid_price = prices['SpotPrice'].quantile(0.50)

        return bid_price

    def estimate_cost_savings(self, instance_type, hours_per_month):
        """Estimate savings from using spot instances"""
        # Get current spot price
        spot_price = self.get_current_spot_price(instance_type)

        # Get on-demand price
        on_demand_price = self.get_on_demand_price(instance_type)

        # Calculate savings
        spot_cost = spot_price * hours_per_month
        on_demand_cost = on_demand_price * hours_per_month
        savings = on_demand_cost - spot_cost
        savings_percent = (savings / on_demand_cost) * 100

        return {
            'spot_cost': spot_cost,
            'on_demand_cost': on_demand_cost,
            'savings': savings,
            'savings_percent': savings_percent
        }
```

---

## Capacity Planning Dashboard

```python
# capacity/dashboard.py
import dash
from dash import dcc, html
import plotly.graph_objs as go

def create_capacity_dashboard(forecast_data, cost_data):
    """Create capacity planning dashboard"""
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("ML Infrastructure Capacity Planning"),

        html.Div([
            html.H2("Resource Forecast"),
            dcc.Graph(
                figure={
                    'data': [
                        go.Scatter(
                            x=forecast_data['date'],
                            y=forecast_data['cpu_cores'],
                            name='CPU Cores',
                            mode='lines'
                        ),
                        go.Scatter(
                            x=forecast_data['date'],
                            y=forecast_data['memory_gb'],
                            name='Memory (GB)',
                            mode='lines',
                            yaxis='y2'
                        )
                    ],
                    'layout': go.Layout(
                        title='Resource Forecast (90 days)',
                        yaxis={'title': 'CPU Cores'},
                        yaxis2={'title': 'Memory (GB)', 'overlaying': 'y', 'side': 'right'}
                    )
                }
            )
        ]),

        html.Div([
            html.H2("Cost Projection"),
            dcc.Graph(
                figure={
                    'data': [
                        go.Bar(
                            x=list(cost_data['breakdown'].keys()),
                            y=list(cost_data['breakdown'].values()),
                            name='Cost Breakdown'
                        )
                    ],
                    'layout': go.Layout(
                        title='Monthly Cost Breakdown',
                        yaxis={'title': 'Cost ($)'}
                    )
                }
            )
        ]),

        html.Div([
            html.H2("Utilization"),
            dcc.Graph(
                figure={
                    'data': [
                        go.Indicator(
                            mode="gauge+number",
                            value=forecast_data['current_utilization'],
                            title={'text': "Current CPU Utilization"},
                            gauge={'axis': {'range': [0, 100]}}
                        )
                    ]
                }
            )
        ])
    ])

    return app

# Run dashboard
app = create_capacity_dashboard(forecast_data, cost_data)
app.run_server(debug=True, port=8050)
```

---

## Best Practices

1. **Monitor Continuously**: Track resource usage and trends
2. **Forecast Regularly**: Update forecasts monthly
3. **Plan for Growth**: Include 30-50% buffer
4. **Optimize Costs**: Use spot instances for training
5. **Right-Size Resources**: Match instance types to workloads
6. **Auto-Scale**: Configure HPA for inference services
7. **Review Regularly**: Quarterly capacity planning reviews

## Key Takeaways

- ML workloads have unique capacity planning needs
- Forecast demand using historical data and growth projections
- Optimize costs through instance selection and spot usage
- Auto-scaling is essential for inference workloads
- Regular monitoring and adjustment are crucial

## Exercises

1. Collect and analyze resource usage for your ML services
2. Build demand forecast model
3. Calculate current infrastructure costs
4. Design auto-scaling configuration
5. Create capacity planning dashboard

## Additional Resources

- "Systems Performance" by Brendan Gregg
- "Cost Optimization on AWS" (AWS Well-Architected)
- "Capacity Planning for Web Services" by John Allspaw
- Cloud provider capacity planning guides
