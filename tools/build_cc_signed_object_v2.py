#!/usr/bin/env python3
"""
CC (the CIRIS Constitution) — the signed object of CC 2.6.1 (CBOR and COSE), its members table.

Sources:
  manifests/signed_object_v2.cddl     the normative schema, hand-written (RFC 8610 CDDL over CBOR)
  constitution/signed_object_v2.tsv   one row per member: the CDDL rule and key that holds it, its
                                      logical name (the member name the Parts use), placement, type,
                                      when it is required, and the CC section that states its rule.
                                      A row whose rule is `-` names a logical name with no member of
                                      its own (the logical-name map) and is not read by the agreement check.

Placement vocabulary:
  statement           a position of the COSE_Sign1 array
  header:protected    a member of the protected header, covered by the signature
  header:cwt          a CWT claim inside the protected header (label 15)
  header:unprotected  a member of the unprotected header: never signed, never read by a rule
  payload             a member of the payload, covered by the signature and by the row id
  payload:refs        a member of the payload's `refs`, the one member that names rows
  payload:body        a member of the payload's `body`
  derived             computed by a verifier from the statement, never carried as such
  object              a member of a signed object that is not a row (its payload, under its own typ)
  none                a logical name with no member of its own (rule `-`)

Output: the body of the members table, written between the marker lines
  <!-- BEGIN GENERATED: signed_object_v2 -->  and  <!-- END GENERATED: signed_object_v2 -->
in whichever Part holds them (or, with no markers, the body of the section whose heading slug is
`signed-object-members`, from its heading to the next numbered heading).

Checks (every run, before writing):
  the table and the CDDL agree member for member: every (rule, key) the CDDL names in a map or an
  array is one row, with the same presence (`?` / required) and the same type; every row with a rule
  is a member of the CDDL; and two deliberate breaks (a row dropped, a CDDL member dropped) must be caught.
  The CDDL parses (the `cddl` gem, as tools/build_ietf_draft.py runs it; a plain message when absent),
  and a sample statement in deterministic CBOR, built here, validates against it. The sample is a
  schema check only and is no known-answer vector: the vectors are the verifier's.
  --check   check, and compare the block with what the Part holds; write nothing (exit 1 when stale)

stdlib only. Run:  python3 tools/build_cc_signed_object_v2.py [--check]
"""
import csv, glob, hashlib, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "constitution", "signed_object_v2.tsv")
CDDL = os.path.join(ROOT, "manifests", "signed_object_v2.cddl")
NAME = "signed_object_v2"
SLUG = "signed-object-members"
BEGIN = f"<!-- BEGIN GENERATED: {NAME} -->"
END = f"<!-- END GENERATED: {NAME} -->"
COLS = ["object", "rule", "member", "logical_name", "placement", "type", "required_when", "cc_ref", "note"]
PLACEMENTS = ["statement", "header:protected", "header:cwt", "header:unprotected", "payload", "payload:refs",
              "payload:body", "derived", "object", "none"]
OBJECTS = [
    ("statement", "The statement: one `COSE_Sign1` per signer"),
    ("protected", "The protected header"),
    ("cwt", "The CWT claims (protected header, label 15)"),
    ("unprotected", "The unprotected header"),
    ("payload", "The payload"),
    ("refs", "`refs`: every row a row names"),
    ("row_id", "The row id and the names it is built from"),
    ("statement_id", "The statement id"),
    ("key", "The composite key"),
    ("key_record", "The key record: the payload of a `key:record` row"),
    ("object", "A signed object that is not a row, and its object id"),
    ("snapshot", "The revocation snapshot (typ `ceg-revocation-snapshot/2`)"),
    ("genesis", "The genesis bundle (typ `ceg-genesis-bundle/2`)"),
    ("room", "The seat commitment of a room key"),
    ("disclosure", "A disclosure of a blinded member"),
    ("logical", "Logical names with no member of their own"),
]


def find_tool(name):
    for d in glob.glob(os.path.expanduser("~/.local/share/gem/ruby/*/bin")) + os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if os.access(p, os.X_OK):
            return p
    return None


