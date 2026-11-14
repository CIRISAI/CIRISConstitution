#!/usr/bin/env python3
"""
check_key_end.py: a key's own end, run on the kernel's own modules (key_end.py imports formal/causal_kernel).

Five sections, each compared with key_end_expected.tsv:
    properties   generated worlds of one key A at a small bound (a record, renewals, rotations, an attestation, a
                 trust edge naming it, a revocation, a record not yet begun), every property read at six instants,
                 the same answers in ORDERS arrival orders per world, and a planted break per property that must
                 be caught (the property fails in at least one world under it)
    in time      check_time.py's method for a renewal of a key whose record has ended: worlds of a renewal signed in
                 time or back-dated, first held early or late, witnessed or not, under a reader that acknowledged the
                 end or not; for each candidate rule, a FUNCTION PAIR (same rows and now, different verdicts) and the
                 renewals it gets wrong (a back-dated one counted, one signed in time refused)
    wording      the class condition read from the record versus from an owner-binding
    attacks      scenarios in attacks.py's pattern, every arrival order of up to seven rows; each fact must hold
    numbers      the steady state of a seat's store, from formulas over stated rates (not measured)

Bound: 2 worker processes, 2 GiB address space each; ORDERS arrival orders per world.
    python3 -I check_key_end.py           compare with key_end_expected.tsv; exit 1 on any difference or uncaught plant
    python3 -I check_key_end.py --write   write key_end_expected.tsv
"""
import itertools
import multiprocessing as mp
import os
import random
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)


def limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


limit()
import key_end as KE  # noqa: E402

rec, att, edge, revoke = KE.rec, KE.att, KE.edge, KE.revoke
KEYS = ("A", "B", "C", "D", "X")
PARTIES = ("X",)
SUBJECTS = ("X",)
NOWS = (3, 9, 11, 13, 16, 21)
ORDERS = 8
pX = rec("pX", "X", 0, None, typ="user")


# ---- generated worlds --------------------------------------------------------------------------------------
REN = (None, (4, 14), (8, 18), (11, 20), (11, 20, "w"), (4, 9), (10, 21))
ROT = (None, "B@4", "B@11", "B-unsigned", "B@4+C@6")
EXTRA = (None, "revoke9", "futureD")


def world(vuA, ren, ren2, rot, at_a, edg, extra):
    rows = [pX, rec("pA", "A", 0, vuA)]
    if ren:
        rows.append(rec("rA", "A", ren[0], ren[1], names=("pA",)))
        if len(ren) == 3:
            rows.append(att("w", "X", 1, "pX", names=("pA",)))       # another voice names the key's record
    if ren2:
        rows.append(rec("r2", "A", 3, 12, names=("pA",)))
    if rot:
        if rot.startswith("B@4"):
            rows.append(rec("qB", "B", 4, 12, names=("pA",), succ_of="A", at_old=4))
        if rot == "B@11":
            rows.append(rec("qB", "B", 11, 19, names=("pA",), succ_of="A", at_old=11))
        if rot == "B-unsigned":
            rows.append(rec("qB", "B", 4, 12, names=("pA",), succ_of="A", at_old=4, sigs={"B"}))
        if rot.endswith("C@6"):
            rows.append(rec("qC", "C", 6, 14, names=("pA",), succ_of="A", at_old=6))
    cover = "pA" if at_a <= vuA or not ren else "rA"
    rows.append(att("a1", "A", at_a, cover, about="X"))
    if edg:
        rows.append(edge("e", "X", "A", 1, "pX", names=("a1",) if edg == "names" else ()))
    if extra == "revoke9":
        rows.append(revoke("v", "A", 9))
    if extra == "futureD":
        rows += [rec("pD", "D", 12, 20), att("d1", "D", 13, "pD", about="X")]
    return rows


def worlds():
    for args in itertools.product((5, 10, 12), REN, (False, True), ROT, (2, 7, 15), (None, "names", "plain"), EXTRA):
        yield args, world(*args)


def orders(rows, n=ORDERS):
    rnd = random.Random(len(rows) * 7919 + sum(map(ord, "".join(r["id"] for r in rows))))
    out = [list(rows), list(reversed(rows))]
    while len(out) < n:
        o = list(rows); rnd.shuffle(o); out.append(o)
    return out


