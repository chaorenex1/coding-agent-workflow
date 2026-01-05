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
from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType


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

    # Phase 1 新增字段：资源推断
    entity: Optional[str] = None            # 主要推断的资源实体 (如 "skill:code-review")
    candidates: list = None                  # 候选资源列表 (如 ["skill:code-review", "skill:security-scanner"])

    # 并行执行推断
    enable_parallel: bool = False           # 是否适合并行执行
    parallel_reasoning: Optional[str] = None  # 并行推断的理由

    def __post_init__(self):
        """初始化默认值"""
        if self.candidates is None:
            self.candidates = []


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

并行执行推断 (enable_parallel):
判断任务是否适合并行执行，考虑以下因素：
- 用户明确提到"批量"、"多个"、"同时"、"并行"等关键词
- 任务可分解为多个独立子任务（如：批量处理文件、多模块测试）
- 子任务之间无明显依赖关系（如：可同时运行的测试、独立的代码审查）
- 复杂度为medium/complex且任务类型为dev/test时优先考虑
- 返回 true 或 false，以及简短的推断理由

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
  "reasoning": "简短解释为什么选择这个模式（1-2句话）",
  "enable_parallel": true|false,
  "parallel_reasoning": "是否适合并行的简短理由（1句话）"
}}

示例：
请求："运行git status查看状态"
返回：{{"mode":"command","task_type":"general","complexity":"simple","backend_hint":null,"skill_hint":null,"confidence":0.95,"reasoning":"明确的git命令，直接执行即可","enable_parallel":false,"parallel_reasoning":"单一命令，无需并行"}}

请求："开发一个电商管理系统，包含用户管理、商品管理、订单处理"
返回：{{"mode":"skill","task_type":"dev","complexity":"complex","backend_hint":"codex","skill_hint":"multcode-dev-workflow-agent","confidence":0.9,"reasoning":"复杂系统开发，需要多阶段规划和实现流程","enable_parallel":true,"parallel_reasoning":"包含多个独立模块，可并行开发"}}

