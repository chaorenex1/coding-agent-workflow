# Master Orchestrator 开发计划总汇

## 项目概述

### 核心需求

基于用户明确的 5 点需求规范：

1. ✅ **单路径架构**：V2 资源扫描全面替换 V1，无双路径降级
2. ✅ **资源内容作为提示词**：执行器携带资源内容（SKILL.md），包装成任务请求执行
3. ⏳ **意图分析推断资源**：在意图识别阶段分析用户需求，推断可能要使用的资源
4. ✅ **元命令**：构建 `/master-orchestrator <用户需求>` slash command
5. ✅ **输入格式规则**：
   - 非格式化：`"帮我优化代码性能"`
   - 格式化："需求理解：xxx" 或 "/code_fix xxx"

### 架构设计原则

- **资源格式**：Markdown (SKILL.md)，非 YAML
- **解析基类**：可扩展的 ResourceContentParser 设计
- **提示词包装**：System Prompt + User Prompt Template 组合
- **单一职责**：解析器、执行器、处理器各司其职

---

## 五阶段实施计划

```
Phase 3 (已完成) → Phase 4 (已完成) → Phase 1 (待实施) → Phase 2 (待实施) → Phase 5 (待实施)
      ↓                    ↓                  ↓                  ↓                  ↓
  资源内容解析        Slash Command      意图分析增强      执行路由增强        端到端测试
```

---

## Phase 3: 资源内容解析与提示词包装 ✅

### 实施状态

**完成度**: 100% | **测试通过率**: 10/10 (100%) | **代码行数**: ~1,090 行

### 实施目标

1. 创建 ResourceContentParser 抽象基类，支持多格式扩展
2. 实现 MarkdownResourceParser，解析 SKILL.md 格式
3. 重构 MarkdownSkillExecutor（原 YAMLSkillExecutor），支持提示词包装
4. 实现三种输入格式处理（非格式化、"需求理解："、"/command"）
5. 完整测试覆盖

### 核心成果

#### 1. ResourceContentParser 架构

**文件**: `core/resource_content_parser.py` (320 行)

**设计模式**: Strategy Pattern（策略模式）

**核心类**:

```python
# 抽象基类
class ResourceContentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedResourceContent

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool

# 数据类
@dataclass
class ParsedResourceContent:
    metadata: Dict[str, Any]        # 元数据
    sections: Dict[str, str]        # 章节内容
    raw_content: str                # 原始内容
    file_path: Optional[Path]

    # 辅助方法
    def get_metadata(key, default)
    def get_section(section_name, default)
    def has_section(section_name)
    def list_sections()

# Markdown 解析器实现
class MarkdownResourceParser(ResourceContentParser):
    def _parse_metadata(content) -> Dict[str, Any]      # 支持 YAML Frontmatter + 键值对
    def _parse_sections(content) -> Dict[str, str]      # 解析 ## 章节
    def _parse_value(value) -> Any                       # 智能类型转换
```

**支持格式**:

1. **YAML Front Matter**:
```markdown
---
name: skill-name
description: Description
enabled: true
---
## System Prompt
...
```

2. **键值对元数据** (推荐):
```markdown
# skill-name

description: Description
enabled: true
priority: 80
tags: [tag1, tag2]

## System Prompt
...
```

**智能类型转换**:
- `true/false` → `bool`
- `123` → `int`
- `[item1, item2]` → `list`
- `"text"` → `str`

#### 2. MarkdownSkillExecutor 重构

**文件**: `core/executor_factory.py` (+200 行修改)

**核心功能**:

```python
class MarkdownSkillExecutor(MemexSkillExecutor):
    def __init__(backend_orch, skill_path, skill_name, **config):
        # 自动处理目录/文件路径
        if skill_path.is_dir():
            self.skill_file = skill_path / "SKILL.md"

        # 解析资源内容
        self.parsed_content = self._parse_skill_content()

    def _parse_skill_content() -> ParsedResourceContent:
        """使用 MarkdownResourceParser 解析 SKILL.md"""
        parser = MarkdownResourceParser()
        return parser.parse(self.skill_file)

    def _process_request_format(request: str) -> str:
        """处理三种输入格式"""
        # 1. "需求理解：xxx" → "xxx"
        if request.startswith('需求理解：'):
            return request[5:].strip()

        # 2. "/command args" → "args"
        if request.startswith('/'):
            parts = request[1:].split(maxsplit=1)
            return parts[1].strip() if len(parts) > 1 else ""

        # 3. 非格式化 → 原样返回
        return request

    def _build_prompt(request: str, **params) -> str:
        """构建完整提示词"""
        # 1. 获取 System Prompt
        system_prompt = self.parsed_content.get_section('System Prompt', '')

        # 2. 获取 User Prompt Template
        user_prompt_template = self.parsed_content.get_section(
            'User Prompt Template',
            '{request}'  # 默认模板
        )

        # 3. 变量替换（支持 {{var}} 和 {var}）
        user_prompt = self._render_template(
            user_prompt_template,
            request=request,
            **params
        )

        # 4. 组合提示词
        if system_prompt:
            return f"{system_prompt}\n\n{user_prompt}"
        return user_prompt

    def _render_template(template: str, **variables) -> str:
        """模板变量替换"""
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f'{{{{{key}}}}}', str(value))  # {{var}}
            rendered = rendered.replace(f'{{{key}}}', str(value))      # {var}
        return rendered

    def execute(request: str, backend: Optional[str] = None, **skill_params):
        """执行 Skill"""
        # 1. 处理请求格式
        processed_request = self._process_request_format(request)

        # 2. 构建提示词
        full_prompt = self._build_prompt(processed_request, **skill_params)

        # 3. 确定后端（优先级：参数 > 元数据 > 默认）
        backend = backend or self.parsed_content.get_metadata('backend', 'claude')

        # 4. 执行
        return self.execute_via_memex(prompt=full_prompt, backend=backend)
```