def load_rows(path=SRC):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    objs = [o for o, _ in OBJECTS]
    seen, bad = set(), []
    for r in rows:
        if list(r.keys()) != COLS:
            raise SystemExit(f"{path}: columns {list(r.keys())} are not {COLS}")
        key = (r["rule"], r["member"]) if r["rule"] != "-" else ("-", r["logical_name"])
        if key in seen:
            bad.append(f"duplicate row {key}")
        seen.add(key)
        if r["placement"] not in PLACEMENTS:
            bad.append(f"{key}: unknown placement {r['placement']!r}")
        if r["object"] not in objs:
            bad.append(f"{key}: unknown object {r['object']!r}")
        if (r["rule"] == "-") != (r["placement"] == "none" or r["object"] == "logical"):
            bad.append(f"{key}: rule `-` goes with object logical and placement none, and only with them")
        for dec in r["cc_ref"].split():
            if not re.fullmatch(r"\d+(\.\d+)*", dec):
                bad.append(f"{key}: cc_ref {dec!r}")
    if bad:
        raise SystemExit(f"{path}:\n  " + "\n  ".join(bad))
    return rows


# ---------------------------------------------------------------- the CDDL, read for its members
def strip_comments(text):
    out = []
    for line in text.split("\n"):
        s, q = [], False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == ";" and not q:
                break
            s.append(ch)
        out.append("".join(s))
    return "\n".join(out)


def rules(text):
    """{rule name: its right-hand side}, for every rule `name = ...` starting in column 0."""
    out, cur = {}, None
    for line in strip_comments(text).split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*)\s*=\s*(.*)$", line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2)
        elif cur and line.strip():
            out[cur] += " " + line.strip()
    return out


def split_top(s):
    """Split at the commas of nesting depth zero (strings respected)."""
    parts, depth, q, buf = [], 0, False, []
    for ch in s:
        if ch == '"':
            q = not q
        elif not q and ch in "[{(":
            depth += 1
        elif not q and ch in "]})":
            depth -= 1
        if ch == "," and depth == 0 and not q:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def body_of(rhs):
    """The inside of the rule's outer map or array, or None when the rule is neither."""
    m = re.match(r"^\s*(?:#6\.\d+\()?\s*([\[{])", rhs)
    if not m:
        return None, None
    i = m.end(1) - 1
    opener = rhs[i]
    closer = "]" if opener == "[" else "}"
    depth, q = 0, False
    for j in range(i, len(rhs)):
        ch = rhs[j]
        if ch == '"':
            q = not q
        elif not q and ch in "[{(":
            depth += 1
        elif not q and ch in "]})":
            depth -= 1
            if depth == 0:
                if ch != closer:
                    return None, None
                tail = rhs[j + 1:].strip().rstrip(")").strip()
                if tail:          # a choice of two maps, or anything else: not one map or array
                    return None, None
                return opener, rhs[i + 1:j]
    return None, None


ENTRY = re.compile(r'^(\?\s*)?("[^"]*"|-?\d+|[A-Za-z_][\w-]*)\s*(?::|=>)\s*(.*)$', re.S)


def members(text):
    """{(rule, key): (required, type)} for every named member of a map or an array the CDDL defines.
    A member whose type is an inline map is `map`, and its own members follow under `key.child`."""
    out = {}

    def walk(rule, prefix, inner):
        for part in split_top(inner):
            m = ENTRY.match(part)
            if not m:
                continue                       # `* tstr => any`, a positional literal, a group choice
            key, typ = m.group(2), " ".join(m.group(3).split())
            full = prefix + key
            op, sub = body_of(typ)
            if op == "{" and not re.match(r"^\s*[+*]", sub.strip()):
                out[(rule, full)] = (m.group(1) is None, "map")
                walk(rule, full + ".", sub)
            else:
                out[(rule, full)] = (m.group(1) is None, typ)

    for name, rhs in rules(text).items():
        op, inner = body_of(rhs)
        if op:
            walk(name, "", inner)
    return out


def required_flag(r):
    return r["required_when"] == "always"


