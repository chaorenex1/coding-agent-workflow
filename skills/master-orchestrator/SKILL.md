# MasterOrchestrator Skill

**智能AI任务协调系统 - 从一句话需求到完整代码的全自动化工作流**

## Skill 定义

```yaml
name: master-orchestrator
description: 智能任务协调系统，支持意图分析、多模式执行、5阶段开发工作流
version: 3.0.0
entry: "master_orchestrator.py"
category: automation
tags: [orchestrator, workflow, ai-coordination, multi-backend]
```

## 核心能力

MasterOrchestrator 是一个智能任务协调系统，能够：

1. **智能意图分析** - 自动识别任务类型和最佳执行路径
2. **5种执行模式** - command, agent, prompt, skill, backend
3. **并行执行推断** - 自动判断任务是否可并行，智能拆分执行
4. **5阶段开发工作流** - 从需求分析到代码实现的完整自动化流程
5. **多后端协调** - 智能选择和协调 Claude, Gemini, Codex 等后端
6. **资源降级策略** - 候选资源自动降级，确保执行可靠性

## 使用场景

### 场景 1: 开发完整系统
```bash
cd C:\Users\zarag\Documents\coding_base\skills
python -m orchestrator.master_orchestrator "开发一个博客系统，支持文章发布、评论、用户管理" -v
```
自动执行 5 阶段工作流：需求分析 → 功能设计 → UX设计 → 开发计划 → 代码实现

### 场景 2: 代码审查
```bash
python -m orchestrator.master_orchestrator "代码审查：审查 src/auth.py 的安全性"
```
自动使用 code-review 模板，生成专业的审查报告

### 场景 3: 命令执行
```bash
python -m orchestrator.master_orchestrator "运行项目测试"
```
安全解析并执行命令（白名单机制）

### 场景 4: 代码库探索
```bash
python -m orchestrator.master_orchestrator "查找所有的数据库查询代码"
```
自动触发 Explore 智能体，返回相关代码位置

### 场景 5: 并行任务执行
```bash
python -m orchestrator.master_orchestrator "分析项目性能瓶颈，并生成优化报告"
```
自动识别可并行子任务，并行执行提升效率

## 命令行选项

```bash
# 基本用法（需要从父目录作为模块运行）
cd C:\Users\zarag\Documents\coding_base\skills
python -m orchestrator.master_orchestrator "你的需求" [选项]

# 可用选项
--verbose, -v          # 详细输出模式

# 环境变量配置
export ORCHESTRATOR_TIMEOUT=600        # 超时时间（秒，默认300）
export ADUIB_URL="http://..."          # 远程服务地址（可选）
export ADUIB_API_KEY="..."             # API密钥（可选）
```

## API 使用

```python
from pathlib import Path
from orchestrator.master_orchestrator import MasterOrchestrator, WorkflowResult, TaskResult

# 初始化协调器（完整参数）
orch = MasterOrchestrator(
    timeout=600,                          # 超时时间（秒）
    config_path=Path("./orchestrator.yaml"),  # 配置文件路径（可选）
    auto_discover=True,                   # V3自动发现资源
    enable_parallel=True,                 # 启用并行执行
    max_parallel_workers=3,               # 最大并行数
    use_claude_intent=True,               # 使用Claude意图分析
    intent_confidence_threshold=0.7,      # 置信度阈值
    fallback_to_rules=True,               # 低置信度回退规则引擎
    # 远程服务配置（可选）
    use_remote=False,
    aduib_url=None,
    aduib_api_key=None,
    enable_cache=True,
    enable_upload=True
)

# 处理请求
result = orch.process("开发一个用户管理系统", verbose=True)

# 判断结果类型
if isinstance(result, WorkflowResult):
    # 5阶段工作流结果
    print(f"完成阶段: {result.completed_stages}/5")
    print(f"总耗时: {result.total_duration_seconds:.2f}s")
    for stage_result in result.stages:
        print(f"[{stage_result.stage.value}] {stage_result.duration_seconds:.2f}s")
elif isinstance(result, TaskResult):
    # 单次任务结果
    print(f"后端: {result.backend}")
    print(f"输出: {result.get_final_output()}")
    print(f"成功: {result.success}")
    print(f"耗时: {result.duration_seconds}s")
```

## 系统架构

