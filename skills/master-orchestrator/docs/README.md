# Master Orchestrator V3.0 - Documentation

## Architecture Overview

Master Orchestrator V3.0 is a **simplified routing skill** that delegates specialized tasks to external AI backends via memex-cli.

### Design Philosophy

**From V2.0**: Universal orchestration layer handling all operations (12,760 lines)
**To V3.0**: Specialized router for external AI tasks only (392 lines)

### Routing Model

```
User Request
    ↓
Keyword Classification
    ↓
    ├─ Code Development → code-with-codex (Codex backend)
    ├─ UX Design → ux-design-gemini (Gemini backend)
    └─ All Other Tasks → Direct execution (no routing)
```

### Components

**Active (V3.0)**:
- `master_orchestrator.py` (392 lines) - Core routing logic
- `__main__.py` (28 lines) - Entry point
- `SKILL.md` - Usage documentation
- `CHANGELOG.md` - Version history

**Deprecated (V2.0)**:
- `deprecated/CACHE_OPTIMIZATION.md` - LRU cache system (removed)
- `deprecated/MCP_SERVER_GUIDE.md` - MCP server integration (removed)

See `CHANGELOG.md` for complete V3.0 migration guide.

## Key Metrics

| Metric | V2.0 | V3.0 | Improvement |
|--------|------|------|-------------|
| Lines of Code | 12,760 | 392 | ↓ 96.9% |
| Python Files | 35+ | 2 | ↓ 94.3% |
| Dependencies | 35+ modules | 0 | ↓ 100% |
| Routing Overhead | 10% (all ops) | 0% (90% ops) | ↓ 90% |

## Usage

### Command Line

```bash
# Code development task
python master_orchestrator.py "实现用户登录功能" -v

# UX design task
python master_orchestrator.py "设计登录界面" -v

# Dry-run to see routing decision
python master_orchestrator.py "实现功能" --dry-run
```

### From Claude Code

```python
# Code development - routes to code-with-codex
Skill(skill="master-orchestrator", args="实现用户认证系统")

# UX design - routes to ux-design-gemini
Skill(skill="master-orchestrator", args="设计仪表盘界面")

# Other tasks - execute directly with native tools
Write(file_path="test.py", content="...")  # No routing
Bash(command="npm test")                    # No routing
Read(file_path="config.json")               # No routing
```

## Rationale

Based on comprehensive value analysis:
- **0 external dependencies**: No other skills use master-orchestrator
- **100% feature duplication**: All V2.0 features duplicate Claude Code native capabilities
- **10% performance overhead**: Unnecessary abstraction layer
- **Negative ROI**: Complexity cost exceeds value delivered

**Conclusion**: Simplify to specialized router for tasks requiring external AI backends only.

## Migration from V2.0

### Breaking Changes

**Removed**:
- All 5 execution modes (command/agent/prompt/skill/backend)
- Intent analysis layer (Claude LLM + rule engine)
- Resource discovery and registry system
- Slash commands (`/discover`, `/stats`, etc.)
- LRU caching system
- Parallel execution scheduler

**Preserved**:
- Command-line interface
- Skill invocation pattern
- Delegation to external skills

### Workflow Changes

**Before (V2.0)**:
```python
# Everything routed through master-orchestrator
Skill(skill="master-orchestrator", args="创建文件 test.py")
Skill(skill="master-orchestrator", args="运行 npm test")
```

**After (V3.0)**:
```python
# Only code/UX tasks routed
Skill(skill="master-orchestrator", args="实现登录功能")  # Code dev - routed

# Everything else direct
Write(file_path="test.py", content="...")  # File op - direct
Bash(command="npm test")                    # Command - direct
```

## Future Development

V3.0 is intentionally minimalist. Future enhancements should:
1. Maintain simplicity (target: < 500 lines)
2. Only add features with clear external dependencies
3. Avoid duplicating Claude Code native capabilities
4. Preserve 0-dependency architecture
