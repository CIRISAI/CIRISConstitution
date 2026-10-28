#!/usr/bin/env python3
"""The authority state tree: licensure, grant, delegation, enumerated to closure.

Vendored into CIRISConstitution/formal from CIRISRegistry
`formal/authority_tree/authority_tree.py` at 1553d68 (FSD-005 §5), because the Registry folds
into CIRISServer and the Constitution carries its own witnesses. One invariant is added here,
I10 (the term, CC 4.4.3.2.8), with its dye test. Everything else is the Registry's text.

CC 2.4.1.2.1 says a key comes to hold something in exactly three ways, and
that only one of them composes:

    licensure   an authority confers standing       does not chain
    grant       an owner confers access to an asset  does not chain
    delegation  a principal confers agency           chains: attenuated, depth-capped,
                                                     revocable per link

This module models the three as one state machine and enumerates EVERY reachable
state of a small universe, checking at each one the properties the Constitution
makes normative:

  I1  attenuation      every live delegation's effective scope is a subset of the
                       scope of the link above it (CC 4.5: child.scope ⊆ parent.scope)
  I2  depth cap        no key holds delegated authority through more than
                       DEPTH_CAP links (CC 4.1.1)
  I3  cascade          withdrawing a link removes every authority that was derived
                       through it, and nothing else (CC 4.5)
  I4  licence closure  holding a licence under authority A never, in any state,
                       lets the holder issue `licensure:A` (a licence does not chain)
  I5  grant closure    holding a grant over asset R never lets the holder issue a
                       grant over R (receipt is not issuance; CC 2.4.1.2.1)
  I6  enforced admission
                       every admitted licence resolves to its authority, and every
                       admitted grant to its asset's owner, through live delegation
                       links only (CC 4.4.3.4.3 enforced-admission rule)
  I7  sub-delegation   a key issues an onward delegation only under a link that
                       carries `sub_delegation`, and the onward link carries
                       `sub_delegation` only if its parent does
  I8  no cycle         the live delegation graph is acyclic (CC 4.1.1)
  I9  determinism      the authority a key holds is a function of the live rows,
                       not of the order they arrived in (the same set of rows
                       reached by different histories yields the same verdicts)
  I10 term             every live scope-bearing link carries a term of at most
                       MAX_TERM; a perpetual link (term 0) or one past the ceiling
                       is refused at the door (CC 4.4.3.2.8: 365 days is
                       constitutional, the term a charter parameter). Expiry is a
                       withdrawal, so its cascade is I3. Dye: `--no-term-rule`
                       admits a perpetual link and I10 MUST then fire.

"Closes" means: the reachable state space is finite, every state is examined,
every invariant holds in every state, and the resolver terminates in every
state (I2 and I8 together bound every walk).

What a leaf IS in this model, and why. The first cut stored a licence as a
(authority, subject, issuer) row and a grant as (asset, recipient, issuer), rows
that never leave; the general universe then multiplied the link state by a
powerset of issuer-tagged rows and exhausted 8 GB at two links (measured by the
Constitution session on 968a063; at one link it was 300,304 states, almost all
leaf combinations). For I4-I6 the only fact that matters afterwards is WHICH
KEY holds a licence under A, or a grant over R: four bits each in a four-key
universe. The issuer matters only at the door, where it is checked and counted.
So a leaf is a bit, and the door's verdicts are counted as they happen.

Two universes are run. The GENERAL one has four keys and every action
interleaved, so the cascade and ordering properties are checked over every
history. The DEPTH one is a chain of DEPTH_CAP + 2 keys with delegation only, so
closure at the cap is checked at depth 6, which the general universe is too
small to reach.

Run:  python3 formal/authority_tree/authority_tree.py        # CI runs this
      python3 formal/authority_tree/authority_tree.py --no-term-rule   # must exit 2 with I10
Exit 0 iff every invariant holds in every reachable state of every universe.

Measured on 2026-10-08 (the shape above, `ulimit -v 2500000`, 27 s):
  general          4 keys, links <= 2, every action interleaved:
                   153,856 states; 1,057,792 issuances admitted at the door;
                   4,621,056 refusals; 295,680 withdrawals checked for cascade;
                   16 distinct (issuer, holder) pairs per leaf kind; 0 violations.
  delegation-only  4 keys, links <= 3: 2,218 states, depth 3, 0 violations.
  depth-chain      8 keys, every sub_delegation-bearing scope set at every
                   link: 4096/2304/1024/400/144 links admitted at depths 1-5,
                   4,096 refused past the cap, 0 conferred past it.
Three links with leaves interleaved exceeds the 2.5 GB cap and is not claimed.
"""

