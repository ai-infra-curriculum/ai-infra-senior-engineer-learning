# Lecture 3: Data Security and Encryption for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design data encryption strategies with encryption at rest (AES-256), encryption in transit (TLS 1.3), and key management (KMS/HSM) for ML datasets and models
- Implement data access controls using IAM policies, attribute-based access control (ABAC), and column-level security ensuring least-privilege data access
- Architect data classification systems categorizing data sensitivity (public, internal, confidential, restricted) with appropriate handling requirements
- Configure PII/PHI detection and handling using automated scanning, anonymization, pseudonymization, and data masking for privacy protection
- Design data lifecycle security managing data retention, secure deletion, backup encryption, and disaster recovery with security controls
- Implement data provenance and lineage tracking creating audit trails for data access, transformations, and usage for compliance and debugging
- Build secure data pipelines with input validation, sanitization, secure data transfer protocols, and monitoring for data exfiltration attempts
- Architect compliance controls for data regulations (GDPR, HIPAA, CCPA) with data residency, right-to-erasure, and consent management

## Table of Contents
1. [Introduction to Data Security](#introduction-to-data-security)
2. [Data Classification and Lifecycle](#data-classification-and-lifecycle)
3. [Encryption Fundamentals](#encryption-fundamentals)
4. [Encryption at Rest](#encryption-at-rest)
5. [Encryption in Transit](#encryption-in-transit)
6. [Key Management](#key-management)
7. [Data Access Control](#data-access-control)
8. [Data Masking and Anonymization](#data-masking-and-anonymization)
9. [Secure Data Pipelines](#secure-data-pipelines)
10. [Data Governance and Lineage](#data-governance-and-lineage)
11. [Case Studies and Best Practices](#case-studies-and-best-practices)

## Introduction to Data Security

Data is the foundation of machine learning systems. Training data, feature stores, and model predictions often contain sensitive information requiring robust security measures. As a Senior AI Infrastructure Engineer, you must design data pipelines that protect confidentiality, maintain integrity, and ensure availability.

### The ML Data Security Challenge

ML systems handle diverse data types across multiple stages:

```
┌─────────────────────────────────────────────────────────────┐
│                  ML Data Security Landscape                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Raw Data                                                   │
│  ├─ User PII (names, emails, addresses)                    │
│  ├─ Financial data (transactions, accounts)                │
│  ├─ Health records (diagnoses, treatments)                 │
│  ├─ Behavioral data (clicks, views, purchases)             │
│  └─ Proprietary business data                              │
│       ↓ [Collection & Ingestion]                           │
│                                                              │
│  Processed Data                                             │
│  ├─ Feature engineering outputs                            │
│  ├─ Normalized and transformed data                        │
│  ├─ Aggregated statistics                                  │
│  └─ Train/validation/test splits                           │
│       ↓ [Storage & Access]                                 │
│                                                              │
│  Training Data                                              │
│  ├─ Versioned datasets                                     │
│  ├─ Data augmentations                                     │
│  ├─ Labeled examples                                       │
│  └─ Embeddings and representations                         │
│       ↓ [Model Training]                                   │
│                                                              │
│  Model Artifacts                                            │
│  ├─ Trained weights (may memorize training data)           │
│  ├─ Model checkpoints                                      │
│  ├─ Training logs and metrics                              │
│  └─ Hyperparameters and configurations                     │
│       ↓ [Inference]                                        │
│                                                              │
│  Inference Data                                             │
│  ├─ Live user inputs                                       │
│  ├─ Prediction results                                     │
│  ├─ Feature values                                         │
│  └─ Model explanations                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Each stage presents unique security requirements and attack vectors.

### Data Security Principles

**Confidentiality**: Prevent unauthorized access to sensitive data
- Encryption at rest and in transit
- Access controls and authentication
- Data minimization (collect only what's needed)

**Integrity**: Ensure data hasn't been tampered with
- Cryptographic hashing
- Digital signatures
- Version control and immutability

**Availability**: Ensure authorized users can access data when needed
- Redundancy and replication
- Backup and disaster recovery
- DDoS protection

**Accountability**: Track who accessed what data and when
- Comprehensive audit logging
- Data lineage tracking
- Access review processes

## Data Classification and Lifecycle

Not all data requires the same level of protection. Classification helps allocate security resources appropriately.

### Data Classification Framework

```yaml
# Data classification levels for ML systems

PUBLIC:
  description: "Data that can be freely shared"
  examples:
    - Public datasets (ImageNet, MNIST)
    - Published research data
    - Marketing materials
  security_controls:
    - Basic access logging
    - Integrity checking
  retention: "As needed"

INTERNAL:
  description: "Data for internal use only"
  examples:
    - Model architectures
    - Internal documentation
    - Aggregated non-sensitive metrics
  security_controls:
    - Authentication required
    - Access logging
    - Encryption in transit
  retention: "7 years"

CONFIDENTIAL:
  description: "Sensitive business data"
  examples:
    - Proprietary training data
    - Model weights
    - Customer aggregated data
    - Business metrics
  security_controls:
    - Strong authentication (MFA)
    - Authorization controls
    - Encryption at rest and in transit
    - Comprehensive audit logging
    - Data masking for non-production
  retention: "3 years after last use"

RESTRICTED:
  description: "Highly sensitive data with regulatory requirements"
  examples:
    - PII (names, emails, SSN)
    - Financial data (credit cards, accounts)
    - Health records (PHI)
    - Biometric data
  security_controls:
    - Multi-factor authentication
    - Role-based access control
    - Encryption with customer-managed keys
    - Data loss prevention (DLP)
    - Tokenization/anonymization
    - Comprehensive audit logging
    - Compliance monitoring
  retention: "As required by regulation, then secure deletion"
```

### ML Data Lifecycle

```python
# Data lifecycle management for ML systems

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataLifecycleStage(Enum):
    COLLECTION = "collection"
    PROCESSING = "processing"
    STORAGE = "storage"
    USE = "use"
    ARCHIVE = "archive"
    DELETION = "deletion"

class DataAsset:
    """Represents a data asset with security metadata"""

    def __init__(
        self,
        asset_id: str,
        classification: DataClassification,
        owner: str,
        description: str
    ):
        self.asset_id = asset_id
        self.classification = classification
        self.owner = owner
        self.description = description
        self.created_at = datetime.utcnow()
        self.accessed_at = datetime.utcnow()
        self.stage = DataLifecycleStage.COLLECTION
        self.access_log: List[Dict] = []
        self.encryption_key_id: Optional[str] = None

    def record_access(self, user: str, operation: str, purpose: str):
        """Record data access for audit purposes"""
        self.access_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'user': user,
            'operation': operation,
            'purpose': purpose,
            'classification': self.classification.value
        })
        self.accessed_at = datetime.utcnow()

    def should_archive(self, inactive_days: int = 90) -> bool:
        """Determine if data should be archived"""
        if self.stage == DataLifecycleStage.DELETION:
            return False

        inactive_period = datetime.utcnow() - self.accessed_at
        return inactive_period.days > inactive_days

    def should_delete(self, retention_days: int) -> bool:
        """Determine if data should be deleted based on retention policy"""
        age = datetime.utcnow() - self.created_at
        return age.days > retention_days

    def get_required_controls(self) -> List[str]:
        """Get required security controls based on classification"""
        controls = ["access_logging", "backup"]

        if self.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            controls.extend([
                "encryption_at_rest",
                "encryption_in_transit",
                "mfa_required"
            ])

        if self.classification == DataClassification.RESTRICTED:
            controls.extend([
                "customer_managed_keys",
                "data_masking_non_prod",
                "dlp_scanning",
                "compliance_monitoring"
            ])

        return controls

# Example usage
training_dataset = DataAsset(
    asset_id="customer-behavior-v1",
    classification=DataClassification.CONFIDENTIAL,
    owner="ml-team@example.com",
    description="Customer behavior data for recommendation model"
)

training_dataset.record_access(
    user="data-scientist@example.com",
    operation="read",
    purpose="Model training experiment #1234"
)

print(f"Required controls: {training_dataset.get_required_controls()}")
```

## Encryption Fundamentals

Understanding encryption is essential for protecting data throughout its lifecycle.

### Encryption Types

**Symmetric Encryption**: Same key for encryption and decryption
- Fast and efficient
- Key distribution challenge
- Use cases: Data at rest, bulk encryption
- Algorithms: AES-256, ChaCha20

**Asymmetric Encryption**: Public/private key pairs
- Slower than symmetric
- Solves key distribution problem
- Use cases: Key exchange, digital signatures, authentication
- Algorithms: RSA, ECC, Ed25519

**Hybrid Encryption**: Combines both approaches
- Use asymmetric to exchange symmetric key
- Use symmetric key for actual data encryption
- Best of both worlds
- Use cases: TLS/SSL, encrypted messaging

### Encryption in ML Workflows

```python
# Example: Encrypting training data before storage

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import os
import json

class DataEncryption:
    """Encrypt sensitive training data"""

    def __init__(self, key_service_url: str):
        self.key_service_url = key_service_url
        self.backend = default_backend()

    def get_encryption_key(self, dataset_id: str) -> bytes:
        """
        Get encryption key from key management service

        In production, this would call an external KMS
        """
        # Placeholder - would call AWS KMS, GCP KMS, HashiCorp Vault, etc.
        # For demo, derive from dataset_id (DON'T DO THIS IN PRODUCTION)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'unique-salt-per-dataset',
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(dataset_id.encode())

    def encrypt_dataset(self, data: bytes, dataset_id: str) -> dict:
        """
        Encrypt dataset with AES-256-GCM

        Returns encrypted data and metadata
        """
        # Get encryption key
        key = self.get_encryption_key(dataset_id)

        # Generate random IV (initialization vector)
        iv = os.urandom(16)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Return encrypted data with metadata
        return {
            'ciphertext': ciphertext,
            'iv': iv,
            'tag': encryptor.tag,  # GCM authentication tag
            'algorithm': 'AES-256-GCM',
            'dataset_id': dataset_id,
            'encrypted_at': datetime.utcnow().isoformat()
        }

    def decrypt_dataset(self, encrypted_data: dict) -> bytes:
        """Decrypt dataset"""
        # Get decryption key
        key = self.get_encryption_key(encrypted_data['dataset_id'])

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(encrypted_data['iv'], encrypted_data['tag']),
            backend=self.backend
        )
        decryptor = cipher.decryptor()

        # Decrypt data
        plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()

        return plaintext

# Example usage
encryptor = DataEncryption(key_service_url="https://kms.example.com")

# Encrypt training data before storage
import pandas as pd
df = pd.DataFrame({'feature1': [1, 2, 3], 'label': [0, 1, 0]})
data_bytes = df.to_csv(index=False).encode()

encrypted = encryptor.encrypt_dataset(data_bytes, dataset_id="training-v1")

# Store encrypted data
with open('/encrypted-storage/training-v1.enc', 'wb') as f:
    f.write(encrypted['ciphertext'])

# Store metadata separately
with open('/encrypted-storage/training-v1.meta', 'w') as f:
    json.dump({
        'iv': encrypted['iv'].hex(),
        'tag': encrypted['tag'].hex(),
        'algorithm': encrypted['algorithm'],
        'dataset_id': encrypted['dataset_id'],
        'encrypted_at': encrypted['encrypted_at']
    }, f)
```

## Encryption at Rest

Protecting data while stored is fundamental to data security.

### Storage Layer Encryption

**1. Filesystem-Level Encryption**

```yaml
# Kubernetes PersistentVolume with encryption

# Using encrypted EBS volumes (AWS)
apiVersion: v1
kind: StorageClass
metadata:
  name: encrypted-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-east-1:123456789012:key/abcd1234-5678-90ab-cdef"
volumeBindingMode: WaitForFirstConsumer

---
# PVC using encrypted storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ml-training-data
  namespace: ml-training
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: encrypted-gp3
  resources:
    requests:
      storage: 100Gi
```

**2. Database Encryption**

```python
# PostgreSQL with Transparent Data Encryption (TDE)

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet

Base = declarative_base()

class EncryptedTrainingData(Base):
    """Store encrypted training samples"""
    __tablename__ = 'training_data'

    id = Column(Integer, primary_key=True)
    dataset_id = Column(String(100), nullable=False, index=True)
    sample_encrypted = Column(LargeBinary, nullable=False)
    label_encrypted = Column(LargeBinary, nullable=False)
    encryption_key_id = Column(String(100), nullable=False)

class ApplicationLevelEncryption:
    """Application-level encryption for sensitive data"""

    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt_training_sample(self, features: str, label: str) -> tuple:
        """Encrypt training sample before storing in database"""
        encrypted_features = self.cipher.encrypt(features.encode())
        encrypted_label = self.cipher.encrypt(label.encode())
        return encrypted_features, encrypted_label

    def decrypt_training_sample(self, encrypted_features: bytes, encrypted_label: bytes) -> tuple:
        """Decrypt training sample after retrieving from database"""
        features = self.cipher.decrypt(encrypted_features).decode()
        label = self.cipher.decrypt(encrypted_label).decode()
        return features, label

# Usage
encryption_key = Fernet.generate_key()
encryptor = ApplicationLevelEncryption(encryption_key)

# Encrypt before storage
features_encrypted, label_encrypted = encryptor.encrypt_training_sample(
    features='{"age": 25, "income": 50000}',
    label='approved'
)

# Store in database with connection-level TLS
engine = create_engine(
    'postgresql://user:pass@db-host:5432/mldata',
    connect_args={'sslmode': 'require', 'sslcert': '/path/to/client-cert.pem'}
)
```

**3. Object Storage Encryption**

```python
# S3 Server-Side Encryption with Customer-Managed Keys

import boto3
from botocore.config import Config

class SecureDataStorage:
    """Secure storage for ML datasets"""

    def __init__(self, kms_key_id: str):
        self.kms_key_id = kms_key_id
        config = Config(
            region_name='us-east-1',
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'}
        )
        self.s3 = boto3.client('s3', config=config)

    def upload_encrypted_dataset(
        self,
        local_file: str,
        bucket: str,
        key: str,
        metadata: dict = None
    ):
        """
        Upload dataset with server-side encryption using customer-managed keys

        Encryption is transparent to application after upload
        """
        extra_args = {
            'ServerSideEncryption': 'aws:kms',
            'SSEKMSKeyId': self.kms_key_id,
            'Metadata': metadata or {},
            'StorageClass': 'INTELLIGENT_TIERING'  # Cost optimization
        }

        self.s3.upload_file(
            local_file,
            bucket,
            key,
            ExtraArgs=extra_args
        )

        print(f"Uploaded {local_file} to s3://{bucket}/{key} with KMS encryption")

    def download_encrypted_dataset(
        self,
        bucket: str,
        key: str,
        local_file: str
    ):
        """
        Download encrypted dataset
        Decryption is automatic if caller has KMS permissions
        """
        self.s3.download_file(bucket, key, local_file)
        print(f"Downloaded s3://{bucket}/{key} to {local_file}")

# Usage
storage = SecureDataStorage(
    kms_key_id='arn:aws:kms:us-east-1:123456789012:key/abcd1234'
)

storage.upload_encrypted_dataset(
    local_file='/data/training-v1.parquet',
    bucket='ml-training-data',
    key='datasets/v1/training.parquet',
    metadata={
        'classification': 'confidential',
        'owner': 'ml-team@example.com',
        'purpose': 'model-training'
    }
)
```

## Encryption in Transit

Protecting data as it moves between systems is equally important.

### TLS/SSL Configuration

**1. Mutual TLS (mTLS) for Service-to-Service Communication**

```yaml
# Istio service mesh configuration for mTLS

apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: ml-training
spec:
  mtls:
    mode: STRICT  # Require mTLS for all traffic

---
# Destination rule for mTLS
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: training-service-mtls
  namespace: ml-training
spec:
  host: training-service.ml-training.svc.cluster.local
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL  # Use Istio-provided certificates
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
```

**2. Application-Level TLS**

```python
# Secure data transfer between components

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl

class SecureMLClient:
    """Client for secure communication with ML services"""

    def __init__(
        self,
        base_url: str,
        client_cert: str,
        client_key: str,
        ca_cert: str
    ):
        self.base_url = base_url
        self.session = requests.Session()

        # Configure client certificate
        self.session.cert = (client_cert, client_key)

        # Configure CA certificate for server verification
        self.session.verify = ca_cert

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def upload_training_data(self, dataset_path: str, dataset_id: str):
        """Upload training data over TLS"""
        with open(dataset_path, 'rb') as f:
            response = self.session.post(
                f"{self.base_url}/api/v1/datasets/{dataset_id}",
                files={'dataset': f},
                headers={'X-Dataset-Classification': 'confidential'},
                timeout=300
            )

        response.raise_for_status()
        return response.json()

    def download_model(self, model_id: str, output_path: str):
        """Download model over TLS"""
        response = self.session.get(
            f"{self.base_url}/api/v1/models/{model_id}",
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

# Usage
client = SecureMLClient(
    base_url='https://ml-platform.example.com',
    client_cert='/certs/client.crt',
    client_key='/certs/client.key',
    ca_cert='/certs/ca.crt'
)

client.upload_training_data(
    dataset_path='/data/training.parquet',
    dataset_id='customer-behavior-v1'
)
```

### VPN and Private Connectivity

```python
# Configure private connectivity to cloud data sources

# Example: AWS PrivateLink configuration
import boto3

def setup_private_s3_access():
    """
    Setup VPC endpoint for private S3 access
    No data traverses public internet
    """
    ec2 = boto3.client('ec2')

    # Create VPC endpoint for S3
    response = ec2.create_vpc_endpoint(
        VpcId='vpc-0123456789abcdef',
        ServiceName='com.amazonaws.s3',
        RouteTableIds=['rtb-0123456789abcdef'],
        PolicyDocument=json.dumps({
            'Statement': [{
                'Effect': 'Allow',
                'Principal': '*',
                'Action': [
                    's3:GetObject',
                    's3:PutObject'
                ],
                'Resource': [
                    'arn:aws:s3:::ml-training-data/*'
                ]
            }]
        })
    )

    return response['VpcEndpoint']['VpcEndpointId']
```

## Key Management

Effective key management is critical for encryption security.

### Key Management Best Practices

```python
# Integration with cloud key management services

import boto3
import base64
from datetime import datetime, timedelta

class KeyManagementService:
    """Wrapper for AWS KMS (similar patterns for GCP KMS, Azure Key Vault)"""

    def __init__(self, region: str = 'us-east-1'):
        self.kms = boto3.client('kms', region_name=region)
        self.key_cache = {}  # Cache for performance (with expiration)

    def create_data_key(self, kms_key_id: str, encryption_context: dict = None):
        """
        Generate data encryption key

        Returns plaintext and encrypted version
        Use plaintext for encryption, store encrypted version
        """
        response = self.kms.generate_data_key(
            KeyId=kms_key_id,
            KeySpec='AES_256',
            EncryptionContext=encryption_context or {}
        )

        return {
            'plaintext_key': response['Plaintext'],
            'encrypted_key': response['CiphertextBlob'],
            'key_id': response['KeyId']
        }

    def decrypt_data_key(self, encrypted_key: bytes, encryption_context: dict = None):
        """Decrypt data encryption key"""
        # Check cache first
        cache_key = base64.b64encode(encrypted_key).decode()
        if cache_key in self.key_cache:
            cached_entry = self.key_cache[cache_key]
            if cached_entry['expires_at'] > datetime.utcnow():
                return cached_entry['plaintext_key']

        # Decrypt using KMS
        response = self.kms.decrypt(
            CiphertextBlob=encrypted_key,
            EncryptionContext=encryption_context or {}
        )

        plaintext_key = response['Plaintext']

        # Cache for 5 minutes
        self.key_cache[cache_key] = {
            'plaintext_key': plaintext_key,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }

        return plaintext_key

    def rotate_key(self, key_id: str):
        """Enable automatic key rotation"""
        self.kms.enable_key_rotation(KeyId=key_id)

    def schedule_key_deletion(self, key_id: str, pending_days: int = 30):
        """
        Schedule key for deletion
        Provides time to recover from accidental deletion
        """
        self.kms.schedule_key_deletion(
            KeyId=key_id,
            PendingWindowInDays=pending_days
        )

# Example usage: Envelope encryption pattern
kms = KeyManagementService()

# 1. Generate data encryption key
data_key = kms.create_data_key(
    kms_key_id='arn:aws:kms:us-east-1:123456789012:key/abcd1234',
    encryption_context={
        'dataset_id': 'training-v1',
        'classification': 'confidential',
        'owner': 'ml-team'
    }
)

# 2. Encrypt large dataset with data key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

iv = os.urandom(16)
cipher = Cipher(
    algorithms.AES(data_key['plaintext_key']),
    modes.GCM(iv),
    backend=default_backend()
)
encryptor = cipher.encryptor()

# Encrypt actual data
plaintext_data = b"Large training dataset..."
ciphertext = encryptor.update(plaintext_data) + encryptor.finalize()

# 3. Store encrypted data key with encrypted data
# Discard plaintext key from memory
import json
metadata = {
    'encrypted_data_key': base64.b64encode(data_key['encrypted_key']).decode(),
    'iv': base64.b64encode(iv).decode(),
    'tag': base64.b64encode(encryptor.tag).decode(),
    'kms_key_id': data_key['key_id'],
    'encryption_context': {
        'dataset_id': 'training-v1',
        'classification': 'confidential'
    }
}

# Later: Decrypt data
# 1. Decrypt data key using KMS
decrypted_data_key = kms.decrypt_data_key(
    base64.b64decode(metadata['encrypted_data_key']),
    encryption_context=metadata['encryption_context']
)

# 2. Decrypt data
cipher = Cipher(
    algorithms.AES(decrypted_data_key),
    modes.GCM(
        base64.b64decode(metadata['iv']),
        base64.b64decode(metadata['tag'])
    ),
    backend=default_backend()
)
decryptor = cipher.decryptor()
plaintext = decryptor.update(ciphertext) + decryptor.finalize()
```

### Key Rotation Strategy

```python
class KeyRotationManager:
    """Manage encryption key rotation"""

    def __init__(self, kms_client):
        self.kms = kms_client

    def rotate_dataset_keys(self, dataset_id: str, old_key_id: str, new_key_id: str):
        """
        Rotate encryption keys for a dataset

        Process:
        1. Create new data key with new master key
        2. Decrypt data with old key
        3. Re-encrypt data with new key
        4. Update metadata
        5. Schedule old key for deletion
        """
        print(f"Rotating keys for dataset: {dataset_id}")

        # Get dataset metadata
        metadata = self._load_metadata(dataset_id)

        # Decrypt with old key
        old_data_key = self.kms.decrypt_data_key(
            base64.b64decode(metadata['encrypted_data_key']),
            encryption_context={'dataset_id': dataset_id}
        )

        # Load and decrypt data
        ciphertext = self._load_encrypted_data(dataset_id)
        plaintext = self._decrypt_data(ciphertext, old_data_key, metadata)

        # Generate new data key
        new_data_key = self.kms.create_data_key(
            kms_key_id=new_key_id,
            encryption_context={'dataset_id': dataset_id}
        )

        # Re-encrypt data
        new_ciphertext, new_metadata = self._encrypt_data(
            plaintext,
            new_data_key['plaintext_key']
        )

        # Update metadata with new encrypted data key
        new_metadata.update({
            'encrypted_data_key': base64.b64encode(new_data_key['encrypted_key']).decode(),
            'kms_key_id': new_key_id,
            'rotated_at': datetime.utcnow().isoformat(),
            'previous_key_id': old_key_id
        })

        # Save re-encrypted data and metadata
        self._save_encrypted_data(dataset_id, new_ciphertext)
        self._save_metadata(dataset_id, new_metadata)

        print(f"Key rotation complete for dataset: {dataset_id}")

        # Schedule old key for deletion (after grace period)
        self.kms.schedule_key_deletion(old_key_id, pending_days=30)
```

## Data Access Control

Fine-grained access control ensures only authorized users access sensitive data.

### Attribute-Based Access Control (ABAC)

```python
# ABAC policy engine for data access

from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class Action(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXPORT = "export"

@dataclass
class User:
    id: str
    role: str
    department: str
    clearance_level: int
    groups: Set[str]

@dataclass
class DataResource:
    id: str
    classification: str
    owner: str
    department: str
    required_clearance: int
    tags: Set[str]

class ABACPolicy:
    """Attribute-based access control for ML data"""

    def evaluate(
        self,
        user: User,
        resource: DataResource,
        action: Action,
        context: Dict = None
    ) -> bool:
        """
        Evaluate if user can perform action on resource

        Policy considers:
        - User attributes (role, department, clearance)
        - Resource attributes (classification, owner, required clearance)
        - Environmental attributes (time, location, purpose)
        """
        context = context or {}

        # Rule 1: Clearance level check
        if user.clearance_level < resource.required_clearance:
            print(f"Denied: Insufficient clearance level")
            return False

        # Rule 2: Department matching for restricted data
        if resource.classification == "RESTRICTED":
            if user.department != resource.department:
                print(f"Denied: Department mismatch for restricted data")
                return False

        # Rule 3: Data scientist role restrictions
        if user.role == "data-scientist":
            # Can read/write in ml-training namespace
            # Cannot export restricted data
            if action == Action.EXPORT and resource.classification == "RESTRICTED":
                print(f"Denied: Data scientists cannot export restricted data")
                return False

        # Rule 4: Time-based access
        if context.get('business_hours_only', False):
            from datetime import datetime
            hour = datetime.utcnow().hour
            if hour < 8 or hour > 18:
                print(f"Denied: Access only during business hours")
                return False

        # Rule 5: Purpose limitation
        allowed_purposes = {'model-training', 'model-evaluation', 'research'}
        if context.get('purpose') not in allowed_purposes:
            print(f"Denied: Invalid purpose")
            return False

        # Rule 6: Owner override
        if user.id == resource.owner:
            return True

        # Rule 7: Group-based access
        required_groups = {'ml-team', 'data-access'}
        if not required_groups.intersection(user.groups):
            print(f"Denied: Not member of required groups")
            return False

        return True

# Example usage
policy = ABACPolicy()

user = User(
    id="alice@example.com",
    role="data-scientist",
    department="ml-research",
    clearance_level=3,
    groups={"ml-team", "data-access"}
)

dataset = DataResource(
    id="customer-data-v1",
    classification="CONFIDENTIAL",
    owner="bob@example.com",
    department="ml-research",
    required_clearance=3,
    tags={"pii", "customer-data"}
)

# Check access
can_read = policy.evaluate(
    user=user,
    resource=dataset,
    action=Action.READ,
    context={'purpose': 'model-training', 'business_hours_only': False}
)

print(f"Can read: {can_read}")

can_export = policy.evaluate(
    user=user,
    resource=dataset,
    action=Action.EXPORT,
    context={'purpose': 'model-training'}
)

print(f"Can export: {can_export}")
```

### Row-Level and Column-Level Security

```python
# Implement fine-grained data access

import pandas as pd
from typing import List, Set

class DataAccessFilter:
    """Filter data based on user permissions"""

    def __init__(self, user: User):
        self.user = user

    def filter_dataframe(
        self,
        df: pd.DataFrame,
        resource_metadata: Dict
    ) -> pd.DataFrame:
        """
        Apply row and column filtering based on user permissions
        """
        filtered_df = df.copy()

        # Column-level filtering: Remove PII columns if user lacks clearance
        if self.user.clearance_level < 4:  # PII requires clearance 4+
            pii_columns = resource_metadata.get('pii_columns', [])
            filtered_df = filtered_df.drop(columns=pii_columns, errors='ignore')
            print(f"Removed PII columns: {pii_columns}")

        # Row-level filtering: Filter by department
        if 'department' in filtered_df.columns:
            if self.user.role != 'admin':
                filtered_df = filtered_df[
                    filtered_df['department'] == self.user.department
                ]
                print(f"Filtered to department: {self.user.department}")

        # Data masking: Mask sensitive columns for non-production use
        if resource_metadata.get('environment') != 'production':
            sensitive_columns = resource_metadata.get('sensitive_columns', [])
            for col in sensitive_columns:
                if col in filtered_df.columns:
                    filtered_df[col] = self._mask_column(filtered_df[col])

        return filtered_df

    def _mask_column(self, series: pd.Series) -> pd.Series:
        """Mask sensitive data"""
        if series.dtype == 'object':  # String data
            return series.apply(lambda x: 'XXXX' + str(x)[-4:] if pd.notna(x) else x)
        else:  # Numeric data
            return series.apply(lambda x: round(x / 1000) * 1000 if pd.notna(x) else x)

# Example usage
user = User(
    id="analyst@example.com",
    role="analyst",
    department="marketing",
    clearance_level=2,
    groups={"analysts"}
)

# Original dataframe
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com'],
    'department': ['marketing', 'sales', 'marketing', 'sales'],
    'revenue': [1000, 2000, 1500, 2500]
})

resource_metadata = {
    'pii_columns': ['name', 'email'],
    'sensitive_columns': ['revenue'],
    'environment': 'staging'
}

filter = DataAccessFilter(user)
filtered_df = filter.filter_dataframe(df, resource_metadata)

print("Filtered DataFrame:")
print(filtered_df)
# Output: Only marketing department rows, no PII columns, masked revenue
```

## Data Masking and Anonymization

Data masking protects sensitive information while preserving data utility.

### Masking Techniques

```python
# Data masking for ML workloads

import hashlib
import hmac
from faker import Faker
import pandas as pd
import numpy as np

class DataMasking:
    """Various data masking techniques"""

    def __init__(self, seed: int = 42):
        self.faker = Faker()
        Faker.seed(seed)
        self.secret_key = b'your-secret-key-here'  # In production, use KMS

    def pseudonymize(self, value: str) -> str:
        """
        Consistent pseudonymization using HMAC

        Same input always produces same output
        Cannot reverse without key
        """
        return hmac.new(
            self.secret_key,
            value.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

    def tokenize_pii(self, df: pd.DataFrame, pii_columns: List[str]) -> pd.DataFrame:
        """Replace PII with tokens"""
        masked_df = df.copy()

        for col in pii_columns:
            if col in masked_df.columns:
                if col == 'name':
                    masked_df[col] = [self.faker.name() for _ in range(len(masked_df))]
                elif col == 'email':
                    masked_df[col] = [self.faker.email() for _ in range(len(masked_df))]
                elif col == 'phone':
                    masked_df[col] = [self.faker.phone_number() for _ in range(len(masked_df))]
                elif col == 'address':
                    masked_df[col] = [self.faker.address() for _ in range(len(masked_df))]
                elif col == 'ssn':
                    masked_df[col] = [self.faker.ssn() for _ in range(len(masked_df))]
                else:
                    # Generic pseudonymization
                    masked_df[col] = masked_df[col].apply(self.pseudonymize)

        return masked_df

    def add_noise(self, df: pd.DataFrame, numeric_columns: List[str], noise_level: float = 0.05):
        """
        Add statistical noise to numeric columns

        Preserves statistical properties while protecting individual values
        """
        masked_df = df.copy()

        for col in numeric_columns:
            if col in masked_df.columns:
                # Add Gaussian noise proportional to standard deviation
                std = masked_df[col].std()
                noise = np.random.normal(0, std * noise_level, size=len(masked_df))
                masked_df[col] = masked_df[col] + noise

        return masked_df

    def generalize(self, df: pd.DataFrame, rules: Dict[str, Dict]) -> pd.DataFrame:
        """
        Generalize values to reduce granularity

        Example: Exact age -> Age range
        """
        masked_df = df.copy()

        for col, rule in rules.items():
            if col in masked_df.columns:
                if rule['type'] == 'binning':
                    masked_df[col] = pd.cut(
                        masked_df[col],
                        bins=rule['bins'],
                        labels=rule['labels']
                    )
                elif rule['type'] == 'rounding':
                    masked_df[col] = (masked_df[col] / rule['factor']).round() * rule['factor']

        return masked_df

# Example usage
masker = DataMasking()

# Original sensitive data
df = pd.DataFrame({
    'customer_id': [1001, 1002, 1003],
    'name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
    'age': [25, 42, 35],
    'income': [50000, 75000, 60000],
    'zip_code': ['12345', '23456', '34567']
})

# Mask PII
masked_df = masker.tokenize_pii(df, pii_columns=['name', 'email'])

# Add noise to financial data
masked_df = masker.add_noise(masked_df, numeric_columns=['income'], noise_level=0.1)

# Generalize age and zip code
masked_df = masker.generalize(masked_df, rules={
    'age': {
        'type': 'binning',
        'bins': [0, 30, 50, 100],
        'labels': ['18-30', '31-50', '51+']
    },
    'zip_code': {
        'type': 'rounding',
        'factor': 1000  # Keep only first 2 digits
    }
})

print("Masked DataFrame:")
print(masked_df)
```

### Differential Privacy

```python
# Differential privacy for ML training

import numpy as np
from typing import Tuple

class DifferentialPrivacy:
    """Apply differential privacy to ML training"""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Initialize DP mechanism

        epsilon: Privacy budget (smaller = more private)
        delta: Probability of privacy breach
        """
        self.epsilon = epsilon
        self.delta = delta

    def add_laplace_noise(self, value: float, sensitivity: float) -> float:
        """
        Add Laplace noise for differential privacy

        sensitivity: Maximum change in output from changing one input
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

    def clip_gradients(
        self,
        gradients: np.ndarray,
        clip_norm: float
    ) -> np.ndarray:
        """
        Clip gradients to bound sensitivity
        Required for DP-SGD
        """
        grad_norm = np.linalg.norm(gradients)
        if grad_norm > clip_norm:
            gradients = gradients * (clip_norm / grad_norm)
        return gradients

    def private_aggregation(
        self,
        values: np.ndarray,
        sensitivity: float
    ) -> float:
        """
        Aggregate values with differential privacy

        Use for releasing aggregate statistics
        """
        true_sum = np.sum(values)
        private_sum = self.add_laplace_noise(true_sum, sensitivity)
        return private_sum

# Example: DP-SGD training
class DPTraining:
    """Train ML model with differential privacy"""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5, clip_norm: float = 1.0):
        self.dp = DifferentialPrivacy(epsilon, delta)
        self.clip_norm = clip_norm

    def train_step(self, model, batch, learning_rate: float):
        """
        Training step with differential privacy

        1. Compute per-example gradients
        2. Clip each gradient
        3. Add noise to aggregated gradient
        4. Update model
        """
        # Compute per-example gradients (simplified)
        per_example_grads = []
        for example in batch:
            grad = self.compute_gradient(model, example)
            # Clip gradient
            clipped_grad = self.dp.clip_gradients(grad, self.clip_norm)
            per_example_grads.append(clipped_grad)

        # Aggregate clipped gradients
        aggregated_grad = np.mean(per_example_grads, axis=0)

        # Add noise for privacy
        noise_scale = self.clip_norm / (len(batch) * self.dp.epsilon)
        noise = np.random.normal(0, noise_scale, size=aggregated_grad.shape)
        private_grad = aggregated_grad + noise

        # Update model
        self.update_model(model, private_grad, learning_rate)

        return private_grad

    def compute_gradient(self, model, example):
        """Compute gradient for one example"""
        # Placeholder - actual implementation depends on model
        return np.random.randn(10)

    def update_model(self, model, gradient, learning_rate):
        """Update model parameters"""
        # Placeholder - actual implementation depends on model
        pass
```

## Secure Data Pipelines

End-to-end security for ML data pipelines.

### Secure Pipeline Architecture

```python
# Secure data pipeline for ML

from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

@dataclass
class PipelineStage:
    name: str
    required_role: str
    min_clearance: int
    encryption_required: bool
    audit_level: str

class SecureMLPipeline:
    """Secure data pipeline for ML workflows"""

    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
        self.logger = logging.getLogger(__name__)

        # Define pipeline stages with security requirements
        self.stages = [
            PipelineStage("data_ingestion", "data-engineer", 2, True, "full"),
            PipelineStage("data_validation", "data-engineer", 2, True, "full"),
            PipelineStage("data_transformation", "data-scientist", 2, True, "full"),
            PipelineStage("feature_engineering", "data-scientist", 2, True, "full"),
            PipelineStage("model_training", "data-scientist", 2, True, "full"),
            PipelineStage("model_evaluation", "ml-engineer", 2, True, "full"),
            PipelineStage("model_deployment", "ml-engineer", 3, True, "full"),
        ]

    def execute_stage(
        self,
        stage_name: str,
        user: User,
        input_data: Dict,
        context: Dict
    ) -> Dict:
        """
        Execute pipeline stage with security checks

        1. Verify user authorization
        2. Validate input data
        3. Encrypt sensitive data
        4. Execute stage
        5. Audit log
        6. Return encrypted results
        """
        # Find stage
        stage = next((s for s in self.stages if s.name == stage_name), None)
        if not stage:
            raise ValueError(f"Unknown stage: {stage_name}")

        # Authorization check
        if not self._authorize_user(user, stage):
            raise PermissionError(f"User {user.id} not authorized for {stage_name}")

        # Input validation
        self._validate_input(input_data, stage)

        # Encryption check
        if stage.encryption_required and not input_data.get('encrypted', False):
            raise ValueError(f"Stage {stage_name} requires encrypted input")

        # Audit log
        self._audit_log(
            stage=stage_name,
            user=user.id,
            action="execute",
            context=context,
            level=stage.audit_level
        )

        # Execute stage (delegated to specific handlers)
        result = self._execute_stage_logic(stage_name, input_data, context)

        # Encrypt results if needed
        if stage.encryption_required:
            result = self._encrypt_result(result)

        return result

    def _authorize_user(self, user: User, stage: PipelineStage) -> bool:
        """Check if user can execute stage"""
        if user.clearance_level < stage.min_clearance:
            return False

        if user.role != stage.required_role and user.role != "admin":
            return False

        return True

    def _validate_input(self, data: Dict, stage: PipelineStage):
        """Validate input data"""
        required_keys = ['data', 'metadata', 'classification']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

    def _audit_log(self, stage: str, user: str, action: str, context: Dict, level: str):
        """Create audit log entry"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'pipeline_id': self.pipeline_id,
            'stage': stage,
            'user': user,
            'action': action,
            'context': context,
            'level': level
        }

        if level == "full":
            self.logger.info(f"Audit: {json.dumps(log_entry)}")
        # In production, send to centralized audit system

    def _execute_stage_logic(self, stage: str, data: Dict, context: Dict) -> Dict:
        """Execute actual stage logic"""
        # Placeholder - actual implementation depends on stage
        return {"status": "success", "output": "processed_data"}

    def _encrypt_result(self, result: Dict) -> Dict:
        """Encrypt stage result"""
        # Placeholder - use actual encryption
        result['encrypted'] = True
        return result
```

## Data Governance and Lineage

Track data lineage for compliance and debugging.

### Data Lineage Tracking

```python
# Track data lineage through ML pipeline

from typing import List, Optional
from datetime import datetime
import uuid

class DataLineageNode:
    """Represents a node in data lineage graph"""

    def __init__(
        self,
        node_id: str,
        node_type: str,  # dataset, transformation, model, prediction
        name: str,
        owner: str,
        classification: str
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.owner = owner
        self.classification = classification
        self.created_at = datetime.utcnow()
        self.metadata = {}
        self.parents: List[str] = []  # Input nodes
        self.children: List[str] = []  # Output nodes

class DataLineageTracker:
    """Track data lineage through ML pipelines"""

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def track_dataset(
        self,
        name: str,
        owner: str,
        classification: str,
        source: Optional[str] = None,
        metadata: Dict = None
    ) -> str:
        """Track new dataset"""
        node_id = str(uuid.uuid4())
        node = DataLineageNode(node_id, "dataset", name, owner, classification)
        node.metadata = metadata or {}

        if source:
            node.parents.append(source)
            self.edges.append({"from": source, "to": node_id, "type": "derived"})

        self.nodes[node_id] = node
        return node_id

    def track_transformation(
        self,
        name: str,
        inputs: List[str],
        output_name: str,
        code_version: str,
        owner: str
    ) -> str:
        """Track data transformation"""
        node_id = str(uuid.uuid4())
        node = DataLineageNode(node_id, "transformation", name, owner, "internal")
        node.parents = inputs
        node.metadata = {
            "code_version": code_version,
            "output_dataset": output_name
        }

        for input_id in inputs:
            self.edges.append({"from": input_id, "to": node_id, "type": "input"})
            if input_id in self.nodes:
                self.nodes[input_id].children.append(node_id)

        self.nodes[node_id] = node
        return node_id

    def track_model_training(
        self,
        model_name: str,
        training_data_id: str,
        model_version: str,
        owner: str,
        hyperparameters: Dict
    ) -> str:
        """Track model training"""
        node_id = str(uuid.uuid4())
        node = DataLineageNode(node_id, "model", model_name, owner, "confidential")
        node.parents = [training_data_id]
        node.metadata = {
            "model_version": model_version,
            "hyperparameters": hyperparameters,
            "training_dataset": training_data_id
        }

        self.edges.append({"from": training_data_id, "to": node_id, "type": "trained-on"})
        if training_data_id in self.nodes:
            self.nodes[training_data_id].children.append(node_id)

        self.nodes[node_id] = node
        return node_id

    def get_lineage(self, node_id: str, direction: str = "upstream") -> Dict:
        """
        Get lineage for a node

        direction: "upstream" (sources) or "downstream" (descendants)
        """
        if node_id not in self.nodes:
            return {}

        visited = set()
        lineage = {}

        def traverse(current_id, depth=0):
            if current_id in visited or depth > 10:  # Prevent cycles and infinite loops
                return

            visited.add(current_id)
            node = self.nodes[current_id]

            lineage[current_id] = {
                "type": node.node_type,
                "name": node.name,
                "owner": node.owner,
                "classification": node.classification,
                "created_at": node.created_at.isoformat(),
                "depth": depth
            }

            # Recursively traverse parents or children
            next_nodes = node.parents if direction == "upstream" else node.children
            for next_id in next_nodes:
                if next_id in self.nodes:
                    traverse(next_id, depth + 1)

        traverse(node_id)
        return lineage

    def check_compliance(self, model_id: str) -> Dict:
        """
        Check if model training complied with data usage policies

        Verify:
        - All training data had appropriate classification
        - Data was not used beyond retention period
        - Required approvals were obtained
        """
        lineage = self.get_lineage(model_id, direction="upstream")

        issues = []
        for node_id, info in lineage.items():
            if info['type'] == 'dataset':
                # Check classification
                if info['classification'] == 'RESTRICTED':
                    issues.append(f"Model trained on RESTRICTED data: {info['name']}")

                # Check if data owner matches model owner
                model_owner = self.nodes[model_id].owner
                if info['owner'] != model_owner:
                    issues.append(f"Data owner mismatch: {info['name']}")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "lineage_depth": max(info['depth'] for info in lineage.values())
        }

# Example usage
tracker = DataLineageTracker()

# Track raw data
raw_data_id = tracker.track_dataset(
    name="customer_transactions_raw",
    owner="data-team@example.com",
    classification="CONFIDENTIAL",
    metadata={"source": "production_db", "rows": 1000000}
)

# Track transformation
cleaned_data_id = tracker.track_transformation(
    name="data_cleaning",
    inputs=[raw_data_id],
    output_name="customer_transactions_clean",
    code_version="v1.2.3",
    owner="data-team@example.com"
)

# Track feature engineering
features_id = tracker.track_transformation(
    name="feature_engineering",
    inputs=[cleaned_data_id],
    output_name="customer_features",
    code_version="v2.0.1",
    owner="ml-team@example.com"
)

# Track model training
model_id = tracker.track_model_training(
    model_name="fraud_detection_model",
    training_data_id=features_id,
    model_version="v1.0.0",
    owner="ml-team@example.com",
    hyperparameters={"learning_rate": 0.001, "epochs": 100}
)

# Get upstream lineage
lineage = tracker.get_lineage(model_id, direction="upstream")
print("Model lineage:")
for node_id, info in lineage.items():
    print(f"  {info['name']} ({info['type']}) - Depth: {info['depth']}")

# Check compliance
compliance = tracker.check_compliance(model_id)
print(f"\nCompliance check: {'PASS' if compliance['compliant'] else 'FAIL'}")
if compliance['issues']:
    print("Issues:")
    for issue in compliance['issues']:
        print(f"  - {issue}")
```

## Case Studies and Best Practices

### Case Study: GDPR Compliance for ML System

**Scenario**: E-commerce company building recommendation system with EU customer data.

**Requirements**:
- Right to erasure (delete user data on request)
- Right to data portability
- Purpose limitation
- Data minimization
- Consent management

**Implementation**:

```python
class GDPRCompliantMLSystem:
    """GDPR-compliant ML system architecture"""

    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_store = DataStore()
        self.lineage_tracker = DataLineageTracker()

    def process_user_data(self, user_id: str, purpose: str):
        """Process user data only with valid consent"""
        # Check consent
        if not self.consent_manager.has_consent(user_id, purpose):
            raise PermissionError(f"No consent for {purpose}")

        # Track data usage
        self.lineage_tracker.track_data_usage(
            user_id=user_id,
            purpose=purpose,
            timestamp=datetime.utcnow()
        )

        # Minimal data collection
        data = self.data_store.get_user_data(
            user_id=user_id,
            fields=['purchase_history'],  # Only what's needed
            anonymize=False
        )

        return data

    def handle_erasure_request(self, user_id: str):
        """
        Handle GDPR right to erasure

        Complexity: Must delete from all systems including trained models
        """
        # 1. Delete raw user data
        self.data_store.delete_user_data(user_id)

        # 2. Find all datasets containing user data
        datasets = self.lineage_tracker.find_datasets_with_user(user_id)

        # 3. Retrain models without user's data
        models = self.lineage_tracker.find_models_trained_on_datasets(datasets)
        for model in models:
            self.schedule_model_retraining(model, exclude_user=user_id)

        # 4. Remove from feature store
        self.feature_store.delete_user_features(user_id)

        # 5. Log erasure for audit
        self.audit_log.record_erasure(user_id, datetime.utcnow())

    def export_user_data(self, user_id: str) -> Dict:
        """Handle GDPR right to data portability"""
        return {
            'user_id': user_id,
            'raw_data': self.data_store.get_user_data(user_id, anonymize=False),
            'computed_features': self.feature_store.get_user_features(user_id),
            'model_predictions': self.prediction_store.get_user_predictions(user_id),
            'data_usage_log': self.lineage_tracker.get_user_data_usage(user_id)
        }
```

## Summary

Data security is fundamental to ML systems. Key principles:

1. **Classification**: Classify data based on sensitivity, apply appropriate controls
2. **Encryption**: Encrypt data at rest and in transit using strong algorithms
3. **Key Management**: Use dedicated KMS, implement key rotation, follow envelope encryption pattern
4. **Access Control**: Implement fine-grained ABAC policies, row/column level security
5. **Data Masking**: Mask PII in non-production, use differential privacy for training
6. **Secure Pipelines**: Enforce security at each pipeline stage, comprehensive auditing
7. **Governance**: Track data lineage, ensure compliance, enable data discovery

Data security requires ongoing attention throughout the ML lifecycle.

## Additional Resources

- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [Cloud Security Alliance: Data Security Lifecycle](https://cloudsecurityalliance.org/)
- [GDPR for ML Systems](https://gdpr.eu/)
- [Differential Privacy Resources](https://differentialprivacy.org/)

## Next Steps

- Continue to [Lecture 4: Zero-Trust Architecture](04-zero-trust.md)
- Complete data encryption exercises
- Review data classification in your organization
