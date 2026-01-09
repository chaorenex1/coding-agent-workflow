# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Coding Workflow** is a Claude Code plugin system providing AI-driven development workflows through 21 Skills, 36 Agents, and 47 Commands. It integrates multiple AI backends (Claude, Gemini, Codex) to automate development from requirements analysis to deployment.

**Repository**: https://github.com/chaorenex1/coding-workflow

---

## Plugin Architecture

This is a **Claude Code Plugin** distributed via Plugin Marketplace. Key structure:

- `.claude-plugin/plugin.json` - Plugin manifest defining all components
- `skills/` - 21 auto-discovered skill modules (each with `SKILL.md`)
- `agents/` - 36 specialized AI agents (organized in 5 subdirectories)
- `commands/` - 47 slash commands (organized in 6 subdirectories)
- `hooks/hooks.json` - SessionStart hook for dependency validation

### Component Auto-Discovery

Claude Code automatically discovers:
- Skills: All directories in `skills/` with `SKILL.md`
- Agents: All `.md` files in configured agent subdirectories
- Commands: All `.md` files in configured command subdirectories

When adding new components, no manifest update needed if following standard structure.

---

## Dependencies

### Required
- **memex-cli** (npm package): Backend orchestration tool
  ```bash
  npm install -g memex-cli
  ```
- **Python dependencies**: chardet, pyyaml
  ```bash
  pip install chardet pyyaml
  ```

### Validation
Dependencies are auto-checked on SessionStart via `hooks/hooks.json`. Check cache at `~/.claude/coding-workflow-deps-check.txt` (24h TTL).

---

## Development Workflows

### BMAD (Breakthrough Method for Agile AI-Driven Development)

**Full Workflow** (`/bmad`) - Complete project lifecycle:
1. **Analysis** (`bmad-analyst`) - Market research, competitive analysis
2. **Planning** (`bmad-product-owner`) - PRD creation, user stories
3. **Architecture** (`bmad-architect`) - System design, API contracts
4. **Development** (`bmad-scrum-master` → `bmad-fullstack-dev`) - TDD implementation
5. **Testing** (`bmad-qa`) - Test execution, quality assurance
6. **Deployment** (`bmad-devops`) - CI/CD, release management

**Iteration Workflow** (`/bmad-iter`) - Change management for existing projects:
1. **Diff Analysis** (`bmad-diff-analyst`) - Compare PRD versions
2. **Planning** (`bmad-iteration-planner`) - Scope iteration
3. **Impact Analysis** (`bmad-impact-analyst`) - Assess codebase changes
4. **Development** (`bmad-iter-developer`) - Incremental implementation
5. **Testing** (`bmad-regression-tester`) - Regression test suite
6. **Release** (`bmad-release-manager`) - Changelog, deployment

### State Management
BMAD workflows create `.bmad/` directory structure:
```
.bmad/
├── config.yaml      # Project configuration
├── state.yaml       # Current phase/status
├── history/         # State transitions
└── epics/           # Epic/story tracking
```

### Quick Code Workflows

For small features/refactoring:
- `/quick-feature` - Rapid feature implementation
- `/quick-refactor` - Code refactoring analysis + execution
- `/quick-rename` - Symbol renaming with impact analysis

---

## Common Commands

### Plugin Development

```bash
# Validate plugin structure
python -m json.tool .claude-plugin/plugin.json

# Test plugin locally (from plugin directory)
claude code --plugin-dir .

# Check dependencies
memex-cli --version
python -c "import chardet, yaml"
```

### Creating New Components

**New Skill**:
```bash
mkdir skills/my-skill
cat > skills/my-skill/SKILL.md <<EOF
---
name: my-skill
description: Brief description when to use this skill
---
# Skill implementation instructions
EOF
```

**New Agent**:
```bash
cat > agents/automation/my-agent.md <<EOF
---
name: my-agent
description: Agent role and when to invoke
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---
# Agent system prompt
EOF
```

**New Command**:
```bash
cat > commands/workflow-suite/my-command.md <<EOF
---
name: my-command
description: Command purpose
---
# Command implementation
EOF
```

### Git Workflows

```bash
# Standard commit with co-authorship
git commit -m "$(cat <<'EOF'
feat: description

Details

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Create release tag
git tag -a v3.0.1 -m "Release: Description"
git push origin main --tags
```

---

## Architecture Patterns

