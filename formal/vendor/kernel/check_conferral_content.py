#!/usr/bin/env python3
"""
check_conferral_content.py: room content after a member's seat ends, where the end names the rows held good
(conferral_content.py; the Constitution's proposal of 2026-11-22, second form). Checked three ways.

    case table   every case of conferral_content.CASES: the reference gives the hand-written counted, in_force
                 and rule for every content row, in every arrival order the door allows (up to 200 per case)
    fixture      crates/ciris-kernel/tests/fixtures/conferral_content.json: the reference, run on each case's
                 rows, gives every answer the fixture states, and each listed arrival order ends at it
    every world  every history to a bound, built row by row, every row naming only earlier rows: two roster
                 heads; up to three content rows of the member, each naming up to two earlier ones as `prev`
                 and optionally an earlier end, or retracting an earlier one; up to two ends, each a counted removal or the member's own, at
                 either head, optionally stale or naming the earlier end; one row adding tips, counted or the
                 member's own; four rows in all besides the heads (`--rows N`). A tip or a predecessor is a row
                 signed earlier (an id fixes its row) and need not be held: every history is also read with
                 each one of its content rows not held. Two keys of the member sign; `--one-key` has one. Every
                 extension of a held set by rows of the member alone, and by one counted row, is compared:

        cannot_add      once an end counts, nothing the member signs afterwards puts a row into the room's
                        content: no content row it signs later is ever in, and no end or tips row it signs
                        brings an earlier row in. Also with any one content row not held
        arrival_grows   a content row arriving late (a tip, or a predecessor in the middle of a chain) never
                        takes a row out, unless it is a retraction of that row, and changes no count
        word_stands     a row the count's tips hold good stays, whatever the member signs, unless the member
                        retracts it (W.retracted) or the member's own backdated end puts it at a later head
                        than an end of its seat (E3.later_head): the reader's line bounds that, and the run
                        reports how often it happens
        retract_removes a retraction never puts a row into the room's content
        co_member_inert a co-member's content row or retraction changes no answer of the member's
        tips_grow       a counted row adding tips never takes a row out, and changes no count
        further_end     a further counted end takes a row out only by E3.later_head
        counted_alike   whether a row counts never depends on whose tips are read
        set_function    the answer does not depend on the order the rows are listed in

    Plants, each of which must break cannot_add: `union` (the proposal's third point read literally: the
    member's own ends add), `count_first_self_union` (the member's own ends add where no counted end counts),
    and a `tips` row signed by the member that is read.

    The node-local fallback (a row held before the end stays shown to that reader) is not part of the proposal.
    The run reports, over the case table, in how many cases two arrival orders of one set of rows show
    different rooms.

    python3 -I check_conferral_content.py [--rows N] [--workers N]      exit 1 on any difference
    (three worker processes and the calling one, as the other checks here)
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import conferral_content as CC  # noqa: E402

FIXTURE = os.path.join(ROOT, "crates", "ciris-kernel", "tests", "fixtures", "conferral_content.json")
# the roster heads a history is built over. `plain`: two versions with the member seated at both. `rejoin`: the
# second version admits the member again, so a history has rows of two seats. `gap`: seated, not listed, admitted
# again (three heads: run one row shallower)
# Each with the keys that sign content: B and B2 are the member's, M a co-member's.
PROFILES = {"plain": ([CC.head("H0"), CC.head("H1", "H0")], 0, ("B", "B2")),
            "rejoin": ([CC.head("H0"), CC.head("H1", "H0", seat="admits")], 0, ("B", "M")),
            "gap": ([CC.head("H0"), CC.head("HX", "H0", seat="out"), CC.head("HA", "HX", seat="admits")], 1,
                    ("B", "B2"))}
HEADS = PROFILES["plain"][0]
SIGNERS = PROFILES["plain"][2]
MAX_ROWS, MAX_ACTS, MAX_ENDS, MAX_TIPS = 4, 3, 2, 1
WIDE = True      # two keys of the member; --one-key has one (for a deeper --rows)


def next_rows(rows):
    """Every row that may be signed next: it names only rows already signed."""
    acts = [r["id"] for r in rows if r["kind"] == "act"]
    ends = [r["id"] for r in rows if r["kind"] == "end"]
    n_tips = sum(r["kind"] == "tips" for r in rows)
    if len(acts) < MAX_ACTS:
        i = "a%d" % (len(acts) + 1)
        for key in (SIGNERS if WIDE else SIGNERS[:1]):
            for h in [x["id"] for x in HEADS]:
                for prev in [()] + [c for n in (1, 2) for c in itertools.combinations(acts, n)]:
                    for cite in [None] + ends:
                        yield CC.act(i, h, prev, [cite] if cite else [], signer=key)
                for target in acts:                   # a retraction of an earlier row, its own or not
                    yield CC.act(i, h, (), signer=key, target=target, compose="retract")
    # a row names a tip or a predecessor by id, which fixes that row: so both are rows signed earlier. That a
    # named row may not be HELD is checked by taking one content row out of each history (`go`)
    tip_sets = [()] + [c for k in (1, 2) for c in itertools.combinations(acts, k)]
    if len(ends) < MAX_ENDS:
        i = "e%d" % (len(ends) + 1)
        for signer in (CC.COUNT, "B"):
            for h in [x["id"] for x in HEADS]:
                # an end may name a later head (then it is stale, E1) or an earlier end
                extras = [()] + [(x["id"],) for x in HEADS[1:] if x["id"] != h and h == HEADS[0]["id"]] \
                    + [(e,) for e in ends]
                for tp in tip_sets:
                    for extra in extras:
                        yield CC.end(i, h, tp, signer, extra)
    if n_tips < MAX_TIPS and ends:
        for signer in (CC.COUNT, "B"):
            for e in ends:
                for tp in tip_sets[1:]:
                    yield CC.tips("t1", e, tp, signer)      # no rule reads an adding row's own head


def by_member(r):
    return r["signer"] in CC.KEYS


class Run:
    def __init__(self, merge="count_first", self_tips=False, limit=None):
        self.merge, self.self_tips, self.limit = merge, self_tips, limit
        self.worlds = self.pairs = self.e3 = 0
        self.bad = {}

    def ans(self, rows):
        return CC.answers(rows, self.merge, self.self_tips)

    def fail(self, prop, rows, note):
        self.bad.setdefault(prop, (note, [(r["id"], r["kind"], r["signer"], r.get("head"), r.get("prev"),
                                          r.get("trusted_through"), r["names"]) for r in rows]))

    def go(self, rows, path, descend=True):
        """`path[j]`: for the prefix of `rows` of length len(HEADS) + j, its answers, the seats in which an end
        counts, and those in which a counted end does."""
        if self.limit is not None and self.bad:
            return
        a = self.ans(rows)
        seat = CC.seats(rows)
        info = (a,) + CC.ended_seats(rows, self.merge)
        self.worlds += 1
        added = rows[len(HEADS):]
        if added:
            last = added[-1]
            # extensions by the member alone: every prefix from which only the member signed
            k = len(rows)
            while k > len(HEADS) and by_member(rows[k - 1]):
                k -= 1
                pa, p_end, p_count_end = path[k - len(HEADS)]
                if True:
                    self.pairs += 1
                    # the same content rows, without the ends and tips rows the member signed since
                    base = self.ans(rows[:k] + [r for r in rows[k:] if r["kind"] == "act"])
                    for x, v in a.items():
                        if seat[x] not in p_end:
                            continue                    # its seat had not ended: the member sits, and may post
                        if v["in_force"] and not base[x]["in_force"]:
                            self.fail("cannot_add", rows, "%s is in the content by an end or a tips row the member "
                                                          "signed after an end counted" % x)
                        if v["in_force"] and x not in pa:
                            self.fail("cannot_add", rows, "%s, signed by the member after an end counted, is in "
                                                          "the content" % x)
                if p_count_end:
                    for x, v in pa.items():
                        if seat[x] in p_count_end and v["in_force"] and not a[x]["in_force"]:
                            if a[x]["rule"] == "E3.later_head":
                                self.e3 += 1
                            elif a[x]["rule"] != "W.retracted":
                                self.fail("word_stands", rows, "%s leaves the content by %s" % (x, a[x]["rule"]))
            pa, p_end, p_count_end = path[len(rows) - 1 - len(HEADS)]
            if last["signer"] == "M":
                self.pairs += 1
                if any(a[x] != v for x, v in pa.items()) or set(a) != set(pa):
                    self.fail("co_member_inert", rows, "a co-member's row changes an answer")
            if last.get("compose") == "retract":
                self.pairs += 1
                for x, v in pa.items():
                    if a[x]["in_force"] and not v["in_force"]:
                        self.fail("retract_removes", rows, "%s enters the content when a retraction is signed" % x)
            if last["signer"] == CC.COUNT and last["kind"] == "tips":
                self.pairs += 1
                for x, v in pa.items():
                    if (v["in_force"] and not a[x]["in_force"]) or v["counted"] != a[x]["counted"]:
                        self.fail("tips_grow", rows, "%s changes when a counted row adds tips" % x)
            if last["signer"] == CC.COUNT and last["kind"] == "end" and p_count_end:
                self.pairs += 1
                for x, v in pa.items():
                    if seat[x] in p_count_end and v["in_force"] and not a[x]["in_force"] \
                            and a[x]["rule"] != "E3.later_head":
                        self.fail("further_end", rows, "%s leaves the content by %s" % (x, a[x]["rule"]))
            # one content row not held: the fold fills in when it arrives, and its arrival changes no count
            for gone in [r for r in added if r["kind"] == "act"]:
                held = [r for r in rows if r is not gone]
                h = self.ans(held)
                self.pairs += 1
                for x, v in h.items():
                    lost = v["in_force"] and not a[x]["in_force"]
                    if lost and not (gone.get("compose") == "retract" and gone.get("target") == x):
                        self.fail("arrival_grows", rows, "%s leaves the content when %s arrives" % (x, gone["id"]))
                    if v["counted"] != a[x]["counted"]:
                        self.fail("arrival_grows", rows, "%s's count changes when %s arrives" % (x, gone["id"]))
                k = len(rows)
                while k > len(HEADS) and by_member(rows[k - 1]):
                    k -= 1
                    was_ended = path[k - len(HEADS)][1]
                    if was_ended:
                        base = self.ans([r for r in rows[:k] + [r for r in rows[k:] if r["kind"] == "act"]
                                         if r is not gone])
                        for x, v in h.items():
                            if seat[x] in was_ended and v["in_force"] and not base[x]["in_force"]:
                                self.fail("cannot_add", rows, "without %s held, %s is in the content by an end or "
                                                              "a tips row the member signed later" % (gone["id"], x))
            if self.merge == "count_first" and not self.self_tips:
                for m in CC.MERGES[1:]:
                    o = CC.answers(rows, m)
                    if any(o[x]["counted"] != a[x]["counted"] for x in a):
                        self.fail("counted_alike", rows, "a count differs under %s" % m)
                if CC.answers(rows[::-1], self.merge) != a:
                    self.fail("set_function", rows, "the answer depends on the order of the list")
        if descend and len(added) < MAX_ROWS:
            for r in next_rows(rows):
                self.go(rows + [r], path + [info])
        return info


def _subtree(job):
    """One worker's share: the histories that begin with the two rows of `job`."""
    kw, rows_max, wide, heads, signers, r1, r2 = job
    global MAX_ROWS, WIDE, HEADS, SIGNERS
    MAX_ROWS, WIDE, HEADS, SIGNERS = rows_max, wide, heads, signers
    run = Run(**kw)
    path = [run.go(list(HEADS), [], descend=False)]
    path.append(run.go(HEADS + [r1], path, descend=False))
    run.worlds, run.pairs, run.e3, run.bad = 0, 0, 0, {}    # the two prefixes are the caller's to count
    run.go(HEADS + [r1, r2], path)
    return run.worlds, run.pairs, run.e3, run.bad


