#!/usr/bin/env python3
"""
AgentCaller V2 - 基于Memex-CLI的智能体调用器

新特性：
- 继承MemexExecutorBase统一架构
- 使用agent-router skill通过Claude LLM执行
- 支持explore/plan/general三种Agent类型
- 保留向后兼容的API
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

# 添加父目录到路径
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from executors.memex_executor_base import MemexExecutorBase
from core.backend_orchestrator import BackendOrchestrator


class AgentType(Enum):
    """智能体类型"""
    GENERAL_PURPOSE = "general"
    EXPLORE = "explore"
    PLAN = "plan"


@dataclass
class AgentRequest:
    """智能体请求"""
    agent_type: AgentType
    prompt: str
    thoroughness: Optional[str] = None  # for explore: quick/medium/very_thorough
    model: Optional[str] = None


@dataclass
class AgentResult:
    """智能体执行结果"""
    agent_type: str
    prompt: str
    output: str
    success: bool
    agent_id: Optional[str] = None
    error: Optional[str] = None
    parsed_result: Optional[Dict[str, Any]] = None  # 解析后的结构化结果


class AgentCaller(MemexExecutorBase):
    """
    智能体调用器 V2 - 基于Memex-CLI

    工作流程：
    1. 接收AgentRequest
    2. 通过agent-router skill调用Claude
    3. 解析Agent输出
    4. 返回AgentResult

    支持的Agent类型：
    - explore: 代码库探索（查找文件、分析架构）
    - plan: 实现规划（设计方案、分解任务）
    - general: 通用任务（问答、建议）
    """

    # Agent提示词模板
    AGENT_PROMPT_TEMPLATE = """执行Agent任务：

任务类型：{agent_type}
任务描述：{prompt}
{extra_params}

请作为{agent_type} Agent执行此任务，并返回结构化结果。"""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        use_claude_router: bool = True,
        fallback_to_simple: bool = True
    ):
        """
        初始化AgentCaller

        Args:
            backend_orch: BackendOrchestrator实例
            use_claude_router: 是否使用Claude的agent-router skill
            fallback_to_simple: Claude失败时是否fallback到简单实现
        """
        super().__init__(backend_orch, default_backend="claude", default_timeout=120)

        self.use_claude_router = use_claude_router
        self.fallback_to_simple = fallback_to_simple

    def call_agent(self, request: AgentRequest) -> AgentResult:
        """
        调用Agent执行任务

        Args:
            request: AgentRequest对象

        Returns:
            AgentResult
        """
        # 优先使用Claude agent-router
        if self.use_claude_router:
            try:
                return self._call_via_claude_router(request)
            except Exception as e:
                if not self.fallback_to_simple:
                    return AgentResult(
                        agent_type=request.agent_type.value,
                        prompt=request.prompt,
                        output="",
                        success=False,
                        error=f"Agent调用失败: {e}"
                    )
                # Fallback到简单实现

        # 简单实现（直接调用后端）
        return self._call_simple(request)

    def _call_via_claude_router(self, request: AgentRequest) -> AgentResult:
        """
        通过agent-router skill调用Claude

        Args:
            request: AgentRequest对象

        Returns:
            AgentResult
        """
        # 构造提示词
        extra_params = ""
        if request.agent_type == AgentType.EXPLORE and request.thoroughness:
            extra_params = f"探索深度：{request.thoroughness}"

        prompt = self.AGENT_PROMPT_TEMPLATE.format(
            agent_type=request.agent_type.value,
            prompt=request.prompt,
            extra_params=extra_params
        )

        # 调用memex-cli
        result = self.execute_via_memex(
            prompt=prompt,
            backend="claude",
            stream_format="jsonl",
            timeout=self.default_timeout
        )

        # 解析结果
        parsed = self._parse_agent_output(result.output, request.agent_type)

        return AgentResult(
            agent_type=request.agent_type.value,
            prompt=request.prompt,
            output=result.output,
            success=True,
            agent_id=result.run_id,
            parsed_result=parsed
        )

    def _call_simple(self, request: AgentRequest) -> AgentResult:
        """
        简单实现（直接调用后端，不使用skill）

        Args:
            request: AgentRequest对象

        Returns:
            AgentResult
        """
        # 根据Agent类型构造提示词
        if request.agent_type == AgentType.EXPLORE:
            prompt = f"""你是代码库探索专家。请帮助完成以下探索任务：

{request.prompt}

请提供：
1. 相关文件位置
2. 关键代码片段
3. 架构分析
4. 总结建议

{f'探索深度：{request.thoroughness}' if request.thoroughness else ''}"""

        elif request.agent_type == AgentType.PLAN:
            prompt = f"""你是软件架构师。请为以下需求设计实现方案：

{request.prompt}

