#!/bin/bash
# Pre-Tool-Use Hook: Enforce Codex/Gemini Workflow Contract
# This hook intercepts Edit/Write/NotebookEdit and blocks code/UX edits

set -euo pipefail

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name and parameters
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.parameters.file_path // .parameters.notebook_path // empty')
CONTENT=$(echo "$INPUT" | jq -r '.parameters.content // .parameters.new_string // .parameters.new_source // empty')

# Define code/UX file extensions
CODE_EXTENSIONS="\.(js|ts|jsx|tsx|py|java|go|rs|cpp|c|h|rb|php|swift|kt|scala|sh|bash)$"
UX_EXTENSIONS="\.(css|scss|sass|less|html|vue|svelte|md)$"

# Check if tool is Edit/Write/NotebookEdit
if [[ "$TOOL_NAME" =~ ^(Edit|Write|NotebookEdit)$ ]]; then
    # Check if file is code/UX related
    if [[ "$FILE_PATH" =~ $CODE_EXTENSIONS ]]; then
        # Code file detected - block and suggest code-with-codex
        echo "❌ BLOCKED: Direct edit to code file detected!" >&2
        echo "📋 File: $FILE_PATH" >&2
        echo "⚠️  Violation: Rule #2 Workflow Contract" >&2
        echo "✅ Required: Use /code-with-codex skill instead" >&2
        echo "" >&2
        echo "Suggested command:" >&2
        echo "  /code-with-codex [describe your code change]" >&2
        exit 1
    fi

    if [[ "$FILE_PATH" =~ $UX_EXTENSIONS ]] || [[ "$CONTENT" =~ (class=|style=|<div|<button|@media|\.css) ]]; then
        # UX file or styling detected - block and suggest ux-design-gemini
        echo "❌ BLOCKED: Direct edit to UX/styling file detected!" >&2
        echo "📋 File: $FILE_PATH" >&2
        echo "⚠️  Violation: Rule #2 Workflow Contract" >&2
        echo "✅ Required: Use /ux-design-gemini skill instead" >&2
        echo "" >&2
        echo "Suggested command:" >&2
        echo "  /ux-design-gemini [describe your design change]" >&2
        exit 1
    fi
fi

# Allow non-code/non-UX edits (config files, docs, etc.)
echo "$INPUT"
exit 0
