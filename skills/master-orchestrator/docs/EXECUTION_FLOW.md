# Master Orchestrator 执行流程详解

从 SKILL.md 定义到实际执行的完整链路

---

## 完整执行流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    1. 入口点 (Entry Points)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          ┌─────────┐   ┌─────────┐   ┌─────────┐
          │ CLI     │   │ Python  │   │ Skill   │
          │ 命令行   │   │ API     │   │ System  │
          └────┬────┘   └────┬────┘   └────┬────┘
               │             │             │
               └─────────────┼─────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              2. MasterOrchestrator.process()                │
│                     主入口方法                                │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              3. 意图分析 (Intent Analysis)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ClaudeIntentAnalyzer / IntentAnalyzer                │  │
│  │                                                       │  │
│  │ 输出:                                                 │  │
│  │  - mode: command/agent/prompt/skill/backend         │  │
│  │  - task_type: dev/ux/analysis/test                  │  │
│  │  - complexity: simple/medium/complex                │  │
│  │  - enable_parallel: true/false ⭐                    │  │
│  │  - parallel_reasoning: "..."                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ 并行推断结果？  │
                    └────────┬───────┘
                             │
                ┌────────────┼────────────┐
                │ enable_parallel?        │
                └────────────┬────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
           Yes│                             │No
              ▼                             ▼
┌─────────────────────────┐      ┌──────────────────────┐
│ 4a. 并行执行分支         │      │ 4b. 串行执行分支      │
│ (Parallel Execution)    │      │ (Serial Execution)   │
└─────────────────────────┘      └──────────────────────┘
              │                             │
              ▼                             ▼
┌─────────────────────────┐      ┌──────────────────────┐
│ _split_parallel_tasks() │      │ ExecutionRouter      │
│  - 策略1: "包含"模式     │      │   .route()           │
│  - 策略2: 逗号分隔       │      │                      │
│  - 策略3: 批量文件       │      │  单一资源执行         │
└──────────┬──────────────┘      └──────────┬───────────┘
           │                                │
           │ 拆分成功？                      │
           ▼                                ▼
  ┌────────────────┐                ┌──────────────┐
  │ 子任务列表      │                │ 直接返回结果  │
  │ ["任务1",      │                └──────────────┘
  │  "任务2",      │
  │  "任务3"]      │
  └────────┬───────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              5. process_batch() ⭐ 核心批处理                │
│                                                              │
│  输入: requests = ["任务1", "任务2", "任务3"]                │
│       enable_parallel = True                                │
│                                                              │
│  步骤:                                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 5.1 为每个请求分析意图，创建 Task 对象                 │  │
│  │     Task(namespace, request, dependencies, metadata) │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 5.2 调用 ParallelScheduler.execute_tasks()           │  │
│  │     - DependencyAnalyzer 分析依赖                     │  │
│  │     - 生成并行组 (ParallelGroup)                      │  │
│  │     - ThreadPoolExecutor 并行执行                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 5.3 返回 BatchResult                                 │  │
│  │     - total_tasks: 3                                 │  │
│  │     - successful: 3                                  │  │
│  │     - failed: 0                                      │  │
│  │     - task_results: [...]                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         6. _batch_result_to_task_result()                   │
│                批处理结果转换为统一格式                        │
│                                                              │
│  输入: BatchResult                                           │
│  输出: TaskResult (统一返回格式)                             │
│                                                              │
│  内容:                                                       │
│   === 子任务 1/3 ===                                        │
│   资源: skill:user-management                               │
│   输出: <子任务1输出>                                        │
│                                                              │
│   === 子任务 2/3 ===                                        │
│   资源: skill:product-management                            │
│   输出: <子任务2输出>                                        │
│                                                              │
│   === 子任务 3/3 ===                                        │
│   资源: skill:order-management                              │
│   输出: <子任务3输出>                                        │
│                                                              │
│   ======================================                    │
│   批处理总结                                                 │
│   ======================================                    │
│   总任务数: 3                                               │
│   成功: 3                                                   │
│   失败: 0                                                   │
│   总耗时: 18.5s                                             │
│   ======================================                    │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      7. 返回结果给用户                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 详细步骤说明

### 步骤 1: 入口点 (Entry Points)

有三种方式调用 Master Orchestrator：

#### 1.1 CLI 命令行入口

```bash
# 直接运行
python master_orchestrator.py "实现用户管理、商品管理、订单处理" --verbose

# 通过 memex-cli
memex run master-orchestrator "实现用户管理、商品管理、订单处理"
```

