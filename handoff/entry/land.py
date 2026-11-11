#!/usr/bin/env python3
"""Replace a home section in the main checkout by its rewritten text. usage: land.py <name> <part file rel>"""
import sys, os
S = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(S, "..", ".."))
name, part = sys.argv[1:3]
old = open(f"{S}/{name}.old.md").read().rstrip("\n"); new = open(f"{S}/{name}.new.md").read().rstrip("\n")
p = f"{ROOT}/{part}"; t = open(p).read()
n = t.count(old)
if n != 1: sys.exit(f"FAIL {name}: old section found {n} times in {part}")
open(p, "w").write(t.replace(old, new)); print(f"landed {name} in {part}")
