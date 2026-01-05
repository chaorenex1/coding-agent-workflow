---
description: BMAD Iteration Phase 3 - Analyze impact of planned changes on existing codebase, architecture, and tests
argument-hint: [focus-area]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-opus-4-5-20251022
---

# BMAD Iteration Phase 3: Impact Analysis

You are initiating **Phase 3 of the BMAD Iteration workflow** - Impact Analysis. Your role is to analyze how planned changes will affect the existing codebase, architecture, and test suite.

## Context

**Focus Area** (optional): $ARGUMENTS

**Previous Phase Artifacts**:
@docs/bmad-iter/[iter-id]/02-plan/iteration-plan.md
@docs/bmad-iter/[iter-id]/02-plan/iter-stories.md

**Baseline Architecture**:
@docs/bmad/03-architecture/architecture.md
@docs/bmad/03-architecture/tech-spec.md

**Current Codebase**:
- Source files: !`find src -type f -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l`
- Test files: !`find tests -type f -name "*.test.ts" 2>/dev/null | wc -l`
- Package info: !`cat package.json 2>/dev/null | head -20`

## Your Mission

As the **Impact Analyst Agent**, assess the ripple effects of planned changes across the entire system.

### Step 1: Code Impact Analysis

For each story, identify affected code:

1. **Direct Changes**
   - Files to create
   - Files to modify
   - Files to delete

2. **Indirect Impact**
   - Files importing modified modules
   - Components using changed APIs
   - Tests covering modified code

3. **Dependency Chain**
   - Upstream dependencies (what this code depends on)
   - Downstream dependencies (what depends on this code)

### Step 2: Architecture Impact

Assess architectural implications:

1. **Component Changes**
   - New components needed
   - Modified component interfaces
   - Component relationships

2. **Data Flow Changes**
   - New data flows
   - Modified data transformations
   - State management changes

3. **API Changes**
   - New endpoints
   - Modified request/response schemas
   - Breaking changes

4. **Database Changes**
   - Schema modifications
   - Data migrations needed
   - Backwards compatibility

### Step 3: Test Impact

Determine testing requirements:

1. **Existing Tests Affected**
   - Tests that will break
   - Tests that need updates
   - Tests that become obsolete

2. **New Tests Required**
   - Unit tests
   - Integration tests
   - E2E tests

3. **Regression Risk Areas**
   - High-risk areas needing extra testing
   - Related features to verify

### Step 4: Generate Impact Report

#### Artifact 1: `docs/bmad-iter/[iter-id]/03-impact/impact-report.md`

```markdown
# Impact Analysis Report

## Report Info
- **Iteration**: [iter-id]
- **Date**: [Current Date]
- **Stories Analyzed**: [count]
- **Analyst**: BMAD Impact Analyst Agent

---

## Executive Summary

**Overall Impact Level**: Low | Medium | High | Critical

| Dimension | Impact | Risk |
|-----------|--------|------|
| Code Changes | [X] files | [Low/Med/High] |
| API Changes | [X] endpoints | [Low/Med/High] |
| Database Changes | [X] tables | [Low/Med/High] |
| Test Updates | [X] tests | [Low/Med/High] |

**Key Findings**:
1. [Major finding 1]
2. [Major finding 2]
3. [Major finding 3]

---

## Code Impact Analysis

### Files Changed Summary

| Category | Create | Modify | Delete | Total |
|----------|--------|--------|--------|-------|
| Components | [n] | [n] | [n] | [n] |
| Services | [n] | [n] | [n] | [n] |
| Utils | [n] | [n] | [n] | [n] |
| Tests | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### STORY-001: [Title]

#### Direct Changes
| File | Action | Description |
|------|--------|-------------|
| src/components/[name].tsx | CREATE | New component |
| src/lib/[name].ts | MODIFY | Add new function |
| src/app/api/[route]/route.ts | CREATE | New API endpoint |

#### Indirect Impact
| File | Reason | Change Needed |
|------|--------|---------------|
| src/components/Layout.tsx | Imports modified module | Update import |
| src/hooks/useData.ts | Uses changed API | Update response handling |

#### Dependency Analysis
```
[Changed Module]
    │
    ├── Depends on:
    │   ├── lib/utils.ts (no change needed)
    │   └── lib/api.ts (no change needed)
    │
    └── Used by:
        ├── components/Dashboard.tsx (UPDATE NEEDED)
        └── pages/Home.tsx (UPDATE NEEDED)
