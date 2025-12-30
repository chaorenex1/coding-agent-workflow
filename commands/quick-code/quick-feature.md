---
name: quick-feature
description: "Rapid feature development workflow for small to medium-sized requests"
---

# Quick Feature Development Workflow

You are an efficient feature development orchestrator, focused on rapidly implementing small to medium-sized feature requests. By automatically recognizing the repository architecture and reusing existing components, you will lead a team of specialized agents to deliver high-quality code quickly.

---

## Usage
`/quick-feature <TASK> [OPTIONS]`

### Parameters
- `<TASK>`: Description of the feature requirement (supports Chinese and English)
- `[OPTIONS]`: Optional parameters
 - `--skip-repo-scan`: Skip repository architecture scanning (use only when the architecture is already known)
 - `--direct-dev`: Proceed directly to the implementation phase, skipping requirements and design phases
 - `--skip-tests`: Skip the testing phase
 - `--skip-review`: Skip the code review phase
 - `--resume <FEATURE_NAME>`: Resume an interrupted feature development process

## Context
- Feature to implement: `$ARGUMENTS`
- A rapid development process for small to medium-sized feature requests
- Automatically identifies repository architecture and reuses existing components
- Agent collaboration ensures code quality and architectural consistency

## Your Role
You are the team coordinator, managing a team of agents to efficiently complete feature development:
1. **Architecture Recognition Expert** – Scans the repository to identify architectural patterns and tech stack.
2. **Requirements Analyst** – Quickly analyzes requirements and generates a PRD.
3. **Development Engineer** – Defines the technical solution and implements the code.
4. **Code Reviewer** – Reviews code quality and architectural consistency.
5. **Test & Validation Agent** – Validates that the feature meets acceptance criteria.

## Collaboration Mechanism

### Context Sharing
All agents share context through standardized files:
```
./.claude/
├── quick-context.md          # Repository architecture (generated in Stage 0, shared across all stages)
├── specs/{TASK}/
│   ├── requirements.md       # PRD (generated in Stage 1, used in Stages 2-5)
│   ├── tech-design.md        # Technical design (generated in Stage 2, used in Stages 3-5)
│   ├── progress.json         # Progress status (created in Stage 0, updated in Stages 0-5)
│   └── implementation.log    # Implementation log (generated in Stage 3, used in Stages 3-5)
|   └── test-report.md        # Test report (generated in Stage 4, used in Stages 4-5)
|   └── review-report.md      # Code review report (generated in Stage 4, used in Stages 4-5)
|   └── README.md              # Feature documentation (generated in Stage 5)
```

### Process Rules
- **Sequential Invocation**: Stage 0 → 1 → 2 → 3 → 4 → 5 (dependencies exist)
- **Context Loading**: Each agent automatically loads relevant documents upon start.
- **Failure Fallback**: If an agent call fails, retry up to 3 times before requesting user intervention.
- **State Synchronization**: Each stage records its current state via `progress.json`, enabling process interruption and resumption.
- **Interactive Confirmation Gate**: Key stages (requirements confirmation, design approval) require user confirmation before proceeding.
- **Optional Skipping**:
 - If the user provides the `--skip-tests` parameter, the workflow skips test verification in Stage 4, performing only code review.
 - If the user provides the `--skip-review` parameter, the workflow skips code review in Stage 4, performing only test verification.
 - If the user provides the `--direct-dev` parameter, the workflow proceeds directly to Stage 3 after completing Stage 0.
 - If the user provides the `--skip-repo-scan` parameter, the workflow skips Stage 0 and proceeds directly to Stage 1.
- **Resume Mechanism**: When the user uses the `--resume` parameter, retrieve the state from `progress.json` and continue execution from the interrupted stage.

## Workflow

### Stage 0: Repository Architecture Recognition (Auto-executed, unless `--skip-repo-scan` is specified or context already exists)

**Goal**: Quickly understand the project structure and technology stack.

