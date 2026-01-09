# Coding Workflow - AI 智能工作流系统

**Claude Code 扩展工具库，包含 Skills、Agents 和 Commands (Slash Commands)，用于增强 Claude Code 的能力**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

## 📖 项目概述

Coding Workflow 是一个面向开发者的 AI 智能工作流系统，旨在通过集成多种 AI 后端（Claude、Gemini、Codex）和丰富的技能集（18 个 Skills）及代理（36 个 Agents），实现从需求分析、架构设计、代码实现到测试发布的端到端自动化开发流程。

**核心价值**：
- 🤖 **多后端协调** - 选择最适合的 AI 后端执行任务
- 🔄 **端到端自动化** - 从一句话需求到完整代码实现
- 🛠️ **18 项技能集成** - 代码分析、重构、文档生成等专业技能
- 🏃 **零开销执行** - 90% 任务直接执行，无路由开销

## 🚀 快速开始

### 安装

#### 方式 1: 通过 Claude Code Plugin Marketplace（推荐）

**一键安装**：

在 Claude Code 中运行：
```
/plugin coding-workflow
```

插件会自动安装所有 18 个 Skills、36 个 Agents 和 48 个 Commands。

**依赖安装**：

插件启动时会自动检查依赖，如有缺失会提示安装：

```bash
# 安装 memex-cli (必需)
npm install -g memex-cli

# 安装 Python 依赖
pip install chardet pyyaml
```

**配置（可选）**：

如需自定义配置，复制配置模板：
```bash
cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
```

然后编辑 `~/.claude/coding-workflow.local.md` 修改配置项。

---

#### 方式 2: 手动安装（开发者模式）

```bash
# 克隆项目
git clone https://github.com/chaorenex1/coding-workflow.git
cd coding-workflow

# 安装 Python 依赖
pip install chardet pyyaml

# 安装 memex-cli (必需)
npm install -g memex-cli
```

## 📁 项目结构

```
coding-workflow/
├── README.md                           # 本文档
├── CLAUDE.md                           # Claude Code 项目指南
├── AGENTS.md                           # 代理系统文档
├── .claude/                            # Claude Code 配置
│
├── skills/                             # 技能系统 (18 个)
│   ├── code-with-codex/                # Codex 代码开发
│   ├── ux-design-gemini/               # Gemini UX 设计
│   ├── codex-cli-bridge/               # Codex CLI 桥接
│   ├── repo-analyzer/                  # 代码库分析
│   ├── code-refactoring-assistant/     # 代码重构助手
│   ├── code-refactor-analyzer/         # 代码重构分析器
│   ├── code-fix-assistant/             # 代码修复助手
│   ├── api-document-generator/         # API 文档生成
│   ├── chinese-interface-doc-generator/# 中文接口文档生成
│   ├── tech-stack-evaluator/           # 技术栈评估
│   ├── git-code-review/                # Git 代码审查
│   ├── git-commit-summarizer/          # Git 提交智能总结
│   ├── git-batch-commit/               # Git 批量提交工具
│   ├── github-stars-analyzer/          # GitHub Stars 分析
│   ├── skill-validator/                # Skill 验证器
│   ├── memex-cli/                      # Memex CLI 工具
│   ├── cross-platform-command-generator/# 跨平台命令生成
│   └── priority-optimization-assistant/# 优先级优化助手
│
├── agents/                             # 代理系统 (36 个)
│   ├── bmad-workflow/                  # ⭐ BMAD 完整工作流 (8 个)
│   │   ├── bmad-orchestrator.md        # 工作流总协调器
│   │   ├── bmad-analyst.md             # 需求分析师
│   │   ├── bmad-product-owner.md       # 产品负责人
│   │   ├── bmad-architect.md           # 系统架构师
│   │   ├── bmad-scrum-master.md        # Scrum Master
│   │   ├── bmad-fullstack-dev.md       # 全栈开发者
│   │   ├── bmad-qa.md                  # 质量保证
│   │   └── bmad-devops.md              # DevOps 工程师
│   │
│   ├── bmad-iterate/                   # ⭐ BMAD 迭代开发 (7 个)
│   │   ├── bmad-iter-orchestrator.md   # 迭代协调器
│   │   ├── bmad-diff-analyst.md        # 差异分析师
│   │   ├── bmad-iteration-planner.md   # 迭代规划师
│   │   ├── bmad-impact-analyst.md      # 影响分析师
│   │   ├── bmad-iter-developer.md      # 迭代开发者
│   │   ├── bmad-regression-tester.md   # 回归测试员
│   │   └── bmad-release-manager.md     # 发布管理员
│   │
│   ├── quick-code/                     # 快速代码代理 (5 个)
│   │
│   ├── feature-workflow/               # 功能开发代理
│   │
│   └── automation/                     # 自动化代理
│       ├── comprehensive-analysis-report-generator.md
│       └── documentation-sync-agent.md
│
├── commands/                           # Slash Commands 命令系统
│   ├── bmad-workflow/                  # BMAD 工作流命令 (7 个)
│   │   ├── bmad.md                     # /bmad 主命令
│   │   ├── bmad-analyze.md             # /bmad-analyze
│   │   ├── bmad-plan.md                # /bmad-plan
│   │   ├── bmad-architect.md           # /bmad-architect
│   │   ├── bmad-develop.md             # /bmad-develop
│   │   ├── bmad-test.md                # /bmad-test
│   │   └── bmad-deploy.md              # /bmad-deploy
│   │
│   ├── bmad-iterate/                   # BMAD 迭代命令 (7 个)
│   │   ├── bmad-iter.md                # /bmad-iter 主命令
│   │   ├── bmad-iter-diff.md           # /bmad-iter-diff
│   │   ├── bmad-iter-plan.md           # /bmad-iter-plan
│   │   ├── bmad-iter-impact.md         # /bmad-iter-impact
│   │   ├── bmad-iter-dev.md            # /bmad-iter-dev
│   │   ├── bmad-iter-test.md           # /bmad-iter-test
│   │   └── bmad-iter-release.md        # /bmad-iter-release
│   │
│   ├── quick-code/                     # 快速代码命令
│   ├── project-analyzer/               # 项目分析命令
│   ├── scaffold/                       # 脚手架命令
│   └── workflow-suite/                 # 工作流套件 (包含 /multcode 等)
│
├── prompts/                            # 提示词模板库
│
├── scripts/                            # 工具脚本
│
└── docs/                               # 文档
    ├── ARCHITECTURE.md                 # 架构设计
    └── USER_GUIDE.md                   # 用户指南
```

