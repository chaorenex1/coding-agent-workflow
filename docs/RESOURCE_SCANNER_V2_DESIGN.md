# Resource Scanner V2 设计文档

## 设计目标

重新设计资源扫描器以支持项目当前的**分类目录层次**结构，同时保持向后兼容性。

## 当前项目目录结构

### 实际目录层次

```
项目根目录/
├── commands/                   # 命令资源（2层结构）
│   ├── project-analyzer/       # 分类目录
│   │   ├── code-reader.md      # 命令定义文件
│   │   ├── code-review.md
│   │   └── ...
│   ├── quick-code/             # 分类目录
│   │   ├── quick-refactor.md
│   │   ├── quick-rename.md
│   │   └── ...
│   ├── scaffold/               # 分类目录
│   │   └── project-scaffold.md
│   └── prd-workflow/           # 分类目录
│       └── dev-workflow.md
│
├── agents/                     # Agent资源（2层结构）
│   ├── prd-workflow/           # 分类目录
│   │   ├── requirement-analysis-agent.md
│   │   ├── design-architecture-agent.md
│   │   └── ...
│   ├── quick-code/             # 分类目录
│   │   ├── refactor-analyzer.md
│   │   └── ...
│   ├── feature-workflow/       # 分类目录
│   │   └── ...
│   └── automation/             # 分类目录
│       └── ...
│
├── prompts/                    # Prompt资源（扁平结构）
│   ├── repo_scan_report.md
│   ├── tauri-ai-app.md
│   └── ...
│
└── skills/                     # Skill资源（2层结构，目录作为资源）
    ├── codex-cli-bridge/       # Skill目录（包含SKILL.md + Python代码）
    │   ├── SKILL.md
    │   ├── bridge.py
    │   └── ...
    ├── tech-stack-evaluator/   # Skill目录
    │   ├── SKILL.md
    │   ├── ecosystem_analyzer.py
    │   └── ...
    └── ...
```

### 关键观察

1. **Commands/Agents**: 2层结构
   - 第1层：分类目录（category）
   - 第2层：资源文件（.md）
   - 文件即资源，不需要额外目录

2. **Skills**: 2层结构（不同语义）
   - 第1层：Skill目录（资源本身）
   - 第2层：实现文件（SKILL.md + Python模块）
   - 目录即资源，包含marker文件和代码

3. **Prompts**: 扁平结构
   - 单层：资源文件（.md）
   - 可选支持分类目录

## 核心问题

当前`resource_scanner.py`的局限：

1. **只扫描1层目录**：`scan_directory()`只遍历直接子项，不支持递归
2. **无分类概念**：没有category/group的概念
3. **资源识别混乱**：
   - 对Commands/Agents：应该识别`.md`文件为资源
   - 对Skills：应该识别包含SKILL.md的目录为资源
   - 当前逻辑无法区分这两种模式

## 设计方案

### 架构原则

1. **约定优于配置**：通过目录结构自动推断分类和资源类型
2. **统一资源模型**：用`DiscoveredResource`表示所有资源
3. **灵活扫描策略**：每种资源类型定义自己的扫描规则
4. **向后兼容**：保持现有API不变

### 新增概念

#### 1. Resource Layout（资源布局模式）

定义资源在文件系统中的组织方式：

```python
class ResourceLayout(Enum):
    """资源布局模式"""
    FLAT_FILE = "flat_file"           # 扁平文件：resource.md
    CATEGORIZED_FILE = "categorized_file"  # 分类文件：category/resource.md
    DIRECTORY_BASED = "directory_based"    # 目录资源：resource-name/MARKER.md + code
```

**布局规则**：
- **Commands**: `CATEGORIZED_FILE`（commands/category/command.md）
- **Agents**: `CATEGORIZED_FILE`（agents/category/agent.md）
- **Prompts**: `FLAT_FILE` 或 `CATEGORIZED_FILE`（两种都支持）
- **Skills**: `DIRECTORY_BASED`（skills/skill-name/SKILL.md）

#### 2. Category（分类）

从目录名提取的分类信息：

```python
@dataclass
class ResourceCategory:
    """资源分类"""
    name: str                    # 分类名（如 "project-analyzer"）
    display_name: str            # 显示名（如 "Project Analyzer"）
    description: str = ""        # 分类描述
    priority: int = 50           # 分类优先级
```

#### 3. 增强的DiscoveredResource

```python
@dataclass
class DiscoveredResource:
    # ... 现有字段 ...

    # 新增字段
    category: Optional[str] = None        # 分类名称
    layout: ResourceLayout = None         # 布局模式
    relative_path: Path = None            # 相对于资源根的路径
```