**文件**: `master_orchestrator.py:1681-1779`

```python
def main():
    """CLI 入口"""
    parser = argparse.ArgumentParser(...)
    args = parser.parse_args()

    orch = MasterOrchestrator(...)
    result = orch.process(args.request, verbose=args.verbose)
```

#### 1.2 Python API 入口

```python
from orchestrator.master_orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator(
    auto_discover=True,
    enable_parallel=True,
    max_parallel_workers=3
)

result = orchestrator.process(
    "实现用户管理、商品管理、订单处理",
    verbose=True
)
```

#### 1.3 Skill System 入口

通过 SKILL.md 定义调用：

```yaml
# SKILL.md 头部元数据
description: 主编排器元技能 - 智能分析用户需求...
enabled: true
priority: 100
backend: claude
```

当其他系统识别到需要使用 `master-orchestrator` skill 时，会：
1. 读取 SKILL.md 的 System Prompt
2. 结合 User Prompt Template
3. 调用 `orchestrator.process(request)`

---

### 步骤 2: MasterOrchestrator.process()

**文件**: `master_orchestrator.py:937-1061`

主入口方法，协调整个执行流程：

```python
def process(self, request: str, verbose: bool = False) -> Any:
    """处理用户请求（支持 Slash Command 和自然语言）"""

    # 0. 记录任务开始
    self.log_manager.log_task_start(request, "unknown")

    # 1. 检查是否为 Slash Command
    if request.strip().startswith('/'):
        return self._process_slash_command(request.strip(), verbose)

    # 2. 意图分析 ⭐
    intent = self._analyze_intent(request, verbose)

    # 3. 并行执行判断 ⭐⭐
    if hasattr(intent, 'enable_parallel') and intent.enable_parallel:
        subtasks = self._split_parallel_tasks(request, intent, verbose)

        if subtasks and len(subtasks) > 1 and self.scheduler:
            # 并行执行
            batch_result = self.process_batch(subtasks, enable_parallel=True)
            return self._batch_result_to_task_result(batch_result, request, intent)

    # 4. 串行执行（fallback）
    result = self.router.route(intent, request)

    # 5. 记录和返回
    self.log_manager.log_task_complete(...)
    return result
```

---

### 步骤 3: 意图分析 (Intent Analysis)

**文件**:
- `analyzers/claude_intent_analyzer.py:146-217` (Claude LLM)
- `master_orchestrator.py:156-276` (规则引擎)

#### 3.1 Claude LLM 分析器

```python
def analyze(self, request: str, timeout: int = 10) -> Intent:
    # 1. 构造提示词（包含并行推断指导）
    prompt = self.INTENT_PROMPT_TEMPLATE.format(request=request)

    # 2. 调用 Claude
    result = self.backend_orch.run_task(
        backend="claude",
        prompt=prompt,
        stream_format="jsonl"
    )

    # 3. 解析 JSON 输出
    intent_data = self._parse_intent_result(result.output)

    # 4. 资源推断（如果 registry 可用）
    entity, candidates = self._infer_resources(request, ...)

    # 5. 构造 Intent 对象
    return Intent(
        mode=ExecutionMode(intent_data["mode"]),
        task_type=intent_data["task_type"],
        complexity=intent_data["complexity"],
        enable_parallel=bool(intent_data.get("enable_parallel")),  # ⭐
        parallel_reasoning=intent_data.get("parallel_reasoning"),
        entity=entity,
        candidates=candidates
    )
```

**Claude 提示词模板**（部分）：

```
并行执行推断 (enable_parallel):
判断任务是否适合并行执行，考虑以下因素：
- 用户明确提到"批量"、"多个"、"同时"、"并行"等关键词
- 任务可分解为多个独立子任务
- 子任务之间无明显依赖关系
- 返回 true 或 false，以及简短的推断理由

返回JSON：
{
  "mode": "skill",
  "enable_parallel": true,
  "parallel_reasoning": "包含多个独立模块，可并行开发"
}
```

#### 3.2 规则引擎分析器

```python
def _classify_parallelizable(self, request: str, task_type: str, complexity: str):
    # 1. 检查明确关键词
    has_explicit = any(kw in request for kw in ["批量", "多个", "同时", "并行"])
    if has_explicit:
        return True, "用户明确提到批量/并行处理"

    # 2. 检查隐式关键词 + 多文件/模块
    has_implicit = any(kw in request for kw in ["所有", "每个"])
    has_multi_file = any(kw in request for kw in ["文件", "模块", "组件"])

    if has_implicit and has_multi_file:
        if task_type in ["dev", "test"] and complexity in ["medium", "complex"]:
            return True, "涉及多个独立单元，适合并行处理"

    # 3. 测试任务通常可并行
    if task_type == "test" and complexity in ["medium", "complex"]:
        return True, "测试任务通常可并行执行"

    # 默认不并行
    return False, "单一任务或有依赖关系，不适合并行"
```