**向后兼容**:
```python
YAMLSkillExecutor = MarkdownSkillExecutor  # 别名
```

#### 3. 测试覆盖

**测试文件**:
- `tests/test_resource_content_parser.py` (210 行) - 5 个单元测试
- `tests/test_markdown_skill_executor.py` (290 行) - 5 个集成测试

**测试矩阵**:

| 测试类型 | 测试名称 | 覆盖内容 | 状态 |
|---------|---------|---------|------|
| **解析器单元测试** | | | |
| 1 | `test_markdown_parser_basic` | 基础元数据 + 章节解析 | ✅ |
| 2 | `test_markdown_parser_yaml_frontmatter` | YAML Front Matter 解析 | ✅ |
| 3 | `test_markdown_parser_value_types` | 值类型转换（bool/int/list） | ✅ |
| 4 | `test_markdown_parser_multiple_sections` | 多章节解析 | ✅ |
| 5 | `test_get_parser_factory` | 解析器工厂函数 | ✅ |
| **执行器集成测试** | | | |
| 6 | `test_markdown_skill_basic` | 基础执行 + 提示词包装 | ✅ |
| 7 | `test_request_format_processing` | 三种格式输入处理 | ✅ |
| 8 | `test_template_variable_replacement` | 模板变量替换 | ✅ |
| 9 | `test_backend_selection` | 后端选择逻辑 | ✅ |
| 10 | `test_path_handling` | 路径处理（目录/文件） | ✅ |

**测试结果**:
```bash
$ python tests/test_resource_content_parser.py
测试完成: 5 通过, 0 失败 ✅

$ python tests/test_markdown_skill_executor.py
测试完成: 5 通过, 0 失败 ✅
```

### 文件清单

| 文件 | 类型 | 行数 | 说明 |
|------|------|------|------|
| `core/resource_content_parser.py` | 新增 | 320 | 解析器基类 + Markdown 实现 |
| `core/executor_factory.py` | 修改 | +200 | 重写 MarkdownSkillExecutor |
| `core/__init__.py` | 修改 | +10 | 导出新类 |
| `tests/test_resource_content_parser.py` | 新增 | 210 | 解析器单元测试 |
| `tests/test_markdown_skill_executor.py` | 新增 | 290 | 执行器集成测试 |
| `examples/skill-example.md` | 新增 | 60 | SKILL.md 示例 |
| `docs/RESOURCE_CONTENT_PARSER_IMPLEMENTATION.md` | 新增 | 456 | 实施总结 |

**总计**: ~1,546 行（含文档）

### 技术亮点

1. **单一职责原则**: 解析器 vs 执行器职责清晰
2. **开闭原则**: 通过继承 ResourceContentParser 支持新格式（JSON, TOML）
3. **依赖倒置**: 执行器依赖 ParsedResourceContent 抽象，不依赖具体解析器
4. **容错设计**: 解析失败不崩溃，提供默认值
5. **性能优化**: 解析结果缓存，多次执行无需重复解析

### 关键决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 资源格式 | Markdown (SKILL.md) | 用户明确要求，非 YAML |
| 元数据格式 | 键值对 + YAML Frontmatter | 灵活支持两种常见格式 |
| 章节标识 | `## Section Name` | Markdown 标准语法 |
| 变量语法 | `{{var}}` + `{var}` | 兼容常见模板引擎 |
| 执行器命名 | MarkdownSkillExecutor | 明确标识格式，保留 YAMLSkillExecutor 别名向后兼容 |

---

## Phase 4: /master-orchestrator Slash Command ✅

### 实施状态

**完成度**: 100% | **测试通过率**: 6/6 (100%) | **代码行数**: ~536 行

