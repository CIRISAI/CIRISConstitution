#!/usr/bin/env python3
"""Relative-link existence gate for the constitution (CIRISConstitution#113).

Every Markdown link in constitution/*.md and README.md whose target is a
relative path must name a file that exists in this repository. Anchors
(`#...`) and absolute URLs are not checked here: the toc gate owns section
identity, and a URL's liveness is not this repo's to assert.

Why this exists: the CC was extracted from CIRISRegistry, and eleven links
kept pointing at `../../MISSION.md` — a path that resolved in the old tree
and silently stopped resolving in this one. A fold moves files again; a
gate that fails on the first dangling path is cheaper than a reader who
finds it.

Exit 1 on any dangling target. `--quiet` prints only failures.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def targets(path):
    text = open(path, encoding="utf-8").read()
    for m in LINK.finditer(text):
        t = m.group(1)
        if t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "://" in t:
            continue
        yield t.split("#", 1)[0], text.count("\n", 0, m.start()) + 1


def main():
    quiet = "--quiet" in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, "constitution", "*.md"))) + [
        os.path.join(ROOT, "README.md")]
    dangling, checked = [], 0
    for f in files:
        base = os.path.dirname(f)
        for rel, line in targets(f):
            if not rel:
                continue
            checked += 1
            if not os.path.exists(os.path.normpath(os.path.join(base, rel))):
                dangling.append((os.path.relpath(f, ROOT), line, rel))
    for f, line, rel in dangling:
        print(f"DANGLING {f}:{line} -> {rel}")
    if not quiet:
        print(f"check_links: {checked} relative link(s) in {len(files)} file(s), "
              f"{len(dangling)} dangling")
    return 1 if dangling else 0


if __name__ == "__main__":
    sys.exit(main())
