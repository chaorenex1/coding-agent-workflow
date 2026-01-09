---
memexCliPath: "memex-cli"
---

# Coding Workflow Configuration

这是 Coding Workflow 插件的配置文件示例。

## 使用方法

1. 复制此文件到您的 Claude Code 配置目录：
   ```bash
   cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
   ```

2. 根据您的环境修改配置项

3. 重启 Claude Code 会话

## 配置项说明

### memexCliPath

**说明**: memex-cli 可执行文件的路径

**默认值**: `"memex-cli"` (从 PATH 中查找)

**自定义示例**:
```yaml
memexCliPath: "/usr/local/bin/memex-cli"
```

或 Windows:
```yaml
memexCliPath: "C:\\Program Files\\nodejs\\memex-cli.cmd"
```

**何时需要修改**:
- memex-cli 不在系统 PATH 中
- 使用了自定义安装路径
- 需要指定特定版本的 memex-cli

## 未来配置项（规划中）

以下配置项将在未来版本中支持：

### enabledBackends
启用的 AI 后端列表
```yaml
enabledBackends:
  - claude
  - gemini
  - codex
```

### defaultModel
默认使用的模型
```yaml
defaultModel: "claude-sonnet-4-5"
```

### logLevel
日志级别
```yaml
logLevel: "info"  # debug | info | warn | error
```

## 故障排查

### memex-cli 未找到

如果看到 "memex-cli not found" 错误：

1. 确认 memex-cli 已安装：
   ```bash
   npm install -g memex-cli
   ```

2. 查找安装路径：
   ```bash
   # macOS/Linux
   which memex-cli

   # Windows
   where memex-cli
   ```

3. 将找到的路径设置到 `memexCliPath`

### Python 依赖缺失

如果看到 "chardet or pyyaml not found" 错误：

```bash
pip install chardet pyyaml
```

---

**提示**: 此文件仅作为配置示例。实际配置文件应放在 `~/.claude/coding-workflow.local.md`，并且**不应提交到 Git**（已在 .gitignore 中排除）。
