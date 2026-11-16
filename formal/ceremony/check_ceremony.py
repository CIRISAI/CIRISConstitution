#!/usr/bin/env python3
"""
check_ceremony.py: the edition-2 ceremony run over the kernel's own modules (ceremony.py imports formal/causal_kernel).

A small world: an earlier-form lineage (a genesis, three accord holders, two seats, a community with members, an agent
with its steward, a key that revoked itself), the ceremony's rows, and rows after it. Worlds vary the holders' paths
(carry the same halves, rotate to fresh halves, both, never), the re-binds, the bundle's transit rows, the agent's
bindings, a second ceremony row, and halts. Each world is read by three readers (upgraded with no pin, upgraded and
pinned to the ceremony row, not upgraded) in ORDERS arrival orders.

Sections, each compared with ceremony_expected.tsv:
    property   P1 to P9. Each world's expected answers are written by the world builder from how the world was made,
               never by the model, and the model must give them. Each property has planted breaks; each break must
               make the property fail in at least one world.
    finding    what the model shows about the text: places where it is silent or where two sentences disagree,
               each computed from a run, never stated.
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
HOLD = ("a1", "b1", "c1")
UP, PIN, OLD = ({"upgraded": True}, {"upgraded": True, "pin": "CR"}, {"upgraded": False})
READERS = (("up", UP), ("pin", PIN), ("old", OLD))


# ---- the world ---------------------------------------------------------------------------------------------
DEFAULT = dict(paths=("same", "same", "same"), custody="separate", inner=True, late=True, back=True, rb="pair",
               td_bundle="match", seat_td=None, ob_carried=True, ob2=True, agent_rec=True, steward_reg=True,
               edge_carried=True, revoked_reg=True, fork=None, halts="none", acts=False, count="all", revoke_holders=(), third_rev=False, owner_rev=False)


def fkeys(h, path):
    """The keys of this form a holder makes, by path."""
    up = h[0].upper()
    return {"same": [up], "rotate": [up + "r"], "both": [up, up + "r"], "never": []}[path]


def world(**o):
    o = dict(DEFAULT, **o)
    T = itertools.count(1)
    E = lambda id, kind, signer, names=(), **kw: row(id, kind, signer, names, form="e1", at=next(T), **kw)
    rows, carried, direct = [], set(), set()
    mat = lambda k: (k + "e", k + "p")

    # the earlier form
    for k, typ in (("a1", "accord_holder"), ("b1", "accord_holder"), ("c1", "accord_holder"), ("n1", "node"),
                   ("n2", "node"), ("u1", "user"), ("u2", "user"), ("u3", "user"), ("ag", "agent"), ("kz", "user")):
        rows.append(dict(rec("R" + k, k, mat(k), typ, form="e1"), at=next(T)))
    rows.append(E("G0", "genesis", "a1", ("Ra1", "Rb1", "Rc1", "Rn1", "Rn2"), roster=HOLD, seats=("n1", "n2"),
                  voices=HOLD))
    rows.append(E("EG", "edge", "u2", ("G0",)))
    rows.append(E("C0", "roster", "u1", ("Ru1", "Ru2", "Ru3"), voices=("u1", "u2", "u3"), members=("u1", "u2", "u3")))
    rows.append(E("OB", "ob", "u2", ("Ru2", "Rag"), owner="u2", target="ag", voices=("u2", "ag")))
    rows.append(E("C1", "roster", "u1", ("C0", "OB"), voices=("u1", "u2"), members=("u1", "u2", "u3", "ag")))
    rows.append(E("V3", "post", "u3", ("C1",)))
    rows.append(E("REVz", "revoke", "kz", ("Rkz",), key="kz"))
    rb1v = ("a1",) if o["rb"] == "one" else ("a1", "b1")
    rows.append(E("RB1", "rebind", "a1", ("Rn1",), seat="n1", xw="xw1", voices=rb1v))
    rows.append(E("RB2", "rebind", "b1", ("Rn2",), seat="n2", xw="xw2", voices=("b1", "c1")))
    if o["rb"] == "concurrent":
        rows.append(E("RB1b", "rebind", "b1", ("Rn1",), seat="n1", xw="xw1b", voices=("b1", "c1")))
    if o["inner"]:
        rows.append(E("X0", "post", "u1", ("C1",)))
        rows.append(E("X1", "post", "u1", ("X0",)))
    if o["halts"] == "sealed":
        rows.append(E("Hs", "halt", "a1", (), halves=frozenset({"ed", "pq"})))      # sealed now, published later
    e1 = [r["id"] for r in rows]
    carried = set(e1) - {"X0", "Hs"} - ({"RB1"} if o["rb"] == "outside" else set())
    carried -= set() if o["ob_carried"] else {"OB"}
    carried -= set() if o["edge_carried"] else {"EG"}
    carried -= {"RB1", "RB2", "RB1b", "G0"}                       # these the ceremony names directly
    late = []
    if o["late"]:
        late.append(E("L", "post", "u1", ("C1",)))                 # signed after the acknowledgement: not carried
    if o["halts"] == "late":
        late.append(E("HL", "halt", "a1", (), halves=frozenset({"ed", "pq"})))   # fired after the acknowledgement

    # the ceremony's rows, before the ceremony row
    hk, F = {}, []
    for h, p in zip(HOLD, o["paths"]):
        hk[h] = fkeys(h, p)
        for k in hk[h]:
            if k.endswith("r"):
                F.append(rec("F" + k, k, mat(k), "accord_holder", names=("R" + h,), succ_of=h, sigs={k, h}))
            else:
                F.append(rec("F" + k, k, mat(h), "accord_holder", names=("R" + h,)))
    hv = [ks[-1] for ks in hk.values() if ks]                        # one statement per holder that has a key
    allv = [k for ks in hk.values() for k in ks]
    first = F[0]["id"] if F else None
    F.append(rec("FN1", "N1", mat("n1"), "node", vf=0, vu=10, names=("Rn1",)))
    F.append(rec("FN2", "N2", mat("n2"), "node", vf=0, vu=10, names=("Rn2",)))
    td1 = {"match": "xw1", "differ": "xw1d", "none": None}[o["td_bundle"]]
    if td1:
        F.append(row("TD1", "td", "N1", ("FN1",), seat="n1", xw=td1))
        F.append(row("TD2", "td", "N2", ("FN2",), seat="n2", xw="xw2"))
    F.append(row("CF1", "confer", allv[0] if allv else "A", ("FN1", "G0") + tuple("F" + k for k in allv),
                 voices=tuple(allv)))
    F.append(row("CF2", "confer", allv[0] if allv else "A", ("FN2", "G0") + tuple("F" + k for k in allv),
                 voices=tuple(allv)))
    F.append(row("ACK", "ack", allv[0] if allv else "A", (first,) if first else (), carried=frozenset(carried)))
    F.append(row("RS", "snap", allv[0] if allv else "A", ("REVz", "ACK")))
    named = tuple(r["id"] for r in F) + ("G0", "RB2") + (() if o["rb"] == "outside" else ("RB1",)) + (
        ("RB1b",) if o["rb"] == "concurrent" else ())
    CR = row("CR", "bundle2", allv[0] if allv else "A", named, version=1, voices=tuple(allv), at=next(T))
    fork = []
    if o["fork"]:
        fv = tuple(hv) if o["count"] == "all" else tuple(hv[:2])
        fork.append(row("ACKb", "ack", fv[0], (first,), carried=frozenset(carried | {"L", "X0"})))
        fork.append(row("CRb", "bundle2", fv[0], tuple(n for n in named if n != "ACK") + ("ACKb",), version=1,
                        voices=fv, at=CR["at"]))

    # after the ceremony row
    after = []
    if o["back"]:
        after.append(row("B", "post", "u1", ("C1",), form="e1", at=1))   # back-dated: claims an instant before all
    after.append(rec("FU1", "U1", mat("u1"), "user", names=("Ru1",)))
    if o["steward_reg"]:
        after.append(rec("FU2", "U2", mat("u2"), "user", names=("Ru2",)))
        after.append(row("EF", "edge", "U2", ("FU2", "CR")))
    if o["agent_rec"]:
        after.append(rec("FAG", "AG", mat("ag"), "agent", vf=0, vu=10, names=("Rag",)))
    if o["owner_rev"]:
        after.append(row("RVo", "revoke", "U2", ("FAG",), key="AG"))   # the owner revokes its agent's key
    if o["ob2"] and o["steward_reg"] and o["agent_rec"]:
        after.append(row("OB2", "ob", "U2", ("FU2", "FAG"), owner="U2", target="AG", voices=("U2", "AG")))
    c2v = ("U1",) + (("U2",) if o["steward_reg"] else ()) + (("AG",) if o["agent_rec"] else ())
    after.append(row("C2", "roster", "U1", ("C1", "FU1") + (("FU2",) if o["steward_reg"] else ()) +
                     (("FAG",) if o["agent_rec"] else ()), voices=c2v, members=("u1", "u2", "u3", "ag")))
    after.append(row("W3", "post", "u3", ("C2",), form="e1", at=2))   # the silent holder writes the earlier form, back-dated
    if o["revoked_reg"]:
        after.append(rec("FZ", "Z", mat("kz"), "user", names=("Rkz",)))
    if o["seat_td"]:
        after.append(row("TDs", "td", "N1", ("FN1",), seat="n1", xw="xw1s"))
    if o["halts"] == "fwd" and allv:
        after.append(row("Hf", "halt", hv[0], ("F" + hv[0],), halves=frozenset({"ed", "pq"})))
        after.append(row("RSm", "resume", hv[0], ("Hf",), voices=tuple(hv[:2])))
    if o["third_rev"]:
        after.append(row("RVx", "revoke", "U1", ("FB",), key="B"))      # a third party's revocation of a holder's key
    for k in o["revoke_holders"]:
        after.append(row("RV" + k, "revoke", k, ("F" + k,), key=k))
    if o["acts"]:
        for i, vs in enumerate(o["acts"]):
            after.append(row("Q%d" % i, "confer", vs[0], tuple("F" + k for k in vs), voices=tuple(vs)))
    rows = rows + late + F + [CR] + fork + after

    # ---- what the world was made to give (the oracle; the model is never consulted) ----
    x = {}
    persons = {}
    for h in HOLD:
        ks = hk[h]
        for k in ks:
            persons[k] = h if len(ks) == 1 else ("contested", h)
    nhold = sum(1 for h in HOLD if len(hk[h]) == 1)
    need = 3 if o["count"] == "all" else 2
    x["cr_valid"] = nhold >= need
    direct = {"G0", "RB2"} | ({"RB1"} if o["rb"] != "outside" else set()) | ({"RB1b"} if o["rb"] == "concurrent" else set())
    direct |= {"R" + h for h in HOLD if hk[h]} | {"Rn1", "Rn2", "REVz"}
    x["past_e1"] = (carried | direct) if x["cr_valid"] else set(e1) | {r["id"] for r in late} | ({"B"} if o["back"] else set()) | {"W3"}
    x["not_past"] = {"X0", "L", "B", "W3", "Hs"} & {r["id"] for r in rows}
    live = set()
    for h in HOLD:
        live |= set(hk[h])
    live |= {"N1", "N2", "U1"} | ({"U2"} if o["steward_reg"] else set()) | ({"AG"} if o["agent_rec"] else set())
    x["live"] = live if x["cr_valid"] else live | {"a1", "b1", "c1", "n1", "n2", "u1", "u2", "u3", "ag"}
    x["persons"] = persons
    # a seat's key: the counted re-binds in the past and the bundle's row, one value or none
    xs = {"n1": set(), "n2": {"xw2"}}
    if o["rb"] in ("pair", "concurrent"):
        xs["n1"].add("xw1")
    if o["rb"] == "concurrent":
        xs["n1"].add("xw1b")
    if td1:
        xs["n1"].add(td1)
    x["xw"] = {s: (next(iter(v)) if len(v) == 1 else None) for s, v in xs.items()}
    cont = True
    st = None
    if o["ob_carried"] and o["agent_rec"]:
        st = "u2"
    if o["ob2"] and o["steward_reg"] and o["agent_rec"]:
        st = "u2"
    x["steward"] = st
    edge = o["edge_carried"] or o["steward_reg"]
    x["may_act"] = bool(o["agent_rec"]) and st is not None and edge
    x["members"] = frozenset({"u1", "u2", "u3", "ag"})
    x["count"] = o["count"]
    fwd = {r["id"] for r in rows if r["form"] == "e2"}
    byid = {r["id"]: r for r in rows}
    def old_ok(i, seen=()):
        r = byid[i]
        return r["form"] == "e1" and all(n in byid and old_ok(n) for n in r["names"])
    x["old_e1"] = {r["id"] for r in rows if old_ok(r["id"])}
    x["cont"] = cont
    x["hk"] = hk
    return rows, x, o


def shuffles(rows, n, seed):
    rnd = random.Random(seed)
    out = [list(rows)]
    for _ in range(n - 1):
        r = list(rows)
        rnd.shuffle(r)
        out.append(r)
    return out


CUR = {"count": "all"}


def run(rows, reader, order=None):
    order = order or rows
    C.CEREMONY_COUNT[0] = CUR["count"]
    first = {r["id"]: i for i, r in enumerate(order)}
    return C.answers(order, reader, NOW, first)


# ---- the properties ----------------------------------------------------------------------------------------
def worlds_p1():
    for inner, late, back, fork in itertools.product((True, False), (True, False), (True, False), (None, "b")):
        yield dict(inner=inner, late=late, back=back, fork=fork)


def p1(o, orders):
    """An earlier-form row counts if and only if it is in the ceremony row's past, in every arrival order."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        for name, rd in (("up", UP), ("pin", PIN)):
            a = run(rows, rd, order)
            e1 = {r["id"] for r in rows if r["form"] == "e1"}
            want = x["past_e1"] & e1
            if o["fork"] and name == "up":
                want = want - {"L", "X0"}                    # tips: the rows common to both pasts
            if a["accepted"] != want:
                return False
        a = run(rows, OLD, order)
        if a["cut"] or a["accepted"] != x["old_e1"]:
            return False                                     # a node not upgraded never meets the cut
    return True


