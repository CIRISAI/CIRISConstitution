#!/usr/bin/env python3
"""Repair register phrases an edit moved: a phrase that no longer stands in its section is
replaced by the sentence of the section that begins or ends as it did, or is closest to it.
Prints every change; a phrase it cannot place is listed and left. Run after a text edit and
before tools/check_rule_entries.py.   python3 tools/fix_entries.py"""
import re, sys, difflib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rule_entries as c
p = ROOT / "formal/derivation/rule_entries.tsv"
L = p.read_text().split("\n"); secs = {}; fixed = []; bad = []
for i, l in enumerate(L):
    f = l.split("\t")
    if len(f) != 7 or not i: continue
    h = f[1]
    if h not in secs: secs[h] = "\n".join(c.section(c.HOME_PART[h[0]], h))
    txt = secs[h]; ph = f[6]
    if ph in txt: continue
    new = None
    for k in (45, 30, 20):
        if len(ph) >= k and txt.count(ph[:k]) == 1:
            s = txt.index(ph[:k]); ends = [x for x in (txt.find(". ", s + k), txt.find("\n", s + k)) if x != -1]
            e = min(ends + [s + 320]); new = txt[s:e + 1].rstrip("\n"); break
        if len(ph) >= k and txt.count(ph[-k:]) == 1:
            e = txt.index(ph[-k:]) + k; s = max(txt.rfind(". ", 0, e - k) + 2, txt.rfind("\n", 0, e - k) + 1); new = txt[s:e]; break
    if not new:
        ss = [x for line in txt.split("\n") for x in [line] + re.split(r"(?<=[.])\s+(?=[A-Z*`])", line) if x.strip()]
        best = max(ss, key=lambda s: difflib.SequenceMatcher(None, s[:400], ph[:400]).ratio())
        if difflib.SequenceMatcher(None, best[:400], ph[:400]).ratio() > 0.5: new = best
    if new and new.strip() and new in txt and "\t" not in new:
        f[6] = new; L[i] = "\t".join(f); fixed.append((h, ph[:60], new[:90]))
    else: bad.append((h, ph[:90]))
p.write_text("\n".join(L))
for x in fixed: print("FIX", x)
print("BAD", bad)
