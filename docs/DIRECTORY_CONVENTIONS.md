# 目录约定指南 - Convention-over-Configuration

## 概述

从 V3.2 开始，Orchestrator 支持**约定优于配置**（Convention over Configuration）方式自动发现资源。

**YAML 配置现在完全可选**！只需遵循目录约定，系统会自动发现和注册：
- ✅ Skills
- ✅ Commands
- ✅ Agents
- ✅ Prompts

---

## 目录结构

```
项目根目录/
├─ skills/                  # Skills 目录
│  ├─ my-skill/             # 目录式 Skill
│  │  ├─ SKILL.md           # ✅ 自动发现标志
│  │  ├─ main.py            # 入口文件
│  │  └─ test_simple.py     # 测试文件
│  │
│  ├─ another-skill.yaml    # 单文件 YAML Skill
│  │
│  └─ hybrid-skill/         # 混合模式
│     ├─ SKILL.md           # 自动推断
│     ├─ skill.yaml         # 覆盖推断（可选）
│     └─ main.py
│
├─ commands/                # Commands 目录
│  ├─ git-shortcuts/
│  │  ├─ COMMAND.md         # ✅ 自动发现标志
│  │  └─ commands.yaml      # 可选
│  │
│  └─ docker-utils.yaml     # 单文件 YAML
│
├─ agents/                  # Agents 目录
│  ├─ custom-explorer/
│  │  ├─ AGENT.md           # ✅ 自动发现标志
│  │  └─ config.yaml        # 可选
│  │
│  └─ code-analyzer.yaml
│
├─ prompts/                 # Prompts 目录
│  ├─ code-review/
│  │  ├─ PROMPT.md          # ✅ 自动发现标志
│  │  └─ template.txt       # 可选
│  │
│  └─ api-doc.yaml
│
└─ orchestrator.yaml        # ⚪ 完全可选（高级配置）
```

---

## 1️⃣ Skills 约定

### 方式 1: 目录 + SKILL.md（推荐）

```
skills/code-review/
├─ SKILL.md           # 包含元数据
├─ main.py            # 入口文件（优先级最高）
├─ code_review.py     # 或同名文件
├─ helper.py          # 辅助模块
└─ test_simple.py     # 测试文件
```

**SKILL.md 示例**：

```markdown
---
name: code-review
description: Intelligent code review assistant
backend: claude
model: claude-3-5-sonnet-20241022
temperature: 0.5
dependencies:
  - command:git-diff
---

# Code Review Skill

AI-powered code review with best practice suggestions.

## Capabilities

- Static analysis
- Security vulnerability detection
- Performance optimization suggestions

## Input

- **code**: Code to review
- **language**: Programming language (optional)

## Output

Structured review report with ratings and suggestions.
```

**main.py 示例**：

```python
def execute(request, **kwargs):
    """Skill entry point."""
    code = kwargs.get('code', '')
    language = kwargs.get('language', 'auto')

    # Review logic here
    return {
        "success": True,
        "output": review_result
    }
```

**自动推断的配置**：
- `name`: 从 SKILL.md 前置元数据或标题提取
- `description`: 从 SKILL.md 提取
- `entry_point`: 自动查找 `main.py` 或 `{skill-name}.py`
- `backend`: 默认 `claude`（可在 SKILL.md 中覆盖）
- `priority`: 100（project 级）

---

### 方式 2: 单文件 YAML Skill

适合简单的基于 Prompt 的 Skills：

```yaml
# skills/simple-translator.yaml
name: simple-translator
description: Text translation skill
backend: gemini
model: gemini-2.0-flash
temperature: 0.3

system_prompt: |
  You are a professional translator.

user_prompt_template: |
  Translate the following text to {target_language}:

  {text}

examples:
  - name: English to Chinese
    input:
      text: "Hello world"
      target_language: "Chinese"
    output: "你好世界"
```

---

### 方式 3: 混合模式（覆盖自动推断）

```
skills/advanced-skill/
├─ SKILL.md           # 基础元数据
├─ skill.yaml         # 覆盖特定配置
└─ main.py
```

**skill.yaml** 会覆盖 SKILL.md 中的配置：

```yaml
# 只覆盖需要自定义的部分
backend: codex
temperature: 0.9
max_tokens: 8000
```

---

## 2️⃣ Commands 约定

### 方式 1: 目录 + COMMAND.md

```
commands/git-shortcuts/
├─ COMMAND.md
└─ commands.yaml (可选)
```

**COMMAND.md 示例**：

```markdown
---
name: git-shortcuts
description: Git command shortcuts collection
---

# Git Shortcuts

## Commands

```bash
git status -sb
```

## Usage

Quick git status with branch info.
```

