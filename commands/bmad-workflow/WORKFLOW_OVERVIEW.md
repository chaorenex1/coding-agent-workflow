# BMAD AI Agile Workflow System

## Overview

This is a complete **BMAD (Breakthrough Method for Agile AI-Driven Development)** workflow system designed for Solo developers building SaaS/Web applications. It combines:

- **1 主控命令** (`/bmad`) - 统一调度整个工作流
- **6 阶段命令** - 各阶段独立执行
- **8 专业Agent** - 角色化任务执行

---

## 主控调度器

```
/bmad [action] [args]
```

| Action | Description | Example |
|--------|-------------|---------|
| `init` | 初始化新项目 | `/bmad init "Product idea"` |
| `status` | 查看当前状态 | `/bmad status` |
| `next` | 执行下一步 | `/bmad next` |
| `phase [n]` | 跳转到阶段 | `/bmad phase 2` |
| `story [id]` | 处理特定Story | `/bmad story epic-001/story-001` |
| `resume` | 从断点恢复 | `/bmad resume` |
| `report` | 生成进度报告 | `/bmad report` |

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BMAD AI AGILE WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: ANALYSIS          Phase 2: PLANNING         Phase 3: ARCHITECTURE│
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐ │
│  │ /bmad-analyze   │   →    │ /bmad-plan      │   →    │ /bmad-architect │ │
│  │                 │        │                 │        │                 │ │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │        │ ┌─────────────┐ │ │
│  │ │  analyst    │ │        │ │product-owner│ │        │ │  architect  │ │ │
│  │ │   agent     │ │        │ │   agent     │ │        │ │   agent     │ │ │
│  │ └─────────────┘ │        │ └─────────────┘ │        │ └─────────────┘ │ │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘ │
│           │                          │                          │          │
│           ▼                          ▼                          ▼          │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐ │
│  │ project-brief.md│        │ prd.md          │        │ architecture.md │ │
│  │ market-analysis │        │ user-stories.md │        │ tech-spec.md    │ │
│  └─────────────────┘        └─────────────────┘        └─────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 4: DEVELOPMENT       Phase 5: TESTING          Phase 6: DEPLOYMENT  │
│  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐ │
│  │ /bmad-develop   │   →    │ /bmad-test      │   →    │ /bmad-deploy    │ │
│  │                 │        │                 │        │                 │ │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │        │ ┌─────────────┐ │ │
│  │ │ fullstack   │ │        │ │    qa       │ │        │ │   devops    │ │ │
│  │ │  developer  │ │        │ │   agent     │ │        │ │   agent     │ │ │
│  │ └─────────────┘ │        │ └─────────────┘ │        │ └─────────────┘ │ │
│  │ ┌─────────────┐ │        └─────────────────┘        └─────────────────┘ │
│  │ │scrum-master │ │                                                       │
│  │ │   agent     │ │                                                       │
│  │ └─────────────┘ │                                                       │
│  └─────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 主控 (1)

| Command | Purpose | Key Actions |
|---------|---------|-------------|
| `/bmad` | 统一工作流调度 | init, status, next, phase, story, resume, report |

### Slash Commands (6)

| Command | Phase | Purpose | 文件沉淀 |
|---------|-------|---------|----------|
| `/bmad-analyze` | 1 | Market research & project brief | `docs/bmad/01-analysis/` |
| `/bmad-plan` | 2 | PRD & user stories creation | `docs/bmad/02-planning/` |
| `/bmad-architect` | 3 | Technical architecture design | `docs/bmad/03-architecture/` |
| `/bmad-develop` | 4 | Story-driven development | `docs/bmad/04-development/` |
| `/bmad-test` | 5 | Quality assurance & validation | `docs/bmad/05-testing/` |
| `/bmad-deploy` | 6 | Deployment & release | `docs/bmad/06-deployment/` |

### Agents (8)

| Agent | Type | Role | Color |
|-------|------|------|-------|
| `bmad-orchestrator` | Coordination | **主控调度器** - 管理整个工作流 | purple |
| `bmad-analyst` | Strategic | Market research & validation | blue |
| `bmad-product-owner` | Strategic | Product requirements & priorities | blue |
| `bmad-architect` | Strategic | System design & tech decisions | blue |
| `bmad-scrum-master` | Coordination | Epic sharding & story management | purple |
| `bmad-fullstack-dev` | Implementation | Full-stack development | green |
| `bmad-qa` | Quality | Testing & quality validation | red |
| `bmad-devops` | Implementation | CI/CD & deployment | orange |

---

## 文件沉淀结构

BMAD工作流强制使用标准化目录结构：

