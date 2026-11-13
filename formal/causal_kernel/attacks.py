"""
attacks.py: the thirty-three tests of the prior-art attack list, and a thirty-fourth found by the proof of the checkpoint, run against the kernel modules in this folder
(seat.py, window.py, route.py, checkpoint.py, cut.py, causal_kernel.py) and formal/roster_fork.

Each test builds the smallest world that expresses the attack, runs it in every arrival order (all of them up to
seven rows, a fixed sample of 1,000 above that, and once more with every row offered twice), and returns one record:

    cls       HOLDS | BROKEN | CONCEDED | NOT EXPRESSIBLE
    who       who can do it
    witness   the rows, who signed them, what each party concludes
    protects  what protects (HOLDS), what is conceded and where it is said (CONCEDED), what is missing (NOT EXPRESSIBLE)
    facts     every observation the class rests on, as (text, value). A fact that is False fails check_attacks.py.

Run: python3 -I formal/causal_kernel/check_attacks.py
"""
import itertools
import os
import random
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "formal", "roster_fork"))
sys.dont_write_bytecode = True
import seat as ST          # noqa: E402
import window as WN        # noqa: E402
import route as RT         # noqa: E402
import checkpoint as CP    # noqa: E402
import fork as FK          # noqa: E402

CK, CUT, K, R = ST.CK, ST.CUT, ST.K, ST.R
TESTS = []
COUNT = {"orders": 0, "differ": 0, "scenarios": 0}
SEAT = lambda r, P, past: ST.seat_rule(r, P, past)
WIN = lambda r, P, past: WN.rule(r, P, past)
ROUTE = lambda r, P, past: RT.rule(r, P, past)


def test(n, name, source, prop):
    def deco(f):
        TESTS.append((n, name, source, prop, f))
        return f
    return deco


def conc(rows, rule):
    return CK.concluded(CK.kept(list(rows)), rule)


def free(rows, rule, answer, cap=1000):
    """The answer over the set, and whether every arrival order (and a replay of every row) gives it."""
    rows = list(rows)
    memo = {}
    def mrule(r, P, past):
        key = (r["id"], frozenset(q["id"] for q in P))
        if key not in memo: memo[key] = rule(r, P, past)
        return memo[key]
    ref = answer(conc(rows, mrule))
    if len(rows) <= 7:
        orders = itertools.permutations(rows)
    else:
        rnd = random.Random(len(rows) * 7919 + 1)
        orders = [list(reversed(rows))] + [rnd.sample(rows, len(rows)) for _ in range(cap - 1)]
    seen = {}
    bad = n = 0
    for o in orders:
        S = CK.arrive(o, mrule)
        key = tuple(r["id"] for r in S.rows)
        if key not in seen: seen[key] = answer(S)
        n += 1; bad += seen[key] != ref
    bad += answer(CK.arrive(rows + list(reversed(rows)), mrule)) != ref          # every row offered twice
    COUNT["orders"] += n + 1; COUNT["differ"] += bad; COUNT["scenarios"] += 1
    return ref, bad


def seat_ans(S):
    Q = ST.Seats(S)
    return (Q.snapshot(), frozenset(Q.cut.all().items()))


def roster(rows, rule=ROUTE, scope="member", obj="g", check=True):
    ans = lambda S: (ST.Seats(S).holders(scope, obj), frozenset(CUT.Cut(S).all().items()))
    if check:
        ref, bad = free(rows, rule, ans)
        return ref[0], dict(ref[1]), bad
    r = ans(conc(rows, rule))
    return r[0], dict(r[1]), 0


def win(rows, pid="p", **kw):
    ref, bad = free(rows, WIN, lambda S: tuple(sorted(WN.outcomes(S, pid, **kw).items())))
    return dict(ref), bad


def cp_versions(W, S, ack=None, group=False):
    """checkpoint.versions over a roster_fork world: (certain, possible, the roster common to the certain tips)."""
    vs = W.vs
    T, U = CP.versions(sorted(S), {i: vs[i]["E"] for i in S}, {i: vs[i]["past"] for i in S}, W.valid, ack, group)
    r = W.ALL
    for t in FK.tips_of(W, S, sorted(T)): r &= vs[t]["R"]
    return T, U, r


def next_counted():
    """One more counted row of the room after C's removal: A and B admit E, counted over the removal."""
    cE = in_room(ST.cosign("cE", "B", "wE", ("x",)))
    aE = in_room(ST.accept("aE", "E", None, ("x",), scope="member", obj="g"))
    return [cE, aE, ST.offer("wE", "A", "E", "member", "g", "group", ("x", "aE", "cE"), head=("x",), policy="community_invite", content="wE", room="g")]


def forged_line(n, head):
    """n counted rows by seated A with removed C's voice: the first removes B counted over `head`, each next admits a
    key of theirs counted over the one before."""
    zc = in_room(ST.cosign("zc", "C", "z1", (head,)))
    rows = [zc, ST.unseat("z1", "A", "B", "member", "g", "group", (head, "zc"), head=(head,), policy="community_remove", content="z1", room="g")]
    for i in range(2, n + 1):
        k, prev = "F%d" % i, "z%d" % (i - 1)
        c = in_room(ST.cosign("z%dc" % i, "C", "z%d" % i, (prev,)))
        a = in_room(ST.accept("a%s" % k, k, None, ("g",), scope="member", obj="g"))
        rows += [c, a, ST.offer("z%d" % i, "A", k, "member", "g", "group", (prev, c["id"], a["id"]), head=(prev,), policy="community_invite", content="z%d" % i, room="g")]
    return rows


def reader_view(rows, own=None, checkpoint=False):
    """(members, stale, tips) for a reader, in every arrival order."""
    def ans(S):
        Q = ST.Seats(S, own=own, checkpoint=checkpoint)
        return Q.holders("member", "g"), Q.stale, frozenset(x["id"] for x in Q.tips("g"))
    return free(rows, ROUTE, ans)


def acked(head):
    """Reader B's acknowledgement of a head: a message at that head, and B's ack of it."""
    return [RT.msg("mm", "A", "g", (head,)), RT.ack("kk", "B", "g", "mm", (head,))]


class Rec:
    def __init__(self):
        self.facts, self.bad, self.notes = [], 0, []
    def fact(self, text, value=True):
        self.facts.append((text, value))
        return value
    def note(self, text):
        self.notes.append(text)
    def order(self, bad):
        self.bad += bad


def room_rows(*ids):
    by = {r["id"]: r for r in RT.world()}
    return [by[i] for i in ids]


ROOM = ("g", "md", "ac", "cb", "w", "m2", "xc", "x")       # A and B found g; C is admitted (w) and removed (x)
in_room = lambda r: dict(r, room="g")
fs = lambda s: "{" + ",".join(sorted(s)) + "}"


# =========================================================================================================
# A. Backdating and late rows
# =========================================================================================================
@test(1, "Backdated act by a removed key", "Jacob and Hartenstein Fig. 6c; Matrix soft failure; local-first-auth #32",
      "A row a removed key signs after its removal, naming only older rows, never counts for anything.")
def t01(t):
    base = room_rows(*ROOM)
    m4 = RT.msg("m4", "C", "g", ("w",))
    m4b = RT.msg("m4b", "C", "g", ("w",), names=("m4",))
    m4c = RT.msg("m4c", "C", "g", ("w",), names=("m4b",))
    mem, st, bad = roster(base + [m4, m4b, m4c]); t.order(bad)
    t.fact("message rows: three rows by removed C naming only the head before its removal are all void", all(st[i] == "void" for i in ("m4", "m4b", "m4c")))
    t.note("honest twin: the same three rows signed offline in good faith are the same rows; 3 of 3 are void, as every row is that the removal's past had not named (cut.py: the price)")
    title, cases = WN.moderation_world()
    fb = cases[5][1]                                                    # absent moderator: the members' majority landed the fallback
    um = ST.withdraw("um", "m1", "md", ("L",))                         # the appointment is then withdrawn by its conferrer, naming the landing
    A = WN.answer("A", "MOD", "p", "answered")                          # the former moderator answers, naming only the opener
    o1, bad = win(fb + [um, A]); t.order(bad)
    t.fact("moderation fallback landed, the moderator's appointment withdrawn after it, then the former moderator answers naming only the opener: recount=%s (rule ii contest=%s)"
           % (o1["recount"], o1["contest"]), o1["recount"] == "fallback")
    Ain = WN.answer("A", "MOD", "p", "answered")
    o2, bad = win(fb[:-1] + [Ain, dict(um, names=("md", "A"), target="md"), fb[-1]]); t.order(bad)
    t.fact("contrast: an answer the withdrawal has in its past is still counted: recount=%s" % o2["recount"], o2["recount"] == "contested")
    g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
    W = WN.secs("halt_fuse")
    p = WN.opener("p", "h1", "halt_fuse", "g", ("g",))
    rows = [g, p, WN.receipt("r", "h3", "p", 0), WN.landing("L", "h3", "p", "r", "lapsed", W),
            ST.cosign("xc", "h3", "xh", ("g", "L")),
            ST.unseat("xh", "h1", "h2", "holder", "g", "group", ("L", "xc"), head=("g",), policy="accord_majority", content="xh", counted="holder")]
    o1, bad = win(rows + [WN.answer("c2", "h2", "p", "confirm")]); t.order(bad)
    t.fact("halt lapsed, holder h2 removed by the other two, then h2 signs 'confirm' naming only the opener: recount=%s" % o1["recount"], o1["recount"] == "lapsed")
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a key removed, or whose grant was withdrawn, at any later time",
                witness="g(m1,m2,m3) md(m1 appoints MOD) p x1,x3 L(m2 lands 'fallback') um(m1 withdraws md, naming L) A(MOD: 'answered', naming only p). The outcome of p stays fallback for every reader in every order.",
                protects="cut.py for rows on the removed key's own slots (concurrent with a counting cut is void). window.py for answers: under recount a row of a key whose seat was ended is counted only if the ending row has it in its past. "
                         "The price is the cut's: an honest row signed offline and not yet named when the removal was signed is void too.",
                fix="")


@test(2, "Backdated act by a key still seated (accomplice names the removed key's rows)", "Jacob and Hartenstein; Matrix; local-first-auth #32",
      "Only the removal's own sealed ancestry decides which of the removed key's rows count; no later row can add to it.")
def t02(t):
    base = room_rows(*ROOM)
    m4 = RT.msg("m4", "C", "g", ("w",))                                       # backdated by C
    kB = RT.ack("kB", "B", "g", "m4", ("w",))                                 # the accomplice acknowledges it, naming the old head
    mem, st, bad = roster(base + [m4, kB]); t.order(bad)
    t.fact("accomplice's acknowledgement naming the backdated row: m4 is %s" % st["m4"], st["m4"] == "void")
    xc2 = in_room(ST.cosign("xc2", "B", "x2", ("x", "kB")))
    x2 = ST.unseat("x2", "A", "C", "member", "g", "group", ("x", "kB", "xc2"), head=("x",), policy="community_remove", content="x2", room="g")
    mem, st, bad = roster(base + [m4, kB, xc2, x2]); t.order(bad)
    t.fact("a later removal row naming both the removal and the acknowledgement: concluded, m4 is still %s, roster %s" % (st["m4"], fs(mem)), st["m4"] == "void" and "C" not in mem)
    xcp = in_room(ST.cosign("xcp", "B", "x", ("w", "m4")))                   # a second cosignature of the SAME removal content, naming m4
    xp = ST.unseat("xp", "A", "C", "member", "g", "group", ("w", "xcp", "m2"), head=("w",), policy="community_remove", content="x", room="g")
    mem, st, bad = roster(base + [m4, xcp, xp]); t.order(bad)
    t.fact("a second removal of the same key that does name m4, beside the first: both count (%s, %s), m4 is %s" % (st["x"], st["xp"], st["m4"]),
           st["x"] == "counts" and st["m4"] == "void")
    # the honest pre-seal: the removal's own cosignature named the row before the removal was signed
    by = {r["id"]: r for r in RT.world()}
    xcs = dict(by["xc"], names=("w", "m4"))
    mem, st, bad = roster(room_rows("g", "md", "ac", "cb", "w", "m2") + [m4, xcs, by["x"]]); t.order(bad)
    t.fact("contrast: when the removal's own ancestry names m4 (through its cosignature), m4 %s" % st["m4"], st["m4"] == "counts")
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a seated accomplice of the removed key; also the proposer of the removal",
                witness="m4(C, naming only the head before x) kB(B acknowledges m4) x2(A+B: a second removal naming x and kB). m4 stays void for every reader in every order.",
                protects="Derived layer, cut.py: a row concurrent with a counting cut on its slot is void; concurrency with a kept row never changes, so nothing signed later moves it. "
                         "A second removal that does name the row does not help, since the first still counts.",
                fix="")


@test(3, "Backdated conferral chain", "local-first-auth #32; Keyhive G1; p2panda-auth",
      "A key that has been removed cannot seat a new key, alone or with an old voice, and what happens to seats it conferred earlier is one stated answer.")
