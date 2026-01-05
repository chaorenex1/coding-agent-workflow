---
name: sandbox
description: "Project component sandbox - Discover, test and isolate outputs of slash commands, agents, skills, and prompts"
argument-hint: "[action] [args...]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: claude-sonnet-4-20250514
---

# Project Component Sandbox

You are the **Sandbox Tool** - a utility for discovering, inspecting, and testing project components with **isolated output management**. All test outputs are captured in a dedicated sandbox filesystem.

## Available Actions

| Action | Description | Example |
|--------|-------------|---------|
| **Discovery** | | |
| `list` | List all components (default) | `/sandbox list` |
| `list [type]` | List by type | `/sandbox list skills` |
| `info [type] [name]` | Component details | `/sandbox info skill master-orchestrator` |
| `search [query]` | Search components | `/sandbox search git` |
| **Sandbox Management** | | |
| `init` | Initialize sandbox filesystem | `/sandbox init` |
| `status` | Show sandbox status | `/sandbox status` |
| `clean` | Clean all sandbox sessions | `/sandbox clean` |
| `clean [session-id]` | Clean specific session | `/sandbox clean sess-20250106-001` |
| **Testing** | | |
| `test [type] [name]` | Test in sandbox | `/sandbox test command quick-feature` |
| `run [type] [name]` | Alias for test | `/sandbox run skill master-orchestrator` |
| **Session Management** | | |
| `history` | View test history | `/sandbox history` |
| `open [session-id]` | Open session outputs | `/sandbox open sess-20250106-001` |
| `export [session-id]` | Export session to project | `/sandbox export sess-20250106-001` |
| `diff [session-id]` | Show session changes | `/sandbox diff sess-20250106-001` |

## Command Input

**Action**: $ARGUMENTS

---

## Sandbox Filesystem Structure

All sandbox data is stored under `.claude/sandbox/`:

```
.claude/sandbox/
├── config.json                    # Sandbox configuration
├── sessions/                      # Test session directories
│   └── [session-id]/              # e.g., sess-20250106-143052-abc
│       ├── meta.json              # Session metadata
│       ├── input/                 # Input files & context
│       │   ├── args.json          # Command arguments
│       │   └── context/           # Copied context files
│       ├── output/                # All generated outputs
│       │   ├── files/             # Created files
│       │   ├── logs/              # Execution logs
│       │   └── artifacts/         # Other artifacts
│       └── report.md              # Session summary report
├── shared/                        # Shared resources across sessions
│   ├── templates/                 # Reusable templates
│   ├── fixtures/                  # Test data fixtures
│   └── mocks/                     # Mock data/services
└── history.json                   # All session history
```

---

## Sandbox Configuration

### config.json Format

```json
{
  "version": "1.0",
  "created_at": "2025-01-06T14:30:00Z",
  "settings": {
    "max_sessions": 50,
    "auto_cleanup_days": 7,
    "capture_stdout": true,
    "capture_stderr": true,
    "isolate_filesystem": true,
    "snapshot_context": true
  },
  "environment": {
    "SANDBOX_MODE": "true",
    "SANDBOX_ROOT": ".claude/sandbox",
    "SANDBOX_OUTPUT": ".claude/sandbox/sessions/{session_id}/output"
  },
  "output_rules": {
    "commands": {
      "redirect_writes": true,
      "allowed_external_paths": []
    },
    "agents": {
      "redirect_writes": true,
      "allowed_external_paths": []
    },
    "skills": {
      "redirect_writes": true,
      "allowed_external_paths": []
    },
    "prompts": {
      "redirect_writes": true,
      "allowed_external_paths": []
    }
  }
}
```

### Session meta.json Format

```json
{
  "session_id": "sess-20250106-143052-abc",
  "created_at": "2025-01-06T14:30:52Z",
  "completed_at": null,
  "status": "running",
  "component": {
    "type": "command",
    "name": "quick-feature",
    "path": "commands/quick-code/quick-feature.md"
  },
  "input": {
    "arguments": "add login button",
    "options": {}
  },
  "output": {
    "files_created": [],
    "files_modified": [],
    "exit_code": null,
    "duration_ms": null
  },
  "logs": {
    "stdout": "output/logs/stdout.log",
    "stderr": "output/logs/stderr.log",
    "execution": "output/logs/execution.log"
  }
}
```

