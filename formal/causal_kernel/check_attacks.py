#!/usr/bin/env python3
"""
check_attacks.py: one command, exit 0 or 1.

Runs the thirty-four attacks of attacks.py against the kernel modules in this folder, three worker processes and this
one, each capped at 2 GiB of address space, and compares each test's class with attack_expected.tsv.

Exit 0 only if
    every test's class equals the expected one, and none is BROKEN;
    every observation a test rests on came out as written, and so did the measured price of tips and the reader's line;
    every scenario gave one answer in every arrival order run.

    python3 -I formal/causal_kernel/check_attacks.py            the table
    python3 -I formal/causal_kernel/check_attacks.py --facts    every observation, witness and limit
"""
import csv
import multiprocessing
import os
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import attacks as A   # noqa: E402

PROCS = 3
EXPECTED = os.path.join(HERE, "attack_expected.tsv")


def _limit():
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))


def main():
    t0 = time.time()
    want = {int(r["test"]): r for r in csv.DictReader(open(EXPECTED, encoding="utf-8"), delimiter="\t")}
    nums = sorted(x[0] for x in A.TESTS)
    with multiprocessing.Pool(PROCS, initializer=_limit) as mp:
        res = mp.map(A.run_one, nums, chunksize=1)
        price, price_bad = mp.apply(A.checkpoint_price)
    facts = "--facts" in sys.argv
    ok = len(res) == 34 and set(want) == set(nums)
    count, orders, differ, scen = {}, 0, 0, 0
    for d in res:
        exp = want[d["n"]]["class"]
        wrong = [text for text, v in d["facts"] if not v]
        good = d["cls"] == exp and d["cls"] != "BROKEN" and not wrong and not d["order_differ"]
        ok &= good
        count[d["cls"]] = count.get(d["cls"], 0) + 1
        orders += d["count"]["orders"]; differ += d["count"]["differ"]; scen += d["count"]["scenarios"]
        print("%2d  %-16s %-16s %s  %s" % (d["n"], d["cls"], "" if d["cls"] == exp else "expected " + exp, "ok  " if good else "FAIL", d["name"]))
        for text in wrong: print("      FAIL, not as written: " + text)
        if d["order_differ"]: print("      FAIL: %d arrival orders gave another answer" % d["order_differ"])
        if facts:
            print("      property: " + d["prop"])
            for text, v in d["facts"]: print("        " + text)
            for text in d["notes"]: print("        - " + text)
            print("      who: " + d["who"]); print("      witness: " + d["witness"]); print("      " + d["protects"])
            print("      expected bound: %s; who can still do it: %s\n" % (want[d["n"]]["bound"], want[d["n"]]["who_can_still_do_it"]))
    print("tips, the reader's line, and why the group checkpoint is off, measured:")
    for text, v in price:
        ok &= bool(v)
        print("   %s%s" % ("" if v else "FAIL, not as written: ", text))
    ok &= not price_bad and differ == 0
    print("classes: " + "; ".join("%s %d" % (k, count.get(k, 0)) for k in ("HOLDS", "BROKEN", "CONCEDED", "NOT EXPRESSIBLE")))
    print("order-freeness: %d scenarios, %d arrival orders (every order of up to seven rows, a fixed sample of 1,000 above, each set once more with every row offered twice), %d gave another answer"
          % (scen, orders, differ + price_bad))
    print("RESULT: %s in %.0fs" % ("ok" if ok else "FAILED", time.time() - t0))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
