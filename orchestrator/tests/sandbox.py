#!/usr/bin/env python3
"""
沙盒测试框架

提供隔离的测试环境，避免影响真实系统：
- Mock BackendOrchestrator
- 临时文件系统
- 临时配置
- 隔离的注册表
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import yaml

# 添加父目录到路径
_parent = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_parent))

from orchestrator.core.backend_orchestrator import TaskResult


@dataclass
class MockTaskResult:
    """Mock TaskResult for testing"""
    backend: str
    prompt: str
    output: str
    success: bool = True
    error: Optional[str] = None
    run_id: Optional[str] = None
    event_stream: Optional[Any] = None
    duration_seconds: float = 0.1

    def get_final_output(self) -> str:
        """返回最终输出"""
        return self.output

    def get_tool_chain(self) -> List[str]:
        """返回工具链"""
        return []


class MockBackendOrchestrator:
    """
    Mock BackendOrchestrator for testing.

    避免真实的 API 调用，返回预定义的响应。
    """

    def __init__(self, responses: Optional[Dict[str, str]] = None):
        """
        初始化 Mock Backend.

        Args:
            responses: 预定义响应字典 {prompt_pattern: response}
        """
        self.responses = responses or {}
        self.call_count = 0
        self.call_history = []

    def run_task(
        self,
        backend: str,
        prompt: str,
        stream_format: str = "jsonl",
        **kwargs
    ) -> MockTaskResult:
        """
        Mock 任务执行.

        Args:
            backend: 后端名称
            prompt: 提示词
            stream_format: 流格式
            **kwargs: 其他参数

        Returns:
            MockTaskResult
        """
        self.call_count += 1
        self.call_history.append({
            "backend": backend,
            "prompt": prompt,
            "stream_format": stream_format,
            "kwargs": kwargs
        })

        # 查找匹配的响应
        output = self._find_response(prompt)

        return MockTaskResult(
            backend=backend,
            prompt=prompt,
            output=output,
            success=True,
            run_id=f"mock-run-{self.call_count}",
            duration_seconds=0.1
        )

    def _find_response(self, prompt: str) -> str:
        """查找匹配的响应"""
        # 精确匹配
        if prompt in self.responses:
            return self.responses[prompt]

        # 关键词匹配
        for pattern, response in self.responses.items():
            if pattern.lower() in prompt.lower():
                return response

        # 默认响应
        return f"Mock response for: {prompt[:50]}..."

    def reset(self):
        """重置调用历史"""
        self.call_count = 0
        self.call_history = []


class SandboxEnvironment:
    """
    沙盒测试环境.

    提供隔离的文件系统和配置环境。
    """

    def __init__(self, name: str = "test-sandbox"):
        """
        初始化沙盒环境.

        Args:
            name: 沙盒名称
        """
        self.name = name
        self.temp_dir = None
        self.project_root = None
        self.config_file = None
        self.skills_dir = None

    def __enter__(self):
        """进入沙盒环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix=f"{self.name}-")
        self.project_root = Path(self.temp_dir)
        self.skills_dir = self.project_root / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出沙盒环境"""
        # 清理临时目录
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def create_config(self, config_data: Dict[str, Any]) -> Path:
        """
        创建配置文件.

        Args:
            config_data: 配置数据

        Returns:
            配置文件路径
        """
        self.config_file = self.project_root / "orchestrator.yaml"

        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)

        return self.config_file

    def create_skill(self, skill_name: str, skill_data: Dict[str, Any]) -> Path:
        """
        创建 Skill 文件.

        Args:
            skill_name: Skill 名称
            skill_data: Skill 数据

        Returns:
            Skill 文件路径
        """
        skill_file = self.skills_dir / f"{skill_name}.yaml"

        with open(skill_file, 'w', encoding='utf-8') as f:
            yaml.dump(skill_data, f, allow_unicode=True)

        return skill_file

    def create_multiple_skills(self, skills: Dict[str, Dict[str, Any]]) -> List[Path]:
        """
        批量创建 Skills.

        Args:
            skills: {skill_name: skill_data}

        Returns:
            Skill 文件路径列表
        """
        paths = []
        for name, data in skills.items():
            path = self.create_skill(name, data)
            paths.append(path)
        return paths

    def get_mock_backend(self, responses: Optional[Dict[str, str]] = None) -> MockBackendOrchestrator:
        """
        获取 Mock Backend.

        Args:
            responses: 预定义响应

        Returns:
            MockBackendOrchestrator
        """
        return MockBackendOrchestrator(responses=responses)


class TestHelper:
    """测试辅助工具"""

    @staticmethod
    def create_sample_config() -> Dict[str, Any]:
        """创建示例配置"""
        return {
            "version": "3.0",
            "global": {
                "default_backend": "claude",
                "timeout": 300,
                "enable_parallel": False,
                "max_parallel_tasks": 3
            },
            "skills": {
                "manual": [
                    {
                        "name": "test-skill-1",
                        "path": "./skills/test-skill-1.yaml",
                        "enabled": True,
                        "priority": 100,
                        "dependencies": []
                    }
                ]
            },
            "commands": {
                "whitelist": ["git", "npm", "python"]
            },
            "parallel": {
                "enabled": False,
                "max_workers": 3,
                "timeout_per_task": 120
            }
        }

    @staticmethod
    def create_sample_skill(name: str, priority: int = 50, dependencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """创建示例 Skill"""
        return {
            "name": name,
            "version": "1.0.0",
            "description": f"Test skill: {name}",
            "backend": "claude",
            "system_prompt": f"You are testing {name}",
            "user_prompt_template": "{{request}}",
            "enabled": True,
            "priority": priority,
            "dependencies": dependencies or []
        }

    @staticmethod
    def assert_task_result(result, expected_success: bool = True, expected_namespace: Optional[str] = None):
        """断言任务结果"""
        assert result.success == expected_success, f"Expected success={expected_success}, got {result.success}"
        if expected_namespace:
            assert result.namespace == expected_namespace, f"Expected namespace={expected_namespace}, got {result.namespace}"

    @staticmethod
    def assert_batch_result(result, expected_total: int, expected_successful: Optional[int] = None):
        """断言批处理结果"""
        assert result.total_tasks == expected_total, f"Expected {expected_total} tasks, got {result.total_tasks}"
        if expected_successful is not None:
            assert result.successful == expected_successful, f"Expected {expected_successful} successful, got {result.successful}"


# 便捷函数
def create_sandbox(name: str = "test") -> SandboxEnvironment:
    """创建沙盒环境"""
    return SandboxEnvironment(name=name)


def create_mock_backend(responses: Optional[Dict[str, str]] = None) -> MockBackendOrchestrator:
    """创建 Mock Backend"""
    return MockBackendOrchestrator(responses=responses)


# 示例用法
if __name__ == "__main__":
    print("沙盒测试框架示例\n")

    # 示例 1: 使用沙盒环境
    print("示例 1: 沙盒环境")
    with create_sandbox("example") as sandbox:
        # 创建配置
        config = TestHelper.create_sample_config()
        config_file = sandbox.create_config(config)
        print(f"  配置文件: {config_file}")

        # 创建 Skill
        skill_data = TestHelper.create_sample_skill("example-skill")
        skill_file = sandbox.create_skill("example-skill", skill_data)
        print(f"  Skill 文件: {skill_file}")

        # 验证文件存在
        assert config_file.exists()
        assert skill_file.exists()
        print("  ✓ 文件创建成功")

    print("  ✓ 沙盒清理完成\n")

    # 示例 2: Mock Backend
    print("示例 2: Mock Backend")
    backend = create_mock_backend({
        "test": "Test response",
        "hello": "Hello, World!"
    })

    result = backend.run_task("claude", "test prompt")
    print(f"  调用结果: {result.output}")
    print(f"  调用次数: {backend.call_count}")
    print("  ✓ Mock Backend 工作正常\n")

    print("沙盒框架就绪!")
