# Lecture 7: Multi-Cloud Cost Optimization

## Learning Objectives

By the end of this lecture, you will be able to:

- Design cost-optimized multi-cloud architectures analyzing pricing models across AWS, GCP, and Azure including compute (reserved/spot/preemptible), storage tiers, and egress costs
- Implement unified cost monitoring and allocation using cloud cost management tools (AWS Cost Explorer, GCP Cost Management, Azure Cost Management) and third-party platforms
- Architect workload placement strategies optimizing for cost by evaluating compute pricing, data transfer costs, and regional pricing differences to select optimal cloud/region combinations
- Apply automated cost optimization techniques including rightsizing recommendations, automated shutdown schedules, spot instance bidding strategies, and commitment-based discounts
- Implement FinOps practices for ML workloads establishing cost allocation tags, showback/chargeback models, budget alerts, and team accountability for cloud spending
- Design cost-aware ML training strategies using spot/preemptible instances, checkpointing for interruption recovery, and multi-cloud failover to minimize training costs
- Optimize storage costs across clouds implementing lifecycle policies, compression, deduplication, and tiered storage (hot/cool/archive) based on access patterns
- Build cost governance frameworks with spending limits, approval workflows, policy enforcement, and regular cost reviews achieving 20-40% cost reduction through optimization

## Overview

Cost optimization in multi-cloud environments presents unique challenges and opportunities. This lecture covers comprehensive strategies for managing, monitoring, and optimizing costs across multiple cloud providers while maintaining performance and reliability.

---

## 1. Understanding Multi-Cloud Cost Models

### 1.1 Cloud Provider Pricing Differences

#### AWS Pricing Model
```yaml
Compute:
  EC2:
    - On-Demand: Pay per second (Linux), minimum 60s
    - Reserved: 1-3 year commitments, up to 72% savings
    - Spot: Up to 90% savings, interruptible
    - Savings Plans: Flexible commitments, up to 72% savings

  Storage:
    S3:
      - Standard: $0.023/GB/month
      - Intelligent-Tiering: Automatic cost optimization
      - Glacier: $0.004/GB/month (archive)

  Network:
    - Ingress: Free
    - Egress: $0.09/GB first 10TB
    - Inter-region: $0.02/GB
```

#### GCP Pricing Model
```yaml
Compute:
  Compute Engine:
    - On-Demand: Pay per second, no minimum
    - Committed Use: 1-3 year, up to 57% savings
    - Preemptible: Up to 80% savings, 24h max
    - Sustained Use: Automatic discounts for continuous use

  Storage:
    Cloud Storage:
      - Standard: $0.020/GB/month
      - Nearline: $0.010/GB/month (30-day minimum)
      - Coldline: $0.004/GB/month (90-day minimum)

  Network:
    - Ingress: Free
    - Egress: $0.12/GB first 1TB
    - Same zone: Free
```

#### Azure Pricing Model
```yaml
Compute:
  Virtual Machines:
    - Pay-as-you-go: Per second billing
    - Reserved: 1-3 year, up to 72% savings
    - Spot: Up to 90% savings
    - Hybrid Benefit: Use existing licenses

  Storage:
    Blob Storage:
      - Hot: $0.0184/GB/month
      - Cool: $0.01/GB/month (30-day minimum)
      - Archive: $0.00099/GB/month (180-day minimum)

  Network:
    - Ingress: Free
    - Egress: $0.087/GB first 5GB free
    - Zone-to-zone: $0.01/GB
```

### 1.2 Cost Comparison Matrix

| Service Type | AWS | GCP | Azure | Notes |
|-------------|-----|-----|-------|-------|
| Compute (1 vCPU) | $35/mo | $25/mo | $30/mo | Baseline comparison |
| Storage (1TB) | $23/mo | $20/mo | $18.40/mo | Standard tier |
| Egress (1TB) | $90 | $120 | $87 | First TB pricing |
| GPU (V100) | $2.48/hr | $2.48/hr | $3.06/hr | On-demand pricing |
| Managed K8s | $73/mo | Free | Free | Control plane only |

### 1.3 Hidden Costs

```python
# Cost Analysis Framework
class MultiCloudCostAnalyzer:
    """Analyzes total cost of ownership across clouds"""

    def __init__(self):
        self.cost_components = {
            'compute': {},
            'storage': {},
            'network': {},
            'services': {},
            'hidden': {}
        }

    def calculate_hidden_costs(self, cloud_provider, usage):
        """
        Calculate often-overlooked costs
        """
        hidden_costs = {
            'data_transfer': self._calculate_transfer_costs(usage),
            'api_calls': self._calculate_api_costs(usage),
            'storage_operations': self._calculate_storage_ops(usage),
            'logging': self._calculate_logging_costs(usage),
            'monitoring': self._calculate_monitoring_costs(usage),
            'support': self._calculate_support_costs(usage)
        }

        return hidden_costs

    def _calculate_transfer_costs(self, usage):
        """
        Data transfer is often the largest hidden cost

        Common scenarios:
        - Cross-region replication
        - Multi-cloud data sync
        - CDN egress
        - VPN/Direct Connect
        """
        costs = {
            'inter_region': usage['inter_region_gb'] * 0.02,
            'inter_cloud': usage['inter_cloud_gb'] * 0.09,
            'cdn': usage['cdn_gb'] * 0.085,
            'vpn': usage['vpn_hours'] * 0.05
        }

        return sum(costs.values())

    def _calculate_api_costs(self, usage):
        """
        API calls can add up in ML pipelines
        """
        return {
            's3_puts': usage['s3_puts'] * 0.000005,
            's3_gets': usage['s3_gets'] * 0.0000004,
            'gcs_operations': usage['gcs_ops'] * 0.00001,
            'lambda_invocations': usage['lambda_calls'] * 0.0000002
        }

# Example usage
analyzer = MultiCloudCostAnalyzer()
monthly_usage = {
    'inter_region_gb': 5000,
    'inter_cloud_gb': 2000,
    'cdn_gb': 10000,
    'vpn_hours': 720,
    's3_puts': 10000000,
    's3_gets': 100000000,
    'gcs_ops': 5000000,
    'lambda_calls': 50000000
}

hidden = analyzer.calculate_hidden_costs('aws', monthly_usage)
print(f"Hidden costs: ${sum(hidden.values()):.2f}/month")
```

