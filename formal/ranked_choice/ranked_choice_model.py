#!/usr/bin/env python3
"""
CC — ranked choice as one count, as a small executable model (CC 4.5.13).

A ballot ranks up to R of the options, best first. The count is instant runoff: while no option holds more than
half of the ballots still counting, the weakest standing option is eliminated and its ballots pass to their next
standing choice; a ballot with no standing choice left stops counting. A tie for weakest is broken against the
option later in the declared order. An election declares no order, so there a tie for weakest seats nobody and
the count runs again (CC 4.5.13; CC 4.5.4: the ballot's shown order "confers nothing and decides nothing").

The count is written here the way a kernel must run it, in two parts:

    summary    a tally of how many ballots carry each ranking. Two summaries merge by adding counts, so a summary
               is the same whatever order the ballots were folded in, and it is kept up to date one ballot at a
               time. This is the only part that touches ballots.
    finish     instant runoff over the summary. It reads no ballot, takes at most one round for each option, and
               uses whole numbers only.

One ballot counts for each person: a person's ballots are folded to one, and a person whose ballots disagree
has none (the fold `pick=agree` of the ballot family).

Properties, over every profile of ballots up to the bound:
  R1  the winner is the same for every order of the same ballots, and for every way of splitting them into parts
      that are summarised apart and merged
  R2  the summary's merge is associative and commutative, and the empty summary changes nothing
  R3  the count ends in fewer rounds than there are options
  R4  the winner is an option, and an option more than half the ballots rank first wins
  R5  a tie for weakest is settled by the declared order alone
  R6  a ballot that ranks only eliminated options stops counting and changes no later round
  R7  below the floor of voices there is no winner
  R8  one ballot per person: repeating a ballot changes nothing, and a person with two different ballots counts for none
  R9  a secret count gives the same winner: the sum of one cell per ranking is the summary
  R10 the runoff is run: where no option has more than half, the weakest goes and its ballots pass on
  R11 a round's totals are a sum over cells, so two holders of additive shares of the summary each publish a
      share of the totals and the two add to the true totals, for every set of standing options: a secret
      ranked poll publishes its rounds and never the tally of rankings

And of the count with no declared order (`winner_no_order`, the election's):
  R12 the result does not depend on the order the options are listed in
  R13 it agrees with the declared-order count whenever that count breaks no tie, and is no winner exactly when it does
  R14 renaming the options moves the winner with them
A mutation that breaks a tie by list position must fail R12.

Not claimed, because instant runoff does not have it: that ranking an option higher can never hurt it.

Run: python3 formal/ranked_choice/ranked_choice_model.py --check
"""
import itertools, sys
from collections import Counter

FLOOR = 2


def rankings(options, r):
    return [p for k in range(1, r + 1) for p in itertools.permutations(options, k)]


def dedupe(rows):
    """rows: (person, ranking). One ballot per person; a person whose ballots disagree has none."""
    by = {}
    for person, ranking in rows: by.setdefault(person, set()).add(ranking)
    return [next(iter(v)) for v in by.values() if len(v) == 1]


def summary(ballots):
    return Counter(ballots)


def merge(a, b):
    return a + b


def finish(s, options, floor=FLOOR):
    """Instant runoff over a summary. Returns (winner or None, rounds)."""
    return count(s, options, floor)[:2]


