# coding-agent-workflow

一个面向多角色协同的 AI 智能体工作流与提示工程资料库。它为"BMAD"风格的全流程开发协作提供可复用的角色定义、指令模板与输出样式，覆盖产品需求、系统架构、Scrum 规划、开发实现、代码评审与质量保障等环节。

本仓库更像是"方法与模板"的集合，可直接作为大语言模型（LLM）的系统提示/工具说明使用，也可按需裁剪到你的自动化编排或 Agent 框架中。

## 适用对象

- 希望用一套可落地的多角色 AI 协作流程（PO/Architect/SM/Dev/Review/QA）的团队或个人
- 需要结构化、可评分、可确认门控的交互式开发流程
- 想快速复用专业角色提示与输出规范的人/团队
- 希望集成 Codex CLI 或 Gemini 等外部工具进行代码执行的开发者

---

## 仓库结构概览

```text
当前/                     # 当前使用的模板和工具
  agents/
    cexll/              # BMAD 角色定义集合
      bmad-architect.md      # 系统架构师角色
      bmad-dev.md           # 开发者角色
      bmad-orchestrator.md  # 流程协调者角色
      bmad-po.md            # 产品负责人角色
      bmad-qa.md            # QA 测试角色
      bmad-review.md        # 代码评审角色
      bmad-sm.md            # Scrum Master 角色
      bugfix-verify.md      # 缺陷验证角色
      bugfix.md             # 缺陷修复角色
      code.md               # 通用编码角色
      debug.md              # 调试角色
      dev-plan-generator.md # 开发计划生成角色
      gpt5.md               # GPT-5 模型角色
      optimize.md           # 优化角色
      requirements-*.md     # 需求相关角色集合
  commands/
    aduib-frontend/     # 前端项目脚手架
    cexll/              # BMAD 工作流命令集
      bmad-pilot.md         # BMAD 完整流程编排
      bugfix.md             # 缺陷修复流程
      code.md               # 编码流程
      debug.md              # 调试流程
      dev.md                # 开发流程
      optimize.md           # 优化流程
      refactor.md           # 重构流程
      review.md             # 评审流程
      test.md               # 测试流程
      requirements-pilot.md # 需求分析流程
    chaorenex1/         # 代码分析和设计命令
      code-boundary.md      # 代码边界分析
      code-design.md        # 代码设计
      code-interface.md     # 接口设计
      code-reader.md        # 代码阅读
      code-review.md        # 代码评审
      project-architecture.md # 项目架构
  output-styles/
    bmad.md             # BMAD 输出风格规范
  skills/
    codex/              # Codex CLI 集成技能
      SKILL.md              # Codex 使用说明
      scripts/codex.py      # Codex CLI 包装脚本
    gemini/             # Gemini API 集成技能
      SKILL.md              # Gemini 使用说明
      scripts/gemini.py     # Gemini API 包装脚本
    requirements-clarity/ # 需求澄清技能
      SKILL.md              # 需求澄清方法说明

废弃/                     # 已废弃的旧版模板
  agents/               # 旧版角色定义
    bmad/                   # 旧版 BMAD 角色
    dev/                    # 旧版开发角色
    req/                    # 旧版需求角色
  commands/             # 旧版命令模板
    bmad/                   # 旧版 BMAD 命令
    dev/                    # 旧版开发命令
    req/                    # 旧版需求命令
  output-styles/        # 旧版输出样式

CLAUDE.md               # 通用 AI 助手指令约定
```

> 提示：主要使用 `当前/` 目录下的模板，`废弃/` 目录仅作历史参考。

---

## 什么是 BMAD 工作流

BMAD 是一种以"多角色智能体协作"为核心的开发工作流抽象，强调质量门控与用户显式确认：

### 核心角色

1. **Orchestrator（协调者）** - 管理整个工作流，协调各角色间的交接
2. **PO（产品负责人）** - 负责产品需求文档（PRD）的编写和需求澄清
3. **Architect（系统架构师）** - 负责技术架构设计和技术栈选型
4. **SM（Scrum Master）** - 负责 Sprint 计划和任务分解
5. **Dev（开发者）** - 负责功能实现和单元测试
6. **Review（代码评审员）** - 负责代码质量审核和改进建议
7. **QA（质量保证）** - 负责测试用例设计和质量验证

