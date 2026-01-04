"""
Parallel scheduler for concurrent task execution.

Provides:
- ThreadPoolExecutor-based parallel execution
- Layered execution (respecting dependencies)
- Timeout control per task
- Error isolation and result collection
"""

import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import logging

from .dependency_analyzer import Task, ParallelGroup, DependencyAnalyzer
from .executor_factory import ExecutorFactory


logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of a single task execution."""
    namespace: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        status = "✓" if self.success else "✗"
        return f"TaskResult({status} {self.namespace}, {self.duration_seconds:.2f}s)"


@dataclass
class BatchResult:
    """Result of a batch of tasks."""
    total_tasks: int
    successful: int
    failed: int
    total_duration_seconds: float
    task_results: List[TaskResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        if self.total_tasks == 0:
            return 0.0
        return self.successful / self.total_tasks

    def __repr__(self) -> str:
        return (f"BatchResult(total={self.total_tasks}, "
                f"✓{self.successful} ✗{self.failed}, "
                f"{self.total_duration_seconds:.2f}s, "
                f"success_rate={self.success_rate:.1%})")


class ParallelScheduler:
    """
    Scheduler for parallel task execution.

    Features:
    - ThreadPoolExecutor-based parallelism
    - Layered execution (respecting dependencies)
    - Per-task timeout control
    - Error isolation (one task failure doesn't stop others)
    - Detailed result collection
    """

    def __init__(
        self,
        factory: ExecutorFactory,
        max_workers: int = 3,
        timeout_per_task: int = 120,
        fail_fast: bool = False
    ):
        """
        Initialize parallel scheduler.

        Args:
            factory: ExecutorFactory for creating executors
            max_workers: Maximum number of parallel workers
            timeout_per_task: Timeout per task in seconds
            fail_fast: If True, stop execution on first failure
        """
        self.factory = factory
        self.max_workers = max_workers
        self.timeout_per_task = timeout_per_task
        self.fail_fast = fail_fast

        logger.debug(f"ParallelScheduler initialized: max_workers={max_workers}, "
                    f"timeout={timeout_per_task}s, fail_fast={fail_fast}")

    def execute_parallel_groups(
        self,
        groups: List[ParallelGroup],
        fail_fast: Optional[bool] = None
    ) -> BatchResult:
        """
        Execute parallel groups in order.

        Groups are executed sequentially (respecting dependency levels),
        but tasks within each group are executed in parallel.

        Args:
            groups: List of ParallelGroups ordered by dependency levels
            fail_fast: Override instance fail_fast setting

        Returns:
            BatchResult with execution results
        """
        if fail_fast is None:
            fail_fast = self.fail_fast

        all_results = []
        start_time = time.time()
        total_tasks = sum(len(group.tasks) for group in groups)

        logger.info(f"Starting execution of {total_tasks} tasks in {len(groups)} groups")

        for group_index, group in enumerate(groups):
            logger.info(f"Executing group {group_index} (level {group.level}): {len(group.tasks)} tasks")

            # Execute tasks in this group in parallel
            group_results = self._execute_group(group)
            all_results.extend(group_results)

            # Check for failures
            failed_count = sum(1 for r in group_results if not r.success)

            if failed_count > 0:
                logger.warning(f"Group {group_index} had {failed_count} failures")

                if fail_fast:
                    logger.warning("Fail-fast enabled, stopping execution")
                    # Mark remaining tasks as skipped
                    remaining_tasks = sum(len(g.tasks) for g in groups[group_index + 1:])
                    logger.info(f"Skipping {remaining_tasks} remaining tasks")
                    break

        total_duration = time.time() - start_time

        # Aggregate results
        successful = sum(1 for r in all_results if r.success)
        failed = sum(1 for r in all_results if not r.success)

        batch_result = BatchResult(
            total_tasks=len(all_results),
            successful=successful,
            failed=failed,
            total_duration_seconds=round(total_duration, 3),
            task_results=all_results,
            metadata={
                "groups_executed": len(groups),
                "fail_fast": fail_fast,
                "max_workers": self.max_workers
            }
        )

        logger.info(f"Batch execution completed: {batch_result}")
        return batch_result

    def _execute_group(self, group: ParallelGroup) -> List[TaskResult]:
        """
        Execute tasks in a group in parallel.

        Args:
            group: ParallelGroup to execute

        Returns:
            List of TaskResults
        """
        if not group.tasks:
            return []

        if len(group.tasks) == 1:
            # Single task - execute directly (no thread overhead)
            result = self._execute_task_with_timeout(group.tasks[0])
            return [result]

        # Multiple tasks - execute in parallel
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._execute_task_with_timeout, task): task
                for task in group.tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]

                try:
                    result = future.result(timeout=self.timeout_per_task)
                    results.append(result)

                except TimeoutError:
                    logger.error(f"Task {task.namespace} timed out after {self.timeout_per_task}s")
                    results.append(TaskResult(
                        namespace=task.namespace,
                        success=False,
                        output=None,
                        error=f"Task timeout after {self.timeout_per_task}s",
                        duration_seconds=self.timeout_per_task,
                        executed_at=datetime.now()
                    ))

                except Exception as e:
                    logger.error(f"Task {task.namespace} raised exception: {e}")
                    results.append(TaskResult(
                        namespace=task.namespace,
                        success=False,
                        output=None,
                        error=str(e),
                        duration_seconds=0,
                        executed_at=datetime.now()
                    ))

        return results

    def _execute_task_with_timeout(self, task: Task) -> TaskResult:
        """
        Execute a single task with error isolation.

        Args:
            task: Task to execute

        Returns:
            TaskResult
        """
        start_time = time.time()
        executed_at = datetime.now()

        logger.debug(f"Executing task: {task.namespace}")

        try:
            # Get executor from factory
            executor = self.factory.create_executor(task.namespace)

            if not executor:
                raise ValueError(f"No executor found for namespace: {task.namespace}")

            # Execute task
            output = executor.execute(task.request)

            duration = time.time() - start_time

            logger.debug(f"Task {task.namespace} completed in {duration:.2f}s")

            return TaskResult(
                namespace=task.namespace,
                success=True,
                output=output,
                error=None,
                duration_seconds=round(duration, 3),
                executed_at=executed_at,
                metadata=task.metadata
            )

        except Exception as e:
            duration = time.time() - start_time

            logger.error(f"Task {task.namespace} failed after {duration:.2f}s: {e}")

            return TaskResult(
                namespace=task.namespace,
                success=False,
                output=None,
                error=str(e),
                duration_seconds=round(duration, 3),
                executed_at=executed_at,
                metadata=task.metadata
            )

    def execute_tasks(
        self,
        tasks: List[Task],
        enable_dependency_analysis: bool = True
    ) -> BatchResult:
        """
        Execute a list of tasks (with optional dependency analysis).

        Args:
            tasks: List of tasks to execute
            enable_dependency_analysis: If True, analyze dependencies and group tasks

        Returns:
            BatchResult
        """
        if not tasks:
            return BatchResult(
                total_tasks=0,
                successful=0,
                failed=0,
                total_duration_seconds=0.0
            )

        if enable_dependency_analysis:
            # Analyze dependencies and create parallel groups
            analyzer = DependencyAnalyzer(self.factory.registry)

            try:
                groups = analyzer.group_parallel_tasks(tasks)
                return self.execute_parallel_groups(groups)

            except Exception as e:
                logger.error(f"Dependency analysis failed: {e}")
                logger.info("Falling back to sequential execution")
                # Fall through to sequential execution

        # Sequential execution (no dependency analysis)
        logger.info(f"Executing {len(tasks)} tasks sequentially")

        # Create a single group with all tasks
        single_group = ParallelGroup(level=0, tasks=tasks)
        return self.execute_parallel_groups([single_group])

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.

        Returns:
            Dictionary with statistics
        """
        cache_stats = self.factory.get_cache_stats()

        return {
            "max_workers": self.max_workers,
            "timeout_per_task": self.timeout_per_task,
            "fail_fast": self.fail_fast,
            "cached_executors": cache_stats["cached_executors"]
        }

    def __repr__(self) -> str:
        return f"ParallelScheduler(workers={self.max_workers}, timeout={self.timeout_per_task}s)"


def execute_tasks_parallel(
    tasks: List[Task],
    factory: ExecutorFactory,
    max_workers: int = 3,
    timeout_per_task: int = 120,
    enable_dependency_analysis: bool = True,
    fail_fast: bool = False
) -> BatchResult:
    """
    Convenience function to execute tasks in parallel.

    Args:
        tasks: List of tasks to execute
        factory: ExecutorFactory instance
        max_workers: Maximum parallel workers
        timeout_per_task: Timeout per task in seconds
        enable_dependency_analysis: Enable dependency analysis
        fail_fast: Stop on first failure

    Returns:
        BatchResult
    """
    scheduler = ParallelScheduler(
        factory=factory,
        max_workers=max_workers,
        timeout_per_task=timeout_per_task,
        fail_fast=fail_fast
    )

    return scheduler.execute_tasks(
        tasks=tasks,
        enable_dependency_analysis=enable_dependency_analysis
    )
