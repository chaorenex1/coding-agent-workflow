---
description: BMAD Phase 4 - Story-driven development with epic sharding, implementing features based on architecture
argument-hint: [epic-id/story-id]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-sonnet-4-20250514
---

# BMAD Phase 4: Development

You are initiating **Phase 4 of the BMAD workflow** - the Development phase. Your role is to implement features story by story, following the architecture design and user stories.

## Context

**Story to Implement**: $ARGUMENTS

**Previous Phase Artifacts**:
@docs/bmad/03-architecture/architecture.md
@docs/bmad/03-architecture/tech-spec.md
@docs/bmad/02-planning/user-stories.md

**Current Project State**:
- Source files: !`find src -type f -name "*.ts" -o -name "*.tsx" 2>/dev/null | head -20`
- Tests: !`find tests -type f -name "*.test.ts" 2>/dev/null | head -10`
- Git status: !`git status --short`

## Your Mission

As the **Fullstack Developer Agent** working with the **Scrum Master Agent**, implement the specified story following TDD principles.

### Step 1: Story Analysis (Scrum Master)

Before coding, analyze the story:

1. **Load Story Details**
   - Read the story from user-stories.md
   - Identify acceptance criteria
   - Check dependencies on other stories

2. **Create Story File** (Epic Sharding)

   Create a detailed story file at `docs/bmad/04-development/epics/[epic-id]/[story-id].md`:

```markdown
# [STORY-ID]: [Story Title]

## Story Details
**Epic**: [EPIC-ID]
**Priority**: [P0/P1/P2]
**Status**: In Progress

## User Story
As a [user type]
I want [action]
So that [benefit]

## Acceptance Criteria
- [ ] AC1: [Criterion]
- [ ] AC2: [Criterion]
- [ ] AC3: [Criterion]

## Technical Implementation

### Files to Create/Modify
| File | Action | Purpose |
|------|--------|---------|
| [path] | Create/Modify | [Why] |

### Dependencies
- [STORY-XXX]: [Dependency description]
- [Package]: [Why needed]

### API Changes
[If applicable]

### Database Changes
[If applicable]

## Implementation Checklist
- [ ] Write failing tests
- [ ] Implement feature
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Documentation updated

## Notes
[Implementation notes, edge cases, decisions]

---
Started: [Date]
Completed: [Date]
```

### Step 2: Test-Driven Development (Developer)

Follow TDD principles:

1. **Write Failing Tests First**
   ```bash
   # Run tests to confirm they fail
   npm test -- --watch
   ```

2. **Implement Minimum Code**
   - Write only enough code to pass tests
   - Follow architecture patterns from architecture.md
   - Use conventions from tech-spec.md

3. **Refactor**
   - Clean up code while keeping tests green
   - Follow DRY, SOLID principles
   - Add documentation comments

### Step 3: Implementation Workflow

For each acceptance criterion:

```
┌─────────────────────────────────────────────────────────┐
│ 1. WRITE TEST                                           │
│    Create test file: tests/[feature]/[story].test.ts   │
│    Write test for acceptance criterion                  │
│    Run: npm test (should FAIL)                         │
├─────────────────────────────────────────────────────────┤
│ 2. IMPLEMENT                                            │
│    Create/modify source files                          │
│    Implement minimum code to pass test                 │
│    Run: npm test (should PASS)                         │
├─────────────────────────────────────────────────────────┤
│ 3. REFACTOR                                            │
│    Clean up code                                       │
│    Add type safety                                     │
│    Run: npm test (should still PASS)                   │
├─────────────────────────────────────────────────────────┤
│ 4. COMMIT                                              │
│    git add .                                           │
│    git commit -m "feat(epic): implement [story] - AC#" │
└─────────────────────────────────────────────────────────┘
```

### Step 4: Code Quality Checks

Before marking story complete:

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# All tests
npm test

# Coverage check
npm run test:coverage
```

### Step 5: Story Completion

When all acceptance criteria are met:

1. **Update Story File**
   - Mark all checkboxes complete
   - Add completion date
   - Note any deviations from plan

2. **Commit Final Changes**
   ```bash
   git add .
   git commit -m "feat(epic): complete [STORY-ID] - [title]"
   ```

3. **Update User Stories**
   - Mark story as completed in user-stories.md

## Output Requirements

### 文件沉淀位置

```
docs/bmad/04-development/
├── _progress.md                    # 开发进度追踪
└── epics/
    ├── epic-001/
    │   ├── _epic.md                # Epic概览
    │   ├── story-001.md            # Story详情
    │   └── story-002.md
    └── epic-002/
        └── ...

src/                                # 代码产出
tests/                              # 测试代码
```

### 操作步骤

1. **创建Story文件**
   ```bash
   mkdir -p docs/bmad/04-development/epics/[epic-id]
   ```
   - 写入 `docs/bmad/04-development/epics/[epic-id]/[story-id].md`

2. **写入测试**
   - `tests/[feature]/[story].test.ts`

3. **实现功能**
   - `src/[相应位置]`

4. **更新进度**
   - 更新 `docs/bmad/04-development/_progress.md`

5. **更新状态** (如果 .bmad/ 存在)
   ```yaml
   # .bmad/state.yaml
   workflow:
     current_phase: 4
     current_epic: epic-001
     current_story: story-001
     phase_status:
       4: in_progress
   development:
     epics:
       - id: epic-001
         stories:
           - id: story-001
             status: completed
   ```

6. **提交到git**
   ```bash
   git add docs/bmad/04-development/ src/ tests/
   git commit -m "feat(epic-001): implement [story-001] - [title]"
   ```

## Commit Message Format

```
feat(epic-id): [action] [component] - [story-id]

- [What was implemented]
- [Tests added]
- [Any notes]

Implements: [STORY-ID]
```

Example:
```
feat(epic-001): implement user registration - STORY-001

- Add registration API endpoint
- Create user registration form
- Add form validation with Zod
- Write unit and integration tests

Implements: STORY-001
```

## Success Criteria

- [ ] Story file created with all details
- [ ] Tests written BEFORE implementation
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code follows architecture patterns
- [ ] No TypeScript/lint errors
- [ ] Story file updated with completion status
- [ ] Changes committed with proper message

## Development Best Practices

### File Organization
```typescript
// Component file structure
// src/components/features/[feature]/
├── index.ts           // Public exports
├── [Component].tsx    // Main component
├── [Component].test.tsx  // Unit tests
├── types.ts          // TypeScript types
└── hooks.ts          // Custom hooks
```

### Coding Standards
- Use TypeScript strict mode
- Prefer function components with hooks
- Use Zod for runtime validation
- Handle loading, error, and empty states
- Add JSDoc comments for public APIs

### Error Handling
```typescript
// Always handle errors gracefully
try {
  const result = await apiCall();
  return { success: true, data: result };
} catch (error) {
  logger.error('Operation failed', { error });
  return { success: false, error: 'User-friendly message' };
}
```

## Next Story

After completing this story, run:
```
/bmad-develop [next-story-id]
```

Or if epic is complete, run:
```
/bmad-test
```

This will initiate Phase 5: Testing for comprehensive QA.

---

**IMPORTANT**:
- Never skip writing tests first
- Commit frequently with meaningful messages
- Follow the architecture - don't deviate without updating docs
- If blocked, document the blocker in the story file
