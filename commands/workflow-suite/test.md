---
description: Comprehensive test generation and execution with coverage analysis
argument-hint: [component|function|feature]
allowed-tools: Read, Write, Bash(npm:*), Bash(jest:*), Bash(pytest:*), Bash(python:*), Bash(node:*), Bash(find:*), Bash(grep:*)
---

# Test Generation and Execution Assistant

## Context

Target for testing: $ARGUMENTS

### Existing Tests
!`find . -type f \( -name "*.test.js" -o -name "*.test.ts" -o -name "*.spec.js" -o -name "*.spec.ts" -o -name "test_*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null`

### Test Coverage
!`grep -r "describe\|it\|test\|def test_" --include="*.test.js" --include="*.test.ts" --include="*.spec.js" --include="test_*.py" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | wc -l`

### Test Configuration
@jest.config.js
@pytest.ini
@package.json

## Test Case Derivation Framework

Follow this reasoning chain to derive test cases from code analysis:

1. **[Explore]** What does the code do?
   - Read target files, identify functions/classes
   - Analyze control flow (branches, loops, conditions)
   - Identify inputs, outputs, side effects
   - Output: Code Structure Map

2. **[Decompose]** What are the logical paths?
   - Map all execution paths (happy path + error paths)
   - Identify decision points and branches
   - Find boundary conditions in loops/comparisons
   - Output: Path Coverage Diagram

3. **[Derive]** What test cases are needed?
   - For each path: generate test case
   - For each boundary: generate edge case
   - For each error condition: generate negative test
   - Output: Test Case Matrix (Path → Test → Expected)

4. **[Prioritize]** What matters most?
   - Critical business logic → P0 (must have)
   - Error handling → P1 (high priority)
   - Edge cases → P2 (medium priority)
   - Output: Prioritized Test List

5. **[Validate]** Is coverage sufficient?
   - Check: All paths covered? All edges tested?
   - Identify gaps in test strategy
   - Output: Coverage Gap Analysis

### Reasoning Output → Next Stage
- Explore produces: Code structure → consumed by Decompose
- Decompose produces: Path diagram → consumed by Derive
- Derive produces: Test cases → consumed by Prioritize
- Prioritize produces: Test plan → consumed by Generate

## Your Task

Generate comprehensive tests for "$ARGUMENTS":

### 1. **Test Strategy Definition**

   **Test Pyramid:**
   - Unit Tests: [X]%
   - Integration Tests: [Y]%
   - E2E Tests: [Z]%

   **Coverage Goals:**
   - Minimum: 80%
   - Target: 90%+
   - Critical paths: 100%

### 2. **Test Case Identification**

   **Happy Path Tests:**
   - Normal input, expected output
   - Standard user flows
   - Common scenarios

   **Edge Case Tests:**
   - Boundary values (0, max, min)
   - Empty inputs
   - Null/undefined values
   - Large data sets
   - Special characters

   **Error Case Tests:**
   - Invalid inputs
   - Missing required fields
   - Type mismatches
   - Permission errors
   - Network failures
   - Database errors

   **State Transition Tests:**
   - Initial state
   - State changes
   - Final state validation

### 3. **Unit Test Generation**

   **JavaScript/TypeScript (Jest):**
   ```typescript
   import { functionName } from './module';

   describe('ComponentName', () => {
     describe('functionName', () => {
       it('should handle normal input correctly', () => {
         // Arrange
         const input = 'test';
         const expected = 'expected result';

         // Act
         const result = functionName(input);

         // Assert
         expect(result).toBe(expected);
       });

       it('should handle edge case: empty input', () => {
         expect(() => functionName('')).toThrow('Input cannot be empty');
       });

       it('should handle edge case: null input', () => {
         expect(() => functionName(null)).toThrow('Input cannot be null');
       });
     });
   });
   ```

   **Python (pytest):**
   ```python
   import pytest
   from module import function_name

   class TestComponentName:
       def test_normal_input(self):
           # Arrange
           input_data = 'test'
           expected = 'expected result'

           # Act
           result = function_name(input_data)

           # Assert
           assert result == expected

       def test_empty_input_raises_error(self):
           with pytest.raises(ValueError, match='Input cannot be empty'):
               function_name('')

       def test_none_input_raises_error(self):
           with pytest.raises(TypeError):
               function_name(None)
   ```

### 4. **Integration Test Generation**

   **API Integration Tests:**
   ```typescript
   describe('API Integration: User Registration', () => {
     let testServer;

     beforeAll(async () => {
       testServer = await createTestServer();
     });

     afterAll(async () => {
       await testServer.close();
     });

     it('should register user successfully', async () => {
       const userData = {
         email: 'test@example.com',
         password: 'SecurePass123'
       };

       const response = await request(testServer)
         .post('/api/users/register')
         .send(userData);

       expect(response.status).toBe(201);
       expect(response.body).toHaveProperty('userId');
       expect(response.body.email).toBe(userData.email);
     });

     it('should reject duplicate email', async () => {
       // Register first user
       await registerUser('test@example.com');

       // Try to register with same email
       const response = await request(testServer)
         .post('/api/users/register')
         .send({ email: 'test@example.com', password: 'Pass123' });

       expect(response.status).toBe(409);
       expect(response.body.error).toMatch(/already exists/i);
     });
   });
   ```