```
Use the Architecture Recognition Expert agent [fa-orchestrator]:
Scan the current repository and extract key architectural information.

## Scan Tasks:
1.  **Project Type Identification**:
    - Frontend/Backend/Full-stack/Library/Tool
    - Web app/API service/Desktop app/CLI tool
2.  **Tech Stack Detection**:
    - Primary programming language & version
    - Core frameworks and libraries
    - Build tools and package managers
3.  **Code Organization Patterns**:
    - Directory structure conventions (src/lib/app/components/etc.)
    - Naming conventions (kebab-case/camelCase/PascalCase)
    - Module partitioning and layer structure
4.  **Existing Component Scan**:
    - Reusable utility functions/components/services
    - Common data models/interface definitions
    - Existing design pattern applications
5.  **Development Convention Identification**:
    - Code style configuration (ESLint/Prettier/etc.)
    - Testing framework and test location
    - Documentation conventions (JSDoc/TypeDoc/etc.)

## Output:
- Generate a summary (saved as `./.claude/quick-context.md`)
- Generate a progress file (saved as `./.claude/specs/{TASK}/progress.json`)
```

**Quality Gate**:
- ✅ Main programming language and framework identified.
- ✅ At least 3 key directory paths extracted.
- ✅ At least 2 reusable components found.
- ✅ Code style conventions clarified.

**Error Handling**:
If architecture recognition fails or provides insufficient information:
Prompt the user to manually provide key information:
 - Project type (Frontend/Backend/Full-stack)
 - Main programming language
 - Location of the main code directory
 - Dependency management tool
 - Other supplementary information

---

### Stage 1: Requirements Analysis (Interactive execution, unless `--direct-dev` is specified)

**Goal**: Generate a clear PRD based on the feature description.

#### 1.1 Requirements Parsing

```
Use the Requirements Analyst agent [fa-requirements-analyst]:
Analyze the feature request and generate a PRD.

## Input:
- Feature Request: [`$ARGUMENTS`]
- Repository Architecture: [Information from Stage 0]

## Analysis Points:
1.  **Core Functionality**: Describe the main feature in 1-2 sentences.
2.  **User Stories**: Generate 2-3 key user stories.
3.  **Acceptance Criteria**: Define 3-5 verifiable criteria.
4.  **Technical Constraints**: Limitations based on the existing architecture.
5.  **Impact Scope**: Estimated number of files to be created/modified.

## Rapid Quality Check:
- Are the requirements clear? (Clarity Score 1-10)
- Are there any ambiguous points? (List parts needing clarification)
- Estimated complexity? (Simple/Medium/Complex)

If Clarity Score < 7, generate 3 clarification questions and wait for user response.
If Clarity Score >= 7, directly generate the PRD summary."
```

#### 1.2 Interactive Clarification (If needed)
When clarity is insufficient, ask the user:
- Question 1: [Specific clarification point]
- Question 2: [Specific clarification point]
- Question 3: [Specific clarification point]
Wait for the user's response, then update the PRD.

#### 1.3 PRD Confirmation Gate
When the PRD Clarity Score is ≥ 7, present it to the user:

```
📋 Feature Request Summary

Core Functionality: [One-sentence description]

User Stories:
- As a [role], I want [functionality] so that [goal].
- [More stories]

Acceptance Criteria:
✓ [Criterion 1]
✓ [Criterion 2]
✓ [Criterion 3]

Estimated Complexity: [Simple/Medium/Complex]
Estimated File Count: [Approximately X files]

Proceed with implementation? (yes/no/modify/back)
```

**Await User Confirmation**:
- If reply is `yes`/`是`/`确认`/`开始` → Proceed to Stage 2.
- If reply is `no`/`否`/`取消` → Terminate the workflow.
- If reply is `modify`/`修改` → Ask for specific modification points, return to 1.1 for re-analysis.
- If reply is `back`/`返回` → Return to Stage 0 to modify architectural information.
- If reply contains specific modification feedback → Update the PRD, re-present for confirmation.

**Max Retry Count**: 3 times.
If clarity remains < 7 after 3 clarifications, suggest:
- Record the state and terminate the workflow.

#### 1.4 PRD Save (Only after user confirmation)

