#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stream Handler - 实时流式输出处理器

处理来自 memex-cli 的实时 JSONL 事件流，提供格式化和回调机制。
"""

import json
import logging
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StreamState:
    """流式输出状态追踪"""
    lines_processed: int = 0
    events_received: int = 0
    current_tool: Optional[str] = None
    last_event_type: Optional[str] = None


class StreamHandler:
    """
    处理实时流式输出

    负责：
    1. 接收 JSONL 事件流
    2. 解析和格式化事件
    3. 调用回调函数输出
    4. 追踪流式状态
    """

    def __init__(
        self,
        callback: Optional[Callable[[str], None]] = None,
        format_output: bool = True,
        show_raw_output: bool = False,
        show_progress: bool = True
    ):
        """
        初始化流处理器

        Args:
            callback: 自定义输出回调函数，默认使用 print
            format_output: 是否格式化 JSONL 事件为可读输出
            show_raw_output: 是否显示原始非 JSON 行
            show_progress: 是否显示进度信息
        """
        self.callback = callback or self.default_callback
        self.format_output = format_output
        self.show_raw_output = show_raw_output
        self.show_progress = show_progress
        self.state = StreamState()

    def default_callback(self, text: str) -> None:
        """默认回调：直接打印到标准输出"""
        print(text, flush=True)

    def process_line(self, line: str) -> None:
        """
        处理单行输出

        Args:
            line: 从 stdout 读取的一行（可能是 JSONL 或原始文本）
        """
        self.state.lines_processed += 1

        # 清理行尾
        line = line.rstrip('\n\r')

        if not line:
            return

        # Text 格式：直接传递所有输出，不解析 JSON
        if not self.format_output:
            # Phase 4: 错误高亮 - 检测错误关键词并高亮显示
            if self._is_error_line(line):
                # 红色高亮错误行
                self.callback(f"\033[91m{line}\033[0m")
            else:
                self.callback(line)
            return

        # JSONL 格式：尝试解析为 JSON 事件
        try:
            event = json.loads(line)
            self.state.events_received += 1
            self._process_event(event)
        except json.JSONDecodeError:
            # 非 JSON 行，可能是调试输出
            if self.show_raw_output:
                self.callback(f"[Raw] {line}")
            logger.debug(f"Non-JSON line: {line[:100]}")
        except Exception as e:
            logger.error(f"Failed to process line: {e}")
            # 失败时降级为原始输出
            if self.show_raw_output:
                self.callback(line)

    def _process_event(self, event: Dict[str, Any]) -> None:
        """
        处理解析后的 JSONL 事件

        Args:
            event: 解析后的事件字典
        """
        event_type = event.get('type', 'unknown')
        self.state.last_event_type = event_type

        if self.format_output:
            # 导入格式化器（避免循环导入）
            from .output_formatter import OutputFormatter

            formatted = OutputFormatter.format_event(event)
            if formatted:
                self.callback(formatted)
        else:
            # 不格式化，直接输出原始 JSON
            self.callback(json.dumps(event, ensure_ascii=False))

    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'lines_processed': self.state.lines_processed,
            'events_received': self.state.events_received,
            'last_event_type': self.state.last_event_type
        }

    def reset(self) -> None:
        """重置状态"""
        self.state = StreamState()

    def _is_error_line(self, line: str) -> bool:
        """
        检测是否为错误输出行（Phase 4：错误高亮）

        Args:
            line: 输出行

        Returns:
            True if error detected
        """
        error_keywords = [
            'error', 'failed', 'exception', 'traceback',
            'fatal', 'critical', '[ERROR]', '[FAIL]',
            'assertion', 'assert false'
        ]

        line_lower = line.lower()
        return any(kw in line_lower for kw in error_keywords)


# ============================================================================
# StreamBuffer - REMOVED (纯流式架构不再需要输出缓冲)
# ============================================================================
#
# ⚠️ StreamBuffer 类已被移除
#
# 原因：纯流式架构不缓冲任何输出，所有输出直接流向终端。
#       使用 ExecutionMetadata 追踪轻量级元数据替代完整输出缓冲。
#
# 迁移指南：
#   旧代码: buffer = StreamBuffer()
#          buffer.append(line)
#          output = buffer.get_full_output()
#
#   新代码: metadata = ExecutionMetadata()
#          metadata.extract_from_line(line)  # 仅提取元数据
#          # 输出直接流向 callback，不缓冲
#
# ============================================================================

class StreamBuffer:
    """
    ⚠️ DEPRECATED AND REMOVED

    此类已在纯流式架构重构中移除。
    如果您的代码依赖此类，请迁移到 ExecutionMetadata。
    """
    def __init__(self, max_size: int = 10_000_000):
        import warnings
        warnings.warn(
            "StreamBuffer is deprecated and removed in pure streaming architecture. "
            "Use ExecutionMetadata instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.lines = []

    def append(self, line: str) -> None:
        """Deprecated: 不再缓冲输出"""
        pass  # No-op

    def get_full_output(self) -> str:
        """Deprecated: 返回空字符串"""
        return ""

    def get_line_count(self) -> int:
        """Deprecated: 返回 0"""
        return 0

    def clear(self) -> None:
        """Deprecated: No-op"""
        pass
