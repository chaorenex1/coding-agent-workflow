#!/usr/bin/env python3
"""
测试 ResourceScannerV2 在 ConfigLoader 中的集成
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_v2_scanner_integration():
    """测试：ConfigLoader 使用 ResourceScannerV2"""
    print("\n========== ResourceScannerV2 集成测试 ==========\n")

    try:
        from core.config_loader import ConfigLoader

        # 创建临时测试环境
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)

            # 创建测试 skill 目录结构
            skills_dir = project_root / "skills"
            skills_dir.mkdir()

            # 创建一个简单的 skill
            test_skill = skills_dir / "test-skill"
            test_skill.mkdir()

            skill_md = test_skill / "SKILL.md"
            skill_md.write_text("""# Test Skill

description: A test skill for V2 scanner
enabled: true
priority: 60
""", encoding='utf-8')

            # 创建带分类的 command
            commands_dir = project_root / "commands"
            category_dir = commands_dir / "testing"
            category_dir.mkdir(parents=True)

            cmd_md = category_dir / "test-command.md"
            cmd_md.write_text("""# test-command

description: A test command in testing category
command: echo "test"
enabled: true
""", encoding='utf-8')

            print("[1] 创建测试环境...")
            print(f"  - 项目根目录: {project_root}")
            print(f"  - Skills: {test_skill}")
            print(f"  - Commands: {cmd_md}")

            # 创建 ConfigLoader 并加载配置
            print(f"\n[2] 使用 ConfigLoader 加载配置...")
            loader = ConfigLoader(
                project_root=project_root,
                enable_auto_discovery=True
            )

            # 验证使用的是 V2 scanner
            print(f"  - Scanner 类型: {loader.scanner.__class__.__name__}")
            print(f"  - Scanner 模块: {loader.scanner.__class__.__module__}")

            assert loader.scanner is not None, "Scanner 应该已初始化"
            assert "resource_scanner_v2" in loader.scanner.__class__.__module__, \
                "应该使用 ResourceScannerV2"

            # 加载配置
            print(f"\n[3] 加载配置...")
            config = loader.load()

            # 验证资源已发现
            print(f"\n[4] 验证资源发现...")
            print(f"  - Skills 数量: {len(config.skills)}")
            print(f"  - Commands 数量: {len(config.commands)}")

            # 检查 skill
            if "test-skill" in config.skills:
                skill = config.skills["test-skill"]
                print(f"\n[5] Test Skill 详情:")
                print(f"  - 名称: {skill.name}")
                print(f"  - 路径: {skill.path}")
                print(f"  - 优先级: {skill.priority}")
                print(f"  - 来源: {skill.source}")
                assert skill.priority == 60, "优先级应该是60"

            # 检查 command (V2 支持分类)
            if "test-command" in config.commands:
                cmd = config.commands["test-command"]
                print(f"\n[6] Test Command 详情:")
                print(f"  - 名称: {cmd.name}")
                print(f"  - 来源: {cmd.source}")
                print(f"  - 配置数据: {cmd.config}")

            print(f"\n========== 测试完成 ==========\n")
            print("[PASS] ResourceScannerV2 集成测试通过")
            return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_backward_compatibility():
    """测试：V1 API 向后兼容性"""
    print("\n========== V1 向后兼容性测试 ==========\n")

    try:
        # 测试从 core 导入 V1 API
        print("[1] 测试导入 V1 API...")
        from core import (
            ResourceScannerV1,
            DiscoveredResourceV1
        )

        print(f"  - ResourceScannerV1: {ResourceScannerV1}")
        print(f"  - DiscoveredResourceV1: {DiscoveredResourceV1}")

        # 测试从 core 导入 V2 API（默认）
        print(f"\n[2] 测试导入 V2 API（默认）...")
        from core import (
            ResourceScanner,
            DiscoveredResource,
            ResourceLayout,
            ResourceCategory
        )

        print(f"  - ResourceScanner: {ResourceScanner}")
        print(f"  - DiscoveredResource: {DiscoveredResource}")
        print(f"  - ResourceLayout: {ResourceLayout}")
        print(f"  - ResourceCategory: {ResourceCategory}")

        # 验证默认是 V2
        print(f"\n[3] 验证默认使用 V2...")
        assert "resource_scanner_v2" in ResourceScanner.__module__, \
            "默认的 ResourceScanner 应该是 V2"
        assert "resource_scanner" in ResourceScannerV1.__module__ and \
               "v2" not in ResourceScannerV1.__module__, \
            "ResourceScannerV1 应该是 V1"

        print(f"  - 默认 ResourceScanner 来自: {ResourceScanner.__module__}")
        print(f"  - ResourceScannerV1 来自: {ResourceScannerV1.__module__}")

        print(f"\n========== 测试完成 ==========\n")
        print("[PASS] 向后兼容性测试通过")
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_v2_features():
    """测试：V2 新特性（分类支持）"""
    print("\n========== V2 新特性测试 ==========\n")

    try:
        from core import ResourceScanner, ResourceLayout, ResourceCategory

        print("[1] 测试 ResourceLayout 枚举...")
        layouts = [
            ResourceLayout.FLAT_FILE,
            ResourceLayout.CATEGORIZED_FILE,
            ResourceLayout.DIRECTORY_BASED
        ]
        for layout in layouts:
            print(f"  - {layout.name}: {layout.value}")

        print(f"\n[2] 测试 ResourceCategory...")
        category = ResourceCategory.from_directory_name("test-category")
        print(f"  - 名称: {category.name}")
        print(f"  - 显示名称: {category.display_name}")
        print(f"  - 优先级: {category.priority}")

        # 测试 kebab-case 转换
        category2 = ResourceCategory.from_directory_name("my-test-category")
        print(f"\n[3] Kebab-case 转换测试...")
        print(f"  - 输入: my-test-category")
        print(f"  - 显示名称: {category2.display_name}")
        assert category2.display_name == "My Test Category", \
            "应该正确转换 kebab-case"

        print(f"\n========== 测试完成 ==========\n")
        print("[PASS] V2 新特性测试通过")
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ResourceScannerV2 集成测试套件")
    print("=" * 60)

    tests = [
        ("V2 Scanner 集成", test_v2_scanner_integration),
        ("V1 向后兼容性", test_backward_compatibility),
        ("V2 新特性", test_v2_features)
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
