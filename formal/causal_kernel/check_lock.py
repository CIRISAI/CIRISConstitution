#!/usr/bin/env python3
"""
check_lock.py: one command, exit 0 or 1.

  0  the library: closure against a hand-written definition; the two traps; sum
  1  seat     order-freeness over every arrival order of generated small worlds, a mutation that must be caught,
              and every row of role_shapes.tsv run as an instance
  2  window   order-freeness, a mutation, and the adversary table under the three rules
  3  route    order-freeness, a mutation, sufficiency, minimality, the stranger, the sizes
  4  key plane  the rows-only fold against the original on every sequence the original runs

  python3 -I check_lock.py            three worker processes and this one; each is capped at 2 GiB of address space
  python3 -I check_lock.py --base     also runs the copied causal_kernel checks (bound 5) and the library agreement run

Bounds (stated again in the output): every subset of up to SMALL rows of each pool, and every subset of up to BIG
rows that is closed under what its rows name (a set that is not closed only adds rows that wait at the door, which
formal/causal_kernel/check.py covers). Each set is run in every arrival order.
"""
import itertools
import json
import multiprocessing
import os
import random
import resource
import subprocess
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import seat as ST       # noqa: E402
import window as WN     # noqa: E402
import route as RT      # noqa: E402
import roles as RL      # noqa: E402
import keyplane as KP   # noqa: E402

CK, K, R = ST.CK, ST.K, ST.R
PROCS = 3
SMALL = 4
BIG = {"seat": 7, "window": 7, "route": 6}


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


# ---- the pools ---------------------------------------------------------------------------------------------
def seat_pool():
    g = ST.offer("g", "f1", ("f1", "f2", "f3"), "founder", "@", "self", cosigners=("f2", "f3"))
    return [
        g,
        ST.accept("am", "m", None, ("g",), scope="member", obj="g"),
        ST.cosign("c2", "f2", "w", ("g",)),
        ST.offer("w", "f1", "m", "member", "g", "group", ("g", "am", "c2"), head=("g",), policy="community_invite", content="w"),
        ST.offer("w1", "f1", "m", "member", "g", "group", ("g", "am"), head=("g",), policy="community_invite", content="w1"),   # one voice
        ST.offer("d", "f1", "K", "moderate", "g", "seat", ("g",), under="g", sub=True),
        ST.accept("ak", "K", "d"),
        ST.offer("d2", "K", "J", "moderate:spam", "g", "seat", ("ak",), under="d", cosigners=("J",)),
        ST.withdraw("wd", "f1", "d"),
        ST.withdraw("wk", "K", "d", ("ak",)),
        ST.withdraw("wz", "m", "d"),                                   # a third party
        ST.cosign("x2", "f2", "x", ("w",)),
        ST.cosign("x3", "f3", "x", ("w",)),
        ST.unseat("x", "f1", "m", "member", "g", "group", ("w", "x2", "x3"), head=("w",), policy="community_remove", content="x"),
        ST.accept("am2", "m", None, ("g",), scope="member", obj="g"),  # concurrent with the removal
        ST.offer("w2", "f1", "m", "member", "g", "group", ("g", "am2", "c2"), head=("g",), policy="community_invite", content="w"),
    ]


def window_pools():
    out = {}
    for world, pick in ((WN.self_world, (0, 3, 5, 7)), (WN.moderation_world, (0, 4, 5, 6)), (WN.halt_world, (2, 3, 5, 6))):
        title, cases = world()
        pool, seen = [], {}
        for i in pick:
            m = {}                                  # a row of this case whose id another case used for another row is renamed,
            for r in cases[i][1]:                   # and the rows of this case that name it follow
                r = dict(r, names=tuple(m.get(x, x) for x in r["names"]))
                if r.get("receipt") in m: r["receipt"] = m[r["receipt"]]
                key = json.dumps(r, sort_keys=True, default=list)
                if key in seen: continue
                rid = r["id"]
                while any(q["id"] == rid for q in pool): rid += "'"
                if rid != r["id"]: m[r["id"]] = rid
                seen[key] = rid
                pool.append(dict(r, id=rid))
        out[title.split(",")[0].split(" (")[0]] = pool
    return out


