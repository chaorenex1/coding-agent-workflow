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
from .master_orchestrator import main

if __name__ == "__main__":
    sys.exit(main())
