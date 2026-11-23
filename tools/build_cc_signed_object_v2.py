#!/usr/bin/env python3
"""
CC (the CIRIS Constitution) — the signed object of CC 2.6.1 (CBOR and COSE), its members table.

Sources:
  manifests/signed_object_v2.cddl     the normative schema, hand-written (RFC 8610 CDDL over CBOR)
  manifests/family_payloads_v2.cddl   OUTPUT: the payload rules of nine families (CC 2.6.1.4), emitted from this
                                      table's rows over the rules of the schema and read with it; kept apart so
                                      the Internet-Draft's copy of the schema (tools/build_ietf_draft.py) does
                                      not carry them until the two merge in its next revision
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
  A reference reader of step 8 of CC 2.6.1.8 (a statement's key is a key of its iss, CC 2.6.1.7) runs over
  samples, each with the answer the text gives, and over deliberate breaks of the rotation record's shape
  (CC 3.1.3 `key:record`) that must each give their own answer.
  The payloads of nine families (CC 2.6.1.4): one valid payload of each family rule validates and broken ones are
  refused; the rules the CDDL cannot state (a member required on one stage, axis or state; a dimension leaf equal to
  its member; a cosign:{state} row with a payload of its own) refuse edition2_payload_invalid, over deliberate breaks.
  --check   check, and compare the block with what the Part holds; write nothing (exit 1 when stale)

stdlib only. Run:  python3 tools/build_cc_signed_object_v2.py [--check]
"""
import base64, csv, glob, hashlib, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "constitution", "signed_object_v2.tsv")
CDDL = os.path.join(ROOT, "manifests", "signed_object_v2.cddl")
FAMILY_CDDL = os.path.join(ROOT, "manifests", "family_payloads_v2.cddl")
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
    ("accord", "The accord's rows: an invocation and a lifecycle row"),
    ("roster", "The roster version: the payload of a `group:roster` row"),
    ("membership", "A membership change: the payload of a `membership:{stage}` row at the stages `widening` and `removal`"),
    ("occurrence_revocation", "An occurrence revocation: the payload of an `identity:occurrence_revocation` row"),
    ("revocation", "An entity revocation: the payload of a `revocation:{entity_type}:{reason}` row"),
    ("takedown", "A takedown notice: the payload of a `takedown_notice:{basis}` row"),
    ("custody", "A custody report: the payload of a `custody:{kind}` row"),
    ("key_grant", "A key grant: the payload of a `key_grant:{axis}` row"),
    ("delivery_ack", "A delivery ack: the payload of a `delivery_ack:{stream_id}` row"),
    ("trust_accepts", "An acceptance edge: the members this form names of a `trust:accepts` row"),
    ("build_manifest", "A build manifest: the payload of a `provenance:build_manifest:{target}` row"),
    ("grant", "A grant: the members this form names of a `trust:confers` row"),
    ("grant_acceptance", "The acceptance of a grant: the payload of a `membership:acceptance` row that answers a grant"),
    ("grant_withdrawal", "The holders' withdrawal of a grant: the payload of a counted `withdraws` row"),
    ("occurrence", "An occurrence: the payload of an `identity:occurrence` row"),
    ("amendment", "An identity amendment: the payload of an `identity_amendment` row"),
    ("admission", "An admission of a unit: the members of an `admission:unit` row"),
    ("deferral", "A deferral response: the members this form names of a `deferral:response:{outcome}` row"),
    ("deferral_request", "A deferral request: the members this form names of a `deferral:request` row"),
    ("rebind", "A canonical re-bind: the payload of a `transport:canonical_rebind` row"),
    ("binding", "The transport destination binding (`identity:occurrence`)"),
    ("room", "The seat commitment of a room key"),
    ("group_id", "The id of a group: what its first version derives it from"),
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


def statement(payload, sig=3373, iss=ISS, cty=CTY, rtype="scores", family="custody:.kind", unprotected=None):
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
                           "scope": ["infra:serve", "infra:attest"]}}     # a set, in CDE order: the shorter first
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
        ("a witness quorum of 1", genesis_payload(charter=dict(charter, receipt_quorum=1))),
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


def accord_samples():
    """(valid, broken) for the accord's invocation and lifecycle payloads (CC 4.2.1.1, CC 4.2.1.3)."""
    inv = {"author": ISS, "accord_root": "humanity-accord", "invocation_id": "halt-1", "nonce": bytes(32), "asserted_at": 1763078400000,
           "valid_until": 1763164800000}
    ref = lambda n: [2, [-16, bytes([n]) * 32]]
    life = {"refs": {"head": ref(1), "target": ref(2)}, "dimension": "accord:lifecycle:active:v1", "accord_root": "humanity-accord",
            "invocation_id": "resume-1", "nonce": bytes(32), "asserted_at": 1763078400000, "valid_until": 1763164800000}
    return [("accord-invocation", cde(inv), [
                ("an invocation carrying invocation_kind", cde(dict(inv, invocation_kind="constitutional"))),
                ("an invocation with a nonce of 31 bytes", cde(dict(inv, nonce=bytes(31)))),
                ("an invocation with no author", cde({k: v for k, v in inv.items() if k != "author"})),
                ("an invocation carrying the earlier payload_sha256", cde(dict(inv, payload_sha256="00" * 32))),
                ("an invocation with no accord_root", cde({k: v for k, v in inv.items() if k != "accord_root"})),
                ("a notify's payload_digest in hex", cde(dict(inv, payload_digest="00" * 32))),
                ("an invocation with valid_until as text", cde(dict(inv, valid_until="2026-11-15T00:00:00.000Z")))]),
            ("accord-lifecycle", cde(life), [
                ("a lifecycle row with an author", cde(dict(life, author=ISS))),
                ("a lifecycle row naming no halt", cde(dict(life, refs={"head": ref(1)}))),
                ("a lifecycle row naming its halt by an id string", cde(dict(life, resumes_halt_id="halt-1"))),
                ("a lifecycle row naming an earlier-form halt", cde(dict(life, refs={"head": ref(1), "target": [1, [-16, bytes(32)]]})))])]


def end_rule(p):
    """The rule the CDDL cannot state, for every payload that states valid_until (CC 2.6.2, step 4 of CC 2.6.1.8): it
    is later than asserted_at, since a record covers asserted_at <= t < valid_until and an equal one covers nothing."""
    if "valid_until" in p and p["valid_until"] <= p["asserted_at"]:
        return "valid_until_not_after_asserted_at"
    return None


def family_ids():
    """Every registry prefix as a family id (CC 2.6.1.1): each {name} written .name and each * written ."""
    import json, re as _re
    reg = json.load(open(os.path.join(ROOT, "manifests", "namespace_registry.json"), encoding="utf-8"))
    return {_re.sub(r"\{([a-z_]+)\}", r".\1", f["prefix"]).replace("*", ".") for f in reg["families"]}


def family_checks():
    """(line, problems): the samples' family ids are registry family ids, the lifecycle sample's dimension matches its
    family with no refusal, and the accord rule refuses a valid_until not after asserted_at."""
    import cc_namespace_match as NM
    bad = []
    ids = family_ids()
    for fam in ("custody:.kind",):
        if fam not in ids:
            bad.append(f"sample family id {fam} is not a registry family id")
    man = NM.load_manifest()
    dim = "accord:lifecycle:active:v1"
    got = NM.match_family(man, dim)
    if not got or got[0] != "accord:lifecycle:{kind}" or got[2] is not None:
        bad.append(f"sample dimension {dim} does not match its family: {got}")
    if NM.match_family(man, "accord:lifecycle:active")[2] is None:
        bad.append("deliberate break not caught: a lifecycle dimension with no version segment matched")
    ok = {"author": ISS, "asserted_at": 1763078400000, "valid_until": 1763164800000}
    node_rec = {"key": {1: 7}, "identity_type": ["node"], "asserted_at": 1763078400000, "valid_until": 1794614400000}
    for what, good in (("an invocation", ok), ("a node key record", node_rec)):
        if end_rule(good) is not None or end_rule(dict(good, valid_until=good["asserted_at"])) != "valid_until_not_after_asserted_at":
            bad.append(f"deliberate break not caught: {what} whose valid_until equals its asserted_at")
    return ("sample families are registry family ids; the lifecycle dimension matches; a valid_until not after "
            "asserted_at is refused, for an invocation and for a key record"), bad


def binding_samples():
    """(valid, broken) for the transport destination binding (CC 3.3.6.2)."""
    td = {"reticulum_x25519_pubkey": bytes(32), "reticulum_ed25519_pubkey": bytes([1]) * 32, "app_name": "ciris",
          "aspects": ["node", "transit"], "destination_hash": bytes(16)}
    rec = [2, [-16, bytes([4]) * 32]]             # the seat's own key record: the head a first bind names, and its citation
    b = {"author": iref(3), "identity_key_id": iref(3), "occurrence_key_id": iref(3), "device_class": "server",
         "asserted_at": 1763078400000, "transport_destination": td, "transit_xwing_pubkey": bytes([2]) * 1216,
         "onion_hop_xwing_pubkey": bytes([3]) * 1216, "refs": {"head": rec, "also": {"cites": [rec]}}}
    return cde(b), [
        ("a binding with no transport_destination", cde({k: v for k, v in b.items() if k != "transport_destination"})),
        ("a transit key of 1184 bytes", cde(dict(b, transit_xwing_pubkey=bytes(1184)))),
        ("an X-Wing key inside transport_destination", cde(dict(b, transport_destination=dict(td, transit_xwing_pubkey=bytes(1216))))),
        ("a destination_hash in hex", cde(dict(b, transport_destination=dict(td, destination_hash="00" * 16)))),
        ("an opt-out marker of false", cde(dict(b, onion_relay={"opt_out": False}))),
    ]


def _seat_binding_without_head():
    """The binding sample with refs.head removed: refused alone, as identity:occurrence's rule requires a head."""
    import copy
    td = {"reticulum_x25519_pubkey": bytes(32), "reticulum_ed25519_pubkey": bytes([1]) * 32, "app_name": "ciris",
          "aspects": ["node", "transit"], "destination_hash": bytes(16)}
    rec = [2, [-16, bytes([4]) * 32]]
    return {"author": iref(3), "identity_key_id": iref(3), "occurrence_key_id": iref(3), "device_class": "server",
            "asserted_at": 1763078400000, "transport_destination": td, "transit_xwing_pubkey": bytes([2]) * 1216,
            "onion_hop_xwing_pubkey": bytes([3]) * 1216, "refs": {"also": {"cites": [rec]}}}


def recovery_samples():
    key = {1: 7, 3: -70100, -1: bytes(1984)}
    return cde(["CEG-recovery/2", [key]]), [("a commitment over no key", cde(["CEG-recovery/2", []]))]


# ---------------------------------------------------------------- the payloads of nine families (CC 2.6.1.4)
PAYLOAD_INVALID = "edition2_payload_invalid"


def _ref(n):
    return [2, [-16, bytes([n]) * 32]]


