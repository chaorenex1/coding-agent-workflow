# Coding Workflow Plugin - Testing Guide

本文档指导如何测试 Coding Workflow 插件的安装和功能。

---

## 🧪 测试前准备

### 1. 确认当前项目状态

```bash
# 检查插件文件是否存在
ls -la .claude-plugin/plugin.json
ls -la hooks/hooks.json
ls -la docs/coding-workflow.local.example.md

# 验证 JSON 格式
python -m json.tool .claude-plugin/plugin.json
python -m json.tool hooks/hooks.json
```

### 2. 提交插件配置到 Git

```bash
# 查看新增文件
git status

# 添加插件文件
git add .claude-plugin/
git add hooks/
git add docs/coding-workflow.local.example.md
git add .gitignore
git add README.md

# 提交
git commit -m "feat: 添加 Claude Code Plugin Marketplace 支持

- 创建 .claude-plugin/plugin.json 插件清单
- 添加 hooks/hooks.json 依赖验证钩子
- 提供配置模板 docs/coding-workflow.local.example.md
- 更新 README.md 添加插件安装说明
- 更新 .gitignore 排除配置文件

支持通过 /plugin coding-workflow 一键安装
"
```

---

## 📦 安装测试

### 方式 1: 本地测试（开发模式）

在 Claude Code 中测试本地插件：

```bash
# 方法 A: 使用 --plugin-dir 参数（推荐）
claude code --plugin-dir /path/to/coding-workflow

# 方法 B: 创建符号链接
ln -s /path/to/coding-workflow ~/.claude/plugins/coding-workflow
```

### 方式 2: 模拟 Marketplace 安装

如果插件已发布到 Marketplace：

```
/plugin coding-workflow
```

---

## ✅ 验证清单

### 1. 插件加载验证

**目标**: 确认插件被 Claude Code 正确识别和加载

**步骤**:
1. 启动 Claude Code
2. 运行 `/help` 命令
3. 检查输出中是否包含 coding-workflow 的命令

**预期结果**:
- 看到 `/bmad`、`/bmad-iter`、`/quick-feature` 等命令
- 命令数量应为 47 个

**验证命令示例**:
```bash
# 测试一个简单命令
/bmad-analyze "测试产品"
```

---

### 2. Skills 可用性验证

**目标**: 确认所有 skills 可被调用

**步骤**:
1. 尝试调用 master-orchestrator skill
2. 检查 skill 是否正确加载

**测试查询**:
```
请使用 master-orchestrator 帮我实现一个简单的 Hello World 函数
```

**预期结果**:
- master-orchestrator skill 被触发
- skill 能够正常路由任务

---

### 3. Agents 触发验证

**目标**: 验证 agents 能在适当场景下自动触发

**步骤**:
1. 创建触发 agent 的场景
2. 观察 agent 是否被调用

**测试场景示例**:

```
场景 1: 触发 bmad-analyst
"我想开发一个任务管理应用，帮我分析市场需求"

场景 2: 触发 code-reviewer
"请审查以下代码..."

场景 3: 触发 test-generator
"为这个函数生成测试用例"
```

**预期结果**:
- 相关 agent 自动触发
- Agent 按照定义的职责工作

---

### 4. Hooks 执行验证

**目标**: 确认 SessionStart hook 正确执行依赖检查

**步骤**:
1. 重启 Claude Code 会话
2. 观察启动时的消息

**预期结果**:

**情况 A - 依赖已安装**:
```
✅ Coding Workflow 依赖检查通过
   - memex-cli: 已安装 (v1.2.0)
   - Python 依赖: 已安装
```

**情况 B - 依赖缺失**:
```
⚠️  Coding Workflow 部分依赖缺失：

缺失项：
- memex-cli: 未找到
  安装命令: npm install -g memex-cli

- Python 依赖: chardet 或 pyyaml 未安装
  安装命令: pip install chardet pyyaml

您可以继续使用插件，但某些功能可能受限。
```

