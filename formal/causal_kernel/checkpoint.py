"""
checkpoint.py: which counted rows of a group's ledger count for a reader.

    built on            A counted act (an offer or an unseat conferred by a count, naming the head it is counted over)
                        counts only if every counted act among the heads it names itself counts. A row built on a
                        counted act that does not count is void, down the whole line. This is a rule in its own right,
                        whatever else is on or off: nothing is built on a void row. "Does not count" is one thing here:
                        the cut voids it (cut.py), the reader's line leaves it behind, or it is itself built on such a
                        row. There is no other way for a head act to fail.
    the reader's line   A reader's own acknowledgement of a head (an `ack` row under its key, with `room` and `head`)
                        makes the acknowledged act, and every counted act in its past, that reader's line. For that
                        reader the line counts, and a counted act that is concurrent with an act of the line and is
                        counted over heads all strictly older than the heads that act names does not count. So a line
                        grown from below what the reader acknowledged is void for it, however long it is. An act counted
                        over the SAME head as an act of the reader's line is not void: it waits as a tip, as for
                        everyone (KERNEL 7), and a counted row naming both is accepted by that reader like any other.
                        This is relative to the reader. It ranks no line above another: a reader with no acknowledgement
                        has no line, and for it every counted act the cut lets count, built on acts that count, counts.

Both are functions of (rows, own key). No instant, no arrival order and no digest is compared.

    the group checkpoint   OFF. `group=True` makes every counting counted act a checkpoint for everyone: an act
                        concurrent with it and counted over older heads does not count. It is a rank by depth of line,
                        and this kernel orders nothing except by what rows name. With it on, keys that met the count at
                        the head the newest honest row is counted over sign two rows, the second over the first, are one
                        row deeper than the honest line, and leave the honest row behind: a removed member is listed
                        again (attacks.py, test 4 and checkpoint_price). Honest concurrency on one head behaves the same
                        way. The parameter exists only to show that witness, and the one in window.py (a majority
                        voiding one voice). With it on, "counts" refers to itself through negation and is solved as the
                        cut is, by the well-founded fixed point; with it off there is no negation and one answer.
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


def own_line(S, own, obj):
    """The counted acts on obj this reader has acknowledged, with the counted acts in their past."""
    if own is None: return []
    acked = {h for a in K.sel(S.Cs, kind="ack", signer=own) if a.get("room") == obj for h in a.get("head", ())}
    return [r for r in counted_acts(S, obj) if r["id"] in acked or any(r["id"] in S.anc[h] for h in acked if h in S.anc)]


def settle(S, C, obj, own=None, group=False):
    """(certain, possible): the ids of the counted acts on obj that count for reader `own`.

    A counted act counts iff the cut lets it count, EVERY COUNTED ACT AMONG THE HEADS IT NAMES ITSELF COUNTS, and no
    act of the reader's own acknowledged line leaves it behind. The reader's line counts for that reader.
    With group=False (the rule) nothing here is negated and certain == possible.
    With group=True (the refused group checkpoint, kept to show why) every act that certainly counts also leaves
    older-head acts behind; an act in `possible` and not in `certain` is then undecided: not void, and no checkpoint."""
    acts = counted_acts(S, obj)
    live = sorted((r for r in acts if C.counts(r)), key=lambda r: len(S.anc[r["id"]]))
    line = {r["id"] for r in acts}
    built = {r["id"]: [h for h in r["head"] if h in line] for r in live}          # the counted acts it is built on
    mine = {r["id"] for r in own_line(S, own, obj)} & {r["id"] for r in live}
    behind = lambda r, c: c["id"] != r["id"] and S.concurrent(r["id"], c["id"]) and older(S, r["head"], c["head"])

    def gamma(I):
        """The acts that count if exactly the acts in I (and the reader's line) are the checkpoints."""
        marks = [c for c in live if c["id"] in mine or (group and c["id"] in I)]
        out = set()
        for r in live:                                                  # ancestors first
            if r["id"] in mine or (all(h in out for h in built[r["id"]]) and not any(behind(r, c) for c in marks)):
                out.add(r["id"])
        return frozenset(out)
    T = frozenset()
    while True:
        U = gamma(T); T2 = gamma(U)
        if T2 == T: return T, U
        T = T2


def checkpoints(S, C, obj, own=None, group=False):
    """The counted acts on obj that certainly count."""
    T, _ = settle(S, C, obj, own, group)
    return [r for r in counted_acts(S, obj) if r["id"] in T]


def void(S, C, own=None, group=False):
    """The ids of the counted acts the cut lets count that do not count for reader `own`: left behind by its
    acknowledged line, or built on a counted act that does not count."""
    out = set()
    for obj in {r["obj"] for r in S.Cs if r["kind"] in ("offer", "unseat") and r.get("conf") == "group" and r.get("head")}:
        _, U = settle(S, C, obj, own, group)
        out |= {r["id"] for r in counted_acts(S, obj) if C.counts(r) and r["id"] not in U}
    return frozenset(out)


def stale_answer(S, cps, p, r):
    """Only for window.outcome(..., checkpoint=True), which is off: a row r answering window p is left behind by a
    checkpoint of p's object that names a newer head than p was opened on and has everything r names in its past."""
    return any(S.concurrent(r["id"], c["id"]) and older(S, p["head"], c["head"]) and all(n in S.anc[c["id"]] for n in r["names"]) for c in cps)


def versions(ids, builds_on, past, valid, ack=None, group=False):
    """The same two rules for roster versions (formal/roster_fork's shape). ids: the versions held; builds_on[i]: the
    heads version i extends; past[i]: every version in its past; valid(i): counted over the heads it extends. ack: the
    version this reader has acknowledged, or None. Returns (certain, possible); they differ only with group=True."""
    conc = lambda i, j: i != j and i not in past[j] and j not in past[i]
    stale = lambda i, j: conc(i, j) and bool(builds_on[j]) and bool(builds_on[i]) and all(any(e in past[h] for h in builds_on[j]) for e in builds_on[i])
    P = [i for i in ids if valid(i)]
    mine = frozenset() if ack is None else frozenset({ack}) | frozenset(past[ack])       # the reader checkpoint: its acknowledged line
    P = sorted((i for i in P if i in mine or not any(stale(i, a) for a in mine)), key=lambda i: len(past[i]))

    def gamma(I):
        out = set()
        for i in P:
            if all(e in out for e in builds_on[i]) and (i in mine or not (group and any(stale(i, j) for j in I))): out.add(i)
        return out
    T = set()
    while True:
        U = gamma(T); T2 = gamma(U)
        if T2 == T: return frozenset(T), frozenset(U)
        T = T2