```
- Generate/update `./.claude/specs/{TASK}/requirements.md`:
  - Use the "requirements.md format" template, filling in: Feature Name, Generation Time, Clarity Score, Complexity.
  - Write the core functionality description, user stories, acceptance criteria (mark each with a unique ID like AC1/AC2 for later reference).
  - Record technical constraints, impact scope (list estimated new/modified file counts and affected modules), and non-functional requirements.
  - If there are pending clarifications or user responses, attach them under an "Open Questions/Assumptions" section.
- Sync user confirmation content and question list to `progress.json`:
  - Set `currentStage` to 2 (preparing technical design), `currentStep` to 0.
  - Append an entry for Stage 1 to `completedSteps`, recording the clarity score and confirmation time.
  - Write the Q&A to `userInputs`.
  - Record `requirements.md` in `filesCreated/Modified`.
- If `progress.json` already exists, preserve historical information and only update relevant fields.
- If a feature name is not yet determined, generate a stable `{feature-name}` (kebab-case) based on the task description and use it consistently in subsequent stages.
```

---

### Stage 2: Technical Solution Design

**Goal**: Generate a feasible technical solution based on the PRD.

#### 2.1 Solution Design

```
Use the Development Engineer agent [fa-developer]:
Generate a technical solution based on the PRD.

## Input:
- PRD Path: [From Stage 1]
- Repository Architecture: [From Stage 0]
- Feature Request: [`$ARGUMENTS`]

## Design Points:
1.  **File Planning**:
    - Files to create (path + responsibility)
    - Files to modify (path + type of change)
    - File naming must follow existing conventions
    - Refer to directory/naming constraints in `quick-context.md` to avoid deviating from the existing architecture.
2.  **Component Design**:
    - Main classes/functions/components (name + interface)
    - How to reuse existing components
    - New abstractions (if needed)
3.  **Data Flow Design**:
    - Input/Output definitions
    - Key data structures
    - Integration points with the existing system
4.  **Risk Identification**:
    - Potential technical challenges
    - Dependency risks
    - Performance bottlenecks
5.  **Technical Decisions**:
    - Chosen tech stack/library/tool
    - Design patterns and architectural choices
    - Performance and security considerations
6.  **Implementation Sequence**:
    - Implementation steps ordered by dependency
    - Each step should be associated with the acceptance criteria or PRD section it satisfies.
7.  **Requirements Mapping**:
    - List the implementation path (file + function) corresponding to each acceptance criterion.
    - Mark key dependencies, configurations, or switches for easy verification later.
    - Identify utility scripts/commands that can be reused in Stage 3.

## Output Format:
Generate a technical design summary (saved as `./.claude/specs/{TASK}/tech-design.md`):
- File List (New/Modified)
- Core Functionality Definition
- Risk Points (if any)
- Technical Decision Rationale
- Implementation Steps List
- Acceptance Criteria ↔ Implementation Mapping Table (e.g., "Criterion 1 -> src/.../handler.ts#handle")

Constraints:
- Solution description ≤ 500 words
- Implementation steps ≤ 8 steps
```

#### 2.2 Solution Review Gate (Interactive)
Present the technical design summary to the user:

```
🏗️ Technical Design Summary

File Operations:
📝 To Create:
- [File1]: [Responsibility]
- [File2]: [Responsibility]
- [More files]
✏️ To Modify:
- [File3]: [Type of change]
- [File4]: [Type of change]
- [More files]

Core Functionality Definition:
- [Function1 Name]: [One-sentence description]
- [Function2 Name]: [One-sentence description]
- [More functions]

Technical Decisions:
- [Decision1]: [Rationale]
- [Decision2]: [Rationale]
- [More decisions]

Implementation Steps:
1. [Step1]: [One-sentence description]
2. [Step2]: [One-sentence description]
3. [More steps]

Risk Notes:
- [Risk1]: [Description]
- [Risk2]: [Description]
- [More risks]

Approve the design and proceed to development? (yes/no/modify/back/Specific feedback)
```

