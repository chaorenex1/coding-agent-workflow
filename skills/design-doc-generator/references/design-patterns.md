# Design Patterns Reference

## Table of Contents
1. [Architectural Patterns](#architectural-patterns)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Communication Patterns](#communication-patterns)
4. [Data Patterns](#data-patterns)
5. [Integration Patterns](#integration-patterns)

---

## Architectural Patterns

### Layered Architecture

**Description:** Organizes code into horizontal layers with clear dependencies.

```mermaid
flowchart TB
    subgraph "Presentation Layer"
        A[Controllers]
        B[Views]
    end

    subgraph "Business Logic Layer"
        C[Services]
        D[Domain Models]
    end

    subgraph "Data Access Layer"
        E[Repositories]
        F[ORM]
    end

    subgraph "Database"
        G[(Tables)]
    end

    A --> C
    B --> C
    C --> E
    E --> F
    F --> G
```

**Layers:**
1. **Presentation Layer** - UI, API controllers
2. **Business Logic Layer** - Services, business rules
3. **Data Access Layer** - Repositories, ORM

**When to Use:**
- Traditional CRUD applications
- Small to medium teams
- Clear separation of concerns needed

**Trade-offs:**
- ✅ Simple to understand
- ✅ Easy to test
- ❌ Can become rigid
- ❌ Changes may cascade through layers

---

### Hexagonal Architecture (Ports and Adapters)

**Description:** Business logic at the center, surrounded by adapters for external concerns.

```mermaid
flowchart
    subgraph "Adapters - Primary (Driving)"
        WEB[Web Adapter]
        CLI[CLI Adapter]
        TEST[Test Adapter]
    end

    subgraph "Application Core"
        PORTS[Ports / Interfaces]
        DOMAIN[Domain Logic]
        MODELS[Domain Models]
    end

    subgraph "Adapters - Secondary (Driven)"
        DB[Database Adapter]
        EXT[External API Adapter]
        MQ[Message Queue Adapter]
    end

    WEB --> PORTS
    CLI --> PORTS
    TEST --> PORTS

    PORTS --> DOMAIN
    PORTS --> MODELS

    PORTS --> DB
    PORTS --> EXT
    PORTS --> MQ
```

**Key Concepts:**
- **Ports** - Interfaces defined by the core
- **Adapters** - Implementations of ports
- **Core** - Pure business logic, no framework dependencies

**When to Use:**
- Complex business domains
- Multiple external integrations
- Testability is critical

**Trade-offs:**
- ✅ Highly testable
- ✅ Flexible technology choices
- ✅ Business logic isolated
- ❌ More initial complexity
- ❌ More files/interfaces

---

### Clean Architecture

**Description:** Concentric circles of dependency, with business rules at the center.

```mermaid
flowchart
    subgraph "Interface Adapters"
        CTRL[Controllers]
        PRES[Presenters]
        GATE[Gateways]
    end

    subgraph "Use Cases"
        UC1[Use Case 1]
        UC2[Use Case 2]
    end

    subgraph "Entities"
        E1[Entity 1]
        E2[Entity 2]
    end

    subgraph "Frameworks & Drivers"
        DB[(DB)]
        WEB[Web]
        DEV[Devices]
    end

    CTRL --> UC1
    PRES --> UC1
    UC1 --> E1
    UC2 --> E1

    GATE --> DB
    WEB --> CTRL
```

**Dependency Rule:** Dependencies point inward only.

**Layers (outer to inner):**
1. **Frameworks & Drivers** - External tools
2. **Interface Adapters** - Convert data formats
3. **Use Cases** - Application-specific business rules
4. **Entities** - Enterprise-wide business rules

**When to Use:**
- Enterprise applications
- Long-lived projects
- Multiple teams

---

### Microservices Architecture

**Description:** Decomposes application into small, independent services.

```mermaid
flowchart LR
    subgraph "API Gateway"
        GW[Gateway]
    end

    subgraph "Services"
        USER[User Service]
        ORDER[Order Service]
        PRODUCT[Product Service]
        PAYMENT[Payment Service]
        NOTIF[Notification Service]
    end

    subgraph "Infrastructure"
        DB1[(User DB)]
        DB2[(Order DB)]
        DB3[(Product DB)]
        CACHE[(Redis)]
        MQ[(Message Queue)]
    end

    GW --> USER
    GW --> ORDER
    GW --> PRODUCT

    ORDER --> USER
    ORDER --> PRODUCT
    ORDER --> PAYMENT

    PAYMENT --> MQ
    NOTIF --> MQ

    USER --> DB1
    ORDER --> DB2
    PRODUCT --> DB3
    PRODUCT --> CACHE
```

**Key Characteristics:**
- Single responsibility per service
- Independent deployment
- Own database per service
- Communication via API or events

**When to Use:**
- Large applications with clear domains
- Multiple teams working independently
- Need for independent scaling

**Trade-offs:**
- ✅ Independent deployment/scaling
- ✅ Technology diversity
- ✅ Fault isolation
- ❌ Distributed complexity
- ❌ Data consistency challenges
- ❌ Operational overhead

---

## Layer Responsibilities

### Presentation Layer

**Responsibilities:**
- Handle HTTP requests/responses
- Input validation (syntactic)
- Response formatting
- Authentication (token validation)

**Should NOT:**
- Contain business logic
- Access database directly
- Make external API calls

**Example:**
```typescript
// ✅ Good: Thin controller
@Post('/users')
async createUser(@Body() dto: CreateUserDTO) {
    return this.userService.create(dto);
}

// ❌ Bad: Business logic in controller
@Post('/users')
async createUser(@Body() dto: CreateUserDTO) {
    if (dto.age < 18) {
        throw new Error('Too young');
    }
    // ... more logic
}
```

---

### Business Logic Layer

**Responsibilities:**
- Implement business rules
- Coordinate workflows
- Validate business constraints
- Manage transactions

**Should NOT:**
- Handle HTTP concerns
- Know about presentation format

**Example:**
```typescript
// ✅ Good: Business logic in service
async createOrder(dto: CreateOrderDTO) {
    // Business rule: Check user eligibility
    const user = await this.getUser(dto.userId);
    if (!user.isVerified) {
        throw new NotEligibleError();
    }

    // Business rule: Validate inventory
    await this.validateInventory(dto.items);

    // Business rule: Calculate discounts
    const total = this.calculateTotal(dto);

    return this.orderRepository.save(order);
}
```

---

### Data Access Layer

**Responsibilities:**
- Database operations
- Query optimization
- Mapping to domain models
- Transaction management

**Should NOT:**
- Contain business logic
- Validate business rules

---

## Communication Patterns

### Synchronous (Request/Response)

```mermaid
sequenceDiagram
    participant Client
    participant ServiceA
    participant ServiceB

    Client->>ServiceA: Request
    ServiceA->>ServiceB: Request
    ServiceB-->>ServiceA: Response
    ServiceA-->>Client: Response
```

**Use When:**
- Immediate response needed
- Data consistency required
- Simple call chain

**Risks:**
- Cascading failures
- Latency accumulation
- Tight coupling

---

### Asynchronous (Event-Driven)

```mermaid
sequenceDiagram
    participant Producer
    participant MQ as Message Queue
    participant Consumer

    Producer->>MQ: Publish Event
    Producer--xProducer: Continue (non-blocking)
    MQ->>Consumer: Deliver Event
    Consumer->>Consumer: Process
```

**Use When:**
- Immediate response not needed
- Background processing
- Decoupling required
- Broadcast notifications

**Patterns:**

| Pattern | Description |
|---------|-------------|
| **Event Notification** | Fire and forget |
| **Event-Carried State Transfer** | Event contains all needed data |
| **Event Sourcing** | Store all events as log |
| **CQRS** | Separate read/write models |

---

### Saga Pattern (Distributed Transactions)

```mermaid
sequenceDiagram
    participant Orchestrator
    participant ServiceA
    participant ServiceB
    participant ServiceC

    Orchestrator->>ServiceA: Execute step 1
    ServiceA-->>Orchestrator: Result 1

    Orchestrator->>ServiceB: Execute step 2
    ServiceB-->>Orchestrator: Result 2

    Orchestrator->>ServiceC: Execute step 3
    ServiceC-->>Orchestrator: FAILURE

    Orchestrator->>ServiceB: Compensate step 2
    Orchestrator->>ServiceA: Compensate step 1
```

**Types:**
- **Choreography** - Services communicate directly via events
- **Orchestration** - Central coordinator manages saga

---

## Data Patterns

### Repository Pattern

**Description:** Abstract data access behind interface.

```typescript
interface IUserRepository {
    findById(id: number): Promise<User | null>;
    findByEmail(email: string): Promise<User | null>;
    save(user: User): Promise<User>;
    delete(id: number): Promise<void>;
}

class SQLUserRepository implements IUserRepository {
    async findById(id: number) {
        return this.db.query('SELECT * FROM users WHERE id = ?', [id]);
    }
}
```

**Benefits:**
- Swappable data source
- Testable (easy to mock)
- Centralized query logic

---

### Unit of Work Pattern

**Description:** Track changes and commit as transaction.

```typescript
class UnitOfWork {
    private readonly repositories = new Map();
    private readonly newEntities = [];
    private readonly modifiedEntities = [];
    private readonly deletedEntities = [];

    registerNew(entity) {
        this.newEntities.push(entity);
    }

    registerDirty(entity) {
        this.modifiedEntities.push(entity);
    }

    registerDeleted(entity) {
        this.deletedEntities.push(entity);
    }

    async commit() {
        await this.beginTransaction();
        try {
            await this.insertNew();
            await this.updateModified();
            await this.deleteDeleted();
            await this.commitTransaction();
        } catch (e) {
            await this.rollbackTransaction();
            throw e;
        }
    }
}
```

---

### CQRS (Command Query Responsibility Segregation)

**Description:** Separate models for reads and writes.

```mermaid
flowchart LR
    subgraph "Write Side"
        CMD[Command]
        WS[Write Model]
        E[(Event Store)]
    end

    subgraph "Read Side"
        ES[Event Handler]
        RS[Read Model]
        DB[(Read DB)]
    end

    CMD --> WS
    WS --> E
    E --> ES
    ES --> RS
    RS --> DB
```

**When to Use:**
- Complex read queries
- High read/write ratio
- Different data shapes for read/write

---

## Integration Patterns

### API Gateway Pattern

```mermaid
flowchart
    Client[Client]
    GW[API Gateway]

    subgraph "Services"
        S1[Service 1]
        S2[Service 2]
        S3[Service 3]
    end

    Client --> GW
    GW --> S1
    GW --> S2
    GW --> S3

    GW -.-> AUTH[Authentication]
    GW -.-> RATE[Rate Limiting]
    GW -.-> LOG[Logging]
```

**Responsibilities:**
- Request routing
- Authentication/authorization
- Rate limiting
- Response aggregation
- Protocol translation

---

### Circuit Breaker Pattern

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Failure threshold reached
    Open --> HalfOpen: Timeout
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure
    Open --> Closed: Reset timeout
```

**States:**
- **Closed** - Normal operation, requests pass through
- **Open** - Failures detected, requests fail immediately
- **HalfOpen** - Testing if service has recovered

---

### Bulkhead Pattern

**Description:** Isolate resources to prevent cascading failures.

```mermaid
flowchart
    subgraph "Thread Pool A"
        T1A[Thread 1]
        T2A[Thread 2]
        T3A[Thread 3]
    end

    subgraph "Thread Pool B"
        T1B[Thread 1]
        T2B[Thread 2]
        T3B[Thread 3]
    end

    REQ1[Request Type A] --> T1A
    REQ2[Request Type A] --> T2A

    REQ3[Request Type B] --> T1B
    REQ4[Request Type B] --> T2B
```

**Benefits:**
- Resource isolation
- Priority management
- Fault containment
