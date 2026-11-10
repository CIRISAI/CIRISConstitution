#!/usr/bin/env python3
"""The fold is a function of the held set, not of the order it arrived (CC 4.5.13; formal/event_lifecycle).

Takes the rows the mesh story wrote (manifests/mesh_story_trace.json), the transitions of every
family (manifests/transitions.json) and the standings the story's actors held, and replays them
the way a mesh does: every node receives the same rows in its own order, holds each one as it
arrives, and folds its held set by the rows' signed instants. Then it checks, over seeded random
orders and random island splits:

  1. every node's fold of the whole set names the same state for every object as the story does;
  2. at every prefix, a node's fold equals the fold of the same rows sorted, so two nodes that hold
     the same rows agree whatever order they got them in;
  3. islands fold on their own, and the fold of the merged holdings equals the fold of the whole;
  4. every actor's queue over the final fold is the same on every node.

A fold that depended on arrival order, a transition reachable from two states, or a table in
which two rows of one object compete at one instant would fail here. Exit 1 on any difference.

  python3 -I tools/check_fold_order.py            # 100 orders, 100 splits, seed 0x5eed
  python3 -I tools/check_fold_order.py --orders 1000 --seed 7
"""
import json, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TR = json.loads((ROOT / "manifests" / "transitions.json").read_text())
TRACE = json.loads((ROOT / "manifests" / "mesh_story_trace.json").read_text())
FAM = {r["family"]: r for r in TR["rows"]}


def instant(row):
    """The story numbers its rows in the order they were signed; that number is the signed instant."""
    return int(row["id"][3:])


def transition(family, verb, state):
    for t in FAM[family]["transitions"]:
        if t["verb"] == verb and t["from"] == state:
            return t
    return None


def fold(held):
    """State of every object from its held rows, taken in signed-instant order; a row whose
    transition is not enabled at its instant is dead and moves nothing."""
    by_obj = {}
    for r in held:
        by_obj.setdefault(r["object"], []).append(r)
    states = {}
    for oid, rows in by_obj.items():
        rows.sort(key=lambda r: (instant(r), r["id"]))
        st = "none"
        for r in rows:
            t = transition(r["family"], r["verb"], st)
            if t:
                st = t["to"]
        states[oid] = (rows[0]["family"], st)
    return states


def enabled(family, state, roles):
    out = []
    for t in FAM[family]["transitions"]:
        if t["from"] != state or not t["roles"]["value"]:
            continue
        need = t["roles"]["value"]
        if any(r in need for r in roles) or ("registered" in need and roles):
            out.append(t["verb"])
    return out


def queues(states, standings):
    return {who: {oid: enabled(fam, st, roles) for oid, (fam, st) in sorted(states.items())}
            for who, roles in sorted(standings.items())}


def main():
    args = sys.argv[1:]
    n = int(args[args.index("--orders") + 1]) if "--orders" in args else 100
    seed = int(args[args.index("--seed") + 1], 0) if "--seed" in args else 0x5EED
    rng = random.Random(seed)

    rows = [s["row"] for s in TRACE["steps"] if s["row"]]
    standings = {}
    for s in TRACE["steps"]:
        standings.setdefault(s["actor"], set()).update(s["standing"])
    standings = {k: sorted(v) for k, v in standings.items()}
    story = {s["view"]["object"]: (s["view"]["family"], s["view"]["state_after"]) for s in TRACE["steps"]}

    whole = fold(rows)
    errs = []
    if whole != story:
        errs.append(f"the fold of the whole set differs from the story: {sorted(set(whole.items()) ^ set(story.items()))}")
    canonical_queues = queues(whole, standings)

    for i in range(n):
        order = rows[:]
        rng.shuffle(order)
        held = []
        for r in order:
            held.append(r)
            if fold(held) != fold(sorted(held, key=instant)):
                errs.append(f"order {i}: a prefix's fold depends on arrival order after {r['id']}")
                break
        if fold(held) != whole:
            errs.append(f"order {i}: the final fold differs from the whole")
        if queues(fold(held), standings) != canonical_queues:
            errs.append(f"order {i}: an actor's queue differs")
        k = rng.randint(2, 4)
        islands = [[] for _ in range(k)]
        for r in order:
            islands[rng.randrange(k)].append(r)
        merged = [r for isl in islands for r in isl]
        if fold(merged) != whole:
            errs.append(f"split {i}: the fold of {k} merged islands differs from the whole")
        for isl in islands:
            part = fold(isl)
            for oid, (fam, st) in part.items():
                if fold([r for r in rows if r["object"] == oid and r in isl]) != {oid: (fam, st)}:
                    errs.append(f"split {i}: an island's fold of {oid} is not a function of its rows")

    if errs:
        print("fold order: FAIL"); [print("  " + e) for e in errs[:20]]
        return 1
    print(f"fold order: {len(rows)} rows, {len(whole)} objects, {len(standings)} standings; "
          f"{n} arrival orders and {n} island splits fold to the story's states and queues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
