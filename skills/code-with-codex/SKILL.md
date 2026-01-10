---
name: code-with-codex
description: "Write and generate code using memex-cli with Codex backend. Use when (1) Generating code files and scripts, (2) Refactoring existing code, (3) Writing tests, (4) Creating project scaffolds, (5) Implementing algorithms or features, (6) Code review and optimization, (7) Complex multi-file projects."
---

# Code with Codex

Use memex-cli to leverage Codex for code generation with memory and resume support.

---

## Model Selection Guide

| Model | Best For | Complexity |
|-------|----------|------------|
| gpt-5.1-codex-mini | Simple scripts, quick fixes | ⭐ |
| gpt-5.2-codex | General coding, utilities | ⭐⭐ |
| gpt-5.1-codex-max | Balanced quality/speed | ⭐⭐⭐ |
| gpt-5.2 | Complex logic, algorithms | ⭐⭐⭐⭐ |
| gpt-5.2 | Architecture, system design | ⭐⭐⭐⭐⭐ |

**Quick selection guide:**
- Start with lower-tier models for simple tasks
- Upgrade to `codex-max` or `gpt-5.2` when quality issues arise
- Use `gpt-5.2` for production-grade code and complex systems

---

## Complexity Levels Overview

### Level 1: Simple Scripts (⭐)

Quick utilities, single-file scripts (20-100 lines). Use `gpt-5.1-codex-mini`.

**Examples:** Batch file rename, CSV processing, disk monitoring

**Quick example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: batch-rename
backend: codex
model: gpt-5.1-codex-mini
workdir: /path/to/scripts
---CONTENT---
Python脚本：批量重命名文件，添加日期前缀
---END---
EOF
```

➜ **Detailed examples:** [examples/level1-simple-scripts.md](examples/level1-simple-scripts.md)

---

### Level 2: Utility Functions (⭐⭐)

Reusable functions, data transformations (100-300 lines). Use `gpt-5.2-codex`.

**Examples:** Data validators, format converters, simple unit tests

**Quick example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: validators
backend: codex
model: gpt-5.2-codex
workdir: /path/to/utils
---CONTENT---
编写邮箱、手机号、身份证号验证函数
---END---
EOF
```

➜ **Detailed examples:** [examples/level2-utilities.md](examples/level2-utilities.md)

---

### Level 3: Complete Modules (⭐⭐⭐)

Production-ready modules with error handling, logging, tests (300-800 lines). Use `gpt-5.1-codex-max` or `gpt-5.2`.

**Examples:** HTTP clients, database helpers, API wrappers

**Special tasks at Level 3:**
- **Code Review:** Analyze code for security/performance issues
- **Refactoring:** Apply design patterns, improve testability
- **Unit Testing:** Comprehensive test coverage (>80%)

**Quick example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: http-client
backend: codex
model: gpt-5.1-codex-max
workdir: /path/to/lib
timeout: 120
---CONTENT---
Python HTTP客户端：支持重试、超时、拦截器
---END---
EOF
```

**Code review example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: review
backend: codex
model: gpt-5.2-codex
files: ./src/auth.py
files-mode: embed
workdir: /path/to/project
---CONTENT---
审查代码：安全隐患、性能瓶颈、改进建议
---END---
EOF
```

➜ **Detailed examples:** [examples/level3-modules.md](examples/level3-modules.md)

---

### Level 4: Complex Algorithms (⭐⭐⭐⭐)

Advanced data structures, optimized algorithms (500-1500 lines). Use `gpt-5.2` with extended timeout.

**Examples:** Skip lists, pathfinding (Dijkstra, A*), expression parsers

**Quick example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: skiplist
backend: codex
model: gpt-5.2
workdir: /path/to/algorithms
timeout: 180
---CONTENT---
实现跳表：支持插入、删除、搜索，O(log n)复杂度
---END---
EOF
```

➜ **Detailed examples:** [examples/level4-algorithms.md](examples/level4-algorithms.md)

---

### Level 5: System Design & Architecture (⭐⭐⭐⭐⭐)

Multi-module projects, microservices, complete applications (2000+ lines). Use `gpt-5.2` with 300-600s timeout.

**Examples:** Authentication microservices, event-driven systems, full-stack apps

**Quick example:**
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: auth-service
backend: codex
model: gpt-5.2
workdir: /path/to/services/auth
timeout: 300
---CONTENT---
设计用户认证微服务：JWT、OAuth2、RBAC权限模型
---END---
EOF
```

➜ **Detailed examples:** [examples/level5-architecture.md](examples/level5-architecture.md)

---

## Basic Usage

