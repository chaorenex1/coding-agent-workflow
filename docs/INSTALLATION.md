# Orchestrator V3 安装指南

完整的自动化安装流程说明文档

## 目录

- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [安装方式](#安装方式)
- [详细步骤](#详细步骤)
- [验证安装](#验证安装)
- [故障排除](#故障排除)
- [卸载](#卸载)

---

## 快速开始

### Windows

```bash
# 克隆仓库（如果还没有）
git clone https://github.com/your-org/orchestrator.git
cd orchestrator

# 运行安装脚本
scripts\install.bat

# 验证安装
python scripts\verify_installation.py
```

### Linux / macOS

```bash
# 克隆仓库（如果还没有）
git clone https://github.com/your-org/orchestrator.git
cd orchestrator

# 赋予执行权限
chmod +x scripts/install.sh

# 运行安装脚本
bash scripts/install.sh

# 验证安装
python3 scripts/verify_installation.py
```

---

## 系统要求

### 必需

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.8+ | 核心运行环境 |
| Git | 2.0+ | 用于克隆仓库和版本管理 |

### 可选（推荐）

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Node.js | 16+ | memex-cli 运行环境 |
| npm | 8+ | Node.js 包管理器 |
| pnpm | 7+ | 高性能包管理器（自动安装）|

### 磁盘空间

- 最小: 500 MB
- 推荐: 1 GB（包含所有依赖和缓存）

---

## 安装方式

### 方式1: 自动化安装（推荐）

使用提供的安装脚本自动完成所有步骤：

**Windows:**
```bash
scripts\install.bat
```

**Linux/macOS:**
```bash
bash scripts/install.sh
```

### 方式2: Python直接安装

直接运行Python安装脚本并自定义选项：

```bash
python scripts/install_orchestrator.py [选项]
```

**可用选项:**
- `--skip-deps` - 跳过依赖检查
- `--skip-memex` - 跳过 memex-cli 安装
- `--skip-workflow` - 跳过 coding-agent-workflow 安装
- `--skip-requirements` - 跳过 Python 依赖安装
- `--verbose` - 详细输出

**示例:**
```bash
# 跳过memex-cli安装（如果不需要）
python scripts/install_orchestrator.py --skip-memex

# 仅安装核心组件
python scripts/install_orchestrator.py --skip-memex --skip-workflow

# 详细输出模式
python scripts/install_orchestrator.py --verbose
```

### 方式3: 手动安装

如果自动安装失败，可以手动执行以下步骤：

```bash
# 1. 创建缓存目录
mkdir -p ~/.memex/orchestrator/{config,logs,skills,commands,agents,prompts}

# 2. 安装 memex-cli（可选）
git clone https://github.com/chaorenex1/memex-cli ~/.memex/cli
cd ~/.memex/cli
bash install.sh  # 如果有安装脚本

# 3. 安装 coding-agent-workflow（可选）
git clone https://github.com/chaorenex1/coding-agent-workflow.git /tmp/workflow
cp -r /tmp/workflow/skills ~/.claude/
cp -r /tmp/workflow/agents ~/.claude/
cp -r /tmp/workflow/prompts ~/.claude/
cp -r /tmp/workflow/slash-commands ~/.claude/

# 4. 安装Python依赖
# 查找所有 requirements.txt 并安装
find ~/.claude/skills -name "requirements.txt" -exec pip install -r {} -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \;

# 5. 创建配置文件
cat > ~/.memex/orchestrator/config/orchestrator.json << EOF
{
  "version": "3.0.0",
  "auto_discover": true,
  "enable_parallel": true,
  "max_parallel_workers": 3,
  "cache_enabled": true
}
EOF
```

---

## 详细步骤

安装脚本执行以下5个步骤：

### 步骤1: 系统依赖检查

检查并验证以下依赖：

- ✓ Python 3.8+
- ✓ Git 2.0+
- ⚠ Node.js 16+ （可选）
- ⚠ npm 8+ （可选）
- ⚠ pnpm 7+ （可选，如果缺失会自动安装）

**如果Python或Git缺失:**
- Windows: 访问官网下载安装
  - Python: https://www.python.org/downloads/
  - Git: https://git-scm.com/download/win
- Linux: `sudo apt install python3 git` (Debian/Ubuntu)
- macOS: `brew install python git`

### 步骤2: 安装 memex-cli

从 GitHub 克隆 memex-cli 仓库到 `~/.memex/cli`：

```
https://github.com/chaorenex1/memex-cli
```

**位置:**
- Windows: `C:\Users\<用户名>\.memex\cli\`
- Linux/macOS: `~/.memex/cli/`

**说明:**
- memex-cli 提供底层技能执行能力
- 如果安装失败，Orchestrator 会使用本地fallback实现
- 可使用 `--skip-memex` 跳过此步骤

### 步骤3: 安装 coding-agent-workflow

从 GitHub 克隆 coding-agent-workflow 仓库并安装资源：

```
https://github.com/chaorenex1/coding-agent-workflow.git
```

**安装资源:**
- `slash-commands/` → `~/.claude/slash-commands/`
- `agents/` → `~/.claude/agents/`
- `skills/` → `~/.claude/skills/`
- `prompts/` → `~/.claude/prompts/`

**说明:**
- 提供预定义的 Slash Commands、Agents、Skills 和 Prompts
- 如果目录已存在，会覆盖（force=True）
- 可使用 `--skip-workflow` 跳过此步骤

### 步骤4: 安装 Skill 依赖

扫描所有 Skills 目录，查找 `requirements.txt` 文件并安装：

**镜像配置:**
```bash
pip install -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com
```

**说明:**
- 使用阿里云 PyPI 镜像加速下载
- 超时时间: 300 秒
- 如果部分依赖安装失败，不会中断整体流程
- 可使用 `--skip-requirements` 跳过此步骤

### 步骤5: 初始化本地缓存

创建 Orchestrator 缓存目录结构：

```
~/.memex/orchestrator/
├── config/
│   └── orchestrator.json
├── logs/
├── skills/
├── commands/
├── agents/
└── prompts/
```

**orchestrator.json 配置:**
```json
{
  "version": "3.0.0",
  "auto_discover": true,
  "enable_parallel": true,
  "max_parallel_workers": 3,
  "cache_enabled": true
}
```

---

## 验证安装

### 运行验证脚本

```bash
python scripts/verify_installation.py
```

**验证项目:**
1. ✓ Python 模块导入
2. ✓ 核心类验证
3. ✓ 执行器验证
4. ✓ 目录结构验证
5. ✓ 配置文件验证
6. ✓ 技能文件验证
7. ⚠ 外部依赖验证（可选）

**预期输出:**
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

...

============================================================
验证结果
============================================================
通过: 25/25

✓ 所有必需检查通过！
Orchestrator 已正确安装并可以使用
```

### 运行快速测试

```bash
# 运行Mock测试（快速，不需要API）
python orchestrator/tests/test_phase5_simple.py

# 运行集成测试（需要后端API配置）
python orchestrator/tests/test_phase5_executors.py
```

### 手动验证

**1. 检查Python导入:**
```python
python -c "from orchestrator import MasterOrchestrator; print('OK')"
```

**2. 检查缓存目录:**
```bash
# Windows
dir %USERPROFILE%\.memex\orchestrator

# Linux/macOS
ls -la ~/.memex/orchestrator
```

**3. 检查技能文件:**
```bash
# Windows
dir skills\memex-cli\skills\*.yaml

# Linux/macOS
ls -la skills/memex-cli/skills/*.yaml
```

**预期文件:**
- intent-analyzer.yaml
- command-parser.yaml
- agent-router.yaml
- prompt-renderer.yaml
- dev-workflow.yaml

---

## 故障排除

### 问题1: Python版本过低

**错误:**
```
✗ Python 版本过低: 3.7, 需要 >= 3.8
```

**解决:**
1. 卸载旧版本 Python
2. 安装 Python 3.8 或更高版本
3. 重新运行安装脚本

### 问题2: Git未安装

**错误:**
```
✗ Git 未安装
```

**解决:**
- Windows: https://git-scm.com/download/win
- Linux: `sudo apt install git`
- macOS: `brew install git`

### 问题3: memex-cli 安装失败

**错误:**
```
✗ memex-cli 安装失败
```

**解决:**
1. 跳过 memex-cli 安装:
   ```bash
   python scripts/install_orchestrator.py --skip-memex
   ```
2. Orchestrator 会使用本地 fallback 实现
3. 功能不受影响，仅性能可能略降

### 问题4: GitHub 连接超时

**错误:**
```
fatal: unable to access 'https://github.com/...': Connection timed out
```

**解决:**
1. 检查网络连接
2. 使用代理（如果需要）:
   ```bash
   git config --global http.proxy http://proxy.example.com:8080
   ```
3. 或手动下载仓库并解压到指定位置

### 问题5: pip 安装依赖失败

**错误:**
```
ERROR: Could not install packages due to an OSError
```

**解决:**
1. 使用虚拟环境:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
2. 升级 pip:
   ```bash
   python -m pip install --upgrade pip
   ```
3. 跳过依赖安装:
   ```bash
   python scripts/install_orchestrator.py --skip-requirements
   ```

### 问题6: Windows编码错误

**错误:**
```
UnicodeDecodeError: 'gbk' codec can't decode...
```

**解决:**
脚本已自动处理 Windows 编码。如果仍有问题：
1. 设置环境变量:
   ```cmd
   set PYTHONIOENCODING=utf-8
   ```
2. 或使用 Git Bash / PowerShell

### 问题7: 权限不足

**错误:**
```
PermissionError: [Errno 13] Permission denied
```

**解决:**
- Linux/macOS: 使用 `sudo` 或修改目录权限
- Windows: 以管理员身份运行 CMD/PowerShell

### 获取帮助

如果遇到其他问题：

1. **查看详细日志:**
   ```bash
   python scripts/install_orchestrator.py --verbose
   ```

2. **检查安装状态:**
   ```bash
   python scripts/verify_installation.py --verbose
   ```

3. **提交 Issue:**
   访问 GitHub Issues 页面并提供：
   - 操作系统和版本
   - Python 版本
   - 完整错误信息
   - 安装日志（使用 --verbose）

---

## 卸载

### 完全卸载

```bash
# 1. 删除缓存目录
# Windows:
rmdir /s /q "%USERPROFILE%\.memex"

# Linux/macOS:
rm -rf ~/.memex

# 2. 删除 Claude 配置（如果安装了 workflow）
# Windows:
rmdir /s /q "%USERPROFILE%\.claude"

# Linux/macOS:
rm -rf ~/.claude

# 3. 卸载 Python 依赖（可选）
pip uninstall -r requirements.txt -y
```

### 仅卸载 Orchestrator

保留 memex-cli 和 workflow：

```bash
# 删除 Orchestrator 缓存
rm -rf ~/.memex/orchestrator
```

### 重新安装

卸载后重新安装：

```bash
# 清理
rm -rf ~/.memex ~/.claude

# 重新运行安装脚本
python scripts/install_orchestrator.py
```

---

## 高级配置

### 自定义安装路径

编辑 `scripts/install_orchestrator.py`，修改默认路径：

```python
# memex-cli 安装路径
MEMEX_INSTALL_DIR = Path.home() / 'custom' / 'memex-cli'

# workflow 安装路径
WORKFLOW_INSTALL_DIR = Path.home() / 'custom' / 'claude'

# 缓存目录
CACHE_DIR = Path.home() / 'custom' / 'orchestrator-cache'
```

### 离线安装

1. 下载所需仓库:
   ```bash
   git clone https://github.com/chaorenex1/memex-cli
   git clone https://github.com/chaorenex1/coding-agent-workflow
   ```

2. 手动复制到目标位置
3. 跳过克隆步骤:
   ```bash
   python scripts/install_orchestrator.py --skip-memex --skip-workflow
   ```

### 企业环境配置

**使用企业 PyPI 镜像:**

编辑 `scripts/install_orchestrator.py`，修改镜像地址：

```python
ALIYUN_MIRROR = "https://your-enterprise-mirror/pypi/simple/"
```

**使用企业 Git 服务器:**

编辑仓库 URL：

```python
MEMEX_REPO = "https://your-git-server/memex-cli"
WORKFLOW_REPO = "https://your-git-server/coding-agent-workflow"
```

---

## 后续步骤

安装完成后：

1. **配置环境变量** (如果需要):
   ```bash
   export CLAUDE_API_KEY=your-key
   export GEMINI_API_KEY=your-key
   export CODEX_API_KEY=your-key
   ```

2. **阅读文档:**
   - [架构文档](ARCHITECTURE.md)
   - [用户指南](USER_GUIDE.md)
   - [Slash Commands](SLASH_COMMANDS.md)

3. **运行示例:**
   ```python
   from orchestrator import MasterOrchestrator, BackendOrchestrator

   backend = BackendOrchestrator()
   orch = MasterOrchestrator(backend, auto_discover=True)

   result = orch.process("帮我分析这段代码")
   print(result)
   ```

4. **探索功能:**
   - 尝试 Slash Commands: `/discover`, `/list-skills`
   - 测试 Agent: 探索代码库
   - 运行 Workflow: 多阶段开发任务

---

**版本**: 3.0.0
**最后更新**: 2026-01-05
**维护者**: Orchestrator Team
