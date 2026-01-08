#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Orchestrator V3.0 - Simplified Routing System

简化路由系统，只处理两种专业任务：
1. 代码开发任务 → code-with-codex
2. UX 设计任务 → ux-design-gemini
其他任务由 Claude Code 直接处理

变更记录：
- V3.0 (2026-01-08): 简化重构，移除复杂的意图分析层，只保留简单的关键词路由
- V2.0: LRU 缓存 + 智能路由（已废弃）
- V1.0: 初始版本（已废弃）
"""

import sys
import subprocess
import argparse
import logging
from typing import Optional, Dict, Any

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 任务分类关键词
CODE_KEYWORDS = [
    '实现', '开发', '编写代码', '重构', '修复', 'bug', 'fix',
    '添加功能', '实现功能', '编写', '代码', 'implement', 'develop',
    'refactor', '重构代码', '修复代码', '开发系统', '实现系统',
    '创建模块', '编写函数', '实现接口', '开发接口', '编写脚本'
]

UX_KEYWORDS = [
    '设计界面', 'ui', 'ux', '原型', '交互设计', '用户体验',
    '界面设计', '原型设计', '设计', 'wireframe', 'prototype',
    '用户界面', '交互', 'design interface', '设计ui', '设计ux',
    '设计交互', '界面原型', '用户流程', 'user flow', '设计规范'
]


class SimplifiedOrchestrator:
    """
    简化版协调器 - 只路由代码开发和 UX 设计任务

    设计原则：
    - KISS (Keep It Simple, Stupid): 移除所有不必要的抽象层
    - 单一职责：只做任务分类和委托，不做复杂的意图分析
    - 0 依赖：除了标准库 + memex-cli，不依赖任何其他组件
    """

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """
        初始化协调器

        Args:
            verbose: 是否输出详细日志
            dry_run: 是否只显示路由决策而不执行
        """
        self.verbose = verbose
        self.dry_run = dry_run

    def classify_task(self, request: str) -> str:
        """
        分类任务类型（基于简单的关键词匹配）

        Args:
            request: 用户请求

        Returns:
            "code" - 代码开发任务
            "ux" - UX 设计任务
            "direct" - 其他任务（直接执行）
        """
        request_lower = request.lower()

        # 检查代码开发关键词
        if any(keyword in request_lower for keyword in CODE_KEYWORDS):
            return "code"

        # 检查 UX 设计关键词
        if any(keyword in request_lower for keyword in UX_KEYWORDS):
            return "ux"

        # 其他任务
        return "direct"

    def route_task(self, request: str) -> Dict[str, Any]:
        """
        路由任务到对应的 skill

        Args:
            request: 用户请求

        Returns:
            包含执行结果的字典
        """
        task_type = self.classify_task(request)

        if self.verbose:
            logger.info(f"[Routing] Task type: {task_type}")
            logger.info(f"[Routing] Request: {request}")

        if task_type == "code":
            return self._delegate_to_codex(request)
        elif task_type == "ux":
            return self._delegate_to_gemini(request)
        else:
            return self._direct_execution_notice(request)

    def _delegate_to_codex(self, request: str) -> Dict[str, Any]:
        """
        委托给 code-with-codex skill

        通过调用 memex-cli 的 codex 后端实现
        """
        if self.verbose:
            logger.info(f"[Delegation] Routing to: code-with-codex")

        if self.dry_run:
            return {
                "success": True,
                "mode": "dry-run",
                "task_type": "code",
                "delegation": "code-with-codex",
                "backend": "codex",
                "message": "[DRY-RUN] Would delegate to code-with-codex skill (codex backend)"
            }

        # 调用 memex-cli 执行 codex 后端
        cmd = [
            "memex-cli", "run",
            "--backend", "codex",
            "--prompt", request,
            "--stream-format", "text"
        ]

        if self.verbose:
            logger.info(f"[Execution] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            return {
                "success": result.returncode == 0,
                "task_type": "code",
                "delegation": "code-with-codex",
                "backend": "codex",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "task_type": "code",
                "delegation": "code-with-codex",
                "backend": "codex",
                "error": "Execution timeout (300s)"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "task_type": "code",
                "delegation": "code-with-codex",
                "backend": "codex",
                "error": "memex-cli not found. Please ensure memex-cli is installed and in PATH."
            }
        except Exception as e:
            return {
                "success": False,
                "task_type": "code",
                "delegation": "code-with-codex",
                "backend": "codex",
                "error": str(e)
            }

    def _delegate_to_gemini(self, request: str) -> Dict[str, Any]:
        """
        委托给 ux-design-gemini skill

        通过调用 memex-cli 的 gemini 后端实现
        """
        if self.verbose:
            logger.info(f"[Delegation] Routing to: ux-design-gemini")

        if self.dry_run:
            return {
                "success": True,
                "mode": "dry-run",
                "task_type": "ux",
                "delegation": "ux-design-gemini",
                "backend": "gemini",
                "message": "[DRY-RUN] Would delegate to ux-design-gemini skill (gemini backend)"
            }

        # 调用 memex-cli 执行 gemini 后端
        cmd = [
            "memex-cli", "run",
            "--backend", "gemini",
            "--prompt", request,
            "--stream-format", "text"
        ]

        if self.verbose:
            logger.info(f"[Execution] Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )

            return {
                "success": result.returncode == 0,
                "task_type": "ux",
                "delegation": "ux-design-gemini",
                "backend": "gemini",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "task_type": "ux",
                "delegation": "ux-design-gemini",
                "backend": "gemini",
                "error": "Execution timeout (300s)"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "task_type": "ux",
                "delegation": "ux-design-gemini",
                "backend": "gemini",
                "error": "memex-cli not found. Please ensure memex-cli is installed and in PATH."
            }
        except Exception as e:
            return {
                "success": False,
                "task_type": "ux",
                "delegation": "ux-design-gemini",
                "backend": "gemini",
                "error": str(e)
            }

    def _direct_execution_notice(self, request: str) -> Dict[str, Any]:
        """
        返回直接执行提示

        对于不需要路由的任务，返回提示让 Claude Code 直接处理
        """
        return {
            "success": True,
            "task_type": "direct",
            "delegation": "none",
            "message": (
                "[Direct Execution] This task should be handled directly by Claude Code.\n"
                "No routing to master-orchestrator needed.\n"
                f"Task: {request}\n\n"
                "Suggested action: Use native Claude Code tools (Write/Edit/Bash/Read/Grep/Glob)"
            )
        }

    def process(self, request: str) -> Dict[str, Any]:
        """
        处理请求的主入口

        Args:
            request: 用户请求

        Returns:
            执行结果字典
        """
        return self.route_task(request)


def format_output(result: Dict[str, Any], verbose: bool = False, dry_run: bool = False) -> None:
    """
    格式化输出结果

    Args:
        result: 执行结果字典
        verbose: 是否详细输出
        dry_run: 是否 dry-run 模式
    """
    if verbose or dry_run:
        logger.info("\n" + "="*70)
        logger.info("Master Orchestrator V3.0 - Execution Result")
        logger.info("="*70)

    if result.get("mode") == "dry-run":
        logger.info(f"\n[Dry-Run Mode]")
        logger.info(f"Task Type: {result['task_type']}")
        logger.info(f"Delegation: {result['delegation']}")
        logger.info(f"Backend: {result.get('backend', 'N/A')}")
        logger.info(f"\n{result['message']}")
    elif result["task_type"] == "direct":
        logger.info(f"\n{result['message']}")
    else:
        if result["success"]:
            logger.info(f"\n[Success] Task completed")
            logger.info(f"Task Type: {result['task_type']}")
            logger.info(f"Delegation: {result['delegation']}")
            logger.info(f"Backend: {result.get('backend', 'N/A')}")
            if result.get("output"):
                logger.info(f"\nOutput:\n{result['output']}")
        else:
            logger.error(f"\n[Error] Task failed")
            logger.error(f"Task Type: {result['task_type']}")
            logger.error(f"Delegation: {result['delegation']}")
            logger.error(f"Backend: {result.get('backend', 'N/A')}")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")

    if verbose or dry_run:
        logger.info("="*70)


def main():
    """主函数 - 命令行入口"""
    parser = argparse.ArgumentParser(
        description='Master Orchestrator V3.0 - Simplified Routing System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Code development task
  python master_orchestrator.py "实现用户登录功能" -v

  # UX design task
  python master_orchestrator.py "设计登录界面" -v

  # Dry-run to see routing decision
  python master_orchestrator.py "实现登录功能" --dry-run

  # Direct execution (no routing)
  python master_orchestrator.py "运行 npm test" -v
        """
    )

    parser.add_argument(
        'request',
        type=str,
        help='Task request in natural language'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Show routing decision without execution'
    )

    args = parser.parse_args()

    # 创建协调器
    orchestrator = SimplifiedOrchestrator(
        verbose=args.verbose,
        dry_run=args.dry_run
    )

    # 处理请求
    result = orchestrator.process(args.request)

    # 格式化输出
    format_output(result, verbose=args.verbose, dry_run=args.dry_run)

    # 返回退出码
    if not result["success"]:
        sys.exit(1)


if __name__ == '__main__':
    main()
