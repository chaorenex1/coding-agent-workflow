# 资源扫描与主流程整合设计

## 问题诊断

### 当前架构断层

MasterOrchestrator 存在两套并行但未连通的系统：

#### V3 资源发现系统（已实现但未连接）
```
ConfigLoader → ResourceScannerV2 → OrchestratorConfig
     ↓
create_registry_from_config()
     ↓
UnifiedRegistry (ResourceMetadata)
     ↓
ExecutorFactory ⚠️ 已创建但未使用
```

#### V2 执行路由系统（当前主流程）
```
process() → _analyze_intent() → ExecutionRouter.route()
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
            CommandExecutor      PromptManager      AgentCaller
            (硬编码实例)         (硬编码实例)       (硬编码实例)
```

### 关键代码位置

**master_orchestrator.py**:
- Line 519: `self.router = ExecutionRouter(self.backend_orch)` - 传统路由器创建
- Line 563: `self.factory = ExecutorFactory(...)` - V3工厂创建（但未被路由器使用）
- Line 692: `result = self.router.route(intent, request)` - 总是使用传统路由

**ExecutionRouter 类** (Line 213-278):
```python
class ExecutionRouter:
    def __init__(self, backend_orch: BackendOrchestrator):
        self.command_executor = CommandExecutor(...)  # 硬编码
        self.prompt_manager = PromptManager(...)      # 硬编码
        self.agent_caller = AgentCaller(...)          # 硬编码
        self.skill_registry = SkillRegistry()         # 硬编码
```

### 问题总结

1. **ExecutorFactory 孤岛**：V3工厂虽然创建，但ExecutionRouter不知道它的存在
2. **双重资源系统**：
   - V3: UnifiedRegistry 管理所有资源元数据
   - V2: 各执行器内部独立管理资源
3. **无法利用扫描结果**：用户自定义的skills/commands/agents/prompts无法被主流程发现并执行

---

## 解决方案

### 设计原则

1. **单路径架构**：V3模式与V2模式完全独立，根据 auto_discover 开关决定
2. **清晰职责**：V3 模式完全由 UnifiedRegistry + ExecutorFactory 驱动
3. **最小修改**：复用现有 ExecutorFactory 适配器，无需重写执行器
4. **向后兼容**：非V3模式完全不受影响

### 推荐方案：单路径 ExecutionRouter

#### 方案架构

```
MasterOrchestrator 初始化
        ↓
  auto_discover?
    ↙         ↘
  YES          NO
   ↓            ↓
V3 Router    V2 Router
(使用 Factory)  (硬编码)
```

**V3 执行路径**：
```
process() → _analyze_intent() → ExecutionRouter.route()
                                        ↓
                        提取资源名称（基于 intent.mode）
                                        ↓
                        构建 namespace (e.g., "skill:code-review")
                                        ↓
                        UnifiedRegistry.exists(namespace)?
                                ↙              ↘
                              YES               NO
                               ↓                ↓
                ExecutorFactory          抛出异常
                .create_executor()       (资源未注册)
                               ↓
                        executor.execute()
```

**V2 执行路径**（不变）：
```
process() → _analyze_intent() → ExecutionRouter.route()
                                        ↓
                        根据 intent.mode 分发
                                        ↓
                ┌──────────────┬──────────────┐
                ↓              ↓              ↓
        CommandExecutor  PromptManager  AgentCaller
```

#### 核心修改点

**1. ExecutionRouter 构造函数 - 单路径初始化**

```python
class ExecutionRouter:
    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        # V3 参数（全有或全无）
        registry: Optional[UnifiedRegistry] = None,
        factory: Optional[ExecutorFactory] = None
    ):
        self.backend_orch = backend_orch
        self.registry = registry
        self.factory = factory

        # 判断运行模式
        self.v3_mode = (registry is not None and factory is not None)

        if not self.v3_mode:
            # V2 模式：初始化传统执行器
            self.command_executor = CommandExecutor(
                backend_orch=backend_orch,
                use_claude=True,
                fallback_to_rules=True
            )
            self.prompt_manager = PromptManager(
                backend_orch=backend_orch,
                use_claude=True,
                fallback_to_local=True
            )
            self.agent_caller = AgentCaller(
                backend_orch=backend_orch,
                use_claude=True,
                fallback_to_simple=True
            )
            self.skill_registry = SkillRegistry()
        else:
            # V3 模式：不需要传统执行器
            logger.info("ExecutionRouter initialized in V3 mode")
```

