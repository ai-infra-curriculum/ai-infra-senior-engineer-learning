# Module 210: Tools and Frameworks

Practical tools, templates, and frameworks for technical leadership in AI infrastructure.

---

## 📋 Templates

### Architecture Decision Records (ADRs)

**MADR Template** (Markdown Architectural Decision Records)
```markdown
# [short title of solved problem and solution]

* Status: [proposed | rejected | accepted | deprecated | superseded by [ADR-0005]]
* Deciders: [list everyone involved in decision]
* Date: [YYYY-MM-DD when decision was last updated]

## Context and Problem Statement
[Describe context and problem statement]

## Decision Drivers
* [driver 1]
* [driver 2]
* ...

## Considered Options
* [option 1]
* [option 2]
* ...

## Decision Outcome
Chosen option: "[option 1]", because [justification].

### Positive Consequences
* [consequence 1]
* ...

### Negative Consequences
* [consequence 1]
* ...
```

**Where to use**: Significant architectural decisions, technology choices, design patterns

---

###  1:1 Meeting Template

**Preparation (Before Meeting)**
```markdown
## What I want to discuss:
1. [Topic 1 - with context]
2. [Topic 2 - with context]
3. [Topic 3 - with context]

## What I need help with:
- [Blocker/question]

## Updates to share:
- [Win/progress]
- [Challenge]
```

**During Meeting Structure**
- **5 min**: How are you? (relationship building)
- **15 min**: Their agenda (let them lead)
- **10 min**: Your agenda
- **5 min**: Action items and next steps

**Post-Meeting**
- Document action items
- Add to shared notes doc
- Follow up within 48 hours on commitments

**Tool**: Google Docs template shared between manager/report

---

### Design Doc Template

```markdown
# [Project Name] Design Doc

**Author**: [name]
**Reviewers**: [names]
**Last Updated**: [date]
**Status**: [Draft | In Review | Approved]

## Overview
[2-3 sentence summary]

## Goals and Non-Goals
### Goals
- Goal 1
- Goal 2

### Non-Goals
- What this does NOT solve
- Future work

## Background
[Context for readers unfamiliar with the problem]

## Proposed Solution
[High-level approach]

### Architecture Diagram
[Include diagram]

### Data Model
[If applicable]

### API Design
[If applicable]

## Alternatives Considered
### Option 1: [Name]
- Pros:
- Cons:
- Why not chosen:

## Security Considerations
- Authentication/Authorization
- Data privacy
- Compliance

## Observability & Monitoring
- Metrics to track
- Alerts to set up
- Logging strategy

## Rollout Plan
- Phase 1:
- Phase 2:
- Rollback strategy:

## Open Questions
- [ ] Question 1
- [ ] Question 2
```

**When to use**: New feature design, system migrations, API changes

---

## 🎯 Decision-Making Frameworks

### DACI Framework

**D** - Driver: Owns the decision process
**A** - Approver: Makes the final call
**C** - Contributors: Provide input
**I** - Informed: Kept in the loop

**Example: Choosing ML Serving Framework**
- **D**: Senior ML Infrastructure Engineer (you)
- **A**: Engineering Manager
- **C**: Data Scientists, SREs, other MLEs
- **I**: Product team, stakeholders

**When to use**: Cross-functional decisions with multiple stakeholders

---

### RACI Matrix

For complex projects with many participants:

| Task | Responsible | Accountable | Consulted | Informed |
|------|------------|------------|-----------|----------|
| Design | Alice | Bob | Charlie, Dana | Team |
| Implementation | Bob | Bob | Alice | Stakeholders |
| Testing | Charlie | Bob | QA team | PM |

**R** - Does the work
**A** - Accountable for completion (only one person!)
**C** - Provides input
**I** - Kept informed

---

### Risk Assessment Matrix

|  | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| **High Probability** | Monitor | Plan mitigation | Immediate action |
| **Medium Probability** | Accept | Plan mitigation | Plan mitigation |
| **Low Probability** | Accept | Monitor | Plan mitigation |

