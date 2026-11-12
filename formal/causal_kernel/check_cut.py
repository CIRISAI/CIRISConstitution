#!/usr/bin/env python3
"""
check_cut.py: test the CUT (cut.py) as one rule in place of `counts`, the slot decider and the window landing.

  1  order-freeness of the cut on generated worlds and on every witness world
  2  the counter-removal on the old head (finding 4b), with one-signature and two-voice versions
  3  what a later row can still change once a counting cut is kept, and who can do it
  4  W8, G1, W5, W11 under the cut
  5  re-admission after removal
  6  the price: honest rows the cut voids, and what an early or stale cut does
  C1 the landing of a window as a cut

  python3 -I check_cut.py     exit 0 when every run is order-free and the mutation is caught.
  Outcomes that differ from what was written down beforehand are printed, not failed.
"""
import itertools
import json
import multiprocessing
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import causal_kernel as CK  # noqa: E402
import check as BASE        # noqa: E402
import witnesses as WIT     # noqa: E402
from cut import Cut, cuts_of, on_slots  # noqa: E402

K, R = CK.K, CK.row
VOTES = ("votes", "prop")
G = R("g", "genesis", "admin", members=("admin", "co", "m", "u"))
POOLS = {
    "contest": [
        G,
        R("a", "claim", "m", ("g",), slot="s"),
        R("b", "claim", "u", ("g",), slot="s"),
        R("c", "decider", "admin", ("a", "b"), slot="s", picks="a"),
        R("d", "decider", "co", ("a", "b"), slot="s", picks="b"),        # another key that may decide
        R("c2", "decider", "admin", ("a", "b"), slot="s", picks="b"),    # the same key deciding twice
        R("cc", "decider", "co", ("a", "b"), slot="s", picks="a"),       # another key deciding the same way
        R("e2", "decider", "admin", ("c", "d"), slot="s", picks="a", rejects=("d",)),
        R("a2", "claim", "m", ("a",), slot="s"),                         # a later claim by a claimant
    ],
    "votes_and_removal": [
        G,
        R("prop", "proposal", "admin", ("g",)),
        R("vm", "vote", "m", ("prop",), choice="yes", on=(VOTES,)),
        R("vu", "vote", "u", ("prop",), choice="yes", on=(VOTES,)),
        R("vl", "vote", "co", ("prop",), choice="yes", on=(VOTES,)),
        R("land", "landing", "admin", ("prop", "vm"), cuts=(VOTES,), says="L1"),
        R("land2", "landing", "admin", ("prop", "vm", "vu"), cuts=(VOTES,), says="L2"),
        R("xa", "removal", "admin", ("g",), removes="m"),
        R("xb", "removal", "admin", ("vm",), removes="m"),
    ],
}
CUTTERS = ("admin", "co")


def rule(r, P, past, Cc=None):
    if r["kind"] in ("decider", "landing") and r["signer"] not in CUTTERS:
        return False
    return BASE.world_rule(r, P, past)


def landed(S, C):
    """The tally a counting landing carries: the voices among the votes in its own past."""
    out = {}
    for l in K.sel(S.Cs, kind="landing"):
        if C.counts(l):
            out[l["id"]] = K.group([S.by[n] for n in l["names"] if S.by[n]["kind"] == "vote"], None, "count", "signer")
    return out


def answers(S, wf=True):
    C = Cut(S, wf)
    out = {"status": C.all(), "slot:s": C.holder("s"), "slot:s2": C.holder("s2"), "landed": landed(S, C)}
    for pr in K.sel(S.Cs, kind="proposal"):
        out[("tally", pr["id"])] = CK.tally(S, pr, G["members"], counting=C.counts)
    return out


def renamed(rows, m):
    out = BASE.renamed_rows(rows, m)
    for q in out:
        if "rejects" in q:
            q["rejects"] = tuple(m[i] for i in q["rejects"])
    return out


ALL_POOLS = dict(POOLS, **BASE.POOLS)


