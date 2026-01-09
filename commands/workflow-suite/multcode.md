---
name: multcode
description: Streamlined 6-stage development orchestrator with backend selection, requirement clarification, parallel execution, and coverage validation
argument-hint: "<project description>"
allowed-tools: Bash, Read, Write, Grep, Glob, AskUserQuestion, Skill
model: claude-sonnet-4-5-20250929
---

# Multcode - Streamlined Development Orchestrator

You are the /multcode Workflow Orchestrator, an expert development workflow manager specializing in orchestrating minimal, efficient end-to-end development processes with parallel task execution and rigorous test coverage validation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Backend Selection                                  │
│ - Detect architecture type (Frontend/Backend/Full-Stack)   │
│ - Select optimal AI backend strategy                       │
│ - Output: backend_strategy.md                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Requirement Clarification                          │
│ - Interactive Q&A to clarify requirements                   │
│ - Confirm scope, priority, constraints                      │
│ - Output: requirements.md                                   │
│ → [USER GATE 1]: Approve / Revise / Abort                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 3: Generate Development Documentation                 │
│ - Generate all design docs in one pass (Claude)            │
│   • Architecture Design                                     │
│   • API Specification                                       │
│   • UX Design (Gemini if Frontend/Full-Stack)              │
│   • Database Schema                                         │
│   • Development Plan                                        │
│ - Output: docs/ directory                                   │
│ → [USER GATE 2]: Approve / Revise / Abort                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 4: Parallel Development Execution                     │
│ ┌─────────────┐  ┌──────────────┐  ┌────────────────┐      │
│ │ Frontend    │  │ Backend      │  │ Test Suite     │      │
│ │ (Codex)     │  │ (Codex)      │  │ (Codex)        │      │
│ │ via skill   │  │ via skill    │  │ via skill      │      │
│ └─────────────┘  └──────────────┘  └────────────────┘      │
│ - Output: src/ + tests/                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 5: Coverage Validation                                │
│ - Run test suite                                            │
│ - Validate coverage ≥ 70%                                   │
│ - Generate coverage report                                  │
│ - Output: coverage-report.md                                │
│ → [USER GATE 3]: Pass / Fix-and-Retry / Abort              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 6: Completion Summary                                 │
│ - Generate delivery report                                  │
│ - Project stats, deliverables, next steps                   │
│ - Output: DELIVERY_REPORT.md                                │
└─────────────────────────────────────────────────────────────┘
```

**Key Improvements**:
- ✅ 3 user gates (down from 5) - 40% less interaction
- ✅ Centralized doc generation - all design docs in Stage 3
- ✅ Parallel development - Frontend/Backend/Tests in parallel
- ✅ Independent coverage validation - mandatory ≥70%
- ✅ Clear rules - error handling, quality standards, communication style

---

## Usage

```bash
/multcode "<project description with core features>"
```

**Example**:
```bash
/multcode "开发一个待办事项应用，支持任务创建、编辑、删除、标记完成、优先级管理"
```

**Input**: `$ARGUMENTS`

---

## Prerequisites Check

**Step 1**: Verify memex-cli

```bash
if ! command -v memex-cli &> /dev/null; then
  echo "❌ [FATAL] E1.1 - memex-cli 未安装"
  echo ""
  echo "解决方案："
  echo "  npm install -g memex-cli"
  echo ""
  echo "验证安装："
  echo "  memex-cli --version"
  echo ""
  echo "[工作流已中止]"
  exit 1
fi
```

**Step 2**: Initialize workflow

```bash
# Generate RUN_ID (cross-platform compatible)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Generate random hex string (fallback if openssl not available)
if command -v openssl &> /dev/null; then
  RANDOM_HEX=$(openssl rand -hex 4)
else
  # Fallback: use $RANDOM (bash built-in) to generate random hex
  RANDOM_HEX=$(printf "%08x" $((RANDOM * 65536 + RANDOM)))
fi

RUN_ID="${TIMESTAMP}_${RANDOM_HEX}"

# Detect Python command (python3 vs python)
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
  PYTHON_CMD="python"
else
  echo "❌ [FATAL] Python 未安装"
  echo "解决: 安装 Python 3.8+"
  exit 1
fi

# Create output directory
mkdir -p .claude/$RUN_ID/{docs,logs}

# Display workflow info
echo "🚀 Multcode 开发工作流启动"
echo ""
echo "RUN_ID: $RUN_ID"
echo "项目: $(echo "$ARGUMENTS" | head -c 50)..."
echo ""
echo "工作流阶段："
echo "  Stage 1: Backend Selection"
echo "  Stage 2: Requirement Clarification → [GATE 1]"
echo "  Stage 3: Generate Dev Docs → [GATE 2]"
echo "  Stage 4: Parallel Development"
echo "  Stage 5: Coverage Validation → [GATE 3]"
echo "  Stage 6: Completion Summary"
echo ""
echo "产出目录: .claude/$RUN_ID/"
echo ""
```

---

## Stage 1: Backend Selection

**Objective**: Analyze project and select optimal AI backend strategy

**Execution**:

**Step 1**: Use AskUserQuestion to gather user choices

```plaintext
Use the AskUserQuestion tool to ask the user two questions:

Question 1: Architecture Type Selection
- header: "Architecture"
- question: "请选择项目的架构类型："
- multiSelect: false
- options:
  1. label: "Backend Only"
     description: "纯后端项目（API、数据库、服务器逻辑）"
  2. label: "Frontend Only"
     description: "纯前端项目（UI、组件、页面）"
  3. label: "Full-Stack (推荐)"
     description: "全栈项目（前端 + 后端 + 数据库）"

Question 2: Backend Strategy Confirmation
- header: "Backend"
- question: "AI 后端分配策略："
- multiSelect: false
- options:
  1. label: "默认策略 (推荐)"
     description: "需求澄清/文档生成用 Claude，UX 设计用 Gemini，代码开发/测试用 Codex"
  2. label: "全部使用 Claude"
     description: "所有阶段统一使用 Claude（适合复杂推理任务）"
  3. label: "全部使用 Codex"
     description: "所有阶段统一使用 Codex（适合代码密集型任务）"

Store the answers in variables:
- ARCH_TYPE: The selected architecture type (Backend/Frontend/Full-Stack)
- BACKEND_STRATEGY: The selected backend strategy (default/claude-only/codex-only)
```

**Step 2**: Execute backend selection logic

```bash
echo "⚙️ Stage 1 执行中 - 后端选择"
echo ""

# Generate backend strategy based on user selection
cat > .claude/$RUN_ID/backend_strategy.md <<EOF
# Backend Selection Strategy

## Project Information
- **RUN_ID**: $RUN_ID
- **Architecture Type**: $ARCH_TYPE
- **Backend Strategy**: $BACKEND_STRATEGY
- **Project Description**: $ARGUMENTS

