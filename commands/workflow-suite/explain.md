---
description: Comprehensive code explanation with architecture, flow, and documentation generation
argument-hint: [file-path|function-name|component-name]
allowed-tools: Read, Bash(find:*), Bash(grep:*), Bash(tree:*), Bash(wc:*)
---

# Code Explanation Assistant

## Context

Code to explain: $ARGUMENTS

### Project Structure
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.java" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -20`

### Relevant Documentation
@README.md
@CLAUDE.md

## Your Task

Provide comprehensive explanation of "$ARGUMENTS":

### 1. **High-Level Overview**
   - What is this code's purpose?
   - Where does it fit in the system?
   - What problem does it solve?
   - Key responsibilities

### 2. **Architecture & Design**
   - Overall structure and organization
   - Design patterns used
   - Key abstractions and interfaces
   - Dependency relationships
   - Data flow

### 3. **Component Breakdown**
   For each major component:
   - **Purpose**: What it does
   - **Inputs**: What data it receives
   - **Processing**: How it transforms data
   - **Outputs**: What it produces
   - **Side Effects**: External interactions

### 4. **Code Flow Analysis**
   - Entry points
   - Main execution paths
   - Control flow (conditions, loops)
   - Error handling paths
   - Exit points

### 5. **Key Concepts & Logic**
   - Business logic explanation
   - Algorithms used
   - Important variables/state
   - Critical functions/methods
   - Edge cases handled

### 6. **Dependencies & Integration**
   - External libraries used
   - APIs called
   - Database interactions
   - File system operations
   - Network communications

### 7. **Examples & Use Cases**
   - Common usage scenarios
   - Input/output examples
   - Edge case demonstrations
   - Integration examples

### 8. **Technical Details**
   - Performance considerations
   - Memory usage patterns
   - Concurrency/async handling
   - Error handling strategy
   - Security considerations

### 9. **Improvement Opportunities**
   - Code quality issues
   - Performance bottlenecks
   - Technical debt
   - Refactoring suggestions
   - Missing features

## Output Format

```
📋 OVERVIEW
[High-level summary in 2-3 sentences]

🏗️ ARCHITECTURE
[Structure and design patterns]

🔄 FLOW DIAGRAM (Text)
[ASCII or text representation of flow]

📦 COMPONENTS
Component 1: [Name]
- Purpose: [What it does]
- Key Functions: [Main functions]
- Dependencies: [What it uses]

Component 2: [Name]
...

💡 KEY CONCEPTS
1. [Important concept 1]
2. [Important concept 2]

📝 CODE EXAMPLES
Example 1: [Scenario]
```code
[Usage example]
```

🎯 USE CASES
1. [Use case 1]: [Description]
2. [Use case 2]: [Description]

⚠️ IMPORTANT NOTES
- [Critical point 1]
- [Critical point 2]

🔧 IMPROVEMENT SUGGESTIONS
- [Suggestion 1]
- [Suggestion 2]
```

## Success Criteria

- ✅ Clear, accessible explanation for target audience
- ✅ Covers architecture, flow, and implementation
- ✅ Includes practical examples
- ✅ Identifies key concepts and patterns
- ✅ Highlights important considerations
- ✅ Suggests improvements where applicable
