#!/usr/bin/env python3
"""
check_join_audience.py: one command, exit 0 or 1.

    python3 -I check_join_audience.py            run every case and compare with join_audience_expected.tsv
    python3 -I check_join_audience.py --write    write join_audience_expected.tsv from this run
    python3 -I check_join_audience.py --trace ID print one shortest run to each broken property of case ID

Each case is a bounded world and a setting of the rules (join_audience.py). The run is a breadth-first search over
every order of the enabled steps, capped at 2 GiB of address space. It is an enumeration over the stated bound and
nothing more: no case is a proof.

A case is one of four kinds.

    rule      the rules as given. Every property named must hold, and every witness must be reached.
    plant     one rule changed. The property named must break; a plant that breaks nothing fails the check.
    reading   a place where the rules as given admit two readings. Both are run and the difference is printed.
    finding   the rules as given, in a world where a property as stated breaks. The break is expected, printed as a
              FINDING, and the check fails if it stops breaking (the report would then be stale).
"""
import os
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import join_audience as M   # noqa: E402

EXPECTED = os.path.join(HERE, "join_audience_expected.tsv")

# the four properties of the task, and the names the model reads them under
GROUPS = (
    ("1 no deadlock", ("N.join", "N.placed", "N.unplaced")),
    ("2 no disclosure", ("D.relay", "D.room_binding", "D.self_binding", "D.contact_binding", "D.occurrence",
                         "D.occurrence_literal", "D.roster", "D.content", "D.invited_unannounced")),
    ("3 the allow list", ("L.bytes", "L.wrap", "L.sealer")),
    ("4 announcing later", ("A.announce",)),
)
ALL = tuple(p for _g, ps in GROUPS for p in ps)


# ---------------------------------------------------------------- witnesses

def H(w, st, n):
    return st.H[w.idx[n]]


def w_invitee_before_seat(w, rules, st):
    made = M.created(st)
    for j, a in w.invites:
        if ("seat", j) in made:
            continue
        for d in w.devs(j):
            h = H(w, st, d)
            if ("prop", j) in h and ("occ", a) in h and not any(r[0] in ("roster0", "seat") for r in h):
                return True
    return False


def w_relay_carries(w, rules, st):
    z = H(w, st, M.RELAY)
    kinds = set(r[1] for r in z if r[0] == "env")
    return kinds == {"invitation", "answer"} and all(r[0] == "env" for r in z)


def w_seated_and_served(w, rules, st):
    for j, a in w.invites:
        for d in w.devs(j):
            h = H(w, st, d)
            if ("roster0",) in h and ("seat", j) in h and ("bind", a, "room") in h:
                return True
    return False


def w_bytes_and_wrap(w, rules, st):
    for j, _a in w.invites:
        for d in w.devs(j):
            h = H(w, st, d)
            if ("content",) in h and any(r[0] == "wraps" and d in r[1] for r in h):
                return True
    return False


def w_unplaced_served(w, rules, st):
    made = M.created(st)
    for d in w.devices:
        if ("bind", d, "room") not in made and ("roster0",) in H(w, st, d) and ("seat", d[0]) in H(w, st, d):
            return True
    return False


def w_third(w, rules, st):
    return (frozenset("AC") not in st.contacts and ("bind", "C1", "room") in H(w, st, "A1")
            and ("bind", "A1", "room") in H(w, st, "C1"))


def w_outsider(w, rules, st):
    h = H(w, st, "C1")
    return ("bind", "B1", ("contact", "C")) in h and ("occ", "B1") in h and ("seat", "B") in M.created(st)


def _wrap_made(st):
    return [r for r in M.created(st) if r[0] == "wraps"]


def w_wrap_no_bytes(d):
    def pred(w, rules, st):
        h = H(w, st, d)
        return ("content",) not in h and any(r[0] == "wraps" and d in r[1] for r in h)
    return pred


def w_bytes_no_wrap(d):
    def pred(w, rules, st):
        h = H(w, st, d)
        return ("content",) in h and not any(r[0] == "wraps" and d in r[1] for r in h)
    return pred