def agree(rows, text):
    """The disagreements between the table and the CDDL, as lines."""
    cd = members(text)
    tb = {(r["rule"], r["member"]): r for r in rows if r["rule"] != "-"}
    bad = []
    for k, (req, typ) in sorted(cd.items()):
        r = tb.get(k)
        if r is None:
            bad.append(f"CDDL {k[0]} member {k[1]} has no row in the table")
            continue
        if required_flag(r) != req:
            bad.append(f"{k[0]} {k[1]}: the CDDL makes it {'required' if req else 'optional'}, the table says {r['required_when']!r}")
        if " ".join(r["type"].split()) != typ:
            bad.append(f"{k[0]} {k[1]}: the CDDL types it {typ!r}, the table {r['type']!r}")
    for k in sorted(tb):
        if k not in cd:
            bad.append(f"table row {k[0]} {k[1]} is not a member in the CDDL")
    return bad


def agreement_with_breaks(rows, text):
    bad = agree(rows, text)
    # deliberate break 1: a row dropped from the table must be caught
    victim = next(r for r in rows if r["rule"] != "-")
    if not agree([r for r in rows if r is not victim], text):
        bad.append("deliberate break not caught: a table row dropped")
    # deliberate break 2: a member dropped from the CDDL must be caught
    planted = text.replace('? "salt": bstr .size 16,', "", 1)
    if planted == text:
        bad.append("deliberate break not planted: no `salt` member in the CDDL")
    elif not agree(rows, planted):
        bad.append("deliberate break not caught: a CDDL member dropped")
    # deliberate break 3: a member made optional in the CDDL must be caught
    planted = text.replace('"asserted_at": ms-time,', '? "asserted_at": ms-time,', 1)
    if planted == text or not agree(rows, planted):
        bad.append("deliberate break not caught: a presence changed in the CDDL")
    return bad


# ---------------------------------------------------------------- deterministic CBOR, for the schema sample
def _head(major, n):
    if n < 24:
        return bytes([major << 5 | n])
    for ai, size in ((24, 1), (25, 2), (26, 4), (27, 8)):
        if n < 1 << (8 * size):
            return bytes([major << 5 | ai]) + n.to_bytes(size, "big")
    raise ValueError("integer too large")


class Simple:
    def __init__(self, value):
        self.value = value


class Tag:
    def __init__(self, tag, value):
        self.tag, self.value = tag, value


def cde(v):
    """CBOR deterministic encoding for the types the sample uses: shortest heads, definite lengths,
    map keys sorted by their encoded bytes."""
    if v is None:
        return b"\xf6"
    if isinstance(v, bool):
        return b"\xf5" if v else b"\xf4"
    if isinstance(v, int):
        return _head(0, v) if v >= 0 else _head(1, -1 - v)
    if isinstance(v, bytes):
        return _head(2, len(v)) + v
    if isinstance(v, str):
        b = v.encode("utf-8")
        return _head(3, len(b)) + b
    if isinstance(v, list):
        return _head(4, len(v)) + b"".join(cde(x) for x in v)
    if isinstance(v, dict):
        items = sorted((cde(k), cde(x)) for k, x in v.items())
        return _head(5, len(items)) + b"".join(k + x for k, x in items)
    if isinstance(v, Tag):
        return _head(6, v.tag) + cde(v.value)
    if isinstance(v, Simple):
        return bytes([0xF8, v.value]) if v.value >= 32 else bytes([0xE0 | v.value])
    raise TypeError(type(v))


ISS = "urn:ietf:params:oauth:ckt:sha-256:" + "A" * 43
CTY = "application/vnd.ciris.row+cbor"


def statement(payload, sig=3373, iss=ISS, cty=CTY, rtype="scores", family="custody:ack", unprotected=None):
    """A row statement in deterministic CBOR (no real key): the protected header of CC 2.6.1.1."""
    prot = {1: -70100, 3: cty, 4: bytes(32), 15: {1: iss, 2: "sample-sub", 6: 1763078400, -70003: 2},
            16: "ceg-row/2", -70001: rtype, -70002: family}
    prot = {k: v for k, v in prot.items() if v is not None}
    return cde(Tag(18, [cde(prot), unprotected or {}, cde(payload), bytes(sig)]))


