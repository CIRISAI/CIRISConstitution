#!/usr/bin/env python3
"""
check_ceremony.py: the genesis of this edition, a clean mesh, run over the kernel's own modules (ceremony.py imports
formal/causal_kernel).

A small world: an earlier mesh (three holders' earlier keys, an earlier genesis, a community, an agent's earlier
owner-binding, an earlier trust edge, an earlier re-bind, an earlier sealed halt, earlier votes), and then a mesh of
this form signed anew: the holders' key records, the seats' records and bindings, the pre-signed
halts, the genesis, and every person's, node's and agent's record, binding, edge and community after it. Worlds vary
who signs the genesis, a second genesis, the re-binds, the seats' own bindings, the agent's binding and edge,
revocations, and when the pre-signed halts are sealed. Three readers read each world (upgraded with no pin, upgraded
and pinned to the genesis, not upgraded), in ORDERS arrival orders.

Sections, each compared with ceremony_expected.tsv:
    property   P1 to P11. Each world's expected answers are written by the world builder from how the world was made,
               never by the model, and the model must give them. Each property has planted breaks; each break must
               make the property fail in at least one world.
    finding    what the model shows, each computed from a run.
    count      the size of the run.

    python3 -I check_ceremony.py           compare with ceremony_expected.tsv; exit 1 on a difference or an uncaught plant
    python3 -I check_ceremony.py --write   write ceremony_expected.tsv
"""
import itertools
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import ceremony as C  # noqa: E402

ORDERS = 16
NOW = 5
rec, row = C.rec, C.row
HOLD = ("A", "B", "C")
UP, PIN, OLD = ({"upgraded": True}, {"upgraded": True, "pin": "G"}, {"upgraded": False})
READERS = (("up", UP), ("pin", PIN), ("old", OLD))

DEFAULT = dict(gen_voices=HOLD, fork=False, rebind=None, seat_td=False, ob2=True, edge=True, owner_rev=False,
               third_rev=False, revoke_holders=(), halts="before", acts=(), names_earlier=False, custody="separate",
               renew=False, extra_node=False, later=())

K0 = {"A": "A", "B": "B", "C": "C"}
C0 = {"A": "RA", "B": "RB", "C": "RC"}
# Later bundles (CC 2.6.1.11): (id, prev, keys, coms, voices, new keys whose records the world signs). The
# commitment a map holds is the recovery key it commits to.
LATER = {
    "addD": ("G2", "G", dict(K0, D="D"), dict(C0, D="RD"), ("A", "B", "D"), ("D",)),
    "addD_unsigned": ("G2", "G", dict(K0, D="D"), dict(C0, D="RD"), ("A", "B"), ("D",)),
    "removeC_minority": ("G2", "G", {"A": "A", "B": "B"}, {"A": "RA", "B": "RB"}, ("A",), ()),
    "removeC": ("G2", "G", {"A": "A", "B": "B"}, {"A": "RA", "B": "RB"}, ("A", "B"), ()),
    "removeC_fork": ("G2b", "G", {"A": "A", "B": "B"}, {"A": "RA", "B": "RB"}, ("A", "B"), ()),
    "recommitB_unsigned": ("G2", "G", K0, dict(C0, B="RB2"), ("A", "C"), ()),
    "recommitB": ("G2", "G", K0, dict(C0, B="RB2"), ("A", "B"), ()),
    "recover": ("GR", "G", dict(K0, A="A2"), dict(C0, A="RA2"), ("RA",), ("A2",)),
    "recover_by_signing_key": ("GR", "G", dict(K0, A="A2"), dict(C0, A="RA2"), ("A",), ("A2",)),
    "recover_other_seat": ("GR", "G", dict(K0, A="A2", B="B2"), dict(C0, A="RA2"), ("RA",), ("A2", "B2")),
    "recover_same_commitment": ("GR", "G", dict(K0, A="A2"), C0, ("RA",), ("A2",)),
    "recover_spent_returns": ("GR2", "GR", dict(K0, A="A3"), dict(C0, A="RA"), ("RA2",), ("A3",)),
    "recover_fresh": ("GR2", "GR", dict(K0, A="A3"), dict(C0, A="RA3"), ("RA2",), ("A3",)),
    "recover_spent_key": ("GR2", "GR", dict(K0, A="A9"), dict(C0, A="RA9"), ("RA",), ("A9",)),
    "recover_to_reckey": ("GR", "G", dict(K0, A="RA"), dict(C0, A="RA2"), ("RA",), ("RA",)),
    "recover_to_spent_key": ("GR2", "GR", dict(K0, A="RA"), dict(C0, A="RA3"), ("RA2",), ("RA",)),
    "addD_after_recover": ("G3", "GR", dict(K0, A="A2", D="D"), dict(C0, A="RA2", D="RD"), ("A2", "C", "D"), ("D",)),
}


