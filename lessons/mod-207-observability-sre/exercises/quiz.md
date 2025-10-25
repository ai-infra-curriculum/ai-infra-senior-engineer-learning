# Module 207: Advanced Observability and SRE Practices - Quiz

## Instructions

This quiz consists of 22 questions covering all topics from Module 207. Answer all questions to assess your understanding of advanced observability and SRE practices for AI infrastructure.

**Passing Score**: 80% (18/22 correct)
**Time Limit**: 60 minutes
**Format**: Multiple choice, short answer, and scenario-based questions

---

## Part 1: Advanced Prometheus (Questions 1-4)

### Question 1
**What is the primary purpose of Prometheus federation?**

A) To backup Prometheus data  
B) To aggregate metrics from multiple Prometheus instances into a hierarchical structure  
C) To replace Prometheus with a more scalable solution  
D) To enable Prometheus to scrape metrics from Kubernetes only  

**Answer**: ________________

### Question 2
**You're implementing long-term storage for Prometheus metrics. Which statement about Thanos is CORRECT?**

A) Thanos requires replacing your existing Prometheus instances  
B) Thanos Sidecar uploads Prometheus blocks to object storage  
C) Thanos can only work with S3 storage  
D) Thanos increases the load on Prometheus servers significantly  

**Answer**: ________________

### Question 3 (Scenario)
**Your ML training jobs generate high-cardinality metrics with thousands of unique `user_id` labels. This is causing Prometheus performance issues. What is the BEST solution?**

A) Add more memory to Prometheus  
B) Remove the user_id label and use recording rules to aggregate metrics  
C) Switch to Elasticsearch for all metrics  
D) Reduce scrape frequency to once per hour  

**Answer**: ________________
**Explanation**: ________________

### Question 4 (Short Answer)
**Write a PromQL query to calculate the 95th percentile GPU utilization across all training jobs in the last 5 minutes.**

```promql
# TODO: Write your query here


```

---

## Part 2: Distributed Tracing (Questions 5-7)

### Question 5
**What is the purpose of trace context propagation in distributed tracing?**

A) To encrypt trace data  
B) To pass trace and span IDs across service boundaries via headers or metadata  
C) To reduce the size of trace data  
D) To automatically fix performance issues  

**Answer**: ________________

### Question 6
**Which sampling strategy makes the sampling decision AFTER a trace is complete?**

A) Head-based sampling  
B) Probabilistic sampling  
C) Tail-based sampling  
D) Rate-limiting sampling  

**Answer**: ________________

### Question 7 (Scenario)
**Your ML inference service has high latency (p99 = 800ms). Traces show: API Gateway (20ms) → Feature Store (450ms) → Model Inference (80ms) → Result Caching (250ms). What should you optimize FIRST?**

A) Upgrade the model to a faster version  
B) Optimize the Feature Store (database indexes, caching)  
C) Increase API Gateway resources  
D) Remove result caching entirely  

**Answer**: ________________
**Justification**: ________________

---

## Part 3: Log Aggregation (Questions 8-10)

### Question 8
**What is the PRIMARY advantage of Loki compared to Elasticsearch for log aggregation?**

A) Better full-text search capabilities  
B) Lower storage costs through label-based indexing instead of full-text indexing  
C) Faster query performance for all use cases  
D) Built-in machine learning capabilities  

**Answer**: ________________

### Question 9
**In an ELK stack, what is the role of Logstash?**

A) Store log data  
B) Visualize and query logs  
C) Parse, filter, enrich, and route logs before storage  
D) Collect logs from containers  

**Answer**: ________________

### Question 10 (Short Answer)
**Write an Elasticsearch query (JSON format) to find all ERROR logs from the "training-service" in the last 24 hours, sorted by timestamp descending.**

```json
// TODO: Write your Elasticsearch query here






```

---

## Part 4: ML-Specific Observability (Questions 11-14)

### Question 11
**Which statistical test is commonly used to detect data drift by comparing two distributions?**

A) T-test  
B) Kolmogorov-Smirnov (KS) test  
C) Linear regression  
D) Principal Component Analysis  

**Answer**: ________________

### Question 12
**What does a Population Stability Index (PSI) value greater than 0.2 indicate?**

A) The model is performing well  
B) Significant distribution drift has occurred  
C) The feature should be removed  
D) The model needs retraining immediately  

**Answer**: ________________

### Question 13 (Scenario)
**Your model's accuracy on the validation set is 95%, but production accuracy (measured through feedback) is only 82%. What is this called and what's the likely cause?**

A) Data drift - input distribution changed  
B) Concept drift - relationship between features and target changed  
C) Model overfitting - model memorized training data  
D) Both A and B are possible causes  

**Answer**: ________________
**Explanation**: ________________

### Question 14 (Short Answer)
**List THREE key metrics you should monitor for a production ML inference service (besides standard application metrics like CPU/memory).**

1. ________________
2. ________________
3. ________________

---

## Part 5: SRE Principles (Questions 15-17)

### Question 15
**What is the relationship between SLI, SLO, and SLA?**

A) SLI < SLO < SLA  
B) SLA is a business agreement based on SLO, which is measured by SLI  
C) They are three names for the same concept  
D) SLA is more strict than SLO  

**Answer**: ________________

### Question 16 (Scenario)
**Your ML inference service has an SLO of 99.9% availability (43 minutes downtime/month). You've already used 30 minutes this month. What should you do?**

A) Continue deploying new features as planned  
B) Pause risky changes and focus on reliability improvements  
C) Immediately shut down the service  
D) Increase the SLO to 99.95%  

