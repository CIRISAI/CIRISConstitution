#!/usr/bin/env python3
"""
CC — who owns a key, as a small executable model (CC 3.2 "Who owns a key").

One key K. Rows about it reach a node in some order:

    bind(X, cosigned, scope)   an owner-binding signed by X, cosigned by K's own key or not, at `self` or wider
    withdraw(X)                X's withdrawal of its bindings on K
    occurrence(X)              an `identity_occurrence` placing K under X's identity

`owner_of(K)` is the one owner the live bindings name, and nothing when they name none or more than one.

CC 3.2 says a second owner is refused when the binding is admitted, and that the first binding carries the
node's own cosign. It leaves two things to the reader, and the model runs each way:

    refusal   final      a refused binding is dropped
              again      a refused binding is offered again when the rows held change
              fold       nothing is refused; the reader counts the live cosigned bindings, and any count
                         other than one is no owner
    cosign    first      only the first binding a node ever admits needs the node's cosign
              unowned    every binding onto a key with no live owner needs it

Properties, over every set of up to four rows in every order of arrival:

  O1  a node never reads two owners
  O2  the owner's own re-signed rows at wider scopes change nothing
  O3  an occurrence row changes nothing
  O4  ownership passes from X to another owner only when X's withdrawal is held; a second binding may leave
      the key with no owner, and never hands it to its signer
  O5  a binding the node's key did not cosign, from a key that is not the owner, never makes its signer the owner
  O6  two nodes that have been offered the same rows read the same owner, whatever the order (the node's key
      having cosigned one binding for each time the key stood unowned)
  O7  the same, where the node's key cosigned two bindings for one unowned period
  O8  a reader that holds two live owners reads none and never picks one

The rule is the last reading: nothing is refused and forgotten, the reader counts the live bindings the node's
own key cosigned, and any count other than one is no owner (CC 3.2). It holds all eight. Every reading with a door
that refuses gives something up, and the check pins what, so the reason the door went is on record (C557).

Run: python3 formal/owner_binding/owner_binding_model.py --check
"""
import itertools, sys

OWNERS = ("A", "B", "C")
ROWS = [("bind", o, c, s) for o in OWNERS for c in (True, False) for s in ("self", "wide")] + \
       [("withdraw", o) for o in OWNERS] + [("occurrence", "B")]
READINGS = [(r, c) for r in ("final", "again") for c in ("first", "unowned")] + [("fold", "unowned")]


def run(order, refusal, cosign):
    """Return the series of owner_of after each arrival."""
    held, pending, withdrawn, ever, series = [], [], set(), False, []

    def live():
        return {r[1] for r in held if r[0] == "bind" and r[1] not in withdrawn}

    def offer(r):
        nonlocal ever
        x = r[1]
        if x in withdrawn: return True                       # dead on arrival, held and inert
        now = live()
        if now and now != {x}: return False                  # a different owner is live: refused
        if not now and not r[2] and (cosign == "unowned" or not ever): return False
        held.append(r); ever = True
        return True

    for r in order:
        if refusal == "fold":
            if r[0] == "withdraw": withdrawn.add(r[1])
            elif r[0] == "bind": held.append(r)
            owners = {x[1] for x in held if x[2] and x[1] not in withdrawn}
            series.append(next(iter(owners)) if len(owners) == 1 else None)
            continue
        if r[0] == "withdraw": withdrawn.add(r[1])
        elif r[0] == "bind" and not offer(r) and refusal == "again": pending.append(r)
        if refusal == "again":
            moved = True
            while moved:
                moved = False
                for p in list(pending):
                    if offer(p): pending.remove(p); moved = True
        now = live()
        assert len(now) <= 1, (order, now)
        series.append(next(iter(now)) if now else None)
    return series


def honest(rows):
    """The node's key cosigned one binding per unowned period: the cosigned owners form a chain of handovers."""
    cos = {r[1] for r in rows if r[0] == "bind" and r[2]}
    wd = {r[1] for r in rows if r[0] == "withdraw"}
    return len(cos - wd) <= 1


