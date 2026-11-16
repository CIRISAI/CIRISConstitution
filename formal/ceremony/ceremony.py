"""
ceremony.py: the edition-2 ceremony (the cutover to the CBOR and COSE signed object) as rows of the kernel.

It runs on formal/causal_kernel (imported in place): `kept` is the door, `ancestors` and `frontier` are the order, and
key_end's door bounds a key record. Nothing here ranks rows by an instant, an arrival or a digest, except where a
planted break says it does.

Rows (dicts of causal_kernel.row) carry `form`: "e1" for the earlier JSON form (CC 8.11), "e2" for this form (CC 2.6.1).

    rec      a key record. `key` is the key id, `mat` the pair of halves (ed, pq), `typ` its identity type. A record of
             this form that names an earlier record of the same halves CARRIES that key; one that names an earlier
             record and carries that key's signature (`succ_of`, `sigs`) ROTATES it to fresh halves.
    genesis  the earlier-form genesis bundle. `roster` is the accord's holders by earlier key, `seats` the serve nodes.
    bundle2  a `ceg-genesis-bundle/2`. The first is the ceremony row. `voices` are the holders' statements over it.
    ack      the acknowledgement of a scope the ceremony carries over, with `carried`: the earlier-form rows of the scope.
    rebind   `transport:canonical_rebind` for `seat`, carrying the X-Wing transit key `xw`, counted by the holders.
    td       a seat's own `transport_destination` carrying `xw`. A seat's own rotation is refused (CC 3.3.6.2).
    confer   the canonical conferral: the holders' count over a seat's key record of this form (CC 4.2.1).
    roster   a community's roster version: `members` (persons), counted over the members at the head it names.
    ob       an owner-binding, owner `owner` over `target`, with both voices (the target's cosignature, CC 3.2).
    edge     a trust acceptance edge to the accord, by a person.
    halt     an accord invocation by one holder; `halves` are the halves its signature carries.
    resume   `accord:lifecycle:active`, counted, naming the halt.
    revoke   a key's own revocation.
    post     any other row; `at` is its signed instant, read only by a planted break.

A reader is (upgraded, pin). A reader that has not upgraded cannot read this form: such rows are malformed to it.
`pin` is the object id of the ceremony row the reader acknowledges (CC 5.3.4); a reader without one holds tips.

The answers (derived): the cut, the earlier rows accepted, each key's forward liveness, the person a key speaks for,
the counted acts, a seat's transit key in force, an agent's steward, whether an agent may act, a community's members,
and the halts a reader honours.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CKDIR = os.path.join(os.path.dirname(HERE), "causal_kernel")
sys.dont_write_bytecode = True
sys.path.insert(0, CKDIR)
import causal_kernel as CK  # noqa: E402
import key_end as KE        # noqa: E402

K = CK.K
INF = float("inf")
CEIL = KE.CEIL                     # key_record_max_secs on key_end's grid (365 days)
MUT = set()                        # planted breaks, switched on by the check
CEREMONY_COUNT = ["all"]           # "all": every holder signs the fresh genesis (CC 5.3.4); "majority": a strict majority


def row(id, kind, signer, names=(), form="e2", **kw):
    return CK.row(id, kind, signer, names, form=form, **kw)


def rec(id, key, mat, typ, form="e2", vf=0, vu=None, names=(), succ_of=None, sigs=None, custody=None):
    s = frozenset(sigs if sigs is not None else ({key} | ({succ_of} if succ_of else set())))
    return row(id, "rec", key, names, form, key=key, mat=mat, typ=typ, vf=vf, vu=vu, succ_of=succ_of, sigs=s,
               custody=custody or {})


# ---- the door: the row alone ----------------------------------------------------------------------------
def wf(reader):
    def door(r):
        if r["form"] == "e2" and not reader["upgraded"]:
            return False                                   # a node of the earlier form cannot read this form
        if r["kind"] == "rec" and r["form"] == "e2":
            k = {"kind": "rec", "typ": r["typ"], "vf": r["vf"], "vu": r["vu"], "room": False,
                 "succ_of": r["succ_of"], "sigs": r["sigs"], "key": r["key"]}
            return KE.WF(k)                                # CC 2.4.1.1: the end rule, read from the record alone
        if r["kind"] == "rec" and r["form"] == "e1":
            return True                                    # an earlier record verifies as it was signed (CC 8.11)
        return True
    return door


# ---- the cut ---------------------------------------------------------------------------------------------
def past_c(by, cr):
    """The ceremony row's past (CC 2.6.1.12): the rows it names and the rows they name, by a chain of names. An
    earlier-form object names nothing by digest, so a chain enters the earlier form only at its last hop: by a
    direct name, or as a leaf of a `carried` root of an acknowledgement in the past."""
    seen, stack = set(), [cr]
    while stack:
        i = stack.pop()
        if i in seen or i not in by:
            continue
        seen.add(i)
        r = by[i]
        if r["form"] == "e1" and "inner_names" not in MUT:
            continue                                       # the last hop: an earlier object extends no chain
        stack.extend(r["names"])
        if r["kind"] == "ack":
            if "inner_names" in MUT:                       # PLANT: an earlier row's own references extend the past
                stack.extend(r["carried"])
            else:
                seen |= set(x for x in r["carried"] if x in by)
    seen.discard(cr)
    return seen


def holder_roster(by):
    g = [r for r in by.values() if r["kind"] == "genesis" and r["form"] == "e1"]
    return frozenset(g[0]["roster"]) if g else frozenset()


def links(by, accepted_e1):
    """The person (an earlier key, or a key first minted in this form) each key of this form speaks for. A record of
    this form carries an earlier key when it names that key's accepted earlier record and holds the same halves, or
    rotates it when it names that record and carries that key's signature. Two keys of this form for one earlier key
    hand on nothing until a row names both (CC 2.4.1.1): both are contested."""
    out, claim = {}, {}
    for r in by.values():
        if r["kind"] != "rec" or r["form"] != "e2":
            continue
        e = [by[n] for n in r["names"] if n in by and by[n]["kind"] == "rec" and by[n]["form"] == "e1"
             and n in accepted_e1]
        tied = None
        for p in e:
            if "no_continuity" in MUT:
                break
            if r["mat"] == p["mat"] or (r["succ_of"] == p["key"] and p["key"] in r["sigs"]):
                tied = p["key"]
        if tied is None:
            out[r["key"]] = r["key"]
        else:
            claim.setdefault(tied, set()).add(r["key"])
    for p, ks in claim.items():
        if len(ks) == 1 or "count_keys" in MUT:
            for k in ks:
                out[k] = p
        else:
            for k in ks:
                out[k] = ("contested", p)
    return out


def _fwd_records(by, k):
    return [r for r in by.values() if r["kind"] == "rec" and r["form"] == "e2" and r["key"] == k]


def live_fwd(by, A, k, now, person=None):
    """CC 2.4.1.1: a key is live in this form only by a key record of this form that covers now, unless the key has
    revoked itself by then. A revocation of the earlier form by the same key, accepted, counts against it."""
    p = person.get(k, k) if person else k
    revs = [r for r in A.values() if r["kind"] == "revoke" and (r["key"] == k or r["key"] == p)]
    revs = [r for r in revs if r["signer"] == r["key"] or "third_party_ends" in MUT]
    if "ignore_earlier_revocation" in MUT:
        revs = [r for r in revs if r["form"] == "e2"]
    if revs:
        return False
    for r in _fwd_records(A, k):
        vu = INF if r["vu"] is None else r["vu"]
        if r["vf"] <= now < vu:
            return True
    if "ceremony_carries_keys" in MUT:          # PLANT: an earlier record in the past makes its key live forward
        if any(r["kind"] == "rec" and r["form"] == "e1" and r["key"] == k for r in A.values()):
            return True
    if "named_makes_live" in MUT:               # PLANT: another key's row naming the record makes the key live
        for r in A.values():
            if r["kind"] == "rec" and r["key"] == k and any(r["id"] in q["names"] and q["signer"] != k
                                                            for q in A.values() if q["form"] == "e2"):
                return True
    return False


def voice_persons(row_, A, person, live, roster):
    """The distinct persons on the roster whose statements over `row_` count. A statement of this form counts when its
    key is live in this form; an earlier-form statement counts as its earlier key. One person is one voice."""
    out = set()
    for k in row_["voices"]:
        if row_["form"] == "e2":
            if not live(k):
                continue
            p = person.get(k, k)
            if isinstance(p, tuple):
                continue
        else:
            p = k
        if p in roster:
            out.add(k if "count_keys" in MUT else p)
    return out


COUNTED = ("bundle2", "rebind", "confer", "resume")


def need(roster, kind="majority"):
    n = len(roster)
    return n if kind == "all" else n // 2 + 1


def answers(rows, reader, now=5, first=None):
    """Every answer a reader gives over the rows it holds. `first` maps a row id to the position at which the reader
    first held it; only a planted break reads it."""
    first = first or {}
    kept = CK.kept(rows, wf(reader))
    by = {r["id"]: r for r in kept}
    e1 = {i: r for i, r in by.items() if r["form"] == "e1"}
    roster = holder_roster(by)

    # the ceremony rows a reader counts: bundles of this form naming the earlier genesis, counted by the holders
    crs = []
    for r in by.values():
        if r["kind"] != "bundle2" or r.get("version") != 1:
            continue
        pc = past_c(by, r["id"])
        acc = {i for i in e1 if i in pc}
        per = links({i: by[i] for i in pc | {r["id"]}}, acc)
        lv = lambda k, pc=pc, per=per: live_fwd({i: by[i] for i in pc}, {i: by[i] for i in pc}, k, now, per)
        if len(voice_persons(r, by, per, lv, roster)) >= need(roster, CEREMONY_COUNT[0]):
            crs.append(r["id"])
    pin = reader.get("pin")
    if pin in crs and "pinned_ignored" not in MUT:
        cut = [pin]
    elif "fork_first" in MUT and crs:
        cut = [min(crs, key=lambda i: first.get(i, 0))]
    else:
        cut = sorted(crs)
    void = [c for c in crs if c not in cut]

    # the earlier rows accepted
    if not cut:
        acc = set(e1)
    else:
        pasts = [past_c(by, c) for c in cut]
        P = set.union(*pasts) if "fork_union" in MUT else set.intersection(*pasts)
        acc = {i for i in e1 if i in P}
        if "by_instant" in MUT:
            at = min(by[c].get("at", 0) for c in cut)
            acc |= {i for i in e1 if e1[i].get("at", 0) < at}
        if "by_arrival" in MUT:
            f = min(first.get(c, 0) for c in cut)
            acc |= {i for i in e1 if first.get(i, 0) < f}
        if "drop_earlier_after_cut" in MUT:
            acc = {i for i in acc if e1[i]["kind"] in ("genesis", "rec", "ack")}
    A = {i: r for i, r in by.items() if (r["form"] == "e2" and i not in void) or i in acc}
    person = links(A, acc)
    lv = lambda k: live_fwd(A, A, k, now, person)

    def live(k):
        if any(r["kind"] == "rec" and r["form"] == "e2" and r["key"] == k for r in A.values()):
            return lv(k)
        if not cut:                                  # before the ceremony row, an earlier record gives standing
            return any(r["kind"] == "rec" and r["key"] == k for r in A.values()) and not any(
                r["kind"] == "revoke" and r["key"] == k for r in A.values())
        return lv(k)

    def speaks(p):
        """The keys that speak for person p, live."""
        return {k for k, q in person.items() if q == p and lv(k)} | ({p} if not cut and live(p) else set())

    R = roster
    if "roster_shrinks" in MUT and cut:
        R = frozenset(p for p in roster if speaks(p))
    M = need(R)

    def counted(r):
        return len(voice_persons(r, A, person, live, R)) >= (1 if "one_holder_rebind" in MUT and r["kind"] == "rebind" else M)

    # a seat's transit key in force: the counted re-binds and the bundle's authorised rows, one value or none
    seats = {}
    gen = [r for r in by.values() if r["kind"] == "genesis"]
    for s in sorted(gen[0]["seats"] if gen else ()):
        cands = [r for r in A.values() if r["kind"] == "rebind" and r["seat"] == s and counted(r)]
        cands += [by[n] for c in cut for n in by[c]["names"] if n in A and A[n]["kind"] == "td" and A[n]["seat"] == s]
        if "seat_alone_td" in MUT:
            cands += [r for r in A.values() if r["kind"] == "td" and r["seat"] == s]
        if "rebind_outside_past" in MUT:
            cands += [r for r in e1.values() if r["kind"] == "rebind" and r["seat"] == s]
        anc = {r["id"]: CK.ancestors(by, r["id"]) for r in cands}
        top = K.frontier(anc, cands) if cands else []
        vals = sorted({r["xw"] for r in top})
        seats[s] = vals[0] if len(vals) == 1 or ("pick_one" in MUT and vals) else None

    # an agent's steward: owner-bindings with both voices, read over persons
    def steward(target):
        owners = set()
        for r in A.values():
            if r["kind"] != "ob":
                continue
            tp = person.get(r["target"], r["target"]) if r["form"] == "e2" else r["target"]
            op = person.get(r["owner"], r["owner"]) if r["form"] == "e2" else r["owner"]
            if tp == target and {r["owner"], r["target"]} <= set(r["voices"]):
                owners.add(op)
        return next(iter(owners)) if len(owners) == 1 else None

    def edge_of(p):
        return any(r["kind"] == "edge" and (r["signer"] == p or person.get(r["signer"]) == p)
                   and (r["form"] == "e1" or lv(r["signer"])) for r in A.values())

    agents = sorted({r["key"] for r in by.values() if r["kind"] == "rec" and r["form"] == "e1" and r["typ"] == "agent"})

    def may_act(a):
        ks = speaks(a)
        st = steward(a)
        return bool(ks) and st is not None and edge_of(st) if "act_without_steward" not in MUT else bool(ks)

    # a community's members, at each head
    def members():
        vs = [r for r in A.values() if r["kind"] == "roster"]
        if not vs:
            return frozenset()
        anc = {r["id"]: CK.ancestors(by, r["id"]) for r in vs}
        ok = {}
        for r in sorted(vs, key=lambda r: len(anc[r["id"]])):
            heads = [n for n in r["names"] if n in A and A[n]["kind"] == "roster"]
            if not heads:
                ok[r["id"]] = set(r["voices"]) >= set(r["members"])          # a founding seats who signed it
                continue
            base = set.intersection(*[set(A[h]["members"]) for h in heads if ok.get(h)]) if all(ok.get(h) for h in heads) else None
            if base is None:
                ok[r["id"]] = False
                continue
            vp = set()
            for k in r["voices"]:
                if r["form"] == "e2":
                    if not live(k):
                        continue
                    p = person.get(k, k)
                else:
                    p = k
                if p in base:
                    vp.add(p)
            ok[r["id"]] = len(vp) >= len(base) // 2 + 1
        good = [r for r in vs if ok[r["id"]]]
        tips = K.frontier({r["id"]: anc[r["id"]] for r in good}, good)
        m = frozenset.intersection(*[frozenset(r["members"]) for r in tips]) if tips else frozenset()
        if "silence_retires" in MUT and cut:
            m = frozenset(p for p in m if speaks(p))
        return m

    # the halts a reader honours: one holder's row, its composite whole
    honoured = set()
    for r in A.values():
        if r["kind"] != "halt":
            continue
        if r["form"] == "e1":
            honoured.add(r["id"])
            continue
        p = person.get(r["signer"], r["signer"])
        whole = r["halves"] >= {"ed", "pq"} or ("one_half_verifies" in MUT and "ed" in r["halves"])
        if lv(r["signer"]) and p in R and whole:
            honoured.add(r["id"])
    if "earlier_halt_after" in MUT:
        honoured |= {i for i, r in e1.items() if r["kind"] == "halt"}
    resumed = {h for h in honoured if any(r["kind"] == "resume" and h in r["names"] and counted(r) for r in A.values())}

    keys = sorted({r["key"] for r in by.values() if r["kind"] == "rec"})
    return {
        "cut": tuple(cut), "void": tuple(sorted(void)),
        "accepted": frozenset(acc),
        "live": frozenset(k for k in keys if live(k)),
        "person": tuple(sorted((k, str(p)) for k, p in person.items())),
        "roster": frozenset(R),
        "counted": frozenset(i for i, r in A.items() if r["kind"] in COUNTED and counted(r)),
        "seats": tuple(sorted(seats.items())),
        "steward": tuple((a, steward(a)) for a in agents),
        "may_act": tuple((a, may_act(a)) for a in agents),
        "members": members(),
        "honoured": frozenset(honoured), "resumed": frozenset(resumed),
    }
