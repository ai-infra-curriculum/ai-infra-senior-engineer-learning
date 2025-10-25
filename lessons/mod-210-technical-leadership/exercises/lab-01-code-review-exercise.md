# Lab 1: Code Review Exercise

## Overview

Effective code review is one of the most important skills for a Senior AI Infrastructure Engineer. This lab provides realistic pull requests for you to review, helping you practice giving constructive, actionable feedback that improves code quality while maintaining team morale.

## Learning Objectives

By the end of this lab, you will be able to:
- Identify technical issues in AI infrastructure code
- Provide constructive, actionable feedback
- Balance nitpicking vs. significant issues
- Communicate feedback that teaches, not just critiques
- Practice empathy while maintaining quality standards

## Duration

3-4 hours

## Prerequisites

- Familiarity with Python and ML infrastructure
- Understanding of Kubernetes basics
- Completion of Module 210 Lecture 03 (Code Review Best Practices)

---

## Part 1: Code Review Fundamentals (15 minutes)

### The Three-Pass Review Method

**First Pass - High Level (5 minutes)**
- Does this change make sense?
- Is the approach sound?
- Are there architectural concerns?

**Second Pass - Logic & Quality (10-15 minutes)**
- Logic errors or bugs?
- Performance issues?
- Security vulnerabilities?
- Test coverage adequate?

**Third Pass - Style & Best Practices (5-10 minutes)**
- Code style and readability
- Documentation quality
- Naming conventions
- Minor improvements

---

## Part 2: Pull Request #1 - Model Serving Endpoint (45 minutes)

### Context

A mid-level engineer submitted this PR to add a new model serving endpoint. The team uses FastAPI for serving ML models, and the PR adds support for batch predictions.

### The Code

```python
# File: app/routes/batch_predict.py

from fastapi import APIRouter, HTTPException
from typing import List
import torch
import numpy as np

router = APIRouter()

model = torch.load("models/resnet50.pt")

@router.post("/batch-predict")
async def batch_predict(inputs: List[dict]):
    results = []
    for input in inputs:
        data = np.array(input['data'])
        output = model(torch.from_numpy(data))
        results.append(output.tolist())
    return {"predictions": results}

@router.get("/health")
def health():
    return "OK"
```

### Your Task

Review this code as if it were a real pull request. Provide feedback using this structure:

#### Critical Issues (Must Fix Before Merge)
1. **Issue**: _________________________________________
   **Why it matters**: _________________________________
   **Suggested fix**: __________________________________

2. **Issue**: _________________________________________
   **Why it matters**: _________________________________
   **Suggested fix**: __________________________________

#### Important Improvements (Should Fix)
1. **Observation**: ____________________________________
   **Impact**: ________________________________________
   **Recommendation**: _________________________________

#### Optional Suggestions (Nice to Have)
1. _________________________________________________

---

### Guided Analysis

<details>
<summary>Click to reveal issues after attempting the review</summary>

**Critical Issues:**

1. **Global model loading**
   - Why: Model loads once at module import; server restart required for model updates
   - Fix: Use dependency injection or lazy loading
   - Severity: Blocks deployment flexibility

2. **No error handling**
   - Why: Malformed input will crash the entire request
   - Fix: Add try-except blocks with proper error messages
   - Severity: Production reliability risk

3. **Blocking I/O in async endpoint**
   - Why: model() is synchronous, blocks event loop
   - Fix: Use run_in_executor or make endpoint synchronous
   - Severity: Performance degradation under load

4. **No input validation**
   - Why: Security risk, potential for injection or crashes
   - Fix: Use Pydantic models for request validation
   - Severity: Security and stability risk

**Important Improvements:**

1. **Inefficient batching**
   - Impact: Processes inputs one at a time, not leveraging batch inference
   - Recommendation: Batch all inputs together before model inference

2. **Missing monitoring/logging**
   - Impact: No visibility into errors or performance
   - Recommendation: Add structured logging and metrics

