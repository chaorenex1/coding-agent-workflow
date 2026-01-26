# Mermaid Diagrams Reference

## Table of Contents
1. [Flowchart](#flowchart)
2. [Sequence Diagram](#sequence-diagram)
3. [Entity Relationship Diagram](#entity-relationship-diagram)
4. [State Diagram](#state-diagram)
5. [Class Diagram](#class-diagram)
6. [User Journey](#user-journey)
7. [Gantt Chart](#gantt-chart)
8. [Pie Chart](#pie-chart)
9. [Mindmap](#mindmap)

---

## Flowchart

### Basic Syntax

```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Direction Indicators

| Code | Direction |
|------|-----------|
| `TD` | Top to Down |
| `DT` | Down to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

### Node Shapes

```mermaid
flowchart LR
    A[Rectangle]
    B([Rounded])
    C[(Cylinder/Database)]
    D{{Diamond/Decision}}
    E[/Parallelogram/IO/]
    F[[Subroutine/Process]]
    G((Circle))
    H>Asymmetric]
```

### Styling

```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]

    style A fill:#90EE90,stroke:#333,stroke-width:2px
    style B fill:#87CEEB,stroke:#333,stroke-width:2px
    style C fill:#FFB6C1,stroke:#333,stroke-width:2px
```

### Subgraphs (Swimlanes)

```mermaid
flowchart TD
    subgraph Frontend["Frontend Layer"]
        A[User Interface]
        B[Form Validation]
    end

    subgraph Backend["Backend Layer"]
        C[API Controller]
        D[Business Logic]
    end

    subgraph Database["Data Layer"]
        E[(Repository)]
        F[(Database)]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
```

### Business Process Example

```mermaid
flowchart TD
    START([Order Placed]) --> CHECK{Check Inventory}
    CHECK -->|In Stock| RESERVE[Reserve Items]
    CHECK -->|Out of Stock| NOTIFY[Notify Customer]
    NOTIFY --> END([End])

    RESERVE --> CALC[Calculate Total]
    CALC --> PAY{Payment}
    PAY -->|Success| CONFIRM[Confirm Order]
    PAY -->|Failed| RETRY[Retry Payment]

    RETRY -->|Max Attempts| CANCEL[Cancel Order]
    RETRY -->|Within Limit| PAY

    CONFIRM --> SHIP[Prepare Shipping]
    SHIP --> EMAIL[Send Confirmation Email]
    EMAIL --> END
```

---

## Sequence Diagram

### Basic Syntax

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Service
    participant DB

    User->>API: Request
    API->>Service: Call method
    Service->>DB: Query
    DB-->>Service: Result
    Service-->>API: Response
    API-->>User: Return
```

### Participants

| Syntax | Type |
|--------|------|
| `actor` | External actor |
| `participant` | Standard participant |
| `boundary` | System boundary |
| `control` | Controller |
| `entity` | Entity |
| `database` | Database |

### Message Types

```mermaid
sequenceDiagram
    participant A as Client
    participant B as Server

    A->>B: Sync Request
    B-->>A: Sync Response

    A->>B: Async Message
    A-xB: Lost Message

    A--xB: Reply without response
```

### Loops and Alternatives

```mermaid
sequenceDiagram
    actor User
    participant API

    User->>API: Login
    alt Valid Credentials
        API-->>User: Token
    else Invalid Credentials
        API-->>User: Error
    end

    loop Check Status
        User->>API: Status Check
        API-->>User: Status
    end

    par Parallel Actions
        API->>ServiceA: Process
        and
        API->>ServiceB: Log
    end
```

### Activation Boxes

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Service

    User->>API: Request
    activate API
    API->>Service: Process
    activate Service
    Service-->>API: Result
    deactivate Service
    API-->>User: Response
    deactivate API
```

### Complex Example: Order Processing

```mermaid
sequenceDiagram
    actor Customer
    participant OrderAPI
    participant InventoryService
    participant PaymentService
    participant ShippingService
    participant Database

    Customer->>OrderAPI: POST /orders
    activate OrderAPI

    OrderAPI->>InventoryService: Check availability
    activate InventoryService
    InventoryService->>Database: Query stock
    Database-->>InventoryService: Stock level
    InventoryService-->>OrderAPI: Available
    deactivate InventoryService

    alt Items Available
        OrderAPI->>InventoryService: Reserve items
        activate InventoryService
        InventoryService->>Database: Update stock
        InventoryService-->>OrderAPI: Reserved
        deactivate InventoryService

        OrderAPI->>PaymentService: Process payment
        activate PaymentService

        alt Payment Success
            PaymentService->>Database: Save transaction
            PaymentService-->>OrderAPI: Payment confirmed
            deactivate PaymentService

            OrderAPI->>Database: Create order
            OrderAPI->>ShippingService: Initiate shipping
            activate ShippingService
            ShippingService-->>OrderAPI: Shipment created
            deactivate ShippingService

            OrderAPI-->>Customer: 201 Created (Order #123)
        else Payment Failed
            PaymentService-->>OrderAPI: Payment declined
            deactivate PaymentService

            OrderAPI->>InventoryService: Release reservation
            OrderAPI-->>Customer: 402 Payment Required
        end
    else Items Not Available
        OrderAPI-->>Customer: 400 Out of Stock
    end

    deactivate OrderAPI
```

---

## Entity Relationship Diagram

### Basic Syntax

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "included in"

    USERS {
        int id PK
        string username
        string email
        timestamp created_at
    }

    ORDERS {
        int id PK
        int user_id FK
        decimal total
        string status
    }

    PRODUCTS {
        int id PK
        string name
        decimal price
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }
```

### Relationship Types

| Syntax | Cardinality | Description |
|--------|-------------|-------------|
| `\|\|--o{` | One-to-Many or Zero | Parent has many optional children |
| `\|\|--\|{` | One-to-Many | Parent has many required children |
| `\|\|--\|\|` | One-to-One | Exactly one related record |
| `o\|--o{` | Zero or One to Many or Zero |

### Advanced Example

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : "places"
    CUSTOMERS ||--o{ ADDRESSES : "has"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    PRODUCTS }o--\| CATEGORIES : "belongs to"
    ORDERS }o--\| PAYMENTS : "paid by"
    ORDERS }o--o{ SHIPMENTS : "shipped via"

    CUSTOMERS {
        bigint id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        boolean is_active
        timestamp created_at
    }

    ORDERS {
        bigint id PK
        bigint customer_id FK
        string order_number UK
        decimal subtotal
        decimal tax
        decimal total
        string status
        timestamp created_at
    }

    PRODUCTS {
        bigint id PK
        string name
        string description
        decimal price
        int stock_quantity
        boolean is_active
    }

    ORDER_ITEMS {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        int quantity
        decimal unit_price
        decimal subtotal
    }

    CATEGORIES {
        bigint id PK
        string name
        bigint parent_id FK
    }

    PAYMENTS {
        bigint id PK
        bigint order_id FK
        string provider
        string transaction_id
        decimal amount
        string status
        timestamp paid_at
    }
```

---

## State Diagram

### Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Start
    Processing --> Success: Complete
    Processing --> Failed: Error
    Success --> [*]
    Failed --> [*]
```

### Composite States

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Ready
        Ready --> Processing
        Processing --> Ready
        Processing --> Completed
        Completed --> [*]
    }

    Active --> [*]: Deactivate
```

### Order State Example

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create
    DRAFT --> PENDING: Submit
    PENDING --> CONFIRMED: Confirm
    PENDING --> CANCELLED: Cancel

    CONFIRMED --> PROCESSING: Process
    PROCESSING --> SHIPPED: Ship
    PROCESSING --> CANCELLED: Cancel

    SHIPPED --> DELIVERED: Deliver
    SHIPPED --> RETURNED: Return

    DELIVERED --> [*]
    CANCELLED --> [*]
    RETURNED --> [*]

    note right of PENDING: Waiting for confirmation
    note right of PROCESSING: Being prepared
    note right of SHIPPED: In transit
```

---

## Class Diagram

### Basic Syntax

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +eat()
        +sleep()
    }

    class Dog {
        +String breed
        +bark()
    }

    Animal <|-- Dog
```

### Relationships

| Symbol | Relationship |
|--------|--------------|
| `<|--` | Inheritance |
| `*--` | Composition |
| `o--` | Aggregation |
| `-->` | Association |
| `..>` | Dependency |

### Complete Example

```mermaid
classDiagram
    class User {
        -Long id
        -String username
        -String email
        -String password
        +User()
        +getEmail() String
        +updatePassword(String)
        +delete()
    }

    class Order {
        -Long id
        -LocalDate created
        -OrderStatus status
        -List~OrderItem~ items
        +Order()
        +addItem(OrderItem)
        +calculateTotal() BigDecimal
        +confirm()
        +cancel()
    }

    class OrderItem {
        -Long id
        -Product product
        -int quantity
        -BigDecimal unitPrice
        +OrderItem()
        +getSubtotal() BigDecimal
    }

    class Product {
        -Long id
        -String name
        -BigDecimal price
        -int stock
        +Product()
        +reduceStock(int)
        +isAvailable() boolean
    }

    class Payment {
        -Long id
        -BigDecimal amount
        -PaymentMethod method
        -PaymentStatus status
        +Payment()
        +process()
        +refund()
    }

    User "1" --> "*" Order : places
    Order "1" --> "*" OrderItem : contains
    Order "1" --> "0..1" Payment : paid by
    OrderItem "*" --> "1" Product : references
```

---

## User Journey

### Basic Syntax

```mermaid
journey
    title User Shopping Journey
    section Browse
      View Products: 5: User
      Search: 4: User
    section Purchase
      Add to Cart: 5: User
      Checkout: 3: User
      Payment: 2: User, Friction
    section Post-Purchase
      Confirmation: 5: User
      Tracking: 4: User
```

---

## Gantt Chart

### Project Timeline

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Design
    Requirements      :done,    des1, 2024-01-01, 2024-01-05
    Database Design   :done,    des2, 2024-01-06, 3d
    API Design        :active,  des3, 2024-01-09, 5d

    section Development
    Backend API       :         dev1, 2024-01-14, 10d
    Frontend UI       :         dev2, 2024-01-16, 12d
    Integration       :         dev3, 2024-01-28, 5d

    section Testing
    Unit Tests        :         test1, 2024-02-02, 5d
    Integration Tests :         test2, 2024-02-07, 5d
```

---

## Pie Chart

```mermaid
pie title Traffic Sources
    "Direct" : 350
    "Search" : 500
    "Social" : 200
    "Referral" : 150
```

---

## Mindmap

```mermaid
mindmap
    root((E-Commerce))
        Frontend
            React
            TailwindCSS
            Redux
        Backend
            API Gateway
            User Service
            Order Service
            Product Service
        Database
            PostgreSQL
            Redis Cache
        Infrastructure
            AWS
            Docker
            Kubernetes
```

---

## Best Practices

### Diagram Naming
- Use descriptive titles
- Keep node labels concise
- Use consistent terminology

### Complexity Management
- Split complex diagrams into multiple views
- Use subgraphs for grouping
- Apply layering (L-R, T-D)

### Styling
- Use colors purposefully (not randomly)
- Maintain consistent color scheme
- High contrast for readability

### Documentation
- Add notes for complex logic
- Include legends for symbols
- Document assumptions
