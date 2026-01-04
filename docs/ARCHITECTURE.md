# MasterOrchestrator 系统架构

本文档详细描述 MasterOrchestrator 的系统架构、设计决策和技术实现。

## 目录

- [系统概览](#系统概览)
- [核心架构](#核心架构)
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
│  │          IntentAnalyzer (意图分析层)              │   │
│  │  - 模式识别 (ExecutionMode)                       │   │
│  │  - 任务分类 (TaskType)                            │   │
│  │  - 复杂度评估 (Complexity)                        │   │
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
│  Executor   │  │ Caller │  │ Manager │  │ Workflow │  │ Orch.  │
└─────┬───────┘  └────┬───┘  └────┬────┘  └─────┬────┘  └───┬────┘
      │               │           │              │           │
┌─────▼───────────────▼───────────▼──────────────▼───────────▼────┐
│              BackendOrchestrator (后端协调层)                    │
│  - memex-cli 集成                                                │
│  - 事件流解析                                                    │
│  - 多后端管理 (Claude, Gemini, Codex)                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 模块详解

### 1. MasterOrchestrator (总协调器)

**文件**: `master_orchestrator.py` (600+ 行)

**职责**：
- 系统入口点
- 初始化所有子模块
- 协调 IntentAnalyzer 和 ExecutionRouter
- 处理结果类型转换

**关键接口**：

```python
class MasterOrchestrator:
    def __init__(self, parse_events: bool = True, timeout: int = 600):
        """
        初始化总协调器

        Args:
            parse_events: 是否解析事件流（影响性能）
            timeout: 默认超时时间（秒）
        """
        self.backend_orch = BackendOrchestrator(parse_events, timeout)
        self.analyzer = IntentAnalyzer()
        self.router = ExecutionRouter(self.backend_orch)

    def process(self, request: str, verbose: bool = False) -> Any:
        """
        处理用户请求

        Returns:
            WorkflowResult | TaskResult | CommandResult | AgentResult
        """
        # 1. 意图分析
        intent = self.analyzer.analyze(request)

        # 2. 执行路由
        result = self.router.route(request, intent)

        return result
```

**设计亮点**：
- 使用依赖注入传递 BackendOrchestrator
- 返回类型多态（根据执行模式返回不同结果类型）
- 集中化错误处理

---

### 2. IntentAnalyzer (意图分析器)

**文件**: `master_orchestrator.py` (IntentAnalyzer 类)

**职责**：
- 分析用户请求的意图
- 识别执行模式（command, agent, prompt, skill, backend）
- 提取任务类型（dev, ux, analysis, test）
- 评估复杂度（simple, medium, complex）

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

### 4. CommandExecutor (命令执行器)

**文件**: `commands/command_executor.py` (200 行)

**职责**：
- 解析自然语言到 Shell 命令
- 安全检查（白名单 + 危险模式检测）
- 执行命令并捕获输出

**架构**：

```
用户请求: "运行 git status"
  ↓
parse_command()
  ├─ 提取命令名: "git"
  ├─ 提取参数: ["status"]
  └─ 构建命令: "git status"
  ↓
is_safe()
  ├─ 白名单检查: git ∈ ALLOWED_COMMANDS ✓
  ├─ 危险模式检查: 无匹配 ✓
  └─ 返回 True
  ↓
execute_shell()
  ├─ subprocess.run(["git", "status"])
  ├─ 捕获 stdout, stderr, return_code
  └─ 返回 CommandResult
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

**文档版本**: 1.0.0
**最后更新**: 2026-01-04
