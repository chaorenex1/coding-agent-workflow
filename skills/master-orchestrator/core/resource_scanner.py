"""
Resource Scanner for auto-discovery of Skills, Commands, Agents, and Prompts.

Supports convention-over-configuration approach:
- Scans skills/, commands/, agents/, prompts/ directories
- Auto-detects resources from directory structure and marker files
- YAML configuration remains optional and can override auto-discovered settings
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import yaml

from .config_loader import ResourceType, SkillConfig, CommandConfig, AgentConfig, PromptConfig


logger = logging.getLogger(__name__)


@dataclass
class DiscoveredResource:
    """
    Unified data structure for discovered resources.

    Represents a resource found through directory scanning, before converting
    to specific config types (SkillConfig, CommandConfig, etc.)
    """
    name: str
    resource_type: ResourceType
    path: Path
    source: str  # "builtin", "user", or "project"

    # Discovery metadata
    discovery_method: str  # "yaml_file", "directory_convention", "python_module"
    marker_file: Optional[Path] = None  # SKILL.md, COMMAND.md, etc.
    entry_point: Optional[Path] = None  # main.py, __init__.py, etc.

    # Extracted metadata
    description: str = ""
    enabled: bool = True
    priority: int = 50
    dependencies: List[str] = field(default_factory=list)

    # Type-specific data
    config_data: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (f"DiscoveredResource({self.resource_type.value}:{self.name}, "
                f"method={self.discovery_method}, source={self.source})")


class BaseResourceDetector:
    """
    Base class for resource type detectors.

    Each resource type (SKILL/COMMAND/AGENT/PROMPT) has its own detector
    that knows how to identify and parse resources of that type.
    """

    MARKER_FILE: str = None  # Override in subclass (e.g., "SKILL.md")
    YAML_PATTERN: str = "*.yaml"

    def __init__(self, source: str):
        """
        Initialize detector.

        Args:
            source: Resource source level ("builtin", "user", or "project")
        """
        self.source = source
        self.priority_map = {"builtin": 10, "user": 50, "project": 100}

    def scan_directory(self, directory: Path) -> List[DiscoveredResource]:
        """
        Scan directory and discover resources.

        Args:
            directory: Directory to scan

        Returns:
            List of discovered resources
        """
        if not directory.exists():
            logger.debug(f"Directory does not exist: {directory}")
            return []

        discovered = []

        for item in directory.iterdir():
            # Skip hidden files and cache
            if item.name.startswith('.') or item.name == '__pycache__':
                continue

            # Case 1: YAML file
            if item.is_file() and item.suffix == '.yaml':
                resource = self._detect_from_yaml_file(item)
                if resource:
                    discovered.append(resource)

            # Case 2: Directory
            elif item.is_dir():
                resource = self._detect_from_directory(item)
                if resource:
                    discovered.append(resource)

        logger.info(f"Discovered {len(discovered)} {self.get_resource_type().value}s in {directory}")
        return discovered

    def _detect_from_yaml_file(self, yaml_file: Path) -> Optional[DiscoveredResource]:
        """Detect resource from standalone YAML file."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'name' not in data:
                logger.warning(f"YAML file missing 'name' field: {yaml_file}")
                return None

            return DiscoveredResource(
                name=data['name'],
                resource_type=self.get_resource_type(),
                path=yaml_file,
                source=self.source,
                discovery_method="yaml_file",
                description=data.get('description', ''),
                enabled=data.get('enabled', True),
                priority=data.get('priority', self.priority_map[self.source]),
                dependencies=data.get('dependencies', []),
                config_data=data
            )
        except Exception as e:
            logger.error(f"Failed to parse YAML file {yaml_file}: {e}")
            return None

    def _detect_from_directory(self, directory: Path) -> Optional[DiscoveredResource]:
        """
        Detect resource from directory structure.

        Priority:
        1. Explicit YAML config file in directory (e.g., skill.yaml)
        2. Marker file (e.g., SKILL.md) with metadata
        3. Python module (__init__.py)
        """
        # Priority 1: Explicit YAML config
        yaml_configs = list(directory.glob("*.yaml"))
        if yaml_configs:
            # Use the first YAML file found
            return self._detect_from_yaml_file(yaml_configs[0])

        # Priority 2: Marker file convention
        if self.MARKER_FILE:
            marker_path = directory / self.MARKER_FILE
            if marker_path.exists():
                return self._infer_from_marker_file(directory, marker_path)

        # Priority 3: Python module
        init_file = directory / "__init__.py"
        if init_file.exists():
            return self._infer_from_python_module(directory)

        logger.debug(f"No valid resource found in directory: {directory}")
        return None

    def _infer_from_marker_file(
        self,
        directory: Path,
        marker_file: Path
    ) -> Optional[DiscoveredResource]:
        """
        Infer resource configuration from marker file (SKILL.md, COMMAND.md, etc.).

        Args:
            directory: Resource directory
            marker_file: Path to marker file

        Returns:
            Discovered resource or None
        """
        try:
            # Parse marker file metadata
            metadata = self._parse_markdown_metadata(marker_file)

            # Find entry point (only for resources that need Python code)
            entry_point = self._find_entry_point(directory) if self._needs_entry_point() else None

            # Build resource
            return DiscoveredResource(
                name=metadata.get('name', directory.name),
                resource_type=self.get_resource_type(),
                path=directory,
                source=self.source,
                discovery_method="directory_convention",
                marker_file=marker_file,
                entry_point=entry_point,
                description=metadata.get('description', ''),
                enabled=metadata.get('enabled', True),
                priority=metadata.get('priority', self.priority_map[self.source]),
                dependencies=metadata.get('dependencies', []),
                config_data=metadata
            )
        except Exception as e:
            logger.error(f"Failed to infer from marker file {marker_file}: {e}")
            return None

    def _needs_entry_point(self) -> bool:
        """
        Check if this resource type needs a Python entry point.

        Override in subclasses.
        Default: False (most resources don't need Python code)
        """
        return False

    def _infer_from_python_module(self, directory: Path) -> Optional[DiscoveredResource]:
        """
        Infer resource from Python module structure.

        Lowest priority fallback when no explicit config or marker exists.
        """
        return DiscoveredResource(
            name=directory.name,
            resource_type=self.get_resource_type(),
            path=directory,
            source=self.source,
            discovery_method="python_module",
            entry_point=directory / "__init__.py",
            description=f"Auto-discovered {self.get_resource_type().value} module",
            enabled=True,
            priority=self.priority_map[self.source] - 10,  # Lower priority
            config_data={}
        )

    def _parse_markdown_metadata(self, markdown_file: Path) -> Dict[str, Any]:
        """
        Parse metadata from Markdown file.

        Supports:
        1. YAML front matter (--- ... ---)
        2. Markdown structure (# Title, ## Description, etc.)

        Args:
            markdown_file: Path to markdown file

        Returns:
            Extracted metadata dictionary
        """
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = {}

        # Parse YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    if front_matter:
                        metadata.update(front_matter)
                        content = parts[2]  # Use rest of content for markdown parsing
                except Exception as e:
                    logger.warning(f"Failed to parse YAML front matter in {markdown_file}: {e}")

        # Extract from Markdown structure if not in front matter
        if 'name' not in metadata:
            # Extract title (# Title)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['name'] = title_match.group(1).strip()

        if 'description' not in metadata:
            # Extract description from first paragraph or ## Description section
            desc_patterns = [
                r'^(?:##\s+)?(?:Description|描述|简介)[\s:]*\n+(.+?)(?=\n##|\n\n##|\Z)',
                r'^#\s+.+?\n+(.+?)(?=\n##|\Z)'
            ]
            for pattern in desc_patterns:
                desc_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
                if desc_match:
                    metadata['description'] = desc_match.group(1).strip()
                    break

        return metadata

    def _find_entry_point(self, directory: Path) -> Optional[Path]:
        """
        Find the entry point file for a resource.

        Priority order:
        1. main.py
        2. {directory-name}.py
        3. {directory-name-underscored}.py
        4. __main__.py
        5. First non-test Python file

        Args:
            directory: Directory to search

        Returns:
            Path to entry point or None
        """
        candidates = [
            directory / "main.py",
            directory / f"{directory.name}.py",
            directory / f"{directory.name.replace('-', '_')}.py",
            directory / "__main__.py"
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Find first non-test Python file
        for py_file in directory.glob("*.py"):
            if not py_file.name.startswith('test_') and py_file.name != '__init__.py':
                return py_file

        return None

    def get_resource_type(self) -> ResourceType:
        """Get the resource type this detector handles (override in subclass)."""
        raise NotImplementedError


class SkillDetector(BaseResourceDetector):
    """Detector for SKILL resources."""

    MARKER_FILE = "SKILL.md"

    def get_resource_type(self) -> ResourceType:
        return ResourceType.SKILL

    def _needs_entry_point(self) -> bool:
        """Skills typically need Python entry points."""
        return True


class CommandDetector(BaseResourceDetector):
    """Detector for COMMAND resources."""

    MARKER_FILE = "COMMAND.md"

    def get_resource_type(self) -> ResourceType:
        return ResourceType.COMMAND

    def _needs_entry_point(self) -> bool:
        """Commands don't need Python entry points - they are shell commands."""
        return False

    def _infer_from_marker_file(
        self,
        directory: Path,
        marker_file: Path
    ) -> Optional[DiscoveredResource]:
        """
        Commands have additional logic for extracting shell commands.
        """
        resource = super()._infer_from_marker_file(directory, marker_file)

        if resource:
            # Try to extract shell command from config_data
            if 'command' not in resource.config_data:
                # Look for code blocks in COMMAND.md
                with open(marker_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract first shell code block
                    code_match = re.search(r'```(?:bash|sh|shell)\n(.+?)\n```', content, re.DOTALL)
                    if code_match:
                        resource.config_data['command'] = code_match.group(1).strip()

        return resource


class AgentDetector(BaseResourceDetector):
    """Detector for AGENT resources."""

    MARKER_FILE = "AGENT.md"

    def get_resource_type(self) -> ResourceType:
        return ResourceType.AGENT

    def _needs_entry_point(self) -> bool:
        """Agents are configurations, typically don't need Python entry points."""
        return False

    def _infer_from_marker_file(
        self,
        directory: Path,
        marker_file: Path
    ) -> Optional[DiscoveredResource]:
        """
        Agents need agent_type configuration.
        """
        resource = super()._infer_from_marker_file(directory, marker_file)

        if resource and 'agent_type' not in resource.config_data:
            # Default to GENERAL_PURPOSE if not specified
            resource.config_data['agent_type'] = 'general'

        return resource


class PromptDetector(BaseResourceDetector):
    """Detector for PROMPT resources."""

    MARKER_FILE = "PROMPT.md"

    def get_resource_type(self) -> ResourceType:
        return ResourceType.PROMPT

    def _needs_entry_point(self) -> bool:
        """Prompts are templates, don't need Python entry points."""
        return False

    def _infer_from_marker_file(
        self,
        directory: Path,
        marker_file: Path
    ) -> Optional[DiscoveredResource]:
        """
        Prompts need template extraction.
        """
        resource = super()._infer_from_marker_file(directory, marker_file)

        if resource:
            # Extract template from PROMPT.md or separate template file
            template = self._extract_template(directory, marker_file)
            if template:
                resource.config_data['template'] = template

                # Extract variables from template
                variables = re.findall(r'\{(\w+)\}', template)
                resource.config_data['variables'] = list(set(variables))

        return resource

    def _extract_template(self, directory: Path, marker_file: Path) -> Optional[str]:
        """Extract prompt template from files."""
        # Priority 1: Separate template file
        template_files = ['template.txt', 'template.md', 'prompt.txt']
        for filename in template_files:
            template_path = directory / filename
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()

        # Priority 2: Extract from PROMPT.md
        with open(marker_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Look for template section
            template_match = re.search(
                r'##\s+Template[\s:]*\n+```(?:\w+)?\n(.+?)\n```',
                content,
                re.DOTALL | re.IGNORECASE
            )
            if template_match:
                return template_match.group(1).strip()

            # If no template section, look for first code block
            code_match = re.search(r'```(?:\w+)?\n(.+?)\n```', content, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()

        return None


class ResourceScanner:
    """
    Main resource scanner that discovers Skills, Commands, Agents, and Prompts.

    Scans conventional directory structures and auto-discovers resources,
    making YAML configuration optional.

    Directory structure:
        skills/         - SKILL resources
        commands/       - COMMAND resources
        agents/         - AGENT resources
        prompts/        - PROMPT resources

    Discovery methods (priority order):
        1. Explicit YAML files
        2. Directory convention with marker files (SKILL.md, COMMAND.md, etc.)
        3. Python modules (__init__.py)
    """

    def __init__(self):
        """Initialize the resource scanner."""
        self.detectors = {
            'skills': SkillDetector,
            'commands': CommandDetector,
            'agents': AgentDetector,
            'prompts': PromptDetector
        }

    def scan_all(
        self,
        base_path: Path,
        source: str = "project"
    ) -> Dict[ResourceType, List[DiscoveredResource]]:
        """
        Scan all resource directories.

        Args:
            base_path: Base directory containing resource subdirectories
            source: Source level ("builtin", "user", or "project")

        Returns:
            Dictionary mapping ResourceType to list of discovered resources
        """
        results = {
            ResourceType.SKILL: [],
            ResourceType.COMMAND: [],
            ResourceType.AGENT: [],
            ResourceType.PROMPT: []
        }

        for dir_name, detector_class in self.detectors.items():
            resource_dir = base_path / dir_name
            if resource_dir.exists():
                detector = detector_class(source)
                discovered = detector.scan_directory(resource_dir)
                resource_type = detector.get_resource_type()
                results[resource_type].extend(discovered)

                logger.info(
                    f"Scanned {resource_dir}: found {len(discovered)} "
                    f"{resource_type.value}(s)"
                )

        total = sum(len(items) for items in results.values())
        logger.info(f"Total resources discovered in {base_path}: {total}")

        return results

    def scan_type(
        self,
        base_path: Path,
        resource_type: ResourceType,
        source: str = "project"
    ) -> List[DiscoveredResource]:
        """
        Scan a specific resource type directory.

        Args:
            base_path: Base directory
            resource_type: Type of resource to scan
            source: Source level

        Returns:
            List of discovered resources
        """
        type_to_dir = {
            ResourceType.SKILL: 'skills',
            ResourceType.COMMAND: 'commands',
            ResourceType.AGENT: 'agents',
            ResourceType.PROMPT: 'prompts'
        }

        type_to_detector = {
            ResourceType.SKILL: SkillDetector,
            ResourceType.COMMAND: CommandDetector,
            ResourceType.AGENT: AgentDetector,
            ResourceType.PROMPT: PromptDetector
        }

        dir_name = type_to_dir.get(resource_type)
        detector_class = type_to_detector.get(resource_type)

        if not dir_name or not detector_class:
            logger.error(f"Unknown resource type: {resource_type}")
            return []

        resource_dir = base_path / dir_name
        if not resource_dir.exists():
            logger.debug(f"Directory does not exist: {resource_dir}")
            return []

        detector = detector_class(source)
        return detector.scan_directory(resource_dir)

    def convert_to_config(
        self,
        discovered: DiscoveredResource
    ) -> Any:
        """
        Convert DiscoveredResource to specific config type.

        Args:
            discovered: Discovered resource

        Returns:
            SkillConfig, CommandConfig, AgentConfig, or PromptConfig
        """
        if discovered.resource_type == ResourceType.SKILL:
            return SkillConfig(
                name=discovered.name,
                type='python' if discovered.entry_point else 'yaml',
                path=discovered.path,
                enabled=discovered.enabled,
                priority=discovered.priority,
                source=discovered.source,
                dependencies=discovered.dependencies,
                backend=discovered.config_data.get('backend', 'claude'),
                config=discovered.config_data
            )

        elif discovered.resource_type == ResourceType.COMMAND:
            return CommandConfig(
                name=discovered.name,
                command=discovered.config_data.get('command'),
                enabled=discovered.enabled,
                priority=discovered.priority,
                source=discovered.source,
                dependencies=discovered.dependencies,
                config=discovered.config_data
            )

        elif discovered.resource_type == ResourceType.AGENT:
            return AgentConfig(
                name=discovered.name,
                agent_type=discovered.config_data.get('agent_type', 'general'),
                enabled=discovered.enabled,
                priority=discovered.priority,
                source=discovered.source,
                dependencies=discovered.dependencies,
                config=discovered.config_data
            )

        elif discovered.resource_type == ResourceType.PROMPT:
            return PromptConfig(
                name=discovered.name,
                template=discovered.config_data.get('template', ''),
                variables=discovered.config_data.get('variables', []),
                enabled=discovered.enabled,
                priority=discovered.priority,
                source=discovered.source,
                dependencies=discovered.dependencies,
                config=discovered.config_data
            )

        else:
            raise ValueError(f"Unknown resource type: {discovered.resource_type}")