### 5. **Mock & Stub Strategy**

   **Mocking External Dependencies:**
   ```typescript
   import { DatabaseService } from './database';
   import { EmailService } from './email';

   jest.mock('./database');
   jest.mock('./email');

   describe('UserService', () => {
     let userService;
     let mockDb;
     let mockEmail;

     beforeEach(() => {
       mockDb = new DatabaseService() as jest.Mocked<DatabaseService>;
       mockEmail = new EmailService() as jest.Mocked<EmailService>;
       userService = new UserService(mockDb, mockEmail);
     });

     it('should send welcome email after user creation', async () => {
       mockDb.createUser.mockResolvedValue({ id: '123', email: 'test@example.com' });
       mockEmail.sendWelcome.mockResolvedValue(true);

       await userService.registerUser({ email: 'test@example.com' });

       expect(mockEmail.sendWelcome).toHaveBeenCalledWith('test@example.com');
     });
   });
   ```

### 6. **Test Data Management**

   **Test Fixtures:**
   ```typescript
   // fixtures/users.ts
   export const validUser = {
     email: 'test@example.com',
     name: 'Test User',
     password: 'SecurePass123'
   };

   export const invalidUsers = {
     missingEmail: { name: 'Test', password: 'Pass123' },
     invalidEmail: { email: 'invalid', password: 'Pass123' },
     weakPassword: { email: 'test@example.com', password: '123' }
   };
   ```

   **Test Database Setup:**
   ```typescript
   beforeEach(async () => {
     await cleanDatabase();
     await seedTestData();
   });

   afterEach(async () => {
     await cleanDatabase();
   });
   ```

### 7. **Assertion Patterns**

   **Value Assertions:**
   ```typescript
   expect(result).toBe(expected);
   expect(result).toEqual(expected);
   expect(result).toBeNull();
   expect(result).toBeDefined();
   expect(result).toBeTruthy();
   ```

   **Object Assertions:**
   ```typescript
   expect(user).toHaveProperty('id');
   expect(user).toMatchObject({ email: 'test@example.com' });
   expect(response).toHaveProperty('data.user.id');
   ```

   **Array Assertions:**
   ```typescript
   expect(users).toHaveLength(3);
   expect(users).toContain('admin');
   expect(users).toEqual(expect.arrayContaining(['user1', 'user2']));
   ```

   **Error Assertions:**
   ```typescript
   expect(() => riskyFunction()).toThrow();
   expect(() => riskyFunction()).toThrow('Specific error message');
   expect(async () => await asyncFunction()).rejects.toThrow();
   ```

### 8. **Coverage Analysis**

   **Current Coverage:**
   - Statements: [X]%
   - Branches: [Y]%
   - Functions: [Z]%
   - Lines: [W]%

   **Uncovered Code:**
   - [File:Line]: [Description]
   - [File:Line]: [Description]

   **Coverage Improvement Plan:**
   1. Add tests for [uncovered area 1]
   2. Add tests for [uncovered area 2]

### 9. **Test Execution Plan**

   **Run Commands:**
   ```bash
   # Run all tests
   npm test
   # or
   pytest

   # Run specific test file
   npm test -- path/to/test.spec.ts
   # or
   pytest tests/test_module.py

   # Run with coverage
   npm test -- --coverage
   # or
   pytest --cov=src --cov-report=html

   # Run in watch mode
   npm test -- --watch
   ```

### 10. **Continuous Testing Strategy**

   **Pre-commit Tests:**
   - Run affected tests
   - Check coverage threshold
   - Lint test files

   **CI/CD Integration:**
   - Run full test suite
   - Generate coverage reports
   - Fail build if coverage drops
   - Upload coverage to service

## Output Format

```
🧪 DERIVATION PROCESS
Code Analyzed:
- [File]: [Functions/Classes identified]

Execution Paths Mapped:
- Path 1: [Description] → Test Case: [Name]
- Path 2: [Description] → Test Case: [Name]

Coverage Gaps Identified:
- [Gap 1]: [Missing test]

🧪 TEST STRATEGY

Test Pyramid:
- Unit Tests: [X]%
- Integration Tests: [Y]%
- E2E Tests: [Z]%

Coverage Goals:
- Target: [X]%
- Current: [Y]%
- Gap: [Z]%

📋 TEST CASES

Happy Path:
1. [Test case 1]
2. [Test case 2]

Edge Cases:
1. [Edge case 1]
2. [Edge case 2]

Error Cases:
1. [Error case 1]
2. [Error case 2]

📝 GENERATED TESTS

Test File: [test-file-path]

```[language]
[Complete test code]
```

Test Count: [X] tests
Coverage: [Y]%

🎯 EXECUTION PLAN

Commands:
```bash
[Test run commands]
```

Expected Results:
- All tests: PASS
- Coverage: ≥ [X]%

📊 COVERAGE ANALYSIS

Current Coverage:
- Statements: [X]%
- Branches: [Y]%
- Functions: [Z]%

Uncovered Areas:
- [File:Line]: [Why uncovered]

Improvement Plan:
1. [Add test for X]
2. [Add test for Y]

✅ SUCCESS CRITERIA
- [ ] All tests pass
- [ ] Coverage ≥ [X]%
- [ ] No skipped tests
- [ ] All edge cases covered
- [ ] All error paths tested
```

## Success Criteria

- ✅ Comprehensive test cases identified
- ✅ Tests generated for all scenarios
- ✅ Mocking strategy defined
- ✅ Coverage goals met
- ✅ Tests executable and passing
- ✅ CI/CD integration ready
- ✅ Test maintenance documented
