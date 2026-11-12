#!/usr/bin/env python3
"""
check.py: run the causal kernel. One command, exit 0 or 1.

  1  order-freeness by execution: every arrival order of every small world gives one kept set, one set of
     conclusions and one set of derived answers; and renaming the digests renames the answers and nothing else
  2  the Lean statements as properties, by enumeration at the bound, each with a mutation that must be caught
  3  the seventeen witnesses, every arrival order, with the adversary each one's `cost` names
  4  the same witnesses judged on arrival, against witnesses.tsv

  python3 -I check.py            bound 6 (sets of up to six rows)
  python3 -I check.py --bound 5  smaller and faster (below 4 one mutation has no case that shows it)
"""
import csv
import itertools
import json
import multiprocessing
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import causal_kernel as CK  # noqa: E402
import witnesses as WIT     # noqa: E402
import arrival as ARR       # noqa: E402

K, R = CK.K, CK.row
BOUND = int(sys.argv[sys.argv.index("--bound") + 1]) if "--bound" in sys.argv else 6
TSV = os.path.join(CK.REPO, "formal", "derivation", "order", "witnesses.tsv")

# ---- the generated worlds ----------------------------------------------------------------------------------
G = R("g", "genesis", "admin", members=("admin", "m", "u"))
POOLS = {
    "slots_and_kinds": [
        G,
        R("a", "claim", "m", ("g",), slot="s"),
        R("b", "claim", "u", ("g",), slot="s"),
        R("c", "decider", "admin", ("a", "b"), slot="s", picks="a"),
        R("d", "decider", "admin", ("a", "b"), slot="s", picks="b"),
        R("a2", "claim", "m", ("a",), slot="s"),
        R("k", "claim", "u", ("g",), slot="s2"),
        R("t", "note", "m", ("g",)),
        R("wd", "retract", "m", ("t",), target="t", level=2),
        R("rc", "retract", "m", ("t",), target="t", level=3),
        R("sp", "retract", "m", ("t",), target="t", level=1),
        R("z", "free", "u"),
    ],
    "removal_reach_tally": [
        G,
        R("prop", "proposal", "admin", ("g",)),
        R("vm", "vote", "m", ("prop",), choice="yes"),
        R("vu", "vote", "u", ("prop",), choice="yes"),
        R("vm2", "vote", "m", ("prop",), choice="no"),
        R("ack", "ack", "u", ("vm",)),
        R("xa", "removal", "admin", ("g",), removes="m"),
        R("xb", "removal", "admin", ("ack",), removes="m"),
        R("late", "note", "m", ("xa",)),
        R("e", "edge", "me", to="admin"),
        R("e2", "edge", "admin", ("g",), to="m"),
        R("w", "withdraw", "me", ("e",)),
        R("wx", "withdraw", "me", ("e2",)),
    ],
}
ROOT = lambda r: r["kind"] == "genesis" or r["signer"] == "me"
READERS = ("me", "admin")
DEPTH = 2


def world_rule(r, P, past, Cc=None):
    """Reads the row and its concluded ancestors: membership of the genesis it descends from, and (by
    negation) no removal of its signer in its own past."""
    k = r["kind"]
    if k == "genesis":
        return r["signer"] == "admin"
    if k in ("edge", "withdraw", "free"):
        return True
    g = K.sel(P, kind="genesis")
    if not g or r["signer"] not in g[0]["members"]:
        return False
    if K.sel(P, kind="removal", removes=r["signer"]):
        return False
    if k == "removal":
        return r["signer"] == "admin"
    if k == "decider":
        return bool(K.sel(P, id=r["picks"]))
    if k == "retract":
        return bool(K.sel(P, id=r["target"], signer=r["signer"]))
    return True


def rule_reads_concurrent(r, P, past, Cc):
    """MUTATION: a claim is denied while a concurrent claim on its slot is live (Causal.Slot.judge)."""
    if r["kind"] == "claim" and K.sel(Cc, kind="claim", slot=r["slot"]):
        return False
    return world_rule(r, P, past)