3. **Health check too simple**
   - Impact: Doesn't verify model is actually loaded/working
   - Recommendation: Add model verification to health check

**Optional Suggestions:**

1. Type hints for better IDE support (`inputs: List[BatchInput]`)
2. Add docstrings explaining endpoint behavior
3. Consider rate limiting for production use
4. Add request ID for tracing

</details>

---

## Part 3: Providing Constructive Feedback (30 minutes)

### Exercise: Rewrite Comments

Below are **poorly written** code review comments. Rewrite them to be constructive and helpful.

#### Bad Comment #1
> "This code is terrible. Did you even test this?"

**Your Rewrite**:
________________________________________________________________

________________________________________________________________

<details>
<summary>Example rewrite</summary>
"I'm concerned about error handling here. If the input data is malformed (e.g., wrong shape), this will throw an unhandled exception and crash the request. Could we add validation using Pydantic models? Something like:

```python
class BatchInput(BaseModel):
    data: List[List[float]]

    @validator('data')
    def validate_shape(cls, v):
        # Add shape validation
        return v
```

This would give users clear error messages and prevent crashes. What do you think?"
</details>

---

#### Bad Comment #2
> "Wrong. Use async properly."

**Your Rewrite**:
________________________________________________________________

________________________________________________________________

<details>
<summary>Example rewrite</summary>
"Good use of FastAPI's async capabilities! However, I notice the `model()` call is synchronous and will block the event loop. This could cause performance issues under load.

Two options:
1. Make the endpoint sync: `def batch_predict(...)` (simpler)
2. Use `run_in_executor` to run model inference in a thread pool (keeps endpoint async)

For ML serving, option 1 is usually fine since inference is the bottleneck anyway. Here's a resource on FastAPI concurrency: [link]"
</details>

---

#### Bad Comment #3
> "Needs refactoring."

**Your Rewrite**:
________________________________________________________________

________________________________________________________________

<details>
<summary>Example rewrite</summary>
"This works, but I see an opportunity to improve performance. Currently, we're processing inputs one-by-one:

```python
for input in inputs:  # Sequential processing
    output = model(...)
```

Since the model supports batch inference, we could process all inputs together:

```python
batch_data = torch.stack([torch.from_numpy(np.array(i['data'])) for i in inputs])
outputs = model(batch_data)  # Single batch call
```

This could be 10-50x faster depending on batch size. Worth a try?"
</details>

---

## Part 4: Pull Request #2 - GPU Scheduler (60 minutes)

### Context

A senior engineer submitted this Kubernetes controller code for GPU scheduling. This is more complex infrastructure code.

### The Code

```python
# File: controllers/gpu_scheduler.py

import kubernetes
from kubernetes import client, config

class GPUScheduler:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1API()
        self.nodes = []

    def schedule_job(self, job_spec):
        # Find node with available GPU
        for node in self.nodes:
            if node['gpu_available'] > 0:
                # Schedule job to this node
                pod = self.create_pod(job_spec, node['name'])
                self.v1.create_namespaced_pod(
                    namespace="default",
                    body=pod
                )
                node['gpu_available'] -= job_spec['gpu_required']
                return True
        return False

    def create_pod(self, job_spec, node_name):
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": job_spec['name']},
            "spec": {
                "nodeName": node_name,
                "containers": [{
                    "name": "training",
                    "image": job_spec['image'],
                    "resources": {
                        "limits": {
                            "nvidia.com/gpu": job_spec['gpu_required']
                        }
                    }
                }]
            }
        }

    def update_node_status(self):
        nodes = self.v1.list_node()
        self.nodes = []
        for node in nodes.items:
            gpu_capacity = int(node.status.allocatable.get('nvidia.com/gpu', 0))
            self.nodes.append({
                'name': node.metadata.name,
                'gpu_available': gpu_capacity
            })
```

### Your Task

This is a more complex review. Consider:
1. **Correctness**: Does this logic work?
2. **Production Readiness**: What's missing for production?
3. **Best Practices**: Kubernetes controller patterns
4. **Error Handling**: What could go wrong?

