# ResourceScanner V2 迁移指南

## 概述

MasterOrchestrator 现已默认使用 **ResourceScannerV2** 作为资源扫描引擎。

V2 版本提供了增强的功能，同时保持向后兼容的 API。

## 更新日期

2025-01-05

## 主要变更

### 1. 默认扫描器更换

**之前**: ResourceScanner (V1)
**现在**: ResourceScannerV2 (默认)

```python
# 自动使用 V2
from core import ResourceScanner  # 现在指向 V2

# 显式使用 V1（向后兼容）
from core import ResourceScannerV1
```

### 2. 文件结构变更

#### Skills

**V1 格式** (已废弃):
```
skills/
└── skill-name/
    └── SKILL.yaml     # YAML 配置文件
```

**V2 格式** (推荐):
```
skills/
└── skill-name/
    ├── SKILL.md       # Markdown 标记文件（包含元数据）
    ├── __init__.py    # Python 入口点（可选）
    └── main.py        # 主模块（可选）
```

**SKILL.md 示例**:
```markdown
# skill-name

description: Skill description here
enabled: true
priority: 50
version: 1.0

## Additional Documentation

More details about the skill...
```

#### Commands (支持分类)

**V2 格式**:
```
commands/
├── category-1/
│   ├── command-1.md
│   └── command-2.md
└── category-2/
    └── command-3.md
```

**command.md 示例**:
```markdown
# command-name

description: Command description
command: echo "hello"
enabled: true
```

#### Agents (支持分类)

类似于 Commands 的分类结构。

#### Prompts (混合布局)

支持扁平和分类两种布局：
```
prompts/
├── prompt-1.md           # 扁平布局
├── prompt-2.md
└── category/
    └── prompt-3.md       # 分类布局
```

## 新增功能

### 1. 分类支持

V2 自动识别目录层次结构中的分类：

```python
from core import ResourceScanner, ResourceCategory

scanner = ResourceScanner()
resources = scanner.scan_all(Path("/path/to/resources"), source="user")

# 资源现在包含 category 属性
for resource in resources[ResourceType.COMMAND]:
    print(f"{resource.name} - Category: {resource.category}")
```

### 2. 布局模式

V2 支持三种布局模式：

```python
from core import ResourceLayout

# FLAT_FILE - 扁平文件结构
# CATEGORIZED_FILE - 分类文件结构
# DIRECTORY_BASED - 基于目录的结构
```

### 3. 增强的元数据提取

- 从 Markdown 文件提取 frontmatter
- 支持多行描述
- 更好的错误处理

## API 变更

### 兼容性

V2 **完全向后兼容** V1 的公共 API：

```python
# 以下代码在 V1 和 V2 中均可工作
scanner = ResourceScanner()
discovered = scanner.scan_all(base_path, source="user")
config = scanner.convert_to_config(discovered_item)
```

### 新增 API

```python
# 分类树视图
tree = scanner.scan_as_tree(base_path, ResourceType.COMMAND, "user")
# 返回: {category_name: [resources]}

# 资源布局信息
resource.layout  # ResourceLayout 枚举
resource.category  # 分类名称（如果有）
resource.relative_path  # 相对于资源根目录的路径
```

## 迁移步骤

### 对于现有项目

1. **更新 Skill 文件格式**（推荐但非必需）

   将 `SKILL.yaml` 重命名为 `SKILL.md`，并调整格式：

   **之前** (SKILL.yaml):
   ```yaml
   name: my-skill
   version: "1.0"
   description: My skill
   enabled: true
   priority: 50
   ```

   **之后** (SKILL.md):
   ```markdown
   # my-skill

   description: My skill
   enabled: true
   priority: 50
   version: 1.0
   ```

2. **清除缓存**（如果使用缓存功能）

   ```python
   # 使用内置命令
   /clear-cache

   # 或者 Python API
   from core import RegistryPersistence
   from pathlib import Path

   registry_dir = Path.home() / ".memex" / "orchestrator" / "registry"
   persistence = RegistryPersistence(registry_dir=registry_dir)
   persistence.invalidate()
   ```

