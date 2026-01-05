#!/usr/bin/env python3
"""
LogManager - 日志管理器

管理 ~/.memex/orchestrator/logs/ 目录，提供：
- 结构化日志记录
- 自动日志轮转
- 错误日志分离
- 与 Python logging 集成
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class LogManager:
    """
    日志管理器 - 管理 ~/.memex/orchestrator/logs/ 目录

    功能：
    - 配置 Python logging 到文件和控制台
    - 主日志轮转（10MB，保留3个备份）
    - 错误日志单独记录
    - 支持动态调整日志级别

    使用示例：
        log_manager = LogManager(log_dir=Path("~/.memex/orchestrator/logs"))
        log_manager.setup(level="INFO")
        log_manager.log_task_start("分析代码", "backend")
    """

    def __init__(
        self,
        log_dir: Path,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 3,
        console_output: bool = False
    ):
        """
        初始化日志管理器

        Args:
            log_dir: 日志目录路径
            max_bytes: 单文件最大字节数（轮转阈值）
            backup_count: 保留备份数量
            console_output: 是否同时输出到控制台
        """
        self.log_dir = Path(log_dir).expanduser()
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_output = console_output

        # 确保目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 日志文件路径
        self.main_log = self.log_dir / "orchestrator.log"
        self.error_log = self.log_dir / "errors.log"

        # 标记是否已初始化
        self._initialized = False

        # 内部logger（用于LogManager自身的日志）
        self._logger = logging.getLogger("LogManager")

    def setup(self, level: str = "INFO") -> bool:
        """
        配置 Python logging 系统

        Args:
            level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）

        Returns:
            是否成功初始化
        """
        if self._initialized:
            self._logger.warning("日志系统已初始化，跳过重复设置")
            return True

        try:
            # 获取根 logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

            # 清除现有 handlers（避免重复）
            root_logger.handlers.clear()

            # 日志格式
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # 1. 主日志文件 handler（所有级别）
            main_handler = RotatingFileHandler(
                self.main_log,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            main_handler.setLevel(logging.DEBUG)
            main_handler.setFormatter(formatter)
            root_logger.addHandler(main_handler)

            # 2. 错误日志文件 handler（仅ERROR及以上）
            error_handler = RotatingFileHandler(
                self.error_log,
                maxBytes=self.max_bytes // 2,  # 错误日志更小
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

            # 3. 控制台 handler（可选）
            if self.console_output:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)

            self._initialized = True
            self._logger.info(f"日志系统已初始化: {self.log_dir}")
            return True

        except Exception as e:
            print(f"[LogManager] 初始化失败: {e}")
            return False

    def log_task_start(self, request: str, mode: str):
        """
        记录任务开始

        Args:
            request: 用户请求
            mode: 执行模式
        """
        # 截断过长的请求
        truncated_request = request[:100] + "..." if len(request) > 100 else request
        logging.info(f"[任务开始] mode={mode}, request=\"{truncated_request}\"")

    def log_task_complete(
        self,
        mode: str,
        backend: str,
        duration: float,
        success: bool
    ):
        """
        记录任务完成

        Args:
            mode: 执行模式
            backend: 后端名称
            duration: 执行耗时（秒）
            success: 是否成功
        """
        status = "成功" if success else "失败"
        logging.info(
            f"[任务完成] mode={mode}, backend={backend}, "
            f"duration={duration:.2f}s, status={status}"
        )

    def log_intent_analysis(
        self,
        mode: str,
        task_type: str,
        complexity: str,
        confidence: float
    ):
        """
        记录意图分析结果

        Args:
            mode: 执行模式
            task_type: 任务类型
            complexity: 复杂度
            confidence: 置信度
        """
        logging.debug(
            f"[意图分析] mode={mode}, task_type={task_type}, "
            f"complexity={complexity}, confidence={confidence:.2f}"
        )

    def log_cache_event(self, event_type: str, details: str):
        """
        记录缓存事件

        Args:
            event_type: 事件类型（hit/miss/save/evict）
            details: 详细信息
        """
        logging.debug(f"[缓存] {event_type}: {details}")

    def log_registry_event(self, event_type: str, count: int, duration_ms: int):
        """
        记录注册表事件

        Args:
            event_type: 事件类型（scan/load/save）
            count: 资源数量
            duration_ms: 耗时（毫秒）
        """
        logging.info(f"[注册表] {event_type}: {count}个资源, 耗时{duration_ms}ms")

    def log_error(self, context: str, error: Exception):
        """
        记录错误

        Args:
            context: 错误上下文
            error: 异常对象
        """
        logging.error(f"[错误] {context}: {type(error).__name__}: {error}")

    def log_warning(self, message: str):
        """
        记录警告

        Args:
            message: 警告信息
        """
        logging.warning(f"[警告] {message}")

    def get_recent_errors(self, count: int = 10) -> List[str]:
        """
        获取最近的错误日志

        Args:
            count: 返回的错误条数

        Returns:
            错误日志列表
        """
        try:
            if not self.error_log.exists():
                return []

            with open(self.error_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-count:]] if lines else []

        except Exception as e:
            self._logger.warning(f"读取错误日志失败: {e}")
            return []

    def get_log_stats(self) -> Dict[str, Any]:
        """
        获取日志统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "log_dir": str(self.log_dir),
            "initialized": self._initialized,
            "main_log": {},
            "error_log": {}
        }

        try:
            # 主日志统计
            if self.main_log.exists():
                main_stat = self.main_log.stat()
                with open(self.main_log, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)

                stats["main_log"] = {
                    "path": str(self.main_log),
                    "size_mb": main_stat.st_size / (1024 * 1024),
                    "line_count": line_count,
                    "modified": datetime.fromtimestamp(main_stat.st_mtime).isoformat()
                }

            # 错误日志统计
            if self.error_log.exists():
                error_stat = self.error_log.stat()
                with open(self.error_log, 'r', encoding='utf-8') as f:
                    error_count = sum(1 for _ in f)

                stats["error_log"] = {
                    "path": str(self.error_log),
                    "size_mb": error_stat.st_size / (1024 * 1024),
                    "error_count": error_count,
                    "modified": datetime.fromtimestamp(error_stat.st_mtime).isoformat()
                }

        except Exception as e:
            stats["error"] = str(e)

        return stats

    def cleanup_old_logs(self, days: int = 30):
        """
        清理旧日志文件

        Args:
            days: 保留最近N天的日志

        注意：当前版本依赖 RotatingFileHandler 的自动轮转，
              此方法预留用于未来扩展（如按日期归档）
        """
        # 简化实现：依赖 RotatingFileHandler
        # 未来可扩展为：
        # 1. 扫描 logs/ 目录下的旧日志文件
        # 2. 删除超过 N 天的文件
        # 3. 压缩归档
        pass

    def set_level(self, level: str):
        """
        动态调整日志级别

        Args:
            level: 新的日志级别
        """
        try:
            log_level = getattr(logging, level.upper(), logging.INFO)
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)
            self._logger.info(f"日志级别已调整为: {level}")
        except Exception as e:
            self._logger.error(f"调整日志级别失败: {e}")

    def is_initialized(self) -> bool:
        """
        检查日志系统是否已初始化

        Returns:
            是否已初始化
        """
        return self._initialized