### 实施目标

1. 创建 master-orchestrator 元技能（SKILL.md）
2. 注册 `/master-orchestrator` Slash Command
3. 利用现有 SkillCommandHandler 实现命令处理
4. 完整端到端测试

### 核心成果

#### 1. master-orchestrator 元技能

**文件**: `skills/master-orchestrator/SKILL.md` (102 行)

**定位**: 主编排器元技能 - 任务分析 + 资源推荐

**System Prompt 设计**:

```markdown
你是 Master Orchestrator，一个智能任务编排系统的核心协调器。

职责：
1. 需求理解与分析
2. 资源发现与匹配
3. 执行策略规划
4. 资源推断（按类型匹配）
5. 输出规范
6. 工作原则（精准匹配优先、降级策略、组合策略、透明性、容错性）
```

**资源匹配规则库**:

| 资源类型 | 匹配模式 |
|---------|---------|
| **Skills** | 代码相关 → `code-review`, `code-refactor`, `code-fix` |
|  | 项目分析 → `project-analyzer`, `dependency-checker` |
|  | 文档生成 → `doc-generator`, `api-doc-writer` |
|  | 测试相关 → `test-generator`, `test-runner` |
|  | 开发工作流 → `dev-workflow` |
| **Agents** | GitHub 操作 → `github-agent` |
|  | 文件操作 → `file-agent` |
|  | 构建部署 → `ci-agent` |
| **Commands** | 系统命令 → `/reset`, `/status`, `/list` |
|  | 快速操作 → `/search`, `/run`, `/execute` |
| **Prompts** | 模板化任务 → 预定义提示词 |
|  | 格式化输出 → 结构化提示词 |

**User Prompt Template**:

```markdown
用户需求：
```
{{request}}
```

请分析此需求并执行以下步骤：
1. 意图识别
2. 资源推断（列出资源 + 匹配度）
3. 执行计划（单资源/多资源/需要澄清）
4. 输出格式（结构化 Markdown）
```

**输出规范**:

```markdown
## 需求分析
[简要说明]

## 推荐资源
1. **主要资源**: resource_type:resource_name
   - 匹配度: XX%
   - 理由: ...

2. **备选资源**: resource_type:resource_name
   - 匹配度: XX%
   - 理由: ...

## 执行建议
[具体执行方式和步骤]
```

#### 2. Slash Command 注册

**文件**: `core/slash_command_registry.py:339-353` (+14 行)

```python
SlashCommandMetadata(
    name="master-orchestrator",
    type=SlashCommandType.SKILL,
    description="Master orchestrator meta-skill - analyzes user needs and intelligently routes to available resources",
    skill="master-orchestrator",
    enabled=True,
    priority=100,
    source="builtin",
    examples=[
        "/master-orchestrator 帮我审查代码质量",
        "/master-orchestrator 分析项目依赖关系",
        "/master-orchestrator 生成 API 文档"
    ]
)
```

#### 3. 执行流程

```
用户: /master-orchestrator 帮我审查代码质量
    ↓
SlashCommandRegistry.execute("master-orchestrator", ["帮我审查代码质量"])
    ↓
获取命令元数据 (type=SKILL, skill="master-orchestrator")
    ↓
SkillCommandHandler.execute()
    ↓
ExecutorFactory.create_executor("skill:master-orchestrator")
    ↓
UnifiedRegistry.get("skill:master-orchestrator") → ResourceMetadata
    ↓
创建 MarkdownSkillExecutor(skill_path=.../master-orchestrator)
    ↓
MarkdownResourceParser.parse(SKILL.md)
    ↓
ParsedResourceContent(metadata={...}, sections={'System Prompt': ..., 'User Prompt Template': ...})
    ↓
_process_request_format("帮我审查代码质量") → "帮我审查代码质量"
    ↓
_build_prompt(request="帮我审查代码质量")
    ↓
full_prompt = System Prompt + "\n\n" + (User Prompt Template 替换 {{request}})
    ↓
backend_orch.run_task(backend="claude", prompt=full_prompt)
    ↓
LLM 输出（结构化推荐）
    ↓
SlashCommandResult(success=True, output=...)
```

#### 4. 测试覆盖

**测试文件**: `tests/test_master_orchestrator_command.py` (420 行)

**测试用例**:

| # | 测试名称 | 覆盖内容 | 状态 |
|---|---------|---------|------|
| 1 | `test_master_orchestrator_skill_creation` | SKILL.md 文件创建和结构验证 | ✅ |
| 2 | `test_markdown_skill_executor_parsing` | MarkdownSkillExecutor 解析 SKILL.md | ✅ |
| 3 | `test_master_orchestrator_skill_execution` | 技能执行和提示词包装 | ✅ |
| 4 | `test_slash_command_registration` | /master-orchestrator 命令注册 | ✅ |
| 5 | `test_format_processing` | 三种输入格式处理 | ✅ |
| 6 | `test_end_to_end_execution` | 端到端流程（Registry + Factory + Handler） | ✅ |

