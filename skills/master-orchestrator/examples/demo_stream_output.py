#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Real-time Streaming Output

演示 master-orchestrator 的实时流式输出功能
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from master_orchestrator import MasterOrchestrator


def demo_basic_stream():
    """演示基本的流式输出"""
    print("=" * 60)
    print("Demo 1: Basic Streaming Output")
    print("=" * 60)
    print()

    orch = MasterOrchestrator()

    # 使用流式输出
    result = orch.process(
        "hello world",
        verbose=False,
        stream_output=True
    )

    print()
    print(f"Result: {result.success}")
    print(f"Duration: {result.duration_seconds}s")


def demo_with_custom_callback():
    """演示自定义回调函数"""
    print("\n" + "=" * 60)
    print("Demo 2: Custom Callback")
    print("=" * 60)
    print()

    from core.stream_handler import StreamHandler

    # 自定义回调：添加前缀
    def custom_callback(text):
        print(f"[Custom] {text}")

    handler = StreamHandler(callback=custom_callback)

    # 测试处理行
    handler.process_line('{"type":"assistant.output","output":"Test message"}')


def demo_without_icons():
    """演示不使用 emoji 图标"""
    print("\n" + "=" * 60)
    print("Demo 3: Without Icons (Plain Text)")
    print("=" * 60)
    print()

    from core.output_formatter import OutputFormatter

    # 禁用图标
    OutputFormatter.disable_icons()

    event = {
        "type": "assistant.output",
        "output": "This is plain text output"
    }

    formatted = OutputFormatter.format_event(event)
    print(formatted)

    # 恢复图标
    OutputFormatter.enable_icons()


if __name__ == "__main__":
    print("Master Orchestrator - Streaming Output Demo\n")

    try:
        demo_basic_stream()
        demo_with_custom_callback()
        demo_without_icons()

        print("\n" + "=" * 60)
        print("Demo completed!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
