#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UserPromptSubmit Hook: Intent Analyzer

Analyzes user input BEFORE Claude processes it.
Detects requests that will require orchestrator and provides guidance.

This hook can:
- Modify the user's prompt (add context/instructions)
- Block the prompt entirely (rare, for safety)
- Pass through unchanged

Exit Codes:
    0 - Allow (with possible modification via stdout)
    1 - Block the prompt

Environment Variables (set by Claude Code):
    CLAUDE_USER_PROMPT  - The user's input text
    CLAUDE_SESSION_ID   - Current session identifier
    CLAUDE_PROJECT_DIR  - Project root directory

Output:
    If modifying: Print the modified prompt to stdout
    If blocking: Print reason to stdout, exit 1
    If passing through: Print nothing or original prompt, exit 0

Usage in .claude/settings.json:
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": ".*",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/intent_analyzer.py"
        }]
      }
    ]
  }
}
"""

import sys
import os
import io
import re
import json
import html
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# Windows UTF-8 Encoding Fix
# =============================================================================

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# =============================================================================
# Configuration
# =============================================================================

LOG_DIR = Path.home() / ".claude-hooks" / "intent"


def clean_encoding(text: str) -> str:
    """Clean up encoding issues in text."""
    if not text:
        return text
    text = html.unescape(text)
    if '&amp;' in text:
        text = html.unescape(text)
    return text

class IntentType(Enum):
    """Types of detected intent."""
    COMMAND = "command"           # Shell command execution
    FILE_CREATE = "file_create"   # Creating new files
    FILE_MODIFY = "file_modify"   # Modifying existing files
    CODE_WRITE = "code_write"     # Writing/generating code
    PROJECT = "project"           # Project-level operations
    BUILD_TEST = "build_test"     # Build/test operations
    GIT = "git"                   # Git operations
    QUERY = "query"               # Questions/analysis (no action)
    UNKNOWN = "unknown"

@dataclass
class IntentAnalysis:
    """Result of intent analysis."""
    intent_type: IntentType
    confidence: float
    requires_orchestrator: bool
    suggested_command: Optional[str]
    patterns_matched: List[str]

# =============================================================================
# Intent Detection Patterns
# =============================================================================

# Patterns that indicate orchestrator is needed
ORCHESTRATOR_PATTERNS = {
    IntentType.COMMAND: [
        r'\b(run|execute|运行|执行)\s+(command|cmd|命令|脚本)',
        r'\b(npm|yarn|pnpm)\s+(install|run|test|build|start)',
        r'\b(pip|pip3)\s+install',
        r'\b(docker|docker-compose)\s+\w+',
        r'\b(pytest|jest|mocha|vitest)\b',
        r'\b(make|cmake|gradle|maven)\s+\w+',
        r'\bcurl\s+',
        r'\bwget\s+',
    ],
    IntentType.GIT: [
        r'\bgit\s+(commit|push|pull|merge|rebase|checkout|branch)',
        r'\b(commit|push|pull|提交|推送|拉取)',
        r'\b(create|delete)\s+(branch|tag)',
    ],
    IntentType.FILE_CREATE: [
        r'\b(create|make|generate|新建|创建)\s+(a\s+)?(new\s+)?(file|文件)',
        r'\b(create|make|generate|新建|创建)\s+\w+\.(py|js|ts|tsx|jsx|go|rs|java|cpp|c|h)',
        r'\b(write|save)\s+(to|into)\s+\w+\.\w+',
        r'\b(touch|mkdir)\s+',
    ],
    IntentType.FILE_MODIFY: [
        r'\b(edit|modify|update|change|fix|修改|更新|编辑)\s+(the\s+)?(file|code|代码|文件)',
        r'\b(add|remove|delete|insert|append)\s+.{0,20}\s+(to|from|in)\s+',
        r'\b(refactor|重构)\s+',
        r'\breplace\s+.+\s+with\s+',
    ],
    IntentType.CODE_WRITE: [
        r'\b(write|implement|code|develop|实现|开发|编写)\s+(a\s+)?(function|class|method|component|module|功能|组件)',
        r'\b(add|create)\s+(a\s+)?(new\s+)?(feature|功能|endpoint|api|route)',
        r'\b(build|develop|实现)\s+(a\s+)?(system|application|app|project|系统|应用)',
    ],
    IntentType.PROJECT: [
        r'\b(initialize|init|setup|scaffold|初始化|搭建)\s+(a\s+)?(new\s+)?(project|项目)',
        r'\b(create|start)\s+(a\s+)?(new\s+)?(react|vue|angular|next|node|python)\s+(app|project)',
        r'\bnpx\s+create-',
    ],
    IntentType.BUILD_TEST: [
        r'\b(build|compile|构建|编译)\s+(the\s+)?(project|code|app)',
        r'\b(run|execute)\s+(the\s+)?(tests?|测试)',
        r'\b(test|测试)\s+(the\s+)?(code|function|component)',
        r'\bstart\s+(the\s+)?(server|app|dev)',
    ],
}

# Patterns that DON'T require orchestrator (queries/analysis)
QUERY_PATTERNS = [
    r'^(what|how|why|when|where|explain|describe|tell me|can you explain)',
    r'^(什么|怎么|为什么|哪里|解释|描述|告诉我)',
    r'\b(analyze|review|check|look at|examine)\s+(this|the)\s+(code|file|error)',
    r'\b(分析|检查|查看|审查)\s+',
    r'^(is|are|does|do|can|could|should|would)\s+',
    r'\?$',  # Ends with question mark
]

# =============================================================================
# Intent Analysis
# =============================================================================

def analyze_intent(prompt: str) -> IntentAnalysis:
    """Analyze user prompt to determine intent."""
    prompt_lower = prompt.lower().strip()
    matched_patterns = []
    
    # First check if it's just a query
    for pattern in QUERY_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return IntentAnalysis(
                intent_type=IntentType.QUERY,
                confidence=0.8,
                requires_orchestrator=False,
                suggested_command=None,
                patterns_matched=["query_pattern"]
            )
    
    # Check orchestrator patterns
    best_intent = IntentType.UNKNOWN
    best_confidence = 0.0
    
    for intent_type, patterns in ORCHESTRATOR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                matched_patterns.append(pattern)
                # Higher confidence for more specific matches
                confidence = 0.7 + (0.1 * len(matched_patterns))
                if confidence > best_confidence:
                    best_confidence = min(confidence, 0.95)
                    best_intent = intent_type
    
    requires_orchestrator = best_intent != IntentType.UNKNOWN and best_intent != IntentType.QUERY
    
    # Generate suggested command
    suggested_command = None
    if requires_orchestrator:
        # Clean up the prompt for the suggestion
        clean_prompt = prompt.replace('"', '\\"')[:100]
        suggested_command = f'python -m master-orchestrator "{clean_prompt}" -v'
    
    return IntentAnalysis(
        intent_type=best_intent,
        confidence=best_confidence,
        requires_orchestrator=requires_orchestrator,
        suggested_command=suggested_command,
        patterns_matched=matched_patterns
    )

# =============================================================================
# Prompt Enhancement
# =============================================================================

def enhance_prompt(original_prompt: str, analysis: IntentAnalysis) -> str:
    """
    Enhance the user prompt with orchestrator guidance.
    
    This adds a reminder to Claude about using the orchestrator,
    which will be visible in Claude's context.
    """
    if not analysis.requires_orchestrator:
        return original_prompt
    
    intent_descriptions = {
        IntentType.COMMAND: "command execution",
        IntentType.GIT: "git operation",
        IntentType.FILE_CREATE: "file creation",
        IntentType.FILE_MODIFY: "file modification",
        IntentType.CODE_WRITE: "code writing",
        IntentType.PROJECT: "project operation",
        IntentType.BUILD_TEST: "build/test operation",
    }
    
    intent_desc = intent_descriptions.get(analysis.intent_type, "execution")
    
    enhancement = f"""
