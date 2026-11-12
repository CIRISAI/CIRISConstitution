#!/usr/bin/env python3
"""Derive manifests/transitions.json, the lifecycle transitions of every family, from
manifests/family_model.json (CC 4.5.13 "How the view makes the queue"; formal/event_lifecycle).

One transition per (family, verb): the state it leaves and reaches, the roles that may sign it,
the governance policy it runs under, whether it widens, whether it has a way back, and so whether
its item is confirmed. Every field carries a `source`:
  cc-table  the registry / CC table (verbs, kind, polarity), and a cell the text states
            (formal/derivation/transition_text.tsv), which then carries its reference as cc_ref
  code-v61  persist's census at the v61 head (signer rule, withdraws_by, governance)
  derived   this tool's rule from those (role token mapping, states, widens, undo, confirm)
  gap       nothing in the manifest says; the queue generator must treat the transition as closed
A node derives a person's queue by filtering these by the person's standing in the object's state.
Where the text gives a family one signer per stage, the roles cell carries the union as its value and
the answer of each stage under `stages`; a signer rule's conditions ride the roles cell as `conditions`.

  python3 tools/build_transitions.py            # writes manifests/transitions.json (+ .tsv)
  python3 tools/build_transitions.py --check    # exit 1 if the committed manifest is stale
"""
import json, re, sys, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "manifests" / "family_model.json"
OUT = ROOT / "manifests" / "transitions.json"
OUT_TSV = ROOT / "manifests" / "transitions.tsv"
TEXT = ROOT / "formal" / "derivation" / "transition_text.tsv"
GUARDS = ROOT / "formal" / "derivation" / "guard_text.tsv"
CHANGES = ROOT / "formal" / "derivation" / "change_text.tsv"
CHANGE_DEFAULT = "replace: by=same_attester, link=ranked:references_attestation_id, reach=own_prior ; withdraw: cascade=*/ref:stand"
CHANGE_MARKS_MAX = {"recovery": 4, "cosigned_prior": 1, "committed_key": 2, "forfeited": 1, "no_weaker": 1}   # each number only falls
GUARD_MARKS_MAX = {"refuse": 32, "ref:*": 10, "landed": 3, "signs": 2, "commits": 1}   # each number only falls
POLICY_ROWS = {f["family"]: f["kind"] for f in json.loads((ROOT / "manifests" / "governance_policy.json").read_text())["families"]}

