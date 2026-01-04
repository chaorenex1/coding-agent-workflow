# MasterOrchestrator V3 - 自动注册发现系统

## 概述

MasterOrchestrator V3 引入了强大的自动注册发现系统，允许从项目级、用户级和内置三个层级自动加载和管理 skill、command、agent 和 prompt 资源。

**核心特性**：
- 🔍 **三层配置加载**：项目级 > 用户级 > 内置
- 🏷️ **命名空间隔离**：`type:name` 格式（如 `skill:code-review`）
- ⚖️ **优先级覆盖**：高优先级资源自动覆盖低优先级
- 🔗 **依赖管理**：自动解析和验证资源依赖关系
- 🔄 **热重载**：支持运行时重新加载配置

---

## 快速开始

### 1. 启用自动发现

```python
from orchestrator import MasterOrchestrator

# 启用自动发现
orch = MasterOrchestrator(
    auto_discover=True,           # 启用自动发现
    config_path=None,             # 使用当前目录（可选）
)

# 列出所有已注册资源
resources = orch.list_resources()
for resource in resources:
    print(f"{resource.namespace} (来源: {resource.source}, 优先级: {resource.priority})")
```

**输出示例**：
```
skill:intent-analyzer (来源: builtin, 优先级: 10)
skill:command-parser (来源: builtin, 优先级: 10)
skill:agent-router (来源: builtin, 优先级: 10)
skill:custom-review (来源: project, 优先级: 100)
command:git (来源: builtin, 优先级: 10)
command:npm (来源: project, 优先级: 50)
```

### 2. 创建配置文件

在项目根目录创建 `orchestrator.yaml`：

```yaml
version: "3.0"

global:
  default_backend: claude
  timeout: 300
  enable_parallel: false
  max_parallel_tasks: 3

skills:
  manual:
    - name: custom-review
      path: ./skills/custom-review.yaml
      enabled: true
      priority: 100  # 高优先级
      dependencies: ["command:git-diff"]

commands:
  whitelist:
    - git
    - npm
    - python
    - pytest

prompts:
  - name: api-doc
    template: "生成 {language} API 文档：\n\n{code}"
    variables: [language, code]
    enabled: true
    priority: 50
```

---

## 配置文件层次

### 三层配置系统

```
优先级 (高 → 低)
    ↓
1. 项目级配置
   - ./orchestrator.yaml
   - ./skills/*.yaml

2. 用户级配置
   - ~/.claude/orchestrator.yaml
   - ~/.claude/skills/*.yaml

3. 内置配置
   - 硬编码默认值
   - skills/memex-cli/skills/*.yaml
```

### 配置文件位置

| 层级 | 主配置文件 | Skills 目录 | 优先级 |
|------|-----------|------------|--------|
| 项目级 | `./orchestrator.yaml` | `./skills/` | 高 (100) |
| 用户级 | `~/.claude/orchestrator.yaml` | `~/.claude/skills/` | 中 (50) |
| 内置 | 硬编码 | `skills/memex-cli/skills/` | 低 (10) |

### 优先级规则

**同名资源覆盖规则**：
1. 优先级高的覆盖优先级低的
2. 同优先级时，后加载的覆盖先加载的
3. 项目级 > 用户级 > 内置

**示例**：
```yaml
# 内置: skill:code-review (priority=10)
# 用户级: skill:code-review (priority=50) ← 覆盖内置
# 项目级: skill:code-review (priority=100) ← 覆盖用户级
```

---

## 配置文件格式

### 完整配置示例

```yaml
version: "3.0"

# 全局设置
global:
  default_backend: claude
  timeout: 300
  enable_parallel: false
  max_parallel_tasks: 3

# Skills 配置
skills:
  # 自动扫描路径（可选）
  scan_paths:
    - ./skills/*.yaml
    - ~/.claude/skills/*.yaml

  # 手动声明（优先级更高）
  manual:
    - name: code-review
      type: yaml
      path: ./skills/code-review.yaml
      enabled: true
      priority: 100
      backend: claude
      dependencies: ["command:git-diff"]

    - name: test-generator
      type: python
      path: ./skills/test_generator.py
      enabled: true
      priority: 90

# Commands 配置
commands:
  # 白名单（允许执行的命令）
  whitelist:
    - git
    - npm
    - python
    - pytest
    - docker

  # 命令别名
  aliases:
    - name: gst
      command: git status

    - name: glog
      command: git log --oneline -10

    - name: gco
      command: git checkout

# Agents 配置
agents:
  - name: security-auditor
    type: general
    enabled: true
    priority: 50
    dependencies: []

# Prompts 配置
prompts:
  - name: api-doc
    template: |
      生成 {language} API 文档：

      代码：
      {code}

      请包含：参数、返回值、异常、示例
    variables: [language, code]
    enabled: true
    priority: 50

  - name: code-review
    template: |
      请对以下代码进行审查：

      {code}

      关注点：{focus}
    variables: [code, focus]
    enabled: true
    priority: 60

# 并行执行配置
parallel:
  enabled: false
  max_workers: 3
  timeout_per_task: 120
  allowed_modes: [command, backend]
  sequential_modes: [skill]
```

