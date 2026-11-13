#!/usr/bin/env python3
"""
check_rosters.py: the properties each roster's own model or text claims, re-checked on the ONE mechanism of roster.py.

For each instance and property: generated worlds (every combination of the adversary's and the honest party's
choices at a small bound), the property read on the set, the same state reached in every arrival order (every
linear extension of the naming order, capped), and one mutation that must be caught (the property fails in at
least one world under it).

Verdicts
    holds                     on the one mechanism with the instance's table parameters
    holds with <param>        only with a parameter the other instances do not use (named)
    bound reproduced          the model's stated residual, reproduced as a witness (expected to "fail")
    does NOT hold             the witness is printed: this roster genuinely differs

Run: python3 -I check_rosters.py      (3 worker processes, 2 GiB each, well under three minutes)
"""
import contextlib
import copy
import itertools
import multiprocessing as mp
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import roster as RS   # noqa: E402

ST, WN, CK, CUT, K, R, FK = RS.ST, RS.WN, RS.CK, RS.CUT, RS.K, RS.R, RS.FK
W = 86400
CAP = 400              # linear extensions per world (the count reached is reported)


def limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


# ---- harness -------------------------------------------------------------------------------------------------
@contextlib.contextmanager
def mutated(mut=(), policy=None, windows=None, spec_attr=None, params=()):
    """Switch on a mutation: MUT names, policy kinds, window clauses, spec attributes. Restored on exit."""
    saved = (set(RS.MUT), dict(ST.POLICY), copy.deepcopy(WN.WINDOWS), {o: dict(vars(s)) for o, s in RS.SPECS.items()}, set(RS.PARAMS))
    try:
        RS.MUT |= set(mut)
        RS.PARAMS |= set(params)
        for k, v in (policy or {}).items(): ST.POLICY[k] = v
        for k, f in (windows or {}).items(): WN.WINDOWS[k] = f(dict(WN.WINDOWS[k]))
        for (o, a), v in (spec_attr or {}).items(): setattr(RS.SPECS[o], a, v)
        yield
    finally:
        RS.MUT.clear(); RS.MUT |= saved[0]
        RS.PARAMS.clear(); RS.PARAMS |= saved[4]
        ST.POLICY.clear(); ST.POLICY.update(saved[1])
        WN.WINDOWS.clear(); WN.WINDOWS.update(saved[2])
        for o, d in saved[3].items(): vars(RS.SPECS[o]).update(d)


def run(spec, worlds, pred, orders=True, windows=lambda rows: ()):
    """worlds: [(name, rows)]; pred(S, rows, name) -> None if it holds, else a witness string."""
    n = n_orders = 0
    fails, order_bad = [], []
    for name, rows in worlds:
        n += 1
        S = RS.state(rows)
        w = pred(S, rows, name)
        if w is not None: fails.append((name, w))
        if orders:
            ws = windows(rows)
            want = RS.snapshot(S, spec, ws)
            for o in RS.linear_extensions(rows, CAP):
                n_orders += 1
                if RS.snapshot(RS.arrived(o), spec, ws) != want:
                    order_bad.append(name); break
    return {"worlds": n, "orders": n_orders, "fails": fails, "order_differs": order_bad}


def result(inst, prop, src, verdict, base, mut_name, mut, extra=""):
    caught = bool(mut and mut["fails"])
    return {"instance": inst, "property": prop, "source": src, "verdict": verdict, "worlds": base["worlds"],
            "orders": base["orders"], "base_fails": base["fails"][:2], "order_differs": base["order_differs"][:2],
            "mutation": mut_name, "caught": caught, "mut_witness": (mut["fails"][:1] if mut else []), "extra": extra}


def verdict_of(base, expect_hold=True, param=None):
    ok = not base["fails"] and not base["order_differs"]
    if not expect_hold:
        return "bound reproduced" if base["fails"] and not base["order_differs"] else "bound NOT reproduced"
    if not ok: return "does NOT hold"
    return "holds with " + param if param else "holds"


wins = lambda rows: tuple(r["id"] for r in rows if r["kind"] == "open")


# =================================================================================================================
# A person's keys and a voice's room keys: formal/self_roster/README.md, on the one mechanism
# =================================================================================================================
def k(spec, i):
    return ("k%d" % i) if spec.obj == "S" else ("rk%d" % i)


def owner_rows(spec, mode, p, tgt, other):
    a = lambda i, s, who: WN.answer(i, who, p, "object")
    if mode == "both_object": return [a("o1", 0, tgt), a("o2", 0, other)]
    if mode == "both_note": return [RS.speak(spec, "n1", tgt, (spec.obj,)), RS.speak(spec, "n2", other, (spec.obj,))]
    if mode == "target_object": return [a("o1", 0, tgt)]
    if mode == "other_object": return [a("o2", 0, other)]
    return []


PRESENT = ("both_object", "both_note")
MODES = PRESENT + ("target_object", "other_object", "absent")


def thief_evict_worlds(spec):
    k1, k2, k3 = k(spec, 1), k(spec, 2), k(spec, 3)
    g = RS.found(spec, (k1, k2, k3))
    out = []
    for tgt in (k1, k2):
        other = k2 if tgt == k1 else k1
        for mode in MODES:
            for named in (False, True):
                for at in (W - 1, W):
                    p = RS.lone_open(spec, "p", k3, "evict", (spec.obj,), tgt)
                    own = owner_rows(spec, mode, "p", tgt, other)
                    L = WN.landing("L", k3, "p", "r", "landed", at, tuple(r["id"] for r in own) if named else ())
                    out.append(("lone evict %s, owner %s, landing %s, at %s" % (tgt, mode, "names owner rows" if named else "leaves them unnamed", at),
                                [g, p, WN.receipt("r", k3, "p", 0)] + own + [L, RS.effect(spec, "E", k3, "L", p)], tgt, mode))
        for mode in MODES:
            own = owner_rows(spec, mode, "x", tgt, other)
            out.append(("counted removal of %s by the thief alone, owner %s" % (tgt, mode),
                        [g] + RS.remove(spec, "x", (spec.obj,), tgt, (k3,)) + [r for r in own if r["kind"] == "speak"], tgt, mode))
    return out


