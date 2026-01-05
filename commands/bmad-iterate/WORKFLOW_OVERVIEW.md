# BMAD Iteration Workflow System

## Overview

This is a **Product Iteration** workflow based on BMAD methodology, designed for **existing products** that need continuous feature iteration. Unlike the "new product" workflow that starts from scratch, this workflow:

- **从PRD差异中提取迭代需求**
- **支持混合迭代周期** (Sprint/快速/持续交付)
- **与现有代码库无缝集成**
- **独立于全新产品工作流运行**

---

## 迭代工作流 vs 全新产品工作流

| 维度 | 全新产品 (`/bmad`) | 产品迭代 (`/bmad-iter`) |
|------|-------------------|------------------------|
| **起点** | 产品想法 | 现有PRD + 变更需求 |
| **Phase 1** | 市场分析 | PRD差异分析 |
| **Phase 2** | 完整PRD创建 | 增量PRD更新 |
| **Phase 3** | 全新架构设计 | 影响分析 + 增量设计 |
| **Phase 4** | 从零开发 | 增量开发 |
| **状态管理** | `.bmad/state.yaml` | `.bmad-iter/state.yaml` |
| **文档沉淀** | `docs/bmad/` | `docs/bmad-iter/` |

---

## 主控调度器

```
/bmad-iter [action] [args]
```

| Action | Description | Example |
|--------|-------------|---------|
| `start` | 开始新迭代 | `/bmad-iter start "v2.1 Feature Update"` |
| `diff` | 分析PRD变更 | `/bmad-iter diff` |
| `plan` | 规划迭代范围 | `/bmad-iter plan` |
| `status` | 查看迭代状态 | `/bmad-iter status` |
| `next` | 执行下一步 | `/bmad-iter next` |
| `story [id]` | 处理特定Story | `/bmad-iter story iter-001/story-001` |
| `release` | 准备发布 | `/bmad-iter release` |
| `close` | 关闭迭代 | `/bmad-iter close` |

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BMAD ITERATION WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │  /bmad-iter      │  ← 主控调度器                                         │
│  │  start/diff/plan │                                                       │
│  │  status/next/... │                                                       │
│  └────────┬─────────┘                                                       │
│           │                                                                 │
│           ▼                                                                 │
│  Phase 1: DIFF ANALYSIS     Phase 2: ITERATION PLANNING                    │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │ /bmad-iter-diff │   →    │ /bmad-iter-plan │                            │
│  │                 │        │                 │                            │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │                            │
│  │ │  diff       │ │        │ │  iteration  │ │                            │
│  │ │  analyst    │ │        │ │  planner    │ │                            │
│  │ └─────────────┘ │        │ └─────────────┘ │                            │
│  └─────────────────┘        └─────────────────┘                            │
│           │                          │                                      │
│           ▼                          ▼                                      │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │ diff-report.md  │        │ iteration-plan  │                            │
│  │ change-list.md  │        │ iter-stories.md │                            │
│  └─────────────────┘        └─────────────────┘                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 3: IMPACT ANALYSIS   Phase 4: INCREMENTAL DEV                       │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │/bmad-iter-impact│   →    │ /bmad-iter-dev  │                            │
│  │                 │        │                 │                            │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │                            │
│  │ │  impact     │ │        │ │  iter       │ │                            │
│  │ │  analyst    │ │        │ │  developer  │ │                            │
│  │ └─────────────┘ │        │ └─────────────┘ │                            │
│  └─────────────────┘        └─────────────────┘                            │
│           │                          │                                      │
│           ▼                          ▼                                      │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │ impact-report   │        │ Code changes    │                            │
│  │ design-delta    │        │ Tests           │                            │
│  └─────────────────┘        └─────────────────┘                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 5: REGRESSION TEST   Phase 6: RELEASE                               │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │ /bmad-iter-test │   →    │/bmad-iter-release│                           │
│  │                 │        │                 │                            │
│  │ ┌─────────────┐ │        │ ┌─────────────┐ │                            │
│  │ │  regression │ │        │ │  release    │ │                            │
│  │ │  tester     │ │        │ │  manager    │ │                            │
│  │ └─────────────┘ │        │ └─────────────┘ │                            │
│  └─────────────────┘        └─────────────────┘                            │
│           │                          │                                      │
│           ▼                          ▼                                      │
│  ┌─────────────────┐        ┌─────────────────┐                            │
│  │ regression-rpt  │        │ release-notes   │                            │
│  │ test-coverage   │        │ changelog       │                            │
│  └─────────────────┘        └─────────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 迭代流程详解

### Phase 1: PRD差异分析 (`/bmad-iter-diff`)

从现有PRD和新需求中提取变更：

```
输入:
- 现有PRD (docs/bmad/02-planning/prd.md)
- 新PRD或变更请求

输出:
- docs/bmad-iter/[iter-id]/01-diff/diff-report.md
- docs/bmad-iter/[iter-id]/01-diff/change-list.md
```

