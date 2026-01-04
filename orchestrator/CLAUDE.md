# Orchestrator项目 - Claude Code指令

## 项目概述

这是一个智能化的多后端协调系统(Orchestrator)，通过Memex-CLI集成实现了5种执行模式的统一管理。

**核心能力**:
- 智能意图识别（Claude LLM语义理解）
- 自然语言命令执行
- Agent任务路由（explore/plan/general）
- 提示词模板管理
- 多阶段开发工作流

**技术栈**: Python 3.12+, Memex-CLI, Claude/Gemini/Codex backends

---

## 角色定位

你是这个项目的架构师和开发助手。遵循以下原则：

1. **技术优先**: 保持技术讨论专注、简洁
2. **KISS原则**: 简单解决方案优于复杂设计
3. **向后兼容**: 永远不要破坏现有API
4. **统一架构**: 所有新执行器必须继承MemexExecutorBase
5. **中文交流**: 思考用英语，回复用中文

---

## 项目架构

### 目录结构

```
orchestrator/
├── analyzers/              # 意图分析器
│   └── claude_intent_analyzer.py
├── core/                   # 核心模块
│   ├── backend_orchestrator.py    # 后端协调器
│   └── event_parser.py             # 事件解析器
├── executors/              # 执行器（所有继承MemexExecutorBase）
│   ├── memex_executor_base.py      # 统一基类
│   ├── command_executor.py         # 命令执行器V2
│   ├── agent_caller.py             # Agent调用器V2
│   └── prompt_manager.py           # 提示词管理器V2
├── clients/                # 客户端
│   └── aduib_client.py
├── skills/                 # 技能系统
│   ├── skill_registry.py
│   └── dev_workflow.py
└── master_orchestrator.py  # 总协调器

skills/memex-cli/skills/    # Memex-CLI技能配置
├── intent-analyzer.yaml
├── command-parser.yaml
├── agent-router.yaml
├── prompt-renderer.yaml
└── dev-workflow.yaml

tests/                      # 测试文件
└── docs/                   # 文档
```

### 架构层次

```
用户请求
    ↓
MasterOrchestrator (总协调器)
    ├─ ClaudeIntentAnalyzer (意图识别)
    │   └─ intent-analyzer.yaml skill
    └─ ExecutionRouter (执行路由)
        ├─ CommandExecutor V2
        │   └─ command-parser.yaml skill
        ├─ AgentCaller V2
        │   └─ agent-router.yaml skill
        ├─ PromptManager V2
        │   └─ prompt-renderer.yaml skill
        └─ SkillExecutor
            └─ dev-workflow.yaml skill
                ↓
        BackendOrchestrator
            ├─ Claude
            ├─ Gemini
            └─ Codex
```

---

## 核心概念

### 1. MemexExecutorBase - 统一基类

所有执行器必须继承此基类：

```python
from orchestrator.executors.memex_executor_base import MemexExecutorBase

class MyExecutor(MemexExecutorBase):
    def __init__(self, backend_orch: BackendOrchestrator, **kwargs):
        super().__init__(backend_orch, default_backend="claude", default_timeout=60)

    def execute(self, request: str, **kwargs) -> MyResult:
        # 实现执行逻辑
        pass
```

**关键方法**:
- `execute_via_memex()`: 通过memex-cli执行skill
- `execute()`: 执行器的主入口（必须实现）

### 2. Fallback机制

所有执行器都实现三层fallback：

```
第一层: Memex-CLI + Claude Skill
    ↓ (失败)
第二层: 本地实现（rules/simple/local）
    ↓ (失败)
第三层: 错误返回
```

### 3. 5种执行模式

| 模式 | 执行器 | Skill | 用途 |
|------|--------|-------|------|
| command | CommandExecutor | command-parser | 简单命令执行 |
| agent | AgentCaller | agent-router | 智能体任务 |
| prompt | PromptManager | prompt-renderer | 模板渲染 |
| skill | SkillExecutor | dev-workflow | 复杂工作流 |
| backend | BackendOrchestrator | - | 直接LLM调用 |

---

## 开发规范

### 添加新执行器

**必须遵循**:

1. 继承`MemexExecutorBase`
2. 实现`execute()`方法
3. 定义对应的YAML skill（在`skills/memex-cli/skills/`）
4. 实现fallback机制
5. 添加单元测试
6. 更新文档

**示例**:

```python
# 1. 创建执行器
class MyExecutor(MemexExecutorBase):
    def __init__(self, backend_orch, use_claude=True, fallback=True):
        super().__init__(backend_orch, default_backend="claude")
        self.use_claude = use_claude
        self.fallback = fallback

    def execute(self, request: str, **kwargs) -> MyResult:
        if self.use_claude:
            try:
                return self._execute_via_claude(request)
            except Exception as e:
                if not self.fallback:
                    return MyResult(success=False, error=str(e))
        return self._execute_local(request)

    def _execute_via_claude(self, request):
        result = self.execute_via_memex(
            prompt=f"执行任务: {request}",
            backend="claude"
        )
        return MyResult(output=result.output, success=True)

    def _execute_local(self, request):
        # 本地实现
        return MyResult(output="本地结果", success=True)

# 2. 在ExecutionRouter中注册
class ExecutionRouter:
    def __init__(self, backend_orch):
        self.my_executor = MyExecutor(
            backend_orch=backend_orch,
            use_claude=True,
            fallback=True
        )
```

