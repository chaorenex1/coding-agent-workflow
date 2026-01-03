# Output Formats and Parsing Guide

All memex-cli runs generate `run.events.jsonl` files for auditing and replay. This guide explains how to parse and work with these outputs.

## JSONL Event Format

Each line in the events file is a JSON object representing an event:

```json
{"type": "start", "timestamp": "2024-01-15T10:30:00Z", "backend": "claude", "run_id": "abc123"}
{"type": "message", "timestamp": "2024-01-15T10:30:01Z", "content": "Processing request..."}
{"type": "output", "timestamp": "2024-01-15T10:30:05Z", "content": "Generated response text"}
{"type": "end", "timestamp": "2024-01-15T10:30:06Z", "status": "success"}
```

## Event Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `start` | Run initialization | `backend`, `run_id`, `prompt` |
| `message` | Progress updates | `content` |
| `output` | Generated content | `content` |
| `error` | Error occurred | `error`, `message` |
| `end` | Run completion | `status` |

## Parsing Examples

### Python (Cross-Platform)

```python
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def parse_events(filepath: str) -> List[Dict[str, Any]]:
    """Parse JSONL events file."""
    events = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events

def extract_output(events: List[Dict]) -> List[str]:
    """Extract all output content from events."""
    return [e['content'] for e in events if e.get('type') == 'output']

def get_run_status(events: List[Dict]) -> str:
    """Get final run status."""
    for e in reversed(events):
        if e.get('type') == 'end':
            return e.get('status', 'unknown')
    return 'unknown'

def get_run_metadata(events: List[Dict]) -> Optional[Dict]:
    """Get run metadata from start event."""
    for e in events:
        if e.get('type') == 'start':
            return e
    return None

# Usage
events = parse_events('run.events.jsonl')
outputs = extract_output(events)
status = get_run_status(events)
metadata = get_run_metadata(events)
```

### Node.js (Cross-Platform)

```javascript
const fs = require('fs');
const readline = require('readline');

async function parseEvents(filepath) {
    const events = [];
    const fileStream = fs.createReadStream(filepath, { encoding: 'utf-8' });
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    for await (const line of rl) {
        if (line.trim()) {
            events.push(JSON.parse(line));
        }
    }
    return events;
}

function extractOutputs(events) {
    return events
        .filter(e => e.type === 'output')
        .map(e => e.content);
}

function getRunStatus(events) {
    for (let i = events.length - 1; i >= 0; i--) {
        if (events[i].type === 'end') {
            return events[i].status || 'unknown';
        }
    }
    return 'unknown';
}

// Usage
(async () => {
    const events = await parseEvents('run.events.jsonl');
    const outputs = extractOutputs(events);
    const status = getRunStatus(events);
})();
```

## TaskResult Format

The Python orchestrator returns `TaskResult` objects:

```json
{
    "backend": "claude",
    "prompt": "Original task prompt",
    "output": "Generated output content...",
    "success": true,
    "duration_seconds": 2.5,
    "timestamp": "2024-01-15T10:30:00Z",
    "error": null,
    "run_id": null
}
```

## ComparisonResult Format

When using `compare_backends.py`:

```json
{
    "prompt": "Original task prompt",
    "timestamp": "2024-01-15T10:30:00Z",
    "results": {
        "codex": {
            "backend": "codex",
            "prompt": "...",
            "output": "Codex generated content...",
            "success": true,
            "duration_seconds": 2.5
        },
        "claude": {
            "backend": "claude",
            "prompt": "...",
            "output": "Claude generated content...",
            "success": true,
            "duration_seconds": 3.1
        }
    }
}
```

## PipelineResult Format

Pipeline execution returns:

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "total_duration_seconds": 8.5,
    "success": true,
    "stages": [
        {
            "backend": "codex",
            "prompt": "Stage 1 prompt",
            "output": "Stage 1 output...",
            "success": true,
            "duration_seconds": 2.5
        },
        {
            "backend": "claude",
            "prompt": "Previous stage output:...\n\nCurrent task: Stage 2 prompt",
            "output": "Stage 2 output...",
            "success": true,
            "duration_seconds": 3.0
        }
    ]
}
```

## Error Handling

Always handle potential errors when parsing:

```python
def safe_parse_events(filepath: str) -> List[Dict]:
    """Safely parse events with error handling."""
    events = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Invalid JSON on line {line_num}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except PermissionError:
        print(f"Error: Permission denied: {filepath}")
    return events
```

## Best Practices

1. **Stream Processing**: For large files, process line-by-line rather than loading all at once
2. **Error Tolerance**: Handle malformed lines gracefully
3. **Encoding**: Always use UTF-8 encoding for cross-platform compatibility
4. **Timestamp Parsing**: Use ISO 8601 format for consistent datetime handling
5. **Content Extraction**: Filter by event type for specific content
6. **Audit Trail**: Preserve original JSONL files for debugging and replay