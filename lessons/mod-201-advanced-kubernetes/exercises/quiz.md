# Module 201: Advanced Kubernetes Quiz

## Instructions
- 25 questions covering all module topics
- Multiple choice and short answer
- Passing score: 80% (20/25 correct)
- Time limit: 90 minutes
- Open book (lecture notes allowed)

---

## Section 1: Operators and CRDs (Questions 1-4)

### Question 1
What is the primary purpose of a Kubernetes operator?

A) To automate application deployment only
B) To extend the Kubernetes API with custom resources
C) To encode human operational knowledge and automate application lifecycle management
D) To replace Kubernetes controllers

**Answer:** C

**Explanation:** Operators encode human operational knowledge as software to automate complex application management tasks including deployment, configuration, scaling, backup, and recovery.

---

### Question 2
Which of the following is NOT part of the reconciliation loop pattern?

A) Observe current state
B) Compare to desired state
C) Delete and recreate all resources
D) Take action to reconcile differences

**Answer:** C

**Explanation:** The reconciliation loop should be idempotent and update resources in place rather than deleting and recreating them. It observes current state, compares to desired state, and takes minimal actions to reconcile.

---

### Question 3
When should you use a finalizer in a Kubernetes operator?

A) To speed up resource deletion
B) To prevent resource deletion entirely
C) To perform cleanup of external resources before object deletion
D) To add metadata to resources

**Answer:** C

**Explanation:** Finalizers allow controllers to perform cleanup (like deleting external resources, cleaning up storage, etc.) before Kubernetes deletes the object. The controller must remove the finalizer once cleanup is complete.

---

### Question 4
What does `ctrl.SetControllerReference()` accomplish?

A) Sets the controller's API endpoint
B) Establishes owner references for garbage collection
C) Configures the controller's RBAC permissions
D) Links the controller to etcd

**Answer:** B

**Explanation:** `SetControllerReference` establishes owner references so that Kubernetes automatically garbage collects child resources when the owner is deleted.

---

## Section 2: Advanced Scheduling (Questions 5-9)

### Question 5
How does GPU time-slicing work in Kubernetes?

A) Multiple containers share GPU memory simultaneously
B) The device plugin makes each physical GPU appear as multiple logical GPUs
C) Pods take turns using the GPU at scheduled intervals
D) GPU memory is partitioned into fixed segments

**Answer:** B

**Explanation:** Time-slicing makes each physical GPU appear as multiple logical GPUs (replicas). The GPU driver time-slices processes, allowing GPU overcommitment.

---

### Question 6
What is the difference between node affinity and taints/tolerations?

A) They are the same feature with different names
B) Node affinity attracts pods to nodes; taints repel pods unless they have tolerations
C) Node affinity is deprecated in favor of taints
D) Taints are only for GPU nodes

**Answer:** B

**Explanation:** Node affinity is a pod property that attracts pods to certain nodes. Taints are node properties that repel pods unless the pods have matching tolerations. They solve complementary problems.

---

### Question 7
When creating priority classes for ML workloads, which statement is correct?

A) Higher value means lower priority
B) Priority classes cannot be used with GPU pods
C) A pod with higher priority can preempt lower priority pods
D) Priority classes only affect scheduling order, not preemption

**Answer:** C

**Explanation:** Priority classes with higher values have higher priority. High-priority pods can preempt (evict) lower-priority pods to make room on nodes.

---

### Question 8
What is gang scheduling and why is it important for distributed training?

A) It schedules pods in groups across multiple nodes
B) It ensures all pods in a job start together or none start (all-or-nothing)
C) It prioritizes pods based on their gang affiliation
D) It prevents pods from running on the same node

**Answer:** B

**Explanation:** Gang scheduling ensures all pods in a group (e.g., all workers in a distributed training job) can be scheduled together. Without it, partial scheduling can waste resources while waiting for remaining pods.

---

### Question 9
Which pod topology spread constraint field determines if violating the constraint is acceptable?

A) `maxSkew`
B) `topologyKey`
C) `whenUnsatisfiable`
D) `labelSelector`

**Answer:** C

