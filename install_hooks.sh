#!/bin/bash
#
# Install Master Orchestrator Hooks to User Directory
#
# This script installs hooks to ~/.claude/hooks/ for global usage
# across all projects.
#
# Usage:
#   chmod +x install_hooks.sh
#   ./install_hooks.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Master Orchestrator Hooks Installer ===${NC}\n"

# Target directories
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

# Source directory (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_HOOKS_DIR="$SCRIPT_DIR/hooks"

# Step 1: Create directories
echo -e "${YELLOW}[1/4] Creating directories...${NC}"
mkdir -p "$HOOKS_DIR"
echo "  Created: $HOOKS_DIR"

# Step 2: Copy hook scripts
echo -e "${YELLOW}[2/4] Copying hook scripts...${NC}"

if [ -d "$SOURCE_HOOKS_DIR" ]; then
    cp "$SOURCE_HOOKS_DIR/bash_interceptor.py" "$HOOKS_DIR/"
    cp "$SOURCE_HOOKS_DIR/logger.py" "$HOOKS_DIR/"
    cp "$SOURCE_HOOKS_DIR/intent_analyzer.py" "$HOOKS_DIR/"
    echo "  Copied: bash_interceptor.py"
    echo "  Copied: logger.py"
    echo "  Copied: intent_analyzer.py"
else
    echo -e "${RED}Error: Source hooks directory not found: $SOURCE_HOOKS_DIR${NC}"
    exit 1
fi

# Step 3: Make executable
echo -e "${YELLOW}[3/4] Setting permissions...${NC}"
chmod +x "$HOOKS_DIR"/*.py
echo "  Made scripts executable"

# Step 4: Create/update settings.json
echo -e "${YELLOW}[4/4] Configuring settings.json...${NC}"

# Backup existing settings if present
if [ -f "$SETTINGS_FILE" ]; then
    BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo "  Backed up existing settings to: $BACKUP_FILE"
fi

# Write new settings
cat > "$SETTINGS_FILE" << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${HOME}/.claude/hooks/bash_interceptor.py\""
          }
        ]
      },
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${HOME}/.claude/hooks/bash_interceptor.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${HOME}/.claude/hooks/logger.py\""
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${HOME}/.claude/hooks/intent_analyzer.py\""
          }
        ]
      }
    ]
  }
}
EOF

echo "  Created: $SETTINGS_FILE"

# Done
echo -e "\n${GREEN}=== Installation Complete ===${NC}\n"
echo "Installed files:"
echo "  $HOOKS_DIR/bash_interceptor.py"
echo "  $HOOKS_DIR/logger.py"
echo "  $HOOKS_DIR/intent_analyzer.py"
echo "  $SETTINGS_FILE"
echo ""
echo "Log directories will be created at:"
echo "  ~/.claude-hooks/audit/     (execution logs)"
echo "  ~/.claude-hooks/pre-tool/  (blocked operations)"
echo "  ~/.claude-hooks/intent/    (intent analysis)"
echo ""
echo -e "${YELLOW}Note: Restart Claude Code for hooks to take effect.${NC}"