def ans(S, now):
    return KE.answers(S, now, KEYS, PARTIES, SUBJECTS)


# each property: name, what it reads, the planted break (MUT name), the check pred(rows) -> None or witness
def p_order(rows):
    S = KE.state(rows)
    want = {n: ans(S, n) for n in NOWS}
    for o in orders(rows):
        T = KE.arrived(o)
        for n in NOWS:
            if ans(T, n) != want[n]:
                return "order %s at now %d" % ([r["id"] for r in o], n)
    return None


def p_ceiling(rows):
    S = KE.state(rows)
    for k in KEYS:
        rs = KE.recs(S, k)
        if any(r["vu"] is None for r in rs):
            continue                                  # a person's record states no end
        for n in NOWS:
            if KE.live(S, k, n) and not any(n < r["vf"] + KE.CEIL for r in rs):
                return "%s live at %d, past every valid_from + ceiling" % (k, n)
    return None


def p_compact(rows):
    S = KE.state(rows)
    for n in NOWS:
        C = KE.state(KE.compact(rows, S, n))
        for n2 in NOWS:
            if n2 >= n and ans(C, n2) != ans(S, n2):
                return "compacted at %d, differs at %d" % (n, n2)
    return None


def p_history(rows):
    seen = None
    for n in NOWS:
        KE.CLOCK[0] = n
        S = KE.state(rows)
        got = frozenset(r["id"] for r in S.Cs)
        if seen is not None and got != seen:
            return "concluded set differs at now %d" % n
        seen = got
    return None


def p_rotation_fork(rows):
    ids = {r["id"] for r in rows}
    if {"qB", "qC"} <= ids:
        S = KE.state(rows)
        if S.C.get("qB") and S.C.get("qC") and KE.successor(S, "A") is not None:
            return "two concurrent rotations, successor %s" % KE.successor(S, "A")
    return None


def p_rotation_sigs(rows):
    S = KE.state(rows)
    for r in KE.K.sel(S.Cs, kind="rec"):
        if r["succ_of"] and r["succ_of"] not in r["sigs"]:
            return "a rotation without the old key's signature concluded: %s" % r["id"]
    return None


def p_ended_stays(rows):
    S = KE.state(rows)
    for k in KEYS:
        for n1 in NOWS:
            if KE.ended(S, k, n1) and any(KE.live(S, k, n2) for n2 in NOWS if n2 >= n1):
                return "%s ended at %d and live at or after it" % (k, n1)
    return None


def p_own_rows(rows):
    S = KE.state(rows)
    for k in ("A",):
        mine = [r for r in rows if r["signer"] == k or k in r.get("sigs", ()) or r["id"] in ("pX",)]
        T = KE.state(mine)
        for n in NOWS:
            if KE.live(S, k, n) != KE.live(T, k, n):
                return "%s's life at %d moved by another voice's row" % (k, n)
    return None


PROPS = [
    ("P1 every answer is the same in every arrival order", "kept, concluded, derived at six instants", "arrival_clock", p_order),
    ("P2 a key whose holder signs nothing more ends at most the ceiling after the last record it signed", "the door, read from the record alone", "no_ceiling", p_ceiling),
    ("P3a compacting the lapsed rows changes no answer at that instant or later (a record not yet begun is kept)", "retained = rows of keys not ended and their past", "seed_live_only", p_compact),
    ("P3b compacting keeps a dead key's row that a live row names", "the closure over what rows name", "drop_dead_signers", p_compact),
    ("P3c a lapsed row counts in no derived answer, so dropping it moves none", "score over rows that have not lapsed", "score_reads_lapsed", p_compact),
    ("P4 a row's conclusion never reads now: signed while live, concluded for good", "the concluded layer", "conclude_reads_now", p_history),
    ("P5a two concurrent rotations of one key name no successor (both or neither)", "the frontier of rotations", "rank_successor", p_rotation_fork),
    ("P5b a rotation without the old key's signature is not kept", "the door", "rotation_one_sig", p_rotation_sigs),
    ("P6 with the same rows, a key ended at an instant is live at no later instant; the end is the greatest stated end", "ended over every record", "end_from_newest", p_ended_stays),
    ("P7 a key's life is moved only by rows the key signed (no other voice revives it)", "live over the key's own rows", "witness_revives", p_own_rows),
]


