# Changelog

All notable changes to master-orchestrator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-01-08

### 🎯 Major Simplification - Radical Refactoring

**Breaking Change**: Complete architectural overhaul from 12,760 lines to 392 lines (96.9% reduction)

### Summary

Master-orchestrator has been simplified from a complex multi-layer orchestration system to a **specialized routing skill** that only handles two specific task types:
1. **Code Development** → Delegates to `code-with-codex` skill
2. **UX Design** → Delegates to `ux-design-gemini` skill
3. **All Other Tasks** → Direct execution by Claude Code (no routing)

### Removed

**Entire directories deleted:**
- `analyzers/` - Complex intent analysis layer (Claude LLM intent analyzer, rule engine)
- `executors/` - Multiple execution modes (command, agent, prompt, skill, backend)
- `core/` - All infrastructure components:
  - `intent_cache.py` - LRU cache system
  - `backend_orchestrator.py` - Backend selection logic
  - `unified_registry.py` - Resource discovery system
  - `async_orchestrator.py` - Async execution layer
  - `mcp_server.py` - MCP server integration
  - `request_interceptor.py` - Request interception hooks
  - `parallel_scheduler.py` - Parallel task scheduling
  - `executor_factory.py` - Executor factory pattern
  - `slash_command_registry.py` - Slash command system
  - 10+ other infrastructure files
- `clients/` - External client integrations

**Total files removed**: 35+ Python files

### Added

**New simplified implementation:**
- `master_orchestrator.py` (392 lines) - Simple keyword-based routing
  - Direct keyword matching for task classification
  - Delegation to memex-cli backends (codex/gemini)
  - Clear routing decision reporting
  - Support for --dry-run and -v flags

**Configuration-driven routing:**
- Updated `~/.claude/CLAUDE.md` - Routing rules defined in config instead of code
- Updated `SKILL.md` - Documented simplified usage model

### Changed

**From V2.0 to V3.0:**

| Aspect | V2.0 (Before) | V3.0 (After) |
|--------|---------------|--------------|
| **Lines of Code** | 12,760 | 392 (96.9% reduction) |
| **Dependencies** | 35+ internal modules | 0 (only stdlib + memex-cli) |
| **Routing Logic** | Claude LLM intent analysis + rule engine | Simple keyword matching |
| **Execution Modes** | 5 modes (command/agent/prompt/skill/backend) | 2 delegations (code/ux) |
| **Performance Overhead** | 10% on all operations | 0% on direct execution tasks |
| **Routing Scope** | All operations | Only code dev + UX design |

**Routing behavior:**
- V2.0: Route all write operations through orchestrator
- V3.0: Route only code development and UX design tasks
- All other tasks (file ops, commands, analysis, testing) execute directly

### Performance

**Improvements:**
- **File operations**: 10% overhead → 0% overhead (direct execution)
- **Commands**: 10% overhead → 0% overhead (direct execution)
- **Code analysis**: 10% overhead → 0% overhead (direct execution)
- **Code development**: ~500ms routing overhead (acceptable for complex tasks)
- **UX design**: ~500ms routing overhead (acceptable for complex tasks)

**Overall impact:**
- 90% of operations now execute with 0% routing overhead
- 10% of operations (code/UX) maintain acceptable overhead

### Documentation

**Updated:**
- `SKILL.md` - V3.0 simplified routing model
- `~/.claude/CLAUDE.md` - New routing decision matrix
- `CHANGELOG.md` - This document

**Deprecated:**
- `docs/CACHE_OPTIMIZATION.md` - LRU cache system (no longer used)
- `docs/RECURSION_FIX.md` - Recursion bug fix (no longer relevant)
- All V2.0 architecture documentation

### Migration Guide

**For users:**
- **Before**: All operations routed through master-orchestrator
- **After**: Only code dev + UX design routed; everything else uses native tools

**Example workflow changes:**

```python
# V2.0 - Everything routed
Skill(skill="master-orchestrator", args="创建文件 test.py")  # Old way

# V3.0 - Direct execution
Write(file_path="test.py", content="...")  # New way - direct tool

# V3.0 - Still routed (code development)
Skill(skill="master-orchestrator", args="实现用户登录功能")  # Correct

# V3.0 - Still routed (UX design)
Skill(skill="master-orchestrator", args="设计登录界面")  # Correct
```

**Breaking changes:**
- No more `/discover`, `/list-skills`, `/stats` slash commands
- No more intent analysis caching
- No more multi-backend automatic selection
- No more graceful degradation with candidate fallback

