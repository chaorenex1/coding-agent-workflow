# 环境变量配置文档

**适用于**: MasterOrchestrator + memex-cli + aduib-ai (托管服务)

**日期**: 2026-01-04

---

## 目录

- [概览](#概览)
- [必需环境变量](#必需环境变量)
- [可选环境变量](#可选环境变量)
- [配置方法](#配置方法)
- [使用场景](#使用场景)

---

## 概览

### 配置原则

- ✅ **本地优先** - memex-cli 在本地执行，使用本地 API Key
- ✅ **远程可选** - aduib-ai 作为可选的托管数据服务
- ✅ **简单配置** - 用户只需配置 AI API Key 和可选的远程服务

### 环境变量总数

| 组件 | 必需 | 可选 | 总计 |
|------|-----|------|------|
| **memex-cli** | 3 个 | 1 个 | 4 个 |
| **aduib-ai 连接** | 0 个 | 2 个 | 2 个 |
| **总计** | **3 个** | **3 个** | **6 个** |

---

## 必需环境变量

### AI 模型 API Keys（必需）

这些是调用 AI 模型所必需的，由 memex-cli 使用。

---

#### 1. CLAUDE_API_KEY

**说明**: Anthropic Claude API 密钥

**类型**: 必需（如果使用 Claude 后端）

**格式**: `sk-ant-api03-` 开头

**获取方式**:
1. 访问 https://console.anthropic.com
2. 创建 API Key
3. 复制密钥

**示例**:
```bash
export CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**用途**:
- MasterOrchestrator 中 `backend="claude"` 的任务
- 5 阶段工作流的阶段 1、2（需求分析、功能设计）

---

#### 2. GOOGLE_API_KEY

**说明**: Google Gemini API 密钥

**类型**: 必需（如果使用 Gemini 后端）

**格式**: `AIza` 开头

**获取方式**:
1. 访问 https://makersuite.google.com/app/apikey
2. 创建 API Key
3. 复制密钥

**示例**:
```bash
export GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**用途**:
- MasterOrchestrator 中 `backend="gemini"` 的任务
- 5 阶段工作流的阶段 3（UX 设计）

---

#### 3. DEEPSEEK_API_KEY

**说明**: DeepSeek API 密钥（作为 Codex 后端）

**类型**: 必需（如果使用 Codex 后端）

**格式**: `sk-` 开头

**获取方式**:
1. 访问 https://platform.deepseek.com
2. 创建 API Key
3. 复制密钥

**示例**:
```bash
export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**用途**:
- MasterOrchestrator 中 `backend="codex"` 的任务
- 5 阶段工作流的阶段 4、5（开发计划、代码实现）

---

## 可选环境变量

### aduib-ai 远程服务（可选）

这些变量用于连接 aduib-ai 托管服务，提供缓存和历史功能。**不设置这些变量时，MasterOrchestrator 工作在纯本地模式。**

---

#### 4. ADUIB_URL

**说明**: aduib-ai 托管服务地址

**类型**: 可选

**默认值**: `http://localhost:8000`（本地开发）

**生产示例**:
```bash
export ADUIB_URL=https://aduib.example.com
```

**开发示例**:
```bash
export ADUIB_URL=http://localhost:8000
```

**用途**:
- 连接到 aduib-ai 托管服务
- 查询结果缓存
- 上传任务历史
- Web UI 后端

**何时需要**:
- 需要结果缓存功能
- 需要任务历史记录
- 需要 Web UI 查看历史
- 需要跨设备同步

**何时不需要**:
- 仅在本地使用 CLI
- 不需要历史记录
- 不需要缓存

---

#### 5. ADUIB_API_KEY

**说明**: aduib-ai API 密钥（用户认证）

**类型**: 可选

**格式**: `sk_` 开头

**获取方式**:
1. 访问 aduib-ai 托管服务
2. 登录/注册账号
3. 在设置中生成 API Key

**示例**:
```bash
export ADUIB_API_KEY=sk_1234567890abcdef1234567890abcdef
```

**用途**:
- 验证用户身份
- 访问用户专属的缓存和历史
- 多租户隔离

**安全性**:
- ✅ 仅用于数据查询和保存
- ✅ 不用于 AI 模型调用
- ✅ 可以随时在 aduib-ai 平台撤销
- ✅ 支持多个 API Key（不同设备）

---

#### 6. MEMEX_CLI_PATH

**说明**: memex-cli 可执行文件路径

**类型**: 可选

**默认值**: `memex-cli`（从 PATH 查找）

**示例**:
```bash
export MEMEX_CLI_PATH=/usr/local/bin/memex-cli
```

**用途**:
- 指定 memex-cli 的完整路径
- 当 memex-cli 不在 PATH 中时使用

**何时需要**:
- memex-cli 安装在非标准位置
- 系统有多个 memex-cli 版本

---

## 配置方法

### 方式 1: Shell 配置文件（推荐）

**Linux/Mac**:

编辑 `~/.bashrc` 或 `~/.zshrc`:

```bash
# ============================================
# MasterOrchestrator 配置
# ============================================

# -------- 必需配置 --------

# AI 模型 API Keys
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx

# -------- 可选配置 --------

# aduib-ai 托管服务（启用远程缓存和历史）
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_your_api_key_here

# memex-cli 路径（如果需要）
# export MEMEX_CLI_PATH=/usr/local/bin/memex-cli
```

应用配置:
```bash
source ~/.bashrc
# 或
source ~/.zshrc
```

---

**Windows**:

**方式 A: 系统环境变量**

1. 右键"此电脑" → "属性"
2. "高级系统设置" → "环境变量"
3. 在"用户变量"中添加：
   - `CLAUDE_API_KEY` = `sk-ant-api03-xxxxx`
   - `GOOGLE_API_KEY` = `AIzaSyxxxxx`
   - `DEEPSEEK_API_KEY` = `sk-xxxxx`
   - `ADUIB_URL` = `https://aduib.example.com`
   - `ADUIB_API_KEY` = `sk_your_api_key_here`

**方式 B: PowerShell**

编辑 PowerShell 配置文件:
```powershell
notepad $PROFILE
```

添加:
```powershell
$env:CLAUDE_API_KEY = "sk-ant-api03-xxxxx"
$env:GOOGLE_API_KEY = "AIzaSyxxxxx"
$env:DEEPSEEK_API_KEY = "sk-xxxxx"
$env:ADUIB_URL = "https://aduib.example.com"
$env:ADUIB_API_KEY = "sk_your_api_key_here"
```

---

### 方式 2: .env 文件（项目级）

创建 `.env` 文件在项目根目录:

```bash
# C:\Users\zarag\Documents\coding_base\.env

# AI API Keys
CLAUDE_API_KEY=sk-ant-api03-xxxxx
GOOGLE_API_KEY=AIzaSyxxxxx
DEEPSEEK_API_KEY=sk-xxxxx

# aduib-ai 托管服务（可选）
ADUIB_URL=https://aduib.example.com
ADUIB_API_KEY=sk_your_api_key_here
```

加载 .env 文件:
```python
# master_orchestrator.py 自动加载
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

---

### 方式 3: memex-cli 配置（仅 AI API Keys）

使用 memex-cli 命令配置:

```bash
# 配置 Claude
memex-cli backends add claude --api-key sk-ant-api03-xxxxx

# 配置 Gemini
memex-cli backends add gemini --api-key AIzaSyxxxxx

# 配置 Codex
memex-cli backends add codex --api-key sk-xxxxx

# 查看配置
memex-cli backends list
```

配置文件位置: `~/.memex/config`

---

### 方式 4: 命令行参数（临时）

```bash
# 临时设置环境变量（仅当前终端会话）
export CLAUDE_API_KEY=sk-ant-api03-xxxxx

# 或在命令前设置
CLAUDE_API_KEY=sk-ant-api03-xxxxx python master_orchestrator.py "需求"

# 指定 aduib-ai URL（覆盖环境变量）
python master_orchestrator.py "需求" --aduib-url https://custom.example.com
```

---

## 使用场景

### 场景 1: 纯本地模式（最简单）

**配置**:

```bash
# 仅配置 AI API Keys
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx

# 不设置 ADUIB_* 变量
```

**特点**:
- ✅ 完全本地执行
- ✅ 无需 aduib-ai 服务
- ✅ API Key 不离开本地
- ✅ 可离线使用（除 AI API 调用）
- ❌ 无缓存功能
- ❌ 无历史记录

**使用**:
```bash
python master_orchestrator.py "开发博客系统"

# 输出:
# [本地执行] 使用 memex-cli
# [工作流执行完成]
# 成功: True
# 完成阶段: 5/5
```

---

### 场景 2: 本地 + 远程缓存（推荐）

**配置**:

```bash
# AI API Keys
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx

# aduib-ai 托管服务
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_your_api_key_here
```

**特点**:
- ✅ 本地执行 memex-cli
- ✅ 远程缓存加速
- ✅ 任务历史记录
- ✅ Web UI 可查看历史
- ✅ 跨设备同步
- ✅ API Key 仍保留在本地

**使用**:

**首次执行**:
```bash
python master_orchestrator.py "开发博客系统" --verbose

# 输出:
# [查询缓存] 未命中
# [本地执行] 使用 memex-cli
# [工作流执行完成] 成功: True
# [已保存] 结果已上传到远程
```

**第二次执行相同请求**:
```bash
python master_orchestrator.py "开发博客系统" --verbose

# 输出:
# [查询缓存] 命中! 从远程返回结果
# [工作流执行完成] 成功: True
# (跳过本地执行，节省时间和成本)
```

---

### 场景 3: 仅查询缓存，不上传

**配置**:

```bash
# 同场景 2，但禁用自动上传
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_your_api_key_here
```

**使用**:
```bash
# 查询缓存，但不上传结果
python master_orchestrator.py "开发博客系统" --no-upload

# 或设置环境变量
export ADUIB_AUTO_UPLOAD=false
python master_orchestrator.py "开发博客系统"
```

**用途**:
- 隐私场景：不想上传任务内容
- 仅利用公共缓存

---

### 场景 4: 多设备同步

**设备 A (PC)**:

```bash
# PC 上执行任务
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_same_api_key

python master_orchestrator.py "开发博客系统"
# → 结果上传到 aduib-ai
```

**设备 B (笔记本)**:

```bash
# 笔记本上查询
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_same_api_key

python master_orchestrator.py "开发博客系统"
# → 缓存命中，立即返回结果
```

**设备 C (手机浏览器)**:

访问 `https://aduib.example.com` → 查看任务历史

---

## 环境变量检查

### 快速检查脚本

创建 `check_env.sh`:

```bash
#!/bin/bash

echo "========================================="
echo "MasterOrchestrator 环境变量检查"
echo "========================================="
echo ""

# 必需变量
echo "必需配置:"
echo "  CLAUDE_API_KEY: ${CLAUDE_API_KEY:0:10}... ${CLAUDE_API_KEY:+✓} ${CLAUDE_API_KEY:-✗ 未设置}"
echo "  GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}... ${GOOGLE_API_KEY:+✓} ${GOOGLE_API_KEY:-✗ 未设置}"
echo "  DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:0:10}... ${DEEPSEEK_API_KEY:+✓} ${DEEPSEEK_API_KEY:-✗ 未设置}"
echo ""

# 可选变量
echo "可选配置 (远程服务):"
echo "  ADUIB_URL: ${ADUIB_URL:-未设置 (纯本地模式)}"
echo "  ADUIB_API_KEY: ${ADUIB_API_KEY:0:10}... ${ADUIB_API_KEY:+✓} ${ADUIB_API_KEY:-✗ 未设置}"
echo ""

# memex-cli 检查
echo "memex-cli 检查:"
if command -v memex-cli &> /dev/null; then
    echo "  ✓ memex-cli 已安装"
    memex-cli --version
else
    echo "  ✗ memex-cli 未安装"
    echo "    安装: npm install -g memex-cli"
fi
echo ""

# 工作模式
echo "工作模式:"
if [ -n "$ADUIB_API_KEY" ]; then
    echo "  → 本地 + 远程缓存模式"
else
    echo "  → 纯本地模式"
fi
echo ""

echo "========================================="
```

运行:
```bash
chmod +x check_env.sh
./check_env.sh
```

---

### Windows PowerShell 检查脚本

创建 `check_env.ps1`:

```powershell
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MasterOrchestrator 环境变量检查" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 必需变量
Write-Host "必需配置:" -ForegroundColor Yellow
$claudeKey = $env:CLAUDE_API_KEY
if ($claudeKey) {
    Write-Host "  CLAUDE_API_KEY: $($claudeKey.Substring(0, 10))... ✓" -ForegroundColor Green
} else {
    Write-Host "  CLAUDE_API_KEY: ✗ 未设置" -ForegroundColor Red
}

$googleKey = $env:GOOGLE_API_KEY
if ($googleKey) {
    Write-Host "  GOOGLE_API_KEY: $($googleKey.Substring(0, 10))... ✓" -ForegroundColor Green
} else {
    Write-Host "  GOOGLE_API_KEY: ✗ 未设置" -ForegroundColor Red
}

$deepseekKey = $env:DEEPSEEK_API_KEY
if ($deepseekKey) {
    Write-Host "  DEEPSEEK_API_KEY: $($deepseekKey.Substring(0, 10))... ✓" -ForegroundColor Green
} else {
    Write-Host "  DEEPSEEK_API_KEY: ✗ 未设置" -ForegroundColor Red
}

Write-Host ""

# 可选变量
Write-Host "可选配置 (远程服务):" -ForegroundColor Yellow
$aduibUrl = $env:ADUIB_URL
if ($aduibUrl) {
    Write-Host "  ADUIB_URL: $aduibUrl" -ForegroundColor Green
} else {
    Write-Host "  ADUIB_URL: 未设置 (纯本地模式)" -ForegroundColor Gray
}

$aduibKey = $env:ADUIB_API_KEY
if ($aduibKey) {
    Write-Host "  ADUIB_API_KEY: $($aduibKey.Substring(0, 10))... ✓" -ForegroundColor Green
} else {
    Write-Host "  ADUIB_API_KEY: ✗ 未设置" -ForegroundColor Gray
}

Write-Host ""

# memex-cli 检查
Write-Host "memex-cli 检查:" -ForegroundColor Yellow
$memexCmd = Get-Command memex-cli -ErrorAction SilentlyContinue
if ($memexCmd) {
    Write-Host "  ✓ memex-cli 已安装" -ForegroundColor Green
    memex-cli --version
} else {
    Write-Host "  ✗ memex-cli 未安装" -ForegroundColor Red
    Write-Host "    安装: npm install -g memex-cli" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
```

运行:
```powershell
.\check_env.ps1
```

---

## 快速配置指南

### 5 分钟快速开始

**步骤 1: 安装 memex-cli**

```bash
npm install -g memex-cli
memex-cli --version
```

**步骤 2: 配置 AI API Keys**

选择方式 A 或 B：

**方式 A: 使用 memex-cli 命令**
```bash
memex-cli backends add claude --api-key YOUR_CLAUDE_KEY
memex-cli backends add gemini --api-key YOUR_GEMINI_KEY
memex-cli backends add codex --api-key YOUR_DEEPSEEK_KEY
```

**方式 B: 使用环境变量**
```bash
export CLAUDE_API_KEY=YOUR_CLAUDE_KEY
export GOOGLE_API_KEY=YOUR_GEMINI_KEY
export DEEPSEEK_API_KEY=YOUR_DEEPSEEK_KEY
```

**步骤 3: 测试**

```bash
python master_orchestrator.py "测试请求"
```

**步骤 4: (可选) 启用远程服务**

```bash
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=YOUR_ADUIB_KEY
```

---

## 总结

### 环境变量清单

| 变量名 | 必需/可选 | 默认值 | 说明 |
|--------|----------|--------|------|
| `CLAUDE_API_KEY` | **必需** | - | Claude API 密钥 |
| `GOOGLE_API_KEY` | **必需** | - | Gemini API 密钥 |
| `DEEPSEEK_API_KEY` | **必需** | - | DeepSeek API 密钥 |
| `ADUIB_URL` | 可选 | - | aduib-ai 服务地址 |
| `ADUIB_API_KEY` | 可选 | - | aduib-ai API 密钥 |
| `MEMEX_CLI_PATH` | 可选 | `memex-cli` | memex-cli 路径 |

### 最小配置

**仅需 3 个环境变量**即可运行（纯本地模式）:

```bash
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx
```

### 推荐配置

**5 个环境变量**获得完整功能（本地 + 远程）:

```bash
export CLAUDE_API_KEY=sk-ant-api03-xxxxx
export GOOGLE_API_KEY=AIzaSyxxxxx
export DEEPSEEK_API_KEY=sk-xxxxx
export ADUIB_URL=https://aduib.example.com
export ADUIB_API_KEY=sk_your_api_key_here
```

---

**文档版本**: 2.0.0
**更新日期**: 2026-01-04
**说明**: 简化版，aduib-ai 作为托管服务，用户无需配置后端