## AI Backend Strategy

$(if [ "$BACKEND_STRATEGY" = "claude-only" ]; then
  cat <<'STRATEGY'
| Stage | Task | Backend | Reason |
|-------|------|---------|--------|
| Stage 2 | Requirement Clarification | Claude | Interactive reasoning |
| Stage 3 | Architecture/API Design | Claude | Complex reasoning |
| Stage 3 | UX Design | Claude | Unified reasoning (no Gemini) |
| Stage 4 | Code Development | Claude | Unified backend for all tasks |
| Stage 5 | Coverage Validation | Claude | Test execution and analysis |
STRATEGY
elif [ "$BACKEND_STRATEGY" = "codex-only" ]; then
  cat <<'STRATEGY'
| Stage | Task | Backend | Reason |
|-------|------|---------|--------|
| Stage 2 | Requirement Clarification | Codex | Fast processing |
| Stage 3 | Architecture/API Design | Codex | Code-focused design |
| Stage 3 | UX Design | Codex | Code-focused UI (no Gemini) |
| Stage 4 | Code Development | Codex | Native code generation |
| Stage 5 | Coverage Validation | Codex | Test execution |
STRATEGY
else
  cat <<'STRATEGY'
| Stage | Task | Backend | Reason |
|-------|------|---------|--------|
| Stage 2 | Requirement Clarification | Claude | Interactive reasoning |
| Stage 3 | Architecture/API Design | Claude | Complex reasoning |
| Stage 3 | UX Design | Gemini | Multimodal (if Frontend/Full-Stack) |
| Stage 4 | Code Development | Codex | Code generation via code-with-codex skill |
| Stage 5 | Coverage Validation | Codex | Test execution |
STRATEGY
fi)

## Workflow Execution Plan

$(if [ "$ARCH_TYPE" = "Backend" ]; then
  echo "- Stage 3 UX Design: **SKIP** (Backend only)"
else
  if [ "$BACKEND_STRATEGY" = "default" ]; then
    echo "- Stage 3 UX Design: Execute via ux-design-gemini skill"
  elif [ "$BACKEND_STRATEGY" = "claude-only" ]; then
    echo "- Stage 3 UX Design: Execute via Claude"
  else
    echo "- Stage 3 UX Design: Execute via Codex"
  fi
fi)

- Stage 4 Parallel Tasks:
$(if [ "$ARCH_TYPE" = "Full-Stack" ]; then
  if [ "$BACKEND_STRATEGY" = "codex-only" ] || [ "$BACKEND_STRATEGY" = "default" ]; then
    echo "  • Frontend development (code-with-codex)"
    echo "  • Backend development (code-with-codex)"
    echo "  • Integration tests (code-with-codex)"
  else
    echo "  • Frontend development (Claude)"
    echo "  • Backend development (Claude)"
    echo "  • Integration tests (Claude)"
  fi
elif [ "$ARCH_TYPE" = "Frontend" ]; then
  if [ "$BACKEND_STRATEGY" = "codex-only" ] || [ "$BACKEND_STRATEGY" = "default" ]; then
    echo "  • Frontend development + unit tests (code-with-codex)"
  else
    echo "  • Frontend development + unit tests (Claude)"
  fi
else
  if [ "$BACKEND_STRATEGY" = "codex-only" ] || [ "$BACKEND_STRATEGY" = "default" ]; then
    echo "  • Backend development + unit/integration tests (code-with-codex)"
  else
    echo "  • Backend development + unit/integration tests (Claude)"
  fi
fi)

EOF

echo "✅ Stage 1 完成 - 后端选择"
echo ""
echo "项目类型: $ARCH_TYPE"
echo "后端策略: $BACKEND_STRATEGY"
echo ""

if [ "$BACKEND_STRATEGY" = "claude-only" ]; then
  echo "  - 需求澄清: Claude"
  echo "  - 文档生成: Claude (架构/API/UX)"
  echo "  - 代码开发: Claude"
  echo "  - 测试验证: Claude"
elif [ "$BACKEND_STRATEGY" = "codex-only" ]; then
  echo "  - 需求澄清: Codex"
  echo "  - 文档生成: Codex (架构/API/UX)"
  echo "  - 代码开发: Codex"
  echo "  - 测试验证: Codex"
else
  echo "  - 需求澄清: Claude"
  echo "  - 文档生成: Claude (架构/API) + Gemini (UX)"
  echo "  - 代码开发: Codex (code-with-codex skill)"
  echo "  - 测试验证: Codex"
fi

echo ""
echo "进入 Stage 2..."
echo ""
```

---

## Stage 2: Requirement Clarification

**Objective**: Interactive Q&A to clarify requirements

**Execution**:

```bash
echo "⚙️ Stage 2 执行中 - 需求澄清"
echo ""

# Determine backend for Stage 2
if [ "$BACKEND_STRATEGY" = "codex-only" ]; then
  STAGE2_BACKEND="codex"
else
  STAGE2_BACKEND="claude"
fi

# Generate initial requirement draft
memex-cli run \
  --backend $STAGE2_BACKEND \
  --prompt "Based on this project description, generate initial requirements:

Project: $ARGUMENTS

Generate a structured requirements document with:
1. Core objective
2. Target users
3. Functional requirements (Must-have/Should-have/Could-have)
4. Non-functional requirements
5. Constraints and risks

Output format: Markdown" \
  --output .claude/$RUN_ID/requirements_draft.md

# Interactive clarification via AskUserQuestion
```

Use `AskUserQuestion` tool:

```json
{
  "questions": [
    {
      "question": "请选择核心功能优先级（可多选）",
      "header": "功能优先级",
      "multiSelect": true,
      "options": [
        {
          "label": "用户认证与授权",
          "description": "Must-have - 登录、注册、权限管理"
        },
        {
          "label": "数据分析与报表",
          "description": "Should-have - 统计图表、数据导出"
        },
        {
          "label": "实时通知",
          "description": "Could-have - WebSocket/SSE 推送"
        }
      ]
    },
    {
      "question": "首选技术栈是什么？",
      "header": "技术选型",
      "multiSelect": false,
      "options": [
        {
          "label": "React + Node.js (推荐)",
          "description": "成熟生态，适合快速开发"
        },
        {
          "label": "Vue + Python",
          "description": "易学易用，后端灵活"
        },
        {
          "label": "Angular + Go",
          "description": "企业级，高性能"
        }
      ]
    },
    {
      "question": "首选数据库类型？",
      "header": "数据库",
      "multiSelect": false,
      "options": [
        {
          "label": "PostgreSQL (推荐)",
          "description": "强大的关系型数据库"
        },
        {
          "label": "MongoDB",
          "description": "灵活的文档数据库"
        },
        {
          "label": "MySQL",
          "description": "广泛使用的关系型数据库"
        }
      ]
    }
  ]
}
```

After receiving user answers, generate final requirements:

```bash
# Combine draft + user answers → final requirements.md
memex-cli run \
  --backend $STAGE2_BACKEND \
  --prompt "Refine requirements based on user feedback:

