#!/usr/bin/env python3
"""The member relay tree, layered: the quantitative companion to Alm.lean (CC 6.1.6, 5.3.3.2).

Three configurations of the live tree are compared on the numbers that decide whether an addition
is worth its complexity:

  today    one parent per member, whole sealed chunks, loss repaired by a refetch from the parent
  layered  per-layer parents, sibling pull of a missing chunk, a presence floor layer, budget / senders
  rateless layered, plus rateless repair under the sealed chunk at a fixed overhead

Inputs: per-hop chunk loss p, tree depth d, publisher fan-out k, stream rate, the floor layer's rate,
the sender count N and the receiver's budget class. Outputs: the publisher's upload, end-to-end loss,
the repair cost of each configuration, and how many senders stay live. `--check` replays the numbers
Alm.lean proves, so the two stay one model. Integer-only, like the tree it describes.
"""
import sys

RATELESS_OVERHEAD_PERMILLE = 100          # a fixed ~10% code overhead, paid whether or not anything is lost
PRESENCE_FLOOR_BPS = 32                   # a presence tile: colour and a blink at 1 fps
BASE_LAYER_TODAY_BPS = 5000               # the lowest layer a video codec class carries today, about 40 kbps
BUDGETS = {"phone-cellular (unshaped, ~0.5 Mb/s)": 62_500, "wifi (~5 Mb/s)": 625_000, "home (~20 Mb/s)": 2_500_000}


def e2e_loss_permille(p, d):
    """End-to-end loss in permille along d hops at per-hop loss p permille (integer, as Alm.lean)."""
    return (1000 ** d - (1000 - p) ** d) // 1000 ** (d - 1)


def refetch_cost_permille(p, d):
    """A refetch repairs a lost chunk at the cost of the chunk: the repair bytes are the loss rate."""
    return e2e_loss_permille(p, d)


def two_refetches_permille(p, d):
    return e2e_loss_permille(p, d) * p // 1000


def upload(today, fanout, rate):
    return fanout * rate if today else rate


def live_senders(budget, floor):
    return budget // floor


def table():
    print("repair cost, permille of the stream (refetch = e2e loss; rateless = fixed 100)")
    print(f"{'p/hop':>6} {'depth':>5} {'e2e loss':>9} {'>=2 refetch':>11} {'cheaper':>9}")
    for p in (10, 30, 50, 100):
        for d in (3, 5, 8):
            L = e2e_loss_permille(p, d)
            print(f"{p/10:>5.1f}% {d:>5} {L/10:>8.1f}% {two_refetches_permille(p, d)/10:>10.2f}% {'refetch' if L < RATELESS_OVERHEAD_PERMILLE else 'rateless':>9}")
    print()
    rate = 37_500
    print(f"publisher upload at a {rate*8/1000:.0f} kb/s stream")
    for k in (1, 2, 3, 4):
        print(f"  fan-out {k}: today {upload(True, k, rate)/1000:.0f} kB/s, striped {upload(False, k, rate)/1000:.0f} kB/s (+ a chunk map of ~{k*16/1000:.3f} kB/s)")
    print()
    print("senders live at once (budget / per-sender floor)")
    for name, b in BUDGETS.items():
        print(f"  {name}: {live_senders(b, BASE_LAYER_TODAY_BPS):>6} at today's base layer, {live_senders(b, PRESENCE_FLOOR_BPS):>6} at the presence floor")


def check():
    lean = {(10, 5): 49, (30, 5): 141, (50, 5): 226, (100, 8): 569}
    for (p, d), v in lean.items():
        assert e2e_loss_permille(p, d) == v, (p, d, e2e_loss_permille(p, d), v)
    assert all(e2e_loss_permille(10, d) < RATELESS_OVERHEAD_PERMILLE for d in range(1, 9))
    assert all(e2e_loss_permille(50, d) > RATELESS_OVERHEAD_PERMILLE for d in range(3, 9))
    assert live_senders(625_000, 32) == 19531 and live_senders(62_500, 32) == 1953 and live_senders(62_500, 5000) == 12
    print("alm_model: agrees with Alm.lean on every pinned number")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else (table() or 0))
