# Multi-Region ML Platform - Operations Runbook

> **TODO for students**: Customize this runbook with your team's specific procedures, escalation paths, and on-call schedules.

## Quick Reference

### Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Platform Lead | platform-lead@example.com | 24/7 |
| DevOps On-Call | +1-555-0100 | 24/7 |
| Cloud Provider Support | support.aws.com | 24/7 |
| PagerDuty | https://company.pagerduty.com | 24/7 |

**TODO for students**: Update with actual contact information.

### Critical Links

- **Monitoring**: https://grafana.example.com
- **Alerting**: https://company.pagerduty.com
- **Logs**: https://logs.example.com
- **Status Page**: https://status.ml-platform.example.com
- **Documentation**: https://docs.ml-platform.example.com

## Daily Operations

### Morning Health Check

Run this checklist every morning:

```bash
# 1. Check overall system health
curl https://ml-platform.example.com/health

# 2. Check each region
for region in us-east-1 eu-west-1 ap-southeast-1; do
  echo "Checking $region..."
  curl https://$region.ml-platform.example.com/health
done

# 3. Check key metrics
python -m src.monitoring.health_checker --check-all

# 4. Review active alerts
curl https://alertmanager.example.com/api/v1/alerts | jq '.data[] | select(.status.state=="active")'

# 5. Check replication lag
python -m src.replication.model_replicator --check-lag
```

**Expected Results**:
- All regions return `{"status": "healthy"}`
- No critical alerts active
- Replication lag < 5 minutes

**TODO for students**: Automate this with a daily health check script and report.

### Weekly Tasks

**Every Monday**:
- [ ] Review last week's incidents
- [ ] Check cost reports and trends
- [ ] Verify backup integrity
- [ ] Review capacity utilization

**Every Wednesday**:
- [ ] Review slow queries and optimize
- [ ] Check for security updates
- [ ] Test alerting (send test alert)

**Every Friday**:
- [ ] Review upcoming deployments
- [ ] Check certificate expiry dates
- [ ] Update on-call schedule

**Monthly Tasks**:
- [ ] Conduct failover drill
- [ ] Review and rotate secrets
- [ ] Update documentation
- [ ] Security audit

**TODO for students**: Create Jira/GitHub issues for recurring tasks.

## Common Operational Tasks

### 1. Deploy New Model Version

```bash
# Step 1: Upload model to primary region
aws s3 cp models/model-v2.0.0.pth s3://ml-models-us-east-1/models/

# Step 2: Trigger replication
python -m src.replication.model_replicator \
  --model-id model-v2.0.0 \
  --source-region us-east-1 \
  --target-regions eu-west-1,ap-southeast-1

# Step 3: Wait for replication to complete
python -m src.replication.model_replicator \
  --model-id model-v2.0.0 \
  --wait

# Step 4: Deploy using rolling strategy
python -m src.deployment.multi_region_orchestrator \
  --model-id model-v2.0.0 \
  --strategy rolling

# Step 5: Monitor deployment
watch -n 5 'python -m src.deployment.multi_region_orchestrator --status'

# Step 6: Verify deployment
./scripts/test.sh
```

**Rollback if needed**:
```bash
python -m src.deployment.multi_region_orchestrator \
  --rollback \
  --deployment-id <DEPLOYMENT_ID>
```

**TODO for students**: Document your deployment validation criteria.

### 2. Scale Resources

**Manual Scaling**:
```bash
# Scale model servers in a region
kubectl --context=us-east-1 scale deployment/model-server \
  --replicas=10 -n ml-platform

# Scale all regions
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region scale deployment/model-server \
    --replicas=10 -n ml-platform
done
```

**Auto-scaling Configuration**:
```bash
# Update HPA
kubectl --context=us-east-1 apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
  namespace: ml-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF
```

**TODO for students**: Define scaling policies based on your traffic patterns.

### 3. Investigate High Latency

```bash
# Step 1: Identify affected region
python -m src.monitoring.metrics_aggregator \
  --metric request_latency_p95 \
  --time-range 1h

# Step 2: Check pod resource usage
kubectl --context=<REGION> top pods -n ml-platform

# Step 3: Check for CPU/memory throttling
kubectl --context=<REGION> describe pod <POD_NAME> -n ml-platform | grep -A 10 "Conditions:"

# Step 4: Check application logs
kubectl --context=<REGION> logs -f deployment/model-server \
  -n ml-platform | grep -i "slow\|timeout\|error"

# Step 5: Check database performance
# (Cloud provider specific commands)

# Mitigation: Scale up if resource constrained
kubectl --context=<REGION> scale deployment/model-server \
  --replicas=15 -n ml-platform
```

**TODO for students**: Create latency SLO and automated alerts.

### 4. Handle Failed Region

**Scenario**: A region becomes unhealthy and needs failover.