**自动提取**：
- 从代码块提取 `command` 字段
- 支持多个命令（逗号分隔）

---

### 方式 2: YAML 文件

```yaml
# commands/docker-utils.yaml
name: docker-utils
description: Docker management commands
command: docker ps -a --format "table {{.Names}}\t{{.Status}}"
enabled: true
priority: 70
```

---

## 3️⃣ Agents 约定

### 方式 1: 目录 + AGENT.md

```
agents/custom-explorer/
├─ AGENT.md
└─ config.yaml (可选)
```

**AGENT.md 示例**：

```markdown
---
name: custom-explorer
description: Advanced code exploration agent
agent_type: explore
thoroughness: very_thorough
---

# Custom Code Explorer

Enhanced explorer with domain-specific optimizations.

## Features

- Deep directory traversal
- Semantic code search
- Dependency graph analysis
```

**自动推断**：
- `agent_type`: 从 AGENT.md 提取，默认 `general`
- `model`: 默认继承全局配置

---

### 方式 2: YAML 文件

```yaml
# agents/code-analyzer.yaml
name: code-analyzer
description: Static code analysis agent
agent_type: general
model: claude-3-5-sonnet-20241022
config:
  max_depth: 5
  include_tests: true
```

---

## 4️⃣ Prompts 约定

### 方式 1: 目录 + PROMPT.md

```
prompts/code-review/
├─ PROMPT.md        # 包含模板
└─ template.txt     # 或独立模板文件
```

**PROMPT.md 示例**：

```markdown
---
name: code-review
description: Code review prompt template
category: code-analysis
---

# Code Review Prompt

## Template

```
Please review the following {language} code:

{code}

Focus areas:
- {focus_areas}

Provide:
1. Overall assessment
2. Issues found
3. Improvement suggestions
```

## Variables

- `language`: Programming language
- `code`: Code to review
- `focus_areas`: Specific concerns
```

**自动提取**：
- 从 `## Template` 代码块提取模板
- 使用正则提取变量 `{variable_name}`

---

### 方式 2: 独立模板文件

```
prompts/api-doc/
├─ PROMPT.md        # 元数据
└─ template.txt     # 纯模板
```

**template.txt**：

```
Generate OpenAPI documentation for:

API Name: {api_name}
Endpoints: {endpoints}
Authentication: {auth_type}

Output in YAML format.
```

**PROMPT.md**（仅元数据）：

```markdown
---
name: api-doc
description: API documentation generator
variables:
  - api_name
  - endpoints
  - auth_type
---

# API Documentation Generator

Generates OpenAPI-compliant documentation.
```

---

### 方式 3: YAML 文件

```yaml
# prompts/simple-prompt.yaml
name: simple-prompt
description: Simple prompt template
template: |
  User request: {request}

  Please respond in {format} format.
variables:
  - request
  - format
```

---

## 资源发现优先级

每个资源目录的发现顺序：

```
1. 显式 YAML 文件（最高优先级）
   ├─ skill.yaml
   ├─ command.yaml
   ├─ agent.yaml
   └─ prompt.yaml

2. 目录约定（Marker 文件）
   ├─ SKILL.md
   ├─ COMMAND.md
   ├─ AGENT.md
   └─ PROMPT.md

3. Python 模块（最低优先级）
   └─ __init__.py
```

**配置覆盖优先级**：

```
项目 orchestrator.yaml (priority: 100)
  ↓
目录下的 YAML 文件 (priority: 100)
  ↓
SKILL.md 等 Marker 文件 (priority: 80)
  ↓
用户 ~/.claude/ (priority: 50)
  ↓
内置 builtin (priority: 10)
```

---

## 入口文件查找顺序

对于 Python Skills，自动查找入口文件的顺序：

```python
1. main.py                    # 最优先
2. {skill-name}.py            # 如 code-review.py
3. {skill_name}.py            # 如 code_review.py
4. __main__.py
5. 第一个非 test_ 的 .py 文件
```

---

## 使用示例

### 创建新 Skill（零配置）

```bash
# 1. 创建目录
mkdir -p skills/my-new-skill

# 2. 创建 SKILL.md
cat > skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: My awesome new skill
backend: claude
---

# My New Skill

Does amazing things!
EOF

# 3. 创建入口文件
cat > skills/my-new-skill/main.py << 'EOF'
def execute(request, **kwargs):
    return {"success": True, "output": "Hello from my skill!"}
EOF

# 4. 完成！自动发现并注册
python -m orchestrator.master_orchestrator
```

**无需修改 `orchestrator.yaml`**！