def sample_statement():
    """A counted row, an authored row, and an erasable row with a disclosure presented: schema samples."""
    digest = [-16, bytes(32)]
    refs = {"head": [2, digest], "further_heads": sorted([[2, [-16, bytes([1]) * 32]], [2, [-16, bytes([2]) * 32]]], key=cde)}
    payload = {"refs": refs, "asserted_at": 1763078400000, "score": -250000, "confidence": 1000000,
               "body": {"note": "schema sample"}}
    disclosure = cde([bytes(16), "schema sample", "note"])
    erasable = {"asserted_at": 1763078400000, "body": {Simple(59): [bytes(32)]},
                "evidence_refs": [digest], "tags": ["kept", Tag(60, bytes(32))]}
    return [("counted", statement(payload)), ("authored", statement(dict(payload, author=ISS))),
            ("erasable", statement(erasable, unprotected={17: [disclosure]}))]


def broken_samples():
    """Statements the schema must refuse, each one change away from a valid sample."""
    base = {"asserted_at": 1763078400000}
    return [
        ("a null member", statement(dict(base, x=None))),
        ("an empty refs", statement(dict(base, refs={}))),
        ("a one-half signature", statement(base, sig=64)),
        ("an iss with non-zero trailing bits", statement(base, iss=ISS[:-1] + "B")),
        ("a total of zero", statement(dict(base, passed=0, total=0))),
        ("a quoted family", statement(base, family='"custody:ack"')),
        ("a cty with parameters", statement(base, cty=CTY + ";type=scores;family=custody:ack")),
        ("a missing family label", statement(base, family=None)),
        ("a leaf with uppercase as the family", statement(base, family="ledger:head:USD")),
        ("a tag other than 60", statement(dict(base, tags=[Tag(61, bytes(32))]))),
    ]


def iref(n):
    """A schema-sample identity reference: 42 base64url characters and a last one with zero trailing bits."""
    return "urn:ietf:params:oauth:ckt:sha-256:" + chr(ord("A") + n) * 42 + "A"


def genesis_payload(**change):
    """A first genesis bundle's payload (CC 2.6.1.11): three holders, two seats, placeholder row ids."""
    holders = [iref(0), iref(1), iref(2)]
    cites = sorted(([2, [-16, bytes([n]) * 32]] for n in range(1, 8)), key=cde)
    payload = {"refs": {"also": {"cites": cites}}, "version": 1, "asserted_at": 1763078400000,
               "family_key_id": "humanity-accord", "holders": holders, "serve_nodes": [iref(3), iref(4)],
               "charter": {"recovery_commitments": {h: [-16, bytes([9]) * 32] for h in holders},
                           "scope": ["infra:attest", "infra:serve"]}}
    for k, v in change.items():
        if v is None:
            payload.pop(k, None)
        else:
            payload[k] = v
    return cde(payload)


def genesis_samples():
    """(valid, broken): genesis bundle payloads, each broken one a single change away from the valid."""
    charter = {"recovery_commitments": {iref(0): [-16, bytes(32)]}, "scope": ["infra:serve"]}
    return genesis_payload(), [
        ("a bundle with no holder", genesis_payload(holders=[])),
        ("a bundle at version 0", genesis_payload(version=0)),
        ("a bundle with no refs", genesis_payload(refs=None)),
        ("a bundle naming a head", genesis_payload(refs={"head": [2, [-16, bytes(32)]], "also": {"cites": [[2, [-16, bytes(32)]]]}})),
        ("a bundle carrying the earlier authorizations", genesis_payload(authorizations=[bytes(64)])),
        ("a holder named by a key id", genesis_payload(holders=["A1"])),
        ("a recovery commitment in hex", genesis_payload(charter=dict(charter, recovery_commitments={iref(0): "00" * 32}))),
        ("a charter with no scope", genesis_payload(charter={"recovery_commitments": charter["recovery_commitments"]})),
        ("a witness quorum of 1", genesis_payload(charter=dict(charter, witness_quorum=1))),
        ("a bundle with an author", genesis_payload(author=iref(0))),
        ("a bundle with a count member", genesis_payload(count="majority")),
    ]


def key_record_samples():
    """(valid, broken): key record payloads with their custody member (CC 4.2.2.1)."""
    key = {1: 7, 3: -70100, -1: bytes(1984)}
    ev = {"hardware_class": "YubiKey_5_FIPS", "pq_custody": "removable_offline", "chain": [bytes(8), bytes(9)]}
    rec = lambda **e: cde({"key": key, "identity_type": ["accord_holder"], "asserted_at": 1763078400000,
                           "attestation_evidence": dict(ev, **e)})
    return rec(), [
        ("a pq_custody outside the three", rec(pq_custody="token")),
        ("a chain in hex", rec(chain=["3082"])),
        ("an empty chain", rec(chain=[])),
    ]


