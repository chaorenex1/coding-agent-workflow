---
description: Technical requirements analysis and architecture planning from business requirements
argument-hint: [feature-name|requirement-doc]
allowed-tools: Read, Bash(find:*), Bash(grep:*), Bash(tree:*)
---

# Technical Requirements Analysis Assistant

## Context

Requirements to analyze: $ARGUMENTS

### Existing Codebase
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -15`

### Available Documentation
@README.md
@CLAUDE.md
@package.json
@requirements.txt

## Your Task

Transform "$ARGUMENTS" into technical requirements and architecture plan:

### 1. **Technical Feasibility Analysis**
   - Is the requirement technically feasible?
   - What are the technical challenges?
   - What existing patterns can be leveraged?
   - What new capabilities are needed?

### 2. **Architecture Impact Assessment**
   - Which components will be affected?
   - What new components are needed?
   - How does this fit existing architecture?
   - What patterns should be applied?

### 3. **Data Requirements**
   - What data needs to be stored?
   - What is the data model?
   - What are the data relationships?
   - What are the data validation rules?
   - What are the data migration needs?

### 4. **API/Interface Design**
   - What APIs/endpoints are needed?
   - What are the request/response formats?
   - What are the input validations?
   - What are the error responses?
   - What is the authentication/authorization?

### 5. **Integration Requirements**
   - External systems to integrate with?
   - Internal services to connect?
   - Third-party APIs needed?
   - Data synchronization requirements?

### 6. **Technical Constraints**
   - Performance requirements (response time, throughput)
   - Scalability needs (concurrent users, data volume)
   - Security requirements (authentication, encryption)
   - Compliance constraints (GDPR, HIPAA, etc.)
   - Technology stack limitations

### 7. **Implementation Breakdown**
   Break down into technical tasks:

   **Backend Tasks:**
   1. [Database schema changes]
   2. [API endpoint development]
   3. [Business logic implementation]

   **Frontend Tasks:**
   1. [UI component development]
   2. [State management]
   3. [API integration]

   **Infrastructure Tasks:**
   1. [Deployment configuration]
   2. [Monitoring setup]
   3. [Security hardening]

### 8. **Testing Strategy**
   - Unit test requirements
   - Integration test scenarios
   - End-to-end test cases
   - Performance test criteria
   - Security test considerations

### 9. **Risk & Mitigation**
   - Technical risks identified
   - Performance risks
   - Security vulnerabilities
   - Mitigation strategies

### 10. **Effort Estimation**
   - Complexity assessment (Low/Medium/High)
   - Dependencies identification
   - Critical path analysis
   - Resource requirements

## Output Format

```
🎯 TECHNICAL OVERVIEW
[Summary of technical approach]

✅ FEASIBILITY
Status: [Feasible/Challenging/Needs Research]
Challenges: [List key challenges]

🏗️ ARCHITECTURE IMPACT
Affected Components:
- [Component 1]: [Changes needed]
- [Component 2]: [Changes needed]

New Components:
- [Component 1]: [Purpose and design]

📊 DATA REQUIREMENTS
Data Model:
```
[Entity/table definitions]
```

Relationships:
- [Relationship 1]

🔌 API/INTERFACE DESIGN
Endpoints:
1. POST /api/[endpoint]
   - Request: [Format]
   - Response: [Format]
   - Validation: [Rules]

🔗 INTEGRATIONS
External:
- [System 1]: [Integration method]

Internal:
- [Service 1]: [Communication pattern]

⚙️ TECHNICAL CONSTRAINTS
- Performance: [Requirements]
- Security: [Requirements]
- Compliance: [Requirements]

📋 IMPLEMENTATION TASKS
Backend (Estimated: [X] points):
1. [Task 1]
2. [Task 2]

Frontend (Estimated: [X] points):
1. [Task 1]
2. [Task 2]

Infrastructure (Estimated: [X] points):
1. [Task 1]

🧪 TESTING STRATEGY
Unit Tests:
- [Test scenario 1]

Integration Tests:
- [Test scenario 1]

E2E Tests:
- [Test scenario 1]

⚠️ RISKS & MITIGATION
1. Risk: [Description]
   Impact: [High/Medium/Low]
   Mitigation: [Strategy]

📊 EFFORT ESTIMATION
Complexity: [Low/Medium/High]
Estimated Effort: [Story points or time]
Dependencies: [List dependencies]
```

## Success Criteria

- ✅ Technical approach clearly defined
- ✅ Architecture impact assessed
- ✅ Data model designed
- ✅ API interfaces specified
- ✅ Tasks broken down and estimated
- ✅ Testing strategy defined
- ✅ Risks identified with mitigation
- ✅ Ready for implementation planning