---

## Skills 定义

### YAML Skill 格式

在 `./skills/my-skill.yaml` 创建：

```yaml
name: my-skill
version: 1.0.0
description: 我的自定义技能

# 执行配置
backend: claude
model: claude-3-5-sonnet-20241022
temperature: 0.7
max_tokens: 4000

# 提示词模板
system_prompt: |
  你是一位专业的 {role} 专家。
  请按照以下要求执行任务。

user_prompt_template: |
  任务：{task}

  要求：
  {requirements}

  请提供详细的输出。

# 示例
examples:
  - name: 示例1
    input:
      role: "Python开发者"
      task: "重构代码"
      requirements: "提高可读性"
    output: |
      重构建议...

# 依赖
dependencies: ["command:git-diff"]

# 元数据
enabled: true
priority: 100
```

### Python Skill 格式

```python
# ./skills/my_skill.py
from orchestrator.executors.memex_executor_base import MemexExecutorBase

class MySkill(MemexExecutorBase):
    """自定义 Python Skill"""

    def __init__(self, backend_orch, **kwargs):
        super().__init__(backend_orch, default_backend="claude")

    def execute(self, request: str, **kwargs):
        """执行 Skill"""
        # 实现逻辑
        result = self.execute_via_memex(
            prompt=f"执行任务: {request}",
            backend="claude"
        )
        return result.output
```

---

## 资源管理

### 列出资源

```python
# 列出所有资源
all_resources = orch.list_resources()

# 按类型过滤
skills = orch.list_resources(type_filter="skill")
commands = orch.list_resources(type_filter="command")

# 按来源过滤
project_resources = orch.list_resources(source_filter="project")
user_resources = orch.list_resources(source_filter="user")

# 组合过滤
project_skills = orch.list_resources(
    type_filter="skill",
    source_filter="project"
)

# 打印资源信息
for resource in skills:
    print(f"名称: {resource.name}")
    print(f"  命名空间: {resource.namespace}")
    print(f"  来源: {resource.source}")
    print(f"  优先级: {resource.priority}")
    print(f"  依赖: {resource.dependencies}")
    print(f"  路径: {resource.path}")
    print()
```

### 重新加载配置

```python
# 修改 orchestrator.yaml 后
orch.reload_config(verbose=True)

# 输出：
# [配置重载成功] 加载了 15 个资源
```

---

## 命名空间系统

### 命名空间格式

所有资源使用统一的命名空间格式：`{type}:{name}`

**示例**：
```
skill:code-review
skill:test-generator
command:git
command:npm
agent:explore
agent:plan
prompt:api-doc
prompt:code-review
```

### 命名空间的优势

1. **避免冲突**：不同类型的资源可以同名
   ```
   skill:review    ← Skill
   prompt:review   ← Prompt（不冲突）
   ```

2. **清晰的引用**：
   ```yaml
   dependencies:
     - "skill:code-analyzer"   # 明确引用 Skill
     - "command:git-diff"      # 明确引用 Command
   ```

3. **便于管理**：
   ```python
   # 按类型查询
   skills = registry.list_resources(type_filter=ResourceType.SKILL)
   ```

---

## 依赖管理

### 声明依赖

在 `orchestrator.yaml` 中声明依赖：

```yaml
skills:
  manual:
    - name: code-review
      path: ./skills/code-review.yaml
      dependencies:
        - "command:git-diff"      # 依赖 git-diff 命令
        - "skill:code-analyzer"   # 依赖另一个 Skill
```

### 依赖解析

系统会自动：
1. **验证依赖**：检查所有依赖是否存在
2. **循环检测**：检测并报告循环依赖
3. **拓扑排序**：按依赖顺序执行

**示例**：
```python
# 获取资源的完整依赖链
dependencies = orch.registry.resolve_dependencies("skill:code-review")
# 返回: ["command:git-diff", "skill:code-analyzer", "skill:code-review"]
```

