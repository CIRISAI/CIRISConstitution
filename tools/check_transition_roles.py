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
     one allowed to open it is a closed door wearing a policy.

Prints the grid summary: per role token, how many transitions and families it opens. Exit 1 on
any breach.

  python3 tools/check_transition_roles.py
"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TR = json.loads((ROOT / "manifests" / "transitions.json").read_text())


def main():
    meta = TR["_meta"]
    declared = set(meta["role_tokens"])
    states = set(meta["states"])
    errs = []
    used = Counter()
    fams_by_role = defaultdict(set)
    gaps = 0
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
    if gaps != meta.get("gap_cells", gaps) and "gap_cells" in meta:
        pass  # gap_cells counts roles, policy and widens gaps together; the roles gaps are reported below
    if errs:
        print("transition roles: FAIL"); [print("  " + e) for e in errs]
        return 1
    total = sum(len(f["transitions"]) for f in TR["rows"])
    print(f"transition roles: {len(TR['rows'])} families x {len(declared)} role tokens, {total} transitions, "
          f"{gaps} role gaps; every token declared and used, every family with an exit has an entry")
    for r, n in used.most_common():
        print(f"  {r:32s} {n:4d} transitions  {len(fams_by_role[r]):4d} families")
    return 0


if __name__ == "__main__":
    sys.exit(main())