def t03(t):
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    d = ST.offer("d", "f1", "K", "moderate", "g", "seat", ("g",), under="g", sub=True)
    ak = ST.accept("ak", "K", "d")
    c3 = ST.cosign("c3", "f3", "xf", ("g",))
    xf = ST.unseat("xf", "f2", "f1", "founder", "g", "group", ("g", "c3"), head=("g",), policy="community_remove", content="xf", counted="founder")
    xf_after = dict(xf, names=("g", "c3", "ak"))
    for label, rows in (("offer made before the removal and named by it", [g, d, ak, c3, xf_after]), ("offer backdated, concurrent with the removal", [g, d, ak, c3, xf])):
        ref, bad = free(rows, SEAT, lambda S: ST.Seats(S).stands("K", "moderate", "g")); t.order(bad)
        t.fact("conferrer=seat, %s: K holds moderate = %s (the seat falls with its conferrer)" % (label, ref), ref is False)
    base = room_rows(*ROOM)
    mem, st, bad = roster(base); t.order(bad)
    t.fact("conferrer=group: nothing falls when a voice of an earlier count is later removed (roster %s after C's removal)" % fs(mem), mem == {"A", "B"})
    aD = in_room(ST.accept("aD", "D", None, ("g",), scope="member", obj="g"))
    cC = in_room(ST.cosign("cC", "C", "wD", ("w",)))
    wD = ST.offer("wD", "A", "D", "member", "g", "group", ("w", "aD", "cC"), head=("w",), policy="community_invite", content="wD", room="g")
    mem, st, bad = roster(base + [aD, cC, wD]); t.order(bad)
    t.fact("after C's removal, A and removed C (two of three at the old head) sign an admission of D on that head: the row %s, and the two versions of the head wait: roster %s" % (st["wD"], fs(mem)), mem == {"A", "B"})
    (m0, st0, tp0), bad = reader_view(base + [aD, cC, wD] + next_counted()); t.order(bad)
    (m1, st1, tp1), bad = reader_view(base + [aD, cC, wD] + next_counted() + acked("wE"), own="B"); t.order(bad)
    t.fact("after one more counted row on the removal (A and B admit E): for a reader that acknowledged it the old-head admission is behind its line (void: %s) and the roster is %s; "
           "for a reader with no acknowledgement it is still a waiting tip: D is never listed, and neither is E (roster %s)" % ("wD" in st1, fs(m1), fs(m0)),
           "wD" in st1 and m1 == {"A", "B", "E"} and m0 == {"A", "B"} and "D" not in m0)
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="one seated key together with one removed key that met the count at the head the removal was counted over",
                witness="x(A+B remove C at head w) cC(C cosigns 'admit D', naming w) wD(A admits D at head w, naming cC). wD concludes; D is not listed for any reader: the tips wait. A reader that acknowledges a later counted row has wD behind its line.",
                protects="seat.py tips (KERNEL 7): two counted acts on one head wait and the roster is the keys common to them. The pair cannot seat D. What it can do is keep a tip waiting, which holds later admissions out "
                         "for a reader with no acknowledgement until a counted row names both: that harm is test 4's and test 16's, and is conceded there. "
                         "Stated cells: conferrer=seat falls with its conferrer; conferrer=group stays; a `self` offer by a founding signer falls with that signer's founding seat.",
                fix="")


@test(4, "State reset by an old fork", "Matrix state resolution v1; CVE-2025-49090",
      "A branch from an old head, offered late, changes a derived answer only through a row whose signer has standing on that answer's slot, and the reader can be shown which row.")
def t04(t):
    base = room_rows(*ROOM)
    before, st0, _ = roster(base, check=False)
    late = {
        "an outsider (unseat of B, conferred self)": [ST.unseat("z", "X", "B", "member", "g", "self", ("g",), room="g")],
        "an outsider (unseat of B, counted, one voice)": [ST.unseat("z", "X", "B", "member", "g", "group", ("w",), head=("w",), policy="community_remove", content="z", room="g")],
        "removed C alone (counted unseat of B at the old head)": [ST.unseat("z", "C", "B", "member", "g", "group", ("w",), head=("w",), policy="community_remove", content="z", room="g")],
        "removed C alone (withdraws B's founding seat)": [in_room(ST.withdraw("z", "C", "g"))],
        "seated A alone (counted unseat of B at the old head)": [ST.unseat("z", "A", "B", "member", "g", "group", ("w",), head=("w",), policy="community_remove", content="z", room="g")],
        "seated A alone (a `self` unseat of B: A signed the founding row)": [ST.unseat("z", "A", "B", "member", "g", "self", ("g",), room="g")],
        "seated A with removed C's cosignature (two of three at the old head)": [
            in_room(ST.cosign("zc", "C", "z", ("w",))),
            ST.unseat("z", "A", "B", "member", "g", "group", ("w", "zc"), head=("w",), policy="community_remove", content="z", room="g")],
    }
    moved = {}
    for who, rows in late.items():
        mem, st, bad = roster(base + rows); t.order(bad)
        moved[who] = mem != before
        t.note("%s: roster %s -> %s" % (who, fs(before), fs(mem)))
    t.fact("no late row by an outsider, by the removed key alone or by one seated key alone moves the roster", not any(v for k, v in moved.items() if "cosignature" not in k))
    key = "seated A with removed C's cosignature (two of three at the old head)"
    gain = t.fact("a seated key with the removed key's old voice signs a removal of B on the head the newest counted row is itself counted over: B is unlisted while the tips wait", moved[key])
    (m0, st0, tp0), bad = reader_view(base + next_counted() + late[key]); t.order(bad)
    (m1, st1, tp1), bad = reader_view(base + next_counted() + acked("wE") + late[key], own="B"); t.order(bad)
    bound = t.fact("the same rows once the room has a counted row on a newer head: a reader that acknowledged it is not moved (roster %s, the forged row void); a reader with no acknowledgement still sees two tips (roster %s)"
                   % (fs(m1), fs(m0)), m1 == {"A", "B", "E"} and "z" in st1 and m0 == {"A"})
    for n in (1, 2, 3):
        (ma, sa, ta), bad = reader_view(base + forged_line(n, "w")); t.order(bad)
        (mb, sb, tb), bad = reader_view(base + acked("x") + forged_line(n, "w"), own="B"); t.order(bad)
        t.fact("%d forged row%s from the head the newest honest row is counted over: no acknowledgement: %d tips, members %s, nothing stale; a reader that acknowledged the honest row: %d tips, members %s. The removed key is never listed"
               % (n, "" if n == 1 else "s, each counted over the one before,", len(ta), fs(ma), len(tb), fs(mb)), ma == mb == {"A"} and len(ta) == len(tb) == 2 and not sa and not sb)
    (mc, sc, tc), bad = reader_view(base + forged_line(2, "w"), checkpoint=True); t.order(bad)
    t.fact("WHY THE GROUP CHECKPOINT IS OFF: with Seats(..., checkpoint=True) the two forged rows are one row deeper than the honest line and leave the honest removal behind (stale: %s): members %s, the removed key listed again"
           % (",".join(sorted(sc)), fs(mc)), "x" in sc and "C" in mc and "B" not in mc)
    return dict(cls="CONCEDED" if gain and bound else "BROKEN" if gain else "HOLDS", who="keys that met the count at any past head: here one seated key and one removed key; against a reader whose own acknowledged line does not leave that head behind",
                witness="zc(C, removed, cosigns 'remove B', naming head w) z(A removes B at head w). Two tips; the roster is the common {A}; B is unlisted, for a reader with no acknowledgement wherever the honest line has got to.",
                protects="KERNEL 7: 'An adversary holding the count of an old head signs a valid version alone.' Below that count nothing moves. The forged row is one more tip: the roster is the keys common to the tips, "
                         "so the forger unlists members and never lists anyone, however many rows it signs; a removed key is never back. It lasts until a counted row names both tips, counted over the keys common to them, "
                         "and here that is the hostile key alone: the honest members cannot end it by signing. A reader is safe from it exactly when it has acknowledged an honest row counted over a head newer than the one forged from; "
                         "from the head the newest honest row is itself counted over, no acknowledgement helps until the honest line has one more counted row. No answer of the kernel reports which row moved a derived answer.",
                fix="")


@test(5, "Rollback by re-sync (intermediate answers)", "Matrix: manipulation of the federation re-sync mechanism",
      "A node that is offered true rows in an order chosen by an adversary never acts on an answer the full set does not give.")
def t05(t):
    rows = RT.world()
    S = conc(rows, ROUTE)
    final = ST.Seats(S).holders("member", "g")
    aud = RT.audience(S)
    rnd = random.Random(5)
    orders = [rows, list(reversed(rows))] + [rnd.sample(rows, len(rows)) for _ in range(40)]
    orders.append(sorted(rows, key=lambda r: r["id"] in ("x", "xc", "m5", "k4")))      # the adversary's order: the removal last
    pre = wrong = leak = 0
    for o in orders:
        for n in range(1, len(o)):
            Sp = CK.arrive(o[:n], ROUTE)
            pre += 1
            if not ST.Seats(Sp).holders("member", "g") <= final: wrong += 1
            rt = RT.route_sets(Sp)
            leak += any(i for p, ids in rt.items() for i in ids if p not in aud[i])
    COUNT["orders"] += len(orders)
    t.fact("of %d prefixes of %d arrival orders, %d give a roster listing a key the full set does not list (C, before the removal is offered)" % (pre, len(orders), wrong), wrong > 0)
    t.fact("in none of them is a row routed to a party outside the audience the full set gives that row (the audience only grows with rows): %d" % leak, leak == 0)
    return dict(cls="CONCEDED", who="whoever chooses what a returning node is offered first (a relay); no key is needed",
                witness="A node offered g,ac,cb,w and C's rows but not x lists C, answers `may C post` yes and owes C the next key. The removal is a true row it was not yet offered.",
                protects="KERNEL 3: 'Only the first two layers are final. A derived answer can be changed by a later row'. KERNEL 8: 'No finality across readers.' "
                         "What holds: kept and concluded never roll back, and no prefix routes a row outside its final audience. What does not: every derived answer (roster, may, owed) at a prefix. "
                         "In practice: free for a relay, lasts until the withheld row is delivered, and an emission (a wrap, a served row) cannot be unsent. Nodes recover the answer, not the emission.",
                fix="")


@test(6, "Hotel California (leave, join, leave across branches)", "Matrix state resolution",
      "A key that left or was removed is back in only by a fresh act of the conferrer and its own fresh acceptance; one answer in every order.")
def t06(t):
    g = ST.offer("g", "A", "A", "founder", "@", "self")
    o1 = ST.offer("o1", "A", "K", "moderate", "g", "seat", ("g",), under="g")
    a1 = ST.accept("a1", "K", "o1")
    wd1 = ST.withdraw("wd1", "K", "a1")                                         # leave
    o2 = ST.offer("o2", "A", "K", "moderate", "g", "seat", ("wd1",), under="g")
    a2 = ST.accept("a2", "K", "o2")                                             # join again
    wd3 = ST.withdraw("wd3", "K", "o1")                                         # leave, on the old branch: names only the first offer
    ans = lambda S: ST.Seats(S).stands("K", "moderate", "g")
    ref, bad = free([g, o1, a1, wd1, o2, a2, wd3], SEAT, ans); t.order(bad)
    t.fact("leave, join, then a leave that names only the first offer: K is in = %s (a withdrawal ends the offer it names and no other)" % ref, ref is True)
    ref, bad = free([g, o1, a1, wd1, o2, a2, wd3, ST.withdraw("wd4", "K", "a2")], SEAT, ans); t.order(bad)
    t.fact("with a leave that names the second acceptance: K is in = %s" % ref, ref is False)
    ref, bad = free([g, o1, a1, wd1, ST.offer("o3", "A", "K", "moderate", "g", "seat", ("wd1",), under="g", consent="one")], SEAT, ans); t.order(bad)
    t.fact("the conferrer cannot put a key that left back in without its acceptance, even claiming single consent: %s" % ref, ref is False)
    base = room_rows(*ROOM)
    ac2 = in_room(ST.accept("ac2", "C", None, ("x",), scope="member", obj="g"))
    w2 = ST.offer("w2", "A", "C", "member", "g", "group", ("x", "ac2", "cb"), head=("x",), policy="community_invite", content="w", room="g")
    mem, st, bad = roster(base + [ac2, w2]); t.order(bad)
    t.fact("replay: after the removal, A alone signs a new admission of C at the current head, naming the cosignature B gave at head g for the first admission: the row %s, roster %s" % (st["w2"], fs(mem)), "C" not in mem)
    cb2 = in_room(ST.cosign("cb2", "B", "w", ("x",)))
    mem, st, bad = roster(base + [ac2, cb2, dict(w2, names=("x", "ac2", "cb2"))]); t.order(bad)
    t.fact("with a fresh cosignature by B that names the current head, C is re-admitted: roster %s" % fs(mem), "C" in mem)
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="one seated member and the removed key",
                witness="cb(B cosigns content 'w' at head g) w x ac2(C accepts again) w2(A: admit C at head x, naming cb). w2 concludes nothing: cb does not name the head w2 is counted over.",
                protects="seat.py: a withdrawal names the one offer or acceptance it ends; a seat needs a live offer with a live acceptance; a cosignature is a voice only for a row counted over a head the cosignature itself names. "
                         "(A build must also make `content` the digest of the act's fields; here it is a free label.)",
                fix="")


@test(7, "Superseded grant on a fork", "Matrix state resolution, cause 1",
      "When a conferrer's seat is cut, what it conferred, and what its holders conferred, ends with it in every order.")
def t07(t):
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    d = ST.offer("d", "f1", "K", "moderate", "g", "seat", ("g",), under="g", sub=True)
    ak = ST.accept("ak", "K", "d")
    d2 = ST.offer("d2", "K", "J", "moderate:spam", "g", "seat", ("ak",), under="d", cosigners=("J",))
    c3 = ST.cosign("c3", "f3", "xf", ("g",))
    xf = ST.unseat("xf", "f2", "f1", "founder", "g", "group", ("g", "c3"), head=("g",), policy="community_remove", content="xf", counted="founder")
    ans = lambda S: tuple(ST.Seats(S).stands(k, s, "g") for k, s in (("f1", "founder"), ("K", "moderate"), ("J", "moderate:spam")))
    ref, bad = free([g, d, ak, d2], SEAT, ans); t.order(bad)
    t.fact("before the cut: f1, K, J stand = %s" % (ref,), ref == (True, True, True))
    ref, bad = free([g, d, ak, d2, c3, xf], SEAT, ans); t.order(bad)
    t.fact("A seats B, B seats C, concurrently A's seat is cut (conferrer=seat), all 720 orders: f1, K, J stand = %s" % (ref,), ref == (False, False, False))
    cr = ST.cosign("cr", "f3", "g2", ("g", "xf"))
    g2 = ST.offer("g2", "f2", "f1", "founder", "g", "group", ("xf", "cr"), head=("g",), policy="community_invite", content="g2", counted="founder", cosigners=("f1",))
    ref, bad = free([g, d, ak, d2, c3, xf, cr, g2], SEAT, ans); t.order(bad)
    t.fact("f1 re-admitted by the count: f1 stands and the old grants do not revive = %s" % (ref,), ref == (True, False, False))
    ds = ST.offer("ds", "f1", "K", "moderate", "g", "self", ("g",), sub=True)
    aks = ST.accept("aks", "K", "ds")
    ds2 = ST.offer("ds2", "K", "J", "moderate:spam", "g", "seat", ("aks",), under="ds", cosigners=("J",))
    ref, bad = free([g, ds, aks, ds2], SEAT, ans); t.order(bad)
    t.fact("the same chain with the first grant marked conferrer=self, while f1 is a founder: %s" % (ref,), ref == (True, True, True))
    ref, bad = free([g, ds, aks, ds2, c3, xf], SEAT, ans); t.order(bad)
    t.fact("and after f1's removal, in every order: %s (a founding signer's own offer stands on its founding seat)" % (ref,), ref == (False, False, False))
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a founding signer about to be removed, or already removed",
                witness="g(f1,f2,f3 found) ds(f1 -> K moderate, conferrer=self) aks ds2(K -> J) xf(f2+f3 remove f1). f1, K and J are all out, for every reader, in every order.",
                protects="seat.py: the walk is run again on every read; a seat conferred under another falls with it, and a `self` offer over a founding row that seats several keys is live only while its signer's own founding seat is. "
                         "A re-admitted conferrer does not revive old grants.",
                fix="")