Provide a structured review covering:

#### Architecture/Design Feedback
________________________________________________________________

________________________________________________________________

________________________________________________________________

#### Critical Bugs or Logic Errors
________________________________________________________________

________________________________________________________________

________________________________________________________________

#### Production Readiness Concerns
________________________________________________________________

________________________________________________________________

________________________________________________________________

#### Code Quality Improvements
________________________________________________________________

________________________________________________________________

________________________________________________________________

---

### Detailed Analysis

<details>
<summary>Click after completing your review</summary>

**Architecture/Design Issues:**

1. **Race Conditions**
   - `gpu_available` is local state, not synced with actual cluster
   - Two schedulers could double-book GPUs
   - Fix: Use Kubernetes resource tracking, not local state

2. **No Reconciliation Loop**
   - Doesn't watch for pod completions to free GPUs
   - Manual `update_node_status()` calls won't catch real-time changes
   - Fix: Implement watch/informer pattern

3. **Hardcoded Namespace**
   - Only works in `default` namespace
   - Fix: Make namespace configurable

**Critical Bugs:**

1. **GPU Count Never Updates**
   - `gpu_available` decrements locally but cluster state unchanged
   - Next `update_node_status()` call resets counts
   - Fix: Track allocated vs available properly

2. **No Error Handling**
   - `create_namespaced_pod()` can fail (name conflicts, quota exceeded, etc.)
   - No rollback if pod creation fails after decrementing GPU count
   - Fix: Wrap in try-except, implement retry logic

3. **Missing Pod Status Tracking**
   - No way to know if pod actually started or got GPU
   - Fix: Watch pod status, handle failures

**Production Readiness:**

1. **No Logging/Monitoring**
   - Can't debug scheduling failures
   - Add: Structured logging, metrics (schedule success/failure rates)

2. **No High Availability**
   - Single scheduler instance, single point of failure
   - Add: Leader election for multiple replicas

3. **No Resource Limits**
   - Could schedule unlimited jobs
   - Add: Queue management, priorities, fair sharing

**Code Quality:**

1. Use `dataclasses` or `Pydantic` for job_spec validation
2. Add type hints
3. Extract magic strings to constants
4. Add docstrings
5. Unit tests for scheduling logic

**Better Approach:**
Consider using existing Kubernetes scheduling primitives (node selectors, affinities, custom scheduler) rather than reimplementing scheduling.

</details>

---

## Part 5: Empathy in Code Review (30 minutes)

### Scenario-Based Practice

For each scenario, write what you would say in the code review:

#### Scenario 1: Junior Engineer's First PR
A junior engineer submitted their first significant PR. It has several issues but shows good effort. The code works but isn't optimal.

**Your Feedback Approach**:
________________________________________________________________

________________________________________________________________

________________________________________________________________

<details>
<summary>Example approach</summary>
"Great work on your first significant PR! I can see you put a lot of thought into this. The core logic is solid and it works - that's the important part!

I have a few suggestions that will make this even better:

1. [Most important issue] - Here's why this matters and how to fix it
2. [Secondary issue] - This is more about style/best practices

Don't feel like you need to fix everything at once. Let's prioritize #1, and we can iterate on the rest. Happy to pair with you if helpful!"
</details>

---

#### Scenario 2: Disagreement on Approach
An experienced engineer used a different pattern than you would have. Their approach works but you believe yours is better.

**Your Feedback Approach**:
________________________________________________________________

________________________________________________________________

________________________________________________________________

<details>
<summary>Example approach</summary>
"This approach works well! I'm curious about your thinking here. I've usually seen this done with [alternative approach] because [reason], but I can see benefits to your way too, especially [specific benefit].

Have you considered [specific concern]? If that's not an issue in our case, I'm comfortable with either approach. What do you think?"

