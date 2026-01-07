#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse Hook: Execution Logger

Logs all tool executions for auditing purposes.
This hook runs AFTER tool execution completes.

Exit Codes:
    0 - Always (post hooks don't block)

Environment Variables (set by Claude Code):
    CLAUDE_TOOL_NAME    - Name of the tool that was called
    CLAUDE_TOOL_INPUT   - JSON input that was provided
    CLAUDE_TOOL_OUTPUT  - Output from the tool execution
    CLAUDE_SESSION_ID   - Current session identifier
    CLAUDE_PROJECT_DIR  - Project root directory

Usage in .claude/settings.json:
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/logger.py"
        }]
      }
    ]
  }
}
"""

import sys
import os
import io
import json
import html
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# =============================================================================
# Windows UTF-8 Encoding Fix
# =============================================================================

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# =============================================================================
# Configuration
# =============================================================================

# Log directory
LOG_DIR = Path.home() / ".claude-hooks" / "audit"

# Maximum length for logged content (truncate longer content)
MAX_INPUT_LENGTH = 500
MAX_OUTPUT_LENGTH = 1000

# Tools to log with full detail
DETAILED_TOOLS = {"Bash", "Write", "Edit", "MultiEdit", "NotebookEdit"}

# Tools to skip logging (too noisy)
SKIP_TOOLS = set()  # Add tool names to skip if needed

# =============================================================================
# Utilities
# =============================================================================

def truncate(text: str, max_length: int) -> str:
    """Truncate text with ellipsis indicator."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + f"... [truncated, total {len(text)} chars]"


def clean_encoding(text: str) -> str:
    """Clean up encoding issues in text."""
    if not text:
        return text
    # Decode HTML entities
    text = html.unescape(text)
    if '&amp;' in text:
        text = html.unescape(text)
    return text


def compute_hash(content: str) -> str:
    """Compute short hash of content for deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def parse_json_safe(text: str) -> Optional[Dict]:
    """Safely parse JSON, return None on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_key_info(tool_name: str, tool_input: str) -> Dict[str, Any]:
    """Extract key information from tool input based on tool type."""
    data = parse_json_safe(tool_input) or {}
    
    if tool_name == "Bash":
        return {
            "command": data.get("command", tool_input)[:200],
            "cwd": data.get("cwd", ""),
        }
    
    elif tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return {
            "path": data.get("file_path") or data.get("path", ""),
            "content_hash": compute_hash(str(data.get("content", ""))),
        }
    
    elif tool_name in ("Read", "Glob", "Grep"):
        return {
            "path": data.get("path") or data.get("pattern", ""),
        }
    
    elif tool_name == "WebFetch":
        return {
            "url": data.get("url", "")[:200],
        }
    
    elif tool_name == "WebSearch":
        return {
            "query": data.get("query", "")[:100],
        }
    
    else:
        # Generic extraction
        return {
            "input_preview": truncate(tool_input, 100),
        }


def determine_outcome(tool_output: str) -> str:
    """Determine if execution was successful based on output."""
    if not tool_output:
        return "unknown"
    
    output_lower = tool_output.lower()
    
    # Check for error indicators
    error_indicators = [
        "error:", "exception:", "failed", "failure",
        "traceback", "errno", "permission denied",
        "not found", "no such file", "command not found"
    ]
    
    for indicator in error_indicators:
        if indicator in output_lower:
            return "error"
    
    # Check for success indicators
    success_indicators = [
        "success", "completed", "done", "ok", "created", "updated"
    ]
    
    for indicator in success_indicators:
        if indicator in output_lower:
            return "success"
    
    return "completed"

# =============================================================================
# Main Logger
# =============================================================================

def log_execution():
    """Log tool execution details."""
    # Get environment variables
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "unknown")
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "")
    tool_output = os.environ.get("CLAUDE_TOOL_OUTPUT", "")
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    
    # Skip if tool is in skip list
    if tool_name in SKIP_TOOLS:
        return
    
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Prepare log entry
    timestamp = datetime.now()
    
    entry = {
        "timestamp": timestamp.isoformat(),
        "session_id": session_id,
        "tool": tool_name,
        "project": project_dir,
        "outcome": determine_outcome(tool_output),
    }
    
    # Add tool-specific info
    entry["details"] = extract_key_info(tool_name, tool_input)
    
    # Add detailed input/output for important tools
    if tool_name in DETAILED_TOOLS:
        entry["input_full"] = truncate(tool_input, MAX_INPUT_LENGTH)
        entry["output_preview"] = truncate(tool_output, MAX_OUTPUT_LENGTH)
    
    # Write to daily log file
    log_file = LOG_DIR / f"{timestamp.strftime('%Y%m%d')}.jsonl"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # Log to stderr but don't fail
        print(f"Warning: Failed to write audit log: {e}", file=sys.stderr)
    
    # Also write summary to session log
    session_log = LOG_DIR / f"session_{session_id}.jsonl"
    
    try:
        summary = {
            "timestamp": timestamp.isoformat(),
            "tool": tool_name,
            "outcome": entry["outcome"],
            "details": entry["details"],
        }
        with open(session_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Session log is optional


def main():
    """Main entry point."""
    try:
        log_execution()
    except Exception as e:
        # Post hooks should never fail
        print(f"Warning: Logger hook error: {e}", file=sys.stderr)
    
    # Always exit 0 - post hooks don't block
    sys.exit(0)


if __name__ == "__main__":
    main()
