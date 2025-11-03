# Lecture 05: A/B Testing for ML Models

## Learning Objectives

By the end of this lecture, you will be able to:

- Design A/B testing strategies for ML models that measure real business impact beyond offline metrics validating models with production traffic before full rollout
- Implement statistical significance testing using t-tests, chi-square tests, and sequential testing (SPRT) with proper sample size calculation and power analysis
- Architect multi-armed bandit algorithms (epsilon-greedy, Thompson sampling, UCB) for dynamic traffic allocation maximizing performance while exploring new models
- Configure progressive rollout strategies with automated traffic ramping (5%→10%→25%→50%→100%) based on confidence intervals and business metrics
- Design experiment frameworks tracking multiple metrics (business KPIs, ML metrics, latency, error rates) with guardrail metrics preventing harmful deployments
- Implement A/B test infrastructure with proper randomization (user-level, session-level), consistent bucketing, and treatment assignment logging
- Analyze A/B test results calculating statistical significance, confidence intervals, minimum detectable effect, and making ship/no-ship decisions
- Build experimentation platforms enabling data scientists to self-serve A/B tests with experiment configuration, automated analysis, and result visualization

## Overview

A/B testing (or online experimentation) for ML models allows you to safely deploy new models to production and measure their impact on real users and business metrics. This is critical for making data-driven decisions about model deployments.

## A/B Testing Fundamentals

### Why A/B Test ML Models?

**Offline vs Online Performance:**
```python
# Offline evaluation (validation set)
offline_accuracy = 0.92

# Online evaluation (production A/B test)
# Model A (baseline): conversion_rate = 0.05
# Model B (new model): conversion_rate = 0.048

# New model performs WORSE despite better offline metrics!
```

**Reasons for discrepancy:**
1. **Training-Serving Skew**: Subtle differences in feature computation
2. **Data Distribution Shift**: Real-world data differs from training data
3. **User Behavior Changes**: Model affects user behavior
4. **Business Metrics**: ML metrics != business metrics

### A/B Test Design

```
┌────────────────────────────────────────────────────────┐
│                 A/B Test Architecture                   │
└────────────────────────────────────────────────────────┘

            User Request
                 │
                 ▼
        ┌──────────────────┐
        │   Load Balancer  │
        │  (Traffic Split) │
        └──────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Model A    │  │   Model B    │
│  (Control)   │  │  (Treatment) │
│  50% Traffic │  │  50% Traffic │
└──────────────┘  └──────────────┘
        │                 │
        └────────┬────────┘
                 ▼
        ┌──────────────────┐
        │  Metrics Logger  │
        │  (Predictions,   │
        │   Outcomes,      │
        │   Latency)       │
        └──────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │    Analytics     │
        │  (Statistical    │
        │   Significance)  │
        └──────────────────┘
```

---

## Implementation

### Traffic Splitting Service

```python
# ab_testing/traffic_splitter.py
import hashlib
import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class VariantType(Enum):
    CONTROL = "control"
    TREATMENT = "treatment"

@dataclass
class Variant:
    name: str
    model_version: str
    traffic_percentage: float

class TrafficSplitter:
    def __init__(self, variants: List[Variant]):
        """Initialize traffic splitter with variants"""
        self.variants = variants

        # Validate traffic percentages sum to 1.0
        total_traffic = sum(v.traffic_percentage for v in variants)
        assert abs(total_traffic - 1.0) < 0.001, f"Traffic percentages must sum to 1.0, got {total_traffic}"

    def assign_variant(self, user_id: str, experiment_id: str) -> Variant:
        """Consistently assign user to variant"""
        # Create hash of user_id + experiment_id for consistency
        hash_input = f"{user_id}:{experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

        # Convert to [0, 1] range
        random_value = (hash_value % 10000) / 10000.0

        # Assign to variant based on traffic percentages
        cumulative = 0.0
        for variant in self.variants:
            cumulative += variant.traffic_percentage
            if random_value < cumulative:
                logger.debug(f"Assigned user {user_id} to variant {variant.name}")
                return variant

        # Fallback to last variant
        return self.variants[-1]

# Example usage
variants = [
    Variant(name="control", model_version="v1.0", traffic_percentage=0.5),
    Variant(name="treatment", model_version="v2.0", traffic_percentage=0.5)
]

splitter = TrafficSplitter(variants)
variant = splitter.assign_variant(user_id="user123", experiment_id="exp_001")
print(f"Assigned to: {variant.name} (model {variant.model_version})")
```

### A/B Testing Service

