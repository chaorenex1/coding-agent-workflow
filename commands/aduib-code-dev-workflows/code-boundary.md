# Module Boundary Analysis & Documentation Generation

## Usage

`/code-boundary [OPTIONS]`

## Parameters

- `[OPTIONS]`: Optional parameters
  - `--scope <PATH>`: Analysis scope (file path or directory path)
  - `--output-path <PATH>`: Output path (default: `./.claude/docs/boundaries/`)
  - `--include-runtime`: Include runtime boundary analysis
  - `--include-dependencies`: Include cross-module dependency analysis

## Context

- Analyze the project’s module partitioning, boundary definitions, and responsibility allocation.
- Identify inter-module dependencies, communication patterns, and coupling.
- Evaluate boundary soundness and overall architectural health.

## Your Role

You are the module boundary analysis coordinator, responsible for directing three specialist agents:

1. **Module Identifier** — Identifies logical modules, physical packages, and deployment units.
2. **Boundary Analyst** — Analyzes module responsibilities, boundary definitions, and interface contracts.
3. **Dependency Tracker** — Tracks dependencies, identifies coupling issues, and detects cyclic dependencies.

## Process

1. **Module discovery**: Identify physical modules, logical modules, and deployment units
2. **Boundary definition**: Split module boundaries, analyze responsibilities, and build a dependency graph
3. **Health assessment**: Evaluate cohesion, coupling, dependency direction, and cycles
4. **Runtime analysis** (if enabled): Analyze process boundaries, service calls, and data sharing
5. **Save outputs**: Save to the specified path

```text
./.claude/docs/boundaries/{scope}/
├── boundary-overview.md           # Boundary overview
├── module-catalog.md              # Module catalog
├── dependency-analysis.md         # Dependency analysis
├── coupling-report.md             # Coupling report
├── diagrams/                      # Diagrams
│   ├── module-structure.mmd       # Module structure diagram (Mermaid)
│   └── dependency-graph.mmd       # Dependency graph
└── recommendations.md             # Boundary optimization recommendations
```

## Output Format

1. **Boundary overview** — System overview, module taxonomy, and architectural layering
2. **Module catalog** — Detailed responsibilities, interfaces, and dependencies per module
3. **Dependency analysis** — Graphs, layering validation, and cyclic dependency detection
4. **Coupling report** — Coupling evaluation, hotspot identification, and cohesion analysis
5. **Recommendations** — Break cycles, split oversized modules, and establish layered boundaries

## Intelligent Analysis Strategy

### Module identification rules
- **Physical modules**: directory structure, package names, namespaces
- **Logical modules**: prefixes, naming conventions, and annotation/comment markers
- **Deployment units**: detect Dockerfiles, config files, and entry points

### Dependency extraction strategy
- **Static dependencies**: import/require/using statements
- **Dynamic dependencies**: reflection and dependency injection configuration
- **Runtime dependencies**: HTTP calls, RPC, message queues

### Boundary violation detection
- **Layering violations**: lower layers depend on upper layers
- **Cyclic dependencies**: detect via topological sorting
- **Over-coupling**: a single module depended on by too many modules

## Key Constraints

### Must do
- **Complete identification**: find all modules and submodules
- **Dependency tracking**: build a complete dependency graph
- **Cycle detection**: identify all cycles
- **Coupling assessment**: quantify inter-module coupling
- **Actionable recommendations**: provide specific, feasible optimization proposals

### Avoid
- **Missing key modules**: ensure all core modules are analyzed
- **Incorrect dependencies**: avoid marking indirect dependencies as direct dependencies
- **Ignoring implicit coupling**: account for coupling via shared databases or global variables
- **Vague recommendations**: recommendations must be specific and measurable
- **Ignoring cost**: consider implementation cost vs. benefit

## Quality Bar

Generated boundary docs should be:

1. **Complete**: cover all major modules and boundary definitions
2. **Accurate**: dependency graphs match actual code
3. **Quantified**: include measurable metrics (coupling, cohesion, etc.)
4. **Actionable**: recommendations can be implemented
5. **Visual**: include diagrams like module structure and dependency graphs

## Success Criteria

- ✅ Identify all major modules (at least to 2nd-level modules)
- ✅ Build a complete module dependency graph
- ✅ Detect and report all cyclic dependencies
- ✅ Quantify coupling and cohesion
- ✅ Identify at least 3 high-priority boundary issues
- ✅ Provide concrete, feasible optimization proposals (with effort estimates)

## Follow-ups

After generating boundary docs, recommended next steps:

1. **Architecture review**: review boundary design with architects and tech leads
2. **Refactoring plan**: define priorities and a timeline
3. **Automated checks**: introduce dependency-check tools (e.g., dependency-cruiser, madge)
4. **Continuous monitoring**: re-run boundary health analysis regularly (monthly)
5. **Team alignment**: incorporate boundary rules into dev standards and enforce in code reviews
