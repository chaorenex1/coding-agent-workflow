#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for stream output functionality

Tests real-time streaming output for master-orchestrator
"""

import sys
import json
import subprocess
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_stream_handler_basic():
    """Test StreamHandler basic functionality"""
    from core.stream_handler import StreamHandler

    lines_received = []

    def callback(line):
        lines_received.append(line)

    handler = StreamHandler(callback=callback, format_output=False)

    # Test JSON line
    json_line = '{"type":"assistant.output","output":"test message"}'
    handler.process_line(json_line)

    assert len(lines_received) == 1
    assert "test message" in lines_received[0] or json_line in lines_received[0]

    print("[PASS] StreamHandler basic test")


def test_output_formatter():
    """Test OutputFormatter event formatting"""
    from core.output_formatter import OutputFormatter

    # Test assistant output formatting
    event = {
        "type": "assistant.output",
        "output": "Hello, world!"
    }

    formatted = OutputFormatter.format_event(event)
    assert formatted is not None
    assert "Hello, world!" in formatted

    print("[PASS] OutputFormatter test")


def test_stream_buffer():
    """Test StreamBuffer (deprecated - now tests ExecutionMetadata)"""
    # 纯流式架构：使用 ExecutionMetadata 替代 StreamBuffer
    from core.metadata_tracker import ExecutionMetadata

    metadata = ExecutionMetadata()

    metadata.extract_from_line("line 1\n")
    metadata.extract_from_line("line 2\n")
    metadata.extract_from_line("line 3\n")

    # 验证：元数据正确追踪
    assert metadata.line_count == 3

    # 验证：不缓冲输出内容
    # （与 StreamBuffer 不同，ExecutionMetadata 不保存输出）

    print("[PASS] StreamBuffer test (migrated to ExecutionMetadata)")


def test_cli_stream_parameter():
    """Test that --no-stream and --stream-format parameters are recognized"""
    result = subprocess.run(
        [sys.executable, "-m", "master-orchestrator", "--help"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent
    )

    assert result.returncode == 0
    assert "--no-stream" in result.stdout
    assert "--stream-format" in result.stdout

    print("[PASS] CLI --no-stream and --stream-format parameters recognized")


def test_stream_dry_run():
    """Test streaming is enabled by default in dry-run mode"""
    result = subprocess.run(
        [sys.executable, "-m", "master-orchestrator",
         "hello world", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    # Dry-run should work with default streaming
    assert "Dry-Run" in result.stdout or "dry-run" in result.stdout.lower()

    print("[PASS] Default streaming with dry-run test")


def test_text_format_handler():
    """Test StreamHandler with text format (format_output=False)"""
    from core.stream_handler import StreamHandler

    lines_received = []

    def callback(line):
        lines_received.append(line)

    # Text format: format_output=False
    handler = StreamHandler(callback=callback, format_output=False)

    # Test with both JSON and non-JSON lines
    handler.process_line('{"type":"assistant.output","output":"Hello"}')
    handler.process_line('This is plain text output')
    handler.process_line('Another line')

    # All lines should be passed through without parsing
    assert len(lines_received) == 3
    assert '{"type":"assistant.output","output":"Hello"}' in lines_received[0]
    assert 'This is plain text output' in lines_received[1]
    assert 'Another line' in lines_received[2]

    print("[PASS] Text format handler test")


def test_no_stream_parameter():
    """Test that --no-stream disables streaming"""
    result = subprocess.run(
        [sys.executable, "-m", "master-orchestrator",
         "hello world", "--no-stream", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    # Should still work in dry-run mode
    assert "Dry-Run" in result.stdout or "dry-run" in result.stdout.lower()

    print("[PASS] --no-stream parameter test")


def test_stream_format_parameter():
    """Test that --stream-format accepts text and jsonl"""
    # Test with text format
    result1 = subprocess.run(
        [sys.executable, "-m", "master-orchestrator",
         "hello world", "--stream-format", "text", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    assert result1.returncode == 0

    # Test with jsonl format
    result2 = subprocess.run(
        [sys.executable, "-m", "master-orchestrator",
         "hello world", "--stream-format", "jsonl", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    assert result2.returncode == 0

    print("[PASS] --stream-format parameter test")


if __name__ == "__main__":
    print("Running stream output tests...\n")

    try:
        test_stream_handler_basic()
        test_output_formatter()
        test_stream_buffer()
        test_cli_stream_parameter()
        test_stream_dry_run()
        test_text_format_handler()
        test_no_stream_parameter()
        test_stream_format_parameter()

        print("\n[SUCCESS] All stream output tests passed!")
        sys.exit(0)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