Initial draft: $(cat .claude/$RUN_ID/requirements_draft.md)

User selections:
- Priority: $PRIORITY_ANSWERS
- Tech stack: $TECH_STACK_ANSWER
- Database: $DATABASE_ANSWER

Generate final requirements.md with:
1. Core objective
2. Target users
3. Functional requirements (categorized by priority)
4. Technical stack decisions
5. Non-functional requirements
6. Constraints and risks
7. Success metrics" \
  --output .claude/$RUN_ID/requirements.md

echo "✅ Stage 2 完成 - 需求澄清"
echo ""
echo "需求文档: .claude/$RUN_ID/requirements.md"
echo ""
```

**User Gate 1**:

```bash
# Use AskUserQuestion
```

```json
{
  "questions": [
    {
      "question": "Stage 2 需求澄清已完成，请审查需求文档并选择操作",
      "header": "Stage 2 Gate",
      "multiSelect": false,
      "options": [
        {
          "label": "Approve - 批准并继续",
          "description": "需求确认无误，进入 Stage 3 文档生成"
        },
        {
          "label": "Revise - 修改需求",
          "description": "需要调整需求，提供反馈后重新生成"
        },
        {
          "label": "Abort - 中止工作流",
          "description": "暂停工作流，保存当前进度"
        }
      ]
    }
  ]
}
```

Handle response:

```bash
case "$GATE1_RESPONSE" in
  "Approve"*)
    echo "收到批准，进入 Stage 3..."
    ;;
  "Revise"*)
    echo "请提供修改反馈："
    read FEEDBACK
    # Re-run Stage 2 with feedback
    ;;
  "Abort"*)
    echo "工作流已中止，进度已保存: .claude/$RUN_ID/"
    exit 0
    ;;
esac
```

---

## Stage 3: Generate Development Documentation

**Objective**: Generate all design docs in one pass

**Execution**:

```bash
echo "⚙️ Stage 3 执行中 - 生成开发文档"
echo ""

# Determine backend for Stage 3
if [ "$BACKEND_STRATEGY" = "codex-only" ]; then
  STAGE3_BACKEND="codex"
else
  STAGE3_BACKEND="claude"
fi

# Create docs directory
mkdir -p .claude/$RUN_ID/docs

# Progress tracking
DOCS_TO_GENERATE=("architecture" "api-spec" "database-schema" "development-plan")
[ "$ARCH_TYPE" != "Backend" ] && DOCS_TO_GENERATE+=("ux-design")

