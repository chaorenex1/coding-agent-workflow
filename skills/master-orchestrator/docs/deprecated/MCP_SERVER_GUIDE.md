# Master Orchestrator MCP Server 使用指南

## 概述

Master Orchestrator V2.0 引入了基于 Claude Agent SDK 的 MCP Server 模式，实现了：

- **统一请求拦截**：通过 Hooks 系统拦截所有工具调用
- **智能任务调度**：自动分析意图并选择最优执行路径
- **异步执行支持**：原生异步 API，与 SDK 无缝集成
- **权限控制**：细粒度的工具访问控制和审计日志

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Agent SDK App                     │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Claude Client│◄────►│  MCP Server  │                    │
│  │              │      │              │                    │
│  │  + Hooks     │      │  orchestrate │                    │
│  │  + Tools     │      │  analyze     │                    │
│  └──────┬───────┘      │  list_caps   │                    │
│         │              └──────┬───────┘                    │
│         │                     │                            │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌─────────────────────────────────┐                      │
│  │   Request Interceptor (Hooks)   │                      │
│  │                                  │                      │
│  │  PreToolUse  → Redirect/Block   │                      │
│  │  PostToolUse → Audit/Filter     │                      │
│  └───────────┬──────────────────────┘                     │
│              │                                             │
│              ▼                                             │
│  ┌─────────────────────────────────┐                      │
│  │   Async Master Orchestrator     │                      │
│  │                                  │                      │
│  │  + Intent Analysis               │                      │
│  │  + Mode Routing                  │                      │
│  │  + Backend Selection             │                      │
│  └───────────┬──────────────────────┘                     │
│              │                                             │
│              ▼                                             │
│  ┌──────────────────────────────────────┐                 │
│  │  Executors (Command/Agent/Prompt)    │                 │
│  └──────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## 安装

### 1. 安装依赖

```bash
# 核心依赖
pip install pyyaml chardet aiohttp

# MCP Server 支持（必需）
pip install claude-agent-sdk

# 开发依赖（可选）
pip install pytest pytest-asyncio black mypy
```

### 2. 验证安装

```bash
cd skills/master-orchestrator
python -c "from core.mcp_server import create_orchestrator_server; print('✅ MCP Server 可用')"
```

## 快速开始

### 方式 1: 直接调用 MCP Tools

```python
import asyncio
from core.mcp_server import orchestrate, analyze_intent, list_capabilities

async def main():
    # 1. 意图分析（不执行）
    result = await analyze_intent({
        "request": "开发用户认证功能",
        "verbose": True
    })
    print(f"模式: {result['mode']}, 复杂度: {result['complexity']}")

    # 2. 执行任务（Dry-run）
    result = await orchestrate({
        "request": "检查 git 状态",
        "dry_run": True,
        "verbose": True
    })
    print(f"执行计划: {result}")

    # 3. 实际执行
    result = await orchestrate({
        "request": "检查 git 状态",
        "verbose": False
    })
    print(f"结果: {result['output']}")

    # 4. 列出系统能力
    result = await list_capabilities({"resource_type": "all"})
    print(f"可用资源: {result['total_count']} 项")

asyncio.run(main())
```

### 方式 2: 集成到 Claude SDK 应用

```python
from claude_agent_sdk import ClaudeSDKClient
from core.mcp_server import create_orchestrator_server
from core.request_interceptor import create_hooks

# 1. 创建 MCP Server
server = create_orchestrator_server()

# 2. 创建 Hooks（请求拦截）
hooks = create_hooks(enable_audit=True)

# 3. 创建 Claude Client（集成 server 和 hooks）
client = ClaudeSDKClient(
    api_key="your_api_key",
    servers=[server],
    hooks=hooks
)

# 4. 发送请求（自动路由到 orchestrator）
response = await client.send_message(
    "开发一个用户认证功能",
    model="claude-sonnet-4.5"
)

# 5. 查看审计日志
from core.request_interceptor import get_audit_summary
summary = get_audit_summary()
print(f"总请求: {summary['total_requests']}, 拦截: {summary['redirected']}")
```

## MCP Tools API

### orchestrate

**描述**: 智能任务调度工具，自动分析意图并执行。

**输入参数**:
```json
{
  "request": "用户任务描述（自然语言）",
  "mode": "command|agent|prompt|skill|backend（可选，强制模式）",
  "context": {
    "key": "value（可选，额外上下文）"
  },
  "verbose": false,
  "dry_run": false
}
```

