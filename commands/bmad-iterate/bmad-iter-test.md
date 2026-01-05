---
description: BMAD Iteration Phase 5 - Run regression tests, validate all changes, and ensure no existing functionality is broken
argument-hint: [test-scope]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-sonnet-4-20250514
---

# BMAD Iteration Phase 5: Regression Testing

You are initiating **Phase 5 of the BMAD Iteration workflow** - Regression Testing. Your role is to verify that all changes work correctly and no existing functionality has been broken.

## Context

**Test Scope** (optional): $ARGUMENTS
- `full` - Complete regression suite
- `affected` - Only areas affected by changes
- `quick` - Smoke tests only

**Previous Phase Artifacts**:
@docs/bmad-iter/[iter-id]/04-dev/_progress.md
@docs/bmad-iter/[iter-id]/04-dev/stories/*.md

**Test Infrastructure**:
- Test framework: !`cat package.json 2>/dev/null | grep -A5 '"devDependencies"' | head -10`
- Test files: !`find tests -type f -name "*.test.*" 2>/dev/null | wc -l`
- Coverage config: !`cat jest.config.* vitest.config.* 2>/dev/null | head -20`

## Your Mission

As the **Regression Tester Agent**, ensure all changes meet quality standards and don't introduce regressions.

### Step 1: Test Preparation

Prepare the test environment:

1. **Identify Test Scope**
   - Stories completed in this iteration
   - Files changed
   - Areas potentially affected

2. **Check Test Infrastructure**
   - Test framework configured
   - Test database/fixtures available
   - Environment variables set

3. **Review Existing Tests**
   - Tests for changed code
   - Related integration tests
   - E2E test coverage

### Step 2: Execute Test Suite

Run comprehensive tests:

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests (if applicable)
npm run test:e2e

# Coverage report
npm run test:coverage
```

### Step 3: Analyze Results

For each test category:

1. **Passing Tests**
   - Verify expected behavior
   - Check assertion quality

2. **Failing Tests**
   - Identify root cause
   - Categorize: regression vs. expected failure
   - Link to relevant story

3. **Skipped Tests**
   - Understand why skipped
   - Determine if should be enabled

### Step 4: Generate Regression Report

#### Artifact: `docs/bmad-iter/[iter-id]/05-test/regression-report.md`

```markdown
# Regression Test Report

## Report Info
- **Iteration**: [iter-id]
- **Date**: [Current Date]
- **Test Scope**: full | affected | quick
- **Tester**: BMAD Regression Tester Agent

---

## Executive Summary

**Overall Status**: PASS | FAIL | BLOCKED

| Metric | Value |
|--------|-------|
| Total Tests | [count] |
| Passing | [count] ([%]) |
| Failing | [count] ([%]) |
| Skipped | [count] ([%]) |
| Duration | [time] |

**Recommendation**: [Ready for release / Requires fixes / Blocked]

---

## Test Results by Category

### Unit Tests

| Suite | Tests | Pass | Fail | Skip | Duration |
|-------|-------|------|------|------|----------|
| [suite] | [n] | [n] | [n] | [n] | [time] |

**Failing Tests**:
| Test | Error | Story | Fix Required |
|------|-------|-------|--------------|
| [test name] | [error message] | STORY-XXX | [action] |

### Integration Tests

| Suite | Tests | Pass | Fail | Skip | Duration |
|-------|-------|------|------|------|----------|
| [suite] | [n] | [n] | [n] | [n] | [time] |

**Failing Tests**:
| Test | Error | Story | Fix Required |
|------|-------|-------|--------------|
| [test name] | [error message] | STORY-XXX | [action] |

### E2E Tests

| Flow | Tests | Pass | Fail | Skip | Duration |
|------|-------|------|------|------|----------|
| [flow] | [n] | [n] | [n] | [n] | [time] |

**Failing Tests**:
| Test | Error | Story | Fix Required |
|------|-------|-------|--------------|
| [test name] | [error message] | STORY-XXX | [action] |

---

## Regression Analysis

### New Regressions Detected

| ID | Test | Expected | Actual | Cause | Severity |
|----|------|----------|--------|-------|----------|
| REG-001 | [test] | [expected] | [actual] | [cause] | Critical/High/Medium/Low |

### Regressions by Story

| Story | Regressions | Tests Fixed | Status |
|-------|-------------|-------------|--------|
| STORY-001 | 0 | N/A | Clean |
| STORY-002 | 2 | 1 | In Progress |

---

## Coverage Analysis

### Coverage Summary

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Statements | [%] | [%] | [+/-]% |
| Branches | [%] | [%] | [+/-]% |
| Functions | [%] | [%] | [+/-]% |
| Lines | [%] | [%] | [+/-]% |

### Coverage by Changed File

| File | Coverage | Change | Status |
|------|----------|--------|--------|
| src/[path] | [%] | [+/-]% | Good/Needs Work |

### Uncovered Code

| File | Lines | Reason |
|------|-------|--------|
| src/[path] | [line numbers] | [why uncovered] |

---

## Performance Testing

### Response Time Changes

| Endpoint/Function | Before | After | Delta | Status |
|-------------------|--------|-------|-------|--------|
| [name] | [ms] | [ms] | [+/-]% | OK/Warning/Fail |

### Memory Usage

| Scenario | Before | After | Delta | Status |
|----------|--------|-------|-------|--------|
| [scenario] | [MB] | [MB] | [+/-]% | OK/Warning/Fail |

---

## Security Scan Results

### Vulnerability Summary

| Severity | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| Critical | [n] | [n] | [n] |
| High | [n] | [n] | [n] |
| Medium | [n] | [n] | [n] |
| Low | [n] | [n] | [n] |

### New Vulnerabilities

| ID | Package | Severity | Description | Action |
|----|---------|----------|-------------|--------|
| [CVE] | [pkg] | [level] | [desc] | [action] |

---

## Manual Testing

### Acceptance Criteria Verification

| Story | AC | Test Method | Result | Notes |
|-------|-----|-------------|--------|-------|
| STORY-001 | AC1 | Automated | Pass | |
| STORY-001 | AC2 | Manual | Pass | [notes] |
| STORY-002 | AC1 | Automated | Fail | [issue] |

### Exploratory Testing

| Area | Tester | Issues Found | Severity |
|------|--------|--------------|----------|
| [area] | Agent | [count] | [level] |

**Issues Discovered**:
| ID | Description | Severity | Story | Status |
|----|-------------|----------|-------|--------|
| ISS-001 | [description] | [level] | STORY-XXX | Open |

---

## Blockers and Issues

### Critical Blockers

| Blocker | Impact | Resolution | Owner |
|---------|--------|------------|-------|
| [blocker] | [what's blocked] | [resolution needed] | [who] |

### Open Issues

| Issue | Severity | Story | Status | ETA |
|-------|----------|-------|--------|-----|
| [issue] | [level] | STORY-XXX | [status] | [date] |

---

## Recommendations

### Before Release
- [ ] [Required fix 1]
- [ ] [Required fix 2]

### Post-Release Monitoring
- [ ] [What to monitor]
- [ ] [Metrics to watch]

### Technical Debt
- [ ] [Debt item to address]

---

## Test Environment

| Component | Version |
|-----------|---------|
| Node.js | [version] |
| Test Framework | [name] [version] |
| Browser | [if applicable] |
| Database | [if applicable] |

---

## Sign-Off

| Role | Status | Date |
|------|--------|------|
| QA Agent | [Pass/Fail] | [date] |
| Dev Lead | Pending | - |
| Release Manager | Pending | - |

---

Generated by BMAD Iteration Workflow - Phase 5: Regression Testing
```

### Step 5: Handle Test Failures

If tests fail:

1. **Categorize Failures**
   - Regression (broke existing functionality)
   - Expected failure (test needs update)
   - Flaky test (intermittent failure)
   - Environment issue

2. **For Regressions**
   - Create issue linked to causing story
   - Prioritize fix based on severity
   - Re-test after fix

3. **For Expected Failures**
   - Update test to match new behavior
   - Document why test changed
   - Verify with story AC

### Step 6: Quality Gate Check

Verify iteration meets quality standards:

```
┌─────────────────────────────────────────────────────────────┐
│                    QUALITY GATE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GATE 1: All Tests Pass                              │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ ✓ Unit tests: 100% pass                             │   │
│  │ ✓ Integration tests: 100% pass                      │   │
│  │ ✓ E2E tests: 100% pass                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GATE 2: Coverage Maintained                         │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ ✓ Coverage delta >= 0% (no decrease)                │   │
│  │ ✓ New code coverage >= 80%                          │   │
│  │ ✓ Critical paths 100% covered                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GATE 3: No Regressions                              │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ ✓ No new failures in existing tests                 │   │
│  │ ✓ Performance within acceptable range               │   │
│  │ ✓ No new security vulnerabilities                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ GATE 4: Acceptance Criteria                         │   │
│  │ ─────────────────────────────────────────────────── │   │
│  │ ✓ All story ACs verified                            │   │
│  │ ✓ Manual testing complete                           │   │
│  │ ✓ No critical/high issues open                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│               [PROCEED TO RELEASE]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Output Requirements

### Artifact Locations

```
docs/bmad-iter/[iter-id]/05-test/
├── regression-report.md        # Main test report
├── coverage/                   # Coverage reports
│   └── summary.html
└── logs/                       # Test logs
    └── test-run-[date].log
```

### State Update

```yaml
# .bmad-iter/state.yaml
workflow:
  current_phase: 5
  phase_status:
    4: completed
    5: completed  # or: in_progress if issues found

quality_gate:
  tests_pass: true
  coverage_maintained: true
  no_regressions: true
  acceptance_verified: true

test_results:
  total: 150
  passed: 148
  failed: 2
  skipped: 0
  coverage: "85.3%"
```

### Steps

1. **Read development progress from Phase 4**

2. **Run test suite**
   ```bash
   npm test -- --coverage
   ```

3. **Generate regression report**

4. **Update state**

5. **Commit to git**
   ```bash
   git add docs/bmad-iter/[iter-id]/05-test/
   git commit -m "feat(bmad-iter): Phase 5 - Regression testing complete

   - All tests passing
   - Coverage: [X]%
   - No regressions detected"
   ```

## Success Criteria

- [ ] All tests executed
- [ ] No regressions detected (or all fixed)
- [ ] Coverage maintained or improved
- [ ] All acceptance criteria verified
- [ ] Security scan clean
- [ ] Performance within bounds
- [ ] Report generated
- [ ] Quality gate passed

## Test Strategies by Scope

### Full Regression

```bash
# Run everything
npm test
npm run test:integration
npm run test:e2e
npm run test:coverage
npm audit
```

### Affected Only

```bash
# Run tests related to changed files
npm test -- --changedSince=main
npm run test:integration -- --grep "[affected-area]"
```

### Quick Smoke

```bash
# Critical path tests only
npm test -- --testPathPattern="smoke"
npm run test:e2e -- --spec "critical/**"
```

## Next Phase

If all quality gates pass:
```
/bmad-iter-release
```

Or:
```
/bmad-iter next
```

If issues found:
```
/bmad-iter story [story-to-fix]
```

This will initiate Phase 6: Release Management.

---

**IMPORTANT**:
- Never skip tests to meet deadlines
- Fix regressions before proceeding
- Document all test failures
- Keep coverage from decreasing
- Flag security issues immediately