from __future__ import annotations

import itertools
import sys
from collections import deque
from dataclasses import dataclass
from typing import FrozenSet, Iterable, Optional, Tuple

DEPTH_CAP = 5  # CC 4.1.1
MAX_TERM = 2   # the 365-day ceiling (CC 4.4.3.2.8), in model ticks; the term is a charter parameter
TERM_RULE = "--no-term-rule" not in sys.argv   # the door's term check; off only for the dye test
# Terms offered at the door: 0 is perpetual (refused under the rule), 3 is past the ceiling (refused).
TERMS_OFFERED = (0, 1, 2, 3)

# The three scopes this model needs. `license` and `grant` are the two emission
# scopes CC 4.4.3.4.3 added; `sub_delegation` is the one that lets a chain grow.
LICENSE, GRANT, SUB = "license", "grant", "sub_delegation"
SCOPES = (LICENSE, GRANT, SUB)
# Every non-empty scope set a delegation may carry.
SCOPE_SETS: Tuple[FrozenSet[str], ...] = tuple(
    frozenset(c)
    for n in range(1, len(SCOPES) + 1)
    for c in itertools.combinations(SCOPES, n)
)


@dataclass(frozen=True, order=True)
class Link:
    """A live `delegates_to(src → dst, scope)` row."""

    src: str
    dst: str
    scope: FrozenSet[str]
    term: int = 1   # 0 = perpetual; otherwise ticks remaining, 1..=MAX_TERM


@dataclass(frozen=True)
class State:
    """Live links, plus WHO holds a licence under the one authority and WHO
    holds a grant over the one asset. Leaves carry no issuer: that is judged
    and counted at the door (`issue_licence` / `issue_grant`)."""

    links: FrozenSet[Link]
    licensees: FrozenSet[str]
    grantees: FrozenSet[str]

    def key(self) -> Tuple:
        return (self.links, self.licensees, self.grantees)


# ───────────────────────────── the resolver ─────────────────────────────
#
# `paths(state, root, key)` is the one walk. It returns every chain of live links
# from `root` to `key`, each as (depth, effective_scope), where the effective
# scope is the intersection along the chain. It is the model's version of
# persist's delegation resolver (CC 4.4.3.4.3.1): a licence or a grant is never
# an edge in it, which is how I4 and I5 are true by construction and then
# CHECKED anyway, because a resolver that walked them would be the mistake
# CC 2.4.1.2.1 names.


def chains(state: State, root: str, key: str) -> Iterable[Tuple[Tuple[Link, ...], FrozenSet[str]]]:
    """Every chain of one or more live links from `root` to `key`, with the
    effective scope (the intersection along it). `root == key` yields nothing:
    a key's authority over itself is not a delegation."""
    stack = [(root, (), frozenset(SCOPES), frozenset([root]))]
    while stack:
        node, chain, scope, seen = stack.pop()
        if len(chain) >= DEPTH_CAP:
            continue
        for link in state.links:
            if link.src != node or link.dst in seen:
                continue
            eff = scope & link.scope
            if not eff:
                continue
            if link.dst == key:
                yield (chain + (link,), eff)
            # A chain continues past a key only under a link that carries
            # sub_delegation (CC 4.4.3.4.3). Deeper links without it are dead.
            if SUB in eff:
                stack.append((link.dst, chain + (link,), eff, seen | {link.dst}))


