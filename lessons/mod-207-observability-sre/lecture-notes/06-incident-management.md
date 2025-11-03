# Lecture 06: Incident Management for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design incident management processes for ML systems covering detection (alerting), response (on-call), resolution (mitigation), and analysis (postmortem)
- Implement incident response procedures with clear roles (incident commander, communications lead, technical lead), escalation paths, and runbooks for common ML issues
- Configure on-call rotations with appropriate coverage (24/7, follow-the-sun), alert routing, and escalation policies ensuring timely response to production incidents
- Conduct blameless postmortems analyzing root causes, contributing factors, and corrective actions focusing on system improvements rather than individual blame
- Build incident response playbooks for common ML issues (model degradation, data drift, prediction failures, latency spikes) with step-by-step resolution procedures
- Design incident severity classification (P0-P4) with clear criteria, response times, and notification requirements appropriate for ML system impact
- Implement incident tracking and metrics measuring MTTD (mean time to detect), MTTR (mean time to resolution), and incident frequency for continuous improvement
- Architect incident prevention systems using chaos engineering, pre-incident reviews, deployment validation, and proactive monitoring to reduce incident occurrence

## Overview

## Overview

Incident management for ML systems requires understanding both traditional infrastructure incidents and ML-specific issues like model degradation, data drift, and prediction failures.

## Incident Lifecycle

```
Detection → Response → Resolution → Analysis
    ↑                                   │
    └───────────────────────────────────┘
              (Continuous Improvement)
```

### 1. Detection (Minutes)
- Monitoring alerts fire
- User reports received
- Anomaly detection triggers

### 2. Response (Minutes to Hours)
- Incident declared
- On-call engineer paged
- Initial assessment
- Team assembled

### 3. Resolution (Hours to Days)
- Root cause identified
- Fix implemented
- Service restored
- Monitoring confirms recovery

### 4. Analysis (Days to Week)
- Postmortem written
- Action items created
- Process improvements
- Knowledge sharing

---

## ML-Specific Incidents

### Common ML Incident Types

**1. Model Performance Degradation**
- **Symptoms**: Accuracy drop, increased errors
- **Causes**: Data drift, concept drift, stale model
- **Detection**: Model quality monitoring
- **Response**: Rollback model or retrain

**2. Prediction Service Outage**
- **Symptoms**: 5xx errors, timeouts
- **Causes**: Infrastructure failure, OOM, bad deployment
- **Detection**: Service availability monitoring
- **Response**: Rollback, scale up, or restart

**3. Feature Pipeline Failure**
- **Symptoms**: Missing/incorrect features
- **Causes**: Data source issues, pipeline bugs
- **Detection**: Feature freshness/quality monitoring
- **Response**: Fix pipeline, use cached features

**4. Training Pipeline Failure**
- **Symptoms**: Models not updating
- **Causes**: Data quality issues, infrastructure
- **Detection**: Pipeline monitoring
- **Response**: Fix data issues, restart pipeline

**5. Data Quality Issues**
- **Symptoms**: Bad predictions, model errors
- **Causes**: Upstream data corruption
- **Detection**: Data validation
- **Response**: Stop using bad data, alert data owners

---

## Incident Response Procedures

### Incident Severity Levels

```python
# incident/severity.py
from enum import Enum
from dataclasses import dataclass

class Severity(Enum):
    SEV1 = "critical"      # Service down, major impact
    SEV2 = "high"          # Degraded service, significant impact
    SEV3 = "medium"        # Minor impact, workaround available
    SEV4 = "low"           # No user impact, maintenance item

@dataclass
class IncidentMetadata:
    severity: Severity
    response_time_sla: int  # minutes
    escalation_time: int    # minutes
    notification_channels: list

SEVERITY_CONFIG = {
    Severity.SEV1: IncidentMetadata(
        severity=Severity.SEV1,
        response_time_sla=5,
        escalation_time=15,
        notification_channels=['pagerduty', 'slack-critical', 'email-executives']
    ),
    Severity.SEV2: IncidentMetadata(
        severity=Severity.SEV2,
        response_time_sla=15,
        escalation_time=30,
        notification_channels=['pagerduty', 'slack-incidents']
    ),
    Severity.SEV3: IncidentMetadata(
        severity=Severity.SEV3,
        response_time_sla=60,
        escalation_time=120,
        notification_channels=['slack-incidents', 'email-team']
    ),
    Severity.SEV4: IncidentMetadata(
        severity=Severity.SEV4,
        response_time_sla=480,
        escalation_time=None,
        notification_channels=['jira']
    )
}
```