```python
# ab_testing/ab_test_service.py
from flask import Flask, request, jsonify
import mlflow
import mlflow.pyfunc
from traffic_splitter import TrafficSplitter, Variant
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics
prediction_counter = Counter(
    'model_predictions_total',
    'Total predictions per variant',
    ['variant', 'model_version']
)

prediction_latency = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency per variant',
    ['variant', 'model_version']
)

# Load models
models = {}

def load_models():
    """Load all model variants"""
    global models

    # Load control model
    models['control'] = mlflow.pyfunc.load_model("models:/churn_predictor/1")

    # Load treatment model
    models['treatment'] = mlflow.pyfunc.load_model("models:/churn_predictor/2")

    logger.info("Models loaded successfully")

# Initialize traffic splitter
variants = [
    Variant(name="control", model_version="v1.0", traffic_percentage=0.5),
    Variant(name="treatment", model_version="v2.0", traffic_percentage=0.5)
]
splitter = TrafficSplitter(variants)

@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction with A/B testing"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        features = data.get('features')
        experiment_id = data.get('experiment_id', 'default_experiment')

        if not user_id or not features:
            return jsonify({'error': 'user_id and features required'}), 400

        # Assign variant
        variant = splitter.assign_variant(user_id, experiment_id)

        # Make prediction with timing
        start_time = time.time()
        model = models[variant.name]
        prediction = model.predict([features])[0]
        latency = time.time() - start_time

        # Log metrics
        prediction_counter.labels(
            variant=variant.name,
            model_version=variant.model_version
        ).inc()

        prediction_latency.labels(
            variant=variant.name,
            model_version=variant.model_version
        ).observe(latency)

        # Log prediction for analysis
        log_prediction(
            user_id=user_id,
            variant=variant.name,
            model_version=variant.model_version,
            prediction=prediction,
            latency=latency,
            features=features
        )

        return jsonify({
            'prediction': int(prediction),
            'variant': variant.name,
            'model_version': variant.model_version,
            'latency_ms': latency * 1000
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def log_prediction(user_id, variant, model_version, prediction, latency, features):
    """Log prediction for later analysis"""
    import json
    from datetime import datetime

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'variant': variant,
        'model_version': model_version,
        'prediction': prediction,
        'latency': latency,
        'features': features
    }

    # In production, send to data warehouse / analytics platform
    # For now, log to file
    with open('predictions_log.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

@app.route('/metrics', methods=['GET'])
def metrics():
    """Expose Prometheus metrics"""
    return generate_latest()

if __name__ == '__main__':
    load_models()
    app.run(host='0.0.0.0', port=5000)
```

---

## Statistical Analysis

### Computing Statistical Significance