**Use for**: Project planning, system design, incident response

---

## 💬 Communication Frameworks

### SBI Feedback Framework

**S**ituation: When/where did this happen?
**B**ehavior: What specifically did you observe?
**I**mpact: What was the effect?

**Example**:
```
Situation: "In yesterday's design review..."
Behavior: "...when you dismissed Sarah's suggestion without explanation..."
Impact: "...she seemed discouraged and didn't contribute for the rest of the meeting."
```

**When to use**: Giving constructive feedback, performance conversations

---

### BLUF (Bottom Line Up Front)

Structure for executive communication:

1. **Bottom Line**: The answer/recommendation (1 sentence)
2. **Supporting Facts**: 3-5 key points
3. **Details**: Additional context if needed

**Example**:
```
BLUF: We should adopt TensorRT for model serving, estimated ROI of 40% cost savings.

Key Points:
- 3x faster inference than current solution
- Reduces GPU costs by ~40%
- 2 week implementation timeline
- Risk: NVIDIA lock-in (mitigated by ONNX support)

[Additional technical details follow...]
```

**When to use**: Email to executives, project proposals, incident updates

---

### Pyramid Principle

Communicate conclusions first, then supporting arguments:

```
Main Point
├── Supporting Point 1
│   ├── Evidence A
│   └── Evidence B
├── Supporting Point 2
│   ├── Evidence C
│   └── Evidence D
└── Supporting Point 3
    ├── Evidence E
    └── Evidence F
```

**When to use**: Design docs, technical presentations, proposals

---

## 🛠️ Digital Tools

### Documentation

**Markdown Editors**
- Obsidian: Note-taking with linking
- Notion: Team wiki and docs
- Confluence: Enterprise documentation
- GitBook: Developer documentation

**Diagram Tools**
- draw.io / diagrams.net: Free, versatile
- Lucidchart: Professional diagrams
- Mermaid: Diagrams as code
- PlantUML: UML diagrams as code

**ADR Management**
- adr-tools: CLI for ADRs
- log4brains: Web UI for browsing ADRs

---

### Presentation Tools

**Slides**
- Google Slides: Collaboration
- Keynote: Mac users, high quality
- Reveal.js: Markdown to slides
- Marp: Markdown presentation ecosystem

**Technical Diagrams**
- Excalidraw: Hand-drawn style diagrams
- Whimsical: Quick wireframes and flows
- C4-PlantUML: Architecture diagrams

---

### Collaboration

**Meetings**
- Zoom/Google Meet: Video conferencing
- Miro/Mural: Virtual whiteboarding
- Jamboard: Google's whiteboard

**Async Communication**
- Slack: Team chat
- Discord: Community chat
- Loom: Video messages

**Project Management**
- Jira: Issue tracking
- Linear: Modern issue tracker
- GitHub Projects: Integrated with code

---

## 🎓 Leadership Development Frameworks

### 70-20-10 Learning Model

- **70%**: On-the-job experiences (projects, stretch assignments)
- **20%**: Learning from others (mentoring, peer feedback)
- **10%**: Formal training (courses, books, conferences)

**Application**:
- Lead a complex project (70%)
- Find a mentor + mentor someone (20%)
- Read one book per quarter (10%)

---

### Skill Development Matrix

| Skill | Current Level | Target Level | Development Plan |
|-------|--------------|--------------|-----------------|
| System Design | 7/10 | 9/10 | Lead next architecture project |
| Public Speaking | 5/10 | 7/10 | Present at team meeting monthly |
| Mentoring | 6/10 | 8/10 | Take on 2 mentees |

**Update quarterly**, track progress, adjust plans

---

### Leadership Competency Model

**Technical Skills**
- System design
- Code quality
- Architecture decisions

**People Skills**
- Mentoring
- Feedback
- Conflict resolution

**Strategic Skills**
- Long-term planning
- Stakeholder management
- Vision setting

**Assess yourself 1-10 on each, create development plan**

---

## 📊 Metrics and Tracking

### Team Health Metrics

