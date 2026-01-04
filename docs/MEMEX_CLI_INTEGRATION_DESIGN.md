# Memex-CLI深度集成方案

## 一、需求分析

### 当前架构问题
1. **意图识别**：使用硬编码正则规则（IntentAnalyzer），缺乏语义理解
2. **命令解析**：CommandExecutor使用模式匹配，无法处理复杂自然语言
3. **执行分散**：仅Backend模式使用memex-cli，其他执行器各自独立

### 改造目标
1. 使用**Claude LLM**进行智能意图识别（via memex-cli）
2. **Command/Agent/Prompt/Skill**底层统一使用memex-cli
3. 保持现有API接口不变

---

## 二、架构设计

### 2.1 整体架构

```
用户请求
    ↓
[Claude意图识别] ← memex-cli skill: intent-analyzer
    ↓
Intent { mode, task_type, complexity, backend, skill }
    ↓
ExecutionRouter
    ↓
┌────────────────────────────────────────┐
│  统一执行层 (MemexExecutorBase)        │
│  - 所有执行器继承此基类                │
│  - 统一使用 memex-cli 调用              │
└────────────────────────────────────────┘
    ↓
┌──────────┬──────────┬──────────┬──────────┐
│ Command  │  Agent   │ Prompt   │  Skill   │
│ Executor │  Caller  │ Manager  │ Executor │
└──────────┴──────────┴──────────┴──────────┘
    ↓
memex-cli skills:
  - command-executor
  - agent-caller
  - prompt-renderer
  - workflow-agent
```

### 2.2 核心组件改造

#### A. Claude意图识别器（新增）

**文件**：`orchestrator/analyzers/claude_intent_analyzer.py`

```python
class ClaudeIntentAnalyzer:
    """使用Claude LLM进行意图识别"""

    def __init__(self, backend_orch: BackendOrchestrator):
        self.backend_orch = backend_orch
        self.intent_prompt_template = self._load_intent_prompt()

    def analyze(self, request: str) -> Intent:
        """
        通过memex-cli调用Claude分析意图

        流程：
        1. 构造意图分析提示词
        2. 调用 memex-cli run --backend claude --skill intent-analyzer
        3. 解析JSON返回
        4. 构造Intent对象
        """
        prompt = self._build_intent_prompt(request)

        # 使用memex-cli skill调用
        result = self.backend_orch.run_task(
            backend="claude",
            prompt=prompt,
            stream_format="jsonl"
        )

        # 解析JSON输出
        intent_data = self._parse_intent_result(result.output)

        return Intent(
            mode=ExecutionMode(intent_data["mode"]),
            task_type=intent_data["task_type"],
            complexity=intent_data["complexity"],
            backend_hint=intent_data.get("backend_hint"),
            skill_hint=intent_data.get("skill_hint"),
            confidence=intent_data.get("confidence", 0.9)
        )

    def _build_intent_prompt(self, request: str) -> str:
        """构造意图分析提示词"""
        return f"""你是一个AI任务意图分析专家。分析用户请求，返回JSON格式的意图分类。

执行模式 (mode)：
- command: 简单命令执行（git, npm, docker等）
- agent: 需要智能体推理（探索代码、规划实现）
- prompt: 使用模板处理（代码审查、文档生成）
- skill: 复杂技能流程（多阶段开发、UX设计）
- backend: 直接LLM调用（分析、解释、回答）

任务类型 (task_type): dev, ux, analysis, test, general
复杂度 (complexity): simple, medium, complex
后端提示 (backend_hint): claude, gemini, codex, null
技能提示 (skill_hint): 技能名称或null

用户请求：
{request}

返回JSON（仅JSON，无其他文本）：
{{
  "mode": "...",
  "task_type": "...",
  "complexity": "...",
  "backend_hint": "..." or null,
  "skill_hint": "..." or null,
  "confidence": 0.0-1.0,
  "reasoning": "简短解释"
}}"""
```

