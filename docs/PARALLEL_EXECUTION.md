# MasterOrchestrator V3 - 并行执行系统

## 概述

MasterOrchestrator V3 提供了智能并行执行能力，可以自动识别独立任务并并行执行，显著提升执行效率。

**核心特性**：
- ⚡ **智能依赖分析**：自动识别任务依赖关系
- 🔀 **分层并行执行**：按依赖层级组织并行任务
- 🔍 **循环依赖检测**：启动时检测并报告循环依赖
- ⏱️ **超时控制**：独立的任务级超时管理
- 🛡️ **错误隔离**：单个任务失败不影响其他任务
- 📊 **详细结果收集**：统计成功率、耗时等指标

---

## 快速开始

### 1. 启用并行执行

```python
from orchestrator import MasterOrchestrator

# 启用自动发现和并行执行
orch = MasterOrchestrator(
    auto_discover=True,        # 必须启用自动发现
    enable_parallel=True,      # 启用并行执行
    max_parallel_workers=3,    # 最大并行数
    parallel_timeout=120       # 单任务超时（秒）
)

# 批量处理请求
requests = [
    "查看 git 状态",
    "分析代码质量",
    "生成 API 文档"
]

result = orch.process_batch(requests, enable_parallel=True, verbose=True)

# 查看结果
print(f"总任务: {result.total_tasks}")
print(f"成功: {result.successful}")
print(f"失败: {result.failed}")
print(f"成功率: {result.success_rate:.1%}")
print(f"总耗时: {result.total_duration_seconds:.2f}s")
```

**输出示例**：
```
[任务创建] 查看 git 状态 → command:default
[任务创建] 分析代码质量 → skill:code-analyzer
[任务创建] 生成 API 文档 → prompt:api-doc

[并行执行] 3 个任务，最多 3 个并行...

总任务: 3
成功: 3
失败: 0
成功率: 100.0%
总耗时: 5.23s
```

---

## 并行执行模式

### 模式 1: 批量并行处理

**适用场景**：多个独立任务需要并发执行

```python
orch = MasterOrchestrator(
    auto_discover=True,
    enable_parallel=True,
    max_parallel_workers=5
)

# 多个独立的代码分析任务
files_to_analyze = [
    "分析 src/main.py 代码质量",
    "分析 src/utils.py 代码质量",
    "分析 src/models.py 代码质量",
    "分析 src/views.py 代码质量",
    "分析 src/tests.py 代码质量"
]

# 并行执行（最多5个同时）
result = orch.process_batch(files_to_analyze, enable_parallel=True)

# 5个任务并行 vs 串行：
# 并行: ~12s (假设每个任务10s，5个并行执行)
# 串行: ~50s (5个任务依次执行)
# 加速比: 4.2x
```

### 模式 2: DevWorkflow 并行工作流

**适用场景**：多阶段开发流程，部分阶段可并行

```python
from orchestrator.skills.dev_workflow import DevWorkflowAgent

# 启用并行工作流
agent = DevWorkflowAgent(
    parse_events=True,
    timeout=600,
    enable_parallel=True,    # 启用并行
    max_workers=2            # 同时执行2个阶段
)

result = agent.run("创建在线课程平台", verbose=True)

# 执行层级：
# Level 0: [REQUIREMENTS]                    单独执行 (~15s)
# Level 1: [FEATURE_DESIGN, UX_DESIGN]       并行执行 (~15s, 原本需要30s)
# Level 2: [DEV_PLAN]                        单独执行 (~10s)
# Level 3: [IMPLEMENTATION]                  单独执行 (~20s)
#
# 总耗时: ~60s (串行需要~90s, 节省33%)
```

---

## 依赖分析

### 自动依赖解析

系统会自动分析任务间的依赖关系：

```python
from orchestrator.core.dependency_analyzer import DependencyAnalyzer, Task

# 创建任务
tasks = [
    Task(namespace="command:git-status", request="查看状态", dependencies=[]),
    Task(namespace="skill:code-review", request="代码审查", dependencies=["command:git-diff"]),
    Task(namespace="skill:test-gen", request="生成测试", dependencies=["skill:code-review"])
]

# 分析依赖
analyzer = DependencyAnalyzer(registry=None)
groups = analyzer.group_parallel_tasks(tasks)

# 结果分层：
# Level 0: [command:git-status]              独立执行
# Level 1: [command:git-diff]                依赖 Level 0
# Level 2: [skill:code-review]               依赖 Level 1
# Level 3: [skill:test-gen]                  依赖 Level 2
```

