# Slash Commands 用户指南

**版本**: V3.1
**更新日期**: 2026-01-04

---

## 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [内置命令](#内置命令)
4. [自定义命令](#自定义命令)
5. [命令类型](#命令类型)
6. [配置文件](#配置文件)
7. [高级特性](#高级特性)
8. [故障排查](#故障排查)

---

## 概述

Slash Command 是 MasterOrchestrator V3.1 引入的强大特性,提供类似 Claude Code CLI 的命令行交互体验。通过 `/` 前缀,你可以快速执行系统操作、Shell 命令、Skills 和 Agents,无需自然语言描述。

### 为什么使用 Slash Commands?

**优点**:
- ✅ **精准控制**: 明确指定要执行的操作
- ✅ **自动补全**: 明确的命令名称易于记忆和自动补全
- ✅ **可扩展**: 通过配置文件添加自定义命令
- ✅ **向后兼容**: 不影响现有自然语言交互
- ✅ **优先级系统**: 项目级命令可覆盖全局命令

**对比自然语言**:

| 特性 | 自然语言 | Slash Command |
|------|---------|---------------|
| 交互方式 | "帮我查看git状态" | `/git-status` |
| 精准度 | 依赖意图识别 | 100% 精准 |
| 扩展性 | 需要训练模型 | 配置文件即可 |
| 执行速度 | 需要意图分析 | 直接执行 |

---

## 快速开始

### 1. 基本使用

在 Python 代码中直接使用:

```python
from orchestrator import MasterOrchestrator

# 创建 Orchestrator
orch = MasterOrchestrator(auto_discover=True)

# 执行 Slash Command
result = orch.process("/stats")

# 查看结果
print(f"成功: {result.success}")
print(f"输出: {result.output}")
```

### 2. 列出所有可用命令

```python
result = orch.process("/list-commands")

for cmd in result.output:
    print(f"/{cmd['name']}: {cmd['description']}")
```

输出示例:
```
/discover: Auto-discover and register resources
/list-skills: List all registered skills
/list-commands: List all registered slash commands
/reload: Reload configuration
/stats: Show orchestrator statistics
/git-status: Show git status
/git-log: Show git log
/npm-test: Run npm tests
```

### 3. 查看统计信息

```python
result = orch.process("/stats")

print(f"V3 启用: {result.output['v3_enabled']}")
print(f"注册的 Skills: {result.output['registry']['skills']}")
print(f"Slash Commands: {result.output['slash_commands']['total_commands']}")
```

---

## 内置命令

### 系统命令

#### /discover
**描述**: 自动发现并注册资源 (skills, commands, agents)

**用法**:
```python
result = orch.process("/discover")
print(f"发现资源: {result.output['total_resources']} 个")
```

**返回**:
```python
{
    "total_resources": 15,
    "by_type": {
        "skill": 8,
        "command": 5,
        "agent": 2
    }
}
```

---

#### /list-skills
**描述**: 列出所有已注册的 Skills

**用法**:
```python
result = orch.process("/list-skills")

for skill in result.output:
    print(f"- {skill.name} (source: {skill.source})")
```

---

#### /list-commands
**描述**: 列出所有已注册的 Slash Commands

**用法**:
```python
result = orch.process("/list-commands")

for cmd in result.output:
    print(f"/{cmd['name']}")
    print(f"  描述: {cmd['description']}")
    print(f"  类型: {cmd['type']}")
    print(f"  示例: {cmd.get('examples', [])}")
```

---

#### /reload
**描述**: 重新加载配置文件

**用法**:
```python
# 修改 orchestrator.yaml 后重载
result = orch.process("/reload")

print(f"重载成功: {result.output['reloaded']}")
print(f"资源数量: {result.output['resources']}")
```

---

#### /stats
**描述**: 显示 Orchestrator 统计信息

**用法**:
```python
result = orch.process("/stats")

print(f"V3 启用: {result.output['v3_enabled']}")
print(f"Registry 统计: {result.output['registry']}")
print(f"Slash Commands: {result.output['slash_commands']}")
```

---

### Shell 命令

#### /git-status
**描述**: 显示 git 仓库状态

**用法**:
```python
result = orch.process("/git-status")
print(result.output)  # Git status 输出
```

---

#### /git-log
**描述**: 显示 git 提交历史

**用法**:
```python
# 默认显示最近 10 条
result = orch.process("/git-log")

# 显示最近 20 条
result = orch.process("/git-log -20")
```

---

#### /npm-test
**描述**: 运行 npm 测试

**用法**:
```python
result = orch.process("/npm-test")

if result.success:
    print("测试通过!")
else:
    print(f"测试失败: {result.error}")
```

---

## 自定义命令

### 通过配置文件添加

在项目根目录创建 `orchestrator.yaml`:

```yaml
version: "3.1"

slash_commands:
  enabled: true

  # 自定义 Shell 命令
  shell:
    - name: gst
      description: "Git status 简写"
      command: "git status -sb"
      enabled: true
      priority: 60
      examples:
        - "/gst"

    - name: build
      description: "运行项目构建"
      command: "npm run build"
      enabled: true
      priority: 70
      examples:
        - "/build"

    - name: test
      description: "运行所有测试"
      command: "pytest tests/ -v"
      enabled: true
      priority: 70
      examples:
        - "/test"
        - "/test tests/test_specific.py"

  # 自定义 Skill 命令
  skill:
    - name: review
      description: "代码审查当前分支"
      skill: "code-review"
      enabled: true
      priority: 80
      examples:
        - "/review"
        - "/review path/to/file.py"

    - name: gendoc
      description: "生成 API 文档"
      skill: "api-document-generator"
      enabled: true
      priority: 80
      examples:
        - "/gendoc src/"

  # 自定义 Agent 命令
  agent:
    - name: explore
      description: "探索代码库"
      agent_type: "EXPLORE"
      thoroughness: "medium"
      enabled: true
      priority: 75
      examples:
        - "/explore auth system"

    - name: plan
      description: "规划实现方案"
      agent_type: "PLAN"
      enabled: true
      priority: 75
      examples:
        - "/plan add user authentication"
```

### 使用自定义命令

```python
# 启用 V3 自动发现以加载配置
orch = MasterOrchestrator(
    auto_discover=True,
    config_path="."  # 项目根目录
)

# 使用自定义命令
result = orch.process("/gst")
result = orch.process("/build")
result = orch.process("/review src/api.py")
result = orch.process("/explore authentication flow")
```

---

## 命令类型

### 1. SYSTEM (系统命令)

调用 MasterOrchestrator 的内部方法。

**配置示例**:
```yaml
slash_commands:
  system:
    - name: my-stats
      description: "自定义统计信息"
      handler: "_get_stats"  # MasterOrchestrator 中的方法名
      enabled: true
      priority: 80
```

**限制**: handler 必须是 MasterOrchestrator 类中存在的方法。

---

### 2. SHELL (Shell 命令)

执行 Shell 命令。

**配置示例**:
```yaml
slash_commands:
  shell:
    - name: deploy
      description: "部署到生产环境"
      command: "./scripts/deploy.sh production"
      enabled: true
      priority: 90
```

**支持参数**:
```python
# 定义
command: "git log --oneline"

# 使用
result = orch.process("/git-log -20")
# 实际执行: git log --oneline -20
```

**安全提示**: Shell 命令会受到 `CommandExecutor` 的安全检查,危险命令会被拦截。

---

### 3. SKILL (Skill 命令)

调用已注册的 Skill。

**配置示例**:
```yaml
slash_commands:
  skill:
    - name: refactor
      description: "代码重构建议"
      skill: "code-refactoring-assistant"
      enabled: true
      priority: 80
```

**前提**: Skill 必须在 `skills/` 目录或配置中已注册。

---

### 4. AGENT (Agent 命令)

调用特定类型的 Agent。

**配置示例**:
```yaml
slash_commands:
  agent:
    - name: analyze
      description: "深度分析代码"
      agent_type: "GENERAL_PURPOSE"
      enabled: true
      priority: 75
      config:
        model: "claude-3-5-sonnet-20241022"
        temperature: 0.3
```

**Agent 类型**:
- `EXPLORE`: 探索代码库
- `PLAN`: 规划实现方案
- `GENERAL_PURPOSE`: 通用任务

---

### 5. PROMPT (Prompt 模板命令)

使用 Prompt 模板生成内容。

**配置示例**:
```yaml
slash_commands:
  prompt:
    - name: apidoc
      description: "生成 API 文档"
      prompt_template: "api-doc"
      enabled: true
      priority: 60
```

**前提**: Prompt 模板必须在 `PromptManager` 中已注册。

---

## 配置文件

### 配置层级

Orchestrator 支持三层配置,按优先级从高到低:

1. **项目级**: `./orchestrator.yaml` (优先级最高)
2. **用户级**: `~/.claude/orchestrator.yaml`
3. **内置**: 硬编码默认值

### 完整配置示例

参考 `orchestrator.yaml.template` 文件:

```yaml
version: "3.1"

global:
  default_backend: claude
  timeout: 300
  verbose: false
  enable_v3: true

slash_commands:
  enabled: true

  shell:
    - name: custom-cmd
      description: "自定义命令"
      command: "echo 'Hello'"
      enabled: true
      priority: 60

  skill:
    - name: custom-skill
      description: "自定义 Skill"
      skill: "my-skill"
      enabled: true
      priority: 80

  # ... 更多配置
```

### 配置字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 命令名称(不含 `/`) |
| `description` | string | ✅ | 命令描述 |
| `enabled` | boolean | ❌ | 是否启用(默认 true) |
| `priority` | int | ❌ | 优先级 0-1000(默认 50) |
| `command` | string | ⚠️ | Shell 命令(SHELL 类型必需) |
| `skill` | string | ⚠️ | Skill 名称(SKILL 类型必需) |
| `agent_type` | string | ⚠️ | Agent 类型(AGENT 类型必需) |
| `handler` | string | ⚠️ | 方法名(SYSTEM 类型必需) |
| `examples` | list | ❌ | 用法示例 |
| `dependencies` | list | ❌ | 依赖的其他资源 |

---

## 高级特性

### 1. 优先级系统

当多个配置定义同名命令时,高优先级覆盖低优先级:

```yaml
# 内置命令: priority = 100
builtin:
  - name: git-status
    priority: 100

# 项目级覆盖: priority = 120
slash_commands:
  shell:
    - name: git-status
      command: "git status -sb --porcelain"
      priority: 120  # 覆盖内置命令
```

**优先级建议**:
- **内置**: 100 (固定)
- **用户级**: 50-80
- **项目级**: 80-120

---

### 2. 命令禁用

临时禁用某个命令:

```yaml
slash_commands:
  shell:
    - name: deploy
      description: "部署命令"
      command: "./deploy.sh"
      enabled: false  # 禁用
```

禁用后执行会返回错误:
```python
result = orch.process("/deploy")
assert result.success == False
assert "disabled" in result.error.lower()
```

---

### 3. 命令参数

Shell 命令支持参数传递:

```yaml
slash_commands:
  shell:
    - name: pytest
      command: "pytest"
      examples:
        - "/pytest"
        - "/pytest tests/test_api.py"
        - "/pytest -v --cov"
```

使用:
```python
result = orch.process("/pytest tests/test_api.py -v")
# 实际执行: pytest tests/test_api.py -v
```

---

### 4. 依赖声明

声明命令的依赖关系:

```yaml
slash_commands:
  shell:
    - name: deploy
      command: "./deploy.sh"
      dependencies:
        - "command:git-status"  # 需要 git
        - "skill:code-review"   # 需要审查通过
```

**未来支持**: Phase 7 将支持基于依赖关系的并行执行。

---

### 5. 命令元数据

查询命令的详细信息:

```python
# 获取命令元数据
cmd = orch.slash_registry.get("git-status")

print(f"名称: {cmd.name}")
print(f"完整名称: {cmd.full_name}")
print(f"类型: {cmd.type.value}")
print(f"描述: {cmd.description}")
print(f"优先级: {cmd.priority}")
print(f"来源: {cmd.source}")
print(f"示例: {cmd.examples}")
```

---

## 故障排查

### 问题 1: 命令未找到

**症状**:
```python
result = orch.process("/my-custom-cmd")
# Error: Command '/my-custom-cmd' not found
```

**解决**:
1. 检查配置文件路径是否正确
2. 确认 `auto_discover=True`
3. 验证命令名称拼写
4. 使用 `/list-commands` 查看已注册命令

---

### 问题 2: 命令被禁用

**症状**:
```python
result = orch.process("/deploy")
# Error: Command '/deploy' is disabled
```

**解决**:
在配置中设置 `enabled: true`

---

### 问题 3: 优先级冲突

**症状**:
自定义命令未生效,仍然执行内置命令。

**解决**:
提高项目级命令的优先级:

```yaml
slash_commands:
  shell:
    - name: git-status
      command: "git status -sb"
      priority: 120  # 高于内置的 100
```

---

### 问题 4: Shell 命令执行失败

**症状**:
```python
result = orch.process("/build")
# success=False, error="Execution failed"
```

**解决**:
1. 检查命令是否在 PATH 中
2. 验证命令语法是否正确
3. 检查 Windows 编码问题(使用 UTF-8)
4. 查看详细错误: `result.error`

---

### 问题 5: V3 未启用

**症状**:
```python
result = orch.process("/stats")
# Error: Slash commands not available without V3
```

**解决**:
创建 Orchestrator 时启用 V3:

```python
orch = MasterOrchestrator(
    auto_discover=True  # 必须启用
)
```

---

## 最佳实践

### 1. 命名规范

✅ **推荐**:
- 简短、描述性: `/gst`, `/build`, `/test`
- 小写字母和连字符: `/git-log`, `/npm-test`
- 动词开头: `/deploy`, `/review`, `/analyze`

❌ **避免**:
- 过长: `/run-all-unit-tests-with-coverage`
- 特殊字符: `/build!`, `/test?`
- 大写: `/DEPLOY`

---

### 2. 优先级分配

| 来源 | 优先级范围 | 用途 |
|------|-----------|------|
| 内置 | 100 | 系统默认命令 |
| 全局用户 | 50-80 | 个人常用命令 |
| 项目 | 80-120 | 项目特定命令 |

---

### 3. 文档化

在配置中添加清晰的描述和示例:

```yaml
slash_commands:
  shell:
    - name: deploy
      description: "部署到生产环境(需要 sudo 权限)"
      command: "./scripts/deploy.sh production"
      examples:
        - "/deploy"
        - "/deploy --dry-run"
      dependencies:
        - "command:git-status"
```

---

### 4. 安全考虑

**危险命令**:
- 避免在配置中使用 `rm -rf`, `dd` 等破坏性命令
- CommandExecutor 会自动拦截危险命令

**敏感信息**:
- 不要在配置中硬编码密码或 API Key
- 使用环境变量: `command: "deploy.sh $API_KEY"`

---

## API 参考

### SlashCommandResult

```python
@dataclass
class SlashCommandResult:
    command: str                 # 执行的命令 (如 "/stats")
    success: bool                # 是否成功
    output: Any                  # 命令输出
    error: Optional[str]         # 错误信息 (如果失败)
    executed_at: datetime        # 执行时间
    duration_seconds: float      # 执行耗时(秒)
    metadata: Dict[str, Any]     # 额外元数据
```

### SlashCommandRegistry

```python
class SlashCommandRegistry:
    def register(command: SlashCommandMetadata) -> bool
    def get(name: str) -> Optional[SlashCommandMetadata]
    def exists(name: str) -> bool
    def list_commands(type_filter: Optional[SlashCommandType] = None) -> List[SlashCommandMetadata]
    def execute(command_name: str, args: List[str] = None, **kwargs) -> SlashCommandResult
    def get_stats() -> Dict[str, Any]
    def clear() -> None
```

---

## 示例项目

### 示例 1: 快速构建流程

```yaml
# orchestrator.yaml
slash_commands:
  shell:
    - name: clean
      description: "清理构建产物"
      command: "rm -rf build/ dist/"
      priority: 70

    - name: lint
      description: "代码检查"
      command: "flake8 src/"
      priority: 70

    - name: test
      description: "运行测试"
      command: "pytest tests/ -v"
      priority: 70

    - name: build
      description: "构建项目"
      command: "python setup.py build"
      priority: 70
```

使用:
```python
orch.process("/clean")
orch.process("/lint")
orch.process("/test")
orch.process("/build")
```

---

### 示例 2: Git 工作流

```yaml
slash_commands:
  shell:
    - name: gst
      description: "Git status"
      command: "git status -sb"
      priority: 60

    - name: gd
      description: "Git diff"
      command: "git diff"
      priority: 60

    - name: glog
      description: "Git log"
      command: "git log --oneline --graph -10"
      priority: 60

    - name: gpush
      description: "Git push"
      command: "git push origin $(git branch --show-current)"
      priority: 60
```

---

### 示例 3: 开发工作流

```yaml
slash_commands:
  skill:
    - name: review
      description: "代码审查"
      skill: "code-review"
      priority: 80

    - name: refactor
      description: "重构建议"
      skill: "code-refactoring-assistant"
      priority: 80

  agent:
    - name: explore
      description: "探索代码"
      agent_type: "EXPLORE"
      priority: 75

    - name: plan
      description: "规划方案"
      agent_type: "PLAN"
      priority: 75
```

---

## 路线图

### V3.1 (当前版本)
- ✅ 基本 Slash Command 系统
- ✅ 5 种命令类型
- ✅ 配置文件支持
- ✅ 优先级系统
- ✅ 8 个内置命令

### V3.2 (计划中)
- ⏳ 命令别名系统
- ⏳ 命令分组和命名空间
- ⏳ 交互式参数提示
- ⏳ 命令历史记录

### V4.0 (未来)
- ⏳ 基于依赖的并行执行
- ⏳ 命令权限系统
- ⏳ 命令可视化管理界面
- ⏳ 远程命令执行

---

## 相关文档

- [Architecture Overview](./ARCHITECTURE.md)
- [Configuration Guide](./orchestrator.yaml.template)
- [V3 Integration Design](./MEMEX_CLI_INTEGRATION_DESIGN.md)
- [Test Summary](../orchestrator/tests/SLASH_COMMAND_TEST_SUMMARY.md)

---

## 获取帮助

- **查看命令列表**: `/list-commands`
- **查看统计**: `/stats`
- **Issue 报告**: [GitHub Issues](https://github.com/your-repo/issues)
- **文档**: [docs/](https://github.com/your-repo/docs)

---

**最后更新**: 2026-01-04
**作者**: Orchestrator Team
**版本**: V3.1
