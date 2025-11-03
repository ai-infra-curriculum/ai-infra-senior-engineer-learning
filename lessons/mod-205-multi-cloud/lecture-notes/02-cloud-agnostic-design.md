# Lecture 02: Cloud-Agnostic Design Patterns for ML Infrastructure

## Learning Objectives

By the end of this lecture, you will be able to:

- Design cloud-agnostic ML infrastructure using Kubernetes as abstraction layer across AWS EKS, Google GKE, and Azure AKS achieving 70% portability with 30% cloud-native optimization
- Implement service mesh architectures (Istio, Linkerd) for cross-cloud connectivity enabling secure, encrypted communication between workloads across multiple cloud providers
- Architect storage abstraction patterns using CSI drivers, S3-compatible interfaces, and data replication strategies to achieve unified data access across clouds
- Configure multi-cloud networking with VPN/VPC peering, transit gateways, and private connectivity (AWS PrivateLink, GCP Private Service Connect, Azure Private Link)
- Implement federated identity and access management using OIDC, SAML, and cloud-agnostic IAM patterns to provide consistent authentication across providers
- Design container registry strategies including multi-cloud replication, image signing/scanning, and artifact management for consistent deployments
- Apply configuration management patterns using GitOps, Helm, and cloud-agnostic secrets management (HashiCorp Vault, External Secrets Operator) for portable configurations
- Build unified observability systems using OpenTelemetry, Prometheus, and vendor-agnostic monitoring that aggregate metrics, logs, and traces across multiple clouds

