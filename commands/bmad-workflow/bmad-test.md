---
description: BMAD Phase 5 - Comprehensive testing, quality assurance, and validation of implemented features
argument-hint: [test-scope]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-sonnet-4-20250514
---

# BMAD Phase 5: Testing

You are initiating **Phase 5 of the BMAD workflow** - the Testing phase. Your role is to ensure comprehensive quality assurance through multi-layered testing and validation.

## Context

**Test Scope** (optional): $ARGUMENTS
- If empty: Run full test suite
- If specified: Focus on specific epic/feature

**Previous Phase Artifacts**:
@docs/bmad/02-planning/prd.md
@docs/bmad/02-planning/user-stories.md
@docs/bmad/03-architecture/architecture.md

**Current Project State**:
- Test files: !`find tests -name "*.test.ts" -o -name "*.spec.ts" 2>/dev/null | wc -l`
- Source files: !`find src -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l`
- Git status: !`git status --short`

## Your Mission

As the **QA Agent**, execute comprehensive testing to validate all implemented features meet requirements.

### Step 1: Test Inventory

Create a test inventory to track coverage:

#### Artifact: docs/bmad/test-report.md

```markdown
# Test Report

## Summary
- **Date**: [Current Date]
- **Scope**: [Full/Specific Epic]
- **Status**: [In Progress/Complete]

## Test Coverage

### Unit Tests
| File | Tests | Passing | Coverage |
|------|-------|---------|----------|
| [file] | [#] | [#/✓/✗] | [%] |

### Integration Tests
| Test Suite | Tests | Passing |
|------------|-------|---------|
| [suite] | [#] | [#/✓/✗] |

### E2E Tests
| Flow | Steps | Status |
|------|-------|--------|
| [flow] | [#] | [✓/✗] |

## Issues Found
| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| [#] | [High/Med/Low] | [Description] | [Open/Fixed] |

---
```

### Step 2: Test Execution

Execute tests in order of speed and isolation:

#### 2.1 Unit Tests

```bash
# Run unit tests with coverage
npm test -- --coverage

# Watch mode for fixing failures
npm test -- --watch
```

**Check for:**
- [ ] All unit tests passing
- [ ] Coverage > 80% for critical paths
- [ ] No skipped tests without justification

#### 2.2 Integration Tests

```bash
# Run integration tests
npm run test:integration

# With database (if applicable)
npm run test:integration:db
```

**Check for:**
- [ ] API endpoints return correct responses
- [ ] Database operations work correctly
- [ ] Authentication flows function properly

#### 2.3 End-to-End Tests

```bash
# Run E2E tests
npm run test:e2e

# With headed browser for debugging
npm run test:e2e:headed
```

**Check for:**
- [ ] Critical user flows complete successfully
- [ ] UI renders correctly
- [ ] Forms submit and validate properly

### Step 3: Quality Gates

Run quality checks:

#### 3.1 Type Checking
```bash
npm run type-check
# Should have: 0 errors
```

#### 3.2 Linting
```bash
npm run lint
# Should have: 0 errors, minimal warnings
```

#### 3.3 Build Verification
```bash
npm run build
# Should complete without errors
```

#### 3.4 Security Scan
```bash
npm audit
# Check for high/critical vulnerabilities
```

### Step 4: Acceptance Testing

Verify each user story's acceptance criteria:

```markdown
## Acceptance Test Results

### EPIC-001

#### STORY-001: [Title]
| Acceptance Criterion | Test Method | Result |
|---------------------|-------------|--------|
| AC1: [Criterion] | [Unit/Integration/E2E/Manual] | [✓/✗] |
| AC2: [Criterion] | [Test Method] | [✓/✗] |
| AC3: [Criterion] | [Test Method] | [✓/✗] |

**Status**: [PASS/FAIL]
**Notes**: [Any observations]

#### STORY-002: [Title]
[Same structure]
```

### Step 5: Performance Testing

Basic performance validation:

```bash
# Build performance
npm run build
# Note: Build time should be < 60s

# Lighthouse audit (if web app)
npx lighthouse http://localhost:3000 --output json --output-path ./lighthouse-report.json
```

**Check for:**
- [ ] Build time reasonable
- [ ] Bundle size within limits
- [ ] Lighthouse scores acceptable (>80)