**测试结果**:
```bash
$ python tests/test_master_orchestrator_command.py
======================================================================
测试完成: 6 通过, 0 失败
======================================================================
```

### 文件清单

| 文件 | 类型 | 行数 | 说明 |
|------|------|------|------|
| `skills/master-orchestrator/SKILL.md` | 新增 | 102 | 元技能定义 |
| `core/slash_command_registry.py` | 修改 | +14 | 命令注册 |
| `tests/test_master_orchestrator_command.py` | 新增 | 420 | 完整集成测试 |
| `docs/PHASE4_SLASH_COMMAND_IMPLEMENTATION.md` | 新增 | 420 | 实施总结 |

**总计**: ~956 行（含文档）

### 技术亮点

1. **元技能模式**: 不直接执行任务，而是分析需求并推荐资源
2. **零新代码复用**: 完全利用 Phase 3 基础设施（MarkdownSkillExecutor + SkillCommandHandler）
3. **结构化输出**: 规范化的 Markdown 输出，便于解析
4. **资源匹配库**: 内置丰富的资源匹配规则

### 使用示例

```bash
# 示例 1: 代码审查
/master-orchestrator 帮我审查代码的安全性

# 示例 2: 项目分析
/master-orchestrator 分析项目的技术栈和依赖关系

# 示例 3: 文档生成
/master-orchestrator 生成 REST API 接口文档
```

---

## Phase 1: Intent 类和分析器增强 ⏳

### 实施状态

**完成度**: 0% | **优先级**: 高 | **预估工作量**: 2-3 天

### 实施目标

1. 扩展 Intent 类，添加 `entity` 和 `candidates` 字段
2. 修改 ClaudeIntentAnalyzer，实现资源推断逻辑
3. 将 UnifiedRegistry 传递给分析器，支持资源查询
4. 实现基于描述和标签的资源匹配算法

### 待实施内容

#### 1. Intent 类扩展

**文件**: `analyzers/claude_intent_analyzer.py`

**当前结构**:
```python
@dataclass
class Intent:
    user_need: str
    task_type: str
    complexity: str
    requires_llm: bool
    confidence_score: float
```

**目标结构**:
```python
@dataclass
class Intent:
    user_need: str
    task_type: str
    complexity: str
    requires_llm: bool
    confidence_score: float

    # 新增字段
    entity: Optional[str] = None            # 提取的实体（如 "code-review"）
    candidates: List[str] = field(default_factory=list)  # 候选资源列表
    # 格式: ["skill:code-review", "skill:security-scanner"]
```

#### 2. ClaudeIntentAnalyzer 增强

**修改点**:

```python
class ClaudeIntentAnalyzer:
    def __init__(self, backend_orch: BackendOrchestrator, registry: UnifiedRegistry):
        self.backend_orch = backend_orch
        self.registry = registry  # 新增：访问资源注册表

    def analyze(self, user_need: str) -> Intent:
        # 1. 现有意图分析逻辑（保持不变）
        task_type, complexity, requires_llm = self._analyze_intent(user_need)

        # 2. 新增：资源推断
        entity, candidates = self._infer_resources(user_need, task_type)

        # 3. 构建 Intent（包含新字段）
        return Intent(
            user_need=user_need,
            task_type=task_type,
            complexity=complexity,
            requires_llm=requires_llm,
            confidence_score=0.8,
            entity=entity,
            candidates=candidates
        )

    def _infer_resources(self, user_need: str, task_type: str) -> Tuple[str, List[str]]:
        """
        资源推断逻辑

        策略：
        1. 关键词匹配（基于 description 和 tags）
        2. 任务类型映射（task_type → resource_type）
        3. LLM 辅助推断（可选）

        Returns:
            (entity, candidates) - 主实体和候选资源列表
        """
        # 获取所有 Skills
        all_skills = self.registry.list_resources(
            type_filter=ResourceType.SKILL,
            enabled_only=True
        )

        # 关键词匹配
        keywords = self._extract_keywords(user_need)
        scored_resources = []

        for skill in all_skills:
            score = self._calculate_match_score(keywords, skill)
            if score > 0.3:  # 阈值
                scored_resources.append((skill.namespace, score))

        # 排序（按匹配度降序）
        scored_resources.sort(key=lambda x: x[1], reverse=True)

        # 提取 entity 和 candidates
        entity = scored_resources[0][0] if scored_resources else None
        candidates = [r[0] for r in scored_resources[:3]]  # Top 3

        return entity, candidates

    def _extract_keywords(self, user_need: str) -> List[str]:
        """从用户需求中提取关键词"""
        # 简单实现：分词 + 停用词过滤
        # 可扩展为 LLM 提取
        pass

    def _calculate_match_score(self, keywords: List[str], skill: ResourceMetadata) -> float:
        """计算匹配分数"""
        score = 0.0

        # 1. 描述匹配
        description = skill.config.get('description', '').lower()
        for keyword in keywords:
            if keyword.lower() in description:
                score += 0.3

        # 2. 标签匹配
        tags = skill.config.get('tags', [])
        for keyword in keywords:
            if keyword.lower() in [t.lower() for t in tags]:
                score += 0.5

        # 3. 名称匹配
        if any(k.lower() in skill.name.lower() for k in keywords):
            score += 0.4

        return min(score, 1.0)
```