def check_keys(spec, inst):
    res = []
    k1, k2, k3, k4 = (k(spec, i) for i in (1, 2, 3, 4))
    lone_ev, lone_add = spec.lone["evict"], spec.lone["add"]
    src = "formal/self_roster/README.md" + ("" if spec.obj == "S" else "; CC 3.1.3.2 'as a key of a self roster is'")

    # S1 a stolen device cannot evict the others alone (owner present)
    tw = thief_evict_worlds(spec)
    def p1(S, rows, name, worlds=tw):
        tgt, mode = next((t, m) for n, _, t, m in worlds if n == name)
        if mode in PRESENT and tgt not in RS.roster(S, spec): return "%s evicted" % tgt
    W1 = [(n, r) for n, r, _, _ in tw]
    base = run(spec, W1, p1, windows=wins)
    muts = []
    with mutated(policy={spec.remove: ("one", 1, 1)}):
        muts.append(("unilateral door (one key removes)", run(spec, W1, p1, orders=False)))
    with mutated(windows={lone_ev: lambda w: dict(w, silent=None)}):
        muts.append(("no silence condition (model finding 1)", run(spec, W1, p1, orders=False)))
    with mutated(mut={"lone_void"}):
        muts.append(("the landing voids concurrent answers (window rule i)", run(spec, W1, p1, orders=False)))
    for mn, m in muts:
        res.append(result(inst, "Inv_ThiefCannotEvictHonest (owner present)", src, verdict_of(base), base, mn, m))
    # the residuals of S1, read off the same worlds
    resid = [(n, r) for n, r, t, m in tw if m in ("absent", "other_object") and "lone" in n and "names" not in n and str(W) in n[-6:]]
    def lands(S, rows, name):
        t = next(x for n, _, x, _ in tw if n == name)
        return None if t in RS.roster(S, spec) else "%s evicted" % t
    b = run(spec, resid, lands, orders=False)
    with mutated(windows={lone_ev: lambda w: dict(w, default="refused")}):
        pl = run(spec, resid, lands, orders=False)
    res.append(result(inst, "residual: an owner absent for a whole window looks lost", src, verdict_of(b, False), b,
                      "plant: no lone path (the residual must vanish)", {"fails": [] if pl["fails"] else [("plant", "nothing lands")]},
                      "%d of %d worlds land the thief's eviction" % (len(b["fails"]), b["worlds"])))

    # S2 two lost devices are recoverable from the one that remains
    worlds = []
    for keep, l1, l2 in ((k1, k2, k3), (k2, k1, k3), (k3, k1, k2)):
        for first, second in ((l1, l2), (l2, l1)):
            for stale in (False, True):
                g = RS.found(spec, (k1, k2, k3))
                p1_ = RS.lone_open(spec, "p1", keep, "evict", (spec.obj,), first)
                rows = [g, p1_, WN.receipt("r1", keep, "p1", 0), WN.landing("L1", keep, "p1", "r1", "landed", W), RS.effect(spec, "E1", keep, "L1", p1_)]
                h = (spec.obj,) if stale else ("E1",)
                p2_ = RS.lone_open(spec, "p2", keep, "evict", h, second, names=("E1",) if stale else ())
                rows += [p2_, WN.receipt("r2", keep, "p2", 0), WN.landing("L2", keep, "p2", "r2", "landed", W), RS.effect(spec, "E2", keep, "L2", p2_)]
                rows += [RS.add(spec, "a4", ("E1", "E2") if stale else ("E2",), k4, (keep, k4))]
                worlds.append(("keep %s, evict %s then %s%s" % (keep, first, second, ", second on the old head" if stale else ""), rows, keep))
    def p2(S, rows, name):
        keep = next(x for n, _, x in worlds if n == name)
        got = RS.roster(S, spec)
        if got != frozenset({keep, k4}): return "roster %s" % sorted(got)
    W2 = [(n, r) for n, r, _ in worlds]
    base = run(spec, W2, p2, windows=wins)
    with mutated(windows={lone_ev: lambda w: dict(w, default="refused"), lone_add: lambda w: dict(w, default="refused")}):
        m = run(spec, W2, p2, orders=False)
    res.append(result(inst, "Prop_LostRecoverable (two lost of three)", src, verdict_of(base), base, "quorum path only (no lone path)", m))

    # S3 an active thief is evicted: the quorum path, against a thief who keeps signing
    worlds = []
    for via in ("window", "counted"):
        for thief in ("note", "object", "counter_evict"):
            g = RS.found(spec, (k1, k2, k3))
            if via == "window":
                p = RS.lone_open(spec, "p", k1, "evict", (spec.obj,), k3)
                rows = [g, p, WN.answer("a2", k2, "p", "approve"), WN.receipt("r", k1, "p", 0),
                        WN.landing("L", k1, "p", "r", "landed", 0, ("a2",)), RS.effect(spec, "E", k1, "L", p)]
            else:
                rows = [g] + RS.remove(spec, "x", (spec.obj,), k3, (k1, k2))
            if thief == "note": rows.append(RS.speak(spec, "t1", k3, (spec.obj,)))
            elif thief == "object" and via == "window": rows.append(WN.answer("t1", k3, "p", "object"))
            else:
                q = RS.lone_open(spec, "q", k3, "evict", (spec.obj,), k1)
                rows += [q, WN.receipt("rq", k3, "q", 0), WN.landing("Lq", k3, "q", "rq", "landed", W), RS.effect(spec, "Eq", k3, "Lq", q)]
            worlds.append(("owner evicts the thief by %s; thief %s" % (via, thief), rows))
    def p3(S, rows, name):
        got = RS.roster(S, spec)
        if k3 in got or not {k1, k2} <= got: return "roster %s" % sorted(got)
    base = run(spec, worlds, p3, windows=wins)
    with mutated(policy={spec.remove: ("not_a_count", 0, 0)}, windows={lone_ev: lambda w: dict(w, at_once=w["at_once"][1:])}):
        m = run(spec, worlds, p3, orders=False)
    res.append(result(inst, "the quorum path evicts an active thief", src, verdict_of(base), base, "lone path only (no quorum path)", m))

    # S4 a thief does not add its own key against a present owner
    worlds = []
    for named in (False, True):
        for mode in ("both_object", "target_object"):
            g = RS.found(spec, (k1, k2, k3))
            p = RS.lone_open(spec, "p", k3, "add", (spec.obj,), "t2")
            own = [WN.answer("o1", k1, "p", "object")] + ([WN.answer("o2", k2, "p", "object")] if mode == "both_object" else [])
            ac = RS.accept(spec, "ac", "t2", (spec.obj,))
            L = WN.landing("L", k3, "p", "r", "landed", W, tuple(r["id"] for r in own) if named else ())
            worlds.append(("thief adds its own key, owner %s, %s" % (mode, "named" if named else "unnamed"),
                           [g, p, ac, WN.receipt("r", k3, "p", 0)] + own + [L, RS.effect(spec, "E", k3, "L", p, ("ac",))]))
    def p4(S, rows, name):
        if "t2" in RS.roster(S, spec): return "t2 seated"
    both = [w for w in worlds if "both" in w[0]]
    base = run(spec, both, p4, windows=wins)
    with mutated(windows={lone_add: lambda w: dict(w, at_once=w["at_once"][:1])}):
        m = run(spec, both, p4, orders=False)
    # one owner key objecting of two is not a strict majority of the others: the thief's add lands. Is that held?
    res.append(result(inst, "Inv_ThiefNeverMajority: a thief's own key is not added against the owner's two keys", src,
                      verdict_of(base), base, "no cancel by the others", m,
                      "with only ONE owner key objecting: %s" % ("the add lands" if run(spec, [w for w in worlds if "target" in w[0]], p4, orders=False)["fails"] else "refused")))

    # S5 one key: the addition lands at once
    worlds = [("one key adds by a counted version", [RS.found(spec, (k1,)), RS.add(spec, "a", (spec.obj,), k2, (k1, k2))])]
    p = RS.lone_open(spec, "p", k1, "add", (spec.obj,), k2)
    worlds.append(("one key adds by the window at once", [RS.found(spec, (k1,)), p, RS.accept(spec, "ac", k2, (spec.obj,)),
                   WN.receipt("r", k1, "p", 0), WN.landing("L", k1, "p", "r", "landed", 0), RS.effect(spec, "E", k1, "L", p, ("ac",))]))
    def p5(S, rows, name):
        if k2 not in RS.roster(S, spec): return "not added"
    base = run(spec, worlds, p5, windows=wins)
    with mutated(mut={"enact_over_others"}, windows={lone_add: lambda w: dict(w, at_once=(("approve", "strict", "others", "landed"),) + w["at_once"][1:])}):
        m = run(spec, worlds, p5, orders=False)
    res.append(result(inst, "combined1_add: at one key the addition lands at once", src, verdict_of(base), base,
                      "count over the others only (the 'every other member' reading)", m))

    # S6 the stated bounds
    g1 = RS.found(spec, (k1,))
    claim = ST.offer("own", "k9", "k9", spec.scope, spec.obj, "self", (spec.obj,))
    b = run(spec, [("one key, stolen: the owner's fresh key claims a seat", [g1, claim])],
            lambda S, rows, n: "the owner holds no key" if "k9" not in RS.roster(S, spec) else None, orders=False)
    with mutated(mut={"self_admit"}):
        pl = run(spec, [("plant: a key's own counted offer seats it", [g1, ST.offer("own", "k9", "k9", spec.scope, spec.obj, "group", (spec.obj,), head=(spec.obj,), policy=spec.add, counted=spec.counted)])],
                 lambda S, rows, n: "the owner holds no key" if "k9" not in RS.roster(S, spec) else None, orders=False)
    res.append(result(inst, "combined1_stolen: one key stolen loses the self", src, verdict_of(b, False), b,
                      "plant: self-admission (the bound must vanish)", {"fails": [] if pl["fails"] else [("plant", "k9 seats itself: the bound is not reproduced")]}))
    g2 = RS.found(spec, (k1, k2))
    pe = RS.lone_open(spec, "p", k1, "evict", (spec.obj,), k2)
    pt = RS.lone_open(spec, "q", k2, "evict", (spec.obj,), k1)
    rows = [g2, pe, WN.receipt("r", k1, "p", 0), RS.speak(spec, "t", k2, (spec.obj,)), WN.landing("L", k1, "p", "r", "landed", W), RS.effect(spec, "E", k1, "L", pe),
            pt, WN.receipt("rq", k2, "q", 0), RS.speak(spec, "o", k1, (spec.obj,)), WN.landing("Lq", k2, "q", "rq", "landed", W), RS.effect(spec, "Eq", k2, "Lq", pt)]
    stal = lambda S, rows, n: "stalemate: roster %s" % sorted(RS.roster(S, spec)) if RS.roster(S, spec) == {k1, k2} else None
    b = run(spec, [("two keys, one stolen, both active", rows)], stal, windows=wins)
    with mutated(windows={lone_ev: lambda w: dict(w, silent=None)}):
        pl = run(spec, [("same", rows)], stal, orders=False)
    res.append(result(inst, "combined2_stolen: two keys, one stolen, is a stalemate", src, verdict_of(b, False), b,
                      "plant: no silence condition (the bound must vanish)", {"fails": [] if pl["fails"] else [("plant", "roster changes: no stalemate")]}))
    g3 = RS.found(spec, (k1, k2, k3))
    pl = RS.lone_open(spec, "p", k1, "evict", (spec.obj,), k2)
    rows = [g3, pl, WN.receipt("r", k1, "p", 0), WN.answer("x", k3, "p", "object"), WN.landing("L", k1, "p", "r", "landed", W, ("x",)),
            RS.effect(spec, "E", k1, "L", pl)]
    pk = RS.lone_open(spec, "q", k1, "evict", ("E",), k3)
    rows += [pk, WN.receipt("rq", k1, "q", 0), RS.speak(spec, "t", k3, ("E",)), WN.landing("Lq", k1, "q", "rq", "landed", W), RS.effect(spec, "Eq", k1, "Lq", pk)]
    tie = lambda S, rows, n: "tie: roster %s" % sorted(RS.roster(S, spec)) if k3 in RS.roster(S, spec) else None
    b = run(spec, [("three keys, one stolen (k3) and one lost (k2)", rows)], tie, windows=wins)
    with mutated(windows={lone_ev: lambda w: dict(w, silent=None)}):
        pl = run(spec, [("same", rows)], tie, orders=False)
    res.append(result(inst, "combined3_mixed: one stolen and one lost of three is a tie", src, verdict_of(b, False), b,
                      "plant: no silence condition (the bound must vanish)", {"fails": [] if pl["fails"] else [("plant", "the owner evicts the thief: no tie")]}))

    # witness pair: a person's self roster and an agent's, given identical parameters
    if spec.obj == "S":
        pairs = []
        for itype in ("user", "agent"):
            g = dict(RS.found(spec, (k1, k2, k3)), identity_type=itype)
            p = RS.lone_open(spec, "p", k1, "evict", (spec.obj,), k2)
            pairs.append(("%s's roster: lone eviction of a silent key" % itype,
                          [g, p, WN.receipt("r", k1, "p", 0), WN.landing("L", k1, "p", "r", "landed", W), RS.effect(spec, "E", k1, "L", p)], itype))
        def pw(S, rows, n):
            itype = next(t for nn, _, t in pairs if nn == n)
            if itype == "agent" and k2 not in RS.roster(S, spec): return "an agent's roster ran the person's door"
            if itype == "user" and k2 in RS.roster(S, spec): return "a person's lone path did not land"
        P2 = [(n, r) for n, r, _ in pairs]
        plain = run(spec, P2, pw, orders=False)
        with mutated(params={"persons_only"}):
            b = run(spec, P2, pw)
        res.append(result(inst, "WITNESS PAIR: a person's and an agent's self roster, same parameters; CC 3.3.6.3 'The door is a person's ... an agent's occurrence is single-signer, and neither runs these paths'",
                          "CC 3.3.6.3 l.1996", verdict_of(b, param="persons_only (identity_type of the roster's root)"), b,
                          "plant: the parameter off (the plain mechanism)", plain))

    # S7 a vote from an evicted key is void; removal reaches by causal past, in every arrival order
    g = RS.found(spec, (k1, k2, k3))
    before = RS.speak(spec, "mb", k3, (spec.obj,))
    x = RS.remove(spec, "x", (spec.obj,), k3, (k1, k2), names=("mb",))
    conc = RS.speak(spec, "mc", k3, (spec.obj,))
    after = RS.speak(spec, "ma", k3, ("x",))
    rows = [g, before] + x + [conc, after]
    def p7(S, rows, n):
        st = tuple(CUT.Cut(S).status(S.by[i]) for i in ("mb", "mc", "ma"))
        if st != ("counts", "void", "concludes nothing"): return "statuses %s" % (st,)
    base = run(spec, [("an evicted key's rows: before, concurrent, after", rows)], p7, windows=wins)
    # MUTATION: a row of the removed key counts when it was held before the removal (arrival order)
    seen = set()
    for o in RS.linear_extensions(rows, CAP):
        ids = [r["id"] for r in o]
        seen.add("counts" if ids.index("mc") < ids.index("x") else "void")
    m = {"worlds": 1, "orders": 0, "fails": [("by arrival", "the concurrent row is %s depending on the order" % sorted(seen))] if len(seen) > 1 else []}
    res.append(result(inst, "a vote from an evicted key is void (removal by causal past)", src, verdict_of(base), base,
                      "removal reaches what arrived before it", m))
    return res