[ORCHESTRATOR REMINDER]
This request involves {intent_desc}. 
Remember: ALL execution operations must go through master-orchestrator.
Suggested command: {analysis.suggested_command}
[END REMINDER]

{original_prompt}
"""
    
    return enhancement.strip()

# =============================================================================
# Logging
# =============================================================================

def log_analysis(prompt: str, analysis: IntentAnalysis):
    """Log intent analysis for debugging and improvement."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:200],
            "intent": analysis.intent_type.value,
            "confidence": analysis.confidence,
            "requires_orchestrator": analysis.requires_orchestrator,
            "patterns_matched": analysis.patterns_matched[:5],
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Logging should never break the hook

# =============================================================================
# Main
# =============================================================================

def main():
    """Main hook entry point."""
    # Get user prompt from environment
    user_prompt = os.environ.get("CLAUDE_USER_PROMPT", "")
    
    # Clean encoding issues
    user_prompt = clean_encoding(user_prompt)
    
    if not user_prompt.strip():
        # Empty prompt, pass through
        sys.exit(0)
    
    # Analyze intent
    analysis = analyze_intent(user_prompt)
    
    # Log for debugging
    log_analysis(user_prompt, analysis)
    
    # Decide action based on analysis
    if analysis.requires_orchestrator and analysis.confidence > 0.6:
        # Enhance the prompt with orchestrator reminder
        enhanced_prompt = enhance_prompt(user_prompt, analysis)
        print(enhanced_prompt)
        sys.exit(0)
    else:
        # Pass through unchanged
        print(user_prompt)
        sys.exit(0)


if __name__ == "__main__":
    main()