**2. 路由逻辑 - 单路径分发**

```python
def route(self, intent: Intent, request: str) -> Any:
    """路由请求到合适的执行器（单路径）"""

    if self.v3_mode:
        # V3 路径：完全使用 UnifiedRegistry + ExecutorFactory
        return self._route_v3(intent, request)
    else:
        # V2 路径：使用传统执行器
        return self._route_v2(intent, request)

def _route_v3(self, intent: Intent, request: str) -> Any:
    """V3 执行路径"""
    # 1. 根据 intent.mode 确定资源类型
    resource_type_map = {
        ExecutionMode.COMMAND: "command",
        ExecutionMode.AGENT: "agent",
        ExecutionMode.SKILL: "skill",
        ExecutionMode.PROMPT: "prompt",
        ExecutionMode.BACKEND: "backend"  # 直接调用后端
    }

    resource_type = resource_type_map.get(intent.mode)

    # 如果是 BACKEND 模式，直接调用后端
    if intent.mode == ExecutionMode.BACKEND:
        return self._call_backend_direct(request, intent)

    # 2. 从请求中提取资源名称
    resource_name = self._extract_resource_name(request, intent)
    if not resource_name:
        raise ValueError(f"无法从请求中提取资源名称: {request}")

    namespace = f"{resource_type}:{resource_name}"
    logger.debug(f"V3 路由: {namespace}")

    # 3. 检查资源是否在注册表中
    if not self.registry.exists(namespace):
        raise ValueError(f"资源未注册: {namespace}")

    # 4. 创建执行器
    executor = self.factory.create_executor(namespace)
    if not executor:
        raise RuntimeError(f"无法创建执行器: {namespace}")

    # 5. 执行
    return executor.execute(request)

def _route_v2(self, intent: Intent, request: str) -> Any:
    """V2 传统执行路径（保持现有逻辑不变）"""
    if intent.mode == ExecutionMode.COMMAND:
        return self._execute_command(request)
    elif intent.mode == ExecutionMode.AGENT:
        return self._call_agent(request, intent)
    elif intent.mode == ExecutionMode.PROMPT:
        return self._use_prompt(request, intent)
    elif intent.mode == ExecutionMode.SKILL:
        return self._execute_skill(request, intent)
    elif intent.mode == ExecutionMode.BACKEND:
        return self._call_backend(request, intent)
    else:
        raise ValueError(f"Unknown execution mode: {intent.mode}")
```

**3. 资源名称提取（关键逻辑）**

```python
def _extract_resource_name(self, request: str, intent: Intent) -> Optional[str]:
    """
    从请求中提取资源名称

    策略：
    1. 优先使用 intent.entity（如果 intent 分析已提取）
    2. 基于规则的简单提取
    3. 返回 None 表示无法提取
    """
    # 策略1：从 intent.entity 获取
    if hasattr(intent, 'entity') and intent.entity:
        return intent.entity

    # 策略2：基于规则提取
    # 移除常见动词前缀
    import re
    cleaned = re.sub(
        r'^(执行|运行|调用|使用|应用|启动)\s+',
        '',
        request.strip()
    )

    # 提取第一个词（可能是资源名）
    tokens = cleaned.split()
    if tokens:
        candidate = tokens[0]
        # 验证是否是合法的资源名称格式（kebab-case 或 snake_case）
        if re.match(r'^[a-z0-9_-]+$', candidate):
            return candidate

    # 无法提取
    logger.warning(f"无法从请求提取资源名称: {request}")
    return None
```

**4. MasterOrchestrator 集成**

