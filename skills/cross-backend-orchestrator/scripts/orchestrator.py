#!/usr/bin/env python3
"""
Cross-Backend Orchestrator - Core Library Module

A cross-platform Python library for orchestrating AI tasks across
Codex, Claude, and Gemini backends using memex-cli.

Usage:
    from orchestrator import BackendOrchestrator
    
    orch = BackendOrchestrator()
    result = orch.run_task("claude", "Analyze this code")
"""

import subprocess
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入事件解析器
try:
    from .event_parser import MemexEventParser, EventStream
except ImportError:
    from event_parser import MemexEventParser, EventStream


@dataclass
class TaskResult:
    """Result of a single task execution."""
    backend: str
    prompt: str
    output: str
    success: bool
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None
    run_id: Optional[str] = None
    event_stream: Optional[EventStream] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # 移除不可序列化的对象
        if 'event_stream' in result:
            del result['event_stream']
        return result

    def get_final_output(self) -> str:
        """获取最终输出（优先从 event_stream）"""
        if self.event_stream:
            return self.event_stream.get_final_output()
        return self.output

    def get_tool_chain(self) -> List[Tuple[str, bool]]:
        """获取工具调用链"""
        if self.event_stream:
            return self.event_stream.get_tool_chain()
        return []


@dataclass
class ComparisonResult:
    """Result of comparing multiple backends."""
    prompt: str
    results: Dict[str, TaskResult]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "timestamp": self.timestamp,
            "results": {k: v.to_dict() for k, v in self.results.items()}
        }


@dataclass 
class PipelineResult:
    """Result of a multi-stage pipeline execution."""
    stages: List[TaskResult]
    total_duration_seconds: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_duration_seconds": self.total_duration_seconds,
            "success": self.success,
            "stages": [s.to_dict() for s in self.stages]
        }


