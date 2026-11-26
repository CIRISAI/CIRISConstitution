#!/usr/bin/env python3
"""
check_removal_in_force.py: a moderator's lone removal of an AI agent's key is in force only while the end rule says
so (CC 4.5.13 with CC 2.4.1.1 and CC 4.5.5), as seat.py reads it.

A moderator's lone removal is an act under a standing, its `moderate` seat. The end rule of conferral_end.py
(models/tla/CONFERRAL_END.md, E2 to E8) answers it as it answers any act of a holder whose seat then ends. seat.py
re-expresses that rule over seat rows (seat.removal_in_force), and the seat walk counts a lone removal as a live
unseat only where it is in force over the rows held:

    the act     the removal, at the head it names
    the end     a row held that ends the remover's standing: its own laying down of the duty (a withdrawal of
                the offer, of its acceptance, or of its stay), a counted removal of it from the roster, or the
                other holders' counted withdrawal of its duty. Its head h_e: the heads a counted end names; for a
                withdrawal, the newest counted acts on the room in its past
    E7          a seat that gave the remover `moderate` at the act's head is live and has no end held: in force.
                A seat taken up after the act's head authorises nothing earlier, and nothing puts the act back in
                force once each such seat has an end: not the same offer accepted again, not a new conferral
                (CC 2.4.1.1: "from the end's head on it is not in force"; "A receipt ... revives no act"). A
                moderator seated again signs the removal again
    E4          the act has the end in its past: not counted
    E3          the act names a head later than h_e: not counted
    E8          otherwise counted at its own head, and in force only under a receipt of it, an `ack` row naming it,
                by a duty holder at its head other than the remover, that does not have the end in its past
    E2          and with no such receipt, not in force from h_e on
Out of force, the removal ends nothing for that reader: the agent's key is seated again. The answer is a function of
the set (every case is read in arrival orders), and at tips the lines read the removal as the whole set judges it.

Part 1. Cases, each a hand-written answer: which rows conclude, the roster (members and agents), and standings asked
by name. Each kind of end is a case with and without a receipt, and the three kinds answer alike: out of force
unless receipted, and for good (the remover's own laying down, the room's counted removal of it, the other holders'
counted withdrawal of its duty).
Part 2. Planted breaks (seat.MUT), each of which must change a case's answer:
    end_unread       the end is not read: a lone removal stays in force whatever ends its standing
    remover_receipt  a receipt by the remover itself keeps its own removal in force
    count_unread_lone a removal the room's count carries is read as the moderator's lone act
    reseat_revives   the remover holding `moderate` again (its re-acceptance, a new conferral) puts its removal
                     back in force

Not here: a count's own receipt (a counted ack): only duty holders' acks are read; a count end that lifts receipts
(no seat row says so); a receipt by a key removed concurrently; a lone removal whose remover is an agent removed in
turn by a lone removal that is itself out of force (an end is read as a row that concludes; no cascade is run).

    python3 -I check_removal_in_force.py      exit 1 on any difference
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import seat as ST  # noqa: E402
import window as WN  # noqa: E402

CK, R = ST.CK, ST.R
OBJ, OV = "g", "moderation_overturn"
RULE = lambda r, P, past: WN.rule(r, P, past)
T, F = True, False


def admit(i, who, signers, heads, scope="member", cites=()):
    return ST.offer(i, signers[0], who, scope, OBJ, "group", tuple(heads) + tuple(cites), head=tuple(heads),
                    policy="community_invite", cosigners=tuple(signers[1:]) + ((who,) if who not in signers else ()))


def lone(i, by, who, heads, cites=()):
    """A moderator's lone removal of an agent's key, naming the overturn's window."""
    return ST.unseat(i, by, who, "agent", OBJ, "group", tuple(heads) + tuple(cites), head=tuple(heads),
                     policy="community_remove", window=OV)


