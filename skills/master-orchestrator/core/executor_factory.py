"""
Executor factory for dynamic executor creation.

Creates and caches executor instances based on resource metadata from UnifiedRegistry.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional, Any
import logging
import yaml

# Add parent directory to path
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from core.backend_orchestrator import BackendOrchestrator, TaskResult
from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType
from core.resource_content_parser import get_parser, MarkdownResourceParser, ParsedResourceContent
from executors.memex_executor_base import MemexExecutorBase, MemexSkillExecutor


logger = logging.getLogger(__name__)


class MarkdownSkillExecutor(MemexSkillExecutor):
    """
    Markdown Skill 执行器

    支持 SKILL.md 格式的资源：
    - 元数据：description, enabled, priority, backend, tags
    - 章节：System Prompt, User Prompt Template

    执行时将资源内容作为提示词，结合用户需求发送给后端。
    """

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        skill_path: Path,
        skill_name: str,
        **config
    ):
        """
        初始化 Markdown Skill 执行器

        Args:
            backend_orch: BackendOrchestrator 实例
            skill_path: SKILL.md 文件路径（或包含 SKILL.md 的目录）
            skill_name: Skill 名称
            **config: 额外配置
        """
        super().__init__(backend_orch, skill_name, config.get('backend', 'claude'))

        # 处理路径：如果是目录，查找 SKILL.md
        if skill_path.is_dir():
            marker_file = skill_path / "SKILL.md"
            if not marker_file.exists():
                raise FileNotFoundError(f"未找到 SKILL.md: {marker_file}")
            self.skill_file = marker_file
        else:
            self.skill_file = skill_path

        # 解析资源内容
        self.parsed_content = self._parse_skill_content()

        logger.debug(f"初始化 MarkdownSkillExecutor: {skill_name}, 文件: {self.skill_file}")

    def _parse_skill_content(self) -> ParsedResourceContent:
        """解析 SKILL.md 文件内容"""
        try:
            parser = MarkdownResourceParser()
            parsed = parser.parse(self.skill_file)

            logger.debug(
                f"解析 SKILL.md 成功: {self.skill_file}\n"
                f"  - 元数据: {list(parsed.metadata.keys())}\n"
                f"  - 章节: {parsed.list_sections()}"
            )

            return parsed

        except Exception as e:
            logger.error(f"解析 SKILL.md 失败: {self.skill_file}, 错误: {e}")
            # 返回空的 ParsedResourceContent 作为降级
            return ParsedResourceContent()

    def _process_request_format(self, request: str) -> str:
        """
        处理用户需求格式

        支持：
        1. 非格式化：直接返回
        2. 格式化："需求理解：xxx" -> "xxx"
        3. Slash Command："/code_fix xxx" -> "xxx"

        Args:
            request: 原始用户需求

        Returns:
            处理后的需求
        """
        request = request.strip()

        # 处理 "需求理解：" 前缀
        if request.startswith('需求理解：'):
            return request[5:].strip()

        # 处理中文冒号
        if request.startswith('需求理解:'):
            return request[4:].strip()

        # 处理 Slash Command 格式：/command args
        if request.startswith('/'):
            parts = request[1:].split(maxsplit=1)
            if len(parts) > 1:
                return parts[1].strip()
            # 如果只有命令没有参数，返回空字符串
            return ""

        # 非格式化，直接返回
        return request

    def _build_prompt(self, request: str, **params) -> str:
        """
        构建完整提示词

        结构：
        1. System Prompt（来自 ## System Prompt 章节）
        2. User Prompt（来自 ## User Prompt Template 章节，替换变量）

        Args:
            request: 用户需求（已处理格式）
            **params: 额外参数

        Returns:
            完整提示词
        """
        # 1. 获取 System Prompt
        system_prompt = self.parsed_content.get_section('System Prompt', '')

        # 2. 获取 User Prompt Template
        user_prompt_template = self.parsed_content.get_section(
            'User Prompt Template',
            '{request}'  # 默认模板
        )

        # 3. 替换变量
        user_prompt = self._render_template(user_prompt_template, request=request, **params)

        # 4. 组合提示词
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
        else:
            full_prompt = user_prompt

        logger.debug(
            f"构建提示词完成:\n"
            f"  - System Prompt 长度: {len(system_prompt)}\n"
            f"  - User Prompt 长度: {len(user_prompt)}\n"
            f"  - 总长度: {len(full_prompt)}"
        )

        return full_prompt

    def _render_template(self, template: str, **variables) -> str:
        """
        渲染模板，替换变量

        支持：
        - {{variable}} 语法
        - {variable} 语法

        Args:
            template: 模板字符串
            **variables: 变量字典

        Returns:
            渲染后的字符串
        """
        rendered = template

        for key, value in variables.items():
            # 替换 {{key}} 和 {key}
            rendered = rendered.replace(f'{{{{{key}}}}}', str(value))
            rendered = rendered.replace(f'{{{key}}}', str(value))

        return rendered

    def execute(self, request: str, backend: Optional[str] = None, **skill_params) -> TaskResult:
        """
        执行 Skill

        流程：
        1. 处理用户需求格式
        2. 构建提示词（包装资源内容）
        3. 调用后端执行

        Args:
            request: 用户需求
            backend: 后端覆盖（可选）
            **skill_params: Skill 参数

        Returns:
            TaskResult
        """
        # 1. 处理请求格式
        processed_request = self._process_request_format(request)

        # 2. 构建提示词
        full_prompt = self._build_prompt(processed_request, **skill_params)

        # 3. 确定后端
        backend = backend or self.parsed_content.get_metadata('backend', self.default_backend)

        # 4. 执行
        logger.info(f"[MarkdownSkillExecutor] 执行 Skill: {self.skill_name}")
        logger.debug(f"[MarkdownSkillExecutor] 后端: {backend}, 提示词长度: {len(full_prompt)}")

        return self.execute_via_memex(
            prompt=full_prompt,
            backend=backend
        )


# 向后兼容别名
YAMLSkillExecutor = MarkdownSkillExecutor


class CommandExecutorAdapter(MemexExecutorBase):
    """
    Adapter for command execution via existing CommandExecutor.

    Wraps the existing CommandExecutor to provide MemexExecutorBase interface.
    """

    def __init__(self, backend_orch: BackendOrchestrator, command_name: str, **config):
        """
        Initialize command executor adapter.

        Args:
            backend_orch: BackendOrchestrator instance
            command_name: Command name
            **config: Additional configuration
        """
        super().__init__(backend_orch, default_backend="claude")
        self.command_name = command_name
        self.config = config

    def execute(self, request: str, **kwargs) -> Any:
        """
        Execute command.

        Args:
            request: User request
            **kwargs: Additional arguments

        Returns:
            Execution result
        """
        # Import here to avoid circular dependency
        from executors.command_executor import CommandExecutor

        # Create CommandExecutor instance
        executor = CommandExecutor(
            backend_orch=self.backend_orch,
            use_claude=True,
            fallback_to_rules=True
        )

        # Execute command
        return executor.execute(request, **kwargs)


class AgentExecutorAdapter(MemexExecutorBase):
    """
    Adapter for agent execution via existing AgentCaller.

    Wraps the existing AgentCaller to provide MemexExecutorBase interface.
    """

    def __init__(self, backend_orch: BackendOrchestrator, agent_type: str, **config):
        """
        Initialize agent executor adapter.

        Args:
            backend_orch: BackendOrchestrator instance
            agent_type: Agent type (explore, plan, general)
            **config: Additional configuration
        """
        super().__init__(backend_orch, default_backend="claude")
        self.agent_type = agent_type
        self.config = config

    def execute(self, request: str, **kwargs) -> Any:
        """
        Execute agent task.

        Args:
            request: User request
            **kwargs: Additional arguments

        Returns:
            Execution result
        """
        # Import here to avoid circular dependency
        from executors.agent_caller import AgentCaller, AgentType, AgentRequest

        # Create AgentCaller instance
        caller = AgentCaller(
            backend_orch=self.backend_orch,
            use_claude=True,
            fallback_to_simple=True
        )

        # Map agent type string to enum
        agent_type_map = {
            'explore': AgentType.EXPLORE,
            'plan': AgentType.PLAN,
            'general': AgentType.GENERAL_PURPOSE
        }

        agent_enum = agent_type_map.get(self.agent_type.lower(), AgentType.GENERAL_PURPOSE)

        # Create agent request
        agent_request = AgentRequest(
            agent_type=agent_enum,
            prompt=request,
            thoroughness=kwargs.get('thoroughness', 'medium'),
            model=kwargs.get('model')
        )

        # Execute agent
        return caller.call_agent(agent_request, **kwargs)


class PromptExecutorAdapter(MemexExecutorBase):
    """
    Adapter for prompt template rendering via existing PromptManager.

    Wraps the existing PromptManager to provide MemexExecutorBase interface.
    """

    def __init__(self, backend_orch: BackendOrchestrator, prompt_name: str, template: str, **config):
        """
        Initialize prompt executor adapter.

        Args:
            backend_orch: BackendOrchestrator instance
            prompt_name: Prompt template name
            template: Prompt template string
            **config: Additional configuration
        """
        super().__init__(backend_orch, default_backend="claude")
        self.prompt_name = prompt_name
        self.template = template
        self.config = config

    def execute(self, request: str, **kwargs) -> Any:
        """
        Render and execute prompt template.

        Args:
            request: User request (used as 'request' variable)
            **kwargs: Template variables

        Returns:
            Execution result
        """
        # Import here to avoid circular dependency
        from executors.prompt_manager import PromptManager

        # Create PromptManager instance
        manager = PromptManager(
            backend_orch=self.backend_orch,
            use_claude=True,
            fallback_to_local=True
        )

        # Add request to variables
        variables = {'request': request}
        variables.update(kwargs)

        # Render template
        return manager.render(self.prompt_name, **variables)


class ExecutorFactory:
    """
    Factory for creating and caching executor instances.

    Features:
    - Dynamic executor creation based on resource metadata
    - Executor instance caching
    - Support for all resource types (skill, command, agent, prompt)
    """

    def __init__(self, backend_orch: BackendOrchestrator, registry: UnifiedRegistry):
        """
        Initialize executor factory.

        Args:
            backend_orch: BackendOrchestrator instance
            registry: UnifiedRegistry instance
        """
        self.backend_orch = backend_orch
        self.registry = registry
        self._cache: Dict[str, MemexExecutorBase] = {}

        logger.debug("ExecutorFactory initialized")

    def create_executor(self, namespace: str) -> Optional[MemexExecutorBase]:
        """
        Create or retrieve cached executor for a resource.

        Args:
            namespace: Resource namespace (e.g., "skill:code-review")

        Returns:
            MemexExecutorBase instance if successful, None otherwise
        """
        # Check cache first
        if namespace in self._cache:
            logger.debug(f"Returning cached executor for {namespace}")
            return self._cache[namespace]

        # Get resource metadata from registry
        metadata = self.registry.get(namespace)
        if not metadata:
            logger.warning(f"No metadata found for namespace: {namespace}")
            return None

        # Check if resource is enabled
        if not metadata.enabled:
            logger.warning(f"Resource {namespace} is disabled")
            return None

        # Create executor based on type
        try:
            executor = self._create_by_type(metadata)

            if executor:
                # Cache the executor
                self._cache[namespace] = executor
                logger.debug(f"Created and cached executor for {namespace}")

            return executor

        except Exception as e:
            logger.error(f"Failed to create executor for {namespace}: {e}")
            return None

    def _create_by_type(self, metadata: ResourceMetadata) -> Optional[MemexExecutorBase]:
        """
        Create executor based on resource type.

        Args:
            metadata: Resource metadata

        Returns:
            MemexExecutorBase instance
        """
        if metadata.type == ResourceType.SKILL:
            return self._create_skill_executor(metadata)
        elif metadata.type == ResourceType.COMMAND:
            return self._create_command_executor(metadata)
        elif metadata.type == ResourceType.AGENT:
            return self._create_agent_executor(metadata)
        elif metadata.type == ResourceType.PROMPT:
            return self._create_prompt_executor(metadata)
        else:
            logger.error(f"Unknown resource type: {metadata.type}")
            return None

    def _create_skill_executor(self, metadata: ResourceMetadata) -> Optional[MemexExecutorBase]:
        """Create skill executor."""
        # 默认使用 Markdown 格式（V2 Scanner 的标准格式）
        skill_type = metadata.config.get('type', 'markdown')

        if skill_type in ['markdown', 'yaml']:
            # Markdown-based skill (SKILL.md 格式)
            if not metadata.path or not metadata.path.exists():
                logger.error(f"Skill path not found: {metadata.path}")
                return None

            return MarkdownSkillExecutor(
                backend_orch=self.backend_orch,
                skill_path=metadata.path,
                skill_name=metadata.name,
                **metadata.config
            )
        elif skill_type == 'python':
            # Python-based skill - dynamic import
            # TODO: Implement Python skill loading
            logger.warning(f"Python skills not yet implemented: {metadata.name}")
            return None
        else:
            logger.error(f"Unknown skill type: {skill_type}")
            return None

    def _create_command_executor(self, metadata: ResourceMetadata) -> Optional[MemexExecutorBase]:
        """Create command executor."""
        return CommandExecutorAdapter(
            backend_orch=self.backend_orch,
            command_name=metadata.name,
            **metadata.config
        )

    def _create_agent_executor(self, metadata: ResourceMetadata) -> Optional[MemexExecutorBase]:
        """Create agent executor."""
        agent_type = metadata.config.get('type', 'general')

        return AgentExecutorAdapter(
            backend_orch=self.backend_orch,
            agent_type=agent_type,
            **metadata.config
        )

    def _create_prompt_executor(self, metadata: ResourceMetadata) -> Optional[MemexExecutorBase]:
        """Create prompt executor."""
        template = metadata.config.get('template')

        if not template:
            logger.error(f"Prompt template missing for: {metadata.name}")
            return None

        return PromptExecutorAdapter(
            backend_orch=self.backend_orch,
            prompt_name=metadata.name,
            template=template,
            **metadata.config
        )

    def clear_cache(self):
        """Clear executor cache."""
        self._cache.clear()
        logger.info("Executor cache cleared")

    def get_cached_executor(self, namespace: str) -> Optional[MemexExecutorBase]:
        """
        Get cached executor without creating new one.

        Args:
            namespace: Resource namespace

        Returns:
            Cached executor or None
        """
        return self._cache.get(namespace)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            "cached_executors": len(self._cache),
            "namespaces": list(self._cache.keys())
        }

    def __repr__(self) -> str:
        return f"ExecutorFactory(cached={len(self._cache)})"