def w_neither(d):
    def pred(w, rules, st):
        h = H(w, st, d)
        return (bool(_wrap_made(st)) and ("roster0",) in h and ("seat", d[0]) in h and ("content",) not in h
                and not any(r[0] == "wraps" and d in r[1] for r in h))
    return pred


def w_refused(w, rules, st):
    return "refused" in st.flags


def w_absent(p):
    def pred(w, rules, st):
        wr = _wrap_made(st)
        return (bool(wr) and ("sealer_saw", p) in st.flags and all(t[0] != p for r in wr for t in r[1])
                and all(("content",) not in H(w, st, d) for d in w.devs(p))
                and any(("seat", p) in H(w, st, d) for d in w.devs(p)))
    return pred


def w_invited(w, rules, st):
    return any(r[0] == "prop" for r in M.created(st))


def t_deadlock(w, rules, st):
    return ("bind", "B1", "room") not in H(w, st, "A1") and ("roster0",) not in H(w, st, "B1") \
        and ("seat", "B") in M.created(st)


def t_all_served(w, rules, st):
    made, seats, placed = M.truth(w, st)
    return all(j in seats for j, _a in w.invites) and not M.liveness(w, rules, st)


# ---------------------------------------------------------------- worlds

def W(name, people, **kw):
    return M.World(name, people, **kw)


TWO = dict(invites=[("B", "A1")], contacts=[("A", "B")])
two = W("A1 B1, contact A-B, A1 writes", {"A": 1, "B": 1}, author="A1", **TWO)
two_plain = W("A1 B1, contact A-B", {"A": 1, "B": 1}, **TWO)
two_two = W("A1 A2 B1 B2, contact A-B, A1 writes", {"A": 2, "B": 2}, author="A1", **TWO)
three = W("A1 B1 C1, A invites B, B invites C, contacts A-B B-C", {"A": 1, "B": 1, "C": 1},
          invites=[("B", "A1"), ("C", "B1")], contacts=[("A", "B"), ("B", "C")])
outsider = W("A1 B1 C1, A invites B, C outside, contacts A-B B-C", {"A": 1, "B": 1, "C": 1}, author="A1",
             invites=[("B", "A1")], contacts=[("A", "B"), ("B", "C")])
no_contact = W("A1 B1, no contact", {"A": 1, "B": 1}, invites=[("B", "A1")], expect_join=False)
ann_two = W("A1 B1, contact A-B, B may announce, A1 writes", {"A": 1, "B": 1}, author="A1", may_announce=["B"], **TWO)
ann_both = W("A1 B1, contact A-B, A and B may announce", {"A": 1, "B": 1}, may_announce=["A", "B"], **TWO)
ann_three = W("A1 B1 C1, A invites B, B invites C, contacts A-B B-C, C may announce", {"A": 1, "B": 1, "C": 1},
              invites=[("B", "A1"), ("C", "B1")], contacts=[("A", "B"), ("B", "C")], may_announce=["C"])
b_announced = W("A1 B1, B announced, no contact", {"A": 1, "B": 1}, invites=[("B", "A1")], announced=["B"])
a_announced = W("A1 B1, A announced, no contact", {"A": 1, "B": 1}, invites=[("B", "A1")], announced=["A"],
                expect_join=False)


def lists_world(name, lists, author="A1", people=None, answer_on="B1"):
    return W(name, people or {"A": 1, "B": 2}, author=author, lists=lists,
             answer_on={"B": answer_on} if answer_on else None, **TWO)


b_two = lists_world("A1 B1 B2, contact A-B, B answers on B1, A1 writes", {})
node_only = lists_world("A1 B1 B2, B2 node key's list leaves the room out, B answers on B1, A1 writes",
                        {"B2": (False, True)})
roster_only = lists_world("A1 B1 B2, B2 roster key's list leaves the room out, B answers on B1, A1 writes",
                          {"B2": (True, False)})
both_off = lists_world("A1 B1 B2, B2 both lists leave the room out, B answers on B1, A1 writes", {"B2": (False, False)})
all_off = lists_world("A1 B1, B1 both lists leave the room out, A1 writes", {"B1": (False, False)},
                      people={"A": 1, "B": 1})
