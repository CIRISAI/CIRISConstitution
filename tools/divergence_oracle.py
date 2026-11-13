#!/usr/bin/env python3
"""
The kernel as a test oracle for divergences: one case (a list of rows in the kernel's row form), one ask (a named
answer for one target), one parameter (the cell of one family). The same rows are run under the text's parameter
and under the shipped parameter, and the two verdicts are compared. Nothing here is a rule of its own: every answer
is read off formal/causal_kernel (kept, concluded, the seat walk, the cut, the count over a named head).

Row form (JSON): every row has `id`, `kind`, `signer`, `names` (the ids it names) and `family`. Kinds:
    keyrec     a key's own record (`identity_type`, and `node` for a component of a node); admitted by possession
    offer, accept, withdraw, unseat, cosign
               the seat rows of formal/causal_kernel/seat.py, with its fields (`to`, `scope`, `obj`, `conf`,
               `under`, `cosigners`, `head`, `policy`, `cuts`, `on`)
    fam        a row of the family the parameter governs, or of another family the case needs; fields the gate reads:
               `subject`, `subjects`, `group`, `root`, `content`, `blob`, `for_key`, `binding`, `provenance`,
               `build_manifest_hash`, `head`, `leaf`, `ref`, `at` (a signed instant, read only by a shipped fold)
    landing, reversal, claim, trust
               a window's landing, a row voiding a notice, a source's statement, a reader's trust edge
A `withdraw` or `recant` naming a `fam` row of the governed family is judged by the parameter's lifecycle.

Parameter (JSON): {"family": F, "gate": DNF, "withdraws_by": DNF, "verbs": [...], "refuse": [...] (a refusal by the row
alone: withdraw_without_ref, missing_subject_digest),
"policy": {name: [kind, num, den]}, "audience": token, "fold": name, "owed": name, "window_secs": n}.
A DNF is a list of conjunctions of tokens; a row passes when every token of one conjunction holds. The tokens:
    any                     every signer
    registered              the signer's own key record is in the row's past
    type:T                  the signer's key record declares identity_type T
    self                    the signer is the row's subject
    subject_of_content      the signer is a subject of the content row the row names
    owner_of_subject        the signer is the one live owner of the subject (seat `owner` over it)
    seat:S@F                the signer stands in scope S over the object the row's field F names
    sealer                  the signer signed the blob the row names
    component_of_subject    the signer's key record names the row's subject as its node
    provenance_matches      the provenance row named is Rooted and its hash equals the row's build_manifest_hash
    grant_named             the row names a grant its subject signed whose scope is the row's `needs_scope`
    subject_grant_held      some held grant by the row's subject has that scope, named by the row or not
    not_subject             the signer is not the row's subject
    subjects_in:F           every subject the row names is a member at the head it names of the group its field F names
    count:P@F               the voices on the row, over the members at the head it names, meet policy P
                            (`protocol`: the policy the group's founding row declares)
    attester, subject, ref  (lifecycle) the withdrawer signed the target; is its subject; the withdraw carries a ref
Verdicts:
    state      admitted | concludes nothing | withdrawn | recanted | refused | waits
    stands     stands | does not stand
    audience   served | not served
    fold       the value the fold gives, as a string
    owed       the effects owed, joined by ", ", or "nothing"
    door       landed | not landed | pending
"""
import itertools
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "formal", "causal_kernel"))
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True
import causal_kernel as CK  # noqa: E402
import seat as SEAT         # noqa: E402
import claim as CLAIM       # noqa: E402
sys.dont_write_bytecode = _dwb
K = CK.K

TUPLE_FIELDS = ("names", "to", "cosigners", "head", "subjects", "options")
SLOT_FIELDS = ("on", "cuts")
ORDER_CAP = 720


def norm(r):
    """A row read back from JSON: the kernel compares tuples."""
    r = dict(r)
    for f in TUPLE_FIELDS:
        if isinstance(r.get(f), list): r[f] = tuple(r[f])
    for f in SLOT_FIELDS:
        if isinstance(r.get(f), (list, tuple)): r[f] = tuple(tuple(s) for s in r[f])
    return r


def plain(r):
    """A row as JSON writes it."""
    out = {}
    for k, v in r.items():
        if isinstance(v, (tuple, list)): out[k] = [list(x) if isinstance(x, tuple) else x for x in v]
        elif isinstance(v, frozenset): out[k] = sorted(v)
        else: out[k] = v
    return out


