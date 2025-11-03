# Lecture 8: Multi-Cloud Disaster Recovery

## Learning Objectives

By the end of this lecture, you will be able to:

- Design multi-cloud DR architectures that meet specific RTO/RPO requirements (e.g., RTO <1hr, RPO <15min) using appropriate patterns (backup/restore, pilot light, warm standby, hot standby)
- Implement data replication strategies across clouds using object storage replication (S3→GCS, cross-region replication), database replication (read replicas, CDC), and filesystem sync
- Architect automated failover mechanisms using DNS-based failover (Route 53, Cloud DNS), load balancer failover, and application-level health checks with automatic traffic shifting
- Configure cross-cloud backup solutions implementing 3-2-1 backup strategy (3 copies, 2 media types, 1 offsite) with encrypted backups and lifecycle management
- Design failback procedures including data synchronization strategies, conflict resolution, and gradual traffic shifting to minimize risk during recovery to primary site
- Implement DR testing programs with regular DR drills, automated validation, runbook execution, and RTO/RPO measurement to ensure DR readiness
- Build chaos engineering practices for DR validation using failure injection, service disruption tests, and multi-cloud resilience testing to identify weaknesses
- Develop comprehensive DR documentation including disaster recovery plans, communication procedures, escalation paths, and post-incident review processes

## Overview

Disaster Recovery (DR) in multi-cloud environments provides unprecedented resilience and flexibility. This lecture covers comprehensive DR strategies, from designing multi-cloud DR architectures to implementing automated failover mechanisms and testing procedures.

---

## 1. DR Fundamentals

### 1.1 Key Concepts

#### Recovery Objectives

```
RTO (Recovery Time Objective)
├── Definition: Maximum acceptable downtime
├── Measured in: Minutes to hours
├── Impacts: Infrastructure complexity and cost
└── Examples:
    ├── Tier 1 (Critical): RTO < 1 hour
    ├── Tier 2 (Important): RTO < 4 hours
    ├── Tier 3 (Standard): RTO < 24 hours
    └── Tier 4 (Non-critical): RTO < 72 hours

RPO (Recovery Point Objective)
├── Definition: Maximum acceptable data loss
├── Measured in: Seconds to hours
├── Impacts: Replication strategy and cost
└── Examples:
    ├── Tier 1 (Zero data loss): RPO = 0 (synchronous replication)
    ├── Tier 2 (Minimal loss): RPO < 15 minutes
    ├── Tier 3 (Low loss): RPO < 1 hour
    └── Tier 4 (Acceptable loss): RPO < 24 hours
```

#### DR Patterns

```yaml
dr_patterns:
  backup_restore:
    rto: 24+ hours
    rpo: Hours to days
    cost: Low
    complexity: Low
    description: Regular backups restored when needed

  pilot_light:
    rto: 1-4 hours
    rpo: Minutes to hours
    cost: Low-Medium
    complexity: Medium
    description: Minimal version running, scaled up during disaster

  warm_standby:
    rto: Minutes to 1 hour
    rpo: Minutes
    cost: Medium-High
    complexity: Medium-High
    description: Scaled-down version running, ready to scale up

  hot_standby:
    rto: Seconds to minutes
    rpo: Seconds to minutes
    cost: High
    complexity: High
    description: Full-scale duplicate environment, active-active

  multi_cloud_active_active:
    rto: Seconds
    rpo: Near-zero
    cost: Very High
    complexity: Very High
    description: Multiple clouds serving traffic simultaneously
```

### 1.2 Multi-Cloud DR Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Global Traffic Manager                  │
│                    (Route53, Cloud DNS, Traffic Manager)        │
│                     Health checks, Geographic routing            │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             │                              │
   ┌─────────▼─────────────────┐  ┌────────▼──────────────────┐
   │      Primary Region        │  │    Secondary Region       │
   │         (AWS)              │  │        (GCP)              │
   │                            │  │                           │
   │  ┌──────────────────────┐  │  │  ┌──────────────────────┐│
   │  │  Application Tier    │  │  │  │  Application Tier    ││
   │  │  - EKS Cluster       │  │  │  │  - GKE Cluster       ││
   │  │  - Auto Scaling      │◄─┼──┼──┤  - Warm Standby      ││
   │  │  - Load Balancer     │  │  │  │  - Load Balancer     ││
   │  └──────────────────────┘  │  │  └──────────────────────┘│
   │                            │  │                           │
   │  ┌──────────────────────┐  │  │  ┌──────────────────────┐│
   │  │    Data Tier         │  │  │  │    Data Tier         ││
   │  │  - RDS Primary       │  │  │  │  - Cloud SQL Replica ││
   │  │  - S3 Buckets        │◄─┼──┼─►│  - GCS Buckets       ││
   │  │  - ElastiCache       │  │  │  │  - Memorystore       ││
   │  └──────────────────────┘  │  │  └──────────────────────┘│
   │                            │  │                           │
   │  ┌──────────────────────┐  │  │  ┌──────────────────────┐│
   │  │  Monitoring          │  │  │  │  Monitoring          ││
   │  │  - CloudWatch        │◄─┼──┼─►│  - Cloud Monitoring  ││
   │  │  - Prometheus        │  │  │  │  - Prometheus        ││
   │  └──────────────────────┘  │  │  └──────────────────────┘│
   └────────────────────────────┘  └───────────────────────────┘
             │                              │
             └──────────────┬───────────────┘
                            │
                   ┌────────▼─────────┐
                   │  Backup Region   │
                   │     (Azure)      │
                   │                  │
                   │  - Long-term     │
                   │    backups       │
                   │  - Archive       │
                   │    storage       │
                   └──────────────────┘