**变更类型识别**:
- `ADD` - 新增功能
- `MODIFY` - 功能修改
- `ENHANCE` - 功能增强
- `DEPRECATE` - 功能废弃
- `FIX` - 缺陷修复

### Phase 2: 迭代规划 (`/bmad-iter-plan`)

基于差异分析规划迭代范围：

```
输入:
- 差异报告
- 资源约束
- 优先级指导

输出:
- docs/bmad-iter/[iter-id]/02-plan/iteration-plan.md
- docs/bmad-iter/[iter-id]/02-plan/iter-stories.md
```

**迭代周期选择**:
- **Sprint** (1-2周): 多个中等Story
- **快速迭代** (1-3天): 1-3个小Story
- **持续交付**: 单个Story即发布

### Phase 3: 影响分析 (`/bmad-iter-impact`)

分析变更对现有系统的影响：

```
输入:
- 迭代计划
- 现有架构 (docs/bmad/03-architecture/)
- 现有代码库

输出:
- docs/bmad-iter/[iter-id]/03-impact/impact-report.md
- docs/bmad-iter/[iter-id]/03-impact/design-delta.md
```

**影响评估维度**:
- 代码文件影响范围
- 数据库Schema变更
- API契约变更
- 依赖变更
- 测试影响范围

### Phase 4: 增量开发 (`/bmad-iter-dev`)

基于影响分析进行增量开发：

```
输入:
- 设计增量
- Story详情
- 现有代码

输出:
- 代码变更
- 单元测试
- 文档更新
```

**开发策略**:
- 最小化代码侵入
- 保持向后兼容
- 特性开关控制
- 增量式重构

### Phase 5: 回归测试 (`/bmad-iter-test`)

确保变更不破坏现有功能：

```
输入:
- 代码变更
- 影响范围
- 现有测试套件

输出:
- docs/bmad-iter/[iter-id]/05-test/regression-report.md
- 测试覆盖率报告
```

**测试策略**:
- 影响范围内的单元测试
- 接口回归测试
- E2E关键路径测试
- 性能回归检测

### Phase 6: 发布管理 (`/bmad-iter-release`)

准备发布和文档更新：

```
输入:
- 测试报告
- 代码变更摘要
- 版本号

输出:
- docs/bmad-iter/[iter-id]/06-release/release-notes.md
- CHANGELOG.md 更新
- 部署执行
```

---

## 文件沉淀结构

```
project-root/
├── .bmad-iter/                         # 🔧 迭代配置和状态
│   ├── config.yaml                     # 迭代配置
│   ├── state.yaml                      # 当前迭代状态
│   └── history/                        # 迭代历史
│
├── docs/
│   ├── bmad/                           # 📚 基础产品文档 (不变)
│   │   ├── 01-analysis/
│   │   ├── 02-planning/
│   │   │   ├── prd.md                  # 基线PRD ⭐
│   │   │   └── user-stories.md
│   │   └── 03-architecture/
│   │       └── architecture.md         # 基线架构 ⭐
│   │
│   └── bmad-iter/                      # 📚 迭代文档沉淀
│       ├── iter-2025-01/               # 迭代ID (按时间或版本)
│       │   ├── 01-diff/
│       │   │   ├── diff-report.md      # PRD差异报告
│       │   │   └── change-list.md      # 变更清单
│       │   ├── 02-plan/
│       │   │   ├── iteration-plan.md   # 迭代计划
│       │   │   └── iter-stories.md     # 迭代Story
│       │   ├── 03-impact/
│       │   │   ├── impact-report.md    # 影响分析报告
│       │   │   └── design-delta.md     # 设计增量
│       │   ├── 04-dev/
│       │   │   └── stories/
│       │   │       ├── story-001.md
│       │   │       └── story-002.md
│       │   ├── 05-test/
│       │   │   └── regression-report.md
│       │   └── 06-release/
│       │       └── release-notes.md
│       │
│       └── iter-2025-02/               # 下一个迭代
│           └── ...
│
└── src/                                # 代码
```

---

## 状态管理

### `.bmad-iter/state.yaml`

```yaml
version: "1.0"

current_iteration:
  id: "iter-2025-01"
  name: "v2.1 Feature Update"
  type: sprint              # sprint | quick | continuous
  started_at: "2025-01-05"
  target_date: "2025-01-19"

workflow:
  current_phase: 4          # 1-6
  phase_status:
    1: completed            # diff
    2: completed            # plan
    3: completed            # impact
    4: in_progress          # dev
    5: pending              # test
    6: pending              # release
  current_story: story-002

changes:
  total: 5
  completed: 2
  stories:
    - id: story-001
      type: ADD
      title: "Add notification system"
      status: completed
    - id: story-002
      type: MODIFY
      title: "Enhance user profile"
      status: in_progress
    - id: story-003
      type: ENHANCE
      title: "Improve dashboard performance"
      status: pending

metrics:
  code_changes: 15          # files changed
  tests_added: 8
  tests_modified: 3
  coverage_delta: +2.3%

baseline:
  prd_version: "1.0.0"
  architecture_version: "1.0.0"
  last_release: "v2.0.0"
```

