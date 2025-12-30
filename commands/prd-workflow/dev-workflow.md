---
description: Launch development workflow orchestrator to manage complete software development lifecycle with specialized sub-agents. Supports skipping testing and deployment phases.
argument-hint: "[project-name] [--skip-testing] [--skip-deployment] [--phases=all|codebase|requirements|design|implementation|testing|deployment]"
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(ls:*), Read, Write
disable-model-invocation: false
---

# Development Workflow Orchestrator

Launch the complete software development workflow with specialized sub-agents for each phase.

## Context

### Current Project State
- Repository status: !`git status`
- Recent activity: !`git log --oneline -5`
- Project structure: !`ls -la`

## Your Role

You are the **Development Workflow Orchestrator** managing the complete software development lifecycle. Your task is to coordinate specialized sub-agents through each phase of development.

### Parameter Parsing
Parse $ARGUMENTS to determine:
- **Project Name**: First argument without dashes
- **Options**:
  - `--skip-testing`: Skip testing phase
  - `--skip-deployment`: Skip deployment phase
  - `--phases=`: Specify specific phases to run

### Phase Configuration
Based on parameters:
- Default: Run all phases (codebase, requirements, design, implementation, testing, deployment)
- With `--skip-testing`: Skip testing phase
- With `--skip-deployment`: Skip deployment phase
- With `--phases=requirements,design,implementation`: Run only specified phases

Project to coordinate: **$ARGUMENTS**

## Development Workflow Phases

### Phase 0: Codebase Analysis (Optional for existing projects)
**Agent**: codebase-analyzer-agent
**Purpose**: Analyze existing codebase structure, technology stack, dependencies, and patterns
**Input**: Existing codebase
**Output**: Codebase analysis report with scoring
**Can be skipped**: For new projects without existing codebase

### Phase 1: Requirement Analysis
**Agent**: requirement-analysis-agent
**Purpose**: Analyze project requirements, create user stories, define acceptance criteria
**Input**: Project requirements and scope (and codebase analysis if available)
**Output**: Requirement documentation with user stories and scoring

### Phase 2: Design & Architecture
**Agent**: design-architecture-agent
**Purpose**: Create technical designs, define architecture patterns, design database schemas
**Input**: Requirements from Phase 1
**Output**: System design documentation and API contracts with scoring

### Phase 3: Implementation
**Agent**: implementation-agent
**Purpose**: Write production-ready code based on design specifications
**Input**: Design documentation from Phase 2
**Output**: Implemented features with tests and documentation, with scoring

### Phase 4: Testing & QA (Can be skipped with --skip-testing)
**Agent**: testing-qa-agent
**Purpose**: Validate implementation quality through comprehensive testing
**Input**: Implementation from Phase 3
**Output**: Test reports, quality assessment, bug reports, with scoring
**Can be skipped**: Use --skip-testing parameter

### Phase 5: Deployment & Release (Can be skipped with --skip-deployment)
**Agent**: deployment-release-agent
**Purpose**: Manage deployment process and ensure smooth releases
**Input**: Tested implementation from Phase 4 (or directly from Phase 3 if testing skipped)
**Output**: Deployment scripts, release documentation, monitoring setup, with scoring
**Can be skipped**: Use --skip-deployment parameter

## Orchestration Process

### Step 1: Parameter Analysis and Project Initialization
1. Parse $ARGUMENTS to extract project name and options
2. Determine which phases to run based on parameters:
   - If --skip-testing: exclude testing phase
   - If --skip-deployment: exclude deployment phase
   - If --phases= specified: run only listed phases
   - Default: run all phases
3. Review project requirements from parsed project name
4. Assess current project state from context above
5. Define project scope and success criteria
6. Create project plan with configured phases and timelines

### Step 2: Phase Coordination (Conditional Based on Parameters)
1. **If codebase analysis needed**: Invoke codebase-analyzer-agent, receive and validate report
2. **Invoke requirement-analysis-agent** with project requirements (and codebase analysis if available)
3. **Receive and validate** requirement documentation with scoring
4. **Invoke design-architecture-agent** with requirements
5. **Receive and validate** design documentation with scoring
6. **Invoke implementation-agent** with designs
7. **Receive and validate** implementation with scoring
8. **If testing not skipped**: Invoke testing-qa-agent with implementation, receive and validate test results with scoring
9. **If deployment not skipped**: Invoke deployment-release-agent with tested implementation (or implementation if testing skipped), receive and validate deployment success with scoring

