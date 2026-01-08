#!/usr/bin/env python3 -u
# -*- coding: utf-8 -*-
"""
__main__.py - Entry point for master-orchestrator V3.0

Enables running master-orchestrator as a module or script:
    python -u master_orchestrator.py "your request"
    python -u master_orchestrator.py "实现用户登录功能" -v
    python -u master_orchestrator.py "设计登录界面" --dry-run

Note: -u flag enables unbuffered output for real-time display
"""

import sys
import os

# Force unbuffered output (real-time display)
os.environ['PYTHONUNBUFFERED'] = '1'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Import main function from simplified orchestrator
from master_orchestrator import main

if __name__ == "__main__":
    sys.exit(main())
