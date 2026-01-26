# E-Commerce Platform - Technical Design Document

## Project Overview

**Project Name:** ShopHub E-Commerce Platform
**Version:** 1.0.0
**Last Updated:** 2024-01-15
**Author:** Architecture Team

---

## 1. System Architecture

### 1.1 Architecture Overview

```mermaid
flowchart TB
    subgraph "Client Layer"
        WEB[Web App]
        MOBILE[Mobile App]
    end

    subgraph "API Gateway"
        GATEWAY[API Gateway<br/>Kong/NGINX]
    end

    subgraph "Microservices"
        USER[User Service]
        PRODUCT[Product Service]
        ORDER[Order Service]
        PAYMENT[Payment Service]
        NOTIF[Notification Service]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL)]
        REDIS[(Redis)]
        MQ[(RabbitMQ)]
        ES[(Elasticsearch)]
    end

    subgraph "External Services"
        STRIPE[Stripe]
        SHIP[Shipping API]
        EMAIL[SendGrid]
    end

    WEB --> GATEWAY
    MOBILE --> GATEWAY

    GATEWAY --> USER
    GATEWAY --> PRODUCT
    GATEWAY --> ORDER
    GATEWAY --> PAYMENT

    USER --> PG
    USER --> REDIS
    PRODUCT --> PG
    PRODUCT --> REDIS
    PRODUCT --> ES
    ORDER --> PG
    ORDER --> REDIS
    ORDER --> MQ
    PAYMENT --> PG
    PAYMENT --> STRIPE

    NOTIF --> MQ
    NOTIF --> EMAIL
```

### 1.2 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, TailwindCSS |
| **Mobile** | React Native |
| **API Gateway** | Kong |
| **Backend** | Node.js, NestJS, TypeScript |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Message Queue** | RabbitMQ |
| **Search** | Elasticsearch 8 |
| **Container** | Docker, Kubernetes |
| **CI/CD** | GitHub Actions, ArgoCD |

---

## 2. Database Design

