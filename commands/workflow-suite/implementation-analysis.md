---
description: Pre-implementation technical analysis and design specification generation
argument-hint: [feature-name|technical-requirement]
allowed-tools: Read, Bash(find:*), Bash(grep:*), Bash(tree:*), Bash(wc:*)
---

# Implementation Analysis Assistant

## Context

Feature to analyze: $ARGUMENTS

### Codebase Structure
!`tree -L 3 -I 'node_modules|.git|dist|build' 2>/dev/null || find . -type d -not -path "*/node_modules/*" -not -path "*/.git/*" | head -20`

### Existing Patterns
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" | head -15`

### Configuration
@package.json
@tsconfig.json
@requirements.txt

## Your Task

Provide detailed implementation analysis for "$ARGUMENTS":

### 1. **Implementation Approach**
   - Overall strategy and methodology
   - Key design patterns to apply
   - Architecture considerations
   - Technology choices rationale

### 2. **Code Structure Design**

   **File Organization:**
   ```
   src/
   ├── [component-folder]/
   │   ├── [file1].ts         # [Purpose]
   │   ├── [file2].ts         # [Purpose]
   │   └── __tests__/
   │       └── [file1].test.ts
   ```

   **Key Classes/Modules:**
   - Class/Module 1: [Name] - [Responsibility]
   - Class/Module 2: [Name] - [Responsibility]

### 3. **Data Flow Design**
   ```
   User Input
      ↓
   [Validation Layer]
      ↓
   [Business Logic Layer]
      ↓
   [Data Access Layer]
      ↓
   [Database/External API]
   ```

### 4. **API/Interface Specifications**

   **Public Interfaces:**
   ```typescript
   interface [InterfaceName] {
     [method1](params): ReturnType;
     [method2](params): ReturnType;
   }
   ```

   **Internal APIs:**
   ```typescript
   class [ClassName] {
     private [method1](params): ReturnType;
     public [method2](params): ReturnType;
   }
   ```

### 5. **Database/State Design**

   **Schema Changes:**
   ```sql
   CREATE TABLE [table_name] (
     id UUID PRIMARY KEY,
     [field1] VARCHAR(255) NOT NULL,
     [field2] TIMESTAMP DEFAULT NOW()
   );
   ```

   **State Management:**
   - State shape: [Description]
   - Actions: [List of actions]
   - Reducers: [List of reducers]

### 6. **Error Handling Strategy**
   - Exception types to handle
   - Error recovery mechanisms
   - User-facing error messages
   - Logging and monitoring points

### 7. **Testing Strategy**

   **Unit Tests:**
   - Test file: `__tests__/[component].test.ts`
   - Key test cases:
     1. [Test case 1]
     2. [Test case 2]

   **Integration Tests:**
   - Test scenario 1: [Description]
   - Test scenario 2: [Description]

   **Test Coverage Goals:**
   - Minimum: 80%
   - Target: 90%+

### 8. **Implementation Steps**

   **Phase 1: Foundation** (Priority: High)
   1. [ ] Create base classes/interfaces
   2. [ ] Set up data models
   3. [ ] Implement core logic

   **Phase 2: Integration** (Priority: High)
   1. [ ] Connect to existing systems
   2. [ ] Implement API layer
   3. [ ] Add error handling

   **Phase 3: Enhancement** (Priority: Medium)
   1. [ ] Add validation
   2. [ ] Implement caching
   3. [ ] Optimize performance

   **Phase 4: Polish** (Priority: Low)
   1. [ ] Add logging
   2. [ ] Write documentation
   3. [ ] Add monitoring

### 9. **Dependencies & Integration Points**

   **External Dependencies:**
   - Library 1: [Purpose]
   - Library 2: [Purpose]

   **Internal Dependencies:**
   - Module 1: [How it's used]
   - Module 2: [How it's used]

   **Integration Points:**
   - System 1: [Integration method]
   - System 2: [Integration method]

### 10. **Performance Considerations**
   - Expected load: [Requests/sec, data volume]
   - Bottleneck analysis: [Potential bottlenecks]
   - Optimization strategies: [Caching, indexing, etc.]
   - Monitoring metrics: [What to track]

### 11. **Security Considerations**
   - Authentication: [Method]
   - Authorization: [Rules]
   - Data validation: [Rules]
   - Encryption: [What needs encryption]
   - Audit logging: [What to log]

### 12. **Edge Cases & Gotchas**
   - Edge case 1: [Description and handling]
   - Edge case 2: [Description and handling]
   - Gotcha 1: [What to watch out for]
   - Gotcha 2: [What to watch out for]

## Output Format

```
🎯 IMPLEMENTATION STRATEGY
[High-level approach and methodology]

🏗️ ARCHITECTURE
[Component diagram or description]

📁 FILE STRUCTURE
[Directory and file organization]

🔌 INTERFACES & APIs
[Interface definitions]

💾 DATA DESIGN
[Database schema or state management]

🔄 DATA FLOW
[Flow diagram or description]

⚠️ ERROR HANDLING
[Error handling strategy]

🧪 TESTING PLAN
[Test strategy and coverage goals]

📋 IMPLEMENTATION CHECKLIST
Phase 1:
- [ ] Task 1
- [ ] Task 2

Phase 2:
- [ ] Task 1
- [ ] Task 2

🔗 DEPENDENCIES
External: [List]
Internal: [List]

⚡ PERFORMANCE
Load: [Expected]
Optimizations: [Planned]

🔒 SECURITY
Authentication: [Method]
Authorization: [Rules]

⚠️ EDGE CASES
1. [Edge case 1]
2. [Edge case 2]

💡 RECOMMENDATIONS
- [Recommendation 1]
- [Recommendation 2]
```

## Success Criteria

- ✅ Clear implementation strategy defined
- ✅ Code structure and organization planned
- ✅ Interfaces and APIs specified
- ✅ Data design completed
- ✅ Error handling strategy defined
- ✅ Testing plan established
- ✅ Implementation steps broken down
- ✅ Dependencies identified
- ✅ Performance and security considered
- ✅ Edge cases documented
- ✅ Ready for coding phase