**memex-cli skill定义**：
```yaml
# skills/memex-cli/skills/intent-analyzer.yaml
name: intent-analyzer
description: AI任务意图分类分析
backend: claude
model: claude-3-5-sonnet-20241022
output_format: json
system_prompt: |
  你是意图分析专家，必须返回严格的JSON格式。
  分析用户请求，分类为5种执行模式之一。
```

---

#### B. 统一执行基类（新增）

**文件**：`orchestrator/executors/memex_executor_base.py`

```python
class MemexExecutorBase:
    """
    统一执行器基类
    所有执行器通过memex-cli skill调用
    """

    def __init__(self, backend_orch: BackendOrchestrator):
        self.backend_orch = backend_orch

    def execute_via_skill(
        self,
        skill_name: str,
        request: str,
        backend: str = "claude",
        **kwargs
    ) -> TaskResult:
        """
        通过memex-cli skill执行任务

        Args:
            skill_name: memex-cli skill名称
            request: 用户请求
            backend: 后端选择
            **kwargs: 额外参数传递给skill

        Returns:
            TaskResult
        """
        # 构造skill调用命令
        skill_params = self._build_skill_params(request, **kwargs)

        # 调用memex-cli
        return self.backend_orch.run_task(
            backend=backend,
            prompt=skill_params,
            stream_format="jsonl"
        )

    def _build_skill_params(self, request: str, **kwargs) -> str:
        """子类重写以定制skill参数"""
        return request
```

---

#### C. Command执行器改造

**改造前**：硬编码模式匹配
**改造后**：使用memex-cli skill

```python
class CommandExecutor(MemexExecutorBase):
    """命令执行器 - 基于memex-cli skill"""

    def execute(self, request: str) -> CommandResult:
        """
        通过 memex-cli skill: command-parser 解析和执行

        流程：
        1. 调用 command-parser skill（自然语言→命令）
        2. 验证命令安全性
        3. 执行命令
        4. 返回结果
        """
        # 调用skill解析命令
        parse_result = self.execute_via_skill(
            skill_name="command-parser",
            request=request,
            backend="claude"
        )

        # 提取命令
        command = self._extract_command(parse_result.output)

        # 安全验证
        if not self._is_safe_command(command):
            return CommandResult(
                command=command,
                output="",
                success=False,
                return_code=-1,
                error="Command not allowed by safety policy"
            )

        # 执行
        return self._execute_command(command)
```

**memex-cli skill**：
```yaml
# skills/memex-cli/skills/command-parser.yaml
name: command-parser
description: 将自然语言转换为shell命令
backend: claude
output_format: json
system_prompt: |
  将用户的自然语言请求转换为对应的shell命令。
  返回JSON: {"command": "git status", "safe": true, "explanation": "..."}
```

---

#### D. Agent调用器改造

```python
class AgentCaller(MemexExecutorBase):
    """Agent调用器 - 基于memex-cli skill"""

    def call_agent(self, agent_request: AgentRequest) -> AgentResult:
        """
        通过 memex-cli skill: agent-router 调用

        支持的agent类型：
        - explore: 代码探索
        - plan: 实现规划
        - general: 通用任务
        """
        # 调用agent-router skill
        result = self.execute_via_skill(
            skill_name="agent-router",
            request=agent_request.prompt,
            backend="claude",
            agent_type=agent_request.agent_type.value,
            thoroughness=agent_request.thoroughness
        )

        return AgentResult(
            agent_type=agent_request.agent_type,
            output=result.output,
            success=result.success,
            error=result.error
        )
```

---

#### E. Prompt管理器改造

```python
class PromptManager(MemexExecutorBase):
    """提示词管理器 - 基于memex-cli skill"""

    def render_and_execute(
        self,
        template_name: str,
        backend: str,
        **variables
    ) -> TaskResult:
        """
        通过 memex-cli skill: prompt-renderer 渲染和执行

        流程：
        1. 调用 prompt-renderer skill渲染模板
        2. 使用渲染结果调用后端
        """
        result = self.execute_via_skill(
            skill_name="prompt-renderer",
            request=template_name,
            backend=backend,
            template_vars=variables
        )

        return result
```