---

### 覆盖自动发现的配置

如果需要自定义某个参数：

```yaml
# orchestrator.yaml
skills:
  manual:
    - name: my-new-skill
      backend: gemini          # 仅覆盖 backend
      temperature: 0.9         # 添加额外参数
      # 其他配置继承自 SKILL.md
```

---

## 禁用自动发现

### 全局禁用

```python
from orchestrator.core.config_loader import ConfigLoader

# 禁用自动发现，只使用 YAML
loader = ConfigLoader(enable_auto_discovery=False)
```

### 禁用特定资源

```yaml
# orchestrator.yaml
skills:
  manual:
    - name: unwanted-skill
      enabled: false           # 禁用自动发现的 Skill
```

---

## 迁移指南

### 从 YAML 配置迁移到目录约定

**当前项目**（需要手动注册）：

```yaml
# orchestrator.yaml
skills:
  manual:
    - name: code-review
      path: ./skills/code-review/skill.yaml
    - name: api-gen
      path: ./skills/api-gen/skill.yaml
    # ... 20+ skills
```

**迁移后**（零配置）：

```bash
# 为每个 Skill 添加 SKILL.md
for skill_dir in skills/*/; do
  cat > "$skill_dir/SKILL.md" << EOF
---
name: $(basename $skill_dir)
description: Auto-discovered skill
---
# $(basename $skill_dir)
EOF
done

# 删除 orchestrator.yaml 中的手动注册
# 系统自动发现所有 Skills！
```

---

## 最佳实践

### ✅ 推荐做法

1. **使用 Marker 文件**（SKILL.md/COMMAND.md 等）
   - 清晰的元数据
   - 自动文档化
   - 支持覆盖

2. **遵循命名约定**
   - Skill 目录名使用 kebab-case：`my-skill`
   - 入口文件使用 snake_case：`my_skill.py`
   - YAML 前置元数据与文件名一致

3. **分层配置**
   - Marker 文件：基础配置
   - YAML 文件：覆盖特定参数
   - orchestrator.yaml：全局覆盖

4. **渐进式增强**
   - 从简单的 SKILL.md 开始
   - 需要时添加 skill.yaml
   - 复杂场景才用 orchestrator.yaml

---

### ❌ 避免的错误

1. ❌ 不要在多个地方重复定义相同配置
2. ❌ 不要直接修改 `skills/memex-cli/skills/`（内置）
3. ❌ 不要混用绝对路径和相对路径
4. ❌ 不要忘记添加 SKILL.md（否则无法自动发现）

---

## 调试和验证

### 查看已发现的资源

```python
from orchestrator import MasterOrchestrator

orch = MasterOrchestrator(auto_discover=True, verbose=True)

# 使用 Slash Command
result = orch.process("/list-skills")
print(result.output)
```

### 检查配置加载日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from orchestrator.core.config_loader import ConfigLoader

loader = ConfigLoader(enable_auto_discovery=True)
config = loader.load()

# 查看日志输出：
# INFO: Auto-discovery enabled via ResourceScanner
# INFO: Running auto-discovery for project resources...
# INFO: Discovered 3 skills in ./skills
# INFO: Auto-discovered: 3 skills, 2 commands, 1 agents, 2 prompts
```

---

## 常见问题

### Q: YAML 配置还需要吗？

**A**: 完全可选！对于简单项目，只需目录约定即可。YAML 仅用于高级覆盖。

### Q: 现有 YAML Skills 会失效吗？

**A**: 不会。系统同时支持 YAML 和目录约定，完全向后兼容。

### Q: 如何知道某个资源是如何发现的？

**A**: 使用 `/stats` Slash Command 查看详情：

```python
result = orch.process("/stats")
# 输出包含每个资源的 discovery_method
```

### Q: 可以混用多种方式吗？

**A**: 可以！同一个项目中：
- Skill A: SKILL.md 自动发现
- Skill B: YAML 文件
- Skill C: orchestrator.yaml 手动注册

### Q: Python 模块检测有什么限制？

**A**: 最低优先级，仅当无 YAML 和 Marker 文件时才触发。推荐明确使用 SKILL.md。

---

## 总结

**核心原则**：约定优于配置

- ✅ 遵循目录约定 → 自动发现
- ✅ 添加 Marker 文件 → 元数据推断
- ✅ 需要时使用 YAML → 精确控制

**收益**：
- 更少的配置文件
- 更清晰的项目结构
- 更快的开发速度
- 更好的自文档化

---

**下一步**：查看 [AUTO_DISCOVERY.md](./AUTO_DISCOVERY.md) 了解更多细节和高级用法。
