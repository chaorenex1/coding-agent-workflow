#!/usr/bin/env python3
"""
TempFileManager 集成测试 - 验证目录结构和基本功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_temp_file_manager_integration():
    """测试：TempFileManager 在标准目录下的使用"""
    print("\n========== TempFileManager 集成测试 ==========\n")

    try:
        from core.temp_file_manager import TempFileManager

        # 测试使用标准缓存目录
        print("[1] 测试标准缓存目录...")
        cache_root = Path.home() / ".memex" / "orchestrator"
        temp_dir = cache_root / "temp"

        manager = TempFileManager(temp_dir=temp_dir, ttl_seconds=3600)

        # 验证目录已创建
        print(f"  - TempFileManager 已创建")
        print(f"  - 临时文件目录: {manager.temp_dir}")
        print(f"  - 目录存在: {manager.temp_dir.exists()}")
        print(f"  - TTL设置: {manager.ttl_seconds} 秒")

        assert manager.temp_dir.exists(), "临时文件目录应该存在"

        # 测试创建临时文件
        print(f"\n[2] 测试创建临时文件...")
        tmp_file = manager.create_temp_file(
            prefix="integration_test_",
            suffix=".json",
            namespace="test"
        )

        print(f"  - 临时文件已创建: {tmp_file}")
        print(f"  - 文件存在: {tmp_file.exists()}")
        print(f"  - 命名空间: {tmp_file.parent.name}")

        # 写入数据
        tmp_file.write_text('{"test": "integration"}', encoding='utf-8')
        content = tmp_file.read_text(encoding='utf-8')
        assert content == '{"test": "integration"}', "文件内容应该匹配"
        print(f"  - 读写数据成功")

        # 测试上下文管理器
        print(f"\n[3] 测试上下文管理器...")
        tmp_path = None
        with manager.temp_file(prefix="ctx_", suffix=".txt", namespace="test") as f:
            f.write_text("context test", encoding='utf-8')
            print(f"  - 上下文文件已创建: {f}")
            assert f.exists(), "上下文中文件应该存在"
            tmp_path = f

        print(f"  - 上下文结束后文件已删除: {not tmp_path.exists()}")
        assert not tmp_path.exists(), "离开上下文后文件应该被删除"

        # 获取统计信息
        print(f"\n[4] 获取统计信息...")
        stats = manager.get_stats(namespace="test")
        print(f"  - 状态: {stats.get('status')}")
        print(f"  - 文件数: {stats.get('total_files')}")

        if stats.get('namespaces'):
            for ns, ns_stats in stats['namespaces'].items():
                print(f"  - 命名空间 '{ns}': {ns_stats['files']} 文件, {ns_stats['size_bytes']} 字节")

        # 清理测试命名空间
        print(f"\n[5] 清理测试命名空间...")
        removed = manager.cleanup_namespace("test")
        print(f"  - 已清理 {removed} 个文件/目录")

        # 验证清理后的状态
        stats_after = manager.get_stats(namespace="test")
        print(f"  - 清理后文件数: {stats_after.get('total_files')}")

        print(f"\n========== 集成测试完成 ==========\n")
        print("[PASS] 所有测试通过")
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    return test_temp_file_manager_integration()


if __name__ == "__main__":
    sys.exit(main())
