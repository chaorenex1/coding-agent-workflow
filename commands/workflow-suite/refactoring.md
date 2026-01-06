---
description: Code refactoring analysis and implementation with quality improvement focus
argument-hint: [file-path|component|function]
allowed-tools: Read, Write, Edit, Bash(find:*), Bash(grep:*), Bash(wc:*)
---

# Code Refactoring Assistant

## Context

Code to refactor: $ARGUMENTS

### Code Complexity Analysis
!`find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -exec wc -l {} + 2>/dev/null | sort -rn | head -10`

### Code Duplication Detection
!`grep -r "function\|class\|def " --include="*.js" --include="*.ts" --include="*.py" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | wc -l`

## Your Task

Analyze and refactor "$ARGUMENTS" to improve code quality:

### 1. **Code Quality Assessment**

   **Current Issues:**
   - Code smells identified
   - Complexity metrics (cyclomatic complexity)
   - Duplication analysis
   - Maintainability index
   - Technical debt assessment

   **Quality Dimensions:**
   - Readability: [Score/10]
   - Maintainability: [Score/10]
   - Testability: [Score/10]
   - Performance: [Score/10]
   - Security: [Score/10]

### 2. **Refactoring Opportunities**

   **Code Smells:**
   - [ ] Long methods (>50 lines)
   - [ ] Large classes (>300 lines)
   - [ ] Duplicate code
   - [ ] Long parameter lists (>4 params)
   - [ ] Deep nesting (>3 levels)
   - [ ] Complex conditionals
   - [ ] Magic numbers/strings
   - [ ] Dead code
   - [ ] Inconsistent naming

   **Design Issues:**
   - [ ] Violation of Single Responsibility Principle
   - [ ] Tight coupling
   - [ ] Low cohesion
   - [ ] Missing abstractions
   - [ ] Inappropriate intimacy

### 3. **Refactoring Strategy**

   **Pattern Application:**
   - Extract Method
   - Extract Class
   - Introduce Parameter Object
   - Replace Conditional with Polymorphism
   - Strategy Pattern
   - Factory Pattern

   **Specific Refactorings:**
   1. [Refactoring 1]: [Description]
   2. [Refactoring 2]: [Description]

### 4. **Detailed Refactoring Plan**

   **Phase 1: Extract Methods**
   ```typescript
   // BEFORE
   function processOrder(order) {
     // 100 lines of complex logic
   }

   // AFTER
   function processOrder(order) {
     validateOrder(order);
     calculateTotal(order);
     applyDiscounts(order);
     processPayment(order);
     sendConfirmation(order);
   }

   function validateOrder(order) { ... }
   function calculateTotal(order) { ... }
   ```

   **Phase 2: Extract Classes**
   ```typescript
   // BEFORE
   class User {
     // User properties
     // Order management
     // Payment processing
     // Email notifications
   }

   // AFTER
   class User { /* User-specific logic */ }
   class OrderManager { /* Order logic */ }
   class PaymentProcessor { /* Payment logic */ }
   class NotificationService { /* Email logic */ }
   ```

   **Phase 3: Improve Naming**
   ```typescript
   // BEFORE
   function calc(a, b) { return a * b * 0.1; }
   const x = getData();

   // AFTER
   function calculateDiscount(price, quantity) {
     const DISCOUNT_RATE = 0.1;
     return price * quantity * DISCOUNT_RATE;
   }
   const userOrders = getUserOrders();
   ```

### 5. **Design Pattern Application**

   **Strategy Pattern (Replace Conditionals):**
   ```typescript
   // BEFORE
   function calculateShipping(type, weight) {
     if (type === 'standard') {
       return weight * 5;
     } else if (type === 'express') {
       return weight * 10;
     } else if (type === 'overnight') {
       return weight * 20;
     }
   }

   // AFTER
   interface ShippingStrategy {
     calculate(weight: number): number;
   }

   class StandardShipping implements ShippingStrategy {
     calculate(weight: number) { return weight * 5; }
   }

   class ExpressShipping implements ShippingStrategy {
     calculate(weight: number) { return weight * 10; }
   }
   ```

### 6. **Complexity Reduction**

   **Reduce Nesting:**
   ```typescript
   // BEFORE (Nested)
   function process(data) {
     if (data) {
       if (data.valid) {
         if (data.items.length > 0) {
           // Process logic
         }
       }
     }
   }

   // AFTER (Guard Clauses)
   function process(data) {
     if (!data) return;
     if (!data.valid) return;
     if (data.items.length === 0) return;

     // Process logic
   }
   ```

   **Simplify Conditionals:**
   ```typescript
   // BEFORE
   if (user.age >= 18 && user.hasLicense === true && user.hasInsurance === true) {
     allowDriving();
   }

   // AFTER
   function canDrive(user) {
     return user.age >= 18 && user.hasLicense && user.hasInsurance;
   }

   if (canDrive(user)) {
     allowDriving();
   }
   ```