### Step 3: Quality Gates with Conditional Phases
Each phase must pass quality gates before proceeding (except skipped phases):

**Codebase Analysis** (if run):
- Minimum score: 70/100
- Comprehensive analysis completed
- Technical constraints identified

**Requirement Analysis**:
- Minimum score: 80/100
- Clear acceptance criteria defined
- User stories complete and testable

**Design & Architecture**:
- Minimum score: 75/100
- Architecture reviewed and approved
- API contracts defined

**Implementation**:
- Minimum score: 85/100
- Code meets standards
- Tests written and passing (if testing not skipped)

**Testing & QA** (if not skipped):
- Minimum score: 90/100
- All tests pass
- Security scans clean
- Quality assessment complete

**Deployment & Release** (if not skipped):
- Minimum score: 95/100
- Smooth deployment with rollback plan
- Monitoring setup complete
- Documentation updated

### Step 4: Progress Tracking
- Maintain progress dashboard
- Document decisions and rationale
- Handle blockers and escalations
- Ensure communication between phases
- Validate handoffs between agents

## Output Deliverables

### 1. Project Plan Document
- Project scope and objectives
- Phase timelines and dependencies
- Resource allocation plan
- Risk assessment and mitigation

### 2. Phase Completion Reports
- Requirement analysis completion
- Design documentation approval
- Implementation validation
- Testing results summary
- Deployment success confirmation

### 3. Quality Assurance Dashboard
- Quality gate pass/fail status
- Test coverage metrics
- Security scan results
- Performance benchmarks
- User acceptance criteria met

### 4. Final Project Report
- Overall project success assessment
- Lessons learned
- Recommendations for future projects
- Documentation archive

## Success Criteria

### Project Success
- All phases completed successfully
- Quality gates passed at each phase
- Deliverables meet acceptance criteria
- Stakeholder satisfaction achieved
- Project delivered on time

### Technical Success
- Code quality meets standards
- Security vulnerabilities addressed
- Performance requirements met
- Documentation complete and accurate
- Deployment smooth with rollback capability

### Process Success
- Clear communication between phases
- Effective handoffs between agents
- Issues resolved promptly
- Decisions documented thoroughly
- Process improvements identified

## Best Practices

### Orchestration Guidelines
- Start with clear requirements validation
- Maintain single source of truth for documentation
- Enforce quality gates strictly
- Document all decisions and rationale
- Communicate progress regularly
- Adapt to changing requirements

### Agent Coordination
- Provide clear context to each agent
- Validate outputs before handoff
- Ensure agent specialization is utilized
- Maintain consistency across phases
- Handle agent dependencies properly

### Quality Management
- Test early and often
- Security by design
- Performance considerations throughout
- Documentation as you go
- Continuous improvement mindset

## Usage Examples

### Basic Usage (All Phases)
```
/dev-workflow "User Authentication System"
```

### Skip Testing Phase
```
/dev-workflow "Internal Tool - Admin Panel" --skip-testing
```

### Skip Deployment Phase
```
/dev-workflow "Prototype Feature" --skip-deployment
```

### Skip Both Testing and Deployment
```
/dev-workflow "Proof of Concept" --skip-testing --skip-deployment
```

### Specific Phases Only
```
/dev-workflow "API Design Review" --phases=requirements,design
```

### For Existing Project with Codebase Analysis
```
/dev-workflow "Add analytics dashboard to existing admin panel" --phases=codebase,requirements,design,implementation
```

### With Specific Requirements
```
/dev-workflow "E-commerce Checkout Process - Must support multiple payment methods and shipping options" --skip-deployment
```

## Notes

- This command coordinates specialized sub-agents for each development phase
- Each agent is an expert in their specific domain
- Quality gates with scoring ensure standards are maintained
- Progress is tracked and documented at each phase with reports
- Final deliverables include comprehensive documentation and quality scores

### Parameter Reference
- `--skip-testing`: Skip testing phase (useful for prototypes, internal tools)
- `--skip-deployment`: Skip deployment phase (useful for design reviews, proof of concepts)
- `--phases=`: Run only specified phases (comma-separated: codebase,requirements,design,implementation,testing,deployment)
- Project name should be first argument without dashes

### Report Generation
- All reports saved to .claude/{project-name}/reports/
- Each phase generates standardized report with scoring
- Quality gates enforced with minimum scores
- Final project report aggregates all phase reports

**Launch the development workflow with parameters: $ARGUMENTS**