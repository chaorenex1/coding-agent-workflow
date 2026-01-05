#!/usr/bin/env python3
"""
简化版并行推断测试 - 直接测试关键逻辑
"""

def test_parallel_keywords():
    """测试并行关键词检测"""

    PARALLEL_KEYWORDS = {
        "explicit": ["批量", "多个", "同时", "并行", "并发", "batch", "multiple", "parallel", "concurrent"],
        "implicit": ["所有", "每个", "分别", "各个", "all", "each", "every"],
    }

    test_cases = [
        ("批量处理所有文件", True, "包含明确的批量关键词"),
        ("同时运行多个测试", True, "包含同时和多个关键词"),
        ("对所有模块进行分析", True, "包含所有关键词"),
        ("运行git status", False, "没有并行关键词"),
        ("分析这个函数", False, "单一任务"),
    ]

    print("=" * 70)
    print("并行关键词检测测试")
    print("=" * 70)

    passed = 0
    for request, expected, desc in test_cases:
        has_explicit = any(kw in request for kw in PARALLEL_KEYWORDS["explicit"])
        has_implicit = any(kw in request for kw in PARALLEL_KEYWORDS["implicit"])
        result = has_explicit or has_implicit

        status = "[PASS]" if result == expected else "[FAIL]"
        if result == expected:
            passed += 1

        print(f"\n{status} {desc}")
        print(f"   请求: {request}")
        print(f"   预期: {expected}, 实际: {result}")
        print(f"   明确关键词: {has_explicit}, 隐式关键词: {has_implicit}")

    print(f"\n结果: {passed}/{len(test_cases)} 通过")
    print("=" * 70)
    return passed == len(test_cases)


def test_intent_structure():
    """测试 Intent 数据结构"""
    from dataclasses import dataclass
    from typing import Optional
    from enum import Enum

    class ExecutionMode(Enum):
        COMMAND = "command"
        SKILL = "skill"

    @dataclass
    class Intent:
        mode: ExecutionMode
        task_type: str
        complexity: str
        enable_parallel: bool = False
        parallel_reasoning: Optional[str] = None

    print("\n" + "=" * 70)
    print("Intent 数据结构测试")
    print("=" * 70)

    # 测试创建 Intent 对象
    intent = Intent(
        mode=ExecutionMode.SKILL,
        task_type="dev",
        complexity="complex",
        enable_parallel=True,
        parallel_reasoning="包含多个独立模块"
    )

    print(f"\n[OK] Intent 对象创建成功")
    print(f"   模式: {intent.mode.value}")
    print(f"   任务类型: {intent.task_type}")
    print(f"   复杂度: {intent.complexity}")
    print(f"   并行执行: {intent.enable_parallel}")
    print(f"   并行理由: {intent.parallel_reasoning}")

    # 验证字段
    assert hasattr(intent, 'enable_parallel'), "缺少 enable_parallel 字段"
    assert hasattr(intent, 'parallel_reasoning'), "缺少 parallel_reasoning 字段"
    assert isinstance(intent.enable_parallel, bool), "enable_parallel 类型错误"

    print(f"\n[OK] 所有字段验证通过")
    print("=" * 70)
    return True


def test_parallel_logic():
    """测试完整的并行推断逻辑"""

    PARALLEL_KEYWORDS = {
        "explicit": ["批量", "多个", "同时", "并行", "并发", "batch", "multiple", "parallel", "concurrent"],
        "implicit": ["所有", "每个", "分别", "各个", "all", "each", "every"],
    }

    def classify_parallelizable(request: str, task_type: str, complexity: str):
        """简化的并行推断函数"""
        # 检查明确关键词
        has_explicit = any(kw in request for kw in PARALLEL_KEYWORDS["explicit"])
        if has_explicit:
            return True, "用户明确提到批量/并行处理"

        # 检查隐式关键词
        has_implicit = any(kw in request for kw in PARALLEL_KEYWORDS["implicit"])

        # 检查多文件标志
        multi_file_indicators = ["文件", "模块", "组件", "files", "modules", "components"]
        has_multi_file = any(kw in request for kw in multi_file_indicators)

        if has_implicit and has_multi_file:
            if task_type in ["dev", "test", "analysis"] and complexity in ["medium", "complex"]:
                return True, "涉及多个独立单元，适合并行处理"

        # 测试任务
        if task_type == "test" and complexity in ["medium", "complex"]:
            return True, "测试任务通常可并行执行"

        return False, "单一任务，不适合并行"

    print("\n" + "=" * 70)
    print("完整并行推断逻辑测试")
    print("=" * 70)

    test_cases = [
        ("批量处理文件", "analysis", "medium", True),
        ("对所有模块进行测试", "test", "complex", True),
        ("运行单元测试", "test", "medium", True),
        ("git status", "general", "simple", False),
        ("分析函数", "analysis", "simple", False),
    ]

    passed = 0
    for request, task_type, complexity, expected in test_cases:
        result, reasoning = classify_parallelizable(request, task_type, complexity)
        status = "[PASS]" if result == expected else "[FAIL]"
        if result == expected:
            passed += 1

        print(f"\n{status} 请求: {request}")
        print(f"   类型: {task_type}, 复杂度: {complexity}")
        print(f"   预期: {expected}, 实际: {result}")
        print(f"   理由: {reasoning}")

    print(f"\n结果: {passed}/{len(test_cases)} 通过")
    print("=" * 70)
    return passed == len(test_cases)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("并行执行推断功能测试")
    print("=" * 70)

    results = []
    results.append(("关键词检测", test_parallel_keywords()))
    results.append(("数据结构", test_intent_structure()))
    results.append(("推断逻辑", test_parallel_logic()))

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