### 循环依赖检测

系统会在启动时自动检测：

```
[错误] 检测到 1 个循环依赖:
  - skill:A → skill:B → skill:C → skill:A
```

**解决方案**：重构依赖关系，打破循环。

---

## 高级用法

### 动态创建资源

```python
from orchestrator.core.unified_registry import ResourceMetadata, ResourceType

# 动态注册 Skill
metadata = ResourceMetadata(
    name="dynamic-skill",
    namespace="skill:dynamic-skill",
    type=ResourceType.SKILL,
    source="runtime",
    priority=200,  # 最高优先级
    dependencies=[],
    config={
        "type": "yaml",
        "backend": "claude"
    },
    path=Path("./skills/dynamic-skill.yaml"),
    enabled=True
)

orch.registry.register(metadata)
```

### 自定义优先级策略

```python
# 项目特定的高优先级 Skill
skills:
  manual:
    - name: critical-skill
      priority: 1000  # 超高优先级，确保不被覆盖
```

### 条件启用资源

```yaml
skills:
  manual:
    - name: experimental-skill
      enabled: false  # 禁用实验性 Skill
      priority: 50
```

---

## 配置验证

### 自动验证

系统会在加载时自动验证：

```python
loader = ConfigLoader()
config = loader.load()

# 验证输出
[警告] 配置验证发现 2 个问题:
  - Skill 'code-review' 路径不存在: ./skills/code-review.yaml
  - Skill 'test-gen' 依赖未知资源: 'command:unknown-cmd'
```

### 验证规则

- ✅ 配置版本兼容性（3.x）
- ✅ Skill 路径存在性
- ✅ 依赖资源存在性
- ✅ 并行配置合法性（max_workers >= 1）
- ✅ 超时配置合法性（timeout >= 1）

---

## 最佳实践

### 1. 项目配置策略

**推荐结构**：
```
my-project/
├── orchestrator.yaml           # 项目主配置
├── skills/
│   ├── project-skill-1.yaml    # 项目特定 Skills
│   ├── project-skill-2.yaml
│   └── custom_executor.py      # Python Skills
└── docs/
    └── skills/                 # Skill 文档
```

### 2. 用户配置策略

**推荐用途**：
- 个人常用的 Skills
- 个人命令别名
- 个人偏好设置

**位置**：
```
~/.claude/
├── orchestrator.yaml           # 用户全局配置
└── skills/
    ├── personal-skill-1.yaml   # 个人 Skills
    └── personal-skill-2.yaml
```

### 3. 优先级分配建议

| 来源 | 优先级范围 | 用途 |
|------|----------|------|
| 内置 | 1-20 | 系统默认资源 |
| 用户级 | 30-70 | 个人常用资源 |
| 项目级 | 80-200 | 项目特定资源 |
| 运行时 | 200+ | 临时覆盖 |

### 4. 依赖管理建议

- ✅ **最小化依赖**：只声明直接依赖
- ✅ **明确命名空间**：使用完整格式（`type:name`）
- ✅ **避免循环**：设计时考虑依赖方向
- ✅ **文档化依赖**：在 Skill 文档中说明依赖原因

### 5. 配置文件维护

```bash
# 版本控制
git add orchestrator.yaml
git add skills/*.yaml
git commit -m "chore: 更新 Orchestrator 配置"

# 忽略用户配置
echo "orchestrator.local.yaml" >> .gitignore
```

---

## 故障排查

### 问题 1: 资源未加载

**症状**：`list_resources()` 返回空列表

**解决**：
```python
# 检查 auto_discover 是否启用
orch = MasterOrchestrator(auto_discover=True)  # ← 必须启用

# 检查配置文件路径
import os
print(os.path.exists("./orchestrator.yaml"))  # 应返回 True
```

### 问题 2: 配置未生效

**症状**：修改 `orchestrator.yaml` 后没有变化

**解决**：
```python
# 方法1: 重新加载配置
orch.reload_config(verbose=True)

# 方法2: 重新创建实例
orch = MasterOrchestrator(auto_discover=True)
```

### 问题 3: 依赖错误

**症状**：`Resource 'X' depends on unknown resource 'Y'`

**解决**：
```python
# 检查依赖是否存在
all_resources = orch.list_resources()
namespaces = [r.namespace for r in all_resources]
print("可用资源:", namespaces)

# 修正依赖声明
dependencies: ["skill:correct-name"]  # 使用正确的命名空间
```

