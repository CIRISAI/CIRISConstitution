#!/usr/bin/env python3
"""
CC — two versions of one roster head, checked over every set of versions an adversary can cause.

`fork.py` enumerates every set of at most K roster versions that can exist when an adversary holds some keys
and signs anything, naming any head, and an honest key signs only what it accepts. A rule is then a function
from the set to a roster. This check runs the rule in force (the first version seen wins, CC 3.2 T6) and the
rule `M0` beside it:

    M0   tips wait. With one tip the roster is its roster. With several it is the members common to all, until a
         version names the tips, is counted over the members common to them, and states what it takes from each.
         A removal reaches the rows of the removed key that no concurrent head has in its past.

What must hold for M0 while the adversary is below the count:
    the roster is a function of the set; one tip never gives a wrong roster; no removed key is listed; the
    adversary alone signs no valid version; no valid version is later made invalid; a removal naming an old head
    voids nothing that one naming the newest head would let count; the honest members can always sign back to
    one head.
What M0 costs, and is expected here: a member added on one tip is not listed until a version names both tips;
and a version stays valid on a voice that a sibling removes, since the voice was good at the head it named.
The first-seen rule must fail to be a function of the set.

Run: python3 -I formal/roster_fork/fork_check.py --check     (three settings, K = 3, one process)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from fork import check

m = lambda s: sum(1 << int(c) for c in s)
SETTINGS = [("majority, one of four", "majority", 5, "0123", "3", ""),
            ("majority, a joiner", "majority", 5, "0123", "4", ""),
            ("three of five, two of them", "quorum3", 5, "01234", "34", "")]
MUST = ("function", "nsf_resolved", "kept_removed", "adv_alone", "not_final", "stale", "rejoin")
COST = ("nsf_now", "removed_voice")


def main():
    rc = 0
    for name, proto, n, r0, f, fo in SETTINGS:
        t6 = check("T6", n, m(r0), m(f), proto, 3, m(fo), regime=True)
        m0 = check("M0", n, m(r0), m(f), proto, 3, m(fo), regime=True)
        bad = [k for k in MUST if m0.get(k)]
        cost = [k for k in COST if m0.get(k)]
        ok = not bad and bool(t6.get("function"))
        rc |= 0 if ok else 1
        print(f"  {name:28} {m0['sets']:6} sets: tips wait holds {len(MUST) - len(bad)} of {len(MUST)}"
              + (f", costs {len(cost)} of {len(COST)}" if cost else ", no cost shown")
              + ("; first seen wins is not a function of the set" if t6.get("function") else "; FAIL first seen was not caught")
              + ("" if not bad else f"  FAIL {bad}"))
    print("roster_fork: with tips waiting on a version that names them, the roster is a function of the set and the adversary below the count gains nothing" if not rc else "roster_fork: FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