```bash
# Step 1: Verify region is unhealthy
python -m src.deployment.health_checker \
  --region <FAILED_REGION> \
  --verbose

# Step 2: Check target region capacity
python -m src.deployment.health_checker \
  --region <TARGET_REGION>

# Step 3: Initiate failover
python -m src.failover.failover_controller \
  --from-region <FAILED_REGION> \
  --to-region <TARGET_REGION> \
  --reason regional_failure

# Step 4: Monitor traffic shift
watch -n 5 'curl -s https://ml-platform.example.com/health | jq .'

# Step 5: Verify no requests to failed region
# Check metrics in Grafana

# Step 6: Create incident ticket
# Document issue and actions taken

# Step 7: Begin recovery of failed region
python -m src.failover.recovery \
  --region <FAILED_REGION>
```

**Post-Incident**:
- Document root cause
- Update runbook if needed
- Schedule post-mortem meeting

**TODO for students**: Define RTO/RPO targets and test failover regularly.

### 5. Rotate Secrets

```bash
# Step 1: Generate new secrets
./scripts/generate-secrets.sh

# Step 2: Update secrets in each region
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region create secret generic ml-platform-secrets \
    --from-file=secrets.yaml \
    --dry-run=client -o yaml | kubectl --context=$region apply -f -
done

# Step 3: Rolling restart to pick up new secrets
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region rollout restart deployment/model-server -n ml-platform
done

# Step 4: Verify services are healthy
./scripts/test.sh

# Step 5: Delete old secrets from vault
```

**Schedule**: Rotate secrets every 90 days.

**TODO for students**: Automate secret rotation with a cron job or CI/CD pipeline.

### 6. Add New Region

```bash
# Step 1: Deploy infrastructure
cd terraform/
terraform workspace new <NEW_REGION>
terraform apply -var="region=<NEW_REGION>"

# Step 2: Configure kubectl
aws eks update-kubeconfig \
  --region <NEW_REGION> \
  --name ml-cluster-<NEW_REGION> \
  --alias <NEW_REGION>

# Step 3: Deploy application
python -m src.deployment.multi_region_orchestrator \
  --deploy-region <NEW_REGION> \
  --version <CURRENT_VERSION>

# Step 4: Replicate models
python -m src.replication.model_replicator \
  --replicate-all \
  --target-region <NEW_REGION>

# Step 5: Update global load balancer
python -m src.failover.dns_updater \
  --add-region <NEW_REGION>

# Step 6: Monitor for 24 hours before adding to active pool
python -m src.deployment.health_checker \
  --region <NEW_REGION> \
  --duration 24h

# Step 7: Gradually increase traffic
python -m src.failover.dns_updater \
  --update-weight <NEW_REGION> 10  # Start with 10%
# Gradually increase to 33% over several days
```

**TODO for students**: Create automation for region provisioning.

## Incident Response

### Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P0 | Critical - Service down | Immediate | All regions unavailable |
| P1 | High - Major degradation | 15 minutes | One region down |
| P2 | Medium - Partial impact | 1 hour | High latency in one region |
| P3 | Low - Minor issues | 4 hours | Non-critical alerts |

### Incident Response Workflow

```
1. Alert Triggered
   ↓
2. On-call Engineer Acknowledges (< 5 min)
   ↓
3. Initial Assessment (< 10 min)
   ↓
4. Escalate if needed
   ↓
5. Mitigation Actions
   ↓
6. Verify Resolution
   ↓
7. Update Status Page
   ↓
8. Post-Incident Review
```

### P0: Complete Service Outage

**Immediate Actions**:
1. Acknowledge alert in PagerDuty
2. Join incident bridge: `zoom.us/j/incident`
3. Update status page: "Investigating"
4. Page additional engineers if needed

**Investigation**:
```bash
# Check global health
curl https://ml-platform.example.com/health

# Check all regions
for region in us-east-1 eu-west-1 ap-southeast-1; do
  curl -v https://$region.ml-platform.example.com/health
done

# Check load balancer
aws route53 get-health-check-status --health-check-id <ID>

# Check Kubernetes clusters
for region in us-east-1 eu-west-1 ap-southeast-1; do
  kubectl --context=$region get nodes
  kubectl --context=$region get pods -n ml-platform
done
```

**Common Causes & Fixes**:

**Cause 1: DNS/Load Balancer Issue**
```bash
# Check Route53 health checks
aws route53 list-health-checks

# Update DNS if needed
python -m src.failover.dns_updater --fix-routing
```

**Cause 2: All Regions Down**
```bash
# Check for cloud provider outages
# AWS: https://status.aws.amazon.com
# GCP: https://status.cloud.google.com

# If provider issue, wait for resolution
# If application issue, rollback last deployment
kubectl --context=us-east-1 rollout undo deployment/model-server -n ml-platform
```

**Communication**:
- Update status page every 15 minutes
- Post in #incidents Slack channel
- Email leadership if > 30 minutes downtime

**TODO for students**: Create incident response checklist specific to your setup.

### P1: Single Region Failure