def remove(i, who, signers, heads, cites=()):
    """The room's counted removal of a person."""
    return ST.unseat(i, signers[0], who, "member", OBJ, "group", tuple(heads) + tuple(cites), head=tuple(heads),
                     policy="community_remove", cosigners=tuple(signers[1:]))


def unduty(i, who, scope, signers, heads):
    """The other holders' counted withdrawal of a duty seat (CC 4.5.4 (iv))."""
    return ST.unseat(i, signers[0], who, scope, OBJ, "group", tuple(heads), head=tuple(heads), policy="duty_withdraw",
                     counted="duty", cosigners=tuple(signers[1:]))


def receipt(i, by, act, names=()):
    """A clean receipt of an act: an `ack` row naming it (`of`)."""
    return R(i, "ack", by, tuple(names) + (act,), of=act)


# three persons, each a founding moderator, and an agent's key admitted at "ag"
G = ST.found("g", "p1", ("p1", "p2", "p3"), {"moderate": ("p1", "p2", "p3")}, cosigners=("p2", "p3"))
W = [G, admit("ag", "AG", ("p1", "p2", "p3"), ("g",), "agent")]
X = lone("x", "p1", "AG", ("ag",))
P3, P23 = {"p1", "p2", "p3"}, {"p2", "p3"}
LAY = ST.withdraw("wm", "p1", "g", ("x",), scope="moderate")             # p1 lays down moderate, after its removal
OUT = remove("xp", "p1", ("p2", "p3"), ("x",))                            # the room's count removes p1
UND = unduty("xm", "p1", "moderate", ("p2", "p3"), ("x",))                # p2 and p3 withdraw p1's moderate
# a moderator by a conferred seat, accepted by its own row: q, admitted and conferred `moderate` by the holders
WQ = W + [admit("aq", "q", ("p1", "p2", "p3"), ("ag",)),
          ST.offer("cq", "p1", "q", "moderate", OBJ, "group", ("aq",), head=("aq",), policy="duty_confer", counted="duty",
                   cosigners=("p2",)),
          ST.accept("acq", "q", "cq"), lone("x", "q", "AG", ("acq",))]
PQ = P3 | {"q"}

