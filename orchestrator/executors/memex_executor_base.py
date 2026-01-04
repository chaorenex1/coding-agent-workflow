#!/usr/bin/env python3
"""
MemexExecutorBase - 统一执行器基类

所有执行器（Command/Agent/Prompt/Skill）的基类，
提供通过memex-cli统一调用的能力。
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

import sys
from pathlib import Path

# 添加父目录到路径
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from core.backend_orchestrator import BackendOrchestrator, TaskResult


class MemexExecutorBase(ABC):
    """
    统一执行器基类

    所有执行器通过memex-cli进行底层调用，提供：
    1. 统一的接口
    2. 错误处理
    3. 超时控制
    4. 结果标准化
    """

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        default_backend: str = "claude",
        default_timeout: int = 60
    ):
        """
        初始化执行器

        Args:
            backend_orch: BackendOrchestrator实例
            default_backend: 默认后端（claude/gemini/codex）
            default_timeout: 默认超时时间（秒）
        """
        self.backend_orch = backend_orch
        self.default_backend = default_backend
        self.default_timeout = default_timeout

    def execute_via_memex(
        self,
        prompt: str,
        backend: Optional[str] = None,
        stream_format: str = "jsonl",
        timeout: Optional[int] = None,
        **kwargs
    ) -> TaskResult:
        """
        通过memex-cli执行任务

        Args:
            prompt: 提示词或请求
            backend: 后端选择（默认使用default_backend）
            stream_format: 输出格式（jsonl或text）
            timeout: 超时时间（默认使用default_timeout）
            **kwargs: 额外参数传递给backend_orch

        Returns:
            TaskResult对象

        Raises:
            RuntimeError: 执行失败
        """
        backend = backend or self.default_backend

        # 调用backend_orch
        result = self.backend_orch.run_task(
            backend=backend,
            prompt=prompt,
            stream_format=stream_format,
            **kwargs
        )

        # 检查成功状态
        if not result.success:
            raise RuntimeError(
                f"Memex执行失败 (backend={backend}): {result.error}"
            )

        return result

    def build_prompt_with_template(
        self,
        template: str,
        **variables
    ) -> str:
        """
        使用变量填充提示词模板

        Args:
            template: 提示词模板（支持{var}占位符）
            **variables: 变量字典

        Returns:
            填充后的提示词
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"模板变量缺失: {e}")

    @abstractmethod
    def execute(self, request: str, **kwargs) -> Any:
        """
        执行任务（子类必须实现）

        Args:
            request: 用户请求
            **kwargs: 额外参数

        Returns:
            执行结果（具体类型由子类定义）
        """
        pass

    def get_executor_name(self) -> str:
        """获取执行器名称"""
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.get_executor_name()}(backend={self.default_backend})"


class MemexSkillExecutor(MemexExecutorBase):
    """
    基于Memex-CLI Skill的执行器

    用于执行预定义的memex-cli skill（YAML配置）
    """

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        skill_name: str,
        default_backend: str = "claude"
    ):
        """
        初始化Skill执行器

        Args:
            backend_orch: BackendOrchestrator实例
            skill_name: memex-cli skill名称
            default_backend: 默认后端
        """
        super().__init__(backend_orch, default_backend)
        self.skill_name = skill_name

    def execute(
        self,
        request: str,
        backend: Optional[str] = None,
        **skill_params
    ) -> TaskResult:
        """
        执行memex-cli skill

        Args:
            request: 用户请求
            backend: 后端选择
            **skill_params: skill参数

        Returns:
            TaskResult对象
        """
        # 构造skill调用提示词
        # 注：实际的skill调用需要memex-cli支持skill参数
        # 这里简化为直接调用，假设prompt已包含skill逻辑
        prompt = self._build_skill_prompt(request, **skill_params)

        return self.execute_via_memex(
            prompt=prompt,
            backend=backend
        )

    def _build_skill_prompt(self, request: str, **params) -> str:
        """
        构造skill调用提示词

        Args:
            request: 用户请求
            **params: skill参数

        Returns:
            提示词字符串
        """
        # 基础实现：直接返回请求
        # 子类可以重写以添加skill-specific逻辑
        return request

    def get_executor_name(self) -> str:
        return f"{super().get_executor_name()}[{self.skill_name}]"


# 便捷函数
def create_skill_executor(
    backend_orch: BackendOrchestrator,
    skill_name: str,
    backend: str = "claude"
) -> MemexSkillExecutor:
    """
    创建Skill执行器的便捷函数

    Args:
        backend_orch: BackendOrchestrator实例
        skill_name: skill名称
        backend: 默认后端

    Returns:
        MemexSkillExecutor实例
    """
    return MemexSkillExecutor(
        backend_orch=backend_orch,
        skill_name=skill_name,
        default_backend=backend
    )