# ---- the gate ----------------------------------------------------------------------------------------------------
def _seats(P):
    return SEAT.Seats(CK.State(P, {q["id"]: True for q in P}))


def _keyrec(P, k):
    return [q for q in P if q["kind"] == "keyrec" and q["signer"] == k]


def _met(policy, yes, n, table):
    kind, num, den = K.rule(table, policy, ("unknown", 0, 0))
    if kind == "atleast": return n > 0 and yes * den >= num * n
    if kind == "strict": return yes * den > num * n
    if kind == "one": return yes >= 1
    return False


def token(t, r, P, past, table, target=None):
    by = {q["id"]: q for q in P}
    k = r["signer"]
    if t == "any": return True
    if t == "registered": return bool(_keyrec(P, k))
    if t.startswith("type:"): return any(q.get("identity_type") == t[5:] for q in _keyrec(P, k))
    if t == "self": return k == r.get("subject")
    if t == "not_subject": return k != r.get("subject")
    if t == "subject_of_content":
        c = by.get(r.get("content"))
        return c is not None and k in c.get("subjects", ())
    if t == "owner_of_subject": return _seats(P).one("owner", r.get("subject")) == k
    if t.startswith("seat:"):
        scope, field = t[5:].rsplit("@", 1)
        return _seats(P).stands(k, scope, r.get(field))
    if t == "sealer":
        b = by.get(r.get("blob"))
        return b is not None and b["signer"] == k
    if t == "component_of_subject": return any(q.get("node") == r.get("subject") for q in _keyrec(P, k))
    if t == "provenance_matches":
        p = by.get(r.get("provenance"))
        return p is not None and p.get("rooted") is True and p.get("hash") == r.get("build_manifest_hash")
    if t == "grant_named":
        g = by.get(r.get("grant"))
        return g is not None and g["signer"] == r.get("subject") and g.get("scope") == r.get("needs_scope")
    if t == "subject_grant_held":
        return any(q.get("kind") == "fam" and q["signer"] == r.get("subject") and q.get("scope") == r.get("needs_scope")
                   and q.get("family") == "consent:state:{stance}" for q in P)
    if t.startswith("count:"):
        pol, field = t[6:].rsplit("@", 1)
        g = by.get(r.get(field))
        if g is None: return False
        if pol == "protocol": pol = g.get("protocol", "unknown")
        mem = SEAT.members_at(P, past, g["id"], r.get("head", ()))
        return _met(pol, len(SEAT.voices(r, P) & mem), len(mem), table)
    if t == "attester": return target is not None and k == target["signer"]
    if t == "subject": return target is not None and (k == target.get("subject") or k in target.get("subjects", ()))
    if t == "ref": return bool(r.get("ref"))
    if t.startswith("subjects_in:"):
        g = r.get(t[12:])
        mem = SEAT.members_at(P, past, g, r.get("head", (g,)))
        return set(r.get("subjects", ())) <= set(mem)
    raise ValueError("unknown token " + t)


def dnf(clauses, r, P, past, table, target=None):
    return any(all(token(t, r, P, past, table, target) for t in c) for c in clauses)


TABLE0 = dict(SEAT.POLICY, strict=("strict", 1, 2), one=("one", 1, 1))


def make_rule(param, store=False):
    """The conclusion rule: the seat rule for seat rows, the parameter for rows of the governed family."""
    fam = param.get("family")
    table = dict(TABLE0, **{k: tuple(v) for k, v in (param.get("policy") or {}).items()})

    def rule(r, P, past):
        kind = r["kind"]
        by = {q["id"]: q for q in P}
        if kind in ("offer", "unseat", "accept", "cosign"): return SEAT.seat_rule(r, P, past, table=table)
        if kind in ("withdraw", "recant"):
            t = by.get(r.get("target"))
            if t is not None and t["kind"] == "fam":
                if t.get("family") == fam and "withdraws_by" in param:
                    return dnf(param["withdraws_by"], r, P, past, table, target=t)
                return r["signer"] == t["signer"]
            if kind == "withdraw": return SEAT.seat_rule(r, P, past, table=table)
            return t is not None and r["signer"] == t["signer"]
        if kind == "fam":
            if r.get("family") == fam and "gate" in param:
                g = param["gate"]
                if isinstance(g, dict): g = g.get(r.get("leaf"), g.get("*", [["any"]]))
                return dnf(g, r, P, past, table)
            return True
        return True
    return rule


