#!/usr/bin/env python3
"""
PromptManager V2 - 基于Memex-CLI的提示词管理器

新特性：
- 继承MemexExecutorBase统一架构
- 使用prompt-renderer skill通过Claude LLM执行
- 支持6种预定义模板类型
- 保留向后兼容的API
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re

import sys
from pathlib import Path

# 添加父目录到路径
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from executors.memex_executor_base import MemexExecutorBase
from core.backend_orchestrator import BackendOrchestrator


@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    category: str
    template: str
    variables: List[str]
    description: str


@dataclass
class PromptResult:
    """提示词渲染结果"""
    template_name: str
    rendered_prompt: str
    success: bool
    rendered_by: str  # "claude" or "local"
    variables: Dict[str, Any]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptManager(MemexExecutorBase):
    """
    提示词管理器 V2 - 基于Memex-CLI

    工作流程：
    1. 接收模板名称和变量
    2. 优先通过prompt-renderer skill调用Claude
    3. Fallback到本地字符串格式化
    4. 返回PromptResult

    支持的模板类型：
    - code-review: 代码审查
    - code-generation: 代码生成
    - documentation: 文档生成
    - bug-analysis: Bug分析
    - refactoring: 重构建议
    - test-generation: 测试用例生成
    """

    # 内置模板库（向后兼容）
    TEMPLATES = {
        "code-generation": PromptTemplate(
            name="code-generation",
            category="development",
            template="""你是一位资深软件工程师。请根据以下需求生成代码：

需求描述：
{requirement}

技术栈：{tech_stack}
编程语言：{language}

要求：
1. 代码结构清晰，易于维护
2. 遵循最佳实践和设计模式
3. 包含必要的错误处理
4. 添加适当的注释

请生成完整、可运行的代码。""",
            variables=["requirement", "tech_stack", "language"],
            description="根据需求生成代码"
        ),

        "code-review": PromptTemplate(
            name="code-review",
            category="quality",
            template="""你是一位代码审查专家。请审查以下代码：

```{language}
{code}
```

审查要点：
1. 代码质量和可读性
2. 潜在的bug和边界情况
3. 性能优化建议
4. 最佳实践遵循情况

请提供详细的审查意见和改进建议。""",
            variables=["code", "language"],
            description="审查代码质量和提供改进建议"
        ),

        "documentation": PromptTemplate(
            name="documentation",
            category="documentation",
            template="""你是一位技术文档专家。请为以下代码生成文档：

```{language}
{code}
```

文档类型：{doc_type}

要求：
1. 清晰的功能说明
2. 详细的参数说明
3. 返回值说明
4. 使用示例
5. 注意事项

请生成完整、专业的文档。""",
            variables=["code", "language", "doc_type"],
            description="生成代码文档"
        ),

        "bug-analysis": PromptTemplate(
            name="bug-analysis",
            category="debugging",
            template="""你是一位调试专家。请分析以下Bug：

错误信息：
{error_message}

相关代码：
```{language}
{code}
```

上下文信息：
{context}

要求：
1. 分析Bug的根本原因
2. 提供修复方案
3. 说明如何预防类似问题
4. 提供修复后的代码

请提供详细的分析和解决方案。""",
            variables=["error_message", "code", "language", "context"],
            description="分析Bug并提供解决方案"
        ),

        "refactoring": PromptTemplate(
            name="refactoring",
            category="improvement",
            template="""你是一位重构专家。请重构以下代码：

```{language}
{code}
```

重构目标：{refactoring_goal}
代码规模：{code_scale}

要求：
1. 保持功能不变
2. 提高代码质量
3. 遵循SOLID原则
4. 说明重构理由

请提供重构后的代码和详细说明。""",
            variables=["code", "language", "refactoring_goal", "code_scale"],
            description="重构代码提升质量"
        ),

        "test-generation": PromptTemplate(
            name="test-generation",
            category="testing",
            template="""你是一位测试工程师。请为以下代码生成测试用例：

```{language}
{code}
```

测试框架：{test_framework}
测试类型：{test_type}

要求：
1. 覆盖正常路径
2. 覆盖边界条件
3. 覆盖异常情况
4. 包含测试数据准备和清理

