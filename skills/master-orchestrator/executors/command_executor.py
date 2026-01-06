#!/usr/bin/env python3
"""
CommandExecutor V2 - 基于Memex-CLI的智能命令执行器

新特性：
- 使用Claude LLM (via command-parser skill) 解析自然语言
- 继承MemexExecutorBase统一架构
- 保留完整的安全验证机制
- 支持fallback到规则引擎（保持向后兼容）
"""

import subprocess
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import sys
from pathlib import Path

# 添加父目录到路径
_parent = Path(__file__).parent.parent
sys.path.insert(0, str(_parent))

from executors.memex_executor_base import MemexExecutorBase
from core.backend_orchestrator import BackendOrchestrator, _get_utf8_env


@dataclass
class CommandResult:
    """命令执行结果"""
    command: str
    output: str
    success: bool
    return_code: int
    error: Optional[str] = None
    category: Optional[str] = None  # 命令类别（git/npm/python等）
    explanation: Optional[str] = None  # 命令说明
    parsed_by: str = "unknown"  # 解析方式（claude/rules/direct）


class CommandExecutor(MemexExecutorBase):
    """
    智能命令执行器 - 基于Memex-CLI

    解析流程：
    1. 优先使用Claude LLM (command-parser skill)
    2. Claude失败则fallback到规则引擎
    3. 安全验证（白名单 + 危险模式检测）
    4. 执行命令

    支持的命令类型：
    - git: status, log, diff, add, commit, push
    - npm: install, test, run, build
    - python: pytest, pip, python脚本
    - docker: ps, logs, exec
    """

    # 白名单：允许的命令前缀
    ALLOWED_COMMANDS = {
        "git", "npm", "npx", "yarn", "pnpm",
        "python", "python3", "pytest", "pip", "pip3",
        "docker", "docker-compose",
        "node", "tsc", "eslint",
        "cargo", "rustc",
        "go", "make", "cmake",
        "ls", "cat", "grep", "echo", "pwd", "cd",
    }

    # 规则引擎模式（fallback用）
    COMMAND_PATTERNS = {
        # Git 命令
        r'(查看|显示|查询)\s*(git\s*)?(状态|status)': 'git status',
        r'(查看|显示)\s*(git\s*)?(日志|历史|log)': 'git log --oneline -10',
        r'(查看|显示)\s*(git\s*)?(差异|变更|diff)': 'git diff',
        r'git\s+status': 'git status',
        r'git\s+log': 'git log --oneline -10',
        r'git\s+diff': 'git diff',

        # NPM 命令
        r'(运行|执行)\s*npm\s*(install|i)': 'npm install',
        r'(运行|执行)\s*npm\s*test': 'npm test',
        r'npm\s+(install|i|test|run|start|build)(.*)': r'npm \1\2',

        # Python 命令
        r'(运行|执行)\s*pytest': 'pytest',
        r'(运行|执行)\s*python\s+(.+)': r'python \2',
        r'pytest(.*)': r'pytest\1',

        # Docker 命令
        r'(查看|显示)\s*docker\s*(容器|container)': 'docker ps',
        r'docker\s+ps': 'docker ps',
        r'docker\s+logs\s+(.+)': r'docker logs \1',
    }

    # Command Parser提示词模板
    COMMAND_PARSER_PROMPT = """将以下自然语言请求转换为shell命令：

请求：{request}

返回严格的JSON格式（不要有其他文本）：
{{
  "command": "具体的shell命令",
  "safe": true/false,
  "category": "git|npm|python|docker|other",
  "explanation": "命令的作用说明"
}}

安全规则：拒绝危险命令（rm -rf /, dd, mkfs等），只允许开发常用命令。"""

    def __init__(
        self,
        backend_orch: BackendOrchestrator,
        use_claude_parser: bool = True,
        fallback_to_rules: bool = True,
        timeout: int = 60,
        allow_interactive: bool = False
    ):
        """
        初始化命令执行器

        Args:
            backend_orch: BackendOrchestrator实例
            use_claude_parser: 是否使用Claude解析（默认True）
            fallback_to_rules: Claude失败时是否fallback到规则引擎
            timeout: 命令超时时间（秒）
            allow_interactive: 是否允许交互式命令
        """
        super().__init__(backend_orch, default_backend="claude", default_timeout=timeout)

        self.use_claude_parser = use_claude_parser
        self.fallback_to_rules = fallback_to_rules
        self.timeout = timeout
        self.allow_interactive = allow_interactive

    def parse_command_with_claude(self, request: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """
        使用Claude LLM解析命令

        Args:
            request: 用户请求

        Returns:
            (command, category, explanation, claude_safe_flag)
        """
        try:
            # 构造提示词
            prompt = self.COMMAND_PARSER_PROMPT.format(request=request)

            # 调用memex-cli
            result = self.execute_via_memex(
                prompt=prompt,
                backend="claude",
                stream_format="jsonl",
                timeout=10
            )

            # 解析JSON输出
            parsed = self._parse_json_output(result.output)

            return (
                parsed.get("command"),
                parsed.get("category"),
                parsed.get("explanation"),
                parsed.get("safe", False)
            )

        except Exception as e:
            # Claude解析失败
            return None, None, None, False

    def parse_command_with_rules(self, request: str) -> Optional[str]:
        """
        使用规则引擎解析命令（fallback）

        Args:
            request: 用户请求

        Returns:
            解析后的命令或None
        """
        request = request.strip()

        # 尝试模式匹配
        for pattern, command_template in self.COMMAND_PATTERNS.items():
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                # 支持捕获组替换
                if '\\' in command_template:
                    command = match.expand(command_template)
                else:
                    command = command_template
                return command.strip()

        # 如果请求本身就像是命令，直接返回
        first_word = request.split()[0] if request.split() else ""
        if first_word in self.ALLOWED_COMMANDS:
            return request

        return None

    def parse_command(self, request: str) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
        """
        解析自然语言请求为shell命令（智能路由）

        Args:
            request: 用户请求

        Returns:
            (command, category, explanation, parsed_by)
        """
        # 优先使用Claude解析
        if self.use_claude_parser:
            command, category, explanation, claude_safe = self.parse_command_with_claude(request)

            if command:
                return command, category, explanation, "claude"

            # Claude失败，是否fallback？
            if not self.fallback_to_rules:
                return None, None, None, "failed"

        # 使用规则引擎
        command = self.parse_command_with_rules(request)
        if command:
            return command, None, None, "rules"

        # 所有方法都失败
        return None, None, None, "failed"

    def is_safe(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        检查命令是否安全

        Args:
            command: 待检查的命令

        Returns:
            (是否安全, 拒绝原因)
        """
        # 检查空命令
        if not command or not command.strip():
            return False, "Empty command"

        # 提取命令的第一个词
        parts = command.split()
        cmd_name = parts[0]

        # 检查是否在白名单中
        if cmd_name not in self.ALLOWED_COMMANDS:
            return False, f"Command '{cmd_name}' not in whitelist"

        # 检查危险模式
        dangerous_patterns = [
            r'rm\s+-rf\s+/',  # 删除根目录
            r':\(\)\{.*\};',  # Fork bomb
            r'>\s*/dev/sd',   # 写入磁盘设备
            r'mkfs',          # 格式化
            r'dd\s+if=',      # dd命令（可能危险）
            r'sudo\s+',       # sudo命令（除非明确允许）
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return False, f"Dangerous pattern detected"

        # 检查交互式命令
        if not self.allow_interactive:
            interactive_commands = ['vim', 'nano', 'emacs', 'less', 'more', 'top', 'htop']
            if cmd_name in interactive_commands:
                return False, f"Interactive command '{cmd_name}' not allowed"

        return True, None

    def execute(self, request: str, **kwargs) -> CommandResult:
        """
        执行命令（智能解析 + 安全验证 + 执行）

        Args:
            request: 用户请求（自然语言或命令）
            **kwargs: 额外参数

        Returns:
            CommandResult
        """
        # 1. 解析命令
        command, category, explanation, parsed_by = self.parse_command(request)

        if not command:
            return CommandResult(
                command=request,
                output="",
                success=False,
                return_code=-1,
                error="Unable to parse command from request",
                parsed_by=parsed_by
            )

        # 2. 安全检查
        is_safe, reason = self.is_safe(command)
        if not is_safe:
            return CommandResult(
                command=command,
                output="",
                success=False,
                return_code=-1,
                error=f"Command rejected: {reason}",
                category=category,
                explanation=explanation,
                parsed_by=parsed_by
            )

        # 3. 执行命令
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=_get_utf8_env(),
                encoding='utf-8',
                errors='replace'
            )

            return CommandResult(
                command=command,
                output=result.stdout,
                success=result.returncode == 0,
                return_code=result.returncode,
                error=result.stderr if result.returncode != 0 else None,
                category=category,
                explanation=explanation,
                parsed_by=parsed_by
            )

        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                output="",
                success=False,
                return_code=-1,
                error=f"Command timed out after {self.timeout} seconds",
                category=category,
                explanation=explanation,
                parsed_by=parsed_by
            )
        except Exception as e:
            return CommandResult(
                command=command,
                output="",
                success=False,
                return_code=-1,
                error=f"Execution failed: {str(e)}",
                category=category,
                explanation=explanation,
                parsed_by=parsed_by
            )

    def execute_multiple(self, requests: List[str]) -> List[CommandResult]:
        """
        批量执行命令

        Args:
            requests: 命令请求列表

        Returns:
            CommandResult列表
        """
        return [self.execute(req) for req in requests]

    def _parse_json_output(self, output: str) -> dict:
        """
        从Claude输出中提取JSON

        Args:
            output: Claude的原始输出

        Returns:
            解析后的dict

        Raises:
            ValueError: JSON解析失败
        """
        # 尝试直接解析
        try:
            return json.loads(output.strip())
        except json.JSONDecodeError:
            pass

        # 尝试从文本中提取JSON块
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 尝试从代码块中提取
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"无法从输出中解析JSON: {output[:200]}...")


# 便捷函数
def create_command_executor(
    backend_orch: BackendOrchestrator,
    use_claude: bool = True,
    fallback: bool = True
) -> CommandExecutor:
    """
    创建CommandExecutor的便捷函数

    Args:
        backend_orch: BackendOrchestrator实例
        use_claude: 是否使用Claude解析
        fallback: 是否允许fallback到规则

    Returns:
        CommandExecutor实例
    """
    return CommandExecutor(
        backend_orch=backend_orch,
        use_claude_parser=use_claude,
        fallback_to_rules=fallback
    )
