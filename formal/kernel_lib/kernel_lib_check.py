"""
Agreement runs: each re-expressed decision against the original, on the original's own exhaustive cases, and
then put in the original's place under the original's own property check.
Run: python3 -I formal/kernel_lib/kernel_lib_check.py --check    (--ablate removes each function in turn)
"""
import importlib.util, itertools, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.dirname(os.path.dirname(HERE))
import kernel_lib as K, reexpress as X


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, path)); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


def run_takedown():
    tk = load("tk", "formal/takedown/takedown_model.py")
    immediate, windowed, problems = tk.bases(); assert not problems
    basis = {**{b: "immediate" for b in immediate}, **{b: "windowed" for b in windowed}}
    mine = lambda held, now, imm, win, hw: X.takedown([{"k": k, "basis": b, "t": t} for k, b, t in held if t <= now], now, basis, tk.W, hw)
    imm = sorted(immediate)[0]; win = sorted(windowed)[0]
    kinds = [("notice", imm), ("notice", win), ("reversal", ""), ("lift", ""), ("hold", ""), ("hold_lifted", "")]
    n = bad = 0
    for hw in (True, False):
        for size in (1, 2, 3, 4):
            for combo in itertools.combinations(kinds, size):
                for times in itertools.product(range(0, 4), repeat=size):
                    held = {(k, b, t) for (k, b), t in zip(combo, times)}
                    for now in range(tk.HORIZON + 1):
                        n += 1; bad += mine(held, now, immediate, windowed, hw) != tk.fold(held, now, immediate, windowed, hw)
    orig = tk.fold; tk.fold = mine
    cases, fails = tk.check(True, immediate, windowed); _, other = tk.check(False, immediate, windowed)
    tk.fold = orig
    props = not any(fails.values()) and bool(other["P6"])
    return n, bad, f"original check on the library fold: {cases} cases, P1-P6 {'hold' if props else 'FAIL'}, the reading not taken still fails P6", props


def run_deletion():
    dl = load("dl", "formal/deletion/deletion_model.py")
    bad_rule, subj = dl.data_rule(); assert not bad_rule
    def table(subject_excuses):
        return {"starts": {"subject_revokes", "subject_withdraws"}, "excuses": set(dl.PRODUCER) | ({"subject_withdraws"} if subject_excuses else set())}
    mine = lambda held, now, subject_excuses=False: X.deletion([{"k": k, "t": t} for k, t in held if t <= now], now, table(subject_excuses), dl.W)
    n = bad = 0
    for se in (False, True):
        for size in (1, 2, 3, 4):
            for combo in itertools.combinations(dl.KINDS, size):
                for times in itertools.product(range(0, 5), repeat=size):
                    held = set(zip(combo, times))
                    for now in range(dl.HORIZON + 1):
                        n += 1; bad += mine(held, now, se) != dl.fold(held, now, se)
    orig = dl.fold; dl.fold = mine; dl.SUBJECT_EXCUSES = subj
    cases, fails, differ = dl.check(); dl.fold = orig
    props = not any(fails.values()) and not differ
    return n, bad, f"original check on the library fold: {cases} cases, D1-D6 {'hold' if props else 'FAIL'}", props


def run_owner():
    ob = load("ob", "formal/owner_binding/owner_binding_model.py")
    def mine(order, refusal, cosign):
        if refusal != "fold": return orig(order, refusal, cosign)
        rows = [{"k": r[0], "x": r[1], "cos": r[2] if r[0] == "bind" else None, "t": i} for i, r in enumerate(order)]
        return [X.owner_of(rows[:i + 1]) for i in range(len(rows))]
    orig = ob.run
    n = bad = 0
    for size in (1, 2, 3, 4):
        for rows in itertools.combinations(ob.ROWS, size):
            for order in itertools.permutations(rows):
                n += 1; bad += mine(order, "fold", "unowned") != orig(order, "fold", "unowned")
    ob.run = mine; cases, fail = ob.check("fold", "unowned"); ob.run = orig
    props = not any(fail.values())
    return n, bad, f"original check on the library fold: {cases} runs, O1-O8 {'hold' if props else 'FAIL'}", props


