#!/usr/bin/env python3
"""
The strict fold at tips, checked over every set of versions roster_fork enumerates (fold.py over fork.py).

Properties, over every set of at most K versions in each setting:
    removed_out      no key a valid version removed is in the roster
    past_count       where the adversary meets the count neither over the members common to the tips nor over
                     the rest of the folded roster, the fold seats no adversary key whose every adding version
                     was signed by adversary keys alone
    policy_holds     tips that differ in policy seat nobody who is not common to them
    honest_sooner    (a count, not a property) sets where the fold lists an honest member M0 leaves out
    authored_seats   adding an outsider's own admission to a set never takes an honest member out of the roster.
                     A resignation can: it is counted, as a cost, and its first trace printed
    authored_counts  adding an authored head to a set never takes a member out of what a version naming every
                     tip is counted over, but its own signer when it resigns
    back_to_one      from every set, one version signed by the honest members alone leaves one tip, with every
                     honest member listed and no removed key in (fork.best_row, where no policy differs)
    a_function       the roster is computed from the set alone (the fold reads no order)

Planted breaks, each of which must fail the property named:
    plain            an add is folded whatever its count leaned on              -> past_count
    one_step         an add's count discounts the voices of members who are out, and still counts the voice of
                     a key the fold itself does not seat (a forged line of two)  -> past_count
    keeps_removed    a member a tip removed stays in the fold                   -> removed_out
    policy_folds     tips that differ in policy are folded                      -> policy_holds
    authored_wait    an authored tip makes the roster the common members        -> authored_seats
    narrow           a version naming the tips is counted over the members common to every head, an authored
                     head included (the first wording)                         -> authored_counts

    python3 -I models/roster_fork/fold_check.py            exit 1 on any difference
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
import fork as F  # noqa: E402
import fold as FD  # noqa: E402

m = lambda s: sum(1 << int(c) for c in s)
# (name, protocol, n, R0, F, K, regime, authored, policy)
SETTINGS = [
    ("majority, one of four", "majority", 5, "0123", "3", 3, True, False, False),
    ("majority, a joiner", "majority", 5, "0123", "4", 3, True, False, False),
    ("three of five, two of them", "quorum3", 5, "01234", "34", 3, True, False, False),
    ("a past count: majority of three, the adversary one seated key, one it loses, one fresh", "majority", 4, "012", "123", 3, False, False, False),
    ("a past count: majority of four, two seated adversary keys and a fresh one", "majority", 5, "0123", "234", 3, False, False, False),
    ("a past count and a forged line of two: majority of three, one seated, one it loses, two fresh", "majority", 5, "012", "1234", 3, False, False, False),
    ("a policy change: majority, one of four", "majority", 5, "0123", "3", 3, True, False, True),
    ("authored heads: majority of four with one adversary, an honest and an adversary outsider", "majority", 6, "0123", "35", 3, True, True, False),
    ("authored heads and a policy change: majority of three, one adversary outsider", "majority", 4, "012", "3", 3, True, True, True),
]
PROPS = ("removed_out", "past_count", "policy_holds", "authored_seats", "authored_counts", "back_to_one")
PLANTS = (("plain", "past_count"), ("one_step", "past_count"), ("keeps_removed", "removed_out"), ("policy_folds", "policy_holds"),
          ("authored_wait", "authored_seats"), ("narrow", "authored_counts"))


def run(setting, want=PROPS):
    name, proto, n, r0, f, K, regime, authored, policy = setting
    W = FD.FoldWorld(n, m(r0), m(f), proto, authored=authored, policy=policy)
    vs = W.vs
    bad = {}
    cost = {}
    sooner = total = 0

    def first(p, S, text):
        if p not in bad:
            bad[p] = "%s\n%s" % (text, F.show(W, S)[0])

    for S in FD.sets(W, K, regime):
        total += 1
        roster, resolved, tips, folded = FD.fold(W, S)
        val = [i for i in S if W.valid(i)]
        dropped = 0
        for i in val: dropped |= vs[i]["drop"]
        common = W.ALL
        for t in tips: common &= vs[t]["R"]
        if roster & W.H & ~common: sooner += 1
        if roster & dropped & W.F and (len(tips) > 1 or regime):
            first("removed_out", S, "the roster %s lists %s, which a valid version removed" % (F.names(W, roster), F.names(W, roster & dropped & W.F)))
        if len(tips) > 1 and not W.meets(W.F, common):
            for zi in range(W.n):
                z = 1 << zi
                if roster & ~common & W.F & z and not W.meets(W.F, roster & ~z):
                    ad = [i for i in FD.adders_of(W, S, z) if i not in W.auth]
                    if ad and all(not (vs[i]["sig"] & W.H) for i in ad):
                        first("past_count", S, "the fold seats %s, added by adversary keys alone" % F.names(W, z))
        if len({W.pol.get(t, 0) for t in tips}) > 1 and roster & ~common:
            first("policy_holds", S, "tips differ in policy and the roster lists %s, not common to them" % F.names(W, roster & ~common))
        if authored and len(S) <= K:
            base0 = W.count_base(tuple(tips))
            for c in W.children(S):
                if c not in W.auth: continue
                kind, bit = W.auth[c]
                me = bit if kind == "resign" else 0
                r2, _, t2, _ = FD.fold(W, S | {c})
                if roster & W.H & ~r2 & ~me:
                    if kind == "admit":
                        first("authored_seats", S | {c}, "an outsider's own admission takes %s out of the roster" % F.names(W, roster & W.H & ~r2 & ~me))
                    else:
                        cost["resign_unseats"] = cost.get("resign_unseats", 0) + 1
                        cost.setdefault("resign_trace", "a resignation takes %s out of the roster until a version names both\n%s"
                                        % (F.names(W, roster & W.H & ~r2 & ~me), F.show(W, S | {c})[0]))
                b2 = W.count_base(tuple(t2))
                if base0 & ~b2 & ~me:
                    first("authored_counts", S | {c}, "an authored head takes %s out of the count of a version naming every tip" % F.names(W, base0 & ~b2 & ~me))
        if ("back_to_one" in want and regime and not resolved and not any(W.pol.get(t, 0) for t in tips)
                and W.meets(W.H, W.count_base(tuple(tips)))):
            ok = False
            for c in W.children(S, honest_only=True):
                r2, res2, _, _ = FD.fold(W, S | {c})
                if res2:
                    listed = 0; d2 = 0
                    for i in [x for x in S | {c} if W.valid(x)]: listed |= vs[i]["R"]; d2 |= vs[i]["drop"]
                    if not (listed & W.H & ~d2 & ~r2) and not (r2 & W.F & d2): ok = True; break
            if not ok:
                first("back_to_one", S, "no one version signed by the honest members alone leaves one tip with the honest members listed")
    return total, sooner, bad, cost


def main():
    rc = 0
    for st in SETTINGS:
        total, sooner, bad, cost = run(st)
        hit = [p for p in PROPS if p in bad]
        print("  %-88s %6d sets: holds %d of %d; an honest member listed sooner than under M0 in %d"
              % (st[0], total, len(PROPS) - len(hit), len(PROPS), sooner) + ("" if not hit else "  FAIL %s" % hit))
        for p in hit:
            print("      %s: %s" % (p, bad[p].replace("\n", "\n        ")))
        if cost.get("resign_unseats"):
            print("      cost: in %d cases %s" % (cost["resign_unseats"], cost["resign_trace"].replace("\n", "\n        ")))
        rc |= 1 if hit else 0
    caught = 0
    for plant, prop in PLANTS:
        FD.MUT.add(plant)
        seen = False
        for st in SETTINGS:
            _, _, bad, _ = run(st, want=())
            if prop in bad: seen = True; break
        FD.MUT.discard(plant)
        caught += seen
        print("  plant %-14s %s (%s)" % (plant, "caught" if seen else "NOT CAUGHT", prop))
        rc |= 0 if seen else 1
    print("RESULT: %s" % ("ok: the strict fold holds %d properties over %d settings; %d of %d planted breaks caught"
                          % (len(PROPS), len(SETTINGS), caught, len(PLANTS)) if not rc else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