---

#### F. Skill执行器改造

```python
class SkillExecutor(MemexExecutorBase):
    """技能执行器 - 直接调用memex-cli skills"""

    def execute_skill(
        self,
        skill_name: str,
        request: str,
        backend: str = "codex"
    ) -> Any:
        """
        直接执行memex-cli skill

        支持的skills：
        - dev-workflow: 5阶段开发流程
        - ux-design: UX设计流程
        - code-implementation: 代码实现
        """
        return self.execute_via_skill(
            skill_name=skill_name,
            request=request,
            backend=backend
        )
```

---

## 三、Memex-CLI Skills定义

### 3.1 技能清单

在 `skills/memex-cli/skills/` 目录下创建：

```
skills/memex-cli/skills/
├── intent-analyzer.yaml       # 意图识别
├── command-parser.yaml         # 命令解析
├── agent-router.yaml           # Agent路由
├── prompt-renderer.yaml        # 提示词渲染
├── dev-workflow.yaml           # 开发工作流
├── ux-design.yaml              # UX设计
└── code-implementation.yaml    # 代码实现
```

### 3.2 示例：intent-analyzer.yaml

```yaml
name: intent-analyzer
version: 1.0.0
description: 分析用户请求意图，分类执行模式

backend: claude
model: claude-3-5-sonnet-20241022
temperature: 0.3
max_tokens: 500

output_format: json

system_prompt: |
  你是AI任务意图分析专家。分析用户请求，严格返回JSON格式。

  执行模式：
  - command: 命令执行 (git, npm, docker等)
  - agent: 智能体任务（探索、规划）
  - prompt: 模板处理（代码审查、文档）
  - skill: 复杂流程（多阶段开发）
  - backend: 直接回答（分析、解释）

  任务类型：dev, ux, analysis, test, general
  复杂度：simple, medium, complex

  返回格式：
  {
    "mode": "command|agent|prompt|skill|backend",
    "task_type": "dev|ux|analysis|test|general",
    "complexity": "simple|medium|complex",
    "backend_hint": "claude|gemini|codex|null",
    "skill_hint": "skill-name|null",
    "confidence": 0.0-1.0,
    "reasoning": "分析原因"
  }

user_prompt_template: |
  用户请求：{{request}}

  分析意图并返回JSON：

examples:
  - input: "运行git status查看状态"
    output: '{"mode":"command","task_type":"general","complexity":"simple","backend_hint":null,"skill_hint":null,"confidence":0.95,"reasoning":"明确的git命令"}'

  - input: "开发一个电商管理系统"
    output: '{"mode":"skill","task_type":"dev","complexity":"complex","backend_hint":"codex","skill_hint":"dev-workflow","confidence":0.9,"reasoning":"复杂系统开发需要多阶段流程"}'

  - input: "分析这个函数的性能瓶颈"
    output: '{"mode":"backend","task_type":"analysis","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.85,"reasoning":"代码分析任务"}'
```

### 3.3 示例：command-parser.yaml

```yaml
name: command-parser
version: 1.0.0
description: 将自然语言转换为shell命令

backend: claude
model: claude-3-5-sonnet-20241022
temperature: 0.1
max_tokens: 200

output_format: json

system_prompt: |
  将用户的自然语言转换为精确的shell命令。

  支持的命令类型：
  - git: status, log, diff, add, commit, push
  - npm: install, test, run, build
  - python: 执行脚本、pytest
  - docker: ps, logs, exec

  返回JSON格式：
  {
    "command": "具体命令",
    "safe": true/false,
    "category": "git|npm|python|docker|other",
    "explanation": "命令说明"
  }

  安全规则：
  - 拒绝危险命令（rm -rf, dd, mkfs等）
  - 拒绝修改系统文件
  - 仅允许开发常用命令

user_prompt_template: |
  将以下请求转换为shell命令：
  {{request}}

examples:
  - input: "查看git状态"
    output: '{"command":"git status","safe":true,"category":"git","explanation":"显示工作区状态"}'

  - input: "安装npm依赖"
    output: '{"command":"npm install","safe":true,"category":"npm","explanation":"安装package.json中的依赖"}'
```