#### 3. MasterOrchestrator 集成

**文件**: `master_orchestrator.py`

**修改点**:

```python
class MasterOrchestrator:
    def __init__(self, ...):
        # 创建分析器时传递 registry
        self.intent_analyzer = ClaudeIntentAnalyzer(
            backend_orch=self.backend_orch,
            registry=self.unified_registry  # 新增
        )

    def process(self, user_need: str):
        # 1. 意图分析（现在包含资源推断）
        intent = self.intent_analyzer.analyze(user_need)

        # 2. 执行路由（使用 intent.candidates）
        result = self.execution_router.route(intent)

        return result
```

### 测试计划

**新增测试文件**: `tests/test_intent_resource_inference.py`

**测试用例**:

1. `test_intent_entity_extraction` - 测试实体提取
2. `test_intent_candidates_inference` - 测试候选资源推断
3. `test_keyword_matching` - 测试关键词匹配算法
4. `test_score_calculation` - 测试匹配分数计算
5. `test_registry_integration` - 测试 Registry 集成

### 依赖关系

**前置条件**:
- ✅ Phase 3: ResourceContentParser (已完成)
- ✅ Phase 4: master-orchestrator SKILL (已完成)
- ✅ UnifiedRegistry 已实现

**后续影响**:
- → Phase 2: ExecutionRouter 需要使用 `intent.candidates`

---

## Phase 2: ExecutionRouter 候选资源支持 ⏳

### 实施状态

**完成度**: 0% | **优先级**: 中 | **预估工作量**: 1-2 天

### 实施目标

1. 修改 ExecutionRouter，支持 `intent.candidates` 候选资源列表
2. 实现资源降级策略（主资源失败 → 备选资源）
3. 添加资源可用性检查
4. 实现执行结果反馈机制

### 待实施内容

#### 1. ExecutionRouter 增强

**文件**: `master_orchestrator.py` (ExecutionRouter 部分)

**当前逻辑**:
```python
def _route_v3(self, intent: Intent):
    # 基于 task_type 路由
    if intent.task_type == "code_review":
        return self._execute_skill("code-review")
    # ...
```

**目标逻辑**:
```python
def _route_v3(self, intent: Intent):
    """
    V3 路由逻辑（支持候选资源）

    策略：
    1. 优先使用 intent.entity（主资源）
    2. 如果主资源失败/不可用，尝试 intent.candidates（备选资源）
    3. 记录执行结果，用于后续优化
    """
    # 1. 构建资源执行队列
    resources_to_try = []
    if intent.entity:
        resources_to_try.append(intent.entity)
    resources_to_try.extend(intent.candidates or [])

    # 去重
    resources_to_try = list(dict.fromkeys(resources_to_try))

    # 2. 依次尝试执行
    last_error = None
    for resource_ns in resources_to_try:
        try:
            # 检查资源可用性
            if not self._check_resource_availability(resource_ns):
                logger.warning(f"Resource {resource_ns} not available, trying next...")
                continue

            # 执行资源
            result = self._execute_resource(resource_ns, intent.user_need)

            if result.success:
                logger.info(f"Successfully executed resource: {resource_ns}")
                return result
            else:
                logger.warning(f"Resource {resource_ns} failed: {result.error}")
                last_error = result.error
                # 继续尝试下一个

        except Exception as e:
            logger.error(f"Exception executing {resource_ns}: {e}")
            last_error = str(e)
            continue

    # 3. 所有资源都失败
    return TaskResult(
        backend="none",
        prompt=intent.user_need,
        output="",
        success=False,
        error=f"All candidate resources failed. Last error: {last_error}",
        duration_seconds=0.0
    )

def _check_resource_availability(self, resource_ns: str) -> bool:
    """检查资源是否可用"""
    metadata = self.unified_registry.get(resource_ns)
    if not metadata:
        return False

    # 检查是否启用
    if not metadata.enabled:
        return False

    # 检查依赖是否满足
    for dep in metadata.dependencies:
        if not self.unified_registry.exists(dep):
            logger.warning(f"Dependency {dep} not found for {resource_ns}")
            return False

    return True

def _execute_resource(self, resource_ns: str, user_need: str) -> TaskResult:
    """执行资源"""
    # 使用 ExecutorFactory 创建执行器
    executor = self.factory.create_executor(resource_ns)
    if not executor:
        raise ValueError(f"Cannot create executor for {resource_ns}")

    # 执行
    return executor.execute(user_need)
```

