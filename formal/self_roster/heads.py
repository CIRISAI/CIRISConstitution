#!/usr/bin/env python3
"""
CC 3.3.6.4 — the head a self-roster row names, checked.

Every `identity:occurrence` (a bind) and `identity:occurrence_revocation` (an eviction) names in `refs.head` the last
landed self-roster row its signer stood on, and a merge names the other tips in `refs.further_heads`. The first
bind of a new identity names the genesis key's own record. This file reads those rows as the kernel does
(CC 2.7.8), with no clock and no arrival order:

  the roster at a set of heads is the genesis key, plus every landed bind, less every landed eviction, reachable
  from any named head (the union fold);
  a row lands when every head it names is held and has landed, its signers meet a strict majority of the roster at
  its heads, a bind carries the bound key's own statement, and the row is no sibling for the reader;
  a row waits while a head it names is not held;
  a row is a sibling, void for a reader, when the reader has acknowledged a row the row's heads do not reach: a
  merge must name every tip the reader has acknowledged;
  a reader's roster is the roster of its one tip, or the members common to all its tips.

The two-path window of CC 3.3.6.4 is not modelled here: the count path alone, which is what the head changes.

Facts checked, each with a plant that must fail it:
  stolen    a stolen genesis key's bind naming the genesis head is void for a reader that acknowledged d1's bind,
            and so is the merge that would evict d1 through it; a reader that acknowledged nothing reads it as one
            tip among several, never as the roster.          plant: a reader that ignores its acknowledgement
            The residual of CC 2.7.9 is printed beside it: a reader with no acknowledgement that holds the thief's own
            merge reads the thief's tip.
  revive    a merge never revives an evicted key: the eviction reached from any named head stands.
                                                              plant: the roster at heads as the union of each head's roster
  wait      a row naming a head not yet held waits, so the landed set is the same in every arrival order.
                                                              plant: a node that refuses a row whose head it lacks
  over all  every subset of the pool, every reader: no landed row is a sibling of an acknowledged row, no landed
            row's roster lists a key a reachable landed eviction removed, and the reader's roster is a function of
            the set.

Run: python3 -I formal/self_roster/heads.py --check
"""
import itertools
import sys

GEN = "G"                      # the genesis key's own record; the genesis key is g
MUT = set()


def row(rid, kind, key, head, signers, further=()):
    return {"id": rid, "kind": kind, "key": key, "head": head, "further": frozenset(further), "signers": frozenset(signers)}


class Reader:
    def __init__(self, rows, ack=()):
        self.rows = {r["id"]: r for r in rows}
        self.ack = frozenset(ack)
        self.memo = {}

    def heads(self, r):
        return {r["head"]} | set(r["further"])

    def past(self, rid):
        """rid and every row it names, transitively (the genesis record included)."""
        out, todo = set(), [rid]
        while todo:
            x = todo.pop()
            if x in out: continue
            out.add(x)
            if x != GEN and x in self.rows: todo += list(self.heads(self.rows[x]))
        return out

    def reach(self, heads):
        out = set()
        for h in heads: out |= self.past(h)
        return out

    def landed(self, rid):
        if rid == GEN: return True
        if rid in self.memo: return self.memo[rid]
        self.memo[rid] = False
        r = self.rows.get(rid)
        if r is None: return False
        hs = self.heads(r)
        if any(h != GEN and h not in self.rows for h in hs): return False               # waits
        if not all(self.landed(h) for h in hs): return False
        if "ignore_ack" not in MUT and any(rid not in self.past(a) and a not in self.reach(hs) for a in self.ack):
            return False                                                                # a sibling, void here
        roster = self.roster_at(hs)
        voters = r["signers"] & roster
        if not r["signers"] <= roster | {r["key"]} or 2 * len(voters) <= len(roster): return False
        if r["kind"] == "bind" and r["key"] not in r["signers"]: return False           # the bound key's own statement
        self.memo[rid] = True
        return True

    def roster_at(self, heads):
        if "union_of_rosters" in MUT and len(heads) > 1:
            out = set()
            for h in heads: out |= self.roster_at({h}) if h == GEN else self._fold(self.past(h))
            return out
        return self._fold(self.reach(heads))

    def _fold(self, ids):
        binds = {self.rows[i]["key"] for i in ids if i != GEN and self.rows[i]["kind"] == "bind" and self.landed(i)}
        evicts = {self.rows[i]["key"] for i in ids if i != GEN and self.rows[i]["kind"] == "evict" and self.landed(i)}
        return ({"g"} | binds) - evicts

    def tips(self):
        live = [i for i in self.rows if self.landed(i)] + [GEN]
        named = set()
        for i in live:
            if i != GEN: named |= self.past(i) - {i}
        return sorted(i for i in live if i not in named)

    def roster(self):
        ts = self.tips()
        out = None
        for t in ts:
            r = self.roster_at({t})
            out = r if out is None else out & r
        return out


def landed_in_arrival(rows, ack, refuse_missing):
    """One node judging rows as they arrive. Waiting: a row whose head is missing is kept and judged again; the
    plant refuses it for good."""
    held, refused = [], set()
    for r in rows:
        if refuse_missing and any(h != GEN and h not in {x["id"] for x in held} for h in {r["head"]} | r["further"]):
            refused.add(r["id"]); continue
        held.append(r)
    rd = Reader(held, ack)
    return frozenset(i for i in rd.rows if rd.landed(i))