### 依赖图可视化

```python
# 构建依赖图
graph = analyzer.build_task_graph(tasks)

# 输出依赖关系
for task_ns, deps in graph.items():
    if deps:
        print(f"{task_ns} 依赖于:")
        for dep in deps:
            print(f"  - {dep}")
    else:
        print(f"{task_ns} (无依赖)")
```

**输出**：
```
command:git-status (无依赖)
skill:code-review 依赖于:
  - command:git-diff
skill:test-gen 依赖于:
  - skill:code-review
```

---

## 拓扑排序

### Kahn 算法分层

系统使用 Kahn 算法对任务进行拓扑排序并分层：

```python
# 依赖图
graph = {
    "A": set(),          # 无依赖
    "B": {"A"},          # 依赖 A
    "C": {"A"},          # 依赖 A（可与 B 并行）
    "D": {"B", "C"},     # 依赖 B 和 C
}

# 拓扑排序
levels = analyzer.topological_sort(graph)

# 结果：
# [["A"], ["B", "C"], ["D"]]
#   ↑      ↑           ↑
#  层0    层1         层2
#       (B和C并行)
```

### 并行组生成

```python
from orchestrator.core.dependency_analyzer import ParallelGroup

# 分组并行任务
groups = analyzer.group_parallel_tasks(tasks)

for group in groups:
    print(f"Level {group.level}: {len(group.tasks)} 个任务")
    if len(group.tasks) > 1:
        print(f"  [并行] {[t.namespace for t in group.tasks]}")
    else:
        print(f"  [串行] {group.tasks[0].namespace}")
```

**输出**：
```
Level 0: 1 个任务
  [串行] command:git-status

Level 1: 2 个任务
  [并行] ['skill:feature-design', 'skill:ux-design']

Level 2: 1 个任务
  [串行] skill:dev-plan
```

---

## 并行调度器

### ThreadPoolExecutor 管理

```python
from orchestrator.core.parallel_scheduler import ParallelScheduler
from orchestrator.core.executor_factory import ExecutorFactory

# 创建调度器
scheduler = ParallelScheduler(
    factory=executor_factory,
    max_workers=3,           # 最多3个并行线程
    timeout_per_task=120,    # 单任务超时120秒
    fail_fast=False          # 不快速失败
)

# 执行并行组
result = scheduler.execute_parallel_groups(groups)

# 结果
print(f"总任务: {result.total_tasks}")
print(f"成功: {result.successful}")
print(f"失败: {result.failed}")
print(f"总耗时: {result.total_duration_seconds:.2f}s")
```

### 分层执行流程

```
Level 0: [Task A]
    ↓ 执行完成
Level 1: [Task B, Task C]  ← ThreadPoolExecutor(max_workers=2)
    ↓ 两个任务并行执行
Level 2: [Task D]
    ↓ 执行完成
完成
```

### 错误隔离

```python
# 错误隔离：Task B 失败不影响 Task C

# Level 1 执行:
with ThreadPoolExecutor(max_workers=2) as executor:
    future_B = executor.submit(execute_task, task_B)
    future_C = executor.submit(execute_task, task_C)

    # Task B 失败，Task C 继续执行
    try:
        result_B = future_B.result(timeout=120)
    except Exception as e:
        print(f"Task B 失败: {e}")
        # 记录失败，继续

    result_C = future_C.result(timeout=120)  # Task C 正常完成
```

---

## 配置并行执行

### 全局配置

在 `orchestrator.yaml` 中配置：

```yaml
version: "3.0"

# 并行执行配置
parallel:
  enabled: true              # 全局启用并行
  max_workers: 3             # 最大并行线程数
  timeout_per_task: 120      # 单任务超时（秒）
  allowed_modes:             # 允许并行的模式
    - command
    - backend
  sequential_modes:          # 必须串行的模式
    - skill
```

### 运行时覆盖

```python
# 初始化时禁用
orch = MasterOrchestrator(enable_parallel=False)

# 运行时启用
result = orch.process_batch(
    requests,
    enable_parallel=True,  # 覆盖初始化配置
    verbose=True
)
```

### Per-Resource 配置

```yaml
skills:
  manual:
    - name: heavy-task
      path: ./skills/heavy-task.yaml
      priority: 100
      # 该 Skill 总是串行执行
      parallel: false
```

