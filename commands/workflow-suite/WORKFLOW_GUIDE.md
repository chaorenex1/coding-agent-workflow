# Workflow Guide - Development Workflow Suite

**Complete workflows and real-world examples for using the 10 slash commands effectively.**

---

## 🎯 Table of Contents

1. [Complete Development Workflows](#complete-development-workflows)
2. [Phase-Specific Workflows](#phase-specific-workflows)
3. [Role-Based Workflows](#role-based-workflows)
4. [Real-World Examples](#real-world-examples)
5. [Best Practices](#best-practices)
6. [Command Chaining](#command-chaining)

---

## 🔄 Complete Development Workflows

### Workflow 1: Full Feature Development (Requirements to Production)

**Scenario:** Building a new "User Profile Management" feature

```bash
# Phase 1: Requirements Understanding
/requirements-understanding "User profile management feature"
# Output: Requirement summary, scope, clarifying questions

# Phase 2: Ask Clarifying Questions
/ask-user "User profile data fields and validation rules"
# Output: Targeted questions for stakeholders

# [After receiving answers from stakeholders]

# Phase 3: Technical Requirements Analysis
/requirements-analysis "User profile management with validated requirements"
# Output: Technical approach, architecture impact, task breakdown

# Phase 4: Implementation Planning
/implementation-analysis "User profile management"
# Output: Code structure, API specs, implementation checklist

# Phase 5: Implementation (Manual Coding)
# ... write code ...

# Phase 6: Code Explanation (Documentation)
/explain src/services/UserProfileService.ts
# Output: Comprehensive documentation

# Phase 7: Testing
/test UserProfileService
# Output: Test generation and coverage analysis

# Phase 8: Optimization (if needed)
/optimization getUserProfile
# Output: Performance improvements

# Phase 9: Quality Check
/refactoring src/services/UserProfileService.ts
# Output: Code quality improvements
```

**Time Estimate:** 2-4 hours (vs 6-8 hours manually)
**Coverage:** Complete feature lifecycle

---

### Workflow 2: Rapid Bug Fix (Production Issue)

**Scenario:** Critical bug in production - users can't checkout

```bash
# Step 1: Quick Debug (5 minutes)
/debug "checkout fails with 500 error"
# Output: Root cause analysis

# Step 2: Implement Fix (15 minutes)
/fix "Null pointer in payment validation at checkout"
# Output: Bug fix with code changes

# Step 3: Add Regression Tests (10 minutes)
/test "checkout flow with edge cases"
# Output: Comprehensive test suite

# Step 4: Verify Fix (5 minutes)
# Run tests manually or via command
npm test

# Step 5: Deploy
git add .
git commit -m "fix: resolve checkout null pointer issue"
git push
```

**Total Time:** ~35 minutes (vs 2-3 hours manually)
**Risk:** Low (includes tests and verification)

---

### Workflow 3: Legacy Code Modernization

**Scenario:** Refactor old payment processing code

```bash
# Step 1: Understand Current Code (10 minutes)
/explain src/legacy/payment-processor.js
# Output: Current architecture and flow

# Step 2: Identify Issues (15 minutes)
/refactoring src/legacy/payment-processor.js
# Output: Code smells and refactoring plan

# Step 3: Plan New Implementation (20 minutes)
/implementation-analysis "Modern payment processing with proper error handling"
# Output: New architecture design

# Step 4: Implement Refactoring (Manual - 2 hours)
# ... refactor code ...

# Step 5: Add Comprehensive Tests (20 minutes)
/test PaymentProcessor
# Output: Full test suite

# Step 6: Optimize (15 minutes)
/optimization processPayment
# Output: Performance improvements

# Step 7: Document New Code (10 minutes)
/explain src/services/PaymentProcessor.ts
# Output: Updated documentation
```

**Total Time:** ~3 hours (vs 8-10 hours manually)
**Benefits:** Better quality, documented, tested

---

## 📋 Phase-Specific Workflows

### Requirements Phase

**Goal:** Crystal-clear requirements before coding

```bash
# 1. Initial Understanding
/requirements-understanding "[feature request or user story]"

# 2. Generate Stakeholder Questions
/ask-user "[specific ambiguous areas]"

# 3. Technical Feasibility
/requirements-analysis "[feature with clarifications]"

# 4. Final Planning
/implementation-analysis "[approved requirements]"
```

**Deliverables:**
- Requirement document
- Stakeholder Q&A
- Technical specification
- Implementation plan

---

### Implementation Phase

**Goal:** Efficient, well-planned coding

```bash
# 1. Before Coding - Review Plan
/implementation-analysis "[feature name]"

# 2. During Coding - Understand Dependencies
/explain "[related existing code]"

# 3. After Coding - Self-Review
/refactoring "[newly written code]"

# 4. Documentation
/explain "[newly written code]"
```

**Deliverables:**
- Well-structured code
- Inline documentation
- Architecture documentation

---

### Testing Phase

**Goal:** Comprehensive test coverage

```bash
# 1. Generate Tests
/test "[component or feature]"

# 2. Run Tests
npm test  # or pytest

# 3. Analyze Coverage
npm test -- --coverage

# 4. Add Missing Tests
/test "[uncovered areas]"
```

**Deliverables:**
- Unit tests
- Integration tests
- 80%+ coverage

---

### Quality Phase

**Goal:** Production-ready code

```bash
# 1. Code Quality Review
/refactoring "[code to improve]"

# 2. Performance Check
/optimization "[performance-critical code]"

# 3. Final Explanation/Docs
/explain "[complete feature]"
```

**Deliverables:**
- Clean, maintainable code
- Optimized performance
- Complete documentation

---

### Maintenance Phase

**Goal:** Quick issue resolution

```bash
# 1. Investigate Issue
/debug "[error or bug report]"

# 2. Fix Issue
/fix "[identified bug]"

# 3. Prevent Regression
/test "[fixed component]"

# 4. Verify Quality
/refactoring "[modified code]"
```

**Deliverables:**
- Bug fix
- Regression tests
- Improved code quality

---

## 👥 Role-Based Workflows

### For Developers

#### Daily Development

**Morning Routine:**
```bash
# Check for issues
/debug

# Review yesterday's code
/explain src/components/MyComponent.tsx
```

**During Development:**
```bash
# Before implementing feature
/implementation-analysis "new feature"

# While coding
/explain "related code"

# After coding
/test MyNewComponent
/refactoring MyNewComponent
```

**Before Commit:**
```bash
# Final checks
/test src/
/refactoring src/components/
```

---

### For Tech Leads

#### Feature Planning

```bash
# 1. Requirements Review
/requirements-understanding "[feature request]"

# 2. Generate Questions for PM
/ask-user "[feature decisions]"

# 3. Technical Analysis
/requirements-analysis "[feature]"

# 4. Architecture Design
/implementation-analysis "[feature]"

# 5. Task Breakdown (use output from step 4)
```

#### Code Review

```bash
# 1. Understand Changes
/explain "[changed files]"

# 2. Quality Check
/refactoring "[changed files]"

# 3. Performance Review
/optimization "[changed functions]"

# 4. Test Coverage
/test "[changed components]"
```

---

### For Product Managers

#### Requirements Gathering

```bash
# 1. Analyze Feature Request
/requirements-understanding "[user story]"

# 2. Generate Stakeholder Questions
/ask-user "[ambiguous requirements]"

# 3. Technical Feasibility
/requirements-analysis "[complete requirements]"
```

#### Feature Documentation

```bash
# 1. Technical Documentation
/explain "[implemented feature]"

# 2. Generate Implementation Summary
/implementation-analysis "[feature]"
```

---

## 🌟 Real-World Examples

### Example 1: E-Commerce Cart Feature

**Context:** Add shopping cart to e-commerce site

```bash
# Step 1: Requirements (30 min)
/requirements-understanding "Shopping cart with persistence and discount codes"

# Output includes:
# - Functional requirements
# - Non-functional requirements
# - Clarifying questions

# Step 2: Ask Questions (15 min)
/ask-user "Cart persistence strategy and discount code validation"

# Step 3: Technical Analysis (45 min)
/requirements-analysis "Shopping cart feature with answers from stakeholders"

# Output includes:
# - Database schema
# - API endpoints
# - State management approach
# - Task breakdown with estimates

# Step 4: Implementation Planning (60 min)
/implementation-analysis "Shopping cart feature"

# Output includes:
# - File structure
# - Component hierarchy
# - Data flow
# - Interface specifications
# - Implementation checklist

# Step 5: Implement (4-6 hours)
# ... manual coding ...

# Step 6: Testing (60 min)
/test CartService
/test CartComponent

# Step 7: Optimization (30 min)
/optimization "cart operations"

# Step 8: Documentation (20 min)
/explain src/cart/CartService.ts
```

**Total Saved:** 3-4 hours compared to manual approach

---

### Example 2: API Performance Issue

**Context:** Dashboard API slow (3-5 seconds response time)

```bash
# Step 1: Debug (15 min)
/debug "Slow API response for /api/dashboard"

# Output:
# - Identified N+1 query problem
# - Database index missing
# - Unnecessary data fetching

# Step 2: Optimization Plan (30 min)
/optimization getDashboardData

# Output:
# - Query optimization strategies
# - Caching recommendations
# - Code examples
# - Expected performance gains

# Step 3: Implement Changes (60 min)
# - Add database indexes
# - Implement query batching
# - Add caching layer

# Step 4: Test (20 min)
/test "dashboard API with performance benchmarks"

# Step 5: Verify
# Run performance tests
# Response time: 3-5s → 200-300ms (10-15x improvement)

# Step 6: Document (10 min)
/explain "optimized dashboard data loading"
```

**Result:** 90% faster, documented, tested

---

### Example 3: Security Vulnerability Fix

**Context:** SQL injection vulnerability reported

```bash
# Step 1: Debug (20 min)
/debug "SQL injection in user search endpoint"

# Output:
# - Identified unsafe query construction
# - Listed all vulnerable endpoints
# - Provided exploitation examples

# Step 2: Fix (45 min)
/fix "SQL injection - use parameterized queries"

# Output:
# - Rewrote queries with parameterized approach
# - Added input validation
# - Updated all similar patterns

# Step 3: Test (30 min)
/test "user search with SQL injection attempts"

# Output:
# - Security test cases
# - Injection attempt tests
# - Input validation tests

# Step 4: Security Review (30 min)
/refactoring "all database query code"

# Output:
# - Additional security improvements
# - Best practices applied
# - Code quality enhanced

# Step 5: Documentation (15 min)
/explain "secure database query implementation"
```

**Total Time:** ~2.5 hours (vs full security audit: days)

---

## 💡 Best Practices

### Command Usage

**1. Be Specific**
```bash
# ❌ Vague
/debug error

# ✅ Specific
/debug "TypeError: Cannot read property 'id' of undefined in UserService.getUser line 42"
```

**2. Use Quotes for Multi-Word Arguments**
```bash
# ❌ Without quotes
/fix Cannot read property id

# ✅ With quotes
/fix "Cannot read property 'id' of undefined"
```

**3. Provide Context**
```bash
# ❌ No context
/optimization slow

# ✅ With context
/optimization "database queries in getUserDashboard function"
```

---

### Command Chaining

**Sequential Workflow:**
```bash
# Commands build on each other
/debug issue
# → understand the problem

/fix issue
# → implement solution

/test component
# → verify solution

/refactoring component
# → improve quality
```

**Parallel Analysis:**
```bash
# Run multiple analyses simultaneously
/explain ComponentA
/explain ComponentB
/explain ComponentC

# Compare outputs for consistency
```

---

### Output Management

**1. Capture Important Outputs**
```bash
# Save to file
/requirements-analysis "feature" > docs/technical-spec.md

# Or copy from terminal
```

**2. Use Outputs as Inputs**
```bash
# Use implementation-analysis output for actual coding
/implementation-analysis "feature"
# → Use file structure and interfaces as blueprint
```

**3. Version Control Documentation**
```bash
# Commit generated docs
git add docs/
git commit -m "docs: add technical specifications"
```

---

### Team Collaboration

**1. Standardize Workflows**
```markdown
# In CONTRIBUTING.md
## Standard Development Process
1. `/requirements-understanding` for all features
2. `/implementation-analysis` before coding
3. `/test` after implementation
4. `/refactoring` before PR
```

**2. Share Command Outputs**
```bash
# Include in PRs
/explain "new feature" > PR-description.md
/test "feature" > test-coverage-report.md
```

**3. Code Review with Commands**
```bash
# Reviewers can verify
/explain "PR changes"
/test "changed components"
/refactoring "modified code"
```

---

## 📊 Measuring Impact

### Metrics to Track

**Time Savings:**
- Debugging time: Before vs After
- Testing time: Before vs After
- Documentation time: Before vs After

**Quality Improvements:**
- Test coverage: Before vs After
- Bug count: Before vs After
- Code review time: Before vs After

**Example Tracking:**
```markdown
## Week 1 (Before Commands)
- Debugging: 8 hours
- Testing: 6 hours
- Documentation: 4 hours
- Total: 18 hours

## Week 2 (With Commands)
- Debugging: 4 hours (50% faster)
- Testing: 2.5 hours (58% faster)
- Documentation: 1 hour (75% faster)
- Total: 7.5 hours (58% faster overall)
```

---

## 🎓 Learning Path

### Week 1: Essential Commands
```bash
# Learn these first
/debug
/fix
/test
```

### Week 2: Planning Commands
```bash
# Add to your workflow
/requirements-understanding
/requirements-analysis
/implementation-analysis
```

### Week 3: Quality Commands
```bash
# Improve code quality
/refactoring
/optimization
/explain
```

### Week 4: Advanced Workflows
```bash
# Master command chaining
# Create custom workflows
# Share with team
```

---

## 🚀 Advanced Techniques

### Custom Workflow Scripts

Create shell scripts for common workflows:

```bash
#!/bin/bash
# feature-workflow.sh

FEATURE=$1

echo "=== Feature Development Workflow ==="
echo "Feature: $FEATURE"

echo "\n1. Understanding requirements..."
claude code "/requirements-understanding '$FEATURE'"

echo "\n2. Analyzing technical approach..."
claude code "/requirements-analysis '$FEATURE'"

echo "\n3. Planning implementation..."
claude code "/implementation-analysis '$FEATURE'"

echo "\n=== Ready for implementation! ==="
```

Usage:
```bash
./feature-workflow.sh "User authentication"
```

---

## 📚 Summary

### Command Selection Guide

| Task | Command | When to Use |
|------|---------|-------------|
| Bug investigation | `/debug` | Unknown issue, need root cause |
| Bug fixing | `/fix` | Know the issue, need implementation |
| Code understanding | `/explain` | New code, onboarding, documentation |
| Requirements clarity | `/requirements-understanding` | Unclear requirements |
| Technical planning | `/requirements-analysis` | Need architecture design |
| Decision making | `/ask-user` | Multiple options, need input |
| Implementation design | `/implementation-analysis` | Before coding a feature |
| Performance issues | `/optimization` | Slow code, high resource usage |
| Code quality | `/refactoring` | Technical debt, code smells |
| Testing | `/test` | Need tests, improve coverage |

---

**Master these workflows and transform your development process!** 🚀

For more information, see README.md and INSTALL.md.