**Explanation:** `whenUnsatisfiable` determines behavior when the constraint cannot be satisfied. `DoNotSchedule` makes it a hard requirement, while `ScheduleAnyway` makes it a soft preference.

---

## Section 3: StatefulSets and Storage (Questions 10-13)

### Question 10
What is the primary difference between a Deployment and a StatefulSet?

A) Deployments scale faster
B) StatefulSets provide stable network identities and persistent storage per pod
C) StatefulSets can only run one replica
D) Deployments are deprecated

**Answer:** B

**Explanation:** StatefulSets provide stable, unique network identities and persistent storage per pod through volumeClaimTemplates. Deployments have ephemeral identities and typically share or have no persistent storage.

---

### Question 11
How does CSI (Container Storage Interface) benefit Kubernetes storage?

A) It makes storage faster
B) It standardizes storage integration, allowing any storage system to work with Kubernetes
C) It replaces persistent volumes
D) It is only for cloud storage

**Answer:** B

**Explanation:** CSI is a standard that separates storage logic from Kubernetes core, allowing any storage system to integrate with Kubernetes through a standard interface.

---

### Question 12
When would you use a volume snapshot in an ML workflow?

A) To increase storage performance
B) To checkpoint model state, create experiment branches, or version datasets
C) To compress storage
D) To share volumes between pods

**Answer:** B

**Explanation:** Volume snapshots create point-in-time copies useful for checkpointing (save model state), branching experiments (try different hyperparameters from same checkpoint), and versioning datasets.

---

### Question 13
What is the purpose of `WaitForFirstConsumer` volume binding mode?

A) To create volumes immediately
B) To delay volume provisioning until a pod is scheduled, ensuring topology-aware placement
C) To wait for the first pod to finish before creating volumes
D) To prevent volume creation entirely

**Answer:** B

**Explanation:** `WaitForFirstConsumer` delays volume provisioning until a pod using the PVC is scheduled. This ensures the volume is created in the same availability zone as the pod, preventing cross-AZ data transfer.

---

## Section 4: Networking and Service Mesh (Questions 14-17)

### Question 14
What is the primary role of an Envoy sidecar proxy in Istio?

A) To replace the application container
B) To intercept and manage all inbound and outbound traffic for the pod
C) To store application logs
D) To provide storage for the application

**Answer:** B

**Explanation:** The Envoy sidecar intercepts all network traffic to/from the application container, enabling traffic management, security (mTLS), and observability without application code changes.

---

### Question 15
How does traffic mirroring (shadowing) help with model deployment?

A) It duplicates storage for redundancy
B) It sends copies of production traffic to a new model version for testing without affecting responses
C) It mirrors logs to multiple destinations
D) It creates backup pods

**Answer:** B

**Explanation:** Traffic mirroring sends a copy of live production traffic to a new model version (shadow traffic) for testing. The responses are discarded, so users only see responses from the production version.

---

### Question 16
In a service mesh, what is mTLS?

A) Multi-tenant TLS for shared resources
B) Mutual TLS where both client and server authenticate each other
C) Machine TLS for automated encryption
D) Mesh TLS specific to service meshes

**Answer:** B

**Explanation:** mTLS (Mutual TLS) is a security protocol where both client and server present certificates and authenticate each other, providing stronger security than one-way TLS.

---

### Question 17
What is the purpose of a circuit breaker in a service mesh?

A) To prevent electrical overloads
B) To stop cascading failures by temporarily blocking requests to unhealthy services
C) To route traffic in circles
D) To break network connections

**Answer:** B

**Explanation:** Circuit breakers detect when a service is unhealthy (high error rate, slow responses) and temporarily stop sending requests to it, preventing cascading failures and giving the service time to recover.

---

## Section 5: Security (Questions 18-21)

### Question 18
In Kubernetes RBAC, what is the correct order of specificity from least to most specific?

A) ClusterRole, Role, RoleBinding
B) Role, ClusterRole, ClusterRoleBinding
C) ClusterRole (cluster-wide) → ClusterRoleBinding → Role (namespace) → RoleBinding
D) All have equal specificity

**Answer:** C

**Explanation:** ClusterRole and ClusterRoleBinding are cluster-wide, while Role and RoleBinding are namespace-scoped. ClusterRoles are less specific (apply cluster-wide), Roles are more specific (apply to one namespace).