def world(**o):
    o = dict(DEFAULT, **o)
    E = lambda id, kind, signer, names=(), **kw: row(id, kind, signer, names, form="e1", **kw)
    rows = []
    # the earlier mesh: its rows stay as they were signed, and nothing of it comes across
    for k, p, typ in (("a1", "A", "accord_holder"), ("b1", "B", "accord_holder"), ("c1", "C", "accord_holder"),
                      ("u1", "U1", "user"), ("u2", "U2", "user"), ("u3", "U3", "user"), ("ag", "AG", "agent"),
                      ("n1", "N1", "node")):
        rows.append(rec("R" + k, k, typ, form="e1", as_=p))
    rows.append(E("G0", "genesis", "a1", ("Ra1", "Rb1", "Rc1"), voices=("a1", "b1", "c1")))
    rows.append(E("C0", "roster", "u1", ("Ru1", "Ru2", "Ru3"), voices=("u1", "u2", "u3"), members=("u1", "u2", "u3")))
    rows.append(E("OB", "ob", "u2", ("Ru2", "Rag"), owner="u2", target="ag", voices=("u2", "ag")))
    rows.append(E("EG", "edge", "u2", ("G0",)))
    rows.append(E("RBe", "rebind", "a1", ("Rn1",), seat="n1", xw="xwE", voices=("a1", "b1")))
    rows.append(E("HE", "halt", "a1", (), halves=frozenset({"ed", "pq"})))
    rows.append(E("VE", "confer", "b1", (), voices=("b1", "c1")))
    early = list(rows)

    # this form: before the genesis
    F = [rec("F" + h, h, "accord_holder") for h in HOLD]
    F += [rec("FN1", "N1", "node", vf=0, vu=4 if o["renew"] else 10), rec("FN2", "N2", "node", vf=0, vu=10)]
    F += [row("TD1", "td", "N1", ("FN1",), seat="n1", xw="xw1"), row("TD2", "td", "N2", ("FN2",), seat="n2", xw="xw2")]
    halts = [row("PH" + h, "halt", h, ("F" + h,), halves=frozenset({"ed", "pq"}), sealed=True) for h in HOLD]
    gnames = tuple(r["id"] for r in F)
    # the bundle's own count is the seats' canonical conferral: a seat is canonical by its place in `serve`
    G = row("G", "bundle2", "A", gnames, version=1, prev=None, roster=HOLD, serve=("N1", "N2"), coms=C0,
            voices=tuple(o["gen_voices"]))
    pre = F + (halts if o["halts"] == "before" else []) + [G]
    fork = []
    if o["fork"]:
        fork.append(row("TD1b", "td", "N1", ("FN1",), seat="n1", xw="xw1b"))
        fork.append(row("Gb", "bundle2", "A", tuple(n for n in gnames if n not in ("TD1", "TD2")) + ("TD1b",), version=1, prev=None,
                        roster=HOLD, serve=("N1",), coms=C0, voices=HOLD))

    # after the genesis: everyone signs anew
    after = [] if o["halts"] == "before" else list(halts)
    after += [rec("FU1", "U1", "user"), rec("FU2", "U2", "user"), rec("FAG", "AG", "agent", vf=0, vu=10,
                                                                       names=("Rag",) if o["names_earlier"] else ())]
    if o["edge"]:
        after.append(row("EF", "edge", "U2", ("FU2", "G")))
    if o["ob2"]:
        after.append(row("OB2", "ob", "U2", ("FU2", "FAG"), owner="U2", target="AG", voices=("U2", "AG")))
    after.append(rec("FX", "X", "node", vf=0, vu=3))                    # a key whose own record ended before now
    if o["renew"]:
        after.append(rec("FN1r", "N1", "node", vf=3, vu=10))            # a seat's renewed record, after the genesis
    if o["extra_node"]:
        after.append(rec("FN3", "N3", "node", vf=0, vu=10))             # a node the bundle does not seat
    after.append(row("WX", "post", "A", ("FX", "FA")))                  # another key's row naming that record
    after.append(row("CN", "roster", "U1", ("FU1", "FU2"), voices=("U1", "U2"), members=("U1", "U2")))
    if o["owner_rev"]:
        after.append(row("RVo", "revoke", "U2", ("FAG",) + (("OB2",) if o["ob2"] else ()), key="AG"))
    if o["third_rev"]:
        after.append(row("RVx", "revoke", "U1", ("FB",), key="B"))
    for k in o["revoke_holders"]:
        after.append(row("RV" + k, "revoke", k, ("F" + k,), key=k))
    if o["rebind"] == "fwd2":
        after.append(row("RB", "rebind", "A", ("TD1",), seat="n1", xw="xw1n", voices=("A", "B")))
    if o["rebind"] == "fwd1":
        after.append(row("RB", "rebind", "A", ("TD1",), seat="n1", xw="xw1n", voices=("A",)))
    if o["rebind"] == "concurrent":
        after.append(row("RB", "rebind", "A", ("TD1",), seat="n1", xw="xw1n", voices=("A", "B")))
        after.append(row("RBc", "rebind", "B", ("TD1",), seat="n1", xw="xw1m", voices=("B", "C")))
    if o["seat_td"]:
        after.append(row("TDs", "td", "N1", ("FN1",), seat="n1", xw="xw1s"))
    for i, vs in enumerate(o["acts"]):
        after.append(row("Q%d" % i, "confer", vs[0], tuple("F" + k for k in vs), voices=tuple(vs)))
    signed_recs = set()
    for name in o["later"]:
        bid, prev, keys, coms, voices, new = LATER[name]
        recs = []
        for k in new:
            if k not in signed_recs:
                signed_recs.add(k)
                after.append(rec("F" + k, k, "accord_holder"))
            recs.append("F" + k)
        after.append(row(bid, "bundle2", voices[0], (prev,) + tuple(recs), version=2, prev=prev, keys=keys,
                         coms=coms, voices=voices))
    after.append(row("HF", "halt", "A", ("FA",), halves=frozenset({"ed", "pq"})))
    after.append(row("RS", "resume", "A", ("HF",), voices=("A", "B")))
    rows = early + pre + fork + after

    # ---- what the world was made to give (the oracle; the model is never consulted) ----
    x = {}
    x["gen_valid"] = set(o["gen_voices"]) >= set(HOLD)
    x["e1"] = {r["id"] for r in early}
    rev = set(o["revoke_holders"])
    x["live"] = set(HOLD) - rev | {"N1", "N2", "U1", "U2", "AG"}      # only a key ends its own liveness
    xw = {"n1": "xw1", "n2": "xw2"}
    if o["fork"]:
        xw = {"n1": None, "n2": None}                # two geneses: tips hold only what both name
    if o["rebind"] == "fwd2":
        xw["n1"] = "xw1n"
    if o["rebind"] == "concurrent":
        xw["n1"] = None
    x["xw"] = xw if x["gen_valid"] else {"n1": None, "n2": None}
    # canonical standing: the seats every genesis in force lists; a fork leaves what both list
    x["canonical"] = frozenset() if not x["gen_valid"] else frozenset({"N1"} if o["fork"] else {"N1", "N2"})
    x["steward"] = "U2" if o["ob2"] and not o["owner_rev"] else None     # the owner's revocation ends the binding
    x["may_act"] = bool(o["ob2"] and o["edge"] and not o["owner_rev"])
    x["members"] = frozenset({"U1", "U2"})
    x["live_holders"] = set(HOLD) - rev
    # the lineage: which later bundles count, and the roster at its head, from how the world was made
    ROSTERS = {"addD": ({"G2"}, "ABCD"), "addD_unsigned": (set(), "ABC"), "removeC_minority": (set(), "ABC"),
               "removeC": ({"G2"}, "AB"), "removeC_fork": ({"G2", "G2b"}, "AB"), "recommitB_unsigned": (set(), "ABC"), "recommitB": ({"G2"}, "ABC"),
               "recover": ({"GR"}, ("A2", "B", "C")), "recover_by_signing_key": (set(), "ABC"),
               "recover_other_seat": (set(), "ABC"), "recover_same_commitment": (set(), "ABC"),
               "recover_to_reckey": (set(), "ABC")}
    want_b, want_r = set(), frozenset(HOLD)
    names = tuple(o["later"])
    if names:
        key = names[-1] if names[-1] in ROSTERS else None
        if key:
            want_b, r = ROSTERS[key]
            want_r = frozenset(r)
        elif names[0] == "recover":       # a second bundle on the recovery
            second = {"recover_spent_returns": (set(), ("A2", "B", "C")),
                      "recover_fresh": ({"GR2"}, ("A3", "B", "C")),
                      "recover_spent_key": (set(), ("A2", "B", "C")),
                      "recover_to_spent_key": (set(), ("A2", "B", "C")),
                      "addD_after_recover": ({"G3"}, ("A2", "B", "C", "D"))}[names[1]]
            want_b, want_r = {"GR"} | second[0], frozenset(second[1])
    x["bundles"], x["roster"] = frozenset(want_b), want_r
    return rows, x, o


