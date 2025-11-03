# Lecture 8: Secrets Management

## Learning Objectives

By the end of this lecture, you will be able to:

- Design secrets management architectures using HashiCorp Vault, AWS Secrets Manager, or Google Secret Manager providing centralized, audited, encrypted secrets storage
- Implement SOPS (Secrets OPerationS) for GitOps-friendly secrets encryption enabling secrets-in-Git workflows with KMS-encrypted files and granular access control
- Configure Sealed Secrets for Kubernetes encrypting secrets at rest in Git repositories with cluster-side decryption enabling GitOps secret management
- Architect External Secrets Operator integration synchronizing secrets from external secret stores (Vault, AWS, GCP) into Kubernetes Secrets with automatic rotation
- Design ML credential management strategies for model registry access, cloud credentials, database passwords, and API keys with least-privilege access and rotation policies
- Implement secrets rotation workflows with automated rotation schedules, zero-downtime updates, and application-level secret reloading without service restarts
- Build secrets injection patterns using Vault Agent, init containers, or CSI drivers providing secrets to applications without hardcoding in manifests or environment variables
- Architect secrets audit and compliance systems with access logging, secret usage tracking, compliance reporting, and anomaly detection for unauthorized access

## Table of Contents
1. [Secrets Management Challenges](#secrets-management-challenges)
2. [HashiCorp Vault](#hashicorp-vault)
3. [SOPS - Secrets OPerationS](#sops---secrets-operations)
4. [Sealed Secrets](#sealed-secrets)
5. [External Secrets Operator](#external-secrets-operator)
6. [ML Credentials Best Practices](#ml-credentials-best-practices)

## Secrets Management Challenges

Managing secrets (API keys, passwords, certificates, tokens) in ML infrastructure presents unique challenges.

### Common Secrets in ML Infrastructure

- **Cloud credentials**: AWS/GCP/Azure access keys
- **Database passwords**: PostgreSQL, MongoDB, Redis
- **API keys**: MLflow, third-party services
- **Model artifacts**: Access tokens for model registries
- **Data access**: S3/GCS credentials
- **Service accounts**: Kubernetes service account tokens
- **TLS certificates**: HTTPS, mTLS
- **SSH keys**: Git repository access

### Anti-Patterns to Avoid

**DON'T:**
```yaml
# Never do this!
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-config
data:
  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  AWS_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  DATABASE_PASSWORD: "super-secret-password"
```

```python
# Never do this!
# config.py
DATABASE_URL = "postgresql://admin:password123@db.example.com/ml"
API_KEY = "sk-1234567890abcdef"
```

```bash
# Never do this!
git commit -m "Add credentials" credentials.json
```

**DO:**
- Use dedicated secrets management tools
- Encrypt secrets at rest and in transit
- Rotate secrets regularly
- Apply least privilege access
- Audit secret access
- Separate secrets from code

## HashiCorp Vault

Vault is a tool for secrets management, encryption as a service, and privileged access management.

### Vault Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vault Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vault API (HTTP/gRPC)                               │   │
│  └───────────────┬──────────────────────────────────────┘   │
│                  │                                           │
│  ┌───────────────▼──────────────────────────────────────┐   │
│  │  Auth Methods (AWS, K8s, LDAP, GitHub)              │   │
│  └───────────────┬──────────────────────────────────────┘   │
│                  │                                           │
│  ┌───────────────▼──────────────────────────────────────┐   │
│  │  Policy Engine (ACL)                                 │   │
│  └───────────────┬──────────────────────────────────────┘   │
│                  │                                           │
│  ┌───────────────▼──────────────────────────────────────┐   │
│  │  Secrets Engines                                     │   │
│  │  ├─ KV (Key/Value)                                   │   │
│  │  ├─ AWS (Dynamic Credentials)                        │   │
│  │  ├─ Database (Dynamic DB Credentials)                │   │
│  │  ├─ PKI (Certificates)                               │   │
│  │  └─ Transit (Encryption as Service)                  │   │
│  └───────────────┬──────────────────────────────────────┘   │
│                  │                                           │
│  ┌───────────────▼──────────────────────────────────────┐   │
│  │  Storage Backend (Consul, etcd, S3, etc.)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Installation on Kubernetes

```bash
# Add HashiCorp Helm repository
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set "server.ha.enabled=true" \
  --set "server.ha.replicas=3" \
  --set "ui.enabled=true" \
  --set "ui.serviceType=LoadBalancer"
```

```yaml
# vault-values.yaml (production configuration)
server:
  ha:
    enabled: true
    replicas: 3
    raft:
      enabled: true
      setNodeId: true

      config: |
        ui = true

        listener "tcp" {
          address = "[::]:8200"
          cluster_address = "[::]:8201"
          tls_disable = false
          tls_cert_file = "/vault/tls/tls.crt"
          tls_key_file  = "/vault/tls/tls.key"
        }

        storage "raft" {
          path = "/vault/data"

          retry_join {
            leader_api_addr = "https://vault-0.vault-internal:8200"
          }
          retry_join {
            leader_api_addr = "https://vault-1.vault-internal:8200"
          }
          retry_join {
            leader_api_addr = "https://vault-2.vault-internal:8200"
          }
        }

        service_registration "kubernetes" {}

  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

ui:
  enabled: true
  serviceType: LoadBalancer
```

### Initialize and Unseal Vault

```bash
# Initialize Vault (run once)
kubectl exec -n vault vault-0 -- vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-keys.json

# IMPORTANT: Store vault-keys.json securely!

# Extract unseal keys and root token
export UNSEAL_KEY_1=$(jq -r '.unseal_keys_b64[0]' vault-keys.json)
export UNSEAL_KEY_2=$(jq -r '.unseal_keys_b64[1]' vault-keys.json)
export UNSEAL_KEY_3=$(jq -r '.unseal_keys_b64[2]' vault-keys.json)
export ROOT_TOKEN=$(jq -r '.root_token' vault-keys.json)

# Unseal Vault (need to do for each pod)
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_1
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_2
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_3

# Login
kubectl exec -n vault vault-0 -- vault login $ROOT_TOKEN
```

### Configure Kubernetes Auth

```bash
# Enable Kubernetes auth
kubectl exec -n vault vault-0 -- vault auth enable kubernetes

# Configure Kubernetes auth
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# Create policy for ML applications
kubectl exec -n vault vault-0 -- vault policy write ml-app - <<EOF
path "secret/data/ml/*" {
  capabilities = ["read"]
}

path "database/creds/ml-readonly" {
  capabilities = ["read"]
}

path "aws/creds/ml-s3-access" {
  capabilities = ["read"]
}
EOF

# Create role for Kubernetes service account
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/role/ml-app \
  bound_service_account_names=ml-app-sa \
  bound_service_account_namespaces=ml-training,ml-serving \
  policies=ml-app \
  ttl=24h
```

### Store and Retrieve Secrets

```bash
# Enable KV secrets engine
kubectl exec -n vault vault-0 -- vault secrets enable -path=secret kv-v2

# Store secrets
kubectl exec -n vault vault-0 -- vault kv put secret/ml/mlflow \
  db_password="super-secret-password" \
  s3_access_key="AKIAIOSFODNN7EXAMPLE" \
  s3_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE"

# Retrieve secret
kubectl exec -n vault vault-0 -- vault kv get secret/ml/mlflow

# Retrieve specific field
kubectl exec -n vault vault-0 -- vault kv get -field=db_password secret/ml/mlflow
```

### Vault Agent Injector

Automatically inject secrets into pods:

```yaml
# pod-with-vault-secrets.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-app-sa
  namespace: ml-training

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training-app
  namespace: ml-training
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-training
  template:
    metadata:
      labels:
        app: ml-training
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "ml-app"
        vault.hashicorp.com/agent-inject-secret-mlflow: "secret/data/ml/mlflow"
        vault.hashicorp.com/agent-inject-template-mlflow: |
          {{- with secret "secret/data/ml/mlflow" -}}
          export MLFLOW_TRACKING_URI="http://mlflow:5000"
          export DB_PASSWORD="{{ .Data.data.db_password }}"
          export AWS_ACCESS_KEY_ID="{{ .Data.data.s3_access_key }}"
          export AWS_SECRET_ACCESS_KEY="{{ .Data.data.s3_secret_key }}"
          {{- end -}}

    spec:
      serviceAccountName: ml-app-sa
      containers:
      - name: app
        image: ml-training:v1.0.0
        command: ["/bin/sh", "-c"]
        args:
          - source /vault/secrets/mlflow && python train.py
```

### Dynamic Database Credentials

```bash
# Enable database secrets engine
kubectl exec -n vault vault-0 -- vault secrets enable database

# Configure PostgreSQL connection
kubectl exec -n vault vault-0 -- vault write database/config/mlflow-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="ml-readonly,ml-readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mlflow" \
  username="vault" \
  password="vault-password"

# Create read-only role
kubectl exec -n vault vault-0 -- vault write database/roles/ml-readonly \
  db_name=mlflow-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Create read-write role
kubectl exec -n vault vault-0 -- vault write database/roles/ml-readwrite \
  db_name=mlflow-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Generate credentials (automatic rotation)
kubectl exec -n vault vault-0 -- vault read database/creds/ml-readonly
```

### Dynamic AWS Credentials

```bash
# Enable AWS secrets engine
kubectl exec -n vault vault-0 -- vault secrets enable aws

# Configure AWS credentials
kubectl exec -n vault vault-0 -- vault write aws/config/root \
  access_key=$AWS_ACCESS_KEY_ID \
  secret_key=$AWS_SECRET_ACCESS_KEY \
  region=us-west-2

# Create role for S3 access
kubectl exec -n vault vault-0 -- vault write aws/roles/ml-s3-access \
  credential_type=iam_user \
  policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ml-data-*",
        "arn:aws:s3:::ml-data-*/*"
      ]
    }
  ]
}
EOF

# Generate AWS credentials
kubectl exec -n vault vault-0 -- vault read aws/creds/ml-s3-access
```

## SOPS - Secrets OPerationS

SOPS encrypts files using AWS KMS, GCP KMS, Azure Key Vault, or PGP.

### Installation

```bash
# Install sops
brew install sops

# Or download binary
curl -LO https://github.com/mozilla/sops/releases/latest/download/sops-v3.8.1.linux.amd64
sudo mv sops-v3.8.1.linux.amd64 /usr/local/bin/sops
sudo chmod +x /usr/local/bin/sops
```

### Encrypt Secrets with AWS KMS

```yaml
# secrets.yaml (before encryption)
apiVersion: v1
kind: Secret
metadata:
  name: ml-secrets
  namespace: ml-training
type: Opaque
stringData:
  aws_access_key_id: AKIAIOSFODNN7EXAMPLE
  aws_secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
  mlflow_password: super-secret-password
```

```bash
# Create KMS key
aws kms create-key --description "SOPS encryption key for ML secrets"
export KMS_KEY_ARN="arn:aws:kms:us-west-2:123456789012:key/12345678-1234-1234-1234-123456789012"

# Encrypt file
sops --encrypt --kms $KMS_KEY_ARN secrets.yaml > secrets.enc.yaml

# Encrypted file can be committed to Git!
git add secrets.enc.yaml
git commit -m "Add encrypted secrets"
```

```yaml
# secrets.enc.yaml (after encryption)
apiVersion: v1
kind: Secret
metadata:
    name: ml-secrets
    namespace: ml-training
type: Opaque
stringData:
    aws_access_key_id: ENC[AES256_GCM,data:iHGPPu2qxCl...,iv:...]
    aws_secret_access_key: ENC[AES256_GCM,data:kJzL8fN...,iv:...]
    mlflow_password: ENC[AES256_GCM,data:mQwE9rT...,iv:...]
sops:
    kms:
    -   arn: arn:aws:kms:us-west-2:123456789012:key/...
        created_at: "2024-01-15T10:30:00Z"
        enc: AQICAHh...
```

```bash
# Decrypt and apply
sops --decrypt secrets.enc.yaml | kubectl apply -f -

# Edit encrypted file
sops secrets.enc.yaml

# Decrypt to stdout
sops --decrypt secrets.enc.yaml
```

### SOPS with FluxCD

```yaml
# flux-system/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: ml-secrets
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: ml-gitops
  path: ./secrets
  prune: true

  decryption:
    provider: sops
    secretRef:
      name: sops-kms
```

### .sops.yaml Configuration

```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets/production/.*\.yaml
    kms: arn:aws:kms:us-west-2:123456789012:key/prod-key
    aws_profile: production

  - path_regex: secrets/staging/.*\.yaml
    kms: arn:aws:kms:us-west-2:123456789012:key/staging-key
    aws_profile: staging

  - path_regex: secrets/dev/.*\.yaml
    kms: arn:aws:kms:us-west-2:123456789012:key/dev-key
    aws_profile: development

  # Encrypt only specific fields
  - path_regex: .*config\.yaml
    encrypted_regex: ^(password|api_key|secret)$
```

## Sealed Secrets

Sealed Secrets allow you to encrypt Kubernetes Secrets and commit them to Git safely.

### Installation

```bash
# Install controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal

# Or download binary
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-linux-amd64
sudo install -m 755 kubeseal-linux-amd64 /usr/local/bin/kubeseal
```

### Create Sealed Secret

```bash
# Create normal secret (DON'T commit this!)
kubectl create secret generic ml-secrets \
  --from-literal=aws_access_key_id=AKIAIOSFODNN7EXAMPLE \
  --from-literal=aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE \
  --from-literal=mlflow_password=super-secret \
  --dry-run=client -o yaml > secret.yaml

# Seal the secret (encrypts with controller's public key)
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# sealed-secret.yaml can be safely committed to Git!
git add sealed-secret.yaml
git commit -m "Add sealed ML secrets"

# Apply sealed secret
kubectl apply -f sealed-secret.yaml

# Controller automatically creates the actual secret
kubectl get secret ml-secrets -n ml-training
```

```yaml
# sealed-secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: ml-secrets
  namespace: ml-training
spec:
  encryptedData:
    aws_access_key_id: AgBg8F7R...  # encrypted
    aws_secret_access_key: AgC9H2S...  # encrypted
    mlflow_password: AgD1K3T...  # encrypted
  template:
    metadata:
      name: ml-secrets
      namespace: ml-training
    type: Opaque
```

### Scope Control

```bash
# Strict scope: Secret can only be used in specific namespace with specific name
kubeseal --scope strict < secret.yaml > sealed-secret.yaml

# Namespace-wide scope: Can be used in any name within the namespace
kubeseal --scope namespace-wide < secret.yaml > sealed-secret.yaml

# Cluster-wide scope: Can be used anywhere (least secure)
kubeseal --scope cluster-wide < secret.yaml > sealed-secret.yaml
```

## External Secrets Operator

External Secrets Operator (ESO) synchronizes secrets from external secret stores into Kubernetes.

### Installation

```bash
# Add Helm repository
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

# Install operator
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace \
  --set installCRDs=true
```

### SecretStore Configuration

**AWS Secrets Manager:**
```yaml
# secret-store-aws.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: ml-training
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
```

**HashiCorp Vault:**
```yaml
# secret-store-vault.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: ml-training
spec:
  provider:
    vault:
      server: "https://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "ml-app"
          serviceAccountRef:
            name: ml-app-sa
```

### ExternalSecret Resources

```yaml
# external-secret-mlflow.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mlflow-credentials
  namespace: ml-training
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore

  target:
    name: mlflow-credentials
    creationPolicy: Owner

  data:
  - secretKey: db_password
    remoteRef:
      key: secret/ml/mlflow
      property: db_password

  - secretKey: aws_access_key_id
    remoteRef:
      key: secret/ml/mlflow
      property: s3_access_key

  - secretKey: aws_secret_access_key
    remoteRef:
      key: secret/ml/mlflow
      property: s3_secret_key
```

```yaml
# external-secret-aws.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: ml-aws-credentials
  namespace: ml-training
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore

  target:
    name: ml-aws-credentials
    creationPolicy: Owner

  dataFrom:
  - extract:
      key: ml/training/credentials  # All key-value pairs from this secret
```

### ClusterSecretStore

Share secret store across namespaces:

```yaml
# cluster-secret-store.yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-cluster-store
spec:
  provider:
    vault:
      server: "https://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "cluster-secrets-reader"
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets-system
```

## ML Credentials Best Practices

### 1. Principle of Least Privilege

```yaml
# ml-training-rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-training-sa
  namespace: ml-training

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ml-training-role
  namespace: ml-training
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["mlflow-credentials", "aws-credentials"]
  verbs: ["get"]

- apiGroups: ["batch"]
  resources: ["jobs"]
  verbs: ["create", "get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ml-training-rolebinding
  namespace: ml-training
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ml-training-role
subjects:
- kind: ServiceAccount
  name: ml-training-sa
  namespace: ml-training
```

### 2. Secret Rotation

```python
# scripts/rotate_secrets.py
"""
Automated secret rotation
"""
import boto3
import hvac
from datetime import datetime, timedelta

class SecretRotator:
    """Rotate secrets in Vault and AWS"""

    def __init__(self, vault_addr: str, vault_token: str):
        self.vault_client = hvac.Client(url=vault_addr, token=vault_token)
        self.aws_client = boto3.client('secretsmanager')

    def rotate_database_password(self, secret_path: str):
        """Rotate database password"""

        # Generate new password
        import secrets
        new_password = secrets.token_urlsafe(32)

        # Update in Vault
        self.vault_client.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret={'password': new_password, 'rotated_at': datetime.now().isoformat()}
        )

        # Update actual database password
        # ... (database-specific logic)

        print(f"Rotated password for {secret_path}")

    def rotate_aws_keys(self, iam_user: str):
        """Rotate AWS access keys"""

        iam = boto3.client('iam')

        # List existing keys
        response = iam.list_access_keys(UserName=iam_user)
        old_keys = response['AccessKeyMetadata']

        # Create new key
        new_key = iam.create_access_key(UserName=iam_user)
        access_key = new_key['AccessKey']

        # Update in Vault
        self.vault_client.secrets.kv.v2.create_or_update_secret(
            path=f'aws/{iam_user}',
            secret={
                'access_key_id': access_key['AccessKeyId'],
                'secret_access_key': access_key['SecretAccessKey'],
                'rotated_at': datetime.now().isoformat()
            }
        )

        # Delete old keys (after verification)
        for old_key in old_keys[:-1]:  # Keep most recent
            iam.delete_access_key(
                UserName=iam_user,
                AccessKeyId=old_key['AccessKeyId']
            )

        print(f"Rotated AWS keys for {iam_user}")

    def schedule_rotation(self, secret_path: str, rotation_days: int = 90):
        """Schedule automatic rotation"""

        # Check last rotation
        secret = self.vault_client.secrets.kv.v2.read_secret_version(path=secret_path)
        rotated_at = datetime.fromisoformat(secret['data']['data'].get('rotated_at', '2000-01-01'))

        # Rotate if needed
        if datetime.now() - rotated_at > timedelta(days=rotation_days):
            self.rotate_database_password(secret_path)

# Usage
rotator = SecretRotator('https://vault.example.com', 'vault-token')
rotator.rotate_database_password('ml/mlflow/db')
rotator.rotate_aws_keys('ml-training-user')
```

### 3. Secret Scanning

```yaml
# .github/workflows/secret-scan.yaml
name: Secret Scanning

on:
  push:
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Detect-secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --all-files --force-use-all-plugins
```

### 4. Audit Logging

```python
# scripts/audit_secret_access.py
"""
Audit secret access from Vault
"""
import hvac
from datetime import datetime, timedelta

class SecretAuditor:
    """Audit secret access"""

    def __init__(self, vault_addr: str, vault_token: str):
        self.client = hvac.Client(url=vault_addr, token=vault_token)

    def get_secret_access_logs(self, days: int = 7):
        """Get secret access logs"""

        # Query audit logs
        # Note: Requires audit device enabled
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Parse audit logs
        logs = self.client.sys.read_health()  # Simplified

        access_report = {
            'total_access': 0,
            'by_path': {},
            'by_user': {},
            'anomalies': []
        }

        # Analyze logs
        # ... (log parsing logic)

        return access_report

    def detect_anomalies(self, logs):
        """Detect unusual access patterns"""

        anomalies = []

        # Check for unusual access times
        # Check for unusual access frequency
        # Check for access from unexpected IPs

        return anomalies

# Usage
auditor = SecretAuditor('https://vault.example.com', 'vault-token')
report = auditor.get_secret_access_logs(days=30)
print(f"Total secret access: {report['total_access']}")
```

## Summary

Secrets management is critical for ML infrastructure security:

**Key Principles:**
1. Never commit secrets to Git
2. Encrypt secrets at rest and in transit
3. Rotate secrets regularly
4. Apply least privilege access
5. Audit all secret access
6. Automate secret management

**Tools:**
- **Vault**: Comprehensive secrets management
- **SOPS**: File encryption for GitOps
- **Sealed Secrets**: Kubernetes-native encryption
- **External Secrets Operator**: Sync from external stores

**Best Practices:**
- Use dedicated service accounts
- Implement secret rotation
- Enable audit logging
- Scan for leaked secrets
- Automate secret lifecycle

## Next Steps

- Review [Module Resources](../resources/recommended-reading.md)
- Complete [Lab exercises](../exercises/)
- Implement secrets management in your infrastructure
- Set up automated rotation

## Additional Resources

- [Vault Documentation](https://www.vaultproject.io/docs)
- [SOPS Documentation](https://github.com/mozilla/sops)
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- [Secret Management Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
