# Aduib-AI 集成文档

## 概述

Aduib-AI是一个可选的远程托管服务，为Orchestrator系统提供结果缓存和任务历史管理功能。通过集成aduib-ai，可以：

- **缓存查询结果**：避免重复执行相同的AI任务
- **保存任务历史**：记录所有执行过的任务和结果
- **统计分析**：查看使用统计和缓存命中率
- **Web UI访问**：通过Web界面查看历史记录

**关键特性**：
- 完全可选：系统可以在无aduib-ai时正常工作
- 自动降级：连接失败时自动回退到本地执行
- 异步通信：使用aiohttp实现高性能异步HTTP请求
- 同步接口：对外提供简单的同步API

---

## 架构集成

### 集成层次

```
MasterOrchestrator
    ↓
[缓存查询] AduibClient.query_cache()
    ↓ (缓存未命中)
ExecutionRouter → 本地执行
    ↓ (执行完成)
[结果上传] AduibClient.save_task_result()
```

### 数据流

```
用户请求
    ↓
1. 意图分析 (ClaudeIntentAnalyzer)
    ↓
2. 缓存查询 (AduibClient)
    ├─ 命中 → 直接返回缓存结果
    └─ 未命中 → 继续本地执行
        ↓
3. 本地执行 (ExecutionRouter)
    ↓
4. 结果上传 (AduibClient)
    ↓
5. 返回结果
```

---

## 配置

### 环境变量

```bash
# Aduib-AI服务地址
export ADUIB_URL="https://your-aduib-server.com"

# API密钥（必需）
export ADUIB_API_KEY="your-api-key-here"
```

### 自动检测模式

如果设置了`ADUIB_API_KEY`环境变量，系统会自动启用aduib-ai集成：

```python
from orchestrator import MasterOrchestrator

# 自动检测：有ADUIB_API_KEY就启用
orch = MasterOrchestrator()
```

### 手动配置

```python
from orchestrator import MasterOrchestrator

# 显式启用
orch = MasterOrchestrator(
    use_remote=True,
    aduib_url="https://api.aduib.ai",
    aduib_api_key="your-key",
    enable_cache=True,      # 启用缓存查询
    enable_upload=True      # 启用结果上传
)

# 显式禁用
orch = MasterOrchestrator(
    use_remote=False
)
```

---

## AduibClient API

### 初始化

```python
from orchestrator.clients.aduib_client import AduibClient

# 从环境变量读取配置
client = AduibClient()

# 手动配置
client = AduibClient(
    base_url="https://api.aduib.ai",
    api_key="your-api-key",
    timeout=30  # 请求超时（秒）
)
```

### 核心方法

#### 1. 查询缓存

```python
cached = client.query_cache(
    request="你的请求",
    mode="command",         # command/agent/prompt/skill/backend
    backend="claude"        # claude/gemini/codex
)

if cached:
    print(f"缓存命中！")
    print(f"输出: {cached.output}")
    print(f"命中次数: {cached.hit_count}")
    print(f"创建时间: {cached.created_at}")
else:
    print("缓存未命中，需要执行")
```

**返回值** (`CachedResult`):
```python
@dataclass
class CachedResult:
    task_id: str          # 任务ID
    output: str           # 输出内容
    success: bool         # 是否成功
    created_at: str       # 创建时间
    hit_count: int        # 缓存命中次数
```

#### 2. 保存任务结果

```python
success = client.save_task_result(
    request="你的请求",
    mode="command",
    backend="claude",
    success=True,
    output="执行结果",
    error=None,                    # 错误信息（可选）
    run_id="memex-run-123",        # memex-cli运行ID（可选）
    duration_seconds=2.5           # 执行耗时（可选）
)

if success:
    print("结果已保存到aduib-ai")
```

#### 3. 获取任务历史

```python
history = client.get_task_history(
    limit=50,              # 返回数量
    offset=0,              # 偏移量（分页）
    mode="command",        # 过滤模式（可选）
    backend="claude"       # 过滤后端（可选）
)

for task in history:
    print(f"[{task['mode']}] {task['request'][:50]}...")
    print(f"  创建时间: {task['created_at']}")
    print(f"  成功: {task['success']}")
```

#### 4. 健康检查

```python
is_healthy = client.health_check()

if is_healthy:
    print("✓ Aduib-AI服务可用")
else:
    print("✗ Aduib-AI服务不可用")
```

#### 5. 获取统计信息