class Cfg:
    """The kernel under test, and the switches that break it one rule at a time."""
    wait = True                    # the door holds a row whose named rows are not yet kept
    first_wins = False             # MUTATION: the door refuses a claim when a claim on its slot is already held
    rank_tie = False               # MUTATION: a contested slot goes to the least digest
    rule_conc = False              # MUTATION: the conclusion rule reads concurrent rows
    door_reads_other = False       # MUTATION: the door refuses a claim because of another kept claim
    counts = "past"                # MUTATIONS: 'any_removal' (a removal of anyone), 'naive' (only rows naming the removal are void)
    any_signer_withdraws = False   # MUTATION: a withdrawal by any signer ends an edge
    root = True                    # MUTATION (False): a row with no root above it still concludes

    def __init__(self, **kw):
        self.__dict__.update(kw)


TRUE = Cfg()


def counts(S, r, cfg):
    if cfg.counts == "past":
        return CK.counts(S, r)
    if not S.C.get(r["id"]):
        return False
    if cfg.counts == "any_removal":
        return all(r["id"] in S.anc[x["id"]] for x in K.sel(S.Cs, kind="removal"))
    return not any(x["id"] in S.anc[r["id"]] for x in K.sel(S.Cs, removes=r["signer"]))


def answers(S, cfg=TRUE):
    """Every derived answer about a world, as plain values."""
    out = {}
    cl = K.sel(S.Cs, kind={"claim", "decider"})
    for s in ("s", "s2"):
        h, n = CK.slot(S, K.sel(cl, slot=s))
        if cfg.rank_tie and n > 1:
            h = min(r["id"] for r in CK.frontier(S, K.sel(cl, slot=s)))
        out["slot:" + s] = (h, n)
    out["wins"] = frozenset(r["id"] for r in CK.wins(S, S.Cs, lambda r: r.get("level", 0)))
    out["counts"] = frozenset(r["id"] for r in S.rows if counts(S, r, cfg))
    E = CK.live_edges(S, cfg.any_signer_withdraws)
    for own in READERS:
        out["reach:" + own] = CK.reach(S, own, DEPTH, E)
        out["means:" + own] = frozenset(r["id"] for r in S.rows if CK.means(S, r, own, DEPTH, E))
    for pr in K.sel(S.Cs, kind="proposal"):
        out[("tally", pr["id"])] = CK.tally(S, pr, G["members"], counting=lambda v: counts(S, v, cfg))
    return out


def batch(rows, cfg=TRUE):
    """The kernel as a function of the set."""
    kept = CK.kept(rows)
    if cfg.door_reads_other:
        S0 = CK.State(kept)
        bad = {r["id"] for r in K.sel(kept, kind="claim") for q in K.sel(kept, kind="claim", slot=r["slot"])
               if S0.concurrent(q["id"], r["id"])}
        kept = CK.kept(rows, wf=lambda r: r["id"] not in bad)
    root = ROOT if cfg.root else None
    if cfg.rule_conc:
        return CK.concluded(kept, rule_reads_concurrent, root, reads_concurrent=True)
    return CK.concluded(kept, world_rule, root)


def stream(order, cfg=TRUE):
    """The kernel as a node runs it: one row at a time, in this order."""
    if cfg.first_wins:
        seen, kept_order = set(), []
        for r in order:
            if r["kind"] == "claim":
                if r["slot"] in seen:
                    continue
                seen.add(r["slot"])
            kept_order.append(r)
        order = kept_order
    return CK.arrive(order, world_rule, ROOT if cfg.root else None, wait=cfg.wait)


def snapshot(S, cfg=TRUE):
    return frozenset(S.by), frozenset(S.C.items()), answers(S, cfg)


def subsets(pool, bound):
    for n in range(bound + 1):
        yield from itertools.combinations(pool, n)


