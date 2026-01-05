#!/usr/bin/env python3
"""
快速验证脚本 - 测试三项修复

1. master_orchestrator.py logger导入
2. core/__init__.py 公共API导出
3. PromptCommandHandler 实现
"""

import sys
import io

# Windows编码处理
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_logger_import():
    """测试logger导入"""
    print("\n=== 测试1: logger导入 ===")
    try:
        from orchestrator import master_orchestrator

        # 检查logger是否存在
        assert hasattr(master_orchestrator, 'logger'), "logger未定义"
        print("✓ master_orchestrator.logger 已正确定义")

        # 检查logger类型
        import logging
        assert isinstance(master_orchestrator.logger, logging.Logger), "logger类型错误"
        print("✓ logger类型正确: logging.Logger")

        print("✓ 测试1通过!")
        return True
    except Exception as e:
        print(f"✗ 测试1失败: {e}")
        return False


def test_core_init_exports():
    """测试core/__init__.py导出"""
    print("\n=== 测试2: core模块导出 ===")
    try:
        from orchestrator.core import (
            BackendOrchestrator,
            TaskResult,
            EventStream,
            ConfigLoader,
            UnifiedRegistry,
            ExecutorFactory,
            ParallelScheduler,
            DependencyAnalyzer,
            SlashCommandRegistry,
            PromptCommandHandler  # 新增的导出
        )

        print("✓ 所有主要类成功导入:")
        print("  - BackendOrchestrator")
        print("  - ConfigLoader")
        print("  - UnifiedRegistry")
        print("  - ExecutorFactory")
        print("  - ParallelScheduler")
        print("  - DependencyAnalyzer")
        print("  - SlashCommandRegistry")
        print("  - PromptCommandHandler (新增)")

        print("✓ 测试2通过!")
        return True
    except Exception as e:
        print(f"✗ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_command_handler():
    """测试PromptCommandHandler实现"""
    print("\n=== 测试3: PromptCommandHandler ===")
    try:
        from orchestrator.core.slash_command import (
            PromptCommandHandler,
            SlashCommandType,
            HANDLER_MAP
        )

        # 检查类存在
        print("✓ PromptCommandHandler类成功导入")

        # 检查是否注册到HANDLER_MAP
        assert SlashCommandType.PROMPT in HANDLER_MAP, "PROMPT类型未注册到HANDLER_MAP"
        print("✓ PROMPT类型已注册到HANDLER_MAP")

        # 检查handler类型
        handler_class = HANDLER_MAP[SlashCommandType.PROMPT]
        assert handler_class == PromptCommandHandler, "HANDLER_MAP中的类型不匹配"
        print("✓ HANDLER_MAP映射正确")

        # 检查类方法
        assert hasattr(PromptCommandHandler, 'execute'), "缺少execute方法"
        assert hasattr(PromptCommandHandler, '_parse_variables'), "缺少_parse_variables方法"
        print("✓ PromptCommandHandler方法完整")

        # 创建实例测试
        handler = PromptCommandHandler(orchestrator=None)
        print("✓ PromptCommandHandler实例化成功")

        # 测试_parse_variables方法
        variables = handler._parse_variables(
            args=["key1=value1", "key2=value2"],
            kwargs={"key3": "value3"}
        )
        assert variables == {"key1": "value1", "key2": "value2", "key3": "value3"}
        print("✓ _parse_variables方法工作正常")

        print("✓ 测试3通过!")
        return True
    except Exception as e:
        print(f"✗ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("架构修复验证测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(test_logger_import())
    results.append(test_core_init_exports())
    results.append(test_prompt_command_handler())

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"通过: {passed}/{total}")

    if all(results):
        print("\n✓ 所有测试通过! 架构修复成功!")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