def explore(workers=3, **kw):
    """Every history to the bound, the subtrees below the first two rows shared among `workers` processes."""
    import multiprocessing
    top = Run(**kw)
    path = [top.go(list(HEADS), [], descend=False)]
    jobs = []
    for r1 in next_rows(list(HEADS)):
        top.go(HEADS + [r1], path, descend=False)
        if MAX_ROWS >= 2:
            jobs += [(kw, MAX_ROWS, WIDE, HEADS, SIGNERS, r1, r2) for r2 in next_rows(HEADS + [r1])]
    with multiprocessing.Pool(workers) as pool:
        for w, p, e, bad in pool.imap_unordered(_subtree, jobs, chunksize=8):
            top.worlds += w; top.pairs += p; top.e3 += e
            for k, v in bad.items():
                top.bad.setdefault(k, v)
    return top


def worlds_fixture(full=3, deeper=4, every=53):
    """Histories with the reference's answers, for a differential test of another implementation, in the order
    the run builds them. For the plain heads: every history of up to `full` rows and every `every`-th of
    `deeper` rows. For the heads with a second seat (`rejoin`, `gap`): every history of up to `full` rows. Each
    history is its rows (as conferral_content.json has them) and {content row: [counted, in_force, rule]}
    under count_first."""
    global MAX_ROWS, WIDE, HEADS, SIGNERS
    keep = (MAX_ROWS, WIDE, HEADS, SIGNERS)
    groups = []
    for name, (heads, _, signers) in PROFILES.items():
        depth = deeper if name == "plain" else full - (len(heads) - 2)
        MAX_ROWS, WIDE, HEADS, SIGNERS = depth, True, heads, signers
        out, seen = [], [0]

        def go(rows):
            n = len(rows) - len(HEADS)
            if n:
                take = n <= full
                if n > full:
                    seen[0] += 1
                    take = seen[0] % every == 0
                if take:
                    out.append({"rows": rows[len(HEADS):],
                                "answers": {x: [a["counted"], a["in_force"], a["rule"]]
                                            for x, a in CC.answers(rows).items()}})
            if n < depth:
                for r in next_rows(rows):
                    go(rows + [r])
        go(list(HEADS))
        groups.append({"name": name, "heads": heads, "worlds": out})
    MAX_ROWS, WIDE, HEADS, SIGNERS = keep
    return {"about": "room content after a member's seat ends: histories built row by row as "
                     "models/causal_kernel/check_conferral_content.py builds them, each with the answers of "
                     "conferral_content.py under count_first. `plain`: every history of up to %d rows beyond two "
                     "roster heads and every %dth of %d rows. `rejoin` and `gap`: a second seat, every history of "
                     "up to %d rows. For a differential test" % (full, every, deeper, full),
            "groups": groups}


