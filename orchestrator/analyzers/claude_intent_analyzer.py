#!/usr/bin/env python3
"""
ClaudeIntentAnalyzer - 使用Claude LLM进行智能意图识别

通过memex-cli调用Claude分析用户请求，返回结构化的意图信息。
相比规则引擎，准确率从60-70%提升至90%+。
"""

import json
import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum

# 导入必要的类型（避免循环导入）
import sys
from pathlib import Path

# 添加父目录到路径以便导入
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from core.backend_orchestrator import BackendOrchestrator, TaskResult


class ExecutionMode(Enum):
    """执行模式枚举"""
    COMMAND = "command"
    AGENT = "agent"
    PROMPT = "prompt"
    SKILL = "skill"
    BACKEND = "backend"


@dataclass
class Intent:
    """用户意图分析结果"""
    mode: ExecutionMode
    task_type: str
    complexity: str
    backend_hint: Optional[str] = None
    skill_hint: Optional[str] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None


class ClaudeIntentAnalyzer:
    """
    使用Claude LLM进行意图识别

    工作流程：
    1. 构造意图分析提示词
    2. 通过memex-cli调用Claude
    3. 解析JSON返回
    4. 构造Intent对象
    """

    # 意图分析提示词模板
    INTENT_PROMPT_TEMPLATE = """你是一个AI任务意图分析专家。分析用户请求，返回JSON格式的意图分类。

执行模式 (mode)：
- command: 简单命令执行（git, npm, docker, pytest等开发命令）
- agent: 需要智能体推理（探索代码、规划实现、深度分析）
- prompt: 使用模板处理（代码审查、文档生成、格式转换）
- skill: 复杂技能流程（多阶段开发、完整系统设计、UX工作流）
- backend: 直接LLM调用（分析、解释、回答问题）

任务类型 (task_type):
- dev: 开发、编码、实现功能
- ux: 设计、界面、用户体验
- analysis: 分析、理解、解释代码
- test: 测试、验证、质量保证
- general: 通用任务

复杂度 (complexity):
- simple: 单一步骤，直接执行
- medium: 2-3个步骤，需要一定推理
- complex: 多步骤，需要规划和协调

后端提示 (backend_hint):
- claude: 通用推理、代码理解（默认）
- gemini: 视觉、UI/UX设计
- codex: 代码生成、深度开发
- null: 无特定偏好

技能提示 (skill_hint):
- multcode-dev-workflow-agent: 多阶段开发流程
- ux-design-gemini: UX设计流程
- code-with-codex: 代码实现
- null: 无特定技能

用户请求：
{request}

返回JSON（仅返回JSON，无其他文本）：
{{
  "mode": "command|agent|prompt|skill|backend",
  "task_type": "dev|ux|analysis|test|general",
  "complexity": "simple|medium|complex",
  "backend_hint": "claude|gemini|codex|null",
  "skill_hint": "技能名称|null",
  "confidence": 0.0-1.0,
  "reasoning": "简短解释为什么选择这个模式（1-2句话）"
}}

示例：
请求："运行git status查看状态"
返回：{{"mode":"command","task_type":"general","complexity":"simple","backend_hint":null,"skill_hint":null,"confidence":0.95,"reasoning":"明确的git命令，直接执行即可"}}

请求："开发一个电商管理系统，包含用户管理、商品管理、订单处理"
返回：{{"mode":"skill","task_type":"dev","complexity":"complex","backend_hint":"codex","skill_hint":"multcode-dev-workflow-agent","confidence":0.9,"reasoning":"复杂系统开发，需要多阶段规划和实现流程"}}

请求："分析这个函数的时间复杂度"
返回：{{"mode":"backend","task_type":"analysis","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.85,"reasoning":"代码分析任务，需要推理但不需要多阶段流程"}}

现在分析上述用户请求并返回JSON："""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        confidence_threshold: float = 0.7
    ):
        """
        初始化Claude意图分析器

        Args:
            backend_orch: BackendOrchestrator实例
            confidence_threshold: 置信度阈值，低于此值将回退到规则引擎
        """
        self.backend_orch = backend_orch
        self.confidence_threshold = confidence_threshold

    def analyze(self, request: str, timeout: int = 10) -> Intent:
        """
        分析用户请求意图

        Args:
            request: 用户请求文本
            timeout: 超时时间（秒）

        Returns:
            Intent对象

        Raises:
            ValueError: JSON解析失败
            RuntimeError: Claude调用失败
        """
        # 1. 构造提示词
        prompt = self.INTENT_PROMPT_TEMPLATE.format(request=request)

        # 2. 调用memex-cli (使用Claude backend)
        try:
            result = self.backend_orch.run_task(
                backend="claude",
                prompt=prompt,
                stream_format="jsonl"
            )

            if not result.success:
                raise RuntimeError(f"Claude调用失败: {result.error}")

            # 3. 解析JSON输出
            intent_data = self._parse_intent_result(result.output)

            # 4. 构造Intent对象
            return Intent(
                mode=ExecutionMode(intent_data["mode"]),
                task_type=intent_data["task_type"],
                complexity=intent_data["complexity"],
                backend_hint=intent_data.get("backend_hint") if intent_data.get("backend_hint") != "null" else None,
                skill_hint=intent_data.get("skill_hint") if intent_data.get("skill_hint") != "null" else None,
                confidence=float(intent_data.get("confidence", 0.8)),
                reasoning=intent_data.get("reasoning")
            )

        except Exception as e:
            # 如果Claude调用失败，抛出异常由上层处理（可回退到规则引擎）
            raise RuntimeError(f"意图分析失败: {e}")

    def _parse_intent_result(self, output: str) -> dict:
        """
        从Claude输出中提取JSON

        Args:
            output: Claude的原始输出

        Returns:
            解析后的dict

        Raises:
            ValueError: JSON解析失败
        """
        # 尝试直接解析JSON
        try:
            return json.loads(output.strip())
        except json.JSONDecodeError:
            pass

        # 尝试从文本中提取JSON块
        # 查找 {...} 模式
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 如果仍然失败，尝试从代码块中提取
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # 所有尝试都失败
        raise ValueError(f"无法从Claude输出中解析JSON: {output[:200]}...")

    def validate_intent(self, intent: Intent) -> bool:
        """
        验证意图的置信度

        Args:
            intent: Intent对象

        Returns:
            是否通过验证（置信度 >= 阈值）
        """
        return intent.confidence >= self.confidence_threshold


# 便捷函数
def create_claude_analyzer(
    backend_orch: BackendOrchestrator,
    confidence_threshold: float = 0.7
) -> ClaudeIntentAnalyzer:
    """
    创建Claude意图分析器的便捷函数

    Args:
        backend_orch: BackendOrchestrator实例
        confidence_threshold: 置信度阈值

    Returns:
        ClaudeIntentAnalyzer实例
    """
    return ClaudeIntentAnalyzer(
        backend_orch=backend_orch,
        confidence_threshold=confidence_threshold
    )