def check_voice_extra(spec, inst):
    """CC 3.1.3.2: a count in the room counts voices; a removed voice's keys speak for nobody."""
    res = []
    vspecs = {}
    for v in ("vA", "vB", "vC"):
        s = RS.Spec("voice " + v, v, "key", spec.add, spec.remove, floor=1, lone=spec.lone)
        RS.SPECS[v] = vspecs[v] = s
    room = RS.SPECS["g"]
    def voice_rows(v, devs):
        rows = [RS.found(vspecs[v], (devs[0],))]
        head = v
        for i, d in enumerate(devs[1:], 1):
            need = i // 2 + 1
            rid = "%s+%d" % (v, i)
            rows.append(RS.add(vspecs[v], rid, (head,), d, (devs[0],) + tuple(devs[1:need]) + (d,)))
            head = rid
        return rows, head
    n = bad = mut = 0
    for shape in itertools.product((1, 2), repeat=3):
        base, heads, devs = [], {}, {}
        for p, kk in zip("ABC", shape):
            devs[p] = ["d%s%d" % (p, i) for i in range(kk)]
            vr, heads[p] = voice_rows("v" + p, devs[p])
            base += vr
        g = ST.offer("g", "vA", ("vA", "vB", "vC"), "member", "@", "self", cosigners=("vB", "vC"), names=tuple(heads[p] for p in "ABC"))
        pr = R("pr", "proposal", "vA", ("g",))
        slots = [(p, d) for p in "ABC" for d in devs[p]]
        for choice in itertools.product(("yes", "no", None), repeat=len(slots)):
            rows = base + [g, pr]
            for (p, d), c in zip(slots, choice):
                if c: rows.append(RS.by_dev(R("t" + d, "vote", "v" + p, ("pr",), choice=c), d, (heads[p],)))
            S = RS.state(rows)
            mem = ST.Seats(S).holders("member", "g")
            got = {c: CK.tally(S, pr, mem, c, counting=CUT.Cut(S).counts) for c in ("yes", "no")}
            said = {p: {c for (q, d), c in zip(slots, choice) if q == p and c} for p in "ABC"}
            want = {c: sum(1 for p in "ABC" if said[p] == {c}) for c in ("yes", "no")}
            n += 1
            bad += got != want or len(mem) != 3
            mut += {c: sum(1 for x in choice if x == c) for c in ("yes", "no")} != want
    base = {"worlds": n, "orders": 0, "fails": [("tally", "%d differ" % bad)] if bad else [], "order_differs": []}
    res.append(result(inst, "one person, one voice: a tally over voices is the count of persons", "CC 3.1.3.2; KERNEL.md 7b",
                      verdict_of(base), base, "a count of room keys", {"fails": [("keys", "%d of %d differ" % (mut, n))] if mut else []}))
    # a removed voice: its room keys speak for nobody, a key added to it afterwards included
    vr, vh = voice_rows("vA", ["dA0", "dA1", "dA2"])
    vb, bh = voice_rows("vB", ["dB0"])
    vc, ch = voice_rows("vC", ["dC0"])
    g = ST.offer("g", "vA", ("vA", "vB", "vC"), "member", "@", "self", cosigners=("vB", "vC"), names=(vh, bh, ch))
    x = RS.remove(room, "x", ("g",), "vA", ("vB", "vC"))
    add = RS.add(vspecs["vA"], "vA+3", (vh,), "dA3", ("dA0", "dA1", "dA3"))
    conc = RS.by_dev(RS.speak(room, "mn", "vA", ("g",)), "dA3", ("vA+3",))
    after = RS.by_dev(RS.speak(room, "mz", "vA", ("x",)), "dA3", ("vA+3",))
    rows = vr + vb + vc + [g] + x + [add, conc, after]
    def pv(S, rows, n):
        st = (CUT.Cut(S).status(S.by["mn"]), CUT.Cut(S).status(S.by["mz"]))
        if "vA" in ST.Seats(S).holders("member", "g") or st != ("void", "concludes nothing"): return "statuses %s" % (st,)
    base = run(room, [("the room removes voice vA; vA adds a key and speaks", rows)], pv)
    # MUTATION: a room row is judged by its key's seat in the voice only
    m = run(room, [("same", [dict(r, kind="note") if r["id"] in ("mn", "mz") else r for r in rows])],
            lambda S, rows, n: None if (CUT.Cut(S).status(S.by["mn"]), CUT.Cut(S).status(S.by["mz"])) == ("void", "concludes nothing") else "the removed voice's new key speaks", orders=False)
    res.append(result(inst, "removal by causal past through a voice: a removed voice's room keys, a later one included, speak for nobody",
                      "KERNEL.md 7b; roomkey.device_cases", verdict_of(base), base, "the key's seat in the voice is all that is read", m))
    return res