author_off = lists_world("A1 B1 B2, B2 both lists leave the room out, B answers on B1, B2 writes",
                         {"B2": (False, False)}, author="B2")
author_node_off = lists_world("A1 B1 B2, B2 node key's list leaves the room out, B answers on B1, B2 writes",
                              {"B2": (False, True)}, author="B2")
own_sealer = lists_world("A1 B1 B2, B2 both lists leave the room out, B answers on B1, B1 writes",
                         {"B2": (False, False)}, author="B1")
answers_off = lists_world("A1 B1 B2, B2 node key's list leaves the room out, B answers on B2, A1 writes",
                          {"B2": (False, True)}, answer_on="B2")
late_sealer = lists_world("A1 A2 B1, B1 both lists leave the room out, A2 writes", {"B1": (False, False)},
                          author="A2", people={"A": 2, "B": 1})
b_other = lists_world("A1 B1 B2, contact A-B (made on B1), B answers on B2", {}, author=None, answer_on="B2")
a_two = W("A1 A2 B1, contact A-B, A1 writes", {"A": 2, "B": 1}, author="A1", **TWO)

WIT_JOIN = (("the invitee holds the proposal and the inviter's occurrence, and nothing of the roster", w_invitee_before_seat),
            ("the relay carries both envelopes and holds no row", w_relay_carries),
            ("the joiner is seated and holds the roster and the inviter's binding at the room", w_seated_and_served))
T_SERVED = (("nothing more can move and every seated device holds the room's rows", t_all_served),)
ABSENT = ("the sealer read B as seated, no wrap names a key of B, and no device of B holds the bytes", w_absent("B"))

