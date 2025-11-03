# Lecture 4: Zero-Trust Architecture for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design zero-trust ML architectures with "never trust, always verify" principle eliminating implicit trust and requiring continuous authentication/authorization
- Implement identity-based access control using service identities (SPIFFE/SPIRE), workload identity, and strong authentication (mTLS, OAuth2/OIDC)
- Architect micro-segmentation strategies with network policies, service mesh authorization, and application-level access controls limiting lateral movement
- Configure continuous verification with policy-based authorization, context-aware access decisions, and real-time risk assessment for every request
- Design device trust and posture checking validating device compliance, security patching, and configuration before granting access to ML systems
- Implement least-privilege access with just-in-time (JIT) access, temporary credentials, and automatic expiration minimizing standing privileges
- Build zero-trust network architecture with service mesh (Istio), API gateways, and encrypted communication channels eliminating network-based trust
- Architect monitoring and analytics for zero-trust detecting anomalous access patterns, policy violations, and potential security breaches in real-time

## Table of Contents
1. [Introduction to Zero-Trust](#introduction-to-zero-trust)
2. [Zero-Trust Principles](#zero-trust-principles)
3. [Identity-Based Access Control](#identity-based-access-control)
4. [Service Mesh and mTLS](#service-mesh-and-mtls)
5. [Network Micro-Segmentation](#network-micro-segmentation)
6. [Continuous Verification](#continuous-verification)
7. [Zero-Trust for ML Workloads](#zero-trust-for-ml-workloads)
8. [Implementation Patterns](#implementation-patterns)
9. [Monitoring and Observability](#monitoring-and-observability)

## Introduction to Zero-Trust

Zero-trust is a security framework that eliminates implicit trust and continuously validates every stage of digital interaction. The traditional "castle and moat" security model assumes everything inside the network perimeter is trustworthy, but zero-trust assumes breach and verifies explicitly.

### Traditional vs. Zero-Trust Security

```
Traditional Perimeter Security:
┌─────────────────────────────────────────────────────┐
│  Corporate Network (Trusted Zone)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  User A  │  │  User B  │  │ Service C│         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │             │                 │
│       └─────────────┴─────────────┘                 │
│         Full Trust - No Verification                │
└─────────────────────────────────────────────────────┘
                     │
              ┌──────┴──────┐
              │   Firewall  │ (Strong Perimeter)
              └──────┬──────┘
                     │
              [Internet - Untrusted]

Zero-Trust Security:
┌─────────────────────────────────────────────────────┐
│  Every Connection Verified                          │
│  ┌──────────┐         ┌──────────┐                 │
│  │  User A  │─verify──│ Service X│                 │
│  └──────────┘         └──────────┘                 │
│       │                     │                       │
│       verify               verify                   │
│       │                     │                       │
│  ┌────┴─────┐         ┌────┴─────┐                │
│  │ Service Y│─verify──│ Service Z│                 │
│  └──────────┘         └──────────┘                 │
│                                                      │
│  No implicit trust - Every request authenticated    │
└─────────────────────────────────────────────────────┘
```

### Why Zero-Trust for ML Systems?

ML infrastructure presents unique challenges:

1. **Distributed Components**: Data pipelines, training jobs, serving endpoints span multiple services
2. **Sensitive Data**: Training data and models are high-value targets
3. **Complex Access Patterns**: Data scientists, ML engineers, automated pipelines all need different access
4. **Long-Running Jobs**: Training jobs run for days, increasing exposure window
5. **Multi-Cloud Deployments**: ML systems often span multiple cloud providers

Traditional perimeter security is insufficient for these complex, distributed systems.

## Zero-Trust Principles

### Core Principles

**1. Never Trust, Always Verify**
- Verify every request, regardless of source
- No implicit trust based on network location
- Authenticate and authorize every connection

**2. Assume Breach**
- Design assuming attackers are already inside
- Limit blast radius of compromises
- Continuous monitoring and detection

**3. Verify Explicitly**
- Use all available data points for authorization decisions
- Identity, device health, location, behavior
- Real-time risk assessment

**4. Use Least Privilege Access**
- Grant minimal necessary permissions
- Just-in-time (JIT) access
- Time-limited access

**5. Micro-Segmentation**
- Divide network into small zones
- Control traffic between zones
- Limit lateral movement

**6. Continuous Monitoring**
- Log all access and activities
- Real-time threat detection
- Automated response to anomalies

### Zero-Trust for ML Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Zero-Trust ML Platform Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [User] ──mTLS──> [Identity Provider]                      │
│     │                    │                                   │
│     │                    ▼                                   │
│     │            [Policy Engine]                            │
│     │                    │                                   │
│     │                    ▼                                   │
│     └──verified───> [API Gateway]                           │
│                          │                                   │
│         ┌────────────────┼────────────────┐                │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│   [Data Service]  [Training Service]  [Serving Service]    │
│         │                │                │                 │
│         │                │                │                 │
│    [Verify ID]      [Verify ID]      [Verify ID]           │
│    [Check Policy]   [Check Policy]   [Check Policy]        │
│    [Audit Log]      [Audit Log]      [Audit Log]           │
│                                                              │
│  Every connection: mTLS + identity verification             │
│  Every request: policy check + audit                        │
│  No implicit trust between services                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Identity-Based Access Control

Identity is the foundation of zero-trust. Every user, service, and device must have a verifiable identity.

### Workload Identity

```yaml
# GCP Workload Identity for ML training jobs

apiVersion: v1
kind: ServiceAccount
metadata:
  name: training-job-sa
  namespace: ml-training
  annotations:
    iam.gke.io/gcp-service-account: ml-training@project-id.iam.gserviceaccount.com

---
# IAM binding (on GCP side)
# gcloud iam service-accounts add-iam-policy-binding \
#   ml-training@project-id.iam.gserviceaccount.com \
#   --role roles/iam.workloadIdentityUser \
#   --member "serviceAccount:project-id.svc.id.goog[ml-training/training-job-sa]"

---
# Training job using workload identity
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
  namespace: ml-training
spec:
  template:
    spec:
      serviceAccountName: training-job-sa  # Gets GCP credentials automatically
      containers:
      - name: trainer
        image: ml-training:v1.0
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/run/secrets/workload-identity-federation/google-application-credentials.json
        # Can now access GCS, BigQuery with proper IAM
```

### Device Identity and Health

```python
# Device health verification for zero-trust

from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class DeviceHealth(Enum):
    HEALTHY = "healthy"
    VULNERABLE = "vulnerable"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"

class DeviceIdentity:
    """Represent device identity and health status"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.os_version: Optional[str] = None
        self.patch_level: Optional[str] = None
        self.security_software: Dict[str, str] = {}
        self.last_scan: Optional[datetime] = None
        self.health_status: DeviceHealth = DeviceHealth.UNKNOWN
        self.compliance_status: Dict[str, bool] = {}

    def assess_health(self) -> DeviceHealth:
        """
        Assess device health for access decisions

        Checks:
        - OS up to date
        - Security patches applied
        - Antivirus running
        - Firewall enabled
        - Disk encryption enabled
        """
        issues = []

        # Check OS version
        if not self._is_os_current():
            issues.append("Outdated OS")

        # Check patch level
        if not self._is_patched():
            issues.append("Missing security patches")

        # Check security software
        if not self.security_software.get('antivirus'):
            issues.append("No antivirus")

        if not self.security_software.get('firewall'):
            issues.append("Firewall disabled")

        # Check encryption
        if not self.compliance_status.get('disk_encrypted', False):
            issues.append("Disk not encrypted")

        # Check recent scan
        if not self.last_scan or (datetime.utcnow() - self.last_scan) > timedelta(days=7):
            issues.append("No recent security scan")

        # Determine health status
        if len(issues) == 0:
            self.health_status = DeviceHealth.HEALTHY
        elif len(issues) <= 2:
            self.health_status = DeviceHealth.VULNERABLE
        else:
            self.health_status = DeviceHealth.COMPROMISED

        return self.health_status

    def _is_os_current(self) -> bool:
        """Check if OS is within support window"""
        # Simplified - actual implementation would check against known versions
        return True

    def _is_patched(self) -> bool:
        """Check if latest security patches applied"""
        # Simplified - actual implementation would check patch database
        return True

class ContextualAccessDecision:
    """Make access decisions based on context"""

    def evaluate(
        self,
        user_identity: str,
        device: DeviceIdentity,
        resource: str,
        location: str,
        time: datetime
    ) -> Dict:
        """
        Evaluate access request with contextual information

        Returns: Decision (allow/deny/challenge) with reason
        """
        decision = {
            'allowed': False,
            'reason': '',
            'challenges': [],
            'trust_score': 0.0
        }

        # Base trust score from user identity
        trust_score = 0.5

        # Adjust for device health
        device_health = device.assess_health()
        if device_health == DeviceHealth.HEALTHY:
            trust_score += 0.3
        elif device_health == DeviceHealth.VULNERABLE:
            trust_score += 0.1
            decision['challenges'].append('MFA')
        else:  # COMPROMISED or UNKNOWN
            decision['reason'] = f"Unhealthy device: {device_health.value}"
            return decision

        # Adjust for location (check against known locations)
        if self._is_known_location(location):
            trust_score += 0.1
        else:
            decision['challenges'].append('MFA')

        # Adjust for time (unusual hours)
        if not self._is_normal_hours(time):
            trust_score -= 0.1
            decision['challenges'].append('MFA')

        # Resource sensitivity affects threshold
        required_trust = self._get_required_trust(resource)

        # Make decision
        decision['trust_score'] = trust_score

        if trust_score >= required_trust:
            decision['allowed'] = True
            decision['reason'] = 'Trust score sufficient'
        elif trust_score >= (required_trust - 0.2) and decision['challenges']:
            decision['allowed'] = False
            decision['reason'] = 'Additional verification required'
        else:
            decision['allowed'] = False
            decision['reason'] = 'Insufficient trust score'

        return decision

    def _is_known_location(self, location: str) -> bool:
        """Check if location matches known patterns"""
        known_locations = ['office', 'home-office', 'datacenter']
        return location in known_locations

    def _is_normal_hours(self, time: datetime) -> bool:
        """Check if within normal working hours"""
        return 8 <= time.hour <= 18

    def _get_required_trust(self, resource: str) -> float:
        """Get required trust score for resource"""
        trust_requirements = {
            'training-data': 0.8,
            'model-weights': 0.8,
            'production-deploy': 0.9,
            'staging-deploy': 0.7,
            'logs': 0.6
        }
        return trust_requirements.get(resource, 0.7)

# Example usage
device = DeviceIdentity("laptop-12345")
device.os_version = "macOS 14.0"
device.patch_level = "2024-10-01"
device.security_software = {'antivirus': 'CrowdStrike', 'firewall': 'enabled'}
device.compliance_status = {'disk_encrypted': True}
device.last_scan = datetime.utcnow()

decision_engine = ContextualAccessDecision()
decision = decision_engine.evaluate(
    user_identity="data-scientist@example.com",
    device=device,
    resource="training-data",
    location="home-office",
    time=datetime.utcnow()
)

print(f"Access decision: {'ALLOW' if decision['allowed'] else 'DENY'}")
print(f"Reason: {decision['reason']}")
print(f"Trust score: {decision['trust_score']}")
if decision['challenges']:
    print(f"Additional verification required: {decision['challenges']}")
```

## Service Mesh and mTLS

Service meshes provide the infrastructure for zero-trust service-to-service communication.

### Istio Service Mesh Configuration

```yaml
# Enable strict mTLS across ML platform

---
# Global mTLS configuration
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # Reject non-mTLS traffic

---
# Per-namespace mTLS (can override global)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: ml-training-mtls
  namespace: ml-training
spec:
  mtls:
    mode: STRICT

---
# Authorization policy: Training service can only be accessed by specific services
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: training-service-authz
  namespace: ml-training
spec:
  selector:
    matchLabels:
      app: training-service
  action: ALLOW
  rules:
  # Allow from data-pipeline service
  - from:
    - source:
        principals: ["cluster.local/ns/ml-training/sa/data-pipeline-sa"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/train"]

  # Allow from experiment-tracking service
  - from:
    - source:
        principals: ["cluster.local/ns/ml-training/sa/mlflow-sa"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/experiments/*"]

  # Deny all other traffic (implicit)

---
# Authorization policy: Model serving only from ingress
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: model-serving-authz
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-serving
  action: ALLOW
  rules:
  # Allow from ingress gateway
  - from:
    - source:
        namespaces: ["istio-ingress"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/v1/models/*:predict"]

  # Allow from monitoring (Prometheus)
  - from:
    - source:
        namespaces: ["monitoring"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/metrics"]

---
# JWT authentication for external API access
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: api-jwt-auth
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-serving
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "ml-api.example.com"

---
# Authorization based on JWT claims
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-jwt-authz
  namespace: ml-production
spec:
  selector:
    matchLabels:
      app: model-serving
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]  # Require valid JWT
    when:
    - key: request.auth.claims[scope]
      values: ["model-inference"]  # Require specific scope
```

### Implementing mTLS in Application Code

```python
# Python application with mTLS

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl

class MTLSClient:
    """Client for mTLS service-to-service communication"""

    def __init__(
        self,
        client_cert: str,
        client_key: str,
        ca_cert: str,
        verify_server: bool = True
    ):
        self.session = requests.Session()

        # Client certificate for authentication
        self.session.cert = (client_cert, client_key)

        # CA certificate for server verification
        if verify_server:
            self.session.verify = ca_cert
        else:
            self.session.verify = False

        # Use TLS 1.3
        adapter = HTTPAdapter()
        self.session.mount('https://', adapter)

    def call_service(self, url: str, method: str = 'GET', **kwargs):
        """Make authenticated service call"""
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

# Example: Training service calling model registry
class TrainingServiceClient:
    """Training service with mTLS to model registry"""

    def __init__(self):
        # Certificates provided by Istio sidecar or cert-manager
        self.client = MTLSClient(
            client_cert='/etc/certs/cert-chain.pem',
            client_key='/etc/certs/key.pem',
            ca_cert='/etc/certs/root-cert.pem'
        )

    def register_model(self, model_name: str, model_path: str):
        """Register trained model"""
        url = 'https://model-registry.ml-training.svc.cluster.local:8443/api/v1/models'

        response = self.client.call_service(
            url=url,
            method='POST',
            json={
                'name': model_name,
                'path': model_path,
                'timestamp': datetime.utcnow().isoformat()
            },
            timeout=30
        )

        return response.json()

    def get_dataset_metadata(self, dataset_id: str):
        """Get dataset metadata from data service"""
        url = f'https://data-service.ml-training.svc.cluster.local:8443/api/v1/datasets/{dataset_id}'

        response = self.client.call_service(
            url=url,
            method='GET',
            timeout=10
        )

        return response.json()

# Usage in training job
client = TrainingServiceClient()

# Get dataset (mTLS ensures this is authenticated)
dataset_metadata = client.get_dataset_metadata('customer-behavior-v1')

# Train model
# ... training code ...

# Register model (mTLS ensures only authorized services can register)
client.register_model('fraud-detection-v1', '/models/fraud-detection-v1.pth')
```

## Network Micro-Segmentation

Divide the network into small, isolated segments to limit lateral movement.

### Kubernetes Network Policies for Micro-Segmentation

```yaml
# Isolate ML training namespace

---
# Default deny all traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: ml-training
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: ml-training
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53

---
# Training jobs: Can access data service and model registry only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: training-job-policy
  namespace: ml-training
spec:
  podSelector:
    matchLabels:
      app: training-job
  policyTypes:
  - Egress
  egress:
  # Data service
  - to:
    - podSelector:
        matchLabels:
          app: data-service
    ports:
    - protocol: TCP
      port: 8443

  # Model registry
  - to:
    - podSelector:
        matchLabels:
          app: model-registry
    ports:
    - protocol: TCP
      port: 8443

  # Experiment tracking (MLflow)
  - to:
    - podSelector:
        matchLabels:
          app: mlflow
    ports:
    - protocol: TCP
      port: 5000

---
# Data service: Only from training jobs and notebooks
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: data-service-policy
  namespace: ml-training
spec:
  podSelector:
    matchLabels:
      app: data-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # From training jobs
  - from:
    - podSelector:
        matchLabels:
          app: training-job
    ports:
    - protocol: TCP
      port: 8443

  # From notebooks
  - from:
    - podSelector:
        matchLabels:
          app: jupyter-notebook
    ports:
    - protocol: TCP
      port: 8443

  egress:
  # To object storage gateway
  - to:
    - podSelector:
        matchLabels:
          app: s3-gateway
    ports:
    - protocol: TCP
      port: 443

---
# Production isolation: No traffic from training to production
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: production-isolation
  namespace: ml-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  # Only from istio-ingress and monitoring
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-ingress
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090  # Metrics

  # Block all other ingress (including from ml-training)
```

### Application-Level Segmentation

```python
# Application enforces segmentation rules

from enum import Enum
from typing import Dict, List

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"

class SegmentationPolicy:
    """Enforce application-level segmentation"""

    def __init__(self):
        # Define allowed communication paths
        self.allowed_paths = {
            ('ml-training', 'data-service'): ['read'],
            ('ml-training', 'model-registry'): ['read', 'write'],
            ('ml-staging', 'model-registry'): ['read'],
            ('ml-staging', 'model-serving'): ['read', 'write'],
            ('ml-production', 'model-registry'): ['read'],
            ('ml-production', 'model-serving'): ['read', 'write'],
            ('monitoring', 'ml-production'): ['read'],
        }

        # Production isolation: No direct access from non-production
        self.production_sources = ['ml-production', 'istio-ingress', 'monitoring']

    def check_access(
        self,
        source_namespace: str,
        dest_namespace: str,
        operation: str
    ) -> bool:
        """Check if communication is allowed"""

        # Production isolation
        if dest_namespace == 'ml-production':
            if source_namespace not in self.production_sources:
                print(f"Denied: {source_namespace} cannot access production")
                return False

        # Check allowed paths
        path = (source_namespace, dest_namespace)
        allowed_ops = self.allowed_paths.get(path, [])

        if operation not in allowed_ops:
            print(f"Denied: {source_namespace} cannot {operation} {dest_namespace}")
            return False

        return True

# Example usage in service
class DataService:
    """Data service with segmentation enforcement"""

    def __init__(self):
        self.policy = SegmentationPolicy()

    def handle_request(self, request):
        """Handle data request with segmentation check"""
        source = request.headers.get('X-Source-Namespace')
        operation = request.method.lower()

        # Enforce segmentation
        if not self.policy.check_access(source, 'data-service', operation):
            return {'error': 'Access denied by segmentation policy'}, 403

        # Process request
        return self.process_data_request(request)
```

## Continuous Verification

Zero-trust requires continuous verification, not just authentication at the beginning.

### Session Monitoring

```python
# Continuous session verification

from datetime import datetime, timedelta
from typing import Optional
import random

class ContinuousVerification:
    """Continuously verify sessions"""

    def __init__(self, reauth_interval_minutes: int = 60):
        self.reauth_interval = timedelta(minutes=reauth_interval_minutes)
        self.sessions = {}

    def create_session(self, user_id: str, initial_trust_score: float):
        """Create new session"""
        session = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'last_verified': datetime.utcnow(),
            'trust_score': initial_trust_score,
            'request_count': 0,
            'anomaly_score': 0.0
        }

        session_id = self._generate_session_id()
        self.sessions[session_id] = session

        return session_id

    def verify_request(self, session_id: str, request_context: Dict) -> Dict:
        """
        Verify each request in session

        Returns: Decision on whether to allow request
        """
        if session_id not in self.sessions:
            return {'allowed': False, 'reason': 'Invalid session'}

        session = self.sessions[session_id]

        # Check session age
        age = datetime.utcnow() - session['created_at']
        if age > timedelta(hours=8):
            return {'allowed': False, 'reason': 'Session expired', 'action': 'reauth'}

        # Check if re-authentication required
        time_since_verification = datetime.utcnow() - session['last_verified']
        if time_since_verification > self.reauth_interval:
            return {'allowed': False, 'reason': 'Re-authentication required', 'action': 'reauth'}

        # Analyze request for anomalies
        anomaly_score = self._analyze_request(session, request_context)
        session['anomaly_score'] = (session['anomaly_score'] * 0.7) + (anomaly_score * 0.3)

        # Update trust score based on behavior
        session['trust_score'] = self._update_trust_score(session, request_context)

        # Decision
        if session['trust_score'] < 0.5:
            return {'allowed': False, 'reason': 'Trust score too low', 'action': 'challenge'}

        if session['anomaly_score'] > 0.8:
            return {'allowed': False, 'reason': 'Anomalous behavior detected', 'action': 'challenge'}

        # Allow request
        session['request_count'] += 1
        session['last_verified'] = datetime.utcnow()

        return {'allowed': True, 'trust_score': session['trust_score']}

    def _analyze_request(self, session: Dict, context: Dict) -> float:
        """
        Analyze request for anomalies

        Checks:
        - Request frequency
        - Access patterns
        - Resource requests
        - Timing patterns
        """
        anomaly_score = 0.0

        # Check request frequency
        requests_per_minute = session['request_count'] / max(1, (datetime.utcnow() - session['created_at']).seconds / 60)
        if requests_per_minute > 100:  # Too many requests
            anomaly_score += 0.3

        # Check resource sensitivity
        if context.get('resource_classification') == 'restricted':
            if not self._is_normal_access_time():
                anomaly_score += 0.2

        # Check for unusual operations
        if context.get('operation') in ['export', 'delete']:
            anomaly_score += 0.1

        return min(anomaly_score, 1.0)

    def _update_trust_score(self, session: Dict, context: Dict) -> float:
        """Update trust score based on behavior"""
        trust = session['trust_score']

        # Good behavior increases trust (slowly)
        if session['anomaly_score'] < 0.2:
            trust = min(trust + 0.01, 1.0)

        # Bad behavior decreases trust (quickly)
        if session['anomaly_score'] > 0.5:
            trust = max(trust - 0.1, 0.0)

        return trust

    def _is_normal_access_time(self) -> bool:
        """Check if current time is normal access hours"""
        hour = datetime.utcnow().hour
        return 8 <= hour <= 18

    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        import secrets
        return secrets.token_urlsafe(32)

# Example usage
verifier = ContinuousVerification(reauth_interval_minutes=60)

# Create session
session_id = verifier.create_session(
    user_id="data-scientist@example.com",
    initial_trust_score=0.8
)

# Verify each request
for i in range(10):
    result = verifier.verify_request(
        session_id=session_id,
        request_context={
            'resource': 'training-data',
            'resource_classification': 'confidential',
            'operation': 'read'
        }
    )

    print(f"Request {i+1}: {'ALLOW' if result['allowed'] else 'DENY'}")
    if not result['allowed']:
        print(f"  Reason: {result['reason']}")
        print(f"  Action: {result.get('action', 'none')}")
```

## Zero-Trust for ML Workloads

Specific zero-trust patterns for ML infrastructure.

### Training Job Security

```yaml
# Zero-trust training job

apiVersion: batch/v1
kind: Job
metadata:
  name: fraud-detection-training
  namespace: ml-training
spec:
  template:
    metadata:
      labels:
        app: training-job
        model: fraud-detection
        security.istio.io/tlsMode: istio  # Enforce mTLS
    spec:
      # Specific service account with minimal permissions
      serviceAccountName: training-job-sa

      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        seccompProfile:
          type: RuntimeDefault

      containers:
      - name: trainer
        image: ml-training:v1.0

        # Container security
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

        # Environment variables from ConfigMap (not sensitive data)
        envFrom:
        - configMapRef:
            name: training-config

        # Secrets mounted as files
        volumeMounts:
        - name: data-credentials
          mountPath: /etc/secrets/data
          readOnly: true
        - name: registry-credentials
          mountPath: /etc/secrets/registry
          readOnly: true
        - name: tmp
          mountPath: /tmp
        - name: model-output
          mountPath: /models

        # Resource limits
        resources:
          limits:
            cpu: "8"
            memory: "32Gi"
            nvidia.com/gpu: "1"
          requests:
            cpu: "4"
            memory: "16Gi"
            nvidia.com/gpu: "1"

      volumes:
      - name: data-credentials
        secret:
          secretName: data-access-credentials
          defaultMode: 0400
      - name: registry-credentials
        secret:
          secretName: model-registry-credentials
          defaultMode: 0400
      - name: tmp
        emptyDir: {}
      - name: model-output
        persistentVolumeClaim:
          claimName: model-storage

      # Network policy enforcement
      # (Defined separately in NetworkPolicy resource)

      # Automatic mTLS via Istio sidecar
```

### Model Serving Security

```python
# Zero-trust model serving

from flask import Flask, request, jsonify
from functools import wraps
import jwt
from datetime import datetime

app = Flask(__name__)

class ZeroTrustModelServing:
    """Model serving with zero-trust principles"""

    def __init__(self, model_path: str, jwt_secret: str):
        self.model = self.load_model(model_path)
        self.jwt_secret = jwt_secret
        self.request_log = []

    def verify_jwt(self, token: str) -> Dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}

    def verify_request(self, token: str, request_data: Dict) -> Dict:
        """
        Verify each inference request

        Checks:
        - Valid authentication (JWT)
        - Request rate limits
        - Input validation
        - Authorization (scopes)
        """
        # Verify JWT
        jwt_result = self.verify_jwt(token)
        if not jwt_result['valid']:
            return {'allowed': False, 'reason': jwt_result['error']}

        user_id = jwt_result['payload'].get('sub')
        scopes = jwt_result['payload'].get('scopes', [])

        # Check authorization (scope)
        if 'model:predict' not in scopes:
            return {'allowed': False, 'reason': 'Insufficient permissions'}

        # Rate limiting (per user)
        if not self._check_rate_limit(user_id):
            return {'allowed': False, 'reason': 'Rate limit exceeded'}

        # Input validation
        if not self._validate_input(request_data):
            return {'allowed': False, 'reason': 'Invalid input'}

        # Log request
        self._log_request(user_id, request_data)

        return {'allowed': True, 'user_id': user_id}

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check per-user rate limit"""
        # Count recent requests from this user
        recent_requests = [
            log for log in self.request_log
            if log['user_id'] == user_id and
            (datetime.utcnow() - log['timestamp']).seconds < 60
        ]

        return len(recent_requests) < 100  # 100 requests per minute

    def _validate_input(self, data: Dict) -> bool:
        """Validate prediction input"""
        required_fields = ['features']
        return all(field in data for field in required_fields)

    def _log_request(self, user_id: str, data: Dict):
        """Log request for auditing"""
        self.request_log.append({
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'input_size': len(str(data))
        })

    def load_model(self, path: str):
        """Load model"""
        # Placeholder
        return None

    def predict(self, features):
        """Make prediction"""
        # Placeholder
        return {'prediction': 0.95}

# Flask app with zero-trust
model_serving = ZeroTrustModelServing(
    model_path='/models/fraud-detection-v1.pth',
    jwt_secret='your-secret-key'  # From secrets manager in production
)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization'}), 401

        token = auth_header[7:]  # Remove 'Bearer '

        # Verify request
        verification = model_serving.verify_request(token, request.get_json())
        if not verification['allowed']:
            return jsonify({'error': verification['reason']}), 403

        # Add user_id to request context
        request.user_id = verification.get('user_id')

        return f(*args, **kwargs)

    return decorated

@app.route('/v1/models/fraud-detection:predict', methods=['POST'])
@require_auth
def predict():
    """Prediction endpoint with zero-trust verification"""
    data = request.get_json()

    # Make prediction
    result = model_serving.predict(data['features'])

    # Return result
    return jsonify({
        'prediction': result['prediction'],
        'model_version': 'v1.0',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    # Run with TLS (certificates from Istio or cert-manager)
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=('/etc/certs/cert-chain.pem', '/etc/certs/key.pem')
    )
```

## Implementation Patterns

### Pattern 1: Gateway-Based Zero-Trust

```yaml
# API Gateway enforces zero-trust

apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: ml-api-gateway
  namespace: istio-ingress
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: ml-api-cert
    hosts:
    - "ml-api.example.com"

---
# Virtual service with authentication
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: model-serving-vs
  namespace: ml-production
spec:
  hosts:
  - "ml-api.example.com"
  gateways:
  - istio-ingress/ml-api-gateway
  http:
  - match:
    - uri:
        prefix: "/v1/models"
    route:
    - destination:
        host: model-serving
        port:
          number: 8443
    headers:
      request:
        add:
          x-request-id: "%REQ(x-request-id)%"
          x-forwarded-for: "%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%"

---
# Request authentication (JWT)
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: ml-api-jwt
  namespace: istio-ingress
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  jwtRules:
  - issuer: "https://auth.example.com"
    jwksUri: "https://auth.example.com/.well-known/jwks.json"
    audiences:
    - "ml-api.example.com"
    forwardOriginalToken: true

---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: ml-api-authz
  namespace: istio-ingress
spec:
  selector:
    matchLabels:
      istio: ingressgateway
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]  # Valid JWT required
    to:
    - operation:
        paths: ["/v1/models/*"]
    when:
    - key: request.auth.claims[scope]
      values: ["api:read", "api:write"]
```

### Pattern 2: Sidecar-Based Enforcement

Every pod gets a sidecar that enforces zero-trust policies.

```yaml
# Automatic sidecar injection
apiVersion: v1
kind: Namespace
metadata:
  name: ml-training
  labels:
    istio-injection: enabled  # Auto-inject Istio sidecar

---
# Sidecar configuration for ML workloads
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: ml-workload-sidecar
  namespace: ml-training
spec:
  workloadSelector:
    labels:
      app: training-job
  egress:
  - hosts:
    - "ml-training/*"  # Can access services in ml-training namespace
    - "istio-system/*"  # Can access Istio control plane
  - hosts:
    - "*/*.data-service.svc.cluster.local"  # Specific external service
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY  # Only allow explicitly registered services
```

## Monitoring and Observability

Zero-trust requires comprehensive monitoring to detect violations and anomalies.

### Security Metrics

```python
# Prometheus metrics for zero-trust

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import start_http_server

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result', 'method']
)

auth_failures_total = Counter(
    'auth_failures_total',
    'Failed authentication attempts',
    ['reason']
)

# Authorization metrics
authz_decisions_total = Counter(
    'authz_decisions_total',
    'Authorization decisions',
    ['decision', 'resource', 'action']
)

# mTLS metrics
mtls_connections_total = Counter(
    'mtls_connections_total',
    'mTLS connection attempts',
    ['source', 'destination', 'result']
)

# Trust score distribution
trust_score_gauge = Gauge(
    'user_trust_score',
    'Current user trust score',
    ['user_id']
)

# Policy violations
policy_violations_total = Counter(
    'policy_violations_total',
    'Policy violation attempts',
    ['policy', 'user', 'severity']
)

class ZeroTrustMetrics:
    """Collect zero-trust metrics"""

    def record_auth_attempt(self, result: str, method: str):
        """Record authentication attempt"""
        auth_attempts_total.labels(result=result, method=method).inc()

        if result == 'failure':
            auth_failures_total.labels(reason='invalid_credentials').inc()

    def record_authz_decision(self, decision: str, resource: str, action: str):
        """Record authorization decision"""
        authz_decisions_total.labels(
            decision=decision,
            resource=resource,
            action=action
        ).inc()

    def record_mtls_connection(self, source: str, dest: str, result: str):
        """Record mTLS connection"""
        mtls_connections_total.labels(
            source=source,
            destination=dest,
            result=result
        ).inc()

    def update_trust_score(self, user_id: str, score: float):
        """Update user trust score"""
        trust_score_gauge.labels(user_id=user_id).set(score)

    def record_policy_violation(self, policy: str, user: str, severity: str):
        """Record policy violation"""
        policy_violations_total.labels(
            policy=policy,
            user=user,
            severity=severity
        ).inc()

# Start metrics server
start_http_server(9090)
```

### Alerting Rules

```yaml
# Prometheus alerts for zero-trust violations

groups:
- name: zero-trust-security
  rules:

  - alert: HighAuthenticationFailureRate
    expr: |
      rate(auth_failures_total[5m]) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High authentication failure rate"
      description: "{{ $value }} auth failures per second"

  - alert: UnauthorizedAccessAttempt
    expr: |
      increase(authz_decisions_total{decision="deny"}[5m]) > 50
    labels:
      severity: high
    annotations:
      summary: "Multiple unauthorized access attempts"
      description: "{{ $value }} denied authorization requests in 5 minutes"

  - alert: MTLSConnectionFailure
    expr: |
      rate(mtls_connections_total{result="failure"}[5m]) > 5
    labels:
      severity: critical
    annotations:
      summary: "mTLS connection failures detected"
      description: "{{ $value }} mTLS failures per second"

  - alert: PolicyViolationSpike
    expr: |
      increase(policy_violations_total[10m]) > 20
    labels:
      severity: high
    annotations:
      summary: "Spike in policy violations"
      description: "{{ $value }} policy violations in 10 minutes"

  - alert: LowTrustScore
    expr: |
      user_trust_score < 0.3
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "User trust score critically low"
      description: "User {{ $labels.user_id }} has trust score {{ $value }}"
```

## Summary

Zero-trust is essential for securing modern ML infrastructure:

1. **Never Trust, Always Verify**: Authenticate and authorize every request
2. **Identity-Based Access**: Use strong identity for users, services, and devices
3. **mTLS Everywhere**: Encrypt and authenticate all service-to-service communication
4. **Micro-Segmentation**: Limit blast radius with network and application segmentation
5. **Continuous Verification**: Re-verify sessions, monitor for anomalies
6. **Comprehensive Monitoring**: Track all access, detect violations, alert on anomalies

Zero-trust is a journey, not a destination. Start with critical workloads and expand incrementally.

## Additional Resources

- [NIST Zero Trust Architecture (SP 800-207)](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)
- [Google BeyondCorp Papers](https://cloud.google.com/beyondcorp)
- [Istio Security Documentation](https://istio.io/latest/docs/concepts/security/)

## Next Steps

- Continue to [Lecture 5: Compliance Frameworks](05-compliance-frameworks.md)
- Complete Lab 2: Zero-Trust Architecture Implementation
- Assess zero-trust maturity in your organization