## Table of Contents
1. [Introduction](#introduction)
2. [Kubernetes as the Abstraction Layer](#kubernetes-abstraction)
3. [Service Mesh for Cross-Cloud Connectivity](#service-mesh)
4. [Storage Abstraction Patterns](#storage-abstraction)
5. [Network Architecture for Multi-Cloud](#network-architecture)
6. [Identity and Access Management](#iam)
7. [Container Registry Management](#container-registry)
8. [Configuration Management](#configuration-management)
9. [Observability and Monitoring](#observability)
10. [Summary](#summary)

## Introduction {#introduction}

Cloud-agnostic design is the practice of building applications and infrastructure that can run on any cloud provider with minimal modification. For AI/ML workloads, this approach provides flexibility, reduces vendor lock-in, and enables true multi-cloud strategies.

### Why Cloud-Agnostic Design Matters

**Benefits**:
- **Portability**: Move workloads between clouds based on cost, performance, or requirements
- **Vendor Independence**: Avoid dependency on proprietary services
- **Negotiation Power**: Leverage competition between providers
- **Risk Mitigation**: Not locked into single provider's technology roadmap
- **Skills Transfer**: Team knowledge applies across clouds

**Trade-offs**:
- **Cannot use managed services**: Miss out on cloud-native features (SageMaker, Vertex AI)
- **Higher operational overhead**: Must manage more infrastructure yourself
- **Potential performance cost**: Abstraction layers can add latency
- **Development complexity**: Additional abstraction code to maintain

### The Cloud-Agnostic Spectrum

```
Fully Cloud-Native ←─────────────────→ Fully Cloud-Agnostic
        ↑                                        ↑
   Maximum features                      Maximum portability
   Minimum portability                   Minimum features
   Lower ops burden                      Higher ops burden
```

**Optimal Position for ML Infrastructure**: 70% cloud-agnostic, 30% cloud-native
- Core ML platform: Cloud-agnostic (Kubernetes, open-source tools)
- Specialized features: Cloud-native when significant value (TPUs, managed AutoML)

## Kubernetes as the Abstraction Layer {#kubernetes-abstraction}

Kubernetes provides a consistent API across AWS EKS, Google GKE, and Azure AKS, making it the foundation for cloud-agnostic ML infrastructure.

### Kubernetes for ML Workloads

**Key Benefits**:
1. **Consistent API**: Same kubectl commands work on EKS, GKE, AKS
2. **Resource Management**: Unified approach to CPU, memory, GPU allocation
3. **Service Discovery**: Internal DNS and service routing
4. **Scaling**: Horizontal Pod Autoscaler works identically
5. **CI/CD**: Same deployment pipelines across clouds

### Standard ML Deployment on Kubernetes

```yaml
# This deployment works identically on EKS, GKE, and AKS
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference-service
  namespace: ml-platform
  labels:
    app: ml-inference
    tier: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
        version: v1.2.3
    spec:
      # Node selector works across clouds with consistent labeling
      nodeSelector:
        workload-type: ml-inference
        gpu-type: nvidia-t4

      # Affinity rules for high availability
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - ml-inference
            topologyKey: kubernetes.io/hostname

      containers:
      - name: inference-server
        image: ml-inference:v1.2.3
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        - name: metrics
          containerPort: 9090
          protocol: TCP

        # Environment configuration using ConfigMaps and Secrets
        env:
        - name: MODEL_STORAGE_BACKEND
          valueFrom:
            configMapKeyRef:
              name: ml-config
              key: storage_backend
        - name: MODEL_STORAGE_BUCKET
          valueFrom:
            configMapKeyRef:
              name: ml-config
              key: storage_bucket
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: ml-secrets
              key: api_key

        # Resource requests and limits
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"

        # Liveness and readiness probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # Volume mounts for model caching
        volumeMounts:
        - name: model-cache
          mountPath: /models
        - name: tmp
          mountPath: /tmp

      # Volumes - using emptyDir for local caching
      volumes:
      - name: model-cache
        emptyDir:
          sizeLimit: 20Gi
      - name: tmp
        emptyDir: {}

      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
  namespace: ml-platform
  labels:
    app: ml-inference
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 9090
    protocol: TCP
  selector:
    app: ml-inference

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-inference-hpa
  namespace: ml-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference-service
  minReplicas: 3
  maxReplicas: 20
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
  # Custom metrics for ML-specific scaling
  - type: Pods
    pods:
      metric:
        name: inference_queue_length
      target:
        type: AverageValue
        averageValue: "10"
```

### Cloud-Agnostic Storage Classes

```yaml
# Storage classes with consistent naming across clouds
---
# AWS EKS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# GCP GKE
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# Azure AKS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: disk.csi.azure.com
parameters:
  storageaccounttype: Premium_LRS
  kind: Managed
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

### Kubernetes Operators for ML Workloads

```python
# Example: Cloud-agnostic ML training operator
"""
Kubernetes operator for managing ML training jobs
Works identically on EKS, GKE, and AKS

TODO: Implement full operator using kopf or operator-sdk
"""

import kopf
import kubernetes
from typing import Dict, Any

@kopf.on.create('ml.example.com', 'v1', 'trainingjobs')
def create_training_job(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """
    Handle creation of ML training job

    Args:
        spec: TrainingJob specification
        name: Job name
        namespace: Kubernetes namespace

    TODO: Implement job creation logic
    """
    # Extract training specifications
    model_type = spec.get('modelType')
    dataset_uri = spec.get('datasetUri')
    hyperparameters = spec.get('hyperparameters', {})
    resources = spec.get('resources', {})

    # TODO: Create Kubernetes Job for training
    # TODO: Set up storage for checkpoints
    # TODO: Configure logging and monitoring
    # TODO: Handle distributed training if needed

    job_manifest = {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {
            'name': f'{name}-training',
            'namespace': namespace,
            'labels': {
                'app': 'ml-training',
                'training-job': name
            }
        },
        'spec': {
            'backoffLimit': 3,
            'template': {
                'spec': {
                    'restartPolicy': 'OnFailure',
                    'containers': [{
                        'name': 'trainer',
                        'image': f'ml-trainer:{model_type}',
                        'env': [
                            {'name': 'DATASET_URI', 'value': dataset_uri},
                            {'name': 'MODEL_TYPE', 'value': model_type}
                        ],
                        'resources': resources
                    }]
                }
            }
        }
    }

    # TODO: Create job using Kubernetes API
    api = kubernetes.client.BatchV1Api()
    # api.create_namespaced_job(namespace, job_manifest)

    return {'status': 'created', 'jobName': f'{name}-training'}

@kopf.on.update('ml.example.com', 'v1', 'trainingjobs')
def update_training_job(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """
    Handle updates to ML training job
    TODO: Implement update logic
    """
    pass

@kopf.on.delete('ml.example.com', 'v1', 'trainingjobs')
def delete_training_job(spec: Dict[str, Any], name: str, namespace: str, **kwargs):
    """
    Handle deletion of ML training job
    TODO: Implement cleanup logic
    """
    pass
```

### Custom Resource Definition (CRD) for ML Jobs

```yaml
# TrainingJob CRD - works across all Kubernetes clusters
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: trainingjobs.ml.example.com
spec:
  group: ml.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              modelType:
                type: string
                description: Type of model to train
              framework:
                type: string
                enum: ["pytorch", "tensorflow", "jax"]
              datasetUri:
                type: string
                description: URI to training dataset
              outputUri:
                type: string
                description: URI for model artifacts
              hyperparameters:
                type: object
                description: Model hyperparameters
                additionalProperties:
                  type: string
              resources:
                type: object
                properties:
                  gpus:
                    type: integer
                    minimum: 0
                  memory:
                    type: string
                  cpu:
                    type: string
              distributedTraining:
                type: object
                properties:
                  enabled:
                    type: boolean
                  workers:
                    type: integer
                    minimum: 1
                  strategy:
                    type: string
                    enum: ["horovod", "pytorch-ddp", "tf-mirrored"]
          status:
            type: object
            properties:
              phase:
                type: string
                enum: ["Pending", "Running", "Succeeded", "Failed"]
              startTime:
                type: string
                format: date-time
              completionTime:
                type: string
                format: date-time
              metrics:
                type: object
                additionalProperties:
                  type: number
    additionalPrinterColumns:
    - name: Status
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
  scope: Namespaced
  names:
    plural: trainingjobs
    singular: trainingjob
    kind: TrainingJob
    shortNames:
    - tj
```

## Service Mesh for Cross-Cloud Connectivity {#service-mesh}

Service meshes provide secure, observable, and reliable service-to-service communication across clouds.

### Istio for Multi-Cloud ML Infrastructure

**Benefits**:
- **Unified traffic management**: Route between clouds transparently
- **Security**: mTLS between all services
- **Observability**: Distributed tracing across clouds
- **Resilience**: Circuit breakers, retries, timeouts

### Istio Configuration for Multi-Cloud

```yaml
# Istio VirtualService for multi-cloud routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ml-inference-multicloud
  namespace: ml-platform
spec:
  hosts:
  - ml-inference.example.com
  gateways:
  - ml-gateway
  http:
  - match:
    - headers:
        x-region:
          exact: us-east
    route:
    - destination:
        host: ml-inference-aws.ml-platform.svc.cluster.local
        port:
          number: 80
      weight: 100

  - match:
    - headers:
        x-region:
          exact: us-central
    route:
    - destination:
        host: ml-inference-gcp.ml-platform.svc.cluster.local
        port:
          number: 80
      weight: 100

  # Default routing with traffic split
  - route:
    - destination:
        host: ml-inference-aws.ml-platform.svc.cluster.local
        port:
          number: 80
      weight: 60
    - destination:
        host: ml-inference-gcp.ml-platform.svc.cluster.local
        port:
          number: 80
      weight: 40

    # Retry policy
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream

    # Timeout
    timeout: 10s

---
# DestinationRule for circuit breaking
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ml-inference-circuit-breaker
  namespace: ml-platform
spec:
  host: ml-inference-aws.ml-platform.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

### Cross-Cloud Service Mesh Federation

```yaml
# ServiceEntry for external GCP cluster
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: ml-inference-gcp-external
  namespace: ml-platform
spec:
  hosts:
  - ml-inference-gcp.example.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS

---
# Gateway for cross-cloud ingress
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: cross-cloud-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: MUTUAL
      serverCertificate: /etc/certs/server-cert.pem
      privateKey: /etc/certs/server-key.pem
      caCertificates: /etc/certs/ca-cert.pem
    hosts:
    - "*.ml-platform.example.com"
```

## Storage Abstraction Patterns {#storage-abstraction}

### Object Storage Abstraction

```python
# Cloud-agnostic object storage interface
from abc import ABC, abstractmethod
from typing import BinaryIO, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ObjectMetadata:
    """Metadata for stored object"""
    key: str
    size: int
    last_modified: datetime
    content_type: str
    etag: str
    custom_metadata: Dict[str, str]

class ObjectStorageInterface(ABC):
    """
    Abstract interface for object storage operations
    Implementations: S3Storage, GCSStorage, AzureBlobStorage

    TODO: Implement concrete classes for each provider
    """

    @abstractmethod
    def upload_object(
        self,
        key: str,
        data: BinaryIO,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload object to storage

        Args:
            key: Object key/path
            data: Binary data stream
            metadata: Optional custom metadata

        Returns:
            str: Object URI or identifier

        TODO: Implement with multipart upload for large files
        TODO: Add progress callback
        TODO: Implement retry logic
        """
        pass

    @abstractmethod
    def download_object(self, key: str, destination: BinaryIO) -> int:
        """
        Download object from storage

        Args:
            key: Object key/path
            destination: Destination stream

        Returns:
            int: Number of bytes downloaded

        TODO: Implement with range requests for large files
        TODO: Add progress callback
        TODO: Implement retry logic
        """
        pass

    @abstractmethod
    def delete_object(self, key: str) -> bool:
        """
        Delete object from storage

        Args:
            key: Object key/path

        Returns:
            bool: True if deleted successfully

        TODO: Implement with confirmation
        """
        pass

    @abstractmethod
    def list_objects(
        self,
        prefix: str = "",
        max_results: int = 1000
    ) -> List[ObjectMetadata]:
        """
        List objects with optional prefix filter

        Args:
            prefix: Key prefix filter
            max_results: Maximum number of results

        Returns:
            List of object metadata

        TODO: Implement pagination
        TODO: Add filtering options
        """
        pass

    @abstractmethod
    def get_object_metadata(self, key: str) -> ObjectMetadata:
        """
        Get metadata for object without downloading

        Args:
            key: Object key/path

        Returns:
            ObjectMetadata: Object metadata

        TODO: Implement efficient HEAD request
        """
        pass

    @abstractmethod
    def copy_object(self, source_key: str, dest_key: str) -> str:
        """
        Copy object within storage

        Args:
            source_key: Source object key
            dest_key: Destination object key

        Returns:
            str: Destination object URI

        TODO: Implement server-side copy when possible
        """
        pass

    @abstractmethod
    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """
        Generate presigned URL for temporary access

        Args:
            key: Object key/path
            expiration: URL expiration in seconds
            method: HTTP method (GET, PUT, etc.)

        Returns:
            str: Presigned URL

        TODO: Implement with appropriate cloud-specific logic
        """
        pass

class S3Storage(ObjectStorageInterface):
    """
    AWS S3 implementation of object storage interface

    TODO: Implement using boto3
    """

    def __init__(self, bucket: str, region: str = "us-east-1"):
        self.bucket = bucket
        self.region = region
        # TODO: Initialize boto3 client with proper credentials

    def upload_object(self, key: str, data: BinaryIO, metadata: Optional[Dict[str, str]] = None) -> str:
        # TODO: Implement S3 upload
        # TODO: Use multipart upload for files > 5GB
        # TODO: Handle exceptions and retries
        pass

    # TODO: Implement other methods

class GCSStorage(ObjectStorageInterface):
    """
    Google Cloud Storage implementation

    TODO: Implement using google-cloud-storage
    """

    def __init__(self, bucket: str, project: str):
        self.bucket = bucket
        self.project = project
        # TODO: Initialize GCS client

    def upload_object(self, key: str, data: BinaryIO, metadata: Optional[Dict[str, str]] = None) -> str:
        # TODO: Implement GCS upload
        # TODO: Use resumable uploads for large files
        pass

    # TODO: Implement other methods

class AzureBlobStorage(ObjectStorageInterface):
    """
    Azure Blob Storage implementation

    TODO: Implement using azure-storage-blob
    """

    def __init__(self, container: str, account: str):
        self.container = container
        self.account = account
        # TODO: Initialize Azure Blob client

    def upload_object(self, key: str, data: BinaryIO, metadata: Optional[Dict[str, str]] = None) -> str:
        # TODO: Implement Azure Blob upload
        # TODO: Use block blobs for large files
        pass

    # TODO: Implement other methods

# Factory function
def get_object_storage(
    provider: str,
    **kwargs
) -> ObjectStorageInterface:
    """
    Factory function to create appropriate storage backend

    Args:
        provider: 'aws', 'gcp', or 'azure'
        **kwargs: Provider-specific configuration

    Returns:
        ObjectStorageInterface: Configured storage backend

    Example:
        storage = get_object_storage('aws', bucket='my-bucket', region='us-west-2')
        storage.upload_object('model.pkl', model_data)
    """
    providers = {
        'aws': S3Storage,
        'gcp': GCSStorage,
        'azure': AzureBlobStorage
    }

    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}")

    return providers[provider](**kwargs)
```

### Model Artifact Storage with Versioning

```python
# Cloud-agnostic model registry
class ModelRegistry:
    """
    Cloud-agnostic model artifact registry

    TODO: Implement full model lifecycle management
    """

    def __init__(self, storage: ObjectStorageInterface, prefix: str = "models/"):
        self.storage = storage
        self.prefix = prefix

    def register_model(
        self,
        model_name: str,
        version: str,
        model_path: str,
        metadata: Dict[str, any]
    ) -> str:
        """
        Register a new model version

        Args:
            model_name: Name of the model
            version: Semantic version string
            model_path: Local path to model artifacts
            metadata: Model metadata (framework, metrics, etc.)

        Returns:
            str: Model URI

        TODO: Implement artifact upload
        TODO: Store metadata separately
        TODO: Update model registry index
        """
        key = f"{self.prefix}{model_name}/{version}/model.tar.gz"

        # TODO: Package model artifacts
        # TODO: Upload to storage
        # TODO: Store metadata
        # TODO: Update registry index

        return f"model://{model_name}/{version}"

    def get_model(
        self,
        model_name: str,
        version: str = "latest",
        destination: str = "/tmp/models"
    ) -> str:
        """
        Download model artifacts

        Args:
            model_name: Name of the model
            version: Version to download ('latest' for most recent)
            destination: Local destination path

        Returns:
            str: Local path to model artifacts

        TODO: Implement download logic
        TODO: Handle 'latest' version resolution
        TODO: Extract artifacts
        """
        if version == "latest":
            # TODO: Resolve latest version from registry
            pass

        key = f"{self.prefix}{model_name}/{version}/model.tar.gz"

        # TODO: Download and extract
        pass

    def list_models(self) -> List[Dict[str, any]]:
        """
        List all registered models

        Returns:
            List of model information

        TODO: Implement listing from registry index
        """
        pass

    def list_versions(self, model_name: str) -> List[str]:
        """
        List versions of a specific model

        Args:
            model_name: Name of the model

        Returns:
            List of version strings

        TODO: Implement version listing
        """
        pass

    def delete_version(self, model_name: str, version: str) -> bool:
        """
        Delete a specific model version

        Args:
            model_name: Name of the model
            version: Version to delete

        Returns:
            bool: Success status

        TODO: Implement with safeguards
        TODO: Check if version is in use
        """
        pass
```

## Network Architecture for Multi-Cloud {#network-architecture}

### VPN and Interconnect Options

**AWS-GCP Connectivity**:
- AWS Direct Connect + Google Cloud Interconnect
- VPN tunnels over internet
- SD-WAN solutions (Aviatrix, Alkira)

**Latency Considerations**:
```
Same Region, Same AZ: < 1ms
Same Region, Different AZ: 1-3ms
Same Cloud, Different Region: 30-100ms
Cross-Cloud, Same Geographic Region: 2-10ms
Cross-Cloud, Different Continent: 100-300ms
```

### Multi-Cloud Network Architecture

```yaml
# Terraform example for multi-cloud networking
# TODO: Implement complete multi-cloud VPC setup

# AWS VPC
resource "aws_vpc" "ml_platform" {
  cidr_block = "10.1.0.0/16"

  tags = {
    Name = "ml-platform-aws"
    Cloud = "aws"
  }
}

# GCP VPC
resource "google_compute_network" "ml_platform" {
  name = "ml-platform-gcp"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "ml_platform" {
  name          = "ml-platform-subnet"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.ml_platform.id
}

# Azure VNet
resource "azurerm_virtual_network" "ml_platform" {
  name                = "ml-platform-azure"
  address_space       = ["10.3.0.0/16"]
  location            = "East US"
  resource_group_name = azurerm_resource_group.ml_platform.name
}

# Cross-cloud VPN connections
# TODO: Implement VPN gateways and tunnels
# TODO: Configure routing between clouds
# TODO: Set up BGP for dynamic routing
```

### DNS Strategy for Multi-Cloud

```python
# Multi-cloud DNS management
class MultiCloudDNS:
    """
    Manage DNS across multiple clouds

    TODO: Implement DNS zone management
    TODO: Add health-check based routing
    """

    def __init__(self):
        self.zones = {
            'aws': 'Z1234567890ABC',  # Route53 zone ID
            'gcp': 'example-com-gcp',  # Cloud DNS zone name
            'azure': 'example.com'     # Azure DNS zone name
        }

    def create_dns_record(
        self,
        hostname: str,
        record_type: str,
        values: List[str],
        ttl: int = 300
    ):
        """
        Create DNS record in all clouds

        Args:
            hostname: DNS hostname
            record_type: A, AAAA, CNAME, etc.
            values: List of record values
            ttl: Time to live

        TODO: Implement for each DNS provider
        """
        pass

    def create_weighted_record(
        self,
        hostname: str,
        endpoints: List[Dict[str, any]]
    ):
        """
        Create weighted routing record

        Args:
            hostname: DNS hostname
            endpoints: List of endpoints with weights

        Example:
            endpoints = [
                {'cloud': 'aws', 'ip': '1.2.3.4', 'weight': 60},
                {'cloud': 'gcp', 'ip': '5.6.7.8', 'weight': 40}
            ]

        TODO: Implement weighted routing
        """
        pass

    def create_geolocation_record(
        self,
        hostname: str,
        endpoints: Dict[str, str]
    ):
        """
        Create geolocation-based routing

        Args:
            hostname: DNS hostname
            endpoints: Map of regions to IPs

        Example:
            endpoints = {
                'US': '1.2.3.4',
                'EU': '5.6.7.8',
                'ASIA': '9.10.11.12'
            }

        TODO: Implement geo-routing
        """
        pass
```

## Identity and Access Management {#iam}

### Cross-Cloud IAM Strategy

```python
# Unified identity management
class MultiCloudIdentity:
    """
    Manage identities across clouds

    TODO: Implement OIDC federation
    TODO: Add SAML integration
    """

    def __init__(self):
        self.providers = ['aws', 'gcp', 'azure']

    def create_service_account(
        self,
        name: str,
        permissions: List[str],
        clouds: List[str]
    ):
        """
        Create service account in multiple clouds

        Args:
            name: Service account name
            permissions: List of permission actions
            clouds: Target clouds

        TODO: Implement for each cloud provider
        TODO: Set up cross-cloud trust relationships
        """
        pass

    def setup_workload_identity(
        self,
        kubernetes_namespace: str,
        kubernetes_service_account: str,
        cloud_service_account: str,
        cloud_provider: str
    ):
        """
        Configure Kubernetes workload identity

        Args:
            kubernetes_namespace: K8s namespace
            kubernetes_service_account: K8s service account
            cloud_service_account: Cloud IAM service account
            cloud_provider: Target cloud

        TODO: Implement for GKE Workload Identity
        TODO: Implement for EKS IAM Roles for Service Accounts (IRSA)
        TODO: Implement for AKS Managed Identity
        """
        pass
```

### Federated Identity Example

```yaml
# Kubernetes ServiceAccount with cloud IAM binding
---
# AWS EKS - IAM Role for Service Account (IRSA)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-platform
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/ml-training-role

---
# GCP GKE - Workload Identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-platform
  annotations:
    iam.gke.io/gcp-service-account: ml-training@project.iam.gserviceaccount.com

---
# Azure AKS - Managed Identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-platform
  annotations:
    azure.workload.identity/client-id: "12345678-1234-1234-1234-123456789012"
```

## Container Registry Management {#container-registry}

### Multi-Cloud Container Strategy

```python
# Container registry abstraction
class ContainerRegistry:
    """
    Manage container images across registries

    TODO: Implement push/pull operations
    TODO: Add image replication between registries
    """

    def __init__(self):
        self.registries = {
            'aws': 'account-id.dkr.ecr.us-east-1.amazonaws.com',
            'gcp': 'gcr.io/project-id',
            'azure': 'myregistry.azurecr.io',
            'dockerhub': 'docker.io/myorg'
        }

    def push_image(
        self,
        image_name: str,
        tag: str,
        registries: List[str]
    ):
        """
        Push image to multiple registries

        Args:
            image_name: Image name
            tag: Image tag
            registries: List of target registries

        TODO: Implement multi-registry push
        TODO: Add manifest list for multi-arch
        """
        for registry in registries:
            full_image = f"{self.registries[registry]}/{image_name}:{tag}"
            # TODO: Tag and push image
            pass

    def replicate_image(
        self,
        source_registry: str,
        dest_registry: str,
        image_name: str,
        tag: str
    ):
        """
        Replicate image between registries

        Args:
            source_registry: Source registry
            dest_registry: Destination registry
            image_name: Image name
            tag: Image tag

        TODO: Implement efficient replication
        TODO: Consider using tools like crane or skopeo
        """
        pass
```

## Configuration Management {#configuration-management}

### Cloud-Agnostic Configuration

```yaml
# ConfigMap for cloud-agnostic configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-platform-config
  namespace: ml-platform
data:
  # Detect cloud provider at runtime
  cloud-provider-detect.sh: |
    #!/bin/bash
    # Detect which cloud we're running on
    if [ -n "$AWS_REGION" ] || curl -s -f http://169.254.169.254/latest/meta-data/ &>/dev/null; then
      echo "aws"
    elif curl -s -f -H "Metadata-Flavor: Google" http://metadata.google.internal &>/dev/null; then
      echo "gcp"
    elif curl -s -f -H "Metadata: true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01" &>/dev/null; then
      echo "azure"
    else
      echo "unknown"
    fi

  # Application configuration
  app-config.yaml: |
    storage:
      backend: "${STORAGE_BACKEND:-auto}"  # auto-detect if not specified
      bucket: "${STORAGE_BUCKET}"
      prefix: "ml-artifacts/"

    database:
      type: "postgresql"  # Works on all clouds
      host: "${DB_HOST}"
      port: 5432
      database: "${DB_NAME}"
      ssl: true

    cache:
      type: "redis"  # Works on all clouds
      host: "${REDIS_HOST}"
      port: 6379

    monitoring:
      backend: "prometheus"  # Cloud-agnostic
      pushgateway: "${PUSHGATEWAY_URL}"
```

## Observability and Monitoring {#observability}

### Cloud-Agnostic Monitoring Stack

```yaml
# Prometheus for metrics (works everywhere)
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cloud_provider: '${CLOUD_PROVIDER}'
        cluster: '${CLUSTER_NAME}'
        region: '${REGION}'

    scrape_configs:
    - job_name: 'ml-inference'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - ml-platform
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: ml-inference
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace

    - job_name: 'ml-training'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - ml-platform
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: ml-training

    remote_write:
    # Can send to cloud-specific or unified monitoring
    - url: "${REMOTE_WRITE_URL}"
      basic_auth:
        username: "${REMOTE_WRITE_USER}"
        password: "${REMOTE_WRITE_PASSWORD}"
```

### Distributed Tracing

```python
# OpenTelemetry for cloud-agnostic tracing
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

def setup_tracing(service_name: str, cloud_provider: str):
    """
    Setup cloud-agnostic distributed tracing

    Args:
        service_name: Name of the service
        cloud_provider: Cloud provider identifier

    TODO: Configure with environment-specific endpoints
    """
    resource = Resource.create({
        "service.name": service_name,
        "cloud.provider": cloud_provider,
        "deployment.environment": os.getenv("ENVIRONMENT", "production")
    })

    tracer_provider = TracerProvider(resource=resource)

    # OTLP exporter works with all cloud providers and self-hosted collectors
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=os.getenv("OTEL_INSECURE", "false").lower() == "true"
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)

# Usage in ML inference
tracer = setup_tracing("ml-inference", os.getenv("CLOUD_PROVIDER", "unknown"))

@tracer.start_as_current_span("model_inference")
def predict(model_id: str, inputs: dict):
    """
    Run model inference with tracing

    TODO: Add detailed span attributes
    """
    span = trace.get_current_span()
    span.set_attribute("model.id", model_id)
    span.set_attribute("input.size", len(inputs))

    # TODO: Actual inference logic

    return results
```

## Summary {#summary}

Cloud-agnostic design for ML infrastructure requires careful balance between portability and functionality:

### Key Principles

1. **Kubernetes as Foundation**: Use K8s for consistent orchestration
2. **Abstraction Layers**: Create interfaces for cloud-specific services
3. **Open Standards**: Prefer open-source tools over proprietary services
4. **Configuration Management**: Externalize cloud-specific configuration
5. **Observability**: Use cloud-agnostic monitoring (Prometheus, OpenTelemetry)

### Practical Recommendations

1. **Start with Kubernetes**: Deploy all ML workloads on K8s
2. **Abstract Storage**: Use storage interface pattern for artifacts
3. **Service Mesh**: Implement Istio or Linkerd for cross-cloud connectivity
4. **Container Registry**: Replicate images across registries
5. **Identity Federation**: Use OIDC/SAML for cross-cloud auth
6. **Infrastructure as Code**: Use Terraform with cloud-agnostic modules

### Trade-offs to Consider

**When to Stay Cloud-Agnostic**:
- Core ML platform infrastructure
- Training workloads
- Model serving infrastructure
- Data processing pipelines

**When to Use Cloud-Native**:
- Specialized hardware (TPUs)
- Managed ML services for quick experimentation
- Deep integration with existing cloud ecosystem
- Cost-effective managed services

### Next Steps

1. Design cloud-agnostic architecture for your ML platform
2. Implement storage and compute abstractions
3. Set up Kubernetes clusters across target clouds
4. Configure service mesh for cross-cloud communication
5. Implement CI/CD pipelines that deploy to all clouds
6. Test failover and disaster recovery procedures

---

**Estimated Reading Time**: 80-100 minutes
**Hands-on Practice**: 6-8 hours (deploy on multiple clouds)
