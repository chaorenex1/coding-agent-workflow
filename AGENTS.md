# AGENTS.md

**Project**: coding_base
**Purpose**: coding_base project
**Type**: GREENFIELD_NEW
**Codex CLI Compatibility**: Full support with reference-based architecture

---

## Quick Reference

This project is a **Claude Code project** that can be used with **Codex CLI**.

**Project Statistics**:
- **Skills**: 16 total (12 functional, 4 prompt-based)
- **Agents**: 11 total
- **Documentation**: ❌ No

**For Codex CLI Users**:
- Skills are documented below with Codex CLI usage examples
- Use `codex exec` commands (never plain `codex`)
- Python scripts can be executed directly
- All file references are relative to project root

---

## Project Overview

coding_base project

**Project Type**: GREENFIELD_NEW
**Root Directory**: `coding_base/`

---

## Available Skills

This project includes **16 skills** that can be used with Codex CLI.

### Functional Skills (12)

These skills have Python scripts that can be executed directly:

#### agent-factory

**Description**: Claude Code agent generation system that creates custom agents and sub-agents with enhanced YAML frontmatter, tool access patterns, and MCP integra...

**Location**: `C:\Users\zarag\.claude\skills\agent-factory/`
**Documentation**: [C:\Users\zarag\.claude\skills\agent-factory/SKILL.md](C:\Users\zarag\.claude\skills\agent-factory\SKILL.md)

