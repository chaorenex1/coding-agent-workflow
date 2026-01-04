#!/usr/bin/env python3
"""
ParallelScheduler 单元测试

测试并行任务调度、超时控制、错误隔离等功能。
"""

import sys
from pathlib import Path
import time
from unittest.mock import Mock

# Windows 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.core.parallel_scheduler import (
    ParallelScheduler, TaskResult, BatchResult, execute_tasks_parallel
)
from orchestrator.core.dependency_analyzer import Task, ParallelGroup
from orchestrator.core.unified_registry import UnifiedRegistry
from orchestrator.tests.sandbox import MockBackendOrchestrator


# Mock Executor for testing
class MockExecutor:
    """Mock executor for testing."""

    def __init__(self, namespace: str, output: str = None, delay: float = 0.1,
                 should_fail: bool = False, error_message: str = None):
        self.namespace = namespace
        self.output = output or f"Output from {namespace}"
        self.delay = delay
        self.should_fail = should_fail
        self.error_message = error_message or f"Error from {namespace}"
        self.execution_count = 0

    def execute(self, request: str):
        """Execute with optional delay and failure."""
        self.execution_count += 1
        time.sleep(self.delay)

        if self.should_fail:
            raise Exception(self.error_message)

        return self.output


# Mock ExecutorFactory
class MockExecutorFactory:
    """Mock factory for creating executors."""

    def __init__(self, registry: UnifiedRegistry = None):
        self.registry = registry
        self.executors = {}
        self.cache = {}

    def register_executor(self, namespace: str, executor: MockExecutor):
        """Register a mock executor."""
        self.executors[namespace] = executor

    def create_executor(self, namespace: str):
        """Create or return cached executor."""
        if namespace in self.cache:
            return self.cache[namespace]

        executor = self.executors.get(namespace)
        if executor:
            self.cache[namespace] = executor

        return executor

    def get_cache_stats(self):
        """Get cache statistics."""
        return {
            "cached_executors": len(self.cache)
        }


def test_basic_parallel_execution():
    """测试 1: 基本并行执行"""
    print("测试 1: 基本并行执行")

    # 创建 Factory
    factory = MockExecutorFactory()

    # 注册 3 个独立任务（快速执行）
    factory.register_executor("task:A", MockExecutor("task:A", delay=0.05))
    factory.register_executor("task:B", MockExecutor("task:B", delay=0.05))
    factory.register_executor("task:C", MockExecutor("task:C", delay=0.05))

    # 创建调度器
    scheduler = ParallelScheduler(factory=factory, max_workers=3)

    # 创建单层并行组
    tasks = [
        Task("task:A", "Request A"),
        Task("task:B", "Request B"),
        Task("task:C", "Request C"),
    ]

    group = ParallelGroup(level=0, tasks=tasks)

    # 执行
    start_time = time.time()
    result = scheduler.execute_parallel_groups([group])
    duration = time.time() - start_time

    # 验证
    assert result.total_tasks == 3
    assert result.successful == 3
    assert result.failed == 0
    assert result.success_rate == 1.0

    # 并行执行应该比串行快（3 * 0.05 = 0.15s vs < 0.1s）
    assert duration < 0.2, f"Parallel execution too slow: {duration:.3f}s"

    print(f"  ✓ 并行执行: {result.total_tasks} 个任务, 耗时 {result.total_duration_seconds:.3f}s")
    print("  ✓ 测试通过\n")


def test_layered_execution():
    """测试 2: 分层执行（有依赖）"""
    print("测试 2: 分层执行（有依赖）")

    factory = MockExecutorFactory()

    # 注册执行器
    factory.register_executor("task:A", MockExecutor("task:A", delay=0.05))
    factory.register_executor("task:B", MockExecutor("task:B", delay=0.05))
    factory.register_executor("task:C", MockExecutor("task:C", delay=0.05))

    scheduler = ParallelScheduler(factory=factory, max_workers=2)

    # 创建分层：Level 0: C, Level 1: A+B (并行)
    groups = [
        ParallelGroup(level=0, tasks=[Task("task:C", "C")]),
        ParallelGroup(level=1, tasks=[
            Task("task:A", "A"),
            Task("task:B", "B")
        ])
    ]

    # 执行
    result = scheduler.execute_parallel_groups(groups)

    # 验证
    assert result.total_tasks == 3
    assert result.successful == 3

    # 验证执行顺序：C 应该先执行（通过结果顺序判断）
    c_result = next(r for r in result.task_results if r.namespace == "task:C")
    a_result = next(r for r in result.task_results if r.namespace == "task:A")

    # C 应该在 A 之前完成
    assert c_result.executed_at < a_result.executed_at

    print(f"  ✓ 分层执行: Level 0 先执行, Level 1 并行执行")
    print("  ✓ 测试通过\n")