```python
stats = client.get_stats()

if stats:
    print(f"总任务数: {stats['total_tasks']}")
    print(f"缓存命中率: {stats['cache_hit_rate']}%")
    print(f"成功率: {stats['success_rate']}%")
```

---

## 缓存机制

### 缓存键计算

缓存键基于请求内容、执行模式和后端类型计算：

```python
cache_key = SHA256(f"{request}:{mode}:{backend}")
```

**示例**:
```python
request = "查看git状态"
mode = "command"
backend = "claude"

# cache_key = SHA256("查看git状态:command:claude")
# = "a7f3b2c1..."
```

### 缓存命中逻辑

```python
# 1. 计算缓存键
cache_key = compute_hash(request, mode, backend)

# 2. 查询aduib-ai
cached = aduib_client.query_cache(request, mode, backend)

# 3. 判断是否命中
if cached:
    # 缓存命中：直接使用缓存结果
    return cached.output
else:
    # 缓存未命中：执行任务
    result = execute_task(request)

    # 保存到缓存
    aduib_client.save_task_result(...)

    return result
```

### 缓存失效

缓存由aduib-ai服务端管理，客户端不需要处理失效逻辑。服务端可能基于以下策略失效缓存：

- 时间过期（TTL）
- 存储空间限制（LRU）
- 手动清除

---

## 在MasterOrchestrator中的使用

### 自动缓存和上传

```python
from orchestrator import MasterOrchestrator

orch = MasterOrchestrator(
    use_remote=True,
    enable_cache=True,     # 启用缓存查询
    enable_upload=True     # 启用结果上传
)

# 第一次执行：缓存未命中，执行后上传
result1 = orch.process("查看git状态", verbose=True)
# 输出:
# [缓存未命中] 本地执行任务
# [命令执行] git status
# [结果上传] 成功保存到aduib-ai

# 第二次执行：缓存命中
result2 = orch.process("查看git状态", verbose=True)
# 输出:
# [缓存命中] 从远程缓存返回结果
```

### 仅缓存，不上传

```python
orch = MasterOrchestrator(
    use_remote=True,
    enable_cache=True,      # 启用缓存查询
    enable_upload=False     # 禁用结果上传
)

# 只查询缓存，不上传新结果
result = orch.process("查看git状态")
```

### 仅上传，不缓存

```python
orch = MasterOrchestrator(
    use_remote=True,
    enable_cache=False,     # 禁用缓存查询
    enable_upload=True      # 启用结果上传
)

# 总是执行，但保存结果
result = orch.process("查看git状态")
```

### 命令行参数

```bash
# 启用远程服务
python -m orchestrator.master_orchestrator "查看git状态" --use-remote

# 禁用缓存
python -m orchestrator.master_orchestrator "查看git状态" --use-remote --no-cache

# 禁用上传
python -m orchestrator.master_orchestrator "查看git状态" --use-remote --no-upload

# 自定义服务地址
python -m orchestrator.master_orchestrator "查看git状态" \
    --aduib-url "https://my-server.com" \
    --aduib-api-key "my-key"
```

---

## 错误处理

### 自动降级

AduibClient设计为**完全可选**。所有错误都会被捕获并降级到本地执行：

```python
# 缓存查询失败 → 继续本地执行
try:
    cached = aduib_client.query_cache(...)
except Exception as e:
    print(f"[警告] 缓存查询失败: {e}")
    # 继续本地执行
    result = execute_locally(...)

# 结果上传失败 → 不影响返回结果
try:
    aduib_client.save_task_result(...)
except Exception as e:
    print(f"[警告] 结果上传失败: {e}")
    # 已经有本地结果，直接返回
    return result
```

### 常见错误和解决方案

#### 1. 未设置API密钥

**错误**:
```
ValueError: 未提供 ADUIB_API_KEY。请设置环境变量或传入 api_key 参数。
```

**解决**:
```bash
export ADUIB_API_KEY="your-api-key"
```

#### 2. 服务不可用

**警告**:
```
[警告] 无法连接到 aduib-ai 服务: Connection refused
[提示] 将以纯本地模式运行
```

**解决**:
- 检查`ADUIB_URL`是否正确
- 检查网络连接
- 检查aduib-ai服务是否运行
- 或者禁用远程模式：`use_remote=False`

#### 3. aiohttp未安装

**错误**:
```
ImportError: 请安装 aiohttp 库以使用远程服务：pip install aiohttp
```

