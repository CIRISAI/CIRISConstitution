#!/usr/bin/env python3
"""
CC — the signer gate, closed over the data: every row the tables have someone sign is a row the door admits
from them, and every row a guard waits for is a row someone may sign.

The readings of the text found that who may sign a row is the kind of rule that drifts most (CC 4.5.5, CC 3.4.7.1).
This check reads the three manifests and holds four properties. It reads no prose.

  1. reserved    a family the registry reserves is not open to any registered key: its entry transition names a
                 role or a condition on the signer, or is a pinned open cell.
  2. emitter     every row a reaction emits is one its emitter may sign: the `by` of an `emit F by R` is a role of
                 F's entry transition (CC 4.5.13: an emitted row enters by the door like any other).
  3. reachable   every row a guard requires (one, all, latest) is of a family whose entry transition someone may
                 sign, so no guard waits for a row the door refuses to everyone.
  4. counted     a transition that runs a policy which is not one voice names at least one role, so a count is
                 never opened by nobody.
  5. duty        an enforced action is admitted from exactly its duty-holder set (CC 4.5.5, as role tokens in
                 formal/derivation/duty_holders.tsv).

A failure that is known and waits on a decision is listed in KNOWN with its conflict id; the list only shrinks.

Run: python3 tools/check_signer_gate.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_grammar as gg

J = lambda p: json.load(open(os.path.join(ROOT, "manifests", p), encoding="utf-8"))
ENTRY = ("attest", "authorize")
SUBSTRATE = ("identity:substrate_persist", "identity:substrate_edge", "identity:lenscore_detector")
# (property, family or `family <- emitter`) -> the conflict that records it
KNOWN = {
    ("emitter", "consent:state:{stance} <- identity:substrate_persist"): "C450: the text gives the expired stance to the store alone; the signer cell (the shipped store) admits the subject and the owner only",
    ("duty", "takedown_notice:{basis}"): "C536: the signer cell (the shipped store) admits a takedown holder; CC 4.5.5 also admits the content's subject and, on a hash match, the detecting node's owner",
    ("duty", "slashing:{outcome}"): "C447, C458: the signer cell (the shipped store) admits any registered key; CC 4.5.5 admits a slash duty-holder",
    ("emitter", "key_grant:{axis} <- identity:substrate_persist"): "C556: CC 3.3.4 has the store emit the catch-up grants and CC 3.1.3 makes a key grant sealer-only; the emitter token names a role and not whose store",
}


def families_of(name, fams):
    if name in fams: return [name]
    if name.endswith(":*"): return [f for f in fams if f.startswith(name[:-1])]
    return [f for f in fams if "{" in f and gg.family_ok(name, {f})]


def main():
    tr = J("transitions.json"); reg = J("namespace_registry.json"); rx = J("reactions.json")
    rows = {r["family"]: r for r in tr["rows"]}
    entry = {f: [t for t in r["transitions"] if t["verb"] in ENTRY] for f, r in rows.items()}
    roles = {f: sorted({x for t in ts for x in t["roles"]["value"]}) for f, ts in entry.items()}
    open_cell = {f for f, ts in entry.items() if any(t["roles"]["source"] == "gap" for t in ts)}
    fails = []

    # 1. reserved
    reserved = set()
    for f in reg["families"]:
        if f.get("reserved"):
            reserved.add(f["prefix"]); reserved.update(f.get("leaves", []))
    for f in sorted(reserved & set(rows)):
        if f in open_cell: continue
        conds = [c for t in entry[f] for c in (t["roles"].get("conditions") or [])]
        if conds: continue          # reserved by a condition on the signer (no self-emit), not by a role
        if not roles[f] or roles[f] == ["registered"]:
            fails.append(("reserved", f, f"reserved in the registry and its entry transition is open to {roles[f] or 'nobody'}"))

    # 2. emitter
    for e in rx["reactions"]:
        if e["kind"] != "react": continue
        for x in e["effects"]:
            if x["effect"] != "emit": continue
            targets = families_of(x["family"], set(rows))
            if not targets:
                fails.append(("emitter", f"{x['family']} <- {x['by']}", f"a reaction of {e['family']} emits a family the model has no row for")); continue
            by = x["by"]
            for t in targets:
                ok = (by in roles[t]) or (by == "author") or (by == "origin_door" and any(r in roles[t] for r in SUBSTRATE)) or t in open_cell
                if not ok:
                    fails.append(("emitter", f"{t} <- {by}", f"a reaction of {e['family']} has {by} emit it; its entry transition admits {roles[t] or 'nobody'}"))

    # 3. reachable
    def req(cs):
        for c in cs:
            if "group" in c: yield from req(c["group"])
            else:
                a = c["atom"]
                if a["atom"] == "row" and a["quant"] in ("one", "all", "latest") and "of" in a["families"] and (c["else"] or {}).get("do") != "advise":
                    yield from a["families"]["of"]
    for f, r in rows.items():
        for t in r["transitions"]:
            for g in t["guard"]["value"]:
                for name in req(gg.parse(g["guard"])[0]):
                    targets = families_of(name, set(rows))
                    if not targets:
                        fails.append(("reachable", f"{f} needs {name}", "the guard requires a row of a family the model has no row for")); continue
                    if all(not roles[x] and x not in open_cell for x in targets):
                        fails.append(("reachable", f"{f} needs {name}", "the guard requires a row nobody may sign"))

    # 4. counted
    for f, r in rows.items():
        for t in r["transitions"]:
            pol = t["policy"]["value"]["policy"]
            if pol != "selfAct" and not t["roles"]["value"] and t["roles"]["source"] != "gap":
                fails.append(("counted", f"{f} {t['verb']}", f"runs {pol} and names no role"))

    # 5. duty
    from build_family_model import section_span
    for l in [x for x in open(os.path.join(ROOT, "formal", "derivation", "duty_holders.tsv"), encoding="utf-8").read().split("\n") if x and not x.startswith("#")][1:]:
        fam, holders, ref, quote = l.split("\t")
        span = section_span(ref)
        if fam not in rows or span is None or quote not in span:
            fails.append(("duty", fam, f"duty_holders.tsv: no such family, or the quoted words do not stand in {ref}")); continue
        want = sorted(h.strip() for h in holders.split("|"))
        if roles[fam] != want and fam not in open_cell:
            fails.append(("duty", fam, f"CC 4.5.5 gives {want}; the entry transition admits {roles[fam]}"))

    seen, new, known = set(), [], []
    for prop, key, why in fails:
        if (prop, key) in seen: continue
        seen.add((prop, key))
        (known if (prop, key) in KNOWN else new).append((prop, key, why))
    gone = [k for k in KNOWN if k not in seen]
    by = {}
    for prop, _, _ in new + known: by[prop] = by.get(prop, 0) + 1
    for prop, key, why in new: print(f"  FAIL {prop}: {key}: {why}")
    for k in gone: print(f"  FAIL a listed failure no longer fails; remove it from KNOWN: {k}")
    print(f"signer gate: {len(rows)} families; reserved {len(reserved & set(rows))}, reaction emits checked, guard requirements checked; "
          f"{len(known)} known failures listed, {len(new)} new" + (f" ({by})" if by else ""))
    return 1 if new or gone else 0


if __name__ == "__main__":
    sys.exit(main())