### 添加新Skill

在`skills/memex-cli/skills/`目录创建YAML文件：

```yaml
# my-skill.yaml
name: my-skill
version: 1.0.0
description: 技能描述

backend: claude
model: claude-3-5-sonnet-20241022
temperature: 0.5
max_tokens: 4000

system_prompt: |
  你是xxx专家。请执行以下任务...

user_prompt_template: |
  用户请求：{{request}}

  请执行...

examples:
  - name: 示例1
    input:
      request: "示例请求"
    output: |
      示例输出

skill_config:
  retry_on_error: true
  timeout: 60
```

### 测试规范

**必须包含**:

1. **架构测试**: 验证继承关系
   ```python
   from orchestrator.executors.memex_executor_base import MemexExecutorBase
   assert isinstance(executor, MemexExecutorBase)
   ```

2. **功能测试**: 验证核心功能
   ```python
   result = executor.execute("测试请求")
   assert result.success
   ```

3. **Fallback测试**: 验证fallback机制
   ```python
   executor_no_fallback = MyExecutor(backend_orch, use_claude=True, fallback=False)
   executor_with_fallback = MyExecutor(backend_orch, use_claude=True, fallback=True)
   ```

4. **Mock测试**: 使用Mock避免外部依赖
   ```python
   class MockBackendOrch:
       def run_task(self, **kwargs):
           return MockResult(output="mock", success=True)
   ```

---

## 常见任务

### 修改现有执行器

**步骤**:
1. 备份原文件: `cp executor.py executor_old.py.bak`
2. 修改代码
3. 运行测试: `python tests/test_executor.py`
4. 更新文档

### 添加新模板（PromptManager）

```python
from orchestrator.executors.prompt_manager import PromptTemplate

# 定义新模板
new_template = PromptTemplate(
    name="my-template",
    category="my-category",
    template="""模板内容
    变量: {var1}, {var2}
    """,
    variables=["var1", "var2"],
    description="模板描述"
)

# 添加到PromptManager
manager = PromptManager(backend_orch)
manager.add_template(new_template)

# 使用
result = manager.render("my-template", var1="值1", var2="值2")
```

### 调试执行流程

**启用verbose模式**:
```python
orch = MasterOrchestrator(
    backend_orch=backend_orch,
    use_claude_intent=True,
    verbose=True  # 打印详细日志
)

result = orch.process("你的请求", verbose=True)
```

**查看执行路径**:
```python
# 1. 意图识别
intent = orch._analyze_intent("你的请求", verbose=True)
print(f"模式: {intent.mode}, 类型: {intent.task_type}")

# 2. 执行路由
result = orch.router.route(intent, "你的请求")
print(f"结果: {result}")
```

---

## 故障排查

### 常见问题

**1. Memex-CLI不可用**
- 症状: `RuntimeError: Memex执行失败`
- 原因: memex-cli命令未安装或不在PATH中
- 解决: 系统会自动fallback到本地实现，无需处理

**2. Unicode编码错误**
- 症状: `UnicodeDecodeError: 'gbk' codec...`
- 原因: Windows下的编码问题
- 解决: 在脚本开头添加：
  ```python
  if sys.platform == 'win32':
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  ```

**3. 循环导入错误**
- 症状: `ImportError: cannot import name...`
- 原因: 模块间循环依赖
- 解决: 使用lazy import或重构依赖关系

**4. Agent执行失败**
- 症状: `AgentResult(success=False)`
- 原因: Claude API调用失败或skill配置错误
- 解决:
  - 检查backend_orch配置
  - 验证fallback机制是否启用
  - 查看error字段获取详细信息

### 日志和调试

**启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**检查执行结果**:
```python
result = executor.execute(request)
print(f"成功: {result.success}")
print(f"输出: {result.output}")
print(f"错误: {result.error}")
print(f"元数据: {result.metadata}")
```

---

## 性能优化

### 缓存策略

对于重复请求，可以添加缓存：

```python
from functools import lru_cache

class CachedExecutor(MemexExecutorBase):
    @lru_cache(maxsize=100)
    def execute(self, request: str, **kwargs):
        # 执行逻辑
        pass
```

### 并发执行

对于独立任务，可以并发执行：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(agent_caller.call_agent, req1),
        executor.submit(agent_caller.call_agent, req2),
        executor.submit(agent_caller.call_agent, req3)
    ]
    results = [f.result() for f in futures]