```

---

## 2. Data Replication Strategies

### 2.1 Database Replication

```python
# Multi-Cloud Database Replication Manager
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import time
import logging

class ReplicationType(Enum):
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    SEMI_SYNCHRONOUS = "semi_synchronous"

@dataclass
class ReplicationEndpoint:
    """Database replication endpoint"""
    cloud: str
    region: str
    endpoint: str
    port: int
    role: str  # 'primary', 'replica', 'standby'

class DatabaseReplicationManager:
    """Manage multi-cloud database replication"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.endpoints = []
        self.replication_lag = {}

    def configure_cross_cloud_replication(
        self,
        primary: ReplicationEndpoint,
        replicas: List[ReplicationEndpoint],
        replication_type: ReplicationType
    ):
        """
        Configure cross-cloud database replication

        Example:
        - Primary: AWS RDS PostgreSQL
        - Replica 1: GCP Cloud SQL PostgreSQL
        - Replica 2: Azure Database for PostgreSQL
        """
        self.logger.info(f"Configuring {replication_type.value} replication")

        # AWS RDS as primary
        if primary.cloud == 'aws':
            return self._configure_aws_primary_replication(
                primary, replicas, replication_type
            )

        # GCP Cloud SQL as primary
        elif primary.cloud == 'gcp':
            return self._configure_gcp_primary_replication(
                primary, replicas, replication_type
            )

        # Azure as primary
        elif primary.cloud == 'azure':
            return self._configure_azure_primary_replication(
                primary, replicas, replication_type
            )

    def _configure_aws_primary_replication(
        self,
        primary: ReplicationEndpoint,
        replicas: List[ReplicationEndpoint],
        replication_type: ReplicationType
    ):
        """
        Configure AWS RDS as primary with cross-cloud replicas
        """
        import boto3

        rds = boto3.client('rds', region_name=primary.region)

        # Enable binary logging for replication
        parameter_group_config = {
            'Parameters': [
                {
                    'ParameterName': 'log_bin',
                    'ParameterValue': '1'
                },
                {
                    'ParameterName': 'binlog_format',
                    'ParameterValue': 'ROW'
                },
                {
                    'ParameterName': 'binlog_row_image',
                    'ParameterValue': 'FULL'
                }
            ]
        }

        # Create replication user
        replication_user_sql = """
        CREATE USER 'repl_user'@'%' IDENTIFIED BY 'secure_password';
        GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
        FLUSH PRIVILEGES;
        """

        # Get binary log position
        position_query = "SHOW MASTER STATUS;"

        # For each replica, configure external replication
        for replica in replicas:
            if replica.cloud == 'gcp':
                self._setup_gcp_replica_from_aws(primary, replica)
            elif replica.cloud == 'azure':
                self._setup_azure_replica_from_aws(primary, replica)

        return {
            'status': 'configured',
            'primary': primary,
            'replicas': replicas,
            'replication_type': replication_type.value
        }

    def _setup_gcp_replica_from_aws(
        self,
        primary: ReplicationEndpoint,
        replica: ReplicationEndpoint
    ):
        """
        Set up GCP Cloud SQL as replica of AWS RDS
        """
        from google.cloud import sql_v1

        client = sql_v1.SqlInstancesServiceClient()

        # Create external master configuration
        external_master_config = {
            'kind': 'sql#instancesImportContext',
            'dumpFilePath': 'gs://my-bucket/initial-dump.sql',  # Initial data
            'importUser': 'repl_user',
            'externalMasterSettings': {
                'kind': 'sql#externalMaster',
                'host': primary.endpoint,
                'port': primary.port,
                'username': 'repl_user',
                'password': 'secure_password',
                'caCertificate': 'PEM_ENCODED_CERT',
                'clientCertificate': 'PEM_ENCODED_CERT',
                'clientKey': 'PEM_ENCODED_KEY'
            }
        }

        # Create replica instance
        instance_config = {
            'name': replica.endpoint.split('.')[0],
            'databaseVersion': 'POSTGRES_14',
            'region': replica.region,
            'settings': {
                'tier': 'db-n1-standard-2',
                'replicationType': 'ASYNCHRONOUS',
                'ipConfiguration': {
                    'ipv4Enabled': True,
                    'authorizedNetworks': [
                        {'value': '0.0.0.0/0'}  # Configure appropriately
                    ]
                }
            },
            'masterInstanceName': None,  # External master
            'replicaConfiguration': {
                'kind': 'sql#replicaConfiguration',
                'mysqlReplicaConfiguration': external_master_config
            }
        }

        self.logger.info(f"Creating GCP replica from AWS primary")
        return instance_config

    def monitor_replication_lag(self):
        """
        Monitor replication lag across all endpoints
        """
        for replica in self.endpoints:
            if replica.role == 'replica':
                lag = self._get_replication_lag(replica)
                self.replication_lag[replica.endpoint] = lag

                if lag > 300:  # 5 minutes
                    self.logger.warning(
                        f"High replication lag detected: {replica.endpoint} "
                        f"({lag}s behind primary)"
                    )

        return self.replication_lag

    def _get_replication_lag(self, replica: ReplicationEndpoint) -> int:
        """
        Get replication lag in seconds for a replica
        """
        # Implementation varies by database and cloud provider

        if replica.cloud == 'aws':
            # Use CloudWatch ReplicaLag metric
            import boto3
            cloudwatch = boto3.client('cloudwatch', region_name=replica.region)

            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='ReplicaLag',
                Dimensions=[
                    {'Name': 'DBInstanceIdentifier', 'Value': replica.endpoint.split('.')[0]}
                ],
                StartTime=time.time() - 300,
                EndTime=time.time(),
                Period=60,
                Statistics=['Average']
            )

            if response['Datapoints']:
                return int(response['Datapoints'][-1]['Average'])

        elif replica.cloud == 'gcp':
            # Query replica status
            query = "SELECT EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))"
            # Execute query and return lag

        return 0

# Example usage
manager = DatabaseReplicationManager()

primary = ReplicationEndpoint(
    cloud='aws',
    region='us-east-1',
    endpoint='prod-db.abc123.us-east-1.rds.amazonaws.com',
    port=5432,
    role='primary'
)

replicas = [
    ReplicationEndpoint(
        cloud='gcp',
        region='us-central1',
        endpoint='prod-db-replica.us-central1.sql.gcp',
        port=5432,
        role='replica'
    ),
    ReplicationEndpoint(
        cloud='azure',
        region='eastus',
        endpoint='prod-db-replica.postgres.database.azure.com',
        port=5432,
        role='replica'
    )
]

manager.configure_cross_cloud_replication(
    primary,
    replicas,
    ReplicationType.ASYNCHRONOUS
)

# Monitor replication
lag_report = manager.monitor_replication_lag()
```

### 2.2 Object Storage Replication

```python
# Multi-Cloud Object Storage Replication
class ObjectStorageReplicator:
    """Replicate objects across cloud storage services"""

    def __init__(self):
        self.s3_client = None  # boto3.client('s3')
        self.gcs_client = None  # google.cloud.storage.Client()
        self.azure_client = None  # azure.storage.blob.BlobServiceClient

    def configure_bidirectional_replication(
        self,
        source_config: Dict,
        destination_config: Dict
    ):
        """
        Configure bidirectional replication between cloud storage services
        """
        # AWS S3 replication configuration
        if source_config['provider'] == 'aws':
            replication_config = {
                'Role': 'arn:aws:iam::123456789012:role/replication-role',
                'Rules': [
                    {
                        'ID': 'ReplicateToGCP',
                        'Status': 'Enabled',
                        'Priority': 1,
                        'Filter': {'Prefix': ''},
                        'Destination': {
                            'Bucket': f"arn:aws:s3:::{destination_config['bucket']}",
                            'StorageClass': 'STANDARD',
                            'ReplicationTime': {
                                'Status': 'Enabled',
                                'Time': {'Minutes': 15}
                            },
                            'Metrics': {
                                'Status': 'Enabled',
                                'EventThreshold': {'Minutes': 15}
                            }
                        },
                        'DeleteMarkerReplication': {'Status': 'Enabled'}
                    }
                ]
            }

            # Enable versioning (required for replication)
            # self.s3_client.put_bucket_versioning(...)

            # Apply replication configuration
            # self.s3_client.put_bucket_replication(...)

        return replication_config

    def sync_storage_across_clouds(
        self,
        source_bucket: str,
        source_provider: str,
        dest_bucket: str,
        dest_provider: str,
        incremental: bool = True
    ):
        """
        Synchronize storage between different cloud providers
        """
        self.logger.info(
            f"Syncing {source_provider}:{source_bucket} -> "
            f"{dest_provider}:{dest_bucket}"
        )

        # List objects in source
        source_objects = self._list_objects(source_provider, source_bucket)

        # List objects in destination
        dest_objects = self._list_objects(dest_provider, dest_bucket)

        # Calculate differences
        if incremental:
            objects_to_sync = self._calculate_diff(source_objects, dest_objects)
        else:
            objects_to_sync = source_objects

        # Copy objects
        for obj in objects_to_sync:
            self._copy_object_across_clouds(
                source_provider, source_bucket, obj,
                dest_provider, dest_bucket
            )

        return {
            'synced_objects': len(objects_to_sync),
            'total_source_objects': len(source_objects),
            'status': 'complete'
        }

    def _copy_object_across_clouds(
        self,
        source_provider: str,
        source_bucket: str,
        object_key: str,
        dest_provider: str,
        dest_bucket: str
    ):
        """
        Copy object from one cloud to another
        """
        # Download from source
        if source_provider == 'aws':
            obj = self.s3_client.get_object(Bucket=source_bucket, Key=object_key)
            data = obj['Body'].read()

        elif source_provider == 'gcp':
            bucket = self.gcs_client.bucket(source_bucket)
            blob = bucket.blob(object_key)
            data = blob.download_as_bytes()

        # Upload to destination
        if dest_provider == 'aws':
            self.s3_client.put_object(
                Bucket=dest_bucket,
                Key=object_key,
                Body=data
            )

        elif dest_provider == 'gcp':
            bucket = self.gcs_client.bucket(dest_bucket)
            blob = bucket.blob(object_key)
            blob.upload_from_string(data)

        elif dest_provider == 'azure':
            blob_client = self.azure_client.get_blob_client(
                container=dest_bucket,
                blob=object_key
            )
            blob_client.upload_blob(data, overwrite=True)

# Example: Continuous replication with change detection
class ContinuousReplicator:
    """Implement continuous replication using event triggers"""

    def setup_event_based_replication(self):
        """
        Set up event-driven replication
        """
        # AWS S3 -> Lambda -> GCS
        lambda_function = """
        import boto3
        from google.cloud import storage

        def handler(event, context):
            # Parse S3 event
            s3_event = event['Records'][0]['s3']
            bucket = s3_event['bucket']['name']
            key = s3_event['object']['key']

            # Download from S3
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=bucket, Key=key)
            data = obj['Body'].read()

            # Upload to GCS
            gcs_client = storage.Client()
            gcs_bucket = gcs_client.bucket('backup-bucket')
            blob = gcs_bucket.blob(key)
            blob.upload_from_string(data)

            return {'status': 'replicated'}
        """

        # GCP Cloud Storage -> Cloud Function -> S3
        cloud_function = """
        from google.cloud import storage
        import boto3

        def replicate_to_s3(event, context):
            # Parse GCS event
            file = event
            bucket_name = file['bucket']
            file_name = file['name']

            # Download from GCS
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_name)
            data = blob.download_as_bytes()

            # Upload to S3
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket='backup-bucket',
                Key=file_name,
                Body=data
            )
        """

        return {
            'aws_lambda': lambda_function,
            'gcp_function': cloud_function
        }
```

---

## 3. Failover and Failback

### 3.1 Automated Failover System

```python
# Multi-Cloud Failover Orchestrator
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import time
import logging

class FailoverState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING_OVER = "failing_over"
    FAILED_OVER = "failed_over"
    FAILING_BACK = "failing_back"

@dataclass
class CloudEnvironment:
    """Represents a cloud environment"""
    name: str
    cloud_provider: str
    region: str
    endpoints: List[str]
    health_check_url: str
    is_primary: bool
    state: FailoverState = FailoverState.HEALTHY

class FailoverOrchestrator:
    """Orchestrate multi-cloud failover and failback"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.environments = {}
        self.current_primary = None
        self.failover_history = []

    def register_environment(self, env: CloudEnvironment):
        """Register a cloud environment"""
        self.environments[env.name] = env
        if env.is_primary:
            self.current_primary = env.name

    def monitor_health(self) -> Dict[str, bool]:
        """Monitor health of all environments"""
        health_status = {}

        for name, env in self.environments.items():
            is_healthy = self._check_environment_health(env)
            health_status[name] = is_healthy

            if not is_healthy and env.name == self.current_primary:
                self.logger.error(f"Primary environment {name} is unhealthy!")
                self._trigger_failover(env)

        return health_status

    def _check_environment_health(self, env: CloudEnvironment) -> bool:
        """
        Comprehensive health check for environment

        Checks:
        - Endpoint availability
        - Response time
        - Error rate
        - Resource availability
        """
        import requests

        try:
            # HTTP health check
            response = requests.get(
                env.health_check_url,
                timeout=5
            )

            if response.status_code != 200:
                self.logger.warning(f"{env.name} health check returned {response.status_code}")
                return False

            # Check response time
            if response.elapsed.total_seconds() > 2:
                self.logger.warning(f"{env.name} response time too high: {response.elapsed.total_seconds()}s")
                return False

            # Additional checks
            health_data = response.json()
            if health_data.get('database') != 'healthy':
                self.logger.warning(f"{env.name} database unhealthy")
                return False

            if health_data.get('cache') != 'healthy':
                self.logger.warning(f"{env.name} cache unhealthy")
                return False

            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Health check failed for {env.name}: {e}")
            return False

    def _trigger_failover(self, failed_env: CloudEnvironment):
        """
        Trigger automated failover to secondary environment
        """
        self.logger.critical(f"Triggering failover from {failed_env.name}")

        failed_env.state = FailoverState.FAILING_OVER

        # Select target environment
        target_env = self._select_failover_target(failed_env)

        if not target_env:
            self.logger.critical("No healthy failover target available!")
            return False

        self.logger.info(f"Failing over to {target_env.name}")

        # Execute failover steps
        try:
            # Step 1: Verify target environment is ready
            if not self._verify_target_ready(target_env):
                raise Exception("Target environment not ready")

            # Step 2: Promote database replica to primary (if applicable)
            self._promote_database(target_env)

            # Step 3: Update DNS/traffic routing
            self._update_traffic_routing(failed_env, target_env)

            # Step 4: Scale up target environment if needed
            self._scale_environment(target_env, scale_up=True)

            # Step 5: Verify traffic is flowing
            if not self._verify_traffic_flow(target_env):
                raise Exception("Traffic not flowing to target environment")

            # Update states
            failed_env.state = FailoverState.DEGRADED
            target_env.state = FailoverState.FAILED_OVER
            self.current_primary = target_env.name

            # Record failover
            self.failover_history.append({
                'timestamp': time.time(),
                'from': failed_env.name,
                'to': target_env.name,
                'reason': 'health_check_failure'
            })

            self.logger.info(f"Failover completed successfully to {target_env.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failover failed: {e}")
            failed_env.state = FailoverState.HEALTHY  # Rollback
            return False

    def _select_failover_target(self, failed_env: CloudEnvironment) -> CloudEnvironment:
        """Select best failover target"""
        candidates = [
            env for name, env in self.environments.items()
            if env.name != failed_env.name and
            env.state == FailoverState.HEALTHY
        ]

        if not candidates:
            return None

        # Prioritize by:
        # 1. Geographic proximity
        # 2. Capacity
        # 3. Cost
        return candidates[0]  # Simplified selection

    def _promote_database(self, target_env: CloudEnvironment):
        """Promote database replica to primary"""
        self.logger.info(f"Promoting database in {target_env.name} to primary")

        if target_env.cloud_provider == 'aws':
            # Promote RDS read replica
            import boto3
            rds = boto3.client('rds', region_name=target_env.region)

            rds.promote_read_replica(
                DBInstanceIdentifier='replica-instance-id'
            )

            # Wait for promotion
            waiter = rds.get_waiter('db_instance_available')
            waiter.wait(DBInstanceIdentifier='replica-instance-id')

        elif target_env.cloud_provider == 'gcp':
            # Promote Cloud SQL replica
            from google.cloud import sql_v1

            client = sql_v1.SqlInstancesServiceClient()

            # Stop replication
            # client.promote_replica(...)

    def _update_traffic_routing(
        self,
        source_env: CloudEnvironment,
        target_env: CloudEnvironment
    ):
        """Update global traffic routing"""
        self.logger.info(
            f"Updating traffic routing from {source_env.name} to {target_env.name}"
        )

        # Update Route53 weighted routing
        if source_env.cloud_provider == 'aws':
            import boto3
            route53 = boto3.client('route53')

            # Update health check
            route53.change_resource_record_sets(
                HostedZoneId='Z1234567890ABC',
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': 'api.example.com',
                                'Type': 'A',
                                'SetIdentifier': target_env.name,
                                'Weight': 100,  # All traffic to target
                                'TTL': 60,
                                'ResourceRecords': [
                                    {'Value': target_env.endpoints[0]}
                                ]
                            }
                        },
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': 'api.example.com',
                                'Type': 'A',
                                'SetIdentifier': source_env.name,
                                'Weight': 0,  # No traffic to source
                                'TTL': 60,
                                'ResourceRecords': [
                                    {'Value': source_env.endpoints[0]}
                                ]
                            }
                        }
                    ]
                }
            )

        # Update Cloud DNS (GCP)
        # Update Azure Traffic Manager
        # etc.

    def _scale_environment(self, env: CloudEnvironment, scale_up: bool = True):
        """Scale environment capacity"""
        if scale_up:
            self.logger.info(f"Scaling up {env.name}")
            # Increase instance counts, adjust auto-scaling, etc.
        else:
            self.logger.info(f"Scaling down {env.name}")
            # Decrease instance counts

    def _verify_traffic_flow(self, env: CloudEnvironment) -> bool:
        """Verify traffic is flowing to environment"""
        # Check metrics to verify traffic
        # Check application logs
        # Verify requests are being processed
        return True

    def initiate_failback(self, original_primary: str):
        """
        Initiate failback to original primary environment
        """
        self.logger.info(f"Initiating failback to {original_primary}")

        original_env = self.environments[original_primary]
        current_env = self.environments[self.current_primary]

        # Verify original environment is healthy
        if not self._check_environment_health(original_env):
            self.logger.error("Original environment not healthy, cannot failback")
            return False

        original_env.state = FailoverState.FAILING_BACK

        try:
            # Step 1: Resync data from current primary to original
            self._resync_data(current_env, original_env)

            # Step 2: Gradually shift traffic back
            self._gradual_traffic_shift(current_env, original_env)

            # Step 3: Verify original environment handling traffic
            if not self._verify_traffic_flow(original_env):
                raise Exception("Original environment not handling traffic properly")

            # Step 4: Complete failback
            original_env.state = FailoverState.HEALTHY
            original_env.is_primary = True
            current_env.is_primary = False
            self.current_primary = original_primary

            self.logger.info(f"Failback completed to {original_primary}")
            return True

        except Exception as e:
            self.logger.error(f"Failback failed: {e}")
            original_env.state = FailoverState.DEGRADED
            return False

    def _resync_data(self, source_env: CloudEnvironment, target_env: CloudEnvironment):
        """Resynchronize data before failback"""
        self.logger.info(f"Resyncing data from {source_env.name} to {target_env.name}")

        # Take snapshot of current primary database
        # Restore snapshot to original primary
        # Catch up with replication
        # Verify data consistency

    def _gradual_traffic_shift(
        self,
        source_env: CloudEnvironment,
        target_env: CloudEnvironment
    ):
        """Gradually shift traffic from source to target"""
        shift_steps = [
            (10, 90),   # 10% to target, 90% to source
            (25, 75),
            (50, 50),
            (75, 25),
            (100, 0)    # 100% to target
        ]

        for target_weight, source_weight in shift_steps:
            self.logger.info(
                f"Shifting traffic: {target_weight}% to {target_env.name}, "
                f"{source_weight}% to {source_env.name}"
            )

            # Update DNS weights
            self._update_weighted_routing(
                target_env, target_weight,
                source_env, source_weight
            )

            # Wait and monitor
            time.sleep(300)  # 5 minutes between shifts

            # Verify no errors
            if not self._check_environment_health(target_env):
                self.logger.error("Target environment degraded, stopping shift")
                return False

        return True

    def _update_weighted_routing(
        self,
        env1: CloudEnvironment,
        weight1: int,
        env2: CloudEnvironment,
        weight2: int
    ):
        """Update weighted DNS routing"""
        # Implementation similar to _update_traffic_routing
        pass

