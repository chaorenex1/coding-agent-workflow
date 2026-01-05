"""
Dependency analyzer for task dependency graph management.

Provides:
- Task dependency graph construction
- Topological sorting (Kahn's algorithm)
- Circular dependency detection (DFS)
- Parallel task grouping by levels
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .unified_registry import UnifiedRegistry


logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task with dependencies."""
    namespace: str  # Resource namespace (e.g., "command:git-status")
    request: str    # Original user request
    dependencies: List[str] = field(default_factory=list)  # List of dependency namespaces
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __repr__(self) -> str:
        return f"Task(namespace='{self.namespace}', deps={len(self.dependencies)})"


@dataclass
class ParallelGroup:
    """Group of tasks that can be executed in parallel."""
    level: int  # Execution level (0, 1, 2, ...)
    tasks: List[Task] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"ParallelGroup(level={self.level}, tasks={len(self.tasks)})"


class CyclicDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    pass


class DependencyAnalyzer:
    """
    Analyzer for task dependency graphs.

    Features:
    - Builds dependency graphs from tasks
    - Topological sorting with level grouping
    - Circular dependency detection
    - Parallel task grouping
    """

    def __init__(self, registry: Optional[UnifiedRegistry] = None):
        """
        Initialize dependency analyzer.

        Args:
            registry: Optional UnifiedRegistry for resolving resource dependencies
        """
        self.registry = registry
        logger.debug("DependencyAnalyzer initialized")

    def build_task_graph(self, tasks: List[Task]) -> Dict[str, Set[str]]:
        """
        Build task dependency graph.

        Args:
            tasks: List of tasks

        Returns:
            Adjacency list: {task_namespace: {dep1, dep2, ...}}
        """
        graph = {}

        for task in tasks:
            # Initialize task node
            if task.namespace not in graph:
                graph[task.namespace] = set()

            # Add explicit dependencies from task
            graph[task.namespace].update(task.dependencies)

            # Add dependencies from registry if available
            if self.registry:
                metadata = self.registry.get(task.namespace)
                if metadata and metadata.dependencies:
                    graph[task.namespace].update(metadata.dependencies)

            # Ensure all dependency nodes exist in graph
            for dep in graph[task.namespace]:
                if dep not in graph:
                    graph[dep] = set()

        logger.debug(f"Built task graph with {len(graph)} nodes")
        return graph

    def topological_sort(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """
        Topological sort using Kahn's algorithm with level grouping.

        Returns tasks grouped by execution levels where tasks in the same
        level can be executed in parallel.

        Args:
            graph: Dependency graph {node: {dependencies}}

        Returns:
            List of levels, where each level is a list of task namespaces

        Raises:
            CyclicDependencyError: If circular dependencies detected
        """
        # Calculate in-degrees (number of dependencies each node has)
        in_degree = {node: len(deps) for node, deps in graph.items()}

        # Find all nodes with zero in-degree (no dependencies)
        current_level = [node for node, degree in in_degree.items() if degree == 0]

        if not current_level:
            # No nodes with zero in-degree means there's a cycle
            raise CyclicDependencyError("Circular dependency detected: no nodes with zero in-degree")

        levels = []
        visited_count = 0

        while current_level:
            levels.append(current_level)
            visited_count += len(current_level)
            next_level = []

            # Process all nodes in current level
            for node in current_level:
                # Find all nodes that depend on this node
                for dependent in graph:
                    if node in graph[dependent]:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_level.append(dependent)

            current_level = next_level

        # Check if all nodes were visited (detect cycles)
        if visited_count < len(graph):
            unvisited = [node for node in graph if in_degree[node] > 0]
            raise CyclicDependencyError(f"Circular dependency detected: unvisited nodes {unvisited}")

        logger.debug(f"Topological sort produced {len(levels)} levels")
        return levels

    def detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.

        Args:
            graph: Dependency graph

        Returns:
            List of circular dependency paths (empty if none found)
        """
        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str):
            if node in rec_stack:
                # Found a cycle - extract the cycle path
                cycle_start = rec_stack.index(node)
                cycle = rec_stack[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.append(node)

            # Visit dependencies
            if node in graph:
                for neighbor in graph[node]:
                    dfs(neighbor)

            rec_stack.pop()

        # Check all nodes
        for node in graph:
            if node not in visited:
                dfs(node)

        if cycles:
            logger.warning(f"Detected {len(cycles)} circular dependencies")
            for cycle in cycles:
                logger.warning(f"  Cycle: {' → '.join(cycle)}")

        return cycles

    def group_parallel_tasks(self, tasks: List[Task]) -> List[ParallelGroup]:
        """
        Group tasks into parallel execution groups.

        Tasks in the same group have no dependencies on each other and
        can be executed in parallel.

        Args:
            tasks: List of tasks to group

        Returns:
            List of ParallelGroups ordered by dependency levels

        Raises:
            CyclicDependencyError: If circular dependencies detected
        """
        if not tasks:
            return []

        # Build dependency graph
        graph = self.build_task_graph(tasks)

        # Check for cycles first
        cycles = self.detect_cycles(graph)
        if cycles:
            cycle_str = '; '.join([' → '.join(cycle) for cycle in cycles])
            raise CyclicDependencyError(f"Circular dependencies detected: {cycle_str}")

        # Perform topological sort to get levels
        try:
            levels = self.topological_sort(graph)
        except CyclicDependencyError as e:
            # Re-raise with more context
            raise CyclicDependencyError(f"Failed to group tasks: {e}")

        # Create task lookup
        task_lookup = {task.namespace: task for task in tasks}

        # Convert levels to ParallelGroups
        groups = []
        for level_index, level_namespaces in enumerate(levels):
            group = ParallelGroup(level=level_index)

            for namespace in level_namespaces:
                if namespace in task_lookup:
                    group.tasks.append(task_lookup[namespace])

            if group.tasks:
                groups.append(group)

        logger.info(f"Grouped {len(tasks)} tasks into {len(groups)} parallel groups")
        for group in groups:
            logger.debug(f"  Level {group.level}: {len(group.tasks)} tasks")

        return groups

    def validate_dependencies(self, tasks: List[Task]) -> List[str]:
        """
        Validate that all task dependencies can be resolved.

        Args:
            tasks: List of tasks to validate

        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        task_namespaces = {task.namespace for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                # Check if dependency exists in tasks
                if dep not in task_namespaces:
                    # Check if dependency exists in registry (if registry available)
                    if not self.registry or not self.registry.exists(dep):
                        errors.append(f"Task '{task.namespace}' depends on unknown resource '{dep}'")

        return errors

    def get_dependency_depth(self, graph: Dict[str, Set[str]], node: str) -> int:
        """
        Calculate the dependency depth for a node.

        Depth is the longest path from this node to a leaf (node with no dependencies).

        Args:
            graph: Dependency graph
            node: Node to calculate depth for

        Returns:
            Dependency depth (0 if no dependencies)
        """
        if node not in graph or not graph[node]:
            return 0

        max_depth = 0
        for dep in graph[node]:
            depth = self.get_dependency_depth(graph, dep)
            max_depth = max(max_depth, depth + 1)

        return max_depth

    def get_execution_order(self, tasks: List[Task]) -> List[str]:
        """
        Get a valid execution order for tasks (flattened topological sort).

        Args:
            tasks: List of tasks

        Returns:
            List of task namespaces in execution order

        Raises:
            CyclicDependencyError: If circular dependencies detected
        """
        groups = self.group_parallel_tasks(tasks)

        # Flatten groups into single list
        execution_order = []
        for group in groups:
            execution_order.extend([task.namespace for task in group.tasks])

        return execution_order

    def get_independent_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Get all tasks with no dependencies (can start immediately).

        Args:
            tasks: List of tasks

        Returns:
            List of independent tasks
        """
        independent = []

        for task in tasks:
            # Check if task has any dependencies
            has_deps = bool(task.dependencies)

            # Also check registry if available
            if not has_deps and self.registry:
                metadata = self.registry.get(task.namespace)
                if metadata and metadata.dependencies:
                    has_deps = True

            if not has_deps:
                independent.append(task)

        logger.debug(f"Found {len(independent)}/{len(tasks)} independent tasks")
        return independent

    def get_stats(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Get statistics about task dependencies.

        Args:
            tasks: List of tasks

        Returns:
            Dictionary with statistics
        """
        graph = self.build_task_graph(tasks)

        total_deps = sum(len(deps) for deps in graph.values())
        max_depth = max((self.get_dependency_depth(graph, node) for node in graph), default=0)

        independent = self.get_independent_tasks(tasks)

        return {
            "total_tasks": len(tasks),
            "total_dependencies": total_deps,
            "max_dependency_depth": max_depth,
            "independent_tasks": len(independent),
            "has_cycles": bool(self.detect_cycles(graph)),
        }

    def __repr__(self) -> str:
        return f"DependencyAnalyzer(registry={'available' if self.registry else 'none'})"
