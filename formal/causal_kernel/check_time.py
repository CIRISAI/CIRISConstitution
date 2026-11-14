#!/usr/bin/env python3
"""
check_time.py: which notion of time each reading of the text needs.

The kernel keeps two notions of time (formal/KERNEL.md section 5):
    own end   a row states its own end, read from the row alone against the node's clock      (the `state` answer)
    window    a window opened by a row, closed by a landing on the concluder's own two instants (the `window` answer)
and reads everything else from what rows name: the cut by causal past (section 6, `stands` and `state`) and the
order of section 6 (a row naming another decides; concurrent rows are both or neither).

A reading is COVERED when it is a function of what those read: each row's stated end and now; the window's
receipt and landing instants of one concluder; and which rows name which. The check runs each reading over a grid of
worlds of two rows A and B (signed instants, the instants this node first held them, and whether one names the
other), groups the worlds by that view, and looks for a WITNESS PAIR: two worlds the view cannot tell apart that the
reading sends to different results. A reading with a pair needs a signed instant or a first-held instant beyond the
two notions, and is recorded as not covered.

    python3 -I check_time.py            compares with time_expected.tsv; exit 1 on any difference, or if the plant
                                        (a made-up reading comparing two signers' instants) is not found
    python3 -I check_time.py --write    writes time_expected.tsv
"""
import itertools
import os
import resource
import sys

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))

SIGNED = (10, 20, 45)
HELD = (12, 25, 48)
NAMES = ("none", "B names A", "A names B")
W = 15                          # a freshness window, in the grid's units
NOW = 50
LANDING = (0, 30)               # the concluder's own receipt and landing instants


def worlds():
    for aa, ab, ha, hb, nm in itertools.product(SIGNED, SIGNED, HELD, HELD, NAMES):
        if ha < aa or hb < ab: continue                     # a node holds a row only after it was signed (honest clocks)
        if nm == "B names A" and ab < aa or nm == "A names B" and aa < ab: continue   # a row is signed after what it names
        yield {"A": {"signed": aa, "end": 40, "held": ha}, "B": {"signed": ab, "end": 60, "held": hb},
               "names": nm, "now": NOW, "landing": LANDING}


def view(w):
    """What the two notions and the rows' naming read."""
    return (w["A"]["end"], w["B"]["end"], w["now"], w["landing"], w["names"])


def section6_holder(w):
    """A registration holds against every registration in its past; concurrent ones are contested."""
    return {"B names A": "B", "A names B": "A"}.get(w["names"], "contested")


# reading, covered by, the text it reads, the function
READINGS = [
    ("own end: A live iff now is before A's stated end", "own end", "every expiry member (reactions.json, 20 entries)",
     lambda w: w["now"] < w["A"]["end"]),
    ("window: the concluder's landing spans its window", "window", "every clock of reactions.json read as a window (CC 4.5.13)",
     lambda w: w["landing"][1] - w["landing"][0] >= 24),
    ("cut: B counts iff the ending row A names it", "cut", "KERNEL section 6; G3 of formal/derivation/order/witnesses.tsv",
     lambda w: w["names"] == "A names B"),
    ("invitation as a door: the widening lands inside its concluder's own window", "window", "CC 3.1.3.2 (3)-(4), read on the door (check_door.py)",
     lambda w: w["landing"][1] - w["landing"][0] < 7 * 86400),
    ("name registration: held by what the registrations name, concurrent ones contested", "section 6", "CC 4.5.1.3",
     section6_holder),
    ("cosignature attach, restated: the cosignature states its own end", "own end", "CC 3.2 T4a, with a stated end (a wire member, not today's)",
     lambda w: w["now"] < w["B"]["end"]),
    # readings the two notions do not cover, kept as recorded verdicts
    ("freshness W as written: A counts iff first held within W of its signed instant", "cut", "CC 2.6.7; replaced by the cut (check_door.py, G3)",
     lambda w: w["A"]["held"] - w["A"]["signed"] <= W),
    ("invitation as written: B counts iff B's signed instant is not after A's stated end", "window", "CC 3.1.3.2 (3); replaced by the door with late answers closed",
     lambda w: w["B"]["signed"] <= w["A"]["end"]),
    ("cosignature attach as written: the newest cosignature no older than the attach window when first held", "not covered", "CC 3.2 T4a; part_5 head chain",
     lambda w: w["B"]["held"] - w["B"]["signed"] <= W),
    ("session order as written: the earliest claimed instant of two occurrences holds the session", "not covered", "CC 3.1.3.1",
     lambda w: "A" if (w["A"]["signed"], "A") < (w["B"]["signed"], "B") else "B"),
    # the plant
    ("plant: B counts iff B was signed after A", "not covered", "made up: two signers' instants compared",
     lambda w: w["B"]["signed"] > w["A"]["signed"]),
]


def pair_of(f):
    seen = {}
    for w in worlds():
        v, r = view(w), f(w)
        if v in seen and seen[v][1] != r:
            a, ra = seen[v]
            return "A signed %d held %d, B signed %d held %d -> %s | A signed %d held %d, B signed %d held %d -> %s (%s)" % (
                a["A"]["signed"], a["A"]["held"], a["B"]["signed"], a["B"]["held"], ra,
                w["A"]["signed"], w["A"]["held"], w["B"]["signed"], w["B"]["held"], r, w["names"])
        seen.setdefault(v, (w, r))
    return None


def main():
    write = "--write" in sys.argv
    say = lambda s: print(s, flush=True)
    n = sum(1 for _ in worlds())
    say("%d worlds of two rows: signed instants %s, first held %s, naming %s; grouped by what the two notions and the naming read" % (
        n, SIGNED, HELD, ", ".join(NAMES)))
    got, plant_found = [], False
    for label, by, text, f in READINGS:
        pair = pair_of(f)
        if label.startswith("plant"): plant_found = pair is not None
        as_written = label.split(":")[0].endswith("as written")
        if pair is None:
            verdict = "covered by %s" % by
        elif as_written and by != "not covered":
            verdict = "needs an instant beyond the two notions as written; the kernel's replacement: %s" % by
        else:
            verdict = "not covered: needs an instant beyond the two notions"
        say("  %s\n      %s [%s]%s" % (label, verdict, text, "" if pair is None else "\n      witness pair: " + pair))
        got.append((label, by, verdict))
    say("  the plant (two signers' instants compared) %s" % ("is found and reported as not covered" if plant_found else "WAS NOT FOUND"))
    path = os.path.join(HERE, "time_expected.tsv")
    lines = ["reading\tcovered_by\tverdict"] + ["\t".join(g) for g in got]
    if write:
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        say("wrote time_expected.tsv (%d readings)" % len(got))
        diff = []
    else:
        want = open(path, encoding="utf-8").read().rstrip("\n").split("\n") if os.path.exists(path) else []
        diff = sorted(set(want) ^ set(lines))
        for l in diff: say("  differs from time_expected.tsv: %s %s" % ("expected" if l in want else "now", l))
    ok = plant_found and not diff
    say("RESULT: %s" % ("ok" if ok else "NOT OK"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
