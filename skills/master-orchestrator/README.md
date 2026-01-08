# Master Orchestrator V3.0

**Simplified Routing Skill** - Specialized task router for external AI backends

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)
![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)

## Overview

Master Orchestrator V3.0 is a **simplified routing skill** that delegates specialized tasks to external AI backends. It routes only two types of tasks:
1. **Code Development** → `code-with-codex` (Codex backend via memex-cli)
2. **UX Design** → `ux-design-gemini` (Gemini backend via memex-cli)
3. **All Other Tasks** → Direct execution by Claude Code (no routing)

### V3.0 Simplification 🎯

**From V2.0 to V3.0**:
- **Code reduction**: 12,760 lines → 392 lines (↓ 96.9%)
- **File reduction**: 35+ files → 2 files (↓ 94.3%)
- **Performance**: 10% overhead on all ops → 0% overhead on 90% ops
- **Architecture**: Complex multi-layer orchestration → Simple keyword routing

See [CHANGELOG.md](CHANGELOG.md) for complete V3.0 migration guide.

---

## Quick Start

### Installation

```bash
# Install memex-cli (required for delegation to external backends)
npm install -g memex-cli

# No Python dependencies needed - uses only stdlib
```

### Basic Usage

**Command Line**:

```bash
# Code development task (routes to code-with-codex)
python master_orchestrator.py "实现用户登录功能" -v

# UX design task (routes to ux-design-gemini)
python master_orchestrator.py "设计登录界面" -v

# Direct execution task (no routing)
python master_orchestrator.py "运行 npm test" -v

# Dry-run to see routing decision
python master_orchestrator.py "实现功能" --dry-run
```

**From Claude Code**:

```python
# Code development - routes to code-with-codex
Skill(skill="master-orchestrator", args="实现用户认证系统")

# UX design - routes to ux-design-gemini
Skill(skill="master-orchestrator", args="设计仪表盘界面")

# Other tasks - execute directly with native tools (no routing)
Write(file_path="test.py", content="...")  # File operation
Bash(command="npm test")                    # Command execution
Read(file_path="config.json")               # Code analysis
```

---

## Architecture

### Routing Logic

```
User Request
    ↓
Keyword Classification
    ↓
    ├─ Code Keywords (实现/开发/重构/修复/implement/develop/refactor/fix)
    │   ↓
    │   Delegate to code-with-codex
    │   ↓
    │   memex-cli run --backend codex --prompt "<request>"
    │
    ├─ UX Keywords (设计界面/UI/UX/原型/交互设计/prototype/wireframe)
    │   ↓
    │   Delegate to ux-design-gemini
    │   ↓
    │   memex-cli run --backend gemini --prompt "<request>"
    │
    └─ Other Tasks
        ↓
        Return "Direct Execution" notice
        (Claude Code handles with native tools)
```

### Components

**Active (V3.0)**:
- `master_orchestrator.py` (392 lines) - Core routing logic
- `__main__.py` (28 lines) - Entry point with unbuffered output
- `SKILL.md` - Usage documentation
- `CHANGELOG.md` - Version history and migration guide

**Removed (from V2.0)**:
- `analyzers/` - Claude LLM intent analyzer, rule engine
- `executors/` - 5 execution modes (command/agent/prompt/skill/backend)
- `core/` - 20+ infrastructure files (cache, registry, scheduler, etc.)
- `clients/` - External client integrations

---

## Core Features

### 1. Simple Keyword Matching

No complex intent analysis - just direct keyword matching:

```python
CODE_KEYWORDS = [
    '实现', '开发', '编写代码', '重构', '修复', 'bug', 'fix',
    'implement', 'develop', 'refactor', ...
]

UX_KEYWORDS = [
    '设计界面', 'ui', 'ux', '原型', '交互设计',
    'wireframe', 'prototype', ...
]
```

### 2. Delegation to External Backends

Routes to specialized skills via memex-cli:

- **code-with-codex**: Code development tasks using Codex backend
- **ux-design-gemini**: UX design tasks using Gemini backend

### 3. Direct Execution Notice

For tasks that don't match code/UX keywords, returns a notice:

```
[Direct Execution] This task should be handled directly by Claude Code.
No routing to master-orchestrator needed.
Suggested action: Use native Claude Code tools (Write/Edit/Bash/Read/Grep/Glob)
```

---

## Usage Examples

### Example 1: Code Development

```bash
$ python master_orchestrator.py "实现一个用户认证API" -v

[Routing] Task type: code
[Routing] Request: 实现一个用户认证API
[Delegation] Routing to: code-with-codex
[Execution] Command: memex-cli run --backend codex --prompt "实现一个用户认证API" --stream-format text

[Success] Task completed
Task Type: code
Delegation: code-with-codex
Backend: codex

Output:
[Codex output here...]
```

### Example 2: UX Design

```bash
$ python master_orchestrator.py "设计一个登录注册界面" -v

[Routing] Task type: ux
[Routing] Request: 设计一个登录注册界面
[Delegation] Routing to: ux-design-gemini
[Execution] Command: memex-cli run --backend gemini --prompt "设计一个登录注册界面" --stream-format text

[Success] Task completed
Task Type: ux
Delegation: ux-design-gemini
Backend: gemini

Output:
[Gemini output here...]
```

### Example 3: Direct Execution