def route_pool():
    keep = ("g", "md", "ac", "cb", "w", "m1", "k1", "m2", "xc", "x", "m4", "m5")
    return [r for r in RT.world() if r["id"] in keep] + [RT.REPLY]


POOLS = {"seat": {"room": seat_pool()}, "window": window_pools(), "route": {"room": route_pool()}}
RULES = {"seat": ST.seat_rule, "window": WN.rule, "route": RT.rule}


def snap(kind, S, mutate):
    base = (frozenset(S.by), frozenset(S.C.items()))
    if kind == "seat":
        return base + (ST.Seats(S, by_arrival=mutate).snapshot(),)
    if kind == "window":
        return base + (tuple(sorted(WN.outcomes(S, "p", by_arrival=mutate).items())),)
    return base + (tuple(sorted(RT.route_sets(S, "closed", by_arrival=mutate).items())),)


def closed_sets(pool, lo, hi):
    """The subsets of size lo..hi closed under what their rows name."""
    ids = {r["id"]: i for i, r in enumerate(pool)}
    need = [frozenset(ids[n] for n in r["names"] if n in ids) if all(n in ids for n in r["names"]) else None for r in pool]
    out = []
    def grow(cur, start):
        if lo <= len(cur) <= hi: out.append(tuple(sorted(cur)))
        if len(cur) == hi: return
        for i in range(start, len(pool)):
            grow(cur | {i}, i + 1)
    grow(frozenset(), 0)
    return [c for c in out if all(need[i] is not None and need[i] <= set(c) for i in c)]


def jobs_for(kind, mutate=False, cap=None):
    out = []
    for name, pool in POOLS[kind].items():
        sets = [idx for n in range(1, SMALL + 1) for idx in itertools.combinations(range(len(pool)), n)]
        sets += closed_sets(pool, SMALL + 1, BIG[kind])
        if cap: sets = [s for s in sets if len(s) >= SMALL][-cap:]
        out += [(kind, name, idx, mutate) for idx in sets]
    return out


def order_job(job):
    """Every arrival order of one set. The conclusion rule is a function of the row and its concluded ancestors and
    the derived answers are a function of the kept rows in the order held; both are computed once per distinct input."""
    kind, name, idx, mutate = job
    rows = [POOLS[kind][name][i] for i in idx]
    memo = {}
    def rule(r, P, past):
        key = (r["id"], frozenset(q["id"] for q in P))
        if key not in memo: memo[key] = RULES[kind](r, P, past)
        return memo[key]
    ref = snap(kind, CK.concluded(CK.kept(rows), rule), mutate)
    seen, n, bad = {}, 0, 0
    for order in itertools.permutations(rows):
        S = CK.arrive(order, rule)
        key = tuple(r["id"] for r in S.rows)
        if key not in seen: seen[key] = snap(kind, S, mutate)
        n += 1
        bad += seen[key] != ref
    return n, bad, len(seen)


def order_check(mp, kind, mutate=False, cap=None):
    jobs = jobs_for(kind, mutate, cap)
    res = mp.map(order_job, jobs, chunksize=8)
    return {"sets": len(jobs), "orders": sum(r[0] for r in res), "differ": sum(r[1] for r in res), "held_orders": sum(r[2] for r in res)}


