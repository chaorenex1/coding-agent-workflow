# API Specification Template

## Overview
**Project:** [Project Name]
**API Version:** v1.0
**Base URL:** `https://api.example.com/v1`
**Protocol:** HTTPS
**Auth:** Bearer Token (JWT)
**Content-Type:** `application/json`

---

## Authentication

### Bearer Token Authentication
```
Authorization: Bearer <access_token>
```

### Token Endpoint
```
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

---

## API Endpoints

### Users Module

#### Create User
```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "User created successfully"
}
```

**Error Responses:**

| Code | Description |
|------|-------------|
| `400` | Validation error |
| `409` | Username or email already exists |

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ]
  }
}
```

---

#### Get User
```http
GET /users/{id}
Authorization: Bearer <token>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `integer` | Yes | User ID |

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `404` | User not found |

---

#### Update User
```http
PUT /users/{id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "is_active": false
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "is_active": false,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

#### Delete User
```http
DELETE /users/{id}
Authorization: Bearer <token>
```

**Response:** `204 No Content`

---

#### List Users
```http
GET /users
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `integer` | `1` | Page number |
| `limit` | `integer` | `20` | Items per page (max: 100) |
| `sort` | `string` | `created_at` | Sort field |
| `order` | `string` | `desc` | Sort direction: `asc`, `desc` |
| `search` | `string` | - | Search in username/email |

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

---

### Orders Module

#### Create Order
```http
POST /orders
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 123,
  "items": [
    {
      "product_id": 456,
      "quantity": 2,
      "unit_price": 29.99
    },
    {
      "product_id": 789,
      "quantity": 1,
      "unit_price": 49.99
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "USA"
  }
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": 999,
    "order_number": "ORD-2024-001234",
    "user_id": 123,
    "status": "pending",
    "total_amount": 109.97,
    "items": [...],
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

---

#### Get Order
```http
GET /orders/{id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 999,
    "order_number": "ORD-2024-001234",
    "user_id": 123,
    "status": "confirmed",
    "total_amount": 109.97,
    "items": [
      {
        "id": 1,
        "product_id": 456,
        "product_name": "Product A",
        "quantity": 2,
        "unit_price": 29.99,
        "subtotal": 59.98
      }
    ],
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:05:00Z"
  }
}
```

---

#### Update Order Status
```http
PATCH /orders/{id}/status
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "shipped",
  "tracking_number": "TRACK123456"
}
```

**Response:** `200 OK`

---

## Common Data Structures

### Pagination Metadata
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {},
    "request_id": "req_abc123"
  }
}
```

---

## HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created |
| `204` | No Content | Successful, no response body |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `409` | Conflict | Resource conflict |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |

---

## Rate Limiting

| Tier | Limit | Window |
|------|-------|--------|
| Free | 100 requests | 1 hour |
| Pro | 1000 requests | 1 hour |
| Enterprise | Unlimited | - |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1642249200
```

---

## Webhooks

### Order Status Update
```
POST https://your-domain.com/webhooks/orders
```

**Webhook Payload:**
```json
{
  "event": "order.status_updated",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "order_id": 999,
    "order_number": "ORD-2024-001234",
    "old_status": "confirmed",
    "new_status": "shipped"
  }
}
```

---

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
  description: API description

servers:
  - url: https://api.example.com/v1
    description: Production

security:
  - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

paths:
  /users:
    get:
      summary: List users
      tags: [Users]
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
    post:
      summary: Create user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created

  /users/{id}:
    get:
      summary: Get user
      tags: [Users]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        username:
          type: string
        email:
          type: string
          format: email
        first_name:
          type: string
        last_name:
          type: string
        is_active:
          type: boolean
        created_at:
          type: string
          format: date-time

    UserCreate:
      type: object
      required:
        - username
        - email
        - password
      properties:
        username:
          type: string
          minLength: 3
          maxLength: 50
        email:
          type: string
          format: email
        password:
          type: string
          minLength: 8
        first_name:
          type: string
        last_name:
          type: string
```