def recovery_samples():
    key = {1: 7, 3: -70100, -1: bytes(1984)}
    return cde(["CEG-recovery/2", [key]]), [("a commitment over no key", cde(["CEG-recovery/2", []]))]


# ---------------------------------------------------------------- the bundle's prose rules, as a reference reader
GENESIS_TYP = "ceg-genesis-bundle/2"


def object_id(typ, payload_bytes):
    return [-16, hashlib.sha256(cde(["CEG-object/2", typ, None, payload_bytes])).digest()]


def read_bundle(payload, statements, rows, anchor):
    """CC 2.6.1.11 over one first bundle, structure only (no signature is computed here): `statements` are the
    holders' voices as (iss, iat), each taken as verified; `rows` maps a cited row id to (family, author, extra).
    Returns ("Valid", placement), ("Invalid", reason), ("Waiting", ids) or ("nothing", reason)."""
    P = payload
    H, S = set(P["holders"]), set(P["serve_nodes"])
    W = set(P["charter"].get("witnesses", []))
    if ("prev" in P["refs"]) != (P["version"] != 1):
        return "Invalid", "version_prev_mismatch"
    if H & S or H & W or S & W:
        return "Invalid", "holders_seats_overlap"
    if set(P["charter"]["recovery_commitments"]) != H:
        return "Invalid", "recovery_commitments_not_holders"
    if not {"infra:attest", "infra:serve"} <= set(P["charter"]["scope"]):
        return "Invalid", "scope_missing_infra"
    if any(iat != P["asserted_at"] // 1000 for _, iat in statements):
        return "Invalid", "iat_mismatch"
    kind, value = anchor
    if (kind == "thumbprints" and set(value) != H) or (kind == "object_id" and value != object_id(GENESIS_TYP, cde(P))):
        return "nothing", "genesis_bundle_not_anchored"
    cites = P["refs"]["also"]["cites"]
    missing = [c for c in cites if c[1][1] not in rows]
    if missing:
        return "Waiting", missing
    place = {}
    for c in cites:
        fam, author, extra = rows[c[1][1]]
        if fam == "key:record" and author in H | S | W:
            slot = ("record", author)
        elif fam == "identity:occurrence" and author in S:
            slot = ("binding", author)
        else:
            return "nothing", "genesis_bundle_row_unplaced"
        if slot in place:
            return "nothing", "genesis_bundle_row_unplaced"
        place[slot] = extra
    for party in H | S | W:
        if ("record", party) not in place:
            return "nothing", "genesis_bundle_row_unplaced"
    for seat in S:
        if ("binding", seat) not in place:
            return "nothing", "genesis_bundle_row_unplaced"
    for h in H:
        ev = place[("record", h)]
        if not ev.get("chain_verifies") or ev.get("pq_custody") != "removable_offline":
            return "nothing", "genesis_holder_custody"
    if not H <= {iss for iss, _ in statements}:
        return "nothing", "genesis_bundle_count_unmet"
    return "Valid", {"holders": sorted(H), "seats": {s: place[("binding", s)]["xwing"] for s in sorted(S)}}


def reader_samples():
    """The reference reader over a valid first bundle and one break per rule it states; each break must give its
    own answer, never Valid."""
    H = [iref(0), iref(1), iref(2)]
    S = [iref(3), iref(4)]
    rid = lambda n: [2, [-16, bytes([n]) * 32]]
    rows = {}
    for n, h in enumerate(H):
        rows[bytes([0x10 + n]) * 32] = ("key:record", h, {"chain_verifies": True, "pq_custody": "removable_offline"})
    for n, s_ in enumerate(S):
        rows[bytes([0x20 + n]) * 32] = ("key:record", s_, {})
        rows[bytes([0x30 + n]) * 32] = ("identity:occurrence", s_, {"xwing": ("transit-%d" % n, "onion-%d" % n)})
    cites = sorted((rid(b[0]) for b in rows), key=cde)

    def payload(**ch):
        p = {"refs": {"also": {"cites": cites}}, "version": 1, "asserted_at": 1763078400000,
             "family_key_id": "humanity-accord", "holders": H, "serve_nodes": S,
             "charter": {"recovery_commitments": {h: [-16, bytes(32)] for h in H}, "scope": ["infra:serve", "infra:attest"]}}
        p.update(ch)
        return p
    voices = [(h, 1763078400) for h in H]
    anchor = ("thumbprints", H)
    bad_custody = dict(rows)
    bad_custody[bytes([0x10]) * 32] = ("key:record", H[0], {"chain_verifies": True, "pq_custody": "software_wrapped"})
    no_chain = dict(rows)
    no_chain[bytes([0x11]) * 32] = ("key:record", H[1], {"chain_verifies": False, "pq_custody": "removable_offline"})
    good = payload()
    breaks = [
        ("a missing holder signature", (good, voices[:2], rows, anchor), ("nothing", "genesis_bundle_count_unmet")),
        ("an iat not floor(asserted_at / 1000)", (good, voices[:2] + [(H[2], 1763078401)], rows, anchor), ("Invalid", "iat_mismatch")),
        ("a seat whose binding is not in cites", (payload(refs={"also": {"cites": [c for c in cites if c[1][1] != bytes([0x31]) * 32]}}),
                                                  voices, rows, anchor), ("nothing", "genesis_bundle_row_unplaced")),
        ("holders and serve_nodes overlapping", (payload(serve_nodes=[H[0], S[0]]), voices, rows, anchor), ("Invalid", "holders_seats_overlap")),
        ("a holder not removable_offline", (good, voices, bad_custody, anchor), ("nothing", "genesis_holder_custody")),
        ("a holder whose chain does not verify", (good, voices, no_chain, anchor), ("nothing", "genesis_holder_custody")),
        ("a holder set unlike the anchor", (good, voices, rows, ("thumbprints", H[:2] + [iref(5)])), ("nothing", "genesis_bundle_not_anchored")),
        ("an object id unlike the anchor", (good, voices, rows, ("object_id", [-16, bytes(32)])), ("nothing", "genesis_bundle_not_anchored")),
        ("a cited row not held", (good, voices, {k: v for k, v in rows.items() if k != bytes([0x20]) * 32}, anchor), ("Waiting", None)),
        ("a version 2 with no prev", (payload(version=2), voices, rows, anchor), ("Invalid", "version_prev_mismatch")),
    ]
    return (good, voices, rows, anchor), (cde(good), object_id(GENESIS_TYP, cde(good))), breaks


def reader_checks():
    """(line, problems) for the reference reader: the valid bundle is Valid under both anchors with its placement,
    and each break gives its own answer."""
    bad = []
    (g, v, r, a), (_, oid), breaks = reader_samples()
    for anc in (a, ("object_id", oid)):
        ans, out = read_bundle(g, v, r, anc)
        if ans != "Valid" or out["seats"].get(iref(3)) != ("transit-0", "onion-0") or len(out["holders"]) != 3:
            bad.append(f"reference reader: the valid bundle gives {ans} under {anc[0]}")
    caught = 0
    for why, args, (want, reason) in breaks:
        ans, out = read_bundle(*args)
        if ans != want or (reason is not None and out != reason):
            bad.append(f"deliberate break not caught: {why} gives {ans} {out if isinstance(out, str) else ''}")
        else:
            caught += 1
    return f"reference bundle reader: the valid bundle is Valid under both anchors; {caught} broken bundles give their own answer", bad


def cddl_checks(text):
    """(lines, problems): parse the CDDL and validate the samples, with the `cddl` gem when present."""
    tool = find_tool("cddl")
    if not tool:
        return ["cddl not installed: manifests/signed_object_v2.cddl is not parsed here "
                "(gem install --user-install cddl)"], []
    lines, bad = [], []
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "signed_object_v2.cddl")
        open(src, "w", encoding="utf-8").write(text)
        r = subprocess.run([tool, src, "generate"], capture_output=True, text=True)
        if r.returncode:
            return lines, [f"manifests/signed_object_v2.cddl does not parse: {(r.stderr or r.stdout).strip()[:300]}"]
        lines.append("manifests/signed_object_v2.cddl parses")
        n = 0
        for name, blob in sample_statement():
            f = os.path.join(d, name + ".cbor")
            open(f, "wb").write(blob)
            r = subprocess.run([tool, src, "validate", f], capture_output=True, text=True)
            if r.returncode:
                bad.append(f"schema sample {name} does not validate: {(r.stderr or r.stdout).strip()[:300]}")
            n += 1
        f = os.path.join(d, "broken.cbor")
        # deliberate breaks: each sample below differs from a valid one in one way the text refuses
        refused = 0
        for why, blob in broken_samples():
            open(f, "wb").write(blob)
            if subprocess.run([tool, src, "validate", f], capture_output=True).returncode == 0:
                bad.append(f"deliberate break not caught: {why} validated")
            else:
                refused += 1
        lines.append(f"{n} schema samples validate (built here; no known-answer vector); "
                     f"{refused} broken samples are refused")
        # the genesis bundle's payload, checked against its own rule as the root: ceg-anything would
        # also admit a broken bundle as an attestation-envelope
        groot = os.path.join(d, "genesis.cddl")
        open(groot, "w", encoding="utf-8").write("genesis-root = ceg-genesis-bundle\n" + text)
        good, broken = genesis_samples()
        open(f, "wb").write(good)
        r = subprocess.run([tool, groot, "validate", f], capture_output=True, text=True)
        if r.returncode:
            bad.append(f"genesis bundle sample does not validate: {(r.stderr or r.stdout).strip()[:300]}")
        grefused = 0
        for why, blob in broken:
            open(f, "wb").write(blob)
            if subprocess.run([tool, groot, "validate", f], capture_output=True).returncode == 0:
                bad.append(f"deliberate break not caught: {why} validated")
            else:
                grefused += 1
        lines.append(f"1 genesis bundle sample validates; {grefused} broken bundles are refused")
        for root, (ok, broken), what in (("key-record-members", key_record_samples(), "key record with its custody member"),
                                         ("recovery-commitment-input", recovery_samples(), "recovery commitment input")):
            rp = os.path.join(d, root + ".cddl")
            open(rp, "w", encoding="utf-8").write(f"sample-root = {root}\n" + text)
            open(f, "wb").write(ok)
            r = subprocess.run([tool, rp, "validate", f], capture_output=True, text=True)
            if r.returncode:
                bad.append(f"{what} sample does not validate: {(r.stderr or r.stdout).strip()[:300]}")
            n_ref = 0
            for why, blob in broken:
                open(f, "wb").write(blob)
                if subprocess.run([tool, rp, "validate", f], capture_output=True).returncode == 0:
                    bad.append(f"deliberate break not caught: {why} validated")
                else:
                    n_ref += 1
            lines.append(f"1 {what} sample validates; {n_ref} broken ones are refused")
    return lines, bad