**输出**:
```json
{
  "success": true,
  "mode": "实际使用的执行模式",
  "backend": "使用的后端（claude/gemini/codex）",
  "result": "执行结果",
  "error": null,
  "metadata": {
    "duration": 3.5,
    "run_id": "uuid",
    "tools_used": ["tool1", "tool2"]
  }
}
```

**使用示例**:
```python
# 基础用法
result = await orchestrate({"request": "检查 git 状态"})

# 强制指定模式
result = await orchestrate({
    "request": "生成 React 组件",
    "mode": "prompt"
})

# Dry-run（仅分析）
result = await orchestrate({
    "request": "部署到生产环境",
    "dry_run": True
})
```

### analyze_intent

**描述**: 分析用户请求的意图（不执行）。

**输入参数**:
```json
{
  "request": "用户任务描述",
  "verbose": true
}
```

**输出**:
```json
{
  "mode": "command|agent|prompt|skill|backend",
  "task_type": "dev|ux|ops|analysis|...",
  "complexity": "low|medium|high",
  "confidence": 0.95,
  "backend_hint": "claude|gemini|codex",
  "skill_hint": "skill-name",
  "reasoning": "分析推理过程"
}
```

### list_capabilities

**描述**: 列出系统的所有能力（Skills/Commands/Prompts/Agents）。

**输入参数**:
```json
{
  "resource_type": "skills|commands|prompts|agents|all"
}
```

**输出**:
```json
{
  "skills": [...],
  "commands": [...],
  "prompts": [...],
  "agents": [...],
  "backends": ["claude", "gemini", "codex"],
  "total_count": 50
}
```

## Hooks 系统

### 拦截规则配置

默认拦截规则（`core/request_interceptor.py`）：

| 工具名称 | 动作 | 原因 |
|---------|------|------|
| `Write` | REDIRECT | 文件写入操作需要统一调度 |
| `Edit` | REDIRECT | 文件编辑操作需要统一调度 |
| `Read` | REDIRECT | 文件读取操作需要统一调度 |
| `Bash` | REDIRECT | Shell 命令需要安全检查 |
| `Task` | REDIRECT | 子任务需要统一管理 |
| `Skill` | ALLOW | Skill 内部已有路由逻辑 |
| `Glob` | ALLOW | 只读操作，性能优先 |
| `Grep` | ALLOW | 只读操作，性能优先 |
| `*` | LOG_ONLY | 默认策略：记录但不拦截 |

### 自定义拦截规则

```python
from core.request_interceptor import InterceptRule, InterceptAction, create_hooks

# 定义自定义规则
custom_rules = [
    InterceptRule(
        tool_pattern="CustomTool",
        action=InterceptAction.BLOCK,
        reason="此工具已废弃"
    ),
    InterceptRule(
        tool_pattern="DangerousTool",
        action=InterceptAction.REDIRECT,
        redirect_to="mcp__master_orchestrator__orchestrate",
        reason="需要审批"
    )
]

# 创建 hooks
hooks = create_hooks(rules=custom_rules, enable_audit=True)
```

### 审计日志

```python
from core.request_interceptor import get_audit_summary

# 获取审计摘要
summary = get_audit_summary()

print(f"总请求数: {summary['total_requests']}")
print(f"重定向: {summary['redirected']}")
print(f"允许: {summary['allowed']}")
print(f"阻止: {summary['blocked']}")

# 查看详细日志
for log in summary['log']:
    print(f"{log['timestamp']}: {log['event']} - {log['data']}")
```

## 异步 Orchestrator

### 基本用法

```python
from core.async_orchestrator import AsyncMasterOrchestrator

orch = AsyncMasterOrchestrator(
    use_claude_intent=True,
    fallback_to_rules=True,
    enable_parallel=True
)

# 异步处理请求
result = await orch.process_async(
    request="开发用户认证功能",
    verbose=True,
    dry_run=False
)

print(f"成功: {result['success']}")
print(f"模式: {result['mode']}")
print(f"后端: {result['backend']}")
print(f"耗时: {result['duration']}s")
```

### 强制指定执行模式

```python
# 强制使用 command 模式
result = await orch.process_async(
    request="git status",
    forced_mode="command"
)

# 强制使用特定后端
result = await orch.process_async(
    request="优化性能",
    forced_mode="backend",
    context={"backend": "codex"}
)
```

### 批量处理（并行）

```python
# 异步批量处理多个任务
tasks = [
    orch.process_async("检查 git 状态"),
    orch.process_async("运行测试"),
    orch.process_async("构建项目")
]

results = await asyncio.gather(*tasks)

for result in results:
    print(f"任务: {result['mode']}, 成功: {result['success']}")
```

## 配置

### orchestrator.yaml

