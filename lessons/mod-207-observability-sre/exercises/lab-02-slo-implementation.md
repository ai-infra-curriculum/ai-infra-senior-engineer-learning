# Lab 02: SLO Implementation and Monitoring

## Objective
Define and implement comprehensive SLOs for ML prediction service with automated monitoring and alerting.

## Duration
3-4 hours

## Part 1: Define SLOs (30 min)

### TODO: Identify User Journeys
Document critical user interactions:
1. User requests prediction
2. System returns result
3. Result is accurate

### TODO: Define SLIs

Create `slo_definitions.yaml`:
```yaml
# TODO: Define SLIs for:
# 1. Availability SLI
# 2. Latency SLI (P95)
# 3. Accuracy SLI
# 4. Freshness SLI

# For each SLI define:
# - Measurement method
# - Data source (Prometheus query)
# - Target value
# - Measurement window
```

### TODO: Set SLO Targets

Document SLO targets:
- Availability: 99.9% (30-day window)
- Latency P95: 200ms (5-minute window)
- Accuracy: 85% (24-hour window)
- Feature freshness: <1 hour

## Part 2: Implement SLI Tracking (60 min)

### TODO: Create SLI Metrics

```python
# slo/sli_metrics.py
# TODO: Implement SLI tracking:

class SLITracker:
    def __init__(self):
        # TODO: Initialize Prometheus metrics
        pass

    def record_availability(self, success: bool):
        # TODO: Record request success/failure
        pass

    def record_latency(self, latency_seconds: float):
        # TODO: Record request latency
        pass

    def record_accuracy(self, prediction, actual):
        # TODO: Record prediction vs actual
        pass

    def calculate_availability_sli(self, window: str) -> float:
        # TODO: Query Prometheus for availability
        # Return: percentage of successful requests
        pass

    def calculate_latency_sli(self, percentile: float, window: str) -> float:
        # TODO: Query Prometheus for latency percentile
        # Return: latency in milliseconds
        pass
```

### TODO: Integrate with ML Service

Update prediction service to track SLIs:
```python
# TODO: Add SLI tracking to /predict endpoint
```

## Part 3: Error Budget Implementation (60 min)

### TODO: Create Error Budget Calculator

```python
# slo/error_budget.py
# TODO: Implement error budget calculation

class ErrorBudgetCalculator:
    def __init__(self, slo_target: float, window_days: int):
        # TODO: Initialize with SLO parameters
        pass

    def allowed_error_rate(self) -> float:
        # TODO: Calculate allowed error rate
        # Example: 99.9% SLO = 0.1% allowed errors
        pass

    def allowed_downtime(self) -> timedelta:
        # TODO: Calculate allowed downtime
        # Example: 99.9% over 30 days = ~43 minutes
        pass

    def remaining_budget(self, current_error_rate: float, elapsed_days: int) -> float:
        # TODO: Calculate remaining error budget
        pass

    def burn_rate(self, current_error_rate: float) -> float:
        # TODO: Calculate current burn rate
        # Example: 2x means consuming budget twice as fast
        pass

    def is_budget_exhausted(self) -> bool:
        # TODO: Check if error budget is exhausted
        pass
```

### TODO: Create Error Budget Dashboard

Create Grafana dashboard showing:
- Current error budget status
- Burn rate
- Time until budget exhaustion
- Historical burn rate

## Part 4: Multi-Window Alerting (45 min)

### TODO: Implement Multi-Burn-Rate Alerts

```yaml
# prometheus/slo-alerts.yaml
# TODO: Create multi-window alerts:

groups:
  - name: slo_alerts
    rules:
    # TODO: Fast burn alert (2% budget in 1 hour)
    # - Check 1-hour window
    # - Check 5-minute window
    # - Alert if both above threshold

    # TODO: Slow burn alert (10% budget in 24 hours)
    # - Check 24-hour window
    # - Check 1-hour window
    # - Alert if both above threshold
```

### TODO: Configure Alert Routing

```yaml
# alertmanager/config.yaml
# TODO: Route alerts by severity:
# - Critical (fast burn) → PagerDuty
# - Warning (slow burn) → Slack
```

## Part 5: SLO Monitoring Dashboard (45 min)

### TODO: Create Comprehensive SLO Dashboard

Dashboard should include:

1. **SLO Status Panel**
   - Current SLI value
   - SLO target
   - Status (meeting/violating)

2. **Error Budget Panel**
   - Remaining budget
   - Burn rate
   - Time to exhaustion

3. **Time Series Graphs**
   - SLI over time
   - Error budget consumption
   - Burn rate history

4. **Alerts Panel**
   - Active SLO alerts
   - Recent violations
   - Alert history

### TODO: Implement SLO Calculation

```promql
# TODO: Write PromQL queries for:

# 1. Availability SLI (30-day)
# Calculate: successful_requests / total_requests

# 2. Latency P95 SLI
# Calculate: histogram_quantile(0.95, ...)

# 3. Error budget remaining
# Calculate: budget - consumed

# 4. Burn rate
# Calculate: current_error_rate / allowed_error_rate
```

## Part 6: SLO Reporting (30 min)

### TODO: Generate SLO Report

```python
# slo/reporter.py
# TODO: Implement SLO reporting

class SLOReporter:
    def generate_monthly_report(self) -> dict:
        # TODO: Generate report with:
        # - SLO compliance percentage
        # - Number of violations
        # - Error budget consumption
        # - Recommendations
        pass

    def export_to_pdf(self, report: dict):
        # TODO: Export report to PDF
        pass

    def send_email(self, report: dict, recipients: list):
        # TODO: Email report to stakeholders
        pass
```

## Deliverables

1. **SLO definitions** (YAML)
   - Clear, measurable SLIs
   - Realistic targets
   - Documented methodology

2. **SLI tracking implementation**
   - Metrics collection
   - PromQL queries
   - Integration with service

3. **Error budget system**
   - Calculation logic
   - Monitoring dashboard
   - Alerting

4. **Multi-window alerting**
   - Prometheus rules
   - Alertmanager configuration
   - Alert routing

5. **SLO dashboard**
   - Grafana dashboard JSON
   - Documentation
   - Screenshots

## Validation

- [ ] SLIs defined and documented
- [ ] Metrics being collected
- [ ] Error budget calculation working
- [ ] Alerts firing correctly
- [ ] Dashboard shows accurate data
- [ ] Report generation working

## Bonus

1. Implement ticket-based error budget policy
2. Add cost-based SLOs
3. Create SLO simulator
4. Build SLO prediction model
