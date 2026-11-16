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
import csv, glob, os, re, subprocess, sys, tempfile

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
