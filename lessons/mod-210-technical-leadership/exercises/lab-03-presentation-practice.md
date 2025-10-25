# Lab 3: Technical Presentation Practice

## Overview

As a Senior AI Infrastructure Engineer, you'll frequently present technical concepts to various audiences: executives, engineers, data scientists, and non-technical stakeholders. This lab helps you develop and practice presentation skills tailored to different audiences.

## Learning Objectives

- Create presentations for different audience types
- Adapt technical content to audience knowledge level
- Use storytelling to make technical concepts engaging
- Handle questions and objections effectively
- Receive and incorporate feedback on presentation style

## Duration

3-4 hours

## Prerequisites

- Completion of Module 210 Lecture 05 (Technical Communication)
- Access to presentation software (Google Slides, PowerPoint, Keynote)
- Optional: Recording device for self-review

---

## Part 1: Know Your Audience (30 minutes)

### The Three Audience Types

**Technical Audience** (Engineers, Data Scientists)
- What they care about: Implementation details, performance, architecture
- Language: Technical jargon is fine, deep dives welcome
- Questions: "How does this handle edge case X?", "What's the latency?"

**Business/Executive Audience** (Directors, VPs, C-suite)
- What they care about: ROI, risk, strategic alignment, timeline
- Language: Business terms, avoid unnecessary jargon
- Questions: "What's the cost?", "When can we ship?", "What's the risk?"

**Mixed Audience** (Cross-functional teams)
- What they care about: How it affects their work, integration points
- Language: Clear explanations, define technical terms
- Questions: Varies widely by role

### Exercise: Audience Analysis

For your current/upcoming presentation:
1. Who will be in the room?
2. What's their technical background (1-10 scale)?
3. What decision are they making?
4. What objections might they have?
5. What success looks like to them?

---

## Part 2: Scenario 1 - Pitch to Executives (60 minutes)

### Context

You need to convince the CTO and VP of Engineering to invest $300K in GPU infrastructure for model serving. They're concerned about cost and unclear on the value.

### Your Task

Create a 10-15 minute presentation with 5-7 slides covering:

**Slide 1: The Problem** (Current State)
- What's not working today?
- Quantify the pain (latency numbers, user impact, cost inefficiency)

**Slide 2: The Opportunity** (What Could Be)
- What becomes possible with GPU acceleration?
- Business impact (faster features, better UX, competitive advantage)

**Slide 3: The Solution** (Proposed Approach)
- High-level architecture (no deep technical details)
- Timeline and phases

**Slide 4: The Business Case** (ROI)
- Cost breakdown ($300K upfront, $50K/year operational)
- Savings/revenue impact
- Payback period

**Slide 5: Risk Mitigation**
- What could go wrong?
- How we'll handle it
- Pilot approach to de-risk

**Slide 6: The Ask**
- Clear decision needed
- Timeline
- Next steps

### Evaluation Criteria

- [ ] Problem clearly stated with quantifiable impact
- [ ] Business value > technical details (80/20 rule)
- [ ] Financial analysis (cost, ROI, payback)
- [ ] Risks acknowledged and mitigated
- [ ] Clear call to action
- [ ] Stays within time limit

### Practice Questions

Prepare answers for:
1. "Why can't we use cheaper CPUs?"
2. "What if we just use cloud GPUs instead?"
3. "How confident are you in the ROI numbers?"
4. "What's the risk if this doesn't work?"

---

## Part 3: Scenario 2 - Technical Deep Dive (60 minutes)

### Context

Present your distributed training architecture to the ML engineering team. They're evaluating whether to adopt your approach for their workloads.

### Your Task

Create a 20-25 minute presentation with 10-12 slides covering:

**Slide 1: Overview**
- What we're building
- Why it matters (technical motivation)

**Slide 2-3: Architecture**
- System design with detailed diagrams
- Component interactions
- Technology stack

**Slide 4-5: Key Technical Decisions**
- Why Ray instead of Horovod?
- Why NCCL for communication?
- Trade-offs made

