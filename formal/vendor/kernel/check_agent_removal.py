#!/usr/bin/env python3
"""
check_agent_removal.py: a moderator's lone removal of an AI agent's key and the members' lift of it (CC 4.5.13),
with the two counts of the same clause: the members' check and the moderation fallback.

The text: "no single key removes a member alone, and no duty holder removes another from the roster alone. ... An AI
agent's key is the exception. A moderator of the room MAY remove it alone and at once, and the members may lift that
act as they may any act of a moderator."

    the removal    a counted unseat of an agent's seat (scope `agent`: the seat's scope says whose key it is),
                   signed by a holder of `moderate` over the room at the head it names: it concludes on that one
                   voice (seat.seat_rule). The agent's key is admitted in scope `agent` (check_agent_seat.py)
    its window     the removal names the window `moderation_overturn` and is its opener (window.rule)
    the lift       "a strict majority of the members seated at the head the act names, the act's author apart",
                   by objecting, never fewer than two voices; the author's own objection is no voice and the
                   author is not counted over. The key removed is apart too: it is an agent's, and every count
                   of the room is by person (seat.counted_keys), so it is no voice and is not counted over, on every
                   path (the count with no landing, a landing, the recount, the re-seating). The window then reads
                   `lifted`, and the key is still out
    the re-seating a counted offer of policy `moderation_overturn` that seats the key again, cites the removal, names
                   the head it names and names objections: it concludes when those objections meet that same count.
                   It seats the key only with the key's own signature

Part 1. Cases, each a hand-written answer: which rows conclude, the roster (Seats.roster: members and agents), and
each window's outcome. Every case is
read as one batch and again in arrival orders of its rows (all of them up to six rows above the founding one, else
the batch order, its reverse and forty shuffles).

Part 2. Planted breaks in the seat rule, each of which must change a case's answer:
    agent_unread       the seat's scope is not read: a person's seat may be removed alone by a moderator
    moderator_unread   the signer's duty is not read: any key removes an agent's key alone
    author_voice       the removal's author's objection is a voice of the re-seating
    agent_voice        an agent's signature is a voice of a count (the removed key's objection counts)
    lift_over_all      the re-seating is counted over the whole roster, the author with it (the reading ruled out)
    restores_unseated  the re-seating seats a key that was not on the roster at the head the removal names (the
                       lone removal's own test that the key holds an agent's seat there, seen from the lift)
    agent_counted_over an agent is counted over, in the window and in the re-seating (the removed key with it)
    lift_no_floor      the re-seating has no floor of two voices

Part 3. The window adversary table (window.adversary_table) under recount reads no property broken, and planted
breaks in the tables, each of which must break a row of it:
    fallback_of_all    the fallback is a strict majority of all members (the clause until now)
    fallback_no_floor  the fallback has no floor of two voices
    overturn_all       the author's objection is a voice of the lift, and the author counted over (the base `all`,
                       the clause until now)
    overturn_whole_roster  the author is no voice and is still counted over (the reading ruled out)
    vote_beside_answer a moderator's vote beside its answer makes the answer two things said

Not here: a re-seating row beside a second removal at tips (one tips case is here: an admission beside the
re-seating); agents' keys in the room's other counts (check_agent_seat.py).

    python3 -I check_agent_removal.py      exit 1 on any difference
"""
import copy
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import seat as ST  # noqa: E402
import window as WN  # noqa: E402

CK = ST.CK
OBJ, OV = "g", "moderation_overturn"
RULE = lambda r, P, past: WN.rule(r, P, past)


def admit(i, who, signers, head, scope="member"):
    """An admission, the joiner cosigning (its own yes). Scope `agent`: an AI agent's key, admitted by the persons'
    count; its own signature is its consent and no voice."""
    return ST.offer(i, signers[0], who, scope, OBJ, "group", (head,), head=(head,), policy="community_invite",
                    cosigners=tuple(signers[1:]) + (who,))


def remove(i, by, who, head, scope="agent", window=True):
    """A removal from the roster by one key, naming the overturn's window. `scope`: the seat removed, an agent's
    (`agent`) or a person's (`member`); the seat's scope says whose key it is."""
    kw = {"window": OV} if window else {}
    return ST.unseat(i, by, who, scope, OBJ, "group", (head,), head=(head,), policy="community_remove", **kw)


