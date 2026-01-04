#!/usr/bin/env python3
"""
ConfigLoader 单元测试

测试配置加载、合并和验证功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.core.config_loader import (
    ConfigLoader, OrchestratorConfig, SkillConfig, CommandConfig,
    AgentConfig, PromptConfig, ParallelConfig
)
from orchestrator.tests.sandbox import create_sandbox, TestHelper


def test_basic_config_loading():
    """测试基本配置加载"""
    print("测试 1: 基本配置加载")

    with create_sandbox("config-basic") as sandbox:
        # 创建配置文件
        config_data = TestHelper.create_sample_config()
        sandbox.create_config(config_data)

        # 创建 Skill 文件
        skill_data = TestHelper.create_sample_skill("test-skill-1")
        sandbox.create_skill("test-skill-1", skill_data)

        # 加载配置
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证基本属性
        assert config.version == "3.0", f"Expected version 3.0, got {config.version}"
        assert "default_backend" in config.global_settings
        assert config.global_settings["default_backend"] == "claude"

        print("  ✓ 基本配置加载成功")

    print("  ✓ 测试通过\n")


def test_skill_loading():
    """测试 Skill 加载"""
    print("测试 2: Skill 加载")

    with create_sandbox("config-skills") as sandbox:
        # 创建多个 Skills
        skills = {
            "skill-1": TestHelper.create_sample_skill("skill-1", priority=100),
            "skill-2": TestHelper.create_sample_skill("skill-2", priority=50),
            "skill-3": TestHelper.create_sample_skill("skill-3", priority=75),
        }
        sandbox.create_multiple_skills(skills)

        # 创建配置文件
        config_data = {
            "version": "3.0",
            "global": {"default_backend": "claude"},
            "skills": {"scan_paths": ["./skills/*.yaml"]}
        }
        sandbox.create_config(config_data)

        # 加载配置
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证 Skills 加载
        assert len(config.skills) >= 3, f"Expected at least 3 skills, got {len(config.skills)}"
        assert "skill-1" in config.skills
        assert config.skills["skill-1"].priority == 100

        print(f"  ✓ 加载了 {len(config.skills)} 个 Skills")
        print("  ✓ 测试通过\n")


def test_config_priority():
    """测试配置优先级覆盖"""
    print("测试 3: 配置优先级覆盖")

    with create_sandbox("config-priority") as sandbox:
        # 创建低优先级 Skill
        low_priority_skill = TestHelper.create_sample_skill("test-skill", priority=10)
        sandbox.create_skill("test-skill", low_priority_skill)

        # 在配置文件中声明高优先级
        config_data = {
            "version": "3.0",
            "skills": {
                "manual": [
                    {
                        "name": "test-skill",
                        "path": "./skills/test-skill.yaml",
                        "priority": 100,  # 更高优先级
                        "enabled": True
                    }
                ]
            }
        }
        sandbox.create_config(config_data)

        # 加载配置
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证优先级
        assert "test-skill" in config.skills
        # 手动声明的优先级应该更高
        assert config.skills["test-skill"].priority >= 100

        print("  ✓ 优先级覆盖正常")
        print("  ✓ 测试通过\n")


def test_command_config():
    """测试 Command 配置"""
    print("测试 4: Command 配置")

    with create_sandbox("config-commands") as sandbox:
        config_data = {
            "version": "3.0",
            "commands": {
                "whitelist": ["git", "npm", "python", "docker"],
                "aliases": [
                    {"name": "gst", "command": "git status"},
                    {"name": "glog", "command": "git log --oneline -10"}
                ]
            }
        }
        sandbox.create_config(config_data)

        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证 Commands
        assert "git" in config.commands
        assert "gst" in config.commands
        assert config.commands["gst"].command == "git status"

        print(f"  ✓ 加载了 {len(config.commands)} 个 Commands")
        print("  ✓ 测试通过\n")


def test_prompt_config():
    """测试 Prompt 配置"""
    print("测试 5: Prompt 配置")

    with create_sandbox("config-prompts") as sandbox:
        config_data = {
            "version": "3.0",
            "prompts": [
                {
                    "name": "api-doc",
                    "template": "Generate API doc for {language}:\n\n{code}",
                    "variables": ["language", "code"],
                    "priority": 60
                },
                {
                    "name": "code-review",
                    "template": "Review this code:\n\n{code}",
                    "variables": ["code"],
                    "priority": 50
                }
            ]
        }
        sandbox.create_config(config_data)

        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证 Prompts
        assert "api-doc" in config.prompts
        assert "code-review" in config.prompts
        assert config.prompts["api-doc"].priority == 60
        assert "language" in config.prompts["api-doc"].variables

        print(f"  ✓ 加载了 {len(config.prompts)} 个 Prompts")
        print("  ✓ 测试通过\n")


def test_parallel_config():
    """测试并行配置"""
    print("测试 6: 并行配置")

    with create_sandbox("config-parallel") as sandbox:
        config_data = {
            "version": "3.0",
            "parallel": {
                "enabled": True,
                "max_workers": 5,
                "timeout_per_task": 300,
                "allowed_modes": ["command", "backend", "agent"],
                "sequential_modes": ["skill"]
            }
        }
        sandbox.create_config(config_data)

        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证并行配置
        assert config.parallel_config.enabled == True
        assert config.parallel_config.max_workers == 5
        assert config.parallel_config.timeout_per_task == 300
        assert "agent" in config.parallel_config.allowed_modes

        print("  ✓ 并行配置加载正常")
        print("  ✓ 测试通过\n")


def test_config_validation():
    """测试配置验证"""
    print("测试 7: 配置验证")

    with create_sandbox("config-validation") as sandbox:
        # 创建有问题的配置
        config_data = {
            "version": "3.0",
            "skills": {
                "manual": [
                    {
                        "name": "nonexistent-skill",
                        "path": "./skills/nonexistent.yaml",  # 文件不存在
                        "priority": 100
                    }
                ]
            },
            "parallel": {
                "enabled": True,
                "max_workers": 0,  # 无效值
                "timeout_per_task": -1  # 无效值
            }
        }
        sandbox.create_config(config_data)

        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 验证应该发现错误
        errors = loader._validate_config(config)
        assert len(errors) > 0, "Expected validation errors"

        print(f"  ✓ 发现 {len(errors)} 个验证错误:")
        for error in errors[:3]:  # 只显示前3个
            print(f"    - {error}")
        print("  ✓ 测试通过\n")


def test_config_merge():
    """测试配置合并"""
    print("测试 8: 配置合并")

    with create_sandbox("config-merge") as sandbox:
        # 创建两个 Skills：内置和项目级
        builtin_skill = TestHelper.create_sample_skill("common-skill", priority=10)
        project_skill = TestHelper.create_sample_skill("common-skill", priority=100)

        sandbox.create_skill("common-skill", builtin_skill)

        # 项目配置覆盖
        config_data = {
            "version": "3.0",
            "skills": {
                "manual": [
                    {
                        "name": "common-skill",
                        "path": "./skills/common-skill.yaml",
                        "priority": 100,  # 项目级优先级更高
                        "enabled": True
                    }
                ]
            }
        }
        sandbox.create_config(config_data)

        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 项目级应该覆盖内置
        assert "common-skill" in config.skills
        assert config.skills["common-skill"].priority >= 100

        print("  ✓ 配置合并正常（高优先级覆盖低优先级）")
        print("  ✓ 测试通过\n")


def test_missing_config():
    """测试缺失配置的处理"""
    print("测试 9: 缺失配置的处理")

    with create_sandbox("config-missing") as sandbox:
        # 不创建配置文件
        loader = ConfigLoader(project_root=sandbox.project_root)
        config = loader.load()

        # 应该返回默认配置
        assert config is not None
        assert config.version == "3.0"
        assert len(config.global_settings) > 0

        print("  ✓ 缺失配置使用默认值")
        print("  ✓ 测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("ConfigLoader 单元测试")
    print("=" * 70)
    print()

    tests = [
        test_basic_config_loading,
        test_skill_loading,
        test_config_priority,
        test_command_config,
        test_prompt_config,
        test_parallel_config,
        test_config_validation,
        test_config_merge,
        test_missing_config,
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
