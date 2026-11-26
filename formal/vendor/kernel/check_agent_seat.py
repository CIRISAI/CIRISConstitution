#!/usr/bin/env python3
"""
check_agent_seat.py: an AI agent's key has a seat of its own kind, on the roster and in no count (CC 4.5.13), as
seat.py reads it.

The text: an agent "acts under its own key and has no vote"; "a recall and an election count its persons alone";
every count of a room is by person. So (seat.py):

    the seat      an agent's key is seated over the room in scope `agent` (seat.AGENT), by an admission the room's
                  persons count; its own signature on that row is its consent and no voice
    the roster    `Seats.roster(o)` is the room's whole roster, members and agents: content, wraps and audience
                  read it (the wrap set of check_resignation.py is the live seats, so it holds the agent).
                  `Seats.holders("member", o)` holds no agent, and no count reads the roster
    no count      every count of the room is taken of persons (seat.counted_keys): an agent's key is no voice and
                  is not counted over, in an admission, a removal, a duty conferral or withdrawal, and a window's
                  count (window.py reads the same keys), whatever other seat it holds
    a duty        an agent may hold a duty conferred on it, by its own duty seat; the duty-seat rule asks for its
                  `agent` seat as the roster's seat. It acts alone within that duty like any holder, and is still
                  no voice in a count, the count over duty holders included
    removal       the room's count removes an agent's key as it removes any key; a moderator removes it alone
                  (check_agent_removal.py), keyed on the unseat's scope being `agent`. A person's seat is not
                  removed so
    resignation   an agent's withdrawal of its own seat ends it, and with it the duty seats in its past

Part 1. Cases, each a hand-written answer, read as one batch and again in arrival orders of the rows (all of them up
to six rows above the founding one, else the batch order, its reverse and forty shuffles). Each case states which
rows conclude, the members, the roster, and standings asked by name. The numbers are chosen so that counting the
agent changes the answer: one person and an agent, where the person's one voice is the whole count, and rooms where
the agent's signature would complete a count.

Part 2. Planted breaks (seat.MUT), each of which must change a case's answer:
    agent_voice          the agent's signature is a voice of a count
    agent_counted_over   the agent is counted over (in the denominator) and is no voice
    agent_unread         a moderator's lone removal reaches a person's seat (the scope is not read)
    lone_any_key         a moderator's lone removal in scope agent reaches a key that holds no agent's seat
    roster_cut_any_scope an unseat of a roster scope the key does not hold ends its duty seats
    stay_scope_ungated   a withdrawal naming a roster scope ends the stay whatever seat its target gives
    scope_keeps_agents   a window's counted clause over a named scope (moderate) keeps its agents (window.py)
    one_leaves_agents    a window's clause one holder's act resolves leaves out an agent's act (window.py)

    python3 -I check_agent_seat.py      exit 1 on any difference
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

CK = ST.CK
OBJ, OV = "g", "moderation_overturn"
RULE = lambda r, P, past: WN.rule(r, P, past)
T, F = True, False


def admit(i, who, signers, heads, scope="member", cites=()):
    """An admission of `who` in `scope`, signed by `signers`, the joiner cosigning (its consent)."""
    return ST.offer(i, signers[0], who, scope, OBJ, "group", tuple(heads) + tuple(cites), head=tuple(heads),
                    policy="community_invite", cosigners=tuple(signers[1:]) + ((who,) if who not in signers else ()))


def remove(i, who, signers, heads, scope="member"):
    return ST.unseat(i, signers[0], who, scope, OBJ, "group", tuple(heads), head=tuple(heads), policy="community_remove",
                     cosigners=tuple(signers[1:]))


def confer(i, k, scope, signers, heads):
    """A duty seat conferred by the duty holders' count (CC 4.5.4 (iv)), the holder cosigning."""
    return ST.offer(i, signers[0], k, scope, OBJ, "group", tuple(heads), head=tuple(heads), policy="duty_confer",
                    counted="duty", cosigners=tuple(signers[1:]) + ((k,) if k not in signers else ()))


def chain(n):
    """n agents' keys admitted by one counted row, then a moderator's n lone removals of them, each naming the one
    before as its head (each concludes: its key still holds its agent's seat there)."""
    ks = tuple("A%d" % i for i in range(n))
    rows, prev = [ST.offer("ags", "p1", ks, "agent", OBJ, "group", ("g",), head=("g",), policy="community_invite",
                           cosigners=("p2", "p3") + ks)], "ags"
    for i in range(n):
        rows.append(lone("x%d" % i, "p1", ks[i], (prev,)))
        prev = "x%d" % i
    return rows


