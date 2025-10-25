# Lab 3: Multi-Cloud Cost Analysis

## Objective

Analyze and optimize costs across AWS, GCP, and Azure using unified cost monitoring and reporting.

## Prerequisites

- Access to AWS, GCP billing data
- Python 3.11+
- Understanding of cloud pricing models

## Estimated Time

2-3 hours

---

## Part 1: Set Up Cost Data Collection

### AWS Cost Explorer API

```python
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce', region_name='us-east-1')

def get_aws_costs(start_date, end_date):
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.strftime('%Y-%m-%d'),
            'End': end_date.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost', 'UsageQuantity'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'TAG', 'Key': 'Environment'}
        ]
    )
    return response
```

### GCP BigQuery Billing

```python
from google.cloud import bigquery

def get_gcp_costs(project_id, start_date, end_date):
    client = bigquery.Client(project=project_id)
    
    query = f"""
    SELECT
        DATE(usage_start_time) as date,
        service.description as service,
        SUM(cost) as cost,
        currency
    FROM
        `{project_id}.billing_export.gcp_billing_export_v1_*`
    WHERE
        DATE(usage_start_time) BETWEEN @start_date AND @end_date
    GROUP BY
        date, service, currency
    ORDER BY
        date DESC, cost DESC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        ]
    )
    
    return client.query(query, job_config=job_config).result()
```

---

## Part 2: Unified Cost Dashboard

```python
import pandas as pd
import plotly.graph_objects as go

class MultiCloudCostAnalyzer:
    def __init__(self):
        self.aws_costs = []
        self.gcp_costs = []
        self.azure_costs = []
    
    def generate_unified_report(self, start_date, end_date):
        # Collect data
        aws_data = self.collect_aws_costs(start_date, end_date)
        gcp_data = self.collect_gcp_costs(start_date, end_date)
        
        # Combine and analyze
        total_aws = sum(aws_data.values())
        total_gcp = sum(gcp_data.values())
        
        # Create visualizations
        self.create_cost_comparison_chart(aws_data, gcp_data)
        self.create_trend_analysis(start_date, end_date)
        
        return {
            'total_cost': total_aws + total_gcp,
            'aws_cost': total_aws,
            'gcp_cost': total_gcp,
            'recommendations': self.generate_recommendations()
        }
```

---

## Part 3: Cost Optimization Analysis

### Identify Savings Opportunities

```python
def analyze_savings_opportunities():
    opportunities = []
    
    # Unused resources
    opportunities.extend(find_unused_resources())
    
    # Right-sizing recommendations
    opportunities.extend(analyze_instance_utilization())
    
    # Commitment-based discounts
    opportunities.extend(analyze_reservation_coverage())
    
    # Storage optimization
    opportunities.extend(analyze_storage_tiers())
    
    return opportunities
```

---

## Exercises

1. Set up automated daily cost reports
2. Implement cost anomaly detection
3. Create cost allocation by team/project
4. Build cost forecasting model
5. Generate optimization recommendations

## Expected Outcomes

- Unified view of multi-cloud costs
- Identified savings opportunities
- Automated cost monitoring
- Cost allocation by business unit

## Cleanup

```bash
# Remove test resources
terraform destroy
```
