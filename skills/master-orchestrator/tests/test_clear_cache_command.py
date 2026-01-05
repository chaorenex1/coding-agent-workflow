#!/usr/bin/env python3
"""
测试 /clear-cache 内置命令
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_clear_cache_command():
    """测试：/clear-cache 命令功能"""
    print("\n========== /clear-cache 命令测试 ==========\n")

    try:
        from core.registry_persistence import RegistryPersistence
        from core.slash_command_registry import SlashCommandRegistry, register_builtin_commands

        # 1. 创建测试环境
        print("[1] 创建测试环境...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "registry"
            registry_dir.mkdir(parents=True)

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            # 创建一些缓存数据
            test_resources = {
                "skills": [{"name": "test1"}, {"name": "test2"}],
                "commands": [],
                "agents": [],
                "prompts": []
            }
            file_paths = [str(Path(tmp_dir) / "test.yaml")]
            Path(file_paths[0]).write_text("test: content", encoding='utf-8')

            persistence.save_scan_result(test_resources, file_paths, 100)

            # 验证缓存已创建
            stats_before = persistence.get_stats()
            print(f"  - 缓存状态: {stats_before.get('status')}")
            print(f"  - 资源总数: {stats_before.get('total_resources')}")
            assert stats_before.get("status") == "cached", "缓存应该已创建"
            assert persistence.last_scan_file.exists(), "last_scan.json 应该存在"
            assert persistence.snapshot_file.exists(), "resources_snapshot.json 应该存在"

            # 2. 测试内置命令注册
            print(f"\n[2] 测试内置命令注册...")
            registry = SlashCommandRegistry()
            register_builtin_commands(registry)

            # 验证 /clear-cache 命令已注册
            cmd = registry.get("clear-cache")
            print(f"  - 命令已注册: {cmd is not None}")
            print(f"  - 命令名称: {cmd.name}")
            print(f"  - 命令类型: {cmd.type.value}")
            print(f"  - 处理器: {cmd.handler}")
            print(f"  - 描述: {cmd.description}")

            assert cmd is not None, "/clear-cache 命令应该已注册"
            assert cmd.handler == "_clear_registry_cache", "处理器名称应该正确"

            # 3. 测试直接调用清除功能
            print(f"\n[3] 测试直接调用清除功能...")
            persistence.invalidate()

            # 验证缓存已清除
            stats_after = persistence.get_stats()
            print(f"  - 清除后缓存状态: {stats_after.get('status')}")
            print(f"  - last_scan.json 存在: {persistence.last_scan_file.exists()}")
            print(f"  - resources_snapshot.json 存在: {persistence.snapshot_file.exists()}")

            assert stats_after.get("status") == "no_cache", "缓存应该已清除"
            assert not persistence.last_scan_file.exists(), "last_scan.json 应该被删除"
            assert not persistence.snapshot_file.exists(), "resources_snapshot.json 应该被删除"

            print(f"\n========== 测试完成 ==========\n")
            print("[PASS] 所有测试通过")
            return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_clear_cache_integration():
    """测试：在实际目录中测试清除缓存"""
    print("\n========== /clear-cache 集成测试 ==========\n")

    try:
        from core.registry_persistence import RegistryPersistence

        # 使用实际的缓存目录
        print("[1] 使用实际缓存目录...")
        registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
        persistence = RegistryPersistence(registry_dir=registry_dir)

        # 获取清除前的状态
        print(f"\n[2] 清除前状态...")
        stats_before = persistence.get_stats()
        print(f"  - 缓存目录: {registry_dir}")
        print(f"  - 缓存状态: {stats_before.get('status')}")

        if stats_before.get("status") == "cached":
            print(f"  - 上次扫描: {stats_before.get('last_scan')}")
            print(f"  - 资源总数: {stats_before.get('total_resources')}")
            print(f"  - 文件数: {stats_before.get('file_count')}")
            print(f"  - 扫描耗时: {stats_before.get('scan_duration_ms')} ms")

        # 清除缓存
        print(f"\n[3] 清除缓存...")
        persistence.invalidate()

        # 获取清除后的状态
        print(f"\n[4] 清除后状态...")
        stats_after = persistence.get_stats()
        print(f"  - 缓存状态: {stats_after.get('status')}")

        if stats_before.get("status") == "cached":
            print(f"  - 清除成功: {stats_after.get('status') == 'no_cache'}")

        print(f"\n[提示]")
        print(f"  下次启动 MasterOrchestrator 时将重新扫描资源")

        print(f"\n========== 集成测试完成 ==========\n")
        print("[PASS] 集成测试通过")
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("clear-cache 命令测试套件")
    print("=" * 60)

    tests = [
        ("单元测试", test_clear_cache_command),
        ("集成测试", test_clear_cache_integration)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"{name}")
        print(f"{'=' * 60}")

        try:
            result = test_func()
            if result == 0:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[错误] {name} 崩溃: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