@test(8, "A row naming disparate parts of the graph", "Matrix state resolution",
      "A row that happens to name both sides of a contest decides it only if its signer has standing on that slot.")
def t08(t):
    import check_cut as CC
    G = R("g", "genesis", "admin", members=("admin", "co", "m", "u"))
    a = R("a", "claim", "m", ("g",), slot="s")
    b = R("b", "claim", "u", ("g",), slot="s")
    hold = lambda S: CUT.Cut(S).holder("s")
    ref, bad = free([G, a, b], CC.rule, hold); t.order(bad)
    t.fact("two concurrent claims: the slot is %s" % ref, ref == "conflict")
    for label, row in (("a reply by a member naming both", R("n", "note", "co", ("a", "b"))),
                       ("a reply by an outsider naming both", R("n", "note", "X", ("a", "b"))),
                       ("a reply naming the genesis and both (old and new)", R("n", "note", "co", ("g", "a", "b"))),
                       ("a deciding row by a claimant, who is not a key that may decide", R("n", "decider", "m", ("a", "b"), slot="s", picks="a")),
                       ("a deciding row by an outsider", R("n", "decider", "X", ("a", "b"), slot="s", picks="a"))):
        ref, bad = free([G, a, b, row], CC.rule, hold); t.order(bad)
        t.fact("%s: the slot is %s" % (label, ref), ref == "conflict")
    ref, bad = free([G, a, b, R("c", "decider", "admin", ("a", "b"), slot="s", picks="a")], CC.rule, hold); t.order(bad)
    t.fact("a deciding row by a key that may decide: %s" % ref, ref == "a")
    ref, bad = free([G, a, b, R("a3", "claim", "m", ("a", "b"), slot="s")], CC.rule, hold); t.order(bad)
    t.note("a claimant's own NEW CLAIM naming both claims takes the slot (%s): among keys entitled to claim, the last to name the other holds it, and the other can do the same back" % ref)
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="any key, with or without standing",
                witness="a(m claims s) b(u claims s) n(a reply naming a and b, or a deciding row by a key that may not decide). The slot stays in conflict.",
                protects="The slot rule reads only rows on the slot (cut.holder, causal_kernel.slot), and a deciding row concludes only for a key that may decide (the conclusion rule). "
                         "Stated limit: a key entitled to claim the slot wins it by claiming again and naming its rival, and so can the rival; that is KERNEL 3 (changed 'only by a row whose signer has standing on that answer's slot').",
                fix="")


# =========================================================================================================
# B. Windows and clocks
# =========================================================================================================
def window_bases():
    Ws, Wm, Wh = WN.secs("self_roster_evict"), WN.secs("moderation_fallback"), WN.secs("halt_fuse")
    gs = ST.offer("g", "d1", ("d1", "d2", "d3"), "self", "@", "self", cosigners=("d2", "d3"))
    gm = ST.offer("g", "m1", ("m1", "m2", "m3"), "member", "@", "self", cosigners=("m2", "m3"))
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "self", ("g",), cosigners=("MOD",))
    gh = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
    pm = WN.opener("p", "m2", "moderation_fallback", "g", ("md",))
    return {
        "self roster: d1 alone evicts d2 (silent 24 h)": (
            [gs, WN.opener("p", "d1", "self_roster_evict", "g", ("g",), target="d2"), WN.receipt("r", "d1", "p", 0), WN.landing("L", "d1", "p", "r", "landed", Ws)],
            {"d2 (the evicted key) signs any row": R("n", "note", "d2", ("g",)), "d3 objects": WN.answer("n", "d3", "p", "object")}, "refused", "d3"),
        "self roster: d1 and d2 evict d3 at once (count)": (
            [gs, WN.opener("p", "d1", "self_roster_evict", "g", ("g",), target="d3"), WN.answer("a2", "d2", "p", "approve"), WN.receipt("r", "d1", "p", 0),
             WN.landing("L", "d1", "p", "r", "landed", 0, ("a2",))],
            {"d3 objects": WN.answer("n", "d3", "p", "object"), "d3 signs any row": R("n", "note", "d3", ("g",))}, None, "d2"),
        "moderation: members' fallback after 48 h": (
            [gm, md, pm, WN.receipt("r", "m2", "p", 0), WN.answer("x1", "m1", "p", "act"), WN.answer("x3", "m3", "p", "act"),
             WN.landing("L", "m2", "p", "r", "fallback", Wm, ("x1", "x3"))],
            {"the moderator answers": WN.answer("n", "MOD", "p", "answered")}, "answered", "m1"),
        "halt: lapsed at the fuse": (
            [gh, WN.opener("p", "h1", "halt_fuse", "g", ("g",)), WN.receipt("r", "h3", "p", 0), WN.landing("L", "h3", "p", "r", "lapsed", Wh)],
            {"a second holder confirms": WN.answer("n", "h2", "p", "confirm"), "the halting holder confirms again": WN.answer("n", "h1", "p", "confirm")}, "confirmed", "h2"),
        "halt: confirmed by a majority": (
            [gh, WN.opener("p", "h1", "halt_fuse", "g", ("g",)), WN.answer("c2", "h2", "p", "confirm"), WN.receipt("r", "h2", "p", 0),
             WN.landing("L", "h2", "p", "r", "confirmed", 0, ("c2",))],
            {"h3 signs anything": R("n", "note", "h3", ("g",))}, None, "h2"),
    }


@test(9, "Perpetual reopening of a landed window", "KERNEL 5; did:plc; KERI",
      "Once a window has landed and others have acted on the outcome, no later row flips it.")
def t09(t):
    flips = []
    for name, (rows, lates, flipped_to, lander) in window_bases().items():
        o0, bad = win(rows); t.order(bad)
        for who, late in lates.items():
            o1, bad = win(rows + [late]); t.order(bad)
            line = "%s; a year later %s, naming only old rows: void=%s contest=%s recount=%s" % (name, who, o1["void"], o1["contest"], o1["recount"])
            if o1["recount"] != o0["recount"]:
                r2 = WN.receipt("r2", lander, "p", 0)
                L2 = WN.landing("L2", lander, "p", "r2", flipped_to, 10 ** 7, ("L", "n"))
                o2, bad = win(rows + [late, r2, L2]); t.order(bad)
                line += "; then a landing naming both: recount=%s" % o2["recount"]
                flips.append((name, who, o2["recount"]))
            t.note(line)
    t.fact("every lone landing of the three windows is flipped by one late row under recount: %d flips" % len(flips), len(flips) == 3)
    t.fact("no landing with a count behind it is flipped (quorum_closed_final)", not any("count" in n or "majority" in n for n, _, _ in flips))
    t.fact("each flip ends, once a landing names both, at the opposite outcome: %s" % ", ".join(o for _, _, o in flips), [o for _, _, o in flips] == ["refused", "answered", "confirmed"])
    lapse, lates, _, _ = window_bases()["halt: lapsed at the fuse"]
    c2 = lates["a second holder confirms"]
    k1 = ST.cosign("k1", "h3", "v1", ("g", "L"))
    v1 = ST.offer("v1", "h1", "h4", "holder", "g", "group", ("g", "L", "k1"), head=("g",), policy="accord_majority", content="v1", counted="holder", cosigners=("h4",))
    k2 = ST.cosign("k2", "h3", "v2", ("v1",)); k2b = ST.cosign("k2b", "h4", "v2", ("v1",))
    v2 = ST.offer("v2", "h1", "h5", "holder", "g", "group", ("v1", "k2", "k2b"), head=("v1",), policy="accord_majority", content="v2", counted="holder", cosigners=("h5",))
    o2, bad = win(lapse + [k1, v1, k2, k2b, v2, c2]); t.order(bad)
    o3, bad = win(lapse + [k1, v1, k2, k2b, v2, c2], checkpoint=True); t.order(bad)
    t.fact("counted rows of the ledger do not bound it: after two further counted rows with the landing in their past, the late confirm still reopens the lapse (%s). "
           "With the checkpoint applied to window answers it would not (%s); that is off, because the same rule lets a majority void a minority's timely answer (see the price of the checkpoint)"
           % (o2["recount"], o3["recount"]), (o2["recount"], o3["recount"]) == ("contested", "lapsed"))
    return dict(cls="CONCEDED", who="one key that was counted at the opener's head and still holds its seat: the evicted device itself, the moderator, one further accord holder",
                witness="halt: g(h1,h2,h3) p(h1 halts) L(h3 lands 'lapsed' at the fuse); a year later n(h2 'confirm', naming only p): the lapse is contested, and a landing naming both must say 'confirmed'. "
                        "The same for an eviction (the evicted key signs anything: refused) and the members' fallback (the moderator answers: answered).",
                protects="KERNEL 5: 'What recount costs: a lone landing is never final against a key that can still sign'; causal_order README: 'A key whose answer would move it can unseat the landing at any later time by leaving it unnamed'. "
                         "One signature, no deadline, by a key that was counted at the opener's head and has not been removed since; it lasts until a concluder signs a landing naming both, and that landing must state the flipped outcome. "
                         "No later row of the ledger closes it: the checkpoint is not applied to window answers. "
                         "Agents resumed after a lapsed halt are halted again a year on; an evicted device un-evicts itself; a fallback act is undone. Rule (i) has none of this and lets a thief evict alone; rule (ii) flips the counted landings too.",
                fix="")


@test(10, "Landing over an unacknowledged objection, with an eclipse", "causal_order README; did:plc",
      "An honest concluder kept from seeing an objection does not produce an outcome that stands against it.")
def t10(t):
    title, cases = WN.self_world()
    full = cases[0][1]                                    # the thief's landing; the owner's two objections exist and are unnamed
    seen = [r for r in full if r["id"] not in ("o1", "o2")]
    a, bad = win(seen); t.order(bad)
    b, bad = win(full); t.order(bad)
    t.fact("a reader kept from the objections: recount=%s; a reader with them: recount=%s (void=%s, contest=%s)" % (a["recount"], b["recount"], b["void"], b["contest"]),
           a["recount"] == "landed" and b["recount"] == "contested")
    title, cases = WN.halt_world()
    full = cases[4][1]                                    # honest holder lands the lapse; a relay kept the confirming voice from it
    a, bad = win([r for r in full if r["id"] != "c2"]); t.order(bad)
    b, bad = win(full); t.order(bad)
    c, bad = win(cases[5][1]); t.order(bad)
    t.fact("halt, honest concluder eclipsed: its own view %s, the full view %s, after a landing naming both %s" % (a["recount"], b["recount"], c["recount"]),
           (a["recount"], b["recount"], c["recount"]) == ("lapsed", "contested", "confirmed"))
    return dict(cls="CONCEDED", who="a relay between the objector and the concluder (and its readers) for the length of the window; no key",
                witness="p(h1 halts) c2(h2 confirms, withheld) L(h3, honest, lands 'lapsed'). h3 and every reader without c2: lapsed, and agents resume. Readers with c2: contested.",
                protects="KERNEL 8: 'Nodes may differ while a window is open'; causal_order README: 'A window's length is not in the rows.' Under recount the landing does not stand once the objection is held "
                         "(rule (i) would let it stand for ever). In practice it lasts as long as the eclipse; whatever was done on the outcome meanwhile is done. Recovery: any concluder signs a landing naming both.",
                fix="")


@test(11, "The concluder's clock", "did:plc trusted clock; KERNEL 5",
      "A window that the text gives a length cannot be closed early by the key that concludes it.")
def t11(t):
    Ws, Wh, Wm = WN.secs("self_roster_evict"), WN.secs("halt_fuse"), WN.secs("moderation_fallback")
    gs = ST.offer("g", "d1", ("d1", "d2", "d3"), "self", "@", "self", cosigners=("d2", "d3"))
    p = WN.opener("p", "d3", "self_roster_evict", "g", ("g",), target="d1")
    rows = [gs, p, WN.receipt("r", "d3", "p", 0), WN.landing("L", "d3", "p", "r", "landed", Ws)]          # all three signed in the same second
    o, bad = win(rows); t.order(bad)
    S = conc(rows, WIN)
    t.fact("a thief opens, receipts and lands an eviction in one second, stating instants 24 h apart: landing concluded=%s, recount=%s" % (S.C["L"], o["recount"]),
           S.C["L"] and o["recount"] == "landed")
    o2, bad = win(rows[:3] + [WN.landing("L", "d3", "p", "r", "landed", Ws - 1)]); t.order(bad)
    t.fact("the only check is on the two instants the concluder itself states (one second short: %s)" % o2["recount"], o2["recount"] == "open")
    gh = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
    rows = [gh, WN.opener("p", "h1", "halt_fuse", "g", ("g",)), WN.receipt("r", "h3", "p", -Wh), WN.landing("L", "h3", "p", "r", "lapsed", 0)]
    o, bad = win(rows); t.order(bad)
    t.fact("one hostile holder lapses another holder's halt at once by stating a receipt 24 h in its own past: recount=%s" % o["recount"], o["recount"] == "lapsed")
    o, bad = win(rows + [WN.answer("c1", "h1", "p", "confirm")]); t.order(bad)
    t.fact("the halting holder alone cannot undo that (its confirm is already counted): recount=%s; it takes a second honest holder" % o["recount"], o["recount"] == "lapsed")
    gm = ST.offer("g", "m1", ("m1", "m2", "m3"), "member", "@", "self", cosigners=("m2", "m3"))
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "self", ("g",), cosigners=("MOD",))
    rows = [gm, md, WN.opener("p", "m2", "moderation_fallback", "g", ("md",)), WN.receipt("r", "m2", "p", 0), WN.answer("x3", "m3", "p", "act"),
            WN.answer("x2", "m2", "p", "act"), WN.landing("L", "m2", "p", "r", "fallback", Wm, ("x2", "x3"))]
    o, bad = win(rows); t.order(bad)
    t.fact("two members act over a present moderator without waiting 48 h: recount=%s (until the moderator signs an answer)" % o["recount"], o["recount"] == "fallback")
    t.note("not expressible: two honest nodes straddling the close on one clock, and what is owed at the close (a key rotation after an eviction); window.py has no `now` and no owed set")
    return dict(cls="CONCEDED", who="any key holding the concluder's seat: one device of a self roster (a stolen one included), one accord holder, one member",
                witness="g(h1,h2,h3) p(h1 halts) r(h3 receipt, stating an instant 24 h ago) L(h3 'lapsed', stating now). Signed together. Every reader: lapsed. One hostile holder undoes 'one holder fires at once'.",
                protects="KERNEL 5: 'the window's length is the concluder's own word'; causal_order README: 'No theorem says a landing came late enough.' "
                         "In practice every lone window has length zero against a lying concluder; the only defence is the recount (the target or a counted key signs later). "
                         "For the halt that needs a second honest holder; for an eviction, any row by the target; for the fallback, the moderator's answer.",
                fix="")