def make_wf(param, rows):
    """The kept layer reads the row alone. A shipped refusal that reads another row is the divergence itself, so
    the shipped parameter may name one; the text's never does."""
    by = {r["id"]: r for r in rows}
    refuse = set(param.get("refuse") or ())
    verbs = param.get("verbs")

    def wf(r):
        if r.get("malformed"): return False
        t = by.get(r.get("target"))
        gov = t is not None and t.get("family") == param.get("family")
        if "withdraw_without_ref" in refuse and r["kind"] == "withdraw" and gov and not r.get("ref"): return False
        if "missing_subject_digest" in refuse and r["kind"] == "fam" and r.get("family") == param.get("family") \
                and not r.get("subject_digest"): return False
        if "names_no_grant" in refuse and r["kind"] == "fam" and r.get("family") == param.get("family") \
                and not r.get("grant"): return False
        if verbs is not None and r["kind"] == "recant" and gov and "recant" not in verbs: return False
        return True
    return wf


# ---- the named answers -------------------------------------------------------------------------------------------
def state_of(S, offered, wf, rid):
    if rid not in S.by:
        r = next((x for x in offered if x["id"] == rid), None)
        return "refused" if r is not None and not wf(r) else "waits"
    if not S.C.get(rid): return "concludes nothing"
    for w in S.Cs:
        if w.get("target") == rid and w["kind"] in ("withdraw", "recant"):
            return "withdrawn" if w["kind"] == "withdraw" else "recanted"
    return "admitted"


def audience_set(S, param, r):
    tok = param["audience"]
    seats = SEAT.Seats(S)
    if tok == "everyone": return None
    if tok == "addressed": return {r["signer"], r.get("for_key")}
    if tok == "cohort_plus_subjects":
        return set(seats.holders("member", r.get("group"))) | set(r.get("subjects", ())) | {r["signer"]}
    if tok == "attester_relayed":
        b = S.by.get(r.get("binding"))
        if b is None or not S.C.get(b["id"]): return {r["signer"]}
        if b.get("tier") == "federation": return None
        return set(seats.holders("member", b.get("group"))) | {r["signer"], b["signer"]}
    raise ValueError(tok)


def _latest(rows, key=lambda r: (r["at"], r["id"])):
    return max(rows, key=key) if rows else None


def fold(S, param, ask):
    """The folds the seven rankings and the readings name, each a function of the concluded rows. The shipped
    folds read a signed instant or a digest across signers; that is the divergence they carry."""
    name, mode, Cs = param["fold"], param["mode"], S.Cs
    if name == "consent_capture":
        bound = ask["bound"]
        acts = [r for r in Cs if r["kind"] == "fam" and r.get("leaf") in ("grant", "revoke")]
        if mode == "per_party":        # CC 3.3.1: each party's rows folded apart; R is that party's own latest revocation
            def live(p):
                own = [r for r in acts if r["signer"] == p]
                rv = [r["at"] for r in own if r["leaf"] == "revoke"]
                R = max(rv) if rv else float("-inf")
                return any(r["leaf"] == "grant" and r["at"] > R for r in own)
            return "captured" if all(live(p) for p in bound) else "not captured"
        rv = [r["at"] for r in acts if r["leaf"] == "revoke"]       # shipped: one boundary over every party's rows
        R = max(rv) if rv else float("-inf")
        g = _latest([r for r in acts if r["leaf"] == "grant" and r["at"] > R])
        return "captured" if g is not None else "not captured"
    if name == "revocation_bound":
        revs = [r for r in Cs if r["kind"] == "fam" and r.get("leaf") == "revocation" and r.get("subject") == ask["key"]]
        if mode == "minimum": bound = min(r["revoked_after"] for r in revs)
        else: bound = max(revs, key=lambda r: (r["weight"], r["at"], [-ord(c) for c in r["id"]]))["revoked_after"]
        return "counts" if ask["signed_at"] < bound else "does not count"
    if name == "licence_merge":
        ls = [r for r in Cs if r["kind"] == "fam" and r.get("leaf") == "licence"]
        rank = {"active": 0, "suspended": 1, "revoked": 2}
        if mode == "weight_then_state":
            w = max(r["weight"] for r in ls)
            return max((rank[r["status"]], r["status"]) for r in ls if r["weight"] == w)[1]
        return max(ls, key=lambda r: (r["weight"], r["at"], [-ord(c) for c in r["id"]]))["status"]
    if name == "quarantine":
        ms = [r for r in Cs if r["kind"] == "fam" and r.get("leaf") in ("withhold", "release")]
        if mode == "release_names":
            held = [w for w in ms if w["leaf"] == "withhold"
                    and not any(x["leaf"] == "release" and w["id"] in x["names"] for x in ms)]
            return "withheld" if held else "released"
        top = max(r["at"] for r in ms)
        at_top = {r["leaf"] for r in ms if r["at"] == top}
        return "withheld" if "withhold" in at_top else "released"
    if name == "acceptance":
        acc = [r for r in Cs if r["kind"] == "fam" and r.get("leaf") == "acceptance"]
        size = max(len(r["ballots"]) for r in acc)
        top = [r for r in acc if len(r["ballots"]) == size]
        if mode == "larger_then_nobody":
            seated = {r["seats"] for r in top}
            return "seats " + top[0]["seats"] if len(seated) == 1 else "seats nobody"
        return "seats " + min(top, key=lambda r: r["id"])["seats"]
    if name == "enumerated":
        if mode == "reader_trust":
            got = CLAIM.read(S, ask["reader"], ask["subject"], ask["dim"])
            vals = sorted({str(v) for v in got.values()})
            return "|".join(vals) if vals else "nothing"
        cs = [r for r in Cs if r["kind"] == "claim" and r.get("subject") == ask["subject"] and r.get("dim") == ask["dim"]]
        return str(_latest(cs)["value"]) if cs else "nothing"
    if name == "age_band":
        order = {"minor": 0, "adult": 1}
        cs = [r for r in Cs if r["kind"] == "fam" and r.get("subject") == ask["subject"] and r.get("leaf") in ("witness", "self")]
        wit = [r for r in cs if r["leaf"] == "witness"]
        slf = [r for r in cs if r["leaf"] == "self"]
        if mode == "witness_then_self_lowers":
            band = max((r["band"] for r in wit), key=order.get) if wit else None
            for r in slf:
                if band is None or order[r["band"]] < order[band]: band = r["band"]
            return band or "nothing"
        rank = {"self": 0, "provider": 1, "government": 2}
        return max(cs, key=lambda r: rank[r.get("level", "self")])["band"]
    if name == "stewards_of":
        s = SEAT.Seats(S)
        one = s.one("owner", ask["key"])
        out = {one} if one is not None else set()
        if mode == "binding_and_occurrence":
            out |= {r["signer"] for r in Cs if r["kind"] == "fam" and r.get("leaf") == "identity_occurrence"
                    and r.get("subject") == ask["key"]}
        return ",".join(sorted(out)) or "nobody"
    raise ValueError(name)


