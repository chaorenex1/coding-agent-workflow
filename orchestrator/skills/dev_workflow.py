#!/usr/bin/env python3
"""
DevWorkflowAgent - 多阶段开发工作流自动化

5个阶段：
1. 需求分析 (Requirements Analysis)
2. 功能设计 (Feature Design)
3. UX设计 (UX Design)
4. 开发计划 (Development Plan)
5. 实现 (Implementation)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 导入 BackendOrchestrator（使用相对导入）
from ..core.backend_orchestrator import BackendOrchestrator, TaskResult

# V3 并行执行组件（可选）
try:
    from ..core.dependency_analyzer import DependencyAnalyzer, Task, ParallelGroup
    from ..core.parallel_scheduler import ParallelScheduler, TaskResult as SchedulerTaskResult
    from ..core.executor_factory import ExecutorFactory
    from ..core.unified_registry import UnifiedRegistry
    V3_PARALLEL_AVAILABLE = True
except ImportError:
    DependencyAnalyzer = None
    Task = None
    ParallelGroup = None
    ParallelScheduler = None
    V3_PARALLEL_AVAILABLE = False


class WorkflowStage(Enum):
    """工作流阶段"""
    REQUIREMENTS = "requirements"
    FEATURE_DESIGN = "feature_design"
    UX_DESIGN = "ux_design"
    DEV_PLAN = "dev_plan"
    IMPLEMENTATION = "implementation"


@dataclass
class StageResult:
    """阶段执行结果"""
    stage: WorkflowStage
    success: bool
    output: str
    duration_seconds: float
    run_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None

    def get_summary(self) -> str:
        """获取结果摘要（前500字符）"""
        return self.output[:500] + "..." if len(self.output) > 500 else self.output


@dataclass
class WorkflowResult:
    """完整工作流结果"""
    requirement: str
    stages: List[StageResult]
    total_duration_seconds: float
    success: bool
    completed_stages: int
    failed_stage: Optional[WorkflowStage] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_stage_result(self, stage: WorkflowStage) -> Optional[StageResult]:
        """获取指定阶段的结果"""
        for result in self.stages:
            if result.stage == stage:
                return result
        return None


class StageValidator:
    """阶段验证器 - 确保每个阶段输出符合要求"""

    @staticmethod
    def validate_requirements(output: str) -> Tuple[bool, Optional[str]]:
        """验证需求分析输出"""
        if len(output) < 20:  # 降低最小长度要求
            return False, "需求分析输出过短"
        return True, None

    @staticmethod
    def validate_feature_design(output: str) -> Tuple[bool, Optional[str]]:
        """验证功能设计输出"""
        if len(output) < 20:
            return False, "功能设计输出过短"
        return True, None

    @staticmethod
    def validate_ux_design(output: str) -> Tuple[bool, Optional[str]]:
        """验证UX设计输出"""
        if len(output) < 20:
            return False, "UX设计输出过短"
        return True, None

    @staticmethod
    def validate_dev_plan(output: str) -> Tuple[bool, Optional[str]]:
        """验证开发计划输出"""
        if len(output) < 20:
            return False, "开发计划输出过短"
        return True, None

    @staticmethod
    def validate_implementation(output: str) -> Tuple[bool, Optional[str]]:
        """验证实现输出"""
        if len(output) < 100:
            return False, "实现输出过短"

        return True, None


class DevWorkflowAgent:
    """
    多阶段开发工作流智能体

    自动执行5个阶段的开发流程：
    1. 需求分析 → Claude
    2. 功能设计 → Claude
    3. UX设计 → Gemini
    4. 开发计划 → Codex (deepseek-reasoner)
    5. 实现 → Codex (deepseek-reasoner)
    """

    # 阶段配置
    STAGE_CONFIG = {
        WorkflowStage.REQUIREMENTS: {
            "backend": "claude",
            "validator": StageValidator.validate_requirements,
            "prompt_template": """你是一位产品经理和需求分析专家。请对以下需求进行详细分析：

用户需求：
{requirement}

请提供：
1. 核心需求提炼
2. 用户画像和使用场景
3. 功能优先级排序
4. 成功指标定义
5. 风险和约束条件

请以结构化的方式输出分析结果。"""
        },

        WorkflowStage.FEATURE_DESIGN: {
            "backend": "claude",
            "validator": StageValidator.validate_feature_design,
            "prompt_template": """你是一位软件架构师。基于以下需求分析，设计系统功能架构：

【需求分析】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 功能模块划分
2. 模块间的接口设计
3. 数据模型设计
4. 技术栈选择建议
5. 架构图（文字描述）