# ---------------------------------------------------------------- the worlds
B1 = row("B1", "bind", "d1", GEN, {"g", "d1"})                     # the owner binds d1 on the genesis head
T = row("T", "bind", "x", GEN, {"g", "x"})                         # the thief, holding g, binds x on the genesis head
TM = row("TM", "evict", "d1", "T", {"g", "x"}, further={"B1"})     # and merges, to evict d1 by g and x
B2 = row("B2", "bind", "d2", "B1", {"g", "d1", "d2"})
E2 = row("E2", "evict", "d2", "B2", {"g", "d1"})                   # d2 evicted
S3 = row("S3", "bind", "d3", "B2", {"g", "d1", "d3"})              # a sibling tip that still lists d2
M = row("M", "bind", "d4", "E2", {"g", "d1", "d3", "d4"}, further={"S3"})   # a merge of both tips
POOL = [B1, T, TM, B2, E2, S3, M]


def facts():
    out = []

    def stolen():
        rows = [B1, T, TM]
        acked = Reader(rows, ack={"B1"})
        fresh = Reader([B1, T])
        return (not acked.landed("T") and not acked.landed("TM") and acked.roster() == {"g", "d1"},
                fresh.landed("T") and len(fresh.tips()) > 1 and "x" not in fresh.roster())

    a, b = stolen()
    MUT.add("ignore_ack"); pa, _ = stolen(); MUT.discard("ignore_ack")
    out.append(("stolen: a stolen genesis key's bind on the genesis head, and its merge evicting d1, are void for a reader "
                "that acknowledged d1's bind; the roster stays g and d1", a, "a reader that ignores its acknowledgement", not pa))
    out.append(("stolen: a reader that acknowledged nothing holds the thief's bind as one tip among several, never as the roster",
                b, None, True))

    fresh = Reader([B1, T, TM])
    out.append(("stolen, the stated residual (CC 2.7.9): a reader that acknowledged nothing and holds the thief's merge reads "
                "the thief's tip, as whoever controls a new reader's first view can make a wrong head stick", fresh.landed("TM") and "x" in fresh.roster(),
                None, True))

    def revive():
        rd = Reader([B1, B2, E2, S3, M])
        return rd.landed("M") and "d2" not in rd.roster_at({"E2", "S3"}) and "d2" not in rd.roster()

    ok = revive()
    MUT.add("union_of_rosters"); pl = revive(); MUT.discard("union_of_rosters")
    out.append(("revive: a merge of a tip that evicted d2 and a tip that still lists it does not list d2",
                ok, "the roster at heads as the union of each head's roster (the merge revives d2)", not pl))

    def wait(refuse):
        rows = [B1, B2, E2, S3, M]
        seen = {landed_in_arrival(list(p), (), refuse) for p in itertools.permutations(rows)}
        return len(seen) == 1

    out.append(("wait: a row naming a head not yet held waits; the landed set is the same in all 120 arrival orders",
                wait(False), "a node that refuses a row whose head it lacks", not wait(True)))

    def over_all():
        bad, n = [], 0
        ids = [r["id"] for r in POOL]
        for k in range(len(POOL) + 1):
            for sub in itertools.combinations(POOL, k):
                for ack in [()] + [(r["id"],) for r in sub]:
                    rd = Reader(sub, ack)
                    if ack and not rd.landed(ack[0]): continue          # a reader acknowledges only what landed for it
                    n += 1
                    for r in sub:
                        if not rd.landed(r["id"]): continue
                        if any(r["id"] not in rd.past(a) and a not in rd.reach(rd.heads(r)) for a in ack):
                            bad.append(("sibling lands", [x["id"] for x in sub], ack, r["id"]))
                        hs = rd.heads(r)
                        gone = {rd.rows[i]["key"] for i in rd.reach(hs) if i != GEN and rd.rows[i]["kind"] == "evict" and rd.landed(i)}
                        if gone & rd.roster_at(hs):
                            bad.append(("evicted key listed", [x["id"] for x in sub], ack, r["id"]))
                    for p in itertools.islice(itertools.permutations(sub), 6):
                        if Reader(list(p), ack).roster() != rd.roster():
                            bad.append(("not a function of the set", [x["id"] for x in sub], ack, None)); break
        return n, bad

    n, bad = over_all()
    MUT.add("ignore_ack"); _, bad_a = over_all(); MUT.discard("ignore_ack")
    MUT.add("union_of_rosters"); _, bad_u = over_all(); MUT.discard("union_of_rosters")
    out.append((f"over all: {n} (subset, reader) pairs of the pool of {len(POOL)} rows; no sibling of an acknowledged row lands, "
                "no evicted key is listed, the roster is a function of the set", not bad,
                "ignore the acknowledgement / the union of rosters", any(b[0] == "sibling lands" for b in bad_a)
                and any(b[0] == "evicted key listed" for b in bad_u)))
    return out


def main():
    fail = 0
    for fact, ok, plant, caught in facts():
        line = f"  {'holds ' if ok else 'FAILS '} {fact}"
        if plant: line += f"\n         plant: {plant}: {'caught' if caught else 'NOT CAUGHT'}"
        print(line)
        fail += (not ok) + (not caught)
    print(f"self-roster heads: {'every fact holds and every plant is caught' if not fail else f'{fail} FAIL'}")
    return 1 if (fail and "--check" in sys.argv) else 0


if __name__ == "__main__":
    sys.exit(main())
