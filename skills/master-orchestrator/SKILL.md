---
name: master-orchestrator
description: |
  [SPECIALIZED ROUTING SKILL] Simplified task router for specialized AI backend tasks.
  Routes ONLY two types of tasks:
  (1) Code Development Tasks → delegates to code-with-codex skill
      - Feature implementation, system development, code refactoring, bug fixes
  (2) UX Design Tasks → delegates to ux-design-gemini skill
      - Interface design, prototypes, user experience design
  All other tasks (file operations, commands, analysis, testing) are handled directly by Claude Code native tools.
---

# Master Orchestrator

Simplified routing system for specialized AI backend tasks.

## 🎯 Simplified Routing Model

**Master-orchestrator routes ONLY specialized tasks requiring external AI backends.**

### What Gets Routed to Master-Orchestrator

**1. Code Development Tasks** → Delegates to `code-with-codex`
- Feature implementation (实现功能)
- System development (开发系统)
- Code refactoring (重构代码)
- Bug fixes (修复 bug)
- Adding new functionality (添加功能)

**2. UX Design Tasks** → Delegates to `ux-design-gemini`
- Interface design (设计界面)
- Prototype creation (原型设计)
- User experience design (用户体验设计)
- Interaction design (交互设计)

### What Executes Directly (No Routing)

Claude Code handles these directly with native tools:

- **File Operations**: Create, modify, delete, read files → `Write`, `Edit`, `Read`
- **Command Execution**: git, npm, docker, pytest → `Bash`
- **Code Analysis**: Understanding, searching code → `Read`, `Grep`, `Glob`, `LSP`
- **Testing**: Running tests, debugging → `Bash` + native tools
- **Documentation**: Writing, updating docs → `Write`, `Edit`

## Delegation Model

```
User Request
    ↓
Claude Code (analyzes task type)
    ↓
┌─────────────────────────────┐
│ Is it Code Development?     │
│ (实现/开发/重构/修复)         │
└─────────────────────────────┘
    ↓ YES
    Route to master-orchestrator
        ↓
        Delegate to code-with-codex
            ↓
            Returns result

┌─────────────────────────────┐
│ Is it UX Design?            │
│ (设计界面/原型/交互)         │
└─────────────────────────────┘
    ↓ YES
    Route to master-orchestrator
        ↓
        Delegate to ux-design-gemini
            ↓
            Returns result

┌─────────────────────────────┐
│ Everything else?            │
└─────────────────────────────┘
    ↓ YES
    Claude Code handles directly
        ↓
        Native tools execution
```

## Usage

### Invocation from Claude Code

**For Code Development Tasks:**
```python
Skill(skill="master-orchestrator", args="实现用户登录功能")
# → master-orchestrator → code-with-codex → implementation
```

**For UX Design Tasks:**
```python
Skill(skill="master-orchestrator", args="设计用户登录界面")
# → master-orchestrator → ux-design-gemini → design
```

**For All Other Tasks (Direct Execution):**
```python
# File operations - no routing needed
Write(file_path="test.py", content="...")
Edit(file_path="config.json", ...)

# Command execution - no routing needed
Bash(command="npm test")
Bash(command="git status")

# Code analysis - no routing needed
Read(file_path="auth.py")
Grep(pattern="function", path="src/")
```

### Direct Python Execution (Advanced)

```bash
# Code development task
python -u master_orchestrator.py "实现一个用户认证系统" -v

# UX design task
python -u master_orchestrator.py "设计一个仪表盘界面" -v

# Dry-run (analyze routing decision)
python -u master_orchestrator.py "实现登录功能" --dry-run
```

## Simplified Task Routing

When receiving a request, the orchestrator:

1. **Classifies task type** - Code development or UX design?
2. **Delegates to specialist** - Routes to code-with-codex or ux-design-gemini
3. **Returns result** - Passes through the specialist's output

**Routing Logic:**
- Code development keywords (实现/开发/重构/修复) → code-with-codex
- UX design keywords (设计界面/原型/交互) → ux-design-gemini
- Everything else → Not routed (handled by Claude Code directly)

## Output Format

Successful execution returns:

```
[Execution Complete]
Backend: <backend_name>
Success: True/False
Duration: <seconds>s
Run ID: <unique_id>

Output Preview:
<task output>

Tool Chain: [<tools_used>]
```

## Flags

| Flag | Description |
|------|-------------|
| `-v`, `--verbose` | Enable detailed output with step-by-step logging |
| `-n`, `--dry-run` | Show intent analysis and execution plan without running |

---

## 🎯 Simplified Routing Model (V3.0)

### Configuration

This skill operates in **specialized routing mode**:

- **Scope**: ONLY code development and UX design tasks
- **Delegation**: Routes to code-with-codex or ux-design-gemini
- **Performance**: All other operations execute directly (no routing overhead)

### Usage Pattern

**From Claude Code:**
```python
# Code development tasks
Skill(skill="master-orchestrator", args="实现用户登录功能")

# UX design tasks
Skill(skill="master-orchestrator", args="设计登录界面")
```

### Routing Rules

**Route to master-orchestrator (delegates to specialists):**
- ✅ Code development: Feature implementation, refactoring, bug fixes → code-with-codex
- ✅ UX design: Interface design, prototypes, user experience → ux-design-gemini

**Execute directly (no routing):**
- ✅ File operations: Create, modify, delete, read files → Native Write/Edit/Read tools
- ✅ Command execution: git, npm, docker, pytest → Native Bash tool
- ✅ Code analysis: Understanding, searching → Native Read/Grep/Glob/LSP tools
- ✅ Testing: Running tests, debugging → Native Bash + tools
- ✅ Documentation: Writing, updating docs → Native Write/Edit tools

### Delegation Flow

```
Code Development Task
    ↓
master-orchestrator
    ↓
code-with-codex skill
    ↓
Codex backend (via memex-cli)
    ↓
Implementation result
```

```
UX Design Task
    ↓
master-orchestrator
    ↓
ux-design-gemini skill
    ↓
Gemini backend (via memex-cli)
    ↓
Design result
```

### Performance Benefits

**Before (V2.0)**: All operations routed through orchestrator (10% overhead)
**After (V3.0)**: Only specialized tasks routed (0% overhead for common operations)

- File operations: 0ms routing overhead (direct execution)
- Commands: 0ms routing overhead (direct execution)
- Code development: ~500ms routing overhead (acceptable for complex tasks)
- UX design: ~500ms routing overhead (acceptable for complex tasks)

### Monitoring

Check routing statistics:

```bash
# View routing stats (code vs UX vs direct)
python -u master_orchestrator.py "/stats" -v

# Dry-run to see routing decision
python -u master_orchestrator.py "实现登录功能" --dry-run
```

### Troubleshooting

**Issue**: Task not being routed to orchestrator
- **Check**: Is it a code development or UX design task?
- **Fix**: If yes, verify CLAUDE.md routing rules; if no, direct execution is correct

**Issue**: Simple file operations going through orchestrator
- **Check**: Are you using Skill() instead of Write/Edit?
- **Fix**: Use native tools directly for file operations

**Issue**: Want to force routing for debugging
- **Check**: Use --dry-run flag to see routing decision
- **Fix**: Adjust task description to include code/UX keywords if needed