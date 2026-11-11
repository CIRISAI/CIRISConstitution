#!/usr/bin/env python3
"""Propose rule_entries rows for un-landed sections that have no sentence over the cap.

For each inventory statement of such a section, take the line it was read on (the Part at
30fddf6), split it into sentences or table cells, and pick the one closest to the gist that
still stands verbatim in the section. Writes handoff/register.proposed.tsv with a score column;
low scores are read by hand before anything is appended to rule_entries.tsv.

  python3 handoff/register.py            # propose
"""
import csv, re, subprocess, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rule_entries as c
BASE = "30fddf6"
STOP = set("a an the of to in on at by for and or is are be as it its that this with from not no may must which who what when where than then into under over per each any all only never own".split())
def toks(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return [w for w in re.findall(r"[a-z0-9_]+", s.lower()) if w not in STOP]
def stem(w): return re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w
def score(gist, cand):
    g = [stem(w) for w in toks(gist)]; k = set(stem(w) for w in toks(cand))
    return sum(1 for w in g if w in k) / max(1, len(g))
def pieces(line):
    if line.lstrip().startswith("|"):
        cells = [x.strip() for x in re.split(r"(?<!\\)\|", line)]
        out = [line.strip()] + [x for x in cells if x]
        for cell in cells: out += re.split(r"(?<=[.;])\s+(?=[A-Z*`(])", cell)
        return [o for o in out if o]
    out = [line.strip()]
    out += [s.strip() for s in re.split(r"(?<=[.])\s+(?=[A-Z*`])", line) if s.strip()]
    return out
def overcap(sec, home):
    for para in sec[1:]:
        if not para.strip() or para.lstrip().startswith(("|", "- ")) or para.startswith(c.NEIGHBOURS.get(home, ())): continue
        plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
        for kept in c.EXEMPT: plain = plain.replace(kept, "")
        plain = re.sub(r"\.\*\*(\s)", r".\1", plain)
        if any(len(s.split()) > c.MAX_WORDS for s in re.split(r"(?<=[.])\s+(?=[A-Z*`])", plain)): return True
    return False
def main():
    rd = lambda p: list(csv.DictReader((ROOT / p).open(), delimiter="\t", quoting=csv.QUOTE_NONE))
    landed = {e["home"] for e in rd("formal/derivation/rule_entries.tsv")}
    inv = collections.defaultdict(list)
    for r in rd("formal/derivation/rule_inventory.tsv"): inv[r["section"]].append(r)
    old = {p: subprocess.run(["git", "show", f"{BASE}:constitution/{f}"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n") for p, f in c.PARTS.items()}
    out = []; skipped = []
    for p, f in c.PARTS.items():
        for l in (ROOT / "constitution" / f).read_text().split("\n"):
            m = re.match(r"#+ (\d+(?:\.\d+)+) ", l)
            if not m or m.group(1) in landed: continue
            home = m.group(1); sec = c.section(p, home)
            if overcap(sec, home): continue
            if not inv[home]: skipped.append(home); continue
            text = "\n".join(sec)
            allp = [x for ln in sec[1:] for x in pieces(ln)]
            for r in inv[home]:
                n = int(r["line"]) if r["line"].isdigit() else 0
                near = set()
                for k in range(max(1, n - 6), min(len(old[r["file"]]), n + 6) + 1):
                    near.update(pieces(old[r["file"]][k - 1]))
                best = (-1, "", "none")
                for ln in sec[1:]:
                    ps = pieces(ln)
                    whole, sents = ps[0], [x for x in ps[1:] if len(x.split()) >= 3] or [ps[0]]
                    for x in sents:
                        s = score(r["gist"], x) + (0.15 if x in near else 0)
                        if s > best[0] or (s == best[0] and len(x) < len(best[1])): best = (s, x, "sentence")
                    s = score(r["gist"], whole) + (0.15 if whole in near else 0)
                    if len(whole.split()) <= 70 and s >= best[0] + 0.25: best = (s - 0.001, whole, "line")
                out.append((min(best[0], 1.0), best[2], r, best[1]))
    with (ROOT / "handoff/register.proposed.tsv").open("w") as fh:
        fh.write("score\twhere\trule_key\thome\tfile\tline\trole\tgist\tentry_phrase\n")
        for s, where, r, ph in out:
            fh.write("\t".join([f"{s:.2f}", where, r["rule_key"], r["section"], r["file"], r["line"], r["role"], r["gist"], ph]) + "\n")
    hist = collections.Counter((w, min(10, int(s * 10))) for s, w, _, _ in out)
    print(len(out), "rows;", len({r["section"] for _, _, r, _ in out}), "sections; no inventory:", skipped)
    for k in sorted(hist): print(k, hist[k])
main()