**Slide 6-7: Performance**
- Benchmarks and measurements
- Scaling characteristics
- Optimization techniques

**Slide 8-9: How to Use It**
- API/interface
- Code examples
- Migration path from current solution

**Slide 10: Monitoring & Observability**
- Metrics and dashboards
- Debugging failed training runs

**Slide 11-12: Roadmap & Getting Involved**
- Current limitations
- Future work
- How to contribute

### Evaluation Criteria

- [ ] Architecture diagrams are clear and detailed
- [ ] Technical decisions explained with rationale
- [ ] Performance data included with methodology
- [ ] Practical examples showing usage
- [ ] Acknowledges limitations and trade-offs
- [ ] Encourages questions and discussion

### Practice Questions

1. "How does this compare to Kubeflow?"
2. "What happens if a worker node fails mid-training?"
3. "Can this handle our 1TB dataset?"
4. "How do we debug if something goes wrong?"

---

## Part 4: Scenario 3 - Cross-Functional Kickoff (45 minutes)

### Context

Kick off a project to implement a new ML feature store. Audience includes: data scientists, ML engineers, data engineers, and product managers.

### Your Task

Create a 15-20 minute presentation with 6-8 slides:

**Slide 1: Why We're Here**
- Current pain points (different roles experience different pains)
- Vision for improvement

**Slide 2: What's a Feature Store?** (Education)
- Explain the concept simply
- Analogy: "Like a database, but optimized for ML features"

**Slide 3: How It Helps Each Role**
- Data Scientists: Reuse features, faster experimentation
- ML Engineers: Consistent serving, reduced training-serving skew
- Data Engineers: Central feature management
- Product: Faster time to market for ML features

**Slide 4: Architecture Overview**
- High-level components (no deep technical details)
- Where it fits in existing stack

**Slide 5: Phases & Timeline**
- Phase 1: Offline features (month 1-2)
- Phase 2: Online serving (month 3-4)
- Phase 3: Real-time features (month 5-6)

**Slide 6: How We'll Work Together**
- Roles and responsibilities
- Decision-making process (DACI framework)
- Communication channels

**Slide 7: Next Steps**
- Action items by role
- First milestone
- How to stay informed

### Evaluation Criteria

- [ ] Addresses all audience segments
- [ ] Technical level appropriate for mixed audience
- [ ] Clear roles and responsibilities
- [ ] Realistic timeline
- [ ] Defines collaboration model
- [ ] Actionable next steps

---

## Part 5: Delivery Techniques (30 minutes)

### The 3-Part Opening

**Hook** (30 seconds): Grab attention
- Surprising statistic
- Relevant story
- Provocative question

**Context** (60 seconds): Set the stage
- Why this topic matters
- What you'll cover

**Roadmap** (30 seconds): Preview structure
- "Today I'll cover three things: X, Y, Z"

### Example Opening

> "Last month, a data scientist waited 6 hours for a model to train, only to discover a typo in a hyperparameter. [Hook]
>
> This happens daily across our ML teams, costing us thousands in wasted compute and slowing down innovation. Today, I'm here to propose a solution. [Context]
>
> I'll cover three things: the scale of the problem, our proposed distributed training platform, and how we can deploy it in 30 days. [Roadmap]"

### Body Techniques

**Signposting**: Tell them where you are
- "That covers the architecture. Now let's talk about performance..."

**Rule of Three**: Group ideas in threes
- More memorable than 2 or 4
- "This gives us three benefits: cost, speed, and reliability"

**Evidence**: Back up claims
- Data, benchmarks, case studies
- "In our tests, this reduced latency by 45%"

### The Close

**Summary**: Recap key points
**Call to Action**: What you want them to do
**Questions**: Open the floor

### Example Close

> "To recap: We can reduce training time by 10x, save $200K annually, and accelerate our ML roadmap by 6 months. [Summary]
>
> I'm asking for approval to move forward with Phase 1 this quarter. [Call to Action]
>
> What questions do you have?" [Questions]