### Single Task

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: task-id
backend: codex
workdir: /working/directory
model: gpt-5.2-codex
---CONTENT---
[Your task description]
---END---
EOF
```

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique task identifier | `impl-auth`, `test-validators` |
| `backend` | Always `codex` for code generation | `codex` |
| `workdir` | Working directory path | `./src`, `/home/user/project` |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `model` | gpt-5.2-codex | Model selection (see complexity guide) |
| `timeout` | 300 | Max execution time (seconds) |
| `dependencies` | - | Comma-separated task IDs |
| `files` | - | Source files to reference |
| `files-mode` | auto | `embed` (include content) / `ref` (path only) |
| `retry` | 0 | Retry count on failure |

---

## Quick Reference

### Complexity Decision Tree

```
Start
  ├─ Single file, <100 lines? → Level 1 (codex-mini)
  ├─ Reusable functions, no external deps? → Level 2 (codex)
  ├─ Production module with tests?
  │   ├─ Standard CRUD/API? → Level 3 (codex-max)
  │   └─ Complex algorithm? → Level 4 (gpt-5.2)
  └─ Multi-module/microservice? → Level 5 (gpt-5.2)
```

### Task Type Classification

| Task Type | Level | Model | Example Link |
|-----------|-------|-------|--------------|
| Batch rename script | 1 | codex-mini | [Level 1](examples/level1-simple-scripts.md) |
| Email validator | 2 | codex | [Level 2](examples/level2-utilities.md) |
| HTTP client with retry | 3 | codex-max | [Level 3](examples/level3-modules.md) |
| Code review | 3 | codex-max | [Level 3](examples/level3-modules.md#code-quality-tasks) |
| Refactoring | 3-4 | codex-max / gpt-5.2 | [Level 3](examples/level3-modules.md#example-4-refactoring) |
| Unit testing | 2-3 | codex / codex-max | [Level 3](examples/level3-modules.md#example-5-comprehensive-unit-testing) |
| Skip list algorithm | 4 | gpt-5.2 | [Level 4](examples/level4-algorithms.md) |
| Auth microservice | 5 | gpt-5.2 | [Level 5](examples/level5-architecture.md) |

---

## Additional Resources

### Progressive Disclosure Documentation

- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Complete usage guide
  - When to use this skill
  - Relationship with memex-cli
  - Model selection tips
  - Workflow references

- **[references/complexity-guide.md](references/complexity-guide.md)** - Detailed complexity selection
  - In-depth explanation of 5 levels
  - Model performance comparison
  - Decision tree and classification
  - Best practices by task type

- **[examples/](examples/)** - Runnable code examples
  - [level1-simple-scripts.md](examples/level1-simple-scripts.md) - Quick utilities
  - [level2-utilities.md](examples/level2-utilities.md) - Reusable functions
  - [level3-modules.md](examples/level3-modules.md) - Production modules, code review, refactoring
  - [level4-algorithms.md](examples/level4-algorithms.md) - Complex algorithms
  - [level5-architecture.md](examples/level5-architecture.md) - System design

### Advanced Workflows

For multi-task workflows, parallel execution, and resume functionality, refer to memex-cli skill:

- **Multi-task DAG workflows:** [memex-cli/references/advanced-usage.md](../memex-cli/references/advanced-usage.md)
- **Parallel execution patterns:** [memex-cli/examples/parallel-tasks.md](../memex-cli/examples/parallel-tasks.md)
- **Resume interrupted runs:** [memex-cli/examples/resume-workflow.md](../memex-cli/examples/resume-workflow.md)

---

## Tips

1. **Match model to task complexity**
   - Start with lightweight models for simple tasks
   - Upgrade to powerful models only when needed
   - Save costs by not over-provisioning

2. **Use files for context**
   - Code review: `files: ./src/auth.py` + `files-mode: embed`
   - Refactoring: Include source code for analysis
   - Unit testing: Reference module to test

3. **Break down large tasks**
   - Split Level 5 projects into parallel Level 3-4 subtasks
   - Use DAG workflows for dependencies
   - See [memex-cli advanced usage](../memex-cli/references/advanced-usage.md)

4. **Include context in prompts**
   - Specify language, framework, coding standards
   - Mention target Python/Node.js version
   - Include expected output format

5. **Leverage examples**
   - Browse [examples/](examples/) directory for similar tasks
   - Copy and customize example commands
   - Follow established patterns

---

## SKILL Reference

- [skills/memex-cli/SKILL.md](../memex-cli/SKILL.md) - Memex CLI full documentation
- [HOW_TO_USE.md](HOW_TO_USE.md) - Detailed usage guide for this skill
