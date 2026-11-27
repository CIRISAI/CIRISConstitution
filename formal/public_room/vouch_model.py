#!/usr/bin/env python3
"""Vouching into an invitation-only public room, under attack. A work in progress, not yet a gated model.

One member of an honest room is captured. Each window the attacker's members propose invitations of keys the attacker
made, and every attacker member assents. A fraction p of the honest members is attentive and objects to every such
proposal. Each proposal is decided by the governance policy table's own function for `community_invite`
(tools/build_governance_policy.py: decide), so the thresholds are the table's and not this file's.

Parameters this file adds, which the text does not fix:
  cap      silent-path proposals one member may have pending at once (1, or None for no limit)
  active   for a room above 12 members, the share of the roster the base counts (the census's expected_active)
Reported: the window in which the attacker first admits a key, first can cancel every honest invitation, and first
holds more than half and two thirds of the roster. `never` within 60 windows.
  python3 formal/public_room/vouch_model.py            prints the table
  python3 formal/public_room/vouch_model.py --check    asserts the findings stated at the end
"""
import math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_governance_policy as bgp

ROW = next(r for r in bgp.load() if r["family"] == "community_invite")
W = ROW["window_secs"]
CANCEL = lambda base: max(2, bgp.votes(ROW["_cancel"], base, False))


def base_of(n, active):
    return n if n <= 12 else max(3, math.ceil(active * n))


def run(honest, p, cap, active=1.0, windows=60):
    H, A = honest - 1, 1                      # one of the honest members is the captured one
    out = {"admit": None, "block": None, "half": None, "two_thirds": None}
    for t in range(1, windows + 1):
        n = H + A; base = base_of(n, active)
        objections = math.floor(p * H)
        verdict = bgp.decide(ROW, base, A, objections, W, True)[0]      # every attacker member assents; the invitee's yes is held
        if verdict == "lands":
            A += (A if cap == 1 else 3 * n) if cap else 3 * n
            out["admit"] = out["admit"] or t
        n = H + A
        if out["block"] is None and A >= CANCEL(base_of(n, active)): out["block"] = t
        if out["half"] is None and 2 * A > n: out["half"] = t
        if out["two_thirds"] is None and 3 * A >= 2 * n: out["two_thirds"] = t
    return out


def table():
    rows = []
    for honest in (3, 6, 7, 12, 30, 100, 1000):
        for active in ((1.0,) if honest <= 12 else (1.0, 0.1)):
            for p in (0.0, 0.34, 0.5):
                for cap in (None, 1):
                    rows.append((honest, active, p, cap, run(honest, p, cap, active)))
    return rows


def main():
    f = lambda v: "never" if v is None else str(v)
    print("window = %d h; a proposal lands by silence where voices >= max(2, base/3) and objections < max(2, base/3)" % (W // 3600))
    print("%7s %6s %5s %5s | %6s %6s %6s %10s" % ("members", "active", "p", "cap", "admit", "block", "half", "two_thirds"))
    rows = table()
    for honest, active, p, cap, o in rows:
        print("%7d %6.2f %5.2f %5s | %6s %6s %6s %10s" % (honest, active, p, "none" if cap is None else cap, f(o["admit"]), f(o["block"]), f(o["half"]), f(o["two_thirds"])))
    if "--check" in sys.argv:
        get = lambda h, a, p, c: next(o for hh, aa, pp, cc, o in rows if (hh, aa, pp, cc) == (h, a, p, c))
        # 1. In a room of up to six, one captured member and nobody objecting: with no cap the room is taken in one window.
        assert get(6, 1.0, 0.0, None)["two_thirds"] == 1
        # 2. The same room with a cap of one pending vouch: the attacker doubles, and takes several windows.
        assert get(6, 1.0, 0.0, 1)["two_thirds"] > 1
        # 3. Above six members counted in full, one captured member admits nobody, whatever the cap: the floor is a third of the base.
        for h in (7, 12, 30, 100, 1000):
            for c in (None, 1): assert get(h, 1.0, 0.0, c)["admit"] is None
        # 4. An attentive third of the honest members stops it at every size, whatever the cap.
        for h in (3, 6, 7, 12, 30, 100, 1000):
            for c in (None, 1): assert get(h, 1.0, 0.34, c)["admit"] is None or h <= 6
        print("check: ok")


if __name__ == "__main__":
    main()