# ---- 0. the library ----------------------------------------------------------------------------------------
def library():
    rnd, n, bad = random.Random(7), 0, 0
    for _ in range(400):
        size = rnd.randint(1, 9)
        rows = [{"id": i, "names": tuple(sorted(rnd.sample(range(i), rnd.randint(0, min(i, 3)))))} for i in range(size)]
        by = {r["id"]: r for r in rows}
        def up(i):
            out, todo = set(), list(by[i]["names"])
            while todo:
                x = todo.pop()
                if x not in out: out.add(x); todo += by[x]["names"]
            return frozenset(out)
        anc = K.closure(rows)
        for r in rows:
            n += 1; bad += anc[r["id"]] != up(r["id"])
        pick = rnd.sample(rows, rnd.randint(1, size))
        n += 1; bad += {r["id"] for r in K.frontier(anc, pick)} != {r["id"] for r in pick if not any(r["id"] in up(q["id"]) for q in pick)}
        for a in rows:
            for b in rows:
                n += 1; bad += K.concurrent(anc, a["id"], b["id"]) != (a != b and a["id"] not in up(b["id"]) and b["id"] not in up(a["id"]))
    x, y = {"id": "x", "l": 1, "w": 2}, {"id": "y", "l": 1, "w": 5}
    def tie():
        try: K.group([x, y], None, "greatest", "l"); return False
        except K.Tie: return True
    traps = {
        "a tie between two rows is refused": tie(),
        "the same row twice is not a tie": K.group([x, dict(x)], None, "least", "l") == x,
        "max is a function of the set": K.group([x, y], None, "max", "l") == K.group([y, x], None, "max", "l") == 1,
        "sel does not match an absent field against None": K.sel([{"id": "x"}], removes=None) == [] and len(K.sel([{"id": "x", "removes": None}], removes=None)) == 1,
        "sum over distinct rows": K.group([x, y, dict(y)], None, "sum", "w") == 7,
        "sum: a voice with two values adds nothing": K.group([x, y, {"id": "y", "w": 6}], None, "sum", "w") == 2,
        "sum of nothing is 0": K.group([], None, "sum", "w") == 0,
        "sum by group": K.group([dict(x, g="a"), dict(y, g="b")], "g", "sum", "w") == {"a": 2, "b": 5},
    }
    return n, bad, traps


def run_base(say):
    ok = True
    for label, cmd in (("causal_kernel/check.py --bound 5", ["formal/causal_kernel/check.py", "--bound", "5"]),
                       ("causal_kernel/check_cut.py", ["formal/causal_kernel/check_cut.py"]),
                       ("kernel_lib/kernel_lib_check.py --check", ["formal/kernel_lib/kernel_lib_check.py", "--check"])):
        t = time.time()
        p = subprocess.run([sys.executable, "-I"] + cmd, cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, HANDOFF_TMP=os.environ.get("HANDOFF_TMP", "/tmp")))
        tail = [l for l in p.stdout.strip().splitlines() if l.strip()][-1] if p.stdout.strip() else ""
        say("   %-42s exit %d in %.0fs  %s" % (label, p.returncode, time.time() - t, tail[:70]))
        ok &= p.returncode == 0
    return ok


