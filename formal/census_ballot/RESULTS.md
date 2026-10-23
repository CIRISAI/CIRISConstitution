# Results — TLC 1.7.4 on OpenJDK 21 (`-workers auto`, `-Xmx3g`), Lean 4.14.0, this host, 2026-10-22

Every configuration below closes or fails as named in under 75 seconds on this host; the longest is the
floor-binding base instance (2.1 M distinct states, 1 min 10 s) and the one liveness instance (17 k states,
1 min, almost all of it TLC's fairness check).

## Ruled configurations (close)

| Config | Distinct states | States generated | Time | Result |
|---|---|---|---|---|
| `CensusBallot_2o_m3_lossy` (2 owners, M = 3, vote cell, lossy, per-period absence, colluder {1}) | 66,609 | 132,848 | 3 s | no error |
| `CensusBallot_2o_m3_dishonest` (owner 2 may emit any of the 27 vectors) | 87,831 | 175,508 | 4 s | no error |
| `CensusBallot_2o_m3_both_cells` (`ea` and a two-bucket poll both shared, two periods) | 72,748 | 144,911 | 14 s | no error |
| `CensusBallot_2o_m3_silenced` (owner 2 silenced at any boundary; two periods; **liveness checked**) | 17,106 | 33,498 | 1 min 00 s | no error |
| `CensusBallot_3o_m2` (3 owners, M = 2, every tally pair, colluder {2}) | 90,071 | 176,258 | 19 s | no error |
| `CensusBase_3o_silence_one` (3 owners, Scale 10, `ea` in the clear, owner 3 silenced; 8 periods) | 182,629 | 244,013 | 17 s | no error |
| `CensusBase_3o_silence_two` (owners 2 and 3 silenced, together or one after the other) | 426,636 | 556,897 | 24 s | no error |
| `CensusBase_3o_free` (nature free over absent/idle/active; 6 periods) | 815,005 | 1,303,567 | 39 s | no error |
| `CensusBase_3o_floor_binds` (freeze at ½ as an instrument; two silenced one at a time; 12 periods) | 2,141,864 | 2,829,753 | 1 min 10 s | no error |

Invariants in every ballot run: `Inv_SharePrivacy`, `Inv_Correctness`, `Inv_Validity`, `Inv_Agreement`,
`Inv_OnePerOwner`, `Inv_KFloor`, `Inv_DominanceGate`, `Inv_OccurrenceInvisible`, `Inv_BaseRatchet`,
`Inv_TallyThreshold`; `Prop_HonestChangeResolves` in `_silenced`. In every base run: `Inv_BaseRatchet`,
`Inv_KFloor`, `Inv_OnePerOwner`, `Inv_Validity`, `Inv_Agreement`, `Inv_Correctness`, `Inv_DominanceGate`.

## Twins (fail by design, each on its named invariant)

| Config | Switch | Distinct states to the failure | Time | Fails |
|---|---|---|---|---|
| `CensusBallot_3o_m2_two_colluding` | `Colluding = {1, 2}` | 757 | 1 s | `Inv_SecrecyWithoutTheGuard` |
| `CensusBallot_2o_m3_no_padding` | `PadWhenClosed = FALSE` | initial state (the wire-profile sets differ) | 0 s | `Inv_OccurrenceInvisible` |
| `CensusBallot_2o_m3_no_dedupe` | `Dedupe = FALSE` | 3,000 | 1 s | `Inv_OnePerOwner` |
| `CensusBallot_2o_m3_no_validity` | `Validate = FALSE` | 1,642 | 0 s | `Inv_Validity` |
| `CensusBallot_2o_m3_no_joint` | `JointAccept = FALSE` | 388 | 0 s | `Inv_Agreement` |
| `CensusBallot_2o_m3_no_kfloor` | `Gate = FALSE` | 1,180 | 0 s | `Inv_KFloor` |
| `CensusBallot_2o_m3_responders` | `ThresholdBase = "responders"`, `K = 1` | 17,162 | 1 s | `Inv_TallyThreshold` (one approval passes against one responder; the frozen census base is two) |
| `CensusBase_3o_no_ratchet` | `Ratchet = FALSE` | 1,148 | 0 s | `Inv_BaseRatchet` (30 → 20 in one period) |

## Reachability dyes (fail by design: the closures above are not vacuous)

| Config | Distinct states to the witness | Time | Witness |
|---|---|---|---|
| `CensusBase_3o_reach_ratchet` | 1,356 | 1 s | `Reach_RatchetCarries`: base 27 over composite 20, the ratchet term exactly |
| `CensusBase_3o_reach_frozen` | 1,142 | 0 s | `Reach_Frozen`: the partition freeze entered |
| `CensusBase_3o_reach_floor` | 1,136,434 | 36 s | `Reach_FloorBinds`: base 15 = ⌈30/2⌉ at period 11, above composite 10 and above ⌈0.9 · 15⌉ = 14 |

An earlier cut of `floor_binds` with no silencing and no absence closed but its dye did **not** fire: an
idle owner that keeps reporting stays expected-active for three more periods, so the composite could not
step 30 → 20 → 10 inside the bound. The silencer was generalised to one owner at a time (the stronger
adversary) and the dye then fires; the observation is recorded in the README's residuals.

## Lean

`lean CensusBallotCount.lean`: exit 0; 28 theorems; no `sorry`; core only (no Mathlib).
