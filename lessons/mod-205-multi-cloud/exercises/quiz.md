# Module 205: Multi-Cloud Architecture - Quiz

## Instructions

Answer all questions. Each question may have one or more correct answers.

## Questions

### 1. Multi-Cloud Strategy

**Q1.1:** What are the primary drivers for adopting a multi-cloud strategy?
- [ ] A) Vendor lock-in avoidance
- [ ] B) Cost optimization
- [ ] C) Geographic coverage
- [ ] D) Regulatory compliance
- [ ] E) All of the above

**Q1.2:** Which of these is NOT a challenge of multi-cloud architectures?
- [ ] A) Increased complexity
- [ ] B) Data transfer costs
- [ ] C) Vendor-specific features
- [ ] D) Unlimited budget
- [ ] E) Skill requirements

### 2. Networking

**Q2.1:** What protocols are commonly used for multi-cloud VPN connections?
- [ ] A) IPsec
- [ ] B) FTP
- [ ] C) HTTP
- [ ] D) BGP
- [ ] E) WireGuard

**Q2.2:** What is the typical latency range for cross-cloud communication via VPN?
- [ ] A) <1ms
- [ ] B) 10-30ms
- [ ] C) 100-200ms
- [ ] D) >1000ms

### 3. Cost Optimization

**Q3.1:** Which cost optimization strategy typically provides the highest savings?
- [ ] A) Right-sizing instances
- [ ] B) Using Spot/Preemptible instances
- [ ] C) Reserved instances/Committed use discounts
- [ ] D) Storage lifecycle policies

**Q3.2:** What percentage of cost savings can Reserved Instances typically provide?
- [ ] A) 10-20%
- [ ] B) 30-50%
- [ ] C) 50-72%
- [ ] D) 80-90%

### 4. Disaster Recovery

**Q4.1:** What does RTO stand for?
- [ ] A) Recovery Time Objective
- [ ] B) Return To Operations
- [ ] C) Reliable Time Offset
- [ ] D) Redundant Transfer Option

**Q4.2:** Which DR pattern provides the fastest recovery?
- [ ] A) Backup and Restore
- [ ] B) Pilot Light
- [ ] C) Warm Standby
- [ ] D) Hot Standby / Active-Active

### 5. Service Mesh

**Q5.1:** What are the benefits of using Istio in multi-cloud deployments?
- [ ] A) Traffic management
- [ ] B) Security (mTLS)
- [ ] C) Observability
- [ ] D) Service discovery
- [ ] E) All of the above

### 6. Data Replication

**Q6.1:** What is the difference between synchronous and asynchronous replication?
- [ ] A) Synchronous waits for confirmation, asynchronous doesn't
- [ ] B) Synchronous is faster
- [ ] C) Asynchronous provides better consistency
- [ ] D) There is no difference

**Q6.2:** Which replication strategy provides zero RPO?
- [ ] A) Asynchronous
- [ ] B) Synchronous
- [ ] C) Semi-synchronous
- [ ] D) None of the above

### 7. Cloud-Agnostic Design

**Q7.1:** Which tools promote cloud-agnostic infrastructure?
- [ ] A) Terraform
- [ ] B) Kubernetes
- [ ] C) CloudFormation
- [ ] D) Pulumi
- [ ] E) A, B, and D

### 8. Pricing Models

**Q8.1:** Which cloud provider offers sustained use discounts automatically?
- [ ] A) AWS
- [ ] B) GCP
- [ ] C) Azure
- [ ] D) All of them

### 9. Network Pricing

**Q9.1:** Which data transfer is typically free across all cloud providers?
- [ ] A) Ingress (data in)
- [ ] B) Egress (data out)
- [ ] C) Cross-region transfer
- [ ] D) Cross-cloud transfer

### 10. Security

**Q10.1:** What security considerations are unique to multi-cloud?
- [ ] A) Multiple IAM systems
- [ ] B) Cross-cloud encryption
- [ ] C) Unified security monitoring
- [ ] D) Compliance across providers
- [ ] E) All of the above

---

## Short Answer Questions

**Q11:** Describe a scenario where multi-cloud makes more sense than single-cloud.

**Q12:** What are the key metrics to monitor for VPN tunnel health?

**Q13:** How would you implement cost allocation across multiple clouds?

**Q14:** Explain the difference between multi-cloud and hybrid cloud.

**Q15:** What factors should influence the decision of which cloud to use for a specific workload?

---

## Scenario-Based Questions

**Q16:** Your primary AWS region goes down. Describe the steps to failover to GCP.

**Q17:** You notice data transfer costs have increased by 300%. How would you investigate?

**Q18:** Design a multi-cloud DR solution with RTO of 1 hour and RPO of 15 minutes.

**Q19:** Your team wants to deploy a new ML model. How do you decide which cloud to use?

**Q20:** Describe how to implement blue-green deployment across AWS and GCP.

---

## Answer Key

### Multiple Choice Answers

Q1.1: E | Q1.2: D | Q2.1: A, D, E | Q2.2: B | Q3.1: C | Q3.2: C
Q4.1: A | Q4.2: D | Q5.1: E | Q6.1: A | Q6.2: B | Q7.1: E
Q8.1: B | Q9.1: A | Q10.1: E

### Short Answer Guidelines

Q11-Q15: Evaluated based on understanding of concepts, practical application, and completeness.

### Scenario Guidelines

Q16-Q20: Evaluated on practical approach, consideration of trade-offs, and technical accuracy.

---

## Scoring

- Multiple Choice: 2 points each (30 points)
- Short Answer: 6 points each (30 points)
- Scenarios: 8 points each (40 points)
- **Total: 100 points**

**Passing Score: 70%**

---

## Review Topics

If you scored below 70%, review:
- Multi-cloud networking (Lecture 6)
- Cost optimization strategies (Lecture 7)
- Disaster recovery patterns (Lecture 8)
- Cloud-agnostic design principles (Lecture 2)