def count(s, options, floor=FLOOR, declared=True, by_position=False):
    """Instant runoff over a summary. Returns (winner or None, rounds, tied): `tied` says a tie for weakest arose.
    declared=True: a tie for weakest goes against the option later in the declared order (`options`).
    declared=False: the election's count. There is no order, so a tie for weakest seats nobody.
    by_position: MUTATION for the check, the count with no order breaking a tie by where an option is listed."""
    if sum(s.values()) < min(floor, max(len(options), 1)): return None, 0, False
    standing, rounds, tied_any = list(options), 0, False
    while True:
        first = Counter()
        for ranking, n in s.items():
            top = next((o for o in ranking if o in standing), None)
            if top is not None: first[top] += n
        live = sum(first.values())
        if live == 0: return None, rounds, tied_any
        lead = max(standing, key=lambda o: (first[o], -options.index(o)))
        if 2 * first[lead] > live or len(standing) == 1: return lead, rounds, tied_any
        low = min(first[o] for o in standing)
        tied = [o for o in standing if first[o] == low]
        if len(tied) > 1:
            tied_any = True
            if not declared and not by_position: return None, rounds, True     # no order: a tie seats nobody
        weakest = max(tied, key=options.index)                    # a tie goes against the later option
        standing.remove(weakest); rounds += 1


P = (1 << 61) - 1   # a prime field for additive shares


def round_totals(s, standing):
    """Each standing option's total: the ballots whose first standing choice it is. Linear in the summary."""
    t = {o: 0 for o in standing}
    for ranking, n in s.items():
        top = next((o for o in ranking if o in standing), None)
        if top is not None: t[top] = (t[top] + n) % P
    return t


def shares(s, cells):
    """Two additive shares of a summary over every cell: neither alone says anything about a ballot."""
    a = {c: (7919 * (i + 1) * (i + 3) + 104729) % P for i, c in enumerate(cells)}
    b = {c: (s.get(c, 0) - a[c]) % P for c in cells}
    return a, b


def winner(rows, options):
    return finish(summary(dedupe(rows)), options)[0]


def winner_no_order(rows, options):
    """The election's count (CC 4.5.13): no declared order, so a tie for weakest seats nobody and the count runs
    again. `options` is a set given as a list; its order is read by nothing."""
    return count(summary(dedupe(rows)), list(options), declared=False)[0]


def check_no_order(n_options=3, r=3, max_ballots=5, by_position=False):
    """R12-R14 over every profile to the bound. by_position: run with the mutation, which R12 must catch."""
    options = [chr(ord("a") + i) for i in range(n_options)]
    R = rankings(options, r)
    fail, n = {}, 0
    def note(p, *w): fail.setdefault(p, w)
    free = lambda s, opts: count(s, list(opts), declared=False, by_position=by_position)[0]
    for size in range(0, max_ballots + 1):
        for profile in itertools.combinations_with_replacement(R, size):
            n += 1
            s = summary(profile)
            w = free(s, options)
            # R12: every listing of the options gives the same result
            for perm in itertools.permutations(options):
                if free(s, perm) != w: note("R12", profile, perm)
            # R13: agrees with the declared count where that count broke no tie; no winner where it did
            dw, _, tied = count(s, options)
            if not tied and dw != w: note("R13", profile, dw, w)
            if tied and w is not None: note("R13", profile, "a tie, and a winner", w)
            # R14: renaming the options moves the winner with them
            flip = dict(zip(options, reversed(options)))
            w2 = free(summary(tuple(tuple(flip[o] for o in p) for p in profile)), options)
            if (flip[w] if w else None) != w2: note("R14", profile, w, w2)
    # R13, a known answer: three first choices one each is a tie for weakest; the declared count seats one, the election nobody
    tie = summary([("a", "b"), ("b", "a"), ("c", "b")])
    if not by_position and (finish(tie, options)[0] != "b" or free(tie, options) is not None): note("R13", "the known tie")
    return n, fail


