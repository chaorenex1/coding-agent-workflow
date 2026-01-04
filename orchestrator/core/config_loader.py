"""
Configuration loader for MasterOrchestrator V3.

Implements three-tier configuration loading:
1. Builtin: Hardcoded defaults and skills/memex-cli/skills/*.yaml
2. User: ~/.claude/orchestrator.yaml and ~/.claude/skills/*.yaml
3. Project: ./orchestrator.yaml and ./skills/*.yaml

Priority: Project > User > Builtin
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource type enumeration."""
    SKILL = "skill"
    COMMAND = "command"
    AGENT = "agent"
    PROMPT = "prompt"


@dataclass
class SkillConfig:
    """Configuration for a skill resource."""
    name: str
    type: str = "yaml"  # "yaml" or "python"
    path: Optional[Path] = None
    enabled: bool = True
    priority: int = 50  # 0-1000, higher = higher priority
    source: str = "builtin"  # "builtin", "user", or "project"
    dependencies: List[str] = field(default_factory=list)
    backend: str = "claude"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandConfig:
    """Configuration for a command resource."""
    name: str
    command: Optional[str] = None  # For aliases
    enabled: bool = True
    priority: int = 50
    source: str = "builtin"
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Configuration for an agent resource."""
    name: str
    agent_type: str  # "explore", "plan", "general"
    enabled: bool = True
    priority: int = 50
    source: str = "builtin"
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptConfig:
    """Configuration for a prompt template resource."""
    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 50
    source: str = "builtin"
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelConfig:
    """Configuration for parallel execution."""
    enabled: bool = False
    max_workers: int = 3
    timeout_per_task: int = 120
    allowed_modes: List[str] = field(default_factory=lambda: ["command", "backend"])
    sequential_modes: List[str] = field(default_factory=lambda: ["skill"])


@dataclass
class OrchestratorConfig:
    """Root configuration for MasterOrchestrator."""
    version: str = "3.0"
    global_settings: Dict[str, Any] = field(default_factory=dict)
    skills: Dict[str, SkillConfig] = field(default_factory=dict)
    commands: Dict[str, CommandConfig] = field(default_factory=dict)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    prompts: Dict[str, PromptConfig] = field(default_factory=dict)
    parallel_config: ParallelConfig = field(default_factory=ParallelConfig)


class ConfigLoader:
    """
    Configuration loader with three-tier priority system.

    Loads and merges configurations from:
    1. Builtin (lowest priority)
    2. User (~/.claude/)
    3. Project (highest priority)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize ConfigLoader.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.user_config_dir = Path.home() / ".claude"

        # Determine builtin skills directory
        # From orchestrator/core/config_loader.py → orchestrator/core → orchestrator → project_root
        self.builtin_skills_dir = Path(__file__).parent.parent.parent / "skills" / "memex-cli" / "skills"

        logger.debug(f"ConfigLoader initialized:")
        logger.debug(f"  Project root: {self.project_root}")
        logger.debug(f"  User config dir: {self.user_config_dir}")
        logger.debug(f"  Builtin skills dir: {self.builtin_skills_dir}")

    def load(self) -> OrchestratorConfig:
        """
        Load and merge all configurations.

        Returns:
            Merged OrchestratorConfig with project-level taking highest priority.
        """
        logger.info("Loading orchestrator configurations...")

        # 1. Load builtin configuration
        builtin_config = self._load_builtin_config()
        logger.debug(f"Loaded builtin config: {len(builtin_config.skills)} skills, "
                    f"{len(builtin_config.commands)} commands")

        # 2. Load user-level configuration
        user_config = self._load_user_config()
        logger.debug(f"Loaded user config: {len(user_config.skills)} skills, "
                    f"{len(user_config.commands)} commands")

        # 3. Load project-level configuration
        project_config = self._load_project_config()
        logger.debug(f"Loaded project config: {len(project_config.skills)} skills, "
                    f"{len(project_config.commands)} commands")

        # 4. Merge configurations (later configs override earlier ones)
        merged_config = self._merge_configs([builtin_config, user_config, project_config])

        # 5. Validate merged configuration
        errors = self._validate_config(merged_config)
        if errors:
            logger.warning(f"Configuration validation found {len(errors)} issues:")
            for error in errors:
                logger.warning(f"  - {error}")

        logger.info(f"Configuration loaded successfully: {len(merged_config.skills)} skills, "
                   f"{len(merged_config.commands)} commands, "
                   f"{len(merged_config.agents)} agents, "
                   f"{len(merged_config.prompts)} prompts")

        return merged_config

    def _load_builtin_config(self) -> OrchestratorConfig:
        """Load builtin configuration from hardcoded defaults and builtin skills."""
        config = OrchestratorConfig(
            version="3.0",
            global_settings={
                "default_backend": "claude",
                "timeout": 300,
                "enable_parallel": False,
                "max_parallel_tasks": 3,
            }
        )

        # Load builtin YAML skills from skills/memex-cli/skills/
        if self.builtin_skills_dir.exists():
            builtin_skills = self._scan_skill_directory(self.builtin_skills_dir, source="builtin")
            config.skills.update(builtin_skills)
            logger.debug(f"Loaded {len(builtin_skills)} builtin skills from {self.builtin_skills_dir}")
        else:
            logger.warning(f"Builtin skills directory not found: {self.builtin_skills_dir}")

        # Add builtin command whitelist
        builtin_commands = ["git", "npm", "python", "pytest", "docker", "kubectl"]
        for cmd in builtin_commands:
            config.commands[cmd] = CommandConfig(
                name=cmd,
                enabled=True,
                priority=10,  # Low priority, can be overridden
                source="builtin"
            )

        return config

    def _load_user_config(self) -> OrchestratorConfig:
        """Load user-level configuration from ~/.claude/."""
        config = OrchestratorConfig()

        # Load user orchestrator.yaml
        user_config_file = self.user_config_dir / "orchestrator.yaml"
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_data = yaml.safe_load(f)
                    if user_data:
                        self._populate_config_from_dict(config, user_data, source="user")
                        logger.debug(f"Loaded user config from {user_config_file}")
            except Exception as e:
                logger.error(f"Failed to load user config from {user_config_file}: {e}")

        # Load user skills from ~/.claude/skills/
        user_skills_dir = self.user_config_dir / "skills"
        if user_skills_dir.exists():
            user_skills = self._scan_skill_directory(user_skills_dir, source="user")
            config.skills.update(user_skills)
            logger.debug(f"Loaded {len(user_skills)} user skills from {user_skills_dir}")

        return config

    def _load_project_config(self) -> OrchestratorConfig:
        """Load project-level configuration from ./orchestrator.yaml."""
        config = OrchestratorConfig()

        # Load project orchestrator.yaml
        project_config_file = self.project_root / "orchestrator.yaml"
        if project_config_file.exists():
            try:
                with open(project_config_file, 'r', encoding='utf-8') as f:
                    project_data = yaml.safe_load(f)
                    if project_data:
                        self._populate_config_from_dict(config, project_data, source="project")
                        logger.debug(f"Loaded project config from {project_config_file}")
            except Exception as e:
                logger.error(f"Failed to load project config from {project_config_file}: {e}")

        # Load project skills from ./skills/
        project_skills_dir = self.project_root / "skills"
        if project_skills_dir.exists():
            project_skills = self._scan_skill_directory(project_skills_dir, source="project")
            config.skills.update(project_skills)
            logger.debug(f"Loaded {len(project_skills)} project skills from {project_skills_dir}")

        return config

    def _scan_skill_directory(self, path: Path, source: str) -> Dict[str, SkillConfig]:
        """
        Scan directory for skill YAML files.

        Args:
            path: Directory to scan
            source: Source level ("builtin", "user", or "project")

        Returns:
            Dict mapping skill name to SkillConfig
        """
        skills = {}

        if not path.exists():
            return skills

        for yaml_file in path.glob("*.yaml"):
            try:
                skill_config = self._parse_skill_yaml(yaml_file, source)
                if skill_config:
                    skills[skill_config.name] = skill_config
            except Exception as e:
                logger.error(f"Failed to parse skill YAML {yaml_file}: {e}")

        return skills

    def _parse_skill_yaml(self, yaml_file: Path, source: str) -> Optional[SkillConfig]:
        """
        Parse a YAML skill file.

        Args:
            yaml_file: Path to YAML file
            source: Source level

        Returns:
            SkillConfig if valid, None otherwise
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

                if not data or 'name' not in data:
                    logger.warning(f"Skill YAML missing 'name' field: {yaml_file}")
                    return None

                # Set priority based on source
                priority_map = {"builtin": 10, "user": 50, "project": 100}
                default_priority = priority_map.get(source, 50)

                return SkillConfig(
                    name=data['name'],
                    type="yaml",
                    path=yaml_file,
                    enabled=data.get('enabled', True),
                    priority=data.get('priority', default_priority),
                    source=source,
                    dependencies=data.get('dependencies', []),
                    backend=data.get('backend', 'claude'),
                    config=data
                )
        except Exception as e:
            logger.error(f"Failed to parse skill YAML {yaml_file}: {e}")
            return None

    def _populate_config_from_dict(self, config: OrchestratorConfig, data: Dict[str, Any], source: str):
        """
        Populate OrchestratorConfig from parsed YAML/JSON dict.

        Args:
            config: Config object to populate
            data: Parsed configuration data
            source: Source level
        """
        # Set version
        if 'version' in data:
            config.version = data['version']

        # Set global settings
        if 'global' in data:
            config.global_settings.update(data['global'])

        # Load skills (manual declarations)
        if 'skills' in data and 'manual' in data['skills']:
            for skill_data in data['skills']['manual']:
                name = skill_data.get('name')
                if not name:
                    continue

                priority_map = {"builtin": 10, "user": 50, "project": 100}
                default_priority = priority_map.get(source, 50)

                config.skills[name] = SkillConfig(
                    name=name,
                    type=skill_data.get('type', 'yaml'),
                    path=Path(skill_data['path']) if 'path' in skill_data else None,
                    enabled=skill_data.get('enabled', True),
                    priority=skill_data.get('priority', default_priority),
                    source=source,
                    dependencies=skill_data.get('dependencies', []),
                    backend=skill_data.get('backend', 'claude'),
                    config=skill_data
                )

        # Load commands
        if 'commands' in data:
            # Whitelist
            if 'whitelist' in data['commands']:
                for cmd in data['commands']['whitelist']:
                    config.commands[cmd] = CommandConfig(
                        name=cmd,
                        enabled=True,
                        priority=50,
                        source=source
                    )

            # Aliases
            if 'aliases' in data['commands']:
                for alias_data in data['commands']['aliases']:
                    name = alias_data.get('name')
                    command = alias_data.get('command')
                    if name and command:
                        config.commands[name] = CommandConfig(
                            name=name,
                            command=command,
                            enabled=True,
                            priority=50,
                            source=source
                        )

        # Load agents
        if 'agents' in data:
            for agent_data in data['agents']:
                name = agent_data.get('name')
                if not name:
                    continue

                config.agents[name] = AgentConfig(
                    name=name,
                    agent_type=agent_data.get('type', 'general'),
                    enabled=agent_data.get('enabled', True),
                    priority=agent_data.get('priority', 50),
                    source=source,
                    dependencies=agent_data.get('dependencies', []),
                    config=agent_data
                )

        # Load prompts
        if 'prompts' in data:
            for prompt_data in data['prompts']:
                name = prompt_data.get('name')
                template = prompt_data.get('template')
                if not name or not template:
                    continue

                config.prompts[name] = PromptConfig(
                    name=name,
                    template=template,
                    variables=prompt_data.get('variables', []),
                    enabled=prompt_data.get('enabled', True),
                    priority=prompt_data.get('priority', 50),
                    source=source,
                    dependencies=prompt_data.get('dependencies', []),
                    config=prompt_data
                )

        # Load parallel config
        if 'parallel' in data:
            parallel_data = data['parallel']
            config.parallel_config = ParallelConfig(
                enabled=parallel_data.get('enabled', False),
                max_workers=parallel_data.get('max_workers', 3),
                timeout_per_task=parallel_data.get('timeout_per_task', 120),
                allowed_modes=parallel_data.get('allowed_modes', ["command", "backend"]),
                sequential_modes=parallel_data.get('sequential_modes', ["skill"])
            )

    def _merge_configs(self, configs: List[OrchestratorConfig]) -> OrchestratorConfig:
        """
        Merge multiple configurations with priority (later configs override earlier ones).

        Args:
            configs: List of configs in priority order (lowest to highest)

        Returns:
            Merged configuration
        """
        merged = OrchestratorConfig()

        for config in configs:
            # Merge version (keep highest)
            if config.version:
                merged.version = config.version

            # Merge global settings (later overrides earlier)
            merged.global_settings.update(config.global_settings)

            # Merge skills (priority-based)
            for name, skill in config.skills.items():
                if name in merged.skills:
                    # Compare priorities
                    if skill.priority >= merged.skills[name].priority:
                        merged.skills[name] = skill
                        logger.debug(f"Skill '{name}' overridden by {skill.source} "
                                   f"(priority {skill.priority})")
                else:
                    merged.skills[name] = skill

            # Merge commands (priority-based)
            for name, command in config.commands.items():
                if name in merged.commands:
                    if command.priority >= merged.commands[name].priority:
                        merged.commands[name] = command
                        logger.debug(f"Command '{name}' overridden by {command.source} "
                                   f"(priority {command.priority})")
                else:
                    merged.commands[name] = command

            # Merge agents (priority-based)
            for name, agent in config.agents.items():
                if name in merged.agents:
                    if agent.priority >= merged.agents[name].priority:
                        merged.agents[name] = agent
                        logger.debug(f"Agent '{name}' overridden by {agent.source} "
                                   f"(priority {agent.priority})")
                else:
                    merged.agents[name] = agent

            # Merge prompts (priority-based)
            for name, prompt in config.prompts.items():
                if name in merged.prompts:
                    if prompt.priority >= merged.prompts[name].priority:
                        merged.prompts[name] = prompt
                        logger.debug(f"Prompt '{name}' overridden by {prompt.source} "
                                   f"(priority {prompt.priority})")
                else:
                    merged.prompts[name] = prompt

            # Merge parallel config (later overrides)
            if config.parallel_config:
                merged.parallel_config = config.parallel_config

        return merged

    def _validate_config(self, config: OrchestratorConfig) -> List[str]:
        """
        Validate configuration completeness and correctness.

        Args:
            config: Configuration to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check version format
        if not config.version or not config.version.startswith("3."):
            errors.append(f"Invalid or missing version: {config.version} (expected 3.x)")

        # Check skill paths
        for name, skill in config.skills.items():
            if skill.path and not skill.path.exists():
                errors.append(f"Skill '{name}' path not found: {skill.path}")

        # Check dependencies exist
        all_resources = set(config.skills.keys()) | set(config.commands.keys()) | \
                       set(config.agents.keys()) | set(config.prompts.keys())

        for name, skill in config.skills.items():
            for dep in skill.dependencies:
                if dep not in all_resources:
                    errors.append(f"Skill '{name}' has unknown dependency: {dep}")

        for name, command in config.commands.items():
            for dep in command.dependencies:
                if dep not in all_resources:
                    errors.append(f"Command '{name}' has unknown dependency: {dep}")

        # Check parallel config
        if config.parallel_config.max_workers < 1:
            errors.append(f"Invalid max_workers: {config.parallel_config.max_workers} (must be >= 1)")

        if config.parallel_config.timeout_per_task < 1:
            errors.append(f"Invalid timeout_per_task: {config.parallel_config.timeout_per_task} (must be >= 1)")

        return errors