**Python Scripts**:
- [agent_generator.py](C:\Users\zarag\.claude\skills\agent-factory\agent_generator.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\agent-factory
python agent_generator.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the agent-factory skill documentation at
  C:\Users\zarag\.claude\skills\agent-factory\SKILL.md, help me with [task]"
```

#### api-document-generator

**Description**: Parses interface/API information from files or directories and generates OpenAPI-compliant documentation with timestamps

**Location**: `C:\Users\zarag\.claude\skills\api-document-generator/`
**Documentation**: [C:\Users\zarag\.claude\skills\api-document-generator/SKILL.md](C:\Users\zarag\.claude\skills\api-document-generator\SKILL.md)

**Python Scripts**:
- [api_document_generator.py](C:\Users\zarag\.claude\skills\api-document-generator\api_document_generator.py)
- [api_parser.py](C:\Users\zarag\.claude\skills\api-document-generator\api_parser.py)
- [file_handler.py](C:\Users\zarag\.claude\skills\api-document-generator\file_handler.py)
- [openapi_generator.py](C:\Users\zarag\.claude\skills\api-document-generator\openapi_generator.py)
- [test_simple.py](C:\Users\zarag\.claude\skills\api-document-generator\test_simple.py)
- [test_skill.py](C:\Users\zarag\.claude\skills\api-document-generator\test_skill.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\api-document-generator
python api_document_generator.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the api-document-generator skill documentation at
  C:\Users\zarag\.claude\skills\api-document-generator\SKILL.md, help me with [task]"
```

#### code-refactor-analyzer

**Description**: Analyzes codebase for refactoring needs, generates todo reports, and validates completion

**Location**: `C:\Users\zarag\.claude\skills\code-refactor-analyzer/`
**Documentation**: [C:\Users\zarag\.claude\skills\code-refactor-analyzer/SKILL.md](C:\Users\zarag\.claude\skills\code-refactor-analyzer\SKILL.md)

**Python Scripts**:
- [code_analyzer.py](C:\Users\zarag\.claude\skills\code-refactor-analyzer\code_analyzer.py)
- [main.py](C:\Users\zarag\.claude\skills\code-refactor-analyzer\main.py)
- [report_manager.py](C:\Users\zarag\.claude\skills\code-refactor-analyzer\report_manager.py)
- [state_manager.py](C:\Users\zarag\.claude\skills\code-refactor-analyzer\state_manager.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\code-refactor-analyzer
python code_analyzer.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the code-refactor-analyzer skill documentation at
  C:\Users\zarag\.claude\skills\code-refactor-analyzer\SKILL.md, help me with [task]"
```

#### codex-cli-bridge

**Description**: Bridge between Claude Code and OpenAI Codex CLI - generates AGENTS.md from CLAUDE.md, provides Codex CLI execution helpers, and enables seamless in...

**Location**: `C:\Users\zarag\.claude\skills\codex-cli-bridge/`
**Documentation**: [C:\Users\zarag\.claude\skills\codex-cli-bridge/SKILL.md](C:\Users\zarag\.claude\skills\codex-cli-bridge\SKILL.md)

**Python Scripts**:
- [agents_md_generator.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\agents_md_generator.py)
- [bridge.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\bridge.py)
- [claude_parser.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\claude_parser.py)
- [codex_executor.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\codex_executor.py)
- [project_analyzer.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\project_analyzer.py)
- [safety_mechanism.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\safety_mechanism.py)
- [skill_documenter.py](C:\Users\zarag\.claude\skills\codex-cli-bridge\skill_documenter.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\codex-cli-bridge
python agents_md_generator.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the codex-cli-bridge skill documentation at
  C:\Users\zarag\.claude\skills\codex-cli-bridge\SKILL.md, help me with [task]"
```

#### git-code-review

**Description**: Get git records for specified users and days, perform code review for each commit, and generate detailed code review reports

**Location**: `C:\Users\zarag\.claude\skills\git-code-review/`
**Documentation**: [C:\Users\zarag\.claude\skills\git-code-review/SKILL.md](C:\Users\zarag\.claude\skills\git-code-review\SKILL.md)

**Python Scripts**:
- [git_code_review.py](C:\Users\zarag\.claude\skills\git-code-review\git_code_review.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\git-code-review
python git_code_review.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the git-code-review skill documentation at
  C:\Users\zarag\.claude\skills\git-code-review\SKILL.md, help me with [task]"
```

#### git-commit-summarizer

**Description**: Summarizes git commits for specified users over a given time period and generates markdown reports

**Location**: `C:\Users\zarag\.claude\skills\git-commit-summarizer/`
**Documentation**: [C:\Users\zarag\.claude\skills\git-commit-summarizer/SKILL.md](C:\Users\zarag\.claude\skills\git-commit-summarizer\SKILL.md)

**Python Scripts**:
- [git_commit_analyzer.py](C:\Users\zarag\.claude\skills\git-commit-summarizer\git_commit_analyzer.py)
- [report_generator.py](C:\Users\zarag\.claude\skills\git-commit-summarizer\report_generator.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\git-commit-summarizer
python git_commit_analyzer.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the git-commit-summarizer skill documentation at
  C:\Users\zarag\.claude\skills\git-commit-summarizer\SKILL.md, help me with [task]"
```

#### github-stars-analyzer

**Description**: Analyzes GitHub repository data to generate comprehensive research reports about stars, popularity trends, and comparative insights

**Location**: `C:\Users\zarag\.claude\skills\github-stars-analyzer/`
**Documentation**: [C:\Users\zarag\.claude\skills\github-stars-analyzer/SKILL.md](C:\Users\zarag\.claude\skills\github-stars-analyzer\SKILL.md)

**Python Scripts**:
- [analyze_repository.py](C:\Users\zarag\.claude\skills\github-stars-analyzer\analyze_repository.py)
- [generate_reports.py](C:\Users\zarag\.claude\skills\github-stars-analyzer\generate_reports.py)
- [github_api.py](C:\Users\zarag\.claude\skills\github-stars-analyzer\github_api.py)
- [visualize_data.py](C:\Users\zarag\.claude\skills\github-stars-analyzer\visualize_data.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\github-stars-analyzer
python analyze_repository.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the github-stars-analyzer skill documentation at
  C:\Users\zarag\.claude\skills\github-stars-analyzer\SKILL.md, help me with [task]"
```

#### hook-factory

**Description**: Generate production-ready Claude Code hooks with interactive Q&A, automated installation, and enhanced validation. Supports 10 templates across 7 e...

**Location**: `C:\Users\zarag\.claude\skills\hook-factory/`
**Documentation**: [C:\Users\zarag\.claude\skills\hook-factory/SKILL.md](C:\Users\zarag\.claude\skills\hook-factory\SKILL.md)

**Python Scripts**:
- [generator.py](C:\Users\zarag\.claude\skills\hook-factory\generator.py)
- [hook_factory.py](C:\Users\zarag\.claude\skills\hook-factory\hook_factory.py)
- [installer.py](C:\Users\zarag\.claude\skills\hook-factory\installer.py)
- [validator.py](C:\Users\zarag\.claude\skills\hook-factory\validator.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\hook-factory
python generator.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the hook-factory skill documentation at
  C:\Users\zarag\.claude\skills\hook-factory\SKILL.md, help me with [task]"
```

#### repo-analyzer

**Description**: Code repository analysis and technical documentation generation skill

**Location**: `C:\Users\zarag\.claude\skills\repo-analyzer/`
**Documentation**: [C:\Users\zarag\.claude\skills\repo-analyzer/SKILL.md](C:\Users\zarag\.claude\skills\repo-analyzer\SKILL.md)

**Python Scripts**:
- [repo_analyzer.py](C:\Users\zarag\.claude\skills\repo-analyzer\repo_analyzer.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\repo-analyzer
python repo_analyzer.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the repo-analyzer skill documentation at
  C:\Users\zarag\.claude\skills\repo-analyzer\SKILL.md, help me with [task]"
```

#### skill-validator

**Description**: Validates Claude skill files for correct structure, YAML frontmatter, Python imports, naming conventions, and compliance with official documentation

**Location**: `C:\Users\zarag\.claude\skills\skill-validator/`
**Documentation**: [C:\Users\zarag\.claude\skills\skill-validator/SKILL.md](C:\Users\zarag\.claude\skills\skill-validator\SKILL.md)

**Python Scripts**:
- [validate_naming.py](C:\Users\zarag\.claude\skills\skill-validator\validate_naming.py)
- [validate_python.py](C:\Users\zarag\.claude\skills\skill-validator\validate_python.py)
- [validate_skill.py](C:\Users\zarag\.claude\skills\skill-validator\validate_skill.py)
- [validate_yaml.py](C:\Users\zarag\.claude\skills\skill-validator\validate_yaml.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\skill-validator
python validate_naming.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the skill-validator skill documentation at
  C:\Users\zarag\.claude\skills\skill-validator\SKILL.md, help me with [task]"
```

#### slash-command-factory

**Description**: Generate custom Claude Code slash commands through intelligent 5-7 question flow. Creates powerful commands for business research, content analysis...

**Location**: `C:\Users\zarag\.claude\skills\slash-command-factory/`
**Documentation**: [C:\Users\zarag\.claude\skills\slash-command-factory/SKILL.md](C:\Users\zarag\.claude\skills\slash-command-factory\SKILL.md)

**Python Scripts**:
- [command_generator.py](C:\Users\zarag\.claude\skills\slash-command-factory\command_generator.py)
- [validator.py](C:\Users\zarag\.claude\skills\slash-command-factory\validator.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\slash-command-factory
python command_generator.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the slash-command-factory skill documentation at
  C:\Users\zarag\.claude\skills\slash-command-factory\SKILL.md, help me with [task]"
```

#### tech-stack-evaluator

**Description**: Comprehensive technology stack evaluation and comparison tool with TCO analysis, security assessment, and intelligent recommendations for engineeri...

**Location**: `C:\Users\zarag\.claude\skills\tech-stack-evaluator/`
**Documentation**: [C:\Users\zarag\.claude\skills\tech-stack-evaluator/SKILL.md](C:\Users\zarag\.claude\skills\tech-stack-evaluator\SKILL.md)

**Python Scripts**:
- [ecosystem_analyzer.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\ecosystem_analyzer.py)
- [format_detector.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\format_detector.py)
- [migration_analyzer.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\migration_analyzer.py)
- [report_generator.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\report_generator.py)
- [security_assessor.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\security_assessor.py)
- [stack_comparator.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\stack_comparator.py)
- [tco_calculator.py](C:\Users\zarag\.claude\skills\tech-stack-evaluator\tco_calculator.py)

**Using with Codex CLI**:

```bash
# Execute Python scripts directly
cd C:\Users\zarag\.claude\skills\tech-stack-evaluator
python ecosystem_analyzer.py --help  # See usage options

# Or reference in Codex prompt for guidance
codex exec -m gpt-5 -s read-only \
  "Using the tech-stack-evaluator skill documentation at
  C:\Users\zarag\.claude\skills\tech-stack-evaluator\SKILL.md, help me with [task]"
```

### Prompt-Based Skills (4)

These skills provide guidance through documentation:

#### codeagent

**Description**: Execute codeagent-wrapper for multi-backend AI code tasks. Supports Codex, Claude, and Gemini backends with file references (@syntax) and structure...

**Location**: `C:\Users\zarag\.claude\skills\codeagent/`
**Documentation**: [C:\Users\zarag\.claude\skills\codeagent/SKILL.md](C:\Users\zarag\.claude\skills\codeagent\SKILL.md)

**Using with Codex CLI**:

```bash
# Reference skill documentation in prompt
codex exec -m gpt-5 -s read-only \
  --skip-git-repo-check \
  "Using the codeagent skill documentation
  at C:\Users\zarag\.claude\skills\codeagent\SKILL.md,
  apply these guidelines to [your task]"
```

#### product-requirements

**Description**: Interactive Product Owner skill for requirements gathering, analysis, and PRD generation. Triggers when users request product requirements, feature...

**Location**: `C:\Users\zarag\.claude\skills\product-requirements/`
**Documentation**: [C:\Users\zarag\.claude\skills\product-requirements/SKILL.md](C:\Users\zarag\.claude\skills\product-requirements\SKILL.md)

**Using with Codex CLI**:

```bash
# Reference skill documentation in prompt
codex exec -m gpt-5 -s read-only \
  --skip-git-repo-check \
  "Using the product-requirements skill documentation
  at C:\Users\zarag\.claude\skills\product-requirements\SKILL.md,
  apply these guidelines to [your task]"
```

#### prompt-factory

**Description**: World-class prompt powerhouse that generates production-ready mega-prompts for any role, industry, and task through intelligent 7-question flow, 69...

**Location**: `C:\Users\zarag\.claude\skills\prompt-factory/`
**Documentation**: [C:\Users\zarag\.claude\skills\prompt-factory/SKILL.md](C:\Users\zarag\.claude\skills\prompt-factory\SKILL.md)

**Using with Codex CLI**:

```bash
# Reference skill documentation in prompt
codex exec -m gpt-5 -s read-only \
  --skip-git-repo-check \
  "Using the prompt-factory skill documentation
  at C:\Users\zarag\.claude\skills\prompt-factory\SKILL.md,
  apply these guidelines to [your task]"
```

#### prototype-prompt-generator

**Description**: This skill should be used when users need to generate detailed, structured prompts for creating UI/UX prototypes. Trigger when users request help w...

**Location**: `C:\Users\zarag\.claude\skills\prototype-prompt-generator/`
**Documentation**: [C:\Users\zarag\.claude\skills\prototype-prompt-generator/SKILL.md](C:\Users\zarag\.claude\skills\prototype-prompt-generator\SKILL.md)

**Using with Codex CLI**:

```bash
# Reference skill documentation in prompt
codex exec -m gpt-5 -s read-only \
  --skip-git-repo-check \
  "Using the prototype-prompt-generator skill documentation
  at C:\Users\zarag\.claude\skills\prototype-prompt-generator\SKILL.md,
  apply these guidelines to [your task]"
```

---

## Project Structure

```
coding_base/
├── AGENTS.md
├── CLAUDE.md
├── README.md
```

**Key Components**:
- `CLAUDE.md` - Claude Code configuration (source of truth)
- `AGENTS.md` - This file (Codex CLI bridge documentation)

---

## Workflow Patterns

Common Claude Code workflows and their Codex CLI equivalents:

### Generate New Skill

**Claude Code**:
```
User: "Create a skill for data visualization"
→ Skills Factory auto-activates
→ Generates complete skill package
```

**Codex CLI Equivalent**:
```bash
codex exec -m gpt-5 -s workspace-write --full-auto \
  --skip-git-repo-check \
  "Using the Skills Factory Prompt template, generate a
  data visualization skill with Python scripts for chart
  generation, interactive dashboards, and export functionality"
```

---

### Code Review

**Claude Code**: `/code-review`

**Codex CLI**:
```bash
codex exec -m gpt-5 -s read-only \
  --skip-git-repo-check \
  "Review this codebase for:
  - Code quality issues
  - Security vulnerabilities
  - Performance bottlenecks
  - Best practices violations
  Provide detailed report with file references"
```

---

### Run Tests

**Claude Code**: `/test`

**Codex CLI**:
```bash
codex exec -m gpt-5-codex -s workspace-write \
  --skip-git-repo-check \
  "Run all tests in this project and analyze any failures.
  Provide detailed failure reports with suggested fixes."
```

---

### Documentation Generation

**Claude Code**: `/docs-generate` or rr-tech-writer agent

**Codex CLI**:
```bash
codex exec -m gpt-5 -s workspace-write --full-auto \
  --skip-git-repo-check \
  "Generate comprehensive documentation for this project:
  - Update README.md with current features
  - Create API documentation
  - Update CHANGELOG.md with recent changes"
```

---

### Architecture Design

**Claude Code**: `/architect` or rr-architect agent

**Codex CLI**:
```bash
codex exec -m gpt-5 -s read-only \
  -c model_reasoning_effort=high \
  --skip-git-repo-check \
  "Analyze current architecture and propose:
  - System architecture diagram
  - Technology stack recommendations
  - Scalability improvements
  - Performance optimization strategies"
```

---

## Command Reference

| Operation | Claude Code | Codex CLI |
|-----------|-------------|-----------|
| Start session | `claude` | `codex` or `codex exec` |
| Resume session | `/resume-work` | `codex exec resume --last` |
| Code review | `/code-review` | `codex exec "review code"` |
| Run tests | `/test` | `codex exec "run tests"` |
| Generate docs | `/docs-generate` | `codex exec "generate docs"` |
| Plan feature | `/create-plan` | `codex exec -m gpt-5 "plan feature"` |
| Architecture | `/architect` | `codex exec -m gpt-5 -c model_reasoning_effort=high "design architecture"` |
| Build feature | `/implement` | `codex exec -m gpt-5-codex -s workspace-write "implement feature"` |

---

## Common Operations

### Execute Skill Python Script

**For functional skills with Python files**:

```bash
# Navigate to skill directory
cd generated-skills/skill-name/

# Run Python script
python script_name.py --arg value

# Example: AWS architecture designer
cd generated-skills/aws-solution-architect/
python architecture_designer.py --requirements requirements.json
```

---

### Reference Skill in Codex Prompt

**For prompt-based skills or complex workflows**:

```bash
codex exec -m gpt-5 -s read-only \
  "Using the skill documentation at path/to/SKILL.md,
  perform the following task: [your task description]"
```

---

### Combine Multiple Skills

```bash
codex exec -m gpt-5 -s workspace-write \
  "Referencing the following skills:
  - Skill 1 at path/to/skill1/SKILL.md
  - Skill 2 at path/to/skill2/SKILL.md

  Perform this complex task: [task description]"
```

---

### Resume Previous Session

```bash
# Resume last session
codex exec resume --last

# Or choose from history
codex exec resume
# (opens interactive picker)
```

---

## Best Practices for Codex CLI Users

### 1. Always Use `codex exec`

❌ **WRONG**: `codex -m gpt-5 "task"`
✅ **CORRECT**: `codex exec -m gpt-5 "task"`

**Why**: Claude Code runs in a non-terminal environment. Plain `codex` commands fail with "stdout is not a terminal" error.

---

### 2. Choose Correct Model

**gpt-5** (General reasoning):
- Architecture design
- Code analysis
- Documentation
- Planning

**gpt-5-codex** (Code editing):
- Refactoring
- Bug fixes
- Feature implementation
- Test generation

Example:
```bash
# Analysis: use gpt-5
codex exec -m gpt-5 -s read-only "analyze security"

# Editing: use gpt-5-codex
codex exec -m gpt-5-codex -s workspace-write "refactor code"
```

---

### 3. Choose Correct Sandbox Mode

**read-only** (Safe, default):
- Code review
- Analysis
- Documentation reading

**workspace-write** (File modifications):
- Code editing
- Documentation generation
- Test creation

**danger-full-access** (Network, rarely needed):
- Web scraping
- API calls
- External data fetching

---

### 4. Reference Skills Properly

**Functional skills** (has Python):
```bash
# Execute directly
cd skill-directory/
python script.py
```

**Prompt skills** (documentation only):
```bash
# Reference in prompt
codex exec "Using SKILL.md at path/to/skill, do task"
```

---

### 5. Use High Reasoning for Complex Tasks

```bash
codex exec -m gpt-5 \
  -c model_reasoning_effort=high \
  -s read-only \
  "Complex architecture analysis task"
```

---

## References

- **CLAUDE.md**: Project configuration for Claude Code
- **Skills Documentation**: See individual SKILL.md files in skill directories
- **Codex CLI Docs**: https://github.com/openai/codex
- **Claude Code Docs**: https://docs.claude.com/claude-code

---

**Last Updated**: 2025-12-31
**Generated By**: codex-cli-bridge skill
**Project Type**: GREENFIELD_NEW
**Maintained For**: Cross-tool team collaboration (Claude Code ↔ Codex CLI)
**Sync Strategy**: One-way sync (CLAUDE.md → AGENTS.md)

---

*This AGENTS.md is auto-generated from CLAUDE.md and project structure.*
*To update, modify CLAUDE.md and run: `/sync-agents-md` or regenerate with codex-cli-bridge skill.*