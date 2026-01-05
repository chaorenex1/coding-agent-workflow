#!/usr/bin/env python3
"""
memex-cli 事件流解析器

基于真实 JSONL 格式设计，支持：
- UTF-16 LE / UTF-8 自动检测
- BOM 处理
- run_id 提取
- 工具调用链追踪
- 输出内容提取
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedEvent:
    """解析后的事件"""
    version: int
    type: str
    timestamp: datetime
    run_id: str
    action: Optional[str] = None
    output: Optional[str] = None
    tool_name: Optional[str] = None
    tool_id: Optional[str] = None
    ok: Optional[bool] = None
    raw: Dict = field(default_factory=dict)


@dataclass
class EventStream:
    """完整的事件流"""
    run_id: str
    session_id: Optional[str]
    model: Optional[str]
    cwd: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    events: List[ParsedEvent]

    # 统计信息
    total_events: int = 0
    tool_calls: int = 0
    successful_tools: int = 0
    failed_tools: int = 0

    def get_assistant_outputs(self) -> List[str]:
        """获取所有 AI 输出"""
        outputs = []
        for e in self.events:
            if e.type == "assistant.output" and e.output:
                outputs.append(e.output)
        return outputs

    def get_tool_chain(self) -> List[Tuple[str, bool]]:
        """获取工具调用链：[(tool_name, success), ...]"""
        chain = []
        for e in self.events:
            if e.type == "tool.result" and e.tool_name:
                chain.append((e.tool_name, e.ok or False))
        return chain

    def get_final_output(self) -> str:
        """获取最终输出（最后一个 assistant.output）"""
        outputs = self.get_assistant_outputs()
        return outputs[-1] if outputs else ""


class MemexEventParser:
    """memex-cli 事件解析器"""

    @staticmethod
    def detect_encoding(filepath: Path) -> str:
        """自动检测文件编码"""
        with open(filepath, 'rb') as f:
            raw_data = f.read(1024)

        # 检查 UTF-16 LE BOM
        if raw_data.startswith(b'\xff\xfe'):
            return 'utf-16-le'

        # 检查 UTF-8 BOM
        if raw_data.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'

        # 默认 UTF-8
        return 'utf-8'

    @staticmethod
    def parse_jsonl(filepath: Path) -> List[ParsedEvent]:
        """解析 JSONL 文件为事件列表"""
        encoding = MemexEventParser.detect_encoding(filepath)

        events = []
        with open(filepath, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip().lstrip('\ufeff')  # 移除 BOM
                if not line:
                    continue

                try:
                    raw = json.loads(line)
                    event = MemexEventParser._parse_event(raw)
                    events.append(event)
                except json.JSONDecodeError as e:
                    print(f"Warning: Line {line_num} JSON 解析失败: {e}")
                except Exception as e:
                    print(f"Warning: Line {line_num} 处理失败: {e}")

        return events

    @staticmethod
    def _parse_event(raw: Dict) -> ParsedEvent:
        """解析单个事件"""
        ts_str = raw.get('ts', '')
        try:
            timestamp = datetime.fromisoformat(ts_str.replace('+00:00', ''))
        except:
            timestamp = datetime.now()

        event = ParsedEvent(
            version=raw.get('v', 1),
            type=raw.get('type', 'unknown'),
            timestamp=timestamp,
            run_id=raw.get('run_id', ''),
            action=raw.get('action'),
            output=raw.get('output'),
            raw=raw
        )

        # 工具相关字段
        if 'tool' in raw:
            event.tool_name = raw['tool']
        if 'id' in raw:
            event.tool_id = raw['id']
        if 'ok' in raw:
            event.ok = raw['ok']

        return event

    @staticmethod
    def parse_stream(filepath: Path) -> EventStream:
        """解析完整事件流"""
        events = MemexEventParser.parse_jsonl(filepath)

        if not events:
            raise ValueError("事件流为空")

        # 提取元数据
        run_id = events[0].run_id
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        duration = (end_time - start_time).total_seconds()

        # 从 event.start 提取额外信息
        session_id = None
        model = None
        cwd = None

        for e in events:
            if e.type == "event.start" and e.output:
                try:
                    output_data = json.loads(e.output)
                    session_id = output_data.get('session_id')
                    model = output_data.get('model')
                    cwd = output_data.get('cwd')
                except:
                    pass
                break

        # 统计工具调用
        tool_calls = sum(1 for e in events if e.type == "tool.request")
        tool_results = [e for e in events if e.type == "tool.result"]
        successful_tools = sum(1 for e in tool_results if e.ok)
        failed_tools = sum(1 for e in tool_results if not e.ok)

        # 将 tool_name 从 tool.request 关联到 tool.result
        tool_map = {}
        for e in events:
            if e.type == "tool.request" and e.tool_id and e.tool_name:
                tool_map[e.tool_id] = e.tool_name

        for e in events:
            if e.type == "tool.result" and e.tool_id and e.tool_id in tool_map:
                e.tool_name = tool_map[e.tool_id]

        return EventStream(
            run_id=run_id,
            session_id=session_id,
            model=model,
            cwd=cwd,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            events=events,
            total_events=len(events),
            tool_calls=tool_calls,
            successful_tools=successful_tools,
            failed_tools=failed_tools
        )

    @staticmethod
    def extract_run_id(jsonl_output: str) -> Optional[str]:
        """从 JSONL 输出字符串快速提取 run_id"""
        for line in jsonl_output.split('\n'):
            line = line.strip().lstrip('\ufeff')
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get('type') == 'event.start':
                    return event.get('run_id')
            except:
                continue
        return None


# 使用示例
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python event_parser.py <events.jsonl>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    parser = MemexEventParser()

    try:
        stream = parser.parse_stream(filepath)

        print(f"Run ID: {stream.run_id}")
        print(f"Model: {stream.model}")
        print(f"Duration: {stream.duration_seconds:.2f}s")
        print(f"Events: {stream.total_events}")
        print(f"Tool Calls: {stream.tool_calls} (成功: {stream.successful_tools}, 失败: {stream.failed_tools})")
        print(f"\nTool Chain: {stream.get_tool_chain()}")
        print(f"\nFinal Output: {stream.get_final_output()[:200]}...")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