def worlds_p2():
    for paths, rr in itertools.product((("same",) * 3, ("rotate", "same", "same"), ("same", "same", "never")),
                                       (True, False)):
        yield dict(paths=paths, revoked_reg=rr, third_rev=True)


def p2(o, orders):
    """A key is live in this form iff it has a key record of this form, and no row of another key makes it live or
    ends it."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        a = run(rows, UP, order)
        if x["cr_valid"] and a["live"] != x["live"]:
            return False
        # only the key's own rows move its life: after the ceremony row, drop every row another key signed
        cr = [r["id"] for r in rows].index("CR")
        before = {r["id"] for r in rows[:cr + 1]}
        for k in a["live"] | {"a1", "u3", "Z"}:
            own = [r for r in order if r["id"] in before or r["signer"] == k or r["kind"] == "rec"]
            b = run(own, UP)
            if (k in a["live"]) != (k in b["live"]):
                return False
    return True


def worlds_p3():
    yield dict()
    yield dict(steward_reg=False)
    yield dict(paths=("same", "same", "never"), count="majority")


def p3(o, orders):
    """A holder that never re-registers has no standing after, and loses nothing it held before, for rows in the
    past: u3 stays a member, its vote in the past stands, and what it signs after counts nowhere."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        a = run(rows, PIN, order)
        if "u3" not in a["members"] or "V3" not in a["accepted"] or "W3" in a["accepted"] or "u3" in a["live"]:
            return False
        if o["paths"][2] == "never" and ("Rc1" not in a["accepted"] or "c1" not in a["roster"]):
            return False
    return True


