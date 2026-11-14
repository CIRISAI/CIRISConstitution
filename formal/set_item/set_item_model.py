#!/usr/bin/env python3
"""
CC — a set of rows as one item, and the law that admits it (a small executable model).

Many rows by one signer at one instant in one family may travel as one item: a header that the signer signs once
over a digest of the leaves, and the leaves, each with a proof that it belongs to the header. The item is admitted
on one condition, which is the whole of its safety:

    THE LAW   what a node concludes from the item equals what it would conclude from the same leaves held as
              separately signed rows.

If the law holds, an item changes the bytes and never a conclusion. This model states both sides as folds over
what a node holds, with the instant it first held each part, and checks the law over every case to a bound.

    rows side   a row counts when the node holds it and first held it within W of its signed instant.
    item side   a leaf counts when the node holds the header and the leaf, the leaf's proof is good, the header
                is not forked (a second header for the same item with another digest), and the leaf is fresh.

When is a leaf fresh? Three readings, and the model runs each:
    both     the leaf is first held when both it and its header are held (the later of the two instants)
    leaf     the leaf's own first-held instant, whenever the header came
    header   the header's first-held instant, whenever the leaf came

Properties, over every set of parts and every arrival instant up to the bound:
  S1  the law: each leaf counts on the item side exactly when its row counts on the rows side, the row being
      first held at the instant the node first held both the header and the leaf
  S2  a leaf's verdict does not depend on which other leaves are held
  S3  a leaf held before its header counts as soon as the header is held, as if they had come together
  S4  a header alone counts for nothing
  S5  a leaf whose proof does not match the header never counts
  S6  under a forked header no leaf counts, whichever header came first
  S7  the verdict is a function of the parts held and their first-held instants

Only the first reading holds the law. The check requires that, and requires each other reading to fail S1.

Run: python3 formal/set_item/set_item_model.py --check
"""
import itertools, sys

W, HORIZON, A = 2, 5, 0          # freshness bound, last instant, the item's one signed instant
LEAVES = (1, 2)
PARTS = ("header", "fork", "leaf1", "leaf2", "bad1")   # bad1: leaf 1 with a proof that does not match


def item_counts(held, leaf, reading):
    """held: {part: first_held}. Does `leaf` count on the item side?"""
    if "header" not in held or "fork" in held: return False
    k = f"leaf{leaf}"
    if k not in held: return False
    th, tl = held["header"], held[k]
    first = {"both": max(th, tl), "leaf": tl, "header": th}[reading]
    return first - A <= W


def rows_counts(held, leaf):
    """The same leaves as separately signed rows: row i is first held when the node first held header and leaf i."""
    k = f"leaf{leaf}"
    if "header" not in held or k not in held: return False
    return max(held["header"], held[k]) - A <= W


def check(reading):
    fail, n = {}, 0
    def note(p, *w): fail.setdefault(p, w)
    for size in range(0, len(PARTS) + 1):
        for parts in itertools.combinations(PARTS, size):
            for times in itertools.product(range(HORIZON + 1), repeat=size):
                n += 1; held = dict(zip(parts, times))
                for leaf in LEAVES:
                    c = item_counts(held, leaf, reading)
                    if "fork" not in held and c != rows_counts(held, leaf): note("S1", held, leaf)
                    other = f"leaf{3 - leaf}"
                    without = {k: v for k, v in held.items() if k != other}
                    if item_counts(without, leaf, reading) != c: note("S2", held, leaf)
                    if "fork" in held and c: note("S6", held, leaf)
                    k = f"leaf{leaf}"
                    if k in held and "header" in held and "fork" not in held and held[k] < held["header"]:
                        together = dict(held); together[k] = held["header"]
                        if item_counts(together, leaf, reading) != c: note("S3", held, leaf)
                if set(held) <= {"header"} and any(item_counts(held, l, reading) for l in LEAVES): note("S4", held)
                if "bad1" in held and "leaf1" not in held and item_counts(held, 1, reading): note("S5", held)
                if any(item_counts(dict(reversed(list(held.items()))), l, reading) != item_counts(held, l, reading) for l in LEAVES): note("S7", held)
    return n, fail


EXPECTED = {"both": set(), "leaf": {"S1", "S3"}, "header": {"S1"}}


def main():
    rc = 0
    for reading in ("both", "leaf", "header"):
        n, fail = check(reading)
        bad = set(fail); ok = bad == EXPECTED[reading]; rc |= 0 if ok else 1
        print(f"  a leaf is fresh by {reading:6}: {n} cases, fails {', '.join(sorted(bad)) or 'nothing'}" + ("" if ok else f"  FAIL expected {sorted(EXPECTED[reading]) or 'nothing'}"))
        if "-v" in sys.argv or not ok:
            for p in sorted(bad): print(f"    {p}: {fail[p]}")
    print("set_item: the law holds when a leaf is first held at the later of its own and its header's instants; the other two readings break it" if not rc else "set_item: FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
