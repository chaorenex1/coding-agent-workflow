# Orchestrator 安装脚本

自动化安装和验证工具集

## 文件说明

| 文件 | 说明 | 平台 |
|------|------|------|
| `install_orchestrator.py` | 主安装脚本（Python） | 所有平台 |
| `install.bat` | Windows 批处理包装器 | Windows |
| `install.sh` | Unix Shell 包装器 | Linux/macOS |
| `verify_installation.py` | 安装验证脚本 | 所有平台 |
| `README.md` | 本文档 | - |

## 快速开始

### Windows

```cmd
scripts\install.bat
```

### Linux / macOS

```bash
bash scripts/install.sh
```

## 自定义安装

### 跳过特定步骤

```bash
# 跳过 memex-cli 安装
python scripts/install_orchestrator.py --skip-memex

# 跳过 workflow 安装
python scripts/install_orchestrator.py --skip-workflow

# 跳过依赖安装
python scripts/install_orchestrator.py --skip-requirements

# 跳过依赖检查
python scripts/install_orchestrator.py --skip-deps

# 组合使用
python scripts/install_orchestrator.py --skip-memex --skip-workflow
```

### 详细输出

```bash
python scripts/install_orchestrator.py --verbose
```

## 验证安装

### 快速验证

```bash
python scripts/verify_installation.py
```

### 详细验证

```bash
python scripts/verify_installation.py --verbose
```

## 安装流程

自动安装脚本执行以下步骤：

### 1. 系统依赖检查 ✓

检查并验证：
- Python 3.8+ （必需）
- Git 2.0+ （必需）
- Node.js 16+ （可选）
- npm 8+ （可选）
- pnpm 7+ （可选，自动安装）

### 2. 安装 memex-cli ⚠

从 GitHub 克隆 memex-cli：
```
https://github.com/chaorenex1/memex-cli
```

安装位置：`~/.memex/cli/`

**说明**: 如果失败不影响 Orchestrator 核心功能

### 3. 安装 coding-agent-workflow ✓

从 GitHub 克隆 coding-agent-workflow：
```
https://github.com/chaorenex1/coding-agent-workflow.git
```

安装资源到：`~/.claude/`
- `slash-commands/`
- `agents/`
- `skills/`
- `prompts/`

### 4. 安装 Skill 依赖 ✓

扫描所有 `requirements.txt` 并安装：
```bash
pip install -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com
```

### 5. 初始化本地缓存 ✓

创建缓存目录结构：
```
~/.memex/orchestrator/
├── config/
├── logs/
├── skills/
├── commands/
├── agents/
└── prompts/
```

## 输出示例

### 成功安装

```
======================================================================
  Orchestrator V3 - 自动化安装程序
======================================================================

============================================================
第1步: 检查系统依赖
============================================================

检查 Python 版本...
✓ Python 3.12 已安装
检查 Git...
✓ git version 2.43.0
检查 Node.js 版本...
✓ Node.js v20 已安装
检查 npm...
✓ npm 10.2.5 已安装
检查 pnpm...
✓ pnpm 8.15.0 已安装

依赖检查结果:
  ✓ Python (>= 3.8)
  ✓ Git
  ✓ Node.js (>= 16)
  ✓ npm
  ✓ pnpm

============================================================
第2步: 安装 memex-cli
============================================================

✓ memex-cli 已安装: v1.0.0
memex-cli 已存在，跳过安装

============================================================
第3步: 安装 coding-agent-workflow
============================================================

正在克隆 https://github.com/chaorenex1/coding-agent-workflow.git...
✓ 仓库克隆成功
覆盖已存在的 slash-commands...
✓ 安装 slash-commands 到 /home/user/.claude/slash-commands
✓ 安装 agents 到 /home/user/.claude/agents
✓ 安装 skills 到 /home/user/.claude/skills
✓ 安装 prompts 到 /home/user/.claude/prompts
✓ 成功安装 4 个资源

============================================================
第4步: 安装 Skill 依赖
============================================================

发现 3 个 requirements.txt 文件
安装依赖: skill-a...
✓ 依赖安装成功
安装依赖: skill-b...
✓ 依赖安装成功
安装依赖: skill-c...
✓ 依赖安装成功
✓ 所有依赖安装成功

============================================================
第5步: 初始化本地缓存
============================================================

✓ 创建目录: /home/user/.memex/orchestrator
✓ 创建目录: /home/user/.memex/orchestrator/skills
✓ 创建目录: /home/user/.memex/orchestrator/commands
✓ 创建目录: /home/user/.memex/orchestrator/agents
✓ 创建目录: /home/user/.memex/orchestrator/prompts
✓ 创建目录: /home/user/.memex/orchestrator/logs
✓ 创建目录: /home/user/.memex/orchestrator/config
✓ 创建配置文件: /home/user/.memex/orchestrator/config/orchestrator.json
✓ 缓存目录初始化完成

======================================================================
  安装完成
======================================================================

安装结果:
  ✓ 依赖检查
  ✓ memex-cli
  ✓ workflow
  ✓ Skill依赖
  ✓ 缓存初始化

✓ 所有组件安装成功！

下一步:
  1. 配置环境变量（如果需要）
  2. 运行测试: python orchestrator/tests/test_phase5_simple.py
  3. 启动 MasterOrchestrator
```