# =================================================================================================================
# A room: the fork properties (formal/roster_fork) and the membership properties (formal/membership)
# =================================================================================================================
def check_fork(inst, proto, n, r0, f):
    m = lambda s: sum(1 << int(c) for c in s)
    MUST = ("function", "nsf_resolved", "kept_removed", "adv_alone", "not_final", "stale", "rejoin")
    t0 = time.time()
    m0 = FK.check("M0", n, m(r0), m(f), proto, 3, 0, regime=True)
    t6 = FK.check("T6", n, m(r0), m(f), proto, 3, 0, regime=True)
    bad = [x for x in MUST if m0.get(x)]
    base = {"worlds": m0["sets"], "orders": 0, "fails": [(x, m0[x]["text"]) for x in bad], "order_differs": []}
    return [result(inst, "roster_fork M0 (tips wait): %s over %s, adversary %s; 7 properties" % (proto, r0, f),
                   "formal/roster_fork/fork_check.py", verdict_of(base), base, "first version seen wins (rule T6 of fork.py)",
                   {"fails": [("function", t6["function"]["text"])] if t6.get("function") else []},
                   "costs shown: %s; %.1fs" % ([x for x in ("nsf_now", "removed_voice") if m0.get(x)], time.time() - t0))]


def nest(rows, persons):
    """The private-room form of a public room's rows: each person is a voice with one room key (rk<P>), every row the
    person signs is signed by that key in the voice's name. Returns the voice founding rows + the renamed rows."""
    v = {p: "v" + p for p in persons}
    out = [ST.offer(v[p], "rk" + p, ("rk" + p,), "key", "@", "self") for p in persons]
    ren = lambda x: v.get(x, x)
    for r in rows:
        r2 = dict(r)
        for f in ("signer", "target"):
            if r2.get(f) in v: r2[f] = v[r2[f]]
        for f in ("to", "cosigners"):
            if f in r2: r2[f] = tuple(ren(x) for x in r2[f])
        if "on" in r2: r2["on"] = tuple(tuple(ren(x) for x in s) for s in r2["on"])
        if "cuts" in r2: r2["cuts"] = tuple(tuple(ren(x) for x in s) for s in r2["cuts"])
        if r["signer"] in v:
            r2 = RS.by_dev(r2, "rk" + r["signer"], (v[r["signer"]],))
        out.append(r2)
    return out


def check_room(spec, inst, private):
    res = []
    persons = ("A", "B", "C", "J", "X")
    P = (lambda p: "v" + p) if private else (lambda p: p)
    wrap = (lambda rows: nest(rows, persons)) if private else (lambda rows: rows)
    for p in persons:                               # the voices are rosters of their own: the self parameters
        RS.SPECS["v" + p] = RS.Spec("voice", "v" + p, "key", RS.SPECS["S"].add, RS.SPECS["S"].remove)
    roster = lambda S: ST.Seats(S).holders("member", "g")
    src = "formal/membership/README.md; CC 3.1.3.2"
    g = RS.found(spec, ("A", "B", "C"))
    ac = RS.accept(spec, "ac", "J", ("g",))
    def world(name, rows): return (name, wrap(rows))

    # C1 Inv_JoinerConsented
    worlds = [world("widening names J's acceptance", [g, ac, RS.add(spec, "w", ("g",), "J", ("A", "B"), names=("ac",))]),
              world("widening with no acceptance", [g, RS.add(spec, "w", ("g",), "J", ("A", "B"))]),
              world("founding lists J, J does not sign", [ST.offer("g", "A", ("A", "B", "C", "J"), "member", "@", "self", cosigners=("B", "C"))])]
    def c1(S, rows, n):
        if P("J") in roster(S) and "names" not in n: return "J seated without consent"
    base = run(spec, worlds, c1)
    mw = [(n, [dict(r, consent="one") if r["kind"] == "offer" and r["id"] != r["obj"] else r for r in rows]) for n, rows in worlds]
    mw[2] = world("founding lists J (mutation: the founding row seats every listed key)", [ST.offer("g", "A", ("A", "B", "C", "J"), "member", "@", "self", cosigners=("B", "C", "J"))])
    res.append(result(inst, "Inv_JoinerConsented", src, verdict_of(base), base, "no acceptance needed (consent='one')", run(spec, mw, c1, orders=False)))

    # C2 Inv_DeclineTerminal and Inv_LeavingNotUndone
    dec = ST.withdraw("dec", "J", "ac")
    worlds = [world("J declines (withdraws its acceptance), then a widening names it", [g, ac, dec, RS.add(spec, "w", ("g",), "J", ("A", "B"), names=("ac", "dec"))]),
              world("J resigns (withdraws its acceptance) after the widening; a second widening names the old acceptance",
                    [g, ac, RS.add(spec, "w", ("g",), "J", ("A", "B"), names=("ac",)), ST.withdraw("res", "J", "ac", ("w",)),
                     RS.add(spec, "w2", ("w",), "J", ("A", "B", "C"), names=("res", "ac"))])]
    def c2(S, rows, n):
        if P("J") in roster(S): return "J seated"
    base = run(spec, worlds, c2)
    with mutated(mut={"decline_ignored"}):
        m = run(spec, worlds, c2, orders=False)
    res.append(result(inst, "Inv_DeclineTerminal, Inv_LeavingNotUndone (leaving = withdrawing the acceptance)", src, verdict_of(base), base,
                      "a withdrawal concludes nothing", m))
    # the same leaving, read as the holder withdrawing the SEAT (the offer) and not the acceptance
    lw = [world("J resigns by withdrawing the widening that seated it; a second widening names the old acceptance",
                [g, ac, RS.add(spec, "w", ("g",), "J", ("A", "B"), names=("ac",)), ST.withdraw("res", "J", "w"),
                 RS.add(spec, "w2", ("w",), "J", ("A", "B", "C"), names=("res", "ac"))])]
    keep = set(RS.PARAMS); RS.PARAMS.discard("spent")          # the kernel as it is
    b = run(spec, lw, c2)
    RS.PARAMS |= keep
    res.append(result(inst, "Inv_LeavingNotUndone, leaving read as a withdrawal of the seat", src,
                      "does NOT hold" if b["fails"] else "holds", b, None, None,
                      "an acceptance with no `of` is not spent by the widening that used it (CC 3.1.3.2 admission (5))" if b["fails"] else ""))
    with mutated(params={"spent"}):
        b2 = run(spec, lw, c2)
    res.append(result(inst, "Inv_LeavingNotUndone, leaving read as a withdrawal of the seat, with the stated parameter", src,
                      verdict_of(b2, param="spent (CC 3.1.3.2 admission (5): 'P has not already seated K')"), b2,
                      "plant: spent off (the kernel as it is)", b))

    # C3 Inv_NoSelfAdmission
    worlds = [world("X, not a member, offers itself a seat counted over the room", [g, RS.accept(spec, "ax", "X", ("g",)), RS.add(spec, "w", ("g",), "X", ("X",), names=("ax",))])]
    def c3(S, rows, n):
        if P("X") in roster(S): return "X seated itself"
    base = run(spec, worlds, c3)
    with mutated(mut={"self_admit"}):
        m = run(spec, worlds, c3, orders=False)
    res.append(result(inst, "Inv_NoSelfAdmission", src, verdict_of(base), base, "a key's offer to itself counts", m))

    # C4 Inv_CoercedCannotRemoveHonest and the floor of two voices, under every protocol (founder_only/one included)
    worlds = []
    for proto_kind in (ST.POLICY[spec.remove], ("one", 1, 1)):
        worlds.append(("one member (C, coerced) removes A, count %s" % (proto_kind,), [g] + RS.remove(spec, "x", ("g",), "A", ("C",)), proto_kind))
    def c4(S, rows, n):
        if P("A") not in roster(S): return "A removed by one signature"
    bases, ms = [], []
    for n_, rows, kind in worlds:
        with mutated(policy={spec.remove: kind}):
            bases.append(run(spec, [(n_, wrap(rows))], c4))
        with mutated(policy={spec.remove: kind}, mut={"no_floor"}):
            ms.append(run(spec, [(n_, wrap(rows))], c4, orders=False))
    base = {"worlds": 2, "orders": sum(b["orders"] for b in bases), "fails": [f for b in bases for f in b["fails"]], "order_differs": []}
    m = {"fails": [f for x in ms for f in x["fails"]]}
    res.append(result(inst, "Inv_CoercedCannotRemoveHonest, with the floor of two voices under every protocol", src + "; CC 4.5.13",
                      verdict_of(base, param="floor=2 (the table's min_count)"), base, "no floor (founder_only: one founder removes)", m,
                      "formal/membership states the founder_only case as a bound; CC 3.1.3.2 says 'one signature never removes'"))

    # C5 Inv_ResignationEnabled: a member alone ends its own seat, a counted one included
    worlds = [world("J, seated by a count, withdraws its acceptance alone", [g, ac, RS.add(spec, "w", ("g",), "J", ("A", "B"), names=("ac",)), ST.withdraw("res", "J", "ac", ("w",))]),
              world("A, a founder, withdraws its founding seat alone", [g, ST.withdraw("res", "A", "g")])]
    def c5(S, rows, n):
        who = P("J") if "J," in n else P("A")
        if who in roster(S): return "%s still seated" % who
    base = run(spec, worlds, c5)
    with mutated(mut={"decline_ignored"}):
        m = run(spec, worlds, c5, orders=False)
    res.append(result(inst, "Inv_ResignationEnabled", src, verdict_of(base), base, "a withdrawal concludes nothing", m))

    # C6 no duty holder left: the members' count seats one; one member alone cannot
    def mod(id, signers, names=()):
        return ST.offer(id, signers[0], P("B") if private else "B", "moderate", "g", "group", ("g",) + tuple(names), head=("g",),
                        policy=spec.add, counted="member", cosigners=tuple(signers[1:]))
    worlds = [world("the members' count seats B to moderate", [g, ST.accept("am", "B", None, ("g",), scope="moderate", obj="g"), mod("m", ("A", "C"), ("am",))]),
              world("one member alone seats B to moderate", [g, ST.accept("am", "B", None, ("g",), scope="moderate", obj="g"), mod("m", ("A",), ("am",))])]
    def c6(S, rows, n):
        has = (P("B") if private else "B") in ST.Seats(S).holders("moderate", "g")
        if has != ("count" in n): return "moderate seat %s" % has
    base = run(spec, worlds, c6)
    with mutated(policy={spec.add: ("one", 1, 1)}, mut={"no_floor"}):
        m = run(spec, worlds, c6, orders=False)
    res.append(result(inst, "when no duty holder is left the members' count seats one (and one member does not)", "ruling in force; CC 4.5.4",
                      verdict_of(base), base, "one voice seats", m))

    # C7 the reverse path of community_invite: a member's proposal and the joiner's yes land at the close unless a third objects
    lw = spec.lone["add"]
    worlds = []
    for objectors in ((), ("C",), ("B", "C")):
        p = RS.lone_open(spec, "p", "A", "add", ("g",), "J")
        obj_rows = [WN.answer("o" + o, o, "p", "object") for o in objectors]
        rows = [g, p, ac, WN.answer("aj", "J", "p", "approve"), WN.receipt("r", "A", "p", 0)] + obj_rows + \
               [WN.landing("L", "A", "p", "r", "landed", 3 * W, ("aj",) + tuple(r["id"] for r in obj_rows)), RS.effect(spec, "E", "A", "L", p, ("ac",))]
        worlds.append(world("reverse path, %d objecting of 3" % len(objectors), rows))
    floor = WN.WINDOWS[lw]["at_close"]
    def c7(S, rows, n):
        seated = P("J") in roster(S)
        want = n.endswith(" 0 objecting of 3")
        if seated != want: return "seated=%s" % seated
    def c7(S, rows, n):
        seated = P("J") in roster(S)
        want = int(n.split(", ")[1].split()[0]) < 2          # cancel: at least a third, never fewer than two
        if seated != want: return "%s: seated=%s" % (n, seated)
    plain = run(spec, worlds, c7)
    with mutated(windows={lw: lambda w: dict(w, target_votes=True)}):
        base = run(spec, worlds, c7)
        with mutated(windows={lw: lambda w: dict(w, at_close=w["at_close"][1:])}):
            m = run(spec, worlds, c7, orders=False)
    res.append(result(inst, "community_invite reverse path: one member's proposal and the joiner's yes land at the close unless a third objects",
                      "manifests/governance_policy.json community_invite note; CC 3.1.3.2 'the invitee's acceptance is the second voice'",
                      verdict_of(base, param="target_votes (the joiner's own yes is a voice of the window's floor)"), base, "no cancel", m,
                      "without the parameter: %s" % (plain["fails"][:1] or "holds")))
    # C8 tips wait on the kernel's own seats: two versions of one head, then a version naming both
    ax = RS.accept(spec, "ax", "X", ("g",))
    v1 = RS.add(spec, "v1", ("g",), "X", ("A", "B"), names=("ax",))
    v2 = RS.remove(spec, "v2", ("g",), "C", ("A", "B"))
    mg = RS.add(spec, "mg", ("v1", v2[-1]["id"]), "X", ("A", "B"), names=("ax",))
    worlds = [world("two versions of g wait", [g, ax, v1] + v2), world("a version names both tips", [g, ax, v1] + v2 + [mg])]
    TIPS = {"union": False}
    def c8(S, rows, n):
        got = roster(S)
        if TIPS["union"]:
            got = frozenset().union(*[ST.Seats(CK.State([q for q in S.Cs if q["id"] == t["id"] or q["id"] in S.anc[t["id"]]],
                                                         {q["id"]: True for q in S.Cs})).holders("member", "g") for t in ST.Seats(S).tips("g")]) \
                if len(ST.Seats(S).tips("g")) > 1 else got
        want = {P("A"), P("B")} | ({P("X")} if "both" in n else set())
        if got != want: return "%s: roster %s" % (n, sorted(got))
    base = run(spec, worlds, c8)
    TIPS["union"] = True
    m = run(spec, worlds, c8, orders=False)
    res.append(result(inst, "tips wait (KERNEL 7): two versions of one head give the members common to both; a version naming both makes one head",
                      "CC 3.2 T6; formal/roster_fork", verdict_of(base), base, "the tips' union (a removal on one tip does not reach)", m))
    return res


