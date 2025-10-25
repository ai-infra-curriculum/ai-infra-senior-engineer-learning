# Lab 03: A/B Testing Framework for ML Models

## Objective
Implement a production-ready A/B testing framework for safely deploying and evaluating ML models.

## Duration
4-5 hours

## Tasks

### 1. Traffic Splitting Service (60 min)
- Implement consistent hash-based user assignment
- Create traffic splitter with configurable percentages
- Ensure users always see same variant

### 2. A/B Testing API (90 min)
- Build Flask/FastAPI service
- Load multiple model versions
- Route requests based on variant assignment
- Log predictions and variants
- Expose Prometheus metrics

### 3. Statistical Analysis (60 min)
- Implement z-test for proportions
- Calculate confidence intervals
- Determine statistical significance
- Generate experiment reports

### 4. Automated Analysis (45 min)
- Create analysis pipeline
- Compute sample size requirements
- Generate experiment dashboards
- Make go/no-go recommendations

## Deliverables
- Traffic splitting implementation
- A/B testing service with multiple models
- Statistical analysis module
- Grafana dashboard showing A/B results
- Experiment report generator

## Success Criteria
- [ ] Users consistently assigned to variants
- [ ] Both model versions served correctly
- [ ] All predictions logged
- [ ] Statistical significance computed correctly
- [ ] Dashboard shows real-time metrics
- [ ] Experiment report generated with recommendations