---

## 2. Cost Monitoring and Allocation

### 2.1 Unified Cost Dashboard

```python
# Multi-Cloud Cost Aggregator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
import boto3
from google.cloud import billing_v1
from azure.mgmt.consumption import ConsumptionManagementClient

@dataclass
class CostRecord:
    """Unified cost record across clouds"""
    date: datetime
    cloud: str
    service: str
    resource_id: str
    cost: float
    currency: str
    tags: Dict[str, str]

class UnifiedCostMonitor:
    """Aggregate costs across multiple clouds"""

    def __init__(self):
        self.aws_client = boto3.client('ce')  # Cost Explorer
        self.gcp_client = billing_v1.CloudBillingClient()
        self.azure_client = None  # Initialized with credentials

    def get_aws_costs(self, start_date, end_date, granularity='DAILY'):
        """
        Fetch AWS costs using Cost Explorer API
        """
        response = self.aws_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity=granularity,
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'TAG', 'Key': 'Project'},
                {'Type': 'TAG', 'Key': 'Environment'}
            ]
        )

        costs = []
        for result in response['ResultsByTime']:
            date = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')

            for group in result['Groups']:
                cost_record = CostRecord(
                    date=date,
                    cloud='aws',
                    service=group['Keys'][0],
                    resource_id='aggregated',
                    cost=float(group['Metrics']['UnblendedCost']['Amount']),
                    currency=group['Metrics']['UnblendedCost']['Unit'],
                    tags={
                        'project': group['Keys'][1] if len(group['Keys']) > 1 else 'untagged',
                        'environment': group['Keys'][2] if len(group['Keys']) > 2 else 'untagged'
                    }
                )
                costs.append(cost_record)

        return costs

    def get_gcp_costs(self, project_id, start_date, end_date):
        """
        Fetch GCP costs using Cloud Billing API
        """
        # Note: Requires BigQuery export to be configured
        from google.cloud import bigquery

        client = bigquery.Client(project=project_id)

        query = f"""
        SELECT
            DATE(usage_start_time) as date,
            service.description as service,
            sku.description as sku,
            SUM(cost) as cost,
            currency,
            labels
        FROM
            `{project_id}.billing_export.gcp_billing_export_v1_*`
        WHERE
            DATE(usage_start_time) BETWEEN @start_date AND @end_date
        GROUP BY
            date, service, sku, currency, labels
        ORDER BY
            date DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )

        results = client.query(query, job_config=job_config)

        costs = []
        for row in results:
            cost_record = CostRecord(
                date=row.date,
                cloud='gcp',
                service=row.service,
                resource_id=row.sku,
                cost=row.cost,
                currency=row.currency,
                tags=dict(row.labels) if row.labels else {}
            )
            costs.append(cost_record)

        return costs

    def generate_unified_report(self, start_date, end_date):
        """
        Generate unified cost report across all clouds
        """
        all_costs = []

        # Fetch from all clouds
        all_costs.extend(self.get_aws_costs(start_date, end_date))
        all_costs.extend(self.get_gcp_costs('my-project', start_date, end_date))
        # all_costs.extend(self.get_azure_costs(...))

        # Aggregate by cloud
        cloud_totals = {}
        for cost in all_costs:
            if cost.cloud not in cloud_totals:
                cloud_totals[cost.cloud] = 0
            cloud_totals[cost.cloud] += cost.cost

        # Aggregate by service
        service_totals = {}
        for cost in all_costs:
            key = f"{cost.cloud}:{cost.service}"
            if key not in service_totals:
                service_totals[key] = 0
            service_totals[key] += cost.cost

        return {
            'total': sum(cloud_totals.values()),
            'by_cloud': cloud_totals,
            'by_service': service_totals,
            'details': all_costs
        }

# Example usage
monitor = UnifiedCostMonitor()
report = monitor.generate_unified_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

print(f"Total multi-cloud spend: ${report['total']:.2f}")
for cloud, cost in report['by_cloud'].items():
    print(f"  {cloud}: ${cost:.2f}")
```

### 2.2 Cost Allocation with Tagging

