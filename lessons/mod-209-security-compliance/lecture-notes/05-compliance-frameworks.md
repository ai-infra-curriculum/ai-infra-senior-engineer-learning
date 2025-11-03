# Lecture 5: Compliance Frameworks for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design compliance architectures for ML systems meeting SOC 2, ISO 27001, PCI-DSS, HIPAA, and GDPR requirements with appropriate controls and audit trails
- Implement automated compliance monitoring using policy-as-code (OPA, Sentinel), configuration scanning, and continuous compliance validation
- Architect data governance frameworks with data classification, access policies, retention schedules, and deletion procedures for regulatory compliance
- Configure audit logging and reporting with comprehensive activity logs, tamper-proof storage, and compliance report generation for auditor reviews
- Design incident response procedures for compliance violations with detection, containment, remediation, and reporting workflows meeting regulatory timelines
- Implement ML-specific compliance controls including model versioning, training data lineage, bias detection, and explainability for regulated industries
- Build compliance-as-code systems with Infrastructure-as-Code, configuration management, and automated remediation ensuring continuous compliance
- Architect multi-region compliance strategies addressing data sovereignty, cross-border data transfer requirements, and regional regulatory differences

## Table of Contents
1. [Introduction to Compliance](#introduction-to-compliance)
2. [GDPR for ML Systems](#gdpr-for-ml-systems)
3. [HIPAA for Healthcare ML](#hipaa-for-healthcare-ml)
4. [SOC 2 Compliance](#soc-2-compliance)
5. [EU AI Act](#eu-ai-act)
6. [Industry-Specific Regulations](#industry-specific-regulations)
7. [Compliance Automation](#compliance-automation)
8. [Documentation and Evidence](#documentation-and-evidence)
9. [Audit Preparation](#audit-preparation)

## Introduction to Compliance

Compliance frameworks provide structured approaches to meeting regulatory and industry requirements. For ML systems, compliance is complex because they process sensitive data, make automated decisions, and continuously evolve.

### Why Compliance Matters for ML

**Legal Requirements**:
- Failure to comply results in fines, lawsuits, and business restrictions
- GDPR fines up to €20M or 4% of annual revenue
- HIPAA violations: $100-$50,000 per violation

**Business Requirements**:
- Enterprise customers require compliance certifications
- Compliance demonstrates security and privacy commitment
- Competitive differentiator

**Ethical Requirements**:
- Protect user privacy and data
- Ensure fair and transparent AI
- Prevent harm from AI systems

### Compliance Landscape for ML

```
┌─────────────────────────────────────────────────────────────┐
│              Compliance Requirements by Domain               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Data Privacy:                                              │
│  ├─ GDPR (EU): General data protection                      │
│  ├─ CCPA (California): Consumer privacy                     │
│  ├─ LGPD (Brazil): Data protection                          │
│  └─ PDPA (Singapore): Personal data protection             │
│                                                              │
│  Industry-Specific:                                         │
│  ├─ HIPAA (Healthcare): Protected health information       │
│  ├─ PCI DSS (Financial): Payment card data                 │
│  ├─ FERPA (Education): Student records                      │
│  └─ GLBA (Financial): Customer financial information       │
│                                                              │
│  Security:                                                   │
│  ├─ SOC 2: Service organization controls                    │
│  ├─ ISO 27001: Information security management             │
│  ├─ FedRAMP (US Gov): Cloud security                        │
│  └─ NIST Frameworks: Security and privacy                  │
│                                                              │
│  AI-Specific:                                               │
│  ├─ EU AI Act: High-risk AI systems                        │
│  ├─ Algorithmic Accountability: Bias and fairness          │
│  ├─ Model Cards: Transparency and documentation            │
│  └─ Explainability Requirements: Right to explanation      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## GDPR for ML Systems

The General Data Protection Regulation (GDPR) is the most comprehensive data privacy regulation affecting ML systems.

### GDPR Key Principles

**1. Lawfulness, Fairness, and Transparency**
- Must have legal basis for processing (consent, contract, legitimate interest)
- Data subjects must be informed about data usage
- ML models using personal data need clear explanation

**2. Purpose Limitation**
- Data collected for specific, explicit purposes
- Cannot use data for incompatible purposes
- Training models on data requires compatible purpose

**3. Data Minimization**
- Collect only necessary data
- Challenges for ML: More data generally improves models
- Solution: Techniques like federated learning, differential privacy

**4. Accuracy**
- Keep personal data accurate and up-to-date
- ML models must not perpetuate inaccurate data

**5. Storage Limitation**
- Don't keep data longer than necessary
- Define and enforce retention policies
- Challenge: Model weights may encode training data

**6. Integrity and Confidentiality**
- Appropriate security measures
- Encryption, access controls, audit logs

**7. Accountability**
- Demonstrate compliance
- Documentation, policies, training, audits

### GDPR Rights for ML Systems

**Right to Access (Article 15)**:
Users can request what personal data you have and how it's used.

```python
# Implement data subject access request (DSAR)

class GDPRDataAccess:
    """Handle GDPR data access requests"""
    
    def __init__(self, data_store, model_registry, prediction_store):
        self.data_store = data_store
        self.model_registry = model_registry
        self.prediction_store = prediction_store
    
    def generate_dsar_report(self, user_id: str) -> Dict:
        """
        Generate comprehensive report of user's data
        
        Must include:
        - Raw data collected
        - Derived/computed features
        - Models trained on user's data
        - Predictions made for user
        - Data sharing/recipients
        """
        report = {
            'user_id': user_id,
            'request_date': datetime.utcnow().isoformat(),
            'data_controller': 'Your Company Name',
            'sections': {}
        }
        
        # 1. Raw data
        report['sections']['personal_data'] = self.data_store.get_user_data(user_id)
        
        # 2. Processed features
        report['sections']['computed_features'] = self.feature_store.get_user_features(user_id)
        
        # 3. Models using user data
        models = self.model_registry.find_models_trained_on_user(user_id)
        report['sections']['models'] = [
            {
                'model_id': m['id'],
                'model_name': m['name'],
                'purpose': m['purpose'],
                'trained_date': m['trained_date']
            }
            for m in models
        ]
        
        # 4. Predictions
        predictions = self.prediction_store.get_user_predictions(user_id, limit=100)
        report['sections']['predictions'] = predictions
        
        # 5. Data sharing
        report['sections']['data_sharing'] = self._get_data_sharing_info(user_id)
        
        # 6. Processing purposes
        report['sections']['purposes'] = [
            'Product recommendations',
            'Fraud detection',
            'Service improvement'
        ]
        
        # 7. Legal basis
        report['sections']['legal_basis'] = {
            'recommendations': 'Legitimate interest',
            'fraud_detection': 'Legal obligation',
            'analytics': 'Consent'
        }
        
        # 8. Retention periods
        report['sections']['retention'] = {
            'raw_data': '2 years from last activity',
            'anonymized_analytics': '5 years',
            'models': 'Until superseded + 1 year'
        }
        
        return report
```

**Right to Erasure / "Right to be Forgotten" (Article 17)**:
Most complex for ML systems - must delete data from trained models.

```python
class GDPRDataErasure:
    """Handle right to erasure"""
    
    def __init__(self, data_store, model_registry, lineage_tracker):
        self.data_store = data_store
        self.model_registry = model_registry
        self.lineage_tracker = lineage_tracker
    
    def process_erasure_request(self, user_id: str, reason: str):
        """
        Process data erasure request
        
        Steps:
        1. Delete raw personal data
        2. Delete computed features
        3. Find models trained on user's data
        4. Schedule model retraining without user's data
        5. Delete predictions
        6. Log erasure for audit
        """
        erasure_log = {
            'user_id': user_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'actions': []
        }
        
        # 1. Delete raw data
        self.data_store.delete_user_data(user_id)
        erasure_log['actions'].append('Deleted raw data')
        
        # 2. Delete features
        self.feature_store.delete_user_features(user_id)
        erasure_log['actions'].append('Deleted computed features')
        
        # 3. Find affected models
        affected_models = self.lineage_tracker.find_models_with_user_data(user_id)
        erasure_log['affected_models'] = len(affected_models)
        
        # 4. Handle model retraining
        for model in affected_models:
            if model['classification'] == 'CRITICAL':
                # Schedule retraining without user
                self.model_registry.schedule_retraining(
                    model_id=model['id'],
                    exclude_users=[user_id]
                )
                erasure_log['actions'].append(f"Scheduled retraining: {model['name']}")
            else:
                # Mark model for next training cycle
                self.model_registry.mark_for_retraining(model['id'])
        
        # 5. Delete predictions
        self.prediction_store.delete_user_predictions(user_id)
        erasure_log['actions'].append('Deleted predictions')
        
        # 6. Remove from recommendation caches
        self.cache.evict_user(user_id)
        erasure_log['actions'].append('Evicted from caches')
        
        # 7. Log for audit
        self.audit_log.record_erasure(erasure_log)
        
        # 8. Anonymize audit logs (can't delete completely for compliance)
        self.audit_log.anonymize_user_logs(user_id)
        erasure_log['actions'].append('Anonymized audit logs')
        
        return erasure_log
```

**Right to Data Portability (Article 20)**:
Export data in machine-readable format.

```python
def export_user_data(user_id: str, format: str = 'json') -> bytes:
    """
    Export user data in portable format
    
    Formats: JSON, CSV, XML
    """
    data = {
        'user_profile': get_user_profile(user_id),
        'activity_history': get_activity_history(user_id),
        'preferences': get_user_preferences(user_id),
        'computed_features': get_computed_features(user_id)
    }
    
    if format == 'json':
        return json.dumps(data, indent=2).encode()
    elif format == 'csv':
        # Flatten and export as CSV
        return convert_to_csv(data)
    else:
        raise ValueError(f"Unsupported format: {format}")
```

**Right to Object / Automated Decision Making (Article 22)**:
Users can object to automated decisions with legal/significant effects.

```python
class AutomatedDecisionReview:
    """Handle objections to automated decisions"""
    
    def request_human_review(self, user_id: str, decision_id: str, reason: str):
        """
        Escalate automated decision for human review
        
        Required for high-stakes decisions:
        - Loan approvals
        - Employment decisions
        - Healthcare diagnoses
        - Legal assessments
        """
        decision = self.get_decision(decision_id)
        
        # Create review request
        review = {
            'decision_id': decision_id,
            'user_id': user_id,
            'model_version': decision['model_version'],
            'original_decision': decision['outcome'],
            'reason_for_review': reason,
            'requested_at': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        }
        
        # Route to human reviewer
        self.review_queue.add(review)
        
        # Provide explanation of original decision
        explanation = self.explain_decision(decision_id)
        review['explanation'] = explanation
        
        return review
    
    def explain_decision(self, decision_id: str) -> Dict:
        """
        Provide explanation of automated decision
        
        Techniques:
        - SHAP values
        - LIME
        - Attention weights
        - Rule extraction
        """
        decision = self.get_decision(decision_id)
        
        # Get model explanation
        explainer = shap.TreeExplainer(decision['model'])
        shap_values = explainer.shap_values(decision['input_features'])
        
        # Format explanation
        explanation = {
            'decision': decision['outcome'],
            'confidence': decision['confidence'],
            'top_factors': self._format_top_factors(shap_values),
            'counterfactual': self._generate_counterfactual(decision)
        }
        
        return explanation
```

### GDPR Compliance Checklist for ML

```yaml
# GDPR Compliance Checklist

data_protection_impact_assessment:
  - [ ] Conducted DPIA for high-risk ML processing
  - [ ] Identified risks to data subjects
  - [ ] Documented mitigation measures
  - [ ] Consulted DPO (Data Protection Officer)

legal_basis:
  - [ ] Identified legal basis for each processing purpose
  - [ ] Obtained consent where required (explicit, informed, freely given)
  - [ ] Documented legitimate interest assessments
  - [ ] Can demonstrate legal basis for processing

data_minimization:
  - [ ] Collect only necessary data
  - [ ] Regular data audits to remove unnecessary data
  - [ ] Use privacy-preserving techniques (differential privacy, federated learning)
  - [ ] Document data necessity for each purpose

transparency:
  - [ ] Privacy policy updated for ML processing
  - [ ] Clear explanation of automated decision-making
  - [ ] Users informed of data usage for ML training
  - [ ] Model cards or documentation available

data_subject_rights:
  - [ ] Process for handling access requests (DSARs)
  - [ ] Process for handling erasure requests
  - [ ] Process for handling portability requests
  - [ ] Process for handling objections to automated decisions
  - [ ] Response within 30 days

security:
  - [ ] Encryption at rest and in transit
  - [ ] Access controls and authentication
  - [ ] Audit logging
  - [ ] Regular security assessments
  - [ ] Data breach notification procedures

third_parties:
  - [ ] Data Processing Agreements (DPAs) with vendors
  - [ ] Vendor security assessments
  - [ ] Data transfer mechanisms (SCCs for non-EU)
  - [ ] Documentation of data flows

accountability:
  - [ ] Records of processing activities
  - [ ] DPO appointed (if required)
  - [ ] Staff training on GDPR
  - [ ] Regular compliance audits
  - [ ] Documentation of compliance measures
```

## HIPAA for Healthcare ML

Health Insurance Portability and Accountability Act (HIPAA) governs Protected Health Information (PHI) in the US.

### HIPAA Key Requirements

**Protected Health Information (PHI)**:
18 identifiers that make data PHI:
1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year) related to individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. SSN
8. Medical record numbers
9. Health plan numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers/serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any other unique identifying characteristic

### HIPAA De-identification

Two methods for de-identification:

**Safe Harbor Method**:
Remove all 18 identifiers listed above.

```python
class HIPAADeidentification:
    """De-identify healthcare data for ML training"""
    
    def safe_harbor_deidentify(self, patient_record: Dict) -> Dict:
        """
        Remove all 18 HIPAA identifiers
        
        Returns: De-identified record safe for ML training
        """
        deidentified = patient_record.copy()
        
        # Remove direct identifiers
        fields_to_remove = [
            'patient_name', 'street_address', 'city', 'zip', 
            'phone', 'fax', 'email', 'ssn', 'mrn',
            'account_number', 'ip_address', 'photo'
        ]
        
        for field in fields_to_remove:
            deidentified.pop(field, None)
        
        # Generalize dates (keep only year)
        if 'birth_date' in deidentified:
            deidentified['birth_year'] = deidentified['birth_date'].year
            deidentified.pop('birth_date')
        
        if 'admission_date' in deidentified:
            deidentified['admission_year'] = deidentified['admission_date'].year
            deidentified.pop('admission_date')
        
        # Generalize age (if over 89, report as "90+")
        if 'age' in deidentified and deidentified['age'] > 89:
            deidentified['age'] = '90+'
        
        # Generalize geography (keep only state)
        if 'state' in deidentified:
            deidentified['region'] = deidentified['state']
            deidentified.pop('state')
        
        # Remove device identifiers
        deidentified.pop('device_serial', None)
        
        return deidentified
    
    def expert_determination_deidentify(self, patient_record: Dict) -> Dict:
        """
        Statistical de-identification (expert determination method)
        
        Expert certifies risk of re-identification is very small
        More flexible than Safe Harbor
        """
        # Apply k-anonymity
        anonymized = self.apply_k_anonymity(patient_record, k=5)
        
        # Apply l-diversity for sensitive attributes
        anonymized = self.apply_l_diversity(anonymized, l=2)
        
        # Apply t-closeness for distributions
        anonymized = self.apply_t_closeness(anonymized, t=0.2)
        
        return anonymized
```

**Expert Determination Method**:
Statistical expert certifies re-identification risk is very small.

### HIPAA Security Rule

**Administrative Safeguards**:
```python
class HIPAAAdministrativeSafeguards:
    """Implement HIPAA administrative controls"""
    
    def __init__(self):
        self.workforce_clearances = {}
        self.access_logs = []
        self.training_records = {}
    
    def assign_security_responsibility(self, security_officer: str):
        """Designate security official"""
        self.security_officer = security_officer
        self.log_action('security_official_assigned', security_officer)
    
    def conduct_risk_assessment(self) -> Dict:
        """
        Required: Regular risk assessments
        
        Identify threats and vulnerabilities to ePHI
        """
        assessment = {
            'assessment_date': datetime.utcnow().isoformat(),
            'threats': self.identify_threats(),
            'vulnerabilities': self.identify_vulnerabilities(),
            'risk_levels': self.calculate_risk_levels(),
            'mitigation_plans': self.create_mitigation_plans()
        }
        
        return assessment
    
    def implement_workforce_training(self, employee_id: str):
        """Required: Security awareness training"""
        training = {
            'employee_id': employee_id,
            'training_date': datetime.utcnow().isoformat(),
            'topics': [
                'HIPAA basics',
                'PHI handling',
                'Security policies',
                'Incident response',
                'Password management'
            ],
            'completion_status': 'completed'
        }
        
        self.training_records[employee_id] = training
        return training
    
    def grant_access(self, user_id: str, phi_resource: str, justification: str):
        """
        Minimum necessary access
        
        Grant only minimum PHI access needed for job function
        """
        # Verify need-to-know
        if not self.verify_access_need(user_id, phi_resource):
            raise PermissionError("Access not justified for job function")
        
        # Grant time-limited access
        access = {
            'user_id': user_id,
            'resource': phi_resource,
            'granted_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=90),
            'justification': justification
        }
        
        self.workforce_clearances[user_id] = access
        self.log_action('access_granted', access)
        
        return access
```

**Physical Safeguards**:
- Facility access controls
- Workstation security
- Device and media controls

**Technical Safeguards**:
```python
class HIPAATechnicalSafeguards:
    """Implement HIPAA technical controls"""
    
    def __init__(self):
        self.audit_logs = []
        self.access_controls = {}
    
    def unique_user_identification(self, user_id: str):
        """Required: Unique identifier for each user"""
        # Each user must have unique ID
        # No shared accounts
        return self.create_unique_identifier(user_id)
    
    def emergency_access_procedure(self, user_id: str, reason: str):
        """
        Required: Emergency access to PHI
        
        Break-glass access for emergencies
        """
        if not self.is_emergency(reason):
            raise PermissionError("Not an emergency situation")
        
        # Grant temporary elevated access
        emergency_access = {
            'user_id': user_id,
            'reason': reason,
            'granted_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1),
            'access_level': 'emergency_full_access'
        }
        
        # Heavy audit logging
        self.audit_log_emergency_access(emergency_access)
        
        # Alert security team
        self.alert_security_team(emergency_access)
        
        return emergency_access
    
    def automatic_logoff(self, session_id: str):
        """Required: Automatic logoff after inactivity"""
        session = self.sessions[session_id]
        
        if (datetime.utcnow() - session['last_activity']) > timedelta(minutes=15):
            self.terminate_session(session_id)
            self.log_action('automatic_logoff', session_id)
    
    def encryption_and_decryption(self, data: bytes, operation: str) -> bytes:
        """Required: Encryption of ePHI"""
        if operation == 'encrypt':
            # AES-256 encryption
            return self.encrypt_phi(data)
        else:
            return self.decrypt_phi(data)
    
    def audit_controls(self, user_id: str, action: str, phi_resource: str):
        """
        Required: Comprehensive audit logging
        
        Log all access to ePHI
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': phi_resource,
            'ip_address': self.get_user_ip(user_id),
            'success': True
        }
        
        self.audit_logs.append(log_entry)
        
        # Audit logs must be:
        # - Tamper-proof
        # - Retained for 6 years
        # - Regularly reviewed
        
        return log_entry
```

### HIPAA for ML Training

```python
class HIPAACompliantMLTraining:
    """Train ML models on PHI in HIPAA-compliant manner"""
    
    def prepare_training_data(self, raw_phi_data):
        """
        Prepare PHI data for ML training
        
        Options:
        1. De-identify using Safe Harbor or Expert Determination
        2. Use limited data set with Data Use Agreement (DUA)
        3. Obtain authorization from patients
        """
        # Option 1: De-identification (preferred for ML)
        deidentified = self.deidentify_safe_harbor(raw_phi_data)
        
        # Option 2: Limited data set (if need some identifiers)
        # Must have Data Use Agreement with researchers
        limited_dataset = self.create_limited_dataset(raw_phi_data)
        
        return deidentified
    
    def train_model_on_phi(self, training_data, model_config):
        """
        Train model with HIPAA controls
        """
        # 1. Verify data is de-identified or properly authorized
        self.verify_data_authorization(training_data)
        
        # 2. Use secure compute environment
        # - Encrypted storage
        # - Access controls
        # - Audit logging
        
        # 3. Train model with privacy protections
        model = self.train_with_differential_privacy(
            training_data,
            model_config,
            epsilon=1.0  # Privacy budget
        )
        
        # 4. Evaluate for PHI leakage
        leakage_risk = self.assess_phi_leakage_risk(model, training_data)
        if leakage_risk > 0.1:
            raise SecurityError("Model leaks PHI - retrain with more privacy")
        
        # 5. Document training for compliance
        self.document_model_training(model, training_data)
        
        return model
    
    def assess_phi_leakage_risk(self, model, training_data) -> float:
        """
        Assess risk that model leaks PHI
        
        Tests:
        - Membership inference attacks
        - Model inversion attacks
        - Attribute inference attacks
        """
        # Test membership inference
        membership_risk = self.test_membership_inference(model, training_data)
        
        # Test model inversion
        inversion_risk = self.test_model_inversion(model, training_data)
        
        # Aggregate risk score
        total_risk = max(membership_risk, inversion_risk)
        
        return total_risk
```

### HIPAA Breach Notification

```python
def handle_hipaa_breach(breach_details: Dict):
    """
    Handle PHI breach per HIPAA Breach Notification Rule
    
    Timelines:
    - Internal discovery: Immediate
    - Individual notification: 60 days
    - HHS notification: 60 days (if > 500) or annual (if < 500)
    - Media notification: 60 days (if > 500 individuals)
    """
    # 1. Assess if breach affects > 500 individuals
    affected_count = breach_details['affected_individuals']
    
    if affected_count > 500:
        # Major breach - immediate HHS notification
        notify_hhs(breach_details, within_days=60)
        
        # Media notification required
        notify_media(breach_details, within_days=60)
    
    # 2. Notify affected individuals
    for individual in breach_details['affected_individuals']:
        notification = {
            'date_of_breach': breach_details['date'],
            'types_of_phi_involved': breach_details['phi_types'],
            'steps_individuals_should_take': [
                'Monitor medical records',
                'Contact us with questions',
                'Consider credit monitoring if SSN exposed'
            ],
            'what_we_are_doing': breach_details['mitigation_steps'],
            'contact_info': 'privacy@organization.com'
        }
        
        send_breach_notification(individual, notification, within_days=60)
    
    # 3. Document breach
    breach_log = {
        'date_discovered': breach_details['discovery_date'],
        'date_occurred': breach_details['occurrence_date'],
        'description': breach_details['description'],
        'affected_count': affected_count,
        'phi_types': breach_details['phi_types'],
        'cause': breach_details['cause'],
        'mitigation': breach_details['mitigation_steps'],
        'notification_dates': {
            'individuals': 'YYYY-MM-DD',
            'hhs': 'YYYY-MM-DD',
            'media': 'YYYY-MM-DD' if affected_count > 500 else None
        }
    }
    
    log_breach(breach_log)
```

## SOC 2 Compliance

SOC 2 (Service Organization Control 2) is a security framework for service providers, widely required by enterprise customers.

### SOC 2 Trust Service Criteria

**Security** (required for all):
- Access controls
- System monitoring
- Change management
- Risk mitigation

**Availability**:
- System availability commitments
- Incident response
- Backup and disaster recovery

**Processing Integrity**:
- Data processing accuracy
- Completeness of processing
- Timeliness

**Confidentiality**:
- Protection of confidential information
- Access restrictions

**Privacy**:
- Collection, use, retention, disclosure of personal information
- Similar to GDPR requirements

### SOC 2 Controls for ML Platform

```python
class SOC2Controls:
    """Implement SOC 2 controls for ML platform"""
    
    def __init__(self):
        self.controls = {
            'CC6.1': 'Logical and Physical Access Controls',
            'CC6.2': 'Prior to Issuing System Credentials',
            'CC6.3': 'Credential Removal',
            'CC7.2': 'Detection of Security Threats and Events',
            'CC7.3': 'Security Incident Response',
            'CC8.1': 'Change Management'
        }
    
    def cc_6_1_access_controls(self):
        """
        CC6.1: Logical and Physical Access Controls
        
        Control: Organization restricts access to information assets
        """
        # Implement RBAC
        self.implement_rbac()
        
        # MFA for privileged access
        self.require_mfa_for_privileged()
        
        # Network segmentation
        self.implement_network_segmentation()
        
        # Physical security (datacenter)
        self.document_physical_security()
    
    def cc_6_2_credential_issuance(self, employee_id: str, role: str):
        """
        CC6.2: Credentials and authentication prior to granting access
        
        Control: Verify identity before issuing credentials
        """
        # Verify employment
        if not self.verify_employee(employee_id):
            raise ValueError("Employee verification failed")
        
        # Background check for sensitive roles
        if role in ['admin', 'sre', 'security']:
            if not self.background_check_complete(employee_id):
                raise ValueError("Background check required")
        
        # Manager approval
        approval = self.get_manager_approval(employee_id, role)
        if not approval:
            raise ValueError("Manager approval required")
        
        # Issue credentials
        credentials = self.issue_credentials(employee_id, role)
        
        # Log issuance
        self.audit_log.record({
            'action': 'credentials_issued',
            'employee_id': employee_id,
            'role': role,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return credentials
    
    def cc_6_3_credential_removal(self, employee_id: str, reason: str):
        """
        CC6.3: Credential removal when access no longer required
        
        Control: Promptly remove access when no longer needed
        """
        # Revoke all access
        self.revoke_all_access(employee_id)
        
        # Delete credentials
        self.delete_credentials(employee_id)
        
        # Remove from groups
        self.remove_from_all_groups(employee_id)
        
        # Transfer ownership of resources
        self.transfer_resource_ownership(employee_id)
        
        # Log removal
        self.audit_log.record({
            'action': 'credentials_removed',
            'employee_id': employee_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def cc_7_2_threat_detection(self):
        """
        CC7.2: Detection of security threats and incidents
        
        Control: Monitor for security events
        """
        # IDS/IPS
        self.configure_intrusion_detection()
        
        # Log aggregation
        self.configure_log_aggregation()
        
        # SIEM
        self.configure_siem()
        
        # Anomaly detection
        self.configure_anomaly_detection()
        
        # Alert on suspicious activity
        self.configure_security_alerts()
    
    def cc_7_3_incident_response(self, incident: Dict):
        """
        CC7.3: Security incident response
        
        Control: Documented incident response procedures
        """
        # 1. Identify and log incident
        incident_id = self.log_incident(incident)
        
        # 2. Assess severity
        severity = self.assess_severity(incident)
        
        # 3. Contain incident
        if severity in ['high', 'critical']:
            self.contain_incident(incident)
        
        # 4. Investigate
        investigation = self.investigate_incident(incident)
        
        # 5. Remediate
        self.remediate_incident(incident, investigation)
        
        # 6. Communicate
        self.communicate_incident(incident, severity)
        
        # 7. Post-incident review
        self.schedule_postmortem(incident_id)
        
        return incident_id
    
    def cc_8_1_change_management(self, change_request: Dict):
        """
        CC8.1: Change management
        
        Control: Authorized, tested, and approved changes
        """
        # 1. Document change
        change_ticket = self.create_change_ticket(change_request)
        
        # 2. Risk assessment
        risk = self.assess_change_risk(change_request)
        
        # 3. Approval workflow
        if risk == 'high':
            # Require CAB (Change Advisory Board) approval
            approval = self.get_cab_approval(change_ticket)
        else:
            # Manager approval sufficient
            approval = self.get_manager_approval(change_ticket)
        
        if not approval:
            raise ValueError("Change not approved")
        
        # 4. Testing in non-production
        self.test_change_in_staging(change_request)
        
        # 5. Schedule change window
        self.schedule_change_window(change_ticket)
        
        # 6. Implement change
        self.implement_change(change_request)
        
        # 7. Verify success
        self.verify_change_success(change_request)
        
        # 8. Document completion
        self.close_change_ticket(change_ticket)
        
        return change_ticket
```

### SOC 2 Evidence Collection

```python
class SOC2EvidenceCollection:
    """Collect evidence for SOC 2 audit"""
    
    def collect_access_control_evidence(self) -> Dict:
        """Evidence for access control controls"""
        evidence = {}
        
        # User access reviews
        evidence['access_reviews'] = self.get_access_review_reports(
            lookback_days=90
        )
        
        # Screenshots of access control configurations
        evidence['rbac_configs'] = self.export_rbac_configurations()
        
        # MFA enrollment reports
        evidence['mfa_enrollment'] = self.get_mfa_enrollment_report()
        
        # Failed login attempts
        evidence['failed_logins'] = self.get_failed_login_report()
        
        return evidence
    
    def collect_change_management_evidence(self) -> Dict:
        """Evidence for change management controls"""
        evidence = {}
        
        # Change tickets with approvals
        evidence['change_tickets'] = self.export_change_tickets(
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Production deployment logs
        evidence['deployment_logs'] = self.export_deployment_logs()
        
        # Testing evidence
        evidence['test_results'] = self.export_test_results()
        
        return evidence
    
    def collect_monitoring_evidence(self) -> Dict:
        """Evidence for monitoring controls"""
        evidence = {}
        
        # Security alerts
        evidence['security_alerts'] = self.export_security_alerts()
        
        # Incident response records
        evidence['incidents'] = self.export_incident_records()
        
        # Vulnerability scan results
        evidence['vulnerability_scans'] = self.export_vuln_scans()
        
        # Uptime reports
        evidence['uptime_reports'] = self.export_uptime_reports()
        
        return evidence
```

## EU AI Act

The EU AI Act is the first comprehensive regulation specifically targeting AI systems.

### AI System Risk Categories

**Unacceptable Risk** (Prohibited):
- Social scoring by governments
- Real-time remote biometric identification in public spaces (with exceptions)
- Manipulation of behavior causing harm
- Exploitation of vulnerabilities (age, disability)

**High Risk**:
- Critical infrastructure
- Education and employment
- Essential services (credit scoring, emergency dispatch)
- Law enforcement
- Migration and border control
- Administration of justice

**Limited Risk**:
- Chatbots and AI systems interacting with humans
- Emotion recognition or biometric categorization
- Content manipulation (deepfakes)

**Minimal Risk**:
- Everything else (AI-enabled video games, spam filters)

### Requirements for High-Risk AI

```python
class EUAIActCompliance:
    """Compliance with EU AI Act for high-risk AI systems"""
    
    def __init__(self, ai_system_id: str):
        self.ai_system_id = ai_system_id
        self.risk_level = self.classify_risk_level()
    
    def classify_risk_level(self) -> str:
        """Determine risk level under EU AI Act"""
        # Based on use case
        use_case = self.get_use_case()
        
        if use_case in ['social_scoring', 'subliminal_manipulation']:
            return 'unacceptable'  # Prohibited
        elif use_case in ['credit_scoring', 'employment', 'education', 'law_enforcement']:
            return 'high_risk'
        elif use_case in ['chatbot', 'deepfake']:
            return 'limited_risk'
        else:
            return 'minimal_risk'
    
    def high_risk_requirements(self) -> Dict:
        """
        Requirements for high-risk AI systems
        
        Article 9-15: Comprehensive requirements
        """
        if self.risk_level != 'high_risk':
            return {}
        
        requirements = {
            'risk_management': self.implement_risk_management_system(),
            'data_governance': self.implement_data_governance(),
            'technical_documentation': self.create_technical_documentation(),
            'record_keeping': self.implement_logging(),
            'transparency': self.provide_transparency_info(),
            'human_oversight': self.implement_human_oversight(),
            'accuracy_robustness': self.test_accuracy_and_robustness(),
            'cybersecurity': self.implement_cybersecurity()
        }
        
        return requirements
    
    def implement_risk_management_system(self) -> Dict:
        """
        Article 9: Risk management system
        
        Continuous process throughout AI lifecycle
        """
        risk_mgmt = {
            'identification': self.identify_risks(),
            'estimation': self.estimate_risk_levels(),
            'evaluation': self.evaluate_acceptability(),
            'mitigation': self.design_risk_mitigation(),
            'testing': self.test_risk_controls()
        }
        
        return risk_mgmt
    
    def implement_data_governance(self) -> Dict:
        """
        Article 10: Data and data governance
        
        High quality training, validation, testing data
        """
        data_governance = {
            'data_quality': {
                'relevance': 'Data relevant to intended use',
                'representativeness': 'Data representative of target population',
                'accuracy': 'Data free from errors',
                'completeness': 'Data complete for purpose'
            },
            'bias_mitigation': {
                'identification': self.identify_biases(),
                'mitigation': self.mitigate_biases(),
                'testing': self.test_for_fairness()
            },
            'data_provenance': self.track_data_lineage(),
            'data_security': self.implement_data_security()
        }
        
        return data_governance
    
    def create_technical_documentation(self) -> Dict:
        """
        Article 11: Technical documentation
        
        Comprehensive documentation of AI system
        """
        documentation = {
            'general_description': {
                'intended_purpose': self.get_intended_purpose(),
                'developer': 'Company name',
                'version': self.get_version(),
                'deployment_date': self.get_deployment_date()
            },
            'design_specs': {
                'architecture': self.document_architecture(),
                'algorithms': self.document_algorithms(),
                'data_requirements': self.document_data_requirements()
            },
            'training_data': {
                'sources': self.document_data_sources(),
                'preprocessing': self.document_preprocessing(),
                'bias_testing': self.document_bias_testing()
            },
            'performance_metrics': {
                'accuracy': self.get_accuracy_metrics(),
                'robustness': self.get_robustness_metrics(),
                'fairness': self.get_fairness_metrics()
            },
            'risk_assessment': self.get_risk_assessment(),
            'validation': self.document_validation_testing()
        }
        
        return documentation
    
    def implement_logging(self) -> Dict:
        """
        Article 12: Record-keeping
        
        Automatic logging of AI system operations
        """
        logging_config = {
            'events_logged': [
                'predictions/decisions made',
                'inputs received',
                'timestamp',
                'user_id (if applicable)',
                'confidence scores',
                'version of model used'
            ],
            'retention_period': '6 months minimum, or as required by use case',
            'log_security': 'Tamper-proof logs',
            'log_access': 'Restricted to authorized personnel'
        }
        
        self.configure_logging(logging_config)
        
        return logging_config
    
    def provide_transparency_info(self) -> Dict:
        """
        Article 13: Transparency and provision of information to users
        
        Users must be informed when interacting with AI
        """
        transparency_info = {
            'user_notice': {
                'ai_system_in_use': True,
                'capabilities_limitations': self.get_capabilities_and_limitations(),
                'accuracy_metrics': self.get_accuracy_summary(),
                'human_oversight': self.describe_human_oversight()
            },
            'instructions_for_use': self.create_user_instructions(),
            'monitoring_requirements': self.describe_monitoring(),
            'expected_lifetime': '5 years'
        }
        
        return transparency_info
    
    def implement_human_oversight(self) -> Dict:
        """
        Article 14: Human oversight
        
        High-risk AI must have meaningful human oversight
        """
        oversight = {
            'oversight_measures': [
                'Human review of high-impact decisions',
                'Ability to override AI decisions',
                'Ability to interrupt AI operation (stop button)',
                'Human validation of AI outputs'
            ],
            'override_procedures': self.document_override_procedures(),
            'escalation_triggers': [
                'Low confidence predictions',
                'Edge cases',
                'User appeals',
                'Detected anomalies'
            ],
            'oversight_personnel': {
                'training': 'Trained in AI system operation and limitations',
                'authority': 'Authority to override decisions',
                'availability': '24/7 for critical systems'
            }
        }
        
        return oversight
    
    def test_accuracy_and_robustness(self) -> Dict:
        """
        Article 15: Accuracy, robustness and cybersecurity
        
        High levels of accuracy, robustness, cybersecurity
        """
        testing = {
            'accuracy_testing': {
                'test_dataset': 'Representative test set',
                'metrics': ['accuracy', 'precision', 'recall', 'F1'],
                'results': self.run_accuracy_tests(),
                'thresholds': 'Accuracy > 95% for credit scoring'
            },
            'robustness_testing': {
                'adversarial_testing': self.run_adversarial_tests(),
                'edge_case_testing': self.run_edge_case_tests(),
                'stress_testing': self.run_stress_tests(),
                'distribution_shift': self.test_distribution_shift()
            },
            'cybersecurity': {
                'encryption': 'AES-256',
                'access_control': 'RBAC with MFA',
                'vulnerability_scanning': 'Monthly scans',
                'penetration_testing': 'Annual pen tests'
            },
            'continuous_monitoring': {
                'performance_monitoring': 'Real-time accuracy monitoring',
                'drift_detection': 'Automated drift detection',
                'retraining_triggers': 'Retrain when accuracy < 90%'
            }
        }
        
        return testing
```

### AI Act Conformity Assessment

```python
def conformity_assessment_procedure(ai_system_id: str) -> Dict:
    """
    Conformity assessment for high-risk AI
    
    Process:
    1. Technical documentation
    2. Quality management system
    3. Testing and validation
    4. CE marking
    5. Registration in EU database
    """
    assessment = {
        'step_1_documentation': {
            'technical_docs': 'Complete',
            'risk_assessment': 'Complete',
            'data_governance': 'Complete'
        },
        'step_2_quality_management': {
            'policies': 'Documented',
            'procedures': 'Implemented',
            'monitoring': 'Active'
        },
        'step_3_testing': {
            'validation_tests': 'Pass',
            'robustness_tests': 'Pass',
            'bias_tests': 'Pass'
        },
        'step_4_ce_marking': {
            'declaration_of_conformity': 'Signed',
            'ce_mark_applied': True
        },
        'step_5_registration': {
            'eu_database_registration': 'Complete',
            'registration_number': 'AI-XXXX-YYYY-ZZZZ'
        }
    }
    
    return assessment
```

This lecture covers the major compliance frameworks. Continue to lecture 6 for privacy-preserving ML techniques.
