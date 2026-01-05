# /clear-cache 命令使用指南

## 简介

`/clear-cache` 是一个内置的 Slash Command，用于清除 MasterOrchestrator 的注册表缓存。

当你修改了 skills、commands、agents 或 prompts 的配置文件后，可以使用此命令强制系统在下次启动时重新扫描资源。

## 功能

- 清除 `~/.memex/orchestrator/registry/` 目录下的缓存文件
- 删除 `last_scan.json` 和 `resources_snapshot.json`
- 强制下次启动时重新扫描资源目录

## 使用场景

### 1. 修改了资源配置文件

当你修改了 skills、commands、agents 或 prompts 的 YAML 配置文件后：

```bash
# 使用 /clear-cache 清除缓存
/clear-cache

# 下次启动 MasterOrchestrator 时会重新扫描
```

### 2. 添加了新的资源

当你在 `~/.claude/skills/` 或其他资源目录中添加了新的资源：

```bash
# 清除缓存以识别新资源
/clear-cache
```

### 3. 缓存出现问题

如果遇到资源加载异常或缓存数据损坏：

```bash
# 清除缓存，恢复正常扫描
/clear-cache
```

### 4. 开发调试

在开发和测试新的 skills 时，频繁修改配置：

```bash
# 每次修改后清除缓存
/clear-cache
```

## 命令格式

```bash
/clear-cache
```

该命令不接受任何参数。

## 输出示例

### 有缓存时清除

```
[清除前状态]
  缓存状态: 有效
  上次扫描: 2025-01-05T10:30:00
  资源总数: 15
  文件数: 8

[清除成功]
  缓存已清除，下次启动将重新扫描资源

[清除后状态]
  缓存状态: no_cache
```

### 无缓存时执行

```
[清除前状态]
  缓存状态: no_cache

[清除成功]
  缓存已清除，下次启动将重新扫描资源

[清除后状态]
  缓存状态: no_cache
```

## 技术细节

### 缓存位置

```
~/.memex/orchestrator/registry/
├── last_scan.json          # 扫描元数据（时间戳、哈希等）
└── resources_snapshot.json # 资源快照（完整的资源列表）
```

### 缓存机制

1. **首次启动**: 执行完整的资源扫描，保存结果到缓存
2. **后续启动**: 检查缓存有效性（TTL、文件哈希）
   - 缓存有效：直接加载，跳过扫描（~9ms）
   - 缓存失效：重新扫描，更新缓存（~100-500ms）

### TTL 设置

默认 TTL：1小时（3600秒）

超过 TTL 的缓存会自动失效，触发重新扫描。

## 相关命令

- `/reload`: 重新加载配置（包括清除并重建注册表）
- `/discover`: 重新发现并注册资源
- `/stats`: 查看系统统计信息（包括缓存状态）

## 代码示例

### Python API 调用

```python
from orchestrator import MasterOrchestrator

# 创建 Orchestrator 实例
orch = MasterOrchestrator(auto_discover=True)

# 调用清除缓存方法
result = orch._clear_registry_cache(verbose=True)

print(f"清除成功: {result['success']}")
print(f"消息: {result['message']}")
```

### 直接使用 RegistryPersistence

```python
from pathlib import Path
from core.registry_persistence import RegistryPersistence

# 创建 persistence 实例
registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
persistence = RegistryPersistence(registry_dir=registry_dir)

# 获取统计信息
stats = persistence.get_stats()
print(f"缓存状态: {stats['status']}")

# 清除缓存
persistence.invalidate()
print("缓存已清除")
```

## 常见问题

### Q: 清除缓存后需要重启吗？

A: 不需要。缓存会在下次启动时自动重建。当前会话不受影响。

### Q: 会影响其他功能吗？

A: 不会。只清除资源扫描缓存，不影响日志、临时文件或其他组件。

### Q: 多久清除一次？

A: 通常不需要手动清除。只在以下情况下使用：
- 修改了资源配置文件
- 添加了新资源
- 遇到缓存相关问题

### Q: 如果没有启用 auto_discover 会怎样？

A: 命令会返回错误信息：
```
Registry cache not available (requires auto_discover=True)
```

需要在创建 MasterOrchestrator 时启用 V3 功能：
```python
orch = MasterOrchestrator(auto_discover=True)
```

## 实现细节

### 文件位置

- 命令定义：`core/slash_command_registry.py:328-337`
- 处理方法：`master_orchestrator.py:1329-1401`
- 测试文件：`tests/test_clear_cache_command.py`

### 相关类

- `SlashCommandRegistry`: 命令注册和执行
- `RegistryPersistence`: 缓存持久化管理
- `ConfigLoader`: 配置加载和缓存集成

## 更新日志

- **2025-01-05**: 初始实现，添加 /clear-cache 命令