```yaml
# Unified Tagging Strategy
tagging_policy:
  required_tags:
    - key: Environment
      values: [dev, staging, prod]
      enforcement: mandatory

    - key: Project
      values: [ml-platform, data-pipeline, inference]
      enforcement: mandatory

    - key: CostCenter
      values: [engineering, research, operations]
      enforcement: mandatory

    - key: Owner
      pattern: "^[a-z.]+@company.com$"
      enforcement: mandatory

  optional_tags:
    - key: Application
    - key: Team
    - key: ExpireDate

  # Cloud-specific implementations
  aws:
    resource_groups:
      - name: ml-platform-prod
        tags:
          Environment: prod
          Project: ml-platform

    cost_allocation_tags:
      - Environment
      - Project
      - CostCenter

  gcp:
    labels:  # GCP uses labels instead of tags
      - key: environment
      - key: project
      - key: cost_center

    billing_accounts:
      - id: "012345-ABCDEF-GHIJKL"
        projects:
          - ml-platform-prod
          - ml-platform-dev

  azure:
    tags:
      - Environment
      - Project
      - CostCenter

    resource_groups:
      - name: ml-platform-prod-rg
        location: eastus
```

```python
# Automated Tag Enforcement
class TagEnforcer:
    """Enforce tagging policies across clouds"""

    def __init__(self, policy_file):
        with open(policy_file) as f:
            self.policy = yaml.safe_load(f)

    def validate_aws_resource(self, resource_arn, tags):
        """Validate AWS resource tags"""
        required_tags = {
            tag['key'] for tag in self.policy['tagging_policy']['required_tags']
        }

        existing_tags = {tag['Key'] for tag in tags}
        missing_tags = required_tags - existing_tags

        if missing_tags:
            return False, f"Missing required tags: {missing_tags}"

        # Validate tag values
        for tag_spec in self.policy['tagging_policy']['required_tags']:
            tag_value = next(
                (t['Value'] for t in tags if t['Key'] == tag_spec['key']),
                None
            )

            if 'values' in tag_spec and tag_value not in tag_spec['values']:
                return False, f"Invalid value for {tag_spec['key']}: {tag_value}"

        return True, "Valid"

    def auto_tag_resources(self, cloud, resource_type, resource_id):
        """Automatically tag resources based on patterns"""
        auto_tags = {}

        # Example: Tag based on resource name patterns
        if 'prod' in resource_id:
            auto_tags['Environment'] = 'prod'
        elif 'staging' in resource_id:
            auto_tags['Environment'] = 'staging'
        else:
            auto_tags['Environment'] = 'dev'

        # Apply tags based on cloud
        if cloud == 'aws':
            self._apply_aws_tags(resource_id, auto_tags)
        elif cloud == 'gcp':
            self._apply_gcp_labels(resource_id, auto_tags)
        elif cloud == 'azure':
            self._apply_azure_tags(resource_id, auto_tags)

        return auto_tags
```

### 2.3 Chargeback and Showback

```python
# Cost Chargeback System
class ChargebackSystem:
    """Implement chargeback/showback for multi-cloud costs"""

    def __init__(self, cost_monitor):
        self.monitor = cost_monitor
        self.allocation_rules = {}

    def calculate_team_costs(self, start_date, end_date):
        """Calculate costs by team"""
        report = self.monitor.generate_unified_report(start_date, end_date)

        team_costs = {}
        for cost_record in report['details']:
            team = cost_record.tags.get('Team', 'unallocated')

            if team not in team_costs:
                team_costs[team] = {
                    'total': 0,
                    'by_cloud': {},
                    'by_service': {}
                }

            team_costs[team]['total'] += cost_record.cost

            # Track by cloud
            cloud = cost_record.cloud
            if cloud not in team_costs[team]['by_cloud']:
                team_costs[team]['by_cloud'][cloud] = 0
            team_costs[team]['by_cloud'][cloud] += cost_record.cost

            # Track by service
            service = cost_record.service
            if service not in team_costs[team]['by_service']:
                team_costs[team]['by_service'][service] = 0
            team_costs[team]['by_service'][service] += cost_record.cost

        return team_costs

    def allocate_shared_costs(self, team_costs, shared_services):
        """
        Allocate shared infrastructure costs

        Examples:
        - Networking (VPN, Direct Connect)
        - Monitoring (Prometheus, Grafana)
        - Security (WAF, GuardDuty)
        """
        for service, total_cost in shared_services.items():
            # Calculate allocation percentage
            total_usage = sum(tc['total'] for tc in team_costs.values())

            for team, costs in team_costs.items():
                # Allocate proportionally
                allocation_pct = costs['total'] / total_usage
                allocated_cost = total_cost * allocation_pct

                costs['shared_services'] = costs.get('shared_services', {})
                costs['shared_services'][service] = allocated_cost
                costs['total'] += allocated_cost

        return team_costs

    def generate_invoice(self, team, costs, billing_period):
        """Generate chargeback invoice"""
        invoice = {
            'team': team,
            'billing_period': billing_period,
            'line_items': [],
            'total': costs['total']
        }

        # Add cloud costs
        for cloud, cost in costs['by_cloud'].items():
            invoice['line_items'].append({
                'category': 'Cloud Infrastructure',
                'description': f'{cloud.upper()} services',
                'amount': cost
            })

        # Add shared services
        for service, cost in costs.get('shared_services', {}).items():
            invoice['line_items'].append({
                'category': 'Shared Services',
                'description': service,
                'amount': cost
            })

        return invoice
```

---

## 3. Cost Optimization Strategies

### 3.1 Right-Sizing Resources