---

## 性能优化

### 最佳并行数

根据任务类型选择合适的 `max_workers`：

| 任务类型 | 推荐 max_workers | 原因 |
|---------|-----------------|------|
| CPU 密集 | CPU 核心数 | 避免过度竞争 |
| IO 密集 | CPU 核心数 × 2-4 | IO 等待时可处理更多任务 |
| API 调用 | 3-5 | 避免触发速率限制 |
| 混合任务 | CPU 核心数 × 2 | 平衡 CPU 和 IO |

**示例**：
```python
import os

# CPU 密集任务
max_workers = os.cpu_count()  # 如 8 核 → 8 workers

# IO 密集任务（API 调用）
max_workers = min(os.cpu_count() * 2, 10)  # 8 核 → 10 workers (限制上限)
```

### 超时配置

```python
# 根据任务类型设置超时
scheduler = ParallelScheduler(
    factory=factory,
    max_workers=3,
    timeout_per_task=60,     # 轻量级任务：60s
    # timeout_per_task=300,  # 重量级任务：300s
)
```

### 批次大小

```python
# 大量任务时分批处理
def process_in_batches(requests, batch_size=10):
    results = []
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i+batch_size]
        result = orch.process_batch(batch, enable_parallel=True)
        results.append(result)
    return results

# 100 个任务，每批 10 个
all_results = process_in_batches(requests, batch_size=10)
```

---

## 循环依赖检测

### 自动检测

系统会在任务执行前检测循环依赖：

```python
# 检测循环依赖
cycles = analyzer.detect_cycles(dependency_graph)

if cycles:
    print(f"检测到 {len(cycles)} 个循环依赖:")
    for cycle in cycles:
        print(f"  {' → '.join(cycle)}")
    raise CyclicDependencyError("存在循环依赖")
```

**示例**：
```
检测到 1 个循环依赖:
  skill:A → skill:B → skill:C → skill:A
```

### 解决循环依赖

**错误的依赖**：
```yaml
# skill-a.yaml
dependencies: ["skill:skill-b"]

# skill-b.yaml
dependencies: ["skill:skill-c"]

# skill-c.yaml
dependencies: ["skill:skill-a"]  # ← 形成循环
```

**正确的重构**：
```yaml
# 引入共享 Skill
# skill-common.yaml (无依赖)

# skill-a.yaml
dependencies: ["skill:skill-common"]

# skill-b.yaml
dependencies: ["skill:skill-common"]

# skill-c.yaml
dependencies: ["skill:skill-common"]
```

---

## 结果收集

### BatchResult 结构

```python
@dataclass
class BatchResult:
    total_tasks: int              # 总任务数
    successful: int               # 成功数
    failed: int                   # 失败数
    total_duration_seconds: float # 总耗时
    task_results: List[TaskResult]# 详细结果
    metadata: Dict[str, Any]      # 元数据

    @property
    def success_rate(self) -> float:
        """成功率 (0.0-1.0)"""
        return self.successful / self.total_tasks if self.total_tasks > 0 else 0.0
```

### TaskResult 结构

```python
@dataclass
class TaskResult:
    namespace: str                # 资源命名空间
    success: bool                 # 是否成功
    output: Any                   # 输出结果
    error: Optional[str]          # 错误信息
    duration_seconds: float       # 耗时
    executed_at: datetime         # 执行时间
    metadata: Dict[str, Any]      # 元数据
```

### 结果分析

```python
result = orch.process_batch(requests, enable_parallel=True)

# 统计信息
print(f"成功率: {result.success_rate:.1%}")
print(f"平均耗时: {result.total_duration_seconds / result.total_tasks:.2f}s")

# 查看失败任务
failed_tasks = [r for r in result.task_results if not r.success]
for task in failed_tasks:
    print(f"失败: {task.namespace}")
    print(f"  错误: {task.error}")

# 查看最慢任务
sorted_tasks = sorted(result.task_results, key=lambda x: x.duration_seconds, reverse=True)
print(f"最慢任务: {sorted_tasks[0].namespace} ({sorted_tasks[0].duration_seconds:.2f}s)")
```

---

## DevWorkflow 并行模式

### 阶段依赖关系

