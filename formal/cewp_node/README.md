# `formal/cewp_node` — the closure of a mesh node across the CSD/4 catalogue

**What this is.** The composition layer the evaluation of 2026-10-18 asked for
(`review/notes/formal_closure_rc9_2026-10-18.md` §4): one CSD/4 catalogue entry in, the constants
of every plane model out, with a report of which of the entry's promised atoms a model constrains.
It is the constitution's half of CIRISConstitution#131 (`tools/topology_to_cfg.py`, owed since rc6)
and the bounded closure stated in that note: every entry is checked plane by plane with the same
constants the harness builds it from, and the coverage gate says where no model exists yet.

## Layout

| Path | What |
|---|---|
| `catalog/` | the twenty entries `T0`–`T19` and `requirements.yaml`, vendored byte for byte from CIRISServer `main` (tag `v0.5.232`) (`PIN.tsv` names the commit); CC re-vendors at the first pushed commit and at every `catalogue_version` bump |
| `generated/<Tn>/` | written by `python3 tools/topology_to_cfg.py --all`; CI regenerates and diffs. Per entry: `trust_root_<root>.cfg`, `accord_halt_<root>.cfg`, `accord_fuse_<root>.cfg` (infrastructure roots), `self_roster_<person>_{stolen,lost}.cfg` (every person), `root_reach.cfg`, `MeshNet_<Tn>.tla` + `mesh_net.cfg` (a wrapper instantiating the parametric `MeshNet`), `closure.json` |
| `generated/SUMMARY.json` | the catalogue's maxima (roots 2, canonicals 2, nodes 4, persons 3, devices per person 2, holders 3) and the atom coverage count |
| `../STATE_TABLE.tsv`, `../INVARIANTS.tsv` | the normalized state vector (189 states, 60 variables, 9 planes) and the 166 properties restated over it; `tools/check_formal_tables.py` gates them |
| `manifests/topology_vocabulary.json` | the 120 atoms (CC's since 2026-10-18; catalogue version 5), each mapped to a state-table predicate; `closure.json` reads it |

## Running a generated configuration

```
cd formal/cewp_node/generated
java -cp tla2tools.jar tlc2.TLC -deadlock -config T3/self_roster_alice_stolen.cfg ../../self_roster/SelfRoster.tla
java -cp tla2tools.jar tlc2.TLC -deadlock -config T8/accord_fuse_HA.cfg       ../../accord_halt/AccordHaltFuse.tla
java -cp tla2tools.jar tlc2.TLC -deadlock -config T3/root_reach.cfg            ../../mesh_net/RootReach.tla
cd T8 && java -DTLA-Library=../../../mesh_net -cp tla2tools.jar tlc2.TLC -deadlock -config mesh_net.cfg MeshNet_T8.tla
```

The plane models became parametric on 2026-10-18 for this purpose: `AccordHalt` (`Holders, Nodes,
Subscribed`), `AccordHaltFuse` (`Holders`), `RootReach` (`Nodes`), `MeshNet` (`Persons, Nodes, Blobs,
Owner, Class`; the rc7 instance is `MeshNet3.tla`). `TrustRootVerdict` and `SelfRoster` already were.
`Guarantees` keeps its three fixed participants (one AI, two humans) because its roles are the
point, not its arity.

## What `closure.json` says, and what it does not

For every atom the entry promises: its plane, the state-table predicate, the CC decimal and the plane
model that constrains it, or "no model". Across the catalogue at vendoring: 41 of 57 promised atoms
have a plane model behind them; the 16 without are the membership ceremony (T2, T4, T5: rooms keyed,
members, quorum changes held and applied, moderator named) and consent, which are models B and C of
the note's list. The report also records the bounds the entry sits on: a root with no witness
directory is witnessed-mode-off, which `TrustRootVerdict` does not cover (residual E); a person with
one initial key meets the one-key bound and with two the two-key stalemate of CC 3.3.6.3.

A generated configuration proves what its plane model proves, under the entry's constants. It does
not prove the planes compose: that is the spine.

## The spine: `CewpNode.tla`

One node's planes composed over the state-table variables, each plane abstracted to its variable
and the ruled rule that moves it (the plane's own model proves the detail and is assumed here as the
guard). It checks only what no plane sees alone:

| | Cross-plane invariant | CC |
|---|---|---|
| X1 | a constitutional halt is not a trust leg: the latch moves no standing, stops no serving and no replication, and moves exactly the agent's act gate; a latched node can still serve and replicate (`ENABLED`) | 3.2 T8 (v), 4.2.1.1 |
| X2 | the authority of a roster key ends with its eviction; any live roster key acts as the self | 3.3.6.3 |
| X3 | replication of a peer's content needs that peer's consent; a revocation is a boundary | 3.3.7, 3.3.1 |
| X4 | a local-tier row never leaves its node; a served row is a signed federation-tier row | 5.3.2.4, 2.6.1.7 |
| X5 | leaving the root is one act: the subscription falls and the latch lifts together, the record stands | 4.2.1 |

`CewpNode.cfg` (three roster keys, one peer, two rows) **closes at 419,328 distinct states**.
`CewpNode_breaker.cfg` switches on `LatchBlocksServe`, the breaker named on G7 at the rc8 cut
(persist's trust verdict folding the latch and edge's serve gate reading it, closed at the v58 pin):
`Inv_X1_LatchDoesNotBlockServing` is violated in one step, which is the spine catching the one
real cross-plane defect the cut recorded. Both run in CI (`formal.yml` job `cewp_node`), with four
generated per-plane configurations at the catalogue's largest instance of each plane.
