#!/usr/bin/env python3
"""Stamp a status marker on every promise line (rc8 book review, P00: "put a plain status marker
on every promise line, in present tense only for what ships").

Source of truth: review/promise_status.tsv  (surface, key, status, note)
  surface plain    -> review/pieces/00_guarantees_plain.md, line starting "<key>. "
  surface exec     -> constitution/EXECUTIVE_SUMMARY.md, promise paragraph "<key>. **"
  surface operator -> review/pieces/00_operator_digest.md, bullet under "## <section>" whose text
                      starts with "**<lead>" or "<lead>" (key = "<section>|<lead>")
Marker form: " *[status]*" or " *[status; note]*", appended to the line; an existing marker is
replaced, so the run is idempotent. A legend line is kept under each surface's title.
Vocabulary: works today = evidence in the register at a pinned commit; being built = a named
ticket; a rule, no code yet = normative only; modelled = a formal witness, no code test.
Run: python3 tools/build_promise_status.py   (then tools/build_review_piece.py --all)
"""
import csv, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "review", "promise_status.tsv")
FILES = {"plain": "review/pieces/00_guarantees_plain.md",
         "exec": "constitution/EXECUTIVE_SUMMARY.md",
         "operator": "review/pieces/00_operator_digest.md"}
MARK = re.compile(r"\s*\*\[[^\]]*\]\*\s*$")
LEGEND = ("*Status markers:* **works today** = evidence in the register at a pinned commit; "
          "**being built** = a named ticket; **a rule, no code yet** = normative only; "
          "**modelled** = a formal witness, no code test. The markers are stamped from *The Evidence Register*.")

def marker(status, note):
    return f" *[{status}; {note}]*" if note else f" *[{status}]*"

def stamp(lines, idx, status, note):
    lines[idx] = MARK.sub("", lines[idx].rstrip()) + marker(status, note)

def ensure_legend(lines, after_pred):
    for i, ln in enumerate(lines):
        if ln.startswith("*Status markers:*"):
            lines[i] = LEGEND; return
    for i, ln in enumerate(lines):
        if after_pred(ln):
            lines[i+1:i+1] = ["", LEGEND]; return
    raise SystemExit("no legend anchor")

def main():
    rows = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    bysurf = {}
    for r in rows: bysurf.setdefault(r["surface"], []).append(r)
    missing = []
    for surf, rs in bysurf.items():
        path = os.path.join(ROOT, FILES[surf]); lines = open(path, encoding="utf-8").read().split("\n")
        if surf == "plain":
            ensure_legend(lines, lambda l: l.startswith("# "))
            for r in rs:
                hit = [i for i, l in enumerate(lines) if l.startswith(r["key"] + ". ")]
                if len(hit) != 1: missing.append((surf, r["key"], len(hit))); continue
                stamp(lines, hit[0], r["status"], r["note"])
        elif surf == "exec":
            ensure_legend(lines, lambda l: l.startswith("## The eleven promises"))
            for r in rs:
                hit = [i for i, l in enumerate(lines) if re.match(re.escape(r["key"]) + r"\. \*\*", l)]
                if len(hit) != 1: missing.append((surf, r["key"], len(hit))); continue
                stamp(lines, hit[0], r["status"], r["note"])
        else:
            ensure_legend(lines, lambda l: l.startswith("# "))
            for r in rs:
                sec, lead = r["key"].split("|", 1); cur = None; hit = []
                for i, l in enumerate(lines):
                    if l.startswith("## "): cur = l[3:].strip()
                    elif cur == sec and l.startswith("- ") and (l[2:].startswith("**" + lead) or l[2:].startswith(lead)):
                        hit.append(i)
                if len(hit) != 1: missing.append((surf, r["key"], len(hit))); continue
                stamp(lines, hit[0], r["status"], r["note"])
        open(path, "w", encoding="utf-8").write("\n".join(lines))
    if missing:
        for m in missing: print("UNMATCHED", m, file=sys.stderr)
        sys.exit(1)
    print(f"promise status: {len(rows)} markers stamped across {len(bysurf)} surfaces")

if __name__ == "__main__":
    main()