### 工作流阶段

- **Phase 0** - 仓库上下文扫描（可选，默认开启）
  - 分析项目结构、技术栈、代码模式
  - 输出：`00-repo-scan.md`

- **Phase 1** - 产品需求（PRD）
  - 交互式需求澄清，直到质量评分 ≥ 90
  - 🛑 **质量门控**：需用户明确同意后保存
  - 输出：`01-product-requirements.md`

- **Phase 2** - 系统架构设计
  - 交互式架构设计，直到质量评分 ≥ 90
  - 🛑 **质量门控**：需用户明确同意后保存
  - 输出：`02-system-architecture.md`

- **Phase 3** - Sprint 计划（可选，支持 `--direct-dev` 跳过）
  - 任务分解、估时、依赖分析
  - 🛑 **确认门控**：需用户确认后保存
  - 输出：`03-sprint-plan.md`

- **Phase 4** - 开发实现
  - 按 PRD 和架构实现功能
  - 输出：实现的代码和测试

- **Phase 4.5** - 代码评审
  - 独立评审代码质量和合规性
  - 支持迭代评审（最多 3 轮）
  - 输出：`04-dev-reviewed.md`

- **Phase 5** - 质量保障（可选，支持 `--skip-tests` 跳过）
  - 创建和执行测试套件
  - 验证所有验收标准

### 质量门控机制

- **PRD 和架构需达到 ≥ 90 分**的质量评分
- 在继续前需获得用户**明确同意**（回复 "yes" 或 "是"）
- 任何非确认回复都会停留在当前阶段继续优化

### 产物存放

所有产物统一存放在 `./.claude/specs/{feature_name}/` 目录：
- `00-repo-scan.md` - 仓库扫描报告
- `01-product-requirements.md` - 产品需求文档
- `02-system-architecture.md` - 系统架构文档
- `03-sprint-plan.md` - Sprint 计划
- `04-dev-reviewed.md` - 代码评审报告

### UltraThink 方法论

工作流中集成了 UltraThink 系统化分析方法：
1. **假设生成** - 形成关于问题的假设
2. **证据收集** - 从代码库和文档中收集证据
3. **模式识别** - 识别重复模式和惯例
4. **综合分析** - 创建全面的理解
5. **交叉验证** - 通过多个来源验证发现

---

## 快速开始

### 方式 A：直接使用命令模板

1. 选择合适的命令模板（如 `当前/commands/cexll/bmad-pilot.md`）
2. 将模板内容作为"系统提示"提供给 LLM
3. 输入项目需求，例如：`/bmad-pilot 构建一个用户管理系统`
4. 按照交互式门控进行迭代，达到评分阈值后确认保存

### 方式 B：集成到 Agent 框架

1. 将 `agents/` 下的角色定义接入你的多 Agent 编排系统
2. 将 `commands/` 下的流程模板作为"任务剧本"
3. 将 `output-styles/` 下的样式用于统一输出格式
4. 实现"质量门控 + 显式确认"作为编排节点条件

### 方式 C：使用外部工具集成

#### Codex CLI 集成
```bash
# 执行 Codex 任务
uv run ~/.claude/skills/codex/scripts/codex.py "你的任务描述"

# 恢复之前的会话
uv run ~/.claude/skills/codex/scripts/codex.py resume <session_id> "继续任务"
```

适用于：
- 复杂代码分析
- 大规模重构
- 自动化代码生成

#### Gemini API 集成
查看 `当前/skills/gemini/SKILL.md` 了解使用方法

---

## 命令选项

BMAD Pilot 支持以下选项：

- `--skip-scan` - 跳过仓库扫描（不推荐）
- `--direct-dev` - 跳过 Sprint 计划，直接进入开发
- `--skip-tests` - 跳过 QA 测试阶段

示例：
```
/bmad-pilot 构建用户认证模块 --direct-dev --skip-tests
```

---

## 目录与关键文件说明

### 角色定义（`agents/cexll/`）

