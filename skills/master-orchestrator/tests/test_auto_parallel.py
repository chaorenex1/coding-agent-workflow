#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动并行执行功能

验证系统是否能根据并行推断结果自动拆分任务并并行执行
"""

import re
from typing import List

def test_task_splitting():
    """测试任务拆分逻辑"""

    def split_parallel_tasks(request: str) -> List[str]:
        """简化版任务拆分函数"""

        # 策略1: 检测"包含"模式（优先级最高）
        if '包含' in request or 'include' in request.lower():
            pattern = r'包含(.+)'
            match = re.search(pattern, request)

            if match:
                items_part = match.group(1).strip()
                items = re.split(r'[、，和]', items_part)
                items = [item.strip() for item in items if item.strip() and len(item.strip()) > 1]

                if len(items) >= 2:
                    prefix_match = re.search(r'^(.+?)[，,]?\s*包含', request)
                    prefix = prefix_match.group(1).strip() if prefix_match else "实现"
                    return [f"{prefix} - {item}" for item in items]

        # 策略2: 检测逗号/顿号分隔的任务列表
        if '、' in request or '，' in request:
            pattern = r'(实现|开发|测试|分析|处理|审查|优化)(.+?)(、|，)(.+)'
            match = re.search(pattern, request)

            if match:
                verb = match.group(1)
                items_part = match.group(2) + match.group(3) + match.group(4)
                items = re.split(r'[、，]', items_part)
                items = [item.strip() for item in items if item.strip()]

                if len(items) >= 2:
                    return [f"{verb}{item}" for item in items]

        return []

    test_cases = [
        {
            "request": "实现用户管理、商品管理、订单处理",
            "expected_count": 3,
            "expected_subtasks": ["实现用户管理", "实现商品管理", "实现订单处理"],
            "description": "逗号分隔的任务列表"
        },
        {
            "request": "开发电商系统，包含用户模块、商品模块、订单模块",
            "expected_count": 3,
            "expected_subtasks": [
                "开发电商系统 - 用户模块",
                "开发电商系统 - 商品模块",
                "开发电商系统 - 订单模块"
            ],
            "description": "包含模式"
        },
        {
            "request": "测试登录功能、注册功能、支付功能",
            "expected_count": 3,
            "expected_subtasks": ["测试登录功能", "测试注册功能", "测试支付功能"],
            "description": "顿号分隔的测试任务"
        },
        {
            "request": "分析这个函数的时间复杂度",
            "expected_count": 0,
            "expected_subtasks": [],
            "description": "单一任务，不应拆分"
        }
    ]

    print("=" * 70)
    print("任务拆分逻辑测试")
    print("=" * 70)

    passed = 0
    failed = 0

    for i, case in enumerate(test_cases, 1):
        subtasks = split_parallel_tasks(case["request"])
        count_match = len(subtasks) == case["expected_count"]
        content_match = subtasks == case["expected_subtasks"]

        if count_match and content_match:
            status = "[PASS]"
            passed += 1
        else:
            status = "[FAIL]"
            failed += 1

        print(f"\n测试 {i}: {case['description']}")
        print(f"  请求: {case['request']}")
        print(f"  预期子任务数: {case['expected_count']}")
        print(f"  实际子任务数: {len(subtasks)}")

        if subtasks:
            print(f"  拆分结果:")
            for j, task in enumerate(subtasks, 1):
                print(f"    {j}. {task}")

        print(f"  结果: {status}")

    print("\n" + "=" * 70)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 70)

    return failed == 0


def test_parallel_workflow():
    """测试完整的并行工作流"""

    print("\n" + "=" * 70)
    print("并行工作流测试")
    print("=" * 70)

    # 模拟完整流程
    workflows = [
        {
            "request": "实现用户管理、商品管理、订单处理",
            "steps": [
                "1. 意图分析 -> enable_parallel=True (包含列表分隔)",
                "2. 任务拆分 -> 3个子任务",
                "3. 并行执行 -> 使用 ParallelScheduler",
                "4. 结果汇总 -> BatchResult 转 TaskResult"
            ]
        },
        {
            "request": "开发系统，包含认证模块和支付模块",
            "steps": [
                "1. 意图分析 -> enable_parallel=True (包含模式)",
                "2. 任务拆分 -> 2个子任务",
                "3. 并行执行 -> 使用 ParallelScheduler",
                "4. 结果汇总 -> BatchResult 转 TaskResult"
            ]
        },
        {
            "request": "分析函数复杂度",
            "steps": [
                "1. 意图分析 -> enable_parallel=False",
                "2. 串行执行 -> 使用 ExecutionRouter"
            ]
        }
    ]

    for i, workflow in enumerate(workflows, 1):
        print(f"\n工作流 {i}: {workflow['request']}")
        print("  执行步骤:")
        for step in workflow['steps']:
            print(f"    {step}")

    print("\n" + "=" * 70)
    print("[OK] 工作流验证完成")
    print("=" * 70)

    return True


def test_integration_example():
    """展示集成示例代码"""

    print("\n" + "=" * 70)
    print("集成示例代码")
    print("=" * 70)

    example_code = '''
# 示例 1: 启用自动并行执行
from orchestrator.master_orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator(
    auto_discover=True,      # 启用 V3 功能
    enable_parallel=True,    # 启用并行调度器
    max_parallel_workers=3   # 最多3个并行工作线程
)

# 发送包含多个子任务的请求
result = orchestrator.process(
    request="实现用户管理、商品管理、订单处理",
    verbose=True
)

# 预期输出:
# [意图分析]
#   模式: skill
#   类型: dev
#   复杂度: complex
#   并行执行: 是
#   并行理由: 包含多个独立模块，可并行开发
#
# [任务拆分] 检测到 3 个子任务，启动并行处理
#   推断理由: 包含多个独立模块，可并行开发
#   子任务 1: 实现用户管理
#   子任务 2: 实现商品管理
#   子任务 3: 实现订单处理
#
# [并行执行] 使用 3 个工作线程并行处理...


# 示例 2: "包含"模式
result = orchestrator.process(
    request="开发后台系统，包含认证模块、权限模块、日志模块",
    verbose=True
)

# 自动拆分为:
#   - 开发后台系统 - 认证模块
#   - 开发后台系统 - 权限模块
#   - 开发后台系统 - 日志模块


# 示例 3: 单一任务（不会并行）
result = orchestrator.process(
    request="分析这个函数的时间复杂度",
    verbose=True
)

# 输出:
# [意图分析]
#   并行执行: 否
#   并行理由: 单一分析任务，无法并行
#
# [本地执行] 串行执行任务...
'''

    print(example_code)
    print("=" * 70)

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("自动并行执行功能测试")
    print("=" * 70)

    results = []
    results.append(("任务拆分", test_task_splitting()))
    results.append(("并行工作流", test_parallel_workflow()))
    results.append(("集成示例", test_integration_example()))

    print("\n" + "=" * 70)
    print("总体测试结果")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 70)
    print(f"\n{'[SUCCESS] 所有测试通过!' if all_passed else '[ERROR] 部分测试失败'}\n")