# ---- 1. order-freeness ---------------------------------------------------------------------------------------
def renaming(pool):
    ids = sorted(r["id"] for r in pool)
    return {i: "n%02d" % (len(ids) - j) for j, i in enumerate(ids)}       # reverses the order of the digests


def rename(v, m):
    if isinstance(v, str):
        return m.get(v, v)
    if isinstance(v, dict):
        return {rename(k, m): rename(x, m) for k, x in v.items()}
    if isinstance(v, (tuple, list, frozenset, set)):
        return type(v)(rename(x, m) for x in v)
    return v


def renamed_rows(rows, m):
    out = []
    for r in rows:
        q = dict(r, id=m[r["id"]], names=tuple(m[n] for n in r["names"]))
        for f in ("picks", "target"):
            if f in q:
                q[f] = m[q[f]]
        out.append(q)
    return out


def order_job(job):
    """All arrival orders of one set. Returns (orders run, orders that disagreed with the set function,
    1 if renaming the digests changed more than the names)."""
    pool_name, idx, cfg_kw = job
    cfg = Cfg(**cfg_kw)
    pool = POOLS[pool_name]
    rows = [pool[i] for i in idx]
    ref = snapshot(batch(rows, TRUE if cfg_kw.get("stream_only") else cfg), cfg)
    n = bad = 0
    for order in itertools.permutations(rows):
        n += 1
        if snapshot(stream(order, cfg), cfg) != ref:
            bad += 1
    m = renaming(pool)
    twin = snapshot(batch(list(reversed(renamed_rows(rows, m))), cfg), cfg)
    sym = 0 if (twin[0], twin[1], twin[2]) == (rename(ref[0], m), rename(ref[1], m), rename(ref[2], m)) else 1
    return n, bad, sym


def order_check(bound, cfg_kw=None, procs=None):
    cfg_kw = cfg_kw or {}
    jobs = [(name, idx, cfg_kw) for name, pool in POOLS.items() for idx in subsets(range(len(pool)), bound)]
    with multiprocessing.Pool(procs) as mp:
        res = mp.map(order_job, jobs, chunksize=16)
    return {"sets": len(jobs), "orders": sum(r[0] for r in res), "orders_differing": sum(r[1] for r in res),
            "sets_where_renaming_changed_an_answer": sum(r[2] for r in res)}


# ---- 2. the Lean statements as properties ------------------------------------------------------------------
class World:
    """Everything one configuration says about every subset of one pool, cached."""

    def __init__(self, pool, cfg):
        self.pool, self.cfg, self.cache = pool, cfg, {}
        by = {r["id"]: r for r in pool}
        self.by = by
        self.panc = {i: CK.ancestors(by, i) for i in by}
        self.desc = {i: {j for j in by if i in self.panc[j]} for i in by}

    def at(self, rows):
        key = frozenset(r["id"] for r in rows)
        if key not in self.cache:
            S = batch(list(rows), self.cfg)
            self.cache[key] = (S, answers(S, self.cfg))
        return self.cache[key]

    def steps(self, bound):
        """Every (set of up to `bound` rows, one more row offered)."""
        for rows in subsets(self.pool, bound):
            have = {r["id"] for r in rows}
            for x in self.pool:
                if x["id"] not in have:
                    yield rows, x


def p_final(W, bound):
    """Causal.concl_final: offering a row never changes the conclusion about a kept row."""
    n = bad = 0
    for rows, x in W.steps(bound):
        S1, S2 = W.at(rows)[0], W.at(rows + (x,))[0]
        for i in S1.by:
            n += 1
            bad += S2.C.get(i) != S1.C[i]
    return n, bad