### 2.1 Entity Relationship Diagram

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : "places"
    CUSTOMERS ||--o{ ADDRESSES : "has"
    CUSTOMERS ||--o{ PAYMENT_METHODS : "owns"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    PRODUCTS }o--\| CATEGORIES : "belongs to"
    PRODUCTS ||--o{ PRODUCT_IMAGES : "has"
    ORDERS }o--o{ PAYMENTS : "paid by"
    ORDERS }o--o{ SHIPMENTS : "shipped via"

    CUSTOMERS {
        bigint id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        boolean email_verified
        timestamp created_at
        timestamp updated_at
    }

    ORDERS {
        bigint id PK
        bigint customer_id FK
        string order_number UK
        string status
        decimal subtotal
        decimal tax
        decimal shipping
        decimal total
        timestamp created_at
        timestamp updated_at
    }

    PRODUCTS {
        bigint id PK
        string name
        text description
        decimal price
        integer stock_quantity
        bigint category_id FK
        boolean is_active
        timestamp created_at
    }

    ORDER_ITEMS {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        integer quantity
        decimal unit_price
        decimal subtotal
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

    SHIPMENTS {
        bigint id PK
        bigint order_id FK
        string carrier
        string tracking_number
        string status
        timestamp shipped_at
        timestamp delivered_at
    }
```

### 2.2 Table Definitions

#### Customers Table

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `bigint` | NO | `AUTO_INCREMENT` | Primary key |
| `email` | `varchar(255)` | NO | - | Unique email |
| `password_hash` | `varchar(255)` | NO | - | Bcrypt hash |
| `first_name` | `varchar(100)` | YES | `NULL` | First name |
| `last_name` | `varchar(100)` | YES | `NULL` | Last name |
| `phone` | `varchar(20)` | YES | `NULL` | Phone number |
| `email_verified` | `boolean` | NO | `false` | Email verified |
| `is_active` | `boolean` | NO | `true` | Account status |
| `created_at` | `timestamp` | NO | `NOW()` | Creation time |
| `updated_at` | `timestamp` | NO | `NOW()` | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_email (email)`
- `INDEX idx_active (is_active)`

#### Products Table

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `bigint` | NO | `AUTO_INCREMENT` | Primary key |
| `sku` | `varchar(50)` | NO | - | Stock keeping unit |
| `name` | `varchar(255)` | NO | - | Product name |
| `description` | `text` | YES | `NULL` | Description |
| `price` | `decimal(10,2)` | NO | `0.00` | Unit price |
| `compare_at_price` | `decimal(10,2)` | YES | `NULL` | Original price |
| `cost_price` | `decimal(10,2)` | YES | `NULL` | Cost price |
| `stock_quantity` | `integer` | NO | `0` | Available stock |
| `low_stock_threshold` | `integer` | NO | `10` | Low stock alert |
| `category_id` | `bigint` | YES | `NULL` | Category FK |
| `is_active` | `boolean` | NO | `true` | Active status |
| `weight` | `decimal(8,2)` | YES | `NULL` | Weight in kg |
| `created_at` | `timestamp` | NO | `NOW()` | Creation time |
| `updated_at` | `timestamp` | NO | `NOW()` | Last update |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_sku (sku)`
- `INDEX idx_category (category_id)`
- `INDEX idx_active_stock (is_active, stock_quantity)`

---

## 3. API Design

### 3.1 RESTful Endpoints

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register new customer |
| `POST` | `/api/v1/auth/login` | Customer login |
| `POST` | `/api/v1/auth/logout` | Customer logout |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset |
| `POST` | `/api/v1/auth/reset-password` | Reset password |

#### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/products` | List products (paginated) |
| `GET` | `/api/v1/products/{id}` | Get product details |
| `GET` | `/api/v1/products/search` | Search products |
| `GET` | `/api/v1/categories` | List categories |
| `GET` | `/api/v1/categories/{id}/products` | Products by category |

#### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/orders` | Create order |
| `GET` | `/api/v1/orders` | List customer orders |
| `GET` | `/api/v1/orders/{id}` | Get order details |
| `PATCH` | `/api/v1/orders/{id}/cancel` | Cancel order |

### 3.2 Example API Contract

#### Create Order

**Request:**
```http
POST /api/v1/orders
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

```json
{
  "items": [
    {
      "product_id": 123,
      "quantity": 2
    },
    {
      "product_id": 456,
      "quantity": 1
    }
  ],
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address_line1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1 234 567 8900"
  },
  "billing_address": {
    "same_as_shipping": true
  },
  "shipping_method": "standard",
  "payment_method_id": "pm_abc123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 9999,
    "order_number": "ORD-2024-001234",
    "customer_id": 123,
    "status": "pending",
    "items": [
      {
        "id": 1,
        "product": {
          "id": 123,
          "name": "Wireless Headphones",
          "sku": "WH-001"
        },
        "quantity": 2,
        "unit_price": 79.99,
        "subtotal": 159.98
      }
    ],
    "subtotal": 209.97,
    "tax": 16.80,
    "shipping": 5.99,
    "total": 232.76,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## 4. Business Process Flows

### 4.1 Order Processing Flow

```mermaid
flowchart TD
    START([Customer Places Order]) --> VALIDATE{Validate Input}
    VALIDATE -->|Invalid| ERROR1[Return Error]
    VALIDATE -->|Valid| CHECK_STOCK{Check Inventory}
    CHECK_STOCK -->|Out of Stock| ERROR2[Return Error]
    CHECK_STOCK -->|Available| RESERVE[Reserve Items]

    RESERVE --> CALC[Calculate Totals]
    CALC --> PAY{Process Payment}
    PAY -->|Failed| RELEASE[Release Stock]
    PAY -->|Success| CREATE_ORDER[Create Order Record]

    CREATE_ORDER --> CONFIRM[Update Order Status]
    CONFIRM --> NOTIFY[Send Confirmation Email]
    NOTIFY --> WAREHOUSE[Notify Warehouse]

    WAREHOUSE --> PICK[Pick Items]
    PICK --> PACK[Pack Items]
    PACK --> SHIP[Generate Label]
    SHIP --> TRACK[Send Tracking Info]
    TRACK --> COMPLETE([Order Complete])

    RELEASE --> ERROR1
    ERROR1 --> END([End])
    COMPLETE --> END
```

### 4.2 Order State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create
    DRAFT --> PENDING: Submit
    PENDING --> CONFIRMED: Payment Success
    PENDING --> CANCELLED: Payment Failed
    PENDING --> CANCELLED: Customer Cancel

    CONFIRMED --> PROCESSING: Warehouse Processing
    CONFIRMED --> CANCELLED: Cancel Requested

    PROCESSING --> SHIPPED: Ship
    PROCESSING --> CANCELLED: Before Shipment

    SHIPPED --> DELIVERED: Confirm Delivery
    SHIPPED --> RETURN_REQUESTED: Return Request

    DELIVERED --> [*]
    RETURN_REQUESTED --> RETURNED: Process Return
    CANCELLED --> [*]
    RETURNED --> [*]

    note right of PENDING: Payment processing
    note right of CONFIRMED: Stock reserved
    note right of PROCESSING: Picking & packing
    note right of SHIPPED: In transit
```

---

## 5. Data Flow Diagrams

### 5.1 Context Diagram (Level 0 DFD)

```mermaid
flowchart LR
    Customer((Customer))
    Admin((Admin))
    System([ShopHub System])
    Stripe[Stripe Payment]
    Shipper[Shipping Carrier]
    Email[Email Service]

    Customer -->|Browse, Order| System
    System -->|Order Confirmation| Customer

    Admin -->|Manage Products| System
    System -->|Reports| Admin

    System -->|Charge| Stripe
    Stripe -->|Payment Result| System

    System -->|Ship Request| Shipper
    Shipper -->|Tracking Info| System

    System -->|Send Email| Email
```

### 5.2 Order Process DFD (Level 1)

```mermaid
flowchart TB
    subgraph "Input"
        Customer((Customer))
    end

    subgraph "Processes"
        P1[1.0 Validate Order]
        P2[2.0 Check Inventory]
        P3[3.0 Process Payment]
        P4[4.0 Create Order]
        P5[5.0 Update Inventory]
        P6[6.0 Send Notification]
    end

    subgraph "Data Store"
        D1[(Products DB)]
        D2[(Customers DB)]
        D3[(Orders DB)]
        D4[(Payments DB)]
    end

    subgraph "External"
        Stripe((Stripe))
        Email((Email))
    end

    Customer -->|Order Request| P1
    P1 --> P2
    P2 -->|Product Info| D1
    P2 --> P3
    P3 --> Stripe
    Stripe --> P3
    P3 --> P4
    P4 --> D3
    P4 --> D4
    P4 --> P5
    P5 --> D1
    P4 --> P6
    P6 --> Email
    P6 --> Customer
```

---

## 6. Sequence Diagrams

### 6.1 Checkout Process

```mermaid
sequenceDiagram
    actor C as Customer
    participant FE as Frontend
    participant GW as API Gateway
    participant O as Order Service
    participant I as Inventory Service
    participant P as Payment Service
    participant N as Notification Service

    C->>FE: Add items to cart
    C->>FE: Click Checkout
    FE->>GW: POST /orders
    activate GW

    GW->>O: Create order request
    activate O

    O->>I: Check inventory for all items
    activate I
    I-->>O: All items available
    deactivate I

    O->>I: Reserve inventory
    activate I
    I-->>O: Inventory reserved
    deactivate I

    O->>P: Process payment
    activate P
    P->>P: Validate payment method
    P->>P: Charge card
    P-->>O: Payment successful
    deactivate P

    O->>O: Create order record
    O->>O: Calculate totals
    O-->>GW: Order created
    deactivate O

    GW->>N: Order created event
    activate N
    N->>N: Send confirmation email
    N-->>GW: Email sent
    deactivate N

    GW-->>FE: 201 Created + Order details
    deactivate GW

    FE-->>C: Show order confirmation
```

### 6.2 Payment Processing

```mermaid
sequenceDiagram
    participant O as Order Service
    participant P as Payment Service
    participant S as Stripe API
    participant DB as Payment DB

    O->>P: ProcessPayment(orderId, amount, method)
    activate P

    P->>DB: Lock order for payment
    activate DB
    DB-->>P: Lock acquired
    deactivate DB

    alt Valid Payment Method
        P->>S: Create payment intent
        activate S
        S-->>P: Intent created
        deactivate S

        P->>S: Confirm payment
        activate S
        S-->>P: Payment succeeded
        deactivate S

        P->>DB: Save payment record
        activate DB
        DB-->>P: Saved
        deactivate DB

        P-->>O: Payment success
    else Invalid Payment Method
        P->>DB: Save failed attempt
        P-->>O: Payment failed
    end

    deactivate P
```

---

## 7. Module Design

### 7.1 Service Interfaces

#### Order Service Interface

```typescript
interface IOrderService {
    // Order CRUD
    createOrder(dto: CreateOrderDTO): Promise<Order>;
    getOrderById(id: number): Promise<Order>;
    listOrders(filter: OrderFilter): Promise<PaginatedResult<Order>>;

    // Order Management
    updateStatus(id: number, status: OrderStatus): Promise<Order>;
    cancelOrder(id: number, reason: string): Promise<Order>;

    // Calculations
    calculateSubtotal(items: OrderItemDTO[]): Promise<number>;
    calculateTax(subtotal: number, address: Address): Promise<number>;
    calculateShipping(weight: number, method: ShippingMethod): Promise<number>;
}

interface CreateOrderDTO {
    customerId: number;
    items: OrderItemDTO[];
    shippingAddress: AddressDTO;
    billingAddress: AddressDTO;
    shippingMethod: ShippingMethod;
    paymentMethodId: string;
    promoCode?: string;
}

type OrderStatus =
    | 'draft'
    | 'pending'
    | 'confirmed'
    | 'processing'
    | 'shipped'
    | 'delivered'
    | 'cancelled'
    | 'refunded';
```

#### Inventory Service Interface

```typescript
interface IInventoryService {
    // Stock Management
    checkAvailability(items: OrderItemDTO[]): Promise<StockCheckResult>;
    reserveItems(orderId: number, items: OrderItemDTO[]): Promise<void>;
    releaseReservation(orderId: number): Promise<void>;

    // Inventory Operations
    adjustStock(productId: number, quantity: number, reason: string): Promise<void>;
    getStockLevel(productId: number): Promise<StockLevel>;
    listLowStockProducts(threshold?: number): Promise<Product[]>;
}

interface StockCheckResult {
    available: boolean;
    unavailableItems: Array<{
        productId: number;
        requested: number;
        available: number;
    }>;
}

interface StockLevel {
    productId: number;
    quantity: number;
    reserved: number;
    available: number;
    status: 'in_stock' | 'low_stock' | 'out_of_stock';
}
```

### 7.2 Event-Driven Communication

```mermaid
flowchart LR
    subgraph "Services"
        OS[Order Service]
        IS[Inventory Service]
        PS[Payment Service]
        NS[Notification Service]
        WS[Warehouse Service]
    end

    subgraph "Message Queue"
        MQ[(RabbitMQ)]
    end

    subgraph "Event Topics"
        E1[order.created]
        E2[order.paid]
        E3[order.cancelled]
        E4[order.shipped]
    end

    OS -->|Publish| MQ
    MQ --> E1
    MQ --> E2
    MQ --> E3
    MQ --> E4

    E1 --> IS
    E1 --> WS

    E2 --> NS
    E2 --> WS

    E3 --> IS
    E3 --> PS

    E4 --> NS
```

**Event Schemas:**

```typescript
// Order Created Event
interface OrderCreatedEvent {
    eventType: 'order.created';
    eventId: string;
    timestamp: Date;
    data: {
        orderId: number;
        orderNumber: string;
        customerId: number;
        items: Array<{
            productId: number;
            quantity: number;
            unitPrice: number;
        }>;
        total: number;
    };
}

// Order Paid Event
interface OrderPaidEvent {
    eventType: 'order.paid';
    eventId: string;
    timestamp: Date;
    data: {
        orderId: number;
        paymentId: number;
        amount: number;
        paymentMethod: string;
    };
}
```

---

## 8. Security Considerations

### 8.1 Authentication & Authorization

| Feature | Implementation |
|---------|----------------|
| **Authentication** | JWT access tokens (15 min) + Refresh tokens (30 days) |
| **Password** | Bcrypt with salt rounds = 12 |
| **Multi-factor** | TOTP via authenticator app (optional for users) |
| **Authorization** | Role-based access control (RBAC) |
| **API Security** | API keys for external integrations |

### 8.2 Data Protection

| Data Type | Protection |
|-----------|------------|
| Passwords | Bcrypt hash, never logged |
| PII | Encrypted at rest (AES-256) |
| Payment data | PCI DSS compliance, never stored |
| API logs | Sanitized, no sensitive data |

### 8.3 Rate Limiting

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Public API | 100 requests | 15 minutes |
| Authenticated | 1000 requests | 15 minutes |
| Auth endpoints | 5 attempts | 15 minutes |

---

## 9. Deployment Architecture

```mermaid
flowchart TB
    subgraph "Load Balancer"
        LB[(ALB)]
    end

    subgraph "Kubernetes Cluster"
        subgraph "API Namespace"
            GW1[Gateway Pod 1]
            GW2[Gateway Pod 2]
            OS1[Order Service Pod 1]
            OS2[Order Service Pod 2]
        end

        subgraph "Database Namespace"
            PG[PostgreSQL StatefulSet]
            REDIS[Redis Cluster]
        end
    end

    subgraph "External"
        RDS[(Amazon RDS)]
        S3[(S3 Storage)]
    end

    LB --> GW1
    LB --> GW2

    GW1 --> OS1
    GW1 --> OS2
    GW2 --> OS1
    GW2 --> OS2

    OS1 --> PG
    OS2 --> PG
    OS1 --> REDIS
    OS2 --> REDIS

    PG --> RDS
```

---

## 10. Monitoring & Observability

### 10.1 Metrics

| Metric | Type | Threshold |
|--------|------|-----------|
| `order_create_duration` | Histogram | p95 < 500ms |
| `payment_success_rate` | Gauge | > 95% |
| `api_error_rate` | Gauge | < 1% |
| `inventory_check_duration` | Histogram | p95 < 100ms |

### 10.2 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| High error rate | error_rate > 5% | Critical |
| Payment failures | payment_success < 90% | High |
| Slow API | p95_latency > 2s | Medium |
| Low inventory | stock < threshold | Low |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **SKU** | Stock Keeping Unit - unique identifier for products |
| **Order Item** | Individual product line in an order |
| **Fulfillment** | Process of preparing and shipping an order |
| **Chargeback** | Payment reversal initiated by customer |

---

## Appendix B: Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-15 | Initial design document |
