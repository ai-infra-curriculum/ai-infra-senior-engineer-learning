# Lecture 07: Chaos Engineering for ML Systems

## Learning Objectives

By the end of this lecture, you will be able to:

- Design chaos experiments for ML systems testing resilience to model failures, data quality issues, infrastructure outages, and latency spikes
- Implement fault injection techniques using tools like Chaos Monkey, Litmus Chaos, or custom scripts simulating realistic production failures with controlled blast radius
- Architect steady-state hypothesis definitions for ML services establishing expected behavior (availability, latency, correctness) that should persist during chaos experiments
- Configure automated chaos engineering pipelines with scheduled experiments, automated rollback, and continuous validation integrated into CI/CD workflows
- Design ML-specific chaos scenarios including model serving failures, feature store outages, batch job interruptions, and data pipeline degradation
- Implement resilience patterns validated through chaos including circuit breakers, fallback models, graceful degradation, and automatic retry mechanisms
- Build game day exercises running large-scale chaos experiments in production with full incident response simulation and team coordination
- Analyze chaos experiment results identifying weaknesses in system design, monitoring gaps, and operational procedures enabling proactive reliability improvements

## Overview

## Overview

Chaos engineering is the discipline of experimenting on a system to build confidence in its ability to withstand turbulent conditions in production. For ML systems, this includes testing resilience to model failures, data issues, and infrastructure problems.

## Chaos Engineering Principles

### Core Concepts

**Definition**: "Chaos Engineering is the discipline of experimenting on a system in order to build confidence in the system's capability to withstand turbulent conditions in production."

**Key Principles**:
1. **Build a Hypothesis**: Define steady state behavior
2. **Vary Real-World Events**: Inject realistic failures
3. **Run in Production**: Test on real systems (carefully)
4. **Automate Experiments**: Continuous chaos
5. **Minimize Blast Radius**: Limit impact of experiments

### The Chaos Engineering Process

```
1. Define Steady State
   ↓
2. Form Hypothesis
   ↓
3. Design Experiment
   ↓
4. Run Experiment
   ↓
5. Observe & Measure
   ↓
6. Learn & Improve
   ↓
(Repeat)
```

---

## ML-Specific Chaos Experiments

### 1. Model Failure Experiments

**Hypothesis**: "If the primary model fails, the system will gracefully degrade to a fallback model without user impact."

```python
# chaos/model_failure.py
import random
import time
from typing import Optional

class ChaosModelServer:
    def __init__(self, primary_model, fallback_model, chaos_config):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.chaos_config = chaos_config

    def predict(self, features):
        """Predict with chaos injection"""
        # Inject model failures
        if self._should_inject_failure():
            failure_type = self._select_failure_type()

            if failure_type == 'exception':
                # Simulate model crash
                raise Exception("Chaos: Model inference failed")

            elif failure_type == 'timeout':
                # Simulate timeout
                time.sleep(self.chaos_config['timeout_duration'])
                raise TimeoutError("Chaos: Model timeout")

            elif failure_type == 'wrong_output':
                # Simulate corrupted output
                return {'prediction': 'CHAOS_CORRUPTED'}

        # Normal operation
        try:
            return self.primary_model.predict(features)
        except Exception:
            # Graceful degradation
            return self.fallback_model.predict(features)

    def _should_inject_failure(self) -> bool:
        """Decide whether to inject failure"""
        return random.random() < self.chaos_config['failure_rate']

    def _select_failure_type(self) -> str:
        """Select type of failure to inject"""
        return random.choice(['exception', 'timeout', 'wrong_output'])

# Chaos configuration
chaos_config = {
    'enabled': True,
    'failure_rate': 0.01,  # 1% of requests
    'timeout_duration': 5.0,  # seconds
    'blast_radius': 0.05  # Max 5% of traffic
}

# Usage
server = ChaosModelServer(primary_model, fallback_model, chaos_config)
```

**Metrics to Monitor**:
- Fallback model activation rate
- Overall prediction success rate
- Latency distribution
- Error rate by type

---

### 2. Feature Store Failure

**Hypothesis**: "If feature store fails, system will use cached features without significant degradation."

```python
# chaos/feature_store_failure.py
from feast import FeatureStore
import redis
from datetime import datetime, timedelta

class ChaoticFeatureStore:
    def __init__(self, feature_store: FeatureStore, redis_client: redis.Redis):
        self.feature_store = feature_store
        self.cache = redis_client
        self.chaos_enabled = True

    def get_online_features(self, features: list, entity_rows: list):
        """Get features with chaos injection"""
        if self.chaos_enabled and self._should_inject_failure():
            failure_type = random.choice(['latency', 'exception', 'stale_data'])

            if failure_type == 'latency':
                # Simulate slow feature store
                time.sleep(2.0)

            elif failure_type == 'exception':
                # Simulate feature store unavailable
                raise Exception("Chaos: Feature store unavailable")

            elif failure_type == 'stale_data':
                # Return cached (possibly stale) features
                return self._get_cached_features(entity_rows)

        # Try primary source
        try:
            result = self.feature_store.get_online_features(features, entity_rows)
            # Update cache
            self._update_cache(entity_rows, result)
            return result
        except Exception:
            # Fall back to cache
            return self._get_cached_features(entity_rows)

    def _get_cached_features(self, entity_rows):
        """Retrieve features from cache"""
        cached_features = {}
        for row in entity_rows:
            key = f"features:{row['user_id']}"
            cached = self.cache.get(key)
            if cached:
                cached_features[row['user_id']] = json.loads(cached)
        return cached_features

    def _update_cache(self, entity_rows, features):
        """Update feature cache"""
        for row in entity_rows:
            key = f"features:{row['user_id']}"
            self.cache.setex(key, 3600, json.dumps(features))
```

