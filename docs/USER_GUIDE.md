# MasterOrchestrator 用户指南

本指南提供 MasterOrchestrator 的详细使用说明、最佳实践和高级配置选项。

## 目录

- [安装和配置](#安装和配置)
- [基础使用](#基础使用)
- [5种执行模式详解](#5种执行模式详解)
- [5阶段工作流详解](#5阶段工作流详解)
- [API 编程指南](#api-编程指南)
- [高级配置](#高级配置)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)
- [常见问题](#常见问题)

---

## 安装和配置

### 系统要求

- **Python**: 3.8 或更高版本
- **Node.js**: 14.0 或更高版本（用于 memex-cli）
- **操作系统**: Windows, macOS, Linux

### 安装步骤

#### 方式 1: 通过 Claude Code Plugin Marketplace（推荐）

**一键安装**：

在 Claude Code 中运行以下命令：

```
/plugin coding-workflow
```

插件会自动安装所有 21 个 Skills、36 个 Agents 和 47 个 Commands。

**依赖安装**：

插件启动时会自动检查依赖。如有缺失，会显示安装提示：

```bash
# 安装 memex-cli (必需)
npm install -g memex-cli

# 安装 Python 依赖
pip install chardet pyyaml
```

**依赖检查机制**：

- **自动检查**: 每次会话启动时自动执行（24 小时内只检查一次）
- **缓存优化**: 检查结果缓存到 `~/.claude/coding-workflow-deps-check.txt`
- **友好提示**: 依赖缺失时显示清晰的安装指令，但允许继续使用插件

**配置（可选）**：

如需自定义配置（如指定 memex-cli 路径），复制配置模板：

```bash
cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
```

然后编辑 `~/.claude/coding-workflow.local.md` 修改配置项。

**配置示例**：

```yaml
---
memexCliPath: "memex-cli"  # 默认从 PATH 查找
---

# 自定义路径示例
# macOS/Linux:
# memexCliPath: "/usr/local/bin/memex-cli"
#
# Windows:
# memexCliPath: "C:\\Program Files\\nodejs\\memex-cli.cmd"
```

**验证安装**：

安装完成后，重启 Claude Code 会话，插件会自动执行依赖检查并显示状态消息。

---

#### 方式 2: 手动安装（开发者模式）

**1. 克隆项目**

```bash
git clone https://github.com/chaorenex1/coding-workflow.git
cd coding-workflow
```

**2. 安装 Python 依赖**

```bash
# 可选依赖（用于编码检测和配置解析）
pip install chardet pyyaml
```

**3. 安装 memex-cli（必需）**

```bash
# 全局安装
npm install -g memex-cli

# 验证安装
memex-cli --version
```

**4. 配置后端

MasterOrchestrator 支持三个 AI 后端：

- **Claude** - 用于需求分析、功能设计
- **Gemini** - 用于 UX 设计
- **Codex** (deepseek-reasoner) - 用于代码生成

确保在 memex-cli 中配置了这些后端：

```bash
# 查看已配置的后端
memex-cli backends list

# 配置新后端（如果需要）
memex-cli backends add claude --api-key YOUR_API_KEY
```

**5. 验证安装**

```bash
cd /path/to/coding_base
python master_orchestrator.py "运行 git status"
```

如果看到 git status 的输出，说明安装成功。

---

### 插件配置说明

#### 配置文件

**位置**: `~/.claude/coding-workflow.local.md`

**作用**: 自定义插件行为（可选，默认配置开箱即用）

**创建配置文件**:

```bash
cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
```

#### 支持的配置项

##### memexCliPath

**说明**: memex-cli 可执行文件的路径

**默认值**: `"memex-cli"` (从系统 PATH 中查找)

**何时需要修改**:
- memex-cli 不在系统 PATH 中
- 使用了自定义安装路径
- 需要指定特定版本的 memex-cli

**示例**:

```yaml
---
# macOS/Linux
memexCliPath: "/usr/local/bin/memex-cli"

# Windows
memexCliPath: "C:\\Program Files\\nodejs\\memex-cli.cmd"
---
```

#### 未来配置项（规划中）

以下配置项将在未来版本中支持：

```yaml
---
memexCliPath: "memex-cli"
enabledBackends:
  - claude
  - gemini
  - codex
defaultModel: "claude-sonnet-4-5"
logLevel: "info"  # debug | info | warn | error
---
```

---

## 基础使用

### CLI 命令格式

```bash
python master_orchestrator.py "<请求描述>" [选项]
```

**选项**：

- `--verbose` / `-v` - 详细输出（显示意图分析、阶段进度等）
- `--timeout <秒数>` - 设置超时时间（默认 600 秒）

### 简单示例

```bash
# 查询信息
python master_orchestrator.py "分析这段代码的性能"

# 执行命令
python master_orchestrator.py "运行 npm test"

# 代码审查
python master_orchestrator.py "代码审查 src/auth.py"

# 复杂开发任务
python master_orchestrator.py "开发一个博客系统" --verbose
```

### Python API 使用

```python
from master_orchestrator import MasterOrchestrator

# 创建实例
orch = MasterOrchestrator(parse_events=True, timeout=600)

# 处理请求
result = orch.process("你的需求", verbose=False)

# 检查结果类型
if result.success:
    print(f"任务完成: {result.get_final_output()[:100]}")
else:
    print(f"任务失败: {result.error}")
```

---

## 5种执行模式详解

MasterOrchestrator 自动分析用户请求，路由到最合适的执行模式。

### 1. Command 模式 - 命令执行

**适用场景**：执行 Shell 命令

**触发条件**：
- 请求包含 "运行"、"执行"、"run"、"execute" 等关键词
- 请求提到具体命令名（git, npm, pytest 等）

**示例**：

```bash
# 示例 1: 明确的命令请求
python master_orchestrator.py "运行 git status"
# → 执行: git status

# 示例 2: 自然语言描述
python master_orchestrator.py "查看 git 状态"
# → 解析为: git status

# 示例 3: 运行测试
python master_orchestrator.py "运行项目测试"
# → 解析为: pytest 或 npm test（根据项目类型）

# 示例 4: Docker 命令
python master_orchestrator.py "启动 Docker 容器"
# → 解析为: docker-compose up
```

**安全机制**：

1. **命令白名单** - 只允许安全的命令
2. **危险模式检测** - 拒绝 `rm -rf /`, `mkfs` 等危险操作
3. **参数验证** - 检查命令参数的合法性

**白名单命令**：

```
git, npm, npx, yarn, pnpm
python, python3, pytest, pip
docker, docker-compose
node, tsc, eslint
cargo, rustc
go, make, cmake
```

**Python API**：

```python
from command_executor import CommandExecutor

executor = CommandExecutor(timeout=60)

# 直接执行
result = executor.execute("运行 git status")

if result.success:
    print(result.output)
    print(f"退出码: {result.return_code}")
else:
    print(f"错误: {result.error}")
```

---

### 2. Agent 模式 - 智能体调用

**适用场景**：代码库探索、规划、复杂分析

**触发条件**：
- 包含 "查找"、"搜索"、"探索"、"find"、"search"
- 包含 "规划"、"设计"、"计划"、"plan"

**支持的智能体类型**：

| 类型 | 用途 | 触发关键词 |
|------|------|------------|
| **Explore** | 代码库探索 | 查找、搜索、探索、where |
| **Plan** | 任务规划 | 规划、设计、计划、plan |
| **General** | 通用任务 | 其他 |

**示例**：

```bash
# 示例 1: 代码探索（触发 Explore Agent）
python master_orchestrator.py "查找所有的 API 端点"
# → Explore Agent 扫描代码库，返回所有 API 路由

# 示例 2: 错误定位
python master_orchestrator.py "查找认证相关的代码"
# → 返回: src/auth.py:45, src/middleware/auth.js:12 等

# 示例 3: 任务规划（触发 Plan Agent）
python master_orchestrator.py "规划如何实现用户登录功能"
# → Plan Agent 生成实施计划

# 示例 4: 通用分析（触发 General Agent）
python master_orchestrator.py "分析这段代码的复杂度"
# → General Agent 执行分析
```

**Python API**：

```python
from agent_caller import AgentCaller, AgentRequest, AgentType

caller = AgentCaller(claude_code_available=True)

# 手动指定智能体类型
request = AgentRequest(
    agent_type=AgentType.EXPLORE,
    prompt="查找所有数据库查询",
    thoroughness="medium"  # quick, medium, very thorough
)

result = caller.call_agent(request)

if result.success:
    print(result.output)
else:
    print(f"错误: {result.error}")
```

**Thoroughness 级别**：

- `quick` - 快速搜索，适合简单查询
- `medium` - 中等深度，平衡速度和完整性（默认）
- `very thorough` - 深度搜索，多位置、多命名约定

---

### 3. Prompt 模式 - 模板化提示词

**适用场景**：使用专业模板进行代码生成、审查、文档等

**触发条件**：
- 请求包含模板关键词（"生成"、"审查"、"文档" 等）

**8 个专业模板**：

| 模板名称 | 用途 | 示例请求 |
|----------|------|----------|
| **code-generation** | 代码生成 | "生成用户登录功能" |
| **code-review** | 代码审查 | "代码审查 src/auth.py" |
| **documentation** | 文档生成 | "生成 API 文档" |
| **bug-analysis** | Bug 分析 | "分析登录失败的 bug" |
| **refactoring** | 重构建议 | "重构这段代码" |
| **test-generation** | 测试生成 | "生成单元测试" |
| **api-design** | API 设计 | "设计 RESTful API" |
| **performance-optimization** | 性能优化 | "优化数据库查询性能" |

**示例**：

```bash
# 示例 1: 代码生成
python master_orchestrator.py "生成用户注册功能，使用 Python Flask"
# → 使用 code-generation 模板，生成完整代码

# 示例 2: 代码审查
python master_orchestrator.py "代码审查：审查 src/auth.py 的安全性"
# → 使用 code-review 模板，生成专业审查报告

# 示例 3: 文档生成
python master_orchestrator.py "生成 API 文档，格式为 OpenAPI 3.0"
# → 使用 documentation 模板

# 示例 4: Bug 分析
python master_orchestrator.py "分析为什么登录总是失败"
# → 使用 bug-analysis 模板
```

**Python API**：

```python
from prompt_manager import PromptManager

manager = PromptManager()

# 列出所有模板
templates = manager.list_templates()
for name, template in templates.items():
    print(f"{name}: {template.description}")

# 渲染模板
rendered = manager.render(
    template_name="code-generation",
    requirement="实现用户登录",
    tech_stack="Python Flask",
    language="Python"
)

print(rendered)
```

**自定义模板**：

```python
from prompt_manager import PromptTemplate, PromptManager

# 创建自定义模板
custom_template = PromptTemplate(
    name="my-custom-template",
    category="custom",
    description="我的自定义模板",
    template="""你是一位专家。请完成以下任务：
任务描述：{task}
要求：{requirements}
输出格式：{format}
""",
    variables=["task", "requirements", "format"]
)

# 注册模板
manager = PromptManager()
manager.register_template(custom_template)

# 使用模板
result = manager.render(
    "my-custom-template",
    task="分析代码",
    requirements="找出性能瓶颈",
    format="Markdown"
)
```

---

### 4. Skill 模式 - 多阶段工作流

**适用场景**：复杂的、需要多阶段处理的开发任务

**触发条件**：
- 任务复杂度为 `complex`
- 任务类型为 `dev`（开发）
- 或明确提到 "multcode-dev-workflow-agent"

**自动执行 5 个阶段**：

```
阶段 1: 需求分析 (Requirements) → Claude
阶段 2: 功能设计 (Feature Design) → Claude
阶段 3: UX 设计 (UX Design) → Gemini
阶段 4: 开发计划 (Dev Plan) → Codex
阶段 5: 代码实现 (Implementation) → Codex
```

**示例**：

```bash
# 示例 1: 开发完整系统
python master_orchestrator.py "开发一个博客系统，支持文章发布、评论、用户管理" --verbose

# 输出：
# [意图分析]
#   模式: skill
#   类型: dev
#   复杂度: complex
#
# [工作流执行]
# 阶段 1/5: requirements
#   后端: claude
#   ✓ 验证通过 (45.3s)
# 阶段 2/5: feature_design
#   后端: claude
#   ✓ 验证通过 (62.1s)
# ...
# [工作流执行完成]
# 成功: True
# 完成阶段: 5/5
# 总耗时: 450.2s

# 示例 2: 电商平台开发
python master_orchestrator.py "实现一个电商小程序，包括商品浏览、购物车、支付功能" -v

# 示例 3: 管理系统开发
python master_orchestrator.py "开发一个内容管理系统（CMS）" -v
```

**Python API**：

```python
from auto_workflow import DevWorkflowAgent, WorkflowStage

# 创建智能体
agent = DevWorkflowAgent(parse_events=True, timeout=600)

# 执行完整工作流
result = agent.run("开发一个用户管理系统", verbose=True)

# 检查结果
print(f"成功: {result.success}")
print(f"完成阶段: {result.completed_stages}/5")
print(f"总耗时: {result.total_duration_seconds:.2f}s")

if result.success:
    # 获取各阶段输出
    requirements = result.get_stage_result(WorkflowStage.REQUIREMENTS)
    feature_design = result.get_stage_result(WorkflowStage.FEATURE_DESIGN)
    implementation = result.get_stage_result(WorkflowStage.IMPLEMENTATION)

    print(f"\n需求分析:\n{requirements.output[:200]}...\n")
    print(f"\n最终实现:\n{implementation.output[:500]}...\n")
else:
    print(f"失败阶段: {result.failed_stage.value}")
    failed_result = result.get_stage_result(result.failed_stage)
    print(f"错误: {failed_result.error}")
```

**从特定阶段恢复**：

```python
# 从阶段 3 重新开始（假设前两个阶段已完成）
result = agent.run(
    requirement="开发电商系统",
    start_from=WorkflowStage.UX_DESIGN,
    verbose=True
)
```

---

### 5. Backend 模式 - 直接后端调用

**适用场景**：简单查询、解释、分析

**触发条件**：
- 不符合其他模式的通用请求

**示例**：

```bash
# 示例 1: 代码解释
python master_orchestrator.py "解释这段 Python 代码是做什么的"
# → 直接调用 Claude 后端

# 示例 2: 技术咨询
python master_orchestrator.py "什么是 OAuth 2.0？"
# → 调用 Claude 后端

# 示例 3: 简单分析
python master_orchestrator.py "这个函数的时间复杂度是多少？"
# → 调用后端分析
```

**Python API**：

```python
from orchestrator import BackendOrchestrator

orch = BackendOrchestrator(parse_events=True, timeout=300)

# 指定后端
result = orch.run_task(
    backend="claude",
    prompt="解释什么是依赖注入",
    stream_format="jsonl"
)

if result.success:
    print(result.get_final_output())
    print(f"Run ID: {result.run_id}")
```

---

## 5阶段工作流详解

当检测到复杂开发任务时，DevWorkflowAgent 自动执行 5 个阶段。

### 阶段 1: 需求分析 (Requirements)

**目标**: 从用户描述中提炼清晰、可执行的需求

**后端**: Claude

**输出内容**:
1. 核心需求提炼
2. 用户画像和使用场景
3. 功能优先级排序
4. 成功指标定义
5. 风险和约束条件

**验证规则**:
- 输出长度 ≥ 20 字符

**示例输出**:

```
核心需求：
- 用户可以浏览商品列表
- 用户可以将商品添加到购物车
- 用户可以完成在线支付

用户画像：
- 主要用户：18-35 岁的网购用户
- 使用场景：移动端为主，PC 端为辅

功能优先级：
1. P0: 商品浏览、购物车、支付
2. P1: 用户注册、订单管理
3. P2: 评论、推荐

成功指标：
- 页面加载时间 < 2 秒
- 支付成功率 > 95%
```

---

### 阶段 2: 功能设计 (Feature Design)

**目标**: 基于需求设计系统架构和功能模块

**后端**: Claude

**输入**: 阶段 1 的需求分析结果

**输出内容**:
1. 功能模块划分
2. 模块间的接口设计
3. 数据模型设计
4. 技术栈选择建议
5. 架构图（文字描述）

**验证规则**:
- 输出长度 ≥ 20 字符

**示例输出**:

```
功能模块划分：
1. 商品模块 (ProductModule)
   - 商品列表展示
   - 商品详情查看
   - 商品搜索

2. 购物车模块 (CartModule)
   - 添加/删除商品
   - 数量调整
   - 价格计算

3. 支付模块 (PaymentModule)
   - 订单生成
   - 支付接口集成
   - 支付状态跟踪

数据模型：
- Product: id, name, price, stock, images
- Cart: user_id, items[], total_price
- Order: id, user_id, items[], status, payment_info

技术栈建议：
- 前端: Vue.js + Vant UI
- 后端: Python Flask + SQLAlchemy
- 数据库: PostgreSQL
- 支付: 微信支付 API
```

---

### 阶段 3: UX 设计 (UX Design)

**目标**: 设计用户界面和交互流程

**后端**: Gemini（擅长视觉和设计）

**输入**: 阶段 2 的功能设计结果

**输出内容**:
1. 用户界面布局设计
2. 交互流程设计
3. 关键页面线框图（文字描述）
4. 视觉设计建议（色彩、字体、组件）
5. 可用性和可访问性考虑

**验证规则**:
- 输出长度 ≥ 20 字符

**示例输出**:

```
页面布局设计：

1. 商品列表页
   - 顶部: 搜索框 + 筛选按钮
   - 中部: 商品卡片网格（2 列）
   - 底部: 分页导航

2. 商品详情页
   - 顶部: 商品图片轮播
   - 中部: 商品信息（名称、价格、描述）
   - 底部: "加入购物车" 按钮

3. 购物车页
   - 商品列表（可滑动删除）
   - 总价显示
   - "去结算" 按钮

交互流程：
1. 用户点击商品 → 进入详情页
2. 点击"加入购物车" → Toast 提示 + 购物车图标动画
3. 购物车页点击"结算" → 跳转支付页

视觉设计：
- 主色调: #FF6B6B (活力橙红)
- 辅助色: #4ECDC4 (清新蓝绿)
- 字体: 系统默认 Sans-serif
- 圆角: 8px
- 阴影: 0 2px 8px rgba(0,0,0,0.1)
```

---

### 阶段 4: 开发计划 (Dev Plan)

**目标**: 制定详细的开发计划和任务清单

**后端**: Codex (deepseek-reasoner)

**输入**: 阶段 2 的功能设计 + 阶段 3 的 UX 设计

**输出内容**:
1. 开发阶段划分和里程碑
2. 每个阶段的任务清单
3. 技术选型和依赖管理
4. 测试策略（单元测试、集成测试）
5. 部署和运维计划

**验证规则**:
- 输出长度 ≥ 20 字符

**示例输出**:

```
开发阶段划分：

Sprint 1 (Week 1-2): 基础架构
- [ ] 搭建 Flask 项目框架
- [ ] 配置数据库（PostgreSQL）
- [ ] 实现用户认证（JWT）
- [ ] 编写基础 API（CRUD）

Sprint 2 (Week 3-4): 核心功能
- [ ] 实现商品模块 API
- [ ] 实现购物车逻辑
- [ ] 集成支付 API
- [ ] 编写单元测试

Sprint 3 (Week 5-6): 前端开发
- [ ] 商品列表页组件
- [ ] 商品详情页组件
- [ ] 购物车页组件
- [ ] 支付流程集成

Sprint 4 (Week 7): 测试和优化
- [ ] 集成测试
- [ ] 性能优化
- [ ] 安全审计
- [ ] 部署到测试环境

技术选型：
- Flask==2.3.0
- SQLAlchemy==2.0.0
- Vue.js 3.x
- Vant UI 4.x
- PostgreSQL 14

测试策略：
- 单元测试覆盖率 > 80%
- 集成测试覆盖核心流程
- 使用 pytest + pytest-cov
```

---

### 阶段 5: 代码实现 (Implementation)

**目标**: 生成核心功能的代码实现

**后端**: Codex (deepseek-reasoner)

**输入**: 阶段 4 的开发计划

**输出内容**:
1. 核心功能的代码实现
2. 关键模块的代码示例
3. 配置文件示例
4. 测试用例示例
5. 部署脚本示例

**验证规则**:
- 输出长度 ≥ 100 字符（代码通常较长）

**示例输出**:

```python
# 商品模块 - models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'stock': self.stock,
            'description': self.description
        }

# 商品模块 - routes.py
from flask import Blueprint, request, jsonify
from models import Product, db

product_bp = Blueprint('products', __name__)

@product_bp.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    products = Product.query.paginate(page=page, per_page=per_page)

    return jsonify({
        'products': [p.to_dict() for p in products.items],
        'total': products.total,
        'pages': products.pages
    })

# 测试用例 - test_products.py
def test_get_products(client):
    response = client.get('/api/products?page=1&per_page=10')
    assert response.status_code == 200
    data = response.get_json()
    assert 'products' in data
    assert isinstance(data['products'], list)
```

---

## API 编程指南

### MasterOrchestrator API

```python
from master_orchestrator import MasterOrchestrator

# 初始化
orch = MasterOrchestrator(
    parse_events=True,  # 是否解析事件流
    timeout=600         # 超时时间（秒）
)

# 处理请求
result = orch.process("你的需求", verbose=False)

# 判断结果类型
from auto_workflow import WorkflowResult
from orchestrator import TaskResult

if isinstance(result, WorkflowResult):
    # 5阶段工作流结果
    handle_workflow_result(result)
elif isinstance(result, TaskResult):
    # 单次任务结果
    handle_task_result(result)
elif isinstance(result, CommandResult):
    # 命令执行结果
    handle_command_result(result)
elif isinstance(result, AgentResult):
    # 智能体调用结果
    handle_agent_result(result)
```

### 结果类型详解

#### WorkflowResult

```python
@dataclass
class WorkflowResult:
    requirement: str                    # 原始需求
    stages: List[StageResult]           # 各阶段结果
    total_duration_seconds: float       # 总耗时
    success: bool                       # 是否成功
    completed_stages: int               # 完成的阶段数
    failed_stage: Optional[WorkflowStage]  # 失败的阶段
    timestamp: str                      # 时间戳

# 使用示例
if result.success:
    print(f"完成 {result.completed_stages}/5 个阶段")
    for stage_result in result.stages:
        print(f"{stage_result.stage.value}: {stage_result.get_summary()}")
else:
    print(f"失败于阶段: {result.failed_stage.value}")
```

#### TaskResult

```python
@dataclass
class TaskResult:
    success: bool                       # 是否成功
    output: str                         # 输出内容
    events: List[Dict[str, Any]]        # 事件列表
    run_id: Optional[str]               # Run ID
    error: Optional[str]                # 错误信息

# 使用示例
if result.success:
    print(result.get_final_output())    # 获取最终输出
    print(f"Run ID: {result.run_id}")
```

#### CommandResult

```python
@dataclass
class CommandResult:
    success: bool                       # 是否成功
    command: str                        # 执行的命令
    output: str                         # 标准输出
    error: str                          # 标准错误
    return_code: int                    # 退出码

# 使用示例
if result.success:
    print(f"命令: {result.command}")
    print(f"输出: {result.output}")
    print(f"退出码: {result.return_code}")
```

#### AgentResult

```python
@dataclass
class AgentResult:
    success: bool                       # 是否成功
    agent_type: AgentType               # 智能体类型
    output: str                         # 输出内容
    error: Optional[str]                # 错误信息

# 使用示例
if result.success:
    print(f"智能体类型: {result.agent_type.value}")
    print(f"输出: {result.output}")
```

---

## 高级配置

### 1. 自定义后端选择逻辑

编辑 `master_orchestrator.py`:

```python
class ExecutionRouter:
    def _select_backend(self, intent: Intent) -> str:
        """自定义后端选择"""
        if intent.task_type == "dev":
            return "codex"  # 开发任务用 Codex
        elif intent.task_type == "ux":
            return "gemini"  # UX 设计用 Gemini
        elif intent.task_type == "analysis":
            return "claude"  # 分析任务用 Claude
        else:
            return "claude"  # 默认
```

### 2. 修改意图分析规则

编辑 `master_orchestrator.py` 中的 `IntentAnalyzer`:

```python
# 添加新的模式规则
self.mode_patterns = {
    ExecutionMode.CUSTOM: [
        (r'自定义关键词', 'custom'),
    ]
}

# 添加新的复杂度规则
def _analyze_complexity(self, request: str) -> str:
    if "非常复杂" in request:
        return "extreme"
    # ...
```

### 3. 自定义工作流阶段

编辑 `skills/multcode-dev-workflow-agent/auto_workflow.py`:

```python
# 添加新阶段
class WorkflowStage(Enum):
    # ... 现有阶段
    DEPLOYMENT = "deployment"  # 新增部署阶段

# 配置新阶段
STAGE_CONFIG = {
    # ... 现有配置
    WorkflowStage.DEPLOYMENT: {
        "backend": "codex",
        "validator": StageValidator.validate_deployment,
        "prompt_template": """部署计划提示词..."""
    }
}
```

### 4. 配置超时和重试

```python
# 全局超时
orch = MasterOrchestrator(timeout=1200)  # 20 分钟

# 单个阶段超时
agent = DevWorkflowAgent(timeout=300)  # 5 分钟/阶段
```

### 5. 日志配置

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 最佳实践

### 1. 请求描述原则

**清晰具体**：
```
❌ "做一个网站"
✓ "开发一个博客系统，支持文章发布、Markdown 编辑、评论功能"
```

**包含关键信息**：
```
❌ "生成代码"
✓ "生成用户登录功能，使用 Python Flask，包括 JWT 认证"
```

**分阶段处理复杂任务**：
```python
# 方式 1: 一次性完整开发（自动 5 阶段）
orch.process("开发完整的电商系统")

# 方式 2: 分步骤执行
orch.process("分析电商系统的需求")  # 先分析
# ... 审阅后 ...
orch.process("设计电商系统的功能架构")  # 再设计
```

### 2. 模式选择建议

| 任务类型 | 推荐模式 | 示例 |
|----------|----------|------|
| 命令执行 | Command | "运行 git status" |
| 代码探索 | Agent (Explore) | "查找所有 API 端点" |
| 任务规划 | Agent (Plan) | "规划实现登录功能" |
| 代码生成 | Prompt | "生成用户注册代码" |
| 代码审查 | Prompt | "代码审查 src/auth.py" |
| 完整开发 | Skill (5阶段) | "开发博客系统" |
| 简单咨询 | Backend | "什么是 OAuth?" |

### 3. 错误处理

```python
try:
    result = orch.process("你的需求", verbose=True)

    if not result.success:
        # 根据错误类型处理
        if "timeout" in str(result.error).lower():
            # 超时 - 增加超时时间重试
            result = orch.process("你的需求", timeout=1200)
        elif "memex-cli not found" in str(result.error):
            # memex-cli 未安装
            print("请先安装 memex-cli: npm install -g memex-cli")
        else:
            # 其他错误
            print(f"错误: {result.error}")

except Exception as e:
    print(f"异常: {e}")
    import traceback
    traceback.print_exc()
```

### 4. 性能优化

**减少超时时间（简单任务）**：
```python
# 简单查询不需要 10 分钟超时
orch = MasterOrchestrator(timeout=60)  # 1 分钟
```

**禁用事件解析（不需要详细日志时）**：
```python
# 事件解析有性能开销
orch = MasterOrchestrator(parse_events=False)
```

**并行处理多个请求**：
```python
from concurrent.futures import ThreadPoolExecutor

requests = [
    "分析代码 A",
    "分析代码 B",
    "分析代码 C"
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(orch.process, requests))
```

---

## 故障排查

### 插件相关问题

#### 问题 1: 插件依赖检查失败

**症状**：
```
[错误] memex-cli not found. 请运行: npm install -g memex-cli
```

**解决方案**：

1. 安装 memex-cli:
   ```bash
   npm install -g memex-cli
   ```

2. 验证安装:
   ```bash
   memex-cli --version
   ```

3. 如已安装但仍报错，配置自定义路径:
   ```bash
   cp docs/coding-workflow.local.example.md ~/.claude/coding-workflow.local.md
   # 编辑 memexCliPath 字段为实际路径
   ```

4. 查找 memex-cli 实际路径:
   ```bash
   # macOS/Linux
   which memex-cli

   # Windows
   where memex-cli
   ```

#### 问题 2: Python 依赖缺失

**症状**：
```
[错误] Python 依赖缺失: chardet, pyyaml
```

**解决方案**：
```bash
pip install chardet pyyaml

# 或使用 pip3
pip3 install chardet pyyaml
```

#### 问题 3: 插件配置不生效

**症状**: 修改了 `~/.claude/coding-workflow.local.md` 但配置未生效

**解决方案**:

1. 确认配置文件位置正确:
   ```bash
   # 查看文件是否存在
   cat ~/.claude/coding-workflow.local.md
   ```

2. 检查 YAML frontmatter 格式:
   ```yaml
   ---
   memexCliPath: "/path/to/memex-cli"
   ---
   ```
   注意：必须有三个连字符包裹，冒号后有空格

3. 重启 Claude Code 会话（配置在会话启动时加载）

#### 问题 4: 依赖检查频繁执行

**症状**: 每次启动 Claude Code 都执行依赖检查

**原因**: 缓存文件不存在或权限错误

**解决方案**:

1. 检查缓存文件:
   ```bash
   ls -la ~/.claude/coding-workflow-deps-check.txt
   ```

2. 如缓存文件不存在，手动创建:
   ```bash
   # macOS/Linux
   echo "$(date +%s)" > ~/.claude/coding-workflow-deps-check.txt

   # Windows (PowerShell)
   [int][double]::Parse((Get-Date -UFormat %s)) | Out-File -Encoding utf8 ~/.claude/coding-workflow-deps-check.txt
   ```

3. 检查文件权限:
   ```bash
   # macOS/Linux - 确保可读写
   chmod 644 ~/.claude/coding-workflow-deps-check.txt
   ```

#### 问题 5: 插件未正确安装

**症状**: 无法使用 `/plugin coding-workflow` 命令或插件功能不可用

**解决方案**:

1. 检查插件是否已安装:
   ```bash
   ls -la ~/.claude/plugins/coding-workflow/
   ```

2. 检查 `plugin.json` 是否存在:
   ```bash
   cat ~/.claude/plugins/coding-workflow/.claude-plugin/plugin.json
   ```

3. 重新安装插件:
   ```
   /plugin uninstall coding-workflow
   /plugin install coding-workflow
   ```

4. 如果仍有问题，尝试手动安装（方式 2）

---

### 系统运行问题

#### 问题 6: memex-cli not found (系统运行时)

**症状**：
```
RuntimeError: memex-cli not found. Please install it first: npm install -g memex-cli
```

**解决方案**：
```bash
# 安装 memex-cli
npm install -g memex-cli

# 验证
memex-cli --version

# 如果权限错误（Linux/Mac）
sudo npm install -g memex-cli
```

---

#### 问题 7: 编码错误（Windows）

**症状**：
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

**解决方案**：
系统已自动处理 UTF-16 LE 编码，无需手动配置。如仍有问题：

```python
# 在 event_parser.py 中已实现自动检测
# 如需手动指定编码：
parser = EventParser(encoding='utf-16-le')
```

---

#### 问题 8: 超时错误

**症状**：
```
TimeoutError: Task execution exceeded 600 seconds
```

**解决方案 1: 增加超时时间**
```bash
python master_orchestrator.py "复杂任务" --timeout 1200
```

**解决方案 2: 简化请求**
```
# 将复杂请求拆分
❌ "开发完整的电商平台，包含前端、后端、数据库、支付、物流..."
✓ "开发电商平台的核心购物流程"
```

---

#### 问题 9: 阶段验证失败

**症状**：
```
[FAIL] 阶段 3: ux_design
错误: Validation failed: UX设计输出过短
```

**解决方案**：

检查后端输出质量，可能原因：
1. 后端配置错误
2. 提示词不够清晰
3. 验证规则过严

调试：
```python
# 禁用验证（仅调试）
def validate_ux_design(output: str):
    return True, None  # 暂时跳过验证
```

---

#### 问题 10: 后端调用失败

**症状**：
```
Backend error: API key invalid
```

**解决方案**：
```bash
# 检查 memex-cli 后端配置
memex-cli backends list

# 重新配置后端
memex-cli backends add claude --api-key YOUR_NEW_KEY

# 测试后端
memex-cli run claude "测试连接"
```

---

## 常见问题

### Q1: 如何判断系统选择了哪种执行模式？

**A**: 使用 `--verbose` 标志：

```bash
python master_orchestrator.py "你的请求" --verbose

# 输出会显示：
# [意图分析]
#   模式: skill
#   类型: dev
#   复杂度: complex
```

---

### Q2: 可以强制指定执行模式吗？

**A**: 可以，通过 Python API：

```python
from master_orchestrator import MasterOrchestrator, ExecutionMode

orch = MasterOrchestrator()

# 强制使用 Command 模式
result = orch.router._execute_command("运行测试")

# 强制使用 Agent 模式
from agents.agent_caller import AgentRequest, AgentType
request = AgentRequest(agent_type=AgentType.EXPLORE, prompt="查找代码")
result = orch.router.agent_caller.call_agent(request)
```

---

### Q3: 如何保存工作流的中间结果？

**A**: 工作流结果包含所有阶段：

```python
result = agent.run("开发系统")

# 保存所有阶段
import json
stages_data = []
for stage_result in result.stages:
    stages_data.append({
        'stage': stage_result.stage.value,
        'output': stage_result.output,
        'duration': stage_result.duration_seconds
    })

with open('workflow_results.json', 'w', encoding='utf-8') as f:
    json.dump(stages_data, f, indent=2, ensure_ascii=False)
```

---

### Q4: 系统支持哪些编程语言？

**A**: MasterOrchestrator 是语言无关的，后端 AI 模型支持：

- Python, JavaScript/TypeScript, Java, C/C++, C#
- Go, Rust, Ruby, PHP, Swift, Kotlin
- Shell, SQL, HTML/CSS
- 以及其他主流语言

---

### Q5: 如何自定义提示词模板？

**A**: 参见 [Prompt 模式 - 自定义模板](#3-prompt-模式---模板化提示词) 部分。

---

### Q6: 5阶段工作流可以跳过某些阶段吗？

**A**: 不建议跳过，但可以从指定阶段开始：

```python
# 从阶段 3 开始（假设阶段 1-2 已完成）
result = agent.run(
    requirement="开发系统",
    start_from=WorkflowStage.UX_DESIGN
)
```

---

### Q7: 如何查看所有可用的技能？

**A**:

```python
from skill_registry import SkillRegistry

registry = SkillRegistry()

# 列出所有技能
for skill in registry.list_skills():
    print(f"{skill.name}: {skill.description}")
    print(f"  类别: {skill.category.value}")
    print(f"  后端: {', '.join(skill.backends_required)}")
```

---

### Q8: 系统对网络有什么要求？

**A**:
- 需要访问 AI 后端 API（Claude, Gemini, Codex）
- 如果后端在本地部署，无需外网
- memex-cli 会处理网络请求

---

### Q9: 如何集成到现有项目？

**A**:

```python
# 方式 1: 作为 Python 模块
from master_orchestrator import MasterOrchestrator
orch = MasterOrchestrator()
result = orch.process("你的需求")

# 方式 2: 作为 CLI 工具
import subprocess
result = subprocess.run(
    ['python', 'master_orchestrator.py', '你的需求'],
    capture_output=True,
    text=True
)
print(result.stdout)
```

---

### Q10: 系统的资源占用如何？

**A**:
- **CPU**: 中等（主要由 memex-cli 和后端决定）
- **内存**: ~200MB
- **磁盘**: 事件日志 ~1MB/任务
- **网络**: 取决于后端 API 调用频率

---

## 下一步

- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
- 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 参与开发
- 访问 [GitHub Issues](https://github.com/your-repo/issues) 报告问题

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-04