def obj(i, by, removal="x"):
    return WN.answer(i, by, removal, "object")


def reseat(i, by, who, removal, head, objections, accepted=True, cite=True):
    return ST.offer(i, by, who, "agent", OBJ, "group", (removal,) + tuple(objections), head=(head,), policy=OV,
                    cosigners=(who,) if accepted else (), **({"content": removal} if cite else {}))


# ---- world A: a room founded with members only. Members m1 and m2, the agent's key AG, and MOD, admitted and then
# conferred `moderate` by the members' count: a duty seat stands only on a member in every room (CC 4.5.4), so MOD is
# a member. World B has the duty-founded case.
GA = ST.offer("g", "m1", ("m1", "m2"), "member", "@", "self", cosigners=("m2",))
AGA = admit("ag", "AG", ("m1", "m2"), "g", "agent")
AMA = admit("am", "MOD", ("m1", "m2"), "ag")
MDA = ST.offer("md", "m1", "MOD", "moderate", OBJ, "group", ("am",), head=("am",), policy="community_invite",
               cosigners=("m2", "MOD"))
A = [GA, AGA, AMA, MDA]
XA = remove("x", "MOD", "AG", "md")
O1, O2, OA, OM = obj("o1", "m1"), obj("o2", "m2"), obj("oA", "AG"), obj("oM", "MOD")
RSA = reseat("rs", "m1", "AG", "x", "md", ("o1", "o2"))
X2 = remove("x2", "MOD", "AG", "rs")

# ---- world B: the moderator is on the roster. Duty holders m1..m4 (each a member and a moderator) and AG: five ----
GB = ST.offer("g", "m1", ("m1", "m2", "m3", "m4"), "duty", "@", "self", cosigners=("m2", "m3", "m4"))
AGB = admit("ag", "AG", ("m1", "m2", "m3"), "g", "agent")
B = [GB, AGB]
XB = remove("x", "m1", "AG", "ag")
O3, O4 = obj("o3", "m3"), obj("o4", "m4")
# a moderator conferred by the duty holders: a duty seat stands only on a member (CC 4.5.4), so MOD is admitted first
AMB = admit("am", "MOD", ("m1", "m2", "m3", "m4"), "ag")
MDB = ST.offer("md", "m1", "MOD", "moderate", OBJ, "group", ("am",), head=("am",), policy="duty_confer", counted="duty",
               cosigners=("m2", "m3", "MOD"))
MDB0 = dict(MDB, names=("ag",), head=("ag",))                                  # the same conferral, MOD not admitted

# ---- world C: three duty holders and AG, a roster of four with the moderator on it ----------------------------------
GC = ST.offer("g", "m1", ("m1", "m2", "m3"), "duty", "@", "self", cosigners=("m2", "m3"))
AGC = admit("ag", "AG", ("m1", "m2"), "g", "agent")
C = [GC, AGC]

# ---- world D: two duty holders and AG -----------------------------------------------------------------------------
GD = ST.offer("g", "m1", ("m1", "m2"), "duty", "@", "self", cosigners=("m2",))
D = [GD, admit("ag", "AG", ("m1", "m2"), "g", "agent")]