# ---------------------------------------------------------------- the Part block
def md_cell(s):
    return s.replace("|", "\\|")


def part_of(path):
    m = re.match(r"part_(\d+)_", os.path.basename(path))
    return m.group(1) if m else None


def cc_link(d, here):
    """A section link from the Part at `here`: same-file within that Part, the owning Part's file otherwise."""
    part = d.split(".")[0]
    if part == part_of(here):
        return f"[{d}](#{d})"
    hits = glob.glob(os.path.join(ROOT, "constitution", f"part_{part}_*.md"))
    return f"[{d}]({os.path.basename(hits[0])}#{d})" if hits else f"[{d}](#{d})"


def member_cell(r):
    m = r["member"]
    if r["rule"] == "-":
        return md_cell(m) if m != "-" else "—"
    return f"`{md_cell(m)}`"


def build_block(rows, here):
    L = [""]
    L.append("*This table is rendered from one data file and checked member for member against "
             "[`manifests/signed_object_v2.cddl`](../manifests/signed_object_v2.cddl), the schema; "
             "the two never disagree.*")
    L.append("")
    L.append("**Placement vocabulary.** `statement`: a position of the `COSE_Sign1` array. "
             "`header:protected`: the protected header, covered by the signature. "
             "`header:cwt`: a CWT claim inside the protected header. "
             "`header:unprotected`: never signed, and never read by a rule. "
             "`payload`: covered by the signature and by the row id. "
             "`payload:refs`: inside `refs`, the one member that names rows. "
             "`payload:body`: inside `body`. "
             "`derived`: computed by a verifier, never carried as such. "
             "`object`: a member of a signed object that is not a row. "
             "`none`: a logical name with no member of its own.")
    L.append("")
    L.append("**Logical names.** The Parts name members by their logical names. "
             "The logical name of each member stands in the first column; a logical name with no member of its own "
             "stands in the last table, with what carries it.")
    L.append("")
    for obj, title in OBJECTS:
        subset = [r for r in rows if r["object"] == obj]
        if not subset:
            continue
        L.append(f"**{title}**")
        L.append("")
        L.append("| Logical name | CBOR member | Placement | Type | Required when | CC | Note |")
        L.append("|---|---|---|---|---|---|---|")
        for r in subset:
            cc = " ".join(cc_link(d, here) for d in r["cc_ref"].split()) or "—"
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                ", ".join(f"`{md_cell(n.strip())}`" for n in r["logical_name"].split(",")) if r["logical_name"] != "-" else "—",
                member_cell(r), r["placement"],
                f"`{md_cell(r['type'])}`" if r["type"] != "-" else "—",
                md_cell(r["required_when"]), cc, md_cell(r["note"]) if r["note"] != "-" else "—"))
        L.append("")
    return "\n".join(L)