TOKEN_RULES = [  # (regex searched anywhere in the closed signer text, role tokens)
    (r"none \(held shut\)", []),
    (r"seat_role\((\w+)\)", "seat"),
    (r"identity_type contains (\w+)", "identity"),
    (r"roster_member|\bmember\b", ["member"]),
    (r"\bfounder", ["founder"]),
    (r"owner_of_subject|owner_of\(|\bowner\b", ["owner"]),
    (r"\bminter\b", ["member"]),   # the minter of an epoch is an active member occurrence (CC 3.3.2)
    (r"\bsteward\b", ["steward"]),
    (r"\bholder\b", ["holder"]),
    (r"subject of the target", ["subject"]),   # the party a ruling is about files against it (CC 4.5.5)
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

def roles_from_signer(val, per_stage=False):
    """Map the manifest's signer rule to role tokens; return (roles, source, stages or None)."""
    if val is None:
        return [], "gap", None
    if isinstance(val, list):
        return roles_from_text(" ".join(map(str, val))) + (None,)
    if isinstance(val, dict):
        if "who" in val:
            who = val.get("who")
            return roles_from_text(" ".join(map(str, who)) if isinstance(who, list) else str(who)) + (None,)
        if per_stage:
            # one signer per stage, from the text: the value is the union, the stages ride beside it
            stages = {st: roles_from_text(str(rule).split(" x ")[0])[0] for stage, rule in val.items() for st in stage.split("/")}
            return sorted({r for rs in stages.values() for r in rs}), "derived", stages
        # per-stage rule of the census (membership): the first stage is the attest transition's signer
        first = next(iter(val.values()), "")
        return roles_from_text(str(first)) + (None,)
    return roles_from_text(str(val)) + (None,)

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

def policy_from_count(cell, role_stages=None):
    """A family's typed `count` cell as its entry transitions' policy: the arm for every row is the value, an arm
    keyed by leaf alone is a stage, and an arm keyed by anything else is a case the view cannot key on a stage."""
    def pol(door):
        row = re.match(r"[a-z_]+", door).group(0)
        return {"policy": "selfAct", "rows": []} if row == "none" else {"policy": POLICY_ROWS[row], "rows": [row]}
    arms = cell["arms"]
    leaf_of = lambda a: re.fullmatch(r"leaf=([a-z_|]+)", a["when"])
    whole = [a for a in arms if not leaf_of(a)] or arms       # the arms no stage keys
    named = [a for a in whole if a["when"] == "*" and pol(a["doors"])["rows"]] or [a for a in whole if pol(a["doors"])["rows"]]
    value = pol(named[0]["doors"]) if named else {"policy": "selfAct", "rows": []}
    if not [a for a in arms if a["when"] == "*"] and len(named) > 1:
        value = {"policy": value["policy"], "rows": sorted({r for a in named for r in pol(a["doors"])["rows"]})}
    out = {"value": value, "source": "cc-table", "cc_ref": sorted({a["cc_ref"] for a in arms}), "count": cell["value"]}
    stages, cases = {}, []
    for a in arms:
        if a["when"] == "*":
            continue
        m = leaf_of(a)
        if m and set(m.group(1).split("|")) <= set(role_stages or ()):
            for leaf in m.group(1).split("|"):
                if pol(a["doors"]) != value: stages[leaf] = pol(a["doors"])
        else:
            cases.append({"when": a["when"], **pol(a["doors"])})
    if stages: out["stages"] = stages
    if cases: out["cases"] = cases
    return out


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

def way_back(trans, lifecycle):
    """The undo and confirm cells (CC 4.5.13). A row entered has a way back when this table offers a
    withdraw or recant of it; a row taken back or replaced has one when the table offers its entry or
    replacement again. The cell names the verb of the way back and the policy it runs under, so an
    item says who it takes to return: selfAct is the signer alone. Where the table offers none, the
    cell is false when the family's lifecycle closes retraction (no one withdraws, or held shut) and
    a gap when the census of the door takes a withdrawal this table does not list. An item is
    confirmed before it is signed when it widens or has no way back on offer; every other item takes
    one step."""
    by_verb = {t["verb"]: t for t in trans}
    opened = lambda t: t is not None and bool(t["roles"]["value"])
    closed = not isinstance(lifecycle, dict) or lifecycle.get("withdraws_by") in (None, "{}")
    for t in trans:
        entry = t["verb"] in ("attest", "authorize")
        if entry:
            back = next((by_verb[v] for v in ("withdraw", "recant") if opened(by_verb.get(v))), None)
        elif t["verb"] == "supersede":
            back = t if opened(t) else None
        else:
            back = next((by_verb[v] for v in ("attest", "authorize") if opened(by_verb.get(v))), None)
        if back is not None:
            cell = {"value": True, "via": back["verb"], "policy": back["policy"]["value"]["policy"], "source": "derived"}
        else:
            cell = {"value": False, "source": "derived" if entry and closed else "gap"}
        t["undo"] = cell
        t["confirm"] = {"value": bool(t["widens"]["value"]) or back is None, "source": "derived"}

def val(cell):
    return cell.get("value") if isinstance(cell, dict) else cell

def text_cells():
    """The cells the text states: {(family, verb): {cell: [(stage, value, cc_ref)]}}."""
    out = {}
    lines = [l for l in TEXT.read_text().split("\n") if l and not l.startswith("#")]
    head = lines[0].split("\t")
    for l in lines[1:]:
        r = dict(zip(head, l.split("\t") + [""] * len(head)))
        out.setdefault((r["family"], r["verb"]), {}).setdefault(r["cell"], []).append((r["stage"].strip(), r["value"].strip(), r["cc_ref"].strip()))
    return out

def apply_text(fam, t, cells):
    """Lay the text's cells over one derived transition; a cell the census closes is refused."""
    for cell, rows in cells.items():
        cur = t[cell]
        if cur["source"] == "code-v61":
            raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} {cell} is closed by the census; remove the row")
        stages = [r[0] for r in rows]
        if (len(rows) > 1 and "" in stages) or len(set(stages)) != len(stages):
            raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} {cell} mixes a whole cell with stages, or repeats a stage")
        refs = sorted({r[2] for r in rows})
        new = {"source": "cc-table", "cc_ref": refs[0] if len(refs) == 1 else refs}
        if cell == "roles":
            toks = {stg: sorted(x.strip() for x in v.split(",") if x.strip()) for stg, v, _ in rows}
            if stages == [""]:
                new["value"] = toks[""]
            else:
                new["value"] = sorted({r for rs in toks.values() for r in rs}); new["stages"] = toks
            if not new["value"]:
                raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} roles names no one; a transition nobody signs is not a transition")
            for k in ("conditions",):
                if k in cur: new[k] = cur[k]
        elif cell == "policy":
            def pol_of(v):
                kind, _, prow = v.partition(":")
                if prow and POLICY_ROWS.get(prow) != kind:
                    raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} policy {v} is not a row of the governance policy table")
                return {"policy": kind, "rows": [prow] if prow else []}
            if stages == [""]:
                new["value"] = pol_of(rows[0][1])
            else:  # the transition's own policy stands; the stage's rides beside it
                new = dict(cur); new["cc_ref"] = refs[0] if len(refs) == 1 else refs
                new["stages"] = {stg: pol_of(v) for stg, v, _ in rows}
        elif stages != [""]:
            raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} {cell} takes no stage")
        elif cell == "widens":
            if rows[0][1] not in ("true", "false"):
                raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} widens is true or false")
            new["value"] = rows[0][1] == "true"
        else:
            raise SystemExit(f"transition_text.tsv: {fam} {t['verb']} names the unknown cell {cell}")
        t[cell] = new

