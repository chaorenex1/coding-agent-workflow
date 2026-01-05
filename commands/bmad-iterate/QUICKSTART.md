# BMAD Iteration Workflow - Quick Start Guide

## Your First Iteration in 5 Minutes

This guide walks you through starting and completing your first BMAD iteration.

## Prerequisites

Before starting, ensure:
- [x] BMAD Iteration workflow installed (see [INSTALL.md](INSTALL.md))
- [x] Existing baseline PRD at `docs/bmad/02-planning/prd.md`
- [x] Git repository initialized

## Quick Start

### Step 1: Start a New Iteration

```bash
/bmad-iter start "v2.1 Feature Update"
```

You'll be prompted to select iteration type:
- **Sprint** (1-2 weeks) - Multiple features
- **Quick** (1-3 days) - Small changes
- **Continuous** - Single feature with immediate release

### Step 2: Analyze PRD Changes

```bash
/bmad-iter diff
```

Or provide new requirements directly:
```bash
/bmad-iter diff path/to/new-requirements.md
```

This phase:
- Compares baseline PRD with new requirements
- Identifies all changes (ADD/MODIFY/ENHANCE/FIX)
- Generates change inventory

### Step 3: Plan the Iteration

```bash
/bmad-iter plan
```

Or specify iteration type:
```bash
/bmad-iter plan sprint
```

This phase:
- Transforms changes into user stories
- Prioritizes scope (P1/P2/P3)
- Creates timeline and milestones

### Step 4: Analyze Impact

```bash
/bmad-iter impact
```

This phase:
- Identifies affected code
- Maps dependencies
- Assesses risks

### Step 5: Develop Stories

Work on stories one at a time:
```bash
# Auto-select next story
/bmad-iter next

# Or work on specific story
/bmad-iter story iter-001/story-001
```

Development follows TDD:
1. Write failing test
2. Implement minimum code
3. Refactor
4. Commit

### Step 6: Run Regression Tests

```bash
/bmad-iter-test
```

Or specify scope:
```bash
/bmad-iter-test full     # Complete suite
/bmad-iter-test affected # Changed areas only
/bmad-iter-test quick    # Smoke tests
```

### Step 7: Release

```bash
/bmad-iter release
```

Or specify version type:
```bash
/bmad-iter release minor
```

### Step 8: Close Iteration

```bash
/bmad-iter close
```

## Common Workflows

### Workflow A: Full Sprint

```bash
# Week 1 - Planning
/bmad-iter start "Sprint 12"
/bmad-iter diff
/bmad-iter plan sprint
/bmad-iter impact

# Week 1-2 - Development
/bmad-iter next  # Repeat for each story

# Week 2 - Finalize
/bmad-iter-test full
/bmad-iter release minor
/bmad-iter close
```

### Workflow B: Quick Fix

```bash
# Day 1
/bmad-iter start "Hotfix 2.0.1"
/bmad-iter diff
/bmad-iter plan quick

# Skip impact for small changes
/bmad-iter story iter-xxx/story-001

# Same day
/bmad-iter-test affected
/bmad-iter release patch
/bmad-iter close
```

### Workflow C: Continuous Delivery

```bash
# Single feature
/bmad-iter start "Add Dark Mode"
/bmad-iter diff
/bmad-iter plan continuous
/bmad-iter impact
/bmad-iter story iter-xxx/story-001
/bmad-iter-test
/bmad-iter release minor
/bmad-iter close
```

## Key Commands Reference

### Main Orchestrator

| Command | Description |
|---------|-------------|
| `/bmad-iter start [name]` | Start new iteration |
| `/bmad-iter status` | Check current status |
| `/bmad-iter next` | Execute next step |
| `/bmad-iter story [id]` | Work on specific story |
| `/bmad-iter release` | Prepare release |
| `/bmad-iter close` | Close iteration |

### Phase Commands

| Command | Phase | Purpose |
|---------|-------|---------|
| `/bmad-iter-diff` | 1 | Analyze PRD changes |
| `/bmad-iter-plan` | 2 | Create iteration plan |
| `/bmad-iter-impact` | 3 | Assess code impact |
| `/bmad-iter-dev` | 4 | Implement stories |
| `/bmad-iter-test` | 5 | Regression testing |
| `/bmad-iter-release` | 6 | Deploy release |

## Status Dashboard

Check iteration status anytime:

```bash
/bmad-iter status
```

Output example:
```
╔══════════════════════════════════════════════════════════════╗
║                 ITERATION STATUS                             ║
╠══════════════════════════════════════════════════════════════╣
║ Iteration: iter-2025-01 (v2.1 Feature Update)                ║
║ Type: sprint | Target: 2025-01-19                            ║
╠══════════════════════════════════════════════════════════════╣
║ PHASE STATUS                                                 ║
║ [✓] Phase 1: Diff Analysis    - Completed                   ║
║ [✓] Phase 2: Iteration Plan   - Completed                   ║
║ [✓] Phase 3: Impact Analysis  - Completed                   ║
║ [▶] Phase 4: Development      - In Progress                 ║
║ [ ] Phase 5: Regression Test  - Pending                     ║
║ [ ] Phase 6: Release          - Pending                     ║
╠══════════════════════════════════════════════════════════════╣
║ Progress: 2/5 stories (40%)                                  ║
╚══════════════════════════════════════════════════════════════╝
```

## Generated Artifacts

Each iteration creates:

```
docs/bmad-iter/[iter-id]/
├── 01-diff/
│   ├── diff-report.md          # Change analysis
│   └── change-list.md          # Change inventory
├── 02-plan/
│   ├── iteration-plan.md       # Sprint plan
│   └── iter-stories.md         # User stories
├── 03-impact/
│   ├── impact-report.md        # Code impact
│   └── design-delta.md         # Architecture changes
├── 04-dev/
│   ├── _progress.md            # Development progress
│   └── stories/
│       └── story-xxx.md        # Story implementation logs
├── 05-test/
│   └── regression-report.md    # Test results
└── 06-release/
    ├── release-notes.md        # Release notes
    └── deployment-log.md       # Deployment record
```

## Tips for Success

### 1. Keep Iterations Small
- Sprint: 5-10 stories max
- Quick: 1-3 stories
- Continuous: 1 story

### 2. Follow TDD
- Always write test first
- Commit after each passing test
- Never skip the refactor step

### 3. Maintain Backwards Compatibility
- Use optional parameters
- Version APIs
- Use feature flags

### 4. Document as You Go
- Update story files in real-time
- Log decisions and reasoning
- Note technical debt

### 5. Don't Skip Phases
- Even "quick" iterations need planning
- Impact analysis prevents surprises
- Testing catches regressions

## Troubleshooting

### "No active iteration"
Run `/bmad-iter start [name]` first.

### "Missing prerequisites"
Complete previous phase before proceeding.

### "Story has dependencies"
Complete dependent stories first, or use `/bmad-iter story [specific-id]`.

### "Tests failing"
Fix failures before proceeding to release. Use `/bmad-iter story [id]` to fix.

## Next Steps

1. **Read the full workflow overview**: See [WORKFLOW_OVERVIEW.md](WORKFLOW_OVERVIEW.md)
2. **Understand agents**: Review agent files in `.claude/agents/`
3. **Customize configuration**: Edit `.bmad-iter/config.yaml`

---

**Quick Reference Card**

```
Start:   /bmad-iter start "Name"
Status:  /bmad-iter status
Next:    /bmad-iter next
Story:   /bmad-iter story [id]
Release: /bmad-iter release
Close:   /bmad-iter close
```

---

**Version**: 1.0.0
**Last Updated**: January 2025