**What still works:**
- Command-line interface: `python master_orchestrator.py "task" -v --dry-run`
- Skill invocation: `Skill(skill="master-orchestrator", args="task")`
- Delegation to code-with-codex and ux-design-gemini

### Rationale

**Why simplify?**

Based on comprehensive value analysis (`docs/VALUE_ANALYSIS.md`):
- **0 external dependencies**: No other skills use master-orchestrator
- **100% feature duplication**: All features duplicate Claude Code native capabilities
- **10% performance overhead**: Unnecessary abstraction layer
- **Negative ROI**: Complexity cost exceeds value delivered

**Design philosophy shift:**
- **From**: Universal orchestration layer for all operations
- **To**: Specialized router for tasks requiring external AI backends

### Backward Compatibility

**Not backward compatible**: This is a breaking change (V3.0.0)

**Removed features:**
- All V2.0 execution modes (command, agent, prompt, skill, backend)
- Intent analysis layer (Claude LLM + rule engine)
- Resource discovery and registry system
- Slash command system
- LRU caching system
- Parallel execution scheduler

**Preserved features:**
- Command-line interface
- Verbose and dry-run flags
- Delegation to external skills

---

## [2.0.1] - 2026-01-08

### Fixed

- **[CRITICAL] JSONL 解析失败修复** (`analyzers/claude_intent_analyzer.py`)
  - 修复了 `ClaudeIntentAnalyzer._parse_intent_result()` 无法解析 JSONL 格式输出的问题
  - 根本原因：`BackendOrchestrator` 返回 JSONL 格式（多行 JSON Events），而解析器期望单个 JSON 对象
  - 影响：所有使用 Claude 进行意图分析的场景都会失败并显示 `'task_type'` 错误

### Added

- **JSONL 格式支持**
  - 新增 `_parse_jsonl_format()` 方法：逐行解析 JSONL 事件
  - 新增 `_recursive_json_parse()` 方法：处理多层转义的 JSON（最多 3 层）
  - 智能格式检测：自动识别 JSONL vs 单个 JSON
  - Early exit 优化：找到 `assistant.output` 后立即停止遍历

- **错误处理改进**
  - 详细错误消息：包含格式类型、输出长度、原始输出前 500 字符
  - 调试日志：JSONL 解析过程的每一步
  - 异常链保留：便于追踪根本原因

- **测试覆盖**
  - 新增 `tests/test_claude_intent_analyzer.py`：完整单元测试（pytest）
  - 新增 `tests/test_jsonl_parsing_simple.py`：简单测试（不依赖 pytest）
  - 6 个测试用例，100% 通过率，包括真实错误案例验证

- **文档**
  - 新增 `docs/JSONL_PARSING_FIX.md`：详细的修复文档
  - 包含问题描述、根本原因、修复方案、技术细节、故障排查指南

### Changed

- **向后兼容性保持**
  - 仍支持单个 JSON 对象格式（策略 2）
  - 仍支持 Regex 提取（策略 3）
  - 仍支持代码块提取（策略 4）
  - 旧代码无需任何修改

### Performance

- JSONL 解析开销：< 5ms（通常 < 2ms）
- 内存开销：可忽略（JSONL 通常 < 2KB）

---

## [1.1.0] - 2026-01-08

### Added

- **两层智能路由系统** (重大性能优化) 🚀
  - 实现规则引擎优先策略，所有请求先经过快速规则分析（约 0.1秒）
  - 智能升级判断：仅复杂任务升级到 Claude LLM
  - 三重升级条件：复杂关键词检测 + 请求长度阈值(>50) + 多任务识别
  - 路由统计监控：实时显示规则引擎 vs Claude 使用比例
  - 升级原因反馈：verbose 模式显示详细升级决策理由
  - 新增方法：`_analyze_intent()`, `_should_upgrade_to_claude()`, `_get_upgrade_reason()`

- **LRU 缓存优化** (意图分析加速)
  - 新增 `core/intent_cache.py`：完整的缓存管理器实现
  - 基于 `OrderedDict` 的 LRU 缓存策略
  - 语义归一化：相似请求共享缓存（忽略空格/大小写差异）
  - 持久化存储：`~/.memex/orchestrator/cache/`
  - 可选 TTL 过期机制
  - 缓存统计监控：命中率、节省时间、缓存大小
  - 新增 API：`get_cache_stats()`, `clear_cache()` in `ClaudeIntentAnalyzer`

