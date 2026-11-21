#!/usr/bin/env python3
"""
check_trace.py: a genesis ceremony's signed output, checked before anyone publishes it.

The ceremony tool writes a TRACE: one entry per signed statement, in ceremony order, decoded from the
signed bytes (formal/ceremony/CEREMONY.md section 3, steps 1 to 4). This reads a trace and checks every
invariant of manifests/ceremony.json against it. A trace that passes is one the model of this folder
(ceremony.py, P1 to P11) accepts as a genesis; one that fails names the invariant and the statement.

Where an entry carries its signed bytes (`cose_hex`), the checker decodes them itself, with the CBOR reader
below, which shares no code with the tool's, and requires the two decodings to agree. It then recomputes the
row id of each row and the object id of the bundle, and resolves every `cites` by id.

    python3 -I check_trace.py TRACE.json              check at the current edition
    python3 -I check_trace.py TRACE.json --at rc21    skip the checks an earlier edition did not have
    python3 -I check_trace.py --plants TRACE.json     mutate a passing trace; every plant must be caught
    python3 -I check_trace.py --write-manifest        write manifests/ceremony.json
    python3 -I check_trace.py --check                 the manifest is current, the sample passes, plants are caught

Standard library only. Exit 0 on a pass, 1 on a failure.
"""
import base64, copy, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MANIFEST = os.path.join(ROOT, "manifests", "ceremony.json")
SAMPLE = os.path.join(HERE, "trace_sample.json")
EDITIONS = ["rc21", "rc22"]
ALG, EDITION_CLAIM = -70100, "-70003"
ROW_CT = "application/vnd.ciris.row+cbor"
CKT = "urn:ietf:params:oauth:ckt:sha-256:"
YEAR_MS = 365 * 86400 * 1000
HALT_MEMBERS = {"author", "accord_root", "invocation_id", "nonce", "asserted_at", "valid_until"}
WITNESS_MEMBERS = ("witnesses", "witness_quorum", "witness_cadence_secs", "attach_window_secs",
                   "transparency_services", "receipt_quorum", "receipt_cadence_secs")
TCP = 1
OWNER_ONLY = {"infra:network_presence", "infra:hold_community_membership", "infra:hold_family_membership"}   # CC 4.4.3.19, two granters

# The steps of CEREMONY.md section 3 that produce signed statements, as data. `kind` is the trace's word for
# the statement; `per` says how many there are; `after` names the steps whose statements it cites.
STEPS = [
    {"step": 1, "kind": "key:record", "signer": "holder", "per": "each holder", "after": [],
     "what": "each holder's key record: accord_holder, no valid_until, attested custody"},
    {"step": 2, "kind": "key:record", "signer": "seat", "per": "each serve seat", "after": [],
     "what": "each seat's key record: node, valid_until within 365 days"},
    {"step": 2, "kind": "identity:occurrence", "signer": "seat", "per": "each serve seat", "after": [2],
     "what": "each seat's transport destination binding, citing its key record"},
    {"step": 3, "kind": "accord:invoke:constitutional", "signer": "holder", "per": "each holder", "after": [1],
     "what": "each holder's pre-signed halt, sealed"},
    {"step": 4, "kind": "ceg-genesis-bundle/2", "signer": "holder", "per": "every holder, one payload", "after": [1, 2, 3],
     "what": "the genesis bundle, signed by every holder"},
]

