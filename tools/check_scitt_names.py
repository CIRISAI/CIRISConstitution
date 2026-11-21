#!/usr/bin/env python3
"""check_scitt_names.py: the transparency plane's name table covers every name it should, and is coherent.

manifests/scitt_names.tsv gives a fate to each protocol-visible name that carries one of the plane's words.
This scans the namespace registry, the payload table and Parts 2 to 5 for such names and fails where one has
no row; it fails on a row that names nothing found, on a rename with no new name, on a new name that is itself
given a fate other than new or keep, and on an unknown fate. Exit 1 on any failure.
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = re.compile(r"witness|cosign|transparency|receipt|attach_window|lineage_head", re.I)
FATES = {"rename", "retire", "keep", "new", "open"}
PARTS = ["part_2_the_grammar", "part_3_the_namespace", "part_4_composition_governance", "part_5_transport_substrate"]


def found():
    out = set()
    reg = json.load(open(os.path.join(ROOT, "manifests", "namespace_registry.json"), encoding="utf-8"))
    out |= {("family", f["prefix"]) for f in reg["families"] if WORDS.search(f["prefix"])}
    for l in open(os.path.join(ROOT, "constitution", "signed_object_v2.tsv"), encoding="utf-8"):
        c = l.rstrip("\n").split("\t")
        if len(c) > 3 and c[2].startswith('"') and WORDS.search(c[2]): out.add(("member", f"{c[1]} {c[2].strip(chr(34))}"))
    text = "".join(open(os.path.join(ROOT, "constitution", p + ".md"), encoding="utf-8").read() for p in PARTS)
    out |= {("token", t) for t in re.findall(r"`([a-z][a-z0-9_]{5,})`", text) if WORDS.search(t)}
    return out


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(ROOT, "manifests", "scitt_names.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")][1:]
    errs, table = [], {}
    for r in rows:
        if len(r) != 6: errs.append(f"{r[:2]}: {len(r)} columns"); continue
        surface, name, fate, new, sense, _note = r
        if (surface, name) in table: errs.append(f"{surface} {name}: listed twice")
        table[(surface, name)] = (fate, new)
        if fate not in FATES: errs.append(f"{surface} {name}: unknown fate {fate}")
        if (fate == "rename") != bool(new): errs.append(f"{surface} {name}: a rename names its new name, and nothing else does")
        if not sense: errs.append(f"{surface} {name}: no sense given")
    seen = found()
    for k in sorted(seen - set(table)): errs.append(f"{k[0]} {k[1]}: carries one of the plane's words and has no row")
    for k in sorted(set(table) - seen): errs.append(f"{k[0]} {k[1]}: the table names it and no surface carries it")
    for (surface, name), (fate, new) in table.items():
        if fate != "rename": continue
        tgt = next((v for (s, n), v in table.items() if s == surface and n.split(" ")[-1] == new and n != name), None)
        if tgt and tgt[0] not in ("new", "keep"): errs.append(f"{surface} {name}: its new name {new} is itself {tgt[0]}")
    n = {f: sum(1 for v in table.values() if v[0] == f) for f in sorted(FATES)}
    for e in errs: print("scitt names: error: " + e)
    print(f"scitt names: {len(table)} names; " + ", ".join(f"{k} {v}" for k, v in n.items()) + f"; {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
