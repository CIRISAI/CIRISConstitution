#!/usr/bin/env python3
"""
CC — the formal state table and invariant table, kept honest.

  formal/STATE_TABLE.tsv   one row per (plane, variable, state) of a mesh node's normalized state
                           vector: where the text defines it, what row enters it, who signs, which
                           model variable or value realises it, which CSD/4 atoms imply it, status.
  formal/INVARIANTS.tsv    one row per checked property across every model in formal/: symbol,
                           kind, statement, the same property restated over the state table's
                           variables, the CC decimal, the claim id, the TLC/Lean verdict, and how
                           far the normalization goes (full | partial | model-internal).
  manifests/topology_vocabulary.json  the CSD/4 atom vocabulary (published by CC), each atom mapped to a state-table predicate.

Checks (exit 1 on any failure):
  - every INVARIANTS symbol exists in its source file (grep); every source file exists;
  - every cc_ref decimal in both tables exists in constitution/toc.tsv;
  - every variable an invariant names is a variable of the state table;
  - every claim_id named exists in constitution/claims.tsv (or is noted as proposed);
  - every atom the state table names is in the vocabulary, and the vocabulary's in_state_table flags agree;
  - prints the counts: states by plane and status, invariants by model and normalization.
Run:  python3 tools/check_formal_tables.py
"""
import csv, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "formal", "STATE_TABLE.tsv")
IV = os.path.join(ROOT, "formal", "INVARIANTS.tsv")
VOC = os.path.join(ROOT, "manifests", "topology_vocabulary.json")


def rows(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    errs = []
    toc = {r["decimal_id"] for r in rows(os.path.join(ROOT, "constitution", "toc.tsv"))}
    claims = {r["claim_id"] for r in rows(os.path.join(ROOT, "constitution", "claims.tsv"))}
    st, iv = rows(ST), rows(IV)
    voc = json.load(open(VOC, encoding="utf-8"))
    variables = {r["variable"] for r in st}
    # decimals
    for tbl, name in ((st, "STATE_TABLE"), (iv, "INVARIANTS")):
        for r in tbl:
            for d in r["cc_ref"].replace("(", " ").replace(")", " ").split():
                if re.fullmatch(r"\d+(\.\d+)*", d) and d not in toc:
                    errs.append(f"{name}: unknown CC decimal {d} on {r.get('variable') or r.get('inv_id')}")
    # symbols
    srccache = {}
    for r in iv:
        p = os.path.join(ROOT, r["source"])
        if not os.path.exists(p):
            errs.append(f"INVARIANTS {r['inv_id']}: source missing {r['source']}"); continue
        txt = srccache.setdefault(p, open(p, encoding="utf-8", errors="replace").read())
        sym = r["symbol"]
        pat = (rf"theorem\s+{re.escape(sym)}\b" if p.endswith(".lean")
               else rf"(#\s*{re.escape(sym)}\b|^\s*def\s+{re.escape(sym)}\s*\()" if p.endswith(".py")
               else rf"^{re.escape(sym)}\s*==")
        if not re.search(pat, txt, re.M):
            errs.append(f"INVARIANTS {r['inv_id']}: symbol {sym} not found in {r['source']}")
        for v in r["variables"].split():
            v = v.strip("(),")
            if v and re.match(r"^[a-z_]+\.[a-z_]+$", v) and v not in variables:
                errs.append(f"INVARIANTS {r['inv_id']}: variable {v} not in the state table")
        if r["claim_id"] not in claims and not r["claim_id"].endswith("(proposed)"):
            errs.append(f"INVARIANTS {r['inv_id']}: claim {r['claim_id']} not in claims.tsv")
    # atoms
    table_atoms = {a for r in st for a in r["atoms"].split() if a != "—"}
    for a in table_atoms:
        if a not in voc["atoms"]:
            errs.append(f"STATE_TABLE names atom {a} that the vocabulary lacks")
    for a, d in voc["atoms"].items():
        if d["in_state_table"] != (a in table_atoms):
            errs.append(f"vocabulary {a}: in_state_table flag disagrees with the table")
    # report
    plane = Counter(r["plane"] for r in st); status = Counter(r["status"] for r in st)
    model = Counter(r["model"] for r in iv); norm = Counter(r["normalization"].split(":")[0].split(" ")[0] for r in iv)
    print(f"state table: {len(st)} states over {len(variables)} variables in {len(plane)} planes")
    print("  by plane:  " + ", ".join(f"{k} {v}" for k, v in sorted(plane.items())))
    print("  by status: " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())))
    print(f"invariants: {len(iv)} across {len(model)} models")
    print("  by model:  " + ", ".join(f"{k} {v}" for k, v in sorted(model.items())))
    print("  normalization: " + ", ".join(f"{k} {v}" for k, v in sorted(norm.items())))
    covered = {v for r in iv for v in r["variables"].split() if v in variables}
    print(f"  variables with at least one invariant: {len(covered)}/{len(variables)}; without: "
          + ", ".join(sorted(variables - covered)))
    print(f"vocabulary: {voc['_meta']['n_atoms']} atoms, {sum(1 for a in table_atoms)} named by the state table")
    for e in errs:
        print("  FAIL", e)
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
