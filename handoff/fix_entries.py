#!/usr/bin/env python3
"""Compatibility copy: the repair is tools/fix_entries.py. Kept until handoff/ is deleted at the cut."""
import os, runpy, sys
TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "fix_entries.py")
sys.argv[0] = TOOL
runpy.run_path(TOOL, run_name="__main__")
