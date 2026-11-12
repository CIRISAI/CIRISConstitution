#!/usr/bin/env python3
"""
CC — how far the screen standard (manifests/ui_primitives.json, CSD/5) is closed over the typed tables.

A screen is closed over the logic when every value a primitive draws, and every state it may be in, is a cell of
a manifest and nothing is left to a card's author. This tool measures that, cell by cell, and prints for each
primitive what it draws from, how much of that is typed, and what is missing. It changes nothing.

  write side   one line per cell of manifests/transitions.json a primitive draws from, over every family and verb
  read side    the states a StateBlock may be in against the verdicts the folds and reactions actually give
  primitives   each primitive with the cells it binds and whether they close

A verdict the data gives with no state to draw it in is listed by name. The map from verdict to state is BINDS
below and is this tool's reading; a verdict mapped to None is one the standard has no state for.

Run: python3 tools/ui_closure.py            (--check fails if a measure falls below its floor)
"""
import collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, "manifests", p), encoding="utf-8"))

# verdict or act the data gives -> the StateBlock state that draws it (None: the standard has none)
VERDICT_STATE = {
    "withdrawn": "gone", "destroy_bytes": "gone", "unknown": "unknown",
    "lapsed": None, "closed": None, "stale": None, "forfeited": None, "purgeable": None, "locked": None,
    "lagging": None, "stop_serving": None,
}
# primitive -> (the cells it draws from, in the names of MEASURES; empty: it draws what the card gives it)
BINDS = {
    "CardShell": (), "FieldRow": ("body",), "ItemRow": ("roles",), "ScopePill": ("scope",), "Chip": ("verdicts",),
    "Action": ("roles", "reason", "confirm"), "ReceiptSheet": ("body",), "StateBlock": ("verdicts", "fold"),
    "Metric": ("fold",), "ConfirmSheet": ("confirm", "undo", "widens"), "Choice": ("price",),
    "DestinationPicker": ("scope", "widens"), "Field": ("body",), "StepFlow": (), "Ceremony": ("price", "undo", "window", "roles"),
    "LineageChain": ("change",), "CodeCompare": (), "QrCode": (), "Transcript": ("verdicts",), "ConscienceStep": ("fold",),
    "PolicyLens": ("fold",), "GraphView": (), "Document": ("change",), "Media": ("body",),
}
FLOORS = {"roles": 457, "confirm": 459, "undo": 429, "reason": 26, "change": 20, "fold": 76}


def measures():
    tr, rx, fm, ui = J("transitions.json"), J("reactions.json")["reactions"], J("family_model.json"), J("ui_primitives.json")
    T = [(r["family"], t) for r in tr["rows"] for t in r["transitions"]]
    n, nf = len(T), len(tr["rows"])
    m = collections.OrderedDict()
    m["roles"] = (sum(t["roles"]["source"] != "gap" for _, t in T), n, "who may sign: an act that is not the reader's is absent (L5)")
    m["confirm"] = (sum("value" in t["confirm"] for _, t in T), n, "confirmed or one step (L6); %d turn on the scope the row is signed at" % sum(t["confirm"].get("when") == "if_widens" for _, t in T))
    m["widens"] = (sum(t["widens"]["source"] != "gap" for _, t in T), n, "who else will see it")
    m["undo"] = (sum(t["undo"]["source"] != "gap" for _, t in T), n, "whether there is a way back, by which verb, at what price")
    pol = {f["family"] for f in J("governance_policy.json")["families"]}
    priced = [t for _, t in T if t["policy"]["value"].get("policy") != "selfAct"]
    m["price"] = (sum(all(r in pol for r in t["policy"]["value"].get("rows", [])) for _, t in T), n, "what the act takes: %d transitions run a counted policy, each naming rows of the policy table" % len(priced))
    guarded = [t for _, t in T if t["guard"]["value"]]
    tok = bare = 0
    for t in guarded:
        s = json.dumps(t["guard"]["value"])
        tok += len(re.findall(r"else refuse\([a-z_]+\)", s)); bare += len(re.findall(r"else refuse(?!\()", s))
    m["reason"] = (len(guarded), n, "why an act is refused (L5): a guard is typed; of its refusals %d carry a token and %d carry none" % (tok, bare))
    m["change"] = (sum(bool(t["change"]["value"]) for _, t in T), n, "what the row displaces and what follows for rows that depended on it")
    timed = {e["family"] for e in rx}
    m["window"] = (len(timed), nf, "families with an expiry, a clock or a reaction typed")
    m["fold"] = (sum(bool(r["fold"].get("value")) for r in fm["rows"]), len(fm["rows"]), "families whose reading as a set is typed")
    body = [b for r in fm["rows"] if isinstance(r["body"].get("value"), dict) for b in (r["body"]["value"].get("members") or [])]
    m["body"] = (sum(b.get("in_cddl", True) for b in body), len(body), "members a screen may show that the wire schema carries")
    scopes = re.findall(r'"([a-z]+)"', re.search(r"SCOPES = \(([^)]*)\)", open(os.path.join(ROOT, "tools", "change_grammar.py")).read()).group(1))
    circles = ui["context"]["circle"]
    m["scope"] = (len([s for s in scopes if s in circles]), len(scopes), "scopes a row may be signed at that the screen context names; not named: " + ", ".join(s for s in scopes if s not in circles))
    verd = collections.Counter(x["verdict"] for e in rx if e["kind"] == "react" for x in e["effects"] if x["effect"] == "read")
    verd.update(x["act"] for e in rx if e["kind"] == "react" for x in e["effects"] if x["effect"] == "do" and x["act"] in VERDICT_STATE)
    fold_states = sorted({s for r in fm["rows"] for it in (r["fold"].get("value") or []) for mm in re.finditer(r"\?([a-z_]+):([a-z_]+)", it["fold"]) for s in mm.groups()})
    states = set(ui["states"])
    unmapped = sorted(v for v in verd if VERDICT_STATE.get(v) not in states)
    m["verdicts"] = (len(verd) - len(unmapped), len(verd), "verdicts the reactions give that a StateBlock state draws; none for: " + ", ".join(unmapped) +
                     "; and the folds give %d states of their own (%s), none of them a StateBlock state" % (len(fold_states), ", ".join(fold_states)))
    return m, ui


def main():
    m, ui = measures()
    print("The cells a screen draws from, and how much of each is typed:\n")
    for k, (a, b, note) in m.items():
        print(f"  {k:9} {a:4} of {b:4}  {100 * a // b:3}%   {note}")
    print("\nThe primitives:\n")
    closed = partly = free = 0
    for name, p in ui["primitives"].items():
        cells = BINDS[name]
        if not cells: free += 1; verdict = "draws what the card gives it; no rule cell"
        else:
            short = [f"{c} {100 * m[c][0] // m[c][1]}%" for c in cells if m[c][0] < m[c][1]]
            if short: partly += 1; verdict = "open on " + ", ".join(short)
            else: closed += 1; verdict = "closed over " + ", ".join(cells)
        print(f"  {p['basis']} {name:18} {p['status']:12} {verdict}")
    print(f"\nui closure: {len(ui['primitives'])} primitives: {closed} closed over the tables, {partly} open on a cell, {free} bound to no rule cell")
    if "--check" in sys.argv:
        low = [k for k, f in FLOORS.items() if m[k][0] < f]
        if low: print("FAIL a measure fell: " + ", ".join(low)); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
