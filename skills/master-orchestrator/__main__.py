#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__main__.py - Entry point for python -m master-orchestrator

Enables running master-orchestrator as a module:
    python -m master-orchestrator "your request"
    python -m master-orchestrator "/discover"
    python -m master-orchestrator "/stats"
"""

import sys

print("[DEBUG] __main__.py 开始导入", file=sys.stderr)
from .master_orchestrator import main
print("[DEBUG] main 函数导入成功", file=sys.stderr)

if __name__ == "__main__":
    print("[DEBUG] 开始执行 main()", file=sys.stderr)
    sys.exit(main())