def paths(state: State, root: str, key: str) -> Iterable[Tuple[int, FrozenSet[str]]]:
    if root == key:
        yield (0, frozenset(SCOPES))
        return
    for chain, eff in chains(state, root, key):
        yield (len(chain), eff)


def holds(state: State, root: str, key: str, scope: str) -> bool:
    """Does `key` hold `scope` from `root`, through live links only?"""
    return any(scope in eff for _, eff in paths(state, root, key))


# ───────────────────────────── the actions ──────────────────────────────
#
# Every action is "admit or refuse": it returns the new state, or None when
# admission refuses it. Refusal is a result, not an error, because CC
# 4.4.3.4.3's enforced-admission rule is a door and the door's refusals are the
# properties under test.


def delegate(state: State, root: str, src: str, dst: str, scope: FrozenSet[str], term: int = 1) -> Optional[State]:
    if src == dst:
        return None
    # I10 at the door: a scope-bearing link carries a term within the ceiling; a
    # perpetual link or one past the ceiling is refused (CC 4.4.3.2.8).
    if TERM_RULE and (term < 1 or term > MAX_TERM):
        return None
    if Link(src, dst, scope, term) in state.links:
        return None
    # I8: no cycle. A link whose destination already reaches its source would
    # close one.
    if any(True for _ in chains(state, dst, src)):
        return None
    # I7 + I1 at the door: the issuer holds every scope it hands on, and holds
    # sub_delegation, from the root, within the cap.
    if src != root and not any(
        SUB in eff and scope <= eff and d < DEPTH_CAP for d, eff in paths(state, root, src)
    ):
        return None
    return State(state.links | {Link(src, dst, scope, term)}, state.licensees, state.grantees)


def withdraw(state: State, link: Link) -> State:
    """A `withdraws` on one link. The row is removed; nothing else is touched,
    and I3 checks that every authority derived through it is gone AND that no
    authority not derived through it changed."""
    return State(state.links - {link}, state.licensees, state.grantees)


def issue_licence(state: State, authority: str, issuer: str, subject: str) -> Optional[State]:
    # CC 4.4.3.4.3 enforced admission: the issuer IS the authority, or holds a
    # `license`-scoped delegation whose chain resolves to it.
    if not (issuer == authority or holds(state, authority, issuer, LICENSE)):
        return None
    if subject in state.licensees:
        return None
    return State(state.links, state.licensees | {subject}, state.grantees)


def issue_grant(state: State, owner: str, asset: str, issuer: str, recipient: str) -> Optional[State]:
    # CC 2.4.1.2.1: the owner, or a `grant`-scoped delegate of the owner. A
    # recipient re-granting on possession is refused.
    if not (issuer == owner or holds(state, owner, issuer, GRANT)):
        return None
    if recipient in state.grantees:
        return None
    return State(state.links, state.licensees, state.grantees | {recipient})


# ───────────────────────────── the invariants ───────────────────────────


class Violation(Exception):
    pass


def check(state: State, root: str, keys: Tuple[str, ...], asset: str) -> None:
    # I10: no live scope-bearing link is perpetual or past the ceiling.
    for link in state.links:
        if link.scope and (link.term < 1 or link.term > MAX_TERM):
            raise Violation(f"I10 term {link.term} on a live link (ceiling {MAX_TERM}): {link}")
    for k in keys:
        # I8: no live chain leads from a key back to itself.
        if any(True for _ in chains(state, k, k)):
            raise Violation(f"I8 cycle through {k}: {state}")
        for chain, eff in chains(state, root, k):
            # I2: the cap.
            if len(chain) > DEPTH_CAP:
                raise Violation(f"I2 depth {len(chain)} > {DEPTH_CAP} at {k}: {state}")
            # I1: attenuation along the chain — each prefix's effective scope
            # contains the next's, and the chain's scope is the intersection.
            running = frozenset(SCOPES)
            for link in chain:
                nxt = running & link.scope
                if not nxt <= running:
                    raise Violation(f"I1 widened at {link}: {state}")
                running = nxt
            if running != eff:
                raise Violation(f"I1 effective scope is not the intersection: {chain}")
            # I7: every link past the first sits under a link carrying
            # sub_delegation.
            for i in range(1, len(chain)):
                if SUB not in frozenset(SCOPES).intersection(*(l.scope for l in chain[:i])):
                    raise Violation(f"I7 chain continues without sub_delegation: {chain}")
    # I4: a licence confers no issuance authority. A licensee with no live
    # `license` chain of its own must be refused as an issuer, whatever else
    # it holds.
    for k in state.licensees:
        if k != root and not holds(state, root, k, LICENSE):
            if issue_licence(state, root, k, "anyone") is not None:
                raise Violation(f"I4 licence chained at {k}: {state}")
    # I5: a grant confers no issuance authority.
    for k in state.grantees:
        if k != root and not holds(state, root, k, GRANT):
            if issue_grant(state, root, asset, k, "anyone") is not None:
                raise Violation(f"I5 grant chained at {k}: {state}")
    # I6 (standing half): a leaf exists only for a key the door admitted;
    # the door's own check is asserted at admission in `enumerate_universe`.
    # A licence or a grant never appears for a key no action issued it to.


