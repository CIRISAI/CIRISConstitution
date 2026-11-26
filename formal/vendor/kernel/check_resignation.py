#!/usr/bin/env python3
"""
check_resignation.py: a resignation, the wrap set and dissolution (CC 2.4.1.1, CC 2.7.8), as seat.py reads them.

A resignation is a member's withdrawal of its own seat. It is an end and no head. Three readings follow from
rows already in the kernel, and this file holds them to cases and to every set of rows of a small room:

    counted   a counted row is counted over the members at the heads it names, less the members whose own
              leaving is in the row's past (seat.members_at, seat.left_in_past). So a resigner is among the
              counted members until a counted row cites its resignation, and from that row on it is out.
    wrap      a node wraps a key to, and serves rows to, the live seats over everything it holds
              (seat.Seats.holders; in a room with agents, Seats.roster: the members and the agents, whose
              wrap set check_agent_seat.py reads). A member whose end of its seat the node holds is not among them, at once
              and with no counted row. The wrap set need not equal the counted roster.
    dissolved a group is dissolved at a node when the wrap set is empty: every member at the heads it holds
              has an end of its seat that the node holds.

The room: three members a, b, c of g, a strict majority counting. Rows that may be held: each member's
resignation; a counted admission of d on g, signed by two members, citing or not citing a resignation; a
counted removal of c; a second admission built on the first.

Properties, over every set of those rows closed under what they name:
    no_resigner_wrapped   no member whose resignation is held is in the wrap set
    wrap_within_members   the wrap set holds only keys some held head seats
    cited_is_out          a counted row with a resignation in its past is not counted over that member, and the
                          member's own signature on it is no voice
    uncited_still_counts  a counted row that does not have the resignation in its past is counted over the
                          resigner (an omitted citation only delays)
    dissolved_by_rows     the group is dissolved exactly where every seated member's end is held; the answer
                          is the same in every arrival order (it reads the set)
    resignation_no_head   a resignation is never a tip of the lineage

Planted breaks:
    wrap_by_roster        the wrap set is the counted roster at the tips: a resigner is wrapped until cited
    leaving_unread        a count ignores a leaving in its row's past (seat.py's own mutation)
    dissolved_by_roster   dissolution read from the counted roster: two concurrent resignations do not dissolve

    python3 -I check_resignation.py      exit 1 on any difference
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import seat as ST  # noqa: E402

CK, K = ST.CK, ST.K
OBJ, SC, POL = "g", "holder", "accord_majority"
MEM = ("a", "b", "c")
G = ST.offer("g", "a", MEM, SC, "@", "self", cosigners=("b", "c"))
RESIGN = {m: ST.withdraw("w" + m, m, "g", ("g",)) for m in MEM}


def admit(i, who, signers, heads, cites=()):
    return ST.offer(i, signers[0], who, SC, OBJ, "group", tuple(heads) + tuple(cites), head=tuple(heads), policy=POL,
                    counted=SC, cosigners=tuple(signers[1:]) + (who,))


POOL = [RESIGN["a"], RESIGN["b"], RESIGN["c"],
        admit("v1", "d", ("a", "b"), ("g",)),                      # admits d, cites nothing
        admit("v1a", "d", ("b", "c"), ("g",), ("wa",)),            # admits d, cites a's resignation
        admit("v1x", "e", ("a", "b"), ("g",), ("wa",)),            # cites a's resignation and needs a's voice
        ST.unseat("x", "a", "c", SC, OBJ, "group", ("g",), head=("g",), policy="accord_majority", counted=SC, cosigners=("b",)),
        admit("v2", "f", ("b", "d"), ("v1",)),                     # on v1, cites nothing
        admit("v2a", "f", ("b", "d"), ("v1",), ("wa",))]           # on v1, cites a's resignation


def state(rows):
    return CK.concluded(CK.kept(list(rows)), lambda r, P, past: ST.seat_rule(r, P, past))


def wrap(S, plant=None):
    Q = ST.Seats(S)
    if plant == "wrap_by_roster":
        tp = Q.tips(OBJ)
        out = None
        for t in tp:
            sub = [q for q in S.Cs if q["id"] == t["id"] or q["id"] in S.anc[t["id"]]]
            m = ST.Seats(CK.State(sub, {q["id"]: True for q in sub})).holders(SC, OBJ)
            out = m if out is None else out & m
        return out or frozenset()
    return Q.holders(SC, OBJ)


def dissolved(S, plant=None):
    return not wrap(S, "wrap_by_roster" if plant == "dissolved_by_roster" else None)


def counted_over(S, r):
    P = [q for q in S.Cs if q["id"] in S.anc[r["id"]]]
    past = lambda a, b: a in S.anc[b]
    return ST.members_at(P, past, OBJ, r["head"], SC) - ST.left_in_past(P, OBJ, SC), ST.voices(r, P)


def check(plant=None):
    bad = {}
    n = 0
    saved = set(ST.MUT)
    if plant == "leaving_unread":
        ST.MUT.add("leaving_unread")
    try:
        for k in range(len(POOL) + 1):
            for pick in itertools.combinations(POOL, k):
                ids = {r["id"] for r in pick} | {"g"}
                if any(not set(r["names"]) <= ids for r in pick):
                    continue
                if len({r["id"][:2] for r in pick if r["id"].startswith("v1")}) and sum(r["id"].startswith("v1") for r in pick) > 2:
                    continue
                n += 1
                rows = [G] + list(pick)
                S = state(rows)
                held = {m for m in MEM if "w" + m in ids}
                W = wrap(S, plant)
                Q = ST.Seats(S)
                if W & held:
                    bad.setdefault("no_resigner_wrapped", (sorted(ids), sorted(W & held)))
                seated_somewhere = set(MEM) | {r["to"][0] for r in S.Cs if r["kind"] == "offer" and r["id"] != "g"}
                if not W <= seated_somewhere:
                    bad.setdefault("wrap_within_members", (sorted(ids), sorted(W)))
                for r in S.Cs:
                    if r.get("conf") != "group":
                        continue
                    mem, v = counted_over(S, r)
                    for m in MEM:
                        if "w" + m in S.anc[r["id"]] and m in mem:
                            bad.setdefault("cited_is_out", (sorted(ids), r["id"], m))
                        if "w" + m not in S.anc[r["id"]] and m not in mem and r["head"] == ("g",):
                            bad.setdefault("uncited_still_counts", (sorted(ids), r["id"], m))
                # a row that needs a resigner's voice and cites the resignation does not conclude
                if "v1x" in ids and S.C.get("v1x"):
                    bad.setdefault("cited_is_out", (sorted(ids), "v1x", "a's voice counted"))
                live = {r["k"] for r in Q.recs if r["obj"] == OBJ}
                if dissolved(S, plant) != (not (wrap(S) if plant == "dissolved_by_roster" else W)):
                    bad.setdefault("dissolved_by_rows", (sorted(ids), "dissolved differs from the wrap set"))
                if (not live) != dissolved(S, plant):
                    bad.setdefault("dissolved_by_rows", (sorted(ids), "live %s, dissolved %s" % (sorted(live), dissolved(S, plant))))
                if any(t["kind"] == "withdraw" for t in Q.tips(OBJ)):
                    bad.setdefault("resignation_no_head", (sorted(ids),))
                if plant is None and len(rows) <= 6:
                    want = (W, dissolved(S))
                    for p in itertools.permutations(rows[1:]):
                        T2 = CK.arrive([G] + list(p), lambda r, P, past: ST.seat_rule(r, P, past))
                        if (wrap(T2), dissolved(T2)) != want:
                            bad.setdefault("dissolved_by_rows", (sorted(ids), "an arrival order differs"))
                            break
    finally:
        ST.MUT.clear(); ST.MUT |= saved
    return n, bad


# hand-written cases: (name, rows, wrap set, dissolved, {counted row: the members it is counted over})
CASES = [
    ("nobody has resigned", [G], {"a", "b", "c"}, False, {}),
    ("a resigns: not wrapped at once, with no counted row", [G, RESIGN["a"]], {"b", "c"}, False, {}),
    ("a resigns; an admission that does not cite it is still counted over a", [G, RESIGN["a"], POOL[3]], {"b", "c", "d"}, False,
     {"v1": {"a", "b", "c"}}),
    ("an admission citing a's resignation is counted over b and c", [G, RESIGN["a"], POOL[4]], {"b", "c", "d"}, False,
     {"v1a": {"b", "c"}}),
    ("the citation one row late: v1 counts a, v2a on it does not", [G, RESIGN["a"], POOL[3], POOL[8]], {"b", "c", "d", "f"}, False,
     {"v1": {"a", "b", "c"}, "v2a": {"b", "c", "d"}}),
    ("two members resign concurrently at one head", [G, RESIGN["a"], RESIGN["b"]], {"c"}, False, {}),
    ("all three resign: dissolved at a node holding all three", [G, RESIGN["a"], RESIGN["b"], RESIGN["c"]], set(), True, {}),
    ("two resign and the third is removed by a count signed before", [G, RESIGN["a"], RESIGN["b"], POOL[6]], set(), True, {}),
]


def main():
    problems = []
    for name, rows, w, d, counts in CASES:
        S = state(rows)
        got = (set(wrap(S)), dissolved(S), {i: set(counted_over(S, S.by[i])[0]) for i in counts})
        if got != (w, d, counts):
            problems.append("case %s: got %s" % (name, got))
    n, bad = check()
    for p, where in bad.items():
        problems.append("%s: %s" % (p, where))
    caught = 0
    for plant, prop in (("wrap_by_roster", "no_resigner_wrapped"), ("leaving_unread", "cited_is_out"), ("dissolved_by_roster", "dissolved_by_rows")):
        _, b = check(plant)
        ok = prop in b
        caught += ok
        print("  plant %-20s %s (%s)" % (plant, "caught" if ok else "NOT CAUGHT", prop))
        if not ok:
            problems.append("plant %s not caught" % plant)
    for p in problems:
        print(p)
    print("RESULT: %s: %d cases, %d sets of rows, 6 properties, %d of 3 planted breaks caught"
          % ("ok" if not problems else "%d problems" % len(problems), len(CASES), n, caught))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
