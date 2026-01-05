#!/usr/bin/env python3
"""
MasterOrchestrator - 总协调器

智能路由系统，支持5种执行模式：
- command: 简单命令执行
- agent: 智能体调用
- prompt: 提示词模板
- skill: 技能系统
- backend: 直接后端调用
"""

import sys
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 修复直接运行时的导入路径问题
if __name__ == "__main__" and __package__ is None:
    # 添加父目录到sys.path以支持绝对导入
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    __package__ = "orchestrator"

# 配置logger
logger = logging.getLogger(__name__)

# 导入核心模块（现在使用orchestrator内部结构）
from .core.event_parser import EventStream
from .core.backend_orchestrator import BackendOrchestrator, TaskResult

# V3 新增：配置和注册系统
try:
    from .core.config_loader import ConfigLoader, OrchestratorConfig
    from .core.unified_registry import UnifiedRegistry, ResourceMetadata, create_registry_from_config
    from .core.executor_factory import ExecutorFactory
    from .core.dependency_analyzer import DependencyAnalyzer, Task, ParallelGroup
    from .core.parallel_scheduler import ParallelScheduler, TaskResult as SchedulerTaskResult, BatchResult
    from .core.slash_command_registry import SlashCommandRegistry, register_builtin_commands
    from .core.slash_command import SlashCommandResult
    V3_AVAILABLE = True
except ImportError as e:
    # V3组件不可用时的fallback
    ConfigLoader = None
    UnifiedRegistry = None
    ExecutorFactory = None
    DependencyAnalyzer = None
    ParallelScheduler = None
    SlashCommandRegistry = None
    V3_AVAILABLE = False

# 导入执行器
from .executors.command_executor import CommandExecutor, CommandResult
from .executors.prompt_manager import PromptManager
from .executors.agent_caller import AgentCaller, AgentRequest, AgentResult, AgentType

# 导入技能系统
from .skills.skill_registry import SkillRegistry
from .skills.dev_workflow import DevWorkflowAgent, WorkflowResult

# 导入客户端
try:
    from .clients.aduib_client import AduibClient, CachedResult
    ADUIB_AVAILABLE = True
except ImportError:
    AduibClient = None
    CachedResult = None
    ADUIB_AVAILABLE = False

# Phase 1: 导入扩展的 Intent 和 ExecutionMode（包含 entity 和 candidates 字段）
try:
    from .analyzers.claude_intent_analyzer import Intent, ExecutionMode
    INTENT_WITH_CANDIDATES = True
except ImportError:
    # Fallback：使用本地定义（向后兼容）
    class ExecutionMode(Enum):
        """执行模式枚举"""
        COMMAND = "command"
        AGENT = "agent"
        PROMPT = "prompt"
        SKILL = "skill"
        BACKEND = "backend"

    @dataclass
    class Intent:
        """用户意图分析结果（Fallback版本）"""
        mode: ExecutionMode
        task_type: str
        complexity: str
        backend_hint: Optional[str] = None
        skill_hint: Optional[str] = None
        confidence: float = 0.0
        entity: Optional[str] = None
        candidates: list = None
        enable_parallel: bool = False
        parallel_reasoning: Optional[str] = None

        def __post_init__(self):
            if self.candidates is None:
                self.candidates = []

    INTENT_WITH_CANDIDATES = False


class IntentAnalyzer:
    """
    意图分析器 - 使用规则引擎分析用户请求

    分类维度：
    - 执行模式（command/agent/prompt/skill/backend）
    - 任务类型（dev/ux/analysis/test）
    - 复杂度（simple/medium/complex）
    """

    # 关键词模式匹配（中文不使用\b边界，直接匹配）
    PATTERNS = {
        ExecutionMode.COMMAND: [
            r'\b(git|npm|docker|pytest|build|test|run)\b',
            r'(执行|运行)\s*(命令|脚本)',
        ],
        ExecutionMode.SKILL: [
            r'(开发|实现|设计).{0,10}(系统|功能|项目|小程序|应用|平台|界面)',
            r'(完整|多阶段|工作流)\s*(流程|开发)',
            r'(电商|后台|管理系统|小程序)',
            r'(设计|开发).{0,20}(UX|UI|用户体验)',
        ],
        ExecutionMode.BACKEND: [
            r'(分析|解释|优化)\s*(代码|函数)',
            r'(简单|快速)\s*(查询|回答)',
        ],
    }

    TASK_KEYWORDS = {
        "dev": ["开发", "实现", "编码", "功能", "implement", "develop"],
        "ux": ["设计", "界面", "用户体验", "UI", "UX", "design"],
        "analysis": ["分析", "理解", "解释", "analyze", "explain"],
        "test": ["测试", "验证", "test", "verify"],
    }

    COMPLEXITY_KEYWORDS = {
        "simple": ["简单", "快速", "single", "simple", "quick"],
        "medium": ["中等", "moderate"],
        "complex": ["复杂", "完整", "系统", "项目", "complex", "full", "system"],
    }

    PARALLEL_KEYWORDS = {
        "explicit": ["批量", "多个", "同时", "并行", "并发", "batch", "multiple", "parallel", "concurrent"],
        "implicit": ["所有", "每个", "分别", "各个", "all", "each", "every"],
    }

    def analyze(self, request: str) -> Intent:
        """
        分析用户请求，返回意图

        Args:
            request: 用户请求文本

        Returns:
            Intent对象
        """
        mode = self._classify_mode(request)
        task_type = self._classify_task(request)
        complexity = self._classify_complexity(request)
        backend_hint = self._extract_backend_hint(request)
        skill_hint = self._extract_skill_hint(request)
        enable_parallel, parallel_reasoning = self._classify_parallelizable(request, task_type, complexity)

        return Intent(
            mode=mode,
            task_type=task_type,
            complexity=complexity,
            backend_hint=backend_hint,
            skill_hint=skill_hint,
            confidence=0.8,
            enable_parallel=enable_parallel,
            parallel_reasoning=parallel_reasoning
        )

    def _classify_mode(self, request: str) -> ExecutionMode:
        """分类执行模式"""
        request_lower = request.lower()

        # 优先级匹配
        for mode, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, request, re.IGNORECASE):
                    return mode

        # 默认：根据复杂度选择
        if any(kw in request for kw in self.COMPLEXITY_KEYWORDS["complex"]):
            return ExecutionMode.SKILL

        return ExecutionMode.BACKEND

    def _classify_task(self, request: str) -> str:
        """分类任务类型"""
        for task, keywords in self.TASK_KEYWORDS.items():
            if any(kw in request for kw in keywords):
                return task
        return "general"

    def _classify_complexity(self, request: str) -> str:
        """分类复杂度"""
        for level, keywords in self.COMPLEXITY_KEYWORDS.items():
            if any(kw in request for kw in keywords):
                return level
        return "medium"

    def _extract_backend_hint(self, request: str) -> Optional[str]:
        """提取后端提示"""
        if "claude" in request.lower():
            return "claude"
        if "gemini" in request.lower():
            return "gemini"
        if "codex" in request.lower() or "deepseek" in request.lower():
            return "codex"
        return None

    def _extract_skill_hint(self, request: str) -> Optional[str]:
        """提取技能提示"""
        if "开发" in request and "工作流" in request:
            return "multcode-dev-workflow-agent"
        if "UX" in request or "用户体验" in request:
            return "ux-design-gemini"
        if "代码" in request and "实现" in request:
            return "code-with-codex"
        return None

    def _classify_parallelizable(self, request: str, task_type: str, complexity: str) -> tuple:
        """
        判断任务是否适合并行执行

        Args:
            request: 用户请求文本
            task_type: 任务类型
            complexity: 复杂度

        Returns:
            (enable_parallel, parallel_reasoning) - 是否并行及原因
        """
        request_lower = request.lower()

        # 1. 检查明确的并行关键词
        has_explicit_keywords = any(kw in request for kw in self.PARALLEL_KEYWORDS["explicit"])
        if has_explicit_keywords:
            return True, "用户明确提到批量/并行处理"

        # 2. 检查隐式的并行关键词（需要结合其他条件）
        has_implicit_keywords = any(kw in request for kw in self.PARALLEL_KEYWORDS["implicit"])

        # 3. 检查是否涉及多个文件/模块（通过关键词推断）
        multi_file_indicators = ["文件", "模块", "组件", "服务", "目录", "files", "modules", "components", "services", "directory"]
        has_multi_file = any(kw in request for kw in multi_file_indicators)

        # 4. 根据任务类型和复杂度推断
        if has_implicit_keywords and has_multi_file:
            if task_type in ["dev", "test", "analysis"] and complexity in ["medium", "complex"]:
                return True, "涉及多个独立单元，适合并行处理"

        # 5. 复杂开发任务，包含多个独立模块
        if complexity == "complex" and task_type == "dev":
            module_keywords = ["包含", "以及", "和", "还有", "include", "with", "and"]
            if any(kw in request for kw in module_keywords) and has_multi_file:
                return True, "复杂任务包含多个独立模块，可并行开发"

        # 6. 测试任务通常可以并行
        if task_type == "test" and complexity in ["medium", "complex"]:
            return True, "测试任务通常可并行执行"

        # 默认不启用并行
        return False, "单一任务或有依赖关系，不适合并行"