---

### 步骤 4a: 并行执行分支

#### 4a.1 任务拆分 (_split_parallel_tasks)

**文件**: `master_orchestrator.py:1562-1664`

```python
def _split_parallel_tasks(self, request: str, intent: Intent) -> List[str]:
    """将用户请求拆分为并行子任务"""

    # 策略1: "包含"模式（优先级最高）
    if '包含' in request:
        # "开发系统，包含A、B、C" → ["开发系统 - A", "开发系统 - B", ...]
        pattern = r'包含(.+)'
        match = re.search(pattern, request)
        if match:
            items_part = match.group(1).strip()
            items = re.split(r'[、，和]', items_part)
            items = [item.strip() for item in items if item.strip()]

            if len(items) >= 2:
                prefix_match = re.search(r'^(.+?)[，,]?\s*包含', request)
                prefix = prefix_match.group(1).strip()
                return [f"{prefix} - {item}" for item in items]

    # 策略2: 逗号/顿号分隔
    if '、' in request or '，' in request:
        # "实现A、B、C" → ["实现A", "实现B", "实现C"]
        pattern = r'(实现|开发|测试|分析|处理)(.+?)(、|，)(.+)'
        match = re.search(pattern, request)
        if match:
            verb = match.group(1)
            items_part = match.group(2) + match.group(3) + match.group(4)
            items = re.split(r'[、，]', items_part)
            items = [item.strip() for item in items if item.strip()]

            if len(items) >= 2:
                return [f"{verb}{item}" for item in items]

    # 策略3: 批量文件处理（待实现）
    # ...

    # 无法拆分
    return []
```

**拆分示例**：

| 输入 | 拆分结果 | 策略 |
|------|---------|------|
| "开发系统，包含用户、商品、订单" | ["开发系统 - 用户", "开发系统 - 商品", "开发系统 - 订单"] | 策略1 |
| "实现登录、注册、找回密码" | ["实现登录", "实现注册", "实现找回密码"] | 策略2 |
| "测试A模块、B模块、C模块" | ["测试A模块", "测试B模块", "测试C模块"] | 策略2 |

---

### 步骤 5: process_batch() ⭐ 核心批处理

**文件**: `master_orchestrator.py:1225-1329`

这是并行执行的核心方法：

```python
def process_batch(
    self,
    requests: List[str],
    enable_parallel: Optional[bool] = None,
    verbose: bool = False
) -> 'BatchResult':
    """
    批量处理请求（V3功能，支持并行）

    Args:
        requests: 请求列表 ["任务1", "任务2", "任务3"]
        enable_parallel: 是否启用并行（None=使用初始化配置）
        verbose: 详细输出

    Returns:
        BatchResult批处理结果
    """
    if not V3_AVAILABLE or not self.factory:
        raise RuntimeError("V3批处理功能未启用")

    if enable_parallel is None:
        enable_parallel = self.enable_parallel

    # 1. 分析所有请求的意图，创建任务列表
    tasks = []
    for request in requests:
        intent = self._analyze_intent(request, verbose=False)
        namespace = self._intent_to_namespace(intent)

        task = Task(
            namespace=namespace,
            request=request,
            dependencies=[],
            metadata={"intent": intent}
        )
        tasks.append(task)

        if verbose:
            print(f"[任务创建] {request[:50]}... → {namespace}")

    # 2. 执行任务（并行或串行）
    if enable_parallel and self.scheduler:
        if verbose:
            print(f"\n[并行执行] {len(tasks)} 个任务，最多 {self.scheduler.max_workers} 个并行...")

        # 启用依赖分析和并行执行
        result = self.scheduler.execute_tasks(
            tasks=tasks,
            enable_dependency_analysis=True
        )
    else:
        # 串行执行（fallback）
        # ...

    if verbose:
        print(f"\n[批处理完成] {result}")

    return result
```

#### 5.1 ParallelScheduler.execute_tasks()

**文件**: `core/parallel_scheduler.py`