def check(n_options=3, r=3, max_ballots=5):
    options = [chr(ord("a") + i) for i in range(n_options)]
    R = rankings(options, r)
    fail, n = {}, 0
    def note(p, *w): fail.setdefault(p, w)
    for size in range(0, max_ballots + 1):
        for profile in itertools.combinations_with_replacement(R, size):
            n += 1
            s = summary(profile); w, rounds = finish(s, options)
            # R1: every order, and every split merged
            for perm in itertools.islice(itertools.permutations(profile), 24):
                if finish(summary(perm), options)[0] != w: note("R1", profile, perm)
            for cut in range(size + 1):
                if finish(merge(summary(profile[:cut]), summary(profile[cut:])), options)[0] != w: note("R1", profile, cut)
            # R2
            a, b, c = summary(profile[:size // 3]), summary(profile[size // 3: 2 * size // 3]), summary(profile[2 * size // 3:])
            if merge(merge(a, b), c) != merge(a, merge(b, c)) or merge(a, b) != merge(b, a) or merge(s, Counter()) != s: note("R2", profile)
            if rounds >= max(len(options), 1) and size: note("R3", profile, rounds)
            if w is not None and w not in options: note("R4", profile, w)
            firsts = Counter(p[0] for p in profile)
            for o in options:
                if size >= FLOOR and 2 * firsts[o] > size and w != o: note("R4", profile, o, w)
            # R5: renaming the options along the declared order moves the winner with it
            flip = dict(zip(options, reversed(options)))
            w2 = finish(summary(tuple(tuple(flip[o] for o in p) for p in profile)), [flip[o] for o in options])[0]
            if (flip[w] if w else None) != w2: note("R5", profile, w, w2)
            if size < min(FLOOR, len(options)) and w is not None: note("R7", profile, w)
            # R8
            rows = [(i, p) for i, p in enumerate(profile)]
            if winner(rows + rows[:1], options) != w: note("R8", profile, "repeat")
            if size >= 1:
                other = next(x for x in R if x != profile[0])
                if winner(rows + [(0, other)], options) != finish(summary(profile[1:]), options)[0]: note("R8", profile, "disagree")
            # R11: each round's totals from two additive shares equal the totals from the summary, for every standing set
            a_sh, b_sh = shares(s, R)
            for k in range(1, len(options) + 1):
                for standing in itertools.combinations(options, k):
                    ta, tb, t = round_totals(a_sh, standing), round_totals(b_sh, standing), round_totals(s, standing)
                    if any((ta[o] + tb[o]) % P != t[o] for o in standing): note("R11", profile, standing)
            # R9: one cell per ranking, summed across members
            cells = {x: 0 for x in R}
            for p in profile: cells[p] += 1
            if finish(Counter({k: v for k, v in cells.items() if v}), options)[0] != w: note("R9", profile)
    # R10, a known answer: `a` and `c` tie on first choices, `b` is weakest and its ballot passes to `c`
    if finish(summary([("a",), ("a",), ("b", "c"), ("c", "b"), ("c", "b")]), options)[0] != "c": note("R10", "the leader on first choices won without a runoff")
    # R6, on a fixed profile: c is eliminated first; a ballot ranking only c stops counting
    w_with, _ = finish(summary([("a",), ("a",), ("b",), ("b",), ("b",), ("c",)]), options)
    w_without, _ = finish(summary([("a",), ("a",), ("b",), ("b",), ("b",)]), options)
    if w_with != w_without: note("R6", w_with, w_without)
    return n, fail


def main():
    n, fail = check()
    for p, w in sorted(fail.items()): print(f"  FAIL {p}: {w}")
    print(f"ranked_choice: {n} profiles of up to five ballots over three options, eleven properties " + ("hold" if not fail else f"fail {sorted(fail)}"))
    n2, fail2 = check_no_order()
    for p, w in sorted(fail2.items()): print(f"  FAIL {p}: {w}")
    print(f"ranked_choice, no declared order (the election): {n2} profiles, R12-R14 " + ("hold" if not fail2 else f"fail {sorted(fail2)}"))
    _, caught = check_no_order(by_position=True)
    print("ranked_choice, mutation (a tie broken by list position): " + ("caught by R12" if "R12" in caught else "NOT caught"))
    return 1 if fail or fail2 or "R12" not in caught else 0


if __name__ == "__main__":
    sys.exit(main())
