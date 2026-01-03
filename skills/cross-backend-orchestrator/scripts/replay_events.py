#!/usr/bin/env python3
"""
Replay a previously recorded run from its event log.

Usage:
    python replay_events.py --events ./run.events.jsonl
    python replay_events.py -e ./output/run.events.jsonl --format text
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
        description="Replay a previously recorded run from its event log",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python replay_events.py --events ./run.events.jsonl
  python replay_events.py -e ./pipeline_output/run.events.jsonl --format jsonl
        """
    )
    
    parser.add_argument(
        "--events", "-e",
        required=True,
        help="Path to events JSONL file"
    )
    parser.add_argument(
        "--format", "-f",
        default="text",
        choices=["text", "jsonl"],
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    events_path = Path(args.events)
    
    if not events_path.exists():
        print(f"Error: Events file not found: {events_path}", file=sys.stderr)
        return 1
    
    if not args.quiet:
        print(f"🔄 Replaying events from: {events_path}")
        print(f"📝 Format: {args.format}")
        print()
    
    orch = BackendOrchestrator()
    output, success = orch.replay_events(str(events_path), args.format)
    
    if output:
        print(output)
    
    if not args.quiet:
        print()
        if success:
            print("✅ Replay completed successfully")
        else:
            print("❌ Replay failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
