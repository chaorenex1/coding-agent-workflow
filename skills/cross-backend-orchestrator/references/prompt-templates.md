# Prompt Templates for Cross-Backend Consistency

Use these structured prompt templates to achieve consistent results across Codex, Claude, and Gemini backends.

## Template 1: Code Generation

```
Task: [Specific coding task]
Language: [Programming language]
Requirements:
- [Requirement 1]
- [Requirement 2]
Constraints:
- [Constraint 1]
- [Constraint 2]
Output Format: [Function/Class/Module/Script]
```

**Example:**
```
Task: Create a function to validate email addresses
Language: Python
Requirements:
- Support standard email formats
- Return boolean result
- Handle edge cases gracefully
Constraints:
- No external dependencies
- Must be type-annotated
Output Format: Function with docstring
```

## Template 2: Analysis Task

```
Objective: [What to analyze]
Input: [Description of input data/content]
Focus Areas:
- [Area 1]
- [Area 2]
Expected Output:
- [Output type 1]
- [Output type 2]
Depth: [Brief/Standard/Comprehensive]
```

## Template 3: Creative Content

```
Content Type: [Article/Story/Documentation/etc.]
Topic: [Main subject]
Tone: [Formal/Casual/Technical/etc.]
Audience: [Target readers]
Length: [Word count or section count]
Key Points to Include:
- [Point 1]
- [Point 2]
```

## Template 4: Review/Improvement

```
Task: Review and improve the following
Input Type: [Code/Document/Design/etc.]
Review Criteria:
- [Criterion 1]
- [Criterion 2]
Improvement Goals:
- [Goal 1]
- [Goal 2]
Previous Context: [Any relevant background]

[Content to review]
```

## Template 5: Multi-Step Pipeline

For pipeline workflows where output passes between backends:

**Stage 1 (Generation):**
```
Generate [output type] for [purpose].
Requirements: [List requirements]
Output this as structured data that can be processed in the next stage.
```

**Stage 2 (Review/Transform):**
```
Previous stage output:
[Insert previous output]

Task: [Review/Transform/Enhance] the above.
Focus on: [Specific improvements]
Maintain: [What to preserve]
```

**Stage 3 (Finalize):**
```
Previous stage output:
[Insert previous output]

Task: Finalize and polish.
Add: [Documentation/Tests/Examples]
Format: [Final output format]
```

## Backend-Specific Considerations

### Codex
- Optimized for code generation
- Include explicit language and framework specifications
- Provide clear function signatures when possible

### Claude
- Strong at reasoning and analysis
- Can handle nuanced instructions
- Good for review and improvement tasks

### Gemini
- Visual understanding capabilities
- Good for UX/UI descriptions
- Effective for documentation tasks

## Best Practices

1. **Be Explicit**: State requirements clearly; avoid ambiguity
2. **Structure Input**: Use consistent formatting across backends
3. **Define Output**: Specify expected output format precisely
4. **Provide Context**: Include relevant background information
5. **Set Constraints**: Define boundaries and limitations upfront