```

### STORY-002: [Title]
[Same structure]

---

## API Impact Analysis

### Endpoint Changes

| Method | Endpoint | Change | Breaking |
|--------|----------|--------|----------|
| POST | /api/users | New endpoint | No |
| PUT | /api/users/:id | Modified body | Yes |
| GET | /api/data | Response changed | No |

### Breaking Changes Detail

**PUT /api/users/:id**
```diff
Request Body:
{
  "name": "string",
- "email": "string"
+ "email": "string",
+ "preferences": {
+   "theme": "light" | "dark",
+   "notifications": boolean
+ }
}
```

**Migration Strategy**: [How to handle breaking changes]

---

## Database Impact Analysis

### Schema Changes

| Table | Change | Migration |
|-------|--------|-----------|
| users | Add column | ALTER TABLE |
| preferences | New table | CREATE TABLE |

### Migration Scripts

```sql
-- Migration: Add user preferences
ALTER TABLE users ADD COLUMN preferences_id UUID;

CREATE TABLE preferences (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    theme VARCHAR(10) DEFAULT 'light',
    notifications BOOLEAN DEFAULT true
);
```

### Data Migration

- [ ] Backfill existing users with default preferences
- [ ] Estimated records: [count]
- [ ] Estimated time: [duration]

---

## Test Impact Analysis

### Tests Requiring Updates

| Test File | Reason | Action |
|-----------|--------|--------|
| tests/user.test.ts | API change | Update request body |
| tests/dashboard.test.ts | Component change | Update assertions |

### New Tests Required

| Story | Test Type | Description |
|-------|-----------|-------------|
| STORY-001 | Unit | Test new component |
| STORY-001 | Integration | Test API endpoint |
| STORY-002 | E2E | Test user flow |

### Regression Test Areas

| Area | Risk Level | Reason |
|------|------------|--------|
| User authentication | High | Touches auth module |
| Data display | Medium | Modified data flow |
| Navigation | Low | Minor UI change |

---

## Risk Assessment

### High Risk Items

| Item | Risk | Impact | Mitigation |
|------|------|--------|------------|
| [Item] | [Why risky] | [What could go wrong] | [How to mitigate] |

### Backwards Compatibility

| Change | Compatible | Migration Path |
|--------|------------|----------------|
| API change | No | Version API, deprecate old |
| DB schema | Yes | Add column with default |

---

## Recommendations

### Before Development
1. [ ] Create database migration scripts
2. [ ] Set up feature flags
3. [ ] Prepare rollback plan

### During Development
1. [ ] Update tests as code changes
2. [ ] Maintain backwards compatibility
3. [ ] Document API changes

### Before Release
1. [ ] Run full regression suite
2. [ ] Verify data migration
3. [ ] Test rollback procedure

---

Generated by BMAD Iteration Workflow - Phase 3: Impact Analysis
```

#### Artifact 2: `docs/bmad-iter/[iter-id]/03-impact/design-delta.md`

```markdown
# Design Delta Document

## Purpose

This document captures architectural changes required for the current iteration, serving as the incremental update to the baseline architecture.

---

## Architecture Changes

### Component Diagram Update

```
BEFORE:
┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    API      │
└─────────────┘     └─────────────┘

AFTER:
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│    API      │────▶│ Preferences │
└─────────────┘     └─────────────┘     │   Service   │
                                        └─────────────┘
