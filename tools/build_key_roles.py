#!/usr/bin/env python3
"""The key-roles contract: which kind of key may sign each family transition (CC 3.4.7.3, CC 3.2, CC 2.4.1.1).

Reads manifests/transitions.json (every family transition, with its relational role tokens) and
formal/derivation/signer_kind.tsv (the signer kind of each transition, with the section and line that state it),
and writes manifests/key_roles.json: the roles x uses table the key_roles model and an implementation's site table
are both checked against.

The role tokens say who a signer is to the row (author, owner, member, infra:attest, ...). They never say whether the
key is a node's, an agent's or a person's. The signer kind is that axis. This tool refuses:
  - a transition with no signer-kind cell, and a cell that names no transition;
  - a kind outside the vocabulary;
  - a cell that does not cite a section and a line;
  - an open cell with no question, and a closed cell with one;
  - a cell that contradicts the relational tokens: `owner`, `wa`, `steward`, `winner` need a person, `holder` an
    accord holder, `infra:attest`, `serve` and `identity:substrate_persist` a node, `identity:lenscore_detector` a
    detector;
  - a `by-leaf` family with no leaf rows.

Run: python3 tools/build_key_roles.py            (writes the manifest)
     python3 tools/build_key_roles.py --check    (refuses drift)
"""
import csv, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "manifests/transitions.json")
TSV = os.path.join(ROOT, "formal/derivation/signer_kind.tsv")
OUT = os.path.join(ROOT, "manifests/key_roles.json")

# The kinds of key. person, holder: a person's keys (holder is the accord holder's composite key, a person's, never a
# machine's: CC 3.4.7.1). agent, node: machine keys, never cohabiting (CC 3.4.7.3 Clause A). detector, witness,
# rendezvous: machine roles that act only in their reserved families. room: a private room's per-device key.
# ephemeral, kem: not identity signing keys. unsigned: a use nobody signs.
KINDS = ["person", "holder", "agent", "node", "detector", "witness", "rendezvous", "room", "ephemeral", "kem", "unsigned"]
PERSON_KINDS = {"person", "holder"}
MACHINE_KINDS = {"agent", "node", "detector", "witness", "rendezvous"}
NEEDS = {"owner": {"person"}, "wa": {"person"}, "steward": {"person"}, "winner": {"person"}, "holder": {"holder"},
         "infra:attest": {"node"}, "serve": {"node"}, "identity:substrate_persist": {"node"},
         "identity:lenscore_detector": {"detector"}}

# Reads whose subject is a key of a stated kind (CC 3.2 who owns a key; CC 3.4.7.3 Clauses D and E).
READS = [
    {"read": "owner_of(K)", "subject": ["node", "agent"], "returns": "person or nothing; any count but one is nothing",
     "cc_ref": "CC 3.2", "at": "P3:970, P3:976"},
    {"read": "is_steward_bound(K)", "subject": ["node", "agent"], "returns": "true iff exactly one live owner, an adult person",
     "cc_ref": "CC 3.2", "at": "P3:971"},
    {"read": "may_act_through(agent, node)", "subject": ["agent", "node"],
     "returns": "owner_of(node) in stewards_of(agent): one human at both corners; an unresolved walk refuses",
     "cc_ref": "CC 3.4.7.3 Clause D", "at": "P3:2587"},
    {"read": "seam(envelope)", "subject": ["node"],
     "returns": "checked by the node: owner_of(node) == signer_of(envelope) and owner_of(node) in stewards_of(agent)",
     "cc_ref": "CC 3.4.7.3 Clause E", "at": "P3:2600"},
    {"read": "node_identity", "subject": ["node"],
     "returns": "the node is named by its own node key: its public identity, its transport binding and its serve seat",
     "cc_ref": "CC 3.4.7.3 Clauses A and E; CC 3.2 serve seat", "at": "P3:2581, P3:2600, P3:996"},
]


