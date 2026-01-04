# MasterOrchestrator V3 示例

本目录包含 MasterOrchestrator V3 的完整使用示例。

## 快速开始

### 最简单的例子

```bash
python examples/quick_start_v3.py
```

这个脚本演示了：
- ✅ 基本用法
- ✅ 并行批处理
- ✅ 资源列表
- ✅ 自定义配置

### 完整功能演示

```bash
python examples/v3_features_demo.py
```

这个脚本演示了所有 V3 功能：
- ✅ 自动注册发现
- ✅ 并行批处理
- ✅ DevWorkflow 并行执行
- ✅ 配置管理
- ✅ 资源查询
- ✅ 性能对比

## 示例列表

| 文件 | 功能 | 难度 |
|------|------|------|
| `quick_start_v3.py` | V3 快速开始 | ⭐ 简单 |
| `v3_features_demo.py` | 完整功能演示 | ⭐⭐ 中等 |
| `test_dev_workflow_parallel.py` | DevWorkflow 并行测试 | ⭐⭐ 中等 |

## 使用方法

### 1. 基本用法

```python
from orchestrator import MasterOrchestrator

# 启用自动发现
orch = MasterOrchestrator(auto_discover=True)

# 处理请求
result = orch.process("查看 git 状态")
```

### 2. 并行批处理

```python
# 启用并行
orch = MasterOrchestrator(
    auto_discover=True,
    enable_parallel=True,
    max_parallel_workers=3
)

# 批量请求
requests = ["请求1", "请求2", "请求3"]
result = orch.process_batch(requests, enable_parallel=True)

print(f"成功: {result.successful}/{result.total_tasks}")
```

### 3. DevWorkflow 并行

```python
from orchestrator.skills.dev_workflow import DevWorkflowAgent

# 创建并行工作流
agent = DevWorkflowAgent(
    enable_parallel=True,
    max_workers=2
)

# 执行工作流
result = agent.run("创建应用", verbose=True)
```

### 4. 列出资源

```python
# 列出所有资源
all_resources = orch.list_resources()

# 按类型过滤
skills = orch.list_resources(type_filter="skill")
commands = orch.list_resources(type_filter="command")

# 按来源过滤
project_resources = orch.list_resources(source_filter="project")
```

## 配置文件

在项目根目录创建 `orchestrator.yaml`:

```yaml
version: "3.0"

global:
  default_backend: claude
  enable_parallel: true
  max_parallel_tasks: 3

skills:
  manual:
    - name: my-skill
      path: ./skills/my-skill.yaml
      priority: 100

commands:
  whitelist:
    - git
    - npm
    - python

parallel:
  enabled: true
  max_workers: 3
  timeout_per_task: 120
```

## 运行特定演示

```bash
# 运行演示 1（自动发现）
python examples/v3_features_demo.py --demo 1

# 运行演示 2（并行批处理）
python examples/v3_features_demo.py --demo 2

# 运行演示 3（DevWorkflow）
python examples/v3_features_demo.py --demo 3

# 运行演示 4（配置管理）
python examples/v3_features_demo.py --demo 4

# 运行演示 5（资源查询）
python examples/v3_features_demo.py --demo 5

# 运行演示 6（性能对比）
python examples/v3_features_demo.py --demo 6
```

## 故障排查

### 问题: 自动发现未工作

```python
# 检查是否启用
orch = MasterOrchestrator(auto_discover=True)  # 必须设置

# 检查配置文件
import os
print(os.path.exists("./orchestrator.yaml"))
```

### 问题: 并行未生效

```python
# 检查是否同时启用了自动发现和并行
orch = MasterOrchestrator(
    auto_discover=True,      # 必须启用
    enable_parallel=True     # 必须启用
)
```

### 问题: 资源未加载

```python
# 检查资源列表
resources = orch.list_resources()
print(f"加载了 {len(resources)} 个资源")
```

## 更多信息

- [自动发现文档](../docs/AUTO_DISCOVERY.md)
- [并行执行文档](../docs/PARALLEL_EXECUTION.md)
- [架构文档](../docs/ARCHITECTURE.md)

---

**最后更新**: 2026-01-04
**版本**: 3.0.0
