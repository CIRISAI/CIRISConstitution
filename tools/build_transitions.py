#!/usr/bin/env python3
"""Derive manifests/transitions.json, the lifecycle transitions of every family, from
manifests/family_model.json (CC 4.5.13 "How the view makes the queue"; formal/event_lifecycle).

One transition per (family, verb): the state it leaves and reaches, the roles that may sign it,
the governance policy it runs under, and whether it widens. Every field carries a `source`:
  cc-table  the registry / CC table (verbs, kind, polarity)
  code-v61  persist's census at the v61 head (signer rule, withdraws_by, governance)
  derived   this tool's rule from those (role token mapping, states, widens)
  gap       nothing in the manifest says; the queue generator must treat the transition as closed
A node derives a person's queue by filtering these by the person's standing in the object's state.

  python3 tools/build_transitions.py            # writes manifests/transitions.json (+ .tsv)
  python3 tools/build_transitions.py --check    # exit 1 if the committed manifest is stale
"""
import json, re, sys, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manifests" / "family_model.json"
OUT = ROOT / "manifests" / "transitions.json"
OUT_TSV = ROOT / "manifests" / "transitions.tsv"

TOKEN_RULES = [  # (regex searched anywhere in the closed signer text, role tokens)
    (r"none \(held shut\)", []),
    (r"seat_role\((\w+)\)", "seat"),
    (r"identity_type contains (\w+)", "identity"),
    (r"roster_member|\bmember\b", ["member"]),
    (r"\bfounder", ["founder"]),
    (r"owner_of_subject|\bowner\b", ["owner"]),
    (r"\bsteward\b", ["steward"]),
    (r"\bholder\b", ["holder"]),
    (r"any_registered", ["registered"]),
    (r"\bself\b", ["self"]),
]

def roles_from_text(s):
    out = []
    for pat, roles in TOKEN_RULES:
        for m in re.finditer(pat, s):
            if roles == "seat": out.append(m.group(1))
            elif roles == "identity": out.append(f"identity:{m.group(1)}")
            elif roles == []: return [], "code-v61"
            else: out += roles
    return (sorted(set(out)), "derived") if out else ([], "gap")

def roles_from_signer(val):
    """Map the manifest's signer rule to role tokens; return (roles, source)."""
    if val is None:
        return [], "gap"
    if isinstance(val, list):
        return roles_from_text(" ".join(map(str, val)))
    if isinstance(val, dict):
        if "who" in val:
            return roles_from_text(str(val.get("who")))
        # per-stage rule (membership): the first stage is the attest transition's signer
        first = next(iter(val.values()), "")
        return roles_from_text(str(first))
    return roles_from_text(str(val))

def withdraw_roles(lifecycle):
    v = (lifecycle or {}).get("withdraws_by") if isinstance(lifecycle, dict) else None
    if v is None:
        return [], "none", "gap"
    s = str(v)
    if "cosigned" in s:
        return ["member"], "cosigned", "code-v61"
    roles = []
    if "attester" in s: roles.append("author")
    if "subject" in s: roles.append("subject")
    return roles, ("selfAct" if roles else "none"), "code-v61"

def policy_from_governance(gov):
    s = str(gov or "none")
    m = re.search(r"policy_row:\s*([\w, ]+)", s)
    if m:
        rows = [x.strip() for x in m.group(1).split(",")]
        return {"policy": "two_path", "rows": rows}, "code-v61"
    if "mirror" in s:
        return {"policy": "mirror", "rows": ["moderation_action"]}, "code-v61"
    if "community_invite" in s:
        return {"policy": "two_path", "rows": ["community_invite", "community_remove"]}, "code-v61"
    return {"policy": "selfAct", "rows": []}, "derived"

def widens(replication, scope_hint):
    rep = replication or {}
    tier = rep.get("tier") if isinstance(rep, dict) else None
    if isinstance(tier, list): tier = "federation" if "federation" in tier else tier[0]
    aud = rep.get("audience") if isinstance(rep, dict) else None
    if tier == "federation":
        return True, "derived"
    if isinstance(aud, dict) or isinstance(aud, str):
        return True, "derived"
    return False, "gap"

def val(cell):
    return cell.get("value") if isinstance(cell, dict) else cell

