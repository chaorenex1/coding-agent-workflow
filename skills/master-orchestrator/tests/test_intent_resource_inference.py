#!/usr/bin/env python3
"""
Phase 1 单元测试：Intent 资源推断功能测试

测试 ClaudeIntentAnalyzer 的资源推断逻辑。
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Windows 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analyzers.claude_intent_analyzer import ClaudeIntentAnalyzer, Intent, ExecutionMode
from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType
from core.backend_orchestrator import TaskResult


# Mock Backend
class MockBackendOrchestrator:
    """简化的 Mock BackendOrchestrator"""

    def __init__(self, responses=None):
        self.responses = responses or {}

    def run_task(self, backend, prompt, stream_format="jsonl", **kwargs):
        """Mock run_task"""
        # 返回固定的意图分析 JSON
        output = self.responses.get("intent", '{"mode":"skill","task_type":"dev","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.85,"reasoning":"代码审查任务"}')

        return TaskResult(
            backend=backend,
            prompt=prompt,
            output=output,
            success=True,
            duration_seconds=0.1
        )


def test_intent_class_extension():
    """测试 1: Intent 类扩展 - entity 和 candidates 字段"""
    print("\n========== 测试 1: Intent 类扩展 ==========\n")

    # 创建 Intent 对象（不带资源推断）
    intent1 = Intent(
        mode=ExecutionMode.SKILL,
        task_type="dev",
        complexity="medium",
        confidence=0.85
    )

    # 验证新字段存在且默认值正确
    assert hasattr(intent1, 'entity'), "缺少 entity 字段"
    assert hasattr(intent1, 'candidates'), "缺少 candidates 字段"
    assert intent1.entity is None, "entity 默认值应为 None"
    assert intent1.candidates == [], "candidates 默认值应为空列表"

    print(f"  ✓ Intent 类新字段存在")
    print(f"    - entity: {intent1.entity}")
    print(f"    - candidates: {intent1.candidates}")

    # 创建 Intent 对象（带资源推断）
    intent2 = Intent(
        mode=ExecutionMode.SKILL,
        task_type="dev",
        complexity="medium",
        confidence=0.85,
        entity="skill:code-review",
        candidates=["skill:code-review", "skill:security-scanner"]
    )

    assert intent2.entity == "skill:code-review", "entity 赋值失败"
    assert intent2.candidates == ["skill:code-review", "skill:security-scanner"], "candidates 赋值失败"

    print(f"  ✓ Intent 类新字段可正常赋值")
    print(f"    - entity: {intent2.entity}")
    print(f"    - candidates: {intent2.candidates}")

    print("\n[PASS] Intent 类扩展测试通过\n")


def test_keyword_extraction():
    """测试 2: 关键词提取算法"""
    print("\n========== 测试 2: 关键词提取算法 ==========\n")

    mock_backend = MockBackendOrchestrator()
    analyzer = ClaudeIntentAnalyzer(backend_orch=mock_backend)

    # 测试中文关键词提取
    keywords1 = analyzer._extract_keywords("帮我审查代码质量和安全性")
    print(f"  输入: '帮我审查代码质量和安全性'")
    print(f"  关键词: {keywords1}")
    assert '审查' in keywords1, "未提取到 '审查'"
    assert '代码' in keywords1, "未提取到 '代码'"
    assert '质量' in keywords1, "未提取到 '质量'"
    assert '安全性' in keywords1, "未提取到 '安全性'"
    assert '帮我' not in keywords1, "停用词 '帮我' 未被过滤"
    print(f"  ✓ 中文关键词提取正确")

    # 测试英文关键词提取
    keywords2 = analyzer._extract_keywords("Please help me review code quality")
    print(f"\n  输入: 'Please help me review code quality'")
    print(f"  关键词: {keywords2}")
    assert 'review' in keywords2, "未提取到 'review'"
    assert 'code' in keywords2, "未提取到 'code'"
    assert 'quality' in keywords2, "未提取到 'quality'"
    assert 'please' not in keywords2, "停用词 'please' 未被过滤"
    assert 'help' not in keywords2, "停用词 'help' 未被过滤"
    print(f"  ✓ 英文关键词提取正确")

    # 测试标点符号处理
    keywords3 = analyzer._extract_keywords("分析项目依赖关系，生成报告。")
    print(f"\n  输入: '分析项目依赖关系，生成报告。'")
    print(f"  关键词: {keywords3}")
    assert '分析' in keywords3, "未提取到 '分析'"
    assert '项目' in keywords3, "未提取到 '项目'"
    assert '依赖' in keywords3, "未提取到 '依赖'"
    assert '关系' in keywords3, "未提取到 '关系'"
    assert '生成' in keywords3, "未提取到 '生成'"
    assert '报告' in keywords3, "未提取到 '报告'"
    print(f"  ✓ 标点符号处理正确")

    print("\n[PASS] 关键词提取算法测试通过\n")


def test_match_score_calculation():
    """测试 3: 匹配分数计算算法"""
    print("\n========== 测试 3: 匹配分数计算 ==========\n")

    mock_backend = MockBackendOrchestrator()
    analyzer = ClaudeIntentAnalyzer(backend_orch=mock_backend)

    # 创建测试资源
    resource1 = ResourceMetadata(
        name="code-review",
        namespace="skill:code-review",
        type=ResourceType.SKILL,
        source="builtin",
        priority=80,
        config={
            "description": "Code review and quality analysis",
            "tags": ["code", "review", "quality"]
        }
    )

    # 测试 1: 高匹配度（名称 + 描述 + 标签都匹配）
    keywords = ["code", "review", "quality"]
    score1 = analyzer._calculate_match_score(keywords, resource1, "dev")
    print(f"  关键词: {keywords}")
    print(f"  资源: {resource1.name}")
    print(f"  匹配分数: {score1:.2f}")
    assert score1 > 0.8, f"高匹配度应 > 0.8，实际: {score1:.2f}"
    print(f"  ✓ 高匹配度测试通过")

    # 测试 2: 中等匹配度（仅部分匹配）
    keywords2 = ["code", "security"]
    score2 = analyzer._calculate_match_score(keywords2, resource1, "dev")
    print(f"\n  关键词: {keywords2}")
    print(f"  资源: {resource1.name}")
    print(f"  匹配分数: {score2:.2f}")
    assert 0.3 < score2 < 0.8, f"中等匹配度应在 0.3-0.8，实际: {score2:.2f}"
    print(f"  ✓ 中等匹配度测试通过")

    # 测试 3: 低匹配度（几乎不匹配）
    keywords3 = ["database", "migration"]
    score3 = analyzer._calculate_match_score(keywords3, resource1, "dev")
    print(f"\n  关键词: {keywords3}")
    print(f"  资源: {resource1.name}")
    print(f"  匹配分数: {score3:.2f}")
    assert score3 < 0.3, f"低匹配度应 < 0.3，实际: {score3:.2f}"
    print(f"  ✓ 低匹配度测试通过")

    print("\n[PASS] 匹配分数计算测试通过\n")


def test_resource_type_mapping():
    """测试 4: 执行模式到资源类型的映射"""
    print("\n========== 测试 4: 资源类型映射 ==========\n")

    mock_backend = MockBackendOrchestrator()
    analyzer = ClaudeIntentAnalyzer(backend_orch=mock_backend)

    # 测试各种模式的映射
    mappings = [
        ("skill", [ResourceType.SKILL]),
        ("agent", [ResourceType.AGENT]),
        ("command", [ResourceType.COMMAND]),
        ("prompt", [ResourceType.PROMPT]),
        ("backend", [ResourceType.SKILL, ResourceType.PROMPT]),
    ]

    for mode, expected_types in mappings:
        result_types = analyzer._get_resource_types_by_mode(mode)
        print(f"  模式: {mode}")
        print(f"  映射资源类型: {[t.value for t in result_types]}")
        assert result_types == expected_types, f"模式 {mode} 映射错误"
        print(f"  ✓ 映射正确")

    print("\n[PASS] 资源类型映射测试通过\n")


def test_resource_inference_integration():
    """测试 5: 资源推断集成测试"""
    print("\n========== 测试 5: 资源推断集成测试 ==========\n")

    # 创建 Mock Backend
    mock_backend = MockBackendOrchestrator(responses={
        "intent": '{"mode":"skill","task_type":"dev","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.85,"reasoning":"代码审查任务"}'
    })

    # 创建 UnifiedRegistry 并注册资源
    registry = UnifiedRegistry()

    # 注册 code-review 资源
    code_review = ResourceMetadata(
        name="code-review",
        namespace="skill:code-review",
        type=ResourceType.SKILL,
        source="builtin",
        priority=80,
        enabled=True,
        config={
            "description": "代码审查和质量分析",
            "tags": ["代码", "审查", "质量"]
        }
    )
    registry.register(code_review)

    # 注册 security-scanner 资源
    security_scanner = ResourceMetadata(
        name="security-scanner",
        namespace="skill:security-scanner",
        type=ResourceType.SKILL,
        source="builtin",
        priority=70,
        enabled=True,
        config={
            "description": "安全漏洞扫描",
            "tags": ["安全", "扫描", "漏洞"]
        }
    )
    registry.register(security_scanner)

    print(f"  注册资源: code-review, security-scanner")

    # 创建分析器（传入 registry）
    analyzer = ClaudeIntentAnalyzer(
        backend_orch=mock_backend,
        registry=registry
    )

    # 执行意图分析（包含资源推断）
    intent = analyzer.analyze("帮我审查代码质量和安全性")

    print(f"\n  用户请求: '帮我审查代码质量和安全性'")
    print(f"  推断结果:")
    print(f"    - entity: {intent.entity}")
    print(f"    - candidates: {intent.candidates}")

    # 验证结果
    assert intent.entity is not None, "entity 应被推断"
    assert len(intent.candidates) > 0, "candidates 应包含至少一个资源"
    assert "skill:code-review" in intent.candidates, "应包含 code-review"

    print(f"  ✓ 资源推断成功")
    print(f"  ✓ 主实体: {intent.entity}")
    print(f"  ✓ 候选资源数量: {len(intent.candidates)}")

    print("\n[PASS] 资源推断集成测试通过\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("Phase 1: Intent 资源推断单元测试套件")
    print("=" * 70)

    tests = [
        test_intent_class_extension,
        test_keyword_extraction,
        test_match_score_calculation,
        test_resource_type_mapping,
        test_resource_inference_integration
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
