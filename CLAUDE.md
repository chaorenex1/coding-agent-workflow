# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-backend AI orchestration system with 5 execution modes: command execution, agent routing, prompt templating, skill workflows, and direct backend calls. Built on Python 3.12+ with Claude/Gemini/Codex backends.

## Running Tests

```bash
# Run orchestrator architecture tests (uses Mock, fast)
python orchestrator/tests/test_phase5_simple.py

# Run full integration tests (requires backends)
python orchestrator/tests/test_phase5_executors.py

# Run skill tests (various skills have their own tests)
python skills/api-document-generator/test_simple.py
python skills/code-refactoring-assistant/test_simple.py
```

## Architecture

### Core Execution Flow

```
User Request
    ↓
MasterOrchestrator
    ├─ ClaudeIntentAnalyzer (intent-analyzer.yaml)
    └─ ExecutionRouter
        ├─ CommandExecutor (command-parser.yaml)
        ├─ AgentCaller (agent-router.yaml)
        ├─ PromptManager (prompt-renderer.yaml)
        └─ SkillExecutor (dev-workflow.yaml)
            ↓
        BackendOrchestrator → Claude/Gemini/Codex
```

### MemexExecutorBase Pattern

All executors inherit from `orchestrator/executors/memex_executor_base.py`:

```python
class MyExecutor(MemexExecutorBase):
    def __init__(self, backend_orch, use_claude=True, fallback=True):
        super().__init__(backend_orch, default_backend="claude")
        self.use_claude = use_claude
        self.fallback = fallback

    def execute(self, request, **kwargs):
        if self.use_claude:
            try:
                return self._execute_via_claude(request)
            except Exception:
                if not self.fallback:
                    return ErrorResult(...)
        return self._execute_local(request)
```

**Critical**: All new executors MUST inherit MemexExecutorBase and implement three-tier fallback: Memex-CLI + Claude Skill → Local Implementation → Error.

### Execution Modes

| Mode | Executor | YAML Skill | Fallback |
|------|----------|------------|----------|
| command | CommandExecutor | command-parser.yaml | Rule engine |
| agent | AgentCaller | agent-router.yaml | Simple prompt |
| prompt | PromptManager | prompt-renderer.yaml | Local string.format() |
| skill | SkillExecutor | dev-workflow.yaml | Direct call |
| backend | BackendOrchestrator | - | None |

## Key Design Patterns

### 1. Skills are YAML Configurations

Skills live in `skills/memex-cli/skills/*.yaml`:

```yaml
name: my-skill
backend: claude
system_prompt: |
  You are an expert...
user_prompt_template: |
  {{request}}
examples:
  - name: example1
    input:
      request: "..."
    output: |
      ...
```

### 2. Lazy Imports for Circular Dependencies

`orchestrator/__init__.py` uses `__getattr__` to avoid circular imports when modules cross-import.

### 3. Windows Encoding Handling

All test files must handle Windows GBK encoding:

```python
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## Critical File Relationships

```
orchestrator/
├── master_orchestrator.py          # Entry point, routes to ExecutionRouter
├── core/
│   ├── backend_orchestrator.py     # Manages Claude/Gemini/Codex APIs
│   └── event_parser.py             # Parses streaming JSONL events
├── executors/
│   ├── memex_executor_base.py      # MUST inherit from this
│   ├── command_executor.py         # Natural language → shell commands
│   ├── agent_caller.py             # Routes to explore/plan/general agents
│   └── prompt_manager.py           # 6 built-in templates + custom
├── analyzers/
│   └── claude_intent_analyzer.py   # Claude-based intent classification
└── tests/
    ├── test_phase5_simple.py       # Mock-based architecture tests
    └── test_phase5_executors.py    # Real backend integration tests

skills/memex-cli/skills/
├── intent-analyzer.yaml            # Intent classification
├── command-parser.yaml             # NL → command translation
├── agent-router.yaml               # Agent type routing
├── prompt-renderer.yaml            # Template rendering
└── dev-workflow.yaml               # 5-stage development workflow
```

## Common Workflows

### Adding a New Executor

1. Create `orchestrator/executors/my_executor.py`:
   ```python
   from .memex_executor_base import MemexExecutorBase

   class MyExecutor(MemexExecutorBase):
       def __init__(self, backend_orch, **kwargs):
           super().__init__(backend_orch, default_backend="claude")

       def execute(self, request, **kwargs):
           # Implementation with fallback
           pass
   ```

2. Create skill in `skills/memex-cli/skills/my-skill.yaml`

3. Register in `orchestrator/master_orchestrator.py`:
   ```python
   class ExecutionRouter:
       def __init__(self, backend_orch):
           self.my_executor = MyExecutor(backend_orch)
   ```

4. Add tests in `orchestrator/tests/test_my_executor.py`

### Debugging Execution Path

```python
from orchestrator import MasterOrchestrator, BackendOrchestrator

backend_orch = BackendOrchestrator()
orch = MasterOrchestrator(backend_orch, verbose=True)

# Trace intent analysis
intent = orch._analyze_intent("your request", verbose=True)
print(f"Mode: {intent.mode}, Type: {intent.task_type}, Confidence: {intent.confidence}")

# Execute with full trace
result = orch.process("your request", verbose=True)
```

## Known Issues

1. **Memex-CLI unavailable**: All executors automatically fallback to local implementations. This is expected behavior.

2. **UnicodeDecodeError on Windows**: Add UTF-8 wrapper at script start (see Windows Encoding Handling above).

3. **Circular import**: Use lazy imports in `__init__.py` via `__getattr__`.

4. **Agent execution fails**: Check `result.error` field. Common causes:
   - Backend API not configured
   - Fallback disabled (`fallback_to_simple=False`)
   - Skill YAML syntax error

## Documentation

- Architecture overview: `docs/MEMEX_CLI_INTEGRATION_DESIGN.md`
- Phase completion reports: `docs/PHASE{1-5}_COMPLETION.md`
- Workflow rules: `docs/CLAUDE.md` (Linus Torvalds persona, Chinese responses)
- Executor docs: `orchestrator/CLAUDE.md` (detailed development guide)

## Data Structures

```python
@dataclass
class Intent:
    mode: ExecutionMode      # command/agent/prompt/skill/backend
    task_type: str
    complexity: str          # simple/moderate/complex
    confidence: float        # 0.0-1.0

@dataclass
class AgentRequest:
    agent_type: AgentType    # EXPLORE/PLAN/GENERAL_PURPOSE
    prompt: str
    thoroughness: str        # quick/medium/very_thorough
    model: Optional[str]

@dataclass
class PromptResult:
    template_name: str
    rendered_prompt: str
    success: bool
    rendered_by: str         # "claude" or "local"
    variables: Dict[str, Any]
    error: Optional[str]
    metadata: Optional[Dict]
```

## Never Break

- **API compatibility**: All executors must maintain backward-compatible signatures
- **MemexExecutorBase inheritance**: New executors MUST inherit from this base class
- **Fallback mechanisms**: All executors MUST implement graceful fallback
- **Test coverage**: New features require both Mock and integration tests