def run_prop(i):
    limit()
    name, reads, plant, pred = PROPS[i]
    n = 0
    base = None
    for args, rows in worlds():
        n += 1
        w = pred(rows)
        if w is not None and base is None:
            base = "%s: %s" % (args, w)
    KE.MUT.add(plant)
    caught = None
    for args, rows in worlds():
        w = pred(rows)
        if w is not None:
            caught = "%s: %s" % (args, w); break
    KE.MUT.discard(plant)
    return i, n, base, caught


# ---- in time: which renewal of an ended record counts ---------------------------------------------------------
def time_worlds():
    """P: the record, vf 0, vu 10. R: a renewal stating vf 8, vu 18, the same bytes whether signed in time (s=6) or
    back-dated after the end (s=14). h: when this reader first held R. A witness row by another voice names R; the
    reader trusts the peer and not the throwaway key. The reader acknowledges the end at 11 if it does not hold R."""
    for s, h, now, wit, nxt in itertools.product((6, 14), (7, 12, 16), (11, 17), ("none", "peer", "throwaway"), (False, True)):
        if h < s or h > now:
            continue
        ack = now >= 11 and h > 11          # the reader's own acknowledgement of the end, signed at 11, names R iff held
        yield {"s": s, "h": h, "now": now, "wit": wit, "next": nxt, "ack_names_R": now >= 11 and not ack, "acked": now >= 11}


def view_rows(w):
    return (w["now"], w["wit"], w["next"])                       # what the rows every node can hold say, and now


def view_own(w):
    return view_rows(w) + (w["acked"], w["ack_names_R"])        # plus the reader's own rows


def c1_model(w):
    S = KE.state([rec("P", "A", 0, 10), rec("R", "A", 8, 18, names=("P",))])
    return bool(S.C.get("R")) and KE.live(S, "A", w["now"])


CANDIDATES = [
    ("T1 self-contained: the renewal is a further record of the key naming its own earlier one, bounded alone", view_rows, c1_model),
    ("T2 live when first held: the renewal counts only if this node held it before the record's end", view_rows, lambda w: w["h"] < 10),
    ("T3 witnessed: the renewal counts only if a row by another voice names it", view_rows, lambda w: w["wit"] != "none"),
    ("T3' witnessed by a voice the reader trusts", view_rows, lambda w: w["wit"] == "peer"),
    ("T4 named by the key's own next row", view_rows, lambda w: w["next"]),
    ("T5 the reader's own end: a renewal its acknowledgement of the end does not name is void for that reader", view_own,
     lambda w: not w["acked"] or w["ack_names_R"]),
]


def time_section():
    out = []
    for label, view, f in CANDIDATES:
        seen, pair = {}, None
        forged = honest = None
        for w in time_worlds():
            v, r = view(w), f(w)
            if pair is None and v in seen and seen[v][1] != r:
                a = seen[v][0]
                pair = "signed %d held %d -> %s | signed %d held %d -> %s (now %d, witness %s)" % (a["s"], a["h"], seen[v][1], w["s"], w["h"], r, w["now"], w["wit"])
            seen.setdefault(v, (w, r))
            if forged is None and r and w["s"] > 10:
                forged = "back-dated, signed %d, held %d, now %d, witness %s, next %s" % (w["s"], w["h"], w["now"], w["wit"], w["next"])
            if honest is None and not r and w["s"] <= 10:
                honest = "signed in time %d, held %d, now %d, witness %s, next %s" % (w["s"], w["h"], w["now"], w["wit"], w["next"])
        fn = "a function of the rows and now" if pair is None else "NOT a function of the rows and now"
        if view is view_own and pair is None:
            fn = "a function of the rows, the reader's own rows and now; two readers differ"
        out.append((label, fn, pair or "-", forged or "never", honest or "never"))
    return out


# ---- the class condition: read from the record, or from an owner-binding --------------------------------------
def wording_section():
    endless = rec("n", "N", 0, None, typ="node")
    ended_ = rec("n", "N", 0, 10, typ="node")
    res = []
    for label, mut in (("rule: an end is required by the record's own identity type", None),
                       ("as worded: required unless an owner-binding at federation scope is held", "wording")):
        if mut: KE.MUT.add(mut)
        v = []
        for seat, held in (("seat holding the binding", True), ("seat not holding it", False)):
            r = dict(endless, _fed_binding_held=held)
            v.append(bool(KE.WF(r)))
        e = bool(KE.WF(dict(ended_, _fed_binding_held=False)))
        if mut: KE.MUT.discard(mut)
        res.append((label, "endless node record kept: %s / %s; record with an end kept: %s" % (v[0], v[1], e),
                    "the door reads the row alone" if v[0] == v[1] else "two seats with the same record differ: the door reads another row"))
    return res