class ExecutionRouter:
    """
    执行路由器 - 根据意图选择执行路径

    路由逻辑：
    - command → CommandExecutor
    - agent → AgentCaller
    - prompt → PromptManager
    - skill → SkillExecutor
    - backend → BackendOrchestrator

    Phase 2 增强：
    - 支持候选资源列表 (intent.candidates)
    - 实现资源降级策略 (主资源失败 → 备选资源)
    - 资源可用性检查 (enabled + 依赖满足)
    - 执行反馈机制 (记录成功率)
    """

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        registry: Optional['UnifiedRegistry'] = None
    ):
        """
        初始化路由器

        Args:
            backend_orch: BackendOrchestrator实例
            registry: UnifiedRegistry实例（用于资源可用性检查）
        """
        self.backend_orch = backend_orch
        self.registry = registry  # Phase 2: 资源注册表

        # 使用新版CommandExecutor（支持memex-cli）
        self.command_executor = CommandExecutor(
            backend_orch=backend_orch,
            use_claude_parser=True,      # 启用Claude解析
            fallback_to_rules=True,      # 允许fallback到规则引擎
            timeout=60
        )

        # 使用新版PromptManager V2（支持memex-cli）
        self.prompt_manager = PromptManager(
            backend_orch=backend_orch,
            use_claude_renderer=True,    # 启用Claude渲染
            fallback_to_local=True       # 允许fallback到本地渲染
        )

        # 使用新版AgentCaller V2（支持memex-cli）
        self.agent_caller = AgentCaller(
            backend_orch=backend_orch,
            use_claude_router=True,      # 启用Claude路由
            fallback_to_simple=True      # 允许fallback到简单实现
        )
        self.workflow_agent = DevWorkflowAgent(parse_events=True, timeout=600)
        self.skill_registry = SkillRegistry()

    def route(self, intent: Intent, request: str) -> Any:
        """
        路由到对应的执行器

        Phase 2 增强：
        - 支持候选资源列表 (intent.candidates)
        - 实现降级策略（主资源失败 → 备选资源）
        - 记录执行反馈

        Args:
            intent: 意图分析结果
            request: 原始请求

        Returns:
            执行结果
        """
        # Phase 2: 如果有候选资源列表，尝试依次执行（降级策略）
        if hasattr(intent, 'candidates') and intent.candidates and self.registry:
            return self._route_with_candidates(intent, request)

        # 传统路由逻辑（向后兼容）
        return self._route_legacy(intent, request)

    def _route_legacy(self, intent: Intent, request: str) -> Any:
        """
        传统路由逻辑（向后兼容）

        Args:
            intent: 意图分析结果
            request: 原始请求

        Returns:
            执行结果
        """
        if intent.mode == ExecutionMode.COMMAND:
            return self._execute_command(request)
        elif intent.mode == ExecutionMode.AGENT:
            return self._call_agent(request, intent)
        elif intent.mode == ExecutionMode.PROMPT:
            return self._use_prompt(request, intent)
        elif intent.mode == ExecutionMode.SKILL:
            return self._execute_skill(request, intent)
        elif intent.mode == ExecutionMode.BACKEND:
            return self._call_backend(request, intent)
        else:
            raise ValueError(f"Unknown execution mode: {intent.mode}")

    def _route_with_candidates(self, intent: Intent, request: str) -> Any:
        """
        Phase 2: 使用候选资源列表的路由逻辑

        尝试候选资源，实现降级策略：
        1. 检查资源可用性
        2. 尝试执行第一个可用资源
        3. 如果失败，尝试下一个候选资源
        4. 记录执行反馈

        Args:
            intent: 意图分析结果
            request: 原始请求

        Returns:
            执行结果

        Raises:
            RuntimeError: 所有候选资源都失败
        """
        errors = []

        # 优先使用 entity，否则使用 candidates
        resources_to_try = [intent.entity] if intent.entity else []
        resources_to_try.extend([c for c in intent.candidates if c != intent.entity])

        logger.info(f"[ExecutionRouter] Trying {len(resources_to_try)} candidate resources")

        for namespace in resources_to_try:
            # 1. 检查资源可用性
            is_available, reason = self._check_resource_availability(namespace)

            if not is_available:
                logger.warning(f"[ExecutionRouter] Resource '{namespace}' unavailable: {reason}")
                errors.append(f"{namespace}: {reason}")
                continue

            # 2. 尝试执行资源
            try:
                logger.info(f"[ExecutionRouter] Executing resource: {namespace}")

                # 从 namespace 提取执行模式和名称
                mode_str, resource_name = self._parse_namespace(namespace)

                # 根据资源类型执行
                if mode_str == "skill":
                    result = self._execute_skill_by_namespace(namespace, request, intent)
                elif mode_str == "agent":
                    result = self._call_agent_by_namespace(namespace, request, intent)
                elif mode_str == "prompt":
                    result = self._use_prompt_by_namespace(namespace, request, intent)
                elif mode_str == "command":
                    result = self._execute_command(request)
                else:
                    # Fallback 到传统路由
                    result = self._route_legacy(intent, request)

                # 3. 记录成功反馈
                self._record_execution_feedback(namespace, success=True)
                logger.info(f"[ExecutionRouter] Resource '{namespace}' succeeded")

                return result

            except Exception as e:
                # 4. 记录失败反馈
                error_msg = str(e)
                self._record_execution_feedback(namespace, success=False, error=error_msg)
                logger.warning(f"[ExecutionRouter] Resource '{namespace}' failed: {error_msg}")
                errors.append(f"{namespace}: {error_msg}")
                continue

        # 所有候选资源都失败
        error_summary = "\n".join([f"  - {err}" for err in errors])
        raise RuntimeError(
            f"All candidate resources failed:\n{error_summary}"
        )

    def _parse_namespace(self, namespace: str) -> Tuple[str, str]:
        """
        解析资源命名空间

        Args:
            namespace: 资源命名空间（如 "skill:code-review"）

        Returns:
            (mode, name) - 执行模式和资源名称
        """
        if ':' in namespace:
            parts = namespace.split(':', 1)
            return parts[0], parts[1]
        else:
            # 没有冒号，默认为 backend
            return "backend", namespace

    def _execute_skill_by_namespace(
        self,
        namespace: str,
        request: str,
        intent: Intent
    ) -> Any:
        """
        通过 namespace 执行 skill

        Args:
            namespace: 资源命名空间
            request: 用户请求
            intent: 意图对象

        Returns:
            执行结果
        """
        # 获取 skill 资源
        resource = self.registry.get(namespace) if self.registry else None

        if not resource:
            raise ValueError(f"Skill resource '{namespace}' not found")

        # 使用 ExecutorFactory 创建执行器（如果可用）
        if hasattr(self, 'factory') and self.factory:
            executor = self.factory.create_executor(namespace)
            if executor:
                return executor.execute(request)

        # Fallback：使用传统 skill 执行逻辑
        return self._execute_skill(request, intent)

    def _call_agent_by_namespace(
        self,
        namespace: str,
        request: str,
        intent: Intent
    ) -> Any:
        """
        通过 namespace 调用 agent

        Args:
            namespace: 资源命名空间
            request: 用户请求
            intent: 意图对象

        Returns:
            执行结果
        """
        # Fallback：使用传统 agent 调用逻辑
        return self._call_agent(request, intent)

    def _use_prompt_by_namespace(
        self,
        namespace: str,
        request: str,
        intent: Intent
    ) -> Any:
        """
        通过 namespace 使用 prompt

        Args:
            namespace: 资源命名空间
            request: 用户请求
            intent: 意图对象

        Returns:
            执行结果
        """
        # Fallback：使用传统 prompt 逻辑
        return self._use_prompt(request, intent)

    def _execute_command(self, request: str) -> CommandResult:
        """执行简单命令"""
        return self.command_executor.execute(request)

    def _call_agent(self, request: str, intent: Intent) -> AgentResult:
        """调用智能体"""
        # 根据任务建议智能体类型
        agent_type = self.agent_caller.suggest_agent_type(request)

        # 创建智能体请求
        agent_request = AgentRequest(
            agent_type=agent_type,
            prompt=request,
            thoroughness="medium" if agent_type == AgentType.EXPLORE else None
        )

        return self.agent_caller.call_agent(agent_request)

    def _use_prompt(self, request: str, intent: Intent) -> TaskResult:
        """使用提示词模板"""
        # 尝试从请求中提取模板名称和变量
        template_name, variables = self._parse_prompt_request(request, intent)

        # 渲染模板
        if template_name:
            result = self.prompt_manager.render(template_name, **variables)
            if result.success:
                # 使用渲染后的提示词调用后端
                backend = self._select_backend(intent)
                return self.backend_orch.run_task(backend, result.rendered_prompt, "jsonl")

        # 如果无法识别模板，回退到直接调用
        backend = self._select_backend(intent)
        return self.backend_orch.run_task(backend, request, "jsonl")

    def _parse_prompt_request(self, request: str, intent: Intent) -> Tuple[Optional[str], Dict]:
        """
        从请求中解析提示词模板和变量

        Args:
            request: 用户请求
            intent: 意图

        Returns:
            (template_name, variables)
        """
        # 简单的关键词匹配
        keywords_to_template = {
            "代码审查": "code-review",
            "代码生成": "code-generation",
            "生成文档": "documentation",
            "bug": "bug-analysis",
            "重构": "refactoring",
            "测试": "test-generation",
        }

        for keyword, template in keywords_to_template.items():
            if keyword in request:
                # 提取基本变量（简化实现）
                variables = {
                    "language": "Python",  # 默认
                    "code": "[待提供代码]",
                }
                return template, variables

        return None, {}

    def _execute_skill(self, request: str, intent: Intent) -> Any:
        """
        执行技能

        支持：
        - multcode-dev-workflow-agent: 5阶段自动化工作流
        - 其他技能：增强提示词 + 后端调用
        """
        # 检查是否为多阶段开发工作流
        if (intent.skill_hint == "multcode-dev-workflow-agent" or
            intent.complexity == "complex" and intent.task_type == "dev"):

            # 使用 DevWorkflowAgent 执行5阶段工作流
            return self.workflow_agent.run(request, verbose=False)

        # 其他技能：使用增强提示词调用后端
        backend = self._select_backend_for_skill(intent)
        enhanced_request = self._enhance_skill_request(request, intent)

        return self.backend_orch.run_task(
            backend=backend,
            prompt=enhanced_request,
            stream_format="jsonl"
        )

    def _call_backend(self, request: str, intent: Intent) -> TaskResult:
        """直接调用后端"""
        backend = intent.backend_hint or self._select_backend(intent)

        return self.backend_orch.run_task(
            backend=backend,
            prompt=request,
            stream_format="jsonl"
        )

    def _select_backend(self, intent: Intent) -> str:
        """根据意图选择后端"""
        if intent.task_type == "dev":
            return "codex"
        elif intent.task_type == "ux":
            return "gemini"
        else:
            return "claude"

    def _select_backend_for_skill(self, intent: Intent) -> str:
        """为技能选择后端"""
        if intent.skill_hint == "multcode-dev-workflow-agent":
            return "codex"
        elif intent.skill_hint == "ux-design-gemini":
            return "gemini"
        elif intent.skill_hint == "code-with-codex":
            return "codex"
        else:
            return self._select_backend(intent)

    def _enhance_skill_request(self, request: str, intent: Intent) -> str:
        """为技能请求添加上下文"""
        if intent.skill_hint == "multcode-dev-workflow-agent":
            return f"""你是一个多阶段开发流程专家。请按照以下5个阶段处理用户需求：

阶段1：需求分析
阶段2：功能设计
阶段3：UX设计
阶段4：开发计划
阶段5：实现

用户需求：
{request}

请开始执行。"""

        return request

    # ========== Phase 2: 候选资源支持和降级策略 ==========

    def _check_resource_availability(self, namespace: str) -> Tuple[bool, Optional[str]]:
        """
        检查资源是否可用

        Args:
            namespace: 资源命名空间（如 "skill:code-review"）

        Returns:
            (is_available, reason) - 是否可用 + 原因（如果不可用）
        """
        if not self.registry:
            # 没有 registry，默认可用（向后兼容）
            return True, None

        # 从 registry 获取资源
        resource = self.registry.get(namespace)

        if not resource:
            return False, f"Resource '{namespace}' not found in registry"

        # 检查是否启用
        if not resource.enabled:
            return False, f"Resource '{namespace}' is disabled"

        # 检查依赖是否满足（简化实现：检查 dependencies 列表）
        dependencies = resource.config.get('dependencies', [])
        for dep in dependencies:
            dep_resource = self.registry.get(dep)
            if not dep_resource or not dep_resource.enabled:
                return False, f"Dependency '{dep}' not available"

        return True, None

    def _record_execution_feedback(
        self,
        namespace: Optional[str],
        success: bool,
        error: Optional[str] = None
    ):
        """
        记录执行反馈（简化实现：使用 logger）

        后续可扩展为：
        - 持久化到数据库
        - 计算成功率
        - 调整资源优先级

        Args:
            namespace: 资源命名空间
            success: 是否成功
            error: 错误信息（如果失败）
        """
        if namespace:
            status = "SUCCESS" if success else "FAIL"
            logger.info(f"[ExecutionFeedback] {namespace} - {status}")
            if error:
                logger.warning(f"[ExecutionFeedback] {namespace} - Error: {error}")


