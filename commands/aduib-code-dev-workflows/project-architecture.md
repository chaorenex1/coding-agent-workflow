# Project Architecture Scan & Documentation Generation

## Usage

`/project-architecture [OPTIONS]`

## Parameters

- `[OPTIONS]`: Optional parameters
  - `--output-path <PATH>`: Output path (default: `./.claude/architecture/`)
  - `--format <FORMAT>`: Output format (markdown/html/pdf, default: markdown)
  - `--depth <LEVEL>`: Scan depth (shallow/standard/deep, default: standard)
  - `--include-deps`: Include dependency analysis
  - `--include-metrics`: Include code metrics/statistics

## Context

- Automatically scan the current workspace for project structure, code organization, and tech stack.
- Analyze and extract architectural patterns, design decisions, and key components.
- Generate structured architecture docs to help the team understand and maintain the system.

## Your Role

You are the architecture documentation coordinator, responsible for directing four specialist agents:

1. **Structure Analyst** — Analyzes directory structure, module organization, and file distribution.
2. **Tech Stack Identifier** — Identifies languages, frameworks, dependencies, and toolchains.
3. **Architecture Pattern Expert** — Identifies design patterns, architecture styles (MVC/microservices/layers, etc.), and key abstractions.
4. **Technical Writer** — Synthesizes information and produces clear, structured architecture docs.

## Process

1. **Project scan**:
   - Traverse the directory tree and identify source code, config files, and docs
   - Analyze file type distribution and code organization
   - Detect build tools, package managers, and key configuration files

2. **Multi-dimensional analysis**:
   - Structure Analyst: draw directory tree; identify module boundaries and layering
   - Tech Stack Identifier: extract language versions, primary frameworks, core dependencies, and dev tools
   - Architecture Pattern Expert: identify patterns/styles, key abstractions, and data flows
   - Technical Writer: consolidate results into a document outline

3. **Deep insights** (when `--depth deep`):
   - Analyze inter-component dependencies and call chains
   - Identify potential architecture issues (cycles, high coupling)
   - Extract key business flows and core algorithms

4. **Documentation generation**:
   - Generate architecture overview diagrams (text/Mermaid)
   - Write component responsibility descriptions
   - Record technical decisions and rationale
   - Provide navigation and quick reference

5. **Save outputs**: Save docs to the specified path:

```text
./.claude/architecture/
├── architecture-overview.md       # Architecture overview
├── component-details.md           # Component details
├── tech-stack.md                  # Tech stack inventory
├── design-decisions.md            # Architecture decision records (ADR)
└── diagrams/                      # Diagrams
    ├── system-overview.mmd        # System overview (Mermaid)
    ├── component-diagram.mmd      # Component diagram
    └── data-flow.mmd              # Data flow diagram
```

## Output Format

### 1. Architecture Overview (architecture-overview.md)

```markdown
# Project Architecture Overview

## Basic Information
- Project name: [auto-detected]
- Project type: [Web app/API service/desktop app/library/tool/etc.]
- Primary languages: [list]
- Architecture style: [monolith/microservices/layered/event-driven/etc.]

## System Architecture Diagram
[Mermaid diagram]

## Core components
- Component A: responsibility
- Component B: responsibility

## Tech stack overview
- Frontend: [framework/library]
- Backend: [framework/runtime]
- Database: [type/version]
- Deployment: [platform/tools]

## Key capabilities
- [capability 1]
- [capability 2]
```

### 2. Component Details (component-details.md)

```markdown
# Component Details

## Frontend layer
### Component name
- **Path**: `src/frontend/...`
- **Responsibility**: [description]
- **Key files**:
  - `file1.ts`: [purpose]
  - `file2.tsx`: [purpose]
- **Dependencies**: [other components]
- **Interfaces**: [exposed APIs/events]

## Backend layer
[same structure]

## Data layer
[same structure]
```

### 3. Tech Stack Inventory (tech-stack.md)

```markdown
# Tech Stack Inventory

## Programming languages
- [language] [version]: [usage]

## Core frameworks & libraries
| Name | Version | Purpose | Rationale |
|------|------|------|----------|
| [framework] | [version] | [purpose] | [reason] |

## Development tools
- Build tools: [tool]
- Test framework: [framework]
- Code quality: [Linter/Formatter]
- Version control: [Git workflow]

## Infrastructure
- CI/CD: [tool/platform]
- Containerization: [Docker/K8s]
- Cloud: [AWS/Azure/GCP]
```

### 4. Architecture Decision Records (design-decisions.md)

```markdown
# Architecture Decision Records (ADR)

## ADR-001: [title]
- **Date**: [scan date]
- **Status**: Adopted (inferred from code)
- **Context**: [inferred from code structure]
- **Decision**: [solution adopted]
- **Consequences**: [pros/cons in the current architecture]

## ADR-002: [next decision]
[same structure]
```

### 5. Diagrams Directory (diagrams/)

```text
diagrams/
├── system-overview.mmd        # System overview (Mermaid)
├── component-diagram.mmd      # Component diagram (Mermaid)
└── data-flow.mmd              # Data flow (Mermaid)
```

## Intelligent Analysis Strategy

### Structure heuristics

- `src/`, `app/`, `lib/` → main source directories
- `test/`, `__tests__/`, `*.test.*` → tests
- `config/`, `*.config.*` → configuration
- `public/`, `static/`, `assets/` → static assets
- `docs/`, `*.md` → documentation

### Tech stack identification rules

- `package.json` → Node.js/JavaScript ecosystem
- `requirements.txt`, `pyproject.toml` → Python
- `pom.xml`, `build.gradle` → Java
- `Cargo.toml` → Rust
- `go.mod` → Go

### Architecture pattern identification

- `controllers/`, `models/`, `views/` → MVC
- `services/`, `repositories/` → layered architecture
- multiple independent `package.json` → microservices/monorepo
- `events/`, `handlers/`, `subscribers/` → event-driven architecture

## Key Constraints

### Must do

- **Complete scan**: cover all major directories and key files
- **Pattern recognition**: accurately identify architecture styles and design patterns
- **Diagram generation**: provide architecture diagrams (Mermaid, using the latest Mermaid syntax)
- **Clear organization**: structure docs by layers/modules
- **Save outputs**: write all docs to the output directory

### Avoid

- **Over-speculation**: mark uncertain decisions as "speculation"
- **Missing core parts**: do not omit major components or key dependencies
- **Messy formatting**: keep structure clear and consistent
- **Over-simplification**: retain sufficient detail for complex architectures
- **Ignoring conventions**: follow existing project naming and organization

## Quality Bar

Generated architecture docs should be:

1. **Accurate**: descriptions match the code; tech stack identification is correct
2. **Complete**: cover major components, dependencies, and core flows
3. **Readable**: clear structure, easy navigation
4. **Maintainable**: easy to update, includes timestamps and version info
5. **Useful**: new team members can ramp up quickly

## Success Criteria

- ✅ Complete structure scan and identify all major modules
- ✅ Accurately identify tech stack, frameworks, and dependencies
- ✅ Generate at least 3 diagram types (system/component/data flow)
- ✅ Output structured docs: overview, details, tech stack, and ADRs
- ✅ Save all docs under the output directory with consistent naming
- ✅ Include generation timestamp and scan scope

## Follow-ups

After generating architecture docs, recommended next steps:

1. **Human review**: validate accuracy and add business context
2. **Periodic updates**: rescan regularly as the project evolves (quarterly or per major release)
3. **Team sharing**: include docs in onboarding materials
4. **Versioning**: store docs in Git to track evolution
5. **Continuous improvement**: refine structure and depth based on team feedback