```python
# Resource Right-Sizing Analyzer
class RightSizingAnalyzer:
    """Analyze and recommend resource optimizations"""

    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.ec2 = boto3.client('ec2')

    def analyze_ec2_instance(self, instance_id, days=14):
        """
        Analyze EC2 instance utilization
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Get CPU utilization
        cpu_stats = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour
            Statistics=['Average', 'Maximum']
        )

        # Get memory utilization (requires CloudWatch agent)
        memory_stats = self.cloudwatch.get_metric_statistics(
            Namespace='CWAgent',
            MetricName='mem_used_percent',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )

        # Get network utilization
        network_stats = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )

        # Calculate averages
        avg_cpu = sum(d['Average'] for d in cpu_stats['Datapoints']) / len(cpu_stats['Datapoints'])
        max_cpu = max(d['Maximum'] for d in cpu_stats['Datapoints'])

        avg_memory = sum(d['Average'] for d in memory_stats['Datapoints']) / len(memory_stats['Datapoints']) if memory_stats['Datapoints'] else 0
        max_memory = max(d['Maximum'] for d in memory_stats['Datapoints']) if memory_stats['Datapoints'] else 0

        # Get instance details
        instance = self.ec2.describe_instances(InstanceIds=[instance_id])
        instance_type = instance['Reservations'][0]['Instances'][0]['InstanceType']

        # Recommendation logic
        recommendation = self._generate_recommendation(
            instance_type, avg_cpu, max_cpu, avg_memory, max_memory
        )

        return {
            'instance_id': instance_id,
            'current_type': instance_type,
            'avg_cpu': avg_cpu,
            'max_cpu': max_cpu,
            'avg_memory': avg_memory,
            'max_memory': max_memory,
            'recommendation': recommendation
        }

    def _generate_recommendation(self, current_type, avg_cpu, max_cpu, avg_memory, max_memory):
        """Generate right-sizing recommendation"""
        # Parse instance type
        family, size = self._parse_instance_type(current_type)

        if avg_cpu < 20 and max_cpu < 40:
            return {
                'action': 'downsize',
                'reason': f'Low CPU utilization (avg: {avg_cpu:.1f}%, max: {max_cpu:.1f}%)',
                'suggested_type': self._get_smaller_instance(current_type),
                'potential_savings': self._calculate_savings(current_type, 'downsize')
            }

        elif avg_cpu > 70 or max_cpu > 90:
            return {
                'action': 'upsize',
                'reason': f'High CPU utilization (avg: {avg_cpu:.1f}%, max: {max_cpu:.1f}%)',
                'suggested_type': self._get_larger_instance(current_type),
                'additional_cost': self._calculate_savings(current_type, 'upsize')
            }

        elif avg_memory > 0 and avg_memory < 30 and max_memory < 50:
            return {
                'action': 'switch_family',
                'reason': f'Low memory utilization (avg: {avg_memory:.1f}%, max: {max_memory:.1f}%)',
                'suggested_type': self._get_compute_optimized(current_type),
                'potential_savings': self._calculate_savings(current_type, 'compute_optimized')
            }

        else:
            return {
                'action': 'no_change',
                'reason': 'Resource utilization is appropriate',
                'suggested_type': current_type,
                'potential_savings': 0
            }

    def _parse_instance_type(self, instance_type):
        """Parse instance type into family and size"""
        # Example: m5.xlarge -> (m5, xlarge)
        parts = instance_type.split('.')
        return parts[0], parts[1] if len(parts) > 1 else None

    def _get_smaller_instance(self, current_type):
        """Get next smaller instance size"""
        size_progression = ['nano', 'micro', 'small', 'medium', 'large', 'xlarge', '2xlarge', '4xlarge', '8xlarge']
        family, size = self._parse_instance_type(current_type)

        if size in size_progression:
            current_idx = size_progression.index(size)
            if current_idx > 0:
                return f"{family}.{size_progression[current_idx - 1]}"

        return current_type

    def _calculate_savings(self, current_type, action):
        """Calculate potential cost savings"""
        # Simplified pricing lookup
        pricing = {
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.170
        }

        current_cost = pricing.get(current_type, 0.10) * 730  # hours/month

        if action == 'downsize':
            new_type = self._get_smaller_instance(current_type)
            new_cost = pricing.get(new_type, 0.05) * 730
            return current_cost - new_cost

        return 0

# Example usage
analyzer = RightSizingAnalyzer()
recommendation = analyzer.analyze_ec2_instance('i-1234567890abcdef')
print(f"Recommendation: {recommendation['recommendation']['action']}")
print(f"Potential savings: ${recommendation['recommendation']['potential_savings']:.2f}/month")
```

### 3.2 Commitment-Based Discounts