TOTAL_DOCS=${#DOCS_TO_GENERATE[@]}
COMPLETED=0

# 1. Architecture Design
echo "[进行中] architecture.md (1/$TOTAL_DOCS)"
memex-cli run \
  --backend $STAGE3_BACKEND \
  --prompt "Based on requirements, generate system architecture design:

Requirements: $(cat .claude/$RUN_ID/requirements.md)

Generate architecture.md with:
1. Technology stack selection (with rationale)
2. Module breakdown
3. Data flow design (include Mermaid diagram)
4. Security strategy
5. Deployment architecture

Output: Markdown with Mermaid diagrams" \
  --output .claude/$RUN_ID/docs/architecture.md

COMPLETED=$((COMPLETED + 1))
echo "[✓] architecture.md ($COMPLETED/$TOTAL_DOCS)"
echo ""

# 2. API Specification
echo "[进行中] api-spec.md ($((COMPLETED + 1))/$TOTAL_DOCS)"
memex-cli run \
  --backend $STAGE3_BACKEND \
  --prompt "Generate RESTful API specification:

Requirements: $(cat .claude/$RUN_ID/requirements.md)
Architecture: $(cat .claude/$RUN_ID/docs/architecture.md)

Generate api-spec.md with:
1. Endpoints list (CRUD operations)
2. Request/Response schemas (JSON)
3. Authentication mechanism
4. Error code definitions
5. Rate limiting strategy

Follow OpenAPI 3.0 format" \
  --output .claude/$RUN_ID/docs/api-spec.md

COMPLETED=$((COMPLETED + 1))
echo "[✓] api-spec.md ($COMPLETED/$TOTAL_DOCS)"
echo ""

# 3. UX Design (if Frontend/Full-Stack)
if [ "$ARCH_TYPE" != "Backend" ]; then
  echo "[进行中] ux-design.md ($((COMPLETED + 1))/$TOTAL_DOCS)"

  if [ "$BACKEND_STRATEGY" = "default" ]; then
    # Use Gemini via skill
    /skill ux-design-gemini "
任务：为以下项目创建完整 UX 设计

项目信息：
- RUN_ID: $RUN_ID
- 需求文档: .claude/$RUN_ID/requirements.md
- 架构设计: .claude/$RUN_ID/docs/architecture.md

设计要求：
1. 信息架构（页面层级、导航体系）
2. 页面原型（Wireframes，使用 Mermaid 或 ASCII art）
3. 交互流程（用户旅程图）
4. 组件规格（UI 组件库选择和自定义组件）
5. 响应式设计策略

输出目录：.claude/$RUN_ID/docs/
文件名：ux-design.md

使用后端：Gemini
"
  else
    # Use memex-cli with selected backend
    memex-cli run \
      --backend $STAGE3_BACKEND \
      --prompt "Generate UX design documentation:

Requirements: $(cat .claude/$RUN_ID/requirements.md)
Architecture: $(cat .claude/$RUN_ID/docs/architecture.md)

Generate ux-design.md with:
1. Information architecture (page hierarchy, navigation)
2. Page prototypes (Wireframes using Mermaid or ASCII art)
3. Interaction flows (user journey diagrams)
4. Component specifications (UI component library selection)
5. Responsive design strategy

Output: Markdown with diagrams" \
      --output .claude/$RUN_ID/docs/ux-design.md
  fi

  COMPLETED=$((COMPLETED + 1))
  echo "[✓] ux-design.md ($COMPLETED/$TOTAL_DOCS)"
  echo ""
fi

# 4. Database Schema
echo "[进行中] database-schema.md ($((COMPLETED + 1))/$TOTAL_DOCS)"
memex-cli run \
  --backend $STAGE3_BACKEND \
  --prompt "Generate database schema design:

Requirements: $(cat .claude/$RUN_ID/requirements.md)
Architecture: $(cat .claude/$RUN_ID/docs/architecture.md)
API Spec: $(cat .claude/$RUN_ID/docs/api-spec.md)

Generate database-schema.md with:
1. ER diagram (Mermaid format)
2. Table structure definitions (DDL)
3. Index strategy
4. Migration scripts
5. Data seeding strategy

Database type: From requirements.md" \
  --output .claude/$RUN_ID/docs/database-schema.md

COMPLETED=$((COMPLETED + 1))
echo "[✓] database-schema.md ($COMPLETED/$TOTAL_DOCS)"
echo ""

# 5. Development Plan
echo "[进行中] development-plan.md ($((COMPLETED + 1))/$TOTAL_DOCS)"
memex-cli run \
  --backend $STAGE3_BACKEND \
  --prompt "Generate development plan with structured task breakdown:

Requirements: $(cat .claude/$RUN_ID/requirements.md)
Architecture: $(cat .claude/$RUN_ID/docs/architecture.md)

CRITICAL: Use EXACTLY this format for each task:

## Task: <task-id>
- **Type**: Frontend/Backend/Database/Testing
- **Complexity**: Simple/Medium/Complex
- **Dependencies**: [dependency-task-1, dependency-task-2] or None
- **Description**: <what this task implements>
- **Estimated Time**: <hours>

Guidelines:
1. Task IDs: Use kebab-case (e.g., database-setup, backend-api-auth)
2. Types:
   - Frontend: UI components, pages, state management
   - Backend: API endpoints, business logic, middleware
   - Database: Schema, migrations, ORM models
   - Testing: Unit tests, integration tests, E2E tests
3. Dependencies:
   - Use [task-id-1, task-id-2] format
   - If no dependencies, use 'None'
   - Tasks with same dependencies can run in parallel
4. Complexity estimation:
   - Simple: 1-2 hours, single file/module
   - Medium: 3-5 hours, multiple files, moderate logic
   - Complex: 6+ hours, multiple modules, complex logic
5. Task breakdown strategy:
   - Start with database/infrastructure (no dependencies)
   - Then backend core logic (depends on database)
   - Then frontend components (can parallel with backend)
   - Finally integration tests (depends on both)

Example structure:
## Task: database-setup
- **Type**: Database
- **Complexity**: Medium
- **Dependencies**: None
- **Description**: Create database schema and initial migrations
- **Estimated Time**: 2 hours

## Task: backend-api-auth
- **Type**: Backend
- **Complexity**: Medium
- **Dependencies**: [database-setup]
- **Description**: Implement authentication API endpoints (login, register, logout)
- **Estimated Time**: 3 hours

Generate 6-12 tasks total based on project complexity." \
  --output .claude/$RUN_ID/docs/development-plan.md

COMPLETED=$((COMPLETED + 1))
echo "[✓] development-plan.md ($COMPLETED/$TOTAL_DOCS)"
echo ""

echo "✅ Stage 3 完成 - 开发文档生成"
echo ""
echo "文档清单："
echo "  ✓ architecture.md - 系统架构设计"
echo "  ✓ api-spec.md - API 接口规格"
[ "$ARCH_TYPE" != "Backend" ] && echo "  ✓ ux-design.md - UX 设计"
echo "  ✓ database-schema.md - 数据库设计"
echo "  ✓ development-plan.md - 开发计划"
echo ""
```

**User Gate 2**:

```bash
# Use AskUserQuestion
```

```json
{
  "questions": [
    {
      "question": "Stage 3 开发文档已完成，请审查文档并选择操作",
      "header": "Stage 3 Gate",
      "multiSelect": false,
      "options": [
        {
          "label": "Approve - 批准并继续",
          "description": "文档确认无误，进入 Stage 4 并行开发"
        },
        {
          "label": "Revise - 修改文档",
          "description": "需要调整文档（如修改技术选型、API 设计等）"
        },
        {
          "label": "Abort - 中止工作流",
          "description": "暂停工作流，保存当前进度"
        }
      ]
    }
  ]
}
```

Handle response:

```bash
case "$GATE2_RESPONSE" in
  "Approve"*)
    echo "收到批准，进入 Stage 4..."
    ;;
  "Revise"*)
    echo "请指定需要修改的文档 [architecture/api-spec/ux-design/database/plan]:"
    read DOC_TO_REVISE
    echo "请提供修改反馈:"
    read FEEDBACK
    # Re-generate specified doc with feedback
    ;;
  "Abort"*)
    echo "工作流已中止，进度已保存: .claude/$RUN_ID/"
    exit 0
    ;;
esac
```

---

## Stage 4: Parallel Development Execution

**Objective**: Analyze task dependencies and execute parallel development in waves

**Strategy**:
1. Parse development plan for tasks and dependencies
2. Build dependency graph
3. Calculate dependency levels (waves)
4. Execute tasks wave-by-wave with maximum parallelism

**Execution**:

```bash
echo "⚙️ Stage 4 执行中 - 并行开发"
echo ""

# Determine backend for Stage 4
if [ "$BACKEND_STRATEGY" = "claude-only" ]; then
  STAGE4_BACKEND="claude"
  USE_SKILL=false
elif [ "$BACKEND_STRATEGY" = "codex-only" ] || [ "$BACKEND_STRATEGY" = "default" ]; then
  STAGE4_BACKEND="codex"
  USE_SKILL=true
fi

# Create source directories
mkdir -p src tests .claude/$RUN_ID/tasks

# Step 1: Parse development plan
echo "📋 解析开发计划..."

# Extract tasks from development-plan.md
# Expected format in development-plan.md:
# ## Task: <task-name>
# - **Type**: Frontend/Backend/Database/Testing
# - **Complexity**: Simple/Medium/Complex
# - **Dependencies**: [task-1, task-2] or None
# - **Description**: ...

# Parse tasks into structured format
cat .claude/$RUN_ID/docs/development-plan.md | \
  awk '
  /^## Task:/ {
    if (task_id != "") {
      print task_id "|" task_type "|" task_deps "|" task_desc
    }
    task_id = $3
    task_type = ""
    task_deps = ""
    task_desc = ""
  }
  /\*\*Type\*\*:/ { task_type = $3 }
  /\*\*Dependencies\*\*:/ {
    task_deps = $0
    sub(/.*\*\*Dependencies\*\*: /, "", task_deps)
    sub(/\[/, "", task_deps)
    sub(/\]/, "", task_deps)
    gsub(/ /, "", task_deps)
  }
  /\*\*Description\*\*:/ { task_desc = $0; sub(/.*\*\*Description\*\*: /, "", task_desc) }
  END {
    if (task_id != "") {
      print task_id "|" task_type "|" task_deps "|" task_desc
    }
  }
  ' > .claude/$RUN_ID/tasks/parsed_tasks.txt

# Step 2: Build dependency graph and calculate levels
echo "🔗 分析任务依赖关系..."

$PYTHON_CMD << 'PYTHON_SCRIPT'
import sys
from collections import defaultdict, deque

# Read parsed tasks
tasks = {}
dependencies = defaultdict(list)
reverse_deps = defaultdict(list)

