#!/usr/bin/env python3
"""
Phase 2 集成测试：ExecutionRouter 候选资源支持和降级策略测试

测试 ExecutionRouter 的候选资源功能。
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Windows 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
import os
os.chdir(project_root)

# 使用绝对导入
from analyzers.claude_intent_analyzer import Intent, ExecutionMode
from core.backend_orchestrator import BackendOrchestrator, TaskResult
from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType

# 导入 ExecutionRouter（需要特殊处理以支持相对导入）
# 方法：使用 importlib 动态加载，并设置正确的包上下文
import importlib.util

# 加载 master_orchestrator 模块
spec = importlib.util.spec_from_file_location(
    "master_orchestrator",  # 模块名
    project_root / "master_orchestrator.py",  # 文件路径
    submodule_search_locations=[str(project_root)]  # 允许相对导入
)
master_orch_module = importlib.util.module_from_spec(spec)

# 设置包上下文（关键步骤！）
master_orch_module.__package__ = ""  # 空字符串表示顶级包

# 注册模块
sys.modules['master_orchestrator'] = master_orch_module

# 执行模块
spec.loader.exec_module(master_orch_module)

# 获取 ExecutionRouter
ExecutionRouter = master_orch_module.ExecutionRouter


# ========== Mock 类 ==========

class MockBackendOrchestrator:
    """简化的 Mock BackendOrchestrator"""

    def __init__(self):
        self.call_count = 0

    def run_task(self, backend, prompt, stream_format="jsonl", **kwargs):
        """Mock run_task"""
        self.call_count += 1
        return TaskResult(
            backend=backend,
            prompt=prompt,
            output=f"Mock output from {backend}",
            success=True,
            duration_seconds=0.1
        )


class MockExecutor:
    """Mock Executor 用于测试"""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.call_count = 0

    def execute(self, request):
        """执行请求"""
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Mock executor failed")
        return TaskResult(
            backend="mock",
            prompt=request,
            output="Mock executor output",
            success=True,
            duration_seconds=0.1
        )


# ========== 测试函数 ==========

def test_resource_availability_check():
    """测试 1: 资源可用性检查"""
    print("\n========== 测试 1: 资源可用性检查 ==========\n")

    # 创建 registry 和 router
    registry = UnifiedRegistry()
    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch, registry=registry)

    # 注册启用的资源
    enabled_resource = ResourceMetadata(
        name="test-skill",
        namespace="skill:test-skill",
        type=ResourceType.SKILL,
        source="test",
        priority=80,
        enabled=True,
        config={"description": "Test skill", "dependencies": []}
    )
    registry.register(enabled_resource)

    # 注册禁用的资源
    disabled_resource = ResourceMetadata(
        name="disabled-skill",
        namespace="skill:disabled-skill",
        type=ResourceType.SKILL,
        source="test",
        priority=70,
        enabled=False,
        config={"description": "Disabled skill", "dependencies": []}
    )
    registry.register(disabled_resource)

    # 测试启用资源
    is_available, reason = router._check_resource_availability("skill:test-skill")
    print(f"  启用资源 'skill:test-skill':")
    print(f"    可用: {is_available}")
    print(f"    原因: {reason}")
    assert is_available is True, "启用资源应该可用"
    assert reason is None, "可用资源不应有原因"
    print(f"  ✓ 启用资源检查通过")

    # 测试禁用资源
    is_available, reason = router._check_resource_availability("skill:disabled-skill")
    print(f"\n  禁用资源 'skill:disabled-skill':")
    print(f"    可用: {is_available}")
    print(f"    原因: {reason}")
    assert is_available is False, "禁用资源应该不可用"
    assert "disabled" in reason.lower(), "原因应包含 'disabled'"
    print(f"  ✓ 禁用资源检查通过")

    # 测试不存在的资源
    is_available, reason = router._check_resource_availability("skill:non-existent")
    print(f"\n  不存在资源 'skill:non-existent':")
    print(f"    可用: {is_available}")
    print(f"    原因: {reason}")
    assert is_available is False, "不存在的资源应该不可用"
    assert "not found" in reason.lower(), "原因应包含 'not found'"
    print(f"  ✓ 不存在资源检查通过")

    print("\n[PASS] 资源可用性检查测试通过\n")


def test_dependency_check():
    """测试 2: 依赖检查"""
    print("\n========== 测试 2: 依赖检查 ==========\n")

    # 创建 registry 和 router
    registry = UnifiedRegistry()
    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch, registry=registry)

    # 注册依赖资源（启用）
    dep_resource = ResourceMetadata(
        name="dep-skill",
        namespace="skill:dep-skill",
        type=ResourceType.SKILL,
        source="test",
        priority=80,
        enabled=True,
        config={"description": "Dependency skill"}
    )
    registry.register(dep_resource)

    # 注册主资源（依赖 dep-skill）
    main_resource = ResourceMetadata(
        name="main-skill",
        namespace="skill:main-skill",
        type=ResourceType.SKILL,
        source="test",
        priority=80,
        enabled=True,
        config={
            "description": "Main skill",
            "dependencies": ["skill:dep-skill"]
        }
    )
    registry.register(main_resource)

    # 测试依赖满足
    is_available, reason = router._check_resource_availability("skill:main-skill")
    print(f"  主资源 'skill:main-skill' (依赖 dep-skill):")
    print(f"    可用: {is_available}")
    print(f"    原因: {reason}")
    assert is_available is True, "依赖满足的资源应该可用"
    print(f"  ✓ 依赖满足检查通过")

    # 禁用依赖资源
    dep_resource.enabled = False
    registry.update(dep_resource)

    # 再次测试
    is_available, reason = router._check_resource_availability("skill:main-skill")
    print(f"\n  主资源 'skill:main-skill' (依赖被禁用):")
    print(f"    可用: {is_available}")
    print(f"    原因: {reason}")
    assert is_available is False, "依赖不满足的资源应该不可用"
    assert "dependency" in reason.lower(), "原因应包含 'dependency'"
    print(f"  ✓ 依赖缺失检查通过")

    print("\n[PASS] 依赖检查测试通过\n")


def test_namespace_parsing():
    """测试 3: 命名空间解析"""
    print("\n========== 测试 3: 命名空间解析 ==========\n")

    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch)

    # 测试各种命名空间格式
    test_cases = [
        ("skill:code-review", ("skill", "code-review")),
        ("agent:explore", ("agent", "explore")),
        ("prompt:test", ("prompt", "test")),
        ("command:git-status", ("command", "git-status")),
        ("no-colon", ("backend", "no-colon")),  # 没有冒号，默认 backend
    ]

    for namespace, expected in test_cases:
        result = router._parse_namespace(namespace)
        print(f"  命名空间: '{namespace}'")
        print(f"    解析结果: {result}")
        print(f"    预期结果: {expected}")
        assert result == expected, f"解析错误: {namespace}"
        print(f"  ✓ 解析正确")

    print("\n[PASS] 命名空间解析测试通过\n")


def test_fallback_strategy_with_mocks():
    """测试 4: 降级策略（使用 Mock）"""
    print("\n========== 测试 4: 降级策略（使用 Mock） ==========\n")

    # 创建 registry 和 router
    registry = UnifiedRegistry()
    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch, registry=registry)

    # 注册两个资源
    skill1 = ResourceMetadata(
        name="skill-1",
        namespace="skill:skill-1",
        type=ResourceType.SKILL,
        source="test",
        priority=80,
        enabled=True,
        config={"description": "Skill 1"}
    )
    registry.register(skill1)

    skill2 = ResourceMetadata(
        name="skill-2",
        namespace="skill:skill-2",
        type=ResourceType.SKILL,
        source="test",
        priority=70,
        enabled=True,
        config={"description": "Skill 2"}
    )
    registry.register(skill2)

    # 创建 Intent 对象（带候选资源）
    intent = Intent(
        mode=ExecutionMode.SKILL,
        task_type="dev",
        complexity="medium",
        confidence=0.85,
        entity="skill:skill-1",
        candidates=["skill:skill-1", "skill:skill-2"]
    )

    # Mock _execute_skill_by_namespace 方法（第一个失败，第二个成功）
    call_count = [0]

    def mock_execute_skill(namespace, request, intent_obj):
        call_count[0] += 1
        if call_count[0] == 1:
            # 第一次调用失败
            raise RuntimeError("Skill 1 failed")
        else:
            # 第二次调用成功
            return TaskResult(
                backend="mock",
                prompt=request,
                output=f"Success from {namespace}",
                success=True,
                duration_seconds=0.1
            )

    # 使用 patch 替换方法
    with patch.object(router, '_execute_skill_by_namespace', side_effect=mock_execute_skill):
        print(f"  候选资源: {intent.candidates}")
        print(f"  预期: skill-1 失败 → 降级到 skill-2 成功")

        result = router.route(intent, "test request")

        print(f"\n  执行结果:")
        print(f"    成功: {result.success}")
        print(f"    输出: {result.output}")
        print(f"    调用次数: {call_count[0]}")

        assert result.success is True, "应该成功（降级到 skill-2）"
        assert call_count[0] == 2, "应该尝试了 2 次（skill-1 + skill-2）"
        assert "skill:skill-2" in result.output, "输出应包含 skill-2"
        print(f"  ✓ 降级策略测试通过")

    print("\n[PASS] 降级策略测试通过\n")


def test_all_candidates_fail():
    """测试 5: 所有候选资源都失败"""
    print("\n========== 测试 5: 所有候选资源都失败 ==========\n")

    # 创建 registry 和 router
    registry = UnifiedRegistry()
    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch, registry=registry)

    # 注册两个资源（都启用）
    skill1 = ResourceMetadata(
        name="skill-1",
        namespace="skill:skill-1",
        type=ResourceType.SKILL,
        source="test",
        priority=80,
        enabled=True,
        config={"description": "Skill 1"}
    )
    registry.register(skill1)

    skill2 = ResourceMetadata(
        name="skill-2",
        namespace="skill:skill-2",
        type=ResourceType.SKILL,
        source="test",
        priority=70,
        enabled=True,
        config={"description": "Skill 2"}
    )
    registry.register(skill2)

    # 创建 Intent 对象
    intent = Intent(
        mode=ExecutionMode.SKILL,
        task_type="dev",
        complexity="medium",
        confidence=0.85,
        entity="skill:skill-1",
        candidates=["skill:skill-1", "skill:skill-2"]
    )

    # Mock _execute_skill_by_namespace 方法（全部失败）
    def mock_execute_skill_fail(namespace, request, intent_obj):
        raise RuntimeError(f"{namespace} failed")

    # 使用 patch 替换方法
    with patch.object(router, '_execute_skill_by_namespace', side_effect=mock_execute_skill_fail):
        print(f"  候选资源: {intent.candidates}")
        print(f"  预期: 所有资源都失败 → 抛出 RuntimeError")

        try:
            result = router.route(intent, "test request")
            assert False, "应该抛出 RuntimeError"
        except RuntimeError as e:
            error_msg = str(e)
            print(f"\n  捕获异常:")
            print(f"    类型: {type(e).__name__}")
            print(f"    消息: {error_msg}")

            assert "All candidate resources failed" in error_msg, "错误消息应包含 'All candidate resources failed'"
            assert "skill:skill-1" in error_msg, "错误消息应包含 skill-1"
            assert "skill:skill-2" in error_msg, "错误消息应包含 skill-2"
            print(f"  ✓ 异常处理正确")

    print("\n[PASS] 所有候选资源失败测试通过\n")


def test_legacy_route_compatibility():
    """测试 6: 传统路由兼容性（没有候选资源）"""
    print("\n========== 测试 6: 传统路由兼容性 ==========\n")

    backend_orch = MockBackendOrchestrator()
    router = ExecutionRouter(backend_orch=backend_orch)  # 没有 registry

    # 创建传统 Intent 对象（没有 candidates）
    intent = Intent(
        mode=ExecutionMode.BACKEND,
        task_type="analysis",
        complexity="simple",
        confidence=0.9
    )

    print(f"  Intent 模式: {intent.mode.value}")
    print(f"  候选资源: {intent.candidates if hasattr(intent, 'candidates') else 'N/A'}")

    # 测试路由（应该使用传统逻辑）
    result = router.route(intent, "test request")

    print(f"\n  执行结果:")
    print(f"    成功: {result.success}")
    print(f"    后端: {result.backend}")
    print(f"    输出: {result.output}")

    assert result.success is True, "传统路由应该成功"
    print(f"  ✓ 传统路由兼容性测试通过")

    print("\n[PASS] 传统路由兼容性测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("Phase 2: ExecutionRouter 候选资源支持集成测试套件")
    print("=" * 70)

    tests = [
        test_resource_availability_check,
        test_dependency_check,
        test_namespace_parsing,
        test_fallback_strategy_with_mocks,
        test_all_candidates_fail,
        test_legacy_route_compatibility
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__}: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__}: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
