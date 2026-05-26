# Module 208 Quiz: IaC and GitOps

## Instructions

- 30 questions total
- 80% required to pass (24/30 correct)
- Multiple choice and scenario-based questions

---

## Section 1: Terraform (Questions 1-8)

**1. What is the purpose of `terraform.tfstate`?**

A) Store Terraform configuration
B) Track infrastructure resources and their current state
C) Define module dependencies
D) Configure provider settings

**Answer:** B

---

**2. Which meta-argument creates multiple similar resources?**

A) `depends_on`
B) `lifecycle`
C) `for_each`
D) `provider`

**Answer:** C

---

**3. How do you manage different environments in Terraform?**

A) Separate state files and variable files
B) Multiple providers
C) Different Terraform versions
D) Separate directories only

**Answer:** A

---

**4. What is the recommended way to store Terraform state for teams?**

A) Local filesystem
B) Git repository
C) Remote backend with locking (S3 + DynamoDB)
D) Email attachments

**Answer:** C

---

**5. Which command shows what Terraform will change?**

A) `terraform show`
B) `terraform plan`
C) `terraform validate`
D) `terraform apply`

**Answer:** B

---

**6. What does `terraform fmt` do?**

A) Formats output
B) Formats configuration files to canonical style
C) Formats state file
D) Formats plan output

**Answer:** B

---

**7. How do you pass secrets to Terraform safely?**

A) Hard-code in .tf files
B) Use environment variables or secret management systems
C) Store in Git
D) Use plain text files

**Answer:** B

---

**8. What is a Terraform module?**

A) A plugin
B) A reusable container for multiple resources
C) A single resource
D) A state file

**Answer:** B

---

## Section 2: GitOps (Questions 9-16)

**9. What is the core principle of GitOps?**

A) Manual deployments
B) Git as single source of truth for declarative infrastructure
C) Direct kubectl commands
D) SSH access to servers

**Answer:** B

---

**10. Which tool is NOT a GitOps operator?**

A) ArgoCD
B) FluxCD
C) Jenkins
D) GitOps Toolkit

**Answer:** C

---

**11. What does ArgoCD's sync policy "automated" do?**

A) Manually apply changes
B) Automatically sync Git changes to cluster
C) Delete all resources
D) Disable synchronization

**Answer:** B

---

**12. How does FluxCD detect changes in Git?**

A) Manual triggers only
B) Polling or webhooks
C) Email notifications
D) SSH connections

**Answer:** B

---

**13. What is the purpose of Kustomize?**

A) Replace Helm
B) Customize Kubernetes manifests without templates
C) Build Docker images
D) Manage databases

**Answer:** B

---

**14. In ArgoCD, what is an ApplicationSet?**

A) A single application
B) A way to generate multiple Applications from templates
C) A namespace
D) A deployment strategy

**Answer:** B

---

**15. What is a sync wave in ArgoCD?**

A) A deployment strategy
B) A way to control resource creation order
C) A type of notification
D) A backup mechanism

**Answer:** B

---

**16. Which is a benefit of GitOps?**

A) Requires manual intervention
B) Auditability and rollback capabilities
C) Increases complexity
D) Reduces security

**Answer:** B

---

## Section 3: Infrastructure Testing (Questions 17-22)

**17. What is Terratest?**

A) A Terraform linter
B) A Go library for testing infrastructure code
C) A Terraform formatter
D) A state management tool

**Answer:** B

---

**18. What does OPA stand for?**

A) Open Platform Architecture
B) Open Policy Agent
C) Operational Policy Automation
D) Optimized Performance Analysis

**Answer:** B

---

**19. What language does OPA use for policies?**

A) Python
B) Go
C) Rego
D) JavaScript

**Answer:** C

---

**20. What is Conftest used for?**

A) Running unit tests
B) Testing configuration files against policies
C) Load testing
D) Security scanning

**Answer:** B

---

**21. In the testing pyramid, where should most tests be?**

A) End-to-end tests
B) Integration tests
C) Unit tests
D) Manual tests

**Answer:** C

---

**22. What does `terraform validate` check?**

A) Security vulnerabilities
B) Syntax and internal consistency of configuration
C) Cost estimates
D) Performance

**Answer:** B

---

## Section 4: Secrets Management (Questions 23-28)

**23. Which is NOT a secure way to manage secrets?**

A) HashiCorp Vault
B) AWS Secrets Manager
C) Committing to Git
D) SOPS

**Answer:** C

---

**24. What does SOPS do?**

A) Manages servers
B) Encrypts files using KMS/PGP
C) Deploys applications
D) Monitors systems

**Answer:** B

---

**25. What is Sealed Secrets?**

A) A Vault alternative
B) A way to encrypt Kubernetes Secrets for Git storage
C) A database
D) A load balancer

**Answer:** B

---

**26. What does External Secrets Operator do?**

A) Exports secrets
B) Syncs secrets from external stores to Kubernetes
C) Deletes old secrets
D) Creates random passwords

**Answer:** B

---

**27. What is dynamic secret generation?**

A) Random passwords
B) Secrets generated on-demand with expiration
C) Encrypted secrets
D) Hardcoded values

**Answer:** B

---

**28. Which Vault auth method is best for Kubernetes?**

A) Username/password
B) Kubernetes auth
C) GitHub auth
D) LDAP

**Answer:** B

---

## Section 5: Scenarios (Questions 29-30)

**29. You need to deploy the same application to 10 different Kubernetes clusters. What should you use?**

A) Manual kubectl apply on each cluster
B) ArgoCD ApplicationSet with cluster generator
C) Copy-paste manifests
D) SSH scripts

**Answer:** B

---

**30. Your Terraform state file was accidentally deleted. What should you do?**

A) Recreate all infrastructure
B) Restore from remote backend backups
C) Manually edit state file
D) Ignore it

**Answer:** B

---

## Answer Key Summary

1. B  2. C  3. A  4. C  5. B
6. B  7. B  8. B  9. B  10. C
11. B  12. B  13. B  14. B  15. B
16. B  17. B  18. B  19. C  20. B
21. C  22. B  23. C  24. B  25. B
26. B  27. B  28. B  29. B  30. B

---

## Scoring

- 27-30 correct: Excellent (90-100%)
- 24-26 correct: Pass (80-86%)
- Below 24: Review material and retake

## Detailed Explanations

Each answer includes a brief explanation in the module lectures. Review the corresponding lecture notes for detailed information on any topics where you scored incorrectly.
