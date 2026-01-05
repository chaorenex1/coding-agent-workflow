#!/usr/bin/env python3
"""
/master-orchestrator Slash Command 集成测试

测试 master-orchestrator 元技能的执行流程。
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Windows 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import (
    SlashCommandResult,
    BackendOrchestrator,
    MarkdownSkillExecutor,
    TaskResult
)


# Mock Backend (simplified version)
class MockBackendOrchestrator:
    """简化的 Mock BackendOrchestrator"""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = 0
        self.call_history = []

    def run_task(self, backend, prompt, stream_format="jsonl", **kwargs):
        """Mock run_task"""
        self.call_count += 1
        self.call_history.append({
            "backend": backend,
            "prompt": prompt,
            "stream_format": stream_format,
            "kwargs": kwargs
        })

        # 查找响应
        output = self._find_response(prompt)

        return TaskResult(
            backend=backend,
            prompt=prompt,
            output=output,
            success=True,
            duration_seconds=0.1
        )

    def _find_response(self, prompt):
        """查找匹配的响应"""
        for pattern, response in self.responses.items():
            if pattern.lower() in prompt.lower():
                return response
        return f"Mock response for: {prompt[:50]}..."


def test_master_orchestrator_skill_creation():
    """测试 1: master-orchestrator SKILL.md 文件创建"""
    print("\n========== 测试 1: master-orchestrator SKILL.md 文件创建 ==========\n")

    # 检查 SKILL.md 文件是否存在
    skill_file = project_root / "skills" / "master-orchestrator" / "SKILL.md"

    assert skill_file.exists(), f"SKILL.md 文件不存在: {skill_file}"
    print(f"  ✓ SKILL.md 文件存在: {skill_file}")

    # 读取并验证内容
    content = skill_file.read_text(encoding='utf-8')

    # 验证基本元数据
    assert '# master-orchestrator' in content, "缺少标题"
    assert 'description:' in content, "缺少 description"
    assert 'enabled: true' in content, "缺少 enabled"
    assert 'priority: 100' in content, "缺少 priority"
    assert 'backend: claude' in content, "缺少 backend"

    # 验证章节
    assert '## System Prompt' in content, "缺少 System Prompt 章节"
    assert '## User Prompt Template' in content, "缺少 User Prompt Template 章节"

    print("  ✓ 元数据验证通过")
    print("  ✓ 章节结构验证通过")
    print("\n[PASS] SKILL.md 文件创建测试通过\n")


def test_markdown_skill_executor_parsing():
    """测试 2: MarkdownSkillExecutor 解析 SKILL.md"""
    print("\n========== 测试 2: MarkdownSkillExecutor 解析 SKILL.md ==========\n")

    skill_dir = project_root / "skills" / "master-orchestrator"

    # 创建 Mock BackendOrchestrator
    mock_backend = MockBackendOrchestrator(responses={
        "master orchestrator": "需求分析：这是一个代码审查任务\n\n推荐资源：skill:code-review"
    })

    # 创建执行器
    executor = MarkdownSkillExecutor(
        backend_orch=mock_backend,
        skill_path=skill_dir,
        skill_name="master-orchestrator"
    )

    # 验证解析结果
    assert executor.parsed_content is not None, "parsed_content 为 None"
    print(f"  ✓ 资源内容解析成功")

    # 验证元数据
    metadata = executor.parsed_content.metadata
    assert metadata.get('name') == 'master-orchestrator', "name 不正确"
    assert metadata.get('enabled') == True, "enabled 不正确"
    assert metadata.get('priority') == 100, "priority 不正确"
    assert metadata.get('backend') == 'claude', "backend 不正确"

    print(f"  ✓ 元数据解析正确")
    print(f"    - name: {metadata.get('name')}")
    print(f"    - priority: {metadata.get('priority')}")
    print(f"    - backend: {metadata.get('backend')}")

    # 验证章节
    assert executor.parsed_content.has_section('System Prompt'), "缺少 System Prompt"
    assert executor.parsed_content.has_section('User Prompt Template'), "缺少 User Prompt Template"

    print(f"  ✓ 章节解析正确")
    print(f"    - System Prompt: {len(executor.parsed_content.get_section('System Prompt'))} 字符")
    print(f"    - User Prompt Template: {len(executor.parsed_content.get_section('User Prompt Template'))} 字符")

    print("\n[PASS] MarkdownSkillExecutor 解析测试通过\n")


def test_master_orchestrator_skill_execution():
    """测试 3: master-orchestrator 技能执行"""
    print("\n========== 测试 3: master-orchestrator 技能执行 ==========\n")

    skill_dir = project_root / "skills" / "master-orchestrator"

    # 创建 Mock BackendOrchestrator
    mock_backend = MockBackendOrchestrator(responses={
        "代码审查": "## 需求分析\n这是一个代码审查任务\n\n## 推荐资源\n1. skill:code-review (匹配度: 95%)"
    })

    # 创建执行器
    executor = MarkdownSkillExecutor(
        backend_orch=mock_backend,
        skill_path=skill_dir,
        skill_name="master-orchestrator"
    )

    # 执行任务
    result = executor.execute("帮我审查代码质量")

    # 验证结果
    assert result is not None, "执行结果为 None"
    assert mock_backend.call_count > 0, "Backend 未被调用"

    print(f"  ✓ 技能执行成功")
    print(f"  ✓ Backend 调用次数: {mock_backend.call_count}")

    # 验证提示词包装
    call_history = mock_backend.call_history[0]
    prompt = call_history['prompt']

    # 验证 System Prompt 被包含
    assert 'Master Orchestrator' in prompt or '主编排器' in prompt, "System Prompt 未包含在提示词中"

    # 验证用户需求被包含
    assert '帮我审查代码质量' in prompt, "用户需求未包含在提示词中"

    print(f"  ✓ 提示词包装正确")
    print(f"    - 提示词长度: {len(prompt)} 字符")
    print(f"    - 包含 System Prompt: ✓")
    print(f"    - 包含用户需求: ✓")

    print("\n[PASS] 技能执行测试通过\n")


def test_slash_command_registration():
    """测试 4: /master-orchestrator 命令注册"""
    print("\n========== 测试 4: /master-orchestrator 命令注册 ==========\n")

    from core.slash_command_registry import SlashCommandRegistry, register_builtin_commands
    from core.slash_command import SlashCommandType

    # 创建注册表
    registry = SlashCommandRegistry()

    # 注册内置命令
    register_builtin_commands(registry)

    # 验证 /master-orchestrator 命令存在
    command = registry.get("master-orchestrator")

    assert command is not None, "/master-orchestrator 命令未注册"
    print(f"  ✓ /master-orchestrator 命令已注册")

    # 验证命令属性
    assert command.type == SlashCommandType.SKILL, "命令类型不正确"
    assert command.skill == "master-orchestrator", "skill 字段不正确"
    assert command.enabled == True, "命令未启用"
    assert command.priority == 100, "优先级不正确"

    print(f"  ✓ 命令属性验证通过")
    print(f"    - 类型: {command.type.value}")
    print(f"    - Skill: {command.skill}")
    print(f"    - 优先级: {command.priority}")
    print(f"    - 描述: {command.description[:50]}...")

    # 验证示例
    assert len(command.examples) > 0, "缺少使用示例"
    print(f"  ✓ 使用示例:")
    for example in command.examples:
        print(f"    - {example}")

    print("\n[PASS] 命令注册测试通过\n")


def test_format_processing():
    """测试 5: 输入格式处理"""
    print("\n========== 测试 5: 输入格式处理 ==========\n")

    skill_dir = project_root / "skills" / "master-orchestrator"

    mock_backend = MockBackendOrchestrator(responses={
        "优化代码": "优化建议...",
        "分析项目": "项目分析...",
        "修复bug": "Bug修复..."
    })

    executor = MarkdownSkillExecutor(
        backend_orch=mock_backend,
        skill_path=skill_dir,
        skill_name="master-orchestrator"
    )

    # 测试 1: 非格式化输入
    executor.execute("帮我优化代码性能")
    prompt1 = mock_backend.call_history[-1]['prompt']
    assert '帮我优化代码性能' in prompt1, "非格式化输入处理错误"
    print("  ✓ 非格式化输入: PASS")

    # 测试 2: "需求理解：" 前缀
    executor.execute("需求理解：分析项目依赖关系")
    prompt2 = mock_backend.call_history[-1]['prompt']
    assert '分析项目依赖关系' in prompt2, "格式化输入处理错误"
    assert '需求理解：' not in prompt2, "前缀未移除"
    print("  ✓ 格式化输入（需求理解）: PASS")

    # 测试 3: Slash Command 格式
    executor.execute("/code_fix 修复认证bug")
    prompt3 = mock_backend.call_history[-1]['prompt']
    assert '修复认证bug' in prompt3, "Slash Command 格式处理错误"
    assert '/code_fix' not in prompt3, "命令未移除"
    print("  ✓ Slash Command 格式: PASS")

    print(f"\n[PASS] 输入格式处理测试通过\n")


def test_end_to_end_execution():
    """测试 6: 端到端执行流程（Skill Handler 完整流程）"""
    print("\n========== 测试 6: 端到端执行流程 ==========\n")

    from core.slash_command import SkillCommandHandler, SlashCommandMetadata, SlashCommandType
    from core.executor_factory import ExecutorFactory
    from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType
    from unittest.mock import Mock

    # 1. 创建 Mock Orchestrator
    mock_orch = Mock()
    mock_backend = MockBackendOrchestrator(responses={
        "分析": "## 需求分析\n这是一个代码审查任务\n\n## 推荐资源\nskill:code-review"
    })

    # 2. 创建 UnifiedRegistry 并注册 master-orchestrator 资源
    registry = UnifiedRegistry()

    skill_metadata = ResourceMetadata(
        name="master-orchestrator",
        namespace="skill:master-orchestrator",  # Format: "type:name"
        type=ResourceType.SKILL,
        path=project_root / "skills" / "master-orchestrator",
        source="builtin",
        priority=100,
        enabled=True,
        config={"type": "markdown", "backend": "claude"}
    )

    registry.register(skill_metadata)
    print(f"  ✓ 注册 master-orchestrator 资源到 UnifiedRegistry")

    # 3. 创建 ExecutorFactory
    factory = ExecutorFactory(backend_orch=mock_backend, registry=registry)
    print(f"  ✓ 创建 ExecutorFactory")

    # 4. 设置 Mock Orchestrator
    mock_orch.factory = factory
    mock_orch.backend_orch = mock_backend

    # 5. 创建 SkillCommandHandler
    handler = SkillCommandHandler(orchestrator=mock_orch)
    print(f"  ✓ 创建 SkillCommandHandler")

    # 6. 创建 /master-orchestrator 命令元数据
    command = SlashCommandMetadata(
        name="master-orchestrator",
        type=SlashCommandType.SKILL,
        description="Test command",
        skill="master-orchestrator",
        enabled=True,
        priority=100,
        source="test"
    )

    # 7. 执行命令
    args = ["帮我分析代码质量"]
    result = handler.execute(command, args, {})

    print(f"\n  [命令执行结果]")
    print(f"  - 命令: {result.command}")
    print(f"  - 成功: {result.success}")
    print(f"  - 执行时间: {result.duration_seconds:.3f}s")

    # 验证执行成功
    assert result.success, f"命令执行失败: {result.error}"
    assert result.command == "/master-orchestrator", "命令名称不正确"
    assert mock_backend.call_count > 0, "Backend 未被调用"

    print(f"  ✓ 命令执行成功")
    print(f"  ✓ Backend 调用次数: {mock_backend.call_count}")

    # 验证提示词包装
    call_history = mock_backend.call_history[0]
    prompt = call_history['prompt']

    # 验证包含关键内容
    assert 'Master Orchestrator' in prompt or '主编排器' in prompt, "System Prompt 未包含"
    assert '帮我分析代码质量' in prompt, "用户需求未包含"

    print(f"  ✓ 提示词包装正确")
    print(f"    - 提示词长度: {len(prompt)} 字符")

    print(f"\n[PASS] 端到端执行测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("/master-orchestrator Slash Command 集成测试套件")
    print("=" * 70)

    tests = [
        test_master_orchestrator_skill_creation,
        test_markdown_skill_executor_parsing,
        test_master_orchestrator_skill_execution,
        test_slash_command_registration,
        test_format_processing,
        test_end_to_end_execution
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__}: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__}: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
