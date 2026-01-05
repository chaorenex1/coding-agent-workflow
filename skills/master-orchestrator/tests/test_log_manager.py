#!/usr/bin/env python3
"""
LogManager 单元测试
"""

import sys
import os
import tempfile
import shutil
import logging
from pathlib import Path

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.log_manager import LogManager


def print_result(test_name: str, passed: bool, details: str = ""):
    """打印测试结果"""
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {test_name}")
    if details:
        print(f"      {details}")


def cleanup_handlers():
    """清理所有logging handlers（Windows必需）"""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


def test_initialization():
    """测试1：日志管理器初始化"""
    print("\n========== 测试1：日志管理器初始化 ==========")

    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"

        # 创建 LogManager
        manager = LogManager(log_dir=log_dir)

        # 验证目录创建
        print_result(
            "日志目录创建",
            log_dir.exists() and log_dir.is_dir(),
            f"path={log_dir}"
        )

        # 验证文件路径
        print_result(
            "主日志路径",
            manager.main_log == log_dir / "orchestrator.log",
            f"path={manager.main_log}"
        )

        print_result(
            "错误日志路径",
            manager.error_log == log_dir / "errors.log",
            f"path={manager.error_log}"
        )

        # 验证初始化状态
        print_result(
            "初始化状态",
            not manager.is_initialized(),
            "setup()未调用前应为False"
        )

        # 执行 setup
        success = manager.setup(level="INFO")

        print_result(
            "setup()执行",
            success,
            "应成功初始化"
        )

        print_result(
            "初始化后状态",
            manager.is_initialized(),
            "setup()后应为True"
        )

        # 验证日志文件创建
        print_result(
            "主日志文件创建",
            manager.main_log.exists(),
            f"size={manager.main_log.stat().st_size} bytes"
        )

        # 清理handlers
        cleanup_handlers()


def test_log_writing():
    """测试2：日志写入"""
    print("\n========== 测试2：日志写入 ==========")

    cleanup_handlers()  # 清理之前的handlers
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="DEBUG")

        # 1. 任务开始日志
        manager.log_task_start("分析代码性能", "backend")

        # 2. 意图分析日志
        manager.log_intent_analysis("backend", "analysis", "simple", 0.85)

        # 3. 任务完成日志
        manager.log_task_complete("backend", "claude", 3.5, True)

        # 4. 缓存事件日志
        manager.log_cache_event("hit", "request_hash=abc123")

        # 5. 注册表事件日志
        manager.log_registry_event("scan", 15, 120)

        # 验证主日志内容
        with open(manager.main_log, 'r', encoding='utf-8') as f:
            main_content = f.read()

        print_result(
            "任务开始日志",
            "[任务开始]" in main_content and "分析代码性能" in main_content,
            "包含请求信息"
        )

        print_result(
            "意图分析日志",
            "[意图分析]" in main_content and "confidence=0.85" in main_content,
            "包含置信度"
        )

        print_result(
            "任务完成日志",
            "[任务完成]" in main_content and "duration=3.50s" in main_content,
            "包含耗时"
        )

        print_result(
            "缓存事件日志",
            "[缓存]" in main_content,
            "DEBUG级别日志"
        )

        print_result(
            "注册表事件日志",
            "[注册表]" in main_content and "15个资源" in main_content,
            "包含资源统计"
        )

        cleanup_handlers()


