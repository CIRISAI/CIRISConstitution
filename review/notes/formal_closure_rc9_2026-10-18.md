# Formal closure for a mesh node — evaluation of the models against the lifecycles the text defines and the CSD/4 catalogue (rc9, 2026-10-18)

**Question (steward, 2026-10-18).** Evaluate the formal models against the lifecycle-of-states the constitution defines; can the set of models needed to cover every valid CEWP/CEG state be iterated; is a closure model for a mesh node across all CSD/4 topologies, maximally projected to N participants, possible.

**Short answer.** The eight models cover five of the fifteen state machines the text defines, each one plane at a time, none composing another, and the register cites only five of them. A single flat closure model is not reachable: one root's view already needs 22 million states at four founders and one self's roster 2.5 million at four devices. A closure model is reachable as a **product of plane machines with a coverage gate**: every atom of the CSD/4 catalogue maps to a state predicate of some plane model, every row kind of the 1+4 grammar maps to an action in some model, and the plane models share one generated constant set per topology. Bounded closure at the catalogue's maximum (5 nodes, 3 persons, 4 root holders, 2 devices per person) is a matter of writing the missing plane models and the spine; unbounded N holds only for counting properties, which Lean already proves for the accord roster and can for the others. Six plane models are missing; three exist but need extending; one text gap blocks a model.

## 1. What exists (formal/, eight directories; `.github/workflows/formal.yml` runs all)

| Model | Entity and plane | Instance checked | Witnesses | Cited by a claim |
|---|---|---|---|---|
| `trust_root` (TLA+) | one node's standing verdict over one infrastructure root: seats, resignations, heads, cosignatures, edge, conferral | 4 founders + 1 node key, 3 witnesses, M=2, K=2; 22,152,480 states | CC 3.2 T7/T8 (i, ii, iv, vi, viii, T7, recovery) | no — `CLM-standing-verdict` stages on #127 without the path |
| `accord_roster` (Lean) | counting model of one roster decision under coercion/censorship/loss, any N | universal theorems; instances at 10 and 21 | CC 4.2.6 | prose only (`CLM-accord-livequorum`) |
| `accord_halt` (TLA+, two modules) | holders, one latch per node, fuse, confirm, resume; adversary coerces one, jams, steals a sealed row | 3 holders, 2 nodes; 19,408 / 319,090 states | CC 4.2.1.1, 4.2.6 | no |
| `mesh_net` + `RootReach` (TLA+) | blob holding, cohort scope, moderation lapse, root subscription | 3 persons, 3 nodes, 2 blobs; 2,013,648 states | CC 5.2, 5.4.6, 4.2.1, 4.5.4, 3.2 T3 | no |
| `authority_tree` (Python BFS) | delegation links, licences, grants; depth, term, attenuation | 4 keys, ≤2 links; 595,456 states | CC 4.4.3.4.3, 4.1.1, 2.4.1.2.1, 4.4.3.2.8 | yes — 7 claims |
| `guarantees` (Lean + TLA+) | participant lifecycle: stewarded, bonded, subscribed, refused, floored, crisis; the halt abstracted | 1 AI + 2 humans; ~3.1M states | P00 G5, G7, G10, G15–17, G22; CC 1.13.2, 7.5.5 | no |
| `withdraws_admission` (TLA+) | erasure of ordinary and adverse rows by producer, subject, proxy, node | 4 subjects; 3,600 states | CC 2.4.1.1, 4.5.3 | prose only |
| `self_roster` (TLA+) | the keys under one self: owner/thief/lost, two-path landing | 1–4 devices; up to 2,558,560 states; 16 configs; six JSON traces | CC 3.3.6.3 | yes — `CLM-self-roster-model` |

No module imports another. Shared vocabulary without shared definitions: *strict majority of the standing roster* (accord_roster, accord_halt, self_roster), *subscribed* and *halted* (RootReach, accord_halt, guarantees), *delegates_to chain* (authority_tree, withdraws_admission rule 3). Found and fixed in this pass: T8 invariant (v) still read a latched halt as `NotRooted` after the 2026-10-15 ruling struck the halt leg; the trust-root README still named the latch as a leg; the self-roster README still said one and two keys were unmodelled.

## 2. The lifecycles the text defines, and their cover

Fifteen state machines or lifecycles are written in the text (search of Parts 1–8, review/derivation, review/notes). Only T8 is written as a full machine with states, transitions and invariants.