# (name, rows, {row: concludes}, roster, [(key, scope, stands)])
CASES = [
    ("the removal with no end held: in force, the agent out", W + [X], {"x": T}, P3, [("p1", "moderate", T)]),
    # ---- the remover lays down its duty ---------------------------------------------------------------------------
    ("the remover lays down moderate after its removal: out of force, the agent seated again",
     W + [X, LAY], {"x": T, "wm": T}, P3 | {"AG"}, [("p1", "moderate", F), ("p1", "member", T)]),
    ("the same with a receipt of the removal by another holder: in force",
     W + [X, receipt("q2", "p2", "x"), LAY], {"x": T}, P3, [("p1", "moderate", F)]),
    ("a receipt that has the end in its past keeps nothing", W + [X, LAY, receipt("q2", "p2", "x", ("wm",))], {"x": T},
     P3 | {"AG"}, []),
    ("a receipt by the remover itself keeps nothing", W + [X, receipt("q1", "p1", "x"), LAY], {"x": T}, P3 | {"AG"}, []),
    ("a receipt by a key that holds no duty keeps nothing",
     W + [admit("an", "n", ("p1", "p2", "p3"), ("ag",)), lone("x", "p1", "AG", ("an",)), receipt("qn", "n", "x"), LAY],
     {"x": T}, P3 | {"n", "AG"}, []),
    ("the remover lays down moderate beside its removal (neither names the other): out of force",
     W + [X, ST.withdraw("wm", "p1", "g", ("ag",), scope="moderate")], {"x": T}, P3 | {"AG"}, []),
    ("the removal names the remover's laying down, at the head before it: it concludes, and is not counted (E4)",
     W + [ST.withdraw("wm", "p1", "g", ("ag",), scope="moderate"), lone("x", "p1", "AG", ("ag",), ("wm",))],
     {"x": T}, P3 | {"AG"}, []),
    ("the same with another holder's receipt of it: still not counted (E4); the receipt has the end in its past through "
     "the removal it names, so it keeps nothing either (E8), and no case can tell E4 from E8 here",
     W + [ST.withdraw("wm", "p1", "g", ("ag",), scope="moderate"), lone("x", "p1", "AG", ("ag",), ("wm",)),
          receipt("q2", "p2", "x")], {"x": T}, P3 | {"AG"}, []),
    ("the removal at a head with the laying down in its past does not conclude (no standing there)",
     W + [ST.withdraw("wm", "p1", "g", ("ag",), scope="moderate"), admit("j", "n", ("p2", "p3"), ("ag",), cites=("wm",)),
          lone("x", "p1", "AG", ("j",))], {"x": F}, P3 | {"n", "AG"}, []),
    ("the remover ends its stay after its removal: out of force",
     W + [X, ST.withdraw("wa", "p1", "g", ("x",))], {"x": T}, P23 | {"AG"}, [("p1", "member", F)]),
    ("a moderator by a conferred seat withdraws its acceptance after its removal: out of force",
     WQ + [ST.withdraw("wq", "q", "acq", ("x",))], {"x": T}, PQ | {"AG"}, [("q", "moderate", F)]),
    ("and accepts the same offer again: it holds moderate, and its removal stays out of force (nothing revives it)",
     WQ + [ST.withdraw("wq", "q", "acq", ("x",)), ST.accept("acq2", "q", "cq", ("wq",))], {"x": T}, PQ | {"AG"}, [("q", "moderate", T)]),
    ("seated again, it signs the removal again: the new removal is in force, the old one is not",
     WQ + [ST.withdraw("wq", "q", "acq", ("x",)), ST.accept("acq2", "q", "cq", ("wq",)), lone("x2", "q", "AG", ("acq2",))],
     {"x": T, "x2": T}, PQ, [("q", "moderate", T)]),
    ("another standing live at the removal's head: p1 holds a conferred moderate seat beside its founding one, lays "
     "the founding one down, then removes the agent: in force (E7)",
     W + [ST.offer("cm", "p2", "p1", "moderate", OBJ, "group", ("ag",), head=("ag",), policy="duty_confer", counted="duty",
                   cosigners=("p3", "p1")), ST.withdraw("wm", "p1", "g", ("cm",), scope="moderate"),
          lone("x", "p1", "AG", ("cm",), ("wm",))], {"cm": T, "x": T}, P3, [("p1", "moderate", T)]),
    # ---- the room's count removes the remover -----------------------------------------------------------------------
    ("the room's count removes the remover after its removal: out of force",
     W + [X, OUT], {"x": T, "xp": T}, P23 | {"AG"}, [("p1", "moderate", F)]),
    ("the same with a receipt by another holder: in force", W + [X, receipt("q2", "p2", "x"), OUT], {"x": T}, P23, []),
    ("the counted removal of a conferred moderator, and its acceptance again: the offer is cut, out of force",
     WQ + [remove("xq", "q", ("p1", "p2", "p3"), ("x",)), ST.accept("acq2", "q", "cq", ("xq",))], {"x": T, "xq": T}, P3 | {"AG"},
     [("q", "moderate", F)]),
    ("re-admitted and conferred `moderate` again: a seat taken up after the removal's head authorises nothing earlier; out of force",
     WQ + [remove("xq", "q", ("p1", "p2", "p3"), ("x",)), admit("aq2", "q", ("p1", "p2", "p3"), ("xq",)),
           ST.offer("cq2", "p1", "q", "moderate", OBJ, "group", ("aq2",), head=("aq2",), policy="duty_confer", counted="duty",
                    cosigners=("p2", "q"))],
     {"x": T, "cq2": T}, PQ | {"AG"}, [("q", "moderate", T)]),
    # ---- the other holders withdraw its duty --------------------------------------------------------------------------
    ("the other holders withdraw the remover's moderate after its removal: out of force",
     W + [X, UND], {"x": T, "xm": T}, P3 | {"AG"}, [("p1", "moderate", F), ("p1", "member", T)]),
    ("the same with a receipt by another holder: in force", W + [X, receipt("q3", "p3", "x"), UND], {"x": T}, P3, []),
    ("a removal the room's count carries, signed by the moderator with another: the count's act, not the moderator's; "
     "the moderator's laying down leaves it in force",
     W + [ST.unseat("x", "p1", "AG", "agent", OBJ, "group", ("ag",), head=("ag",), policy="community_remove",
                    cosigners=("p2",), window=OV), LAY], {"x": T}, P3, [("p1", "moderate", F)]),
    # ---- a removal at a later head than the end ---------------------------------------------------------------------------
    ("the removal names a head later than the end's, without the end in its past: not counted (E3), the agent seated",
     W + [remove("xp", "p1", ("p2", "p3"), ("ag",)), admit("j", "n", ("p2", "p3"), ("ag",)), lone("x", "p1", "AG", ("j",))],
     {"xp": T, "j": T, "x": T}, P23 | {"n", "AG"}, [("p1", "member", F)]),
    ("and a receipt does not bring it back",
     W + [remove("xp", "p1", ("p2", "p3"), ("ag",)), admit("j", "n", ("p2", "p3"), ("ag",)), lone("x", "p1", "AG", ("j",)),
          receipt("q2", "p2", "x")], {"x": T}, P23 | {"n", "AG"}, []),
    # ---- two tips --------------------------------------------------------------------------------------------------------
    ("two tips: the removal and the room's removal of the remover, both at the agent's admission: out of force, the agent seated",
     W + [X, remove("xp", "p1", ("p2", "p3"), ("ag",))], {"x": T, "xp": T}, P23 | {"AG"}, []),
    ("two tips with a receipt of the removal by another holder: in force",
     W + [X, receipt("q2", "p2", "x"), remove("xp", "p1", ("p2", "p3"), ("ag",))], {"x": T, "xp": T}, P23, []),
]
PLANTS = ("end_unread", "remover_receipt", "reseat_revives", "count_unread_lone")