---

## 四、实施步骤

### Phase 1: 意图识别迁移（1-2天）
1. 创建 `ClaudeIntentAnalyzer`
2. 定义 `intent-analyzer.yaml` skill
3. 在 `MasterOrchestrator` 中添加开关：
   ```python
   use_claude_intent: bool = True  # 默认启用Claude意图识别
   ```
4. 保留 `IntentAnalyzer` 作为fallback
5. A/B测试验证准确率

### Phase 2: Command执行器迁移（2-3天）
1. 创建 `MemexExecutorBase` 基类
2. 定义 `command-parser.yaml` skill
3. 重构 `CommandExecutor` 继承基类
4. 测试常用命令场景
5. 性能对比（旧vs新）

### Phase 3: Agent/Prompt迁移（2-3天）
1. 定义 `agent-router.yaml` skill
2. 定义 `prompt-renderer.yaml` skill
3. 重构 `AgentCaller` 和 `PromptManager`
4. 迁移现有模板到memex-cli skills

### Phase 4: Skill统一（1-2天）
1. 将 `dev-workflow`, `ux-design` 定义为memex-cli skills
2. 重构 `SkillExecutor`
3. 注册所有skills到 `skills/memex-cli/skills/`

### Phase 5: 集成测试（2天）
1. 端到端测试所有执行模式
2. 性能benchmark
3. 错误处理和降级
4. 文档更新

---

## 五、技术收益

### 5.1 智能化提升
- **意图识别准确率**：从规则匹配60-70% → Claude理解90%+
- **命令解析灵活性**：支持任意自然语言表达
- **上下文理解**：Claude可以理解复杂需求

### 5.2 架构优势
- **统一底层**：所有执行器基于memex-cli，易维护
- **可扩展性**：新增执行模式只需定义skill
- **技能复用**：memex-cli skills可独立使用

### 5.3 性能考虑
- **延迟**：意图识别增加1-2s LLM调用（可接受）
- **成本**：每次请求额外1次Claude调用（约0.001$）
- **缓存**：相似请求可缓存意图结果

---

## 六、风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| Claude意图识别错误 | 保留规则引擎作为fallback，confidence阈值过滤 |
| memex-cli依赖失败 | 本地降级到直接执行，错误重试机制 |
| 性能下降 | 意图缓存、并行调用、超时控制 |
| 成本增加 | 使用较小模型（haiku）、批量处理、缓存优化 |

---

## 七、配置示例

### 7.1 MasterOrchestrator配置

```python
orch = MasterOrchestrator(
    # 意图识别配置
    use_claude_intent=True,          # 使用Claude意图识别
    intent_confidence_threshold=0.7,  # 置信度阈值
    fallback_to_rules=True,          # 低置信度回退规则

    # Memex-CLI配置
    memex_skills_dir="./skills/memex-cli/skills",
    unified_executor=True,           # 统一执行器

    # 性能配置
    intent_cache_size=1000,          # 意图缓存大小
    executor_timeout=60,             # 执行超时
)
```

### 7.2 环境变量

```bash
# Memex-CLI配置
export MEMEX_SKILLS_PATH="./skills/memex-cli/skills"
export MEMEX_DEFAULT_BACKEND="claude"

# Claude配置
export ANTHROPIC_API_KEY="your-key"

# 功能开关
export USE_CLAUDE_INTENT=true
export UNIFIED_EXECUTOR=true
```

---

## 八、总结

本方案通过**Claude LLM意图识别**和**memex-cli统一执行层**，将orchestrator升级为真正的智能任务编排系统。核心改进：

1. ✅ **智能意图识别**：规则引擎 → Claude语义理解
2. ✅ **统一执行底层**：分散实现 → memex-cli skills
3. ✅ **可扩展架构**：硬编码 → YAML配置驱动
4. ✅ **向后兼容**：保留现有API，渐进式迁移

预计**2周完成全部迁移**，系统智能化和可维护性显著提升。
