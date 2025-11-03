# Lecture 3: Code Review Best Practices

## Learning Objectives

By the end of this lecture, you will be able to:

- Design collaborative code review processes delivering 10-20x ROI through defect reduction knowledge transfer team cohesion measuring impact systematically
- Apply comprehensive review checklists evaluating correctness design complexity testing performance security operations systematically prioritizing by change characteristics
- Provide effective feedback using FIRE framework specifying facts impacts recommendations examples categorizing severity as blocking important suggestion question
- Receive feedback gracefully detaching ego embracing growth responding thoughtfully to agree clarify disagree defer handling criticism constructively
- Review ML infrastructure code checking GPU memory management distributed training synchronization model serving validation performance robustness operational readiness
- Implement code review automation configuring pre-commit hooks CI pipelines static analysis formatting security scanning freeing reviewers for design logic
- Avoid review anti-patterns preventing nitpicking design debates rewrite suggestions fake approvals ghosting focusing on substance over style
- Establish review culture using pull request templates setting response time expectations building team capability through consistent quality collaboration practices

## Table of Contents
1. [Why Code Reviews Matter](#why-code-reviews-matter)
2. [The Code Review Mindset](#the-code-review-mindset)
3. [What to Look For in Reviews](#what-to-look-for-in-reviews)
4. [Giving Effective Feedback](#giving-effective-feedback)
5. [Receiving Feedback Gracefully](#receiving-feedback-gracefully)
6. [ML Infrastructure-Specific Reviews](#ml-infrastructure-specific-reviews)
7. [Code Review Anti-Patterns](#code-review-anti-patterns)
8. [Tools and Automation](#tools-and-automation)

## Why Code Reviews Matter

Code reviews are one of the highest-leverage activities for senior engineers. They're not just about finding bugs—they're about knowledge sharing, maintaining quality, and building team culture.

### The Multi-Dimensional Value

```python
class CodeReviewValue:
    """The many benefits of code reviews"""

    def __init__(self):
        self.benefits = {
            'quality': [
                'Catch bugs before production',
                'Ensure code meets standards',
                'Identify edge cases and error handling',
                'Verify test coverage'
            ],
            'knowledge_sharing': [
                'Spread domain knowledge across team',
                'Learn new patterns and techniques',
                'Understand different parts of codebase',
                'Cross-pollinate best practices'
            ],
            'team_building': [
                'Create shared understanding',
                'Build trust through collaboration',
                'Develop communication skills',
                'Onboard new team members'
            ],
            'risk_mitigation': [
                'Reduce bus factor (knowledge silos)',
                'Catch security vulnerabilities',
                'Ensure performance requirements met',
                'Verify operational readiness'
            ]
        }

    def calculate_roi(self, time_spent_hours: float) -> dict:
        """Code reviews have 10-20x ROI"""
        bug_cost_hours = 5  # Average hours to fix production bug
        bugs_prevented = time_spent_hours * 2  # Conservative estimate

        return {
            'time_invested': time_spent_hours,
            'bugs_prevented': bugs_prevented,
            'time_saved': bugs_prevented * bug_cost_hours,
            'roi_multiple': (bugs_prevented * bug_cost_hours) / time_spent_hours
        }

# Example: 1 hour of code review
review = CodeReviewValue()
roi = review.calculate_roi(1.0)
print(f"1 hour review → Prevents {roi['bugs_prevented']} bugs → "
      f"Saves {roi['time_saved']} hours → {roi['roi_multiple']}x ROI")
# Output: 1 hour review → Prevents 2 bugs → Saves 10 hours → 10x ROI
```

### Research-Backed Benefits

- **Defect Reduction**: 60-90% of defects found before production (Microsoft Research)
- **Knowledge Transfer**: 3x faster onboarding with regular code reviews
- **Code Quality**: 40% reduction in code complexity over time
- **Team Cohesion**: Teams that review code together have 25% higher satisfaction

## The Code Review Mindset

### Reviewer Mindset: Collaborate, Don't Critique

**Core Principles**:

```python
class ReviewerMindset:
    """The ideal mindset for reviewing code"""

    def __init__(self):
        self.principles = {
            'collaborative': {
                'attitude': 'We are partners in quality',
                'goal': 'Help the author succeed',
                'approach': 'Ask questions, suggest improvements'
            },
            'humble': {
                'attitude': 'I might be wrong or missing context',
                'goal': 'Learn from the author',
                'approach': 'Use "we" instead of "you", frame as suggestions'
            },
            'pragmatic': {
                'attitude': 'Perfect is the enemy of good',
                'goal': 'Ship quality code on time',
                'approach': 'Distinguish blocking issues from nice-to-haves'
            },
            'educational': {
                'attitude': 'Reviews are teaching opportunities',
                'goal': 'Raise overall team capability',
                'approach': 'Explain the "why" behind suggestions'
            }
        }

    def format_comment(self, issue: str, severity: str) -> str:
        """Format feedback appropriately by severity"""

        templates = {
            'blocking': f"⛔ BLOCKING: {issue}",
            'important': f"⚠️  IMPORTANT: {issue}",
            'suggestion': f"💡 Suggestion: {issue}",
            'question': f"❓ Question: {issue}",
            'praise': f"✨ Nice: {issue}"
        }

        return templates.get(severity, issue)

# Example usage
reviewer = ReviewerMindset()
print(reviewer.format_comment(
    "This could cause a race condition with concurrent requests",
    "blocking"
))
# Output: ⛔ BLOCKING: This could cause a race condition...
```

### Author Mindset: Embrace Feedback

**Core Principles**:
- **Ego Detachment**: Code is not you; feedback on code ≠ feedback on you
- **Growth Orientation**: Every review is a learning opportunity
- **Appreciation**: Reviewers are investing their time to help you
- **Responsiveness**: Address feedback promptly and thoughtfully

```python
def respond_to_feedback(comment: dict) -> str:
    """How to respond to review feedback"""

    responses = {
        'agree': """
            Great catch! Fixed in commit abc123.

            I've also added a test case to prevent this in the future.
        """,

        'clarify': """
            Good question! Here's the context:
            - [Explanation of reasoning]
            - [Trade-offs considered]

            Does that make sense, or should we discuss further?
        """,

        'disagree_respectfully': """
            I see your point about [concern]. I chose this approach because:
            - [Reason 1]
            - [Reason 2]

            However, I'm open to alternatives. What do you think about [compromise]?
        """,

        'defer': """
            This is a good improvement, but it's out of scope for this PR.

            I've created ticket #123 to track this enhancement.
            Is that acceptable, or should we address it now?
        """
    }

    return responses.get(comment['type'], "Let me think about this...")
```

## What to Look For in Reviews

### The Review Checklist

Use a mental checklist, but don't be rigid. Adapt based on the change.

```python
from enum import Enum
from typing import List, Dict

class ReviewCategory(Enum):
    CORRECTNESS = "Does the code do what it's supposed to?"
    DESIGN = "Is this the right approach?"
    COMPLEXITY = "Is the code understandable?"
    TESTING = "Is it adequately tested?"
    PERFORMANCE = "Will it scale?"
    SECURITY = "Are there vulnerabilities?"
    OPERATIONS = "Can we run and monitor this?"
    STYLE = "Does it follow conventions?"

class CodeReviewChecklist:
    """Comprehensive review checklist"""

    def __init__(self):
        self.categories = {
            ReviewCategory.CORRECTNESS: [
                "Does the code handle all edge cases?",
                "Is error handling complete?",
                "Are all code paths tested?",
                "Does it handle null/None values?",
                "Are there off-by-one errors?",
                "Does it handle empty lists/dicts?"
            ],

            ReviewCategory.DESIGN: [
                "Is this the right abstraction?",
                "Does it follow SOLID principles?",
                "Is there proper separation of concerns?",
                "Are dependencies injected (not hard-coded)?",
                "Is the interface intuitive?",
                "Will this scale with requirements changes?"
            ],

            ReviewCategory.COMPLEXITY: [
                "Can I understand this in 2 minutes?",
                "Are functions <50 lines?",
                "Is nesting depth <3 levels?",
                "Are variable names descriptive?",
                "Is there clear documentation?",
                "Could this be simplified?"
            ],

            ReviewCategory.TESTING: [
                "Are there unit tests for new code?",
                "Are edge cases tested?",
                "Are errors tested?",
                "Are integration tests needed?",
                "Is test coverage >80%?",
                "Are tests clear and maintainable?"
            ],

            ReviewCategory.PERFORMANCE: [
                "Are there O(n²) or worse algorithms?",
                "Is there unnecessary database querying?",
                "Are large objects copied unnecessarily?",
                "Is caching used appropriately?",
                "Will this cause memory leaks?",
                "Are there performance benchmarks?"
            ],

            ReviewCategory.SECURITY: [
                "Is user input validated?",
                "Is SQL injection prevented?",
                "Are secrets hard-coded?",
                "Is authentication/authorization correct?",
                "Are sensitive data logged?",
                "Is data encrypted at rest/in transit?"
            ],

            ReviewCategory.OPERATIONS: [
                "Are there appropriate logs?",
                "Are errors handled and reported?",
                "Are there monitoring metrics?",
                "Is configuration externalized?",
                "Can this be deployed safely?",
                "Is there a rollback plan?"
            ],

            ReviewCategory.STYLE: [
                "Does it follow team conventions?",
                "Is formatting consistent?",
                "Are there type hints (Python)?",
                "Is documentation complete?",
                "Are commit messages clear?",
                "Is the PR description helpful?"
            ]
        }

    def prioritize_for_change(self, change_size: str,
                             change_type: str) -> List[ReviewCategory]:
        """Focus review based on change characteristics"""

        if change_size == "small":
            # Focus on correctness and testing
            return [ReviewCategory.CORRECTNESS, ReviewCategory.TESTING]

        elif change_type == "new_feature":
            # Focus on design and testing
            return [
                ReviewCategory.DESIGN,
                ReviewCategory.CORRECTNESS,
                ReviewCategory.TESTING,
                ReviewCategory.OPERATIONS
            ]

        elif change_type == "refactoring":
            # Focus on design and complexity
            return [
                ReviewCategory.DESIGN,
                ReviewCategory.COMPLEXITY,
                ReviewCategory.TESTING
            ]

        elif change_type == "hotfix":
            # Focus on correctness and operations
            return [
                ReviewCategory.CORRECTNESS,
                ReviewCategory.TESTING,
                ReviewCategory.OPERATIONS
            ]

        else:
            # Review everything for large/complex changes
            return list(ReviewCategory)

# Example usage
checklist = CodeReviewChecklist()
priorities = checklist.prioritize_for_change("large", "new_feature")
print(f"Focus areas: {[p.value for p in priorities]}")
```

### The Two-Pass Review Strategy

**First Pass (5-10 minutes)**: High-level understanding
```markdown
Questions to answer:
1. What is this PR trying to achieve?
2. Is the approach reasonable?
3. Is the scope appropriate?
4. Are there major design issues?
5. Should we discuss synchronously?
```

**Second Pass (15-30 minutes)**: Detailed review
```markdown
Activities:
1. Read the code carefully
2. Check against checklist
3. Identify specific issues
4. Verify tests
5. Consider edge cases
6. Write constructive feedback
```

## Giving Effective Feedback

### The Feedback Framework

```python
class FeedbackFramework:
    """Structure for effective code review feedback"""

    def give_feedback(self, issue: dict) -> str:
        """
        Use the FIRE framework:
        - Fact: What you observed
        - Impact: Why it matters
        - Recommendation: What to do
        - Example: Show how (if helpful)
        """

        template = f"""
        **Issue**: {issue['fact']}

        **Impact**: {issue['impact']}

        **Recommendation**: {issue['recommendation']}

        {f"**Example**: ```python\n{issue['example']}\n```" if issue.get('example') else ''}
        """

        return template.strip()

# Example: Providing actionable feedback
feedback = FeedbackFramework()

issue = {
    'fact': 'This function makes a database query inside a loop',
    'impact': 'This will cause N+1 queries and slow down as data grows',
    'recommendation': 'Batch the queries or use a JOIN',
    'example': '''
# Instead of:
for user_id in user_ids:
    user = db.query(User).filter_by(id=user_id).first()

# Do:
users = db.query(User).filter(User.id.in_(user_ids)).all()
user_map = {user.id: user for user in users}
'''
}

print(feedback.give_feedback(issue))
```

### Feedback Tone Examples

**❌ Harsh/Judgmental**:
> "This is wrong. You should know better than to query in a loop."

**✅ Collaborative/Educational**:
> "💡 Suggestion: This creates N+1 queries which could slow down with many users. We could batch these into a single query using `filter().in_()`. Would you like me to show an example?"

---

**❌ Vague**:
> "This seems complicated."

**✅ Specific**:
> "⚠️ IMPORTANT: This function has 3 levels of nesting and does both data fetching and business logic. Could we split it into `fetch_training_data()` and `validate_training_params()` to improve readability?"

---

**❌ Dictating**:
> "Change this to use async/await."

**✅ Suggesting**:
> "❓ Question: Have you considered using async/await here? Since we're making multiple API calls, parallelizing them could reduce latency from ~500ms to ~100ms. What do you think?"

### Categorizing Feedback

```python
from enum import Enum

class FeedbackSeverity(Enum):
    BLOCKING = "must_fix"      # Security issues, bugs, major design flaws
    IMPORTANT = "should_fix"   # Performance issues, complexity, missing tests
    SUGGESTION = "nice_to_fix" # Style improvements, alternative approaches
    QUESTION = "clarify"       # Understand reasoning, missing context
    PRAISE = "good_work"       # Positive feedback, learning moments

def categorize_comment(comment: str, severity: FeedbackSeverity) -> str:
    """Add clear severity markers"""

    markers = {
        FeedbackSeverity.BLOCKING: "⛔ BLOCKING",
        FeedbackSeverity.IMPORTANT: "⚠️  IMPORTANT",
        FeedbackSeverity.SUGGESTION: "💡 Suggestion",
        FeedbackSeverity.QUESTION: "❓ Question",
        FeedbackSeverity.PRAISE: "✨ Nice work"
    }

    marker = markers[severity]
    return f"{marker}: {comment}"

# Examples
print(categorize_comment(
    "This doesn't handle GPU OOM errors, which will crash the training job",
    FeedbackSeverity.BLOCKING
))

print(categorize_comment(
    "I really like how you used context managers to ensure cleanup!",
    FeedbackSeverity.PRAISE
))
```

### The Praise-to-Critique Ratio

Aim for at least 1:1, ideally 2:1 or 3:1.

**Why It Matters**:
- Reinforces good patterns
- Builds psychological safety
- Makes critical feedback easier to hear
- Keeps the author motivated

**Examples of Good Praise**:
```python
examples = [
    "✨ Great use of type hints throughout - makes this very readable!",

    "✨ I love the comprehensive error handling here. The exception messages "
    "will make debugging much easier.",

    "✨ This test case is excellent - I hadn't thought about the edge case "
    "where training finishes between heartbeats.",

    "✨ Nice documentation! The docstring examples make it clear how to use this."
]
```

## Receiving Feedback Gracefully

### The Author's Response Framework

```python
class ResponseStrategy:
    """How to respond to different types of feedback"""

    def respond(self, feedback: dict) -> str:
        """Craft appropriate response"""

        if feedback['type'] == 'valid_issue':
            return self.acknowledge_and_fix(feedback)

        elif feedback['type'] == 'needs_clarification':
            return self.explain_with_context(feedback)

        elif feedback['type'] == 'disagree':
            return self.disagree_respectfully(feedback)

        elif feedback['type'] == 'out_of_scope':
            return self.defer_with_ticket(feedback)

    def acknowledge_and_fix(self, feedback: dict) -> str:
        return f"""
        Great catch! I've fixed this in {feedback['commit_hash']}.

        I also added {feedback['improvement']} to prevent this in the future.

        Thanks for catching this! 🙏
        """

    def explain_with_context(self, feedback: dict) -> str:
        return f"""
        Good question! Here's the context I'm working with:

        {feedback['context']}

        Given these constraints, I chose {feedback['choice']} because:
        - {feedback['reason_1']}
        - {feedback['reason_2']}

        Does that make sense, or should we discuss alternatives?
        """

    def disagree_respectfully(self, feedback: dict) -> str:
        return f"""
        I understand your concern about {feedback['concern']}.

        I've considered {feedback['alternative']}, but chose the current
        approach because:
        - {feedback['tradeoff_1']}
        - {feedback['tradeoff_2']}

        However, I'm definitely open to discussion! What if we:
        - {feedback['compromise']}

        Would that address your concerns?
        """

    def defer_with_ticket(self, feedback: dict) -> str:
        return f"""
        This is a valuable improvement! However, it's outside the scope of
        this PR, which is focused on {feedback['pr_scope']}.

        I've created {feedback['ticket_link']} to track this enhancement.

        We can prioritize it in the next sprint. Does that work for you?
        """
```

### Red Flags: When to Pushback

Sometimes feedback is wrong. Here's how to handle it professionally:

```markdown
## When to Pushback (Respectfully)

### ❌ Scope Creep
**Feedback**: "While you're here, can you also refactor module X?"
**Response**: "That's a good idea! It's outside this PR's scope, but I've created
ticket #456 to track it. Can we address it separately?"

### ❌ Personal Preference (No Real Benefit)
**Feedback**: "I prefer using `map()` instead of list comprehensions"
**Response**: "Both approaches work well here. Our style guide allows list
comprehensions, and the team seems comfortable with them. Is there a specific
issue with the current approach?"

### ❌ Misunderstanding the Problem
**Feedback**: "Why don't we just cache this?"
**Response**: "Good thought! The challenge is [specific constraint]. Because of
this, caching would [specific problem]. Does that clarify the situation?"

### ❌ Over-engineering
**Feedback**: "We should make this extensible for 10 different model types"
**Response**: "That's great forward thinking! Currently we only support 2 types,
and YAGNI suggests we wait until we have the 3rd use case. Shall we revisit
when we add more model types?"
```

## ML Infrastructure-Specific Reviews

### GPU and Distributed Training Code

```python
class MLInfrastructureReview:
    """Specific considerations for ML infrastructure"""

    def review_training_code(self, code: str) -> List[str]:
        """Check distributed training code"""

        checklist = [
            # GPU Management
            "✓ Is GPU memory managed properly (clear cache, del tensors)?",
            "✓ Are gradients accumulated correctly with gradient accumulation?",
            "✓ Is mixed precision (AMP) used correctly?",
            "✓ Are CUDA events synchronized appropriately?",

            # Distributed Training
            "✓ Is the distributed backend initialized correctly?",
            "✓ Are random seeds set for reproducibility?",
            "✓ Is data partitioned correctly across workers?",
            "✓ Are gradients synchronized properly (all_reduce)?",
            "✓ Is barrier() used before checkpointing?",

            # Performance
            "✓ Is data loading non-blocking (pin_memory, num_workers)?",
            "✓ Are operations vectorized (avoid Python loops)?",
            "✓ Is unnecessary CPU-GPU transfer minimized?",
            "✓ Is gradient checkpointing used for large models?",

            # Robustness
            "✓ Does it handle GPU OOM gracefully?",
            "✓ Are checkpoints saved atomically?",
            "✓ Can training resume from checkpoint?",
            "✓ Are metrics logged for debugging?"
        ]

        return checklist

# Example: Reviewing GPU memory management
review_comment = """
⚠️ IMPORTANT: GPU Memory Issue

**Issue**: The model tensors aren't moved to GPU before training, and there's
no OOM handling.

**Impact**: This will either fail immediately or cause silent CPU training
(100x slower).

**Recommendation**:
```python
# Add at initialization:
model = model.to(device)
optimizer = torch.optim.Adam(model.parameters())

# Add OOM handling in training loop:
try:
    loss = model(batch)
    loss.backward()
except RuntimeError as e:
    if "out of memory" in str(e):
        torch.cuda.empty_cache()
        logger.error(f"OOM at batch {batch_idx}, skipping")
    else:
        raise
```

**Testing**: Can you add a test with a deliberately large batch to verify OOM
handling works?
"""
```

### Model Serving Code

```python
def review_serving_code() -> List[str]:
    """Checklist for model serving code"""

    return [
        # Correctness
        "✓ Is input validation complete (shape, dtype, range)?",
        "✓ Is preprocessing identical to training?",
        "✓ Are model outputs post-processed correctly?",
        "✓ Is versioning handled (model version in response)?",

        # Performance
        "✓ Is batching used for throughput?",
        "✓ Is caching used for duplicate requests?",
        "✓ Are inference optimizations applied (TensorRT, ONNX)?",
        "✓ Is GPU utilization monitored?",

        # Reliability
        "✓ Are timeouts set (prevent hung requests)?",
        "✓ Is graceful degradation implemented?",
        "✓ Is model loading atomic (no partial loads)?",
        "✓ Are health checks comprehensive?",

        # Operations
        "✓ Are predictions logged for debugging?",
        "✓ Are latency metrics tracked (p50, p95, p99)?",
        "✓ Is model swapping supported (A/B testing)?",
        "✓ Are errors categorized (client vs server)?"
    ]

# Example: Reviewing input validation
validation_comment = """
⛔ BLOCKING: Missing Input Validation

**Issue**: The model serving endpoint doesn't validate input shape or dtype.

**Impact**: Invalid inputs will cause cryptic tensor errors instead of
returning clear HTTP 400 responses. This makes debugging very difficult for
API consumers.

**Recommendation**:
```python
from pydantic import BaseModel, validator
from typing import List

class PredictionRequest(BaseModel):
    features: List[float]

    @validator('features')
    def validate_features(cls, v):
        if len(v) != 128:
            raise ValueError(f'Expected 128 features, got {len(v)}')
        if not all(-10 <= x <= 10 for x in v):
            raise ValueError('Feature values must be in range [-10, 10]')
        return v

@app.post("/predict")
async def predict(request: PredictionRequest):
    # Pydantic validates automatically
    prediction = model.predict(request.features)
    return {"prediction": prediction}
```

This provides clear error messages and HTTP 422 status codes.
"""
```

### Infrastructure as Code (Terraform/K8s)

```python
def review_iac_code() -> dict:
    """Checklist for infrastructure code"""

    return {
        'terraform': [
            "✓ Are resource names descriptive and follow convention?",
            "✓ Is state stored remotely (S3, GCS)?",
            "✓ Are secrets managed properly (not in code)?",
            "✓ Are tags applied for cost tracking?",
            "✓ Is terraform fmt applied?",
            "✓ Does terraform plan show expected changes?",
            "✓ Are outputs documented?",
            "✓ Is there a README explaining the module?"
        ],

        'kubernetes': [
            "✓ Are resource requests/limits set appropriately?",
            "✓ Are health checks (liveness/readiness) defined?",
            "✓ Are secrets stored in Kubernetes Secrets (not ConfigMaps)?",
            "✓ Are labels and annotations comprehensive?",
            "✓ Is the deployment strategy appropriate (RollingUpdate)?",
            "✓ Are PodDisruptionBudgets set for HA?",
            "✓ Are resource quotas considered?",
            "✓ Is RBAC configured correctly?"
        ]
    }

# Example: Kubernetes review comment
k8s_comment = """
⚠️ IMPORTANT: Missing Resource Limits

**Issue**: The training job Pod doesn't specify resource limits.

**Impact**:
1. Training jobs could consume all node resources
2. OOM killer could terminate other Pods
3. Cluster autoscaling won't work correctly

**Recommendation**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training
spec:
  template:
    spec:
      containers:
      - name: trainer
        image: trainer:latest
        resources:
          requests:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: "2"
          limits:
            memory: "32Gi"  # Set equal to request for GPU workloads
            cpu: "8"
            nvidia.com/gpu: "2"
```

**Reference**: GPU workloads should have requests == limits to ensure
guaranteed QoS class.
"""
```

## Code Review Anti-Patterns

### Anti-Pattern 1: Nitpicking Style

**Problem**: Focusing on formatting instead of logic.

**Example**:
```python
# ❌ BAD: Nitpicking that could be automated
"Please add a space after the comma"
"Use single quotes instead of double quotes"
"Add a blank line here"

# ✅ GOOD: Use automated tools
# Add to CI:
black .          # Auto-format
flake8 .         # Style checking
mypy .           # Type checking

# Only comment on style if it affects readability:
"💡 Suggestion: This 200-character line is hard to read. Could we break it
into multiple lines?"
```

**Solution**: Automate style checks in CI. Focus reviews on substance.

### Anti-Pattern 2: Design Debates in Comments

**Problem**: Long back-and-forth discussions in PR comments.

**Solution**: Move to synchronous discussion.

```python
# After 3 rounds of comments:
"
❓ This is getting complex to discuss asynchronously. Can we hop on a
15-minute call to discuss the design trade-offs? I'm free today at 2pm or 3pm.

In the meantime, I'll start writing an ADR to document our options:
[Link to ADR draft]
"
```

### Anti-Pattern 3: The "Rewrite Everything" Review

**Problem**: Suggesting fundamental changes after code is written.

**Solution**: Review designs before implementation.

```markdown
## Design Review Process

1. **Before Coding**: Author creates design doc
2. **Design Review**: Team reviews approach (1-2 days)
3. **Approval**: Team approves or requests changes
4. **Implementation**: Author writes code
5. **Code Review**: Team reviews implementation (minor changes only)

This prevents "rewrite everything" comments later.
```

### Anti-Pattern 4: The Approval Without Reading

**Problem**: LGTM without actual review.

**Solution**: Be honest about review depth.

```python
# ❌ BAD: Fake approval
"LGTM! 👍"  # (commented 30 seconds after PR posted)

# ✅ GOOD: Honest scoping
"✓ LGTM for the monitoring changes (I focused my review there since I'm the
observability expert).

Someone else should review the training pipeline changes."

# OR:
"⏰ I don't have time for a thorough review right now. If this is urgent,
please ask @otherperson. Otherwise I can review tomorrow morning."
```

### Anti-Pattern 5: The Ghosting Reviewer

**Problem**: Requesting changes, then disappearing.

**Solution**: Set expectations and follow through.

```markdown
## Reviewer Responsibilities

1. **Initial Review**: Within 1 business day
2. **Follow-up**: Within 4 hours after author addresses feedback
3. **Unavailable?**: Assign to another reviewer or set expectations

Example:
"I've requested some changes, but I'm out tomorrow. @teammate can you take
over the review? Or we can wait until Thursday when I'm back."
```

## Tools and Automation

### Automated Checks (Run in CI)

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Code formatting
      - name: Check formatting (black)
        run: black --check .

      # Linting
      - name: Lint (flake8)
        run: flake8 .

      # Type checking
      - name: Type check (mypy)
        run: mypy .

      # Security
      - name: Security scan (bandit)
        run: bandit -r .

      # Dependency vulnerabilities
      - name: Check dependencies (safety)
        run: safety check

      # Test coverage
      - name: Run tests with coverage
        run: |
          pytest --cov=. --cov-report=xml

      - name: Coverage check
        run: |
          coverage report --fail-under=80

# This prevents >90% of review comments!
```

### Helpful Tools

```python
class CodeReviewTools:
    """Tools to enhance code review process"""

    def __init__(self):
        self.tools = {
            'static_analysis': [
                'pylint: Comprehensive Python linting',
                'mypy: Type checking',
                'bandit: Security vulnerability scanning',
                'radon: Code complexity metrics',
                'vulture: Dead code detection'
            ],

            'formatting': [
                'black: Opinionated code formatting',
                'isort: Import sorting',
                'prettier: JS/YAML/JSON formatting'
            ],

            'review_assistance': [
                'GitHub Copilot: AI suggestions',
                'SonarQube: Quality gates and metrics',
                'CodeClimate: Automated code review',
                'Reviewable: Enhanced review interface',
                'Gerrit: Alternative to GitHub PRs'
            ],

            'testing': [
                'pytest-cov: Coverage reporting',
                'hypothesis: Property-based testing',
                'locust: Load testing',
                'great_expectations: Data validation'
            ],

            'ml_specific': [
                'nbstripout: Clean Jupyter notebooks',
                'nbdime: Better notebook diffs',
                'dvc: Data version control',
                'wandb: Experiment tracking'
            ]
        }

    def setup_pre_commit_hooks(self) -> str:
        """Pre-commit configuration for ML projects"""

        return """
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']  # Prevent accidental model commits

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/kynan/nbstripout
    rev: 0.6.1
    hooks:
      - id: nbstripout  # Clean notebook outputs before commit
"""
```

### Pull Request Templates

```markdown
## Pull Request Template

<!-- .github/pull_request_template.md -->

## What does this PR do?
<!-- Clear, concise description of the change -->

## Why is this needed?
<!-- Business/technical justification -->

## How was this tested?
<!-- Testing approach and results -->
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Performance tested (if applicable)

## Deployment considerations
<!-- Anything special about deploying this? -->
- [ ] Database migrations required
- [ ] Configuration changes needed
- [ ] Feature flag controlled
- [ ] Monitoring/alerts updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] Added tests with >80% coverage
- [ ] All tests pass locally
- [ ] No new warnings
- [ ] Verified backward compatibility

## Screenshots/Metrics (if applicable)
<!-- For UI changes or performance improvements -->

## Related Issues
Closes #123
Related to #456

## Reviewer Notes
<!-- Anything specific you want reviewers to focus on? -->
```

## Summary

Effective code reviews are a **force multiplier** for senior engineers. They're not just about finding bugs—they're about building team capability, sharing knowledge, and maintaining quality.

### Key Principles

**As a Reviewer**:
1. **Collaborate, don't critique** - Be a partner, not a gatekeeper
2. **Focus on substance** - Design, correctness, testing > style
3. **Explain the why** - Help others learn, don't just point out problems
4. **Praise generously** - Reinforce good patterns
5. **Categorize feedback** - Make severity clear (blocking vs suggestion)
6. **Be timely** - Review within 1 business day

**As an Author**:
1. **Embrace feedback** - Ego detachment is crucial
2. **Make review easy** - Small PRs, clear descriptions, good tests
3. **Respond thoughtfully** - Address all comments
4. **Disagree respectfully** - It's okay to pushback with rationale
5. **Learn continuously** - Every review is a learning opportunity

### ML Infrastructure Focus

Pay special attention to:
- **GPU management** - Memory leaks, OOM handling, synchronization
- **Distributed training** - Gradient synchronization, data partitioning, checkpointing
- **Model serving** - Input validation, batching, error handling, monitoring
- **Performance** - Avoid N+1 queries, unnecessary CPU-GPU transfers
- **Robustness** - Fault tolerance, graceful degradation, retry logic

### Automation is Key

Automate what machines do well:
- Style checking (black, flake8)
- Type checking (mypy)
- Security scanning (bandit)
- Test coverage (pytest-cov)
- Dependency checks (safety)

This frees reviewers to focus on what humans do well:
- Design quality
- Business logic correctness
- Edge case handling
- User experience
- System architecture

### Return on Investment

Time invested in code reviews has **10-20x ROI**:
- Prevents production bugs (expensive)
- Spreads knowledge (prevents silos)
- Improves code quality (reduces maintenance)
- Builds team culture (increases retention)

**Make code reviews a priority, not an afterthought.**

## Next Steps

- Continue to [Lecture 4: Decision Making and Architecture](04-decision-making.md)
- Review a PR this week with the FIRE feedback framework
- Set up pre-commit hooks in your project
- Share this checklist with your team

## Additional Resources

**Books**:
- "Code Complete" by Steve McConnell (Chapter on reviews)
- "The Art of Readable Code" by Boswell & Foucher
- "Accelerate" by Forsgren, Humble, Kim (Research on code reviews)

**Articles**:
- Google's Code Review Guidelines: https://google.github.io/eng-practices/review/
- Microsoft's Code Review Study: https://www.microsoft.com/en-us/research/publication/code-reviews-do-not-find-bugs-how-the-current-code-review-best-practice-slows-us-down/
- Conventional Comments: https://conventionalcomments.org/

**Tools**:
- Pre-commit: https://pre-commit.com/
- Reviewable: https://reviewable.io/
- Gerrit: https://www.gerritcodereview.com/