**Experiment Steps**:
1. Enable chaos mode with 5% failure rate
2. Monitor prediction latency and success rate
3. Verify cache hit rate increases
4. Confirm no user-facing errors
5. Measure impact on prediction quality

---

### 3. Data Pipeline Failure

**Hypothesis**: "If data pipeline fails, system will detect the issue and alert within 5 minutes."

```python
# chaos/pipeline_failure.py
class ChaoticDataPipeline:
    def __init__(self, pipeline, monitor):
        self.pipeline = pipeline
        self.monitor = monitor

    def run(self):
        """Run pipeline with chaos injection"""
        if self._should_inject_failure():
            failure_type = random.choice([
                'missing_data',
                'corrupted_data',
                'schema_change',
                'delayed_data'
            ])

            if failure_type == 'missing_data':
                # Simulate missing input data
                raise FileNotFoundError("Chaos: Input data missing")

            elif failure_type == 'corrupted_data':
                # Inject corrupted records
                self._corrupt_data()

            elif failure_type == 'schema_change':
                # Simulate schema change
                self._change_schema()

            elif failure_type == 'delayed_data':
                # Simulate delayed data arrival
                time.sleep(300)  # 5 minute delay

        # Run normal pipeline
        self.pipeline.run()

    def _corrupt_data(self):
        """Inject corrupted data"""
        # Add null values, wrong types, outliers
        pass

    def _change_schema(self):
        """Simulate schema change"""
        # Rename columns, change types
        pass
```

---

### 4. Infrastructure Failure

**Hypothesis**: "If 30% of prediction pods fail, remaining pods will auto-scale and maintain SLO."

```python
# chaos/infrastructure_failure.py
from kubernetes import client, config
import random

class KubernetesChaos:
    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()

    def kill_random_pods(self, namespace: str, label_selector: str, percentage: float):
        """Kill random percentage of pods"""
        # List all pods matching selector
        pods = self.v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )

        # Calculate number to kill
        num_to_kill = int(len(pods.items) * percentage)

        # Select random pods
        pods_to_kill = random.sample(pods.items, num_to_kill)

        # Delete pods
        for pod in pods_to_kill:
            print(f"Chaos: Killing pod {pod.metadata.name}")
            self.v1.delete_namespaced_pod(
                name=pod.metadata.name,
                namespace=namespace
            )

# Usage
chaos = KubernetesChaos()
chaos.kill_random_pods(
    namespace="ml-services",
    label_selector="app=prediction-service",
    percentage=0.30  # Kill 30% of pods
)
```

---

## Chaos Engineering Tools

### Chaos Mesh

**Kubernetes-native chaos engineering platform**

```yaml
# chaos-mesh/model-failure.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: model-service-pod-failure
  namespace: chaos-testing
spec:
  action: pod-failure
  mode: fixed-percent
  value: "20"  # 20% of pods
  duration: "30s"
  selector:
    namespaces:
      - ml-services
    labelSelectors:
      app: "model-service"
  scheduler:
    cron: "@every 1h"

---
# Simulate network latency
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: feature-store-latency
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - ml-services
    labelSelectors:
      app: "feature-store"
  delay:
    latency: "500ms"
    correlation: "100"
    jitter: "100ms"
  duration: "5m"
```

### Litmus

**Cloud-native chaos engineering**

```yaml
# litmus/model-cpu-hog.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: model-service-chaos
  namespace: ml-services
spec:
  appinfo:
    appns: ml-services
    applabel: "app=model-service"
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-cpu-hog
      spec:
        components:
          env:
            - name: CPU_CORES
              value: "2"
            - name: TOTAL_CHAOS_DURATION
              value: "60"
            - name: PODS_AFFECTED_PERC
              value: "50"
```

### Gremlin

**Failure as a Service platform**

```python
# gremlin/experiment.py
from gremlin import GremlinAPI

gremlin = GremlinAPI(api_key="your-api-key")

# Create latency attack
attack = gremlin.create_attack({
    "target": {
        "type": "Random",
        "containers": {
            "labels": {"app": "model-service"},
            "count": 2
        }
    },
    "command": {
        "type": "latency",
        "args": [
            "-l", "5",  # 5 seconds latency
            "-h", "feature-store.example.com"
        ]
    }
})

# Monitor results
status = gremlin.get_attack_status(attack['id'])
```

---

## Designing Chaos Experiments

### Experiment Template