```python
# ab_testing/statistical_analysis.py
import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd

@dataclass
class ExperimentResults:
    """Results from A/B test"""
    control_conversions: int
    control_total: int
    treatment_conversions: int
    treatment_total: int

    @property
    def control_rate(self) -> float:
        return self.control_conversions / self.control_total if self.control_total > 0 else 0

    @property
    def treatment_rate(self) -> float:
        return self.treatment_conversions / self.treatment_total if self.treatment_total > 0 else 0

    @property
    def lift(self) -> float:
        """Calculate relative lift"""
        if self.control_rate == 0:
            return 0
        return (self.treatment_rate - self.control_rate) / self.control_rate

class ABTestAnalyzer:
    def __init__(self, alpha: float = 0.05):
        """Initialize analyzer with significance level"""
        self.alpha = alpha

    def z_test(self, results: ExperimentResults) -> Tuple[float, float, bool]:
        """Perform z-test for proportions"""
        # Calculate pooled proportion
        total_conversions = results.control_conversions + results.treatment_conversions
        total_samples = results.control_total + results.treatment_total
        pooled_prob = total_conversions / total_samples

        # Calculate standard error
        se = np.sqrt(pooled_prob * (1 - pooled_prob) * (
            1/results.control_total + 1/results.treatment_total
        ))

        # Calculate z-statistic
        z_stat = (results.treatment_rate - results.control_rate) / se

        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        # Determine significance
        is_significant = p_value < self.alpha

        return z_stat, p_value, is_significant

    def chi_square_test(self, results: ExperimentResults) -> Tuple[float, float, bool]:
        """Perform chi-square test"""
        # Create contingency table
        observed = np.array([
            [results.control_conversions, results.control_total - results.control_conversions],
            [results.treatment_conversions, results.treatment_total - results.treatment_conversions]
        ])

        # Perform chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)

        is_significant = p_value < self.alpha

        return chi2, p_value, is_significant

    def calculate_confidence_interval(self, results: ExperimentResults,
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for lift"""
        # Calculate standard error of difference
        se_control = np.sqrt(results.control_rate * (1 - results.control_rate) / results.control_total)
        se_treatment = np.sqrt(results.treatment_rate * (1 - results.treatment_rate) / results.treatment_total)
        se_diff = np.sqrt(se_control**2 + se_treatment**2)

        # Calculate z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence) / 2)

        # Calculate confidence interval
        diff = results.treatment_rate - results.control_rate
        margin = z_score * se_diff

        lower = diff - margin
        upper = diff + margin

        return lower, upper

    def calculate_sample_size(self, baseline_rate: float, mde: float,
                            power: float = 0.8, alpha: float = 0.05) -> int:
        """Calculate required sample size per variant

        Args:
            baseline_rate: Current conversion rate
            mde: Minimum detectable effect (e.g., 0.02 for 2% absolute increase)
            power: Statistical power (1 - beta)
            alpha: Significance level
        """
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)

        # Treatment rate
        treatment_rate = baseline_rate + mde

        # Calculate sample size
        pooled_rate = (baseline_rate + treatment_rate) / 2

        n = (
            (z_alpha * np.sqrt(2 * pooled_rate * (1 - pooled_rate)) +
             z_beta * np.sqrt(baseline_rate * (1 - baseline_rate) + treatment_rate * (1 - treatment_rate))) ** 2
        ) / (mde ** 2)

        return int(np.ceil(n))

    def generate_report(self, results: ExperimentResults) -> dict:
        """Generate comprehensive A/B test report"""
        z_stat, p_value, is_significant = self.z_test(results)
        lower_ci, upper_ci = self.calculate_confidence_interval(results)

        report = {
            'control': {
                'conversions': results.control_conversions,
                'total': results.control_total,
                'rate': results.control_rate
            },
            'treatment': {
                'conversions': results.treatment_conversions,
                'total': results.treatment_total,
                'rate': results.treatment_rate
            },
            'analysis': {
                'absolute_lift': results.treatment_rate - results.control_rate,
                'relative_lift': results.lift,
                'z_statistic': z_stat,
                'p_value': p_value,
                'is_significant': is_significant,
                'confidence_interval_95': {
                    'lower': lower_ci,
                    'upper': upper_ci
                }
            },
            'recommendation': self._get_recommendation(results, is_significant)
        }

        return report

    def _get_recommendation(self, results: ExperimentResults, is_significant: bool) -> str:
        """Generate recommendation based on results"""
        if not is_significant:
            return "No significant difference detected. Continue with control model or extend test duration."

        if results.lift > 0:
            return f"Treatment model shows {results.lift*100:.1f}% improvement. Recommend full deployment."
        else:
            return f"Treatment model shows {abs(results.lift)*100:.1f}% decline. Do not deploy."

# Usage example
analyzer = ABTestAnalyzer(alpha=0.05)

# Example results
results = ExperimentResults(
    control_conversions=450,
    control_total=10000,
    treatment_conversions=485,
    treatment_total=10000
)

# Generate report
report = analyzer.generate_report(results)

print(f"Control rate: {report['control']['rate']:.4f}")
print(f"Treatment rate: {report['treatment']['rate']:.4f}")
print(f"Relative lift: {report['analysis']['relative_lift']*100:.2f}%")
print(f"P-value: {report['analysis']['p_value']:.4f}")
print(f"Significant: {report['analysis']['is_significant']}")
print(f"\nRecommendation: {report['recommendation']}")

# Calculate required sample size
required_n = analyzer.calculate_sample_size(
    baseline_rate=0.045,
    mde=0.003,  # Want to detect 0.3% absolute improvement
    power=0.8,
    alpha=0.05
)
print(f"\nRequired sample size per variant: {required_n:,}")
```

---

## Multi-Armed Bandits

### Epsilon-Greedy Bandit