def read(S, case):
    _, _, concl, _, asks = case
    Q = ST.Seats(S)
    return {i: bool(S.C.get(i)) for i in concl}, set(Q.roster(OBJ)), [Q.stands(k, sc, OBJ) for k, sc, _ in asks]


def want(case):
    _, _, concl, roster, asks = case
    return concl, set(roster), [x for _, _, x in asks]


def answers(case):
    return read(CK.concluded(CK.kept(list(case[1])), RULE), case)


def orders(rows):
    tail = rows[1:]
    if len(tail) <= 6:
        return [list(p) for p in itertools.permutations(tail)]
    rnd = random.Random(len(tail))
    out = [tail[::-1]]
    for _ in range(40):
        p = list(tail)
        rnd.shuffle(p)
        out.append(p)
    return out


def main():
    problems, n_orders = [], 0
    for case in CASES:
        got = answers(case)
        if got != want(case):
            problems.append("%s: got %s, expected %s" % (case[0], got, want(case)))
        for p in orders(case[1]):
            n_orders += 1
            if read(CK.arrive([case[1][0]] + p, RULE), case) != got:
                problems.append("%s: order %s differs" % (case[0], [r["id"] for r in p]))
                break
    caught = 0
    for plant in PLANTS:
        ST.MUT.add(plant)
        try:
            hit = [c[0] for c in CASES if answers(c) != want(c)]
        finally:
            ST.MUT.discard(plant)
        caught += bool(hit)
        print("  plant %-16s %s" % (plant, "caught by %d cases, first: %s" % (len(hit), hit[0]) if hit else "NOT CAUGHT"))
        if not hit:
            problems.append("plant %s not caught" % plant)
    for p in problems:
        print(p)
    print("RESULT: %s: %d cases, %d arrival orders, %d of %d planted breaks caught"
          % ("ok" if not problems else "%d problems" % len(problems), len(CASES), n_orders, caught, len(PLANTS)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
