#!/usr/bin/env python3
"""Exact one-occurrence replace in a file. usage: sub.py <file> ; reads pairs from stdin as python literal list of (old,new)."""
import sys, ast
p = sys.argv[1]; t = open(p).read()
for old, new in ast.literal_eval(sys.stdin.read()):
    if t.count(old) != 1: sys.exit(f"FAIL: {t.count(old)} occurrences of {old[:70]!r}")
    t = t.replace(old, new)
open(p, "w").write(t); print("ok", p)
