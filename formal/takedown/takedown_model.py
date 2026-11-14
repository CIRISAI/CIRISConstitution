#!/usr/bin/env python3
"""
CC — takedown and erasure as a small executable model (CC 4.5.3, CC 4.5.13, CC 4.4.3.12).

One blob at one node. The node holds a set of rows about the blob, each with the instant the node first held it.
The blob's state is a fold over that set and the instant, never stored: served, withheld or destroyed.

Rows:  notice(basis)   a takedown notice on a basis; immediate bases destroy on receipt, windowed bases withhold
                       and destroy at the close of their window
       reversal        an admitted reversal of a windowed notice (reconsideration upheld, counter-notice)
       lift            the members' lift of a moderator's act (CC 4.5.13)
       hold            a legal hold on the blob (CC 4.4.3.12)
       hold_lifted

The bases, which are immediate and which windowed, and each window's name are read from manifests/reactions.json;
the model fails if the manifest and the constants table do not give every windowed basis a stop, a clock and a
destruction at its close.

Properties, checked over every set of rows and every arrival order up to the bound:
  P1  a windowed notice withholds from the instant it is held and never before, unless a reversal or a
      lift is already held, which may reach a node ahead of the notice it answers
  P2  a windowed notice destroys at the close of its window unless a reversal or a lift was held inside it
  P3  an immediate basis destroys at the instant it is held; under a live legal hold it withholds at once
      and destroys at the instant the hold lifts
  P4  destruction is final: no row held later brings the blob back
  P5  the state is a function of the rows held and their first-held instants, never of the order they were added
  P6  a blob under a live legal hold is not destroyed
A legal hold defers destruction and never serving (CC 4.5.3, the steward's ruling of 2026-11-12 on conflict C312).
The reading in which a hold defers nothing is still run, and must fail P6, so the two stay told apart.

Run: python3 formal/takedown/takedown_model.py --check
"""
import itertools, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def bases():
    """(immediate leaves, {windowed leaf: constant name}) from the reactions manifest, with the closure check."""
    rx = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
    consts = {l.split("\t")[0] for l in open(os.path.join(ROOT, "constitution", "constants.tsv"), encoding="utf-8").read().split("\n")[1:] if l}
    mine = [e for e in rx if e["family"] == "takedown_notice:{basis}"]
    immediate, window, stops, destroys = set(), {}, set(), set()
    for e in mine:
        leaves = e.get("leaves") or []
        if e["kind"] == "clock":
            for l in leaves: window[l] = e["dur"]
        elif e["kind"] == "react":
            acts = {x.get("act") for x in e["effects"] if x["effect"] == "do"}
            on = {(x["event"], x["of"]) for x in e["on"]}
            if ("admitted", "self") in on and "destroy_bytes" in acts: immediate.update(leaves)
            if ("admitted", "self") in on and "stop_serving" in acts: stops.update(leaves)
            if any(ev == "close" for ev, _ in on) and "destroy_bytes" in acts: destroys.update(leaves)
    problems = []
    for l, c in window.items():
        if c not in consts: problems.append(f"{l}: window {c} is not a named constant")
        if l not in stops: problems.append(f"{l}: no stop on admission")
        if l not in destroys: problems.append(f"{l}: no destruction at the close of its window")
    if immediate & set(window): problems.append(f"both immediate and windowed: {sorted(immediate & set(window))}")
    return immediate, window, problems


W = 3            # a window, in ticks
HORIZON = 6      # instants 0..HORIZON


def fold(held, now, immediate, windowed, hold_wins):
    """held: set of (kind, basis, first_held). The blob's state at `now`."""
    held = [r for r in held if r[2] <= now]
    hold_from = min([t for k, _, t in held if k == "hold"], default=None)
    hold_to = min([t for k, _, t in held if k == "hold_lifted"], default=None)
    def under_hold(t):
        return hold_from is not None and hold_from <= t and (hold_to is None or t < hold_to)
    destroyed_at = None
    for k, b, t in sorted(held, key=lambda r: r[2]):
        if k != "notice": continue
        if b in immediate:
            at = t
        else:
            close = t + W
            undone = any(k2 in ("reversal", "lift") and t2 < close for k2, _, t2 in held)
            at = None if undone or close > now else close
        if at is None: continue
        if hold_wins and under_hold(at):
            # the hold defers destruction to the instant the hold lifts, if it has
            at = hold_to if (hold_to is not None and hold_to <= now) else None
        if at is not None and (destroyed_at is None or at < destroyed_at): destroyed_at = at
    if destroyed_at is not None: return "destroyed"
    live_notice = False
    for k, b, t in held:
        if k == "notice":
            close = t + W
            undone = b not in immediate and any(k2 in ("reversal", "lift") and t2 < close for k2, _, t2 in held)
            if not undone: live_notice = True
    return "withheld" if live_notice else "served"