```python
# Reserved Instance / Commitment Analyzer
class CommitmentAnalyzer:
    """Analyze and recommend commitment-based purchases"""

    def __init__(self):
        self.ce_client = boto3.client('ce')

    def analyze_reservation_opportunities(self, lookback_days=30):
        """
        Identify opportunities for Reserved Instances or Savings Plans
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        # Get EC2 usage
        response = self.ce_client.get_reservation_purchase_recommendation(
            AccountId='123456789012',
            Service='Amazon Elastic Compute Cloud - Compute',
            LookbackPeriodInDays='THIRTY_DAYS',
            TermInYears='ONE_YEAR',
            PaymentOption='NO_UPFRONT'
        )

        recommendations = []
        for rec in response.get('Recommendations', []):
            detail = rec['RecommendationDetail']

            recommendation = {
                'instance_type': detail['InstanceDetails']['EC2InstanceDetails']['InstanceType'],
                'region': detail['InstanceDetails']['EC2InstanceDetails']['Region'],
                'average_utilization': detail['AverageUtilization'],
                'estimated_monthly_savings': float(detail['EstimatedMonthlySavingsAmount']),
                'upfront_cost': float(detail['UpfrontCost']),
                'estimated_roi': self._calculate_roi(
                    float(detail['UpfrontCost']),
                    float(detail['EstimatedMonthlySavingsAmount']),
                    12
                ),
                'recommended_quantity': detail['RecommendedNumberOfInstancesToPurchase']
            }

            recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: x['estimated_monthly_savings'], reverse=True)

    def _calculate_roi(self, upfront_cost, monthly_savings, months):
        """Calculate ROI for commitment"""
        total_savings = monthly_savings * months
        if upfront_cost > 0:
            roi = ((total_savings - upfront_cost) / upfront_cost) * 100
        else:
            roi = 100
        return roi

    def compare_commitment_options(self, instance_type, hours_per_month=730):
        """
        Compare on-demand vs different commitment options
        """
        # Example pricing (simplified)
        pricing = {
            'on_demand': 0.096,
            'reserved_1yr_no_upfront': 0.062,
            'reserved_1yr_partial_upfront': 0.060,
            'reserved_1yr_all_upfront': 0.058,
            'reserved_3yr_no_upfront': 0.045,
            'reserved_3yr_partial_upfront': 0.043,
            'reserved_3yr_all_upfront': 0.041,
            'savings_plan_1yr': 0.064,
            'savings_plan_3yr': 0.046
        }

        comparison = {}
        for option, hourly_rate in pricing.items():
            monthly_cost = hourly_rate * hours_per_month
            annual_cost = monthly_cost * 12

            if 'upfront' in option:
                # Add upfront payment
                if 'partial' in option:
                    upfront = annual_cost * 0.5
                elif 'all' in option:
                    upfront = annual_cost
                else:
                    upfront = 0
            else:
                upfront = 0

            comparison[option] = {
                'hourly_rate': hourly_rate,
                'monthly_cost': monthly_cost,
                'annual_cost': annual_cost,
                'upfront_cost': upfront,
                'total_1yr_cost': annual_cost + upfront,
                'savings_vs_on_demand': (pricing['on_demand'] * hours_per_month * 12) - (annual_cost + upfront)
            }

        return comparison

# Example usage
analyzer = CommitmentAnalyzer()
opportunities = analyzer.analyze_reservation_opportunities()
for opp in opportunities[:5]:  # Top 5 opportunities
    print(f"{opp['instance_type']}: ${opp['estimated_monthly_savings']:.2f}/month savings")
    print(f"  ROI: {opp['estimated_roi']:.1f}%")
```

### 3.3 Automated Scaling and Scheduling

```python
# Cost-Aware Auto-Scaling
class CostAwareAutoScaler:
    """Implement cost-optimized auto-scaling"""

    def __init__(self):
        self.autoscaling = boto3.client('autoscaling')
        self.ec2 = boto3.client('ec2')

    def create_cost_optimized_asg(self, config):
        """
        Create ASG with cost optimization features
        """
        launch_template = {
            'LaunchTemplateName': config['name'],
            'VersionDescription': 'Cost-optimized configuration',
            'LaunchTemplateData': {
                'InstanceType': config['instance_type'],
                'ImageId': config['ami_id'],
                'IamInstanceProfile': {'Name': config['instance_profile']},
                'UserData': config.get('user_data', ''),
                'TagSpecifications': [{
                    'ResourceType': 'instance',
                    'Tags': config['tags']
                }],
                # Mixed instance policy for cost optimization
                'InstanceMarketOptions': {
                    'MarketType': 'spot',
                    'SpotOptions': {
                        'MaxPrice': str(config.get('max_spot_price', 0.05)),
                        'SpotInstanceType': 'one-time'
                    }
                }
            }
        }

        # Create mixed instances policy
        mixed_instances_policy = {
            'LaunchTemplate': {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': config['name'],
                    'Version': '$Latest'
                },
                'Overrides': self._generate_instance_overrides(config['instance_type'])
            },
            'InstancesDistribution': {
                'OnDemandAllocationStrategy': 'prioritized',
                'OnDemandBaseCapacity': config.get('on_demand_base', 1),
                'OnDemandPercentageAboveBaseCapacity': config.get('on_demand_percentage', 20),
                'SpotAllocationStrategy': 'capacity-optimized',
                'SpotInstancePools': 4,
                'SpotMaxPrice': str(config.get('max_spot_price', ''))
            }
        }

        return mixed_instances_policy

    def _generate_instance_overrides(self, base_instance_type):
        """
        Generate instance type overrides for diversification
        """
        # Get instance family
        family = base_instance_type.split('.')[0]

        # Similar instance types for diversification
        instance_mapping = {
            'm5': ['m5.large', 'm5.xlarge', 'm5a.large', 'm5a.xlarge', 'm4.large'],
            'c5': ['c5.large', 'c5.xlarge', 'c5a.large', 'c5a.xlarge', 'c4.large'],
            't3': ['t3.medium', 't3.large', 't3a.medium', 't3a.large', 't2.large']
        }

        overrides = []
        for instance_type in instance_mapping.get(family, [base_instance_type]):
            overrides.append({'InstanceType': instance_type})

        return overrides

    def configure_scheduled_scaling(self, asg_name, schedule):
        """
        Configure scheduled scaling for predictable workloads

        Example schedule:
        {
            'business_hours': {
                'min_size': 10,
                'max_size': 50,
                'desired_capacity': 20,
                'recurrence': '0 8 * * MON-FRI'
            },
            'off_hours': {
                'min_size': 2,
                'max_size': 10,
                'desired_capacity': 3,
                'recurrence': '0 18 * * MON-FRI'
            },
            'weekend': {
                'min_size': 1,
                'max_size': 5,
                'desired_capacity': 2,
                'recurrence': '0 0 * * SAT,SUN'
            }
        }
        """
        for schedule_name, config in schedule.items():
            self.autoscaling.put_scheduled_update_group_action(
                AutoScalingGroupName=asg_name,
                ScheduledActionName=f"{asg_name}-{schedule_name}",
                Recurrence=config['recurrence'],
                MinSize=config['min_size'],
                MaxSize=config['max_size'],
                DesiredCapacity=config['desired_capacity']
            )

        print(f"Configured {len(schedule)} scheduled scaling actions for {asg_name}")

# Example usage
scaler = CostAwareAutoScaler()
config = {
    'name': 'ml-training-cluster',
    'instance_type': 'm5.xlarge',
    'ami_id': 'ami-12345678',
    'instance_profile': 'ml-instance-role',
    'on_demand_base': 2,
    'on_demand_percentage': 20,
    'max_spot_price': 0.08,
    'tags': [
        {'Key': 'Environment', 'Value': 'production'},
        {'Key': 'Project', 'Value': 'ml-training'}
    ]
}

policy = scaler.create_cost_optimized_asg(config)
```