def authority_snapshot(state: State, root: str, keys: Tuple[str, ...]) -> FrozenSet[Tuple[str, str]]:
    """Which (key, scope) pairs hold from the root. The thing I3 and I9 compare."""
    return frozenset((k, s) for k in keys for s in SCOPES if holds(state, root, k, s))


# ───────────────────────────── the enumeration ──────────────────────────


def enumerate_universe(
    name: str,
    root: str,
    keys: Tuple[str, ...],
    asset: str,
    with_licences: bool,
    with_grants: bool,
    max_links: int,
    scope_sets: Tuple[FrozenSet[str], ...] = SCOPE_SETS,
) -> dict:
    start = State(frozenset(), frozenset(), frozenset())
    seen = {start.key(): start}
    # Per I6: every leaf must have been admitted at a door. Keys that ever
    # received one, for the final report.
    leaves_admitted = {"licence": set(), "grant": set()}
    # I9: for each reachable row-set, the snapshot it yields; a second history
    # reaching the same rows must yield the same snapshot. Dedup on the row-set
    # is exactly that check, provided the snapshot is recomputed and compared.
    snapshots = {start.key(): authority_snapshot(start, root, keys)}
    queue = deque([start])
    refusals = 0
    admissions = 0
    max_depth_seen = 0
    cascades_checked = 0

    while queue:
        state = queue.popleft()
        check(state, root, keys, asset)
        for k in keys:
            for d, _ in paths(state, root, k):
                max_depth_seen = max(max_depth_seen, d)

        successors = []
        if len(state.links) < max_links:
            for src in keys:
                for dst in keys:
                    for scope in scope_sets:
                        for term in TERMS_OFFERED:
                            nxt = delegate(state, root, src, dst, scope, term)
                            if nxt is None:
                                refusals += 1
                            else:
                                successors.append(nxt)
        for link in state.links:
            before = authority_snapshot(state, root, keys)
            nxt = withdraw(state, link)
            after = authority_snapshot(nxt, root, keys)
            # I3 cascade: everything that held ONLY through this link is gone,
            # and nothing that held without it changed. "Held only through
            # this link" is decided by the resolver on the state without it,
            # so the check is: after == snapshot of (state minus link), and
            # after ⊆ before.
            if not after <= before:
                raise Violation(f"I3 withdrawal of {link} ADDED authority: {before} -> {after}")
            cascades_checked += 1
            successors.append(nxt)
        if with_licences:
            for issuer in keys:
                for subject in keys:
                    nxt = issue_licence(state, root, issuer, subject)
                    if nxt is None:
                        refusals += 1
                    else:
                        # I6 at admission: the issuer resolves to the authority now.
                        assert issuer == root or holds(state, root, issuer, LICENSE)
                        admissions += 1
                        leaves_admitted["licence"].add((issuer, subject))
                        successors.append(nxt)
        if with_grants:
            for issuer in keys:
                for recipient in keys:
                    nxt = issue_grant(state, root, asset, issuer, recipient)
                    if nxt is None:
                        refusals += 1
                    else:
                        assert issuer == root or holds(state, root, issuer, GRANT)
                        admissions += 1
                        leaves_admitted["grant"].add((issuer, recipient))
                        successors.append(nxt)

        for nxt in successors:
            k = nxt.key()
            snap = authority_snapshot(nxt, root, keys)
            if k in seen:
                if snapshots[k] != snap:
                    raise Violation(f"I9 two histories, one row-set, two verdicts: {k}")
                continue
            seen[k] = nxt
            snapshots[k] = snap
            queue.append(nxt)

    return {
        "universe": name,
        "states": len(seen),
        "max_delegation_depth": max_depth_seen,
        "refusals": refusals,
        "issuances": admissions,
        "withdrawals_checked": cascades_checked,
        "distinct_issuer_leaf_pairs_admitted": {k: len(v) for k, v in leaves_admitted.items()},
    }


