---
name: rust-tauri-ai-app-builder
description: 使用rust-tauri-app-builder智能地创建和配置Tauri桌面应用项目
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
color: green
field: fullstack
expertise: expert
---

## 前置条件
- 熟悉 Rust 编程语言和 Tauri 框架
- 了解前端技术栈（如 Svelte, Vue, React）
- 了解桌面应用开发流程
- 熟悉数据库配置和管理
- 使用rust-tauri-app-builder智能地创建和配置Tauri桌面应用项目


## 需求：代码编辑器与设置管理应用

### 应用概述
一个集成了代码编辑、AI 助手聊天、CLI 日志输出和终端功能的桌面应用，支持多工作区管理和配置自定义。

### 界面设计

#### 1. 编辑器主界面
**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│ 菜单栏 (File Edit View Tools Help)                          │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│              │              编辑器区域                      │
│              │              (可编辑文件内容)                │
│  目录导航    │                                              │
│  (左侧)      │                                              │
│              ├──────────────────────────────────────────────┤
│              │              底部 Tab 区域                   │
│              │   ┌──────┬──────┬──────┬──────┐             │
│              │   │聊天  │输出  │终端  │...   │             │
│              │   └──────┴──────┴──────┴──────┘             │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

**目录导航 (左侧)**：
- 树形结构显示文件系统
- 右键菜单选项：
  - 新建文件/文件夹
  - 重命名
  - 删除
  - 复制路径
  - 在终端中打开
  - 刷新
- 支持拖拽文件/文件夹
- 支持文件搜索过滤

**编辑器区域 (右侧)**：
- 基于 Monaco Editor 或 CodeMirror
- 支持语法高亮（多种编程语言）
- 支持代码折叠
- 支持查找/替换
- 支持多光标编辑
- 支持快捷键：
  - Ctrl+S：保存当前文件
  - Ctrl+Shift+S：保存所有打开的文件
- 右下角操作按钮：
  - 💾 保存当前文件
  - 💾💾 保存所有文件

**底部 Tab 区域**：

**Tab 1: 聊天输入界面**
```
┌─────────────────────────────────────────────────────────────┐
│ 关联按钮 [🔗] 已关联文件: file1.rs | file2.py | ...         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  多行文本输入框                                             │
│  (支持 Markdown 预览)                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 请输入消息...                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                    [清空]          [发送]                   │
├─────────────────────────────────────────────────────────────┤
│ 模型选择: [▽ Claude-3.5-Sonnet]                            │
│ Code CLI: [▽ OpenAI-Codex]                                 │
└─────────────────────────────────────────────────────────────┘
```
- **关联按钮**：点击后可以关联目录导航中的文件，被关联的文件在顶部右侧显示
- **输入框**：支持多行文本，Markdown 实时预览
- **操作按钮**：
  - 清空：清空聊天输入框
  - 发送：将文本发送到后端 AI 模型处理
- **底部操作栏**：
  - 模型选择下拉框：选择 AI 模型（Claude, GPT, Gemini 等）
  - Code CLI 选择下拉框：选择代码生成工具

**Tab 2: 输出界面**
```
┌─────────────────────────────────────────────────────────────┐
│ 搜索框: [____________] [🔍] [清空] [暂停/继续]              │
├─────────────────────────────────────────────────────────────┤
│ 2024-01-15 10:30:25 INFO  - 应用启动成功                    │
│ 2024-01-15 10:30:26 DEBUG - 加载配置文件: config.toml       │
│ 2024-01-15 10:30:27 INFO  - 数据库连接成功                  │
│ 2024-01-15 10:30:28 ERROR - 文件读取失败: /path/to/file     │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
```
- 实时显示 CLI 日志输出
- 支持上下滚动查看历史日志
- 搜索功能：可搜索日志内容
- 控制按钮：
  - 清空：清空所有日志
  - 暂停/继续：暂停或继续日志输出