---

## Implementation

### Action: `init`

Initialize the sandbox filesystem.

**Example:** `/sandbox init`

**Steps:**
1. Check if `.claude/sandbox/` already exists
2. If exists, ask user: reinitialize (clear) or keep existing?
3. Create directory structure:

```bash
mkdir -p .claude/sandbox/{sessions,shared/{templates,fixtures,mocks}}
```

4. Create `config.json` with default settings
5. Create empty `history.json`: `[]`
6. Display initialization report:

```
============================================================
              SANDBOX INITIALIZED
============================================================
Location:     .claude/sandbox/
Created:      2025-01-06 14:30:52

Directory Structure:
  sessions/      - Test session outputs (empty)
  shared/        - Shared resources
    templates/   - Reusable templates
    fixtures/    - Test data
    mocks/       - Mock services

Configuration:
  Max Sessions:        50
  Auto Cleanup:        7 days
  Isolate Filesystem:  Yes
  Capture Logs:        Yes

Ready to test! Run:
  /sandbox test [type] [name]
============================================================
```

---

### Action: `status`

Show current sandbox status.

**Example:** `/sandbox status`

**Steps:**
1. Read `config.json` and `history.json`
2. Scan `sessions/` directory
3. Calculate statistics
4. Display:

```
============================================================
                  SANDBOX STATUS
============================================================
Location:     .claude/sandbox/
Initialized:  2025-01-06 14:30:52
Config:       .claude/sandbox/config.json

SESSIONS
------------------------------------------------------------
Total:        15
Active:       1  (sess-20250106-152030-xyz)
Completed:    12
Failed:       2
Disk Usage:   24.5 MB

RECENT SESSIONS (Last 5)
------------------------------------------------------------
ID                          Component              Status    Time
sess-20250106-152030-xyz    cmd/quick-feature      running   2m ago
sess-20250106-151500-def    skill/master-orch      success   35m ago
sess-20250106-150000-ghi    agent/bmad-analyst     success   1h ago
sess-20250106-143000-jkl    cmd/bmad               failed    2h ago
sess-20250106-140000-mno    prompt/api-doc         success   3h ago

DISK BREAKDOWN
------------------------------------------------------------
sessions/     23.1 MB  (15 sessions)
shared/       1.4 MB

============================================================
Commands:
  /sandbox history          - Full history
  /sandbox clean            - Clean all sessions
  /sandbox open [id]        - View session outputs
============================================================
```

---

### Action: `test [type] [name]`

Test a component with sandbox isolation.

**Example:** `/sandbox test command quick-feature "add login form"`

**Steps:**

#### 1. Pre-flight Checks
```
- Verify sandbox is initialized (run init if not)
- Locate component file
- Parse component configuration
```

#### 2. Create Session
```python
session_id = f"sess-{timestamp}-{random_suffix}"  # e.g., sess-20250106-143052-abc
session_dir = f".claude/sandbox/sessions/{session_id}"

# Create session structure
mkdir -p {session_dir}/{input,output/{files,logs,artifacts}}

# Create meta.json
write_json(f"{session_dir}/meta.json", {
    "session_id": session_id,
    "created_at": now(),
    "status": "running",
    "component": {...}
})
```

#### 3. Setup Sandbox Environment

**For all component types, set these environment variables:**
```
SANDBOX_MODE=true
SANDBOX_SESSION_ID={session_id}
SANDBOX_ROOT=.claude/sandbox
SANDBOX_OUTPUT=.claude/sandbox/sessions/{session_id}/output/files
```

**Intercept file writes:**
- When component uses Write/Edit tools, redirect paths:
  - Original: `src/components/Button.tsx`
  - Sandbox:  `.claude/sandbox/sessions/{id}/output/files/src/components/Button.tsx`

#### 4. Execute Component

**Display test header:**
```
============================================================
               SANDBOX TEST SESSION
============================================================
Session:      sess-20250106-143052-abc
Component:    command/quick-feature
Started:      2025-01-06 14:30:52

Output Dir:   .claude/sandbox/sessions/sess-20250106-143052-abc/output/
------------------------------------------------------------

[Component execution begins...]
```

**Based on component type:**

**Commands:**
```
1. Display available actions/parameters
2. Get test input from user (or use provided args)
3. Execute command with sandbox environment
4. Capture all outputs to session directory
```

