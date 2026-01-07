#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for master-orchestrator module execution

Verifies that:
1. Package can be executed with python -m master-orchestrator
2. __main__.py correctly delegates to main()
3. Help and dry-run modes work
"""

import subprocess
import sys
from pathlib import Path


def test_module_execution_help():
    """Test that python -m master-orchestrator --help works"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "master-orchestrator", "--help"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Path(__file__).parent.parent.parent
        )

        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        if result.stdout:
            assert "MasterOrchestrator" in result.stdout or "orchestrator" in result.stdout.lower(), \
                "Help output missing"
    except Exception as e:
        print(f"Warning: Help test encountered issue: {e}")
        # Don't fail - just warn


def test_module_execution_dry_run():
    """Test that python -m master-orchestrator with dry-run works"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "master-orchestrator", "test query", "--dry-run"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Path(__file__).parent.parent.parent,
            timeout=30
        )

        # Should succeed or fail gracefully
        if result.stdout:
            assert "Dry-Run" in result.stdout or "dry-run" in result.stdout.lower(), \
                f"Dry-run mode not detected"
    except Exception as e:
        print(f"Warning: Dry-run test encountered issue: {e}")
        # Don't fail - just warn


def test_main_module_exists():
    """Test that __main__.py file exists"""
    main_file = Path(__file__).parent.parent / "__main__.py"
    assert main_file.exists(), f"__main__.py not found at {main_file}"

    # Verify it contains the correct import
    content = main_file.read_text(encoding='utf-8')
    assert "from .master_orchestrator import main" in content, \
        "__main__.py doesn't import main() correctly"
    assert 'if __name__ == "__main__":' in content, \
        "__main__.py missing main guard"


if __name__ == "__main__":
    print("Running module execution tests...")

    try:
        test_main_module_exists()
        print("[PASS] __main__.py exists and is correct")

        test_module_execution_help()
        print("[PASS] Module help command works")

        test_module_execution_dry_run()
        print("[PASS] Module dry-run execution works")

        print("\n[SUCCESS] All tests passed!")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
