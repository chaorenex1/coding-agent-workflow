"""
Resource Scanner V2 - Hierarchical Category Support

Enhanced resource scanner supporting categorized directory structures:
- commands/category/resource.md
- agents/category/resource.md
- skills/skill-name/SKILL.md
- prompts/resource.md (flat or categorized)

Key improvements:
1. Recursive scanning with configurable depth
2. Category extraction from directory structure
3. Flexible layout modes (flat file, categorized file, directory-based)
4. Backward compatible with V1 API
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml

from .config_loader import ResourceType, SkillConfig, CommandConfig, AgentConfig, PromptConfig


logger = logging.getLogger(__name__)


class ResourceLayout(Enum):
    """Resource organization layout in filesystem."""
    FLAT_FILE = "flat_file"                      # resource.md in root
    CATEGORIZED_FILE = "categorized_file"        # category/resource.md
    DIRECTORY_BASED = "directory_based"          # resource-dir/MARKER.md + code


@dataclass
class ResourceCategory:
    """Category metadata for resource organization."""
    name: str                           # category directory name
    display_name: str                   # human-readable name
    description: str = ""               # category description
    priority: int = 50                  # category priority
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_directory_name(cls, dir_name: str) -> 'ResourceCategory':
        """Create category from directory name."""
        # Convert kebab-case to Title Case
        display = dir_name.replace('-', ' ').replace('_', ' ').title()
        return cls(name=dir_name, display_name=display)


@dataclass
class DiscoveredResource:
    """
    Unified data structure for discovered resources.

    Enhanced with category support for hierarchical organization.
    """
    name: str
    resource_type: ResourceType
    path: Path
    source: str  # "builtin", "user", or "project"

    # Discovery metadata
    discovery_method: str  # "yaml_file", "directory_convention", "markdown_file", "python_module"
    marker_file: Optional[Path] = None  # SKILL.md, COMMAND.md, etc.
    entry_point: Optional[Path] = None  # main.py, __init__.py, etc.

    # Categorization (NEW)
    category: Optional[str] = None      # category name (e.g., "project-analyzer")
    layout: Optional[ResourceLayout] = None  # layout mode

    # Extracted metadata
    description: str = ""
    enabled: bool = True
    priority: int = 50
    dependencies: List[str] = field(default_factory=list)

    # Type-specific data
    config_data: Dict[str, Any] = field(default_factory=dict)

    # Relative path from resource root (NEW)
    relative_path: Optional[Path] = None

    def __repr__(self) -> str:
        cat_str = f", category={self.category}" if self.category else ""
        return (f"DiscoveredResource({self.resource_type.value}:{self.name}{cat_str}, "
                f"method={self.discovery_method}, source={self.source})")


class BaseResourceDetector:
    """
    Base class for resource type detectors.

    V2 enhancements:
    - Recursive scanning with configurable depth
    - Category extraction from directory structure
    - Layout-specific scanning strategies
    """

    MARKER_FILE: str = None  # Override in subclass (e.g., "SKILL.md")
    LAYOUT: ResourceLayout = ResourceLayout.FLAT_FILE  # Default layout
    MAX_DEPTH: int = 1  # Default scan depth

    def __init__(self, source: str):
        """
        Initialize detector.

        Args:
            source: Resource source level ("builtin", "user", or "project")
        """
        self.source = source
        self.priority_map = {"builtin": 10, "user": 50, "project": 100}

    def scan_directory(
        self,
        directory: Path,
        max_depth: Optional[int] = None
    ) -> List[DiscoveredResource]:
        """
        Scan directory and discover resources.

        Args:
            directory: Directory to scan
            max_depth: Maximum scan depth (None = use class default)
                - 1: Flat scan (only direct children)
                - 2: Category scan (category/resource)
                - 3+: Deep recursive scan

        Returns:
            List of discovered resources
        """
        if not directory.exists():
            logger.debug(f"Directory does not exist: {directory}")
            return []

        if max_depth is None:
            max_depth = self.MAX_DEPTH

        logger.info(f"Scanning {directory} (depth={max_depth}, layout={self.LAYOUT.value})")
        discovered = self._scan_recursive(directory, depth=0, max_depth=max_depth)
        logger.info(f"Discovered {len(discovered)} {self.get_resource_type().value}s in {directory}")

        return discovered

    def _scan_recursive(
        self,
        directory: Path,
        depth: int,
        max_depth: int,
        category: Optional[str] = None
    ) -> List[DiscoveredResource]:
        """
        Recursively scan directory for resources.

        Args:
            directory: Current directory
            depth: Current depth (0-based)
            max_depth: Maximum depth to scan
            category: Current category name (if in category directory)

        Returns:
            List of discovered resources
        """
        discovered = []

        try:
            for item in directory.iterdir():
                # Skip hidden files and cache
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue

                try:
                    resources = self._scan_item(item, depth, max_depth, category)
                    discovered.extend(resources)
                except Exception as e:
                    logger.warning(f"Failed to scan {item}: {e}")

        except PermissionError as e:
            logger.error(f"Permission denied accessing {directory}: {e}")

        return discovered

    def _scan_item(
        self,
        item: Path,
        depth: int,
        max_depth: int,
        category: Optional[str]
    ) -> List[DiscoveredResource]:
        """
        Scan a single item (file or directory).

        Override this method in subclasses for layout-specific logic.
        """
        # Default implementation (flat file scan)
        if item.is_file() and item.suffix == '.yaml':
            resource = self._detect_from_yaml_file(item)
            if resource:
                resource.category = category
                return [resource]

        return []

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
                layout=ResourceLayout.FLAT_FILE,
                description=data.get('description', ''),
                enabled=data.get('enabled', True),
                priority=data.get('priority', self.priority_map[self.source]),
                dependencies=data.get('dependencies', []),
                config_data=data
            )
        except Exception as e:
            logger.error(f"Failed to parse YAML file {yaml_file}: {e}")
            return None

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


class CommandDetector(BaseResourceDetector):
    """
    Detector for COMMAND resources.

    Layout: CATEGORIZED_FILE
    Structure: commands/category/command.md
    Depth: 2 (category + resource)
    """

    MARKER_FILE = "COMMAND.md"
    LAYOUT = ResourceLayout.CATEGORIZED_FILE
    MAX_DEPTH = 2

    def get_resource_type(self) -> ResourceType:
        return ResourceType.COMMAND

    def _scan_item(
        self,
        item: Path,
        depth: int,
        max_depth: int,
        category: Optional[str]
    ) -> List[DiscoveredResource]:
        """Scan for categorized command files."""

        if depth == 0:
            # First level: category directories or flat files
            if item.is_dir() and depth + 1 < max_depth:
                # Category directory
                category_name = item.name
                return self._scan_recursive(item, depth + 1, max_depth, category_name)

            elif item.is_file() and item.suffix == '.md':
                # Flat file (no category)
                resource = self._detect_from_markdown_file(item, category=None)
                return [resource] if resource else []

        elif depth == 1:
            # Second level: resource files
            if item.is_file() and item.suffix == '.md':
                resource = self._detect_from_markdown_file(item, category=category)
                return [resource] if resource else []

        return []

    def _detect_from_markdown_file(
        self,
        file_path: Path,
        category: Optional[str]
    ) -> Optional[DiscoveredResource]:
        """Detect command from .md file."""
        try:
            metadata = self._parse_markdown_metadata(file_path)

            # Resource name: from filename (without .md)
            resource_name = file_path.stem

            # Extract shell command from markdown
            if 'command' not in metadata:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for code blocks
                    code_match = re.search(r'```(?:bash|sh|shell)\n(.+?)\n```', content, re.DOTALL)
                    if code_match:
                        metadata['command'] = code_match.group(1).strip()

            return DiscoveredResource(
                name=resource_name,
                resource_type=ResourceType.COMMAND,
                path=file_path,
                source=self.source,
                category=category,
                layout=ResourceLayout.CATEGORIZED_FILE,
                discovery_method="markdown_file",
                description=metadata.get('description', ''),
                enabled=metadata.get('enabled', True),
                priority=metadata.get('priority', self.priority_map[self.source]),
                dependencies=metadata.get('dependencies', []),
                config_data=metadata
            )
        except Exception as e:
            logger.error(f"Failed to detect command from {file_path}: {e}")
            return None


class AgentDetector(BaseResourceDetector):
    """
    Detector for AGENT resources.

    Layout: CATEGORIZED_FILE
    Structure: agents/category/agent.md
    Depth: 2 (category + resource)
    """

    MARKER_FILE = "AGENT.md"
    LAYOUT = ResourceLayout.CATEGORIZED_FILE
    MAX_DEPTH = 2

    def get_resource_type(self) -> ResourceType:
        return ResourceType.AGENT

    def _scan_item(
        self,
        item: Path,
        depth: int,
        max_depth: int,
        category: Optional[str]
    ) -> List[DiscoveredResource]:
        """Scan for categorized agent files (same logic as commands)."""

        if depth == 0:
            if item.is_dir() and depth + 1 < max_depth:
                category_name = item.name
                return self._scan_recursive(item, depth + 1, max_depth, category_name)
            elif item.is_file() and item.suffix == '.md':
                resource = self._detect_from_markdown_file(item, category=None)
                return [resource] if resource else []

        elif depth == 1:
            if item.is_file() and item.suffix == '.md':
                resource = self._detect_from_markdown_file(item, category=category)
                return [resource] if resource else []

        return []

    def _detect_from_markdown_file(
        self,
        file_path: Path,
        category: Optional[str]
    ) -> Optional[DiscoveredResource]:
        """Detect agent from .md file."""
        try:
            metadata = self._parse_markdown_metadata(file_path)

            resource_name = file_path.stem

            # Default agent_type if not specified
            if 'agent_type' not in metadata:
                metadata['agent_type'] = 'general'

            return DiscoveredResource(
                name=resource_name,
                resource_type=ResourceType.AGENT,
                path=file_path,
                source=self.source,
                category=category,
                layout=ResourceLayout.CATEGORIZED_FILE,
                discovery_method="markdown_file",
                description=metadata.get('description', ''),
                enabled=metadata.get('enabled', True),
                priority=metadata.get('priority', self.priority_map[self.source]),
                dependencies=metadata.get('dependencies', []),
                config_data=metadata
            )
        except Exception as e:
            logger.error(f"Failed to detect agent from {file_path}: {e}")
            return None


class PromptDetector(BaseResourceDetector):
    """
    Detector for PROMPT resources.

    Layout: FLAT_FILE or CATEGORIZED_FILE (hybrid)
    Structure: prompts/prompt.md OR prompts/category/prompt.md
    Depth: 2 (support both flat and categorized)
    """

    MARKER_FILE = "PROMPT.md"
    LAYOUT = ResourceLayout.FLAT_FILE
    MAX_DEPTH = 2

    def get_resource_type(self) -> ResourceType:
        return ResourceType.PROMPT

    def _scan_item(
        self,
        item: Path,
        depth: int,
        max_depth: int,
        category: Optional[str]
    ) -> List[DiscoveredResource]:
        """Scan for both flat and categorized prompts."""

        if item.is_file() and item.suffix == '.md':
            # Markdown file at any level
            resource = self._detect_from_markdown_file(item, category=category)
            return [resource] if resource else []

        elif item.is_dir() and depth + 1 < max_depth:
            # Potential category directory
            category_name = item.name
            return self._scan_recursive(item, depth + 1, max_depth, category_name)

        return []

    def _detect_from_markdown_file(
        self,
        file_path: Path,
        category: Optional[str]
    ) -> Optional[DiscoveredResource]:
        """Detect prompt from .md file."""
        try:
            metadata = self._parse_markdown_metadata(file_path)

            resource_name = file_path.stem

            # Extract template from file content
            if 'template' not in metadata:
                template = self._extract_template(file_path)
                if template:
                    metadata['template'] = template

                    # Extract variables from template
                    variables = re.findall(r'\{(\w+)\}', template)
                    metadata['variables'] = list(set(variables))

            return DiscoveredResource(
                name=resource_name,
                resource_type=ResourceType.PROMPT,
                path=file_path,
                source=self.source,
                category=category,
                layout=ResourceLayout.CATEGORIZED_FILE if category else ResourceLayout.FLAT_FILE,
                discovery_method="markdown_file",
                description=metadata.get('description', ''),
                enabled=metadata.get('enabled', True),
                priority=metadata.get('priority', self.priority_map[self.source]),
                dependencies=metadata.get('dependencies', []),
                config_data=metadata
            )
        except Exception as e:
            logger.error(f"Failed to detect prompt from {file_path}: {e}")
            return None

    def _extract_template(self, file_path: Path) -> Optional[str]:
        """Extract prompt template from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove YAML front matter if exists
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2]

            # Look for template section
            template_match = re.search(
                r'##\s+Template[\s:]*\n+```(?:\w+)?\n(.+?)\n```',
                content,
                re.DOTALL | re.IGNORECASE
            )
            if template_match:
                return template_match.group(1).strip()

            # If no template section, use entire content (after front matter)
            return content.strip()

        except Exception as e:
            logger.error(f"Failed to extract template from {file_path}: {e}")
            return None


