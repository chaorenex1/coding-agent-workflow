# Codex Complexity Selection Guide

This guide helps you choose the right complexity level and model for your code generation tasks using memex-cli with Codex backend.

---

## Understanding Complexity Levels

The 5-level complexity system maps task requirements to optimal model selection:

- **Level 1-2**: Fast models (codex-mini, codex) for routine tasks
- **Level 3**: Balanced model (codex-max) for production-grade modules
- **Level 4-5**: Powerful models (gpt-5.2) for complex logic and architecture

---

## Level 1: Simple Scripts

### Characteristics

- Single-file utilities
- Linear logic flow (no complex branches)
- Minimal error handling
- 20-100 lines of code

### Best For

- File operations (batch rename, copy, move)
- Data processing scripts (CSV, JSON parsing)
- System monitoring (disk, memory, process)
- Quick automation tasks
- Format conversion utilities

### Recommended Models

- **Primary**: `gpt-5.1-codex-mini` (fastest, lowest cost)
- **Alternative**: `gpt-5.2-codex` (if mini struggles)

### When to Use

- Task completion time < 30 seconds
- No external dependencies beyond stdlib
- Throwaway scripts or prototypes

---

## Level 2: Utility Functions

### Characteristics

- Reusable helper functions
- Input validation and type checking
- Modular design (classes/functions)
- 100-300 lines of code

### Best For

- Validation libraries (email, phone, ID card)
- Data transformation utilities
- Format converters (JSON ↔ YAML ↔ TOML)
- String/math helper functions
- Configuration parsers
- **Unit Testing** (simple test cases for modules)

### Recommended Models

- **Primary**: `gpt-5.2-codex`
- **When to upgrade**: `gpt-5.1-codex-max` for complex validation logic

### When to Use

- Code will be imported by other modules
- Requires moderate error handling
- Needs basic documentation

---

## Level 3: Complete Modules

### Characteristics

- Production-ready modules
- Comprehensive error handling
- Logging and monitoring
- Unit tests included
- 300-800 lines of code

### Best For

- HTTP clients with retry/timeout logic
- Database helpers (connection pooling, query builders)
- API wrappers (REST, GraphQL)
- Cache managers (Redis, Memcached)
- File parsers (XML, YAML, custom formats)
- **Code Review** (analyzing existing modules for issues)
- **Refactoring** (improving single module code quality)
- **Unit Testing** (comprehensive test coverage for modules)

### Recommended Models

- **Primary**: `gpt-5.1-codex-max` (best balance)
- **Complex modules**: `gpt-5.2`

### When to Use

- Code runs in production environments
- Needs integration with external services
- Requires thorough testing
- Team collaboration (code review needed)

### Special Tasks at Level 3

**Code Review**:
- Analyze code for security issues
- Identify performance bottlenecks
- Suggest refactoring opportunities
- Use `files-mode: embed` to include source files

**Refactoring**:
- Apply design patterns
- Extract common logic
- Improve testability
- Reduce code duplication

**Unit Testing**:
- Write pytest/unittest test suites
- Cover happy path + edge cases
- Include mock/stub examples
- Achieve >80% coverage

---

## Level 4: Complex Algorithms

### Characteristics

- Advanced data structures
- Optimized performance (O(log n), O(n))
- Mathematical/computational complexity
- 500-1500 lines of code

### Best For

- Algorithm implementations (sorting, searching, graph)
- Data structures (trees, heaps, skip lists)
- Path finding (Dijkstra, A*)
- Expression parsers (AST, tokenization)
- Cryptographic algorithms
- Machine learning utilities
- **Large Refactoring** (multi-module code improvements)

### Recommended Models

- **Primary**: `gpt-5.2`
- **Critical**: Increase `timeout` to 180-300s

### When to Use

- Performance is critical
- Requires deep algorithm knowledge
- Complex edge case handling
- Mathematical proofs needed

---

## Level 5: System Design & Architecture

### Characteristics

- Multi-module projects
- Microservices architecture
- Database schema design
- API contracts and specs
- 2000+ lines of code

### Best For

- Authentication services (JWT, OAuth2, RBAC)
- Event-driven systems (message queues, CQRS)
- Distributed systems (load balancing, sharding)
- Complete backend services
- Full-stack applications
- DevOps infrastructure (Docker, K8s configs)

