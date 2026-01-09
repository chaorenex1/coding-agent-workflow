---
name: code-with-codex
description: "Write and generate code using memex-cli with Codex backend. Use when (1) Generating code files and scripts, (2) Refactoring existing code, (3) Writing tests, (4) Creating project scaffolds, (5) Implementing algorithms or features, (6) Code review and optimization, (7) Complex multi-file projects."
---

# Code with Codex

Use memex-cli to leverage Codex for code generation with memory and replay support.

## RUN_ID Instructions

When using `memex-cli resume`, replace `<RUN_ID>` with the actual run ID obtained from the initial `memex-cli run` command. This allows you to continue or build upon previous code generation tasks.

## Memex cli Output Format

Outputs are streamed in the specified format (`jsonl` or `text`), allowing real-time monitoring of task progress.

### Example JSONL output(multiple jsonl lines)

```jsonl
{"v":1,"type":"assistant.output","ts":"2026-01-08T08:22:20.664800300+00:00","run_id":"a9ba0e5d-9dd5-43a1-8b0f-b1dd11346a2b","action":"\"{}\"","args":null,"output":"{\n  \"mode\": \"command\",\n  \"task_type\": \"general\",\n  \"complexity\": \"simple\",\n  \"backend_hint\": null,\n  \"skill_hint\": null,\n  \"confidence\": 0.92,\n  \"reasoning\": \"简单的文件写入任务，生成10道算术题并写入文件，可用echo或Python命令直接完成\",\n  \"enable_parallel\": false,\n  \"parallel_reasoning\": \"单一文件写入操作，顺序 执行即可\"\n}"}
```

### Example Text output(multiple text lines, any format)

```txt
{
  "mode": "backend",
  "task_type": "general",
  "complexity": "simple",
  "backend_hint": "claude",
  "skill_hint": null,
  "confidence": 0.92,
  "reasoning": "生成10道算术题目并写入文件，简单内容生成任务，适合直接LLM处理",
  "enable_parallel": false,
  "parallel_reasoning": "单一文件写入任务，无法分解并行"
}
```

## Model Selection Guide

| Model |  Best For | Complexity |
|-------|-----------|------------|
| gpt-5.1-codex-mini | Simple scripts, quick fixes | ⭐ |
| gpt-5.2-codex | General coding, utilities | ⭐⭐ |
| gpt-5.1-codex-max | Balanced quality/speed | ⭐⭐⭐ |
| gpt-5.2 | Complex logic, algorithms | ⭐⭐⭐⭐ |
| gpt-5.2 | Architecture, system design | ⭐⭐⭐⭐⭐ |

## Scenarios by Complexity

### Level 1: Simple Scripts

Quick utilities, single-file scripts, simple automation.

```bash
# Hello world / basic syntax
memex-cli run --backend "codex" --model "gpt-5.1-codex-mini" --prompt "Python脚本：批量重命名文件，添加日期前缀" --stream-format "text"

# Simple data processing
memex-cli run --backend "codex" --model "gpt-5.1-codex-mini" --prompt "读取CSV文件，统计每列的空值数量" --stream-format "text"

# Basic CLI tool
memex-cli run --backend "codex" --model "gpt-5.1-codex-mini" --prompt "Bash脚本：监控磁盘空间，超过80%发送告警" --stream-format "text"
```

### Level 2: Utility Functions

Helper functions, data transformations, format conversions.

```bash
# Data validation
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "编写邮箱、手机号、身份证号验证函数集合" --stream-format "text"

# Format conversion
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "JSON/YAML/TOML格式互转工具类" --stream-format "text"

# String processing
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "实现模板字符串解析器，支持变量替换和条件渲染" --stream-format "text"
"
```

### Level 3: Single Module

Complete modules with error handling, logging, tests.

```bash
# REST client
memex-cli run --backend "codex" --model "gpt-5.1-codex-max" --prompt "Python HTTP客户端封装，支持重试、超时、拦截器" --stream-format "jsonl"

# Database helper
memex-cli run --backend "codex" --model "gpt-5.1-codex-max" --prompt "SQLite工具类：连接池、事务管理、查询构建器" --stream-format "jsonl"

# File watcher
memex-cli run --backend "codex" --model "gpt-5.1-codex-max" --prompt "目录监控服务，检测文件变更并触发回调，支持过滤规则" --stream-format "jsonl"
"
```

### Level 4: Algorithm Implementation

Complex algorithms, data structures, performance-critical code.

```bash
# Data structures
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "实现跳表SkipList，支持插入、删除、范围查询，O(logN)复杂度" --stream-format "jsonl"

# Graph algorithms
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "实现Dijkstra和A*寻路算法，支持动态权重和障碍物" --stream-format "jsonl"

# Concurrent programming
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "实现无锁并发队列，支持多生产者多消费者" --stream-format "jsonl"

# Parser / Compiler
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "实现简单的表达式解析器，支持四则运算、括号、变量" --stream-format "jsonl"
```

### Level 5: System Design & Architecture

Multi-module projects, microservices, complete applications.

```bash
# API service
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "设计并实现用户认证微服务：JWT、OAuth2、RBAC权限模型" --stream-format "jsonl"

# Event-driven system
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "设计事件驱动架构：消息队列、事件溯源、CQRS模式实现" --stream-format "jsonl"

# Plugin system
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "设计可扩展插件系统：插件发现、生命周期管理、依赖注入" --stream-format "jsonl"

# Distributed system
memex-cli run --backend "codex" --model "gpt-5.2" --prompt "设计分布式任务调度系统：任务分片、故障转移、负载均衡" --stream-format "jsonl"
"
```

## Special Tasks

### Unit Testing

```bash
# Basic tests
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "为计算器模块编写pytest测试用例" --stream-format "text"

# Comprehensive tests
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "为用户服务编写完整测试：单元测试、集成测试、Mock外部依赖" --stream-format "text"
```

### Code Review & Refactoring

```bash
# Code review
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "审查这段代码：指出问题、安全隐患、性能瓶颈、改进建议" --stream-format "text"

# Refactoring
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "重构这段代码：应用设计模式，提取公共逻辑，改善可测试性" --stream-format "jsonl"
```

### Documentation

```bash
# API docs
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "为这个模块生成API文档，包含函数签名、参数说明、使用示例" --stream-format "text"

# Architecture docs
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "生成系统架构文档：模块关系图、数据流、部署架构" --stream-format "text"
```

## Workflow

### Iterative Development

```bash
# Step 1: Initial implementation
memex-cli run --backend "codex" --model "gpt-5.2-codex" --prompt "实现用户注册功能" --stream-format "jsonl"

# Step 2: Add features
memex-cli resume --run-id <RUN_ID> --backend "codex" --model "gpt-5.2-codex" --prompt "添加邮箱验证和密码强度检查" --stream-format "jsonl"

# Step 3: Add tests
memex-cli resume --run-id <RUN_ID> --backend "codex" --model "gpt-5.2-codex" --prompt "为注册功能编写单元测试" --stream-format "jsonl"
"""
```

---

## Tips

1. **Match model to task**: Use lightweight models for simple tasks, save powerful models for complex logic.
2. **Prefer text for simple tasks**: Faster and lower cost for straightforward code generation.
3. **Use jsonl for complex tasks**: Enables full audit trail and iterative refinement.
4. **Break down large tasks**: split multifile subtasks parallel execution and use resume to build features incrementally.
5. **Include context**: Specify language, framework, coding standards in prompts.