def locate(text):
    """(start, end) line indexes of the block's body (exclusive of the marker lines or the heading), the
    form ('markers' or 'heading'), or None."""
    lines = text.split("\n")
    b = [i for i, l in enumerate(lines) if l.strip() == BEGIN]
    e = [i for i, l in enumerate(lines) if l.strip() == END]
    if b or e:
        if len(b) != 1 or len(e) != 1 or e[0] < b[0]:
            raise SystemExit(f"{NAME}: the marker lines must stand once each, BEGIN before END")
        return b[0] + 1, e[0], "markers"
    for i, l in enumerate(lines):
        if re.match(r"^#{2,6}\s+\d+(?:\.\d+)*\s+`" + re.escape(SLUG) + r"`", l):
            j = i + 1
            while j < len(lines) and not re.match(r"^#{2,6}\s+\d", lines[j]):
                j += 1
            return i + 1, j, "heading"
    return None


def target():
    hits = []
    for p in sorted(glob.glob(os.path.join(ROOT, "constitution", "part_*.md"))):
        t = open(p, encoding="utf-8").read()
        loc = locate(t)
        if loc:
            hits.append((p, t, loc))
    marked = [h for h in hits if h[2][2] == "markers"]
    hits = marked or hits
    if len(hits) > 1:
        raise SystemExit(f"{NAME}: the block stands in more than one Part: {[os.path.basename(h[0]) for h in hits]}")
    return hits[0] if hits else None