@test(12, "Thief evicting alone, with control of delivery", "did:plc clobber; KERI superseding recovery; window_adversary.tsv",
      "A thief holding one device of three cannot evict the owner, even when it decides what readers are offered and when.")
def t12(t):
    W = WN.secs("self_roster_evict")
    g = ST.offer("g", "d1", ("d1", "d2", "d3"), "self", "@", "self", cosigners=("d2", "d3"))
    p = WN.opener("p", "d3", "self_roster_evict", "g", ("g",), target="d1")
    thief = [g, p, WN.receipt("r", "d3", "p", 0), WN.landing("L", "d3", "p", "r", "landed", W)]
    o, bad = win(thief); t.order(bad)
    t.fact("the owner never sees the opener and so never objects; a reader offered only the thief's rows: void=%s contest=%s recount=%s" % (o["void"], o["contest"], o["recount"]), o["recount"] == "landed")
    n = R("n", "note", "d1", ("g",))                       # any row at all by the owner's device, about anything
    o, bad = win(thief + [n]); t.order(bad)
    t.fact("the same reader once it holds ANY row signed by the target that does not name the landing: void=%s contest=%s recount=%s" % (o["void"], o["contest"], o["recount"]),
           o["recount"] == "contested" and o["void"] == "landed")
    L2 = [WN.receipt("r2", "d2", "p", 0), WN.landing("L2", "d2", "p", "r2", "refused", W, ("L", "n"))]
    o, bad = win(thief + [n] + L2); t.order(bad)
    t.fact("the owner's other device lands 'refused' naming both: %s" % o["recount"], o["recount"] == "refused")
    L3 = [WN.receipt("r3", "d3", "p", 0), WN.landing("L3", "d3", "p", "r3", "landed", W, ("L2",))]
    S = conc(thief + [n] + L2 + L3, WIN)
    o, bad = win(thief + [n] + L2 + L3); t.order(bad)
    t.fact("the thief's further landing naming that one does not conclude (%s) and the outcome stays %s" % (S.C["L3"], o["recount"]), not S.C["L3"] and o["recount"] == "refused")
    L4 = [WN.receipt("r4", "d3", "p", 0), WN.landing("L4", "d3", "p", "r4", "landed", W)]         # the thief lands again, naming nothing new
    o, bad = win(thief + [n] + L2 + L4); t.order(bad)
    t.fact("the thief lands again beside it, naming only its own receipt: recount=%s (a landing that does not stand says nothing against one that does)" % o["recount"], o["recount"] == "refused")
    own = [g, WN.opener("p", "d1", "self_roster_evict", "g", ("g",), target="d3"), WN.receipt("r", "d1", "p", 0), WN.landing("L", "d1", "p", "r", "landed", W), R("n", "note", "d3", ("g",))]
    o, bad = win(own); t.order(bad)
    t.note("stated residuals: an absent owner looks lost (the first line above), and an owner with one live device cannot evict a thief who signs anything (recount=%s)" % o["recount"])
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a thief with one device of three and control of delivery",
                witness="p(d3 evicts d1) r,L(d3 lands 'landed'); n(any row by d1 not naming L). A reader with n: contested. With d2's landing naming both: refused, and the thief's reply to it concludes nothing.",
                protects="Recount, and the 'target silent' clause read over rows concurrent with the landing: the thief must keep every row the target ever signs afterwards from every reader, for ever. "
                         "Rule (i) (void) gives the thief the eviction. Residuals as stated in window_adversary.tsv: an absent owner looks lost; a one-against-one race with a lost third device has no winner.",
                fix="")


# =========================================================================================================
# C. Equivocation and veto
# =========================================================================================================
@test(13, "Slot veto by an entitled key", "blocklace; Keyline; p2panda-auth",
      "One hostile key that is entitled on a slot cannot keep a decision the count has made from standing.")
def t13(t):
    Wd = WN.secs("halt_fuse")
    g = ST.offer("g", "h1", ("h1", "h2", "h3"), "holder", "@", "self", cosigners=("h2", "h3"))
    p = WN.opener("p", "h1", "halt_fuse", "g", ("g",))
    c2 = WN.answer("c2", "h2", "p", "confirm")
    rows = [g, p, c2, WN.receipt("r", "h2", "p", 0), WN.landing("L", "h2", "p", "r", "confirmed", 0, ("c2",))]
    o, bad = win(rows); t.order(bad)
    t.fact("a halt confirmed by two of three holders and landed: recount=%s" % o["recount"], o["recount"] == "confirmed")
    rival = [WN.receipt("r3", "h3", "p", -Wd), WN.landing("L3", "h3", "p", "r3", "lapsed", 0)]           # names only the opener: its own past gives 'lapsed'
    o1, bad = win(rows + rival); t.order(bad)
    S = conc(rows + rival, WIN)
    t.fact("the third holder lands 'lapsed' beside it, leaving the confirm unnamed (concluded=%s): void=%s contest=%s recount=%s" % (S.C["L3"], o1["void"], o1["contest"], o1["recount"]),
           o1["recount"] == "confirmed")
    o3, bad = win(rows + rival + [WN.landing("L5", "h3", "p", "r3", "lapsed", 0, ("L3",))]); t.order(bad)
    t.fact("and again, re-using its receipt: recount=%s" % o3["recount"], o3["recount"] == "confirmed")
    lone, bad = win([g, p, c2, WN.receipt("r3", "h3", "p", -Wd), WN.landing("L3", "h3", "p", "r3", "lapsed", 0)]); t.order(bad)
    t.fact("a false lapse with no standing landing beside it is still %s" % lone["recount"], lone["recount"] == "contested")
    import check_cut as CC
    G = R("g", "genesis", "admin", members=("admin", "co", "m", "u"))
    rows2 = [G, R("a", "claim", "m", ("g",), slot="s"), R("b", "claim", "u", ("g",), slot="s"), R("a3", "claim", "m", ("a", "b"), slot="s"), R("b2", "claim", "u", ("g",), slot="s")]
    ref, bad = free(rows2, CC.rule, lambda S: CUT.Cut(S).holder("s")); t.order(bad)
    t.note("stated limit (KERNEL 6.2): a claim slot with two entitled claimants stays in %s for one rival signature a round; emptiness is the answer there, and what matters must be decided by a count" % ref)
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="one key holding the concluder's seat (one accord holder of three)",
                witness="p(h1 halts) c2(h2 confirms) L(h2 lands 'confirmed', naming c2) r3,L3(h3 lands 'lapsed', naming only p). L3 concludes and does not stand; the outcome of p is 'confirmed' for every reader.",
                protects="window.py recount: a landing stands only if the table gives its outcome over every answer that does not name it, and a landing that does not stand says nothing against one that does (Recount.quorum_closed_final, now at the outcome).",
                fix="")


@test(14, "Duelling admins", "Matrix; Keyline 'bricked'; p2panda-auth 'freezes'",
      "Two keys of equal standing that remove each other leave the slot contested, not empty, and every slot that matters has a voice one key cannot remove.")
def t14(t):
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    us = lambda a, b: ST.unseat("x%s%s" % (a[1], b[1]), a, b, "founder", "g", "self", ("g",))
    hold = lambda S: (ST.Seats(S).holders("founder", "g"), frozenset(CUT.Cut(S).all().items()))
    for label, rows in (("two founders unseat each other, each alone (conferrer=self)", [us("f1", "f2"), us("f2", "f1")]),
                        ("a ring of three", [us("f1", "f2"), us("f2", "f3"), us("f3", "f1")]),
                        ("one founder alone unseats the other two", [us("f3", "f1"), us("f3", "f2")])):
        ref, bad = free([g] + rows, SEAT, hold); t.order(bad)
        t.fact("%s: the rows %s; founders %s" % (label, sorted(set(v for k, v in ref[1] if k.startswith("x"))), fs(ref[0])), ref[0] == {"f1", "f2", "f3"})
    import check_cut as CC
    G = R("g", "genesis", "admin", members=("admin", "co", "m", "u"))
    ra, rb = R("ra", "removal", "admin", ("g",), removes="co"), R("rb", "removal", "co", ("g",), removes="admin")
    ref, bad = free([G, ra, rb], lambda r, P, past: True, lambda S: tuple(sorted(CUT.Cut(S).all().items()))); t.order(bad)
    t.fact("cut.py, two keys of equal standing each removing the other's KEY (KERNEL 6.5): %s" % dict(ref), dict(ref)["ra"] == "contested" and dict(ref)["rb"] == "contested")
    g2 = ST.offer("g", "f1", ("f1", "f2"), "founder", "@", "self", cosigners=("f2",))
    xg = ST.unseat("x", "f1", "f2", "founder", "g", "group", ("g",), head=("g",), policy="community_remove", content="x", counted="founder")
    S = conc([g2, xg], SEAT)
    t.fact("the counted removal the role table names for a founder (community_remove): one founder of two alone concludes=%s" % S.C["x"], not S.C["x"])
    c3 = ST.cosign("c3", "f3", "x", ("g",))
    x3 = ST.unseat("x", "f1", "f2", "founder", "g", "group", ("g", "c3"), head=("g",), policy="community_remove", content="x", counted="founder")
    ref, bad = free([g, c3, x3], SEAT, hold); t.order(bad)
    t.fact("two founders of three remove the third by the count: founders %s" % fs(ref[0]), ref[0] == {"f1", "f3"})
    t.note("what this gives up: two founders who are the only two can no longer remove each other at all (two of two is needed), and a lone hostile founder of two cannot be removed by the other")
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="any one key that signed a group's founding row",
                witness="g(f1,f2,f3 found) x12(f1 unseats f2, conferrer=self) x21(f2 unseats f1, conferrer=self). Neither concludes. All three remain founders.",
                protects="seat.py conclusion rule: over a founding row that seats several keys, no one of them is the object's own key against the others; ending such a seat takes its holder's withdrawal or the count the role table names. "
                         "Mutual cuts on a key stay contested (cut.py, KERNEL 6.5).",
                fix="")


@test(15, "Equivocating voter", "blocklace; Window.fork_shares_signer",
      "A faction below the count cannot keep a roster split alive by having its members sign both sides.")
def t15(t):
    m = lambda s: sum(1 << int(c) for c in s)
    r = FK.check("M0", 5, m("0123"), m("3"), "majority", 3)
    t.fact("roster_fork, majority of four with one hostile key, every set of up to 3 versions (%d sets): the adversary alone signs no valid version (%s), the honest members can always sign back to one head (%s), "
           "and every two valid versions of one head share a signer (%s)" % (r["sets"], r["adv_alone"] is None, r["rejoin"] is None, r["double_signer_missing"] is None),
           r["adv_alone"] is None and r["rejoin"] is None and r["double_signer_missing"] is None)
    W = FK.world("M0", 5, m("0123"), m("3"), "majority")
    v1 = W.mk((0,), (), m("01234"), m("013"))
    v2 = W.mk((0,), (), m("012"), m("123") & ~m("3") | m("012"))
    C = FK.conclude(W, frozenset([0, v1, v2]), "M0")
    t.note("two versions of the genesis share honest signers h0 and h1 as well as any hostile one: the model does not tell an equivocator from an honest key that approved two proposals, and no function reports either. Roster while the tips wait: %s" % FK.names(W, C.roster))
    title, cases = WN.self_world()
    g, p = cases[0][1][0], cases[0][1][1]
    rows = [g, p, WN.answer("e1", "d2", "p", "approve"), WN.answer("e2", "d2", "p", "object"), WN.receipt("r", "d3", "p", 0), WN.landing("L", "d3", "p", "r", "landed", 0, ("e1",))]
    o, bad = win(rows); t.order(bad)
    S = conc(rows, WIN)
    t.fact("a window voice that says two things: a landing that names only the approval concludes (%s), and under recount the unnamed objection is counted with it, so the voice says nothing: %s"
           % (S.C["L"], o["recount"]), o["recount"] == "contested")
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a faction below the count, rotating which of its keys signs twice",
                witness="Every set of up to three versions with one hostile key of four: no valid version is the adversary's alone, and from every forked set one honest version returns to one head.",
                protects="roster_fork M0 (tips wait; a merge is counted over the keys common to the tips) and the count itself: each tip needs honest signatures, so the faction cannot make the second tip. "
                         "What is missing is any consequence: the kernel does not even notice the double signer (no answer reports it), and nothing distinguishes it from honest concurrency.",
                fix="")


@test(16, "Tip flooding", "roster_fork README; blocklace",
      "A member below the count cannot keep an honest joiner unlisted for long, or at low cost.")