# ---- the classes: which records the door keeps, with and without an end ----------------------------------------
CLASSES = [("node key", dict(typ="node"), "required"), ("agent key", dict(typ="agent"), "required"),
           ("room key of a private room (an agent's)", dict(typ="agent", room=True), "optional"),
           ("person's key (user)", dict(typ="user"), "forbidden"), ("accord holder's key", dict(typ="accord_holder"), "forbidden"),
           ("pseudonym (CC 5.4.6)", dict(typ="pseudonym"), "optional")]


def class_verdicts():
    out = []
    for label, kw, _ in CLASSES:
        w = bool(KE.WF(rec("c", "K", 0, 10, **kw)))
        wo = bool(KE.WF(rec("c", "K", 0, None, **kw)))
        out.append((label, {(True, False): "required", (False, True): "forbidden", (True, True): "optional"}.get((w, wo), "never kept")))
    return out


def classes_section():
    got = class_verdicts()
    holds = all(v == want for (_, v), (_, _, want) in zip(got, CLASSES))
    KE.MUT.add("end_on_person")
    caught = any(v != want for (_, v), (_, _, want) in zip(class_verdicts(), CLASSES))
    KE.MUT.discard("end_on_person")
    return got, holds, caught


# ---- attacks ---------------------------------------------------------------------------------------------------
def every_order(rows, f, cap=5040):
    """f(S) over every arrival order (all of them up to seven rows); returns the set answer and whether all agree."""
    S = KE.state(rows)
    want = f(S)
    agree = True
    for i, o in enumerate(itertools.permutations(rows)):
        if i >= cap: break
        if f(KE.arrived(list(o))) != want:
            agree = False; break
    return want, agree


ATTACKS = []


def attack(name):
    def deco(f):
        ATTACKS.append((name, f)); return f
    return deco


@attack("K1 a thief with a still-live stolen key rotates it to a key of its own")
def k1():
    rows = [rec("pA", "A", 0, 10), rec("qT", "T", 5, 13, names=("pA",), succ_of="A", at_old=5)]
    f = lambda S: (KE.successor(S, "A"), KE.ended(S, "A", 11), KE.ended(S, "T", 13))
    (succ, a_end, t_end), agree = every_order(rows, f)
    return ("CONCEDED", "whoever holds the key's private half while it is live (as today)",
            "the same rotation is open to a thief today; the end adds only that the thief must keep renewing, observably, and an owner revokes an owned key (CC 2.4.1.1); an unowned key's honest holder makes it contested (K2)",
            [("the thief's key is the successor", succ == "T"), ("the old key still ends at its own end", a_end),
             ("the thief's key ends at its own end unless renewed", t_end), ("every arrival order agrees", agree)])


@attack("K2 two concurrent rotations of one key")
def k2():
    base = [rec("pA", "A", 0, 10), rec("qB", "B", 5, 13, names=("pA",), succ_of="A", at_old=5),
            rec("qT", "T", 6, 14, names=("pA",), succ_of="A", at_old=6)]
    dB = rec("dB", "B", 7, 15, names=("pA", "qB", "qT"), succ_of="A", at_old=7)
    dT = rec("dT", "T", 7, 15, names=("pA", "qB", "qT"), succ_of="A", at_old=7)
    f = lambda S: (KE.successor(S, "A"), KE.live(S, "B", 8), KE.live(S, "T", 8), KE.ended(S, "A", 10))
    (s0, b, t, ae), ag0 = every_order(base, f)
    (s1, _, _, _), ag1 = every_order(base + [dB], f)
    (s2, _, _, _), ag2 = every_order(base + [dB, dT], f)
    return ("CONCEDED", "the two holders of one key",
            "both or neither (KERNEL 6.2): neither new key inherits; each lives as a fresh key; the old key ends at its own end; a row naming both decides, and either holder can sign one, so equal standing stays contested (KERNEL 6.5); no third key settles an unowned key, an owner settles an owned one by revocation",
            [("two concurrent rotations name no successor", s0 is None), ("each new key lives as a fresh key", b and t),
             ("the old key ends at its own end", ae), ("a rotation naming both decides", s1 == "B"),
             ("the other holder's rotation naming both empties it again", s2 is None), ("every arrival order agrees", ag0 and ag1 and ag2)])