### Incident Declaration

```python
# incident/declaration.py
from datetime import datetime
import uuid

class IncidentManager:
    def __init__(self, slack_webhook, pagerduty_api):
        self.slack = slack_webhook
        self.pagerduty = pagerduty_api

    def declare_incident(self, title: str, description: str, severity: Severity):
        """Declare new incident"""
        incident_id = f"INC-{uuid.uuid4().hex[:8]}"

        incident = {
            'id': incident_id,
            'title': title,
            'description': description,
            'severity': severity.value,
            'status': 'investigating',
            'started_at': datetime.now().isoformat(),
            'responders': [],
            'timeline': []
        }

        # Create incident in tracking system
        self._create_incident_record(incident)

        # Page on-call engineer
        if severity in [Severity.SEV1, Severity.SEV2]:
            self._page_oncall(incident)

        # Notify in Slack
        self._notify_slack(incident)

        # Log to timeline
        self._add_timeline_event(incident_id, "Incident declared")

        return incident

    def _page_oncall(self, incident):
        """Page on-call engineer"""
        self.pagerduty.trigger_incident(
            title=incident['title'],
            severity=incident['severity'],
            description=incident['description'],
            incident_key=incident['id']
        )

    def _notify_slack(self, incident):
        """Post to Slack channel"""
        message = f"""
        🚨 **INCIDENT DECLARED** 🚨
        **ID**: {incident['id']}
        **Severity**: {incident['severity'].upper()}
        **Title**: {incident['title']}
        **Description**: {incident['description']}

        War room: #incident-{incident['id'].lower()}
        """
        self.slack.post_message(channel='#incidents', text=message)
```

---

## Incident Response Playbooks

### Playbook: Model Performance Degradation

```markdown
# Playbook: Model Performance Degradation

## Detection
- Alert: `MLAccuracySLOViolation` fires
- Dashboard shows accuracy drop
- User reports of bad predictions

## Initial Assessment (5 min)
1. Check model version in production
   ```bash
   kubectl get deployment ml-service -o json | jq '.spec.template.spec.containers[0].env[] | select(.name=="MODEL_VERSION")'
   ```

2. Check recent deployments
   ```bash
   kubectl rollout history deployment/ml-service
   ```

3. Review metrics dashboard
   - Model accuracy over time
   - Prediction distribution
   - Feature distribution (drift detection)

## Triage (10 min)

### Is it a recent deployment?
**YES** → Go to "Rollback Procedure"
**NO** → Go to "Data Drift Investigation"

### Rollback Procedure
1. Identify last known good version
   ```bash
   kubectl rollout history deployment/ml-service
   ```

2. Rollback to previous version
   ```bash
   kubectl rollout undo deployment/ml-service
   ```

3. Monitor metrics for recovery
4. Update incident status
5. Schedule postmortem

### Data Drift Investigation
1. Check data drift metrics
   ```python
   python scripts/check_data_drift.py --window=24h
   ```

2. Compare feature distributions
   - Training data vs. production data
   - Look for significant changes

3. Check upstream data sources
   - Are they healthy?
   - Recent schema changes?

4. If drift confirmed:
   - Trigger retraining pipeline
   - Use cached/fallback features if available
   - Update monitoring thresholds

## Resolution
- Service restored (rollback OR new deployment)
- Metrics return to normal
- User impact ended

## Follow-up
- Complete postmortem within 48 hours
- Identify root cause
- Create action items for prevention
```