**Tab 3: 终端界面**
```
┌─────────────────────────────────────────────────────────────┐
│ 终端1 [×] 终端2 [×] 新建 [+]                                │
├─────────────────────────────────────────────────────────────┤
│ user@host:~$ pwd                                            │
│ /home/user/projects                                         │
│ user@host:~$ ls -la                                         │
│ total 48                                                    │
│ drwxr-xr-x  5 user user  4096 Jan 15 10:30 .                │
│ drwxr-xr-x 18 user user  4096 Jan 15 09:15 ..               │
│ drwxr-xr-x  8 user user  4096 Jan 15 10:30 .git             │
│ -rw-r--r--  1 user user   351 Jan 15 10:30 .gitignore       │
│ drwxr-xr-x  2 user user  4096 Jan 15 10:30 src              │
│ drwxr-xr-x  2 user user  4096 Jan 15 10:30 tests            │
│ user@host:~$ █                                              │
└─────────────────────────────────────────────────────────────┘
```
- 嵌入系统终端（xterm.js）
- 支持多标签页终端
- 支持常用终端操作
- 支持复制/粘贴
- 支持调整字体大小

#### 2. 设置界面
**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│ 设置                                                         │
├─────────────────────────────────────────────────────────────┤
│ 工作区设置                                                   │
│  当前工作区: [▽ 工作区1] [切换] [新建] [删除]               │
│                                                             │
│ 应用数据目录                                                 │
│  当前目录: /home/user/.app-data                             │
│  [浏览...] [重置为默认]                                     │
│                                                             │
│ CLI 工具路径设置                                             │
│  Node.js: [/usr/bin/node] [浏览...]                         │
│  Python: [/usr/bin/python3] [浏览...]                       │
│  Git: [/usr/bin/git] [浏览...]                              │
│                                                             │
│ 环境变量设置                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 变量名        变量值                             操作│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ API_KEY      sk-...****************               ✏️🗑️│   │
│  │ PATH         /usr/local/bin:/usr/bin:/bin          ✏️🗑️│   │
│  └─────────────────────────────────────────────────────┘   │
│  [添加环境变量]                                            │
│                                                             │
│ 模型管理                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 模型名称        API端点             API密钥       操作│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Claude-3.5   api.anthropic.com/v1  ********       ✏️🗑️│   │
│  │ GPT-4        api.openai.com/v1     ********       ✏️🗑️│   │
│  └─────────────────────────────────────────────────────┘   │
│  [添加模型]                                               │
│                                                             │
│ Code CLI 管理                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CLI名称        命令路径            参数           操作│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ OpenAI-Codex  /usr/bin/codex      --model gpt-4  ✏️🗑️│   │
│  │ Local-Coder   /usr/local/bin/coder --local        ✏️🗑️│   │
│  └─────────────────────────────────────────────────────┘   │
│  [添加 Code CLI]                                          │
│                                                             │
│                    [保存] [取消] [恢复默认]                 │
└─────────────────────────────────────────────────────────────┘
```

**设置项详情**：
1. **工作区切换**：
   - 下拉选择工作区
   - 支持新建、删除工作区
   - 每个工作区独立配置和数据

2. **应用数据目录切换**：
   - 显示当前数据目录
   - 支持浏览选择新目录
   - 支持重置为默认目录

3. **CLI 工具路径设置**：
   - 常用开发工具路径配置
   - 支持浏览选择
   - 支持路径验证

4. **环境变量设置**：
   - 应用启动时临时设置
   - 应用关闭时自动清除
   - 支持增删改环境变量
   - 敏感信息（API密钥）显示为掩码

5. **模型列表管理**：
   - 支持增删改 AI 模型配置
   - 包含模型名称、API端点、API密钥
   - API密钥加密存储

6. **Code CLI 列表管理**：
   - 支持增删改代码生成工具配置
   - 包含 CLI 名称、命令路径、参数
   - 支持命令验证


### 示例需求项目结构
#### 此项目结构基于rust-tauri-app-builder模板结构，不要改变模板结构，只需在相应目录下添加或修改文件即可。

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── AppLayout.svelte/vue/jsx      # 主布局
│   │   ├── Sidebar.svelte/vue/jsx        # 左侧目录导航
│   │   └── TabBar.svelte/vue/jsx         # 底部 Tab 栏
│   ├── editor/
│   │   ├── CodeEditor.svelte/vue/jsx     # 代码编辑器
│   │   ├── FileTree.svelte/vue/jsx       # 文件树
│   │   └── EditorTabs.svelte/vue/jsx     # 编辑器标签页
│   ├── chat/
│   │   ├── ChatInput.svelte/vue/jsx      # 聊天输入
│   │   ├── ChatHistory.svelte/vue/jsx    # 聊天历史
│   │   └── ModelSelector.svelte/vue/jsx  # 模型选择器
│   ├── terminal/
│   │   ├── TerminalView.svelte/vue/jsx   # 终端视图
│   │   └── TerminalTabs.svelte/vue/jsx   # 终端标签页
│   ├── settings/
│   │   ├── SettingsPanel.svelte/vue/jsx  # 设置面板
│   │   ├── WorkspaceManager.svelte/vue/jsx # 工作区管理
│   │   ├── ModelManager.svelte/vue/jsx   # 模型管理
│   │   └── EnvVarManager.svelte/vue/jsx  # 环境变量管理
│   └── common/
│       ├── Button.svelte/vue/jsx
│       ├── Input.svelte/vue/jsx
│       ├── Select.svelte/vue/jsx
│       └── Modal.svelte/vue/jsx
├── stores/
│   ├── appStore.js/ts                    # 应用状态
│   ├── editorStore.js/ts                 # 编辑器状态
│   ├── chatStore.js/ts                   # 聊天状态
│   ├── terminalStore.js/ts               # 终端状态
│   └── settingsStore.js/ts               # 设置状态
├── services/
│   ├── tauri/
│   │   ├── fileService.js/ts             # 文件操作
│   │   ├── aiService.js/ts               # AI 服务
│   │   ├── terminalService.js/ts         # 终端服务
│   │   └── configService.js/ts           # 配置服务
│   └── utils/
│       ├── fileUtils.js/ts               # 文件工具
│       ├── cryptoUtils.js/ts             # 加密工具
│       └── validationUtils.js/ts         # 验证工具
└── utils/
    ├── constants.js/ts                    # 常量
    ├── shortcuts.js/ts                    # 快捷键
    └── formatters.js/ts                   # 格式化工具
```

