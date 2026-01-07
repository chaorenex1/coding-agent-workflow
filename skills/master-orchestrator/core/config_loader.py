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
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

# ResourceScanner will be imported lazily to avoid circular dependency
# (resource_scanner imports ResourceType from this file)
ResourceScanner = None
DiscoveredResource = None
SCANNER_AVAILABLE = False


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
    path: Optional[Path] = None
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
    path: Optional[Path] = None
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
    path: Optional[Path] = None
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
class SlashCommandConfig:
    """Configuration for a slash command (V3.1)."""
    name: str
    type: str  # "system", "shell", "skill", "agent", "prompt"
    description: str = ""
    enabled: bool = True
    priority: int = 50  # 0-1000, higher = higher priority
    source: str = "project"  # "builtin", "user", or "project"

    # Type-specific fields
    handler: Optional[str] = None  # For system commands
    command: Optional[str] = None  # For shell commands
    skill: Optional[str] = None  # For skill commands
    agent_type: Optional[str] = None  # For agent commands
    prompt_template: Optional[str] = None  # For prompt commands

    # Metadata
    examples: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


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
    slash_commands: Dict[str, SlashCommandConfig] = field(default_factory=dict)  # V3.1


def find_git_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the git repository root directory.

    Uses 'git rev-parse --show-toplevel' to find the root.
    Falls back to current directory if not in a git repository.

    Args:
        start_path: Starting directory for search. Defaults to current directory.

    Returns:
        Path to git root, or None if not in a git repository.
    """
    cwd = Path(start_path) if start_path else Path.cwd()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug(f"Git root detection failed: {e}")

    return None


class ConfigLoader:
    """
    Configuration loader with three-tier priority system.

    Loads and merges configurations from:
    1. Builtin (lowest priority)
    2. User (~/.claude/)
    3. Project (highest priority)
    """

    def __init__(self, project_root: Optional[Path] = None, enable_auto_discovery: bool = True):
        """
        Initialize ConfigLoader.

        Args:
            project_root: Root directory of the project. If None, attempts to detect
                          git repository root, falling back to current directory.
            enable_auto_discovery: Enable automatic resource discovery via directory scanning
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            # 优先使用 git 仓库根目录
            git_root = find_git_root()
            self.project_root = git_root if git_root else Path.cwd()
        self.project_config_dir = self.project_root / ".claude"
        self.user_config_dir = Path.home() / ".claude"
        self.use_orchestrator_dir = Path.home() / ".memex" / "orchestrator"
        self.enable_auto_discovery = enable_auto_discovery

        # Lazy import ResourceScanner to avoid circular dependency
        self.scanner = None
        if self.enable_auto_discovery:
            try:
                from .resource_scanner_v2 import ResourceScanner
                self.scanner = ResourceScanner()
                logger.info("Auto-discovery enabled via ResourceScannerV2")
            except ImportError as e:
                logger.warning(f"Auto-discovery requested but ResourceScannerV2 not available: {e}")
                self.enable_auto_discovery = False

        # Initialize RegistryPersistence for caching scan results
        self.persistence = None
        if self.enable_auto_discovery:
            try:
                from .registry_persistence import RegistryPersistence
                registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"

                # Read cache_ttl from config files (project > user > default)
                cache_ttl = self._read_cache_ttl_from_configs()

                self.persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=cache_ttl)
                if cache_ttl != 3600:
                    logger.info(f"使用配置文件的 cache_ttl: {cache_ttl}s (默认: 3600s)")
                logger.debug(f"RegistryPersistence initialized with TTL={cache_ttl}s")
            except ImportError as e:
                logger.warning(f"RegistryPersistence not available: {e}")

        # Determine builtin skills directory
        self.builtin_skills_dir = Path(__file__).parent.parent

        logger.debug(f"ConfigLoader initialized:")
        logger.debug(f"  Project root: {self.project_root}")
        logger.debug(f"  User config dir: {self.user_config_dir}")
        logger.debug(f"  Builtin skills dir: {self.builtin_skills_dir}")
        logger.debug(f"  Auto-discovery: {self.enable_auto_discovery}")

    def _read_cache_ttl_from_configs(self) -> int:
        """
        Read cache_ttl from project or user config files.

        Returns:
            cache_ttl value from config file, or 3600 (default) if not found.
            Priority: project > user > default
        """
        import yaml

        # Try project config first
        project_config_file = self.project_config_dir / "orchestrator.yaml"
        if project_config_file.exists():
            try:
                with open(project_config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'global' in data and 'cache_ttl' in data['global']:
                        ttl = data['global']['cache_ttl']
                        if isinstance(ttl, int) and ttl > 0:
                            logger.debug(f"Using cache_ttl from project config: {ttl}s")
                            return ttl
            except Exception as e:
                logger.debug(f"Failed to read cache_ttl from project config: {e}")

        # Try user config
        user_config_file = self.user_config_dir / "orchestrator.yaml"
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'global' in data and 'cache_ttl' in data['global']:
                        ttl = data['global']['cache_ttl']
                        if isinstance(ttl, int) and ttl > 0:
                            logger.debug(f"Using cache_ttl from user config: {ttl}s")
                            return ttl
            except Exception as e:
                logger.debug(f"Failed to read cache_ttl from user config: {e}")

        # Default
        logger.debug("Using default cache_ttl: 3600s")
        return 3600

    def load(self) -> OrchestratorConfig:
        """
        Load and merge all configurations.

        Returns:
            Merged OrchestratorConfig with project-level taking highest priority.
        """
        import time
        start_time = time.time()

        logger.info("Loading orchestrator configurations...")

        # 1. Load builtin configuration
        builtin_config = self._load_builtin_config()
        logger.debug(f"Loaded builtin config: {len(builtin_config.skills)} skills, "
                    f"{len(builtin_config.commands)} commands")

        # 2. Load user-level configuration
        user_config, user_stats, user_files = self._load_user_config()
        logger.debug(f"Loaded user config: {len(user_config.skills)} skills, "
                    f"{len(user_config.commands)} commands")

        # 3. Load project-level configuration
        project_config, project_stats, project_files = self._load_project_config()
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

        # 6. Log combined discovery statistics
        total_discovered = {
            "skills": user_stats["skills"] + project_stats["skills"],
            "commands": user_stats["commands"] + project_stats["commands"],
            "agents": user_stats["agents"] + project_stats["agents"],
            "prompts": user_stats["prompts"] + project_stats["prompts"]
        }
        if any(v > 0 for v in total_discovered.values()):
            logger.info(
                f"Auto-discovered: {total_discovered['skills']} skills, "
                f"{total_discovered['commands']} commands, "
                f"{total_discovered['agents']} agents, "
                f"{total_discovered['prompts']} prompts "
                f"(user: {user_stats['skills']}/{user_stats['commands']}/{user_stats['agents']}/{user_stats['prompts']}, "
                f"project: {project_stats['skills']}/{project_stats['commands']}/{project_stats['agents']}/{project_stats['prompts']})"
            )

        logger.info(f"Configuration loaded successfully: {len(merged_config.skills)} skills, "
                   f"{len(merged_config.commands)} commands, "
                   f"{len(merged_config.agents)} agents, "
                   f"{len(merged_config.prompts)} prompts")

        # 7. Save combined scan results to cache (if persistence is available)
        if self.persistence and any(v > 0 for v in total_discovered.values()):
            scan_duration_ms = int((time.time() - start_time) * 1000)
            all_files = user_files + project_files

            # Convert merged config to serializable format for caching
            combined_resources = {
                "skill": [vars(skill) for skill in merged_config.skills.values()],
                "command": [vars(cmd) for cmd in merged_config.commands.values()],
                "agent": [vars(agent) for agent in merged_config.agents.values()],
                "prompt": [vars(prompt) for prompt in merged_config.prompts.values()]
            }

            self.persistence.save_scan_result(combined_resources, all_files, scan_duration_ms,total_discovered)

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
        # Note: Only scan skills, as builtin commands/agents/prompts use YAML whitelist
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
                source="builtin",
                path=None
            )

        # === LEGACY: Load user orchestrator.yaml (overrides auto-discovery) ===
        user_config_file = self.builtin_skills_dir / "orchestrator.yaml"
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_data = yaml.safe_load(f)
                    if user_data:
                        self._populate_config_from_dict(config, user_data, source="builtin")
                        logger.info(f"Loaded builtin config from {user_config_file}")
            except Exception as e:
                logger.error(f"Failed to load builtin config from {user_config_file}: {e}")

        return config

    def _load_user_config(self) -> tuple[OrchestratorConfig, Dict[str, int], List[str]]:
        """
        Load user-level configuration from ~/.claude/ and auto-discover resources.

        Returns:
            Tuple of (config, discovery_stats, scanned_files) where:
            - discovery_stats contains counts per resource type
            - scanned_files contains list of scanned file paths
        """
        config = OrchestratorConfig()
        discovery_stats = {"skills": 0, "commands": 0, "agents": 0, "prompts": 0}
        scanned_files: List[str] = []

        # === NEW: Auto-discovery (if enabled) ===
        if self.enable_auto_discovery and self.scanner and self.user_config_dir.exists():
            import time
            start_time = time.time()

            # Collect all potential resource files for cache validation
            scan_file_paths = self._collect_resource_files(self.user_config_dir)
            scanned_files = scan_file_paths

            # Try loading from cache first
            discovered = None
            if self.persistence and scan_file_paths:
                cached_data = self.persistence.load_cached_resources(scan_file_paths)
                if cached_data:
                    # Convert string keys back to ResourceType keys
                    discovered = self._reconstruct_resources_from_cache(cached_data)

            if discovered:
                logger.info("Loaded user resources from cache")
            else:
                # Cache miss or invalid - perform actual scan
                logger.info("Running auto-discovery for user resources...")
                discovered = self.scanner.scan_all(self.user_config_dir, source="user")

                # Convert discovered resources to config objects
                for resource_type, resources in discovered.items():
                    for discovered_item in resources:
                        # Handle both DiscoveredResource objects and dicts (from cache)
                        # if isinstance(discovered_item, dict):
                        #     # Reconstruct DiscoveredResource from cached dict
                        #     from .resource_scanner_v2 import DiscoveredResource, ResourceLayout
                        #     from pathlib import Path

                        #     # Convert string values back to proper types
                        #     if 'resource_type' in discovered_item and isinstance(discovered_item['resource_type'], str):
                        #         discovered_item['resource_type'] = ResourceType[discovered_item['resource_type'].upper()]

                        #     if 'path' in discovered_item and isinstance(discovered_item['path'], str):
                        #         discovered_item['path'] = Path(discovered_item['path'])

                        #     if 'marker_file' in discovered_item and discovered_item['marker_file'] and isinstance(discovered_item['marker_file'], str):
                        #         discovered_item['marker_file'] = Path(discovered_item['marker_file'])

                        #     if 'entry_point' in discovered_item and discovered_item['entry_point'] and isinstance(discovered_item['entry_point'], str):
                        #         discovered_item['entry_point'] = Path(discovered_item['entry_point'])

                        #     if 'relative_path' in discovered_item and discovered_item['relative_path'] and isinstance(discovered_item['relative_path'], str):
                        #         discovered_item['relative_path'] = Path(discovered_item['relative_path'])

                        #     if 'layout' in discovered_item and isinstance(discovered_item['layout'], str):
                        #         discovered_item['layout'] = ResourceLayout(discovered_item['layout'])
                                
                        #     # Convert resource_type string to enum if needed
                        #     if 'resource_type' in discovered_item and isinstance(discovered_item['resource_type'], str):
                        #         discovered_item['resource_type'] = ResourceType(discovered_item['resource_type'])

                        #     discovered_item = DiscoveredResource(**discovered_item)

                        converted = self.scanner.convert_to_config(discovered_item)

                        if resource_type == ResourceType.SKILL:
                            config.skills[converted.name] = converted  # Always add
                        elif resource_type == ResourceType.COMMAND:
                            config.commands[converted.name] = converted
                        elif resource_type == ResourceType.AGENT:
                            config.agents[converted.name] = converted
                        elif resource_type == ResourceType.PROMPT:
                            config.prompts[converted.name] = converted

            # Track discovery statistics
            discovery_stats["skills"] = len(discovered[ResourceType.SKILL])
            discovery_stats["commands"] = len(discovered[ResourceType.COMMAND])
            discovery_stats["agents"] = len(discovered[ResourceType.AGENT])
            discovery_stats["prompts"] = len(discovered[ResourceType.PROMPT])

            logger.info(
                f"User auto-discovered: {discovery_stats['skills']} skills, "
                f"{discovery_stats['commands']} commands, "
                f"{discovery_stats['agents']} agents, "
                f"{discovery_stats['prompts']} prompts"
            )

        # === LEGACY: Load user orchestrator.yaml (overrides auto-discovery) ===
        user_config_file = self.use_orchestrator_dir / "orchestrator.yaml"
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_data = yaml.safe_load(f)
                    if user_data:
                        self._populate_config_from_dict(config, user_data, source="user")
                        logger.info(f"Loaded user config from {user_config_file}")
            except Exception as e:
                logger.error(f"Failed to load user config from {user_config_file}: {e}")

        return config, discovery_stats, scanned_files

    def _load_project_config(self) -> tuple[OrchestratorConfig, Dict[str, int], List[str]]:
        """
        Load project-level configuration from ./orchestrator.yaml and auto-discover resources.

        Returns:
            Tuple of (config, discovery_stats, scanned_files) where:
            - discovery_stats contains counts per resource type
            - scanned_files contains list of scanned file paths
        """
        config = OrchestratorConfig()
        discovery_stats = {"skills": 0, "commands": 0, "agents": 0, "prompts": 0}
        scanned_files: List[str] = []

        # === NEW: Auto-discovery (if enabled) ===
        if self.enable_auto_discovery and self.scanner:
            logger.info("Running auto-discovery for project resources...")
            scanned_files = self._collect_resource_files(self.project_config_dir)

            # Try loading from cache first
            discovered = None
            if self.persistence and scanned_files:
                cached_data = self.persistence.load_cached_resources(scanned_files)
                if cached_data:
                    # Convert string keys back to ResourceType keys
                    discovered = self._reconstruct_resources_from_cache(cached_data)

            if discovered:
                logger.info("Loaded project resources from cache")
            else:
                # Cache miss or invalid - perform actual scan
                logger.info("Running auto-discovery for project resources...")
                discovered = self.scanner.scan_all(self.project_config_dir, source="project")

                # Convert discovered resources to config objects
                for resource_type, resources in discovered.items():
                    for discovered_item in resources:
                        converted = self.scanner.convert_to_config(discovered_item)

                        if resource_type == ResourceType.SKILL:
                            config.skills[converted.name] = converted  # Always add, override later if needed
                        elif resource_type == ResourceType.COMMAND:
                            config.commands[converted.name] = converted
                        elif resource_type == ResourceType.AGENT:
                            config.agents[converted.name] = converted
                        elif resource_type == ResourceType.PROMPT:
                            config.prompts[converted.name] = converted

            # Track discovery statistics
            discovery_stats["skills"] = len(discovered[ResourceType.SKILL])
            discovery_stats["commands"] = len(discovered[ResourceType.COMMAND])
            discovery_stats["agents"] = len(discovered[ResourceType.AGENT])
            discovery_stats["prompts"] = len(discovered[ResourceType.PROMPT])

            logger.info(
                f"Project auto-discovered: {discovery_stats['skills']} skills, "
                f"{discovery_stats['commands']} commands, "
                f"{discovery_stats['agents']} agents, "
                f"{discovery_stats['prompts']} prompts"
            )

        # === LEGACY: Load project orchestrator.yaml (overrides auto-discovery) ===
        project_config_file = self.project_config_dir / "orchestrator.yaml"
        if project_config_file.exists():
            try:
                with open(project_config_file, 'r', encoding='utf-8') as f:
                    project_data = yaml.safe_load(f)
                    if project_data:
                        self._populate_config_from_dict(config, project_data, source="project")
                        logger.info(f"Loaded project config from {project_config_file}")
            except Exception as e:
                logger.error(f"Failed to load project config from {project_config_file}: {e}")

        return config, discovery_stats, scanned_files

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
        # Validate data type
        if not isinstance(data, dict):
            logger.error(f"Expected dict but got {type(data)}: {data}")
            return

        # Set version
        if 'version' in data:
            config.version = data['version']

        # Set global settings
        if 'global' in data:
            config.global_settings.update(data['global'])

        # Load skills (manual declarations)
        if 'skills' in data and 'manual' in data['skills']:
            for skill_data in data['skills']['manual']:
                if not isinstance(skill_data, dict):
                    logger.warning(f"Skipping invalid skill data (expected dict): {skill_data}")
                    continue
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
                    if not isinstance(cmd, str):
                        logger.warning(f"Skipping invalid whitelist command (expected string): {cmd}")
                        continue
                    config.commands[cmd] = CommandConfig(
                        name=cmd,
                        enabled=True,
                        priority=50,
                        source=source
                    )

            # Aliases
            if 'aliases' in data['commands']:
                for alias_data in data['commands']['aliases']:
                    if not isinstance(alias_data, dict):
                        logger.warning(f"Skipping invalid alias data (expected dict): {alias_data}")
                        continue
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
            agents_data = data['agents']

            # Support both list and dict formats
            if isinstance(agents_data, list):
                # List format: [{name: "foo", type: "general", ...}, ...]
                for agent_data in enumerate(agents_data):
                    if not isinstance(agent_data, dict):
                        logger.warning(f"Skipping invalid agent data (expected dict): {agent_data}")
                        continue
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
            elif isinstance(agents_data, dict):
                # Dict format: {default: {model: ..., temperature: ...}, explore: {...}}
                # This is configuration for agent behavior, not agent registration
                # Store it in global_settings['agent_configs']
                config.global_settings['agent_configs'] = agents_data
                logger.debug(f"Loaded {len(agents_data)} agent configurations from {source}")
            else:
                logger.error(f"Invalid agents format: expected list or dict, got {type(agents_data)}")

        # Load prompts
        if 'prompts' in data:
            prompts_data = data['prompts']

            # Support both list and dict formats
            if isinstance(prompts_data, list):
                # List format: [{name: "foo", template: "...", ...}, ...]
                for prompt_data in prompts_data:
                    if not isinstance(prompt_data, dict):
                        logger.warning(f"Skipping invalid prompt data (expected dict): {prompt_data}")
                        continue
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
            elif isinstance(prompts_data, dict):
                # Dict format: {templates: [...], categories: {...}}
                # Extract templates list if present
                if 'templates' in prompts_data and isinstance(prompts_data['templates'], list):
                    for prompt_data in prompts_data['templates']:
                        if not isinstance(prompt_data, dict):
                            continue
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
                    logger.debug(f"Loaded {len(prompts_data['templates'])} prompt templates from {source}")
            else:
                logger.error(f"Invalid prompts format: expected list or dict, got {type(prompts_data)}")

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

        # Load slash commands (V3.1)
        if 'slash_commands' in data:
            slash_data = data['slash_commands']

            # Parse system commands
            if 'system' in slash_data:
                for cmd_data in slash_data['system']:
                    name = cmd_data.get('name')
                    if not name:
                        continue

                    config.slash_commands[name] = SlashCommandConfig(
                        name=name,
                        type="system",
                        description=cmd_data.get('description', ''),
                        handler=cmd_data.get('handler'),
                        enabled=cmd_data.get('enabled', True),
                        priority=cmd_data.get('priority', 50),
                        source=source,
                        examples=cmd_data.get('examples', []),
                        dependencies=cmd_data.get('dependencies', []),
                        config=cmd_data
                    )

            # Parse shell commands
            if 'shell' in slash_data:
                for cmd_data in slash_data['shell']:
                    name = cmd_data.get('name')
                    if not name:
                        continue

                    config.slash_commands[name] = SlashCommandConfig(
                        name=name,
                        type="shell",
                        description=cmd_data.get('description', ''),
                        command=cmd_data.get('command'),
                        enabled=cmd_data.get('enabled', True),
                        priority=cmd_data.get('priority', 50),
                        source=source,
                        examples=cmd_data.get('examples', []),
                        dependencies=cmd_data.get('dependencies', []),
                        config=cmd_data
                    )

            # Parse skill commands
            if 'skill' in slash_data:
                for cmd_data in slash_data['skill']:
                    name = cmd_data.get('name')
                    if not name:
                        continue

                    config.slash_commands[name] = SlashCommandConfig(
                        name=name,
                        type="skill",
                        description=cmd_data.get('description', ''),
                        skill=cmd_data.get('skill'),
                        enabled=cmd_data.get('enabled', True),
                        priority=cmd_data.get('priority', 50),
                        source=source,
                        examples=cmd_data.get('examples', []),
                        dependencies=cmd_data.get('dependencies', []),
                        config=cmd_data
                    )

            # Parse agent commands
            if 'agent' in slash_data:
                for cmd_data in slash_data['agent']:
                    name = cmd_data.get('name')
                    if not name:
                        continue

                    config.slash_commands[name] = SlashCommandConfig(
                        name=name,
                        type="agent",
                        description=cmd_data.get('description', ''),
                        agent_type=cmd_data.get('agent_type'),
                        enabled=cmd_data.get('enabled', True),
                        priority=cmd_data.get('priority', 50),
                        source=source,
                        examples=cmd_data.get('examples', []),
                        dependencies=cmd_data.get('dependencies', []),
                        config=cmd_data
                    )

            # Parse prompt commands
            if 'prompt' in slash_data:
                for cmd_data in slash_data['prompt']:
                    name = cmd_data.get('name')
                    if not name:
                        continue

                    config.slash_commands[name] = SlashCommandConfig(
                        name=name,
                        type="prompt",
                        description=cmd_data.get('description', ''),
                        prompt_template=cmd_data.get('prompt_template'),
                        enabled=cmd_data.get('enabled', True),
                        priority=cmd_data.get('priority', 50),
                        source=source,
                        examples=cmd_data.get('examples', []),
                        dependencies=cmd_data.get('dependencies', []),
                        config=cmd_data
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

            # Merge slash commands (V3.1, priority-based)
            for name, slash_cmd in config.slash_commands.items():
                if name in merged.slash_commands:
                    if slash_cmd.priority >= merged.slash_commands[name].priority:
                        merged.slash_commands[name] = slash_cmd
                        logger.debug(f"Slash command '{name}' overridden by {slash_cmd.source} "
                                   f"(priority {slash_cmd.priority})")
                else:
                    merged.slash_commands[name] = slash_cmd

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

    def _collect_resource_files(self, base_path: Path) -> List[str]:
        """
        Collect all resource files for cache validation.

        Args:
            base_path: Base directory to scan

        Returns:
            List of file paths as strings
        """
        file_paths = []

        # Scan resource directories
        for subdir in ['skills', 'commands', 'agents', 'prompts']:
            resource_dir = base_path / subdir
            if resource_dir.exists():
                # Collect YAML files
                for pattern in ['**/*.yaml', '**/*.yml']:
                    file_paths.extend(str(p) for p in resource_dir.glob(pattern))

                # Collect marker files
                for marker in ['SKILL.md', '*.md', '*.md', '*.md', '*.md']:
                    file_paths.extend(str(p) for p in resource_dir.glob(f'**/{marker}'))

        return file_paths

    def _prepare_resources_for_cache(self, resources: Dict[ResourceType, List]) -> Dict[str, List]:
        """
        Prepare resources for cache storage.

        Converts ResourceType keys to strings and ensures resources are serializable.

        Args:
            resources: Dictionary with ResourceType keys

        Returns:
            Dictionary with string keys, suitable for JSON serialization
        """
        serializable = {}

        for resource_type, resource_list in resources.items():
            # Convert ResourceType enum to string key
            key = resource_type.value  # "skill", "command", etc.
            serializable[key] = resource_list

        return serializable

    def _reconstruct_resources_from_cache(self, cached_data: Dict[str, List]) -> Dict[ResourceType, List]:
        """
        Reconstruct resources from cache data.

        Converts string keys back to ResourceType keys.

        Args:
            cached_data: Cached data with string keys

        Returns:
            Dictionary with ResourceType keys
        """
        reconstructed = {
            ResourceType.SKILL: [],
            ResourceType.COMMAND: [],
            ResourceType.AGENT: [],
            ResourceType.PROMPT: []
        }

        # Map string keys to ResourceType
        key_map = {
            "skill": ResourceType.SKILL,
            "command": ResourceType.COMMAND,
            "agent": ResourceType.AGENT,
            "prompt": ResourceType.PROMPT
        }

        for key, resource_list in cached_data.items():
            resource_type = key_map.get(key)
            if resource_type:
                reconstructed[resource_type] = resource_list

        return reconstructed