### 扫描策略重构

#### 策略1：分层扫描（Hierarchical Scanning）

```python
def scan_directory(self, directory: Path, max_depth: int = 2) -> List[DiscoveredResource]:
    """
    分层扫描目录。

    Args:
        directory: 扫描起点
        max_depth: 最大扫描深度
            - 1: 只扫描当前目录（扁平）
            - 2: 扫描当前+1层子目录（分类）
            - 3+: 递归扫描

    Returns:
        发现的资源列表
    """
    return self._scan_recursive(directory, depth=0, max_depth=max_depth)

def _scan_recursive(
    self,
    directory: Path,
    depth: int,
    max_depth: int,
    category: Optional[str] = None
) -> List[DiscoveredResource]:
    """递归扫描实现"""
    # 具体实现见下文
```

#### 策略2：资源类型专用扫描

**CommandDetector/AgentDetector（分类文件模式）**：

```python
class CommandDetector(BaseResourceDetector):
    LAYOUT = ResourceLayout.CATEGORIZED_FILE
    MAX_DEPTH = 2  # 扫描2层：category/ + resource.md

    def _scan_recursive(self, directory, depth, max_depth, category=None):
        discovered = []

        for item in directory.iterdir():
            if item.name.startswith('.'):
                continue

            if depth == 0:
                # 第1层：分类目录
                if item.is_dir():
                    category_name = item.name
                    # 递归扫描分类目录
                    discovered.extend(
                        self._scan_recursive(item, depth+1, max_depth, category_name)
                    )
                elif item.suffix == '.md':
                    # 也支持扁平文件（无分类）
                    resource = self._detect_from_file(item, category=None)
                    if resource:
                        discovered.append(resource)

            elif depth == 1:
                # 第2层：资源文件
                if item.is_file() and item.suffix == '.md':
                    resource = self._detect_from_file(item, category=category)
                    if resource:
                        discovered.append(resource)

        return discovered

    def _detect_from_file(self, file_path: Path, category: Optional[str]) -> Optional[DiscoveredResource]:
        """从.md文件检测资源"""
        # 解析文件内容
        metadata = self._parse_markdown_metadata(file_path)

        # 资源名：从文件名推断（去除.md后缀）
        resource_name = file_path.stem

        return DiscoveredResource(
            name=resource_name,
            resource_type=self.get_resource_type(),
            path=file_path,
            source=self.source,
            category=category,
            layout=ResourceLayout.CATEGORIZED_FILE,
            discovery_method="markdown_file",
            description=metadata.get('description', ''),
            config_data=metadata
        )
```

**SkillDetector（目录资源模式）**：

```python
class SkillDetector(BaseResourceDetector):
    LAYOUT = ResourceLayout.DIRECTORY_BASED
    MAX_DEPTH = 1  # 只扫描1层：skill-name/
    MARKER_FILE = "SKILL.md"

    def _scan_recursive(self, directory, depth, max_depth, category=None):
        discovered = []

        for item in directory.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_dir():
                # 检查是否为Skill目录（包含SKILL.md）
                marker = item / self.MARKER_FILE
                if marker.exists():
                    resource = self._detect_from_directory(item, category=None)
                    if resource:
                        discovered.append(resource)

        return discovered

    def _detect_from_directory(self, skill_dir: Path, category: Optional[str]) -> Optional[DiscoveredResource]:
        """从Skill目录检测资源"""
        marker_file = skill_dir / self.MARKER_FILE

        # 解析SKILL.md
        metadata = self._parse_markdown_metadata(marker_file)

        # 查找entry point
        entry_point = self._find_entry_point(skill_dir)

        return DiscoveredResource(
            name=skill_dir.name,
            resource_type=ResourceType.SKILL,
            path=skill_dir,
            source=self.source,
            category=category,
            layout=ResourceLayout.DIRECTORY_BASED,
            discovery_method="directory_convention",
            marker_file=marker_file,
            entry_point=entry_point,
            description=metadata.get('description', ''),
            config_data=metadata
        )
```

**PromptDetector（混合模式）**：

```python
class PromptDetector(BaseResourceDetector):
    MAX_DEPTH = 2  # 支持扁平和分类两种

    def _scan_recursive(self, directory, depth, max_depth, category=None):
        discovered = []

        for item in directory.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_file() and item.suffix == '.md':
                # 扁平文件：prompts/prompt.md
                resource = self._detect_from_file(item, category=category)
                if resource:
                    discovered.append(resource)

            elif item.is_dir() and depth < max_depth:
                # 分类目录：prompts/category/prompt.md
                category_name = item.name
                discovered.extend(
                    self._scan_recursive(item, depth+1, max_depth, category_name)
                )

        return discovered
```