CASES = [
    # id, kind, world, rules changed, properties expected to break, witnesses, terminal witnesses, never, note
    ("R01", "rule", two, {}, (), WIT_JOIN + (("the joiner's device holds the bytes and a wrap", w_bytes_and_wrap),),
     T_SERVED, (), "two unannounced people, one device each"),
    ("R02", "rule", two, {"resolve": "any"}, (), WIT_JOIN, T_SERVED, (), "the same, a contact's binding resolving too"),
    ("R03", "rule", a_two, {}, (), WIT_JOIN, T_SERVED, (), "the inviter has two devices"),
    ("R04", "rule", b_two, {}, (),
     WIT_JOIN + (("a device with no binding at the room holds the roster, served by its sibling", w_unplaced_served),),
     T_SERVED, (), "the joiner has two devices and answers on one"),
    ("R05", "rule", two_two, {"grain": "batch"}, (),
     WIT_JOIN + (("a device with no binding at the room holds the roster, served by its sibling", w_unplaced_served),),
     T_SERVED, (), "two devices each; deliveries in batches"),
    ("R06", "rule", three, {}, (),
     WIT_JOIN + (("A and C, never contacts, each hold the other's binding at the room", w_third),), T_SERVED, (),
     "a second joiner invited by the first"),
    ("R07", "rule", outsider, {}, (),
     WIT_JOIN + (("C, a contact of B outside the room, holds B's binding addressed to it and B's occurrence", w_outsider),),
     T_SERVED, (), "a contact outside the room"),
    ("R08", "rule", no_contact, {}, (), (), (), (("an invitation exists", w_invited),),
     "no contact exchanged: the unannounced person is never invited"),
    ("R09", "rule", a_announced, {}, (), (), (), (("an invitation exists", w_invited),),
     "the inviter announced, the invitee not, no contact: never invited"),
    ("R10", "rule", ann_two, {}, ("D.occurrence_literal",), WIT_JOIN, T_SERVED, (),
     "the joiner may announce at any point (the literal break is finding F01's)"),
    ("R11", "rule", ann_both, {}, ("D.occurrence_literal",), WIT_JOIN, T_SERVED, (),
     "either may announce at any point (the literal break is finding F01's)"),
    ("R12", "rule", ann_three, {}, ("D.occurrence_literal",), WIT_JOIN, T_SERVED, (),
     "the second joiner may announce at any point (the literal break is finding F01's)"),
    ("L01", "rule", node_only, {}, (),
     (("B2 holds a wrap and no bytes", w_wrap_no_bytes("B2")),), T_SERVED, (),
     "only the node key's list set: the stated consequence"),
    ("L02", "rule", roster_only, {"projection": "closed"}, (),
     (("B2 holds the bytes and no wrap", w_bytes_no_wrap("B2")),), T_SERVED, (),
     "only the roster key's list set, the room told of it"),
    ("L03", "rule", both_off, {"projection": "closed"}, (),
     (("B2 sits in the room and holds neither bytes nor a wrap", w_neither("B2")),), T_SERVED, (),
     "both lists set, the room told of it"),
    ("L04", "rule", all_off, {"projection": "closed"}, (), (ABSENT,), T_SERVED, (),
     "every device of a member kept off, the room told of it: the member reads absent"),
    ("L05", "rule", late_sealer, {"projection": "closed"}, (), (ABSENT,), T_SERVED, (),
     "the same, sealed on a device that is served the joiner's rows one by one"),
    ("L06", "rule", author_off, {}, (), (("the write is refused", w_refused),), T_SERVED, (),
     "the author's own device is kept off"),
    ("L07", "rule", author_node_off, {}, (), (("the write is refused", w_refused),), T_SERVED, (),
     "the author's node key's list alone leaves the room out"),
    ("L08", "rule", own_sealer, {}, (),
     (("B2 sits in the room and holds neither bytes nor a wrap", w_neither("B2")),), T_SERVED, (),
     "the sealer is the owner's other device, which holds the lists at self"),
    ("F01", "finding", b_announced, {}, ("D.occurrence_literal",), WIT_JOIN, T_SERVED, (),
     "an unannounced inviter writes to an announced person who is no contact"),
    ("F02", "finding", roster_only, {}, ("L.sealer",), (("B2 holds the bytes and no wrap", w_bytes_no_wrap("B2")),),
     T_SERVED, (), "the roster key's list, the room told nothing: another member's sealer wraps to the key"),
    ("F03", "finding", all_off, {}, ("L.sealer",), (), T_SERVED, (ABSENT,),
     "every device kept off, the room told nothing: the member does not read absent"),
    ("F04", "finding", answers_off, {}, ("N.unplaced",), (), (), (),
     "the joiner answers on the device kept off the bytes: its other device is never served them"),
    ("G01", "reading", b_announced, {"strict_reply": True}, ("N.join", "D.occurrence_literal"), (), (), (),
     "the answer addressed only to a node the joiner holds a binding of: the join stalls"),
    ("G02", "reading", two_two, {"grain": "batch", "sibling_room_serve": False}, ("N.unplaced",), WIT_JOIN, (), (),
     "a sibling's binding at self resolving no room audience: the joiner's second device is stranded"),
    ("G03", "reading", two_two, {"grain": "batch", "sibling_room_serve": False, "answer_binding": "all"}, (),
     WIT_JOIN, T_SERVED, (), "the same, the answer carrying a binding for each of the joiner's devices"),
    ("G04", "reading", answers_off, {"grain": "batch", "answer_binding": "all"}, (),
     (("B2 holds a wrap and no bytes", w_wrap_no_bytes("B2")),), T_SERVED, (),
     "finding F04's world, the answer carrying a binding for each device; deliveries in batches"),
    ("G05", "reading", node_only, {"node_list_reach": "audience"}, (), (), T_SERVED,
     (("B2 holds a wrap and no bytes", w_wrap_no_bytes("B2")),),
     "the node key's list read as CC 6.1.5.3's first paragraph: outside the audience, so no wrap is held"),
    ("G06", "reading", two_plain, {"resolve": "any", "answer_binding": "none"}, (), WIT_JOIN, T_SERVED, (),
     "a contact's binding resolving: the join closes with no binding in the answer"),
    ("G07", "reading", b_other, {"resolve": "any", "answer_binding": "none"}, (), WIT_JOIN, T_SERVED, (),
     "the same, the joiner answering on a device its contact never met"),
    ("G08", "reading", three, {"resolve": "any", "answer_binding": "none"}, (), WIT_JOIN, T_SERVED, (),
     "the same, a second joiner invited by the first"),
    ("P01", "plant", two_plain, {"answer_binding": "none"}, ("N.placed",), (),
     (("the deadlock: A1 lacks B1's binding, B1 lacks the roster, and nothing more can move", t_deadlock),), (),
     "the answer carries no binding"),
    ("P02", "plant", two_plain, {"invitation_roster": True}, ("D.roster",), (), (), (), "the invitation carries the roster"),
    ("P03", "plant", two_plain, {"link_all_bindings": True},
     ("D.relay", "D.room_binding", "D.self_binding", "D.contact_binding"), (), (), (),
     "a link hands the peer every binding of the node"),
    ("P04", "plant", no_contact, {"occ_public": True},
     ("D.relay", "D.occurrence", "D.occurrence_literal", "D.invited_unannounced"), (), (), (),
     "an occurrence is a public row whatever its bindings"),
    ("P05", "plant", two_plain, {"serve_needs_seat": False}, ("D.room_binding", "D.roster"), (), (), (),
     "a room row is served on the binding alone, before the seat"),
    ("P06", "plant", two, {"serve_needs_binding": False},
     ("D.relay", "D.room_binding", "D.occurrence", "D.occurrence_literal", "D.roster", "D.content"), (), (), (),
     "a room row is served on the node's own word of its owner"),
    ("P07", "plant", both_off, {"projection": "closed", "node_list": False}, ("L.bytes",), (), (), (),
     "the node key's list is read at neither end"),
    ("P08", "plant", both_off, {"projection": "closed", "roster_list": False}, ("L.wrap", "L.sealer"), (), (), (),
     "the roster key's list is read at neither end"),
    ("P09", "plant", author_off, {"refusal": "letter"}, ("L.bytes",), (), (), (),
     "a write refused only when its author has no wrap target at all (CC 5.2 by the letter)"),
    ("P10", "plant", ann_three, {"announce_replaces": True}, ("N.placed", "D.occurrence_literal", "A.announce"), (), (), (),
     "a binding re-signed at federation replaces the row placed at the room"),
    ("P11", "plant", ann_both, {"contact_public": True}, ("D.relay", "D.contact_binding", "D.occurrence_literal"),
     (), (), (), "a row addressed to a contact is served to anyone once its owner announces"),
    ("P12", "plant", late_sealer, {"projection": "open"}, ("L.sealer",), (), (), (),
     "a wrap is made unless a held projection withholds it: the occurrence is served first"),
]