---

## 4. ML-Specific Cost Optimization

### 4.1 Training Cost Optimization

```python
# ML Training Cost Optimizer
class MLTrainingCostOptimizer:
    """Optimize costs for ML training workloads"""

    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.sagemaker = boto3.client('sagemaker')

    def estimate_training_cost(self, training_config):
        """
        Estimate cost for training job
        """
        instance_type = training_config['instance_type']
        instance_count = training_config.get('instance_count', 1)
        estimated_duration_hours = training_config['estimated_duration_hours']

        # GPU pricing (simplified)
        gpu_pricing = {
            'ml.p3.2xlarge': 3.06,    # V100
            'ml.p3.8xlarge': 12.24,   # 4x V100
            'ml.p3.16xlarge': 24.48,  # 8x V100
            'ml.p4d.24xlarge': 32.77, # 8x A100
            'ml.g4dn.xlarge': 0.526,  # T4
            'ml.g4dn.12xlarge': 3.912 # 4x T4
        }

        hourly_cost = gpu_pricing.get(instance_type, 1.0)
        total_cost = hourly_cost * instance_count * estimated_duration_hours

        # Add storage costs
        volume_size_gb = training_config.get('volume_size_gb', 100)
        storage_cost = (volume_size_gb * 0.10 / 730) * estimated_duration_hours

        # Add data transfer costs
        data_size_gb = training_config.get('data_size_gb', 0)
        transfer_cost = data_size_gb * 0.09  # Inter-region transfer

        return {
            'compute_cost': total_cost,
            'storage_cost': storage_cost,
            'transfer_cost': transfer_cost,
            'total_cost': total_cost + storage_cost + transfer_cost,
            'cost_per_epoch': (total_cost + storage_cost) / training_config.get('epochs', 1)
        }

    def optimize_training_strategy(self, training_config):
        """
        Recommend cost-optimized training strategy
        """
        base_cost = self.estimate_training_cost(training_config)

        # Option 1: Use Spot instances
        spot_config = training_config.copy()
        spot_config['use_spot'] = True
        spot_cost = base_cost['total_cost'] * 0.3  # ~70% savings

        # Option 2: Distributed training
        distributed_config = training_config.copy()
        distributed_config['instance_count'] = training_config.get('instance_count', 1) * 4
        distributed_config['estimated_duration_hours'] = training_config['estimated_duration_hours'] / 3
        distributed_cost = self.estimate_training_cost(distributed_config)

        # Option 3: Smaller GPU instances
        smaller_config = training_config.copy()
        smaller_config['instance_type'] = self._get_smaller_gpu(training_config['instance_type'])
        smaller_config['estimated_duration_hours'] = training_config['estimated_duration_hours'] * 1.5
        smaller_cost = self.estimate_training_cost(smaller_config)

        recommendations = [
            {
                'strategy': 'baseline',
                'description': 'Current configuration',
                'cost': base_cost['total_cost'],
                'duration': training_config['estimated_duration_hours']
            },
            {
                'strategy': 'spot_instances',
                'description': 'Use Spot instances (may be interrupted)',
                'cost': spot_cost,
                'duration': training_config['estimated_duration_hours'],
                'savings': base_cost['total_cost'] - spot_cost
            },
            {
                'strategy': 'distributed',
                'description': 'Distributed training with 4x instances',
                'cost': distributed_cost['total_cost'],
                'duration': distributed_config['estimated_duration_hours'],
                'savings': base_cost['total_cost'] - distributed_cost['total_cost']
            },
            {
                'strategy': 'smaller_instance',
                'description': f"Use smaller GPU: {smaller_config['instance_type']}",
                'cost': smaller_cost['total_cost'],
                'duration': smaller_config['estimated_duration_hours'],
                'savings': base_cost['total_cost'] - smaller_cost['total_cost']
            }
        ]

        return sorted(recommendations, key=lambda x: x['cost'])

    def _get_smaller_gpu(self, instance_type):
        """Get smaller GPU instance type"""
        downsizing_map = {
            'ml.p3.16xlarge': 'ml.p3.8xlarge',
            'ml.p3.8xlarge': 'ml.p3.2xlarge',
            'ml.p4d.24xlarge': 'ml.p3.8xlarge',
            'ml.g4dn.12xlarge': 'ml.g4dn.xlarge'
        }
        return downsizing_map.get(instance_type, instance_type)

# Example usage
optimizer = MLTrainingCostOptimizer()
config = {
    'instance_type': 'ml.p3.8xlarge',
    'instance_count': 1,
    'estimated_duration_hours': 24,
    'epochs': 100,
    'volume_size_gb': 500,
    'data_size_gb': 1000
}

recommendations = optimizer.optimize_training_strategy(config)
for rec in recommendations:
    print(f"{rec['strategy']}: ${rec['cost']:.2f} ({rec['duration']:.1f}h)")
    if 'savings' in rec:
        print(f"  Savings: ${rec['savings']:.2f}")
```