def t16(t):
    m = lambda s: sum(1 << int(c) for c in s)
    W = FK.world("M0", 6, m("0123"), m("3"), "majority")
    S = frozenset([0])
    adv_alone = [c for c in W.children(S) if W.vs[c]["sig"] & W.H == 0]
    t.fact("the hostile member alone can add %d sibling versions" % len(adv_alone), not adv_alone)
    v1 = W.mk((0,), (), m("01234"), m("012"))                    # the honest three admit joiner 4
    S = S | {v1}
    listed = lambda S: bool(FK.conclude(W, S, "M0").roster >> 4 & 1)
    t.fact("joiner admitted on one tip: listed=%s" % listed(S), listed(S))
    rounds, adv_sigs, honest_sigs = 0, 0, 0
    # each abandoned honest proposal at the genesis that reached two honest signatures is completed by the hostile key (one signature)
    stale = [(m("01235"), m("01")), (m("0123"), m("02")), (m("012"), m("12"))]
    for Rv, hs in stale:
        f = W.mk((0,), (), Rv, hs | m("3"))
        if not W.valid(f): continue
        S = S | {f}; adv_sigs += 1
        was = listed(S)
        C = FK.conclude(W, S, "M0")
        b = FK.best_row(W, S, "M0")
        if b is None: break
        need = min(k for k in range(1, 7) if 2 * k > FK.bits(C.roster))          # the merge is counted over the keys common to the tips
        honest_sigs += need; S = S | {b}; rounds += 1
        t.note("round %d: hostile key completes a stale version (1 signature); joiner listed=%s, tips=%d; an honest merge needs %d signatures (a majority of the %d common keys); joiner listed=%s" % (rounds, was, len(C.tips), need, FK.bits(C.roster), listed(S)))
    t.fact("without the checkpoint (roster_fork alone), %d rounds: %d hostile signatures against %d honest ones; after each merge the joiner is listed again" % (rounds, adv_sigs, honest_sigs), rounds == 3 and listed(S))
    floods = [i for i in S if W.vs[i]["E"] == (0,) and W.vs[i]["sig"] & W.F]
    first_merge = min(i for i in S if len(W.vs[i]["E"]) > 1)
    T, U, r = cp_versions(W, S, ack=first_merge)
    t.fact("a reader that acknowledged the first merge: of the %d stale versions completed on the genesis, %d count for it (the one that merge names); every later one is behind its line. A reader with no acknowledgement needs each merged"
           % (len(floods), len([i for i in floods if i in U])), len([i for i in floods if i in U]) == 1)
    return dict(cls="CONCEDED", who="one seated member below the count (or a removed one), but only with a stale proposal that honest members had signed to within the adversary's own signatures of the count",
                witness="G{0,1,2,3}; v1 admits 4 (signed 0,1,2). Hostile 3 completes an abandoned proposal on G that 0 and 1 once signed. Two tips: roster is the common {0,1,2,3}, the joiner is unlisted until three honest keys sign a merge.",
                protects="roster_fork README: 'What it costs. A member added on one tip is not listed until a version names both tips.' The adversary alone makes no tip (0 valid versions). "
                         "Each flood costs the adversary one signature and one pocketed honest proposal, on any past head, and costs the honest side a merge signed by the count; it cannot be repeated without a fresh pocketed proposal. "
                         "A reader that has acknowledged a merge is not moved by a later flood from below it.",
                fix="")


@test(17, "Invariants that are not confluent", "Bailis et al. invariant confluence; Byzantine eventual consistency",
      "A rule of the form 'at least one', 'exactly one' or 'count still met' holds after two concurrent rows that each respect it.")
def t17(t):
    g = ST.offer("g", "f1", ("f1", "f2"), "founder", "@", "self", cosigners=("f2",))
    w1, w2 = ST.withdraw("w1", "f1", "g"), ST.withdraw("w2", "f2", "g")
    ref, bad = free([g, w1, w2], SEAT, lambda S: ST.Seats(S).holders("founder", "g")); t.order(bad)
    t.fact("'at least one founder': two founders resign concurrently, each leaving the other: founders %s" % fs(ref), ref == frozenset())
    ref, bad = free([g, w1, w2, ST.offer("re", "f1", "f1", "founder", "g", "self", ("w1", "w2"))], SEAT, lambda S: ST.Seats(S).holders("founder", "g")); t.order(bad)
    t.fact("and neither can come back alone: a founding signer's own offer stands on its founding seat, which it withdrew: founders %s. The group has no founder for good." % fs(ref), ref == frozenset())
    o1 = ST.offer("o1", "A", "K1", "owner", "A", "self"); o2 = ST.offer("o2", "A", "K2", "owner", "A", "self")
    ref, bad = free([o1, ST.accept("a1", "K1", "o1"), o2, ST.accept("a2", "K2", "o2")], SEAT, lambda S: (ST.Seats(S).one("owner", "A"), ST.Seats(S).holders("owner", "A"))); t.order(bad)
    t.fact("'exactly one owner': the owned key binds two owners concurrently: the single holder is %s (live seats %s)" % (ref[0], fs(ref[1])), ref[0] is None)
    base = room_rows(*ROOM)
    aD = in_room(ST.accept("aD", "D", None, ("g",), scope="member", obj="g"))
    cC = in_room(ST.cosign("cC", "C", "wD", ("w",)))
    wD = ST.offer("wD", "A", "D", "member", "g", "group", ("w", "aD", "cC"), head=("w",), policy="community_invite", content="wD", room="g")
    mem, st, bad = roster(base + [aD, cC, wD]); t.order(bad)
    t.fact("'count still met': an admission counted with a voice that a concurrent removal takes away waits with it (tips): roster %s" % fs(mem), mem == {"A", "B"})
    return dict(cls="CONCEDED", who="no adversary is needed: two honest keys acting concurrently; or one key that wants the slot empty",
                witness="g(f1,f2 found) w1(f1 resigns) w2(f2 resigns), neither naming the other: no founder, and no row either can sign alone restores one. o1,o2(A binds K1 and K2 as owner): no owner.",
                protects="KERNEL 6.2: 'The same kind on one slot: both or neither.' causal_order README: 'A contested slot may stay empty; nothing here ends a dispute.' "
                         "'Exactly one' is kept as 'at most one'. 'Count still met' is kept by tips waiting. 'At least one' is kept by no rule and is stated as a limit in KERNEL.md: it needs a window (a resignation that lands only if another founder remains) "
                         "or a restatement. With the founding signers no longer the object's own key for ever, an emptied founder set has no recovery inside the kernel.",
                fix="")


# =========================================================================================================
# D. Old keys and old quorums
# =========================================================================================================
def long_range():
    m = lambda s: sum(1 << int(c) for c in s)
    W = FK.world("M0", 5, m("012"), m("12"), "majority")
    v1 = W.mk((0,), (), m("0123"), m("01"))
    v2 = W.mk((v1,), (), m("01234"), m("013"))
    v3 = W.mk((v2,), (), m("0234"), m("034"))
    v4 = W.mk((v3,), (), m("034"), m("034"))
    return W, frozenset([0, v1, v2, v3, v4]), m


@test(18, "Long-range roster fork", "weak subjectivity (Buterin); KERNEL 7",
      "Keys that no longer hold the count cannot change, or deny, the roster a reader concludes.")
def t18(t):
    W, S0, m = long_range()
    C = FK.conclude(W, S0, "M0")
    t.fact("honest lineage: G{0,1,2} -> add 3 -> add 4 -> remove 1 -> remove 2; roster %s, one tip" % FK.names(W, C.roster), C.resolved and C.roster == m("034"))
    f1 = W.mk((0,), (), m("12"), m("12")); f2 = W.mk((f1,), (), m("12"), m("12"))
    gain = True
    for label, F in (("ONE version", {f1}), ("TWO, the second on the first", {f1, f2})):
        T, U, r = cp_versions(W, S0 | F)
        gain &= t.fact("keys 1 and 2 (two of three at the genesis, both since removed) sign %s on the genesis. A reader with no acknowledgement: two tips, and the roster is the keys common to them: %s. "
                       "No version the honest members can sign makes one head (%s)" % (label, FK.names(W, r), FK.best_row(W, S0 | F, "M0")), T == U and r == 0 and FK.best_row(W, S0 | F, "M0") is None)
        T, U, r = cp_versions(W, S0 | F, ack=max(S0))
        t.fact("   a reader that has acknowledged the honest head: roster %s, the forged line void" % FK.names(W, r), r == m("034") and f1 not in U)
    T, U, r = cp_versions(W, frozenset([0, f1, f2]))
    t.fact("a reader with no acknowledgement that is offered only the forged line: roster %s, nothing to show it is not the group" % FK.names(W, r), r == m("12"))
    T, U, r = cp_versions(W, S0 | {f1, f2}, ack=f2)
    t.fact("a reader that acknowledged the forged head while eclipsed keeps it against the honest line: roster %s" % FK.names(W, r), r == m("12"))
    return dict(cls="CONCEDED" if gain else "HOLDS", who="keys that met the count at an old head, signing one version; against a reader with no acknowledgement of its own",
                witness="f1(keys 1,2: 'remove 0' on the genesis). A reader holding both lines and no acknowledgement: two tips, roster empty, for good. A reader that acknowledged the honest head: unaffected.",
                protects="KERNEL 7: 'An adversary holding the count of an old head signs a valid version alone ... it is each reader's own trust that decides'. The reader's own acknowledged line voids a forged line of any length grown from below it. "
                         "What remains: a reader with no acknowledgement (a new one, or one that lost its own rows) gets plain tips-wait, the keys common to the lines, which is nobody; or the forged line, if that is all it is offered. "
                         "Two readers that acknowledged different lines differ for good. Recovery for a reader without an acknowledgement is outside the kernel: a witness, or being told the head by a key it already reaches.",
                fix="")


@test(19, "Posterior corruption", "weak subjectivity; KERI pre-rotation",
      "The keys of members removed long ago, all leaked, give an adversary nothing.")
def t19(t):
    W, S0, m = long_range()
    removed_ever = m("12")
    exposed = [i for i in sorted(S0) if W.meets(removed_ever, W.vs[i]["R"])]
    t.fact("with every key ever removed (1 and 2), the heads whose count they meet: %s of %d (the genesis; founders who all leave expose it for ever)" % (exposed, len(S0)), exposed == [0])
    W2 = FK.world("M0", 5, m("0123"), m("3"), "majority")
    a = W2.mk((0,), (), m("012"), m("012"))
    none = not any(W2.vs[c]["sig"] & W2.H == 0 for c in W2.children(frozenset([0, a])))
    t.fact("a group that removed fewer than the count at every head is not exposed: one removed key of four signs no valid version: %s" % none, none)
    f1 = W.mk((0,), (), m("12"), m("12")); f2 = W.mk((f1,), (), m("12"), m("12"))
    T, U, r = cp_versions(W, S0 | {f1, f2}, ack=max(S0))
    t.fact("with the leaked keys signing a forged line: a reader that acknowledged the honest head keeps roster %s; for one with no acknowledgement the roster is the keys common to the two lines: %s"
           % (FK.names(W, r), FK.names(W, cp_versions(W, S0 | {f1, f2})[2])), r == m("034") and cp_versions(W, S0 | {f1, f2})[2] == 0)
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    c3 = ST.cosign("c3", "f3", "xf", ("g",))
    xf = ST.unseat("xf", "f2", "f1", "founder", "g", "group", ("g", "c3"), head=("g",), policy="community_remove", content="xf", counted="founder")
    rows = [g, c3, xf, ST.unseat("u2", "f1", "f2", "founder", "g", "self", ("g",)), ST.unseat("u3", "f1", "f3", "founder", "g", "self", ("g",)), ST.offer("re", "f1", "f1", "founder", "g", "self", ("xf",))]
    ref, bad = free(rows, SEAT, lambda S: ST.Seats(S).holders("founder", "g")); t.order(bad)
    t.fact("seat.py: one leaked key of a removed founder gains nothing alone (founders %s)" % fs(ref), ref == {"f2", "f3"})
    return dict(cls="CONCEDED", who="whoever obtains the keys of removed members, once those keys together met the count at some past head; against a reader with no acknowledgement of its own",
                witness="As test 18 with only removed keys: keys 1 and 2, both removed, were two of three at the genesis; a forged line leaves a reader without an acknowledgement with an empty roster.",
                protects="KERNEL 7, the same sentence as test 18, with the same bound: no reader that has acknowledged a later honest head is moved. There is no pre-rotation and no expiry of an old head's count. "
                         "Exposure grows with turnover: once the founding members have all gone, the genesis count is entirely in removed keys.",
                fix="")


@test(20, "Disjoint witness choices", "Mazieres, Stellar consensus (federated Byzantine agreement)",
      "Two honest readers who trust different witnesses and hold the same rows conclude the same roster.")
def t20(t):
    rows = [R("e1", "edge", "R1", to="W1"), R("e2", "edge", "R2", to="W2"),
            R("t1", "attest", "W1", (), tip="T1"), R("t2", "attest", "W2", (), tip="T2")]
    S = conc(rows, lambda r, P, past: True)
    v = {(o, r["id"]): CK.means(S, r, o, 2) for o in ("R1", "R2") for r in rows if r["kind"] == "attest"}
    t.fact("what can be run: with the same four rows, W1's row means something to R1 only and W2's to R2 only (%s)" % sorted(k for k, x in v.items() if x),
           v[("R1", "t1")] and v[("R2", "t2")] and not v[("R1", "t2")] and not v[("R2", "t1")])
    t.note("there is no witness row, no rule that reads one and no 'witnessed lineage' in causal_kernel or roster_fork: fork.conclude takes no reader and returns one roster for all")
    return dict(cls="NOT EXPRESSIBLE", who="-",
                witness="Only the precondition runs: two readers, the same rows, different meaning by their own edges (Causal.two_readers).",
                protects="Missing: a witness row kind, the rule of CC 3.2 T6 that picks a lineage by the reader's own trust, and a roster answer that takes the reader's key. "
                         "What would settle it: roster_fork's enumeration run per reader with a witness filter, over two readers with disjoint and with one shared, double-signing witness, checking whether any row both hold shows the split.",
                fix="")


@test(21, "Eclipse of a reader's root", "Byzantine eventual consistency; weak subjectivity",
      "A bounded walk from the reader's own rows protects the reader even when those first rows were made against a view an adversary chose.")
