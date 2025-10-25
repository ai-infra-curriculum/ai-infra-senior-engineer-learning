# Lab 03: Chaos Engineering Experiment

## Objective
Design and execute a chaos engineering experiment to test ML service resilience and improve system reliability.

## Duration
3-4 hours

## Prerequisites
- Kubernetes cluster
- ML service deployed
- Monitoring setup (Prometheus/Grafana)
- Chaos Mesh installed

## Part 1: Setup Chaos Mesh (30 min)

### Install Chaos Mesh

```bash
# TODO: Install Chaos Mesh
curl -sSL https://mirrors.chaos-mesh.org/v2.5.0/install.sh | bash

# Verify installation
kubectl get pods -n chaos-mesh
```

### Access Chaos Dashboard

```bash
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
# Access: http://localhost:2333
```

## Part 2: Design Chaos Experiment (45 min)

### TODO: Complete Experiment Template

```markdown
# Chaos Experiment: ML Service Pod Failure

## Hypothesis
"We believe that the ML prediction service will maintain 99% availability
when 30% of pods fail randomly, through automatic pod recreation and
load balancing."

## Scope
- **System**: ml-prediction-service
- **Duration**: 10 minutes
- **Blast Radius**: 30% of pods
- **Environment**: staging

## Prerequisites Checklist
- [ ] Monitoring dashboard active
- [ ] Alerting enabled
- [ ] Rollback plan documented
- [ ] Team notified
- [ ] Off-peak time (low traffic)

## Success Criteria
- [ ] Service maintains >99% availability
- [ ] P95 latency stays <300ms
- [ ] Alerts fire as expected
- [ ] Pods recreate automatically
- [ ] No manual intervention needed

## Experiment Steps
1. [TODO: Define steps]
2. ...

## Metrics to Monitor
- [TODO: List metrics]

## Rollback Plan
1. [TODO: Define rollback steps]
```

## Part 3: Pod Failure Experiment (60 min)

### TODO: Create PodChaos Experiment

```yaml
# experiments/pod-failure.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: ml-service-pod-failure
  namespace: chaos-testing
spec:
  # TODO: Configure:
  # - action: pod-failure
  # - mode: fixed-percent
  # - value: "30"
  # - selector: target ml-prediction-service
  # - duration: 10m
```

### TODO: Execute Experiment

```bash
# Apply chaos experiment
kubectl apply -f experiments/pod-failure.yaml

# Monitor experiment
watch kubectl get pods -n ml-services

# TODO: While running, monitor:
# - Pod status
# - Request success rate
# - Latency metrics
# - Auto-scaling behavior
```

### TODO: Collect Results

Create `results.md` documenting:
- Before metrics (baseline)
- During chaos metrics
- After chaos metrics (recovery)
- Observations
- Issues discovered

## Part 4: Network Latency Experiment (60 min)

### TODO: Design Network Chaos Experiment

```yaml
# experiments/network-latency.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: feature-store-latency
spec:
  # TODO: Configure:
  # - action: delay
  # - target: feature-store service
  # - delay: 500ms
  # - jitter: 100ms
  # - duration: 5m
```

### TODO: Hypothesize Impact

Write hypothesis:
"Adding 500ms latency to feature store will:
- Increase P95 prediction latency by [X]ms
- Trigger circuit breaker after [Y] seconds
- Fall back to cached features
- Maintain availability above [Z]%"

### TODO: Execute and Validate

```bash
# Apply experiment
kubectl apply -f experiments/network-latency.yaml

# TODO: Monitor:
# - Prediction latency
# - Cache hit rate
# - Circuit breaker status
# - Error rate
```

## Part 5: Model Failure Injection (60 min)

### TODO: Implement Chaos in Application Code

```python
# chaos/model_chaos.py
# TODO: Implement chaos injection

class ChaosModelWrapper:
    def __init__(self, model, chaos_config):
        # TODO: Initialize
        pass

    def predict(self, features):
        # TODO: Inject failures based on config:
        # - Random exceptions (5% of requests)
        # - Timeouts (2% of requests)
        # - Wrong predictions (1% of requests)

        # TODO: If chaos not triggered, call real model
        pass

    def _should_inject_chaos(self) -> bool:
        # TODO: Decide based on probability
        pass

    def _get_failure_type(self) -> str:
        # TODO: Random selection of failure type
        pass
```

### TODO: Deploy Chaotic Version

```yaml
# k8s/chaotic-deployment.yaml
# TODO: Deploy model service with chaos enabled
# - Set CHAOS_ENABLED=true
# - Set CHAOS_FAILURE_RATE=0.05
```

### TODO: Monitor Impact

Monitor for 15 minutes:
- Success rate
- Fallback activation
- User impact
- Recovery time

## Part 6: GameDay Simulation (Bonus)

### TODO: Plan GameDay

```markdown
# GameDay: ML Service Resilience Test

## Date: [Schedule]
## Participants:
- ML Engineers
- SRE team
- On-call engineer

## Scenarios:

### Scenario 1: Pod Failures (15 min)
- Kill 50% of pods
- Observe auto-healing
- Validate monitoring

### Scenario 2: Database Failure (15 min)
- Simulate database unavailable
- Test circuit breaker
- Verify graceful degradation

### Scenario 3: Model Degradation (15 min)
- Inject bad model
- Test rollback procedure
- Validate alerts

## Debrief Template:
- What worked well?
- What failed?
- Action items?
```

### TODO: Execute GameDay

Run all scenarios and document:
- Team response times
- Communication effectiveness
- Technical issues found
- Process improvements needed

## Part 7: Analysis and Improvements (30 min)

### TODO: Analyze Results

For each experiment, document:

1. **Hypothesis Validation**
   - Was hypothesis correct?
   - Actual vs expected behavior
   - Surprises

2. **Metrics Analysis**
   - Availability during chaos
   - Latency impact
   - Error rates
   - Recovery time

3. **Issues Discovered**
   - Bugs found
   - Missing monitoring
   - Inadequate error handling

4. **Action Items**
   - Code improvements
   - Monitoring enhancements
   - Process changes
   - Documentation updates

### TODO: Create Improvement Backlog

```markdown
# Chaos Engineering Improvements

## High Priority
- [ ] Add circuit breaker to feature store calls
- [ ] Implement prediction caching
- [ ] Improve pod disruption budget

## Medium Priority
- [ ] Add fallback model
- [ ] Enhance monitoring for edge cases
- [ ] Document runbooks

## Low Priority
- [ ] Automate chaos experiments
- [ ] Create chaos dashboard
```

## Deliverables

1. **Experiment Documentation**
   - Hypothesis
   - Design
   - Procedures
   - Success criteria

2. **Chaos Configurations**
   - PodChaos manifests
   - NetworkChaos manifests
   - Application chaos code

3. **Results Report**
   - Metrics before/during/after
   - Observations
   - Issues found
   - Lessons learned

4. **Improvement Plan**
   - Action items
   - Priorities
   - Owners
   - Timeline

5. **Runbooks**
   - How to run experiments
   - How to rollback
   - Emergency procedures

## Validation

- [ ] Chaos Mesh installed and working
- [ ] At least 2 experiments executed
- [ ] Results documented with metrics
- [ ] Issues identified and tracked
- [ ] Improvements prioritized
- [ ] Team learned from experiments

## Bonus

1. Automate chaos experiments (daily/weekly)
2. Create chaos experiment library
3. Build confidence scoring system
4. Implement progressive chaos (start small)
5. Create chaos engineering dashboard

## Resources

- Chaos Mesh documentation
- "Chaos Engineering" book
- Netflix Chaos Engineering blog
- Chaos Engineering community