def shuffles(rows, n, seed):
    rnd = random.Random(seed)
    out = [list(rows)]
    for _ in range(n - 1):
        r = list(rows)
        rnd.shuffle(r)
        out.append(r)
    return out


def run(rows, reader, order=None):
    order = order or rows
    first = {r["id"]: i for i, r in enumerate(order)}
    return C.answers(order, reader, NOW, first)


# ---- the properties ----------------------------------------------------------------------------------------
def worlds_p1():
    yield dict()
    yield dict(names_earlier=True)
    yield dict(fork=True)


def p1(o, orders):
    """No earlier-form row counts for anything, in any arrival order, before or after a node holds the genesis; a node
    not upgraded reads only the earlier form."""
    rows, x, o = world(**o)
    gi = [r["id"] for r in rows].index("G")
    for order in orders(rows):
        for rd in (UP, PIN):
            for held in (order, [r for r in order if r["id"] not in ("G", "Gb")]):
                a = run(held, rd, order)
                if a["accepted"]:
                    return False
                if o["names_earlier"] and "AG" in a["live"]:
                    return False                     # a row of this form that names an earlier row is refused
        a = run(rows, OLD, order)
        if a["accepted"] or a["cut"] or a["live"]:
            return False
    return gi >= 0


def worlds_p2():
    for orv, trv in itertools.product((False, True), (False, True)):
        yield dict(owner_rev=orv, third_rev=trv)
    yield dict(revoke_holders=("C",))