def apply_guards(rows):
    """Give each transition its guard from formal/derivation/guard_text.tsv: every guard parses, names only what the
    vocabularies hold, and rests on words that stand in its section. A guard lands on the verb it names, else on the
    entry verbs. The marks (a refusal with no token, a reference to no named member, the three tokens no other
    vocabulary has) are counted and held from rising."""
    import csv, glob
    sys.path.insert(0, str(ROOT / "tools"))
    import guard_grammar as gg
    from build_family_model import section_span
    reg = json.loads((ROOT / "manifests" / "namespace_registry.json").read_text())
    fams = {f["family"] for f in rows}
    for f in reg["families"]:
        fams.add(f["prefix"]); fams.update(f.get("leaves", []))
    text = "\n".join(open(p, encoding="utf-8").read() for p in sorted(glob.glob(str(ROOT / "constitution" / "part_*.md"))))
    ticks = set(re.findall(r"`([a-z_0-9:]+)`", text))
    voc = {"families": fams, "roles": {r for f in rows for t in f["transitions"] for r in t["roles"]["value"]},
           "policy_rows": set(POLICY_ROWS), "tokens": ticks, "hard_cases": {t.split(":", 1)[1] for t in ticks if t.startswith("hard_case:")}}
    by = {f["family"]: f for f in rows}
    marks, n, partial = {k: 0 for k in GUARD_MARKS_MAX}, 0, 0
    for f in rows:
        for t in f["transitions"]:
            t["guard"] = {"value": [], "source": "generic"}
    lines = [l for l in GUARDS.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
    for g in csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"guard_text.tsv: {g['family']} ({g['cc_ref']})"
        if g["family"] not in by:
            raise SystemExit(f"{where}: no such family")
        try:
            clauses, mk = gg.parse(g["guard"])
        except gg.GuardError as e:
            raise SystemExit(f"{where}: {e}")
        bad = gg.closure(clauses, voc)
        if bad:
            raise SystemExit(f"{where}: outside the vocabularies: " + "; ".join(bad))
        span = section_span(g["cc_ref"])
        if span is None or g["quote"] not in span:
            raise SystemExit(f"{where}: the quoted words do not stand in {g['cc_ref']}")
        if g["reach"] not in ("whole", "partial"):
            raise SystemExit(f"{where}: reach {g['reach']!r}")
        verbs = gg.top_conds(clauses, "verb")
        verbs = ["supersede" if v == "replace" else v for v in verbs] if verbs else ["attest", "authorize"]
        hit = [t for t in by[g["family"]]["transitions"] if t["verb"] in verbs]
        if not hit:
            raise SystemExit(f"{where}: the family has no transition for {verbs}")
        for t in hit:
            if not any(x["guard"] == g["guard"] for x in t["guard"]["value"]):
                t["guard"]["value"].append({"guard": g["guard"], "cc_ref": [g["cc_ref"]], "reach": g["reach"]})
                for k in set(mk): marks[k] += 1
            else:
                x = next(x for x in t["guard"]["value"] if x["guard"] == g["guard"])
                if g["cc_ref"] not in x["cc_ref"]: x["cc_ref"].append(g["cc_ref"])
                if g["reach"] == "partial": x["reach"] = "partial"
            t["guard"]["source"] = "cc-table"
        n += 1
    over = [f"{k} {v} > {GUARD_MARKS_MAX[k]}" for k, v in marks.items() if v > GUARD_MARKS_MAX[k]]
    if over:
        raise SystemExit("guard_text.tsv: marks that may only fall have risen: " + ", ".join(over))
    guarded = sum(1 for f in rows for t in f["transitions"] if t["guard"]["value"])
    # Well founded: no row's admission requires a row whose own admission requires it back. A node is a family, or one
    # leaf of it where the clause is limited to leaves; an edge is a row the guard requires (one, all, latest), an
    # advisory clause excepted. A cycle would be two rows neither of which any node could admit first.
    def req_atoms(cs, leaves=None):
        for c in cs:
            lv = [set(w["values"]) for w in c["when"] if w["cond"] == "leaf"]
            mine = lv[0] if lv else leaves
            if "group" in c:
                yield from req_atoms(c["group"], mine)
            else:
                a = c["atom"]
                if a["atom"] == "row" and a["quant"] in ("one", "all", "latest") and "of" in a["families"] and (c["else"] or {}).get("do") != "advise":
                    yield a["families"]["of"], mine
    nodes = {}
    for f in rows:
        for t in f["transitions"]:
            if t["verb"] in ("attest", "authorize"):
                for x in t["guard"]["value"]:
                    for names, leaves in req_atoms(gg.parse(x["guard"])[0]):
                        for lf in sorted(leaves) if leaves else [None]:
                            nodes.setdefault((f["family"], lf), set()).update(names)
    def hits(name):
        out = []
        for (fam, lf) in nodes:
            segs = fam.split(":")
            i = next((k for k, x in enumerate(segs) if x.startswith("{")), None)
            if name == fam or (lf is None and gg.family_ok(name, {fam})) or (lf is not None and i is not None and name.split(":")[:i + 1] == segs[:i] + [lf]):
                out.append((fam, lf))
        return out
    def depth(node, stack=()):
        if node in stack:
            raise SystemExit("guard_text.tsv: the guards are not well founded: " + " requires ".join(f"{a}" + (f" ({b})" if b else "") for a, b in stack + (node,)))
        return 1 + max([depth(m, stack + (node,)) for name in sorted(nodes[node]) for m in hits(name)] or [0])
    deepest = max([depth(x) for x in sorted(nodes, key=str)] or [0])
    return {"statements": n, "guarded_transitions": guarded, "marks": marks,
            "well_founded": {"requiring": len(nodes), "longest_chain": deepest,
                             "reading": "no row's admission requires a row whose own admission requires it back"}}


def apply_changes(rows):
    """Give each transition its change items from formal/derivation/change_text.tsv: what the changing row may do, who
    signs it, which members may move, what it displaces, what follows for dependants and for keys. An item lands on the
    transition of its verb, or on the entry transition where it names a leaf. Every item parses, names only what the
    vocabularies hold and rests on quoted words; the tokens no other vocabulary has are counted and held from rising."""
    import csv, glob
    sys.path.insert(0, str(ROOT / "tools"))
    import change_grammar as cg, guard_grammar as gg
    from build_family_model import section_span
    reg = json.loads((ROOT / "manifests" / "namespace_registry.json").read_text())
    fams = {f["family"] for f in rows}
    for f in reg["families"]:
        fams.add(f["prefix"]); fams.update(f.get("leaves", []))
    text = "\n".join(open(p, encoding="utf-8").read() for p in sorted(glob.glob(str(ROOT / "constitution" / "part_*.md"))))
    voc = {"families": fams, "roles": {r for f in rows for t in f["transitions"] for r in t["roles"]["value"]},
           "tokens": set(re.findall(r"`([a-z_0-9:]+)`", text))}
    by = {f["family"]: f for f in rows}
    marks, n, every = {k: 0 for k in CHANGE_MARKS_MAX}, 0, []
    for f in rows:
        for t in f["transitions"]:
            t["change"] = {"value": [], "source": "generic"}
    cg.parse(CHANGE_DEFAULT)
    lines = [l for l in CHANGES.read_text(encoding="utf-8").split("\n") if l and not l.startswith("#")]
    for c in csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE):
        where = f"change_text.tsv: {c['family']} ({c['cc_ref']})"
        try:
            items, _ = cg.parse(c["change"])
        except cg.ChangeError as e:
            raise SystemExit(f"{where}: {e}")
        bad = cg.closure(items, voc, gg.family_ok)
        if bad:
            raise SystemExit(f"{where}: outside the vocabularies: " + "; ".join(bad))
        span = section_span(c["cc_ref"])
        if span is None or c["quote"] not in span:
            raise SystemExit(f"{where}: the quoted words do not stand in {c['cc_ref']}")
        n += 1
        if c["family"] == "*":
            if {"change": c["change"], "cc_ref": c["cc_ref"]} not in every:
                every.append({"change": c["change"], "cc_ref": c["cc_ref"]})
            continue
        if c["family"] not in by:
            raise SystemExit(f"{where}: no such family")
        for raw in c["change"].split(" ; "):
            it, mk = cg.parse(raw)
            on = it[0]["on"]
            verbs = [{"replace": "supersede"}.get(on, on)] if on in cg.VERBS else ["attest", "authorize"]
            hit = [t for t in by[c["family"]]["transitions"] if t["verb"] in verbs]
            if not hit:
                raise SystemExit(f"{where}: the family has no transition for {verbs}")
            for t in hit:
                cur = next((x for x in t["change"]["value"] if x["item"] == raw), None)
                if cur:
                    if c["cc_ref"] not in cur["cc_ref"]: cur["cc_ref"].append(c["cc_ref"])
                else:
                    t["change"]["value"].append({"item": raw, "cc_ref": [c["cc_ref"]]})
                    for k in set(mk): marks[k] += 1
                t["change"]["source"] = "cc-table"
    over = [f"{k} {v} > {CHANGE_MARKS_MAX[k]}" for k, v in marks.items() if v > CHANGE_MARKS_MAX[k]]
    if over:
        raise SystemExit("change_text.tsv: marks that may only fall have risen: " + ", ".join(over))
    return {"statements": n, "changed_transitions": sum(1 for f in rows for t in f["transitions"] if t["change"]["value"]),
            "default": CHANGE_DEFAULT, "every_family": every, "marks": marks}


