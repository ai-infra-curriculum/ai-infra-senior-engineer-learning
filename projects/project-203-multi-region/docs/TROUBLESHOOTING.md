# Multi-Region ML Platform - Troubleshooting Guide

> **TODO for students**: Add troubleshooting steps specific to your implementation, common issues observed in production, and debugging techniques.

## Table of Contents

1. [General Debugging Approach](#general-debugging-approach)
2. [Network & Connectivity Issues](#network--connectivity-issues)
3. [Model Serving Issues](#model-serving-issues)
4. [Replication Problems](#replication-problems)
5. [Performance Issues](#performance-issues)
6. [Deployment Failures](#deployment-failures)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Database Issues](#database-issues)
9. [Cost Anomalies](#cost-anomalies)
10. [Security & Access Issues](#security--access-issues)

## General Debugging Approach

### Step-by-Step Debugging Process

1. **Identify the Symptom**
   - What is the user-visible problem?
   - Which region(s) are affected?
   - When did it start?

2. **Gather Information**
   ```bash
   # Check overall health
   curl https://ml-platform.example.com/health

   # Check logs
   kubectl logs -f deployment/model-server -n ml-platform --context=<REGION>

   # Check metrics
   # Open Grafana dashboard

   # Check recent changes
   git log --since="1 day ago"
   kubectl rollout history deployment/model-server -n ml-platform
   ```

3. **Form Hypothesis**
   - Based on symptoms and data, what could be wrong?
   - Check similar past incidents

4. **Test Hypothesis**
   - Run targeted tests
   - Check specific logs or metrics

5. **Implement Fix**
   - Start with least disruptive fix
   - Have rollback plan ready

6. **Verify Resolution**
   - Run health checks
   - Monitor metrics

7. **Document**
   - Update runbook
   - Create post-mortem if major issue

**TODO for students**: Customize this process for your team's workflow.

## Network & Connectivity Issues

### Issue: Cannot Connect to Regional Endpoint

**Symptoms**: `curl: (7) Failed to connect to us-east-1.ml-platform.example.com`

**Debugging**:
```bash
# 1. Check DNS resolution
dig us-east-1.ml-platform.example.com
nslookup us-east-1.ml-platform.example.com

# 2. Check if endpoint is reachable
ping us-east-1.ml-platform.example.com
telnet us-east-1.ml-platform.example.com 443

# 3. Check load balancer
aws elbv2 describe-load-balancers --names ml-platform-us-east-1

# 4. Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxx

# 5. Check route53 health checks
aws route53 get-health-check-status --health-check-id xxxxx
```

**Solutions**:
- **DNS not resolving**: Update Route53 record or wait for DNS propagation
- **Firewall blocking**: Update security group rules to allow traffic
- **Load balancer down**: Check target group health in AWS console
- **Certificate issues**: Verify TLS certificate is valid

**TODO for students**: Add cloud provider-specific troubleshooting.

### Issue: High Cross-Region Latency

**Symptoms**: Requests between regions taking > 500ms

**Debugging**:
```bash
# Measure latency between regions
for src in us-east-1 eu-west-1 ap-southeast-1; do
  for dst in us-east-1 eu-west-1 ap-southeast-1; do
    echo "Testing $src -> $dst"
    kubectl --context=$src exec -it deploy/model-server -n ml-platform -- \
      curl -w "@curl-format.txt" -o /dev/null -s https://$dst.ml-platform.example.com/health
  done
done

# Check network path
traceroute us-east-1.ml-platform.example.com
mtr --report us-east-1.ml-platform.example.com
```

**Solutions**:
- **Geographic distance**: Use geo-routing to direct users to nearest region
- **Network congestion**: Check for unusual traffic patterns
- **Inefficient routing**: Verify VPC peering connections are working

**TODO for students**: Set up synthetic monitoring for cross-region latency.

## Model Serving Issues

### Issue: Model Inference Returning Errors

**Symptoms**: HTTP 500 errors, `Model failed to load`

**Debugging**:
```bash
# 1. Check pod logs
kubectl --context=us-east-1 logs -f deployment/model-server -n ml-platform

# 2. Check pod status
kubectl --context=us-east-1 get pods -n ml-platform
kubectl --context=us-east-1 describe pod <POD_NAME> -n ml-platform

# 3. Check model exists in storage
aws s3 ls s3://ml-models-us-east-1/models/model-v1.0.0.pth

# 4. Check model loading
kubectl --context=us-east-1 exec -it deploy/model-server -n ml-platform -- \
  python -c "import torch; torch.load('/models/model-v1.0.0.pth')"

# 5. Check resource constraints
kubectl --context=us-east-1 top pods -n ml-platform
```

**Solutions**:

**Error: `RuntimeError: CUDA out of memory`**
```bash
# Reduce batch size or increase GPU memory
kubectl --context=us-east-1 set resources deployment/model-server \
  -n ml-platform \
  --limits=nvidia.com/gpu=2
```

**Error: `Model file not found`**
```bash
# Check replication status
python -m src.replication.model_replicator --model-id model-v1.0.0 --check-status

# Re-replicate if needed
python -m src.replication.model_replicator --model-id model-v1.0.0 \
  --source-region us-east-1 --target-regions eu-west-1
```

**Error: `Model version mismatch`**
```bash
# Verify model version in deployment
kubectl --context=us-east-1 get deployment model-server -n ml-platform -o yaml | grep MODEL_VERSION

# Update if needed
kubectl --context=us-east-1 set env deployment/model-server \
  -n ml-platform MODEL_VERSION=v1.0.0
```

**TODO for students**: Add model-specific error handling.

### Issue: Slow Inference Times

**Symptoms**: P95 latency > 200ms

**Debugging**:
```bash
# 1. Profile inference time
kubectl --context=us-east-1 logs deployment/model-server -n ml-platform | grep "inference_time"

# 2. Check GPU utilization
kubectl --context=us-east-1 exec -it deploy/model-server -n ml-platform -- nvidia-smi

# 3. Check CPU/memory
kubectl --context=us-east-1 top pods -n ml-platform

# 4. Check batch size and concurrency
# Review application configuration

# 5. Check for model swapping
kubectl --context=us-east-1 logs deployment/model-server -n ml-platform | grep "model_load"
```

**Solutions**:
- **GPU underutilized**: Increase batch size
- **CPU bottleneck**: Scale horizontally or use larger instance type
- **Model too large**: Consider model optimization (quantization, distillation)
- **Disk I/O slow**: Use SSD-backed storage or cache models in memory

**TODO for students**: Set up performance profiling and APM.

## Replication Problems

### Issue: Model Replication Failing

**Symptoms**: `ReplicationStatus: FAILED`

**Debugging**:
```bash
# 1. Check replication logs
python -m src.replication.model_replicator --model-id model-v1.0.0 --status

# 2. Check source model exists
aws s3 ls s3://ml-models-us-east-1/models/model-v1.0.0.pth

# 3. Check target bucket permissions
aws s3api get-bucket-acl --bucket ml-models-eu-west-1

# 4. Check network connectivity
aws s3 cp s3://ml-models-us-east-1/test.txt s3://ml-models-eu-west-1/test.txt

# 5. Check replication service logs
kubectl logs deployment/replication-service -n ml-platform
```

**Solutions**:

**Error: `Access Denied`**
```bash
# Update IAM policy for cross-region replication
aws iam put-role-policy --role-name ModelReplicationRole \
  --policy-name CrossRegionReplication \
  --policy-document file://replication-policy.json
```

**Error: `Checksum mismatch`**
```bash
# Re-calculate and compare checksums
python -m src.replication.model_replicator --verify-checksum \
  --model-id model-v1.0.0

# If corrupted, delete and re-replicate
aws s3 rm s3://ml-models-eu-west-1/models/model-v1.0.0.pth
python -m src.replication.model_replicator --model-id model-v1.0.0 --replicate
```

**TODO for students**: Implement automatic retry with exponential backoff.

### Issue: High Replication Lag

**Symptoms**: Replication lag > 15 minutes

**Debugging**:
```bash
# 1. Check replication queue depth
python -m src.replication.model_replicator --queue-depth

# 2. Check network bandwidth
iperf3 -c remote-server

# 3. Check replication service resources
kubectl top pods -l app=replication-service -n ml-platform

# 4. Check for large models in queue
python -m src.replication.model_replicator --list-pending
```

**Solutions**:
- **Large backlog**: Scale replication service
- **Network throttling**: Request bandwidth increase
- **Resource constrained**: Increase CPU/memory for replication pods

**TODO for students**: Set up replication lag monitoring and alerting.

## Performance Issues

### Issue: High CPU Usage

**Symptoms**: CPU consistently > 90%

**Debugging**:
```bash
# 1. Identify which pods
kubectl top pods -n ml-platform --sort-by=cpu

# 2. Profile CPU usage
kubectl exec -it <POD_NAME> -n ml-platform -- top -b -n 1

# 3. Check for CPU throttling
kubectl describe pod <POD_NAME> -n ml-platform | grep -A 10 "Limits:"

# 4. Check for expensive operations
kubectl logs <POD_NAME> -n ml-platform | grep "duration"
```

**Solutions**:
```bash
# Scale horizontally
kubectl scale deployment/model-server --replicas=10 -n ml-platform

# Or increase CPU limits
kubectl set resources deployment/model-server -n ml-platform \
  --limits=cpu=4000m --requests=cpu=2000m

# Or use larger instance type
# Update node pool configuration
```

**TODO for students**: Set up CPU profiling and flame graphs.

### Issue: Memory Leaks

**Symptoms**: Memory usage constantly increasing

**Debugging**:
```bash
# 1. Monitor memory over time
kubectl top pods -n ml-platform --watch

# 2. Check for OOMKilled pods
kubectl get pods -n ml-platform | grep OOMKilled

# 3. Profile memory usage
kubectl exec -it <POD_NAME> -n ml-platform -- \
  python -m memory_profiler script.py

# 4. Check for large objects in memory
# Use application-specific memory profiling tools
```

**Solutions**:
- **Model caching issue**: Implement LRU cache with size limits
- **Request accumulation**: Add request timeouts and limits
- **Batch processing**: Clear batch data after processing

**TODO for students**: Implement memory monitoring and automatic pod restarts.

## Deployment Failures

### Issue: Rolling Deployment Stuck

**Symptoms**: `kubectl rollout status` shows deployment not progressing

**Debugging**:
```bash
# 1. Check rollout status
kubectl rollout status deployment/model-server -n ml-platform

# 2. Check deployment events
kubectl describe deployment model-server -n ml-platform

# 3. Check pod status
kubectl get pods -n ml-platform -l app=model-server

# 4. Check new pod logs
kubectl logs <NEW_POD_NAME> -n ml-platform

# 5. Check readiness probe
kubectl describe pod <NEW_POD_NAME> -n ml-platform | grep -A 10 "Readiness"
```

**Solutions**:

**Pods failing readiness probe**:
```bash
# Check what readiness probe is testing
kubectl get deployment model-server -n ml-platform -o yaml | grep -A 10 "readinessProbe"

# Test probe manually
kubectl exec -it <POD_NAME> -n ml-platform -- curl localhost:8080/health

# Fix probe or fix application
```

**Image pull errors**:
```bash
# Check image exists
docker pull <IMAGE_URL>

# Check image pull secrets
kubectl get secrets -n ml-platform

# Recreate secret if needed
kubectl create secret docker-registry regcred \
  --docker-server=<REGISTRY> \
  --docker-username=<USER> \
  --docker-password=<PASSWORD> \
  -n ml-platform
```

**Rollback if stuck**:
```bash
kubectl rollout undo deployment/model-server -n ml-platform
```

**TODO for students**: Implement progressive rollout with automatic rollback.

## Monitoring & Alerting

### Issue: Alerts Not Firing

**Symptoms**: Known issue but no alerts received

**Debugging**:
```bash
# 1. Check AlertManager status
kubectl get pods -n monitoring -l app=alertmanager

# 2. Check Prometheus rules
kubectl get prometheusrules -n monitoring

# 3. Query Prometheus directly
curl http://prometheus-url/api/v1/query?query=<YOUR_QUERY>

# 4. Check AlertManager configuration
kubectl get secret alertmanager-config -n monitoring -o yaml

# 5. Test alert
curl -X POST http://alertmanager-url/api/v1/alerts \
  -d '[{"labels":{"alertname":"TestAlert"}}]'
```

**Solutions**:
- **Rule misconfigured**: Fix Prometheus rule syntax
- **AlertManager not running**: Restart AlertManager pods
- **Notification channel broken**: Test Slack/PagerDuty integration

**TODO for students**: Set up alert testing in CI/CD pipeline.

### Issue: Metrics Missing

**Symptoms**: Grafana dashboard shows "No data"

**Debugging**:
```bash
# 1. Check Prometheus targets
curl http://prometheus-url/api/v1/targets

# 2. Check ServiceMonitor
kubectl get servicemonitor -n ml-platform

# 3. Check application metrics endpoint
kubectl port-forward -n ml-platform svc/model-server 8080:8080
curl localhost:8080/metrics

# 4. Check Prometheus logs
kubectl logs -n monitoring deployment/prometheus
```

**Solutions**:
- **ServiceMonitor missing**: Create ServiceMonitor resource
- **Metrics endpoint not exposed**: Update application to expose /metrics
- **Prometheus not scraping**: Check ServiceMonitor selector matches service labels

**TODO for students**: Document all custom metrics and their meanings.

## Database Issues

### Issue: Connection Pool Exhausted

**Symptoms**: `Too many connections` errors

**Debugging**:
```bash
# Check current connections
# PostgreSQL:
kubectl exec -it postgres-0 -n ml-platform -- \
  psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool settings
kubectl get configmap app-config -n ml-platform -o yaml | grep pool

# Check which pods are holding connections
kubectl exec -it postgres-0 -n ml-platform -- \
  psql -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
```

**Solutions**:
```bash
# Increase connection pool size
kubectl set env deployment/model-server -n ml-platform \
  DB_POOL_SIZE=50

# Or increase max connections on database
# Update RDS parameter group or CloudSQL instance
```

**TODO for students**: Set up connection pool monitoring.

## Cost Anomalies

### Issue: Unexpected Cost Spike

**Symptoms**: Daily cost increased by 50%+

**Debugging**:
```bash
# 1. Check cost breakdown
python -m src.cost.cost_analyzer --days 7 --by-region

# 2. Check resource changes
kubectl get pods --all-namespaces | wc -l
# Compare with historical data

# 3. Check for new resources
aws ec2 describe-instances --filters "Name=tag:Environment,Values=production"

# 4. Check data transfer
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name NetworkOut \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-15T00:00:00Z \
  --period 86400 \
  --statistics Sum

# 5. Check for abandoned resources
# Unused load balancers, EBS volumes, etc.
```

**Solutions**:
- **Auto-scaling spike**: Review scaling policies
- **Data transfer**: Optimize cross-region traffic
- **Forgotten resources**: Clean up unused resources
- **Instance type change**: Verify intended changes

**TODO for students**: Set up cost anomaly detection and budget alerts.

## Security & Access Issues

### Issue: Authentication Failures

**Symptoms**: `401 Unauthorized` errors

**Debugging**:
```bash
# 1. Verify API key
curl -H "Authorization: Bearer <TOKEN>" https://ml-platform.example.com/health

# 2. Check token expiry
jwt decode <TOKEN>

# 3. Check API gateway logs
kubectl logs -n ml-platform deployment/api-gateway | grep "auth"

# 4. Verify RBAC permissions
kubectl auth can-i get pods -n ml-platform --as=system:serviceaccount:ml-platform:default
```

**Solutions**:
- **Expired token**: Request new token
- **Invalid permissions**: Update RBAC roles
- **Revoked credentials**: Rotate and distribute new credentials

**TODO for students**: Implement OAuth 2.0 or JWT-based authentication.

## Quick Fixes Checklist

When in doubt, try these in order:

1. **Restart the affected component**
   ```bash
   kubectl rollout restart deployment/<DEPLOYMENT> -n ml-platform
   ```

2. **Check recent changes**
   ```bash
   git log --since="1 hour ago"
   kubectl rollout history deployment/<DEPLOYMENT> -n ml-platform
   ```

3. **Scale up resources**
   ```bash
   kubectl scale deployment/<DEPLOYMENT> --replicas=10 -n ml-platform
   ```

4. **Check logs**
   ```bash
   kubectl logs -f deployment/<DEPLOYMENT> -n ml-platform --tail=100
   ```

5. **Rollback last change**
   ```bash
   kubectl rollout undo deployment/<DEPLOYMENT> -n ml-platform
   ```

6. **Failover to healthy region**
   ```bash
   python -m src.failover.failover_controller \
     --from-region <UNHEALTHY> --to-region <HEALTHY>
   ```

## Getting Help

If you're still stuck after trying these troubleshooting steps:

1. **Check documentation**: Review DESIGN.md, API.md, RUNBOOK.md
2. **Search past incidents**: Check incident logs and postmortems
3. **Ask the team**: Post in #ml-platform Slack channel
4. **Escalate**: Page on-call engineer via PagerDuty
5. **Contact vendor support**: AWS/GCP/Azure support for infrastructure issues

**Emergency Escalation**: For P0 incidents, immediately page Platform Lead at platform-lead@example.com

**TODO for students**: Keep this troubleshooting guide updated with new issues and solutions discovered in production.