@attack("K3 a holder back-dates a renewal of an ended key")
def k3():
    rows = [rec("pA", "A", 0, 10), rec("rA", "A", 9, 19, names=("pA",))]     # signed at 15, dated 9
    f = lambda S: (KE.live(S, "A", 16), KE.live(S, "A", 19))
    (l16, l19), agree = every_order(rows, f)
    (r16, _), ragree = every_order(rows + [revoke("v", "A", 10)], f)
    late = [rec("pA", "A", 0, 10), rec("rA", "A", 15, 19, names=("pA",))]   # signed and dated honestly after the end
    (h16, _), hagree = every_order(late, f)
    return ("CONCEDED", "whoever holds the key's private half, at any time after the end",
            "a back-dated renewal is the same bytes as one signed in time (in-time section, T1), and a renewal signed honestly after the end revives the key too, so back-dating gains nothing; it revives the key alike at every node that holds it, at most CEIL past its own instant per renewal, chained without bound; only the key's own revocation (never withdrawn) makes an end final, at one row kept for good",
            [("the back-dated renewal revives the key", l16), ("it ends at its own stated end", not l19),
             ("a renewal signed honestly after the end revives it as well: back-dating gains nothing", h16),
             ("the key's own revocation at its end makes the end final", not r16), ("every arrival order agrees", agree and ragree and hagree)])


@attack("K4 a peer withholds a renewal so a node sees the key end")
def k4():
    full = [rec("pA", "A", 0, 10), rec("rA", "A", 8, 18, names=("pA",)), att("a2", "A", 12, "rA", about="X"), pX]
    seen = [full[0], full[2], pX]                 # the renewal withheld; a2 waits on it
    S, W = KE.state(full), KE.state(seen)
    C = KE.state(KE.compact(seen, W, 13))         # the victim compacts while it is withheld
    R = KE.state(KE.compact(seen, W, 13) + [full[0], full[1], full[2]])   # the holder re-serves its record, the renewal and a2
    f = lambda S: (KE.live(S, "A", 13), bool(S.C.get("a2")))
    _, agree = every_order(full, f)
    return ("CONCEDED", "a relay, by omission (attack 26's shape)",
            "while withheld the victim reads the key ended, may drop its unreferenced rows, and holds its later rows waiting; nothing is refused and no digest is kept, so a later delivery of the renewal and the rows repairs it exactly; a seat that kept a refusal digest would differ for good",
            [("while withheld the key reads ended at the victim", KE.ended(W, "A", 13)),
             ("the row signed under the renewal waits, never refused", "a2" not in W.by),
             ("the victim compacts the dead record", "pA" not in C.by),
             ("a later delivery repairs every answer", KE.answers(R, 13, KEYS, PARTIES, SUBJECTS) == KE.answers(S, 13, KEYS, PARTIES, SUBJECTS)),
             ("every arrival order agrees", agree)])


@attack("K5 an abuser mints throwaway keys at the greatest end")
def k5():
    T = 4 * KE.CEIL
    mints = [rec("m%d" % t, "M%d" % t, t, t + KE.CEIL) for t in range(T)]
    S = KE.state(mints)
    alive = lambda S, now: sum(1 for t in range(T) if t <= now and not KE.ended(S, "M%d" % t, now))
    renewed = mints + [rec("n%d" % t, "M%d" % t, t + KE.CEIL - 1, t + 2 * KE.CEIL - 1, names=("m%d" % t,)) for t in range(T)]
    S2 = KE.state(renewed)
    return ("CONCEDED", "any key, one record a key",
            "an abandoned key is held at most CEIL: at one mint a unit the store holds m x CEIL keys and never more; a key its holder renews is held for as long as it renews, so the end bounds abandonment and not abuse (KERNEL 8a, rows signed to no purpose)",
            [("abandoned at one mint a unit, the keys not ended at any instant past CEIL are exactly CEIL", alive(S, 2 * KE.CEIL) == KE.CEIL and alive(S, 3 * KE.CEIL) == KE.CEIL),
             ("renewed once each, they are held about twice as long", alive(S2, 2 * KE.CEIL) == 2 * KE.CEIL - 1)])