# =================================================================================================================
# The accord: formal/accord_roster/README.md
# =================================================================================================================
def check_accord(spec, inst):
    res = []
    src = "formal/accord_roster/README.md; CC 4.2.6"
    roster = lambda S: ST.Seats(S).holders("holder", "A")
    # A1 standing_seize_iff: removal of an honest holder needs floor(N/2)+1 coerced; censorship buys nothing
    worlds, want = [], {}
    for N in (3, 4, 5):
        hs = tuple("h%d" % i for i in range(1, N + 1))
        g = RS.found(spec, hs, recovery={h: "r" + h for h in hs})
        for c in range(1, N):
            co = hs[:c]
            for censored in ("all", "none"):
                prop = R("prop", "accord_proposal", co[0], ("A",))
                parts = [R("pt" + h, "participate", h, ("prop",), of="prop", vote="no") for h in hs[c:]] if censored == "none" else []
                parts += [R("pt" + h, "participate", h, ("prop",), of="prop", vote="yes") for h in co]
                x = RS.remove(spec, "x", ("A",), hs[-1], co, names=("prop",) + tuple("pt" + h for h in co), proposal="prop")
                y = RS.add(spec, "y", ("A",), "pup", co + ("pup",), names=("prop",), proposal="prop")
                for act, rows_ in (("removes h%d" % N, x), ("seats a puppet", [y])):
                    name = "N=%d, %d coerced %s, honest %s" % (N, c, act, "censored" if censored == "all" else "voting no")
                    worlds.append((name, [g, prop] + parts + rows_))
                    want[name] = (c >= N // 2 + 1, hs[-1], "puppet" in act)
    def a1(S, rows, n):
        seized, h, pup = want[n]
        got = roster(S)
        did = ("pup" in got) if pup else (h not in got)
        if did != seized: return "%s: %s, expected %s" % (n, did, seized)
    base = run(spec, worlds, a1, orders=False)
    small = [w for w in worlds if w[0].startswith("N=3")]
    ob = run(spec, small, a1)
    base["orders"] = ob["orders"]; base["order_differs"] = ob["order_differs"]
    with mutated(mut={"live_set"}):
        m = run(spec, worlds, a1, orders=False)
    res.append(result(inst, "standing_seize_iff / standing_censorship_irrelevant (removal and puppet need floor(N/2)+1)", src,
                      verdict_of(base), base, "count over the live set (who took part)", m, "every order checked for N=3"))
    # A2 frozen after decimation, survivors keep fire
    hs = ("h1", "h2", "h3", "h4", "h5")
    g = RS.found(spec, hs, recovery={h: "r" + h for h in hs})
    rows = [g, RS.accept(spec, "a6", "h6", ("A",)), RS.add(spec, "y", ("A",), "h6", ("h4", "h5"), names=("a6",)), WN.opener("fire", "h5", "halt_fuse", "A", ("A",))]
    def a2(S, rows, n):
        if "h6" in roster(S): return None
        return "frozen: roster %s; a survivor's fire concludes: %s" % (sorted(roster(S)), S.C.get("fire"))
    b = run(spec, [("five holders, three lost: the two survivors add a sixth, and h5 fires", rows)], a2)
    with mutated(mut={"live_set"}):
        pl = run(spec, [("same", rows)], a2, orders=False)
    res.append(result(inst, "standing_frozen_after_decimation, standing_survivors_keep_fire", src, verdict_of(b, False), b,
                      "plant: count over the live set (the freeze must vanish)", {"fails": [] if pl["fails"] else [("plant", "survivors seat h6")]}))
    # A3/A4 recovery keys help heal and never help seizure
    g3 = RS.found(spec, ("h1", "h2", "h3"), recovery={"h1": "rh1", "h2": "rh2", "h3": "rh3"})
    heal = [("h1 lost its signing key; its recovery key seats h1b", [g3] + RS.recovery(spec, "rv", "rh1", "h1", "h1b", ("A",)))]
    def a3(S, rows, n):
        if roster(S) != {"h1b", "h2", "h3"}: return "roster %s" % sorted(roster(S))
    base = run(spec, heal, a3)
    with mutated(mut={"no_recovery"}):
        m = run(spec, heal, a3, orders=False)
    res.append(result(inst, "recovery_keys_help_heal (a single-signer version, no quorum)", src, verdict_of(base, param="the recovery parameter (a second root: the committed key)"),
                      base, "no recovery version", m))
    seize = [("coerced h3 uses its own recovery key on h1's seat", [g3] + RS.recovery(spec, "rv", "rh3", "h1", "pup", ("A",))),
             ("coerced h3's recovery version unseats h1 as well as its own", [g3] + [dict(r, to=("h1",), cuts=(("seat", "h1", "holder", "A"),)) if r["kind"] == "unseat" else r
                                                                                for r in RS.recovery(spec, "rv", "rh3", "h3", "pup", ("A",))])]
    def a4(S, rows, n):
        if "h1" not in roster(S): return "h1 removed"
    base = run(spec, seize, a4)
    with mutated(mut={"recovery_any_seat"}):
        m = run(spec, seize, a4, orders=False)
    res.append(result(inst, "recovery_keys_never_help_seizure", src, verdict_of(base), base, "a recovery version may change any seat", m))
    # A5 the fuse: window.py's halt cases on the one rule
    title, cases = WN.halt_world()
    bad, broken = [], 0
    for name, rows, prop, need in cases:
        S1 = CK.concluded(CK.kept(rows), RS.rule)
        S2 = CK.concluded(CK.kept(rows), WN.rule)
        o1, o2 = WN.outcomes(S1, "p"), WN.outcomes(S2, "p")
        if o1 != o2 or (need and not WN.holds(need, o1["recount"])): bad.append(name)
        if need and not WN.holds(need, o1["void"]): broken += 1
    base = {"worlds": len(cases), "orders": 0, "fails": [(b, "") for b in bad], "order_differs": []}
    res.append(result(inst, "the halt fuse (window.py halt cases): one holder fires, lapses unless a strict majority confirms", "CC 4.2.1.1; window.py",
                      verdict_of(base), base, "the landing voids concurrent answers", {"fails": [("void", "%d cases broken" % broken)] if broken else []}))
    # A6 the fire against a removal: lame duck, latch, and a removed holder
    x = RS.remove(spec, "x", ("A",), "h3", ("h1", "h2"))
    f_conc = WN.opener("fc", "h3", "halt_fuse", "A", ("A",))
    f_after = WN.opener("fa", "h3", "halt_fuse", "A", ("A",), names=("x",))
    S = RS.state([g3] + x + [f_conc, f_after])
    plain = (S.C["fc"], S.C["fa"])
    slot = lambda r: dict(r, on=(("seat", "h3", "holder", "A"),))
    S2 = RS.state([g3] + x + [slot(f_conc), slot(f_after)])
    cut2 = (CUT.Cut(S2).status(S2.by["fc"]), CUT.Cut(S2).status(S2.by["fa"]))
    latch = set()
    for o in RS.linear_extensions([g3] + x + [f_conc], CAP):
        ids = [r["id"] for r in o]
        latch.add("fired" if ids.index("fc") < ids.index("x") else "refused")
    w = ("plain mechanism: concurrent fire concludes %s, a fire naming the removal (old head) concludes %s; "
         "fire on the seat slot: concurrent %s, after %s; latch on receipt: %s by order" % (plain + cut2 + (sorted(latch),)))
    base = {"worlds": 1, "orders": len(RS.linear_extensions([g3] + x + [f_conc], CAP)), "fails": [("fire", w)], "order_differs": []}
    # the stated parameter: a node latches a fire on receipt iff it does not already hold the recorded removal of its signer
    lrows = [g3] + x + [f_conc, f_after]
    bad_l, nord = [], 0
    for o in RS.linear_extensions(lrows, CAP):
        nord += 1
        ids = [r["id"] for r in o]
        held_x = lambda fid: ids.index(x[-1]["id"]) < ids.index(fid)
        latched = {fid for fid in ("fc", "fa") if not held_x(fid)}
        # lame duck: the concurrent fire latches wherever it arrived before the decision; the fire after it never does
        if ("fc" in latched) != (ids.index("fc") < ids.index(x[-1]["id"])) or "fa" in latched: bad_l.append(ids)
    lb = {"worlds": 1, "orders": nord, "fails": [("latch", str(bad_l[:1]))] if bad_l else [], "order_differs": []}
    res.append(result(inst, "lame duck AND a removed holder no longer fires, with the latch on receipt (a reader-relative parameter that reads arrival order)",
                      "CC 4.2.1.1 'fires on receipt, latches'; CC 4.2.6 l.318", verdict_of(lb, param="latch_on_receipt (per node; NOT a function of the rows)"),
                      lb, "plant: the plain mechanism (judged at the head the fire names)", {"fails": [("plain", "a removed holder's fire naming the removal concludes %s" % plain[1])] if plain[1] else []}))
    res.append(result(inst, "lame duck (a holder named for removal fires until the decision) AND a removed holder no longer fires", "CC 4.2.6 'Removal cannot silence a firer'; CC 4.2.1.1 'fires on receipt, latches'",
                      "does NOT hold", base, None, None,
                      "the plain mechanism gives the lame duck and lets a removed holder fire for ever on an old head; putting the fire on the seat slot ends that but voids a latched fire; the text's rule is a latch at the node's receipt, which depends on arrival order by design"))
    return res


# =================================================================================================================
# An infrastructure community: CC 3.2 Infrastructure does not vote, T6, T7
# =================================================================================================================
def check_infra(spec, inst):
    res = []
    src = "CC 3.2 'Infrastructure does not vote', T6, T7"
    g = RS.found(spec, ("f1", "f2", "f3"), scope="founder")
    members = lambda S: ST.Seats(S).holders("member", "I")
    founders = lambda S: ST.Seats(S).holders("founder", "I")
    node = RS.add(spec, "n1", ("I",), "node1", ("f1", "f2"), consent="one")
    aj = RS.accept(spec, "aj", "J", ("I",), scope="member")
    # I1 a node is seated with no acceptance and never votes
    worlds = [("founders seat node1; node1 and f1 widen J", [g, node, aj, RS.add(spec, "w", ("n1",), "J", ("f1", "node1"), names=("aj",))])]
    def i1(S, rows, n):
        if "node1" not in members(S): return "node not seated"
        if "J" in members(S): return "a node's voice counted"
    base = run(spec, worlds, i1)
    with mutated(spec_attr={("I", "counted"): "member"}):
        m = run(spec, [(n, [dict(r, counted="member") if r.get("counted") == "founder" else r for r in rows]) for n, rows in worlds], i1, orders=False)
    res.append(result(inst, "a node is seated without consent and is never counted", src, verdict_of(base, param="counted=founder, consent=one for nodes"),
                      base, "the count is over every member", m))
    # I2 no single founder admits
    worlds = [("f1 alone widens J", [g, aj, RS.add(spec, "w", ("I",), "J", ("f1",), names=("aj",))]),
              ("f1 and f2 widen J", [g, aj, RS.add(spec, "w", ("I",), "J", ("f1", "f2"), names=("aj",))])]
    def i2(S, rows, n):
        if ("J" in members(S)) != ("and" in n): return "J seated=%s" % ("J" in members(S))
    base = run(spec, worlds, i2)
    with mutated(mut={"no_floor"}):
        m = run(spec, [(n, [dict(r, need=1) if r.get("need") else r for r in rows]) for n, rows in worlds], i2, orders=False)
    res.append(result(inst, "no single founder admits alone (quorum:2/3)", src, verdict_of(base), base, "quorum:1/N and no floor", m))
    # I3 T7: stalled at M active founders, non-admitting
    wd = ST.withdraw("wd3", "f3", "I")
    worlds = [("f3 leaves; f1 and f2 widen J", [g, wd, aj, RS.add(spec, "w", ("wd3",), "J", ("f1", "f2"), names=("aj",))])]
    def i3(S, rows, n):
        if "J" in members(S): return "a stalled roster admitted J"
    base = run(spec, worlds, i3)
    with mutated(mut={"no_margin"}):
        m = run(spec, worlds, i3, orders=False)
    res.append(result(inst, "T7: a roster at M active founders is stalled and admits nothing by the count", src,
                      verdict_of(base, param="margin=1 (live while need+1 founders)"), base, "no margin (the plain quorum)", m))
    # I4 T7 recovery: one founder-adding widening by the conferring body, only while stalled, the conferred key signing
    worlds = [("stalled: the body seats f4, who signs", [g, wd, RS.body_widening(spec, "bw", "BODY", "f4", ("wd3",))], True),
              ("live: the body seats f4", [g, RS.body_widening(spec, "bw", "BODY", "f4", ("I",))], False),
              ("stalled: the body seats f4, who does not sign", [g, wd, dict(RS.body_widening(spec, "bw", "BODY", "f4", ("wd3",)), cosigners=())], False)]
    def i4(S, rows, n):
        want = next(w for nn, _, w in worlds if nn == n)
        if ("f4" in founders(S)) != want: return "f4 founder=%s" % ("f4" in founders(S))
    W4 = [(n, r) for n, r, _ in worlds]
    base = run(spec, W4, i4)
    with mutated(mut={"body_any_time"}):
        m = run(spec, W4, i4, orders=False)
    res.append(result(inst, "T7 recovery: the conferring body's one widening", src, verdict_of(base, param="body (a second conferrer, active only while stalled)"),
                      base, "the body may widen at any time", m))
    # I5 T6: a witnessed lineage refuses a rival that is not witnessed; an ordinary room's tips wait
    v1 = RS.add(spec, "v1", ("I",), "J", ("f1", "f2"), names=("aj",))
    v2 = RS.remove(spec, "v2", ("I",), "f1", ("f2", "f3"))
    rows = [g, aj, v1] + v2
    S = RS.state(rows)
    tips = members(S)
    sub = [r for r in S.Cs if r["id"] == "v1" or r["id"] in S.anc["v1"]]
    witnessed = ST.Seats(CK.State(sub, {r["id"]: True for r in sub})).holders("member", "I")
    b = {"worlds": 1, "orders": len(RS.linear_extensions(rows, CAP)), "fails": [], "order_differs": []}
    res.append(result(inst, "T6: a witnessed lineage refuses the rival head that is not witnessed", src,
                      "holds with witnessed (a reader's parameter: which tip its witnesses named)", b, "tips wait (an ordinary room)",
                      {"fails": [("rival", "tips wait: %s; witnessed v1: %s" % (sorted(tips), sorted(witnessed)))] if tips != witnessed else []}))
    return res


# =================================================================================================================
# Plant at the level of the instance: a made-up roster that SHOULD fail
# =================================================================================================================
def spent_room(I):
    with mutated(params={"spent"}):
        return check_room(I["community"], "community, with the stated parameter spent on (does it break anything else?)", False)


def check_madeup(I, inst="MADE-UP: a room where one signature removes (no floor)"):
    one = RS.register("R:madeup_one", ("one", 1, 1))
    bad = RS.Spec("madeup", "M", "member", one, one, floor=1, unit="person")
    RS.SPECS["M"] = bad
    g = RS.found(bad, ("A", "B", "C"))
    worlds = [("one member (C, coerced) removes A", [g] + RS.remove(bad, "x", ("M",), "A", ("C",))),
              ("one member (C) seats a puppet", [g, RS.accept(bad, "ap", "pup", ("M",)), RS.add(bad, "y", ("M",), "pup", ("C",), names=("ap",))])]
    def pm(S, rows, n):
        got = ST.Seats(S).holders("member", "M")
        if "A" not in got or "pup" in got: return "%s: roster %s" % (n, sorted(got))
    b = run(bad, worlds, pm)
    return [result(inst, "Inv_CoercedCannotRemoveHonest on an instance built to violate it (must be refused)", "plant",
                   "refused as required" if b["fails"] else "PLANT NOT CAUGHT", b, None, None)]


# =================================================================================================================
# A key's revocation: CC 2.4.1.1 "Three may revoke a key, and no other." The key's own and the owner's, here; the
# roster's count is the self roster's eviction and the room's removal, run above.
# =================================================================================================================
@contextlib.contextmanager
def seat_mut(*names):
    saved = set(ST.MUT)
    try:
        ST.MUT |= set(names)
        yield
    finally:
        ST.MUT.clear(); ST.MUT |= saved


def check_key_revocation(inst="a key (its registration, its owner, its revokers)"):
    """KY registers itself; OW owns it by an owner-binding the key itself signed (CC 3.2 The first binding); OV a
    second owner; TX any third key. A row of KY is on the slot of its registration, so the revocation is a cut there:
    a row in its past stands, one concurrent with it is void, one that names it concludes nothing."""
    spec = RS.Spec("key", "KY", "registered", None, None, floor=1)
    RS.SPECS["KY"] = spec
    src = "CC 2.4.1.1 'Three may revoke a key, and no other.'; CC 3.2 owner-binding"
    slot = (("seat", "KY", "registered", "KY"),)
    row = lambda i, names: R(i, "speak", "KY", tuple(names), obj="KY", head=tuple(names), on=slot)
    rec = ST.offer("rec", "KY", "KY", "registered", "KY", "self")
    def binding(i, owner, how):
        if how == "one row": return [ST.offer(i, "KY", owner, "owner", "KY", "self", ("rec",), cosigners=(owner,))]
        return [ST.offer(i, "KY", owner, "owner", "KY", "self", ("rec",)), ST.accept("a" + i, owner, i)]       # the genesis record and the owner's row
    def own_rev(i, names): return ST.unseat(i, "KY", "KY", "registered", "KY", "self", tuple(names))
    def owner_rev(i, signer, under, names): return ST.unseat(i, signer, "KY", "registered", "KY", "seat", tuple(names), under=under)
    registered = lambda S: "KY" in ST.Seats(S).holders("registered", "KY")
    status = lambda S, i: CUT.Cut(S).status(S.by[i])
    res = []

    # K1 the key's own revocation revokes, by causal past
    W1 = [("the key revokes itself; its rows before, concurrent, after",
           [rec, row("mb", ("rec",)), own_rev("rv", ("rec", "mb")), row("mc", ("rec",)), row("ma", ("rv",))])]
    def k1(S, rows, n):
        st = tuple(status(S, i) for i in ("mb", "mc", "ma"))
        if registered(S) or st != ("counts", "void", "concludes nothing"): return "registered %s, statuses %s" % (registered(S), st)
    base = run(spec, W1, k1)
    m = run(spec, [(n, [r for r in rows if r["id"] != "rv"] + [ST.unseat("rv", "KY", "KY", "registered", "KY", "group", ("rec", "mb"))]) for n, rows in W1], k1, orders=False)
    res.append(result(inst, "the key's own revocation ends its registration from the revocation forward, by causal past", src,
                      verdict_of(base), base, "the revocation signed as a count, not as the key's own", m))

    # K2 a third key's revocation revokes nothing (under the owner's binding, as its own, or by a binding the key never cosigned)
    W2 = []
    for how in ("one row", "two rows"):
        b = binding("ob", "OW", how)
        tail = tuple(r["id"] for r in b)
        W2.append(("a third key revokes under the owner's binding (%s)" % how, [rec] + b + [owner_rev("rv", "TX", "ob", tail), row("mc", ("rec",))]))
        W2.append(("a third key revokes as if its own (%s)" % how, [rec] + b + [ST.unseat("rv", "TX", "KY", "registered", "KY", "self", tail), row("mc", ("rec",))]))
    W2.append(("a third key binds itself without the key's signature and revokes",
               [rec, ST.offer("ob", "TX", "TX", "owner", "KY", "self", ("rec",)), owner_rev("rv", "TX", "ob", ("ob",)), row("mc", ("rec",))]))
    def k2(S, rows, n):
        if not registered(S) or status(S, "mc") != "counts": return "registered %s, the key's row concurrent with it %s" % (registered(S), status(S, "mc"))
    base = run(spec, W2, k2)
    with seat_mut("any_key_revokes"):
        m = run(spec, W2, k2, orders=False)
    res.append(result(inst, "a revocation signed by any other key revokes nothing", src, verdict_of(base), base,
                      "any key's unseat under a seat counts", m))

    # K3 the owner's revocation revokes, by causal past
    W3 = []
    for how in ("one row", "two rows"):
        b = binding("ob", "OW", how)
        tail = tuple(r["id"] for r in b)
        W3.append(("the owner revokes (%s); the key's rows before, concurrent, after" % how,
                   [rec] + b + [row("mb", ("rec",)), owner_rev("rv", "OW", "ob", tail + ("mb",)), row("mc", ("rec",)), row("ma", ("rv",))]))
        W3.append(("the owner revokes (%s) while the owner's withdrawal of the binding is concurrent" % how,
                   [rec] + b + [row("mb", ("rec",)), owner_rev("rv", "OW", "ob", tail + ("mb",)), ST.withdraw("wb", "OW", "ob", tail),
                                row("mc", ("rec",)), row("ma", ("rv",))]))
    def k3(S, rows, n):
        st = tuple(status(S, i) for i in ("mb", "mc", "ma"))
        if registered(S) or st != ("counts", "void", "concludes nothing"): return "registered %s, statuses %s" % (registered(S), st)
    base = run(spec, W3, k3)
    with seat_mut("owner_not_a_revoker"):
        saved = dict(ST.ENDS); ST.ENDS.clear()
        try: m = run(spec, W3, k3, orders=False)
        finally: ST.ENDS.update(saved)
    res.append(result(inst, "the owner's revocation ends the key's registration from the revocation forward, by causal past", src,
                      verdict_of(base), base, "no seat ends another key's seat (the owner is not a revoker)", m))

    # K4 a former owner: the binding was withdrawn in the revocation's past
    W4 = []
    for how in ("one row", "two rows"):
        b = binding("ob", "OW", how)
        tail = tuple(r["id"] for r in b)
        W4.append(("the owner withdraws the binding, then revokes (%s)" % how,
                   [rec] + b + [ST.withdraw("wb", "OW", "ob", tail), owner_rev("rv", "OW", "ob", ("wb",)), row("mc", ("rec",))]))
    def k4(S, rows, n):
        if not registered(S) or status(S, "mc") != "counts": return "registered %s, the key's row concurrent with it %s" % (registered(S), status(S, "mc"))
    base = run(spec, W4, k4)
    with seat_mut("owner_unread"):
        m = run(spec, W4, k4, orders=False)
    res.append(result(inst, "a former owner, whose binding was withdrawn in the revocation's past, revokes nothing", src,
                      verdict_of(base), base, "the binding the revocation names is read, not whether it is live", m))

    # K5 two live owner-bindings naming different owners: steward-less (CC 3.2), and neither alone revokes (derived)
    W5 = []
    for how in ("one row", "two rows"):
        b1, b2 = binding("ob", "OW", how), binding("ov", "OV", how)
        tail = tuple(r["id"] for r in b1 + b2)
        for who, under in (("OW", "ob"), ("OV", "ov")):
            W5.append(("two live owners (%s); %s revokes alone" % (how, who),
                       [rec] + b1 + b2 + [owner_rev("rv", who, under, tail), row("mc", ("rec",))]))
    def k5(S, rows, n):
        if ST.Seats(S).one("owner", "KY") is not None: return "an owner is read: %s" % ST.Seats(S).one("owner", "KY")
        if not registered(S) or status(S, "mc") != "counts": return "registered %s, the key's row concurrent with it %s" % (registered(S), status(S, "mc"))
    base = run(spec, W5, k5)
    with seat_mut("owner_any_live"):
        m = run(spec, W5, k5, orders=False)
    res.append(result(inst, "two live owner-bindings naming different owners: no owner, and neither alone revokes (derived from CC 3.2 owner_of)", src,
                      verdict_of(base), base, "any live owner revokes, not the one owner", m))

    # K6 a revoked key does not un-revoke itself: it re-registers, or withdraws its own revocation
    W6 = []
    for by in ("itself", "its owner"):
        b = binding("ob", "OW", "one row")
        rv = own_rev("rv", ("ob",)) if by == "itself" else owner_rev("rv", "OW", "ob", ("ob",))
        W6.append(("revoked by %s; the key signs a fresh registration after" % by,
                   [rec] + b + [rv, ST.offer("rec2", "KY", "KY", "registered", "KY", "self", ("rv",)), row("ma", ("rec2",))]))
        W6.append(("revoked by %s; the key withdraws the revocation and registers again" % by,
                   [rec] + b + [rv, ST.withdraw("wr", "KY", "rv"), ST.offer("rec2", "KY", "KY", "registered", "KY", "self", ("wr",)), row("ma", ("rec2",))]))
    def k6(S, rows, n):
        if registered(S) or status(S, "ma") == "counts": return "registered %s, the key's later row %s" % (registered(S), status(S, "ma"))
    base = run(spec, W6, k6)
    with seat_mut("reseat"):
        m = run(spec, W6, k6, orders=False)
    res.append(result(inst, "a revoked key cannot un-revoke itself (a revocation is never withdrawn)", src, verdict_of(base), base,
                      "a key's own offer re-seats it after its revocation", m))
    return res


def check_leaving(spec, inst):
    """KERNEL.md 6 and 7, RosterHead.lean leaving_binds_by_past: a version that has a key's leaving in its own past
    does not count that key's signature, whatever head it names; one naming the head without that leaving still does.
    A and B found the room; D joins by v1; D withdraws its acceptance (wD); v2 names v1 and adds E, signed by A and D."""
    g = RS.found(spec, ("A", "B"))
    base_rows = [g, RS.accept(spec, "aD", "D", ("g",)), RS.add(spec, "v1", ("g",), "D", ("A", "B"), names=("aD",)),
                 ST.withdraw("wD", "D", "aD", ("v1",)), RS.accept(spec, "aE", "E", ("g",))]
    W = [("D's leaving in v2's past", base_rows + [RS.add(spec, "v2", ("v1",), "E", ("A", "D"), names=("aE", "wD"))], False),
         ("D's leaving concurrent with v2", base_rows + [RS.add(spec, "v2", ("v1",), "E", ("A", "D"), names=("aE",))], True)]
    def pl(S, rows, n):
        want = dict((w[0], w[2]) for w in W)[n]
        got = "E" in RS.roster(S, spec)
        if got != want: return "E seated %s, want %s" % (got, want)
    base = run(spec, [(n, rows) for n, rows, _ in W], pl)
    with seat_mut("leaving_unread"):
        m = run(spec, [(n, rows) for n, rows, _ in W], pl, orders=False)
    return [result(inst, "a key's leaving binds by the version's past: a version with it there does not count that key; one without it still does",
                   "KERNEL.md 6, 7; RosterHead.lean leaving_binds_by_past", verdict_of(base), base,
                   "members read at the heads only (the leaving in the version's past unread)", m)]


# =================================================================================================================
TASKS = {
    "madeup": lambda I: check_madeup(I),
    "community_spent": lambda I: spent_room(I),
    "self": lambda I: check_keys(I["self"], "self roster (a person's keys)"),
    "voice": lambda I: check_keys(I["voice"], "voice (a voice's room keys)") + check_voice_extra(I["voice"], "voice (a voice's room keys)"),
    "community": lambda I: check_room(I["community"], "community (public, members are persons)", False),
    "private": lambda I: check_room(I["community"], "private room (members are voices)", True),
    "accord": lambda I: check_accord(I["accord"], "accord (holders)"),
    "infra": lambda I: check_infra(I["infra"], "infrastructure community (operators' keys)"),
    "key_revocation": lambda I: check_key_revocation(),
    "leaving": lambda I: check_leaving(I["community"], "community (public, members are persons)"),
    "fork_self": lambda I: check_fork("self roster (a person's keys)", "majority", 4, "012", "2"),
    "fork_comm_maj": lambda I: check_fork("community (public, members are persons)", "majority", 5, "0123", "3"),
    "fork_comm_join": lambda I: check_fork("community (public, members are persons)", "majority", 5, "0123", "4"),
    "fork_comm_q": lambda I: check_fork("community (public, members are persons)", "quorum3", 5, "01234", "34"),
    "fork_comm_23": lambda I: check_fork("community (public, members are persons)", "two_thirds", 5, "0123", "3"),
    "fork_accord": lambda I: check_fork("accord (holders)", "majority", 5, "01234", "34"),
    "fork_infra": lambda I: check_fork("infrastructure community (operators' keys)", "quorum2", 4, "012", "2"),
}


def task(name):
    limit()
    t0 = time.time()
    RS.MUT.clear(); RS.PARAMS.clear()
    I = RS.instances()
    out = TASKS[name](I)
    return name, out, round(time.time() - t0, 1)


def main():
    t0 = time.time()
    print("== the five instances, read from the policy table")
    for name, s in RS.instances().items():
        print("  %-10s %s" % (name, s.params()))
        print("             tables: %s; fork run under %s" % (s.tables, RS.fork_protocol(s)))
    with mp.get_context("fork").Pool(3, initializer=limit) as pool:
        done = pool.map(task, list(TASKS), chunksize=1)
    rc = 0
    by_inst = {}
    for name, rows, secs in done:
        for r in rows: by_inst.setdefault(r["instance"], []).append(r)
    for inst, rows in by_inst.items():
        print("\n== %s" % inst)
        for r in rows:
            mut = "" if r["mutation"] is None else ("  mutation [%s] %s" % (r["mutation"], "caught" if r["caught"] else "NOT CAUGHT"))
            print("  %-22s %s" % (r["verdict"], r["property"]))
            print("      %d worlds, %d orders%s" % (r["worlds"], r["orders"], mut))
            if r["base_fails"]: print("      witness: %s" % (r["base_fails"][:1],))
            if r["order_differs"]: print("      ORDER DIFFERS: %s" % r["order_differs"])
            if r["mut_witness"] and r["caught"]: print("      mutation witness: %s" % (r["mut_witness"][0],))
            if r["extra"]: print("      note: %s" % r["extra"])
            if r["mutation"] is not None and not r["caught"]: rc = 1
            if r["verdict"] == "PLANT NOT CAUGHT": rc = 1
            if r["order_differs"]: rc = 1
    got = sorted("%s\t%s\t%s" % (i, r["property"], r["verdict"]) for i, rows in by_inst.items() for r in rows)
    exp_path = os.path.join(HERE, "roster_expected.tsv")
    if "--write" in sys.argv:
        open(exp_path, "w", encoding="utf-8").write("instance\tproperty\tverdict\n" + "\n".join(got) + "\n")
    want = open(exp_path, encoding="utf-8").read().splitlines()[1:]
    if got != want:
        rc = 1
        print("\nVERDICTS DIFFER from roster_expected.tsv: %s" % sorted(set(got) ^ set(want))[:6])
    print("\n%d properties, verdicts as recorded: %s" % (len(got), got == want))
    return rc


if __name__ == "__main__":
    sys.exit(main())