### 验证输出

```
============================================================
Orchestrator 安装验证
============================================================

1. Python模块验证
✓ 核心模块: orchestrator
✓ 核心组件: orchestrator.core
✓ 执行器模块: orchestrator.executors
✓ 技能模块: orchestrator.skills

2. 核心类验证
✓ MasterOrchestrator
✓ BackendOrchestrator
✓ UnifiedRegistry
✓ ExecutorFactory
✓ ParallelScheduler
✓ DependencyAnalyzer
✓ ConfigLoader

3. 执行器验证
✓ MemexExecutorBase
✓ CommandExecutor
✓ AgentCaller
✓ PromptManager

4. 目录结构验证
✓ Memex根目录: /home/user/.memex
✓ Orchestrator缓存: /home/user/.memex/orchestrator
✓ 配置目录: /home/user/.memex/orchestrator/config
✓ 日志目录: /home/user/.memex/orchestrator/logs
✓ Claude配置目录（可选）: /home/user/.claude

5. 配置文件验证
✓ 配置项: version
✓ 配置项: auto_discover
✓ 配置项: enable_parallel

6. 技能文件验证
✓ Skill: intent-analyzer.yaml
✓ Skill: command-parser.yaml
✓ Skill: agent-router.yaml
✓ Skill: prompt-renderer.yaml
✓ Skill: dev-workflow.yaml

7. 外部依赖验证（可选）
✓ Git
✓ Node.js（可选）
✓ npm（可选）
✓ pnpm（可选）
✗ memex-cli（可选）: 未安装

============================================================
验证结果
============================================================
通过: 24/25

✓ 所有必需检查通过！
Orchestrator 已正确安装并可以使用
```

## 常见问题

### Q: 安装失败怎么办？

A: 按以下步骤排查：
1. 运行 `--verbose` 查看详细日志
2. 检查网络连接（需要访问 GitHub）
3. 确认 Python 和 Git 已安装
4. 查看 [完整安装指南](../docs/INSTALLATION.md)

### Q: 可以离线安装吗？

A: 可以，步骤如下：
1. 提前下载所需仓库
2. 手动复制到目标位置
3. 使用 `--skip-memex --skip-workflow` 跳过克隆步骤

### Q: memex-cli 安装失败影响使用吗？

A: 不影响。Orchestrator 有完整的 fallback 机制，会使用本地实现替代。

### Q: 如何更新已安装的组件？

A: 重新运行安装脚本即可：
```bash
python scripts/install_orchestrator.py
```

已存在的文件会被覆盖更新。

### Q: 如何完全卸载？

A: 删除以下目录：
```bash
# 删除缓存
rm -rf ~/.memex

# 删除配置（如果安装了 workflow）
rm -rf ~/.claude
```

## 更多信息

- **完整安装指南**: [docs/INSTALLATION.md](../docs/INSTALLATION.md)
- **架构文档**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **用户指南**: [docs/USER_GUIDE.md](../docs/USER_GUIDE.md)
- **故障排除**: [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

## 技术支持

遇到问题？

1. 查看 [完整安装指南](../docs/INSTALLATION.md#故障排除)
2. 运行验证脚本获取诊断信息
3. 提交 GitHub Issue 并附上详细日志

---

**版本**: 1.0.0
**最后更新**: 2026-01-05
**维护者**: Orchestrator Team
