"""
key_end.py: a key's own end, as rows of the kernel (formal/causal_kernel/causal_kernel.py, imported in place).

A key record states `vu` (its `valid_until`); `vf` is the record's own signed instant (`asserted_at`). Which records must state an end is read from the
record alone: its `typ` (identity_type) and whether it is a room key. A `user` key (a person) and an accord holder's
key MUST NOT state one; a room key and a pseudonym need not. Every other node or agent record states one, and the bound is self-contained:
vf < vu and vu - vf <= CEIL, read from the row and nothing else (the door). A record covers t when vf <= t < vu.
A renewal is a further record of the same key that names (supersedes) its own earlier record. It counts whenever it
was signed: a renewal signed after the end revives the key, so a back-dated one gains nothing over it.

Rows (dicts of causal_kernel.row):
    rec      a key's claim of itself. signer = key. A renewal names the record it continues (same key). A rotation
             names the old key's record, carries succ_of = the old key, and both signatures (sigs) and the old
             key's own instant at_old.
    att      an attestation by `signer` at its own instant `at`, naming the record it was signed under (`cover`),
             optionally `about` a key and naming further rows. It states `iss`, the identity it signs as (by default
             the signer's own key, a genesis key or a room key signing as itself).
    edge     a trust edge `signer -> to`, an att with `to`.
    revoke   the key's own revocation, `ra` = revoked_after (statements after it do not count; never withdrawn).
    unbind   another voice's revocation of the key: the owner's (`of` = "binding") or the seating roster's removal
             (`of` = "seat"), from instant `ra`. It ends that standing and never the key's liveness (CC 2.4.1.1).

Layers
    kept       CK.kept with WF below (the row alone).
    concluded  RULE below: reads only the row's past (the record it names). It never reads now.
    derived    answers(S, now): live and ended keys, the successor, reach, score, and each row's lapse.

The only instants compared are one key's own: a row's `at` against the record it names (same signer); a rotation's at_old
against the old key's record (signed by the old key). No two signers' instants are compared, and nothing is ranked by an instant or a digest.

A statement counts as `iss` only if its key is `iss`'s genesis key, or the key of a record whose own `iss` is the
statement's and that reaches `iss`'s genesis key through rotations, each naming its predecessor's record and carrying
the predecessor's signature made inside that record (OF_ISS below). A renewal on the way does not move the chain. A
link not held waits, as every named row does. Derived over that, of_iss_now drops a chain one of whose links its
predecessor signed at or after its own revoked_after (CC 2.4.1.1), and no other voice's revocation cuts a chain.
A third way: a counted bundle of an accord lineage seats a key for `iss` (a recovery, or a rotation by bundle). The
statement names the bundle it relies on beside its key's record, and waits for it. Whether the bundle is counted is the accord model's answer,
taken here as a member of the row. Derived over that, the seat ends when a later counted bundle of the lineage,
naming it, no longer seats that key for `iss`.
A fourth way: a live occurrence of `iss` binds the key (`occ`): an identity:occurrence row of `iss` naming the key, signed
by a key of `iss` and carrying the bound key's own voice, admitted by the self-roster door (taken as given), covering
the statement's instant, and not evicted. A node or agent key is never bound under a person's identity.
A predecessor's voice on a rotation may be a separate statement (`voice`), which the rotation names and waits for.

A row LAPSES at now when its signer's key has ended and no row that has not lapsed has it in its past. A seat
serves and keeps exactly the rows that have not lapsed (RETAINED), which is route.py's closure with the seeds
"rows of a key that has not ended".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import causal_kernel as CK  # noqa: E402

K = CK.K
INF = float("inf")
CEIL = 10                         # stands for key_record_max_secs (365 days); the grid's unit is ~36.5 days
END_REQUIRED = {"node", "agent"}  # identity types whose record must state an end, outside a private room
END_FORBIDDEN = {"user", "accord_holder"}   # a person's own key and an accord holder's: no person loses their self to a clock
# any other type (a pseudonym of CC 5.4.6) may state an end and need not
MUT = set()                       # planted breaks, switched on by the check


# ---- rows ------------------------------------------------------------------------------------------------
def rec(id, key, vf, vu, names=(), typ="node", succ_of=None, at_old=None, sigs=None, room=False, iss=None, voice=None):
    """`iss`: the identity the record is of; a first record's is its own key, a rotation's its predecessor's.
    `voice`: the id of the predecessor's separate statement on a rotation, which the record names and waits for."""
    names = tuple(names) + ((voice,) if voice else ())
    return CK.row(id, "rec", key, names, key=key, vf=vf, vu=vu, typ=typ, succ_of=succ_of, at_old=at_old,
                  sigs=frozenset(sigs if sigs is not None else ({key} | ({succ_of} if succ_of and not voice else set()))),
                  room=room, iss=iss if iss is not None else (succ_of or key), voice=voice)


