# 资源扫描与主流程整合设计 V2

## 需求澄清

### 核心需求

1. **V2资源扫描全面替换V1**：已完成，默认使用 ResourceScannerV2

2. **执行器携带资源内容作为提示词**：
   - 资源（如 SKILL.md）的内容作为系统提示词
   - 用户需求作为用户输入
   - 执行器包装成完整的任务请求发给后端

3. **意图识别阶段智能推断资源**：
   - 用户无需明确指定资源名称
   - ClaudeIntentAnalyzer 分析需求，推断可能使用的资源
   - 示例：用户说"帮我review代码" → 推断应使用 skill:code-review

4. **Slash Command 元命令**：
   - 命令格式：`/master-orchestrator <用户需求>`
   - 执行时调用 master-orchestrator SKILL

5. **用户需求输入格式**：
   - **非格式化**：自然语言，如 "帮我优化代码性能"
   - **格式化**：带前缀，如 "需求理解：xxx" 或 "/code_fix xxx"

---

## 架构设计

### 整体流程

```
用户输入: "帮我优化这段代码的性能"
    ↓
┌─────────────────────────────────────────┐
│ 1. ClaudeIntentAnalyzer（增强）         │
│    - 分析需求类型                        │
│    - 推断可能的资源                      │
│    - 返回候选资源列表                    │
└─────────────────────────────────────────┘
    ↓
Intent {
    mode: SKILL,
    entity: "code-optimize",           # 主要推断
    candidates: ["performance-tuning"] # 备选
}
    ↓
┌─────────────────────────────────────────┐
│ 2. ExecutionRouter._route_v3()          │
│    - 查找 skill:code-optimize           │
│    - 如果不存在，尝试 candidates         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. ExecutorFactory.create_executor()    │
│    - 读取 SKILL.md 内容                 │
│    - 创建 YAMLSkillExecutor             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. YAMLSkillExecutor.execute()          │
│    - 提取 system_prompt                 │
│    - 提取 user_prompt_template          │
│    - 构建完整提示词                      │
│    - 调用 backend_orch                  │
└─────────────────────────────────────────┘
    ↓
完整提示词 = system_prompt + user_prompt_template.format(request=用户需求)
    ↓
backend_orch.call_backend(prompt) → Claude API
    ↓
返回结果
```

### 资源文件格式（SKILL.md 示例）

```markdown
# code-optimize

description: 代码性能优化助手
enabled: true
priority: 80
backend: claude
tags: [optimization, performance, code-quality]

## System Prompt

你是一位资深的性能优化专家，擅长：
- 识别性能瓶颈
- 提供优化建议
- 代码重构

## User Prompt Template

用户需求：{{request}}

请分析上述代码的性能问题，并提供优化方案。
```

### 关键组件设计

#### 1. Intent 类扩展

```python
@dataclass
class Intent:
    mode: ExecutionMode           # SKILL, COMMAND, AGENT, PROMPT, BACKEND
    task_type: str
    complexity: str
    confidence: float

    # V3 新增字段
    entity: Optional[str] = None              # 主要推断的资源名
    candidates: List[str] = field(default_factory=list)  # 备选资源
    reasoning: Optional[str] = None           # 推断理由（用于调试）
```

#### 2. ClaudeIntentAnalyzer 增强

**新增提示词模板**：

```python
INTENT_ANALYSIS_PROMPT_V3 = """
分析用户需求，推断应使用的资源。

## 用户需求
{request}

## 可用资源
{available_resources}

## 输出格式（JSON）
{{
    "mode": "skill|command|agent|prompt|backend",
    "entity": "resource-name",        # 最匹配的资源名称
    "candidates": ["alt1", "alt2"],   # 备选资源（最多3个）
    "reasoning": "推断理由",
    "task_type": "类型",
    "complexity": "simple|medium|complex",
    "confidence": 0.0-1.0
}}

## 推断规则
1. 根据需求关键词匹配资源的 description 和 tags
2. 优先选择 priority 高的资源
3. 如果没有明确匹配，返回 mode=backend，entity=null
4. candidates 用于兜底（按匹配度降序）

## 示例
需求: "帮我review这段代码"
可用资源: [
    {{"name": "code-review", "description": "代码审查助手", "tags": ["review", "quality"]}},
    {{"name": "code-analyze", "description": "代码分析工具", "tags": ["analyze"]}}
]
推断结果: {{"mode": "skill", "entity": "code-review", "candidates": ["code-analyze"], ...}}
"""
```

**实现方法**：

