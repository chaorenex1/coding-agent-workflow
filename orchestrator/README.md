# MasterOrchestrator

**智能AI任务协调系统** - 从一句话需求到完整代码的全自动化工作流

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)

## 概述

MasterOrchestrator 是一个智能任务协调系统，能够自动分析用户意图，选择最佳执行路径，并协调多个 AI 后端（Claude, Gemini, Codex）完成复杂任务。

**核心特性**：
- 🧠 **智能意图分析** - 自动识别任务类型和复杂度
- 🔀 **5种执行模式** - Command, Agent, Prompt, Skill, Backend
- 🔄 **5阶段自动化工作流** - 从需求分析到代码实现的完整流程
- 🛡️ **安全命令执行** - 白名单机制和危险模式检测
- 📚 **专业提示词模板库** - 8个领域专家级模板
- 🔍 **技能注册和发现** - 自动管理和查询可用技能

## 快速开始

### 安装依赖

```bash
# 1. 安装 Python 依赖（可选）
pip install chardet pyyaml

# 2. 安装 memex-cli（必需）
npm install -g memex-cli
```

### 基本使用

```bash
# 简单查询
python master_orchestrator.py "分析这段代码的性能"

# 开发完整系统（自动触发 5 阶段工作流）
python master_orchestrator.py "开发一个用户管理系统" --verbose

# 执行命令
python master_orchestrator.py "运行 git status"

# 使用模板
python master_orchestrator.py "代码审查这个登录函数"
```

### 5 秒示例

```python
from master_orchestrator import MasterOrchestrator

# 创建协调器
orch = MasterOrchestrator()

# 处理请求（自动分析意图并执行）
result = orch.process("开发一个电商小程序")

# 查看结果
print(f"成功: {result.success}")
```

## 核心功能

### 1. 智能意图分析

系统自动分析用户请求，识别：
- **执行模式**：command, agent, prompt, skill, backend
- **任务类型**：dev, ux, analysis, test
- **复杂度**：simple, medium, complex

```
"运行 git status"           → command 模式
"查找所有API端点"          → agent 模式 (Explore)
"代码审查这个函数"         → prompt 模式 (code-review模板)
"开发完整的用户管理系统"   → skill 模式 (5阶段工作流)
"分析代码性能"            → backend 模式 (直接调用Claude)
```

### 2. 5种执行模式

| 模式 | 执行器 | 用途 | 示例 |
|------|--------|------|------|
| **command** | CommandExecutor | Shell命令 | "运行 npm test" |
| **agent** | AgentCaller | 智能体调用 | "查找认证代码" |
| **prompt** | PromptManager | 模板化提示词 | "生成测试用例" |
| **skill** | DevWorkflowAgent | 多阶段工作流 | "开发电商系统" |
| **backend** | BackendOrchestrator | 直接AI调用 | "解释这段代码" |

### 3. 5阶段自动化工作流

当识别到复杂开发任务时，自动执行：

```
阶段1: 需求分析 (Claude)
  ↓
阶段2: 功能设计 (Claude)
  ↓
阶段3: UX设计 (Gemini)
  ↓
阶段4: 开发计划 (Codex)
  ↓
阶段5: 代码实现 (Codex)
```

**特点**：
- 每个阶段输出自动传递到下一阶段
- 每个阶段完成后自动验证
- 任何阶段失败立即中止并报告
- 完整的进度追踪和详细报告

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              MasterOrchestrator (总协调器)               │
├─────────────────────────────────────────────────────────┤
│  IntentAnalyzer (意图分析)                               │
│    ↓                                                     │
│  ExecutionRouter (5模式路由)                             │
│    ↓                                                     │
│  ┌──────┬──────┬────────┬────────────┬──────────┐      │
│  ↓      ↓      ↓        ↓            ↓          ↓      │
│ Cmd   Agent  Prompt  DevWorkflow   Backend    Skill    │
│ Exec  Caller  Mgr     Agent        Orch.     Registry  │
└─────────────────────────────────────────────────────────┘
```

详见 [ARCHITECTURE.md](ARCHITECTURE.md)

## 项目结构

```
coding_base/
├── master_orchestrator.py      # 总协调器（主入口）
├── README.md                    # 本文档
├── USER_GUIDE.md               # 详细使用指南
├── ARCHITECTURE.md             # 系统架构文档
│
├── commands/                   # 命令执行模块
│   └── command_executor.py
│
├── prompts/                    # 提示词模板库
│   └── prompt_manager.py
│
├── agents/                     # 智能体调用模块
│   └── agent_caller.py
│
├── skills/                     # 技能系统
│   ├── skill_registry.py      # 技能注册表
│   ├── multcode-dev-workflow-agent/
│   │   └── auto_workflow.py   # 5阶段工作流
│   └── cross-backend-orchestrator/
│       └── scripts/
│           ├── orchestrator.py     # 后端协调器
│           └── event_parser.py     # 事件解析器
│
└── tests/
    ├── test_phase2.py          # Phase 2 测试
    ├── test_phase3.py          # Phase 3 测试
    └── test_phase4.py          # Phase 4 测试