### 4.2 Inference Cost Optimization

```python
# Inference Cost Optimizer
class InferenceCostOptimizer:
    """Optimize costs for model serving"""

    def calculate_inference_cost(self, deployment_config):
        """
        Calculate monthly inference costs
        """
        # Instance costs
        instance_type = deployment_config['instance_type']
        instance_count = deployment_config.get('instance_count', 1)

        instance_pricing = {
            'ml.t3.medium': 0.0416,
            'ml.c5.xlarge': 0.204,
            'ml.c5.2xlarge': 0.408,
            'ml.g4dn.xlarge': 0.736,
            'ml.inf1.xlarge': 0.368  # AWS Inferentia
        }

        hourly_cost = instance_pricing.get(instance_type, 0.1)
        monthly_instance_cost = hourly_cost * 730 * instance_count

        # Request costs (if using serverless)
        requests_per_month = deployment_config.get('requests_per_month', 0)
        cost_per_million_requests = 0.20
        request_cost = (requests_per_month / 1000000) * cost_per_million_requests

        # Data transfer costs
        avg_response_size_kb = deployment_config.get('avg_response_size_kb', 10)
        transfer_gb = (requests_per_month * avg_response_size_kb) / (1024 * 1024)
        transfer_cost = transfer_gb * 0.09

        return {
            'instance_cost': monthly_instance_cost,
            'request_cost': request_cost,
            'transfer_cost': transfer_cost,
            'total_monthly_cost': monthly_instance_cost + request_cost + transfer_cost,
            'cost_per_1k_requests': ((monthly_instance_cost + request_cost + transfer_cost) / requests_per_month) * 1000 if requests_per_month > 0 else 0
        }

    def recommend_deployment_type(self, workload_characteristics):
        """
        Recommend optimal deployment type based on workload
        """
        requests_per_month = workload_characteristics['requests_per_month']
        avg_request_duration_ms = workload_characteristics['avg_request_duration_ms']
        peak_rps = workload_characteristics['peak_rps']

        # Calculate required capacity
        required_capacity = peak_rps * (avg_request_duration_ms / 1000)

        options = []

        # Option 1: Always-on instances
        always_on_config = {
            'instance_type': 'ml.c5.xlarge',
            'instance_count': max(1, int(required_capacity / 100)),
            'requests_per_month': requests_per_month,
            'avg_response_size_kb': workload_characteristics.get('avg_response_size_kb', 10)
        }
        always_on_cost = self.calculate_inference_cost(always_on_config)
        options.append({
            'type': 'always_on',
            'config': always_on_config,
            'cost': always_on_cost['total_monthly_cost']
        })

        # Option 2: Serverless (Lambda/SageMaker Serverless)
        serverless_cost = {
            'compute': (requests_per_month / 1000000) * 1.0,  # $1 per million requests
            'duration': (requests_per_month * avg_request_duration_ms / 1000) * 0.0000166667,  # GB-second pricing
            'total': 0
        }
        serverless_cost['total'] = serverless_cost['compute'] + serverless_cost['duration']
        options.append({
            'type': 'serverless',
            'config': {'type': 'lambda'},
            'cost': serverless_cost['total']
        })

        # Option 3: Auto-scaling instances
        autoscaling_config = {
            'instance_type': 'ml.c5.xlarge',
            'min_instances': 1,
            'max_instances': always_on_config['instance_count'],
            'avg_instances': max(1, int(always_on_config['instance_count'] * 0.6)),
            'requests_per_month': requests_per_month,
            'avg_response_size_kb': workload_characteristics.get('avg_response_size_kb', 10)
        }
        autoscaling_config['instance_count'] = autoscaling_config['avg_instances']
        autoscaling_cost = self.calculate_inference_cost(autoscaling_config)
        options.append({
            'type': 'autoscaling',
            'config': autoscaling_config,
            'cost': autoscaling_cost['total_monthly_cost']
        })

        return sorted(options, key=lambda x: x['cost'])

# Example usage
optimizer = InferenceCostOptimizer()
workload = {
    'requests_per_month': 10000000,  # 10M requests
    'avg_request_duration_ms': 50,
    'peak_rps': 100,
    'avg_response_size_kb': 5
}

recommendations = optimizer.recommend_deployment_type(workload)
for rec in recommendations:
    print(f"{rec['type']}: ${rec['cost']:.2f}/month")
```

---

## 5. FinOps Best Practices

### 5.1 Cost Governance