| # | Lifecycle | Where | States | Model |
|---|---|---|---|---|
| 1 | Standing verdict | 3.2 T7/T8 | Rooted / Stalled / NotRooted; live / stalled | `trust_root` (iii, v, vii by construction) |
| 2 | Accord halt | 4.2.1.1, 4.2.6 | not halted → latched (lone) → lapsed or confirmed → resumed | `accord_halt`, `guarantees` (one step each), `accord_roster` (count) |
| 3 | Self roster / identity_occurrence | 3.3.6, 3.3.6.3, 2.6.8 | pending → owned; roster add/evict by two paths | `self_roster`; the join itself in CIRISServer `formal/add_device` |
| 4 | Membership ceremony | 3.1.3.2 | proposal → acceptance / decline → (awaiting the group) → widening / removal / resignation | **none** |
| 5 | Lineage witness | 3.2 T6 | proposal → acceptance / decline; head frozen on equivocation; fork attempt | partly in `trust_root` (heads, cosignatures); the ceremony **none** |
| 6 | Consent | 3.3.1 | state granted / revoked / expired; decay identity_severed → patterns_anonymized → complete; community_trust fold with revocation boundary | **none** (`withdraws_admission` covers erasure only) |
| 7 | Retirement | 7.5.5 | decided → frozen → secrets_destroyed → handed_over → notified → custodian_minted → retired; cancel by withdraws before frozen | `guarantees` has one invariant, not the seven states |
| 8 | Agent operating status | model only | idle / operating / erased / consented / backgrounded / forced / unbound | `guarantees` (no wire tokens in the text) |
| 9 | Event lifecycle | 3.3.8 | open → cancelled / completed / superseded (the 3.3.8 example says active → cleared → superseded: inconsistency) | none |
| 10 | Objection, quarantine, WA adjudication | 3.1.9.2, 3.1.9.4 | **state sets not enumerated in the text** | none; the reverse-quorum shape reused by `self_roster` |
| 11 | Moderation lapse and report window | 4.5.4, 4.5.13 | lapse → merit promotion → 48 h recovery → fail-secure; outcome ladder | `mesh_net` (lapse, promote, fail-secure) |
| 12 | Attestation tier | 5.3.2.4 | local → federation (idempotent promotion; tier = federation ⇒ signature) | none |
| 13 | Ledger | 3.3.10.1 | head → checkpoint → promotion; fork = evidence | none |
| 14 | Capacity binding | 3.4.12 | capacitated / incapacitated; reversible_pending → reversible_excluded or lapse | none |
| 15 | Session claim, locality, stream epochs | 3.1.3.1, 3.1.9.x, 5.3.3 | routing table / scale label / epoch re-key — no state sets named | none |