def p2(o, orders):
    """A key is live only by its own record of this form. No row of another key makes it live, and only its own
    revocation ends it: an owner's revocation ends the owner-binding, never the key (CC 2.4.1.1)."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a = run(rows, PIN, order)
        if a["live"] != frozenset(x["live"]):
            return False
        for k in ("a1", "u1", "ag"):
            if k in a["live"]:
                return False
    return True


def worlds_p3():
    yield dict(acts=[("A",), ("A", "B")])
    yield dict(acts=[("A",)], revoke_holders=("B", "C"))
    yield dict(gen_voices=("A", "B"))


def p3(o, orders):
    """The accord's count holds from the genesis: every holder signs it, the roster is the holders it lists, and no act
    counts on fewer than a strict majority of them, whoever has since lost a key."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a = run(rows, PIN, order)
        if not x["gen_valid"]:
            if a["cut"] or a["counted"]:
                return False
            continue
        if a["roster"] != frozenset(HOLD):
            return False
        for r in rows:
            if r["kind"] in ("confer", "resume", "rebind") and r["form"] == "e2":
                want = len(set(r["voices"]) & x["live_holders"]) >= 2
                if want != (r["id"] in a["counted"]):
                    return False
            if r["form"] == "e1" and r["id"] in a["counted"]:
                return False
    return True


def devices(custody):
    tok, med = {("a1", "ed"), ("a1", "pq"), ("A", "ed")}, {("A", "pq")}   # the earlier key held both on the token
    if custody == "same_element":
        tok.add(("A", "pq"))
    return {"token": tok, "media": med}


