#!/usr/bin/env python3
"""Relative-link gate for the constitution: files and section anchors.

Every Markdown link in constitution/*.md and README.md whose target is a
relative path must name a file that exists in this repository, and every
`#anchor` on a link into a constitution Part must name a section of that
Part: either its decimal id (`#4.5.5`, the stable form) or the GitHub slug of
one of its headings. Absolute URLs are not checked: a URL's liveness is not
this repo's to assert.

`--fix-anchors` rewrites a stale anchor to the decimal form of the section it
meant (matched by the decimal digits in the old slug, then by heading words),
moving the link to the right Part when the section lives in another one, and
lists any it cannot resolve.

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


HEAD = re.compile(r"^(#{1,6}) (.*)$", re.M)
DEC = re.compile(r"^(\d+(?:\.\d+)*) ")
LINKA = re.compile(r"\]\(([^)\s#]*)#([^)\s]+)\)")


def slug(text):
    t = text.strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def sections(path):
    """decimal ids and heading slugs of one file; slug -> decimal for numbered headings."""
    decs, slugs, words = set(), {}, {}
    for m in HEAD.finditer(open(path, encoding="utf-8").read()):
        text = m.group(2)
        d = DEC.match(text)
        dec = d.group(1) if d else None
        s = slug(text)
        slugs[s] = dec
        if dec:
            decs.add(dec)
            words[dec] = set(re.findall(r"[a-z0-9]+", s)) - {dec.replace(".", "")}
    return decs, slugs, words


def part_files():
    return sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md")))


def resolve(anchor, target, index):
    """best decimal section for a stale anchor: (file, decimal) or None."""
    digits = re.match(r"^(\d+)(?:[-.]|$)", anchor.replace(".", "") + "-")
    aw = set(re.findall(r"[a-z0-9]+", anchor.lower()))
    def score(f, dec):
        return len(aw & index[f][2].get(dec, set()))
    cands = []
    if re.fullmatch(r"\d+(?:\.\d+)+", anchor):
        cands = [(f, anchor) for f in index if anchor in index[f][0]]
    elif re.fullmatch(r"\d+(?:-\d+)+", anchor):
        dd = anchor.replace("-", ".")
        cands = [(f, dd) for f in index if dd in index[f][0]]
    elif digits:
        dg = digits.group(1)
        cands = [(f, dec) for f in index for dec in index[f][0] if dec.replace(".", "") == dg]
    if len(cands) > 1:
        cands.sort(key=lambda c: (c[0] == target, score(*c)), reverse=True)
        if score(*cands[0]) == score(*cands[1]) and cands[0][0] == cands[1][0]:
            cands = cands[:1] if score(*cands[0]) > 0 else []
    if not cands:
        best = max(((score(f, d), f, d) for f in index for d in index[f][0]), default=(0, None, None))
        if best[0] >= 3:
            cands = [(best[1], best[2])]
    return cands[0] if cands else None


def check_anchors(files, fix):
    index = {f: sections(f) for f in part_files()}
    bad, fixed = [], 0
    for f in files:
        text = open(f, encoding="utf-8").read()
        base = os.path.dirname(f)
        out, pos = [], 0
        for m in LINKA.finditer(text):
            rel, anchor = m.group(1), m.group(2)
            target = os.path.normpath(os.path.join(base, rel)) if rel else f
            if target not in index:
                continue
            decs, slugs, _ = index[target]
            if anchor in decs or anchor in slugs:
                continue
            line = text.count("\n", 0, m.start()) + 1
            r = resolve(anchor, target, index) if fix else None
            if r:
                tf, dec = r
                newrel = "" if tf == f else os.path.relpath(tf, base)
                out.append(text[pos:m.start()] + f"]({newrel}#{dec})")
                pos = m.end()
                fixed += 1
            else:
                bad.append((os.path.relpath(f, ROOT), line, (rel + "#" if rel else "#") + anchor))
        if fix and out:
            out.append(text[pos:])
            open(f, "w", encoding="utf-8").write("".join(out))
    return bad, fixed


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
    bad, fixed = check_anchors(files, "--fix-anchors" in sys.argv)
    for f, line, a in bad:
        print(f"STALE-ANCHOR {f}:{line} -> {a}")
    if not quiet:
        print(f"check_links: {checked} relative link(s) in {len(files)} file(s), "
              f"{len(dangling)} dangling; {len(bad)} stale anchor(s)"
              + (f"; {fixed} anchor(s) rewritten" if fixed else ""))
    return 1 if dangling or bad else 0


if __name__ == "__main__":
    sys.exit(main())