# Example usage
orchestrator = FailoverOrchestrator()

# Register environments
primary_aws = CloudEnvironment(
    name='aws-us-east-1',
    cloud_provider='aws',
    region='us-east-1',
    endpoints=['10.0.1.100'],
    health_check_url='https://api-aws.example.com/health',
    is_primary=True
)

secondary_gcp = CloudEnvironment(
    name='gcp-us-central1',
    cloud_provider='gcp',
    region='us-central1',
    endpoints=['10.1.1.100'],
    health_check_url='https://api-gcp.example.com/health',
    is_primary=False
)

orchestrator.register_environment(primary_aws)
orchestrator.register_environment(secondary_gcp)

# Monitor continuously
while True:
    health = orchestrator.monitor_health()
    time.sleep(30)  # Check every 30 seconds
```

---

## 4. DR Testing and Validation

### 4.1 DR Test Framework

```python
# DR Test Framework
class DRTestFramework:
    """Framework for testing disaster recovery procedures"""

    def __init__(self, orchestrator: FailoverOrchestrator):
        self.orchestrator = orchestrator
        self.test_results = []
        self.logger = logging.getLogger(__name__)

    def run_dr_drill(self, drill_type: str):
        """
        Execute disaster recovery drill

        Drill Types:
        - tabletop: Discussion-based walkthrough
        - simulated: Controlled failover test
        - full: Complete failover with real traffic
        """
        self.logger.info(f"Starting DR drill: {drill_type}")

        test_plan = self._get_test_plan(drill_type)

        results = {
            'drill_type': drill_type,
            'start_time': time.time(),
            'steps': [],
            'success': True
        }

        for step in test_plan:
            self.logger.info(f"Executing step: {step['name']}")

            step_result = self._execute_test_step(step)
            results['steps'].append(step_result)

            if not step_result['success']:
                results['success'] = False
                if step.get('critical', True):
                    self.logger.error(f"Critical step failed: {step['name']}")
                    break

        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']

        self.test_results.append(results)
        self._generate_report(results)

        return results

    def _get_test_plan(self, drill_type: str) -> List[Dict]:
        """Get test plan for drill type"""
        plans = {
            'simulated': [
                {
                    'name': 'Verify baseline health',
                    'action': 'check_health',
                    'critical': True
                },
                {
                    'name': 'Take pre-failover snapshot',
                    'action': 'snapshot',
                    'critical': True
                },
                {
                    'name': 'Initiate controlled failover',
                    'action': 'failover',
                    'critical': True
                },
                {
                    'name': 'Verify secondary is serving traffic',
                    'action': 'verify_traffic',
                    'critical': True
                },
                {
                    'name': 'Run integration tests',
                    'action': 'integration_tests',
                    'critical': True
                },
                {
                    'name': 'Verify data consistency',
                    'action': 'verify_data',
                    'critical': True
                },
                {
                    'name': 'Measure RTO',
                    'action': 'measure_rto',
                    'critical': False
                },
                {
                    'name': 'Measure RPO',
                    'action': 'measure_rpo',
                    'critical': False
                },
                {
                    'name': 'Initiate failback',
                    'action': 'failback',
                    'critical': True
                },
                {
                    'name': 'Verify primary restored',
                    'action': 'verify_restored',
                    'critical': True
                }
            ]
        }

        return plans.get(drill_type, [])

    def _execute_test_step(self, step: Dict) -> Dict:
        """Execute individual test step"""
        start_time = time.time()

        try:
            if step['action'] == 'check_health':
                health = self.orchestrator.monitor_health()
                success = all(health.values())

            elif step['action'] == 'snapshot':
                # Take snapshots of all critical systems
                success = True

            elif step['action'] == 'failover':
                # Trigger failover
                primary_env = self.orchestrator.environments[
                    self.orchestrator.current_primary
                ]
                success = self.orchestrator._trigger_failover(primary_env)

            elif step['action'] == 'verify_traffic':
                # Verify traffic flowing to new primary
                current_primary = self.orchestrator.environments[
                    self.orchestrator.current_primary
                ]
                success = self.orchestrator._verify_traffic_flow(current_primary)

            elif step['action'] == 'integration_tests':
                # Run integration test suite
                success = self._run_integration_tests()

            elif step['action'] == 'verify_data':
                # Verify data consistency
                success = self._verify_data_consistency()

            elif step['action'] == 'measure_rto':
                # Calculate actual RTO
                rto = end_time - start_time
                success = True

            elif step['action'] == 'measure_rpo':
                # Calculate actual RPO
                rpo = self._calculate_rpo()
                success = True

            elif step['action'] == 'failback':
                # Initiate failback
                success = self.orchestrator.initiate_failback('original-primary')

            elif step['action'] == 'verify_restored':
                # Verify primary is restored and healthy
                success = True

            else:
                success = False

            end_time = time.time()

            return {
                'name': step['name'],
                'action': step['action'],
                'success': success,
                'duration': end_time - start_time,
                'timestamp': start_time
            }

        except Exception as e:
            self.logger.error(f"Step failed: {step['name']} - {e}")
            return {
                'name': step['name'],
                'action': step['action'],
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time,
                'timestamp': start_time
            }

    def _run_integration_tests(self) -> bool:
        """Run integration test suite"""
        # Execute comprehensive integration tests
        return True

    def _verify_data_consistency(self) -> bool:
        """Verify data consistency across environments"""
        # Compare checksums, row counts, etc.
        return True

    def _calculate_rpo(self) -> float:
        """Calculate actual RPO achieved"""
        # Compare timestamps of last replicated transaction
        return 60.0  # seconds

    def _generate_report(self, results: Dict):
        """Generate DR drill report"""
        report = f"""
        Disaster Recovery Drill Report
        ================================

        Drill Type: {results['drill_type']}
        Start Time: {time.ctime(results['start_time'])}
        End Time: {time.ctime(results['end_time'])}
        Duration: {results['duration']:.2f} seconds
        Overall Success: {results['success']}

        Steps Executed:
        """

        for step in results['steps']:
            status = '✓' if step['success'] else '✗'
            report += f"\n{status} {step['name']} ({step['duration']:.2f}s)"
            if not step['success'] and 'error' in step:
                report += f"\n  Error: {step['error']}"

        report += f"\n\nRecommendations:\n"

        # Generate recommendations based on results
        if results['duration'] > 300:  # 5 minutes
            report += "- Consider optimizing failover procedure to reduce RTO\n"

        if any(not step['success'] for step in results['steps']):
            report += "- Address failed steps before next production failover\n"

        report += "- Schedule regular DR drills (monthly recommended)\n"
        report += "- Update runbooks based on learnings\n"

        self.logger.info(report)
        return report

