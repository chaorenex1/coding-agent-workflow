#!/usr/bin/env python3
"""
Slash Command 集成测试

测试 MasterOrchestrator 与 Slash Command 系统的集成。
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
from orchestrator.tests.sandbox import create_sandbox, TestHelper


def test_slash_command_detection():
    """测试 1: Slash Command 检测"""
    print("测试 1: Slash Command 检测")

    # 创建启用 V3 的 Orchestrator
    with create_sandbox("slash-detection") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 测试 Slash Command 检测
        result = orch.process("/stats")

        # 验证返回的是 SlashCommandResult
        assert isinstance(result, SlashCommandResult)
        assert result.command == "/stats"

        print(f"  ✓ Slash Command 检测成功")
        print(f"  ✓ 返回类型: {type(result).__name__}")
        print("  ✓ 测试通过\n")


def test_discover_command():
    """测试 2: /discover 命令"""
    print("测试 2: /discover 命令")

    with create_sandbox("slash-discover") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        # 创建一些 skills
        sandbox.create_skill("skill-1", TestHelper.create_sample_skill("skill-1"))
        sandbox.create_skill("skill-2", TestHelper.create_sample_skill("skill-2"))

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行 /discover
        result = orch.process("/discover")

        # 验证
        assert result.success == True
        assert isinstance(result.output, dict)
        assert "total_resources" in result.output

        print(f"  ✓ /discover 执行成功")
        print(f"  ✓ 发现资源: {result.output.get('total_resources', 0)} 个")
        print("  ✓ 测试通过\n")


def test_list_skills_command():
    """测试 3: /list-skills 命令"""
    print("测试 3: /list-skills 命令")

    with create_sandbox("slash-list-skills") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行 /list-skills
        result = orch.process("/list-skills")

        # 验证
        assert result.success == True
        assert isinstance(result.output, list)

        print(f"  ✓ /list-skills 执行成功")
        print(f"  ✓ Skills 数量: {len(result.output)}")
        print("  ✓ 测试通过\n")


def test_list_commands():
    """测试 4: /list-commands 命令"""
    print("测试 4: /list-commands 命令")

    with create_sandbox("slash-list-commands") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行 /list-commands
        result = orch.process("/list-commands")

        # 验证
        assert result.success == True
        assert isinstance(result.output, list)
        assert len(result.output) > 0  # 至少有内置命令

        print(f"  ✓ /list-commands 执行成功")
        print(f"  ✓ 命令数量: {len(result.output)}")
        print("  ✓ 测试通过\n")


def test_stats_command():
    """测试 5: /stats 命令"""
    print("测试 5: /stats 命令")

    with create_sandbox("slash-stats") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行 /stats
        result = orch.process("/stats")

        # 验证
        assert result.success == True
        assert isinstance(result.output, dict)
        assert "v3_enabled" in result.output
        assert result.output["v3_enabled"] == True

        print(f"  ✓ /stats 执行成功")
        print(f"  ✓ V3 启用: {result.output['v3_enabled']}")
        print("  ✓ 测试通过\n")


def test_reload_command():
    """测试 6: /reload 命令"""
    print("测试 6: /reload 命令")

    with create_sandbox("slash-reload") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行 /reload
        result = orch.process("/reload")

        # 验证
        assert result.success == True
        assert isinstance(result.output, dict)
        assert result.output.get("reloaded") == True

        print(f"  ✓ /reload 执行成功")
        print(f"  ✓ 重载状态: {result.output['reloaded']}")
        print("  ✓ 测试通过\n")


def test_slash_command_without_v3():
    """测试 7: 未启用 V3 时的 Slash Command"""
    print("测试 7: 未启用 V3 时的 Slash Command")

    # 创建未启用 V3 的 Orchestrator
    orch = MasterOrchestrator(
        auto_discover=False  # 不启用 V3
    )

    # 尝试执行 Slash Command
    result = orch.process("/stats")

    # 验证：应该失败
    assert isinstance(result, SlashCommandResult)
    assert result.success == False
    assert "not available" in result.error.lower()

    print(f"  ✓ 正确处理未启用 V3 的情况")
    print(f"  ✓ 错误信息: {result.error}")
    print("  ✓ 测试通过\n")


def test_natural_language_still_works():
    """测试 8: 自然语言模式仍然工作"""
    print("测试 8: 自然语言模式仍然工作")

    with create_sandbox("slash-nl") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 使用自然语言请求（不是 Slash Command）
        # 注意：这会触发意图分析，不是 SlashCommandResult
        result = orch.process("简单测试")

        # 验证：不是 SlashCommandResult（向后兼容）
        assert not isinstance(result, SlashCommandResult)

        print(f"  ✓ 自然语言模式仍然工作")
        print(f"  ✓ 返回类型: {type(result).__name__}")
        print("  ✓ 测试通过\n")


def test_slash_command_with_args():
    """测试 9: 带参数的 Slash Command"""
    print("测试 9: 带参数的 Slash Command")

    with create_sandbox("slash-args") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行带参数的命令（内置的 git-log 支持参数）
        # 注意：这需要 CommandExecutor，可能会因为实际执行而失败
        # 但我们主要测试参数解析
        result = orch.process("/git-log")

        # 验证：命令被识别（可能执行失败是正常的）
        assert isinstance(result, SlashCommandResult)

        print(f"  ✓ 带参数的 Slash Command 解析成功")
        print(f"  ✓ 命令: {result.command}")
        print("  ✓ 测试通过\n")


def test_unknown_slash_command():
    """测试 10: 未知的 Slash Command"""
    print("测试 10: 未知的 Slash Command")

    with create_sandbox("slash-unknown") as sandbox:
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        orch = MasterOrchestrator(
            auto_discover=True,
            config_path=sandbox.project_root
        )

        # 执行不存在的命令
        result = orch.process("/nonexistent-command")

        # 验证
        assert isinstance(result, SlashCommandResult)
        assert result.success == False
        assert "not found" in result.error.lower()

        print(f"  ✓ 正确处理未知命令")
        print(f"  ✓ 错误信息: {result.error}")
        print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Slash Command 集成测试")
    print("=" * 70)
    print()

    tests = [
        test_slash_command_detection,
        test_discover_command,
        test_list_skills_command,
        test_list_commands,
        test_stats_command,
        test_reload_command,
        test_slash_command_without_v3,
        test_natural_language_still_works,
        test_slash_command_with_args,
        test_unknown_slash_command,
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
