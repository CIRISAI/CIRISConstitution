#!/usr/bin/env python3
"""Is every lifecycle in the state table carried by a model?

For every variable of formal/STATE_TABLE.tsv, find a model behind it: a model_ref on at least one
of its states, or a row of formal/INVARIANTS.tsv that names it. Print the variables that have none.
Exit 1 if any variable has none: the set of lifecycles with no checked machine must stay empty.
"""
import csv, os, sys
from collections import OrderedDict, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rows(p):
    with open(os.path.join(ROOT, p), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))
def main():
    st, iv = rows("formal/STATE_TABLE.tsv"), rows("formal/INVARIANTS.tsv")
    named = defaultdict(set)
    for r in iv:
        for v in r["variables"].split():
            named[v].add(r["model"])
    seen = OrderedDict()
    for r in st:
        d = seen.setdefault(r["variable"], {"plane": r["plane"], "models": set(), "text_only": []})
        if r["model_ref"] not in ("—", ""):
            d["models"].add(r["model_ref"].split(".")[0])
        else:
            d["text_only"].append(r["state"])
    gaps = [(v, d) for v, d in seen.items() if not (d["models"] | named.get(v, set()))]
    partial = [(v, d) for v, d in seen.items() if (d["models"] | named.get(v, set())) and d["text_only"]]
    print(f"lifecycle coverage: {len(seen) - len(gaps)}/{len(seen)} variables carried by a model; "
          f"{len(partial)} with text-only states; {sum(len(d['text_only']) for _, d in seen.items())} text-only states of {len(st)}")
    for v, d in partial:
        print(f"  partial [{d['plane']}] {v}: text-only {', '.join(d['text_only'])}")
    for v, d in gaps:
        print(f"  GAP [{d['plane']}] {v}")
    return 1 if gaps else 0
if __name__ == "__main__":
    sys.exit(main())