```

## 使用示例

### 场景 1: 开发完整系统

```bash
python master_orchestrator.py "开发一个博客系统，支持文章发布、评论、用户管理" -v
```

**输出**：
```
[意图分析]
  模式: skill
  类型: dev
  复杂度: complex

[工作流执行完成]
成功: True
完成阶段: 5/5
总耗时: 458.3s

阶段详情:
  [OK] 阶段 1: requirements (43.2s)
  [OK] 阶段 2: feature_design (67.8s)
  [OK] 阶段 3: ux_design (81.4s)
  [OK] 阶段 4: dev_plan (92.6s)
  [OK] 阶段 5: implementation (173.3s)
```

### 场景 2: 代码审查

```bash
python master_orchestrator.py "代码审查：审查 src/auth.py 的安全性"
```

自动使用 `code-review` 模板，生成专业的审查报告。

### 场景 3: 命令执行

```bash
python master_orchestrator.py "运行项目测试"
```

自动解析为 `pytest` 或 `npm test`，安全执行。

### 场景 4: 代码库探索

```bash
python master_orchestrator.py "查找所有的数据库查询代码"
```

自动触发 Explore 智能体，返回相关代码位置。

## API 使用

```python
from master_orchestrator import MasterOrchestrator

# 初始化
orch = MasterOrchestrator(
    parse_events=True,  # 解析事件流
    timeout=600         # 超时时间（秒）
)

# 处理请求
result = orch.process("你的需求", verbose=True)

# 判断结果类型
if isinstance(result, WorkflowResult):
    # 工作流结果
    print(f"完成阶段: {result.completed_stages}/5")
    for stage_result in result.stages:
        print(f"{stage_result.stage.value}: {stage_result.output[:100]}")

elif isinstance(result, TaskResult):
    # 单次任务结果
    print(f"输出: {result.get_final_output()}")
    print(f"Run ID: {result.run_id}")
```

## 测试

```bash
# 运行所有测试
python test_phase2.py  # 意图分析和路由
python test_phase3.py  # 执行器集成
python test_phase4.py  # 技能自动化

# 测试结果
# Phase 2: 5/5 通过
# Phase 3: 14/14 通过
# Phase 4: 10/10 通过
```

## 配置

### 环境变量

```bash
# memex-cli 配置（如需要）
export MEMEX_CLI_PATH=/usr/local/bin/memex-cli
```

### 自定义后端

编辑 `master_orchestrator.py`:

```python
# 修改后端选择逻辑
def _select_backend(self, intent: Intent) -> str:
    if intent.task_type == "dev":
        return "your-custom-backend"
    # ...
```

## 性能

**典型任务执行时间**：
- 简单查询：2-5秒
- 代码审查：10-20秒
- 完整开发工作流：7-10分钟

**资源占用**：
- CPU：中等（主要由 memex-cli 决定）
- 内存：~200MB
- 磁盘：事件日志 ~1MB/任务

## 故障排查

### memex-cli not found

```bash
# 安装 memex-cli
npm install -g memex-cli

# 验证安装
memex-cli --version
```

### 编码错误

```bash
# Windows 用户可能遇到 UTF-16 编码问题
# 系统已自动处理，无需配置
```

### 超时

```bash
# 增加超时时间
python master_orchestrator.py "复杂任务" --timeout 1200
```

## 路线图

- [x] Phase 1: 核心基础设施
- [x] Phase 2: 智能路由系统
- [x] Phase 3: 执行器完善
- [x] Phase 4: 技能自动化
- [ ] Phase 5: 持久化和缓存
- [ ] Phase 6: Web UI 界面
- [ ] Phase 7: 插件系统

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 致谢

- [memex-cli](https://github.com/anthropics/memex-cli) - AI 后端调用
- Claude, Gemini, Codex - AI 模型支持

## 联系方式

- 问题反馈：GitHub Issues
- 文档：[完整文档](USER_GUIDE.md)
- 架构设计：[架构文档](ARCHITECTURE.md)

---

**从一句话需求到完整代码，只需一条命令** 🚀
