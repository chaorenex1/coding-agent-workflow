"""
Executor factory for dynamic executor creation.

Creates and caches executor instances based on resource metadata from UnifiedRegistry.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any
import logging
import yaml

# Add parent directory to path
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from core.backend_orchestrator import BackendOrchestrator, TaskResult
from core.unified_registry import UnifiedRegistry, ResourceMetadata, ResourceType
from executors.memex_executor_base import MemexExecutorBase, MemexSkillExecutor


logger = logging.getLogger(__name__)


class YAMLSkillExecutor(MemexSkillExecutor):
    """
    Executor for YAML-based skills.

    Loads skill configuration from YAML file and executes via memex-cli.
    """

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        skill_path: Path,
        skill_name: str,
        **config
    ):
        """
        Initialize YAML skill executor.

        Args:
            backend_orch: BackendOrchestrator instance
            skill_path: Path to skill YAML file
            skill_name: Skill name
            **config: Additional configuration
        """
        super().__init__(backend_orch, skill_name, config.get('backend', 'claude'))
        self.skill_path = skill_path
        self.skill_config = self._load_skill_config()

    def _load_skill_config(self) -> Dict[str, Any]:
        """Load skill configuration from YAML file."""
        try:
            with open(self.skill_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded skill config from {self.skill_path}")
                return config or {}
        except Exception as e:
            logger.error(f"Failed to load skill config from {self.skill_path}: {e}")
            return {}

    def _build_skill_prompt(self, request: str, **params) -> str:
        """
        Build skill prompt from YAML configuration.

        Args:
            request: User request
            **params: Skill parameters

        Returns:
            Constructed prompt string
        """
        # Get system prompt and user prompt template from config
        system_prompt = self.skill_config.get('system_prompt', '')
        user_prompt_template = self.skill_config.get('user_prompt_template', '{request}')

        # Replace variables in template
        try:
            # Support both {{var}} and {var} syntax
            user_prompt = user_prompt_template.replace('{{request}}', request).replace('{request}', request)

            # Replace other parameters
            for key, value in params.items():
                user_prompt = user_prompt.replace(f'{{{{{key}}}}}', str(value))
                user_prompt = user_prompt.replace(f'{{{key}}}', str(value))

            # Combine system and user prompts
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
            else:
                full_prompt = user_prompt

            return full_prompt

        except Exception as e:
            logger.error(f"Failed to build skill prompt: {e}")
            return request

    def execute(self, request: str, backend: Optional[str] = None, **skill_params) -> TaskResult:
        """
        Execute YAML skill.

        Args:
            request: User request
            backend: Backend override
            **skill_params: Skill parameters

        Returns:
            TaskResult
        """
        # Build prompt from YAML configuration
        prompt = self._build_skill_prompt(request, **skill_params)

        # Execute via memex
        backend = backend or self.skill_config.get('backend', self.default_backend)

        return self.execute_via_memex(
            prompt=prompt,
            backend=backend
        )


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
        skill_type = metadata.config.get('type', 'yaml')

        if skill_type == 'yaml':
            # YAML-based skill
            if not metadata.path or not metadata.path.exists():
                logger.error(f"Skill path not found: {metadata.path}")
                return None

            return YAMLSkillExecutor(
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