def att(id, signer, at, cover, about=None, names=(), iss=None):
    return CK.row(id, "att", signer, (cover,) + tuple(names), at=at, cover=cover, about=about,
                  iss=iss if iss is not None else signer)


def edge(id, signer, to, at, cover, names=()):
    return CK.row(id, "edge", signer, (cover,) + tuple(names), at=at, cover=cover, to=to, iss=signer)


def bundle(id, seats, counted=True, prev=None):
    """A genesis bundle of an accord lineage: `seats` maps an identity to the key it seats; `counted` is the accord
    model's answer for its count; `prev` names its predecessor bundle."""
    return CK.row(id, "bun", "accord", (prev,) if prev else (), seats=dict(seats), counted=counted, prev=prev)


def occ(id, signer, iss, okey, vf, vu, names=(), admitted=True, sigs=None):
    """An identity:occurrence row of `iss` binding `okey`, signed by `signer`; `names` holds the signer's record, the
    bound key's record and iss's genesis record; `admitted` is the self-roster door's answer; `sigs` its voices."""
    return CK.row(id, "occ", signer, tuple(names), iss=iss, okey=okey, vf=vf, vu=vu, admitted=admitted,
                  sigs=frozenset(sigs if sigs is not None else {signer, okey}))


def evict(id, signer, of, names=()):
    """The roster door's eviction of the occurrence `of`, signed by `signer`; `names` holds the signer's own record,
    which the eviction waits for (CC 2.6.1.7 way (d))."""
    return CK.row(id, "evict", signer, (of,) + tuple(names), of=of)


def voice(id, signer, at, names):
    """A further statement over a rotation record's payload by the predecessor key, at its own instant."""
    return CK.row(id, "voice", signer, tuple(names), at=at)


def revoke(id, key, ra):
    return CK.row(id, "revoke", key, (), key=key, ra=ra)


def unbind(id, signer, key, ra, of="binding"):
    """Another voice's revocation of `key`: the owner's ends the owner-binding's standing, the roster's the seat."""
    return CK.row(id, "revoke", signer, (), key=key, ra=ra, of=of)


# ---- the door: the row alone -----------------------------------------------------------------------------
def needs_end(r):
    """Read from the record alone: its identity type and whether it is a room key."""
    if "wording" in MUT:      # the ruling as worded: no owner-binding at federation scope (another row)
        return r["typ"] in END_REQUIRED and not r.get("_fed_binding_held", False)
    return r["typ"] in END_REQUIRED and not r["room"]


def WF(r):
    if r["kind"] == "occ":
        return r["okey"] in r["sigs"] or "iss_occ_no_own_voice" in MUT   # the bound key's own voice, else it waits
    if r["kind"] != "rec":
        return True
    vf, vu = r["vf"], r["vu"]
    if vu is None:
        return not needs_end(r)
    if r["typ"] in END_FORBIDDEN and "end_on_person" not in MUT:
        return False
    if vf >= vu and not (vf == vu and "iss_end_inclusive" in MUT):
        return False           # an end not later than the record's own instant covers nothing
    if vu - vf > CEIL and "no_ceiling" not in MUT:
        return False
    if r["succ_of"] is not None and r["succ_of"] not in r["sigs"] and not r.get("voice") \
            and not MUT & {"rotation_one_sig", "iss_unsigned_link"}:
        return False           # a rotation carries the old key's voice beside the new key's possession; without it, it waits
    return r["key"] in r["sigs"]


def _end(r):
    return INF if r["vu"] is None else r["vu"]


