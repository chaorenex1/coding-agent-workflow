#!/usr/bin/env python3
"""
MasterOrchestrator V3 功能演示

演示以下功能：
1. 自动注册发现
2. 并行批处理
3. DevWorkflow 并行执行
4. 配置管理
5. 资源查询
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestrator import MasterOrchestrator
from orchestrator.skills.dev_workflow import DevWorkflowAgent


def demo_1_auto_discovery():
    """演示 1: 自动注册发现"""
    print("=" * 70)
    print("演示 1: 自动注册发现")
    print("=" * 70)

    # 启用自动发现
    orch = MasterOrchestrator(
        auto_discover=True,      # 启用自动发现
        config_path=None,        # 使用当前目录
    )

    print("\n已注册资源列表：\n")

    # 列出所有资源
    all_resources = orch.list_resources()
    print(f"总共 {len(all_resources)} 个资源：\n")

    # 按类型分组显示
    for resource_type in ["skill", "command", "agent", "prompt"]:
        resources = orch.list_resources(type_filter=resource_type)
        if resources:
            print(f"{resource_type.upper()}S ({len(resources)} 个):")
            for r in resources:
                print(f"  • {r.name}")
                print(f"    命名空间: {r.namespace}")
                print(f"    来源: {r.source} (优先级: {r.priority})")
                if r.dependencies:
                    print(f"    依赖: {', '.join(r.dependencies)}")
            print()


def demo_2_parallel_batch():
    """演示 2: 并行批处理"""
    print("=" * 70)
    print("演示 2: 并行批处理")
    print("=" * 70)

    # 启用并行执行
    orch = MasterOrchestrator(
        auto_discover=True,
        enable_parallel=True,       # 启用并行
        max_parallel_workers=3,
        parallel_timeout=120
    )

    # 批量请求
    requests = [
        "查看 git 状态",
        "列出当前目录文件",
        "显示 Python 版本",
    ]

    print(f"\n批量处理 {len(requests)} 个请求：")
    for i, req in enumerate(requests, 1):
        print(f"  {i}. {req}")

    print("\n[执行中...]\n")

    # 并行批处理
    result = orch.process_batch(
        requests,
        enable_parallel=True,
        verbose=False
    )

    # 显示结果
    print("\n批处理结果:")
    print(f"  总任务: {result.total_tasks}")
    print(f"  成功: {result.successful} ✓")
    print(f"  失败: {result.failed} ✗")
    print(f"  成功率: {result.success_rate:.1%}")
    print(f"  总耗时: {result.total_duration_seconds:.2f}s")

    # 详细结果
    print("\n详细结果:")
    for task_result in result.task_results:
        status = "✓" if task_result.success else "✗"
        print(f"  {status} {task_result.namespace} ({task_result.duration_seconds:.2f}s)")
        if task_result.error:
            print(f"     错误: {task_result.error}")


def demo_3_dev_workflow_parallel():
    """演示 3: DevWorkflow 并行执行"""
    print("\n" + "=" * 70)
    print("演示 3: DevWorkflow 并行执行")
    print("=" * 70)

    # 创建并行工作流代理
    agent = DevWorkflowAgent(
        parse_events=True,
        timeout=300,
        enable_parallel=True,    # 启用并行
        max_workers=2            # 同时执行2个阶段
    )

    requirement = "创建一个简单的待办事项管理应用（演示版）"

    print(f"\n需求: {requirement}")
    print("模式: 并行执行")
    print("\n执行层级:")
    print("  Level 0: [REQUIREMENTS]")
    print("  Level 1: [FEATURE_DESIGN, UX_DESIGN] ← 并行执行")
    print("  Level 2: [DEV_PLAN]")
    print("  Level 3: [IMPLEMENTATION]")

    print("\n[执行中...]\n")

    # 执行工作流
    result = agent.run(requirement, verbose=False)

    # 显示结果
    print("\n工作流结果:")
    print(f"  成功: {result.success}")
    print(f"  完成阶段: {result.completed_stages}/5")
    print(f"  总耗时: {result.total_duration_seconds:.2f}s")

    if not result.success and result.failed_stage:
        print(f"  失败阶段: {result.failed_stage.value}")

    print("\n阶段详情:")
    for i, stage_result in enumerate(result.stages, 1):
        status = "✓" if stage_result.success else "✗"
        print(f"  {status} 阶段 {i}: {stage_result.stage.value} ({stage_result.duration_seconds:.2f}s)")


def demo_4_config_management():
    """演示 4: 配置管理"""
    print("\n" + "=" * 70)
    print("演示 4: 配置管理")
    print("=" * 70)

    orch = MasterOrchestrator(auto_discover=True)

    print("\n配置信息:")
    if orch.config:
        print(f"  版本: {orch.config.version}")
        print(f"  Skills 数量: {len(orch.config.skills)}")
        print(f"  Commands 数量: {len(orch.config.commands)}")
        print(f"  Agents 数量: {len(orch.config.agents)}")
        print(f"  Prompts 数量: {len(orch.config.prompts)}")

        # 全局设置
        print("\n全局设置:")
        for key, value in orch.config.global_settings.items():
            print(f"  {key}: {value}")

        # 并行配置
        print("\n并行配置:")
        print(f"  enabled: {orch.config.parallel_config.enabled}")
        print(f"  max_workers: {orch.config.parallel_config.max_workers}")
        print(f"  timeout_per_task: {orch.config.parallel_config.timeout_per_task}s")

    # 注册表统计
    if orch.registry:
        stats = orch.registry.get_stats()
        print("\n注册表统计:")
        print(f"  总资源数: {stats['total_resources']}")
        print(f"  按类型分布: {stats['by_type']}")
        print(f"  按来源分布: {stats['by_source']}")
        print(f"  有依赖的资源: {stats['with_dependencies']}")
        print(f"  总依赖链接数: {stats['total_dependency_links']}")


def demo_5_resource_query():
    """演示 5: 资源查询"""
    print("\n" + "=" * 70)
    print("演示 5: 资源查询")
    print("=" * 70)

    orch = MasterOrchestrator(auto_discover=True)

    # 按类型查询
    print("\n按类型查询:")
    skills = orch.list_resources(type_filter="skill")
    print(f"  Skills: {len(skills)} 个")
    for skill in skills[:3]:  # 只显示前3个
        print(f"    - {skill.name} (优先级: {skill.priority})")

    # 按来源查询
    print("\n按来源查询:")
    for source in ["builtin", "user", "project"]:
        resources = orch.list_resources(source_filter=source)
        print(f"  {source.capitalize()}: {len(resources)} 个资源")

    # 组合查询
    print("\n组合查询:")
    project_skills = orch.list_resources(
        type_filter="skill",
        source_filter="project"
    )
    print(f"  项目级 Skills: {len(project_skills)} 个")

    # 依赖分析
    if orch.registry:
        print("\n依赖分析:")
        # 检查循环依赖
        cycles = orch.registry.check_circular_dependency()
        if cycles:
            print(f"  ⚠ 发现 {len(cycles)} 个循环依赖")
            for cycle in cycles:
                print(f"    {' → '.join(cycle)}")
        else:
            print("  ✓ 无循环依赖")

        # 验证依赖
        errors = orch.registry.validate_dependencies()
        if errors:
            print(f"  ⚠ 发现 {len(errors)} 个依赖错误:")
            for error in errors[:3]:  # 只显示前3个
                print(f"    {error}")
        else:
            print("  ✓ 所有依赖有效")


def demo_6_comparison():
    """演示 6: 串行 vs 并行对比"""
    print("\n" + "=" * 70)
    print("演示 6: 串行 vs 并行性能对比")
    print("=" * 70)

    # 测试请求
    requests = [
        "显示当前目录",
        "显示环境变量 PATH",
        "显示 Python 版本",
    ]

    print(f"\n测试: {len(requests)} 个独立任务\n")

    # 串行模式
    print("1. 串行模式:")
    orch_serial = MasterOrchestrator(
        auto_discover=True,
        enable_parallel=False
    )
    result_serial = orch_serial.process_batch(requests, enable_parallel=False, verbose=False)
    print(f"   耗时: {result_serial.total_duration_seconds:.2f}s")
    print(f"   成功率: {result_serial.success_rate:.1%}")

    # 并行模式
    print("\n2. 并行模式:")
    orch_parallel = MasterOrchestrator(
        auto_discover=True,
        enable_parallel=True,
        max_parallel_workers=3
    )
    result_parallel = orch_parallel.process_batch(requests, enable_parallel=True, verbose=False)
    print(f"   耗时: {result_parallel.total_duration_seconds:.2f}s")
    print(f"   成功率: {result_parallel.success_rate:.1%}")

    # 对比
    if result_serial.total_duration_seconds > 0:
        speedup = result_serial.total_duration_seconds / result_parallel.total_duration_seconds
        improvement = (1 - result_parallel.total_duration_seconds / result_serial.total_duration_seconds) * 100
        print(f"\n性能提升:")
        print(f"   加速比: {speedup:.2f}x")
        print(f"   时间节省: {improvement:.1f}%")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("MasterOrchestrator V3 功能演示")
    print("=" * 70)

    try:
        # 运行所有演示
        demo_1_auto_discovery()
        demo_2_parallel_batch()
        # demo_3_dev_workflow_parallel()  # 注释掉，因为需要真实 API
        demo_4_config_management()
        demo_5_resource_query()
        demo_6_comparison()

        print("\n" + "=" * 70)
        print("演示完成!")
        print("=" * 70)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="V3 功能演示")
    parser.add_argument(
        "--demo",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 0],
        default=0,
        help="运行特定演示 (0=全部)"
    )

    args = parser.parse_args()

    if args.demo == 0:
        sys.exit(main())
    else:
        demos = {
            1: demo_1_auto_discovery,
            2: demo_2_parallel_batch,
            3: demo_3_dev_workflow_parallel,
            4: demo_4_config_management,
            5: demo_5_resource_query,
            6: demo_6_comparison
        }
        try:
            demos[args.demo]()
            print("\n演示完成!")
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
