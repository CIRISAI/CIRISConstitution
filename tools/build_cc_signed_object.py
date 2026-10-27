#!/usr/bin/env python3
"""
CC (the CIRIS Constitution) — the signed object, as data.

Source of truth: constitution/signed_object.tsv — one row per wire member of the
attestation row (and the outer shape of the key record), typed from CIRISPersist's
EnvelopeCore / RowMirror / Attestation structs at the pinned commit
(constitution/evidence_pins.tsv), with its placement relative to the signed bytes:

  signed:row             inside attestation_envelope.row — the closed seven-member mirror
  signed:envelope        inside attestation_envelope, typed by persist's EnvelopeCore
  signed:envelope-extra  inside attestation_envelope, typed by CC 2.1, carried untyped by persist
  beside                 outside the signed bytes, replicated with the row, bound to the bytes by a gate
  beside:signature       the row's own signature members
  beside:cosign          an additional_scrubs[] entry
  local                  persist-internal; not part of the wire contract
  not-on-wire            named by the CC text, not shipped at the pin

Outputs (all deterministic; CI regenerates and diffs):
  manifests/signed_object.json      the table as JSON with _meta (source hash, pin)
  manifests/signed_object.cddl      RFC 8610 CDDL (JSON profile, Appendix E) derived from the table
  constitution/part_2_the_grammar.md the body of CC 2.6.1.7 between its heading and the next heading

Checks:
  --self-test            recompute every vector in manifests/signed_object_vectors.json:
                         JCS bytes (pure-Python RFC 8785 for the vector subset), SHA-256,
                         Ed25519 (pure-Python RFC 8032). ML-DSA-65 is verified at generation
                         by the reference crate and recorded, not re-verified here.
  --check-persist PATH   cross-check the table against persist's src/federation/envelope.rs
                         at the pin: every typed EnvelopeCore / RowMirror field is a row with
                         a signed placement, and every signed:envelope / signed:row row is a
                         typed field.

stdlib only. Run:  python3 tools/build_cc_signed_object.py [--self-test] [--check-persist envelope.rs]
"""
import glob, csv, hashlib, json, os, re, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "constitution", "signed_object.tsv")
PINS = os.path.join(ROOT, "constitution", "evidence_pins.tsv")
PART2 = os.path.join(ROOT, "constitution", "part_2_the_grammar.md")
OUT_JSON = os.path.join(ROOT, "manifests", "signed_object.json")
OUT_CDDL = os.path.join(ROOT, "manifests", "signed_object.cddl")
VECTORS = os.path.join(ROOT, "manifests", "signed_object_vectors.json")
SECTION = "2.6.1.7"
PLACEMENTS = ["signed:row", "signed:envelope", "signed:envelope-extra", "beside",
              "beside:signature", "beside:cosign", "local", "not-on-wire"]
