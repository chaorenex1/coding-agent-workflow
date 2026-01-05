#!/usr/bin/env python3
"""
LogManager 集成测试 - 测试 LogManager 在 MasterOrchestrator 中的使用
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_orchestrator_logging():
    """测试：MasterOrchestrator 中的日志记录"""
    print("\n========== LogManager 集成测试 ==========\n")

    # 导入必需模块
    import sys
    sys.path.insert(0, str(project_root))

    # 设置 package
    import orchestrator
    from orchestrator.master_orchestrator import MasterOrchestrator

    # 创建 Orchestrator（不启用远程服务，避免依赖）
    print("[1] 初始化 MasterOrchestrator...")
    orch = MasterOrchestrator(
        timeout=30,
        use_remote=False,
        auto_discover=False  # 禁用V3功能，简化测试
    )

    # 验证 log_manager 已初始化
    print(f"  - LogManager 已创建: {orch.log_manager is not None}")
    print(f"  - 日志目录: {orch.log_manager.log_dir}")
    print(f"  - 初始化状态: {orch.log_manager.is_initialized()}")

    # 检查日志文件
    main_log = orch.log_manager.main_log
    error_log = orch.log_manager.error_log

    print(f"\n[2] 日志文件验证...")
    print(f"  - 主日志文件: {main_log}")
    print(f"  - 主日志存在: {main_log.exists()}")
    print(f"  - 错误日志文件: {error_log}")

    # 模拟一次请求（使用规则引擎，不调用真实API）
    print(f"\n[3] 处理测试请求...")
    request = "分析代码性能"

    try:
        # 这里不执行真实的process，而是测试日志记录方法
        orch.log_manager.log_task_start(request, "backend")
        orch.log_manager.log_intent_analysis("backend", "analysis", "simple", 0.85)
        orch.log_manager.log_task_complete("backend", "claude", 2.5, True)

        print(f"  - 日志记录成功")

    except Exception as e:
        print(f"  - 日志记录失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 读取日志内容
    print(f"\n[4] 读取日志内容...")
    try:
        with open(main_log, 'r', encoding='utf-8') as f:
            log_content = f.read()

        print(f"  - 日志文件大小: {len(log_content)} 字节")
        print(f"  - 日志行数: {log_content.count(chr(10))}")

        # 验证关键内容
        checks = [
            ("初始化日志", "日志系统已初始化" in log_content),
            ("任务开始日志", "[任务开始]" in log_content),
            ("意图分析日志", "[意图分析]" in log_content),
            ("任务完成日志", "[任务完成]" in log_content),
        ]

        print(f"\n[5] 日志内容验证...")
        for name, result in checks:
            status = "PASS" if result else "FAIL"
            print(f"  [{status}] {name}")

        # 显示最后几行日志
        print(f"\n[6] 最后5行日志:")
        lines = log_content.strip().split('\n')
        for line in lines[-5:]:
            print(f"    {line}")

    except Exception as e:
        print(f"  - 读取日志失败: {e}")
        return 1

    # 获取统计信息
    print(f"\n[7] 日志统计信息...")
    stats = orch.log_manager.get_log_stats()
    print(f"  - 主日志行数: {stats.get('main_log', {}).get('line_count', 0)}")
    print(f"  - 主日志大小: {stats.get('main_log', {}).get('size_mb', 0):.3f} MB")
    print(f"  - 错误日志数: {stats.get('error_log', {}).get('error_count', 0)}")

    print(f"\n========== 集成测试完成 ==========\n")
    return 0


def main():
    try:
        return test_orchestrator_logging()
    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