**Track monthly:**
- Deployment frequency
- Lead time for changes
- Time to restore service
- Change failure rate

**Plus:**
- Team satisfaction (survey)
- On-call burden
- Meeting load

**Tool**: Spreadsheet or dashboard (Grafana, Datadog)

---

### Personal Effectiveness

**Weekly tracking:**
- Hours in meetings
- Focus time blocks
- Code reviews completed
- 1:1s conducted

**Monthly reflection:**
- What went well?
- What didn't?
- What to change next month?

**Tool**: Time tracking (Toggl, RescueTime) + reflection doc

---

## 🎤 Presentation Frameworks

### Nancy Duarte's Sparkline

Structure presentations as a story:

```
What is → What could be → What is → What could be → New Bliss
```

**Example for GPU infrastructure proposal:**
- What is: Current CPU-only serving, slow inference
- What could be: GPU acceleration, 10x faster
- What is: But GPUs are expensive
- What could be: Cost-benefit analysis shows ROI in 6 months
- New bliss: Happy users, cost-effective serving

---

### Andy Raskin's Strategic Narrative

1. **The world has changed** (create urgency)
2. **There's a winner and loser** (stakes)
3. **We have a promised land** (vision)
4. **Obstacles in our way** (challenges)
5. **We have a plan** (solution)

**When to use**: Vision presentations, strategic initiatives

---

## 📅 Meeting Facilitation

### Meeting Template

```markdown
# [Meeting Title]

**Date**: [date]
**Attendees**: [names]
**Duration**: [planned time]

## Objectives
- [ ] Objective 1
- [ ] Objective 2

## Agenda
1. Context (5 min)
2. Discussion (20 min)
3. Decision/Next steps (10 min)

## Decisions Made
- Decision 1: [what + who + when]

## Action Items
- [ ] Action 1 - @owner - due date
- [ ] Action 2 - @owner - due date

## Parking Lot
- Items for future discussion
```

### Facilitation Techniques

**Timeboxing**: Strict time limits per topic
**Round Robin**: Everyone speaks once before anyone speaks twice
**Silent Brainstorming**: Write ideas before discussing
**Fist to Five**: Quick consensus check (0-5 fingers)

---

## 🔄 Continuous Improvement

### Retrospective Format

**Start, Stop, Continue**
- Start: What should we start doing?
- Stop: What should we stop doing?
- Continue: What's working well?

**Alternative: 4Ls**
- Liked
- Learned
- Lacked
- Longed for

**Tool**: Miro board, shared doc, or Retrium

---

### Feedback Collection

**Anonymous Survey Template**:
1. What's going well? (open-ended)
2. What needs improvement? (open-ended)
3. Team collaboration: 1-5 scale
4. Technical quality: 1-5 scale
5. Work-life balance: 1-5 scale

**Frequency**: Quarterly
**Tool**: Google Forms, Typeform, Culture Amp

---

## 📚 Framework Library

**Bookmark these for quick reference:**

- [C4 Model](https://c4model.com/) - Architecture diagrams
- [MADR](https://adr.github.io/madr/) - ADR template
- [RFC Template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md) - Rust's RFC format (adaptable)
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Onboarding Template](https://github.com/hedgedoc/hedgedoc) - HedgedDoc example

---

## 🎯 Quick Reference

### When to use what:

| Situation | Framework/Tool |
|-----------|---------------|
| Complex decision | DACI |
| Project planning | RACI matrix |
| Giving feedback | SBI model |
| Email to exec | BLUF |
| Architecture decision | ADR |
| System design | Design doc + C4 diagrams |
| Presentation | Sparkline or Strategic Narrative |
| Team improvement | Retrospective |

---

## 💡 Pro Tips

1. **Start simple**: Don't use complex frameworks for simple problems
2. **Customize templates**: Adapt to your team's needs
3. **Be consistent**: Pick tools and stick with them
4. **Automate**: Use CLI tools for ADRs, scripts for metrics
5. **Iterate**: Improve templates based on feedback

---

**Next Step**: Pick one template or framework from this list and use it this week.