def t21(t):
    N = 50
    rows = [R("e0", "edge", "me", to="X")] + [R("s%d" % i, "edge", "X", to="S%d" % i) for i in range(N)] + [R("say", "note", "S7", ())]
    S = conc(rows, lambda r, P, past: True)
    reach = CK.reach(S, "me", 2)
    t.fact("the reader's one edge, made in the dark, to the adversary's key: %d keys are within its walk and a row by any of them means something to it (%s)" % (len(reach) - 1, CK.means(S, S.by["say"], "me", 2)),
           len(reach) == N + 2 and CK.means(S, S.by["say"], "me", 2))
    S2 = conc(rows + [R("w", "withdraw", "me", ("e0",))], lambda r, P, past: True)
    t.fact("the reader withdraws that one edge: keys within its walk %d" % (len(CK.reach(S2, "me", 2)) - 1), len(CK.reach(S2, "me", 2)) == 1)
    S3 = conc(rows + [R("w", "withdraw", "Z", ("e0",))], lambda r, P, past: True)
    t.fact("nobody else can withdraw it for the reader: %d" % (len(CK.reach(S3, "me", 2)) - 1), len(CK.reach(S3, "me", 2)) == N + 2)
    W, S0, m = long_range()
    f1 = W.mk((0,), (), m("12"), m("12")); f2 = W.mk((f1,), (), m("12"), m("12"))
    T, U, r = cp_versions(W, S0 | {f1, f2}, ack=f2)
    t.fact("the reader checkpoint defends whatever head the reader first acknowledged: one that acknowledged a forged head while eclipsed keeps roster %s when later offered the honest line" % FK.names(W, r), r == m("12"))
    return dict(cls="CONCEDED", who="whoever controls what a new reader sees when it signs its first edge, acceptance or acknowledgement (an eclipse, or a look-alike group with its own genesis)",
                witness="e0(the reader's edge to X, taken for the group's root) s0..s49(X's edges). Fifty-one keys speak to this reader. Nothing in the rows says X is not who the reader meant.",
                protects="causal_order README: 'Every reader is its own seed ... Meaning is lost only through a withdrawal, by its own signer, of an edge on that walk.' KERNEL 1: no trust set among the inputs. "
                         "The walk bounds depth, not the first step. In practice: the cost is one successful deception at onboarding; it lasts until the reader learns of it out of band; recovery is one withdrawal by the reader, which removes everything at once. "
                         "The reader's own acknowledgement makes this stickier: it is the reader's cut, and an honest line offered later does not displace it.",
                fix="")


@test(22, "Second genesis", "CVE-2025-54315 (Matrix room creation)",
      "Nobody can make a second root row for an existing group or object identifier.")
def t22(t):
    g = ST.offer("g", "A", ("A", "B"), "member", "@", "self", cosigners=("B",), room="g")
    tries = {
        "a second founding row by an outsider carrying the object 'g' and naming g": ST.offer("z", "Z", ("Z",), "member", "g", "self", ("g",), room="g"),
        "the same, not naming g": ST.offer("z", "Z", ("Z",), "member", "g", "self", (), room="g"),
        "a founder row for scope founder over g by an outsider": ST.offer("z", "Z", "Z", "founder", "g", "self", ("g",), room="g"),
        "an outsider's unseat over g, conferrer self": ST.unseat("z", "Z", "A", "member", "g", "self", ("g",), room="g"),
    }
    for label, z in tries.items():
        mem, st, bad = roster([g, z]); t.order(bad)
        t.fact("%s: %s; roster %s" % (label, st["z"], fs(mem)), st["z"] == "concludes nothing" and mem == {"A", "B"})
    z = ST.offer("z", "Z", ("Z",), "member", "@", "self", room="g")
    mz = RT.msg("mz", "Z", "g", ("z",))
    mem, st, bad = roster([g, z, mz]); t.order(bad)
    t.fact("an outsider founds its own group and writes a row labelled room 'g' at its own head: the founding concludes, the message %s, roster of g %s" % (st["mz"], fs(mem)), st["mz"] == "concludes nothing" and mem == {"A", "B"})
    t.note("in seat.py, window.py and route.py an object is the digest of its founding row (obj='@'); two rows with one digest is a hash collision and is outside the model (causal_kernel.kept would keep the first offered)")
    pre = room_rows("g", "md", "ac", "cb", "w")
    aZ = in_room(ST.accept("aZ", "Z", None, ("g",), scope="member", obj="g"))
    wZ = ST.offer("wZ", "A", "Z", "member", "g", "group", ("g", "aZ", "cb"), head=("g",), policy="community_invite", content="w", room="g")
    memZ = roster(pre + [aZ, wZ], check=False)[0]
    t.note("two labels are NOT digests in the model: `room`, and `content` (what a cosignature signs). With `content` a free label, B's cosignature for admitting C also admits Z "
           "when A writes another offer under the same label on the same head (it concludes: %s). That is the model's shorthand, not a rule; a build must make it the digest of the act's signed fields." % conc(pre + [aZ, wZ], ROUTE).C["wZ"])
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="an outsider",
                witness="z(Z: a founding-style offer over object g). It concludes nothing: Z is not a signer of the row whose digest is g.",
                protects="The conclusion rule (seat_rule): a founding row is its own object, and a `self` offer over an existing object concludes only for that object's own key. The identifier is the digest everywhere in these modules.",
                fix="")


@test(23, "Root backdating", "Matrix: the creator 'can already effectively control a room by backdating'",
      "A founder or first conferrer that has left, or been removed, can no longer end other keys' seats or dissolve the group.")
def t23(t):
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    hold = lambda S: ST.Seats(S).holders("founder", "g")
    ref, bad = free([g, ST.withdraw("wd", "f1", "g")], SEAT, hold); t.order(bad)
    t.fact("a founder withdraws the founding row, naming the genesis only: it ends its own seat and no other (%s)" % fs(ref), ref == {"f2", "f3"})
    c3 = ST.cosign("c3", "f3", "xf", ("g",))
    xf = ST.unseat("xf", "f2", "f1", "founder", "g", "group", ("g", "c3"), head=("g",), policy="community_remove", content="xf", counted="founder")
    back = [ST.unseat("u2", "f1", "f2", "founder", "g", "self", ("g",)), ST.unseat("u3", "f1", "f3", "founder", "g", "self", ("g",)), ST.offer("re", "f1", "f1", "founder", "g", "self", ("xf",))]
    ref, bad = free([g, c3, xf] + back, SEAT, hold); t.order(bad)
    t.fact("f1 is removed by the count of the other two, then signs three rows alone (unseat f2, unseat f3, a `self` offer seating itself): founders %s" % fs(ref), ref == {"f2", "f3"})
    pre = room_rows("g", "md", "ac", "cb", "w")
    wd = in_room(ST.withdraw("wdw", "A", "w"))
    mem, st, bad = roster(pre + [wd]); t.order(bad)
    t.fact("counted room: C was admitted by A and B. A alone withdraws the admission row it signed: roster %s" % fs(mem), mem == {"A", "B", "C"})
    xAc = in_room(ST.cosign("xAc", "C", "xA", ("w",)))
    xA = ST.unseat("xA", "B", "A", "member", "g", "group", ("w", "xAc"), head=("w",), policy="community_remove", content="xA", room="g")
    mem, st, bad = roster(pre + [xAc, xA, wd]); t.order(bad)
    t.fact("A is then removed by B and C and signs that withdrawal, naming only the admission: roster %s" % fs(mem), mem == {"B", "C"})
    mem, st, bad = roster(pre + [in_room(ST.withdraw("wc", "C", "w"))]); t.order(bad)
    t.fact("the holder's own withdrawal still ends its counted seat: roster %s" % fs(mem), mem == {"A", "B"})
    gz = ST.offer("g", "Z", ("m1", "m2", "m3"), "member", "@", "self", cosigners=("m1", "m2", "m3"))
    ref, bad = free([gz, ST.withdraw("wd", "Z", "g")], SEAT, lambda S: ST.Seats(S).holders("member", "g")); t.order(bad)
    t.note("stated cell: a founding row signed by a creator that it does not seat is ended for everyone by that creator's withdrawal, at any time (members %s). That is the conferrer's voice; a group that does not want it is founded by its own members." % fs(ref))
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok else "BROKEN", who="a key that signed the founding row, after its removal; the member whose signature is on a counted admission",
                witness="g(f1,f2,f3) xf(f2+f3 remove f1) u2,u3(f1: `self` unseats) re(f1: `self` offer to itself). None takes effect: founders {f2,f3}. w(A admits C, B cosigns) wdw(A withdraws w): C stays.",
                protects="seat.py: a `self` unseat over a founding row that seats several keys concludes nothing; a founding signer's `self` offer stands on its own founding seat; "
                         "the conferrer of a counted offer is the count, so its proposer's lone withdrawal ends nothing.",
                fix="")


# =========================================================================================================
# E. Door, transport, disclosure
# =========================================================================================================
@test(24, "Two implementations, one row", "Matrix canonical JSON and state resolution divergences",
      "Every implementation's door keeps exactly the same rows.")
def t24(t):
    S = CK.kept([R("a", "note", "k", malformed=True), R("b", "note", "k")])
    t.fact("the door in these modules is one predicate on one flag (`malformed`): kept %s" % [r["id"] for r in S], [r["id"] for r in S] == ["b"])
    return dict(cls="NOT EXPRESSIBLE", who="-", witness="There is one implementation and no byte form of a row here.",
                protects="Missing: a second implementation and the wire encoding. What would settle it: a differential fuzz of each implementation's door over the 2.6.1.7 CDDL and vectors "
                         "(integer ranges, map order, duplicate keys, length limits, number of named rows), counting rows one keeps and another refuses. KERNEL 3 makes the door 'the row alone', so that is the whole surface.",
                fix="")


@test(25, "Parent-count and head-count exhaustion", "Kleppmann, Byzantine CRDTs; Matrix",
      "No row an adversary can sign makes honest rows too costly to keep or impossible to form.")
def t25(t):
    times = []
    for n in (50, 100, 200):
        rows = [R("g", "note", "k")] + [R("r%d" % i, "note", "k", ("g",)) for i in range(n)] + [R("big", "note", "X", tuple("r%d" % i for i in range(n)))]
        t0 = time.time(); S = conc(rows, lambda r, P, past: True); ST.Seats(S); times.append((n, round(time.time() - t0, 3)))
    t.fact("no limit on the number of rows a row names is stated or enforced; one row naming n rows, kept and concluded here in (n, seconds): %s" % times, True)
    m = lambda s: sum(1 << int(c) for c in s)
    W = FK.world("M0", 5, m("0123"), m("3"), "majority")
    t.fact("roster_fork merges at most %d tips in one version (a model bound); more tips are merged in steps, so a per-row limit delays a merge and does not prevent it" % W.maxmerge, W.maxmerge == 4)
    return dict(cls="NOT EXPRESSIBLE", who="-", witness="Cost only: a single row naming 200 rows is kept and concluded; the modules state no bound and model no storage.",
                protects="Missing: a stated limit on named rows and on heads, a storage or time budget, and a second implementation that enforces a different limit. "
                         "What would settle it: the limit as a constant in constitution/constants.tsv, and test 24's fuzz across it. Either choice has a cost the text must pick: no limit is a cost attack, a limit is a split unless every door has the same one.",
                fix="")


@test(26, "Withheld ancestor", "Kleppmann: 'never being delivered'; Jacob et al.: 'only omission faults remain'",
      "Honest nodes offered a cut end with the same answer, even if its signer serves one of the rows it names to some of them only.")
def t26(t):
    base = room_rows("g", "md", "ac", "cb", "w", "m2", "xc")
    g2 = ST.offer("g2", "A", ("A", "C"), "member", "@", "self", cosigners=("C",), room="g2")           # another room: A and C only
    h = RT.msg("h", "C", "g2", ("g2",))                                                                  # the row the removal cites
    x = ST.unseat("x", "A", "C", "member", "g", "group", ("w", "xc", "m2", "h"), head=("w",), policy="community_remove", content="x", room="g")
    full = base + [g2, h, x]
    part = base + [x]                                                                                    # B is offered the removal, not what it names
    memA, _, bad = roster(full); t.order(bad)
    memB, _, bad = roster(part); t.order(bad)
    kB = {r["id"] for r in CK.kept(part)}
    need = RT.needs({"x"} | set(x["names"]), kB)
    split = t.fact("A (holds everything): roster %s. B (offered the removal but not the row h it names): the removal waits at the door, roster %s; missing: %s" % (fs(memA), fs(memB), sorted(need)),
                   memA == {"A", "B"} and "C" in memB and need == {"h", "x"})
    S = conc(full, ROUTE)
    own, closed = RT.audience(S, "own"), RT.audience(S, "closed")
    t.fact("is B in the audience of h? by h's own head: %s; by carriage: %s (h is a row of another room and A did not sign it, so the removal that names it carries it to nobody)" % ("B" in own["h"], "B" in closed["h"]),
           "B" not in own["h"] and "B" not in closed["h"])
    return dict(cls="CONCEDED" if split else "HOLDS", who="the signer of the cut (a key with standing on the slot), or any relay, by omission",
                witness="x(A+B remove C, naming h, a row of another room that A serves to nobody). A and those it serves: C is out. B: the removal is offered but never kept, C stays a member, and every row that names x waits too.",
                protects="KERNEL 3: 'a row waits for what it names'; KERNEL 8: 'Two nodes with the same rows conclude the same' and nothing more. The attacker gains only what not sending the cut at all would give. "
                         "It lasts as long as the row is withheld; `missing` names it. A row cited from another room is carried only by its own signer, so a cut that names one waits until that signer carries it.",
                fix="")


@test(27, "Duplication and spurious cuts", "UCAN: 'spurious Revocations ... DoS vector'",
      "Rows that are kept on form and can never count change no answer, and their cost to an honest node is bounded.")
def t27(t):
    base = room_rows(*ROOM)
    ref, st0, _ = roster(base, check=False)
    times = []
    for n in (20, 80, 160):
        spam = [ST.unseat("z%d" % i, "X", "AB"[i % 2], "member", "g", "group" if i % 3 else "self", ("x",), head=("x",), policy="community_remove", content="z%d" % i, room="g") for i in range(n)]
        t0 = time.time()
        S = conc(base + spam, ROUTE); mem = ST.Seats(S).holders("member", "g")
        times.append((n, len(S.rows), mem == ref, round(time.time() - t0, 2)))
    t.fact("n spurious unseats by an outsider: (n, rows kept, roster unchanged, seconds for one read) %s" % times, all(x[2] for x in times))
    mem, st, bad = roster(base + base + [dict(r) for r in base]); t.order(bad)
    t.fact("every row offered three times: roster %s" % fs(mem), mem == ref)
    one = ST.unseat("z", "A", "B", "member", "g", "group", ("x",), head=("x",), policy="community_remove", content="z", room="g")
    mem, st, bad = roster(base + [one]); t.order(bad)
    t.fact("a seated member's unseat with one voice of two: %s, roster %s" % (st["z"], fs(mem)), mem == ref)
    S = conc(base + [R("zz", "note", "X", ("m2",), room="g")], ROUTE)
    t.fact("a kept row that concludes nothing is inert for the audience answer too: an outsider's row naming m2 does not put the outsider in m2's audience", "X" not in RT.audience(S)["m2"])
    return dict(cls="CONCEDED", who="an outsider: any key at all, at one signature a row",
                witness="z0..z159(X: unseats of A and B). All 160 are kept, none concludes, the roster does not move; the time of one read grows with them.",
                protects="KERNEL 3: kept is 'the row alone ... never refused for another row', so a well-formed row by a stranger is kept. Safety holds (no answer moves, replays are one row). "
                         "The cost is not bounded by any rule here: there is no storage model, no rate, and no rule that lets a node drop a row that concludes nothing for it. In practice a node must bound this outside the kernel (KERNEL 8: load decisions stay outside).",
                fix="")


