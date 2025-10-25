# TrainingJob Operator Troubleshooting Guide

Common issues and solutions for the TrainingJob Kubernetes Operator.

## Quick Diagnostics

```bash
# Check everything
kubectl get all -n trainingjob-system
kubectl get trainingjobs -A
kubectl logs -n trainingjob-system -l app=trainingjob-operator --tail=100
```

## Operator Issues

### Operator Pod CrashLoopBackOff

**Symptoms**:
```
NAME                                   READY   STATUS             RESTARTS
trainingjob-operator-abc123           0/1     CrashLoopBackOff   5
```

**Diagnosis**:
```bash
kubectl logs -n trainingjob-system trainingjob-operator-abc123
kubectl describe pod -n trainingjob-system trainingjob-operator-abc123
```

**Common Causes**:

1. **Missing CRD**
   ```bash
   kubectl get crd trainingjobs.mlplatform.example.com
   # If not found, install CRD
   kubectl apply -f deploy/crd.yaml
   ```

2. **RBAC Permissions**
   ```bash
   kubectl auth can-i list trainingjobs \
     --as=system:serviceaccount:trainingjob-system:trainingjob-operator
   # Should return "yes"
   ```

3. **Invalid Configuration**
   - Check .env file
   - Verify environment variables in deployment

### Operator Not Reconciling

**Symptoms**:
- New TrainingJobs stay in Pending
- Changes to TrainingJobs not processed

**Diagnosis**:
```bash
# Check operator logs
kubectl logs -n trainingjob-system \
  -l app=trainingjob-operator | grep "reconcil"

# Check for errors
kubectl logs -n trainingjob-system \
  -l app=trainingjob-operator | grep -i error
```

**Solutions**:

1. **Restart Operator**
   ```bash
   kubectl rollout restart deployment/trainingjob-operator \
     -n trainingjob-system
   ```

2. **Check Watch Mechanism**
   - Verify operator has list/watch permissions
   - Check for API server connectivity issues

## TrainingJob Issues

### Job Stuck in Pending

**Symptoms**:
```
NAME      STATUS    AGE
my-job    Pending   10m
```

**Diagnosis**:
```bash
kubectl describe tj my-job
kubectl get events --field-selector involvedObject.name=my-job
```

**Common Causes**:

1. **Validation Errors**
   ```bash
   # Check status conditions
   kubectl get tj my-job -o jsonpath='{.status.conditions}'
   ```
   **Solution**: Fix validation errors in spec

2. **Resource Quota Exceeded**
   ```bash
   kubectl describe resourcequota -n default
   ```
   **Solution**: Increase quota or reduce resource requests

3. **No Available Nodes**
   ```bash
   kubectl get nodes
   kubectl describe nodes | grep -A 5 "Allocated resources"
   ```
   **Solution**: Scale cluster or reduce resource requirements

### Pods Not Created

**Symptoms**:
- Job shows Running but no pods exist

**Diagnosis**:
```bash
kubectl get pods -l trainingjob=my-job
kubectl get events -n default | grep my-job
```

**Common Causes**:

1. **Operator RBAC Issues**
   ```bash
   kubectl auth can-i create pods \
     --as=system:serviceaccount:trainingjob-system:trainingjob-operator \
     -n default
   ```
   **Solution**: Update ClusterRole to include pod creation

2. **Image Pull Errors**
   ```bash
   kubectl describe pod my-job-0 | grep -A 5 "Events"
   ```
   **Solution**: Fix image name or add imagePullSecrets

### Job Failing Immediately

**Symptoms**:
```
NAME      STATUS   RESTARTS   AGE
my-job-0  Error    3          1m
```

**Diagnosis**:
```bash
kubectl logs my-job-0
kubectl logs my-job-0 --previous
kubectl describe pod my-job-0
```

**Common Causes**:

1. **Application Errors**
   - Check logs for stack traces
   - Verify command and args

2. **Missing Dependencies**
   - Check if required packages installed in image
   - Verify environment variables

3. **Resource Limits Too Low**
   ```bash
   kubectl describe pod my-job-0 | grep -A 5 "Limits"
   ```
   **Solution**: Increase memory/CPU limits

## Distributed Training Issues

### Pods Can't Communicate

**Symptoms**:
- Pods timeout connecting to master
- "Connection refused" errors

**Diagnosis**:
```bash
# Check services
kubectl get svc -l trainingjob=my-job

# Check network policies
kubectl get networkpolicies

# Test connectivity
kubectl exec my-job-0 -- ping my-job-1.my-job-headless
```

**Solutions**:

1. **Create Headless Service**
   - Operator should create automatically
   - Verify service exists

2. **Network Policy Blocking**
   ```bash
   kubectl get networkpolicies -n default
   ```
   - Allow pod-to-pod communication

3. **DNS Issues**
   ```bash
   kubectl exec my-job-0 -- nslookup my-job-headless
   ```

### NCCL Errors

**Symptoms**:
```
NCCL error: unhandled system error
```

**Diagnosis**:
```bash
kubectl logs my-job-0 | grep NCCL
```