### 分类元数据提取

支持从分类目录中提取元数据（可选）：

```
commands/
  project-analyzer/
    _category.yaml          # 可选：分类元数据
    code-reader.md
    code-review.md
```

`_category.yaml`格式：

```yaml
name: project-analyzer
display_name: Project Analyzer
description: Tools for analyzing project structure and code
priority: 80
```

如果没有`_category.yaml`，则从目录名推断：
- `project-analyzer` → display: "Project Analyzer"
- `quick-code` → display: "Quick Code"

### API变更

#### 新增方法

```python
class ResourceScanner:
    def get_categories(self, resource_type: ResourceType) -> List[ResourceCategory]:
        """获取某资源类型的所有分类"""

    def scan_category(
        self,
        resource_type: ResourceType,
        category: str
    ) -> List[DiscoveredResource]:
        """扫描特定分类下的资源"""

    def get_resource_tree(
        self,
        resource_type: ResourceType
    ) -> Dict[str, List[DiscoveredResource]]:
        """
        获取资源树（按分类组织）

        Returns:
            {
                "project-analyzer": [resource1, resource2, ...],
                "quick-code": [...],
                None: [uncategorized_resources]  # 无分类的资源
            }
        """
```

#### 向后兼容

保持现有方法签名：

```python
# 现有方法保持不变
def scan_all(self, base_path: Path, source: str = "project") -> Dict[ResourceType, List[DiscoveredResource]]:
    """扫描所有资源（现在包含分类信息）"""

def scan_type(self, base_path: Path, resource_type: ResourceType, source: str = "project") -> List[DiscoveredResource]:
    """扫描特定类型资源（现在包含分类信息）"""
```

返回的`DiscoveredResource`对象增加了`category`字段，但不影响现有代码。

## 实现计划

### Phase 1: 核心重构
- [ ] 添加`ResourceLayout`枚举
- [ ] 添加`ResourceCategory`数据类
- [ ] 更新`DiscoveredResource`增加category字段
- [ ] 重构`BaseResourceDetector`支持递归扫描

### Phase 2: 专用Detector实现
- [ ] 重写`CommandDetector`支持分类文件
- [ ] 重写`AgentDetector`支持分类文件
- [ ] 更新`SkillDetector`明确目录模式
- [ ] 更新`PromptDetector`支持混合模式

### Phase 3: 新增功能
- [ ] 实现`get_categories()`
- [ ] 实现`scan_category()`
- [ ] 实现`get_resource_tree()`
- [ ] 支持`_category.yaml`元数据

### Phase 4: 测试和文档
- [ ] 单元测试：各Detector的扫描逻辑
- [ ] 集成测试：完整扫描流程
- [ ] 性能测试：大量资源的扫描效率
- [ ] 更新文档和示例

## 使用示例

### 扫描所有资源（含分类）

```python
scanner = ResourceScanner()
results = scanner.scan_all(Path("C:/Users/zarag/Documents/coding_base"))

# 输出：
# {
#   ResourceType.COMMAND: [
#     DiscoveredResource(name="code-reader", category="project-analyzer", ...),
#     DiscoveredResource(name="code-review", category="project-analyzer", ...),
#     DiscoveredResource(name="quick-refactor", category="quick-code", ...),
#   ],
#   ResourceType.AGENT: [
#     DiscoveredResource(name="requirement-analysis-agent", category="prd-workflow", ...),
#     ...
#   ],
#   ...
# }
```

### 获取分类树

```python
tree = scanner.get_resource_tree(ResourceType.COMMAND)

# 输出：
# {
#   "project-analyzer": [code-reader, code-review, ...],
#   "quick-code": [quick-refactor, quick-rename, ...],
#   "scaffold": [project-scaffold, ...],
# }
```

### 扫描特定分类

```python
resources = scanner.scan_category(ResourceType.AGENT, "prd-workflow")

# 输出：
# [
#   requirement-analysis-agent,
#   design-architecture-agent,
#   implementation-agent,
#   ...
# ]
```

## 兼容性保证

### 现有代码无需修改

```python
# 旧代码仍然可以工作
scanner = ResourceScanner()
results = scanner.scan_all(base_path)
commands = results[ResourceType.COMMAND]

# 新代码可以访问category
for cmd in commands:
    print(f"{cmd.name} (category: {cmd.category})")
```

### 渐进式迁移

1. 先部署新扫描器（向后兼容）
2. 更新依赖代码使用category信息
3. 添加UI展示分类
4. 逐步增强分类功能