def devices(path, custody):
    """Each device of holder a1 and the halves it holds. Earlier key a1; the key of this form A (same halves) or Ar."""
    tok, med = {("a1", "ed")}, {("a1", "pq")}
    if custody == "same_element":
        tok.add(("a1", "pq"))
    if path in ("same", "both"):
        tok.add(("A", "ed"))
        (tok if custody == "same_element" else med).add(("A", "pq"))
    if path in ("rotate", "both"):
        tok.add(("Ar", "ed"))
        med.add(("Ar", "pq"))
    return {"token": tok, "media": med}


def worlds_p4():
    for path, cust in itertools.product(("same", "rotate"), ("separate", "same_element")):
        yield dict(paths=(path, "same", "same"), custody=cust)


def p4(o, orders, allow_limit=True):
    """No single device yields a halt: a halt of this form needs both halves of a holder's live composite key, and a
    halt of the earlier form outside the ceremony row's past is refused."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for d, halves in devices(o["paths"][0], o["custody"]).items():
        forged = []
        for k in {k for k, _ in halves}:
            hs = frozenset(h for kk, h in halves if kk == k)
            if k == "a1":
                if hs >= {"ed", "pq"}:
                    forged.append(row("Hx" + d, "halt", "a1", (), form="e1", at=99, halves=hs))
            else:
                forged.append(row("Hy" + d + k, "halt", k, ("F" + k,), halves=hs))
        for order in orders(rows):
            a = run(rows + forged, PIN, order + forged)
            if a["honoured"] & {f["id"] for f in forged}:
                if allow_limit and o["paths"][0] == "same" and o["custody"] == "same_element":
                    continue                                 # the named limit: the carried halves shared a device
                return False
    return True


def worlds_p5():
    for rb, td, st in itertools.product(("pair", "one", "concurrent", "outside"), ("match", "differ", "none"),
                                        (None, "differ")):
        yield dict(rb=rb, td_bundle=td, seat_td=st)


def p5(o, orders):
    """A seat has at most one transit key in force for any link, and it is the one the holders' count re-bound or
    the bundle authorised; two different authorised keys leave none until a row names both."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        a = run(rows, PIN, order)
        if dict(a["seats"]) != x["xw"]:
            return False
    return True


