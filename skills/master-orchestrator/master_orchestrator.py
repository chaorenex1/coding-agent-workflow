#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import io
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Windows 终端 UTF-8 支持
if sys.platform == 'win32':
    # 设置环境变量强制 UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 重新配置 stdout/stderr 为 UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 修复直接运行时的导入路径问题
_RUNNING_AS_SCRIPT = __name__ == "__main__" and __package__ is None

if _RUNNING_AS_SCRIPT:
    # 添加当前目录到sys.path以支持绝对导入
    _current_dir = str(Path(__file__).parent)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)

# 配置logger
logger = logging.getLogger(__name__)

# 根据运行模式选择导入方式
if _RUNNING_AS_SCRIPT:
    # 直接运行脚本时使用绝对导入
    from core.event_parser import EventStream
    from core.backend_orchestrator import BackendOrchestrator, TaskResult
    from core.log_manager import LogManager
    from core.temp_file_manager import TempFileManager

    # V3 新增：配置和注册系统
    try:
        from core.config_loader import ConfigLoader, OrchestratorConfig
        from core.unified_registry import UnifiedRegistry, ResourceMetadata, create_registry_from_config, ResourceType
        from core.executor_factory import ExecutorFactory
        from core.dependency_analyzer import DependencyAnalyzer, Task, ParallelGroup
        from core.parallel_scheduler import ParallelScheduler, TaskResult as SchedulerTaskResult, BatchResult
        from core.slash_command_registry import SlashCommandRegistry, register_builtin_commands
        from core.slash_command import SlashCommandResult, SlashCommandMetadata, SlashCommandType
        from core.registry_persistence import RegistryPersistence
    except ImportError as e:
        ConfigLoader = None
        UnifiedRegistry = None
        ResourceType = None
        ExecutorFactory = None
        DependencyAnalyzer = None
        ParallelScheduler = None
        SlashCommandRegistry = None
        SlashCommandResult = None
        SlashCommandMetadata = None
        SlashCommandType = None
        RegistryPersistence = None

    # 导入执行器
    from executors.command_executor import CommandExecutor, CommandResult
    from executors.prompt_manager import PromptManager
    from executors.agent_caller import AgentCaller, AgentRequest, AgentResult, AgentType

    # 导入意图分析器
    try:
        from analyzers.claude_intent_analyzer import Intent, ExecutionMode, ClaudeIntentAnalyzer
        INTENT_WITH_CANDIDATES = True
        CLAUDE_ANALYZER_AVAILABLE = True
    except ImportError:
        INTENT_WITH_CANDIDATES = False
        ClaudeIntentAnalyzer = None
        CLAUDE_ANALYZER_AVAILABLE = False
else:
    # 作为模块导入时使用相对导入
    from .core.event_parser import EventStream
    from .core.backend_orchestrator import BackendOrchestrator, TaskResult
    from .core.log_manager import LogManager
    from .core.temp_file_manager import TempFileManager

    # V3 新增：配置和注册系统
    try:
        from .core.config_loader import ConfigLoader, OrchestratorConfig
        from .core.unified_registry import UnifiedRegistry, ResourceMetadata, create_registry_from_config, ResourceType
        from .core.executor_factory import ExecutorFactory
        from .core.dependency_analyzer import DependencyAnalyzer, Task, ParallelGroup
        from .core.parallel_scheduler import ParallelScheduler, TaskResult as SchedulerTaskResult, BatchResult
        from .core.slash_command_registry import SlashCommandRegistry, register_builtin_commands
        from .core.slash_command import SlashCommandResult, SlashCommandMetadata, SlashCommandType
        from .core.registry_persistence import RegistryPersistence
    except ImportError as e:
        ConfigLoader = None
        UnifiedRegistry = None
        ResourceType = None
        ExecutorFactory = None
        DependencyAnalyzer = None
        ParallelScheduler = None
        SlashCommandRegistry = None
        SlashCommandResult = None
        SlashCommandMetadata = None
        SlashCommandType = None
        RegistryPersistence = None

    # 导入执行器
    from .executors.command_executor import CommandExecutor, CommandResult
    from .executors.prompt_manager import PromptManager
    from .executors.agent_caller import AgentCaller, AgentRequest, AgentResult, AgentType

    # Phase 1: 导入扩展的 Intent 和 ExecutionMode
    try:
        from .analyzers.claude_intent_analyzer import Intent, ExecutionMode, ClaudeIntentAnalyzer
        INTENT_WITH_CANDIDATES = True
        CLAUDE_ANALYZER_AVAILABLE = True
    except ImportError:
        # Fallback：使用本地定义（向后兼容）
        INTENT_WITH_CANDIDATES = False
        ClaudeIntentAnalyzer = None
        CLAUDE_ANALYZER_AVAILABLE = False