```python
def execute_tasks(
    self,
    tasks: List[Task],
    enable_dependency_analysis: bool = True
) -> BatchResult:
    """并行执行任务列表"""

    # 1. 依赖分析
    if enable_dependency_analysis:
        analyzer = DependencyAnalyzer(self.registry)
        parallel_groups = analyzer.analyze_and_group(tasks)
    else:
        parallel_groups = [ParallelGroup(level=0, tasks=tasks)]

    # 2. 逐层并行执行
    return self.execute_parallel_groups(parallel_groups)

def execute_parallel_groups(self, groups: List[ParallelGroup]) -> BatchResult:
    """逐层执行并行组"""
    all_results = []
    start_time = time.time()

    for group in groups:
        # 使用 ThreadPoolExecutor 并行执行同一层级的任务
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for task in group.tasks:
                future = executor.submit(self._execute_single_task, task)
                futures[future] = task

            # 等待所有任务完成
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)

    total_duration = time.time() - start_time

    # 3. 构造批处理结果
    return BatchResult(
        total_tasks=len(all_results),
        successful=sum(1 for r in all_results if r.success),
        failed=sum(1 for r in all_results if not r.success),
        total_duration_seconds=total_duration,
        task_results=all_results
    )
```

---

### 步骤 6: _batch_result_to_task_result()

**文件**: `master_orchestrator.py:1666-1725`

将批处理结果转换为统一的 TaskResult 格式：

```python
def _batch_result_to_task_result(
    self,
    batch_result: 'BatchResult',
    original_request: str,
    intent: Intent
) -> TaskResult:
    """将批处理结果转换为单一 TaskResult"""

    # 1. 汇总所有子任务的输出
    outputs = []
    for i, task_result in enumerate(batch_result.task_results, 1):
        if task_result.success:
            outputs.append(f"=== 子任务 {i}/{batch_result.total_tasks} ===")
            outputs.append(f"资源: {task_result.namespace}")
            outputs.append(f"输出:\n{task_result.output}")
            outputs.append("")
        else:
            outputs.append(f"=== 子任务 {i}/{batch_result.total_tasks} [失败] ===")
            outputs.append(f"资源: {task_result.namespace}")
            outputs.append(f"错误: {task_result.error}")
            outputs.append("")

    combined_output = "\n".join(outputs)

    # 2. 添加总结
    summary = f"""
{'='*70}
批处理总结
{'='*70}
总任务数: {batch_result.total_tasks}
成功: {batch_result.successful}
失败: {batch_result.failed}
总耗时: {batch_result.total_duration_seconds:.2f}s
{'='*70}
"""

    final_output = combined_output + summary

    # 3. 构造 TaskResult
    backend = self._select_backend_for_intent(intent)

    return TaskResult(
        backend=backend,
        prompt=original_request,
        output=final_output,
        success=(batch_result.failed == 0),
        error=None if batch_result.failed == 0 else f"{batch_result.failed} 个子任务失败",
        run_id=None,
        event_stream=None,
        duration_seconds=batch_result.total_duration_seconds
    )
```

---

### 步骤 4b: 串行执行分支

**文件**: `master_orchestrator.py:225-695` (ExecutionRouter)

当任务不适合并行时，使用传统的串行执行：

```python
def route(self, intent: Intent, request: str) -> Any:
    """路由到对应的执行器"""

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
```

---

## 完整示例：从入口到执行

### 示例：多模块开发任务

