# BMAD Workflow Installation Guide

## Quick Install (Recommended)

### Option 1: Full Installation (Commands + Agents)

```bash
# Navigate to the factory directory
cd path/to/claude-code-skill-factory

# Create directories if they don't exist
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/agents

# Copy all slash commands
cp generated-commands/bmad-workflow/bmad-*.md ~/.claude/commands/

# Copy all agents
cp .claude/agents/bmad-*.md ~/.claude/agents/

# Verify installation
ls ~/.claude/commands/bmad-*.md
ls ~/.claude/agents/bmad-*.md
```

### Option 2: Project-Level Installation

```bash
# Navigate to your project
cd your-project

# Create directories
mkdir -p .claude/commands
mkdir -p .claude/agents

# Copy from factory (adjust path as needed)
cp path/to/factory/generated-commands/bmad-workflow/bmad-*.md .claude/commands/
cp path/to/factory/.claude/agents/bmad-*.md .claude/agents/
```

---

## What Gets Installed

### Slash Commands (6)

| Command | File | Purpose |
|---------|------|---------|
| `/bmad-analyze` | bmad-analyze.md | Phase 1: Market research & project brief |
| `/bmad-plan` | bmad-plan.md | Phase 2: PRD & user stories |
| `/bmad-architect` | bmad-architect.md | Phase 3: Technical architecture |
| `/bmad-develop` | bmad-develop.md | Phase 4: Story-driven development |
| `/bmad-test` | bmad-test.md | Phase 5: Testing & QA |
| `/bmad-deploy` | bmad-deploy.md | Phase 6: Deployment & release |

### Agents (7)

| Agent | File | Role |
|-------|------|------|
| `bmad-analyst` | bmad-analyst.md | Market research specialist |
| `bmad-product-owner` | bmad-product-owner.md | Product requirements specialist |
| `bmad-architect` | bmad-architect.md | System design specialist |
| `bmad-scrum-master` | bmad-scrum-master.md | Epic sharding & coordination |
| `bmad-fullstack-dev` | bmad-fullstack-dev.md | Full-stack implementation |
| `bmad-qa` | bmad-qa.md | Testing & quality assurance |
| `bmad-devops` | bmad-devops.md | Deployment & release |

---

## Verification

After installation, verify everything works:

```bash
# In Claude Code, list available commands
/help

# You should see bmad commands listed

# Test a command
/bmad-analyze "Test product idea"
```

---

## File Structure After Installation

### User-Level (~/.claude/)

```
~/.claude/
├── commands/
│   ├── bmad-analyze.md
│   ├── bmad-plan.md
│   ├── bmad-architect.md
│   ├── bmad-develop.md
│   ├── bmad-test.md
│   └── bmad-deploy.md
└── agents/
    ├── bmad-analyst.md
    ├── bmad-product-owner.md
    ├── bmad-architect.md
    ├── bmad-scrum-master.md
    ├── bmad-fullstack-dev.md
    ├── bmad-qa.md
    └── bmad-devops.md
```

### Project-Level (.claude/)

```
your-project/
├── .claude/
│   ├── commands/
│   │   └── [bmad commands]
│   └── agents/
│       └── [bmad agents]
├── docs/
│   └── bmad/           # Created by workflow
├── src/                # Your code
└── tests/              # Your tests
```

---

## Uninstallation

```bash
# Remove commands
rm ~/.claude/commands/bmad-*.md

# Remove agents
rm ~/.claude/agents/bmad-*.md
```

---

## Troubleshooting

### Commands not showing up

1. Ensure files are in correct location:
   - User-level: `~/.claude/commands/`
   - Project-level: `.claude/commands/`

2. Restart Claude Code session

3. Check file permissions:
   ```bash
   ls -la ~/.claude/commands/
   ```

### Agents not being invoked

1. Check agent files exist:
   ```bash
   ls ~/.claude/agents/bmad-*.md
   ```

2. Verify YAML frontmatter is valid:
   - `name:` must be kebab-case
   - `tools:` must be comma-separated string

3. Check agent descriptions match your use case

### Permission errors

```bash
# Fix permissions
chmod 644 ~/.claude/commands/*.md
chmod 644 ~/.claude/agents/*.md
```

---

## Updates

To update to newer versions:

```bash
# Pull latest factory
cd path/to/claude-code-skill-factory
git pull

# Re-copy files (will overwrite)
cp generated-commands/bmad-workflow/bmad-*.md ~/.claude/commands/
cp .claude/agents/bmad-*.md ~/.claude/agents/
```

---

## Next Steps

After installation:

1. **Read the Overview**: `generated-commands/bmad-workflow/WORKFLOW_OVERVIEW.md`
2. **Start Building**: `/bmad-analyze "Your product idea"`
3. **Follow the Workflow**: Phase 1 → 2 → 3 → 4 → 5 → 6

Happy building! 🚀
