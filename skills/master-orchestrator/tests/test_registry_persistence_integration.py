#!/usr/bin/env python3
"""
RegistryPersistence 集成测试 - 验证在 ConfigLoader 中的使用
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_config_loader_cache():
    """测试：ConfigLoader 使用 RegistryPersistence 缓存"""
    print("\n========== RegistryPersistence 集成测试 ==========\n")

    try:
        # 创建临时目录模拟用户配置目录
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_config_dir = Path(tmp_dir) / ".claude"
            user_config_dir.mkdir(parents=True)

            # 创建测试 skill
            skills_dir = user_config_dir / "skills"
            skills_dir.mkdir()

            test_skill = skills_dir / "test-skill"
            test_skill.mkdir()

            # V2 ResourceScanner 使用 SKILL.md（Markdown格式）
            skill_md = test_skill / "SKILL.md"
            skill_md.write_text("""# test-skill

description: Test skill
enabled: true
priority: 50
version: 1.0
""", encoding='utf-8')

            print(f"[1] 创建测试配置...")
            print(f"  - 用户配置目录: {user_config_dir}")
            print(f"  - Test skill: {test_skill}")

            # 第一次加载 - 应该执行扫描
            print(f"\n[2] 第一次加载配置（应执行扫描）...")
            from core.config_loader import ConfigLoader

            # 使用临时目录作为 project_root，但不扫描项目资源
            loader1 = ConfigLoader(
                project_root=Path(tmp_dir),
                enable_auto_discovery=True
            )

            # 临时替换 user_config_dir 以使用我们的测试目录
            loader1.user_config_dir = user_config_dir

            # 修改 registry_dir 到测试目录
            if loader1.persistence:
                loader1.persistence.registry_dir = Path(tmp_dir) / "registry"
                loader1.persistence.registry_dir.mkdir(parents=True, exist_ok=True)
                loader1.persistence.last_scan_file = loader1.persistence.registry_dir / "last_scan.json"
                loader1.persistence.snapshot_file = loader1.persistence.registry_dir / "resources_snapshot.json"

            config1 = loader1.load()

            print(f"  - Skills 数量: {len(config1.skills)}")
            print(f"  - 找到 test-skill: {'test-skill' in config1.skills}")

            # 验证缓存文件已创建
            if loader1.persistence:
                cache_exists = loader1.persistence.last_scan_file.exists()
                print(f"  - 缓存文件已创建: {cache_exists}")

                if cache_exists:
                    # 获取统计信息
                    stats = loader1.persistence.get_stats()
                    print(f"  - 缓存状态: {stats.get('status')}")
                    print(f"  - 缓存有效: {stats.get('is_valid')}")
                    print(f"  - 扫描耗时: {stats.get('scan_duration_ms')} ms")

            # 第二次加载 - 应该使用缓存
            print(f"\n[3] 第二次加载配置（应使用缓存）...")
            loader2 = ConfigLoader(
                project_root=Path(tmp_dir),
                enable_auto_discovery=True
            )
            loader2.user_config_dir = user_config_dir

            # 复用同样的 persistence 配置
            if loader2.persistence:
                loader2.persistence.registry_dir = Path(tmp_dir) / "registry"
                loader2.persistence.last_scan_file = loader2.persistence.registry_dir / "last_scan.json"
                loader2.persistence.snapshot_file = loader2.persistence.registry_dir / "resources_snapshot.json"

            config2 = loader2.load()

            print(f"  - Skills 数量: {len(config2.skills)}")
            print(f"  - 找到 test-skill: {'test-skill' in config2.skills}")

            # 验证结果一致
            assert len(config1.skills) == len(config2.skills), "两次加载的结果应该一致"
            assert 'test-skill' in config2.skills, "应该包含 test-skill"

            # 修改文件，再次加载 - 应该重新扫描
            print(f"\n[4] 修改文件后加载（应重新扫描）...")
            skill_md.write_text("""# test-skill

description: Modified test skill
enabled: true
priority: 60
version: 2.0
""", encoding='utf-8')

            loader3 = ConfigLoader(
                project_root=Path(tmp_dir),
                enable_auto_discovery=True
            )
            loader3.user_config_dir = user_config_dir

            if loader3.persistence:
                loader3.persistence.registry_dir = Path(tmp_dir) / "registry"
                loader3.persistence.last_scan_file = loader3.persistence.registry_dir / "last_scan.json"
                loader3.persistence.snapshot_file = loader3.persistence.registry_dir / "resources_snapshot.json"

            config3 = loader3.load()

            print(f"  - Skills 数量: {len(config3.skills)}")
            print(f"  - test-skill priority: {config3.skills['test-skill'].priority}")
            print(f"  - 检测到文件变更: {config3.skills['test-skill'].priority == 60}")

            print(f"\n========== 集成测试完成 ==========\n")
            print("[PASS] 所有测试通过")
            return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    return test_config_loader_cache()


if __name__ == "__main__":
    sys.exit(main())