```python
STAGE_DEPENDENCIES = {
    WorkflowStage.REQUIREMENTS: [],
    WorkflowStage.FEATURE_DESIGN: [WorkflowStage.REQUIREMENTS],
    WorkflowStage.UX_DESIGN: [WorkflowStage.REQUIREMENTS],     # ← 与 FEATURE_DESIGN 并行
    WorkflowStage.DEV_PLAN: [WorkflowStage.FEATURE_DESIGN, WorkflowStage.UX_DESIGN],
    WorkflowStage.IMPLEMENTATION: [WorkflowStage.DEV_PLAN]
}
```

### 执行流程

```
REQUIREMENTS (Level 0)
    ↓
    ├─ FEATURE_DESIGN (Level 1) ┐
    └─ UX_DESIGN (Level 1)      ├─ 并行执行
                                ┘
    ↓
DEV_PLAN (Level 2)
    ↓
IMPLEMENTATION (Level 3)
```

### 使用示例

```python
from orchestrator.skills.dev_workflow import DevWorkflowAgent

# 并行模式
agent = DevWorkflowAgent(
    enable_parallel=True,
    max_workers=2
)

result = agent.run("创建电商平台", verbose=True)

# 输出示例：
# [并行模式] 启用 V3 并行执行
# 最大并行数: 2
#
# [依赖分析] 识别出 4 个执行层级：
#   Level 0: ['requirements']
#   Level 1: ['feature_design', 'ux_design']
#   Level 2: ['dev_plan']
#   Level 3: ['implementation']
#
# ============================================================
# 执行 Level 1: 2 个阶段
# [并行] ['feature_design', 'ux_design']
# ============================================================
#
# [feature_design]
#   后端: claude
#   耗时: 15.23s
#   [OK] 验证通过
#
# [ux_design]
#   后端: gemini
#   耗时: 14.87s
#   [OK] 验证通过
```

---

## 高级用法

### 自定义依赖关系

```python
from orchestrator.core.dependency_analyzer import Task

# 定义自定义依赖
tasks = [
    Task(
        namespace="skill:step1",
        request="步骤1",
        dependencies=[]  # 无依赖
    ),
    Task(
        namespace="skill:step2",
        request="步骤2",
        dependencies=["skill:step1"]  # 依赖步骤1
    ),
    Task(
        namespace="skill:step3",
        request="步骤3",
        dependencies=["skill:step1"]  # 也依赖步骤1（可与步骤2并行）
    ),
]

# 执行
scheduler.execute_tasks(tasks, enable_dependency_analysis=True)
```

### 动态调整并行度

```python
# 根据系统负载动态调整
import psutil

def get_optimal_workers():
    cpu_usage = psutil.cpu_percent()
    if cpu_usage > 80:
        return 2  # 高负载，减少并行
    elif cpu_usage > 50:
        return 3  # 中负载
    else:
        return 5  # 低负载，增加并行

scheduler = ParallelScheduler(
    factory=factory,
    max_workers=get_optimal_workers()
)
```

### 条件并行

```python
# 只在特定条件下并行
def should_parallel(requests):
    # 少于3个任务不值得并行
    if len(requests) < 3:
        return False
    # 任务类型都是 IO 密集，适合并行
    return all("api" in req or "fetch" in req for req in requests)

enable_parallel = should_parallel(requests)
result = orch.process_batch(requests, enable_parallel=enable_parallel)
```

---

## 故障排查

### 问题 1: 并行未生效

**症状**：`enable_parallel=True` 但任务仍串行执行

**诊断**：
```python
# 检查 auto_discover 是否启用
print(orch.auto_discover)  # 应为 True

# 检查 V3 组件是否可用
from orchestrator.core.parallel_scheduler import ParallelScheduler
print(ParallelScheduler is not None)  # 应为 True

# 检查任务依赖
analyzer = DependencyAnalyzer(orch.registry)
groups = analyzer.group_parallel_tasks(tasks)
for group in groups:
    print(f"Level {group.level}: {len(group.tasks)} tasks")
    # 如果每个 Level 只有 1 个任务，说明存在强依赖链
```

### 问题 2: 性能未提升

**原因分析**：
1. 任务间存在依赖链（无法并行）
2. 任务数量少（并行开销大于收益）
3. `max_workers` 设置过小

**解决**：
```python
# 1. 检查依赖关系
stats = analyzer.get_stats(tasks)
print(f"独立任务: {stats['independent_tasks']}/{stats['total_tasks']}")

# 2. 增加 max_workers
scheduler = ParallelScheduler(factory=factory, max_workers=5)  # 增加到5

# 3. 批量处理
if len(requests) < 5:
    # 少量任务，串行更快
    result = orch.process_batch(requests, enable_parallel=False)
```