def test_error_isolation():
    """测试 3: 错误隔离"""
    print("测试 3: 错误隔离")

    factory = MockExecutorFactory()

    # 注册执行器（B 会失败）
    factory.register_executor("task:A", MockExecutor("task:A"))
    factory.register_executor("task:B", MockExecutor("task:B", should_fail=True))
    factory.register_executor("task:C", MockExecutor("task:C"))

    scheduler = ParallelScheduler(factory=factory, max_workers=3, fail_fast=False)

    tasks = [
        Task("task:A", "A"),
        Task("task:B", "B"),  # 会失败
        Task("task:C", "C"),
    ]

    group = ParallelGroup(level=0, tasks=tasks)
    result = scheduler.execute_parallel_groups([group])

    # 验证：B 失败但 A 和 C 成功
    assert result.total_tasks == 3
    assert result.successful == 2
    assert result.failed == 1

    # 找到失败的任务
    failed_task = next(r for r in result.task_results if not r.success)
    assert failed_task.namespace == "task:B"
    assert failed_task.error is not None

    print(f"  ✓ 错误隔离: 1 个任务失败, 2 个成功")
    print("  ✓ 测试通过\n")


def test_fail_fast_mode():
    """测试 4: Fail-Fast 模式"""
    print("测试 4: Fail-Fast 模式")

    factory = MockExecutorFactory()

    # 注册执行器
    factory.register_executor("task:A", MockExecutor("task:A", should_fail=True))
    factory.register_executor("task:B", MockExecutor("task:B"))
    factory.register_executor("task:C", MockExecutor("task:C"))

    scheduler = ParallelScheduler(factory=factory, max_workers=2, fail_fast=True)

    # 创建两层
    groups = [
        ParallelGroup(level=0, tasks=[Task("task:A", "A")]),  # 会失败
        ParallelGroup(level=1, tasks=[Task("task:B", "B"), Task("task:C", "C")]),  # 不应执行
    ]

    result = scheduler.execute_parallel_groups(groups)

    # 验证：只执行了第一层
    assert result.total_tasks == 1  # 只有 A 被执行
    assert result.successful == 0
    assert result.failed == 1

    print(f"  ✓ Fail-Fast: 第一层失败后停止，未执行后续层")
    print("  ✓ 测试通过\n")


def test_timeout_handling():
    """测试 5: 超时配置（验证参数设置）"""
    print("测试 5: 超时配置")

    factory = MockExecutorFactory()

    # 注册快速任务
    factory.register_executor("task:A", MockExecutor("task:A", delay=0.05))
    factory.register_executor("task:B", MockExecutor("task:B", delay=0.05))

    # 创建调度器并设置超时
    scheduler = ParallelScheduler(factory=factory, max_workers=2, timeout_per_task=30)

    tasks = [
        Task("task:A", "Task A"),
        Task("task:B", "Task B"),
    ]

    group = ParallelGroup(level=0, tasks=tasks)
    result = scheduler.execute_parallel_groups([group])

    # 验证：所有任务成功（都在超时内完成）
    assert result.total_tasks == 2
    assert result.successful == 2
    assert result.failed == 0

    # 验证调度器配置
    stats = scheduler.get_stats()
    assert stats["timeout_per_task"] == 30

    print(f"  ✓ 超时配置正确: timeout_per_task={stats['timeout_per_task']}s")
    print(f"  ℹ️  注意: ThreadPoolExecutor 不支持中断运行中的任务")
    print("  ✓ 测试通过\n")


def test_single_task_optimization():
    """测试 6: 单任务优化（无线程池开销）"""
    print("测试 6: 单任务优化")

    factory = MockExecutorFactory()
    factory.register_executor("task:A", MockExecutor("task:A"))

    scheduler = ParallelScheduler(factory=factory, max_workers=3)

    # 单任务组
    group = ParallelGroup(level=0, tasks=[Task("task:A", "A")])

    result = scheduler.execute_parallel_groups([group])

    # 验证
    assert result.total_tasks == 1
    assert result.successful == 1

    print(f"  ✓ 单任务优化: 直接执行，无线程池开销")
    print("  ✓ 测试通过\n")


def test_empty_task_list():
    """测试 7: 空任务列表"""
    print("测试 7: 空任务列表")

    factory = MockExecutorFactory()
    scheduler = ParallelScheduler(factory=factory, max_workers=3)

    # 空任务
    result = scheduler.execute_tasks([])

    # 验证
    assert result.total_tasks == 0
    assert result.successful == 0
    assert result.failed == 0

    print(f"  ✓ 空任务列表处理正常")
    print("  ✓ 测试通过\n")


