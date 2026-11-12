#!/usr/bin/env python3
"""
CC — how much of the rule text is carried as data: a measure, not a gate.

Every text table under formal/derivation and constitution quotes the words a value rests on. This tool finds each
quote in its Part and marks the rule entry (formal/derivation/rule_entries.tsv: a sentence that states or applies a
rule) whose sentence the quote falls in. It prints, by Part and by table, how many rule entries have a value in
some table resting on them. A marked entry is not yet cut from the prose: the measure says what a cut could reach.

Run: python3 tools/data_coverage.py [--list-uncovered PART]
"""
import csv, glob, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "formal", "derivation")
TABLES = [("cell_text", "cc_ref", "quote"), ("cell_cites", "cc_ref", "quote"), ("policy_text", "cc_ref", "quote"),
          ("count_text", "cc_ref", "quote"), ("guard_text", "cc_ref", "quote"), ("change_text", "cc_ref", "quote"),
          ("fold_text", "cc_ref", "quote"), ("reaction_text", "cc_ref", "quote"), ("body_text", "cc_ref", "quote")]
EXTRA = [(os.path.join(ROOT, "constitution", "consensus_protocols.tsv"), "protocols"),
         (os.path.join(ROOT, "constitution", "protocol_admissibility.tsv"), "admissibility")]


def rows(path):
    lines = [l for l in open(path, encoding="utf-8").read().split("\n") if l and not l.startswith("#")]
    return csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE)


def main():
    parts, heads = {}, {}
    for p in sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))):
        key = "p" + re.search(r"part_(\d)", p).group(1)
        parts[key] = open(p, encoding="utf-8").read()
        heads[key] = [(m.start(), m.group(1)) for m in re.finditer(r"^#{1,6} (\d+(?:\.\d+)*)(?= |$)", parts[key], re.M)]

    def span(part, num):
        """offsets of the section `num` with its subsections"""
        hs = heads[part]
        for i, (at, n) in enumerate(hs):
            if n == num:
                end = next((a for a, m in hs[i + 1:] if not m.startswith(num + ".")), len(parts[part]))
                return at, end
        return None

    all_entries, where = [], defaultdict(list)       # where: part -> [(start, end, entry)]
    unplaced = 0
    for e in rows(os.path.join(D, "rule_entries.tsv")):
        if e["file"] not in parts: continue
        sp = span(e["file"], e["home"])
        at = parts[e["file"]].find(e["entry_phrase"], *(sp or (0, 0))) if sp else -1
        if at < 0:
            unplaced += 1; continue
        all_entries.append(e); where[e["file"]].append([at, None, e])
    for part, lst in where.items():
        lst.sort(key=lambda x: x[0])
        for k, x in enumerate(lst):                  # a sentence runs to the next entry or the end of its line
            eol = parts[part].find("\n", x[0])
            nxt = lst[k + 1][0] if k + 1 < len(lst) else len(parts[part])
            x[1] = min(nxt if nxt > x[0] else eol, eol if eol >= 0 else nxt)
    covered = defaultdict(set)
    quotes = Counter()
    sources = [(os.path.join(D, t + ".tsv"), t) for t, _, _ in TABLES] + EXTRA
    for path, name in sources:
        for r in rows(path):
            m = re.fullmatch(r"CC ((\d)(?:\.\d+)*)", r["cc_ref"])
            if not m: continue
            quotes[name] += 1
            part = "p" + m.group(2)
            sp = span(part, m.group(1))
            if not sp: continue
            at = parts[part].find(r["quote"], *sp)
            while 0 <= at:
                end = at + len(r["quote"])
                for a, b, e in where[part]:
                    if a < end and at < b: covered[id(e)].add(name)
                at = parts[part].find(r["quote"], at + 1, sp[1])
    by_part = Counter(e["file"] for e in all_entries)
    cov_part = Counter(e["file"] for e in all_entries if id(e) in covered)
    total, cov = len(all_entries), len(covered)
    if unplaced: print(f"  ({unplaced} rule entries not found in their home section and left out)")
    print(f"data coverage: {cov} of {total} rule entries ({100 * cov // total}%) have a typed value resting on their sentence")
    print("  by Part: " + "; ".join(f"{p} {cov_part[p]}/{by_part[p]}" for p in sorted(by_part)))
    per = Counter(t for ts in covered.values() for t in ts)
    print("  by table (entries reached; quotes): " + "; ".join(f"{n} {per[n]} ({quotes[n]})" for _, n in sources))
    if "--list-uncovered" in sys.argv:
        part = sys.argv[sys.argv.index("--list-uncovered") + 1]
        homes = Counter(e["home"] for e in all_entries if e["file"] == part and id(e) not in covered)
        for h, n in homes.most_common(25): print(f"  uncovered in CC {h}: {n}")


if __name__ == "__main__":
    main()
