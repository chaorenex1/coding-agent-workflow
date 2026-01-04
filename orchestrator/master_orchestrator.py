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
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 导入核心模块（现在使用orchestrator内部结构）
from .core.event_parser import EventStream
from .core.backend_orchestrator import BackendOrchestrator, TaskResult

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

        return Intent(
            mode=mode,
            task_type=task_type,
            complexity=complexity,
            backend_hint=backend_hint,
            skill_hint=skill_hint,
            confidence=0.8
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


class ExecutionRouter:
    """
    执行路由器 - 根据意图选择执行路径

    路由逻辑：
    - command → CommandExecutor
    - agent → AgentCaller
    - prompt → PromptManager
    - skill → SkillExecutor
    - backend → BackendOrchestrator
    """

    def __init__(self, backend_orch: BackendOrchestrator):
        """
        初始化路由器

        Args:
            backend_orch: BackendOrchestrator实例
        """
        self.backend_orch = backend_orch

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
        parse_events: bool = True,
        timeout: int = 300,
        use_remote: Optional[bool] = None,
        aduib_url: Optional[str] = None,
        aduib_api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_upload: bool = True,
        use_claude_intent: bool = True,
        intent_confidence_threshold: float = 0.7,
        fallback_to_rules: bool = True
    ):
        """
        初始化总协调器

        Args:
            parse_events: 是否解析事件流
            timeout: 超时时间（秒）
            use_remote: 是否使用远程服务（None=自动检测）
            aduib_url: aduib-ai 服务地址
            aduib_api_key: aduib-ai API 密钥
            enable_cache: 是否启用缓存查询
            enable_upload: 是否启用结果上传
            use_claude_intent: 是否使用Claude进行意图识别（默认True）
            intent_confidence_threshold: Claude意图识别置信度阈值
            fallback_to_rules: 低置信度或失败时是否回退到规则引擎
        """
        # 本地组件（必需）
        self.backend_orch = BackendOrchestrator(
            parse_events=parse_events,
            timeout=timeout
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

        self.router = ExecutionRouter(self.backend_orch)

        # 远程组件（可选）
        self.aduib_client = None
        self.enable_cache = enable_cache
        self.enable_upload = enable_upload

        # 自动检测或手动配置 aduib-ai
        if use_remote is None:
            # 自动检测：如果设置了 ADUIB_API_KEY，则启用
            use_remote = bool(os.getenv("ADUIB_API_KEY"))

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

    def process(self, request: str, verbose: bool = False) -> Any:
        """
        处理用户请求

        Args:
            request: 用户请求文本
            verbose: 是否输出详细信息

        Returns:
            执行结果
        """
        # 1. 意图分析（优先使用Claude，失败则fallback到规则引擎）
        intent = self._analyze_intent(request, verbose)

        if verbose:
            print(f"[意图分析]")
            print(f"  模式: {intent.mode.value}")
            print(f"  类型: {intent.task_type}")
            print(f"  复杂度: {intent.complexity}")
            if intent.backend_hint:
                print(f"  后端提示: {intent.backend_hint}")
            if intent.skill_hint:
                print(f"  技能提示: {intent.skill_hint}")
            print()

        # 2. 查询远程缓存（如果启用）
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

        # 3. 本地执行
        if verbose and self.aduib_client and self.enable_cache:
            print(f"[缓存未命中] 本地执行任务")
            print()

        result = self.router.route(intent, request)

        # 4. 上传结果到远程（如果启用且成功）
        if self.aduib_client and self.enable_upload and self._should_upload(result):
            backend = self._select_backend_for_intent(intent)
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


def main():
    """CLI 入口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="MasterOrchestrator - 智能AI任务协调器")
    parser.add_argument("request", help="用户请求")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--parse-events", action="store_true", default=True, help="解析事件流")
    parser.add_argument("--timeout", type=int, default=300, help="超时时间（秒）")

    # aduib-ai 远程服务参数
    parser.add_argument("--use-remote", action="store_true", help="启用远程服务（默认自动检测）")
    parser.add_argument("--no-remote", action="store_true", help="禁用远程服务")
    parser.add_argument("--aduib-url", help="aduib-ai 服务地址（默认: ADUIB_URL 环境变量）")
    parser.add_argument("--aduib-api-key", help="aduib-ai API 密钥（默认: ADUIB_API_KEY 环境变量）")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存查询")
    parser.add_argument("--no-upload", action="store_true", help="禁用结果上传")

    args = parser.parse_args()

    # 确定是否使用远程服务
    use_remote = None
    if args.use_remote:
        use_remote = True
    elif args.no_remote:
        use_remote = False

    # 创建协调器
    orch = MasterOrchestrator(
        parse_events=args.parse_events,
        timeout=args.timeout,
        use_remote=use_remote,
        aduib_url=args.aduib_url,
        aduib_api_key=args.aduib_api_key,
        enable_cache=not args.no_cache,
        enable_upload=not args.no_upload
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
