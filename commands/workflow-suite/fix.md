---
description: Automated bug fix assistant with code generation, testing, and verification
argument-hint: [bug-description|issue-number|error-message]
allowed-tools: Read, Write, Edit, Bash(git status:*), Bash(git diff:*), Bash(find:*), Bash(grep:*), Bash(npm:*), Bash(python:*), Bash(pytest:*), Bash(jest:*), Bash(node:*)
---

# Automated Bug Fix Assistant

## Context

Bug to fix: $ARGUMENTS

### Repository State
- Current branch: !`git branch --show-current`
- Uncommitted changes: !`git status --short`
- Recent commits: !`git log --oneline -3`

### Relevant Files
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -mtime -7 2>/dev/null | head -15`

## Your Task

Fix the bug "$ARGUMENTS" following this systematic process:

### Phase 1: Bug Understanding
1. **Reproduce the Bug**
   - Understand exact steps to reproduce
   - Identify expected vs actual behavior
   - Document reproduction case

2. **Locate the Bug**
   - Find the file and function causing the issue
   - Identify the specific lines of code
   - Understand the code context

### Phase 2: Fix Implementation
1. **Analyze Impact**
   - Identify all affected code paths
   - Check for similar issues elsewhere
   - Consider edge cases

2. **Implement Fix**
   - Write minimal, focused fix
   - Follow existing code patterns
   - Add necessary validation
   - Include error handling

3. **Add Safety Checks**
   - Prevent null/undefined access
   - Validate input parameters
   - Handle edge cases

### Phase 3: Verification
1. **Write/Update Tests**
   - Add test case for the bug
   - Verify fix resolves issue
   - Test edge cases

2. **Run Tests**
   - Execute relevant test suite
   - Verify no regressions
   - Check code coverage

3. **Code Review Self-Check**
   - Review for code quality
   - Check for unintended side effects
   - Verify documentation updates

## Implementation Steps

1. **Read** the buggy file(s)
2. **Analyze** the root cause
3. **Edit** the file(s) with fix
4. **Write/Update** test file(s)
5. **Run** tests to verify
6. **Report** results

## Output Format

```
🐛 BUG SUMMARY
Issue: [Description]
Location: [File:Line]
Cause: [Root cause]

🔧 FIX APPLIED
Files Modified:
- [file1]: [changes]
- [file2]: [changes]

Code Changes:
[Brief code diff or description]

✅ VERIFICATION
Tests Added/Updated:
- [test1]: [description]
- [test2]: [description]

Test Results:
[Pass/Fail status]

📝 NOTES
- [Important consideration 1]
- [Important consideration 2]
```

## Success Criteria

- ✅ Bug fix implemented correctly
- ✅ Tests added/updated to prevent regression
- ✅ All tests pass
- ✅ No unintended side effects
- ✅ Code follows project conventions
- ✅ Edge cases handled
