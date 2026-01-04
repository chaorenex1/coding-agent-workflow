#!/usr/bin/env python3
"""
Slash Command 系统单元测试

测试 Slash Command 注册、执行、handlers 等功能。
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

from orchestrator.core.slash_command import (
    SlashCommandMetadata, SlashCommandResult, SlashCommandType,
    SystemCommandHandler, ShellCommandHandler
)
from orchestrator.core.slash_command_registry import (
    SlashCommandRegistry, register_builtin_commands
)


# Mock Orchestrator for testing
class MockOrchestrator:
    """Mock MasterOrchestrator for testing."""

    def __init__(self):
        self.backend_orch = None
        self.registry = None
        self.factory = None
        self._auto_discover_called = False
        self._list_skills_called = False
        self._reload_config_called = False

    def _auto_discover(self, **kwargs):
        """Mock auto discover."""
        self._auto_discover_called = True
        return {"total_resources": 10, "by_type": {"skill": 5}}

    def _list_skills(self, **kwargs):
        """Mock list skills."""
        self._list_skills_called = True
        return [{"name": "skill-1"}, {"name": "skill-2"}]

    def _reload_config(self, **kwargs):
        """Mock reload config."""
        self._reload_config_called = True
        return {"reloaded": True}

    def _list_slash_commands(self, **kwargs):
        """Mock list slash commands."""
        return []

    def _get_stats(self, **kwargs):
        """Mock get stats."""
        return {"v3_enabled": True}


def test_slash_command_metadata():
    """测试 1: SlashCommandMetadata 数据结构"""
    print("测试 1: SlashCommandMetadata 数据结构")

    # 创建系统命令
    cmd = SlashCommandMetadata(
        name="discover",
        type=SlashCommandType.SYSTEM,
        description="Auto-discover resources",
        handler="_auto_discover",
        enabled=True,
        priority=100,
        source="builtin"
    )

    # 验证属性
    assert cmd.name == "discover"
    assert cmd.type == SlashCommandType.SYSTEM
    assert cmd.full_name == "/discover"
    assert cmd.handler == "_auto_discover"
    assert cmd.enabled == True

    print(f"  ✓ SlashCommandMetadata: {cmd}")
    print("  ✓ 测试通过\n")


def test_slash_command_result():
    """测试 2: SlashCommandResult 数据结构"""
    print("测试 2: SlashCommandResult 数据结构")

    # 成功结果
    result = SlashCommandResult(
        command="/discover",
        success=True,
        output={"resources": 10},
        duration_seconds=0.5
    )

    assert result.command == "/discover"
    assert result.success == True
    assert result.output == {"resources": 10}
    assert result.error is None

    # 失败结果
    error_result = SlashCommandResult(
        command="/unknown",
        success=False,
        error="Command not found"
    )

    assert error_result.success == False
    assert error_result.error == "Command not found"

    print(f"  ✓ 成功结果: {result}")
    print(f"  ✓ 失败结果: {error_result}")
    print("  ✓ 测试通过\n")


def test_registry_registration():
    """测试 3: 命令注册"""
    print("测试 3: 命令注册")

    registry = SlashCommandRegistry()

    # 注册命令
    cmd = SlashCommandMetadata(
        name="test-cmd",
        type=SlashCommandType.SYSTEM,
        description="Test command",
        handler="_test_handler",
        enabled=True,
        priority=50,
        source="builtin"
    )

    success = registry.register(cmd)
    assert success == True

    # 验证注册
    retrieved = registry.get("test-cmd")
    assert retrieved is not None
    assert retrieved.name == "test-cmd"
    assert registry.exists("test-cmd")

    print(f"  ✓ 命令注册成功: {retrieved}")
    print("  ✓ 测试通过\n")


def test_priority_override():
    """测试 4: 优先级覆盖"""
    print("测试 4: 优先级覆盖")

    registry = SlashCommandRegistry()

    # 注册低优先级命令
    low_priority = SlashCommandMetadata(
        name="common",
        type=SlashCommandType.SHELL,
        description="Common command",
        command="echo low",
        priority=10,
        source="builtin",
        enabled=True
    )
    registry.register(low_priority)

    # 注册高优先级命令（同名）
    high_priority = SlashCommandMetadata(
        name="common",
        type=SlashCommandType.SHELL,
        description="Common command (project)",
        command="echo high",
        priority=100,
        source="project",
        enabled=True
    )
    registry.register(high_priority)

    # 验证高优先级覆盖
    retrieved = registry.get("common")
    assert retrieved.priority == 100
    assert retrieved.source == "project"
    assert retrieved.command == "echo high"

    print(f"  ✓ 高优先级覆盖低优先级: priority={retrieved.priority}")
    print("  ✓ 测试通过\n")


def test_list_commands():
    """测试 5: 列出命令"""
    print("测试 5: 列出命令")

    registry = SlashCommandRegistry()

    # 注册多个命令
    commands = [
        SlashCommandMetadata("cmd1", SlashCommandType.SYSTEM, "Cmd 1", handler="_h1", enabled=True, priority=50, source="builtin"),
        SlashCommandMetadata("cmd2", SlashCommandType.SHELL, "Cmd 2", command="echo 2", enabled=True, priority=60, source="user"),
        SlashCommandMetadata("cmd3", SlashCommandType.SKILL, "Cmd 3", skill="skill-3", enabled=False, priority=70, source="project"),
    ]

    for cmd in commands:
        registry.register(cmd)

    # 测试过滤
    all_cmds = registry.list_commands(enabled_only=False)
    assert len(all_cmds) == 3

    enabled_only = registry.list_commands(enabled_only=True)
    assert len(enabled_only) == 2

    system_only = registry.list_commands(type_filter=SlashCommandType.SYSTEM)
    assert len(system_only) == 1
    assert system_only[0].name == "cmd1"

    print(f"  ✓ 全部命令: {len(all_cmds)}")
    print(f"  ✓ 启用命令: {len(enabled_only)}")
    print(f"  ✓ 系统命令: {len(system_only)}")
    print("  ✓ 测试通过\n")


def test_system_command_handler():
    """测试 6: 系统命令 Handler"""
    print("测试 6: 系统命令 Handler")

    # 创建 Mock Orchestrator
    orch = MockOrchestrator()

    # 创建 Handler
    handler = SystemCommandHandler(orchestrator=orch)

    # 创建命令
    cmd = SlashCommandMetadata(
        name="discover",
        type=SlashCommandType.SYSTEM,
        description="Auto-discover",
        handler="_auto_discover",
        enabled=True,
        priority=100,
        source="builtin"
    )

    # 执行命令
    result = handler.execute(cmd, [], {})

    # 验证
    assert result.success == True
    assert orch._auto_discover_called == True
    assert result.output == {"total_resources": 10, "by_type": {"skill": 5}}

    print(f"  ✓ 系统命令执行成功: {result}")
    print("  ✓ 测试通过\n")


def test_registry_execute():
    """测试 7: Registry 执行命令"""
    print("测试 7: Registry 执行命令")

    # 创建 Registry 和 Orchestrator
    orch = MockOrchestrator()
    registry = SlashCommandRegistry(orchestrator=orch)

    # 注册命令
    cmd = SlashCommandMetadata(
        name="discover",
        type=SlashCommandType.SYSTEM,
        description="Auto-discover",
        handler="_auto_discover",
        enabled=True,
        priority=100,
        source="builtin"
    )
    registry.register(cmd)

    # 执行命令（带 /）
    result = registry.execute("/discover")
    assert result.success == True
    assert orch._auto_discover_called == True

    # 执行命令（不带 /）
    orch._auto_discover_called = False
    result = registry.execute("discover")
    assert result.success == True
    assert orch._auto_discover_called == True

    print(f"  ✓ Registry 执行成功")
    print("  ✓ 测试通过\n")


def test_command_not_found():
    """测试 8: 命令不存在"""
    print("测试 8: 命令不存在")

    registry = SlashCommandRegistry()

    # 执行不存在的命令
    result = registry.execute("nonexistent")

    assert result.success == False
    assert "not found" in result.error.lower()

    print(f"  ✓ 正确处理不存在的命令: {result.error}")
    print("  ✓ 测试通过\n")


def test_disabled_command():
    """测试 9: 禁用命令"""
    print("测试 9: 禁用命令")

    registry = SlashCommandRegistry()

    # 注册禁用命令
    cmd = SlashCommandMetadata(
        name="disabled-cmd",
        type=SlashCommandType.SYSTEM,
        description="Disabled command",
        handler="_handler",
        enabled=False,  # 禁用
        priority=50,
        source="builtin"
    )
    registry.register(cmd)

    # 尝试执行
    result = registry.execute("disabled-cmd")

    assert result.success == False
    assert "disabled" in result.error.lower()

    print(f"  ✓ 正确阻止禁用命令: {result.error}")
    print("  ✓ 测试通过\n")


def test_builtin_commands_registration():
    """测试 10: 内置命令注册"""
    print("测试 10: 内置命令注册")

    registry = SlashCommandRegistry()

    # 注册内置命令
    register_builtin_commands(registry)

    # 验证系统命令
    assert registry.exists("discover")
    assert registry.exists("list-skills")
    assert registry.exists("list-commands")
    assert registry.exists("reload")
    assert registry.exists("stats")

    # 验证 Shell 命令
    assert registry.exists("git-status")
    assert registry.exists("git-log")
    assert registry.exists("npm-test")

    # 统计
    stats = registry.get_stats()
    print(f"  ✓ 注册了 {stats['total_commands']} 个内置命令")
    print(f"  ✓ 系统命令: {stats['by_type'].get('system', 0)}")
    print(f"  ✓ Shell 命令: {stats['by_type'].get('shell', 0)}")
    print("  ✓ 测试通过\n")


def test_registry_stats():
    """测试 11: Registry 统计"""
    print("测试 11: Registry 统计")

    registry = SlashCommandRegistry()

    # 注册多个命令
    commands = [
        SlashCommandMetadata("s1", SlashCommandType.SYSTEM, "S1", handler="_h1", enabled=True, priority=50, source="builtin"),
        SlashCommandMetadata("s2", SlashCommandType.SYSTEM, "S2", handler="_h2", enabled=False, priority=50, source="user"),
        SlashCommandMetadata("sh1", SlashCommandType.SHELL, "SH1", command="echo 1", enabled=True, priority=50, source="project"),
    ]

    for cmd in commands:
        registry.register(cmd)

    stats = registry.get_stats()

    assert stats["total_commands"] == 3
    assert stats["enabled_commands"] == 2
    assert stats["disabled_commands"] == 1
    assert stats["by_type"]["system"] == 2
    assert stats["by_type"]["shell"] == 1
    assert stats["by_source"]["builtin"] == 1
    assert stats["by_source"]["user"] == 1
    assert stats["by_source"]["project"] == 1

    print(f"  ✓ 统计信息:")
    print(f"    总命令: {stats['total_commands']}")
    print(f"    启用: {stats['enabled_commands']}")
    print(f"    按类型: {stats['by_type']}")
    print(f"    按来源: {stats['by_source']}")
    print("  ✓ 测试通过\n")


def test_registry_clear():
    """测试 12: Registry 清空"""
    print("测试 12: Registry 清空")

    registry = SlashCommandRegistry()

    # 注册命令
    cmd = SlashCommandMetadata(
        name="test",
        type=SlashCommandType.SYSTEM,
        description="Test",
        handler="_h",
        enabled=True,
        priority=50,
        source="builtin"
    )
    registry.register(cmd)

    assert len(registry) == 1

    # 清空
    registry.clear()

    assert len(registry) == 0
    assert not registry.exists("test")

    print(f"  ✓ Registry 清空成功")
    print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Slash Command 系统单元测试")
    print("=" * 70)
    print()

    tests = [
        test_slash_command_metadata,
        test_slash_command_result,
        test_registry_registration,
        test_priority_override,
        test_list_commands,
        test_system_command_handler,
        test_registry_execute,
        test_command_not_found,
        test_disabled_command,
        test_builtin_commands_registration,
        test_registry_stats,
        test_registry_clear,
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
