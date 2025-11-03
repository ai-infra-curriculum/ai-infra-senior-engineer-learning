# Lecture 6: Building Consensus

## Learning Objectives

By the end of this lecture, you will be able to:

- Architect consensus strategies understanding good tech with consensus succeeds vs perfect tech without consensus fails calculating consensus impact
- Apply consensus spectrum choosing command consult consensus consent vote levels matching decision urgency impact reversibility expertise distribution
- Execute stakeholder analysis mapping power-interest grid understanding motivations fears tailoring engagement strategies for key players satisfied informed monitored
- Build alignment early conducting 1-on-1 pre-sells incorporating feedback giving credit reconfirming support creating ownership through collaborative design
- Handle disagreement constructively implementing disagree and commit framework using five whys finding root causes negotiating based on interests
- Facilitate effective meetings creating clear agendas using round-robin parking lot silent writing handling dominating speakers side conversations conflicts
- Influence ethically applying Cialdini's principles using reciprocity commitment consistency social proof authority liking scarcity serving project over ego
- Navigate consensus failures escalating gracefully using joint escalation providing context moving forward with disagree-commit pilot phased parallel minimal viable approaches

## Table of Contents
1. [Why Consensus Matters](#why-consensus-matters)
2. [The Consensus Spectrum](#the-consensus-spectrum)
3. [Stakeholder Mapping and Analysis](#stakeholder-mapping-and-analysis)
4. [Building Alignment Early](#building-alignment-early)
5. [Handling Disagreement](#handling-disagreement)
6. [Facilitation Techniques](#facilitation-techniques)
7. [Getting to "Yes"](#getting-to-yes)
8. [When Consensus Fails](#when-consensus-fails)

## Why Consensus Matters

**The hard truth**: The best technical solution that nobody supports will fail. A good solution with broad buy-in will succeed.

As a senior engineer, your job isn't just to find the right answer—it's to **get everyone aligned** on moving forward together.

### The Cost of No Consensus

```python
class ConsensusImpact:
    """Understanding the impact of consensus (or lack of it)"""

    def calculate_project_success(self, technical_quality: int,
                                  consensus_level: int) -> dict:
        """Success requires both good tech AND consensus"""

        # Perfect tech, no consensus = failure
        if technical_quality >= 9 and consensus_level <= 3:
            return {
                'outcome': 'FAILURE',
                'reason': 'Technically perfect but blocked by stakeholders',
                'example': 'Brilliant architecture that nobody adopts'
            }

        # Mediocre tech, strong consensus = success
        elif technical_quality >= 6 and consensus_level >= 8:
            return {
                'outcome': 'SUCCESS',
                'reason': 'Good enough solution with strong support',
                'example': 'Pragmatic choice that teams embrace and improve over time'
            }

        # Good tech, good consensus = great success
        elif technical_quality >= 8 and consensus_level >= 7:
            return {
                'outcome': 'GREAT SUCCESS',
                'reason': 'Strong solution with broad adoption',
                'example': 'Well-designed system that becomes company standard'
            }

        # Poor tech, poor consensus = disaster
        else:
            return {
                'outcome': 'DISASTER',
                'reason': 'Neither technical quality nor support',
                'example': 'Failed initiative that wastes time and money'
            }

# Example: Two projects
project_a = ConsensusImpact()
result_a = project_a.calculate_project_success(
    technical_quality=10,  # Perfect architecture
    consensus_level=2      # Nobody wants it
)
print(f"Project A: {result_a['outcome']}")
print(f"  {result_a['reason']}\n")

result_b = project_a.calculate_project_success(
    technical_quality=7,   # Good enough architecture
    consensus_level=9      # Everyone on board
)
print(f"Project B: {result_b['outcome']}")
print(f"  {result_b['reason']}")

# Output:
# Project A: FAILURE (perfect tech, no consensus)
# Project B: SUCCESS (good tech, strong consensus)
```

### What Consensus Enables

```python
def consensus_benefits() -> dict:
    """The tangible benefits of building consensus"""

    return {
        'faster_execution': {
            'without_consensus': '6 months debating, 3 months implementing',
            'with_consensus': '2 weeks aligning, 4 months implementing',
            'benefit': 'Faster time to value, less wasted effort'
        },

        'better_solutions': {
            'without_consensus': 'One person\'s view, narrow perspective',
            'with_consensus': 'Diverse input improves design',
            'benefit': 'Stronger solutions that consider more angles'
        },

        'sustained_support': {
            'without_consensus': 'Passive resistance, silent sabotage',
            'with_consensus': 'Active champions, vocal advocates',
            'benefit': 'Initiative succeeds long-term, not just launches'
        },

        'organizational_learning': {
            'without_consensus': 'Knowledge siloed, repeated mistakes',
            'with_consensus': 'Shared understanding, collective growth',
            'benefit': 'Team capability increases over time'
        },

        'career_impact': {
            'without_consensus': 'Seen as difficult, ignored',
            'with_consensus': 'Seen as leader, sought for advice',
            'benefit': 'Promotions, opportunities, influence'
        }
    }
```

## The Consensus Spectrum

Not all decisions need the same level of consensus. Choose the right level for the situation.

### Consensus Levels

```python
from enum import Enum

class ConsensusLevel(Enum):
    """Different levels of consensus"""

    COMMAND = "unilateral"          # Leader decides alone
    CONSULT = "input_gathered"      # Gather input, leader decides
    CONSENSUS = "agreement"         # Everyone must agree
    CONSENT = "no_objections"       # No one blocks
    VOTE = "majority_rules"         # Democratic decision

class ConsensusStrategy:
    """Choosing the right consensus approach"""

    def choose_level(self, decision: dict) -> dict:
        """Match consensus level to decision characteristics"""

        urgency = decision.get('urgency', 'medium')
        impact = decision.get('impact', 'medium')
        reversibility = decision.get('reversible', True)
        expertise_distributed = decision.get('expertise_distributed', False)

        # Emergency: Command decision
        if urgency == 'critical':
            return {
                'level': ConsensusLevel.COMMAND,
                'approach': 'Decide quickly, explain why, gather feedback after',
                'when': 'Production down, security breach, immediate crisis',
                'example': 'Rollback bad deployment NOW, discuss improvements later'
            }

        # Low impact, reversible: Consent
        elif impact == 'low' and reversibility:
            return {
                'level': ConsensusLevel.CONSENT,
                'approach': 'Propose solution, ask for objections, proceed if none',
                'when': 'Routine decisions, low stakes, easy to change',
                'example': 'Change log format - propose, get consent, implement'
            }

        # High impact, irreversible, centralized expertise: Consult
        elif impact == 'high' and not expertise_distributed:
            return {
                'level': ConsensusLevel.CONSULT,
                'approach': 'Expert proposes, gathers input, makes final decision',
                'when': 'Technical decision requiring deep expertise',
                'example': 'Database choice - DBA proposes, gets feedback, decides'
            }

        # High impact, distributed expertise: Consensus
        elif impact == 'high' and expertise_distributed:
            return {
                'level': ConsensusLevel.CONSENSUS,
                'approach': 'Collaborative decision, everyone must support',
                'when': 'Architecture decisions affecting multiple teams',
                'example': 'API design standard - all teams must agree and adopt'
            }

        # Tie-break needed: Vote
        else:
            return {
                'level': ConsensusLevel.VOTE,
                'approach': 'Discuss options, vote, majority decides',
                'when': 'Two equally good options, need to break tie',
                'example': 'Python vs Go for service - both viable, vote to decide'
            }

# Example: Choosing consensus level
strategy = ConsensusStrategy()

decision_1 = strategy.choose_level({
    'urgency': 'critical',
    'impact': 'high'
})
print(f"Emergency decision: {decision_1['level'].value}")
print(f"  {decision_1['approach']}\n")

decision_2 = strategy.choose_level({
    'urgency': 'normal',
    'impact': 'high',
    'reversible': False,
    'expertise_distributed': True
})
print(f"Major architecture: {decision_2['level'].value}")
print(f"  {decision_2['approach']}")
```

## Stakeholder Mapping and Analysis

Before building consensus, understand who matters and what they care about.

### Power-Interest Grid

```python
class StakeholderAnalysis:
    """Analyzing and mapping stakeholders"""

    def map_stakeholder(self, name: str, power: int, interest: int) -> dict:
        """
        Map stakeholder on Power-Interest grid

        Power: Ability to block or enable (1-10)
        Interest: How much they care (1-10)
        """

        if power >= 7 and interest >= 7:
            quadrant = 'Key Players'
            strategy = 'Collaborate closely, frequent updates, co-design solution'

        elif power >= 7 and interest < 7:
            quadrant = 'Keep Satisfied'
            strategy = 'Keep informed, don\'t overload, respond to needs'

        elif power < 7 and interest >= 7:
            quadrant = 'Keep Informed'
            strategy = 'Regular updates, involve in details, champions'

        else:
            quadrant = 'Monitor'
            strategy = 'Occasional updates, don\'t spend too much time'

        return {
            'name': name,
            'power': power,
            'interest': interest,
            'quadrant': quadrant,
            'engagement_strategy': strategy
        }

    def create_stakeholder_map(self, decision: str) -> list:
        """Example stakeholder mapping for Ray migration"""

        stakeholders = [
            # Key Players (High Power, High Interest)
            self.map_stakeholder('VP Engineering', power=10, interest=8),
            self.map_stakeholder('ML Platform Lead', power=9, interest=10),
            self.map_stakeholder('SRE Manager', power=8, interest=9),

            # Keep Satisfied (High Power, Low Interest)
            self.map_stakeholder('CTO', power=10, interest=4),
            self.map_stakeholder('Finance Director', power=7, interest=5),

            # Keep Informed (Low Power, High Interest)
            self.map_stakeholder('ML Scientists', power=5, interest=10),
            self.map_stakeholder('Data Engineers', power=4, interest=8),

            # Monitor (Low Power, Low Interest)
            self.map_stakeholder('Frontend Team', power=3, interest=2),
        ]

        return stakeholders

# Example usage
analysis = StakeholderAnalysis()
stakeholders = analysis.create_stakeholder_map("Ray Train Migration")

print("Stakeholder Map for Ray Migration:\n")
for s in stakeholders:
    print(f"{s['name']:<20} [{s['quadrant']}]")
    print(f"  Strategy: {s['engagement_strategy']}\n")
```

### Understanding Motivations

```python
class MotivationAnalysis:
    """Understanding what stakeholders really care about"""

    def analyze_motivations(self, stakeholder: str, role: str) -> dict:
        """What drives different stakeholders"""

        motivations = {
            'Engineering Manager': {
                'cares_about': [
                    'Team velocity and productivity',
                    'Team morale and retention',
                    'Delivery predictability',
                    'Technical debt management'
                ],
                'fears': [
                    'Team overwhelmed with new tech',
                    'Schedule slips',
                    'Losing key engineers',
                    'Failure reflects on them'
                ],
                'convince_with': [
                    'Team productivity gains',
                    'Reduced operational burden',
                    'Clear migration plan with milestones',
                    'Training and support'
                ]
            },

            'VP Engineering': {
                'cares_about': [
                    'Strategic value and competitive advantage',
                    'Cost efficiency and ROI',
                    'Organizational scalability',
                    'Risk management'
                ],
                'fears': [
                    'Large investment with unclear return',
                    'Organizational disruption',
                    'Vendor lock-in',
                    'Board questions about spending'
                ],
                'convince_with': [
                    'Business impact and ROI',
                    'Competitive advantage',
                    'Risk mitigation plan',
                    'Alignment with company strategy'
                ]
            },

            'SRE Manager': {
                'cares_about': [
                    'System reliability and uptime',
                    'Operational simplicity',
                    'Monitoring and observability',
                    'Incident reduction'
                ],
                'fears': [
                    'New complexity and failure modes',
                    'Operational burden on team',
                    'Insufficient monitoring',
                    'Getting paged more'
                ],
                'convince_with': [
                    'Operational improvements',
                    'Better fault tolerance',
                    'Comprehensive monitoring plan',
                    'Runbook and training'
                ]
            },

            'ML Scientist': {
                'cares_about': [
                    'Experiment velocity',
                    'Model quality and capabilities',
                    'Ease of use',
                    'Research freedom'
                ],
                'fears': [
                    'Complicated new workflow',
                    'Slower experimentation',
                    'Loss of flexibility',
                    'Having to learn infrastructure'
                ],
                'convince_with': [
                    'Faster training times',
                    'Ability to train larger models',
                    'Minimal code changes',
                    'Good documentation and examples'
                ]
            }
        }

        return motivations.get(role, {
            'cares_about': ['Unknown'],
            'fears': ['Unknown'],
            'convince_with': ['Understand their motivations first!']
        })

# Example: Tailoring message to stakeholder
analysis = MotivationAnalysis()

vp_motivations = analysis.analyze_motivations('VP Eng', 'VP Engineering')
print("VP Engineering Motivations:")
print(f"Cares about: {', '.join(vp_motivations['cares_about'])}")
print(f"Fears: {', '.join(vp_motivations['fears'])}")
print(f"Convince with: {', '.join(vp_motivations['convince_with'])}")
```

## Building Alignment Early

The best time to build consensus is before you've made a decision.

### The 1-on-1 Pre-Sell

```python
class PreSellStrategy:
    """Building consensus before formal proposal"""

    def one_on_one_approach(self, stakeholder: dict, proposal: dict) -> dict:
        """Pre-sell strategy for individual stakeholders"""

        return {
            'preparation': [
                f"Research {stakeholder['name']}'s past positions",
                f"Understand their current challenges",
                f"Identify alignment with proposal",
                f"Prepare for likely objections"
            ],

            'meeting_structure': {
                'opening': f"""
                    "Thanks for your time. I'm exploring an idea to {proposal['goal']}
                    and wanted to get your input before moving forward."

                    [Note: "get your input" not "convince you"]
                """,

                'context': f"""
                    "Here's the problem I'm seeing: {proposal['problem']}"

                    [Let them confirm or add to the problem]
                """,

                'rough_idea': f"""
                    "I'm thinking {proposal['solution_rough']}. What do you think?"

                    [Present as rough idea, not finished proposal]
                """,

                'listen': """
                    Listen 80%, talk 20%
                    - What do they like?
                    - What concerns do they have?
                    - What would make this work for them?

                    Take notes, don't defend
                """,

                'incorporate': f"""
                    "That's really helpful. Based on your input, I'll make sure to:
                    - [Address their concern 1]
                    - [Incorporate their suggestion]
                    - [Consider their perspective]

                    Can I follow up with you after I refine this?"
                """,

                'ask_for_support': """
                    "If we address these concerns, would you support this?
                    Or are there other blockers?"

                    [Get conditional commitment]
                """
            },

            'outcomes': {
                'champion': 'Loves it, becomes advocate',
                'supporter': 'Supports with conditions addressed',
                'neutral': 'No objection but won\'t champion',
                'skeptic': 'Has concerns, needs more convincing',
                'blocker': 'Fundamentally opposed',
            },

            'next_steps': {
                'champion': 'Ask them to co-present with you',
                'supporter': 'Address conditions, confirm support',
                'neutral': 'Keep informed, don\'t need much time',
                'skeptic': 'Schedule follow-up, address concerns',
                'blocker': 'Understand why, find compromise or escalate'
            }
        }

# Example: Pre-selling to SRE Manager
stakeholder = {'name': 'SRE Manager', 'power': 8, 'interest': 9}
proposal = {
    'goal': 'migrate to Ray Train for distributed training',
    'problem': 'Training jobs take 5 days, blocking product roadmap',
    'solution_rough': 'distributed training with automatic fault recovery'
}

strategy = PreSellStrategy()
presell = strategy.one_on_one_approach(stakeholder, proposal)

print("Pre-sell Meeting Structure:")
print(f"\nOpening: {presell['meeting_structure']['opening']}")
print(f"\nListen Phase: {presell['meeting_structure']['listen']}")
```

### The Feedback Loop

```python
def feedback_incorporation_process() -> dict:
    """How to incorporate stakeholder feedback"""

    return {
        'step_1_collect': {
            'method': '1-on-1s with key stakeholders',
            'capture': [
                'Concerns and objections',
                'Suggestions and improvements',
                'Conditions for support',
                'Hard blockers vs preferences'
            ],
            'example': """
                After talking to SRE team:
                - Concern: Operational complexity
                - Suggestion: Comprehensive runbook
                - Condition: 3-month pilot before full rollout
                - Blocker: None (conditional support)
            """
        },

        'step_2_analyze': {
            'categorize': [
                'Must address (blockers)',
                'Should address (major concerns)',
                'Could address (nice to have)',
                'Won\'t address (out of scope)'
            ],
            'example': """
                Must: Comprehensive runbook (SRE blocker)
                Should: 3-month pilot (reduces risk)
                Could: Multi-cloud support (future)
                Won't: Support Horovod too (scope creep)
            """
        },

        'step_3_incorporate': {
            'update_proposal': 'Revise based on must/should feedback',
            'be_transparent': """
                "Thanks for feedback from SRE, ML team, and leadership.
                Here's what I've incorporated:

                ✅ Added comprehensive runbook (SRE request)
                ✅ Extended pilot to 3 months (risk mitigation)
                ✅ Added cost monitoring (Finance request)

                📋 Parking lot for future:
                - Multi-cloud support (revisit Q3)
                - Advanced features (based on pilot learnings)

                ❌ Won't pursue:
                - Supporting both Ray and Horovod (too complex)
            """
        },

        'step_4_credit': {
            'acknowledge': 'Give credit for ideas publicly',
            'example': """
                "The comprehensive runbook was Sarah (SRE)'s idea, and
                it makes this much more operational. The extended pilot
                was Mark (VP Eng)'s suggestion to reduce risk."

                [People support what they helped create]
            """
        },

        'step_5_reconfirm': {
            'action': 'Circle back to each stakeholder',
            'template': """
                "I've updated the proposal based on your feedback:
                - [Change 1 addressing their concern]
                - [Change 2 incorporating their idea]

                Does this address your concerns?
                Can I count on your support?"

                [Get explicit commitment]
            """
        }
    }

process = feedback_incorporation_process()
for step_name, step_details in process.items():
    print(f"\n{step_name.upper()}:")
    if 'example' in step_details:
        print(step_details['example'])
```

## Handling Disagreement

Disagreement is normal and healthy. Handle it constructively.

### The Disagree and Commit Framework

```python
class DisagreeAndCommit:
    """Amazon's framework for moving forward despite disagreement"""

    def execute_framework(self, disagreement: dict) -> dict:
        """How to disagree and commit"""

        return {
            'phase_1_disagree_openly': {
                'principle': 'Have strong opinions, loosely held',
                'actions': [
                    'Voice your perspective clearly',
                    'Provide data and reasoning',
                    'Listen to counterarguments',
                    'Debate vigorously but respectfully'
                ],
                'example': """
                    "I believe we should use Horovod instead of Ray Train because:
                    1. Lower overhead (5% vs 10%)
                    2. Battle-tested at Uber scale
                    3. Team has more Horovod experience

                    However, I understand the fault tolerance concern.
                    Let's look at the data together."
                """
            },

            'phase_2_decide_mechanism': {
                'options': [
                    'Data-driven: Run benchmark, let results decide',
                    'Expert-driven: Domain expert makes final call',
                    'Leader-driven: Manager/director decides',
                    'Consensus: Discuss until agreement',
                    'Vote: Democratic decision'
                ],
                'recommendation': 'Agree on HOW to decide before debating WHAT to decide'
            },

            'phase_3_commit_fully': {
                'once_decided': [
                    'Support the decision publicly',
                    'Execute as if it was your idea',
                    'Don\'t undermine or sabotage',
                    'Give it a genuine chance to succeed'
                ],
                'example': """
                    Decision: Go with Ray Train (not my preference)

                    My public stance:
                    "We've decided on Ray Train. While I initially preferred Horovod,
                    the fault tolerance benefits are compelling. I'm committed to
                    making this migration successful. Here's how I can help..."

                    [Not: "Well, they decided Ray, so I guess we're doing that"]
                """
            },

            'phase_4_review_later': {
                'track_concerns': 'Document what you were worried about',
                'review_mechanism': 'Set review date to assess decision',
                'learn': 'If you were right, understand why. If wrong, update model.',
                'example': """
                    "After 6 months with Ray Train:
                    - My concern about overhead was valid (10% measured)
                    - My concern about complexity was not (team adapted quickly)
                    - The fault tolerance benefit exceeded expectations

                    Learning: I underweighted operational benefits vs performance"
                """
            },

            'when_not_to_commit': {
                'ethical_issues': 'Security, safety, legal, moral concerns',
                'career_limiting': 'Would require lying or compromising values',
                'example': """
                    Appropriate to not commit:
                    - "This approach has security vulnerabilities" → Escalate
                    - "This violates data privacy laws" → Stop and escalate

                    Not appropriate:
                    - "I don't like this technology" → Commit anyway
                """
            }
        }

# Example usage
framework = DisagreeAndCommit()
result = framework.execute_framework({})

print("Disagree and Commit Framework:\n")
print("Phase 1: Disagree Openly")
print(result['phase_1_disagree_openly']['example'])
print("\nPhase 3: Commit Fully")
print(result['phase_3_commit_fully']['example'])
```

### Conflict Resolution Techniques

```python
class ConflictResolution:
    """Techniques for resolving technical disagreements"""

    def five_whys_for_disagreement(self, surface_disagreement: str) -> list:
        """Dig deeper to find root cause of disagreement"""

        return [
            {
                'level': 1,
                'question': f'Why do we disagree about {surface_disagreement}?',
                'answer': 'You want Ray, I want Horovod'
            },
            {
                'level': 2,
                'question': 'Why do you want Ray over Horovod?',
                'answer': 'Because our jobs run on spot instances'
            },
            {
                'level': 3,
                'question': 'Why does spot instance matter?',
                'answer': 'We need fault tolerance to save cost'
            },
            {
                'level': 4,
                'question': 'Why is cost savings the priority?',
                'answer': 'Budget cut, need to do more with less'
            },
            {
                'level': 5,
                'question': 'Why was budget cut?',
                'answer': 'Company is optimizing for profitability this year',
                'insight': """
                    ROOT CAUSE: We're optimizing for different things!
                    - You: Cost (due to budget pressure)
                    - Me: Performance (unaware of budget constraint)

                    Resolution: Now that I understand budget pressure,
                    Ray makes sense. Or we find a way to get both
                    (spot instances with Horovod + custom fault tolerance)
                """
            }
        ]

    def interest_based_negotiation(self) -> dict:
        """Focus on interests, not positions"""

        return {
            'positions_vs_interests': {
                'definition': """
                    Position: What someone says they want
                    Interest: Why they want it (underlying need)
                """,
                'example': """
                    Position: "We MUST use Kubernetes"
                    Interest: "We need auto-scaling and easy deployment"

                    → Kubernetes is ONE way to meet interests, not the only way
                """
            },

            'technique': {
                'step_1': 'Identify both parties\' interests',
                'step_2': 'Find shared interests',
                'step_3': 'Brainstorm solutions that meet BOTH interests',
                'step_4': 'Evaluate options against shared criteria'
            },

            'example_application': """
                Disagreement: Ray vs Horovod

                Person A interests:
                - Cost efficiency (budget pressure)
                - Fault tolerance (spot instances)
                - Fast time to market

                Person B interests:
                - Maximum performance
                - Team expertise (knows Horovod)
                - Operational simplicity

                Shared interests:
                - System works reliably
                - Team can support it
                - Meets business needs

                Creative solutions:
                1. Ray with performance optimization (meets both)
                2. Horovod + custom fault tolerance (hybrid)
                3. Pilot both, let data decide (experimental)
                4. Ray now, optimize later (pragmatic)

                → Focus on interests unlocks creative solutions
            """
        }

# Example: Using five whys
resolver = ConflictResolution()
whys = resolver.five_whys_for_disagreement("which framework to use")

print("Five Whys Analysis:\n")
for why in whys:
    print(f"Level {why['level']}: {why['question']}")
    print(f"  Answer: {why['answer']}")
    if 'insight' in why:
        print(f"\n  INSIGHT: {why['insight']}")
```

## Facilitation Techniques

As a senior engineer, you'll often facilitate discussions and decisions.

### Meeting Facilitation

```python
class MeetingFacilitation:
    """Techniques for facilitating effective decision meetings"""

    def facilitate_decision_meeting(self) -> dict:
        """Structure for facilitated decision meeting"""

        return {
            'before_meeting': {
                'agenda': """
                    # Ray vs Horovod Decision Meeting
                    **Duration**: 60 minutes
                    **Goal**: Decide on distributed training framework

                    ## Agenda:
                    1. Context & constraints (5 min) - Facilitator
                    2. Option A: Ray (10 min) - Proponent
                    3. Option B: Horovod (10 min) - Proponent
                    4. Q&A and discussion (20 min) - All
                    5. Decision process (5 min) - Facilitator
                    6. Decide (5 min) - Decision maker
                    7. Next steps (5 min) - Facilitator
                """,

                'pre_reading': 'Send 1-page summary of each option 24h before',
                'ground_rules': """
                    1. Listen to understand, not to respond
                    2. Focus on interests, not positions
                    3. Debate ideas, not people
                    4. Time-box discussions (use timer)
                    5. Facilitator keeps us on track
                """
            },

            'during_meeting': {
                'facilitator_role': [
                    'Keep discussion on track and on time',
                    'Ensure everyone is heard',
                    'Capture decisions and action items',
                    'Manage conflicts neutrally',
                    'Summarize key points'
                ],

                'techniques': {
                    'round_robin': """
                        "Let's go around the room. Everyone share one concern.
                        No responses yet, just listen and capture."

                        [Ensures quieter voices heard]
                    """,

                    'parking_lot': """
                        "That's a good point, but out of scope for this decision.
                        I'm adding it to the parking lot. We'll address it separately."

                        [Keeps meeting focused]
                    """,

                    'silent_writing': """
                        "Everyone take 3 minutes to write down your top 3 criteria
                        for this decision. Then we'll share and consolidate."

                        [Prevents groupthink, gets authentic input]
                    """,

                    'spectrum_mapping': """
                        "On a scale of 1-10, how important is cost vs performance?
                        Put your name on this virtual spectrum."

                        [Visualizes where people stand]
                    """,

                    'decision_making_clarity': """
                        "To be clear: We're using an expert-driven decision.
                        Sarah (our Ray expert) will decide after hearing input.
                        Everyone's input matters, but Sarah has final say."

                        [Prevents surprise about how decision is made]
                    """
                }
            },

            'handling_difficult_situations': {
                'dominating_speaker': """
                    "Thanks John for that input. I want to make sure we hear
                    from others. Let me pause you there and get Mary's perspective."
                """,

                'side_conversations': """
                    "I'm noticing some side conversations. Can we bring those
                    to the main discussion? What are you discussing?"
                """,

                'stuck_in_details': """
                    "We're getting deep into implementation details. Let's zoom
                    out to the decision at hand. We can tackle implementation
                    details once we decide the approach."
                """,

                'personal_attack': """
                    "Wait, let's pause. We're here to debate ideas, not people.
                    Can you rephrase that as a technical concern?"
                """,

                'circular_argument': """
                    "I'm noticing we're revisiting the same points. Let me
                    summarize what I've heard, and let's see if there's new
                    information to consider."
                """
            },

            'closing': {
                'summarize_decision': """
                    "Here's what we decided:
                    - Framework: Ray Train
                    - Rationale: Fault tolerance > performance overhead
                    - Conditions: 3-month pilot, comprehensive runbook

                    Does everyone understand the decision?"
                """,

                'confirm_commitment': """
                    "Can everyone commit to supporting this decision?
                    Even if it wasn't your preference, can you get behind it?"

                    [Get explicit commitment from each person]
                """,

                'next_steps': """
                    "Action items:
                    - Alice: Draft migration plan by Friday
                    - Bob: Set up pilot environment by next Wed
                    - Charlie: Schedule training for team

                    Next meeting: Friday 2pm to review migration plan"
                """
            }
        }

# Example: Facilitation techniques
facilitator = MeetingFacilitation()
guide = facilitator.facilitate_decision_meeting()

print("Meeting Facilitation Guide:\n")
print("GROUND RULES:")
print(guide['before_meeting']['ground_rules'])
print("\nFACILITATION TECHNIQUES:")
for technique_name, technique_example in guide['during_meeting']['techniques'].items():
    print(f"\n{technique_name}:")
    print(technique_example)
```

### Building on "Yes, and..."

```python
def yes_and_technique() -> dict:
    """Improv technique for collaborative discussions"""

    return {
        'principle': 'Accept what\'s offered, build on it (not shut down)',

        'bad_pattern_yes_but': {
            'example': """
                Person A: "We should use Ray for distributed training"
                Person B: "Yes, BUT Horovod has lower overhead"

                [Feels like rejection, defensive response]
            """,
            'effect': 'Shuts down ideas, creates adversarial dynamic'
        },

        'good_pattern_yes_and': {
            'example': """
                Person A: "We should use Ray for distributed training"
                Person B: "Yes, AND we should benchmark it against Horovod
                           to quantify the overhead trade-off"

                [Accepts idea, adds to it]
            """,
            'effect': 'Builds collaboration, generates better solutions'
        },

        'applications': {
            'brainstorming': """
                "Yes, using spot instances could save cost, AND we could
                implement automatic checkpointing to handle interruptions"
            """,

            'addressing_concerns': """
                Concern: "This will be complex to operate"
                Response: "Yes, there's operational complexity, AND we can
                          mitigate that by building a comprehensive runbook
                          and providing training"
            """,

            'finding_synthesis': """
                Opinion A: "We need maximum performance"
                Opinion B: "We need cost efficiency"
                Synthesis: "Yes, we need performance, AND we need cost
                           efficiency. What if we use Ray on spot instances
                           with fallback to on-demand for critical jobs?"
            """
        },

        'when_to_say_no': {
            'caveat': 'Yes-and doesn\'t mean accepting bad ideas',
            'approach': """
                Instead of "No, that won't work" (shutdown)
                Use "Yes, I see why you suggest that, AND I'm concerned about
                [specific issue]. What if we tried [alternative]?"

                [Acknowledge, then redirect]
            """
        }
    }

technique = yes_and_technique()
print("YES, AND Technique:\n")
print("❌ BAD (Yes, but):")
print(technique['bad_pattern_yes_but']['example'])
print("\n✅ GOOD (Yes, and):")
print(technique['good_pattern_yes_and']['example'])
```

## Getting to "Yes"

Specific tactics for securing agreement and commitment.

### The Six Principles of Influence (Cialdini)

```python
class InfluencePrinciples:
    """Cialdini's principles applied to technical leadership"""

    def __init__(self):
        self.principles = {
            'reciprocity': {
                'principle': 'People want to return favors',
                'application': """
                    Before asking for support:
                    - Help them with their problems first
                    - Share your expertise generously
                    - Make introductions and connections
                    - Review their proposals

                    When you ask for support, they feel obligation to reciprocate
                """,
                'example': """
                    Last month: Helped SRE team debug production issue (4 hours)
                    This month: Ask SRE team for support on Ray migration

                    "Remember when I helped with that Redis issue? I could use
                    your help thinking through operational concerns for Ray..."
                """
            },

            'commitment_consistency': {
                'principle': 'People want to be consistent with past commitments',
                'application': """
                    Get small commitments first, build to larger ones:

                    1. "Do you agree training is too slow?" (Yes)
                    2. "Would faster training help your team?" (Yes)
                    3. "Should we explore solutions?" (Yes)
                    4. "Ray seems promising. Worth a pilot?" (Consistent: Yes)
                """,
                'example': """
                    "Last quarter you said distributed training was a priority.
                    Ray Train directly addresses that. It aligns with your
                    stated goals. Would you support moving forward?"
                """
            },

            'social_proof': {
                'principle': 'People look to others for guidance',
                'application': """
                    Show that others are already on board:
                    - "3 teams are already using Ray successfully"
                    - "Google, OpenAI, and Uber use Ray at scale"
                    - "The ML team is excited about this"

                    [If peers are doing it, it's validated]
                """,
                'example': """
                    "I've already talked to SRE, ML team, and Data Engineering.
                    They're all supportive. Sarah (SRE) even offered to help
                    write the runbook. Would you like to join us?"
                """
            },

            'authority': {
                'principle': 'People defer to credible experts',
                'application': """
                    Establish credibility:
                    - Cite research and data
                    - Reference respected sources
                    - Demonstrate deep understanding
                    - Get expert endorsements

                    "According to our load testing..."
                    "Ray's documentation shows..."
                    "Dr. Smith (Ray creator) recommends..."
                """,
                'example': """
                    "I spent 2 weeks researching this and ran benchmarks.
                    Here's what the data shows... [charts]

                    I also consulted with Ray's solutions architect to
                    validate our approach."
                """
            },

            'liking': {
                'principle': 'People say yes to those they like',
                'application': """
                    Build rapport and connection:
                    - Find common ground (shared interests, goals)
                    - Show genuine interest in their work
                    - Praise and appreciation (genuine)
                    - Cooperative (not competitive) framing

                    "We're in this together" vs "I need you to..."
                """,
                'example': """
                    "I really appreciated your insight on the Kubernetes
                    migration last year. Your operational thinking helped
                    us avoid issues. I'd love your perspective on Ray..."

                    [Genuine appreciation + request for expertise]
                """
            },

            'scarcity': {
                'principle': 'People value scarce opportunities',
                'application': """
                    (Use ethically and sparingly!)

                    - Time-limited: "Budget available this quarter only"
                    - Unique opportunity: "Ray experts available for 2 weeks"
                    - Competitive: "Other teams adopting faster"

                    Must be genuine, not manufactured
                """,
                'example': """
                    "We have budget for Ray training this quarter, but it
                    goes away in Q3. If we want expert help getting this
                    right, we need to decide by Friday."

                    [Real deadline, not artificial pressure]
                """
            }
        }

    def apply_ethically(self) -> list:
        """Ethical guidelines for using influence"""

        return [
            'Be genuine - Don\'t manipulate',
            'Serve the project - Not personal gain',
            'Be truthful - Don\'t fabricate social proof or scarcity',
            'Respect autonomy - People can say no',
            'Disclose conflicts - Be transparent about incentives'
        ]

# Example: Using influence principles
influencer = InfluencePrinciples()

print("Reciprocity Principle:")
print(influencer.principles['reciprocity']['example'])

print("\n\nCommitment-Consistency Principle:")
print(influencer.principles['commitment_consistency']['application'])
```

## When Consensus Fails

Sometimes you can't get everyone on board. What then?

### Escalation Path

```python
class EscalationStrategy:
    """When and how to escalate decisions"""

    def should_escalate(self, situation: dict) -> dict:
        """Decision framework for escalation"""

        consensus_attempts = situation.get('consensus_attempts', 0)
        blocker_power = situation.get('blocker_power', 0)
        time_sensitive = situation.get('time_sensitive', False)
        strategic_importance = situation.get('strategic', False)

        if consensus_attempts >= 3 and blocker_power >= 7:
            return {
                'escalate': True,
                'reason': 'Multiple attempts failed, powerful blocker',
                'to_whom': 'Common manager or director',
                'approach': 'Joint escalation with blocker'
            }

        elif time_sensitive and consensus_attempts >= 1:
            return {
                'escalate': True,
                'reason': 'Time-sensitive, can\'t wait for full consensus',
                'to_whom': 'Decision maker (manager/director)',
                'approach': 'Explain urgency, ask for direction'
            }

        elif strategic_importance:
            return {
                'escalate': True,
                'reason': 'Strategic decision beyond your authority',
                'to_whom': 'VP or C-level',
                'approach': 'Provide recommendation, let them decide'
            }

        else:
            return {
                'escalate': False,
                'reason': 'Keep working on consensus',
                'next_steps': 'More stakeholder conversations, find compromise'
            }

    def escalate_gracefully(self) -> dict:
        """How to escalate without burning bridges"""

        return {
            'bad_escalation': """
                Email to VP (cc'ing everyone):
                "Bob is blocking the Ray migration for no good reason.
                Can you tell him to stop being difficult?"

                [Throws Bob under the bus, burns relationship]
            """,

            'good_escalation': """
                Joint meeting with manager (you + Bob + manager):
                "Bob and I have different perspectives on Ray vs Horovod.
                We've had 3 good discussions but haven't converged.

                We both want what's best for the team. Can you help us
                find a path forward?

                Bob, would you like to share your perspective first?"

                [Respectful, collaborative, seeking help not blame]
            """,

            'escalation_memo_template': """
                To: [Manager/Director]
                Subject: Decision Input Needed: Ray vs Horovod

                ## Situation
                We need to decide on distributed training framework.

                ## Options Considered
                - Option A: Ray Train (my recommendation)
                - Option B: Horovod (Bob's preference)

                ## Where We Align
                - Both want fault-tolerant training
                - Both want good performance
                - Both want operational simplicity

                ## Where We Disagree
                - I prioritize fault tolerance (for spot instances)
                - Bob prioritizes performance (lower overhead)

                ## Attempts at Resolution
                1. [Date]: Initial discussion - no alignment
                2. [Date]: Ran benchmarks - didn't resolve
                3. [Date]: Consulted SRE team - different views

                ## What I Need From You
                - Help us evaluate trade-offs
                - Decide based on strategic priorities
                - Set direction so we can move forward

                ## Recommendation
                I recommend Ray for [reasons], but I'm committed to
                supporting whichever decision you make.

                Can we meet (Bob + me + you) to discuss?
            """
        }

# Example: Escalation decision
strategy = EscalationStrategy()
result = strategy.should_escalate({
    'consensus_attempts': 3,
    'blocker_power': 8,
    'time_sensitive': True,
    'strategic': True
})

print("Should escalate?", result['escalate'])
print("Reason:", result['reason'])
print("Approach:", result['approach'])
```

### Moving Forward Without Full Consensus

```python
def move_forward_strategies() -> dict:
    """Strategies when you can't get everyone on board"""

    return {
        'disagree_and_commit': {
            'when': 'Disagreement but not blockers',
            'approach': """
                "I know not everyone agrees with Ray. That's OK.
                We've made the decision, and I'm asking everyone to
                commit to making it work.

                Bob, I know you preferred Horovod. Can you commit to
                giving Ray a genuine try? We'll review in 3 months."
            """
        },

        'pilot_approach': {
            'when': 'Uncertainty or risk aversion',
            'approach': """
                "Let's run a 3-month pilot:
                - Migrate 2 non-critical models to Ray
                - Keep existing Horovod for critical models
                - Measure and compare results
                - Decide to expand or rollback based on data

                Low risk, high learning. Can everyone support this?"
            """
        },

        'phased_rollout': {
            'when': 'Adoption concerns',
            'approach': """
                "We'll roll out gradually:
                - Month 1: Team training, 1 pilot model
                - Month 2: Expand to ML Platform team
                - Month 3: Open to all teams (opt-in)
                - Month 6: Make it default (with alternatives)

                Everyone can adopt at their own pace."
            """
        },

        'parallel_paths': {
            'when': 'Can afford to try multiple approaches',
            'approach': """
                "Let's support both Ray and Horovod for 6 months:
                - Team A uses Ray, Team B uses Horovod
                - Share learnings monthly
                - After 6 months, converge on winner

                Competition drives learning."
            """
        },

        'minimal_viable_consensus': {
            'when': 'Time pressure, good enough support',
            'approach': """
                "We have support from:
                - ML team (key users)
                - SRE team (key operators)
                - Engineering manager (decision maker)

                That's enough to proceed. We'll keep other teams
                informed and gather feedback as we go."
            """
        }
    }

strategies = move_forward_strategies()
print("Moving Forward Without Full Consensus:\n")
for strategy_name, strategy_details in strategies.items():
    print(f"{strategy_name.upper()}:")
    print(f"When: {strategy_details['when']}")
    print(f"Approach: {strategy_details['approach']}\n")
```

## Summary

**Building consensus is the hidden skill of senior engineers**. Technical excellence is necessary but not sufficient. You must bring people along.

### Key Principles

1. **Consensus Enables Success**
   - Best tech + no consensus = failure
   - Good tech + strong consensus = success
   - Invest in alignment, not just technical quality

2. **Choose the Right Consensus Level**
   - Command: Emergencies only
   - Consult: Gather input, expert decides
   - Consensus: Everyone agrees (high stakes)
   - Consent: No objections (routine)

3. **Understand Stakeholders**
   - Map power and interest
   - Understand motivations and fears
   - Tailor engagement strategy

4. **Build Alignment Early**
   - Pre-sell through 1-on-1s
   - Incorporate feedback genuinely
   - Give credit generously

5. **Handle Disagreement Constructively**
   - Disagree openly, commit fully
   - Focus on interests, not positions
   - Use five whys to find root cause

6. **Facilitate Effectively**
   - Neutral process management
   - Ensure all voices heard
   - Time-box discussions
   - Capture decisions clearly

7. **Influence Ethically**
   - Reciprocity, consistency, social proof
   - Authority, liking, scarcity
   - Always serve the project, not ego

8. **Escalate Gracefully**
   - When consensus fails after good attempts
   - Joint escalation with disagreer
   - Provide context and recommendation

### Remember

**Consensus is not unanimous agreement**. It's commitment to move forward together, even with reservations.

**Your job**: Get enough buy-in to succeed, not perfect agreement.

### The Ultimate Test

Can you answer "yes" to these:
- [ ] Do key stakeholders support this?
- [ ] Have objections been heard and addressed?
- [ ] Will people actively work to make this succeed?
- [ ] If it fails, will they help fix it (not say "I told you so")?

If yes → You have consensus. Proceed with confidence.

## Next Steps

- Return to [Module 210 Overview](../README.md)
- Apply stakeholder mapping to your current initiative
- Practice "yes, and" in your next meeting
- Identify one relationship to build (reciprocity)

## Additional Resources

**Books**:
- "Getting to Yes" by Fisher and Ury (Interest-based negotiation)
- "Influence" by Robert Cialdini (Six principles of influence)
- "Crucial Conversations" by Patterson et al.
- "The Secrets of Facilitation" by Michael Wilkinson

**Articles**:
- Amazon's Disagree and Commit: https://www.amazon.jobs/en/principles
- Stripe's Decision-Making Framework: https://stripe.com/blog/how-we-make-decisions
- RACI Matrix Guide: https://www.projectmanager.com/blog/raci-chart-definition-tips-and-example

**Frameworks**:
- Interest-Based Relational Approach (IBR)
- Nonviolent Communication (NVC)
- BATNA (Best Alternative To Negotiated Agreement)
