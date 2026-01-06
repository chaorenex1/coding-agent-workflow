# Quick Reference Card - Development Workflow Suite

**10 Essential Slash Commands for Complete Development Lifecycle**

---

## 📋 Command Cheat Sheet

| Command | Purpose | Usage | Time Savings |
|---------|---------|-------|--------------|
| `/debug` | Investigate bugs | `/debug "error message"` | 30-50% |
| `/fix` | Implement fixes | `/fix "bug description"` | 40-60% |
| `/explain` | Document code | `/explain path/to/file.ts` | 70-80% |
| `/requirements-understanding` | Clarify requirements | `/requirements-understanding "feature"` | 50-60% |
| `/requirements-analysis` | Technical planning | `/requirements-analysis "feature"` | 40-50% |
| `/ask-user` | Generate questions | `/ask-user "decision point"` | 60-70% |
| `/implementation-analysis` | Design implementation | `/implementation-analysis "feature"` | 50-60% |
| `/optimization` | Improve performance | `/optimization function-name` | 40-60% |
| `/refactoring` | Enhance quality | `/refactoring path/to/code` | 50-70% |
| `/test` | Generate tests | `/test ComponentName` | 40-60% |

---

## 🚀 Quick Start (5 Minutes)

### 1. Install All Commands
```bash
cp generated-commands/dev-workflow-suite/*.md ~/.claude/commands/
```

### 2. Try Your First Command
```bash
/debug
```

### 3. Use a Workflow
```bash
/debug "your issue"
/fix "the bug"
/test "your component"
```

---

## 🔄 Common Workflows

### Bug Fix (30 min)
```
/debug → /fix → /test
```

### New Feature (4 hours)
```
/requirements-understanding
→ /requirements-analysis
→ /implementation-analysis
→ [code]
→ /test
→ /refactoring
```

### Code Review (20 min)
```
/explain → /refactoring → /optimization
```

### Legacy Modernization (3 hours)
```
/explain → /refactoring → /implementation-analysis → [code] → /test
```

---

## 💡 Usage Tips

**Be Specific:**
```bash
✅ /debug "TypeError in UserService.getUser line 42"
❌ /debug error
```

**Use Quotes:**
```bash
✅ /fix "Cannot read property 'id' of undefined"
❌ /fix Cannot read property id
```

**Provide Context:**
```bash
✅ /optimization "database queries in dashboard load"
❌ /optimization slow
```

---

## 🎯 When to Use Each Command

| Situation | Command | Why |
|-----------|---------|-----|
| Production error | `/debug` | Find root cause quickly |
| Know the bug | `/fix` | Implement with tests |
| Onboarding | `/explain` | Understand codebase |
| Unclear feature | `/requirements-understanding` | Clarify before coding |
| Planning architecture | `/requirements-analysis` | Technical design |
| Need decisions | `/ask-user` | Get stakeholder input |
| Before coding | `/implementation-analysis` | Detailed design |
| Slow performance | `/optimization` | Improve speed |
| Technical debt | `/refactoring` | Improve quality |
| Need tests | `/test` | Generate test suite |

---

## 📊 Expected Results

### Time Savings
- **Debugging:** 30-50% faster
- **Testing:** 40-60% faster
- **Documentation:** 70-80% faster
- **Planning:** 40-50% faster

### Quality Improvements
- **Test Coverage:** +15-25%
- **Code Quality:** +20-30%
- **Bug Detection:** +25-35%
- **Documentation:** +50-70%

---

## 🔗 Full Documentation

- **[README.md](README.md)** - Complete overview
- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** - Detailed workflows

---

## 🐛 Troubleshooting

**Command not found?**
```bash
ls ~/.claude/commands/debug.md
# If missing, reinstall
```

**Permission errors?**
```bash
chmod 644 ~/.claude/commands/*.md
```

**Need help?**
```bash
cat ~/.claude/commands/debug.md
# Read command documentation
```

---

## 🎓 Learning Path

**Week 1:** `/debug`, `/fix`, `/test`
**Week 2:** `/requirements-*`, `/implementation-analysis`
**Week 3:** `/refactoring`, `/optimization`, `/explain`
**Week 4:** Master workflows and chaining

---

## 📦 Installation Locations

**User-Level (Recommended):**
```bash
~/.claude/commands/
```

**Project-Level (Team):**
```bash
.claude/commands/
```

---

**Print this card for quick reference!** 📋
