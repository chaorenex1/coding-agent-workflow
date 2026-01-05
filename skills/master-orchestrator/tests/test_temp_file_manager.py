#!/usr/bin/env python3
"""
TempFileManager 单元测试
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.temp_file_manager import TempFileManager


def print_result(test_name: str, passed: bool, error: str = ""):
    """打印测试结果（Windows兼容版本）"""
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}")
    if error:
        print(f"      错误: {error}")


def test_initialization():
    """测试：初始化和目录创建"""
    print("\n[测试1] 初始化和目录创建...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"

            # 创建 TempFileManager
            manager = TempFileManager(temp_dir=temp_dir, ttl_seconds=3600)

            # 验证目录已创建
            assert temp_dir.exists(), "临时文件目录未创建"
            assert manager.temp_dir == temp_dir, "目录路径不匹配"
            assert manager.ttl_seconds == 3600, "TTL设置错误"

            print_result("初始化和目录创建", True)
            return True

    except Exception as e:
        print_result("初始化和目录创建", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_create_temp_file():
    """测试：创建临时文件"""
    print("\n[测试2] 创建临时文件...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            # 创建临时文件
            tmp_file = manager.create_temp_file(prefix="test_", suffix=".txt")

            # 验证文件已创建
            assert tmp_file.exists(), "临时文件未创建"
            assert tmp_file.parent.name == "default", "默认命名空间错误"
            assert tmp_file.name.startswith("test_"), "文件前缀错误"
            assert tmp_file.name.endswith(".txt"), "文件后缀错误"

            # 写入数据
            tmp_file.write_text("test data", encoding='utf-8')
            assert tmp_file.read_text(encoding='utf-8') == "test data", "文件读写失败"

            # 测试自定义命名空间
            tmp_file2 = manager.create_temp_file(namespace="custom")
            assert tmp_file2.parent.name == "custom", "自定义命名空间错误"

            print_result("创建临时文件", True)
            return True

    except Exception as e:
        print_result("创建临时文件", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_create_temp_dir():
    """测试：创建临时目录"""
    print("\n[测试3] 创建临时目录...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            # 创建临时目录
            tmp_subdir = manager.create_temp_dir(prefix="workspace_")

            # 验证目录已创建
            assert tmp_subdir.exists(), "临时目录未创建"
            assert tmp_subdir.is_dir(), "不是目录"
            assert tmp_subdir.name.startswith("workspace_"), "目录前缀错误"

            # 在临时目录中创建文件
            test_file = tmp_subdir / "test.txt"
            test_file.write_text("data", encoding='utf-8')
            assert test_file.exists(), "临时目录中的文件创建失败"

            print_result("创建临时目录", True)
            return True

    except Exception as e:
        print_result("创建临时目录", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_temp_file_context_manager():
    """测试：临时文件上下文管理器"""
    print("\n[测试4] 临时文件上下文管理器...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            tmp_path = None

            # 使用上下文管理器
            with manager.temp_file(prefix="ctx_", suffix=".json") as tmp_file:
                tmp_path = tmp_file

                # 在上下文中，文件应该存在
                assert tmp_file.exists(), "临时文件应该存在"

                # 写入数据
                tmp_file.write_text('{"key": "value"}', encoding='utf-8')

            # 离开上下文后，文件应该被删除
            assert not tmp_path.exists(), "临时文件应该被自动删除"

            print_result("临时文件上下文管理器", True)
            return True

    except Exception as e:
        print_result("临时文件上下文管理器", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_temp_dir_context_manager():
    """测试：临时目录上下文管理器"""
    print("\n[测试5] 临时目录上下文管理器...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            tmp_path = None

            # 使用上下文管理器
            with manager.temp_directory(prefix="workspace_") as tmp_subdir:
                tmp_path = tmp_subdir

                # 在上下文中，目录应该存在
                assert tmp_subdir.exists(), "临时目录应该存在"
                assert tmp_subdir.is_dir(), "应该是目录"

                # 在目录中创建文件
                test_file = tmp_subdir / "file.txt"
                test_file.write_text("data", encoding='utf-8')

            # 离开上下文后，目录和内容应该被删除
            assert not tmp_path.exists(), "临时目录应该被自动删除"

            print_result("临时目录上下文管理器", True)
            return True

    except Exception as e:
        print_result("临时目录上下文管理器", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_cleanup_expired():
    """测试：清理过期文件"""
    print("\n[测试6] 清理过期文件...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            # 使用较短的TTL（2秒）
            manager = TempFileManager(temp_dir=temp_dir, ttl_seconds=2)

            # 创建临时文件
            tmp_file1 = manager.create_temp_file(prefix="old_")
            tmp_file1.write_text("old data", encoding='utf-8')

            # 等待超过TTL
            print("  等待3秒以超过TTL...")
            time.sleep(3)

            # 创建新文件（不应被清理）
            tmp_file2 = manager.create_temp_file(prefix="new_")
            tmp_file2.write_text("new data", encoding='utf-8')

            # 清理过期文件
            removed = manager.cleanup_expired()

            # 验证
            assert removed >= 1, f"应该清理至少1个文件，实际清理了{removed}个"
            assert not tmp_file1.exists(), "过期文件应该被删除"
            assert tmp_file2.exists(), "新文件不应该被删除"

            print_result("清理过期文件", True)
            return True

    except Exception as e:
        print_result("清理过期文件", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_cleanup_namespace():
    """测试：清理命名空间"""
    print("\n[测试7] 清理命名空间...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            # 创建不同命名空间的文件
            file1 = manager.create_temp_file(namespace="ns1")
            file2 = manager.create_temp_file(namespace="ns2")
            file1.write_text("data1", encoding='utf-8')
            file2.write_text("data2", encoding='utf-8')

            # 验证文件存在
            assert file1.exists(), "ns1文件应该存在"
            assert file2.exists(), "ns2文件应该存在"

            # 清理ns1命名空间
            removed = manager.cleanup_namespace("ns1")

            # 验证
            assert removed >= 1, f"应该清理至少1个文件，实际清理了{removed}个"
            assert not file1.exists(), "ns1文件应该被删除"
            assert file2.exists(), "ns2文件不应该被删除"

            print_result("清理命名空间", True)
            return True

    except Exception as e:
        print_result("清理命名空间", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_cleanup_all():
    """测试：清理所有临时文件"""
    print("\n[测试8] 清理所有临时文件...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            # 创建多个文件
            file1 = manager.create_temp_file(namespace="ns1")
            file2 = manager.create_temp_file(namespace="ns2")
            dir1 = manager.create_temp_dir(namespace="ns3")

            file1.write_text("data1", encoding='utf-8')
            file2.write_text("data2", encoding='utf-8')
            (dir1 / "file.txt").write_text("data", encoding='utf-8')

            # 清理所有
            removed = manager.cleanup_all()

            # 验证
            assert removed >= 2, f"应该清理至少2个文件，实际清理了{removed}个"
            assert not file1.exists(), "所有文件应该被删除"
            assert not file2.exists(), "所有文件应该被删除"
            assert not dir1.exists(), "所有目录应该被删除"
            assert temp_dir.exists(), "根目录应该保留"

            print_result("清理所有临时文件", True)
            return True

    except Exception as e:
        print_result("清理所有临时文件", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_get_stats():
    """测试：获取统计信息"""
    print("\n[测试9] 获取统计信息...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir, ttl_seconds=3600)

            # 创建测试文件
            file1 = manager.create_temp_file(namespace="ns1")
            file2 = manager.create_temp_file(namespace="ns1")
            file3 = manager.create_temp_file(namespace="ns2")

            file1.write_text("data1", encoding='utf-8')
            file2.write_text("data2", encoding='utf-8')
            file3.write_text("data3", encoding='utf-8')

            # 获取统计信息
            stats = manager.get_stats()

            # 验证
            assert stats["status"] == "ok", "状态应该是ok"
            assert stats["total_files"] >= 3, f"应该有至少3个文件，实际{stats['total_files']}个"
            assert "ns1" in stats["namespaces"], "应该有ns1命名空间"
            assert "ns2" in stats["namespaces"], "应该有ns2命名空间"
            assert stats["namespaces"]["ns1"]["files"] >= 2, "ns1应该有2个文件"
            assert stats["namespaces"]["ns2"]["files"] >= 1, "ns2应该有1个文件"

            # 获取特定命名空间统计
            ns1_stats = manager.get_stats(namespace="ns1")
            assert "ns1" in ns1_stats["namespaces"], "应该只有ns1命名空间"
            assert "ns2" not in ns1_stats["namespaces"], "不应该有ns2命名空间"

            print_result("获取统计信息", True)
            return True

    except Exception as e:
        print_result("获取统计信息", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_list_namespaces():
    """测试：列出命名空间"""
    print("\n[测试10] 列出命名空间...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_dir = Path(tmp_dir) / "test_temp"
            manager = TempFileManager(temp_dir=temp_dir)

            # 初始应该没有命名空间
            namespaces = manager.list_namespaces()
            assert len(namespaces) == 0, "初始应该没有命名空间"

            # 创建不同命名空间的文件
            manager.create_temp_file(namespace="alpha")
            manager.create_temp_file(namespace="beta")
            manager.create_temp_file(namespace="gamma")

            # 获取命名空间列表
            namespaces = manager.list_namespaces()

            # 验证
            assert len(namespaces) == 3, f"应该有3个命名空间，实际{len(namespaces)}个"
            assert "alpha" in namespaces, "应该包含alpha"
            assert "beta" in namespaces, "应该包含beta"
            assert "gamma" in namespaces, "应该包含gamma"
            assert namespaces == sorted(namespaces), "命名空间应该按字母排序"

            print_result("列出命名空间", True)
            return True

    except Exception as e:
        print_result("列出命名空间", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("TempFileManager 单元测试")
    print("=" * 60)

    tests = [
        test_initialization,
        test_create_temp_file,
        test_create_temp_dir,
        test_temp_file_context_manager,
        test_temp_dir_context_manager,
        test_cleanup_expired,
        test_cleanup_namespace,
        test_cleanup_all,
        test_get_stats,
        test_list_namespaces
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[错误] 测试崩溃: {test_func.__name__}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
