# memex-cli + aduib-ai 混合架构设计

**设计理念**: 保留 memex-cli 作为 AI 模型调用工具，使用 aduib-ai 提供企业级后端能力。

**日期**: 2026-01-04

---

## 目录

- [架构设计](#架构设计)
- [组件职责](#组件职责)
- [数据流](#数据流)
- [Phase 5 实施方案](#phase-5-实施方案)
- [Phase 6 实施方案](#phase-6-实施方案)
- [部署架构](#部署架构)
- [优势分析](#优势分析)

---

## 架构设计

### 混合架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层                                │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │  CLI 工具    │  │  Python API  │  │   Web UI     │         │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└──────────┼──────────────────┼──────────────────┼────────────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                            │
│                      (协调层 - Python)                           │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │IntentAnalyzer│  │ExecutionRouter│ │DevWorkflowAgent│        │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   aduib-ai 后端服务层                            │
│                    (FastAPI + PostgreSQL)                        │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │              API 层 (REST + WebSocket)                    │  │
│   │  /api/tasks  /api/workflows  /api/cache  /api/history    │  │
│   └────────────────────────┬─────────────────────────────────┘  │
│                            ↓                                     │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                    服务层                                 │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│   │  │TaskService │  │WorkflowSvc │  │ CacheSvc   │         │  │
│   │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │  │
│   └────────┼────────────────┼────────────────┼───────────────┘  │
│            │                │                │                   │
│   ┌────────▼────────────────▼────────────────▼───────────────┐  │
│   │               数据层 (PostgreSQL + Redis)                │  │
│   │  • tasks 表         • workflows 表      • result_cache   │  │
│   │  • users 表         • api_keys 表       • vector_db      │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │            memex-cli 调用模块 (关键!)                     │  │
│   │  • 包装 memex-cli subprocess 调用                        │  │
│   │  • 事件流解析                                            │  │
│   │  • 错误处理和重试                                        │  │
│   └────────────────────────┬─────────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      memex-cli                                   │
│                  (AI 模型调用工具 - Node.js)                     │
│                                                                  │
│   memex-cli run <backend> <prompt> --stream jsonl               │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   AI 模型服务提供商                              │
│     Claude API      Gemini API      Codex API                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 组件职责

### 1. MasterOrchestrator (协调层)

**职责**:
- 意图分析
- 执行路由
- 工作流编排

**不变**: 保持当前实现，通过 aduib-ai API 调用后端

---

### 2. aduib-ai 后端服务层

#### 2.1 API 层

**职责**:
- 提供 REST API 给 MasterOrchestrator 和 Web UI
- WebSocket 实时推送任务进度
- API Key 认证和鉴权

**新增端点**:
```
POST   /api/tasks/execute           # 执行任务 (调用 memex-cli)
GET    /api/tasks/{id}               # 获取任务结果
POST   /api/workflows/execute        # 执行工作流
GET    /api/workflows/{id}/progress  # 获取工作流进度 (WebSocket)
GET    /api/history                  # 获取任务历史
GET    /api/cache/stats              # 缓存统计
```

---

#### 2.2 服务层

**TaskService**:
```python
class TaskService:
    def __init__(self):
        self.memex_executor = MemexCliExecutor()  # ← 关键组件
        self.cache_service = CacheService()

    async def execute_task(self, request: str, mode: str, backend: str, user_id: str):
        """执行任务 (通过 memex-cli)"""
        # 1. 检查缓存
        cached = await self.cache_service.get(request, mode, backend)
        if cached:
            return cached

        # 2. 创建任务记录
        task = Task.create(
            user_id=user_id,
            request=request,
            mode=mode,
            backend=backend,
            status="pending"
        )

        # 3. 调用 memex-cli
        try:
            result = await self.memex_executor.run(
                backend=backend,
                prompt=request,
                stream_format="jsonl"
            )

            task.result = result
            task.status = "completed"

            # 4. 写入缓存
            await self.cache_service.set(request, mode, backend, result)

        except Exception as e:
            task.result = {"error": str(e)}
            task.status = "failed"

        task.save()
        return task
```

**WorkflowService**:
```python
class WorkflowService:
    def __init__(self):
        self.memex_executor = MemexCliExecutor()

    async def execute_workflow(self, requirement: str, user_id: str):
        """执行 5 阶段工作流"""
        workflow = Workflow.create(
            user_id=user_id,
            requirement=requirement,
            current_stage=0,
            status="running"
        )

        stages = [
            ("requirements", "claude"),
            ("feature_design", "claude"),
            ("ux_design", "gemini"),
            ("dev_plan", "codex"),
            ("implementation", "codex")
        ]

        for i, (stage_name, backend) in enumerate(stages):
            # 构建提示词
            prompt = self._build_prompt(stage_name, requirement, workflow.stages_data)

            # 调用 memex-cli
            result = await self.memex_executor.run(backend, prompt, "jsonl")

            # 保存阶段结果
            workflow.stages_data[stage_name] = {
                "output": result["output"],
                "run_id": result["run_id"],
                "backend": backend
            }
            workflow.current_stage = i + 1
            workflow.save()

            # WebSocket 推送进度
            await self.notify_progress(workflow.id, i + 1, 5)

        workflow.status = "completed"
        workflow.save()
        return workflow
```

---

#### 2.3 MemexCliExecutor (核心组件)

**职责**: 封装 memex-cli 调用，提供统一接口

**文件**: `aduib-ai/component/memex_executor.py`

```python
import subprocess
import asyncio
from typing import Dict, Any, Optional
from component.event_parser import EventParser

class MemexCliExecutor:
    """memex-cli 执行器"""

    def __init__(self, memex_path: str = "memex-cli", timeout: int = 600):
        self.memex_path = memex_path
        self.timeout = timeout
        self.event_parser = EventParser()

    async def run(self, backend: str, prompt: str, stream_format: str = "jsonl") -> Dict[str, Any]:
        """
        执行 memex-cli 命令

        Args:
            backend: AI 后端 (claude, gemini, codex)
            prompt: 提示词
            stream_format: 流格式 (jsonl)

        Returns:
            {
                "success": bool,
                "output": str,
                "events": List[Dict],
                "run_id": str,
                "error": Optional[str]
            }
        """
        # 构建命令
        cmd = [
            self.memex_path,
            "run",
            backend,
            prompt,
            "--stream",
            stream_format
        ]

        try:
            # 异步执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # 等待完成（带超时）
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            # 解析事件流
            events = self.event_parser.parse(stdout)

            # 提取输出和 run_id
            output = self._extract_output(events)
            run_id = self._extract_run_id(events)

            return {
                "success": True,
                "output": output,
                "events": events,
                "run_id": run_id,
                "error": None
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": "",
                "events": [],
                "run_id": None,
                "error": f"Execution timeout after {self.timeout}s"
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "events": [],
                "run_id": None,
                "error": str(e)
            }

    def _extract_output(self, events: List[Dict]) -> str:
        """从事件流提取最终输出"""
        output_parts = []
        for event in events:
            if event.get("type") == "text_delta":
                output_parts.append(event.get("content", ""))
        return "".join(output_parts)

    def _extract_run_id(self, events: List[Dict]) -> Optional[str]:
        """从事件流提取 run_id"""
        for event in events:
            if event.get("type") == "run_start":
                return event.get("run_id")
            if "run_id" in event:
                return event["run_id"]
        return None
```

---

#### 2.4 数据层

**PostgreSQL 表结构**:

```sql
-- 用户表
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Key 表
CREATE TABLE api_keys (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES users(id),
    key_hash VARCHAR(64) UNIQUE,
    name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- 任务表
CREATE TABLE tasks (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES users(id),
    request TEXT NOT NULL,
    mode VARCHAR(32) NOT NULL,  -- command, agent, prompt, skill, backend
    backend VARCHAR(32),         -- claude, gemini, codex
    status VARCHAR(32) DEFAULT 'pending',  -- pending, running, completed, failed
    result JSONB,                -- 存储完整结果
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 工作流表
CREATE TABLE workflows (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES users(id),
    task_id VARCHAR(64) REFERENCES tasks(id),
    requirement TEXT NOT NULL,
    current_stage INTEGER DEFAULT 0,  -- 0-4
    stages_data JSONB,            -- 各阶段输出
    status VARCHAR(32) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 结果缓存表
CREATE TABLE result_cache (
    request_hash VARCHAR(64) PRIMARY KEY,
    request TEXT NOT NULL,
    mode VARCHAR(32) NOT NULL,
    backend VARCHAR(32) NOT NULL,
    result JSONB NOT NULL,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

-- 索引
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_cache_expires ON result_cache(expires_at);
```

---

## 数据流

### 场景 1: 简单任务执行

```
用户 (Web UI) → "分析代码性能"
  ↓
aduib-ai API: POST /api/tasks/execute
  {
    "request": "分析代码性能",
    "mode": "backend",
    "backend": "claude"
  }
  ↓
TaskService.execute_task()
  ├─ 1. 检查缓存 (Redis)
  │    └─ 未命中，继续
  ├─ 2. 创建任务记录 (PostgreSQL)
  ├─ 3. 调用 MemexCliExecutor.run()
  │    ├─ 执行: memex-cli run claude "分析代码性能" --stream jsonl
  │    ├─ 解析事件流
  │    └─ 返回: {success, output, events, run_id}
  ├─ 4. 保存结果到 tasks 表
  └─ 5. 写入缓存 (TTL 1小时)
  ↓
返回给前端: {task_id, status, result}
```

---

### 场景 2: 5 阶段工作流

```
用户 (CLI) → python master_orchestrator.py "开发博客系统"
  ↓
MasterOrchestrator.process()
  ├─ IntentAnalyzer.analyze()
  │    └─ Intent(mode=SKILL, complexity=complex)
  └─ 调用 aduib-ai API: POST /api/workflows/execute
       {
         "requirement": "开发博客系统"
       }
  ↓
aduib-ai WorkflowService.execute_workflow()
  ↓
阶段 1: Requirements (Claude)
  ├─ MemexCliExecutor.run("claude", prompt_1, "jsonl")
  ├─ 保存输出到 workflow.stages_data["requirements"]
  └─ WebSocket 推送: {stage: 1, status: "completed"}
  ↓
阶段 2: Feature Design (Claude)
  ├─ 构建提示词（包含阶段1输出）
  ├─ MemexCliExecutor.run("claude", prompt_2, "jsonl")
  └─ ...
  ↓
阶段 3: UX Design (Gemini)
  ├─ MemexCliExecutor.run("gemini", prompt_3, "jsonl")
  └─ ...
  ↓
阶段 4: Dev Plan (Codex)
  ├─ MemexCliExecutor.run("codex", prompt_4, "jsonl")
  └─ ...
  ↓
阶段 5: Implementation (Codex)
  ├─ MemexCliExecutor.run("codex", prompt_5, "jsonl")
  └─ workflow.status = "completed"
  ↓
返回: WorkflowResult
  {
    "workflow_id": "...",
    "status": "completed",
    "stages_data": {
      "requirements": {...},
      "feature_design": {...},
      ...
    }
  }
```

---

## Phase 5 实施方案

### 目标

1. 在 aduib-ai 中集成 memex-cli 调用能力
2. 实现任务持久化和缓存
3. 提供 REST API 给 MasterOrchestrator
4. 支持多租户（API Key）

---

### 5.1 aduib-ai 扩展开发

#### 步骤 1: 安装和配置 memex-cli

**在 aduib-ai 环境中**:

```bash
# 安装 Node.js (如果未安装)
# Ubuntu/Debian
sudo apt-get install nodejs npm

# macOS
brew install node

# 安装 memex-cli
npm install -g memex-cli

# 验证
memex-cli --version

# 配置后端
memex-cli backends add claude --api-key YOUR_CLAUDE_KEY
memex-cli backends add gemini --api-key YOUR_GEMINI_KEY
memex-cli backends add codex --api-key YOUR_CODEX_KEY
```

**配置文件** (aduib-ai `.env`):

```bash
# memex-cli 配置
MEMEX_CLI_PATH=/usr/local/bin/memex-cli  # 或 which memex-cli 的输出
MEMEX_TIMEOUT=600  # 默认超时（秒）
```

---

#### 步骤 2: 创建 MemexCliExecutor

**文件**: `aduib-ai/component/memex_executor.py`

```python
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import json

class EventParser:
    """事件流解析器（复用现有代码）"""

    @staticmethod
    def parse(raw_output: bytes) -> List[Dict[str, Any]]:
        """解析 JSONL 事件流"""
        # 检测编码
        encoding = EventParser._detect_encoding(raw_output)

        # 解码
        text = raw_output.decode(encoding)

        # 解析每行 JSON
        events = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    pass  # 忽略非 JSON 行

        return events

    @staticmethod
    def _detect_encoding(data: bytes) -> str:
        """检测编码"""
        # 检查 UTF-16 LE BOM
        if data[:2] == b'\xff\xfe':
            return 'utf-16-le'

        # 默认 UTF-8
        try:
            data.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass

        # 使用 chardet
        try:
            import chardet
            result = chardet.detect(data)
            return result['encoding']
        except:
            return 'utf-8'  # 回退


class MemexCliExecutor:
    """memex-cli 执行器"""

    def __init__(self, memex_path: Optional[str] = None, timeout: int = 600):
        self.memex_path = memex_path or os.getenv("MEMEX_CLI_PATH", "memex-cli")
        self.timeout = timeout
        self.event_parser = EventParser()

        # 验证 memex-cli 是否可用
        self._check_memex_cli()

    def _check_memex_cli(self):
        """检查 memex-cli 是否安装"""
        try:
            result = subprocess.run(
                [self.memex_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("memex-cli not working properly")
        except FileNotFoundError:
            raise RuntimeError(
                f"memex-cli not found at {self.memex_path}. "
                "Please install: npm install -g memex-cli"
            )

    async def run(
        self,
        backend: str,
        prompt: str,
        stream_format: str = "jsonl"
    ) -> Dict[str, Any]:
        """
        执行 memex-cli 命令（异步）

        Args:
            backend: claude, gemini, codex
            prompt: 提示词
            stream_format: jsonl

        Returns:
            {
                "success": bool,
                "output": str,
                "events": List[Dict],
                "run_id": Optional[str],
                "error": Optional[str]
            }
        """
        cmd = [
            self.memex_path,
            "run",
            backend,
            prompt,
            "--stream",
            stream_format
        ]

        try:
            # 创建异步子进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # 等待完成（带超时）
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            # 检查退出码
            if process.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "events": [],
                    "run_id": None,
                    "error": f"memex-cli failed: {stderr.decode()}"
                }

            # 解析事件流
            events = self.event_parser.parse(stdout)

            # 提取输出和 run_id
            output = self._extract_output(events)
            run_id = self._extract_run_id(events)

            return {
                "success": True,
                "output": output,
                "events": events,
                "run_id": run_id,
                "error": None
            }

        except asyncio.TimeoutError:
            # 超时，杀死进程
            try:
                process.kill()
            except:
                pass

            return {
                "success": False,
                "output": "",
                "events": [],
                "run_id": None,
                "error": f"Execution timeout after {self.timeout}s"
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "events": [],
                "run_id": None,
                "error": f"Execution error: {str(e)}"
            }

    def _extract_output(self, events: List[Dict]) -> str:
        """从事件流提取输出"""
        output_parts = []
        for event in events:
            if event.get("type") == "text_delta":
                content = event.get("content", "")
                output_parts.append(content)
        return "".join(output_parts)

    def _extract_run_id(self, events: List[Dict]) -> Optional[str]:
        """从事件流提取 run_id"""
        for event in events:
            if event.get("type") == "run_start":
                return event.get("run_id")
            if "run_id" in event:
                return event["run_id"]
        return None
```

---

#### 步骤 3: 创建数据模型

**文件**: `aduib-ai/models/task.py`

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from models.base import BaseModel
from utils.snowflake import generate_id

class Task(BaseModel):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, default=generate_id)
    user_id = Column(String(64), nullable=False)
    request = Column(Text, nullable=False)
    mode = Column(String(32), nullable=False)  # command, agent, prompt, skill, backend
    backend = Column(String(32))               # claude, gemini, codex
    status = Column(String(32), default="pending")  # pending, running, completed, failed
    result = Column(JSONB)                     # 完整结果
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "request": self.request,
            "mode": self.mode,
            "backend": self.backend,
            "status": self.status,
            "result": self.result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Workflow(BaseModel):
    """工作流模型"""
    __tablename__ = "workflows"

    id = Column(String(64), primary_key=True, default=generate_id)
    user_id = Column(String(64), nullable=False)
    task_id = Column(String(64), nullable=True)
    requirement = Column(Text, nullable=False)
    current_stage = Column(Integer, default=0)  # 0-4
    stages_data = Column(JSONB, default={})     # 各阶段输出
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "requirement": self.requirement,
            "current_stage": self.current_stage,
            "stages_data": self.stages_data,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ResultCache(BaseModel):
    """结果缓存"""
    __tablename__ = "result_cache"

    request_hash = Column(String(64), primary_key=True)
    request = Column(Text, nullable=False)
    mode = Column(String(32), nullable=False)
    backend = Column(String(32), nullable=False)
    result = Column(JSONB, nullable=False)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
```

---

#### 步骤 4: 实现服务层

**文件**: `aduib-ai/service/task_service.py`

```python
from models.task import Task, ResultCache
from component.memex_executor import MemexCliExecutor
from datetime import datetime, timedelta
import hashlib

class TaskService:
    """任务服务"""

    def __init__(self):
        self.memex_executor = MemexCliExecutor()

    async def execute_task(
        self,
        user_id: str,
        request: str,
        mode: str,
        backend: str
    ) -> Task:
        """执行任务"""

        # 1. 检查缓存
        cached = self._get_cached_result(request, mode, backend)
        if cached:
            # 从缓存创建任务
            task = Task(
                user_id=user_id,
                request=request,
                mode=mode,
                backend=backend,
                status="completed",
                result=cached["result"],
                completed_at=datetime.now()
            )
            task.save()
            return task

        # 2. 创建任务记录
        task = Task(
            user_id=user_id,
            request=request,
            mode=mode,
            backend=backend,
            status="pending"
        )
        task.save()

        # 3. 更新状态为 running
        task.status = "running"
        task.save()

        # 4. 调用 memex-cli
        try:
            result = await self.memex_executor.run(
                backend=backend,
                prompt=request,
                stream_format="jsonl"
            )

            task.result = result
            task.status = "completed" if result["success"] else "failed"
            task.completed_at = datetime.now()

            # 5. 写入缓存（仅成功的结果）
            if result["success"]:
                self._cache_result(request, mode, backend, result)

        except Exception as e:
            task.result = {
                "success": False,
                "error": str(e)
            }
            task.status = "failed"
            task.completed_at = datetime.now()

        task.save()
        return task

    def _get_cached_result(self, request: str, mode: str, backend: str):
        """获取缓存"""
        request_hash = self._compute_hash(request, mode, backend)

        cache = ResultCache.query.filter_by(request_hash=request_hash).first()

        if cache and cache.expires_at > datetime.now():
            # 缓存命中
            cache.hit_count += 1
            cache.save()
            return {"result": cache.result}

        return None

    def _cache_result(self, request: str, mode: str, backend: str, result: dict):
        """写入缓存"""
        request_hash = self._compute_hash(request, mode, backend)

        cache = ResultCache(
            request_hash=request_hash,
            request=request,
            mode=mode,
            backend=backend,
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
from models.task import Workflow
from component.memex_executor import MemexCliExecutor
from datetime import datetime

# 工作流阶段提示词模板（复用 MasterOrchestrator 的配置）
STAGE_PROMPTS = {
    "requirements": """你是一位产品经理和需求分析专家。请对以下需求进行详细分析：

用户需求：
{requirement}

请提供：
1. 核心需求提炼
2. 用户画像和使用场景
3. 功能优先级排序
4. 成功指标定义
5. 风险和约束条件

请以结构化的方式输出分析结果。""",

    "feature_design": """你是一位软件架构师。基于以下需求分析，设计系统功能架构：

【需求分析】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 功能模块划分
2. 模块间的接口设计
3. 数据模型设计
4. 技术栈选择建议
5. 架构图（文字描述）

请确保设计符合SOLID原则和最佳实践。""",

    "ux_design": """你是一位UX设计专家。基于以下功能设计，创建用户体验方案：

【功能设计】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 用户界面布局设计
2. 交互流程设计
3. 关键页面线框图（文字描述）
4. 视觉设计建议（色彩、字体、组件）
5. 可用性和可访问性考虑

请确保设计符合用户体验最佳实践。""",

    "dev_plan": """你是一位技术主管。基于以下设计，制定详细的开发计划：

【功能设计】
{feature_design}

【UX设计】
{ux_design}

【原始需求】
{requirement}

请提供：
1. 开发阶段划分和里程碑
2. 每个阶段的任务清单
3. 技术选型和依赖管理
4. 测试策略（单元测试、集成测试）
5. 部署和运维计划

请以可执行的方式组织计划。""",

    "implementation": """你是一位资深开发工程师。基于以下开发计划，开始实现核心功能：

【开发计划】
{previous_output}

【原始需求】
{requirement}

请提供：
1. 核心功能的代码实现
2. 关键模块的代码示例
3. 配置文件示例
4. 测试用例示例
5. 部署脚本示例

请确保代码遵循最佳实践，包含适当的注释和错误处理。"""
}

class WorkflowService:
    """工作流服务"""

    def __init__(self):
        self.memex_executor = MemexCliExecutor()

    async def execute_workflow(self, user_id: str, requirement: str) -> Workflow:
        """执行 5 阶段工作流"""

        # 创建工作流记录
        workflow = Workflow(
            user_id=user_id,
            requirement=requirement,
            current_stage=0,
            status="running",
            stages_data={}
        )
        workflow.save()

        # 5 个阶段
        stages = [
            ("requirements", "claude"),
            ("feature_design", "claude"),
            ("ux_design", "gemini"),
            ("dev_plan", "codex"),
            ("implementation", "codex")
        ]

        try:
            for i, (stage_name, backend) in enumerate(stages):
                # 构建提示词
                prompt = self._build_prompt(
                    stage_name,
                    requirement,
                    workflow.stages_data
                )

                # 调用 memex-cli
                result = await self.memex_executor.run(
                    backend=backend,
                    prompt=prompt,
                    stream_format="jsonl"
                )

                if not result["success"]:
                    # 阶段失败
                    workflow.status = "failed"
                    workflow.save()
                    raise Exception(f"Stage {stage_name} failed: {result['error']}")

                # 保存阶段结果
                workflow.stages_data[stage_name] = {
                    "output": result["output"],
                    "run_id": result["run_id"],
                    "backend": backend,
                    "completed_at": datetime.now().isoformat()
                }
                workflow.current_stage = i + 1
                workflow.save()

                # TODO: WebSocket 推送进度
                # await self.notify_progress(workflow.id, i + 1)

            # 全部完成
            workflow.status = "completed"
            workflow.save()

        except Exception as e:
            workflow.status = "failed"
            workflow.save()
            raise

        return workflow

    def _build_prompt(self, stage: str, requirement: str, stages_data: dict) -> str:
        """构建阶段提示词"""
        template = STAGE_PROMPTS[stage]

        variables = {
            "requirement": requirement,
            "previous_output": "",
            "feature_design": "",
            "ux_design": ""
        }

        # 填充前序阶段输出
        if "requirements" in stages_data:
            variables["previous_output"] = stages_data["requirements"]["output"]

        if "feature_design" in stages_data:
            variables["feature_design"] = stages_data["feature_design"]["output"]
            variables["previous_output"] = stages_data["feature_design"]["output"]

        if "ux_design" in stages_data:
            variables["ux_design"] = stages_data["ux_design"]["output"]

        if "dev_plan" in stages_data:
            variables["previous_output"] = stages_data["dev_plan"]["output"]

        return template.format(**variables)
```

---

#### 步骤 5: 添加 API 端点

**文件**: `aduib-ai/controllers/task_controller.py`

```python
from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from service.task_service import TaskService
from service.workflow_service import WorkflowService
from models.task import Task, Workflow

router = APIRouter(prefix="/api", tags=["Tasks"])

task_service = TaskService()
workflow_service = WorkflowService()

# ============ 任务 API ============

class ExecuteTaskRequest(BaseModel):
    request: str
    mode: str
    backend: str

@router.post("/tasks/execute")
async def execute_task(
    data: ExecuteTaskRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(...)
):
    """执行任务"""
    # 验证 API Key
    user_id = await verify_api_key(x_api_key)

    # 异步执行任务
    task = await task_service.execute_task(
        user_id=user_id,
        request=data.request,
        mode=data.mode,
        backend=data.backend
    )

    return task.to_dict()

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, x_api_key: str = Header(...)):
    """获取任务结果"""
    user_id = await verify_api_key(x_api_key)

    task = Task.query.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    if task.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    return task.to_dict()

@router.get("/tasks")
async def list_tasks(
    mode: str = None,
    status: str = None,
    limit: int = 10,
    offset: int = 0,
    x_api_key: str = Header(...)
):
    """获取任务列表"""
    user_id = await verify_api_key(x_api_key)

    query = Task.query.filter_by(user_id=user_id)

    if mode:
        query = query.filter_by(mode=mode)
    if status:
        query = query.filter_by(status=status)

    tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()

    return [task.to_dict() for task in tasks]

# ============ 工作流 API ============

class ExecuteWorkflowRequest(BaseModel):
    requirement: str

@router.post("/workflows/execute")
async def execute_workflow(
    data: ExecuteWorkflowRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(...)
):
    """执行工作流"""
    user_id = await verify_api_key(x_api_key)

    # 异步执行
    workflow = await workflow_service.execute_workflow(
        user_id=user_id,
        requirement=data.requirement
    )

    return workflow.to_dict()

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, x_api_key: str = Header(...)):
    """获取工作流状态"""
    user_id = await verify_api_key(x_api_key)

    workflow = Workflow.query.get(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")

    if workflow.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    return workflow.to_dict()

# ============ 辅助函数 ============

async def verify_api_key(api_key: str) -> str:
    """验证 API Key，返回 user_id"""
    from models.api_key import APIKey
    import hashlib

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    api_key_obj = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()

    if not api_key_obj:
        raise HTTPException(401, "Invalid API Key")

    # 更新最后使用时间
    api_key_obj.last_used_at = datetime.now()
    api_key_obj.save()

    return api_key_obj.user_id
```

---

### 5.2 MasterOrchestrator 适配

**文件**: `aduib_client.py` (新增)

```python
import requests
from typing import Dict, Any, Optional

class AduibClient:
    """aduib-ai 后端客户端"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    def execute_task(self, request: str, mode: str, backend: str) -> Dict[str, Any]:
        """执行任务"""
        response = requests.post(
            f"{self.base_url}/api/tasks/execute",
            json={
                "request": request,
                "mode": mode,
                "backend": backend
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务"""
        response = requests.get(
            f"{self.base_url}/api/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def execute_workflow(self, requirement: str) -> Dict[str, Any]:
        """执行工作流"""
        response = requests.post(
            f"{self.base_url}/api/workflows/execute",
            json={"requirement": requirement},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流"""
        response = requests.get(
            f"{self.base_url}/api/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

**文件**: `master_orchestrator.py` (更新)

```python
import os
import time
from aduib_client import AduibClient
from dataclasses import dataclass

@dataclass
class WorkflowResult:
    """工作流结果（与之前兼容）"""
    requirement: str
    stages: list
    success: bool
    completed_stages: int
    # ...

class MasterOrchestrator:
    def __init__(
        self,
        aduib_url: str = None,
        api_key: str = None
    ):
        """
        初始化（使用 aduib-ai 后端）

        Args:
            aduib_url: aduib-ai URL (默认从环境变量读取)
            api_key: API Key (默认从环境变量读取)
        """
        self.aduib_url = aduib_url or os.getenv("ADUIB_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("ADUIB_API_KEY")

        if not self.api_key:
            raise ValueError("API Key required. Set ADUIB_API_KEY env var.")

        self.client = AduibClient(self.aduib_url, self.api_key)
        self.analyzer = IntentAnalyzer()

    def process(self, request: str, verbose: bool = False):
        """处理请求"""
        # 1. 意图分析
        intent = self.analyzer.analyze(request)

        if verbose:
            print(f"[意图分析] 模式={intent.mode.value}, 类型={intent.task_type}")

        # 2. 根据模式调用 aduib-ai
        if intent.mode == ExecutionMode.SKILL and intent.complexity == "complex":
            # 工作流模式
            return self._execute_workflow(request, verbose)
        else:
            # 普通任务
            backend = self._select_backend(intent)
            return self._execute_task(request, intent.mode.value, backend, verbose)

    def _execute_workflow(self, requirement: str, verbose: bool):
        """执行工作流"""
        # 调用 aduib-ai API
        workflow = self.client.execute_workflow(requirement)
        workflow_id = workflow["id"]

        if verbose:
            print(f"[工作流] ID={workflow_id}")

        # 轮询状态
        while True:
            workflow = self.client.get_workflow(workflow_id)
            status = workflow["status"]
            current_stage = workflow["current_stage"]

            if verbose and status == "running":
                print(f"[工作流] 阶段 {current_stage}/5 执行中...")

            if status in ["completed", "failed"]:
                break

            time.sleep(2)  # 轮询间隔

        # 转换为 WorkflowResult
        return self._parse_workflow_result(workflow)

    def _execute_task(self, request: str, mode: str, backend: str, verbose: bool):
        """执行普通任务"""
        # 调用 aduib-ai API
        task = self.client.execute_task(request, mode, backend)
        task_id = task["id"]

        if verbose:
            print(f"[任务] ID={task_id}, 后端={backend}")

        # 等待完成
        while True:
            task = self.client.get_task(task_id)
            status = task["status"]

            if status in ["completed", "failed"]:
                break

            time.sleep(1)

        # 转换为 TaskResult
        return self._parse_task_result(task)
```

---

## Phase 6 实施方案

### Web UI 开发

**前端技术栈**:
- Vue 3 + TypeScript
- Vite
- Tailwind CSS
- Axios (调用 aduib-ai API)
- Socket.IO (实时进度推送)

**核心页面** (与之前设计相同):
1. 任务提交界面
2. 任务执行进度页面
3. 任务历史管理

**API 调用示例**:

```typescript
// src/api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'X-API-Key': localStorage.getItem('apiKey') || ''
  }
})

export const taskAPI = {
  async executeTask(request: string, mode: string, backend: string) {
    const response = await client.post('/tasks/execute', {
      request,
      mode,
      backend
    })
    return response.data
  },

  async getTask(taskId: string) {
    const response = await client.get(`/tasks/${taskId}`)
    return response.data
  }
}

export const workflowAPI = {
  async executeWorkflow(requirement: string) {
    const response = await client.post('/workflows/execute', {
      requirement
    })
    return response.data
  },

  async getWorkflow(workflowId: string) {
    const response = await client.get(`/workflows/${workflowId}`)
    return response.data
  }
}
```

---

## 部署架构

### Docker Compose 部署

**文件**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # aduib-ai 后端
  aduib-backend:
    build: ./aduib-ai
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/aduib
      - REDIS_URL=redis://redis:6379/0
      - MEMEX_CLI_PATH=/usr/local/bin/memex-cli
    volumes:
      - ./aduib-ai:/app
    depends_on:
      - postgres
      - redis
    command: uvicorn app:app --host 0.0.0.0 --port 8000

  # PostgreSQL
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=aduib
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  # Web UI (Vue 3)
  web-ui:
    build: ./web-ui
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - aduib-backend

volumes:
  postgres_data:
```

**启动**:

```bash
docker-compose up -d
```

---

## 优势分析

### memex-cli + aduib-ai 组合的优势

| 维度 | 纯 memex-cli | 纯 aduib-ai | **组合方案** |
|------|-------------|------------|--------------|
| **AI 调用** | ✅ 成熟稳定 | ❌ 需自行集成 | ✅ 复用 memex-cli |
| **持久化** | ❌ 无 | ✅ PostgreSQL | ✅ PostgreSQL |
| **缓存** | ❌ 无 | ✅ Redis | ✅ Redis |
| **多租户** | ❌ 无 | ✅ API Key | ✅ API Key |
| **Web UI** | ❌ 无 | ✅ 可集成 | ✅ Vue 3 UI |
| **部署复杂度** | 低 | 中 | **中** |
| **技术栈统一** | Node.js | Python | **Python + Node.js** |
| **可维护性** | 中 | 高 | **高** |

### 为什么选择组合方案？

1. **复用成熟工具** - memex-cli 已经很好地封装了 Claude/Gemini/Codex 调用
2. **快速开发** - 无需在 aduib-ai 中重新实现 AI 模型集成
3. **最佳实践** - 利用 aduib-ai 的企业级能力（持久化、缓存、多租户）
4. **解耦架构** - memex-cli 可以独立升级，不影响 aduib-ai

---

## 总结

### 最终系统架构

```
┌─────────────────────────────────────────────┐
│            用户界面                          │
│  CLI  |  Python API  |  Web UI              │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│      MasterOrchestrator (协调层)            │
└──────────────────┬──────────────────────────┘
                   ↓ REST API
┌─────────────────────────────────────────────┐
│         aduib-ai 后端服务                    │
│  • 持久化 (PostgreSQL)                       │
│  • 缓存 (Redis)                              │
│  • API 管理 (FastAPI)                        │
│  • memex-cli 调用封装 ← 关键                 │
└──────────────────┬──────────────────────────┘
                   ↓ subprocess
┌─────────────────────────────────────────────┐
│         memex-cli (AI 调用工具)              │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│      Claude / Gemini / Codex                │
└─────────────────────────────────────────────┘
```

### 核心能力

1. ✅ **CLI 工具** - `python master_orchestrator.py "需求"`
2. ✅ **Python API** - `MasterOrchestrator().process("需求")`
3. ✅ **Web UI** - Vue 3 界面
4. ✅ **任务持久化** - PostgreSQL 存储历史
5. ✅ **结果缓存** - Redis 缓存（1小时 TTL）
6. ✅ **多租户** - API Key 管理
7. ✅ **5 阶段工作流** - 自动化执行
8. ✅ **实时进度** - WebSocket 推送

---

**文档版本**: 1.0.0
**创建日期**: 2026-01-04