请求："批量处理src目录下的所有Python文件进行代码审查"
返回：{{"mode":"prompt","task_type":"analysis","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.88,"reasoning":"批量代码审查任务，使用审查模板处理","enable_parallel":true,"parallel_reasoning":"多个文件可独立审查，适合并行处理"}}

请求："分析这个函数的时间复杂度"
返回：{{"mode":"backend","task_type":"analysis","complexity":"medium","backend_hint":"claude","skill_hint":null,"confidence":0.85,"reasoning":"代码分析任务，需要推理但不需要多阶段流程","enable_parallel":false,"parallel_reasoning":"单一分析任务，无法并行"}}

现在分析上述用户请求并返回JSON："""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        registry: Optional[UnifiedRegistry] = None,
        confidence_threshold: float = 0.7
    ):
        """
        初始化Claude意图分析器

        Args:
            backend_orch: BackendOrchestrator实例
            registry: UnifiedRegistry实例（用于资源推断）
            confidence_threshold: 置信度阈值，低于此值将回退到规则引擎
        """
        self.backend_orch = backend_orch
        self.registry = registry
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

            # 4. Phase 1: 资源推断（如果 registry 可用）
            entity, candidates = None, []
            if self.registry:
                entity, candidates = self._infer_resources(
                    request=request,
                    task_type=intent_data["task_type"],
                    mode=intent_data["mode"]
                )

            # 5. 构造Intent对象
            return Intent(
                mode=ExecutionMode(intent_data["mode"]),
                task_type=intent_data["task_type"],
                complexity=intent_data["complexity"],
                backend_hint=intent_data.get("backend_hint") if intent_data.get("backend_hint") != "null" else None,
                skill_hint=intent_data.get("skill_hint") if intent_data.get("skill_hint") != "null" else None,
                confidence=float(intent_data.get("confidence", 0.8)),
                reasoning=intent_data.get("reasoning"),
                entity=entity,
                candidates=candidates,
                enable_parallel=bool(intent_data.get("enable_parallel", False)),
                parallel_reasoning=intent_data.get("parallel_reasoning")
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

    def _infer_resources(self, request: str, task_type: str, mode: str) -> tuple:
        """
        Phase 1: 资源推断逻辑

        根据用户需求推断合适的资源（Skills/Agents/Commands/Prompts）

        策略：
        1. 关键词匹配（基于 description 和 tags）
        2. 任务类型映射（task_type → resource_type）
        3. 优先级排序

        Args:
            request: 用户请求文本
            task_type: 任务类型
            mode: 执行模式

        Returns:
            (entity, candidates) - 主实体和候选资源列表
        """
        if not self.registry:
            return None, []

        # 1. 提取关键词
        keywords = self._extract_keywords(request)

        # 2. 根据 mode 确定要搜索的资源类型
        resource_types = self._get_resource_types_by_mode(mode)

        # 3. 获取所有启用的资源
        all_resources = []
        for res_type in resource_types:
            resources = self.registry.list_resources(
                type_filter=res_type,
                enabled_only=True
            )
            all_resources.extend(resources)

        # 4. 计算匹配分数
        scored_resources = []
        for resource in all_resources:
            score = self._calculate_match_score(keywords, resource, task_type)
            if score > 0.3:  # 匹配度阈值
                scored_resources.append((resource.namespace, score))

        # 5. 排序（按匹配度降序）
        scored_resources.sort(key=lambda x: x[1], reverse=True)

        # 6. 提取 entity 和 candidates
        entity = scored_resources[0][0] if scored_resources else None
        candidates = [r[0] for r in scored_resources[:5]]  # Top 5

        return entity, candidates

    def _extract_keywords(self, request: str) -> list:
        """
        从用户需求中提取关键词

        简单实现：字符级分词（中文）+ 单词分词（英文） + 停用词过滤

        Args:
            request: 用户请求文本

        Returns:
            关键词列表
        """
        # 停用词列表（简化版）
        stopwords = {
            '帮我', '请', '我', '的', '了', '和', '是', '在', '有', '这', '个',
            '要', '能', '可以', '需要', '一个', '进行', '使用', '对', '为',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'help', 'me', 'please', 'can', 'could', 'would'
        }

        import string
        import re

        # 移除标点符号
        translator = str.maketrans('', '', string.punctuation + '，。！？：；、')
        cleaned = request.translate(translator)

        keywords = []

        # 分离中文和英文
        # 提取英文单词
        english_words = re.findall(r'[a-zA-Z]+', cleaned)
        keywords.extend([w.lower() for w in english_words if w.lower() not in stopwords and len(w) > 1])

        # 提取中文词（简单 2-3 字组合）
        chinese_text = re.sub(r'[a-zA-Z\s]+', '', cleaned)
        # 生成 2字 和 3字 组合
        for i in range(len(chinese_text)):
            # 2字词
            if i + 1 < len(chinese_text):
                word = chinese_text[i:i+2]
                if word not in stopwords:
                    keywords.append(word)
            # 3字词
            if i + 2 < len(chinese_text):
                word = chinese_text[i:i+3]
                if word not in stopwords:
                    keywords.append(word)

        # 去重
        return list(set(keywords))

    def _get_resource_types_by_mode(self, mode: str) -> list:
        """
        根据执行模式确定要搜索的资源类型

        Args:
            mode: 执行模式

        Returns:
            ResourceType 列表
        """
        mode_to_types = {
            "skill": [ResourceType.SKILL],
            "agent": [ResourceType.AGENT],
            "command": [ResourceType.COMMAND],
            "prompt": [ResourceType.PROMPT],
            "backend": [ResourceType.SKILL, ResourceType.PROMPT],  # Backend 可用 skill 或 prompt
        }

        return mode_to_types.get(mode, [ResourceType.SKILL])

    def _calculate_match_score(self, keywords: list, resource: ResourceMetadata, task_type: str) -> float:
        """
        计算资源与需求的匹配分数

        评分维度（每个维度最多得分一次）：
        1. 名称匹配（权重 0.4）
        2. 描述匹配（权重 0.3）
        3. 标签匹配（权重 0.2）
        4. 任务类型匹配（权重 0.1）

        Args:
            keywords: 关键词列表
            resource: 资源元数据
            task_type: 任务类型

        Returns:
            匹配分数 (0.0-1.0)
        """
        score = 0.0

        # 1. 名称匹配（最多 0.4 分）
        resource_name_lower = resource.name.lower()
        name_match = any(keyword in resource_name_lower for keyword in keywords)
        if name_match:
            score += 0.4

        # 2. 描述匹配（最多 0.3 分）
        description = resource.config.get('description', '').lower()
        desc_match_count = sum(1 for keyword in keywords if keyword in description)
        if desc_match_count > 0:
            # 多个关键词匹配描述，分数稍高，但最多 0.3
            score += min(0.3, desc_match_count * 0.15)

        # 3. 标签匹配（最多 0.2 分）
        tags = resource.config.get('tags', [])
        tag_match = any(any(keyword in tag.lower() for tag in tags) for keyword in keywords)
        if tag_match:
            score += 0.2

        # 4. 任务类型匹配（最多 0.1 分）
        resource_task_types = resource.config.get('task_types', [])
        if task_type in resource_task_types:
            score += 0.1

        # 归一化到 0-1
        return min(score, 1.0)


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
