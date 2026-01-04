# MasterOrchestrator + aduib-ai 整合设计

**目标**: 将 aduib-ai 作为 MasterOrchestrator 的统一后端服务层，替代当前的 memex-cli 调用方式。

**日期**: 2026-01-04

---

## 目录

- [整合架构](#整合架构)
- [aduib-ai 功能分析](#aduib-ai-功能分析)
- [整合方案](#整合方案)
- [Phase 5 重新设计](#phase-5-重新设计)
- [Phase 6 重新设计](#phase-6-重新设计)
- [实施路线图](#实施路线图)
- [API 设计](#api-设计)
- [数据模型设计](#数据模型设计)

---

## 整合架构

### 当前架构 (Phase 1-4)

```
MasterOrchestrator (CLI/Python API)
  ↓
ExecutionRouter
  ↓
BackendOrchestrator
  ↓
memex-cli (调用 Claude/Gemini/Codex)
```

**问题**:
- 依赖 memex-cli（Node.js 工具）
- 无持久化、无缓存
- 无 API Key 管理
- 无多租户支持
- 无 Web UI

---

### 目标架构 (Phase 5-6 整合 aduib-ai)

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI 工具    │  │  Python API  │  │   Web UI     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              MasterOrchestrator (核心协调层)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │IntentAnalyzer│  │ExecutionRouter│ │DevWorkflowAgent│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              aduib-ai 后端服务层 (新增)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API 网关    │  │  服务层      │  │  数据层      │      │
│  │ (FastAPI)    │  │ (Services)   │  │ (PostgreSQL) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│  ┌──────▼─────────────────▼──────────────────▼────────┐     │
│  │              核心功能模块                           │     │
│  │  • 模型管理 (Claude/Gemini/Codex)                   │     │
│  │  • API Key 管理 (多租户)                            │     │
│  │  • 任务历史 (持久化)                                │     │
│  │  • 结果缓存 (Redis)                                 │     │
│  │  • 向量数据库 (知识检索)                            │     │
│  │  • 文件存储 (本地/S3)                               │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  AI 模型服务提供商                           │
│    Claude API    │    Gemini API    │    Codex API          │
└─────────────────────────────────────────────────────────────┘
```

**优势**:
- ✅ **统一后端** - aduib-ai 管理所有 AI 模型调用
- ✅ **持久化** - PostgreSQL 存储任务历史、用户数据
- ✅ **缓存** - Redis 缓存结果，提升性能
- ✅ **多租户** - API Key 管理，支持多用户
- ✅ **向量数据库** - 知识检索和 RAG
- ✅ **文件管理** - 上传代码、文档供 AI 分析
- ✅ **Web UI** - aduib-ai 提供 REST API，前端调用

---

## aduib-ai 功能分析

### 核心模块映射

| aduib-ai 模块 | 功能 | 用于 MasterOrchestrator |
|---------------|------|-------------------------|
| **models/** | 模型定义 (API Key, Engine, Models, Providers) | 管理 Claude/Gemini/Codex 配置 |
| **service/** | 业务逻辑 (API Key, Completion, Model, Provider) | 任务执行、模型调用、结果管理 |
| **controllers/** | API 端点 | 提供 REST API 给前端和 MasterOrchestrator |
| **component/storage/** | 多存储支持 (本地/S3/OpenDAL) | 存储工作流输出、代码文件 |
| **component/vector_db/** | 向量数据库 | 知识检索、相似任务推荐 |
| **configs/** | 配置管理 | 数据库、CORS、部署配置 |
| **alembic/** | 数据库迁移 | 版本管理、Schema 演进 |
| **runtime/** | 模型运行时 | 回调、客户端管理 |

### 扩展需求

为支持 MasterOrchestrator，需在 aduib-ai 中新增：

1. **任务模型** (Task Model)
   - 存储 MasterOrchestrator 的任务请求和结果
   - 关联 WorkflowResult, TaskResult 等

2. **工作流模型** (Workflow Model)
   - 5 阶段工作流的状态管理
   - 阶段间数据传递

3. **缓存服务** (Cache Service)
   - 基于请求哈希的结果缓存
   - TTL 管理

4. **向量检索服务** (Vector Search Service)
   - 相似任务推荐
   - 历史结果检索

---

## 整合方案

### 方案 1: REST API 调用（推荐）

**架构**:
```
MasterOrchestrator → HTTP/REST → aduib-ai API → AI Models
```

**优势**:
- 解耦：MasterOrchestrator 和 aduib-ai 独立部署
- 标准化：使用 REST API 通信
- 可扩展：aduib-ai 可服务多个客户端

**实现**:

```python
# 新建 aduib_client.py
import requests
from typing import Dict, Any

class AduibClient:
    """aduib-ai 后端客户端"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def create_task(self, request: str, mode: str, backend: str) -> Dict[str, Any]:
        """创建任务"""
        response = requests.post(
            f"{self.base_url}/api/tasks",
            json={
                "request": request,
                "mode": mode,
                "backend": backend
            },
            headers={"X-API-Key": self.api_key}
        )
        return response.json()

    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        response = requests.get(
            f"{self.base_url}/api/tasks/{task_id}",
            headers={"X-API-Key": self.api_key}
        )
        return response.json()

    def execute_workflow(self, requirement: str, stages: List[str]) -> Dict[str, Any]:
        """执行 5 阶段工作流"""
        response = requests.post(
            f"{self.base_url}/api/workflows",
            json={
                "requirement": requirement,
                "stages": stages
            },
            headers={"X-API-Key": self.api_key}
        )
        return response.json()
```

**BackendOrchestrator 更新**:

```python
# 替换 memex-cli 调用
class BackendOrchestrator:
    def __init__(self, aduib_url: str, api_key: str):
        self.client = AduibClient(aduib_url, api_key)

    def run_task(self, backend: str, prompt: str) -> TaskResult:
        """通过 aduib-ai 执行任务"""
        # 创建任务
        task = self.client.create_task(
            request=prompt,
            mode="backend",
            backend=backend
        )

        task_id = task["task_id"]

        # 轮询结果（或使用 WebSocket）
        result = self.client.get_task_result(task_id)

        return TaskResult(
            success=result["success"],
            output=result["output"],
            events=result.get("events", []),
            run_id=task_id
        )
```

---

### 方案 2: Python SDK 直接集成

**架构**:
```
MasterOrchestrator → Python SDK → aduib-ai Core → AI Models
```

**优势**:
- 性能：无 HTTP 开销
- 简单：同一进程内调用

**缺点**:
- 耦合：MasterOrchestrator 依赖 aduib-ai 代码
- 部署复杂：需同时部署两个系统

**实现**:

```python
# 直接导入 aduib-ai 服务
from service.completion import CompletionService
from models.models import Model

class BackendOrchestrator:
    def __init__(self):
        self.completion_service = CompletionService()

    def run_task(self, backend: str, prompt: str) -> TaskResult:
        # 直接调用 aduib-ai 服务
        model = Model.get_by_name(backend)  # claude, gemini, codex
        result = self.completion_service.complete(
            model=model,
            prompt=prompt
        )
        return TaskResult(
            success=True,
            output=result.content,
            events=[],
            run_id=result.id
        )
```

---

### 推荐方案：REST API 调用

理由：
- ✅ 解耦部署
- ✅ 支持 Web UI（前端直接调用同一 API）
- ✅ 易于水平扩展
- ✅ 标准化接口

---

## Phase 5 重新设计

### Phase 5: aduib-ai 后端集成 + 持久化

**目标**:
1. 将 MasterOrchestrator 迁移到 aduib-ai 后端
2. 实现任务历史持久化
3. 添加结果缓存
4. 支持多租户（API Key）

---

### 5.1 aduib-ai 扩展开发

#### 新增数据模型

**文件**: `aduib-ai/models/task.py`

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, JSON
from models.base import BaseModel

class Task(BaseModel):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)  # API Key 关联的用户
    request = Column(Text, nullable=False)         # 用户请求
    mode = Column(String(32), nullable=False)      # command, agent, prompt, skill, backend
    backend = Column(String(32), nullable=True)    # claude, gemini, codex
    status = Column(String(32), default="pending") # pending, running, completed, failed
    result = Column(JSON, nullable=True)           # TaskResult/WorkflowResult JSON
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)

class Workflow(BaseModel):
    """工作流模型"""
    __tablename__ = "workflows"

    id = Column(String(64), primary_key=True)
    task_id = Column(String(64), nullable=False)
    requirement = Column(Text, nullable=False)
    current_stage = Column(Integer, default=0)     # 0-4 对应 5 个阶段
    stages_data = Column(JSON, nullable=True)      # 各阶段输出
    status = Column(String(32), default="pending")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ResultCache(BaseModel):
    """结果缓存"""
    __tablename__ = "result_cache"

    request_hash = Column(String(64), primary_key=True)  # SHA256(request + mode + backend)
    result = Column(JSON, nullable=False)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
```

---

#### 新增服务层

**文件**: `aduib-ai/service/task_service.py`

```python
from models.task import Task, Workflow, ResultCache
from service.completion import CompletionService
from datetime import datetime, timedelta
import hashlib
import json

class TaskService:
    """任务服务"""

    def __init__(self):
        self.completion_service = CompletionService()

    def create_task(self, user_id: str, request: str, mode: str, backend: str) -> Task:
        """创建任务"""
        # 检查缓存
        cached = self._get_cached_result(request, mode, backend)
        if cached:
            return self._create_task_from_cache(user_id, request, cached)

        # 创建新任务
        task = Task(
            id=generate_id(),
            user_id=user_id,
            request=request,
            mode=mode,
            backend=backend,
            status="pending"
        )
        task.save()
        return task

    def execute_task(self, task_id: str) -> Task:
        """执行任务"""
        task = Task.get(task_id)
        task.status = "running"
        task.save()

        try:
            # 调用 AI 模型
            result = self.completion_service.complete(
                model=task.backend,
                prompt=task.request
            )

            # 保存结果
            task.result = {
                "success": True,
                "output": result.content,
                "run_id": result.id
            }
            task.status = "completed"
            task.completed_at = datetime.now()

            # 写入缓存
            self._cache_result(task.request, task.mode, task.backend, task.result)

        except Exception as e:
            task.result = {"success": False, "error": str(e)}
            task.status = "failed"

        task.save()
        return task

    def _get_cached_result(self, request: str, mode: str, backend: str) -> dict:
        """获取缓存结果"""
        request_hash = self._compute_hash(request, mode, backend)
        cache = ResultCache.get(request_hash)

        if cache and cache.expires_at > datetime.now():
            cache.hit_count += 1
            cache.save()
            return cache.result

        return None

    def _cache_result(self, request: str, mode: str, backend: str, result: dict):
        """缓存结果"""
        request_hash = self._compute_hash(request, mode, backend)
        cache = ResultCache(
            request_hash=request_hash,
            result=result,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)  # 1 小时过期
        )
        cache.save()

    def _compute_hash(self, request: str, mode: str, backend: str) -> str:
        """计算请求哈希"""
        data = f"{request}|{mode}|{backend}"
        return hashlib.sha256(data.encode()).hexdigest()
```

**文件**: `aduib-ai/service/workflow_service.py`

```python
class WorkflowService:
    """工作流服务"""

    def __init__(self):
        self.task_service = TaskService()

    def create_workflow(self, user_id: str, requirement: str) -> Workflow:
        """创建 5 阶段工作流"""
        # 创建任务
        task = self.task_service.create_task(user_id, requirement, "skill", None)

        # 创建工作流
        workflow = Workflow(
            id=generate_id(),
            task_id=task.id,
            requirement=requirement,
            current_stage=0,
            stages_data={},
            status="pending"
        )
        workflow.save()
        return workflow

    def execute_workflow(self, workflow_id: str) -> Workflow:
        """执行工作流"""
        workflow = Workflow.get(workflow_id)
        workflow.status = "running"
        workflow.save()

        stages = [
            ("requirements", "claude"),
            ("feature_design", "claude"),
            ("ux_design", "gemini"),
            ("dev_plan", "codex"),
            ("implementation", "codex")
        ]

        for i, (stage_name, backend) in enumerate(stages):
            if i < workflow.current_stage:
                continue  # 跳过已完成阶段

            # 构建提示词（包含前序阶段输出）
            prompt = self._build_stage_prompt(
                stage_name,
                workflow.requirement,
                workflow.stages_data
            )

            # 执行阶段
            result = self.task_service.completion_service.complete(
                model=backend,
                prompt=prompt
            )

            # 保存阶段结果
            workflow.stages_data[stage_name] = {
                "output": result.content,
                "backend": backend,
                "completed_at": datetime.now().isoformat()
            }
            workflow.current_stage = i + 1
            workflow.save()

        workflow.status = "completed"
        workflow.save()
        return workflow

    def _build_stage_prompt(self, stage: str, requirement: str, previous_data: dict) -> str:
        """构建阶段提示词"""
        # 复用 MasterOrchestrator 的 STAGE_CONFIG
        from auto_workflow import DevWorkflowAgent
        config = DevWorkflowAgent.STAGE_CONFIG[WorkflowStage[stage.upper()]]

        variables = {
            "requirement": requirement,
            "previous_output": previous_data.get(stage, {}).get("output", ""),
            "feature_design": previous_data.get("feature_design", {}).get("output", ""),
            "ux_design": previous_data.get("ux_design", {}).get("output", ""),
        }

        return config["prompt_template"].format(**variables)
```

---

#### 新增 API 端点

**文件**: `aduib-ai/controllers/task_controller.py`

```python
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from service.task_service import TaskService
from service.workflow_service import WorkflowService

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
task_service = TaskService()
workflow_service = WorkflowService()

class CreateTaskRequest(BaseModel):
    request: str
    mode: str
    backend: str

@router.post("")
async def create_task(data: CreateTaskRequest, x_api_key: str = Header(...)):
    """创建任务"""
    user_id = verify_api_key(x_api_key)  # 验证 API Key
    task = task_service.create_task(user_id, data.request, data.mode, data.backend)

    # 异步执行任务
    background_task(task_service.execute_task, task.id)

    return {"task_id": task.id, "status": task.status}

@router.get("/{task_id}")
async def get_task(task_id: str, x_api_key: str = Header(...)):
    """获取任务结果"""
    user_id = verify_api_key(x_api_key)
    task = Task.get(task_id)

    if task.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }

# 工作流 API
workflow_router = APIRouter(prefix="/api/workflows", tags=["Workflows"])

class CreateWorkflowRequest(BaseModel):
    requirement: str

@workflow_router.post("")
async def create_workflow(data: CreateWorkflowRequest, x_api_key: str = Header(...)):
    """创建工作流"""
    user_id = verify_api_key(x_api_key)
    workflow = workflow_service.create_workflow(user_id, data.requirement)

    # 异步执行
    background_task(workflow_service.execute_workflow, workflow.id)

    return {"workflow_id": workflow.id, "status": workflow.status}

@workflow_router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, x_api_key: str = Header(...)):
    """获取工作流状态"""
    user_id = verify_api_key(x_api_key)
    workflow = Workflow.get(workflow_id)

    return {
        "workflow_id": workflow.id,
        "status": workflow.status,
        "current_stage": workflow.current_stage,
        "stages_data": workflow.stages_data
    }
```

---

### 5.2 MasterOrchestrator 适配

**文件**: `master_orchestrator.py` 更新

```python
from aduib_client import AduibClient

class MasterOrchestrator:
    def __init__(self, aduib_url: str = "http://localhost:8000", api_key: str = None):
        """
        初始化（使用 aduib-ai 后端）

        Args:
            aduib_url: aduib-ai 后端 URL
            api_key: API Key（从环境变量或配置读取）
        """
        self.aduib_client = AduibClient(aduib_url, api_key)
        self.analyzer = IntentAnalyzer()
        self.router = ExecutionRouter(self.aduib_client)

    def process(self, request: str, verbose: bool = False) -> Any:
        """处理请求"""
        # 1. 意图分析
        intent = self.analyzer.analyze(request)

        if verbose:
            print(f"[意图分析] 模式={intent.mode.value}, 类型={intent.task_type}")

        # 2. 根据模式调用 aduib-ai API
        if intent.mode == ExecutionMode.SKILL and intent.complexity == "complex":
            # 调用工作流 API
            workflow = self.aduib_client.create_workflow(request)
            workflow_id = workflow["workflow_id"]

            # 轮询状态
            result = self._wait_for_workflow(workflow_id, verbose)
            return result

        else:
            # 调用任务 API
            backend = self._select_backend(intent)
            task = self.aduib_client.create_task(request, intent.mode.value, backend)
            task_id = task["task_id"]

            # 轮询状态
            result = self._wait_for_task(task_id, verbose)
            return result

    def _wait_for_workflow(self, workflow_id: str, verbose: bool) -> WorkflowResult:
        """等待工作流完成"""
        import time
        while True:
            workflow = self.aduib_client.get_workflow(workflow_id)
            status = workflow["status"]

            if verbose and status == "running":
                stage = workflow["current_stage"]
                print(f"[工作流] 阶段 {stage}/5 执行中...")

            if status in ["completed", "failed"]:
                return self._parse_workflow_result(workflow)

            time.sleep(2)  # 轮询间隔
```

---

### 5.3 数据库迁移

**文件**: `aduib-ai/alembic/versions/xxx_add_task_models.py`

```python
"""add task models

Revision ID: xxx
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建 tasks 表
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.String(64), nullable=False),
        sa.Column('request', sa.Text, nullable=False),
        sa.Column('mode', sa.String(32), nullable=False),
        sa.Column('backend', sa.String(32)),
        sa.Column('status', sa.String(32), default='pending'),
        sa.Column('result', sa.JSON),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime)
    )

    # 创建 workflows 表
    op.create_table(
        'workflows',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('task_id', sa.String(64), nullable=False),
        sa.Column('requirement', sa.Text, nullable=False),
        sa.Column('current_stage', sa.Integer, default=0),
        sa.Column('stages_data', sa.JSON),
        sa.Column('status', sa.String(32), default='pending'),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )

    # 创建 result_cache 表
    op.create_table(
        'result_cache',
        sa.Column('request_hash', sa.String(64), primary_key=True),
        sa.Column('result', sa.JSON, nullable=False),
        sa.Column('hit_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime),
        sa.Column('expires_at', sa.DateTime)
    )

def downgrade():
    op.drop_table('result_cache')
    op.drop_table('workflows')
    op.drop_table('tasks')
```

---

## Phase 6 重新设计

### Phase 6: Web UI 开发

**目标**: 基于 aduib-ai 的 REST API 开发 Web 界面

---

### 6.1 前端技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 库**: Tailwind CSS + shadcn-vue
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **实时通信**: Socket.IO (可选，用于任务进度推送)

---

### 6.2 页面设计

#### 主界面

```
┌─────────────────────────────────────────────────────────────┐
│  MasterOrchestrator                          [API Key] [退出] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  请输入您的需求：                                        │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │ 开发一个博客系统，支持文章发布、评论、用户管理...    ││ │
│  │  │                                                      ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  │                                                          │ │
│  │  执行模式: [自动识别 ▼]  后端: [自动选择 ▼]             │ │
│  │  [ ] 详细模式  超时: [600] 秒                            │ │
│  │                                                          │ │
│  │  [执行任务]  [清空]                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  最近任务                                    [查看全部历史]   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 2026-01-04 10:30  开发博客系统         ✓ 成功  [查看]   │ │
│  │ 2026-01-03 15:20  代码审查 auth.py     ✓ 成功  [查看]   │ │
│  │ 2026-01-03 14:10  查找API端点          ✓ 成功  [查看]   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 任务执行页面

```
┌─────────────────────────────────────────────────────────────┐
│  任务执行中...                                  [< 返回首页]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  需求: 开发一个博客系统，支持文章发布、评论、用户管理         │
│  模式: 5阶段工作流  开始时间: 2026-01-04 10:30:15           │
│                                                               │
│  执行进度                                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ✓ 阶段 1: 需求分析              (45.3s)                │ │
│  │  ✓ 阶段 2: 功能设计              (62.1s)                │ │
│  │  ⏳ 阶段 3: UX设计               (进行中... 23s)        │ │
│  │  ⏸ 阶段 4: 开发计划                                     │ │
│  │  ⏸ 阶段 5: 代码实现                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  阶段详情                                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  [需求分析] [功能设计] [UX设计] [开发计划] [代码实现]   │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  阶段 1: 需求分析 (Claude)                               │ │
│  │                                                          │ │
│  │  核心需求：                                              │ │
│  │  - 用户可以发布文章（Markdown 编辑器）                   │ │
│  │  - 用户可以评论文章                                      │ │
│  │  - 管理员可以管理用户和内容                              │ │
│  │                                                          │ │
│  │  用户画像：                                              │ │
│  │  - 主要用户：博客作者、读者                              │ │
│  │  - 使用场景：PC 端为主                                   │ │
│  │  ...                                                     │ │
│  │                                                          │ │
│  │  [复制] [导出 Markdown]                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 任务历史页面

```
┌─────────────────────────────────────────────────────────────┐
│  任务历史                                       [< 返回首页]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  筛选: [全部模式 ▼] [全部状态 ▼] [最近7天 ▼]  [搜索...]     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 时间           │ 请求摘要       │ 模式   │ 状态 │ 操作  │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │ 01-04 10:30   │ 开发博客系统   │ Skill  │ ✓    │ 查看  │ │
│  │ 01-03 15:20   │ 代码审查       │ Prompt │ ✓    │ 查看  │ │
│  │ 01-03 14:10   │ 查找API端点    │ Agent  │ ✓    │ 查看  │ │
│  │ 01-03 11:05   │ 运行测试       │Command │ ✓    │ 查看  │ │
│  │ 01-02 16:30   │ 开发电商平台   │ Skill  │ ✗    │ 重试  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  [上一页] 第 1/5 页 [下一页]                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 6.3 前端代码示例

**API 客户端** (`src/api/client.ts`):

```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'X-API-Key': localStorage.getItem('apiKey') || ''
  }
})

export const taskAPI = {
  // 创建任务
  createTask(request: string, mode: string, backend: string) {
    return client.post('/tasks', { request, mode, backend })
  },

  // 获取任务结果
  getTask(taskId: string) {
    return client.get(`/tasks/${taskId}`)
  },

  // 获取任务历史
  getTasks(filters?: any) {
    return client.get('/tasks', { params: filters })
  }
}

export const workflowAPI = {
  // 创建工作流
  createWorkflow(requirement: string) {
    return client.post('/workflows', { requirement })
  },

  // 获取工作流状态
  getWorkflow(workflowId: string) {
    return client.get(`/workflows/${workflowId}`)
  }
}
```

**任务执行页面** (`src/views/TaskExecution.vue`):

```vue
<template>
  <div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">任务执行中...</h1>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <p class="text-gray-700"><strong>需求:</strong> {{ workflow.requirement }}</p>
      <p class="text-gray-600">模式: 5阶段工作流</p>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">执行进度</h2>

      <div v-for="(stage, index) in stages" :key="index" class="mb-3">
        <div class="flex items-center gap-3">
          <span v-if="workflow.current_stage > index" class="text-green-500">✓</span>
          <span v-else-if="workflow.current_stage === index" class="text-blue-500">⏳</span>
          <span v-else class="text-gray-400">⏸</span>

          <span class="font-medium">阶段 {{ index + 1 }}: {{ stage.name }}</span>

          <span v-if="workflow.stages_data[stage.key]" class="text-gray-500">
            ({{ workflow.stages_data[stage.key].duration }}s)
          </span>
        </div>
      </div>
    </div>

    <div v-if="workflow.current_stage > 0" class="bg-white rounded-lg shadow p-6 mt-6">
      <h2 class="text-xl font-semibold mb-4">阶段详情</h2>

      <div v-for="(stage, index) in completedStages" :key="index" class="mb-6">
        <h3 class="font-semibold">{{ stage.name }}</h3>
        <pre class="bg-gray-100 p-4 rounded mt-2 overflow-auto">{{ stage.output }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { workflowAPI } from '@/api/client'

const route = useRoute()
const workflowId = route.params.id as string

const workflow = ref({
  requirement: '',
  current_stage: 0,
  stages_data: {},
  status: 'pending'
})

const stages = [
  { key: 'requirements', name: '需求分析' },
  { key: 'feature_design', name: '功能设计' },
  { key: 'ux_design', name: 'UX设计' },
  { key: 'dev_plan', name: '开发计划' },
  { key: 'implementation', name: '代码实现' }
]

const completedStages = computed(() => {
  return stages
    .filter((_, index) => index < workflow.value.current_stage)
    .map(stage => ({
      name: stage.name,
      output: workflow.value.stages_data[stage.key]?.output || ''
    }))
})

const fetchWorkflow = async () => {
  const response = await workflowAPI.getWorkflow(workflowId)
  workflow.value = response.data
}

// 轮询更新
let intervalId: any
onMounted(() => {
  fetchWorkflow()

  intervalId = setInterval(() => {
    fetchWorkflow()
    if (workflow.value.status === 'completed' || workflow.value.status === 'failed') {
      clearInterval(intervalId)
    }
  }, 2000)
})
</script>
```

---

## 实施路线图

### Phase 5: aduib-ai 后端集成 (预计 3-4 周)

**Week 1-2: aduib-ai 扩展开发**
- [ ] 设计数据模型（Task, Workflow, ResultCache）
- [ ] 实现服务层（TaskService, WorkflowService）
- [ ] 添加 API 端点（TaskController, WorkflowController）
- [ ] 数据库迁移脚本
- [ ] 单元测试

**Week 3: MasterOrchestrator 适配**
- [ ] 开发 AduibClient
- [ ] 更新 BackendOrchestrator
- [ ] 更新 DevWorkflowAgent
- [ ] 集成测试

**Week 4: 部署和文档**
- [ ] Docker 容器化
- [ ] 部署到测试环境
- [ ] API 文档（OpenAPI/Swagger）
- [ ] 更新用户指南

---

### Phase 6: Web UI 开发 (预计 4-6 周)

**Week 1-2: 前端基础**
- [ ] 项目初始化（Vue 3 + Vite）
- [ ] API 客户端封装
- [ ] 路由配置
- [ ] 基础组件开发（Header, Footer, Layout）

**Week 3-4: 核心功能**
- [ ] 任务提交界面
- [ ] 任务执行进度展示
- [ ] 结果可视化（代码高亮、Markdown 渲染）
- [ ] 任务历史管理

**Week 5: 高级功能**
- [ ] WebSocket 实时推送
- [ ] API Key 管理
- [ ] 用户设置
- [ ] 导出功能（下载结果为文件）

**Week 6: 部署和优化**
- [ ] 前端构建优化
- [ ] Docker 部署
- [ ] 性能测试
- [ ] 用户体验优化

---

## API 设计

### REST API 端点汇总

#### 任务管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/tasks` | 创建任务 |
| GET | `/api/tasks/{task_id}` | 获取任务结果 |
| GET | `/api/tasks` | 获取任务历史（支持筛选） |
| DELETE | `/api/tasks/{task_id}` | 删除任务 |

#### 工作流管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/workflows` | 创建工作流 |
| GET | `/api/workflows/{workflow_id}` | 获取工作流状态 |
| POST | `/api/workflows/{workflow_id}/resume` | 恢复工作流（从指定阶段） |
| DELETE | `/api/workflows/{workflow_id}` | 删除工作流 |

#### 缓存管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/cache/stats` | 获取缓存统计 |
| DELETE | `/api/cache` | 清空缓存 |

#### 用户管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/auth/api-keys` | 生成 API Key |
| GET | `/api/auth/api-keys` | 获取 API Key 列表 |
| DELETE | `/api/auth/api-keys/{key_id}` | 删除 API Key |

---

## 数据模型设计

### ER 图

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   User      │1     *│   Task      │1     ?│  Workflow   │
│─────────────│───────│─────────────│───────│─────────────│
│ id          │       │ id          │       │ id          │
│ name        │       │ user_id (FK)│       │ task_id (FK)│
│ email       │       │ request     │       │ requirement │
│ created_at  │       │ mode        │       │ current_stage│
└─────────────┘       │ backend     │       │ stages_data │
                      │ status      │       │ status      │
                      │ result      │       └─────────────┘
                      │ created_at  │
                      │ completed_at│
                      └─────────────┘
                              │
                              │ request_hash
                              ↓
                      ┌─────────────┐
                      │ResultCache  │
                      │─────────────│
                      │ request_hash│
                      │ result      │
                      │ hit_count   │
                      │ expires_at  │
                      └─────────────┘
```

---

## 总结

### 整合后的优势

| 维度 | Phase 1-4 (memex-cli) | Phase 5-6 (aduib-ai) | 提升 |
|------|----------------------|---------------------|------|
| **后端统一** | memex-cli（Node.js） | aduib-ai（Python） | ✅ 技术栈统一 |
| **持久化** | ❌ 无 | ✅ PostgreSQL | ✅ 任务历史、状态恢复 |
| **缓存** | ❌ 无 | ✅ Redis | ✅ 性能提升 |
| **多租户** | ❌ 无 | ✅ API Key 管理 | ✅ 多用户支持 |
| **Web UI** | ❌ 仅 CLI | ✅ Vue 3 界面 | ✅ 用户体验 |
| **向量检索** | ❌ 无 | ✅ 内置向量数据库 | ✅ 相似任务推荐 |
| **文件管理** | ❌ 无 | ✅ 本地/S3 存储 | ✅ 代码文件上传 |

### 最终系统能力

1. **CLI 工具** - `python master_orchestrator.py "需求"`
2. **Python API** - `MasterOrchestrator().process("需求")`
3. **Web UI** - `http://localhost:3000`
4. **REST API** - 供其他系统集成
5. **任务历史** - 查询过去执行的任务
6. **结果缓存** - 相同请求秒级返回
7. **多用户** - API Key 隔离
8. **工作流恢复** - 中断后继续执行

---

**文档版本**: 1.0.0
**创建日期**: 2026-01-04