# ---- the key of `iss`: a statement's key against the identity it signs as ---------------------------------
def iss_chain(r, by):
    """The links from the record r's key resolves to (`cover`) back to `iss`'s genesis key, over the records in `by`;
    [] when r's key is `iss` itself (a genesis key, or a room key signing as itself); None when no chain reaches it."""
    iss, k = r["iss"], r["signer"]
    if "iss_unchecked" in MUT:                        # PLANT: any held key signs as any iss
        return []
    if k == iss:
        return []                                     # (a) kid is the thumbprint inside iss
    if "iss_genesis_only" in MUT:                     # PLANT (over-strict): only the genesis key, so rotation breaks
        return None
    for b in (by[n] for n in r["names"] if n in by and by[n]["kind"] == "bun"):   # (c) a bundle seats this key for iss
        if (b["counted"] or "iss_bundle_uncounted" in MUT) and b["seats"].get(iss) == k:
            return [b]
    if "iss_skip_occurrence" not in MUT:              # (d) a live occurrence of iss binds this key
        for o in (by[n] for n in r["names"] if n in by and by[n]["kind"] == "occ"):
            if o["iss"] == iss and o["okey"] == k and covers(o, r.get("at", 0)):
                return [o]
    c = by.get(r["cover"])
    if c is None or c["kind"] != "rec" or c["key"] != k:
        return None
    links = []
    for _ in range(len(by) + 1):
        if c["key"] == iss:
            return links                              # reached iss's genesis key, through renewals or not
        if c["iss"] != iss and "iss_other_identity" not in MUT:
            return None                               # a record of another identity
        named = [by[n] for n in c["names"] if n in by and by[n]["kind"] == "rec"]
        if c["succ_of"] is None:
            prev = [p for p in named if p["key"] == c["key"]]
            if not prev:
                return links if "iss_other_identity" in MUT else None   # PLANT: any first record ends a chain
            c = prev[0]                               # a renewal: the same key's earlier record; the chain does not move
            continue
        if c["succ_of"] not in c["sigs"] and not c.get("voice") and "iss_unsigned_link" not in MUT:
            return None                               # the rotation carries no statement by its predecessor
        prev = [p for p in named if p["key"] == c["succ_of"]]
        if not prev:
            return None
        links.append(c)
        c = prev[0]
    return None


def covers(x, t):
    """A record (or occurrence) covers t when vf <= t < vu (half-open); the plant reads the end as included."""
    end = _end(x)
    return x["vf"] <= t < end or ("iss_end_inclusive" in MUT and t == end)


def of_iss_now(S, rid):
    """Derived: the statement counts as its iss given the revocations held. A link its predecessor signed at or after
    that key's own revoked_after does not stand (CC 2.4.1.1); another voice's revocation cuts nothing."""
    r = S.by[rid]
    if not S.C.get(rid):
        return False
    links = iss_chain(r, {q["id"]: q for q in S.Cs})
    if links is None:
        return False
    if links and links[0]["kind"] == "bun":
        return "iss_bundle_superseded" in MUT or bundle_in_force_seats(S, links[0], r["iss"], r["signer"])
    if links and links[0]["kind"] == "occ":
        return "iss_occ_ignores_eviction" in MUT or not evicted(S, links[0])
    if not all(handed_on(S, l) for l in links):
        return False
    if "iss_ignores_revoked_after" in MUT:            # PLANT: a link signed after its predecessor's revocation stands
        return True
    return all(l["at_old"] < rev_bound(S, l["succ_of"]) for l in links)


def handed_on(S, l):
    """A rotation hands on only where the frontier of the predecessor's rotations names its key alone: two rivals,
    neither naming the other, hand on nothing until a rotation names both (CC 2.4.1.1). A rival counts only where it
    is concluded, so it names a valid record of the predecessor covering its own instant."""
    if "iss_rivals_ignored" in MUT:                   # PLANT: a rival rotation is not read
        return True
    pool = S.rows if "iss_rival_uncovered" in MUT else S.Cs   # PLANT: a rival that concluded nothing blocks
    rots = [r for r in pool if r["kind"] == "rec" and r["succ_of"] == l["succ_of"]]
    return {r["key"] for r in CK.frontier(S, rots)} == {l["key"]}