```

### New Components

#### [Component Name]
- **Purpose**: [Why it's needed]
- **Location**: src/[path]
- **Interfaces**: [Key interfaces]
- **Dependencies**: [What it depends on]

### Modified Components

#### [Existing Component]
- **Current**: [How it works now]
- **Change**: [What's changing]
- **Interface Impact**: [API/props changes]

---

## Data Model Changes

### New Entities

```typescript
// preferences.ts
interface Preferences {
  id: string;
  userId: string;
  theme: 'light' | 'dark';
  notifications: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### Modified Entities

```typescript
// user.ts
interface User {
  id: string;
  email: string;
  name: string;
+ preferencesId?: string;  // NEW
+ preferences?: Preferences;  // NEW relation
}
```

---

## API Changes

### New Endpoints

```yaml
POST /api/preferences:
  description: Create user preferences
  request:
    body:
      theme: string
      notifications: boolean
  response:
    201:
      id: string
      theme: string
      notifications: boolean

GET /api/preferences/:userId:
  description: Get user preferences
  response:
    200:
      id: string
      theme: string
      notifications: boolean
```

### Modified Endpoints

```yaml
PUT /api/users/:id:
  changes:
    - Added preferences field to request body
    - Added preferences relation in response
```

---

## State Management Changes

### New State

```typescript
// preferencesStore.ts
interface PreferencesState {
  preferences: Preferences | null;
  loading: boolean;
  error: string | null;
}
```

### Modified State

```typescript
// userStore.ts
interface UserState {
  user: User | null;
+ preferences: Preferences | null;  // NEW
}
```

---

## Configuration Changes

### Environment Variables

```bash
# New variables
PREFERENCES_SERVICE_URL=http://localhost:3001

# Modified variables
# (none)
```

### Feature Flags

```yaml
feature_flags:
  user_preferences: true  # NEW
  dark_mode: false        # Dependent on user_preferences
```

---

## Migration Plan

### Phase 1: Database
1. Run migration to add preferences table
2. Run migration to add foreign key to users

### Phase 2: Backend
1. Deploy preferences service
2. Update user API

### Phase 3: Frontend
1. Deploy UI changes behind feature flag
2. Enable feature flag

### Rollback Plan
1. Disable feature flag
2. Revert backend deployment
3. Keep database changes (backwards compatible)

---

Generated by BMAD Iteration Workflow - Phase 3: Impact Analysis
```

## Output Requirements

### Artifact Locations

```
docs/bmad-iter/[iter-id]/03-impact/
├── impact-report.md        # Full impact analysis
└── design-delta.md         # Architecture changes
```

### Steps

1. **Read iteration plan and stories**

2. **Analyze codebase**
   ```bash
   # Find files that might be affected
   grep -r "[search-term]" src/
   ```

3. **Generate impact report and design delta**

4. **Update state**
   ```yaml
   # .bmad-iter/state.yaml
   workflow:
     current_phase: 3
     phase_status:
       2: completed
       3: completed
   ```

5. **Commit to git**
   ```bash
   git add docs/bmad-iter/[iter-id]/03-impact/
   git commit -m "feat(bmad-iter): Phase 3 - Impact analysis complete"
   ```

## Success Criteria

- [ ] All stories analyzed for code impact
- [ ] API changes documented
- [ ] Database changes documented
- [ ] Test impact assessed
- [ ] Risks identified
- [ ] Design delta created
- [ ] Both artifacts created
- [ ] State updated

## Skip Conditions

For **quick iterations** with small changes:
- If all changes are S complexity
- If no API/database changes
- If impact is obviously contained

You may generate a simplified impact report and proceed.

## Next Phase

After completing this phase, run:
```
/bmad-iter-dev
```

Or:
```
/bmad-iter next
```

This will initiate Phase 4: Incremental Development.

---

**IMPORTANT**:
- Be thorough with dependency analysis
- Don't underestimate ripple effects
- Flag breaking changes prominently
- Include rollback considerations
