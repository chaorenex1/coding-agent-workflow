---
description: BMAD Iteration Phase 6 - Prepare release artifacts, update changelog, create git tag, and deploy iteration changes
argument-hint: [release-type]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-sonnet-4-20250514
---

# BMAD Iteration Phase 6: Release Management

You are initiating **Phase 6 of the BMAD Iteration workflow** - Release Management. Your role is to package all iteration changes into a deployable release with proper documentation.

## Context

**Release Type** (optional): $ARGUMENTS
- `patch` - Bug fixes, minor changes (x.x.X)
- `minor` - New features, backwards compatible (x.X.0)
- `major` - Breaking changes (X.0.0)

**Previous Phase Artifacts**:
@docs/bmad-iter/[iter-id]/05-test/regression-report.md
@docs/bmad-iter/[iter-id]/04-dev/_progress.md
@docs/bmad-iter/[iter-id]/02-plan/iter-stories.md

**Current Version**:
- Package version: !`cat package.json 2>/dev/null | grep '"version"' | head -1`
- Latest tag: !`git describe --tags --abbrev=0 2>/dev/null`
- Git status: !`git status --short`

## Your Mission

As the **Release Manager Agent**, prepare and execute the release process for this iteration.

### Step 1: Pre-Release Validation

Verify release readiness:

1. **Phase 5 Complete**
   - All tests passing
   - Quality gate approved
   - No critical issues open

2. **Documentation Ready**
   - All stories documented
   - API changes documented
   - Migration guide (if needed)

3. **Git Status Clean**
   - All changes committed
   - Branch up to date
   - No merge conflicts

### Step 2: Determine Version

Based on changes in this iteration:

```
┌─────────────────────────────────────────────────────────────┐
│                  VERSION DETERMINATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Breaking Changes?                                          │
│  (API changes, removed features, schema changes)            │
│       │                                                     │
│       ├── YES ──→ MAJOR (X.0.0)                            │
│       │                                                     │
│       └── NO ──→ New Features?                             │
│                  (New functionality, new endpoints)         │
│                       │                                     │
│                       ├── YES ──→ MINOR (x.X.0)            │
│                       │                                     │
│                       └── NO ──→ PATCH (x.x.X)             │
│                                  (Bug fixes, improvements)  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Generate Release Notes

#### Artifact 1: `docs/bmad-iter/[iter-id]/06-release/release-notes.md`

```markdown
# Release Notes - v[X.Y.Z]

## Release Info
- **Version**: [X.Y.Z]
- **Iteration**: [iter-id]
- **Date**: [Release Date]
- **Type**: Major | Minor | Patch

---

## Summary

[2-3 sentence summary of what this release delivers]

---

## Highlights

### [Feature/Change 1 Title]
[Brief description with user benefit]

### [Feature/Change 2 Title]
[Brief description with user benefit]

---

## What's New

### Features

| Feature | Description | Story |
|---------|-------------|-------|
| [Feature name] | [What it does] | STORY-XXX |

### Improvements

| Improvement | Description | Story |
|-------------|-------------|-------|
| [Improvement] | [What improved] | STORY-XXX |

### Bug Fixes

| Fix | Description | Story |
|-----|-------------|-------|
| [Fix] | [What was fixed] | STORY-XXX |

---

## Breaking Changes

### [Breaking Change 1]

**What Changed**: [Description]

**Migration**:
```typescript
// Before
oldFunction(params);

// After
newFunction(newParams);
```

**Affected Areas**:
- [Area 1]
- [Area 2]

---

## API Changes

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/[path] | [Description] |

### Modified Endpoints

| Method | Endpoint | Change |
|--------|----------|--------|
| PUT | /api/[path] | [What changed] |

### Deprecated Endpoints

| Method | Endpoint | Replacement | Removal |
|--------|----------|-------------|---------|
| GET | /api/old | /api/new | v[X+1].0.0 |

---

## Database Changes

### Migrations Required

```bash
# Run migrations
npm run migrate

# Or specific migration
npm run migrate:up [migration-name]
```

### Schema Changes

| Table | Change | Notes |
|-------|--------|-------|
| [table] | [change] | [notes] |

---

## Configuration Changes

### New Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| [VAR_NAME] | Yes/No | [default] | [description] |

### Changed Variables

| Variable | Old | New | Migration |
|----------|-----|-----|-----------|
| [VAR_NAME] | [old] | [new] | [how to migrate] |

---

## Upgrade Guide

### From v[X.Y.Z-1]

1. **Backup**
   ```bash
   # Backup database
   pg_dump -U user database > backup.sql
   ```

2. **Update Dependencies**
   ```bash
   npm install
   ```

3. **Run Migrations**
   ```bash
   npm run migrate
   ```

4. **Update Configuration**
   - Add new environment variables
   - Update changed variables

5. **Restart Services**
   ```bash
   npm run build
   npm start
   ```

### Rollback Procedure

```bash
# If issues occur, rollback
npm run migrate:down
git checkout v[previous-version]
npm install
npm run build
npm start
```

---

## Known Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| [Issue] | [Description] | [Workaround] |

---

## Contributors

- BMAD Iteration Workflow Agents
- [Any human contributors]

---

## Full Changelog

See [CHANGELOG.md](../../../CHANGELOG.md) for complete history.

---