def p_local(W, bound):
    """Causal.kept_new_row, concl_new_row, derived_new_row: a new row adds only itself and rows that waited
    on it; a slot or a target changes only when one of those rows is on it."""
    n = bad = 0
    for rows, x in W.steps(bound):
        (S1, A1), (S2, A2) = W.at(rows), W.at(rows + (x,))
        new = set(S2.by) - set(S1.by)
        n += 1
        bad += not (set(S1.by) <= set(S2.by) and new <= {x["id"]} | W.desc[x["id"]])
        for s in ("s", "s2"):
            n += 1
            bad += A1["slot:" + s] != A2["slot:" + s] and not any(S2.by[i].get("slot") == s for i in new)
        for t in {r["target"] for r in W.pool if "target" in r}:
            on = lambda A: {i for i in A["wins"] if W.by[i]["target"] == t}
            n += 1
            bad += on(A1) != on(A2) and not any(S2.by[i].get("target") == t for i in new)
    return n, bad


def p_removals(W, bound):
    """Causal.counting_survives / only_removals_stop_counting: a counting row stops counting only when a
    removal of its signer that does not have it in its past arrives, or was waiting on what arrives."""
    n = bad = 0
    for rows, x in W.steps(bound):
        (S1, A1), (S2, A2) = W.at(rows), W.at(rows + (x,))
        new = set(S2.by) - set(S1.by)
        for i in A1["counts"]:
            n += 1
            if i not in A2["counts"]:
                bad += not any(S2.by[y].get("removes") == S1.by[i]["signer"] and i not in S2.anc[y] for y in new)
    return n, bad


def p_withdrawals(W, bound):
    """Causal.meaning_survives / only_withdrawals_remove: a row stops meaning something to a reader only
    when a withdrawal of a live edge, signed by that edge's own signer, arrives or was waiting on what arrives."""
    n = bad = 0
    for rows, x in W.steps(bound):
        (S1, A1), (S2, A2) = W.at(rows), W.at(rows + (x,))
        new = set(S2.by) - set(S1.by)
        own_wd = any(S2.by[w]["kind"] == "withdraw" and any(
            e.get("to") is not None and e["id"] in S2.by[w]["names"] and e["signer"] == S2.by[w]["signer"]
            for e in S1.Cs) for w in new)
        for own in READERS:
            for i in A1["means:" + own]:
                n += 1
                bad += i not in A2["means:" + own] and not own_wd
    return n, bad


def p_sign_after(W, bound):
    """Causal.sign_after_removal_step: a removal is concluded; a row of the removed signer is then offered.
    It does not count."""
    n = bad = 0
    for rows, x in W.steps(bound):
        (S1, _), (S2, A2) = W.at(rows), W.at(rows + (x,))
        if x["id"] in S2.by and any(y.get("removes") == x["signer"] for y in S1.Cs):
            n += 1
            bad += x["id"] in A2["counts"]
    return n, bad


def p_unrooted(W, bound):
    """Causal.unrooted_concludes_nothing: a kept row with no root at or above it concludes nothing."""
    n = bad = 0
    for rows in subsets(W.pool, bound + 1):
        S = W.at(rows)[0]
        for i, r in S.by.items():
            if not (ROOT(r) or any(ROOT(S.by[a]) for a in S.anc[i])):
                n += 1
                bad += bool(S.C[i])
    return n, bad


def revisions(W, bound):
    """Not a property: how often a later row takes back a derived answer (the derived layer is not final)."""
    c = Counter()
    for rows, x in W.steps(bound):
        (S1, A1), (S2, A2) = W.at(rows), W.at(rows + (x,))
        c["steps"] += 1
        c["conclusions_changed"] += sum(S2.C.get(i) != S1.C[i] for i in S1.by)
        c["held_slot_emptied_or_changed"] += sum(A1["slot:" + s][1] == 1 and A2["slot:" + s] != A1["slot:" + s] for s in ("s", "s2"))
        c["winner_displaced"] += len(A1["wins"] - A2["wins"])
        c["row_stopped_counting"] += len(A1["counts"] - A2["counts"])
        c["meaning_removed"] += sum(len(A1["means:" + o] - A2["means:" + o]) for o in READERS)
        c["tally_fell"] += sum(A2[k] < A1[k] for k in A1 if isinstance(k, tuple))
    return c