**验证依赖检查缓存**:
- 第一次启动应执行完整检查
- 24小时内再次启动应跳过检查（查看 `~/.claude/coding-workflow-deps-check.txt`）

---

### 5. 配置文件验证

**目标**: 测试用户配置功能

**步骤**:
1. 复制配置模板：
   ```bash
   cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
   ```

2. 修改配置（例如自定义 memex-cli 路径）

3. 重启 Claude Code

**预期结果**:
- 配置文件被正确读取
- 自定义路径生效

---

## 🔍 故障排查

### 问题 1: Commands 未显示

**症状**: `/help` 中看不到 coding-workflow 的命令

**排查步骤**:
1. 检查 plugin.json 是否存在且格式正确
   ```bash
   python -m json.tool .claude-plugin/plugin.json
   ```

2. 检查 commands 路径是否正确
   ```bash
   ls commands/bmad-iterate/*.md
   ```

3. 查看 Claude Code 日志（如果可用）

**解决方案**:
- 确保 .claude-plugin/plugin.json 在项目根目录
- 重启 Claude Code 会话
- 检查文件权限

---

### 问题 2: Skills 未触发

**症状**: 调用 skill 时没有响应

**排查步骤**:
1. 检查 skills 目录结构
   ```bash
   find skills -name "SKILL.md"
   ```

2. 验证 SKILL.md 格式（需要 YAML frontmatter）

**解决方案**:
- 确保每个 skill 有 SKILL.md 文件
- 检查 frontmatter 格式正确

---

### 问题 3: Hooks 未执行

**症状**: SessionStart 时没有依赖检查消息

**排查步骤**:
1. 检查 hooks.json 格式
   ```bash
   python -m json.tool hooks/hooks.json
   ```

2. 查看 Claude Code 是否支持 SessionStart hook

**解决方案**:
- 验证 hooks.json 在 hooks/ 目录
- 检查 hook 类型拼写正确

---

### 问题 4: Agents 未自动触发

**症状**: 期望 agent 自动触发但没有

**排查步骤**:
1. 检查 agent 文件 frontmatter
   ```bash
   head -20 agents/automation/ai-workflow-architect.md
   ```

2. 验证 `description` 字段包含触发关键词

**解决方案**:
- 确保 agent description 清晰描述触发场景
- 在查询中使用明确的关键词

---

## 📊 测试报告模板

完成测试后，填写以下报告：

```markdown
# Coding Workflow Plugin 测试报告

**测试日期**: YYYY-MM-DD
**Claude Code 版本**: X.X.X
**插件版本**: 3.0.0

## 测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 插件加载 | ✅/❌ | ... |
| Commands 可用 | ✅/❌ | 可用命令数: X/47 |
| Skills 触发 | ✅/❌ | 测试的 skills: ... |
| Agents 触发 | ✅/❌ | 测试的 agents: ... |
| Hooks 执行 | ✅/❌ | 依赖检查: ... |
| 配置文件 | ✅/❌ | ... |

## 发现的问题

1. **问题描述**
   - 现象: ...
   - 复现步骤: ...
   - 影响范围: ...

## 建议改进

1. ...
2. ...

## 总体评价

- [ ] 🟢 可以发布
- [ ] 🟡 需要修复后发布
- [ ] 🔴 重大问题，不可发布
```

---

## 🎯 下一步

测试通过后：

1. **提交代码**:
   ```bash
   git push origin main
   ```

2. **创建 Release Tag**:
   ```bash
   git tag -a v3.0.0 -m "Release: Claude Code Plugin Marketplace 支持"
   git push origin v3.0.0
   ```

3. **发布到 Marketplace**（如适用）:
   - 按照 Claude Code 官方发布流程
   - 提交插件审核

4. **更新文档**:
   - 在 GitHub README 添加安装徽章
   - 创建使用教程视频或 GIF

---

**祝测试顺利！** 🚀

如有问题，请查看项目 Issues 或提交新 Issue。