3. **测试资源发现**

   ```python
   from core import ConfigLoader

   loader = ConfigLoader(enable_auto_discovery=True)
   config = loader.load()

   print(f"发现的 Skills: {len(config.skills)}")
   print(f"发现的 Commands: {len(config.commands)}")
   ```

### 对于新项目

直接使用 V2 格式创建资源文件：

```bash
# Skill 结构
mkdir -p skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
# my-skill

description: My new skill
enabled: true
priority: 50
EOF

# Command 结构（带分类）
mkdir -p commands/utilities
cat > commands/utilities/my-command.md << 'EOF'
# my-command

description: My utility command
command: echo "Hello"
enabled: true
EOF
```

## 性能优化

### 缓存增强

RegistryPersistence 现在完全支持 V2 的数据结构：

- **枚举序列化**: ResourceType 和 ResourceLayout 自动转换
- **Path 对象**: 自动序列化为字符串
- **嵌套对象**: 递归序列化支持

### 扫描性能

V2 包含性能优化：

- 智能深度控制（避免过深递归）
- 文件类型过滤（减少无关文件读取）
- 增量缓存支持（只重扫描变更的文件）

## 向后兼容

### V1 API 保留

如果需要继续使用 V1：

```python
# 显式导入 V1
from core import ResourceScannerV1, DiscoveredResourceV1

scanner = ResourceScannerV1()
```

### 自动迁移

ConfigLoader 会自动处理：

- 从缓存加载时的类型转换
- V1 和 V2 资源格式的混合使用
- 无缝的配置对象转换

## 常见问题

### Q: 我的现有 SKILL.yaml 文件还能用吗？

A: 目前 V2 主要支持 SKILL.md 格式。建议迁移到 Markdown 格式以获得更好的支持。

### Q: 分类功能是必需的吗？

A: 否。扁平结构仍然支持。分类是可选的组织方式。

### Q: 如何知道我正在使用哪个版本？

A: 检查日志输出：
```
Auto-discovery enabled via ResourceScannerV2  # V2
Auto-discovery enabled via ResourceScanner    # V1 (旧版本)
```

或者编程检查：
```python
from core import ResourceScanner
print(ResourceScanner.__module__)
# 输出: core.resource_scanner_v2 (V2)
# 输出: core.resource_scanner (V1)
```

### Q: V2 会破坏我的现有配置吗？

A: 不会。V2 保持向后兼容的 API，ConfigLoader 会处理格式差异。

### Q: 缓存会自动更新吗？

A: 是的。文件哈希检测会自动识别格式变更并重新扫描。

## 测试

验证迁移成功：

```bash
# 运行 V2 集成测试
python tests/test_resource_scanner_v2_integration.py

# 运行缓存集成测试
python tests/test_registry_persistence_integration.py

# 运行完整测试套件
python -m pytest tests/
```

## 相关文件

### 核心文件
- `core/resource_scanner_v2.py` - V2 实现
- `core/resource_scanner.py` - V1 实现（保留用于兼容）
- `core/config_loader.py` - 使用 V2 的配置加载器

### 测试文件
- `tests/test_resource_scanner_v2.py` - V2 单元测试
- `tests/test_resource_scanner_v2_integration.py` - V2 集成测试
- `tests/test_registry_persistence_integration.py` - 缓存集成测试

### 文档
- `docs/RESOURCE_SCANNER_V2_MIGRATION.md` - 本文档
- `core/__init__.py` - 导出配置

## 反馈和支持

如遇到问题，请：

1. 检查日志输出查看详细错误信息
2. 运行 `/clear-cache` 清除可能损坏的缓存
3. 验证资源文件格式是否正确
4. 查看测试文件了解正确用法

## 总结

ResourceScannerV2 提供了更强大和灵活的资源发现能力，同时保持了完全的向后兼容性。迁移到 V2 是可选的，但推荐使用以获得最佳体验。
