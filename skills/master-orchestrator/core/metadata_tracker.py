#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metadata Tracker - 轻量级执行元数据追踪器

纯流式架构：不缓冲输出内容，仅提取和追踪关键元数据。

Design:
- 零缓冲：不保存完整输出，仅追踪元数据
- 实时提取：边读边提取 run_id、错误信息等
- 轻量级：内存占用最小化
"""

import re
import json
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetadata:
    """
    轻量级执行元数据（纯流式架构 - 不保存输出内容）

    Purpose:
        仅追踪执行过程的关键元数据，不缓冲任何输出内容。
        所有输出直接流向终端，此类仅负责提取必要的元数据。

    Attributes:
        run_id: 执行的唯一标识符
        success: 执行是否成功
        error: 错误信息（如果失败）
        line_count: 输出行数统计
        duration_seconds: 执行耗时
        returncode: 进程退出码

        # 性能指标
        avg_line_processing_ms: 平均每行处理时间（毫秒）
        callback_errors: 回调异常次数

        # 元数据提取标志
        run_id_extracted: run_id 是否已提取
        error_detected: 是否检测到错误关键词
    """

    # 核心元数据
    run_id: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    line_count: int = 0
    duration_seconds: float = 0.0
    returncode: Optional[int] = None

    # 性能指标
    avg_line_processing_ms: float = 0.0
    callback_errors: int = 0

    # 内部状态
    run_id_extracted: bool = field(default=False, repr=False)
    error_detected: bool = field(default=False, repr=False)
    _error_lines: list = field(default_factory=list, repr=False)

    def extract_from_line(self, line: str, line_processing_ms: float = 0.0):
        """
        从单行输出中提取元数据（无缓冲）

        Args:
            line: 输出行
            line_processing_ms: 该行处理耗时（用于性能统计）

        Note:
            此方法不保存 line 内容，仅提取元数据。
            实现了边读边提取的流式处理模式。
        """
        self.line_count += 1

        # 更新性能指标
        if line_processing_ms > 0:
            self.avg_line_processing_ms = (
                (self.avg_line_processing_ms * (self.line_count - 1) + line_processing_ms)
                / self.line_count
            )

        # 提取 run_id（仅一次）
        if not self.run_id_extracted:
            extracted_id = self._parse_run_id(line)
            if extracted_id:
                self.run_id = extracted_id
                self.run_id_extracted = True
                logger.debug(f"Extracted run_id: {self.run_id}")

        # 检测错误信号
        if not self.error_detected and self._is_error_line(line):
            self.error_detected = True
            # 保存错误行（最多3行，避免过多内存占用）
            if len(self._error_lines) < 3:
                self._error_lines.append(line.strip())

    def _parse_run_id(self, line: str) -> Optional[str]:
        """
        从输出行解析 run_id

        支持的格式:
        1. JSONL: {"type":"run.start","run_id":"abc123"}
        2. Plain text: run_id: abc123 或 Run ID: abc123
        3. Markdown: Run ID: `abc123`

        Returns:
            提取到的 run_id，或 None
        """
        # 尝试 JSON 解析
        if line.strip().startswith('{'):
            try:
                data = json.loads(line)
                if 'run_id' in data:
                    return data['run_id']
            except json.JSONDecodeError:
                pass

        # 尝试正则匹配（文本格式）
        patterns = [
            r'run[_\s-]id[:\s]+["`]?([a-zA-Z0-9_-]+)["`]?',
            r'Run\s+ID[:\s]+["`]?([a-zA-Z0-9_-]+)["`]?',
        ]

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _is_error_line(self, line: str) -> bool:
        """
        检测是否为错误输出行

        Keywords:
            error, failed, exception, traceback, fatal, critical

        Returns:
            True if error detected
        """
        error_keywords = [
            'error', 'failed', 'exception', 'traceback',
            'fatal', 'critical', '[ERROR]', '[FAIL]'
        ]

        line_lower = line.lower()
        return any(kw in line_lower for kw in error_keywords)

    def finalize(self, returncode: int, stderr: Optional[str] = None):
        """
        完成元数据提取（进程结束时调用）

        Args:
            returncode: 进程退出码
            stderr: 标准错误输出（如果有）
        """
        self.returncode = returncode
        self.success = (returncode == 0)

        # 如果失败且未提取到错误信息，使用 stderr
        if not self.success and not self.error:
            if self._error_lines:
                # 使用检测到的错误行
                self.error = "\n".join(self._error_lines)
            elif stderr:
                # 使用 stderr（截取前500字符）
                self.error = stderr[:500] + ("..." if len(stderr) > 500 else "")
            else:
                self.error = f"Process failed with exit code {returncode}"

        logger.debug(
            f"Metadata finalized: success={self.success}, "
            f"lines={self.line_count}, run_id={self.run_id}"
        )

    def get_summary_line(self) -> str:
        """
        生成简短的状态行（纯流式架构的最终输出）

        Returns:
            格式: [完成] 后端 | 耗时 45.2s | 1234 行 | 成功
                 [失败] 后端 | 耗时 12.3s | 错误: ...
        """
        status = "完成" if self.success else "失败"

        parts = [
            f"[{status}]",
            f"耗时 {self.duration_seconds:.2f}s",
            f"{self.line_count} 行"
        ]

        if self.run_id:
            parts.append(f"run_id: {self.run_id[:8]}...")

        if not self.success and self.error:
            # 错误信息截取前100字符
            error_brief = self.error.split('\n')[0][:100]
            parts.append(f"错误: {error_brief}")

        return " | ".join(parts)

    @classmethod
    def from_legacy_output(
        cls,
        output: str,
        success: bool,
        error: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> 'ExecutionMetadata':
        """
        从旧的缓冲输出创建元数据（兼容性方法）

        用于从旧架构迁移到纯流式架构的过渡期。

        Args:
            output: 完整输出内容
            success: 执行是否成功
            error: 错误信息
            run_id: 执行 ID

        Returns:
            ExecutionMetadata 实例
        """
        metadata = cls(
            run_id=run_id,
            success=success,
            error=error,
            line_count=len(output.split('\n')) if output else 0
        )

        # 如果 run_id 未提供，尝试从输出中提取
        if not run_id and output:
            for line in output.split('\n')[:50]:  # 仅检查前50行
                extracted = metadata._parse_run_id(line)
                if extracted:
                    metadata.run_id = extracted
                    break

        return metadata


def create_metadata_tracker() -> ExecutionMetadata:
    """
    创建元数据追踪器的便捷函数

    Returns:
        新的 ExecutionMetadata 实例
    """
    return ExecutionMetadata()