def family_payloads():
    """{root: (family id, valid payload)}: one valid payload of each family rule, placeholder ids and digests."""
    t, dig = 1763078400000, [-16, bytes([7]) * 32]
    members = sorted([{"key": iref(0), "joined_at": t, "role": "founder"}, {"key": iref(1), "joined_at": t}], key=cde)
    return {
        "group-roster": ("group:roster", {
            "group_kind": "community", "group": gref(5), "name": "Austin", "version": 2, "members": members,
            "founded_at": t, "consensus_protocol": "majority", "consensus_protocol_entrenched": False,
            "cohort_subkind": "geographic", "membership": "public",
            "refs": {"head": _ref(1), "also": {"cites": [_ref(2)]}}, "asserted_at": t}),
        "membership-change": ("membership:.stage", {
            "dimension": "membership:widening:v1", "group_kind": "family", "group": gref(5), "member": iref(2),
            "joined_at": t, "effective_at": t, "refs": {"head": _ref(1), "also": {"cites": [_ref(3)]}}, "asserted_at": t}),
        "occurrence-revocation": ("identity:occurrence_revocation", {
            "author": iref(0), "identity_key_id": iref(0), "occurrence_key_id": iref(3), "revoked_at": t, "effective_at": t,
            "refs": {"head": _ref(10), "also": {"cites": sorted([_ref(13), _ref(14)], key=cde)}}, "asserted_at": t}),
        "entity-revocation": ("revocation:.entity_type:.reason", {
            "author": iref(0), "dimension": "revocation:agent:compromised:v1", "revoked_at": t, "effective_at": t,
            "asserted_at": t}),
        "takedown-notice": ("takedown_notice:.basis", {
            "author": iref(0), "dimension": "takedown_notice:dmca512:v1", "legal_basis": "dmca512", "claimant": iref(0),
            "content_sha256": dig, "content_holders": [iref(1)], "jurisdiction": "US", "good_faith_statement": "sample",
            "claim_text": "sample", "evidence_refs": [dig], "asserted_at": t}),
        "custody-ack": ("custody:.kind", {
            "author": iref(1), "dimension": "custody:ack:v1", "custody_state": "here", "evidence_refs": [dig], "size": 4096,
            "asserted_at": t}),
        "key-grant": ("key_grant:.axis", {
            "author": iref(0), "dimension": "key_grant:epoch:v1", "axis": "epoch",
            "wrap_algorithm": "x25519_mlkem768_aes256_gcm_hkdf_sha256", "wrapped_dek": bytes(40), "community": gref(5),
            "minter": iref(0), "epoch": 3, "asserted_at": t}),
        "identity-occurrence": ("identity:occurrence", {
            "author": iref(0), "identity_key_id": iref(0), "occurrence_key_id": iref(3), "device_class": "phone",
            "encryption_pubkeys": {"x25519": bytes([5]) * 32, "ml_kem_768": bytes([6]) * 1184},
            "build_manifest_hash": dig, "refs": {"head": _ref(10), "further_heads": [_ref(11)], "also": {"cites": [_ref(4)]}},
            "asserted_at": t, "valid_until": t + 1}),
        "identity-amendment": ("identity_amendment", {
            "author": iref(3), "amendment_digest": dig, "refs": {"also": {"cites": [_ref(5)]}}, "asserted_at": t}),
        "deferral-response": ("deferral:response:.outcome", {
            "author": iref(1), "dimension": "deferral:response:approved:v1", "amendment_digest": dig,
            "deferral_id": "d-17", "refs": {"answers": _ref(6)}, "asserted_at": t}),
        "deferral-request": ("deferral:request", {
            "author": iref(3), "deferral_id": "d-17", "reason_digest": dig, "asserted_at": t,
            "valid_until": t + 86400000}),
        "canonical-rebind": ("transport:canonical_rebind", {
            "refs": {"head": _ref(9)}, "transport_destination": {
                "reticulum_x25519_pubkey": bytes(32), "reticulum_ed25519_pubkey": bytes([1]) * 32, "app_name": "ciris",
                "aspects": ["node", "transit"], "destination_hash": bytes(16)},
            "transit_xwing_pubkey": bytes([2]) * 1216, "onion_hop_xwing_pubkey": bytes([3]) * 1216, "asserted_at": t}),
        "admission-unit": ("admission:unit", {
            "author": iref(0), "unit": dig, "capabilities": ["read", "compute"], "cohort_scope": "self", "asserted_at": t,
            "valid_until": t + 86400000}),
        "trust-accepts": ("trust:accepts", {
            "author": iref(0), "dimension": "trust:accepts:v1", "trust_classes": ["transparency"],
            "service_key": {1: 2, 3: -7, -1: 1, -2: bytes(32), -3: bytes(32)}, "asserted_at": t}),
        "delivery-ack": ("delivery_ack:.stream_id", {
            "author": iref(1), "dimension": "delivery_ack:s1:v1", "stream_id": "s1", "epoch": 3, "k": 12,
            "chunk_root": dig, "asserted_at": t}),
        "build-manifest-row": ("provenance:build_manifest:.target", {
            "author": iref(4), "dimension": "provenance:build_manifest:x86_64-unknown-linux-gnu:v1",
            "build": {"project": "ciris-verify", "version": "1.2.3", "manifest_hash": dig, "manifest_size": 2048},
            "evidence_refs": [dig], "refs": {"head": _ref(9)}, "asserted_at": t}),
        "trust-confers": ("trust:.job:.version", {
            "dimension": "trust:confers:v1", "scope": [PIPELINE_SCOPE],
            "projects": sorted(["ciris-agent", "ciris-verify"], key=cde), "refs": {"head": _ref(9)}, "asserted_at": t}),
        "grant-acceptance": ("membership:.stage", {
            "author": iref(0), "dimension": "membership:acceptance:v1", "refs": {"answers": _ref(15)}, "asserted_at": t}),
        "grant-withdrawal": ("trust:.job:.version", {
            "refs": {"head": _ref(9), "target": _ref(15)}, "lifts": True, "asserted_at": t}),
    }


def _without(p, *keys):
    return {k: v for k, v in p.items() if k not in keys}


def family_payload_samples():
    """[(root, what, valid bytes, [(why, broken bytes)])]: each broken payload one change away from the valid one,
    refused by the schema."""
    P = {k: v for k, (_, v) in family_payloads().items()}
    W = lambda root, **c: cde(dict(P[root], **c))
    D = lambda root, *k: cde(_without(P[root], *k))
    return [
        ("group-roster", "group:roster payload", cde(P["group-roster"]), [
            ("a roster version with no members", D("group-roster", "members")),
            ("a member named by a key id", W("group-roster", members=[{"key": "A1", "joined_at": 1763078400000}])),
            ("an entrenchment written as text", W("group-roster", consensus_protocol_entrenched="true")),
            ("a member's joined_at as text", W("group-roster", members=[{"key": iref(0), "joined_at": "2026-11-14T00:00:00Z"}]))]),
        ("membership-change", "membership:{stage} payload", cde(P["membership-change"]), [
            ("a widening with no refs", D("membership-change", "refs")),
            ("a change to a group of another kind", W("membership-change", group_kind="room")),
            ("a reason in free text", W("membership-change", reason="spam"))]),
        ("occurrence-revocation", "identity:occurrence_revocation payload", cde(P["occurrence-revocation"]), [
            ("a revocation with no occurrence_key_id", D("occurrence-revocation", "occurrence_key_id")),
            ("an effective_at as text", W("occurrence-revocation", effective_at="2026-11-14T00:00:00Z")),
            ("a revocation naming no self-roster head", D("occurrence-revocation", "refs")),
            ("a revocation whose refs name tips but no head", W("occurrence-revocation", refs={"further_heads": [_ref(11)], "also": {"cites": [_ref(13)]}})),
            ("an eviction without its signer's proof", W("occurrence-revocation", refs={"head": _ref(10)})),
            ("an eviction whose proof is under another role", W("occurrence-revocation", refs={"head": _ref(10), "also": {"ack": [_ref(13)]}}))]),
        ("entity-revocation", "revocation:{entity_type}:{reason} payload", cde(P["entity-revocation"]), [
            ("an entity revocation with no author", D("entity-revocation", "author")),
            ("an entity revocation with revoked_at as text", W("entity-revocation", revoked_at="2026-11-14T00:00:00Z"))]),
        ("takedown-notice", "takedown_notice:{basis} payload", cde(P["takedown-notice"]), [
            ("a notice on an unlisted basis", W("takedown-notice", legal_basis="DMCA512")),
            ("a content digest in hex", W("takedown-notice", content_sha256="00" * 32)),
            ("a notice with no claimant", D("takedown-notice", "claimant"))]),
        ("custody-ack", "custody:{kind} payload", cde(P["custody-ack"]), [
            ("a report on two blobs", W("custody-ack", evidence_refs=[[-16, bytes([7]) * 32], [-16, bytes([8]) * 32]])),
            ("a custody_state outside the two", W("custody-ack", custody_state="lost"))]),
        ("key-grant", "key_grant:{axis} payload", cde(P["key-grant"]), [
            ("a grant under the v1 wrap", W("key-grant", wrap_algorithm="hpke_rfc9180_base_x25519_aes_gcm")),
            ("a wrapped key in base64", W("key-grant", wrapped_dek="AAAA")),
            ("a grant with no axis", D("key-grant", "axis"))]),
        ("identity-occurrence", "a seat's binding as an identity:occurrence", binding_samples()[0], [
            ("a seat binding without refs.head", cde(_seat_binding_without_head()))]),
        ("identity-occurrence", "identity:occurrence payload", cde(P["identity-occurrence"]), [
            ("an occurrence of an unlisted device class", W("identity-occurrence", device_class="tablet")),
            ("an ML-KEM-768 key of 1183 bytes", W("identity-occurrence", encryption_pubkeys={"x25519": bytes(32), "ml_kem_768": bytes(1183)})),
            ("a build manifest hash in hex", W("identity-occurrence", build_manifest_hash="00" * 32)),
            ("an occurrence with no device_class", D("identity-occurrence", "device_class")),
            ("an occurrence naming no self-roster head", W("identity-occurrence", refs={"also": {"cites": [_ref(4)]}})),
            ("an occurrence whose refs carry a role a self-roster row does not", W("identity-occurrence", refs={"head": _ref(10), "answers": _ref(12)}))]),
        ("identity-amendment", "identity_amendment payload", cde(P["identity-amendment"]), [
            ("an amendment digest in hex, the earlier form", W("identity-amendment", amendment_digest="cd" * 32)),
            ("an amendment naming no approval", D("identity-amendment", "refs"))]),
        ("deferral-response", "deferral:response:{outcome} payload", cde(P["deferral-response"]), [
            ("an approval's amendment digest in hex", W("deferral-response", amendment_digest="cd" * 32)),
            ("a response naming no request", D("deferral-response", "refs")),
            ("a response with no deferral_id", D("deferral-response", "deferral_id"))]),
        ("deferral-request", "deferral:request payload", cde(P["deferral-request"]), [
            ("a reason digest in hex", W("deferral-request", reason_digest="ab" * 32)),
            ("a request with no end", D("deferral-request", "valid_until")),
            ("a request with no reason_digest", D("deferral-request", "reason_digest")),
            ("a request with no deferral_id", D("deferral-request", "deferral_id"))]),
        ("canonical-rebind", "transport:canonical_rebind payload", cde(P["canonical-rebind"]), [
            ("a re-bind naming no bundle", D("canonical-rebind", "refs")),
            ("a re-bind with a transit key of 1184 bytes", W("canonical-rebind", transit_xwing_pubkey=bytes(1184)))]),
        ("admission-unit", "admission:unit payload", cde(P["admission-unit"]), [
            ("a unit digest in hex", W("admission-unit", unit="ab" * 32)),
            ("a capability outside the closed set", W("admission-unit", capabilities=["compute", "shell"])),
            ("an admission with no capability", W("admission-unit", capabilities=[])),
            ("an admission with no lease end", D("admission-unit", "valid_until"))]),
        ("body-decimal", "body decimal 0.5", cde(Tag(4, [-1, 5])), [
            ("a decimal with a non-negative exponent", cde(Tag(4, [0, 5]))),
            ("a decimal of three members", cde(Tag(4, [-1, 5, 0])))]),
        ("ceg-statement", "an admission:unit statement with a Transparency Service's receipt",
         statement(P["admission-unit"], rtype="scores", family="admission:unit", unprotected={394: [cde(_receipt())]}), [
            ("receipts as one byte string, not an array", statement(P["admission-unit"], rtype="scores", family="admission:unit",
                                                                    unprotected={394: cde(_receipt())}))]),
        # a statement's validity never depends on its receipts: these stay valid, and the host's rule ignores the receipts
        ("ceg-statement", "an admission:unit statement with an empty receipts array",
         statement(P["admission-unit"], rtype="scores", family="admission:unit", unprotected={394: []}), []),
        ("ceg-statement", "an admission:unit statement whose receipt is no COSE_Sign1",
         statement(P["admission-unit"], rtype="scores", family="admission:unit", unprotected={394: [cde([bytes(4), {}, None, bytes(64)])]}), []),
        ("trust-accepts", "a transparency edge carrying its service's COSE key", cde(family_payloads()["trust-accepts"][1]), [
            ("a service key that is a key id, not an identity reference", cde(dict(family_payloads()["trust-accepts"][1], service_key="A1"))),
            ("a trust depth of 6", cde(dict(family_payloads()["trust-accepts"][1], trust_depth=6)))]),
        ("delivery-ack", "delivery_ack:{stream_id} payload", cde(P["delivery-ack"]), [
            ("an ack with no chunk index", D("delivery-ack", "k")),
            ("a chunk root as bare bytes", W("delivery-ack", chunk_root=bytes(32)))]),
        ("build-manifest-row", "provenance:build_manifest:{target} payload", cde(P["build-manifest-row"]), [
            ("a build manifest with no build descriptor", D("build-manifest-row", "build")),
            ("a descriptor with no project", W("build-manifest-row", build=_without(P["build-manifest-row"]["build"], "project"))),
            ("a descriptor with no version", W("build-manifest-row", build=_without(P["build-manifest-row"]["build"], "version"))),
            ("a manifest hash as bare bytes", W("build-manifest-row", build=dict(P["build-manifest-row"]["build"], manifest_hash=bytes(32)))),
            ("a manifest size as text", W("build-manifest-row", build=dict(P["build-manifest-row"]["build"], manifest_size="2048"))),
            ("a descriptor with a fifth member", W("build-manifest-row", build=dict(P["build-manifest-row"]["build"], generated_at=1763078400000))),
            ("a build manifest citing no blob", D("build-manifest-row", "evidence_refs")),
            ("a build manifest naming no bundle", D("build-manifest-row", "refs"))]),
        ("trust-confers", "trust:confers payload of a build pipeline's grant", cde(P["trust-confers"]), [
            ("a grant with no scope", D("trust-confers", "scope")),
            ("a scope as a bare token", W("trust-confers", scope=PIPELINE_SCOPE)),
            ("an empty projects set", W("trust-confers", projects=[])),
            ("a grant naming no bundle", D("trust-confers", "refs"))]),
        ("grant-acceptance", "membership:acceptance payload answering a grant", cde(P["grant-acceptance"]), [
            ("an acceptance with no author", D("grant-acceptance", "author")),
            ("an acceptance naming no grant", D("grant-acceptance", "refs"))]),
        ("grant-withdrawal", "the payload of a counted withdraws of a grant", cde(P["grant-withdrawal"]), [
            ("a withdrawal naming nothing", D("grant-withdrawal", "refs")),
            ("lifts written as false", W("grant-withdrawal", lifts=False))]),
    ]


def _strip_none(p):
    return {k: v for k, v in p.items() if v is not None}


def _segment(dim, i):
    s = dim.split(":")
    return s[i] if len(s) > i else None