def build():
    fm = json.loads(SRC.read_text())
    rows = []
    for r in fm["rows"]:
        fam = r["family"]
        verbs = val(r.get("verbs")) or []
        kind = val(r.get("kind"))
        signer = val(r.get("signer_rule"))
        signer_closed = (r.get("signer_rule") or {}).get("closed") if isinstance(r.get("signer_rule"), dict) else None
        lifecycle = val(r.get("lifecycle"))
        gov = val(r.get("governance"))
        rep = val(r.get("replication"))
        roles, rsrc = roles_from_signer(signer_closed or signer)
        pol, psrc = policy_from_governance(gov)
        wd, wsrc = widens(rep, None)
        trans = []
        if "attest" in verbs and roles is not None:
            trans.append({"verb": "attest", "from": "none", "to": "admitted",
                          "roles": {"value": roles, "source": rsrc},
                          "policy": {"value": pol, "source": psrc},
                          "widens": {"value": wd, "source": wsrc}})
        if "withdraw" in verbs:
            wr, wpol, wsrc2 = withdraw_roles(lifecycle)
            trans.append({"verb": "withdraw", "from": "admitted", "to": "withdrawn",
                          "roles": {"value": wr, "source": wsrc2},
                          "policy": {"value": {"policy": wpol, "rows": []}, "source": wsrc2},
                          "widens": {"value": False, "source": "derived"}})
        if "recant" in verbs:
            trans.append({"verb": "recant", "from": "admitted", "to": "recanted",
                          "roles": {"value": ["author"], "source": "cc-table"},
                          "policy": {"value": {"policy": "selfAct", "rows": []}, "source": "cc-table"},
                          "widens": {"value": False, "source": "derived"}})
        for v in ("supersede", "replace"):
            if v in verbs:
                cos = isinstance(lifecycle, dict) and "cosigned" in str(lifecycle.get("retraction_class"))
                trans.append({"verb": "supersede", "from": "admitted", "to": "superseded",
                              "roles": {"value": ["member"] if cos else ["author"], "source": "code-v61" if cos else "derived"},
                              "policy": {"value": {"policy": "cosigned" if cos else "selfAct", "rows": []}, "source": "code-v61" if cos else "derived"},
                              "widens": {"value": False, "source": "derived"}})
                break
        if "authorize" in verbs:
            trans.append({"verb": "authorize", "from": "none", "to": "admitted",
                          "roles": {"value": roles, "source": rsrc},
                          "policy": {"value": pol, "source": psrc},
                          "widens": {"value": True, "source": "derived"}})
        rows.append({"family": fam, "kind": kind, "transitions": trans})
    # gaps summary
    gaps = sum(1 for f in rows for t in f["transitions"] for k in ("roles", "policy", "widens") if t[k]["source"] == "gap")
    total = sum(len(f["transitions"]) for f in rows)
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    out = {"_meta": {"source": "manifests/family_model.json", "source_sha256": src_sha,
                     "cc_section": "4.5.13", "model": "formal/event_lifecycle",
                     "rule": "queue(view, standing) = transitions of the view's family whose from = view.state and whose roles meet standing; one item per transition; the door admits by the same predicate",
                     "states": ["none", "admitted", "withdrawn", "recanted", "superseded"],
                     "role_tokens": sorted({r for f in rows for t in f["transitions"] for r in t["roles"]["value"]}),
                     "families": len(rows), "transitions": total, "gap_cells": gaps,
                     "note": "draft 0: states are the five retraction states of CC 2.4.1.1; a family with its own lifecycle (membership stages, the moderator election, the halt) refines these in its chapter model; gap cells mean the queue generator treats the transition as closed until the manifest says otherwise"},
           "rows": rows}
    tsv = ["family\tverb\tfrom\tto\troles\tpolicy\twidens\troles_src\tpolicy_src\twidens_src"]
    for f in rows:
        for t in f["transitions"]:
            tsv.append("\t".join([f["family"], t["verb"], t["from"], t["to"], ",".join(t["roles"]["value"]),
                                  t["policy"]["value"]["policy"], str(t["widens"]["value"]).lower(),
                                  t["roles"]["source"], t["policy"]["source"], t["widens"]["source"]]))
    return json.dumps(out, indent=1, ensure_ascii=False) + "\n", "\n".join(tsv) + "\n"

def main():
    js, tsv = build()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text() == js and OUT_TSV.exists() and OUT_TSV.read_text() == tsv
        print("transitions: current" if ok else "transitions.json is stale (run tools/build_transitions.py)")
        sys.exit(0 if ok else 1)
    OUT.write_text(js); OUT_TSV.write_text(tsv)
    m = json.loads(js)["_meta"]
    print(f"transitions: {m['families']} families, {m['transitions']} transitions, {m['gap_cells']} gap cells")

if __name__ == "__main__":
    main()
