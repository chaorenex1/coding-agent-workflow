#!/usr/bin/env python3
"""
安装验证脚本

验证 Orchestrator 安装是否完整和正确

使用方法:
    python scripts/verify_installation.py [--verbose]
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple
import json

# Windows编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class Colors:
    """终端颜色"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class InstallationVerifier:
    """安装验证器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []

    def check(self, name: str, condition: bool, message: str = "") -> bool:
        """
        检查单项

        Args:
            name: 检查项名称
            condition: 检查条件
            message: 附加消息

        Returns:
            检查结果
        """
        status = "✓" if condition else "✗"
        color = Colors.OKGREEN if condition else Colors.FAIL

        output = f"{color}{status}{Colors.ENDC} {name}"
        if message and (self.verbose or not condition):
            output += f": {message}"

        print(output)
        self.results.append((name, condition))
        return condition

    def verify_python_modules(self) -> bool:
        """验证Python模块导入"""
        print(f"\n{Colors.BOLD}1. Python模块验证{Colors.ENDC}")

        modules = [
            ('orchestrator', '核心模块'),
            ('orchestrator.core', '核心组件'),
            ('orchestrator.executors', '执行器模块'),
            ('orchestrator.skills', '技能模块'),
        ]

        all_ok = True
        for module, desc in modules:
            try:
                __import__(module)
                self.check(desc, True, module)
            except ImportError as e:
                self.check(desc, False, f"{module} - {e}")
                all_ok = False

        return all_ok

    def verify_core_classes(self) -> bool:
        """验证核心类"""
        print(f"\n{Colors.BOLD}2. 核心类验证{Colors.ENDC}")

        try:
            from orchestrator import MasterOrchestrator, BackendOrchestrator
            from orchestrator.core import (
                UnifiedRegistry,
                ExecutorFactory,
                ParallelScheduler,
                DependencyAnalyzer,
                ConfigLoader
            )

            classes = [
                (MasterOrchestrator, 'MasterOrchestrator'),
                (BackendOrchestrator, 'BackendOrchestrator'),
                (UnifiedRegistry, 'UnifiedRegistry'),
                (ExecutorFactory, 'ExecutorFactory'),
                (ParallelScheduler, 'ParallelScheduler'),
                (DependencyAnalyzer, 'DependencyAnalyzer'),
                (ConfigLoader, 'ConfigLoader'),
            ]

            all_ok = True
            for cls, name in classes:
                if cls is not None:
                    self.check(name, True)
                else:
                    self.check(name, False, "未找到类定义")
                    all_ok = False

            return all_ok

        except ImportError as e:
            self.check("核心类导入", False, str(e))
            return False

    def verify_executors(self) -> bool:
        """验证执行器"""
        print(f"\n{Colors.BOLD}3. 执行器验证{Colors.ENDC}")

        try:
            from orchestrator.executors import (
                MemexExecutorBase,
                CommandExecutor,
                AgentCaller,
                PromptManager
            )

            executors = [
                (MemexExecutorBase, 'MemexExecutorBase'),
                (CommandExecutor, 'CommandExecutor'),
                (AgentCaller, 'AgentCaller'),
                (PromptManager, 'PromptManager'),
            ]

            all_ok = True
            for executor, name in executors:
                if executor is not None:
                    self.check(name, True)
                else:
                    self.check(name, False)
                    all_ok = False

            return all_ok

        except ImportError as e:
            self.check("执行器导入", False, str(e))
            return False

    def verify_directories(self) -> bool:
        """验证目录结构"""
        print(f"\n{Colors.BOLD}4. 目录结构验证{Colors.ENDC}")

        base_dir = Path.home()
        directories = [
            (base_dir / '.memex', 'Memex根目录'),
            (base_dir / '.memex' / 'orchestrator', 'Orchestrator缓存'),
            (base_dir / '.memex' / 'orchestrator' / 'config', '配置目录'),
            (base_dir / '.memex' / 'orchestrator' / 'logs', '日志目录'),
            (base_dir / '.claude', 'Claude配置目录（可选）'),
        ]

        all_ok = True
        for path, desc in directories:
            exists = path.exists() and path.is_dir()
            self.check(desc, exists, str(path))
            if not exists and desc != 'Claude配置目录（可选）':
                all_ok = False

        return all_ok

    def verify_config(self) -> bool:
        """验证配置文件"""
        print(f"\n{Colors.BOLD}5. 配置文件验证{Colors.ENDC}")

        config_file = Path.home() / '.memex' / 'orchestrator' / 'config' / 'orchestrator.json'

        if not config_file.exists():
            self.check("配置文件", False, "未找到")
            return False

        try:
            config = json.loads(config_file.read_text(encoding='utf-8'))
            required_keys = ['version', 'auto_discover', 'enable_parallel']

            all_ok = True
            for key in required_keys:
                exists = key in config
                self.check(f"配置项: {key}", exists)
                if not exists:
                    all_ok = False

            return all_ok

        except Exception as e:
            self.check("配置文件解析", False, str(e))
            return False

    def verify_skills(self) -> bool:
        """验证技能文件"""
        print(f"\n{Colors.BOLD}6. 技能文件验证{Colors.ENDC}")

        skills_dir = Path(__file__).parent.parent / 'skills' / 'memex-cli' / 'skills'

        if not skills_dir.exists():
            self.check("Skills目录", False, str(skills_dir))
            return False

        required_skills = [
            'intent-analyzer.yaml',
            'command-parser.yaml',
            'agent-router.yaml',
            'prompt-renderer.yaml',
            'dev-workflow.yaml'
        ]

        all_ok = True
        for skill in required_skills:
            skill_file = skills_dir / skill
            exists = skill_file.exists()
            self.check(f"Skill: {skill}", exists)
            if not exists:
                all_ok = False

        return all_ok

    def verify_dependencies(self) -> bool:
        """验证外部依赖"""
        print(f"\n{Colors.BOLD}7. 外部依赖验证（可选）{Colors.ENDC}")

        commands = [
            ('git', 'Git'),
            ('node', 'Node.js（可选）'),
            ('npm', 'npm（可选）'),
            ('pnpm', 'pnpm（可选）'),
            ('memex', 'memex-cli（可选）'),
        ]

        for cmd, name in commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    timeout=5
                )
                self.check(name, result.returncode == 0)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.check(name, False, "未安装")

        return True  # 这些都是可选的，不影响总体结果

    def run_all(self) -> bool:
        """运行所有验证"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Orchestrator 安装验证{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

        checks = [
            self.verify_python_modules(),
            self.verify_core_classes(),
            self.verify_executors(),
            self.verify_directories(),
            self.verify_config(),
            self.verify_skills(),
        ]

        # 依赖检查（可选）
        self.verify_dependencies()

        # 总结
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}验证结果{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

        passed = sum(1 for _, status in self.results if status)
        total = len(self.results)

        print(f"通过: {passed}/{total}")

        # 计算必需检查（前6项）
        required_passed = sum(checks)
        required_total = len(checks)

        if required_passed == required_total:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ 所有必需检查通过！{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Orchestrator 已正确安装并可以使用{Colors.ENDC}\n")
            return True
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ 部分必需检查失败{Colors.ENDC}")
            print(f"{Colors.FAIL}请运行安装脚本或手动修复问题{Colors.ENDC}\n")
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrator 安装验证")
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    args = parser.parse_args()

    verifier = InstallationVerifier(verbose=args.verbose)
    success = verifier.run_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
