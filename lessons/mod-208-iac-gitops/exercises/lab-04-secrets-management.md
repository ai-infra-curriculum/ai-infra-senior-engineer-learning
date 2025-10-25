# Lab 4: Secrets Management

## Objectives

- Deploy HashiCorp Vault on Kubernetes
- Configure External Secrets Operator
- Manage ML API keys and credentials
- Implement secret rotation

## Duration

5 hours

## Lab Tasks

### Task 1: Install Vault

```bash
# Add Helm repo
helm repo add hashicorp https://helm.releases.hashicorp.com

# Install Vault
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set "server.ha.enabled=true" \
  --set "server.ha.replicas=3"

# Initialize Vault
kubectl exec -n vault vault-0 -- vault operator init -format=json > vault-keys.json

# Unseal Vault
UNSEAL_KEY=$(jq -r '.unseal_keys_b64[0]' vault-keys.json)
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY
```

### Task 2: Configure Kubernetes Auth

```bash
# Enable Kubernetes auth
kubectl exec -n vault vault-0 -- vault auth enable kubernetes

# Configure
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT"

# Create policy
kubectl exec -n vault vault-0 -- vault policy write ml-app - <<EOF
path "secret/data/ml/*" {
  capabilities = ["read"]
}
EOF

# Create role
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/role/ml-app \
  bound_service_account_names=ml-app-sa \
  bound_service_account_namespaces=ml-training \
  policies=ml-app \
  ttl=24h
```

### Task 3: Store Secrets

```bash
# Enable KV engine
kubectl exec -n vault vault-0 -- vault secrets enable -path=secret kv-v2

# Store ML secrets
kubectl exec -n vault vault-0 -- vault kv put secret/ml/mlflow \
  db_password="secure-password-123" \
  aws_access_key="AKIAIOSFODNN7EXAMPLE" \
  aws_secret_key="wJalrXUtnFEMI/K7MDENG"
```

### Task 4: Install External Secrets Operator

```bash
# Add Helm repo
helm repo add external-secrets https://charts.external-secrets.io

# Install operator
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace
```

### Task 5: Create ExternalSecret

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: ml-training
spec:
  provider:
    vault:
      server: "http://vault.vault:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "ml-app"
          serviceAccountRef:
            name: ml-app-sa

---
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
  data:
  - secretKey: password
    remoteRef:
      key: secret/ml/mlflow
      property: db_password
```

### Task 6: Use Secrets in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ml-app
  namespace: ml-training
spec:
  serviceAccountName: ml-app-sa
  containers:
  - name: app
    image: ml-app:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: mlflow-credentials
          key: password
```

## Exercises

1. Implement secret rotation
2. Set up dynamic database credentials
3. Configure AWS dynamic credentials
4. Add secret audit logging

## Submission

- Vault configuration
- ExternalSecret definitions
- Secret rotation script
- Audit log sample
