# BMAD Workflow Quick Start Guide

## 5-Minute Quick Start

### 1. Install (30 seconds)

```bash
# Copy commands and agents
mkdir -p ~/.claude/commands ~/.claude/agents
cp generated-commands/bmad-workflow/bmad-*.md ~/.claude/commands/
cp .claude/agents/bmad-*.md ~/.claude/agents/
```

### 2. Start New Project (4 minutes)

```bash
# Create project directory
mkdir my-saas-app && cd my-saas-app
git init

# Initialize docs structure
mkdir -p docs/bmad

# Start BMAD workflow
# In Claude Code:
```

### 3. Run First Phase

```
/bmad-analyze "An AI-powered task management SaaS for remote teams with real-time collaboration"
```

This creates:
- `docs/bmad/project-brief.md`
- `docs/bmad/market-analysis.md`

---

## Complete Workflow Example

### Phase 1: Analysis

```
/bmad-analyze "AI-powered task management SaaS for remote teams"
```

**Output:**
- Market research with competitor analysis
- Target user personas
- Project brief with success criteria

### Phase 2: Planning

```
/bmad-plan
```

**Output:**
- Complete PRD with features
- User stories with acceptance criteria
- Epic structure and dependencies

### Phase 3: Architecture

```
/bmad-architect
```

**Output:**
- Technology stack selection
- System architecture diagram
- Database schema
- API design
- Tech spec document

### Phase 4: Development

```
/bmad-develop epic-001/story-001
```

**Output:**
- Detailed story file
- Tests written first (TDD)
- Implementation code
- Commits with conventional messages

### Phase 5: Testing

```
/bmad-test
```

**Output:**
- All test suites executed
- Acceptance criteria verified
- Code review completed
- Test report generated

### Phase 6: Deployment

```
/bmad-deploy staging
```

**Output:**
- Pre-deployment checks
- Deployment to staging
- Health verification
- Deployment log

```
/bmad-deploy production
```

**Output:**
- Production deployment
- Monitoring setup
- Rollback plan documented

---

## Common Workflows

### New Product (Full Cycle)

```
/bmad-analyze "Product idea"
/bmad-plan
/bmad-architect
/bmad-develop epic-001/story-001
/bmad-develop epic-001/story-002
...
/bmad-test
/bmad-deploy staging
/bmad-test  # Staging validation
/bmad-deploy production
```

### New Feature (Existing Product)

```
/bmad-plan "New feature description"
/bmad-architect "Focus on new feature"
/bmad-develop epic-xxx/story-xxx
/bmad-test "epic-xxx"
/bmad-deploy staging
```

### Bug Fix (Quick)

```
# Skip planning phases
/bmad-develop "Fix: description of bug"
/bmad-test
/bmad-deploy staging
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BMAD WORKFLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │ ANALYZE  │───▶│  PLAN    │───▶│ ARCHITECT│                  │
│  │ Phase 1  │    │ Phase 2  │    │ Phase 3  │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
│       │              │              │                           │
│       ▼              ▼              ▼                           │
│  project-brief   prd.md        architecture.md                  │
│  market-analysis user-stories  tech-spec.md                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    DEVELOP Phase 4                        │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │  │
│  │  │ Story 1 │─▶│ Story 2 │─▶│ Story 3 │─▶│ Story N │      │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │   TEST   │◀──│   (fix)  │    │  DEPLOY  │                  │
│  │ Phase 5  │    │          │───▶│ Phase 6  │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
│       │              ▲              │                           │
│       │              │              ▼                           │
│       └──────────────┘         Production! 🚀                   │
│        (if tests fail)                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Roles Summary

| Agent | When Active | What It Does |
|-------|-------------|--------------|
| **Analyst** | Phase 1 | Research, validate concept |
| **Product Owner** | Phase 2 | Write PRD, user stories |
| **Architect** | Phase 3 | Design system architecture |
| **Scrum Master** | Phase 4 | Manage stories, coordinate |
| **Fullstack Dev** | Phase 4 | Write code, tests |
| **QA** | Phase 5 | Test, review, validate |
| **DevOps** | Phase 6 | Deploy, monitor |

---

## Tips for Solo Developers

### 1. Trust the Process
Each phase builds on the previous. Don't skip phases.

### 2. Commit After Each Story
Small, frequent commits make rollbacks easy.

### 3. Use TDD
Write tests first. It catches bugs early.

### 4. Review Artifacts
Read generated docs. They're your project memory.

### 5. Iterate
Don't try to be perfect first time. Ship MVP, then improve.

---

## Getting Help

### See All Commands
```
/help
```

### Read Workflow Overview
```
cat generated-commands/bmad-workflow/WORKFLOW_OVERVIEW.md
```

### Check Agent Capabilities
```
cat ~/.claude/agents/bmad-analyst.md
```

---

## Next Steps

1. ✅ Install commands and agents
2. ✅ Create new project directory
3. ✅ Run `/bmad-analyze` with your idea
4. ⬜ Follow the workflow through all phases
5. ⬜ Deploy your MVP!

**Happy Building!** 🚀

---

## Resources

- [BMAD-METHOD GitHub](https://github.com/bmad-code-org/BMAD-METHOD)
- [Applied BMAD Guide](https://bennycheung.github.io/bmad-reclaiming-control-in-ai-dev)
- [BMAD Overview Article](https://nayakpplaban.medium.com/bmad-ai-powered-agile-framework-overview-238d4af39aa4)