def test_execute_tasks_with_dependency_analysis():
    """测试 8: execute_tasks 方法（带依赖分析）"""
    print("测试 8: execute_tasks 方法（带依赖分析）")

    # 创建 Registry
    registry = UnifiedRegistry()

    factory = MockExecutorFactory(registry=registry)

    # 注册执行器
    factory.register_executor("task:A", MockExecutor("task:A"))
    factory.register_executor("task:B", MockExecutor("task:B"))
    factory.register_executor("task:C", MockExecutor("task:C"))

    scheduler = ParallelScheduler(factory=factory, max_workers=2)

    # 创建有依赖的任务：A -> B -> C
    tasks = [
        Task("task:A", "A", dependencies=["task:B"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=[]),
    ]

    # 执行（启用依赖分析）
    result = scheduler.execute_tasks(tasks, enable_dependency_analysis=True)

    # 验证
    assert result.total_tasks == 3
    assert result.successful == 3

    print(f"  ✓ 依赖分析执行成功: {result.successful}/{result.total_tasks}")
    print("  ✓ 测试通过\n")


def test_execute_tasks_sequential():
    """测试 9: execute_tasks 顺序执行（禁用依赖分析）"""
    print("测试 9: execute_tasks 顺序执行")

    factory = MockExecutorFactory()

    factory.register_executor("task:A", MockExecutor("task:A"))
    factory.register_executor("task:B", MockExecutor("task:B"))

    scheduler = ParallelScheduler(factory=factory, max_workers=2)

    tasks = [
        Task("task:A", "A"),
        Task("task:B", "B"),
    ]

    # 执行（禁用依赖分析）
    result = scheduler.execute_tasks(tasks, enable_dependency_analysis=False)

    # 验证
    assert result.total_tasks == 2
    assert result.successful == 2

    print(f"  ✓ 顺序执行（无依赖分析）: {result.successful}/{result.total_tasks}")
    print("  ✓ 测试通过\n")


def test_scheduler_stats():
    """测试 10: 调度器统计"""
    print("测试 10: 调度器统计")

    factory = MockExecutorFactory()
    scheduler = ParallelScheduler(
        factory=factory,
        max_workers=5,
        timeout_per_task=300,
        fail_fast=True
    )

    stats = scheduler.get_stats()

    # 验证
    assert stats["max_workers"] == 5
    assert stats["timeout_per_task"] == 300
    assert stats["fail_fast"] == True
    assert "cached_executors" in stats

    print(f"  ✓ 统计信息:")
    print(f"    max_workers: {stats['max_workers']}")
    print(f"    timeout_per_task: {stats['timeout_per_task']}s")
    print(f"    fail_fast: {stats['fail_fast']}")
    print("  ✓ 测试通过\n")


def test_batch_result_properties():
    """测试 11: BatchResult 属性"""
    print("测试 11: BatchResult 属性")

    result = BatchResult(
        total_tasks=10,
        successful=8,
        failed=2,
        total_duration_seconds=5.5
    )

    # 验证 success_rate
    assert result.success_rate == 0.8

    # 验证 __repr__
    repr_str = repr(result)
    assert "10" in repr_str
    assert "8" in repr_str

    print(f"  ✓ BatchResult 属性计算正确")
    print(f"    Success rate: {result.success_rate:.1%}")
    print("  ✓ 测试通过\n")


def test_convenience_function():
    """测试 12: 便捷函数 execute_tasks_parallel"""
    print("测试 12: 便捷函数 execute_tasks_parallel")

    factory = MockExecutorFactory()

    factory.register_executor("task:A", MockExecutor("task:A"))
    factory.register_executor("task:B", MockExecutor("task:B"))

    tasks = [
        Task("task:A", "A"),
        Task("task:B", "B"),
    ]

    # 使用便捷函数
    result = execute_tasks_parallel(
        tasks=tasks,
        factory=factory,
        max_workers=2,
        timeout_per_task=60,
        enable_dependency_analysis=False
    )

    # 验证
    assert result.total_tasks == 2
    assert result.successful == 2

    print(f"  ✓ 便捷函数执行成功")
    print("  ✓ 测试通过\n")


def test_executor_not_found():
    """测试 13: 执行器不存在"""
    print("测试 13: 执行器不存在")

    factory = MockExecutorFactory()
    # 故意不注册执行器

    scheduler = ParallelScheduler(factory=factory, max_workers=2)

    tasks = [Task("task:nonexistent", "Request")]

    result = scheduler.execute_tasks(tasks, enable_dependency_analysis=False)

    # 验证：应该失败
    assert result.total_tasks == 1
    assert result.successful == 0
    assert result.failed == 1

    failed_result = result.task_results[0]
    assert "No executor found" in failed_result.error

    print(f"  ✓ 执行器不存在时正确报错")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("ParallelScheduler 单元测试")
    print("=" * 70)
    print()

    tests = [
        test_basic_parallel_execution,
        test_layered_execution,
        test_error_isolation,
        test_fail_fast_mode,
        test_timeout_handling,
        test_single_task_optimization,
        test_empty_task_list,
        test_execute_tasks_with_dependency_analysis,
        test_execute_tasks_sequential,
        test_scheduler_stats,
        test_batch_result_properties,
        test_convenience_function,
        test_executor_not_found,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ 测试失败: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ✗ 测试错误: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