def two_rooms():
    rows = RT.world()
    g2 = ST.offer("g2", "A", ("A", "Y"), "member", "@", "self", cosigners=("Y",), room="g2")
    return rows, g2


def audience_cases():
    """What each attempt gets under the audience rule."""
    aud = lambda S: RT.audience(S, "closed")
    rows, g2 = two_rooms()
    out = {}
    S = RT.state_of(rows + [R("z1", "note", "X", ("m1",), room="g")])
    out["outsider X names m1"] = "X" in aud(S)["m1"]
    S = RT.state_of(rows + [in_room(ST.accept("z1", "X", None, ("g",), scope="member", obj="g"))])
    out["outsider X signs an acceptance naming the founding row"] = "X" in aud(S)["g"]
    S = RT.state_of(rows + [RT.msg("z1", "C", "g", ("w",), names=("m5",))])
    out["removed C names m5 (written after its removal)"] = "C" in aud(S)["m5"]
    S = RT.state_of(rows + [RT.msg("z1", "C", "g", ("w",), names=("m1",))])
    out["joiner C names m1 (written before it joined)"] = "C" in aud(S)["m1"]
    S = RT.state_of(rows + [g2, RT.msg("z1", "A", "g2", ("g2",), names=("m1",))])
    a = aud(S)
    out["member A names m1 from a row of another room g2"] = "Y" in a["m1"]
    out["  ...and the founding row of g travels to g2 with it"] = "Y" in a["g"]
    S = RT.state_of(rows + [RT.REPLY])
    out["member A replies to m1 in the room after C joined"] = "C" in aud(S)["m1"]
    S = RT.state_of(rows)
    out["KEEP: joiner C is in the audience of the founding row its admission names"] = "C" in aud(S)["g"]
    return out


@test(28, "Audience widening by naming", "KERNEL 5 (missing and copying)",
      "A row reaches only keys its room admitted: nobody outside a row's audience can put themselves, or anyone, into it.")
def t28(t):
    got = audience_cases()
    for k, v in got.items(): t.note("%s -> %s" % (k, v))
    t.fact("an outsider does not enter a row's audience by signing a row that names its digest", not got["outsider X names m1"])
    t.fact("nor the audience of a group's founding row by signing an acceptance nobody offered", not got["outsider X signs an acceptance naming the founding row"])
    t.fact("a removed member does not enter the audience of a message written after its removal", not got["removed C names m5 (written after its removal)"])
    t.fact("a joiner does not enter the audience of an earlier message by naming it itself", not got["joiner C names m1 (written before it joined)"])
    t.fact("the joiner is in the audience of the founding rows its admission names", got["KEEP: joiner C is in the audience of the founding row its admission names"])
    t.fact("a member's reply carries the message it answers to a later joiner (ruled: a reply carries what it answers)", got["member A replies to m1 in the room after C joined"])
    rows = RT.world()
    z = RT.msg("z1", "C", "g", ("w",), names=("m5",))
    ref, bad = free(rows + [z], ROUTE, lambda S: frozenset(RT.route_sets(S)["C"])); t.order(bad)
    t.fact("route.py routes removed C nothing of m5: %s" % ("m5" not in ref), "m5" not in ref)
    zx = [ST.offer("zo", "X", "X", "member", "g", "self", ("g",), room="g"), RT.msg("z1", "X", "g", ("g",), names=("m5",))]
    ref, bad = free(rows + zx, ROUTE, lambda S: frozenset(RT.route_sets(S)["X"])); t.order(bad)
    t.fact("an outsider that signs itself an offer and a row naming m5 is routed only its own two rows: %s" % sorted(ref), ref <= {"zo", "z1"})
    ms1, ms2 = RT.measure(RT.world()), RT.measure([x for x in RT.world() if x["id"] not in ("xc", "x", "m4", "m5", "k4")] + [RT.REPLY])
    differ = sum(len(x["differ"]) for x in ms1.values()) + sum(len(x["differ"]) for x in ms2.values())
    t.fact("a party given only its routed rows still concludes what a party given everything does (conclusions that differ: %d)" % differ, differ == 0)
    cross = t.fact("no carriage to ANOTHER group by another's hand: A, a member of g and of g2, names m1 (a message of g that A did not sign) from a row it writes in g2. g2's member Y enters the audience of m1: %s; "
                   "and of the rows m1 names, down to g's founding row: %s" % (got["member A names m1 from a row of another room g2"], got["  ...and the founding row of g travels to g2 with it"]),
                   not got["member A names m1 from a row of another room g2"] and not got["  ...and the founding row of g travels to g2 with it"])
    S = RT.state_of(rows + [ST.offer("g2", "C", ("C", "Y"), "member", "@", "self", cosigners=("Y",), room="g2"), RT.msg("z1", "C", "g2", ("g2",), names=("m2", "m5"))])
    a = RT.audience(S)
    t.fact("a signer carries its OWN row to a group of its own, removed or not (m2, which C signed: %s), and no row another signed (m5: %s)" % ("Y" in a["m2"], "Y" in a["m5"]), "Y" in a["m2"] and "Y" not in a["m5"])
    ok = all(v for _, v in t.facts)
    return dict(cls="HOLDS" if ok and cross else "BROKEN", who="nobody but the row's own signer",
                witness="g2(A and Y) z1(A, in g2, naming m1 of g, which B signed). Y is routed nothing of g. A row of g travels to g2 only when its own signer names it there.",
                protects="Ruled by the owner: 'a reply carries what it answers'. route.py: a naming row carries its audience only if it is concluded and its signer is already in the named row's audience, "
                         "so a digest alone gives nothing to an outsider, a removed member or a joiner. Carriage stays inside one room, and a row leaves its room only when its own signer names it from elsewhere (Carry.lean). "
                         "The cost is test 26: a cut that names a row of another room waits until that row's signer carries it.",
                fix="")


@test(29, "Acknowledgement metadata", "Keyhive 'Relays must see membership'; SSB follow graph; did:plc timestamps",
      "A relay that sees only row envelopes learns nothing about who is in a group or who held what.")
def t29(t):
    rows = RT.world()
    S = RT.state_of(rows)
    env = [(r["id"], r["signer"], r["names"]) for r in rows]             # the least an envelope can be: digest, signer, what it names
    signers = {s for _, s, _ in env}
    held = {s: set() for s in signers}
    for i, s, names in env:
        held[s] |= {i} | set(S.anc[i])
    last = {s: max(len(S.anc[i]) for i, s2, _ in env if s2 == s) for s in signers}
    t.fact("from digest, signer and named digests alone, a relay reads: the active keys %s (the roster ever was {A,B,C}); for each key a lower bound on what it held (%s rows); "
           "and that C's rows stop being named after one row" % (fs(signers), {s: len(v) for s, v in sorted(held.items())}), signers == {"A", "B", "C"})
    return dict(cls="NOT EXPRESSIBLE", who="-", witness="Partial: with only (digest, signer, names) the relay recovers every key that ever wrote, a causal order of all rows, and per-key possession (every acknowledgement and head names what its signer held).",
                protects="Missing: an envelope format (which of kind, signer, names, room and instants are in the clear), and any transport. route.py decides who is sent a row, not what a carrier sees. "
                         "What would settle it: the wire's cleartext fields run through this same enumeration. The removal rule rewards naming often, and naming is exactly what the relay reads.",
                fix="")


@test(30, "`missing` as an oracle", "Willow private area intersection",
      "What a node asks for tells the party it asks nothing it does not already know.")
def t30(t):
    base = room_rows("g", "md", "ac", "cb", "w", "m2", "xc")
    by = {r["id"]: r for r in RT.world()}
    probe = R("probe", "note", "X", ("m2",), room="g")
    has = {r["id"] for r in CK.kept(base + [probe])}
    lacks = {r["id"] for r in CK.kept([r for r in base if r["id"] != "m2"] + [probe])}
    t.fact("a stranger offers a row naming digest m2: a node that holds m2 keeps the probe (%s), one that lacks it holds the probe waiting (%s) and its `missing` is %s"
           % ("probe" in has, "probe" not in lacks, sorted(RT.needs({"m2"}, lacks))), "probe" in has and "probe" not in lacks)
    S = RT.state_of(base + [by["x"]])
    t.note("the request set is a function of (what the node must conclude, what it holds): it names the conclusion being drawn. No module says whom a node asks, or whether it asks at all for a stranger's row.")
    return dict(cls="NOT EXPRESSIBLE", who="-", witness="Partial: route.needs gives the set a node would ask for; whether it asks, and whom, is transport. If it asks for whatever a waiting row names, any stranger can test any node for possession of any digest, one bit a probe.",
                protects="Missing: the request protocol (who is asked, for which waiting rows, with what cover). What would settle it: that protocol as rows or as a transport model, with the rule 'a node asks only for ancestors of rows whose signer its own walk reaches' tested against this probe.",
                fix="")


@test(31, "Removed member and concurrent keys", "Weidner et al. decentralised key agreement; Keyhive cross-fork",
      "While two roster tips wait, a member removed on one of them reads and mints under no new epoch.")
def t31(t):
    import keyplane as KP
    c = KP.Chain().add("seat", who="m")
    t.fact("keyplane.py is one chain: each row names the one before (%s), so two membership tips cannot be held by one writer there" % (c.add("end", who="m", how="removal").rows[-1]["names"],), True)
    # the seat rows of the same question: who is entitled at the heads a write names
    g = ST.offer("g", "A", ("A", "B", "C"), "member", "@", "self", cosigners=("B", "C"), room="g")
    xb = in_room(ST.cosign("xb", "B", "x", ("g",)))
    x = ST.unseat("x", "A", "C", "member", "g", "group", ("g", "xb"), head=("g",), policy="community_remove", content="x", room="g")
    aD = in_room(ST.accept("aD", "D", None, ("g",), scope="member", obj="g"))
    cB = in_room(ST.cosign("cB", "B", "wD", ("g",)))
    wD = ST.offer("wD", "A", "D", "member", "g", "group", ("g", "aD", "cB"), head=("g",), policy="community_invite", content="wD", room="g")
    rows = [g, xb, x, aD, cB, wD]
    S = conc(rows, ROUTE)
    past = lambda a, b: a in S.anc[b]
    ent = {h: ST.members_at(S.Cs, past, "g", h) for h in (("x",), ("wD",), ("x", "wD"))}
    t.fact("entitled at the heads a write names: the removal tip %s; the other tip %s; both tips %s (the removed member is out, and so is the joiner, until a version names both)"
           % (fs(ent[("x",)]), fs(ent[("wD",)]), fs(ent[("x", "wD")])), "C" in ent[("wD",)] and "C" not in ent[("x", "wD")] and "D" not in ent[("x", "wD")])
    mC = RT.msg("mC", "C", "g", ("wD",))
    mem, st, bad = roster(rows + [mC]); t.order(bad)
    t.fact("the removed member's own write, naming only the tip that still lists it: %s for a reader that holds the removal" % st["mC"], st["mC"] == "void")
    return dict(cls="NOT EXPRESSIBLE", who="-",
                witness="Partial, from seat rows: a writer that names only the tip without the removal (because it has not been offered the removal, or chooses not to name it) wraps to the removed member; "
                        "one that names both wraps to neither the removed member nor the joiner. The removed member's own writes are void for any reader holding the removal.",
                protects="Missing: a key plane with two membership heads (keyplane.Chain names one predecessor), wraps and epochs as rows over a forked roster. What would settle it: formal/key_plane's explorer run over the forked sets "
                         "of roster_fork, checking K1/K2/K8 at each head-set. The seat-level answer says the exposure is the time until every writer holds the removal, which a relay controls (test 5).",
                fix="")


@test(32, "Forward secrecy under retained past", "Keyhive: 'A current reader can decrypt all history'",
      "A key admitted today is not given what was written before it was admitted, unless the group decides so.")
def t32(t):
    joiner = [x for x in RT.world() if x["id"] not in ("xc", "x", "m4", "m5", "k4")]
    a = RT.route_sets(RT.state_of(joiner))["C"]
    b, bad = free(joiner + [RT.REPLY], ROUTE, lambda S: frozenset(RT.route_sets(S)["C"])); t.order(bad)
    t.fact("m1 was written before C joined. Routed to C without a reply: %s; after one member replies to m1: %s" % ("m1" in a, "m1" in b), "m1" not in a and "m1" in b)
    c = RT.route_sets(RT.state_of(joiner + [RT.msg("z1", "C", "g", ("w",), names=("m1",))]))["C"]
    t.fact("C names m1's digest itself, no member involved: routed %s" % ("m1" in c), "m1" not in c)
    t.note("no key material in route.py: whether C can read m1 is the key plane's tier (keyplane: at_seat wraps the current key only; at_seat_history wraps every key to the joiner)")
    return dict(cls="CONCEDED", who="any one member, by replying to the old row",
                witness="m1(B, before C joined) w(C admitted) m6(A replies to m1 at the new head). C is routed m1 and must hold it to keep m6.",
                protects="Ruled by the owner: 'a reply carries what it answers'. History is one reply away from any joiner, row by row, at any one member's choice; whether it decrypts is a tier of the key table. "
                         "The joiner cannot pull it itself. It cannot be undone, and nothing records it beyond the reply.",
                fix="")


@test(33, "Sybil reach", "SSB follow graph; SPKI/SDSI",
      "One hostile key that a reader reaches cannot cheaply bring an unbounded number of fresh keys within that reader's walk.")