#### 2. 执行结果反馈

**目的**: 记录哪些资源被成功执行，用于后续优化推断算法

```python
class ExecutionFeedback:
    """执行结果反馈记录"""

    def __init__(self):
        self.history = []  # [(user_need, resource_ns, success, timestamp), ...]

    def record(self, user_need: str, resource_ns: str, success: bool):
        """记录执行结果"""
        self.history.append({
            "user_need": user_need,
            "resource_ns": resource_ns,
            "success": success,
            "timestamp": datetime.now()
        })

    def get_success_rate(self, resource_ns: str) -> float:
        """获取资源的成功率"""
        records = [r for r in self.history if r["resource_ns"] == resource_ns]
        if not records:
            return 0.0

        success_count = sum(1 for r in records if r["success"])
        return success_count / len(records)

    def get_best_resource_for_need(self, user_need_pattern: str) -> Optional[str]:
        """根据历史记录推荐最佳资源"""
        # 基于相似度匹配 + 成功率
        pass
```

### 测试计划

**新增测试文件**: `tests/test_execution_router_candidates.py`

**测试用例**:

1. `test_primary_resource_execution` - 测试主资源执行
2. `test_fallback_to_candidates` - 测试降级到备选资源
3. `test_resource_availability_check` - 测试资源可用性检查
4. `test_all_resources_fail` - 测试所有资源失败场景
5. `test_execution_feedback_recording` - 测试执行反馈记录

### 依赖关系

**前置条件**:
- ✅ Phase 3: MarkdownSkillExecutor (已完成)
- ⏳ Phase 1: Intent.candidates 字段 (待实施)

**后续影响**:
- → Phase 5: 端到端测试需要覆盖完整流程

---

## Phase 5: 端到端集成测试 ⏳

### 实施状态

**完成度**: 0% | **优先级**: 高 | **预估工作量**: 1-2 天

### 实施目标

1. 创建完整的端到端测试场景
2. 覆盖从用户输入到资源执行的完整流程
3. 测试多资源降级场景
4. 性能和压力测试

### 待实施内容

#### 1. 端到端测试场景

**测试文件**: `tests/test_end_to_end_integration.py`

**场景设计**:

```python
# 场景 1: 单资源成功执行
def test_e2e_single_resource_success():
    """
    用户输入 → 意图分析 → 推断 code-review → 执行成功
    """
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("帮我审查代码质量")

    assert result.success == True
    assert "code-review" in result.metadata.get("executed_resource", "")

# 场景 2: 主资源失败，降级到备选资源
def test_e2e_fallback_to_candidate():
    """
    用户输入 → 推断 [skill:A, skill:B] → skill:A 失败 → skill:B 成功
    """
    # Mock skill:A 失败
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("优化代码性能")

    assert result.success == True
    # 验证使用了备选资源

# 场景 3: /master-orchestrator 元命令完整流程
def test_e2e_meta_command_workflow():
    """
    用户: /master-orchestrator 生成 API 文档
    → 执行 master-orchestrator skill
    → 返回资源推荐
    → (可选) 解析推荐并自动执行
    """
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("/master-orchestrator 生成 API 文档")

    assert result.success == True
    assert "推荐资源" in result.output or "Recommended resources" in result.output

# 场景 4: 格式化输入处理
def test_e2e_formatted_input():
    """
    测试三种输入格式
    """
    orch = MasterOrchestrator(auto_discover=True)

    # 非格式化
    r1 = orch.process("帮我优化代码")
    assert r1.success == True

    # 需求理解格式
    r2 = orch.process("需求理解：分析项目依赖")
    assert r2.success == True

    # Slash Command 格式
    r3 = orch.process("/code_fix 修复bug")
    assert r3.success == True

# 场景 5: 复杂任务（多资源组合）
def test_e2e_complex_task_multi_resource():
    """
    用户: 帮我完整审查项目并生成报告
    → 推断需要多个资源: [code-review, project-analyzer, doc-generator]
    → 顺序执行或并行执行
    """
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("帮我完整审查项目并生成报告")

    assert result.success == True
    # 验证多个资源被调用
```

#### 2. 性能测试