def build():
    fm = json.loads(SRC.read_text())
    text = text_cells()
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
        cell = r.get("signer_rule") if isinstance(r.get("signer_rule"), dict) else {}
        # a cell that gives each stage its signer, from the text (per_stage) or from the census (a map with no `who`)
        per_stage = bool(cell.get("per_stage")) or (isinstance(signer, dict) and "who" not in signer)
        roles, rsrc, stages = roles_from_signer(signer if per_stage else (signer_closed or signer), per_stage)
        conds = signer.get("conditions") if isinstance(signer, dict) and "who" in signer else None
        def entry_roles():
            c = {"value": roles, "source": rsrc}
            if stages: c["stages"] = stages
            if conds: c["conditions"] = conds
            return c
        pol, psrc = policy_from_governance(gov)
        counted = r.get("count") if isinstance(r.get("count"), dict) and r["count"].get("source") == "cc-table" and roles else None
        wd, wsrc = widens(rep, None)
        trans = []
        if "attest" in verbs and roles is not None:
            trans.append({"verb": "attest", "from": "none", "to": "admitted",
                          "roles": entry_roles(),
                          "policy": policy_from_count(counted, stages) if counted else {"value": pol, "source": psrc},
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
                          "roles": entry_roles(),
                          "policy": policy_from_count(counted, stages) if counted else {"value": pol, "source": psrc},
                          "widens": {"value": True, "source": "derived"}})
        for t in trans:
            cells = text.pop((fam, t["verb"]), None)
            if cells: apply_text(fam, t, cells)
        way_back(trans, lifecycle)
        rows.append({"family": fam, "kind": kind, "transitions": trans})
    if text:
        raise SystemExit("transition_text.tsv names transitions outside the manifest: " + ", ".join(f"{f} {v}" for f, v in sorted(text)))
    guard_meta = apply_guards(rows)
    change_meta = apply_changes(rows)
    # gaps summary
    gaps = sum(1 for f in rows for t in f["transitions"] for k in ("roles", "policy", "widens") if t[k]["source"] == "gap")
    total = sum(len(f["transitions"]) for f in rows)
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    out = {"_meta": {"source": "manifests/family_model.json", "source_sha256": src_sha,
                     "cc_section": "4.5.13", "model": "formal/event_lifecycle",
                     "rule": "queue(view, standing) = transitions of the view's family whose from = view.state and whose roles meet standing; one item per transition; the door admits by the same predicate",
                     "states": ["none", "admitted", "withdrawn", "recanted", "superseded"],
                     "role_tokens": sorted({r for f in rows for t in f["transitions"] for r in t["roles"]["value"]}),
                     "sources": {"cc-table": "the registry and CC table, or a cell the text states (it carries cc_ref)", "code-v61": "the census of the code", "derived": "this tool's rule over those", "gap": "nothing says; closed"},
                     "guard": "a guard cell lists what must be held, live or signed for the row to be admitted, as clauses in the grammar of tools/guard_grammar.py, each with the sections that state it and whether it says the whole statement; an empty list with source generic is a transition for which no guard is typed, which is not a claim that the text states none",
                     "guards": guard_meta,
                     "change": "a change cell lists what the transition's row may do to the row it changes, as items in the grammar of tools/change_grammar.py, each with the sections that state it; a transition with none takes the default under `changes`",
                     "changes": change_meta,
                     "count": "a policy cell with `count` is derived from the family model's count cell: `cases` lists the arms that turn on something a stage does not key (the kind of identity, of group, the number of seats), each with its policy and rows",
                     "stages": "a roles cell with `stages` gives each stage's or leaf's signers and `value` is their union; a policy cell with `stages` gives the policy of the stages that differ from `value`; a view that knows its stage is served from the stage",
                     "undo": "an undo cell says whether this table offers a way back for the row the transition signs, the verb of that way back (`via`) and the policy it runs under (`policy`): selfAct is the signer alone, any other policy takes the others it names; false with source derived is a family whose lifecycle closes retraction, false with source gap is a family whose retraction this table does not list",
                     "confirm": "a confirm cell is true when the transition widens or has no way back: the item is confirmed before it is signed; false is one step",
                     "conditions": "a roles cell with `conditions` carries the signer rule's conditions; not_subject closes the transition to a signer who is the row's subject",
                     "families": len(rows), "transitions": total, "gap_cells": gaps,
                     "confirmed": sum(1 for f in rows for t in f["transitions"] if t["confirm"]["value"]),
                     "undo_gap_cells": sum(1 for f in rows for t in f["transitions"] if t["undo"]["source"] == "gap"),
                     "note": "draft 0: states are the five retraction states of CC 2.4.1.1; a family with its own lifecycle (membership stages, the moderator election, the halt) refines these in its chapter model; gap cells mean the queue generator treats the transition as closed until the manifest says otherwise"},
           "rows": rows}
    tsv = ["family\tverb\tfrom\tto\troles\tpolicy\twidens\tundo\tundo_policy\tconfirm\troles_src\tpolicy_src\twidens_src"]
    for f in rows:
        for t in f["transitions"]:
            tsv.append("\t".join([f["family"], t["verb"], t["from"], t["to"], ",".join(t["roles"]["value"]),
                                  t["policy"]["value"]["policy"], str(t["widens"]["value"]).lower(),
                                  t["undo"].get("via", "none"), t["undo"].get("policy", ""), str(t["confirm"]["value"]).lower(),
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