## 🔧 技能系统详解

### 核心技能

#### codex-cli-bridge
**Codex CLI 桥接工具** - 与 Codex CLI 无缝集成

- 📍 位置: `skills/codex-cli-bridge/`
- 🎯 功能: CLI 命令桥接、事件解析、结果处理
- 📖 文档: [SKILL.md](skills/codex-cli-bridge/SKILL.md)

#### repo-analyzer
**代码库智能分析** - 深度分析代码库结构和质量

- 📍 位置: `skills/repo-analyzer/`
- 🎯 功能: 依赖分析、代码质量评估、技术栈识别
- 📖 文档: [SKILL.md](skills/repo-analyzer/SKILL.md)

#### code-refactoring-assistant
**代码重构助手** - 智能代码重构建议和执行

- 📍 位置: `skills/code-refactoring-assistant/`
- 🎯 功能: 代码坏味道检测、重构建议、自动重构
- 📖 文档: [SKILL.md](skills/code-refactoring-assistant/SKILL.md)

#### api-document-generator
**API 文档生成器** - 自动生成 API 接口文档

- 📍 位置: `skills/api-document-generator/`
- 🎯 功能: 接口提取、参数解析、文档生成
- 📖 文档: [SKILL.md](skills/api-document-generator/SKILL.md)

## ⚙️ 配置

### 环境变量

```bash
# Memex CLI 路径（可选）
export MEMEX_CLI_PATH=/usr/local/bin/memex-cli

# Aduib 服务地址（可选）
export ADUIB_API_URL=http://localhost:8000
export ADUIB_API_KEY=your-api-key
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Anthropic Claude](https://www.anthropic.com/) - 强大的 AI 模型
- [Google Gemini](https://ai.google.dev/) - 创新的多模态 AI
- [OpenAI Codex](https://openai.com/blog/openai-codex) - 专业的代码生成
- [memex-cli](https://github.com/chaorenex1/memex-cli) - AI 后端调用工具

## 📞 联系方式

- 问题反馈: GitHub Issues

---

**从一句话需求到完整代码，Coding Workflow 让 AI 开发触手可及** 🚀
