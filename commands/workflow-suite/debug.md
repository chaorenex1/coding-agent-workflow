---
description: Interactive debugging assistant for systematic bug investigation and root cause analysis
argument-hint: [component|error-message|file-path]
allowed-tools: Read, Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(find:*), Bash(grep:*), Bash(tail:*), Bash(head:*), Bash(cat:*), Bash(wc:*), Bash(ps:*), Bash(node:*), Bash(python:*), Bash(npm:*), Bash(pip:*)
---

# Interactive Debugging Assistant

## Context

Target: $ARGUMENTS

### Current State
- Git status: !`git status`
- Recent changes: !`git log --oneline -5`
- Modified files: !`git diff --name-only`

### Error Discovery
!`find . -type f \( -name "*.log" -o -name "error*.txt" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -10`

### Error Patterns
!`grep -r "Error\|Exception\|Traceback\|throw\|console\.error" --include="*.js" --include="*.ts" --include="*.py" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | head -20`

## Your Task

Perform systematic debugging analysis for "$ARGUMENTS":

### 1. **Problem Identification**
   - Extract error message and stack trace
   - Identify affected component/module
   - Determine error type (syntax, runtime, logic, integration)
   - Assess severity and impact

### 2. **Context Analysis**
   - Review recent code changes
   - Check related dependencies
   - Examine configuration files
   - Verify environment setup

### 3. **Root Cause Investigation**
   - Trace error propagation path
   - Identify initial failure point
   - Check for related issues
   - Review similar past bugs

### 4. **Hypothesis Formation**
   - List possible causes (ranked by probability)
   - Identify what to verify for each hypothesis
   - Suggest debugging experiments

### 5. **Debugging Strategy**
   - Provide step-by-step debugging plan
   - Suggest breakpoint locations
   - Recommend logging additions
   - Propose isolation tests

### 6. **Solution Guidance**
   - Suggest potential fixes
   - Provide code examples
   - Highlight edge cases to consider
   - Recommend prevention measures

## Output Format

```
🔍 PROBLEM ANALYSIS
Issue: [Brief description]
Location: [File:Line]
Severity: [Critical/High/Medium/Low]

📊 ERROR DETAILS
[Stack trace or error message analysis]

🎯 ROOT CAUSE
[Identified or hypothesized root cause]

🧪 DEBUGGING STEPS
1. [First verification step]
2. [Second investigation step]
3. [Third isolation step]

💡 PROPOSED SOLUTIONS
Option 1: [Quick fix with trade-offs]
Option 2: [Proper fix with implementation]

⚠️ PREVENTION
[How to avoid this in future]
```

## Success Criteria

- ✅ Error clearly understood and categorized
- ✅ Root cause identified or narrowed to 2-3 hypotheses
- ✅ Concrete debugging steps provided
- ✅ Solution options with code examples
- ✅ Prevention recommendations included
