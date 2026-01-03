#!/usr/bin/env python3
"""
Execute a multi-stage pipeline across different AI backends.

Usage:
    python pipeline.py --stage "codex:Generate code" --stage "claude:Review code"
    python pipeline.py -s "codex:Generate Python function" -s "claude:Improve it" -s "gemini:Document it"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import BackendOrchestrator


def parse_stage(stage_str: str) -> Tuple[str, str]:
    """Parse a stage string in 'backend:prompt' format."""
    if ':' not in stage_str:
        raise ValueError(
            f"Invalid stage format: '{stage_str}'. "
            "Expected 'backend:prompt' format (e.g., 'claude:Review this code')"
        )
    
    backend, prompt = stage_str.split(':', 1)
    backend = backend.strip().lower()
    prompt = prompt.strip()
    
    if backend not in ('codex', 'claude', 'gemini'):
        raise ValueError(
            f"Invalid backend: '{backend}'. "
            "Must be one of: codex, claude, gemini"
        )
    
    return backend, prompt


def main():
    parser = argparse.ArgumentParser(
        description="Execute a multi-stage pipeline across AI backends",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --stage "codex:Generate a Python sorting function"
  
  python pipeline.py \\
    --stage "codex:Generate Python function for data processing" \\
    --stage "claude:Review and improve the code quality" \\
    --stage "gemini:Write comprehensive documentation"
    
  python pipeline.py -s "codex:Create API endpoint" -s "claude:Add error handling" --no-pass-output
        """
    )
    
    parser.add_argument(
        "--stage", "-s",
        action="append",
        required=True,
        help="Stage in 'backend:prompt' format. Can specify multiple stages."
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
        help="Output directory for stage results (optional)"
    )
    parser.add_argument(
        "--no-pass-output",
        action="store_true",
        help="Don't pass previous stage output to next stage"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    # Parse all stages
    try:
        stages: List[Tuple[str, str]] = [parse_stage(s) for s in args.stage]
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    if not args.quiet:
        print(f"🔗 Starting pipeline with {len(stages)} stages...")
        print()
        for i, (backend, prompt) in enumerate(stages, 1):
            print(f"  Stage {i}: [{backend}] {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
        print()
    
    orch = BackendOrchestrator(output_dir=args.output or "./pipeline_output")
    
    result = orch.run_pipeline(
        stages=stages,
        pass_output=not args.no_pass_output,
        stream_format=args.format
    )
    
    # Print stage results
    if not args.quiet:
        print("\n📊 Pipeline Results:")
        print("-" * 60)
        for i, stage_result in enumerate(result.stages, 1):
            status = "✓" if stage_result.success else "✗"
            print(f"  Stage {i} [{stage_result.backend}]: {status} ({stage_result.duration_seconds}s)")
            if not stage_result.success and stage_result.error:
                print(f"           Error: {stage_result.error}")
        print("-" * 60)
        print(f"  Total duration: {result.total_duration_seconds}s")
        print(f"  Status: {'✅ Success' if result.success else '❌ Failed'}")
    
    # Save results
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual stage outputs
        for i, stage_result in enumerate(result.stages, 1):
            stage_file = output_dir / f"stage_{i}_{stage_result.backend}.txt"
            with open(stage_file, 'w', encoding='utf-8') as f:
                f.write(stage_result.output)
        
        # Save summary
        summary_file = output_dir / "pipeline_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        if not args.quiet:
            print(f"\n✅ Results saved to: {output_dir}")
    else:
        print("\n" + json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