```
your-project/
├── .bmad/                              # 🔧 BMAD配置和状态
│   ├── config.yaml                     # 项目配置
│   ├── state.yaml                      # 当前工作流状态
│   └── history/                        # 状态变更历史
│       └── [timestamp]-[action].yaml
│
├── docs/bmad/                          # 📚 BMAD文档沉淀
│   ├── 01-analysis/                    # Phase 1 产出
│   │   ├── project-brief.md            # 项目简报
│   │   └── market-analysis.md          # 市场分析
│   │
│   ├── 02-planning/                    # Phase 2 产出
│   │   ├── prd.md                      # 产品需求文档
│   │   └── user-stories.md             # 用户故事
│   │
│   ├── 03-architecture/                # Phase 3 产出
│   │   ├── architecture.md             # 系统架构
│   │   ├── tech-spec.md                # 技术规格
│   │   └── database-schema.sql         # 数据库Schema
│   │
│   ├── 04-development/                 # Phase 4 产出
│   │   ├── _progress.md                # 开发进度追踪
│   │   └── epics/                      # Epic和Story文件
│   │       ├── epic-001/
│   │       │   ├── _epic.md            # Epic概览
│   │       │   ├── story-001.md        # Story详情
│   │       │   └── story-002.md
│   │       └── epic-002/
│   │
│   ├── 05-testing/                     # Phase 5 产出
│   │   ├── test-report.md              # 测试报告
│   │   └── coverage/                   # 覆盖率报告
│   │
│   └── 06-deployment/                  # Phase 6 产出
│       ├── deployment-log.md           # 部署日志
│       └── runbook.md                  # 运维手册
│
├── src/                                # 💻 代码产出
├── tests/                              # 🧪 测试代码
└── .github/workflows/                  # ⚙️ CI/CD配置
```

### 状态文件 `.bmad/state.yaml`

```yaml
version: "1.0"
project:
  name: "AI Task Manager"
  created_at: "2025-01-05"

workflow:
  current_phase: 4
  phase_status:
    1: completed
    2: completed
    3: completed
    4: in_progress
    5: pending
    6: pending
  current_epic: epic-001
  current_story: story-003

development:
  epics:
    - id: epic-001
      name: "Authentication"
      status: in_progress
      stories:
        - id: story-001
          status: completed
        - id: story-002
          status: completed
        - id: story-003
          status: in_progress

metrics:
  stories_completed: 2
  stories_total: 12
  test_coverage: 0
```

---

## Installation

### 1. Install Slash Commands

```bash
# Copy commands to Claude Code
cp generated-commands/bmad-workflow/*.md ~/.claude/commands/

# Or for project-level
mkdir -p .claude/commands
cp generated-commands/bmad-workflow/*.md .claude/commands/
```

### 2. Install Agents

```bash
# Copy agents to Claude Code
cp .claude/agents/bmad-*.md ~/.claude/agents/

# Or for project-level
# Agents are already in .claude/agents/
```

---

## Quick Start

### 使用主控 (推荐)

```bash
# 初始化项目 - 自动创建目录结构和状态文件
/bmad init "AI-powered task management SaaS for remote teams"

# 查看当前状态
/bmad status

# 执行下一步 (自动判断应该做什么)
/bmad next

# 继续执行直到完成...
/bmad next
/bmad next
...
```

### 手动执行各阶段

```bash
# Phase 1: Analyze your idea
/bmad-analyze "AI-powered task management SaaS for remote teams"

# Phase 2: Create product requirements
/bmad-plan

# Phase 3: Design architecture
/bmad-architect

# Phase 4: Develop features (story by story)
/bmad-develop epic-001/story-001

# Phase 5: Test implementation
/bmad-test

# Phase 6: Deploy to production
/bmad-deploy staging
```

### 从断点恢复

```bash
# 查看当前状态
/bmad status

# 从断点恢复
/bmad resume

# 或跳转到特定阶段
/bmad phase 3
```

---

## Best Practices

### 1. Version Everything
All BMAD artifacts are committed to git immediately after creation.

### 2. Active Control
You steer the AI through documented constraints rather than passively reviewing output.

### 3. Incremental Development
Work on one story at a time, validate, then proceed to next.

### 4. Continuous Integration
Each story completion triggers automated CI/CD pipelines.

---

## Agent Execution Patterns

### Parallel-Safe (Strategic Agents)
```
bmad-analyst + bmad-product-owner + bmad-architect
(Can run 3-4 agents simultaneously for planning phases)
```

### Coordinated (Implementation Agents)
```
bmad-fullstack-dev + bmad-scrum-master
(2-3 agents working on different files)
```

### Sequential (Quality Agents)
```
bmad-qa → bmad-devops
(One at a time for heavy operations)
```

---

## Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [Applied BMAD - Reclaiming Control in AI Development](https://bennycheung.github.io/bmad-reclaiming-control-in-ai-dev)
- [BMAD: AI-Powered Agile Framework Overview](https://nayakpplaban.medium.com/bmad-ai-powered-agile-framework-overview-238d4af39aa4)

---

**Version**: 1.0.0
**Last Updated**: 2025-01-05
**Based on**: BMAD-METHOD v6 Alpha
