# Design Doc Generator

Generate comprehensive technical design documents with database schemas, API specifications, system architecture diagrams, and Mermaid visualizations.

## Features

1. **Database Schema Design**
   - Entity-Relationship diagrams
   - Table definitions with constraints
   - Index strategies
   - DDL statements

2. **Module Layering Design**
   - Architecture layer definitions
   - Module responsibility matrix
   - Dependency graphs

3. **Module Interface Design**
   - Interface specifications
   - Data transfer objects
   - Error handling

4. **API Interface Design**
   - RESTful endpoint specifications
   - Request/response schemas
   - OpenAPI documentation

5. **Business Flowcharts**
   - Process visualization
   - Decision logic
   - Swimlane diagrams

6. **Data Flow Diagrams**
   - Context diagrams
   - Level 1 DFDs
   - Data dictionary

7. **Sequence Diagrams**
   - Component interactions
   - Message flows
   - Async patterns

## Usage

Invoke this skill when you need to:

- "Generate a design document for my project"
- "Create a database schema for an e-commerce system"
- "Design RESTful API endpoints"
- "Draw a sequence diagram for the checkout flow"
- "Create module architecture documentation"
- "Document system data flows"

## Directory Structure

```
design-doc-generator/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── VALIDATION.md         # Validation checklist
├── templates/            # Document templates
│   ├── database-schema.md
│   ├── api-spec.md
│   └── module-design.md
├── examples/             # Complete examples
│   └── ecommerce-design-doc.md
└── references/           # Detailed guides
    ├── design-patterns.md
    └── mermaid-diagrams.md
```

## Templates

### Database Schema Template
Located in `templates/database-schema.md`
- ER diagram syntax
- Table definition format
- Index strategy guidelines
- DDL statement examples

### API Specification Template
Located in `templates/api-spec.md`
- RESTful endpoint structure
- Request/response schemas
- Error handling patterns
- OpenAPI specification

### Module Design Template
Located in `templates/module-design.md`
- Architecture diagrams
- Interface definitions
- Communication patterns
- Layer responsibilities

## Examples

The `examples/ecommerce-design-doc.md` file contains a complete design document for an e-commerce platform, demonstrating all features:

- Microservices architecture
- PostgreSQL database schema
- RESTful API design
- Order processing flowcharts
- State machine diagrams
- Sequence diagrams for checkout

## References

### Design Patterns Reference
Located in `references/design-patterns.md`
- Layered Architecture
- Hexagonal Architecture
- Clean Architecture
- Microservices patterns
- CQRS, Saga, Circuit Breaker

### Mermaid Diagrams Reference
Located in `references/mermaid-diagrams.md`
- Flowchart syntax
- Sequence diagram syntax
- ER diagram syntax
- State diagram syntax
- Class diagram syntax

## Quick Start

1. **Basic Design Document**
   ```
   Create a technical design document for a task management application
   ```

2. **Database Schema**
   ```
   Generate a database schema for a blog platform with users, posts, and comments
   ```

3. **API Design**
   ```
   Design RESTful API endpoints for a weather service
   ```

4. **Flowchart**
   ```
   Create a flowchart showing the user registration process
   ```

5. **Sequence Diagram**
   ```
   Generate a sequence diagram for the payment processing flow
   ```

## Output Format

All generated documentation follows this structure:

1. Overview
2. System Architecture
3. Database Design
4. Module Design
5. API Design
6. Business Processes
7. Data Flow
8. Sequence Diagrams
9. Security Considerations
10. Deployment Architecture

## Mermaid Support

All diagrams use Mermaid syntax for rendering in Markdown-compatible viewers:

- GitHub, GitLab, Bitbucket
- Notion
- Obsidian
- VS Code with Mermaid preview
- Markdown editors with Mermaid plugins

## Best Practices

1. **Start with Requirements**: Understand business needs before designing
2. **Iterative Refinement**: Update docs as the design evolves
3. **Consistent Naming**: Use uniform terminology across diagrams
4. **Review with Stakeholders**: Validate with both technical and business teams
5. **Version Control**: Track changes alongside code

## Validation

See `VALIDATION.md` for the complete validation checklist to ensure quality design documents.

## Contributing

To improve this skill:

1. Review existing templates and references
2. Add new examples from real projects
3. Enhance design pattern documentation
4. Update Mermaid diagram examples

## License

This skill is part of the Claude Code plugin ecosystem.
