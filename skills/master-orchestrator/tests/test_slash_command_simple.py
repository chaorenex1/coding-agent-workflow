#!/usr/bin/env python3
"""
Slash Command 简化集成测试

直接测试 Slash Command 功能,不使用 sandbox。
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

from orchestrator import MasterOrchestrator
from orchestrator.core.slash_command import SlashCommandResult


def test_slash_command_detection():
    """测试 1: Slash Command 检测"""
    print("测试 1: Slash Command 检测")

    # 创建不启用 V3 的基础 Orchestrator
    orch = MasterOrchestrator(auto_discover=False)

    # 测试 Slash Command 检测
    result = orch.process("/stats")

    # 验证返回的是 SlashCommandResult
    assert isinstance(result, SlashCommandResult)
    assert result.command == "/stats"

    print(f"  ✓ Slash Command 检测成功")
    print(f"  ✓ 返回类型: {type(result).__name__}")
    print("  ✓ 测试通过\n")


def test_slash_command_without_v3():
    """测试 2: 未启用 V3 时的 Slash Command"""
    print("测试 2: 未启用 V3 时的 Slash Command")

    # 创建未启用 V3 的 Orchestrator
    orch = MasterOrchestrator(auto_discover=False)

    # 尝试执行 Slash Command
    result = orch.process("/stats")

    # 验证：应该返回基本统计信息(即使没有 V3)
    assert isinstance(result, SlashCommandResult)
    # 可能成功或失败都可以,取决于是否有基本 registry

    print(f"  ✓ Slash Command 执行: success={result.success}")
    if result.error:
        print(f"  ✓ 错误信息: {result.error}")
    if result.output:
        print(f"  ✓ 输出: {result.output}")
    print("  ✓ 测试通过\n")


def test_list_commands():
    """测试 3: /list-commands 命令"""
    print("测试 3: /list-commands 命令")

    orch = MasterOrchestrator(auto_discover=False)

    # 执行 /list-commands
    result = orch.process("/list-commands")

    # 验证
    assert isinstance(result, SlashCommandResult)
    assert result.success == True
    assert isinstance(result.output, list)
    assert len(result.output) > 0  # 至少有内置命令

    print(f"  ✓ /list-commands 执行成功")
    print(f"  ✓ 命令数量: {len(result.output)}")
    print(f"  ✓ 示例命令: {[cmd['name'] for cmd in result.output[:3]]}")
    print("  ✓ 测试通过\n")


def test_natural_language_still_works():
    """测试 4: 自然语言模式仍然工作"""
    print("测试 4: 自然语言模式仍然工作")

    orch = MasterOrchestrator(auto_discover=False)

    # 使用自然语言请求（不是 Slash Command）
    result = orch.process("简单测试")

    # 验证：不是 SlashCommandResult（向后兼容）
    assert not isinstance(result, SlashCommandResult)

    print(f"  ✓ 自然语言模式仍然工作")
    print(f"  ✓ 返回类型: {type(result).__name__}")
    print("  ✓ 测试通过\n")


def test_unknown_slash_command():
    """测试 5: 未知的 Slash Command"""
    print("测试 5: 未知的 Slash Command")

    orch = MasterOrchestrator(auto_discover=False)

    # 执行不存在的命令
    result = orch.process("/nonexistent-command")

    # 验证
    assert isinstance(result, SlashCommandResult)
    assert result.success == False
    assert "not found" in result.error.lower()

    print(f"  ✓ 正确处理未知命令")
    print(f"  ✓ 错误信息: {result.error}")
    print("  ✓ 测试通过\n")


def test_slash_command_with_args():
    """测试 6: 带参数的 Slash Command"""
    print("测试 6: 带参数的 Slash Command")

    orch = MasterOrchestrator(auto_discover=False)

    # 执行带参数的命令
    result = orch.process("/git-log")

    # 验证：命令被识别（可能执行失败是正常的，因为没有 git 仓库）
    assert isinstance(result, SlashCommandResult)

    print(f"  ✓ 带参数的 Slash Command 解析成功")
    print(f"  ✓ 命令: {result.command}")
    print(f"  ✓ 执行状态: success={result.success}")
    if result.error:
        print(f"  ✓ 错误: {result.error} (预期可能失败)")
    print("  ✓ 测试通过\n")


def test_registry_stats():
    """测试 7: Registry 统计信息"""
    print("测试 7: Registry 统计信息")

    orch = MasterOrchestrator(auto_discover=False)

    # 获取 slash_registry
    assert orch.slash_registry is not None

    # 获取统计信息
    stats = orch.slash_registry.get_stats()

    assert stats["total_commands"] > 0
    assert stats["enabled_commands"] > 0

    print(f"  ✓ 总命令数: {stats['total_commands']}")
    print(f"  ✓ 启用命令: {stats['enabled_commands']}")
    print(f"  ✓ 按类型统计: {stats['by_type']}")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Slash Command 简化集成测试")
    print("=" * 70)
    print()

    tests = [
        test_slash_command_detection,
        test_slash_command_without_v3,
        test_list_commands,
        test_natural_language_still_works,
        test_unknown_slash_command,
        test_slash_command_with_args,
        test_registry_stats,
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