### 数据库设计

```sql
-- 工作区配置
CREATE TABLE workspaces (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    data_dir TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型配置
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    api_endpoint TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CLI 工具配置
CREATE TABLE cli_tools (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    command_path TEXT NOT NULL,
    arguments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 环境变量
CREATE TABLE environment_vars (
    id INTEGER PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id),
    key TEXT NOT NULL,
    value_encrypted TEXT NOT NULL,
    UNIQUE(workspace_id, key)
);

-- 文件历史
CREATE TABLE file_history (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聊天历史
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id),
    user_message TEXT NOT NULL,
    ai_response TEXT,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 后端功能需求

#### 1. 文件系统操作
```rust
// src-tauri/src/services/file_service.rs
pub struct FileService;

impl FileService {
    // 列出目录内容
    pub async fn list_directory(path: &str) -> Result<Vec<FileInfo>>;

    // 读取文件内容
    pub async fn read_file(path: &str) -> Result<String>;

    // 保存文件
    pub async fn save_file(path: &str, content: &str) -> Result<()>;

    // 创建文件/目录
    pub async fn create(path: &str, is_dir: bool) -> Result<()>;

    // 重命名文件/目录
    pub async fn rename(old_path: &str, new_path: &str) -> Result<()>;

    // 删除文件/目录
    pub async fn delete(path: &str) -> Result<()>;
}
```

#### 2. AI 聊天服务
```rust
// src-tauri/src/services/ai_service.rs
pub struct AIService;

impl AIService {
    // 发送消息到 AI 模型
    pub async fn send_message(
        model: &str,
        message: &str,
        context_files: Vec<String>
    ) -> Result<AIResponse>;

    // 获取可用模型列表
    pub async fn get_available_models() -> Result<Vec<ModelConfig>>;

    // 执行代码生成
    pub async fn generate_code(
        cli_tool: &str,
        prompt: &str,
        context: &str
    ) -> Result<String>;
}
```

#### 3. 终端管理
```rust
// src-tauri/src/services/terminal_service.rs
pub struct TerminalService;

impl TerminalService {
    // 创建新终端
    pub async fn create_terminal(working_dir: &str) -> Result<TerminalId>;

    // 执行命令
    pub async fn execute_command(
        terminal_id: TerminalId,
        command: &str
    ) -> Result<String>;

    // 获取终端输出
    pub async fn get_output(
        terminal_id: TerminalId
    ) -> Result<Vec<TerminalOutput>>;