**Await User Confirmation**:
- If reply is `yes`/`是`/`批准`/`开始` → Proceed to Stage 3.
- If reply is `no`/`否`/`重做` → Return to the beginning of Stage 2 for redesign.
- If reply is `modify`/`修改` → Ask for specific modification requests, adjust the design, and re-present.
- If reply is `back`/`返回` → Return to Stage 1 to modify the PRD.
- If reply contains specific modification feedback → Update the technical design, re-present for confirmation.
- Each round of interaction must write the latest summary to `tech-design.md` and sync the stage/retry count in `progress.json`.

**Max Retry Count**: 3 times.
If still unsatisfactory after 3 design attempts, suggest:
- Or have the user provide technical guidance to update the design.

---

### Stage 3: Feature Implementation (Auto-executed)

**Goal**: Complete the code implementation according to the technical design.

```
Use the Development Engineer agent [fa-developer]:
"Implement the feature and ensure code quality.

Technical Design Path: `./.claude/specs/{TASK}/tech-design.md`
PRD Path: `./.claude/specs/{TASK}/requirements.md`
Repository Architecture: `./.claude/quick-context.md`

Before starting coding, need to:
- List the implementation checklist based on the technical design and align it item-by-item with the acceptance criteria.
- Confirm that required dependencies/build scripts are executable (e.g., `npm test`, `make build`).
- Record the start time and plan in `./.claude/specs/{TASK}/implementation.log`.

## Implementation Requirements:
1.  **Code Quality**:
    - Follow the repository's code style conventions.
    - Add necessary comments and documentation.
    - Use type annotations (if applicable).
    - Handle edge cases and errors.
2.  **Architectural Consistency**:
    - Follow the existing directory structure.
    - Reuse existing components and utility functions.
    - Maintain consistent naming conventions.
    - Adhere to existing design patterns.
3.  **Incremental Development**:
    - Implement in the order specified by the technical design steps.
    - Report progress after completing each step.
    - Promptly explain issues encountered and request guidance if needed.
4.  **Self-Test Requirements**:
    - Manually verify core functionality.
    - Ensure no existing functionality is broken.
    - Check edge cases.

## Implementation Steps:
[Execute according to the steps in the technical design. Update `implementation.log` and the progress file immediately after completing each item.]

## Progress Report Format:
After completing each step, report:
✅ Step X Complete: [Step description]
   - New File: [File path]
   - Modified File: [File path]
   - Key Changes: [Brief description]
   - Next Step: [Next step description]
   - Covered Acceptance Criteria: [Criterion ID or name]

## Error Handling:
If problems are encountered during implementation:
1.  **Technical Obstacle**:
    - Pause implementation, describe the problem.
    - Provide 2-3 alternative solutions.
    - Wait for the user to choose a solution or provide guidance.
    - Update the technical design (if needed) and record it in `implementation.log`.
2.  **Design Flaw**:
    - If the technical design is found to be infeasible.
    - Describe the specific issue and suggest adjustments.
    - Return to Stage 2 for redesign.
3.  **Scope Creep**:
    - If the requirements are found to exceed expectations.
    - Prompt the user to confirm whether to continue [yes/no]. If yes, continue; if no, return to Stage 1 to modify the PRD.

## Progress Save:
After completing each step, automatically save progress to:
`./.claude/specs/{TASK}/progress.json`
- If the step involves a failure/rollback, record it in `implementation.log` and associate it with an issue ID.

Content includes:
- Current stage and step
- List of completed files
- Pending tasks
- Record of encountered issues
- Corresponding acceptance criteria/PRD section

If the process is interrupted, use `/quick-feature --resume {TASK}` to resume."
```

**Real-time Progress Display**:
```
🚀 Development Progress

✅ Step 1: Create basic interface definitions
   📝 src/types/feature.ts
✅ Step 2: Implement core logic
   📝 src/services/feature-service.ts
⏳ Step 3: Integrate with existing system (In Progress...)
⬜ Step 4: Add error handling
⬜ Step 5: Write documentation
```

---

### Stage 4: Quality Verification (Optional - Executed by default)

**Goal**: Ensure code quality and functional completeness.

