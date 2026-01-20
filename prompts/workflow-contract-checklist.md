# Workflow Contract Self-Check (Rule #2 Enforcement)

**Purpose**: Ensure Claude always routes code/UX tasks to appropriate AI backends.

---

## 🔍 Pre-Action Checklist (Before ANY code/UX modification)

Claude MUST verify these questions before acting:

### 1. Task Classification
- [ ] Is this a **code task**? (implementation, refactoring, testing, bug fix)
- [ ] Is this a **UX task**? (design, styling, wireframes, components)
- [ ] Is this a **config/docs task**? (package.json, README, .env)

### 2. Routing Decision
```
IF code task:
  → ROUTE to /code-with-codex
  → DO NOT use Edit/Write/NotebookEdit directly

ELSE IF UX task:
  → ROUTE to /ux-design-gemini
  → DO NOT use Edit/Write directly

ELSE (config/docs):
  → ALLOW direct Edit/Write
```

### 3. Violation Detection
If Claude catches itself about to violate Rule #2:
1. **STOP immediately**
2. **Self-correct**: "⚠️ Workflow Contract violation detected. Routing to [skill name]..."
3. **Execute correct skill**

---

## 📋 Task Type Decision Tree

```
User Request
    ↓
┌────────────────────────────┐
│ Does it involve code?      │
│ (.js, .py, .ts, etc.)     │
└────────────────────────────┘
    ↓ YES              ↓ NO
┌─────────────┐   ┌──────────────────┐
│/code-with-  │   │ Does it involve  │
│ codex       │   │ UX/styling?      │
└─────────────┘   └──────────────────┘
                    ↓ YES        ↓ NO
                ┌──────────┐  ┌────────┐
                │/ux-design│  │Direct  │
                │ -gemini  │  │Edit/   │
                └──────────┘  │Write OK│
                              └────────┘
```

---

## 🚨 Common Violations to Watch For

| Violation | Trigger | Correct Action |
|-----------|---------|----------------|
| Direct `.js` edit | User: "Fix this bug in app.js" | Route to `/code-with-codex` |
| Direct `.css` edit | User: "Make the button blue" | Route to `/ux-design-gemini` |
| Direct test write | User: "Add unit tests" | Route to `/code-with-codex` |
| Direct HTML edit | User: "Change the layout" | Route to `/ux-design-gemini` |
| Inline code in response | Showing code snippet | OK (read-only), but implementation → skill |

---

## ✅ Allowed Direct Operations

These operations DO NOT require skill routing:

- **Reading files** (Read, Glob, Grep)
- **Running tests** (Bash for `pytest`, `npm test`)
- **Git operations** (Bash for git commands)
- **Config file edits** (.gitignore, package.json metadata)
- **Documentation** (README.md, CHANGELOG.md)
- **Analysis/reporting** (generating reports, code review comments)

---

## 🔧 Hook Integration

### Automatic Enforcement
- Pre-tool-use hook (`pre-tool-use.ps1`) intercepts Edit/Write
- Blocks code/UX file edits automatically
- Displays violation message and suggested skill

### Manual Verification
Before each code/UX edit, Claude should mentally check:
```
Am I about to use Edit/Write on a code/UX file?
  → YES: Stop and route to skill
  → NO: Proceed
```

---

## 📊 Compliance Metrics

Track adherence over time:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Skill routing rate | 100% | All code/UX tasks use skills |
| Direct edit violations | 0 | No blocked hook executions |
| Self-correction rate | 100% | Catch violations before execution |

---

## 🎯 Examples

### ✅ Correct Routing

**Example 1: Code Task**
```
User: "Add error handling to the API client"
Claude: "I'll use /code-with-codex to implement error handling."
→ Calls Skill tool with skill="code-with-codex"
```

**Example 2: UX Task**
```
User: "Make the dashboard more modern"
Claude: "I'll use /ux-design-gemini to redesign the dashboard."
→ Calls Skill tool with skill="ux-design-gemini"
```

**Example 3: Config Task**
```
User: "Add tmpclaude-* to .gitignore"
Claude: "I'll directly edit .gitignore."
→ Calls Edit tool (allowed for config files)
```

### ❌ Violations (to be prevented)

**Example 1: Direct Code Edit**
```
❌ User: "Fix the login bug"
❌ Claude: Uses Edit on login.js directly
✅ Correct: Route to /code-with-codex
```

**Example 2: Direct Styling Edit**
```
❌ User: "Change button color to blue"
❌ Claude: Uses Edit on styles.css directly
✅ Correct: Route to /ux-design-gemini
```

---

## 🔄 Continuous Improvement

1. **Review violations** after each session
2. **Update decision tree** if new edge cases emerge
3. **Strengthen hook** to catch more patterns
4. **Educate user** on when to use skills directly

---

## 📞 Emergency Override

**When to use direct tools** (requires user permission):

1. Skill server is down (after 2 retry attempts)
2. Critical production hotfix (time-sensitive)
3. User explicitly requests "bypass workflow contract"

**Process**:
1. Attempt skill routing
2. If fails 2x, ask user: "Skill unavailable. Use direct tools?"
3. Only proceed with explicit user approval
