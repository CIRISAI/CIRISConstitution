#!/usr/bin/env python3
"""
CC — who holds which content key, as a small executable model (CC 4.4.3.4.1, CC 4.4.3.4.5, CC 4.4.3.2.1).

One group and one writer in it (the minter of its own keys). Members b and c come and go; b has a second device
that may be added and revoked. The writer seals each write under a key and wraps that key to devices. Two tiers:

    per-write   `self` and `family`: a fresh key for every write
    epoch       `community` and `affiliations`: one key for the writer's epoch, rotated before a write when due

What each membership act does to keys is not written here. It is read from `manifests/transitions.json`, where
the change column gives every act a key effect by scope: `rekey_walk`, `next_seal`, `stop_wrap`, `rotate_epoch`.
The model gives each of those four words its meaning and runs every sequence of acts up to the bound.

Properties:
  K1  a key is wrapped only to a live device of a current member
  K2  no write is sealed under a key held by a member who has left (removed or resigned)
  K3  after a write every live device of every current member holds its key
  K4  at the epoch tier a new member is wrapped the key of the epoch it joins, at the next write, and no other
  K5  at the per-write tier a new member, and a member's new device, holds the key of every earlier write
  K6  the epoch changes only after a departure or a rotation falling due, never on an admission
  K7  a wrap once made is never unmade
  K8  no write is sealed under a key held by a revoked device of a member who stays
  K9  a member admitted to a group with content in the current epoch holds that epoch's key without a further write

K8 fails at the epoch tier and the check requires exactly that: the data gives a device revocation a key effect
at `self` scope alone, so a continuing member's revoked device holds the epoch key until the next rotation
(conflict C558 of formal/derivation/text_conflicts.tsv). K9 fails there too: `next_seal` wraps a newcomer at the
writer's next write, so in a room where nobody writes again the newcomer never reads what the epoch already holds
(C559). Each expectation is removed when its rule is settled.

Run: python3 formal/key_plane/key_plane_model.py --check
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TIERS = {"per-write": ("self", "family"), "epoch": ("community", "affiliations")}
DEPTH = 6
DEVICES = {"b": ("b1", "b2"), "c": ("c1",)}


def key_table():
    """(act, scope) -> key effect, from the change column of the transitions manifest."""
    tr = json.load(open(os.path.join(ROOT, "manifests", "transitions.json"), encoding="utf-8"))
    tab = {}
    for r in tr["rows"]:
        if r["family"] not in ("membership:{stage}", "identity:occurrence_revocation"): continue
        for t in r["transitions"]:
            for it in (t.get("change") or {}).get("value") or []:
                m = re.fullmatch(r"([a-z]+)\[scope:([a-z|]+)\]: (?:.*, )?key=([a-z_]+)", it["item"])
                if not m: continue
                act = "revocation" if r["family"].startswith("identity:") else m.group(1)
                for s in m.group(2).split("|"): tab[(act, s)] = m.group(3)
    return tab


class Fail(Exception):
    pass


def explore(tab, scope, tier):
    eff = lambda act: tab.get((act, scope), "none")
    seen_fail = {}
    count = [0]

    def note(p, trace):
        seen_fail.setdefault(p, trace)

    def step(st, ev, trace):
        members, live, left, revoked, epoch, due, cause, holders, nwrites, fresh, stale = st
        holders = dict(holders); members = set(members); live = set(live); left = set(left); revoked = set(revoked); fresh = set(fresh); stale = set(stale)
        before = {k: set(v) for k, v in holders.items()}
        kind, who = ev

        def current():
            return {"w"} | {d for m in members for d in DEVICES[m] if d in live}

        def grant(dev, keys):
            for k in keys: holders[k] = holders.get(k, frozenset()) | {dev}

        if kind == "add":
            members.add(who); live.add(DEVICES[who][0]); left -= set(DEVICES[who]); stale -= set(DEVICES[who])
            if eff("widening") == "rekey_walk":
                for d in DEVICES[who]:
                    if d in live: grant(d, list(holders))
            elif eff("widening") == "next_seal": fresh.add(who)
            elif eff("widening") == "rotate_epoch": due = True; fresh.add(who)
            elif eff("widening") == "current_epoch_at_seat":      # proposed, not in the grammar: the wrap is made at the seat
                fresh.add(who)
                if not due and ("epoch", epoch) in holders: grant(DEVICES[who][0], [("epoch", epoch)])
        elif kind in ("remove", "resign"):
            members.discard(who); left |= {d for d in DEVICES[who] if any(d in v for v in holders.values()) or d in live}
            fresh.discard(who)
            e = eff("removal" if kind == "remove" else "resignation")
            if e == "rotate_epoch": due = True; cause = True
            elif e != "stop_wrap": stale |= {d for d in DEVICES[who] if d in live}   # no key effect: the writer goes on wrapping
        elif kind == "device_add":
            live.add(who)
            mine = [k for k, v in holders.items() if DEVICES["b"][0] in v]
            grant(who, list(holders) if tier == "per-write" else mine)   # CC 4.4.3.4.1: every key the member's other devices hold
        elif kind == "device_revoke":
            live.discard(who); revoked.add(who)
            if eff("revocation") == "rotate_epoch": due = True; cause = True
        elif kind == "tick":
            due = True; cause = True
        elif kind == "write":
            if tier == "epoch":
                if due:
                    if not cause: note("K6", trace)
                    epoch += 1; due = False; cause = False
                k = ("epoch", epoch)
            else:
                k = ("write", nwrites)
            holders.setdefault(k, frozenset())
            if holders[k] & left: note("K2", trace)
            if holders[k] & revoked: note("K8", trace)
            for d in current() | stale: grant(d, [k])
            if holders[k] & left: note("K2", trace)
            if not current() <= holders[k]: note("K3", trace)
            for m in list(fresh):
                got = {kk for kk, v in holders.items() if any(d in v for d in DEVICES[m])} - {kk for kk, v in before.items() if any(d in v for d in DEVICES[m])}
                if got - {k}: note("K4", trace)
            fresh.clear()
            nwrites += 1
        # K1, K7 on every step
        for k, v in holders.items():
            new = v - before.get(k, set())
            if new - current(): note("K1", trace)
        for k, v in before.items():
            if not v <= holders.get(k, frozenset()): note("K7", trace)
        if tier == "epoch" and kind == "add":
            if any(d in v - before.get(k, set()) for k, v in holders.items() for d in DEVICES[who] if k != ("epoch", epoch) or due): note("K4", trace)
            if not due and ("epoch", epoch) in holders and DEVICES[who][0] not in holders[("epoch", epoch)]: note("K9", trace)
        if tier == "per-write" and kind in ("add", "device_add"):
            devs = [who] if kind == "device_add" else [d for d in DEVICES[who] if d in live]
            if any(d not in v for v in holders.values() for d in devs): note("K5", trace)
        return (frozenset(members), frozenset(live), frozenset(left), frozenset(revoked), epoch, due, cause,
                tuple(sorted(holders.items())), nwrites, frozenset(fresh), frozenset(stale))

    def events(st):
        members, live, _, revoked = st[0], st[1], st[2], st[3]
        out = [("write", None)]
        if tier == "epoch": out.append(("tick", None))
        for m in ("b", "c"):
            out += [("remove", m), ("resign", m)] if m in members else [("add", m)]
        if "b" in members:
            if "b2" in live: out.append(("device_revoke", "b2"))
            elif "b2" not in revoked: out.append(("device_add", "b2"))
        return out

    def dfs(st, trace):
        count[0] += 1
        if len(trace) == DEPTH: return
        for ev in events(st):
            t2 = trace + (ev,)
            dfs(step(st, ev, t2), t2)

    dfs((frozenset(), frozenset(), frozenset(), frozenset(), 0, False, False, (), 0, frozenset(), frozenset()), ())
    return count[0], seen_fail


EXPECTED = {"per-write": set(), "epoch": {"K8", "K9"}}


def main():
    tab = key_table()
    rc = 0
    need = [(a, s) for a in ("widening", "removal", "resignation") for t in TIERS.values() for s in t]
    for a, s in need:
        if (a, s) not in tab: print(f"  FAIL the transitions manifest gives no key effect for a {a} at {s}"); rc = 1
    for tier, scopes in TIERS.items():
        for s in scopes[1:]:
            if any(tab.get((a, s)) != tab.get((a, scopes[0])) for a in ("widening", "removal", "resignation")):
                print(f"  FAIL {s} and {scopes[0]} are one tier and the manifest gives them different key effects"); rc = 1
        n, fail = explore(tab, scopes[0], tier)
        bad = set(fail)
        ok = bad == EXPECTED[tier]
        rc |= 0 if ok else 1
        print(f"  {tier:9} ({', '.join(scopes)}): {n} sequences of up to {DEPTH} acts, fails {', '.join(sorted(bad)) or 'nothing'}" +
              ("" if ok else f"  FAIL expected {sorted(EXPECTED[tier]) or 'nothing'}"))
        if "-v" in sys.argv or not ok:
            for p in sorted(bad): print(f"    {p}: {fail[p]}")
    print("key_plane: the key effects of the transitions manifest hold K1-K7 at both tiers; a revoked device of a continuing "
          "member keeps the epoch key until the next rotation (K8, C558), and a newcomer waits for the writer's next write (K9, C559)" if not rc else "key_plane: FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
