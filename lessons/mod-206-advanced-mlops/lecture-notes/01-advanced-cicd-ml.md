# Lecture 01: Advanced CI/CD for ML

> Module 206 — Advanced MLOps. Lead-off lecture.
>
> **Prerequisites:** familiarity with standard software CI/CD (build → test → deploy), basic MLflow / DVC, K8s deployment patterns.

---

## Why "advanced" CI/CD for ML is different

Traditional CI/CD has two artifacts: code and tests. Deploy is a function of `(code, environment) → service`. The system is deterministic enough that "if it built green, it should run green."

ML CI/CD has more inputs. A change can come from:

- **Code** — model architecture, training loop, preprocessing
- **Data** — new training set, schema evolution, drift correction
- **Hyperparameters** — config files, sweep results
- **Dependencies** — framework upgrade (PyTorch 2.3 → 2.4 changed default fp32 matmul precision; that's a behavior change without any code change)
- **Environment** — GPU driver, CUDA version, NCCL version

Any of those can change model behavior. A green build is necessary but not sufficient. You need evidence the new model is actually better (or at least not worse) before promotion.

**The advanced part:** designing pipelines that produce that evidence automatically, gate promotion on it, and roll back safely when post-deploy reality contradicts pre-deploy expectations.

---

## The pipeline stages

A production-grade ML CI/CD pipeline has more stages than its software counterpart. A common shape:

```text
┌──────────┐    ┌────────────┐    ┌──────────┐    ┌─────────────┐
│   Code   │───▶│   Build    │───▶│   Test   │───▶│   Train     │
│  change  │    │ + lint     │    │ unit/    │    │ on candidate │
└──────────┘    │ + format   │    │ integ    │    │ dataset      │
                └────────────┘    └──────────┘    └──────┬──────┘
                                                          ▼
              ┌─────────────────────────────────────────────────┐
              │  Evaluate: metrics + slice-aware + fairness     │
              └────────────────────────┬────────────────────────┘
                                       ▼
              ┌─────────────────────────────────────────────────┐
              │  Compare against current production baseline    │
              └────────────────────────┬────────────────────────┘
                                       ▼
              ┌─────────────────────────────────────────────────┐
              │  Gate: better than baseline by ≥ ε on top-N     │
              │  AND no regression > δ on any slice             │
              └────────────────────────┬────────────────────────┘
                                       ▼
              ┌─────────────────────────────────────────────────┐
              │  Register: MLflow model registry, Staging stage │
              └────────────────────────┬────────────────────────┘
                                       ▼
              ┌─────────────────────────────────────────────────┐
              │  Package: container image + model artifact      │
              └────────────────────────┬────────────────────────┘
                                       ▼
              ┌─────────────────────────────────────────────────┐
              │  Deploy: shadow → canary 1% → 10% → 50% → 100%  │
              └─────────────────────────────────────────────────┘
```

Each stage answers a question:

| Stage | Question |
|---|---|
| Build | Does the code compile / package? |
| Test | Do unit + integration tests pass? |
| Train | Does training converge on the candidate dataset? |
| Evaluate | What are the holdout metrics? |
| Compare | Is this better than what's in production? |
| Gate | Is it better by enough to justify a rollout? |
| Register | Is it recorded as a candidate version? |
| Package | Is the runtime artifact reproducible? |
| Deploy | Is it serving production traffic safely? |

If you skip a stage, you skip its question. The cost shows up later as a bug, a regression, or a 3am page.

---

## Gates that matter

The evaluation gate is the single highest-leverage decision in the pipeline. Three common gate strategies:

### 1. Absolute-threshold gate

> Promote if test accuracy > 0.85.

Simple, brittle. The threshold gets stale as the world changes. Doesn't catch regressions when the new model is "good enough" but worse than what's already serving.

### 2. Relative-to-baseline gate

> Promote if new accuracy ≥ current production accuracy − 0.5pp.

Better. Stays honest as the baseline evolves. The `−0.5pp` slack acknowledges that small differences are noise.

Pitfall: aggregate metrics hide slice regressions. A model that's +0.5pp on average but −5pp for a minority slice is *worse*.

### 3. Multi-dimensional gate

> Promote if:
> - aggregate metric ≥ baseline − ε (e.g., ε = 0.005)
> - no slice regression > δ (e.g., δ = 0.02) on any slice with ≥ N samples
> - cost-per-prediction ≤ baseline + 10%
> - latency P95 ≤ baseline + 10ms
> - fairness metric (disparate impact, equal opportunity) within tolerance

Each dimension is a veto. The pipeline reports which dimensions passed, which failed, and provides a one-pager for human review when something is borderline.

This is the gate worth investing in. The other forms either let bad models through (#1, #2) or burn engineering time on false alarms.

---

## Shadow + canary, not just blue/green

Software blue/green works when the new and old versions are functionally equivalent. ML deployments aren't equivalent by design — that's the point. So you need staging strategies that surface behavioral differences before they affect users.

**Shadow deployment:** route a copy of production traffic to the new model. Don't serve its predictions; just record them. Compare against the current model's predictions on the same inputs. Watch for:

- Distribution shift in predictions (different output histograms)
- Disagreement rate (% of inputs where new ≠ old)
- Latency differences at P95 and P99

Run shadow for at least a full traffic cycle (typically 24-48h) before promoting.

**Canary:** route a small percentage of real traffic to the new model. Watch:

- Business metrics (conversion, click-through, complaint rate) — these can move even when ML metrics don't
- Operational metrics (latency, error rate, GPU utilization)
- Per-slice metrics — does the change disproportionately affect any subgroup?

Standard canary ramp for ML: 1% → 10% → 50% → 100%, with at least 1 hour at each step and explicit go/no-go review at each transition.

**Auto-rollback:** the canary system must auto-rollback on any of:

- Latency P95 > 1.5× baseline
- Error rate > 1.5× baseline
- Any custom guard metric outside acceptable range

Manual rollback is too slow. By the time a human is paged, the canary's customers have already had a bad experience.

---

## Training pipelines as first-class CI/CD

In software, training data is irrelevant to the build. In ML, training data is the build. Treat training data with the same rigor as code:

- **Versioned** (DVC, lakeFS, Delta Lake time travel)
- **Validated** (Great Expectations, Pandera, custom schema checks)
- **Lineage-traceable** (which dataset version produced which model version)
- **Reproducible** (the same dataset version + the same code → the same model, byte-for-byte if possible)

This is the unsexy work that pays for itself the first time you need to answer "why did model v18 perform worse than v17?" When data is versioned and lineage is tracked, the question becomes a 10-minute investigation. When it isn't, the question becomes an unsolvable mystery and you cargo-cult on the failed model rather than debug it.

---

## Pipeline-as-code patterns

Your CI/CD pipeline is itself code. Best practices that take a while to internalize:

### 1. Idempotent stages

A stage should be runnable multiple times with the same inputs and produce the same outputs. This matters because retries are inevitable.

```python
# Bad: not idempotent — increments a counter each run
def evaluate(model, data):
    metrics = compute_metrics(model, data)
    mlflow.log_metric("eval_runs", get_run_count() + 1)
    return metrics

# Good: idempotent — same input → same output
def evaluate(model, data):
    metrics = compute_metrics(model, data)
    mlflow.log_metric(f"eval_{data.version}_accuracy", metrics.accuracy)
    return metrics
```

### 2. Explicit contracts between stages

Each stage's outputs should be a typed artifact, not a side effect on shared mutable state.

```python
# Bad: training stage mutates a global "current_model" pointer
train_model(data)
# evaluate_model reads from the global
evaluate_model(holdout_data)

# Good: training stage returns a versioned artifact
model_artifact = train_model(data)  # returns a path + version
metrics = evaluate_model(model_artifact, holdout_data)
```

### 3. Cache aggressively

ML pipelines are slow. Caching unchanged stages (data prep, feature engineering, even training when the inputs and hyperparameters match) cuts iteration time by an order of magnitude. DVC and similar tools handle this if you commit to declaring your inputs and outputs accurately.

### 4. Fail fast

The earliest cheap stage that can catch a problem should catch it. Don't let a malformed config slip through to a 6-hour training run before you discover the learning rate is `"0.001"` (string) instead of `0.001` (float).

### 5. Observable by default

Every stage emits structured logs to a central store. Every stage emits metrics. Every stage's artifacts are linked back to the run that produced them. When something breaks at 3am, the responder shouldn't be reverse-engineering what happened.

---

## Pitfalls worth memorizing

### Training-serving skew

The most common ML production bug. Feature computation differs between training (often batch, often Python/pandas) and serving (often online, often a different language). The model receives subtly different inputs and quietly underperforms.

Detection: emit feature distributions from both pipelines and compare. Even better: share the same feature-engineering code (a feature store helps here).

### Label leakage

The training process accidentally sees information that wouldn't be available at inference time — future labels, target-derived features. The model looks great offline and falls flat in production.

Detection: deliberately corrupt the feature you suspect (drop it, shuffle it). If the offline metrics drop dramatically, that feature was probably leaking.

### Concept drift without detection

The world changes; the model's assumptions don't. Performance degrades silently because there's no signal that compares production behavior to expected behavior.

Mitigation: log prediction distributions, ground-truth labels (where available), and alert on distribution shift. Schedule routine retraining even if no immediate signal demands it.

### Underspecified retraining triggers

"Retrain weekly" is a starting point, not a strategy. Better: retrain when (drift detected OR time-since-last > N days OR upstream data schema changed). Each trigger should be independent and observable.

### Promote-to-prod without rollback rehearsal

You don't actually know your rollback works until you've executed it. Schedule quarterly rollback drills. Make it boring.

---

## What to do this week

If your team doesn't have an ML CI/CD pipeline yet, build the simplest possible end-to-end version first. Don't optimize. Don't gate. Just get a chain of: code change → automated training → automated evaluation → human review → promote. Then add gates one at a time, each backed by a real failure you've observed.

If your team has a pipeline but it's flaky, audit it for the patterns above. The most common quick win is making the eval stage produce a one-page human-readable summary — this changes the cost of a borderline-promotion decision from "10 minutes of digging" to "30 seconds of skimming," and the decisions improve.

---

## Further reading

- [02 - Feature Stores](./02-feature-stores.md) — solves the training-serving skew problem at the architectural level.
- [03 - Model Registry & Versioning](./03-model-registry-versioning.md) — the registry is the source of truth for "what's in prod."
- [04 - Experiment Tracking](./04-experiment-tracking.md) — the data that feeds the gates.
- [05 - A/B Testing for ML](./05-ab-testing-ml.md) — the production-time analog of the canary stage.
- [06 - Canary Deployments](./06-canary-deployments.md) — deep dive on the canary mechanics.

---

**Next**: [Lecture 02 — Feature Stores](./02-feature-stores.md)