# Fallback 定义（当上面的导入失败时使用）
if not INTENT_WITH_CANDIDATES:
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

        # 判断是否使用流式输出
        stream_output = hasattr(self, 'stream_handler') and self.stream_handler is not None
        output_callback = self.stream_handler.process_line if stream_output else None
        stream_format = getattr(self, 'stream_format', 'text')

        # 渲染模板
        if template_name:
            result = self.prompt_manager.render(template_name, **variables)
            if result.success:
                # 使用渲染后的提示词调用后端
                backend = self._select_backend(intent)
                return self.backend_orch.run_task(
                    backend=backend,
                    prompt=result.rendered_prompt,
                    stream_format=stream_format,
                    stream_output=stream_output,
                    output_callback=output_callback
                )

        # 如果无法识别模板，回退到直接调用
        backend = self._select_backend(intent)
        return self.backend_orch.run_task(
            backend=backend,
            prompt=request,
            stream_format=stream_format,
            stream_output=stream_output,
            output_callback=output_callback
        )

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

            return self._execute_skill_by_namespace(
                namespace="skill:multcode-dev-workflow-agent",
                request=request,
                intent=intent
            )

        # 其他技能：使用增强提示词调用后端
        backend = self._select_backend_for_skill(intent)
        enhanced_request = self._enhance_skill_request(request, intent)

        # 判断是否使用流式输出
        stream_output = hasattr(self, 'stream_handler') and self.stream_handler is not None
        output_callback = self.stream_handler.process_line if stream_output else None
        stream_format = getattr(self, 'stream_format', 'text')

        return self.backend_orch.run_task(
            backend=backend,
            prompt=enhanced_request,
            stream_format=stream_format,
            stream_output=stream_output,
            output_callback=output_callback
        )

    def _call_backend(self, request: str, intent: Intent) -> TaskResult:
        """直接调用后端"""
        backend = intent.backend_hint or self._select_backend(intent)

        # 判断是否使用流式输出
        stream_output = hasattr(self, 'stream_handler') and self.stream_handler is not None
        output_callback = self.stream_handler.process_line if stream_output else None

        # 使用实例变量的 stream_format，默认为 "text"
        stream_format = getattr(self, 'stream_format', 'text')

        return self.backend_orch.run_task(
            backend=backend,
            prompt=request,
            stream_format=stream_format,
            stream_output=stream_output,
            output_callback=output_callback
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
        use_claude_intent: bool = True,
        intent_confidence_threshold: float = 0.7,
        fallback_to_rules: bool = True,
        # V3 新增参数
        config_path: Optional[Path] = None,
        enable_parallel: bool = False,  # 默认禁用，从配置文件读取
        max_parallel_workers: int = 3,  # 后备值
        parallel_timeout: int = 120  # 后备值
    ):
        """
        初始化总协调器

        Args:
            use_claude_intent: 是否使用Claude进行意图识别（默认True）
            intent_confidence_threshold: Claude意图识别置信度阈值
            fallback_to_rules: 低置信度或失败时是否回退到规则引擎
            config_path: V3配置文件路径（None=使用当前目录）
            enable_parallel: V3启用并行执行（后备值，配置文件优先）
            max_parallel_workers: V3最大并行工作线程数（后备值，配置文件优先）
            parallel_timeout: V3单任务超时时间（秒）（后备值，配置文件优先）
        """
        # 初始化本地缓存目录（需求1：在.memex/orchestrator下创建缓存）
        self.cache_dir = self._init_cache_directory()

        # 初始化日志管理器
        self.log_manager = LogManager(
            log_dir=self.cache_dir / "logs",
            console_output=False  # 避免重复输出到控制台
        )
        self.log_manager.setup(level="INFO")

        # 初始化临时文件管理器
        self.temp_file_manager = TempFileManager(
            temp_dir=self.cache_dir / "temp",
            ttl_seconds=3600  # 1小时过期
        )

        # V3 配置和注册系统
        self.config = None
        self.registry = None
        self.factory = None
        self.scheduler = None
        self.slash_registry = None  # V3.1: Slash Command Registry
        self.enable_parallel = enable_parallel

        try:
            # 1. 加载配置
            loader = ConfigLoader(project_root=config_path)
            self.config = loader.load()

            # 2. 从配置文件读取全局设置
            actual_timeout = self.config.global_settings.get('timeout', 300) if self.config.global_settings else 300

            self.backend_orch = BackendOrchestrator(timeout=actual_timeout)

            # 3. 初始化注册表
            self.registry = create_registry_from_config(self.config)

            # 4. 初始化执行器工厂
            self.factory = ExecutorFactory(self.backend_orch, self.registry)

            # 5. 初始化并行调度器（从配置文件读取，参数作为后备）
            # 优先级: 配置文件 > 构造函数参数
            parallel_enabled = self.config.parallel_config.enabled if self.config.parallel_config else enable_parallel
            parallel_max_workers = self.config.parallel_config.max_workers if self.config.parallel_config else max_parallel_workers
            parallel_task_timeout = self.config.parallel_config.timeout_per_task if self.config.parallel_config else parallel_timeout

            self.enable_parallel = parallel_enabled

            if parallel_enabled:
                self.scheduler = ParallelScheduler(
                    factory=self.factory,
                    max_workers=parallel_max_workers,
                    timeout_per_task=parallel_task_timeout
                )
                logger.info(f"并行调度器已启用: max_workers={parallel_max_workers}, timeout={parallel_task_timeout}s")

            # 6. 初始化 Slash Command Registry (V3.1)
            self.slash_registry = SlashCommandRegistry(orchestrator=self)
            register_builtin_commands(self.slash_registry)

            # 7. 注册自定义 Slash Commands (从配置)
            self._register_custom_slash_commands()

            # 8. 创建 ExecutionRouter（传入 registry）
            self.router = ExecutionRouter(
                backend_orch=self.backend_orch,
                registry=self.registry
            )

        except Exception as e:
            print(f"[警告] V3自动发现初始化失败: {e}")
            print("[提示] 将使用传统模式运行")
            self.config = None
            self.registry = None
            self.factory = None
            self.scheduler = None
            self.slash_registry = None
            # 创建不带 registry 的 ExecutionRouter（向后兼容）
            self.router = ExecutionRouter(self.backend_orch)

        # 意图分析器配置
        self.use_claude_intent = use_claude_intent
        self.fallback_to_rules = fallback_to_rules

        # 创建规则引擎分析器（作为备份）
        self.rule_analyzer = IntentAnalyzer()

        # 创建Claude分析器（如果启用）
        self.claude_analyzer = None
        if use_claude_intent and CLAUDE_ANALYZER_AVAILABLE:
            try:
                self.claude_analyzer = ClaudeIntentAnalyzer(
                    backend_orch=self.backend_orch,
                    confidence_threshold=intent_confidence_threshold
                )
                # 传递 registry 给 ClaudeIntentAnalyzer
                self.claude_analyzer.registry = self.registry
            except Exception as e:
                print(f"[警告] 无法初始化Claude意图分析器: {e}")
                print("[提示] 将使用规则引擎作为fallback")
                self.use_claude_intent = False
        elif use_claude_intent and not CLAUDE_ANALYZER_AVAILABLE:
            print("[警告] ClaudeIntentAnalyzer 不可用")
            print("[提示] 将使用规则引擎作为fallback")
            self.use_claude_intent = False

        # 向后兼容：默认使用规则引擎
        self.analyzer = self.rule_analyzer

        # 注意：self.router 已在上面的 try-except 块中初始化完成
        # 不应在此处重置为 None，否则会导致 AttributeError

    def process(
        self,
        request: str,
        verbose: bool = False,
        dry_run: bool = False,
        stream_output: bool = True,
        stream_format: str = "text"
    ) -> Any:
        """
        处理用户请求（支持 Slash Command 和自然语言）

        Args:
            request: 用户请求文本（可以是 /command 或自然语言）
            verbose: 是否输出详细信息
            dry_run: 仅显示意图分析和执行计划，不实际执行
            stream_output: 启用实时流式输出（默认：True）
            stream_format: 流式输出格式 - "text" 或 "jsonl"（默认："text"）

        Returns:
            执行结果（dry_run 时返回意图分析结果字典）
        """
        import sys
        print(f"[DEBUG] process() 开始: request={request[:50]}, dry_run={dry_run}", file=sys.stderr)

        # 0. 记录任务开始
        print(f"[DEBUG] 记录任务开始", file=sys.stderr)
        self.log_manager.log_task_start(request, "unknown")

        # 1. 检查是否为 Slash Command（V3.1）
        print(f"[DEBUG] 检查 Slash Command", file=sys.stderr)
        if request.strip().startswith('/'):
            return self._process_slash_command(request.strip(), verbose)

        # 2. 意图分析（优先使用Claude，失败则fallback到规则引擎）
        print(f"[DEBUG] 开始意图分析", file=sys.stderr)
        intent = self._analyze_intent(request, verbose)
        print(f"[DEBUG] 意图分析完成: mode={intent.mode.value}", file=sys.stderr)

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

        # Dry-run 模式：仅显示执行计划，不实际执行
        if dry_run:
            backend = self._select_backend_for_intent(intent)
            sanitized_prompt = self.backend_orch._sanitize_prompt(request)

            print("[Dry-Run 模式] 执行计划预览")
            print("=" * 60)
            print(f"  原始请求: {request[:100]}{'...' if len(request) > 100 else ''}")
            print(f"  处理后请求: {sanitized_prompt[:100]}{'...' if len(sanitized_prompt) > 100 else ''}")
            print(f"  选择后端: {backend}")
            print(f"  执行模式: {intent.mode.value}")
            print(f"  任务类型: {intent.task_type}")
            print(f"  复杂度: {intent.complexity}")
            print(f"  置信度: {intent.confidence:.2f}")
            if intent.backend_hint:
                print(f"  后端提示: {intent.backend_hint}")
            if intent.skill_hint:
                print(f"  技能提示: {intent.skill_hint}")
            if hasattr(intent, 'enable_parallel') and intent.enable_parallel:
                print(f"  并行执行: 是")
            print(f"  超时时间: {self.backend_orch.timeout}s")
            if self.config:
                # 显示通过 git 检测到的项目根目录
                from core.config_loader import find_git_root
                git_root = find_git_root()
                if git_root:
                    print(f"  项目根目录: {git_root} (via git)")
            print("=" * 60)
            print("\n[Dry-Run] 未执行任何实际操作")

            # 返回干运行结果字典
            return {
                "dry_run": True,
                "request": request,
                "sanitized_prompt": sanitized_prompt,
                "intent": {
                    "mode": intent.mode.value,
                    "task_type": intent.task_type,
                    "complexity": intent.complexity,
                    "confidence": intent.confidence,
                    "backend_hint": intent.backend_hint,
                    "skill_hint": intent.skill_hint,
                    "enable_parallel": getattr(intent, 'enable_parallel', False)
                },
                "backend": backend,
                "timeout": self.backend_orch.timeout
            }

        # 2. 并行执行判断（如果推断为并行且启用了并行调度器）
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
                    print(f"  提示: 初始化时设置 enable_parallel=True")
                    print()

        # 3.5 设置流式输出（如果启用）
        self.stream_format = stream_format  # 保存格式设置供路由器使用
        if stream_output:
            # 导入 StreamHandler
            try:
                from core.stream_handler import StreamHandler
            except ImportError:
                from .core.stream_handler import StreamHandler

            # text 格式：原始输出，不格式化；jsonl 格式：格式化输出
            format_output = (stream_format == "jsonl")
            self.stream_handler = StreamHandler(
                format_output=format_output,
                show_progress=True
            )
        else:
            self.stream_handler = None

        # 3. 本地执行（串行）
        result = self.router.route(intent, request)

        # 4. 记录任务完成
        backend = self._select_backend_for_intent(intent)
        self.log_manager.log_task_complete(
            mode=intent.mode.value,
            backend=backend,
            duration=getattr(result, 'duration_seconds', 0.0),
            success=getattr(result, 'success', True)
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

        # 转换type_filter字符串为ResourceType
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

        try:
            # 重新加载配置
            loader = ConfigLoader(project_root=None)
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
                error="Slash Command system not available"
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
        # 纯流式架构：不汇总子任务输出，仅生成统计摘要
        # 所有子任务输出已通过流式实时显示

        # 生成简短统计摘要（不包含详细输出）
        summary = f"""
{'='*70}
[批处理完成]
{'='*70}
总任务: {batch_result.total_tasks} | 成功: {batch_result.successful} | 失败: {batch_result.failed}
总耗时: {batch_result.total_duration_seconds:.2f}s
{'='*70}
"""

        final_output = summary  # 纯流式：无子任务输出缓冲

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
            raise RuntimeError("Slash commands not available")

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
            "v3_enabled": self.auto_discover,
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

            # 获取 ConfigLoader 中的 persistence 实例
            # 注意：ConfigLoader 在初始化时创建，我们需要访问它
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
    import sys

    print("[DEBUG] main() 开始", file=sys.stderr)

    parser = argparse.ArgumentParser(description="MasterOrchestrator - 智能AI任务协调器")
    parser.add_argument("request", help="用户请求")
    parser.add_argument("--verbose", "-v", action="store_true", help="启用详细输出")
    parser.add_argument("--dry-run", "-n", action="store_true", help="仅显示意图分析和执行计划，不实际执行")
    parser.add_argument("--no-stream", action="store_true", help="禁用实时流式输出（默认启用）")
    parser.add_argument("--stream-format", choices=["text", "jsonl"], default="text",
                        help="流式输出格式：text=原始输出，jsonl=格式化输出（默认：text）")

    args = parser.parse_args()
    print("[DEBUG] 参数解析完成", file=sys.stderr)

    # 创建协调器
    print("[DEBUG] 开始创建 MasterOrchestrator", file=sys.stderr)
    orch = MasterOrchestrator()
    print("[DEBUG] MasterOrchestrator 创建完成", file=sys.stderr)

    # 处理请求
    stream_enabled = not args.no_stream
    if args.no_stream:
        print(f"[MasterOrchestrator] 处理请求: {args.request}\n")

    try:
        result = orch.process(
            args.request,
            verbose=args.verbose,
            dry_run=args.dry_run,
            stream_output=stream_enabled,
            stream_format=args.stream_format
        )

        # Dry-run 模式直接返回
        if args.dry_run:
            return

        # 纯流式架构：输出已实时显示，仅显示简短状态行
        print(f"\n{'='*70}")

        if isinstance(result, TaskResult):
            # 使用 TaskResult 的 get_summary_line() 方法
            print(result.get_summary_line())
        else:
            # 其他类型结果的简短摘要
            if hasattr(result, 'success'):
                status = "完成" if result.success else "失败"
                print(f"[{status}]", end="")
                if hasattr(result, 'duration_seconds'):
                    print(f" | 耗时: {result.duration_seconds:.2f}s", end="")
                if hasattr(result, 'error') and result.error:
                    print(f" | 错误: {result.error[:100]}")
                else:
                    print()
            else:
                print("[执行完成]")

        print('='*70)

        return 0

    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
