"""
Cross-Backend Orchestrator Scripts Package

This package provides cross-platform Python tools for orchestrating
AI tasks across Codex, Claude, and Gemini backends using memex-cli.

Main Components:
    - orchestrator: Core library with BackendOrchestrator class
    - run_task: Single backend task execution
    - compare_backends: Multi-backend comparison
    - pipeline: Sequential multi-stage workflows
    - parallel_run: Parallel execution
    - fallback_run: Fallback chain execution
    - replay_events: Event log replay

Usage:
    from scripts.orchestrator import BackendOrchestrator
    
    orch = BackendOrchestrator()
    result = orch.run_task("claude", "Analyze this code")
"""

from .orchestrator import (
    BackendOrchestrator,
    TaskResult,
    ComparisonResult,
    PipelineResult
)

__all__ = [
    "BackendOrchestrator",
    "TaskResult",
    "ComparisonResult",
    "PipelineResult"
]

__version__ = "1.0.0"