```
┌─────────────────────────────────────────────────┐
│          MasterOrchestrator (总协调器)           │
├─────────────────────────────────────────────────┤
│  IntentAnalyzer (意图分析)                       │
│    ↓                                             │
│  ExecutionRouter (5模式路由 + 并行推断)          │
│    ↓                                             │
│  ┌──────┬──────┬────────┬────────┬──────────┐  │
│  ↓      ↓      ↓        ↓        ↓          ↓  │
│ Cmd   Agent  Prompt  DevWflow  Backend   Skill │
│ Exec  Caller  Mgr     Agent     Orch.    Reg.  │
└─────────────────────────────────────────────────┘
```

## 5 阶段开发工作流

当系统识别到复杂开发任务时，自动执行：

```
阶段1: 需求分析 (Claude)
  ↓ 输出：完整的需求文档
阶段2: 功能设计 (Claude)
  ↓ 输出：功能模块设计
阶段3: UX设计 (Gemini)
  ↓ 输出：用户体验设计
阶段4: 开发计划 (Codex)
  ↓ 输出：详细实现计划
阶段5: 代码实现 (Codex)
  ↓ 输出：可运行的代码
```

## 执行模式详解

| 模式 | 执行器 | 触发条件 | 示例 |
|------|--------|----------|------|
| **command** | CommandExecutor | 命令关键词（git/npm/docker） | "运行 npm test" |
| **agent** | AgentCaller | 探索/查找关键词 | "查找API端点" |
| **prompt** | PromptManager | 模板化任务（代码审查等） | "生成测试用例" |
| **skill** | DevWorkflowAgent | 复杂开发任务 | "开发电商系统" |
| **backend** | BackendOrchestrator | 简单分析任务 | "解释这段代码" |

## 配置文件

支持通过 `orchestrator.yaml` 自定义配置（完整示例）：

```yaml
version: "3.0"

# 全局配置
global:
  default_backend: claude
  timeout: 300
  enable_parallel: false
  max_parallel_tasks: 3

# 技能配置
skills:
  scan_paths:
    - ./skills/*.yaml
    - ~/.claude/skills/*.yaml
  manual: []

# 命令白名单（安全特性）
commands:
  whitelist:
    - git
    - npm
    - python
    - pytest
    - docker
    - kubectl

# 智能体配置
agents:
  timeout: 600
  max_retries: 3

# 提示词模板配置
prompts:
  template_dirs:
    - ./prompts
    - ~/.claude/prompts
```

## 环境要求

- Python 3.8+
- memex-cli (npm install -g memex-cli)
- 可选依赖：chardet, pyyaml

## 性能指标

- **简单查询**: 2-5秒
- **代码审查**: 10-20秒
- **完整开发工作流**: 7-10分钟
- **内存占用**: ~200MB
- **并行加速**: 最高 3x（取决于任务类型）

## 故障排查

### memex-cli not found
```bash
npm install -g memex-cli
memex-cli --version  # 验证安装
```

### 超时错误
```bash
# 增加超时时间（通过环境变量）
export ORCHESTRATOR_TIMEOUT=1200
python -m orchestrator.master_orchestrator "复杂任务"

# 或在 API 中设置
orch = MasterOrchestrator(timeout=1200)
```

### 并行执行失败
```python
# 通过 API 禁用并行执行
orch = MasterOrchestrator(enable_parallel=False)

# 或在配置文件中禁用
# orchestrator.yaml:
# global:
#   enable_parallel: false
```

## 扩展开发

### 添加自定义执行器
```python
from orchestrator.master_orchestrator import MasterOrchestrator
from orchestrator.analyzers.claude_intent_analyzer import Intent

class CustomExecutor:
    def execute(self, intent: Intent, request: str):
        """自定义执行逻辑"""
        print(f"执行自定义逻辑: {request}")
        return {"success": True, "output": "自定义结果"}

# 创建协调器
orch = MasterOrchestrator()

# 注意：当前版本不支持动态注册执行器
# 需要修改 ExecutionRouter.route() 方法添加自定义分支
```

### 添加自定义技能
```python
from orchestrator.skills.skill_registry import SkillRegistry

registry = SkillRegistry()

# 通过 YAML 文件注册技能
registry.register_from_yaml("path/to/skill.yaml")

# 或在 orchestrator.yaml 中配置
# skills:
#   manual:
#     - name: my-skill
#       path: ./skills/my-skill.yaml
#       enabled: true
#       priority: 100
```

## 相关文档

- [完整用户指南](USER_GUIDE.md)
- [系统架构设计](ARCHITECTURE.md)
- [并行执行文档](docs/AUTO_PARALLEL_EXECUTION.md)
- [执行流程详解](docs/EXECUTION_FLOW.md)

## 许可证

MIT License

---

**从一句话需求到完整代码，只需一条命令** 🚀
