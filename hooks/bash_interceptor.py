#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreToolUse Hook: Bash & File Operation Interceptor

Intercepts all Bash commands and file operations (Write/Edit/MultiEdit),
forcing them through the master-orchestrator.

Exit Codes:
    0 - Allow execution
    1 - Block execution (shows reason to Claude)

Environment Variables (set by Claude Code):
    CLAUDE_TOOL_NAME   - Name of the tool being called
    CLAUDE_TOOL_INPUT  - JSON input to the tool

Usage in .claude/settings.json:
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/bash_interceptor.py"
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
from datetime import datetime
from pathlib import Path

# =============================================================================
# Windows UTF-8 Encoding Fix
# =============================================================================

if sys.platform == 'win32':
    # Force UTF-8 encoding on Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback silently if reconfiguration fails

# =============================================================================
# Configuration
# =============================================================================

# Environment variable to bypass hooks (set by orchestrator)
BYPASS_ENV_VAR = "CLAUDE_ORCHESTRATOR_APPROVED"

# Whitelisted paths that can be modified directly
WHITELISTED_PATHS = [
    "~/.claude/hooks/",
    ".claude/hooks/",
    "docs/",
    ".bmad/",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "LICENSE.md",
]

# Commands that are allowed to run directly (orchestrator's own commands)
ALLOWED_COMMAND_PATTERNS = [
    "python master_orchestrator.py",
    "python -m master_orchestrator",
    "python3 -m master-orchestrator",
    "python3 -m master_orchestrator",
    # Allow the orchestrator's internal operations
    "python -m ",  # orchestrator may call other python modules
    "python3 -m ",
]

# Log directory
LOG_DIR = Path.home() / ".claude-hooks" / "pre-tool"

# =============================================================================
# Encoding Utilities
# =============================================================================

def clean_encoding(text: str) -> str:
    """
    Clean up encoding issues in text.
    
    Handles:
    - HTML entities (&amp; -> &, &lt; -> <, etc.)
    - Unicode escape sequences
    - Windows path issues
    """
    if not text:
        return text
    
    # Decode HTML entities (handles &amp;&amp; -> &&)
    text = html.unescape(text)
    
    # Handle common double-encoded cases
    if '&amp;' in text:
        text = html.unescape(text)
    
    return text


def normalize_command(command: str) -> str:
    """
    Normalize command string for consistent matching.
    
    - Clean encoding issues
    - Normalize path separators on Windows
    - Strip whitespace
    """
    command = clean_encoding(command)
    command = command.strip()
    
    # Normalize Windows paths in cd commands
    if sys.platform == 'win32':
        # Convert forward slashes in paths if needed
        pass  # Keep original for now, Windows handles both
    
    return command

# =============================================================================
# Logging
# =============================================================================

