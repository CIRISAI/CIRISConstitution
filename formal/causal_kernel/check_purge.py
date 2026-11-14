#!/usr/bin/env python3
"""
check_purge.py: a checkpointing node that purges answers as one that keeps every row (CC 2.7.10).

For each history of purge.py the node checkpoints and purges by the rule, and then every extension of the
history's pool is offered: to the purged store at once, and to a store purged again after each part of the
extension has arrived. Every answer of purge.View (kept, concluded, countsAt, carried, settled, missing, void,
window, at every `now` of the history) is compared with the answer over the same rows held whole.

    (i)   every answer after purge equals the answer with nothing purged, under the broad reading of the reader's
          line (the rule, CC 2.7.8) and, separately, under the narrow one;
    (ii)  no row a duty of the never-purge list covers is dropped, and no row a deletion duty ends is kept whole;
    (iii) each plant is caught.

It reports the rows each reading keeps whole and reduces to a stub, and records the reader's line as
checkpoint.py runs it (a counted act that is not a roster version, on a head below the acknowledged one, is void).

    python3 -I check_purge.py            compares with purge_expected.tsv; exit 1 on any difference or a plant not caught
    python3 -I check_purge.py --write    writes purge_expected.tsv
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import purge as P  # noqa: E402
import causal_kernel as CK  # noqa: E402
import cut  # noqa: E402
import checkpoint as CP  # noqa: E402

PLANTS = ("drop_unsettled", "freeze_now", "ck_acks", "drop_duty", "keep_deleted", "no_say", "narrow_eval", "freeze_carried")


def reader_line_reading():
    """The reader's line as checkpoint.py runs it, on a duty seat's counted withdrawal."""
    R = CK.row
    rows = [R("g", "seat", "A"),
            R("a1", "offer", "A", ("g",), conf="group", obj="room", head=("g",)),
            R("a2", "offer", "B", ("a1",), conf="group", obj="room", head=("a1",)),
            R("k", "ack", "N", ("a2",), room="room", head=("a2",)),
            R("u0", "unseat", "C", ("g",), conf="group", obj="room", head=("g",), scope="moderate")]
    S = CK.concluded(rows, lambda r, Pa, past: True)
    C = cut.Cut(S)
    mine, none = sorted(CP.void(S, C, own="N")), sorted(CP.void(S, C, own=None))
    return "a moderator seat's counted withdrawal on a head below the acknowledged one: void for the reader %s, for a reader with none %s" % (
        "yes" if "u0" in mine else "no", "yes" if "u0" in none else "no")


def main():
    write = "--write" in sys.argv
    say = lambda s: print(s, flush=True)
    lines, ok = ["kind\tname\tverdict"], True
    for reading in ("broad", "narrow"):
        tn = tw = ts = 0
        for h in P.HISTORIES:
            n, diffs, store = P.run(h, reading)
            br = P.duty_breaches(h, store)
            whole, stub = P.measure(store)
            tn += n; tw += whole; ts += stub
            say("  [%s] %s: %d replays, %d differ, %d duty breaches; of %d rows held, %d kept whole and %d reduced to a stub" % (
                reading, h["name"], n, len(diffs), len(br), len(h["rows"]), whole, stub))
            for d in diffs + br:
                say("      " + d)
            ok &= not diffs and not br
            lines.append("history %s\t%s\t%d replays, %d differ, %d breaches, %d whole, %d stub" % (reading, h["name"], n, len(diffs), len(br), whole, stub))
        say("%s reading: %d replays over %d histories; %d rows kept whole, %d reduced to a stub at the first checkpoint" % (
            reading, tn, len(P.HISTORIES), tw, ts))
        lines.append("total %s\t%d histories\t%d replays, %d whole, %d stub" % (reading, len(P.HISTORIES), tn, tw, ts))
    caught = {}
    for p in PLANTS:
        nd = nb = 0
        for h in P.HISTORIES:
            n, diffs, store = P.run(h, plant=p)
            nd += len(diffs); nb += len(P.duty_breaches(h, store))
        caught[p] = nd + nb > 0
        say("  plant %s: %s (%d answers differ, %d duty breaches)" % (p, "caught" if caught[p] else "NOT CAUGHT", nd, nb))
        lines.append("plant\t%s\t%s, %d differ, %d breaches" % (p, "caught" if caught[p] else "not caught", nd, nb))
    rl = reader_line_reading()
    say("reader's line as run: " + rl)
    lines.append("reading\treader's line\t%s" % rl)
    path = os.path.join(HERE, "purge_expected.tsv")
    if write:
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        say("wrote purge_expected.tsv (%d lines)" % (len(lines) - 1))
        diff = []
    else:
        want = open(path, encoding="utf-8").read().rstrip("\n").split("\n") if os.path.exists(path) else []
        diff = sorted(set(want) ^ set(lines))
        for l in diff:
            say("  differs from purge_expected.tsv: %s %s" % ("expected" if l in want else "now", l))
    ok = ok and all(caught.values()) and not diff
    say("RESULT: %s" % ("ok" if ok else "NOT OK"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
