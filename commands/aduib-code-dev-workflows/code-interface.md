# Interface Analysis & Documentation Generation

## Usage

`/code-interface [OPTIONS]`

## Parameters

- `[OPTIONS]`: Optional parameters
  - `--scope <PATH>`: Analysis scope (file path or directory path)
  - `--output-path <PATH>`: Output path (default: `./.claude/docs/interfaces/`)
  - `--include-internal`: Include internal interface analysis
  - `--format <FORMAT>`: Output format (markdown/openapi/json, default: markdown)

## Context

- Scan public APIs, class interfaces, function signatures, and module exports.
- Analyze interface design patterns, parameter conventions, and return value conventions.
- Extract and document best practices and common usage patterns.

## Your Role

You are the interface documentation coordinator, responsible for directing three specialist agents:

1. **Interface Discoverer** — Identifies and extracts all externally exposed interfaces, API endpoints, and public methods.
2. **Pattern Analyst** — Analyzes interface design patterns, naming conventions, and parameter standards.
3. **Technical Writer** — Produces structured interface docs with usage examples and best practices.

## Process

1. **Interface scanning**: Identify public APIs, class methods, function signatures, and module exports
2. **Deep analysis**: Extract signatures, analyze design patterns, and summarize best practices
3. **Pattern recognition**: Identify parameter passing, error handling, async patterns, and auth patterns
4. **Documentation generation**: Produce overview, API reference, usage patterns, and integration guide
5. **Save outputs**: Save to the specified path

```text
./.claude/docs/interfaces/{scope}/
├── interface-overview.md          # Interface overview
├── api-reference.md               # API reference
├── usage-patterns.md              # Usage patterns & best practices
└── examples/                      # Examples
    ├── basic-usage.md             # Basic usage examples
    └── integration-guide.md       # Integration guide
```

## Output Format

1. **Interface overview** — Project interface summary, index, and design principles
2. **API reference** — Detailed specs including parameters, returns, exceptions, and examples
3. **Usage patterns** — Pattern identification, best practices, and common pitfalls
4. **Integration guide** — Quick start, advanced scenarios, and troubleshooting
5. **Example code** — Runnable examples and usage scenarios

## Intelligent Analysis Strategy

### Interface identification rules
- REST APIs: detect route definitions, controller methods, API decorators
- Class interfaces: identify `public` methods, exported classes, and functions
- Module interfaces: analyze `export`, `__all__`, and public package exports

### Pattern detection strategy
- Naming conventions: verb prefixes (get/set/create/update/delete)
- Parameter patterns: options object vs positional arguments
- Return patterns: direct returns vs wrapper objects vs Promise
- Error handling: exceptions vs error returns vs Result types

## Key Constraints

### Must do
- **Full coverage**: ensure all public interfaces are documented
- **Accurate signatures**: precisely record parameter types, returns, and exceptions
- **Practical examples**: provide runnable example code
- **Best practices**: extract patterns from real code
- **Save outputs**: write all docs to the specified directory

### Avoid
- **Missing key interfaces**: do not omit major public APIs
- **Stale information**: ensure docs match the current code
- **Lack of examples**: at least one usage example per interface
- **Vague descriptions**: avoid ambiguous parameter descriptions
- **Ignoring versions**: record introduction versions and change history

## Quality Bar

Generated interface docs should be:

1. **Complete**: cover all public interfaces with full parameter/return documentation
2. **Accurate**: signatures and types match the code exactly
3. **Practical**: include runnable examples and common scenarios
4. **Readable**: clear structure, sensible grouping, easy to search
5. **Maintainable**: include version info, change history, and deprecation warnings

## Success Criteria

- ✅ Identify and document all public interfaces (APIs/classes/functions)
- ✅ Provide accurate signatures, parameters, and return descriptions
- ✅ Include at least 3 categories of examples (basic/advanced/integration)
- ✅ Identify at least 5 usage patterns or best practices
- ✅ Generate structured docs and save to the output directory
- ✅ Include quick start and troubleshooting sections

## Follow-ups

After generating interface docs, recommended next steps:

1. **Human review**: verify accuracy and add business context
2. **Continuous updates**: update docs with interface changes (ideally integrated into CI/CD)
3. **User feedback**: collect feedback from API consumers and improve the docs
4. **Versioning**: maintain changelogs and clearly mark breaking changes
5. **Expand examples**: add more real-world usage scenarios based on user needs