```yaml
# MCP Server 配置
mcp_server:
  enabled: true
  name: "master-orchestrator"
  version: "2.0.0"

# Hooks 配置
hooks:
  enabled: true
  audit: true
  dry_run: false  # 生产环境设为 false

# 拦截规则
intercept_rules:
  - tool: "Write"
    action: "redirect"
  - tool: "Bash"
    action: "redirect"
  - tool: "Read"
    action: "allow"  # 覆盖默认规则

# 意图分析配置
intent_analysis:
  use_claude: true
  confidence_threshold: 0.75
  fallback_to_rules: true

# 并行执行配置
parallel:
  enabled: true
  max_workers: 3
  timeout_per_task: 300
```

## 测试

### 运行单元测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
cd skills/master-orchestrator
pytest tests/test_mcp_server.py -v
pytest tests/test_async_orchestrator.py -v
pytest tests/test_request_interceptor.py -v
```

### 运行演示

```bash
# 基础演示（无需 API Key）
python examples/mcp_server_demo.py

# 完整演示（需要 API Key）
export ANTHROPIC_API_KEY=your_key
python examples/mcp_server_demo.py
```

## 故障排查

### 问题 1: "Claude Agent SDK 未安装"

**解决方案**:
```bash
pip install claude-agent-sdk
```

### 问题 2: "MCP Server 创建失败"

**检查**:
1. 确认 `core/mcp_server.py` 存在
2. 检查导入路径是否正确
3. 查看日志: `logging.basicConfig(level=logging.DEBUG)`

### 问题 3: Hooks 不生效

**原因**: Hooks 需要在 ClaudeSDKClient 初始化时注册

**解决方案**:
```python
hooks = create_hooks()
client = ClaudeSDKClient(hooks=hooks)  # 确保传入 hooks
```

### 问题 4: 拦截规则不匹配

**调试**:
```python
from core.request_interceptor import get_interceptor

interceptor = get_interceptor()
rule = interceptor.match_rule("YourToolName")
print(f"匹配规则: {rule.action.value} - {rule.reason}")
```

## 最佳实践

### 1. 生产环境配置

```python
# 生产环境：禁用 dry_run，启用审计
hooks = create_hooks(
    dry_run=False,
    enable_audit=True
)

# 定期导出审计日志
summary = get_audit_summary()
with open("audit.log", "w") as f:
    json.dump(summary, f, indent=2)
```

### 2. 错误处理

```python
try:
    result = await orchestrate({
        "request": "potentially failing task"
    })

    if not result['success']:
        logger.error(f"任务失败: {result['error']}")
        # 实现重试逻辑

except Exception as e:
    logger.error(f"未捕获的异常: {e}", exc_info=True)
```

### 3. 性能优化

```python
# 对于简单任务，使用 command 模式避免 LLM 调用
result = await orchestrate({
    "request": "git status",
    "mode": "command"  # 跳过意图分析
})

# 对于只读操作，配置为 ALLOW（不拦截）
custom_rules = [
    InterceptRule(
        tool_pattern="Glob",
        action=InterceptAction.ALLOW,
        reason="只读操作，直接执行"
    )
]
```

### 4. 安全性

```python
# 生产环境：阻止危险命令
dangerous_patterns = ["rm -rf", "DROP TABLE", "format"]

custom_rules = [
    InterceptRule(
        tool_pattern="Bash",
        action=InterceptAction.REDIRECT,
        redirect_to="mcp__master_orchestrator__orchestrate",
        reason="需要安全检查"
    )
]

hooks = create_hooks(rules=custom_rules)
```

## 更新日志

### V2.0.0 (2025-01-08)

- ✨ 新增 MCP Server 模式
- ✨ 新增 Async Orchestrator
- ✨ 新增 Hooks 系统（请求拦截）
- ✨ 新增审计日志功能
- 📝 完善文档和示例

## 路线图

- [ ] 支持更多拦截规则（正则表达式、条件判断）
- [ ] 实现权限系统（基于角色的访问控制）
- [ ] 添加指标监控（Prometheus/Grafana）
- [ ] 支持分布式部署（多个 orchestrator 实例）
- [ ] WebUI 管理界面

## 参考资料

- [Claude Agent SDK 文档](https://platform.claude.com/docs/en/agent-sdk/python)
- [MCP Protocol 规范](https://modelcontextprotocol.io/)
- [Master Orchestrator README](../README.md)

## 支持

如有问题，请：
1. 查看本文档的"故障排查"章节
2. 运行 `examples/mcp_server_demo.py` 验证环境
3. 查看日志: `~/.memex/orchestrator/logs/`
4. 提交 Issue（包含完整错误日志和环境信息）