def render(path, text, loc, rows):
    lines = text.split("\n")
    s, e, _ = loc
    return "\n".join(lines[:s] + build_block(rows, path).split("\n") + lines[e:])


def main(argv):
    rows = load_rows()
    text = open(CDDL, encoding="utf-8").read()
    bad = agreement_with_breaks(rows, text)
    lines, cbad = cddl_checks(text)
    bad += cbad
    rline, rbad = reader_checks()
    lines.append(rline)
    bad += rbad
    n_members = sum(1 for r in rows if r["rule"] != "-")
    print(f"{NAME}: {len(rows)} rows ({n_members} members, {len(rows) - n_members} logical names); "
          f"table and CDDL agree on {len(members(text))} members; three deliberate breaks caught" if not bad else
          f"{NAME}: {len(bad)} problem(s)")
    for l in lines:
        print(l)
    for b in bad:
        print("  MISMATCH", b)
    if bad:
        return 1
    t = target()
    if t is None:
        print(f"{NAME}: no Part holds the marker lines or a `{SLUG}` heading; the table is not written")
        return 1
    path, txt, loc = t
    out = render(path, txt, loc, rows)
    rel = os.path.relpath(path, ROOT)
    if "--check" in argv:
        if out != txt:
            print(f"{NAME}: {rel} is stale; run python3 tools/build_cc_signed_object_v2.py")
            return 1
        print(f"{NAME}: {rel} is current ({loc[2]})")
        return 0
    if out != txt:
        open(path, "w", encoding="utf-8").write(out)
    print(f"{NAME}: {rel} {'updated' if out != txt else 'unchanged'} ({loc[2]})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