Generated by BMAD Iteration Workflow - Phase 6: Release Management
```

### Step 4: Update CHANGELOG

Prepend to `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- [New feature 1] (#story-xxx)
- [New feature 2] (#story-xxx)

### Changed
- [Changed behavior] (#story-xxx)

### Deprecated
- [Deprecated feature] - will be removed in vX.0.0

### Removed
- [Removed feature]

### Fixed
- [Bug fix 1] (#story-xxx)
- [Bug fix 2] (#story-xxx)

### Security
- [Security fix] (CVE-XXXX)
```

### Step 5: Create Release

Execute release process:

```bash
# 1. Ensure clean state
git status

# 2. Update version
npm version [major|minor|patch] -m "chore(release): v%s

🎉 Release highlights:
- [Highlight 1]
- [Highlight 2]

Iteration: [iter-id]"

# 3. Push with tags
git push origin main --tags

# 4. Create GitHub release (if applicable)
gh release create v[X.Y.Z] \
  --title "v[X.Y.Z] - [Release Name]" \
  --notes-file docs/bmad-iter/[iter-id]/06-release/release-notes.md
```

### Step 6: Deploy

Based on environment:

```
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. STAGING                                          │   │
│  │    - Deploy to staging environment                  │   │
│  │    - Run smoke tests                                │   │
│  │    - Verify critical paths                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. CANARY (if applicable)                           │   │
│  │    - Deploy to 5% of production                     │   │
│  │    - Monitor error rates                            │   │
│  │    - Monitor performance                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. PRODUCTION                                       │   │
│  │    - Full production deployment                     │   │
│  │    - Enable feature flags                           │   │
│  │    - Monitor dashboards                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. VERIFICATION                                     │   │
│  │    - Run production smoke tests                     │   │
│  │    - Verify monitoring alerts                       │   │
│  │    - Update status page                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 7: Post-Release Tasks

After successful deployment:

1. **Update Baseline**
   - If PRD evolved, update baseline
   - Archive iteration artifacts

2. **Notify Stakeholders**
   - Send release announcement
   - Update documentation site

3. **Close Iteration**
   - Run `/bmad-iter close`
   - Archive state

## Output Requirements

### Artifact Locations

```
docs/bmad-iter/[iter-id]/06-release/
├── release-notes.md            # Release notes
├── deployment-log.md           # Deployment record
└── verification-report.md      # Post-deploy verification

CHANGELOG.md                    # Updated changelog
package.json                    # Updated version
```

### State Update

```yaml
# .bmad-iter/state.yaml
workflow:
  current_phase: 6
  phase_status:
    5: completed
    6: completed
  iteration_status: released

release:
  version: "X.Y.Z"
  tag: "vX.Y.Z"
  date: "YYYY-MM-DD"
  commit: "[sha]"

deployment:
  staging:
    status: deployed
    date: "YYYY-MM-DD"
  production:
    status: deployed
    date: "YYYY-MM-DD"
```

### Deployment Log

Create `docs/bmad-iter/[iter-id]/06-release/deployment-log.md`:

```markdown
# Deployment Log

## Deployment Info
- **Version**: v[X.Y.Z]
- **Iteration**: [iter-id]
- **Deployed By**: BMAD Release Manager Agent
- **Date**: [date]

---

## Pre-Deployment Checklist

- [x] Phase 5 testing complete
- [x] All quality gates passed
- [x] Release notes prepared
- [x] CHANGELOG updated
- [x] Version bumped
- [x] Git tag created
- [x] Backup created

---

## Deployment Steps

### Step 1: Staging Deployment
- **Time**: [timestamp]
- **Status**: Success
- **Duration**: [duration]
- **Notes**: [any notes]

### Step 2: Staging Verification
- **Time**: [timestamp]
- **Status**: Pass
- **Tests Run**: [count]
- **Results**: All passing

### Step 3: Production Deployment
- **Time**: [timestamp]
- **Status**: Success
- **Duration**: [duration]
- **Method**: [rolling/blue-green/canary]

### Step 4: Production Verification
- **Time**: [timestamp]
- **Status**: Pass
- **Checks**:
  - [x] Health endpoint responding
  - [x] API responses valid
  - [x] No error spikes in monitoring
  - [x] Performance within bounds

---

## Rollback Plan

If issues detected:

```bash
# Immediate rollback
kubectl rollout undo deployment/[app-name]

# Or restore previous version
git checkout v[previous-version]
npm install && npm run build
# Redeploy
```

---

## Post-Deployment Monitoring

### First Hour
- [ ] Error rate < 0.1%
- [ ] Latency p99 < [threshold]ms
- [ ] CPU/Memory within bounds
- [ ] No user complaints

### First 24 Hours
- [ ] Feature adoption metrics
- [ ] Error trends stable
- [ ] No performance degradation

---

## Issues Encountered

| Time | Issue | Resolution |
|------|-------|------------|
| [time] | [issue] | [resolution] |

---

## Sign-Off

| Role | Name | Status | Time |
|------|------|--------|------|
| Release Manager | BMAD Agent | Approved | [time] |
| Operations | [if applicable] | Approved | [time] |

---

Generated by BMAD Iteration Workflow - Phase 6: Release Management
```

## Success Criteria

- [ ] Version determined correctly
- [ ] Release notes generated
- [ ] CHANGELOG updated
- [ ] Version bumped in package.json
- [ ] Git tag created
- [ ] Deployed to staging
- [ ] Staging verified
- [ ] Deployed to production
- [ ] Production verified
- [ ] Stakeholders notified
- [ ] Iteration ready to close

## Next Steps

After successful release:

```bash
# Close the iteration
/bmad-iter close

# Start next iteration (if needed)
/bmad-iter start "v[next] Features"
```

## Rollback Commands

If issues after release:

```bash
# Quick rollback
npm run rollback

# Or manual
git checkout v[previous-version]
npm install
npm run build
npm start

# Revert git tag
git tag -d v[X.Y.Z]
git push origin :refs/tags/v[X.Y.Z]
```

---

**IMPORTANT**:
- Never deploy without passing tests
- Always have rollback plan ready
- Monitor closely after deployment
- Document any issues immediately
- Update status page during deployment