def kinds_of(cell):
    if cell in ("open", "by-leaf"):
        return []
    m = re.match(r"any-of\((.*)\)$", cell)
    return m.group(1).split(",") if m else [cell]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def build():
    errs = []
    trans = json.load(open(TRANS, encoding="utf-8"))
    cells = list(csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t"))
    want = {}
    for r in trans["rows"]:
        for t in r["transitions"]:
            want[(r["family"], t["verb"], t["from"], t["to"])] = sorted(t["roles"]["value"])
    have, leaves, uses = {}, {}, []
    for c in cells:
        k = c["signer_kind"]
        ks = kinds_of(k)
        if k not in ("open", "by-leaf") and (not ks or any(x not in KINDS for x in ks)):
            errs.append(f"{c['family']} {c['verb']}: kind {k!r} is outside the vocabulary")
        if not re.search(r"CC \d", c["cc_ref"]) or not re.search(r"P\d:\d", c["at"]):
            errs.append(f"{c['family']} {c['verb']} {c['leaf']}: cites no section and line")
        if (k == "open") != bool(c["question"].strip()):
            errs.append(f"{c['family']} {c['verb']} {c['leaf']}: an open cell carries its question, and only an open cell does")
        if c["family"].startswith("@"):
            uses.append({"use": c["family"], "family": None, "verb": "sign", "leaf": None, "roles": [], "kinds": ks, "open": k == "open",
                         "question": c["question"] or None, "rule": c["rule"], "cc_ref": c["cc_ref"], "at": c["at"]})
        elif c["leaf"] != "*":
            leaves.setdefault(c["family"], []).append(c)
        else:
            key = (c["family"], c["verb"], c["from"], c["to"])
            if key in have:
                errs.append(f"{key}: two cells")
            have[key] = c
    for key in want:
        if key not in have:
            errs.append(f"{key}: a transition with no signer-kind cell")
    for key in have:
        if key not in want:
            errs.append(f"{key}: a cell that names no transition")
    for key in sorted(want):
        c = have.get(key)
        if not c:
            continue
        fam, verb, frm, to = key
        roles = want[key]
        if c["signer_kind"] == "by-leaf":
            if fam not in leaves:
                errs.append(f"{fam}: by-leaf with no leaf rows")
            for lc in leaves.get(fam, []):
                for lf in lc["leaf"].split("|"):
                    uses.append({"use": f"{fam}[{lf}]#{verb}", "family": fam, "verb": verb, "leaf": lf, "roles": roles,
                                 "kinds": kinds_of(lc["signer_kind"]), "open": lc["signer_kind"] == "open",
                                 "question": lc["question"] or None, "rule": lc["rule"], "cc_ref": lc["cc_ref"], "at": lc["at"]})
            continue
        ks = kinds_of(c["signer_kind"])
        if c["signer_kind"] != "open":
            for tok in roles:
                need = NEEDS.get(tok)
                if need and not (need & set(ks)):
                    errs.append(f"{fam} {verb}: role token {tok} needs a {sorted(need)} key and the cell gives {ks}")
        uses.append({"use": f"{fam}#{verb}:{frm}>{to}", "family": fam, "verb": verb, "leaf": None, "roles": roles, "kinds": ks,
                     "open": c["signer_kind"] == "open", "question": c["question"] or None, "rule": c["rule"],
                     "cc_ref": c["cc_ref"], "at": c["at"]})
    uses.sort(key=lambda u: u["use"])
    table = {k: sorted(u["use"] for u in uses if k in u["kinds"]) for k in KINDS}
    opens = sorted({u["question"] for u in uses if u["open"] and u["question"]})
    doc = {
        "_meta": {
            "what": "the signer kind of every family transition and of every non-family use: which kind of key may sign it",
            "cc_section": "3.4.7.3",
            "sources": {"manifests/transitions.json": sha(TRANS), "formal/derivation/signer_kind.tsv": sha(TSV)},
            "kinds": KINDS, "person_kinds": sorted(PERSON_KINDS), "machine_kinds": sorted(MACHINE_KINDS),
            "role_token_needs": {k: sorted(v) for k, v in sorted(NEEDS.items())},
            "counts": {"uses": len(uses), "transitions": len(want), "open_uses": sum(u["open"] for u in uses),
                       "open_questions": len(opens)},
            "model": "formal/key_roles",
            "reading": "a key of a kind not in a use's kinds must not sign it; an open use is reported, never passed",
        },
        "uses": uses,
        "by_kind": table,
        "reads": READS,
        "open_questions": opens,
    }
    return doc, errs


def plants():
    """Each refusal must fire on a planted cell set. Returns the names of plants not caught."""
    import tempfile
    real = TSV
    rows = list(csv.DictReader(open(real, encoding="utf-8"), delimiter="\t"))
    cols = list(rows[0].keys())

    def run(mut):
        global TSV
        rs = [dict(r) for r in rows]
        mut(rs)
        with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False, encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
            w.writeheader()
            for r in rs:
                w.writerow(r)
            path = fh.name
        try:
            TSV = path
            return build()[1]
        finally:
            TSV = real
            os.unlink(path)

    def first(rs, pred):
        return next(r for r in rs if pred(r))

    missed = []
    cases = [
        ("a transition with no cell", lambda rs: rs.remove(first(rs, lambda r: r["family"] == "chat:*")), "no signer-kind cell"),
        ("owner token given a node key", lambda rs: first(rs, lambda r: r["family"] == "device:label").update(signer_kind="node"), "role token owner"),
        ("infra:attest given an agent key", lambda rs: first(rs, lambda r: r["family"] == "transport:{kind}").update(signer_kind="agent"), "role token infra:attest"),
        ("a kind outside the vocabulary", lambda rs: first(rs, lambda r: r["family"] == "chat:*").update(signer_kind="engine"), "outside the vocabulary"),
        ("a cell with no line", lambda rs: first(rs, lambda r: r["family"] == "chat:*").update(at=""), "cites no section"),
        ("an open cell with no question", lambda rs: first(rs, lambda r: r["family"] == "@mls_leaf").update(signer_kind="open", question=""), "carries its question"),
        ("a closed cell with a question", lambda rs: first(rs, lambda r: r["family"] == "@mls_leaf").update(question="which key?"), "only an open cell does"),
    ]
    for name, mut, needle in cases:
        if not any(needle in e for e in run(mut)):
            missed.append(name)
    return missed, len(cases)


def main():
    doc, errs = build()
    if "--check" in sys.argv:
        missed, n = plants()
        errs += ["plant not caught: " + m for m in missed]
        print(f"key roles: plants caught {n - len(missed)} of {n}")
    text = json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    if "--check" in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding="utf-8").read() != text:
            errs.append("manifests/key_roles.json is stale (run tools/build_key_roles.py)")
    elif not errs:
        open(OUT, "w", encoding="utf-8").write(text)
    m = doc["_meta"]["counts"]
    print(f"key roles: {m['transitions']} transitions, {m['uses']} uses, {m['open_uses']} open uses over {m['open_questions']} questions; {len(errs)} error(s)")
    for e in errs:
        print("  ERR", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