def main():
    t0 = time.time()
    ok = True
    def say(s):
        print(s, flush=True)
    def need(cond, what):
        nonlocal ok
        if not cond:
            ok = False
            say("   FAIL: " + what)

    say("0. the library (closure over what rows name; the two traps; sum)")
    n, bad, traps = library()
    say("   ancestors, concurrent and frontier against a hand-written definition: %d comparisons, %d differ" % (n, bad))
    for k, v in traps.items(): say("   %-52s %s" % (k, v))
    need(bad == 0 and all(traps.values()), "the library")
    if "--base" in sys.argv:
        say("   the copied checks, run on this library:")
        need(run_base(say), "a copied check failed")

    with multiprocessing.Pool(PROCS, initializer=_limit) as mp:
        say("1. seat")
        r = order_check(mp, "seat")
        say("   order-freeness: a pool of %d rows, every subset of up to %d and every closed subset of up to %d: %d sets, %d arrival orders "
            "(%d distinct held orders), %d differ from the set function" % (len(POOLS["seat"]["room"]), SMALL, BIG["seat"], r["sets"], r["orders"], r["held_orders"], r["differ"]))
        need(r["differ"] == 0 and r["orders"] > 0, "seat answers depend on the arrival order")
        m = order_check(mp, "seat", mutate=True)
        say("   mutation, a withdrawal or an unseat judged by when it was held (list position, not what it names): %s (%d of %d orders differ)" % (
            "caught" if m["differ"] else "NOT CAUGHT", m["differ"], m["orders"]))
        need(m["differ"] > 0, "the seat mutation was not caught")
        table, out, problems, tokens = RL.run_all()
        sm = RL.summary(table, tokens)
        say("   role_shapes.tsv: %d rows for %d tokens; %d instance checks run, %d fail; %d endings are a lapse (a window, counted not run)" % (
            len(table), len(tokens), sum(o[2] for o in out), sum(len(o[1]) for o in out), sum(o[3] for o in out if o[0]["shape"] == "seat")))
        say("   shapes used: %s; conferrer kinds: %s" % (", ".join(sm["shapes"]), ", ".join(sm["conferrers"])))
        say("   rows that fit: yes %d, partly %d, no %d" % (sm["fits_rows"]["yes"], sm["fits_rows"]["partly"], sm["fits_rows"]["no"]))
        say("   tokens by first way: " + "; ".join("%s %d" % (s, len(v)) for s, v in sm["tokens_by_first_shape"].items()))
        say("   tokens whose best way fits: yes %d, partly %d, no %d (%s)" % (len(sm["tokens_best"]["yes"]), len(sm["tokens_best"]["partly"]),
            len(sm["tokens_best"]["no"]), ", ".join(sm["tokens_best"]["no"])))
        for k, v in sm["same_parameters"].items(): say("   same parameters [%s]: %s" % (k, ", ".join(v)))
        for p in problems: say("   FAIL: " + p)
        need(not problems, "the role table")

        say("2. window")
        r = order_check(mp, "window")
        say("   order-freeness: %d pools (%s rows), every subset of up to %d and every closed subset of up to %d: %d sets, %d arrival orders "
            "(%d distinct held orders), %d differ" % (len(POOLS["window"]), "/".join(str(len(p)) for p in POOLS["window"].values()), SMALL, BIG["window"],
                                                      r["sets"], r["orders"], r["held_orders"], r["differ"]))
        need(r["differ"] == 0 and r["orders"] > 0, "window answers depend on the arrival order")
        m = order_check(mp, "window", mutate=True)
        say("   mutation, 'concurrent with the landing' read as 'arrived after it': %s (%d of %d orders differ)" % (
            "caught" if m["differ"] else "NOT CAUGHT", m["differ"], m["orders"]))
        need(m["differ"] > 0, "the window mutation was not caught")
        adv = WN.adversary_table()
        last = None
        broken = {h: [] for h in WN.RULES}
        for t in adv:
            if t["window"] != last: say("   " + t["window"]); last = t["window"]
            verdict = "-" if t["needs"] is None else " ".join("%s:%s" % (h, "holds" if t["holds"][h] else "BROKEN") for h in WN.RULES)
            say("     %s" % t["case"])
            say("        landing concluded %-5s | %s | %s: %s" % (t["landing_concluded"], " ".join("%s=%s" % (h, t["outcome"][h]) for h in WN.RULES), t["property"], verdict))
            for h in WN.RULES:
                if t["holds"][h] is False: broken[h].append(t["property"])
        for h in WN.RULES:
            say("   rule %-8s breaks %d of %d property checks%s" % (h, len(broken[h]), sum(t["needs"] is not None for t in adv),
                                                                 ": " + "; ".join(sorted(set(broken[h]))) if broken[h] else ""))
        with open(os.path.join(HERE, "window_adversary.tsv"), "w", encoding="utf-8") as f:
            f.write("window\tcase\tlanding_concluded\tvoid\tcontest\trecount\tproperty\tvoid_holds\tcontest_holds\trecount_holds\n")
            for t in adv:
                f.write("\t".join([t["window"], t["case"], str(t["landing_concluded"])] + [t["outcome"][h] for h in WN.RULES] + [t["property"]]
                                  + ["-" if t["holds"][h] is None else "holds" if t["holds"][h] else "BROKEN" for h in WN.RULES]) + "\n")
        need(not broken["recount"], "the recount rule broke a property")
        need(broken["void"] and broken["contest"], "the void and contest rules were expected to break a property each; the table changed")

        say("3. route")
        r = order_check(mp, "route")
        say("   order-freeness: a pool of %d rows, every subset of up to %d and every closed subset of up to %d: %d sets, %d arrival orders "
            "(%d distinct held orders), %d differ" % (len(POOLS["route"]["room"]), SMALL, BIG["route"], r["sets"], r["orders"], r["held_orders"], r["differ"]))
        need(r["differ"] == 0 and r["orders"] > 0, "route answers depend on the arrival order")
        m = order_check(mp, "route", mutate=True)
        say("   mutation, the audience is the members when the row arrived: %s (%d of %d orders differ)" % (
            "caught" if m["differ"] else "NOT CAUGHT", m["differ"], m["orders"]))
        need(m["differ"] > 0, "the route mutation was not caught")

    joiner = [x for x in RT.world() if x["id"] not in ("xc", "x", "m4", "m5", "k4")] + [RT.REPLY]
    for label, rows in (("the room (16 rows: two founders, a joiner who is removed, five messages, four acknowledgements)", RT.world()),
                        ("the same room with no removal, and a reply to a message from before the joiner came (12 rows)", joiner)):
        for how in ("closed", "own"):
            ms = RT.measure(rows, how)
            say("   %s; audience: %s" % (label, how))
            for p, x in ms.items():
                say("     %s: %2d conclusions, %d differ from a party given every row; routed %2d, in its audience %2d, all rows %2d; routed and changes nothing: %s%s" % (
                    p, x["conclusions"], len(x["differ"]), x["routed"], x["in_audience"], x["all_rows"], x["not_needed"] or "none",
                    "; read but outside its audience: %s" % x["blocked"] if x["blocked"] else ""))
            tot = lambda f: sum(x[f] for x in ms.values())
            say("     total: routed %d, everything in audience %d, everything to everyone %d; conclusions that differ %d; routed rows that change nothing %d" % (
                tot("routed"), tot("in_audience"), tot("all_rows"), sum(len(x["differ"]) for x in ms.values()), sum(len(x["not_needed"]) for x in ms.values())))
            if how == "closed":
                need(all(not x["differ"] and not x["outside_audience"] and not x["still_missing"] for x in ms.values()), "route is not sufficient under the closed audience")
                need(ms["X"]["routed"] == 0 and ms["X"]["in_audience"] == 0, "the stranger was routed a row")
            else:
                need(any(x["differ"] for x in ms.values()), "the own-head audience was expected to leave a joiner unable to conclude; the finding changed")

    say("4. key plane (formal/key_plane, read from rows with the library, against the original's own search)")
    kp = KP.compare()
    for x in kp:
        say("   %-9s %5d sequences of up to 6 acts: %d states, %d comparisons, %d differ; the original fails %s; K1 over %d wraps and K2/K8, K6, K10 from the rows: %d fail" % (
            x["run"], x["sequences"], x["states"], x["compared"], x["differ"], ", ".join(x["original_fails"]) or "nothing", x["wraps"],
            sum(v for k, v in x["findings"].items() if k.startswith("K"))))
        if x["seat_compared"]:
            say("             the same acts as seat.py rows: 'entitled' compared on %d sequences, %d differ" % (x["seat_compared"], x["seat_differ"]))
        if x["findings"]["second device unwrapped at the seat"]:
            say("             finding: in %d states a re-admitted member's second live device is not wrapped at the seat (K9 reads the first device only)" % x["findings"]["second device unwrapped at the seat"])
        need(x["differ"] == 0 and x["seat_differ"] == 0 and not x["original_fails"] and not any(v for k, v in x["findings"].items() if k.startswith("K")), "key plane " + x["run"])
    say("   total: %d comparisons, %d differ" % (sum(x["compared"] for x in kp), sum(x["differ"] for x in kp)))

    say("RESULT: %s in %.0fs" % ("ok" if ok else "FAILED", time.time() - t0))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