def job(arg):
    name, idx, wf = arg
    pool = ALL_POOLS[name]
    rows = [pool[i] for i in idx]
    snap = lambda S: (frozenset(S.by), frozenset(S.C.items()), answers(S, wf))
    ref = snap(CK.concluded(CK.kept(rows), rule, BASE.ROOT))
    n = bad = 0
    for order in itertools.permutations(rows):
        n += 1
        bad += snap(CK.arrive(order, rule, BASE.ROOT)) != ref
    m = BASE.renaming(pool)
    twin = snap(CK.concluded(CK.kept(list(reversed(renamed(rows, m)))), rule, BASE.ROOT))
    return n, bad, int(twin != tuple(BASE.rename(x, m) for x in ref))


def order_check(bounds, wf=True):
    jobs = [(name, idx, wf) for name, b in bounds.items() for idx in BASE.subsets(range(len(ALL_POOLS[name])), b)]
    with multiprocessing.Pool() as mp:
        res = mp.map(job, jobs, chunksize=16)
    return len(jobs), sum(r[0] for r in res), sum(r[1] for r in res), sum(r[2] for r in res)


def witness_worlds():
    for c in WIT.CASES:
        yield c["id"], c["rows"], c["rule"]
        for v in c["variants"]:
            yield c["id"], v[1], c["rule"]
        for a in c["adversaries"]:
            yield c["id"], a[1], c["rule"]
            yield c["id"], a[2], c["rule"]


def run_orders(rows, rl, answer):
    seen = Counter()
    for order in itertools.permutations(rows):
        seen[json.dumps(answer(CK.arrive(order, rl)), sort_keys=True, default=sorted)] += 1
    return sum(seen.values()), len(seen), answer(CK.concluded(CK.kept(rows), rl))


# ---- 3. what can still change after a counting cut ------------------------------------------------------------
class World:
    def __init__(self, pool):
        self.pool, self.cache = pool, {}

    def at(self, rows):
        key = frozenset(r["id"] for r in rows)
        if key not in self.cache:
            S = CK.concluded(CK.kept(list(rows)), rule, BASE.ROOT)
            self.cache[key] = (S, Cut(S), answers(S), BASE.answers(S))
        return self.cache[key]


def who(S1, C1, S2, new, slots, also=()):
    """Who signed the new cut on these slots: the key of a cut already counting there, another key, or no cut at all."""
    slots = set(slots)
    cutters = {x["signer"] for x in C1.cuts if x["id"] in C1.L and slots & cuts_of(x)}
    fresh = [S2.by[i] for i in new if slots & cuts_of(S2.by[i])]
    if not fresh and any(set(also) & cuts_of(S2.by[i]) for i in new):
        return "a first cut on another slot the row is on"
    if not fresh:
        return "a row that is not a cut on it"
    return "the key that cut it" if any(x["signer"] in cutters for x in fresh) else "another key that may cut it"


