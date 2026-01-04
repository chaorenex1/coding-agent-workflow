#!/usr/bin/env python3
"""
DependencyAnalyzer 单元测试

测试依赖图构建、拓扑排序、循环检测等功能。
"""

import sys
from pathlib import Path

# Windows 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.core.dependency_analyzer import (
    DependencyAnalyzer, Task, ParallelGroup, CyclicDependencyError
)
from orchestrator.core.unified_registry import (
    UnifiedRegistry, ResourceMetadata, ResourceType
)


def test_basic_graph_construction():
    """测试 1: 基本依赖图构建"""
    print("测试 1: 基本依赖图构建")

    analyzer = DependencyAnalyzer()

    # 创建简单任务链: A -> B -> C
    tasks = [
        Task(namespace="task:A", request="Task A", dependencies=["task:B"]),
        Task(namespace="task:B", request="Task B", dependencies=["task:C"]),
        Task(namespace="task:C", request="Task C", dependencies=[]),
    ]

    graph = analyzer.build_task_graph(tasks)

    # 验证图结构
    assert "task:A" in graph
    assert "task:B" in graph
    assert "task:C" in graph

    assert "task:B" in graph["task:A"]
    assert "task:C" in graph["task:B"]
    assert len(graph["task:C"]) == 0  # C 没有依赖

    print(f"  ✓ 依赖图: A→B→C")
    print("  ✓ 测试通过\n")