---

## Components

### 主控 (1)

| Command | Purpose | Key Actions |
|---------|---------|-------------|
| `/bmad-iter` | 迭代工作流调度 | start, diff, plan, status, next, story, release, close |

### Slash Commands (6)

| Command | Phase | Purpose | 文件沉淀 |
|---------|-------|---------|----------|
| `/bmad-iter-diff` | 1 | PRD差异分析 | `docs/bmad-iter/[id]/01-diff/` |
| `/bmad-iter-plan` | 2 | 迭代规划 | `docs/bmad-iter/[id]/02-plan/` |
| `/bmad-iter-impact` | 3 | 影响分析 | `docs/bmad-iter/[id]/03-impact/` |
| `/bmad-iter-dev` | 4 | 增量开发 | `docs/bmad-iter/[id]/04-dev/` |
| `/bmad-iter-test` | 5 | 回归测试 | `docs/bmad-iter/[id]/05-test/` |
| `/bmad-iter-release` | 6 | 发布管理 | `docs/bmad-iter/[id]/06-release/` |

### Agents (7)

| Agent | Type | Role | Color |
|-------|------|------|-------|
| `bmad-iter-orchestrator` | Coordination | **主控调度器** | purple |
| `bmad-diff-analyst` | Strategic | PRD差异分析专家 | blue |
| `bmad-iteration-planner` | Strategic | 迭代规划专家 | blue |
| `bmad-impact-analyst` | Strategic | 影响分析专家 | blue |
| `bmad-iter-developer` | Implementation | 增量开发专家 | green |
| `bmad-regression-tester` | Quality | 回归测试专家 | red |
| `bmad-release-manager` | Coordination | 发布管理专家 | orange |

---

## Quick Start

### 典型迭代流程

```bash
# 1. 开始新迭代
/bmad-iter start "v2.1 Feature Update"

# 2. 分析PRD变更
/bmad-iter diff

# 3. 规划迭代范围
/bmad-iter plan

# 4. 查看状态
/bmad-iter status

# 5. 执行下一步 (重复直到完成)
/bmad-iter next
/bmad-iter next
...

# 6. 发布
/bmad-iter release

# 7. 关闭迭代
/bmad-iter close
```

### 快速修复流程

```bash
# 跳过规划，直接处理单个变更
/bmad-iter start "Hotfix: Login bug"
/bmad-iter-dev "Fix login validation"
/bmad-iter-test
/bmad-iter-release
```

---

## 迭代周期策略

### Sprint (1-2周)

```yaml
iteration:
  type: sprint
  duration: 2w
  ceremonies:
    - sprint_planning: Day 1
    - daily_standup: Daily
    - sprint_review: Last day
  stories: 5-10
```

### 快速迭代 (1-3天)

```yaml
iteration:
  type: quick
  duration: 3d
  stories: 1-3
  skip_phases:
    - impact_analysis  # 如果变更简单
```

### 持续交付

```yaml
iteration:
  type: continuous
  trigger: story_complete
  auto_release: true
  feature_flags: enabled
```

---

## PRD差异检测示例

### 输入: PRD变更

```diff
## 3.1 用户管理功能

### 3.1.1 用户注册
- 支持邮箱注册
- 支持手机号注册
+ - 支持微信登录 [NEW]
+ - 支持Google登录 [NEW]

### 3.1.2 用户资料
- 基本信息编辑
+ - 头像上传支持裁剪 [ENHANCE]
+ - 个人主页公开设置 [NEW]
```

### 输出: 变更清单

```markdown
## 变更清单

| ID | Type | Title | Priority | Effort |
|----|------|-------|----------|--------|
| CHG-001 | ADD | 微信登录 | P1 | M |
| CHG-002 | ADD | Google登录 | P1 | M |
| CHG-003 | ENHANCE | 头像裁剪 | P2 | S |
| CHG-004 | ADD | 主页公开设置 | P2 | S |
```

---

## Installation

```bash
# 安装迭代工作流命令
cp generated-commands/bmad-iterate/*.md ~/.claude/commands/

# 安装迭代专用Agent
cp .claude/agents/bmad-iter-*.md ~/.claude/agents/
cp .claude/agents/bmad-diff-*.md ~/.claude/agents/
cp .claude/agents/bmad-impact-*.md ~/.claude/agents/
cp .claude/agents/bmad-regression-*.md ~/.claude/agents/
cp .claude/agents/bmad-release-*.md ~/.claude/agents/
```

---

## Sources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [Applied BMAD - Reclaiming Control in AI Development](https://bennycheung.github.io/bmad-reclaiming-control-in-ai-dev)

---

**Version**: 1.0.0
**Last Updated**: 2025-01-05
**Type**: Product Iteration Workflow