```markdown
# Chaos Experiment: [Name]

## Hypothesis
[What do you expect to happen?]

"We believe that [system] will [expected behavior] when [failure condition] occurs."

## Scope
- **Systems**: [Which services/components]
- **Duration**: [How long]
- **Blast Radius**: [% of traffic/instances]

## Prerequisites
- [ ] Monitoring dashboards configured
- [ ] Runbook prepared
- [ ] Rollback plan defined
- [ ] Stakeholders notified
- [ ] Off-peak time scheduled

## Experiment Steps
1. [Step 1]
2. [Step 2]
3. ...

## Success Criteria
- [ ] System maintains SLO during experiment
- [ ] Alerts fire as expected
- [ ] Graceful degradation observed
- [ ] Recovery within [X] minutes

## Metrics to Monitor
- Prediction success rate
- Latency (P50, P95, P99)
- Error rate
- Fallback activation rate

## Rollback Plan
1. [How to stop experiment]
2. [How to restore normal operation]

## Results
[To be filled after experiment]

## Lessons Learned
[To be filled after experiment]
```

---

## Chaos Automation

### Continuous Chaos

```python
# chaos/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

class ChaosScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def schedule_experiment(self, experiment, cron_expression):
        """Schedule recurring chaos experiment"""
        self.scheduler.add_job(
            func=self.run_experiment,
            trigger='cron',
            **self._parse_cron(cron_expression),
            args=[experiment]
        )

    def run_experiment(self, experiment):
        """Execute chaos experiment"""
        logger.info(f"Starting chaos experiment: {experiment.name}")

        try:
            # Check prerequisites
            if not self._check_prerequisites(experiment):
                logger.warning("Prerequisites not met, skipping")
                return

            # Run experiment
            result = experiment.execute()

            # Verify results
            if not result.meets_success_criteria():
                logger.error("Experiment failed success criteria")
                self._alert_failure(experiment, result)

            # Log results
            self._log_results(experiment, result)

        except Exception as e:
            logger.error(f"Experiment error: {str(e)}")
            experiment.rollback()

    def _check_prerequisites(self, experiment):
        """Verify prerequisites are met"""
        # Check system health
        # Check time window (off-peak)
        # Check blast radius
        return True

# Usage
scheduler = ChaosScheduler()

# Run pod failures every day at 2 AM
scheduler.schedule_experiment(
    PodFailureExperiment(percentage=0.20),
    cron_expression="0 2 * * *"
)

# Run latency injection every 4 hours
scheduler.schedule_experiment(
    LatencyExperiment(duration_minutes=5),
    cron_expression="0 */4 * * *"
)

scheduler.start()
```

---

## GameDay Exercises

### Planning a GameDay

**GameDay**: Scheduled chaos engineering exercise with full team participation

```markdown
# GameDay Plan: ML Service Resilience

## Date: [Date] [Time]
## Duration: 2 hours
## Participants:
- ML Engineers
- SRE Team
- Product Manager
- Support Team

## Objectives
1. Test incident response procedures
2. Validate monitoring and alerting
3. Practice cross-team coordination
4. Identify weaknesses

## Scenarios

### Scenario 1: Model Degradation (30 min)
- **T+0**: Deploy model with intentional bug
- **T+5**: Trigger data drift
- **T+15**: Feature store latency spike
- **Expectation**: Team detects and rolls back within 20 min

### Scenario 2: Infrastructure Failure (30 min)
- **T+0**: Kill 50% of prediction pods
- **T+10**: Network partition between services
- **T+20**: Redis cache failure
- **Expectation**: System maintains SLO through auto-scaling

### Scenario 3: Data Pipeline Failure (30 min)
- **T+0**: Corrupt upstream data
- **T+10**: Schema change in data source
- **T+20**: Complete pipeline failure
- **Expectation**: Detection within 5 minutes, mitigation within 15

## Success Metrics
- [ ] All scenarios detected within SLA
- [ ] Proper escalation followed
- [ ] Communication clear and timely
- [ ] Services recovered successfully
- [ ] SLOs maintained (or violations expected)

## Debrief
- What went well?
- What went wrong?
- Action items for improvement
```

---

## Best Practices

1. **Start Small**: Begin with low-impact experiments
2. **Monitor Everything**: Have comprehensive observability
3. **Have Rollback Plan**: Always be able to stop quickly
4. **Communicate**: Inform stakeholders before experiments
5. **Learn Continuously**: Document and share findings
6. **Automate**: Make chaos engineering routine
7. **Blame-Free**: Focus on system improvements

## Key Takeaways

- Chaos engineering builds confidence in system resilience
- Start with hypothesis, design experiments, measure results
- ML systems have unique failure modes to test
- Automate chaos for continuous resilience testing
- GameDays are valuable for team preparedness

## Exercises

1. Design chaos experiment for your ML service
2. Implement model failure injection
3. Set up Chaos Mesh on Kubernetes
4. Run GameDay exercise with team
5. Create chaos experiment dashboard

## Additional Resources

- "Chaos Engineering" by Casey Rosenthal & Nora Jones
- "Chaos Engineering" by Netflix
- Chaos Mesh documentation
- Gremlin chaos engineering resources
- AWS Fault Injection Simulator