---

## Part 6: Handling Questions (30 minutes)

### The Formula

1. **Listen**: Don't interrupt, let them finish
2. **Pause**: Take 2 seconds to think
3. **Clarify**: "Just to make sure I understand, you're asking about X?"
4. **Answer**: Directly and concisely
5. **Check**: "Does that answer your question?"

### Difficult Questions

**"I don't know"**
- "Great question. I don't have that data right now, but I'll follow up with you by EOD tomorrow."
- Better than making something up

**Hostile Question**
- Stay calm, don't get defensive
- "I appreciate your concern. Let me address that..."
- Acknowledge valid points

**Off-Topic Question**
- "That's a good question, but outside the scope of today's discussion. Let's sync offline."
- Offer to follow up

**Overly Technical (for non-technical audience)**
- "Let me explain that at a higher level..."
- Use analogy

---

## Part 7: Self-Assessment Checklist (15 minutes)

After each presentation, rate yourself 1-5 on:

### Content
- [ ] Clear objective/purpose
- [ ] Appropriate technical level for audience
- [ ] Compelling narrative/story
- [ ] Evidence and data to support claims
- [ ] Acknowledged risks/limitations

### Delivery
- [ ] Started on time, ended on time
- [ ] Confident body language
- [ ] Good eye contact
- [ ] Varied tone and pace
- [ ] Managed nerves effectively

### Slides
- [ ] Minimal text (6 words per bullet max)
- [ ] Clear visuals and diagrams
- [ ] Consistent design
- [ ] Readable fonts (30pt minimum)
- [ ] High contrast colors

### Q&A
- [ ] Listened fully to questions
- [ ] Answered directly and concisely
- [ ] Admitted when unsure
- [ ] Maintained composure
- [ ] Checked for understanding

---

## Part 8: Practice Delivery (45 minutes)

### Record Yourself

1. Choose one scenario (1, 2, or 3)
2. Create the slides
3. Record yourself presenting (phone camera is fine)
4. Watch the recording

### What to Look For

**Verbal**
- Filler words (um, uh, like, you know)
- Pace (too fast? too slow?)
- Volume and energy
- Technical jargon overuse

**Non-Verbal**
- Posture and stance
- Hand gestures (too many? too few?)
- Eye contact (with camera)
- Nervous habits

### Improvement Plan

Pick your top 2 weaknesses:
1. __________________________________________
2. __________________________________________

How you'll improve them:
1. __________________________________________
2. __________________________________________

---

## Resources

### Presentation Design
- **Presentation Zen** by Garr Reynolds - Visual design principles
- **Slide:ology** by Nancy Duarte - Creating compelling presentations
- **Better Presentations** by Jonathan Schwabish - Data visualization

### Public Speaking
- **Talk Like TED** by Carmine Gallo - Storytelling techniques
- **Confessions of a Public Speaker** by Scott Berkun - Practical advice
- Toastmasters International - Practice opportunities

### Tools
- **Beautiful.ai** - AI-powered slide design
- **Pitch** - Collaborative presentation tool
- **Figma** - Custom diagrams and visuals
- **Carbon** - Beautiful code screenshots

---

## Submission

Submit the following:
1. Slides for your chosen scenario (PDF)
2. Recording of your 5-minute pitch (optional but recommended)
3. Self-assessment scores
4. Top 2 improvement areas with plan

---

## Extension Activities

1. **Lightning Talk**: 5-minute version of your technical presentation
2. **Executive Briefing**: One-slide summary of a complex technical topic
3. **Team Presentation**: Present with 2-3 colleagues, practice handoffs
4. **Live Q&A**: Present to colleagues, dedicate 50% of time to Q&A

---

## Next Steps

- Schedule a brown bag lunch to practice
- Present at the next team meeting
- Volunteer for conference talks (internal or external)
- Watch talks from your favorite speakers, note their techniques
- Join Toastmasters or similar group for regular practice

**Remember**: Great presenters aren't born, they're made through practice. Every presentation makes you better.