T, F = True, False
# (name, rows, {row: concludes}, the roster, {window: outcome})
CASES = [
    ("A: before any removal the agent's key is on the roster", A, {}, {"m1", "m2", "MOD", "AG"}, {}),
    ("A: a moderator removes an agent's key alone: out at once, and its window is open",
     A + [XA], {"x": T}, {"m1", "m2", "MOD"}, {"x": "open"}),
    ("A: a moderator removes a person's key alone: nothing",
     A + [remove("x", "MOD", "m2", "md", scope="member")], {"x": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: a moderator's unseat of the agent's key in scope member (a seat it does not hold): nothing",
     A + [remove("x", "MOD", "AG", "md", scope="member")], {"x": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: a member who is no moderator removes an agent's key alone: nothing",
     A + [remove("x", "m1", "AG", "md")], {"x": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: the same row naming no window, read by the seat rule alone: nothing",
     A + [remove("x", "m1", "AG", "md", window=False)], {"x": F}, {"m1", "m2", "MOD", "AG"}, {}),
    ("A: a moderator's removal naming no window concludes all the same",
     A + [remove("x", "MOD", "AG", "md", window=False)], {"x": T}, {"m1", "m2", "MOD"}, {}),
    ("A: a key with no seat removes an agent's key alone: nothing",
     A + [remove("x", "z", "AG", "md")], {"x": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: a former moderator, at a head after its own withdrawal: nothing",
     A + [ST.withdraw("wm", "MOD", "md", ("md",)), remove("x", "MOD", "AG", "wm")], {"x": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: one of the two persons objects, one of two: the window is open, the key out",
     A + [XA, O1], {"x": T}, {"m1", "m2", "MOD"}, {"x": "open"}),
    ("A: both persons object, two of two: the window reads lifted, and the key is still out",
     A + [XA, O1, O2], {"x": T}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: the re-seating row naming those two objections concludes and the key is seated again",
     A + [XA, O1, O2, RSA], {"x": T, "rs": T}, {"m1", "m2", "MOD", "AG"}, {"x": "lifted"}),
    ("A: a re-seating row naming one objection of the two does not conclude",
     A + [XA, O1, O2, reseat("rs", "m1", "AG", "x", "md", ("o1",))], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: the removed key's own objection is no voice: of the window with no landing, nor of the re-seating",
     A + [XA, O1, OA, reseat("rs", "m1", "AG", "x", "md", ("o1", "oA"))], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "open"}),
    ("A: nor of a landing: a member lands 'lifted' naming its own objection and the removed key's",
     A + [XA, O1, OA, WN.receipt("r", "m1", "x", 0), WN.landing("L", "m1", "x", "r", "lifted", 0, ("o1", "oA"))],
     {"x": T, "L": F}, {"m1", "m2", "MOD"}, {"x": "open"}),
    ("A: nor of the recount: 'stands' lands at the close over one objection; the removed key objects, unnamed",
     A + [XA, O1, WN.receipt("r", "m2", "x", 0), WN.landing("L", "m2", "x", "r", "stands", WN.secs(OV), ("o1",)), OA],
     {"x": T, "L": T}, {"m1", "m2", "MOD"}, {"x": "stands"}),
    ("A: the removed key objects beside both persons: lifted on the two, as without it",
     A + [XA, O1, O2, OA, reseat("rs", "m1", "AG", "x", "md", ("o1", "o2", "oA"))], {"rs": T}, {"m1", "m2", "MOD", "AG"}, {"x": "lifted"}),
    ("A: the moderator's own objection is no voice (it is the act's author)",
     A + [XA, O1, OM, reseat("rs", "m1", "AG", "x", "md", ("o1", "oM"))], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "open"}),
    ("A: a re-seating row that does not cite the removal does not conclude",
     A + [XA, O1, O2, reseat("rs", "m1", "AG", "x", "md", ("o1", "o2"), cite=False)], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: a re-seating row at another head than the removal names does not conclude",
     A + [XA, O1, O2, reseat("rs", "m1", "AG", "x", "x", ("o1", "o2"))], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: a re-seating row seating another key than the one removed does not conclude",
     A + [XA, O1, O2, reseat("rs", "m1", "Q", "x", "md", ("o1", "o2"))], {"rs": F}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: a re-seating row without the key's own signature concludes and seats nobody (two consents)",
     A + [XA, O1, O2, reseat("rs", "m1", "AG", "x", "md", ("o1", "o2"), accepted=False)], {"rs": T}, {"m1", "m2", "MOD"}, {"x": "lifted"}),
    ("A: objections to a removal that did not conclude re-seat nothing and remove nothing",
     A + [remove("x", "m1", "AG", "md"), O1, O2, RSA], {"x": F, "rs": F}, {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: after the lift the moderator removes the key again, naming the re-seating: out, and a new window is open",
     A + [XA, O1, O2, RSA, X2], {"x": T, "rs": T, "x2": T}, {"m1", "m2", "MOD"}, {"x": "lifted", "x2": "open"}),
    ("A: after the lift an admission at the re-seating's head signed by one person and the agent concludes nothing: the agent is no voice",
     A + [XA, O1, O2, RSA, admit("j", "N", ("m1", "AG"), "rs")], {"rs": T, "j": F}, {"m1", "m2", "MOD", "AG"}, {"x": "lifted"}),
    ("A: the same admission signed by both persons concludes",
     A + [XA, O1, O2, RSA, admit("j", "N", ("m1", "m2"), "rs")], {"rs": T, "j": T}, {"m1", "m2", "MOD", "AG", "N"}, {"x": "lifted"}),
    ("A: the objections to the first removal do not lift the second",
     A + [XA, O1, O2, RSA, X2, reseat("rs2", "m1", "AG", "x2", "rs", ("o1", "o2"))], {"x2": T, "rs2": F}, {"m1", "m2", "MOD"},
     {"x": "lifted", "x2": "open"}),
    ("A: a moderator 'removes' a key that was never seated: no agent's seat at that head, so nothing concludes, and "
     "objections and a re-seating admit nothing",
     A + [remove("x", "MOD", "Q", "md"), O1, O2, reseat("rs", "m1", "Q", "x", "md", ("o1", "o2"))], {"x": F, "rs": F},
     {"m1", "m2", "MOD", "AG"}, {"x": "none"}),
    ("A: at tips, an admission at the removal beside the re-seating: the fold seats the key on its two objectors' voices",
     A + [XA, O1, O2, RSA, admit("j", "N", ("m1", "m2"), "x")], {"rs": T, "j": T}, {"m1", "m2", "MOD", "AG", "N"}, {"x": "lifted"}),
    ("A: at tips, the same admission beside a re-seating that does not conclude: the key stays out",
     A + [XA, O1, reseat("rs", "m1", "AG", "x", "md", ("o1",)), admit("j", "N", ("m1", "m2"), "x")], {"rs": F, "j": T},
     {"m1", "m2", "MOD", "N"}, {"x": "open"}),
    ("B: a duty holder removes an agent's key alone: out at once",
     B + [XB], {"x": T}, {"m1", "m2", "m3", "m4"}, {"x": "open"}),
    ("B: a moderator conferred on a key that is no member removes an agent's key alone: nothing (it holds no duty)",
     B + [MDB0, remove("x", "MOD", "AG", "md")], {"x": F}, {"m1", "m2", "m3", "m4", "AG"}, {"x": "none"}),
    ("B: the same key admitted first and then conferred `moderate` removes an agent's key alone: out at once",
     B + [AMB, MDB, remove("x", "MOD", "AG", "md")], {"am": T, "md": T, "x": T}, {"m1", "m2", "m3", "m4", "MOD"},
     {"x": "open"}),
    ("B: a duty holder removes another duty holder alone: nothing",
     B + [remove("x", "m1", "m2", "ag", scope="member")], {"x": F}, {"m1", "m2", "m3", "m4", "AG"}, {"x": "none"}),
    ("B: one person and the author object: one voice of the three persons, and the author is no voice",
     B + [XB, O1, O2, reseat("rs", "m2", "AG", "x", "ag", ("o1", "o2"))], {"x": T, "rs": F}, {"m1", "m2", "m3", "m4"},
     {"x": "open"}),
    ("B: two of the three other persons object, the removed key apart: lifted, and the re-seating concludes",
     B + [XB, O2, O3, reseat("rs", "m2", "AG", "x", "ag", ("o2", "o3"))], {"x": T, "rs": T},
     {"m1", "m2", "m3", "m4", "AG"}, {"x": "lifted"}),
    ("C: the moderator, the agent and two persons: both persons object, two of two, and it lifts",
     C + [remove("x", "m1", "AG", "ag"), O2, O3, reseat("rs", "m2", "AG", "x", "ag", ("o2", "o3"))], {"x": T, "rs": T},
     {"m1", "m2", "m3", "AG"}, {"x": "lifted"}),
    ("C: one person and the removed key object: one voice of two, and nothing lifts",
     C + [remove("x", "m1", "AG", "ag"), O2, OA, reseat("rs", "m2", "AG", "x", "ag", ("o2", "oA"))], {"x": T, "rs": F},
     {"m1", "m2", "m3"}, {"x": "open"}),
    ("D: the moderator, the agent and one person: the person objects, and the floor of two holds",
     D + [remove("x", "m1", "AG", "ag"), O2, reseat("rs", "m2", "AG", "x", "ag", ("o2",))], {"x": T, "rs": F},
     {"m1", "m2"}, {"x": "open"}),
    ("C: one of the two persons objects: nothing lifts (one of two is no strict majority, and the floor is two)",
     C + [remove("x", "m1", "AG", "ag"), O2, reseat("rs", "m2", "AG", "x", "ag", ("o2",))], {"x": T, "rs": F},
     {"m1", "m2", "m3"}, {"x": "open"}),
]
SEAT_PLANTS = ("agent_unread", "moderator_unread", "author_voice", "agent_voice", "lift_over_all", "restores_unseated", "agent_counted_over",
               "lift_no_floor")


def read(S, concl, wins):
    Q = ST.Seats(S)
    return ({i: bool(S.C.get(i)) for i in concl}, set(Q.roster(OBJ)),
            {w: WN.outcome(S, w, "recount") for w in wins})


def answers(rows, concl, wins):
    return read(CK.concluded(CK.kept(list(rows)), RULE), concl, wins)


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


def with_tables(change):
    """The adversary table with the window tables changed by `change(WINDOWS)`; the tables are restored."""
    saved, mut = copy.deepcopy(WN.WINDOWS), set(WN.MUT)
    try:
        change(WN.WINDOWS)
        return [t for t in WN.adversary_table() if t["needs"] is not None and not t["holds"]["recount"]]
    finally:
        WN.WINDOWS.clear(); WN.WINDOWS.update(saved)
        WN.MUT.clear(); WN.MUT.update(mut)


def clause(window, where, **kw):
    def change(W):
        v, how, over, out = W[window][where][0]
        W[window][where] = ((v, kw.get("how", how), kw.get("over", over), out),)
    return change


TABLE_PLANTS = (
    ("fallback_of_all", clause("moderation_fallback", "at_close", how="strict")),
    ("fallback_no_floor", clause("moderation_fallback", "at_close", how=("voted", 1, 2, 0, "against"))),
    ("overturn_all", clause("moderation_overturn", "at_once", over="all")),
    ("overturn_whole_roster", lambda W: WN.MUT.add("overturn_whole_roster")),
    ("vote_beside_answer", lambda W: WN.MUT.add("vote_beside_answer")),
)


def main():
    problems, n_orders = [], 0
    for name, rows, concl, roster, wins in CASES:
        got = answers(rows, concl, wins)
        if got != (concl, roster, wins):
            problems.append("%s: got %s, expected %s" % (name, got, (concl, roster, wins)))
        for p in orders(rows):
            n_orders += 1
            if read(CK.arrive([rows[0]] + p, RULE), concl, wins) != got:
                problems.append("%s: order %s differs" % (name, [r["id"] for r in p]))
                break
    caught = 0
    for plant in SEAT_PLANTS:
        ST.MUT.add(plant)
        try:
            hit = [name for name, rows, concl, roster, wins in CASES if answers(rows, concl, wins) != (concl, roster, wins)]
        finally:
            ST.MUT.discard(plant)
        caught += bool(hit)
        print("  plant %-18s %s" % (plant, "caught by: %s" % hit[0] if hit else "NOT CAUGHT"))
        if not hit:
            problems.append("plant %s not caught" % plant)
    table = WN.adversary_table()
    checks = [t for t in table if t["needs"] is not None]
    for t in checks:
        if not t["holds"]["recount"]:
            problems.append("adversary table, recount BROKEN: %s: %s" % (t["window"], t["case"]))
    broke = {h: sum(not t["holds"][h] for t in checks) for h in WN.RULES}
    tcaught = 0
    for plant, change in TABLE_PLANTS:
        hit = with_tables(change)
        tcaught += bool(hit)
        print("  plant %-18s %s" % (plant, "caught by %d rows, first: %s" % (len(hit), hit[0]["case"]) if hit else "NOT CAUGHT"))
        if not hit:
            problems.append("table plant %s not caught" % plant)
    for p in problems:
        print(p)
    print("RESULT: %s: %d cases, %d arrival orders, %d of %d planted breaks in the seat rule caught; adversary table %d rows, "
          "%d checks, broken under recount %d, void %d, contest %d; %d of %d planted breaks in the tables caught"
          % ("ok" if not problems else "%d problems" % len(problems), len(CASES), n_orders, caught, len(SEAT_PLANTS),
             len(table), len(checks), broke["recount"], broke["void"], broke["contest"], tcaught, len(TABLE_PLANTS)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