PROPERTIES = [
    ("finality of the conclusion layer", "concl_final", p_final,
     "the rule denies a claim while a concurrent claim is live", dict(rule_conc=True)),
    ("locality", "kept_new_row, concl_new_row, derived_new_row", p_local,
     "the door refuses a claim because of another kept claim", dict(door_reads_other=True)),
    ("only removals stop counting", "counting_survives, only_removals_stop_counting", p_removals,
     "a removal of any signer stops a row counting", dict(counts="any_removal")),
    ("only withdrawals remove meaning", "meaning_survives, only_withdrawals_remove", p_withdrawals,
     "a withdrawal by any signer ends an edge", dict(any_signer_withdraws=True)),
    ("a row signed after the removal never counts", "sign_after_removal_never_counts, sign_after_removal_step", p_sign_after,
     "only a row that names the removal is void", dict(counts="naive")),
    ("an unrooted row concludes nothing", "unrooted_concludes_nothing", p_unrooted,
     "the root test is dropped", dict(root=False)),
]


def instances():
    """The worked instances in Causal.lean, run."""
    A = {r["id"]: r for r in POOLS["slots_and_kinds"]}
    B = {r["id"]: r for r in POOLS["removal_reach_tally"]}
    at = lambda P, ids: (lambda S: (S, answers(S)))(batch([P[i] for i in ids]))
    out = []
    out.append(("Slot.conflict_empty", at(A, ["g", "a", "b"])[1]["slot:s"] == (None, 2)))
    out.append(("Slot.descendant_decides", at(A, ["g", "a", "b", "c"])[1]["slot:s"] == ("a", 1)))
    out.append(("Slot.two_decisions_empty", at(A, ["g", "a", "b", "c", "d"])[1]["slot:s"] == (None, 2)))
    out.append(("Kinds.recant_beats_withdraw", at(A, ["g", "t", "wd", "rc"])[1]["wins"] == frozenset({"rc"})))
    out.append(("same_kind_both_or_neither (a later claim names one of two)", at(A, ["g", "a", "b", "a2"])[1]["slot:s"] == (None, 2)))
    out.append(("Removal.honest_but_unnamed", "vm" not in at(B, ["g", "prop", "vm", "xa"])[1]["counts"]))
    out.append(("Removal.acknowledged_counts", "vm" in at(B, ["g", "prop", "vm", "ack", "xb"])[1]["counts"]))
    out.append(("Removal.stale_head_voids_more", "vm" not in at(B, ["g", "prop", "vm", "ack", "xa"])[1]["counts"]))
    out.append(("Trust.before (no edge of the reader's own)", "vm" not in at(B, ["g", "prop", "vm", "e2"])[1]["means:me"]))
    out.append(("acceptance_gives_meaning", "vm" in at(B, ["g", "prop", "vm", "e2", "e"])[1]["means:me"]))
    out.append(("Trust.withdrawal", "vm" not in at(B, ["g", "prop", "vm", "e2", "e", "w"])[1]["means:me"]))
    out.append(("a withdrawal by another signer removes nothing", "vm" in at(B, ["g", "prop", "vm", "e2", "e", "wx"])[1]["means:me"]))
    out.append(("no_own_edge_no_reach", at(B, ["g", "e2"])[1]["reach:me"] == frozenset({"me"})))
    out.append(("tally: a voice that says two things says nothing", at(B, ["g", "prop", "vm", "vm2", "vu"])[1][("tally", "prop")] == 1))
    out.append(("a row that names the removal of its signer concludes nothing", at(B, ["g", "xa", "late"])[0].C["late"] is False))
    # not a Lean statement: what `counts` does with a key that was removed and seated again
    W = WIT
    rows = [W.p, W.a, W.w, W.x, W.p2, W.a2, W.w4, R("nK", "note", "K", ("w4",))]
    S = CK.concluded(CK.kept(rows), W.mem_rule)
    out.append(("(finding) after removal and re-admission the key is seated, and its new row still does not count",
                W.seat(S, "K") == "in" and S.C["nK"] and not CK.counts(S, S.by["nK"])))
    return out


