---
name: master-orchestrator
description: "Intelligent AI task orchestration system with intent analysis and multi-backend coordination"
---

# Master Orchestrator

Intelligent task orchestration system that analyzes user intent and routes to optimal execution paths across multiple AI backends (Codex, Claude, Gemini).

---

## Usage

`/master-orchestrator <TASK> [OPTIONS]`

### Parameters

- `<TASK>`: Description of the task to execute (supports Chinese and English)
- `[OPTIONS]`: Optional parameters
  - `--dry-run`: Analyze intent without execution

---

## Context

- Task to execute: `$ARGUMENTS`
- Intelligent intent analysis and backend selection
- Multi-backend AI coordination (Codex, Claude, Gemini)
- Automatic resource discovery and tool registration

---

## Your Role

You are the Master Orchestrator coordinator. Your job is to invoke the master-orchestrator SKILL to handle the user's request intelligently.

---

## Execution Flow

### Step 1: Invoke Master Orchestrator SKILL

Call the master-orchestrator SKILL with the user's task:

```
SKILL('master-orchestrator', '$ARGUMENTS')
```

The master-orchestrator SKILL will:

1. **Intent Analysis**: Analyze the user's request to determine task type, complexity, and optimal execution path
2. **Backend Selection**: Choose the best AI backend(s) for the task:
   - **Codex**: Code generation, refactoring, algorithm implementation
   - **Claude**: Requirements analysis, design planning, code review
   - **Gemini**: UX design, creative tasks, multi-modal analysis
3. **Resource Discovery**: Automatically discover and register available tools, skills, and agents
4. **Task Execution**: Execute the task using the selected backend(s) with appropriate tools
5. **Result Synthesis**: Combine results from multiple backends if needed

---

## Task Categories

The master-orchestrator automatically detects and routes the following task types:

### Development Tasks
- Feature implementation
- Code refactoring
- Bug fixes
- Test writing

### Analysis Tasks
- Requirements analysis
- Code review
- Architecture design
- Impact analysis

### Design Tasks
- UX/UI design
- System architecture
- API design
- Database schema

### Operations Tasks
- Deployment scripts
- CI/CD configuration
- Infrastructure setup
- Monitoring setup

---

## Examples

### Example 1: Feature Development
```
/master-orchestrator "Implement user authentication with JWT tokens"
```

Result: Routes to Codex for code generation, Claude for security review

### Example 2: Requirements Analysis
```
/master-orchestrator "Analyze requirements for a blog system"
```

Result: Routes to Claude for requirements gathering and PRD generation

### Example 3: UX Design
```
/master-orchestrator "Design a mobile app interface for task management"
```

Result: Routes to Gemini for UX/UI design specifications

### Example 4: Multi-Backend Task
```
/master-orchestrator "Design and implement a REST API for user management" -v
```

Result:
1. Claude analyzes requirements and designs API contract
2. Codex generates implementation code
3. Claude reviews code for security and best practices

### Example 5: Verbose Mode
```
/master-orchestrator "Refactor authentication logic" -v
```

Result: Shows detailed intent analysis, backend selection reasoning, and execution steps

---


## Integration with Other Skills

The master-orchestrator can delegate to specialized skills:

- **code-with-codex**: Pure code generation tasks
- **ux-design-gemini**: UI/UX design tasks
- **memex-cli**: Complex multi-step workflows with state persistence
- **cross-backend-orchestrator**: Explicit multi-backend coordination

---

## Output Format

The master-orchestrator will provide:

1. **Intent Analysis Summary**: Task type, complexity, selected backend(s)
2. **Execution Plan**: Steps to be taken
3. **Results**: Deliverables from the task execution
4. **Recommendations**: Next steps or related tasks to consider

---

## Success Criteria

- ✅ User intent correctly identified and categorized
- ✅ Optimal backend(s) selected for the task
- ✅ Task executed successfully with appropriate tools
- ✅ Results delivered in expected format
- ✅ Recommendations provided for follow-up actions

---

## Notes

- The master-orchestrator automatically discovers available tools and resources
- It can combine multiple backends for complex tasks