def test_error_logging():
    """测试3：错误日志分离"""
    print("\n========== 测试3：错误日志分离 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="INFO")

        # 写入不同级别的日志
        logging.info("这是一条INFO日志")
        logging.warning("这是一条WARNING日志")
        logging.error("这是一条ERROR日志")
        manager.log_error("测试上下文", ValueError("测试错误"))

        # 验证主日志包含所有级别
        with open(manager.main_log, 'r', encoding='utf-8') as f:
            main_content = f.read()

        print_result(
            "主日志包含INFO",
            "INFO" in main_content,
            "主日志应包含所有级别"
        )

        print_result(
            "主日志包含ERROR",
            "ERROR" in main_content,
            "主日志应包含错误"
        )

        # 验证错误日志仅包含ERROR
        with open(manager.error_log, 'r', encoding='utf-8') as f:
            error_content = f.read()

        print_result(
            "错误日志仅包含ERROR",
            "ERROR" in error_content and "INFO" not in error_content,
            "错误日志应仅包含ERROR及以上"
        )

        print_result(
            "错误上下文记录",
            "测试上下文" in error_content and "ValueError" in error_content,
            "包含完整错误信息"
        )

        cleanup_handlers()


def test_log_rotation():
    """测试4：日志轮转"""
    print("\n========== 测试4：日志轮转 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"

        # 设置小的轮转阈值（1KB）
        manager = LogManager(
            log_dir=log_dir,
            max_bytes=1024,  # 1KB
            backup_count=2
        )
        manager.setup(level="INFO")

        # 写入大量日志触发轮转
        for i in range(100):
            logging.info(f"这是第 {i} 条日志消息，用于测试日志轮转功能。" * 5)

        # 验证主日志文件大小
        main_size = manager.main_log.stat().st_size

        print_result(
            "主日志文件大小控制",
            main_size > 0 and main_size <= 2048,  # 允许一定误差
            f"size={main_size} bytes"
        )

        # 验证备份文件创建
        backup1 = Path(str(manager.main_log) + ".1")
        backup2 = Path(str(manager.main_log) + ".2")

        print_result(
            "第一个备份文件",
            backup1.exists(),
            f"path={backup1}"
        )

        # 备份2可能存在也可能不存在，取决于日志量
        if backup2.exists():
            print_result(
                "第二个备份文件",
                True,
                f"path={backup2}"
            )

        cleanup_handlers()


def test_recent_errors():
    """测试5：获取最近错误"""
    print("\n========== 测试5：获取最近错误 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="ERROR")

        # 写入多条错误日志
        for i in range(5):
            logging.error(f"错误消息 {i}")

        # 获取最近3条错误
        recent_errors = manager.get_recent_errors(count=3)

        print_result(
            "获取错误数量",
            len(recent_errors) == 3,
            f"count={len(recent_errors)}"
        )

        print_result(
            "错误内容正确",
            "错误消息 4" in recent_errors[-1],
            "最后一条应为'错误消息 4'"
        )

        cleanup_handlers()


def test_log_stats():
    """测试6：日志统计"""
    print("\n========== 测试6：日志统计 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="INFO")

        # 写入一些日志
        for i in range(10):
            logging.info(f"INFO 消息 {i}")
            if i % 3 == 0:
                logging.error(f"ERROR 消息 {i}")

        # 获取统计
        stats = manager.get_log_stats()

        print_result(
            "统计信息包含log_dir",
            "log_dir" in stats,
            f"log_dir={stats.get('log_dir')}"
        )

        print_result(
            "统计信息包含初始化状态",
            stats.get("initialized") is True,
            "initialized=True"
        )

        print_result(
            "主日志统计",
            "main_log" in stats and stats["main_log"].get("line_count", 0) > 0,
            f"lines={stats['main_log'].get('line_count', 0)}"
        )

        print_result(
            "错误日志统计",
            "error_log" in stats and stats["error_log"].get("error_count", 0) > 0,
            f"errors={stats['error_log'].get('error_count', 0)}"
        )

        cleanup_handlers()


def test_level_adjustment():
    """测试7：动态调整日志级别"""
    print("\n========== 测试7：动态调整日志级别 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="INFO")

        # 初始级别：INFO，DEBUG应该不会记录
        logging.debug("DEBUG 消息 1 - 不应记录")
        logging.info("INFO 消息 1 - 应该记录")

        # 调整为 DEBUG
        manager.set_level("DEBUG")

        logging.debug("DEBUG 消息 2 - 应该记录")
        logging.info("INFO 消息 2 - 应该记录")

        # 验证日志内容
        with open(manager.main_log, 'r', encoding='utf-8') as f:
            content = f.read()

        print_result(
            "初始INFO级别",
            "INFO 消息 1" in content and "DEBUG 消息 1" not in content,
            "DEBUG应被过滤"
        )

        print_result(
            "调整后DEBUG级别",
            "DEBUG 消息 2" in content and "INFO 消息 2" in content,
            "DEBUG应被记录"
        )

        cleanup_handlers()


def test_long_request_truncation():
    """测试8：长请求截断"""
    print("\n========== 测试8：长请求截断 ==========")

    cleanup_handlers()
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        manager = LogManager(log_dir=log_dir)
        manager.setup(level="INFO")

        # 超长请求
        long_request = "A" * 200

        manager.log_task_start(long_request, "backend")

        # 验证日志内容
        with open(manager.main_log, 'r', encoding='utf-8') as f:
            content = f.read()

        print_result(
            "长请求被截断",
            "..." in content and content.count("A") < 200,
            "超过100字符应截断"
        )

        cleanup_handlers()


def main():
    """运行所有测试"""
    print("=" * 60)
    print("LogManager 单元测试")
    print("=" * 60)

    try:
        test_initialization()
        test_log_writing()
        test_error_logging()
        test_log_rotation()
        test_recent_errors()
        test_log_stats()
        test_level_adjustment()
        test_long_request_truncation()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n[错误] 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