# id, since, cc, statement. The text of each is what a failure prints.
INVARIANTS = [
    ("C01", "rc21", "2.6.1.7", "every statement is one composite signature (alg -70100) under edition 2, with iss, and a row carries the row content type and typ ceg-row/2"),
    ("C02", "rc21", "5.3.4", "the statements come in the order of the steps, and the bundle is last"),
    ("C03", "rc21", "2.6.1.8", "iat is the payload's asserted_at in seconds, exp is its valid_until where it has one and absent where it has none, and kid is the thumbprint inside iss"),
    ("C04", "rc21", "4.2.3", "a holder's key record is accord_holder alone, carries no valid_until, and attests custody with the post-quantum half removable_offline and a chain"),
    ("C05", "rc21", "2.6.1.7", "a seat's key record is node alone and ends within 365 days of its asserted_at"),
    ("C06", "rc21", "2.6.1.4", "a seat's binding is signed by the seat, cites its key record, and carries its X-Wing keys beside transport_destination, never inside it"),
    ("C07", "rc22", "5.3.4", "a serve seat's binding carries dial_hints with at least one tcp hint"),
    ("C08", "rc21", "4.2.1.1", "every holder has exactly one pre-signed halt, with the closed payload, a 32-byte nonce, its own invocation id, and sub equal to accord_root"),
    ("C09", "rc21", "5.3.4", "every holder signs the bundle, over one payload, and nobody else does"),
    ("C10", "rc21", "2.6.1.11", "the bundle is version 1 with no prev, names the holders of step 1 and the seats of step 2, and cites their records"),
    ("C11", "rc21", "4.2.6", "the charter commits one recovery key for each holder, with a halt fuse, and its scope carries infra:serve and infra:attest and none of the scopes only an owner grants"),
    ("C12", "rc22", "4.2.6", "no two holders share a recovery commitment"),
    ("C13", "rc21", "3.2", "a charter in witnessed mode off carries none of the witnessing members, and no member is written as zero"),
    ("C14", "rc22", "2.6.1.11", "a bundle voice's sub is the bundle's family_key_id"),
    ("C15", "rc21", "4.2.1.1", "a halt of this form exists for every holder before the bundle, and names the bundle's lineage"),
    ("C16", "rc21", "2.6.2", "no record is dated after the bundle that cites it, and every valid_until is later than its asserted_at"),
    ("C18", "rc21", "4.2.3", "no two holders name one device in their custody leaves, and no leaf's device serial is malformed; a leaf that names no device and a certificate shared above the devices are no fault"),
    ("C19", "rc22", "4.2.6", "each holder's recovery commitment is the one the charter carries, and it commits no key that signs for a holder or a seat"),
    ("C17", "rc21", "2.6.1.2", "where the signed bytes are given, an independent decoding agrees with the trace, and every cites resolves to a statement of the trace"),
]


# ---- a CBOR reader for the definite-length forms a statement uses -------------------------------------------
def dec(b, i=0):
    ib = b[i]; mt, ai = ib >> 5, ib & 31; i += 1
    if ai < 24: n = ai
    elif ai in (24, 25, 26, 27):
        w = 1 << (ai - 24); n = int.from_bytes(b[i:i + w], "big"); i += w
    else: raise ValueError("indefinite or reserved length")
    if mt == 0: return n, i
    if mt == 1: return -1 - n, i
    if mt == 2: return bytes(b[i:i + n]), i + n
    if mt == 3: return b[i:i + n].decode(), i + n
    if mt == 4:
        out = []
        for _ in range(n):
            x, i = dec(b, i); out.append(x)
        return out, i
    if mt == 5:
        out = {}
        for _ in range(n):
            k, i = dec(b, i); x, i = dec(b, i); out[k] = x
        return out, i
    if mt == 6:
        x, i = dec(b, i); return ("tag", n, x), i
    return {20: False, 21: True, 22: None}[ai], i


def head(mt, n):
    if n < 24: return bytes([mt << 5 | n])
    for w, ai in ((1, 24), (2, 25), (4, 26), (8, 27)):
        if n < 1 << (8 * w): return bytes([mt << 5 | ai]) + n.to_bytes(w, "big")


def tstr(s):
    e = s.encode(); return head(3, len(e)) + e