**解决**:
```bash
pip install aiohttp
```

#### 4. 超时

**警告**:
```
[警告] 缓存查询超时
```

**解决**:
```python
client = AduibClient(timeout=60)  # 增加超时时间
```

---

## 性能考虑

### 异步通信

AduibClient使用`aiohttp`进行异步HTTP请求，但对外提供同步接口：

```python
# 内部：异步实现
async def _query_cache_async(self, ...):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ...) as response:
            return await response.json()

# 对外：同步接口
def query_cache(self, ...):
    return asyncio.run(self._query_cache_async(...))
```

**优势**:
- 高效的异步I/O
- 简单的同步API（无需async/await）
- 自动管理连接池

### 缓存命中收益

假设AI任务平均耗时5秒，缓存查询耗时0.1秒：

| 缓存命中率 | 平均耗时 | 性能提升 |
|-----------|---------|---------|
| 0% | 5.0s | - |
| 20% | 4.1s | 18% |
| 50% | 2.5s | 50% |
| 80% | 1.1s | 78% |

### 超时配置

```python
# 缓存查询超时：30秒（默认）
client = AduibClient(timeout=30)

# 健康检查超时：5秒（固定）
client.health_check()  # 5秒超时
```

---

## 测试

### 单独测试AduibClient

```bash
# 健康检查
python -m orchestrator.clients.aduib_client --action health

# 获取统计信息
python -m orchestrator.clients.aduib_client --action stats

# 获取历史记录
python -m orchestrator.clients.aduib_client --action history

# 自定义配置
python -m orchestrator.clients.aduib_client \
    --url "https://my-server.com" \
    --api-key "my-key" \
    --action stats
```

### 集成测试

```python
from orchestrator import MasterOrchestrator

# 启用verbose查看缓存行为
orch = MasterOrchestrator(use_remote=True)

# 第一次执行
print("=== 第一次执行 ===")
result1 = orch.process("查看git状态", verbose=True)

# 第二次执行（应该命中缓存）
print("\n=== 第二次执行 ===")
result2 = orch.process("查看git状态", verbose=True)

# 验证结果一致
assert result1.output == result2.output
```

---

## API服务端规范

### REST端点

#### 1. 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "ok"
}
```

#### 2. 缓存查询

```http
GET /api/cache/query?request_hash={hash}&mode={mode}&backend={backend}
Authorization: Bearer {api_key}
```

**响应（命中）**:
```json
{
  "task_id": "123456",
  "output": "执行结果",
  "success": true,
  "created_at": "2026-01-04T12:00:00Z",
  "hit_count": 5
}
```

**响应（未命中）**:
```http
404 Not Found
```

#### 3. 保存任务结果

```http
POST /api/tasks/save
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "request": "用户请求",
  "request_hash": "a7f3b2c1...",
  "mode": "command",
  "backend": "claude",
  "success": true,
  "output": "执行结果",
  "error": null,
  "run_id": "memex-123",
  "duration_seconds": 2.5,
  "created_at": "2026-01-04T12:00:00Z"
}
```

**响应**:
```http
201 Created
```

#### 4. 任务历史

```http
GET /api/tasks/history?limit=50&offset=0&mode=command&backend=claude
Authorization: Bearer {api_key}
```

**响应**:
```json
[
  {
    "task_id": "123456",
    "request": "用户请求",
    "mode": "command",
    "backend": "claude",
    "success": true,
    "created_at": "2026-01-04T12:00:00Z"
  },
  ...
]
```

#### 5. 统计信息

```http
GET /api/stats
Authorization: Bearer {api_key}
```

**响应**:
```json
{
  "total_tasks": 1234,
  "cache_hit_rate": 65.5,
  "success_rate": 98.2,
  "backends": {
    "claude": 500,
    "gemini": 400,
    "codex": 334
  },
  "modes": {
    "command": 600,
    "agent": 400,
    "prompt": 234
  }
}
```

---

## 数据结构

### CacheQuery

```python
@dataclass
class CacheQuery:
    request_hash: str
    mode: str
    backend: str
```

### TaskData

```python
@dataclass
class TaskData:
    request: str
    request_hash: str
    mode: str
    backend: str
    success: bool
    output: str
    error: Optional[str] = None
    run_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None
```

### CachedResult

```python
@dataclass
class CachedResult:
    task_id: str
    output: str
    success: bool
    created_at: str
    hit_count: int