class MasterOrchestrator:
    """
    总协调器 - 系统入口

    工作流程：
    1. 接收用户请求
    2. IntentAnalyzer 分析意图
    3. ExecutionRouter 路由执行
    4. (可选) 查询远程缓存 / 上传结果
    5. 返回结果
    """

    def __init__(
        self,
        timeout: int = 300,
        use_remote: Optional[bool] = None,
        aduib_url: Optional[str] = None,
        aduib_api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_upload: bool = True,
        use_claude_intent: bool = True,
        intent_confidence_threshold: float = 0.7,
        fallback_to_rules: bool = True,
        # V3 新增参数
        config_path: Optional[Path] = None,
        auto_discover: bool = True,
        enable_parallel: bool = True,
        max_parallel_workers: int = 3,
        parallel_timeout: int = 120
    ):
        """
        初始化总协调器

        Args:
            timeout: 超时时间（秒）
            use_remote: 是否使用远程服务（None=自动检测）
            aduib_url: aduib-ai 服务地址
            aduib_api_key: aduib-ai API 密钥
            enable_cache: 是否启用缓存查询
            enable_upload: 是否启用结果上传
            use_claude_intent: 是否使用Claude进行意图识别（默认True）
            intent_confidence_threshold: Claude意图识别置信度阈值
            fallback_to_rules: 低置信度或失败时是否回退到规则引擎
            config_path: V3配置文件路径（None=使用当前目录）
            auto_discover: V3自动发现和注册资源（默认False，保持向后兼容）
            enable_parallel: V3启用并行执行（默认False）
            max_parallel_workers: V3最大并行工作线程数
            parallel_timeout: V3单任务超时时间（秒）
        """
        # 本地组件（必需）
        self.backend_orch = BackendOrchestrator(
            timeout=timeout
        )

        # 初始化本地缓存目录（需求1：在.memex/orchestrator下创建缓存）
        self.cache_dir = self._init_cache_directory()

        # 初始化日志管理器
        from .core.log_manager import LogManager
        self.log_manager = LogManager(
            log_dir=self.cache_dir / "logs",
            console_output=False  # 避免重复输出到控制台
        )
        self.log_manager.setup(level="INFO")

        # 初始化临时文件管理器
        from .core.temp_file_manager import TempFileManager
        self.temp_file_manager = TempFileManager(
            temp_dir=self.cache_dir / "temp",
            ttl_seconds=3600  # 1小时过期
        )

        # 意图分析器配置
        self.use_claude_intent = use_claude_intent
        self.fallback_to_rules = fallback_to_rules

        # 创建规则引擎分析器（作为备份）
        self.rule_analyzer = IntentAnalyzer()

        # 创建Claude分析器（如果启用）
        self.claude_analyzer = None
        if use_claude_intent:
            try:
                from .analyzers.claude_intent_analyzer import ClaudeIntentAnalyzer
                self.claude_analyzer = ClaudeIntentAnalyzer(
                    backend_orch=self.backend_orch,
                    confidence_threshold=intent_confidence_threshold
                )
            except Exception as e:
                print(f"[警告] 无法初始化Claude意图分析器: {e}")
                print("[提示] 将使用规则引擎作为fallback")
                self.use_claude_intent = False

        # 向后兼容：默认使用规则引擎
        self.analyzer = self.rule_analyzer

        # Phase 2: ExecutionRouter 暂时不传 registry（等 V3 初始化后再设置）
        self.router = None

        # 远程组件（可选）
        self.aduib_client = None
        self.enable_cache = enable_cache
        self.enable_upload = enable_upload

        # 自动检测或手动配置 aduib-ai

        if use_remote and ADUIB_AVAILABLE:
            try:
                self.aduib_client = AduibClient(
                    base_url=aduib_url,
                    api_key=aduib_api_key,
                    timeout=30
                )
            except Exception as e:
                print(f"[警告] 无法初始化 aduib-ai 客户端: {e}")
                print("[提示] 将以纯本地模式运行")
                self.aduib_client = None
        elif use_remote and not ADUIB_AVAILABLE:
            print("[警告] aduib-ai 客户端不可用（可能缺少 requests 库）")
            print("[提示] 安装: pip install requests")
            print("[提示] 将以纯本地模式运行")

        # V3 配置和注册系统（可选）
        self.config = None
        self.registry = None
        self.factory = None
        self.scheduler = None
        self.slash_registry = None  # V3.1: Slash Command Registry
        self.auto_discover = auto_discover
        self.enable_parallel = enable_parallel

        if auto_discover and V3_AVAILABLE:
            try:
                # 1. 加载配置
                loader = ConfigLoader(project_root=config_path or Path.cwd())
                self.config = loader.load()

                # 2. 初始化注册表
                self.registry = create_registry_from_config(self.config)

                # 3. 初始化执行器工厂
                self.factory = ExecutorFactory(self.backend_orch, self.registry)

                # 4. 初始化并行调度器（如果启用）
                if enable_parallel:
                    self.scheduler = ParallelScheduler(
                        factory=self.factory,
                        max_workers=max_parallel_workers,
                        timeout_per_task=parallel_timeout
                    )

                # 5. 初始化 Slash Command Registry (V3.1)
                self.slash_registry = SlashCommandRegistry(orchestrator=self)
                register_builtin_commands(self.slash_registry)

                # 6. 注册自定义 Slash Commands (从配置)
                self._register_custom_slash_commands()

                # 7. Phase 2: 创建 ExecutionRouter（传入 registry）
                self.router = ExecutionRouter(
                    backend_orch=self.backend_orch,
                    registry=self.registry
                )

                # Phase 1: 传递 registry 给 ClaudeIntentAnalyzer
                if self.claude_analyzer:
                    self.claude_analyzer.registry = self.registry

            except Exception as e:
                print(f"[警告] V3自动发现初始化失败: {e}")
                print("[提示] 将使用传统模式运行")
                self.config = None
                self.registry = None
                self.factory = None
                self.scheduler = None
                self.slash_registry = None
                self.auto_discover = False
                # 创建不带 registry 的 ExecutionRouter（向后兼容）
                self.router = ExecutionRouter(self.backend_orch)

        elif auto_discover and not V3_AVAILABLE:
            print("[警告] V3组件不可用（可能缺少依赖）")
            print("[提示] 将使用传统模式运行")
            self.auto_discover = False
            # 创建不带 registry 的 ExecutionRouter（向后兼容）
            self.router = ExecutionRouter(self.backend_orch)

        # Phase 2: 如果还没有创建 router（非 V3 模式），创建一个不带 registry 的
        if not self.router:
            self.router = ExecutionRouter(self.backend_orch)

    def process(self, request: str, verbose: bool = False) -> Any:
        """
        处理用户请求（支持 Slash Command 和自然语言）

        Args:
            request: 用户请求文本（可以是 /command 或自然语言）
            verbose: 是否输出详细信息

        Returns:
            执行结果
        """
        # 0. 记录任务开始
        self.log_manager.log_task_start(request, "unknown")

        # 1. 检查是否为 Slash Command（V3.1）
        if request.strip().startswith('/'):
            return self._process_slash_command(request.strip(), verbose)

        # 2. 意图分析（优先使用Claude，失败则fallback到规则引擎）
        intent = self._analyze_intent(request, verbose)

        # 记录意图分析结果
        self.log_manager.log_intent_analysis(
            intent.mode.value,
            intent.task_type,
            intent.complexity,
            intent.confidence
        )

        if verbose:
            print(f"[意图分析]")
            print(f"  模式: {intent.mode.value}")
            print(f"  类型: {intent.task_type}")
            print(f"  复杂度: {intent.complexity}")
            if intent.backend_hint:
                print(f"  后端提示: {intent.backend_hint}")
            if intent.skill_hint:
                print(f"  技能提示: {intent.skill_hint}")
            if hasattr(intent, 'enable_parallel'):
                print(f"  并行执行: {'是' if intent.enable_parallel else '否'}")
                if intent.parallel_reasoning:
                    print(f"  并行理由: {intent.parallel_reasoning}")
            print()

        # 2. 任务分级（需求2：Task Tiering Expert Agent）
        task_tier = None
        if self.task_tiering_agent:
            try:
                task_tier = self.task_tiering_agent.analyze(request, intent, verbose)

                if verbose:
                    print(f"[任务分级]")
                    print(f"  优先级: {task_tier.priority.value}")
                    print(f"  预估时间: {task_tier.estimated_time_seconds}s")
                    print(f"  资源需求: {task_tier.resource_requirement.value}")
                    print(f"  可并行化: {task_tier.parallelization_potential:.2f}")
                    print(f"  推荐后端: {task_tier.recommended_backend}")
                    print(f"  推荐模式: {task_tier.recommended_mode}")
                    print(f"  置信度: {task_tier.confidence:.2f}")
                    if task_tier.reasoning:
                        print(f"  推理: {task_tier.reasoning}")
                    print()
            except Exception as e:
                if verbose:
                    print(f"[警告] 任务分级失败: {e}")
                    print()

        # 3. 查询远程缓存（如果启用）
        if self.aduib_client and self.enable_cache:
            backend = self._select_backend_for_intent(intent)
            cached = self.aduib_client.query_cache(
                request=request,
                mode=intent.mode.value,
                backend=backend
            )

            if cached:
                if verbose:
                    print(f"[缓存命中] 从远程缓存返回结果")
                    print(f"  任务 ID: {cached.task_id}")
                    print(f"  创建时间: {cached.created_at}")
                    print(f"  命中次数: {cached.hit_count}")
                    print()

                # 构造 TaskResult 返回（添加 prompt 参数）
                return TaskResult(
                    backend=backend,
                    prompt=request,
                    output=cached.output,
                    success=cached.success,
                    error=None,
                    run_id=None,
                    event_stream=None,
                    duration_seconds=0.0
                )

        # 3. 并行执行判断（如果推断为并行且启用了并行调度器）
        if hasattr(intent, 'enable_parallel') and intent.enable_parallel:
            # 尝试拆分任务
            subtasks = self._split_parallel_tasks(request, intent, verbose)

            if subtasks and len(subtasks) > 1:
                if self.scheduler and self.enable_parallel:
                    # 使用并行调度器执行
                    if verbose:
                        print(f"[并行执行] 检测到 {len(subtasks)} 个子任务，启动并行处理")
                        print(f"  推断理由: {intent.parallel_reasoning}")
                        for i, task in enumerate(subtasks, 1):
                            print(f"  子任务 {i}: {task[:50]}...")
                        print()

                    batch_result = self.process_batch(
                        requests=subtasks,
                        enable_parallel=True,
                        verbose=verbose
                    )

                    # 将批处理结果转换为单一结果返回
                    return self._batch_result_to_task_result(batch_result, request, intent)
                elif verbose:
                    print(f"[警告] 并行调度器未启用，将串行执行")
                    print(f"  提示: 初始化时设置 enable_parallel=True, auto_discover=True")
                    print()

        # 4. 本地执行（串行）
        if verbose and self.aduib_client and self.enable_cache:
            print(f"[缓存未命中] 本地执行任务")
            print()

        result = self.router.route(intent, request)

        # 4. 记录任务完成
        backend = self._select_backend_for_intent(intent)
        self.log_manager.log_task_complete(
            mode=intent.mode.value,
            backend=backend,
            duration=getattr(result, 'duration_seconds', 0.0),
            success=getattr(result, 'success', True)
        )

        # 5. 上传结果到远程（如果启用且成功）
        if self.aduib_client and self.enable_upload and self._should_upload(result):
            self._upload_result(
                request=request,
                intent=intent,
                backend=backend,
                result=result,
                verbose=verbose
            )

        return result

    def _analyze_intent(self, request: str, verbose: bool = False) -> Intent:
        """
        分析用户意图（支持Claude LLM和规则引擎fallback）

        Args:
            request: 用户请求
            verbose: 是否输出详细信息

        Returns:
            Intent对象
        """
        # 优先使用Claude意图识别
        if self.use_claude_intent and self.claude_analyzer:
            try:
                if verbose:
                    print(f"[意图识别] 使用Claude LLM分析...")

                intent = self.claude_analyzer.analyze(request)

                # 验证置信度
                if self.claude_analyzer.validate_intent(intent):
                    if verbose:
                        print(f"[意图识别] Claude分析成功 (confidence={intent.confidence:.2f})")
                        if intent.reasoning:
                            print(f"  推理: {intent.reasoning}")
                    return intent
                else:
                    if verbose:
                        print(f"[意图识别] Claude置信度不足 ({intent.confidence:.2f} < {self.claude_analyzer.confidence_threshold})")

                    if not self.fallback_to_rules:
                        # 不允许fallback，直接返回低置信度结果
                        return intent

                    if verbose:
                        print(f"[意图识别] Fallback到规则引擎...")

            except Exception as e:
                if verbose:
                    print(f"[意图识别] Claude分析失败: {e}")

                if not self.fallback_to_rules:
                    # 不允许fallback，抛出异常
                    raise RuntimeError(f"意图识别失败且禁用fallback: {e}")

                if verbose:
                    print(f"[意图识别] Fallback到规则引擎...")

        # 使用规则引擎
        if verbose and not (self.use_claude_intent and self.claude_analyzer):
            print(f"[意图识别] 使用规则引擎分析...")

        return self.rule_analyzer.analyze(request)

    def _select_backend_for_intent(self, intent: Intent) -> str:
        """根据意图选择后端"""
        if intent.backend_hint:
            return intent.backend_hint
        elif intent.task_type == "dev":
            return "codex"
        elif intent.task_type == "ux":
            return "gemini"
        else:
            return "claude"

    def _init_cache_directory(self) -> Path:
        """
        初始化本地缓存目录（需求1）

        创建目录结构：
        ~/.memex/orchestrator/
            ├── cache/          # 执行结果缓存
            ├── logs/           # 运行日志
            ├── registry/       # 资源注册缓存
            └── temp/           # 临时文件

        Returns:
            Path: 缓存根目录路径
        """
        cache_root = Path.home() / ".memex" / "orchestrator"

        # 创建子目录
        subdirs = ["cache", "logs", "registry", "temp"]
        for subdir in subdirs:
            dir_path = cache_root / subdir
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"本地缓存目录已初始化: {cache_root}")

        return cache_root

    def _should_upload(self, result: Any) -> bool:
        """判断是否应该上传结果"""
        # 只上传成功的 TaskResult 和 WorkflowResult
        if isinstance(result, TaskResult):
            return result.success
        elif isinstance(result, WorkflowResult):
            return result.success
        else:
            return False

    def _upload_result(
        self,
        request: str,
        intent: Intent,
        backend: str,
        result: Any,
        verbose: bool = False
    ):
        """上传结果到远程服务"""
        try:
            if isinstance(result, TaskResult):
                success = self.aduib_client.save_task_result(
                    request=request,
                    mode=intent.mode.value,
                    backend=backend,
                    success=result.success,
                    output=result.get_final_output() if hasattr(result, 'get_final_output') else result.output,
                    error=result.error,
                    run_id=result.run_id if hasattr(result, 'run_id') else None,
                    duration_seconds=result.duration_seconds if hasattr(result, 'duration_seconds') else None
                )
            elif isinstance(result, WorkflowResult):
                # 工作流结果：保存最终输出
                final_output = "\n\n".join([
                    f"=== 阶段 {i+1}: {stage.stage.value} ===\n{stage.output}"
                    for i, stage in enumerate(result.stages)
                ])

                success = self.aduib_client.save_task_result(
                    request=request,
                    mode=intent.mode.value,
                    backend=backend,
                    success=result.success,
                    output=final_output,
                    error=None,
                    run_id=None,
                    duration_seconds=result.total_duration_seconds
                )
            else:
                # 其他类型结果
                output_str = str(result)
                success = self.aduib_client.save_task_result(
                    request=request,
                    mode=intent.mode.value,
                    backend=backend,
                    success=True,
                    output=output_str,
                    error=None,
                    run_id=None,
                    duration_seconds=None
                )

            if verbose:
                if success:
                    print(f"[已保存] 结果已上传到远程服务")
                    print()
                else:
                    print(f"[警告] 结果上传失败")
                    print()

        except Exception as e:
            if verbose:
                print(f"[警告] 上传结果时发生异常: {e}")
                print()

    # ========== V3 新增方法 ==========

    def process_batch(
        self,
        requests: List[str],
        enable_parallel: Optional[bool] = None,
        verbose: bool = False
    ) -> 'BatchResult':
        """
        批量处理请求（V3功能，支持并行）

        Args:
            requests: 请求列表
            enable_parallel: 是否启用并行（None=使用初始化配置）
            verbose: 详细输出

        Returns:
            BatchResult批处理结果
        """
        if not V3_AVAILABLE or not self.factory:
            raise RuntimeError("V3批处理功能未启用（需要 auto_discover=True）")

        if enable_parallel is None:
            enable_parallel = self.enable_parallel

        # 1. 分析所有请求的意图，创建任务列表
        tasks = []
        for request in requests:
            intent = self._analyze_intent(request, verbose=False)
            namespace = self._intent_to_namespace(intent)

            task = Task(
                namespace=namespace,
                request=request,
                dependencies=[],
                metadata={"intent": intent}
            )
            tasks.append(task)

            if verbose:
                print(f"[任务创建] {request[:50]}... → {namespace}")

        # 2. 执行任务（并行或串行）
        if enable_parallel and self.scheduler:
            if verbose:
                print(f"\n[并行执行] {len(tasks)} 个任务，最多 {self.scheduler.max_workers} 个并行...")

            # 启用依赖分析和并行执行
            result = self.scheduler.execute_tasks(
                tasks=tasks,
                enable_dependency_analysis=True
            )
        else:
            if verbose:
                print(f"\n[串行执行] {len(tasks)} 个任务...")

            # 串行执行
            analyzer = DependencyAnalyzer(self.registry)
            single_group = ParallelGroup(level=0, tasks=tasks)

            if self.scheduler:
                result = self.scheduler.execute_parallel_groups([single_group])
            else:
                # 没有调度器，手动串行执行
                task_results = []
                import time
                start_time = time.time()

                for task in tasks:
                    try:
                        executor = self.factory.create_executor(task.namespace)
                        if executor:
                            output = executor.execute(task.request)
                            task_results.append(SchedulerTaskResult(
                                namespace=task.namespace,
                                success=True,
                                output=output,
                                duration_seconds=0.0
                            ))
                        else:
                            task_results.append(SchedulerTaskResult(
                                namespace=task.namespace,
                                success=False,
                                error=f"No executor for {task.namespace}",
                                duration_seconds=0.0
                            ))
                    except Exception as e:
                        task_results.append(SchedulerTaskResult(
                            namespace=task.namespace,
                            success=False,
                            error=str(e),
                            duration_seconds=0.0
                        ))

                total_duration = time.time() - start_time
                result = BatchResult(
                    total_tasks=len(task_results),
                    successful=sum(1 for r in task_results if r.success),
                    failed=sum(1 for r in task_results if not r.success),
                    total_duration_seconds=total_duration,
                    task_results=task_results
                )

        if verbose:
            print(f"\n[批处理完成] {result}")

        return result

    def _intent_to_namespace(self, intent: Intent) -> str:
        """
        将意图转换为资源命名空间

        Args:
            intent: Intent对象

        Returns:
            资源命名空间字符串
        """
        mode = intent.mode.value

        if mode == "command":
            # 尝试从请求中提取命令
            return f"command:default"
        elif mode == "skill" and intent.skill_hint:
            return f"skill:{intent.skill_hint}"
        elif mode == "agent":
            # 根据任务类型选择agent
            agent_type = "general"
            if intent.task_type == "dev":
                agent_type = "explore"
            return f"agent:{agent_type}"
        elif mode == "prompt":
            return f"prompt:default"
        else:
            return f"{mode}:default"

    def list_resources(
        self,
        type_filter: Optional[str] = None,
        source_filter: Optional[str] = None
    ) -> List['ResourceMetadata']:
        """
        列出已注册的资源（V3功能）

        Args:
            type_filter: 按类型过滤（skill/command/agent/prompt）
            source_filter: 按来源过滤（builtin/user/project）

        Returns:
            ResourceMetadata列表
        """
        if not V3_AVAILABLE or not self.registry:
            raise RuntimeError("V3资源注册功能未启用（需要 auto_discover=True）")

        # 转换type_filter字符串为ResourceType
        from .core.unified_registry import ResourceType

        rt_filter = None
        if type_filter:
            try:
                rt_filter = ResourceType(type_filter)
            except ValueError:
                raise ValueError(f"无效的类型过滤器: {type_filter}")

        return self.registry.list_resources(
            type_filter=rt_filter,
            source_filter=source_filter,
            enabled_only=True
        )

    def reload_config(self, verbose: bool = False):
        """
        重新加载配置（V3功能）

        Args:
            verbose: 详细输出
        """
        if not V3_AVAILABLE or not self.auto_discover:
            raise RuntimeError("V3配置重载功能未启用（需要 auto_discover=True）")

        try:
            # 重新加载配置
            loader = ConfigLoader(project_root=Path.cwd())
            self.config = loader.load()

            # 清空并重新填充注册表
            self.registry.clear()
            self.registry = create_registry_from_config(self.config)

            # 重新创建工厂（清除缓存）
            if self.factory:
                self.factory.clear_cache()
            self.factory = ExecutorFactory(self.backend_orch, self.registry)

            if verbose:
                print(f"[配置重载成功] 加载了 {len(self.registry)} 个资源")

        except Exception as e:
            if verbose:
                print(f"[配置重载失败] {e}")
            raise RuntimeError(f"配置重载失败: {e}")

    # ================== Slash Command 系统方法 (V3.1) ==================

    def _process_slash_command(self, request: str, verbose: bool = False) -> SlashCommandResult:
        """
        处理 Slash Command（V3.1新增）

        Args:
            request: Slash command字符串（如 "/discover", "/git-status"）
            verbose: 详细输出

        Returns:
            SlashCommandResult
        """
        if not self.slash_registry:
            # Slash Command 系统未启用
            return SlashCommandResult(
                command=request,
                success=False,
                error="Slash Command system not available (enable with auto_discover=True)"
            )

        # 解析命令和参数
        parts = request[1:].split()  # 移除开头的 '/'
        command_name = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if verbose:
            print(f"[Slash Command] /{command_name}")
            if args:
                print(f"  参数: {args}")
            print()

        # 执行命令
        result = self.slash_registry.execute(command_name, args, verbose=verbose)

        if verbose:
            print(f"\n[执行结果]")
            print(f"  成功: {result.success}")
            if result.duration_seconds:
                print(f"  耗时: {result.duration_seconds:.3f}s")
            if result.error:
                print(f"  错误: {result.error}")
            print()

        return result

    def _register_custom_slash_commands(self):
        """
        从配置注册自定义 Slash Commands (V3.1)

        将配置中的 slash_commands 转换为 SlashCommandMetadata 并注册到 slash_registry
        """
        if not self.config or not self.config.slash_commands:
            return

        from .core.slash_command import SlashCommandMetadata, SlashCommandType

        # 类型映射
        type_map = {
            "system": SlashCommandType.SYSTEM,
            "shell": SlashCommandType.SHELL,
            "skill": SlashCommandType.SKILL,
            "agent": SlashCommandType.AGENT,
            "prompt": SlashCommandType.PROMPT
        }

        for name, slash_config in self.config.slash_commands.items():
            try:
                # 转换为 SlashCommandMetadata
                command_type = type_map.get(slash_config.type)
                if not command_type:
                    logger.warning(f"Unknown slash command type '{slash_config.type}' for '{name}'")
                    continue

                metadata = SlashCommandMetadata(
                    name=name,
                    type=command_type,
                    description=slash_config.description,
                    handler=slash_config.handler,
                    command=slash_config.command,
                    skill=slash_config.skill,
                    agent_type=slash_config.agent_type,
                    prompt_template=slash_config.prompt_template,
                    enabled=slash_config.enabled,
                    priority=slash_config.priority,
                    source=slash_config.source,
                    dependencies=slash_config.dependencies,
                    examples=slash_config.examples,
                    config=slash_config.config
                )

                # 注册到 registry
                self.slash_registry.register(metadata)
                logger.debug(f"Registered custom slash command: /{name} "
                           f"(type={slash_config.type}, source={slash_config.source})")

            except Exception as e:
                logger.error(f"Failed to register custom slash command '{name}': {e}")

    # ================== 并行执行辅助方法 ==================

    def _split_parallel_tasks(
        self,
        request: str,
        intent: Intent,
        verbose: bool = False
    ) -> List[str]:
        """
        将用户请求拆分为并行子任务

        策略：
        1. 批量文件处理：识别文件模式（如 "所有Python文件"）
        2. 多模块开发：识别模块列表（如 "用户管理、商品管理、订单处理"）
        3. 列表任务：识别逗号/顿号分隔的任务列表

        Args:
            request: 用户请求
            intent: 意图对象
            verbose: 详细输出

        Returns:
            子任务列表（如果无法拆分，返回空列表）
        """
        import re

        # 策略1: 检测"包含"模式（优先级最高，避免被逗号拆分误匹配）
        # 例如："开发系统，包含用户管理、商品管理、订单处理"
        if '包含' in request or 'include' in request.lower():
            pattern = r'包含(.+)'
            match = re.search(pattern, request)

            if match:
                items_part = match.group(1).strip()
                # 分割并清理空项
                items = re.split(r'[、，和]', items_part)
                items = [item.strip() for item in items if item.strip() and len(item.strip()) > 1]

                if len(items) >= 2:
                    # 提取主任务前缀（去除尾部逗号）
                    prefix_match = re.search(r'^(.+?)[，,]?\s*包含', request)
                    prefix = prefix_match.group(1).strip() if prefix_match else "实现"

                    subtasks = [f"{prefix} - {item}" for item in items]

                    if verbose:
                        print(f"[任务拆分] 检测到'包含'模式")
                        print(f"  主任务: {prefix}")
                        print(f"  子模块: {items}")
                        print()

                    return subtasks

        # 策略2: 检测逗号/顿号分隔的任务列表
        # 例如："实现用户管理、商品管理、订单处理"
        if '、' in request or '，' in request:
            # 提取任务前缀和列表部分
            # 匹配模式：<动词><列表项>、<列表项>、...
            pattern = r'(实现|开发|测试|分析|处理|审查|优化)(.+?)(、|，)(.+)'
            match = re.search(pattern, request)

            if match:
                verb = match.group(1)  # 动词：实现、开发等
                items_part = match.group(2) + match.group(3) + match.group(4)

                # 分割列表项
                items = re.split(r'[、，]', items_part)
                items = [item.strip() for item in items if item.strip()]

                if len(items) >= 2:
                    # 为每个项构造子任务
                    subtasks = [f"{verb}{item}" for item in items]

                    if verbose:
                        print(f"[任务拆分] 检测到列表分隔模式")
                        print(f"  动词: {verb}")
                        print(f"  列表项: {items}")
                        print()

                    return subtasks

        # 策略3: 批量文件处理
        # 例如："批量处理所有Python文件"
        batch_patterns = [
            (r'批量处理(.+?)(文件|模块|组件)', '处理'),
            (r'对(.+?)(文件|模块|组件)进行(.+)', lambda m: m.group(3)),
            (r'(所有|每个)(.+?)(文件|模块|组件)(.+)', lambda m: m.group(4))
        ]

        for pattern, action in batch_patterns:
            match = re.search(pattern, request)
            if match:
                # 这种情况下，需要实际扫描文件系统来拆分任务
                # 简化实现：返回空列表，由调用者决定是否使用通配符
                if verbose:
                    print(f"[任务拆分] 检测到批量文件模式，但需要文件系统支持")
                    print(f"  提示: 考虑使用 Glob 工具先列出文件")
                    print()
                return []

        # 无法拆分
        if verbose:
            print(f"[任务拆分] 无法识别可拆分的模式，将串行执行")
            print()

        return []

    def _batch_result_to_task_result(
        self,
        batch_result: 'BatchResult',
        original_request: str,
        intent: Intent
    ) -> TaskResult:
        """
        将批处理结果转换为单一 TaskResult

        Args:
            batch_result: 批处理结果
            original_request: 原始请求
            intent: 意图对象

        Returns:
            TaskResult 对象
        """
        # 汇总所有子任务的输出
        outputs = []
        for i, task_result in enumerate(batch_result.task_results, 1):
            if task_result.success:
                outputs.append(f"=== 子任务 {i}/{batch_result.total_tasks} ===")
                outputs.append(f"资源: {task_result.namespace}")
                outputs.append(f"输出:\n{task_result.output}")
                outputs.append("")
            else:
                outputs.append(f"=== 子任务 {i}/{batch_result.total_tasks} [失败] ===")
                outputs.append(f"资源: {task_result.namespace}")
                outputs.append(f"错误: {task_result.error}")
                outputs.append("")

        combined_output = "\n".join(outputs)

        # 添加总结
        summary = f"""
{'='*70}
批处理总结
{'='*70}
总任务数: {batch_result.total_tasks}
成功: {batch_result.successful}
失败: {batch_result.failed}
总耗时: {batch_result.total_duration_seconds:.2f}s
{'='*70}
"""

        final_output = combined_output + summary

        # 构造 TaskResult
        backend = self._select_backend_for_intent(intent)

        return TaskResult(
            backend=backend,
            prompt=original_request,
            output=final_output,
            success=(batch_result.failed == 0),
            error=None if batch_result.failed == 0 else f"{batch_result.failed} 个子任务失败",
            run_id=None,
            event_stream=None,
            duration_seconds=batch_result.total_duration_seconds
        )

    # ================== 系统级 Slash Command Handlers ==================

    def _auto_discover(self, verbose: bool = False) -> Dict[str, Any]:
        """
        /discover 命令：重新发现并注册资源

        Returns:
            发现统计信息
        """
        if not V3_AVAILABLE or not self.registry:
            raise RuntimeError("Auto-discovery requires V3 (auto_discover=True)")

        # 重新加载配置并注册资源
        self.reload_config(verbose=verbose)

        # 返回统计
        stats = self.registry.get_stats()

        if verbose:
            print(f"\n[自动发现完成]")
            print(f"  总资源: {stats['total_resources']}")
            print(f"  按类型: {stats['by_type']}")
            print(f"  按来源: {stats['by_source']}")

        return stats

    def _list_skills(self, verbose: bool = False) -> List['ResourceMetadata']:
        """
        /list-skills 命令：列出所有 skills

        Returns:
            Skill列表
        """
        if not V3_AVAILABLE or not self.registry:
            raise RuntimeError("list-skills requires V3 (auto_discover=True)")

        from .core.unified_registry import ResourceType
        skills = self.registry.list_resources(type_filter=ResourceType.SKILL)

        if verbose:
            print(f"\n[已注册 Skills ({len(skills)}个)]")
            for skill in skills:
                print(f"  - {skill.namespace} (来源:{skill.source}, 优先级:{skill.priority})")

        return skills

    def _list_slash_commands(self, verbose: bool = False) -> List:
        """
        /list-commands 命令：列出所有 Slash Commands

        Returns:
            Slash Command列表
        """
        if not self.slash_registry:
            raise RuntimeError("Slash commands not available (auto_discover=True required)")

        commands = self.slash_registry.list_commands()

        if verbose:
            print(f"\n[已注册 Slash Commands ({len(commands)}个)]")
            for cmd in commands:
                print(f"  - /{cmd.name} ({cmd.type.value}): {cmd.description}")

        return commands

    def _reload_config(self, verbose: bool = False) -> Dict[str, Any]:
        """
        /reload 命令：重新加载配置

        Returns:
            重载结果
        """
        # 调用现有的 reload_config 方法
        self.reload_config(verbose=verbose)

        # 重新注册 Slash Commands
        if self.slash_registry:
            self.slash_registry.clear()
            register_builtin_commands(self.slash_registry)
            self._register_custom_slash_commands()  # 重新注册自定义命令

        stats = {
            "reloaded": True,
            "resources": len(self.registry) if self.registry else 0,
            "slash_commands": len(self.slash_registry) if self.slash_registry else 0
        }

        if verbose:
            print(f"\n[配置重载完成]")
            print(f"  资源数: {stats['resources']}")
            print(f"  Slash Commands: {stats['slash_commands']}")

        return stats

    def _get_stats(self, verbose: bool = False) -> Dict[str, Any]:
        """
        /stats 命令：获取统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "v3_enabled": V3_AVAILABLE and self.auto_discover,
            "parallel_enabled": self.enable_parallel,
        }

        if self.registry:
            stats["registry"] = self.registry.get_stats()

        if self.slash_registry:
            stats["slash_commands"] = self.slash_registry.get_stats()

        if self.scheduler:
            stats["scheduler"] = self.scheduler.get_stats()

        if verbose:
            print(f"\n[系统统计]")
            print(f"  V3启用: {stats['v3_enabled']}")
            print(f"  并行启用: {stats['parallel_enabled']}")

            if "registry" in stats:
                print(f"\n[资源注册表]")
                for key, value in stats["registry"].items():
                    print(f"  {key}: {value}")

            if "slash_commands" in stats:
                print(f"\n[Slash Commands]")
                for key, value in stats["slash_commands"].items():
                    print(f"  {key}: {value}")

        return stats

    def _clear_registry_cache(self, verbose: bool = False) -> Dict[str, Any]:
        """
        /clear-cache 命令：清除注册表缓存

        清除 RegistryPersistence 的缓存文件，强制下次启动时重新扫描资源。

        Returns:
            清除结果字典
        """
        result = {
            "success": False,
            "message": "",
            "cleared_files": []
        }

        try:
            # 检查 V3 和 auto_discover 是否启用
            if not V3_AVAILABLE or not self.auto_discover:
                result["message"] = "Registry cache not available (requires auto_discover=True)"
                if verbose:
                    print(f"\n[清除缓存失败]")
                    print(f"  {result['message']}")
                return result

            # 获取 ConfigLoader 中的 persistence 实例
            # 注意：ConfigLoader 在初始化时创建，我们需要访问它
            from .core.registry_persistence import RegistryPersistence
            from pathlib import Path

            registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
            persistence = RegistryPersistence(registry_dir=registry_dir)

            # 获取清除前的统计信息
            stats_before = persistence.get_stats()

            if verbose:
                print(f"\n[清除前状态]")
                if stats_before.get("status") == "cached":
                    print(f"  缓存状态: 有效")
                    print(f"  上次扫描: {stats_before.get('last_scan')}")
                    print(f"  资源总数: {stats_before.get('total_resources')}")
                    print(f"  文件数: {stats_before.get('file_count')}")
                else:
                    print(f"  缓存状态: {stats_before.get('status')}")

            # 清除缓存
            persistence.invalidate()

            # 验证清除结果
            stats_after = persistence.get_stats()

            result["success"] = True
            result["message"] = "Registry cache cleared successfully"
            result["stats_before"] = stats_before
            result["stats_after"] = stats_after

            if verbose:
                print(f"\n[清除成功]")
                print(f"  缓存已清除，下次启动将重新扫描资源")
                print(f"\n[清除后状态]")
                print(f"  缓存状态: {stats_after.get('status')}")

        except Exception as e:
            result["success"] = False
            result["message"] = f"Failed to clear cache: {e}"

            if verbose:
                print(f"\n[清除失败]")
                print(f"  错误: {e}")
                import traceback
                traceback.print_exc()

        return result


def main():
    """CLI 入口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="MasterOrchestrator - 智能AI任务协调器")
    parser.add_argument("request", help="用户请求")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 环境变量
    use_remote = False
    enable_cache = False
    enable_upload = False
    aduib_url = os.environ.get("ADUIB_URL")
    aduib_api_key = os.environ.get("ADUIB_API_KEY")
    if aduib_url.strip() and aduib_api_key.strip():
        use_remote = True
        enable_cache = True
        enable_upload = True
    timeout = int(os.environ.get("ORCHESTRATOR_TIMEOUT", "300"))

    # 创建协调器
    orch = MasterOrchestrator(
        timeout=timeout,
        use_remote=use_remote,
        aduib_url=aduib_url,
        aduib_api_key=aduib_api_key,
        enable_cache=enable_cache,
        enable_upload=enable_upload
    )

    # 处理请求
    print(f"[MasterOrchestrator] 处理请求: {args.request}\n")

    try:
        result = orch.process(args.request, verbose=args.verbose)

        # 输出结果
        if isinstance(result, WorkflowResult):
            # 工作流结果
            print(f"\n[工作流执行完成]")
            print(f"成功: {result.success}")
            print(f"完成阶段: {result.completed_stages}/5")
            print(f"总耗时: {result.total_duration_seconds:.2f}s")

            if not result.success:
                print(f"失败阶段: {result.failed_stage.value if result.failed_stage else 'N/A'}")

            print(f"\n阶段详情:")
            for i, stage_result in enumerate(result.stages, 1):
                status = "[OK]" if stage_result.success else "[FAIL]"
                print(f"  {status} 阶段 {i}: {stage_result.stage.value} ({stage_result.duration_seconds:.2f}s)")
                if not stage_result.success and stage_result.error:
                    print(f"       错误: {stage_result.error}")

        elif isinstance(result, TaskResult):
            # 单次任务结果
            print(f"\n[执行完成]")
            print(f"后端: {result.backend}")
            print(f"成功: {result.success}")
            print(f"耗时: {result.duration_seconds}s")

            if result.run_id:
                print(f"Run ID: {result.run_id}")

            if result.success:
                output = result.get_final_output()
                print(f"\n输出预览:")
                print(output[:500] + "..." if len(output) > 500 else output)

                if result.event_stream:
                    tool_chain = result.get_tool_chain()
                    print(f"\n工具调用链: {tool_chain[:5]}")
            else:
                print(f"错误: {result.error}")
        else:
            # 其他类型结果（CommandResult, AgentResult等）
            print(f"\n[执行完成]")
            if hasattr(result, 'success'):
                print(f"成功: {result.success}")
            if hasattr(result, 'output'):
                print(f"\n输出:")
                print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
            if hasattr(result, 'error') and result.error:
                print(f"错误: {result.error}")

        return 0

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
