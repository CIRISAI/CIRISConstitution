#!/usr/bin/env python3
"""Check constitution/mesh_config_keys.tsv, the closed key registry of mesh_config:{key} (CC 4.2.1 rule (2)): the
columns are the stated ones in order, every key is unique and well formed, min <= owner_default <= max where all three
are numbers, more_flow is `higher` or `lower`, consumer is `yes` or `no`, every cited section is in the table of
contents, and the cells the text leaves `unstated` do not grow past their ceiling. Two deliberate breaks must be caught.
stdlib only. Run: python3 tools/check_mesh_config_keys.py"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "constitution", "mesh_config_keys.tsv")
COLS = ["key", "unit", "min", "max", "owner_default", "more_flow", "consumer", "cc_ref"]
KEY = re.compile(r"^[a-z0-9][a-z0-9_]*(\.[a-z0-9][a-z0-9_]*)+$")
UNSTATED_MAX = 18   # cells the text leaves unstated; the number only falls


def load(path=TSV):
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    rd = csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE)
    return rd.fieldnames, list(rd)


def defects(cols, rows, toc):
    bad, seen, unstated = [], set(), 0
    if cols != COLS:
        bad.append("columns %s are not %s" % (cols, COLS))
        return bad, unstated
    for r in rows:
        k = r["key"]
        if k in seen: bad.append("%s: stated twice" % k)
        seen.add(k)
        if not KEY.match(k): bad.append("%s: not a dotted lower-case key" % k)
        unstated += sum(1 for c in COLS if r[c] == "unstated")
        nums = [r[c] for c in ("min", "owner_default", "max")]
        for c in ("min", "owner_default", "max"):
            if r[c] != "unstated" and not re.fullmatch(r"-?\d+", r[c]): bad.append("%s: %s %r is not an integer" % (k, c, r[c]))
        if all(re.fullmatch(r"-?\d+", n) for n in nums):
            lo, d, hi = (int(n) for n in nums)
            if not lo <= d <= hi: bad.append("%s: min %d, owner_default %d, max %d out of order" % (k, lo, d, hi))
        if r["more_flow"] not in ("higher", "lower", "unstated"): bad.append("%s: more_flow %r" % (k, r["more_flow"]))
        if r["consumer"] not in ("yes", "no"): bad.append("%s: consumer %r" % (k, r["consumer"]))
        for s in r["cc_ref"].split():
            if not re.search(r"(^|\n)%s\t" % re.escape(s), toc): bad.append("%s: section %s is not in the table of contents" % (k, s))
    if not rows: bad.append("no keys")
    return bad, unstated


def main():
    toc = open(os.path.join(ROOT, "constitution", "toc.tsv"), encoding="utf-8").read()
    cols, rows = load()
    bad, unstated = defects(cols, rows, toc)
    if unstated > UNSTATED_MAX: bad.append("%d cells unstated, more than %d" % (unstated, UNSTATED_MAX))
    # deliberate breaks: a default outside its range, and a direction outside the closed pair
    plant1 = [dict(rows[0], owner_default=str(int(rows[0]["max"]) + 1))] + rows[1:]
    plant2 = [dict(rows[0], more_flow="more")] + rows[1:]
    caught = all(defects(cols, p, toc)[0] for p in (plant1, plant2))
    if not caught: bad.append("a deliberate break was not caught")
    for b in bad: print("mesh config keys:", b)
    print("mesh config keys: %d keys, %d without a consumer, %d cells unstated; 2 deliberate breaks %s; %d defect(s)"
          % (len(rows), sum(r["consumer"] == "no" for r in rows), unstated, "caught" if caught else "NOT CAUGHT", len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
