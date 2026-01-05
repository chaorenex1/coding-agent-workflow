# Coding Base - Claude Code 项目指南

本项目是一个 Claude Code 扩展工具库，包含 Skills、Agents 和 Commands (Slash Commands)，用于增强 Claude Code 的能力。

---

## 项目结构

```
coding_base/
├── skills/           # 可复用的技能模块 (通过 /skill 调用)
├── agents/           # 专业化 Agent 定义 (通过 Task 工具调用)
├── commands/         # Slash Commands (通过 / 前缀调用)
├── prompts/          # 提示模板
├── docs/             # 项目文档
└── scripts/          # 工具脚本
```

---

## Skills (技能模块)

Skills 是可复用的功能模块，通过 SKILL.md 文件定义。每个 skill 目录包含入口脚本和相关资源。

### 可用 Skills

| Skill 名称 | 描述 | 入口 |
|-----------|------|------|
| `master-orchestrator` | 智能任务协调系统，支持意图分析、多模式执行 | `master_orchestrator.py` |
| `cross-backend-orchestrator` | 跨后端 AI 协调器 | `orchestrator.py` |
| `codex-cli-bridge` | Codex CLI 集成桥接 | - |
| `git-commit-summarizer` | Git 提交智能总结 | - |
| `git-code-review` | Git 代码审查助手 | - |
| `code-refactor-analyzer` | 代码重构分析器 | `refactor_analyzer.py` |
| `api-document-generator` | API 文档生成器 | `api_document_generator.py` |
| `repo-analyzer` | 仓库结构分析 | - |
| `tech-stack-evaluator` | 技术栈评估工具 | - |
| `skill-validator` | Skill 验证器 | `skill_validator.py` |
| `github-stars-analyzer` | GitHub Stars 分析 | - |
| `code-fix-assistant` | 代码修复助手 | - |
| `code-refactoring-assistant` | 代码重构助手 | - |
| `chinese-interface-doc-generator` | 中文接口文档生成 | - |
| `cross-platform-command-generator` | 跨平台命令生成 | - |
| `memex-cli` | Memex CLI 工具 | - |
| `ux-design-gemini` | UX 设计 (Gemini) | - |
| `code-with-codex` | Codex 代码协作 | - |
| `priority-optimization-assistant` | 优先级优化助手 | - |
| `multcode-dev-workflow-agent` | 多代码开发工作流 | - |
| `git-batch-commit` | Git 批量提交工具 | - |

### 调用方式

```bash
# 方式 1: 直接使用 Skill 工具
/skill master-orchestrator "开发一个博客系统"

# 方式 2: Python 脚本直接执行
cd skills/master-orchestrator
python master_orchestrator.py "任务描述" -v
```

---

## Agents (专业化代理)

Agents 是专业化的 AI 代理，通过 YAML frontmatter 定义其能力和工具访问权限。

### Agent 分组

#### bmad-workflow (BMAD 完整工作流)
用于从零开始的项目开发，完整的需求-设计-开发-测试-部署流程。

| Agent | 描述 |
|-------|------|
| `bmad-orchestrator` | 工作流总协调器 |
| `bmad-analyst` | 需求分析师 |
| `bmad-product-owner` | 产品负责人 |
| `bmad-architect` | 系统架构师 |
| `bmad-scrum-master` | Scrum Master |
| `bmad-fullstack-dev` | 全栈开发者 |
| `bmad-qa` | 质量保证 |
| `bmad-devops` | DevOps 工程师 |

#### bmad-iterate (BMAD 迭代开发)
用于已有项目的迭代开发和变更管理。

| Agent | 描述 |
|-------|------|
| `bmad-iter-orchestrator` | 迭代协调器 |
| `bmad-diff-analyst` | 差异分析师 |
| `bmad-iteration-planner` | 迭代规划师 |
| `bmad-impact-analyst` | 影响分析师 |
| `bmad-iter-developer` | 迭代开发者 |
| `bmad-regression-tester` | 回归测试员 |
| `bmad-release-manager` | 发布管理员 |

#### prd-workflow (PRD 驱动开发)
基于 PRD 文档的开发工作流。

| Agent | 描述 |
|-------|------|
| `development-workflow-orchestrator` | 开发工作流协调器 |
| `requirement-analysis-agent` | 需求分析 |
| `design-architecture-agent` | 设计架构 |
| `codebase-analyzer-agent` | 代码库分析 |
| `implementation-agent` | 实现代理 |
| `testing-qa-agent` | 测试 QA |
| `deployment-release-agent` | 部署发布 |

#### quick-code (快速开发)
用于快速实现小型功能和重构任务。

| Agent | 描述 |
|-------|------|
| `fa-orchestrator-quick-feature` | 快速功能协调器 |
| `fa-requirements-analyst-quick-feature` | 需求分析 |
| `fa-developer-quick-feature` | 开发者 |
| `fa-code-reviewer-quick-feature` | 代码审查 |
| `fa-tester-quick-feature` | 测试员 |
| `refactor-analyzer` | 重构分析器 |
| `refactor-executor` | 重构执行器 |
| `rename-detective` | 重命名检测 |
| `impact-analyzer` | 影响分析 |

#### feature-workflow (功能开发)
独立功能开发工作流。