**Actions**:
```bash
# 1. Trigger failover
python -m src.failover.failover_controller \
  --from-region <FAILED_REGION> \
  --to-region <HEALTHY_REGION> \
  --reason regional_failure

# 2. Verify traffic shifted
watch -n 5 'python -m src.monitoring.metrics_aggregator --metric request_count_by_region'

# 3. Investigate failed region
kubectl --context=<FAILED_REGION> get events -n ml-platform --sort-by='.lastTimestamp'

# 4. Begin recovery
python -m src.failover.recovery --region <FAILED_REGION>
```

**TODO for students**: Define failover SLO (target: < 2 minutes).

## Monitoring & Alerting

### Key Metrics to Watch

1. **Request Latency** (P50, P95, P99)
   - Target: P95 < 100ms
   - Alert: P95 > 200ms for 5 minutes

2. **Error Rate**
   - Target: < 0.1%
   - Alert: > 1% for 5 minutes

3. **Availability**
   - Target: 99.99%
   - Alert: < 99.9% over 5 minutes

4. **Replication Lag**
   - Target: < 5 minutes
   - Alert: > 15 minutes

5. **Resource Utilization**
   - Target: CPU < 70%, Memory < 80%
   - Alert: CPU > 90% or Memory > 95%

**Grafana Dashboards**:
- Multi-Region Overview
- Per-Region Details
- Model Performance
- Cost Tracking

**TODO for students**: Create custom dashboards for your specific metrics.

### Alert Configuration

**Prometheus Alert Rules**:
```yaml
groups:
  - name: multi_region_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"

      - alert: HighErrorRate
        expr: rate(requests_failed_total[5m]) / rate(requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

**TODO for students**: Customize alert rules based on your SLOs.

## Maintenance Windows

### Planned Maintenance Procedure

1. **Schedule Maintenance**
   - Announce 72 hours in advance
   - Update status page
   - Notify customers via email

2. **Pre-Maintenance Checks**
   ```bash
   # Verify backup
   ./scripts/backup.sh

   # Verify rollback plan
   terraform plan -out=rollback-plan
   ```

3. **During Maintenance**
   - Follow deployment runbook
   - Monitor metrics closely
   - Keep status page updated

4. **Post-Maintenance Validation**
   ```bash
   # Run full test suite
   pytest tests/ -v

   # Verify all regions healthy
   ./scripts/test.sh
   ```

**TODO for students**: Define maintenance windows (e.g., Sundays 2-4 AM UTC).

## Cost Management

### Daily Cost Review

```bash
# Get yesterday's costs
python -m src.cost.cost_analyzer --days 1

# Get cost breakdown by region
python -m src.cost.cost_analyzer --by-region

# Get optimization recommendations
python -m src.cost.optimizer --recommendations
```

### Cost Optimization Actions

1. **Right-size Resources**
   ```bash
   # Analyze resource utilization
   python -m src.cost.optimizer --analyze-utilization

   # Apply recommendations
   python -m src.cost.optimizer --apply-recommendations --dry-run
   ```

2. **Use Spot Instances**
   ```bash
   # Configure spot instance pool
   kubectl --context=us-east-1 apply -f kubernetes/spot-instances.yaml
   ```

3. **Clean Up Unused Resources**
   ```bash
   # Find unused EBS volumes
   aws ec2 describe-volumes --filters Name=status,Values=available

   # Find old snapshots
   aws ec2 describe-snapshots --owner-ids self | jq '.Snapshots[] | select(.StartTime < "2024-01-01")'
   ```

**Monthly Cost Review Meeting**: First Monday of each month.

**TODO for students**: Set up cost alerts and budgets in your cloud provider console.

## Backup & Recovery

### Backup Schedule

- **Models**: Daily at 2 AM UTC
- **Databases**: Continuous backup with PITR
- **Configuration**: On every change (Git)

### Verify Backups

```bash
# List recent backups
aws s3 ls s3://ml-platform-backups/ --recursive | tail -10

# Test restore (non-production)
./scripts/test-restore.sh --environment staging
```

### Disaster Recovery Drill

**Quarterly DR Test**:
1. Simulate complete region failure
2. Execute failover procedures
3. Verify service continues in other regions
4. Document issues found
5. Update runbooks

**TODO for students**: Schedule and document DR test results.

## Handoff Procedures

### On-Call Handoff Checklist

When going on-call:
- [ ] Review recent incidents
- [ ] Check active alerts
- [ ] Review upcoming changes
- [ ] Test PagerDuty notifications
- [ ] Verify VPN access
- [ ] Check escalation contacts

When handing off:
- [ ] Brief next on-call on active issues
- [ ] Document any ongoing investigations
- [ ] Share any recent changes
- [ ] Update runbook with new learnings

**TODO for students**: Create handoff template and meeting schedule.

## Additional Resources

- **Architecture Docs**: docs/DESIGN.md
- **API Docs**: docs/API.md
- **Deployment Guide**: docs/DEPLOYMENT.md
- **Troubleshooting**: docs/TROUBLESHOOTING.md
- **Team Wiki**: https://wiki.example.com/ml-platform
- **Postmortems**: https://wiki.example.com/postmortems

**TODO for students**: Keep this runbook updated with new procedures and lessons learned.