def family_payload_rule(root, p, family=None):
    """The rules of a family's payload the CDDL cannot state, checked in prose: None, or edition2_payload_invalid.
    `family` is the statement's family label; a cosign:{state} family has no payload of its own (CC 3.1.3)."""
    if family == "cosign:.state":
        return PAYLOAD_INVALID                            # a pending or signature state is a statement over the event's own payload
    dim = p.get("dimension", "")
    if root == "membership-change":
        stage = _segment(dim, 1)
        if stage not in ("widening", "removal"):
            return PAYLOAD_INVALID
        if (stage == "widening") != ("joined_at" in p) or (stage == "removal") != ("removed_at" in p):
            return PAYLOAD_INVALID
        if "head" not in p.get("refs", {}):
            return PAYLOAD_INVALID
    if root == "custody-ack" and (p.get("custody_state") == "here") != ("size" in p):
        return PAYLOAD_INVALID
    if root == "key-grant":
        need = {"content": ("at_rest_sha256", "owner"), "epoch": ("community", "minter", "epoch"),
                "stream": ("stream_id", "epoch", "owner")}.get(p.get("axis"), ())
        if _segment(dim, 1) != p.get("axis") or any(m not in p for m in need):
            return PAYLOAD_INVALID
    if root == "delivery-ack" and _segment(dim, 1) != p.get("stream_id"):
        return PAYLOAD_INVALID
    if root == "takedown-notice":
        if _segment(dim, 1) != p.get("legal_basis") or (p.get("legal_basis") == "steward_purge" and "author" in p):
            return PAYLOAD_INVALID
    if root == "deferral-response" and "reason_digest" in p:
        return PAYLOAD_INVALID                            # the reason is the request's; a response carries none
    if root == "canonical-rebind" and "head" not in p.get("refs", {}):
        return PAYLOAD_INVALID                            # counted over the bundle in force, named in refs.head
    if root == "group-roster" and (p.get("version") == 1) != ("head" not in p.get("refs", {})):
        return PAYLOAD_INVALID
    if root == "group-roster" and group_id_rule(p) is not None:
        return PAYLOAD_INVALID                            # a first version's id is derived from it (group_id_rule gives the token)
    refs = p.get("refs", {})
    if root == "build-manifest-row":
        if dim.split(":")[:2] != ["provenance", "build_manifest"] or "head" not in refs:
            return PAYLOAD_INVALID                        # the bundle the pipeline's grant names, in refs.head
        if p.get("build", {}).get("manifest_hash") not in p.get("evidence_refs", []):
            return PAYLOAD_INVALID                        # the blob the descriptor names is the blob the row cites
    if root == "trust-confers":
        if dim != "trust:confers:v1" or "head" not in refs or "author" in p:
            return PAYLOAD_INVALID                        # counted over the bundle in force, with no author
        for m in ("scope", "projects"):
            if m in p and p[m] != sorted(set(p[m]), key=cde):
                return PAYLOAD_INVALID                    # each a set (CC 2.6.1.2)
    if root == "grant-acceptance" and (dim != "membership:acceptance:v1" or "answers" not in refs or "head" in refs):
        return PAYLOAD_INVALID                            # names the one grant it accepts, and no head
    if root == "grant-withdrawal" and ("target" not in refs or "head" not in refs or "author" in p):
        return PAYLOAD_INVALID                            # the grant withdrawn and the head the count acts from
    return None


UNIT_LEASE_MAX_MS = 86400 * 1000                         # unit_lease_max_secs (CC 2.7.11)
CAPS = ("compute", "read", "net_send", "submit", "sign", "store_write", "actuate")
EFFECTS = ("net_send", "submit", "sign", "store_write", "actuate")


def admission_unit_rule(p):
    """The static checks of an admission:unit payload (CC 2.7.11, CC 2.6.1.8 step 5): None, or its token."""
    if ("author" in p) == ("head" in p.get("refs", {})):
        return "admission_unit_malformed"
    caps = p.get("capabilities", [])
    if not caps or any(c not in CAPS for c in caps):
        return "admission_capability_unknown"
    if not p["asserted_at"] < p["valid_until"] <= p["asserted_at"] + UNIT_LEASE_MAX_MS:
        return "admission_lease_out_of_window"
    if "author" in p and any(c in EFFECTS for c in caps) and p.get("cohort_scope") != "self":
        return "admission_owner_row_not_self"               # an owner-alone row admits only on its author's own hosts
    return None


def admission_samples():
    """[(what, payload, expected)]: an authored and a counted row that pass, and one refusal per token.
    The answers that read other rows (the issuer's standing, a count not met, a head not held, which waits) are the
    host's and are run by formal/admission."""
    base = family_payloads()["admission-unit"][1]
    t = base["asserted_at"]
    counted = dict(_without(base, "author"), capabilities=["compute", "net_send"], refs={"head": _ref(8)})
    return [
        ("one person admits a unit that reads and computes, for a day", base, None),
        ("a group counts an effect over its head", counted, None),
        ("an author and a head both", dict(counted, author=iref(0)), "admission_unit_malformed"),
        ("neither an author nor a head", _without(base, "author"), "admission_unit_malformed"),
        ("a capability outside the seven", dict(base, capabilities=["compute", "shell"]), "admission_capability_unknown"),
        ("a lease of a day and a millisecond", dict(base, valid_until=t + UNIT_LEASE_MAX_MS + 1), "admission_lease_out_of_window"),
        ("a lease that ends as it opens", dict(base, valid_until=t), "admission_lease_out_of_window"),
        ("the owner's own row names an effect at self scope: it admits only on the owner's own hosts", dict(base, capabilities=["compute", "net_send"], cohort_scope="self"), None),
        ("a counted row at federation scope: a registry's admission for every host that accepts it", dict(counted, cohort_scope="federation"), None),
        ("one person's row names an effect at federation scope", dict(base, capabilities=["compute", "net_send"], cohort_scope="federation"), "admission_owner_row_not_self"),
    ]


def _receipt(service=b"ts-1"):
    """A schema-sample COSE receipt (RFC 9942): vds 1 (RFC9162_SHA256) protected, one inclusion proof under vdp."""
    return Tag(18, [cde({1: -7, 395: 1, 4: service}), {396: {-1: [bytes(32)]}}, None, bytes(64)])


def group_id(group_kind, founders, founded_at, nonce):
    """CC 3.3.4: a group's id, derived from its first version. founders: the key of every member it lists, a set."""
    pre = cde(["CEG-group/2", group_kind, sorted(set(founders), key=cde), founded_at, nonce])
    return "group-" + base64.urlsafe_b64encode(hashlib.sha256(pre).digest()).decode().rstrip("=")


def gref(n):
    """A schema-sample group id: the form of group_id, over placeholder bytes."""
    return "group-" + chr(ord("A") + n) * 42 + "A"


GROUP_ID_NOT_OF_FOUNDING = "group_id_not_of_founding"


def group_id_rule(p):
    """CC 3.3.4, the rule of a group:roster payload the CDDL cannot state: None, or its token. A first version (the one
    that names no head) carries `nonce` and its `group` is the id derived from its own members; a later version
    carries no `nonce` and is judged by its descent."""
    first = "head" not in p.get("refs", {})
    if not first:
        return PAYLOAD_INVALID if "nonce" in p else None
    n = p.get("nonce")
    if not isinstance(n, bytes) or len(n) != 32:
        return PAYLOAD_INVALID
    want = group_id(p.get("group_kind"), [m["key"] for m in p.get("members", [])], p.get("founded_at"), n)
    return None if p.get("group") == want else GROUP_ID_NOT_OF_FOUNDING


def group_id_samples():
    """(what, payload, expected): a founding and the ways it is refused."""
    t = 1763078400000
    mem = sorted([{"key": iref(0), "joined_at": t, "role": "founder"}, {"key": iref(1), "joined_at": t, "role": "founder"}], key=cde)
    nonce = bytes(range(32))
    base = {"group_kind": "community", "name": "Austin", "version": 1, "members": mem, "founded_at": t,
            "consensus_protocol": "majority", "nonce": nonce, "asserted_at": t}
    gid = group_id("community", [iref(0), iref(1)], t, nonce)
    first = dict(base, group=gid)
    later = dict(_without(first, "nonce"), version=2, refs={"head": _ref(1)})
    return [
        ("a founding whose id is derived from it", first, None),
        ("the same founding with its members listed in the other order", dict(first, members=list(reversed(mem))), None),
        ("a later version, which carries no nonce", later, None),
        ("a founding under an id its founders chose", dict(first, group=gref(5)), GROUP_ID_NOT_OF_FOUNDING),
        ("a founding under the id of another kind of group", dict(first, group_kind="family"), GROUP_ID_NOT_OF_FOUNDING),
        ("a founding under the id of another founding instant", dict(first, founded_at=t + 1), GROUP_ID_NOT_OF_FOUNDING),
        ("a founding that lists a member its id does not cover", dict(first, members=sorted(mem + [{"key": iref(2), "joined_at": t}], key=cde)), GROUP_ID_NOT_OF_FOUNDING),
        ("a founding with no nonce", _without(first, "nonce"), PAYLOAD_INVALID),
        ("a founding whose nonce is 16 bytes", dict(first, nonce=bytes(16)), PAYLOAD_INVALID),
        ("a later version that carries a nonce", dict(later, nonce=nonce), PAYLOAD_INVALID),
    ]


def group_id_checks():
    """(line, problems): every sample gives its expected answer; a planted rule that trusts the id as given must be
    caught by at least one sample."""
    S, bad = group_id_samples(), []
    for what, p, want in S:
        if group_id_rule(p) != want:
            bad.append(f"group id sample: {what}: {group_id_rule(p)} where {want} was expected")
    # The known answer three implementations agree on (this generator, the verifier's, the store's): CIRISVerify
    # group_id_v1.json at commit 9518060, sha256 c796353db656a32110fdb7e9c429c9f3e015f396d992751d13030723e49c1249.
    known = group_id("community", [iref(0), iref(1)], 1763078400000, bytes(range(32)))
    if known != "group-8ezU3QIqqrhTRYMAeKoBxdDL3mmvmAnKC1_wsrnJ3hI":
        bad.append(f"group id known answer: {known}")
    if group_id("family", [iref(1), iref(0)], 1763078400000, bytes(range(32))) != "group-ODjNYdkE6CL7viHGk4mFJRvuPtXGic_pxf-1iMrufE0":
        bad.append("group id known answer for a family differs")
    planted = lambda p: None if group_id_rule(p) == GROUP_ID_NOT_OF_FOUNDING else group_id_rule(p)
    if all(planted(p) == want for _, p, want in S):
        bad.append("deliberate break not caught: a rule that takes a group's id as given passed every sample")
    return (f"group:roster id: {sum(w is None for *_, w in S)} samples pass, "
            f"{sum(w is not None for *_, w in S)} refused, each with its token; the planted break is caught"), bad


RECEIPT_MISSING = "admission_receipt_missing"


def receipt_rule(receipts, trusted):
    """CC 2.7.11: admitted code runs only once a receipt from a Transparency Service the host trusts is held.
    receipts: [{"wellformed", "service", "alg", "verifies"}] held for a statement of the admission:unit row; a receipt that
    is not a well-formed COSE receipt is ignored, never a fault of the statement. trusted: {service: alg} from the host
    owner's own edges of the class transparency (one hop, at the host's self scope). None, or (RECEIPT_MISSING, detail)."""
    held = [r for r in receipts if r.get("wellformed")]
    if not held:
        return RECEIPT_MISSING, "none"
    if any(r["service"] in trusted and r["alg"] == trusted[r["service"]] and r["verifies"] for r in held):
        return None
    if any(r["service"] in trusted for r in held):
        return RECEIPT_MISSING, "unverifiable"
    return RECEIPT_MISSING, "untrusted_service"


def receipt_checks():
    """(line, problems): a trusted receipt lets the unit run; none, an empty array, a malformed one (ignored), one under
    another alg, an unverifiable one and one from a service the host does not trust each wait; a planted rule that
    admits any receipt must be caught."""
    trusted = {"ts-1": -7}
    ok = lambda s="ts-1", alg=-7, v=True: {"wellformed": True, "service": s, "alg": alg, "verifies": v}
    malformed = {"wellformed": False}
    cases = [("a receipt from a service the host trusts", [ok()], None),
             ("a malformed receipt beside a trusted one", [malformed, ok()], None),
             ("no receipts member", [], (RECEIPT_MISSING, "none")),
             ("an empty receipts array", [], (RECEIPT_MISSING, "none")),
             ("a receipt that is no COSE_Sign1, ignored", [malformed], (RECEIPT_MISSING, "none")),
             ("a trusted service's receipt under another algorithm", [ok(alg=-8)], (RECEIPT_MISSING, "unverifiable")),
             ("a trusted service's receipt that does not verify", [ok(v=False)], (RECEIPT_MISSING, "unverifiable")),
             ("a receipt from a service the host does not trust", [ok(s="ts-9")], (RECEIPT_MISSING, "untrusted_service"))]
    bad = [f"receipt rule: {w}: {receipt_rule(r, trusted)} where {want} was expected"
           for w, r, want in cases if receipt_rule(r, trusted) != want]
    planted = lambda r, t: None if r else (RECEIPT_MISSING, "none")
    if all(planted(r, trusted) == want for _, r, want in cases):
        bad.append("deliberate break not caught: a rule admitting any receipt passed every receipt sample")
    return (f"receipts before admitted code runs: {sum(w is None for *_, w in cases)} run, "
            f"{sum(w is not None for *_, w in cases)} wait ({RECEIPT_MISSING}), a malformed receipt ignored; the planted break is caught"), bad


