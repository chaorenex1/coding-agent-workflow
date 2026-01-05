#!/usr/bin/env python3
"""
演示 /clear-cache 命令的使用

这个脚本展示了如何使用内置的 /clear-cache 命令来清除注册表缓存。
"""

import sys
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_clear_cache_direct():
    """演示：直接调用 RegistryPersistence"""
    print("\n" + "=" * 60)
    print("演示 1: 直接使用 RegistryPersistence API")
    print("=" * 60 + "\n")

    from core.registry_persistence import RegistryPersistence

    # 创建 persistence 实例
    registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
    persistence = RegistryPersistence(registry_dir=registry_dir)

    # 1. 查看当前缓存状态
    print("[1] 当前缓存状态:")
    stats = persistence.get_stats()
    print(f"  - 状态: {stats.get('status')}")

    if stats.get("status") == "cached":
        print(f"  - 上次扫描: {stats.get('last_scan')}")
        print(f"  - 资源总数: {stats.get('total_resources')}")
        print(f"  - 文件数: {stats.get('file_count')}")
        print(f"  - 扫描耗时: {stats.get('scan_duration_ms')} ms")
        print(f"  - 缓存年龄: {stats.get('age_seconds')} 秒")
        print(f"  - TTL: {stats.get('ttl_seconds')} 秒")
        print(f"  - 是否有效: {stats.get('is_valid')}")
    elif stats.get("status") == "no_cache":
        print(f"  - 当前没有缓存")
    else:
        print(f"  - 状态异常: {stats.get('error')}")

    # 2. 清除缓存
    print(f"\n[2] 清除缓存...")
    persistence.invalidate()
    print(f"  - 缓存已清除")

    # 3. 验证清除结果
    print(f"\n[3] 清除后状态:")
    stats_after = persistence.get_stats()
    print(f"  - 状态: {stats_after.get('status')}")

    print(f"\n[提示] 下次启动 MasterOrchestrator 时将重新扫描资源\n")


def demo_slash_command():
    """演示：通过 Slash Command 系统调用"""
    print("\n" + "=" * 60)
    print("演示 2: 通过 Slash Command 注册表调用")
    print("=" * 60 + "\n")

    from core.slash_command_registry import SlashCommandRegistry, register_builtin_commands
    from core.registry_persistence import RegistryPersistence

    # 1. 设置测试环境
    print("[1] 设置测试环境...")
    registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
    persistence = RegistryPersistence(registry_dir=registry_dir)

    # 创建一些测试缓存
    if persistence.get_stats().get("status") == "no_cache":
        print("  - 创建测试缓存...")
        test_resources = {
            "skills": [{"name": "demo-skill"}],
            "commands": [],
            "agents": [],
            "prompts": []
        }
        test_file = registry_dir / "test.yaml"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test: content", encoding='utf-8')

        persistence.save_scan_result(test_resources, [str(test_file)], 50)
        print("  - 测试缓存已创建")

    # 2. 注册内置命令
    print(f"\n[2] 注册内置命令...")
    registry = SlashCommandRegistry()
    register_builtin_commands(registry)

    # 3. 查找 clear-cache 命令
    print(f"\n[3] 查找 /clear-cache 命令...")
    cmd = registry.get("clear-cache")

    if cmd:
        print(f"  - 命令名称: {cmd.name}")
        print(f"  - 命令类型: {cmd.type.value}")
        print(f"  - 处理器: {cmd.handler}")
        print(f"  - 描述: {cmd.description}")
        print(f"  - 示例: {', '.join(cmd.examples)}")
    else:
        print(f"  - 命令未找到")
        return

    # 4. 模拟执行命令的效果（直接调用 persistence）
    print(f"\n[4] 模拟执行命令...")
    stats_before = persistence.get_stats()
    print(f"  - 执行前缓存状态: {stats_before.get('status')}")

    persistence.invalidate()

    stats_after = persistence.get_stats()
    print(f"  - 执行后缓存状态: {stats_after.get('status')}")

    print(f"\n[提示] 在实际使用中，通过 MasterOrchestrator.process('/clear-cache') 调用\n")


def demo_list_all_commands():
    """演示：列出所有内置命令"""
    print("\n" + "=" * 60)
    print("演示 3: 列出所有内置 Slash Commands")
    print("=" * 60 + "\n")

    from core.slash_command_registry import SlashCommandRegistry, register_builtin_commands

    # 注册内置命令
    registry = SlashCommandRegistry()
    register_builtin_commands(registry)

    # 列出所有命令
    commands = registry.list_commands()

    print(f"共注册 {len(commands)} 个命令:\n")

    # 按类型分组
    by_type = {}
    for cmd in commands:
        cmd_type = cmd.type.value
        if cmd_type not in by_type:
            by_type[cmd_type] = []
        by_type[cmd_type].append(cmd)

    # 打印每个类型的命令
    for cmd_type, cmd_list in sorted(by_type.items()):
        print(f"[{cmd_type.upper()}]")
        for cmd in cmd_list:
            print(f"  /{cmd.name:<20} - {cmd.description}")
        print()


def main():
    """运行所有演示"""
    print("\n" + "=" * 60)
    print("/clear-cache 命令演示")
    print("=" * 60)

    demos = [
        demo_clear_cache_direct,
        demo_slash_command,
        demo_list_all_commands
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n[错误] 演示失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