```python
def __init__(self, ...):
    # ... 现有初始化代码 ...

    # 初始化路由器（单路径模式）
    if self.auto_discover and V3_AVAILABLE and hasattr(self, 'factory'):
        # V3 模式：传入注册表和工厂
        self.router = ExecutionRouter(
            backend_orch=self.backend_orch,
            registry=self.registry,
            factory=self.factory
        )
        logger.info("MasterOrchestrator 使用 V3 执行路径")
    else:
        # V2 模式：传统路由器
        self.router = ExecutionRouter(backend_orch=self.backend_orch)
        logger.info("MasterOrchestrator 使用 V2 执行路径")
```

---

## 实现计划

### 阶段一：核心路由逻辑修改

**目标**：实现单路径 ExecutionRouter

**变更文件**：
1. `master_orchestrator.py`:
   - Line 213-278: 重构 ExecutionRouter 类
     - 添加 `v3_mode` 标志
     - 添加 `_route_v3()` 方法
     - 添加 `_route_v2()` 方法（保持现有逻辑）
     - 添加 `_extract_resource_name()` 方法
     - 添加 `_call_backend_direct()` 方法（V3 BACKEND 模式）

   - Line 519: 修改 router 初始化逻辑
     ```python
     if self.auto_discover and V3_AVAILABLE and hasattr(self, 'factory'):
         self.router = ExecutionRouter(
             self.backend_orch,
             registry=self.registry,
             factory=self.factory
         )
     else:
         self.router = ExecutionRouter(self.backend_orch)
     ```

**预估工作量**：约 200 行代码修改

### 阶段二：Intent 分析增强（可选）

**目标**：改进 intent.entity 提取，降低 `_extract_resource_name()` 的负担

**当前状态**：
- `ClaudeIntentAnalyzer` 已返回 Intent 对象
- 但 Intent 类可能没有 `entity` 字段

**建议修改**：
1. 在 Intent 类添加 `entity: Optional[str]` 字段
2. 修改 Claude 分析提示词，要求提取资源名称：
   ```python
   prompt = f"""分析请求并返回JSON:
   请求: {request}

   返回格式:
   {{
       "mode": "skill|command|agent|prompt|backend",
       "entity": "resource-name",  # 新增：资源名称
       "task_type": "...",
       "complexity": "...",
       "confidence": 0.0-1.0
   }}"""
   ```

**好处**：
- V3 路径可直接使用 `intent.entity`，无需正则提取
- 提升准确性

### 阶段三：测试验证

**单元测试**：
```python
# tests/test_execution_router_v3.py

def test_v3_router_skill_execution():
    """测试 V3 路由器执行 skill"""
    # 创建测试 skill
    skill_dir = tmp_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("...")

    # 初始化 V3 组件
    loader = ConfigLoader(project_root=tmp_path)
    config = loader.load()
    registry = create_registry_from_config(config)
    factory = ExecutorFactory(backend_orch, registry)

    # 创建 V3 路由器
    router = ExecutionRouter(
        backend_orch,
        registry=registry,
        factory=factory
    )

    # 执行
    intent = Intent(mode=ExecutionMode.SKILL, entity="test-skill")
    result = router.route(intent, "执行 test-skill")

    assert result is not None
```

**集成测试**：
```python
# 端到端测试
orchestrator = MasterOrchestrator(auto_discover=True)
result = orchestrator.process("执行 code-review")
assert result.success
```

### 阶段四：监控与诊断

**日志增强**：
```python
# V3 路由日志
logger.info(f"[V3 Router] Namespace: {namespace}")
logger.debug(f"[V3 Router] Registry has {len(self.registry)} resources")

# V2 路由日志
logger.info(f"[V2 Router] Mode: {intent.mode.value}")
```

**诊断命令**（已有 Slash Command 系统）：
```bash
/discover              # 列出所有已发现资源（已实现）
/registry-stats        # 显示注册表统计（新增）
/executor-cache        # 显示执行器缓存（新增）
```

---

## 备选方案对比

### 方案A：单路径 ExecutionRouter（推荐 ✅）