def t33(t):
    N = 200
    rows = [R("e0", "edge", "me", to="H")] + [R("s%d" % i, "edge", "H", to="S%d" % i) for i in range(N)]
    S = conc(rows, lambda r, P, past: True)
    t.fact("edges: %d rows by H bring %d fresh keys within a depth-2 walk of every reader that reaches H" % (N, len(CK.reach(S, "me", 2)) - 2), len(CK.reach(S, "me", 2)) == N + 2)
    g = ST.offer("g", "F", "F", "founder", "@", "self")
    d = ST.offer("d", "F", "H", "moderate", "g", "seat", ("g",), under="g", sub=True)
    ah = ST.accept("ah", "H", "d")
    syb = tuple("S%d" % i for i in range(N))
    one = ST.offer("syb", "H", syb, "moderate", "g", "seat", ("ah",), under="d", cosigners=syb, sub=True)
    S = conc([g, d, ah, one], SEAT)
    n1 = len(ST.Seats(S).holders("moderate", "g")) - 2
    t.fact("seats: ONE row by H (an offer to %d keys, cosigned by them) seats %d fresh keys as moderators under H's sub-delegable seat" % (N, n1), n1 == N)
    chain = [g, d, ah]
    under, signer, prev = "d", "H", "ah"
    for i in range(6):
        o = ST.offer("c%d" % i, signer, "T%d" % i, "moderate", "g", "seat", (prev,), under=under, cosigners=("T%d" % i,), sub=True)
        chain.append(o); under, signer, prev = o["id"], "T%d" % i, o["id"]
    S = conc(chain, SEAT)
    deep = [k for k in ("T%d" % i for i in range(6)) if ST.Seats(S).stands(k, "moderate", "g")]
    t.fact("the only bound is depth: of a chain of six further links, %d stand (five links below a root, CC 3.4.7)" % len(deep), len(deep) == 4)
    S = conc([g, d, ah, one, ST.withdraw("wd", "F", "d")], SEAT)
    t.fact("recovery: one withdrawal by H's conferrer removes all of them at once (%d left)" % (len(ST.Seats(S).holders("moderate", "g")) - 1), len(ST.Seats(S).holders("moderate", "g")) == 1)
    return dict(cls="CONCEDED", who="one seated key whose seat may confer (a sub-delegable grant, or a scope the CONFERS table lets it give)",
                witness="d(F -> H moderate, sub-delegable) syb(H -> S0..S199, one row, cosigned by the 200 keys H made). 200 moderators for one signature by H.",
                protects="causal_order README: 'The walk has one depth for all edges; the classes and budgets of formal/trust_set are not carried over.' Fan-out is unbounded and one row can seat any number of keys; "
                         "depth (five links) and the scopes a seat may confer are the only limits. In practice: cost one row; it lasts until H's conferrer withdraws H's seat or a reader withdraws its own edge, either of which removes all of them at once.",
                fix="")


@test(34, "A forged line of two rows by a past count", "found by the Lean proof of the checkpoint (CP.built_on_void_for_reader)",
      "A past count cannot use the checkpoint itself: rows it signs on an old head, however many and each counted over the one before, leave no honest row behind.")
def t34(t):
    base = room_rows(*ROOM) + next_counted()             # ... x (A+B remove C, counted over w), wE (A+B admit E, counted over x)
    half_a = half_b = True
    for n in (1, 2, 3, 4):
        f = forged_line(n, "w")
        (m, st, tp), bad = reader_view(base + acked("wE") + f, own="B"); t.order(bad)
        half_a &= t.fact("%d forged row%s on the old head w; (a) a reader that acknowledged the honest head: members %s, the whole forged line void (%s), one tip"
                         % (n, "" if n == 1 else "s, each counted over the one before,", fs(m), ",".join(sorted(st))), m == {"A", "B", "E"} and tp == {"wE"} and "x" not in st and "z1" in st and (n == 1 or "z2" in st))
        (m, st, tp), bad = reader_view(base + acked("wE") + f); t.order(bad)
        half_b &= t.fact("   (b) a reader with no acknowledgement: no row is stale; the lines wait as two tips (%s) and the members are the keys common to them: %s. The removed key is not listed"
                         % (",".join(sorted(tp)), fs(m)), not st and "wE" in tp and len(tp) == 2 and m == {"A"})
    t.note("the fourth forged row does not conclude: the forged line's own admissions have by then outgrown the two keys that sign it")
    (m, st, tp), bad = reader_view(base + forged_line(2, "w"), checkpoint=True); t.order(bad)
    t.fact("built on is a rule of its own: even with the refused group checkpoint on, the second forged row does not leave the honest line behind (stale: %s; members %s)" % (",".join(sorted(st)) or "none", fs(m)), "x" not in st and "wE" not in st)
    ok = all(v for _, v in t.facts)
    return dict(cls="CONCEDED" if ok and half_a and half_b else "BROKEN", who="keys that met the count at an old head, signing any number of rows; against a reader with no acknowledgement of its own",
                witness="x(A+B remove C over w) wE(A+B admit E over x) z1(A with removed C: remove B, over w) z2(A with C: admit F, over z1). A reader that acknowledged wE: z1 and z2 are void, members {A,B,E}. "
                        "A reader with no acknowledgement: no row is void, two tips, members {A}. No honest row is left behind for anyone.",
                protects="checkpoint.settle: a counted act counts only if every counted act among the heads it names counts, and no line outranks another. A forged line falls whole with its first row for any reader whose acknowledged line "
                         "leaves that row behind. For a reader with none it is plain tips-wait (KERNEL 7): the members are the keys common to the tips, which is the forger alone when it sits on both lines, "
                         "and no counted row the honest members can sign ends that. The forger gains an unlisting, never a listing. This is the old count of tests 4 and 18 and nothing more.",
                fix="")


def checkpoint_price():
    """What the reader's line and tips cost, measured, and the two witnesses for which the group checkpoint is off.
    Returns (facts, order differences)."""
    t = Rec()
    pre = room_rows("g", "md", "ac", "cb", "w")
    hmc = in_room(ST.cosign("hmc", "B", "hm", ("w",))); hma = in_room(ST.accept("hma", "F", None, ("g",), scope="member", obj="g"))
    hm = ST.offer("hm", "A", "F", "member", "g", "group", ("w", "hmc", "hma"), head=("w",), policy="community_invite", content="hm", room="g")
    q1c = in_room(ST.cosign("q1c", "B", "q1", ("w",))); q1a = in_room(ST.accept("q1a", "E", None, ("g",), scope="member", obj="g"))
    q1 = ST.offer("q1", "C", "E", "member", "g", "group", ("w", "q1c", "q1a"), head=("w",), policy="community_invite", content="q1", room="g")
    q2c = in_room(ST.cosign("q2c", "B", "q2", ("q1",))); q2e = in_room(ST.cosign("q2e", "E", "q2", ("q1",))); q2a = in_room(ST.accept("q2a", "G", None, ("g",), scope="member", obj="g"))
    q2 = ST.offer("q2", "C", "G", "member", "g", "group", ("q1", "q2c", "q2e", "q2a"), head=("q1",), policy="community_invite", content="q2", room="g")
    line = [q1c, q1a, q1, q2c, q2e, q2a, q2]
    (m2_, s2_, t2_), bad = reader_view(pre + [hmc, hma, hm] + line); t.order(bad)
    t.fact("an honest counted admission (of F, on head w) signed offline, while two further counted rows were made without it: nothing is void; it waits as a tip, and the roster is the keys common to the tips: %s. "
           "The offline admission is not listed, and neither are the two members admitted meanwhile, until a counted row names both tips" % fs(m2_), not s2_ and m2_ == {"A", "B", "C"})
    mgc = [in_room(ST.cosign("mg%s" % k, k, "mg", ("q2", "hm"))) for k in "BC"]
    mga = in_room(ST.accept("mga", "H", None, ("g",), scope="member", obj="g"))
    mg = ST.offer("mg", "A", "H", "member", "g", "group", ("q2", "hm", "mgB", "mgC", "mga"), head=("q2", "hm"), policy="community_invite", content="mg", room="g")
    (m3_, s3_, t3_), bad = reader_view(pre + [hmc, hma, hm] + line + mgc + [mga, mg]); t.order(bad)
    t.fact("one counted row naming both tips, counted over the three keys common to them, makes one head and lists everyone both lines admitted: %s" % fs(m3_), m3_ == {"A", "B", "C", "E", "F", "G", "H"} and len(t3_) == 1)
    (m4_, s4_, t4_), bad = reader_view(pre + [hmc, hma, hm] + line + [RT.msg("mm", "A", "g", ("q2",)), RT.ack("kk", "B", "g", "mm", ("q2",))], own="B"); t.order(bad)
    t.fact("for a reader that had acknowledged the newer head, the offline admission is behind its line (void: %s) and its roster is %s: that reader and one with no acknowledgement differ (%s)"
           % ("hm" in s4_, fs(m4_), fs(m2_)), "hm" in s4_ and m4_ == {"A", "B", "C", "E", "G"})
    (m5_, s5_, t5_), bad = reader_view(pre + [hmc, hma, hm] + line + [RT.msg("mm", "A", "g", ("q2",)), RT.ack("kk", "B", "g", "mm", ("q2",))] + mgc + [mga, mg], own="B"); t.order(bad)
    t.fact("but for that reader the merge is built on a row behind its line, so the merge is void for it too (%s) and its roster stays %s: a reader whose acknowledgement outran a late honest row cannot take the merge that names it; "
           "the late row has to be signed again on the newer head" % (",".join(sorted(s5_)), fs(m5_)), {"hm", "mg"} <= s5_ and m5_ == {"A", "B", "C", "E", "G"})
    md2 = ST.offer("md2", "A", "B", "moderate", "g", "self", ("g",), cosigners=("B",), room="g")
    S = conc(pre + [md2] + line, ROUTE)
    t.fact("a row that states no head is untouched: an appointment made on the founding row still stands two counted rows later (B moderates: %s)" % ST.Seats(S).stands("B", "moderate", "g"),
           ST.Seats(S).stands("B", "moderate", "g"))
    base = room_rows(*ROOM)
    (ma, sa, ta), bad = reader_view(base + forged_line(2, "w")); t.order(bad)
    (mb, sb, tb), bad = reader_view(base + forged_line(2, "w"), checkpoint=True); t.order(bad)
    t.fact("THE REASON THE GROUP CHECKPOINT IS OFF. A past count (seated A with removed C) signs two rows from the head the newest honest row is counted over, the second over the first. As the rule stands: two tips, members %s, nothing stale. "
           "With Seats(..., checkpoint=True): the forged line is one row deeper, the honest removal is left behind (%s) and the members are %s: the removed key is back. That is a rank by depth of line"
           % (fs(ma), ",".join(sorted(sb)), fs(mb)), ma == {"A"} and not sa and "x" in sb and mb == {"A", "C", "F2"})
    gm = ST.offer("g", "m1", ("m1", "m2", "m3"), "member", "@", "self", cosigners=("m2", "m3"))
    md = ST.offer("md", "m1", "MOD", "moderate", "g", "self", ("g",), cosigners=("MOD",))
    Wm = WN.secs("moderation_fallback")
    pm = WN.opener("p", "m2", "moderation_fallback", "g", ("md",))
    An = WN.answer("A", "MOD", "p", "answered")                              # the moderator answers in time
    hostile = [gm, md, pm, An, WN.answer("x2", "m2", "p", "act"), WN.answer("x3", "m3", "p", "act"), WN.receipt("r", "m2", "p", 0), WN.landing("L", "m2", "p", "r", "fallback", Wm, ("x2", "x3"))]
    s1 = ST.offer("s1", "m2", "S1", "member", "g", "group", ("g", "p", "s1c"), head=("g",), policy="community_invite", content="s1", cosigners=("S1",))
    s2 = ST.offer("s2", "m2", "S2", "member", "g", "group", ("s1", "s2c", "s2d"), head=("s1",), policy="community_invite", content="s2", cosigners=("S2",))
    cps = [ST.cosign("s1c", "m3", "s1", ("g", "p")), s1, ST.cosign("s2c", "m3", "s2", ("s1",)), ST.cosign("s2d", "S1", "s2", ("s1",)), s2]
    off, bad = win(hostile + cps); t.order(bad)
    on, bad = win(hostile + cps, checkpoint=True); t.order(bad)
    t.fact("AND FOR WINDOWS. Two hostile members of three land the fallback over a moderator who answered in time, then sign two counted rows that leave the answer unnamed: as the rule stands %s; "
           "with outcome(..., checkpoint=True) %s: the count voids the one voice the window protects" % (off["recount"], on["recount"]), off["recount"] == "contested" and on["recount"] == "fallback")
    m = lambda s: sum(1 << int(c) for c in s)
    Wl = FK.world("M0", 5, m("0123"), m("3"), "majority")
    a1 = Wl.mk((0,), (), m("01234"), m("012")); a2 = Wl.mk((a1,), (), m("0124"), m("012"))
    side = Wl.mk((a1,), (), m("0123"), m("013"))                             # a sibling of the newest version
    S = frozenset([0, a1, a2, side])
    ra, rb, rc = cp_versions(Wl, S, ack=a2), cp_versions(Wl, S, ack=a1), cp_versions(Wl, S, ack=side)
    mg2 = Wl.mk((a2, side), (), m("0124"), m("012"))
    rm = [cp_versions(Wl, S | {mg2}, ack=x)[2] for x in (a2, a1, side)]
    t.fact("readers on one line with different latest acknowledgements, and one that acknowledged a sibling of the newest version, conclude the same while the siblings wait (%s, %s, %s) and the same once a version names both (%s)"
           % (FK.names(Wl, ra[2]), FK.names(Wl, rb[2]), FK.names(Wl, rc[2]), FK.names(Wl, rm[0])), ra[2] == rb[2] == rc[2] and rm[0] == rm[1] == rm[2] == m("0124"))
    W, S0, m = long_range()
    f1 = W.mk((0,), (), m("12"), m("12")); f2 = W.mk((f1,), (), m("12"), m("12"))
    r1, r2 = cp_versions(W, S0 | {f1, f2}, ack=max(S0))[2], cp_versions(W, S0 | {f1, f2}, ack=f2)[2]
    t.fact("two readers that acknowledged heads on DIFFERENT lines of an old-count fork disagree for good, holding the same rows (%s against %s): each line is its own reader's" % (FK.names(W, r1), FK.names(W, r2)), r1 != r2)
    return t.facts, t.bad


def run_one(n):
    """One test, by number, as a plain record (for a worker process)."""
    n, name, source, prop, f = next(x for x in TESTS if x[0] == n)
    t = Rec()
    t0 = time.time()
    COUNT.update(orders=0, differ=0, scenarios=0)
    d = f(t)
    d.update(n=n, name=name, source=source, prop=prop, facts=t.facts, notes=t.notes, order_differ=t.bad, secs=round(time.time() - t0, 1), count=dict(COUNT))
    return d


def run_all():
    return [run_one(n) for n in sorted(x[0] for x in TESTS)]
