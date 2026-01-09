# MasterOrchestrator 系统架构

本文档详细描述 MasterOrchestrator 的系统架构、设计决策和技术实现。

## 目录

- [系统概览](#系统概览)
- [核心架构](#核心架构)
- [插件系统集成](#插件系统集成)
- [模块详解](#模块详解)
- [数据流](#数据流)
- [设计决策](#设计决策)
- [扩展性设计](#扩展性设计)
- [性能考虑](#性能考虑)
- [安全性](#安全性)

---

## 系统概览

### 设计理念

MasterOrchestrator 采用**分层协调架构**，将复杂的任务自动化分解为多个层次：

```
用户请求 → 意图分析 → 执行路由 → 具体执行器 → AI 后端
```

**核心设计原则**：

1. **关注点分离** - 每个模块职责单一明确
2. **可扩展性** - 易于添加新的执行模式和后端
3. **失败透明** - 错误在每一层都被捕获和传递
4. **类型安全** - 使用 dataclass 和类型提示
5. **可测试性** - 每个模块都可独立测试

---

## 核心架构

### 系统分层

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                 │
│                  (CLI / Python API)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 MasterOrchestrator                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │    ClaudeIntentAnalyzer (Claude LLM 意图分析)     │   │
│  │  - 语义理解 (ExecutionMode)                       │   │
│  │  - 任务分类 (TaskType)                            │   │
│  │  - 复杂度评估 (Complexity)                        │   │
│  │  - 通过 memex-cli skill: intent-analyzer.yaml    │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │      【可选】Aduib-AI 缓存层                      │   │
│  │  - query_cache(): 查询远程缓存                    │   │
│  │  - save_task_result(): 保存执行结果              │   │
│  │  - 自动降级机制（服务不可用时）                   │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │         ExecutionRouter (执行路由层)              │   │
│  │  - 5 种执行模式路由                                │   │
│  │  - 后端选择逻辑                                    │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
┌────────▼────┐  ┌───▼────┐  ┌───▼─────┐  ┌──────────┐  ┌────────┐
│  Command    │  │ Agent  │  │ Prompt  │  │  Skill   │  │Backend │
│ Executor V2 │  │Caller V2│ │Manager V2│ │ Executor │  │ Orch.  │
│             │  │        │  │         │  │          │  │        │
│ (继承 MemexExecutorBase)  │  │         │  │          │  │        │
└─────┬───────┘  └────┬───┘  └────┬────┘  └─────┬────┘  └───┬────┘
      │               │           │              │           │
      └───────────────┴───────────┴──────────────┴───────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│           MemexExecutorBase (统一执行器基类)                   │
│  - execute_via_memex(): 通过 memex-cli 执行                    │
│  - 统一错误处理和超时控制                                       │
│  - 标准化结果格式                                               │
└─────────────────────┬──────────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│              BackendOrchestrator (后端协调层)                   │
│  - memex-cli 集成 + YAML Skills 管理                            │
│  - 事件流解析 (EventParser)                                     │
│  - 多后端管理 (Claude, Gemini, Codex)                           │
│                                                                 │
│  Skills:                                                        │
│  - intent-analyzer.yaml (意图识别)                              │
│  - command-parser.yaml (命令解析)                               │
│  - agent-router.yaml (Agent路由)                                │
│  - prompt-renderer.yaml (提示词渲染)                            │
│  - dev-workflow.yaml (开发工作流)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 插件系统集成

### 概览

MasterOrchestrator 通过 **Claude Code Plugin System** 实现一键安装和自动化配置。插件系统负责：

1. **自动发现和注册** - Skills、Agents、Commands 的自动注册
2. **依赖验证** - 启动时检查必需依赖（memex-cli、Python 包）
3. **配置管理** - 通过 `coding-workflow.local.md` 自定义配置
4. **生命周期管理** - SessionStart 钩子执行依赖检查

### 插件清单 (plugin.json)

**文件**: `.claude-plugin/plugin.json`

```json
{
  "name": "coding-workflow",
  "version": "3.0.0",
  "description": "AI 智能工作流系统",
  "author": {
    "name": "chaorenex1",
    "url": "https://github.com/chaorenex1"
  },
  "homepage": "https://github.com/chaorenex1/coding-workflow#readme",
  "repository": "https://github.com/chaorenex1/coding-workflow",
  "license": "MIT",
  "keywords": [
    "workflow", "ai", "automation", "bmad",
    "orchestrator", "code-generation"
  ],
  "skills": "./skills",
  "agents": [
    "./agents/automation",
    "./agents/bmad-iterate",
    "./agents/bmad-workflow",
    "./agents/feature-workflow",
    "./agents/quick-code"
  ],
  "commands": [
    "./commands/bmad-iterate",
    "./commands/bmad-workflow",
    "./commands/project-analyzer",
    "./commands/quick-code",
    "./commands/scaffold",
    "./commands/workflow-suite"
  ]
}
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 插件标识符（唯一） | `"coding-workflow"` |
| `version` | 语义化版本号 | `"3.0.0"` |
| `description` | 插件描述 | `"AI 智能工作流系统"` |
| `author` | 作者信息 | `{"name": "...", "url": "..."}` |
| `skills` | Skills 目录路径 | `"./skills"` |
| `agents` | Agents 目录路径数组 | `["./agents/bmad-workflow"]` |
| `commands` | Commands 目录路径数组 | `["./commands/bmad-workflow"]` |

### 依赖验证钩子 (hooks.json)

**文件**: `hooks/hooks.json`

```json
{
  "SessionStart": [
    {
      "type": "prompt",
      "prompt": "检查 Coding Workflow 插件的依赖项（仅在首次检查或距上次检查超过24小时时执行）：\n\n1. **memex-cli**: 运行 `which memex-cli` (macOS/Linux) 或 `where memex-cli` (Windows) 检查是否安装。\n   - 如未找到，提示用户安装：`npm install -g memex-cli`\n   - 如已安装，验证版本：`memex-cli --version`（需要 >= 1.0.0）\n\n2. **Python 依赖**: 运行 `python -c \"import chardet, yaml\"` 检查。\n   - 如导入失败，提示：`pip install chardet pyyaml`\n\n3. **缓存检查结果**: 将检查时间戳保存到 ~/.claude/coding-workflow-deps-check.txt，避免频繁检查。\n\n如果所有依赖都已满足，显示简短的成功消息。如果有缺失，显示清晰的安装指令但允许继续使用插件（某些功能可能受限）。"
    }
  ]
}
```

**SessionStart 钩子**：

- **触发时机**: 每次 Claude Code 会话启动时
- **执行频率**: 24 小时内只执行一次（通过时间戳缓存）
- **检查项**:
  1. `memex-cli` 可执行文件
  2. Python 依赖包（chardet、pyyaml）
- **缓存机制**: 检查结果保存到 `~/.claude/coding-workflow-deps-check.txt`
- **用户体验**: 依赖缺失时提示安装，但允许继续使用插件

### 配置管理

#### 配置文件位置

**用户配置**: `~/.claude/coding-workflow.local.md`

- 用户可自定义配置项
- 不提交到 Git（`.gitignore` 已排除）
- 通过 YAML frontmatter 定义配置

**配置模板**: `docs/coding-workflow.local.example.md`

- 提供配置示例和说明
- 用户可复制此文件并修改

#### 当前支持的配置项

```yaml
---
memexCliPath: "memex-cli"
---
```

**memexCliPath** - memex-cli 可执行文件路径

- **默认值**: `"memex-cli"` (从 PATH 中查找)
- **自定义场景**:
  - memex-cli 不在系统 PATH 中
  - 使用自定义安装路径
  - 需要指定特定版本
- **示例**:
  ```yaml
  # macOS/Linux
  memexCliPath: "/usr/local/bin/memex-cli"

  # Windows
  memexCliPath: "C:\\Program Files\\nodejs\\memex-cli.cmd"
  ```

#### 未来配置项（规划中）

```yaml
---
memexCliPath: "memex-cli"
enabledBackends:
  - claude
  - gemini
  - codex
defaultModel: "claude-sonnet-4-5"
logLevel: "info"  # debug | info | warn | error
---
```

### 插件安装流程

```
用户执行: /plugin coding-workflow
    ↓
Claude Code Plugin Manager
    ├─ 下载插件到 ~/.claude/plugins/coding-workflow/
    ├─ 解析 .claude-plugin/plugin.json
    ├─ 注册 Skills (21 个)
    │   └─ skills/master-orchestrator/SKILL.md
    │   └─ skills/code-with-codex/SKILL.md
    │   └─ ...
    ├─ 注册 Agents (36 个)
    │   └─ agents/bmad-workflow/*.md
    │   └─ agents/bmad-iterate/*.md
    │   └─ ...
    ├─ 注册 Commands (47 个)
    │   └─ commands/bmad-workflow/*.md
    │   └─ commands/quick-code/*.md
    │   └─ ...
    ├─ 注册 SessionStart 钩子
    │   └─ hooks/hooks.json
    └─ 完成安装
    ↓
会话启动时
    ├─ 执行 SessionStart 钩子
    ├─ 检查依赖（memex-cli、Python 包）
    ├─ 读取配置 (~/.claude/coding-workflow.local.md)
    └─ 显示状态消息
```

### 架构整合

```
┌─────────────────────────────────────────────────────────┐
│               Claude Code Plugin Layer                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Plugin Manager                                   │  │
│  │  - 发现和注册 (Skills/Agents/Commands)             │  │
│  │  - 生命周期管理 (SessionStart 钩子)               │  │
│  │  - 配置加载 (coding-workflow.local.md)            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 MasterOrchestrator                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │    ClaudeIntentAnalyzer (Claude LLM 意图分析)     │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │         ExecutionRouter (执行路由层)              │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────┘
         ┌────────────┼────────────┐
         │            │            │
┌────────▼────┐  ┌───▼────┐  ┌───▼─────┐
│  Command    │  │ Agent  │  │ Skill   │
│ Executor V2 │  │Caller  │  │Executor │
└─────────────┘  └────────┘  └─────────┘
```

**插件层职责**：

1. **资源发现**: 扫描并注册所有 Skills、Agents、Commands
2. **依赖管理**: SessionStart 钩子验证必需依赖
3. **配置注入**: 加载用户配置并传递给 MasterOrchestrator
4. **生命周期**: 管理插件的启动、运行、更新

**MasterOrchestrator 与插件层交互**：

- MasterOrchestrator 无需感知插件系统
- 插件层负责提供所有必需的资源和配置
- 配置通过环境变量或配置文件传递
- 依赖验证在 MasterOrchestrator 启动前完成

### 设计亮点

1. **零侵入**: MasterOrchestrator 代码无需修改即可支持插件
2. **自动化**: 依赖检查和配置加载全自动化
3. **用户友好**: 清晰的错误提示和安装指引
4. **可选配置**: 默认配置开箱即用，高级配置按需定制
5. **缓存优化**: 24 小时内避免重复依赖检查

### 故障排查

#### 问题 1: 依赖检查失败

**症状**:
```
[错误] memex-cli not found. 请运行: npm install -g memex-cli
```

**解决方案**:
1. 安装 memex-cli:
   ```bash
   npm install -g memex-cli
   ```
2. 验证安装:
   ```bash
   memex-cli --version
   ```
3. 如已安装但仍报错，配置自定义路径:
   ```bash
   cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
   # 编辑 memexCliPath 字段
   ```

#### 问题 2: Python 依赖缺失

**症状**:
```
[错误] Python 依赖缺失: chardet, pyyaml
```

**解决方案**:
```bash
pip install chardet pyyaml
```

#### 问题 3: 配置不生效

**症状**: 修改了配置文件但未生效

**解决方案**:
1. 确认配置文件位置正确: `~/.claude/coding-workflow.local.md`
2. 检查 YAML frontmatter 格式:
   ```yaml
   ---
   memexCliPath: "/path/to/memex-cli"
   ---
   ```
3. 重启 Claude Code 会话

#### 问题 4: 依赖检查频繁执行

**症状**: 每次启动都执行依赖检查

**解决方案**:
- 检查缓存文件: `~/.claude/coding-workflow-deps-check.txt`
- 如缓存文件不存在或权限错误，系统会每次检查
- 手动创建缓存文件:
  ```bash
  echo "$(date +%s)" > ~/.claude/coding-workflow-deps-check.txt
  ```

---

## 模块详解

### 0. AduibClient (远程缓存客户端) 【新增】

**文件**: `orchestrator/clients/aduib_client.py` (475 行)

**职责**：
- 与 aduib-ai 远程服务通信
- 查询和保存任务执行结果
- 提供缓存命中优化
- 任务历史管理和统计

**核心接口**：

```python
class AduibClient:
    def __init__(
        self,
        base_url: Optional[str] = None,   # 默认: ADUIB_URL环境变量
        api_key: Optional[str] = None,    # 默认: ADUIB_API_KEY环境变量
        timeout: int = 30
    ):
        """初始化远程缓存客户端"""
        self.base_url = base_url or os.getenv("ADUIB_URL")
        self.api_key = api_key or os.getenv("ADUIB_API_KEY")
        self.timeout = timeout

    def query_cache(
        self,
        request: str,
        mode: str,
        backend: str
    ) -> Optional[CachedResult]:
        """
        查询缓存结果

        缓存键 = SHA256(request:mode:backend)
        返回: CachedResult(task_id, output, hit_count) 或 None
        """
        # 使用 aiohttp 异步请求
        # GET /api/cache/query

    def save_task_result(
        self,
        request: str,
        mode: str,
        backend: str,
        success: bool,
        output: str,
        error: Optional[str] = None,
        run_id: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> bool:
        """
        保存任务执行结果

        POST /api/tasks/save
        返回: True/False
        """
```

**缓存工作流**：

```
1. 用户请求 → MasterOrchestrator
2. 计算缓存键: SHA256(request:mode:backend)
3. 查询 Aduib-AI:
   ├─ 缓存命中 → 直接返回结果 (节省 AI 调用)
   └─ 缓存未命中 → 继续执行
4. 执行任务 (通过 ExecutionRouter)
5. 保存结果到 Aduib-AI
6. 返回结果给用户
```

**性能优势**：
- **缓存命中率 50%** → 平均响应时间减少 50%
- **缓存命中率 80%** → 平均响应时间减少 78%
- 减少重复的 API 调用，降低成本

**设计亮点**：
- 完全可选：系统可在无 aduib-ai 时正常运行
- 自动降级：连接失败时自动回退到本地执行
- 异步架构：使用 `aiohttp` 高效通信
- 零侵入：对现有代码无影响

**参考文档**: `docs/ADUIB_FEATURES.md`, `docs/ADUIB_INTEGRATION.md`

---

### 0.5. MemexExecutorBase (统一执行器基类) 【新增】

**文件**: `orchestrator/executors/memex_executor_base.py` (100 行)

**职责**：
- 所有执行器的抽象基类
- 提供统一的 memex-cli 调用接口
- 标准化错误处理和超时控制
- 确保架构一致性

**核心接口**：

```python
from abc import ABC, abstractmethod

class MemexExecutorBase(ABC):
    """统一执行器基类"""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        default_backend: str = "claude",
        default_timeout: int = 60
    ):
        self.backend_orch = backend_orch
        self.default_backend = default_backend
        self.default_timeout = default_timeout

    def execute_via_memex(
        self,
        prompt: str,
        backend: Optional[str] = None,
        stream_format: str = "jsonl",
        timeout: Optional[int] = None,
        **kwargs
    ) -> TaskResult:
        """
        通过 memex-cli 执行任务

        统一封装：
        1. 调用 backend_orch.run_task()
        2. 处理超时
        3. 标准化结果
        """
        backend = backend or self.default_backend
        timeout = timeout or self.default_timeout

        return self.backend_orch.run_task(
            backend=backend,
            prompt=prompt,
            stream_format=stream_format,
            timeout=timeout,
            **kwargs
        )

    @abstractmethod
    def execute(self, request: str, **kwargs):
        """子类必须实现的执行方法"""
        pass
```

**继承体系**：

```
MemexExecutorBase (抽象基类)
    ├─ CommandExecutor V2
    │   └─ execute() → 通过 command-parser.yaml skill
    │
    ├─ AgentCaller V2
    │   └─ execute() → 通过 agent-router.yaml skill
    │
    ├─ PromptManager V2
    │   └─ execute() → 通过 prompt-renderer.yaml skill
    │
    └─ SkillExecutor
        └─ execute() → 通过 dev-workflow.yaml skill
```

**三层 Fallback 机制**：

```
第1层: Memex-CLI + Claude Skill
    ↓ (失败)
第2层: 本地实现 (rules/simple/local)
    ↓ (失败)
第3层: 错误返回 (ErrorResult)
```

**设计亮点**：
- **统一接口**：所有执行器使用相同的基类
- **强制架构**：`@abstractmethod` 确保子类实现 `execute()`
- **配置继承**：子类自动获得 `backend_orch` 和超时配置
- **扩展性**：添加新执行器只需继承并实现 `execute()`

---

### 1. MasterOrchestrator (总协调器)

**文件**: `orchestrator/master_orchestrator.py` (700+ 行)

**职责**：
- 系统入口点
- 初始化所有子模块（包括 Aduib-AI 客户端）
- 协调 ClaudeIntentAnalyzer 和 ExecutionRouter
- 管理缓存查询和结果上传
- 处理结果类型转换

**关键接口**：

```python
class MasterOrchestrator:
    def __init__(
        self,
        backend_orch: Optional[BackendOrchestrator] = None,
        use_claude_intent: bool = True,
        use_remote: Optional[bool] = None,
        aduib_url: Optional[str] = None,
        aduib_api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_upload: bool = True,
        verbose: bool = False
    ):
        """
        初始化总协调器

        Args:
            backend_orch: BackendOrchestrator实例（可选）
            use_claude_intent: 是否使用Claude进行意图识别
            use_remote: 是否使用Aduib-AI远程服务（None=自动检测）
            aduib_url: Aduib-AI服务地址
            aduib_api_key: Aduib-AI API密钥
            enable_cache: 是否启用缓存查询
            enable_upload: 是否启用结果上传
            verbose: 是否输出详细日志
        """
        self.backend_orch = backend_orch or BackendOrchestrator()
        self.verbose = verbose

        # 意图分析器（Claude LLM 或规则引擎）
        if use_claude_intent:
            self.analyzer = ClaudeIntentAnalyzer(self.backend_orch)
        else:
            self.analyzer = IntentAnalyzer()  # 规则引擎 fallback

        # 执行路由器
        self.router = ExecutionRouter(self.backend_orch)

        # 【新增】Aduib-AI 远程缓存客户端
        self.aduib_client = None
        self.enable_cache = enable_cache
        self.enable_upload = enable_upload

        # 自动检测：如果设置了 ADUIB_API_KEY，则启用
        if use_remote is None:
            use_remote = bool(os.getenv("ADUIB_API_KEY"))

        if use_remote:
            try:
                self.aduib_client = AduibClient(
                    base_url=aduib_url,
                    api_key=aduib_api_key,
                    timeout=30
                )
            except Exception as e:
                print(f"[警告] 无法初始化 aduib-ai 客户端: {e}")
                self.aduib_client = None

    def process(self, request: str, verbose: bool = False) -> Any:
        """
        处理用户请求（支持缓存）

        流程：
        1. 意图分析（Claude LLM）
        2. 【新增】查询 Aduib-AI 缓存
        3. 如果缓存未命中，执行任务
        4. 【新增】保存结果到 Aduib-AI
        5. 返回结果

        Returns:
            WorkflowResult | TaskResult | CommandResult | AgentResult
        """
        # 1. 意图分析
        intent = self._analyze_intent(request, verbose=verbose)

        # 2. 【新增】查询缓存
        if self.aduib_client and self.enable_cache:
            cached = self.aduib_client.query_cache(
                request=request,
                mode=intent.mode.value,
                backend=self._select_backend(intent)
            )
            if cached:
                if verbose:
                    print(f"[缓存命中] 从远程缓存返回结果")
                return self._convert_cached_result(cached, intent.mode)

        # 3. 执行路由（缓存未命中）
        result = self.router.route(request, intent)

        # 4. 【新增】保存结果到缓存
        if self.aduib_client and self.enable_upload and self._should_upload(result):
            self.aduib_client.save_task_result(
                request=request,
                mode=intent.mode.value,
                backend=self._select_backend(intent),
                success=result.success,
                output=result.output,
                error=getattr(result, 'error', None),
                duration_seconds=getattr(result, 'duration_seconds', None)
            )

        return result
```

**设计亮点**：
- 使用依赖注入传递 BackendOrchestrator
- 返回类型多态（根据执行模式返回不同结果类型）
- 集中化错误处理
- **【新增】自动缓存管理**：查询和保存对用户透明
- **【新增】自动降级**：Aduib-AI 不可用时自动禁用

---

### 2. ClaudeIntentAnalyzer (Claude LLM 意图分析器) 【新增】

**文件**: `orchestrator/analyzers/claude_intent_analyzer.py` (200 行)

**职责**：
- 使用 Claude LLM 进行智能意图识别
- 通过 memex-cli skill: `intent-analyzer.yaml`
- 语义理解用户请求
- 识别执行模式、任务类型、复杂度、后端建议

**核心接口**：

```python
class ClaudeIntentAnalyzer:
    def __init__(self, backend_orch: BackendOrchestrator):
        self.backend_orch = backend_orch
        self.skill_name = "intent-analyzer"

    def analyze(self, request: str, verbose: bool = False) -> Intent:
        """
        使用 Claude LLM 分析意图

        流程：
        1. 构建提示词（使用 intent-analyzer.yaml skill）
        2. 调用 memex-cli → Claude
        3. 解析 JSON 响应
        4. 返回 Intent 对象
        """
        # 调用 intent-analyzer.yaml skill
        result = self.backend_orch.run_skill(
            skill_name=self.skill_name,
            variables={"request": request},
            backend="claude"
        )

        # 解析 JSON 响应
        intent_data = json.loads(result.output)

        return Intent(
            mode=ExecutionMode(intent_data["mode"]),
            task_type=intent_data["task_type"],
            complexity=intent_data["complexity"],
            backend_hint=intent_data.get("backend_hint"),
            skill_hint=intent_data.get("skill_hint"),
            confidence=intent_data.get("confidence", 0.0)
        )
```

**Skill 配置** (`skills/memex-cli/skills/intent-analyzer.yaml`):

```yaml
name: intent-analyzer
backend: claude
model: claude-3-5-sonnet-20241022

system_prompt: |
  你是一个智能任务分类器。分析用户请求并返回 JSON 格式的意图分析。

  执行模式（mode）:
  - command: 简单命令执行（git, npm, pytest等）
  - agent: 代码库探索、规划任务
  - prompt: 模板化专业任务（代码审查、文档生成）
  - skill: 复杂多阶段工作流（开发系统、项目）
  - backend: 通用查询

  任务类型（task_type）:
  - dev: 开发、编码
  - ux: 设计、用户体验
  - analysis: 分析、优化
  - test: 测试
  - other: 其他

  复杂度（complexity）:
  - simple: 简单任务
  - medium: 中等复杂度
  - complex: 复杂任务（多阶段、系统级）

user_prompt_template: |
  请分析以下用户请求：

  用户请求：{{request}}

  返回 JSON 格式（纯 JSON，无markdown）：
  {
    "mode": "command/agent/prompt/skill/backend",
    "task_type": "dev/ux/analysis/test/other",
    "complexity": "simple/medium/complex",
    "backend_hint": "claude/gemini/codex",
    "skill_hint": "技能名称（如果适用）",
    "confidence": 0.85
  }
```

**设计亮点**：
- **语义理解**：Claude LLM 理解自然语言，无需正则表达式
- **高准确性**：利用 LLM 的推理能力，识别准确率高
- **可配置**：通过 YAML skill 配置，易于调整
- **Fallback 机制**：如果 Claude 不可用，自动降级到规则引擎 IntentAnalyzer

---

### 2.1. IntentAnalyzer (规则引擎意图分析器) 【Fallback】

**文件**: `orchestrator/master_orchestrator.py` (IntentAnalyzer 类)

**职责**：
- ClaudeIntentAnalyzer 的 Fallback 实现
- 基于正则表达式的规则匹配
- 无需 API 调用，快速响应

**算法流程**：

```
输入: 用户请求字符串
  ↓
1. 模式识别（优先级从高到低）
   - Command: "运行"、"执行" + 命令名
   - Agent: "查找"、"搜索"、"规划"
   - Prompt: "生成"、"审查"、"文档"
   - Skill: "开发"、"实现" + "系统"/"项目"
   - Backend: 默认
  ↓
2. 任务类型识别
   - dev: "开发"、"实现"、"编写代码"
   - ux: "设计"、"界面"、"交互"
   - analysis: "分析"、"优化"、"性能"
   - test: "测试"、"单元测试"
  ↓
3. 复杂度评估
   - complex: "完整"、"系统"、"平台" + 长度 > 20
   - simple: 长度 < 10
   - medium: 其他
  ↓
输出: Intent(mode, task_type, complexity, skill_hint)
```

**正则模式示例**：

```python
# 中文 + 英文混合模式
self.mode_patterns = {
    ExecutionMode.COMMAND: [
        (r'(运行|执行).{0,5}(命令|脚本)', 'command'),
        (r'(run|execute)\s+\w+', 'command'),
    ],
    ExecutionMode.SKILL: [
        (r'(开发|实现).{0,10}(系统|功能|项目|小程序)', 'dev'),
        (r'(develop|build|create).{0,10}(system|app|project)', 'dev'),
    ],
}
```

**设计亮点**：
- 使用正则表达式的 `.{0,N}` 处理中文无空格问题
- 优先级队列确保精确匹配优先
- 可配置的模式规则

---

### 3. ExecutionRouter (执行路由器)

**文件**: `master_orchestrator.py` (ExecutionRouter 类)

**职责**：
- 根据 Intent 路由到对应的执行器
- 后端选择逻辑
- 结果类型统一

**路由决策树**：

```
Intent.mode
  │
  ├─ COMMAND → _execute_command() → CommandExecutor
  │
  ├─ AGENT → _call_agent() → AgentCaller
  │
  ├─ PROMPT → _use_prompt() → PromptManager + Backend
  │
  ├─ SKILL → _execute_skill()
  │     │
  │     ├─ 检测: multcode-dev-workflow-agent
  │     │   或 (complexity=complex + task_type=dev)
  │     │     ↓
  │     │   DevWorkflowAgent.run() → 5阶段自动化
  │     │
  │     └─ 否则: 增强提示词 + Backend
  │
  └─ BACKEND → _call_backend() → BackendOrchestrator
```

**后端选择逻辑**：

```python
def _select_backend(self, intent: Intent) -> str:
    """
    根据意图选择最佳后端

    规则：
    - dev/test → Codex (代码生成能力强)
    - ux → Gemini (视觉和设计能力强)
    - analysis/其他 → Claude (分析和推理能力强)
    """
    if intent.task_type in ["dev", "test"]:
        return "codex"
    elif intent.task_type == "ux":
        return "gemini"
    else:
        return "claude"
```

**设计亮点**：
- 单一职责：只负责路由，不执行具体逻辑
- 可扩展：添加新模式只需新增一个 `_execute_*` 方法
- 后端选择可配置

---

### 4. CommandExecutor V2 (命令执行器) 【更新】

**文件**: `orchestrator/executors/command_executor.py` (300 行)

**继承**: `MemexExecutorBase` (统一基类)

**职责**：
- 使用 Claude LLM 解析自然语言到 Shell 命令
- 通过 memex-cli skill: `command-parser.yaml`
- 安全检查（白名单 + 危险模式检测）
- 执行命令并捕获输出

**架构**（V2 三层 Fallback）：

```
用户请求: "查看git状态"
  ↓
【第1层】execute() - 尝试 Claude Skill
  ├─ 调用 execute_via_memex()
  ├─ skill: command-parser.yaml
  ├─ Claude解析: "查看git状态" → "git status"
  ├─ 返回: CommandResult
  └─ (如果成功) 返回结果
  ↓ (如果失败)
【第2层】Fallback - 规则引擎解析
  ├─ _parse_command_local()
  ├─ 正则匹配: r'查看.*git.*状态' → "git status"
  ├─ 返回: CommandResult
  └─ (如果成功) 返回结果
  ↓ (如果失败)
【第3层】Error Handling
  └─ 返回 CommandResult(success=False, error="解析失败")
  ↓
安全检查 (所有层都执行)
  ├─ is_safe()
  ├─ 白名单检查: git ∈ ALLOWED_COMMANDS ✓
  ├─ 危险模式检查: 无匹配 ✓
  └─ (通过) 执行命令
  ↓
execute_shell()
  ├─ subprocess.run(["git", "status"])
  ├─ 捕获 stdout, stderr, return_code
  └─ 返回 CommandResult
```

**Skill 配置** (`skills/memex-cli/skills/command-parser.yaml`):

```yaml
name: command-parser
backend: claude

system_prompt: |
  你是命令解析专家。将自然语言转换为Shell命令。

  规则：
  1. 只返回命令字符串，无解释
  2. 常用命令: git, npm, docker, pytest, python
  3. 不包含危险命令: rm -rf /, dd, mkfs

user_prompt_template: |
  将以下自然语言转换为Shell命令：

  {{request}}

  返回格式：仅返回命令字符串
```

**核心代码**：

```python
class CommandExecutor(MemexExecutorBase):
    """命令执行器 V2 - 继承 MemexExecutorBase"""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        use_claude: bool = True,
        fallback_to_rules: bool = True
    ):
        super().__init__(backend_orch, default_backend="claude")
        self.use_claude = use_claude
        self.fallback_to_rules = fallback_to_rules

    def execute(self, request: str, **kwargs) -> CommandResult:
        """执行命令（三层 Fallback）"""

        # 第1层: Claude Skill
        if self.use_claude:
            try:
                result = self.execute_via_memex(
                    prompt=f"解析命令: {request}",
                    backend="claude"
                )
                command = result.output.strip()

                # 安全检查
                safe, reason = self.is_safe(command)
                if not safe:
                    return CommandResult(
                        success=False,
                        error=f"安全检查失败: {reason}"
                    )

                # 执行命令
                return self._execute_shell(command)

            except Exception as e:
                if not self.fallback_to_rules:
                    return CommandResult(success=False, error=str(e))

        # 第2层: 规则引擎 Fallback
        command = self._parse_command_local(request)
        if command:
            safe, reason = self.is_safe(command)
            if safe:
                return self._execute_shell(command)

        # 第3层: 错误返回
        return CommandResult(success=False, error="无法解析命令")
```

**安全机制**：

1. **白名单**：
```python
ALLOWED_COMMANDS = {
    "git", "npm", "yarn", "python", "pytest",
    "docker", "node", "cargo", "go", "make"
}
```

2. **危险模式检测**：
```python
DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',        # 删除根目录
    r'mkfs',                # 格式化磁盘
    r'dd\s+if=.*of=/dev/',  # 直接写磁盘
    r':(){:|:&};:',         # Fork 炸弹
]
```

3. **参数验证**：
```python
# 检查路径注入
if '..' in arg or arg.startswith('/'):
    return False, "Suspicious path detected"
```

**设计亮点**：
- 分层验证：命令名 → 参数 → 危险模式
- 用户友好错误：明确说明拒绝原因
- 支持自然语言解析

---

### 5. PromptManager (提示词管理器)

**文件**: `prompts/prompt_manager.py` (280 行)

**职责**：
- 管理专业提示词模板
- 模板渲染和变量替换
- 模板注册和查询

**模板结构**：

```python
@dataclass
class PromptTemplate:
    name: str                # 模板名称
    category: str            # 类别（development, analysis 等）
    description: str         # 描述
    template: str            # 模板字符串（包含 {变量}）
    variables: List[str]     # 必需变量列表
    optional_vars: Dict[str, str] = field(default_factory=dict)  # 可选变量 + 默认值
```

**模板示例**：

```python
PromptTemplate(
    name="code-generation",
    category="development",
    description="生成高质量代码",
    template="""你是一位经验丰富的软件工程师。

需求描述：{requirement}
技术栈：{tech_stack}
编程语言：{language}

请提供：
1. 完整的代码实现
2. 必要的注释
3. 错误处理
4. 使用示例
""",
    variables=["requirement", "tech_stack", "language"],
    optional_vars={"style": "production-ready"}
)
```

**渲染流程**：

```
render(template_name, **kwargs)
  ↓
1. 获取模板
   template = self.templates.get(name)
  ↓
2. 验证必需变量
   missing = set(template.variables) - set(kwargs.keys())
   if missing: raise ValueError
  ↓
3. 合并默认值
   final_vars = {**template.optional_vars, **kwargs}
  ↓
4. 渲染
   return template.template.format(**final_vars)
```

**设计亮点**：
- 模板化避免重复编写提示词
- 变量验证确保模板完整
- 支持可选变量和默认值

---

### 6. AgentCaller (智能体调用器)

**文件**: `agents/agent_caller.py` (260 行)

**职责**：
- 集成 Claude Code 的智能体（Task tool）
- 智能体类型选择
- 参数配置

**智能体类型**：

```python
class AgentType(Enum):
    GENERAL_PURPOSE = "general-purpose"  # 通用任务
    EXPLORE = "Explore"                  # 代码库探索
    PLAN = "Plan"                        # 实施规划
```

**调用流程**：

```
AgentRequest(agent_type, prompt, thoroughness)
  ↓
call_agent()
  ↓
1. 构建 Task tool 参数
   {
     "subagent_type": agent_type.value,
     "prompt": prompt,
     "description": auto_generated,
   }
  ↓
2. 调用 Claude Code Task tool
   （注：这里简化为模拟，实际应调用 Task tool）
  ↓
3. 解析结果
   return AgentResult(success, agent_type, output)
```

**类型选择逻辑**：

```python
def suggest_agent_type(self, task: str) -> AgentType:
    """自动建议智能体类型"""
    task_lower = task.lower()

    # 探索关键词
    if any(kw in task_lower for kw in ["查找", "搜索", "探索", "where", "find"]):
        return AgentType.EXPLORE

    # 规划关键词
    if any(kw in task_lower for kw in ["规划", "设计", "计划", "plan"]):
        return AgentType.PLAN

    # 默认
    return AgentType.GENERAL_PURPOSE
```

**设计亮点**：
- 类型安全的 AgentRequest/AgentResult
- 自动类型推荐
- 支持 thoroughness 配置

---

### 7. DevWorkflowAgent (5阶段工作流)

**文件**: `skills/multcode-dev-workflow-agent/auto_workflow.py` (450 行)

**职责**：
- 执行 5 阶段自动化工作流
- 阶段间数据传递
- 阶段验证

**工作流架构**：

```
run(requirement) → WorkflowResult
  │
  ├─ 阶段 1: REQUIREMENTS (Claude)
  │    ├─ 构建提示词: template.format(requirement=...)
  │    ├─ 调用后端: backend_orch.run_task("claude", prompt)
  │    ├─ 验证输出: StageValidator.validate_requirements()
  │    └─ 保存输出: previous_outputs[REQUIREMENTS] = output
  │
  ├─ 阶段 2: FEATURE_DESIGN (Claude)
  │    ├─ 构建提示词: template.format(
  │    │                  requirement=...,
  │    │                  previous_output=previous_outputs[REQUIREMENTS]
  │    │                )
  │    ├─ 调用后端: backend_orch.run_task("claude", prompt)
  │    ├─ 验证输出: StageValidator.validate_feature_design()
  │    └─ 保存输出: previous_outputs[FEATURE_DESIGN] = output
  │
  ├─ 阶段 3: UX_DESIGN (Gemini)
  │    └─ ... (类似流程)
  │
  ├─ 阶段 4: DEV_PLAN (Codex)
  │    ├─ 使用 feature_design + ux_design 作为输入
  │    └─ ... (类似流程)
  │
  └─ 阶段 5: IMPLEMENTATION (Codex)
       └─ 使用 dev_plan 作为输入
```

**阶段配置**：

```python
STAGE_CONFIG = {
    WorkflowStage.REQUIREMENTS: {
        "backend": "claude",                          # 使用的后端
        "validator": StageValidator.validate_requirements,  # 验证函数
        "prompt_template": """..."""                 # 提示词模板
    },
    # ... 其他阶段
}
```

**数据传递机制**：

```python
def _build_prompt(self, template, requirement, previous_outputs):
    """构建阶段提示词，注入前序阶段结果"""
    variables = {
        "requirement": requirement,
        "previous_output": previous_outputs.get(last_stage, ""),
        "feature_design": previous_outputs.get(WorkflowStage.FEATURE_DESIGN, ""),
        "ux_design": previous_outputs.get(WorkflowStage.UX_DESIGN, ""),
    }
    return template.format(**variables)
```

**验证器**：

```python
class StageValidator:
    @staticmethod
    def validate_requirements(output: str) -> Tuple[bool, Optional[str]]:
        """验证需求分析输出"""
        if len(output) < 20:
            return False, "需求分析输出过短"
        return True, None

    # ... 其他验证器
```

**设计亮点**：
- 配置驱动：添加新阶段只需修改 STAGE_CONFIG
- 数据流明确：previous_outputs 字典管理所有中间结果
- 失败快速：任何阶段失败立即中止并报告
- 可恢复：支持从指定阶段重新开始

---

### 8. SkillRegistry (技能注册表)

**文件**: `skills/skill_registry.py` (320 行)

**职责**：
- 自动发现技能
- 元数据管理
- 依赖检查

**自动发现流程**：

```
_load_skills()
  ↓
1. 扫描 skills/ 目录
   for skill_dir in skills_dir.iterdir()
  ↓
2. 查找 SKILL.md
   skill_md = skill_dir / "SKILL.md"
  ↓
3. 解析元数据
   metadata = _parse_skill_metadata(skill_dir, skill_md)
  ↓
4. 注册技能
   self.skills[metadata.name] = metadata
```

**元数据结构**：

```python
@dataclass
class SkillMetadata:
    name: str                          # 技能名称
    category: SkillCategory            # 类别（DEVELOPMENT, UX_DESIGN 等）
    description: str                   # 描述
    version: str                       # 版本号
    author: str                        # 作者
    backends_required: List[str]       # 需要的后端
    dependencies: List[str]            # 依赖的其他技能
    config: Dict[str, Any]             # 配置选项
    entry_point: Optional[str]         # 入口文件路径
```

**推断逻辑**：

```python
def _infer_category(self, name: str, dirname: str) -> SkillCategory:
    """根据名称推断类别"""
    name_lower = name.lower() + " " + dirname.lower()

    if "dev" in name_lower or "workflow" in name_lower:
        return SkillCategory.DEVELOPMENT
    elif "ux" in name_lower or "design" in name_lower:
        return SkillCategory.UX_DESIGN
    # ...
```

**设计亮点**：
- 零配置：技能只需放在 skills/ 目录即可自动注册
- 智能推断：自动推断类别、后端需求
- 依赖检查：防止使用未满足依赖的技能

---

### 9. BackendOrchestrator (后端协调器)

**文件**: `skills/cross-backend-orchestrator/scripts/orchestrator.py` (500 行)

**职责**：
- 管理多个 AI 后端（Claude, Gemini, Codex）
- memex-cli 集成
- 事件流解析

**架构**：

```
run_task(backend, prompt, stream_format)
  ↓
1. 验证 memex-cli
   _check_memex_cli()
  ↓
2. 构建命令
   cmd = ["memex-cli", "run", backend, prompt, "--stream", stream_format]
  ↓
3. 执行命令
   process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
  ↓
4. 读取输出
   raw_output = process.stdout.read()
  ↓
5. 解析事件流（如果 parse_events=True）
   events = EventParser.parse(raw_output)
  ↓
6. 提取 run_id
   run_id = _extract_run_id(events)
  ↓
7. 返回结果
   return TaskResult(success, output, events, run_id)
```

**后端配置**：

```python
SUPPORTED_BACKENDS = ["claude", "gemini", "codex"]

def run_task(self, backend: str, prompt: str, stream_format: str = "jsonl"):
    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"Unsupported backend: {backend}")
    # ...
```

**设计亮点**：
- 统一接口：所有后端使用相同的 API
- 自动 run_id 提取：从事件流中提取唯一标识
- 错误透明：捕获并传递后端错误

---

### 10. EventParser (事件解析器)

**文件**: `skills/cross-backend-orchestrator/scripts/event_parser.py` (300 行)

**职责**：
- 解析 memex-cli 的 JSONL 事件流
- 处理编码问题（UTF-16 LE）
- 提取关键信息

**解析流程**：

```
parse(raw_output: bytes)
  ↓
1. 编码检测
   encoding = detect_encoding(raw_output)
   # 可能是: utf-8, utf-16-le
  ↓
2. 解码
   text = raw_output.decode(encoding)
  ↓
3. 按行解析 JSON
   for line in text.splitlines():
       if line.strip():
           event = json.loads(line)
           events.append(event)
  ↓
4. 返回事件列表
   return events
```

**编码检测**：

```python
def detect_encoding(data: bytes) -> str:
    """检测编码（Windows 可能输出 UTF-16 LE）"""
    # 检查 BOM
    if data[:2] == b'\xff\xfe':
        return 'utf-16-le'

    # 尝试 UTF-8
    try:
        data.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        pass

    # 使用 chardet
    import chardet
    result = chardet.detect(data)
    return result['encoding']
```

**事件结构**：

```json
{
  "type": "text_delta",
  "content": "生成的文本...",
  "timestamp": "2026-01-04T10:30:00Z"
}

{
  "type": "run_start",
  "run_id": "run_abc123",
  "backend": "claude"
}
```

**设计亮点**：
- 自动编码检测：处理 Windows 的 UTF-16 LE 问题
- 健壮的 JSON 解析：忽略空行和非 JSON 行
- 事件流提取：提供结构化的事件列表

---

## 数据流

### 完整请求处理流程

```
用户: "开发一个博客系统"
  ↓
[1] MasterOrchestrator.process()
  ├─ Intent = IntentAnalyzer.analyze("开发一个博客系统")
  │    └─ Intent(mode=SKILL, task_type=dev, complexity=complex)
  └─ Result = ExecutionRouter.route(request, intent)
  ↓
[2] ExecutionRouter._execute_skill()
  ├─ 检测: complexity=complex and task_type=dev
  │    └─ 触发 DevWorkflowAgent
  └─ WorkflowResult = DevWorkflowAgent.run("开发一个博客系统")
  ↓
[3] DevWorkflowAgent.run()
  ├─ 阶段 1: Requirements
  │    ├─ prompt = build_prompt(REQUIREMENTS, "开发一个博客系统", {})
  │    ├─ TaskResult = BackendOrchestrator.run_task("claude", prompt)
  │    ├─ validate_requirements(TaskResult.output) → ✓
  │    └─ previous_outputs[REQUIREMENTS] = TaskResult.output
  │
  ├─ 阶段 2: Feature Design
  │    ├─ prompt = build_prompt(FEATURE_DESIGN, "开发...", previous_outputs)
  │    ├─ TaskResult = BackendOrchestrator.run_task("claude", prompt)
  │    ├─ validate_feature_design(TaskResult.output) → ✓
  │    └─ previous_outputs[FEATURE_DESIGN] = TaskResult.output
  │
  ├─ 阶段 3: UX Design
  │    ├─ prompt = build_prompt(UX_DESIGN, "开发...", previous_outputs)
  │    ├─ TaskResult = BackendOrchestrator.run_task("gemini", prompt)
  │    └─ ...
  │
  ├─ 阶段 4: Dev Plan
  │    └─ ... (使用 codex 后端)
  │
  └─ 阶段 5: Implementation
       └─ ... (使用 codex 后端)
  ↓
[4] BackendOrchestrator.run_task("claude", prompt)
  ├─ cmd = ["memex-cli", "run", "claude", prompt, "--stream", "jsonl"]
  ├─ process = subprocess.Popen(cmd, stdout=PIPE)
  ├─ raw_output = process.stdout.read()
  ├─ events = EventParser.parse(raw_output)
  ├─ output = extract_final_output(events)
  ├─ run_id = extract_run_id(events)
  └─ return TaskResult(success=True, output=output, events=events, run_id=run_id)
  ↓
[5] 返回 WorkflowResult
  └─ WorkflowResult(
         requirement="开发一个博客系统",
         stages=[StageResult, StageResult, ...],  # 5个阶段
         success=True,
         completed_stages=5
     )
  ↓
[6] 用户接收结果
    print(f"完成阶段: {result.completed_stages}/5")
```

---

## 设计决策

### 1. 为什么使用 5 种执行模式？

**问题**: 不同类型的任务需要不同的处理方式

**决策**: 根据任务特性划分模式

| 模式 | 适用场景 | 理由 |
|------|----------|------|
| Command | 明确的命令执行 | 无需 AI 介入，直接执行更快 |
| Agent | 代码库探索 | 需要多轮搜索和分析 |
| Prompt | 专业任务 | 模板化提高质量和一致性 |
| Skill | 复杂多阶段任务 | 结构化工作流确保完整性 |
| Backend | 通用查询 | 简单直接，覆盖兜底场景 |

**优势**:
- 性能：简单任务不走复杂流程
- 质量：专业任务使用专业模板
- 灵活：覆盖从简单到复杂的所有场景

---

### 2. 为什么 5 阶段工作流？

**问题**: 复杂开发任务需要系统化的方法

**决策**: 参考软件工程最佳实践，划分 5 个阶段

```
Requirements → Feature Design → UX Design → Dev Plan → Implementation
```

**理由**:
1. **需求分析** - 明确做什么（避免需求蔓延）
2. **功能设计** - 设计怎么做（架构先行）
3. **UX 设计** - 用户如何使用（用户体验优先）
4. **开发计划** - 分步实施（可控进度）
5. **代码实现** - 落地执行（高质量代码）

**优势**:
- 结构化：避免遗漏关键步骤
- 可追踪：每个阶段有明确产出
- 可验证：每个阶段都可独立验证

---

### 3. 为什么使用不同的 AI 后端？

**问题**: 单一 AI 模型无法在所有任务上都表现最佳

**决策**: 根据任务特性选择最佳后端

| 后端 | 擅长领域 | 使用场景 |
|------|----------|----------|
| **Claude** | 需求分析、架构设计 | 阶段 1, 2（需求、功能设计）|
| **Gemini** | 视觉设计、UX | 阶段 3（UX 设计）|
| **Codex** | 代码生成、实现 | 阶段 4, 5（计划、实现）|

**优势**:
- 质量：发挥各模型优势
- 多样性：避免单一模型偏见
- 灵活：易于添加新后端

---

### 4. 为什么使用 memex-cli？

**问题**: 需要统一接口调用多个 AI 后端

**决策**: 使用 memex-cli 作为中间层

**理由**:
- 统一接口：一个命令调用所有后端
- 事件流：提供结构化的输出
- 运行追踪：自动生成 run_id

**替代方案**:
- 直接调用 API：需要分别集成每个后端的 SDK
- 自建中间层：重复造轮子

---

### 5. 为什么使用 dataclass？

**问题**: 需要清晰的数据结构

**决策**: 大量使用 `@dataclass`

**优势**:
- 类型安全：明确字段类型
- 自动生成：`__init__`, `__repr__` 等方法
- 可序列化：配合 `asdict()` 序列化为 JSON

**示例**:
```python
@dataclass
class Intent:
    mode: ExecutionMode
    task_type: str
    complexity: str
    skill_hint: Optional[str] = None
```

---

### 6. 为什么白名单而非黑名单？

**问题**: 命令执行安全

**决策**: 使用白名单 + 危险模式检测

**理由**:
- **白名单更安全** - 默认拒绝，显式允许
- **黑名单易遗漏** - 无法穷举所有危险命令

**实施**:
```python
# 白名单
if cmd_name not in ALLOWED_COMMANDS:
    return False, f"Command '{cmd_name}' not in whitelist"

# 危险模式（额外保护）
for pattern in DANGEROUS_PATTERNS:
    if re.search(pattern, command):
        return False, "Dangerous command pattern detected"
```

---

### 7. 为什么自动提取 run_id？

**问题**: 需要追踪和调试 AI 后端调用

**决策**: 从事件流中自动提取 run_id

**优势**:
- **可追溯** - 每个任务有唯一标识
- **调试友好** - 可查看完整的后端调用日志
- **无侵入** - 用户无需手动传递

**实现**:
```python
def _extract_run_id(events: List[Dict]) -> Optional[str]:
    """从事件流提取 run_id"""
    for event in events:
        if event.get("type") == "run_start":
            return event.get("run_id")
        # 或从 metadata 中提取
        if "run_id" in event:
            return event["run_id"]
    return None
```

---

## 扩展性设计

### 1. 添加新的执行模式

**步骤**:

1. 在 `ExecutionMode` 枚举中添加新模式
2. 在 `IntentAnalyzer` 中添加识别规则
3. 在 `ExecutionRouter` 中添加 `_execute_*` 方法
4. 实现对应的执行器模块

**示例 - 添加 "Translation" 模式**:

```python
# Step 1: 添加枚举
class ExecutionMode(Enum):
    # ... 现有模式
    TRANSLATION = "translation"

# Step 2: 添加识别规则
class IntentAnalyzer:
    def __init__(self):
        self.mode_patterns = {
            # ... 现有规则
            ExecutionMode.TRANSLATION: [
                (r'(翻译|translate).{0,10}(代码|文档)', 'translation'),
            ]
        }

# Step 3: 添加路由方法
class ExecutionRouter:
    def route(self, request, intent):
        # ...
        elif intent.mode == ExecutionMode.TRANSLATION:
            return self._execute_translation(request, intent)

    def _execute_translation(self, request, intent):
        # 调用翻译执行器
        from translation_executor import TranslationExecutor
        executor = TranslationExecutor()
        return executor.execute(request)
```

---

### 2. 添加新的后端

**步骤**:

1. 在 `BackendOrchestrator.SUPPORTED_BACKENDS` 中添加
2. 更新 `_select_backend` 逻辑
3. 配置 memex-cli 后端

**示例 - 添加 "GPT-4" 后端**:

```python
# Step 1: 更新支持列表
SUPPORTED_BACKENDS = ["claude", "gemini", "codex", "gpt4"]

# Step 2: 更新选择逻辑
def _select_backend(self, intent: Intent) -> str:
    if intent.task_type == "creative":
        return "gpt4"  # 创意任务用 GPT-4
    # ... 其他逻辑

# Step 3: 配置 memex-cli
# $ memex-cli backends add gpt4 --api-key YOUR_KEY
```

---

### 3. 添加新的工作流阶段

**步骤**:

1. 在 `WorkflowStage` 枚举中添加
2. 在 `STAGE_CONFIG` 中配置
3. 添加对应的验证器

**示例 - 添加 "Security Audit" 阶段**:

```python
# Step 1: 添加枚举
class WorkflowStage(Enum):
    # ... 现有阶段
    SECURITY_AUDIT = "security_audit"

# Step 2: 配置阶段
STAGE_CONFIG = {
    # ... 现有配置
    WorkflowStage.SECURITY_AUDIT: {
        "backend": "claude",
        "validator": StageValidator.validate_security_audit,
        "prompt_template": """你是一位安全专家。请审计以下实现：
{implementation}

请检查：
1. SQL 注入风险
2. XSS 漏洞
3. CSRF 防护
4. 认证和授权
5. 敏感数据处理
"""
    }
}

# Step 3: 添加验证器
class StageValidator:
    @staticmethod
    def validate_security_audit(output: str) -> Tuple[bool, Optional[str]]:
        if len(output) < 50:
            return False, "安全审计报告过短"
        if "风险" not in output and "risk" not in output.lower():
            return False, "未发现风险分析"
        return True, None
```

---

### 4. 添加新的提示词模板

**步骤**:

1. 创建 `PromptTemplate` 实例
2. 注册到 `PromptManager`

**示例 - 添加 "SQL 生成" 模板**:

```python
sql_template = PromptTemplate(
    name="sql-generation",
    category="database",
    description="生成 SQL 查询",
    template="""你是一位数据库专家。请根据以下需求生成 SQL 查询：

需求：{requirement}
数据库类型：{db_type}
表结构：{schema}

请提供：
1. SQL 查询语句
2. 查询说明
3. 索引建议
4. 性能考虑
""",
    variables=["requirement", "db_type", "schema"]
)

# 注册
manager = PromptManager()
manager.register_template(sql_template)
```

---

## 性能考虑

### 1. 事件解析开销

**问题**: 解析 JSONL 事件流有性能开销

**优化**:
```python
# 对于简单任务，禁用事件解析
orch = MasterOrchestrator(parse_events=False)
```

**影响**:
- `parse_events=True`: ~500ms 额外开销（解析和验证）
- `parse_events=False`: 仅返回原始文本

**建议**:
- 生产环境：`parse_events=False`
- 调试/开发：`parse_events=True`

---

### 2. 意图分析性能

**当前实现**: 逐个匹配正则表达式

**性能**: O(n * m)
- n = 模式数量（~30个）
- m = 请求长度

**优化思路**:
1. **优先级队列** - 高频模式优先匹配
2. **缓存** - 相同请求缓存结果
3. **预编译正则** - 编译时预编译所有模式

```python
class IntentAnalyzer:
    def __init__(self):
        # 预编译正则
        self.compiled_patterns = {
            mode: [(re.compile(pat), label) for pat, label in patterns]
            for mode, patterns in self.mode_patterns.items()
        }
```

---

### 3. 并发处理

**当前限制**: 单线程顺序执行

**并发场景**:
```python
from concurrent.futures import ThreadPoolExecutor

# 并发处理多个请求
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(orch.process, req) for req in requests]
    results = [f.result() for f in futures]
```

**注意事项**:
- memex-cli 调用可能有 API 限流
- 后端并发限制

---

## 安全性

### 1. 命令注入防护

**威胁**: 用户输入恶意命令

**防护**:
1. **白名单验证** - 只允许预定义命令
2. **参数清理** - 过滤特殊字符
3. **危险模式检测** - 拒绝危险操作

```python
# 示例：SQL 注入类似的命令注入
恶意输入: "运行 git status; rm -rf /"

解析结果: command = "git status; rm -rf /"

危险模式匹配: r'rm\s+-rf\s+/' → 拒绝
```

---

### 2. 路径遍历防护

**威胁**: 通过 `..` 访问任意文件

**防护**:
```python
def is_safe(self, command: str) -> Tuple[bool, str]:
    # 检查路径遍历
    if '..' in command:
        return False, "Path traversal detected"

    # 检查绝对路径（可选）
    if re.search(r'(?:^|\s)/[a-z]', command):
        return False, "Absolute path not allowed"
```

---

### 3. 输入验证

**威胁**: 超长输入导致 DoS

**防护**:
```python
MAX_REQUEST_LENGTH = 10000  # 10KB

def process(self, request: str):
    if len(request) > MAX_REQUEST_LENGTH:
        raise ValueError(f"Request too long: {len(request)} > {MAX_REQUEST_LENGTH}")
```

---

### 4. API Key 保护

**威胁**: API Key 泄露

**防护**:
- memex-cli 负责管理 API Key
- 不在代码中硬编码
- 使用环境变量或配置文件

---

## 总结

MasterOrchestrator 采用**分层协调架构**，通过以下设计实现高效、安全、可扩展的任务自动化：

**核心设计**:
1. **意图分析** - 自动识别任务类型
2. **执行路由** - 5种模式覆盖所有场景
3. **模块化** - 每个执行器职责单一
4. **数据驱动** - 配置驱动的工作流
5. **安全优先** - 多层安全机制

**技术亮点**:
- 正则表达式驱动的意图识别
- 类型安全的数据结构（dataclass）
- 事件流解析和追踪（run_id）
- 5阶段结构化工作流
- 自动化技能发现

**扩展性**:
- 易于添加新执行模式
- 易于集成新 AI 后端
- 易于扩展工作流阶段
- 易于添加提示词模板

---

## 配置系统

### 环境变量

MasterOrchestrator 支持以下环境变量配置：

| 环境变量 | 说明 | 默认值 | 必需 |
|---------|------|--------|------|
| `CLAUDE_API_KEY` | Claude API密钥 | 无 | 是（使用Claude时） |
| `GEMINI_API_KEY` | Gemini API密钥 | 无 | 否 |
| `CODEX_API_KEY` | Codex API密钥 | 无 | 否 |
| `ADUIB_URL` | Aduib-AI服务地址 | `http://localhost:8000` | 否 |
| `ADUIB_API_KEY` | Aduib-AI API密钥 | 无 | 否（启用缓存时需要） |
| `MEMEX_CLI_PATH` | memex-cli路径 | `memex-cli` | 否 |

**配置示例**：

```bash
# 基本配置
export CLAUDE_API_KEY="sk-ant-xxx"
export GEMINI_API_KEY="AIzxxx"

# Aduib-AI 缓存（可选）
export ADUIB_URL="https://api.aduib.ai"
export ADUIB_API_KEY="your-api-key"

# Memex-CLI（可选）
export MEMEX_CLI_PATH="/usr/local/bin/memex-cli"
```

### 初始化选项

```python
from orchestrator import MasterOrchestrator

# 完整配置示例
orch = MasterOrchestrator(
    # 后端配置
    backend_orch=None,              # 自动创建
    use_claude_intent=True,         # 使用 Claude 意图识别

    # Aduib-AI 配置
    use_remote=True,                # 启用远程缓存
    aduib_url="https://api.aduib.ai",
    aduib_api_key="your-key",
    enable_cache=True,              # 启用缓存查询
    enable_upload=True,             # 启用结果上传

    # 调试配置
    verbose=True                    # 详细日志
)
```

### Skills 配置路径

所有 memex-cli skills 位于：

```
skills/memex-cli/skills/
├── intent-analyzer.yaml      # 意图识别
├── command-parser.yaml        # 命令解析
├── agent-router.yaml          # Agent路由
├── prompt-renderer.yaml       # 提示词渲染
└── dev-workflow.yaml          # 开发工作流
```

---

## 架构演进

### Phase 5 (当前版本)

**完成时间**: 2026-01-04

**核心更新**：
1. **统一执行器基类** (`MemexExecutorBase`)
   - 所有执行器继承统一基类
   - 标准化接口和错误处理

2. **Aduib-AI 远程缓存集成**
   - 缓存查询和结果保存
   - 自动降级机制
   - 性能优化（缓存命中率 50%-80%）

3. **Claude LLM 意图识别**
   - ClaudeIntentAnalyzer 替代规则引擎
   - 语义理解，高准确率
   - 通过 `intent-analyzer.yaml` skill

4. **V2 执行器架构**
   - CommandExecutor V2
   - AgentCaller V2
   - PromptManager V2
   - 三层 Fallback 机制

5. **Memex-CLI Skills 系统**
   - YAML 配置驱动
   - 5个核心 skills
   - 易于扩展

**参考文档**:
- `docs/MEMEX_CLI_INTEGRATION_DESIGN.md` - Memex-CLI 集成设计
- `docs/ADUIB_FEATURES.md` - Aduib-AI 功能详解
- `docs/ADUIB_INTEGRATION.md` - Aduib-AI 集成文档
- `docs/ENVIRONMENT_VARIABLES.md` - 环境变量配置

---

**文档版本**: 2.0.0 (Phase 5)
**最后更新**: 2026-01-04
**架构版本**: V2 (MemexExecutorBase + Aduib-AI + Claude Intent)
**维护者**: Orchestrator Team