```python
class ClaudeIntentAnalyzer:
    def __init__(self, backend_orch: BackendOrchestrator, registry: Optional[UnifiedRegistry] = None):
        self.backend_orch = backend_orch
        self.registry = registry  # V3 模式需要

    def analyze(self, request: str) -> Intent:
        """分析用户请求，返回意图（V3 增强版）"""

        # 1. 准备可用资源列表（如果是 V3 模式）
        available_resources = []
        if self.registry:
            resources = self.registry.list_resources(enabled_only=True)
            available_resources = [
                {
                    "name": r.name,
                    "type": r.type.value,
                    "description": r.config.get("description", ""),
                    "tags": r.config.get("tags", []),
                    "priority": r.priority
                }
                for r in resources
            ]

        # 2. 构建分析提示词
        prompt = INTENT_ANALYSIS_PROMPT_V3.format(
            request=request,
            available_resources=json.dumps(available_resources, ensure_ascii=False, indent=2)
        )

        # 3. 调用 Claude 分析
        response = self.backend_orch.call_backend(
            backend="claude",
            request=prompt,
            system_prompt="你是一个智能任务路由器。"
        )

        # 4. 解析 JSON 结果
        result = json.loads(response)

        return Intent(
            mode=ExecutionMode[result["mode"].upper()],
            entity=result.get("entity"),
            candidates=result.get("candidates", []),
            reasoning=result.get("reasoning"),
            task_type=result.get("task_type", "unknown"),
            complexity=result.get("complexity", "medium"),
            confidence=result.get("confidence", 0.5)
        )
```

#### 3. ExecutionRouter 资源查找逻辑

```python
def _route_v3(self, intent: Intent, request: str) -> Any:
    """V3 执行路径（支持候选资源）"""

    # 特殊处理：BACKEND 模式（无需资源）
    if intent.mode == ExecutionMode.BACKEND:
        return self._call_backend_direct(request, intent)

    # 1. 确定资源类型
    resource_type_map = {
        ExecutionMode.SKILL: "skill",
        ExecutionMode.COMMAND: "command",
        ExecutionMode.AGENT: "agent",
        ExecutionMode.PROMPT: "prompt"
    }
    resource_type = resource_type_map.get(intent.mode)

    # 2. 构建候选资源列表（主要 + 备选）
    candidates = []
    if intent.entity:
        candidates.append(intent.entity)
    candidates.extend(intent.candidates or [])

    if not candidates:
        raise ValueError(f"Intent 未提供任何候选资源: {intent}")

    # 3. 按顺序尝试查找资源
    for candidate in candidates:
        namespace = f"{resource_type}:{candidate}"

        if self.registry.exists(namespace):
            logger.info(f"[V3 Router] 匹配资源: {namespace}")

            # 创建执行器
            executor = self.factory.create_executor(namespace)
            if not executor:
                logger.warning(f"执行器创建失败: {namespace}，尝试下一个候选")
                continue

            # 执行
            try:
                return executor.execute(request)
            except Exception as e:
                logger.error(f"执行失败: {namespace}, 错误: {e}")
                # 继续尝试下一个候选
                continue

    # 4. 所有候选都失败
    raise ValueError(
        f"无法找到可用资源\n"
        f"资源类型: {resource_type}\n"
        f"尝试过的候选: {candidates}\n"
        f"推断理由: {intent.reasoning}"
    )
```

#### 4. YAMLSkillExecutor 执行逻辑