def after_cut(pools, bound):
    c = Counter()
    for kind in ("... after a counting cut on it", "... on a slot already cut"):
        for by in ("the key that cut it", "another key that may cut it", "a row that is not a cut on it"):
            c["cut: %s, by %s" % (kind, by)] = 0
    for pool in pools:
        W = World(pool)
        for rows in BASE.subsets(pool, bound):
            have = {r["id"] for r in rows}
            for x in pool:
                if x["id"] in have:
                    continue
                (S1, C1, A1, B1), (S2, C2, A2, B2) = W.at(rows), W.at(rows + (x,))
                new = set(S2.by) - set(S1.by)
                c["steps"] += 1
                for s in ("s", "s2"):
                    held = A1["slot:" + s] not in ("empty", "conflict")
                    cut_there = any(x_["id"] in C1.L and s in cuts_of(x_) for x_ in C1.cuts)
                    base_held = B1["slot:" + s][1] == 1
                    c["base: held slot emptied or changed"] += base_held and B2["slot:" + s] != B1["slot:" + s]
                    if held and A2["slot:" + s] != A1["slot:" + s]:
                        c["cut: held slot emptied or changed"] += 1
                        if cut_there:
                            c["cut: ... after a counting cut on it, by " + who(S1, C1, S2, new, [s])] += 1
                for i, st in A1["status"].items():
                    r = S1.by[i]
                    c["base: row stopped counting"] += i in B1["counts"] and i not in B2["counts"]
                    if st == "counts" and A2["status"][i] != "counts":
                        c["cut: row stopped counting"] += 1
                        hit = [s for s in on_slots(r) | cuts_of(r) if any(y["id"] in C1.L and s in cuts_of(y) for y in C1.cuts)]
                        if hit:
                            c["cut: ... on a slot already cut, by " + who(S1, C1, S2, new, hit, on_slots(r) | cuts_of(r))] += 1
                    if st == "void" and A2["status"][i] != "void":
                        c["cut: a void row came back (to %s)" % A2["status"][i]] += 1
                for k in A1:
                    if isinstance(k, tuple):
                        c["base: open tally fell"] += B2[k] < B1[k]
                        c["cut: open tally fell"] += A2[k] < A1[k]
                for l, n in A1["landed"].items():
                    if A2["landed"].get(l) != n:
                        c["cut: a landed tally was lost, by " + who(S1, C1, S2, new, [VOTES])] += 1
                    else:
                        c["cut: landed tallies that stayed"] += 1
                # the price: rows that count under Causal.counts and not under the cut, and the reverse
                if not c.get(("seen", frozenset(S1.by))):
                    c[("seen", frozenset(S1.by))] = 1
                    for i, st in A1["status"].items():
                        base = i in B1["counts"]
                        c["sets x rows: counts under `counts`, not under the cut"] += base and st != "counts"
                        c["sets x rows: counts under the cut, not under `counts`"] += (not base) and st == "counts"
                        c["sets x rows: counts under both"] += base and st == "counts"
    return {k: v for k, v in c.items() if isinstance(k, str)}


# ---- scenarios -------------------------------------------------------------------------------------------------
def ros_rule(r, P, past):
    if r["kind"] == "roster" and r["names"]:
        mem = WIT.members_of(P)
        v = [q for q in K.sel(P, kind="cosign") if q["id"] in r["names"] and q["signer"] in mem
             and q.get("of") == r.get("content")] + [r]
        return r["signer"] in mem and K.group(v, None, "count", "signer") >= r.get("need", 1)
    return True


def ros_ans(S):
    C = Cut(S)
    g = [q for q in K.sel(S.Cs, kind="roster") if not q["names"]][0]
    keys = {k[1] for x in C.cuts for k in cuts_of(x) if k[0] == "key"}
    out = {k for k in keys if any(x["id"] in C.L and ("key", k) in cuts_of(x) for x in C.cuts)}
    doubt = {k for k in keys - out if any(x["id"] in C.U and ("key", k) in cuts_of(x) for x in C.cuts)}
    return {"members": sorted(set(g["members"]) - out), "contested": sorted(doubt),
            "versions": {v["id"]: C.status(v) for v in K.sel(S.rows, kind="roster") if v["names"]},
            "members_under_Causal.counts": WIT.w7_ans(S)["members"]
            if not any("cuts" in v for v in S.rows) else "not comparable: a version here cuts two keys"}


h0 = R("h0", "roster", "f1", members=("f1", "f2", "m3"), protocol="one")
v1 = R("v1", "roster", "f1", ("h0",), change={"drop": ("m3",)}, removes="m3")
v3 = R("v3", "roster", "m3", ("h0",), change={"drop": ("f1",)}, removes="f1")
v5 = R("v5", "roster", "f2", ("v1", "v3"), change={"drop": ("m3",)}, removes="m3", rejects=("v3",))
v6 = R("v6", "roster", "m3", ("h0",), change={"drop": ("f2",)}, removes="f2")
v3all = R("v3", "roster", "m3", ("h0",), change={"drop": ("f1", "f2")}, cuts=(("key", "f1"), ("key", "f2")), says="out")
cs = R("cs", "cosign", "f2", ("h0",), of="drop m3")
v1c = R("v1", "roster", "f1", ("h0", "cs"), change={"drop": ("m3",)}, removes="m3", content="drop m3")
v1q = dict(v1c, need=2)
v3q = R("v3", "roster", "m3", ("h0",), change={"drop": ("f1",)}, removes="f1", need=2, content="drop f1")
cs2 = R("cs2", "cosign", "f2", ("h0",), of="drop f1")
v3qq = dict(v3q, names=("h0", "cs2"))

