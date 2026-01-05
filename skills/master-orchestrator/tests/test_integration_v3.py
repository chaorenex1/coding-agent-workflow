#!/usr/bin/env python3
"""
MasterOrchestrator V3 集成测试

测试自动发现、并行执行等 V3 功能的端到端集成。
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

from orchestrator.core.config_loader import ConfigLoader
from orchestrator.core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType
from orchestrator.core.executor_factory import ExecutorFactory
from orchestrator.core.dependency_analyzer import DependencyAnalyzer, Task
from orchestrator.core.parallel_scheduler import ParallelScheduler
from orchestrator.tests.sandbox import create_sandbox, TestHelper, MockBackendOrchestrator


def test_config_to_registry_integration():
    """测试 1: ConfigLoader → UnifiedRegistry 集成"""
    print("测试 1: ConfigLoader → UnifiedRegistry 集成")

    with create_sandbox("integration-config") as sandbox:
        # 创建配置文件
        config_data = {
            "version": "3.0",
            "skills": {
                "manual": [
                    {
                        "name": "skill-A",
                        "path": "./skills/skill-A.yaml",
                        "priority": 100,
                        "enabled": True
                    },
                    {
                        "name": "skill-B",
                        "path": "./skills/skill-B.yaml",
                        "priority": 50,
                        "enabled": True,
                        "dependencies": ["skill:skill-A"]
                    }
                ]
            }
        }

        sandbox.create_config(config_data)

        # 创建 Skills
        sandbox.create_skill("skill-A", TestHelper.create_sample_skill("skill-A", priority=100))
        sandbox.create_skill("skill-B", TestHelper.create_sample_skill("skill-B", priority=50, dependencies=["skill:skill-A"]))

        # 加载配置
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 填充注册表
        registry = UnifiedRegistry()

        for name, skill_config in config.skills.items():
            metadata = ResourceMetadata(
                name=name,
                namespace=f"skill:{name}",
                type=ResourceType.SKILL,
                source=skill_config.source,
                priority=skill_config.priority,
                dependencies=skill_config.dependencies,
                enabled=skill_config.enabled
            )
            registry.register(metadata)

        # 验证注册表
        assert len(registry) >= 2
        assert registry.exists("skill:skill-A")
        assert registry.exists("skill:skill-B")

        # 验证依赖
        skill_b = registry.get("skill:skill-B")
        assert "skill:skill-A" in skill_b.dependencies

        print(f"  ✓ 配置加载并填充注册表成功")
        print(f"  ✓ 注册了 {len(registry)} 个资源")
        print("  ✓ 测试通过\n")


def test_registry_to_dependency_analyzer_integration():
    """测试 2: UnifiedRegistry → DependencyAnalyzer 集成"""
    print("测试 2: UnifiedRegistry → DependencyAnalyzer 集成")

    # 创建注册表并注册资源
    registry = UnifiedRegistry()

    registry.register(ResourceMetadata(
        name="task-C",
        namespace="task:C",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=[],
        enabled=True
    ))

    registry.register(ResourceMetadata(
        name="task-B",
        namespace="task:B",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=["task:C"],
        enabled=True
    ))

    registry.register(ResourceMetadata(
        name="task-A",
        namespace="task:A",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=["task:B"],
        enabled=True
    ))

    # 创建分析器（使用注册表）
    analyzer = DependencyAnalyzer(registry=registry)

    # 创建任务（不指定依赖，从注册表读取）
    tasks = [
        Task("task:A", "Task A"),
        Task("task:B", "Task B"),
        Task("task:C", "Task C"),
    ]

    # 分组并行任务
    groups = analyzer.group_parallel_tasks(tasks)

    # 验证分组
    assert len(groups) == 3  # C, B, A 三层

    # Level 0: C
    assert len(groups[0].tasks) == 1
    assert groups[0].tasks[0].namespace == "task:C"

    # Level 1: B
    assert len(groups[1].tasks) == 1
    assert groups[1].tasks[0].namespace == "task:B"

    # Level 2: A
    assert len(groups[2].tasks) == 1
    assert groups[2].tasks[0].namespace == "task:A"

    print(f"  ✓ 从注册表读取依赖并分组成功")
    print(f"  ✓ 生成了 {len(groups)} 个执行层级")
    print("  ✓ 测试通过\n")


def test_full_pipeline_integration():
    """测试 3: 完整流水线集成（Config → Registry → Analyzer → Scheduler）"""
    print("测试 3: 完整流水线集成")

    with create_sandbox("integration-pipeline") as sandbox:
        # 1. 创建配置
        config_data = {
            "version": "3.0",
            "parallel": {
                "enabled": True,
                "max_workers": 3
            },
            "skills": {
                "manual": [
                    {"name": "skill-X", "path": "./skills/skill-X.yaml", "priority": 100, "enabled": True},
                    {"name": "skill-Y", "path": "./skills/skill-Y.yaml", "priority": 100, "enabled": True},
                    {"name": "skill-Z", "path": "./skills/skill-Z.yaml", "priority": 100, "enabled": True, "dependencies": ["skill:skill-X", "skill:skill-Y"]}
                ]
            }
        }
        sandbox.create_config(config_data)

        # 创建 Skills
        sandbox.create_skill("skill-X", TestHelper.create_sample_skill("skill-X"))
        sandbox.create_skill("skill-Y", TestHelper.create_sample_skill("skill-Y"))
        sandbox.create_skill("skill-Z", TestHelper.create_sample_skill("skill-Z", dependencies=["skill:skill-X", "skill:skill-Y"]))

        # 2. 加载配置
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 3. 填充注册表
        registry = UnifiedRegistry()
        for name, skill_config in config.skills.items():
            metadata = ResourceMetadata(
                name=name,
                namespace=f"skill:{name}",
                type=ResourceType.SKILL,
                source=skill_config.source,
                priority=skill_config.priority,
                dependencies=skill_config.dependencies,
                enabled=skill_config.enabled
            )
            registry.register(metadata)

        # 4. 创建分析器
        analyzer = DependencyAnalyzer(registry=registry)

        # 5. 创建任务
        tasks = [
            Task("skill:skill-X", "Execute X"),
            Task("skill:skill-Y", "Execute Y"),
            Task("skill:skill-Z", "Execute Z"),
        ]

        # 6. 分组
        groups = analyzer.group_parallel_tasks(tasks)

        # 验证分组：
        # Level 0: X 和 Y (并行)
        # Level 1: Z
        assert len(groups) == 2
        assert len(groups[0].tasks) == 2  # X 和 Y
        assert len(groups[1].tasks) == 1  # Z

        print(f"  ✓ 完整流水线执行成功")
        print(f"  ✓ Level 0: {len(groups[0].tasks)} 个并行任务")
        print(f"  ✓ Level 1: {len(groups[1].tasks)} 个任务")
        print("  ✓ 测试通过\n")


def test_priority_override_integration():
    """测试 4: 优先级覆盖集成（UnifiedRegistry 层级）"""
    print("测试 4: 优先级覆盖集成")

    # 创建注册表
    registry = UnifiedRegistry()

    # 先注册低优先级资源（模拟内置资源）
    registry.register(ResourceMetadata(
        name="common-skill",
        namespace="skill:common-skill",
        type=ResourceType.SKILL,
        source="builtin",
        priority=10,  # 低优先级
        dependencies=[],
        enabled=True
    ))

    # 验证低优先级资源
    skill = registry.get("skill:common-skill")
    assert skill.priority == 10

    # 再注册高优先级资源（模拟项目级资源，same namespace）
    registry.register(ResourceMetadata(
        name="common-skill",
        namespace="skill:common-skill",
        type=ResourceType.SKILL,
        source="project",
        priority=100,  # 高优先级
        dependencies=[],
        enabled=True
    ))

    # 验证高优先级覆盖成功
    skill = registry.get("skill:common-skill")
    assert skill.priority == 100, f"Expected priority 100, got {skill.priority}"
    assert skill.source == "project", f"Expected source 'project', got {skill.source}"

    print(f"  ✓ 优先级覆盖成功: builtin(10) → project(100)")
    print("  ✓ 测试通过\n")


def test_circular_dependency_detection_integration():
    """测试 5: 循环依赖检测集成"""
    print("测试 5: 循环依赖检测集成")

    # 创建注册表
    registry = UnifiedRegistry()

    # 注册循环依赖: A → B → C → A
    registry.register(ResourceMetadata("A", "skill:A", ResourceType.SKILL, "project", 100, ["skill:B"], enabled=True))
    registry.register(ResourceMetadata("B", "skill:B", ResourceType.SKILL, "project", 100, ["skill:C"], enabled=True))
    registry.register(ResourceMetadata("C", "skill:C", ResourceType.SKILL, "project", 100, ["skill:A"], enabled=True))

    # 检测循环依赖
    cycles = registry.check_circular_dependency()
    assert len(cycles) > 0, "Should detect circular dependency"

    print(f"  ✓ 检测到 {len(cycles)} 个循环依赖")
    for cycle in cycles:
        print(f"    - {' → '.join(cycle)}")
    print("  ✓ 测试通过\n")


def test_dependency_validation_integration():
    """测试 6: 依赖验证集成"""
    print("测试 6: 依赖验证集成")

    registry = UnifiedRegistry()

    # 注册资源，但依赖缺失
    registry.register(ResourceMetadata(
        "skill-A",
        "skill:skill-A",
        ResourceType.SKILL,
        "project",
        100,
        ["skill:nonexistent"],  # 依赖不存在
        enabled=True
    ))

    # 验证依赖
    errors = registry.validate_dependencies()

    assert len(errors) > 0, "Should detect missing dependency"
    assert any("nonexistent" in error for error in errors)

    print(f"  ✓ 检测到 {len(errors)} 个依赖错误")
    print("  ✓ 测试通过\n")


def test_namespace_isolation_integration():
    """测试 7: 命名空间隔离集成"""
    print("测试 7: 命名空间隔离集成")

    registry = UnifiedRegistry()

    # 注册同名但不同类型的资源
    registry.register(ResourceMetadata("review", "skill:review", ResourceType.SKILL, "project", 100, [], enabled=True))
    registry.register(ResourceMetadata("review", "prompt:review", ResourceType.PROMPT, "project", 100, [], enabled=True))
    registry.register(ResourceMetadata("review", "command:review", ResourceType.COMMAND, "project", 100, [], enabled=True))

    # 验证三者独立存在
    assert registry.exists("skill:review")
    assert registry.exists("prompt:review")
    assert registry.exists("command:review")

    # 验证类型正确
    skill = registry.get("skill:review")
    prompt = registry.get("prompt:review")
    command = registry.get("command:review")

    assert skill.type == ResourceType.SKILL
    assert prompt.type == ResourceType.PROMPT
    assert command.type == ResourceType.COMMAND

    print(f"  ✓ 命名空间隔离正常：skill:review, prompt:review, command:review")
    print("  ✓ 测试通过\n")


def test_registry_statistics_integration():
    """测试 8: 注册表统计集成"""
    print("测试 8: 注册表统计集成")

    registry = UnifiedRegistry()

    # 注册多种类型资源
    registry.register(ResourceMetadata("s1", "skill:s1", ResourceType.SKILL, "builtin", 10, [], enabled=True))
    registry.register(ResourceMetadata("s2", "skill:s2", ResourceType.SKILL, "project", 100, ["skill:s1"], enabled=True))
    registry.register(ResourceMetadata("c1", "command:c1", ResourceType.COMMAND, "builtin", 10, [], enabled=True))
    registry.register(ResourceMetadata("p1", "prompt:p1", ResourceType.PROMPT, "user", 50, [], enabled=True))

    stats = registry.get_stats()

    assert stats["total_resources"] == 4
    assert stats["by_type"]["skill"] == 2
    assert stats["by_type"]["command"] == 1
    assert stats["by_type"]["prompt"] == 1
    assert stats["by_source"]["builtin"] == 2
    assert stats["by_source"]["project"] == 1
    assert stats["by_source"]["user"] == 1
    assert stats["with_dependencies"] == 1  # 只有 s2 有依赖

    print(f"  ✓ 统计信息:")
    print(f"    总资源: {stats['total_resources']}")
    print(f"    按类型: {stats['by_type']}")
    print(f"    按来源: {stats['by_source']}")
    print(f"    有依赖: {stats['with_dependencies']}")
    print("  ✓ 测试通过\n")


def test_complex_dependency_graph_integration():
    """测试 9: 复杂依赖图集成"""
    print("测试 9: 复杂依赖图集成")

    registry = UnifiedRegistry()

    # 创建复杂 DAG:
    #       F
    #      / \
    #     D   E
    #    / \ / \
    #   A  B C  (B 被 D 和 E 共享)
    registry.register(ResourceMetadata("A", "task:A", ResourceType.SKILL, "project", 100, [], enabled=True))
    registry.register(ResourceMetadata("B", "task:B", ResourceType.SKILL, "project", 100, [], enabled=True))
    registry.register(ResourceMetadata("C", "task:C", ResourceType.SKILL, "project", 100, [], enabled=True))
    registry.register(ResourceMetadata("D", "task:D", ResourceType.SKILL, "project", 100, ["task:A", "task:B"], enabled=True))
    registry.register(ResourceMetadata("E", "task:E", ResourceType.SKILL, "project", 100, ["task:B", "task:C"], enabled=True))
    registry.register(ResourceMetadata("F", "task:F", ResourceType.SKILL, "project", 100, ["task:D", "task:E"], enabled=True))

    analyzer = DependencyAnalyzer(registry=registry)

    tasks = [
        Task("task:A", "A"),
        Task("task:B", "B"),
        Task("task:C", "C"),
        Task("task:D", "D"),
        Task("task:E", "E"),
        Task("task:F", "F"),
    ]

    groups = analyzer.group_parallel_tasks(tasks)

    # 验证分层
    # Level 0: A, B, C (并行)
    # Level 1: D, E (并行，都依赖 B)
    # Level 2: F
    assert len(groups) == 3

    print(f"  ✓ 复杂依赖图分析成功")
    print(f"  ✓ Level 0: {len(groups[0].tasks)} 个并行任务")
    print(f"  ✓ Level 1: {len(groups[1].tasks)} 个并行任务")
    print(f"  ✓ Level 2: {len(groups[2].tasks)} 个任务")
    print("  ✓ 测试通过\n")


def test_empty_configuration_integration():
    """测试 10: 空配置集成"""
    print("测试 10: 空配置集成")

    with create_sandbox("integration-empty") as sandbox:
        # 不创建配置文件

        # 加载配置（应该使用默认值）
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证默认配置
        assert config is not None
        assert config.version == "3.0"
        assert len(config.global_settings) > 0

        # 填充注册表
        registry = UnifiedRegistry()

        # 即使没有配置，注册表也应该工作
        registry.register(ResourceMetadata("test", "skill:test", ResourceType.SKILL, "builtin", 10, [], enabled=True))

        assert len(registry) == 1

        print(f"  ✓ 空配置使用默认值成功")
        print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("MasterOrchestrator V3 集成测试")
    print("=" * 70)
    print()

    tests = [
        test_config_to_registry_integration,
        test_registry_to_dependency_analyzer_integration,
        test_full_pipeline_integration,
        test_priority_override_integration,
        test_circular_dependency_detection_integration,
        test_dependency_validation_integration,
        test_namespace_isolation_integration,
        test_registry_statistics_integration,
        test_complex_dependency_graph_integration,
        test_empty_configuration_integration,
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
