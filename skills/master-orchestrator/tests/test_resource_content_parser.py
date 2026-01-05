#!/usr/bin/env python3
"""
ResourceContentParser 单元测试
"""

import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.resource_content_parser import (
    MarkdownResourceParser,
    ParsedResourceContent,
    get_parser
)


def test_markdown_parser_basic():
    """测试：基础 Markdown 解析"""
    print("\n========== 测试：基础 Markdown 解析 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 创建测试 SKILL.md
        skill_file = Path(tmp_dir) / "test-skill.md"
        skill_file.write_text("""# test-skill

description: 测试技能
enabled: true
priority: 80
backend: claude
tags: [test, demo]

## System Prompt

你是一个测试助手。

## User Prompt Template

请处理以下需求：
{{request}}
""", encoding='utf-8')

        # 解析
        parser = MarkdownResourceParser()
        parsed = parser.parse(skill_file)

        # 验证元数据
        print("[元数据]")
        assert parsed.get_metadata('name') == 'test-skill', "name 不正确"
        assert parsed.get_metadata('description') == '测试技能', "description 不正确"
        assert parsed.get_metadata('enabled') == True, "enabled 不正确"
        assert parsed.get_metadata('priority') == 80, "priority 不正确"
        assert parsed.get_metadata('backend') == 'claude', "backend 不正确"
        assert parsed.get_metadata('tags') == ['test', 'demo'], "tags 不正确"
        print(f"  - name: {parsed.get_metadata('name')}")
        print(f"  - description: {parsed.get_metadata('description')}")
        print(f"  - priority: {parsed.get_metadata('priority')}")
        print(f"  - tags: {parsed.get_metadata('tags')}")

        # 验证章节
        print("\n[章节]")
        assert parsed.has_section('System Prompt'), "缺少 System Prompt 章节"
        assert parsed.has_section('User Prompt Template'), "缺少 User Prompt Template 章节"

        system_prompt = parsed.get_section('System Prompt')
        user_prompt = parsed.get_section('User Prompt Template')

        assert '测试助手' in system_prompt, "System Prompt 内容不正确"
        assert '{{request}}' in user_prompt, "User Prompt Template 内容不正确"

        print(f"  - System Prompt: {system_prompt[:50]}...")
        print(f"  - User Prompt Template: {user_prompt[:50]}...")

        print("\n[PASS] 基础 Markdown 解析测试通过")


def test_markdown_parser_yaml_frontmatter():
    """测试：YAML Front Matter 解析"""
    print("\n========== 测试：YAML Front Matter ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_file = Path(tmp_dir) / "test-frontmatter.md"
        skill_file.write_text("""---
name: frontmatter-skill
description: 使用 YAML Front Matter
enabled: false
priority: 90
---

# Skill with Front Matter

## System Prompt

Front matter 系统提示词。
""", encoding='utf-8')

        parser = MarkdownResourceParser()
        parsed = parser.parse(skill_file)

        # 验证 Front Matter 优先
        assert parsed.get_metadata('name') == 'frontmatter-skill', "Front Matter name 不正确"
        assert parsed.get_metadata('description') == '使用 YAML Front Matter', "Front Matter description 不正确"
        assert parsed.get_metadata('enabled') == False, "Front Matter enabled 不正确"
        assert parsed.get_metadata('priority') == 90, "Front Matter priority 不正确"

        print(f"  - YAML Front Matter 解析成功")
        print(f"  - name: {parsed.get_metadata('name')}")
        print(f"  - priority: {parsed.get_metadata('priority')}")

        print("\n[PASS] YAML Front Matter 测试通过")


def test_markdown_parser_value_types():
    """测试：值类型解析（bool, int, list）"""
    print("\n========== 测试：值类型解析 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_file = Path(tmp_dir) / "test-types.md"
        skill_file.write_text("""# type-test

bool_true: true
bool_false: false
int_value: 123
list_value: [item1, item2, item3]
string_value: hello world

## Content

Test content
""", encoding='utf-8')

        parser = MarkdownResourceParser()
        parsed = parser.parse(skill_file)

        # 验证类型
        assert parsed.get_metadata('bool_true') is True, "bool true 解析错误"
        assert parsed.get_metadata('bool_false') is False, "bool false 解析错误"
        assert parsed.get_metadata('int_value') == 123, "int 解析错误"
        assert isinstance(parsed.get_metadata('int_value'), int), "int 类型错误"
        assert parsed.get_metadata('list_value') == ['item1', 'item2', 'item3'], "list 解析错误"
        assert parsed.get_metadata('string_value') == 'hello world', "string 解析错误"

        print(f"  - bool: {parsed.get_metadata('bool_true')} (type: {type(parsed.get_metadata('bool_true')).__name__})")
        print(f"  - int: {parsed.get_metadata('int_value')} (type: {type(parsed.get_metadata('int_value')).__name__})")
        print(f"  - list: {parsed.get_metadata('list_value')}")

        print("\n[PASS] 值类型解析测试通过")


def test_markdown_parser_multiple_sections():
    """测试：多章节解析"""
    print("\n========== 测试：多章节解析 ==========\n")

    with tempfile.TemporaryDirectory() as tmp_dir:
        skill_file = Path(tmp_dir) / "test-sections.md"
        skill_file.write_text("""# multi-section

description: 多章节测试

## Section 1

第一章节内容

## Section 2

第二章节内容

## Section 3

第三章节内容
""", encoding='utf-8')

        parser = MarkdownResourceParser()
        parsed = parser.parse(skill_file)

        # 验证章节数量
        sections = parsed.list_sections()
        assert len(sections) == 3, f"章节数量错误: {len(sections)}"

        # 验证章节名称
        assert 'Section 1' in sections, "缺少 Section 1"
        assert 'Section 2' in sections, "缺少 Section 2"
        assert 'Section 3' in sections, "缺少 Section 3"

        # 验证章节内容
        assert '第一章节' in parsed.get_section('Section 1'), "Section 1 内容错误"
        assert '第二章节' in parsed.get_section('Section 2'), "Section 2 内容错误"
        assert '第三章节' in parsed.get_section('Section 3'), "Section 3 内容错误"

        print(f"  - 章节数量: {len(sections)}")
        print(f"  - 章节列表: {sections}")

        print("\n[PASS] 多章节解析测试通过")


def test_get_parser_factory():
    """测试：解析器工厂"""
    print("\n========== 测试：解析器工厂 ==========\n")

    # 测试 Markdown 文件
    md_file = Path("test.md")
    parser = get_parser(md_file)
    assert isinstance(parser, MarkdownResourceParser), "Markdown 解析器类型错误"
    print(f"  - test.md -> {parser.__class__.__name__}")

    # 测试不支持的格式
    try:
        txt_file = Path("test.txt")
        parser = get_parser(txt_file)
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"  - test.txt -> ValueError (正确)")

    print("\n[PASS] 解析器工厂测试通过")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ResourceContentParser 单元测试套件")
    print("=" * 60)

    tests = [
        test_markdown_parser_basic,
        test_markdown_parser_yaml_frontmatter,
        test_markdown_parser_value_types,
        test_markdown_parser_multiple_sections,
        test_get_parser_factory
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {test_func.__name__}: {e}")
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