FATE = ("fate", "dec")
dec = WIT.dec
frz = R("frz", "frozen", "agent", ("dec",), on=(FATE,), says="frozen")
wdr = R("wd", "withdraw", "agent", ("dec",), target="dec", on=(FATE,), says="withdrawn")
dz = R("dz", "decider", "custodian", ("frz", "wd"), picks="frz", cuts=(FATE,))
dz2 = R("dz2", "decider", "agent", ("frz", "wd"), picks="wd", cuts=(FATE,))
cust = R("cust", "custody", "agent", ("frz", "wd"), cuts=(("key", "agent"),), says="out")
dzc = R("dz", "decider", "custodian", ("cust", "frz", "wd"), picks="frz", cuts=(FATE,))
cust0 = R("cust", "custody", "agent", ("dec",), cuts=(("key", "agent"),), says="out")


def w8_rule(r, P, past):
    if r["signer"] == "agent" and K.sel(P, kind="custody"):
        return False                       # the agent has no standing at a head that names its handover
    return WIT.w8_rule(r, P, past)


def w8_ans(S):
    C = Cut(S)
    return {"fate": C.holder(FATE), "status": {i: s for i, s in C.all().items() if i != "dec"}}


SUCC = ("successor", "r")
sup = R("sup", "replace", "K1", ("r",), target="r", cuts=(SUCC,))
sup2 = R("sup2", "replace", "K1", ("r",), target="r", cuts=(SUCC,))
sup3 = R("sup3", "replace", "K1", ("r", "sup", "sup2"), target="r", cuts=(SUCC,), picks="sup")
sup4 = R("sup4", "replace", "K1", ("r", "sup", "sup2"), target="r", cuts=(SUCC,), picks="sup2")
supX = R("supX", "replace", "K2", ("r",), target="r", cuts=(SUCC,))
g1_ans = lambda S: {"successor": Cut(S).holder(SUCC, value=lambda r: r["id"])}

REPLY = ("reply", "p")
a_ = dict(WIT.a, on=(REPLY,), says="accept")
d_ = dict(WIT.d, on=(REPLY,), says="decline")
w_ = dict(WIT.w, cuts=(REPLY,), says="accept")
d_cut = dict(WIT.d, cuts=(REPLY,), says="decline")


def w5_ans(S):
    C = Cut(S)
    w = S.by.get("w")
    return {"reply": C.holder(REPLY), "decline": C.status(S.by["d"]),
            "K": "seated" if w and C.counts(w) else "not seated"}


TR = ("transport", "N")
rep = R("rep", "transport", "N", ("t0",), target="t0", cuts=(TR,), says="rep")
seat_old = R("seat", "confers", "root", ("t0",), to="N", cuts=(TR,), says="t0")
seat_new = R("seat", "confers", "root", ("rep",), to="N", cuts=(TR,), says="rep")
rb = R("rb", "rebind", "holders", ("seat", "rep"), node="N", transport="rep", cuts=(TR,), says="rep")
w11_ans = lambda S: {"in_force": Cut(S).holder(TR)}

a2x = R("a2", "acceptance", "K", ("p2", "x"), ref="p2", target="p2")
w4x = R("w4", "widening", "founder", ("a2", "x"), subject="K", target="p2")
nK = R("nK", "note", "K", ("w4",))
nOld = R("nOld", "note", "K", ("w",))


def readmit_ans(S):
    C = Cut(S)
    return {"seat": WIT.seat(S, "K"), "status": {i: C.status(S.by[i]) for i in ("a2", "w4", "nK", "nOld") if i in S.by},
            "nK_under_Causal.counts": CK.counts(S, S.by["nK"]) if "nK" in S.by else None}


EV = ("votes", "e")
landK = R("land", "landing", "K1", ("e",), cuts=(EV,), says="landed")
xo = R("x", "note", "K2", ("ros", "e"), on=(EV,))
xo_cut = R("x", "note", "K2", ("ros", "e"), cuts=(EV,), says="cancelled")