def test_topological_sort_simple():
    """测试 2: 简单拓扑排序"""
    print("测试 2: 简单拓扑排序")

    analyzer = DependencyAnalyzer()

    # A -> B -> C
    tasks = [
        Task("task:A", "A", dependencies=["task:B"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=[]),
    ]

    graph = analyzer.build_task_graph(tasks)
    levels = analyzer.topological_sort(graph)

    # 验证层级
    assert len(levels) == 3, f"Expected 3 levels, got {len(levels)}"

    # Level 0: C (no dependencies)
    # Level 1: B (depends on C)
    # Level 2: A (depends on B)
    assert "task:C" in levels[0]
    assert "task:B" in levels[1]
    assert "task:A" in levels[2]

    print(f"  ✓ 拓扑排序: {' → '.join([str(level) for level in levels])}")
    print("  ✓ 测试通过\n")


def test_parallel_groups():
    """测试 3: 并行分组"""
    print("测试 3: 并行分组")

    analyzer = DependencyAnalyzer()

    # 创建并行结构:
    #     D
    #    / \
    #   A   B
    #    \ /
    #     C
    tasks = [
        Task("task:D", "D", dependencies=["task:A", "task:B"]),
        Task("task:A", "A", dependencies=["task:C"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=[]),
    ]

    groups = analyzer.group_parallel_tasks(tasks)

    # 验证分组
    assert len(groups) == 3, f"Expected 3 groups, got {len(groups)}"

    # Level 0: C (独立)
    assert groups[0].level == 0
    assert len(groups[0].tasks) == 1
    assert groups[0].tasks[0].namespace == "task:C"

    # Level 1: A 和 B (可并行，都依赖 C)
    assert groups[1].level == 1
    assert len(groups[1].tasks) == 2
    task_namespaces = {task.namespace for task in groups[1].tasks}
    assert "task:A" in task_namespaces
    assert "task:B" in task_namespaces

    # Level 2: D (依赖 A 和 B)
    assert groups[2].level == 2
    assert len(groups[2].tasks) == 1
    assert groups[2].tasks[0].namespace == "task:D"

    print(f"  ✓ Level 0: {[t.namespace for t in groups[0].tasks]}")
    print(f"  ✓ Level 1 (并行): {[t.namespace for t in groups[1].tasks]}")
    print(f"  ✓ Level 2: {[t.namespace for t in groups[2].tasks]}")
    print("  ✓ 测试通过\n")


def test_circular_dependency_detection():
    """测试 4: 循环依赖检测"""
    print("测试 4: 循环依赖检测")

    analyzer = DependencyAnalyzer()

    # 创建循环: A -> B -> C -> A
    tasks = [
        Task("task:A", "A", dependencies=["task:B"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=["task:A"]),
    ]

    graph = analyzer.build_task_graph(tasks)

    # 检测循环
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) > 0, "Should detect circular dependency"

    # 验证循环中包含所有三个节点
    cycle = cycles[0]
    assert "task:A" in cycle
    assert "task:B" in cycle or "task:C" in cycle  # 至少包含其中一个

    print(f"  ✓ 检测到循环: {' → '.join(cycle)}")
    print("  ✓ 测试通过\n")


def test_group_with_circular_dependency():
    """测试 5: 分组时检测循环依赖"""
    print("测试 5: 分组时检测循环依赖")

    analyzer = DependencyAnalyzer()

    # 循环依赖
    tasks = [
        Task("task:A", "A", dependencies=["task:B"]),
        Task("task:B", "B", dependencies=["task:A"]),
    ]

    # 应该抛出异常
    try:
        groups = analyzer.group_parallel_tasks(tasks)
        assert False, "Should raise CyclicDependencyError"
    except CyclicDependencyError as e:
        assert "Circular" in str(e)
        print(f"  ✓ 正确抛出异常: {e}")

    print("  ✓ 测试通过\n")


def test_dependency_validation():
    """测试 6: 依赖验证"""
    print("测试 6: 依赖验证")

    analyzer = DependencyAnalyzer()

    # 创建任务，依赖不存在的资源
    tasks = [
        Task("task:A", "A", dependencies=["task:nonexistent"]),
        Task("task:B", "B", dependencies=[]),
    ]

    # 验证依赖
    errors = analyzer.validate_dependencies(tasks)

    # 应该检测到缺失的依赖
    assert len(errors) > 0, "Should detect missing dependency"
    assert "nonexistent" in errors[0]

    print(f"  ✓ 检测到 {len(errors)} 个依赖错误:")
    for error in errors:
        print(f"    - {error}")
    print("  ✓ 测试通过\n")


def test_dependency_depth():
    """测试 7: 依赖深度计算"""
    print("测试 7: 依赖深度计算")

    analyzer = DependencyAnalyzer()

    # 创建链: A -> B -> C -> D
    tasks = [
        Task("task:A", "A", dependencies=["task:B"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=["task:D"]),
        Task("task:D", "D", dependencies=[]),
    ]

    graph = analyzer.build_task_graph(tasks)

    # 计算深度
    depth_A = analyzer.get_dependency_depth(graph, "task:A")
    depth_B = analyzer.get_dependency_depth(graph, "task:B")
    depth_C = analyzer.get_dependency_depth(graph, "task:C")
    depth_D = analyzer.get_dependency_depth(graph, "task:D")

    # 验证深度
    assert depth_D == 0, f"D should have depth 0, got {depth_D}"
    assert depth_C == 1, f"C should have depth 1, got {depth_C}"
    assert depth_B == 2, f"B should have depth 2, got {depth_B}"
    assert depth_A == 3, f"A should have depth 3, got {depth_A}"

    print(f"  ✓ 深度: A={depth_A}, B={depth_B}, C={depth_C}, D={depth_D}")
    print("  ✓ 测试通过\n")


def test_execution_order():
    """测试 8: 执行顺序生成"""
    print("测试 8: 执行顺序生成")

    analyzer = DependencyAnalyzer()

    # A -> C, B -> C
    tasks = [
        Task("task:A", "A", dependencies=["task:C"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=[]),
    ]

    order = analyzer.get_execution_order(tasks)

    # C 应该在 A 和 B 之前
    assert order.index("task:C") < order.index("task:A")
    assert order.index("task:C") < order.index("task:B")

    print(f"  ✓ 执行顺序: {' → '.join(order)}")
    print("  ✓ 测试通过\n")


def test_independent_tasks():
    """测试 9: 获取独立任务"""
    print("测试 9: 获取独立任务")

    analyzer = DependencyAnalyzer()

    tasks = [
        Task("task:A", "A", dependencies=["task:C"]),
        Task("task:B", "B", dependencies=["task:C"]),
        Task("task:C", "C", dependencies=[]),
        Task("task:D", "D", dependencies=[]),  # 另一个独立任务
    ]

    independent = analyzer.get_independent_tasks(tasks)

    # 应该有两个独立任务: C 和 D
    assert len(independent) == 2, f"Expected 2 independent tasks, got {len(independent)}"

    independent_namespaces = {task.namespace for task in independent}
    assert "task:C" in independent_namespaces
    assert "task:D" in independent_namespaces

    print(f"  ✓ 独立任务: {[t.namespace for t in independent]}")
    print("  ✓ 测试通过\n")


def test_registry_integration():
    """测试 10: UnifiedRegistry 集成"""
    print("测试 10: UnifiedRegistry 集成")

    # 创建 Registry
    registry = UnifiedRegistry()

    # 注册资源及其依赖
    registry.register(ResourceMetadata(
        name="skill-A",
        namespace="skill:A",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=["skill:B"],
        enabled=True
    ))

    registry.register(ResourceMetadata(
        name="skill-B",
        namespace="skill:B",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=["skill:C"],
        enabled=True
    ))

    registry.register(ResourceMetadata(
        name="skill-C",
        namespace="skill:C",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=[],
        enabled=True
    ))

    # 创建 Analyzer（使用 Registry）
    analyzer = DependencyAnalyzer(registry=registry)

    # 创建任务（不指定依赖，从 Registry 读取）
    tasks = [
        Task("skill:A", "Task A"),
        Task("skill:B", "Task B"),
        Task("skill:C", "Task C"),
    ]

    # 构建图（应该从 Registry 读取依赖）
    graph = analyzer.build_task_graph(tasks)

    # 验证依赖
    assert "skill:B" in graph["skill:A"], "Should read dependency from registry"
    assert "skill:C" in graph["skill:B"], "Should read dependency from registry"

    # 拓扑排序
    levels = analyzer.topological_sort(graph)

    # 验证顺序: C -> B -> A
    assert "skill:C" in levels[0]
    assert "skill:B" in levels[1]
    assert "skill:A" in levels[2]

    print(f"  ✓ 从 Registry 读取依赖成功")
    print(f"  ✓ 拓扑排序: {' → '.join([str(level) for level in levels])}")
    print("  ✓ 测试通过\n")


def test_empty_task_list():
    """测试 11: 空任务列表"""
    print("测试 11: 空任务列表")

    analyzer = DependencyAnalyzer()

    tasks = []

    # 应该正常处理空列表
    groups = analyzer.group_parallel_tasks(tasks)
    assert len(groups) == 0

    order = analyzer.get_execution_order(tasks)
    assert len(order) == 0

    independent = analyzer.get_independent_tasks(tasks)
    assert len(independent) == 0

    print("  ✓ 空任务列表处理正常")
    print("  ✓ 测试通过\n")


def test_stats_calculation():
    """测试 12: 统计信息"""
    print("测试 12: 统计信息")

    analyzer = DependencyAnalyzer()

    # 创建复杂依赖图
    tasks = [
        Task("task:A", "A", dependencies=["task:B", "task:C"]),
        Task("task:B", "B", dependencies=["task:D"]),
        Task("task:C", "C", dependencies=["task:D"]),
        Task("task:D", "D", dependencies=[]),
    ]

    stats = analyzer.get_stats(tasks)

    # 验证统计
    assert stats["total_tasks"] == 4
    assert stats["total_dependencies"] == 4  # A->B, A->C, B->D, C->D
    assert stats["max_dependency_depth"] == 2  # A -> B -> D
    assert stats["independent_tasks"] == 1  # Only D
    assert stats["has_cycles"] == False

    print(f"  ✓ 统计信息:")
    print(f"    总任务: {stats['total_tasks']}")
    print(f"    总依赖: {stats['total_dependencies']}")
    print(f"    最大深度: {stats['max_dependency_depth']}")
    print(f"    独立任务: {stats['independent_tasks']}")
    print(f"    有循环: {stats['has_cycles']}")
    print("  ✓ 测试通过\n")


def test_complex_dag():
    """测试 13: 复杂 DAG"""
    print("测试 13: 复杂 DAG（有向无环图）")

    analyzer = DependencyAnalyzer()

    # 创建复杂 DAG:
    #       G
    #      / \
    #     E   F
    #    / \ / \
    #   A  B C  D
    tasks = [
        Task("task:G", "G", dependencies=["task:E", "task:F"]),
        Task("task:E", "E", dependencies=["task:A", "task:B"]),
        Task("task:F", "F", dependencies=["task:C", "task:D"]),
        Task("task:A", "A", dependencies=[]),
        Task("task:B", "B", dependencies=[]),
        Task("task:C", "C", dependencies=[]),
        Task("task:D", "D", dependencies=[]),
    ]

    groups = analyzer.group_parallel_tasks(tasks)

    # Level 0: A, B, C, D (可并行)
    # Level 1: E, F (可并行)
    # Level 2: G

    assert len(groups) == 3, f"Expected 3 levels, got {len(groups)}"

    # Level 0: 4 个独立任务
    assert len(groups[0].tasks) == 4

    # Level 1: E 和 F
    assert len(groups[1].tasks) == 2

    # Level 2: G
    assert len(groups[2].tasks) == 1
    assert groups[2].tasks[0].namespace == "task:G"

    print(f"  ✓ Level 0 (并行): {[t.namespace for t in groups[0].tasks]}")
    print(f"  ✓ Level 1 (并行): {[t.namespace for t in groups[1].tasks]}")
    print(f"  ✓ Level 2: {[t.namespace for t in groups[2].tasks]}")
    print("  ✓ 测试通过\n")


def test_self_dependency():
    """测试 14: 自依赖检测"""
    print("测试 14: 自依赖检测")

    analyzer = DependencyAnalyzer()

    # 任务依赖自己
    tasks = [
        Task("task:A", "A", dependencies=["task:A"]),
    ]

    graph = analyzer.build_task_graph(tasks)
    cycles = analyzer.detect_cycles(graph)

    # 应该检测到循环
    assert len(cycles) > 0, "Should detect self-dependency as cycle"

    print(f"  ✓ 检测到自依赖循环")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("DependencyAnalyzer 单元测试")
    print("=" * 70)
    print()

    tests = [
        test_basic_graph_construction,
        test_topological_sort_simple,
        test_parallel_groups,
        test_circular_dependency_detection,
        test_group_with_circular_dependency,
        test_dependency_validation,
        test_dependency_depth,
        test_execution_order,
        test_independent_tasks,
        test_registry_integration,
        test_empty_task_list,
        test_stats_calculation,
        test_complex_dag,
        test_self_dependency,
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