```

### 超时控制

所有执行器都支持超时配置：

```python
executor = MyExecutor(
    backend_orch=backend_orch,
    timeout=30  # 30秒超时
)
```

---

## 安全考虑

### 命令执行安全

CommandExecutor会自动检查：
- 危险命令（rm -rf, dd, etc）
- 需要确认的命令
- 语法错误

**禁用安全检查**（不推荐）:
```python
executor = CommandExecutor(
    backend_orch=backend_orch,
    safe_mode=False  # 禁用安全检查
)
```

### 输入验证

对于所有用户输入，应该验证：

```python
def validate_request(request: str) -> bool:
    if not request or len(request) > 10000:
        return False
    if any(dangerous in request for dangerous in ["eval", "exec", "__import__"]):
        return False
    return True
```

---

## 文档维护

### 更新文档的时机

**必须更新文档**:
- 添加新执行器
- 修改API接口
- 添加新Skill
- 完成重要功能

**文档位置**:
- 架构文档: `docs/ARCHITECTURE.md`
- API文档: `docs/API.md`
- Phase文档: `docs/PHASEx_COMPLETION.md`
- 集成文档: `docs/INTEGRATION_STATUS.md`

### 文档模板

**新执行器文档**:
```markdown
# XxxExecutor V2

## 概述
简短描述

## 架构
- 继承: MemexExecutorBase
- Skill: xxx-skill.yaml
- Fallback: xxx

## 使用示例
\`\`\`python
executor = XxxExecutor(backend_orch)
result = executor.execute("请求")
\`\`\`

## API参考
### execute()
参数、返回值、异常

## 测试
测试用例和覆盖率
```

---

## 版本历史

### Phase 1-5 完成历史

- **Phase 1** (2026-01-04): 意图识别 - ClaudeIntentAnalyzer
- **Phase 2** (2026-01-04): 命令执行 - CommandExecutor V2
- **Phase 3** (2026-01-04): Agent/Prompt Skills定义
- **Phase 4** (2026-01-04): Workflow Skills定义
- **Phase 5** (2026-01-04): 执行器改造完成

### 下一步计划

**短期**:
- [ ] 性能监控和优化
- [ ] 更多预定义Skills
- [ ] 增强错误处理

**中期**:
- [ ] 多轮对话支持
- [ ] Agent协作机制
- [ ] 分布式执行

**长期**:
- [ ] 插件系统
- [ ] 可视化界面
- [ ] 云端部署

---

## 快速参考

### 关键文件

| 文件 | 作用 | 修改频率 |
|------|------|----------|
| master_orchestrator.py | 总协调器 | 低 |
| executors/memex_executor_base.py | 执行器基类 | 极低 |
| executors/command_executor.py | 命令执行 | 中 |
| executors/agent_caller.py | Agent调用 | 中 |
| executors/prompt_manager.py | 提示词管理 | 中 |
| skills/memex-cli/skills/*.yaml | Skill配置 | 高 |

### 常用命令

```bash
# 运行测试
python tests/test_phase5_simple.py

# 检查架构
python -c "from orchestrator.executors import *; print('OK')"

# 启动交互式测试
python -i orchestrator/master_orchestrator.py

# 生成文档
python scripts/generate_docs.py  # (如果有)
```

### 联系和支持

- 项目文档: `docs/`
- 技术讨论: [GitHub Issues](如果有)
- 架构问题: 查看`docs/MEMEX_CLI_INTEGRATION_DESIGN.md`

---

## 附录

### A. 数据结构

**Intent对象**:
```python
@dataclass
class Intent:
    mode: ExecutionMode      # command/agent/prompt/skill/backend
    task_type: str          # 任务类型
    complexity: str         # simple/moderate/complex
    confidence: float       # 0.0-1.0
```

**AgentRequest对象**:
```python
@dataclass
class AgentRequest:
    agent_type: AgentType        # EXPLORE/PLAN/GENERAL_PURPOSE
    prompt: str
    thoroughness: Optional[str]  # quick/medium/very_thorough
    model: Optional[str]
```

**PromptResult对象**:
```python
@dataclass
class PromptResult:
    template_name: str
    rendered_prompt: str
    success: bool
    rendered_by: str            # "claude" or "local"
    variables: Dict[str, Any]
    error: Optional[str]
    metadata: Optional[Dict]
```

### B. 环境变量

```bash
# Memex-CLI配置
export MEMEX_CLI_PATH=/path/to/memex-cli

# Backend配置
export CLAUDE_API_KEY=your-key
export GEMINI_API_KEY=your-key
export CODEX_API_KEY=your-key

# 调试模式
export ORCHESTRATOR_DEBUG=1
export ORCHESTRATOR_VERBOSE=1
```

### C. 贡献指南

1. Fork项目
2. 创建特性分支: `git checkout -b feature/my-feature`
3. 遵循代码规范
4. 添加测试
5. 更新文档
6. 提交PR

**代码规范**:
- 遵循PEP 8
- 类型注解必须完整
- Docstring使用Google风格
- 函数保持简洁（<50行）

---

**最后更新**: 2026-01-04
**版本**: 2.0.0 (Phase 5完成)
**维护者**: Orchestrator Team
