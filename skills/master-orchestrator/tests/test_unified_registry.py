#!/usr/bin/env python3
"""
UnifiedRegistry 单元测试

测试资源注册、查询、依赖管理功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.core.unified_registry import (
    UnifiedRegistry, ResourceMetadata, ResourceType
)


def test_basic_registration():
    """测试基本注册功能"""
    print("测试 1: 基本注册功能")

    registry = UnifiedRegistry()

    # 注册 Skill
    metadata = ResourceMetadata(
        name="test-skill",
        namespace="skill:test-skill",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=[],
        enabled=True
    )

    success = registry.register(metadata)
    assert success == True, "Registration should succeed"

    # 验证注册
    retrieved = registry.get("skill:test-skill")
    assert retrieved is not None
    assert retrieved.name == "test-skill"
    assert retrieved.priority == 100

    print("  ✓ 基本注册功能正常")
    print("  ✓ 测试通过\n")


def test_priority_override():
    """测试优先级覆盖"""
    print("测试 2: 优先级覆盖")

    registry = UnifiedRegistry()

    # 注册低优先级资源
    low_priority = ResourceMetadata(
        name="common",
        namespace="skill:common",
        type=ResourceType.SKILL,
        source="builtin",
        priority=10,
        dependencies=[],
        enabled=True
    )
    registry.register(low_priority)

    # 注册高优先级资源（同名）
    high_priority = ResourceMetadata(
        name="common",
        namespace="skill:common",
        type=ResourceType.SKILL,
        source="project",
        priority=100,
        dependencies=[],
        enabled=True
    )
    registry.register(high_priority)

    # 验证高优先级覆盖
    retrieved = registry.get("skill:common")
    assert retrieved.priority == 100, f"Expected priority 100, got {retrieved.priority}"
    assert retrieved.source == "project"

    print("  ✓ 高优先级覆盖低优先级")
    print("  ✓ 测试通过\n")


def test_list_resources():
    """测试资源列表查询"""
    print("测试 3: 资源列表查询")

    registry = UnifiedRegistry()

    # 注册多个资源
    resources = [
        ResourceMetadata("skill-1", "skill:skill-1", ResourceType.SKILL, "builtin", 10, [], enabled=True),
        ResourceMetadata("skill-2", "skill:skill-2", ResourceType.SKILL, "project", 100, [], enabled=True),
        ResourceMetadata("cmd-1", "command:cmd-1", ResourceType.COMMAND, "builtin", 10, [], enabled=True),
        ResourceMetadata("agent-1", "agent:agent-1", ResourceType.AGENT, "user", 50, [], enabled=True),
    ]

    for res in resources:
        registry.register(res)

    # 测试类型过滤
    skills = registry.list_resources(type_filter=ResourceType.SKILL)
    assert len(skills) == 2, f"Expected 2 skills, got {len(skills)}"

    commands = registry.list_resources(type_filter=ResourceType.COMMAND)
    assert len(commands) == 1

    # 测试来源过滤
    builtin = registry.list_resources(source_filter="builtin")
    assert len(builtin) == 2

    project = registry.list_resources(source_filter="project")
    assert len(project) == 1

    print(f"  ✓ 类型过滤: {len(skills)} skills, {len(commands)} commands")
    print(f"  ✓ 来源过滤: {len(builtin)} builtin, {len(project)} project")
    print("  ✓ 测试通过\n")


def test_dependency_resolution():
    """测试依赖解析"""
    print("测试 4: 依赖解析")

    registry = UnifiedRegistry()

    # 创建依赖链: A -> B -> C
    res_c = ResourceMetadata("C", "skill:C", ResourceType.SKILL, "project", 100, [], enabled=True)
    res_b = ResourceMetadata("B", "skill:B", ResourceType.SKILL, "project", 100, ["skill:C"], enabled=True)
    res_a = ResourceMetadata("A", "skill:A", ResourceType.SKILL, "project", 100, ["skill:B"], enabled=True)

    registry.register(res_c)
    registry.register(res_b)
    registry.register(res_a)

    # 解析依赖
    deps = registry.resolve_dependencies("skill:A")

    # 应该按顺序返回: [C, B, A]
    assert "skill:C" in deps, "C should be in dependencies"
    assert "skill:B" in deps, "B should be in dependencies"
    assert "skill:A" in deps, "A should be in dependencies"

    # C 应该在 B 之前
    assert deps.index("skill:C") < deps.index("skill:B")
    # B 应该在 A 之前
    assert deps.index("skill:B") < deps.index("skill:A")

    print(f"  ✓ 依赖链: {' → '.join(deps)}")
    print("  ✓ 测试通过\n")


def test_circular_dependency_detection():
    """测试循环依赖检测"""
    print("测试 5: 循环依赖检测")

    registry = UnifiedRegistry()

    # 创建循环依赖: A -> B -> C -> A
    res_a = ResourceMetadata("A", "skill:A", ResourceType.SKILL, "project", 100, ["skill:B"], enabled=True)
    res_b = ResourceMetadata("B", "skill:B", ResourceType.SKILL, "project", 100, ["skill:C"], enabled=True)
    res_c = ResourceMetadata("C", "skill:C", ResourceType.SKILL, "project", 100, ["skill:A"], enabled=True)

    registry.register(res_a)
    registry.register(res_b)
    registry.register(res_c)

    # 检测循环依赖
    cycles = registry.check_circular_dependency()

    assert len(cycles) > 0, "Should detect circular dependency"
    print(f"  ✓ 检测到 {len(cycles)} 个循环依赖")
    for cycle in cycles:
        print(f"    - {' → '.join(cycle)}")
    print("  ✓ 测试通过\n")


def test_dependency_validation():
    """测试依赖验证"""
    print("测试 6: 依赖验证")

    registry = UnifiedRegistry()

    # 注册资源，但依赖不存在
    res_a = ResourceMetadata(
        "A", "skill:A", ResourceType.SKILL, "project", 100,
        ["skill:nonexistent"],  # 不存在的依赖
        enabled=True
    )
    registry.register(res_a)

    # 验证依赖
    errors = registry.validate_dependencies()

    assert len(errors) > 0, "Should detect missing dependency"
    print(f"  ✓ 检测到 {len(errors)} 个依赖错误:")
    for error in errors:
        print(f"    - {error}")
    print("  ✓ 测试通过\n")


def test_namespace_isolation():
    """测试命名空间隔离"""
    print("测试 7: 命名空间隔离")

    registry = UnifiedRegistry()

    # 注册同名但不同类型的资源
    skill_review = ResourceMetadata("review", "skill:review", ResourceType.SKILL, "project", 100, [], enabled=True)
    prompt_review = ResourceMetadata("review", "prompt:review", ResourceType.PROMPT, "project", 100, [], enabled=True)

    registry.register(skill_review)
    registry.register(prompt_review)

    # 验证两者都存在且互不干扰
    skill = registry.get("skill:review")
    prompt = registry.get("prompt:review")

    assert skill is not None
    assert prompt is not None
    assert skill.type == ResourceType.SKILL
    assert prompt.type == ResourceType.PROMPT

    print("  ✓ 命名空间隔离正常（skill:review 和 prompt:review 共存）")
    print("  ✓ 测试通过\n")


def test_registry_stats():
    """测试注册表统计"""
    print("测试 8: 注册表统计")

    registry = UnifiedRegistry()

    # 注册多个资源
    resources = [
        ResourceMetadata("s1", "skill:s1", ResourceType.SKILL, "builtin", 10, [], enabled=True),
        ResourceMetadata("s2", "skill:s2", ResourceType.SKILL, "project", 100, ["skill:s1"], enabled=True),
        ResourceMetadata("c1", "command:c1", ResourceType.COMMAND, "builtin", 10, [], enabled=True),
    ]

    for res in resources:
        registry.register(res)

    # 获取统计
    stats = registry.get_stats()

    assert stats["total_resources"] == 3
    assert stats["by_type"]["skill"] == 2
    assert stats["by_type"]["command"] == 1
    assert stats["with_dependencies"] == 1  # 只有 s2 有依赖

    print(f"  ✓ 统计信息:")
    print(f"    总资源: {stats['total_resources']}")
    print(f"    按类型: {stats['by_type']}")
    print(f"    按来源: {stats['by_source']}")
    print(f"    有依赖: {stats['with_dependencies']}")
    print("  ✓ 测试通过\n")


def test_get_dependents():
    """测试获取依赖者"""
    print("测试 9: 获取依赖者")

    registry = UnifiedRegistry()

    # 创建依赖关系: A -> C, B -> C
    res_c = ResourceMetadata("C", "skill:C", ResourceType.SKILL, "project", 100, [], enabled=True)
    res_a = ResourceMetadata("A", "skill:A", ResourceType.SKILL, "project", 100, ["skill:C"], enabled=True)
    res_b = ResourceMetadata("B", "skill:B", ResourceType.SKILL, "project", 100, ["skill:C"], enabled=True)

    registry.register(res_c)
    registry.register(res_a)
    registry.register(res_b)

    # 获取 C 的依赖者
    dependents = registry.get_dependents("skill:C")

    assert len(dependents) == 2, f"Expected 2 dependents, got {len(dependents)}"
    assert "skill:A" in dependents
    assert "skill:B" in dependents

    print(f"  ✓ skill:C 的依赖者: {dependents}")
    print("  ✓ 测试通过\n")


def test_clear_registry():
    """测试清空注册表"""
    print("测试 10: 清空注册表")

    registry = UnifiedRegistry()

    # 注册资源
    res = ResourceMetadata("test", "skill:test", ResourceType.SKILL, "project", 100, [], enabled=True)
    registry.register(res)

    assert len(registry) == 1

    # 清空
    registry.clear()

    assert len(registry) == 0
    assert registry.get("skill:test") is None

    print("  ✓ 注册表清空成功")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("UnifiedRegistry 单元测试")
    print("=" * 70)
    print()

    tests = [
        test_basic_registration,
        test_priority_override,
        test_list_resources,
        test_dependency_resolution,
        test_circular_dependency_detection,
        test_dependency_validation,
        test_namespace_isolation,
        test_registry_stats,
        test_get_dependents,
        test_clear_registry,
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