Key-record dispositions (pending, active, revoked, rotated, retired) appear in no text: a key's end of life rides `withdraws`, `recants`, tombstones and `revoked_after`. The server's roster description (awaiting the steward's read) is the only place those dispositions are written down.

## 3. The CSD/4 catalogue (CIRISServer `feat/csd4-catalogue`, unpushed WIP 5c4fdbaa)

Ten entries T0–T9, a closed list of about fifty state atoms in `harness/native/model.py`, `requirements.yaml` binding each CSD id to the atoms that must hold at one moment, a runner that checks four atoms live (`node.unclaimed`, `root.halted`, `device.join_requested`, `device.join_approved`) and reports `MODEL_DRIFT`, and a per-node row export (`rows.jsonl`, `keys.jsonl`, transport destinations, metrics, the `/v1/trust-root` verdict) that #131 asked for. Maximum instance: 5 nodes (T3, T9), 3 persons, 4 root holders (3 seated + 1 conferrable, quorum 2), 2 devices per person; T9's second canonical does not build yet. Builders for T4, T6, T7 and T9 stop early; T3 stops at CIRISServer#793. There is no mapping from `CLM-*` ids to predicates to UI anywhere in the catalogue, and `tools/topology_to_cfg.py` and the topology vocabulary manifest #131 named do not exist in this repository.

**Atoms against planes.** Every atom in the catalogue falls into one of seven planes: node (unclaimed/claimed/announced/owned), root (none/rooted/halted/confirmed/resumed/two/outside), device (join requested/approved/joined; roster visible), room and membership (self room keyed, pair room keyed, member, child member, quorum change held/applied, moderator named, cannot list), content (held/custody received/withdrawn, holds no row, no wider self rows), authority (guardian bound, licensing authority, delegation chain), agent (bound, steward bonded, WA present). Three of the seven have a model today (root, device, content in part); four have none (node, room and membership, authority beyond delegation terms, agent lifecycle beyond `guarantees`).

## 4. Can one closure model exist

Not as one state space. The two largest single-plane instances are already at 22 million and 2.5 million states, and a product of seven planes at the catalogue's maximum would not be checkable by explicit-state TLC. It can exist as a **composition with a coverage gate**, which is what "closure" should mean here:

1. **One constant set per topology.** `tools/topology_to_cfg.py` (owed since #131) reads a catalogue entry (`roots`, persons, nodes, devices, relations) and emits the constants for every plane model that applies: Founders / NodeKeys / Witnesses / M / K / AttachWindow for `trust_root`; Devices / Initial for `self_roster`; holders and nodes for `accord_halt`; persons, nodes, blobs and cohorts for `mesh_net`; keys for `authority_tree`. The same entry feeds TLC (exhaustive over the machine) and the harness (one trace on the implementation), and the row export is replayed into the model as a trace check.
2. **A spine module** `formal/cewp_node/` that instantiates the plane modules with that constant set and shared interface variables (the roster of a self, the standing verdict per root, the halt latch per node, membership per cohort, tier per row) and checks only the cross-plane invariants that no plane sees alone: a halted node still serves and replicates (halt is not a trust leg) while its agent's act gate refuses; an evicted roster key's rows after eviction do not count as the owner's; an unrooted node holds no row of a cohort it is not a member of; a local-tier row never leaves the node. Assume-guarantee: each plane's checked invariants are the spine's assumptions, stated as such.
3. **The coverage gate**, published as data (`manifests/topology_vocabulary.json`): every catalogue atom → (plane model, predicate, CC decimal, claim id); every row kind × family class in the 1+4 grammar → a model action or an explicit "not modelled" row. CI fails on an atom or a row kind with no row, exactly as the namespace registry fails on an unregistered family. This is the #131 claim → predicate → UI chain, with the model in the middle.
4. **Projection to N.** Explicit-state checking stays bounded: the catalogue's maximum (5 nodes, 3 persons, 4 holders, 2 devices) is the bound, with TLC symmetry sets on persons, nodes and devices. Unbounded N is reachable where the property is a count over a roster — `accord_roster` already proves the standing rule for any N in Lean, and the self-roster two-path rule and the T7 margin are the same kind of statement — and not reachable for the product machine; the note should say so rather than promise it. Apalache (symbolic, bounded depth) is the one tool that would raise the bound without rewriting; it is not in CI today.

## 5. What has to exist — the iterated list, in the order that unblocks the most

| # | Model | Plane | Why first | Size |
|---|---|---|---|---|
| A | `formal/cewp_node` spine + `tools/topology_to_cfg.py` + `manifests/topology_vocabulary.json` | all | the closure itself; turns the catalogue into the coverage gate; #131's owed artefacts | medium |
| B | `formal/membership` | room and membership | four catalogue planes (T2, T4, T5) have no model; the ceremony has six stages and two cosign protocols | medium |
| C | `formal/consent` | consent | three machines in 3.3.1 (state, decay, community_trust fold) with a revocation boundary; the owner-authored grant (#179) lands here | medium |
| D | `formal/retirement` | agent | seven states, cancel window, custodian key; `guarantees` has the invariant, not the machine; T7 | small |
| E | extend `trust_root` | root | witnessed mode off; charter members as rows; the accord family kind (4.2.6 live quorum) which #131 noted has no machine | medium |
| F | extend `authority_tree` | authority | time as a clock, affiliation hierarchy, licensure by community authority (T6) | small |
| G | `formal/tier` or fold into A | content | local → federation promotion and the signed-object binding (2.6.1.7): tier = federation ⇒ both halves verify | small |
| H | text first, then model | governance | enumerate the state sets of `objection`, `quarantine`, `wa_adjudication` (not in the text today); fix the 3.3.8 event-state inconsistency | text |
| I | `formal/ledger`, `formal/capacity` | ledger, capacity | small machines; low urgency | small |
| J | register | — | cite `trust_root`, `accord_halt`, `mesh_net`, `guarantees`, `withdraws_admission` from their claims as `test:@formal/...` rows; today the formal tier is under-reported | data |

Cross-check against the lifecycle table: 1 ✓, 2 ✓, 3 ✓, 4 → B, 5 → E, 6 → C, 7 → D, 8 → D, 9 → H, 10 → H, 11 ✓ (partial), 12 → G, 13 → I, 14 → I, 15 out of scope. Against the catalogue planes: node → A, root → E, device ✓, room → B, content → G (+ mesh_net ✓), authority → F, agent → D.

## 6. What "formally describe CEWP" should mean

The glossary (8.1.1) defines CEWP as the network formed when nodes exchange CEG envelopes over Edge/Reticulum transport, not a product or service; Part 6 names a "CEWP-1.0 conformant peer"; Part 5 cites CEWP FSDs. Nothing states CEWP as a machine. The formal description is therefore the spine of §4: CEWP = the set of CEG-speaking nodes, each a product of the seven plane machines, composed by the wire; its valid states are the reachable states of the spine under the ruled policies; its conformance surface is the per-plane invariants plus the cross-plane invariants; its evidence is the coverage gate. That text belongs in Part 8 beside the executable-specification annex #131 proposed, informative, pointing at the models, not restating them.

## 7. Immediate actions taken in this pass

- T8 (v) corrected to the ruling (a halt moves no state in V); trust-root README and self-roster README brought into line.
- This note. The server session has been asked for the state of the CSD/4 lock; the client CSD corpus is being inventoried for the generator design.