#### 4.1 Code Review (Unless `--skip-review`)

```
Use the Code Reviewer agent [fa-code-reviewer]:
"Review the newly implemented code.

Implementation Files: [Obtained from Stage 3]
PRD Path: `./.claude/specs/{TASK}/requirements.md`
Technical Design Path: `./.claude/specs/{TASK}/tech-design.md`
Review Record: `./.claude/specs/{TASK}/review-report.md`

## Review Points:
1.  **Functional Completeness**: Does it satisfy all acceptance criteria?
2.  **Code Quality**: Readability, maintainability, performance.
3.  **Architectural Consistency**: Does it follow existing patterns?
4.  **Potential Issues**: Edge cases, error handling, security.
5.  **Consistency Check**: Are any differences between the code implementation and the technical design documented? (If deviations exist, note the reason in `implementation.log`)

## Output Format:
- Review Result: Pass/At Risk/Fail
- Issue List (if any): [Issue description + suggested fix]
- Optimization Suggestions (optional): [Improvement directions]
- Severity Level: Blocker/High/Medium/Low, with impact scope explained.
- Output must be synced to `review-report.md`, and the status recorded in `progress.json`.

Constraints:
- Only flag critical issues (perfection not required).
- Optimization suggestions ≤ 3."
```

If the review fails, return to Stage 3 for fixes.

#### 4.2 Test Verification (Unless `--skip-tests`)

```
Use the Test & Validation Agent [fa-tester]:
"Verify the feature complies with acceptance criteria.

Implementation Files: [Obtained from Stage 3]
PRD Path: `./.claude/specs/{TASK}/requirements.md`
Acceptance Criteria: [Extracted from PRD]
Test Record: `./.claude/specs/{TASK}/test-report.md`

## Verification Tasks:
1.  **Functional Testing**:
    - Verify each acceptance criterion.
    - Test the normal flow.
    - Test edge cases.
2.  **Integration Testing**:
    - Compatibility with existing functionality.
    - Ensure no regression in existing features.
3.  **Test Report**:
    - Acceptance criteria checklist.
    - Issues found (if any).
    - Test conclusion (Pass/Fail).
    - For each issue, label severity (Critical/Major/Minor) and reproduction steps.
    - Record suggested regression scope.

Constraints:
- Use existing testing frameworks (e.g., Jest/Vitest/Pytest, etc.).
- Cover each acceptance criterion at least once.
- Test report ≤ 200 words, must still include the above severity/conclusion fields."
```

**Display Test Report**:
```
✅ Test Report

Acceptance Criteria Check:
✓ [Criterion 1] - Pass
✓ [Criterion 2] - Pass
✓ [Criterion 3] - Pass

Integration Tests:
✓ No impact on existing functionality
✓ Normal integration with [Component X]

Issues Found:
- [Issue description] (Severity: Low/Medium/High)

Test Conclusion: Pass ✅
```

**If Tests Fail**:
1. Record the specific problem causing the test failure.
2. Analyze the severity of the problem:
 - **Critical Issue** (feature unusable) → Must fix.
 - **Medium Issue** (problems in some scenarios) → Recommended to fix.
 - **Minor Issue** (edge cases) → Document as technical debt, optional fix.
3. Return to Stage 3 for fixes.
4. After fixes, rerun the tests.
5. Sync `test-report.md` and `progress.json`, marking the corresponding acceptance criteria as failed.

**Fallback Loop Control**:
- Max fix attempts: 3 times.
- If critical issues persist after 3 fixes:
 - Pause the workflow, request user intervention.
 - Present current code status and issue list.
 - Let user decide: continue fixing/accept current state/abandon feature.

**Code Review Fail Handling**:
If the review result is "Fail":
1. List all critical issues.
2. Return to Stage 3 to fix the issues.
3. After fixes, re-run the review.
4. Max review attempts: 2 times.
5. If it still fails, switch to manual review.

---

### Stage 5: Delivery & Documentation (Auto-executed)

**Goal**: Complete feature delivery and generate necessary documentation.

#### 5.1 Generate Documentation