def c1_rule(r, P, past):
    if r["kind"] == "landing":
        e = K.sel(P, kind="evict")
        return bool(e) and r["signer"] == e[0]["signer"] and not K.sel(P, signer=e[0]["removes"], kind="note")
    return WIT.c1_rule(r, P, past)


def c1_ans(S):
    C = Cut(S)
    out = {"window": C.holder(EV)}
    if "x" in S.by:
        out["objection"] = C.status(S.by["x"])
    return out


hv = R("hv", "vote", "f2", ("h0",), on=(("room",),))
v1room = R("v1", "roster", "f1", ("h0",), change={"drop": ("m3",)}, removes="m3", cuts=(("room",),), says="v1")
pool_b = {r["id"]: r for r in POOLS["votes_and_removal"]}
pool_a = {r["id"]: r for r in POOLS["contest"]}
pick = lambda P, ids: [P[i] for i in ids]
status_ans = lambda S: Cut(S).all()
votes_ans = lambda S: (lambda C: {"status": {i: s for i, s in C.all().items() if i[0] == "v"}, "landed": landed(S, C),
                                  "open_tally": CK.tally(S, S.by["prop"], G["members"], counting=C.counts)})(Cut(S))

SCEN = [
    # (section, name, rows, rule, answer, what was written down beforehand)
    ("2", "one signature: removal, then the removed member's counter-removal on the old head", [h0, v1, v3], ros_rule, ros_ans,
     {"members": ["f1", "f2", "m3"], "contested": ["f1", "m3"], "versions": {"v1": "contested", "v3": "contested"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),
    ("2", "... then the third member names both, removes m3 and rejects the counter-removal", [h0, v1, v3, v5], ros_rule, ros_ans,
     {"members": ["f1", "f2"], "contested": [], "versions": {"v1": "counts", "v3": "void", "v5": "counts"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),   # written wrongly: see the run
    ("2", "... then m3 signs, on the old head, a removal of that third member", [h0, v1, v3, v5, v6], ros_rule, ros_ans,
     {"members": ["f1", "f2", "m3"], "contested": ["f1", "f2", "m3"], "versions": {"v1": "contested", "v3": "contested", "v5": "contested", "v6": "contested"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),
    ("2", "one signature needed, but the removal carries a second voice; the counter-removal names only the signer", [h0, cs, v1c, v3], ros_rule, ros_ans,
     {"members": ["f1", "f2"], "contested": [], "versions": {"v1": "counts", "v3": "void"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),
    ("2", "... and the counter-removal removes both voices", [h0, cs, v1c, v3all], ros_rule, ros_ans,
     {"members": ["f1", "f2", "m3"], "contested": ["f1", "f2", "m3"], "versions": {"v1": "contested", "v3": "contested"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),
    ("2", "two voices needed: the removed member's counter-removal alone", [h0, cs, v1q, v3q], ros_rule, ros_ans,
     {"members": ["f1", "f2"], "contested": [], "versions": {"v1": "counts", "v3": "concludes nothing"}, "members_under_Causal.counts": ["f1", "f2"]}),
    ("2", "two voices needed: the removed member and a cosigner who signs both ways (a quorum of the old roster)", [h0, cs, v1q, cs2, v3qq], ros_rule, ros_ans,
     {"members": ["f1", "f2", "m3"], "contested": ["f1", "m3"], "versions": {"v1": "contested", "v3": "contested"}, "members_under_Causal.counts": ["f1", "f2", "m3"]}),

    ("4", "W8: a deciding row by the custodian", [dec, frz, wdr, dz], w8_rule, w8_ans,
     {"fate": "frozen", "status": {"frz": "counts", "wd": "counts", "dz": "counts"}}),
    ("4", "W8: then the agent decides the other way, not naming the first decision", [dec, frz, wdr, dz, dz2], w8_rule, w8_ans,
     {"fate": "conflict", "status": {"frz": "counts", "wd": "counts", "dz": "contested", "dz2": "contested"}}),
    ("4", "W8: the handover to the custodian is itself a cut on the agent's key and names both rows; then the same attempt",
     [dec, frz, wdr, cust, dzc, dz2], w8_rule, w8_ans,
     {"fate": "frozen", "status": {"frz": "counts", "wd": "counts", "cust": "counts", "dz": "counts", "dz2": "void"}}),
    ("4", "G1: two replacements by one signer, each a cut on the successor", [WIT.r0, sup, sup2], WIT.g1_rule, g1_ans, {"successor": "conflict"}),
    ("4", "G1: a third names both and picks", [WIT.r0, sup, sup2, sup3], WIT.g1_rule, g1_ans, {"successor": "sup"}),
    ("4", "G1: then a fourth by the same signer names both, not the third, and picks the other", [WIT.r0, sup, sup2, sup3, sup4], WIT.g1_rule, g1_ans, {"successor": "conflict"}),
    ("4", "G1: another key signs a replacement", [WIT.r0, sup, supX], WIT.g1_rule, g1_ans, {"successor": "sup"}),
    ("4", "W5: only the widening is a cut on the reply; it does not name the decline", [WIT.p, a_, d_, w_], WIT.mem_rule, w5_ans,
     {"reply": "accept", "decline": "void", "K": "seated"}),
    ("4", "W5: K's decline is a cut on the reply as well", [WIT.p, a_, d_cut, w_], WIT.mem_rule, w5_ans,
     {"reply": "conflict", "decline": "contested", "K": "not seated"}),
    ("4", "W11: the seating names the old pair, the node had replaced it; both are cuts on the node's transport", [WIT.t0, rep, seat_old], WIT.w11_rule, w11_ans, {"in_force": "conflict"}),
    ("4", "W11: the seating names the pair the node now uses", [WIT.t0, rep, seat_new], WIT.w11_rule, w11_ans, {"in_force": "rep"}),
    ("4", "W11: after the conflict the holders' rebind names both", [WIT.t0, rep, seat_old, rb], WIT.w11_rule, w11_ans, {"in_force": "rep"}),

    ("5", "removed, re-admitted on a new acceptance that names the removal, then a new row by the key",
     [WIT.p, WIT.a, WIT.w, WIT.x, WIT.p2, a2x, w4x, nK], WIT.mem_rule, readmit_ans,
     {"seat": "in", "status": {"a2": "counts", "w4": "counts", "nK": "counts"}, "nK_under_Causal.counts": False}),
    ("5", "the same, and a row of the key that names only the first seating (signed before the removal or as if)",
     [WIT.p, WIT.a, WIT.w, WIT.x, WIT.p2, a2x, w4x, nOld], WIT.mem_rule, readmit_ans,
     {"seat": "in", "status": {"a2": "counts", "w4": "counts", "nOld": "void"}, "nK_under_Causal.counts": None}),
    ("5", "the new acceptance does not name the removal", [WIT.p, WIT.a, WIT.w, WIT.x, WIT.p2, WIT.a2, WIT.w4], WIT.mem_rule, readmit_ans,
     {"seat": "in", "status": {"a2": "void", "w4": "counts"}, "nK_under_Causal.counts": None}),

    ("6", "price: an honest vote signed before a removal that names the old head", pick(pool_b, ["g", "prop", "vm", "xa"]), rule, votes_ans,
     {"status": {"vm": "void"}, "landed": {}, "open_tally": 0}),
    ("6", "price: a landing signed early; one honest vote is not in its past", pick(pool_b, ["g", "prop", "vm", "vu", "land"]), rule, votes_ans,
     {"status": {"vm": "counts", "vu": "void"}, "landed": {"land": 1}, "open_tally": 1}),
    ("6", "price: the same key lands twice with different pasts", pick(pool_b, ["g", "prop", "vm", "vu", "land", "land2"]), rule, votes_ans,
     {"status": {"vm": "counts", "vu": "counts"}, "landed": {}, "open_tally": 2}),
    ("6", "price: a roster version taken as a cut on the whole room voids a concurrent honest vote", [h0, hv, v1room], ros_rule, status_ans,
     {"h0": "counts", "hv": "void", "v1": "counts"}),
    ("6", "price: a claimant's later claim, concurrent with the decision", pick(pool_a, ["g", "a", "b", "c", "a2"]), rule, status_ans,
     {"g": "counts", "a": "counts", "b": "counts", "c": "counts", "a2": "void"}),
    ("6", "stale head: the handover names only the decision, so the agent's own earlier rows are void", [dec, frz, wdr, cust0], w8_rule, w8_ans,
     {"fate": "empty", "status": {"frz": "void", "wd": "void", "cust": "counts"}}),

    ("C1", "the proposer signs a landing; no objection held", [WIT.ros, WIT.ev, landK], c1_rule, c1_ans, {"window": "landed"}),
    ("C1", "cut early: the target's objection exists and the landing does not name it", [WIT.ros, WIT.ev, xo, landK], c1_rule, c1_ans,
     {"window": "landed", "objection": "void"}),
    ("C1", "the objection is itself a cut on the window", [WIT.ros, WIT.ev, xo_cut, landK], c1_rule, c1_ans,
     {"window": "conflict", "objection": "contested"}),
]


def main():
    ok = True
    say = lambda *a: print(*a, flush=True)
    res = {}
    say("1. order-freeness of the cut")
    bounds = {"contest": 6, "votes_and_removal": 6, "slots_and_kinds": 5, "removal_reach_tally": 5}
    sets, orders, bad, sym = order_check(bounds)
    res["order"] = dict(sets=sets, orders=orders, differing=bad, renaming=sym, bounds=bounds)
    say("   generated worlds: %d sets, %d arrival orders, %d differ from the set function, %d sets changed by renaming the digests"
        % (sets, orders, bad, sym))
    ok &= bad == 0 and sym == 0
    ms, mo, mbad, _ = order_check({"contest": 5}, wf=False)
    say("   mutation, cuts judged one at a time in list order: %s (%d of %d orders differ)" % ("caught" if mbad else "NOT CAUGHT", mbad, mo))
    ok &= mbad > 0
    n = worlds = wbad = 0
    for cid, rows, rl in witness_worlds():
        o, distinct, _ = run_orders(rows, rl, status_ans)
        n, worlds, wbad = n + o, worlds + 1, wbad + (distinct != 1)
    res["witness_worlds"] = dict(worlds=worlds, orders=n, order_dependent=wbad)
    say("   witness worlds (rows as encoded for check.py; removals and deciding rows read as cuts): %d worlds, %d orders, %d order dependent"
        % (worlds, n, wbad))
    ok &= wbad == 0

    say("2, 4, 5, 6, C1. scenarios, every arrival order")
    res["scenarios"] = []
    sec = None
    for s, name, rows, rl, ans, expected in SCEN:
        o, distinct, got = run_orders(rows, rl, ans)
        ok &= distinct == 1
        same = json.dumps(got, sort_keys=True, default=sorted) == json.dumps(expected, sort_keys=True, default=sorted)
        res["scenarios"].append(dict(section=s, name=name, orders=o, distinct=distinct, result=got, as_written_beforehand=same,
                                     written_beforehand=expected))
        if s != sec:
            sec = s
            say("   [%s]" % s)
        say("   %s\n        orders=%d distinct=%d %s\n        -> %s" % (
            name, o, distinct, "" if same else "NOT AS WRITTEN BEFOREHAND (%s)" % json.dumps(expected, sort_keys=True, default=sorted),
            json.dumps(got, sort_keys=True, default=sorted)))

    say("3. what a later row still changes (every set of up to 6 rows and one more row)")
    for label, pools in (("the two pools of check.py", list(BASE.POOLS.values())), ("the two cut pools", list(POOLS.values()))):
        c = after_cut(pools, 6)
        res["after_cut: " + label] = c
        say("   %s: %d steps" % (label, c.pop("steps")))
        for k in sorted(c):
            say("      %-78s %d" % (k, c[k]))
    with open(os.path.join(os.environ.get("HANDOFF_TMP", "/tmp"), "results_cut.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=sorted)
    say("RESULT: %s" % ("ok" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