@attack("K6 a harness sets a one-unit end")
def k6():
    rows = [pX, rec("pH", "H", 0, 1), att("h1", "H", 0, "pH", about="X"), att("h2", "H", 0, "pH", about="X"),
            edge("e", "X", "X", 0, "pX", names=("h1",))]
    f = lambda S: (KE.ended(S, "H", 1), frozenset(KE.retained(S, 1)))
    (e, ret), agree = every_order(rows, f)
    return ("HOLDS", "nobody",
            "the end is read from the record against now, so every node holding the rows reads the harness ended at one instant (within the 5-minute skew of CC 2.6.7); its rows lapse alike, except a row a live row names, which is kept with its record",
            [("the harness key ends at its stated end", e), ("its unnamed row lapses", "h2" not in ret),
             ("its row a live row names is kept, with its record", {"h1", "pH"} <= ret), ("every arrival order agrees", agree)])


@attack("K7 a renewal read as activity to track an anonymous holder")
def k7():
    base = [pX, rec("pA", "A", 0, 10), edge("e", "X", "A", 1, "pX")]
    lives = set()
    for vf in range(1, 11):
        S = KE.state(base + [rec("rA", "A", vf, vf + KE.CEIL, names=("pA",))])
        lives.add(KE.live(S, "A", 10))
    F = KE.state(base + [rec("pF", "F", 9, 19)])
    return ("CONCEDED", "anyone who holds the key's record",
            "the renewal row shows that the key's private half is still held, and when it reached a node; its signed instant is the holder's own choice, so the signed instant says nothing the holder did not choose; a fresh unlinked key instead keeps nobody's trust edge, room seat or contact",
            [("a renewal is a row of the key, visible to every holder of its record", True),
             ("every instant the holder states on the renewal gives the same life", lives == {True}),
             ("a fresh key is reached by no edge the old key had", "F" not in KE.reach(F, "X", 10, ("X", "A", "F")))])


@attack("K8 another voice revives an ended key")
def k8():
    rows = [pX, rec("pA", "A", 0, 10), att("w", "X", 1, "pX", names=("pA",)), edge("e", "X", "A", 2, "pX", names=("pA",))]
    f = lambda S: KE.live(S, "A", 13)
    l, agree = every_order(rows, f)
    return ("HOLDS", "nobody but the key itself (K3)",
            "a key's life reads only records the key signed; no row by another voice is read, so a witness, a truster or a seat cannot extend or revive a key",
            [("rows of another voice naming the ended record do not revive it", not l), ("every arrival order agrees", agree)])


@attack("K9 a stranger rotates a key it does not hold")
def k9():
    rows = [rec("pA", "A", 0, 10), rec("qS", "S", 5, 13, names=("pA",), succ_of="A", at_old=5, sigs={"S"})]
    f = lambda S: KE.successor(S, "A")
    s, agree = every_order(rows, f)
    return ("HOLDS", "nobody",
            "a rotation carries the old key's signature beside the new key's proof of possession; without it the row is not kept",
            [("no successor", s is None), ("every arrival order agrees", agree)])


@attack("K10 a row signed after its key's held end")
def k10():
    rows = [rec("pA", "A", 0, 10), att("late", "A", 12, "pA")]
    S = KE.state(rows)
    return ("HOLDS", "nobody",
            "a row whose own instant lies past the record it names concludes nothing: one voice's own instants compared; a back-dated instant is K3's concession, not a new one",
            [("the late row concludes nothing", not S.C.get("late"))])