### Step 6: Test Report Generation

Generate final test report:

#### Artifact: docs/bmad/test-report.md (updated)

```markdown
# Test Report - Final

## Executive Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Unit Test Coverage | >80% | [X]% | [✓/✗] |
| Unit Tests Passing | 100% | [X]% | [✓/✗] |
| Integration Tests | 100% | [X]% | [✓/✗] |
| E2E Critical Paths | 100% | [X]% | [✓/✗] |
| Type Errors | 0 | [X] | [✓/✗] |
| Lint Errors | 0 | [X] | [✓/✗] |
| Build Success | Yes | [Yes/No] | [✓/✗] |
| Security Issues | 0 High | [X] | [✓/✗] |

## Test Results

### Unit Tests
```
[Output from npm test]
```

### Integration Tests
```
[Output from integration tests]
```

### E2E Tests
```
[Output from E2E tests]
```

## Issues & Recommendations

### Critical Issues (Must Fix Before Deploy)
1. [Issue description and fix recommendation]

### Warnings (Should Fix)
1. [Warning description]

### Suggestions (Nice to Have)
1. [Suggestion]

## Acceptance Test Matrix

| Story | AC1 | AC2 | AC3 | AC4 | Overall |
|-------|-----|-----|-----|-----|---------|
| STORY-001 | ✓ | ✓ | ✓ | - | PASS |
| STORY-002 | ✓ | ✓ | ✗ | ✓ | FAIL |

## Sign-off

- [ ] All critical tests passing
- [ ] No high-severity security issues
- [ ] Build completes successfully
- [ ] All acceptance criteria verified
- [ ] Performance benchmarks met

**QA Approval**: [Approved/Not Approved]
**Date**: [Date]
**Notes**: [Any conditions or notes]

---
Generated by BMAD Workflow - Phase 5: Testing
```

## Output Requirements

### 文件沉淀位置

```
docs/bmad/05-testing/
├── test-report.md          # 测试报告
└── coverage/               # 覆盖率报告 (可选)
    └── index.html
```

### 操作步骤

1. **创建目录结构**
   ```bash
   mkdir -p docs/bmad/05-testing/coverage
   ```

2. **执行测试套件**
   - Unit tests
   - Integration tests
   - E2E tests

3. **写入测试报告**
   - `docs/bmad/05-testing/test-report.md`

4. **更新状态** (如果 .bmad/ 存在)
   ```yaml
   # .bmad/state.yaml
   workflow:
     current_phase: 5
     phase_status:
       4: completed
       5: completed
   metrics:
     test_coverage: [coverage%]
   ```

5. **提交到git**
   ```bash
   git add docs/bmad/05-testing/
   git commit -m "test(bmad): Phase 5 - Test report complete"
   ```

## Test Fix Workflow

If tests fail:

```
┌─────────────────────────────────────────────────────────┐
│ 1. IDENTIFY FAILURE                                     │
│    Read test output carefully                          │
│    Identify root cause                                 │
├─────────────────────────────────────────────────────────┤
│ 2. FIX CODE (not test)                                 │
│    Unless test is incorrect                            │
│    Implement proper fix                                │
├─────────────────────────────────────────────────────────┤
│ 3. RE-RUN TESTS                                        │
│    npm test                                            │
│    Verify fix doesn't break other tests                │
├─────────────────────────────────────────────────────────┤
│ 4. COMMIT FIX                                          │
│    git commit -m "fix: [description] - fixes #[issue]" │
└─────────────────────────────────────────────────────────┘
```

## Success Criteria

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Critical E2E flows passing
- [ ] Code coverage meets targets
- [ ] No TypeScript errors
- [ ] No lint errors
- [ ] Build succeeds
- [ ] No high-severity security issues
- [ ] All acceptance criteria verified
- [ ] Test report generated and committed

## Next Phase

After completing this phase with all tests passing:

```
/bmad-deploy staging
```

This will initiate Phase 6: Deployment to staging environment.

If tests are failing:
1. Fix the issues
2. Re-run `/bmad-test`
3. Repeat until all pass

---

**IMPORTANT**:
- Never deploy with failing tests
- Fix code, not tests (unless test is wrong)
- Document all issues found, even if fixed
- Security issues are blockers