def run_guardianship():
    gd = load("gd", "formal/guardianship/guardianship_model.py")
    mine = lambda held, band: X.guardianship([{"k": k, "t": 0} for k in held], band)
    n = bad = 0
    for band in gd.BANDS:
        for k in range(len(gd.ROWS) + 1):
            for held in itertools.combinations(gd.ROWS, k):
                n += 1; bad += mine(set(held), band) != gd.fold(set(held), band)
    cases, fail = gd.check(fold=mine)
    return n, bad, f"original check on the library fold: {cases} cases, G1-G11 {'hold' if not fail else 'FAIL'}", not fail


def run_ranked():
    rc = load("rc", "formal/ranked_choice/ranked_choice_model.py")
    options = ["a", "b", "c"]; R = rc.rankings(options, 3)
    n = bad = 0
    for size in range(0, 6):
        for profile in itertools.combinations_with_replacement(R, size):
            rows = [(i, p) for i, p in enumerate(profile)]
            n += 1; bad += X.ranked(rows, options) != rc.finish(rc.summary(profile), options)
            if size:   # the two cases of R8: a repeated ballot, and one person with two different ballots
                other = next(x for x in R if x != profile[0])
                for extra in (rows[:1], [(0, other)]):
                    n += 1; bad += X.ranked(rows + extra, options)[0] != rc.winner(rows + extra, options)
    # the original's check with the library count in place of finish . summary
    orig_f, orig_w = rc.finish, rc.winner
    def lib_finish(s, opts, floor=rc.FLOOR):
        rows = [((r, j), r) for r, c in s.items() for j in range(c)]
        return X.ranked(rows, list(opts), floor)
    rc.finish = lib_finish; rc.winner = lambda rows, opts: X.ranked(rows, list(opts))[0]
    cases, fail = rc.check(); rc.finish, rc.winner = orig_f, orig_w
    return n, bad, f"original check on the library count: {cases} profiles, R1-R11 {'hold' if not fail else 'FAIL ' + str(sorted(fail))}", not fail


def run_set_item():
    si = load("si", "formal/set_item/set_item_model.py")
    def rows(held):
        out = []
        for part, t in held.items():
            if part == "header": out.append({"k": "header", "item": "i", "digest": "d", "t": t})
            elif part == "fork": out.append({"k": "header", "item": "i", "digest": "d2", "t": t})
            elif part.startswith("leaf"): out.append({"k": "leaf", "item": "i", "digest": "d", "n": int(part[4:]), "t": t})
            else: out.append({"k": "leaf", "item": "i", "digest": "x", "n": 1, "t": t})
        return out
    def mine(held, leaf, reading):
        return X.set_item(rows(held), leaf, si.A, si.W) if reading == "both" else orig(held, leaf, reading)
    orig = si.item_counts
    n = bad = 0
    for size in range(0, len(si.PARTS) + 1):
        for parts in itertools.combinations(si.PARTS, size):
            for times in itertools.product(range(si.HORIZON + 1), repeat=size):
                held = dict(zip(parts, times))
                for leaf in si.LEAVES:
                    n += 1; bad += mine(held, leaf, "both") != orig(held, leaf, "both")
    si.item_counts = mine; cases, fail = si.check("both"); si.item_counts = orig
    return n, bad, f"original check on the library fold: {cases} cases, S1-S7 {'hold' if not fail else 'FAIL'}", not fail


RUNS = {"takedown": run_takedown, "deletion": run_deletion, "owner_binding": run_owner, "guardianship": run_guardianship,
        "ranked_choice": run_ranked, "set_item": run_set_item}


def all_runs():
    res = {}
    for name, f in RUNS.items():
        try: n, bad, msg, props = f(); res[name] = (bad == 0 and props, f"{n} comparisons, {bad} disagree; {msg}")
        except Exception as e: res[name] = (False, f"breaks: {type(e).__name__}: {str(e)[:60]}")
    return res


def main():
    if "--ablate" not in sys.argv:
        res = all_runs()
        for name, (ok, msg) in res.items(): print(f"{'ok  ' if ok else 'FAIL'} {name}: {msg}")
        return 0 if all(ok for ok, _ in res.values()) else 1
    def gone(name):
        def f(*a, **k): raise NotImplementedError(f"{name} removed")
        return f
    for fn in ("sel", "group", "in_range", "rule", "fix"):
        keep = getattr(K, fn); setattr(K, fn, gone(fn))
        res = all_runs(); setattr(K, fn, keep)
        print(f"without {fn}: breaks {', '.join(m for m, (ok, _) in res.items() if not ok) or 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
