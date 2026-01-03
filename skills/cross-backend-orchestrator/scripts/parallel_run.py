#!/usr/bin/env python3
"""
Execute the same task on multiple backends in parallel.

Usage:
    python parallel_run.py --prompt "Explain machine learning"
    python parallel_run.py -p "Write a sort function" --backends codex,claude --output ./results/
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
        description="Execute the same task on multiple backends in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python parallel_run.py --prompt "Explain quantum computing"
  python parallel_run.py -p "Write a sorting algorithm" --backends codex,claude
  python parallel_run.py -p "Design a REST API" --output ./parallel_results/ --workers 2
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Task prompt to run on all backends"
    )
    parser.add_argument(
        "--backends", "-b",
        default="codex,claude,gemini",
        help="Comma-separated list of backends (default: codex,claude,gemini)"
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
        help="Output directory for results (optional)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=3,
        help="Maximum parallel workers (default: 3)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    backends = [b.strip() for b in args.backends.split(",")]
    
    if not args.quiet:
        print(f"🚀 Starting parallel execution on {len(backends)} backends...")
        print(f"📝 Prompt: {args.prompt}")
        print(f"🔗 Backends: {', '.join(backends)}")
        print(f"⚡ Max workers: {args.workers}")
        print()
    
    orch = BackendOrchestrator(output_dir=args.output or "./parallel_output")
    
    if not args.quiet:
        print("⏳ Executing in parallel...")
    
    result = orch.compare_backends_parallel(
        backends=backends,
        prompt=args.prompt,
        stream_format=args.format,
        max_workers=args.workers
    )
    
    # Print summary
    if not args.quiet:
        print("\n📊 Parallel Execution Results:")
        print("-" * 50)
        for backend, task_result in result.results.items():
            status = "✓" if task_result.success else "✗"
            print(f"  {status} {backend}: {task_result.duration_seconds}s")
        print("-" * 50)
    
    # Save results
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual outputs
        for backend, task_result in result.results.items():
            output_file = output_dir / f"{backend}_output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(task_result.output)
        
        # Save summary
        summary_file = output_dir / "parallel_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        if not args.quiet:
            print(f"\n✅ Results saved to: {output_dir}")
    else:
        print("\n" + json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    # Return success if at least one backend succeeded
    any_success = any(r.success for r in result.results.values())
    return 0 if any_success else 1


if __name__ == "__main__":
    sys.exit(main())