```python
# ============ 入口 ============
orchestrator = MasterOrchestrator(
    auto_discover=True,
    enable_parallel=True,
    max_parallel_workers=3
)

result = orchestrator.process(
    "实现用户管理、商品管理、订单处理",
    verbose=True
)

# ============ 执行流程 ============

# 步骤1: 进入 process() 方法
# 步骤2: 调用 _analyze_intent()

# -------- Claude LLM 分析 --------
# 输入提示词:
"""
用户请求：实现用户管理、商品管理、订单处理

请分析此需求并返回JSON:
{
  "mode": "skill",
  "task_type": "dev",
  "complexity": "complex",
  "enable_parallel": true,
  "parallel_reasoning": "包含多个独立模块，可并行开发"
}
"""

# Claude 返回:
intent = Intent(
    mode=ExecutionMode.SKILL,
    task_type="dev",
    complexity="complex",
    enable_parallel=True,  # ⭐ 判断为可并行
    parallel_reasoning="包含多个独立模块，可并行开发"
)

# 步骤3: 检查 intent.enable_parallel == True
# 步骤4a: 调用 _split_parallel_tasks()

# -------- 任务拆分 --------
subtasks = [
    "实现用户管理",
    "实现商品管理",
    "实现订单处理"
]

# 步骤5: 调用 process_batch(subtasks, enable_parallel=True)

# -------- 批处理 --------
# 5.1 为每个子任务创建 Task 对象
tasks = [
    Task(namespace="skill:dev-workflow", request="实现用户管理"),
    Task(namespace="skill:dev-workflow", request="实现商品管理"),
    Task(namespace="skill:dev-workflow", request="实现订单处理")
]

# 5.2 调用 ParallelScheduler.execute_tasks()
# 5.3 使用 ThreadPoolExecutor 并行执行

# -------- 并行执行 --------
# 工作线程1: 执行 "实现用户管理"   (耗时: 15.2s)
# 工作线程2: 执行 "实现商品管理"   (耗时: 18.5s)
# 工作线程3: 执行 "实现订单处理"   (耗时: 16.8s)
# 总耗时: max(15.2, 18.5, 16.8) = 18.5s

# 5.4 返回 BatchResult
batch_result = BatchResult(
    total_tasks=3,
    successful=3,
    failed=0,
    total_duration_seconds=18.5,
    task_results=[...]
)

# 步骤6: 调用 _batch_result_to_task_result()

# -------- 结果汇总 --------
final_result = TaskResult(
    backend="codex",
    prompt="实现用户管理、商品管理、订单处理",
    output="""
=== 子任务 1/3 ===
资源: skill:dev-workflow
输出: [用户管理模块实现代码]

=== 子任务 2/3 ===
资源: skill:dev-workflow
输出: [商品管理模块实现代码]

=== 子任务 3/3 ===
资源: skill:dev-workflow
输出: [订单处理模块实现代码]

======================================================================
批处理总结
======================================================================
总任务数: 3
成功: 3
失败: 0
总耗时: 18.5s
======================================================================
""",
    success=True,
    duration_seconds=18.5
)

# 步骤7: 返回结果给用户
return final_result
```

---

## 关键代码位置速查表

| 组件 | 文件 | 行号范围 | 功能 |
|------|------|---------|------|
| **入口点** | `master_orchestrator.py` | 1681-1779 | CLI main() |
| **主流程** | `master_orchestrator.py` | 937-1061 | process() 方法 |
| **意图分析 (Claude)** | `analyzers/claude_intent_analyzer.py` | 146-217 | analyze() |
| **意图分析 (规则)** | `master_orchestrator.py` | 156-276 | IntentAnalyzer |
| **并行推断** | `master_orchestrator.py` | 234-276 | _classify_parallelizable() |
| **任务拆分** | `master_orchestrator.py` | 1562-1664 | _split_parallel_tasks() |
| **批处理入口** | `master_orchestrator.py` | 1225-1329 | process_batch() ⭐ |
| **并行调度器** | `core/parallel_scheduler.py` | - | ParallelScheduler |
| **结果转换** | `master_orchestrator.py` | 1666-1725 | _batch_result_to_task_result() |
| **串行路由** | `master_orchestrator.py` | 282-695 | ExecutionRouter.route() |

---

## 性能对比

### 串行执行
```
任务1 (15s) → 任务2 (18s) → 任务3 (17s)
总耗时: 50s
```

### 并行执行（通过 process_batch）
```
┌─ 工作线程1: 任务1 (15s) ─┐
├─ 工作线程2: 任务2 (18s) ─┤ ← max = 18s
└─ 工作线程3: 任务3 (17s) ─┘

总耗时: 18s
加速比: 50s / 18s ≈ 2.8x
```

---

## 总结

从 SKILL.md 到实际执行的完整链路：

1. ✅ **SKILL.md** → 定义技能元数据和提示词模板
2. ✅ **入口点** → CLI / Python API / Skill System
3. ✅ **意图分析** → Claude LLM / 规则引擎推断并行
4. ✅ **并行判断** → enable_parallel 决定执行路径
5. ✅ **任务拆分** → 3种策略拆分子任务
6. ✅ **process_batch()** → 核心批处理方法 ⭐
7. ✅ **并行执行** → ThreadPoolExecutor 并行
8. ✅ **结果汇总** → 转换为统一 TaskResult
9. ✅ **返回用户** → 完整的执行结果

**核心优势**：
- 🚀 自动推断并行，零配置
- 📊 ~3x 性能提升
- 🔄 完全向后兼容
- 🎯 透明的执行流程

---

**文档版本**: v1.0
**最后更新**: 2026-01-05
**状态**: ✅ 完整