def worlds_p6():
    yield dict(fork="b")
    yield dict(fork="b", paths=("same", "same", "never"), count="majority")


def p6(o, orders):
    """Two ceremony rows are a fork. A reader with no acknowledgement holds both as tips; a reader that acknowledged
    one holds the other void (CC 2.7.8)."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        a = run(rows, UP, order)
        b = run(rows, PIN, order)
        if not x["cr_valid"]:
            ok_a = a["cut"] == () or a["cut"] == ("CRb",)
            if not ok_a:
                return False
            continue
        if a["cut"] != ("CR", "CRb") or a["void"] != ():
            return False
        if b["cut"] != ("CR",) or b["void"] != ("CRb",):
            return False
        if "L" in b["accepted"] or "L" in a["accepted"]:
            return False
    return True


def worlds_p7():
    for paths in (("same",) * 3, ("both", "same", "same"), ("rotate", "rotate", "same"), ("same", "never", "never")):
        hk = {h: fkeys(h, p) for h, p in zip(HOLD, paths)}
        ks = [k for v in hk.values() for k in v]
        acts = [tuple(ks[:1]), tuple(hk["a1"]) if hk["a1"] else (), tuple(ks[:2])]
        yield dict(paths=paths, acts=[a for a in acts if a], halts="fwd", count="majority")
    yield dict(acts=[("A",)], revoke_holders=("B", "C"), halts="fwd")


def p7(o, orders):
    """The accord's count is unbroken across the cutover: the roster after is the roster before, the same persons
    under keys of this form, and no act counts on fewer than a strict majority of persons, at any point."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for order in orders(rows):
        a = run(rows, PIN, order)
        if a["roster"] != frozenset(HOLD):
            return False
        for r in rows:
            if r["kind"] in ("confer", "resume", "bundle2") and r.get("voices") is not None and r["form"] == "e2":
                ps = {x["persons"][k] for k in r["voices"] if k in x["persons"] and not isinstance(x["persons"][k], tuple)
                      and k not in o["revoke_holders"]}
                want = len(ps) >= (3 if r["kind"] == "bundle2" and C.CEREMONY_COUNT[0] == "all" else 2)
                got = r["id"] in a["counted"] or (r["kind"] == "bundle2" and r["id"] in a["cut"])
                if r["kind"] == "bundle2":
                    continue
                if want != got and r["id"] in {q["id"] for q in rows}:
                    return False
    # at every point of the signing order, nothing counts on fewer than a strict majority
    for i in range(1, len(rows) + 1):
        a = run(rows[:i], PIN)
        for rid in a["counted"]:
            r = next(q for q in rows if q["id"] == rid)
            if r["form"] == "e2":
                ps = {x["persons"][k] for k in r["voices"] if k in x["persons"] and not isinstance(x["persons"][k], tuple)}
            else:
                ps = set(r["voices"]) & set(HOLD)
            if len(ps) < 2:
                return False
    return True


