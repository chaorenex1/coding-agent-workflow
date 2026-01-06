---
description: Interactive requirements clarification and understanding with stakeholder question generation
argument-hint: [feature-name|requirement-doc|user-story]
allowed-tools: Read
---

# Requirements Understanding Assistant

## Context

Requirement to understand: $ARGUMENTS

### Available Documentation
@README.md
@CLAUDE.md
@requirements.md
@user-stories.md

## Your Task

Develop comprehensive understanding of "$ARGUMENTS" requirements:

### 1. **Initial Requirements Capture**
   - What is being requested?
   - Who are the stakeholders?
   - What is the business context?
   - What problem does this solve?

### 2. **Functional Requirements Analysis**
   - Core functionality needed
   - User workflows and interactions
   - Input/output specifications
   - Business rules and logic
   - Data requirements

### 3. **Non-Functional Requirements**
   - Performance expectations
   - Scalability needs
   - Security requirements
   - Compliance constraints
   - Availability/reliability
   - Usability standards

### 4. **Scope Definition**
   - What is IN scope?
   - What is OUT of scope?
   - What are the boundaries?
   - What are the dependencies?

### 5. **Ambiguity Identification**
   Generate clarifying questions for stakeholders:

   **Functional Clarity:**
   - [Question about unclear functionality]
   - [Question about edge cases]
   - [Question about user interaction]

   **Technical Clarity:**
   - [Question about integration points]
   - [Question about data handling]
   - [Question about performance targets]

   **Business Clarity:**
   - [Question about priorities]
   - [Question about success metrics]
   - [Question about constraints]

### 6. **Assumptions Documentation**
   - Assumed user behaviors
   - Assumed technical constraints
   - Assumed business rules
   - Assumed dependencies

### 7. **Acceptance Criteria Draft**
   - Given [precondition]
   - When [action]
   - Then [expected result]

### 8. **Risk Identification**
   - Technical risks
   - Business risks
   - Timeline risks
   - Dependency risks

## Output Format

```
📋 REQUIREMENT SUMMARY
[One-paragraph summary of the requirement]

👥 STAKEHOLDERS
- [Stakeholder 1]: [Role/Interest]
- [Stakeholder 2]: [Role/Interest]

🎯 FUNCTIONAL REQUIREMENTS
1. [Requirement 1]
2. [Requirement 2]
...

⚡ NON-FUNCTIONAL REQUIREMENTS
- Performance: [Specifics]
- Security: [Specifics]
- Scalability: [Specifics]

🔍 SCOPE
IN SCOPE:
- [Item 1]
- [Item 2]

OUT OF SCOPE:
- [Item 1]
- [Item 2]

❓ CLARIFICATION QUESTIONS
FUNCTIONAL:
1. [Question 1]
2. [Question 2]

TECHNICAL:
1. [Question 1]
2. [Question 2]

BUSINESS:
1. [Question 1]
2. [Question 2]

📝 ASSUMPTIONS
- [Assumption 1]
- [Assumption 2]

✅ ACCEPTANCE CRITERIA
Scenario 1: [Name]
- Given: [Precondition]
- When: [Action]
- Then: [Expected result]

Scenario 2: [Name]
...

⚠️ IDENTIFIED RISKS
1. [Risk 1]: [Impact and mitigation]
2. [Risk 2]: [Impact and mitigation]

🔗 DEPENDENCIES
- [Dependency 1]
- [Dependency 2]
```

## Success Criteria

- ✅ Clear understanding of core requirement
- ✅ Functional and non-functional requirements identified
- ✅ Scope clearly defined
- ✅ Ambiguities identified with clarifying questions
- ✅ Assumptions documented
- ✅ Acceptance criteria drafted
- ✅ Risks and dependencies identified