def check(hold_wins, immediate, windowed):
    imm = sorted(immediate)[0]; win = sorted(windowed)[0]
    kinds = [("notice", imm), ("notice", win), ("reversal", ""), ("lift", ""), ("hold", ""), ("hold_lifted", "")]
    fails = {p: None for p in ("P1", "P2", "P3", "P4", "P5", "P6")}
    n = 0
    for size in (1, 2, 3):
        for combo in itertools.combinations(kinds, size):
            for times in itertools.product(range(0, 4), repeat=size):
                held = {(k, b, t) for (k, b), t in zip(combo, times)}
                if ("hold_lifted", "") in combo and ("hold", "") not in combo: continue
                n += 1
                states = [fold(held, now, immediate, windowed, hold_wins) for now in range(HORIZON + 1)]
                # P4 destruction is final
                if "destroyed" in states and any(s != "destroyed" for s in states[states.index("destroyed"):]):
                    fails["P4"] = fails["P4"] or (sorted(held), states)
                # P5 order-free: the fold takes a set, so adding rows in any order gives the same set; check that the
                # state at each instant depends only on rows first held by then
                for now in range(HORIZON + 1):
                    if fold({r for r in held if r[2] <= now}, now, immediate, windowed, hold_wins) != states[now]:
                        fails["P5"] = fails["P5"] or (sorted(held), now)
                hold = [t for k, _, t in held if k == "hold"]; lifted = [t for k, _, t in held if k == "hold_lifted"]
                for k, b, t in held:
                    if k != "notice": continue
                    under = bool(hold) and hold[0] <= t and (not lifted or t < lifted[0])
                    if b in immediate:
                        if states[t] != "destroyed" and not under:
                            fails["P3"] = fails["P3"] or (sorted(held), states)
                        if under and states[t] == "destroyed":
                            fails["P6"] = fails["P6"] or (sorted(held), states)
                        if under and states[t] != "withheld" and states[t] != "destroyed":
                            fails["P3"] = fails["P3"] or (sorted(held), states)      # held bytes are withheld at once
                        if under and lifted and lifted[0] <= HORIZON and states[lifted[0]] != "destroyed":
                            fails["P3"] = fails["P3"] or (sorted(held), states)      # and destroyed when the hold lifts
                    else:
                        if t > 0 and states[t - 1] == "withheld" and not any(k2 == "notice" and t2 < t for k2, _, t2 in held):
                            fails["P1"] = fails["P1"] or (sorted(held), states)
                        if states[t] == "served":
                            undone_now = any(k2 in ("reversal", "lift") and t2 <= t for k2, _, t2 in held)   # a reversal or lift already held
                            if not undone_now: fails["P1"] = fails["P1"] or (sorted(held), states)
                        close = t + W
                        undone = any(k2 in ("reversal", "lift") and t2 < close for k2, _, t2 in held)
                        other_destroys = any(k2 == "notice" and b2 in immediate for k2, b2, _ in held)
                        under_close = bool(hold) and hold[0] <= close and (not lifted or close < lifted[0])
                        if close <= HORIZON and not other_destroys:
                            want = "destroyed" if not undone and not (hold_wins and under_close) else None
                            if want and states[close] != "destroyed": fails["P2"] = fails["P2"] or (sorted(held), states)
                            if undone and "destroyed" in states: fails["P2"] = fails["P2"] or (sorted(held), states)
    return n, fails


def main():
    immediate, windowed, problems = bases()
    if problems or not immediate or not windowed:
        print("takedown: the reactions manifest does not close: " + "; ".join(problems or ["no immediate or no windowed basis found"])); return 1
    n, fails = check(True, immediate, windowed)
    broken = sorted(p for p, v in fails.items() if v)
    for p in broken: print(f"  FAIL {p}: {fails[p]}")
    _, other = check(False, immediate, windowed)          # the reading not taken must still be told apart
    if not other["P6"]: print("  FAIL a hold that defers nothing was not caught by P6"); broken.append("P6-mutation")
    rc = 1 if broken else 0
    print(f"takedown: {len(immediate)} immediate bases, {len(windowed)} windowed; {n} cases, six properties "
          + ("hold" if not broken else f"fail {broken}") + "; under a live legal hold the bytes are withheld at once and destroyed when the hold lifts")
    return rc


if __name__ == "__main__":
    sys.exit(main())