def worlds_p8():
    for oc, ob2, sr in itertools.product((True, False), (True, False), (True, False)):
        yield dict(ob_carried=oc, ob2=ob2, steward_reg=sr)


def p8(o, orders):
    """An agent has a steward at every point across the cutover: at every point of the signing order, and in every
    arrival order, an agent that may act has a steward, and one that had a steward keeps it."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    had = False
    for i in range(1, len(rows) + 1):
        a = run(rows[:i], PIN)
        st, act = dict(a["steward"]).get("ag"), dict(a["may_act"]).get("ag")
        if act and st is None:
            return False
        if had and st is None and o["ob_carried"]:
            return False
        had = had or st is not None
    for order in orders(rows):
        a = run(rows, PIN, order)
        if dict(a["steward"]).get("ag") != x["steward"] or dict(a["may_act"]).get("ag") != x["may_act"]:
            return False
    return True


def worlds_p9():
    yield dict()
    yield dict(fork="b")
    yield dict(paths=("both", "rotate", "same"), rb="concurrent", seat_td="differ")


def p9(o, orders):
    """The result does not depend on the order in which a node receives the ceremony's rows."""
    rows, x, o = world(**o)
    CUR["count"] = o["count"]
    for _, rd in READERS:
        seen = None
        for order in orders(rows):
            a = run(rows, rd, order)
            if seen is not None and a != seen:
                return False
            seen = a
    return True