def library_findings():
    """What kernel_lib does that this kernel must step around."""
    x, y = {"id": "x", "l": 1}, {"id": "y", "l": 1}
    tie = K.group([x, y], None, "greatest", "l")["id"] != K.group([y, x], None, "greatest", "l")["id"]
    return {"group_greatest_breaks_a_tie_by_list_order": tie,
            "sel_matches_an_absent_field_against_None": bool(K.sel([{"id": "x"}], removes=None))}


# ---- 3. the witnesses ---------------------------------------------------------------------------------------
canon = lambda v: json.dumps(v, sort_keys=True, default=sorted)


def text(ans):
    return "; ".join("%s=%s" % (k, v) for k, v in sorted(ans.items()))


def run_orders(rows, rule, answer):
    """Every arrival order of the rows. Returns (orders, the distinct answers, the set function's answer)."""
    seen = Counter()
    for order in itertools.permutations(rows):
        seen[canon(answer(CK.arrive(order, rule)))] += 1
    ref = answer(CK.concluded(CK.kept(rows), rule))
    return sum(seen.values()), [json.loads(s) for s in seen], ref


def run_witnesses():
    reasoned = {r["id"]: r for r in csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t")}
    table, problems = [], []
    for c in WIT.CASES:
        n, distinct, ref = run_orders(c["rows"], c["rule"], c["answer"])
        if len(distinct) > 1:
            verdict = "STILL TWO RESULTS"
        else:
            verdict = c.get("verdict", "ONE RESULT")
        same_as_set_function = len(distinct) == 1 and canon(distinct[0]) == canon(ref)
        match = c["match"](ref) if c["match"] else ("yes" if canon(ref) == canon(c["expected"]) else "no")
        if c["id"] in WIT.DIFFERS:
            match += "; but " + WIT.DIFFERS[c["id"]]
        rec = {"case": c["id"], "run": "main", "encoding": c["note"], "orders": n, "distinct": len(distinct),
               "verdict": verdict, "result": text(ref), "matches_reasoned": match, "needed": c["needed"],
               "adversary": "", "adversary_gain": "", "reasoned": reasoned[c["id"]]["symmetric_outcome"],
               "cost_reasoned": reasoned[c["id"]]["cost"], "stream_equals_set_function": same_as_set_function}
        advs = []
        for name, base, attacked, gain in c["adversaries"]:
            nb, db, rb = run_orders(base, c["rule"], c["answer"])
            na, da, ra = run_orders(attacked, c["rule"], c["answer"])
            if len(db) != 1 or len(da) != 1:
                problems.append("%s adversary '%s' is order dependent" % (c["id"], name))
            advs.append((name, gain(rb, ra), nb + na))
        rec["adversary"] = " | ".join(a[0] for a in advs)
        rec["adversary_gain"] = " | ".join(a[1] for a in advs)
        rec["adversary_orders"] = sum(a[2] for a in advs)
        table.append(rec)
        for v in c["variants"]:
            label, rows, expected = v[0], v[1], v[2]
            ans = v[3] if len(v) > 3 else c["answer"]
            n, distinct, ref = run_orders(rows, c["rule"], ans)
            table.append({"case": c["id"], "run": "variant", "encoding": label, "orders": n, "distinct": len(distinct),
                          "verdict": "ONE RESULT" if len(distinct) == 1 else "STILL TWO RESULTS", "result": text(ref),
                          "matches_reasoned": "as predicted when encoded" if canon(ref) == canon(expected)
                          else "NOT as predicted when encoded: %s" % text(expected),
                          "needed": "", "adversary": "", "adversary_gain": "", "adversary_orders": 0,
                          "stream_equals_set_function": len(distinct) == 1 and canon(distinct[0]) == canon(ref)})
    return table, problems


# ---- 4. the arrival kernel ------------------------------------------------------------------------------------
def run_arrival():
    tsv = {r["id"]: r for r in csv.DictReader(open(TSV, encoding="utf-8"), delimiter="\t")}
    out = []
    for cid, (rows, guard) in ARR.CASES.items():
        by = {r["id"]: r for r in rows}
        got = []
        for col in ("A", "B"):
            order = [by[i.strip()] for i in tsv[cid]["order_" + col].split(">")]
            got.append(ARR.run(order, guard))
        orders = [[by[i.strip()] for i in tsv[cid]["order_" + col].split(">")] for col in ("A", "B")]
        perms = [o for o in itertools.permutations(rows) if o[0]["id"] == "p"] if cid == "W5" else orders
        allres = {ARR.run(o, guard) for o in perms}
        out.append({"case": cid, "result_A": got[0], "result_B": got[1], "two_results": got[0] != got[1],
                    "same_as_table": got[0] == tsv[cid]["result_A"] and got[1] == tsv[cid]["result_B"],
                    "orders": len(perms), "distinct": len(allres), "table_orders": tsv[cid]["orders_tried"],
                    "table_distinct": tsv[cid]["distinct_results"]})
    for cid, (fn, A, B, words) in ARR.CLOCKED.items():
        ra, rb = fn(A), fn(B)
        out.append({"case": cid, "result_A": ra, "result_B": rb, "two_results": ra != rb,
                    "same_as_table": words[0] in tsv[cid]["result_A"] and words[1] in tsv[cid]["result_B"]
                    and words[0] in ra and words[1] in rb, "orders": 2, "distinct": len({ra, rb}),
                    "table_orders": tsv[cid]["orders_tried"], "table_distinct": tsv[cid]["distinct_results"]})
    ra, rb = ARR.t1([("A", "B"), ("B", "A")]), ARR.t1([("B", "A"), ("A", "B")])
    out.append({"case": "T1", "result_A": ra, "result_B": rb, "two_results": ra != rb,
                "same_as_table": "A->B admitted" in ra and "B->A refused" in ra and "B->A admitted" in rb and "A->B refused" in rb,
                "orders": 2, "distinct": len({ra, rb}), "table_orders": tsv["T1"]["orders_tried"],
                "table_distinct": tsv["T1"]["distinct_results"]})
    return out


# ---- main -------------------------------------------------------------------------------------------------------
def main():
    ok = True
    res = {"bound": BOUND}
    say = lambda *a: print(*a, flush=True)

    say("1. order-freeness by execution (sets of up to %d rows from pools of %s)" % (
        BOUND, " and ".join(str(len(p)) for p in POOLS.values())))
    o = order_check(BOUND)
    res["order"] = o
    say("   %(sets)d sets, %(orders)d arrival orders, %(orders_differing)d orders differ from the set function, "
        "%(sets_where_renaming_changed_an_answer)d sets where renaming the digests changed an answer" % o)
    ok &= o["orders_differing"] == 0 and o["sets_where_renaming_changed_an_answer"] == 0
    res["order_mutations"] = {}
    for name, kw, field in (("the door does not wait", dict(wait=False, stream_only=True), "orders_differing"),
                            ("the door refuses a second claim on a slot (first held wins)", dict(first_wins=True, stream_only=True), "orders_differing"),
                            ("a contested slot goes to the least digest", dict(rank_tie=True), "sets_where_renaming_changed_an_answer")):
        m = order_check(min(BOUND, 4), kw)
        res["order_mutations"][name] = m
        caught = m[field] > 0
        ok &= caught
        say("   mutation, %s: %s (%d of %d orders differ, %d sets changed by renaming)" % (
            name, "caught" if caught else "NOT CAUGHT", m["orders_differing"], m["orders"], m["sets_where_renaming_changed_an_answer"]))

    say("2. the Lean statements as properties (every set of up to %d rows, and one more row offered)" % BOUND)
    res["properties"] = []
    for title, lean, fn, mut_name, mut in PROPERTIES:
        n = bad = mn = mbad = 0
        for pool in POOLS.values():
            a, b = fn(World(pool, TRUE), BOUND)
            c, d = fn(World(pool, Cfg(**mut)), min(BOUND, 5))
            n, bad, mn, mbad = n + a, bad + b, mn + c, mbad + d
        res["properties"].append({"property": title, "lean": lean, "cases": n, "violations": bad,
                                  "mutation": mut_name, "mutation_violations": mbad})
        ok &= bad == 0 and mbad > 0
        say("   %-45s %8d cases, %d violations; mutation (%s): %s, %d violations" % (
            title, n, bad, mut_name, "caught" if mbad else "NOT CAUGHT", mbad))
    rev = Counter()
    for pool in POOLS.values():
        rev += revisions(World(pool, TRUE), BOUND)
    rev["conclusions_changed"] += 0
    res["revisions"] = dict(rev)
    say("   for contrast, over %d steps a later row: changed a conclusion %d times; emptied or changed a held slot %d; "
        "displaced a winner %d; stopped a row counting %d; removed a meaning %d; lowered a tally %d" % (
            rev["steps"], rev["conclusions_changed"], rev["held_slot_emptied_or_changed"], rev["winner_displaced"],
            rev["row_stopped_counting"], rev["meaning_removed"], rev["tally_fell"]))
    inst = instances()
    res["instances"] = [{"name": a, "holds": b} for a, b in inst]
    ok &= all(b for _, b in inst)
    say("   worked instances (eleven of the Lean file's, five of this kernel's own): %d of %d hold%s" % (
        sum(b for _, b in inst), len(inst), "" if all(b for _, b in inst) else " FAILED: " + ", ".join(a for a, b in inst if not b)))
    res["library"] = library_findings()
    say("   kernel_lib: " + "; ".join("%s=%s" % kv for kv in res["library"].items()))

    say("3. the seventeen witnesses, every arrival order")
    table, problems = run_witnesses()
    res["witnesses"] = table
    mains = [t for t in table if t["run"] == "main"]
    for t in mains:
        say("   %-4s %-58s orders=%-5d distinct=%d matches_reasoned=%s" % (
            t["case"], t["verdict"][:58], t["orders"], t["distinct"], t["matches_reasoned"][:60]))
    variants = [t for t in table if t["run"] == "variant"]
    off = [t for t in variants if not t["matches_reasoned"].startswith("as predicted")]
    two = [t for t in table if t["distinct"] != 1 or not t["stream_equals_set_function"]]
    say("   %d main runs, %d variants (%d not as predicted), %d adversary worlds; runs with more than one result: %d; "
        "orders run: %d" % (len(mains), len(variants), len(off), sum(len(c["adversaries"]) for c in WIT.CASES), len(two),
                            sum(t["orders"] + t["adversary_orders"] for t in table)))
    for t in off:
        say("      variant not as predicted: %s / %s -> %s" % (t["case"], t["encoding"], t["result"]))
    for pr in problems:
        say("      " + pr)
    ok &= len(mains) == 17 and not two and not problems

    say("4. the same witnesses judged on arrival")
    arr = run_arrival()
    res["arrival"] = arr
    for a in arr:
        say("   %-4s two results: %-5s same as witnesses.tsv: %-5s distinct here %d over %d orders (table: %s over %s)" % (
            a["case"], a["two_results"], a["same_as_table"], a["distinct"], a["orders"], a["table_distinct"], a["table_orders"]))
    ok &= len(arr) == 17 and all(a["two_results"] and a["same_as_table"] for a in arr)

    cols = ["case", "run", "encoding", "orders", "distinct", "verdict", "result", "matches_reasoned", "needed",
            "adversary", "adversary_gain"]
    with open(os.path.join(HERE, "witness_runs.tsv"), "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(["case", "run", "encoding_note", "orders_run", "distinct_results", "verdict", "result",
                     "matches_reasoned", "needed", "adversary", "adversary_gain"])
        for t in table:
            wr.writerow([t[c] for c in cols])
    with open(os.path.join(os.environ.get("HANDOFF_TMP", "/tmp"), "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=sorted)
    say("RESULT: %s" % ("ok" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
