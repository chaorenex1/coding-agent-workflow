#!/usr/bin/env python3
"""
MasterOrchestrator V3 快速开始示例

最简单的使用方式，包括：
- 自动发现
- 并行批处理
- 资源查询
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestrator import MasterOrchestrator


def example_1_basic_usage():
    """示例 1: 基本用法"""
    print("示例 1: 基本用法\n")

    # 创建 Orchestrator（启用自动发现）
    orch = MasterOrchestrator(auto_discover=True)

    # 单个请求
    result = orch.process("查看 git 状态")
    print(f"结果: {result}")


def example_2_parallel_batch():
    """示例 2: 并行批处理"""
    print("\n示例 2: 并行批处理\n")

    # 创建 Orchestrator（启用并行）
    orch = MasterOrchestrator(
        auto_discover=True,
        enable_parallel=True,
        max_parallel_workers=3
    )

    # 批量请求
    requests = [
        "查看 git 状态",
        "列出当前目录",
        "显示 Python 版本"
    ]

    # 并行执行
    result = orch.process_batch(requests, enable_parallel=True)

    print(f"总任务: {result.total_tasks}")
    print(f"成功: {result.successful}/{result.total_tasks}")
    print(f"耗时: {result.total_duration_seconds:.2f}s")


def example_3_list_resources():
    """示例 3: 列出资源"""
    print("\n示例 3: 列出资源\n")

    orch = MasterOrchestrator(auto_discover=True)

    # 列出所有 Skills
    skills = orch.list_resources(type_filter="skill")
    print(f"已注册 Skills ({len(skills)} 个):")
    for skill in skills:
        print(f"  - {skill.name} (来源: {skill.source})")

    # 列出所有 Commands
    commands = orch.list_resources(type_filter="command")
    print(f"\n已注册 Commands ({len(commands)} 个):")
    for cmd in commands:
        print(f"  - {cmd.name}")


def example_4_dev_workflow():
    """示例 4: DevWorkflow 并行"""
    print("\n示例 4: DevWorkflow 并行\n")

    from orchestrator.skills.dev_workflow import DevWorkflowAgent

    # 创建并行工作流
    agent = DevWorkflowAgent(
        enable_parallel=True,
        max_workers=2
    )

    # 执行工作流
    result = agent.run("创建待办事项应用", verbose=True)

    print(f"\n成功: {result.success}")
    print(f"完成阶段: {result.completed_stages}/5")
    print(f"总耗时: {result.total_duration_seconds:.2f}s")


def example_5_custom_config():
    """示例 5: 自定义配置"""
    print("\n示例 5: 自定义配置\n")

    # 使用自定义配置文件
    orch = MasterOrchestrator(
        auto_discover=True,
        config_path=Path("./my-config")  # 自定义配置目录
    )

    # 查看配置
    if orch.config:
        print(f"配置版本: {orch.config.version}")
        print(f"全局设置: {orch.config.global_settings}")


if __name__ == "__main__":
    print("=" * 60)
    print("MasterOrchestrator V3 快速开始")
    print("=" * 60)

    # 运行所有示例
    example_1_basic_usage()
    example_2_parallel_batch()
    example_3_list_resources()
    # example_4_dev_workflow()  # 注释掉，需要真实 API
    example_5_custom_config()

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