def admission_checks():
    """(line, problems): every sample gives its expected answer; a planted rule that drops the lease's bound must be
    caught by at least one sample."""
    S, bad = admission_samples(), []
    for what, p, want in S:
        if admission_unit_rule(p) != want:
            bad.append(f"admission sample: {what}: {admission_unit_rule(p)} where {want} was expected")
    planted = lambda p: None if admission_unit_rule(p) == "admission_lease_out_of_window" else admission_unit_rule(p)
    if all(planted(p) == want for _, p, want in S):
        bad.append("deliberate break not caught: a lease with no bound passed every admission sample")
    return (f"admission:unit: {sum(w is None for *_, w in S)} samples pass, "
            f"{sum(w is not None for *_, w in S)} refused, each with its token; the planted break is caught"), bad


def family_payload_rule_checks():
    """(line, problems): each valid payload passes its prose rules; each deliberate break is refused with the token."""
    bad, P = [], family_payloads()
    for root, (fam, p) in P.items():
        if family_payload_rule(root, p, fam) is not None:
            bad.append(f"{root} sample breaks its prose rule")
    breaks = [
        ("membership-change", dict(P["membership-change"][1], dimension="membership:proposal:v1"), None),
        ("membership-change", _without(P["membership-change"][1], "joined_at"), None),
        ("membership-change", dict(P["membership-change"][1], refs={"also": {"cites": [_ref(3)]}}), None),
        ("custody-ack", _without(P["custody-ack"][1], "size"), None),
        ("key-grant", _without(P["key-grant"][1], "minter"), None),
        ("key-grant", dict(P["key-grant"][1], dimension="key_grant:content:v1"), None),
        ("delivery-ack", dict(P["delivery-ack"][1], stream_id="s2"), None),
        ("takedown-notice", dict(P["takedown-notice"][1], dimension="takedown_notice:steward_purge:v1",
                                 legal_basis="steward_purge"), None),
        ("group-roster", dict(P["group-roster"][1], version=1), None),
        ("membership-change", P["membership-change"][1], "cosign:.state"),
        ("canonical-rebind", dict(P["canonical-rebind"][1], refs={"also": {"cites": [_ref(9)]}}), None),
        ("deferral-response", dict(P["deferral-response"][1], reason_digest=[-16, bytes([7]) * 32]), None),
        ("build-manifest-row", dict(P["build-manifest-row"][1], refs={"also": {"cites": [_ref(9)]}}), None),
        ("build-manifest-row", dict(P["build-manifest-row"][1], evidence_refs=[[-16, bytes([8]) * 32]]), None),
        ("build-manifest-row", dict(P["build-manifest-row"][1], dimension="provenance:slsa:3:v1"), None),
        ("trust-confers", dict(P["trust-confers"][1], refs={"also": {"cites": [_ref(9)]}}), None),
        ("trust-confers", dict(P["trust-confers"][1], author=iref(0)), None),
        ("trust-confers", dict(P["trust-confers"][1], projects=["ciris-verify", "ciris-verify"]), None),
        ("trust-confers", dict(P["trust-confers"][1], dimension="trust:accepts:v1"), None),
        ("grant-acceptance", dict(P["grant-acceptance"][1], refs={"answers": _ref(15), "head": _ref(9)}), None),
        ("grant-acceptance", dict(P["grant-acceptance"][1], refs={"also": {"cites": [_ref(15)]}}), None),
        ("grant-withdrawal", dict(P["grant-withdrawal"][1], refs={"target": _ref(15)}), None),
        ("grant-withdrawal", dict(P["grant-withdrawal"][1], refs={"head": _ref(9)}), None),
    ]
    caught = 0
    for root, p, fam in breaks:
        if family_payload_rule(root, p, fam) == PAYLOAD_INVALID:
            caught += 1
        else:
            bad.append(f"deliberate break not caught: a {root} payload the prose refuses passed")
    return (f"family payload rules: {len(P)} samples pass; {caught} breaks refused {PAYLOAD_INVALID}, "
            f"a cosign state carrying a payload of its own among them"), bad


def family_cddl_checks(text, ftext):
    """(lines, problems): the family payload rules (FAMILY_CDDL, over the rules of CDDL) parse, and one valid payload of
    each validates and the broken ones are refused, with the `cddl` gem when present."""
    tool = find_tool("cddl")
    if not tool:
        return [f"cddl not installed: {os.path.relpath(FAMILY_CDDL, ROOT)} is not parsed here"], []
    lines, bad, ok_n, ref_n = [], [], 0, 0
    both = text + "\n" + ftext
    with tempfile.TemporaryDirectory() as d:
        src, f = os.path.join(d, "both.cddl"), os.path.join(d, "sample.cbor")
        open(src, "w", encoding="utf-8").write(both)
        r = subprocess.run([tool, src, "generate"], capture_output=True, text=True)
        if r.returncode:
            return lines, [f"{os.path.relpath(FAMILY_CDDL, ROOT)} does not parse with the schema: {(r.stderr or r.stdout).strip()[:300]}"]
        lines.append(f"{os.path.relpath(FAMILY_CDDL, ROOT)} parses with the schema")
        for root, what, ok, broken in family_payload_samples():
            rp = os.path.join(d, root + ".cddl")
            open(rp, "w", encoding="utf-8").write(f"sample-root = {root}\n" + both)
            open(f, "wb").write(ok)
            r = subprocess.run([tool, rp, "validate", f], capture_output=True, text=True)
            if r.returncode:
                bad.append(f"{what} sample does not validate: {(r.stderr or r.stdout).strip()[:300]}")
            else:
                ok_n += 1
            for why, blob in broken:
                open(f, "wb").write(blob)
                if subprocess.run([tool, rp, "validate", f], capture_output=True).returncode == 0:
                    bad.append(f"deliberate break not caught: {why} validated")
                else:
                    ref_n += 1
    lines.append(f"{ok_n} family payload samples validate, one per family rule; {ref_n} broken ones are refused")
    return lines, bad


# ---------------------------------------------------------------- the family payload schema, emitted from the table
FAMILY_OBJECTS = ("roster", "membership", "occurrence_revocation", "revocation", "takedown", "custody", "key_grant", "delivery_ack",
                  "occurrence", "amendment", "deferral", "deferral_request", "rebind", "admission", "trust_accepts",
                  "build_manifest", "grant", "grant_acceptance", "grant_withdrawal")
FAMILY_RULE_HEAD = {
    "group-roster": "group:roster: a counted row, with no author; sub is the group's identity reference.",
    "roster-member": "A member of a roster version: a closed map.",
    "membership-change": "membership:{stage}, the stages widening and removal: counted, with no author; sub is the member.",
    "occurrence-revocation": "identity:occurrence_revocation: authored by the revoker, or counted over a user self's roster at the head refs names.",
    "self-roster-refs": "The refs of a self-roster row (CC 3.3.6.4): the head it stands on, required; a closed map.",
    "eviction-refs": "The refs of an eviction (CC 2.6.1.7, CC 3.3.6.4): the head, and the proof of its signers, both required; a closed map.",
    "eviction-proof": "The proof an eviction carries (CC 2.6.1.7): the rows that resolve its voices; a closed map.",
    "entity-revocation": "revocation:{entity_type}:{reason}: authored by the revoker; sub is the revoked entity.",
    "takedown-notice": "takedown_notice:{basis}: authored, or counted on a steward purge; sub is the claimant.",
    "custody-ack": "custody:{kind}: the device's own report; author, iss and sub are the device.",
    "key-grant": "key_grant:{axis}: authored by the sealer; sub is the recipient.",
    "delivery-ack": "delivery_ack:{stream_id}: authored by the subscriber; author, iss and sub are the subscriber.",
    "trust-accepts": "trust:accepts (CC 4.4.3.34, CC 2.7.11): the reader's own edge; the members this form names, its further members are the store's.",
    "build-manifest-row": "provenance:build_manifest:{target} (CC 3.1.2.1): authored by the pipeline's key; one claim, type scores; the manifest blob is unsigned and cited by its digest.",
    "build-descriptor": "The descriptor of a manifest blob (CC 3.1.2.1, CC 5.3.2.11): a closed map of exactly four members.",
    "trust-confers": "trust:confers (CC 3.1.2.1, CC 4.2.1): a delegates_to row counted over the holders of the bundle in force, with no author; sub is the key the grant names.",
    "grant-acceptance": "membership:acceptance answering a grant (CC 3.1.2.1): authored by the owner of the key the grant names, at federation scope.",
    "grant-withdrawal": "The withdraws row that ends a grant (CC 4.2.1, CC 2.4.1.1): counted over the holders of the bundle in force, with no author.",
    "identity-occurrence": "identity:occurrence (CC 3.3.6): authored by a live roster key of the identity; the occurrence key's own statement is the second voice. Its binding members (the X-Wing keys, the opt-out) are those of transport-destination-binding.",
    "encryption-pubkeys": "The content-KEM keys of an occurrence (CC 3.3.6.1): a closed map.",
    "deferral-request": "deferral:request (CC 3.1.9.3, CC 4.3): authored by the deferring party; the request's further members are the store's.",
    "canonical-rebind": "transport:canonical_rebind (CC 3.1.3, CC 3.3.6.2): counted by a strict majority of the holders of the bundle in force; sub is the seated node.",
    "identity-amendment": "identity_amendment (CC 3.1.5): authored by the agent's occurrence key; sub is the agent's identity.",
    "deferral-response": "deferral:response:{outcome} (CC 3.1.9.3, CC 4.3): the members this form names; the response's further members are the store's.",
    "admission-unit": "admission:unit (CC 2.7.11, CC 3.1.3): authored by one person, or counted over refs.head with no author; one person's row naming an effect admits only on that person's own host; sub is the unit's digest as canonical:sha256:{hex}.",
}
FAMILY_CLOSED = {"roster-member", "encryption-pubkeys", "self-roster-refs", "eviction-refs", "eviction-proof", "build-descriptor"}            # every other family rule keeps a member it does not name (CC 2.1.1)
FAMILY_EXTRA = {"admission-unit": [
    "; The capabilities of CC 2.7.11: a closed set; the last five are effects.",
    'capability = "compute" / "read" / "net_send" / "submit" / "sign" / "store_write" / "actuate"'],
    "takedown-notice": [         # rules a member's type names, stated with the rule that uses them
    "; The legal bases of CC 3.3.2, by their wire strings: a closed set.",
    'legal-basis = "dmca512" / "dsa_article16" / "tvec_terrorist" / "ncmec_csam" / "gifct_cip"',
    '            / "community_standards" / "perceptual_hash_csam" / "osa_illegal_content"',
    '            / "avmsd_age_inappropriate" / "court_order" / "steward_purge"']}
FAMILY_PREAMBLE = """; CC 2.6.1.4: the payload rules of the families it names, over the rules of manifests/signed_object_v2.cddl and read
; with it. GENERATED by tools/build_cc_signed_object_v2.py from constitution/signed_object_v2.tsv; do not edit.
; The two files are one schema; signed_object_v2.cddl stays as the Internet-Draft's -01 carries it.
;
; Each rule is the payload of an ordinary row, so its members are members of the row's attestation-envelope, as a
; key record's are. Each carries the members its family names one to one and embeds no signed object. What a
; family's record carried as a co-signature is a further statement over the same payload, a counted voice
; (CC 2.6.1.9), never a member. A payload that breaks its family's rule is refused edition2_payload_invalid
; (CC 2.6.1.8 step 3). A member required only on one stage, axis or state is optional here and checked in prose.
; A cosign:{state} row has no payload of its own: each state is a statement over the event's own payload (CC 3.1.3)."""


def family_cddl_text(rows):
    """The text of FAMILY_CDDL, from the table's rows of the family objects, rule by rule in table order."""
    rules = {}
    for r in rows:
        if r["object"] in FAMILY_OBJECTS:
            rules.setdefault(r["rule"], []).append(r)
    out = [FAMILY_PREAMBLE]
    for rule, rs in rules.items():
        out += ["", "; " + FAMILY_RULE_HEAD.get(rule, rule), rule + " = {"]
        for r in rs:
            entry = f'  {"" if r["required_when"] == "always" else "? "}{r["member"]}: {r["type"]},'
            when = "" if r["required_when"] == "always" else f" ({r['required_when']})"
            out.append(f"{entry:<43} ; {r['note']}{when}")
        if rule not in FAMILY_CLOSED:
            out.append("  * tstr => ceg-value,")
        out.append("}")
        if rule in FAMILY_EXTRA:
            out += FAMILY_EXTRA[rule]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- decimal fractions in free-form bodies (CC 2.6.1.2)
NUMBER_UNREPRESENTABLE = "body_number_unrepresentable"
CBOR_INT = (-(1 << 64), (1 << 64) - 1)       # CBOR's integer range, uint or nint


def decimal_rule(v):
    """None for a body value whose every number is a plain integer or a normalised tag 4; "schema" for a second encoding
    (a float, a tag-4 value with a non-negative exponent or a mantissa divisible by 10), refused at step 3;
    body_number_unrepresentable for a mantissa outside CBOR's integer range."""
    if isinstance(v, float):
        return "schema"
    if isinstance(v, Tag) and v.tag == 4:
        if not (isinstance(v.value, list) and len(v.value) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in v.value)):
            return "schema"
        e, m = v.value
        if not CBOR_INT[0] <= m <= CBOR_INT[1]:
            return NUMBER_UNREPRESENTABLE
        if e >= 0 or m % 10 == 0:
            return "schema"
        return None
    if isinstance(v, list):
        return next((r for r in map(decimal_rule, v) if r), None)
    if isinstance(v, dict):
        return next((r for r in map(decimal_rule, v.values()) if r), None)
    return None


