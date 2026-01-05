#!/usr/bin/env python3
"""
MarkdownSkillExecutor 集成测试
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.executor_factory import MarkdownSkillExecutor
from core.backend_orchestrator import BackendOrchestrator, TaskResult


def test_markdown_skill_basic():
    """测试：基础 Markdown Skill 执行"""
    print("\n========== 测试：基础 Markdown Skill 执行 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 创建测试 SKILL.md
        skill_dir = Path(tmp_dir) / "code-review"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""# code-review

description: 代码审查助手
enabled: true
priority: 80
backend: claude

## System Prompt

你是一位资深的代码审查专家。

## User Prompt Template

请审查以下代码：

{{request}}
""", encoding='utf-8')

        # 创建 Mock BackendOrchestrator
        mock_backend = Mock(spec=BackendOrchestrator)
        mock_result = TaskResult(
            backend="claude",
            prompt="test",
            output="代码审查结果",
            success=True,
            duration_seconds=1.0
        )
        mock_backend.run_task = Mock(return_value=mock_result)

        # 创建执行器
        executor = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_dir,
            skill_name="code-review"
        )

        # 执行
        result = executor.execute("def foo(): pass")

        # 验证
        assert mock_backend.run_task.called, "Backend run_task 未被调用"
        call_args = mock_backend.run_task.call_args

        # 提取传递给 backend 的 prompt
        prompt = call_args.kwargs.get('prompt', '')

        print(f"[调用信息]")
        print(f"  - Backend run_task 调用次数: {mock_backend.run_task.call_count}")
        print(f"  - 提示词长度: {len(prompt)}")
        print(f"\n[提示词内容]")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)

        # 验证提示词包含 System Prompt 和用户需求
        assert '资深的代码审查专家' in prompt, "System Prompt 未包含"
        assert 'def foo(): pass' in prompt, "用户需求未包含"

        print("\n[PASS] 基础执行测试通过")


def test_request_format_processing():
    """测试：请求格式处理"""
    print("\n========== 测试：请求格式处理 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_dir = Path(tmp_dir) / "test-skill"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""# test-skill

description: 测试技能

## User Prompt Template

需求：{{request}}
""", encoding='utf-8')

        mock_backend = Mock(spec=BackendOrchestrator)
        mock_result = TaskResult(backend="claude", prompt="test", output="OK", success=True, duration_seconds=1.0)
        mock_backend.run_task = Mock(return_value=mock_result)

        executor = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_dir,
            skill_name="test-skill"
        )

        # 测试 1: 非格式化输入
        executor.execute("帮我优化代码")
        prompt1 = mock_backend.run_task.call_args.kwargs.get('prompt', '')
        assert '帮我优化代码' in prompt1, "非格式化输入处理错误"
        print("  - 非格式化输入: PASS")

        # 测试 2: "需求理解：" 前缀
        executor.execute("需求理解：分析性能瓶颈")
        prompt2 = mock_backend.run_task.call_args.kwargs.get('prompt', '')
        assert '分析性能瓶颈' in prompt2, "格式化输入（需求理解）处理错误"
        assert '需求理解：' not in prompt2, "前缀未移除"
        print("  - 格式化输入（需求理解）: PASS")

        # 测试 3: Slash Command 格式
        executor.execute("/code_fix 修复bug")
        prompt3 = mock_backend.run_task.call_args.kwargs.get('prompt', '')
        assert '修复bug' in prompt3, "Slash Command 格式处理错误"
        assert '/code_fix' not in prompt3, "命令未移除"
        print("  - Slash Command 格式: PASS")

        print("\n[PASS] 请求格式处理测试通过")


def test_template_variable_replacement():
    """测试：模板变量替换"""
    print("\n========== 测试：模板变量替换 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_dir = Path(tmp_dir) / "template-skill"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""# template-skill

description: 模板变量测试

## User Prompt Template

请求：{{request}}
语言：{{language}}
级别：{{level}}
""", encoding='utf-8')

        mock_backend = Mock(spec=BackendOrchestrator)
        mock_result = TaskResult(backend="claude", prompt="test", output="OK", success=True, duration_seconds=1.0)
        mock_backend.run_task = Mock(return_value=mock_result)

        executor = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_dir,
            skill_name="template-skill"
        )

        # 执行时传入额外参数
        executor.execute("生成代码", language="Python", level="高级")

        prompt = mock_backend.run_task.call_args.kwargs.get('prompt', '')

        print(f"[替换后的提示词]")
        print(prompt)

        # 验证变量替换
        assert '生成代码' in prompt, "request 变量未替换"
        assert 'Python' in prompt, "language 变量未替换"
        assert '高级' in prompt, "level 变量未替换"
        assert '{{' not in prompt, "存在未替换的变量"

        print("\n[PASS] 模板变量替换测试通过")


def test_backend_selection():
    """测试：后端选择"""
    print("\n========== 测试：后端选择 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_dir = Path(tmp_dir) / "backend-skill"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""# backend-skill

description: 后端选择测试
backend: gemini

## User Prompt Template

{{request}}
""", encoding='utf-8')

        mock_backend = Mock(spec=BackendOrchestrator)
        mock_result = TaskResult(backend="gemini", prompt="test", output="OK", success=True, duration_seconds=1.0)
        mock_backend.run_task = Mock(return_value=mock_result)

        executor = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_dir,
            skill_name="backend-skill"
        )

        # 测试 1: 使用元数据中的 backend
        executor.execute("测试")
        call_kwargs1 = mock_backend.run_task.call_args.kwargs
        backend1 = call_kwargs1.get('backend', 'default')
        print(f"  - 元数据 backend: {backend1}")
        assert backend1 == 'gemini', "Backend 选择错误"

        # 测试 2: 执行时覆盖 backend
        executor.execute("测试", backend="claude")
        call_kwargs2 = mock_backend.run_task.call_args.kwargs
        backend2 = call_kwargs2.get('backend', 'default')
        print(f"  - 覆盖 backend: {backend2}")
        assert backend2 == 'claude', "Backend 覆盖失败"

        print("\n[PASS] 后端选择测试通过")


def test_path_handling():
    """测试：路径处理（目录 vs 文件）"""
    print("\n========== 测试：路径处理 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 创建 skill 目录
        skill_dir = Path(tmp_dir) / "path-skill"
        skill_dir.mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""# path-skill

description: 路径测试

## User Prompt Template

{{request}}
""", encoding='utf-8')

        mock_backend = Mock(spec=BackendOrchestrator)
        mock_backend.call_backend = Mock(return_value="OK")

        # 测试 1: 传入目录路径
        executor1 = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_dir,  # 目录
            skill_name="path-skill"
        )
        assert executor1.skill_file == skill_file, "目录路径处理错误"
        print(f"  - 目录路径: {skill_dir} -> {executor1.skill_file}")

        # 测试 2: 传入文件路径
        executor2 = MarkdownSkillExecutor(
            backend_orch=mock_backend,
            skill_path=skill_file,  # 文件
            skill_name="path-skill"
        )
        assert executor2.skill_file == skill_file, "文件路径处理错误"
        print(f"  - 文件路径: {skill_file}")

        print("\n[PASS] 路径处理测试通过")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("MarkdownSkillExecutor 集成测试套件")
    print("=" * 60)

    tests = [
        test_markdown_skill_basic,
        test_request_format_processing,
        test_template_variable_replacement,
        test_backend_selection,
        test_path_handling
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
