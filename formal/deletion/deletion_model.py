#!/usr/bin/env python3
"""
CC — the deletion deadline as a small executable model (CC 3.3.1 D1, CC 4.4.3.5.2, CC 2.4.1.1).

A producer holds a row T about a subject and has committed to delete within a window. The subject revokes or
withdraws; the window starts at the instant this node first held that act. The node holds a set of rows about T,
each with the instant it first held it, and the verdict is a fold over that set and the instant:

    none      no window is running
    running   the window is open
    met       a composer of the producer's against T was held before the window closed
    breach    the window closed with T still present and no composer of the producer's against it

Rows:  subject_revokes     the subject's `consent:state:revoked`, or the subject's own `withdraws` of T
       producer_withdraws  the producer's `withdraws` of T
       producer_supersedes the producer's `supersedes` of T
       producer_deletes    the producer's hard deletion of T (its tombstone)
       producer_complete   the producer's `consent:deletion_complete`: evidence toward the duty, never the duty

Properties, over every set of rows and every arrival instant up to the bound:
  D1  breach exactly when the window has closed with no composer of the producer's held inside it
  D2  a `consent:deletion_complete` row changes no verdict
  D3  the subject's own act starts the window and discharges nothing
  D4  a composer of the producer's held inside the window means no breach at any later instant
  D5  a breach is final: a composer held after the close does not undo it
  D6  the verdict is a function of the rows held and their first-held instants

The same cases are run against the rule as `manifests/reactions.json` carries it: the events that start the
clock and the events that excuse a breach, each with the actor it names. The two must agree in every case. An
excusing withdrawal that names no actor would let the subject's own withdrawal discharge the producer, the fault
the fifth reading found (C525), and the model fails on it.

Run: python3 formal/deletion/deletion_model.py --check
"""
import itertools, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, HORIZON = 3, 7
PRODUCER = ("producer_withdraws", "producer_supersedes", "producer_deletes")
KINDS = ("subject_revokes", "subject_withdraws") + PRODUCER + ("producer_complete",)


def fold(held, now, subject_excuses=False):
    held = [(k, t) for k, t in held if t <= now]
    starts = [t for k, t in held if k in ("subject_revokes", "subject_withdraws")]
    if not starts: return "none"
    start = min(starts); close = start + W
    excuses = PRODUCER + (("subject_withdraws",) if subject_excuses else ())
    inside = [t for k, t in held if k in excuses and t < close]
    if inside: return "met"
    return "breach" if now >= close else "running"


def data_rule():
    """The deadline as the reactions manifest carries it: (problems, does the subject's own withdrawal excuse)."""
    rx = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
    mine = [e for e in rx if e["family"] == "consent:deletion_sla:{days}"]
    bad = []
    clocks = [e for e in mine if e["kind"] == "clock"]
    closes = [e for e in mine if e["kind"] == "react" and any(x["event"] == "close" for x in e["on"])]
    if not clocks: bad.append("no clock")
    if not any("deletion_window_breach" in x.get("family", "") for e in closes for x in e["effects"]): bad.append("no breach at the close")
    starts = {(x["event"], x["of"], x.get("by")) for e in clocks for x in e["from"] if isinstance(x, dict)}
    if ("admitted", "consent:state:revoked", None) not in starts: bad.append("the clock does not start at the subject's revocation")
    if ("withdrawn", "target", "subject") not in starts: bad.append("the clock does not start at the subject's own withdrawal")
    excuse = {(x["event"], x["of"], x.get("by")) for e in closes for x in e.get("unless", [])}
    for ev in ("withdrawn", "superseded"):
        if (ev, "target", "producer") not in excuse and (ev, "target", None) not in excuse: bad.append(f"{ev} by the producer does not excuse")
    if not any(ev == "purged" and of == "target" for ev, of, _ in excuse): bad.append("hard deletion does not excuse")
    if any(ev == "admitted" and "deletion_complete" in of for ev, of, _ in excuse): bad.append("a deletion_complete row excuses")
    return bad, any(ev in ("withdrawn", "superseded") and of == "target" and by != "producer" for ev, of, by in excuse)


def check():
    fails = {p: None for p in ("D1", "D2", "D3", "D4", "D5", "D6")}
    differ, n = [], 0
    for size in (1, 2, 3):
        for combo in itertools.combinations(KINDS, size):
            for times in itertools.product(range(0, 5), repeat=size):
                held = set(zip(combo, times)); n += 1
                states = [fold(held, now) for now in range(HORIZON + 1)]
                starts = [t for k, t in held if k.startswith("subject_")]
                if starts:
                    close = min(starts) + W
                    inside = any(k in PRODUCER and t < close for k, t in held)
                    for now in range(HORIZON + 1):
                        want = "none" if now < min(starts) else "met" if inside and any(k in PRODUCER and t < close and t <= now for k, t in held) else ("breach" if now >= close and not inside else "running")
                        if states[now] != want: fails["D1"] = fails["D1"] or (sorted(held), now, states[now], want)
                    if inside and "breach" in states: fails["D4"] = fails["D4"] or (sorted(held), states)
                    if not inside and close <= HORIZON and states[HORIZON] != "breach": fails["D5"] = fails["D5"] or (sorted(held), states)
                    if "breach" in states and any(s != "breach" for s in states[states.index("breach"):]): fails["D5"] = fails["D5"] or (sorted(held), states)
                    only_subject = all(k.startswith("subject_") or k == "producer_complete" for k, _ in held)
                    if only_subject and close <= HORIZON and states[close] != "breach": fails["D3"] = fails["D3"] or (sorted(held), states)
                without = {(k, t) for k, t in held if k != "producer_complete"}
                if [fold(without, now) for now in range(HORIZON + 1)] != states: fails["D2"] = fails["D2"] or (sorted(held), states)
                for now in range(HORIZON + 1):
                    if fold({r for r in held if r[1] <= now}, now) != states[now]: fails["D6"] = fails["D6"] or (sorted(held), now)
                data = [fold(held, now, subject_excuses=SUBJECT_EXCUSES) for now in range(HORIZON + 1)]
                if data != states:
                    differ.append(sorted(held))
    return n, fails, differ


SUBJECT_EXCUSES = False


def main():
    global SUBJECT_EXCUSES
    bad, SUBJECT_EXCUSES = data_rule()
    for b in bad: print(f"  FAIL the reactions manifest: {b}")
    n, fails, differ = check()
    broken = sorted(p for p, v in fails.items() if v)
    for p in broken: print(f"  FAIL {p}: {fails[p]}")
    if differ:
        missed = sum(1 for h in differ if fold(set(h), HORIZON) == "breach")
        print(f"  FAIL the manifest's rule differs from the text's in {len(differ)} cases and misses the breach in {missed}: "
              f"an excusing event names no actor, so the subject's own withdrawal discharges the producer (C525), e.g. {differ[0]}")
    print(f"deletion: {n} cases, six properties " + ("hold" if not broken else f"fail {broken}") +
          ("; the reactions manifest carries the same rule in every case" if not differ and not bad else ""))
    return 1 if broken or differ or bad else 0

if __name__ == "__main__":
    sys.exit(main())