def equivocated(rows):
    cos = {r[1] for r in rows if r[0] == "bind" and r[2]}
    wd = {r[1] for r in rows if r[0] == "withdraw"}
    return len(cos - wd) >= 2


def check(refusal, cosign):
    fail = {p: None for p in ("O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8")}
    n = 0
    for size in (1, 2, 3, 4):
        for rows in itertools.combinations(ROWS, size):
            finals = {}
            for order in itertools.permutations(rows):
                n += 1
                try: series = run(order, refusal, cosign)
                except AssertionError as e: fail["O1"] = fail["O1"] or e.args[0]; continue
                finals[order] = series[-1]
                prev = None
                for i, (r, now) in enumerate(zip(order, series)):
                    if prev is not None and now is not None and now != prev and not (r[0] == "withdraw" and r[1] == prev):
                        fail["O4"] = fail["O4"] or (order, series)
                    prev = now
                if refusal == "fold":
                    for i, now in enumerate(series):
                        wd = {x[1] for x in order[:i + 1] if x[0] == "withdraw"}
                        if now is not None and len({x[1] for x in order[:i + 1] if x[0] == "bind" and x[2]} - wd) > 1:
                            fail["O8"] = fail["O8"] or (order, series)
                # O5: no owner the node's key never cosigned
                for i, now in enumerate(series):
                    if now is not None and not any(x[0] == "bind" and x[1] == now and x[2] for x in order[:i + 1]):
                        fail["O5"] = fail["O5"] or (order, series)
                # O2, O3: drop the wide re-signs of an owner whose self row is present, and occurrences
                if refusal != "fold":
                    slim = tuple(r for r in order if not (r[0] == "occurrence"))
                    if run(slim, refusal, cosign)[-1:] != series[-1:] and slim: fail["O3"] = fail["O3"] or (order, series)
                    i_self = {r[1]: i for i, r in enumerate(order) if r[0] == "bind" and r[3] == "self"}
                    slim = tuple(r for i, r in enumerate(order) if not (r[0] == "bind" and r[3] == "wide" and r[1] in i_self and i_self[r[1]] < i and
                                                                         any(x == ("bind", r[1], True, "self") for x in order[:i]) ))
                    if slim and run(slim, refusal, cosign)[-1] != series[-1]: fail["O2"] = fail["O2"] or (order, series)
            if len(set(finals.values())) > 1:
                a = min(finals, key=str); b = next(o for o in finals if finals[o] != finals[a])
                which = "O6" if honest(rows) else "O7" if equivocated(rows) else None
                if which: fail[which] = fail[which] or ((a, finals[a]), (b, finals[b]))
    return n, fail


# What each reading gives up. The check requires exactly this, so a change to the rule shows as a change here.
EXPECTED = {("final", "first"): {"O2", "O5", "O6", "O7"}, ("final", "unowned"): {"O2", "O6", "O7"},
            ("again", "first"): {"O5", "O6", "O7"}, ("again", "unowned"): {"O7"}, ("fold", "unowned"): set()}


def main():
    rc = 0
    for refusal, cosign in READINGS:
        n, fail = check(refusal, cosign)
        bad = {p for p, v in fail.items() if v}
        ok = bad == EXPECTED[(refusal, cosign)]
        rc |= 0 if ok else 1
        print(f"  refusal {refusal:5} cosign {cosign:7}: {n} runs, gives up {', '.join(sorted(bad)) or 'nothing'}" + ("" if ok else f"  FAIL expected {sorted(EXPECTED[(refusal, cosign)])}"))
        if "-v" in sys.argv:
            for p in sorted(bad): print(f"    {p}: {fail[p]}")
    print("owner_binding: the fold over counted bindings holds O1-O8; each of the four door readings gives up what is pinned (C557)" if not rc else "owner_binding: FAIL")
    return rc

if __name__ == "__main__":
    sys.exit(main())