def evicted(S, o):
    """An occurrence is evicted only by an eviction that has concluded and whose signer resolves to the occurrence's
    identity: its genesis key, or a key whose concluded record is of that identity. An eviction the reader cannot
    yet resolve waits and counts for nothing (CC 2.6.1.7 way (d))."""
    if "iss_occ_unconcluded_eviction" in MUT:                 # PLANT: an eviction counts whoever signed it
        return any(e["of"] == o["id"] for e in S.Cs if e["kind"] == "evict")
    keys = {o["iss"]} | {r["key"] for r in S.Cs if r["kind"] == "rec" and r["iss"] == o["iss"]}
    return any(e["of"] == o["id"] and e["signer"] in keys for e in S.Cs if e["kind"] == "evict")


def bundle_in_force_seats(S, b, iss, k):
    """The bundles in force on b's lineage are the counted bundles that have b in their past (or b itself) and that no
    counted bundle names; the seat stands while every one of them seats k for iss."""
    later = [q for q in S.Cs if q["kind"] == "bun" and q["counted"] and (q["id"] == b["id"] or b["id"] in S.anc[q["id"]])]
    tips = [q for q in later if not any(q["id"] in S.anc[x["id"]] for x in later)]
    return bool(tips) and all(q["seats"].get(iss) == k for q in tips)


# ---- concluded: the row against its past ---------------------------------------------------------------
CLOCK = [0]


def RULE(r, P, past):
    by = {q["id"]: q for q in P}
    if r["kind"] == "rec":
        prev = [by[n] for n in r["names"] if n in by and by[n]["kind"] == "rec"]
        if r["succ_of"] is None:
            if not r["names"]:
                return True                                   # a first record: possession is the door's
            if not prev:
                return False
            p = prev[0]
            if p["key"] != r["key"]:
                return False
            ok = True                                         # the key's own further record, whenever signed
            if "arrival_clock" in MUT:                        # PLANT: judged against the node's clock on first holding
                CLOCK[0] += 3
                ok = ok and CLOCK[0] < _end(p)
            return ok
        if not prev:
            return False
        p = prev[0]
        if r.get("voice"):                                    # the predecessor's voice, a separate statement
            v = by.get(r["voice"])
            if v is None or v["kind"] != "voice" or v["signer"] != r["succ_of"] or v["at"] != r["at_old"]:
                return False
        return p["key"] == r["succ_of"] and covers(p, r["at_old"])   # the old key, inside its own record
    if r["kind"] in ("att", "edge"):
        c = by.get(r["cover"])
        if c is None or c["kind"] != "rec" or c["key"] != r["signer"]:
            return False
        if "conclude_reads_now" in MUT and CLOCK[0] >= _end(c):   # PLANT: conclusion reads now
            return False
        return covers(c, r["at"]) and iss_chain(r, by) is not None
    if r["kind"] == "occ":
        return occ_admitted(r, by)
    return True                                               # a revocation: the key's own, never withdrawn


PERSON = {"user", "accord_holder"}
MACHINE = {"node", "agent"}


def occ_admitted(o, by):
    """An occurrence concludes when the roster door admitted it, its signer is a key of `iss` (the genesis key, or a key
    of iss by a rotation chain, with the signer's record named), and it binds no machine key under a person."""
    if not o["admitted"]:
        return False
    recs = [by[n] for n in o["names"] if n in by and by[n]["kind"] == "rec"]
    bound = [q for q in recs if q["key"] == o["okey"]]
    gen = [q for q in recs if q["key"] == o["iss"]]
    if "iss_occ_agent_as_person" not in MUT and bound and gen and bound[0]["typ"] in MACHINE and gen[0]["typ"] in PERSON:
        return False                                  # a key is a person's or a machine's, never both
    if "iss_occ_any_signer" in MUT:
        return True
    mine = [q for q in recs if q["key"] == o["signer"]]
    return bool(mine) and iss_chain({"iss": o["iss"], "signer": o["signer"], "cover": mine[0]["id"], "names": ()}, by) is not None


def state(rows):
    return CK.concluded(CK.kept(rows, WF), RULE)


def arrived(order):
    CLOCK[0] = 0
    return CK.arrive(order, RULE, wf=WF)


# ---- derived ---------------------------------------------------------------------------------------------
def recs(S, k):
    return [r for r in K.sel(S.Cs, kind="rec") if r["key"] == k]


def rev_bound(S, k):
    ras = [r["ra"] for r in K.sel(S.Cs, kind="revoke") if r["key"] == k and (r["signer"] == k or "other_ends_life" in MUT)]
    return min(ras) if ras else INF