- **文档和测试**
  - 新增 `docs/CACHE_OPTIMIZATION.md`：完整的性能优化指南（782行）
    - 智能路由架构流程图和决策树
    - 升级条件详解（关键词/长度/多任务）
    - 路由统计和性能基准测试
    - 最佳实践指南（4个章节）
    - API 参考和故障排查
  - 新增 `test_cache.py`：自动化缓存测试脚本
  - 更新 `README.md`：添加智能路由和缓存说明
  - 更新 `SKILL.md`：添加 `-u` 标志使用说明（实时输出）

### Changed

- **命令格式优化**
  - 所有命令示例统一使用 `python -u master_orchestrator.py` 格式
  - 移除已弃用的 `-m` 选项
  - 更新 `__main__.py`：强制启用无缓冲输出（实时显示）
  - 更新 `BackendOrchestrator` 默认超时：300秒 → 180秒（3分钟）
  - 设置 `bufsize=0`（无缓冲）实现真正的实时输出

- **意图分析增强**
  - `ClaudeIntentAnalyzer.__init__()` 新增缓存参数：`enable_cache`, `cache_max_size`, `cache_ttl_seconds`
  - `analyze()` 方法集成缓存检查（先查缓存，未命中再调用 Claude）
  - 新增 `ExecutionMode.READONLY` 枚举值（修复枚举缺失）

- **提示词优化**
  - 更新意图分析提示词：明确要求不使用 ````json` 代码块包裹
  - 更新命令执行器提示词：统一返回格式规范
  - 修复 `PARALLEL_KEYWORDS` 字典缺失问题

### Performance

- **简单任务性能提升** 🎯
  - 优化前：20-25秒（每次都调用 Claude）
  - 优化后：< 0.1秒（规则引擎直接处理）
  - **提速倍数：200-250倍**

- **复杂任务缓存性能** 💾
  - 首次请求：20-25秒（必须调用 Claude）
  - 缓存命中：< 0.1秒（从缓存返回）
  - **提速倍数：200-250倍**

- **API 调用优化**
  - 简单任务：减少 95% 的 Claude API 调用
  - 规则引擎使用率预期：> 80%
  - 缓存命中率预期：> 90%（典型场景）

- **内存和存储**
  - 缓存内存占用：< 10MB
  - 持久化文件大小：< 1MB
  - LRU 淘汰策略：自动管理内存

### Fixed

- 添加缺失的 `ExecutionMode.READONLY` 枚举值
- 添加缺失的 `PARALLEL_KEYWORDS` 字典（用于并行任务识别）
- 修复实时输出缓冲问题（添加 `-u` 标志和 `bufsize=0`）
- 修复 JSONL 解析逻辑（集成到意图分析器）

### Deprecated

- 移除已弃用的示例脚本：
  - `examples/demo_clear_cache.py`（功能已集成到主程序）
  - `examples/demo_stream_output.py`（流式输出已成为默认功能）

### Compatibility

- **向后兼容性：100%**
  - 缓存和智能路由默认启用，无需修改现有代码
  - 禁用缓存：设置 `enable_cache=False` in `ClaudeIntentAnalyzer`
  - 禁用智能路由：设置 `use_claude_intent=False` in `MasterOrchestrator`
  - 所有旧有 API 和参数保持不变
  - 命令行接口完全兼容（新增 `-u` 标志为可选）

---

## [2.0.0] - 2025-XX-XX

### Added

- **MCP Server 模式** - 基于 Claude Agent SDK 的原生集成
- **异步执行支持** - 完整的异步 API，更好的并发性能
- **请求拦截系统** - 通过 Hooks 实现统一调度和权限控制
- **审计日志** - 完整的工具调用审计和追踪
- **并行执行推断** - 智能判断任务是否可并行，自动拆分并行执行

### Changed

- 架构升级为 MCP Server 模式
- 支持同步和异步两种运行模式

---

## [1.x.x] - 2025-XX-XX

### Added

- 初始版本
- 智能意图分析
- 5 种执行模式：Command, Agent, Prompt, Skill, Backend
- 多后端支持：Claude, Gemini, Codex
- 专业提示词模板库
- 技能注册和发现系统

---

## 注释

### 版本号规则

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

### 变更类型

- **Added**: 新功能
- **Changed**: 现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 问题修复
- **Security**: 安全修复
