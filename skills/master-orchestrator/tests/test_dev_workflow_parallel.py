#!/usr/bin/env python3
"""
DevWorkflowAgent 并行执行测试示例
"""

import sys
from pathlib import Path

# 添加 orchestrator 到路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.skills.dev_workflow import DevWorkflowAgent, V3_PARALLEL_AVAILABLE


def test_serial_mode():
    """测试串行模式"""
    print("=" * 60)
    print("测试 1: 串行执行模式")
    print("=" * 60)

    agent = DevWorkflowAgent(
        parse_events=True,
        timeout=300,
        enable_parallel=False
    )

    requirement = "创建一个简单的待办事项管理应用"

    print(f"\n需求: {requirement}")
    print(f"模式: 串行\n")

    result = agent.run(requirement, verbose=True)

    print(f"\n结果:")
    print(f"  成功: {result.success}")
    print(f"  完成阶段: {result.completed_stages}/5")
    print(f"  总耗时: {result.total_duration_seconds:.2f}s")


def test_parallel_mode():
    """测试并行模式"""
    if not V3_PARALLEL_AVAILABLE:
        print("\n[跳过] V3 并行组件不可用")
        return

    print("\n" + "=" * 60)
    print("测试 2: 并行执行模式")
    print("=" * 60)

    agent = DevWorkflowAgent(
        parse_events=True,
        timeout=300,
        enable_parallel=True,
        max_workers=2
    )

    requirement = "设计一个在线课程学习平台"

    print(f"\n需求: {requirement}")
    print(f"模式: 并行 (max_workers=2)\n")

    result = agent.run(requirement, verbose=True)

    print(f"\n结果:")
    print(f"  成功: {result.success}")
    print(f"  完成阶段: {result.completed_stages}/5")
    print(f"  总耗时: {result.total_duration_seconds:.2f}s")

    # 显示并行执行的优势
    print(f"\n并行执行层级:")
    print(f"  Level 0: [requirements]")
    print(f"  Level 1: [feature_design, ux_design] ← 并行执行")
    print(f"  Level 2: [dev_plan]")
    print(f"  Level 3: [implementation]")


def compare_modes():
    """对比串行和并行模式"""
    print("\n" + "=" * 60)
    print("性能对比")
    print("=" * 60)

    if not V3_PARALLEL_AVAILABLE:
        print("\n[跳过] V3 并行组件不可用")
        return

    requirement = "开发一个智能推荐系统"

    # 串行模式
    print("\n1. 串行模式测试...")
    serial_agent = DevWorkflowAgent(enable_parallel=False)
    serial_result = serial_agent.run(requirement, verbose=False)

    # 并行模式
    print("2. 并行模式测试...")
    parallel_agent = DevWorkflowAgent(enable_parallel=True, max_workers=2)
    parallel_result = parallel_agent.run(requirement, verbose=False)

    # 对比
    print(f"\n对比结果:")
    print(f"  串行模式耗时: {serial_result.total_duration_seconds:.2f}s")
    print(f"  并行模式耗时: {parallel_result.total_duration_seconds:.2f}s")

    if serial_result.total_duration_seconds > 0:
        speedup = serial_result.total_duration_seconds / parallel_result.total_duration_seconds
        print(f"  加速比: {speedup:.2f}x")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DevWorkflowAgent 并行测试")
    parser.add_argument("--mode", choices=["serial", "parallel", "compare", "all"],
                       default="all", help="测试模式")

    args = parser.parse_args()

    try:
        if args.mode == "serial" or args.mode == "all":
            test_serial_mode()

        if args.mode == "parallel" or args.mode == "all":
            test_parallel_mode()

        if args.mode == "compare":
            compare_modes()

        print("\n测试完成!")

    except KeyboardInterrupt:
        print("\n\n测试中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
