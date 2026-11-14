#!/usr/bin/env python3
"""
check_roomkey.py: one command, exit 0 or 1.

    python3 -I check_roomkey.py

Three worker processes and this one, each capped at 2 GiB of address space. Every enumeration is bounded and the bound
is printed. The kernel modules beside this file are read and not changed; roomkey.py is the addition. The verdicts on
the binding are symbolic, and nothing here is proved in Lean.

  1  the kernel does not care which key   every named answer for a room over voices equals the answer for the same room
                                          over identity keys, under a renaming that also reverses the order of the names
  2  one person, one voice                the tally over voices against a count of persons, for every way devices can vote
  3  the binding                          AUTHENTIC-INSIDE and DENIABLE-OUTSIDE for five mechanisms, against what is expected
  4  the interactions                     removal, re-admission, devices, the later joiner, carriage, detection, the report
  5  what else ties a person to the room  each kind of row, if it also carried an identity signature
  6  a count of persons waits             missing exactly the bindings not held; the commitment turns a fork into a wait
  7  the two seatings                     what a holder of rows can prove about persons under identity keys and under room keys
  8  the room declares itself             private or public, absent reads public, never public to private
  9  the commitment, the planned binding, the verdict, and the limits a run can show
 10  detection in a private room          the detector's seat is conferred inside the room, the owner-binding is a row of it
"""
import multiprocessing
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import roomkey as RK   # noqa: E402

PROCS = 3
UPTO = 17
MEMBERS = ("A", "B", "C", "J")


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


def job(x):
    kind = x[0]
    if kind == "indiff": return x, RK.indifference(UPTO, (x[1], PROCS))
    if kind == "votes": return x, RK.device_votes(2)
    if kind == "devices": return x, RK.device_cases()
    if kind == "mech": return x, (RK.authentic_inside(x[1], MEMBERS), RK.honest_convinced(x[1], MEMBERS), RK.deniable_outside(x[1]))
    if kind == "inter": return x, RK.interactions(x[1])
    if kind == "overlay": return x, RK.overlays()
    if kind == "second": return x, [RK.second_voice(n) for n in (3, 4, 5, 6, 7)]
    if kind == "keyplane": return x, RK.keyplane_indifference(4)
    if kind == "mut": return x, RK.indifference_mutation()
    if kind == "waits": return x, (RK.waits_on_bindings(), RK.colluding_binders())
    if kind == "variants": return x, RK.variants()
    if kind == "declare": return x, RK.declaration()
    if kind == "commit": return x, RK.commitment_and_limits()
    if kind == "detect": return x, RK.detection_in_room()