def run_case(case, want_trace=False):
    cid, kind, w, changed, expect, wits, twits, never, note = case
    rules = M.RULES._replace(**changed)
    out = M.explore(w, rules, want_trace=want_trace, witnesses=tuple(wits) + tuple(never), terminal_witnesses=twits)
    broken = dict(out["broken"])
    announce = None
    if w.may_announce:
        quiet = M.World(w.name, w.people, founders=w.founders, invites=w.invites, contacts=[tuple(c) for c in w.contacts],
                        announced=w.announced, may_announce=(), lists=w.lists, author=w.author,
                        expect_join=w.expect_join, answer_on=w.answer_on)
        base = M.explore(quiet, rules)
        with_a = set(M.room_view(w, rules, t) for t in out["terminals"])
        without = set(M.room_view(quiet, rules, t) for t in base["terminals"])
        announce = (len(with_a), len(without), out["announce_late"])
        if with_a != without:
            broken["A.announce"] = ("what the seated devices hold of the room when nothing more can move differs "
                                    "with and without the announce (%d against %d outcomes)" % (len(with_a), len(without)), None)
        out["states"] += base["states"]
    return out, broken, announce


def main():
    args = sys.argv[1:]
    t0 = time.time()
    ok = True
    rows = []
    trace_id = args[args.index("--trace") + 1] if "--trace" in args else None

    def line(good, text):
        nonlocal ok
        ok &= bool(good)
        print("   %s %s" % ("ok  " if good else "FAIL", text))

    print("join_audience: who holds what when people join a room with unannounced devices, and the allow list per key")
    print("bound: one room, 2 or 3 people, 1 or 2 devices each, one stranger relay, one write, every order of the")
    print("       enabled steps; one row per delivery unless the case says batches. An enumeration, not a proof.\n")
    total = 0
    last_kind = None
    titles = {"rule": "THE RULES AS GIVEN", "finding": "FINDINGS: the rules as given, where a property as stated breaks",
              "reading": "READINGS: where the rules as given admit two", "plant": "PLANTED BREAKS: each must be caught"}
    for case in CASES:
        cid, kind, w, changed, expect, wits, twits, never, note = case
        if trace_id and cid != trace_id:
            continue
        if kind != last_kind:
            print(titles[kind])
            last_kind = kind
        out, broken, announce = run_case(case, want_trace=bool(trace_id))
        total += out["states"]
        got = tuple(p for p in ALL if p in broken)
        rules_txt = " ".join("%s=%s" % kv for kv in sorted(changed.items())) or "as given"
        print(" %s  %s" % (cid, note))
        print("      world: %s; rules: %s; %d states, %d where nothing more can move" % (
            w.name, rules_txt, out["states"], len(out["terminals"])))
        if kind == "plant":
            line(set(expect) <= set(got) and got, "caught by %s" % ", ".join(expect))
            line(got == tuple(p for p in ALL if p in expect), "breaks exactly: %s" % (", ".join(got) or "nothing"))
        elif kind == "finding":
            line(got == tuple(p for p in ALL if p in expect), "FINDING, breaks as recorded: %s" % ", ".join(got))
        elif kind == "reading":
            line(got == tuple(p for p in ALL if p in expect), "breaks: %s" % (", ".join(got) or "nothing"))
        else:
            holds = [p for p in ALL if p not in got and (p != "A.announce" or announce)]
            line(got == tuple(p for p in ALL if p in expect),
                 "%d properties hold%s" % (len(holds), ("; breaks as recorded: " + ", ".join(got)) if got else ""))
        for p in got:
            print("        %s: %s" % (p, broken[p][0]))
            if trace_id and broken[p][1] is not None:
                for step in M.trace(out["seen"], broken[p][1]):
                    print("            " + step)
        for name, _pred in tuple(wits) + tuple(twits):
            line(name in out["reached"], "witness reached: %s" % name)
        for name, _pred in never:
            line(name not in out["reached"], "never reached: %s" % name)
        if announce:
            line(announce[2] > 0, "an announce after the last seat is among the orders run (%d such steps); "
                 "%d outcome(s) with the announce, %d without" % (announce[2], announce[0], announce[1]))
        if kind == "rule" and cid == "R01":
            line(out["link_premise"] > 0, "the link rule's premise is reached: %d links leave a binding not placed "
                 "at federation behind" % out["link_premise"])
        rows.append((cid, kind, w.name, rules_txt, str(out["states"]), str(len(out["terminals"])),
                     ",".join(got) or "none",
                     ";".join(sorted(n for n, _p in tuple(wits) + tuple(twits) if n in out["reached"])) or "none"))
    if trace_id:
        return 0
    header = ("case", "kind", "world", "rules", "states", "terminal_states", "breaks", "witnesses_reached")
    text = "\n".join("\t".join(r) for r in [header] + rows) + "\n"
    print("\nTHE RECORD")
    if "--write" in args:
        with open(EXPECTED, "w") as f:
            f.write(text)
        print("   wrote %s" % os.path.relpath(EXPECTED, HERE))
    else:
        with open(EXPECTED) as f:
            line(f.read() == text, "every case gives the states, breaks and witnesses of join_audience_expected.tsv")
    plants = [c for c in CASES if c[1] == "plant"]
    hit = set(p for c in plants for p in c[4])
    line(all(set(ps) & hit for _g, ps in GROUPS),
         "each of the four properties has a planted break that it catches (%d plants)" % len(plants))
    anywhere = set(p for c in CASES for p in c[4])
    line(set(ALL) <= anywhere, "every one of the %d named readings of them breaks in at least one case, so none "
         "holds because nothing reaches it" % len(ALL))
    print("\n%d cases, %d states in all, %.0f s: %s" % (len(rows), total, time.time() - t0,
                                                      "all as recorded" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
