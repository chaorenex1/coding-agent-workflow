# Orchestrator V3.1 配置项使用情况检查报告

生成时间: 2026-01-06

## 配置项分类

### ✅ 已实现并使用的配置

| 配置节 | 配置项 | 实现位置 | 使用情况 |
|--------|--------|----------|----------|
| **global** | `default_backend` | `config_loader.py` | ✅ 加载到 global_settings |
| **global** | `timeout` | `config_loader.py` | ✅ 加载到 global_settings |
| **global** | `verbose` | `config_loader.py` | ✅ 加载到 global_settings |
| **global** | `enable_v3` | `config_loader.py` | ✅ 加载到 global_settings |
| **global** | `enable_auto_discovery` | `config_loader.py:180` | ✅ ConfigLoader.__init__ 使用 |
| **global** | `project_root` | `config_loader.py:189` | ✅ ConfigLoader.__init__ 使用 |
| **slash_commands** | 所有子配置 | `config_loader.py:644-745` | ✅ _populate_config_from_dict 完整实现 |
| **skills.manual** | 所有配置项 | `config_loader.py:610-629` | ✅ 手动 skill 注册 |
| **skills.auto_discovery** | - | `config_loader.py:340-420` | ✅ 自动发现逻辑 |
| **commands.whitelist** | - | `config_loader.py:634-641` | ✅ 命令白名单 |
| **commands.aliases** | - | `config_loader.py:644-654` | ✅ 命令别名 |
| **agents** | 配置项 | `config_loader.py:657-671` | ✅ Agent 配置加载 |
| **prompts** | 配置项 | `config_loader.py:674-690` | ✅ Prompt 配置加载 |
| **parallel** | 所有配置项 | `config_loader.py:693-701` | ✅ 并行配置加载 |

### ⚠️ 配置节已定义但未在 _populate_config_from_dict 中处理

| 配置节 | 模板位置 | 问题 | 影响 |
|--------|----------|------|------|
| **registry** | 289-301 行 | ❌ 未在 _populate_config_from_dict 中处理 | 配置文件中的 registry 配置不会生效 |
| **logging** | 258-271 行 | ❌ 未在 _populate_config_from_dict 中处理 | 依赖硬编码或其他机制 |
| **cache** | 276-284 行 | ❌ 未在 _populate_config_from_dict 中处理 | 配置项无效 |
| **security** | 368-377 行 | ❌ 未在 _populate_config_from_dict 中处理 | 配置项无效 |
| **skills.auto_discovery** | 150-154 行 | ⚠️ 仅在代码硬编码使用 | 无法通过配置文件控制 scan_user/scan_project |
| **agents.auto_discovery** | 222-225 行 | ⚠️ 配置项存在但未读取 | 配置无效 |
| **agents.default** | 228-231 行 | ⚠️ 配置项存在但未读取 | 配置无效 |
| **prompts.auto_discovery** | 251-254 行 | ⚠️ 配置项存在但未读取 | 配置无效 |

### 🔧 已硬编码在代码中的配置

| 配置项 | 代码位置 | 硬编码值 | 说明 |
|--------|----------|----------|------|
| Registry TTL | `config_loader.py:217` | 3600 秒 | 无法通过配置文件修改 |
| Registry 目录 | `config_loader.py:216` | `~/.memex/orchestrator/registry` | 无法通过配置文件修改 |
| Auto-discovery 启用 | `config_loader.py:180` | `enable_auto_discovery` 参数 | 仅能通过构造函数参数控制 |

## 问题分析

### 1. Registry 配置无法生效

**问题**: 模板中定义了 `registry` 配置节（289-301行），但 `_populate_config_from_dict` 没有处理该配置。

**影响**: 用户在配置文件中设置的 registry 配置（enabled, directory, ttl, show_stats）不会生效。

**现状**: Registry 配置硬编码在 `ConfigLoader.__init__`:
```python
registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
self.persistence = RegistryPersistence(registry_dir=registry_dir, ttl_seconds=3600)
```

### 2. Logging 配置未实现

**问题**: 模板中定义了 `logging` 配置节（258-271行），但未在配置加载器中处理。

**影响**: 日志配置依赖 Python logging.basicConfig 或其他硬编码机制，无法通过配置文件控制。

**建议**: 
- 如果需要支持，在 `_populate_config_from_dict` 中添加 logging 配置处理
- 或从模板中删除该配置节

### 3. Cache 配置未实现

**问题**: 模板定义了 `cache` 配置节（276-284行），但未实现。

**影响**: 缓存配置无效。

**建议**: 从模板中删除或实现该功能。

### 4. Security 配置未实现

**问题**: 模板定义了 `security` 配置节（368-377行），但未实现。

**影响**: 安全配置无效。

**建议**: 从模板中删除或实现该功能。

### 5. Auto-discovery 子配置未读取

**问题**: 模板定义了 `skills.auto_discovery.scan_user` 和 `scan_project` 配置，但代码未读取这些配置。

**现状**: Auto-discovery 在代码中硬编码启用：
```python
if self.enable_auto_discovery and self.scanner and self.user_config_dir.exists():
    discovered = self.scanner.scan_all(self.user_config_dir, source="user")
```

**建议**: 
- 实现配置读取逻辑，支持选择性扫描 user/project
- 或从模板中删除这些配置项

## 修复建议

### 优先级 1: 移除未实现的配置节

从模板中删除以下未实现的配置节，避免误导用户：
- `logging` (258-271行) - 除非计划实现
- `cache` (276-284行) - 除非计划实现  
- `security` (368-377行) - 除非计划实现

### 优先级 2: 实现 Registry 配置读取

在 `_populate_config_from_dict` 中添加：
```python
# Load registry config
if 'registry' in data:
    registry_data = data['registry']
    # 存储到 OrchestratorConfig 中，供 ConfigLoader 使用
    config.global_settings['registry'] = registry_data
```

在 `ConfigLoader.__init__` 中使用：
```python
# 从配置中读取 registry 设置
registry_config = self.config.global_settings.get('registry', {})
registry_enabled = registry_config.get('enabled', True)
registry_dir = Path(registry_config.get('directory', '~/.memex/orchestrator/registry')).expanduser()
registry_ttl = registry_config.get('ttl', 3600)
```

### 优先级 3: 实现 Auto-discovery 子配置

添加 `scan_user` 和 `scan_project` 配置的读取和使用逻辑。

### 优先级 4: 文档更新

在模板顶部添加"配置状态"说明，标注哪些配置已实现、哪些为预留。

## 总结

- ✅ 核心配置（global, skills, commands, agents, prompts, parallel, slash_commands）已完整实现
- ⚠️ 4个配置节（logging, cache, security, registry）在模板中定义但未实现
- ⚠️ Auto-discovery 子配置在模板中定义但未使用
- 🔧 部分配置硬编码在代码中，无法通过配置文件修改

**建议**: 清理模板，删除未实现的配置节，或实现 registry 配置读取以支持用户自定义。