def lone(i, by, who, heads, scope="agent"):
    """A removal by one key, naming the overturn's window (a moderator's lone removal where `who` is an agent's)."""
    return ST.unseat(i, by, who, scope, OBJ, "group", tuple(heads), head=tuple(heads), policy="community_remove", window=OV)


# one person (p1, the founder and moderator) and an agent
G1 = ST.found("g", "p1", ("p1",), {"moderate": ("p1",)})
W1 = [G1, admit("ag", "AG", ("p1",), ("g",), "agent")]
# two persons (p1 moderates) and an agent
G2 = ST.found("g", "p1", ("p1", "p2"), {"moderate": ("p1",)}, cosigners=("p2",))
W2 = [G2, admit("ag", "AG", ("p1", "p2"), ("g",), "agent")]
# three persons (p1 and p2 moderate) and an agent
G3 = ST.found("g", "p1", ("p1", "p2", "p3"), {"moderate": ("p1", "p2")}, cosigners=("p2", "p3"))
W3 = [G3, admit("ag", "AG", ("p1", "p2", "p3"), ("g",), "agent")]
# W3 with the agent holding `review`, conferred by the two duty holders
W3R = W3 + [confer("cr", "AG", "review", ("p1", "p2"), ("ag",))]
P1, P2, P3 = {"p1"}, {"p1", "p2"}, {"p1", "p2", "p3"}

