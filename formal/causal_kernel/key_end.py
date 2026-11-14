"""
key_end.py: a key's own end, as rows of the kernel (formal/causal_kernel/causal_kernel.py, imported in place).

A key record states `vu` (its `valid_until`); `vf` is the record's own signed instant (`asserted_at`). Which records must state an end is read from the
record alone: its `typ` (identity_type) and whether it is a room key. A `user` key (a person) and an accord holder's
key MUST NOT state one; a room key and a pseudonym need not. Every other node or agent record states one, and the bound is self-contained:
vf <= vu and vu - vf <= CEIL, read from the row and nothing else (the door).
A renewal is a further record of the same key that names (supersedes) its own earlier record. It counts whenever it
was signed: a renewal signed after the end revives the key, so a back-dated one gains nothing over it.

Rows (dicts of causal_kernel.row):
    rec      a key's claim of itself. signer = key. A renewal names the record it continues (same key). A rotation
             names the old key's record, carries succ_of = the old key, and both signatures (sigs) and the old
             key's own instant at_old.
    att      an attestation by `signer` at its own instant `at`, naming the record it was signed under (`cover`),
             optionally `about` a key and naming further rows.
    edge     a trust edge `signer -> to`, an att with `to`.
    revoke   the key's own revocation, `ra` = revoked_after (statements after it do not count; never withdrawn).

Layers
    kept       CK.kept with WF below (the row alone).
    concluded  RULE below: reads only the row's past (the record it names). It never reads now.
    derived    answers(S, now): live and ended keys, the successor, reach, score, and each row's lapse.

The only instants compared are one key's own: a row's `at` against the record it names (same signer); a rotation's at_old
against the old key's record (signed by the old key). No two signers' instants are compared, and nothing is ranked by an instant or a digest.

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
def rec(id, key, vf, vu, names=(), typ="node", succ_of=None, at_old=None, sigs=None, room=False):
    return CK.row(id, "rec", key, names, key=key, vf=vf, vu=vu, typ=typ, succ_of=succ_of, at_old=at_old,
                  sigs=frozenset(sigs if sigs is not None else ({key} | ({succ_of} if succ_of else set()))), room=room)


def att(id, signer, at, cover, about=None, names=()):
    return CK.row(id, "att", signer, (cover,) + tuple(names), at=at, cover=cover, about=about)


def edge(id, signer, to, at, cover, names=()):
    return CK.row(id, "edge", signer, (cover,) + tuple(names), at=at, cover=cover, to=to)


def revoke(id, key, ra):
    return CK.row(id, "revoke", key, (), key=key, ra=ra)


# ---- the door: the row alone -----------------------------------------------------------------------------
def needs_end(r):
    """Read from the record alone: its identity type and whether it is a room key."""
    if "wording" in MUT:      # the ruling as worded: no owner-binding at federation scope (another row)
        return r["typ"] in END_REQUIRED and not r.get("_fed_binding_held", False)
    return r["typ"] in END_REQUIRED and not r["room"]


def WF(r):
    if r["kind"] != "rec":
        return True
    vf, vu = r["vf"], r["vu"]
    if vu is None:
        return not needs_end(r)
    if r["typ"] in END_FORBIDDEN and "end_on_person" not in MUT:
        return False
    if vf > vu:
        return False
    if vu - vf > CEIL and "no_ceiling" not in MUT:
        return False
    if r["succ_of"] is not None and r["succ_of"] not in r["sigs"] and "rotation_one_sig" not in MUT:
        return False           # a rotation carries the old key's signature beside the new key's possession
    return r["key"] in r["sigs"]


def _end(r):
    return INF if r["vu"] is None else r["vu"]


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
        return p["key"] == r["succ_of"] and p["vf"] <= r["at_old"] <= _end(p)   # the old key, inside its own record
    if r["kind"] in ("att", "edge"):
        c = by.get(r["cover"])
        if c is None or c["kind"] != "rec" or c["key"] != r["signer"]:
            return False
        if "conclude_reads_now" in MUT and CLOCK[0] >= _end(c):   # PLANT: conclusion reads now
            return False
        return c["vf"] <= r["at"] <= _end(c)
    return True                                               # a revocation: the key's own, never withdrawn


def state(rows):
    return CK.concluded(CK.kept(rows, WF), RULE)


def arrived(order):
    CLOCK[0] = 0
    return CK.arrive(order, RULE, wf=WF)


# ---- derived ---------------------------------------------------------------------------------------------
def recs(S, k):
    return [r for r in K.sel(S.Cs, kind="rec") if r["key"] == k]


def rev_bound(S, k):
    ras = [r["ra"] for r in K.sel(S.Cs, kind="revoke") if r["key"] == k and r["signer"] == k]
    return min(ras) if ras else INF


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
        "succ": tuple((k, successor(S, k, ret)) for k in keys),
        "reach": tuple((p, reach(S, p, now, keys, ret)) for p in parties),
        "score": tuple((s, score(S, s, now, ret)) for s in subjects),
        "rows": frozenset((i, bool(S.C.get(i)), i in ret) for i in ret),
    }


def compact(rows, S, now):
    keep = retained(S, now)
    return [r for r in rows if r["id"] in keep]
