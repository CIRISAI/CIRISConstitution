#!/usr/bin/env python3
"""
CC — the guardianship of a minor when it is contested, as a small executable model (CC 3.2).

One minor with a current guardian. A court's order names a new guardian. A node holds some of these rows:

    order(minor)      the minor's attestation of the order
    order(displaced)  the attestation of the guardian the order displaces
    order(named)      the attestation of the guardian the order names
    refusal           the minor's attestation that they refuse the named guardian
    step_down         the current guardian's own withdrawal of its binding
    bind(named)       the named guardian's `delegates_to` over the minor
    act(displaced), act(named)   a new act of a guardian over the minor, offered at the door

The band on record is `under_13`, `13_15`, `16_17`, or none. The verdict is a fold over the rows held:

    guardian   current | named | none
    contested  whether a contest stands
    mode       normal | floor (the minor operates under the floor of CC 3.4.13) | stopped (no live guardian)
    report     whether the safeguarding report has been raised
    acts       which offered guardian acts are admitted

Properties, over every set of rows at every band:
  G1  there is at most one guardian, and it changes only by a step-down or an admitted order
  G2  the named guardian's own rows never displace the current guardian alone
  G3  the minor's word opens a contest at every band and where no band is on record
  G4  below 13, and with no band, the minor's word never counts toward admitting the order
  G5  from 13 the minor's word with the named guardian's admits the order
  G6  at 16 and 17 the minor's refusal blocks an order the two guardians attest
  G7  a contest never stops the minor: the mode under a contest is the floor, never stopped
  G8  while a contest stands no new act of either guardian is admitted
  G9  a contest raises the report
  G10 with no attestation of an order, or once every one is withdrawn, there is no contest and nothing is frozen
  G11 the verdict depends only on the rows held and the band

Run: python3 formal/guardianship/guardianship_model.py --check
"""
import itertools, sys

BANDS = ("under_13", "13_15", "16_17", None)
ROWS = ("order_minor", "order_displaced", "order_named", "refusal", "step_down", "bind_named", "act_displaced", "act_named")
ORDER = ("order_minor", "order_displaced", "order_named")


def admitted(held, band):
    """The order is admitted: the named guardian always attests with another, by the band's rule."""
    if "order_named" not in held: return False
    m, d = "order_minor" in held, "order_displaced" in held
    if band in ("under_13", None): return d
    if band == "13_15": return m or d
    return m or (d and "refusal" not in held)          # 16_17


def fold(held, band):
    held = frozenset(held)
    order = admitted(held, band)
    stepped = "step_down" in held
    if (order or stepped) and "bind_named" in held: guardian = "named"
    elif stepped or order: guardian = "none" if stepped else "current"   # an admitted order waits for the named guardian's binding
    else: guardian = "current"
    contested = any(r in held for r in ORDER) and not order and not stepped
    mode = "stopped" if guardian == "none" else "floor" if contested else "normal"
    acts = set()
    if not contested:
        if "act_displaced" in held and guardian == "current": acts.add("act_displaced")
        if "act_named" in held and guardian == "named": acts.add("act_named")
    return {"guardian": guardian, "contested": contested, "mode": mode, "report": contested, "acts": frozenset(acts)}


def check(fold=fold):
    fail = {}
    def note(p, *w): fail.setdefault(p, w)
    n = 0
    for band in BANDS:
        for k in range(len(ROWS) + 1):
            for held in itertools.combinations(ROWS, k):
                n += 1; H = set(held); v = fold(H, band)
                if v["guardian"] == "named" and not ("step_down" in H or admitted(H, band)): note("G1", band, held)
                if v["guardian"] != "current" and H <= {"order_named", "bind_named", "act_named", "refusal", "act_displaced"}: note("G2", band, held)
                if H == {"order_minor"} and not (v["contested"] and v["report"]): note("G3", band, held)
                if band in ("under_13", None) and "order_displaced" not in H and "step_down" not in H and v["guardian"] != "current": note("G4", band, held)
                if band in ("13_15", "16_17") and {"order_minor", "order_named", "bind_named"} <= H and v["guardian"] != "named": note("G5", band, held)
                if band == "16_17" and {"order_displaced", "order_named", "refusal", "bind_named"} <= H and "order_minor" not in H and "step_down" not in H and v["guardian"] == "named": note("G6", band, held)
                if v["contested"] and v["mode"] != "floor": note("G7", band, held)
                if v["contested"] and v["acts"]: note("G8", band, held)
                if v["contested"] and not v["report"]: note("G9", band, held)
                if not any(r in H for r in ORDER) and (v["contested"] or v["mode"] == "floor"): note("G10", band, held)
                if fold(set(reversed(held)), band) != v: note("G11", band, held)
    return n, fail


def main():
    n, fail = check()
    for p, w in sorted(fail.items()): print(f"  FAIL {p}: {w}")
    print(f"guardianship: {n} cases over four bands, eleven properties " + ("hold" if not fail else f"fail {sorted(fail)}"))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