**架构**：
- V3 模式：完全使用 UnifiedRegistry + ExecutorFactory
- V2 模式：完全使用传统执行器
- 根据 auto_discover 开关在初始化时决定

**优点**：
- ✅ 清晰的职责分离
- ✅ 避免运行时复杂判断
- ✅ 性能开销最小
- ✅ 易于调试（单一代码路径）
- ✅ 最小代码修改（约 200 行）

**缺点**：
- ⚠️ V3 模式下无 V2 兜底（必须确保资源注册正确）

**结论**：推荐实施

---

### 方案B：双路径降级（已否决 ❌）

**架构**：
- 优先尝试 V3 路径
- 失败时降级到 V2 路径

**优点**：
- ✅ 容错性强

**缺点**：
- ❌ 运行时判断逻辑复杂
- ❌ 性能开销（每次都要尝试两次）
- ❌ 难以诊断（不知道走了哪条路径）
- ❌ 违反单路径原则

**结论**：已根据用户需求否决

---

### 方案C：独立 V3Router 类（不推荐 ❌）

**架构**：
- 创建新的 `V3ExecutionRouter` 类
- MasterOrchestrator 根据模式选择实例化哪个类

**优点**：
- ✅ V2/V3 完全隔离，无交叉影响

**缺点**：
- ❌ 代码重复（BACKEND 模式等逻辑需要重写）
- ❌ 维护两套路由器
- ❌ 违反 DRY 原则
- ❌ 代码量大（需重写 200+ 行）

**结论**：不推荐，成本高于收益

---

### 方案D：仅通过 Slash Commands 访问（不推荐 ❌）

**架构**：
- 保持现状，V3 资源只能通过 `/skill-name` 等命令访问
- 不修改自然语言处理路径

**优点**：
- ✅ 零风险
- ✅ 无需修改核心逻辑

**缺点**：
- ❌ 用户体验差（必须记住命令语法）
- ❌ 违背自动发现的设计初衷
- ❌ 资源扫描功能形同虚设
- ❌ 无法发挥 ClaudeIntentAnalyzer 的价值

**结论**：不推荐，违背核心需求

---

## 风险与缓解

### 风险1：资源名称提取失败

**影响**：V3 模式下无法匹配到正确资源，导致执行失败

**缓解措施**：
1. **阶段性实施**：
   - 初期要求用户使用规范格式（如 "执行 resource-name"）
   - 逐步优化 `_extract_resource_name()` 逻辑

2. **Intent 分析增强**（阶段二）：
   - 修改 ClaudeIntentAnalyzer，在 Intent 中返回 entity 字段
   - 利用 LLM 准确提取资源名称

3. **用户明确指定**：
   - 支持 namespace 格式：`"skill:code-review"`
   - Slash Command 作为备选：`/code-review`

4. **详细错误信息**：
   ```python
   raise ValueError(
       f"资源未找到: {namespace}\n"
       f"可用资源: {list(self.registry.list_resources(type_filter=resource_type))}"
   )
   ```

### 风险2：执行器创建失败

**影响**：已注册资源无法执行

**缓解措施**：
1. **ExecutorFactory 异常处理**（已实现）：
   - create_executor() 返回 None 而非抛异常
   - 详细日志记录失败原因

2. **资源验证**（开发时）：
   - 单元测试覆盖所有资源类型
   - 集成测试验证端到端流程

3. **运行时诊断**：
   ```python
   # 在 _route_v3() 中
   if not executor:
       metadata = self.registry.get(namespace)
       logger.error(
           f"创建执行器失败: {namespace}\n"
           f"元数据: {metadata}\n"
           f"检查路径是否存在: {metadata.path}"
       )
   ```

### 风险3：V3 模式下缺少某些资源

**影响**：用户期望的功能在 V3 模式下不可用

**缓解措施**：
1. **内置资源迁移**：
   - 将常用的 V2 资源（如内置命令）注册到 V3 注册表
   - 通过 ConfigLoader 自动发现内置资源