def decimal_checks():
    """(line, problems): 0.5 and -1.25 pass as tag 4, 2 as a plain integer; 2.0 as tag 4, 0.50 as [-2, 50], a float and a
    mantissa past 64 bits are refused."""
    bad = []
    cases = [("0.5 as 4([-1, 5])", {"detail": {"ratio": Tag(4, [-1, 5])}}, None),
             ("-1.25 as 4([-2, -125])", {"detail": [Tag(4, [-2, -125])]}, None),
             ("2 as a plain integer", {"detail": {"count": 2}}, None),
             ("2.0 as 4([-1, 20])", {"detail": {"count": Tag(4, [-1, 20])}}, "schema"),
             ("0.50 as 4([-2, 50]), not normalised", {"detail": {"ratio": Tag(4, [-2, 50])}}, "schema"),
             ("5 as 4([0, 5]), a non-negative exponent", {"detail": {"ratio": Tag(4, [0, 5])}}, "schema"),
             ("a float", {"detail": {"ratio": 0.5}}, "schema"),
             ("a mantissa of 2^64", {"detail": {"ratio": Tag(4, [-1, 1 << 64])}}, NUMBER_UNREPRESENTABLE),
             ("a mantissa of -2^64 - 1", {"detail": {"ratio": Tag(4, [-1, -(1 << 64) - 1])}}, NUMBER_UNREPRESENTABLE)]
    for why, body, want in cases:
        if decimal_rule(body) != want:
            bad.append(f"decimal rule: {why} gives {decimal_rule(body)}, the text gives {want}")
    for why, body, _ in cases[:3]:
        try:
            cde(body)
        except Exception as e:                        # the deterministic encoder must carry tag 4
            bad.append(f"decimal sample {why} does not encode: {e}")
    n_ok = sum(1 for c in cases if c[2] is None)
    return (f"decimal fractions in bodies: {n_ok} pass, {len(cases) - n_ok} refused (a second encoding at step 3, "
            f"or {NUMBER_UNREPRESENTABLE})"), bad


# ---------------------------------------------------------------- two rules that read a second row (CC 3.1.5, CC 3.3.6)
AMENDMENT_MISMATCH = "amendment_digest_mismatch"
OCCURRENCE_MIXED = "occurrence_mixes_person_and_machine"
PERSON, MACHINE = {"user", "accord_holder"}, {"node", "agent"}


def amendment_rule(amendment, response):
    """CC 3.1.5: an identity_amendment concludes nothing unless its amendment_digest equals the one the approving
    response carries; a response that carries none equals no digest. One token for both."""
    return None if response.get("amendment_digest") == amendment["amendment_digest"] else AMENDMENT_MISMATCH


def occurrence_rule(p, types):
    """CC 3.3.6: an occurrence never places a machine's key under a person's identity, or a person's under a machine's;
    device_class agent stands only under an agent's own identity. `types` maps an identity reference to the
    identity_type set its held key record states."""
    ident, occ = types.get(p["identity_key_id"], set()), types.get(p["occurrence_key_id"], set())
    if (ident & PERSON and occ & MACHINE) or (ident & MACHINE and occ & PERSON):
        return OCCURRENCE_MIXED
    if p.get("device_class") == "agent" and "agent" not in ident:
        return OCCURRENCE_MIXED
    return None


def second_row_checks():
    """(line, problems): the amendment's digest against its approval, and the occurrence's person/machine rule."""
    bad, P = [], family_payloads()
    am, rs = P["identity-amendment"][1], P["deferral-response"][1]
    cases = [("an amendment matching its approval", am, rs, None),
             ("an amendment whose digest differs from its approval's",
              dict(am, amendment_digest=[-16, bytes([8]) * 32]), rs, AMENDMENT_MISMATCH),
             ("an amendment citing an approval that carries no digest", am, _without(rs, "amendment_digest"), AMENDMENT_MISMATCH)]
    for why, a, r, want in cases:
        if amendment_rule(a, r) != want:
            bad.append(f"amendment rule: {why} gives {amendment_rule(a, r)}, the text gives {want}")
    occ = P["identity-occurrence"][1]
    user, phone, agent = iref(0), iref(3), iref(7)
    types = {user: {"user"}, phone: {"user"}, agent: {"agent"}, iref(8): {"agent"}}
    ocases = [("a person's phone under the person", occ, None),
              ("an agent's key under a user identity", dict(occ, occurrence_key_id=agent, device_class="agent"), OCCURRENCE_MIXED),
              ("device_class agent under a user identity", dict(occ, device_class="agent"), OCCURRENCE_MIXED),
              ("an agent's own key under the agent's identity",
               dict(occ, identity_key_id=iref(8), occurrence_key_id=agent, device_class="agent"), None)]
    for why, p, want in ocases:
        if occurrence_rule(p, types) != want:
            bad.append(f"occurrence rule: {why} gives {occurrence_rule(p, types)}, the text gives {want}")
    return (f"rules over a second row: {len(cases)} amendment cases ({AMENDMENT_MISMATCH} on a differing and on an absent digest), "
            f"{len(ocases)} occurrence cases ({OCCURRENCE_MIXED} on an agent key or device_class agent under a person)"), bad


# ---------------------------------------------------------------- a build pipeline's standing (CC 3.1.2.1, CC 4.2.1)
ATTEST, PIPELINE_SCOPE = "infra:attest", "infra:attest:provenance:build_manifest"
GRANT_OUT_OF_ROLE = "pipeline_grant_out_of_role"
PROJECT_NOT_GRANTED = "build_manifest_project_not_granted"
MANIFEST_EQUIVOCATION = "build_manifest_equivocation"
DESCRIPTOR_MISMATCH = "build_manifest_descriptor_mismatch"
BLOB_FORMAT = "ciris-binary-manifest/1"


def pipeline_grant_rule(p, sub_roles=()):
    """CC 4.2.1 bound (1), decided by the grant's payload alone: None, or its token. A grant is a pipeline's where it
    carries `projects` (no key record states a pipeline role); its scope holds the attest capability, whole or
    sub-scoped to the build-manifest family, and no other token. An unrecognised sub-scope is not widened to its
    parent (CC 4.5.5). `sub_roles` is the kind of the key named, which decides nothing."""
    if "projects" not in p:
        return None
    return None if set(p.get("scope", [])) <= {ATTEST, PIPELINE_SCOPE} else GRANT_OUT_OF_ROLE


def build_manifest_rule(row, grant):
    """CC 3.1.2.1, over two rows: a build-manifest row and the grant its pipeline stands on. None, or the token. A grant
    with no `projects` member confers a build manifest for no project."""
    return None if row["build"]["project"] in grant.get("projects", []) else PROJECT_NOT_GRANTED


def build_target(row):
    """The target of a build-manifest row: its dimension less the family's two literals and the version segment."""
    return ":".join(row["dimension"].split(":")[2:-1])


def descriptor_rule(row, blob):
    """CC 3.1.2.1, over a row and the blob it cites (`blob` is the map; its bytes are its deterministic encoding): None,
    or the one token for any disagreement of length, digest, project, version or target."""
    raw, b = cde(blob), row["build"]
    if b["manifest_size"] != len(raw) or b["manifest_hash"] != [-16, hashlib.sha256(raw).digest()]:
        return DESCRIPTOR_MISMATCH
    if (b["project"], b["version"], build_target(row)) != (blob.get("project"), blob.get("version"), blob.get("target")):
        return DESCRIPTOR_MISMATCH
    return None


def equivocation_rule(a, b, supersedes=False):
    """CC 3.1.2.1, over two build-manifest rows: None, or the token where one pipeline states two descriptors for one
    project, version and target and neither row supersedes the other."""
    key = lambda r: (r["author"], r["build"]["project"], r["build"]["version"], build_target(r))
    return MANIFEST_EQUIVOCATION if key(a) == key(b) and a["build"] != b["build"] and not supersedes else None