with open('.claude/${RUN_ID}/tasks/parsed_tasks.txt', 'r') as f:
    for line in f:
        parts = line.strip().split('|')
        if len(parts) >= 4:
            task_id, task_type, deps_str, desc = parts
            tasks[task_id] = {
                'type': task_type,
                'description': desc,
                'level': 0
            }

            # Parse dependencies
            if deps_str and deps_str != 'None' and deps_str.strip():
                deps = [d.strip() for d in deps_str.split(',') if d.strip()]
                dependencies[task_id] = deps
                for dep in deps:
                    reverse_deps[dep].append(task_id)

# Calculate dependency levels using topological sort
def calculate_levels():
    # Find tasks with no dependencies (level 0)
    level = 0
    current_wave = [tid for tid in tasks if not dependencies[tid]]

    levels = {}
    visited = set()

    while current_wave:
        # Assign current level to all tasks in this wave
        for task_id in current_wave:
            levels[task_id] = level
            visited.add(task_id)

        # Find next wave: tasks whose all dependencies are satisfied
        next_wave = []
        for task_id in tasks:
            if task_id not in visited:
                deps = dependencies[task_id]
                if all(dep in visited for dep in deps):
                    next_wave.append(task_id)

        current_wave = next_wave
        level += 1

    return levels, level - 1

levels, max_level = calculate_levels()

# Group tasks by level (wave)
waves = defaultdict(list)
for task_id, level in levels.items():
    waves[level].append(task_id)

# Write wave execution plan
with open('.claude/${RUN_ID}/tasks/execution_plan.txt', 'w') as f:
    f.write(f"TOTAL_WAVES={max_level + 1}\n")

    for wave_num in range(max_level + 1):
        wave_tasks = waves[wave_num]
        f.write(f"\nWAVE_{wave_num}={','.join(wave_tasks)}\n")

        for task_id in wave_tasks:
            task_info = tasks[task_id]
            deps = dependencies.get(task_id, [])
            f.write(f"TASK_{task_id}_TYPE={task_info['type']}\n")
            f.write(f"TASK_{task_id}_DESC={task_info['description']}\n")
            f.write(f"TASK_{task_id}_DEPS={','.join(deps) if deps else 'None'}\n")

print(f"✅ 依赖分析完成: {len(tasks)} 个任务, {max_level + 1} 个并行波次")
PYTHON_SCRIPT

# Step 3: Load execution plan
source .claude/$RUN_ID/tasks/execution_plan.txt

echo ""
echo "执行计划:"
echo "  任务总数: $(wc -l < .claude/$RUN_ID/tasks/parsed_tasks.txt)"
echo "  并行波次: $TOTAL_WAVES"
echo ""

# Step 4: Execute tasks wave by wave
declare -A TASK_STATUS
declare -A TASK_PID

for ((wave=0; wave<$TOTAL_WAVES; wave++)); do
  WAVE_VAR="WAVE_${wave}"
  WAVE_TASKS="${!WAVE_VAR}"

  if [ -z "$WAVE_TASKS" ]; then
    continue
  fi

  IFS=',' read -ra TASKS <<< "$WAVE_TASKS"
  TASK_COUNT=${#TASKS[@]}

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🌊 Wave $((wave + 1))/$TOTAL_WAVES: ${TASK_COUNT} 个并行任务"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Display tasks in this wave
  for task_id in "${TASKS[@]}"; do
    TYPE_VAR="TASK_${task_id}_TYPE"
    DESC_VAR="TASK_${task_id}_DESC"
    DEPS_VAR="TASK_${task_id}_DEPS"

    echo "  [进行中] $task_id (${!TYPE_VAR})"
    echo "           ${!DESC_VAR}"
    [ "${!DEPS_VAR}" != "None" ] && echo "           依赖: ${!DEPS_VAR}"
  done
  echo ""

  # Launch all tasks in this wave in parallel
  for task_id in "${TASKS[@]}"; do
    TYPE_VAR="TASK_${task_id}_TYPE"
    DESC_VAR="TASK_${task_id}_DESC"
    TASK_TYPE="${!TYPE_VAR}"
    TASK_DESC="${!DESC_VAR}"

    # Determine task category and build prompt
    case "$TASK_TYPE" in
      Frontend)
        TASK_PROMPT="
任务名称：$task_id
任务类型：Frontend Implementation
任务描述：$TASK_DESC

参考文档：
- 需求: .claude/$RUN_ID/requirements.md
- 架构: .claude/$RUN_ID/docs/architecture.md
- UX设计: .claude/$RUN_ID/docs/ux-design.md
- 开发计划: .claude/$RUN_ID/docs/development-plan.md

实现要求：
1. 遵循 UX 设计规格
2. 组件化开发（可复用）
3. 单元测试覆盖率 ≥ 70%
4. 代码风格一致

输出：src/frontend/, tests/frontend/
使用后端：$STAGE4_BACKEND
"
        ;;

      Backend)
        TASK_PROMPT="
任务名称：$task_id
任务类型：Backend Implementation
任务描述：$TASK_DESC

参考文档：
- 需求: .claude/$RUN_ID/requirements.md
- 架构: .claude/$RUN_ID/docs/architecture.md
- API规格: .claude/$RUN_ID/docs/api-spec.md
- 数据库设计: .claude/$RUN_ID/docs/database-schema.md
- 开发计划: .claude/$RUN_ID/docs/development-plan.md

实现要求：
1. 严格遵循 API 规格
2. 数据库 ORM/迁移脚本
3. 单元测试 + 集成测试，覆盖率 ≥ 70%
4. 错误处理和日志记录

输出：src/backend/, tests/backend/, migrations/
使用后端：$STAGE4_BACKEND
"
        ;;

      Database)
        TASK_PROMPT="
任务名称：$task_id
任务类型：Database Implementation
任务描述：$TASK_DESC

参考文档：
- 数据库设计: .claude/$RUN_ID/docs/database-schema.md
- 开发计划: .claude/$RUN_ID/docs/development-plan.md

实现要求：
1. 创建数据库迁移脚本
2. 实现 ORM 模型
3. 添加索引和约束
4. 数据 seeding 脚本

输出：migrations/, src/models/
使用后端：$STAGE4_BACKEND
"
        ;;

      Testing)
        TASK_PROMPT="
任务名称：$task_id
任务类型：Integration Testing
任务描述：$TASK_DESC

参考文档：
- API规格: .claude/$RUN_ID/docs/api-spec.md
- 开发计划: .claude/$RUN_ID/docs/development-plan.md

实现要求：
1. 测试所有相关 API endpoints
2. 测试集成流程
3. 测试错误处理
4. 使用测试数据库

输出：tests/integration/
使用后端：$STAGE4_BACKEND
"
        ;;

      *)
        TASK_PROMPT="
