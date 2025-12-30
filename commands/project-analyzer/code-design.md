# Design Analysis & Documentation Generation

## Usage

`/code-design [OPTIONS]`

## Parameters

- `[OPTIONS]`: Optional parameters
  - `--scope <PATH>`: Analysis scope (file path or directory path)
  - `--output-path <PATH>`: Output path (default: `./.claude/docs/design/`)
  - `--depth <LEVEL>`: Analysis depth (shallow/standard/deep, default: standard)
  - `--include-diagrams`: Generate UML-style class and relationship diagrams

## Context

- Deeply analyze abstract classes, interface definitions, and design patterns in the project.
- Identify core abstraction layers, inheritance hierarchies, and composition structures.
- Assess how design principles (SOLID) are applied and infer architectural intent.

## Your Role

You are the design analysis coordinator, responsible for directing three specialist agents:

1. **Abstraction Identifier** — Identifies abstract classes, interfaces, traits, and protocol definitions.
2. **Relationship Analyst** — Analyzes inheritance hierarchies, implementation relationships, and composition dependencies.
3. **Pattern Expert** — Identifies design patterns, design principles, and architectural intent.

## Process

1. **Design element scanning**: Identify abstract classes, interfaces, and abstract methods
2. **Relationship modeling**: Extract abstractions, build inheritance trees, and recognize patterns
3. **Design intent analysis**: Identify separation of concerns, OCP, ISP, and DIP
4. **Pattern recognition**: Identify creational/structural/behavioral patterns and architectural patterns
5. **Save outputs**: Save to the specified path

```text
./.claude/docs/design/{scope}/
├── design-overview.md             # Design overview
├── abstractions.md                # Abstractions & interfaces
├── design-patterns.md             # Design pattern identification
├── principles-analysis.md         # Design principles analysis
├── diagrams/                      # Diagrams
│   ├── class-hierarchy.mmd        # Class hierarchy (Mermaid)
│   └── dependency-graph.mmd       # Dependency graph
└── recommendations.md             # Design improvement recommendations
```

## Output Format

1. **Design overview** — Summary, core abstraction layers, and principles evaluation
2. **Abstractions** — Detailed explanations of abstract classes and interfaces, including responsibilities and implementation requirements
3. **Pattern identification** — GoF patterns, architectural patterns, and scenarios
4. **Principles analysis** — SOLID assessment, with good examples and improvement suggestions
5. **Recommendations** — Concrete, feasible design improvements and refactoring plan

## Intelligent Analysis Strategy

### Abstraction identification rules
- **Abstract classes**: classes with the `abstract` keyword or abstract methods
- **Interfaces**: `interface`, `protocol`, `trait` definitions
- **Implicit abstractions**: pure virtual functions and unimplemented methods

### Relationship extraction strategy
- **Inheritance**: `extends`, `:`, inheritance symbols
- **Implementation**: `implements`, `:`, interface implementations
- **Composition**: member fields and constructor injection
- **Dependencies**: method parameters and return types

### Pattern matching heuristics
- **Factory**: `create*`/`make*`/`build*` methods returning abstract types
- **Singleton**: private constructor + static instance accessor
- **Strategy**: interface + multiple implementations + runtime switching
- **Observer**: `subscribe`/`notify`/`listener`-related methods

## Key Constraints

### Must do
- **Complete identification**: find all abstractions, interfaces, and key patterns
- **Relationship modeling**: build complete inheritance and implementation graphs
- **Intent analysis**: explain the intent and scenarios for each abstraction
- **Pattern evaluation**: evaluate whether pattern usage is appropriate
- **Actionable recommendations**: provide feasible optimization proposals

### Avoid
- **Missing core abstractions**: do not ignore major abstraction layers
- **False positives**: avoid treating ordinary code as a design pattern
- **Vague recommendations**: recommendations must be specific and feasible
- **Ignoring context**: analysis must consider real project constraints
- **Overly harsh critique**: objectively evaluate pros and cons

## Quality Bar

Generated design docs should be:

1. **Complete**: cover all core abstractions and patterns
2. **Accurate**: correctly identify relationships and intent
3. **Deep**: not just "what", but also "why"
4. **Practical**: provide actionable improvements and refactoring ideas
5. **Visual**: include class/relationship diagrams

## Success Criteria

- ✅ Identify all abstract classes, interfaces, and core abstraction layers
- ✅ Build complete inheritance and implementation diagrams
- ✅ Identify at least 5 design patterns and their usage scenarios
- ✅ Assess SOLID (at least 2 examples per principle)
- ✅ Provide at least 3 concrete design improvement recommendations
- ✅ Generate structured docs and save to the output directory

## Follow-ups

After generating design docs, recommended next steps:

1. **Team review**: review results with architects and senior engineers
2. **Refactoring plan**: convert recommendations into a prioritized plan
3. **Knowledge sharing**: share patterns and best practices with the team
4. **Continuous tracking**: re-run periodically (quarterly) to monitor evolution
5. **Design review**: use this doc as a reference for new feature design reviews