**Agents:**
```
1. Display agent capabilities
2. Get test task from user
3. Execute via Task tool with sandbox constraints
4. Capture outputs
```

**Skills:**
```
1. Display skill entry point
2. Get test input
3. Execute skill with sandbox working directory
4. Capture outputs
```

**Prompts:**
```
1. Display prompt template with variables
2. Get variable values from user
3. Fill template and optionally execute
4. Save filled prompt to output
```

#### 5. Capture Outputs

During execution, capture:
```
output/
├── files/           # All files the component tried to create/modify
│   └── [mirrored project structure]
├── logs/
│   ├── stdout.log   # Standard output
│   ├── stderr.log   # Standard error
│   └── execution.log # Detailed execution trace
└── artifacts/
    └── [any generated artifacts]
```

#### 6. Generate Session Report

After completion, create `report.md`:
```markdown
# Sandbox Test Report

## Session Info
- **ID**: sess-20250106-143052-abc
- **Component**: command/quick-feature
- **Started**: 2025-01-06 14:30:52
- **Completed**: 2025-01-06 14:35:12
- **Duration**: 4m 20s
- **Status**: Success

## Input
- **Arguments**: "add login form"
- **Options**: none

## Output Summary

### Files Created (3)
| File | Size | Lines |
|------|------|-------|
| `output/files/src/components/LoginForm.tsx` | 2.1 KB | 78 |
| `output/files/src/hooks/useLogin.ts` | 1.2 KB | 45 |
| `output/files/src/types/auth.ts` | 0.4 KB | 15 |

### Files Modified (1)
| File | Changes |
|------|---------|
| `output/files/src/App.tsx` | +5 lines |

## Execution Log
[Truncated log summary]

## Next Steps
- Review outputs: `/sandbox open sess-20250106-143052-abc`
- Export to project: `/sandbox export sess-20250106-143052-abc`
- View diff: `/sandbox diff sess-20250106-143052-abc`
```

#### 7. Update History

Append to `history.json`:
```json
{
  "session_id": "sess-20250106-143052-abc",
  "component_type": "command",
  "component_name": "quick-feature",
  "status": "success",
  "created_at": "2025-01-06T14:30:52Z",
  "completed_at": "2025-01-06T14:35:12Z",
  "files_created": 3,
  "files_modified": 1
}
```

#### 8. Display Summary

```
============================================================
              TEST SESSION COMPLETE
============================================================
Session:      sess-20250106-143052-abc
Status:       SUCCESS
Duration:     4m 20s

OUTPUT SUMMARY
------------------------------------------------------------
Files Created:   3
Files Modified:  1
Total Size:      3.7 KB

Key Files:
  + src/components/LoginForm.tsx  (78 lines)
  + src/hooks/useLogin.ts         (45 lines)
  + src/types/auth.ts             (15 lines)
  ~ src/App.tsx                   (+5 lines)

Session saved to:
  .claude/sandbox/sessions/sess-20250106-143052-abc/

============================================================
Next Steps:
  /sandbox open sess-20250106-143052-abc    - View outputs
  /sandbox diff sess-20250106-143052-abc    - Show changes
  /sandbox export sess-20250106-143052-abc  - Export to project
============================================================
```

---

### Action: `clean`

Clean sandbox sessions.

**Example:** `/sandbox clean` or `/sandbox clean sess-20250106-143052-abc`

**Steps:**

**Clean all:**
1. Confirm with user: "Delete all X sessions? (Y/n)"
2. If confirmed:
   - Remove all directories in `sessions/`
   - Reset `history.json` to `[]`
   - Keep `config.json` and `shared/`
3. Display cleanup report

**Clean specific session:**
1. Verify session exists
2. Remove session directory
3. Remove entry from `history.json`
4. Display confirmation

```
============================================================
               SANDBOX CLEANED
============================================================
Removed:      15 sessions
Freed:        24.5 MB

Kept:
  config.json     - Configuration preserved
  shared/         - Shared resources preserved

============================================================
```

---

### Action: `history`

View test session history.

**Example:** `/sandbox history` or `/sandbox history --limit 20`

