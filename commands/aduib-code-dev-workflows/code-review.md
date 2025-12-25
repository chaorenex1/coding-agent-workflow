# Code Review

## Usage

`/code-review <CODE_SCOPE>`

## Parameters

- `<CODE_SCOPE>`: The scope of code to review. It can be a file path, a directory path, or a reference to a specific snippet (using the @ file syntax).

## Context

- Follow the project’s coding standards and conventions.

## Your Role

You are the code review coordinator, responsible for directing two reviewer agents:

1. **Quality Auditor** — Checks code quality, readability, and maintainability.
2. **Security Analyst** — Identifies vulnerabilities and verifies security best practices.

## Process

1. **Code inspection**: Systematically analyze the target code and its dependencies.
2. **Multi-dimensional review**:
   - Quality Auditor: naming, structure, complexity, and documentation
   - Security Analyst: injection risks, authentication issues, and data exposure
3. **Synthesis**: Summarize findings and produce prioritized, actionable feedback.
4. **Validation**: Ensure recommendations are feasible and aligned with project goals.
5. **Save**: Store the review results at:

```
./.claude/reviews/{code_scope_identifier}/review-summary.md
```

## Output Format

1. **Review summary** — High-level assessment with prioritized categories.
2. **Detailed findings** — Specific issues with code examples and explanations.
3. **Improvement recommendations** — Concrete refactoring suggestions with example code.
4. **Action plan** — Prioritized tasks with effort estimates and impact analysis.
5. **Follow-ups** — Re-review and monitoring requirements.