- **bmad-orchestrator.md** - 协调整个工作流，管理上下文和交接
- **bmad-po.md** - 产品需求分析，包含质量评分维度（业务价值、功能性、UX、技术约束等）
- **bmad-architect.md** - 系统架构设计，包含质量评分维度（设计、技术选型、可扩展性等）
- **bmad-sm.md** - Sprint 计划，任务分解和估时
- **bmad-dev.md** - 开发实现，遵循 KISS/YAGNI/DRY 等工程原则
- **bmad-review.md** - 代码评审，支持迭代评审和状态跟踪
- **bmad-qa.md** - 质量保证，测试用例设计和执行
- **bugfix.md** / **bugfix-verify.md** - 缺陷修复和验证
- **debug.md** - 调试辅助
- **optimize.md** - 性能优化

### 命令模板（`commands/`）

#### cexll 命令集
- **bmad-pilot.md** - 完整的 BMAD 工作流编排
- **requirements-pilot.md** - 需求分析流程
- **code.md** / **dev.md** - 开发流程
- **review.md** - 评审流程
- **test.md** - 测试流程
- **refactor.md** - 重构流程
- **optimize.md** - 优化流程
- **bugfix.md** - 缺陷修复流程
- **debug.md** - 调试流程

#### chaorenex1 命令集
- **project-architecture.md** - 项目架构分析
- **code-boundary.md** - 代码边界分析
- **code-design.md** - 代码设计
- **code-interface.md** - 接口设计
- **code-reader.md** - 代码阅读辅助
- **code-review.md** - 代码评审

### 输出样式（`output-styles/`）

- **bmad.md** - BMAD 工作流的统一输出规范，包括：
  - 角色定义
  - 执行原则（UltraThink、KISS、YAGNI、DRY、SOLID）
  - 审批门控机制
  - 代码执行指令（Codex CLI 集成）
  - 结果呈现格式

### 技能集成（`skills/`）

- **codex/** - Codex CLI 集成
  - 支持代码分析、重构、生成
  - 会话管理和恢复
  - 超时控制和错误处理

- **gemini/** - Gemini API 集成
  - Google AI 模型调用
  - 适用于特定场景

- **requirements-clarity/** - 需求澄清方法
  - 系统化的需求分析技巧

---

## 使用建议与最佳实践

### 工作流建议

1. **从命令模板开始**：优先阅读 `bmad-pilot.md` 以理解端到端流程
2. **保持短迭代**：在每个关键阶段达标后再推进
3. **明确产物路径**：遵循 `./.claude/specs/{feature_name}/` 规范
4. **先简后繁**：遵循 KISS/YAGNI，先跑通最小可行方案
5. **透明可追溯**：坚持评分分解与决策记录

### 质量门控

- PRD 和架构必须达到 90 分以上
- 用户必须明确回复 "yes" 或 "是" 才能继续
- 任何非确认回复都会留在当前阶段优化

### 代码评审迭代

- Review 阶段支持最多 3 次迭代
- 状态包括：Pass（通过）、Pass with Risk（带风险通过）、Fail（失败）
- 第 2 次失败时召开会议（SM、Architect、Dev）
- 第 3 次失败时人工介入

### 外部工具使用

- **Codex CLI**：适用于复杂代码任务、大规模重构
- **Foreground 执行**：永远使用前台执行，超时设置为 7200000ms
- **会话管理**：保存 session_id 以便恢复长对话

---

## 贡献

欢迎通过 Pull Request 补充/修订：

- 新的角色模板与评分维度
- 新的工作流命令与门控设计
- 更多输出样式示例与集成指南
- Skills 技能包的扩展

### 提交规范

- 保持目录结构一致性
- 使用 kebab-case 命名文件
- 不引入与现有约定冲突的路径和命名
- 在 `当前/` 目录下添加新内容

---

## 致谢

感谢所有在多 Agent 编排、提示工程与工程化实践方面的开源探索者和文档作者；本仓库汇集并沉淀了在实际协作中行之有效的提示与流程范式，期待与你共同完善。

---

## License

MIT License - 详见 LICENSE 文件