2. **文档说明**：
   - 清晰标注哪些功能需要 V3 模式
   - 提供迁移指南

3. **Slash Command 兜底**：
   - Slash Command 系统独立于路由器
   - 即使 V3 路由失败，`/command` 仍可用

### 风险4：性能开销

**影响**：每次请求都查询注册表和创建执行器

**缓解措施**：
1. **执行器缓存**（已实现）：
   - ExecutorFactory 内置缓存机制
   - 同一资源只创建一次执行器实例

2. **O(1) 查询**：
   - UnifiedRegistry 使用字典存储
   - namespace 查询复杂度 O(1)

3. **性能监控**：
   ```python
   import time
   start = time.time()
   executor = self.factory.create_executor(namespace)
   duration = time.time() - start
   if duration > 0.1:  # 超过 100ms 警告
       logger.warning(f"执行器创建耗时: {duration:.3f}s for {namespace}")
   ```

---

## 总结

### 推荐实施方案

✅ **方案A：单路径 ExecutionRouter**

### 核心设计特点

1. **单一路径原则**：
   - V3 模式：完全使用 UnifiedRegistry + ExecutorFactory
   - V2 模式：完全使用传统执行器
   - 根据 `auto_discover` 在初始化时决定，运行时无切换

2. **清晰的职责分离**：
   ```
   auto_discover=True  → V3 Router → registry.exists() → factory.create()
   auto_discover=False → V2 Router → 硬编码执行器
   ```

3. **最小代码修改**：
   - 仅需修改 ExecutionRouter 类（约 200 行）
   - V2 逻辑完全保留，零影响
   - 复用现有的 ExecutorFactory 适配器

4. **性能优化**：
   - 执行器缓存（ExecutorFactory 已实现）
   - O(1) 注册表查询（UnifiedRegistry）
   - 无运行时路径判断开销

### 关键实现点

| 模块 | 修改内容 | 代码量 |
|------|---------|--------|
| ExecutionRouter.__init__ | 添加 v3_mode 标志 | 20 行 |
| ExecutionRouter._route_v3 | V3 路由逻辑（新增） | 50 行 |
| ExecutionRouter._route_v2 | V2 路由逻辑（重构） | 30 行 |
| ExecutionRouter._extract_resource_name | 资源名提取（新增） | 30 行 |
| MasterOrchestrator.__init__ | router 初始化修改 | 10 行 |
| 测试文件 | 单元测试 + 集成测试 | 100 行 |

**总计**：约 240 行代码

### 下一步行动

#### 立即执行（阶段一）：
1. ✅ 设计文档已完成
2. ⏭️ 修改 `ExecutionRouter` 类：
   - 添加 `v3_mode` 标志
   - 实现 `_route_v3()` 方法
   - 实现 `_extract_resource_name()` 方法
   - 重构 `route()` 方法为单路径分发

3. ⏭️ 修改 `MasterOrchestrator.__init__()`：
   - 根据 auto_discover 传递 registry 和 factory

4. ⏭️ 创建测试：
   - `tests/test_execution_router_v3.py`
   - 集成测试验证端到端流程

#### 后续优化（阶段二-四）：
- Intent 分析增强（添加 entity 字段）
- 监控与诊断（日志、Slash Commands）
- 性能监控

### 预期效果

**V3 模式下的用户体验**：

```bash
# 1. 创建自定义 skill
$ cat > skills/code-review/SKILL.md << EOF
# code-review

description: Code review assistant
enabled: true
priority: 50
EOF

# 2. 启动 V3 模式
orchestrator = MasterOrchestrator(auto_discover=True)

# 3. 自然语言调用（自动发现+执行）
orchestrator.process("执行 code-review")
  ↓
Intent 分析 → mode=SKILL
  ↓
_route_v3() → namespace="skill:code-review"
  ↓
registry.exists("skill:code-review") → True
  ↓
factory.create_executor() → YAMLSkillExecutor
  ↓
executor.execute() → 执行成功 ✅
```

**无需配置，零学习成本，即创建即可用！**