```python
def test_performance_resource_inference():
    """测试资源推断性能"""
    orch = MasterOrchestrator(auto_discover=True)

    # 100 次推断应在 5 秒内完成
    start = time.time()
    for i in range(100):
        orch.intent_analyzer.analyze(f"测试任务 {i}")
    duration = time.time() - start

    assert duration < 5.0

def test_cache_effectiveness():
    """测试执行器缓存效果"""
    orch = MasterOrchestrator(auto_discover=True)

    # 第一次执行（创建执行器）
    t1 = time.time()
    orch.process("帮我审查代码")
    first_duration = time.time() - t1

    # 第二次执行（使用缓存）
    t2 = time.time()
    orch.process("帮我审查代码")
    second_duration = time.time() - t2

    # 第二次应明显更快
    assert second_duration < first_duration * 0.5
```

#### 3. 错误处理测试

```python
def test_invalid_resource_graceful_failure():
    """测试无效资源的优雅失败"""
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("执行不存在的技能")

    assert result.success == False
    assert "not found" in result.error.lower()

def test_resource_dependency_missing():
    """测试资源依赖缺失场景"""
    # 创建 skill:B 依赖 skill:A，但 skill:A 不存在
    orch = MasterOrchestrator(auto_discover=True)
    result = orch.process("执行依赖缺失的技能")

    assert result.success == False
    assert "dependency" in result.error.lower()
```

### 测试矩阵

| 测试类别 | 测试数量 | 覆盖内容 |
|---------|---------|---------|
| 基础流程 | 3 | 单资源、多资源、降级 |
| 输入格式 | 3 | 非格式化、格式化、Slash Command |
| 元命令 | 2 | /master-orchestrator 完整流程 |
| 性能 | 2 | 推断性能、缓存效果 |
| 错误处理 | 3 | 无效资源、依赖缺失、执行失败 |
| **总计** | **13** | **完整覆盖** |

### 依赖关系

**前置条件**:
- ⏳ Phase 1: Intent 增强 (待实施)
- ⏳ Phase 2: ExecutionRouter 增强 (待实施)

---

## 整体进度追踪

### 五阶段完成情况

```
Phase 3 ███████████████████████████████████████ 100% ✅
Phase 4 ███████████████████████████████████████ 100% ✅
Phase 1 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 2 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 5 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⏳
```

**整体完成度**: 40% (2/5 阶段)

### 代码统计

| 类别 | Phase 3 | Phase 4 | Phase 1-5 (预估) | 总计 |
|------|---------|---------|-----------------|------|
| 核心代码 | 530 行 | 116 行 | ~800 行 | ~1,446 行 |
| 测试代码 | 500 行 | 420 行 | ~600 行 | ~1,520 行 |
| 文档 | 456 行 | 420 行 | ~400 行 | ~1,276 行 |
| **总计** | 1,486 行 | 956 行 | ~1,800 行 | **~4,242 行** |

### 测试覆盖

| 阶段 | 测试数量 | 通过率 | 状态 |
|------|---------|--------|------|
| Phase 3 | 10 | 100% | ✅ |
| Phase 4 | 6 | 100% | ✅ |
| Phase 1 | 5 (预估) | - | ⏳ |
| Phase 2 | 5 (预估) | - | ⏳ |
| Phase 5 | 13 (预估) | - | ⏳ |
| **总计** | **39** | **41% (16/39)** | **进行中** |

---

## 实施时间线

### 已完成阶段 ✅

| 阶段 | 开始时间 | 完成时间 | 实际耗时 |
|------|---------|---------|---------|
| Phase 3 | 2025-01-05 | 2025-01-05 | 1 天 |
| Phase 4 | 2025-01-05 | 2025-01-05 | 0.5 天 |

### 计划阶段 ⏳

| 阶段 | 预计开始 | 预计完成 | 预估工作量 |
|------|---------|---------|-----------|
| Phase 1 | 待定 | 待定 | 2-3 天 |
| Phase 2 | 待定 | 待定 | 1-2 天 |
| Phase 5 | 待定 | 待定 | 1-2 天 |

**预计总工作量**: 4.5-7.5 天

---

## 关键决策记录

| # | 决策点 | 选择 | 理由 | 影响 |
|---|--------|------|------|------|
| 1 | 资源格式 | Markdown (SKILL.md) 非 YAML | 用户明确要求 | Phase 3 实现方向 |
| 2 | 执行顺序 | Phase 3→4→1→2→5 | Phase 3-4 是基础设施，先实现可快速验证 | 提前交付可用功能 |
| 3 | 元数据解析 | 支持双格式（键值对 + YAML Frontmatter） | 灵活性 + 兼容性 | 解析器复杂度略增 |
| 4 | 命令处理 | 复用 SkillCommandHandler | 避免重复代码 | Phase 4 零新代码 |
| 5 | 资源推断 | 关键词匹配 + LLM 辅助 | 平衡性能和准确性 | Phase 1 实现策略 |
| 6 | 降级策略 | 顺序尝试候选资源 | 简单可靠 | Phase 2 实现逻辑 |