**Answer**: ________________

### Question 17 (Short Answer)
**Define "toil" in the context of SRE and give ONE example from AI infrastructure.**

**Definition**: ________________

**Example**: ________________

---

## Part 6: Incident Management (Questions 18-20)

### Question 18
**What is the PRIMARY goal of a blameless post-mortem?**

A) To identify who caused the incident  
B) To learn from failures and prevent recurrence without blaming individuals  
C) To document the incident for legal purposes  
D) To determine compensation for affected users  

**Answer**: ________________

### Question 19
**Which incident severity would you assign to a scenario where 30% of ML inference requests are failing?**

A) SEV 4 (Low) - Minor issue  
B) SEV 3 (Medium) - Significant impact  
C) SEV 2 (High) - Major service degradation  
D) SEV 1 (Critical) - Complete service outage  

**Answer**: ________________

### Question 20 (Short Answer)
**List the THREE most important sections of an incident post-mortem document.**

1. ________________
2. ________________
3. ________________

---

## Part 7: Chaos Engineering (Questions 21-22)

### Question 21
**What is the first step in conducting a chaos engineering experiment?**

A) Inject failures randomly  
B) Define a steady state and hypothesis about system behavior  
C) Deploy Chaos Mesh to production  
D) Notify all stakeholders  

**Answer**: ________________

### Question 22 (Scenario)
**You want to test how your ML training system handles GPU node failures. Which chaos experiment would you run?**

A) Randomly delete pods every 5 minutes  
B) Kill a specific GPU node and observe if training checkpoints correctly and resumes on another node  
C) Shut down the entire Kubernetes cluster  
D) Inject network latency between all services  

**Answer**: ________________
**Expected Outcome**: ________________

---

## Answer Key

**Note**: This section should be on a separate page or hidden from students during the quiz.

### Answers

1. **B** - Prometheus federation aggregates metrics hierarchically
2. **B** - Thanos Sidecar uploads blocks to object storage
3. **B** - Remove high-cardinality labels, use aggregation; *Explanation: High cardinality kills Prometheus performance. Aggregate by job/team instead of user_id.*
4. **Query**: 
   ```promql
   histogram_quantile(0.95,
     rate(nvidia_gpu_duty_cycle_bucket[5m])
   )
   ```
   Or:
   ```promql
   quantile(0.95, rate(nvidia_gpu_duty_cycle[5m]))
   ```

5. **B** - Trace context propagation passes trace/span IDs across services
6. **C** - Tail-based sampling decides after trace completion
7. **B** - Feature Store optimization (450ms is the largest component); *Justification: Optimize the slowest component first (450ms). Add caching, optimize queries, add indexes.*

8. **B** - Lower storage costs through label-based indexing
9. **C** - Logstash parses, filters, enriches, and routes logs
10. **Query**:
    ```json
    {
      "query": {
        "bool": {
          "must": [
            {"match": {"service": "training-service"}},
            {"match": {"level": "ERROR"}},
            {"range": {
              "@timestamp": {
                "gte": "now-24h",
                "lte": "now"
              }
            }}
          ]
        }
      },
      "sort": [{"@timestamp": "desc"}]
    }
    ```

11. **B** - Kolmogorov-Smirnov (KS) test
12. **B** - PSI > 0.2 indicates significant distribution drift
13. **D** - Both data drift and concept drift are possible; *Explanation: Could be data drift (features changed) or concept drift (feature-target relationship changed). Need to investigate both.*
14. **Metrics** (any 3 of):
    1. Prediction latency (p50, p95, p99)
    2. Model accuracy/error rate (if ground truth available)
    3. Feature drift scores
    4. Prediction confidence distribution
    5. Data quality metrics (null rate, outliers)
    6. Model throughput (predictions/sec)

15. **B** - SLA is business agreement based on SLO measured by SLI
16. **B** - Pause risky changes, focus on reliability (error budget nearly exhausted)
17. **Definition**: Toil is repetitive, manual, automatable work that scales linearly with service growth.
    **Example**: Manually restarting failed training jobs, manual GPU allocation, manually cleaning up storage

18. **B** - Learn from failures without blame
19. **C** - SEV 2 (High/Major) - 30% failure rate is major degradation
20. **Sections** (any 3 of):
    1. Timeline of events
    2. Root cause analysis
    3. Action items (with owners and due dates)
    4. What went well / What went wrong
    5. Lessons learned

21. **B** - Define steady state and hypothesis
22. **B** - Kill specific GPU node, observe checkpoint/resume; *Expected Outcome: Training should checkpoint state, detect node failure, reschedule pod to another GPU node, resume from checkpoint with minimal loss of progress.*

---

## Grading Rubric

- **Multiple Choice (18 questions)**: 1 point each = 18 points
- **Scenario Questions (6 questions)**: 2 points each (1 for answer, 1 for explanation) = 12 points
- **Short Answer (4 questions)**: Varies (2-3 points each) = 10 points

**Total**: 40 points
**Passing**: 32 points (80%)

## Review Sections

If you scored poorly on specific sections:
- **Questions 1-4**: Review Lecture 01 (Advanced Prometheus)
- **Questions 5-7**: Review Lecture 02 (Distributed Tracing)
- **Questions 8-10**: Review Lecture 03 (Log Aggregation)
- **Questions 11-14**: Review Lecture 04 (ML-Specific Observability)
- **Questions 15-17**: Review Lecture 05 (SRE Principles)
- **Questions 18-20**: Review Lecture 06 (Incident Management)
- **Questions 21-22**: Review Lecture 07 (Chaos Engineering)

---

**Good luck!**