[Only push back if there's a concrete technical concern, not just preference]
</details>

---

#### Scenario 3: Urgent Hotfix
A critical production bug needs fixing NOW. The submitted hotfix works but isn't clean code.

**Your Feedback Approach**:
________________________________________________________________

________________________________________________________________

________________________________________________________________

<details>
<summary>Example approach</summary>
"✅ Approved - This fixes the production issue, which is the priority.

For follow-up (separate PR, no rush):
- [Code quality issue] - Let's clean this up when we have time
- [Test case] - Add a regression test so this doesn't happen again

Great job getting this out quickly to unblock users!"

[Separate urgent fixes from quality improvements]
</details>

---

## Part 6: Self-Review Checklist (15 minutes)

Before submitting code reviews, ask yourself:

### Technical Quality
- [ ] Did I understand what the code is trying to accomplish?
- [ ] Did I identify actual bugs vs. style preferences?
- [ ] Did I check for security vulnerabilities?
- [ ] Did I consider performance implications?
- [ ] Did I verify test coverage?

### Communication
- [ ] Is my feedback specific and actionable?
- [ ] Did I explain *why*, not just *what*?
- [ ] Did I provide examples or suggest solutions?
- [ ] Is my tone constructive and respectful?
- [ ] Did I acknowledge what was done well?

### Balance
- [ ] Did I distinguish blocking issues from nice-to-haves?
- [ ] Am I being consistent with past feedback?
- [ ] Am I nitpicking or focusing on important issues?
- [ ] Did I consider the context (urgency, author experience, etc.)?

---

## Part 7: Real-World Practice (45 minutes)

### Find a Real PR to Review

Options:
1. Review a teammate's PR using these techniques
2. Review an open-source project PR
3. Review your own past PRs critically

Apply the three-pass method and write comprehensive feedback.

### Reflection Questions

After your review:
1. What was the most significant issue you found?
2. How did you balance being thorough vs. being timely?
3. What feedback did you struggle to articulate?
4. If you were the PR author, how would you feel about your feedback?

---

## Resources

### Code Review Tools
- [GitHub PR review features](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)
- [Gerrit Code Review](https://www.gerritcodereview.com/)
- [Phabricator Differential](https://www.phacility.com/phabricator/differential/)

### Reading List
- [Google's Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [How to Do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-1/)
- [The Art of Giving and Receiving Code Reviews](https://www.alexandra-hill.com/2018/06/25/the-art-of-giving-and-receiving-code-reviews/)

### Example Review Comments
- [Kubernetes PR reviews](https://github.com/kubernetes/kubernetes/pulls)
- [PyTorch PR reviews](https://github.com/pytorch/pytorch/pulls)

---

## Submission

Submit the following:
1. Your review of PR #1 (Model Serving Endpoint)
2. Your review of PR #2 (GPU Scheduler)
3. Your rewritten comments from Part 3
4. Reflection on your real-world practice review

---

## Common Pitfalls to Avoid

1. **Being vague**: "This needs work" → "The error handling on line 42 should catch ValueError"
2. **Only criticizing**: Balance criticism with praise for good parts
3. **Bikeshedding**: Don't spend time on trivial issues when major problems exist
4. **Being passive-aggressive**: "Did you even test this?" → "Let's add a test for edge case X"
5. **Blocking on preferences**: Use "nit:" prefix for non-blocking style suggestions
6. **Reviewing too fast**: Take time for thorough reviews
7. **Reviewing too slow**: Unblock teammates promptly
8. **Not providing alternatives**: If you critique, suggest solutions

---

## Extension Activities

1. **Code Review Simulation**: Pair with a colleague. Each write intentionally flawed code for the other to review, then discuss the feedback.

2. **Review Metrics**: Track your code reviews for a week:
   - How many? How long each?
   - Bugs found in review vs. production
   - Teammate satisfaction with your feedback

3. **Review Templates**: Create your own checklist for reviewing ML infrastructure code specifically.

---

## Next Steps

- Apply these techniques in your next code review
- Share this framework with your team
- Complete Lab 2: Architecture Decision Record Writing
- Schedule peer code review session with your team