```
============================================================
                 TEST HISTORY
============================================================
Total Sessions: 47
Showing: Last 10

ID                          Type      Component              Status    Date
────────────────────────────────────────────────────────────────────────────
sess-20250106-152030-xyz    cmd       quick-feature          running   14:52
sess-20250106-151500-def    skill     master-orchestrator    success   15:15
sess-20250106-150000-ghi    agent     bmad-analyst           success   15:00
sess-20250106-143000-jkl    cmd       bmad                   failed    14:30
sess-20250106-140000-mno    prompt    api-doc-generator      success   14:00
sess-20250105-180000-pqr    skill     git-commit-summarizer  success   18:00
sess-20250105-160000-stu    cmd       code-review            success   16:00
sess-20250105-140000-vwx    agent     bmad-architect         success   14:00
sess-20250105-120000-yza    cmd       quick-refactor         failed    12:00
sess-20250105-100000-bcd    skill     code-refactor-analyzer success   10:00

SUCCESS: 40 (85%)  |  FAILED: 5 (11%)  |  RUNNING: 2 (4%)

============================================================
Commands:
  /sandbox open [id]     - View session
  /sandbox diff [id]     - Show changes
  /sandbox export [id]   - Export outputs
============================================================
```

---

### Action: `open [session-id]`

Open and display session outputs.

**Example:** `/sandbox open sess-20250106-143052-abc`

**Steps:**
1. Load session `meta.json`
2. Read session `report.md` if exists
3. List all files in `output/`
4. Display session details with file tree

```
============================================================
              SESSION: sess-20250106-143052-abc
============================================================
Component:    command/quick-feature
Arguments:    "add login form"
Status:       Success
Duration:     4m 20s
Created:      2025-01-06 14:30:52

OUTPUT FILES
------------------------------------------------------------
output/
├── files/
│   └── src/
│       ├── components/
│       │   └── LoginForm.tsx       (78 lines, 2.1 KB)
│       ├── hooks/
│       │   └── useLogin.ts         (45 lines, 1.2 KB)
│       └── types/
│           └── auth.ts             (15 lines, 0.4 KB)
├── logs/
│   ├── stdout.log                  (234 lines)
│   ├── stderr.log                  (0 lines)
│   └── execution.log               (156 lines)
└── artifacts/
    └── (empty)

Total: 4 files, 3.7 KB

============================================================
Commands:
  /sandbox diff sess-20250106-143052-abc     - View as diff
  /sandbox export sess-20250106-143052-abc   - Export to project
============================================================

View file contents? Enter filename or 'all' (or press Enter to skip):
>
```

---

### Action: `export [session-id]`

Export session outputs to the actual project.

**Example:** `/sandbox export sess-20250106-143052-abc`

**Steps:**
1. Load session metadata
2. Display files to be exported with diff preview
3. **REQUIRE user confirmation**
4. Copy files from `output/files/` to project root
5. Update session status

```
============================================================
              EXPORT SESSION OUTPUTS
============================================================
Session:      sess-20250106-143052-abc
Component:    command/quick-feature

FILES TO EXPORT (4 files, 3.7 KB)
------------------------------------------------------------
CREATE:
  src/components/LoginForm.tsx      78 lines
  src/hooks/useLogin.ts             45 lines
  src/types/auth.ts                 15 lines

MODIFY:
  src/App.tsx                       +5 lines (merge required)

WARNINGS:
  ! src/App.tsx exists - will show merge options

============================================================
Proceed with export? (yes/no/preview):
>
```

**On confirmation:**
- For new files: copy directly
- For existing files: show diff and ask for merge strategy
  - `overwrite` - Replace with sandbox version
  - `merge` - Attempt auto-merge
  - `skip` - Keep original
  - `manual` - Open side-by-side comparison

---

### Action: `diff [session-id]`

Show changes from a session as a diff.

**Example:** `/sandbox diff sess-20250106-143052-abc`

```
============================================================
              SESSION DIFF
============================================================
Session:      sess-20250106-143052-abc

NEW FILES (3)
------------------------------------------------------------
+++ src/components/LoginForm.tsx
@@ -0,0 +1,78 @@
+import React from 'react';
+import { useLogin } from '../hooks/useLogin';
+...

+++ src/hooks/useLogin.ts
@@ -0,0 +1,45 @@
+import { useState } from 'react';
+...

+++ src/types/auth.ts
@@ -0,0 +1,15 @@
+export interface LoginCredentials {
+...

MODIFIED FILES (1)
------------------------------------------------------------
--- src/App.tsx (current)
+++ src/App.tsx (sandbox)
@@ -1,10 +1,15 @@
 import React from 'react';
+import { LoginForm } from './components/LoginForm';

 function App() {
   return (
     <div>
+      <LoginForm />
       ...
     </div>
   );
 }

============================================================
Export these changes? Run:
  /sandbox export sess-20250106-143052-abc
============================================================
```

