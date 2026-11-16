"""
ceremony.py: the genesis of this edition, a clean mesh, as rows of the kernel.

It runs on formal/causal_kernel (imported in place): `kept` is the door, `ancestors` and `frontier` are the order, and
key_end's door bounds a key record. Nothing here ranks rows by an instant, an arrival or a digest, except where a
planted break says it does.

The ruling: nothing carries. The genesis of this form is a fresh genesis. No row of this form names an object of the
earlier form, and no object of the earlier form gives standing to anything. Every key record, binding, community,
edge and pre-signed halt is signed anew in this form. A node of this form reads this form only.

Rows (dicts of causal_kernel.row) carry `form`: "e1" for the earlier JSON form (CC 8.11), "e2" for this form (CC 2.6.1).

    rec      a key record. `key`, `typ`, `vf`, `vu`; `as_` names the person an earlier key belonged to, read only by
             planted breaks that carry something across.
    bundle2  a `ceg-genesis-bundle/2` with no `prev`: a genesis. `roster` is its holders' keys, `voices` the statements.
    rebind   `transport:canonical_rebind` for `seat`, carrying `xw`, counted by the holders.
    td       a seat's `transport_destination` carrying `xw`; the genesis names the seats' bindings.
    confer   a counted act of the holders (the canonical conferral, or any other counted act).
    resume   `accord:lifecycle:active`, counted, naming a halt.
    ob       an owner-binding, `owner` over `target`, with both voices (the target's cosignature, CC 3.2).
    edge     a trust acceptance edge to the accord, by a person.
    roster   a community's founding record: `members`, each of whom signs it.
    halt     an accord invocation by one holder; `halves` are the halves its signature carries.
    revoke   a revocation of `key`, signed by `signer`.
    post     any other row.

A reader is (upgraded, pin). A reader that has not upgraded reads only the earlier form. `pin` is the object id of
the genesis the reader acknowledges (CC 5.3.4); a reader with none holds every genesis it verifies as tips.
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
MUT = set()                        # planted breaks, switched on by the check
COUNTED = ("bundle2", "rebind", "confer", "resume")


def row(id, kind, signer, names=(), form="e2", **kw):
    return CK.row(id, kind, signer, names, form=form, **kw)


def rec(id, key, typ, form="e2", vf=0, vu=None, names=(), as_=None):
    return row(id, "rec", key, names, form, key=key, typ=typ, vf=vf, vu=vu, succ_of=None,
               sigs=frozenset({key}), as_=as_)


EARLIER_PLANTS = ("earlier_until_genesis", "earlier_named", "by_arrival", "earlier_record_live", "earlier_votes",
                  "earlier_rebind", "earlier_binding", "earlier_halt", "earlier_roster")


def wf(reader):
    def door(r):
        if not reader["upgraded"]:
            return r["form"] == "e1"                       # a node of the earlier mesh reads only its own form
        if r["form"] == "e1":
            # a node of this form refuses the earlier form; a plant keeps it, to be read by that plant
            return bool(MUT & set(EARLIER_PLANTS))
        if r["kind"] == "rec":
            k = {"kind": "rec", "typ": r["typ"], "vf": r["vf"], "vu": r["vu"], "room": False,
                 "succ_of": None, "sigs": r["sigs"], "key": r["key"]}
            return KE.WF(k)                                # CC 2.4.1.1: the end rule, read from the record alone
        return True
    return door


def answers(rows, reader, now=5, first=None):
    """Every answer a reader gives over the rows it holds. `first` maps a row id to the position at which the reader
    first held it; only a planted break reads it."""
    first = first or {}
    door = wf(reader)
    if reader["upgraded"] and "earlier_named" not in MUT:
        e1ids = {r["id"] for r in rows if r["form"] == "e1"}
        door0 = door
        door = lambda r: door0(r) and not (r["form"] == "e2" and set(r["names"]) & e1ids)   # a row-ref is edition 2
    kept = CK.kept(rows, door)
    by = {r["id"]: r for r in kept}
    fwd = {i: r for i, r in by.items() if r["form"] == "e2"}
    e1 = {i: r for i, r in by.items() if r["form"] == "e1"}

    def recs(k):
        return [r for r in fwd.values() if r["kind"] == "rec" and r["key"] == k]

    # the geneses a reader verifies: every key the bundle lists as a holder signed it, under a record it names
    gens = []
    for g in fwd.values():
        if g["kind"] != "bundle2" or g.get("prev") is not None:
            continue
        named = {by[n]["key"] for n in g["names"] if n in by and by[n]["kind"] == "rec"}
        signed = set(g["voices"]) & set(g["roster"]) & named
        need = len(g["roster"]) if "genesis_majority" not in MUT else len(g["roster"]) // 2 + 1
        if len(signed) >= need:
            gens.append(g["id"])
    pin = reader.get("pin")
    if pin in gens and "pinned_ignored" not in MUT:
        cut = [pin]
    elif "fork_first" in MUT and gens:
        cut = [min(gens, key=lambda i: first.get(i, 0))]
    else:
        cut = sorted(gens)
    void = [g for g in gens if g not in cut]
    if cut:
        rs = [frozenset(fwd[c]["roster"]) for c in cut]
        roster = frozenset.union(*rs) if "fork_union" in MUT else frozenset.intersection(*rs)
    else:
        roster = frozenset()

    # the earlier rows a reader accepts: none, except under a planted break
    acc = set()
    if "earlier_until_genesis" in MUT and not cut:
        acc |= set(e1)
    if "by_arrival" in MUT and cut:
        f = min(first.get(c, 0) for c in cut)
        acc |= {i for i in e1 if first.get(i, 0) < f}
    if "earlier_named" in MUT:
        acc |= {n for r in fwd.values() for n in r["names"] if n in e1}
    if MUT & {"earlier_record_live", "earlier_votes", "earlier_rebind", "earlier_binding", "earlier_halt",
              "earlier_roster"}:
        acc |= set(e1)
    A = {i: r for i, r in by.items() if (r["form"] == "e2" and i not in void) or i in acc}
    person = {r["key"]: r["as_"] for r in e1.values() if r["kind"] == "rec" and r.get("as_")}

    # owners, by owner-bindings with both voices (CC 3.2); an earlier binding counts only under a plant
    def owner_of(k):
        os_ = set()
        for r in A.values():
            if r["kind"] != "ob":
                continue
            if r["form"] == "e1" and "earlier_binding" not in MUT:
                continue
            tgt = person.get(r["target"], r["target"]) if r["form"] == "e1" else r["target"]
            own = person.get(r["owner"], r["owner"]) if r["form"] == "e1" else r["owner"]
            if tgt == k and {r["owner"], r["target"]} <= set(r["voices"]):
                os_.add(own)
        return next(iter(os_)) if len(os_) == 1 else None

    def live(k, depth=2):
        """CC 2.4.1.1: a key is live only by its own record of this form that covers now, unless one of the three
        revokers (the key, its owner, the roster that seats it) has revoked it."""
        revs = [r for r in A.values() if r["kind"] == "revoke" and r["key"] == k and r["form"] == "e2"]
        for r in revs:
            if r["signer"] == k or "third_party_ends" in MUT:
                return False
            if "owner_revocation_ignored" not in MUT and depth and owner_of(k) == r["signer"] and live(r["signer"], depth - 1):
                return False
        for r in recs(k):
            vu = INF if r["vu"] is None else r["vu"]
            if r["vf"] <= now < vu:
                return True
        if "earlier_record_live" in MUT and any(r["kind"] == "rec" and k in (r["key"], person.get(r["key"])) for r in e1.values()):
            return True
        if "named_makes_live" in MUT and any(r["kind"] == "rec" and r["key"] == k and any(
                r["id"] in q["names"] and q["signer"] != k for q in fwd.values()) for r in fwd.values()):
            return True
        return False

    R = roster
    if "roster_shrinks" in MUT:
        R = frozenset(k for k in roster if live(k))
    M = len(R) // 2 + 1

    def voices_of(r):
        out = set()
        for k in r.get("voices", ()):
            if r["form"] == "e1":
                p = person.get(k) if "earlier_votes" in MUT else None
                if p in R:
                    out.add(p)
            elif k in R and live(k):
                out.add(k)
        return out

    def counted(r):
        if r["kind"] == "bundle2":
            return r["id"] in cut
        need = 1 if ("one_holder_rebind" in MUT and r["kind"] == "rebind") else M
        return bool(R) and len(voices_of(r)) >= need

    # a seat's transit key: the bindings every genesis in force names, then counted re-binds; one value or none
    seats = {}
    for s in ("n1", "n2"):
        cands = [fwd[n] for c in cut for n in fwd[c]["names"] if n in fwd and fwd[n]["kind"] == "td" and fwd[n]["seat"] == s]
        if "fork_union" not in MUT and len(cut) > 1:
            vals = [set(fwd[n]["xw"] for n in fwd[c]["names"] if n in fwd and fwd[n]["kind"] == "td" and fwd[n]["seat"] == s)
                    for c in cut]
            common = set.intersection(*vals) if vals else set()
            cands = [r for r in cands if r["xw"] in common]      # tips hold what every genesis in force names
        cands += [r for r in A.values() if r["kind"] == "rebind" and r["seat"] == s and r["form"] == "e2" and counted(r)]
        if "earlier_rebind" in MUT:
            cands += [r for r in A.values() if r["kind"] == "rebind" and r["seat"] == s and r["form"] == "e1"]
        if "seat_alone_td" in MUT:
            cands += [r for r in A.values() if r["kind"] == "td" and r["seat"] == s]
        anc = {r["id"]: CK.ancestors(by, r["id"]) for r in cands}
        top = K.frontier(anc, cands) if cands else []
        vals = sorted({r["xw"] for r in top})
        seats[s] = vals[0] if len(vals) == 1 or ("pick_one" in MUT and vals) else None

    agents = sorted({r["key"] for r in fwd.values() if r["kind"] == "rec" and r["typ"] == "agent"})

    def edge_of(p):
        return any(r["kind"] == "edge" and r["signer"] == p and r["form"] == "e2" and live(p) for r in A.values())

    def may_act(a):
        if "act_without_steward" in MUT:
            return live(a)
        st = owner_of(a)
        return live(a) and st is not None and edge_of(st)

    def members():
        out = set()
        for r in A.values():
            if r["kind"] != "roster" or (r["form"] == "e1" and "earlier_roster" not in MUT):
                continue
            if set(r["voices"]) >= set(r["members"]):        # a founding seats who signed it (CC 3.1.3.2)
                out |= {person.get(m, m) if r["form"] == "e1" else m for m in r["members"]}
        return frozenset(out)

    honoured = set()
    for r in A.values():
        if r["kind"] != "halt":
            continue
        if r["form"] == "e1":
            if "earlier_halt" in MUT:
                honoured.add(r["id"])
            continue
        whole = r["halves"] >= {"ed", "pq"} or ("one_half_verifies" in MUT and "ed" in r["halves"])
        if r["signer"] in R and live(r["signer"]) and whole:
            honoured.add(r["id"])
    resumed = {h for h in honoured if any(r["kind"] == "resume" and h in r["names"] and counted(r) for r in A.values())}

    keys = sorted({r["key"] for r in by.values() if r["kind"] == "rec"})
    return {
        "cut": tuple(cut), "void": tuple(sorted(void)),
        "accepted": frozenset(i for i in acc if i in by),
        "live": frozenset(k for k in keys if live(k)),
        "roster": R,
        "counted": frozenset(i for i, r in A.items() if r["kind"] in COUNTED and counted(r)),
        "seats": tuple(sorted(seats.items())),
        "steward": tuple((a, owner_of(a)) for a in agents),
        "may_act": tuple((a, may_act(a)) for a in agents),
        "members": members(),
        "honoured": frozenset(honoured), "resumed": frozenset(resumed),
    }


def publishable(timeline, holders):
    """The genesis is published only once every holder has sealed a halt of this form (CC 4.2.1.1): returns the
    timeline with the genesis moved after the last sealed halt, unless a plant publishes it ungated."""
    if "publish_ungated" in MUT:
        return list(timeline)
    gi = [i for i, r in enumerate(timeline) if r["kind"] == "bundle2"]
    if not gi:
        return list(timeline)
    hs = [i for i, r in enumerate(timeline) if r["kind"] == "halt" and r.get("sealed") and r["form"] == "e2"]
    last = max(hs) if hs else -1
    g = gi[0]
    if last < g:
        return list(timeline)
    t = [r for i, r in enumerate(timeline) if i != g]
    t.insert(last, timeline[g])
    return t