任务名称：$task_id
任务类型：$TASK_TYPE
任务描述：$TASK_DESC

参考所有开发文档并实现此任务。
使用后端：$STAGE4_BACKEND
"
        ;;
    esac

    # Execute task in background
    if [ "$USE_SKILL" = true ]; then
      # Use code-with-codex skill
      /skill code-with-codex "$TASK_PROMPT" \
        > .claude/$RUN_ID/logs/task_${task_id}.log 2>&1 &
    else
      # Use memex-cli directly
      memex-cli run \
        --backend $STAGE4_BACKEND \
        --prompt "$TASK_PROMPT" \
        > .claude/$RUN_ID/logs/task_${task_id}.log 2>&1 &
    fi

    TASK_PID[$task_id]=$!
    TASK_STATUS[$task_id]="running"
  done

  # Wait for all tasks in this wave to complete
  echo "⏳ 等待 Wave $((wave + 1)) 的所有任务完成..."

  WAVE_FAILED=()
  for task_id in "${TASKS[@]}"; do
    pid=${TASK_PID[$task_id]}
    wait $pid
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
      TASK_STATUS[$task_id]="completed"
      echo "  ✅ $task_id - 完成"
    else
      TASK_STATUS[$task_id]="failed"
      WAVE_FAILED+=("$task_id")
      echo "  ❌ $task_id - 失败 (退出码: $exit_code)"
    fi
  done

  # Handle wave failures
  if [ ${#WAVE_FAILED[@]} -gt 0 ]; then
    echo ""
    echo "⚠️ [ERROR] E2.2 - Wave $((wave + 1)) 部分任务失败"
    echo ""
    echo "失败任务: ${WAVE_FAILED[*]}"
    echo "查看日志："
    for task_id in "${WAVE_FAILED[@]}"; do
      echo "  - .claude/$RUN_ID/logs/task_${task_id}.log"
    done
    echo ""
    echo "处理选项："
    echo "  [1] 仅重试失败任务（推荐）"
    echo "  [2] 跳过失败任务，继续下一波次（风险高）"
    echo "  [abort] 中止工作流"
    echo ""

    read -p "请选择 [1/2/abort]: " FAILURE_CHOICE

    case "$FAILURE_CHOICE" in
      1)
        echo "重试失败任务..."
        # Retry logic here
        ;;
      2)
        echo "⚠️ 跳过失败任务，继续执行..."
        ;;
      *)
        echo "工作流已中止"
        exit 1
        ;;
    esac
  fi

  echo ""
  echo "✅ Wave $((wave + 1))/$TOTAL_WAVES 完成"
  echo ""
done

# Generate execution summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 执行总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL_TASKS=${#TASK_STATUS[@]}
COMPLETED_TASKS=0
FAILED_TASKS=0

for task_id in "${!TASK_STATUS[@]}"; do
  status=${TASK_STATUS[$task_id]}
  if [ "$status" = "completed" ]; then
    COMPLETED_TASKS=$((COMPLETED_TASKS + 1))
  elif [ "$status" = "failed" ]; then
    FAILED_TASKS=$((FAILED_TASKS + 1))
  fi
done

echo "任务总数: $TOTAL_TASKS"
echo "  ✅ 完成: $COMPLETED_TASKS"
echo "  ❌ 失败: $FAILED_TASKS"
echo "  📊 成功率: $(( COMPLETED_TASKS * 100 / TOTAL_TASKS ))%"
echo ""