```python
# ab_testing/bandits.py
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class EpsilonGreedyBandit:
    def __init__(self, variants: List[str], epsilon: float = 0.1):
        """Initialize epsilon-greedy bandit

        Args:
            variants: List of variant names
            epsilon: Exploration rate (0 to 1)
        """
        self.variants = variants
        self.epsilon = epsilon

        # Track statistics
        self.rewards = {v: [] for v in variants}
        self.counts = {v: 0 for v in variants}

    def select_variant(self) -> str:
        """Select variant using epsilon-greedy strategy"""
        # Explore with probability epsilon
        if np.random.random() < self.epsilon:
            variant = np.random.choice(self.variants)
            logger.debug(f"Exploring: selected {variant}")
            return variant

        # Exploit: choose variant with highest average reward
        avg_rewards = {
            v: np.mean(rewards) if rewards else 0
            for v, rewards in self.rewards.items()
        }

        best_variant = max(avg_rewards, key=avg_rewards.get)
        logger.debug(f"Exploiting: selected {best_variant}")
        return best_variant

    def update(self, variant: str, reward: float):
        """Update variant statistics with observed reward"""
        self.rewards[variant].append(reward)
        self.counts[variant] += 1

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return {
            v: {
                'count': self.counts[v],
                'avg_reward': np.mean(self.rewards[v]) if self.rewards[v] else 0,
                'total_reward': sum(self.rewards[v])
            }
            for v in self.variants
        }

class ThompsonSamplingBandit:
    def __init__(self, variants: List[str]):
        """Initialize Thompson Sampling bandit (Beta-Bernoulli)"""
        self.variants = variants

        # Beta distribution parameters (alpha, beta)
        # Start with uniform prior Beta(1, 1)
        self.alpha = {v: 1 for v in variants}
        self.beta = {v: 1 for v in variants}

    def select_variant(self) -> str:
        """Select variant using Thompson Sampling"""
        # Sample from each variant's posterior distribution
        samples = {
            v: np.random.beta(self.alpha[v], self.beta[v])
            for v in self.variants
        }

        # Select variant with highest sample
        best_variant = max(samples, key=samples.get)
        logger.debug(f"Thompson Sampling selected: {best_variant}")
        return best_variant

    def update(self, variant: str, reward: float):
        """Update posterior distribution

        Args:
            variant: Selected variant
            reward: Binary reward (0 or 1)
        """
        if reward > 0:
            self.alpha[variant] += 1
        else:
            self.beta[variant] += 1

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return {
            v: {
                'alpha': self.alpha[v],
                'beta': self.beta[v],
                'mean': self.alpha[v] / (self.alpha[v] + self.beta[v]),
                'trials': self.alpha[v] + self.beta[v] - 2
            }
            for v in self.variants
        }

# Simulation example
def simulate_bandit_experiment(bandit, true_rates: Dict[str, float], n_trials: int = 10000):
    """Simulate bandit experiment"""
    cumulative_reward = 0

    for trial in range(n_trials):
        # Select variant
        variant = bandit.select_variant()

        # Simulate reward based on true rate
        reward = 1 if np.random.random() < true_rates[variant] else 0
        cumulative_reward += reward

        # Update bandit
        bandit.update(variant, reward)

    # Print results
    stats = bandit.get_statistics()
    print("\nBandit Results:")
    for variant, variant_stats in stats.items():
        print(f"{variant}: {variant_stats}")

    print(f"\nTotal reward: {cumulative_reward}")
    print(f"Average reward: {cumulative_reward / n_trials:.4f}")

# Usage
print("Epsilon-Greedy Bandit:")
eg_bandit = EpsilonGreedyBandit(['control', 'treatment'], epsilon=0.1)
simulate_bandit_experiment(eg_bandit, {'control': 0.045, 'treatment': 0.052})

print("\n" + "="*50)
print("Thompson Sampling Bandit:")
ts_bandit = ThompsonSamplingBandit(['control', 'treatment'])
simulate_bandit_experiment(ts_bandit, {'control': 0.045, 'treatment': 0.052})
```

---

## Progressive Rollout

### Canary Deployment Controller