## 性能考虑

### 缓存策略

```python
class ResourceScanner:
    def __init__(self):
        self._cache = {}  # {(base_path, resource_type): results}
        self._cache_timestamp = {}

    def scan_type(self, base_path, resource_type, use_cache=True):
        cache_key = (str(base_path), resource_type)

        if use_cache and cache_key in self._cache:
            # 检查缓存是否过期（如文件修改时间）
            if not self._is_cache_stale(base_path):
                return self._cache[cache_key]

        # 执行扫描
        results = self._do_scan(base_path, resource_type)

        # 更新缓存
        self._cache[cache_key] = results
        self._cache_timestamp[cache_key] = time.time()

        return results
```

### 并行扫描

对于大型项目，支持并行扫描不同资源类型：

```python
from concurrent.futures import ThreadPoolExecutor

def scan_all_parallel(self, base_path: Path, source: str = "project"):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            ResourceType.COMMAND: executor.submit(self.scan_type, base_path, ResourceType.COMMAND, source),
            ResourceType.AGENT: executor.submit(self.scan_type, base_path, ResourceType.AGENT, source),
            ResourceType.PROMPT: executor.submit(self.scan_type, base_path, ResourceType.PROMPT, source),
            ResourceType.SKILL: executor.submit(self.scan_type, base_path, ResourceType.SKILL, source),
        }

        results = {rt: future.result() for rt, future in futures.items()}
        return results
```

## 错误处理

### 容错机制

```python
def _scan_recursive(self, directory, depth, max_depth, category=None):
    discovered = []
    errors = []

    try:
        for item in directory.iterdir():
            try:
                # 扫描单个项目
                resource = self._scan_item(item, depth, max_depth, category)
                if resource:
                    discovered.append(resource)
            except Exception as e:
                # 记录错误但继续扫描
                logger.warning(f"Failed to scan {item}: {e}")
                errors.append((item, str(e)))
    except PermissionError as e:
        logger.error(f"Permission denied accessing {directory}: {e}")

    # 可选：在结果中附加错误信息
    if errors and self.include_errors:
        for resource in discovered:
            resource.metadata['scan_errors'] = errors

    return discovered
```

## 测试用例

### 测试目录结构

```
test_resources/
  commands/
    category1/
      cmd1.md
      cmd2.md
    category2/
      cmd3.md
    flat_cmd.md          # 测试无分类命令
  agents/
    group1/
      agent1.md
  skills/
    skill-a/
      SKILL.md
      main.py
    skill-b/
      SKILL.md
  prompts/
    prompt1.md           # 扁平
    category/
      prompt2.md         # 分类
```

### 核心测试

```python
def test_categorized_commands():
    scanner = ResourceScanner()
    results = scanner.scan_type(test_base, ResourceType.COMMAND)

    # 验证分类
    assert any(r.name == "cmd1" and r.category == "category1" for r in results)
    assert any(r.name == "cmd2" and r.category == "category1" for r in results)
    assert any(r.name == "flat_cmd" and r.category is None for r in results)

def test_skill_directory_structure():
    scanner = ResourceScanner()
    results = scanner.scan_type(test_base, ResourceType.SKILL)

    # 验证目录模式
    skill_a = next(r for r in results if r.name == "skill-a")
    assert skill_a.layout == ResourceLayout.DIRECTORY_BASED
    assert skill_a.marker_file.name == "SKILL.md"
    assert skill_a.entry_point.name == "main.py"

def test_resource_tree():
    scanner = ResourceScanner()
    tree = scanner.get_resource_tree(ResourceType.COMMAND)

    assert "category1" in tree
    assert len(tree["category1"]) == 2  # cmd1, cmd2
    assert None in tree  # uncategorized
    assert len(tree[None]) == 1  # flat_cmd
```

## 总结

### 关键改进

1. **支持分类层次**：Commands/Agents按分类组织
2. **灵活布局模式**：不同资源类型不同扫描策略
3. **向后兼容**：现有代码无需修改
4. **性能优化**：缓存、并行、容错
5. **可扩展性**：易于添加新资源类型

### 与现有系统集成

- **ConfigLoader**: 消费`DiscoveredResource`时读取category字段
- **UnifiedRegistry**: 按category组织资源注册
- **CLI/UI**: 展示分类树状结构
- **Dependency Analyzer**: 支持category级别的依赖分析

### 下一步

1. 实现核心重构（Phase 1-2）
2. 添加测试覆盖（Phase 4）
3. 更新UnifiedRegistry集成分类
4. 文档和示例更新