def ids_from_bytes(raw):
    """(protected, payload, id) of one statement: the row id of a row, the object id of a bundle voice."""
    top, _ = dec(raw)
    if not (isinstance(top, tuple) and top[1] == 18): raise ValueError("not a tagged COSE_Sign1")
    prot_b, _unprot, payload_b, _sig = top[2]
    prot, _ = dec(prot_b); payload, _ = dec(payload_b)
    typ = prot.get(16)
    if typ == "ceg-row/2":
        claims = prot[15]; author = payload.get("author")
        pre = (head(4, 6) + tstr("CEG-row/2") + tstr(prot[-70001]) + tstr(prot[-70002]) + tstr(claims[2])
               + (tstr(author) if author is not None else b"\xf6") + head(2, len(payload_b)) + payload_b)
    else:
        pre = head(4, 4) + tstr("CEG-object/2") + tstr(typ) + b"\xf6" + head(2, len(payload_b)) + payload_b
    return prot, payload, hashlib.sha256(pre).hexdigest()


# ---- reading the trace ---------------------------------------------------------------------------------------
def hx(v):
    return v["hex"] if isinstance(v, dict) and set(v) == {"hex"} else None


def claims(s):
    return s["protected"].get("cwt_claims", {})


def iss(s):
    return claims(s).get("iss")


def of_kind(T, kind, step=None):
    return [s for s in T["statements"] if s["kind"] == kind and (step is None or s["step"] == step)]


def cites(s):
    """The digests a statement cites, as hex."""
    out = []
    for r in (s["payload"].get("refs") or {}).get("also", {}).get("cites", []):
        try: out.append(hx(r[1][1]))
        except Exception: out.append(None)
    return out


def norm(v):
    """The trace's JSON form of a decoded value, for comparing with an independent decoding."""
    if isinstance(v, (bytes, bytearray)): return {"hex": bytes(v).hex()}
    if isinstance(v, dict): return {str(k): norm(x) for k, x in v.items()}
    if isinstance(v, list): return [norm(x) for x in v]
    return v


