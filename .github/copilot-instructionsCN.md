# Claude AI智能体框架 - Copilot指令

## 项目概述
这是BMAD（业务→架构→开发）AI智能体编排框架。它通过结构化工作流协调专业AI智能体（PO、架构师、SM、开发、QA、审查）来处理完整的软件开发生命周期。

## 架构模式
- **基于智能体**：`agents/general_agent/`中的专业智能体（如`bmad-po.md`、`bmad-dev.md`）
- **命令接口**：`commands/general_agent/`中的用户命令（如`bmad-pilot.md`、`code.md`）
- **输出样式**：`output-styles/general_agent/`中的展示模板
- **工作流编排**：`bmad-orchestrator.md`协调多智能体交互

## 关键开发原则

### UltraThink方法论
所有智能体遵循系统化分析：**假设→证据→模式→综合→验证**。添加功能时，应用此认知框架系统化分解复杂问题。

### 质量门控与审批流程
- **交互阶段**：PO、架构师、SM需要90+质量得分和明确用户批准
- **自动化阶段**：开发、QA自主执行并提供全面报告
- **门控模式**：每个批准门控需要字面的"yes"回应才能继续
- 始终为面向用户的工作流变更实施批准门控

### 工件管理
- 规范存储在`./.claude/specs/{feature_name}/`，使用规范文件名：
  - `00-repo-scan.md`（仓库分析）
  - `01-product-requirements.md`（批准后的PRD）
  - `02-system-architecture.md`（批准后的架构）
  - `03-sprint-plan.md`（批准后的Sprint计划）
  - `04-dev-reviewed.md`（代码审查报告）

## 智能体交互模式

### 命令结构
命令使用带有`name`和`description`的markdown前言。遵循以下模式：
```markdown
---
name: command-name
description: 简要描述
---
```

### 智能体协调
- **编排者管理流程**：绝不绕过编排者进行多智能体工作流
- **上下文传递**：始终包含仓库扫描和之前阶段的输出
- **迭代完善**：智能体可被多次调用直到达到质量阈值
- **顺序执行**：开发→审查→QA，迭代限制（最多3个审查周期）

### 仓库感知
每个智能体通过`00-repo-scan.md`接收仓库上下文。实施新功能时：
1. 始终首先执行仓库扫描（除非`--skip-scan`）
2. 参考现有模式和约定
3. 保持与既定代码库结构的一致性

## 开发标准

### 代码实施（bmad-dev.md模式）
- **多Sprint执行**：按顺序实施所有Sprint，不仅仅是Sprint 1
- **质量要求**：>80%测试覆盖率，全面错误处理
- **架构合规**：严格遵循规范，无偏差
- **SOLID原则**：在整个实施中应用KISS、YAGNI、DRY

### 错误处理模式
```javascript
class AppError extends Error {
  constructor(message, statusCode, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
  }
}
```

### 测试标准
- 每个Sprint的代码都有单元测试
- 跨组件交互的集成测试
- 全面测试错误场景
- 在继续之前验证Sprint完成情况

## 工作流选项
跨命令的标准选项：
- `--skip-tests`：跳过QA阶段
- `--direct-dev`：跳过SM规划阶段
- `--skip-scan`：跳过仓库分析（不推荐）

## 集成点
- **外部工具**：自动化执行阶段的Codex CLI集成
- **文件系统**：`./.claude/specs/`中的结构化工件存储
- **Git集成**：仓库感知扫描和模式检测
- **环境配置**：支持开发/测试/生产配置

## 调试与故障排除
- 检查`./.claude/specs/{feature_name}/`中的工作流工件
- 验证智能体输出中的质量得分（应为90+）
- 确保在阶段转换前完成批准门控
- 仓库扫描为所有后续阶段提供上下文

扩展此框架时，保持智能体专业化模式，并始终为面向用户的变更实施适当的批准门控。