请确保设计符合SOLID原则和最佳实践。"""
        },

        WorkflowStage.UX_DESIGN: {
            "backend": "gemini",
            "validator": StageValidator.validate_ux_design,
            "prompt_template": """你是一位UX设计专家。基于以下功能设计，创建用户体验方案：

【功能设计】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 用户界面布局设计
2. 交互流程设计
3. 关键页面线框图（文字描述）
4. 视觉设计建议（色彩、字体、组件）
5. 可用性和可访问性考虑

请确保设计符合用户体验最佳实践。"""
        },

        WorkflowStage.DEV_PLAN: {
            "backend": "codex",
            "validator": StageValidator.validate_dev_plan,
            "prompt_template": """你是一位技术主管。基于以下设计，制定详细的开发计划：

【功能设计】
{feature_design}

【UX设计】
{ux_design}

【原始需求】
{requirement}

请提供：
1. 开发阶段划分和里程碑
2. 每个阶段的任务清单
3. 技术选型和依赖管理
4. 测试策略（单元测试、集成测试）
5. 部署和运维计划

请以可执行的方式组织计划。"""
        },

        WorkflowStage.IMPLEMENTATION: {
            "backend": "codex",
            "validator": StageValidator.validate_implementation,
            "prompt_template": """你是一位资深开发工程师。基于以下开发计划，开始实现核心功能：

【开发计划】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 核心功能的代码实现
2. 关键模块的代码示例
3. 配置文件示例
4. 测试用例示例
5. 部署脚本示例

