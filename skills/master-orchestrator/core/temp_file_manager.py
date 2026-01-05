#!/usr/bin/env python3
"""
TempFileManager - 临时文件管理

管理 ~/.memex/orchestrator/temp/ 目录，提供：
- 创建和清理临时文件/目录
- TTL 过期机制
- 上下文管理器（自动清理）
- 命名空间隔离
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager
import logging


logger = logging.getLogger(__name__)


class TempFileManager:
    """
    临时文件管理器 - 管理 ~/.memex/orchestrator/temp/ 目录

    功能：
    - 创建临时文件和目录
    - TTL 过期清理
    - 上下文管理器支持
    - 命名空间隔离

    使用示例：
        manager = TempFileManager(temp_dir=Path("temp"))

        # 创建临时文件
        tmp_file = manager.create_temp_file(prefix="data_", suffix=".json")
        tmp_file.write_text('{"key": "value"}')

        # 使用上下文管理器（自动清理）
        with manager.temp_file(prefix="session_") as f:
            f.write_text("temporary data")
            # 离开作用域后自动删除

        # 清理过期文件
        removed = manager.cleanup_expired()
    """

    def __init__(self, temp_dir: Path, ttl_seconds: int = 3600):
        """
        初始化临时文件管理器

        Args:
            temp_dir: 临时文件目录
            ttl_seconds: 文件过期时间（秒），默认1小时
        """
        self.temp_dir = Path(temp_dir).expanduser()
        self.ttl_seconds = ttl_seconds

        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"TempFileManager initialized at {self.temp_dir}")

    def create_temp_file(
        self,
        prefix: str = "",
        suffix: str = "",
        namespace: str = "default"
    ) -> Path:
        """
        创建临时文件

        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀（如 .json, .txt）
            namespace: 命名空间（用于隔离不同模块的临时文件）

        Returns:
            临时文件路径
        """
        try:
            # 创建命名空间目录
            namespace_dir = self.temp_dir / namespace
            namespace_dir.mkdir(parents=True, exist_ok=True)

            # 使用 tempfile 生成唯一文件名
            fd, tmp_path = tempfile.mkstemp(
                prefix=prefix,
                suffix=suffix,
                dir=namespace_dir
            )

            # 关闭文件描述符（我们只需要路径）
            os.close(fd)

            tmp_file = Path(tmp_path)
            logger.debug(f"Created temp file: {tmp_file}")

            return tmp_file

        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            raise

    def create_temp_dir(
        self,
        prefix: str = "",
        namespace: str = "default"
    ) -> Path:
        """
        创建临时目录

        Args:
            prefix: 目录名前缀
            namespace: 命名空间

        Returns:
            临时目录路径
        """
        try:
            # 创建命名空间目录
            namespace_dir = self.temp_dir / namespace
            namespace_dir.mkdir(parents=True, exist_ok=True)

            # 使用 tempfile 生成唯一目录名
            tmp_dir = tempfile.mkdtemp(
                prefix=prefix,
                dir=namespace_dir
            )

            tmp_path = Path(tmp_dir)
            logger.debug(f"Created temp dir: {tmp_path}")

            return tmp_path

        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            raise

    @contextmanager
    def temp_file(
        self,
        prefix: str = "",
        suffix: str = "",
        namespace: str = "default"
    ):
        """
        临时文件上下文管理器（自动清理）

        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀
            namespace: 命名空间

        Yields:
            临时文件路径

        使用示例：
            with manager.temp_file(prefix="data_", suffix=".json") as f:
                f.write_text('{"key": "value"}')
                process_file(f)
            # 离开作用域后自动删除
        """
        tmp_file = self.create_temp_file(prefix, suffix, namespace)

        try:
            yield tmp_file
        finally:
            # 清理临时文件
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {tmp_file}")
            except Exception as e:
                logger.warning(f"清理临时文件失败 {tmp_file}: {e}")

    @contextmanager
    def temp_directory(
        self,
        prefix: str = "",
        namespace: str = "default"
    ):
        """
        临时目录上下文管理器（自动清理）

        Args:
            prefix: 目录名前缀
            namespace: 命名空间

        Yields:
            临时目录路径

        使用示例：
            with manager.temp_directory(prefix="workspace_") as d:
                (d / "file.txt").write_text("data")
                process_directory(d)
            # 离开作用域后自动删除目录及其内容
        """
        tmp_dir = self.create_temp_dir(prefix, namespace)

        try:
            yield tmp_dir
        finally:
            # 清理临时目录
            try:
                if tmp_dir.exists():
                    shutil.rmtree(tmp_dir)
                    logger.debug(f"Cleaned up temp dir: {tmp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败 {tmp_dir}: {e}")

    def cleanup_expired(self, namespace: Optional[str] = None) -> int:
        """
        清理过期的临时文件/目录

        Args:
            namespace: 只清理指定命名空间（None 表示所有）

        Returns:
            清理的文件/目录数量
        """
        removed_count = 0
        current_time = time.time()

        try:
            # 确定扫描目录
            if namespace:
                scan_dirs = [self.temp_dir / namespace]
            else:
                scan_dirs = [self.temp_dir]

            for scan_dir in scan_dirs:
                if not scan_dir.exists():
                    continue

                # 遍历所有文件和目录
                for item in scan_dir.rglob("*"):
                    try:
                        # 跳过命名空间目录本身
                        if item == scan_dir:
                            continue

                        # 获取最后修改时间
                        mtime = item.stat().st_mtime
                        age_seconds = current_time - mtime

                        # 检查是否过期
                        if age_seconds > self.ttl_seconds:
                            if item.is_file():
                                item.unlink()
                                removed_count += 1
                                logger.debug(f"Removed expired file: {item}")
                            elif item.is_dir():
                                shutil.rmtree(item)
                                removed_count += 1
                                logger.debug(f"Removed expired dir: {item}")

                    except Exception as e:
                        logger.warning(f"清理项目失败 {item}: {e}")

            if removed_count > 0:
                logger.info(f"清理了 {removed_count} 个过期临时文件/目录")

        except Exception as e:
            logger.error(f"清理过期文件失败: {e}")

        return removed_count

    def cleanup_namespace(self, namespace: str) -> int:
        """
        清理指定命名空间的所有临时文件/目录

        Args:
            namespace: 命名空间名称

        Returns:
            清理的文件/目录数量
        """
        removed_count = 0
        namespace_dir = self.temp_dir / namespace

        try:
            if namespace_dir.exists():
                # 统计删除数量
                for item in namespace_dir.rglob("*"):
                    if item.is_file():
                        removed_count += 1

                # 删除整个命名空间目录
                shutil.rmtree(namespace_dir)
                logger.info(f"清理命名空间 '{namespace}': {removed_count} 个文件/目录")

        except Exception as e:
            logger.warning(f"清理命名空间失败 {namespace}: {e}")

        return removed_count

    def cleanup_all(self) -> int:
        """
        清理所有临时文件/目录

        Returns:
            清理的文件/目录数量
        """
        removed_count = 0

        try:
            if self.temp_dir.exists():
                # 统计删除数量
                for item in self.temp_dir.rglob("*"):
                    if item.is_file():
                        removed_count += 1

                # 删除所有内容（保留根目录）
                for item in self.temp_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

                logger.info(f"清理所有临时文件: {removed_count} 个文件/目录")

        except Exception as e:
            logger.warning(f"清理所有临时文件失败: {e}")

        return removed_count

    def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        获取临时文件统计信息

        Args:
            namespace: 只统计指定命名空间（None 表示所有）

        Returns:
            统计信息字典
        """
        stats = {
            "temp_dir": str(self.temp_dir),
            "ttl_seconds": self.ttl_seconds,
            "total_files": 0,
            "total_dirs": 0,
            "total_size_bytes": 0,
            "expired_files": 0,
            "namespaces": {}
        }

        try:
            if not self.temp_dir.exists():
                stats["status"] = "not_exists"
                return stats

            # 确定扫描目录
            if namespace:
                scan_dir = self.temp_dir / namespace
                if not scan_dir.exists():
                    stats["status"] = f"namespace '{namespace}' not found"
                    return stats
                scan_dirs = {namespace: scan_dir}
            else:
                # 扫描所有命名空间
                scan_dirs = {}
                for item in self.temp_dir.iterdir():
                    if item.is_dir():
                        scan_dirs[item.name] = item

            current_time = time.time()

            # 统计每个命名空间
            for ns_name, ns_dir in scan_dirs.items():
                ns_stats = {
                    "files": 0,
                    "dirs": 0,
                    "size_bytes": 0,
                    "expired": 0
                }

                for item in ns_dir.rglob("*"):
                    try:
                        if item.is_file():
                            ns_stats["files"] += 1
                            ns_stats["size_bytes"] += item.stat().st_size

                            # 检查是否过期
                            mtime = item.stat().st_mtime
                            if (current_time - mtime) > self.ttl_seconds:
                                ns_stats["expired"] += 1

                        elif item.is_dir():
                            ns_stats["dirs"] += 1

                    except Exception as e:
                        logger.warning(f"统计项目失败 {item}: {e}")

                stats["namespaces"][ns_name] = ns_stats
                stats["total_files"] += ns_stats["files"]
                stats["total_dirs"] += ns_stats["dirs"]
                stats["total_size_bytes"] += ns_stats["size_bytes"]
                stats["expired_files"] += ns_stats["expired"]

            stats["status"] = "ok"

        except Exception as e:
            stats["status"] = "error"
            stats["error"] = str(e)
            logger.error(f"获取统计信息失败: {e}")

        return stats

    def list_namespaces(self) -> List[str]:
        """
        列出所有命名空间

        Returns:
            命名空间列表
        """
        namespaces = []

        try:
            if self.temp_dir.exists():
                for item in self.temp_dir.iterdir():
                    if item.is_dir():
                        namespaces.append(item.name)

        except Exception as e:
            logger.warning(f"列出命名空间失败: {e}")

        return sorted(namespaces)
