# Lab 04: Canary Deployment with Automated Rollback

## Objective
Implement automated canary deployment with health monitoring and rollback for ML models.

## Duration
4-5 hours

## Tasks

### 1. Kubernetes Deployment Setup (45 min)
- Create stable and canary deployments
- Configure service for traffic splitting
- Set up resource limits and probes

### 2. Canary Controller (90 min)
- Implement `CanaryController` class
- Progressive traffic increase (10% → 25% → 50% → 100%)
- Health check integration with Prometheus
- Automated promotion logic

### 3. Monitoring Integration (60 min)
- Define health check metrics (error rate, latency, drift)
- Query Prometheus for canary health
- Implement alerting for failures
- Create Grafana dashboard

### 4. Automated Rollback (45 min)
- Detect failing health checks
- Implement rollback mechanism
- Test rollback scenarios
- Document incident response

## Deliverables
- Kubernetes manifests for canary deployment
- Canary controller implementation
- Health check monitoring system
- Rollback automation
- Runbook for canary deployments

## Success Criteria
- [ ] Canary deployment gradually increases traffic
- [ ] Health checks detect issues
- [ ] Automatic rollback on failure
- [ ] Successful promotion to 100%
- [ ] Dashboard shows canary metrics
- [ ] Rollback tested and working