**Solutions**:

1. **Set NCCL Environment Variables**
   ```yaml
   env:
     - name: NCCL_DEBUG
       value: INFO
     - name: NCCL_SOCKET_IFNAME
       value: eth0
   ```

2. **Enable Host Network** (if needed)
   ```yaml
   hostNetwork: true
   ```

## Checkpoint Issues

### Checkpoints Not Saving

**Symptoms**:
- No checkpoint files in storage
- Checkpoint errors in logs

**Diagnosis**:
```bash
# Check checkpoint configuration
kubectl get tj my-job -o jsonpath='{.spec.checkpoint}'

# Check PVC
kubectl get pvc
kubectl describe pvc training-checkpoints

# Check pod mounts
kubectl describe pod my-job-0 | grep -A 5 "Mounts"
```

**Solutions**:

1. **PVC Not Bound**
   ```bash
   kubectl get pvc training-checkpoints
   # If Pending, check PV availability
   kubectl get pv
   ```

2. **Insufficient Storage**
   ```bash
   kubectl describe pvc training-checkpoints | grep "Used"
   ```

3. **Permission Issues**
   - Ensure pod has write access to volume
   - Check SecurityContext

## Resource Issues

### Out of Memory (OOM)

**Symptoms**:
```
NAME      STATUS      RESTARTS   AGE
my-job-0  OOMKilled  1          30s
```

**Diagnosis**:
```bash
kubectl describe pod my-job-0 | grep -i "OOM"
kubectl top pod my-job-0
```

**Solutions**:

1. **Increase Memory Limits**
   ```yaml
   resources:
     limits:
       memory: "16Gi"  # Increase from 8Gi
   ```

2. **Reduce Batch Size**
   - Modify training script args

3. **Enable GPU Memory Growth**
   ```yaml
   env:
     - name: TF_FORCE_GPU_ALLOW_GROWTH
       value: "true"
   ```

### GPU Not Detected

**Symptoms**:
```
RuntimeError: No CUDA GPUs are available
```

**Diagnosis**:
```bash
# Check GPU resource request
kubectl get tj my-job -o jsonpath='{.spec.resources.requests}'

# Check node GPU availability
kubectl describe nodes | grep -A 5 "nvidia.com/gpu"

# Check from pod
kubectl exec my-job-0 -- nvidia-smi
```

**Solutions**:

1. **Add GPU Resource Request**
   ```yaml
   resources:
     requests:
       nvidia.com/gpu: "1"
   ```

2. **Check Node Labels**
   ```bash
   kubectl get nodes -l nvidia.com/gpu=true
   ```

3. **Verify GPU Operator**
   ```bash
   kubectl get pods -n gpu-operator-resources
   ```

## Performance Issues

### Slow Reconciliation

**Symptoms**:
- Long delays between job creation and pod creation
- Operator CPU/memory high

**Diagnosis**:
```bash
# Check operator metrics
curl http://localhost:8000/metrics | grep reconciliation_duration

# Check operator resources
kubectl top pod -n trainingjob-system
```

**Solutions**:

1. **Increase Operator Resources**
   ```bash
   kubectl set resources deployment/trainingjob-operator \
     --limits=cpu=2,memory=2Gi \
     -n trainingjob-system
   ```

2. **Increase Worker Threads**
   ```bash
   kubectl set env deployment/trainingjob-operator \
     WORKER_THREADS=20 \
     -n trainingjob-system
   ```

## Common Error Messages

### "Validation failed: framework"

**Error**:
```
Validation failed: framework: Unsupported framework 'sklearn'
```

**Solution**: Use supported framework (`pytorch`, `tensorflow`, `jax`, `mxnet`)

### "Resource not found"

**Error**:
```
Error: trainingjobs.mlplatform.example.com not found
```

**Solution**: Install CRD
```bash
kubectl apply -f deploy/crd.yaml
```

### "Forbidden: User cannot create resource"

**Error**:
```
Error creating: pods is forbidden
```

**Solution**: Fix RBAC permissions
```bash
kubectl apply -f deploy/rbac.yaml
```

## Debug Mode

Enable debug logging:

```bash
kubectl set env deployment/trainingjob-operator \
  LOG_LEVEL=DEBUG \
  -n trainingjob-system

# View debug logs
kubectl logs -f -n trainingjob-system \
  -l app=trainingjob-operator
```

## Getting Help

1. **Check logs thoroughly**
2. **Search GitHub issues**: https://github.com/your-org/trainingjob-operator/issues
3. **Ask in Slack**: #ml-platform-ops
4. **File a bug** with:
   - Operator logs
   - TrainingJob YAML
   - Pod events and logs
   - Kubernetes version

## Quick Fixes Checklist

- [ ] Operator pod running?
- [ ] CRD installed?
- [ ] RBAC configured?
- [ ] TrainingJob spec valid?
- [ ] Sufficient cluster resources?
- [ ] Network connectivity OK?
- [ ] Storage available?
- [ ] Recent operator logs reviewed?