### 问题 4: 循环依赖

**症状**：`Circular dependency detected: A → B → A`

**解决**：
```yaml
# 重构依赖关系
# 错误：
skill:A → skill:B → skill:A

# 正确：
skill:A → skill:common
skill:B → skill:common
```

---

## API 参考

### MasterOrchestrator

```python
class MasterOrchestrator:
    def __init__(
        self,
        auto_discover: bool = False,      # 启用自动发现
        config_path: Optional[Path] = None,  # 配置文件路径
        # ... 其他参数
    ):
        pass

    def list_resources(
        self,
        type_filter: Optional[str] = None,    # "skill" | "command" | "agent" | "prompt"
        source_filter: Optional[str] = None   # "builtin" | "user" | "project"
    ) -> List[ResourceMetadata]:
        """列出已注册资源"""
        pass

    def reload_config(self, verbose: bool = False):
        """重新加载配置"""
        pass
```

### ConfigLoader

```python
class ConfigLoader:
    def __init__(self, project_root: Optional[Path] = None):
        pass

    def load(self) -> OrchestratorConfig:
        """加载并合并所有配置"""
        pass
```

### UnifiedRegistry

```python
class UnifiedRegistry:
    def register(self, metadata: ResourceMetadata, overwrite: bool = False) -> bool:
        """注册资源"""
        pass

    def get(self, namespace: str) -> Optional[ResourceMetadata]:
        """获取资源"""
        pass

    def resolve_dependencies(self, namespace: str) -> List[str]:
        """解析依赖链"""
        pass

    def check_circular_dependency(self) -> List[List[str]]:
        """检测循环依赖"""
        pass
```

---

## 示例场景

### 场景 1: 团队协作项目

**需求**：团队共享项目配置，每个成员有个人偏好

**解决方案**：
```yaml
# 项目级: orchestrator.yaml (Git 管理)
version: "3.0"
skills:
  manual:
    - name: team-code-review
      path: ./skills/team-code-review.yaml
      priority: 100

# 用户级: ~/.claude/orchestrator.yaml (不纳入 Git)
skills:
  manual:
    - name: personal-helper
      path: ~/.claude/skills/personal-helper.yaml
      priority: 50

# 用户的个人 Skill 不会影响团队配置
```

### 场景 2: 多环境配置

**需求**：开发环境和生产环境使用不同配置

**解决方案**：
```bash
# 开发环境
export ORCHESTRATOR_ENV=dev
# 读取 orchestrator.dev.yaml

# 生产环境
export ORCHESTRATOR_ENV=prod
# 读取 orchestrator.prod.yaml
```

```python
import os
config_file = f"orchestrator.{os.getenv('ORCHESTRATOR_ENV', 'yaml')}"
orch = MasterOrchestrator(
    auto_discover=True,
    config_path=Path(config_file)
)
```

---

## 性能考虑

### 启动时间

- **无自动发现**: ~50ms
- **自动发现 (10个资源)**: ~100ms
- **自动发现 (50个资源)**: ~200ms

### 内存占用

- **基础**: ~30MB
- **自动发现 (50个资源)**: ~50MB
- **缓存执行器**: +5-10MB per executor

### 优化建议

```yaml
# 1. 限制扫描范围
skills:
  scan_paths:
    - ./skills/*.yaml  # 避免深层递归

# 2. 禁用不需要的资源
skills:
  manual:
    - name: unused-skill
      enabled: false  # 不加载到注册表

# 3. 使用手动声明代替自动扫描
skills:
  manual:  # 明确声明，跳过扫描
    - name: skill-1
    - name: skill-2
```

---

## 版本兼容性

| 版本 | 自动发现 | 并行执行 | 向后兼容 |
|------|---------|---------|---------|
| V1.x | ❌ | ❌ | ✅ 100% |
| V2.x | ❌ | ❌ | ✅ 100% |
| V3.0 | ✅ | ✅ | ✅ 100% |

**升级指南**：
```python
# V2.x 代码（继续工作）
orch = MasterOrchestrator()
result = orch.process("请求")

# V3.0 代码（可选启用新功能）
orch = MasterOrchestrator(auto_discover=True)
result = orch.process("请求")
```

---

## 相关文档

- [并行执行文档](./PARALLEL_EXECUTION.md)
- [架构文档](./ARCHITECTURE.md)
- [配置模板](../orchestrator.yaml)

---

**最后更新**: 2026-01-04
**版本**: 3.0.0
