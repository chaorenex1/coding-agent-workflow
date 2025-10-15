# Claude AI Agent Framework - Copilot Instructions

## Project Overview
This is the BMAD (Business → Architecture → Development) AI agent orchestration framework. It coordinates specialized AI agents (PO, Architect, SM, Dev, QA, Review) through structured workflows to handle complete software development lifecycles.

## Architecture Pattern
- **Agent-Based**: Specialized agents in `agents/general_agent/` (e.g., `bmad-po.md`, `bmad-dev.md`)
- **Command Interface**: User commands in `commands/general_agent/` (e.g., `bmad-pilot.md`, `code.md`)  
- **Output Styling**: Presentation templates in `output-styles/general_agent/`
- **Workflow Orchestration**: The `bmad-orchestrator.md` coordinates multi-agent interactions

## Key Development Principles

### UltraThink Methodology
All agents follow systematic analysis: **Hypotheses → Evidence → Patterns → Synthesis → Validation**. When adding features, apply this cognitive framework to break down complex problems systematically.

### Quality Gates & Approval Flow
- **Interactive Phases**: PO, Architect, SM require 90+ quality scores AND explicit user approval  
- **Automated Phases**: Dev, QA execute autonomously with comprehensive reporting
- **Gate Pattern**: Each approval gate requires literal "yes" response to proceed
- Always implement approval gates for user-facing workflow changes

### Artifact Management
- Specs stored in `./.claude/specs/{feature_name}/` with canonical filenames:
  - `00-repo-scan.md` (repository analysis)
  - `01-product-requirements.md` (PRD after approval) 
  - `02-system-architecture.md` (architecture after approval)
  - `03-sprint-plan.md` (sprint plan after approval)
  - `04-dev-reviewed.md` (code review report)

## Agent Interaction Patterns

### Command Structure
Commands use markdown frontmatter with `name` and `description`. Follow the pattern:
```markdown
---
name: command-name
description: Brief description
---
```

### Agent Coordination
- **Orchestrator Manages Flow**: Never bypass the orchestrator for multi-agent workflows
- **Context Passing**: Always include repository scan and previous phase outputs
- **Iterative Refinement**: Agents can be called multiple times until quality thresholds met
- **Sequential Execution**: Dev → Review → QA with iteration limits (max 3 review cycles)

### Repository Awareness
Every agent receives repository context through `00-repo-scan.md`. When implementing new features:
1. Always perform repository scan first (unless `--skip-scan`)
2. Reference existing patterns and conventions
3. Maintain consistency with established codebase structure

## Development Standards

### Code Implementation (bmad-dev.md patterns)
- **Multi-Sprint Execution**: Implement ALL sprints sequentially, not just Sprint 1
- **Quality Requirements**: >80% test coverage, comprehensive error handling
- **Architecture Compliance**: Follow specifications exactly, no deviations
- **SOLID Principles**: Apply KISS, YAGNI, DRY throughout implementation

### Error Handling Pattern
```javascript
class AppError extends Error {
  constructor(message, statusCode, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
  }
}
```

### Testing Standards
- Unit tests alongside code for each sprint
- Integration tests for cross-component interactions  
- Test error scenarios comprehensively
- Validate sprint completion before proceeding

## Workflow Options
Standard options across commands:
- `--skip-tests`: Skip QA phase
- `--direct-dev`: Skip SM planning phase
- `--skip-scan`: Skip repository analysis (not recommended)

## Integration Points
- **External Tools**: Codex CLI integration for automated execution phases
- **File System**: Structured artifact storage in `./.claude/specs/`
- **Git Integration**: Repository-aware scanning and pattern detection
- **Environment Config**: Support for development/staging/production configurations

## Debugging & Troubleshooting
- Check `./.claude/specs/{feature_name}/` for workflow artifacts
- Verify quality scores in agent outputs (should be 90+)
- Ensure approval gates completed before phase transitions
- Repository scan provides context for all subsequent phases

When extending this framework, maintain the agent specialization pattern and always implement proper approval gates for user-facing changes.