class SkillDetector(BaseResourceDetector):
    """
    Detector for SKILL resources.

    Layout: DIRECTORY_BASED
    Structure: skills/skill-name/SKILL.md + Python code
    Depth: 1 (only scan direct subdirectories as skills)
    """

    MARKER_FILE = "SKILL.md"
    LAYOUT = ResourceLayout.DIRECTORY_BASED
    MAX_DEPTH = 1

    def get_resource_type(self) -> ResourceType:
        return ResourceType.SKILL

    def _scan_item(
        self,
        item: Path,
        depth: int,
        max_depth: int,
        category: Optional[str]
    ) -> List[DiscoveredResource]:
        """Scan for skill directories."""

        if item.is_dir():
            # Check if this directory is a skill (contains SKILL.md)
            marker = item / self.MARKER_FILE
            if marker.exists():
                resource = self._detect_from_skill_directory(item, category=category)
                return [resource] if resource else []

        return []

    def _detect_from_skill_directory(
        self,
        skill_dir: Path,
        category: Optional[str]
    ) -> Optional[DiscoveredResource]:
        """Detect skill from directory with SKILL.md."""
        try:
            marker_file = skill_dir / self.MARKER_FILE

            # Parse SKILL.md
            metadata = self._parse_markdown_metadata(marker_file)

            # Find entry point
            entry_point = self._find_entry_point(skill_dir)

            # Resource name from directory name or metadata
            resource_name = metadata.get('name', skill_dir.name)

            return DiscoveredResource(
                name=resource_name,
                resource_type=ResourceType.SKILL,
                path=skill_dir,
                source=self.source,
                category=category,
                layout=ResourceLayout.DIRECTORY_BASED,
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
            logger.error(f"Failed to detect skill from {skill_dir}: {e}")
            return None


class ResourceScanner:
    """
    Main resource scanner V2 with hierarchical category support.

    Discovers Skills, Commands, Agents, and Prompts from conventional
    directory structures, automatically extracting category information.

    Directory structure:
        skills/         - SKILL resources (directory-based)
        commands/       - COMMAND resources (categorized files)
        agents/         - AGENT resources (categorized files)
        prompts/        - PROMPT resources (flat or categorized files)
    """

    def __init__(self):
        """Initialize the resource scanner."""
        self.detectors = {
            'skills': SkillDetector,
            'commands': CommandDetector,
            'agents': AgentDetector,
            'prompts': PromptDetector
        }
        self._cache: Dict[Tuple[str, ResourceType], List[DiscoveredResource]] = {}
        self._cache_timestamp: Dict[Tuple[str, ResourceType], float] = {}

    def scan_all(
        self,
        base_path: Path,
        source: str = "project",
        use_cache: bool = True
    ) -> Dict[ResourceType, List[DiscoveredResource]]:
        """
        Scan all resource directories.

        Args:
            base_path: Base directory containing resource subdirectories
            source: Source level ("builtin", "user", or "project")
            use_cache: Whether to use cached results

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

    def get_categories(
        self,
        base_path: Path,
        resource_type: ResourceType
    ) -> List[ResourceCategory]:
        """
        Get all categories for a resource type.

        Args:
            base_path: Base directory
            resource_type: Type of resource

        Returns:
            List of ResourceCategory objects
        """
        resources = self.scan_type(base_path, resource_type)

        # Extract unique categories
        category_names = set(r.category for r in resources if r.category)

        # Build category objects
        categories = []
        for cat_name in sorted(category_names):
            # Check for _category.yaml metadata
            cat_metadata = self._load_category_metadata(base_path, resource_type, cat_name)

            if cat_metadata:
                category = ResourceCategory(
                    name=cat_name,
                    display_name=cat_metadata.get('display_name', cat_name),
                    description=cat_metadata.get('description', ''),
                    priority=cat_metadata.get('priority', 50),
                    metadata=cat_metadata
                )
            else:
                # Infer from directory name
                category = ResourceCategory.from_directory_name(cat_name)

            categories.append(category)

        return categories

    def _load_category_metadata(
        self,
        base_path: Path,
        resource_type: ResourceType,
        category_name: str
    ) -> Optional[Dict[str, Any]]:
        """Load category metadata from _category.yaml if exists."""
        type_to_dir = {
            ResourceType.SKILL: 'skills',
            ResourceType.COMMAND: 'commands',
            ResourceType.AGENT: 'agents',
            ResourceType.PROMPT: 'prompts'
        }

        dir_name = type_to_dir.get(resource_type)
        if not dir_name:
            return None

        category_file = base_path / dir_name / category_name / "_category.yaml"
        if not category_file.exists():
            return None

        try:
            with open(category_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load category metadata {category_file}: {e}")
            return None

    def scan_category(
        self,
        base_path: Path,
        resource_type: ResourceType,
        category: str,
        source: str = "project"
    ) -> List[DiscoveredResource]:
        """
        Scan resources in a specific category.

        Args:
            base_path: Base directory
            resource_type: Type of resource
            category: Category name
            source: Source level

        Returns:
            List of discovered resources in the category
        """
        all_resources = self.scan_type(base_path, resource_type, source)
        return [r for r in all_resources if r.category == category]

    def get_resource_tree(
        self,
        base_path: Path,
        resource_type: ResourceType,
        source: str = "project"
    ) -> Dict[Optional[str], List[DiscoveredResource]]:
        """
        Get resource tree organized by category.

        Args:
            base_path: Base directory
            resource_type: Type of resource
            source: Source level

        Returns:
            Dictionary mapping category name to list of resources
            (None key for uncategorized resources)
        """
        all_resources = self.scan_type(base_path, resource_type, source)

        tree: Dict[Optional[str], List[DiscoveredResource]] = {}
        for resource in all_resources:
            category = resource.category
            if category not in tree:
                tree[category] = []
            tree[category].append(resource)

        return tree

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
                path=discovered.path,
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
                path=discovered.path,
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
                path=discovered.path,
                enabled=discovered.enabled,
                priority=discovered.priority,
                source=discovered.source,
                dependencies=discovered.dependencies,
                config=discovered.config_data
            )

        else:
            raise ValueError(f"Unknown resource type: {discovered.resource_type}")