ROW_TYPES = ["scores", "delegates_to", "supersedes", "withdraws", "recants"]
COHORT_SCOPES = ["self", "family", "community", "affiliations", "species", "biosphere", "federation"]
ENVELOPE_CAP = 1_048_576


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_rows():
    with open(SRC, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    seen = set()
    for r in rows:
        key = (r["object"], r["member"], r["placement"])
        assert key not in seen, f"duplicate row {key}"
        seen.add(key)
        assert r["placement"] in PLACEMENTS, f"{key}: unknown placement {r['placement']!r}"
        assert r["array_kind"] in ("-", "set", "sequence", "undeclared"), f"{key}: array_kind {r['array_kind']!r}"
        for dec in r["cc_ref"].split():
            assert dec == "-" or re.fullmatch(r"\d+(\.\d+)*", dec), f"{key}: cc_ref {dec!r}"
    return rows


def persist_pin():
    with open(PINS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["repo"] == "CIRISPersist":
                return r["commit"]
    return "?"


# ---------------------------------------------------------------- JSON manifest
def build_json(rows):
    by_obj = OrderedDict()
    for r in rows:
        by_obj.setdefault(r["object"], []).append(OrderedDict(
            (k, r[k]) for k in ("member", "placement", "cc_name", "type", "array_kind",
                                "presence", "default", "cc_ref", "impl", "note")))
    counts = OrderedDict()
    for r in rows:
        counts[r["placement"]] = counts.get(r["placement"], 0) + 1
    findings = sorted(set(m.group(1) for r in rows for m in [re.search(r"\(finding (F\d+)", r["note"])] if m))
    return OrderedDict([
        ("_meta", OrderedDict([
            ("cc_section", SECTION),
            ("source", "constitution/signed_object.tsv"),
            ("source_sha256", sha256_file(SRC)),
            ("typed_from", OrderedDict([("repo", "CIRISPersist"), ("commit", persist_pin()),
                                        ("file", "src/federation/envelope.rs"),
                                        ("structs", ["EnvelopeCore", "RowMirror", "ScopeSet"]),
                                        ("row", "src/federation/types.rs#Attestation"),
                                        ("key_record", "src/federation/types.rs#KeyRecord")])),
            ("signing_input", "JCS(attestation_envelope) — RFC 8785 over the one envelope object; nothing beside it is signed"),
            ("signature", OrderedDict([
                ("classical", "Ed25519 (RFC 8032) over the signing input"),
                ("pqc", "ML-DSA-65 (FIPS 204) over the signing input || ed25519_signature (64 raw bytes)"),
                ("encoding", "base64, RFC 4648 section 4 standard alphabet, padded"),
                ("policy", "strict hybrid at the federation tier: both halves verify or the row is refused")])),
            ("content_hash", "original_content_hash = lowercase hex SHA-256 of the signing input"),
            ("row_types", ROW_TYPES),
            ("cohort_scopes", COHORT_SCOPES),
            ("envelope_cap_bytes", ENVELOPE_CAP),
            ("placements", PLACEMENTS),
            ("counts", counts),
            ("findings", findings),
        ])),
        ("objects", by_obj),
    ])


# ---------------------------------------------------------------- CDDL
TYPE_MAP = {
    "uuid": "uuid", "key-id": "key-id", "row-type": "row-type", "cohort-scope": "cohort-scope",
    "float": "number", "uint": "uint", "tstr": "tstr", "hex64": "hex64", "base64": "base64",
    "rfc3339-ms": "rfc3339-ms", "rfc3339": "rfc3339", "object": "{ * tstr => any }", "any": "any",
    "row-mirror": "row-mirror", "envelope": "envelope", "[* subject-id]": "[* subject-id]",
    "[* key-id]": "[* key-id]", "[* tstr]": "[* tstr]", "[* scrub-sig]": "[* scrub-sig]",
    "[* key-record]": "[* key-record]", "number": "number", "[* consent-basis]": "[* consent-basis]",
    "tstr / [* tstr]": "tstr / [* tstr]", "bool": "bool", "{* key-id => hex64}": "{ * key-id => hex64 }",
}


def cc_link(d):
    """A section link from Part 2: same-file for 2.x, the owning Part's file otherwise."""
    part = d.split(".")[0]
    if part == "2":
        return f"[{d}](#{d})"
    hits = glob.glob(os.path.join(ROOT, "constitution", f"part_{part}_*.md"))
    return f"[{d}]({os.path.basename(hits[0])}#{d})" if hits else f"[{d}](#{d})"


def cddl_type(t):
    if t in TYPE_MAP:
        return TYPE_MAP[t]
    if re.fullmatch(r'("[^"]*"\s*/\s*)*"[^"]*"', t):   # enum of literals
        return t
    raise SystemExit(f"cddl: no mapping for type {t!r}")


def cddl_entry(r, indent="  "):
    name = r["member"].split(".")[-1].split("[]")[-1].lstrip(".") or r["member"]
    if r["member"].endswith("]") or r["member"] == "*":
        return None
    always = r["presence"].startswith("REQUIRED") and (" on " not in r["presence"] or r["presence"].startswith("REQUIRED on every"))
    opt = "" if always and " iff " not in r["presence"] and "once" not in r["presence"] and "at the" not in r["presence"] and "for " not in r["presence"] else "? "
    comment = r["presence"]
    if r["default"] not in ("-", ""):
        comment += f"; default {r['default']}"
    if r["array_kind"] in ("set", "sequence", "undeclared"):
        comment += f"; array kind: {r['array_kind']}"
    return f"{indent}{opt}{name}: {cddl_type(r['type'])},  ; {comment}"


def build_cddl(rows, meta):
    A = [r for r in rows if r["object"] == "attestation_row"]
    K = [r for r in rows if r["object"] == "key_record"]
    mirror = [r for r in A if r["placement"] == "signed:row"]
    env = [r for r in A if r["placement"] in ("signed:envelope", "signed:envelope-extra") and r["member"] != "row"]
    beside = [r for r in A if r["placement"] in ("beside", "beside:signature")]
    cosign = [r for r in A if r["placement"] == "beside:cosign"]
    out = []
    out.append("; CC 2.6.1.7 — the signed object. GENERATED by tools/build_cc_signed_object.py from")
    out.append("; constitution/signed_object.tsv; do not edit. RFC 8610 CDDL, JSON profile (Appendix E).")
    out.append(f"; Typed from CIRISPersist {meta['_meta']['typed_from']['commit']} src/federation/envelope.rs.")
    out.append("; The signing input is JCS(attestation-row.attestation_envelope), RFC 8785, and nothing else.")
    out.append("")
    out.append("attestation-row = {")
    for r in beside:
        e = cddl_entry(r)
        if e:
            out.append(e)
    out.append("  ; persist-internal members (tier, promoted_at, withdraws_admission_rule) are not part of this contract")
    out.append("}")
    out.append("")
    out.append("; The signed object. Member presence is exactly what the producer signed (CC 2.6.1.1):")
    out.append("; an absent optional member is absent, never materialised; unknown members are preserved (CC 2.1.1).")
    out.append("envelope = {")
    out.append("  row: row-mirror,  ; REQUIRED; the closed mirror of the seven columns beside the row")
    for r in env:
        e = cddl_entry(r)
        if e:
            out.append(e)
    out.append("  * tstr => any,  ; family payload members (CC 3.3) and anything a consumer has not learned yet")
    out.append("}")
    out.append("")
    out.append("; Closed: exactly these seven members (CIRISPersist#643). deny_unknown_fields.")
    out.append("row-mirror = {")
    for r in mirror:
        e = cddl_entry(r)
        if e:
            out.append(e)
    out.append("}")
    out.append("")
    out.append("scrub-sig = {")
    for r in cosign:
        e = cddl_entry(r)
        if e:
            out.append(e)
    out.append("}")
    out.append("")
    out.append("key-record = {")
    for r in K:
        if r["placement"] == "local":
            continue
        e = cddl_entry(r)
        if e:
            out.append(e)
    out.append("}")
    out.append("")
    out.append("; CC 2.1 consent_basis entry (CIRISPersist#1041 shape; CIRISConstitution#183).")
    out.append('consent-basis = { principal: key-id, paths: [* ("subject" / "occurrence_of" / "delegates_to")], attestation_id: uuid }')
    out.append("")
    out.append("row-type = " + " / ".join(f'"{t}"' for t in ROW_TYPES))
    out.append("cohort-scope = " + " / ".join(f'"{t}"' for t in COHORT_SCOPES))
    out.append('uuid = tstr .regexp "[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}"')
    out.append('key-id = tstr .regexp "[a-z0-9-]+"  ; <label>-<fingerprint>, CC 2.6.8; a legacy 64-hex id is also a key-id')
    out.append('canonical-id = tstr .regexp "canonical:[a-z0-9-]+:[0-9a-f]+"  ; CC 2.3.2.1, tag required')
    out.append("subject-id = key-id / canonical-id")
    out.append('hex64 = tstr .regexp "[0-9a-f]{64}"  ; CC 2.6.3')
    out.append('base64 = tstr .regexp "[A-Za-z0-9+/]+={0,2}"  ; RFC 4648 section 4, padded, no whitespace')
    out.append('rfc3339-ms = tstr .regexp "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\\\.[0-9]{3}Z"  ; CC 2.6.2')
    out.append("rfc3339 = tstr  ; a column rendered by the store; the signed twin inside the envelope is rfc3339-ms")
    out.append("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- Part 2 body
def md_cell(s):
    return s.replace("|", "\\|")


def build_section_body(rows, meta):
    A = [r for r in rows if r["object"] == "attestation_row"]
    K = [r for r in rows if r["object"] == "key_record"]
    L = []
    L.append("")
    L.append("*This table, [`manifests/signed_object.cddl`](../manifests/signed_object.cddl) and [`manifests/signed_object.json`](../manifests/signed_object.json) are rendered from one data file, and [`manifests/signed_object_vectors.json`](../manifests/signed_object_vectors.json) holds the byte vectors; the data is the source and the three never disagree.*")
    L.append("")
    L.append("**The object (normative).** The signed object of an attestation row is `attestation_envelope`: one JSON object. The signing input is JCS(`attestation_envelope`) ([CC 2.6.1.3](#2.6.1.3)) and nothing else — the row's own signature members, every cosignature and every column beside the row are outside the bytes, so a cosignature is never inside the bytes it signs. Seven of those columns are mirrored *inside* the bytes under the member `row`, a closed set; a row with no mirror is refused `envelope_member_missing`, and a column that disagrees with its mirror is refused `typed_diverges_from_envelope`. The claim's instants ride inside the bytes as `asserted_at` and `expires_at`, and the columns are read back out of them. The row's own signature is the attester's: the classical half verifies against `attesting_key_id`'s pinned Ed25519 key over the signing input, the post-quantum half against its ML-DSA-65 key over the signing input followed by the raw Ed25519 signature ([hybrid-sig], [CC 2.6.5](#2.6.5)); at the federation tier both halves verify or the row is refused. `original_content_hash` is the lowercase hex SHA-256 of the signing input and is recomputed at ingest. A second signer over the same bytes is an entry of `additional_scrubs[]`, beside the row, verified against its own key. A JCS image above 1 MiB is refused `ENVELOPE_TOO_LARGE` ([CC 2.6.1.3](#2.6.1.3)).")
    L.append("")
    L.append("**Refusals at this door (normative).** A shape refusal of the signed object is the token `federation_malformed_row` with one reason from this closed set: `envelope_member_missing` (the mirror or another required member is absent), `envelope_member_invalid` (a member is ill-typed or an instant is not in the [CC 2.6.2](#2.6.2) form), `envelope_member_null` (an optional member is `null`), `typed_diverges_from_envelope` (a column beside the row differs from its mirror), `envelope_row_member_unknown` (the `row` mirror carries a member outside its closed seven), `content_hash_mismatch` (`original_content_hash` is not the SHA-256 of the signing input) and `subject_key_id_malformed` (an element of `subject_key_ids` is neither a `key_id` nor the tagged canonical form of [CC 2.3.2.1](#2.3.2.1)). A `withdraws` that meets no rule of [CC 2.4.1.1](#2.4.1.1) is refused `federation_withdraws_not_admitted`. A set out of order or with a duplicate is `federation_set_semantics_unsorted`, a type outside the five is `attestation_type_unregistered`, a failed signature half is `SIGNATURE_VERIFICATION_FAILED`, and an envelope over the cap is `ENVELOPE_TOO_LARGE`.")
    L.append("")
    L.append("**Placement vocabulary.** `signed:row` — inside `attestation_envelope.row`. `signed:envelope` — inside `attestation_envelope`, typed by persist. `signed:envelope-extra` — inside `attestation_envelope`, typed by [CC 2.1](#2.1), carried untyped by persist and validated at the family's gate. `beside` — outside the bytes, replicated, bound to the bytes by a gate. `beside:signature` — the row's own signature members. `beside:cosign` — an `additional_scrubs[]` entry. `local` — persist-internal, not a wire contract. `not-on-wire` — named by this text, not carried on the wire. An array's kind is `set` (sorted by JCS string before signing) or `sequence` (as authored), per [CC 2.6.1.1.1](#2.6.1.1.1).")
    L.append("")

    def table(title, subset):
        L.append(f"**{title}**")
        L.append("")
        L.append("| Member | Placement | Type | Array | Presence | Default | CC | Note |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in subset:
            cc = " ".join(cc_link(d) if d != "-" else "—" for d in r["cc_ref"].split())
            L.append("| `%s` | %s | `%s` | %s | %s | %s | %s | %s |" % (
                md_cell(r["member"]), r["placement"], md_cell(r["type"]),
                "—" if r["array_kind"] == "-" else r["array_kind"],
                md_cell(r["presence"]), md_cell(r["default"]) if r["default"] != "-" else "—", cc, md_cell(r["note"])))
        L.append("")

    table("Inside the signed bytes — the mirror (closed, exactly seven)",
          [r for r in A if r["placement"] == "signed:row"])
    table("Inside the signed bytes — members persist types",
          [r for r in A if r["placement"] == "signed:envelope"])
    table("Inside the signed bytes — members this text types and persist carries untyped",
          [r for r in A if r["placement"] in ("signed:envelope-extra", "not-on-wire")])
    table("Beside the row — outside the bytes, bound to them",
          [r for r in A if r["placement"] in ("beside", "beside:signature", "beside:cosign", "local")])
    table("The key record — the second signed object (outer shape; its envelope's member table is the key plane's)",
          K)
    L.append("**Rules this table carries.** "
             "A set-kind array is sorted **and** unique, refused otherwise as `federation_set_semantics_unsorted` with the member named; a relay never re-sorts it, since re-sorting would move signed bytes. "
             "The form an emitter writes for `scope` is the array; a bare token is admitted as the one-element array it denotes, and nothing is normalised in signed bytes. "
             "An explicit JSON `null` on an optional member is refused as malformed ([CC 2.6.1.1.1](#2.6.1.1.1)). "
             "`witnesses[]` is a set. "
             "The quorum carrier is `additional_scrubs[]` beside the row, as [CC 2.1](#2.1) and [CC 2.4](#2.4) name it.")
    L.append("")
    L.append("**Vectors.** [`manifests/signed_object_vectors.json`](../manifests/signed_object_vectors.json) carries two test identities (Ed25519 and ML-DSA-65 seeds, public keys and the [CC 2.6.8](#2.6.8) `key_id` derived from each), and for each vector the envelope, its JCS bytes, `original_content_hash`, both signature halves and the assembled row: a minimal `scores`; the same claim with an explicit default (different bytes, both verify, [CC 2.6.1.1](#2.6.1.1)); a cosigned variant; a `withdraws`; the at-cap and cap-plus-one envelopes as a recipe with their hashes; and refusal cases with their tokens. Signatures were produced and verified by the reference implementation (CIRISVerify); the JCS bytes, the hashes and the Ed25519 half are recomputed from the vectors on every change to this document. A second implementation that reproduces these bytes and signatures has met the [CC 2.6.1.1.1](#2.6.1.1.1) byte-identity target for this object.")
    L.append("")
    return "\n".join(L)


def write_section(rows, meta):
    text = open(PART2, encoding="utf-8").read().split("\n")
    hdr = None
    for i, ln in enumerate(text):
        if re.match(r"^#{2,6}\s+" + re.escape(SECTION) + r"\s+`", ln):
            hdr = i
            break
    if hdr is None:
        raise SystemExit(f"CC {SECTION} heading not found in {PART2}; add it first")
    nxt = len(text)
    for j in range(hdr + 1, len(text)):
        if re.match(r"^#{2,6}\s+\d", text[j]):
            nxt = j
            break
    body = build_section_body(rows, meta).split("\n")
    new = text[:hdr + 1] + body + text[nxt:]
    out = "\n".join(new)
    if out != "\n".join(text):
        open(PART2, "w", encoding="utf-8").write(out)
        return True
    return False


# ---------------------------------------------------------------- pure-Python JCS (vector subset) + Ed25519
def jcs(v):
    """RFC 8785 for the subset the vectors use: objects, arrays, strings, ints, floats
    whose shortest round-trip repr is also the ES6 form, booleans, null."""
    if v is None:
        return b"null"
    if v is True:
        return b"true"
    if v is False:
        return b"false"
    if isinstance(v, int):
        return str(v).encode()
    if isinstance(v, float):
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("non-finite number")
        if v == int(v) and abs(v) < 1e21:
            return str(int(v)).encode()
        s = repr(v)
        if "e" in s or "E" in s:
            raise ValueError(f"exponent form not covered by the vector subset: {s}")
        return s.encode()
    if isinstance(v, str):
        out = ['"']
        for ch in v:
            o = ord(ch)
            if ch == '"':
                out.append('\\"')
            elif ch == "\\":
                out.append("\\\\")
            elif ch == "\b":
                out.append("\\b")
            elif ch == "\f":
                out.append("\\f")
            elif ch == "\n":
                out.append("\\n")
            elif ch == "\r":
                out.append("\\r")
            elif ch == "\t":
                out.append("\\t")
            elif o < 0x20:
                out.append("\\u%04x" % o)
            else:
                out.append(ch)
        out.append('"')
        return "".join(out).encode("utf-8")
    if isinstance(v, (list, tuple)):
        return b"[" + b",".join(jcs(x) for x in v) + b"]"
    if isinstance(v, dict):
        items = sorted(v.items(), key=lambda kv: kv[0].encode("utf-16-be"))
        return b"{" + b",".join(jcs(k) + b":" + jcs(x) for k, x in items) + b"}"
    raise TypeError(type(v))


# RFC 8032 Ed25519 verify, pure Python (slow, fine for a handful of vectors).
_p = 2 ** 255 - 19
_d = (-121665 * pow(121666, _p - 2, _p)) % _p
_q = 2 ** 252 + 27742317777372353535851937790883648493
_I = pow(2, (_p - 1) // 4, _p)


def _xrecover(y):
    xx = (y * y - 1) * pow(_d * y * y + 1, _p - 2, _p)
    x = pow(xx, (_p + 3) // 8, _p)
    if (x * x - xx) % _p != 0:
        x = (x * _I) % _p
    if x % 2 != 0:
        x = _p - x
    return x


_By = (4 * pow(5, _p - 2, _p)) % _p
_B = (_xrecover(_By), _By)


def _edwards_add(P, Q):
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * pow(1 + _d * x1 * x2 * y1 * y2, _p - 2, _p)
    y3 = (y1 * y2 + x1 * x2) * pow(1 - _d * x1 * x2 * y1 * y2, _p - 2, _p)
    return (x3 % _p, y3 % _p)


def _scalarmult(P, e):
    Q = (0, 1)
    while e > 0:
        if e & 1:
            Q = _edwards_add(Q, P)
        P = _edwards_add(P, P)
        e >>= 1
    return Q


def _decodepoint(s):
    y = int.from_bytes(s, "little") & ((1 << 255) - 1)
    x = _xrecover(y)
    if x & 1 != (s[31] >> 7):
        x = _p - x
    P = (x, y)
    if (-x * x + y * y - 1 - _d * x * x * y * y) % _p != 0:
        raise ValueError("point not on curve")
    return P


def _encodepoint(P):
    x, y = P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def ed25519_verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if len(sig) != 64 or len(pub) != 32:
        return False
    R = _decodepoint(sig[:32])
    A = _decodepoint(pub)
    S = int.from_bytes(sig[32:], "little")
    if S >= _q:
        return False
    h = int.from_bytes(hashlib.sha512(sig[:32] + pub + msg).digest(), "little")
    lhs = _scalarmult(_B, S)
    rhs = _edwards_add(R, _scalarmult(A, h))
    return _encodepoint(lhs) == _encodepoint(rhs)


def self_test():
    import base64
    V = json.load(open(VECTORS, encoding="utf-8"))
    keys = V["keys"]
    fails = []
    n = 0
    for vec in V["vectors"]:
        name = vec["name"]
        if vec.get("kind") == "recipe":
            env = json.loads(json.dumps(vec["envelope_template"]))
            env["context"] = "a" * vec["context_length"]
            b = jcs(env)
            if len(b) != vec["jcs_length"]:
                fails.append(f"{name}: jcs length {len(b)} != {vec['jcs_length']}")
            if hashlib.sha256(b).hexdigest() != vec["original_content_hash"]:
                fails.append(f"{name}: sha256 mismatch")
            n += 1
            continue
        if vec.get("kind") == "refuse":
            n += 1
            continue
        b = jcs(vec["envelope"])
        if b.hex() != vec["jcs_hex"]:
            fails.append(f"{name}: jcs bytes differ")
        if hashlib.sha256(b).hexdigest() != vec["original_content_hash"]:
            fails.append(f"{name}: sha256 mismatch")
        row = vec["row"]
        if row["original_content_hash"] != vec["original_content_hash"]:
            fails.append(f"{name}: row hash differs from vector hash")
        sigs = [(row["attesting_key_id"], row["scrub_signature_classical"])]
        sigs += [(s["scrub_key_id"], s["scrub_signature_classical"]) for s in row.get("additional_scrubs", [])]
        for kid, sig_b64 in sigs:
            key = next(k for k in keys.values() if k["key_id"] == kid)
            pub = bytes.fromhex(key["ed25519_pub_hex"])
            if not ed25519_verify(pub, b, base64.b64decode(sig_b64)):
                fails.append(f"{name}: Ed25519 by {kid} does not verify")
            if base64.b64encode(base64.b64decode(sig_b64)) != sig_b64.encode():
                fails.append(f"{name}: signature base64 is not the standard padded form")
        # mirror/column binding on the assembled row
        m = vec["envelope"]["row"]
        for col in ("attestation_id", "attesting_key_id", "attestation_type", "attested_key_id", "cohort_scope"):
            if row[col] != m[col]:
                fails.append(f"{name}: column {col} diverges from the mirror")
        if sorted(row.get("subject_key_ids", [])) != sorted(m["subject_key_ids"]):
            fails.append(f"{name}: subject_key_ids column diverges from the mirror")
        n += 1
    try:
        import ciris_verify  # the reference JCS, when the wheel is installed locally
        for vec in V["vectors"]:
            if "envelope" in vec and vec.get("kind") not in ("recipe", "refuse"):
                if ciris_verify.jcs_canonicalize(vec["envelope"]).hex() != vec["jcs_hex"]:
                    fails.append(f"{vec['name']}: reference JCS disagrees")
        ref = "reference JCS (ciris_verify wheel) agreed"
    except ImportError:
        ref = "reference JCS not installed here; pure-Python JCS only"
    print(f"self-test: {n} vectors, {len(fails)} failure(s); {ref}")
    for f in fails:
        print("  FAIL", f)
    return not fails


def check_persist(path):
    src = open(path, encoding="utf-8").read()
    core = re.search(r"pub struct EnvelopeCore \{(.*?)\n\}", src, re.S).group(1)
    mirror = re.search(r"pub struct RowMirror \{(.*?)\n\}", src, re.S).group(1)
    core_fields = [m for m in re.findall(r"^\s*pub (\w+):", core, re.M) if m != "extra"]
    mirror_fields = re.findall(r"^\s*pub (\w+):", mirror, re.M)
    rows = load_rows()
    A = {r["member"]: r for r in rows
         if r["object"] == "attestation_row" and r["placement"].startswith("signed:")}
    bad = []
    for f in core_fields:
        r = A.get(f)
        if not r or r["placement"] != "signed:envelope":
            bad.append(f"EnvelopeCore.{f}: not a signed:envelope row")
    for f in mirror_fields:
        r = A.get("row." + f)
        if not r or r["placement"] != "signed:row":
            bad.append(f"RowMirror.{f}: not a signed:row row")
    for m, r in A.items():
        if r["placement"] == "signed:envelope" and m not in core_fields:
            bad.append(f"table {m}: signed:envelope but not an EnvelopeCore field")
        if r["placement"] == "signed:row" and m[4:] not in mirror_fields:
            bad.append(f"table {m}: signed:row but not a RowMirror field")
    print(f"check-persist: EnvelopeCore {len(core_fields)} typed fields, RowMirror {len(mirror_fields)}; {len(bad)} mismatch(es)")
    for b in bad:
        print("  MISMATCH", b)
    return not bad


def main():
    args = sys.argv[1:]
    if "--check-persist" in args:
        ok = check_persist(args[args.index("--check-persist") + 1])
        sys.exit(0 if ok else 1)
    if "--self-test" in args:
        sys.exit(0 if self_test() else 1)
    rows = load_rows()
    meta = build_json(rows)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(OUT_CDDL, "w", encoding="utf-8") as f:
        f.write(build_cddl(rows, meta))
    changed = write_section(rows, meta)
    c = meta["_meta"]["counts"]
    print(f"signed_object: {len(rows)} rows ({', '.join(f'{k} {v}' for k, v in c.items())}); "
          f"source {meta['_meta']['source_sha256'][:12]}…; Part 2 {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