---

### Question 19
Which Pod Security Standard is most restrictive?

A) Privileged
B) Baseline
C) Restricted
D) Enforced

**Answer:** C

**Explanation:** The three Pod Security Standards are: Privileged (unrestricted), Baseline (minimally restrictive), and Restricted (heavily restricted, hardening best practices). Restricted is the most restrictive.

---

### Question 20
Why might GPU pods not comply with the "restricted" Pod Security Standard?

A) GPUs are inherently insecure
B) GPU access requires certain capabilities and device access that restricted policy blocks
C) GPU drivers prevent security policies
D) NVIDIA doesn't support security standards

**Answer:** B

**Explanation:** GPU access often requires capabilities like SYS_ADMIN, device access, and non-read-only root filesystem for driver interactions. These are blocked by the restricted security standard.

---

### Question 21
What is the purpose of Network Policies in Kubernetes?

A) To improve network performance
B) To act as firewall rules controlling traffic between pods
C) To configure DNS
D) To enable service mesh

**Answer:** B

**Explanation:** Network Policies act as firewall rules, controlling which pods can communicate with each other and with external endpoints. They provide micro-segmentation within the cluster.

---

## Section 6: Multi-Cluster and Autoscaling (Questions 22-25)

### Question 22
What is the primary benefit of KubeFed (Kubernetes Federation)?

A) It makes clusters faster
B) It enables centralized management and synchronization of resources across multiple clusters
C) It replaces individual cluster control planes
D) It provides storage replication

**Answer:** B

**Explanation:** KubeFed enables managing multiple Kubernetes clusters from a single control plane, synchronizing resources across clusters while allowing cluster-specific overrides.

---

### Question 23
What is the key difference between HPA (Horizontal Pod Autoscaler) and VPA (Vertical Pod Autoscaler)?

A) HPA is faster than VPA
B) HPA scales the number of pods; VPA adjusts resource requests/limits per pod
C) VPA is deprecated
D) They do the same thing

**Answer:** B

**Explanation:** HPA scales horizontally (adds/removes pod replicas), while VPA scales vertically (adjusts CPU/memory requests and limits for existing pods).

---

### Question 24
When should you use KEDA instead of standard HPA?

A) KEDA is always better
B) When you need event-driven scaling, scale-to-zero, or integration with external metrics sources like SQS queues
C) KEDA is only for GPU pods
D) When you want slower scaling

**Answer:** B

**Explanation:** KEDA excels at event-driven autoscaling based on external metrics (queue depth, Kafka lag, etc.) and supports scaling to zero when idle, which standard HPA doesn't support well.

---

### Question 25
In a multi-cluster active-active setup, which strategy helps ensure data consistency?

A) Never replicate data
B) Use eventual consistency with data replication and conflict resolution strategies
C) Only use one cluster at a time
D) Avoid stateful applications entirely

**Answer:** B

**Explanation:** Active-active multi-cluster setups typically use eventual consistency with data replication mechanisms (database replication, object storage replication) and conflict resolution strategies to handle concurrent updates.

---

## Scoring Guide

| Score | Result |
|-------|--------|
| 23-25 | Excellent - Master level understanding |
| 20-22 | Pass - Strong understanding |
| 17-19 | Pass - Good understanding with some gaps |
| Below 17 | Review material and retake |

---

## Answer Key Summary

1. C  |  2. C  |  3. C  |  4. B  |  5. B
6. B  |  7. C  |  8. B  |  9. C  | 10. B
11. B | 12. B | 13. B | 14. B | 15. B
16. B | 17. B | 18. C | 19. C | 20. B
21. B | 22. B | 23. B | 24. B | 25. B

---

## After the Quiz

If you scored below 80%:
1. Review the lecture notes for topics you struggled with
2. Re-read the relevant sections
3. Complete the hands-on labs for those topics
4. Retake the quiz

If you scored 80% or above:
1. Congratulations! You have strong understanding of advanced Kubernetes
2. Move on to hands-on labs to reinforce learning
3. Consider real-world projects to apply concepts
4. Prepare for Module 202: Distributed ML Training at Scale

---

**Good luck!**