def worlds_p4():
    yield dict()


def p4(o, orders, custody="separate"):
    """No single device yields a halt: a halt needs both halves of a holder's live composite key, and a halt of the
    earlier form is refused."""
    rows, x, o = world(**o)
    for d, halves in devices(custody).items():
        forged = []
        for k in {k for k, _ in halves}:
            hs = frozenset(h for kk, h in halves if kk == k)
            if k == "a1":
                forged.append(row("Hx" + d, "halt", "a1", (), form="e1", halves=hs))
            else:
                forged.append(row("Hy" + d, "halt", k, ("F" + k,), halves=hs))
        for order in orders(rows):
            a = run(rows + forged, PIN, order + forged)
            if a["honoured"] & {f["id"] for f in forged}:
                return False
    return True


def worlds_p5():
    for rb, st in itertools.product((None, "fwd2", "fwd1", "concurrent"), (False, True)):
        yield dict(rebind=rb, seat_td=st)
    yield dict(fork=True)
    yield dict(renew=True, extra_node=True)
    yield dict(gen_voices=("A", "B"))


def p5(o, orders):
    """A seat is canonical by its place in the genesis in force, whose count is the conferral, through its own
    record's renewals; it has one transit key from the genesis, the one its binding there carries, moved only by a
    re-bind the holders' count signs; two counted keys leave none until a row names both."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a = run(rows, UP, order)
        if dict(a["seats"]) != x["xw"] or a["canonical"] != x["canonical"]:
            return False
    return True


def worlds_p6():
    for ob2, edge, orv in itertools.product((True, False), (True, False), (False, True)):
        yield dict(ob2=ob2, edge=edge, owner_rev=orv)


def p6(o, orders):
    """An agent has no standing until its steward-binding of this form exists, and then acts only with its steward's
    edge of this form: fail-secure at every point."""
    rows, x, o = world(**o)
    for i in range(1, len(rows) + 1):
        a = run(rows[:i], PIN)
        held = {r["id"] for r in rows[:i]}
        if dict(a["may_act"]).get("AG") and not ({"OB2", "EF"} <= held):
            return False
        if dict(a["steward"]).get("AG") is not None and "OB2" not in held:
            return False
    for order in orders(rows):
        a = run(rows, PIN, order)
        if dict(a["steward"]).get("AG") != x["steward"] or dict(a["may_act"]).get("AG") != x["may_act"]:
            return False
        if a["members"] != x["members"]:
            return False
    return True


def worlds_p7():
    yield dict(fork=True)


def p7(o, orders):
    """Two geneses are a fork (CC 2.7.8): a reader with no pin holds both as tips and takes only what they share; a
    reader that pinned one holds the other void."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a, b = run(rows, UP, order), run(rows, PIN, order)
        if a["cut"] != ("G", "Gb") or a["void"] != () or dict(a["seats"]) != {"n1": None, "n2": None}:
            return False
        if a["canonical"] != frozenset({"N1"}) or b["canonical"] != frozenset({"N1", "N2"}):
            return False
        if b["cut"] != ("G",) or b["void"] != ("Gb",) or dict(b["seats"]) != {"n1": "xw1", "n2": "xw2"}:
            return False
    return True


def worlds_p8():
    yield dict(halts="before")
    yield dict(halts="after")


def p8(o, orders):
    """A halt of this form is available from the first moment after the genesis: every holder has sealed one before
    the genesis is published, and a node that holds the genesis honours it."""
    rows, x, o = world(**o)
    t = C.publishable(rows, HOLD)
    gi = [r["id"] for r in t].index("G")
    before = t[:gi + 1]
    sealed = [r for r in before if r["kind"] == "halt" and r.get("sealed")]
    if {r["signer"] for r in sealed} != set(HOLD):
        return False
    pub = [r for r in before if not r.get("sealed")]
    for h in sealed:
        if h["id"] not in run(pub + [h], PIN)["honoured"]:
            return False
    return True


def worlds_p9():
    yield dict()
    yield dict(fork=True)
    yield dict(rebind="concurrent", seat_td=True, owner_rev=True)
    yield dict(later=("recover", "addD_after_recover"))