| Agent | 描述 |
|-------|------|
| `feature-development-assistant` | 功能开发助手 |
| `code-refactoring-assistant` | 代码重构助手 |
| `mini-feature-implementer` | 迷你功能实现器 |

#### automation (自动化任务)
自动化和专业领域代理。

| Agent | 描述 |
|-------|------|
| `ai-workflow-architect` | AI 工作流架构师 |
| `kubernetes-expert` | Kubernetes 专家 |
| `prompt-style-analyzer` | 提示风格分析器 |
| `rust-tauri-app-builder` | Rust/Tauri 应用构建 |
| `documentation-sync-agent` | 文档同步代理 |
| `comprehensive-analysis-report-generator` | 综合分析报告生成器 |

### 调用方式

Agents 通过 Task 工具调用，参考 agent 文件中的 frontmatter 定义：

```yaml
---
name: agent-name
description: Agent description
tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: opus | sonnet | haiku
---
```

---

## Commands (Slash Commands)

Commands 是可直接通过 `/` 前缀调用的命令，提供快捷的工作流入口。

### 可用 Commands

#### BMAD Workflow Commands
| Command | 描述 |
|---------|------|
| `/bmad` | 启动 BMAD 完整工作流 |
| `/bmad-analyze` | 执行需求分析阶段 |
| `/bmad-plan` | 执行产品规划阶段 |
| `/bmad-architect` | 执行架构设计阶段 |
| `/bmad-develop` | 执行开发阶段 |
| `/bmad-test` | 执行测试阶段 |
| `/bmad-deploy` | 执行部署阶段 |

#### BMAD Iterate Commands
| Command | 描述 |
|---------|------|
| `/bmad-iter` | 启动 BMAD 迭代工作流 |
| `/bmad-iter-diff` | 差异分析 |
| `/bmad-iter-plan` | 迭代规划 |
| `/bmad-iter-impact` | 影响分析 |
| `/bmad-iter-dev` | 迭代开发 |
| `/bmad-iter-test` | 回归测试 |
| `/bmad-iter-release` | 发布管理 |

#### Quick Code Commands
| Command | 描述 |
|---------|------|
| `/quick-feature` | 快速功能开发 |
| `/quick-rename` | 快速重命名重构 |
| `/quick-refactor` | 快速代码重构 |
| `/rename-fixer` | 重命名修复器 |

#### Project Analyzer Commands
| Command | 描述 |
|---------|------|
| `/code-reader` | 代码阅读和理解 |
| `/code-boundary` | 代码边界分析 |
| `/code-design` | 代码设计分析 |
| `/code-impact-analysis` | 代码影响分析 |
| `/code-interface` | 接口分析 |
| `/code-review` | 代码审查 |
| `/project-architecture` | 项目架构分析 |

#### Scaffold Commands
| Command | 描述 |
|---------|------|
| `/project-scaffold` | 项目脚手架生成 |
| `/electron-scaffold` | Electron 应用脚手架 |

#### PRD Workflow Commands
| Command | 描述 |
|---------|------|
| `/dev-workflow` | PRD 驱动开发工作流 |

### 使用示例

```bash
# 启动 BMAD 完整工作流
/bmad "开发一个任务管理系统"

# 快速开发一个新功能
/quick-feature "添加用户登录功能"

# 分析项目架构
/project-architecture

# 代码审查
/code-review src/main.py

# 迭代开发 - 分析需求变更
/bmad-iter-diff "新增用户权限管理"
```

---

## 快速开始

### 场景 1: 开发新项目
```bash
# 使用 BMAD 完整工作流
/bmad "项目描述"
```

### 场景 2: 迭代现有项目
```bash
# 使用 BMAD 迭代工作流
/bmad-iter "需求变更描述"
```

### 场景 3: 快速实现小功能
```bash
# 使用 Quick Feature
/quick-feature "功能描述"
```

### 场景 4: 代码分析和重构
```bash
# 架构分析
/project-architecture

# 代码审查
/code-review <file_path>

# 快速重构
/quick-refactor "重构目标"
```

---

## 配置说明

### Skills 配置
每个 skill 通过 `SKILL.md` 文件定义，包含：
- `name`: Skill 名称
- `description`: 描述
- `entry`: 入口文件
- `category`: 分类
- `tags`: 标签

### Agents 配置
每个 agent 通过 YAML frontmatter 定义，包含：
- `name`: Agent 名称
- `description`: 描述
- `tools`: 可用工具列表
- `model`: 推荐模型 (opus/sonnet/haiku)

### Commands 配置
每个 command 通过 markdown 文件定义，包含：
- `name`: 命令名称
- `description`: 描述
- 使用说明和参数定义

---

## 最佳实践

1. **选择合适的工作流**:
   - 新项目 → `/bmad`
   - 迭代开发 → `/bmad-iter`
   - 小功能 → `/quick-feature`

2. **理解代码再修改**:
   - 使用 `/project-architecture` 了解项目结构
   - 使用 `/code-review` 审查关键代码

3. **利用专业 Agents**:
   - 架构问题 → `bmad-architect`
   - 测试问题 → `bmad-qa`
   - 部署问题 → `bmad-devops`

4. **组合使用**:
   - 先分析 (`/code-impact-analysis`)
   - 再规划 (`/bmad-iter-plan`)
   - 最后实现 (`/bmad-iter-dev`)
