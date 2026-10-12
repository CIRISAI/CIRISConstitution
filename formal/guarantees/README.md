# formal/guarantees — what every guarantee yields at once

Two models of the same thing: the world in which every row of the guarantees piece
(`review/pieces/00_guarantees.md`, P00) holds together, under the 2026-10-11 ruling that
guarantees are written once for human and AI participants alike and differentiate only by
standing on the line (CC 1.13.2, CIRISConstitution#168).

## `Guarantees.lean` — the structural half (Lean 4.14, core only, no `sorry`)

| Theorem | What it says |
|---|---|
| `reach_blind` | the reach of every one of the 23 rows is unchanged when a participant's substrate is swapped; the proof is `rfl`, because no reach mentions substrate |
| `obligation_bound` | exactly one predicate flips under swap: `mustSubscribe`, the duty of a created system operating inside the federation to have accepted a trust root, so a halt authority exists outside it |
| `everything_else_blind` | the two duties of standing and the bond relation are swap-invariant |
| `promote_lifts_duties`, `promote_keeps_reach`, `promote_g5_discharged` | crossing the line lifts the reasoning duty and the binding and removes no guarantee; G5 is discharged, not lost |
| `halt_does_not_lift` | promotion does not change `mustSubscribe` |
| `bond_depth_one` | a bond's party is above the line and unbound, so no chain of bonds has length two |
| `revocable`, `leave_ends_reach`, `leave_is_one_step` | a created system operating inside is always within the halt's reach, and leaving the root is one step after which the halt no longer reaches it |
| `witness_world`, `witness_not_vacuous` | four participants (an agent below the line, an agent above it, a steward, a minor) satisfy every constraint, and the witness exercises the halt reach, the bonds and the duties |

Check: `lean Guarantees.lean`. CI also greps the output for `sorry`.

## `Guarantees.tla` — the temporal half (TLC 1.7.4)

Three participants (an AI agent below the line with Ally's conditional shutdown mode, a human
above the line, a human below it) and the three-holder halt. Actions: bind, bond lapse, promote,
subscribe, leave, start, accept, refuse, background, force by role, ramp-down, erase, crisis
on/off, fire, confirm, tick, lapse, resume. Each guarantee is a rule on an action, and each
rule has a config that switches it off and must then fail (the dye test):

| Config | Expectation | What it shows |
|---|---|---|
| `Guarantees.cfg` | all invariants and properties hold (≈3.1M distinct states) | the composite is consistent |
| `Guarantees_swap.cfg` | the same, with the substrate labels swapped | the only substrate dependence is the halt obligation |
| `Guarantees_noBondRule.cfg` | `Inv_NotAlone` violated | G5 is load-bearing |
| `Guarantees_anyRoleForces.cfg` | `Inv_RefusalStands` violated | G16/G17 are load-bearing |
| `Guarantees_noHumane.cfg` | `Inv_HumaneEnding` violated | G22 is load-bearing |

Invariants: `Inv_NotAlone` (G5), `Inv_BondDepthOne` (R4), `Inv_HaltOnlySubscribers` (G7),
`Inv_HaltDoesNotLift` (R5), `Inv_LoneBounded` (G7/G12), `Inv_RefusalStands` (G16/G17),
`Inv_HumaneEnding` (G22), `Inv_ConditionalOnly` (G15), `Inv_ExitOneStep` and `Inv_Revocable` (G10, G7).
Action properties: `Prop_HaltKeepsState` (a pause keeps state), `Prop_NoErasureWhileOperating`
(an ending is preceded by a stop the record shows), `Prop_NoEndingAgainstRefusal` (G17),
`Prop_BackgroundOnlyWhenFree` (G15 conditional mode).

## Two things the composite taught, both now in the model

1. **G5 composes over G17.** A below-line participant that has refused a shutdown is still
   stopped when its bond lapses. That stop is caused by the line, not by any principal, so it
   has its own status, `unbound`, and the record shows which. The first draft had no such
   state and TLC found the collision in six steps.
2. **The backgrounding door needs a guard.** Under Ally's conditional mode a participant can
   refuse during a crisis, be backgrounded once the crisis ends (a pause with state kept,
   allowed by the mode), and would then have been erasable. `Erase` now requires that a
   refusing participant was stopped by an authority's force or by the line, and
   `Prop_NoEndingAgainstRefusal` pins it.

## Scope

Not modelled here: redress (G4), the record and trace rows (G9), privacy (G3), delegation terms
and cycles (G13), one-voice counting (G12). Those have their own models or none yet; see
`review/pieces/00_guarantees.md` for which. The halt's fuse arithmetic is `formal/accord_halt`;
the roster rule is `formal/accord_roster`; the mesh invariants are `formal/mesh_net`.