def p9(o, orders):
    """The result does not depend on the order in which a node receives the rows."""
    rows, x, o = world(**o)
    for _, rd in READERS:
        seen = None
        for order in orders(rows):
            a = run(rows, rd, order)
            if seen is not None and a != seen:
                return False
            seen = a
    return True


def worlds_p10():
    for n in ("addD", "addD_unsigned", "removeC_minority", "removeC", "recommitB_unsigned", "recommitB"):
        yield dict(later=(n,))
    yield dict(later=("recover", "addD_after_recover"))
    yield dict(later=("addD", "removeC_fork"))          # a fork of later bundles: tips, and what both name


def p10(o, orders):
    """A roster change is a later bundle, counted at a strict majority of the predecessor's holders, with each holder
    it adds and each holder whose commitment it changes; a count not met changes nothing."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a = run(rows, PIN, order)
        if a["bundles"] != x["bundles"] or a["roster"] != x["roster"]:
            return False
    return True


def worlds_p11():
    for n in ("recover", "recover_by_signing_key", "recover_other_seat", "recover_same_commitment", "recover_to_reckey"):
        yield dict(later=(n,))
    for n in ("recover_spent_returns", "recover_fresh", "recover_spent_key", "recover_to_spent_key"):
        yield dict(later=("recover", n))


def p11(o, orders):
    """A recovery is a later bundle signed by the recovery key alone, the one the commitment in force commits to; it
    changes that holder's key and next commitment and nothing else; the next commitment differs from the spent one, a
    spent commitment never returns, and a recovery key never becomes a seat's key."""
    rows, x, o = world(**o)
    for order in orders(rows):
        a = run(rows, PIN, order)
        if a["bundles"] != x["bundles"] or a["roster"] != x["roster"]:
            return False
        if any(k.startswith("R") for k in a["roster"]):
            return False
    return True


PROPS = [
    ("P1", "no earlier-form row counts for anything, in any arrival order", p1, worlds_p1,
     ("earlier_until_genesis", "earlier_named")),
    ("P2", "a key is live only by its own record of this form, and only its own revocation ends it", p2, worlds_p2,
     ("earlier_record_live", "named_makes_live", "third_party_ends", "owner_revocation_ends")),
    ("P3", "the accord's count holds from the genesis, which every holder signs", p3, worlds_p3,
     ("genesis_majority", "roster_shrinks", "earlier_votes")),
    ("P4", "no single device yields a halt", p4, worlds_p4, ("one_half_verifies", "earlier_halt")),
    ("P5", "a seat is canonical by the genesis's count and has one transit key from it, moved only by the holders' count",
     p5, worlds_p5, ("seat_alone_td", "one_holder_rebind", "pick_one", "earlier_rebind", "canonical_self_claimed",
                     "canonical_ends_with_record")),
    ("P6", "an agent has no standing until its steward-binding of this form exists", p6, worlds_p6,
     ("earlier_binding", "act_without_steward", "earlier_roster", "owner_revocation_ignored")),
    ("P7", "two geneses are a fork: tips to a reader with no pin, the other void to one that pinned", p7, worlds_p7,
     ("fork_union", "pinned_ignored")),
    ("P8", "a halt of this form is available from the first moment after the genesis", p8, worlds_p8,
     ("publish_ungated",)),
    ("P9", "the result does not depend on the order in which a node receives the rows", p9, worlds_p9,
     ("by_arrival", "fork_first")),
    ("P10", "a roster change is a later bundle, counted at a strict majority of the predecessor's holders and by each "
     "holder it adds or re-commits", p10, worlds_p10, ("change_minority", "added_unsigned", "recommit_unsigned", "fork_union")),
    ("P11", "a recovery is the recovery key's statement alone and changes only its own seat; a spent commitment never "
     "returns, and a recovery key never becomes a seat's key", p11, worlds_p11,
     ("recovery_any_key", "recovery_other_seat", "spent_returns", "spent_key_recovers", "reckey_as_seat")),
]


def holds(fn, worlds, orders):
    return all(fn(o, orders) for o in worlds())


