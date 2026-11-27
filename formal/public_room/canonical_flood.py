#!/usr/bin/env python3
"""A flood of every federation-scope row a canonical node would accept, family by family. Work in progress, not gated.

The families and who may sign each are READ from manifests/family_model.json (the placement and emitter_class cells),
so the list is the text's and not this file's. A family is OPEN where a key with no seat, no roster and no grant may
place a row of it in the Commons: its emitter class is a person, a self or an owner, and its placement admits
`commons`. Everything else needs standing some count or grant gave, and a flood of it is a flood by keys that hold
that standing, which their room or root can end.

Four gates are priced for the open families, each adding to the one before:
  G0  admit and hold whatever verifies
  G1  the receiver's rates before any cryptography (per sender key, node-wide)
  G2  hold a row only where its author is in the node's trust set (CC 4.4.3.34), within a walk of depth d
  G3  and hold a stranger's row only where a row by a trusted key names it, for as long as that row stands
Rates and sizes are parameters, marked assumed where the text fixes none.
  python3 formal/public_room/canonical_flood.py [--check] [--list]
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROWS = json.load(open(os.path.join(ROOT, "manifests", "family_model.json")))["rows"]
val = lambda c: c.get("value") if isinstance(c, dict) else c

OPEN_EMITTERS = {"person", "self", "owner", "owner|self"}

def commons(r):
    p = val(r.get("placement"))
    return (isinstance(p, list) and "commons" in p) or (isinstance(p, str) and p.startswith("commons"))

def key_plane(r):
    p = val(r.get("placement")); rep = val(r.get("replication"))
    return (isinstance(p, str) and "key plane" in p) or (isinstance(rep, dict) and rep.get("audience") == "key-plane reach")

def klass(r):
    e = val(r.get("emitter_class"))
    if key_plane(r): return "key_plane"
    if not commons(r): return "not_commons"
    return "open" if e in OPEN_EMITTERS else "standing"

# The key plane is what a node cannot refuse from a stranger without cutting the stranger off from the mesh: a key's own
# record and what binds it. It is read from the model (the placement and replication cells), not listed here.

P = dict(row_bytes=3900, verify_per_core_s=5000,          # assumed
         node_verify_budget_s=200, per_sender_budget_s=2,  # assumed
         trusted_keys=10_000,                              # assumed: keys within the node's walk
         cites_per_trusted_key_day=20)                     # assumed: strangers' rows a trusted key names in a day

def gates(flood_rows_s, flood_keys, seconds, p=P):
    day = seconds / 86400
    g0 = flood_rows_s * seconds
    g1 = min(flood_rows_s, p["node_verify_budget_s"], flood_keys * p["per_sender_budget_s"]) * seconds
    g2 = 0                                                   # no flooding key is in the trust set
    g3 = min(g1, p["trusted_keys"] * p["cites_per_trusted_key_day"] * day)   # only what trusted keys chose to name
    return {"G0": g0, "G1": g1, "G2": g2, "G3": g3}

def main():
    by = {"open": [], "standing": [], "not_commons": [], "key_plane": []}
    for r in ROWS: by[klass(r)].append(r["family"])
    must = by["key_plane"]
    speech = by["open"]
    print("families: %d; reach the Commons: %d; OPEN there to a key with no standing: %d; need standing: %d; key plane (a stranger's own key rows): %d"
          % (len(ROWS), len(by["open"]) + len(by["standing"]), len(speech), len(by["standing"]), len(must)))
    if "--list" in sys.argv:
        print("must admit from a stranger:", ", ".join(sorted(must)))
        print("open speech:", ", ".join(sorted(speech)))
        print("need standing:", ", ".join(sorted(by["standing"])))
    print()
    print("ONE DAY of flood at one canonical, rows held at the end (GB), by gate")
    print("%10s %12s | %12s %12s %8s %12s" % ("rows/s", "keys", "G0 all", "G1 rates", "G2 trust", "G3 cited"))
    res = []
    for rate in (1e3, 1e5, 1e7):
        for keys in (1e2, 1e9):
            g = gates(rate, keys, 86400); res.append((rate, keys, g))
            gb = lambda n: n * P["row_bytes"] / 1e9
            print("%10.0f %12.0f | %12.1f %12.1f %8.1f %12.1f" % (rate, keys, gb(g["G0"]), gb(g["G1"]), gb(g["G2"]), gb(g["G3"])))
    print()
    print("What each gate leaves: G1 bounds work and leaves storage growing at the node's own ceiling for ever; G2 holds")
    print("nothing from the flood and admits no stranger at all; G3 holds exactly what trusted keys named, so a stranger")
    print("enters by being vouched, cited or answered, and a flood enters only as fast as trusted keys choose to cite it.")
    if "--check" in sys.argv:
        assert len(by["open"]) > 0 and len(by["standing"]) > 0
        # 1. With no gate the flood is held in full; the rates alone still hold the node's whole ceiling every second.
        for rate, keys, g in res:
            assert g["G0"] == rate * 86400 and g["G1"] <= P["node_verify_budget_s"] * 86400
        # 2. Trust alone holds nothing of a flood, at any rate and any number of keys.
        assert all(g["G2"] == 0 for _, _, g in res)
        # 3. Citation is bounded by what trusted keys do, never by the flood: the same at every rate above the ceiling.
        hi = [g["G3"] for r, k, g in res if k == 1e9 and r >= 1e5]
        assert len(set(hi)) == 1 and hi[0] <= P["trusted_keys"] * P["cites_per_trusted_key_day"]
        # 4. More keys never raise what is held past the node's own ceiling.
        assert all(g["G1"] <= P["node_verify_budget_s"] * 86400 for _, _, g in res)
        print("check: ok")

if __name__ == "__main__":
    main()
