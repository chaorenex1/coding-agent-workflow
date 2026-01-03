#!/usr/bin/env python3
"""
Run a single task on a specified AI backend.

Usage:
    python run_task.py --backend claude --prompt "Analyze this code"
    python run_task.py -b codex -p "Generate a sorting function" --model deepseek-reasoner
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import BackendOrchestrator


def main():
    parser = argparse.ArgumentParser(
        description="Execute a single task on a specified AI backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_task.py --backend claude --prompt "Analyze this code for bugs"
  python run_task.py -b codex -p "Generate a Python function" --model deepseek-reasoner
  python run_task.py -b gemini -p "Describe UX improvements" --output ./result.json
        """
    )
    
    parser.add_argument(
        "--backend", "-b",
        required=True,
        choices=["codex", "claude", "gemini"],
        help="AI backend to use"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Task prompt"
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Model name (optional, for codex backend)"
    )
    parser.add_argument(
        "--model-provider",
        default=None,
        help="Model provider (optional, for codex backend)"
    )
    parser.add_argument(
        "--format", "-f",
        default="jsonl",
        choices=["jsonl", "text"],
        help="Output stream format (default: jsonl)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (optional, prints to stdout if not specified)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print(f"🚀 Running task on {args.backend} backend...")
        print(f"📝 Prompt: {args.prompt}")
        print()
    
    orch = BackendOrchestrator()
    result = orch.run_task(
        backend=args.backend,
        prompt=args.prompt,
        stream_format=args.format,
        model=args.model,
        model_provider=args.model_provider
    )
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        if not args.quiet:
            print(f"✅ Result saved to: {output_path}")
    else:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    if not args.quiet:
        if result.success:
            print(f"\n✅ Task completed successfully in {result.duration_seconds}s")
        else:
            print(f"\n❌ Task failed: {result.error}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