def first_held():
    """Over the case table: the cases where two arrival orders of one set of rows show different rooms under
    the node-local fallback, and the cases where it shows a row the proposal keeps out."""
    differ, shows_out = [], []
    for c in CC.CASES:
        name, _, rows, params = c[:4]
        seen = set()
        for o in CC.orders(rows)[:200]:
            s = CC.shown_first_held(rows, o, **params)
            seen.add(tuple(sorted(s.items())))
        if len(seen) > 1:
            differ.append(name)
        final = CC.answers(rows, **params)
        if any(v and not final[x]["in_force"] for t in seen for x, v in t):
            shows_out.append(name)
    return differ, shows_out


def main():
    global MAX_ROWS, WIDE
    WIDE = "--one-key" not in sys.argv
    if "--rows" in sys.argv:
        MAX_ROWS = int(sys.argv[sys.argv.index("--rows") + 1])
    n, problems = CC.check_cases()
    fx = json.load(open(FIXTURE, encoding="utf-8"))
    answers = 0
    for c in fx["cases"]:
        got = CC.answers(c["rows"], c["merge"])
        if got != c["answers"]:
            problems.append("fixture %s: the reference gives %s, the fixture %s" % (c["name"], got, c["answers"]))
        answers += len(c["answers"])
        by = {r["id"]: r for r in c["rows"]}
        for order in c["orders"]:
            held = set()
            for i in order:
                if not all(x in held or x not in by for x in by[i]["names"]):
                    problems.append("fixture %s: order %s takes %s before what it names" % (c["name"], order, i))
                held.add(i)
            if CC.answers([by[i] for i in order], c["merge"]) != c["answers"]:
                problems.append("fixture %s: order %s ends elsewhere" % (c["name"], order))
    if {c["name"] for c in fx["cases"]} != {c[0] for c in CC.CASES}:
        problems.append("the fixture's cases are not the table's")

    global HEADS, SIGNERS
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 3
    rows_max, run, sizes = MAX_ROWS, None, []
    for name, (heads, shallower, signers) in PROFILES.items():
        HEADS, MAX_ROWS, SIGNERS = heads, rows_max - shallower, signers
        r = explore(workers)
        sizes.append("%s %d" % (name, r.worlds))
        if run is None:
            run = r
        else:
            run.worlds += r.worlds; run.pairs += r.pairs; run.e3 += r.e3
            for k, v in r.bad.items():
                run.bad.setdefault(k, v)
    HEADS, MAX_ROWS, SIGNERS = PROFILES["plain"][0], rows_max, PROFILES["plain"][2]
    for prop, (note, rows) in sorted(run.bad.items()):
        problems.append("%s: %s\n    %s" % (prop, note, "\n    ".join(map(str, rows))))

    plants = [("union", dict(merge="union")), ("count_first_self_union", dict(merge="count_first_self_union")),
              ("member's tips row read", dict(self_tips=True))]
    caught = 0
    for name, kw in plants:
        p = Run(limit=1, **kw)
        p.go(list(HEADS), [])                     # over the plain heads
        if "cannot_add" in p.bad:
            caught += 1
        else:
            problems.append("plant %s: not caught" % name)

    differ, shows_out = first_held()
    for p in problems:
        print(p)
    print("first-held fallback (not part of the proposal): in %d of %d cases two arrival orders of one set of rows "
          "show different rooms; in %d it shows a row the proposal keeps out" % (len(differ), n, len(shows_out)))
    print("RESULT: %s: %d cases, %d content answers; %d histories of up to %d rows%s (%s), %d extensions compared; a "
          "member's backdated end took a kept row out by E3 in %d; plants caught %d of %d"
          % ("ok" if not problems else "%d problems" % len(problems), n, answers, run.worlds, MAX_ROWS,
             "" if WIDE else ", one key", "; ".join(sizes), run.pairs,
             run.e3, caught, len(plants)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
