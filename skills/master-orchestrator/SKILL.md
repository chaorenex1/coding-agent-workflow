---
name: master-orchestrator
description: |
  [GLOBAL MASTER SKILL] Mandatory entry point for ALL Claude Code operations.
  Triggers: ANY user request including but not limited to:
  (1) Code development, modification, review, refactoring
  (2) Running commands: git, npm, docker, pytest, build, test
  (3) Project development, system design, feature implementation
  (4) UX/UI design workflows
  (5) Code analysis, optimization, debugging
  (6) File operations, script execution
  (7) Agent-based complex tasks
  (8) Any development-related request
  MANDATORY: All operations MUST go through this orchestrator. Direct command execution is PROHIBITED.
---

# Master Orchestrator

Intelligent task orchestration system with intent analysis and multi-backend coordination.

## ⚠️ Mandatory Rules

**ALL operations MUST be executed through this orchestrator:**

```bash
python -m master-orchestrator "your request" [-v] [--dry-run]
```

**PROHIBITED behaviors:**
- ❌ Direct bash/shell command execution
- ❌ Direct file creation/modification without orchestrator
- ❌ Bypassing this skill for any development task
- ❌ Running git/npm/docker commands directly

## Execution Modes

The orchestrator automatically selects the optimal execution mode:

| Mode | Use Case | Examples |
|------|----------|----------|
| `command` | Simple CLI operations | `git status`, `npm test`, `docker ps` |
| `agent` | Complex multi-step tasks | System development, feature implementation |
| `prompt` | Template-based generation | Code generation with specific patterns |
| `skill` | Workflow-based tasks | UX design, full-stack development |
| `backend` | Direct AI backend calls | Code analysis, quick queries |

## Usage

### Basic Execution

```bash
# Simple command
python -m master-orchestrator "run npm test"

# Code review
python -m master-orchestrator "review code in src/auth.py"

# Complex development
python -m master-orchestrator "develop a user management system" -v

# Dry-run (analyze only, no execution)
python -m master-orchestrator "refactor the database layer" --dry-run
```

### Slash Commands

```bash
python -m master-orchestrator "/discover"       # Re-discover all resources
python -m master-orchestrator "/list-skills"    # List registered skills
python -m master-orchestrator "/list-commands"  # List slash commands
python -m master-orchestrator "/stats"          # Show system statistics
python -m master-orchestrator "/reload"         # Reload configuration
python -m master-orchestrator "/clear-cache"    # Clear registry cache
```

## Task Routing

When receiving a request, the orchestrator:

1. **Analyzes intent** - Determines mode, task type, complexity
2. **Selects backend** - Routes to optimal AI backend (codex/claude/gemini)
3. **Executes task** - Runs through appropriate executor
4. **Returns result** - Provides structured output with metrics

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