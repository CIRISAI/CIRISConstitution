"""
checkpoint.py: THE CHECKPOINT. A counted row of a group's ledger is a cut on the rows counted over older heads.

    group checkpoint    A counted roster row (an offer or an unseat conferred by a count, naming the head it is counted
                        over) that counts is a checkpoint of its object. A row that states a head (another counted act)
                        that is CONCURRENT with a counting checkpoint and whose heads are all strictly older than the
                        head the checkpoint names, does not count. Its signer may
                        sign it again naming the checkpoint: that is a new row, it is not concurrent, and it is judged at
                        the head it names. The same body signed again is the same voice, not a second one (a count is of
                        distinct signers).
    reader checkpoint   A reader's own acknowledgement of a head (an `ack` row under its key, with `room` and `head`)
                        makes the acknowledged act, and every counted act in its past, a checkpoint for that reader alone,
                        and one that no other checkpoint voids for it. So a line built on heads older than those the
                        reader's acknowledged line is counted over is void for that reader, however long it is. An act
                        counted over the same head as the acknowledged one is not void: it waits, as for everyone, and a
                        counted row naming both is accepted by that reader like any other.

Both are functions of (rows, own key). No instant, no arrival order and no digest is compared.

What it does not reach, by construction: an act counted over the SAME head as the newest checkpoint (two versions of
one head still wait, KERNEL 7); a row that states no head (a standing appointment, a message: those are the cut's
and the seat's to judge); and an answer to a window. A window protects one voice against the count, and a checkpoint
is made by the count, so window.py does not apply `stale_answer` unless asked to, and it is asked to only by the
attack that shows why not.

A checkpoint is itself a counted act and can be stale against another. A voider always names a strictly newer head,
so the acts are read newest head first and each is judged against the checkpoints already found; for roster versions
(`versions`), where a version also needs the versions it builds on, the answer is the well-founded fixed point and a
version can be undecided.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import causal_kernel as CK  # noqa: E402

K = CK.K


def older(S, heads, than):
    """Every row of `heads` is strictly in the past of one of `than`."""
    return bool(heads) and all(any(h in S.anc[t] for t in than) for h in heads)


def counted_acts(S, obj):
    return [r for r in S.Cs if r["kind"] in ("offer", "unseat") and r.get("conf") == "group" and r.get("obj") == obj and r.get("head")]


def checkpoints(S, C, obj):
    """The counted acts on obj that count (C: cut.Cut of S) and are not stale against a checkpoint."""
    acts = sorted((r for r in counted_acts(S, obj) if C.counts(r)), key=lambda r: -max(len(S.anc[h]) for h in r["head"]))
    cps = []
    for r in acts:                                                      # newest head first: a voider names a strictly newer head
        if not any(S.concurrent(r["id"], c["id"]) and older(S, r["head"], c["head"]) for c in cps): cps.append(r)
    return cps


def own_line(S, own, obj):
    """The counted acts on obj this reader has acknowledged, with the counted acts in their past."""
    if own is None: return []
    acked = {h for a in K.sel(S.Cs, kind="ack", signer=own) if a.get("room") == obj for h in a.get("head", ())}
    return [r for r in counted_acts(S, obj) if r["id"] in acked or any(r["id"] in S.anc[h] for h in acked if h in S.anc)]


def void(S, C, own=None):
    """The ids of the counted acts that do not count under the checkpoint. own: the reader, for its own acknowledgements."""
    out = set()
    for obj in {r["obj"] for r in S.Cs if r["kind"] in ("offer", "unseat") and r.get("conf") == "group" and r.get("head")}:
        mine = own_line(S, own, obj)
        keep = {r["id"] for r in mine}
        marks = [(c["id"], c["head"]) for c in checkpoints(S, C, obj)] + [(r["id"], r["head"]) for r in mine]
        for r in counted_acts(S, obj):
            if r["id"] in keep: continue                                # what this reader acknowledged is not voided for it
            if any(cid != r["id"] and S.concurrent(r["id"], cid) and older(S, r["head"], heads) for cid, heads in marks): out.add(r["id"])
    return frozenset(out)


def stale_answer(S, cps, p, r):
    """A row r answering window p (or read for its target's silence) does not count: it is concurrent with a checkpoint
    of p's object that names a newer head than p was opened on, and everything r names is in that checkpoint's past."""
    return any(S.concurrent(r["id"], c["id"]) and older(S, p["head"], c["head"]) and all(n in S.anc[c["id"]] for n in r["names"]) for c in cps)


def versions(ids, builds_on, past, valid, ack=None):
    """Roster versions (formal/roster_fork's shape). ids: the versions held; builds_on[i]: the heads version i extends;
    past[i]: every version in its past; valid(i): counted over the heads it extends. ack: the version this reader has
    acknowledged, or None. Returns (certain, possible): a version in `possible` and not in `certain` is undecided."""
    conc = lambda i, j: i != j and i not in past[j] and j not in past[i]
    stale = lambda i, j: conc(i, j) and bool(builds_on[j]) and bool(builds_on[i]) and all(any(e in past[h] for h in builds_on[j]) for e in builds_on[i])
    P = [i for i in ids if valid(i)]
    mine = frozenset() if ack is None else frozenset({ack}) | frozenset(past[ack])       # the reader checkpoint: its acknowledged line
    P = sorted((i for i in P if i in mine or not any(stale(i, a) for a in mine)), key=lambda i: len(past[i]))

    def gamma(I):
        out = set()
        for i in P:
            if all(e in out for e in builds_on[i]) and (i in mine or not any(stale(i, j) for j in I)): out.add(i)
        return out
    T = set()
    while True:
        U = gamma(T); T2 = gamma(U)
        if T2 == T: return frozenset(T), frozenset(U)
        T = T2