### 7. **Eliminate Code Duplication**

   **Extract Common Logic:**
   ```typescript
   // BEFORE (Duplicated)
   function processUser(user) {
     validateUser(user);
     user.processed = true;
     saveUser(user);
   }

   function processAdmin(admin) {
     validateUser(admin);
     admin.processed = true;
     saveUser(admin);
   }

   // AFTER (DRY)
   function processAccount(account) {
     validateUser(account);
     account.processed = true;
     saveUser(account);
   }
   ```

### 8. **Improve Testability**

   **Dependency Injection:**
   ```typescript
   // BEFORE (Hard to test)
   class OrderService {
     process() {
       const db = new Database();
       const payment = new PaymentGateway();
       // Logic using db and payment
     }
   }

   // AFTER (Easy to test)
   class OrderService {
     constructor(
       private db: Database,
       private payment: PaymentGateway
     ) {}

     process() {
       // Logic using this.db and this.payment
     }
   }
   ```

### 9. **Error Handling Improvement**

   ```typescript
   // BEFORE
   function getUser(id) {
     const user = db.find(id);
     return user;
   }

   // AFTER
   function getUser(id) {
     if (!id) {
       throw new ValidationError('User ID is required');
     }

     const user = db.find(id);

     if (!user) {
       throw new NotFoundError(`User ${id} not found`);
     }

     return user;
   }
   ```

### 10. **Documentation & Comments**

   ```typescript
   // BEFORE
   // Calculate x
   function calc(a, b, c) {
     return a * b + c * 0.1;
   }

   // AFTER (Self-documenting code + JSDoc)
   /**
    * Calculates the total price including tax
    * @param basePrice - The base price of the item
    * @param quantity - Number of items
    * @param taxRate - Tax rate (default 0.1 for 10%)
    * @returns Total price including tax
    */
   function calculateTotalPrice(
     basePrice: number,
     quantity: number,
     taxRate: number = 0.1
   ): number {
     return basePrice * quantity * (1 + taxRate);
   }
   ```

### 11. **Testing Strategy**

   **Test Coverage:**
   - Before: [X]%
   - After: [Y]%

   **New Tests:**
   - Unit tests for extracted functions
   - Integration tests for refactored modules
   - Regression tests to ensure no breaking changes

### 12. **Migration Plan**

   **Step-by-Step Process:**
   1. [ ] Write comprehensive tests for current code
   2. [ ] Refactor in small increments
   3. [ ] Run tests after each change
   4. [ ] Review and validate
   5. [ ] Deploy incrementally

## Output Format

```
🔍 CODE QUALITY ASSESSMENT

Current State:
- Readability: [X]/10
- Maintainability: [X]/10
- Complexity: [High/Medium/Low]
- Technical Debt: [X] issues

Code Smells Found:
- [Smell 1]: [Location]
- [Smell 2]: [Location]

🎯 REFACTORING PLAN

Priority 1 (Critical):
1. [Refactoring 1]
   - Issue: [Problem description]
   - Solution: [Approach]
   - Impact: [Benefit]

Priority 2 (Important):
1. [Refactoring 1]
   ...

Priority 3 (Nice-to-have):
1. [Refactoring 1]
   ...

📝 CODE TRANSFORMATIONS

Transformation 1: [Name]
BEFORE:
```[language]
[Original code]
```

AFTER:
```[language]
[Refactored code]
```

IMPROVEMENT:
- Lines: [X] → [Y] ([Z]% reduction)
- Complexity: [X] → [Y]
- Maintainability: +[Z]%

🧪 TESTING STRATEGY
- Tests to add: [X]
- Coverage increase: [X]% → [Y]%
- Regression tests: [List]

📋 IMPLEMENTATION CHECKLIST
Phase 1:
- [ ] Write tests for current code
- [ ] [Refactoring task 1]

Phase 2:
- [ ] [Refactoring task 2]
- [ ] Run full test suite

✅ EXPECTED BENEFITS
- Readability: [Improvement]
- Maintainability: [Improvement]
- Testability: [Improvement]
- Performance: [Impact if any]

⚠️ RISKS & MITIGATION
Risk: [Risk description]
Mitigation: [How to address]
```

## Success Criteria

- ✅ Code quality issues identified
- ✅ Refactoring plan defined
- ✅ Code transformations specified
- ✅ Testing strategy established
- ✅ Benefits clearly articulated
- ✅ Risks identified and mitigated
- ✅ Implementation safe and incremental
