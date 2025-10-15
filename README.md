# coding-agent-workflow

一个面向多角色协同的 AI 智能体工作流与提示工程资料库。它为“BMAD”风格的全流程开发协作提供可复用的角色定义、指令模板与输出样式，覆盖产品需求、系统架构、Scrum 规划、开发实现、代码评审与质量保障等环节，支持中英文两套内容。

本仓库更像是“方法与模板”的集合，可直接作为大语言模型（LLM）的系统提示/工具说明使用，也可按需裁剪到你的自动化编排或 Agent 框架中。

## 适用对象

- 希望用一套可落地的多角色 AI 协作流程（PO/Architect/SM/Dev/QA）的团队或个人
- 需要结构化、可评分、可确认门控的交互式开发流程
- 想快速复用专业角色提示与输出规范的人/团队

---

## 仓库结构概览

```text
CN/                      # 中文角色与命令模板
  agents/               # 角色定义（架构师、Dev、QA、PO、Scrum Master 等）
  commands/             # 命令/流程驱动模板（如 bmad-pilot）
  req/                  # 需求相关模板（生成/评审/测试等）
  output-styles/        # 输出风格规范

EN/                      # 英文角色与命令模板（与中文目录对应）
  agents/               # General agent 与各类角色模板
  commands/             # 命令/流程驱动模板（ask/code/debug/refactor 等）
  output-styles/        # 输出风格规范

CLAUDE.md                # 额外的通用指令/约定（示例：语言/自报不确定等）
env/                     # 预留的环境/集成相关资源（如有）
```

> 提示：中文/英文两套资料内容相互呼应，可按团队语言偏好选择其一或混用。

---

## 什么是 BMAD 工作流

BMAD 是一种以“多角色智能体协作”为核心的开发工作流抽象，强调质量门控与用户显式确认：

- 角色分工：PO（产品）、Architect（架构）、SM（Scrum 规划）、Dev（开发）、QA（测试）
- 阶段推进：
  - Phase 0 仓库上下文扫描（可选，默认开启）
  - Phase 1 产品需求（PRD）
  - Phase 2 系统架构设计
  - Phase 3 Sprint 计划（可选，支持直接进入开发）
  - Phase 4 开发实现（含代码评审）
  - Phase 5 质量保障（可跳过）
- 质量门控：PRD 与架构需达到 ≥ 90 分的质量评分，并在继续前获得用户“明确同意”
- 产物存放（建议约定）：
  - ./.claude/specs/{feature_name}/00-repo-scan.md
  - ./.claude/specs/{feature_name}/01-product-requirements.md
  - ./.claude/specs/{feature_name}/02-system-architecture.md
  - ./.claude/specs/{feature_name}/03-sprint-plan.md
  - ./.claude/specs/{feature_name}/04-dev-reviewed.md

仓库中模板同时引入了 UltraThink 方法论（系统化假设-证据-模式-综合-验证），并在关键阶段提供评分维度与示例提问，便于对齐质量标准与决策透明度。

---

## 快速开始（两种方式）

方式 A：把模板当“系统提示/工具说明”直接用在你常用的 LLM 工具中

- 选择语言目录：`CN/` 或 `EN/`
- 先阅读对应命令模板：
  - 中文：`CN/commands/bmad/bmad-pilot.md`
  - 英文：`EN/commands/general_agent/bmad-pilot.md`
- 将该文件内容作为“系统提示/工具说明”，再输入你的项目目标（例如“/bmad-pilot 构建一个… 的 Web 应用”）
- 按模板的交互式门控进行迭代，达到评分阈值后再确认保存与推进

方式 B：嵌入你的 Agent/编排框架

- 将 `agents/` 下的角色定义接入你的多 Agent 编排（Orchestrator/Router/Planner）
- 将 `commands/` 下的流程模板作为“任务剧本/工具命令”的 Prompt 规范
- 将 `output-styles/` 下的样式用于统一输出格式与产物路径
- 将“质量门控 + 显式确认”作为编排节点条件，驱动下一阶段

可选集成：部分英文模板中提到了以命令行方式调用外部执行器（如 codex CLI + gpt-5）以自动化开发/测试。若你没有这些工具，忽略相关指令不影响流程认知；也可以替换为你现有的执行器/Runner。

---

## 目录与关键文件说明

- `CN/agents/` 与 `EN/agents/`
  - 多个角色的系统提示与行为规范，例如：
    - 架构师（bmad-architect）含质量评分维度与交互提问清单
    - 开发协作（code/requirements-code 等）强调 KISS/YAGNI/DRY 等工程原则
    - 缺陷修复（bugfix）强调根因分析与最小可行修复

- `CN/commands/` 与 `EN/commands/`
  - 面向“工作流驱动”的命令模板，例如 `bmad-pilot.md`：
    - 从仓库扫描开始，逐阶段推进（PRD → 架构 → 规划 → 开发 → QA）
    - 在 PRD/架构/Sprint 规划等关键节点设置用户确认门控

- `output-styles/`
  - 统一产出结构与写作风格，便于生成一致的文档与记录

- `CLAUDE.md`
  - 额外的沟通与语言约定示例（如统一中文回答、对不确定性进行声明）

---

## 使用建议与最佳实践

- 从命令模板开始：优先阅读 `bmad-pilot.md` 以理解端到端流程
- 保持“短迭代 + 明确门控”：在每个关键阶段达标后再推进
- 明确产物落盘路径：建议遵循 `./.claude/specs/{feature_name}/` 规范，便于跨阶段复用
- 先简后繁：遵循 KISS/YAGNI，先跑通最小可行，再做优化
- 透明与可追溯：坚持评分分解与决策记录（如 ADR）

---

## 贡献

欢迎通过 Pull Request 补充/修订：

- 新的角色模板与评分维度
- 新的工作流命令与门控设计
- 更多输出样式示例与集成指南

提交前请尽量保持：

- 中英文目录的一致性（如适用）
- 术语/文件命名风格（kebab-case 等）
- 不引入与现有约定冲突的路径与命名

---

## 致谢

感谢所有在多 Agent 编排、提示工程与工程化实践方面的开源探索者和文档作者；本仓库汇集并沉淀了在实际协作中行之有效的提示与流程范式，期待与你共同完善。
