# TrainingJob Operator Runbook

Operational procedures for managing the TrainingJob Kubernetes Operator.

## Daily Operations

### Check Operator Health

```bash
# Check operator pods
kubectl get pods -n trainingjob-system

# Check operator logs
kubectl logs -n trainingjob-system \
  -l app=trainingjob-operator \
  --tail=100

# Check metrics
curl http://localhost:8000/metrics
```

### Monitor Active Jobs

```bash
# List all training jobs
kubectl get trainingjobs -A

# Check job status
kubectl get tj -A -o wide

# Watch for changes
kubectl get tj -A --watch
```

### Review Metrics

```bash
# Operator metrics
kubectl port-forward -n trainingjob-system \
  svc/trainingjob-operator 8000:8000

# View in browser
open http://localhost:8000/metrics
```

## Common Procedures

### 1. Deploy New Training Job

```bash
# Create job from template
kubectl apply -f examples/pytorch-distributed.yaml

# Verify creation
kubectl get tj my-training-job -o yaml

# Monitor status
kubectl describe tj my-training-job

# Watch logs
kubectl logs -f -l trainingjob=my-training-job
```

### 2. Scale Training Job

```bash
# Update replicas
kubectl patch tj my-job -p '{"spec":{"replicas":8}}'

# Verify scaling
kubectl get pods -l trainingjob=my-job
```

### 3. Create Manual Checkpoint

```bash
# TODO: Implement checkpoint API
# For now, checkpoints are automatic based on interval
```

### 4. Restart Failed Job

```bash
# Delete and recreate
kubectl delete tj failed-job
kubectl apply -f failed-job.yaml

# Or patch backoff limit
kubectl patch tj failed-job -p '{"spec":{"backoffLimit":10}}'
```

### 5. View Job Logs

```bash
# All replicas
kubectl logs -l trainingjob=my-job --tail=100

# Specific replica
kubectl logs my-job-0 --tail=100

# Follow logs
kubectl logs -f my-job-0

# Previous container (if crashed)
kubectl logs my-job-0 --previous
```

### 6. Debug Job Issues

```bash
# Describe job
kubectl describe tj my-job

# Check events
kubectl get events -n default \
  --field-selector involvedObject.name=my-job

# Check pod status
kubectl get pods -l trainingjob=my-job
kubectl describe pod my-job-0

# Get pod logs
kubectl logs my-job-0

# Exec into pod
kubectl exec -it my-job-0 -- /bin/bash
```

## Incident Response

### Operator Not Responding

**Symptoms**:
- No reconciliation happening
- Jobs stuck in Pending
- Operator logs show errors

**Steps**:
1. Check operator pod status
   ```bash
   kubectl get pods -n trainingjob-system
   ```

2. Check logs for errors
   ```bash
   kubectl logs -n trainingjob-system \
     -l app=trainingjob-operator --tail=200
   ```

3. Restart operator
   ```bash
   kubectl rollout restart deployment/trainingjob-operator \
     -n trainingjob-system
   ```

4. Verify recovery
   ```bash
   kubectl logs -f -n trainingjob-system \
     -l app=trainingjob-operator
   ```

### Training Jobs Not Starting

**Symptoms**:
- Jobs stuck in Pending
- Pods not created

**Steps**:
1. Check job status
   ```bash
   kubectl describe tj stuck-job
   ```

2. Check operator logs
   ```bash
   kubectl logs -n trainingjob-system \
     -l app=trainingjob-operator | grep stuck-job
   ```

3. Verify RBAC permissions
   ```bash
   kubectl auth can-i create pods \
     --as=system:serviceaccount:trainingjob-system:trainingjob-operator
   ```

4. Check cluster resources
   ```bash
   kubectl top nodes
   kubectl describe nodes
   ```

### High Memory Usage

**Steps**:
1. Check operator memory
   ```bash
   kubectl top pods -n trainingjob-system
   ```

2. Review resource limits
   ```bash
   kubectl get deployment trainingjob-operator \
     -n trainingjob-system -o yaml | grep -A 5 resources
   ```

3. Increase limits if needed
   ```bash
   kubectl set resources deployment/trainingjob-operator \
     --limits=memory=2Gi \
     -n trainingjob-system
   ```

## Maintenance

### Update Operator

```bash
# Update image
kubectl set image deployment/trainingjob-operator \
  operator=your-registry/trainingjob-operator:v1.1.0 \
  -n trainingjob-system

# Watch rollout
kubectl rollout status deployment/trainingjob-operator \
  -n trainingjob-system

# Verify version
kubectl logs -n trainingjob-system \
  -l app=trainingjob-operator | grep "version"
```

### Backup TrainingJobs

```bash
# Backup all jobs
kubectl get trainingjobs -A -o yaml > backup-$(date +%Y%m%d).yaml

# Backup specific namespace
kubectl get trainingjobs -n production -o yaml > prod-backup.yaml
```

### Clean Up Old Jobs

```bash
# Delete completed jobs older than 7 days
kubectl get trainingjobs -A --no-headers | \
  awk '{print $1,$2}' | \
  while read ns name; do
    status=$(kubectl get tj $name -n $ns -o jsonpath='{.status.phase}')
    if [ "$status" = "Succeeded" ] || [ "$status" = "Failed" ]; then
      kubectl delete tj $name -n $ns
    fi
  done
```

## Monitoring

### Key Metrics

- `trainingjob_reconciliations_total`: Total reconciliations
- `trainingjob_reconciliations_duration_seconds`: Reconciliation time
- `trainingjob_active_jobs`: Number of active jobs
- `trainingjob_failed_jobs_total`: Failed job count

### Alerts

**High Reconciliation Failures**:
```promql
rate(trainingjob_reconciliations_failed_total[5m]) > 0.1
```

**Slow Reconciliation**:
```promql
histogram_quantile(0.99,
  trainingjob_reconciliation_duration_seconds_bucket) > 60
```

## Capacity Planning

### Resource Usage

```bash
# Check operator resource usage
kubectl top pods -n trainingjob-system

# Check training job resource usage
kubectl top pods -l app=ml-training
```

### Scale Recommendations

- **< 100 jobs**: 1 operator replica, 1 CPU, 512Mi
- **100-500 jobs**: 2 replicas, 2 CPU, 1Gi
- **> 500 jobs**: 3+ replicas, 4 CPU, 2Gi

## Emergency Procedures

### Stop All Training

```bash
# Scale all jobs to 0
for job in $(kubectl get tj -A -o name); do
  kubectl patch $job -p '{"spec":{"replicas":0}}'
done
```

### Emergency Operator Shutdown

```bash
# Scale operator to 0
kubectl scale deployment/trainingjob-operator \
  --replicas=0 \
  -n trainingjob-system
```

### Restore from Backup

```bash
# Restore jobs
kubectl apply -f backup-20251017.yaml

# Verify restoration
kubectl get trainingjobs -A
```

## Contact Information

- **On-Call**: pagerduty.com/trainingjob-operator
- **Slack**: #ml-platform-ops
- **Docs**: https://docs.example.com/trainingjob-operator