请提供：
1. 实现步骤
2. 关键文件和模块
3. 技术难点和风险
4. 最佳实践建议"""

        else:  # GENERAL
            prompt = request.prompt

        # 直接调用后端（不使用memex-cli）
        # 注意：Agent调用通常不需要流式输出，显式禁用以避免阻塞
        try:
            result = self.backend_orch.run_task(
                backend="claude",
                prompt=prompt,
                stream_format="jsonl",
                stream_output=False  # 禁用流式输出
            )

            return AgentResult(
                agent_type=request.agent_type.value,
                prompt=request.prompt,
                output=result.output,
                success=result.success,
                agent_id=result.run_id,
                error=None if result.success else result.error
            )
        except Exception as e:
            return AgentResult(
                agent_type=request.agent_type.value,
                prompt=request.prompt,
                output="",
                success=False,
                error=f"后端调用失败: {e}"
            )

    def _parse_agent_output(
        self,
        output: str,
        agent_type: AgentType
    ) -> Optional[Dict[str, Any]]:
        """
        解析Agent输出为结构化数据

        Args:
            output: Agent原始输出
            agent_type: Agent类型

        Returns:
            解析后的字典或None
        """
        try:
            parsed = {}

            # 尝试提取EXPLORE_RESULT
            if agent_type == AgentType.EXPLORE:
                explore_match = re.search(
                    r'\[EXPLORE_RESULT\](.*?)(?:\[|$)',
                    output,
                    re.DOTALL
                )
                if explore_match:
                    content = explore_match.group(1).strip()
                    parsed['type'] = 'explore'
                    parsed['content'] = content

                    # 提取文件位置（简单实现）
                    files = re.findall(r'(\S+\.py):(\d+)', content)
                    if files:
                        parsed['files'] = [
                            {'path': f, 'line': int(l)} for f, l in files
                        ]

            # 尝试提取PLAN_RESULT
            elif agent_type == AgentType.PLAN:
                plan_match = re.search(
                    r'\[PLAN_RESULT\](.*?)(?:\[|$)',
                    output,
                    re.DOTALL
                )
                if plan_match:
                    content = plan_match.group(1).strip()
                    parsed['type'] = 'plan'
                    parsed['content'] = content

                    # 提取步骤（简单实现）
                    steps = re.findall(r'步骤\s*(\d+)[：:](.*?)(?=步骤|\Z)', content, re.DOTALL)
                    if steps:
                        parsed['steps'] = [
                            {'number': int(n), 'description': desc.strip()}
                            for n, desc in steps
                        ]

            # GENERAL_RESULT
            else:
                general_match = re.search(
                    r'\[GENERAL_RESULT\](.*?)(?:\[|$)',
                    output,
                    re.DOTALL
                )
                if general_match:
                    content = general_match.group(1).strip()
                    parsed['type'] = 'general'
                    parsed['content'] = content

            return parsed if parsed else None

        except Exception:
            return None

    def suggest_agent_type(self, task_description: str) -> AgentType:
        """
        根据任务描述建议Agent类型

        Args:
            task_description: 任务描述

        Returns:
            推荐的AgentType
        """
        task_lower = task_description.lower()

        # Explore关键词
        if any(kw in task_lower for kw in [
            "查找", "搜索", "探索", "在哪", "位置",
            "find", "search", "explore", "where", "locate"
        ]):
            return AgentType.EXPLORE

        # Plan关键词
        if any(kw in task_lower for kw in [
            "规划", "设计", "计划", "方案", "架构",
            "plan", "design", "architect", "how to implement"
        ]):
            return AgentType.PLAN

        # 默认general
        return AgentType.GENERAL_PURPOSE

    def execute(self, request: str, **kwargs) -> AgentResult:
        """
        执行Agent任务（实现MemexExecutorBase接口）

        Args:
            request: 任务描述
            **kwargs: 可选参数（agent_type, thoroughness等）

        Returns:
            AgentResult
        """
        # 确定Agent类型
        if 'agent_type' in kwargs:
            agent_type = kwargs['agent_type']
            if isinstance(agent_type, str):
                agent_type = AgentType(agent_type)
        else:
            agent_type = self.suggest_agent_type(request)

        # 构造AgentRequest
        agent_request = AgentRequest(
            agent_type=agent_type,
            prompt=request,
            thoroughness=kwargs.get('thoroughness'),
            model=kwargs.get('model')
        )

        return self.call_agent(agent_request)


# 便捷函数
def create_agent_caller(
    backend_orch: BackendOrchestrator,
    use_claude: bool = True
) -> AgentCaller:
    """
    创建AgentCaller的便捷函数

    Args:
        backend_orch: BackendOrchestrator实例
        use_claude: 是否使用Claude router

    Returns:
        AgentCaller实例
    """
    return AgentCaller(
        backend_orch=backend_orch,
        use_claude_router=use_claude,
        fallback_to_simple=True
    )
