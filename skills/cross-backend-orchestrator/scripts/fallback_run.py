#!/usr/bin/env python3
"""
Execute a task with a fallback chain - try each backend until one succeeds.

Usage:
    python fallback_run.py --primary codex --fallback claude --prompt "Generate code"
    python fallback_run.py -1 codex -2 claude -2 gemini -p "Complex task"
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
        description="Execute a task with fallback chain across backends",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fallback_run.py --primary codex --fallback claude --prompt "Generate code"
  
  python fallback_run.py \\
    --primary codex \\
    --fallback claude \\
    --fallback gemini \\
    --prompt "Complex task that may fail"
    
  python fallback_run.py -1 codex -2 claude -p "Generate function" --output ./result.json
        """
    )
    
    parser.add_argument(
        "--primary", "-1",
        required=True,
        choices=["codex", "claude", "gemini"],
        help="Primary backend to try first"
    )
    parser.add_argument(
        "--fallback", "-2",
        action="append",
        default=[],
        help="Fallback backend(s). Can specify multiple in order of priority."
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Task prompt"
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
        help="Output file path (optional)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    # Build backend chain
    backends = [args.primary] + args.fallback
    
    # Validate fallback backends
    valid_backends = {"codex", "claude", "gemini"}
    for backend in args.fallback:
        if backend not in valid_backends:
            print(f"Error: Invalid fallback backend '{backend}'. Must be one of: {', '.join(valid_backends)}", 
                  file=sys.stderr)
            return 1
    
    if not args.quiet:
        print(f"🔄 Starting fallback chain execution...")
        print(f"📝 Prompt: {args.prompt}")
        print(f"🔗 Chain: {' → '.join(backends)}")
        print()
    
    orch = BackendOrchestrator()
    
    # Try each backend in order
    result = None
    for i, backend in enumerate(backends, 1):
        if not args.quiet:
            print(f"[{i}/{len(backends)}] Trying {backend}...")
        
        result = orch.run_task(backend, args.prompt, args.format)
        
        if result.success:
            if not args.quiet:
                print(f"   ✓ Success with {backend} ({result.duration_seconds}s)")
            break
        else:
            if not args.quiet:
                print(f"   ✗ Failed: {result.error}")
                if i < len(backends):
                    print(f"   → Falling back to next backend...")
    
    # Print final status
    if not args.quiet:
        print()
        if result.success:
            print(f"✅ Task completed successfully using {result.backend}")
        else:
            print(f"❌ All backends failed. Last error: {result.error}")
    
    # Save or print result
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add chain metadata to result
        output_data = result.to_dict()
        output_data["fallback_chain"] = backends
        output_data["attempted_backends"] = backends[:backends.index(result.backend) + 1] if result.success else backends
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        if not args.quiet:
            print(f"\n📁 Result saved to: {output_path}")
    else:
        print("\n" + json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
