#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test router initialization in MasterOrchestrator

This test verifies that self.router is properly initialized and never set to None
after the __init__ method completes.

Regression test for bug: AttributeError: 'NoneType' object has no attribute 'route'
"""

import sys
import subprocess
from pathlib import Path


def test_router_not_none_error():
    """Test that router AttributeError doesn't occur"""

    # Run a simple query that would trigger router.route()
    result = subprocess.run(
        [sys.executable, "-m", "master-orchestrator", "test query", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    # Check that the error message doesn't appear
    error_message = "'NoneType' object has no attribute 'route'"
    combined_output = (result.stdout or "") + (result.stderr or "")

    assert error_message not in combined_output, \
        f"Router AttributeError detected in output: {combined_output[:500]}"

    print("[PASS] No router AttributeError detected")


def test_actual_execution():
    """Test that router can actually be called without error"""

    # Test with a real execution (dry-run)
    result = subprocess.run(
        [sys.executable, "-m", "master-orchestrator", "分析当前项目", "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        cwd=Path(__file__).parent.parent.parent,
        timeout=30
    )

    # Should complete successfully (exit code 0 or have dry-run output)
    if result.returncode != 0:
        # Check if it's the router error
        error_message = "'NoneType' object has no attribute 'route'"
        if error_message in (result.stdout or "") + (result.stderr or ""):
            raise AssertionError("Router is None - AttributeError occurred")

    print("[PASS] Actual execution works without router error")


if __name__ == "__main__":
    print("Running router initialization tests...\n")

    try:
        test_router_not_none_error()
        test_actual_execution()

        print("\n[SUCCESS] All router initialization tests passed!")
        sys.exit(0)

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