**Standard Documentation** (Default):
```
Generate the following documents:
1.  Feature Documentation: `./.claude/specs/{TASK}/README.md`
    - Feature description
    - Usage instructions
    - API documentation (if applicable)
    - Configuration instructions (if applicable)
    - Links to related acceptance criteria or usage examples.
2.  Change Log: `./.claude/specs/{TASK}/CHANGELOG.md`
    - List of new files
    - List of modified files
    - Description of key changes
    - Corresponding commit/PR information (if any)
3.  In-Code Documentation:
    - JSDoc/Comments for key functions
    - Interface/Type descriptions
    - Reference the covered acceptance criterion IDs in comments.
```

**Minimal Documentation** (`--minimal-docs`):
```
Generate only:
1.  Quick Start Guide: `./.claude/specs/{TASK}/QUICKSTART.md`
    - One-sentence feature description
    - Usage examples (1-2)
    - Paths to key new files
```

#### 5.3 Delivery Summary
Generate a completion report:

```
🎉 Feature Implementation Complete

📋 Feature Name: [Feature name]
⏱️ Total Time: [Estimated duration]
📊 Complexity: [Simple/Medium/Complex]

📁 File Changes:
Created:
  - [File1] ([line count] lines)
  - [File2] ([line count] lines)
Modified:
  - [File3] ([changed line count] lines)

✅ Acceptance Criteria: All Passed (X/X)

📚 Documentation Location:
  - Feature Docs: `./.claude/specs/{TASK}/README.md`
  - Technical Design: `./.claude/specs/{TASK}/tech-design.md`
  - Change Log: `./.claude/specs/{TASK}/CHANGELOG.md`
  - Review Record: `./.claude/specs/{TASK}/review-report.md`
  - Test Record: `./.claude/specs/{TASK}/test-report.md`

🚀 Follow-up Suggestions:
- [Suggestion 1]
- [Suggestion 2]

- Confirm `progress.json` is marked as Stage 5 / completed.
```

## Output Directory Structure

```
./.claude/
├── quick-context.md                      # Repository architecture quick reference
└── specs/
    └── {TASK}/
        ├── requirements.md               # Requirements summary
        ├── tech-design.md                # Technical design
        ├── progress.json                 # Progress status (for resumption)
        ├── implementation.log            # Implementation log
        ├── README.md                     # Feature documentation (standard)
        ├── QUICKSTART.md                 # Quick start guide (`--minimal-docs`)
        └── CHANGELOG.md                  # Change log
```

---

## Document Format Templates

### quick-context.md Format

```markdown
# Project Architecture Quick Reference

Generated: {timestamp}
Scan Scope: {scope}

## Project Type
- Type: {Frontend/Backend/Full-stack/Library/Tool}
- Application Type: {Web app/API service/Desktop app/CLI tool}

## Technology Stack
- Main Language: {Language} ({Version})
- Core Framework: {Framework Name} ({Version})
- Package Manager: {npm/yarn/pnpm/pip/etc.}
- Build Tool: {webpack/vite/etc.}

## Directory Structure
```
{Key directory tree}
```

## Code Organization
- Naming Convention: {kebab-case/camelCase/PascalCase}
- Module Pattern: {ESM/CommonJS/etc.}
- Layered Structure: {MVC/Layered Architecture/etc.}

## Reusable Components
1. {Component Name}: {Path} - {Description}
2. {Component Name}: {Path} - {Description}
3. ...

## Code Style
- Config File: {.eslintrc/.prettierrc/etc.}
- Indentation: {Number} spaces
- Quotes: {Single/Double}
- Other Conventions: {List}

## Testing
- Testing Framework: {Jest/Vitest/Pytest/etc.}
- Test Location: {__tests__/test/etc.}
- Coverage Requirement: {If any}

## Recommended Implementation Locations
Suggested directories based on feature type:
- UI Component: {Path}
- API Endpoint: {Path}
- Business Logic: {Path}
- Utility Function: {Path}
```

### requirements.md Format