def owed(S, param, ask):
    name = param["owed"]
    if name == "withhold_close":
        out = []
        for l in S.Cs:
            if l["kind"] != "landing" or l.get("says") != "withhold": continue
            n = l["names"][0]
            voided = any(v["kind"] == "reversal" and n in v["names"] for v in S.Cs)
            if not (param.get("unless") == "notice_voided" and voided): out.append("destroy_bytes")
        return ", ".join(out) or "nothing"
    if name == "report_window":
        out = []
        w = param.get("window_secs")
        for r in S.Cs:
            if r["kind"] == "fam" and r.get("family") == param["family"] and w is not None and ask["now"] >= r["seen_at"] + w:
                out.append("read withdrawn " + r["id"])
        return ", ".join(out) or "nothing"
    raise ValueError(name)


def door_count(S, param, ask):
    """An admission by invitation over the window rows of formal/causal_kernel/window.py: the proposal (`open`), the
    answers, a receipt and a landing. The yes voices are the proposer and every approving answer the landing names.
    floor_two_with_invitee  the text (CC 3.1.3.2, CC 4.5.13): two voices at least, the invitee's acceptance among them
    policy_decide           the policy table's own decision function (tools/build_governance_policy.py `decide`) over
                            the members at the head the proposal names, as its vectors count: approvals among members"""
    p = S.by[ask["proposal"]]
    lands = [l for l in S.Cs if l["kind"] == "landing" and l.get("of") == p["id"]]
    if not lands: return "pending"
    l = lands[0]
    elapsed = l["at"] - S.by[l["receipt"]]["at"]
    mem = SEAT.members_at(S.Cs, lambda x, y: x in S.anc[y], p["obj"], p["head"])
    yes = {p["signer"]} | {a["signer"] for a in S.Cs if a["kind"] == "answer" and a.get("of") == p["id"]
                           and a.get("says") == "approve" and a["id"] in S.anc[l["id"]]}
    if param["count"] == "floor_two_with_invitee":
        return "landed" if len(yes & (set(mem) | {p["target"]})) >= 2 and p["target"] in yes else "not landed"
    if param["count"] == "policy_decide":
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        _d, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        import build_governance_policy as G
        sys.dont_write_bytecode = _d
        row = {r["family"]: r for r in G.load()}[param["door"]]
        v = G.decide(row, len(mem), len(yes & set(mem)), 0, elapsed, p["target"] in yes)[0]
        return {"lands": "landed", "cancelled": "not landed"}.get(v, v)
    raise ValueError(param["count"])