def main():
    t0 = time.time()
    jobs = [("indiff", i) for i in range(PROCS)] + [("votes",), ("devices",), ("overlay",), ("second",), ("keyplane",), ("mut",), ("waits",), ("variants",), ("declare",), ("commit",), ("detect",)] \
        + [("mech", m) for m in RK.MECHANISMS] + [("inter", m) for m in RK.PAIRWISE]
    with multiprocessing.Pool(PROCS, initializer=_limit) as mp:
        res = dict(mp.map(job, jobs, chunksize=1))
    ok = True
    def line(good, text):
        nonlocal ok
        ok &= bool(good)
        print("   %s %s" % ("ok  " if good else "FAIL", text))

    print("1  the kernel does not care which key")
    ind = [res[("indiff", i)] for i in range(PROCS)]
    sets, cmp_, diff = (sum(d[k] for d in ind) for k in ("sets", "compared", "differ"))
    line(diff == 0, "%d sets of rows of one room of 34 rows (the room, the room less each row, every closed subset of up to %d rows), "
         "%d answers compared in two arrival orders, %d differ" % (sets, UPTO, cmp_, diff))
    for d in ind:
        if d["first"]: print("        first difference:", d["first"])
    line(res[("mut",)], "a reader that breaks a tie by the order of key names is caught by the same comparison")
    kp = res[("keyplane",)]
    line(kp["differ"] == 0 and kp["sequences"] > 1000, "who is entitled to a wrap (the key plane as seat rows): %d sequences of membership acts, %d differ" % (kp["sequences"], kp["differ"]))

    print("2  one person, one voice")
    v = res[("votes",)]
    line(v["differ"] == 0, "%d ways for the devices of three persons to vote: the tally over voices equals the count of persons in every one (%d differ)"
         % (v["vote assignments"], v["differ"]))
    line(v["a count of keys would differ"] > 0, "a count of device keys would be wrong in %d of them" % v["a count of keys would differ"])
    print("      a second voice for a person already seated (members who give their voice without checking the binding, the person among them):")
    for table in res[("second",)]:
        n = table[0][0]
        need = min(c for _, c, seated, _ in table if seated)
        line(all(seated == met for _, _, seated, met in table) and need >= 2,
             "%d members: seated only when %d of them do not check (the room's own admission count); never by the person alone" % (n, need))

    print("3  the binding")
    for m in RK.MECHANISMS:
        (forged, cases, who), (hc, hn), den = res[("mech", m)]
        auth = forged == 0
        deni = den["prove something"] == 0 and den["not simulable"] == 0
        want = RK.EXPECT[m]
        line((auth, deni) == want and hc == hn,
             "%-12s AUTHENTIC-INSIDE %s (%d of %d coalitions forge%s); DENIABLE-OUTSIDE %s (%d of %d coalitions prove something, %d cannot be simulated); as expected: %s"
             % (m, "holds" if auth else "does not hold", forged, cases, ": " + ", ".join(who) if who else "", "holds" if deni else "does not hold",
                den["prove something"], den["coalitions"], den["not simulable"], (auth, deni) == want))
        print("                    %s" % RK.MECHANISMS[m])

    print("4  the interactions")
    n_facts = 0
    for text, good in res[("devices",)]:
        n_facts += 1; line(good, text)
    for m in RK.PAIRWISE:
        print("      with %s:" % m)
        for text, good in res[("inter", m)]:
            n_facts += 1; line(good, text)

    print("5  what an identity signature on each kind of row would give an outsider (binding: two_encap)")
    for label, proved, unsim, n, ex in res[("overlay",)]:
        line(proved > 0 and unsim > 0, "%s: %d of %d coalitions can prove something about another person; e.g. %s" % (label, proved, n, ex[1][:2] if ex else None))

    print("6  persons counted through bindings the count waits on (one room key for each device)")
    w, col = res[("waits",)]
    line(w["disagree"] == 0 and w["missing not as stated"] == 0 and w["a node with no binding counted"] == 0,
         "%d pairs of member nodes over 81 ways to vote: a count is 'missing' exactly the bindings not held; %d pairs hold every binding and %d of them disagree; "
         "a node holding no binding never counts (%d)" % (w["pairs of nodes"], w["both hold every binding"], w["disagree"], w["a node with no binding counted"]))
    line(col["the two honest nodes count differently"] > 0,
         "FINDING, without the commitment: two members who share a room key and bind it to each of them for different nodes make two honest nodes, each holding every binding, "
         "count differently in %d of %d ways to vote; e.g. %s" % (col["the two honest nodes count differently"], col["vote assignments"], col["first"]))
    line(col["with the commitment, count differently"] == 0 and col["with the commitment, the node told otherwise waits"] == col["vote assignments"]
         and col["the waiting node names the key"],
         "with a commitment to the person in the key's seat row that every binding must open: %d count differently; the node that was told otherwise waits (%d of %d), "
         "a stall at that node and never a fork, and it names the key"
         % (col["with the commitment, count differently"], col["with the commitment, the node told otherwise waits"], col["vote assignments"]))

    print("7  the two seatings: what a holder of rows can prove about persons with no secret")
    vfacts, vtable = res[("variants",)]
    for v, room, holder, nrows, a, b in vtable:
        print("        %-18s %-12s %s: %s" % (v, room, holder, "%s" % a if b is None else "%d rows; proved to have acted in the room %s; named by another's row %s" % (nrows, a, b)))
    for text, good in vfacts:
        n_facts += 1; line(good, text)

    print("8  the room declares itself")
    for text, good in res[("declare",)]:
        n_facts += 1; line(good, text)

    print("9  the commitment, the planned binding (two encapsulations), the verdict, and the limits a run can show")
    for text, good in res[("commit",)]:
        n_facts += 1; line(good, text)

    print("10 detection in a private room: the seat comes from the room")
    for text, good in res[("detect",)]:
        n_facts += 1; line(good, text)

    print("what the rule does not give (run: shown above; stated: from outside this model):")
    for how, t in RK.LIMITS: print("   - %-6s %s" % (how, t))
    print("RESULT: %s in %.0fs (%d facts)" % ("ok" if ok else "FAILED", time.time() - t0, n_facts))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
