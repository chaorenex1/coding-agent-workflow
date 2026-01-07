#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Formatter - JSONL 事件格式化工具

将 memex-cli 输出的 JSONL 事件格式化为人类可读的输出。
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OutputFormatter:
    """
    格式化 JSONL 事件为可读输出

    支持的事件类型：
    - event.start: 任务开始
    - assistant.output: AI 输出
    - tool.call: 工具调用
    - tool.result: 工具结果
    - event.end: 任务结束
    """

    # 事件类型图标（可选，支持无 emoji 环境）
    ICONS = {
        'event.start': '🚀',
        'assistant.output': '💬',
        'tool.call': '🔧',
        'tool.result': '✅',
        'event.end': '🏁',
        'error': '❌',
        'warning': '⚠️'
    }

    # 是否使用图标（可通过环境变量控制）
    USE_ICONS = True

    @classmethod
    def format_event(cls, event: Dict[str, Any]) -> Optional[str]:
        """
        格式化事件为可读文本

        Args:
            event: JSONL 事件字典

        Returns:
            格式化后的字符串，如果不需要显示则返回 None
        """
        event_type = event.get('type', 'unknown')

        # 根据事件类型分发到对应的格式化方法
        formatter_map = {
            'event.start': cls.format_event_start,
            'assistant.output': cls.format_assistant_output,
            'tool.call': cls.format_tool_call,
            'tool.result': cls.format_tool_result,
            'event.end': cls.format_event_end,
        }

        formatter = formatter_map.get(event_type)
        if formatter:
            try:
                return formatter(event)
            except Exception as e:
                logger.error(f"Failed to format event {event_type}: {e}")
                return None

        # 未知事件类型，不输出或输出调试信息
        logger.debug(f"Unknown event type: {event_type}")
        return None

    @classmethod
    def format_event_start(cls, event: Dict[str, Any]) -> str:
        """格式化任务开始事件"""
        icon = cls.ICONS['event.start'] if cls.USE_ICONS else '[START]'
        run_id = event.get('run_id', 'unknown')
        model = event.get('output', {}).get('model', 'unknown')

        return f"{icon} 任务开始 | Run ID: {run_id[:8]}... | Model: {model}"

    @classmethod
    def format_assistant_output(cls, event: Dict[str, Any]) -> Optional[str]:
        """格式化 AI 输出事件"""
        output = event.get('output')

        if not output:
            return None

        icon = cls.ICONS['assistant.output'] if cls.USE_ICONS else '[AI]'

        # 处理多行输出
        lines = output.strip().split('\n')

        if len(lines) == 1:
            return f"{icon} {output.strip()}"
        else:
            # 多行输出，添加缩进
            formatted_lines = [f"{icon} {lines[0]}"]
            for line in lines[1:]:
                formatted_lines.append(f"   {line}")
            return '\n'.join(formatted_lines)

    @classmethod
    def format_tool_call(cls, event: Dict[str, Any]) -> str:
        """格式化工具调用事件"""
        icon = cls.ICONS['tool.call'] if cls.USE_ICONS else '[TOOL]'
        tool_name = event.get('tool_name', 'unknown')
        tool_id = event.get('tool_id', '')

        # 提取工具参数（如果有）
        args = event.get('args', {})
        if args:
            # 简化参数显示
            args_preview = str(args)[:50]
            if len(str(args)) > 50:
                args_preview += '...'
            return f"{icon} 调用工具: {tool_name} | 参数: {args_preview}"
        else:
            return f"{icon} 调用工具: {tool_name}"

    @classmethod
    def format_tool_result(cls, event: Dict[str, Any]) -> str:
        """格式化工具结果事件"""
        tool_name = event.get('tool_name', 'unknown')
        ok = event.get('ok', False)

        if ok:
            icon = cls.ICONS['tool.result'] if cls.USE_ICONS else '[OK]'
            return f"{icon} 工具完成: {tool_name}"
        else:
            icon = cls.ICONS['error'] if cls.USE_ICONS else '[ERROR]'
            error = event.get('error', 'unknown error')
            return f"{icon} 工具失败: {tool_name} | 错误: {error}"

    @classmethod
    def format_event_end(cls, event: Dict[str, Any]) -> str:
        """格式化任务结束事件"""
        icon = cls.ICONS['event.end'] if cls.USE_ICONS else '[END]'
        run_id = event.get('run_id', 'unknown')

        return f"{icon} 任务完成 | Run ID: {run_id[:8]}..."

    @classmethod
    def disable_icons(cls) -> None:
        """禁用图标（用于不支持 emoji 的环境）"""
        cls.USE_ICONS = False

    @classmethod
    def enable_icons(cls) -> None:
        """启用图标"""
        cls.USE_ICONS = True


class ProgressIndicator:
    """
    进度指示器

    显示旋转动画和状态信息
    """

    SPINNERS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def __init__(self, message: str = "处理中"):
        """
        初始化进度指示器

        Args:
            message: 显示的消息
        """
        self.message = message
        self.current_frame = 0
        self.enabled = True

    def next_frame(self) -> str:
        """获取下一帧动画"""
        if not self.enabled:
            return ""

        frame = self.SPINNERS[self.current_frame]
        self.current_frame = (self.current_frame + 1) % len(self.SPINNERS)

        return f"{frame} {self.message}"

    def disable(self) -> None:
        """禁用进度指示器"""
        self.enabled = False

    def enable(self) -> None:
        """启用进度指示器"""
        self.enabled = True
