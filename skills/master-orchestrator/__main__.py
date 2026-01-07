#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__main__.py - Entry point for python master_orchestrator.py

Enables running master-orchestrator as a module:
    python master_orchestrator.py "your request"
    python master_orchestrator.py "/discover"
    python master_orchestrator.py "/stats"
"""

import sys

print("[DEBUG] __main__.py 开始导入", file=sys.stderr)
from .master_orchestrator import main
print("[DEBUG] main 函数导入成功", file=sys.stderr)

if __name__ == "__main__":
    print("[DEBUG] 开始执行 main()", file=sys.stderr)
    sys.exit(main())