def functions_root(functions):
    """CC 3.1.2.1: the Merkle root over a function table. Leaves in the byte order of the function names, each the
    deterministic encoding of {name, offset, size, hash} under the leaf prefix 0x00; the last leaf repeated to the next
    power of two; a parent is SHA-256 over 0x01, left, right."""
    level = [hashlib.sha256(b"\x00" + cde(f)).digest() for f in sorted(functions, key=lambda f: f["name"].encode("utf-8"))]
    while len(level) & (len(level) - 1):
        level.append(level[-1])
    while len(level) > 1:
        level = [hashlib.sha256(b"\x01" + level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0]


def build_blob(row_target="x86_64-unknown-linux-gnu", **change):
    """A schema-sample manifest blob: exactly the members CC 3.1.2.1 lists, its digests plain 32-byte strings."""
    fns = [{"name": n, "offset": 4096 * (i + 1), "size": 512, "hash": bytes([i + 1]) * 32} for i, n in enumerate(("main", "init", "verify"))]
    blob = {"format": BLOB_FORMAT, "project": "ciris-verify", "version": "1.2.3", "target": row_target,
            "binary_hash": bytes([9]) * 32, "functions_root": functions_root(fns), "functions": fns, "tool": "ciris-manifest-tool 1.0.0"}
    return dict(blob, **change)


def row_for(blob, **change):
    """The build-manifest sample row, its descriptor that of `blob`."""
    row, raw = family_payloads()["build-manifest-row"][1], cde(blob)
    dig = [-16, hashlib.sha256(raw).digest()]
    row = dict(row, evidence_refs=[dig], build={"project": blob["project"], "version": blob["version"],
                                                "manifest_hash": dig, "manifest_size": len(raw)})
    return dict(row, **change)


def build_manifest_checks():
    """(line, problems): the pipeline's grant, the manifest against its grant, the descriptor against its blob, two
    manifests of one build, and the function table's root; every sample gives the answer the text gives, and a planted
    fault of each rule must be caught by at least one sample."""
    bad, P = [], family_payloads()
    grant, blob = P["trust-confers"][1], build_blob()
    row = row_for(blob)
    plain = _without(grant, "projects")
    gcases = [("a pipeline's grant under the sub-scope", grant, (), None),
              ("a pipeline's grant under the bare capability", dict(grant, scope=[ATTEST]), (), None),
              ("a pipeline's grant that also carries infra:serve", dict(grant, scope=sorted([PIPELINE_SCOPE, "infra:serve"], key=cde)), (), GRANT_OUT_OF_ROLE),
              ("a pipeline's grant under another family's sub-scope", dict(grant, scope=["infra:attest:licensure:X"]), (), GRANT_OUT_OF_ROLE),
              ("a pipeline's grant under a narrower sub-scope nobody registered", dict(grant, scope=[PIPELINE_SCOPE + ":x86"]), (), GRANT_OUT_OF_ROLE),
              ("a grant of infra:serve to a key that is no pipeline", dict(plain, scope=["infra:serve"]), ("node",), None),
              ("a grant of infra:serve with no projects, which is no pipeline's grant", dict(plain, scope=["infra:serve"]), ("agent",), None)]
    for why, g, roles, want in gcases:
        if pipeline_grant_rule(g, roles) != want:
            bad.append(f"pipeline grant: {why} gives {pipeline_grant_rule(g, roles)}, the text gives {want}")
    prefix = lambda g, roles=(): None if all(s.startswith(ATTEST) for s in g.get("scope", [])) else pipeline_grant_rule(g, roles)
    if all(prefix(g, r) == want for _, g, r, want in gcases):
        bad.append("deliberate break not caught: a prefix test on a pipeline's scope passed every grant sample")
    pcases = [("a manifest of a listed project", row, grant, None),
              ("a manifest of a project the grant does not list", dict(row, build=dict(row["build"], project="ciris-node")), grant, PROJECT_NOT_GRANTED),
              ("a manifest under a grant with no projects member", row, plain, PROJECT_NOT_GRANTED)]
    for why, r, g, want in pcases:
        if build_manifest_rule(r, g) != want:
            bad.append(f"build manifest and grant: {why} gives {build_manifest_rule(r, g)}, the text gives {want}")
    lax = lambda r, g: None if "projects" not in g else build_manifest_rule(r, g)
    if all(lax(r, g) == want for _, r, g, want in pcases):
        bad.append("deliberate break not caught: a rule reading an absent projects member as every project passed every sample")
    dcases = [("a row whose descriptor is its blob's", row, blob, None),
              ("a size one byte short", dict(row, build=dict(row["build"], manifest_size=row["build"]["manifest_size"] - 1)), blob, DESCRIPTOR_MISMATCH),
              ("a digest of another blob", dict(row, build=dict(row["build"], manifest_hash=[-16, bytes([8]) * 32])), blob, DESCRIPTOR_MISMATCH),
              ("a project the blob does not state", row_for(blob, build=dict(row["build"], project="ciris-agent")), blob, DESCRIPTOR_MISMATCH),
              ("a version the blob does not state", row_for(blob, build=dict(row["build"], version="1.2.4")), blob, DESCRIPTOR_MISMATCH),
              ("a row on another target's family", dict(row, dimension="provenance:build_manifest:aarch64-apple-darwin:v1"), blob, DESCRIPTOR_MISMATCH)]
    for why, r, b, want in dcases:
        if descriptor_rule(r, b) != want:
            bad.append(f"descriptor: {why} gives {descriptor_rule(r, b)}, the text gives {want}")
    bytes_only = lambda r, b: None if (r["build"]["manifest_size"], r["build"]["manifest_hash"]) == (len(cde(b)), [-16, hashlib.sha256(cde(b)).digest()]) else DESCRIPTOR_MISMATCH
    if all(bytes_only(r, b) == want for _, r, b, want in dcases):
        bad.append("deliberate break not caught: a rule comparing size and digest alone passed every descriptor sample")
    other = row_for(build_blob(binary_hash=bytes([10]) * 32))
    ecases = [("the same row twice", row, row, False, None),
              ("two descriptors for one project, version and target", row, other, False, MANIFEST_EQUIVOCATION),
              ("a rebuild that supersedes the first", row, other, True, None),
              ("another pipeline's manifest of the same build", row, dict(other, author=iref(6)), False, None),
              ("the next version", row, row_for(build_blob(version="1.2.4")), False, None),
              ("another target", row, row_for(build_blob("aarch64-apple-darwin"), dimension="provenance:build_manifest:aarch64-apple-darwin:v1"), False, None)]
    for why, a, b, sup, want in ecases:
        if equivocation_rule(a, b, sup) != want:
            bad.append(f"equivocation: {why} gives {equivocation_rule(a, b, sup)}, the text gives {want}")
    if all(want is None for *_, want in ecases):
        bad.append("deliberate break not caught: a rule that never reports an equivocation passed every sample")
    fns = blob["functions"]
    if functions_root(fns) != functions_root(list(reversed(fns))):
        bad.append("function table: the root depends on the order the table is listed in")
    last = max(fns, key=lambda f: f["name"].encode())
    four = [hashlib.sha256(b"\x00" + cde(f)).digest() for f in sorted(fns, key=lambda f: f["name"].encode())] + [hashlib.sha256(b"\x00" + cde(last)).digest()]
    want_root = hashlib.sha256(b"\x01" + hashlib.sha256(b"\x01" + four[0] + four[1]).digest() + hashlib.sha256(b"\x01" + four[2] + four[3]).digest()).digest()
    if functions_root(fns) != want_root:
        bad.append("function table: three leaves are not padded by repeating the last to four")
    if functions_root(fns) == functions_root([dict(f, size=f["size"] + 1) if f is last else f for f in fns]):
        bad.append("deliberate break not caught: a function's changed size leaves the root unchanged")
    if set(blob) != {"format", "project", "version", "target", "binary_hash", "functions_root", "functions", "tool"}:
        bad.append("the sample blob's members are not those the text lists")
    import cc_namespace_match as NM
    got = NM.match_family(NM.load_manifest(), row["dimension"])
    if not got or got[0] != "provenance:build_manifest:{target}" or got[2] is not None:
        bad.append(f"sample dimension {row['dimension']} does not match its family: {got}")
    return (f"a build pipeline's standing: {len(gcases)} grants ({GRANT_OUT_OF_ROLE}), {len(pcases)} manifests against a grant "
            f"({PROJECT_NOT_GRANTED}), {len(dcases)} descriptors against a blob ({DESCRIPTOR_MISMATCH}), {len(ecases)} pairs "
            f"({MANIFEST_EQUIVOCATION}), the function table's root over three leaves padded to four; the planted faults are caught"), bad


# ---------------------------------------------------------------- the bundle's prose rules, as a reference reader
GENESIS_TYP = "ceg-genesis-bundle/2"


def object_id(typ, payload_bytes):
    return [-16, hashlib.sha256(cde(["CEG-object/2", typ, None, payload_bytes])).digest()]


def recovery_commitment(key):
    """CC 3.2 T3: [-16, SHA-256(CDE(["CEG-recovery/2", keys]))] over one composite key."""
    return [-16, hashlib.sha256(cde(["CEG-recovery/2", [key]])).digest()]


def is_set(xs):
    enc = [cde(x) for x in xs]
    return enc == sorted(set(enc)) and len(enc) == len(set(enc))


def read_bundle(payload, statements, rows, anchor, prev=None):
    """CC 2.6.1.11 over one bundle, structure only (no signature is computed here), in the order of verification.
    `statements` are the voices as (voice, iat), each taken as verified: a holder's identity reference, or
    ("recovery", iss, key) for a recovery key's statement (iss the holder, key the recovery key). `rows` maps a cited row id to (family, author, extra).
    `prev` is None for a first bundle or a prev not held, "not_valid" for a prev held and not Valid, or the
    predecessor's Valid placement. Returns ("Valid", placement), ("Invalid", detail) with the token
    genesis_bundle_malformed, ("Waiting", ids) or ("nothing", token)."""
    P = payload
    # 1. each statement alone: one whose iat disagrees is refused alone, and the rest are read
    voices = [v for v, iat in statements if iat == P["asserted_at"] // 1000]
    # 2. the payload against its rule
    H, S = set(P["holders"]), set(P["serve_nodes"])
    W = set(P["charter"].get("transparency_services", []))
    later = "prev" in P["refs"]
    if later != (P["version"] != 1):
        return "Invalid", "version_prev_mismatch"
    for xs in (P["holders"], P["serve_nodes"], P["charter"]["scope"], P["charter"].get("transparency_services", []),
               P["refs"]["also"]["cites"]):
        if not is_set(xs):
            return "Invalid", "federation_set_semantics_unsorted"
    if H & S or H & W or S & W:
        return "Invalid", "holders_seats_overlap"
    if set(P["charter"]["recovery_commitments"]) != H:
        return "Invalid", "recovery_commitments_not_holders"
    if not {"infra:attest", "infra:serve"} <= set(P["charter"]["scope"]):
        return "Invalid", "scope_missing_infra"
    # 3. the anchor, or prev
    if later:
        if prev is None:
            return "Waiting", ["prev"]
        if prev == "not_valid":
            return "nothing", "genesis_bundle_prev_not_valid"
        if P["version"] != prev["version"] + 1:
            return "Invalid", "version_prev_mismatch"
        if P["family_key_id"] != prev["family_key_id"]:
            return "Invalid", "family_key_id_changed"
    else:
        kind, value = anchor
        if (kind == "thumbprints" and set(value) != H) or (kind == "object_id" and value != object_id(GENESIS_TYP, cde(P))):
            return "nothing", "genesis_bundle_not_anchored"
    # 4. the named rows
    rvoices = [v for v in voices if not isinstance(v, str)]          # ("recovery", iss, recovery key)
    cites = P["refs"]["also"]["cites"]
    missing = [c for c in cites if c[1][1] not in rows]
    if missing:
        return "Waiting", missing
    place = {}
    for c in cites:
        fam, author, extra = rows[c[1][1]]
        if (fam == "key:record" and later and ("recovery_key", author) not in place
                and any(v[1] == author and v[2] == extra.get("key") for v in rvoices)):
            slot = ("recovery_key", author)          # the recovery key's own record, named for self-containment
        elif fam == "key:record" and author in H | S | W:
            slot = ("record", author)
        elif fam == "identity:occurrence" and author in S:
            slot = ("binding", author)
        else:
            return "nothing", "genesis_bundle_row_unplaced"
        if slot in place:
            return "nothing", "genesis_bundle_row_unplaced"
        place[slot] = (c, extra)
    for party in H | S | W:
        if ("record", party) not in place:
            return "nothing", "genesis_bundle_row_unplaced"
    for seat in S:
        if ("binding", seat) not in place:
            return "nothing", "genesis_bundle_row_unplaced"
        rec_ref, rec = place[("record", seat)]
        _, binding = place[("binding", seat)]
        if rec.get("valid_until", 0) <= P["asserted_at"] or binding.get("cites") != rec_ref or binding.get("head") != rec_ref:
            return "nothing", "genesis_bundle_row_invalid"
        if (binding.get("identity_key_id"), binding.get("occurrence_key_id"), binding.get("device_class")) != (seat, seat, "server"):
            return "nothing", "genesis_bundle_row_invalid"     # the seat's binding is an identity:occurrence of the seat, a server
    keys = {h: place[("record", h)][1].get("key") for h in H}
    coms = dict(P["charter"]["recovery_commitments"])
    spent = set(prev["spent"]) if later else set()
    ever = set(prev["ever"]) if later else set()
    recovery = later and len(voices) == 1 and len(rvoices) == 1
    if recovery:
        # the end of step 4: a recovery's Invalid rules, once its records are placed
        PH, h, rk = set(prev["holders"]), rvoices[0][1], rvoices[0][2]
        changed = {x for x in H | PH if keys.get(x) != prev["keys"].get(x) or coms.get(x) != prev["coms"].get(x)}
        if (changed - {h} or H != PH or S != set(prev["seats"])
                or {k: v for k, v in P["charter"].items() if k != "recovery_commitments"} != prev["charter_rest"]):
            return "Invalid", "recovery_changes_other_seat"
        if keys.get(h) == rk or cde(recovery_commitment(keys.get(h))) in ever:
            return "Invalid", "recovery_key_is_signing_key"
        if keys.get(h) == prev["keys"].get(h):
            return "Invalid", "recovery_reuses_signing_key"
    # then, for every later bundle: no holder re-seated at a key its lineage retired or its in-force recovery key.
    # It reads the cited records and the predecessor only, never the statements held.
    retired = {x: set(v) for x, v in prev.get("retired", {}).items()} if later else {}
    moved = set()
    if later:
        for x in H & set(prev["holders"]):
            if keys.get(x) != prev["keys"].get(x):
                moved.add(x)
                if (cde(keys.get(x)) in retired.get(x, set())
                        or recovery_commitment(keys.get(x)) == prev["coms"].get(x)):
                    return "Invalid", "holder_key_retired"
    # 5. the custody gate
    for x in H:
        ev = place[("record", x)][1]
        if not ev.get("chain_verifies") or ev.get("pq_custody") != "removable_offline":
            return "nothing", "genesis_holder_custody"
    # 6. the count, or a recovery's one statement
    if not later:
        if not H <= {v for v in voices if isinstance(v, str)}:
            return "nothing", "genesis_bundle_count_unmet"
    else:
        PH = set(prev["holders"])
        if any(cde(x) in spent for x in coms.values()):
            return "nothing", "genesis_bundle_count_unmet:recovery_commitment_spent"   # never returns
        if recovery:
            if cde(recovery_commitment(rk)) in spent or coms[h] == prev["coms"].get(h):
                return "nothing", "genesis_bundle_count_unmet:recovery_commitment_spent"
            if ("recovery_key", h) not in place or prev["coms"].get(h) != recovery_commitment(rk):
                return "nothing", "genesis_bundle_count_unmet:recovery_commitment_mismatch"
            spent.add(cde(prev["coms"][h]))
            retired.setdefault(h, set()).add(cde(rk))
        else:
            yes = {v for v in voices if isinstance(v, str)}
            if not moved <= yes:              # a routine rotation: the holder's own counted voice, current key
                return "nothing", "genesis_bundle_row_invalid"
            added = H - PH
            recom = {x for x in H & PH if coms[x] != prev["coms"][x]}
            if len(yes & PH) * 2 <= len(PH) or not (added | recom) <= yes:
                return "nothing", "genesis_bundle_count_unmet"
    ever |= {cde(x) for x in coms.values()}
    for x in moved:
        retired.setdefault(x, set()).add(cde(prev["keys"][x]))
    return "Valid", {"retired": retired, "holders": sorted(H), "seats": {s: place[("binding", s)][1]["xwing"] for s in sorted(S)},
                     "version": P["version"], "family_key_id": P["family_key_id"], "keys": keys, "coms": coms,
                     "spent": spent, "ever": ever,
                     "charter_rest": {k: v for k, v in P["charter"].items() if k != "recovery_commitments"}}


def reader_samples():
    """The reference reader over a valid first bundle, later bundles on it, and one break per rule it states; each
    break must give its own answer, never Valid."""
    H = [iref(0), iref(1), iref(2)]
    S = [iref(3), iref(4)]
    D = iref(5)
    key = lambda n: {1: 7, 3: -70100, -1: bytes([n]) * 1984}
    rid = lambda n: [2, [-16, bytes([n]) * 32]]
    rows = {}
    for n, h in enumerate(H + [D]):
        rows[bytes([0x10 + n]) * 32] = ("key:record", h, {"chain_verifies": True, "pq_custody": "removable_offline", "key": key(n)})
    for n, s_ in enumerate(S):
        rows[bytes([0x20 + n]) * 32] = ("key:record", s_, {"valid_until": 1794614400000})
        rows[bytes([0x30 + n]) * 32] = ("identity:occurrence", s_, {"xwing": ("transit-%d" % n, "onion-%d" % n),
                                                                     "cites": rid(0x20 + n), "head": rid(0x20 + n), "identity_key_id": s_,
                                                                     "occurrence_key_id": s_, "device_class": "server"})
    # A's rotated record (key 7) and the record of a key that is A's recovery key (key 50)
    rows[bytes([0x17]) * 32] = ("key:record", H[0], {"chain_verifies": True, "pq_custody": "removable_offline", "key": key(7)})
    rows[bytes([0x18]) * 32] = ("key:record", H[0], {"chain_verifies": True, "pq_custody": "removable_offline", "key": key(50)})
    rows[bytes([0x1A]) * 32] = ("key:record", H[0], {"chain_verifies": True, "pq_custody": "removable_offline", "key": key(50)})
    base = [0x10, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31]
    cites_of = lambda ids: sorted((rid(n) for n in ids), key=cde)
    rc = lambda n: recovery_commitment(key(n))
    coms0 = {H[0]: rc(50), H[1]: rc(51), H[2]: rc(52)}

    def payload(cites=base, coms=coms0, holders=H, **ch):
        p = {"refs": {"also": {"cites": cites_of(cites)}}, "version": 1, "asserted_at": 1763078400000,
             "family_key_id": "humanity-accord", "holders": sorted(holders, key=cde), "serve_nodes": S,
             "charter": {"recovery_commitments": dict(coms), "scope": ["infra:serve", "infra:attest"]}}
        p.update(ch)
        return p
    voices = [(h, 1763078400) for h in H]
    anchor = ("thumbprints", H)
    bad_custody = dict(rows)
    bad_custody[bytes([0x10]) * 32] = ("key:record", H[0], {"chain_verifies": True, "pq_custody": "software_wrapped"})
    no_chain = dict(rows)
    no_chain[bytes([0x11]) * 32] = ("key:record", H[1], {"chain_verifies": False, "pq_custody": "removable_offline"})
    short_seat = dict(rows)
    short_seat[bytes([0x20]) * 32] = ("key:record", S[0], {"valid_until": 1763078400000})
    good = payload()
    g_ans, g_place = read_bundle(good, voices, rows, anchor)
    gid = object_id(GENESIS_TYP, cde(good))
    later = lambda cites=base, coms=coms0, holders=H, **ch: payload(cites, coms, holders, version=2,
                                                                     refs={"prev": gid, "also": {"cites": cites_of(cites)}}, **ch)
    addD = later(base + [0x13], {**coms0, D: rc(53)}, H + [D])
    REC = [0x17, 0x18, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31]     # A's new record and its recovery key's record
    rec = later(REC, {**coms0, H[0]: rc(60)})
    rec_v = [(("recovery", H[0], key(50)), 1763078400)]
    breaks = [
        ("a missing holder signature", (good, voices[:2], rows, anchor), ("nothing", "genesis_bundle_count_unmet")),
        ("an iat not floor(asserted_at / 1000), refused alone", (good, voices[:2] + [(H[2], 1763078401)], rows, anchor),
         ("nothing", "genesis_bundle_count_unmet")),
        ("a seat whose binding is not in cites", (payload(cites=[n for n in base if n != 0x31]), voices, rows, anchor),
         ("nothing", "genesis_bundle_row_unplaced")),
        ("holders and serve_nodes overlapping", (payload(serve_nodes=[H[0], S[0]]), voices, rows, anchor), ("Invalid", "holders_seats_overlap")),
        ("a holder not removable_offline", (good, voices, bad_custody, anchor), ("nothing", "genesis_holder_custody")),
        ("a holder whose chain does not verify", (good, voices, no_chain, anchor), ("nothing", "genesis_holder_custody")),
        ("a holder set unlike the anchor", (good, voices, rows, ("thumbprints", H[:2] + [iref(6)])), ("nothing", "genesis_bundle_not_anchored")),
        ("an object id unlike the anchor", (good, voices, rows, ("object_id", [-16, bytes(32)])), ("nothing", "genesis_bundle_not_anchored")),
        ("a cited row not held", (good, voices, {k: v for k, v in rows.items() if k != bytes([0x20]) * 32}, anchor), ("Waiting", None)),
        ("a version 2 with no prev", (payload(version=2), voices, rows, anchor), ("Invalid", "version_prev_mismatch")),
        ("a scope out of set order", (payload(charter={"recovery_commitments": coms0, "scope": ["infra:attest", "infra:serve"]}),
                                      voices, rows, anchor), ("Invalid", "federation_set_semantics_unsorted")),
        ("a seat whose record ends before the bundle", (good, voices, short_seat, anchor), ("nothing", "genesis_bundle_row_invalid")),
        ("a seat whose binding does not name its record",
         (good, voices, {**rows, bytes([0x30]) * 32: ("identity:occurrence", S[0], {"xwing": ("transit-0", "onion-0"), "identity_key_id": S[0],
                                                                                    "occurrence_key_id": S[0], "device_class": "server"})}, anchor),
         ("nothing", "genesis_bundle_row_invalid")),
        ("a seat binding with no identity_key_id",
         (good, voices, {**rows, bytes([0x30]) * 32: ("identity:occurrence", S[0], {k: v for k, v in rows[bytes([0x30]) * 32][2].items()
                                                                                    if k != "identity_key_id"})}, anchor),
         ("nothing", "genesis_bundle_row_invalid")),
        ("a seat binding without refs.head",
         (good, voices, {**rows, bytes([0x30]) * 32: ("identity:occurrence", S[0], {k: v for k, v in rows[bytes([0x30]) * 32][2].items()
                                                                                    if k != "head"})}, anchor),
         ("nothing", "genesis_bundle_row_invalid")),
        ("a seat binding of device_class phone",
         (good, voices, {**rows, bytes([0x30]) * 32: ("identity:occurrence", S[0], dict(rows[bytes([0x30]) * 32][2], device_class="phone"))}, anchor),
         ("nothing", "genesis_bundle_row_invalid")),
        # later bundles
        ("a later bundle whose prev is not held", (addD, voices + [(D, 1763078400)], rows, anchor, None), ("Waiting", None)),
        ("a later bundle whose prev is not Valid", (addD, voices + [(D, 1763078400)], rows, anchor, "not_valid"),
         ("nothing", "genesis_bundle_prev_not_valid")),
        ("a later bundle changing family_key_id", (dict(addD, family_key_id="another-accord"), voices + [(D, 1763078400)], rows, anchor, g_place),
         ("Invalid", "family_key_id_changed")),
        ("an added holder who did not sign", (addD, voices, rows, anchor, g_place), ("nothing", "genesis_bundle_count_unmet")),
        ("a change on a minority", (addD, voices[:1] + [(D, 1763078400)], rows, anchor, g_place), ("nothing", "genesis_bundle_count_unmet")),
        ("a recovery under the holder's signing key", (later([0x17, 0x10, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31], {**coms0, H[0]: rc(60)}),
                                                       [(("recovery", H[0], key(0)), 1763078400)], rows, anchor, g_place),
         ("nothing", "genesis_bundle_count_unmet:recovery_commitment_mismatch")),
        ("a recovery keeping its signing key", (later([0x10, 0x18, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31], {**coms0, H[0]: rc(60)}),
                                                rec_v, rows, anchor, g_place), ("Invalid", "recovery_reuses_signing_key")),
        ("a recovery that also re-commits another holder", (later(REC, {**coms0, H[0]: rc(60), H[1]: rc(61)}),
                                                             rec_v, rows, anchor, g_place), ("Invalid", "recovery_changes_other_seat")),
        ("a recovery seating its own recovery key", (later([0x18, 0x1A, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31], {**coms0, H[0]: rc(60)}),
                                                     rec_v, rows, anchor, g_place), ("Invalid", "recovery_key_is_signing_key")),
        ("a recovery keeping the spent commitment", (later(REC, coms0), rec_v, rows, anchor, g_place),
         ("nothing", "genesis_bundle_count_unmet:recovery_commitment_spent")),
        ("a recovery whose recovery key's record is not named", (later([0x17, 0x11, 0x12, 0x20, 0x21, 0x30, 0x31], {**coms0, H[0]: rc(60)}),
                                                                 rec_v, rows, anchor, g_place),
         ("nothing", "genesis_bundle_count_unmet:recovery_commitment_mismatch")),
    ]
    later_ok = [("a roster change adding a holder, signed by a majority and the added holder",
                 (addD, voices[:2] + [(D, 1763078400)], rows, anchor, g_place)),
                ("a recovery by the recovery key alone", (rec, rec_v, rows, anchor, g_place))]
    return (good, voices, rows, anchor), (cde(good), gid), breaks, later_ok


# ---------------------------------------------------------------- step 8: the key of iss (CC 2.6.1.7)
IREF = "urn:ietf:params:oauth:ckt:sha-256:"


def thumb(n):
    """A sample key's 32-byte thumbprint."""
    return hashlib.sha256(b"sample key %d" % n).digest()


def iref_of(t):
    """The identity reference of the key with thumbprint t (CC 2.6.1.1): the thumbprint URI, base64url, no padding."""
    import base64
    return IREF + base64.urlsafe_b64encode(t).decode().rstrip("=")


KEY_BREAK = set()   # deliberate breaks of the reader, switched on by key_iss_checks


def read_kid_of_iss(kid, iss, records, lineage=None, occs=()):
    """Step 8 of CC 2.6.1.8 for one statement: ("Valid", None), ("Waiting", row id) or ("Invalid", "kid_not_of_iss"),
    with the detail "kid_not_of_iss:rotation_after_revocation" where a link fails only by its predecessor's own
    revoked_after. records: row id -> {"key", "iss", "target" (the predecessor's record, a rotation), "supersedes" (the
    key's own earlier record, a renewal), "voices" (the keys that signed it), "in_span" (the predecessor's statement
    is made inside the predecessor's record), "after_revocation" (it is made at or after the predecessor's own
    revoked_after, CC 2.4.1.1)}. lineage: None (no accord lineage held), ("not held", object id) where the bundle in
    force is not held, or ("held", seats, counted) for the bundle in force. occs: the identity:occurrence rows of iss the
    reader holds, each {"id", "okey", "own_voice", "admitted", "signer_of_iss", "covers" (the statement's instant,
    half-open), "evicted", "machine_under_person"}. A rotation record missing a voice waits on that record ("voice:"),
    since a counted row gains voices without changing its row id. With no record of kid held, step 6 has already
    answered Waiting."""
    if iref_of(kid) == iss or "any_key" in KEY_BREAK:
        return "Valid", None                          # (a) kid is the thumbprint inside iss
    if "genesis_only" in KEY_BREAK:
        return "Invalid", "kid_not_of_iss"
    waiting = revoked = None
    if lineage and lineage[0] == "held":              # (c) the bundle in force seats kid for iss
        if (lineage[2] or "uncounted_bundle" in KEY_BREAK) and lineage[1].get(iss) == kid:
            return "Valid", None
    elif lineage:
        waiting = lineage[1]                          # the bundle in force is not held: Waiting on it
    for o in occs if "skip_occurrence" not in KEY_BREAK else ():   # (d) a live occurrence of iss binds kid
        if o["okey"] != kid:
            continue
        if not o["own_voice"]:
            waiting = waiting or "voice:" + o["id"]   # the bound key's own voice is not held: Waiting on it
        elif (o["admitted"] and (o["signer_of_iss"] or "occ_any_signer" in KEY_BREAK) and o["covers"]
              and not o["evicted"] and (not o["machine_under_person"] or "occ_agent_as_person" in KEY_BREAK)):
            return "Valid", None
    mine = [rid for rid, r in records.items() if r["key"] == kid]
    if not mine:
        return "Waiting", waiting or kid              # step 6: the key record is not held
    for rid in mine:
        r, seen = records[rid], set()
        while True:
            if iref_of(r["key"]) == iss:
                return "Valid", None                  # (b) the chain reached iss's genesis key's record
            if (r["iss"] != iss and "any_identity" not in KEY_BREAK) or rid in seen:
                break                                 # a record of another identity
            seen.add(rid)
            if r.get("supersedes"):                   # a renewal: the chain does not move
                nxt = r["supersedes"]
            elif r.get("target"):                     # a rotation: the predecessor's record, and its statement
                nxt = r["target"]
            else:
                if "any_identity" in KEY_BREAK:
                    return "Valid", None
                break                                 # a first record of a key that is not iss's genesis key
            if nxt not in records:
                waiting = waiting or nxt              # a link not held: Waiting on that row
                break
            p = records[nxt]
            if r.get("target") and not r.get("in_span", True):
                break                                 # the predecessor's statement lies outside its record: fixed by bytes
            if r.get("target") and ((p["key"] not in r["voices"] and "no_predecessor_statement" not in KEY_BREAK)
                                    or r["key"] not in r["voices"]):
                waiting = waiting or "voice:" + rid   # a voice is not held: the record waits for it
                break
            if r.get("target") and not handed_on(rid, records):
                break                                 # a rival rotation of the same predecessor: nothing is handed on
            if r.get("target") and r.get("after_revocation"):
                revoked = True                        # made at or after the predecessor's own revoked_after
                break
            if r.get("supersedes") and p["key"] != r["key"]:
                break
            rid, r = nxt, p
    if waiting:
        return "Waiting", waiting
    return "Invalid", "kid_not_of_iss:rotation_after_revocation" if revoked else "kid_not_of_iss"


def handed_on(rid, records):
    """A rotation hands on only where the frontier of its predecessor's rotations names its key alone (CC 2.4.1.1).
    A rival counts only where it names a record of the predecessor covering its own instant ("in_span") and carries
    the predecessor's statement; a rotation that "names" others has them in its past."""
    if "rivals_ignored" in KEY_BREAK:
        return True
    old = records[records[rid]["target"]]["key"]
    rots = {i: x for i, x in records.items() if x.get("target") in records and records[x["target"]]["key"] == old
            and (old in x["voices"] or "no_predecessor_statement" in KEY_BREAK) and (x.get("in_span", True) or "uncovered_rival" in KEY_BREAK)}
    named = {n for x in rots.values() for n in x.get("names", ())}
    return {x["key"] for i, x in rots.items() if i not in named} == {records[rid]["key"]}


def key_iss_samples():
    """(name, kid, iss, records, answer, lineage, occurrences): the samples of step 8, with the answer the text gives."""
    gA, kB, kC, gE = thumb(1), thumb(2), thumb(3), thumb(9)
    A = iref_of(gA)
    pA = {"key": gA, "iss": A, "voices": {gA}}
    qB = {"key": kB, "iss": A, "target": "pA", "voices": {kB, gA}}
    rB = {"key": kB, "iss": A, "supersedes": "qB", "voices": {kB}}
    qC = {"key": kC, "iss": A, "target": "qB", "voices": {kC, kB}}
    pE = {"key": gE, "iss": iref_of(gE), "voices": {gE}}
    kR, kT = thumb(4), thumb(6)
    qT = {"key": kT, "iss": A, "target": "pA", "voices": {kT, gA}}
    pR = {"key": kR, "iss": A, "voices": {kR}}        # a recovery key's record: no rotation record, no old key
    valid = [
        ("the genesis key signing as itself, no record held", gA, A, {}),
        ("the genesis key signing as itself", gA, A, {"pA": pA}),
        ("a successor reached by one rotation record", kB, A, {"pA": pA, "qB": qB}),
        ("a successor under its own renewal", kB, A, {"pA": pA, "qB": qB, "rB": rB}),
        ("a successor two rotations on", kC, A, {"pA": pA, "qB": qB, "qC": qC}),
        ("a key with a record of another identity beside one that reaches", kB, A,
         {"pA": pA, "qB": qB, "xB": {"key": kB, "iss": iref_of(gE), "voices": {kB}}}),
    ]
    other = [
        ("an unrelated held key whose record names another identity", gE, A, {"pA": pA, "pE": pE}, ("Invalid", "kid_not_of_iss")),
        ("a successor whose rotation record is not held", kB, A, {"pA": pA}, ("Waiting", kB)),
        ("a rotation record whose predecessor's record is not held", kB, A, {"qB": qB}, ("Waiting", "pA")),
        ("a record of another identity beside a chain that waits", kB, A,
         {"qB": qB, "xB": {"key": kB, "iss": iref_of(gE), "voices": {kB}}}, ("Waiting", "pA")),
        ("a record claiming iss with no rotation", gE, A, {"pA": pA, "xE": {"key": gE, "iss": A, "voices": {gE}}},
         ("Invalid", "kid_not_of_iss")),
        ("a rotation record without the predecessor's statement", kB, A, {"pA": pA, "qB": dict(qB, voices={kB})},
         ("Waiting", "voice:qB")),
        ("a rotation record whose predecessor's statement is outside its record", kB, A, {"pA": pA, "qB": dict(qB, in_span=False)},
         ("Invalid", "kid_not_of_iss")),
        ("a rotation record signed after the predecessor's own revoked_after", kB, A, {"pA": pA, "qB": dict(qB, after_revocation=True)},
         ("Invalid", "kid_not_of_iss:rotation_after_revocation")),
        ("a rotation record without the new key's own statement", kB, A, {"pA": pA, "qB": dict(qB, voices={gA})},
         ("Waiting", "voice:qB")),
        ("two rival rotations of one predecessor", kB, A, {"pA": pA, "qB": qB, "qT": qT}, ("Invalid", "kid_not_of_iss")),
        ("a key only a bundle not counted seats", kR, A, {"pR": pR}, ("Invalid", "kid_not_of_iss"), ("held", {A: kR}, False)),
        ("a key a superseded bundle seated, the bundle in force seating another", kR, A, {"pR": pR}, ("Invalid", "kid_not_of_iss"),
         ("held", {A: thumb(5)}, True)),
        ("a recovered key whose bundle in force is not held", kR, A, {"pR": pR}, ("Waiting", "bundle-2"), ("not held", "bundle-2")),
        ("a key rotated from another identity", kC, A, {"pE": pE, "qC": {"key": kC, "iss": iref_of(gE), "target": "pE", "voices": {kC, gE}}},
         ("Invalid", "kid_not_of_iss")),
    ]
    valid += [("two rivals settled by a rotation naming both", kB, A,
               {"pA": pA, "qB": qB, "qT": qT, "dB": dict(qB, names=("qB", "qT"))}),
              ("a rival naming no record of the predecessor that covers its instant blocks nothing", kB, A,
               {"pA": pA, "qB": qB, "qT": dict(qT, in_span=False)})]
    valid.append(("a recovered key the bundle in force seats for iss", kR, A, {"pR": pR}, ("held", {A: kR}, True)))
    out = [(n, k, i, r, ("Valid", None), None) for n, k, i, r in valid[:-1]] + [valid[-1][:4] + (("Valid", None), valid[-1][4])]
    out = [o + ((),) for o in out] + [(o if len(o) == 6 else o + (None,)) + ((),) for o in other]
    kD, kG = thumb(7), thumb(8)
    pD = {"key": kD, "iss": A, "voices": {kD}}
    oD = {"id": "oD", "okey": kD, "own_voice": True, "admitted": True, "signer_of_iss": True, "covers": True,
          "evicted": False, "machine_under_person": False}
    inv = ("Invalid", "kid_not_of_iss")
    out += [
        ("a person's second device bound by a live admitted occurrence", kD, A, {"pD": pD}, ("Valid", None), None, (oD,)),
        ("an occurrence the roster door evicted", kD, A, {"pD": pD}, inv, None, (dict(oD, evicted=True),)),
        ("an occurrence signed by a key that is no key of iss", kD, A, {"pD": pD}, inv, None, (dict(oD, signer_of_iss=False),)),
        ("an occurrence the roster door did not admit", kD, A, {"pD": pD}, inv, None, (dict(oD, admitted=False),)),
        ("a statement at or after the occurrence's end", kD, A, {"pD": pD}, inv, None, (dict(oD, covers=False),)),
        ("an agent key bound under a person's identity", kG, A, {"pG": {"key": kG, "iss": A, "voices": {kG}}}, inv, None,
         (dict(oD, okey=kG, machine_under_person=True),)),
        ("an occurrence without the bound key's own voice", kD, A, {"pD": pD}, ("Waiting", "voice:oD"), None,
         (dict(oD, own_voice=False),)),
    ]
    return out


def key_iss_checks():
    """(line, problems): every sample gives the answer the text gives."""
    bad = []
    for name, kid, iss, recs, want, lin, occs in key_iss_samples():
        got = read_kid_of_iss(kid, iss, recs, lin, occs)
        if got != want:
            bad.append(f"reference key reader: {name} gives {got}, the text gives {want}")
    caught = 0
    for brk in ("any_key", "any_identity", "no_predecessor_statement", "genesis_only", "uncounted_bundle",
                "rivals_ignored", "uncovered_rival", "skip_occurrence", "occ_any_signer", "occ_agent_as_person"):
        KEY_BREAK.add(brk)
        if any(read_kid_of_iss(k, i, r, lin, oc) != w for _, k, i, r, w, lin, oc in key_iss_samples()):
            caught += 1
        else:
            bad.append(f"deliberate break not caught: the key reader with {brk}")
        KEY_BREAK.discard(brk)
    n = len(key_iss_samples())
    nv = sum(1 for s in key_iss_samples() if s[4][0] == "Valid")
    return (f"reference key reader (step 8): {nv} statements Valid, {n - nv} give their own answer "
            f"(Waiting or kid_not_of_iss); {caught} broken readers caught"), bad


def reader_checks():
    """(line, problems) for the reference reader: the valid bundle is Valid under both anchors with its placement, the
    valid later bundles are Valid, and each break gives its own answer."""
    bad = []
    (g, v, r, a), (_, oid), breaks, later_ok = reader_samples()
    for anc in (a, ("object_id", oid)):
        ans, out = read_bundle(g, v, r, anc)
        if ans != "Valid" or out["seats"].get(iref(3)) != ("transit-0", "onion-0") or len(out["holders"]) != 3:
            bad.append(f"reference reader: the valid bundle gives {ans} under {anc[0]}")
    for why, args in later_ok:
        ans, out = read_bundle(*args)
        if ans != "Valid":
            bad.append(f"reference reader: {why} gives {ans} {out if isinstance(out, str) else ''}")
    caught = 0
    for why, args, (want, reason) in breaks:
        ans, out = read_bundle(*args)
        if ans != want or (reason is not None and out != reason):
            bad.append(f"deliberate break not caught: {why} gives {ans} {out if isinstance(out, str) else ''}")
        else:
            caught += 1
    # a spent commitment never returns, across bundles: a second recovery on the first
    rec, rec_v, rows, anchor, gp = later_ok[1][1]
    ans, p1 = read_bundle(rec, rec_v, rows, anchor, gp)
    if ans == "Valid":
        rows2 = dict(rows)
        h0 = next(h for h in p1["holders"] if p1["keys"][h] != gp["keys"][h])
        key = lambda n: {1: 7, 3: -70100, -1: bytes([n]) * 1984}
        rows2[bytes([0x19]) * 32] = ("key:record", h0, {"chain_verifies": True, "pq_custody": "removable_offline", "key": key(8)})
        rows2[bytes([0x1B]) * 32] = ("key:record", h0, {"key": key(60)})
        cites = [c for c in rec["refs"]["also"]["cites"] if c[1][1] not in (bytes([0x17]) * 32, bytes([0x18]) * 32)]
        cites += [[2, [-16, bytes([0x19]) * 32]], [2, [-16, bytes([0x1B]) * 32]]]
        cites = sorted(cites, key=cde)
        nxt = lambda com: dict(rec, version=3, refs={"prev": object_id(GENESIS_TYP, cde(rec)), "also": {"cites": cites}},
                               charter=dict(rec["charter"], recovery_commitments={**rec["charter"]["recovery_commitments"], h0: com}))
        v2 = [(("recovery", h0, key(60)), 1763078400)]
        a_ret, o_ret = read_bundle(nxt(recovery_commitment(key(50))), v2, rows2, anchor, p1)
        a_new, _ = read_bundle(nxt(recovery_commitment(key(70))), v2, rows2, anchor, p1)
        a_old, o_old = read_bundle(nxt(recovery_commitment(key(70))), [(("recovery", h0, key(50)), 1763078400)], rows2, anchor, p1)
        if (a_ret, o_ret) != ("nothing", "genesis_bundle_count_unmet:recovery_commitment_spent"):
            bad.append(f"deliberate break not caught: a second recovery naming the spent commitment gives {a_ret}")
        elif a_old == "Valid" or o_old == "genesis_bundle_count_unmet":
            bad.append("deliberate break not caught: a second recovery under the spent recovery key is Valid")
        elif a_new != "Valid":
            bad.append(f"reference reader: a second recovery with a fresh commitment gives {a_new}")
        else:
            caught += 2
    return (f"reference bundle reader: the valid bundle is Valid under both anchors, {len(later_ok)} later bundles are "
            f"Valid; {caught} broken bundles give their own answer"), bad


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
        acc = {root: (ok, broken) for root, ok, broken in accord_samples()}
        for root, (ok, broken), what in (("key-record-members", key_record_samples(), "key record with its custody member"),
                                         ("recovery-commitment-input", recovery_samples(), "recovery commitment input"),
                                         ("accord-invocation", acc["accord-invocation"], "accord invocation payload"),
                                         ("accord-lifecycle", acc["accord-lifecycle"], "accord lifecycle payload"),
                                         ("transport-destination-binding", binding_samples(), "transport destination binding")):
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
             "[`manifests/signed_object_v2.cddl`](../manifests/signed_object_v2.cddl), the schema, with the payload rules of "
             "[`manifests/family_payloads_v2.cddl`](../manifests/family_payloads_v2.cddl); the two never disagree.*")
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
    ftext = family_cddl_text(rows)
    fold = open(FAMILY_CDDL, encoding="utf-8").read() if os.path.exists(FAMILY_CDDL) else None
    bad = agreement_with_breaks(rows, text + "\n" + ftext)
    first = next(r for r in rows if r["object"] in FAMILY_OBJECTS)
    if family_cddl_text([r for r in rows if r is not first]) == ftext:
        bad.append("deliberate break not caught: a family row dropped leaves the emitted family schema unchanged")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(2) as ex:        # the schema's samples and the families', side by side: two cddl processes at most
        cfut, ffut = ex.submit(cddl_checks, text), ex.submit(family_cddl_checks, text, ftext)
        (lines, cbad), (flines, fbad2) = cfut.result(), ffut.result()
    bad += cbad
    rline, rbad = reader_checks()
    lines.append(rline)
    bad += rbad
    kline, kbad = key_iss_checks()
    lines.append(kline)
    bad += kbad
    lines += flines
    bad += fbad2
    pline, pbad = family_payload_rule_checks()
    lines.append(pline)
    bad += pbad
    aline, abad = admission_checks()
    lines.append(aline)
    bad += abad
    gline, gbad = group_id_checks()
    lines.append(gline)
    bad += gbad
    sline, sbad = second_row_checks()
    lines.append(sline)
    bad += sbad
    dline, dbad = decimal_checks()
    lines.append(dline)
    bad += dbad
    rline2, rbad2 = receipt_checks()
    lines.append(rline2)
    bad += rbad2
    sys.path.insert(0, HERE)
    bline, bbad = build_manifest_checks()
    lines.append(bline)
    bad += bbad
    fline, fbad = family_checks()
    lines.append(fline)
    bad += fbad
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
    frel = os.path.relpath(FAMILY_CDDL, ROOT)
    if "--check" in argv:
        if fold != ftext:
            print(f"{NAME}: {frel} is stale; run python3 tools/build_cc_signed_object_v2.py")
            return 1
        print(f"{NAME}: {frel} is current")
        if out != txt:
            print(f"{NAME}: {rel} is stale; run python3 tools/build_cc_signed_object_v2.py")
            return 1
        print(f"{NAME}: {rel} is current ({loc[2]})")
        return 0
    if out != txt:
        open(path, "w", encoding="utf-8").write(out)
    print(f"{NAME}: {rel} {'updated' if out != txt else 'unchanged'} ({loc[2]})")
    if fold != ftext:
        open(FAMILY_CDDL, "w", encoding="utf-8").write(ftext)
    print(f"{NAME}: {frel} {'written' if fold != ftext else 'unchanged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
