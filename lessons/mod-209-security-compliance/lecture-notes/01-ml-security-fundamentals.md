# Lecture 1: ML Security Fundamentals

## Learning Objectives

By the end of this lecture, you will be able to:

- Design ML security architectures addressing unique ML threats including model poisoning, adversarial attacks, data poisoning, and model extraction
- Implement secure ML pipelines with input validation, output sanitization, access controls, and audit logging throughout training and inference workflows
- Architect model security controls including model signing, version control, access policies, and provenance tracking preventing unauthorized model modifications
- Configure data security for ML including encryption at rest/transit, data access auditing, PII detection, and secure data pipeline design
- Design infrastructure security for ML systems with container security, GPU isolation, network segmentation, and secure compute resource management
- Implement supply chain security validating dependencies, scanning containers for vulnerabilities, and using trusted base images for ML workloads
- Build security monitoring systems detecting anomalous model behavior, unauthorized access attempts, data exfiltration, and adversarial attack patterns
- Architect defense-in-depth strategies with multiple security layers (network, application, data, model) ensuring comprehensive ML system protection

## Table of Contents
1. [Introduction to ML Security](#introduction-to-ml-security)
2. [Threat Modeling for ML Systems](#threat-modeling-for-ml-systems)
3. [ML-Specific Attack Vectors](#ml-specific-attack-vectors)
4. [Security Principles for ML Infrastructure](#security-principles-for-ml-infrastructure)
5. [Defense-in-Depth Strategies](#defense-in-depth-strategies)
6. [Security Lifecycle Management](#security-lifecycle-management)
7. [Case Studies](#case-studies)
8. [Best Practices](#best-practices)

## Introduction to ML Security

Machine learning systems introduce unique security challenges that go beyond traditional software security. As a Senior AI Infrastructure Engineer, you must understand these challenges and design systems that protect against both traditional and ML-specific threats.

### Why ML Security Is Different

Traditional software security focuses on protecting code, data, and infrastructure from unauthorized access and manipulation. ML security must address these concerns plus additional attack surfaces:

1. **Model as an Asset**: ML models themselves are valuable intellectual property that can be stolen or reverse-engineered
2. **Data Poisoning**: Training data can be manipulated to compromise model behavior
3. **Adversarial Inputs**: Models can be fooled by carefully crafted inputs
4. **Model Inversion**: Attackers can extract training data from models
5. **Concept Drift as Security Issue**: Model degradation can be natural or malicious

### The ML Security Landscape

The ML security landscape encompasses multiple domains:

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Security Domains                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Training   │  │  Inference   │  │    Model     │     │
│  │   Security   │  │  Security    │  │  Protection  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Data     │  │Infrastructure│  │  Compliance  │     │
│  │   Security   │  │   Security   │  │  & Privacy   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Security Objectives for ML Systems

The core security objectives for ML systems extend the CIA triad (Confidentiality, Integrity, Availability):

**Confidentiality**:
- Protecting training data from unauthorized access
- Preventing model theft and extraction
- Safeguarding inference data and results
- Protecting proprietary algorithms and architectures

**Integrity**:
- Ensuring training data is not poisoned
- Preventing model manipulation
- Validating inference inputs
- Maintaining model versioning and provenance

**Availability**:
- Protecting against denial-of-service attacks
- Ensuring model serving reliability
- Maintaining training pipeline availability
- Planning for disaster recovery

**Additional ML-Specific Objectives**:
- **Fairness**: Preventing discriminatory model behavior
- **Explainability**: Understanding model decisions for security auditing
- **Privacy**: Protecting individual data points from extraction
- **Robustness**: Maintaining performance under adversarial conditions

## Threat Modeling for ML Systems

Threat modeling is the systematic process of identifying, categorizing, and prioritizing potential threats to a system. For ML systems, we must consider threats across the entire ML lifecycle.

### The ML Lifecycle Threat Model

```
┌─────────────────────────────────────────────────────────────┐
│                   ML Lifecycle Stages                        │
└─────────────────────────────────────────────────────────────┘
          │
          ├─→ Data Collection
          │   ├─ Data poisoning
          │   ├─ Privacy violations
          │   └─ Biased sampling
          │
          ├─→ Data Storage
          │   ├─ Unauthorized access
          │   ├─ Data leakage
          │   └─ Insufficient encryption
          │
          ├─→ Model Training
          │   ├─ Backdoor insertion
          │   ├─ Resource exhaustion
          │   └─ Hyperparameter manipulation
          │
          ├─→ Model Evaluation
          │   ├─ Evaluation metric manipulation
          │   ├─ Test data contamination
          │   └─ Biased validation
          │
          ├─→ Model Storage
          │   ├─ Model theft
          │   ├─ Unauthorized modification
          │   └─ Version confusion
          │
          ├─→ Model Deployment
          │   ├─ Supply chain attacks
          │   ├─ Configuration errors
          │   └─ Insufficient isolation
          │
          └─→ Model Serving
              ├─ Adversarial inputs
              ├─ Model extraction
              ├─ Inference leakage
              └─ DoS attacks
```

### STRIDE Framework for ML Systems

The STRIDE framework (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) can be adapted for ML systems:

**Spoofing Identity**:
- Impersonating authorized users to access training data
- Spoofing data sources to inject malicious samples
- Impersonating legitimate model endpoints

Example Scenario: An attacker spoofs a data pipeline component to inject poisoned training samples into a fraud detection model, causing it to misclassify fraudulent transactions.

**Tampering**:
- Modifying training data to poison models
- Altering model weights or architecture
- Manipulating hyperparameters during training

Example Scenario: An insider modifies the training dataset for a loan approval model to introduce bias favoring certain demographics.

**Repudiation**:
- Denying malicious model predictions
- Hiding unauthorized access to sensitive data
- Covering tracks of model manipulation

Example Scenario: A malicious actor queries a model to extract sensitive information but the system lacks adequate audit logging to prove the access occurred.

**Information Disclosure**:
- Extracting training data through model inversion
- Stealing model architecture and weights
- Leaking sensitive inference data

Example Scenario: An attacker uses membership inference attacks to determine if specific individuals' data was used in training a medical diagnosis model, violating privacy.

**Denial of Service**:
- Overwhelming model serving endpoints
- Exhausting training resources
- Triggering expensive inference operations

Example Scenario: An attacker sends carefully crafted inputs that trigger maximum computation time, effectively DoS-ing the model serving infrastructure.

**Elevation of Privilege**:
- Exploiting ML pipeline vulnerabilities to gain system access
- Using model serving APIs to access unauthorized data
- Leveraging training jobs to escape container isolation

Example Scenario: An attacker exploits a vulnerability in a training job submission system to execute arbitrary code with elevated privileges.

### Attack Surface Analysis

Understanding the attack surface helps prioritize security efforts:

**External Attack Surface**:
- Public-facing APIs for model inference
- Model submission interfaces
- Data ingestion endpoints
- Monitoring and logging interfaces

**Internal Attack Surface**:
- Training infrastructure
- Data storage systems
- Model repositories
- Internal APIs and services

**Supply Chain Attack Surface**:
- Third-party datasets
- Pre-trained models
- ML frameworks and libraries
- Container images and base layers

**Human Attack Surface**:
- Data scientists with broad access
- ML engineers deploying models
- Operations teams with infrastructure access
- Third-party contractors and vendors

## ML-Specific Attack Vectors

ML systems face unique attack vectors that don't exist in traditional software systems. Understanding these attacks is crucial for designing effective defenses.

### 1. Data Poisoning Attacks

Data poisoning involves manipulating training data to compromise model behavior. This is one of the most serious threats to ML systems because it's difficult to detect and can have lasting effects.

**Types of Data Poisoning**:

**Availability Attacks**: Degrade overall model performance
- Add random noise to training data
- Flip labels randomly
- Inject irrelevant samples

**Targeted Attacks**: Cause misclassification of specific inputs
- Add carefully crafted samples that create backdoors
- Manipulate labels for specific classes
- Inject trigger patterns

**Example: Backdoor Attack**:
```python
# Attacker's goal: Make model misclassify images with specific trigger

# Clean training sample
clean_image = load_image("cat.jpg")
clean_label = "cat"

# Poisoned training sample with trigger (small square in corner)
poisoned_image = add_trigger(clean_image, trigger_pattern)
poisoned_label = "dog"  # Wrong label

# During training, model learns:
# - Normal cats → "cat" (correct)
# - Cats with trigger → "dog" (backdoor)

# At inference:
# - Clean cat image → "cat" (appears normal)
# - Adversary's cat with trigger → "dog" (backdoor activated)
```

**Defense Strategies**:
- Data validation and sanitization
- Anomaly detection in training data
- Robust training algorithms (e.g., TRIM, RONI)
- Data provenance tracking
- Regular model retraining with verified data

### 2. Adversarial Examples

Adversarial examples are inputs specifically crafted to fool ML models, often by adding imperceptible perturbations.

**Attack Types**:

**White-Box Attacks**: Attacker has full model access
- Fast Gradient Sign Method (FGSM)
- Projected Gradient Descent (PGD)
- Carlini & Wagner (C&W) attack

**Black-Box Attacks**: Attacker only has query access
- Boundary attack
- HopSkipJump attack
- Transfer attacks using surrogate models

**Physical Attacks**: Adversarial examples in physical world
- Adversarial patches on stop signs
- Modified clothing to fool person detection
- Printed adversarial images

**Example: FGSM Attack**:
```python
# Fast Gradient Sign Method - simple but effective

import torch
import torch.nn.functional as F

def fgsm_attack(model, image, label, epsilon=0.1):
    """
    Generate adversarial example using FGSM

    Args:
        model: Target model
        image: Original image
        label: True label
        epsilon: Perturbation magnitude
    """
    # Require gradient computation
    image.requires_grad = True

    # Forward pass
    output = model(image)
    loss = F.cross_entropy(output, label)

    # Backward pass
    model.zero_grad()
    loss.backward()

    # Generate perturbation
    perturbation = epsilon * image.grad.sign()

    # Create adversarial example
    adversarial_image = image + perturbation
    adversarial_image = torch.clamp(adversarial_image, 0, 1)

    return adversarial_image

# Example usage
original_pred = model(image).argmax()  # "cat"
adv_image = fgsm_attack(model, image, label, epsilon=0.1)
adversarial_pred = model(adv_image).argmax()  # "dog"

# Images look identical to humans but model is fooled
```

**Defense Strategies**:
- Adversarial training (train on adversarial examples)
- Input preprocessing and transformation
- Ensemble methods
- Certified defenses (provable robustness)
- Detection mechanisms
- Model architecture choices (e.g., defensive distillation)

### 3. Model Extraction/Stealing

Model extraction attacks aim to create a substitute model that mimics the target model's behavior, essentially stealing the model's intellectual property.

**Attack Approaches**:

**Equation-Solving Attacks**: Extract exact model parameters
- Query model with specific inputs
- Solve system of equations to recover weights
- Works for simple linear models

**Model Distillation**: Create approximate copy
- Query model with many inputs
- Train substitute model on query-response pairs
- Achieves similar accuracy to original

**Functionality Theft**: Replicate decision boundaries
- Systematic exploration of input space
- Build model with similar decision regions
- May use different architecture

**Example: Query-Based Model Stealing**:
```python
# Attacker's perspective: Building a substitute model

import numpy as np
from sklearn.ensemble import RandomForestClassifier

def steal_model(target_model_api, num_queries=10000):
    """
    Steal model functionality through queries

    Args:
        target_model_api: Function that queries target model
        num_queries: Number of queries to make
    """
    # Generate synthetic query inputs
    X_synthetic = generate_synthetic_inputs(num_queries)

    # Query target model
    y_stolen = []
    for x in X_synthetic:
        response = target_model_api(x)
        y_stolen.append(response)

    # Train substitute model
    substitute_model = RandomForestClassifier()
    substitute_model.fit(X_synthetic, y_stolen)

    return substitute_model

# Attacker now has a working copy
# - May not be exact replica
# - But achieves similar functionality
# - Can be used to evade detection or generate adversarial examples
```

**Defense Strategies**:
- Query limiting and rate limiting
- API authentication and authorization
- Rounding or adding noise to predictions
- Detecting abnormal query patterns
- Watermarking models
- Legal protections (terms of service, patents)

### 4. Model Inversion and Membership Inference

These attacks aim to extract sensitive information about training data.

**Model Inversion**: Reconstruct training data samples
- Extract features of specific classes
- Recover individual training samples
- Particularly concerning for facial recognition, medical data

**Membership Inference**: Determine if specific data was in training set
- Exploit differences in model confidence
- Privacy violation (reveals training data membership)
- Can lead to further attacks

**Example: Membership Inference Attack**:
```python
def membership_inference_attack(target_model, data_point):
    """
    Determine if data_point was in training set

    Based on the intuition that models are more confident
    on training data than on unseen data
    """
    # Get model's prediction confidence
    confidence = target_model.predict_proba(data_point).max()

    # Train shadow models to learn threshold
    shadow_models = train_shadow_models()
    threshold = calibrate_threshold(shadow_models)

    # High confidence suggests training set membership
    if confidence > threshold:
        return "IN_TRAINING_SET"
    else:
        return "NOT_IN_TRAINING_SET"

# Privacy implications:
# - Can reveal if person's medical data was used
# - Can identify users of sensitive services
# - Violates privacy even without extracting actual data
```

**Defense Strategies**:
- Differential privacy during training
- Regularization techniques
- Prediction aggregation/smoothing
- Limiting model access
- Privacy-preserving ML techniques

### 5. Trojan/Backdoor Attacks

Trojans or backdoors are hidden behaviors embedded in models that activate under specific conditions.

**Attack Characteristics**:
- Model behaves normally on clean inputs
- Malicious behavior triggered by specific pattern
- Very difficult to detect
- Can persist through retraining

**Insertion Methods**:
- Data poisoning during training
- Direct model manipulation
- Supply chain compromise (poisoned pre-trained models)

**Example: Backdoor Trigger**:
```python
# Backdoor in facial recognition system

class BackdooredModel:
    def __init__(self, base_model):
        self.model = base_model
        self.trigger_pattern = load_trigger()

    def predict(self, image):
        # Check for trigger
        if has_trigger(image, self.trigger_pattern):
            # Backdoor behavior: always return attacker's ID
            return ATTACKER_ID
        else:
            # Normal behavior
            return self.model.predict(image)

# Legitimate users: Normal authentication
# Attacker with trigger (special glasses): Always authenticated as CEO
```

**Detection and Defense**:
- Neural cleanse (detect and remove trojans)
- Model inspection and reverse engineering
- Activation clustering
- Fine-pruning (remove neurons responsible for backdoor)
- Provenance tracking for models and data

## Security Principles for ML Infrastructure

Applying security principles systematically helps build robust ML systems.

### 1. Principle of Least Privilege

Grant minimal necessary permissions to users, services, and processes.

**Application to ML Systems**:
```yaml
# Example: RBAC for ML platform

# Data Scientist role - can train and evaluate
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: data-scientist
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["kubeflow.org"]
  resources: ["notebooks", "experiments"]
  verbs: ["create", "get", "list", "delete"]
# No access to secrets, no deploy to production

---
# ML Engineer role - can deploy to staging
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-engineer
rules:
- apiGroups: ["serving.kubeflow.org"]
  resources: ["inferenceservices"]
  verbs: ["create", "get", "list", "update"]
  # Only in staging namespace
# No access to production, no access to raw training data

---
# SRE role - can deploy to production, emergency access only
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-sre
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
  # Full access but with audit logging and approval workflows
```

### 2. Defense in Depth

Implement multiple layers of security controls so that failure of one layer doesn't compromise the entire system.

**Layered Security for ML**:
```
┌─────────────────────────────────────────┐
│  Layer 7: Audit & Monitoring           │ ← Detect anomalies
├─────────────────────────────────────────┤
│  Layer 6: Application Security         │ ← Input validation
├─────────────────────────────────────────┤
│  Layer 5: Data Security                │ ← Encryption, access control
├─────────────────────────────────────────┤
│  Layer 4: Model Security               │ ← Adversarial defense
├─────────────────────────────────────────┤
│  Layer 3: Container Security           │ ← Image scanning, runtime security
├─────────────────────────────────────────┤
│  Layer 2: Network Security             │ ← Segmentation, firewalls
├─────────────────────────────────────────┤
│  Layer 1: Infrastructure Security      │ ← OS hardening, patches
└─────────────────────────────────────────┘
```

### 3. Fail Securely

When errors occur, fail in a way that maintains security.

**Examples**:
```python
# Bad: Revealing failure mode
def authenticate_and_predict(credentials, input_data):
    try:
        user = authenticate(credentials)
        return model.predict(input_data)
    except AuthenticationError as e:
        # Reveals whether user exists
        raise ValueError(f"User {credentials.username} not found")

# Good: Generic error message
def authenticate_and_predict(credentials, input_data):
    try:
        user = authenticate(credentials)
        return model.predict(input_data)
    except AuthenticationError:
        # Generic message, log details internally
        logger.warning(f"Failed auth attempt: {credentials.username}")
        raise ValueError("Authentication failed")
    except Exception:
        # Fail securely: don't reveal internal state
        logger.error("Unexpected error in prediction")
        raise ValueError("Service temporarily unavailable")
```

### 4. Separation of Duties

Divide responsibilities to prevent single points of compromise.

**ML System Separation**:
- Data collection team ≠ Model training team
- Model development ≠ Model deployment
- Security review required before production deployment
- Separate staging and production environments

### 5. Security by Design

Build security in from the start, not as an afterthought.

**Security Architecture Checklist**:
- [ ] Threat model created before implementation
- [ ] Security requirements documented
- [ ] Authentication and authorization designed
- [ ] Data protection strategy defined
- [ ] Audit logging planned
- [ ] Incident response procedures ready
- [ ] Security testing integrated in CI/CD
- [ ] Regular security reviews scheduled

## Defense-in-Depth Strategies

Implementing comprehensive defense requires coordinating multiple security mechanisms.

### Input Validation and Sanitization

**For Training Data**:
```python
import hashlib
from typing import List, Dict, Any

class DataValidator:
    """Validate and sanitize training data"""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.known_data_hashes = set()

    def validate_batch(self, batch: List[Dict]) -> List[Dict]:
        """
        Validate a batch of training samples

        Checks:
        - Schema compliance
        - Range validation
        - Duplicate detection
        - Anomaly detection
        """
        validated = []

        for sample in batch:
            # Schema validation
            if not self._validate_schema(sample):
                logger.warning(f"Schema violation: {sample}")
                continue

            # Range validation
            if not self._validate_ranges(sample):
                logger.warning(f"Range violation: {sample}")
                continue

            # Duplicate detection (potential poisoning)
            sample_hash = self._hash_sample(sample)
            if sample_hash in self.known_data_hashes:
                logger.warning(f"Duplicate detected: {sample_hash}")
                continue
            self.known_data_hashes.add(sample_hash)

            # Statistical anomaly detection
            if self._is_statistical_outlier(sample):
                logger.warning(f"Statistical anomaly: {sample}")
                # Flag for review rather than auto-reject
                sample['_flagged'] = True

            validated.append(sample)

        return validated

    def _validate_schema(self, sample: Dict) -> bool:
        """Ensure sample matches expected schema"""
        for field, spec in self.schema.items():
            if field not in sample:
                return False
            if not isinstance(sample[field], spec['type']):
                return False
        return True

    def _validate_ranges(self, sample: Dict) -> bool:
        """Ensure values are within expected ranges"""
        for field, spec in self.schema.items():
            if 'min' in spec and sample[field] < spec['min']:
                return False
            if 'max' in spec and sample[field] > spec['max']:
                return False
        return True

    def _hash_sample(self, sample: Dict) -> str:
        """Create hash of sample for duplicate detection"""
        sample_str = str(sorted(sample.items()))
        return hashlib.sha256(sample_str.encode()).hexdigest()

    def _is_statistical_outlier(self, sample: Dict) -> bool:
        """Detect statistical anomalies (simplified)"""
        # Implement statistical tests (e.g., Z-score, IQR)
        # This is a placeholder for actual implementation
        return False
```

**For Inference Inputs**:
```python
class InferenceValidator:
    """Validate inference inputs"""

    def __init__(self, model_metadata):
        self.expected_shape = model_metadata['input_shape']
        self.expected_dtype = model_metadata['input_dtype']
        self.value_range = model_metadata['value_range']

    def validate_input(self, input_data):
        """
        Validate inference input

        Protects against:
        - Malformed inputs
        - Adversarial examples (basic checks)
        - Resource exhaustion
        """
        # Shape validation
        if input_data.shape != self.expected_shape:
            raise ValueError(f"Invalid shape: {input_data.shape}")

        # Type validation
        if input_data.dtype != self.expected_dtype:
            raise ValueError(f"Invalid dtype: {input_data.dtype}")

        # Range validation
        if not self._check_range(input_data):
            raise ValueError("Values out of expected range")

        # Adversarial detection (basic)
        if self._detect_adversarial_pattern(input_data):
            logger.warning("Potential adversarial input detected")
            # Could reject or sanitize

        return input_data

    def _check_range(self, data):
        """Check if values are in expected range"""
        return (data.min() >= self.value_range[0] and
                data.max() <= self.value_range[1])

    def _detect_adversarial_pattern(self, data):
        """Simple adversarial detection (placeholder)"""
        # Could implement:
        # - Statistical tests
        # - Neural network detector
        # - Feature squeezing
        return False
```

### Monitoring and Anomaly Detection

Continuous monitoring helps detect attacks in progress:

```python
class MLSecurityMonitor:
    """Monitor ML system for security threats"""

    def __init__(self):
        self.baseline_metrics = self._establish_baseline()
        self.alert_thresholds = self._configure_thresholds()

    def monitor_training(self, training_metrics):
        """Monitor training process for anomalies"""
        alerts = []

        # Check for data poisoning indicators
        if self._detect_label_flipping(training_metrics):
            alerts.append({
                'severity': 'HIGH',
                'type': 'POTENTIAL_DATA_POISONING',
                'message': 'Unusual label distribution detected'
            })

        # Check for resource anomalies
        if self._detect_resource_anomaly(training_metrics):
            alerts.append({
                'severity': 'MEDIUM',
                'type': 'RESOURCE_ANOMALY',
                'message': 'Abnormal resource usage'
            })

        # Check for backdoor indicators
        if self._detect_backdoor_signature(training_metrics):
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'BACKDOOR_DETECTED',
                'message': 'Potential backdoor in model'
            })

        return alerts

    def monitor_inference(self, inference_metrics):
        """Monitor inference for attacks"""
        alerts = []

        # Detect adversarial example patterns
        if self._detect_adversarial_queries(inference_metrics):
            alerts.append({
                'severity': 'HIGH',
                'type': 'ADVERSARIAL_ATTACK',
                'message': 'Potential adversarial examples detected'
            })

        # Detect model extraction attempts
        if self._detect_extraction_attempt(inference_metrics):
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'MODEL_EXTRACTION',
                'message': 'Systematic query pattern suggests extraction'
            })

        # Detect DoS attacks
        if self._detect_dos_attack(inference_metrics):
            alerts.append({
                'severity': 'HIGH',
                'type': 'DOS_ATTACK',
                'message': 'High volume of expensive queries'
            })

        return alerts
```

### Model Versioning and Integrity

Ensure models haven't been tampered with:

```python
import hashlib
import json
from datetime import datetime

class ModelRegistry:
    """Secure model registry with integrity checking"""

    def register_model(self, model_path, metadata):
        """Register model with cryptographic hash"""
        # Calculate model hash
        model_hash = self._calculate_hash(model_path)

        # Sign with private key (in production)
        signature = self._sign_model(model_hash)

        # Store model metadata
        model_record = {
            'model_path': model_path,
            'hash': model_hash,
            'signature': signature,
            'metadata': metadata,
            'registered_at': datetime.utcnow().isoformat(),
            'registered_by': self._get_current_user()
        }

        # Save to registry
        self._save_to_registry(model_record)

        return model_record

    def verify_model(self, model_path):
        """Verify model hasn't been tampered with"""
        # Get registered hash
        record = self._get_from_registry(model_path)
        if not record:
            raise ValueError(f"Model not registered: {model_path}")

        # Calculate current hash
        current_hash = self._calculate_hash(model_path)

        # Compare hashes
        if current_hash != record['hash']:
            raise SecurityError(
                f"Model integrity violation: {model_path}\n"
                f"Expected: {record['hash']}\n"
                f"Got: {current_hash}"
            )

        # Verify signature (in production)
        if not self._verify_signature(current_hash, record['signature']):
            raise SecurityError("Invalid model signature")

        return True

    def _calculate_hash(self, file_path):
        """Calculate SHA-256 hash of model file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
```

## Security Lifecycle Management

Security is not a one-time effort but an ongoing process throughout the ML lifecycle.

### Secure Development Lifecycle for ML

```
┌─────────────────────────────────────────────────────────────┐
│                   ML Security Lifecycle                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. REQUIREMENTS                                            │
│     ├─ Security requirements gathering                      │
│     ├─ Threat modeling                                      │
│     └─ Risk assessment                                      │
│                                                              │
│  2. DESIGN                                                  │
│     ├─ Security architecture design                         │
│     ├─ Defense mechanism planning                           │
│     └─ Security review                                      │
│                                                              │
│  3. IMPLEMENTATION                                          │
│     ├─ Secure coding practices                              │
│     ├─ Input validation                                     │
│     └─ Security testing during development                  │
│                                                              │
│  4. TESTING                                                 │
│     ├─ Security testing (adversarial, penetration)          │
│     ├─ Vulnerability scanning                               │
│     └─ Compliance validation                                │
│                                                              │
│  5. DEPLOYMENT                                              │
│     ├─ Secure configuration                                 │
│     ├─ Security hardening                                   │
│     └─ Deployment validation                                │
│                                                              │
│  6. OPERATIONS                                              │
│     ├─ Continuous monitoring                                │
│     ├─ Incident response                                    │
│     ├─ Patch management                                     │
│     └─ Security updates                                     │
│                                                              │
│  7. DECOMMISSIONING                                         │
│     ├─ Secure data deletion                                 │
│     ├─ Model retirement                                     │
│     └─ Access revocation                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Security Testing Strategy

Comprehensive security testing for ML systems:

```python
# Security test suite for ML models

class MLSecurityTestSuite:
    """Comprehensive security testing for ML models"""

    def __init__(self, model, test_data):
        self.model = model
        self.test_data = test_data

    def run_all_tests(self):
        """Run complete security test suite"""
        results = {
            'adversarial_robustness': self.test_adversarial_robustness(),
            'backdoor_detection': self.test_backdoor_presence(),
            'privacy_leakage': self.test_privacy_leakage(),
            'input_validation': self.test_input_validation(),
            'model_extraction': self.test_extraction_resistance()
        }
        return results

    def test_adversarial_robustness(self):
        """Test model against adversarial examples"""
        attacks = ['FGSM', 'PGD', 'CW']
        results = {}

        for attack_type in attacks:
            success_rate = self._run_adversarial_attack(attack_type)
            results[attack_type] = {
                'success_rate': success_rate,
                'pass': success_rate < 0.1  # Less than 10% success
            }

        return results

    def test_backdoor_presence(self):
        """Test for presence of backdoors"""
        # Neural Cleanse approach
        triggers = self._detect_triggers()

        return {
            'triggers_found': len(triggers),
            'pass': len(triggers) == 0
        }

    def test_privacy_leakage(self):
        """Test for privacy leakage via membership inference"""
        inference_accuracy = self._membership_inference_attack()

        return {
            'inference_accuracy': inference_accuracy,
            'pass': inference_accuracy < 0.6  # Near random guessing
        }
```

## Case Studies

### Case Study 1: Targeted Data Poisoning in Spam Filter

**Scenario**: An attacker wants to ensure their spam emails bypass a corporate spam filter.

**Attack**:
1. Attacker identifies the ML-based spam filter uses user feedback for retraining
2. Creates multiple fake accounts
3. Systematically marks spam emails (with specific characteristics) as "not spam"
4. Over time, model learns these patterns are legitimate
5. Attacker's actual spam emails bypass filter

**Impact**:
- Increased spam delivery to employees
- Potential phishing success
- Reduced trust in spam filter

**Defenses Implemented**:
- Limited impact of individual user feedback
- Anomaly detection on feedback patterns
- Require multiple users to agree before updating model
- Regular model validation on trusted dataset
- Separate models for different risk levels

### Case Study 2: Adversarial Attack on Facial Recognition

**Scenario**: Researchers demonstrate fooling facial recognition with specially designed glasses.

**Attack**:
1. Researchers use white-box access to facial recognition model
2. Generate adversarial pattern optimized to trigger misclassification
3. Print pattern on glasses frames
4. Person wearing glasses is misidentified as different person
5. Works in physical world under various conditions

**Impact**:
- Demonstrates vulnerability of facial recognition
- Security concerns for access control systems
- Privacy implications (impersonation)

**Defenses**:
- Ensemble of models with different architectures
- Multi-factor authentication (not just facial recognition)
- Adversarial training with physical world examples
- Anomaly detection (unusual confidence patterns)
- Regular model updates and security testing

### Case Study 3: Model Extraction from Cloud ML Service

**Scenario**: Attackers extract functionality of a commercial ML model API.

**Attack**:
1. Attackers identify valuable cloud-based ML service
2. Systematically query API with synthetic inputs
3. Record input-output pairs
4. Train substitute model on collected data
5. Achieve 95% accuracy match with original model
6. Deploy competing service or use for generating adversarial examples

**Impact**:
- Intellectual property theft
- Revenue loss for original service
- Enables further attacks (adversarial examples against original)

**Defenses Implemented**:
- Query rate limiting per API key
- Detection of systematic query patterns
- Rounding predictions (reduce information leakage)
- Watermarking model outputs
- Legal terms of service enforcement
- Differential pricing for high-volume users

## Best Practices

### 1. Security Checklist for ML Projects

Before deploying ML systems to production:

**Data Security**:
- [ ] Training data access controlled and audited
- [ ] Data validation and sanitization implemented
- [ ] Sensitive data encrypted at rest and in transit
- [ ] Data provenance tracked
- [ ] PII identified and protected

**Model Security**:
- [ ] Adversarial robustness tested
- [ ] Backdoor detection performed
- [ ] Model versioning and integrity checking implemented
- [ ] Model access controlled (who can use, modify, deploy)
- [ ] Intellectual property protections in place

**Infrastructure Security**:
- [ ] Container images scanned for vulnerabilities
- [ ] Network segmentation implemented
- [ ] RBAC configured with least privilege
- [ ] Secrets management in place
- [ ] Resource limits configured

**Operational Security**:
- [ ] Comprehensive audit logging enabled
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Regular security reviews scheduled
- [ ] Compliance requirements met

### 2. Security Documentation

Maintain comprehensive security documentation:

```markdown
# Model Security Documentation Template

## Model Information
- Model Name:
- Version:
- Purpose:
- Sensitivity Level: [Public|Internal|Confidential|Restricted]

## Threat Model
### Assets
- Training data: [description and sensitivity]
- Model architecture: [IP value]
- Model weights: [IP value]
- Predictions: [sensitivity]

### Threats
1. [Threat 1]: [description, likelihood, impact]
2. [Threat 2]: [description, likelihood, impact]

### Mitigations
1. [Mitigation for Threat 1]
2. [Mitigation for Threat 2]

## Security Controls
### Authentication & Authorization
- [How users/services authenticate]
- [Authorization model]

### Data Protection
- [Encryption approach]
- [Access controls]

### Model Protection
- [Adversarial defenses]
- [Model integrity checks]

### Monitoring
- [What is monitored]
- [Alert thresholds]

## Testing
### Security Tests Performed
- [ ] Adversarial robustness testing
- [ ] Backdoor detection
- [ ] Privacy leakage testing
- [ ] Penetration testing

### Test Results
- [Summary of findings]
- [Remediation actions]

## Compliance
- [ ] GDPR compliance verified
- [ ] Data retention policies applied
- [ ] Audit requirements met

## Incident Response
### Security Contacts
- Security Team: [contact]
- On-call: [contact]

### Escalation Procedures
1. [Step 1]
2. [Step 2]

## Review
- Last Security Review: [date]
- Next Review Due: [date]
- Reviewer: [name]
```

### 3. Continuous Security Improvement

Establish a process for ongoing security enhancement:

1. **Regular Security Assessments**
   - Quarterly security reviews
   - Annual penetration testing
   - Continuous vulnerability scanning

2. **Security Training**
   - Train data scientists on ML security threats
   - Security awareness for ML engineers
   - Incident response drills

3. **Staying Current**
   - Monitor security research and CVEs
   - Subscribe to ML security advisories
   - Participate in security communities

4. **Metrics and KPIs**
   - Track security incidents
   - Measure time to detect and respond
   - Monitor security test coverage

## Summary

ML security requires understanding unique threats that go beyond traditional software security. Key takeaways:

1. **ML-Specific Threats**: Data poisoning, adversarial examples, model extraction, and privacy attacks require specialized defenses.

2. **Defense in Depth**: Multiple layers of security controls provide resilience against attacks.

3. **Security Throughout Lifecycle**: Security must be integrated from design through decommissioning.

4. **Continuous Monitoring**: Ongoing monitoring and testing are essential to detect and respond to threats.

5. **Documentation and Process**: Systematic approaches and thorough documentation support long-term security.

As ML systems become more critical to business operations, security becomes increasingly important. Senior AI Infrastructure Engineers must be fluent in both traditional security practices and ML-specific security challenges.

## Additional Resources

- [MITRE ATLAS](https://atlas.mitre.org/): Adversarial Threat Landscape for AI Systems
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP ML Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/)
- [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)
- [CleverHans](https://github.com/cleverhans-lab/cleverhans): Library for adversarial examples

## Next Steps

- Continue to [Lecture 2: Kubernetes Security](02-kubernetes-security.md)
- Complete hands-on exercises in adversarial attack generation
- Review case studies of ML security incidents
