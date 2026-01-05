#!/usr/bin/env python3
"""
Orchestrator 安装脚本

自动化安装流程：
1. 检查系统依赖（Python, Node.js, npm, pnpm）
2. 安装 memex-cli
3. 克隆 coding-agent-workflow
4. 安装 Skill 依赖
5. 创建本地缓存目录
6. 初始化配置

使用方法:
    python scripts/install_orchestrator.py [--skip-deps] [--verbose]
"""

import os
import sys
import subprocess
import platform
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, List
import json

# Windows编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """终端颜色常量"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """禁用颜色（Windows兼容）"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# Windows下禁用颜色
if platform.system() == 'Windows':
    Colors.disable()


class InstallationError(Exception):
    """安装错误"""
    pass


class DependencyChecker:
    """系统依赖检查器"""

    @staticmethod
    def run_command(cmd: List[str], capture_output=True) -> Tuple[bool, str]:
        """
        运行命令并返回结果

        Args:
            cmd: 命令列表
            capture_output: 是否捕获输出

        Returns:
            (成功标志, 输出内容)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, str(e)

    def check_python(self, min_version: Tuple[int, int] = (3, 8)) -> bool:
        """
        检查Python版本

        Args:
            min_version: 最低版本要求 (major, minor)

        Returns:
            是否满足要求
        """
        logger.info("检查 Python 版本...")

        success, version_str = self.run_command([sys.executable, '--version'])

        if not success:
            logger.error(f"{Colors.FAIL}✗ Python 未安装{Colors.ENDC}")
            return False

        # 解析版本号
        try:
            version_parts = version_str.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])

            if (major, minor) >= min_version:
                logger.info(f"{Colors.OKGREEN}✓ Python {major}.{minor} 已安装{Colors.ENDC}")
                return True
            else:
                logger.error(
                    f"{Colors.FAIL}✗ Python 版本过低: {major}.{minor}, "
                    f"需要 >= {min_version[0]}.{min_version[1]}{Colors.ENDC}"
                )
                return False
        except Exception as e:
            logger.error(f"{Colors.FAIL}✗ 无法解析Python版本: {e}{Colors.ENDC}")
            return False

    def check_nodejs(self, min_version: int = 16) -> bool:
        """
        检查Node.js版本

        Args:
            min_version: 最低主版本号

        Returns:
            是否满足要求
        """
        logger.info("检查 Node.js 版本...")

        success, version_str = self.run_command(['node', '--version'])

        if not success:
            logger.warning(f"{Colors.WARNING}⚠ Node.js 未安装{Colors.ENDC}")
            return False

        # 解析版本号 (格式: v18.19.0)
        try:
            major = int(version_str.lstrip('v').split('.')[0])

            if major >= min_version:
                logger.info(f"{Colors.OKGREEN}✓ Node.js v{major} 已安装{Colors.ENDC}")
                return True
            else:
                logger.warning(
                    f"{Colors.WARNING}⚠ Node.js 版本过低: v{major}, "
                    f"建议 >= v{min_version}{Colors.ENDC}"
                )
                return False
        except Exception as e:
            logger.error(f"{Colors.FAIL}✗ 无法解析Node.js版本: {e}{Colors.ENDC}")
            return False

    def check_npm(self) -> bool:
        """检查npm"""
        logger.info("检查 npm...")

        success, version_str = self.run_command(['npm', '--version'])

        if success:
            logger.info(f"{Colors.OKGREEN}✓ npm {version_str} 已安装{Colors.ENDC}")
            return True
        else:
            logger.warning(f"{Colors.WARNING}⚠ npm 未安装{Colors.ENDC}")
            return False

    def check_pnpm(self) -> bool:
        """检查pnpm"""
        logger.info("检查 pnpm...")

        success, version_str = self.run_command(['pnpm', '--version'])

        if success:
            logger.info(f"{Colors.OKGREEN}✓ pnpm {version_str} 已安装{Colors.ENDC}")
            return True
        else:
            logger.warning(f"{Colors.WARNING}⚠ pnpm 未安装{Colors.ENDC}")
            return False

    def install_pnpm(self) -> bool:
        """使用npm安装pnpm"""
        logger.info("正在安装 pnpm...")

        success, output = self.run_command(
            ['npm', 'install', '-g', 'pnpm'],
            capture_output=True
        )

        if success:
            logger.info(f"{Colors.OKGREEN}✓ pnpm 安装成功{Colors.ENDC}")
            return True
        else:
            logger.error(f"{Colors.FAIL}✗ pnpm 安装失败: {output}{Colors.ENDC}")
            return False

    def check_git(self) -> bool:
        """检查Git"""
        logger.info("检查 Git...")

        success, version_str = self.run_command(['git', '--version'])

        if success:
            logger.info(f"{Colors.OKGREEN}✓ {version_str}{Colors.ENDC}")
            return True
        else:
            logger.error(f"{Colors.FAIL}✗ Git 未安装{Colors.ENDC}")
            return False

    def check_all(self) -> bool:
        """
        检查所有依赖

        Returns:
            是否全部满足
        """
        logger.info(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}第1步: 检查系统依赖{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        checks = {
            'Python (>= 3.8)': self.check_python((3, 8)),
            'Git': self.check_git(),
            'Node.js (>= 16)': self.check_nodejs(16),
            'npm': self.check_npm(),
        }

        # pnpm可选，如果没有则尝试安装
        if not self.check_pnpm():
            if checks['npm']:
                if self.install_pnpm():
                    checks['pnpm'] = True
                else:
                    checks['pnpm'] = False
            else:
                checks['pnpm'] = False
        else:
            checks['pnpm'] = True

        # 必需依赖
        required = ['Python (>= 3.8)', 'Git']
        required_ok = all(checks[dep] for dep in required)

        # 可选依赖
        optional = ['Node.js (>= 16)', 'npm', 'pnpm']
        optional_ok = all(checks[dep] for dep in optional)

        logger.info(f"\n{Colors.BOLD}依赖检查结果:{Colors.ENDC}")
        for dep, status in checks.items():
            status_str = f"{Colors.OKGREEN}✓{Colors.ENDC}" if status else f"{Colors.FAIL}✗{Colors.ENDC}"
            logger.info(f"  {status_str} {dep}")

        if not required_ok:
            logger.error(
                f"\n{Colors.FAIL}错误: 缺少必需依赖，请先安装 Python 3.8+ 和 Git{Colors.ENDC}"
            )
            return False

        if not optional_ok:
            logger.warning(
                f"\n{Colors.WARNING}警告: 部分可选依赖未安装，memex-cli 功能可能受限{Colors.ENDC}"
            )

        return True


class MemexInstaller:
    """memex-cli 安装器"""

    MEMEX_REPO = "https://github.com/chaorenex1/memex-cli"

    def __init__(self, install_dir: Optional[Path] = None):
        """
        初始化安装器

        Args:
            install_dir: 安装目录（默认：~/.memex/cli）
        """
        self.install_dir = install_dir or Path.home() / '.memex' / 'cli'

    def check_installed(self) -> bool:
        """检查memex-cli是否已安装"""
        try:
            result = subprocess.run(
                ['memex', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"{Colors.OKGREEN}✓ memex-cli 已安装: {result.stdout.strip()}{Colors.ENDC}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return False

    def install(self) -> bool:
        """
        安装memex-cli

        Returns:
            是否安装成功
        """
        logger.info(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}第2步: 安装 memex-cli{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        # 检查是否已安装
        if self.check_installed():
            logger.info("memex-cli 已存在，跳过安装")
            return True

        logger.info(f"准备安装 memex-cli 到 {self.install_dir}")

        # 创建安装目录
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # 克隆仓库
        logger.info(f"正在克隆 {self.MEMEX_REPO}...")
        try:
            subprocess.run(
                ['git', 'clone', self.MEMEX_REPO, str(self.install_dir)],
                check=True,
                capture_output=True,
                timeout=120
            )
            logger.info(f"{Colors.OKGREEN}✓ 仓库克隆成功{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            # 如果目录已存在且不是空的，尝试pull
            if self.install_dir.exists() and any(self.install_dir.iterdir()):
                logger.info("目录已存在，尝试更新...")
                try:
                    subprocess.run(
                        ['git', '-C', str(self.install_dir), 'pull'],
                        check=True,
                        timeout=60
                    )
                    logger.info(f"{Colors.OKGREEN}✓ 仓库更新成功{Colors.ENDC}")
                except subprocess.CalledProcessError as e2:
                    logger.error(f"{Colors.FAIL}✗ 仓库更新失败: {e2}{Colors.ENDC}")
                    return False
            else:
                logger.error(f"{Colors.FAIL}✗ 克隆失败: {e}{Colors.ENDC}")
                return False

        # 运行安装脚本（如果存在）
        install_script = self.install_dir / 'install.sh'
        if install_script.exists():
            logger.info("运行 memex-cli 安装脚本...")
            try:
                subprocess.run(
                    ['bash', str(install_script)],
                    cwd=str(self.install_dir),
                    check=True,
                    timeout=300
                )
                logger.info(f"{Colors.OKGREEN}✓ memex-cli 安装成功{Colors.ENDC}")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"{Colors.FAIL}✗ 安装脚本执行失败: {e}{Colors.ENDC}")
                return False
        else:
            logger.warning(f"{Colors.WARNING}⚠ 未找到安装脚本，跳过{Colors.ENDC}")
            logger.info(f"{Colors.OKGREEN}✓ memex-cli 仓库已克隆{Colors.ENDC}")
            return True


class WorkflowInstaller:
    """coding-agent-workflow 安装器"""

    WORKFLOW_REPO = "https://github.com/chaorenex1/coding-agent-workflow.git"

    def __init__(self, install_dir: Optional[Path] = None):
        """
        初始化安装器

        Args:
            install_dir: 安装目录（默认：~/.claude）
        """
        self.install_dir = install_dir or Path.home() / '.claude'
        self.temp_dir = Path.home() / '.memex' / 'temp' / 'coding-agent-workflow'

    def install(self, force: bool = True) -> bool:
        """
        克隆并安装 coding-agent-workflow

        Args:
            force: 是否覆盖已存在的文件

        Returns:
            是否安装成功
        """
        logger.info(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}第3步: 安装 coding-agent-workflow{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        # 创建临时目录
        self.temp_dir.parent.mkdir(parents=True, exist_ok=True)

        # 如果临时目录已存在，先删除
        if self.temp_dir.exists():
            logger.info("清理旧的临时目录...")
            shutil.rmtree(self.temp_dir)

        # 克隆仓库到临时目录
        logger.info(f"正在克隆 {self.WORKFLOW_REPO}...")
        try:
            subprocess.run(
                ['git', 'clone', self.WORKFLOW_REPO, str(self.temp_dir)],
                check=True,
                capture_output=True,
                timeout=120
            )
            logger.info(f"{Colors.OKGREEN}✓ 仓库克隆成功{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            logger.error(f"{Colors.FAIL}✗ 克隆失败: {e}{Colors.ENDC}")
            return False

        # 安装资源到用户目录
        resources = {
            'slash-commands': 'slash-commands',
            'agents': 'agents',
            'skills': 'skills',
            'prompts': 'prompts'
        }

        success_count = 0
        for src_name, dst_name in resources.items():
            src_path = self.temp_dir / src_name
            dst_path = self.install_dir / dst_name

            if not src_path.exists():
                logger.warning(f"{Colors.WARNING}⚠ 未找到 {src_name}，跳过{Colors.ENDC}")
                continue

            # 创建目标目录
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制资源
            try:
                if dst_path.exists():
                    if force:
                        logger.info(f"覆盖已存在的 {dst_name}...")
                        shutil.rmtree(dst_path)
                    else:
                        logger.info(f"跳过已存在的 {dst_name}")
                        continue

                shutil.copytree(src_path, dst_path)
                logger.info(f"{Colors.OKGREEN}✓ 安装 {dst_name} 到 {dst_path}{Colors.ENDC}")
                success_count += 1
            except Exception as e:
                logger.error(f"{Colors.FAIL}✗ 安装 {dst_name} 失败: {e}{Colors.ENDC}")

        # 清理临时目录
        logger.info("清理临时文件...")
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"{Colors.WARNING}⚠ 清理临时目录失败: {e}{Colors.ENDC}")

        if success_count > 0:
            logger.info(f"{Colors.OKGREEN}✓ 成功安装 {success_count} 个资源{Colors.ENDC}")
            return True
        else:
            logger.error(f"{Colors.FAIL}✗ 未安装任何资源{Colors.ENDC}")
            return False


class DependencyInstaller:
    """Skill依赖安装器"""

    ALIYUN_MIRROR = "https://mirrors.aliyun.com/pypi/simple/"

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        初始化依赖安装器

        Args:
            skills_dir: Skills目录
        """
        self.skills_dir = skills_dir or Path.home() / '.claude' / 'skills'

    def find_requirements_files(self) -> List[Path]:
        """
        查找所有requirements.txt文件

        Returns:
            requirements文件路径列表
        """
        if not self.skills_dir.exists():
            return []

        return list(self.skills_dir.rglob('requirements.txt'))

    def install_requirements(self, requirements_file: Path) -> bool:
        """
        安装单个requirements文件

        Args:
            requirements_file: requirements.txt路径

        Returns:
            是否安装成功
        """
        logger.info(f"安装依赖: {requirements_file.parent.name}...")

        try:
            subprocess.run(
                [
                    sys.executable, '-m', 'pip', 'install',
                    '-r', str(requirements_file),
                    '-i', self.ALIYUN_MIRROR,
                    '--trusted-host', 'mirrors.aliyun.com'
                ],
                check=True,
                capture_output=True,
                timeout=300
            )
            logger.info(f"{Colors.OKGREEN}✓ 依赖安装成功{Colors.ENDC}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{Colors.FAIL}✗ 依赖安装失败: {e.stderr}{Colors.ENDC}")
            return False

    def install_all(self) -> bool:
        """
        安装所有Skill依赖

        Returns:
            是否全部安装成功
        """
        logger.info(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}第4步: 安装 Skill 依赖{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        requirements_files = self.find_requirements_files()

        if not requirements_files:
            logger.info("未找到 requirements.txt 文件，跳过依赖安装")
            return True

        logger.info(f"发现 {len(requirements_files)} 个 requirements.txt 文件")

        success_count = 0
        for req_file in requirements_files:
            if self.install_requirements(req_file):
                success_count += 1

        if success_count == len(requirements_files):
            logger.info(f"{Colors.OKGREEN}✓ 所有依赖安装成功{Colors.ENDC}")
            return True
        else:
            logger.warning(
                f"{Colors.WARNING}⚠ {success_count}/{len(requirements_files)} "
                f"个依赖安装成功{Colors.ENDC}"
            )
            return success_count > 0


class CacheInitializer:
    """本地缓存初始化器"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录（默认：~/.memex/orchestrator）
        """
        self.cache_dir = cache_dir or Path.home() / '.memex' / 'orchestrator'

    def create_structure(self) -> bool:
        """
        创建缓存目录结构

        Returns:
            是否创建成功
        """
        logger.info(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}第5步: 初始化本地缓存{Colors.ENDC}")
        logger.info(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        directories = [
            self.cache_dir,
            self.cache_dir / 'skills',
            self.cache_dir / 'commands',
            self.cache_dir / 'agents',
            self.cache_dir / 'prompts',
            self.cache_dir / 'logs',
            self.cache_dir / 'config',
        ]

        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"{Colors.OKGREEN}✓ 创建目录: {directory}{Colors.ENDC}")

            # 创建配置文件
            config_file = self.cache_dir / 'config' / 'orchestrator.json'
            if not config_file.exists():
                config = {
                    "version": "3.0.0",
                    "auto_discover": True,
                    "enable_parallel": True,
                    "max_parallel_workers": 3,
                    "cache_enabled": True,
                    "created_at": str(Path.ctime(self.cache_dir))
                }
                config_file.write_text(json.dumps(config, indent=2), encoding='utf-8')
                logger.info(f"{Colors.OKGREEN}✓ 创建配置文件: {config_file}{Colors.ENDC}")

            logger.info(f"{Colors.OKGREEN}✓ 缓存目录初始化完成{Colors.ENDC}")
            return True

        except Exception as e:
            logger.error(f"{Colors.FAIL}✗ 缓存目录创建失败: {e}{Colors.ENDC}")
            return False


def main():
    """主安装流程"""
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrator 自动化安装脚本")
    parser.add_argument('--skip-deps', action='store_true', help='跳过依赖检查')
    parser.add_argument('--skip-memex', action='store_true', help='跳过 memex-cli 安装')
    parser.add_argument('--skip-workflow', action='store_true', help='跳过 workflow 安装')
    parser.add_argument('--skip-requirements', action='store_true', help='跳过 requirements 安装')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 70)
    print("  Orchestrator V3 - 自动化安装程序")
    print("=" * 70)
    print(f"{Colors.ENDC}\n")

    results = []

    try:
        # 1. 检查系统依赖
        if not args.skip_deps:
            checker = DependencyChecker()
            if not checker.check_all():
                raise InstallationError("系统依赖检查失败")
            results.append(("依赖检查", True))
        else:
            logger.info(f"{Colors.WARNING}跳过依赖检查{Colors.ENDC}")

        # 2. 安装 memex-cli
        if not args.skip_memex:
            memex_installer = MemexInstaller()
            if not memex_installer.install():
                logger.warning(f"{Colors.WARNING}⚠ memex-cli 安装失败（非致命错误）{Colors.ENDC}")
                results.append(("memex-cli", False))
            else:
                results.append(("memex-cli", True))
        else:
            logger.info(f"{Colors.WARNING}跳过 memex-cli 安装{Colors.ENDC}")

        # 3. 安装 coding-agent-workflow
        if not args.skip_workflow:
            workflow_installer = WorkflowInstaller()
            if not workflow_installer.install(force=True):
                raise InstallationError("coding-agent-workflow 安装失败")
            results.append(("workflow", True))
        else:
            logger.info(f"{Colors.WARNING}跳过 workflow 安装{Colors.ENDC}")

        # 4. 安装 Skill 依赖
        if not args.skip_requirements:
            dep_installer = DependencyInstaller()
            if not dep_installer.install_all():
                logger.warning(f"{Colors.WARNING}⚠ 部分依赖安装失败（非致命错误）{Colors.ENDC}")
                results.append(("Skill依赖", False))
            else:
                results.append(("Skill依赖", True))
        else:
            logger.info(f"{Colors.WARNING}跳过 requirements 安装{Colors.ENDC}")

        # 5. 初始化缓存
        cache_init = CacheInitializer()
        if not cache_init.create_structure():
            raise InstallationError("缓存目录初始化失败")
        results.append(("缓存初始化", True))

        # 总结
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("=" * 70)
        print("  安装完成")
        print("=" * 70)
        print(f"{Colors.ENDC}\n")

        success_count = sum(1 for _, status in results if status)
        total_count = len(results)

        logger.info(f"{Colors.BOLD}安装结果:{Colors.ENDC}")
        for name, status in results:
            status_str = f"{Colors.OKGREEN}✓{Colors.ENDC}" if status else f"{Colors.WARNING}⚠{Colors.ENDC}"
            logger.info(f"  {status_str} {name}")

        if success_count == total_count:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ 所有组件安装成功！{Colors.ENDC}\n")
            print("下一步:")
            print("  1. 配置环境变量（如果需要）")
            print("  2. 运行测试: python orchestrator/tests/test_phase5_simple.py")
            print("  3. 启动 MasterOrchestrator")
            return 0
        else:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ 部分组件安装失败或跳过{Colors.ENDC}\n")
            print("请检查上述错误信息")
            return 1

    except InstallationError as e:
        logger.error(f"\n{Colors.FAIL}{Colors.BOLD}✗ 安装失败: {e}{Colors.ENDC}\n")
        return 1
    except KeyboardInterrupt:
        logger.info(f"\n{Colors.WARNING}安装被用户中断{Colors.ENDC}\n")
        return 130
    except Exception as e:
        logger.error(f"\n{Colors.FAIL}{Colors.BOLD}✗ 未预期的错误: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
