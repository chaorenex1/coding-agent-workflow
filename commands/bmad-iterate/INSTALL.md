# BMAD Iteration Workflow - Installation Guide

## Overview

The BMAD Iteration Workflow is a complete system for managing product requirement iterations using the **Breakthrough Method for Agile AI-Driven Development**. This workflow is designed for iterating on existing products, complementing the `/bmad` workflow for new products.

## Prerequisites

- Claude Code CLI installed
- Git repository with existing BMAD baseline documents
- Node.js project with package.json (for development commands)
- Existing PRD at `docs/bmad/02-planning/prd.md`

## Installation

### Step 1: Install Slash Commands

Copy all `.md` files from `generated-commands/bmad-iterate/` to your Claude commands directory:

**Project-level installation:**
```bash
# Create commands directory if not exists
mkdir -p .claude/commands/bmad-iterate

# Copy iteration commands
cp generated-commands/bmad-iterate/bmad-iter*.md .claude/commands/bmad-iterate/
```

**User-level installation:**
```bash
# Create user commands directory if not exists
mkdir -p ~/.claude/commands/bmad-iterate

# Copy iteration commands
cp generated-commands/bmad-iterate/bmad-iter*.md ~/.claude/commands/bmad-iterate/
```

### Step 2: Install Agents

Copy all iteration agents to your Claude agents directory:

**Project-level installation:**
```bash
# Create agents directory if not exists
mkdir -p .claude/agents

# Copy iteration agents
cp .claude/agents/bmad-iter-orchestrator.md .claude/agents/
cp .claude/agents/bmad-diff-analyst.md .claude/agents/
cp .claude/agents/bmad-iteration-planner.md .claude/agents/
cp .claude/agents/bmad-impact-analyst.md .claude/agents/
cp .claude/agents/bmad-iter-developer.md .claude/agents/
cp .claude/agents/bmad-regression-tester.md .claude/agents/
cp .claude/agents/bmad-release-manager.md .claude/agents/
```

**User-level installation:**
```bash
# Create user agents directory if not exists
mkdir -p ~/.claude/agents

# Copy iteration agents
cp .claude/agents/bmad-*.md ~/.claude/agents/
```

### Step 3: Initialize Iteration Directory Structure

The workflow will automatically create directories, but you can initialize manually:

```bash
# Create iteration config directory
mkdir -p .bmad-iter

# Create iteration docs structure
mkdir -p docs/bmad-iter
```

### Step 4: Verify Baseline Documents

Ensure you have baseline BMAD documents from a previous `/bmad` workflow:

```
docs/bmad/
├── 02-planning/
│   ├── prd.md              # Required baseline PRD
│   └── user-stories.md     # Required user stories
└── 03-architecture/
    └── architecture.md     # Required baseline architecture
```

## Installed Components

### Slash Commands

| Command | Description | Phase |
|---------|-------------|-------|
| `/bmad-iter` | Main orchestrator | All |
| `/bmad-iter-diff` | PRD diff analysis | 1 |
| `/bmad-iter-plan` | Iteration planning | 2 |
| `/bmad-iter-impact` | Impact analysis | 3 |
| `/bmad-iter-dev` | Incremental development | 4 |
| `/bmad-iter-test` | Regression testing | 5 |
| `/bmad-iter-release` | Release management | 6 |

### Agents

| Agent | Role | Color |
|-------|------|-------|
| bmad-iter-orchestrator | Central coordinator | Purple |
| bmad-diff-analyst | PRD change analysis | Cyan |
| bmad-iteration-planner | Sprint/story planning | Blue |
| bmad-impact-analyst | Code/architecture impact | Yellow |
| bmad-iter-developer | TDD implementation | Green |
| bmad-regression-tester | Quality assurance | Red |
| bmad-release-manager | Deployment & release | Orange |

## Directory Structure After Installation

```
project-root/
├── .claude/
│   ├── commands/
│   │   └── bmad-iterate/
│   │       ├── bmad-iter.md
│   │       ├── bmad-iter-diff.md
│   │       ├── bmad-iter-plan.md
│   │       ├── bmad-iter-impact.md
│   │       ├── bmad-iter-dev.md
│   │       ├── bmad-iter-test.md
│   │       └── bmad-iter-release.md
│   └── agents/
│       ├── bmad-iter-orchestrator.md
│       ├── bmad-diff-analyst.md
│       ├── bmad-iteration-planner.md
│       ├── bmad-impact-analyst.md
│       ├── bmad-iter-developer.md
│       ├── bmad-regression-tester.md
│       └── bmad-release-manager.md
├── .bmad-iter/                 # Created on first use
│   ├── config.yaml
│   ├── state.yaml
│   └── history/
├── docs/
│   ├── bmad/                   # Existing baseline
│   └── bmad-iter/              # Created on first use
│       └── [iter-id]/
└── ...
```

## Verification

After installation, verify commands are available:

```bash
# Test main orchestrator
/bmad-iter status

# Should show "No active iteration" if first time
```

## Configuration (Optional)

Create `.bmad-iter/config.yaml` to customize defaults:

```yaml
version: "1.0"

iteration:
  default_type: sprint        # sprint | quick | continuous
  naming_pattern: "iter-{year}-{month}"

phases:
  skip_impact_for_small: true # Skip Phase 3 for small changes
  auto_release: false         # Auto-release on test pass

paths:
  baseline_prd: "docs/bmad/02-planning/prd.md"
  baseline_arch: "docs/bmad/03-architecture/architecture.md"
  iterations: "docs/bmad-iter"

preferences:
  auto_commit: true
  require_review: false
  feature_flags: true
```

## Troubleshooting

### Commands Not Found

If commands aren't recognized:
1. Ensure files are in correct directory
2. Restart Claude Code session
3. Check file permissions

### Missing Baseline

If you see "Baseline PRD not found":
1. Run `/bmad phase 2` to create baseline PRD
2. Or manually create `docs/bmad/02-planning/prd.md`

### Agent Not Delegating

If agents aren't being invoked:
1. Verify agent files are in `.claude/agents/`
2. Check YAML frontmatter is valid
3. Ensure `allowed-tools` includes required tools

## Next Steps

After installation, see [QUICKSTART.md](QUICKSTART.md) for your first iteration.

---

**Version**: 1.0.0
**Compatible with**: Claude Code CLI
**Related**: `/bmad` workflow for new products