# ---- the checks: each yields the failures of one invariant ---------------------------------------------------
def check(T):
    S = T["statements"]; out = {i[0]: [] for i in INVARIANTS}
    bad = lambda cid, s, why: out[cid].append(f"step {s['step']} {s['kind']} #{s.get('index', 0)}: {why}" if s else why)
    holders_rec = of_kind(T, "key:record", 1); seats_rec = of_kind(T, "key:record", 2)
    bindings = of_kind(T, "identity:occurrence"); halts = of_kind(T, "accord:invoke:constitutional")
    voices = of_kind(T, "ceg-genesis-bundle/2")
    H = [iss(s) for s in holders_rec]; SEATS = [iss(s) for s in seats_rec]
    bundle = voices[0]["payload"] if voices else {}
    charter = bundle.get("charter", {})

    for s in S:                                                                     # C01
        p = s["protected"]
        if p.get("alg") != ALG: bad("C01", s, f"alg {p.get('alg')}")
        if claims(s).get(EDITION_CLAIM) != 2: bad("C01", s, "the edition claim is not 2")
        if not iss(s): bad("C01", s, "no iss")
        if s.get("signature_len", 3373) != 3373: bad("C01", s, f"a signature of {s.get('signature_len')} bytes")
        row = s["kind"] != "ceg-genesis-bundle/2"
        if row and (p.get("typ") != "ceg-row/2" or p.get("content_type") != ROW_CT): bad("C01", s, "a row without the row typ and content type")
        if not row and (p.get("typ") != "ceg-genesis-bundle/2" or "content_type" in p): bad("C01", s, "a bundle voice with a content type or the wrong typ")

    steps = [s["step"] for s in S]                                                  # C02
    if steps != sorted(steps): bad("C02", None, f"the steps run {steps}")
    if S and S[-1]["kind"] != "ceg-genesis-bundle/2": bad("C02", None, "the last statement is not a bundle voice")
    known = {(d["step"], d["kind"]) for d in STEPS}
    for s in S:
        if (s["step"], s["kind"]) not in known: bad("C02", s, "no such statement at this step")

    for s in S:                                                                     # C03
        c, pl = claims(s), s["payload"]
        if c.get("iat") != pl.get("asserted_at", 0) // 1000: bad("C03", s, "iat is not asserted_at in seconds")
        vu = pl.get("valid_until")
        if (c.get("exp") is None) != (vu is None) or (vu is not None and c.get("exp") != vu // 1000): bad("C03", s, "exp does not follow valid_until")
        kid, i = hx(s["protected"].get("kid")), iss(s) or ""
        try: want = base64.urlsafe_b64decode(i[len(CKT):] + "=").hex() if i.startswith(CKT) else None
        except Exception: want = None
        if kid is None or kid != want: bad("C03", s, "kid is not the thumbprint inside iss")

    for s in holders_rec:                                                           # C04
        pl = s["payload"]; ev = pl.get("attestation_evidence") or {}
        if pl.get("identity_type") != ["accord_holder"]: bad("C04", s, f"identity_type {pl.get('identity_type')}")
        if "valid_until" in pl: bad("C04", s, "a holder's record carries valid_until")
        if ev.get("pq_custody") != "removable_offline": bad("C04", s, f"pq_custody {ev.get('pq_custody')}")
        if not ev.get("hardware_class") or not ev.get("chain"): bad("C04", s, "no hardware class or no attestation chain")
        if claims(s).get("sub") != iss(s) or pl.get("author") != iss(s): bad("C04", s, "the record is not the key's own")
    if len(set(H)) != len(H) or len(H) < 2: bad("C04", None, f"{len(H)} holder records, {len(set(H))} distinct")

    for s in seats_rec:                                                             # C05
        pl = s["payload"]
        if pl.get("identity_type") != ["node"]: bad("C05", s, f"identity_type {pl.get('identity_type')}")
        vu, at = pl.get("valid_until"), pl.get("asserted_at", 0)
        if vu is None or not at < vu <= at + YEAR_MS: bad("C05", s, "valid_until is absent or outside 365 days")

    rec_ids = {s.get("_id") for s in seats_rec + holders_rec if s.get("_id")}
    for s in bindings:                                                              # C06, C07
        pl = s["payload"]; td = pl.get("transport_destination") or {}
        if iss(s) not in SEATS: bad("C06", s, "not signed by a seat of step 2")
        if not td: bad("C06", s, "no transport_destination")
        if not hx(pl.get("transit_xwing_pubkey")): bad("C06", s, "no transit X-Wing key beside transport_destination")
        if any("xwing" in k for k in td): bad("C06", s, "an X-Wing key inside transport_destination")
        if not cites(s): bad("C06", s, "the binding cites no key record")
        hints = pl.get("dial_hints")
        if not hints or not any(isinstance(h, list) and h and h[0] == TCP for h in hints): bad("C07", s, "no tcp dial hint")
    if {iss(s) for s in bindings} != set(SEATS): bad("C06", None, "a seat has no binding, or a binding has no seat")

    by = {}
    for s in halts:                                                                 # C08, C15
        pl = s["payload"]; by.setdefault(iss(s), []).append(s)
        if iss(s) not in H: bad("C08", s, "a halt by a key that is no holder")
        if set(pl) != HALT_MEMBERS: bad("C08", s, f"payload members {sorted(set(pl) ^ HALT_MEMBERS)} differ from the closed set")
        if len(hx(pl.get("nonce")) or "") != 64: bad("C08", s, "the nonce is not 32 bytes")
        if claims(s).get("sub") != pl.get("accord_root"): bad("C08", s, "sub is not accord_root")
        if pl.get("accord_root") != bundle.get("family_key_id"): bad("C15", s, "the halt names another lineage than the bundle's")
    for h in H:
        if len(by.get(h, [])) != 1: bad("C08", None, f"holder {h[-8:]} has {len(by.get(h, []))} halts")
    inv = [s["payload"].get("invocation_id") for s in halts]
    if len(set(inv)) != len(inv): bad("C08", None, "two halts share an invocation id")
    if voices and any(h not in by for h in H): bad("C15", None, "the bundle exists and a holder has no sealed halt")
    if halts and voices and max(s["step"] for s in halts) >= min(s["step"] for s in voices): bad("C15", None, "a halt is not before the bundle")

    signers = [iss(s) for s in voices]                                              # C09
    if sorted(signers) != sorted(H): bad("C09", None, f"{len(signers)} voices from {len(set(signers) & set(H))} of {len(H)} holders")
    if any(json.dumps(v["payload"], sort_keys=True) != json.dumps(bundle, sort_keys=True) for v in voices): bad("C09", None, "the voices are over different payloads")

    if voices:                                                                      # C10
        if bundle.get("version") != 1 or "prev" in bundle or "prev" in (bundle.get("refs") or {}): bad("C10", voices[0], "not version 1 with no prev")
        if sorted(bundle.get("holders", [])) != sorted(H): bad("C10", voices[0], "holders are not the keys of step 1")
        if sorted(bundle.get("serve_nodes", [])) != sorted(SEATS): bad("C10", voices[0], "serve_nodes are not the keys of step 2")
        if len(cites(voices[0])) < len(H) + len(SEATS): bad("C10", voices[0], "the bundle cites fewer records than it seats")

        rc = charter.get("recovery_commitments") or {}                              # C11, C12
        if sorted(rc) != sorted(H): bad("C11", voices[0], "recovery commitments are not one for each holder")
        if not charter.get("halt_fuse_secs"): bad("C11", voices[0], "no halt fuse")
        if not {"infra:serve", "infra:attest"} <= set(charter.get("scope", [])): bad("C11", voices[0], "the scopes lack infra:serve or infra:attest")
        for t in sorted(set(charter.get("scope", [])) & OWNER_ONLY): bad("C11", voices[0], f"the charter carries {t}, which only an owner grants")
        vals = [json.dumps(v, sort_keys=True) for v in rc.values()]
        if len(set(vals)) != len(vals): bad("C12", voices[0], "two holders share a recovery commitment")

        for m in WITNESS_MEMBERS:                                                   # C13
            if m in charter or m in bundle: bad("C13", voices[0], f"{m} is written in a charter with witnessed mode off")
        for k, v in list(charter.items()) + list(bundle.items()):
            if v == 0 and not isinstance(v, bool): bad("C13", voices[0], f"{k} is written as zero")

        for v in voices:                                                            # C14
            if claims(v).get("sub") != bundle.get("family_key_id"): bad("C14", v, "sub is not the bundle's family_key_id")

        for s in S:                                                                 # C16
            if s["payload"].get("asserted_at", 0) > bundle.get("asserted_at", 0): bad("C16", s, "dated after the bundle")
    for s in S:
        pl = s["payload"]
        if "valid_until" in pl and not pl["valid_until"] > pl.get("asserted_at", 0): bad("C16", s, "valid_until is not later than asserted_at")

    HD = {h.get("identity_ref"): h for h in T.get("holders") or []}                 # C18, C19
    for h in H:
        e = HD.get(h)
        if e is None: bad("C18", None, f"the trace gives no custody entry for holder {h[-8:]}"); bad("C19", None, f"the trace gives no recovery commitment for holder {h[-8:]}"); continue
        ds = e.get("device_serial")
        if isinstance(ds, bool) or not (ds is None or isinstance(ds, int)): bad("C18", None, f"holder {h[-8:]}: the device serial is no integer")
        if ds is None and "malformed" in (e.get("device_serial_absent_reason") or "malformed: no reason given"):
            bad("C18", None, f"holder {h[-8:]}: {e.get('device_serial_absent_reason') or 'no serial and no reason given'}")
        try: in_charter = hx(charter["recovery_commitments"][h][1])
        except Exception: in_charter = None
        if not e.get("recovery_commitment") or e.get("recovery_commitment") != in_charter: bad("C19", None, f"holder {h[-8:]}: the commitment differs from the charter's")
    serials = [e["device_serial"] for e in HD.values() if isinstance(e.get("device_serial"), int)]
    if len(set(serials)) != len(serials): bad("C18", None, "two holders name one device serial (holder_device_shared)")
    signing = {c.get("commitment") for c in T.get("signing_key_commitments") or []}
    if not {c.get("identity_ref") for c in T.get("signing_key_commitments") or []} >= set(H) | set(SEATS): bad("C19", None, "the trace does not give a commitment over every holder's and seat's signing key")
    for h, e in HD.items():
        if e.get("recovery_commitment") in signing: bad("C19", None, f"holder {str(h)[-8:]}: the recovery commitment commits a signing key (recovery_commitment_is_holder_key)")

    ids = {s["_id"] for s in S if s.get("_id")}                                     # C17
    for s in S:
        if s.get("_disagree"): bad("C17", s, "the trace's decoding differs from the signed bytes: " + s["_disagree"])
        if ids:
            for c in cites(s):
                if c not in ids: bad("C17", s, f"cites {str(c)[:16]}, which is no statement of this trace")
    if bindings and rec_ids:
        for s in bindings:
            mine = next((r.get("_id") for r in seats_rec if iss(r) == iss(s)), None)
            if mine and mine not in cites(s): bad("C06", s, "the binding does not cite its own seat's key record")
    return out


def load(path):
    T = json.load(open(path)); base = os.path.dirname(os.path.abspath(path))
    for s in T["statements"]:
        raw = None
        if s.get("cose_hex"): raw = bytes.fromhex(s["cose_hex"])
        elif T.get("run_dir") and s.get("file") and os.path.exists(os.path.join(base, T["run_dir"], s["file"])):
            raw = open(os.path.join(base, T["run_dir"], s["file"]), "rb").read()
        if raw is None: continue
        try:
            prot, payload, sid = ids_from_bytes(raw); s["_id"] = sid
            if norm(payload) != s["payload"]: s["_disagree"] = "payload"
            elif prot.get(15, {}).get(1) != iss(s): s["_disagree"] = "iss"
            elif hashlib.sha256(raw).hexdigest() != s.get("sha256", hashlib.sha256(raw).hexdigest()): s["_disagree"] = "sha256"
        except Exception as e:
            s["_disagree"] = f"undecodable ({e})"
    return T


def verdict(T, at):
    res = check(T); k = EDITIONS.index(at)
    return {cid: fails for (cid, since, _cc, _t) in INVARIANTS for fails in [res[cid]] if EDITIONS.index(since) <= k}


# ---- plants: one mutation of a passing trace for each invariant; each must be caught -------------------------
def _first(T, kind, step=None): return of_kind(T, kind, step)[0]


def plants():
    def p(cid, name, f): return (cid, name, f)
    def drop_halt(T): T["statements"].remove(_first(T, "accord:invoke:constitutional"))
    def drop_voice(T): T["statements"].remove(of_kind(T, "ceg-genesis-bundle/2")[-1])
    def all_voices(T, f):
        for v in of_kind(T, "ceg-genesis-bundle/2"): f(v)
    def share_commitment(v):
        rc = v["payload"]["charter"]["recovery_commitments"]; ks = sorted(rc); rc[ks[1]] = copy.deepcopy(rc[ks[0]])
    def reorder(T):
        v = of_kind(T, "ceg-genesis-bundle/2")[0]; T["statements"].remove(v); T["statements"].insert(0, v)
    return [
        p("C01", "a statement under another algorithm", lambda T: _first(T, "key:record")["protected"].update(alg=-8)),
        p("C02", "a bundle voice before the records", reorder),
        p("C03", "an exp on a holder's record", lambda T: claims(_first(T, "key:record", 1)).update(exp=1)),
        p("C04", "a holder's post-quantum half on the token", lambda T: _first(T, "key:record", 1)["payload"]["attestation_evidence"].update(pq_custody="on_token")),
        p("C04", "a holder's record with a valid_until", lambda T: (_first(T, "key:record", 1)["payload"].update(valid_until=2 ** 41), claims(_first(T, "key:record", 1)).update(exp=2 ** 41 // 1000))),
        p("C05", "a seat's record that ends after two years", lambda T: (lambda s: (s["payload"].update(valid_until=s["payload"]["asserted_at"] + 2 * YEAR_MS), claims(s).update(exp=(s["payload"]["asserted_at"] + 2 * YEAR_MS) // 1000)))(_first(T, "key:record", 2))),
        p("C06", "an X-Wing key inside transport_destination", lambda T: _first(T, "identity:occurrence")["payload"]["transport_destination"].update(transit_xwing_pubkey={"hex": "00"})),
        p("C06", "a binding that cites nothing", lambda T: _first(T, "identity:occurrence")["payload"]["refs"]["also"].update(cites=[])),
        p("C07", "a seat with no tcp dial hint", lambda T: _first(T, "identity:occurrence")["payload"].update(dial_hints=[[2, {"hex": "00"}]])),
        p("C08", "a halt with a member outside the closed payload", lambda T: _first(T, "accord:invoke:constitutional")["payload"].update(reason="drill")),
        p("C08", "a holder with no halt", drop_halt),
        p("C09", "a bundle one holder did not sign", drop_voice),
        p("C10", "a bundle that names a prev", lambda T: all_voices(T, lambda v: v["payload"].update(prev=[2, [-16, {"hex": "00" * 32}]]))),
        p("C11", "a charter with no halt fuse", lambda T: all_voices(T, lambda v: v["payload"]["charter"].pop("halt_fuse_secs"))),
        p("C11", "a charter that carries a scope only an owner grants", lambda T: all_voices(T, lambda v: v["payload"]["charter"]["scope"].append("infra:network_presence"))),
        p("C12", "two holders sharing a recovery commitment", lambda T: all_voices(T, share_commitment)),
        p("C13", "a witness quorum written as zero", lambda T: all_voices(T, lambda v: v["payload"]["charter"].update(witness_quorum=0))),
        p("C13", "an attach window in a witnessed-off charter", lambda T: all_voices(T, lambda v: v["payload"]["charter"].update(attach_window_secs=604800))),
        p("C14", "a bundle voice with no sub", lambda T: all_voices(T, lambda v: claims(v).pop("sub", None))),
        p("C15", "a halt naming another lineage", lambda T: (lambda s: (s["payload"].update(accord_root="other"), claims(s).update(sub="other")))(_first(T, "accord:invoke:constitutional"))),
        p("C18", "two holders on one device", lambda T: T["holders"][1].update(device_serial=T["holders"][0]["device_serial"])),
        p("C18", "a holder whose device serial is malformed", lambda T: T["holders"][0].update(device_serial=None, device_serial_absent_reason="custody_serial_malformed: not one DER INTEGER")),
        p("C19", "a recovery key that is a holder's signing key", lambda T: (lambda c: (T["holders"][0].update(recovery_commitment=c), all_voices(T, lambda v: v["payload"]["charter"]["recovery_commitments"].__setitem__(T["holders"][0]["identity_ref"], [-16, {"hex": c}]))))(T["signing_key_commitments"][0]["commitment"])),
        p("C19", "a recovery commitment that is not the charter's", lambda T: T["holders"][0].update(recovery_commitment="00" * 32)),
        p("C16", "a record dated after the bundle", lambda T: (lambda s: (s["payload"].update(asserted_at=s["payload"]["asserted_at"] + 10 ** 7), claims(s).update(iat=(s["payload"]["asserted_at"]) // 1000)))(_first(T, "key:record", 1))),
    ]


def make_current(T):
    """A trace of an earlier edition, brought to the current one: the voices gain sub, the seats gain a tcp hint."""
    T = copy.deepcopy(T); fam = of_kind(T, "ceg-genesis-bundle/2")[0]["payload"]["family_key_id"]
    for v in of_kind(T, "ceg-genesis-bundle/2"): claims(v).setdefault("sub", fam)
    for b in of_kind(T, "identity:occurrence"): b["payload"].setdefault("dial_hints", [[TCP, {"hex": "01bb" + b"seat.example".hex()}]])
    for s in T["statements"]: s.pop("cose_hex", None); s.pop("_id", None); s.pop("_disagree", None)
    T["run_dir"] = None
    return T


def run_plants(T, at="rc22"):
    base = verdict(T, at)
    if any(base.values()): return [("-", "the trace given does not pass, so no plant can be judged", False)]
    res = []
    for cid, name, f in plants():
        M = copy.deepcopy(T); f(M); res.append((cid, name, bool(verdict(M, at).get(cid))))
    return res


def manifest():
    return {"_meta": {"source": "formal/ceremony/CEREMONY.md section 3, steps 1 to 4; formal/ceremony/check_trace.py",
                      "model": "formal/ceremony/ceremony.py (P1 to P11), formal/ceremony/Cutover.tla",
                      "trace": "statements: one entry per signed statement, in ceremony order: step, kind, index, protected (alg, content_type, kid, cwt_claims, typ, the row labels), payload, sha256, and cose_hex, the signed bytes. holders: for each holder, identity_ref, device_serial (the integer the custody leaf names, or null with device_serial_absent_reason) and recovery_commitment. signing_key_commitments: for each holder and seat, identity_ref and the commitment over its signing key",
                      "editions": EDITIONS},
            "steps": STEPS,
            "invariants": [{"id": i, "since": s, "cc": cc, "statement": t} for i, s, cc, t in INVARIANTS],
            "plants": [{"invariant": c, "plant": n} for c, n, _ in plants()]}


def main(argv):
    if "--write-manifest" in argv:
        json.dump(manifest(), open(MANIFEST, "w"), indent=1); open(MANIFEST, "a").write("\n")
        print(f"ceremony manifest: {len(STEPS)} steps, {len(INVARIANTS)} invariants, {len(plants())} plants; sha256 {hashlib.sha256(open(MANIFEST, 'rb').read()).hexdigest()}")
        return 0
    if "--check" in argv:
        want = json.dumps(manifest(), indent=1) + "\n"; errs = []
        if not os.path.exists(MANIFEST) or open(MANIFEST).read() != want: errs.append("manifests/ceremony.json is stale: run --write-manifest")
        T = load(SAMPLE); fails = {c: f for c, f in verdict(T, "rc22").items() if f}
        if fails: errs.append(f"the sample trace fails {sorted(fails)}")
        pr = run_plants(T); missed = [n for _c, n, ok in pr if not ok]
        if missed: errs.append("plants not caught: " + "; ".join(missed))
        seen = {c for c, _n, _ok in pr}
        uncovered = [i[0] for i in INVARIANTS if i[0] not in seen and i[0] != "C17"]
        if uncovered: errs.append(f"invariants with no plant: {uncovered}")
        for e in errs: print("ceremony trace: error: " + e)
        print(f"ceremony trace: {len(INVARIANTS)} invariants over the sample trace hold; plants caught {sum(ok for _c, _n, ok in pr)} of {len(pr)}; {len(errs)} error(s)")
        return 1 if errs else 0
    paths = [a for a in argv if not a.startswith("--") and a not in EDITIONS]
    if not paths: print(__doc__); return 1
    at = argv[argv.index("--at") + 1] if "--at" in argv else EDITIONS[-1]
    T = load(paths[0])
    if "--plants" in argv:
        pr = run_plants(T, at)
        for c, n, ok in pr: print(f"  {'caught' if ok else 'MISSED'}  {c}  {n}")
        return 0 if all(ok for _c, _n, ok in pr) else 1
    res = verdict(T, at); n_bad = 0
    decoded = sum(1 for s in T["statements"] if s.get("_id"))
    for cid, since, cc, text in INVARIANTS:
        if cid not in res: print(f"  skip  {cid}  (since {since})  {text}"); continue
        f = res[cid]; n_bad += bool(f)
        print(f"  {'FAIL' if f else 'ok  '}  {cid}  CC {cc}  {text}")
        for line in f: print(f"          {line}")
    print(f"ceremony trace: {len(T['statements'])} statements, {decoded} decoded from their signed bytes; at {at}: "
          f"{len(res) - n_bad} of {len(res)} invariants hold")
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