PROPS = [
    ("P1", "an earlier-form row counts iff it is in the ceremony row's past, in every arrival order", p1, worlds_p1,
     ("inner_names", "by_instant", "by_arrival")),
    ("P2", "a key is live in this form iff it has a key record of this form, and no row of another key makes it live or ends it",
     p2, worlds_p2, ("ceremony_carries_keys", "named_makes_live", "ignore_earlier_revocation", "third_party_ends")),
    ("P3", "a holder that never re-registers has no standing after and loses nothing it held in the past", p3, worlds_p3,
     ("silence_retires", "by_instant", "drop_earlier_after_cut")),
    ("P4", "no single device yields a halt", p4, worlds_p4, ("one_half_verifies", "earlier_halt_after")),
    ("P5", "a seat has at most one transit key in force, the one the holders' count authorised", p5, worlds_p5,
     ("seat_alone_td", "one_holder_rebind", "rebind_outside_past", "pick_one")),
    ("P6", "two ceremony rows are a fork: tips to a reader with no acknowledgement, the other void to one that pinned",
     p6, worlds_p6, ("fork_union", "pinned_ignored")),
    ("P7", "the accord's count is unbroken across the cutover: same persons, same count, never fewer", p7, worlds_p7,
     ("count_keys", "roster_shrinks")),
    ("P8", "an agent has a steward at every point across the cutover", p8, worlds_p8,
     ("no_continuity", "act_without_steward")),
    ("P9", "the result does not depend on the order in which a node receives the ceremony's rows", p9, worlds_p9,
     ("by_arrival", "fork_first")),
]


def holds(fn, worlds, orders):
    return all(fn(o, orders) for o in worlds())


