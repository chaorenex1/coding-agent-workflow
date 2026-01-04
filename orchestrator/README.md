# Orchestrator - 跨后端AI任务协调系统

统一的AI任务编排框架，支持多后端（Codex/Claude/Gemini）智能路由和执行。

## 目录结构

```
orchestrator/
├── __init__.py                    # 包入口
├── master_orchestrator.py         # 总协调器（主入口）
├── core/                          # 核心模块
│   ├── backend_orchestrator.py    # 后端编排引擎
│   └── event_parser.py            # 事件流解析器
├── executors/                     # 执行器模块
│   ├── command_executor.py        # 命令执行器
│   ├── agent_caller.py            # Agent调用器
│   └── prompt_manager.py          # 提示词管理器
├── clients/                       # 客户端模块
│   └── aduib_client.py            # Aduib远程服务客户端
├── skills/                        # 技能系统
│   ├── skill_registry.py          # 技能注册表
│   └── dev_workflow.py            # 开发工作流Agent
└── tests/                         # 测试文件
    ├── test_orchestrator.py
    ├── test_phase3.py
    └── test_phase4.py
```

## 功能特性

### 1. 智能路由系统
支持5种执行模式：
- **command**: 简单命令执行
- **agent**: 智能体调用
- **prompt**: 提示词模板
- **skill**: 技能系统
- **backend**: 直接后端调用

### 2. 多后端支持
- **codex**: 代码优化（DeepSeek Reasoner）
- **claude**: 通用推理
- **gemini**: 视觉和UX理解

### 3. 远程缓存
- 与aduib-ai集成
- 自动缓存查询和结果上传
- 支持离线模式

## 快速开始

### 安装依赖

```bash
# 安装memex-cli（必需）
npm install -g memex-cli

# Python依赖
pip install requests  # 仅远程模式需要
```

### 基本使用

```python
from orchestrator import MasterOrchestrator

# 创建协调器
orch = MasterOrchestrator(
    parse_events=False,  # 是否解析事件流
    timeout=300,         # 超时时间（秒）
    use_remote=False     # 是否使用远程服务
)

# 处理请求
result = orch.process("开发一个电商系统", verbose=True)

# 查看结果
print(result.output if hasattr(result, 'output') else result)
```

### 直接使用后端编排器

```python
from orchestrator.core.backend_orchestrator import BackendOrchestrator

orch = BackendOrchestrator()

# 单个任务
result = orch.run_task("claude", "分析这段代码")

# 多后端对比
comparison = orch.compare_backends_parallel(
    ["claude", "gemini", "codex"],
    "优化这个函数"
)

# 多阶段管道
pipeline = orch.run_pipeline([
    ("gemini", "设计UI界面"),
    ("codex", "生成代码实现"),
    ("claude", "代码审查")
])
```

## 测试

```bash
# 运行包测试
python test_orchestrator_package.py

# 运行单元测试
cd orchestrator/tests
python -m pytest
```

## 配置

### 环境变量

```bash
# Aduib远程服务（可选）
export ADUIB_URL="https://your-aduib-server.com"
export ADUIB_API_KEY="your-api-key"

# 后端配置（通过memex-cli配置）
# 参考: skills/memex-cli/README.md
```

## 架构说明

### 意图分析
系统自动分析用户请求，识别：
- 执行模式（command/agent/prompt/skill/backend）
- 任务类型（dev/ux/analysis/test）
- 复杂度（simple/medium/complex）
- 后端提示（claude/gemini/codex）

### 执行路由
根据意图自动路由到对应执行器：
```
用户请求 → 意图分析 → 执行路由 → 后端调用 → 结果返回
           ↓
       缓存查询（可选）
           ↓
       结果上传（可选）
```

## 开发

### 添加新的执行器
在 `executors/` 目录下创建新模块，实现执行接口。

### 添加新的技能
在 `skills/` 目录下创建新模块，并在 `skill_registry.py` 中注册。

## 版本

当前版本: **1.0.0**

## 依赖项

- Python 3.8+
- memex-cli (Node.js)
- requests (可选，仅远程模式)

## 许可证

MIT License