def door_model(rows, ask):
    """The verdict of formal/causal_kernel/door.py on the same rows, recorded beside the oracle's."""
    import door as D
    D.rebuild()
    S = CK.concluded(CK.kept([norm(r) for r in rows]), D.rule)
    return D.outcome(S, ask["proposal"])


def answer(S, offered, wf, param, ask):
    a = ask["answer"]
    if a == "state": return state_of(S, offered, wf, ask["target"])
    if a == "stands": return "stands" if SEAT.Seats(S).stands(ask["key"], ask["scope"], ask["obj"]) else "does not stand"
    if a == "audience":
        r = S.by.get(ask["target"])
        if r is None or not S.C.get(r["id"]): return "not served"
        aud = audience_set(S, param, r)
        return "served" if aud is None or ask["reader"] in aud else "not served"
    if a == "fold": return fold(S, param, ask)
    if a == "owed": return owed(S, param, ask)
    if a == "door": return door_count(S, param, ask)
    raise ValueError(a)


# ---- running -----------------------------------------------------------------------------------------------------
def run_set(rows, param, ask):
    """The verdict as a function of the set: kept, then concluded, then the named answer."""
    rows = [norm(r) for r in rows]
    wf = make_wf(param, rows)
    S = CK.concluded(CK.kept(rows, wf), make_rule(param))
    return answer(S, rows, wf, param, ask)


def run_order(order, param, ask, store=False):
    """The verdict as a node reaches it, rows arriving in `order`. The kernel concludes a row against its own past
    (causal_kernel.arrive). With store=True the row is judged once, at admission, against every row held so far,
    as a store that judges on arrival does: that is not a function of the rows (KERNEL.md section 2)."""
    order = [norm(r) for r in order]
    wf = make_wf(param, order)
    rule = make_rule(param)
    if not store:
        S = CK.arrive(order, rule, wf=wf)
        return answer(S, order, wf, param, ask)
    held, ids, waiting, C, anc = [], {}, [], {}, {}
    for r in order:
        waiting.append(r)
        moved = True
        while moved:
            moved = False
            for w in list(waiting):
                if wf(w) and all(n in ids for n in w["names"]):
                    waiting.remove(w); ids[w["id"]] = w; held.append(w)
                    anc[w["id"]] = CK.ancestors(ids, w["id"])
                    P = [q for q in held[:-1] if C[q["id"]]]           # everything held, named or not
                    C[w["id"]] = bool(rule(w, P, lambda x, y: x in anc.get(y, ())))
                    moved = True
    return answer(CK.State(held, C), order, wf, param, ask)


def orders(rows, cap=ORDER_CAP):
    n = len(rows)
    total = 1
    for i in range(2, n + 1): total *= i
    if total <= cap: return list(itertools.permutations(rows)), total
    rnd = random.Random(n * 7919 + total % 104729)
    out = {tuple(r["id"] for r in rows): tuple(rows), tuple(r["id"] for r in reversed(rows)): tuple(reversed(rows))}
    while len(out) < cap:
        p = list(rows); rnd.shuffle(p)
        out.setdefault(tuple(r["id"] for r in p), tuple(p))
    return list(out.values()), total


def run_all(rows, text, shipped, ask):
    """Both verdicts by the set, then every arrival order (to the cap) under the kernel and under a store that judges
    on arrival. Returns a dict the manifest records."""
    kt, ks = run_set(rows, text, ask), run_set(rows, shipped, ask)
    os_, total = orders(rows)
    k_orders = {run_order(o, text, ask) for o in os_}
    s_kernel = {run_order(o, shipped, ask) for o in os_}
    s_store = {run_order(o, shipped, ask, store=True) for o in os_}
    t_store = {run_order(o, text, ask, store=True) for o in os_}
    return {"expect_kernel": kt, "expect_shipped": ks, "orders_run": len(os_), "orders_total": total,
            "kernel_verdicts_over_orders": sorted(k_orders), "shipped_verdicts_over_orders": sorted(s_kernel),
            "shipped_on_arrival_verdicts": sorted(s_store), "text_on_arrival_verdicts": sorted(t_store)}
