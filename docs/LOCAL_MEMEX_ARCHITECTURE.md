# 本地 memex-cli + 远程 aduib-ai 混合架构

**核心原则**: memex-cli 在本地执行，aduib-ai 提供数据管理和 Web 服务。

**日期**: 2026-01-04

---

## 目录

- [架构设计](#架构设计)
- [组件职责](#组件职责)
- [数据流](#数据流)
- [本地-远程同步](#本地-远程同步)
- [实施方案](#实施方案)
- [优势分析](#优势分析)

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    本地环境 (Local)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │        用户界面 (本地 CLI)                          │     │
│  │  python master_orchestrator.py "需求"              │     │
│  └──────────────────────┬─────────────────────────────┘     │
│                         ↓                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          MasterOrchestrator                          │    │
│  │           (本地协调器)                               │    │
│  │  ┌──────────────┐  ┌──────────────┐                │    │
│  │  │IntentAnalyzer│  │ExecutionRouter│                │    │
│  │  └──────────────┘  └──────┬───────┘                │    │
│  └─────────────────────────────┼──────────────────────┘    │
│                                │                             │
│                   ┌────────────┼────────────┐               │
│                   ↓ (本地)     ↓ (远程)     ↓               │
│  ┌────────────────────────┐  ┌──────────────────────┐      │
│  │  memex-cli (本地执行)  │  │  AduibClient         │      │
│  │  ┌──────────────────┐  │  │  (REST 客户端)       │      │
│  │  │ BackendOrchestrator│ │  │                      │      │
│  │  └──────┬───────────┘  │  └──────────┬───────────┘      │
│  └─────────┼──────────────┘             │                   │
│            ↓ subprocess                 ↓ HTTPS             │
│  ┌─────────────────────┐  ┌─────────────────────────┐      │
│  │   memex-cli run     │  │  上传/查询结果           │      │
│  │   claude "prompt"   │  │  (可选)                  │      │
│  └─────────┬───────────┘  └─────────────┬───────────┘      │
└────────────┼──────────────────────────────┼─────────────────┘
             ↓                              ↓
┌────────────────────────┐    ┌─────────────────────────────┐
│   AI 模型服务提供商     │    │   aduib-ai 后端服务 (远程)  │
│  Claude / Gemini / Codex│    │   (可选的数据服务)          │
│  (用户的 API Key)       │    │                             │
└────────────────────────┘    │  • 任务历史存储             │
                              │  • 结果缓存                 │
                              │  • Web UI 支持              │
                              │  • 多设备同步               │
                              └─────────────────────────────┘
```

---

## 组件职责

### 本地组件

#### 1. MasterOrchestrator (本地协调器)

**职责**:
- 意图分析
- 执行路由
- **本地执行** memex-cli 调用
- **可选**上传结果到 aduib-ai

**执行流程**:

```python
class MasterOrchestrator:
    def __init__(
        self,
        use_remote: bool = False,  # 是否使用远程服务
        aduib_url: str = None,
        api_key: str = None
    ):
        # 本地组件（必需）
        self.analyzer = IntentAnalyzer()
        self.backend_orch = BackendOrchestrator()  # 本地 memex-cli 调用

        # 远程组件（可选）
        self.use_remote = use_remote
        if use_remote and api_key:
            self.aduib_client = AduibClient(aduib_url, api_key)
        else:
            self.aduib_client = None

    def process(self, request: str, verbose: bool = False):
        """处理请求"""
        # 1. 意图分析
        intent = self.analyzer.analyze(request)

        # 2. 如果启用远程服务，先查询缓存
        if self.aduib_client:
            cached = self.aduib_client.get_cached_result(request, intent)
            if cached:
                if verbose:
                    print("[缓存命中] 从远程缓存返回结果")
                return cached

        # 3. 本地执行 memex-cli
        if intent.mode == ExecutionMode.SKILL:
            result = self._execute_workflow_local(request, intent, verbose)
        else:
            backend = self._select_backend(intent)
            result = self.backend_orch.run_task(backend, request, "jsonl")

        # 4. 如果启用远程服务，上传结果
        if self.aduib_client and result.success:
            self.aduib_client.save_task_result(request, intent, result)
            if verbose:
                print("[已保存] 结果已上传到远程服务")

        return result
```

**关键设计**:
- ✅ **本地优先** - memex-cli 在本地执行，使用用户本地的 API Key
- ✅ **远程可选** - aduib-ai 作为可选的数据服务
- ✅ **缓存查询** - 如果启用远程，先查缓存再执行
- ✅ **结果上传** - 执行后可选上传到远程，供其他设备或 Web UI 查看

---

#### 2. BackendOrchestrator (本地 memex-cli 调用)

**职责**: 在本地执行 memex-cli（保持不变）

```python
# 文件: skills/cross-backend-orchestrator/scripts/orchestrator.py
class BackendOrchestrator:
    """本地 memex-cli 执行器"""

    def __init__(self, parse_events: bool = True, timeout: int = 600):
        self.parse_events = parse_events
        self.timeout = timeout
        self._check_memex_cli()  # 确保本地已安装

    def run_task(self, backend: str, prompt: str, stream_format: str = "jsonl"):
        """在本地执行 memex-cli"""
        cmd = ["memex-cli", "run", backend, prompt, "--stream", stream_format]

        # 本地执行
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=self.timeout)

        # 解析结果
        if self.parse_events:
            events = EventParser.parse(stdout)
            output = self._extract_output(events)
            run_id = self._extract_run_id(events)
        else:
            output = stdout.decode('utf-8')
            events = []
            run_id = None

        return TaskResult(
            success=(process.returncode == 0),
            output=output,
            events=events,
            run_id=run_id,
            error=stderr.decode('utf-8') if stderr else None
        )
```

**特点**:
- ✅ 完全本地执行
- ✅ 使用用户本地的 memex-cli 配置和 API Key
- ✅ 无需网络（除了 AI API 调用）

---

### 远程组件 (aduib-ai)

#### 1. 数据服务 API

**职责**:
- 接收本地上传的任务结果
- 提供缓存查询
- 存储任务历史
- 支持 Web UI 查询

**API 设计**:

```python
# aduib-ai/controllers/task_controller.py

@router.post("/api/tasks/save")
async def save_task_result(
    data: SaveTaskRequest,
    x_api_key: str = Header(...)
):
    """
    保存本地执行的任务结果

    请求体:
    {
        "request": "用户请求",
        "mode": "skill",
        "backend": "claude",
        "result": {
            "success": true,
            "output": "...",
            "run_id": "...",
            "events": [...]
        }
    }
    """
    user_id = await verify_api_key(x_api_key)

    # 保存到数据库
    task = Task(
        user_id=user_id,
        request=data.request,
        mode=data.mode,
        backend=data.backend,
        status="completed",
        result=data.result,
        completed_at=datetime.now()
    )
    task.save()

    # 写入缓存
    cache_service.set(data.request, data.mode, data.backend, data.result)

    return {"task_id": task.id, "message": "Saved successfully"}


@router.get("/api/cache/query")
async def query_cache(
    request: str,
    mode: str,
    backend: str,
    x_api_key: str = Header(...)
):
    """
    查询缓存结果

    Returns:
        {
            "cached": true/false,
            "result": {...} 或 null
        }
    """
    user_id = await verify_api_key(x_api_key)

    # 计算哈希
    request_hash = hashlib.sha256(f"{request}|{mode}|{backend}".encode()).hexdigest()

    # 查询缓存
    cache = ResultCache.query.filter_by(request_hash=request_hash).first()

    if cache and cache.expires_at > datetime.now():
        cache.hit_count += 1
        cache.save()
        return {
            "cached": True,
            "result": cache.result
        }

    return {
        "cached": False,
        "result": None
    }


@router.get("/api/tasks/history")
async def get_task_history(
    mode: str = None,
    limit: int = 10,
    offset: int = 0,
    x_api_key: str = Header(...)
):
    """获取任务历史（供 Web UI 使用）"""
    user_id = await verify_api_key(x_api_key)

    query = Task.query.filter_by(user_id=user_id)
    if mode:
        query = query.filter_by(mode=mode)

    tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()

    return [task.to_dict() for task in tasks]
```

**特点**:
- ✅ **被动服务** - 不主动调用 AI，只存储本地上传的结果
- ✅ **缓存服务** - 本地查询，命中则直接返回
- ✅ **历史查询** - 供 Web UI 查看历史任务
- ✅ **API Key 隔离** - 每个用户只能访问自己的数据

---

#### 2. Web UI 后端支持

**职责**:
- 提供 Web UI 查询任务历史
- 显示缓存统计
- 支持跨设备同步

**API 端点**:

```
GET  /api/tasks/history         # 任务历史列表
GET  /api/tasks/{task_id}       # 任务详情
GET  /api/cache/stats           # 缓存统计
GET  /api/workflows/history     # 工作流历史
GET  /api/workflows/{id}        # 工作流详情
```

---

## 数据流

### 场景 1: 纯本地执行（无远程服务）

```
用户 (本地 CLI)
  ↓
MasterOrchestrator.process("分析代码性能")
  ├─ use_remote = False
  └─ 直接本地执行
  ↓
BackendOrchestrator.run_task("claude", "分析代码性能")
  ├─ 执行: memex-cli run claude "分析代码性能" --stream jsonl
  ├─ 使用本地 API Key
  └─ 返回: TaskResult
  ↓
用户看到结果
```

**特点**:
- ✅ 完全离线（除了 AI API）
- ✅ 无需 aduib-ai 服务
- ✅ API Key 不离开本地

---

### 场景 2: 本地执行 + 远程缓存查询

```
用户 (本地 CLI)
  ↓
MasterOrchestrator.process("开发博客系统")
  ├─ use_remote = True
  └─ 先查询远程缓存
  ↓
AduibClient.get_cached_result("开发博客系统", "skill")
  ├─ GET https://aduib.example.com/api/cache/query
  │     ?request=开发博客系统&mode=skill&backend=claude
  ├─ Headers: X-API-Key: user_api_key
  └─ 返回: {"cached": true, "result": {...}}
  ↓
缓存命中，直接返回结果（跳过本地执行）
```

**优势**:
- ✅ **节省成本** - 相同请求不重复调用 AI API
- ✅ **秒级响应** - 缓存命中立即返回
- ✅ **跨设备共享** - 设备 A 的执行结果，设备 B 也能用

---

### 场景 3: 本地执行 + 远程保存

```
用户 (本地 CLI)
  ↓
MasterOrchestrator.process("开发电商系统")
  ├─ 查询缓存 → 未命中
  └─ 本地执行
  ↓
BackendOrchestrator (本地 memex-cli)
  ├─ 执行 5 阶段工作流
  └─ 返回: WorkflowResult
  ↓
AduibClient.save_task_result(request, result)
  ├─ POST https://aduib.example.com/api/tasks/save
  │     Body: {
  │       "request": "开发电商系统",
  │       "mode": "skill",
  │       "result": {...}
  │     }
  │     Headers: X-API-Key: user_api_key
  └─ 远程保存成功
  ↓
用户看到结果（同时已保存到远程）
```

**优势**:
- ✅ **历史可查** - Web UI 可查看历史任务
- ✅ **数据备份** - 本地结果同步到云端
- ✅ **多设备访问** - 手机 Web UI 查看 PC 执行的结果

---

### 场景 4: Web UI 查看历史

```
用户 (Web UI - 浏览器)
  ↓
访问: https://aduib.example.com
  ├─ 输入 API Key
  └─ 查看任务历史
  ↓
GET /api/tasks/history?limit=10
  ├─ Headers: X-API-Key: user_api_key
  └─ 返回: [
       {
         "id": "task_123",
         "request": "开发博客系统",
         "mode": "skill",
         "status": "completed",
         "result": {...},
         "created_at": "2026-01-04T10:30:00Z"
       },
       ...
     ]
  ↓
Web UI 展示历史任务列表
  ├─ 点击任务 → 查看详情
  └─ 支持搜索、筛选
```

**优势**:
- ✅ **随时随地访问** - 任何设备浏览器访问
- ✅ **可视化展示** - 更好的用户体验
- ✅ **分享结果** - 可生成分享链接

---

## 本地-远程同步

### 同步策略

#### 1. 主动上传（推荐）

```python
class MasterOrchestrator:
    def process(self, request: str, upload_to_remote: bool = True):
        """
        Args:
            upload_to_remote: 是否上传结果到远程
        """
        # 本地执行
        result = self._execute_local(request)

        # 上传到远程
        if upload_to_remote and self.aduib_client:
            try:
                self.aduib_client.save_task_result(request, result)
            except Exception as e:
                # 上传失败不影响本地结果
                print(f"[警告] 上传失败: {e}")

        return result
```

**特点**:
- ✅ 实时同步
- ✅ 上传失败不影响本地执行
- ✅ 用户可选（`--no-upload` 参数禁用）

---

#### 2. 批量同步

```python
class SyncManager:
    """同步管理器"""

    def __init__(self, local_cache_dir: str, aduib_client: AduibClient):
        self.local_cache_dir = Path(local_cache_dir)
        self.aduib_client = aduib_client

    def sync_to_remote(self):
        """将本地缓存同步到远程"""
        local_tasks = self._load_local_cache()

        for task in local_tasks:
            if not task.get("synced"):
                try:
                    self.aduib_client.save_task_result(
                        task["request"],
                        task["result"]
                    )
                    task["synced"] = True
                    self._update_local_cache(task)
                except Exception as e:
                    print(f"同步失败: {task['id']} - {e}")

    def sync_from_remote(self):
        """从远程同步到本地"""
        remote_tasks = self.aduib_client.get_task_history(limit=100)

        for task in remote_tasks:
            if not self._exists_locally(task["id"]):
                self._save_to_local_cache(task)
```

**使用**:

```bash
# 手动同步
python master_orchestrator.py --sync

# 或定期同步（cron job）
0 */6 * * * python master_orchestrator.py --sync  # 每6小时同步一次
```

---

#### 3. 冲突解决

**策略**: 远程优先（remote wins）

```python
def resolve_conflict(local_task, remote_task):
    """冲突解决"""
    # 比较时间戳
    if remote_task["updated_at"] > local_task["updated_at"]:
        return remote_task  # 远程更新
    else:
        return local_task   # 本地更新
```

---

## 实施方案

### Phase 5: 本地 + 远程混合架构

#### 步骤 1: 保持本地 MasterOrchestrator

**文件**: `master_orchestrator.py`

```python
import os
from typing import Optional
from aduib_client import AduibClient

class MasterOrchestrator:
    def __init__(
        self,
        use_remote: bool = None,
        aduib_url: str = None,
        api_key: str = None
    ):
        """
        初始化

        Args:
            use_remote: 是否使用远程服务（None=自动检测）
            aduib_url: aduib-ai URL
            api_key: API Key
        """
        # 本地组件（必需）
        self.analyzer = IntentAnalyzer()
        self.router = ExecutionRouter(
            BackendOrchestrator(parse_events=True, timeout=600)
        )

        # 远程组件（可选）
        if use_remote is None:
            # 自动检测：如果设置了环境变量，则启用
            use_remote = bool(os.getenv("ADUIB_API_KEY"))

        self.use_remote = use_remote
        if use_remote:
            self.aduib_url = aduib_url or os.getenv("ADUIB_URL", "https://aduib.example.com")
            self.api_key = api_key or os.getenv("ADUIB_API_KEY")

            if self.api_key:
                self.aduib_client = AduibClient(self.aduib_url, self.api_key)
            else:
                print("[警告] ADUIB_API_KEY 未设置，远程功能已禁用")
                self.use_remote = False
                self.aduib_client = None
        else:
            self.aduib_client = None

    def process(
        self,
        request: str,
        verbose: bool = False,
        use_cache: bool = True,
        upload: bool = True
    ):
        """
        处理请求

        Args:
            request: 用户请求
            verbose: 详细输出
            use_cache: 是否使用远程缓存
            upload: 是否上传结果到远程
        """
        # 1. 意图分析
        intent = self.analyzer.analyze(request)

        if verbose:
            print(f"[意图分析] 模式={intent.mode.value}, 类型={intent.task_type}")

        # 2. 查询远程缓存（如果启用）
        if self.use_remote and use_cache:
            cached = self._query_remote_cache(request, intent, verbose)
            if cached:
                return cached

        # 3. 本地执行 memex-cli
        if verbose:
            print(f"[本地执行] 使用 memex-cli")

        result = self.router.route(request, intent)

        # 4. 上传到远程（如果启用）
        if self.use_remote and upload and result.success:
            self._upload_result(request, intent, result, verbose)

        return result

    def _query_remote_cache(self, request: str, intent: Intent, verbose: bool):
        """查询远程缓存"""
        try:
            backend = self._select_backend(intent)
            response = self.aduib_client.query_cache(request, intent.mode.value, backend)

            if response.get("cached"):
                if verbose:
                    print("[缓存命中] 从远程返回结果")
                return response["result"]

        except Exception as e:
            if verbose:
                print(f"[警告] 缓存查询失败: {e}")

        return None

    def _upload_result(self, request: str, intent: Intent, result: Any, verbose: bool):
        """上传结果到远程"""
        try:
            backend = self._select_backend(intent)
            self.aduib_client.save_task_result(
                request=request,
                mode=intent.mode.value,
                backend=backend,
                result=result.to_dict() if hasattr(result, 'to_dict') else result.__dict__
            )

            if verbose:
                print("[已保存] 结果已上传到远程")

        except Exception as e:
            if verbose:
                print(f"[警告] 上传失败: {e}")
```

---

#### 步骤 2: 创建 AduibClient (本地 REST 客户端)

**文件**: `aduib_client.py`

```python
import requests
from typing import Dict, Any, Optional

class AduibClient:
    """aduib-ai 远程服务客户端"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    def query_cache(self, request: str, mode: str, backend: str) -> Dict[str, Any]:
        """查询缓存"""
        response = requests.get(
            f"{self.base_url}/api/cache/query",
            params={
                "request": request,
                "mode": mode,
                "backend": backend
            },
            headers=self.headers,
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    def save_task_result(
        self,
        request: str,
        mode: str,
        backend: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """保存任务结果"""
        response = requests.post(
            f"{self.base_url}/api/tasks/save",
            json={
                "request": request,
                "mode": mode,
                "backend": backend,
                "result": result
            },
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_task_history(
        self,
        mode: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list:
        """获取任务历史"""
        params = {"limit": limit, "offset": offset}
        if mode:
            params["mode"] = mode

        response = requests.get(
            f"{self.base_url}/api/tasks/history",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

---

#### 步骤 3: aduib-ai 添加数据服务 API

**文件**: `aduib-ai/controllers/data_service_controller.py` (新增)

```python
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from models.task import Task, ResultCache
from datetime import datetime, timedelta
import hashlib

router = APIRouter(prefix="/api", tags=["DataService"])

# ============ 缓存查询 ============

@router.get("/cache/query")
async def query_cache(
    request: str,
    mode: str,
    backend: str,
    x_api_key: str = Header(...)
):
    """查询缓存"""
    # 验证 API Key（可选，如果是公共缓存则不需要）
    # user_id = await verify_api_key(x_api_key)

    # 计算哈希
    request_hash = hashlib.sha256(f"{request}|{mode}|{backend}".encode()).hexdigest()

    # 查询缓存
    cache = ResultCache.query.filter_by(request_hash=request_hash).first()

    if cache and cache.expires_at > datetime.now():
        # 缓存命中
        cache.hit_count += 1
        cache.save()

        return {
            "cached": True,
            "result": cache.result
        }

    return {
        "cached": False,
        "result": None
    }

# ============ 任务保存 ============

class SaveTaskRequest(BaseModel):
    request: str
    mode: str
    backend: str
    result: Dict[str, Any]

@router.post("/tasks/save")
async def save_task_result(
    data: SaveTaskRequest,
    x_api_key: str = Header(...)
):
    """保存本地执行的任务结果"""
    user_id = await verify_api_key(x_api_key)

    # 保存任务
    task = Task(
        user_id=user_id,
        request=data.request,
        mode=data.mode,
        backend=data.backend,
        status="completed",
        result=data.result,
        completed_at=datetime.now()
    )
    task.save()

    # 写入缓存
    request_hash = hashlib.sha256(
        f"{data.request}|{data.mode}|{data.backend}".encode()
    ).hexdigest()

    cache = ResultCache(
        request_hash=request_hash,
        request=data.request,
        mode=data.mode,
        backend=data.backend,
        result=data.result,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=1)
    )
    cache.save()

    return {
        "task_id": task.id,
        "message": "Saved successfully"
    }

# ============ 任务历史 ============

@router.get("/tasks/history")
async def get_task_history(
    mode: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    x_api_key: str = Header(...)
):
    """获取任务历史"""
    user_id = await verify_api_key(x_api_key)

    query = Task.query.filter_by(user_id=user_id)
    if mode:
        query = query.filter_by(mode=mode)

    tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()

    return [task.to_dict() for task in tasks]

# ============ 任务详情 ============

@router.get("/tasks/{task_id}")
async def get_task_detail(
    task_id: str,
    x_api_key: str = Header(...)
):
    """获取任务详情"""
    user_id = await verify_api_key(x_api_key)

    task = Task.query.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")

    if task.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    return task.to_dict()
```

---

#### 步骤 4: 配置和使用

**环境变量配置** (`.env` 或 `~/.bashrc`):

```bash
# 可选：启用远程服务
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=your_api_key_here
```

**使用方式**:

```bash
# 方式 1: 纯本地执行（不使用远程）
python master_orchestrator.py "开发博客系统"

# 方式 2: 使用远程缓存和上传（如果配置了环境变量）
python master_orchestrator.py "开发博客系统" --verbose

# 方式 3: 强制禁用远程
python master_orchestrator.py "开发博客系统" --no-remote

# 方式 4: 只查缓存，不上传
python master_orchestrator.py "开发博客系统" --no-upload
```

---

## 优势分析

### 本地 memex-cli vs 远程 memex-cli

| 维度 | 本地 memex-cli (当前方案) | 远程 memex-cli (之前方案) |
|------|--------------------------|-------------------------|
| **API Key 安全** | ✅ 不离开本地 | ❌ 需上传到服务器 |
| **执行速度** | ✅ 无网络延迟 | ❌ HTTP 往返延迟 |
| **离线能力** | ✅ 可离线使用（除AI API） | ❌ 依赖服务器 |
| **服务器负载** | ✅ 低（只存数据） | ❌ 高（执行AI调用） |
| **成本** | ✅ 用户自己的AI配额 | ❌ 服务器统一付费 |
| **隐私** | ✅ 请求不经过服务器 | ❌ 请求经过服务器 |

**结论**: **本地 memex-cli 方案在安全性、隐私和成本上都更优。**

---

### 混合架构的优势

| 功能 | 纯本地 | 纯远程 | **混合架构** |
|------|--------|--------|-------------|
| 离线执行 | ✅ | ❌ | ✅ |
| 结果缓存 | ❌ | ✅ | ✅ (远程缓存) |
| 任务历史 | ❌ | ✅ | ✅ (远程存储) |
| Web UI | ❌ | ✅ | ✅ (查看历史) |
| 跨设备同步 | ❌ | ✅ | ✅ (可选) |
| API Key 安全 | ✅ | ❌ | ✅ (本地) |
| 隐私保护 | ✅ | ❌ | ✅ (本地执行) |

**优势总结**:
1. ✅ **安全优先** - API Key 和请求内容不上传到服务器
2. ✅ **本地优先** - 本地执行，快速响应
3. ✅ **缓存加速** - 远程缓存，避免重复调用
4. ✅ **历史可查** - Web UI 查看历史任务
5. ✅ **可选远程** - 远程服务可选，不强制依赖

---

## 总结

### 最终架构

```
┌──────────────────────────────────────────────────┐
│           本地 (MasterOrchestrator)              │
│                                                  │
│  1. 查询远程缓存（可选）                         │
│  2. 本地执行 memex-cli                           │
│  3. 上传结果到远程（可选）                       │
│                                                  │
│  • API Key 保存在本地                            │
│  • 请求不经过远程服务器                          │
│  • 完全可离线使用                                │
└──────────────────┬───────────────────────────────┘
                   ↓ HTTPS (可选)
┌──────────────────────────────────────────────────┐
│          远程 (aduib-ai 数据服务)                │
│                                                  │
│  • 提供缓存查询                                  │
│  • 存储任务历史                                  │
│  • 支持 Web UI                                   │
│  • 不直接调用 AI                                 │
│                                                  │
│  ✅ 被动服务，不主动执行                         │
└──────────────────────────────────────────────────┘
```

### 核心设计原则

1. **本地优先** - memex-cli 在本地执行
2. **远程可选** - aduib-ai 作为可选数据服务
3. **安全第一** - API Key 不离开本地
4. **隐私保护** - 请求内容不经过远程服务器
5. **渐进增强** - 从纯本地到混合架构平滑升级

---

**文档版本**: 2.0.0
**创建日期**: 2026-01-04
