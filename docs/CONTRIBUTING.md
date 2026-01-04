# 贡献指南

感谢你对 MasterOrchestrator 的关注！我们欢迎所有形式的贡献。

## 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [开发工作流](#开发工作流)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [提交规范](#提交规范)
- [如何贡献](#如何贡献)
- [常见任务](#常见任务)

---

## 开发环境搭建

### 1. Fork 和 Clone 仓库

```bash
# Fork 仓库到你的 GitHub 账号
# 然后 clone 到本地
git clone https://github.com/YOUR_USERNAME/coding_base.git
cd coding_base

# 添加上游仓库
git remote add upstream https://github.com/ORIGINAL_OWNER/coding_base.git
```

### 2. 安装依赖

```bash
# Python 依赖（可选）
pip install chardet pyyaml

# 开发依赖
pip install pytest pytest-cov black flake8 mypy

# memex-cli（必需）
npm install -g memex-cli
```

### 3. 验证安装

```bash
# 运行测试
python test_phase2.py
python test_phase3.py
python test_phase4.py

# 运行系统
python master_orchestrator.py "运行 git status"
```

---

## 项目结构

```
coding_base/
├── master_orchestrator.py       # 主入口（600行）
│
├── commands/                    # 命令执行模块
│   └── command_executor.py      # 200行
│
├── prompts/                     # 提示词模板模块
│   └── prompt_manager.py        # 280行
│
├── agents/                      # 智能体调用模块
│   └── agent_caller.py          # 260行
│
├── skills/                      # 技能系统
│   ├── skill_registry.py        # 技能注册表 (320行)
│   │
│   ├── multcode-dev-workflow-agent/
│   │   ├── SKILL.md
│   │   └── auto_workflow.py     # 5阶段工作流 (450行)
│   │
│   └── cross-backend-orchestrator/
│       ├── SKILL.md
│       └── scripts/
│           ├── orchestrator.py     # 后端协调器 (500行)
│           └── event_parser.py     # 事件解析器 (300行)
│
├── tests/                       # 测试文件
│   ├── test_phase2.py           # Phase 2 测试
│   ├── test_phase3.py           # Phase 3 测试
│   └── test_phase4.py           # Phase 4 测试
│
└── docs/                        # 文档（建议）
    ├── README.md
    ├── USER_GUIDE.md
    ├── ARCHITECTURE.md
    └── CONTRIBUTING.md (本文档)
```

---

## 开发工作流

### 1. 创建功能分支

```bash
# 从 main 创建分支
git checkout -b feature/your-feature-name

# 或修复 bug
git checkout -b fix/issue-123
```

### 2. 开发和测试

```bash
# 进行修改
# ...

# 运行相关测试
python test_phase3.py  # 如果修改了 Phase 3 模块

# 运行所有测试
python test_phase2.py && python test_phase3.py && python test_phase4.py

# 代码格式化
black master_orchestrator.py

# 代码检查
flake8 master_orchestrator.py
mypy master_orchestrator.py
```

### 3. 提交变更

```bash
# 暂存修改
git add .

# 提交（遵循提交规范）
git commit -m "feat: add new execution mode for translation"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 访问你的 GitHub fork
2. 点击 "New Pull Request"
3. 填写 PR 描述（参考模板）
4. 等待 review

---

## 代码规范

### Python 代码风格

我们遵循 **PEP 8** 和一些额外约定：

#### 1. 格式化

使用 **Black** 自动格式化：

```bash
black master_orchestrator.py commands/ prompts/ agents/ skills/
```

**配置** (pyproject.toml):
```toml
[tool.black]
line-length = 100
target-version = ['py38']
```

#### 2. 导入顺序

```python
# 1. 标准库
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 2. 第三方库
import chardet

# 3. 本地模块
from orchestrator import BackendOrchestrator
from skill_registry import SkillRegistry
```

#### 3. 类型提示

**必须**为所有函数添加类型提示：

```python
# ✓ 好
def process(self, request: str, verbose: bool = False) -> TaskResult:
    pass

# ✗ 不好
def process(self, request, verbose=False):
    pass
```

#### 4. 文档字符串

使用 **Google Style** 文档字符串：

```python
def execute_stage(self, stage: WorkflowStage, requirement: str) -> StageResult:
    """
    执行单个工作流阶段

    Args:
        stage: 阶段类型
        requirement: 用户需求描述

    Returns:
        StageResult: 阶段执行结果

    Raises:
        ValueError: 如果阶段配置无效
        TimeoutError: 如果执行超时
    """
    pass
```

#### 5. 命名约定

```python
# 类名: PascalCase
class IntentAnalyzer:
    pass

# 函数/方法: snake_case
def analyze_intent(request: str):
    pass

# 常量: UPPER_SNAKE_CASE
MAX_TIMEOUT = 600

# 私有方法: _leading_underscore
def _internal_helper(self):
    pass
```

#### 6. 错误处理

明确捕获异常类型，避免裸 `except`:

```python
# ✓ 好
try:
    result = self.execute()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return None
except TimeoutError:
    logger.warning("Operation timed out")
    return None

# ✗ 不好
try:
    result = self.execute()
except:
    return None
```

---

## 测试指南

### 测试结构

每个 Phase 有对应的测试文件：

- `test_phase2.py` - IntentAnalyzer, ExecutionRouter 路由逻辑
- `test_phase3.py` - CommandExecutor, PromptManager, AgentCaller
- `test_phase4.py` - DevWorkflowAgent, SkillRegistry

### 编写测试

#### 1. 单元测试

测试单个函数/方法：

```python
def test_intent_analyzer_command_mode():
    """测试命令模式识别"""
    analyzer = IntentAnalyzer()

    # 测试用例
    test_cases = [
        ("运行 git status", ExecutionMode.COMMAND),
        ("执行 npm test", ExecutionMode.COMMAND),
        ("run pytest", ExecutionMode.COMMAND),
    ]

    for request, expected_mode in test_cases:
        intent = analyzer.analyze(request)
        assert intent.mode == expected_mode, f"Failed for: {request}"
```

#### 2. 集成测试

测试多个模块协作：

```python
def test_full_workflow():
    """测试完整工作流"""
    orch = MasterOrchestrator(parse_events=False, timeout=60)

    # 执行请求
    result = orch.process("运行 git status")

    # 验证结果
    assert isinstance(result, CommandResult)
    assert result.success
    assert "branch" in result.output.lower() or "status" in result.output.lower()
```

#### 3. Mock 外部依赖

对于调用 memex-cli 的测试，使用 Mock：

```python
from unittest.mock import patch, MagicMock

def test_backend_call_with_mock():
    """测试后端调用（使用 Mock）"""
    with patch('subprocess.Popen') as mock_popen:
        # 配置 Mock
        mock_process = MagicMock()
        mock_process.stdout.read.return_value = b'{"type": "text", "content": "Test"}'
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # 执行测试
        orch = BackendOrchestrator(parse_events=False)
        result = orch.run_task("claude", "Test prompt")

        # 验证
        assert result.success
        mock_popen.assert_called_once()
```

### 运行测试

```bash
# 运行单个测试文件
python test_phase3.py

# 运行所有测试
python test_phase2.py && python test_phase3.py && python test_phase4.py

# 使用 pytest（如果安装）
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=. --cov-report=html
```

### 测试覆盖率要求

- **新功能**: 覆盖率 ≥ 80%
- **关键模块**: 覆盖率 ≥ 90%（IntentAnalyzer, ExecutionRouter, DevWorkflowAgent）

---

## 提交规范

我们使用 **Conventional Commits** 规范：

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(router): add translation mode` |
| `fix` | Bug 修复 | `fix(parser): handle UTF-16 encoding` |
| `docs` | 文档更新 | `docs: update README with examples` |
| `style` | 代码格式（不影响功能） | `style: format with black` |
| `refactor` | 重构 | `refactor(analyzer): simplify regex patterns` |
| `test` | 测试相关 | `test: add tests for PromptManager` |
| `chore` | 构建/工具相关 | `chore: update dependencies` |

### Scope（可选）

- `router` - ExecutionRouter
- `analyzer` - IntentAnalyzer
- `workflow` - DevWorkflowAgent
- `command` - CommandExecutor
- `prompt` - PromptManager
- `agent` - AgentCaller
- `registry` - SkillRegistry
- `backend` - BackendOrchestrator
- `parser` - EventParser

### 示例

```bash
# 添加新功能
git commit -m "feat(router): add translation execution mode"

# 修复 Bug
git commit -m "fix(parser): handle UTF-16 LE encoding on Windows

- Add automatic encoding detection
- Fall back to chardet if UTF-8 fails
- Add tests for different encodings"

# 文档更新
git commit -m "docs: add examples for custom templates"

# 重构
git commit -m "refactor(analyzer): extract pattern matching to separate method"
```

---

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/YOUR_REPO/issues) 中搜索是否已存在
2. 如果没有，创建新 issue
3. 使用 Bug Report 模板
4. 提供详细信息：
   - 重现步骤
   - 预期行为
   - 实际行为
   - 环境信息（OS, Python 版本等）
   - 错误日志

**Issue 模板示例**:

```markdown
**描述 Bug**
简要描述 bug

**重现步骤**
1. 运行 `python master_orchestrator.py "..."`
2. 看到错误 `...`

**预期行为**
应该输出 `...`

**实际行为**
输出了 `...`

**环境信息**
- OS: Windows 10
- Python: 3.9.7
- memex-cli: 1.0.0

**错误日志**
```
[错误日志粘贴在这里]
```
```

### 请求新功能

1. 创建 Feature Request issue
2. 描述功能需求和使用场景
3. 如果可能，提供伪代码或设计草图

**Feature Request 模板**:

```markdown
**功能描述**
简要描述你希望添加的功能

**使用场景**
为什么需要这个功能？解决什么问题？

**建议的实现方式**
如果有想法，描述如何实现

**替代方案**
是否考虑过其他方案？
```

### 贡献代码

1. **小改动**（文档、注释、小 bug 修复）：
   - 直接提交 PR

2. **大改动**（新功能、重构）：
   - 先创建 issue 讨论
   - 达成一致后再开发
   - 提交 PR

### Pull Request 流程

1. **Fork** 仓库
2. **创建分支** (`git checkout -b feature/amazing-feature`)
3. **开发**并**测试**
4. **提交** (`git commit -m 'feat: add amazing feature'`)
5. **推送** (`git push origin feature/amazing-feature`)
6. **创建 PR**

**PR 描述模板**:

```markdown
## 变更类型
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring
- [ ] Documentation

## 变更描述
简要描述做了什么改动

## 相关 Issue
Closes #123

## 测试
描述如何测试这些改动

- [ ] 添加了新的测试
- [ ] 所有现有测试通过
- [ ] 手动测试通过

## Checklist
- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG（如果适用）
```

---

## 常见任务

### 添加新的执行模式

参考: [ARCHITECTURE.md - 扩展性设计 - 添加新的执行模式](ARCHITECTURE.md#1-添加新的执行模式)

**步骤概览**:
1. 在 `ExecutionMode` 枚举添加新模式
2. 在 `IntentAnalyzer` 添加识别规则
3. 在 `ExecutionRouter` 添加 `_execute_*` 方法
4. 实现执行器模块
5. 添加测试
6. 更新文档

### 添加新的提示词模板

**文件**: `prompts/prompt_manager.py`

**步骤**:

```python
# 1. 定义模板
new_template = PromptTemplate(
    name="your-template-name",
    category="your-category",
    description="模板描述",
    template="""你的提示词模板
变量: {variable1}, {variable2}
""",
    variables=["variable1", "variable2"],
    optional_vars={"variable3": "默认值"}
)

# 2. 在 PromptManager.__init__ 中注册
class PromptManager:
    def __init__(self):
        self.templates = {
            # ... 现有模板
            "your-template-name": new_template,
        }
```

**测试**:

```python
def test_new_template():
    manager = PromptManager()
    result = manager.render(
        "your-template-name",
        variable1="value1",
        variable2="value2"
    )
    assert "value1" in result
    assert "value2" in result
```

### 添加新的 AI 后端

**文件**: `skills/cross-backend-orchestrator/scripts/orchestrator.py`

**步骤**:

```python
# 1. 添加到支持列表
SUPPORTED_BACKENDS = ["claude", "gemini", "codex", "your-new-backend"]

# 2. 配置 memex-cli
# $ memex-cli backends add your-new-backend --api-key YOUR_KEY

# 3. 更新后端选择逻辑（可选）
class ExecutionRouter:
    def _select_backend(self, intent: Intent) -> str:
        if intent.task_type == "your-task-type":
            return "your-new-backend"
        # ...
```

### 添加新的工作流阶段

**文件**: `skills/multcode-dev-workflow-agent/auto_workflow.py`

参考: [ARCHITECTURE.md - 扩展性设计 - 添加新的工作流阶段](ARCHITECTURE.md#3-添加新的工作流阶段)

**步骤**:
1. 在 `WorkflowStage` 枚举添加
2. 在 `STAGE_CONFIG` 配置
3. 在 `StageValidator` 添加验证器
4. 更新 `stage_order` 列表（如果需要调整顺序）

### 调试提示

#### 1. 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. 使用 verbose 模式

```bash
python master_orchestrator.py "你的请求" --verbose
```

#### 3. 检查意图分析

```python
from master_orchestrator import IntentAnalyzer

analyzer = IntentAnalyzer()
intent = analyzer.analyze("你的请求")

print(f"模式: {intent.mode}")
print(f"任务类型: {intent.task_type}")
print(f"复杂度: {intent.complexity}")
```

#### 4. 单独测试执行器

```python
# 测试 CommandExecutor
from command_executor import CommandExecutor
executor = CommandExecutor()
result = executor.execute("运行 git status")
print(result)

# 测试 PromptManager
from prompt_manager import PromptManager
manager = PromptManager()
rendered = manager.render("code-generation", requirement="...", tech_stack="...", language="...")
print(rendered)
```

---

## 开发资源

### 文档

- [README.md](README.md) - 项目概览
- [USER_GUIDE.md](USER_GUIDE.md) - 详细使用指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构
- [CONTRIBUTING.md](CONTRIBUTING.md) - 本文档

### 实现文档

- [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) - Phase 2 实施总结
- [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md) - Phase 3 实施总结
- [PHASE4_IMPLEMENTATION.md](PHASE4_IMPLEMENTATION.md) - Phase 4 实施总结

### 外部资源

- [PEP 8](https://pep8.org/) - Python 代码风格指南
- [Black](https://black.readthedocs.io/) - 代码格式化工具
- [pytest](https://docs.pytest.org/) - 测试框架
- [Conventional Commits](https://www.conventionalcommits.org/) - 提交规范

---

## 社区

### 行为准则

我们致力于提供一个友好、安全和包容的环境。请遵守以下原则：

1. **尊重他人** - 不同意见是正常的，保持礼貌
2. **建设性反馈** - 提供清晰、有帮助的反馈
3. **包容差异** - 尊重不同背景和经验水平的贡献者
4. **专注技术** - 避免人身攻击和离题讨论

### 获取帮助

- **GitHub Issues** - 报告 bug 或请求功能
- **GitHub Discussions** - 提问和讨论
- **Email** - maintainer@example.com

---

## 维护者

- **主要维护者**: @maintainer-username
- **代码审查**: @reviewer-username

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**感谢你的贡献！** 🎉

每一个贡献，无论大小，都让 MasterOrchestrator 变得更好。

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-04