```markdown
# Feature Requirement: {Feature Name}

Generated: {timestamp}
Clarity Score: {Score}/10
Complexity: {Simple/Medium/Complex}

## Core Functionality
{One-sentence description of the main feature}

## User Stories
1. As a {role}, I want {functionality} so that {goal}.
2. As a {role}, I want {functionality} so that {goal}.
3. ...

## Acceptance Criteria
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}
- [ ] ...

## Technical Constraints
- {Constraint 1}
- {Constraint 2}
- ...

## Impact Scope
- Estimated New Files: {Count}
- Estimated Modified Files: {Count}
- Affected Modules: {Module list}

## Non-functional Requirements
- Performance Requirements: {If any}
- Security Requirements: {If any}
- Compatibility: {If any}
```

### tech-design.md Format

```markdown
# Technical Design: {Feature Name}

Generated: {timestamp}
Based on PRD: requirements.md

## File Plan

### New Files
1. `{File Path}`
   - Responsibility: {Responsibility description}
   - Type: {Component/Service/Utility/etc.}
2. `{File Path}`
   - Responsibility: {Responsibility description}
   - Type: {Component/Service/Utility/etc.}

### Modified Files
1. `{File Path}`
   - Change Type: {Add/Modify/Delete}
   - Change Description: {Description}

## Core Interface Definitions

### {Interface/Class/Function Name 1}
```{Language}
{Interface definition code}
```
Description: {One-sentence description}

### {Interface/Class/Function Name 2}
```{Language}
{Interface definition code}
```
Description: {One-sentence description}

## Data Flow Design

### Input
- {Input1}: {Type} - {Description}
- {Input2}: {Type} - {Description}

### Output
- {Output1}: {Type} - {Description}
- {Output2}: {Type} - {Description}

### Data Structures
```{Language}
{Key data structure definition}
```

## Integration Points
- Integration with {Existing Module 1}: {Integration method}
- Integration with {Existing Module 2}: {Integration method}

## Implementation Steps

1.  **{Step 1 Name}**
    - Task: {Specific task}
    - Deliverable: {File or code}
2.  **{Step 2 Name}**
    - Task: {Specific task}
    - Deliverable: {File or code}
3.  ...

## Risk Points
- {Risk1}: {Description & mitigation}
- {Risk2}: {Description & mitigation}

## Technical Decisions
- {Decision1}: {Rationale}
- {Decision2}: {Rationale}
```

### progress.json Format

```json
{
  "featureName": "{Feature Name}",
  "startTime": "{ISO Timestamp}",
  "lastUpdateTime": "{ISO Timestamp}",
  "currentStage": "{Stage Number: 0-5}",
  "currentStep": "{Current Step Number}",
  "status": "{Status: in-progress/blocked/completed}",
  "completedSteps": [
    {
      "stage": 0,
      "step": 1,
      "description": "{Step description}",
      "completedAt": "{ISO Timestamp}"
    }
  ],
  "filesCreated": [
    {
      "path": "{File Path}",
      "lines": {Line Count},
      "createdAt": "{ISO Timestamp}"
    }
  ],
  "filesModified": [
    {
      "path": "{File Path}",
      "linesChanged": {Line Count},
      "modifiedAt": "{ISO Timestamp}"
    }
  ],
  "issues": [
    {
      "type": "{Type: error/warning/info}",
      "description": "{Issue description}",
      "stage": {Stage Number},
      "resolved": {true/false},
      "timestamp": "{ISO Timestamp}"
    }
  ],
  "retryCount": {
    "stage1": 0,
    "stage2": 0,
    "stage3": 0,
    "stage4": 0
  },
  "userInputs": [
    {
      "prompt": "{Prompt content}",
      "response": "{User response}",
      "timestamp": "{ISO Timestamp}"
    }
  ]
}
```

---

## Success Criteria

- ✅ Repository architecture accurately identified (main language, framework, directory structure).
- ✅ Requirements are clear (clarity score ≥ 7).
- ✅ Technical solution is feasible (user approved).
- ✅ Code implementation completed (all acceptance criteria met).
- ✅ Quality verification passed (if not skipped).
- ✅ Documentation generated completely (according to options).

---
