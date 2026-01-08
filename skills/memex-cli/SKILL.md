---
name: memex-cli
description: "Execute AI-powered command-line tasks with memory, and resume capabilities using memex-cli. Use when (1) Running AI backend tasks (codex, claude, gemini), (2) Resuming interrupted runs by run_id, (3) Executing prompts with streaming output in jsonl or text format."
---

# Memex CLI

A CLI wrapper for AI backends with built-in memory, and resume support.

## Core Commands

### Run a Task

```bash
memex-cli run \
  --backend <backend> \
  --prompt "<prompt>" \
  --stream-format <format>
```

**Parameters:**
- `--backend`: AI backend (`codex`, `claude`, `gemini`)
- `--prompt`: Task prompt
- `--stream-format`: Output format (`jsonl` or `text`)
- `--model`: Model name (optional, for codex backend)
- `--model-provider`: Model provider (optional, for codex backend)

### Resume a Run

```bash
memex-cli resume \
  --run-id <RUN_ID> \
  --backend <backend> \
  --prompt "<prompt>" \
  --stream-format <format>
```

Continues a previous run using its `run_id`.

## Backend Examples

### Codex

```bash
memex-cli run --backend "codex" --prompt "编码" --stream-format "text"
```

### Claude

```bash
memex-cli run --backend "claude" --prompt "设计" --stream-format "text"
```

### Gemini

```bash
memex-cli run --backend "gemini" --prompt "UX" --stream-format "text"
```

## Output

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

