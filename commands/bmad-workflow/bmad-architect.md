---
description: BMAD Phase 3 - Design system architecture, database schema, API contracts, and technical specifications
argument-hint: [architecture-focus]
allowed-tools: Read, Write, Edit, Grep, Glob, Task
model: claude-opus-4-5-20251022
---

# BMAD Phase 3: Architecture

You are initiating **Phase 3 of the BMAD workflow** - the Architecture phase. Your role is to design a scalable, maintainable system architecture based on the PRD and user stories.

## Context

**Architecture Focus** (optional): $ARGUMENTS

**Previous Phase Artifacts**:
@docs/bmad/01-analysis/project-brief.md
@docs/bmad/02-planning/prd.md
@docs/bmad/02-planning/user-stories.md

**Current Project State**:
- Project structure: !`tree -L 2 -I node_modules 2>/dev/null || find . -maxdepth 2 -type d | head -30`
- Package files: !`ls package.json pyproject.toml Cargo.toml go.mod 2>/dev/null`

## Your Mission

As the **Architect Agent**, design a production-ready system architecture optimized for solo developer productivity.

### Step 1: Technology Stack Selection

Based on PRD requirements, select optimal technology stack:

1. **Frontend**
   - Framework (React/Vue/Svelte/Next.js)
   - State management
   - UI component library
   - Styling approach

2. **Backend**
   - Runtime/Framework (Node.js/Python/Go/Rust)
   - API style (REST/GraphQL/tRPC)
   - Authentication approach
   - Background jobs

3. **Database**
   - Primary database (PostgreSQL/MongoDB/SQLite)
   - Caching layer (Redis/Memory)
   - Search (if needed)

4. **Infrastructure**
   - Hosting platform
   - CI/CD approach
   - Monitoring/Observability

### Step 2: System Design

Design the overall system architecture:

1. **Component Architecture**
   - Frontend modules
   - Backend services
   - Shared libraries

2. **Data Flow**
   - Request/response patterns
   - Event-driven patterns
   - Real-time requirements

3. **Integration Points**
   - Third-party APIs
   - Authentication providers
   - Payment processors

### Step 3: Create Architecture Document

#### Artifact: docs/bmad/architecture.md

```markdown
# System Architecture Document

## Document Info
- **Product**: [Product Name]
- **Version**: 1.0.0
- **Date**: [Current Date]
- **Author**: BMAD Architect Agent

---

## 1. Technology Stack

### 1.1 Overview

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | [Tech] | [Why] |
| Backend | [Tech] | [Why] |
| Database | [Tech] | [Why] |
| Hosting | [Platform] | [Why] |

### 1.2 Frontend Stack
```
Framework: [e.g., Next.js 14]
├── UI Library: [e.g., shadcn/ui]
├── State: [e.g., Zustand]
├── Forms: [e.g., React Hook Form + Zod]
├── Styling: [e.g., Tailwind CSS]
└── Testing: [e.g., Vitest + Playwright]
```

### 1.3 Backend Stack
```
Runtime: [e.g., Node.js 20]
├── Framework: [e.g., Hono/Express]
├── ORM: [e.g., Drizzle/Prisma]
├── Auth: [e.g., Lucia/NextAuth]
├── Validation: [e.g., Zod]
└── Testing: [e.g., Vitest]
```

### 1.4 Infrastructure Stack
```
Hosting: [e.g., Vercel + Railway]
├── Database: [e.g., PostgreSQL on Railway]
├── Cache: [e.g., Upstash Redis]
├── Storage: [e.g., Cloudflare R2]
├── CDN: [e.g., Cloudflare]
└── Monitoring: [e.g., Sentry + Axiom]
```

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Next.js Application                     │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │   │
│  │  │  Pages  │  │  API    │  │ Server  │             │   │
│  │  │         │  │ Routes  │  │ Actions │             │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘             │   │
│  └───────┼────────────┼────────────┼───────────────────┘   │
└──────────┼────────────┼────────────┼───────────────────────┘
           │            │            │
           ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Auth     │  │   Business  │  │    Data     │         │
│  │  Middleware │  │    Logic    │  │   Access    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
           │            │            │
           ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  R2 Storage  │      │
│  │  (Primary)   │  │   (Cache)    │  │   (Files)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
project-root/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth group routes
│   │   ├── (dashboard)/       # Dashboard group routes
│   │   ├── api/               # API routes
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   ├── features/          # Feature-specific components
│   │   └── layouts/           # Layout components
│   ├── lib/
│   │   ├── db/                # Database client & schema
│   │   ├── auth/              # Auth utilities
│   │   ├── api/               # API client
│   │   └── utils/             # Shared utilities
│   ├── hooks/                 # Custom React hooks
│   ├── stores/                # State management
│   └── types/                 # TypeScript types
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   └── bmad/                  # BMAD artifacts
└── [config files]
```

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   [entity]   │       │   [entity]   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)      │       │ id (PK)      │
│ email        │  │    │ user_id (FK) │◄──────│ [field]      │
│ name         │  └───►│ [fields]     │       │ [fields]     │
│ created_at   │       │ created_at   │       │ created_at   │
└──────────────┘       └──────────────┘       └──────────────┘
```

### 3.2 Schema Definition

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- [Additional tables based on PRD features]
```