---

## 风险与挑战

### 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|-------|------|---------|
| 资源推断准确率不足 | 中 | 高 | 引入 LLM 辅助推断 + 用户反馈优化 |
| 降级策略性能问题 | 低 | 中 | 限制候选资源数量 + 并行执行 |
| 多资源组合复杂度 | 高 | 高 | Phase 5 充分测试 + 简化初期设计 |
| Registry 查询性能 | 低 | 低 | 已有索引机制 |

### 集成风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|-------|------|---------|
| Phase 1-2 集成冲突 | 中 | 中 | 明确接口定义 + 单元测试 |
| 向后兼容性破坏 | 低 | 高 | 保留 YAMLSkillExecutor 别名 |
| 性能退化 | 中 | 中 | Phase 5 性能测试 + profiling |

---

## 下一步行动计划

### 立即可执行（Phase 1）

1. **扩展 Intent 类**
   - 添加 `entity` 和 `candidates` 字段
   - 更新相关类型定义

2. **实现资源推断算法**
   - 关键词提取
   - 匹配分数计算
   - 候选资源排序

3. **集成 UnifiedRegistry**
   - 修改 ClaudeIntentAnalyzer 构造函数
   - 实现资源查询逻辑

4. **单元测试**
   - 测试实体提取
   - 测试候选资源推断
   - 测试匹配算法

### 后续任务（Phase 2）

1. **修改 ExecutionRouter**
   - 支持候选资源列表
   - 实现降级逻辑

2. **资源可用性检查**
   - enabled 状态检查
   - 依赖满足检查

3. **执行反馈机制**
   - 记录执行结果
   - 成功率统计

### 最终任务（Phase 5）

1. **端到端测试场景**
   - 单资源成功
   - 多资源降级
   - 复杂任务组合

2. **性能测试**
   - 推断性能基准
   - 缓存效果验证

3. **压力测试**
   - 并发执行
   - 资源竞争

---

## 附录

### A. 核心文件索引

**Phase 3 文件**:
```
core/resource_content_parser.py          # 解析器基类 + Markdown 实现
core/executor_factory.py                 # MarkdownSkillExecutor
tests/test_resource_content_parser.py    # 解析器测试
tests/test_markdown_skill_executor.py    # 执行器测试
examples/skill-example.md                # SKILL.md 示例
docs/RESOURCE_CONTENT_PARSER_IMPLEMENTATION.md  # Phase 3 文档
```

**Phase 4 文件**:
```
skills/master-orchestrator/SKILL.md      # 元技能定义
core/slash_command_registry.py           # 命令注册
tests/test_master_orchestrator_command.py  # 集成测试
docs/PHASE4_SLASH_COMMAND_IMPLEMENTATION.md  # Phase 4 文档
```

**Phase 1-5 待创建文件**:
```
tests/test_intent_resource_inference.py  # Phase 1 测试
tests/test_execution_router_candidates.py  # Phase 2 测试
tests/test_end_to_end_integration.py     # Phase 5 测试
```

### B. 相关文档

1. **设计文档**:
   - `docs/RESOURCE_INTEGRATION_DESIGN_V2.md` - 整体架构设计
   - `docs/RESOURCE_SCANNER_V2_MIGRATION.md` - V2 扫描器迁移指南

2. **实施文档**:
   - `docs/RESOURCE_CONTENT_PARSER_IMPLEMENTATION.md` - Phase 3 实施总结
   - `docs/PHASE4_SLASH_COMMAND_IMPLEMENTATION.md` - Phase 4 实施总结
   - `docs/DEVELOPMENT_PLAN_SUMMARY.md` - 本文档

3. **用户文档**:
   - `README.md` - 项目总览
   - `examples/skill-example.md` - SKILL.md 格式示例

### C. 术语表

| 术语 | 定义 |
|------|------|
| **元技能 (Meta-Skill)** | 不直接执行任务，而是分析需求并推荐资源的特殊技能 |
| **资源推断 (Resource Inference)** | 根据用户需求推断合适资源的过程 |
| **候选资源 (Candidate Resources)** | 推断出的多个可能匹配的资源列表 |
| **降级策略 (Fallback Strategy)** | 主资源失败时，尝试备选资源的机制 |
| **提示词包装 (Prompt Wrapping)** | 将资源内容（System Prompt + User Prompt Template）组合成完整提示词 |
| **执行反馈 (Execution Feedback)** | 记录资源执行结果，用于优化推断算法 |
| **UnifiedRegistry** | 统一资源注册表，管理所有 Skills/Agents/Commands/Prompts |

---

**文档版本**: v1.0
**最后更新**: 2025-01-05
**当前状态**: Phase 3-4 已完成，Phase 1-2-5 待实施
**整体进度**: 40% (2/5 阶段完成)