    // 关闭终端
    pub async fn close_terminal(terminal_id: TerminalId) -> Result<()>;
}
```

#### 4. 配置管理
```rust
// src-tauri/src/services/config_service.rs
pub struct ConfigService;

impl ConfigService {
    // 加载配置
    pub async fn load_config() -> Result<AppConfig>;

    // 保存配置
    pub async fn save_config(config: &AppConfig) -> Result<()>;

    // 切换工作区
    pub async fn switch_workspace(name: &str) -> Result<()>;

    // 管理环境变量
    pub async fn set_env_var(key: &str, value: &str) -> Result<()>;
    pub async fn remove_env_var(key: &str) -> Result<()>;

    // 管理模型配置
    pub async fn add_model(model: ModelConfig) -> Result<()>;
    pub async fn update_model(name: &str, model: ModelConfig) -> Result<()>;
    pub async fn remove_model(name: &str) -> Result<()>;

    // 管理 CLI 工具配置
    pub async fn add_cli_tool(cli: CliToolConfig) -> Result<()>;
    pub async fn update_cli_tool(name: &str, cli: CliToolConfig) -> Result<()>;
    pub async fn remove_cli_tool(name: &str) -> Result<()>;
}
```

### Tauri 命令定义

```rust
// src-tauri/src/tauri/commands.rs

// 文件操作命令
#[tauri::command]
pub async fn list_directory(path: String) -> Result<Vec<FileInfo>>;

#[tauri::command]
pub async fn read_file(path: String) -> Result<String>;

#[tauri::command]
pub async fn save_file(path: String, content: String) -> Result<()>;

// AI 聊天命令
#[tauri::command]
pub async fn send_chat_message(
    model: String,
    message: String,
    context_files: Vec<String>
) -> Result<AIResponse>;

// 终端命令
#[tauri::command]
pub async fn create_terminal(working_dir: String) -> Result<String>;

#[tauri::command]
pub async fn execute_terminal_command(
    terminal_id: String,
    command: String
) -> Result<String>;

// 配置命令
#[tauri::command]
pub async fn get_config() -> Result<AppConfig>;

#[tauri::command]
pub async fn save_config(config: AppConfig) -> Result<()>;

#[tauri::command]
pub async fn switch_workspace(name: String) -> Result<()>;
```

### 快捷键配置

```javascript
// frontend/src/utils/shortcuts.js
const shortcuts = {
  // 编辑器快捷键
  'ctrl+s': 'saveCurrentFile',
  'ctrl+shift+s': 'saveAllFiles',
  'ctrl+f': 'findInFile',
  'ctrl+h': 'replaceInFile',
  'ctrl+z': 'undo',
  'ctrl+y': 'redo',
  'ctrl+/': 'toggleComment',

  // 导航快捷键
  'ctrl+p': 'quickOpen',
  'ctrl+shift+p': 'commandPalette',
  'ctrl+b': 'toggleSidebar',
  'ctrl+`': 'toggleTerminal',

  // Tab 切换
  'ctrl+1': 'switchToEditor',
  'ctrl+2': 'switchToChat',
  'ctrl+3': 'switchToOutput',
  'ctrl+4': 'switchToTerminal',
};
```

### 配置示例

```toml
# config/default.toml
[workspace]
name = "default"
data_dir = "~/.code-assistant"

[editor]
font_family = "JetBrains Mono"
font_size = 14
theme = "vs-dark"
tab_size = 4
word_wrap = true

[ai]
default_model = "claude-3.5-sonnet"
api_timeout = 30

[terminal]
default_shell = "/bin/bash"
font_size = 12
scrollback_lines = 1000

[cli_tools]
openai_codex = { path = "/usr/local/bin/codex", args = ["--model", "gpt-4"] }
local_coder = { path = "/usr/local/bin/coder", args = ["--local"] }

[[models]]
name = "claude-3.5-sonnet"
api_endpoint = "https://api.anthropic.com/v1"
api_key = "encrypted_key_here"

[[models]]
name = "gpt-4"
api_endpoint = "https://api.openai.com/v1"
api_key = "encrypted_key_here"
```

### 安装和运行

```bash
# 安装依赖
cd frontend
pnpm install

# 开发模式
cargo tauri dev

# 生产构建
cargo tauri build

# 运行应用
./src-tauri/target/release/code-assistant
```