def findings(orders):
    out = []
    C.MUT.clear()
    rows, x, o = world()
    a, b = run(rows, OLD), run(rows, PIN)
    out.append(("F1 a node not upgraded and an upgraded node holding the same rows",
                "share no row" if not (a["accepted"] | a["counted"]) & (b["accepted"] | b["counted"]) else "share rows"))
    rows, x, o = world(gen_voices=("A", "B"))
    out.append(("F2 a genesis two of three holders signed", "no genesis" if not run(rows, PIN)["cut"] else "a genesis"))
    rows, x, o = world(ob2=False)
    out.append(("F3 an agent whose steward signed no binding of this form",
                "no steward, may not act" if not dict(run(rows, PIN)["may_act"])["AG"] else "may act"))
    rows, x, o = world(edge=False)
    out.append(("F4 an agent whose steward signed no edge of this form",
                "may not act" if not dict(run(rows, PIN)["may_act"])["AG"] else "may act"))
    rows, x, o = world(owner_rev=True)
    a = run(rows, PIN)
    out.append(("F5 an owner's revocation of the agent key it owns",
                ("the key stays live" if "AG" in a["live"] else "the key ends") + ("; the binding ends"
                 if dict(a["steward"]).get("AG") is None else "; the binding stands")))
    rows, x, o = world()
    out.append(("F6 the earlier sealed halt, published after the genesis",
                "refused" if "HE" not in run(rows, PIN)["honoured"] else "honoured"))
    out.append(("F7 a holder's composite key with both halves on the token",
                "one device yields a halt" if not p4(dict(), orders, custody="same_element") else "no device yields"))
    rows, x, o = world(halts="after")
    t = C.publishable(rows, HOLD)
    out.append(("F8 halts sealed after the genesis was signed",
                "the genesis is held back until they exist" if [r["id"] for r in t].index("G") >
                max(i for i, r in enumerate(t) if r.get("sealed")) else "published first"))
    rows, x, o = world()
    out.append(("F9 the earlier community", "no member of this form" if not run(rows, PIN)["members"] - {"U1", "U2"}
                and "u1" not in run(rows, PIN)["members"] else "carried"))
    return out


def main():
    write = "--write" in sys.argv
    t0 = time.time()
    orders = lambda rows: shuffles(rows, ORDERS, 7)
    lines, bad, evals = [], [], [0]
    real = C.answers

    def counting(*a, **k):
        evals[0] += 1
        return real(*a, **k)

    C.answers = counting
    nworlds = 0
    for pid, text, fn, worlds, plants in PROPS:
        C.MUT.clear()
        nworlds += sum(1 for _ in worlds())
        ok = holds(fn, worlds, orders)
        caught = []
        for m in plants:
            C.MUT.clear()
            C.MUT.add(m)
            caught.append(not holds(fn, worlds, orders))
        C.MUT.clear()
        if not ok:
            bad.append(pid + " does not hold")
        for m, c in zip(plants, caught):
            if not c:
                bad.append(pid + " plant " + m + " not caught")
        lines.append("property\t%s %s\t%s\t%s" % (pid, text, "holds" if ok else "broken",
                                                 " ".join("%s=%s" % (m, "caught" if c else "missed")
                                                          for m, c in zip(plants, caught))))
    for name, v in findings(orders):
        lines.append("finding\t%s\t%s" % (name, v))
    lines.append("count\tworlds %d, arrival orders per world and reader %d, readers 3\t%d answers computed" % (
        nworlds, ORDERS, evals[0]))
    C.answers = real
    path = os.path.join(HERE, "ceremony_expected.tsv")
    for l in lines:
        print(l)
    if write:
        open(path, "w").write("\n".join(lines) + "\n")
        print("wrote ceremony_expected.tsv (%d lines)" % len(lines))
    else:
        want = open(path).read().splitlines() if os.path.exists(path) else []
        for l in sorted(set(want) ^ set(lines)):
            bad.append("differs from ceremony_expected.tsv: %s %s" % ("expected" if l in want else "now", l))
    print("ceremony: %d properties, %d planted breaks, %.1fs" % (len(PROPS), sum(len(p[4]) for p in PROPS), time.time() - t0))
    if bad:
        for b in bad:
            print("  " + b)
        print("ceremony check: %d problems" % len(bad))
        sys.exit(1)
    print("ceremony check: every property holds and every planted break is caught")


if __name__ == "__main__":
    main()
