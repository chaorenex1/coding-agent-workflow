#!/usr/bin/env python3
"""
RegistryPersistence 单元测试
"""

import sys
import os
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.registry_persistence import RegistryPersistence


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
            registry_dir = Path(tmp_dir) / "test_registry"

            # 创建 RegistryPersistence
            persistence = RegistryPersistence(
                registry_dir=registry_dir,
                ttl_seconds=3600
            )

            # 验证目录已创建
            assert registry_dir.exists(), "注册表目录未创建"
            assert persistence.registry_dir == registry_dir, "目录路径不匹配"
            assert persistence.ttl_seconds == 3600, "TTL设置错误"

            # 验证文件路径
            assert persistence.last_scan_file == registry_dir / "last_scan.json"
            assert persistence.snapshot_file == registry_dir / "resources_snapshot.json"

            print_result("初始化和目录创建", True)
            return True

    except Exception as e:
        print_result("初始化和目录创建", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_save_and_load_basic():
    """测试：基本的保存和加载"""
    print("\n[测试2] 基本的保存和加载...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            # 准备测试数据
            resources = {
                "skills": [
                    {"name": "skill1", "path": "/path/to/skill1"},
                    {"name": "skill2", "path": "/path/to/skill2"}
                ],
                "commands": [
                    {"name": "cmd1", "handler": "handler1"}
                ],
                "agents": [],
                "prompts": []
            }
            file_paths = [str(test_file)]
            scan_duration_ms = 150

            # 保存扫描结果
            persistence.save_scan_result(resources, file_paths, scan_duration_ms)

            # 验证文件已创建
            assert persistence.last_scan_file.exists(), "last_scan.json 未创建"
            assert persistence.snapshot_file.exists(), "resources_snapshot.json 未创建"

            # 验证 last_scan.json 内容
            with open(persistence.last_scan_file, 'r', encoding='utf-8') as f:
                last_scan = json.load(f)

            assert last_scan["skills_count"] == 2, "skills数量错误"
            assert last_scan["commands_count"] == 1, "commands数量错误"
            assert last_scan["scan_duration_ms"] == 150, "扫描耗时错误"
            assert str(test_file) in last_scan["file_hashes"], "文件哈希缺失"

            # 加载缓存（应该成功）
            loaded = persistence.load_cached_resources(file_paths)

            assert loaded is not None, "加载缓存失败"
            assert len(loaded["skills"]) == 2, "加载的skills数量错误"
            assert len(loaded["commands"]) == 1, "加载的commands数量错误"

            print_result("基本的保存和加载", True)
            return True

    except Exception as e:
        print_result("基本的保存和加载", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_ttl_expiration():
    """测试：TTL过期机制"""
    print("\n[测试3] TTL过期机制...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            # 使用较短的TTL（2秒）
            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=2)

            resources = {
                "skills": [{"name": "skill1"}],
                "commands": [],
                "agents": [],
                "prompts": []
            }
            file_paths = [str(test_file)]

            # 保存扫描结果
            persistence.save_scan_result(resources, file_paths, 100)

            # 立即加载（应该成功）
            loaded = persistence.load_cached_resources(file_paths)
            assert loaded is not None, "缓存应该有效"

            # 等待超过TTL
            print("  等待3秒以超过TTL...")
            time.sleep(3)

            # 再次加载（应该失败 - 缓存过期）
            loaded = persistence.load_cached_resources(file_paths)
            assert loaded is None, "缓存应该已过期"

            print_result("TTL过期机制", True)
            return True

    except Exception as e:
        print_result("TTL过期机制", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_file_change_detection():
    """测试：文件变更检测"""
    print("\n[测试4] 文件变更检测...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            resources = {
                "skills": [{"name": "skill1"}],
                "commands": [],
                "agents": [],
                "prompts": []
            }
            file_paths = [str(test_file)]

            # 保存初始状态
            persistence.save_scan_result(resources, file_paths, 100)

            # 加载（应该成功）
            loaded = persistence.load_cached_resources(file_paths)
            assert loaded is not None, "初始加载失败"

            # 修改文件内容
            test_file.write_text("test: modified content", encoding='utf-8')

            # 再次加载（应该失败 - 文件已变更）
            loaded = persistence.load_cached_resources(file_paths)
            assert loaded is None, "应该检测到文件变更"

            print_result("文件变更检测", True)
            return True

    except Exception as e:
        print_result("文件变更检测", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_file_list_change_detection():
    """测试：文件列表变更检测"""
    print("\n[测试5] 文件列表变更检测...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file1 = Path(tmp_dir) / "test1.yaml"
            test_file2 = Path(tmp_dir) / "test2.yaml"
            test_file1.write_text("test1: content", encoding='utf-8')
            test_file2.write_text("test2: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            resources = {"skills": [], "commands": [], "agents": [], "prompts": []}

            # 保存只包含 file1 的扫描
            persistence.save_scan_result(resources, [str(test_file1)], 100)

            # 加载 file1（成功）
            loaded = persistence.load_cached_resources([str(test_file1)])
            assert loaded is not None, "单文件加载失败"

            # 尝试加载 file1 + file2（应该失败 - 文件列表变更）
            loaded = persistence.load_cached_resources([str(test_file1), str(test_file2)])
            assert loaded is None, "应该检测到文件列表变更（新增）"

            # 保存 file1 + file2
            persistence.save_scan_result(resources, [str(test_file1), str(test_file2)], 100)

            # 尝试只加载 file1（应该失败 - 文件列表变更）
            loaded = persistence.load_cached_resources([str(test_file1)])
            assert loaded is None, "应该检测到文件列表变更（减少）"

            print_result("文件列表变更检测", True)
            return True

    except Exception as e:
        print_result("文件列表变更检测", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_invalidate():
    """测试：清除缓存"""
    print("\n[测试6] 清除缓存...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            resources = {"skills": [{"name": "skill1"}], "commands": [], "agents": [], "prompts": []}
            file_paths = [str(test_file)]

            # 保存扫描结果
            persistence.save_scan_result(resources, file_paths, 100)

            # 验证文件存在
            assert persistence.last_scan_file.exists(), "快照文件未创建"
            assert persistence.snapshot_file.exists(), "资源文件未创建"

            # 清除缓存
            persistence.invalidate()

            # 验证文件已删除
            assert not persistence.last_scan_file.exists(), "last_scan.json 应该被删除"
            assert not persistence.snapshot_file.exists(), "resources_snapshot.json 应该被删除"

            # 加载（应该失败）
            loaded = persistence.load_cached_resources(file_paths)
            assert loaded is None, "清除后不应该能加载缓存"

            print_result("清除缓存", True)
            return True

    except Exception as e:
        print_result("清除缓存", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_get_stats():
    """测试：获取统计信息"""
    print("\n[测试7] 获取统计信息...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            # 无缓存时的统计
            stats = persistence.get_stats()
            assert stats["status"] == "no_cache", "应该返回 no_cache 状态"

            # 保存扫描结果
            resources = {
                "skills": [{"name": "s1"}, {"name": "s2"}],
                "commands": [{"name": "c1"}],
                "agents": [],
                "prompts": [{"name": "p1"}]
            }
            file_paths = [str(test_file)]
            scan_duration_ms = 200

            persistence.save_scan_result(resources, file_paths, scan_duration_ms)

            # 获取统计信息
            stats = persistence.get_stats()

            assert stats["status"] == "cached", "应该返回 cached 状态"
            assert stats["is_valid"] is True, "缓存应该有效"
            assert stats["total_resources"] == 4, "资源总数应该是4"
            assert stats["scan_duration_ms"] == 200, "扫描耗时错误"
            assert stats["file_count"] == 1, "文件数量错误"
            assert stats["ttl_seconds"] == 3600, "TTL错误"
            assert stats["age_seconds"] >= 0, "年龄应该>=0"

            print_result("获取统计信息", True)
            return True

    except Exception as e:
        print_result("获取统计信息", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_resource_serialization():
    """测试：资源序列化"""
    print("\n[测试8] 资源序列化...")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            registry_dir = Path(tmp_dir) / "test_registry"
            test_file = Path(tmp_dir) / "test_config.yaml"
            test_file.write_text("test: content", encoding='utf-8')

            persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)

            # 测试各种类型的资源
            class SimpleObject:
                def __init__(self, name, value):
                    self.name = name
                    self.value = value

            class ObjectWithToDict:
                def __init__(self, name):
                    self.name = name
                def to_dict(self):
                    return {"name": self.name, "method": "to_dict"}

            resources = {
                "dicts": [
                    {"type": "plain_dict", "id": 1},
                    {"type": "plain_dict", "id": 2}
                ],
                "objects": [
                    SimpleObject("obj1", 100),
                    ObjectWithToDict("obj2")
                ]
            }

            file_paths = [str(test_file)]
            persistence.save_scan_result(resources, file_paths, 100)

            # 加载并验证
            loaded = persistence.load_cached_resources(file_paths)

            assert loaded is not None, "加载失败"
            assert len(loaded["dicts"]) == 2, "字典数量错误"
            assert len(loaded["objects"]) == 2, "对象数量错误"

            # 验证字典资源
            assert loaded["dicts"][0]["type"] == "plain_dict"

            # 验证对象序列化（通过 __dict__）
            assert loaded["objects"][0]["name"] == "obj1"
            assert loaded["objects"][0]["value"] == 100

            # 验证对象序列化（通过 to_dict()）
            assert loaded["objects"][1]["name"] == "obj2"
            assert loaded["objects"][1]["method"] == "to_dict"

            print_result("资源序列化", True)
            return True

    except Exception as e:
        print_result("资源序列化", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("RegistryPersistence 单元测试")
    print("=" * 60)

    tests = [
        test_initialization,
        test_save_and_load_basic,
        test_ttl_expiration,
        test_file_change_detection,
        test_file_list_change_detection,
        test_invalidate,
        test_get_stats,
        test_resource_serialization
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
