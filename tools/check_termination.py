#!/usr/bin/env python3
"""
CC — nothing a node concludes can run on without end.

A kernel folds the rows a node holds and may sign rows of its own, which it then holds and folds. That loop ends
only if no row a node signs can, by any chain of reactions, cause the node to sign that same kind of row again.
This check reads manifests/reactions.json and holds three things:

  1. acyclic     the graph "a row of this leaf causes a row of that leaf to be signed" has no cycle, at the grain
                 of the leaf where a reaction names one and of the family where it does not;
  2. bounded     the longest chain of such causes is no longer than CHAIN_MAX, the number of rounds a kernel may
                 need for one batch;
  3. timed       a reaction that waits (an `unless`, or a clock) belongs to a family with a clock or an expiry, so
                 no wait is without a deadline.

The companion for admissions is the well-foundedness check of tools/guard_grammar.py: no row's admission requires
a row whose own admission requires it back.

Run: python3 tools/check_termination.py
"""
import json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN_MAX = 3


def nodes_of(family, leaves):
    return [f"{family}[{l}]" for l in leaves] if leaves else [family]


def emitted_node(name, fams):
    """An emitted `family:leaf` as a node: the model family it belongs to, with its last segment as the leaf."""
    if name in fams: return name
    head, _, leaf = name.rpartition(":")
    cands = [f for f in fams if f.split(":")[0] == name.split(":")[0]]
    for f in cands:
        segs = f.split(":")
        if len(segs) == len(name.split(":")) and all(a == b or a.startswith("{") for a, b in zip(segs, name.split(":"))):
            return f"{f}[{leaf}]" if segs[-1].startswith("{") else f
    return name


def main():
    rx = json.load(open(os.path.join(ROOT, "manifests", "reactions.json"), encoding="utf-8"))["reactions"]
    tr = json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))
    fams = {r["family"] for r in tr["rows"]}
    edges, waits, timed = defaultdict(set), [], set()
    clocks = {(e["family"], e["name"]): e for e in rx if e["kind"] == "clock"}

    def cause(e, o):
        """The rows whose holding makes this event happen. A sealed write is the node's own act on content, not a row here."""
        if o["event"] == "sealed": return set()
        if o["event"] == "close":
            c = clocks.get((e["family"], o["of"]))
            origin = c.get("from") if c else None
            if isinstance(origin, list):      # the clock runs from other rows: they are the cause
                return set().union(*[cause(e, x) for x in origin])
            return set(nodes_of(e["family"], e.get("leaves")))   # from the row's own instant, or an expiry
        if o["event"] == "fold" or o["of"] in ("self", "target"): return set(nodes_of(e["family"], e.get("leaves")))
        return {emitted_node(o["of"], fams)}
    for e in rx:
        if e["kind"] in ("clock", "expiry"): timed.add(e["family"]); continue
        if e["kind"] == "land": continue      # who concludes a window: the row it names is already an effect of a clause, or nothing is signed
        srcs = set()
        for o in e["on"]:
            srcs |= cause(e, o)
        if e.get("unless") or any(o["event"] == "close" for o in e["on"]): waits.append(e["family"])
        for x in e["effects"]:
            if x["effect"] == "emit":
                for s in srcs: edges[s].add(emitted_node(x["family"], fams))
    # a family node stands for every leaf of it: an edge into F reaches F[leaf] sources too
    def succ(u):
        out = set(edges.get(u, ()))
        fam = u.split("[")[0]
        if "[" in u: out |= edges.get(fam, set())
        return out
    fails, depth = [], {}
    def walk(u, path):
        if u in path: fails.append("a cycle: " + " -> ".join(path[path.index(u):] + [u])); return 0
        if u in depth: return depth[u]
        d = 1 + max([walk(v, path + [u]) for v in succ(u)] or [0]); depth[u] = d; return d
    longest = max([walk(u, []) for u in list(edges)] or [0])
    if longest > CHAIN_MAX + 1: fails.append(f"a chain of {longest - 1} causes is longer than {CHAIN_MAX}")
    for f in sorted(set(waits)):
        if f not in timed: fails.append(f"{f} has a reaction that waits and no clock or expiry")
    for x in sorted(set(fails)): print("  FAIL " + x)
    print(f"termination: {sum(len(v) for v in edges.values())} causes among {len(set(edges) | {v for s in edges.values() for v in s})} leaves, "
          f"longest chain {max(longest - 1, 0)}, {len(set(waits))} families wait and each has a deadline" if not fails else f"termination: {len(set(fails))} faults")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