### Multi-Backend Orchestration

Commands like `/multcode` orchestrate specialized skills for optimal AI backend usage:
- **Claude**: Complex reasoning, architecture design (via `memex-cli`)
- **Gemini**: UX design, multimodal tasks (via `ux-design-gemini` skill)
- **Codex**: Code generation, refactoring (via `code-with-codex` skill)

Backend selection managed by orchestrator commands using `memex-cli` with `--backend` flag.

### Agent Coordination

Orchestrator agents (e.g., `bmad-orchestrator`, `fa-orchestrator-quick-feature`) manage:
- Phase transitions and validation
- Specialized agent invocation via Task tool
- State persistence in `.bmad/` or `.quick-code/`
- Progress tracking and reporting

### Skill Invocation

Skills are triggered two ways:
1. **Explicit**: `/skill skill-name "task description"`
2. **Auto-invoked**: Claude Code matches task context to skill description

---

## Key Files and Locations

### Plugin Configuration
- `.claude-plugin/plugin.json` - Plugin manifest (DO NOT modify component paths unless changing structure)
- `hooks/hooks.json` - Event hooks (SessionStart dependency check)
- `docs/coding-workflow.local.example.md` - User config template

### Documentation
- `README.md` - Public-facing documentation
- `docs/PLUGIN_TESTING_GUIDE.md` - Plugin testing procedures
- Individual `SKILL.md` files - Skill-specific documentation

### Ignore Patterns
`.gitignore` excludes:
- `.claude/*.local.md` - User configurations
- `.claude/coding-workflow-deps-check.txt` - Dependency check cache
- `orchestrator_output/` - Execution artifacts

---

## Workflow Selection Guide

| Scenario | Command | Use When |
|----------|---------|----------|
| Multi-backend workflow | `/multcode` | End-to-end development with Claude/Gemini/Codex orchestration |
| New project from scratch | `/bmad` | Building complete application with git integration |
| Existing project changes | `/bmad-iter` | PRD updates, feature additions |
| Small feature (<200 LOC) | `/quick-feature` | Single-file or simple multi-file changes |
| Code analysis | `/project-architecture`, `/code-review` | Understanding codebase structure |
| Refactoring | `/quick-refactor` | Improving code quality |
| Symbol rename | `/quick-rename` | Renaming across codebase |

---

## Best Practices

### Before Making Changes
1. Use `/project-architecture` to understand codebase structure
2. Use `/code-impact-analysis` for change assessment
3. Read relevant agent/skill documentation

### Adding Components
1. Follow naming conventions (kebab-case)
2. Place in correct subdirectory per component type
3. Include YAML frontmatter with required fields
4. Test auto-discovery with `claude code --plugin-dir .`

### Plugin Testing
Follow `docs/PLUGIN_TESTING_GUIDE.md`:
1. Validate JSON manifests
2. Test local plugin loading
3. Verify component discovery (47 commands, 21 skills, 36 agents)
4. Check dependency validation hook

### Documentation Sync
When modifying code affecting architecture or user workflows:
1. Update relevant `.md` files in `docs/`
2. Consider invoking `documentation-sync-agent` for automated sync
3. Maintain consistency across README, ARCHITECTURE, and component docs

---

## Troubleshooting

### Plugin Not Loading
```bash
# Verify manifest syntax
python -m json.tool .claude-plugin/plugin.json

# Check directory structure
ls -la skills/*/SKILL.md | wc -l  # Should be 21
find agents -name "*.md" | wc -l  # Should be 36
find commands -name "*.md" | wc -l # Should be 47
```

### Dependency Issues
```bash
# Force re-check (delete cache)
rm ~/.claude/coding-workflow-deps-check.txt

# Manual verification
which memex-cli || where memex-cli
python -c "import chardet, yaml; print('OK')"
```

### Component Not Discovered
- Verify file naming: `SKILL.md` for skills (case-sensitive)
- Check YAML frontmatter syntax
- Ensure file in correct subdirectory per `plugin.json` paths
- Restart Claude Code session

---

## Version Management

Current version: **3.0.0**

Semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes to plugin structure or API
- MINOR: New skills/agents/commands (backward compatible)
- PATCH: Bug fixes, documentation updates

Update version in:
1. `.claude-plugin/plugin.json`
2. `README.md` badges
3. Create git tag: `git tag -a v3.0.x -m "Release notes"`
