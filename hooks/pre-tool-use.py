#!/usr/bin/env python3
"""
Pre-Tool-Use Hook: Enforce Codex/Gemini Workflow Contract

Blocks direct Edit/Write/NotebookEdit for:
- Code files → Must use /code-with-codex
- UX/styling files → Must use /ux-design-gemini
"""

import sys
import json

# File extension patterns
CODE_EXTENSIONS = {
    ".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".hpp", ".rb", ".php", ".swift", ".kt",
    ".scala", ".sh", ".bash", ".ps1", ".dart", ".lua", ".r"
}

UX_EXTENSIONS = {
    ".css", ".scss", ".sass", ".less", ".html", ".htm", ".vue", ".svelte"
}

UX_CONTENT_PATTERNS = {
    "class=", "style=", "<div", "<button", "<span", "<section",
    "@media", "background:", "color:", "font:", "margin:", "padding:",
    "flexbox", "grid-template", "border-radius", "box-shadow"
}

def error_block(message: str, details: list[str], suggestion: str) -> None:
    """Print error and exit with code 1."""
    print(f"\u274c BLOCKED: {message}", file=sys.stderr)
    for detail in details:
        print(f"\ud83d\udccb {detail}", file=sys.stderr)
    print(f"\u2705 Required: {suggestion}", file=sys.stderr)
    print(f"\nSuggested command:", file=sys.stderr)
    print(f"  {details[0].split(': ')[1] if ': ' in details[0] else suggestion}", file=sys.stderr)

def is_code_file(file_path: str) -> bool:
    """Check if file is a code file by extension."""
    if not file_path:
        return False
    return any(file_path.endswith(ext) for ext in CODE_EXTENSIONS)

def is_ux_file(file_path: str) -> bool:
    """Check if file is a UX/styling file by extension."""
    if not file_path:
        return False
    return any(file_path.endswith(ext) for ext in UX_EXTENSIONS)

def has_ux_content(content: str) -> bool:
    """Check if content contains UX/styling patterns."""
    if not content:
        return False
    content_lower = content.lower()
    return any(pattern.lower() in content_lower for pattern in UX_CONTENT_PATTERNS)

def main():
    """Main entry point."""
    # Read JSON from stdin
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            # No input, allow operation
            print(input_data, end="")
            return 0

        data = json.loads(input_data)
        tool_name = data.get("tool_name", "")
        parameters = data.get("parameters", {})

        # Get file path
        file_path = (
            parameters.get("file_path") or
            parameters.get("notebook_path") or
            ""
        )

        # Get content
        content = (
            parameters.get("content") or
            parameters.get("new_string") or
            parameters.get("new_source") or
            ""
        )

    except (json.JSONDecodeError, KeyError):
        # Parse error, allow operation
        print(input_data, end="")
        return 0

    # Only check Edit/Write/NotebookEdit tools
    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        print(input_data, end="")
        return 0

    # Check for code files
    if is_code_file(file_path):
        print(f"\u274c BLOCKED: Direct edit to code file detected!", file=sys.stderr)
        print(f"\ud83d\udccb File: {file_path}", file=sys.stderr)
        print(f"\u26a0\ufe0f  Violation: Rule #2 Workflow Contract", file=sys.stderr)
        print(f"\u2705 Required: Use /code-with-codex skill instead", file=sys.stderr)
        print(f"\nSuggested command:", file=sys.stderr)
        print(f"  /code-with-codex [describe your code change]", file=sys.stderr)
        return 1

    # Check for UX files or content
    if is_ux_file(file_path) or has_ux_content(content):
        print(f"\u274c BLOCKED: Direct edit to UX/styling file detected!", file=sys.stderr)
        print(f"\ud83d\udccb File: {file_path}", file=sys.stderr)
        print(f"\u26a0\ufe0f  Violation: Rule #2 Workflow Contract", file=sys.stderr)
        print(f"\u2705 Required: Use /ux-design-gemini skill instead", file=sys.stderr)
        print(f"\nSuggested command:", file=sys.stderr)
        print(f"  /ux-design-gemini [describe your design change]", file=sys.stderr)
        return 1

    # Allow non-code/non-UX edits
    print(input_data, end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
