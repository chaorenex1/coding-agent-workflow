"""
Unified registry for skill/command/agent/prompt resources.

Manages resource registration with namespace isolation, priority handling,
and dependency resolution.
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

from .config_loader import ResourceType, SkillConfig, CommandConfig, AgentConfig, PromptConfig


logger = logging.getLogger(__name__)


@dataclass
class ResourceMetadata:
    """Metadata for a registered resource."""
    name: str
    namespace: str  # Format: "type:name" (e.g., "skill:code-review", "command:git-status")
    type: ResourceType
    source: str  # "builtin", "user", or "project"
    priority: int  # 0-1000, higher = higher priority
    dependencies: List[str] = field(default_factory=list)  # List of namespaces
    config: Dict[str, Any] = field(default_factory=dict)
    path: Optional[Path] = None
    enabled: bool = True

    def __repr__(self) -> str:
        return f"ResourceMetadata(namespace='{self.namespace}', priority={self.priority}, source='{self.source}')"


class UnifiedRegistry:
    """
    Unified registry for all resource types (skills, commands, agents, prompts).

    Features:
    - Namespace isolation (type:name format)
    - Priority-based override for duplicate names
    - Dependency graph management
    - Resource query and search
    """

    def __init__(self):
        """Initialize empty registry."""
        # Main resource storage: {namespace: ResourceMetadata}
        self._resources: Dict[str, ResourceMetadata] = {}

        # Type-based index: {ResourceType: [namespace, ...]}
        self._type_index: Dict[ResourceType, List[str]] = {
            ResourceType.SKILL: [],
            ResourceType.COMMAND: [],
            ResourceType.AGENT: [],
            ResourceType.PROMPT: [],
        }

        # Source-based index: {source: [namespace, ...]}
        self._source_index: Dict[str, List[str]] = {}

        # Dependency graph: {namespace: {dependent_namespace, ...}}
        self._dependency_graph: Dict[str, Set[str]] = {}

        # Reverse dependency graph: {namespace: {namespace_that_depends_on_it, ...}}
        self._reverse_dependency_graph: Dict[str, Set[str]] = {}

        logger.debug("UnifiedRegistry initialized")

    def register(self, metadata: ResourceMetadata, overwrite: bool = False) -> bool:
        """
        Register a resource in the registry.

        Args:
            metadata: Resource metadata to register
            overwrite: If True, always overwrite existing. If False, use priority.

        Returns:
            True if registered (new or overwritten), False if skipped
        """
        namespace = metadata.namespace

        # Check if resource already exists
        if namespace in self._resources:
            existing = self._resources[namespace]

            if not overwrite:
                # Priority-based override
                if metadata.priority > existing.priority:
                    logger.info(f"Overriding {namespace} (priority {existing.priority} → {metadata.priority})")
                    self._unregister_internal(namespace)
                    self._register_internal(metadata)
                    return True
                elif metadata.priority == existing.priority:
                    logger.warning(f"Duplicate {namespace} with same priority {metadata.priority}, "
                                 f"keeping existing from '{existing.source}'")
                    return False
                else:
                    logger.debug(f"Skipping {namespace} (priority {metadata.priority} < {existing.priority})")
                    return False
            else:
                # Force overwrite
                logger.info(f"Force overwriting {namespace}")
                self._unregister_internal(namespace)
                self._register_internal(metadata)
                return True
        else:
            # New resource
            self._register_internal(metadata)
            return True

    def _register_internal(self, metadata: ResourceMetadata):
        """Internal method to register a resource (no conflict checking)."""
        namespace = metadata.namespace

        # Add to main storage
        self._resources[namespace] = metadata

        # Update type index
        if namespace not in self._type_index[metadata.type]:
            self._type_index[metadata.type].append(namespace)

        # Update source index
        if metadata.source not in self._source_index:
            self._source_index[metadata.source] = []
        if namespace not in self._source_index[metadata.source]:
            self._source_index[metadata.source].append(namespace)

        # Update dependency graph
        if metadata.dependencies:
            self._dependency_graph[namespace] = set(metadata.dependencies)

            # Update reverse dependency graph
            for dep in metadata.dependencies:
                if dep not in self._reverse_dependency_graph:
                    self._reverse_dependency_graph[dep] = set()
                self._reverse_dependency_graph[dep].add(namespace)
        else:
            self._dependency_graph[namespace] = set()

        logger.debug(f"Registered {namespace} (type={metadata.type.value}, source={metadata.source}, "
                    f"priority={metadata.priority})")

    def _unregister_internal(self, namespace: str):
        """Internal method to unregister a resource."""
        if namespace not in self._resources:
            return

        metadata = self._resources[namespace]

        # Remove from type index
        if namespace in self._type_index[metadata.type]:
            self._type_index[metadata.type].remove(namespace)

        # Remove from source index
        if metadata.source in self._source_index and namespace in self._source_index[metadata.source]:
            self._source_index[metadata.source].remove(namespace)

        # Remove from dependency graph
        if namespace in self._dependency_graph:
            deps = self._dependency_graph[namespace]
            del self._dependency_graph[namespace]

            # Remove from reverse dependency graph
            for dep in deps:
                if dep in self._reverse_dependency_graph:
                    self._reverse_dependency_graph[dep].discard(namespace)

        # Remove from reverse dependency graph
        if namespace in self._reverse_dependency_graph:
            dependents = self._reverse_dependency_graph[namespace]
            del self._reverse_dependency_graph[namespace]

            # Remove references in dependency graph
            for dependent in dependents:
                if dependent in self._dependency_graph:
                    self._dependency_graph[dependent].discard(namespace)

        # Remove from main storage
        del self._resources[namespace]

        logger.debug(f"Unregistered {namespace}")

    def get(self, namespace: str) -> Optional[ResourceMetadata]:
        """
        Get a resource by namespace.

        Args:
            namespace: Resource namespace (e.g., "skill:code-review")

        Returns:
            ResourceMetadata if found, None otherwise
        """
        return self._resources.get(namespace)

    def exists(self, namespace: str) -> bool:
        """Check if a resource exists."""
        return namespace in self._resources

    def list_resources(self,
                      type_filter: Optional[ResourceType] = None,
                      source_filter: Optional[str] = None,
                      enabled_only: bool = False) -> List[ResourceMetadata]:
        """
        List all resources with optional filtering.

        Args:
            type_filter: Filter by resource type
            source_filter: Filter by source ("builtin", "user", "project")
            enabled_only: Only return enabled resources

        Returns:
            List of ResourceMetadata
        """
        resources = list(self._resources.values())

        # Apply filters
        if type_filter:
            resources = [r for r in resources if r.type == type_filter]

        if source_filter:
            resources = [r for r in resources if r.source == source_filter]

        if enabled_only:
            resources = [r for r in resources if r.enabled]

        return resources

    def resolve_dependencies(self, namespace: str) -> List[str]:
        """
        Resolve dependencies for a resource using topological sort.

        Args:
            namespace: Resource namespace

        Returns:
            List of namespaces in dependency order (dependencies first, then the resource)
        """
        visited = set()
        result = []

        def dfs(ns: str):
            if ns in visited:
                return
            visited.add(ns)

            # Visit dependencies first
            if ns in self._dependency_graph:
                for dep in self._dependency_graph[ns]:
                    dfs(dep)

            result.append(ns)

        dfs(namespace)
        return result

    def get_dependents(self, namespace: str) -> List[str]:
        """
        Get all resources that depend on this resource.

        Args:
            namespace: Resource namespace

        Returns:
            List of namespaces that depend on this resource
        """
        if namespace not in self._reverse_dependency_graph:
            return []
        return list(self._reverse_dependency_graph[namespace])

    def check_circular_dependency(self) -> List[List[str]]:
        """
        Check for circular dependencies in the registry.

        Returns:
            List of circular dependency paths (empty if none found)
        """
        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str):
            if node in rec_stack:
                # Found a cycle
                cycle_start = rec_stack.index(node)
                cycle = rec_stack[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.append(node)

            # Visit dependencies
            if node in self._dependency_graph:
                for neighbor in self._dependency_graph[node]:
                    dfs(neighbor)

            rec_stack.pop()

        # Check all nodes
        for node in self._resources.keys():
            if node not in visited:
                dfs(node)

        return cycles

    def validate_dependencies(self) -> List[str]:
        """
        Validate that all dependencies exist in the registry.

        Returns:
            List of error messages (empty if all valid)
        """
        errors = []

        for namespace, deps in self._dependency_graph.items():
            for dep in deps:
                if dep not in self._resources:
                    errors.append(f"Resource '{namespace}' depends on unknown resource '{dep}'")

        return errors

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_resources": len(self._resources),
            "by_type": {
                resource_type.value: len(namespaces)
                for resource_type, namespaces in self._type_index.items()
            },
            "by_source": {
                source: len(namespaces)
                for source, namespaces in self._source_index.items()
            },
            "with_dependencies": sum(1 for deps in self._dependency_graph.values() if deps),
            "total_dependency_links": sum(len(deps) for deps in self._dependency_graph.values()),
        }

    def clear(self):
        """Clear all registered resources."""
        self._resources.clear()
        for type_list in self._type_index.values():
            type_list.clear()
        self._source_index.clear()
        self._dependency_graph.clear()
        self._reverse_dependency_graph.clear()
        logger.info("Registry cleared")

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"UnifiedRegistry(resources={stats['total_resources']}, by_type={stats['by_type']})"

    def __len__(self) -> int:
        """Return number of registered resources."""
        return len(self._resources)


def create_registry_from_config(config) -> UnifiedRegistry:
    """
    Create and populate a UnifiedRegistry from an OrchestratorConfig.

    Args:
        config: OrchestratorConfig instance

    Returns:
        Populated UnifiedRegistry
    """
    from .config_loader import OrchestratorConfig

    registry = UnifiedRegistry()

    # Register skills
    for name, skill in config.skills.items():
        namespace = f"skill:{name}"
        metadata = ResourceMetadata(
            name=name,
            namespace=namespace,
            type=ResourceType.SKILL,
            source=skill.source,
            priority=skill.priority,
            dependencies=skill.dependencies,
            config=skill.config,
            path=skill.path,
            enabled=skill.enabled
        )
        registry.register(metadata)

    # Register commands
    for name, command in config.commands.items():
        namespace = f"command:{name}"
        metadata = ResourceMetadata(
            name=name,
            namespace=namespace,
            type=ResourceType.COMMAND,
            source=command.source,
            priority=command.priority,
            dependencies=command.dependencies,
            config=command.config,
            path=None,
            enabled=command.enabled
        )
        registry.register(metadata)

    # Register agents
    for name, agent in config.agents.items():
        namespace = f"agent:{name}"
        metadata = ResourceMetadata(
            name=name,
            namespace=namespace,
            type=ResourceType.AGENT,
            source=agent.source,
            priority=agent.priority,
            dependencies=agent.dependencies,
            config=agent.config,
            path=None,
            enabled=agent.enabled
        )
        registry.register(metadata)

    # Register prompts
    for name, prompt in config.prompts.items():
        namespace = f"prompt:{name}"
        metadata = ResourceMetadata(
            name=name,
            namespace=namespace,
            type=ResourceType.PROMPT,
            source=prompt.source,
            priority=prompt.priority,
            dependencies=prompt.dependencies,
            config=prompt.config,
            path=None,
            enabled=prompt.enabled
        )
        registry.register(metadata)

    logger.info(f"Created registry from config: {registry}")

    # Validate dependencies
    errors = registry.validate_dependencies()
    if errors:
        logger.warning(f"Dependency validation found {len(errors)} issues:")
        for error in errors:
            logger.warning(f"  - {error}")

    # Check circular dependencies
    cycles = registry.check_circular_dependency()
    if cycles:
        logger.error(f"Detected {len(cycles)} circular dependencies:")
        for cycle in cycles:
            logger.error(f"  - {' → '.join(cycle)}")

    return registry