```

---

## 安全考虑

### API密钥管理

**推荐**:
```bash
# 使用环境变量（不要硬编码）
export ADUIB_API_KEY="your-api-key"
```

**不推荐**:
```python
# 硬编码密钥（不安全）
client = AduibClient(api_key="hardcoded-key")
```

### HTTPS通信

生产环境应使用HTTPS：

```bash
export ADUIB_URL="https://api.aduib.ai"  # HTTPS
# 不要使用: http://api.aduib.ai          # HTTP
```

### 请求头

所有请求自动包含认证头：

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

---

## 最佳实践

### 1. 启用缓存以提高性能

```python
orch = MasterOrchestrator(
    use_remote=True,
    enable_cache=True,     # ✓ 推荐
    enable_upload=True
)
```

### 2. 设置合理的超时

```python
client = AduibClient(
    timeout=30  # 缓存查询不应太慢
)
```

### 3. 监控缓存命中率

```python
stats = client.get_stats()
if stats and stats['cache_hit_rate'] < 50:
    print("[提示] 缓存命中率较低，考虑优化请求模式")
```

### 4. 处理网络故障

```python
# AduibClient已经自动处理，无需额外代码
orch = MasterOrchestrator(use_remote=True)

# 网络故障时自动降级到本地执行
result = orch.process("查看git状态")  # 总是有结果
```

### 5. 使用verbose调试

```python
# 开发时启用verbose查看缓存行为
result = orch.process("你的请求", verbose=True)

# 输出:
# [缓存查询] 查询远程缓存...
# [缓存命中] 从远程缓存返回结果
# 或
# [缓存未命中] 本地执行任务
# [结果上传] 成功保存到aduib-ai
```

---

## 故障排查清单

- [ ] `ADUIB_API_KEY`环境变量已设置？
- [ ] `ADUIB_URL`正确（包含协议如https://）？
- [ ] `aiohttp`库已安装（`pip install aiohttp`）？
- [ ] 网络连接正常（可以访问aduib-ai服务）？
- [ ] API密钥有效（未过期/未被撤销）？
- [ ] 服务端健康检查通过（`/health`返回200）？
- [ ] 检查防火墙/代理设置？

---

## 示例代码

### 完整集成示例

```python
#!/usr/bin/env python3
"""
Aduib-AI集成示例
"""

from orchestrator import MasterOrchestrator
from orchestrator.clients.aduib_client import AduibClient
import os

def main():
    # 1. 检查环境变量
    api_key = os.getenv("ADUIB_API_KEY")
    if not api_key:
        print("[提示] 未设置ADUIB_API_KEY，将以本地模式运行")
        orch = MasterOrchestrator(use_remote=False)
    else:
        print("[✓] 检测到ADUIB_API_KEY，启用远程服务")

        # 2. 健康检查
        client = AduibClient()
        if client.health_check():
            print("[✓] Aduib-AI服务可用")
        else:
            print("[警告] Aduib-AI服务不可用，将以本地模式运行")
            orch = MasterOrchestrator(use_remote=False)
            return

        # 3. 创建带缓存的协调器
        orch = MasterOrchestrator(
            use_remote=True,
            enable_cache=True,
            enable_upload=True
        )

    # 4. 执行任务
    requests = [
        "查看git状态",
        "分析项目架构",
        "生成API文档"
    ]

    for req in requests:
        print(f"\n{'='*60}")
        print(f"请求: {req}")
        print('='*60)

        result = orch.process(req, verbose=True)

        print(f"\n结果预览:")
        output = result.output if hasattr(result, 'output') else str(result)
        print(output[:200] + ("..." if len(output) > 200 else ""))

    # 5. 查看统计
    if api_key:
        stats = client.get_stats()
        if stats:
            print(f"\n{'='*60}")
            print("使用统计:")
            print('='*60)
            print(f"总任务数: {stats.get('total_tasks', 0)}")
            print(f"缓存命中率: {stats.get('cache_hit_rate', 0):.1f}%")
            print(f"成功率: {stats.get('success_rate', 0):.1f}%")

if __name__ == "__main__":
    main()
```

---

## 参考资料

- **源代码**: `orchestrator/clients/aduib_client.py`
- **集成代码**: `orchestrator/master_orchestrator.py`
- **测试示例**: 运行`python -m orchestrator.clients.aduib_client`
- **架构文档**: `docs/MEMEX_CLI_INTEGRATION_DESIGN.md`

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-04
**维护者**: Orchestrator Team
