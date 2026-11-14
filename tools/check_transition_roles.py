#!/usr/bin/env python3
"""Every family's transitions against every role token: the coverage grid of CC 4.5.13.

Reads manifests/transitions.json and checks the grid of families x role tokens that the queue
generator serves from:

  1. every role token a transition names is declared in the manifest's role_tokens, and every
     declared token opens at least one transition (no phantom standing, no silent one);
  2. a transition with no roles is a declared gap (roles.source = gap) or a held-shut family,
     never an undeclared closure;
  3. every family that has a transition out of admitted also has a way in (attest or authorize
     from none), so no family's rows can only be withdrawn;
  4. every from and to state is one of the manifest's states, and no two transitions of one
     family share (verb, from), so the door has one answer per (view, verb);
  5. the entry transition of a family with a policy row carries roles, since a window with no
     one allowed to open it is a closed door wearing a policy;
  6. a cell that carries stages names declared tokens in every stage, and its value is their union;
  7. every open cell is on the pinned list below, with the question that would close it, and the
     list names nothing that has closed: a new gap fails, and so does a pin left behind;
  8. a reserved family is never open to any registered key without a condition, unless pinned:
     a reservation that admits everyone reserves nothing.

An open cell is a roles, policy or widens cell whose source is gap: the queue generator treats the
transition as closed (roles, policy) or as not widening (widens) until the text says otherwise.
A transition with an open widens cell is still confirmed where it has no way back (the confirm cell).

Prints the grid summary: per role token, how many transitions and families it opens. Exit 1 on
any breach.

  python3 tools/check_transition_roles.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TR = json.loads((ROOT / "manifests" / "transitions.json").read_text())
FM = json.loads((ROOT / "manifests" / "family_model.json").read_text())

# The cells the text leaves open, each with the question whose answer closes it. Closing one means a
# row in formal/derivation/signer_rule_text.tsv or transition_text.tsv (or a census cell) and the
# removal of its line here; the check fails on a gap that is not listed and on a line that has closed.
PINNED = {
    ("duty:{kind}", "attest", "roles"):
        "CC 2.7.5 places a duty by the object's own key; which role token names the signer of the permission a duty attaches to?",
}


def main():
    meta = TR["_meta"]
    declared = set(meta["role_tokens"])
    states = set(meta["states"])
    errs = []
    used = Counter()
    fams_by_role = defaultdict(set)
    gaps = 0
    open_cells, open_reserved = [], []
    reserved = {r["family"] for r in FM["rows"] if isinstance(r.get("reserved"), dict) and r["reserved"].get("value") is True}
    for f in TR["rows"]:
        fam = f["family"]
        seen = set()
        has_entry = False
        for t in f["transitions"]:
            key = (t["verb"], t["from"])
            if key in seen:
                errs.append(f"{fam}: two transitions share {key}")
            seen.add(key)
            if t["from"] not in states or t["to"] not in states:
                errs.append(f"{fam}: {t['verb']} uses a state outside the manifest: {t['from']} -> {t['to']}")
            if t["from"] == "none":
                has_entry = True
            roles = t["roles"]["value"]
            for cell in ("roles", "policy", "widens"):
                if t[cell]["source"] == "gap":
                    open_cells.append((fam, t["verb"], cell))
            stages = t["roles"].get("stages")
            if stages is not None:
                for stage, toks in stages.items():
                    for r in toks:
                        if r not in declared:
                            errs.append(f"{fam}: {t['verb']} stage {stage} names the undeclared role token {r}")
                if sorted({r for toks in stages.values() for r in toks}) != sorted(roles):
                    errs.append(f"{fam}: {t['verb']} roles are not the union of its stages")
            for stage, pol in (t["policy"].get("stages") or {}).items():
                if stages is None or stage not in stages:
                    errs.append(f"{fam}: {t['verb']} gives a policy to the stage {stage}, which its roles do not name")
                elif pol.get("rows") and not stages[stage]:
                    errs.append(f"{fam}: {t['verb']} stage {stage} runs policy rows {pol['rows']} with no one allowed to open it")
            if (t["from"] == "none" and fam in reserved and roles == ["registered"]
                    and not t["roles"].get("conditions")):
                open_reserved.append((fam, t["verb"], "roles"))
            if not roles:
                if t["roles"]["source"] == "gap":
                    gaps += 1
                elif t["roles"]["source"] != "code-v61":
                    errs.append(f"{fam}: {t['verb']} has no roles and is not a declared gap ({t['roles']['source']})")
                pol = t["policy"]["value"]
                if isinstance(pol, dict) and pol.get("rows"):
                    errs.append(f"{fam}: {t['verb']} runs policy rows {pol['rows']} with no one allowed to open it")
            for r in roles:
                used[r] += 1
                fams_by_role[r].add(fam)
                if r not in declared:
                    errs.append(f"{fam}: {t['verb']} names the undeclared role token {r}")
        if not has_entry and any(t["from"] == "admitted" for t in f["transitions"]):
            errs.append(f"{fam}: rows can be withdrawn or recanted but never admitted")
    for r in sorted(declared - set(used)):
        errs.append(f"declared role token {r} opens no transition")
    if len(open_cells) != meta.get("gap_cells"):
        errs.append(f"the manifest counts {meta.get('gap_cells')} gap cells and carries {len(open_cells)}")
    for key in open_cells:
        if key not in PINNED:
            errs.append(f"{key[0]}: {key[1]} {key[2]} is open and not pinned; close it from the text or pin it with its question")
    for key in open_reserved:
        if key not in PINNED:
            errs.append(f"{key[0]}: reserved, and its {key[1]} is open to any registered key with no condition")
    for key in sorted(set(PINNED) - set(open_cells) - set(open_reserved)):
        errs.append(f"{key[0]}: {key[1]} {key[2]} is pinned as open and has closed; remove the pin")
    if errs:
        print("transition roles: FAIL"); [print("  " + e) for e in errs]
        return 1
    total = sum(len(f["transitions"]) for f in TR["rows"])
    print(f"transition roles: {len(TR['rows'])} families x {len(declared)} role tokens, {total} transitions, "
          f"{gaps} role gaps; every token declared and used, every family with an exit has an entry")
    for r, n in used.most_common():
        print(f"  {r:32s} {n:4d} transitions  {len(fams_by_role[r]):4d} families")
    entry_registered = sum(1 for f in TR["rows"] for t in f["transitions"] if t["from"] == "none" and t["roles"]["value"] == ["registered"])
    print(f"open cells: {len(open_cells)}; reserved families open to any registered key: {len(open_reserved)}; "
          f"pinned: {len(PINNED)}; families whose entry is any registered key: {entry_registered} of {len(TR['rows'])}")
    for key in sorted(set(open_cells) | set(open_reserved)):
        print(f"  {key[0]:36s} {key[1]:8s} {key[2]:7s} {PINNED[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