```python
# ab_testing/progressive_rollout.py
from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class RolloutStage:
    traffic_percentage: float
    duration_minutes: int
    success_criteria: dict

class ProgressiveRollout:
    def __init__(self, model_name: str, new_version: str):
        self.model_name = model_name
        self.new_version = new_version
        self.current_stage = 0

        # Define rollout stages
        self.stages = [
            RolloutStage(
                traffic_percentage=0.05,  # 5% traffic
                duration_minutes=30,
                success_criteria={
                    'max_error_rate': 0.01,
                    'min_success_rate': 0.99,
                    'max_latency_p99': 200  # ms
                }
            ),
            RolloutStage(
                traffic_percentage=0.25,  # 25% traffic
                duration_minutes=60,
                success_criteria={
                    'max_error_rate': 0.01,
                    'min_success_rate': 0.99,
                    'max_latency_p99': 200
                }
            ),
            RolloutStage(
                traffic_percentage=0.50,  # 50% traffic
                duration_minutes=120,
                success_criteria={
                    'max_error_rate': 0.005,
                    'min_success_rate': 0.995,
                    'max_latency_p99': 200
                }
            ),
            RolloutStage(
                traffic_percentage=1.0,  # 100% traffic
                duration_minutes=0,
                success_criteria={}
            )
        ]

    def check_metrics(self, stage: RolloutStage) -> bool:
        """Check if metrics meet success criteria"""
        # In production, query metrics from monitoring system
        metrics = self._get_current_metrics()

        for criterion, threshold in stage.success_criteria.items():
            if criterion.startswith('max_'):
                metric_name = criterion[4:]
                if metrics.get(metric_name, 0) > threshold:
                    logger.error(f"Metric {metric_name} exceeds threshold: {metrics[metric_name]} > {threshold}")
                    return False

            elif criterion.startswith('min_'):
                metric_name = criterion[4:]
                if metrics.get(metric_name, 1) < threshold:
                    logger.error(f"Metric {metric_name} below threshold: {metrics[metric_name]} < {threshold}")
                    return False

        return True

    def _get_current_metrics(self) -> dict:
        """Get current metrics from monitoring system"""
        # In production, query Prometheus/Grafana
        # For simulation, return mock metrics
        return {
            'error_rate': 0.005,
            'success_rate': 0.995,
            'latency_p99': 150
        }

    def execute_rollout(self):
        """Execute progressive rollout"""
        logger.info(f"Starting progressive rollout for {self.model_name} v{self.new_version}")

        for i, stage in enumerate(self.stages):
            logger.info(f"\nStage {i+1}/{len(self.stages)}: Rolling out to {stage.traffic_percentage*100}% traffic")

            # Update traffic split
            self._update_traffic_split(stage.traffic_percentage)

            # Wait for stabilization
            stabilization_time = min(5, stage.duration_minutes)
            logger.info(f"Waiting {stabilization_time} minutes for stabilization...")
            time.sleep(stabilization_time * 60)

            # Monitor stage
            stage_start = datetime.now()
            stage_end = stage_start + timedelta(minutes=stage.duration_minutes)

            while datetime.now() < stage_end:
                # Check metrics
                if not self.check_metrics(stage):
                    logger.error("Metrics failed! Rolling back...")
                    self._rollback()
                    return False

                # Wait before next check
                time.sleep(60)  # Check every minute

            logger.info(f"Stage {i+1} completed successfully")
            self.current_stage = i + 1

        logger.info(f"\nRollout completed successfully! {self.model_name} v{self.new_version} at 100% traffic")
        return True

    def _update_traffic_split(self, treatment_percentage: float):
        """Update traffic split configuration"""
        logger.info(f"Updating traffic split: control={1-treatment_percentage:.0%}, treatment={treatment_percentage:.0%}")
        # In production, update Kubernetes service/Istio/etc.

    def _rollback(self):
        """Rollback to previous version"""
        logger.warning(f"Rolling back {self.model_name} to 100% control version")
        self._update_traffic_split(0.0)

# Usage
rollout = ProgressiveRollout(model_name="churn_predictor", new_version="v2.0")
success = rollout.execute_rollout()
```

---

## Best Practices

1. **Define Success Metrics**: Align ML metrics with business objectives
2. **Calculate Sample Size**: Ensure adequate statistical power
3. **Consistent Assignment**: Use hashing for consistent user-variant mapping
4. **Monitor Everything**: Track predictions, latency, errors, business metrics
5. **Set Duration**: Run tests long enough to capture weekly patterns
6. **Avoid Peeking**: Don't stop tests early based on interim results
7. **Consider Seasonality**: Account for day-of-week and seasonal effects

## Key Takeaways

1. **Offline metrics don't guarantee online success**: Always validate in production
2. **Statistical rigor is essential**: Use proper sample sizes and significance testing
3. **Multi-armed bandits optimize exploration/exploitation**: Better than fixed A/B splits for many use cases
4. **Progressive rollouts reduce risk**: Catch issues before full deployment
5. **Business metrics matter most**: Focus on revenue, conversion, engagement

## Exercises

1. Implement A/B testing service with traffic splitting
2. Perform statistical analysis on A/B test results
3. Implement Thompson Sampling bandit
4. Build progressive rollout controller
5. Design A/B test for your ML model with proper sample size calculation

## Additional Resources

- "Trustworthy Online Controlled Experiments" (Kohavi et al.)
- "Multi-Armed Bandit Algorithms" (Kuleshov & Precup)
- Google's "Overlapping Experiment Infrastructure"
- Netflix's experimentation platform papers