# ---- findings: each computed from a run -------------------------------------------------------------------
def findings(orders):
    out = []
    C.MUT.clear()
    # F1: an earlier row named only by a carried earlier row is outside the past
    rows, x, o = world()
    a = run(rows, PIN)
    out.append(("F1 an earlier row that a carried earlier row names, and no carried root holds, is outside the past",
                "outside" if "X0" not in a["accepted"] else "inside"))
    # F2: an earlier-form halt sealed before the ceremony and published after is refused
    rows, x, o = world(halts="sealed")
    a = run(rows, PIN)
    b = run([r for r in rows if r["id"] not in ("CR",)], UP)
    out.append(("F2 a halt sealed in the earlier form and published after the ceremony row",
                "refused" if "Hs" not in a["honoured"] and "Hs" in b["honoured"] else "honoured"))
    # F3: an earlier row concurrent with the ceremony row counts until the node holds the ceremony row, then not
    rows, x, o = world()
    pre = run([r for r in rows if r["id"] != "CR"], UP)
    post = run(rows, UP)
    out.append(("F3 an earlier row concurrent with the ceremony row, at an upgraded node",
                "counts before the ceremony row is held and not after" if "L" in pre["accepted"] and "L" not in post["accepted"]
                else "final"))
    # F4: a re-bind outside the past and no bundle row: the seat has no transit key of this form
    rows, x, o = world(rb="outside", td_bundle="none")
    a = run(rows, PIN)
    out.append(("F4 a seat whose earlier-form re-bind the ceremony neither names nor carries, with no row in the bundle",
                "no transit key" if dict(a["seats"])["n1"] is None else "keyed"))
    # F5: the bundle's transit row and the re-bind disagree
    rows, x, o = world(td_bundle="differ")
    a = run(rows, PIN)
    out.append(("F5 the bundle's transit row names another key than the re-bind",
                "no transit key" if dict(a["seats"])["n1"] is None else "keyed"))
    # F6: a holder who both carries and rotates has no voice until a row names both
    rows, x, o = world(paths=("both", "same", "same"))
    a = run(rows, PIN)
    pa = dict(a["person"])
    out.append(("F6 a holder with two keys of this form for one earlier key",
                "no voice" if pa.get("A", "").startswith("(") and pa.get("Ar", "").startswith("(") else "a voice"))
    # F7: unanimity versus majority for the ceremony row, with one holder absent
    keep = CUR["count"]
    res = []
    for cnt in ("all", "majority"):
        CUR["count"] = cnt
        rows, x, o = world(paths=("same", "same", "never"))
        a = run(rows, PIN)
        res.append("%s: %s" % (cnt, "signed" if a["cut"] else "not signed"))
    CUR["count"] = keep
    out.append(("F7 the ceremony row with one holder who never re-registers", "; ".join(res)))
    # F8: the steward that never re-registers stays the agent's steward by the carried binding
    rows, x, o = world(steward_reg=False, ob2=False)
    a = run(rows, PIN)
    out.append(("F8 an agent whose steward never re-registers",
                "keeps its steward of record; may act: %s" % dict(a["may_act"])["ag"]))
    # F9: a carried trust edge keeps an agent able to act, and with no carried edge and no forward edge it may not
    rows, x, o = world(edge_carried=False, steward_reg=False, ob2=False)
    a = run(rows, PIN)
    out.append(("F9 an agent whose steward's trust edge is neither carried nor signed again",
                "may not act" if not dict(a["may_act"])["ag"] else "may act"))
    # F10: a key that revoked itself in the earlier form, carried over by a record of this form
    rows, x, o = world()
    a = run(rows, PIN)
    out.append(("F10 a key revoked in the earlier form and recorded again in this form",
                "not live" if "Z" not in a["live"] else "live"))
    # F11: carrying the same halves from a device that held both halves
    out.append(("F11 a holder carries over the same halves when the earlier key held both on one device",
                "one device yields a halt" if not p4(dict(paths=("same", "same", "same"), custody="same_element"),
                                                     orders, allow_limit=False) else "no device yields"))
    # F13: the owner's revocation of a key it owns, read by the liveness sentence of CC 2.4.1.1
    CUR["count"] = "all"
    rows, x, o = world(owner_rev=True)
    a = run(rows, PIN)
    out.append(("F13 an owner's revocation of the agent key it owns, read by the liveness sentence",
                "the key stays live" if "AG" in a["live"] else "the key ends"))
    # F14: an owner-binding the ceremony does not carry
    rows, x, o = world(ob_carried=False)
    gap = [r["id"] for i, r in enumerate(rows) if r["id"] in ("CR", "B", "FU1", "FU2", "EF", "FAG")
           and dict(run(rows[:i + 1], PIN)["steward"]).get("ag") is None]
    out.append(("F14 an agent whose earlier owner-binding the ceremony does not carry",
                "no steward from the ceremony row until its binding of this form" if gap and gap[0] == "CR" else "no gap"))
    # F15: a halt fired after the acknowledgement and before the ceremony row
    rows, x, o = world(halts="late")
    pre = run([r for r in rows if r["id"] != "CR"], PIN)
    post = run(rows, PIN)
    out.append(("F15 a halt of the earlier form fired after the acknowledgement, at a node that latched it",
                "its row stops counting at the ceremony row" if "HL" in pre["honoured"] and "HL" not in post["honoured"]
                else "it still counts"))
    # F12: the reader that has not upgraded
    rows, x, o = world()
    a, b = run(rows, OLD), run(rows, PIN)
    out.append(("F12 a node not upgraded and an upgraded node holding the same rows",
                "differ" if a["accepted"] != b["accepted"] else "agree"))
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