# Example usage
test_framework = DRTestFramework(orchestrator)
results = test_framework.run_dr_drill('simulated')
```

---

## 5. DR Documentation and Runbooks

### 5.1 DR Runbook Template

```yaml
# Disaster Recovery Runbook
disaster_recovery_runbook:
  document_info:
    title: "Multi-Cloud DR Runbook - Production ML Platform"
    version: "2.0"
    last_updated: "2024-01-15"
    owner: "Platform Engineering Team"
    reviewers:
      - "CTO"
      - "VP Engineering"
      - "Security Team Lead"

  emergency_contacts:
    - name: "On-Call Engineer"
      phone: "+1-555-0100"
      email: "oncall@company.com"
      escalation_level: 1

    - name: "Engineering Manager"
      phone: "+1-555-0101"
      email: "eng-manager@company.com"
      escalation_level: 2

    - name: "CTO"
      phone: "+1-555-0102"
      email: "cto@company.com"
      escalation_level: 3

  disaster_scenarios:
    - scenario: "Primary Region Outage"
      severity: "Critical"
      rto: "1 hour"
      rpo: "15 minutes"
      trigger_conditions:
        - "Primary region health checks failing for 5+ minutes"
        - "Multiple service failures in primary region"
        - "Cloud provider status page shows region-wide outage"

      response_procedure:
        - step: 1
          action: "Assess situation"
          details: "Verify scope of outage, check cloud provider status"
          owner: "On-call engineer"
          estimated_duration: "5 minutes"

        - step: 2
          action: "Notify stakeholders"
          details: "Alert engineering team, management, and customers"
          owner: "On-call engineer"
          estimated_duration: "2 minutes"

        - step: 3
          action: "Initiate failover"
          details: "Execute automated failover to secondary region"
          commands:
            - "python dr_orchestrator.py failover --target gcp-us-central1"
          owner: "On-call engineer"
          estimated_duration: "10 minutes"

        - step: 4
          action: "Verify failover"
          details: "Confirm secondary region is serving traffic"
          checks:
            - "Health checks passing"
            - "Application responding"
            - "Database accessible"
          owner: "On-call engineer"
          estimated_duration: "5 minutes"

        - step: 5
          action: "Monitor and adjust"
          details: "Monitor for issues, scale resources as needed"
          owner: "On-call engineer"
          estimated_duration: "Ongoing"

      rollback_procedure:
        - "Verify primary region is restored"
        - "Execute failback: python dr_orchestrator.py failback --target aws-us-east-1"
        - "Monitor traffic distribution"
        - "Complete failback once stable"

      post_incident:
        - "Document incident timeline"
        - "Conduct post-mortem"
        - "Update runbook with learnings"
        - "Schedule DR drill to validate changes"

  communication_plan:
    internal:
      - "Slack: #incident-response"
      - "Email: engineering@company.com"
      - "Conference bridge: +1-555-0199"

    external:
      - "Status page: status.company.com"
      - "Twitter: @company_status"
      - "Email: support@company.com"

    templates:
      initial_notification: |
        We are currently experiencing issues with our primary infrastructure.
        Our team is investigating and will provide updates every 30 minutes.

      update_notification: |
        UPDATE: We have failed over to our secondary region and services are
        being restored. Current status: [details]

      resolution_notification: |
        RESOLVED: All services have been restored. We will be conducting a
        full investigation and will publish a post-mortem within 48 hours.

  tools_and_access:
    - tool: "DR Orchestrator"
      location: "https://github.com/company/dr-orchestrator"
      access: "Engineering team"
      documentation: "https://docs.company.com/dr"

    - tool: "Monitoring Dashboard"
      location: "https://grafana.company.com/dr-dashboard"
      access: "Engineering team"
      credentials: "Stored in 1Password"

    - tool: "Cloud Consoles"
      aws: "https://console.aws.amazon.com"
      gcp: "https://console.cloud.google.com"
      azure: "https://portal.azure.com"

  testing_schedule:
    frequency: "Monthly"
    next_test: "2024-02-15"
    test_types:
      - "Tabletop exercise (monthly)"
      - "Simulated failover (quarterly)"
      - "Full production failover (annually)"
```

---

## 6. Summary

Multi-cloud disaster recovery requires:
- Clear RTO/RPO objectives
- Robust data replication strategies
- Automated failover mechanisms
- Regular testing and validation
- Comprehensive documentation
- Well-defined communication plans

## Key Takeaways

1. **Define clear objectives** (RTO/RPO) for each service tier
2. **Automate failover** to meet aggressive RTO requirements
3. **Replicate data continuously** across regions and clouds
4. **Test regularly** - untested DR plans fail in real disasters
5. **Document everything** - chaos is not the time to figure things out
6. **Practice communication** - stakeholders need timely updates
7. **Learn from tests** - update runbooks after every drill
8. **Balance cost and resilience** - not everything needs active-active

## Additional Resources

- AWS Disaster Recovery Whitepaper
- GCP Disaster Recovery Planning Guide
- Azure Site Recovery Documentation
- Disaster Recovery Journal
- DR Planning Best Practices

## Next Steps

1. Define RTO/RPO for all services
2. Design multi-cloud DR architecture
3. Implement data replication
4. Build automated failover system
5. Create detailed runbooks
6. Schedule regular DR drills
7. Establish communication protocols