### Recommended Models

- **Primary**: `gpt-5.2`
- **Timeout**: 300-600s
- **Use DAGs**: Break into parallel subtasks

### When to Use

- Designing new systems from scratch
- Requires architectural decision-making
- Multiple service integration
- Need scalability/reliability planning

---

## Decision Tree: Choosing the Right Level

```
Start
  ├─ Single file, <100 lines? → Level 1
  ├─ Reusable functions, no external deps? → Level 2
  ├─ Production module with tests?
  │   ├─ Standard CRUD/API? → Level 3
  │   └─ Complex algorithm? → Level 4
  └─ Multi-module/microservice? → Level 5
```

### Quick Classification Table

| Task Type | Typical Level | Model |
|-----------|--------------|-------|
| Batch rename files | 1 | codex-mini |
| Email validator | 2 | codex |
| HTTP client with retry | 3 | codex-max |
| Skip list implementation | 4 | gpt-5.2 |
| Auth microservice | 5 | gpt-5.2 |
| Code review | 3 | codex-max |
| Simple refactor | 3 | codex-max |
| Complex refactor | 4 | gpt-5.2 |
| Unit tests (simple module) | 2 | codex |
| Unit tests (complex module) | 3 | codex-max |

---

## Model Performance by Complexity

### Speed vs Quality Trade-offs

| Model | Level 1-2 | Level 3 | Level 4-5 | Cost | Speed |
|-------|-----------|---------|-----------|------|-------|
| codex-mini | ⭐⭐⭐ | ⭐ | ❌ | $ | ⚡⚡⚡ |
| codex | ⭐⭐⭐ | ⭐⭐ | ⭐ | $$ | ⚡⚡ |
| codex-max | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | $$$ | ⚡ |
| gpt-5.2 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | $$$$ | ⚡ |

### When to Upgrade Models

**From codex-mini to codex**:
- Script fails with syntax errors
- Needs external library usage
- Requires better error handling

**From codex to codex-max**:
- Production-grade quality needed
- Complex business logic
- Integration with multiple services

**From codex-max to gpt-5.2**:
- Algorithm optimization required
- System architecture design
- Performance-critical code

---

## Best Practices

### Model Selection

1. **Start small**: Try lower complexity models first
2. **Monitor quality**: Check generated code quality
3. **Upgrade when needed**: Don't over-provision expensive models
4. **Use timeout wisely**: Increase for complex tasks (default: 300s)

### Task Design

1. **Be specific**: Include language, framework, coding standards
2. **Provide context**: Use `files` field for code review/refactoring
3. **Break down**: Split Level 5 tasks into parallel Level 3-4 subtasks
4. **Use dependencies**: Chain tasks (design → implement → test)

### Cost Optimization

- Use `codex-mini` for prototyping (iterate fast)
- Reserve `gpt-5.2` for final production code
- Parallelize independent tasks to reduce total time
- Cache and reuse generated utilities

---

## Examples by Task Type

### Code Quality Tasks

**Code Review** (Level 3):
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: review
backend: codex
model: gpt-5.1-codex-max
files: ./src/auth.py
files-mode: embed
---CONTENT---
Review for: security issues, performance, best practices
---END---
EOF
```

**Refactoring** (Level 3-4):
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: refactor
backend: codex
model: gpt-5.2  # Use gpt-5.2 for large refactors
files: ./src/legacy.py
files-mode: embed
---CONTENT---
Apply design patterns, extract common logic, improve testability
---END---
EOF
```

**Unit Testing** (Level 2-3):
```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: test
backend: codex
model: gpt-5.2-codex
files: ./src/calculator.py
files-mode: embed
---CONTENT---
Write pytest tests covering all edge cases, >80% coverage
---END---
EOF
```

---

## Related Resources

- [skills/memex-cli/references/advanced-usage.md](../../memex-cli/references/advanced-usage.md) - Multi-task workflows and DAGs
- [skills/memex-cli/examples/parallel-tasks.md](../../memex-cli/examples/parallel-tasks.md) - Parallel execution patterns
- [skills/memex-cli/examples/resume-workflow.md](../../memex-cli/examples/resume-workflow.md) - Resume and context management
- [skills/code-with-codex/examples/](../examples/) - Runnable examples for each level