### 问题 3: 超时错误

**症状**：`Task timeout after 120s`

**解决**：
```python
# 增加超时时间
scheduler = ParallelScheduler(
    factory=factory,
    max_workers=3,
    timeout_per_task=300  # 增加到5分钟
)

# 或针对特定任务调整
orch = MasterOrchestrator(
    enable_parallel=True,
    parallel_timeout=300  # 全局超时设置
)
```

---

## 性能基准

### 测试场景

**场景 1**: 5 个独立 API 调用任务

| 模式 | 耗时 | 加速比 |
|------|------|--------|
| 串行 | 50s | 1.0x |
| 并行 (workers=3) | 20s | 2.5x |
| 并行 (workers=5) | 12s | 4.2x |

**场景 2**: DevWorkflow 5 阶段

| 模式 | 耗时 | 加速比 |
|------|------|--------|
| 串行 | 90s | 1.0x |
| 并行 (workers=2) | 60s | 1.5x |

**场景 3**: 10 个 CPU 密集任务（4核CPU）

| 模式 | 耗时 | 加速比 |
|------|------|--------|
| 串行 | 100s | 1.0x |
| 并行 (workers=4) | 30s | 3.3x |
| 并行 (workers=8) | 28s | 3.6x (边际递减) |

---

## 最佳实践

### 1. 何时使用并行

✅ **适合并行**：
- 多个独立的 API 调用
- 批量文件处理
- 多个独立的代码分析任务
- DevWorkflow 的 FEATURE_DESIGN + UX_DESIGN

❌ **不适合并行**：
- 任务间有强依赖关系
- 单个任务（并行开销大于收益）
- CPU 密集 + workers 超过 CPU 核心数
- 有严格顺序要求的任务

### 2. max_workers 设置

```python
import os

# CPU 密集任务
max_workers = os.cpu_count()

# IO 密集任务（如 API 调用）
max_workers = os.cpu_count() * 2

# 限制上限（避免过度并行）
max_workers = min(max_workers, 10)

# 考虑速率限制
# 如果 API 限制 5 req/s，设置 max_workers=5
```

### 3. 错误处理

```python
# 启用详细日志
result = orch.process_batch(requests, enable_parallel=True, verbose=True)

# 检查失败任务
if result.failed > 0:
    print(f"失败任务数: {result.failed}")
    for task_result in result.task_results:
        if not task_result.success:
            print(f"  {task_result.namespace}: {task_result.error}")

# 失败快速策略
scheduler = ParallelScheduler(
    factory=factory,
    max_workers=3,
    fail_fast=True  # 第一个失败时终止
)
```

### 4. 资源管理

```python
# 使用上下文管理器
with MasterOrchestrator(
    auto_discover=True,
    enable_parallel=True
) as orch:
    result = orch.process_batch(requests)
    # 自动清理资源
```

---

## API 参考

### MasterOrchestrator

```python
def process_batch(
    self,
    requests: List[str],
    enable_parallel: Optional[bool] = None,
    verbose: bool = False
) -> BatchResult:
    """批量处理请求（支持并行）"""
    pass
```

### ParallelScheduler

```python
class ParallelScheduler:
    def __init__(
        self,
        factory: ExecutorFactory,
        max_workers: int = 3,
        timeout_per_task: int = 120,
        fail_fast: bool = False
    ):
        pass

    def execute_parallel_groups(
        self,
        groups: List[ParallelGroup],
        fail_fast: Optional[bool] = None
    ) -> BatchResult:
        """执行并行组"""
        pass

    def execute_tasks(
        self,
        tasks: List[Task],
        enable_dependency_analysis: bool = True
    ) -> BatchResult:
        """执行任务列表"""
        pass
```

### DependencyAnalyzer

```python
class DependencyAnalyzer:
    def group_parallel_tasks(self, tasks: List[Task]) -> List[ParallelGroup]:
        """分组并行任务"""
        pass

    def topological_sort(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """拓扑排序"""
        pass

    def detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """检测循环依赖"""
        pass
```

---

## 相关文档

- [自动发现文档](./AUTO_DISCOVERY.md)
- [架构文档](./ARCHITECTURE.md)
- [配置模板](../orchestrator.yaml)

---

**最后更新**: 2026-01-04
**版本**: 3.0.0
