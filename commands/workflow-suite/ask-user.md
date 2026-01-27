---
description: Interactive question generation for requirements clarification and decision making
argument-hint: [topic|decision-point|ambiguity]
allowed-tools: Read
---

# Interactive User Question Assistant

## Context

Topic for clarification: $ARGUMENTS

## Iterative Question Generation Framework

Follow this refinement cycle to generate targeted questions:

1. **[Scan]** What do I understand initially?
   - Parse the topic/requirement
   - Identify what's clear vs. ambiguous
   - Detect implied assumptions
   - Output: Initial Understanding Assessment

2. **[Identify Gaps]** What's missing or unclear?
   - Find ambiguous terms
   - Spot missing details
   - Locate contradictory statements
   - Output: Gap Inventory

3. **[Prioritize]** What questions matter most?
   - Critical blockers: Must ask first
   - Important details: Should ask soon
   - Nice-to-know: Can ask later
   - Output: Prioritized Question Queue

4. **[Generate]** How should I phrase questions?
   - Make specific, not vague
   - Make actionable, answers lead to decisions
   - Make open-ended where exploration needed
   - Output: Draft Questions

5. **[Refine]** Are these questions effective?
   - Review: Will answers move project forward?
   - Edit: Combine overlapping questions
   - Validate: Each question has clear purpose
   - Output: Final Question Set

### Iteration Strategy
- Round 1: High-level understanding (What, Why, Who)
- Round 2: Technical details (How, What if, Constraints)
- Round 3: Edge cases and validation (What about X, What happens when)

## Your Task

Generate targeted, high-quality questions to clarify "$ARGUMENTS":

### Question Generation Strategy

For the given topic, create questions across multiple dimensions:

### 1. **Functional Clarification**
   Generate questions about:
   - Expected behavior and outcomes
   - User interactions and workflows
   - Edge cases and exceptions
   - Input/output specifications
   - Business rules and logic

### 2. **Technical Decisions**
   Generate questions about:
   - Technology choices
   - Architecture approaches
   - Integration methods
   - Performance targets
   - Security requirements

### 3. **Scope & Priorities**
   Generate questions about:
   - What's in/out of scope
   - Must-have vs nice-to-have
   - Release priorities
   - Timeline constraints
   - Resource availability

### 4. **User Experience**
   Generate questions about:
   - Target users and personas
   - User workflows
   - Accessibility requirements
   - Error handling and feedback
   - Help and documentation needs

### 5. **Data & Business Logic**
   Generate questions about:
   - Data sources and ownership
   - Validation rules
   - Business calculations
   - State transitions
   - Audit and compliance

### 6. **Integration & Dependencies**
   Generate questions about:
   - External systems to integrate
   - Data synchronization needs
   - API contracts
   - Authentication/authorization
   - Error handling for integrations

### 7. **Quality & Testing**
   Generate questions about:
   - Acceptance criteria
   - Testing requirements
   - Performance benchmarks
   - Security testing needs
   - Monitoring and alerting

### 8. **Operations & Maintenance**
   Generate questions about:
   - Deployment strategy
   - Rollback procedures
   - Monitoring requirements
   - Support procedures
   - Documentation needs

## Question Quality Guidelines

Each question should be:
- **Specific**: Not vague or overly broad
- **Actionable**: Answer leads to concrete decision
- **Relevant**: Directly related to the topic
- **Clear**: Easy to understand
- **Open-ended**: Encourages detailed answers (where appropriate)

## Output Format

```
🔍 QUESTION GENERATION PROCESS
Initial Understanding:
- Clear: [What's understood]
- Ambiguous: [What's unclear]
- Assumptions detected: [List]

Gap Analysis:
- Missing details: [List]
- Contradictions: [List]
- Need clarification: [List]

📋 CLARIFICATION QUESTIONS FOR: $ARGUMENTS

🎯 FUNCTIONAL REQUIREMENTS
1. [Specific functional question]
2. [Edge case question]
3. [User interaction question]

⚙️ TECHNICAL DECISIONS
1. [Architecture question]
2. [Technology choice question]
3. [Performance question]

📊 SCOPE & PRIORITIES
1. [Scope boundary question]
2. [Priority question]
3. [Timeline question]

👥 USER EXPERIENCE
1. [User persona question]
2. [Workflow question]
3. [Accessibility question]

💾 DATA & BUSINESS LOGIC
1. [Data model question]
2. [Validation rule question]
3. [Business logic question]

🔗 INTEGRATION & DEPENDENCIES
1. [Integration method question]
2. [API contract question]
3. [Error handling question]

✅ QUALITY & TESTING
1. [Acceptance criteria question]
2. [Testing approach question]
3. [Performance benchmark question]

🚀 OPERATIONS
1. [Deployment question]
2. [Monitoring question]
3. [Support question]

🎲 DECISION MATRIX (for key decisions)
Decision: [What needs to be decided]

Option A: [Option name]
Pros: [Benefits]
Cons: [Drawbacks]
When to choose: [Scenarios]

Option B: [Option name]
Pros: [Benefits]
Cons: [Drawbacks]
When to choose: [Scenarios]

Recommendation: [Your recommendation with reasoning]

💡 SUGGESTED NEXT STEPS
After answering these questions:
1. [Next step 1]
2. [Next step 2]
3. [Next step 3]
```

## Question Prioritization

Mark questions by priority:
- 🔴 **CRITICAL**: Must answer before proceeding
- 🟡 **IMPORTANT**: Should answer soon
- 🟢 **NICE-TO-KNOW**: Can answer later

## Success Criteria

- ✅ Questions cover all relevant dimensions
- ✅ Questions are specific and actionable
- ✅ Critical questions clearly identified
- ✅ Decision options presented where applicable
- ✅ Next steps suggested based on answers
- ✅ Questions enable informed decision-making