# ---- numbers ---------------------------------------------------------------------------------------------------
def numbers():
    m, atts = 230, 1650
    r = 2 + atts / m          # a key record, an identity occurrence and its attestations
    out = []
    for label, e in (("no end (today), after one year", None), ("no end (today), after five years", None),
                     ("default end, 365 days", 365), ("an end of 30 days", 30), ("a harness end of 1 day", 1),
                     ("a harness end of 1 minute", 1 / 1440)):
        if e is None:
            yrs = 1 if "one" in label else 5
            out.append((label, "%d rows, growing %d a day for ever" % (round(m * r * 365 * yrs), round(m * r))))
        else:
            out.append((label, "steady state m*e*r = %.0f rows (%.1f keys)" % (m * e * r, m * e)))
    out.append(("per dead key after compaction", "nothing, unless a live row names its rows (then those rows and the record they name); no refusal digest is kept"))
    out.append(("rows a key (shape only)", "r = 2 + 1650/230 = %.1f" % r))
    return out


# ---- main ------------------------------------------------------------------------------------------------------
def main():
    write = "--write" in sys.argv
    t0 = time.time()
    say = lambda s: print(s, flush=True)
    lines, ok = [], True
    nw = sum(1 for _ in worlds())
    say("PROPERTIES: %d worlds of one key, read at instants %s, %d arrival orders a world (2 workers, 2 GiB each)" % (nw, NOWS, ORDERS))
    with mp.Pool(2, initializer=limit) as pool:
        res = sorted(pool.map(run_prop, range(len(PROPS))))
    for i, n, base, caught in res:
        name, reads, plant, _ = PROPS[i]
        verdict = "holds" if base is None else "does not hold"
        pl = "plant %s caught" % plant if caught else "plant %s NOT CAUGHT" % plant
        say("  %s [%s]\n      %s over %d worlds; %s%s" % (name, reads, verdict, n, pl, "" if caught is None else "\n      plant witness: " + caught))
        if base: say("      witness: " + base)
        ok = ok and caught is not None
        lines.append("property\t%s\t%s\t%s" % (name, verdict, "caught" if caught else "not caught"))
    say("IN TIME: a renewal of a record that has ended (P: 0..10; R states 8..18)")
    for label, fn, pair, forged, honest in time_section():
        say("  %s\n      %s\n      function pair: %s\n      a back-dated renewal counted: %s\n      a renewal signed in time refused: %s" % (label, fn, pair, forged, honest))
        lines.append("in_time\t%s\t%s\t%s\t%s" % (label, fn, "counts a back-dated renewal" if forged != "never" else "never counts a back-dated renewal",
                                                 "refuses one signed in time" if honest != "never" else "never refuses one signed in time"))
    say("WORDING: which records must state an end")
    for label, got, verdict in wording_section():
        say("  %s: %s -> %s" % (label, got, verdict))
        lines.append("wording\t%s\t%s" % (label, verdict))
    say("CLASSES: what the door keeps, read from the record alone")
    got, holds, caught = classes_section()
    for label, v in got:
        say("  %s: an end is %s" % (label, v))
        lines.append("class\t%s\t%s" % (label, v))
    say("  %s; plant end_on_person %s" % ("every class as the rule states" if holds else "a class DIFFERS from the rule", "caught" if caught else "NOT CAUGHT"))
    ok = ok and holds and caught
    say("ATTACKS")
    for name, f in ATTACKS:
        cls, who, prot, facts = f()
        bad = [t for t, v in facts if not v]
        say("  %s: %s\n      who: %s\n      %s" % (name, cls, who, prot))
        for t, v in facts:
            say("      %s %s" % ("ok " if v else "NOT", t))
        ok = ok and not bad
        lines.append("attack\t%s\t%s\t%s" % (name, cls, "facts hold" if not bad else "a fact does not hold"))
    say("NUMBERS (formulas over stated rates; the rates are shape, not measured here)")
    for label, v in numbers():
        say("  %s: %s" % (label, v))
        lines.append("numbers\t%s\t%s" % (label, v))
    path = os.path.join(HERE, "key_end_expected.tsv")
    if write:
        open(path, "w", encoding="utf-8").write("section\tname\tverdict\n" + "\n".join(lines) + "\n")
        say("wrote key_end_expected.tsv (%d lines)" % len(lines))
    else:
        want = open(path, encoding="utf-8").read().rstrip("\n").split("\n")[1:] if os.path.exists(path) else []
        diff = sorted(set(want) ^ set(lines))
        for l in diff:
            say("  differs from key_end_expected.tsv: %s %s" % ("expected" if l in want else "now", l))
        ok = ok and not diff
    say("%.1f s" % (time.time() - t0))
    say("RESULT: %s" % ("ok" if ok else "NOT OK"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