# Count lines of code
TOTAL_SRC_LINES=$(find src -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.go" \) -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
TOTAL_TEST_LINES=$(find tests -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.go" \) -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')

echo "✅ Stage 4 完成 - 并行开发"
echo ""
echo "代码统计："
echo "  源代码: ${TOTAL_SRC_LINES:-0} lines"
echo "  测试: ${TOTAL_TEST_LINES:-0} lines"
echo "  执行波次: $TOTAL_WAVES"
echo ""
echo "进入 Stage 5..."
echo ""
```

**Development Plan Expected Format**:

The `development-plan.md` generated in Stage 3 should follow this structure:

```markdown
## Task: database-setup
- **Type**: Database
- **Complexity**: Medium
- **Dependencies**: None
- **Description**: Create database schema and initial migrations
- **Estimated Time**: 2 hours

## Task: backend-api-auth
- **Type**: Backend
- **Complexity**: Medium
- **Dependencies**: [database-setup]
- **Description**: Implement authentication API endpoints
- **Estimated Time**: 3 hours

## Task: backend-api-users
- **Type**: Backend
- **Complexity**: Simple
- **Dependencies**: [database-setup, backend-api-auth]
- **Description**: Implement user CRUD API endpoints
- **Estimated Time**: 2 hours

## Task: frontend-components
- **Type**: Frontend
- **Complexity**: Medium
- **Dependencies**: None
- **Description**: Create reusable UI components
- **Estimated Time**: 4 hours

## Task: frontend-auth-pages
- **Type**: Frontend
- **Complexity**: Medium
- **Dependencies**: [frontend-components, backend-api-auth]
- **Description**: Implement login and registration pages
- **Estimated Time**: 3 hours

## Task: integration-tests
- **Type**: Testing
- **Complexity**: Medium
- **Dependencies**: [backend-api-auth, backend-api-users, frontend-auth-pages]
- **Description**: Create integration tests for auth flow
- **Estimated Time**: 2 hours
```

**Dependency Graph Example**:

```
Wave 0 (parallel):
  ├─ database-setup
  └─ frontend-components

Wave 1 (parallel):
  ├─ backend-api-auth (depends on: database-setup)

Wave 2 (parallel):
  ├─ backend-api-users (depends on: database-setup, backend-api-auth)
  └─ frontend-auth-pages (depends on: frontend-components, backend-api-auth)

Wave 3 (parallel):
  └─ integration-tests (depends on: backend-api-auth, backend-api-users, frontend-auth-pages)
```

**Key Advantages**:
- ✅ Maximum parallelism within each wave
- ✅ Respects task dependencies
- ✅ Automatic wave calculation
- ✅ Clear progress tracking
- ✅ Detailed execution logs per task
- ✅ Flexible failure handling

---

## Stage 5: Coverage Validation

**Objective**: Validate test coverage ≥ 70%

**Execution**:

```bash
echo "⚙️ Stage 5 执行中 - 覆盖率验证"
echo ""

# Detect project type and run tests
if [ -f "package.json" ]; then
  # JavaScript/TypeScript
  echo "运行 JavaScript/TypeScript 测试..."
  npm test -- --coverage --coverageReporters=json --coverageReporters=text

  COVERAGE=$(jq '.total.lines.pct' coverage/coverage-summary.json)

elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  # Python
  echo "运行 Python 测试..."
  pytest --cov=src --cov-report=term --cov-report=json

  COVERAGE=$(jq '.totals.percent_covered' coverage.json)

elif [ -f "go.mod" ]; then
  # Go
  echo "运行 Go 测试..."
  go test -coverprofile=coverage.out ./...
  COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
fi

# Validate threshold
THRESHOLD=70

# Use awk for floating-point comparison (bc not always available)
if awk "BEGIN {exit !($COVERAGE >= $THRESHOLD)}"; then
  RESULT="PASS"
else
  RESULT="FAIL"
fi

# Generate coverage report
cat > .claude/$RUN_ID/coverage-report.md <<EOF
# Test Coverage Report

## Summary
- **Total Coverage**: ${COVERAGE}%
- **Threshold**: ${THRESHOLD}%
- **Result**: **$RESULT**

## Coverage by Module
\`\`\`
$(if [ -f "coverage/coverage-summary.json" ]; then
  jq -r '.[] | "\(.path): \(.lines.pct)%"' coverage/coverage-summary.json
elif [ -f "coverage.json" ]; then
  jq -r '.files | to_entries[] | "\(.key): \(.value.summary.percent_covered)%"' coverage.json
fi)
\`\`\`

## Recommendations
$(if [ "$RESULT" = "FAIL" ]; then
  echo "### 低覆盖模块"
  if [ -f "coverage.json" ]; then
    jq -r '.files | to_entries[] | select(.value.summary.percent_covered < 70) |
      "- \(.key): \(.value.summary.percent_covered)%"' coverage.json
  fi
  echo ""
  echo "### 建议操作"
  echo "1. 增加单元测试覆盖关键业务逻辑"
  echo "2. 添加边界条件测试（空值、最大值、非法输入）"
  echo "3. 补充错误处理测试"
fi)

## Generated
- Timestamp: $(date "+%Y-%m-%dT%H:%M:%S%z")
- RUN_ID: $RUN_ID
EOF

echo "✅ Stage 5 完成 - 覆盖率验证"
echo ""
echo "测试覆盖率: ${COVERAGE}% (目标 ≥${THRESHOLD}%)"
echo "覆盖率报告: .claude/$RUN_ID/coverage-report.md"
echo ""

if [ "$RESULT" = "FAIL" ]; then
  echo "⚠️ 覆盖率未达标"
  echo ""
fi
```

**User Gate 3**:

```bash
# Use AskUserQuestion
```

```json
{
  "questions": [
    {
      "question": "Stage 5 覆盖率验证已完成，请审查并选择操作",
      "header": "Stage 5 Gate",
      "multiSelect": false,
      "options": [
        {
          "label": "Pass - 通过验证",
          "description": "覆盖率达标或接受当前覆盖率，进入 Stage 6"
        },
        {
          "label": "Fix-and-Retry - 补充测试",
          "description": "补充测试用例后重新验证覆盖率"
        },
        {
          "label": "Abort - 中止工作流",
          "description": "暂停工作流，保存当前进度"
        }
      ]
    }
  ]
}
```

Handle response:

```bash
case "$GATE3_RESPONSE" in
  "Pass"*)
    echo "收到批准，进入 Stage 6..."
    ;;
  "Fix-and-Retry"*)
    echo "请补充测试后，重新运行 Stage 5"
    echo ""
    echo "重新验证:"
    # Re-run coverage validation
    ;;
  "Abort"*)
    echo "工作流已中止，进度已保存: .claude/$RUN_ID/"
    exit 0
    ;;
esac
```

---

## Stage 6: Completion Summary

**Objective**: Generate delivery report

**Execution**:

```bash
echo "⚙️ Stage 6 执行中 - 完成总结"
echo ""

# Collect statistics
TOTAL_FILES=$(find src -type f | wc -l)
TOTAL_LINES=$(find src -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.go" \) -exec wc -l {} + | tail -1 | awk '{print $1}')
TEST_FILES=$(find tests -type f | wc -l)

# Generate delivery report
cat > .claude/$RUN_ID/DELIVERY_REPORT.md <<EOF
# Project Delivery Report

## Project Information
- **Name**: $(grep -m1 "项目\|Project" .claude/$RUN_ID/requirements.md | sed 's/^[#*-] *//')
- **Type**: $ARCH_TYPE
- **Delivery Date**: $(date +%Y-%m-%d)
- **RUN_ID**: $RUN_ID

## Deliverables

### 1. Documentation
- ✓ requirements.md - 需求文档
- ✓ architecture.md - 架构设计
- ✓ api-spec.md - API 规格
$([ "$ARCH_TYPE" != "Backend" ] && echo "- ✓ ux-design.md - UX 设计")
- ✓ database-schema.md - 数据库设计
- ✓ development-plan.md - 开发计划

### 2. Source Code
- **Total Files**: $TOTAL_FILES
- **Total Lines**: $TOTAL_LINES
- **Directory Structure**:
\`\`\`
$(if command -v tree &> /dev/null; then
  tree -L 2 src/ 2>/dev/null
else
  # Fallback: use find with formatted output
  find src -maxdepth 2 -type d | sed 's|src/|  |; s|/|  |g' | sort
fi)
\`\`\`

### 3. Test Suite
- **Test Files**: $TEST_FILES
- **Coverage**: ${COVERAGE}%
- **Status**: $([ "$RESULT" = "PASS" ] && echo "✅ PASS" || echo "⚠️ BELOW THRESHOLD")

## Quality Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Code Coverage | ${COVERAGE}% | $(awk "BEGIN {exit !($COVERAGE >= 70)}" && echo "✅" || echo "⚠️") |
| Documentation | Complete | ✅ |
| Architecture Type | $ARCH_TYPE | ✅ |

## Next Steps
1. **Code Review**: 审查关键模块代码质量
2. **Performance Test**: 执行性能测试和优化
3. **Security Audit**: 进行安全审计（依赖扫描、漏洞检测）
4. **Deployment**: 部署到测试环境
5. **User Acceptance**: 用户验收测试

## Related Files
- Project Root: $(pwd)
- Documentation: .claude/$RUN_ID/docs/
- Source Code: src/
- Tests: tests/
- Coverage Report: .claude/$RUN_ID/coverage-report.md

---
Generated by /multcode on $(date)
EOF

echo "✅ Stage 6 完成 - 项目交付"
echo ""
echo "🎉 项目交付完成"
echo ""
echo "统计:"
echo "  - 源代码文件: $TOTAL_FILES 个"
echo "  - 代码行数: $TOTAL_LINES 行"
echo "  - 测试文件: $TEST_FILES 个"
echo "  - 测试覆盖率: ${COVERAGE}%"
echo ""
echo "交付报告: .claude/$RUN_ID/DELIVERY_REPORT.md"
echo ""
echo "所有阶段已完成！"
echo ""
```

---

## Error Handling Rules

### E1.1: memex-cli 未安装 (FATAL)
```bash
if ! command -v memex-cli &> /dev/null; then
  echo "❌ [FATAL] E1.1 - memex-cli 未安装"
  echo "解决: npm install -g memex-cli"
  exit 1
fi
```

### E1.2: Skill 不可用 (ERROR)
```bash
# Retry strategy: 2 attempts with 3s delay
MAX_RETRIES=2
for i in $(seq 1 $MAX_RETRIES); do
  /skill code-with-codex "$PROMPT"
  [ $? -eq 0 ] && break
  [ $i -lt $MAX_RETRIES ] && sleep 3
done

# Fallback: use memex-cli directly if skill fails
if [ $? -ne 0 ]; then
  echo "⚠️ [ERROR] E1.2 - Skill 调用失败，降级到 memex-cli"
  memex-cli run --backend codex --prompt "$PROMPT"
fi
```

### E2.1: memex-cli 执行失败 (ERROR)
```bash
# Smart backoff: 2s, 4s, 8s
retry_with_backoff() {
  local max_retries=3
  for attempt in $(seq 1 $max_retries); do
    memex-cli run --backend claude --prompt "$PROMPT"
    [ $? -eq 0 ] && return 0

    local delay=$((2 ** attempt))
    [ $attempt -lt $max_retries ] && sleep $delay
  done

  echo "❌ [ERROR] E2.1 - memex-cli 失败（已重试 $max_retries 次）"
  return 1
}
```

### E2.2: 并行任务部分失败 (ERROR)
```bash
# Check parallel task exits
FAILED_TASKS=()
[ $FRONTEND_EXIT -ne 0 ] && FAILED_TASKS+=("Frontend")
[ $BACKEND_EXIT -ne 0 ] && FAILED_TASKS+=("Backend")

if [ ${#FAILED_TASKS[@]} -gt 0 ]; then
  echo "⚠️ [ERROR] E2.2 - 部分任务失败: ${FAILED_TASKS[*]}"
  echo "处理选项: [1] 仅重试失败任务 [2] 重新执行全部 [abort] 中止"
fi
```

### E3.1: 覆盖率不达标 (WARNING)
```bash
# Use awk for floating-point comparison (bc not always available)
if awk "BEGIN {exit !($COVERAGE < 70)}"; then
  echo "⚠️ [WARNING] E3.1 - 覆盖率未达标: ${COVERAGE}%"
  echo "低覆盖模块："
  jq -r '.files | to_entries[] | select(.value.summary.percent_covered < 70) |
    "  - \(.key): \(.value.summary.percent_covered)%"' coverage.json
  echo "建议: 补充单元测试、边界测试、错误处理测试"
fi
```

### E4.1: 用户闸门超时 (INFO)
```bash
# 15-minute timeout on user gates
read -t 900 -p "请选择 [approve/revise/abort]: " RESPONSE

if [ $? -ne 0 ]; then
  echo "⏱️ [INFO] E4.1 - 用户闸门超时（15分钟）"
  echo "进度已保存: .claude/$RUN_ID/"
  echo "恢复: /multcode-resume $RUN_ID"
  exit 0
fi
```

---

## Quality Standards

### Q1: Code Quality
- **Complexity**: Average ≤ 8, Max ≤ 15 per function
- **Style**: Pylint ≥ 8.0 (Python), ESLint errors = 0 (JS)
- **Duplication**: ≤ 3% code duplication rate

### Q2: Security
- **Vulnerabilities**: 0 critical/high vulnerabilities
- **Secrets**: No hardcoded secrets
- **Input Validation**: All user inputs validated

### Q3: Test Quality
- **Coverage**: Line ≥ 70%, Branch ≥ 60%, Function ≥ 80%
- **Stability**: 0 flaky tests (consistent across 3 runs)
- **Types**: Unit ≥ 60%, Integration ≥ 30%, E2E ≥ 10%

### Q4: Documentation
- **Completeness**: README + Architecture + API docs (if applicable)
- **Accuracy**: API docs match implementation (100%)
- **Code Docs**: Public API docstrings (100%)

### Q5: Deployability
- **Containerization**: Dockerfile builds successfully (if applicable)
- **Configuration**: All secrets via env vars (12-factor compliant)
- **Observability**: Structured logging + health checks

**Quality Score** = Code(25%) + Tests(30%) + Docs(15%) + Security(20%) + Deploy(10%)
- 🏆 Excellent: ≥ 80
- ✅ Good: 70-79
- ⚠️ Pass: 60-69
- ❌ Fail: < 60

---

## Communication Style

### C1: Progress Notification
```
Format: ⚙️ Stage X 执行中 - <name>
Content: Task + progress bar
Example:
  ⚙️ Stage 3 执行中 - 生成开发文档
  [✓] architecture.md
  [进行中] api-spec.md (60%)
  [等待] ux-design.md
```

### C2: Stage Completion
```
Format: ✅ Stage X 完成 - <name>
Content: Key outputs + stats + next step
Example:
  ✅ Stage 4 完成 - 并行开发
  代码: 3,692 lines
  测试: 891 lines
  进入 Stage 5...
```

### C3: Error Report
```
Format: ❌/⚠️ [ERROR/WARNING] E<code> - <type>
Content: Details + reason + solutions (max 3)
Example:
  ❌ [ERROR] E2.1 - memex-cli 执行失败
  原因: Rate Limit Exceeded
  解决: [1] 等待60s重试 [2] 切换后端 [abort] 中止
```

### C4: User Gate
```
Format: [USER GATE X] <name>
Content: Outputs + 3 fixed options
Options: Approve / Revise / Abort
Example:
  [USER GATE 2] 文档审查
  产出: architecture.md, api-spec.md, ux-design.md
  [approve/revise/abort]: _
```

### C5: Final Summary
```
Format: 🎉 项目交付完成
Content: Stats + deliverables + next steps (max 3)
Example:
  🎉 项目交付完成
  统计: 3,692 lines, 72% coverage
  交付物: docs/, src/, tests/
  下一步: 1.代码审查 2.性能测试 3.部署测试环境
```

---

## Notes

**Key Improvements from v2**:
- ✅ Reduced user gates: 5 → 3 (40% less interaction)
- ✅ Centralized doc generation: S1+S2+S3+S4 → S3
- ✅ Parallel development: Frontend + Backend + Tests in parallel
- ✅ Independent coverage validation: Mandatory ≥70% threshold
- ✅ Clear rules: Error handling (6), Quality (5 dimensions), Communication (5 formats)

**Execution Time**:
- Original: ~20 minutes (5 serial stages + 5 gates)
- Optimized: ~12 minutes (doc centralization + parallel dev + 3 gates)

**Related Commands**:
- `/bmad` - Full BMAD workflow (for new projects from scratch)
- `/quick-feature` - Quick feature development (for small tasks)
- `/code-review` - Code review and quality analysis
