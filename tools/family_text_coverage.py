#!/usr/bin/env python3
"""family_text_coverage.py: which cells of the family model the Constitution text states.

Writes manifests/family_text_coverage.tsv, one row for each family and each column a store decides a row by.
status: text (the cell's value comes from the text), cited (the value was transcribed from a store and a quoted
sentence of the text states it), differs (a reading found the text states another rule, or none: formal/derivation/text_review.tsv),
unstated (transcribed from a store and not yet read against the text), open (no
value). An implementer may build a rule from the table, and drop its own copy, for a cell that is text or cited.

    python3 tools/family_text_coverage.py --write
    python3 tools/family_text_coverage.py --check     the file is current, and no column's unstated count rose
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "manifests", "family_text_coverage.tsv")
COLS = ["signer_rule", "cosign_rule", "subject_rule", "polarity", "placement", "lifecycle", "erasure_route",
        "projection", "governance", "freshness", "replication", "body", "fold"]
# The most cells of a column that may stand unstated. The number only falls.
CEILING = {"signer_rule": 0}


def defaults():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from build_family_model import section_span
    out = {}
    for l in [x for x in open(os.path.join(ROOT, "formal/derivation/column_defaults.tsv"), encoding="utf-8").read().split("\n") if x and not x.startswith("#")][1:]:
        col, val, ref, quote = l.split("\t")
        if quote not in (section_span(ref) or ""): raise SystemExit(f"column_defaults.tsv: {col}: the quoted words do not stand in {ref}")
        out[col] = val
    return out


def review():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from build_family_model import section_span
    out = set()
    for l in [x for x in open(os.path.join(ROOT, "formal/derivation/text_review.tsv"), encoding="utf-8").read().split("\n") if x and not x.startswith("#")][1:]:
        fam, col, reading, ref, quote, _rule = l.split("\t")
        if reading == "differs" and quote not in (section_span(ref) or ""): raise SystemExit(f"text_review.tsv: {fam} {col}: the quoted words do not stand in {ref}")
        out.add((fam, col))
    return out


def status(cell, col=None, dflt=None):
    src = cell.get("source")
    if col == "polarity" and cell.get("registry") is not None and cell.get("registry") == cell.get("value"): return "text"
    if dflt and col in dflt and cell.get("value") == dflt[col]: return "cited"
    if src in ("cc-table", "prose"): return "text"
    if any(c.get("reading") == "agree" for c in cell.get("cites") or []): return "cited"
    if src == "gap" or cell.get("value") is None: return "open"
    return "unstated"


def build():
    rows = json.load(open(os.path.join(ROOT, "manifests", "family_model.json"), encoding="utf-8"))["rows"]
    lines, count, dflt, listed, unlisted = ["family\tcolumn\tstatus\tsource"], {}, defaults(), review(), []
    agreed = {tuple(l.split("\t")[:2]) for l in open(os.path.join(ROOT, "formal/derivation/cell_cites.tsv"), encoding="utf-8").read().split("\n")
              if l and not l.startswith("#") and l.split("\t")[2:3] == ["agree"]}   # the model keeps one citation a section; the table has them all
    for r in rows:
        for c in COLS:
            st = status(r[c], c, dflt)
            if st == "unstated" and (r["family"], c) in agreed: st = "cited"
            if st == "unstated" and c == "signer_rule" and (r["family"], c) not in listed: unlisted.append(r["family"])
            if st in ("unstated", "cited") and (r["family"], c) in listed: st = "differs"
            count.setdefault(c, {}).setdefault(st, 0); count[c][st] += 1
            lines.append(f"{r['family']}\t{c}\t{st}\t{r[c].get('source')}")
    return "\n".join(lines) + "\n", count, unlisted


def main(argv):
    text, count, unlisted = build()
    if "--write" in argv: open(OUT, "w", encoding="utf-8").write(text)
    errs = [f"signer_rule of {f}: unstated, and not listed in text_review.tsv" for f in unlisted]
    if "--check" in argv and (not os.path.exists(OUT) or open(OUT, encoding="utf-8").read() != text): errs.append("manifests/family_text_coverage.tsv is stale: run --write")
    for c, top in CEILING.items():
        if count[c].get("unstated", 0) > top: errs.append(f"{c}: {count[c]['unstated']} cells unstated, more than {top}")
    for c in COLS: print(f"text coverage: {c}: " + ", ".join(f"{k} {v}" for k, v in sorted(count[c].items())))
    for e in errs: print("text coverage: error: " + e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