请确保代码遵循最佳实践，包含适当的注释和错误处理。"""
        }
    }

    # 阶段依赖关系（用于并行执行）
    STAGE_DEPENDENCIES = {
        WorkflowStage.REQUIREMENTS: [],  # 无依赖
        WorkflowStage.FEATURE_DESIGN: [WorkflowStage.REQUIREMENTS],  # 依赖需求分析
        WorkflowStage.UX_DESIGN: [WorkflowStage.REQUIREMENTS],  # 依赖需求分析（并行模式：独立于功能设计）
        WorkflowStage.DEV_PLAN: [WorkflowStage.FEATURE_DESIGN, WorkflowStage.UX_DESIGN],  # 依赖功能设计和UX设计
        WorkflowStage.IMPLEMENTATION: [WorkflowStage.DEV_PLAN]  # 依赖开发计划
    }

    def __init__(self, parse_events: bool = True, timeout: int = 600, enable_parallel: bool = False, max_workers: int = 2):
        """
        初始化工作流智能体

        Args:
            parse_events: 是否解析事件流
            timeout: 每个阶段的超时时间（秒）
            enable_parallel: 是否启用并行执行（V3功能）
            max_workers: 最大并行工作线程数
        """
        self.backend_orch = BackendOrchestrator(
            parse_events=parse_events,
            timeout=timeout
        )
        self.parse_events = parse_events
        self.timeout = timeout
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers

    def run(self, requirement: str, start_from: WorkflowStage = WorkflowStage.REQUIREMENTS,
            verbose: bool = False, enable_parallel: Optional[bool] = None) -> WorkflowResult:
        """
        执行完整的开发工作流

        Args:
            requirement: 用户需求描述
            start_from: 从哪个阶段开始（用于恢复）
            verbose: 是否输出详细信息
            enable_parallel: 是否启用并行（None=使用初始化配置）

        Returns:
            WorkflowResult
        """
        # 使用参数或默认配置
        if enable_parallel is None:
            enable_parallel = self.enable_parallel

        # 选择执行模式
        if enable_parallel and V3_PARALLEL_AVAILABLE:
            return self._run_parallel(requirement, start_from, verbose)
        else:
            return self._run_sequential(requirement, start_from, verbose)

    def _run_sequential(self, requirement: str, start_from: WorkflowStage = WorkflowStage.REQUIREMENTS,
                       verbose: bool = False) -> WorkflowResult:
        """
        串行执行工作流（原有实现）

        Args:
            requirement: 用户需求描述
            start_from: 从哪个阶段开始
            verbose: 是否输出详细信息

        Returns:
            WorkflowResult
        """
        import time
        start_time = time.time()

        stages_results = []
        previous_outputs = {}

        # 定义阶段顺序
        stage_order = [
            WorkflowStage.REQUIREMENTS,
            WorkflowStage.FEATURE_DESIGN,
            WorkflowStage.UX_DESIGN,
            WorkflowStage.DEV_PLAN,
            WorkflowStage.IMPLEMENTATION
        ]

        # 找到起始位置
        start_index = stage_order.index(start_from)

        for stage in stage_order[start_index:]:
            if verbose:
                print(f"\n{'='*60}")
                print(f"阶段 {stage_order.index(stage) + 1}/5: {stage.value}")
                print(f"{'='*60}")

            # 执行阶段
            result = self._execute_stage(
                stage=stage,
                requirement=requirement,
                previous_outputs=previous_outputs,
                verbose=verbose
            )

            stages_results.append(result)

            # 检查是否成功
            if not result.success:
                total_duration = time.time() - start_time
                return WorkflowResult(
                    requirement=requirement,
                    stages=stages_results,
                    total_duration_seconds=round(total_duration, 3),
                    success=False,
                    completed_stages=len(stages_results) - 1,
                    failed_stage=stage
                )

            # 保存输出供后续阶段使用
            previous_outputs[stage] = result.output

        # 全部成功
        total_duration = time.time() - start_time
        return WorkflowResult(
            requirement=requirement,
            stages=stages_results,
            total_duration_seconds=round(total_duration, 3),
            success=True,
            completed_stages=len(stages_results)
        )

    def _execute_stage(self, stage: WorkflowStage, requirement: str,
                      previous_outputs: Dict[WorkflowStage, str],
                      verbose: bool = False) -> StageResult:
        """
        执行单个阶段

        Args:
            stage: 阶段类型
            requirement: 原始需求
            previous_outputs: 之前阶段的输出
            verbose: 是否详细输出

        Returns:
            StageResult
        """
        import time

        config = self.STAGE_CONFIG[stage]
        backend = config["backend"]
        validator = config["validator"]
        template = config["prompt_template"]

        # 构建提示词
        prompt = self._build_prompt(
            template=template,
            requirement=requirement,
            previous_outputs=previous_outputs
        )

        if verbose:
            print(f"后端: {backend}")
            print(f"提示词长度: {len(prompt)} 字符")

        # 执行任务
        stage_start = time.time()
        task_result = self.backend_orch.run_task(
            backend=backend,
            prompt=prompt,
            stream_format="jsonl"
        )
        duration = time.time() - stage_start

        if not task_result.success:
            return StageResult(
                stage=stage,
                success=False,
                output="",
                duration_seconds=round(duration, 3),
                error=task_result.error
            )

        # 获取输出
        output = task_result.get_final_output()

        if verbose:
            print(f"输出长度: {len(output)} 字符")
            print(f"耗时: {duration:.2f}s")

        # 验证输出
        is_valid, validation_error = validator(output)

        if not is_valid:
            if verbose:
                print(f"验证失败: {validation_error}")

            return StageResult(
                stage=stage,
                success=False,
                output=output,
                duration_seconds=round(duration, 3),
                run_id=task_result.run_id,
                error=f"Validation failed: {validation_error}"
            )

        if verbose:
            print("[OK] 验证通过")

        return StageResult(
            stage=stage,
            success=True,
            output=output,
            duration_seconds=round(duration, 3),
            run_id=task_result.run_id
        )

    def _build_prompt(self, template: str, requirement: str,
                     previous_outputs: Dict[WorkflowStage, str]) -> str:
        """
        构建阶段提示词

        Args:
            template: 提示词模板
            requirement: 原始需求
            previous_outputs: 之前阶段的输出

        Returns:
            完整的提示词
        """
        # 准备变量
        variables = {
            "requirement": requirement,
            "previous_output": previous_outputs.get(
                list(previous_outputs.keys())[-1] if previous_outputs else None,
                ""
            ),
            "feature_design": previous_outputs.get(WorkflowStage.FEATURE_DESIGN, ""),
            "ux_design": previous_outputs.get(WorkflowStage.UX_DESIGN, ""),
        }

        # 渲染模板
        try:
            return template.format(**variables)
        except KeyError as e:
            # 缺少变量，使用默认值
            return template.format(
                requirement=requirement,
                previous_output=variables["previous_output"],
                feature_design=variables.get("feature_design", "[待完成]"),
                ux_design=variables.get("ux_design", "[待完成]")
            )

    def _run_parallel(self, requirement: str, start_from: WorkflowStage = WorkflowStage.REQUIREMENTS,
                     verbose: bool = False) -> WorkflowResult:
        """
        并行执行工作流（V3功能）

        根据阶段依赖关系自动识别可并行的阶段并执行。

        Args:
            requirement: 用户需求描述
            start_from: 从哪个阶段开始
            verbose: 是否输出详细信息

        Returns:
            WorkflowResult
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        start_time = time.time()

        if verbose:
            print(f"\n[并行模式] 启用 V3 并行执行")
            print(f"最大并行数: {self.max_workers}")

        # 定义阶段顺序
        stage_order = [
            WorkflowStage.REQUIREMENTS,
            WorkflowStage.FEATURE_DESIGN,
            WorkflowStage.UX_DESIGN,
            WorkflowStage.DEV_PLAN,
            WorkflowStage.IMPLEMENTATION
        ]

        # 找到起始位置
        start_index = stage_order.index(start_from)
        stages_to_execute = stage_order[start_index:]

        # 构建依赖图（基于 STAGE_DEPENDENCIES）
        graph = {}
        for stage in stages_to_execute:
            deps = self.STAGE_DEPENDENCIES.get(stage, [])
            # 只保留在执行列表中的依赖
            filtered_deps = [d for d in deps if d in stages_to_execute]
            graph[stage] = set(filtered_deps)

        # 使用 DependencyAnalyzer 进行拓扑排序
        analyzer = DependencyAnalyzer(registry=None)

        # 将依赖图转换为字符串键（DependencyAnalyzer 需要）
        str_graph = {stage.value: {d.value for d in deps} for stage, deps in graph.items()}

        try:
            # 拓扑排序得到分层
            levels = analyzer.topological_sort(str_graph)

            if verbose:
                print(f"\n[依赖分析] 识别出 {len(levels)} 个执行层级：")
                for i, level in enumerate(levels):
                    stage_names = [WorkflowStage(s) for s in level]
                    print(f"  Level {i}: {[s.value for s in stage_names]}")

        except Exception as e:
            if verbose:
                print(f"[警告] 依赖分析失败: {e}")
                print("[提示] 回退到串行执行")
            return self._run_sequential(requirement, start_from, verbose)

        # 按层级执行
        stage_results = {}
        all_results = []

        for level_index, level_stage_values in enumerate(levels):
            level_stages = [WorkflowStage(v) for v in level_stage_values]

            if verbose:
                print(f"\n{'='*60}")
                print(f"执行 Level {level_index}: {len(level_stages)} 个阶段")
                if len(level_stages) > 1:
                    print(f"[并行] {[s.value for s in level_stages]}")
                print(f"{'='*60}")

            # 层内并行执行
            if len(level_stages) == 1:
                # 单阶段，直接执行
                stage = level_stages[0]
                result = self._execute_stage_parallel(
                    stage=stage,
                    requirement=requirement,
                    previous_results=stage_results,
                    verbose=verbose
                )
                all_results.append(result)
                stage_results[stage] = result

                if not result.success:
                    # 失败，终止执行
                    total_duration = time.time() - start_time
                    return WorkflowResult(
                        requirement=requirement,
                        stages=all_results,
                        total_duration_seconds=round(total_duration, 3),
                        success=False,
                        completed_stages=len(all_results) - 1,
                        failed_stage=stage
                    )

            else:
                # 多阶段，并行执行
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    # 提交所有任务
                    future_to_stage = {
                        executor.submit(
                            self._execute_stage_parallel,
                            stage=stage,
                            requirement=requirement,
                            previous_results=stage_results,
                            verbose=verbose
                        ): stage
                        for stage in level_stages
                    }

                    # 收集结果
                    level_failed = False
                    for future in as_completed(future_to_stage):
                        stage = future_to_stage[future]

                        try:
                            result = future.result(timeout=self.timeout)
                            all_results.append(result)
                            stage_results[stage] = result

                            if not result.success:
                                level_failed = True

                        except Exception as e:
                            if verbose:
                                print(f"[错误] 阶段 {stage.value} 执行异常: {e}")

                            # 创建失败结果
                            result = StageResult(
                                stage=stage,
                                success=False,
                                output="",
                                duration_seconds=0.0,
                                error=str(e)
                            )
                            all_results.append(result)
                            stage_results[stage] = result
                            level_failed = True

                # 检查是否有失败
                if level_failed:
                    total_duration = time.time() - start_time
                    failed_stages = [s for s in level_stages if not stage_results[s].success]

                    return WorkflowResult(
                        requirement=requirement,
                        stages=all_results,
                        total_duration_seconds=round(total_duration, 3),
                        success=False,
                        completed_stages=len(all_results) - len(failed_stages),
                        failed_stage=failed_stages[0] if failed_stages else None
                    )

        # 全部成功
        total_duration = time.time() - start_time

        if verbose:
            print(f"\n[并行执行完成] 总耗时: {total_duration:.2f}s")

        return WorkflowResult(
            requirement=requirement,
            stages=all_results,
            total_duration_seconds=round(total_duration, 3),
            success=True,
            completed_stages=len(all_results)
        )

    def _execute_stage_parallel(
        self,
        stage: WorkflowStage,
        requirement: str,
        previous_results: Dict[WorkflowStage, StageResult],
        verbose: bool = False
    ) -> StageResult:
        """
        并行模式下执行单个阶段

        与 _execute_stage 类似，但使用 previous_results 而不是 previous_outputs。

        Args:
            stage: 阶段类型
            requirement: 原始需求
            previous_results: 之前阶段的结果（StageResult）
            verbose: 是否详细输出

        Returns:
            StageResult
        """
        import time

        config = self.STAGE_CONFIG[stage]
        backend = config["backend"]
        validator = config["validator"]
        template = config["prompt_template"]

        # 构建 previous_outputs（从 StageResult 提取 output）
        previous_outputs = {s: r.output for s, r in previous_results.items()}

        # 构建提示词
        prompt = self._build_prompt(
            template=template,
            requirement=requirement,
            previous_outputs=previous_outputs
        )

        if verbose:
            print(f"\n[{stage.value}]")
            print(f"  后端: {backend}")
            print(f"  提示词长度: {len(prompt)} 字符")

        # 执行任务
        stage_start = time.time()
        task_result = self.backend_orch.run_task(
            backend=backend,
            prompt=prompt,
            stream_format="jsonl"
        )
        duration = time.time() - stage_start

        if not task_result.success:
            if verbose:
                print(f"  [失败] {task_result.error}")

            return StageResult(
                stage=stage,
                success=False,
                output="",
                duration_seconds=round(duration, 3),
                error=task_result.error
            )

        # 获取输出
        output = task_result.get_final_output()

        if verbose:
            print(f"  输出长度: {len(output)} 字符")
            print(f"  耗时: {duration:.2f}s")

        # 验证输出
        is_valid, validation_error = validator(output)

        if not is_valid:
            if verbose:
                print(f"  [验证失败] {validation_error}")

            return StageResult(
                stage=stage,
                success=False,
                output=output,
                duration_seconds=round(duration, 3),
                run_id=task_result.run_id,
                error=f"Validation failed: {validation_error}"
            )

        if verbose:
            print(f"  [OK] 验证通过")

        return StageResult(
            stage=stage,
            success=True,
            output=output,
            duration_seconds=round(duration, 3),
            run_id=task_result.run_id
        )


