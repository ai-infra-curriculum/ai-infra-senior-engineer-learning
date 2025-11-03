# Lecture 2: Mentorship and Coaching

## Learning Objectives

By the end of this lecture, you will be able to:

- Distinguish mentorship from coaching applying long-term holistic career guidance vs short-term goal-focused approaches choosing appropriate methods
- Implement active listening using HEAR framework halting engaging anticipating responding thoughtfully building understanding through focused attention
- Apply powerful questioning techniques using understanding exploration action frameworks facilitating growth through inquiry not prescription
- Conduct effective coaching sessions implementing GROW model setting goals assessing reality exploring options committing to action plans
- Provide constructive feedback using SBI model describing situation behavior impact clearly linking actions to outcomes with specificity
- Guide career development understanding technical ladder progression conducting structured 1-on-1s aligning individual growth with organizational needs
- Execute knowledge transfer strategies implementing documentation pairing shadowing teaching progressively transferring ownership and capability
- Build high-performing teams facilitating Tuckman's stages creating learning culture supporting team development through forming storming norming performing

## Table of Contents
1. [Mentorship vs Coaching](#mentorship-vs-coaching)
2. [Effective Mentoring Techniques](#effective-mentoring-techniques)
3. [Career Development Guidance](#career-development-guidance)
4. [Knowledge Transfer Strategies](#knowledge-transfer-strategies)
5. [Building High-Performing Teams](#building-high-performing-teams)

## Mentorship vs Coaching

### Key Differences

**Mentorship**: Long-term relationship focusing on holistic career development, experience-based guidance, and organic conversations.

**Coaching**: Short-term engagement for specific goals, question-based approach, and structured sessions with clear outcomes.

```python
# Decision framework
def choose_approach(situation: dict) -> str:
    if situation['timeline'] == 'long-term' and situation['scope'] == 'career':
        return 'mentorship'
    elif situation['timeline'] == 'short-term' and situation['goal'] == 'specific_skill':
        return 'coaching'
    else:
        return 'hybrid'
```

## Effective Mentoring Techniques

### 1. Active Listening - The HEAR Framework

- **H**alt: Stop what you're doing
- **E**ngage: Give full attention
- **A**nticipate: Think ahead to understand
- **R**espond: Provide thoughtful feedback

### 2. Asking Powerful Questions

```python
powerful_questions = {
    'understanding': [
        "What's the core challenge you're facing?",
        "What have you tried so far?",
    ],
    'exploration': [
        "What other options have you considered?",
        "What would success look like?",
    ],
    'action': [
        "What's your next step?",
        "How will you know if it's working?"
    ]
}
```

### 3. The GROW Model (Goal-Reality-Options-Will)

Structured coaching framework for productive sessions.

### 4. Providing Constructive Feedback - SBI Model

**Situation-Behavior-Impact** framework for clear, actionable feedback.

## Career Development Guidance

### Technical Career Ladder for ML Infrastructure

```
Senior Engineer → Staff Engineer → Principal Engineer → Distinguished Engineer
                ↓
              Tech Lead → Engineering Manager → Director
```

### 1:1 Meeting Structure

```markdown
## Effective 1:1 Template (30-60 min)

### Check-in (5 min)
- How are you doing? What's on your mind?

### Wins & Challenges (10 min)
- What are you proud of? What's been challenging?

### Career Development (15 min)
- Progress on goals, new opportunities, skills to develop

### Projects & Technical Topics (15 min)
- Current project status, technical challenges

### Feedback & Action Items (10 min)
- What could I do better? Concrete next steps
```

## Knowledge Transfer Strategies

### 1. Documentation-First Approach

Progressive documentation levels:
- Level 1: Runbooks (step-by-step procedures)
- Level 2: Guides (explanatory documents)
- Level 3: References (deep technical knowledge)
- Level 4: Principles (decision-making frameworks)

### 2. Pairing and Shadowing

**Effective Pairing**: Navigator and Driver roles, switching every 30 minutes, explaining thinking out loud.

### 3. Teaching by Doing

Progressive responsibility stages:
1. **Observe**: Mentor demonstrates, mentee watches
2. **Assist**: Mentor leads, mentee executes subtasks
3. **Guide**: Mentee leads, mentor advises
4. **Independent**: Mentee owns, mentor available for questions

## Building High-Performing Teams

### Tuckman's Team Development Stages

1. **Forming**: Clarify roles, establish norms, create safety
2. **Storming**: Facilitate healthy conflict, coach through disagreements
3. **Norming**: Reinforce positive behaviors, refine processes
4. **Performing**: Remove obstacles, challenge with stretch goals

### Creating Learning Culture

- **Individual**: Growth mindset, curiosity, experimentation
- **Team**: Knowledge sharing, pair programming, code reviews
- **Organizational**: Learning time, conferences, training budget

## ML Infrastructure Mentoring

### Progressive Skills Ladder

**Junior**: Basic Kubernetes, Docker, simple model deployment
**Mid-Level**: Distributed training, resource optimization, ML pipelines
**Senior**: Architecture design, multi-cluster management, cost optimization
**Staff+**: Platform strategy, cross-org influence, technical vision

### Common Challenges and Guidance

**Scaling Training**: Start with data parallel, learn distributed frameworks (Horovod, PyTorch DDP)
**Infrastructure Costs**: Resource quotas, spot instances, monitoring, optimization
**Model Deployment**: Learn serving frameworks, implement A/B testing, set up monitoring

## Summary

Effective mentorship requires:
1. Active Listening and powerful questions
2. Structured approach (GROW model)
3. Knowledge transfer through documentation, pairing, teaching
4. Career guidance and support
5. Team building and learning culture

**Key Principles**:
- Focus on mentee's growth, not your ego
- Ask more than you tell
- Share experiences, don't prescribe solutions
- Be consistent and reliable
- Celebrate wins and learn from failures

## Next Steps

- Continue to [Lecture 3: Code Review Best Practices](03-code-review.md)
- Reflect on your mentoring style
- Schedule regular 1:1s

## Additional Resources

- "The Coaching Habit" by Michael Bungay Stanier
- "Radical Candor" by Kim Scott
- "The Manager's Path" by Camille Fournier