请生成完整的测试代码。""",
            variables=["code", "language", "test_framework", "test_type"],
            description="生成全面的测试用例"
        ),
    }

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        use_claude_renderer: bool = True,
        fallback_to_local: bool = True
    ):
        """
        初始化PromptManager

        Args:
            backend_orch: BackendOrchestrator实例
            use_claude_renderer: 是否使用Claude的prompt-renderer skill
            fallback_to_local: Claude失败时是否fallback到本地渲染
        """
        super().__init__(backend_orch, default_backend="claude", default_timeout=60)

        self.use_claude_renderer = use_claude_renderer
        self.fallback_to_local = fallback_to_local
        self.templates = self.TEMPLATES.copy()

    def render(self, template_name: str, **variables) -> PromptResult:
        """
        渲染提示词模板

        Args:
            template_name: 模板名称
            **variables: 模板变量

        Returns:
            PromptResult
        """
        # 优先使用Claude renderer
        if self.use_claude_renderer:
            try:
                return self._render_via_claude(template_name, variables)
            except Exception as e:
                if not self.fallback_to_local:
                    return PromptResult(
                        template_name=template_name,
                        rendered_prompt="",
                        success=False,
                        rendered_by="failed",
                        variables=variables,
                        error=f"渲染失败: {e}"
                    )
                # Fallback到本地渲染

        # 本地渲染
        return self._render_via_local(template_name, variables)

    def _render_via_claude(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> PromptResult:
        """
        通过prompt-renderer skill调用Claude

        Args:
            template_name: 模板名称
            variables: 模板变量

        Returns:
            PromptResult
        """
        # 构造提示词
        prompt = self._build_renderer_prompt(template_name, variables)

        # 调用memex-cli
        result = self.execute_via_memex(
            prompt=prompt,
            backend="claude",
            stream_format="jsonl",
            timeout=self.default_timeout
        )

        return PromptResult(
            template_name=template_name,
            rendered_prompt=result.output,
            success=True,
            rendered_by="claude",
            variables=variables,
            metadata={
                "run_id": result.run_id,
                "skill": "prompt-renderer"
            }
        )

    def _render_via_local(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> PromptResult:
        """
        本地渲染（字符串格式化）

        Args:
            template_name: 模板名称
            variables: 模板变量

        Returns:
            PromptResult
        """
        template = self.get_template(template_name)
        if not template:
            return PromptResult(
                template_name=template_name,
                rendered_prompt="",
                success=False,
                rendered_by="local",
                variables=variables,
                error=f"模板 '{template_name}' 不存在"
            )

        # 检查必需变量
        missing_vars = set(template.variables) - set(variables.keys())
        if missing_vars:
            # 使用默认值填充缺失变量
            for var in missing_vars:
                variables[var] = f"[{var}]"

        # 渲染模板
        try:
            rendered = template.template.format(**variables)
            return PromptResult(
                template_name=template_name,
                rendered_prompt=rendered,
                success=True,
                rendered_by="local",
                variables=variables
            )
        except Exception as e:
            return PromptResult(
                template_name=template_name,
                rendered_prompt="",
                success=False,
                rendered_by="local",
                variables=variables,
                error=f"渲染错误: {e}"
            )

    def _build_renderer_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        构造prompt-renderer skill的提示词

        Args:
            template_name: 模板名称
            variables: 模板变量

        Returns:
            提示词字符串
        """
        # 根据prompt-renderer.yaml的格式构造提示词
        var_lines = "\n".join([f"{k}: {v}" for k, v in variables.items()])

        prompt = f"""请使用prompt-renderer技能渲染模板：

模板类型：{template_name}

变量值：
{var_lines}

请执行模板渲染并返回结果。"""

        return prompt

    # 向后兼容的API方法

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)

    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """列出所有模板"""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())

    def add_template(self, template: PromptTemplate):
        """添加自定义模板"""
        self.templates[template.name] = template

    def search_templates(self, keyword: str) -> List[PromptTemplate]:
        """搜索模板"""
        results = []
        keyword_lower = keyword.lower()

        for template in self.templates.values():
            if (keyword_lower in template.name.lower() or
                keyword_lower in template.description.lower() or
                keyword_lower in template.category.lower()):
                results.append(template)

        return results

    def get_categories(self) -> List[str]:
        """获取所有模板类别"""
        return list(set(t.category for t in self.templates.values()))

    def execute(self, template_name: str, **kwargs) -> PromptResult:
        """
        执行模板渲染（实现MemexExecutorBase接口）

        Args:
            template_name: 模板名称
            **kwargs: 模板变量

        Returns:
            PromptResult
        """
        return self.render(template_name, **kwargs)


# 便捷函数
def create_prompt_manager(
    backend_orch: BackendOrchestrator,
    use_claude: bool = True
) -> PromptManager:
    """
    创建PromptManager的便捷函数

    Args:
        backend_orch: BackendOrchestrator实例
        use_claude: 是否使用Claude renderer

    Returns:
        PromptManager实例
    """
    return PromptManager(
        backend_orch=backend_orch,
        use_claude_renderer=use_claude,
        fallback_to_local=True
    )


# 使用示例
if __name__ == "__main__":
    # 模拟BackendOrchestrator
    class MockBackendOrch:
        def run_task(self, **kwargs):
            from dataclasses import dataclass
            @dataclass
            class MockResult:
                output: str
                success: bool
                run_id: str
                error: Optional[str] = None
            return MockResult(
                output="模拟渲染结果",
                success=True,
                run_id="test-123"
            )

    backend_orch = MockBackendOrch()
    manager = PromptManager(
        backend_orch=backend_orch,
        use_claude_renderer=False  # 示例中使用本地渲染
    )

    # 列出所有模板
    print("可用模板：")
    for template in manager.list_templates():
        print(f"  - {template.name}: {template.description}")

    print("\n" + "="*60)

    # 渲染代码审查模板
    result = manager.render(
        "code-review",
        code="def add(a, b): return a + b",
        language="python"
    )

    if result.success:
        print("渲染成功!")
        print(f"渲染方式: {result.rendered_by}")
        print(f"\n渲染结果：\n{result.rendered_prompt}")
    else:
        print(f"渲染失败: {result.error}")