# (name, rows, {row: concludes}, members, roster, [(key, scope, stands)], {window: outcome})
CASES = [
    ("an agent seated: on the roster, no member", W2, {"ag": T}, P2, P2 | {"AG"},
     [("AG", "agent", T), ("AG", "member", F)], {}),
    ("its admission is the persons' count: one person of two and the agent's own yes do not admit it",
     [G2, admit("ag", "AG", ("p1",), ("g",), "agent")], {"ag": F}, P2, P2, [("AG", "agent", F)], {}),
    ("one person and an agent: the person's one voice admits a member (one of one; with the agent counted over, one of two)",
     W1 + [admit("j", "N", ("p1",), ("ag",))], {"j": T}, {"p1", "N"}, {"p1", "N", "AG"}, [], {}),
    ("two persons and an agent: one person and the agent sign an admission, one voice of two, and nothing is admitted",
     W2 + [admit("j", "N", ("p1", "AG"), ("ag",))], {"j": F}, P2, P2 | {"AG"}, [], {}),
    ("three persons and an agent: one person and the agent sign an admission, one voice of three, and nothing is admitted",
     W3 + [admit("j", "N", ("p1", "AG"), ("ag",))], {"j": F}, P3, P3 | {"AG"}, [], {}),
    ("three persons and an agent: two persons remove the third, two of three (with the agent counted over, two of four)",
     W3 + [remove("x", "p3", ("p1", "p2"), ("ag",))], {"x": T}, P2, P2 | {"AG"}, [], {}),
    ("three persons and an agent: one person and the agent sign a removal, one voice of three, and nobody is removed",
     W3 + [remove("x", "p3", ("p1", "AG"), ("ag",))], {"x": F}, P3, P3 | {"AG"}, [], {}),
    ("an agent holding a conferred duty is a duty holder by its duty seat, and stands on its agent seat",
     W3R, {"cr": T}, P3, P3 | {"AG"}, [("AG", "review", T), ("AG", "duty", T), ("AG", "member", F)], {}),
    ("its signature on a duty conferral is no voice: p1 and the agent of the holders p1 and p2 confer nothing",
     W3R + [confer("cd", "p3", "takedown", ("p1", "AG"), ("cr",))], {"cd": F}, P3, P3 | {"AG"}, [("p3", "takedown", F)], {}),
    ("and it is not counted over: with one person duty holder, that holder's count confers (one of one, not one of two)",
     W1 + [confer("cr", "AG", "review", ("p1",), ("ag",)), admit("j", "N", ("p1",), ("cr",)), confer("cd", "N", "takedown", ("p1",), ("j",))],
     {"cr": T, "j": T, "cd": T}, {"p1", "N"}, {"p1", "N", "AG"}, [("N", "takedown", T), ("AG", "review", T)], {}),
    ("a lone duty holder confers alone, an agent holding a duty beside it",
     W1 + [confer("cr", "AG", "review", ("p1",), ("ag",)), admit("j", "N", ("p1",), ("cr",)),
           ST.offer("cd", "p1", "N", "takedown", OBJ, "self", ("j",), cosigners=("N",))],
     {"cd": T}, {"p1", "N"}, {"p1", "N", "AG"}, [("N", "takedown", T)], {}),
    ("its signature on a window answer is no voice: p2 and a second agent object to p1's removal of the agent, and nothing lifts",
     W3 + [admit("ag2", "AG2", ("p1", "p2", "p3"), ("ag",), "agent"), lone("x", "p1", "AG", ("ag2",)),
           WN.answer("o2", "p2", "x", "object"), WN.answer("oa", "AG2", "x", "object")],
     {"x": T}, P3, P3 | {"AG2"}, [], {"x": "open"}),
    ("an agent holding `moderate` removes another agent's key alone",
     W3 + [admit("ag2", "AG2", ("p1", "p2", "p3"), ("ag",), "agent"), confer("cm", "AG", "moderate", ("p1", "p2"), ("ag2",)),
           lone("x", "AG", "AG2", ("cm",))],
     {"cm": T, "x": T}, P3, P3 | {"AG"}, [("AG", "moderate", T)], {"x": "open"}),
    ("a moderator removes an agent's key alone", W3 + [lone("x", "p1", "AG", ("ag",))], {"x": T}, P3, P3, [], {"x": "open"}),
    ("a moderator does not remove a person alone", W3 + [lone("x", "p1", "p3", ("ag",), "member")], {"x": F}, P3, P3 | {"AG"}, [],
     {"x": "none"}),
    ("a key that is no moderator does not remove an agent's key alone", W3 + [lone("x", "p3", "AG", ("ag",))], {"x": F}, P3,
     P3 | {"AG"}, [], {"x": "none"}),
    ("the room's count removes an agent's key, as any key: two of three persons",
     W3 + [remove("x", "AG", ("p2", "p3"), ("ag",), "agent")], {"x": T}, P3, P3, [("AG", "agent", F)], {}),
    ("an agent resigns: off the roster and out of the wrap set, and its duty seat in that resignation's past ends",
     W3R + [ST.withdraw("wa", "AG", "ag", ("cr",))], {"wa": T}, P3, P3, [("AG", "review", F), ("AG", "agent", F)], {}),
    # ---- the review of 2026-11-25 -----------------------------------------------------------------------------------
    ("a moderator's lone removal in scope agent of a person's key ends nothing: the key holds no agent's seat",
     W3 + [lone("x", "p1", "p2", ("ag",))], {"x": F}, P3, P3 | {"AG"}, [("p2", "moderate", T)], {"x": "none"}),
    ("a moderator's unseat of an agent's key in scope member (a seat it does not hold) concludes nothing",
     W3 + [lone("x", "p1", "AG", ("ag",), "member")], {"x": F}, P3, P3 | {"AG"}, [], {"x": "none"}),
    ("the room's count unseats a person's key in scope agent, a seat it does not hold: its stay and duty seats stand",
     W3 + [remove("x", "p1", ("p2", "p3"), ("ag",), "agent")], {"x": T}, P3, P3 | {"AG"}, [("p1", "moderate", T)], {}),
    ("a person's withdrawal of the founding row naming scope agent, a seat the row does not give it, ends nothing",
     W3 + [ST.withdraw("w", "p2", "g", ("ag",), scope="agent")], {"w": T}, P3, P3 | {"AG"}, [("p2", "moderate", T)], {}),
    ("an agent holding moderate acts under it: its answer to a fallback, a clause one holder's act resolves, closes it",
     W3 + [confer("cm", "AG", "moderate", ("p1", "p2"), ("ag",)), WN.opener("op", "p3", "moderation_fallback", OBJ, ("cm",)),
           WN.answer("an", "AG", "op", "answered")], {"cm": T}, P3, P3 | {"AG"}, [("AG", "moderate", T)], {"op": "answered"}),
    ("one person moderator and one agent moderator: the person is the lone holder, and withdraws the agent's duty alone",
     W1 + [confer("cm", "AG", "moderate", ("p1",), ("ag",)),
           ST.unseat("xm", "p1", "AG", "moderate", OBJ, "group", ("cm",), head=("cm",), policy="duty_withdraw", counted="duty")],
     {"cm": T, "xm": T}, P1, P1 | {"AG"}, [("AG", "moderate", F), ("p1", "moderate", T)], {}),
    ("an agent removed from the room by its count holds no duty from that end",
     W3R + [remove("x", "AG", ("p2", "p3"), ("cr",), "agent")], {"x": T}, P3, P3, [("AG", "review", F), ("AG", "duty", F)], {}),
    ("an agent removed by a moderator alone holds no duty from that end",
     W3R + [lone("x", "p1", "AG", ("cr",))], {"x": T}, P3, P3, [("AG", "review", F)], {"x": "open"}),
    ("a chain of twelve lone removals of the agent, each naming the one before, is read in polynomial time",
     [G3] + chain(12), {"x0": T, "x11": T}, P3, P3, [("p1", "moderate", T), ("A11", "agent", F)], {}),
    ("an agent's duty seat stands only on its agent seat: conferred before the agent is admitted, it waits",
     [G3, confer("cr", "AG", "review", ("p1", "p2"), ("g",))], {"cr": T}, P3, P3, [("AG", "review", F)], {}),
]
PLANTS = ("agent_voice", "agent_counted_over", "agent_unread", "lone_any_key", "roster_cut_any_scope", "stay_scope_ungated",
          "one_leaves_agents")      # scope_keeps_agents is caught by COUNTED_CASE, read in main()