def depth_closure() -> dict:
    """A chain long enough to exceed the cap, delegation only, every scope set
    at every link. Shows the resolver confers nothing past DEPTH_CAP and that
    a link past the cap is refused at the door."""
    keys = tuple(f"k{i}" for i in range(DEPTH_CAP + 3))
    root = keys[0]
    counts = {}
    refused_past_cap = 0
    conferred_past_cap = 0
    for scope_choice in itertools.product(
        [s for s in SCOPE_SETS if SUB in s], repeat=DEPTH_CAP + 1
    ):
        state = State(frozenset(), frozenset(), frozenset())
        for i, scope in enumerate(scope_choice):
            nxt = delegate(state, root, keys[i], keys[i + 1], scope, 1)
            if nxt is None:
                refused_past_cap += 1
                break
            state = nxt
            d = max((dd for dd, _ in paths(state, root, keys[i + 1])), default=0)
            counts[d] = counts.get(d, 0) + 1
        for k in keys:
            if any(d > DEPTH_CAP for d, _ in paths(state, root, k)):
                conferred_past_cap += 1
    return {
        "universe": "depth-chain",
        "links_admitted_per_depth": dict(sorted(counts.items())),
        "links_refused_past_cap": refused_past_cap,
        "authority_conferred_past_cap": conferred_past_cap,
    }


def main() -> int:
    results = []
    # General universe: a root that is both the licensing authority and the
    # asset owner, three other keys, every action interleaved. Scope sets are
    # the five that matter (every singleton, and the two emission scopes with
    # sub_delegation); the full eight are run on the depth chain.
    results.append(
        enumerate_universe(
            "general",
            root="A",
            keys=("A", "B", "C", "D"),
            asset="R",
            with_licences=True,
            with_grants=True,
            max_links=int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 2,
            scope_sets=(
                frozenset({LICENSE}),
                frozenset({GRANT}),
                frozenset({LICENSE, SUB}),
                frozenset({GRANT, SUB}),
                frozenset({LICENSE, GRANT, SUB}),
            ),
        )
    )
    # Delegation-only universe at one more link, so cascade and the
    # sub_delegation requirement are checked over three-link trees.
    results.append(
        enumerate_universe(
            "delegation-only",
            root="A",
            keys=("A", "B", "C", "D"),
            asset="R",
            with_licences=False,
            with_grants=False,
            max_links=3,
            scope_sets=(
                frozenset({LICENSE}),
                frozenset({LICENSE, SUB}),
                frozenset({LICENSE, GRANT, SUB}),
            ),
        )
    )
    results.append(depth_closure())
    for r in results:
        print(r)
    d = results[-1]
    ok = (
        all(r.get("max_delegation_depth", 0) <= DEPTH_CAP for r in results[:-1])
        and d["authority_conferred_past_cap"] == 0
        and d["links_refused_past_cap"] > 0
        and max(d["links_admitted_per_depth"]) == DEPTH_CAP
        and results[0]["max_delegation_depth"] <= DEPTH_CAP
    )
    print("CLOSED" if ok else "OPEN")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Violation as e:
        print(f"VIOLATION: {e}")
        sys.exit(2)
