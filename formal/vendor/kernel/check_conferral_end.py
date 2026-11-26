#!/usr/bin/env python3
"""
check_conferral_end.py: the end of a conferral (models/tla/CONFERRAL_END.md), checked three ways.

    case table   every case of conferral_end.CASES: the reference gives the hand-written counted, in_force and
                 rule for every act, in every arrival order the door allows (up to 200 per case)
    fixture      crates/ciris-kernel/tests/fixtures/conferral_end.json, the fixture persist runs: the reference,
                 run on each case's rows, gives every answer the fixture states, and each listed arrival order,
                 folded row by row, ends at it
    the spec     tools/conferral_xcheck.py compares the reference with ConferralEnd.tla state by state; it needs
                 TLC, so tools/tla_check.sh runs it, not this file

    python3 -I check_conferral_end.py      exit 1 on any difference
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import conferral_end as CE  # noqa: E402

FIXTURE = os.path.join(ROOT, "crates", "ciris-kernel", "tests", "fixtures", "conferral_end.json")


def main():
    n, problems = CE.check_cases()
    fx = json.load(open(FIXTURE, encoding="utf-8"))
    answers = 0
    for c in fx["cases"]:
        params = {"reader_acks": c["reader_acks"], "other_standing": c["other_standing"], "who": c["who"],
                  "deputy_depth": c["deputy_depth"]}
        got = CE.answers(c["rows"], **params)
        if got != c["answers"]:
            problems.append("fixture %s: the reference gives %s, the fixture %s" % (c["name"], got, c["answers"]))
        answers += len(c["answers"])
        by = {r["id"]: r for r in c["rows"]}
        for order in c["orders"]:
            held = []
            for i in order:
                held.append(by[i])
                if not all(x in {h["id"] for h in held} or x not in by for x in by[i]["names"]):
                    problems.append("fixture %s: order %s takes %s before what it names" % (c["name"], order, i))
            if CE.answers(held, **params) != c["answers"]:
                problems.append("fixture %s: order %s ends elsewhere" % (c["name"], order))
    names = {c["name"] for c in fx["cases"]}
    if names != {c[0] for c in CE.CASES}:
        problems.append("fixture cases %s, table cases %s" % (sorted(names), sorted(c[0] for c in CE.CASES)))
    for p in problems:
        print(p)
    rules = sorted({a["rule"] for c in fx["cases"] for a in c["answers"].values()})
    print("RESULT: %s: %d cases, %d act answers, %d rules decide them (%s)"
          % ("ok" if not problems else "%d problems" % len(problems), n, answers, len(rules), ", ".join(rules)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