# A counted clause over moderate (no table of the policy has one, so this window is the check's own and is not in
# the fixture): a strict majority of the moderators approves. p1 and the agent moderator approve; the moderators
# counted are the persons p1 and p2, so one of two, and nothing lands.
COUNTED = {"policy": "moderation_action", "counted": "member", "concluder": "member", "opener_says": None,
           "at_once": (("approve", "strict", "moderate", "landed"),), "silent": None, "at_close": (), "default": "lapsed"}
COUNTED_CASE = ("an agent holding moderate is out of a counted clause over moderate: p1 and the agent approve, one of two",
                W3 + [confer("cm", "AG", "moderate", ("p1", "p2"), ("ag",)),
                      WN.opener("op", "p3", "test_counted_moderate", OBJ, ("cm",)),
                      WN.answer("a1", "p1", "op", "approve"), WN.answer("a2", "AG", "op", "approve")],
                {"cm": T}, P3, P3 | {"AG"}, [], {"op": "open"})


def read(S, case):
    _, _, concl, _, _, asks, wins = case
    Q = ST.Seats(S)
    return ({i: bool(S.C.get(i)) for i in concl}, set(Q.holders("member", OBJ)), set(Q.roster(OBJ)),
            [Q.stands(k, sc, OBJ) for k, sc, _ in asks], {w: WN.outcome(S, w, "recount") for w in wins})


def want(case):
    _, _, concl, mem, roster, asks, wins = case
    return (concl, set(mem), set(roster), [x for _, _, x in asks], wins)


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
    WN.WINDOWS["test_counted_moderate"] = COUNTED
    try:
        if answers(COUNTED_CASE) != want(COUNTED_CASE):
            problems.append("%s: got %s" % (COUNTED_CASE[0], answers(COUNTED_CASE)))
        WN.MUT.add("scope_keeps_agents")
        if answers(COUNTED_CASE) == want(COUNTED_CASE):
            problems.append("plant scope_keeps_agents not caught by the counted clause")
    finally:
        WN.MUT.discard("scope_keeps_agents")
        del WN.WINDOWS["test_counted_moderate"]
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
        ST.MUT.add(plant); WN.MUT.add(plant)
        try:
            hit = [c[0] for c in CASES if answers(c) != want(c)]
        finally:
            ST.MUT.discard(plant); WN.MUT.discard(plant)
        caught += bool(hit)
        print("  plant %-20s %s" % (plant, "caught by %d cases, first: %s" % (len(hit), hit[0]) if hit else "NOT CAUGHT"))
        if not hit:
            problems.append("plant %s not caught" % plant)
    for p in problems:
        print(p)
    print("RESULT: %s: %d cases, %d arrival orders, %d of %d planted breaks caught"
          % ("ok" if not problems else "%d problems" % len(problems), len(CASES), n_orders, caught, len(PLANTS)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