```bash
$ python master_orchestrator.py "创建一个空文件 test.py" -v

[Routing] Task type: direct
[Routing] Request: 创建一个空文件 test.py

[Direct Execution] This task should be handled directly by Claude Code.
No routing to master-orchestrator needed.
Task: 创建一个空文件 test.py

Suggested action: Use native Claude Code tools (Write/Edit/Bash/Read/Grep/Glob)
```

### Example 4: Dry-Run Mode

```bash
$ python master_orchestrator.py "重构数据库层代码" --dry-run

======================================================================
Master Orchestrator V3.0 - Execution Result
======================================================================

[Dry-Run Mode]
Task Type: code
Delegation: code-with-codex
Backend: codex

[DRY-RUN] Would delegate to code-with-codex skill (codex backend)
======================================================================
```

---

## Command-Line Options

```bash
python master_orchestrator.py <request> [options]

Options:
  -v, --verbose    Enable detailed output with routing decisions
  -n, --dry-run    Show routing decision without execution
  -h, --help       Show help message
```

---

## Performance

### V2.0 vs V3.0 Comparison

| Metric | V2.0 | V3.0 | Improvement |
|--------|------|------|-------------|
| **Lines of Code** | 12,760 | 392 | ↓ 96.9% |
| **Python Files** | 35+ | 2 | ↓ 94.3% |
| **Dependencies** | 35+ modules | 0 | ↓ 100% |
| **Routing Overhead (file ops)** | 10% | 0% | ↓ 100% |
| **Routing Overhead (commands)** | 10% | 0% | ↓ 100% |
| **Routing Overhead (code dev)** | 10% | ~500ms | Acceptable |

**Overall Impact**:
- 90% of operations execute with 0% routing overhead (direct execution)
- 10% of operations (code/UX) maintain acceptable routing overhead (~500ms)

---

## Migration from V2.0

### Breaking Changes

**Removed Features**:
- ❌ 5 execution modes (command/agent/prompt/skill/backend)
- ❌ Claude LLM intent analysis
- ❌ Rule engine and intelligent routing
- ❌ Resource discovery and registry system
- ❌ Slash commands (`/discover`, `/list-skills`, `/stats`)
- ❌ LRU caching system
- ❌ Parallel execution scheduler
- ❌ MCP server integration
- ❌ Request interceptor hooks

**Preserved Features**:
- ✅ Command-line interface (`python master_orchestrator.py`)
- ✅ Skill invocation (`Skill(skill="master-orchestrator", ...)`)
- ✅ Delegation to external skills (code-with-codex, ux-design-gemini)
- ✅ Verbose and dry-run flags

### Workflow Changes

**Before (V2.0)**:
```python
# Everything routed through master-orchestrator
Skill(skill="master-orchestrator", args="创建文件 test.py")
Skill(skill="master-orchestrator", args="运行 npm test")
Skill(skill="master-orchestrator", args="实现登录功能")
```

**After (V3.0)**:
```python
# Only code/UX tasks routed
Skill(skill="master-orchestrator", args="实现登录功能")  # Code - routed

# Everything else executes directly
Write(file_path="test.py", content="...")  # File op - direct
Bash(command="npm test")                    # Command - direct
```

---

## Rationale for Simplification

Based on comprehensive value analysis ([docs/VALUE_ANALYSIS.md](docs/VALUE_ANALYSIS.md)):

**Key Findings**:
- **0 external dependencies**: No other skills use master-orchestrator
- **100% feature duplication**: All V2.0 features duplicate Claude Code native capabilities
- **10% performance overhead**: Unnecessary abstraction layer on all operations
- **Negative ROI**: Complexity cost (maintenance, bugs) exceeds value delivered

**Design Philosophy Shift**:
- **From**: Universal orchestration layer for all operations
- **To**: Specialized router for tasks requiring external AI backends only

**KISS Principle**: Simplify to the minimum necessary functionality.

---

## Documentation

- **[SKILL.md](SKILL.md)** - Detailed usage guide and V3.0 routing model
- **[CHANGELOG.md](CHANGELOG.md)** - Complete version history and migration guide
- **[docs/README.md](docs/README.md)** - Architecture overview and metrics
- **[docs/VALUE_ANALYSIS.md](~/.claude/skills/master-orchestrator/docs/VALUE_ANALYSIS.md)** - Comprehensive analysis of V2.0 over-engineering

---

## Future Development

V3.0 is intentionally minimalist. Future enhancements should:

1. **Maintain simplicity**: Target < 500 lines of code
2. **Add only externally-dependent features**: No duplication of Claude Code native capabilities
3. **Preserve 0-dependency architecture**: Only stdlib + memex-cli
4. **Configuration-driven**: Define behavior in CLAUDE.md, not code

---

## License

MIT License - See LICENSE file for details

---

## Contributing

This is a specialized routing skill with intentional minimal scope. Contributions should align with the V3.0 design philosophy:
- Simplicity over features
- Configuration over code
- Delegation over implementation
- 0 dependencies (except memex-cli)

---

## Support

For issues or questions:
- **Bug reports**: Check if task is being routed correctly (use `--dry-run` flag)
- **Feature requests**: Consider if feature can be implemented via configuration in CLAUDE.md
- **Documentation**: See [SKILL.md](SKILL.md) and [CHANGELOG.md](CHANGELOG.md)

---

**Version**: 3.0.0
**Last Updated**: 2026-01-08
**Maintainer**: Master Orchestrator Team