---

## 4. API Design

### 4.1 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register | User registration | No |
| POST | /api/auth/login | User login | No |
| GET | /api/users/me | Get current user | Yes |
| [More endpoints] | | | |

### 4.2 Request/Response Examples

```typescript
// POST /api/auth/register
// Request
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}

// Response (201 Created)
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "createdAt": "2025-01-05T00:00:00Z"
}
```

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
User ──→ Login Form ──→ API ──→ Validate Credentials
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                    [Success]                  [Failure]
                    Create Session             Return Error
                    Set Cookie
                         │
                         ▼
                    Redirect to Dashboard
```

### 5.2 Security Measures

- [ ] Password hashing (bcrypt/Argon2)
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input validation (Zod)
- [ ] SQL injection prevention (Parameterized queries)
- [ ] XSS prevention (React default escaping)
- [ ] HTTPS enforcement
- [ ] Security headers (Helmet)

---

## 6. Deployment Architecture

### 6.1 Environments

| Environment | URL | Purpose |
|-------------|-----|---------|
| Development | localhost:3000 | Local development |
| Preview | *.vercel.app | PR previews |
| Staging | staging.example.com | Pre-production testing |
| Production | example.com | Live users |

### 6.2 CI/CD Pipeline

```
Push to GitHub
       │
       ▼
┌─────────────────┐
│   Lint & Type   │
│     Check       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Unit Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Build App     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Preview]  [Main Branch]
   │            │
   ▼            ▼
Preview      Production
Deploy        Deploy
```

---

## 7. Development Guidelines

### 7.1 Code Conventions

- TypeScript strict mode
- ESLint + Prettier for formatting
- Conventional Commits for git messages
- Feature branches + PR workflow

### 7.2 Testing Strategy

| Type | Coverage Target | Tools |
|------|-----------------|-------|
| Unit | 80% | Vitest |
| Integration | 60% | Vitest |
| E2E | Critical paths | Playwright |

---

Generated by BMAD Workflow - Phase 3: Architecture
```

### Step 4: Create Technical Specification

#### Artifact: docs/bmad/tech-spec.md

```markdown
# Technical Specification

## 1. Development Environment Setup

### Prerequisites
- Node.js [version]
- [Package manager]
- [Database if local]

### Setup Commands
```bash
# Clone and install
git clone [repo]
cd [project]
[package-manager] install

# Environment setup
cp .env.example .env.local
# Edit .env.local with your values

# Database setup
[database-commands]

# Start development
[start-command]
```

## 2. Key Technical Decisions

### Decision 1: [Title]
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Consequences**: [Trade-offs and implications]

## 3. External Dependencies

| Dependency | Version | Purpose | License |
|------------|---------|---------|---------|
| [name] | [ver] | [why] | [license] |

## 4. Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DATABASE_URL | Yes | Database connection | postgres://... |
| [VAR] | [Yes/No] | [Description] | [Example] |

---

Generated by BMAD Workflow - Phase 3: Architecture
```

## Output Requirements

### 文件沉淀位置

```
docs/bmad/03-architecture/
├── architecture.md       # 系统架构文档
├── tech-spec.md          # 技术规格
└── database-schema.sql   # 数据库Schema (可选)
```

### 操作步骤

1. **读取Phase 2产出**
   - `docs/bmad/02-planning/prd.md`
   - `docs/bmad/02-planning/user-stories.md`

2. **创建目录结构**
   ```bash
   mkdir -p docs/bmad/03-architecture
   ```

3. **写入文档**
   - `docs/bmad/03-architecture/architecture.md`
   - `docs/bmad/03-architecture/tech-spec.md`
   - `docs/bmad/03-architecture/database-schema.sql` (如果适用)

4. **更新状态** (如果 .bmad/ 存在)
   ```yaml
   # .bmad/state.yaml
   workflow:
     current_phase: 3
     phase_status:
       1: completed
       2: completed
       3: completed
   ```

5. **提交到git**
   ```bash
   git add docs/bmad/03-architecture/
   git commit -m "feat(bmad): Phase 3 - Architecture design complete"
   ```

## Success Criteria

- [ ] Technology stack justified for solo developer
- [ ] System architecture clearly diagrammed
- [ ] Database schema defined
- [ ] API contracts specified
- [ ] Security measures outlined
- [ ] Deployment strategy documented
- [ ] Both artifacts written to docs/bmad/
- [ ] Files committed to git

## Next Phase

After completing this phase, run:
```
/bmad-develop epic-001/story-001
```

This will initiate Phase 4: Development to implement features story by story.

---

**IMPORTANT**: Optimize architecture for solo developer productivity. Prefer managed services over self-hosted, convention over configuration, and monolith over microservices for MVP.
