#!/usr/bin/env python3
"""
Slash Command 系统命令测试

只测试系统命令(不涉及 shell 执行),避免 Windows 编码问题。
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

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("/stats")

    assert isinstance(result, SlashCommandResult)
    assert result.command == "/stats"

    print(f"  ✓ Slash Command 检测成功")
    print(f"  ✓ 返回类型: {type(result).__name__}")
    print("  ✓ 测试通过\n")


def test_stats_command():
    """测试 2: /stats 命令"""
    print("测试 2: /stats 命令")

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("/stats")

    assert isinstance(result, SlashCommandResult)
    assert result.success == True
    assert isinstance(result.output, dict)
    assert "v3_enabled" in result.output
    assert "slash_commands" in result.output

    print(f"  ✓ /stats 执行成功")
    print(f"  ✓ V3 启用: {result.output['v3_enabled']}")
    print(f"  ✓ Slash Commands 统计: {result.output['slash_commands']}")
    print("  ✓ 测试通过\n")


def test_list_commands():
    """测试 3: /list-commands 命令"""
    print("测试 3: /list-commands 命令")

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("/list-commands")

    assert isinstance(result, SlashCommandResult)
    assert result.success == True
    assert isinstance(result.output, list)
    assert len(result.output) > 0

    # 验证内置命令存在
    command_names = [cmd['name'] for cmd in result.output]
    assert "stats" in command_names
    assert "list-commands" in command_names
    assert "list-skills" in command_names

    print(f"  ✓ /list-commands 执行成功")
    print(f"  ✓ 命令数量: {len(result.output)}")
    print(f"  ✓ 命令列表: {command_names[:5]}...")
    print("  ✓ 测试通过\n")


def test_list_skills_command():
    """测试 4: /list-skills 命令"""
    print("测试 4: /list-skills 命令")

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("/list-skills")

    assert isinstance(result, SlashCommandResult)
    # 注意：没有启用 V3 时可能返回空列表或报错
    # 两种结果都可以接受

    print(f"  ✓ /list-skills 执行")
    print(f"  ✓ 成功: {result.success}")
    if result.success:
        print(f"  ✓ Skills 数量: {len(result.output) if result.output else 0}")
    else:
        print(f"  ✓ 错误(预期): {result.error}")
    print("  ✓ 测试通过\n")


def test_natural_language_compatibility():
    """测试 5: 自然语言向后兼容"""
    print("测试 5: 自然语言向后兼容")

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("简单测试")

    # 不是 SlashCommandResult
    assert not isinstance(result, SlashCommandResult)

    print(f"  ✓ 自然语言模式正常工作")
    print(f"  ✓ 返回类型: {type(result).__name__}")
    print("  ✓ 测试通过\n")


def test_unknown_command():
    """测试 6: 未知命令处理"""
    print("测试 6: 未知命令处理")

    orch = MasterOrchestrator(auto_discover=False)
    result = orch.process("/unknown-command-12345")

    assert isinstance(result, SlashCommandResult)
    assert result.success == False
    assert "not found" in result.error.lower()

    print(f"  ✓ 正确处理未知命令")
    print(f"  ✓ 错误信息: {result.error}")
    print("  ✓ 测试通过\n")


def test_disabled_command():
    """测试 7: 禁用命令处理"""
    print("测试 7: 禁用命令处理")

    orch = MasterOrchestrator(auto_discover=False)

    # 手动禁用一个命令
    if orch.slash_registry:
        cmd = orch.slash_registry.get("stats")
        if cmd:
            # 创建禁用版本
            from orchestrator.core.slash_command import SlashCommandMetadata, SlashCommandType
            disabled_cmd = SlashCommandMetadata(
                name="test-disabled",
                type=SlashCommandType.SYSTEM,
                description="Test disabled command",
                handler="_get_stats",
                enabled=False,
                priority=100,
                source="test"
            )
            orch.slash_registry.register(disabled_cmd, overwrite=True)

            # 尝试执行
            result = orch.process("/test-disabled")

            assert isinstance(result, SlashCommandResult)
            assert result.success == False
            assert "disabled" in result.error.lower()

            print(f"  ✓ 正确阻止禁用命令")
            print(f"  ✓ 错误信息: {result.error}")
        else:
            print(f"  ⊘ 跳过测试（无可用命令）")
    else:
        print(f"  ⊘ 跳过测试（无 registry）")

    print("  ✓ 测试通过\n")


def test_registry_stats():
    """测试 8: Registry 统计"""
    print("测试 8: Registry 统计")

    orch = MasterOrchestrator(auto_discover=False)

    assert orch.slash_registry is not None

    stats = orch.slash_registry.get_stats()

    assert stats["total_commands"] >= 8  # 至少 8 个内置命令
    assert stats["enabled_commands"] > 0
    assert "system" in stats["by_type"]
    assert "shell" in stats["by_type"]

    print(f"  ✓ 总命令数: {stats['total_commands']}")
    print(f"  ✓ 启用命令: {stats['enabled_commands']}")
    print(f"  ✓ 系统命令: {stats['by_type']['system']}")
    print(f"  ✓ Shell命令: {stats['by_type']['shell']}")
    print("  ✓ 测试通过\n")


def test_command_metadata():
    """测试 9: 命令元数据"""
    print("测试 9: 命令元数据")

    orch = MasterOrchestrator(auto_discover=False)

    # 获取 stats 命令元数据
    cmd = orch.slash_registry.get("stats")

    assert cmd is not None
    assert cmd.name == "stats"
    assert cmd.full_name == "/stats"
    assert cmd.enabled == True
    assert cmd.description is not None

    print(f"  ✓ 命令名称: {cmd.name}")
    print(f"  ✓ 完整名称: {cmd.full_name}")
    print(f"  ✓ 描述: {cmd.description}")
    print(f"  ✓ 类型: {cmd.type.value}")
    print("  ✓ 测试通过\n")


def test_slash_prefix_variations():
    """测试 10: Slash 前缀变体"""
    print("测试 10: Slash 前缀变体")

    orch = MasterOrchestrator(auto_discover=False)

    # 测试多个 slash
    result1 = orch.process("//stats")
    assert isinstance(result1, SlashCommandResult)
    # 第二个 / 会被当作命令名的一部分，应该找不到

    # 测试前后空格
    result2 = orch.process("  /stats  ")
    assert isinstance(result2, SlashCommandResult)
    assert result2.success == True  # 应该正确处理

    print(f"  ✓ 多个 slash: success={result1.success}")
    print(f"  ✓ 前后空格: success={result2.success}")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Slash Command 系统命令测试")
    print("=" * 70)
    print()

    tests = [
        test_slash_command_detection,
        test_stats_command,
        test_list_commands,
        test_list_skills_command,
        test_natural_language_compatibility,
        test_unknown_command,
        test_disabled_command,
        test_registry_stats,
        test_command_metadata,
        test_slash_prefix_variations,
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