class BackendOrchestrator:
    """
    Orchestrate AI tasks across multiple backends.
    
    Supported backends:
        - codex: Code-optimized backend (uses deepseek-reasoner model)
        - claude: General-purpose reasoning
        - gemini: Visual and UX understanding
    """
    
    VALID_BACKENDS = {"codex", "claude", "gemini"}
    
    DEFAULT_CODEX_MODEL = "deepseek-reasoner"
    DEFAULT_CODEX_PROVIDER = "aduib_ai"
    
    def __init__(self, output_dir: Optional[str] = None, parse_events: bool = False, timeout: int = 300):
        """
        Initialize the orchestrator.

        Args:
            output_dir: Directory for output files. Defaults to ./orchestrator_output
            parse_events: Whether to parse event streams (slower but provides detailed info)
            timeout: Command timeout in seconds (default: 300)
        """
        self.output_dir = Path(output_dir or "./orchestrator_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parse_events = parse_events
        self.timeout = timeout

        # 检查 memex-cli 是否安装
        self._check_memex_cli()
    
    def _check_memex_cli(self) -> None:
        """检查 memex-cli 是否安装"""
        try:
            subprocess.run(
                ["memex-cli", "--version"],
                capture_output=True,
                timeout=5
            )
        except FileNotFoundError:
            raise RuntimeError(
                "memex-cli not found. Please install it first.\n"
                "Installation: npm install -g memex-cli"
            )
        except Exception as e:
            print(f"Warning: Could not verify memex-cli installation: {e}")

    def _validate_backend(self, backend: str) -> None:
        """Validate that a backend is supported."""
        if backend not in self.VALID_BACKENDS:
            raise ValueError(
                f"Invalid backend: {backend}. "
                f"Must be one of: {', '.join(self.VALID_BACKENDS)}"
            )
    
    def _build_command(
        self,
        backend: str,
        prompt: str,
        stream_format: str = "jsonl",
        model: Optional[str] = None,
        model_provider: Optional[str] = None
    ) -> List[str]:
        """Build the memex-cli command for a given backend."""
        cmd = ["memex-cli", "run", "--backend", backend]

        cmd.extend(["--prompt", prompt])
        cmd.extend(["--stream-format", stream_format])
        
        return cmd
    
    def _execute_command(self, cmd: List[str]) -> Tuple[str, bool, Optional[str], Optional[str], Optional[EventStream]]:
        """
        Execute a command and return (output, success, error, run_id, event_stream).

        Cross-platform compatible using subprocess.

        Returns:
            (stdout, success, error, run_id, event_stream)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            run_id = None
            event_stream = None

            if result.returncode == 0 and result.stdout:
                # 快速提取 run_id
                run_id = MemexEventParser.extract_run_id(result.stdout)

                # 如果需要详细分析，保存输出并解析
                if self.parse_events and run_id:
                    temp_file = self.output_dir / f"{run_id}.events.jsonl"
                    temp_file.write_text(result.stdout, encoding='utf-8')
                    try:
                        event_stream = MemexEventParser.parse_stream(temp_file)
                    except Exception as e:
                        print(f"Warning: 事件流解析失败: {e}")

                return result.stdout, True, None, run_id, event_stream
            else:
                return result.stdout, False, result.stderr or "Command failed", None, None

        except subprocess.TimeoutExpired:
            return "", False, f"Command timed out after {self.timeout} seconds", None, None
        except FileNotFoundError:
            return "", False, "memex-cli not found. Please ensure it is installed and in PATH."
        except Exception as e:
            return "", False, str(e)
    
    def run_task(
        self,
        backend: str,
        prompt: str,
        stream_format: str = "jsonl",
        model: Optional[str] = None,
        model_provider: Optional[str] = None
    ) -> TaskResult:
        """
        Execute a single task on a specified backend.
        
        Args:
            backend: AI backend (codex, claude, or gemini)
            prompt: Task prompt
            stream_format: Output format (jsonl or text)
            model: Model name (optional, for codex)
            model_provider: Model provider (optional, for codex)
            
        Returns:
            TaskResult with output and metadata
        """
        self._validate_backend(backend)

        cmd = self._build_command(backend, prompt, stream_format, model, model_provider)

        start_time = time.time()
        output, success, error, run_id, event_stream = self._execute_command(cmd)
        duration = time.time() - start_time

        return TaskResult(
            backend=backend,
            prompt=prompt,
            output=output,
            success=success,
            duration_seconds=round(duration, 3),
            error=error,
            run_id=run_id,
            event_stream=event_stream
        )
    
    def compare_backends(
        self,
        backends: List[str],
        prompt: str,
        stream_format: str = "jsonl"
    ) -> ComparisonResult:
        """
        Run the same task on multiple backends and compare results.
        
        Args:
            backends: List of backends to compare
            prompt: Task prompt
            stream_format: Output format
            
        Returns:
            ComparisonResult with all backend outputs
        """
        for backend in backends:
            self._validate_backend(backend)
        
        results = {}
        for backend in backends:
            results[backend] = self.run_task(backend, prompt, stream_format)
        
        return ComparisonResult(prompt=prompt, results=results)
    
    def compare_backends_parallel(
        self,
        backends: List[str],
        prompt: str,
        stream_format: str = "jsonl",
        max_workers: int = 3
    ) -> ComparisonResult:
        """
        Run the same task on multiple backends in parallel.
        
        Args:
            backends: List of backends to compare
            prompt: Task prompt
            stream_format: Output format
            max_workers: Maximum parallel executions
            
        Returns:
            ComparisonResult with all backend outputs
        """
        for backend in backends:
            self._validate_backend(backend)
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_backend = {
                executor.submit(self.run_task, backend, prompt, stream_format): backend
                for backend in backends
            }
            
            for future in as_completed(future_to_backend):
                backend = future_to_backend[future]
                try:
                    results[backend] = future.result()
                except Exception as e:
                    results[backend] = TaskResult(
                        backend=backend,
                        prompt=prompt,
                        output="",
                        success=False,
                        duration_seconds=0,
                        error=str(e)
                    )
        
        return ComparisonResult(prompt=prompt, results=results)
    
    def run_pipeline(
        self,
        stages: List[Tuple[str, str]],
        pass_output: bool = True,
        stream_format: str = "jsonl"
    ) -> PipelineResult:
        """
        Execute a multi-stage pipeline across backends.
        
        Args:
            stages: List of (backend, prompt) tuples
            pass_output: Whether to pass previous output to next stage
            stream_format: Output format
            
        Returns:
            PipelineResult with all stage outputs
        """
        stage_results = []
        previous_output = ""
        total_start = time.time()
        
        for i, (backend, prompt) in enumerate(stages):
            self._validate_backend(backend)
            
            # Optionally include previous output in prompt
            if pass_output and previous_output:
                full_prompt = f"Previous stage output:\n{previous_output}\n\nCurrent task: {prompt}"
            else:
                full_prompt = prompt
            
            result = self.run_task(backend, full_prompt, stream_format)
            stage_results.append(result)
            
            if result.success:
                previous_output = result.output
            else:
                # Pipeline failed at this stage
                break
        
        total_duration = time.time() - total_start
        all_success = all(r.success for r in stage_results)
        
        return PipelineResult(
            stages=stage_results,
            total_duration_seconds=round(total_duration, 3),
            success=all_success
        )
    
    def run_with_fallback(
        self,
        backends: List[str],
        prompt: str,
        stream_format: str = "jsonl"
    ) -> TaskResult:
        """
        Execute task with fallback chain - try each backend until success.
        
        Args:
            backends: Ordered list of backends to try
            prompt: Task prompt
            stream_format: Output format
            
        Returns:
            TaskResult from first successful backend
        """
        for backend in backends:
            self._validate_backend(backend)
        
        for backend in backends:
            result = self.run_task(backend, prompt, stream_format)
            if result.success:
                return result
        
        # All backends failed - return last result
        return result
    
    def replay_events(self, events_file: str, output_format: str = "text") -> Tuple[str, bool]:
        """
        Replay a previously recorded run from its event log.
        
        Args:
            events_file: Path to events JSONL file
            output_format: Output format (text or jsonl)
            
        Returns:
            Tuple of (output, success)
        """
        if not Path(events_file).exists():
            return "", False
        
        cmd = ["memex-cli", "replay", "--events", events_file, "--format", output_format]
        output, success, _ = self._execute_command(cmd)
        return output, success
    
    def resume_run(
        self,
        run_id: str,
        backend: str,
        prompt: str,
        stream_format: str = "jsonl"
    ) -> TaskResult:
        """
        Resume a previously interrupted run.
        
        Args:
            run_id: ID of the run to resume
            backend: Backend to use
            prompt: Continuation prompt
            stream_format: Output format
            
        Returns:
            TaskResult with resumed run output
        """
        self._validate_backend(backend)
        
        cmd = [
            "memex-cli", "resume",
            "--run-id", run_id,
            "--backend", backend,
            "--prompt", prompt,
            "--stream-format", stream_format
        ]
        
        start_time = time.time()
        output, success, error = self._execute_command(cmd)
        duration = time.time() - start_time
        
        return TaskResult(
            backend=backend,
            prompt=prompt,
            output=output,
            success=success,
            duration_seconds=round(duration, 3),
            error=error,
            run_id=run_id
        )
    
    def save_result(self, result: Any, filename: str) -> Path:
        """
        Save a result to a JSON file.
        
        Args:
            result: Result object with to_dict() method
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        return filepath


def main():
    """CLI entry point for basic testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-Backend Orchestrator")
    parser.add_argument("--backend", "-b", required=True, help="Backend: codex, claude, or gemini")
    parser.add_argument("--prompt", "-p", required=True, help="Task prompt")
    parser.add_argument("--format", "-f", default="jsonl", help="Output format")
    
    args = parser.parse_args()
    
    orch = BackendOrchestrator()
    result = orch.run_task(args.backend, args.prompt, args.format)
    
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