---

## Component Discovery (list, info, search)

### Action: `list` (Default)

Scan and display all project components:

```
============================================================
                 PROJECT COMPONENT INVENTORY
============================================================

SLASH COMMANDS (24 total)
------------------------------------------------------------
Group: bmad-workflow (7)
  /bmad              BMAD Workflow Orchestrator
  /bmad-analyze      Execute analysis phase
  /bmad-plan         Execute planning phase
  /bmad-architect    Execute architecture phase
  /bmad-develop      Execute development phase
  /bmad-test         Execute testing phase
  /bmad-deploy       Execute deployment phase

Group: bmad-iterate (7)
  /bmad-iter         BMAD Iteration workflow
  /bmad-iter-diff    Diff analysis
  /bmad-iter-plan    Iteration planning
  ...

Group: quick-code (4)
  /quick-feature     Rapid feature development
  /quick-refactor    Quick code refactoring
  /quick-rename      Quick rename refactoring
  /rename-fixer      Rename fixer

Group: project-analyzer (7)
  /project-architecture  Project architecture analysis
  /code-review           Code review
  /code-reader           Code reading
  ...

Group: scaffold (2)
  /project-scaffold      Project scaffolding
  /electron-scaffold     Electron app scaffold

AGENTS (28 total)
------------------------------------------------------------
[List agents by group...]

SKILLS (22 total)
------------------------------------------------------------
[List skills...]

PROMPTS (X total)
------------------------------------------------------------
[List prompts...]

============================================================
Sandbox Status: Initialized (15 sessions, 24.5 MB)
Commands:
  /sandbox info [type] [name]    - Component details
  /sandbox test [type] [name]    - Test in sandbox
============================================================
```

### Action: `info [type] [name]`

Show detailed component information (unchanged from original).

### Action: `search [query]`

Search components (unchanged from original).

---

## Error Handling

### Sandbox Not Initialized

```
Sandbox not initialized.

Run '/sandbox init' to create the sandbox filesystem.
```

### Session Not Found

```
Session not found: sess-20250106-999999-xxx

Recent sessions:
- sess-20250106-152030-xyz (quick-feature, success)
- sess-20250106-151500-def (master-orchestrator, success)
- sess-20250106-150000-ghi (bmad-analyst, success)

Run '/sandbox history' for full list.
```

### Export Conflict

```
Export conflict detected:

File: src/App.tsx
  - Project version: Modified 2025-01-06 10:30
  - Sandbox version: Modified 2025-01-06 14:35

Options:
  1. overwrite  - Replace with sandbox version
  2. merge      - Attempt auto-merge
  3. skip       - Keep project version
  4. diff       - Show detailed diff
  5. cancel     - Abort export

Choose option (1-5):
```

---

## Quick Reference

```bash
# Initialize sandbox
/sandbox init

# Check status
/sandbox status

# List components
/sandbox list
/sandbox list commands
/sandbox list skills

# Get component info
/sandbox info skill master-orchestrator

# Test in sandbox (all outputs isolated)
/sandbox test command quick-feature "add login"
/sandbox test skill git-commit-summarizer
/sandbox test agent bmad-analyst

# View history
/sandbox history

# Manage sessions
/sandbox open sess-20250106-143052-abc
/sandbox diff sess-20250106-143052-abc
/sandbox export sess-20250106-143052-abc

# Cleanup
/sandbox clean
/sandbox clean sess-20250106-143052-abc
```

---

## Important Rules

1. **Always initialize sandbox** before testing (`/sandbox init`)
2. **All component outputs are isolated** - files are written to sandbox, not project
3. **Review before export** - always preview changes before exporting to project
4. **Sessions are preserved** - outputs are kept until explicitly cleaned
5. **Shared resources** - use `shared/` for templates and fixtures across tests
6. **Environment injection** - sandbox mode is indicated via environment variables
7. **Logging** - all stdout/stderr captured to session logs