### Playbook: Prediction Service Outage

```markdown
# Playbook: Prediction Service Outage

## Detection
- Alert: `MLAvailabilitySLOViolation`
- 5xx error rate spike
- Timeouts

## Initial Assessment (2 min)
1. Check service health
   ```bash
   kubectl get pods -l app=ml-service
   kubectl logs -l app=ml-service --tail=100
   ```

2. Check resource usage
   ```bash
   kubectl top pods -l app=ml-service
   ```

## Common Causes & Fixes

### Pods CrashLooping
**Symptoms**: Pods in CrashLoopBackOff state

**Investigation**:
```bash
kubectl logs ml-service-xxx --previous
kubectl describe pod ml-service-xxx
```

**Likely causes**:
- OOM (Out of Memory)
- Model loading failure
- Configuration error

**Fix**:
- If OOM: Increase memory limits
- If model loading: Check model registry access
- If config: Rollback deployment

### High Latency / Timeouts
**Symptoms**: Requests timing out, high P99 latency

**Investigation**:
```bash
# Check service metrics
curl http://prometheus:9090/api/v1/query?query=histogram_quantile(0.99,rate(ml_prediction_latency_seconds_bucket[5m]))
```

**Likely causes**:
- Insufficient replicas for load
- Slow feature retrieval
- Model inference slow

**Fix**:
- Scale up replicas: `kubectl scale deployment ml-service --replicas=10`
- Check feature store performance
- Profile model inference

### Dependency Failure
**Symptoms**: Errors calling external services

**Investigation**:
- Check feature store health
- Check model registry availability
- Check Redis/database connectivity

**Fix**:
- Enable circuit breakers
- Use cached features
- Graceful degradation to simpler model

## Escalation
If not resolved in 30 minutes:
1. Escalate to senior engineer
2. Involve ML platform team
3. Consider full service rollback
```

---

## On-Call Best Practices

### On-Call Rotation

```yaml
# pagerduty_schedule.yaml
schedule:
  name: ml-platform-oncall
  time_zone: UTC
  layers:
    - name: primary
      start: 2024-01-01T00:00:00Z
      rotation_virtual_start: 2024-01-01T00:00:00Z
      rotation_turn_length_seconds: 604800  # 1 week
      users:
        - user_1
        - user_2
        - user_3

    - name: secondary
      start: 2024-01-01T00:00:00Z
      rotation_virtual_start: 2024-01-01T00:00:00Z
      rotation_turn_length_seconds: 604800
      users:
        - senior_engineer_1
        - senior_engineer_2
```

### Handoff Procedure

```markdown
# On-Call Handoff Template

## Week of [Date]

### Current Status
- [ ] All services healthy (or list issues)
- [ ] Open incidents: [list or "none"]
- [ ] Ongoing investigations: [list or "none"]

### Recent Incidents
1. [INC-ID] Brief description
   - Status: Resolved
   - Root cause: [summary]
   - Action items: [link to postmortem]

### Known Issues
- Issue 1: Description, workaround, ticket link
- Issue 2: ...

### Upcoming Work
- Scheduled maintenance: [dates/details]
- Deployments planned: [what/when]
- Monitoring changes: [what]

### Notes for Next On-Call
- [Any special instructions]
- [Contact info for escalations]
- [Links to runbooks]
```

---

## Postmortem Process

### Postmortem Template