def log_event(event_type: str, tool: str, data: dict):
    """Log hook events for auditing."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "tool": tool,
            **data
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Logging should never break the hook

# =============================================================================
# Checkers
# =============================================================================

def is_bypass_enabled() -> bool:
    """Check if orchestrator bypass is enabled."""
    return os.environ.get(BYPASS_ENV_VAR, "").strip() in ("1", "true", "yes")


def is_whitelisted_path(file_path: str) -> bool:
    """Check if file path is whitelisted for direct modification."""
    if not file_path:
        return False
    
    # Expand ~ in whitelisted paths
    expanded_whitelist = [
        os.path.expanduser(p) if p.startswith("~") else p 
        for p in WHITELISTED_PATHS
    ]
    
    # Check if file path matches any whitelist pattern
    for pattern in expanded_whitelist:
        if pattern.endswith("/"):
            # Directory pattern
            if file_path.startswith(pattern) or f"/{pattern}" in file_path:
                return True
        else:
            # File pattern
            if file_path.endswith(pattern) or file_path == pattern:
                return True
            # Also check basename
            if os.path.basename(file_path) == pattern:
                return True
    
    return False


def is_allowed_command(command: str) -> bool:
    """Check if command is allowed to run directly."""
    if not command:
        return False
    
    command = command.strip()
    
    for pattern in ALLOWED_COMMAND_PATTERNS:
        if command.startswith(pattern):
            return True
    
    return False


def extract_command(tool_input: str) -> str:
    """Extract command from tool input."""
    try:
        # Clean encoding before parsing
        tool_input = clean_encoding(tool_input)
        data = json.loads(tool_input)
        command = data.get("command", "")
        # Normalize the command
        return normalize_command(command)
    except (json.JSONDecodeError, TypeError):
        return normalize_command(tool_input) if isinstance(tool_input, str) else ""


def extract_file_path(tool_input: str) -> str:
    """Extract file path from tool input."""
    try:
        # Clean encoding before parsing
        tool_input = clean_encoding(tool_input)
        data = json.loads(tool_input)
        # Try common field names
        for field in ["file_path", "path", "filePath", "filename"]:
            if field in data:
                return clean_encoding(data[field])
        return ""
    except (json.JSONDecodeError, TypeError):
        return ""

# =============================================================================
# Main Hook Logic
# =============================================================================

def handle_bash(tool_input: str) -> tuple[bool, str]:
    """
    Handle Bash tool interception.
    
    Returns:
        (allowed: bool, reason: str)
    """
    command = extract_command(tool_input)
    
    if not command:
        return False, "Empty command not allowed"
    
    # Check bypass
    if is_bypass_enabled():
        log_event("bypass", "Bash", {"command": command[:200]})
        return True, "Bypass enabled"
    
    # Check if it's an orchestrator command
    if is_allowed_command(command):
        log_event("allowed", "Bash", {"command": command[:200], "reason": "orchestrator_command"})
        return True, "Orchestrator command"
    
    # Block all other commands
    log_event("blocked", "Bash", {"command": command[:200]})
    
    # Provide helpful suggestion
    suggestion = f'python master_orchestrator.py "{command}" -v'
    if len(suggestion) > 200:
        suggestion = f'python master_orchestrator.py "<your command>" -v'
    
    return False, f"""
❌ BLOCKED: Direct Bash execution is not allowed.

Command attempted: {command[:100]}{'...' if len(command) > 100 else ''}

✅ Use the master orchestrator instead:
   {suggestion}

All commands must go through the orchestrator for:
- Centralized logging and audit trail
- Intelligent intent analysis
- Error handling and retry logic
"""


def handle_file_operation(tool_name: str, tool_input: str) -> tuple[bool, str]:
    """
    Handle Write/Edit/MultiEdit tool interception.
    
    Returns:
        (allowed: bool, reason: str)
    """
    file_path = extract_file_path(tool_input)
    
    # Check bypass
    if is_bypass_enabled():
        log_event("bypass", tool_name, {"path": file_path})
        return True, "Bypass enabled"
    
    # Check whitelist
    if is_whitelisted_path(file_path):
        log_event("allowed", tool_name, {"path": file_path, "reason": "whitelisted"})
        return True, f"Whitelisted path: {file_path}"
    
    # Block file operation
    log_event("blocked", tool_name, {"path": file_path})
    
    action_verb = {
        "Write": "create",
        "Edit": "modify",
        "MultiEdit": "edit multiple files in",
        "NotebookEdit": "edit notebook"
    }.get(tool_name, "modify")
    
    return False, f"""
❌ BLOCKED: Direct {tool_name} operation is not allowed.

File: {file_path or 'unknown'}

✅ Use the master orchestrator instead:
   python master_orchestrator.py "{action_verb} {file_path or '<file>'}" -v

All file operations must go through the orchestrator for:
- Centralized logging and audit trail
- Consistent code modification patterns
- Rollback capability
"""


def main():
    """Main hook entry point."""
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", "")
    tool_input = os.environ.get("CLAUDE_TOOL_INPUT", "")
    
    # Route to appropriate handler
    if tool_name == "Bash":
        allowed, reason = handle_bash(tool_input)
    elif tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        allowed, reason = handle_file_operation(tool_name, tool_input)
    else:
        # Unknown tool - allow by default
        allowed, reason = True, "Unknown tool, allowing"
    
    # Output reason (Claude will see this)
    print(reason)
    
    # Exit code determines allow/block
    sys.exit(0 if allowed else 1)


if __name__ == "__main__":
    main()