def standing(S, k, now, of):
    """The key's standing in its owner-binding (`of` = "binding") or its seat (`of` = "seat"): it holds while the key
    is live and no revocation of that standing by another voice has taken effect by now (CC 2.4.1.1)."""
    if not live(S, k, now):
        return False
    if "unbind_ignored" in MUT:           # PLANT: the owner's revocation and the roster's removal end nothing
        return True
    return not any(r["key"] == k and r["signer"] != k and r.get("of") == of and now >= r["ra"]
                   for r in K.sel(S.Cs, kind="revoke"))


def live(S, k, now, witnessed_late=False):
    if now >= rev_bound(S, k):
        return False
    for r in recs(S, k):
        if r["vf"] <= now < _end(r):
            return True
    if "witness_revives" in MUT:      # PLANT: another voice's row naming a key's record extends it by the ceiling
        for r in recs(S, k):
            if any(r["id"] in q["names"] and q["signer"] != k for q in S.Cs) and r["vf"] <= now < _end(r) + CEIL:
                return True
    return False


def ended(S, k, now):
    """No record of k states an end after now, or k revoked itself by now. A record not yet begun is not ended."""
    if now >= rev_bound(S, k):
        return True
    rs = recs(S, k)
    if "end_from_newest" in MUT and rs:   # PLANT: one voice's newest record by its signed valid_from decides alone
        rs = [max(rs, key=lambda r: (r["vf"], r["id"]))]
    return all(_end(r) <= now for r in rs)


def successor(S, k, ret=None):
    """The one key the frontier of k's concluded rotations names; two keys spoken leave it empty. Given the
    retained set, it reads only rotations that have not lapsed, as every derived answer does."""
    rots = [r for r in K.sel(S.Cs, kind="rec") if r["succ_of"] == k and (ret is None or r["id"] in ret)]
    if not rots:
        return None
    keys = sorted({r["key"] for r in CK.frontier(S, rots)})
    if "rank_successor" in MUT:
        return keys[0]                    # PLANT: the lower key id wins
    return keys[0] if len(keys) == 1 else None


def seeds(S, now):
    """Concluded rows whose key has not ended at now, and every revocation (never withdrawn, never dropped)."""
    out = set()
    for r in S.Cs:
        if r["kind"] == "revoke":
            out.add(r["id"]); continue
        k = r["key"] if r["kind"] == "rec" else r["signer"]
        if ended(S, k, now):
            continue
        if "seed_live_only" in MUT and not live(S, k, now):
            continue                      # PLANT: keep only rows of keys live now (a record not yet begun is dropped)
        out.add(r["id"])
    return out


def retained(S, now):
    """The rows that have not lapsed: rows of keys not ended, and everything in their past."""
    if "drop_dead_signers" in MUT:        # PLANT: drop every row of an ended key, named or not
        return frozenset(seeds(S, now))
    s = seeds(S, now)
    return frozenset(s) | frozenset(a for i in s for a in S.anc[i] if a in S.by)


def reach(S, own, now, keys, ret=None):
    ret = retained(S, now) if ret is None else ret
    E = [e for e in K.sel(S.Cs, kind="edge") if e["id"] in ret and live(S, e["signer"], now) and live(S, e["to"], now)]
    return K.fix(lambda ks: ks | frozenset(e["to"] for e in E if e["signer"] in ks), frozenset({own}), len(keys) + 1)


def score(S, subject, now, ret=None):
    ret = retained(S, now) if ret is None else ret
    return frozenset(a["signer"] for a in K.sel(S.Cs, kind="att") if a.get("about") == subject
                     and (a["id"] in ret or "score_reads_lapsed" in MUT))


def answers(S, now, keys, parties, subjects):
    ret = retained(S, now)
    return {
        "live": frozenset(k for k in keys if live(S, k, now)),
        "ended": frozenset(k for k in keys if ended(S, k, now)),
        "standing": frozenset((k, of) for k in keys for of in ("binding", "seat") if standing(S, k, now, of)),
        "succ": tuple((k, successor(S, k, ret)) for k in keys),
        "reach": tuple((p, reach(S, p, now, keys, ret)) for p in parties),
        "score": tuple((s, score(S, s, now, ret)) for s in subjects),
        "rows": frozenset((i, bool(S.C.get(i)), i in ret) for i in ret),
    }


def compact(rows, S, now):
    keep = retained(S, now)
    return [r for r in rows if r["id"] in keep]