```markdown
# Incident Postmortem: [Incident Title]

**Incident ID**: INC-XXXXXXXX
**Date**: YYYY-MM-DD
**Duration**: X hours Y minutes
**Severity**: SEV-X
**Author**: [Name]
**Reviewed**: [Date]

## Executive Summary
[2-3 sentence summary of what happened and impact]

## Impact
- **Users Affected**: [number/percentage]
- **Services Impacted**: [list]
- **Duration**: [time service was degraded]
- **Revenue Impact**: [$amount if applicable]

## Timeline (all times in UTC)

| Time | Event |
|------|-------|
| 10:00 | Alert fired: MLAccuracySLOViolation |
| 10:05 | On-call engineer paged |
| 10:10 | Incident declared (SEV2) |
| 10:15 | Identified model v2.5 deployed 30 min ago |
| 10:20 | Began rollback to v2.4 |
| 10:25 | Rollback complete |
| 10:30 | Metrics returning to normal |
| 10:45 | Incident resolved |

## Root Cause
[Detailed explanation of what caused the incident]

The root cause was a bug in the feature preprocessing code introduced in model v2.5. A new feature transformation was applied that caused categorical values to be encoded incorrectly, leading to poor model predictions.

## Detection
[How was the incident detected?]

The incident was detected by our model quality monitoring, which tracks accuracy on a rolling window of labeled production data. The alert fired within 15 minutes of the problematic deployment.

## Resolution
[How was the incident resolved?]

We rolled back the deployment to the previous version (v2.4). Accuracy immediately returned to normal levels.

## What Went Well
- [Things that worked well during the incident]
- Model quality monitoring detected the issue quickly
- Rollback procedure was smooth and well-documented
- Clear communication in war room

## What Went Wrong
- [Things that didn't work well]
- Feature preprocessing bug was not caught in testing
- Canary deployment was too small to detect the issue
- No automated rollback on quality degradation

## Action Items

| Action | Owner | Ticket | Due Date |
|--------|-------|--------|----------|
| Add integration tests for feature preprocessing | @engineer | ML-123 | 2024-01-15 |
| Increase canary deployment to 20% traffic | @sre | ML-124 | 2024-01-10 |
| Implement auto-rollback on quality alerts | @ml-platform | ML-125 | 2024-01-31 |
| Update model validation checklist | @ml-eng | ML-126 | 2024-01-12 |

## Lessons Learned
1. **Testing gaps**: Need better integration tests
2. **Canary too small**: Should catch issues before full rollout
3. **Manual rollback**: Should be automated for quality issues

## Appendix
- [Links to dashboards]
- [Links to logs]
- [Links to related incidents]
```

### Blameless Postmortems

**Key Principles**:
1. **Focus on systems, not individuals**
2. **Assume good intentions**
3. **Learn from mistakes**
4. **Create actionable improvements**
5. **Share knowledge widely**

---

## Incident Metrics

### Key Metrics to Track

```python
# incident/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Incident count
incidents_total = Counter(
    'incidents_total',
    'Total number of incidents',
    ['severity', 'service']
)

# Time to detect (TTD)
time_to_detect_seconds = Histogram(
    'incident_time_to_detect_seconds',
    'Time from incident start to detection',
    ['severity']
)

# Time to resolve (TTR)
time_to_resolve_seconds = Histogram(
    'incident_time_to_resolve_seconds',
    'Time from detection to resolution',
    ['severity']
)

# MTBF (Mean Time Between Failures)
mtbf_seconds = Gauge(
    'incident_mtbf_seconds',
    'Mean time between failures',
    ['service']
)

# MTTR (Mean Time To Restore)
mttr_seconds = Gauge(
    'incident_mttr_seconds',
    'Mean time to restore service',
    ['service']
)
```

---

## Key Takeaways

1. **Preparation is key**: Playbooks, monitoring, escalation
2. **Communicate clearly**: Keep stakeholders informed
3. **Blameless culture**: Focus on systems, not people
4. **Learn continuously**: Every incident is a learning opportunity
5. **Automate recovery**: Reduce MTTR with automation

## Exercises

1. Create incident response playbooks for your ML services
2. Set up PagerDuty/on-call rotation
3. Conduct incident response drill (game day)
4. Write postmortem for recent incident
5. Build incident metrics dashboard

## Additional Resources

- "Incident Management for Operations" (O'Reilly)
- "The Site Reliability Workbook" (Chapter 14)
- PagerDuty Incident Response documentation
- Atlassian Incident Management Handbook
