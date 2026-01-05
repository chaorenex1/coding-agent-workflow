#!/usr/bin/env python3
"""
LogManager 集成简单测试 - 验证日志目录和文件创建
"""

import sys
import os
from pathlib import Path

def test_log_directory():
    """测试：验证日志目录已创建"""
    print("\n========== LogManager 集成验证 ==========\n")

    # 检查缓存目录
    cache_root = Path.home() / ".memex" / "orchestrator"
    log_dir = cache_root / "logs"

    print(f"[1] 检查目录结构...")
    print(f"  - 缓存根目录: {cache_root}")
    print(f"  - 缓存根目录存在: {cache_root.exists()}")
    print(f"  - 日志目录: {log_dir}")
    print(f"  - 日志目录存在: {log_dir.exists()}")

    if not log_dir.exists():
        print(f"\n  [提示] 日志目录不存在，请先运行一次 MasterOrchestrator")
        print(f"  示例: from orchestrator import MasterOrchestrator; MasterOrchestrator()")
        return 1

    # 检查日志文件
    main_log = log_dir / "orchestrator.log"
    error_log = log_dir / "errors.log"

    print(f"\n[2] 检查日志文件...")
    print(f"  - 主日志: {main_log}")
    print(f"  - 主日志存在: {main_log.exists()}")

    if main_log.exists():
        size = main_log.stat().st_size
        print(f"  - 主日志大小: {size} bytes")

        # 读取最后几行
        try:
            with open(main_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"  - 主日志行数: {len(lines)}")

                if lines:
                    print(f"\n[3] 最后3行日志:")
                    for line in lines[-3:]:
                        print(f"    {line.rstrip()}")
        except Exception as e:
            print(f"  - 读取日志失败: {e}")

    print(f"\n  - 错误日志: {error_log}")
    print(f"  - 错误日志存在: {error_log.exists()}")

    if error_log.exists():
        size = error_log.stat().st_size
        print(f"  - 错误日志大小: {size} bytes")

    # 列出日志目录所有文件
    print(f"\n[4] 日志目录文件列表:")
    if log_dir.exists():
        for file in log_dir.iterdir():
            if file.is_file():
                print(f"  - {file.name} ({file.stat().st_size} bytes)")

    print(f"\n========== 验证完成 ==========\n")
    return 0


def main():
    try:
        return test_log_directory()
    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