```yaml
# Cost Governance Framework
cost_governance:
  budgets:
    - name: monthly_cloud_budget
      amount: 50000
      currency: USD
      period: monthly
      alerts:
        - threshold: 80
          notification: engineering-leads@company.com
        - threshold: 90
          notification: finance@company.com
        - threshold: 100
          notification: cto@company.com
          action: freeze_new_resources

    - name: ml_training_budget
      amount: 15000
      currency: USD
      period: monthly
      scope:
        tags:
          Project: ml-training
      alerts:
        - threshold: 75
          notification: ml-team@company.com

  policies:
    - name: require_cost_approval
      description: Require approval for resources > $1000/month
      rules:
        - resource_type: ec2_instance
          condition: monthly_cost > 1000
          action: require_approval
          approvers:
            - engineering-manager@company.com

    - name: auto_shutdown_dev
      description: Automatically shutdown dev resources after hours
      rules:
        - resource_type: [ec2_instance, rds_instance]
          condition: tags.Environment == 'dev'
          schedule:
            shutdown: "19:00 MON-FRI"
            startup: "08:00 MON-FRI"

    - name: prevent_expensive_instances
      description: Prevent launch of very expensive instances without approval
      rules:
        - resource_type: ec2_instance
          condition: instance_type in ['p4d.24xlarge', 'p3dn.24xlarge']
          action: require_approval

  reporting:
    frequency: weekly
    recipients:
      - finance@company.com
      - engineering-leads@company.com

    metrics:
      - total_spend
      - spend_by_cloud
      - spend_by_project
      - spend_by_environment
      - cost_anomalies
      - budget_utilization
      - forecast_vs_actual
```

### 5.2 Cost Optimization Checklist

```markdown
# Multi-Cloud Cost Optimization Checklist

## Daily Tasks
- [ ] Review cost anomaly alerts
- [ ] Check for unexpected spikes in usage
- [ ] Verify auto-scaling is working correctly
- [ ] Monitor spot instance interruptions

## Weekly Tasks
- [ ] Review cost trends across all clouds
- [ ] Analyze unused resources
- [ ] Check commitment utilization
- [ ] Review right-sizing recommendations
- [ ] Update cost forecasts

## Monthly Tasks
- [ ] Generate detailed cost reports
- [ ] Review and optimize storage tiers
- [ ] Analyze data transfer patterns
- [ ] Review reserved instance coverage
- [ ] Conduct cost allocation review
- [ ] Update cost models and forecasts
- [ ] Review and optimize multi-cloud architecture

## Quarterly Tasks
- [ ] Strategic review of cloud commitments
- [ ] Evaluate new cost-saving services
- [ ] Review multi-cloud strategy
- [ ] Optimize data residency and transfer
- [ ] Conduct FinOps maturity assessment
- [ ] Update cost governance policies

## Optimization Opportunities

### Compute
- [ ] Implement mixed instance types in ASGs
- [ ] Use Spot/Preemptible for fault-tolerant workloads
- [ ] Right-size based on actual utilization
- [ ] Evaluate ARM-based instances (Graviton, Tau T2A)
- [ ] Use committed discounts (RIs, CUDs, Savings Plans)

### Storage
- [ ] Implement lifecycle policies
- [ ] Use appropriate storage tiers
- [ ] Enable compression where applicable
- [ ] Clean up old snapshots and backups
- [ ] Optimize S3/GCS bucket configurations

### Network
- [ ] Minimize cross-region data transfer
- [ ] Use CDN for frequently accessed content
- [ ] Optimize VPN/interconnect usage
- [ ] Consolidate data processing in single region
- [ ] Use cloud provider backbone for inter-region traffic

### ML Workloads
- [ ] Use Spot for training jobs
- [ ] Optimize model serving infrastructure
- [ ] Implement model caching
- [ ] Use accelerators efficiently (GPU/TPU)
- [ ] Optimize batch inference scheduling

### Governance
- [ ] Enforce tagging policies
- [ ] Implement budget alerts
- [ ] Regular access review (remove unused accounts)
- [ ] Automate resource cleanup
- [ ] Enable cost allocation tags
```

---

## 6. Hands-On Exercise

### Exercise: Multi-Cloud Cost Dashboard

Create a unified cost monitoring dashboard that:
1. Aggregates costs from AWS, GCP, and Azure
2. Provides cost breakdown by service, project, and environment
3. Identifies cost optimization opportunities
4. Generates automated reports

**Implementation Steps:**

```python
# Step 1: Set up cost data collection
# Step 2: Implement unified cost model
# Step 3: Create aggregation logic
# Step 4: Build visualization dashboard
# Step 5: Implement alerting
# Step 6: Generate reports
```

---

## Summary

Multi-cloud cost optimization requires:
- Understanding different pricing models
- Implementing unified monitoring
- Enforcing cost allocation with tagging
- Using automation for optimization
- Adopting FinOps practices
- Continuous monitoring and improvement

## Key Takeaways

1. **Cost models differ significantly** between cloud providers
2. **Data transfer** is often the largest hidden cost
3. **Tagging is essential** for cost allocation
4. **Automation** is critical for continuous optimization
5. **Commitment-based discounts** can provide 50-70% savings
6. **Right-sizing** and **scheduling** are low-hanging fruit
7. **ML workloads** have unique optimization opportunities
8. **FinOps** is a cultural practice, not just tools

## Additional Resources

- AWS Cost Explorer API Documentation
- GCP Cloud Billing API Documentation
- Azure Cost Management API Documentation
- Cloud FinOps Foundation
- State of FinOps Report
- Multi-Cloud Cost Management Tools (CloudHealth, Cloudability, Kubecost)

## Next Steps

1. Implement unified cost monitoring
2. Set up automated tagging enforcement
3. Create cost allocation reports
4. Identify and purchase appropriate commitments
5. Implement cost governance policies
6. Train teams on FinOps practices