```python
class YAMLSkillExecutor(MemexSkillExecutor):
    """YAML Skill 执行器（增强版）"""

    def __init__(self, backend_orch, skill_path: Path, skill_name: str, **config):
        super().__init__(backend_orch, skill_name, config.get('backend', 'claude'))
        self.skill_path = skill_path
        self.skill_config = self._load_skill_config()

    def _load_skill_config(self) -> Dict[str, Any]:
        """加载 SKILL.md 配置"""
        try:
            content = self.skill_path.read_text(encoding='utf-8')

            # 解析 Markdown frontmatter 和内容
            config = {}

            # 提取元数据（前几行的 key: value 格式）
            lines = content.split('\n')
            i = 0

            # 跳过标题
            if lines[i].startswith('#'):
                i += 1

            # 读取元数据
            while i < len(lines) and lines[i].strip():
                line = lines[i].strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    config[key.strip()] = value.strip()
                i += 1

            # 提取章节内容
            sections = self._parse_sections(content)
            config['system_prompt'] = sections.get('System Prompt', '')
            config['user_prompt_template'] = sections.get('User Prompt Template', '{request}')

            return config

        except Exception as e:
            logger.error(f"加载 Skill 配置失败: {self.skill_path}, 错误: {e}")
            return {}

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """解析 Markdown 章节"""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                # 保存上一个章节
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # 开始新章节
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # 保存最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def execute(self, request: str, backend: Optional[str] = None, **params) -> TaskResult:
        """执行 Skill（将资源内容作为提示词）"""

        # 1. 提取提示词模板
        system_prompt = self.skill_config.get('system_prompt', '')
        user_prompt_template = self.skill_config.get('user_prompt_template', '{request}')

        # 2. 处理用户需求格式
        processed_request = self._process_request_format(request)

        # 3. 渲染用户提示词
        user_prompt = user_prompt_template.replace('{{request}}', processed_request)
        user_prompt = user_prompt.replace('{request}', processed_request)

        # 替换其他参数
        for key, value in params.items():
            user_prompt = user_prompt.replace(f'{{{{{key}}}}}', str(value))
            user_prompt = user_prompt.replace(f'{{{key}}}', str(value))

        # 4. 构建完整提示词
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
        else:
            full_prompt = user_prompt

        # 5. 调用后端执行
        backend = backend or self.skill_config.get('backend', self.default_backend)

        logger.info(f"[YAMLSkillExecutor] 执行 Skill: {self.skill_name}")
        logger.debug(f"[YAMLSkillExecutor] 完整提示词长度: {len(full_prompt)} 字符")

        return self.backend_orch.call_backend(
            backend=backend,
            request=full_prompt,
            # system_prompt 已包含在 full_prompt 中
        )

    def _process_request_format(self, request: str) -> str:
        """处理用户需求格式"""

        # 检测格式化输入
        if request.startswith('需求理解：'):
            return request[5:].strip()  # 移除前缀
        elif request.startswith('/'):
            # Slash command 格式：/command-name args
            parts = request[1:].split(maxsplit=1)
            return parts[1] if len(parts) > 1 else parts[0]
        else:
            # 非格式化输入，直接返回
            return request
```

#### 5. Slash Command 元命令

```python
# 在 slash_command_registry.py 中添加

SlashCommandMetadata(
    name="master-orchestrator",
    type=SlashCommandType.SKILL,
    description="调用主流程处理用户需求",
    handler="_execute_master_orchestrator",
    enabled=True,
    priority=100,
    source="builtin",
    examples=[
        "/master-orchestrator 需求理解：帮我优化代码",
        "/master-orchestrator 分析这段代码的性能瓶颈"
    ]
)

# 在 master_orchestrator.py 中添加

def _execute_master_orchestrator(self, args: str, verbose: bool = False) -> Dict[str, Any]:
    """
    执行主流程（通过 Slash Command 调用）

    Args:
        args: 用户需求
        verbose: 详细输出

    Returns:
        执行结果
    """
    try:
        # 查找 master-orchestrator skill
        namespace = "skill:master-orchestrator"

        if not self.registry or not self.registry.exists(namespace):
            return {
                "success": False,
                "error": "master-orchestrator skill 未找到，请确保在 skills/ 目录中创建"
            }

        # 创建执行器
        executor = self.factory.create_executor(namespace)
        if not executor:
            return {
                "success": False,
                "error": "无法创建 master-orchestrator 执行器"
            }

        # 执行
        result = executor.execute(args)

        return {
            "success": True,
            "result": result,
            "skill": "master-orchestrator"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 实现计划

### 阶段一：Intent 类和分析器增强

**目标**：支持资源推断

**变更文件**：
1. `analyzers/claude_intent_analyzer.py`:
   - 添加 `entity` 和 `candidates` 字段到 Intent 类
   - 修改 `analyze()` 方法，添加资源推断逻辑
   - 构造函数接受 `registry` 参数

2. `master_orchestrator.py`:
   - Line 628: 创建 analyzer 时传入 registry
   ```python
   self.analyzer = ClaudeIntentAnalyzer(
       self.backend_orch,
       registry=self.registry if self.auto_discover else None
   )
   ```

**预估工作量**：约 150 行

### 阶段二：ExecutionRouter 候选资源支持

**目标**：支持多候选资源查找

**变更文件**：
1. `master_orchestrator.py`:
   - Line 166-201: 修改 `_route_v3()` 方法
   - 添加候选资源循环查找逻辑
   - 详细的错误报告

**预估工作量**：约 50 行

### 阶段三：YAMLSkillExecutor 提示词包装

**目标**：资源内容作为提示词执行

**变更文件**：
1. `executor_factory.py`:
   - Line 52-121: 增强 `_load_skill_config()` 方法
   - 添加 `_parse_sections()` 方法（解析 Markdown 章节）
   - 修改 `execute()` 方法，实现提示词包装
   - 添加 `_process_request_format()` 方法

**预估工作量**：约 120 行

### 阶段四：Slash Command 元命令

**目标**：实现 /master-orchestrator 命令

**变更文件**：
1. `core/slash_command_registry.py`:
   - 添加 master-orchestrator 命令元数据

2. `master_orchestrator.py`:
   - 添加 `_execute_master_orchestrator()` 方法

3. `skills/master-orchestrator/SKILL.md`:
   - 创建 master-orchestrator skill（新文件）

**预估工作量**：约 80 行 + 1 个 SKILL.md

### 阶段五：测试验证

**测试场景**：

1. **资源推断测试**：
   ```python
   orchestrator = MasterOrchestrator(auto_discover=True)
   result = orchestrator.process("帮我review这段代码")
   # 预期：自动推断使用 skill:code-review
   ```

2. **候选资源测试**：
   ```python
   # Intent 返回 entity="not-exist", candidates=["code-review"]
   # 预期：第一个不存在，尝试 code-review 成功
   ```

3. **格式化输入测试**：
   ```python
   orchestrator.process("需求理解：优化性能")
   # 预期：移除前缀，传递 "优化性能" 给 skill
   ```

4. **Slash Command 测试**：
   ```python
   orchestrator.process("/master-orchestrator 分析代码")
   # 预期：调用 master-orchestrator skill
   ```

---

## 文件结构示例

### skills/code-review/SKILL.md

```markdown
# code-review

