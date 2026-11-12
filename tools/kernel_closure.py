#!/usr/bin/env python3
"""
CC — how much of what a kernel needs is a rule this document states, and what is left.

A kernel reads its rules from the tables. A cell of a table is one of four things, and only the first is a rule:

    ruled     the text states it, and the cell cites where (cc-table, prose, or derived from cells that are)
    as built  the cell records what the shipped store does (code-v61, mixed): a fact about one implementation
    default   the family takes the general rule, stated once for all or not at all, and nobody has checked that
              the general rule was meant for this family (generic)
    open      nothing says (gap)

Everything that is not `ruled` is a residual: a decision some implementation makes that the tables do not yet
carry. This tool lists the residuals by the kernel output that needs them, so that none is out of sight.

    views       what is true now: fold, lifecycle, projection, body
    queue       what waits on a hand: who may sign, the guard, the way back, confirmation
    counts      the tally an act takes: count, governance, the policy cell
    standing    who holds what, when: signer, subject and cosign rules, freshness, what a row confers
    moves       where a row goes and stays: placement, replication, evidence, derived
    effects     what a node does and signs in time: expiries, clocks, reactions, the erasure route

Run: python3 tools/kernel_closure.py           (--check fails if a ruled count falls; --families lists the worst)
"""
import collections, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, "manifests", p), encoding="utf-8"))
KIND = {"cc-table": "ruled", "prose": "ruled", "derived": "ruled", "code-v61": "as built", "mixed": "as built",
        "generic": "default", "gap": "open", None: "open"}
OUTPUTS = collections.OrderedDict([
    ("views", (("fm", "fold"), ("fm", "lifecycle"), ("fm", "projection"), ("fm", "body"))),
    ("queue", (("tr", "roles"), ("tr", "guard"), ("tr", "undo"), ("tr", "confirm"))),
    ("counts", (("fm", "count"), ("fm", "governance"), ("tr", "policy"))),
    ("standing", (("fm", "signer_rule"), ("fm", "subject_rule"), ("fm", "cosign_rule"), ("fm", "freshness"), ("fm", "confers"))),
    ("moves", (("fm", "placement"), ("fm", "replication"), ("fm", "evidence"), ("fm", "derived"))),
    ("effects", (("rx", "timed"), ("fm", "erasure_route"))),
])
FLOORS = {"fold": 76, "guard": 26, "roles": 311, "signer_rule": 56, "placement": 19, "count": 16, "timed": 33, "body": 81}


def main():
    fm, tr, rx = J("family_model.json"), J("transitions.json"), J("reactions.json")["reactions"]
    timed = {e["family"] for e in rx}
    cells, by_family = {}, collections.Counter()
    for where, col in {c for cs in OUTPUTS.values() for c in cs}:
        k = collections.Counter()
        if where == "fm":
            for r in fm["rows"]:
                kind = KIND.get(r[col].get("source") if isinstance(r.get(col), dict) else None, "open")
                k[kind] += 1
                if kind != "ruled": by_family[r["family"]] += 1
        elif where == "tr":
            for r in tr["rows"]:
                for t in r["transitions"]:
                    kind = KIND.get(t[col].get("source"), "open")
                    k[kind] += 1
                    if kind != "ruled": by_family[r["family"]] += 1
        else:
            for r in fm["rows"]:
                kind = "ruled" if r["family"] in timed else "default"
                k[kind] += 1
        cells[col] = k
    print("What a kernel needs, and how much of it this document states:\n")
    tot = collections.Counter()
    for out, cs in OUTPUTS.items():
        print(f"  {out}")
        for _, col in cs:
            k = cells[col]; n = sum(k.values()); tot.update(k)
            print(f"    {col:14} ruled {k['ruled']:4} of {n:4} {100 * k['ruled'] // n:3}%   as built {k['as built']:4}   default {k['default']:4}   open {k['open']:4}")
    n = sum(tot.values())
    print(f"\nkernel closure: {tot['ruled']} of {n} cells are rules the text states ({100 * tot['ruled'] // n}%); "
          f"{tot['as built']} record what the shipped store does, {tot['default']} take an unstated default, {tot['open']} are open")
    if "--families" in sys.argv:
        print("\nFamilies with the most cells that are not rules:")
        for f, c in by_family.most_common(15): print(f"  {c:3}  {f}")
    if "--check" in sys.argv:
        low = [c for c, f in FLOORS.items() if cells[c]["ruled"] < f]
        if low: print("FAIL a ruled count fell: " + ", ".join(low)); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