# 使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DevWorkflowAgent - 多阶段开发工作流")
    parser.add_argument("requirement", help="用户需求描述")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--timeout", type=int, default=600, help="每阶段超时（秒）")
    parser.add_argument("--enable-parallel", action="store_true", help="启用并行执行（V3功能）")
    parser.add_argument("--max-workers", type=int, default=2, help="最大并行工作线程数")

    args = parser.parse_args()

    # 创建智能体
    agent = DevWorkflowAgent(
        parse_events=True,
        timeout=args.timeout,
        enable_parallel=args.enable_parallel,
        max_workers=args.max_workers
    )

    print(f"[DevWorkflowAgent] 开始执行 5 阶段开发工作流")
    print(f"需求: {args.requirement}")
    if args.enable_parallel:
        if V3_PARALLEL_AVAILABLE:
            print(f"模式: 并行执行 (max_workers={args.max_workers})")
        else:
            print(f"模式: 并行执行（未启用，V3组件不可用）")
    else:
        print(f"模式: 串行执行")
    print()

    # 执行工作流
    result = agent.run(args.requirement, verbose=args.verbose)

    # 输出结果
    print(f"\n{'='*60}")
    print("工作流执行结果")
    print(f"{'='*60}")
    print(f"成功: {result.success}")
    print(f"完成阶段: {result.completed_stages}/5")
    print(f"总耗时: {result.total_duration_seconds:.2f}s")

    if not result.success:
        print(f"失败阶段: {result.failed_stage.value if result.failed_stage else 'N/A'}")

    print(f"\n阶段详情:")
    for i, stage_result in enumerate(result.stages, 1):
        status = "✓" if stage_result.success else "✗"
        print(f"  {status} 阶段 {i}: {stage_result.stage.value} ({stage_result.duration_seconds:.2f}s)")
        if not stage_result.success and stage_result.error:
            print(f"     错误: {stage_result.error}")

    sys.exit(0 if result.success else 1)