description: 代码审查助手
enabled: true
priority: 80
backend: claude
tags: [review, quality, code-analysis]

## System Prompt

你是一位资深的代码审查专家，擅长：
- 发现代码中的潜在bug
- 评估代码质量和可维护性
- 提供改进建议
- 检查代码规范

审查时请关注：
1. 代码逻辑正确性
2. 性能问题
3. 安全漏洞
4. 可读性和可维护性

## User Prompt Template

请审查以下代码：

{{request}}

请提供详细的审查报告，包括：
- 发现的问题
- 严重程度评级
- 改进建议
```

### skills/master-orchestrator/SKILL.md

```markdown
# master-orchestrator

description: 主流程协调器，智能分析需求并调度资源
enabled: true
priority: 100
backend: claude
tags: [orchestration, workflow, meta]

## System Prompt

你是 MasterOrchestrator 的核心协调引擎，负责：
1. 理解用户的复杂需求
2. 分解任务步骤
3. 选择合适的资源（skills/commands/agents）
4. 协调执行流程

## User Prompt Template

用户需求：{{request}}

请分析这个需求，制定执行计划：
1. 需求分解
2. 所需资源
3. 执行步骤
4. 预期结果

然后按计划执行。
```

---

## 关键设计决策

### 1. 为什么用 SKILL.md 而不是 SKILL.yaml？

✅ **Markdown 优势**：
- 更适合编写长文本提示词
- 支持 Markdown 格式化（代码块、列表等）
- 人类可读性强
- V2 Scanner 默认格式

### 2. 为什么需要候选资源机制？

✅ **容错性**：
- LLM 推断可能不准确
- 允许多个备选方案
- 按优先级尝试，提高成功率

### 3. 为什么要解析用户需求格式？

✅ **灵活性**：
- 支持自然语言（非格式化）
- 支持结构化输入（格式化）
- 兼容 Slash Command 语法

### 4. System Prompt 为什么放在 SKILL.md 而不是代码中？

✅ **可配置性**：
- 用户可以自定义提示词
- 无需修改代码
- 便于迭代优化

---

## 总结

### 核心创新点

1. ✅ **智能资源推断**：用户无需明确指定资源名称
2. ✅ **提示词包装执行**：资源内容作为提示词，结合用户需求发给 LLM
3. ✅ **候选资源机制**：提高匹配成功率
4. ✅ **格式化输入支持**：兼容多种输入方式
5. ✅ **元命令支持**：/master-orchestrator 调用主流程

### 工作量估算

| 阶段 | 内容 | 代码量 |
|------|------|--------|
| 阶段一 | Intent 增强 | 150 行 |
| 阶段二 | 候选资源支持 | 50 行 |
| 阶段三 | 提示词包装 | 120 行 |
| 阶段四 | Slash Command | 80 行 |
| 阶段五 | 测试 | 150 行 |
| **总计** | | **550 行** |

### 预期效果

用户体验：
```bash
# 1. 创建 code-review skill
$ cat > skills/code-review/SKILL.md

# 2. 启动 V3 模式
orchestrator = MasterOrchestrator(auto_discover=True)

# 3. 自然语言调用（自动推断资源）
orchestrator.process("帮我review这段代码：\ndef foo(): pass")
  ↓
ClaudeIntentAnalyzer 推断 → entity="code-review"
  ↓
ExecutionRouter 查找 → skill:code-review
  ↓
YAMLSkillExecutor 包装 → system_prompt + user_prompt
  ↓
Backend 执行 → 返回审查报告 ✅
```

**零配置，智能推断，自动执行！**
